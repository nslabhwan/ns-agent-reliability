from __future__ import annotations

import asyncio
import json
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from fastmcp import Client


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_port(port: int, process: subprocess.Popen[bytes], timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"server exited early: {process.returncode}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.05)
    raise RuntimeError("OpenSynapse MCP server did not open its loopback port")


async def use_node(port: int, root: Path) -> dict[str, object]:
    endpoint = f"http://127.0.0.1:{port}/mcp"
    target = root / "verified.txt"
    async with Client(endpoint, timeout=10) as client:
        status = (await client.call_tool("dc_status", {})).data
        write = (
            await client.call_tool(
                "dc_write_text",
                {"path": str(target), "content": "OPENSYNAPSE_E2E_OK\n"},
            )
        ).data
        read = (await client.call_tool("dc_read_text", {"path": str(target)})).data
        bounded = None
        if "uptime" in (status.get("policy", {}).get("commands") or []):
            bounded = (await client.call_tool("dc_run_bounded", {"command": "uptime"})).data
        return {
            "status": "PASS",
            "endpoint": endpoint,
            "product": status.get("product"),
            "component": status.get("component"),
            "write_status": write.get("status"),
            "read_content": read.get("content"),
            "bounded_status": None if bounded is None else bounded.get("status"),
            "bounded_shell": None if bounded is None else bounded.get("shell"),
        }


def main() -> int:
    cli = Path(sys.executable).with_name("opensynapse")
    if not cli.is_file():
        raise RuntimeError(f"installed opensynapse CLI missing: {cli}")

    port = free_port()
    with tempfile.TemporaryDirectory(prefix="opensynapse-e2e-") as raw:
        root = Path(raw)
        config = root / "config.json"

        install = subprocess.run(
            [
                str(cli),
                "install",
                "--root",
                str(root),
                "--write-root",
                str(root),
                "--enable-safe-commands",
                "--config",
                str(config),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
        if install.returncode != 0:
            raise RuntimeError(install.stderr.decode("utf-8", errors="replace"))

        server = subprocess.Popen(
            [
                str(cli),
                "serve",
                "--transport",
                "http",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--config",
                str(config),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            wait_for_port(port, server)
            outcome = asyncio.run(use_node(port, root))
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)

    if outcome["product"] != "OpenSynapse":
        raise RuntimeError(f"wrong product identity: {outcome!r}")
    if outcome["write_status"] != "OK":
        raise RuntimeError(f"write failed: {outcome!r}")
    if outcome["read_content"] != "OPENSYNAPSE_E2E_OK\n":
        raise RuntimeError(f"readback mismatch: {outcome!r}")
    if outcome["bounded_status"] not in {None, "OK"}:
        raise RuntimeError(f"bounded command failed: {outcome!r}")
    if outcome["bounded_shell"] not in {None, False}:
        raise RuntimeError(f"unexpected shell execution: {outcome!r}")

    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
