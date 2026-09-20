from __future__ import annotations

import hashlib
import os
import platform
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import DirectChannelConfig
from .policy import (
    PolicyError,
    contains_sensitive_value,
    is_blocked_path,
    redact_text,
    resolve_allowed_path,
)


def _node_identity() -> tuple[str, str]:
    prefix = os.environ.get("PREFIX", "")
    executable = sys.executable
    is_termux = (
        bool(os.environ.get("TERMUX_VERSION"))
        or "com.termux" in prefix
        or "/data/data/com.termux/" in executable
    )
    if is_termux:
        return "android-termux", "SELF_HOSTED_ANDROID"
    return "linux", "SELF_HOSTED_SERVER"


class DirectChannelRuntime:
    def __init__(self, config: DirectChannelConfig):
        self.config = config

    def status(self) -> dict[str, Any]:
        node_type, authority = _node_identity()
        return {
            "status": "OK",
            "product": "OpenSynapse",
            "component": "Direct Channel",
            "version": "0.2.0a6",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "host": platform.node(),
            "platform": platform.system(),
            "python": platform.python_version(),
            "node_type": node_type,
            "policy": self.config.public_view(),
            "authority": authority,
        }

    def read_text(self, path: str, offset: int = 0, limit: int | None = None) -> dict[str, Any]:
        target = resolve_allowed_path(path, self.config.read_roots, self.config)
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise PolicyError("INVALID_OFFSET")
        bounded = self.config.max_read_bytes if limit is None else limit
        if isinstance(bounded, bool) or not isinstance(bounded, int) or bounded < 1:
            raise PolicyError("INVALID_LIMIT")
        bounded = min(bounded, self.config.max_read_bytes)
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(target, flags)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode):
                raise PolicyError("REGULAR_FILE_REQUIRED")
            os.lseek(fd, offset, os.SEEK_SET)
            raw = os.read(fd, bounded + 1)
        finally:
            os.close(fd)
        truncated = len(raw) > bounded
        raw = raw[:bounded]
        text = raw.decode("utf-8", errors="replace")
        safe, redactions = redact_text(text)
        return {
            "status": "OK",
            "path": str(target),
            "offset": offset,
            "bytes_returned": len(raw),
            "truncated": truncated,
            "redaction_count": redactions,
            "content": safe,
        }

    def list_directory(self, path: str, limit: int = 200) -> dict[str, Any]:
        target = resolve_allowed_path(path, self.config.read_roots, self.config)
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise PolicyError("INVALID_LIMIT")
        bounded = min(limit, 500)
        entries: list[dict[str, Any]] = []
        with os.scandir(target) as scan:
            for entry in scan:
                child = target / entry.name
                if is_blocked_path(child, self.config) or entry.is_symlink():
                    continue
                kind = "directory" if entry.is_dir(follow_symlinks=False) else "file" if entry.is_file(follow_symlinks=False) else "other"
                entries.append({"name": entry.name, "kind": kind})
        entries.sort(key=lambda item: (item["kind"] != "directory", item["name"].lower()))
        return {
            "status": "OK",
            "path": str(target),
            "entries": entries[:bounded],
            "truncated": len(entries) > bounded,
            "hidden_by_policy": True,
        }

    def tail_log(self, path: str, lines: int = 100) -> dict[str, Any]:
        target = resolve_allowed_path(path, self.config.read_roots, self.config)
        if isinstance(lines, bool) or not isinstance(lines, int) or lines < 1:
            raise PolicyError("INVALID_LINES")
        line_limit = min(lines, 500)
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(target, flags)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode):
                raise PolicyError("REGULAR_FILE_REQUIRED")
            size = metadata.st_size
            start = max(0, size - self.config.max_read_bytes)
            os.lseek(fd, start, os.SEEK_SET)
            raw = os.read(fd, self.config.max_read_bytes)
        finally:
            os.close(fd)
        text = raw.decode("utf-8", errors="replace")
        if start:
            first_break = text.find("\n")
            text = text[first_break + 1 :] if first_break >= 0 else ""
        selected = "\n".join(text.splitlines()[-line_limit:])
        safe, redactions = redact_text(selected)
        return {
            "status": "OK",
            "path": str(target),
            "lines_requested": line_limit,
            "redaction_count": redactions,
            "content": safe,
        }

    def write_text(self, path: str, content: str, expected_sha256: str | None = None) -> dict[str, Any]:
        if not self.config.write_roots:
            raise PolicyError("WRITE_DISABLED")
        target = resolve_allowed_path(path, self.config.write_roots, self.config)
        raw = content.encode("utf-8")
        if len(raw) > self.config.max_write_bytes:
            raise PolicyError("WRITE_TOO_LARGE")
        if contains_sensitive_value(content):
            raise PolicyError("SENSITIVE_CONTENT_DENIED")
        target.parent.mkdir(parents=True, exist_ok=True)
        before: str | None = None
        if target.exists():
            if not target.is_file() or target.is_symlink():
                raise PolicyError("REGULAR_FILE_REQUIRED")
            before = hashlib.sha256(target.read_bytes()).hexdigest()
        if expected_sha256 is not None and before != expected_sha256:
            raise PolicyError("EXPECTED_SHA256_MISMATCH")
        fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary, 0o600)
            os.replace(temporary, target)
            directory_fd = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        after = hashlib.sha256(raw).hexdigest()
        return {"status": "OK", "path": str(target), "before_sha256": before, "after_sha256": after, "bytes_written": len(raw)}

    def process_status(self, pid: int) -> dict[str, Any]:
        if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
            raise PolicyError("INVALID_PID")
        source = Path(f"/proc/{pid}/status")
        try:
            raw = source.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError as exc:
            raise PolicyError("PROCESS_NOT_FOUND") from exc
        allowed = {"Name", "State", "VmRSS", "VmSize", "Threads"}
        values: dict[str, str] = {}
        for line in raw.splitlines():
            key, sep, value = line.partition(":")
            if sep and key in allowed:
                values[key] = value.strip()
        return {"status": "OK", "pid": pid, "process": values, "argv_returned": False, "environment_returned": False}

    def run_bounded(self, command: str, args: list[str] | None = None, cwd: str | None = None, timeout: int | None = None) -> dict[str, Any]:
        executable = (self.config.commands or {}).get(command)
        if executable is None:
            raise PolicyError("COMMAND_NOT_ALLOWED")
        if not self.config.execute_roots:
            raise PolicyError("EXECUTION_DISABLED")
        selected_cwd = cwd or str(self.config.execute_roots[0])
        workdir = resolve_allowed_path(selected_cwd, self.config.execute_roots, self.config)
        if not workdir.is_dir():
            raise PolicyError("EXECUTE_CWD_MUST_BE_DIRECTORY")
        argv = [] if args is None else args
        if not isinstance(argv, list) or len(argv) > 64 or any(not isinstance(v, str) or len(v) > 4096 for v in argv):
            raise PolicyError("INVALID_ARGUMENTS")
        joined = "\n".join(argv)
        if contains_sensitive_value(joined):
            raise PolicyError("SENSITIVE_ARGUMENT_DENIED")
        bounded_timeout = self.config.max_timeout_seconds if timeout is None else timeout
        if isinstance(bounded_timeout, bool) or not isinstance(bounded_timeout, int) or bounded_timeout < 1:
            raise PolicyError("INVALID_TIMEOUT")
        bounded_timeout = min(bounded_timeout, self.config.max_timeout_seconds)
        executable_path = Path(executable)
        if not executable_path.is_absolute() or not executable_path.is_file() or executable_path.is_symlink():
            raise PolicyError("EXECUTABLE_INVALID")
        try:
            completed = subprocess.run(
                [str(executable_path), *argv],
                cwd=workdir,
                env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=bounded_timeout,
                shell=False,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise PolicyError("COMMAND_TIMEOUT") from exc
        stdout = completed.stdout[: self.config.max_output_bytes].decode("utf-8", errors="replace")
        stderr = completed.stderr[: self.config.max_output_bytes].decode("utf-8", errors="replace")
        stdout, out_redactions = redact_text(stdout)
        stderr, err_redactions = redact_text(stderr)
        return {
            "status": "OK" if completed.returncode == 0 else "ERROR",
            "command": command,
            "argv": argv,
            "cwd": str(workdir),
            "exit_code": completed.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "redaction_count": out_redactions + err_redactions,
            "shell": False,
        }
