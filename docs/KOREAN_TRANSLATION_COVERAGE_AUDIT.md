# Korean translation coverage audit

This document tracks translation areas that differ between the legacy JA2 1.13 Korean patch and JA2-Stracciatella.

## Measured externalized-string snapshot

The automated coverage audit passed structurally with the following measured result:

- Korean string families missing: **0**
- translatable externalized strings: **2,118**
- strings changed from English: **199**
- strings still identical to English: **1,919**
- placeholder mismatches: **0**
- structural mismatches: **0**

Per family:

| Family | Changed / total | Still English-identical |
| --- | ---: | ---: |
| `ammo-calibre-bobbyray` | 4 / 17 | 13 |
| `ammo-calibre` | 4 / 17 | 13 |
| `new-strings` | 5 / 5 | 0 |
| `shipping-destinations` | 17 / 17 | 0 |
| `strategic-map-land-types` | 39 / 39 | 0 |
| `strategic-map-town-name-locatives` | 12 / 12 | 0 |
| `strategic-map-town-names` | 12 / 12 | 0 |
| `tooltips` | 105 / 109 | 4 |
| `translation` | 1 / 1,890 | 1,889 |

The dominant remaining externalized UI task is therefore `translation-kor.json`.

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

`translation-kor.json` currently mirrors the English structure and still contains mostly English text. The measured audit found only **1 of 1,890** translatable entries changed from English. The existing 1.13 Korean UI corpus should be matched against `translation-eng.json` by English source text and then reviewed for context and placeholder compatibility.

Do not treat the mere presence of `translation-kor.json` as completion.

### 3. Mercenary dialogue

The Korean localization mod now contains **54 vanilla-compatible `MercEdt/*.EDT` files**, including `000.EDT`. They were imported only when the legacy Korean file exactly matched the Stracciatella vanilla reference size and were verified as 480-byte-record aligned before commit.

Files not proven compatible remain excluded from the runtime mod.

Known audit result:

- 54 files are size/record-layout compatible with vanilla and are now imported;
- 16 files require record-level handling: `005`, `032`, `040`, `046`, `051`-`061`, `064`;
- known 1.13-only candidates include `062`, `149`, `165`-`169`, and `snitch/023`;
- Stracciatella-only `200.EDT` currently has no Korean source and should keep English fallback until translated.

### 4. NPC dialogue

The legacy Korean patch contains `Patch/Data/NPCData/*.EDT`. A safe importer now compares these only against Stracciatella's bundled vanilla localization reference by filename and exact byte size. `Patch/Data-1.13/NpcData` is never used.

Only exact-layout matches may be committed. Size mismatches remain excluded for record-level review.

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

A safe importer now compares only `Patch/Data/BinaryData` against the Stracciatella vanilla reference by filename and exact byte size. `Patch/Data-1.13/BinaryData` is never used.

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
