# Korean Localization Plan

## Goal

Add first-class Korean resource support to JA2 Stracciatella while reusing the existing Korean Jagged Alliance 2 translation wherever the original JA2 data format is compatible.

Existing Korean translation source:
- https://github.com/munument1/Jagged-Alliance2-korean

Development branch:
- `korean-localization`

## What can be reused

High-confidence reusable assets from the existing Korean patch:

- `BinaryData/*.EDT`
- `MercEdt/*.EDT`
- `NPCData/*.EDT`
- translated image resources when the Stracciatella resource is identical to the original JA2 asset

Do not directly import JA2 1.13-only resources such as `TableData` extensions, enemy-taunt data, or other features that do not exist in Stracciatella.

## Stracciatella localization architecture

Stracciatella already has a CJK localization precedent through the Simplified Chinese implementation.

Relevant components:

- `VanillaVersion::SIMPLIFIED_CHINESE`
- `assets/mods/simplified-chinese-localization/`
- `assets/externalized/strings/*-chs.json`
- `assets/externalized/translation_tables/translation-table-chs.json`
- STI font resources in the localization mod

The Korean implementation should mirror this architecture with a `KOREAN` resource version and `kor` suffix.

## Implementation phases

### Phase 1 - Engine/resource version

Add `KOREAN` to all resource-version interfaces:

- Rust `VanillaVersion`
- C API string conversion/tests
- CLI help/resource-version parsing
- desktop launcher version list
- Android resource-version list
- content-manager resource suffix handling
- externalized string suffix handling (`-kor`)

Add `isKoreanVersion()` where language-specific vanilla behavior requires the same handling as English/Chinese.

### Phase 2 - Korean localization mod

Use:

`assets/mods/korean-localization/`

Expected structure:

```text
assets/mods/korean-localization/
  manifest.json
  data/
    BinaryData/
    MercEdt/
    npcdata/
    Fonts/
    loadscreens/
```

The launcher should automatically enable `korean-localization` when the resource version is `KOREAN`, matching the existing Simplified Chinese behavior.

### Phase 3 - Font proof of concept

The current font system uses Unicode codepoints mapped to STI glyph indexes through an external translation table.

Create:

- `assets/externalized/translation_tables/translation-table-kor.json`
- a minimal Korean STI font set in `assets/mods/korean-localization/data/Fonts/`

First POC target:

- ASCII
- Korean syllables required by one short test string
- punctuation

Verify Korean display before importing the full translation.

For production, generate the Korean STI fonts and translation table from a deterministic glyph list so every font uses the exact same glyph ordering.

### Phase 4 - Externalized UI strings

Create `*-kor.json` counterparts for localized string resources under:

`assets/externalized/strings/`

Reuse the existing translated built-in/UI strings by matching English source strings or stable indexes. Preserve formatting tokens and array ordering exactly.

### Phase 5 - Original JA2 data import

Import compatible Korean EDT resources into the Korean localization mod only after verifying record layout against Stracciatella/original JA2 expectations.

Priority order:

1. `MercEdt`
2. `NPCData`
3. `BinaryData`
4. localized image resources

Do not blindly copy the entire existing 1.13 Data tree.

### Phase 6 - QA

Smoke-test at least:

- launcher resource selection
- main menu
- new game
- IMP creation
- AIM/MERC laptop pages
- tactical UI
- strategic map
- AIM merc dialogue
- recruitable RPC dialogue
- civilian/NPC dialogue
- save/load

Check specifically for:

- missing glyphs
- invalid character fallback (`?`)
- line wrapping
- clipping/overflow
- broken EDT record boundaries
- untranslated Stracciatella-only strings

## Immediate next milestone

A build that exposes `Korean` in the launcher and renders one Korean test string with a Korean STI font without breaking English resources.
