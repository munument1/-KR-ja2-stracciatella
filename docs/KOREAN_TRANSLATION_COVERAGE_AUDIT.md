# Korean translation coverage audit

This document tracks translation areas that differ between the legacy JA2 1.13 Korean patch and JA2-Stracciatella.

## Current findings

### 1. Externalized Stracciatella strings

Stracciatella stores many strings in `assets/externalized/strings/` instead of the legacy executable/resource layout.

Korean files currently present include:

- `ammo-calibre-kor.json`
- `ammo-calibre-bobbyray-kor.json`
- `new-strings-kor.json`
- `shipping-destinations-kor.json`
- `strategic-map-land-types-kor.json`
- `strategic-map-town-names-kor.json`
- `strategic-map-town-name-locatives-kor.json`
- `translation-kor.json`
- `tooltips-kor.json`

`tooltips-kor.json` is Stracciatella-specific and was added during this audit because the legacy 1.13 patch does not provide a directly reusable equivalent.

### 2. Main UI translation is not yet complete

`translation-kor.json` currently mirrors the English structure and still contains mostly English text. The existing 1.13 Korean translation corpus should be matched against `translation-eng.json` by English source text and then reviewed for context and placeholder compatibility.

Do not treat the mere presence of `translation-kor.json` as completion.

### 3. Mercenary dialogue

The Korean localization mod currently contains only `MercEdt/000.EDT` as a committed runtime dialogue file.

The legacy Korean patch contains many more `MercEdt/*.EDT` files. These must be split into:

- vanilla-compatible files that can be reused directly after record-count validation;
- files whose 1.13 record count differs from vanilla and therefore require record-level reconstruction;
- 1.13-only profiles/files that must not be imported.

Known prior audit result:

- 54 files were identified as size/record-layout compatible with vanilla, including `000.EDT`;
- 16 files require record-level handling: `005`, `032`, `040`, `046`, `051`-`061`, `064`;
- known 1.13-only candidates include `062`, `149`, `165`-`169`, and `snitch/023`;
- Stracciatella-only `200.EDT` currently has no Korean source and should keep English fallback until translated.

### 4. NPC dialogue

The legacy Korean patch contains `Patch/Data/NPCData/*.EDT`, while the current Stracciatella Korean mod has no `NPCData` directory yet.

This is a major untranslated runtime area. Each file must be compared to the vanilla Stracciatella resource layout before import. Do not bulk-copy the 1.13 directory without validating record counts and profile mapping.

### 5. BinaryData text resources

The legacy Korean patch contains translated `BinaryData` EDT resources such as:

- `AIMHIST.EDT`
- `AIMPOL.EDT`
- `ALUMNAME.EDT`
- `ALUMNI.EDT`
- `CREDITS.EDT`
- `FILES.EDT`
- `FLOWERCARD.EDT`
- `FLOWERDESC.EDT`
- `HELP.EDT`
- `IMPASS.EDT`
- `IMPTEXT.EDT`
- and additional binary text resources

These cover web pages, help, IMP text, dossier/history material, flower shop text and other areas that will remain English until ported.

Each file must be checked against vanilla record size/count before reuse.

### 6. 1.13-only content must stay excluded

Do not import 1.13-specific gameplay/configuration data merely because it contains Korean text. Examples include:

- `Data-1.13/TableData`
- `Ja2_Options.INI`
- `Skills_Settings.INI`
- 1.13-specific item/weapon data
- 1.13-only profiles/dialogue additions

The goal is a Korean localization layer for vanilla-compatible Stracciatella, not a partial 1.13 data port.

## Completion criteria

The localization should not be called complete until all of the following are true:

1. Every English externalized string family used by the Korean resource version has a Korean counterpart or an intentional documented fallback.
2. `translation-kor.json` has been matched against the legacy Korean UI corpus and all remaining English entries have been reviewed.
3. Vanilla-compatible `MercEdt` files have been imported and validated.
4. Vanilla-compatible `NPCData` files have been imported and validated.
5. Vanilla-compatible `BinaryData` text resources have been imported and validated.
6. Stracciatella-only strings such as informative tooltips are translated separately.
7. A runtime sweep covers main menu, new game, IMP, A.I.M., M.E.R.C., Bobby Ray, tactical UI, strategic map, NPC dialogue, merc dialogue, help, email/files and end-game/credits paths.

## Safety rule

For all structured strings, preserve placeholder count/order (`%s`, `%d`, etc.), array length and key names. For EDT files, preserve record size/count required by the vanilla resource being replaced.
