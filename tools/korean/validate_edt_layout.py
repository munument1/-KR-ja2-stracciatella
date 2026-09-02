#!/usr/bin/env python3
"""Validate Korean classic EDT assets against Stracciatella's bundled reference."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import struct
import sys

BYTES_PER_CHAR = 2
EXPECTED_COUNTS = {
    "MercEdt": 70,
    "NPCData": 164,
    "BinaryData": 20,
}

EXPECTED_MERC_NAMES = {
    *(f"{i:03d}.EDT" for i in range(62)),
    "063.EDT", "064.EDT", "066.EDT", "067.EDT", "068.EDT", "069.EDT", "070.EDT", "072.EDT",
}
REFERENCE_ONLY_NPC_FILES = {"56.edt"}

BINARY_LAYOUTS: dict[str, tuple[int, ...]] = {
    "AIMBIOS.EDT": (400, 160),
    "AIMHIST.EDT": (400,),
    "AIMPOL.EDT": (400,),
    "ALUMNAME.EDT": (80,),
    "ALUMNI.EDT": (80, 560),
    "BRAYDESC.EDT": (80, 320),
    "CREDITS.EDT": (80,),
    "EMAIL.EDT": (160,),
    "FILES.EDT": (400,),
    "FLOWERCARD.EDT": (400,),
    "FLOWERDESC.EDT": (80, 80, 320),
    "HELP.EDT": (640,),
    "IMPASS.EDT": (320,),
    "IMPTEXT.EDT": (400,),
    "INSURANCEMULTI.EDT": (400,),
    "INSURANCESINGLE.EDT": (80,),
    "ITEMDESC.EDT": (80, 80, 240),
    "MERCBIOS.EDT": (400, 160),
    "QUESTS.EDT": (80, 80),
    "RIS.EDT": (400,),
}

MERC_RE = re.compile(r"^\d{3}\.EDT$", re.IGNORECASE)
NPC_DIALOGUE_RE = re.compile(r"^(?:\d{2,3}|D_\d{3})\.EDT$", re.IGNORECASE)
NPC_CIV_RE = re.compile(r"^CIV\d{2}\.EDT$", re.IGNORECASE)
NPC_SECTOR_RE = re.compile(r"^[A-P]\d{1,2}\.EDT$", re.IGNORECASE)


def edt_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted((p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".edt"), key=lambda p: p.name.casefold())


def layout_for(group: str, filename: str) -> tuple[int, ...] | None:
    upper = filename.upper()
    if group == "BinaryData": return BINARY_LAYOUTS.get(upper)
    if group == "MercEdt": return (240,) if MERC_RE.fullmatch(filename) else None
    if group == "NPCData":
        if NPC_CIV_RE.fullmatch(filename) or NPC_SECTOR_RE.fullmatch(filename): return (160,)
        if NPC_DIALOGUE_RE.fullmatch(filename): return (240,)
    return None


def reference_dir(root: Path, group: str) -> Path:
    name = {"MercEdt": "MercEdt", "NPCData": "npcdata", "BinaryData": "BinaryData"}[group]
    return root / name


def malformed_decoded_unit(raw: int) -> bool:
    unit = raw - 1 if raw > 33 else raw
    return 0xD800 <= unit <= 0xDFFF or 0xFDD0 <= unit <= 0xFDEF or unit in (0xFFFE, 0xFFFF)


def validate_payload(path: Path, layout: tuple[int, ...]) -> list[str]:
    errors: list[str] = []
    data = path.read_bytes()
    stride = sum(layout) * BYTES_PER_CHAR
    if not data: return [f"{path}: empty EDT file"]
    if len(data) % stride: return [f"{path}: {len(data)} bytes is not divisible by {stride}-byte record size"]
    for row in range(len(data) // stride):
        cursor = row * stride
        for column, width in enumerate(layout):
            units = struct.unpack_from(f"<{width}H", data, cursor)
            try: end = units.index(0)
            except ValueError: end = width - 1
            for idx, raw in enumerate(units[:end]):
                if malformed_decoded_unit(raw):
                    return [f"{path}: row {row} col {column} char {idx} has decode-unsafe UTF-16 unit"]
            cursor += width * BYTES_PER_CHAR
    return errors


def validate_group(data_root: Path, ref_root: Path, group: str) -> tuple[int, int, list[str]]:
    errors: list[str] = []
    directory = data_root / group
    files = edt_files(directory)
    refs = edt_files(reference_dir(ref_root, group))
    ref_index = {p.name.casefold(): p for p in refs}
    actual = {p.name.casefold() for p in files}
    if len(files) != EXPECTED_COUNTS[group]: errors.append(f"{directory}: expected {EXPECTED_COUNTS[group]} EDT files, found {len(files)}")
    if group == "MercEdt":
        expected = {x.casefold() for x in EXPECTED_MERC_NAMES}
        missing, extra = sorted(expected - actual), sorted(actual - expected)
        if missing: errors.append(f"{directory}: missing MercEdt files: {', '.join(missing)}")
        if extra: errors.append(f"{directory}: unexpected MercEdt files: {', '.join(extra)}")
    elif group == "BinaryData":
        expected = {x.casefold() for x in BINARY_LAYOUTS}
        missing, extra = sorted(expected - actual), sorted(actual - expected)
        if missing: errors.append(f"{directory}: missing BinaryData files: {', '.join(missing)}")
        if extra: errors.append(f"{directory}: unexpected BinaryData files: {', '.join(extra)}")
    else:
        expected = {p.name.casefold() for p in refs if layout_for("NPCData", p.name) is not None and p.name.casefold() not in REFERENCE_ONLY_NPC_FILES}
        missing, extra = sorted(expected - actual), sorted(actual - expected)
        if missing: errors.append(f"{directory}: missing vanilla NPCData files: {', '.join(missing)}")
        if extra: errors.append(f"{directory}: unexpected NPCData files: {', '.join(extra)}")
    total_bytes = 0
    for path in files:
        layout = layout_for(group, path.name)
        if layout is None:
            errors.append(f"{path}: unknown EDT layout"); continue
        total_bytes += path.stat().st_size
        ref = ref_index.get(path.name.casefold())
        if ref is None:
            errors.append(f"{path}: no same-named bundled reference"); continue
        if path.stat().st_size != ref.stat().st_size:
            errors.append(f"{path}: size mismatch korean={path.stat().st_size}, reference={ref.stat().st_size}"); continue
        errors.extend(validate_payload(path, layout))
    return len(files), total_bytes, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    data_root = repo / "assets/mods/korean-localization/data"
    ref_root = repo / "assets/mods/simplified-chinese-localization/data"
    all_errors: list[str] = []
    total_files = total_bytes = 0
    print(f"Korean EDT root : {data_root}")
    print(f"Layout reference: {ref_root}\n")
    for group in ("MercEdt", "NPCData", "BinaryData"):
        count, size, errors = validate_group(data_root, ref_root, group)
        total_files += count; total_bytes += size; all_errors.extend(errors)
        print(f"{group}: files={count}, bytes={size}")
    print("\nSummary")
    print(f"  files  : {total_files} (expected {sum(EXPECTED_COUNTS.values())})")
    print(f"  bytes  : {total_bytes}")
    print(f"  errors : {len(all_errors)}")
    print(f"  result : {'FAIL' if all_errors else 'PASS'}")
    if all_errors:
        print("\nIssues", file=sys.stderr)
        for error in all_errors: print(f"  ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__": raise SystemExit(main())
