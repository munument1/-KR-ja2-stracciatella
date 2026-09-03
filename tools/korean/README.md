# Korean font generation

JA2 Stracciatella renders in-game text with indexed ETRLE-compressed STI font files. The bundled Simplified Chinese localization already contains an extended font set that supports 16-bit glyph indices.

`generate_korean_sti_fonts.py` uses those Chinese STI files as templates:

1. Preserve glyph indices `0..213` unchanged. These are the common Latin, European and Cyrillic glyphs used by Stracciatella.
2. Remove the Chinese glyphs that start at index `214`.
3. Render Korean glyphs from a local Korean-capable TTF.
4. Append 51 Hangul compatibility jamo and all 11,172 modern precomposed Hangul syllables.
5. Write matching Korean STI files and `translation-table-kor.json`.

The final Korean mapping contains 11,437 glyphs (`214 + 51 + 11,172`).

## Requirements

- Python 3.10 or newer
- Pillow
- A local Korean-capable TTF

Install Pillow:

```bash
python -m pip install Pillow
```

The TTF is intentionally not copied into this repository by the generator. Point the tool at a font installed or stored locally. The existing Korean JA2 project uses Galmuri bitmap TTF files and is a suitable source when working in a local checkout that already contains them.

## Generate the complete font set

Run from the repository root:

```bash
python tools/korean/generate_korean_sti_fonts.py \
  --ttf /path/to/korean-font.ttf
```

Outputs:

```text
assets/mods/korean-localization/data/Fonts/*.sti
assets/externalized/translation_tables/translation-table-kor.json
```

The script uses these source templates by default:

```text
assets/mods/simplified-chinese-localization/data/Fonts/*.sti
assets/externalized/translation_tables/translation-table-chs.json
```

## Generate one font for a smoke test

Use `--only` to reduce turnaround time while testing:

```bash
python tools/korean/generate_korean_sti_fonts.py \
  --ttf /path/to/korean-font.ttf \
  --only SMALLFONT1.sti
```

`--scale` adjusts the initial TTF pixel size relative to the original JA2 font height. The generator automatically decreases the size until a representative Hangul syllable fits.

```bash
python tools/korean/generate_korean_sti_fonts.py \
  --ttf /path/to/korean-font.ttf \
  --scale 0.9 \
  --only SMALLFONT1.sti
```

The default output adds a one-pixel JA2-style shadow using source palette index `1`; glyph foreground uses index `2`, and transparent pixels use index `0`. `--no-shadow` disables the generated source shadow.

## Current integration status

The `KOREAN` resource version is registered in the Rust configuration, CLI, Android configuration and desktop launcher. Selecting Korean also enables the `korean-localization` mod.

Until the generated Korean font set and translated Stracciatella string files are committed, Korean intentionally boots using English vanilla resource behavior. This allows engine work and translation asset porting to proceed without making the branch unbootable.

After the Korean STI files and translation table have been validated in-game, the next integration step is to switch the Korean resource version from the English translation-table fallback to `translation-table-kor.json` and begin adding `-kor` externalized strings.
