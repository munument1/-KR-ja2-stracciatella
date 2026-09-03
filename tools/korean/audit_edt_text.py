#!/usr/bin/env python3
"""Audit decoded Korean EDT text for high-confidence foreign/garbled characters.

The structural EDT validator proves that a file can be read safely, but structurally
valid UTF-16 can still contain text imported with the wrong encoding. This tool
mirrors the Korean runtime path in LoadEncryptedData(): ROT-1 followed by the legacy
Ivan-Dolvich Cyrillic repair used by all non-Russian resource versions.

Hangul, ASCII, Latin/Latin-extended text, normal Unicode punctuation/symbols, and
whitespace are accepted. CJK ideographs, Japanese kana, Bopomofo, Cyrillic,
private-use characters, and unexpected control codes are reported, except for an
exact allowlist of intentional foreign-language quotes inherited from vanilla JA2.
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


# Exact runtime-decoded foreign-language lines intentionally present in vanilla JA2.
# Quote 73 is QUOTE_ME_TOO in Dialogue_Control.h. Ivan's vanilla EDT stores the
# Russian "Я ТОЖЕ." through JA2's historical broken Cyrillic encoding; the engine
# explicitly repairs that encoding in LoadEncryptedData(). EMAIL.EDT row 156 also
# contains an intentionally garbled A.I.M. forwarded-message payload; bundled
# vanilla localization references preserve the same Cyrillic-style transmission.
# Keep exact guards so any different Cyrillic text still fails the audit.
INTENTIONAL_FOREIGN_TEXT: dict[tuple[str, str, int, int], str] = {
    ("MercEdt", "007.edt", 73, 0): "Я ТОЖЕ.",
    ("BinaryData", "email.edt", 156, 0): "AIM 서버에서 온 전달 메시지: НАИdАМ ПИЕИЙСИ",
}


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


def decode_korean_runtime_unit(raw_unit: int) -> int:
    """Mirror the SE_NORMAL branch used by GameVersion::KOREAN."""
    c = decrypt_rot1(raw_unit)

    # LoadEncryptedData() repairs Ivan Dolvich's intentionally Russian lines in all
    # non-Russian versions after the language-specific conversion block.
    if 0x044D <= c <= 0x0452:  # encoded Cyrillic A .. IE
        c += -0x044D + 0x0410
    elif c == 0x0453:  # encoded Cyrillic IO
        c = 0x0401
    elif 0x0454 <= c <= 0x0467:  # encoded ZHE .. SHCHA
        c += -0x0454 + 0x0416
    elif 0x0468 <= c <= 0x046C:  # encoded YERU .. YA
        c += -0x0468 + 0x042B

    return c


def decode_field(data: bytes, offset: int, width_chars: int) -> str:
    units = struct.unpack_from(f"<{width_chars}H", data, offset)
    try:
        end = units.index(0)
    except ValueError:
        # LoadEncryptedData() reserves the final unit for an in-memory NUL.
        end = max(0, len(units) - 1)

    decoded = [decode_korean_runtime_unit(unit) for unit in units[:end]]
    return "".join(chr(unit) for unit in decoded)


def preview(text: str, limit: int = 120) -> str:
    escaped = text.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    if len(escaped) > limit:
        return escaped[: limit - 1] + "…"
    return escaped


def decode_reference_field(
    *, reference_root: Path, finding: Finding
) -> str | None:
    columns = layout_for(finding.group, finding.path.name)
    if columns is None or finding.column >= len(columns):
        return None

    ref_dir = REFERENCE_DIRS[finding.group]
    ref_path = reference_root / ref_dir / finding.path.name
    if not ref_path.is_file():
        candidates = {p.name.casefold(): p for p in edt_files(reference_root / ref_dir)}
        ref_path = candidates.get(finding.path.name.casefold())
        if ref_path is None:
            return None

    data = ref_path.read_bytes()
    stride = row_bytes(columns)
    if not data or len(data) % stride or finding.row >= len(data) // stride:
        return None

    offset = finding.row * stride
    offset += sum(columns[: finding.column]) * BYTES_PER_CHAR
    return decode_field(data, offset, columns[finding.column])


def scan_group(group: str, data_root: Path) -> tuple[int, int, int, list[Finding]]:
    directory = data_root / group
    files = edt_files(directory)
    fields_scanned = 0
    chars_scanned = 0
    intentional_records = 0
    findings: list[Finding] = []

    for path in files:
        columns = layout_for(group, path.name)
        if columns is None:
            continue
        stride = row_bytes(columns)
        data = path.read_bytes()
        if not data or len(data) % stride:
            continue

        records = len(data) // stride
        for row in range(records):
            cursor = row * stride
            for column, width_chars in enumerate(columns):
                text = decode_field(data, cursor, width_chars)
                fields_scanned += 1
                chars_scanned += len(text)

                allow_key = (group, path.name.casefold(), row, column)
                allowed = INTENTIONAL_FOREIGN_TEXT.get(allow_key)
                if allowed is not None and text == allowed:
                    intentional_records += 1
                    cursor += width_chars * BYTES_PER_CHAR
                    continue

                for index, ch in enumerate(text):
                    kind = classify_suspicious(ch)
                    if kind is not None:
                        findings.append(
                            Finding(group, path, row, column, index, ch, kind, text)
                        )
                cursor += width_chars * BYTES_PER_CHAR

    return fields_scanned, chars_scanned, intentional_records, findings


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
    reference_root = repo_root / "assets" / "mods" / "simplified-chinese-localization" / "data"
    groups = args.group or list(EXPECTED_COUNTS)

    total_fields = 0
    total_chars = 0
    total_intentional = 0
    findings: list[Finding] = []

    print(f"Korean EDT root: {data_root}")
    print(f"Reference root : {reference_root}")
    print(f"Groups         : {', '.join(groups)}")
    print()

    for group in groups:
        fields, chars, intentional, group_findings = scan_group(group, data_root)
        total_fields += fields
        total_chars += chars
        total_intentional += intentional
        findings.extend(group_findings)
        print(
            f"{group}: fields={fields}, decoded_chars={chars}, "
            f"intentional_foreign={intentional}, suspicious_chars={len(group_findings)}"
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
                f"U+{ord(finding.char):04X} {finding.kind} ({name}): {preview(finding.text)}"
            )

            key = (finding.group, finding.path.as_posix(), finding.row, finding.column)
            if key not in shown_reference_records:
                shown_reference_records.add(key)
                reference_text = decode_reference_field(
                    reference_root=reference_root, finding=finding
                )
                if reference_text is not None:
                    print(f"    reference: {preview(reference_text)}")

        if len(findings) > args.max_details:
            print(f"  ... {len(findings) - args.max_details} additional findings omitted")

        counts = Counter(f.kind for f in findings)
        print("\nKinds")
        for kind, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            print(f"  {kind:<32} {count}")

    affected_records = {(f.group, f.path.as_posix(), f.row, f.column) for f in findings}
    affected_files = {f.path.as_posix() for f in findings}

    print("\nSummary")
    print(f"  fields scanned      : {total_fields}")
    print(f"  decoded characters  : {total_chars}")
    print(f"  intentional foreign : {total_intentional}")
    print(f"  suspicious chars    : {len(findings)}")
    print(f"  affected records    : {len(affected_records)}")
    print(f"  affected files      : {len(affected_files)}")
    print(f"  result              : {'SUSPICIOUS' if findings else 'PASS'}")

    if args.fail_on_suspicious and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
