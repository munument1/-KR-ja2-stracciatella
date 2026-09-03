#!/usr/bin/env python3
"""Audit Korean JA2 Stracciatella runtime localization assets."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import struct
import sys

@dataclass(frozen=True)
class RequiredAsset:
    path: str
    size: int | None = None
    magic: bytes | None = None
    reason: str = ""

BINARY_SIZES = {
    "AIMBIOS.EDT": 44_800,
    "AIMHIST.EDT": 18_400,
    "AIMPOL.EDT": 36_800,
    "ALUMNAME.EDT": 8_160,
    "ALUMNI.EDT": 65_280,
    "BRAYDESC.EDT": 280_800,
    "CREDITS.EDT": 39_680,
    "EMAIL.EDT": 143_360,
    "FILES.EDT": 57_600,
    "FLOWERCARD.EDT": 7_200,
    "FLOWERDESC.EDT": 9_600,
    "HELP.EDT": 157_440,
    "IMPASS.EDT": 146_560,
    "IMPTEXT.EDT": 191_200,
    "INSURANCEMULTI.EDT": 28_800,
    "INSURANCESINGLE.EDT": 4_800,
    "ITEMDESC.EDT": 280_800,
    "MERCBIOS.EDT": 12_320,
    "QUESTS.EDT": 7_360,
    "RIS.EDT": 54_400,
}
REQUIRED_FONT_FILES = {
    "BLOCKFONT2.sti", "BLOCKFONTNARROW.sti", "CLOCKFONT.sti", "COMPFONT.sti",
    "FONT10ARIAL.sti", "FONT10ARIALBOLD.sti", "FONT10ROMAN.sti", "FONT12ARIAL.sti",
    "FONT12ARIALFIXEDWIDTH.sti", "FONT12POINT1.sti", "FONT12ROMAN.sti", "FONT14ARIAL.sti",
    "FONT14HUMANIST.sti", "FONT14SANSERIF.sti", "FONT14SANSSERIF.sti", "FONT16ARIAL.sti",
    "HUGEFONT.sti", "LARGEFONT1.sti", "MERCFONT.sti", "SMALLCOMPFONT.sti",
    "SMALLFONT1.sti", "TINYFONT1.sti", "blockfont.sti",
}
REQUIRED = tuple(RequiredAsset(f"BinaryData/{name}", size=size, reason="Runtime EDT resource; exact vanilla-layout size is required.") for name, size in BINARY_SIZES.items()) + (
    RequiredAsset("Loadscreens/ja2logo.sti", size=22_505, magic=b"STCI", reason="MainMenuScreen loads the Korean logo directly."),
    RequiredAsset("Loadscreens/titletext.sti", magic=b"STCI", reason="MLG_TITLETEXT supplies the five Korean main-menu labels."),
)
REVIEWED_EXCLUSIONS = (
    ("BinaryData/FLWRDESC.EDT", "No current Stracciatella runtime reference; FLOWERDESC.EDT is the active florist description resource."),
    ("TableData/DifficultySettings.xml", "JA2 1.13-only gameplay data; no Stracciatella runtime reference."),
    ("TableData/EnemyTaunts", "JA2 1.13-only feature data; no Stracciatella runtime reference."),
    ("Interface/RoleIcons.sti", "JA2 1.13 UI-extension asset; no current Stracciatella filename reference."),
    ("Interface/plusminusbuttons.sti", "JA2 1.13 UI-extension asset; no current Stracciatella filename reference."),
)

def validate_required(root: Path, asset: RequiredAsset) -> list[str]:
    path = root / asset.path
    if not path.is_file(): return [f"MISSING {asset.path}: {asset.reason}"]
    errors: list[str] = []
    if asset.size is not None and path.stat().st_size != asset.size: errors.append(f"SIZE {asset.path}: expected {asset.size}, got {path.stat().st_size}")
    if asset.magic is not None and path.read_bytes()[:len(asset.magic)] != asset.magic: errors.append(f"MAGIC {asset.path}: expected {asset.magic!r}")
    return errors

def validate_titletext(root: Path) -> list[str]:
    path = root / "Loadscreens/titletext.sti"
    if not path.is_file(): return []
    raw = path.read_bytes()
    if len(raw) < 64: return ["STRUCT Loadscreens/titletext.sti: shorter than STCI header"]
    sub_count = struct.unpack_from("<H", raw, 28)[0]
    flags = struct.unpack_from("<I", raw, 16)[0]
    errors = []
    if sub_count != 20: errors.append(f"STRUCT Loadscreens/titletext.sti: expected 20 frames, got {sub_count}")
    if not (flags & 0x0008) or not (flags & 0x0020): errors.append("STRUCT Loadscreens/titletext.sti: expected indexed ETRLE-compressed STI")
    return errors

def validate_fonts(root: Path) -> list[str]:
    font_dir = root / "Fonts"
    if not font_dir.is_dir(): return ["MISSING Fonts: Korean STI font directory is absent"]
    actual = {p.name for p in font_dir.iterdir() if p.is_file()}
    errors = [f"MISSING Fonts/{name}: font is used by the JA2 font table" for name in sorted(REQUIRED_FONT_FILES - actual)]
    for name in sorted(REQUIRED_FONT_FILES & actual):
        if (font_dir / name).read_bytes()[:4] != b"STCI": errors.append(f"MAGIC Fonts/{name}: expected b'STCI'")
    return errors

def validate_translation_table(repo: Path) -> list[str]:
    path = repo / "assets/externalized/translation_tables/translation-table-kor.json"
    if not path.is_file(): return ["MISSING translation-table-kor.json"]
    table = json.loads(path.read_text(encoding="utf-8"))
    if "·" not in table: return ["FONT U+00B7 middle dot is missing from Korean translation table"]
    return []

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mod-dir", type=Path, default=Path("assets/mods/korean-localization/data"))
    args = parser.parse_args()
    errors: list[str] = []
    print("Korean runtime asset audit\n==========================")
    for asset in REQUIRED:
        found = validate_required(args.mod_dir, asset); errors.extend(found)
        print(f"{'FAIL' if found else 'OK':4} {asset.path} - {asset.reason}")
    title = validate_titletext(args.mod_dir); errors.extend(title)
    print(f"{'FAIL' if title else 'OK':4} Loadscreens/titletext.sti - 20 indexed ETRLE frames")
    fonts = validate_fonts(args.mod_dir); errors.extend(fonts)
    print(f"{'FAIL' if fonts else 'OK':4} Fonts - {len(REQUIRED_FONT_FILES)} required STI fonts")
    repo = Path(__file__).resolve().parents[2]
    table_errors = validate_translation_table(repo); errors.extend(table_errors)
    print(f"{'FAIL' if table_errors else 'OK':4} translation-table-kor.json - U+00B7 mapped")
    print("\nReviewed legacy exclusions\n==========================")
    for path, reason in REVIEWED_EXCLUSIONS: print(f"SKIP {path} - {reason}")
    if errors:
        print("\nRuntime asset audit failed:", file=sys.stderr)
        for error in errors: print(f"  {error}", file=sys.stderr)
        return 1
    print(f"\nRequired runtime assets: {len(REQUIRED)} files + {len(REQUIRED_FONT_FILES)} fonts present and structurally valid")
    return 0


if __name__ == "__main__": raise SystemExit(main())
