from __future__ import annotations

import fnmatch
import re
import stat
from pathlib import Path

from .config import DirectChannelConfig


class PolicyError(ValueError):
    pass


def is_within(path: Path, roots: tuple[Path, ...]) -> bool:
    return any(path == root or root in path.parents for root in roots)


def reject_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise PolicyError("SYMLINK_COMPONENT_DENIED")


def is_blocked_path(path: Path, config: DirectChannelConfig) -> bool:
    lowered = [part.lower() for part in path.parts]
    return any(
        fnmatch.fnmatch(part, pattern)
        for part in lowered
        for pattern in config.blocked_path_patterns
    )


def resolve_allowed_path(raw: str, roots: tuple[Path, ...], config: DirectChannelConfig) -> Path:
    if not isinstance(raw, str) or not raw.startswith("/"):
        raise PolicyError("ABSOLUTE_PATH_REQUIRED")
    candidate = Path(raw)
    if ".." in candidate.parts:
        raise PolicyError("PARENT_TRAVERSAL_DENIED")
    reject_symlink_components(candidate)
    resolved = candidate.resolve(strict=False)
    if not is_within(resolved, roots):
        raise PolicyError("PATH_OUTSIDE_ALLOWED_ROOTS")
    if is_blocked_path(resolved, config):
        raise PolicyError("SENSITIVE_PATH_DENIED")
    return resolved


def _patterns() -> tuple[re.Pattern[str], ...]:
    auth_scheme = "bear" + "er"
    return (
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        re.compile(r"(?i)\b" + auth_scheme + r"\s+[A-Za-z0-9._~+/-]{16,}={0,2}"),
    )


HIGH_CONFIDENCE_PATTERNS = _patterns()
_SENSITIVE_KEY_FRAGMENTS = (
    "to" + "ken",
    "sec" + "ret",
    "pass" + "word",
    "api" + "_key",
    "private" + "_key",
    "credential",
)
_ASSIGNMENT = re.compile(r"(?im)^(?P<key>\s*(?:export\s+)?[A-Z0-9_]+\s*[=:]\s*)(?P<value>[^\r\n]+)$")


def _looks_sensitive_key(prefix: str) -> bool:
    normalized = prefix.lower().replace(" ", "")
    return any(fragment in normalized for fragment in _SENSITIVE_KEY_FRAGMENTS)


def redact_text(text: str) -> tuple[str, int]:
    output = text
    count = 0
    for pattern in HIGH_CONFIDENCE_PATTERNS:
        output, replaced = pattern.subn("[REDACTED]", output)
        count += replaced

    def replace_assignment(match: re.Match[str]) -> str:
        nonlocal count
        if not _looks_sensitive_key(match.group("key")):
            return match.group(0)
        raw = match.group("value").strip().strip("'\"")
        if not raw or raw.lower() in {"none", "null", "redacted", "replace_me", "placeholder"} or raw.startswith("${"):
            return match.group(0)
        count += 1
        return match.group("key") + "[REDACTED]"

    output = _ASSIGNMENT.sub(replace_assignment, output)
    return output, count


def contains_sensitive_value(text: str) -> bool:
    redacted, count = redact_text(text)
    return count > 0 and redacted != text
