#!/usr/bin/env python3
"""Safely import legacy Korean JA2 EDT assets into the Stracciatella Korean mod.

The old Korean patch targets JA2 1.13, while Stracciatella targets vanilla JA2.
Some EDT filenames exist in both projects but contain a different number of fixed-size
records. This tool therefore uses the bundled Simplified Chinese localization as a
vanilla/Stracciatella structural reference.

By default only exact-size files are imported. With --trim-extra-records, a legacy file
that contains more complete records than the vanilla reference may be imported by
keeping only the reference-sized prefix. This is safe for MercEdt because vanilla quote
IDs 0..116 keep the same ordering in JA2 1.13; the extra 1.13 merc quote IDs are appended
after the vanilla range rather than inserted into it.

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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        "--trim-extra-records",
        action="store_true",
        help="allow a longer legacy MercEdt to be truncated to the vanilla reference record count",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return a non-zero exit code when unsafe structural mismatches are found",
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
    copied_trimmed = 0
    verified_existing = 0
    skipped_existing = 0
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
            print(f"INVALID  {name}: legacy {src_size} bytes is not a multiple of {EDT_RECORD_SIZE}")
            invalid += 1
            continue
        if ref_size % EDT_RECORD_SIZE != 0:
            print(f"INVALID  {name}: reference {ref_size} bytes is not a multiple of {EDT_RECORD_SIZE}")
            invalid += 1
            continue

        trim = False
        if src_size < ref_size:
            print(
                f"MISMATCH {name}: legacy={src_size} bytes ({src_size // EDT_RECORD_SIZE} records), "
                f"vanilla={ref_size} bytes ({ref_size // EDT_RECORD_SIZE} records); legacy source is too short"
            )
            mismatched += 1
            continue
        if src_size > ref_size:
            if not args.trim_extra_records:
                print(
                    f"MISMATCH {name}: legacy={src_size} bytes ({src_size // EDT_RECORD_SIZE} records), "
                    f"vanilla={ref_size} bytes ({ref_size // EDT_RECORD_SIZE} records)"
                )
                mismatched += 1
                continue
            trim = True

        src_data = src.read_bytes()
        candidate = src_data[:ref_size]
        candidate_hash = sha256_bytes(candidate)
        record_count = ref_size // EDT_RECORD_SIZE

        if dst.exists() and not args.overwrite:
            dst_hash = sha256(dst)
            if dst_hash == candidate_hash:
                mode = "trimmed prefix" if trim else "exact source"
                print(f"OK       {name}: already imported, {record_count} records ({mode})")
                verified_existing += 1
            else:
                print(f"SKIP     {name}: destination exists with different content (use --overwrite)")
                skipped_existing += 1
            continue

        mode = "TRIM" if trim else "SAFE"
        if args.dry_run:
            if trim:
                print(
                    f"{mode:<8} {name}: {src_size // EDT_RECORD_SIZE} -> {record_count} records"
                )
            else:
                print(f"{mode:<8} {name}: {record_count} records")
            continue

        if trim:
            dst.write_bytes(candidate)
        else:
            shutil.copyfile(src, dst)

        dst_hash = sha256(dst)
        if dst_hash != candidate_hash:
            print(f"ERROR    {name}: SHA-256 mismatch after import", file=sys.stderr)
            return 3

        if trim:
            print(
                f"COPIED   {name}: trimmed {src_size // EDT_RECORD_SIZE} -> {record_count} records, "
                f"sha256={candidate_hash[:12]}"
            )
            copied_trimmed += 1
        else:
            print(f"COPIED   {name}: {record_count} records, sha256={candidate_hash[:12]}")
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
    print(f"  copied with trim   : {copied_trimmed}")
    print(f"  already identical  : {verified_existing}")
    print(f"  existing preserved : {skipped_existing}")
    print(f"  unsafe mismatches  : {mismatched}")
    print(f"  invalid record size: {invalid}")
    print(f"  legacy-only        : {len(source_only)}")
    print(f"  vanilla-only       : {len(reference_only)}")

    if args.strict and (mismatched or invalid):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
