from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_BLOCKED_PATH_PATTERNS = (
    ".env",
    ".ssh",
    ".aws",
    ".gnupg",
    "id_rsa",
    "id_ed25519",
)


class ConfigError(ValueError):
    pass


def _absolute_roots(values: Any, field: str) -> tuple[Path, ...]:
    if values is None:
        return ()
    if not isinstance(values, list) or any(not isinstance(v, str) or not v.startswith("/") for v in values):
        raise ConfigError(f"{field} must be a list of absolute paths")
    return tuple(Path(v).resolve(strict=False) for v in values)


@dataclass(frozen=True)
class DirectChannelConfig:
    read_roots: tuple[Path, ...]
    write_roots: tuple[Path, ...] = ()
    execute_roots: tuple[Path, ...] = ()
    commands: dict[str, str] | None = None
    blocked_path_patterns: tuple[str, ...] = DEFAULT_BLOCKED_PATH_PATTERNS
    max_read_bytes: int = 65536
    max_write_bytes: int = 65536
    max_output_bytes: int = 65536
    max_timeout_seconds: int = 60

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "DirectChannelConfig":
        if not isinstance(value, dict):
            raise ConfigError("config must be a JSON object")
        read_roots = _absolute_roots(value.get("read_roots"), "read_roots")
        if not read_roots:
            raise ConfigError("read_roots must contain at least one absolute path")
        write_roots = _absolute_roots(value.get("write_roots", []), "write_roots")
        execute_roots = _absolute_roots(value.get("execute_roots", []), "execute_roots")

        commands = value.get("commands", {})
        if not isinstance(commands, dict):
            raise ConfigError("commands must be an object mapping public names to absolute executables")
        clean_commands: dict[str, str] = {}
        for name, executable in commands.items():
            if not isinstance(name, str) or not name or not name.replace("-", "_").isalnum():
                raise ConfigError("command names must be simple identifiers")
            if not isinstance(executable, str) or not executable.startswith("/"):
                raise ConfigError(f"command {name!r} must use an absolute executable path")
            clean_commands[name] = executable

        patterns = value.get("blocked_path_patterns", list(DEFAULT_BLOCKED_PATH_PATTERNS))
        if not isinstance(patterns, list) or any(not isinstance(p, str) or not p for p in patterns):
            raise ConfigError("blocked_path_patterns must be a list of non-empty strings")

        def positive_int(name: str, default: int, maximum: int) -> int:
            raw = value.get(name, default)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0 or raw > maximum:
                raise ConfigError(f"{name} must be an integer between 1 and {maximum}")
            return raw

        return cls(
            read_roots=read_roots,
            write_roots=write_roots,
            execute_roots=execute_roots,
            commands=clean_commands,
            blocked_path_patterns=tuple(p.lower() for p in patterns),
            max_read_bytes=positive_int("max_read_bytes", 65536, 1024 * 1024),
            max_write_bytes=positive_int("max_write_bytes", 65536, 1024 * 1024),
            max_output_bytes=positive_int("max_output_bytes", 65536, 1024 * 1024),
            max_timeout_seconds=positive_int("max_timeout_seconds", 60, 300),
        )

    @classmethod
    def load(cls, path: str | Path) -> "DirectChannelConfig":
        target = Path(path)
        return cls.from_dict(json.loads(target.read_text(encoding="utf-8")))

    def public_view(self) -> dict[str, Any]:
        return {
            "read_roots": [str(p) for p in self.read_roots],
            "write_roots": [str(p) for p in self.write_roots],
            "execute_roots": [str(p) for p in self.execute_roots],
            "commands": sorted((self.commands or {}).keys()),
            "max_read_bytes": self.max_read_bytes,
            "max_write_bytes": self.max_write_bytes,
            "max_output_bytes": self.max_output_bytes,
            "max_timeout_seconds": self.max_timeout_seconds,
        }
