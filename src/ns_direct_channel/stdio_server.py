from __future__ import annotations

import json
import sys
from typing import Any

from .config import DirectChannelConfig
from .policy import PolicyError
from .runtime import DirectChannelRuntime


TOOLS: list[dict[str, Any]] = [
    {
        "name": "dc_status",
        "description": "Return host/runtime status and the configured public capability boundary.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "dc_read_text",
        "description": "Read bounded UTF-8 text from an absolute path inside configured read roots.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "offset": {"type": "integer", "minimum": 0},
                "limit": {"type": ["integer", "null"], "minimum": 1},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "dc_list_directory",
        "description": "List a configured directory without following symbolic links.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "dc_tail_log",
        "description": "Return the bounded tail of a text log inside configured read roots.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "lines": {"type": "integer", "minimum": 1},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "dc_process_status",
        "description": "Return safe process status fields without argv or environment values.",
        "inputSchema": {
            "type": "object",
            "properties": {"pid": {"type": "integer", "minimum": 1}},
            "required": ["pid"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "dc_write_text",
        "description": "Atomically write text only inside configured write roots; optional SHA compare-and-swap.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "expected_sha256": {"type": ["string", "null"]},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
        "annotations": {
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
        },
    },
    {
        "name": "dc_run_bounded",
        "description": "Run a configured command by public name with shell disabled and bounded output/time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "args": {"type": ["array", "null"], "items": {"type": "string"}},
                "cwd": {"type": ["string", "null"]},
                "timeout": {"type": ["integer", "null"], "minimum": 1},
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False},
    },
]


def _denied(exc: Exception) -> dict[str, Any]:
    return {"status": "POLICY_DENIED", "error": str(exc)}


def call_tool(runtime: DirectChannelRuntime, name: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        if name == "dc_status":
            return runtime.status()
        if name == "dc_read_text":
            return runtime.read_text(
                args["path"],
                offset=args.get("offset", 0),
                limit=args.get("limit"),
            )
        if name == "dc_list_directory":
            return runtime.list_directory(args["path"], limit=args.get("limit", 200))
        if name == "dc_tail_log":
            return runtime.tail_log(args["path"], lines=args.get("lines", 100))
        if name == "dc_process_status":
            return runtime.process_status(int(args["pid"]))
        if name == "dc_write_text":
            return runtime.write_text(
                args["path"],
                args["content"],
                expected_sha256=args.get("expected_sha256"),
            )
        if name == "dc_run_bounded":
            return runtime.run_bounded(
                args["command"],
                args=args.get("args"),
                cwd=args.get("cwd"),
                timeout=args.get("timeout"),
            )
        raise ValueError("TOOL_UNKNOWN")
    except (PolicyError, OSError) as exc:
        return _denied(exc)


def handle_request(runtime: DirectChannelRuntime, message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}

    if request_id is None and method in {
        "notifications/initialized",
        "notifications/cancelled",
    }:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "OpenSynapse", "version": runtime.status()["version"]},
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        name = str(params.get("name", ""))
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "INVALID_ARGUMENTS"},
            }
        try:
            result = call_tool(runtime, name, arguments)
        except (KeyError, TypeError, ValueError) as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": str(exc)[:300]},
            }
        text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": text}],
                "structuredContent": result,
                "isError": False,
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "METHOD_NOT_FOUND"},
    }


def run_stdio_server(config: DirectChannelConfig) -> None:
    runtime = DirectChannelRuntime(config)
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
            if not isinstance(message, dict):
                raise ValueError("JSON_OBJECT_REQUIRED")
            response = handle_request(runtime, message)
        except Exception as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"PARSE_ERROR:{type(exc).__name__}"},
            }
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
