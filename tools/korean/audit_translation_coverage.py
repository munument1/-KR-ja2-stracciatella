#!/usr/bin/env python3
"""Audit Korean translation coverage against Stracciatella English resources.

The audit distinguishes three states for non-empty strings:
- translated: Korean intentionally differs from English;
- intentional-identical: proper names, coordinates, units, technical IDs and
  control tokens that should remain exactly as in the source;
- untranslated: English-identical text that still needs localization review.

Structural and placeholder mismatches remain hard failures.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z]|\{[^{}]*\}")
TRAILING_COMMA_RE = re.compile(r",(?=\s*[}\]])")

TECHNICAL_AMMO_LABELS = {
    "0",
    "9mm",
    "CAWS",
    "5.45mm",
    "5.56mm",
    "7.62mm NATO",
    "7.62mm N.",
    "7.62mm WP",
    "4.7mm",
    "5.7mm",
}

TOOLTIP_CONTROL_PATHS = {
    "demarcationStrings[0]",  # indentation
    "demarcationStrings[1]",  # visual divider
    "statusStrings[0]",       # |?|?|? control-highlight token
    "statusStrings[1]",       # ??? unknown marker
}

TRANSLATION_INTENTIONAL_PREFIXES: tuple[tuple[str, str], ...] = (
    ("gzCreditNames[", "credit/person name"),
    ("gzMoneyAmounts[", "literal currency amount"),
    ("pBookMarkStrings[", "site/organization brand"),
    ("pMapDepthIndex[", "map depth coordinate"),
    ("pMapHortIndex[", "map coordinate"),
    ("pMapVertIndex[", "map coordinate"),
    ("pSenderNameList[", "sender/person/organization name"),
)

TRANSLATION_INTENTIONAL_EXACT: dict[str, str] = {
    "MercHomePageText[4]": "in-universe software/version name",
    "gWeaponStatsDesc[6]": "literal equals symbol",
    "pLaptopIcons[7]": "in-universe browser product name",
    "pMessageStrings[12]": "technical unit rpm",
    "pMessageStrings[14]": "technical unit m",
    "pMessageStrings[16]": "technical unit kg",
    "pMessageStrings[17]": "technical unit lb",
    "pMessageStrings[19]": "currency code USD",
    "pMilitiaConfirmStrings[5]": "keyboard input hint Y/N",
    "pPOWStrings[1]": "unknown-value marker",
    "pWebTitle": "in-universe browser product name",
    "sFloristText[2]": "telephone number",
    "sFloristText[3]": "postal address",
    "sFloristText[4]": "URL",
}

WEB_BRANDS = {"A.I.M.", "Bobby Ray's", "I.M.P.", "M.E.R.C."}


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


def intentional_identical_reason(family: str, path: str, value: str) -> str | None:
    if family in {"ammo-calibre", "ammo-calibre-bobbyray"}:
        if value in TECHNICAL_AMMO_LABELS:
            return "technical ammunition/calibre identifier"
        return None

    if family == "tooltips":
        if path in TOOLTIP_CONTROL_PATHS:
            return "layout/control marker"
        return None

    if family != "translation":
        return None

    for prefix, reason in TRANSLATION_INTENTIONAL_PREFIXES:
        if path.startswith(prefix):
            return reason

    reason = TRANSLATION_INTENTIONAL_EXACT.get(path)
    if reason:
        return reason

    if path.startswith("pWebPagesTitles[") and value in WEB_BRANDS:
        return "site/organization brand"

    return None


def count_edt_files(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(1 for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".edt")


def compare_family(eng_path: Path, kor_path: Path) -> dict[str, Any]:
    eng = load_json(eng_path)
    kor = load_json(kor_path)
    eng_flat = dict(walk(eng))
    kor_flat = dict(walk(kor))
    family = family_name(eng_path)

    missing_paths = sorted(set(eng_flat) - set(kor_flat))
    extra_paths = sorted(set(kor_flat) - set(eng_flat))
    type_mismatches: list[str] = []
    placeholder_mismatches: list[str] = []
    untranslated: list[str] = []
    untranslated_entries: list[dict[str, str]] = []
    intentional_entries: list[dict[str, str]] = []
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
            reason = intentional_identical_reason(family, path, e)
            if reason:
                intentional_entries.append({"path": path, "value": e, "reason": reason})
            else:
                untranslated.append(path)
                untranslated_entries.append({"path": path, "value": e})
        else:
            translated += 1

    intentional_identical = len(intentional_entries)
    covered = translated + intentional_identical

    return {
        "family": family,
        "english": str(eng_path),
        "korean": str(kor_path),
        "translatable": translatable,
        "translated": translated,
        "intentional_identical": intentional_identical,
        "covered": covered,
        "untranslated": len(untranslated),
        "untranslated_paths": untranslated,
        "untranslated_entries": untranslated_entries,
        "intentional_identical_entries": intentional_entries,
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
    parser.add_argument(
        "--list-untranslated",
        action="append",
        default=[],
        metavar="FAMILY",
        help="print unresolved English-identical entries for a family (repeatable; use 'all' for every family)",
    )
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

    runtime = {
        "MercEdt_count": count_edt_files(args.mod_dir / "MercEdt"),
        "NPCData_count": count_edt_files(args.mod_dir / "NPCData"),
        "BinaryData_EDT_count": count_edt_files(args.mod_dir / "BinaryData"),
    }

    totals = {
        "translatable": sum(x["translatable"] for x in families),
        "translated": sum(x["translated"] for x in families),
        "intentional_identical": sum(x["intentional_identical"] for x in families),
        "covered": sum(x["covered"] for x in families),
        "untranslated": sum(x["untranslated"] for x in families),
        "placeholder_mismatches": sum(len(x["placeholder_mismatches"]) for x in families),
        "structural_mismatches": sum(
            len(x["missing_paths"]) + len(x["extra_paths"]) + len(x["type_mismatches"])
            for x in families
        ),
    }
    totals["changed_percent"] = round(
        100.0 * totals["translated"] / totals["translatable"], 2
    ) if totals["translatable"] else 100.0
    totals["effective_percent"] = round(
        100.0 * totals["covered"] / totals["translatable"], 2
    ) if totals["translatable"] else 100.0

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
        f"Changed from English: {totals['translated']}/{totals['translatable']} "
        f"({totals['changed_percent']:.2f}%)"
    )
    print(f"Intentional source-identical strings: {totals['intentional_identical']}")
    print(f"Unresolved untranslated strings: {totals['untranslated']}")
    print(
        f"Effective localization coverage: {totals['covered']}/{totals['translatable']} "
        f"({totals['effective_percent']:.2f}%)"
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
            f"{item['family']}: changed={item['translated']}, "
            f"intentional-identical={item['intentional_identical']}, "
            f"unresolved={item['untranslated']}, total={item['translatable']}, "
            f"placeholder mismatches={len(item['placeholder_mismatches'])}, "
            f"structural mismatches={len(item['missing_paths']) + len(item['extra_paths']) + len(item['type_mismatches'])}"
        )

    requested = set(args.list_untranslated)
    if requested:
        print()
        print("Unresolved English-identical entries")
        print("====================================")
        for item in families:
            if "all" not in requested and item["family"] not in requested:
                continue
            print(f"[{item['family']}] {item['untranslated']} entries")
            for entry in item["untranslated_entries"]:
                print(f"{entry['path']} = {json.dumps(entry['value'], ensure_ascii=False)}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if (
        missing_korean_files
        or totals["untranslated"]
        or totals["placeholder_mismatches"]
        or totals["structural_mismatches"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
