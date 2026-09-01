#!/usr/bin/env python3
"""Safely import legacy Korean JA2 EDT assets into the Stracciatella Korean mod.

The old Korean patch targets JA2 1.13, while Stracciatella targets vanilla JA2.
Some EDT filenames exist in both projects but contain a different number of fixed-size
records.  This tool therefore uses the bundled Simplified Chinese localization as a
vanilla/Stracciatella structural reference and only copies files whose byte size is an
exact match.

Initial supported category: MercEdt.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import sys


EDT_RECORD_SIZE = 480
SUPPORTED_CATEGORIES = ("MercEdt",)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def edt_files(directory: Path) -> dict[str, Path]:
    if not directory.is_dir():
        raise FileNotFoundError(directory)
    return {
        path.name.upper(): path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.upper() == ".EDT"
    }


def sort_key(name: str) -> tuple[int, int | str]:
    stem = Path(name).stem
    try:
        return (0, int(stem))
    except ValueError:
        return (1, stem)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--legacy-root",
        type=Path,
        required=True,
        help="checkout root of munument1/Jagged-Alliance2-korean",
    )
    parser.add_argument(
        "--category",
        choices=SUPPORTED_CATEGORIES,
        default="MercEdt",
        help="legacy EDT category to import (default: MercEdt)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="JA2-Stracciatella checkout root (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would be copied without writing files",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace already-present destination files after validation",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return a non-zero exit code when structural mismatches are found",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    legacy_root = args.legacy_root.resolve()
    category = args.category

    source_dir = legacy_root / "Patch" / "Data" / category
    reference_dir = (
        repo_root
        / "assets"
        / "mods"
        / "simplified-chinese-localization"
        / "data"
        / category
    )
    destination_dir = (
        repo_root
        / "assets"
        / "mods"
        / "korean-localization"
        / "data"
        / category
    )

    try:
        source = edt_files(source_dir)
        reference = edt_files(reference_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: directory not found: {exc}", file=sys.stderr)
        return 2

    source_names = set(source)
    reference_names = set(reference)
    common_names = sorted(source_names & reference_names, key=sort_key)
    source_only = sorted(source_names - reference_names, key=sort_key)
    reference_only = sorted(reference_names - source_names, key=sort_key)

    destination_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    verified_existing = 0
    mismatched = 0
    invalid = 0

    print(f"Legacy source : {source_dir}")
    print(f"Vanilla ref   : {reference_dir}")
    print(f"Destination   : {destination_dir}")
    print()

    for name in common_names:
        src = source[name]
        ref = reference[name]
        dst = destination_dir / ref.name
        src_size = src.stat().st_size
        ref_size = ref.stat().st_size

        if src_size % EDT_RECORD_SIZE != 0:
            print(f"INVALID  {name}: {src_size} bytes is not a multiple of {EDT_RECORD_SIZE}")
            invalid += 1
            continue

        if src_size != ref_size:
            print(
                f"MISMATCH {name}: legacy={src_size} bytes ({src_size // EDT_RECORD_SIZE} records), "
                f"vanilla={ref_size} bytes ({ref_size // EDT_RECORD_SIZE} records)"
            )
            mismatched += 1
            continue

        src_hash = sha256(src)
        if dst.exists() and not args.overwrite:
            dst_hash = sha256(dst)
            if dst_hash == src_hash:
                print(f"OK       {name}: already imported, {src_size // EDT_RECORD_SIZE} records")
                verified_existing += 1
            else:
                print(f"SKIP     {name}: destination exists with different content (use --overwrite)")
            continue

        if args.dry_run:
            print(f"SAFE     {name}: {src_size // EDT_RECORD_SIZE} records")
            continue

        shutil.copyfile(src, dst)
        dst_hash = sha256(dst)
        if dst_hash != src_hash:
            print(f"ERROR    {name}: SHA-256 mismatch after copy", file=sys.stderr)
            return 3

        print(f"COPIED   {name}: {src_size // EDT_RECORD_SIZE} records, sha256={src_hash[:12]}")
        copied += 1

    if source_only:
        print("\nEXCLUDED legacy-only files (not present in vanilla reference):")
        for name in source_only:
            print(f"  {name} ({source[name].stat().st_size} bytes)")

    if reference_only:
        print("\nFALLBACK vanilla-only files (no Korean legacy counterpart):")
        for name in reference_only:
            print(f"  {name} ({reference[name].stat().st_size} bytes)")

    print("\nSummary")
    print(f"  common files       : {len(common_names)}")
    print(f"  copied             : {copied}")
    print(f"  already identical  : {verified_existing}")
    print(f"  size mismatches    : {mismatched}")
    print(f"  invalid record size: {invalid}")
    print(f"  legacy-only        : {len(source_only)}")
    print(f"  vanilla-only       : {len(reference_only)}")

    if args.strict and (mismatched or invalid):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
