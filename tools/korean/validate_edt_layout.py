#!/usr/bin/env python3
"""Validate Korean JA2 Stracciatella classic EDT file layouts.

Classic EDT files contain fixed-width, ROT-1-obfuscated UTF-16LE strings and
carry no layout metadata. This validator mirrors the layouts used by the
Stracciatella loaders and compares Korean files with the bundled Simplified
Chinese localization, which is used as an exact vanilla/Stracciatella layout
reference.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import struct
import sys


BYTES_PER_CHAR = 2
EXPECTED_COUNTS = {
    # 70 translated/safely reconstructed runtime files. 200.EDT is the
    # NO_PROFILE sentinel and intentionally remains a base-game fallback.
    "MercEdt": 70,
    # Includes SKYRIDER (097.EDT).  The previous 161-file count accidentally
    # omitted this valid vanilla NPC dialogue file.
    "NPCData": 162,
    "BinaryData": 16,
}

# Exact translated MercEdt profile set.  A count alone can miss a replacement
# error where one required profile disappears and another file is added.
EXPECTED_MERC_NAMES = {
    *(f"{i:03d}.EDT" for i in range(62)),
    "063.EDT",
    "064.EDT",
    "066.EDT",
    "067.EDT",
    "068.EDT",
    "069.EDT",
    "070.EDT",
    "072.EDT",
}

# Character widths, as passed to openEDT()/loadEncryptedString().
BINARY_LAYOUTS: dict[str, tuple[int, ...]] = {
    "AIMHIST.EDT": (400,),
    "AIMPOL.EDT": (400,),
    "ALUMNAME.EDT": (80,),
    "ALUMNI.EDT": (80, 560),
    "CREDITS.EDT": (80,),
    # EMail.cc uses MAIL_STRING_SIZE == 320 bytes per encrypted record,
    # corresponding to 160 UTF-16 code units on disk.
    "EMAIL.EDT": (160,),
    "FILES.EDT": (400,),
    "FLOWERCARD.EDT": (400,),
    "FLOWERDESC.EDT": (80, 80, 320),
    "HELP.EDT": (640,),
    "IMPASS.EDT": (320,),
    "IMPTEXT.EDT": (400,),
    "INSURANCEMULTI.EDT": (400,),
    "INSURANCESINGLE.EDT": (80,),
    "QUESTS.EDT": (80, 80),
    "RIS.EDT": (400,),
}

REFERENCE_DIRS = {
    "MercEdt": "MercEdt",
    "NPCData": "npcdata",
    "BinaryData": "BinaryData",
}

MERC_RE = re.compile(r"^\d{3}\.EDT$", re.IGNORECASE)
NPC_DIALOGUE_RE = re.compile(r"^(?:\d{2,3}|D_\d{3})\.EDT$", re.IGNORECASE)
NPC_CIV_RE = re.compile(r"^CIV\d{2}\.EDT$", re.IGNORECASE)
NPC_SECTOR_RE = re.compile(r"^[A-P]\d{1,2}\.EDT$", re.IGNORECASE)


@dataclass(frozen=True)
class Issue:
    severity: str
    path: Path
    message: str
    row: int | None = None
    column: int | None = None

    def render(self, repo_root: Path) -> str:
        try:
            display_path = self.path.relative_to(repo_root)
        except ValueError:
            display_path = self.path
        location = ""
        if self.row is not None:
            location += f" row={self.row}"
        if self.column is not None:
            location += f" col={self.column}"
        return f"{self.severity:<7} {display_path}{location}: {self.message}"


@dataclass
class GroupStats:
    files: int = 0
    bytes: int = 0
    records: int = 0
    fields: int = 0


def edt_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        (p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".edt"),
        key=lambda p: p.name.casefold(),
    )


def index_casefold(paths: list[Path]) -> dict[str, Path]:
    return {p.name.casefold(): p for p in paths}


def layout_for(group: str, filename: str) -> tuple[int, ...] | None:
    upper = filename.upper()
    if group == "BinaryData":
        return BINARY_LAYOUTS.get(upper)
    if group == "MercEdt":
        return (240,) if MERC_RE.fullmatch(filename) else None
    if group == "NPCData":
        if NPC_CIV_RE.fullmatch(filename) or NPC_SECTOR_RE.fullmatch(filename):
            # Civ_Quotes.cc uses CIV_QUOTE_TEXT_SIZE == 160.
            return (160,)
        if NPC_DIALOGUE_RE.fullmatch(filename):
            # Normal NPC dialogue files use DIALOGUESIZE == 240.
            return (240,)
    return None


def row_bytes(columns: tuple[int, ...]) -> int:
    return sum(columns) * BYTES_PER_CHAR


def decrypt_rot1(code_unit: int) -> int:
    # Mirrors LoadEncryptedString(): only values above ASCII '!' are shifted.
    return code_unit - 1 if code_unit > 33 else code_unit


def malformed_code_unit(code_unit: int) -> bool:
    return (
        0xD800 <= code_unit <= 0xDFFF
        or 0xFDD0 <= code_unit <= 0xFDEF
        or code_unit in (0xFFFE, 0xFFFF)
    )


def unpack_field(data: bytes, offset: int, width_chars: int) -> tuple[int, ...]:
    return struct.unpack_from(f"<{width_chars}H", data, offset)


def first_nul(units: tuple[int, ...]) -> int | None:
    try:
        return units.index(0)
    except ValueError:
        return None


def has_post_nul_data(units: tuple[int, ...]) -> bool:
    terminator = first_nul(units)
    return terminator is not None and any(units[terminator + 1 :])


def validate_field(
    *,
    data: bytes,
    offset: int,
    width_chars: int,
    path: Path,
    row: int,
    column: int,
    issues: list[Issue],
    reference_data: bytes | None = None,
    reference_offset: int | None = None,
) -> None:
    units = unpack_field(data, offset, width_chars)
    terminator = first_nul(units)

    if terminator is None:
        # LoadEncryptedData() forcibly NUL-terminates the final code unit, so a
        # completely full field loses its final on-disk code unit at runtime.
        payload = units[:-1]
        reference_full = False
        if reference_data is not None and reference_offset is not None:
            reference_units = unpack_field(reference_data, reference_offset, width_chars)
            reference_full = first_nul(reference_units) is None
        issues.append(
            Issue(
                "INFO" if reference_full else "WARNING",
                path,
                (
                    "field has no on-disk NUL terminator; the same full-width layout is present in the reference"
                    if reference_full
                    else "field has no on-disk NUL terminator; runtime will discard its final code unit"
                ),
                row,
                column,
            )
        )
    else:
        payload = units[:terminator]
        if has_post_nul_data(units):
            inherited = False
            if reference_data is not None and reference_offset is not None:
                reference_units = unpack_field(reference_data, reference_offset, width_chars)
                inherited = has_post_nul_data(reference_units)
            issues.append(
                Issue(
                    "INFO" if inherited else "WARNING",
                    path,
                    (
                        "non-zero UTF-16 data appears after the first NUL terminator; the same residue exists in the reference"
                        if inherited
                        else "non-zero UTF-16 data appears after the first NUL terminator; Korean-only residue"
                    ),
                    row,
                    column,
                )
            )

    for idx, raw_unit in enumerate(payload):
        unit = decrypt_rot1(raw_unit)
        if malformed_code_unit(unit):
            issues.append(
                Issue(
                    "ERROR",
                    path,
                    f"invalid/decode-unsafe UTF-16 code unit U+{unit:04X} at character {idx}",
                    row,
                    column,
                )
            )
            break
        if unit == 0xFFFD:
            issues.append(
                Issue(
                    "WARNING",
                    path,
                    f"replacement character U+FFFD at character {idx}",
                    row,
                    column,
                )
            )
            break


def report_set_difference(
    *,
    path: Path,
    actual: set[str],
    expected: set[str],
    issues: list[Issue],
    label: str,
) -> None:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        issues.append(Issue("ERROR", path, f"missing {label}: {', '.join(missing)}"))
    if extra:
        issues.append(Issue("ERROR", path, f"unexpected {label}: {', '.join(extra)}"))


def validate_group(
    *,
    group: str,
    data_root: Path,
    reference_root: Path,
    repo_root: Path,
    check_reference: bool,
    issues: list[Issue],
    verbose: bool,
) -> GroupStats:
    directory = data_root / group
    files = edt_files(directory)
    stats = GroupStats(files=len(files))

    expected_count = EXPECTED_COUNTS[group]
    if len(files) != expected_count:
        issues.append(
            Issue(
                "ERROR",
                directory,
                f"expected {expected_count} EDT files, found {len(files)}",
            )
        )

    actual_upper = {p.name.upper() for p in files}
    if group == "BinaryData":
        report_set_difference(
            path=directory,
            actual=actual_upper,
            expected=set(BINARY_LAYOUTS),
            issues=issues,
            label="layout files",
        )
    elif group == "MercEdt":
        report_set_difference(
            path=directory,
            actual=actual_upper,
            expected=EXPECTED_MERC_NAMES,
            issues=issues,
            label="translated MercEdt files",
        )

    reference_index: dict[str, Path] = {}
    if check_reference:
        ref_dir = reference_root / REFERENCE_DIRS[group]
        ref_files = edt_files(ref_dir)
        if not ref_files:
            issues.append(Issue("ERROR", ref_dir, "reference EDT directory missing or empty"))
        reference_index = index_casefold(ref_files)

        # NPCData is a direct runtime data family.  Require exact filename
        # parity with the bundled vanilla reference so a valid NPC cannot
        # silently fall back to English merely because the total count matches.
        if group == "NPCData" and ref_files:
            expected_npc = {
                p.name.casefold()
                for p in ref_files
                if layout_for("NPCData", p.name) is not None
            }
            actual_npc = {p.name.casefold() for p in files}
            report_set_difference(
                path=directory,
                actual=actual_npc,
                expected=expected_npc,
                issues=issues,
                label="vanilla NPCData files",
            )

    if verbose:
        print(f"[{group}]")

    for path in files:
        columns = layout_for(group, path.name)
        if columns is None:
            issues.append(Issue("ERROR", path, "no known Stracciatella EDT layout for this filename"))
            continue

        size = path.stat().st_size
        stats.bytes += size
        if size == 0:
            issues.append(Issue("ERROR", path, "empty EDT file"))
            continue
        if size % BYTES_PER_CHAR:
            issues.append(Issue("ERROR", path, f"odd byte length {size}; not valid UTF-16 storage"))
            continue

        stride = row_bytes(columns)
        if size % stride:
            issues.append(
                Issue(
                    "ERROR",
                    path,
                    f"{size} bytes is not divisible by {stride}-byte row size for columns {columns}",
                )
            )
            continue

        records = size // stride
        if records == 0:
            issues.append(Issue("ERROR", path, "contains zero complete records"))
            continue

        stats.records += records
        stats.fields += records * len(columns)

        reference_data: bytes | None = None
        if check_reference:
            ref = reference_index.get(path.name.casefold())
            if ref is None:
                issues.append(Issue("ERROR", path, "no same-named Simplified Chinese vanilla-layout reference"))
            else:
                ref_size = ref.stat().st_size
                if ref_size != size:
                    issues.append(
                        Issue(
                            "ERROR",
                            path,
                            f"size differs from vanilla-layout reference: korean={size}, reference={ref_size}",
                        )
                    )
                else:
                    reference_data = ref.read_bytes()

        data = path.read_bytes()
        for row in range(records):
            cursor = row * stride
            for column, width_chars in enumerate(columns):
                validate_field(
                    data=data,
                    offset=cursor,
                    width_chars=width_chars,
                    path=path,
                    row=row,
                    column=column,
                    issues=issues,
                    reference_data=reference_data,
                    reference_offset=cursor if reference_data is not None else None,
                )
                cursor += width_chars * BYTES_PER_CHAR

        if verbose:
            print(
                f"  OK {path.name:<22} {size:>7} bytes  row={stride:>4}  "
                f"records={records:>3}  columns={columns}"
            )

    print(
        f"{group}: files={stats.files}, bytes={stats.bytes}, "
        f"records={stats.records}, fields={stats.fields}"
    )
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[2] if len(script_path.parents) > 2 else Path.cwd()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_repo_root,
        help="JA2-Stracciatella checkout root (default: derived from this script)",
    )
    parser.add_argument(
        "--no-reference-check",
        action="store_true",
        help="skip exact byte-size/content-anomaly comparison with the bundled Simplified Chinese vanilla-layout reference",
    )
    parser.add_argument("--verbose", action="store_true", help="print every validated file")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat Korean-only content warnings as failures in addition to structural errors",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    data_root = repo_root / "assets" / "mods" / "korean-localization" / "data"
    reference_root = repo_root / "assets" / "mods" / "simplified-chinese-localization" / "data"

    issues: list[Issue] = []
    totals = GroupStats()

    print(f"Korean EDT root : {data_root}")
    if not args.no_reference_check:
        print(f"Layout reference: {reference_root}")
    print()

    for group in ("MercEdt", "NPCData", "BinaryData"):
        stats = validate_group(
            group=group,
            data_root=data_root,
            reference_root=reference_root,
            repo_root=repo_root,
            check_reference=not args.no_reference_check,
            issues=issues,
            verbose=args.verbose,
        )
        totals.files += stats.files
        totals.bytes += stats.bytes
        totals.records += stats.records
        totals.fields += stats.fields
        print()

    errors = [issue for issue in issues if issue.severity == "ERROR"]
    warnings = [issue for issue in issues if issue.severity == "WARNING"]
    infos = [issue for issue in issues if issue.severity == "INFO"]

    if issues:
        print("Issues")
        max_details = 100
        for issue in issues[:max_details]:
            print(" ", issue.render(repo_root))
        if len(issues) > max_details:
            print(f"  ... {len(issues) - max_details} additional issues omitted")
        print()

    print("Summary")
    print(f"  files    : {totals.files} (expected {sum(EXPECTED_COUNTS.values())})")
    print(f"  bytes    : {totals.bytes}")
    print(f"  records  : {totals.records}")
    print(f"  fields   : {totals.fields}")
    print(f"  errors   : {len(errors)}")
    print(f"  warnings : {len(warnings)}")
    print(f"  info     : {len(infos)}")

    failed = bool(errors) or (args.strict and bool(warnings))
    print(f"  result   : {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
