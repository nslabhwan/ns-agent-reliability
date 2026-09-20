from __future__ import annotations

import hashlib
import json
import os
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


SUPPORTED_TUNNEL_TAG = "v0.0.14"
GITHUB_RELEASE = (
    "https://api.github.com/repos/openai/tunnel-client/releases/tags/"
    + SUPPORTED_TUNNEL_TAG
)
USER_AGENT = "OpenSynapse/0.2"


class TunnelClientError(RuntimeError):
    pass


def default_install_root() -> Path:
    return Path.home() / ".local" / "share" / "opensynapse" / "tunnel-client"


def default_profile_dir() -> Path:
    return Path.home() / ".config" / "opensynapse" / "tunnel"


def _github_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def _download(url: str, target: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response, target.open("wb") as out:
        shutil.copyfileobj(response, out)


def _platform_asset(tag: str) -> str:
    if platform.system() != "Linux":
        raise TunnelClientError(
            "automatic tunnel-client install currently supports Linux only"
        )
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        arch = "amd64"
    elif machine in {"aarch64", "arm64"}:
        arch = "arm64"
    else:
        raise TunnelClientError(
            f"unsupported Linux architecture for tunnel-client: {machine}"
        )
    return f"tunnel-client-{tag}-linux-{arch}.zip"


def _asset_url(release: dict, name: str) -> str:
    for asset in release.get("assets", []):
        if asset.get("name") == name:
            url = asset.get("browser_download_url")
            if url:
                return str(url)
    raise TunnelClientError(
        f"official tunnel-client release asset not found: {name}"
    )


def _expected_sha256(sums_text: str, asset_name: str) -> str:
    for line in sums_text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].lstrip("*") == asset_name:
            digest = parts[0].lower()
            if len(digest) == 64 and all(
                ch in "0123456789abcdef" for ch in digest
            ):
                return digest
    raise TunnelClientError(
        f"checksum missing for official release asset: {asset_name}"
    )


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def install_official_tunnel_client(
    install_root: Path | None = None,
) -> dict[str, str]:
    root = (install_root or default_install_root()).expanduser()
    release = _github_json(GITHUB_RELEASE)
    tag = str(release.get("tag_name") or "")
    if tag != SUPPORTED_TUNNEL_TAG:
        raise TunnelClientError(
            "official tunnel-client release mismatch: "
            f"expected {SUPPORTED_TUNNEL_TAG}, got {tag}"
        )

    asset_name = _platform_asset(tag)
    zip_url = _asset_url(release, asset_name)
    sums_url = _asset_url(release, "SHA256SUMS.txt")

    with tempfile.TemporaryDirectory(prefix="opensynapse-tunnel-") as raw:
        tmp = Path(raw)
        archive = tmp / asset_name
        sums = tmp / "SHA256SUMS.txt"
        _download(zip_url, archive)
        _download(sums_url, sums)

        expected = _expected_sha256(
            sums.read_text(encoding="utf-8"),
            asset_name,
        )
        actual = _sha256(archive)
        if actual != expected:
            raise TunnelClientError(
                "official tunnel-client checksum mismatch: "
                f"expected {expected}, got {actual}"
            )

        version_dir = root / tag
        version_dir.mkdir(parents=True, exist_ok=True)
        binary = version_dir / "tunnel-client"
        cloudflared = version_dir / "cloudflared"

        with zipfile.ZipFile(archive) as zf:
            for member, target in (
                ("tunnel-client", binary),
                ("cloudflared", cloudflared),
            ):
                try:
                    data = zf.read(member)
                except KeyError as exc:
                    raise TunnelClientError(
                        f"official tunnel-client archive has no {member} binary"
                    ) from exc
                target.write_bytes(data)
                target.chmod(
                    target.stat().st_mode
                    | stat.S_IXUSR
                    | stat.S_IXGRP
                    | stat.S_IXOTH
                )

    current = root / "current"
    if current.is_symlink() or current.exists():
        if current.is_dir() and not current.is_symlink():
            raise TunnelClientError(
                f"refusing to replace non-symlink path: {current}"
            )
        current.unlink()
    current.symlink_to(version_dir.name)

    receipt = {
        "source": "openai/tunnel-client",
        "tag": tag,
        "asset": asset_name,
        "sha256": actual,
        "binary": str(binary),
        "cloudflared": str(cloudflared),
    }
    (version_dir / "opensynapse-install-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n",
        encoding="utf-8",
    )
    return receipt


def resolve_tunnel_client(
    explicit: str | None,
    install_missing: bool = True,
) -> tuple[Path, dict | None]:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file() or not os.access(path, os.X_OK):
            raise TunnelClientError(
                f"tunnel-client is not executable: {path}"
            )
        return path, None

    found = shutil.which("tunnel-client")
    if found:
        return Path(found).resolve(), None

    managed = default_install_root() / "current" / "tunnel-client"
    if managed.is_file() and os.access(managed, os.X_OK):
        return managed.resolve(), None

    if not install_missing:
        raise TunnelClientError(
            "tunnel-client not found; install the official "
            "openai/tunnel-client binary or allow automatic install"
        )

    receipt = install_official_tunnel_client()
    binary = Path(receipt["binary"]).resolve()
    return binary, receipt


def build_opensynapse_mcp_command(config_path: Path) -> str:
    argv = [
        sys.executable,
        "-m",
        "opensynapse.cli",
        "serve",
        "--transport",
        "stdio",
        "--config",
        str(config_path),
    ]
    return shlex.join(argv)


def prepare_profile(
    tunnel_binary: Path,
    tunnel_id: str,
    config_path: Path,
    profile: str,
    profile_dir: Path,
    api_key_ref: str = "env:CONTROL_PLANE_API_KEY",
) -> subprocess.CompletedProcess[str]:
    if not tunnel_id.startswith("tunnel_"):
        raise TunnelClientError("tunnel id must start with 'tunnel_'")

    profile_dir.mkdir(parents=True, exist_ok=True)
    mcp_command = build_opensynapse_mcp_command(config_path)
    argv = [
        str(tunnel_binary),
        "init",
        "--sample",
        "sample_mcp_stdio_local",
        "--profile",
        profile,
        "--profile-dir",
        str(profile_dir),
        "--tunnel-id",
        tunnel_id,
        "--mcp-command",
        mcp_command,
        "--control-plane-api-key-ref",
        api_key_ref,
        "--health-listen-addr",
        "127.0.0.1:0",
        "--force",
    ]
    return subprocess.run(
        argv,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def doctor_profile(
    tunnel_binary: Path,
    profile: str,
    profile_dir: Path,
) -> subprocess.CompletedProcess[str]:
    argv = [
        str(tunnel_binary),
        "doctor",
        "--profile",
        profile,
        "--profile-dir",
        str(profile_dir),
        "--json",
        "--explain",
    ]
    return subprocess.run(
        argv,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )


def run_profile(
    tunnel_binary: Path,
    profile: str,
    profile_dir: Path,
) -> int:
    argv = [
        str(tunnel_binary),
        "run",
        "--profile",
        profile,
        "--profile-dir",
        str(profile_dir),
    ]
    completed = subprocess.run(argv, check=False)
    return int(completed.returncode)
