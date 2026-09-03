#!/usr/bin/env python3
"""Build vanilla-layout Korean BinaryData missing from the legacy Korean patch.

AIM/MERC biography files are copied from the JA2 1.13 Korean patch and trimmed to
Stracciatella's bundled vanilla reference size. Item/Bobby Ray text is rebuilt
from the Korean 1.13 Items.xml into the classic fixed-width encrypted EDT layout.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET

BYTES_PER_CHAR = 2


def normalize_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def encode_field(text: str, width_chars: int) -> bytes:
    text = (text or "").replace("\ufeff", "")
    raw = text.encode("utf-16-le")
    units = list(struct.unpack(f"<{len(raw) // 2}H", raw)) if raw else []
    units = units[: max(0, width_chars - 1)]
    if units and 0xD800 <= units[-1] <= 0xDBFF:
        units.pop()
    encrypted = [(u + 1 if u > 33 else u) & 0xFFFF for u in units]
    encrypted.append(0)
    encrypted.extend([0] * (width_chars - len(encrypted)))
    return struct.pack(f"<{width_chars}H", *encrypted)


def copy_trimmed(src: Path, ref: Path, dst: Path, row_chars: int) -> None:
    if not src.is_file():
        raise FileNotFoundError(src)
    if not ref.is_file():
        raise FileNotFoundError(ref)
    src_data = src.read_bytes()
    ref_size = ref.stat().st_size
    row_bytes = row_chars * BYTES_PER_CHAR
    if len(src_data) < ref_size:
        raise ValueError(f"{src}: legacy source shorter than vanilla reference ({len(src_data)} < {ref_size})")
    if len(src_data) % row_bytes or ref_size % row_bytes:
        raise ValueError(f"{src}: biography data is not aligned to {row_bytes}-byte records")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src_data[:ref_size])
    print(f"{dst.name}: {len(src_data) // row_bytes} legacy rows -> {ref_size // row_bytes} vanilla rows")


def parse_items(path: Path) -> dict[int, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    root = ET.parse(path).getroot()
    records: dict[int, dict[str, str]] = {}
    available: set[str] = set()
    for node in root.iter():
        fields: dict[str, str] = {}
        for child in list(node):
            key = normalize_tag(child.tag)
            available.add(key)
            fields[key] = child.text or ""
        if "uiindex" not in fields:
            continue
        try:
            idx = int(fields["uiindex"].strip())
        except ValueError:
            continue
        records[idx] = fields
    required = {"szitemname", "szlongitemname", "szitemdesc"}
    if not records or not required.issubset(available):
        raise ValueError(
            f"could not find expected Korean item fields in {path}; "
            f"records={len(records)}, tags={', '.join(sorted(available)[:80])}"
        )
    return records


def first(fields: dict[str, str], *names: str, fallback: str = "") -> str:
    for name in names:
        value = fields.get(name.casefold(), "")
        if value:
            return value
    return fallback


def build_item_files(items_xml: Path, item_ref: Path, bray_ref: Path, item_dst: Path, bray_dst: Path) -> None:
    records = parse_items(items_xml)
    item_stride_chars = 80 + 80 + 240
    bray_stride_chars = 80 + 320
    item_stride_bytes = item_stride_chars * BYTES_PER_CHAR
    bray_stride_bytes = bray_stride_chars * BYTES_PER_CHAR
    if item_ref.stat().st_size % item_stride_bytes:
        raise ValueError(f"{item_ref}: invalid ITEMDESC reference size")
    if bray_ref.stat().st_size % bray_stride_bytes:
        raise ValueError(f"{bray_ref}: invalid BRAYDESC reference size")
    item_count = item_ref.stat().st_size // item_stride_bytes
    bray_count = bray_ref.stat().st_size // bray_stride_bytes
    if item_count != bray_count:
        raise ValueError(f"reference item counts disagree: ITEMDESC={item_count}, BRAYDESC={bray_count}")

    item_out = bytearray()
    bray_out = bytearray()
    translated_names = translated_desc = translated_bray = 0
    for idx in range(item_count):
        fields = records.get(idx, {})
        short_name = first(fields, "szItemName")
        long_name = first(fields, "szLongItemName", fallback=short_name)
        description = first(fields, "szItemDesc")
        br_name = first(fields, "szBRName", "szBRItemName", fallback=short_name)
        br_desc = first(fields, "szBRDesc", "szBRItemDesc", fallback=description)

        item_out.extend(encode_field(short_name, 80))
        item_out.extend(encode_field(long_name, 80))
        item_out.extend(encode_field(description, 240))
        bray_out.extend(encode_field(br_name, 80))
        bray_out.extend(encode_field(br_desc, 320))

        translated_names += int(bool(short_name or long_name))
        translated_desc += int(bool(description))
        translated_bray += int(bool(br_name or br_desc))

    if len(item_out) != item_ref.stat().st_size or len(bray_out) != bray_ref.stat().st_size:
        raise AssertionError("generated item EDT size mismatch")
    if translated_names < 200 or translated_desc < 100:
        raise ValueError(
            f"Korean Items.xml coverage unexpectedly low: names={translated_names}, descriptions={translated_desc}"
        )

    item_dst.parent.mkdir(parents=True, exist_ok=True)
    item_dst.write_bytes(item_out)
    bray_dst.write_bytes(bray_out)
    print(
        f"ITEMDESC/BRAYDESC: vanilla items={item_count}, "
        f"named={translated_names}, described={translated_desc}, bobby-ray-text={translated_bray}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    legacy = args.legacy_root.resolve()
    ref = repo / "assets/mods/simplified-chinese-localization/data/BinaryData"
    dst = repo / "assets/mods/korean-localization/data/BinaryData"
    legacy_bin = legacy / "Patch/Data-1.13/BinaryData"

    copy_trimmed(
        legacy_bin / "AIMBIOS.EDT", ref / "AIMBIOS.EDT", dst / "AIMBIOS.EDT", 560
    )
    copy_trimmed(
        legacy_bin / "MERCBIOS.EDT", ref / "MERCBIOS.EDT", dst / "MERCBIOS.EDT", 560
    )
    build_item_files(
        legacy / "Patch/Data-1.13/TableData/Items/Items.xml",
        ref / "ITEMDESC.EDT",
        ref / "BRAYDESC.EDT",
        dst / "ITEMDESC.EDT",
        dst / "BRAYDESC.EDT",
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
