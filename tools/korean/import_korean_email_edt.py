#!/usr/bin/env python3
"""Import the vanilla-compatible Korean EMAIL.EDT from the legacy 1.13 patch.

The legacy 1.13 EMAIL.EDT contains additional records that do not exist in the
vanilla Stracciatella layout. EMAIL.EDT uses fixed 320-byte records, so retain
only the prefix required by Stracciatella's bundled localization reference.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MAIL_RECORD_SIZE = 320


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-root", type=Path, required=True)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("assets/mods/simplified-chinese-localization/data/BinaryData/EMAIL.EDT"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("assets/mods/korean-localization/data/BinaryData/EMAIL.EDT"),
    )
    args = parser.parse_args()

    source = args.legacy_root / "Patch" / "Data-1.13" / "BinaryData" / "EMAIL.EDT"
    if not source.is_file():
        raise SystemExit(f"Missing legacy Korean EMAIL.EDT: {source}")
    if not args.reference.is_file():
        raise SystemExit(f"Missing Stracciatella EMAIL.EDT reference: {args.reference}")

    source_data = source.read_bytes()
    target_size = args.reference.stat().st_size

    if target_size % MAIL_RECORD_SIZE:
        raise SystemExit(
            f"Reference EMAIL.EDT size {target_size} is not divisible by {MAIL_RECORD_SIZE}"
        )
    if len(source_data) % MAIL_RECORD_SIZE:
        raise SystemExit(
            f"Legacy EMAIL.EDT size {len(source_data)} is not divisible by {MAIL_RECORD_SIZE}"
        )
    if len(source_data) < target_size:
        raise SystemExit(
            f"Legacy EMAIL.EDT is shorter than reference: {len(source_data)} < {target_size}"
        )

    target_records = target_size // MAIL_RECORD_SIZE
    source_records = len(source_data) // MAIL_RECORD_SIZE
    trimmed_records = source_records - target_records

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(source_data[:target_size])

    if args.output.stat().st_size != target_size:
        raise SystemExit("EMAIL.EDT output size verification failed")

    print(
        f"EMAIL.EDT: source={source_records} records, target={target_records} records, "
        f"trimmed={trimmed_records} records, output={target_size} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
