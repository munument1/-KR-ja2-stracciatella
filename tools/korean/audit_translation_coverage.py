#!/usr/bin/env python3
"""Audit Korean translation coverage against Stracciatella English resources.

This script is intentionally conservative: it reports missing Korean counterparts,
entries that are still identical to English, and structural/placeholder mismatches.
It does not modify translation files.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z]|\{[^{}]*\}")
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


def walk(value: Any, prefix: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            p = f"{prefix}.{key}" if prefix else key
            yield from walk(child, p)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            p = f"{prefix}[{i}]"
            yield from walk(child, p)
    else:
        yield prefix, value


def placeholders(value: str) -> list[str]:
    return PLACEHOLDER_RE.findall(value)


def family_name(path: Path) -> str:
    name = path.name
    assert name.endswith("-eng.json")
    return name[:-len("-eng.json")]


def compare_family(eng_path: Path, kor_path: Path) -> dict[str, Any]:
    eng = load_json(eng_path)
    kor = load_json(kor_path)
    eng_flat = dict(walk(eng))
    kor_flat = dict(walk(kor))

    missing_paths = sorted(set(eng_flat) - set(kor_flat))
    extra_paths = sorted(set(kor_flat) - set(eng_flat))
    type_mismatches: list[str] = []
    placeholder_mismatches: list[str] = []
    untranslated: list[str] = []
    translated = 0
    translatable = 0

    for path in sorted(set(eng_flat) & set(kor_flat)):
        e = eng_flat[path]
        k = kor_flat[path]
        if type(e) is not type(k):
            type_mismatches.append(path)
            continue
        if not isinstance(e, str):
            continue
        if not e or e.startswith("__"):
            continue
        translatable += 1
        if placeholders(e) != placeholders(k):
            placeholder_mismatches.append(path)
        if e == k:
            untranslated.append(path)
        else:
            translated += 1

    return {
        "family": family_name(eng_path),
        "english": str(eng_path),
        "korean": str(kor_path),
        "translatable": translatable,
        "translated": translated,
        "untranslated": len(untranslated),
        "untranslated_paths": untranslated,
        "missing_paths": missing_paths,
        "extra_paths": extra_paths,
        "type_mismatches": type_mismatches,
        "placeholder_mismatches": placeholder_mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strings-dir",
        type=Path,
        default=Path("assets/externalized/strings"),
        help="directory containing *-eng.json and *-kor.json",
    )
    parser.add_argument(
        "--mod-dir",
        type=Path,
        default=Path("assets/mods/korean-localization/data"),
        help="Korean localization mod data directory",
    )
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    families: list[dict[str, Any]] = []
    missing_korean_files: list[str] = []

    for eng_path in sorted(args.strings_dir.glob("*-eng.json")):
        family = family_name(eng_path)
        kor_path = eng_path.with_name(f"{family}-kor.json")
        if not kor_path.exists():
            missing_korean_files.append(str(kor_path))
            continue
        families.append(compare_family(eng_path, kor_path))

    merc_dir = args.mod_dir / "MercEdt"
    npc_dir = args.mod_dir / "NPCData"
    binary_dir = args.mod_dir / "BinaryData"

    runtime = {
        "MercEdt_count": len(list(merc_dir.glob("*.EDT"))) if merc_dir.exists() else 0,
        "NPCData_count": len(list(npc_dir.glob("*.EDT"))) if npc_dir.exists() else 0,
        "BinaryData_EDT_count": len(list(binary_dir.glob("*.EDT"))) if binary_dir.exists() else 0,
    }

    totals = {
        "translatable": sum(x["translatable"] for x in families),
        "translated": sum(x["translated"] for x in families),
        "untranslated": sum(x["untranslated"] for x in families),
        "placeholder_mismatches": sum(len(x["placeholder_mismatches"]) for x in families),
        "structural_mismatches": sum(
            len(x["missing_paths"]) + len(x["extra_paths"]) + len(x["type_mismatches"])
            for x in families
        ),
    }

    report = {
        "missing_korean_files": missing_korean_files,
        "totals": totals,
        "runtime_data": runtime,
        "families": families,
    }

    print("Korean translation coverage audit")
    print("=================================")
    print(f"Missing Korean string files: {len(missing_korean_files)}")
    for path in missing_korean_files:
        print(f"  MISSING {path}")
    print(
        f"Externalized strings: {totals['translated']}/{totals['translatable']} changed from English; "
        f"{totals['untranslated']} still identical to English"
    )
    print(f"Placeholder mismatches: {totals['placeholder_mismatches']}")
    print(f"Structural mismatches: {totals['structural_mismatches']}")
    print(
        "Runtime EDT files in Korean mod: "
        f"MercEdt={runtime['MercEdt_count']}, "
        f"NPCData={runtime['NPCData_count']}, "
        f"BinaryData={runtime['BinaryData_EDT_count']}"
    )
    print()

    for item in families:
        print(
            f"{item['family']}: {item['translated']}/{item['translatable']} translated, "
            f"{item['untranslated']} English-identical, "
            f"placeholder mismatches={len(item['placeholder_mismatches'])}, "
            f"structural mismatches={len(item['missing_paths']) + len(item['extra_paths']) + len(item['type_mismatches'])}"
        )

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if missing_korean_files or totals["placeholder_mismatches"] or totals["structural_mismatches"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
