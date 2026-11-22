from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def evaluate_demo(cwd: Path) -> dict[str, Any]:
    root = cwd.resolve()
    config_path = root / "service.json"

    if config_path.is_symlink():
        return {"status": "UNHEALTHY", "reason": "CONFIG_SYMLINK_DENIED", "config": str(config_path)}
    if not config_path.is_file():
        return {"status": "UNHEALTHY", "reason": "CONFIG_MISSING", "config": str(config_path)}

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "UNHEALTHY", "reason": "CONFIG_INVALID_JSON", "config": str(config_path)}

    if not isinstance(data, dict):
        return {"status": "UNHEALTHY", "reason": "CONFIG_NOT_OBJECT", "config": str(config_path)}

    enabled_ok = data.get("enabled") is True
    port = data.get("listen_port")
    port_ok = isinstance(port, int) and not isinstance(port, bool) and 1024 <= port <= 65535
    upstream_ok = data.get("upstream") == "http://127.0.0.1:9000"

    checks = {
        "enabled": enabled_ok,
        "listen_port": port_ok,
        "upstream": upstream_ok,
    }
    if not enabled_ok:
        reason = "SERVICE_DISABLED"
    elif not port_ok:
        reason = "LISTEN_PORT_INVALID"
    elif not upstream_ok:
        reason = "UPSTREAM_INVALID"
    else:
        reason = "HEALTHY"

    return {
        "status": "HEALTHY" if all(checks.values()) else "UNHEALTHY",
        "reason": reason,
        "service": data.get("service"),
        "checks": checks,
        "config": str(config_path),
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        print(json.dumps({"status": "ERROR", "reason": "ARGUMENTS_NOT_ALLOWED"}, indent=2))
        return 2
    result = evaluate_demo(Path.cwd())
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "HEALTHY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
