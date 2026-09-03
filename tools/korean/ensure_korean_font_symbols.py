#!/usr/bin/env python3
"""Ensure Korean localization punctuation always has a runtime font mapping."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

TABLE = Path("assets/externalized/translation_tables/translation-table-kor.json")
# U+00B7 currently has no dedicated glyph in the preserved JA2 font base. Map it
# to the guaranteed ASCII period glyph so Font.cc never receives an invalid char.
ALIASES = {"·": "."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(TABLE.read_text(encoding="utf-8"))
    changed = False
    for char, fallback in ALIASES.items():
        if fallback not in data:
            raise SystemExit(f"fallback glyph missing from Korean table: {fallback!r}")
        expected = int(data[fallback])
        if data.get(char) != expected:
            if args.check:
                print(
                    f"missing/wrong Korean font mapping U+{ord(char):04X}: "
                    f"{data.get(char)!r} != {expected}", file=sys.stderr
                )
                return 1
            data[char] = expected
            changed = True
    if changed:
        TABLE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Korean font symbol mappings: OK (changed={changed})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
