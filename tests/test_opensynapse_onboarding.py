from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "onboard-openai.sh"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def test_guided_onboarding_finishes_without_secret_in_state(tmp_path: Path) -> None:
    home = tmp_path / "home"
    bin_dir = home / ".local" / "bin"
    fake_bin = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "curl",
        "#!/bin/sh\nprintf '%s\\n' '#!/bin/sh' 'exit 0'\n",
    )
    _write_executable(
        bin_dir / "opensynapse",
        """#!/bin/sh
if [ "$1 $2" = "autostart status" ]; then
  printf '%s\\n' '{"enabled":"enabled","active":"active","linger":"yes","reboot_recovery":"READY"}'
  exit 0
fi
if [ "$1" = "status" ]; then
  printf '%s\\n' '{"status":"OK","version":"test"}'
  exit 0
fi
exit 0
""",
    )

    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "PATH": f"{fake_bin}:{env.get('PATH', '')}",
            "OPENSYNAPSE_BIN_DIR": str(bin_dir),
        }
    )
    tunnel_id = "tunnel_0123456789abcdef0123456789abcdef"
    completed = subprocess.run(
        [str(SCRIPT), tunnel_id],
        text=True,
        capture_output=True,
        env=env,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "CONNECTED_AUTOSTART_READY" in completed.stdout
    assert "Authentication: None / No authentication" in completed.stdout
    assert "OPENSYNAPSE_E2E.txt" in completed.stdout

    state = json.loads((home / ".config" / "opensynapse" / "onboarding.json").read_text())
    assert state["tunnel_id"] == tunnel_id
    assert state["local_status"] == "CONNECTED_AUTOSTART_READY"
    assert state["secret_stored_here"] is False
    assert "key" not in " ".join(state).lower()


def test_guided_onboarding_rejects_bad_tunnel_id(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")
    completed = subprocess.run(
        [str(SCRIPT), "not-a-tunnel"],
        text=True,
        capture_output=True,
        env=env,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 2
    assert "tunnel ID must look like" in completed.stderr
