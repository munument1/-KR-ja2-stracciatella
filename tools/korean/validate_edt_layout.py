#!/usr/bin/env python3
"""Validate Korean JA2 Stracciatella classic EDT file layouts.

Classic EDT files contain fixed-width, ROT-1-obfuscated UTF-16LE strings and
carry no layout metadata. This validator mirrors the layouts used by the
Stracciatella loaders and also compares Korean files with the bundled
Simplified Chinese localization, which is used by the Korean import tools as
an exact vanilla/Stracciatella byte-size reference.
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
    "MercEdt": 54,
    "NPCData": 161,
    "BinaryData": 15,
}

# Character widths, as passed to openEDT()/loadEncryptedString().
BINARY_LAYOUTS: dict[str, tuple[int, ...]] = {
    "AIMHIST.EDT": (400,),
    "AIMPOL.EDT": (400,),
    "ALUMNAME.EDT": (80,),
    "ALUMNI.EDT": (80, 560),
    "CREDITS.EDT": (80,),
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
    return code_unit - 1 if code_unit > 33 else code_unit


def malformed_code_unit(code_unit: int) -> bool:
    return (
        0xD800 <= code_unit <= 0xDFFF
        or 0xFDD0 <= code_unit <= 0xFDEF
        or code_unit in (0xFFFE, 0xFFFF)
    )


def validate_field(
    *,
    data: bytes,
    offset: int,
    width_chars: int,
    path: Path,
    row: int,
    column: int,
    issues: list[Issue],
) -> None:
    units = struct.unpack_from(f"<{width_chars}H", data, offset)
    try:
        terminator = units.index(0)
        payload = units[:terminator]
        padding = units[terminator + 1 :]
        if any(padding):
            issues.append(
                Issue(
                    "WARNING",
                    path,
                    "non-zero UTF-16 data appears after the first NUL terminator",
                    row,
                    column,
                )
            )
    except ValueError:
        # LoadEncryptedData() forcibly NUL-terminates the final code unit, so a
        # completely full field loses its final on-disk code unit at runtime.
        payload = units[:-1]
        issues.append(
            Issue(
                "WARNING",
                path,
                "field has no on-disk NUL terminator; runtime will discard its final code unit",
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

    if group == "BinaryData":
        actual = {p.name.upper() for p in files}
        expected = set(BINARY_LAYOUTS)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            issues.append(
                Issue("ERROR", directory, f"missing layout files: {', '.join(missing)}")
            )
        if extra:
            issues.append(
                Issue("ERROR", directory, f"unrecognized layout files: {', '.join(extra)}")
            )

    reference_index: dict[str, Path] = {}
    if check_reference:
        ref_dir = reference_root / REFERENCE_DIRS[group]
        ref_files = edt_files(ref_dir)
        if not ref_files:
            issues.append(Issue("ERROR", ref_dir, "reference EDT directory missing or empty"))
        reference_index = index_casefold(ref_files)

    if verbose:
        print(f"[{group}]")

    for path in files:
        columns = layout_for(group, path.name)
        if columns is None:
            issues.append(
                Issue("ERROR", path, "no known Stracciatella EDT layout for this filename")
            )
            continue

        size = path.stat().st_size
        stats.bytes += size
        if size == 0:
            issues.append(Issue("ERROR", path, "empty EDT file"))
            continue
        if size % BYTES_PER_CHAR:
            issues.append(
                Issue("ERROR", path, f"odd byte length {size}; not valid UTF-16 storage")
            )
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

        if check_reference:
            ref = reference_index.get(path.name.casefold())
            if ref is None:
                issues.append(
                    Issue("ERROR", path, "no same-named Simplified Chinese vanilla-layout reference")
                )
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
                )
                cursor += width_chars * BYTES_PER_CHAR

        if verbose:
            print(
                f"  OK {path.name:<22} {size:>7} bytes  "
                f"row={stride:>4}  records={records:>3}  columns={columns}"
            )

    print(
        f"{group}: files={stats.files}, bytes={stats.bytes}, "
        f"records={stats.records}, fields={stats.fields}"
    )
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    script_path = Path(__file__).resolve()
    default_repo_root = (
        script_path.parents[2] if len(script_path.parents) > 2 else Path.cwd()
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_repo_root,
        help="JA2-Stracciatella checkout root (default: derived from this script)",
    )
    parser.add_argument(
        "--no-reference-check",
        action="store_true",
        help="skip exact byte-size comparison with the bundled Simplified Chinese vanilla-layout reference",
    )
    parser.add_argument("--verbose", action="store_true", help="print every validated file")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat content warnings as failures in addition to structural errors",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    data_root = repo_root / "assets" / "mods" / "korean-localization" / "data"
    reference_root = (
        repo_root / "assets" / "mods" / "simplified-chinese-localization" / "data"
    )

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

    failed = bool(errors) or (args.strict and bool(warnings))
    print(f"  result   : {'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
