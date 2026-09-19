from __future__ import annotations

import json
import os
from pathlib import Path

from opensynapse.cli import main
from opensynapse.tunnel import _expected_sha256, build_opensynapse_mcp_command


def test_expected_sha256_selects_exact_asset() -> None:
    name = "tunnel-client-v0.0.14-linux-amd64.zip"
    digest = "a" * 64
    text = f"{digest}  {name}\n" + ("b" * 64) + "  other.zip\n"
    assert _expected_sha256(text, name) == digest


def test_mcp_command_quotes_config_path() -> None:
    command = build_opensynapse_mcp_command(Path("/tmp/config with space.json"))
    assert "-m opensynapse.cli serve" in command
    assert "--transport stdio" in command
    assert "'/tmp/config with space.json'" in command


def test_connect_openai_prepare_only_uses_secret_reference(tmp_path: Path, monkeypatch, capsys) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    config = tmp_path / "config.json"
    assert main(["install", "--root", str(root), "--config", str(config)]) == 0
    capsys.readouterr()

    log = tmp_path / "argv.json"
    fake = tmp_path / "tunnel-client"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['FAKE_TUNNEL_LOG']).write_text(json.dumps(sys.argv[1:]))\n"
        "raise SystemExit(0)\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    monkeypatch.setenv("FAKE_TUNNEL_LOG", str(log))
    monkeypatch.delenv("CONTROL_PLANE_API_KEY", raising=False)

    profile_dir = tmp_path / "profiles"
    rc = main([
        "connect",
        "openai",
        "--tunnel-id",
        "tunnel_0123456789abcdef",
        "--config",
        str(config),
        "--profile-dir",
        str(profile_dir),
        "--tunnel-client",
        str(fake),
        "--prepare-only",
    ])
    assert rc == 0

    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "PREPARED"
    assert "CONTROL_PLANE_API_KEY" in output["secret_storage"]

    argv = json.loads(log.read_text())
    assert argv[0] == "init"
    assert "--control-plane-api-key-ref" in argv
    ref_index = argv.index("--control-plane-api-key-ref") + 1
    assert argv[ref_index] == "env:CONTROL_PLANE_API_KEY"
    assert "--health-listen-addr" in argv
    health_index = argv.index("--health-listen-addr") + 1
    assert argv[health_index] == "127.0.0.1:0"
    assert not any("sk-" in value for value in argv)


def test_connect_openai_requires_runtime_key_after_prepare(tmp_path: Path, monkeypatch, capsys) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    config = tmp_path / "config.json"
    assert main(["install", "--root", str(root), "--config", str(config)]) == 0
    capsys.readouterr()

    fake = tmp_path / "tunnel-client"
    fake.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.delenv("CONTROL_PLANE_API_KEY", raising=False)

    rc = main([
        "connect",
        "openai",
        "--tunnel-id",
        "tunnel_0123456789abcdef",
        "--config",
        str(config),
        "--profile-dir",
        str(tmp_path / "profiles"),
        "--tunnel-client",
        str(fake),
        "--no-run",
    ])
    assert rc == 2
    assert "CONTROL_PLANE_API_KEY is required" in capsys.readouterr().err
