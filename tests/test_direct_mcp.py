from __future__ import annotations

from pathlib import Path

from fastmcp import Client

from ns_direct_channel.config import DirectChannelConfig
from ns_direct_channel.server import create_server


async def test_real_mcp_protocol_status_and_read(tmp_path: Path) -> None:
    source = tmp_path / "probe.txt"
    source.write_text("DIRECT_CHANNEL_E2E_OK\n", encoding="utf-8")
    config = DirectChannelConfig.from_dict({
        "read_roots": [str(tmp_path)],
        "write_roots": [],
        "execute_roots": [],
        "commands": {},
    })
    server = create_server(config)
    async with Client(server) as client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools}
        assert {"dc_status", "dc_read_text", "dc_run_bounded"}.issubset(names)

        status = await client.call_tool("dc_status", {})
        assert status.data["status"] == "OK"
        assert status.data["product"] == "OpenSynapse"

        read = await client.call_tool("dc_read_text", {"path": str(source)})
        assert read.data["status"] == "OK"
        assert read.data["content"] == "DIRECT_CHANNEL_E2E_OK\n"


async def test_mcp_policy_denial_is_structured(tmp_path: Path) -> None:
    config = DirectChannelConfig.from_dict({
        "read_roots": [str(tmp_path)],
        "write_roots": [],
        "execute_roots": [],
        "commands": {},
    })
    server = create_server(config)
    async with Client(server) as client:
        result = await client.call_tool("dc_read_text", {"path": "/etc/passwd"})
        assert result.data == {"status": "POLICY_DENIED", "error": "PATH_OUTSIDE_ALLOWED_ROOTS"}
