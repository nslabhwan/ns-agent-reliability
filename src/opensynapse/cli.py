from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path

from ns_direct_channel.config import DirectChannelConfig
from ns_direct_channel.runtime import DirectChannelRuntime
from ns_direct_channel.stdio_server import run_stdio_server
from opensynapse.tunnel import (
    TunnelClientError,
    default_profile_dir,
    doctor_profile,
    prepare_profile,
    resolve_tunnel_client,
    run_profile,
)


def default_config_path() -> Path:
    return Path.home() / ".config" / "opensynapse" / "config.json"


def detect_node_type() -> str:
    prefix = os.environ.get("PREFIX", "")
    executable = sys.executable
    if (
        os.environ.get("TERMUX_VERSION")
        or "com.termux" in prefix
        or "/data/data/com.termux/" in executable
    ):
        return "android-termux"
    if platform.system() == "Linux":
        return "linux"
    return platform.system().lower()


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
    node_type = detect_node_type()
    if node_type not in {"linux", "android-termux"}:
        raise SystemExit("OpenSynapse alpha currently supports Linux and Android/Termux")

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
        "node_type": node_type,
        "config": str(target),
        "read_roots": config["read_roots"],
        "write_roots": config["write_roots"],
        "safe_commands": sorted(config["commands"]),
        "doctor": runtime.status(),
        "next": [
            "opensynapse connect openai --tunnel-id tunnel_...",
            "opensynapse serve --transport stdio",
        ],
    }
    if node_type == "linux":
        result["next"].append("opensynapse serve --transport http")
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
    data["node_type"] = detect_node_type()
    data["config"] = str(Path(args.config).expanduser())
    print(json.dumps(data, indent=2))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    config = DirectChannelConfig.load(Path(args.config).expanduser())
    if args.transport == "stdio":
        run_stdio_server(config)
        return 0

    if args.host not in {"127.0.0.1", "localhost", "::1"} and not args.allow_nonloopback:
        raise SystemExit(
            "refusing non-loopback HTTP bind; keep the local node private and use a reviewed authenticated HTTPS ingress"
        )
    try:
        from ns_direct_channel.server import create_server
    except ImportError as exc:
        raise SystemExit(
            "HTTP transport requires the optional OpenSynapse http extra; reinstall with [http]"
        ) from exc
    server = create_server(config)
    server.run(transport="http", host=args.host, port=args.port)
    return 0


def cmd_connect_openai(args: argparse.Namespace) -> int:
    config_path = Path(args.config).expanduser().resolve()
    DirectChannelConfig.load(config_path)

    tunnel_binary, installed = resolve_tunnel_client(
        args.tunnel_client,
        install_missing=not args.no_install_client,
    )
    profile_dir = Path(args.profile_dir).expanduser().resolve()
    prepared = prepare_profile(
        tunnel_binary=tunnel_binary,
        tunnel_id=args.tunnel_id,
        config_path=config_path,
        profile=args.profile,
        profile_dir=profile_dir,
    )
    if prepared.returncode != 0:
        detail = (prepared.stderr or prepared.stdout).strip()
        raise TunnelClientError(f"tunnel-client profile preparation failed: {detail}")

    result = {
        "status": "PREPARED" if args.prepare_only else "PREPARED_FOR_DOCTOR",
        "product": "OpenSynapse",
        "connection": "openai-secure-mcp-tunnel",
        "tunnel_client": str(tunnel_binary),
        "installed_official_client": installed,
        "profile": args.profile,
        "profile_dir": str(profile_dir),
        "config": str(config_path),
        "tunnel_id": args.tunnel_id,
        "secret_storage": "CONTROL_PLANE_API_KEY environment reference; value is not written by OpenSynapse",
    }

    if args.prepare_only:
        print(json.dumps(result, indent=2))
        return 0

    if not os.environ.get("CONTROL_PLANE_API_KEY"):
        raise TunnelClientError(
            "CONTROL_PLANE_API_KEY is required for OpenAI Secure MCP Tunnel; create a runtime API key with Tunnels Read + Use and export it in the environment"
        )

    doctor = doctor_profile(tunnel_binary, args.profile, profile_dir)
    if doctor.returncode != 0:
        detail = (doctor.stderr or doctor.stdout).strip()
        raise TunnelClientError(f"official tunnel-client doctor failed: {detail}")

    try:
        doctor_data = json.loads(doctor.stdout)
    except json.JSONDecodeError:
        doctor_data = {"raw": doctor.stdout.strip()}

    result["status"] = "READY"
    result["doctor"] = doctor_data
    print(json.dumps(result, indent=2))

    if args.no_run:
        return 0
    return run_profile(tunnel_binary, args.profile, profile_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="opensynapse",
        description="Let ChatGPT work on machines you own through bounded, verifiable device access.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    install = sub.add_parser("install", help="configure this machine as an OpenSynapse node")
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

    connect = sub.add_parser("connect", help="connect this OpenSynapse node to a supported AI host")
    connect_sub = connect.add_subparsers(dest="provider", required=True)
    openai = connect_sub.add_parser(
        "openai",
        help="connect through the official OpenAI Secure MCP Tunnel",
    )
    openai.add_argument("--tunnel-id", required=True, help="OpenAI tunnel id (tunnel_...)")
    openai.add_argument("--config", default=str(default_config_path()))
    openai.add_argument("--profile", default="opensynapse")
    openai.add_argument("--profile-dir", default=str(default_profile_dir()))
    openai.add_argument("--tunnel-client", help="explicit path to an official tunnel-client binary")
    openai.add_argument(
        "--no-install-client",
        action="store_true",
        help="fail instead of downloading the pinned official openai/tunnel-client release",
    )
    openai.add_argument(
        "--prepare-only",
        action="store_true",
        help="install/find tunnel-client and create the profile without contacting the control plane",
    )
    openai.add_argument(
        "--no-run",
        action="store_true",
        help="run the official Doctor but do not start the foreground tunnel daemon",
    )
    openai.set_defaults(func=cmd_connect_openai)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, OSError, json.JSONDecodeError, TunnelClientError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
