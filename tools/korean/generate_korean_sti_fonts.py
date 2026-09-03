#!/usr/bin/env python3
"""Build Korean JA2 Stracciatella STI fonts from the bundled Chinese font set.

The Simplified Chinese localization already solved the hard part of extending JA2's
font format beyond the original 8-bit glyph set. Its font STI files keep 214 common
Latin/European/Cyrillic glyphs at indices 0..213 and append CJK glyphs afterwards.

This tool keeps those first 214 glyphs (including their palette and metrics), drops
the Chinese glyphs, then appends Hangul glyphs rendered from a user-supplied TTF.
It also writes translation-table-kor.json with matching glyph indices.

The script does not redistribute the TTF. Pass a local path to a Korean-capable font
(e.g. the Galmuri font already used by the existing Korean JA2 patch).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import struct
import sys
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - dependency error path
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc


STCI_HEADER_SIZE = 64
STCI_SUBIMAGE_SIZE = 16
STCI_INDEXED = 0x0008
STCI_ETRLE_COMPRESSED = 0x0020
BASE_GLYPH_COUNT = 214
TRANSPARENT_PIXEL = 0
SHADOW_PIXEL = 1
FOREGROUND_PIXEL = 2
RUN_LIMIT = 0x7F

# Unicode punctuation used by Korean strings but absent from the preserved
# 0..213 base glyph set. Alias these to readable ASCII glyphs so the runtime
# never falls back to '?'. Dedicated glyphs can replace these aliases later.
KOREAN_FALLBACK_ALIASES = {
    "~": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "『": '"',
    "』": '"',
}

# Same font set shipped by the Simplified Chinese localization mod.
FONT_FILES = (
    "BLOCKFONT2.sti",
    "BLOCKFONTNARROW.sti",
    "CLOCKFONT.sti",
    "COMPFONT.sti",
    "FONT10ARIAL.sti",
    "FONT10ARIALBOLD.sti",
    "FONT10ROMAN.sti",
    "FONT12ARIAL.sti",
    "FONT12ARIALFIXEDWIDTH.sti",
    "FONT12POINT1.sti",
    "FONT12ROMAN.sti",
    "FONT14ARIAL.sti",
    "FONT14HUMANIST.sti",
    "FONT14SANSERIF.sti",
    "FONT14SANSSERIF.sti",
    "FONT16ARIAL.sti",
    "HUGEFONT.sti",
    "LARGEFONT1.sti",
    "MERCFONT.sti",
    "SMALLCOMPFONT.sti",
    "SMALLFONT1.sti",
    "TINYFONT1.sti",
    "blockfont.sti",
)


@dataclass(frozen=True)
class SubImage:
    data_offset: int
    data_length: int
    offset_x: int
    offset_y: int
    height: int
    width: int

    @classmethod
    def unpack_from(cls, data: bytes, offset: int) -> "SubImage":
        return cls(*struct.unpack_from("<IIhhHH", data, offset))

    def pack(self) -> bytes:
        return struct.pack(
            "<IIhhHH",
            self.data_offset,
            self.data_length,
            self.offset_x,
            self.offset_y,
            self.height,
            self.width,
        )


@dataclass
class StiFile:
    header: bytearray
    palette: bytes
    subimages: list[SubImage]
    pixel_data: bytes

    @classmethod
    def read(cls, path: Path) -> "StiFile":
        raw = path.read_bytes()
        if len(raw) < STCI_HEADER_SIZE or raw[:4] != b"STCI":
            raise ValueError(f"{path}: not an STCI file")

        header = bytearray(raw[:STCI_HEADER_SIZE])
        flags = struct.unpack_from("<I", header, 16)[0]
        if not (flags & STCI_INDEXED) or not (flags & STCI_ETRLE_COMPRESSED):
            raise ValueError(f"{path}: expected indexed ETRLE-compressed STI")

        color_count = struct.unpack_from("<I", header, 24)[0]
        if color_count != 256:
            raise ValueError(f"{path}: expected 256-color STI, got {color_count}")

        subimage_count = struct.unpack_from("<H", header, 28)[0]
        stored_size = struct.unpack_from("<I", header, 8)[0]
        palette_start = STCI_HEADER_SIZE
        palette_end = palette_start + color_count * 3
        sub_start = palette_end
        sub_end = sub_start + subimage_count * STCI_SUBIMAGE_SIZE
        pixel_end = sub_end + stored_size
        if pixel_end > len(raw):
            raise ValueError(f"{path}: truncated STI payload")

        palette = raw[palette_start:palette_end]
        subimages = [
            SubImage.unpack_from(raw, sub_start + i * STCI_SUBIMAGE_SIZE)
            for i in range(subimage_count)
        ]
        pixel_data = raw[sub_end:pixel_end]
        return cls(header, palette, subimages, pixel_data)


def korean_codepoints() -> list[str]:
    # Modern Hangul compatibility jamo commonly used for standalone consonants/vowels.
    chars = [chr(cp) for cp in range(0x3131, 0x3164)]
    # All 11,172 precomposed modern Hangul syllables.
    chars.extend(chr(cp) for cp in range(0xAC00, 0xD7A4))
    return chars


def encode_etrle_row(row: Iterable[int]) -> bytes:
    """Encode one scanline in the ETRLE form used by JA2 STI files."""
    source = list(row)
    out = bytearray()
    i = 0
    while i < len(source):
        transparent = source[i] == TRANSPARENT_PIXEL
        j = i + 1
        while j < len(source) and (source[j] == TRANSPARENT_PIXEL) == transparent and j - i < RUN_LIMIT:
            j += 1
        length = j - i
        if transparent:
            out.append(0x80 | length)
        else:
            out.append(length)
            out.extend(source[i:j])
        i = j
    out.append(0)  # end-of-line marker
    return bytes(out)


def render_hangul_glyph(
    font: ImageFont.FreeTypeFont,
    ch: str,
    target_height: int,
    add_shadow: bool,
) -> tuple[int, int, bytes]:
    canvas_size = max(64, target_height * 2)
    canvas = Image.new("L", (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(canvas)
    draw.text((0, 0), ch, font=font, fill=255)
    bbox = canvas.getbbox()

    if bbox is None:
        raise ValueError(f"font rendered an empty glyph for U+{ord(ch):04X}")

    left, top, right, bottom = bbox
    glyph_width = max(1, right - left)
    glyph_height = max(1, bottom - top)

    advance = max(1, int(math.ceil(font.getlength(ch))))

    width = max(glyph_width, advance) + (1 if add_shadow else 0)

    crop = canvas.crop(bbox)

    mask = Image.new("L", (width, target_height), 0)
    x = max(0, (width - (1 if add_shadow else 0) - glyph_width) // 2)
    y = max(0, (target_height - glyph_height) // 2)
    mask.paste(crop, (x, y))
    pixels = mask.load()

    indexed = [[TRANSPARENT_PIXEL] * width for _ in range(target_height)]
    on_pixels: list[tuple[int, int]] = []
    for yy in range(target_height):
        for xx in range(width):
            if pixels[xx, yy] >= 128:
                on_pixels.append((xx, yy))

    if not on_pixels:
        raise ValueError(f"font rendered an empty glyph for U+{ord(ch):04X}")

    if add_shadow:
        for xx, yy in on_pixels:
            sx, sy = xx + 1, yy + 1
            if sx < width and sy < target_height:
                indexed[sy][sx] = SHADOW_PIXEL

    for xx, yy in on_pixels:
        indexed[yy][xx] = FOREGROUND_PIXEL

    encoded = b"".join(encode_etrle_row(row) for row in indexed)
    return width, target_height, encoded


def fit_font(ttf_path: Path, target_height: int, scale: float) -> ImageFont.FreeTypeFont:
    """Choose the largest pixel size whose representative Hangul glyph fits."""
    start = max(1, int(round(target_height * scale)))
    for size in range(start, 0, -1):
        try:
            font = ImageFont.truetype(str(ttf_path), size=size)
        except (OSError, ValueError):
            continue
        canvas = Image.new("L", (100, 100), 0)
        draw = ImageDraw.Draw(canvas)
        draw.text((0, 0), "한", font=font, fill=255)
        bbox = canvas.getbbox()
        if bbox is not None and (bbox[3] - bbox[1]) <= target_height:
            return font

    for size in (16, 21, 12, 10, 8):
        try:
            font = ImageFont.truetype(str(ttf_path), size=size)
            canvas = Image.new("L", (100, 100), 0)
            draw = ImageDraw.Draw(canvas)
            draw.text((0, 0), "한", font=font, fill=255)
            bbox = canvas.getbbox()
            if bbox is not None and (bbox[3] - bbox[1]) <= target_height:
                return font
        except (OSError, ValueError):
            continue

    # Fallback to returning the specified TTF at its default size
    for default_size in (12, 16, 21):
        try:
            return ImageFont.truetype(str(ttf_path), size=default_size)
        except (OSError, ValueError):
            continue
    raise ValueError(f"could not load TTF {ttf_path}")


def rewrite_font(
    template_path: Path,
    output_path: Path,
    ttf_path: Path,
    chars: list[str],
    scale: float,
    add_shadow: bool,
) -> int:
    sti = StiFile.read(template_path)
    if len(sti.subimages) < BASE_GLYPH_COUNT:
        raise ValueError(
            f"{template_path}: has only {len(sti.subimages)} glyphs; expected at least {BASE_GLYPH_COUNT}"
        )

    base_subimages = sti.subimages[:BASE_GLYPH_COUNT]
    new_subimages: list[SubImage] = []
    new_pixel_data = bytearray()

    # Repack the first 214 common glyphs without changing their pixels or metrics.
    for sub in base_subimages:
        start = sub.data_offset
        end = start + sub.data_length
        payload = sti.pixel_data[start:end]
        if len(payload) != sub.data_length:
            raise ValueError(f"{template_path}: invalid base glyph payload")
        offset = len(new_pixel_data)
        new_pixel_data.extend(payload)
        new_subimages.append(
            SubImage(offset, len(payload), sub.offset_x, sub.offset_y, sub.height, sub.width)
        )

    # JA2 reports line height from glyph 0, so use it as the hard Hangul cell height.
    first = base_subimages[0]
    target_height = max(1, first.height + max(first.offset_y, 0))
    font = fit_font(ttf_path, target_height, scale)

    for ch in chars:
        width, height, payload = render_hangul_glyph(font, ch, target_height, add_shadow)
        offset = len(new_pixel_data)
        new_pixel_data.extend(payload)
        new_subimages.append(SubImage(offset, len(payload), 0, 0, height, width))

    if len(new_subimages) > 0xFFFF:
        raise ValueError(f"too many glyphs for STI: {len(new_subimages)}")

    header = bytearray(sti.header)
    struct.pack_into("<I", header, 4, sum(s.width * s.height for s in new_subimages))
    struct.pack_into("<I", header, 8, len(new_pixel_data))
    struct.pack_into("<H", header, 28, len(new_subimages))
    struct.pack_into("<I", header, 48, 0)  # font STI app-data is not needed

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        f.write(header)
        f.write(sti.palette)
        for sub in new_subimages:
            f.write(sub.pack())
        f.write(new_pixel_data)

    return target_height


def write_translation_table(base_table_path: Path, output_path: Path, chars: list[str]) -> None:
    with base_table_path.open("r", encoding="utf-8") as f:
        source = json.load(f)

    base_pairs = sorted(
        ((ch, int(idx)) for ch, idx in source.items() if int(idx) < BASE_GLYPH_COUNT),
        key=lambda pair: pair[1],
    )
    indices = {idx for _, idx in base_pairs}
    expected = set(range(BASE_GLYPH_COUNT))
    if indices != expected:
        missing = sorted(expected - indices)
        raise ValueError(
            f"base translation table does not cover glyph indices 0..213; missing {missing[:10]}"
        )

    table: dict[str, int] = {}
    for ch, idx in base_pairs:
        table[ch] = idx
    for offset, ch in enumerate(chars):
        table[ch] = BASE_GLYPH_COUNT + offset

    for ch, fallback in KOREAN_FALLBACK_ALIASES.items():
        table[ch] = table[fallback]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
        f.write("\n")


def select_ttf_for_font(ttf_dir: Path, filename: str, target_height: int) -> Path:
    fn_upper = filename.upper()
    if target_height <= 9:
        candidate = ttf_dir / "Galmuri9Bitmap-Regular-2.40.4.ttf"
        if candidate.is_file():
            return candidate
    elif target_height in (10, 11, 12, 13):
        if "COMP" in fn_upper or "NARROW" in fn_upper:
            candidate = ttf_dir / "Galmuri11Bitmap-Condensed-2.40.4.ttf"
            if candidate.is_file():
                return candidate
        candidate = ttf_dir / "Galmuri11Bitmap-Regular-2.40.4.ttf"
        if candidate.is_file():
            return candidate
    elif target_height >= 14:
        candidate = ttf_dir / "Galmuri14Bitmap-Regular-2.40.4.ttf"
        if candidate.is_file():
            return candidate

    # Default fallback
    for fallback_name in (
        "Galmuri11Bitmap-Regular-2.40.4.ttf",
        "Galmuri11Bitmap-Condensed-2.40.4.ttf",
        "Galmuri14Bitmap-Regular-2.40.4.ttf",
        "Galmuri9Bitmap-Regular-2.40.4.ttf",
    ):
        cand = ttf_dir / fallback_name
        if cand.is_file():
            return cand
    raise FileNotFoundError(f"No suitable Galmuri TTF found in {ttf_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=Path("assets/mods/simplified-chinese-localization/data/Fonts"),
        help="directory containing the Simplified Chinese localization STI fonts",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("assets/mods/korean-localization/data/Fonts"),
        help="output directory for Korean STI fonts",
    )
    parser.add_argument(
        "--base-table",
        type=Path,
        default=Path("assets/externalized/translation_tables/translation-table-chs.json"),
        help="Chinese translation table used to preserve the common 0..213 glyph mapping",
    )
    parser.add_argument(
        "--output-table",
        type=Path,
        default=Path("assets/externalized/translation_tables/translation-table-kor.json"),
        help="output Korean translation table",
    )
    parser.add_argument("--ttf", type=Path, default=None, help="local Korean-capable TTF font")
    parser.add_argument(
        "--ttf-dir",
        type=Path,
        default=None,
        help="directory containing Galmuri TTF fonts (Galmuri9, Galmuri11, Galmuri14)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="initial TTF pixel-size multiplier relative to each JA2 font height (default: 1.0)",
    )
    parser.add_argument(
        "--no-shadow",
        action="store_true",
        help="do not add JA2 source-pixel shadow (palette index 1) behind Hangul glyphs",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="optional subset of STI filenames to generate",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.ttf and not args.ttf_dir:
        raise SystemExit("Must specify either --ttf or --ttf-dir")
    if args.ttf and not args.ttf.is_file():
        raise SystemExit(f"TTF not found: {args.ttf}")
    if args.ttf_dir and not args.ttf_dir.is_dir():
        raise SystemExit(f"TTF directory not found: {args.ttf_dir}")
    if args.scale <= 0:
        raise SystemExit("--scale must be greater than zero")

    chars = korean_codepoints()
    font_files = tuple(args.only) if args.only else FONT_FILES

    print(f"Hangul glyphs to append: {len(chars)}")
    for filename in font_files:
        template = args.template_dir / filename
        if not template.is_file():
            raise SystemExit(f"template STI not found: {template}")

        # Determine target height first to select appropriate TTF if using --ttf-dir
        sti_temp = StiFile.read(template)
        first_sub = sti_temp.subimages[0]
        target_height = max(1, first_sub.height + max(first_sub.offset_y, 0))

        if args.ttf_dir:
            ttf_path = select_ttf_for_font(args.ttf_dir, filename, target_height)
        else:
            ttf_path = args.ttf

        output = args.output_dir / filename
        height = rewrite_font(
            template,
            output,
            ttf_path,
            chars,
            args.scale,
            add_shadow=not args.no_shadow,
        )
        print(
            f"{filename:28s}: generated {BASE_GLYPH_COUNT + len(chars)} glyphs "
            f"(height {height}px using {ttf_path.name})"
        )

    write_translation_table(args.base_table, args.output_table, chars)
    print(f"translation table: {args.output_table}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
