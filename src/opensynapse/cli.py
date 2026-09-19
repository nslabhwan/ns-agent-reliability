from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
from pathlib import Path

from ns_direct_channel.config import DirectChannelConfig
from ns_direct_channel.runtime import DirectChannelRuntime
from ns_direct_channel.server import create_server


def default_config_path() -> Path:
    return Path.home() / ".config" / "opensynapse" / "config.json"


def _safe_commands() -> dict[str, str]:
    result: dict[str, str] = {}
    for name in ("uptime", "df", "free"):
        found = shutil.which(name)
        if found:
            result[name] = str(Path(found).resolve())
    return result


def _load_runtime(config_path: str) -> DirectChannelRuntime:
    config = DirectChannelConfig.load(Path(config_path).expanduser())
    return DirectChannelRuntime(config)


def cmd_install(args: argparse.Namespace) -> int:
    if platform.system() != "Linux":
        raise SystemExit("OpenSynapse alpha installer currently supports Linux only")

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"root does not exist or is not a directory: {root}")

    write_roots = [str(Path(p).expanduser().resolve()) for p in args.write_root]
    for path in write_roots:
        if not Path(path).is_dir():
            raise SystemExit(f"write root does not exist or is not a directory: {path}")

    target = Path(args.config).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "read_roots": [str(root)],
        "write_roots": write_roots,
        "execute_roots": [str(root)] if args.enable_safe_commands else [],
        "commands": _safe_commands() if args.enable_safe_commands else {},
        "max_read_bytes": 65536,
        "max_write_bytes": 65536,
        "max_output_bytes": 65536,
        "max_timeout_seconds": 60,
    }
    DirectChannelConfig.from_dict(config)

    if target.exists() and not args.force:
        raise SystemExit(f"config already exists: {target}; pass --force to replace")

    target.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    target.chmod(0o600)

    runtime = DirectChannelRuntime(DirectChannelConfig.from_dict(config))
    result = {
        "status": "INSTALLED",
        "product": "OpenSynapse",
        "node_type": "linux",
        "config": str(target),
        "read_roots": config["read_roots"],
        "write_roots": config["write_roots"],
        "safe_commands": sorted(config["commands"]),
        "doctor": runtime.status(),
        "next": [
            "opensynapse serve --transport http",
            "connect the HTTPS MCP endpoint through the supported OpenSynapse/ChatGPT connection flow",
        ],
    }
    print(json.dumps(result, indent=2))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    runtime = _load_runtime(args.config)
    print(json.dumps(runtime.status(), indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    runtime = _load_runtime(args.config)
    data = runtime.status()
    data["product"] = "OpenSynapse"
    data["node_type"] = "linux"
    data["config"] = str(Path(args.config).expanduser())
    print(json.dumps(data, indent=2))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    config = DirectChannelConfig.load(Path(args.config).expanduser())
    server = create_server(config)
    if args.transport == "stdio":
        server.run()
        return 0
    if args.host not in {"127.0.0.1", "localhost", "::1"} and not args.allow_nonloopback:
        raise SystemExit(
            "refusing non-loopback HTTP bind; keep the local node private and use a reviewed authenticated HTTPS ingress"
        )
    server.run(transport="http", host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="opensynapse",
        description="Let ChatGPT work on machines you own through bounded, verifiable device access.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    install = sub.add_parser("install", help="configure this Linux machine as an OpenSynapse node")
    install.add_argument("--root", required=True, help="directory AI may read")
    install.add_argument("--write-root", action="append", default=[], help="directory AI may write; repeatable")
    install.add_argument(
        "--enable-safe-commands",
        action="store_true",
        help="enable bounded uptime/df/free commands when available",
    )
    install.add_argument("--config", default=str(default_config_path()))
    install.add_argument("--force", action="store_true")
    install.set_defaults(func=cmd_install)

    doctor = sub.add_parser("doctor", help="validate configuration and show the effective access boundary")
    doctor.add_argument("--config", default=str(default_config_path()))
    doctor.set_defaults(func=cmd_doctor)

    status = sub.add_parser("status", help="show this node's current OpenSynapse boundary")
    status.add_argument("--config", default=str(default_config_path()))
    status.set_defaults(func=cmd_status)

    serve = sub.add_parser("serve", help="serve the local MCP node")
    serve.add_argument("--config", default=str(default_config_path()))
    serve.add_argument("--transport", choices=("stdio", "http"), default="stdio")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8767)
    serve.add_argument("--allow-nonloopback", action="store_true")
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
