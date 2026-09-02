#!/usr/bin/env python3
"""Audit Korean JA2 Stracciatella runtime localization assets.

This audit complements the JSON-string and EDT-layout validators.  It checks
assets that the engine still opens directly at runtime and keeps a visible list
of reviewed legacy exclusions and known visual-localization gaps.

The legacy JA2 1.13 Korean patch contains many resources that Stracciatella does
not consume, so legacy presence alone is never treated as proof that a file
belongs in the vanilla-compatible Korean mod.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True)
class RequiredAsset:
    path: str
    size: int | None = None
    magic: bytes | None = None
    reason: str = ""


# BinaryData files that are still consumed through EDTFile/openEDT() or direct
# loadEncryptedString() calls.  Sizes match the bundled Simplified Chinese
# vanilla/Stracciatella-layout reference used by validate_edt_layout.py.
BINARY_SIZES = {
    "AIMHIST.EDT": 18_400,
    "AIMPOL.EDT": 36_800,
    "ALUMNAME.EDT": 8_160,
    "ALUMNI.EDT": 65_280,
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
    "QUESTS.EDT": 7_360,
    "RIS.EDT": 54_400,
}

REQUIRED_FONT_FILES = {
    "BLOCKFONT2.sti",
    "BLOCKFONTNARROW.sti",
    "CLOCKFONT.sti",
    "COMPFONT.sti",
    "FONT10ARIAL.sti",
    "FONT10ARIALBOLD.sti",
    "FONT10ROMAN.sti",
    "FONT12ARIAL.sti",
    "FONT12ARIALFIXEDWIDTH.sti",
    "FONT12POINT1.sti",
    "FONT12ROMAN.sti",
    "FONT14ARIAL.sti",
    "FONT14HUMANIST.sti",
    "FONT14SANSERIF.sti",
    "FONT14SANSSERIF.sti",
    "FONT16ARIAL.sti",
    "HUGEFONT.sti",
    "LARGEFONT1.sti",
    "MERCFONT.sti",
    "SMALLCOMPFONT.sti",
    "SMALLFONT1.sti",
    "TINYFONT1.sti",
    "blockfont.sti",
}

REQUIRED = tuple(
    RequiredAsset(
        f"BinaryData/{name}",
        size=size,
        reason="Runtime EDT resource; exact vanilla-layout size is required.",
    )
    for name, size in BINARY_SIZES.items()
) + (
    RequiredAsset(
        "Loadscreens/ja2logo.sti",
        size=22_505,
        magic=b"STCI",
        reason="MainMenuScreen loads Loadscreens/ja2logo.sti directly.",
    ),
)

# Missing files here do not fail CI yet because there is no verified Korean
# source asset to import.  They are nevertheless real runtime localization
# gaps and must remain visible until deliberately localized or code-rendered.
KNOWN_GAPS = (
    (
        "Loadscreens/titletext.sti",
        "MainMenuScreen uses MLG_TITLETEXT for the five main-menu button images. "
        "The Simplified Chinese localization supplies TITLETEXT.STI, while the "
        "legacy Korean patch has no equivalent; Korean therefore falls back to "
        "the English baked-text button graphic today.",
    ),
)

# Reviewed legacy resources that should NOT be copied merely because they exist
# in Jagged-Alliance2-korean.  Keep this list visible so future audits do not
# repeatedly mistake externalized/1.13-only resources for localization gaps.
REVIEWED_EXCLUSIONS = (
    ("BinaryData/AIMBIOS.EDT", "AIM biography text is externalized in Stracciatella models."),
    ("BinaryData/MERCBIOS.EDT", "M.E.R.C. biographies are externalized in MERCListingModel."),
    ("BinaryData/BRAYDESC.EDT", "Bobby Ray item names/descriptions are provided by ItemModel."),
    ("BinaryData/ITEMDESC.EDT", "Item descriptions are externalized in ItemModel."),
    ("BinaryData/FLWRDESC.EDT", "Obsolete duplicate filename; Stracciatella maps florist descriptions to flowerdesc.edt."),
    ("TableData/DifficultySettings.xml", "JA2 1.13-only gameplay data; no Stracciatella runtime reference."),
    ("TableData/EnemyTaunts", "JA2 1.13-only feature data; no Stracciatella runtime reference."),
    ("Interface/RoleIcons.sti", "JA2 1.13 UI-extension asset; no current Stracciatella filename reference."),
    ("Interface/plusminusbuttons.sti", "JA2 1.13 UI-extension asset; no current Stracciatella filename reference."),
)


def validate_required(root: Path, asset: RequiredAsset) -> list[str]:
    errors: list[str] = []
    path = root / asset.path
    if not path.is_file():
        return [f"MISSING {asset.path}: {asset.reason}"]

    if asset.size is not None and path.stat().st_size != asset.size:
        errors.append(
            f"SIZE {asset.path}: expected {asset.size}, got {path.stat().st_size}"
        )
    if asset.magic is not None:
        with path.open("rb") as f:
            got = f.read(len(asset.magic))
        if got != asset.magic:
            errors.append(
                f"MAGIC {asset.path}: expected {asset.magic!r}, got {got!r}"
            )
    return errors


def validate_fonts(root: Path) -> list[str]:
    errors: list[str] = []
    font_dir = root / "Fonts"
    if not font_dir.is_dir():
        return ["MISSING Fonts: Korean STI font directory is absent"]

    actual = {p.name for p in font_dir.iterdir() if p.is_file()}
    for name in sorted(REQUIRED_FONT_FILES - actual):
        errors.append(f"MISSING Fonts/{name}: font is used by the JA2 font table")

    for name in sorted(REQUIRED_FONT_FILES & actual):
        path = font_dir / name
        with path.open("rb") as f:
            magic = f.read(4)
        if magic != b"STCI":
            errors.append(f"MAGIC Fonts/{name}: expected b'STCI', got {magic!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mod-dir",
        type=Path,
        default=Path("assets/mods/korean-localization/data"),
    )
    args = parser.parse_args()

    errors: list[str] = []
    print("Korean runtime asset audit")
    print("==========================")
    for asset in REQUIRED:
        asset_errors = validate_required(args.mod_dir, asset)
        errors.extend(asset_errors)
        state = "FAIL" if asset_errors else "OK"
        print(f"{state:4} {asset.path} - {asset.reason}")

    font_errors = validate_fonts(args.mod_dir)
    errors.extend(font_errors)
    print(
        f"{'FAIL' if font_errors else 'OK':4} Fonts - "
        f"{len(REQUIRED_FONT_FILES)} required STI font filenames and STCI headers"
    )

    print()
    print("Known localization gaps")
    print("=======================")
    for path, reason in KNOWN_GAPS:
        state = "OPEN" if not (args.mod_dir / path).is_file() else "DONE"
        print(f"{state:4} {path} - {reason}")

    print()
    print("Reviewed legacy exclusions")
    print("==========================")
    for path, reason in REVIEWED_EXCLUSIONS:
        print(f"SKIP {path} - {reason}")

    if errors:
        print(file=sys.stderr)
        print("Runtime asset audit failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print()
    print(
        f"Required runtime assets: {len(REQUIRED)} files + "
        f"{len(REQUIRED_FONT_FILES)} fonts present and structurally valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
