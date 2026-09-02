#!/usr/bin/env python3
"""Generate Korean main-menu TITLETEXT.STI from the bundled Chinese template.

The title-text STI contains 20 ETRLE-compressed subimages. MainMenuScreen uses
frames 0..16 for the five menu buttons; frames 17..19 are preserved byte-for-byte
from the template. The generator keeps frame geometry/palette and replaces only
the baked text in the runtime-used frames with Korean labels.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import struct

from PIL import Image, ImageDraw, ImageFont

STCI_HEADER_SIZE = 64
SUBIMAGE_SIZE = 16
TRANSPARENT = 0
RUN_LIMIT = 0x7F
EXPECTED_FRAME_COUNT = 20

FRAME_LABELS = {
    0: "새 게임", 1: "새 게임", 2: "새 게임",
    3: "불러오기", 4: "불러오기", 5: "불러오기", 6: "불러오기",
    7: "설정", 8: "설정", 9: "설정",
    10: "제작진", 11: "제작진", 12: "제작진", 13: "제작진",
    14: "종료", 15: "종료", 16: "종료",
}


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


def decode_etrle(payload: bytes, width: int, height: int) -> list[list[int]]:
    rows: list[list[int]] = []
    pos = 0
    for _ in range(height):
        row: list[int] = []
        while True:
            if pos >= len(payload):
                raise ValueError("truncated ETRLE payload")
            control = payload[pos]
            pos += 1
            if control == 0:
                break
            if control & 0x80:
                row.extend([TRANSPARENT] * (control & 0x7F))
            else:
                count = control
                if pos + count > len(payload):
                    raise ValueError("truncated ETRLE literal run")
                row.extend(payload[pos:pos + count])
                pos += count
        if len(row) != width:
            raise ValueError(f"decoded row width {len(row)} != expected {width}")
        rows.append(row)
    return rows


def encode_row(row: list[int]) -> bytes:
    out = bytearray()
    i = 0
    while i < len(row):
        transparent = row[i] == TRANSPARENT
        j = i + 1
        while (
            j < len(row)
            and (row[j] == TRANSPARENT) == transparent
            and j - i < RUN_LIMIT
        ):
            j += 1
        count = j - i
        if transparent:
            out.append(0x80 | count)
        else:
            out.append(count)
            out.extend(row[i:j])
        i = j
    out.append(0)
    return bytes(out)


def luma(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def choose_frame_colors(
    rows: list[list[int]], palette: bytes
) -> tuple[int, int | None]:
    used = sorted({px for row in rows for px in row if px != TRANSPARENT})
    if not used:
        return 1, None

    def rgb(idx: int) -> tuple[int, int, int]:
        off = idx * 3
        vals = palette[off : off + 3]
        return vals[0], vals[1], vals[2]

    foreground = max(used, key=lambda idx: luma(rgb(idx)))
    darker = [idx for idx in used if idx != foreground]
    shadow = min(darker, key=lambda idx: luma(rgb(idx))) if darker else None
    return foreground, shadow


def fit_font(
    ttf: Path, text: str, max_width: int, max_height: int
) -> ImageFont.FreeTypeFont:
    """Load the largest native bitmap strike that actually fits the frame.

    Galmuri Bitmap TTFs expose discrete strike sizes. Pillow raises
    OSError("invalid pixel size") for sizes that are not present. TITLETEXT frames
    are only about 22 pixels tall, but Galmuri14's loadable strike can be 21px,
    so probing only max_height..6 misses it after the frame padding is removed.
    Probe a wider range and judge the rendered bounding box instead.
    """
    supported: list[int] = []
    candidates = list(range(max(32, max_height * 2), 5, -1))
    for fallback in (32, 28, 24, 21, 20, 18, 16, 14, 12, 11, 10, 9, 8):
        if fallback not in candidates:
            candidates.append(fallback)

    for size in candidates:
        try:
            font = ImageFont.truetype(str(ttf), size=size)
        except (OSError, ValueError):
            continue
        supported.append(size)
        box = font.getbbox(text)
        if box[2] - box[0] <= max_width and box[3] - box[1] <= max_height:
            return font

    raise ValueError(
        f"cannot fit {text!r} into {max_width}x{max_height}; "
        f"supported bitmap sizes tried: {supported}"
    )


def render_label(
    text: str,
    width: int,
    height: int,
    foreground: int,
    shadow: int | None,
    ttf: Path,
) -> list[list[int]]:
    font = fit_font(ttf, text, max(1, width - 4), max(1, height - 2))
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    box = draw.textbbox((0, 0), text, font=font)
    text_w = box[2] - box[0]
    text_h = box[3] - box[1]
    x = (width - text_w) // 2 - box[0]
    y = (height - text_h) // 2 - box[1]
    draw.text((x, y), text, font=font, fill=255)

    pix = mask.load()
    rows = [[TRANSPARENT] * width for _ in range(height)]
    on: list[tuple[int, int]] = []
    for yy in range(height):
        for xx in range(width):
            if pix[xx, yy] >= 128:
                on.append((xx, yy))

    if shadow is not None:
        for xx, yy in on:
            sx, sy = xx + 1, yy + 1
            if sx < width and sy < height:
                rows[sy][sx] = shadow
    for xx, yy in on:
        rows[yy][xx] = foreground
    return rows


def generate(template: Path, output: Path, ttf: Path) -> None:
    raw = template.read_bytes()
    if len(raw) < STCI_HEADER_SIZE or raw[:4] != b"STCI":
        raise ValueError(f"{template}: not an STCI file")

    header = bytearray(raw[:STCI_HEADER_SIZE])
    flags = struct.unpack_from("<I", header, 16)[0]
    if not (flags & 0x0008) or not (flags & 0x0020):
        raise ValueError("TITLETEXT template must be indexed ETRLE STI")

    color_count = struct.unpack_from("<I", header, 24)[0]
    sub_count = struct.unpack_from("<H", header, 28)[0]
    stored_size = struct.unpack_from("<I", header, 8)[0]
    if color_count != 256:
        raise ValueError(f"expected 256 colors, got {color_count}")
    if sub_count != EXPECTED_FRAME_COUNT:
        raise ValueError(
            f"expected {EXPECTED_FRAME_COUNT} TITLETEXT frames, got {sub_count}"
        )

    palette_start = STCI_HEADER_SIZE
    palette_end = palette_start + color_count * 3
    sub_start = palette_end
    sub_end = sub_start + sub_count * SUBIMAGE_SIZE
    pixel_end = sub_end + stored_size
    if pixel_end > len(raw):
        raise ValueError("truncated TITLETEXT template")

    palette = raw[palette_start:palette_end]
    subs = [
        SubImage.unpack_from(raw, sub_start + i * SUBIMAGE_SIZE)
        for i in range(sub_count)
    ]
    old_pixels = raw[sub_end:pixel_end]
    trailing = raw[pixel_end:]

    new_pixels = bytearray()
    new_subs: list[SubImage] = []
    for index, sub in enumerate(subs):
        payload = old_pixels[sub.data_offset : sub.data_offset + sub.data_length]
        if len(payload) != sub.data_length:
            raise ValueError(f"frame {index}: truncated payload")

        if index in FRAME_LABELS:
            old_rows = decode_etrle(payload, sub.width, sub.height)
            fg, shadow = choose_frame_colors(old_rows, palette)
            rows = render_label(
                FRAME_LABELS[index], sub.width, sub.height, fg, shadow, ttf
            )
            encoded = b"".join(encode_row(row) for row in rows)
        else:
            encoded = payload

        offset = len(new_pixels)
        new_pixels.extend(encoded)
        new_subs.append(
            SubImage(
                offset,
                len(encoded),
                sub.offset_x,
                sub.offset_y,
                sub.height,
                sub.width,
            )
        )

    struct.pack_into("<I", header, 4, sum(s.width * s.height for s in new_subs))
    struct.pack_into("<I", header, 8, len(new_pixels))
    struct.pack_into("<H", header, 28, len(new_subs))

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as f:
        f.write(header)
        f.write(palette)
        for sub in new_subs:
            f.write(sub.pack())
        f.write(new_pixels)
        f.write(trailing)

    check = output.read_bytes()
    if check[:4] != b"STCI":
        raise ValueError("generated TITLETEXT has invalid magic")
    print(
        f"Generated {output} ({len(check)} bytes, {len(new_subs)} frames; localized 0..16)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(
            "assets/mods/simplified-chinese-localization/data/loadscreens/TITLETEXT.STI"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("assets/mods/korean-localization/data/Loadscreens/titletext.sti"),
    )
    parser.add_argument("--ttf", type=Path, required=True)
    args = parser.parse_args()
    generate(args.template, args.output, args.ttf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
