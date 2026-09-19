from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .config import DirectChannelConfig
from .runtime import DirectChannelRuntime
from .server import create_server


def default_config_path() -> Path:
    return Path.home() / ".config" / "ns-direct-channel" / "config.json"


def _safe_commands() -> dict[str, str]:
    result: dict[str, str] = {}
    for name in ("uptime", "df", "free"):
        found = shutil.which(name)
        if found:
            result[name] = str(Path(found).resolve())
    return result


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.config).expanduser()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"root does not exist or is not a directory: {root}")
    write_roots = [str(Path(p).expanduser().resolve()) for p in args.write_root]
    execute_roots = [str(root)] if args.enable_safe_commands else []
    config = {
        "read_roots": [str(root)],
        "write_roots": write_roots,
        "execute_roots": execute_roots,
        "commands": _safe_commands() if args.enable_safe_commands else {},
        "max_read_bytes": 65536,
        "max_write_bytes": 65536,
        "max_output_bytes": 65536,
        "max_timeout_seconds": 60,
    }
    DirectChannelConfig.from_dict(config)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not args.force:
        raise SystemExit(f"config already exists: {target}; pass --force to replace")
    target.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    target.chmod(0o600)
    print(json.dumps({"status": "CREATED", "config": str(target), "root": str(root), "safe_commands": sorted(config["commands"])}, indent=2))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    config = DirectChannelConfig.load(Path(args.config).expanduser())
    runtime = DirectChannelRuntime(config)
    print(json.dumps(runtime.status(), indent=2))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    config = DirectChannelConfig.load(Path(args.config).expanduser())
    server = create_server(config)
    if args.transport == "stdio":
        server.run()
        return 0
    if args.host not in {"127.0.0.1", "localhost", "::1"} and not args.allow_nonloopback:
        raise SystemExit("refusing non-loopback HTTP bind; use a secure tunnel/reverse proxy, or pass --allow-nonloopback deliberately")
    server.run(transport="http", host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ns-direct-channel", description="Self-hosted MCP bridge for your own Linux server")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a minimal local config")
    init.add_argument("--root", required=True, help="absolute or user-relative directory that AI clients may read")
    init.add_argument("--write-root", action="append", default=[], help="directory that AI clients may write; repeatable")
    init.add_argument("--enable-safe-commands", action="store_true", help="enable bounded uptime/df/free commands when available")
    init.add_argument("--config", default=str(default_config_path()))
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    doctor = sub.add_parser("doctor", help="validate config and print the effective public boundary")
    doctor.add_argument("--config", default=str(default_config_path()))
    doctor.set_defaults(func=cmd_doctor)

    serve = sub.add_parser("serve", help="run the MCP server")
    serve.add_argument("--config", default=str(default_config_path()))
    serve.add_argument("--transport", choices=("stdio", "http"), default="stdio")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8767)
    serve.add_argument("--allow-nonloopback", action="store_true", help="advanced: bind HTTP beyond loopback; secure it externally")
    serve.set_defaults(func=cmd_serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
