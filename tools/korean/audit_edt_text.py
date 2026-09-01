#!/usr/bin/env python3
"""Audit decoded Korean EDT text for high-confidence foreign/garbled characters.

The structural EDT validator proves that a file can be read safely, but structurally
valid UTF-16 can still contain text imported with the wrong encoding. This tool
mirrors Stracciatella's ROT-1 decode and reports suspicious script ranges that should
not normally appear in a Korean localization (CJK ideographs, Japanese kana,
Bopomofo, Cyrillic, private-use characters, and unexpected control codes).

It is intentionally conservative: Hangul, ASCII, Latin/Latin-extended text, normal
Unicode punctuation/symbols, and whitespace are accepted. Each finding includes the
EDT file, row/column, code point, decoded Korean text, and the same decoded field from
the bundled Simplified Chinese vanilla-layout reference when available. The reference
is diagnostic only; it helps identify the intended meaning before changing game text.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import struct
import sys
import unicodedata

from validate_edt_layout import (
    BYTES_PER_CHAR,
    EXPECTED_COUNTS,
    REFERENCE_DIRS,
    decrypt_rot1,
    edt_files,
    layout_for,
    row_bytes,
)


@dataclass(frozen=True)
class Finding:
    group: str
    path: Path
    row: int
    column: int
    index: int
    char: str
    kind: str
    text: str


def classify_suspicious(ch: str) -> str | None:
    cp = ord(ch)

    # C0/C1 controls are never expected inside displayed dialogue except TAB/LF/CR.
    if (cp < 0x20 and cp not in (0x09, 0x0A, 0x0D)) or 0x7F <= cp <= 0x9F:
        return "control"

    ranges = (
        (0x3400, 0x4DBF, "CJK Extension A"),
        (0x4E00, 0x9FFF, "CJK ideograph"),
        (0xF900, 0xFAFF, "CJK compatibility ideograph"),
        (0x3040, 0x309F, "Hiragana"),
        (0x30A0, 0x30FF, "Katakana"),
        (0x31F0, 0x31FF, "Katakana extension"),
        (0xFF65, 0xFF9F, "halfwidth Katakana"),
        (0x3100, 0x312F, "Bopomofo"),
        (0x31A0, 0x31BF, "Bopomofo extension"),
        (0x0400, 0x052F, "Cyrillic"),
        (0xE000, 0xF8FF, "private use"),
    )
    for start, end, label in ranges:
        if start <= cp <= end:
            return label

    if cp in (0xFEFF, 0xFFFC, 0xFFFD):
        return {
            0xFEFF: "embedded BOM",
            0xFFFC: "object replacement character",
            0xFFFD: "replacement character",
        }[cp]

    return None


def decode_field(data: bytes, offset: int, width_chars: int) -> str:
    units = struct.unpack_from(f"<{width_chars}H", data, offset)
    try:
        end = units.index(0)
    except ValueError:
        # Match LoadEncryptedData(): the runtime reserves the final unit for NUL.
        end = max(0, len(units) - 1)

    decoded = [decrypt_rot1(unit) for unit in units[:end]]
    return "".join(chr(unit) for unit in decoded)


def preview(text: str, limit: int = 120) -> str:
    escaped = text.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    if len(escaped) > limit:
        return escaped[: limit - 1] + "…"
    return escaped


def decode_reference_field(
    *,
    reference_root: Path,
    finding: Finding,
) -> str | None:
    columns = layout_for(finding.group, finding.path.name)
    if columns is None or finding.column >= len(columns):
        return None

    ref_dir = REFERENCE_DIRS[finding.group]
    ref_path = reference_root / ref_dir / finding.path.name
    if not ref_path.is_file():
        # Preserve the validator's case-insensitive reference behavior.
        candidates = {p.name.casefold(): p for p in edt_files(reference_root / ref_dir)}
        ref_path = candidates.get(finding.path.name.casefold())
        if ref_path is None:
            return None

    data = ref_path.read_bytes()
    stride = row_bytes(columns)
    if not data or len(data) % stride:
        return None
    if finding.row >= len(data) // stride:
        return None

    offset = finding.row * stride
    offset += sum(columns[: finding.column]) * BYTES_PER_CHAR
    return decode_field(data, offset, columns[finding.column])


def scan_group(group: str, data_root: Path) -> tuple[int, int, list[Finding]]:
    directory = data_root / group
    files = edt_files(directory)
    fields_scanned = 0
    chars_scanned = 0
    findings: list[Finding] = []

    for path in files:
        columns = layout_for(group, path.name)
        if columns is None:
            continue
        stride = row_bytes(columns)
        data = path.read_bytes()
        if not data or len(data) % stride:
            # Structural problems are the responsibility of validate_edt_layout.py.
            continue

        records = len(data) // stride
        for row in range(records):
            cursor = row * stride
            for column, width_chars in enumerate(columns):
                text = decode_field(data, cursor, width_chars)
                fields_scanned += 1
                chars_scanned += len(text)
                for index, ch in enumerate(text):
                    kind = classify_suspicious(ch)
                    if kind is not None:
                        findings.append(
                            Finding(group, path, row, column, index, ch, kind, text)
                        )
                cursor += width_chars * BYTES_PER_CHAR

    return fields_scanned, chars_scanned, findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    script_path = Path(__file__).resolve()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=script_path.parents[2],
        help="JA2-Stracciatella checkout root",
    )
    parser.add_argument(
        "--group",
        action="append",
        choices=tuple(EXPECTED_COUNTS),
        help="scan only this EDT group; may be repeated",
    )
    parser.add_argument(
        "--max-details",
        type=int,
        default=200,
        help="maximum individual findings printed (default: 200)",
    )
    parser.add_argument(
        "--fail-on-suspicious",
        action="store_true",
        help="return exit code 1 when any suspicious decoded character is found",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    repo_root = args.repo_root.resolve()
    data_root = repo_root / "assets" / "mods" / "korean-localization" / "data"
    reference_root = (
        repo_root / "assets" / "mods" / "simplified-chinese-localization" / "data"
    )
    groups = args.group or list(EXPECTED_COUNTS)

    total_fields = 0
    total_chars = 0
    findings: list[Finding] = []

    print(f"Korean EDT root: {data_root}")
    print(f"Reference root : {reference_root}")
    print(f"Groups         : {', '.join(groups)}")
    print()

    for group in groups:
        fields, chars, group_findings = scan_group(group, data_root)
        total_fields += fields
        total_chars += chars
        findings.extend(group_findings)
        print(
            f"{group}: fields={fields}, decoded_chars={chars}, "
            f"suspicious_chars={len(group_findings)}"
        )

    if findings:
        print("\nSuspicious decoded text")
        shown_reference_records: set[tuple[str, str, int, int]] = set()
        for finding in findings[: max(0, args.max_details)]:
            try:
                rel = finding.path.relative_to(repo_root)
            except ValueError:
                rel = finding.path
            name = unicodedata.name(finding.char, "UNNAMED")
            print(
                f"  {rel} row={finding.row} col={finding.column} char={finding.index} "
                f"U+{ord(finding.char):04X} {finding.kind} ({name}): "
                f"{preview(finding.text)}"
            )

            key = (finding.group, finding.path.as_posix(), finding.row, finding.column)
            if key not in shown_reference_records:
                shown_reference_records.add(key)
                reference_text = decode_reference_field(
                    reference_root=reference_root,
                    finding=finding,
                )
                if reference_text is not None:
                    print(f"    reference: {preview(reference_text)}")

        if len(findings) > args.max_details:
            print(f"  ... {len(findings) - args.max_details} additional findings omitted")

        counts = Counter(f.kind for f in findings)
        print("\nKinds")
        for kind, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            print(f"  {kind:<32} {count}")

    affected_records = {
        (f.group, f.path.as_posix(), f.row, f.column) for f in findings
    }
    affected_files = {f.path.as_posix() for f in findings}

    print("\nSummary")
    print(f"  fields scanned     : {total_fields}")
    print(f"  decoded characters : {total_chars}")
    print(f"  suspicious chars   : {len(findings)}")
    print(f"  affected records   : {len(affected_records)}")
    print(f"  affected files     : {len(affected_files)}")
    print(f"  result             : {'SUSPICIOUS' if findings else 'PASS'}")

    if args.fail_on_suspicious and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
