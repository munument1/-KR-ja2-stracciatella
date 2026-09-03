#!/usr/bin/env python3
"""Add safe fallback glyph aliases for Korean punctuation missing from JA2 fonts.

The Korean STI set preserves the first 214 glyphs from the Simplified Chinese
font set, then appends Hangul. Some punctuation used by localized strings is not
present in that preserved base set. Until dedicated glyphs are generated, map
those Unicode characters to readable ASCII glyphs that are guaranteed to exist.

This script updates both the generated Korean translation table and the font
generator so a later regeneration will preserve the aliases.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


TABLE_PATH = Path("assets/externalized/translation_tables/translation-table-kor.json")
GENERATOR_PATH = Path("tools/korean/generate_korean_sti_fonts.py")

# Characters observed as sgp/Font.cc "Invalid character" errors in the Korean
# runtime log. Values are readable ASCII glyphs present in the common base set.
FALLBACK_ALIASES = {
    "~": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "『": '"',
    "』": '"',
}

GENERATOR_CONSTANT = '''\n# Unicode punctuation used by Korean strings but absent from the preserved\n# 0..213 base glyph set. Alias these to readable ASCII glyphs so the runtime\n# never falls back to '?'. Dedicated glyphs can replace these aliases later.\nKOREAN_FALLBACK_ALIASES = {\n    "~": "-",\n    "‘": "'",\n    "’": "'",\n    "“": '\"',\n    "”": '\"',\n    "『": '\"',\n    "』": '\"',\n}\n'''

GENERATOR_INSERT_AFTER = "RUN_LIMIT = 0x7F\n"
GENERATOR_TABLE_NEEDLE = '''    for offset, ch in enumerate(chars):\n        table[ch] = BASE_GLYPH_COUNT + offset\n\n    output_path.parent.mkdir(parents=True, exist_ok=True)\n'''
GENERATOR_TABLE_REPLACEMENT = '''    for offset, ch in enumerate(chars):\n        table[ch] = BASE_GLYPH_COUNT + offset\n\n    for ch, fallback in KOREAN_FALLBACK_ALIASES.items():\n        table[ch] = table[fallback]\n\n    output_path.parent.mkdir(parents=True, exist_ok=True)\n'''


def expected_alias_indices(table: dict[str, int]) -> dict[str, int]:
    expected: dict[str, int] = {}
    for ch, fallback in FALLBACK_ALIASES.items():
        if fallback not in table:
            raise ValueError(f"fallback glyph {fallback!r} is missing from Korean translation table")
        expected[ch] = int(table[fallback])
    return expected


def patch_translation_table(check_only: bool) -> bool:
    table = json.loads(TABLE_PATH.read_text(encoding="utf-8"))
    expected = expected_alias_indices(table)
    wrong = {ch: (table.get(ch), idx) for ch, idx in expected.items() if table.get(ch) != idx}
    if not wrong:
        return False
    if check_only:
        for ch, (actual, wanted) in wrong.items():
            print(f"missing/wrong alias U+{ord(ch):04X} {ch!r}: {actual!r} != {wanted}", file=sys.stderr)
        raise SystemExit(1)
    for ch, idx in expected.items():
        table[ch] = idx
    TABLE_PATH.write_text(json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return True


def patch_generator(check_only: bool) -> bool:
    text = GENERATOR_PATH.read_text(encoding="utf-8")
    changed = False

    if "KOREAN_FALLBACK_ALIASES = {" not in text:
        if check_only:
            print("font generator is missing KOREAN_FALLBACK_ALIASES", file=sys.stderr)
            raise SystemExit(1)
        if GENERATOR_INSERT_AFTER not in text:
            raise ValueError("could not find RUN_LIMIT insertion point in font generator")
        text = text.replace(
            GENERATOR_INSERT_AFTER,
            GENERATOR_INSERT_AFTER + GENERATOR_CONSTANT,
            1,
        )
        changed = True

    if "for ch, fallback in KOREAN_FALLBACK_ALIASES.items():" not in text:
        if check_only:
            print("font generator does not write Korean fallback aliases", file=sys.stderr)
            raise SystemExit(1)
        if GENERATOR_TABLE_NEEDLE not in text:
            raise ValueError("could not find translation-table write block in font generator")
        text = text.replace(GENERATOR_TABLE_NEEDLE, GENERATOR_TABLE_REPLACEMENT, 1)
        changed = True

    if changed:
        GENERATOR_PATH.write_text(text, encoding="utf-8", newline="\n")
    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify aliases and generator support without modifying files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generator_changed = patch_generator(args.check)
    table_changed = patch_translation_table(args.check)

    if args.check:
        print("Korean font fallback aliases: OK")
    else:
        print(f"font generator changed: {generator_changed}")
        print(f"translation table changed: {table_changed}")
        patch_generator(True)
        patch_translation_table(True)
        print("Korean font fallback aliases applied and verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
