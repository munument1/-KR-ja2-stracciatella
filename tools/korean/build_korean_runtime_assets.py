#!/usr/bin/env python3
"""Build Korean runtime assets that need compatibility handling.

This wrapper keeps the generic STI generator intact but applies the Korean UI
font policy used by the localization: compact/small JA2 font slots are rendered
from Galmuri9, while larger slots continue to use the generator's normal
Galmuri11/Galmuri14 selection.
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_korean_sti_fonts as fonts  # noqa: E402


GALMURI9_FONT_FILES = {
    "BLOCKFONT2.STI",
    "CLOCKFONT.STI",
    "COMPFONT.STI",
    "FONT10ARIAL.STI",
    "FONT10ARIALBOLD.STI",
    "FONT10ROMAN.STI",
    "SMALLCOMPFONT.STI",
    "SMALLFONT1.STI",
    "TINYFONT1.STI",
}

_original_select_ttf_for_font = fonts.select_ttf_for_font


def select_ttf_for_font(ttf_dir: Path, filename: str, target_height: int) -> Path:
    if filename.upper() in GALMURI9_FONT_FILES:
        candidate = ttf_dir / "Galmuri9Bitmap-Regular-2.40.4.ttf"
        if not candidate.is_file():
            raise FileNotFoundError(f"Required Galmuri9 font not found: {candidate}")
        return candidate
    return _original_select_ttf_for_font(ttf_dir, filename, target_height)


fonts.select_ttf_for_font = select_ttf_for_font


if __name__ == "__main__":
    raise SystemExit(fonts.main())
