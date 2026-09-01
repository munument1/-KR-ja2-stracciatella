#!/usr/bin/env python3
"""Validate Korean externalized localization files against English sources.

Checks:
- JSON/Stracciatella commented-JSON syntax
- matching object keys
- matching scalar/container types
- matching list lengths
- matching printf-style placeholders (%s, %d, etc.; %% ignored)
- matching StringTheory brace placeholders ({}, {1}, {2.1f}, etc.)

This intentionally validates structure and formatting contracts, not translation text.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

PRINTF_RE = re.compile(
    r"%(?:\d+\$)?[-+#0 ']*\d*(?:\.\d+)?[hljztL]*[diuoxXfFeEgGaAcspn]"
)
BRACE_RE = re.compile(r"(?<!\{)\{([^{}]*)\}(?!\})")
TRAILING_COMMA_RE = re.compile(r",(?=\s*[}\]])")


def strip_json_comments(text: str) -> str:
    """Remove // and /* */ comments without touching quoted strings."""
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(text):
        ch = text[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == "/" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "/":
                i += 2
                while i < len(text) and text[i] not in "\r\n":
                    i += 1
                continue
            if nxt == "*":
                i += 2
                while i + 1 < len(text) and text[i:i + 2] != "*/":
                    i += 1
                i += 2
                continue

        out.append(ch)
        i += 1
    return "".join(out)


def load_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    text = strip_json_comments(text)
    text = TRAILING_COMMA_RE.sub("", text)
    return json.loads(text)


def printf_signature(text: str) -> Counter[str]:
    """Return printf conversion types while ignoring literal %%."""
    scrubbed = text.replace("%%", "")
    return Counter(match.group(0)[-1] for match in PRINTF_RE.finditer(scrubbed))


def brace_signature(text: str) -> Counter[str]:
    """Return StringTheory brace field specifications.

    The exact field contents are kept because formats such as {2.1f} and {}
    are semantically different in StringTheory.
    """
    return Counter(match.group(1) for match in BRACE_RE.finditer(text))


def format_signature(text: str) -> tuple[Counter[str], Counter[str]]:
    return printf_signature(text), brace_signature(text)


def walk_compare(eng: Any, kor: Any, path: str, errors: list[str]) -> None:
    if type(eng) is not type(kor):
        errors.append(
            f"{path}: type mismatch: eng={type(eng).__name__}, kor={type(kor).__name__}"
        )
        return

    if isinstance(eng, dict):
        eng_keys = set(eng)
        kor_keys = set(kor)
        for key in sorted(eng_keys - kor_keys):
            errors.append(f"{path}: missing Korean key {key!r}")
        for key in sorted(kor_keys - eng_keys):
            errors.append(f"{path}: extra Korean key {key!r}")
        for key in sorted(eng_keys & kor_keys):
            walk_compare(eng[key], kor[key], f"{path}.{key}", errors)
        return

    if isinstance(eng, list):
        if len(eng) != len(kor):
            errors.append(f"{path}: list length mismatch: eng={len(eng)}, kor={len(kor)}")
        for i, (eng_item, kor_item) in enumerate(zip(eng, kor)):
            walk_compare(eng_item, kor_item, f"{path}[{i}]", errors)
        return

    if isinstance(eng, str):
        eng_sig = format_signature(eng)
        kor_sig = format_signature(kor)
        if eng_sig != kor_sig:
            errors.append(
                f"{path}: format placeholder mismatch\n"
                f"  eng: {eng!r}\n"
                f"  kor: {kor!r}\n"
                f"  eng printf={dict(eng_sig[0])}, braces={dict(eng_sig[1])}\n"
                f"  kor printf={dict(kor_sig[0])}, braces={dict(kor_sig[1])}"
            )


def corresponding_english_file(kor_file: Path) -> Path:
    name = kor_file.name
    if not name.endswith("-kor.json"):
        raise ValueError(f"not a Korean localization JSON: {kor_file}")
    return kor_file.with_name(name[:-9] + "-eng.json")


def iter_pairs(strings_dir: Path, explicit: Iterable[Path] | None) -> list[tuple[Path, Path]]:
    if explicit:
        kor_files = list(explicit)
    else:
        kor_files = sorted(strings_dir.glob("*-kor.json"))

    pairs: list[tuple[Path, Path]] = []
    for kor in kor_files:
        eng = corresponding_english_file(kor)
        if not eng.is_file():
            raise FileNotFoundError(
                f"English reference is missing for {kor.name}: expected {eng.name}"
            )
        pairs.append((eng, kor))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Korean externalized strings against English reference files."
    )
    parser.add_argument(
        "--strings-dir",
        type=Path,
        default=Path("assets/externalized/strings"),
        help="externalized strings directory (default: assets/externalized/strings)",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="optional specific *-kor.json files; otherwise validate all",
    )
    args = parser.parse_args()

    try:
        pairs = iter_pairs(args.strings_dir, args.files or None)
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not pairs:
        print("ERROR: no Korean localization JSON files found", file=sys.stderr)
        return 2

    total_errors = 0
    for eng_path, kor_path in pairs:
        errors: list[str] = []
        try:
            eng = load_json(eng_path)
            kor = load_json(kor_path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FAIL {kor_path}: {exc}")
            total_errors += 1
            continue

        walk_compare(eng, kor, "$", errors)
        if errors:
            total_errors += len(errors)
            print(f"FAIL {kor_path} ({len(errors)} issue(s))")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {kor_path}")

    if total_errors:
        print(f"\nLocalization validation failed: {total_errors} issue(s).")
        return 1

    print(f"\nLocalization validation passed for {len(pairs)} Korean file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
