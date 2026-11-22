from __future__ import annotations

import json
from pathlib import Path

from opensynapse.demo_health import evaluate_demo, main


def _write_config(root: Path, *, enabled: bool) -> None:
    (root / "service.json").write_text(
        json.dumps({
            "service": "demo-api",
            "enabled": enabled,
            "listen_port": 8080,
            "upstream": "http://127.0.0.1:9000",
        }) + "\n",
        encoding="utf-8",
    )


def test_demo_health_detects_disabled_service(tmp_path: Path) -> None:
    _write_config(tmp_path, enabled=False)
    result = evaluate_demo(tmp_path)
    assert result["status"] == "UNHEALTHY"
    assert result["reason"] == "SERVICE_DISABLED"
    assert result["checks"]["listen_port"] is True
    assert result["checks"]["upstream"] is True


def test_demo_health_passes_after_minimum_fix(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_config(tmp_path, enabled=True)
    monkeypatch.chdir(tmp_path)
    assert main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "HEALTHY"
    assert all(output["checks"].values())
