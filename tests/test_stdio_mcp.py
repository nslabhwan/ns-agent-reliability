from __future__ import annotations

from pathlib import Path

from ns_direct_channel.config import DirectChannelConfig
from ns_direct_channel.runtime import DirectChannelRuntime
from ns_direct_channel.stdio_server import handle_request


def _runtime(tmp_path: Path) -> DirectChannelRuntime:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    cfg = DirectChannelConfig.from_dict({
        "read_roots": [str(workspace)],
        "write_roots": [str(workspace)],
        "execute_roots": [],
        "commands": {},
        "max_read_bytes": 65536,
        "max_write_bytes": 65536,
        "max_output_bytes": 65536,
        "max_timeout_seconds": 60,
    })
    return DirectChannelRuntime(cfg)


def test_stdio_initialize_and_tool_list(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    init = handle_request(runtime, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-06-18"},
    })
    assert init is not None
    assert init["result"]["serverInfo"]["name"] == "OpenSynapse"

    listed = handle_request(runtime, {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    })
    names = {tool["name"] for tool in listed["result"]["tools"]}
    assert names == {
        "dc_status",
        "dc_read_text",
        "dc_list_directory",
        "dc_tail_log",
        "dc_process_status",
        "dc_write_text",
        "dc_run_bounded",
    }


def test_stdio_write_then_readback(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    target = tmp_path / "workspace" / "proof.txt"

    wrote = handle_request(runtime, {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "dc_write_text",
            "arguments": {"path": str(target), "content": "ANDROID_STDIO_OK\n"},
        },
    })
    assert wrote["result"]["structuredContent"]["status"] == "OK"

    read = handle_request(runtime, {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "dc_read_text",
            "arguments": {"path": str(target)},
        },
    })
    assert read["result"]["structuredContent"]["content"] == "ANDROID_STDIO_OK\n"
