# Korean localization branch instructions

These instructions are authoritative for work on the `korean-localization` branch.

## Project goal

The primary deliverable is a **Korean localization mod for JA2 Stracciatella**, not a separately maintained Korean executable.

The final test/distribution artifact should contain one top-level folder:

- `korean-localization/`

The repository may keep source assets in their upstream-style locations for maintainability. Packaging combines them into that one mod folder:

- `assets/mods/korean-localization/**` -> `korean-localization/**`
- `assets/externalized/strings/*-kor.json` -> `korean-localization/data/strings/`
- `assets/externalized/translation_tables/translation-table-kor.json` -> `korean-localization/data/translation_tables/`

Do not refactor these source locations merely to make the repository itself look like the final ZIP. Keep the build/package path simple instead.

## Known working gameplay baseline

Already confirmed by actual gameplay:

- New Game screen displays Korean correctly.
- Options screen displays Korean correctly.
- A configured New Game can enter the actual game successfully.
- In-game Korean dialogue displays correctly.
- Korean runtime fonts work.

Do not rework these areas unless a regression is reported.

## Build policy

### Asset/translation work: no executable build

For changes limited to Korean localization data, including:

- translated `*-kor.json`
- EDT dialogue/text
- NPCData / MercEdt / BinaryData
- Korean fonts and STI images
- `translation-table-kor.json`
- localization asset-generation or audit scripts

use validation plus `Korean Asset Test Package` only.

**Do not compile Windows, Linux, macOS or Android executables for routine localization changes.**

The lightweight package workflow must produce the single-folder artifact `JA2-Stracciatella-Korean-Localization-Mod` and contain no executable.

### Engine changes: exceptional and minimal

The official engine already contains hard-coded resource-version support for languages such as Simplified Chinese. Korean likewise needs minimal engine support until it is accepted upstream, such as:

- `VanillaVersion::KOREAN`
- Korean resource-version selection
- `-kor` externalized-string suffix
- only genuinely Korean-specific runtime behavior that cannot be represented by mod data

Do not modify the engine to solve translation, AIM/MERC/IMP text, items, EDT, fonts, images or other problems that can be solved in the localization mod.

If an engine change is genuinely required, build **Windows only**, once after the source change is stable. Do not run the upstream Linux/macOS/Android matrix for this branch.

Do not reuse or hijack the Simplified Chinese resource version for Korean.

## CI policy

- Upstream `GitHub CI` is intentionally skipped for the Korean localization PR/branch.
- `Korean Asset Test Package` is the normal path for current work.
- `Korean Windows Test Build` is only for genuine engine/build-source changes or an explicit request for a fresh executable baseline.
- `Build Korean Runtime Assets` may regenerate assets but must not trigger a full executable build just because assets changed.
- Never rerun the same failed workflow repeatedly without identifying the exact failure first.

## Runtime rules that must not regress

- Keep the existing Korean resource-version path while upstream support is pending.
- Keep `-kor` externalized-string suffix support.
- Do not weaken `Font.cc` invalid-character validation.
- Keep U+00B7 (`·`) mapped in the Korean translation table.
- Do not enlarge the Save/Load font again; `SAVE_LOAD_NORMAL_FONT` should remain `FONT12ARIAL` unless a demonstrated regression requires a separate fix.
- Do not copy whole JA2 1.13 EDT files into vanilla Stracciatella without validating record count, layout and size.

## Translation policy

Source priority:

1. Existing Korean JA2 translation when structurally compatible.
2. Translate current English source directly.
3. Other localizations are structure/context references only.

Intentional originals may remain for person names, firearm model names, brands, abbreviations, coordinates, ammunition calibers, URLs and identifiers.

Always preserve placeholders, tags, escapes and structural keys. Placeholder mismatch and structural mismatch must remain zero.

## Current localization focus

Current QA/content priorities are:

- A.I.M. biography and additional information
- A.I.M. equipment/item names
- MERC biographies
- IMP text
- Bobby Ray and general item names/descriptions
- remaining accessible English fallback
- main-menu baked label sizing and Korean font quality

A.I.M. biography/additional information and item names are data-driven (`AIMBIOS.EDT`, `ITEMDESC.EDT` / `BRAYDESC.EDT`), so treat them as mod-data work unless evidence proves otherwise.

## Working style

Work in short chunks with one clear target, minimal changed files, validation, and a concise report. CI success is not gameplay verification; label it accurately.
