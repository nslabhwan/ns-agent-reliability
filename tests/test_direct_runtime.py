from __future__ import annotations

import os
from pathlib import Path

import pytest

from ns_direct_channel.config import DirectChannelConfig
from ns_direct_channel.policy import PolicyError
from ns_direct_channel.runtime import DirectChannelRuntime


def make_runtime(root: Path) -> DirectChannelRuntime:
    printf = Path("/usr/bin/printf")
    commands = {"printf": str(printf)} if printf.is_file() else {}
    config = DirectChannelConfig.from_dict({
        "read_roots": [str(root)],
        "write_roots": [str(root)],
        "execute_roots": [str(root)],
        "commands": commands,
    })
    return DirectChannelRuntime(config)


def test_read_write_list_and_cas(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    source = tmp_path / "hello.txt"
    source.write_text("hello\nworld\n", encoding="utf-8")

    read = runtime.read_text(str(source))
    assert read["status"] == "OK"
    assert read["content"] == "hello\nworld\n"

    listing = runtime.list_directory(str(tmp_path))
    assert {row["name"] for row in listing["entries"]} == {"hello.txt"}

    target = tmp_path / "written.txt"
    first = runtime.write_text(str(target), "first\n")
    second = runtime.write_text(str(target), "second\n", expected_sha256=first["after_sha256"])
    assert second["status"] == "OK"
    assert target.read_text(encoding="utf-8") == "second\n"

    with pytest.raises(PolicyError, match="EXPECTED_SHA256_MISMATCH"):
        runtime.write_text(str(target), "third\n", expected_sha256="0" * 64)


def test_symlink_escape_denied(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    outside = tmp_path.parent / "outside-direct-channel.txt"
    outside.write_text("outside", encoding="utf-8")
    link = tmp_path / "escape"
    link.symlink_to(outside)
    with pytest.raises(PolicyError, match="SYMLINK_COMPONENT_DENIED"):
        runtime.read_text(str(link))


def test_process_status_never_returns_argv_or_environment(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    result = runtime.process_status(os.getpid())
    assert result["status"] == "OK"
    assert result["argv_returned"] is False
    assert result["environment_returned"] is False
    assert "Name" in result["process"]


def test_bounded_execution_uses_configured_executable(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    if "printf" not in (runtime.config.commands or {}):
        pytest.skip("/usr/bin/printf unavailable")
    result = runtime.run_bounded("printf", ["portable-ok"], cwd=str(tmp_path))
    assert result["status"] == "OK"
    assert result["stdout"] == "portable-ok"
    assert result["shell"] is False


def test_unconfigured_command_denied(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    with pytest.raises(PolicyError, match="COMMAND_NOT_ALLOWED"):
        runtime.run_bounded("anything-else", [], cwd=str(tmp_path))
