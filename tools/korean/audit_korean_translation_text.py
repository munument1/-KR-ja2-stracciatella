#!/usr/bin/env python3
"""Fail on high-confidence English fallback in Korean runtime BinaryData text."""

from __future__ import annotations

from pathlib import Path
import re
import sys

from audit_edt_text import decode_field
from validate_edt_layout import BYTES_PER_CHAR

TARGETS: dict[str, tuple[tuple[int, ...], set[int]]] = {
    "AIMBIOS.EDT": ((400, 160), {0, 1}),
    "MERCBIOS.EDT": ((400, 160), {0, 1}),
    "ITEMDESC.EDT": ((80, 80, 240), {2}),
    "BRAYDESC.EDT": ((80, 320), {1}),
    "IMPASS.EDT": ((320,), {0}),
    "IMPTEXT.EDT": ((400,), {0}),
}

LATIN_RE = re.compile(r"[A-Za-z]")
HANGUL_RE = re.compile(r"[\u3131-\u318E\uAC00-\uD7A3]")


def probable_english_fallback(text: str) -> bool:
    text = " ".join(text.split())
    if len(text) < 24 or HANGUL_RE.search(text):
        return False
    latin = len(LATIN_RE.findall(text))
    letters = sum(ch.isalpha() for ch in text)
    return latin >= 12 and letters > 0 and latin / letters >= 0.85


def preview(text: str, limit: int = 150) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    root = repo / "assets/mods/korean-localization/data/BinaryData"
    findings: list[str] = []
    total_fields = 0

    for filename, (layout, checked_columns) in TARGETS.items():
        path = root / filename
        if not path.is_file():
            findings.append(f"MISSING {filename}")
            continue
        stride = sum(layout) * BYTES_PER_CHAR
        data = path.read_bytes()
        if len(data) % stride:
            findings.append(f"STRUCT {filename}: {len(data)} bytes not divisible by {stride}")
            continue
        rows = len(data) // stride
        file_findings = 0
        for row in range(rows):
            cursor = row * stride
            for column, width in enumerate(layout):
                text = decode_field(data, cursor, width)
                if column in checked_columns and text.strip():
                    total_fields += 1
                    if probable_english_fallback(text):
                        findings.append(f"{filename} row={row} col={column}: {preview(text)}")
                        file_findings += 1
                cursor += width * BYTES_PER_CHAR
        print(f"{filename}: rows={rows}, suspicious_english={file_findings}")

    if findings:
        print("\nHigh-confidence Korean translation gaps:", file=sys.stderr)
        for finding in findings[:200]:
            print(f"  {finding}", file=sys.stderr)
        if len(findings) > 200:
            print(f"  ... {len(findings) - 200} more", file=sys.stderr)
        return 1
    print(f"Korean BinaryData translation audit: PASS ({total_fields} meaningful fields checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
