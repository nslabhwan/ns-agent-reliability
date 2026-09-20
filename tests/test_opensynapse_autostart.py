from __future__ import annotations

from pathlib import Path

import opensynapse.autostart as autostart


def test_user_unit_contains_only_key_file_reference(tmp_path: Path) -> None:
    text = autostart.build_user_unit(
        tunnel_id="tunnel_0123456789abcdef0123456789abcdef",
        config_path=tmp_path / "config.json",
        profile_dir=tmp_path / "profile",
        runtime_key_file=tmp_path / "runtime.key",
        python_executable=tmp_path / "venv" / "bin" / "python",
    )
    assert "Restart=always" in text
    assert "RestartSec=5" in text
    assert "--runtime-key-file" in text
    assert str(tmp_path / "runtime.key") in text
    assert "CONTROL_PLANE_API_KEY=" not in text
    assert "sk-" not in text


def test_install_user_autostart_writes_mode_600_and_enables(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "config.json"
    key = tmp_path / "runtime.key"
    config.write_text("{}")
    key.write_text("placeholder")
    unit = tmp_path / "opensynapse-tunnel.service"
    monkeypatch.setattr(autostart, "default_user_unit_path", lambda: unit)

    calls: list[tuple[str, ...]] = []

    class Result:
        returncode = 0
        stdout = "active\n"
        stderr = ""

    def fake_run(*args: str):
        calls.append(tuple(args))
        if args[0] == "is-enabled":
            r = Result(); r.stdout = "enabled\n"; return r
        if args[0] == "is-active":
            r = Result(); r.stdout = "active\n"; return r
        return Result()

    monkeypatch.setattr(autostart, "_run_user_systemctl", fake_run)
    monkeypatch.setattr(autostart, "_linger_state", lambda: "yes")
    out = autostart.install_user_autostart(
        tunnel_id="tunnel_0123456789abcdef0123456789abcdef",
        config_path=config,
        profile_dir=tmp_path / "profile",
        runtime_key_file=key,
    )
    assert unit.exists()
    assert oct(unit.stat().st_mode & 0o777) == "0o600"
    assert ("daemon-reload",) in calls
    assert ("enable", "--now", autostart.SERVICE_NAME) in calls
    assert out["reboot_recovery"] == "READY"


def test_install_reports_user_systemd_unavailable(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "config.json"
    key = tmp_path / "runtime.key"
    config.write_text("{}")
    key.write_text("placeholder")
    unit = tmp_path / "opensynapse-tunnel.service"
    monkeypatch.setattr(autostart, "default_user_unit_path", lambda: unit)

    class Result:
        returncode = 1
        stdout = ""
        stderr = "Failed to connect to bus"

    monkeypatch.setattr(autostart, "_run_user_systemctl", lambda *args: Result())
    out = autostart.install_user_autostart(
        tunnel_id="tunnel_0123456789abcdef0123456789abcdef",
        config_path=config,
        profile_dir=tmp_path / "profile",
        runtime_key_file=key,
    )
    assert out["status"] == "UNIT_WRITTEN_SYSTEMD_USER_UNAVAILABLE"
    assert out["reboot_recovery"] == "PENDING"


def test_status_distinguishes_login_recovery_from_unattended_boot(tmp_path: Path, monkeypatch) -> None:
    unit = tmp_path / "opensynapse-tunnel.service"
    unit.write_text("[Unit]\n")
    monkeypatch.setattr(autostart, "default_user_unit_path", lambda: unit)

    class Result:
        returncode = 0
        stdout = "active\n"
        stderr = ""

    def fake_run(*args: str):
        r = Result()
        r.stdout = "enabled\n" if args[0] == "is-enabled" else "active\n"
        return r

    monkeypatch.setattr(autostart, "_run_user_systemctl", fake_run)
    monkeypatch.setattr(autostart, "_linger_state", lambda: "no")
    out = autostart.user_autostart_status()
    assert out["reboot_recovery"] == "READY_AFTER_LOGIN"
    assert str(out["unattended_boot_next"]).startswith("sudo loginctl enable-linger")


def test_user_unit_preserves_virtualenv_python_symlink_path(tmp_path: Path) -> None:
    real_python = tmp_path / "usr" / "bin" / "python3.11"
    real_python.parent.mkdir(parents=True)
    real_python.write_text("python")
    venv_python = tmp_path / "venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.symlink_to(real_python)

    text = autostart.build_user_unit(
        tunnel_id="tunnel_0123456789abcdef0123456789abcdef",
        config_path=tmp_path / "config.json",
        profile_dir=tmp_path / "profile",
        runtime_key_file=tmp_path / "runtime.key",
        python_executable=venv_python,
    )
    assert str(venv_python) in text
    assert str(real_python) not in text
