#!/usr/bin/env python3
"""Import the vanilla-compatible Korean EMAIL.EDT from the legacy 1.13 patch.

The legacy 1.13 EMAIL.EDT contains additional records that do not exist in the
vanilla Stracciatella layout. EMAIL.EDT uses fixed 320-byte records, so retain
only the prefix required by Stracciatella's bundled localization reference.

Two legacy Korean records exactly fill all 160 UTF-16 code units. Stracciatella
force-terminates loaded EDT strings, which would discard the final code unit.
Apply narrowly-scoped wording fixes to those known records so every imported
mail string has an on-disk NUL terminator.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import struct


MAIL_RECORD_SIZE = 320
MAIL_RECORD_CHARS = MAIL_RECORD_SIZE // 2

# Use anchored substitutions instead of matching the whole legacy string.
# This still fails closed if the expected Korean phrase is absent, while
# tolerating harmless differences in the deliberately garbled terminal text
# embedded in Grizzly's answering-machine message.
FULL_WIDTH_RECORD_FIXES: dict[int, tuple[tuple[str, str], ...]] = {
    130: (
        ("메사지를", "메시지를"),
        ("도라왔다", "돌아왔다"),
        ("이 기술 쓰레기 정말 싫다.", "이 쓰레기 정말 싫다."),
    ),
    312: (
        ("절망적이지 않다고 받아들이기 시작했습니다.", "절망적이지 않다고 느끼기 시작했습니다."),
    ),
}


def decrypt_record(record: bytes) -> str:
    units = struct.unpack(f"<{MAIL_RECORD_CHARS}H", record)
    decoded: list[int] = []
    for unit in units:
        if unit == 0:
            break
        decoded.append(unit - 1 if unit > 33 else unit)
    return "".join(chr(unit) for unit in decoded)


def encrypt_record(text: str) -> bytes:
    if len(text) >= MAIL_RECORD_CHARS:
        raise ValueError(
            f"EMAIL.EDT replacement must leave room for NUL: {len(text)} >= {MAIL_RECORD_CHARS}"
        )
    encrypted = [ord(ch) + 1 if ord(ch) > 33 else ord(ch) for ch in text]
    encrypted.extend([0] * (MAIL_RECORD_CHARS - len(encrypted)))
    return struct.pack(f"<{MAIL_RECORD_CHARS}H", *encrypted)


def apply_full_width_fixes(data: bytearray) -> None:
    for record_index, substitutions in FULL_WIDTH_RECORD_FIXES.items():
        start = record_index * MAIL_RECORD_SIZE
        end = start + MAIL_RECORD_SIZE
        original = decrypt_record(bytes(data[start:end]))
        if len(original) != MAIL_RECORD_CHARS:
            raise SystemExit(
                f"EMAIL.EDT record {record_index} is no longer exactly {MAIL_RECORD_CHARS} chars; "
                "refusing to apply the legacy full-width fix"
            )

        replacement = original
        for old, new in substitutions:
            if old not in replacement:
                raise SystemExit(
                    f"EMAIL.EDT record {record_index} does not contain expected phrase {old!r}; "
                    "refusing to rewrite it"
                )
            replacement = replacement.replace(old, new, 1)

        data[start:end] = encrypt_record(replacement)
        if decrypt_record(bytes(data[start:end])) != replacement:
            raise SystemExit(f"EMAIL.EDT record {record_index} rewrite verification failed")
        print(
            f"EMAIL.EDT record {record_index}: shortened {len(original)} -> {len(replacement)} chars "
            "to preserve the runtime NUL terminator"
        )


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

    output_data = bytearray(source_data[:target_size])
    apply_full_width_fixes(output_data)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output_data)

    if args.output.stat().st_size != target_size:
        raise SystemExit("EMAIL.EDT output size verification failed")

    print(
        f"EMAIL.EDT: source={source_records} records, target={target_records} records, "
        f"trimmed={trimmed_records} records, output={target_size} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
