#!/usr/bin/env python3
"""Remove Korean-only garbage after NUL terminators in classic EDT fields.

The classic JA2 EDT loaders stop at the first UTF-16 NUL in each fixed-width
field.  Old translation/import tooling can leave stale non-zero code units in
the unused tail of a field.  Those bytes are normally invisible, but keeping
fixed records clean avoids accidental garbage if a consumer scans or rewrites
the field differently.

Only residue that is present in the Korean file *and absent at the same field*
in the bundled Simplified Chinese vanilla-layout reference is removed.  Any
residue inherited from the reference layout is left untouched.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import struct
import sys

from validate_edt_layout import (
    BYTES_PER_CHAR,
    REFERENCE_DIRS,
    edt_files,
    index_casefold,
    layout_for,
    row_bytes,
)


def units_at(data: bytes | bytearray, offset: int, width_chars: int) -> tuple[int, ...]:
    return struct.unpack_from(f"<{width_chars}H", data, offset)


def residue_after_nul(units: tuple[int, ...]) -> tuple[int, ...]:
    try:
        nul = units.index(0)
    except ValueError:
        return ()
    return units[nul + 1 :]


def clear_after_first_nul(data: bytearray, offset: int, width_chars: int) -> int:
    units = units_at(data, offset, width_chars)
    try:
        nul = units.index(0)
    except ValueError:
        return 0

    changed_units = 0
    for index in range(nul + 1, width_chars):
        if units[index] != 0:
            struct.pack_into("<H", data, offset + index * BYTES_PER_CHAR, 0)
            changed_units += 1
    return changed_units


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[2]
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_repo_root,
        help="JA2-Stracciatella checkout root (default: derived from this script)",
    )
    parser.add_argument(
        "--expect-changed-fields",
        type=int,
        default=None,
        help="fail unless exactly this many Korean-only residue fields are cleaned",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    data_root = repo_root / "assets" / "mods" / "korean-localization" / "data"
    reference_root = (
        repo_root / "assets" / "mods" / "simplified-chinese-localization" / "data"
    )

    changed_fields = 0
    changed_units = 0
    changed_files: list[Path] = []
    inherited_residue_fields = 0

    for group in ("MercEdt", "NPCData", "BinaryData"):
        korean_files = edt_files(data_root / group)
        reference_files = index_casefold(edt_files(reference_root / REFERENCE_DIRS[group]))

        for path in korean_files:
            columns = layout_for(group, path.name)
            if columns is None:
                print(f"ERROR no known EDT layout for {path}", file=sys.stderr)
                return 2

            reference = reference_files.get(path.name.casefold())
            if reference is None:
                print(f"ERROR missing reference file for {path}", file=sys.stderr)
                return 2

            raw = path.read_bytes()
            ref_raw = reference.read_bytes()
            if len(raw) != len(ref_raw):
                print(
                    f"ERROR size mismatch for {path}: korean={len(raw)} reference={len(ref_raw)}",
                    file=sys.stderr,
                )
                return 2

            stride = row_bytes(columns)
            if len(raw) % stride:
                print(f"ERROR invalid row boundary for {path}", file=sys.stderr)
                return 2

            data = bytearray(raw)
            file_changed_fields = 0
            records = len(raw) // stride

            for row in range(records):
                cursor = row * stride
                for column, width_chars in enumerate(columns):
                    korean_units = units_at(data, cursor, width_chars)
                    reference_units = units_at(ref_raw, cursor, width_chars)
                    korean_residue = residue_after_nul(korean_units)
                    reference_residue = residue_after_nul(reference_units)

                    if any(korean_residue):
                        if any(reference_residue):
                            inherited_residue_fields += 1
                        else:
                            removed = clear_after_first_nul(data, cursor, width_chars)
                            if removed:
                                file_changed_fields += 1
                                changed_fields += 1
                                changed_units += removed
                                print(
                                    f"CLEAN {path.relative_to(repo_root)} row={row} col={column} "
                                    f"removed_units={removed}"
                                )
                    cursor += width_chars * BYTES_PER_CHAR

            if file_changed_fields:
                path.write_bytes(data)
                changed_files.append(path)

    print()
    print("Summary")
    print(f"  changed files             : {len(changed_files)}")
    print(f"  changed fields            : {changed_fields}")
    print(f"  cleared UTF-16 code units : {changed_units}")
    print(f"  inherited residue fields  : {inherited_residue_fields}")
    for path in changed_files:
        print(f"  file                      : {path.relative_to(repo_root)}")

    if args.expect_changed_fields is not None and changed_fields != args.expect_changed_fields:
        print(
            f"ERROR expected {args.expect_changed_fields} changed fields, got {changed_fields}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
