#!/usr/bin/env python3
"""Deterministic content QA for public Markdown/HTML/text surfaces."""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".html", ".htm", ".txt"}
EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", "build", "dist"}
DETACHED_KO = re.compile(r"([가-힣]{2,})\s+(은|는|이|가|을|를|에|의|와|과|로|으로|도|만)(?=\s|[,.!?]|$)")
INLINE_CODE = re.compile(r"`[^`]*`")
HTML_TAG = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z'-]*\b")
COMMON_MISSPELLINGS = {
    "teh": "the", "recieve": "receive", "seperate": "separate",
    "occured": "occurred", "dependancy": "dependency",
    "compatability": "compatibility", "sucess": "success",
    "mutiple": "multiple", "enviroment": "environment",
    "relevent": "relevant", "adress": "address",
}


def tracked_text_files() -> list[Path]:
    try:
        raw = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout
        rels = [Path(x) for x in raw.decode("utf-8", errors="replace").split("\0") if x]
    except Exception:
        rels = [p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file()]
    return sorted(
        ROOT / rel for rel in rels
        if rel.suffix.lower() in TEXT_SUFFIXES and not any(x in EXCLUDED_PARTS for x in rel.parts)
    )


def split_table_row(line: str) -> list[str]:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return []
    return [x.strip() for x in re.split(r"(?<!\\)\|", s[1:-1])]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells)


def prose(line: str) -> str:
    line = INLINE_CODE.sub("", line)
    line = HTML_TAG.sub("", line)
    line = re.sub(r"!?\[[^\]]*\]\([^)]*\)", "", line)
    return line


def long_unbroken_word(cell: str) -> str | None:
    cleaned = cell.replace("`", " ")
    parts = re.split(r"\s+", cleaned)
    for part in parts:
        word = part.strip("*[](){}<>,;!?\"'")
        if len(word) < 30:
            continue
        if word.startswith("http://") or word.startswith("https://"):
            continue
        if all(ch in "0123456789abcdefABCDEF" for ch in word) and len(word) in {40, 64}:
            continue
        if all(ch.isalnum() or ch in "_./:-" for ch in word):
            return word
    return None


def audit_markdown(lines: list[str]) -> list[str]:
    issues: list[str] = []
    in_fence = False
    table: list[tuple[int, list[str]]] = []

    def flush_table() -> None:
        nonlocal table
        if len(table) < 2:
            table = []
            return
        expected = len(table[0][1])
        if any(len(cells) != expected for _, cells in table[1:]):
            details = ",".join(f"L{ln}:{len(cells)}" for ln, cells in table)
            issues.append(f"MARKDOWN_TABLE_COLUMNS:{details}")
        if expected >= 3:
            for ln, cells in table:
                if is_separator(cells):
                    continue
                prose_lengths = [len(HTML_TAG.sub("", INLINE_CODE.sub("", cell)).strip()) for cell in cells]
                if max(prose_lengths, default=0) >= 55:
                    issues.append(f"MOBILE_PROSE_TABLE:L{ln}:cols={expected}:max_prose={max(prose_lengths)}")
                    break
        if expected >= 5:
            for ln, cells in table:
                if is_separator(cells):
                    continue
                for cell in cells:
                    word = long_unbroken_word(cell)
                    if word:
                        issues.append(f"MOBILE_TABLE_OVERFLOW:L{ln}:{word}")
        table = []

    blank_run = 0
    for no, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            flush_table()
            in_fence = not in_fence
            blank_run = 0
            continue
        if in_fence:
            continue

        if line.strip():
            blank_run = 0
        else:
            blank_run += 1
            if blank_run == 3:
                issues.append(f"EXCESS_BLANK_LINES:L{no}")

        if line.endswith(" "):
            spaces = len(line) - len(line.rstrip(" "))
            if spaces != 2:
                issues.append(f"TRAILING_SPACE:L{no}:{spaces}")
        if "\u00a0" in line:
            issues.append(f"NON_BREAKING_SPACE:L{no}")

        cells = split_table_row(line)
        if cells:
            table.append((no, cells))
        else:
            flush_table()

        text = prose(line)
        match = DETACHED_KO.search(text)
        if match:
            issues.append(f"DETACHED_KO_PARTICLE:L{no}:{match.group(1)} {match.group(2)}")
        for word in WORD_RE.findall(text):
            suggestion = COMMON_MISSPELLINGS.get(word.lower())
            if suggestion:
                issues.append(f"COMMON_MISSPELLING:L{no}:{word}->{suggestion}")

    flush_table()
    return issues


def audit_plain(lines: list[str]) -> list[str]:
    issues: list[str] = []
    blank_run = 0
    for no, line in enumerate(lines, 1):
        if line.strip():
            blank_run = 0
        else:
            blank_run += 1
            if blank_run == 3:
                issues.append(f"EXCESS_BLANK_LINES:L{no}")
        if line.endswith(" "):
            issues.append(f"TRAILING_SPACE:L{no}")
        if "\u00a0" in line:
            issues.append(f"NON_BREAKING_SPACE:L{no}")
    return issues


def audit(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return audit_markdown(lines) if path.suffix.lower() == ".md" else audit_plain(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--strict", action="store_true")
    ns = ap.parse_args()
    files = [Path(x).resolve() for x in ns.files] if ns.files else tracked_text_files()
    total = 0
    checked = 0
    for path in files:
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        checked += 1
        issues = audit(path)
        if issues:
            rel = path.relative_to(ROOT) if ROOT in path.parents else path
            print(f"{rel}:")
            for issue in issues:
                print(f"  - {issue}")
            total += len(issues)
    print(f"CONTENT_QA_FILES={checked}")
    print(f"CONTENT_QA_ISSUES={total}")
    print(f"CONTENT_QA={'PASS' if total == 0 else 'FAIL'}")
    return 1 if ns.strict and total else 0


if __name__ == "__main__":
    raise SystemExit(main())
