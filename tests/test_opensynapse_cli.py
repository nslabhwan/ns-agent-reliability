from __future__ import annotations

import json
from pathlib import Path

from opensynapse.cli import main


def test_install_then_status(tmp_path: Path, capsys) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    config = tmp_path / "config.json"

    rc = main([
        "install",
        "--root",
        str(root),
        "--write-root",
        str(root),
        "--enable-safe-commands",
        "--config",
        str(config),
    ])
    assert rc == 0
    install_out = json.loads(capsys.readouterr().out)
    assert install_out["status"] == "INSTALLED"
    assert install_out["product"] == "OpenSynapse"
    assert config.exists()
    assert oct(config.stat().st_mode & 0o777) == "0o600"

    rc = main(["status", "--config", str(config)])
    assert rc == 0
    status_out = json.loads(capsys.readouterr().out)
    assert status_out["product"] == "OpenSynapse"
    assert status_out["node_type"] == "linux"


def test_install_rejects_missing_root(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    config = tmp_path / "config.json"

    try:
        main(["install", "--root", str(missing), "--config", str(config)])
    except SystemExit as exc:
        assert "root does not exist" in str(exc)
    else:
        raise AssertionError("missing root must be rejected")


def test_detects_termux_node_type(tmp_path: Path, monkeypatch, capsys) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    config = tmp_path / "config.json"
    monkeypatch.setenv("TERMUX_VERSION", "0.118")
    monkeypatch.setenv("PREFIX", "/data/data/com.termux/files/usr")

    rc = main([
        "install",
        "--root",
        str(root),
        "--config",
        str(config),
    ])
    assert rc == 0
    output = json.loads(capsys.readouterr().out)
    assert output["node_type"] == "android-termux"

    rc = main(["status", "--config", str(config)])
    assert rc == 0
    status = json.loads(capsys.readouterr().out)
    assert status["node_type"] == "android-termux"
    assert status["authority"] == "SELF_HOSTED_ANDROID"


def test_actual_android_platform_with_termux_is_allowed(tmp_path: Path, monkeypatch, capsys) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    config = tmp_path / "config.json"
    monkeypatch.setenv("TERMUX_VERSION", "0.118")
    monkeypatch.setenv("PREFIX", "/data/data/com.termux/files/usr")
    monkeypatch.setattr("opensynapse.cli.platform.system", lambda: "Android")

    rc = main([
        "install",
        "--root",
        str(root),
        "--write-root",
        str(root),
        "--config",
        str(config),
    ])
    assert rc == 0
    output = json.loads(capsys.readouterr().out)
    assert output["node_type"] == "android-termux"
    assert output["doctor"]["authority"] == "SELF_HOSTED_ANDROID"


def test_demo_writes_and_reads_back_proof(tmp_path: Path, capsys) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    config = tmp_path / "config.json"

    rc = main([
        "install",
        "--root",
        str(root),
        "--write-root",
        str(root),
        "--config",
        str(config),
    ])
    assert rc == 0
    capsys.readouterr()

    rc = main(["demo", "--config", str(config)])
    assert rc == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "PASS"
    assert output["readback"]["content_match"] is True
    assert output["readback"]["sha256_match"] is True
    proof = root / "OPENSYNAPSE_DEMO.txt"
    assert proof.exists()
    assert "bounded execution demo" in proof.read_text(encoding="utf-8")


def test_demo_requires_explicit_write_root(tmp_path: Path, capsys) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    config = tmp_path / "config.json"
    assert main(["install", "--root", str(root), "--config", str(config)]) == 0
    capsys.readouterr()
    try:
        main(["demo", "--config", str(config)])
    except SystemExit as exc:
        assert "explicit writable workspace" in str(exc)
    else:
        raise AssertionError("demo must refuse read-only configurations")
