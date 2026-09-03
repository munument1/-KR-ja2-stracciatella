#!/usr/bin/env python3
"""Build Korean runtime assets that need compatibility handling.

This wrapper keeps the generic STI generator intact but applies the Korean UI
font policy used by the localization:

- JA2 font slots with a cell height of 8px or less use Galmuri7.
- Compact tactical/UI slots above 8px use Galmuri9.
- Larger slots continue to use the generator's normal Galmuri11/Galmuri14
  selection.
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_korean_sti_fonts as fonts  # noqa: E402


GALMURI9_FONT_FILES = {
    "CLOCKFONT.STI",
    "FONT10ARIAL.STI",
    "FONT10ARIALBOLD.STI",
    "FONT12ARIAL.STI",
    "SMALLFONT1.STI",
    "TINYFONT1.STI",
}

_original_select_ttf_for_font = fonts.select_ttf_for_font


def select_ttf_for_font(ttf_dir: Path, filename: str, target_height: int) -> Path:
    if target_height <= 8:
        candidate = ttf_dir / "Galmuri7Bitmap-Regular-2.40.4.ttf"
        if not candidate.is_file():
            raise FileNotFoundError(f"Required Galmuri7 font not found: {candidate}")
        return candidate

    if filename.upper() in GALMURI9_FONT_FILES:
        candidate = ttf_dir / "Galmuri9Bitmap-Regular-2.40.4.ttf"
        if not candidate.is_file():
            raise FileNotFoundError(f"Required Galmuri9 font not found: {candidate}")
        return candidate

    return _original_select_ttf_for_font(ttf_dir, filename, target_height)


fonts.select_ttf_for_font = select_ttf_for_font


if __name__ == "__main__":
    raise SystemExit(fonts.main())
