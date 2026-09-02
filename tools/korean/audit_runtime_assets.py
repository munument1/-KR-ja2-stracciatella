#!/usr/bin/env python3
"""Audit Korean runtime assets that are not covered by externalized JSON strings.

This intentionally uses a small, reviewed manifest.  The legacy JA2 1.13 Korean
patch contains many gameplay/UI extension resources that Stracciatella does not
consume.  Treating every legacy file as required would create false positives
and risks importing 1.13-only data into vanilla-compatible Stracciatella.
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


REQUIRED = (
    RequiredAsset(
        "BinaryData/EMAIL.EDT",
        size=143_360,
        reason="Email bodies are still loaded from BinaryData/EMAIL.EDT at runtime.",
    ),
    RequiredAsset(
        "Loadscreens/ja2logo.sti",
        size=22_505,
        magic=b"STCI",
        reason="MainMenuScreen loads Loadscreens/ja2logo.sti directly.",
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
    ("BinaryData/FLOWERDESC.EDT", "Legacy florist description EDT is not referenced by current Stracciatella source."),
    ("BinaryData/FLWRDESC.EDT", "Legacy florist description EDT is not referenced by current Stracciatella source."),
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
    print(f"Required runtime assets: {len(REQUIRED)}/{len(REQUIRED)} present and valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
