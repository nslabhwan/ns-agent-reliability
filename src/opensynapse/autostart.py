from __future__ import annotations

import os
import subprocess
import sys
import getpass
from pathlib import Path


SERVICE_NAME = "opensynapse-tunnel.service"


def default_user_unit_path() -> Path:
    return Path.home() / ".config" / "systemd" / "user" / SERVICE_NAME


def _quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def build_user_unit(
    *,
    tunnel_id: str,
    config_path: Path,
    profile_dir: Path,
    runtime_key_file: Path,
    python_executable: Path | None = None,
) -> str:
    if not tunnel_id.startswith("tunnel_"):
        raise ValueError("tunnel id must start with 'tunnel_'")
    # Do not resolve the virtualenv interpreter symlink: resolving it can collapse
    # ~/.local/share/opensynapse/venv/bin/python to /usr/bin/python3.x and lose
    # the venv site-packages at service startup. Preserve the executable path.
    py = Path(os.path.abspath(str(python_executable or sys.executable)))
    argv = [
        str(py),
        "-m",
        "opensynapse.cli",
        "connect",
        "openai",
        "--tunnel-id",
        tunnel_id,
        "--config",
        str(config_path.resolve()),
        "--profile-dir",
        str(profile_dir.resolve()),
        "--runtime-key-file",
        str(runtime_key_file.resolve()),
    ]
    exec_start = " ".join(_quote(part) for part in argv)
    return (
        "[Unit]\n"
        "Description=OpenSynapse Secure MCP Tunnel\n"
        "After=network-online.target\n"
        "Wants=network-online.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"ExecStart={exec_start}\n"
        "Restart=always\n"
        "RestartSec=5\n"
        "UMask=0077\n\n"
        "[Install]\n"
        "WantedBy=default.target\n"
    )


def _run_user_systemctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["systemctl", "--user", *args],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def install_user_autostart(
    *,
    tunnel_id: str,
    config_path: Path,
    profile_dir: Path,
    runtime_key_file: Path,
    activate: bool = True,
) -> dict[str, object]:
    if os.name != "posix":
        raise OSError("systemd user autostart is currently supported on Linux only")
    if not runtime_key_file.is_file():
        raise FileNotFoundError(f"runtime key file not found: {runtime_key_file}")
    if not config_path.is_file():
        raise FileNotFoundError(f"OpenSynapse config not found: {config_path}")

    unit_path = default_user_unit_path()
    unit_path.parent.mkdir(parents=True, exist_ok=True)
    unit_path.write_text(
        build_user_unit(
            tunnel_id=tunnel_id,
            config_path=config_path,
            profile_dir=profile_dir,
            runtime_key_file=runtime_key_file,
        ),
        encoding="utf-8",
    )
    unit_path.chmod(0o600)

    reload_result = _run_user_systemctl("daemon-reload")
    if reload_result.returncode != 0:
        detail = (reload_result.stderr or reload_result.stdout).strip()
        return {
            "status": "UNIT_WRITTEN_SYSTEMD_USER_UNAVAILABLE",
            "unit": str(unit_path),
            "detail": detail,
            "reboot_recovery": "PENDING",
        }

    if not activate:
        return {
            "status": "UNIT_WRITTEN",
            "unit": str(unit_path),
            "reboot_recovery": "PENDING_ENABLE",
        }

    enabled = _run_user_systemctl("enable", "--now", SERVICE_NAME)
    if enabled.returncode != 0:
        detail = (enabled.stderr or enabled.stdout).strip()
        return {
            "status": "UNIT_WRITTEN_ENABLE_FAILED",
            "unit": str(unit_path),
            "detail": detail,
            "reboot_recovery": "PENDING",
        }

    state = user_autostart_status()
    state["status"] = "ENABLED" if state.get("active") == "active" else "ENABLED_NOT_ACTIVE"
    return state


def _linger_state() -> str:
    try:
        completed = subprocess.run(
            ["loginctl", "show-user", getpass.getuser(), "-p", "Linger", "--value"],
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"
    if completed.returncode != 0:
        return "unknown"
    value = (completed.stdout or "").strip().lower()
    return value if value in {"yes", "no"} else "unknown"


def user_autostart_status() -> dict[str, object]:
    unit_path = default_user_unit_path()
    enabled = _run_user_systemctl("is-enabled", SERVICE_NAME)
    active = _run_user_systemctl("is-active", SERVICE_NAME)
    linger = _linger_state()
    service_ready = enabled.returncode == 0 and active.returncode == 0
    if service_ready and linger == "yes":
        reboot_recovery = "READY"
    elif service_ready:
        reboot_recovery = "READY_AFTER_LOGIN"
    else:
        reboot_recovery = "NOT_READY"
    return {
        "unit": str(unit_path),
        "unit_exists": unit_path.is_file(),
        "enabled": (enabled.stdout or "").strip() or "unknown",
        "active": (active.stdout or "").strip() or "unknown",
        "linger": linger,
        "reboot_recovery": reboot_recovery,
        "unattended_boot_next": (
            f"sudo loginctl enable-linger {getpass.getuser()}"
            if service_ready and linger == "no"
            else None
        ),
    }


def remove_user_autostart() -> dict[str, object]:
    unit_path = default_user_unit_path()
    _run_user_systemctl("disable", "--now", SERVICE_NAME)
    if unit_path.exists():
        unit_path.unlink()
    _run_user_systemctl("daemon-reload")
    return {"status": "REMOVED", "unit": str(unit_path), "unit_exists": unit_path.exists()}
