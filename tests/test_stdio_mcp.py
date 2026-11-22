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


def test_stdio_server_recovery_read_fix_verify(tmp_path: Path) -> None:
    import json
    import sys

    workspace = tmp_path / "workspace"
    demo_dir = workspace / "server-recovery-demo"
    demo_dir.mkdir(parents=True)
    verifier = Path(sys.executable).parent / "opensynapse-demo-health"
    assert verifier.is_file() and not verifier.is_symlink()

    config_path = demo_dir / "service.json"
    log_path = demo_dir / "service.log"
    original = {
        "service": "demo-api",
        "enabled": False,
        "listen_port": 8080,
        "upstream": "http://127.0.0.1:9000",
    }
    config_path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
    log_path.write_text(
        "ERROR startup refused: service is disabled by service.json\n"
        "INFO listener and upstream settings passed validation\n",
        encoding="utf-8",
    )

    runtime = DirectChannelRuntime(DirectChannelConfig.from_dict({
        "read_roots": [str(workspace)],
        "write_roots": [str(workspace)],
        "execute_roots": [str(workspace)],
        "commands": {"demohealth": str(verifier)},
        "max_read_bytes": 65536,
        "max_write_bytes": 65536,
        "max_output_bytes": 65536,
        "max_timeout_seconds": 60,
    }))

    read_log = handle_request(runtime, {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "dc_read_text",
            "arguments": {"path": str(log_path)},
        },
    })
    assert "service is disabled" in read_log["result"]["structuredContent"]["content"]

    read_config = handle_request(runtime, {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "dc_read_text",
            "arguments": {"path": str(config_path)},
        },
    })
    before = json.loads(read_config["result"]["structuredContent"]["content"])
    assert before == original

    repaired = dict(before)
    repaired["enabled"] = True
    write_fix = handle_request(runtime, {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "dc_write_text",
            "arguments": {
                "path": str(config_path),
                "content": json.dumps(repaired, indent=2) + "\n",
            },
        },
    })
    assert write_fix["result"]["structuredContent"]["status"] == "OK"

    verify = handle_request(runtime, {
        "jsonrpc": "2.0",
        "id": 13,
        "method": "tools/call",
        "params": {
            "name": "dc_run_bounded",
            "arguments": {
                "command": "demohealth",
                "cwd": str(demo_dir),
            },
        },
    })
    result = verify["result"]["structuredContent"]
    assert result["exit_code"] == 0
    health = json.loads(result["stdout"])
    assert health["status"] == "HEALTHY"
    assert all(health["checks"].values())

    final = json.loads(config_path.read_text(encoding="utf-8"))
    assert {k: final[k] for k in final if k != "enabled"} == {
        k: original[k] for k in original if k != "enabled"
    }
    assert final["enabled"] is True
