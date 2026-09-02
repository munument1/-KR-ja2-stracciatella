# Korean localization branch instructions

These instructions are authoritative for work on the `korean-localization` branch.

## Goal

Maintain and test the Korean localization without rebuilding unrelated Stracciatella targets.
Prefer the smallest validation/build path that can prove the current change.

## Known working baseline

The following were already confirmed in actual gameplay before this file was added:

- New Game screen displays Korean correctly.
- Options screen displays Korean correctly.
- A configured New Game can enter the actual game successfully.
- In-game Korean dialogue displays correctly.
- Korean runtime fonts work.

CI baseline:

- `Korean Windows Test Build` run #35 (`33607294939`) completed successfully.
- The successful Windows artifact was built from source commit `d23e3db5222b62037616a0e34eb0003ca7036da1`.
- Artifact name: `JA2-Stracciatella-Korean-Windows-Test`.
- Artifact SHA-256 reported by GitHub: `218f1faa9ae29e4dcac80bab1120b6d2d78caf2e35752ebf6e50744b79782230`.
- Later commits before this instruction file were CI-only and did not change the game source.

## Build decision: do this before any CI work

### 1. Asset-only change: DO NOT rebuild Stracciatella

Treat these as asset-only unless the same commit also changes engine/build source:

- `assets/mods/korean-localization/**`
- `assets/externalized/strings/*-kor.json`
- `assets/externalized/translation_tables/translation-table-kor.json`
- Korean EDT, STI, fonts, menu images, translated JSON, NPCData, MercEdt and BinaryData
- Korean asset-generation/import/audit scripts when they only regenerate the files above

For asset-only work:

1. Run the Korean validation/audit scripts.
2. Generate/rebuild runtime assets only when required.
3. Use `Korean Asset Test Package` to make a lightweight overlay artifact.
4. Do not compile Linux, macOS, Android, or Windows executables.

Important: `mods/korean-localization` alone is sufficient only when the changed files are actually confined to that mod directory. Korean `*-kor.json` strings and `translation-table-kor.json` are packaged under the installed `externalized/` directory, so the lightweight test artifact includes both the mod and the Korean externalized files.

### 2. Engine/build change: build Windows only

A new executable is required when changing runtime/build source such as:

- `src/**`
- `rust/**`
- `.ci/**`
- `cmake/**`
- `CMakeLists.txt`
- build/toolchain metadata that can affect the executable

For those changes, use `Korean Windows Test Build` only. Do not run the upstream Linux/macOS/Android matrix for Korean localization testing.

### 3. Mixed change

If both source and assets change, finish and validate the assets first, then run one Windows test build after the source is stable. Do not rebuild after every asset edit.

## CI policy

- Upstream `GitHub CI` is intentionally skipped for the Korean localization PR/branch because it launches Linux, Linux-mingw64, macOS, Android and lint matrices that are not useful for routine localization work.
- `Korean Asset Test Package` is the normal test path for translation/font/EDT/STI changes.
- `Korean Windows Test Build` is reserved for source/build changes or an explicit manual request for a fresh executable baseline.
- `Build Korean Runtime Assets` may regenerate and commit runtime assets, but must not automatically trigger a full Windows compile merely because generated assets changed.
- Never repeatedly rerun the same failed workflow without first identifying and fixing the exact failing step.

## Korean runtime rules that must not be regressed

- Keep `isKoreanVersion()` and the Korean localization path.
- Keep the `-kor` externalized-string suffix support in `src/externalized/strings/Localization.cc`.
- Do not weaken `Font.cc` invalid-character validation to hide missing mappings.
- Keep U+00B7 (`·`) mapped through the Korean translation table; do not solve it by disabling validation.
- Do not enlarge the Save/Load font again. `SAVE_LOAD_NORMAL_FONT` should remain `FONT12ARIAL` unless a new, demonstrated regression requires a separate fix.
- Do not revert `GameRes.cc`/English-version behavior as a shortcut for Korean support.
- Do not copy whole 1.13 EDT files into vanilla Stracciatella without validating record count/layout/size.

## Translation policy

Korean source priority:

1. Existing Korean JA2 translation when structurally compatible.
2. Translate the current English source directly.
3. Other localizations may be used only for structure/context, never as the Korean translation source.

Intentional English/original text can remain when appropriate, including person names, firearm model names, company/brand names, abbreviations, coordinates, ammunition calibers, URLs and identifiers. Do not translate these blindly just to make an audit number larger.

Always preserve placeholders, tags, escapes and structural keys. Placeholder mismatch and structural mismatch must remain zero.

## Current localization focus

Do not rework already confirmed New Game/Options/game-entry/dialogue behavior unless a regression is reported. Current QA focus is:

- A.I.M. biography and additional-information runtime paths
- A.I.M. equipment/item names
- MERC biographies
- IMP text
- Bobby Ray and general item names/descriptions
- remaining accessible English fallback
- main-menu baked label sizing and Korean font quality

## Working style

Work in short chunks. Each chunk should have one clear target, minimal commits, validation, and a concise report. CI success is not the same as gameplay verification; label it accurately.
