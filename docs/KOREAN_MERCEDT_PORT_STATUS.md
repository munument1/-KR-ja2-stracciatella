# Korean MercEdt port status

This document tracks the first-pass structural comparison between the legacy JA2 1.13 Korean `MercEdt` files and the MercEdt set bundled with Stracciatella's Simplified Chinese localization, which is used here only as a vanilla/Stracciatella record-count reference.

The legacy source is `munument1/Jagged-Alliance2-korean/Patch/Data/MercEdt`.
The target is `assets/mods/korean-localization/data/MercEdt`.

## Safe first-pass imports

MercEdt records are 480 bytes each. A file is considered safe for direct first-pass import only when:

1. the filename exists in both the legacy Korean set and the Stracciatella reference set;
2. the legacy file size is a multiple of 480 bytes; and
3. the legacy and reference file sizes are identical.

There are **54 direct-import candidates including `000.EDT`**. `000.EDT` is already present in the Korean localization mod, leaving **53 additional files** for the safe import pass.

Matching files:

- `000`-`004`
- `006`-`031`
- `033`-`039`
- `041`-`045`
- `047`-`050`
- `063`
- `066`-`070`
- `072`

Use `tools/korean/import_legacy_edt.py` to copy and SHA-256 verify these files in a local checkout.

## Record-count mismatches

These files exist in both sets but must **not** be copied wholesale until their quote-slot mapping is checked.

| File | Legacy Korean | Vanilla reference | Difference |
| --- | ---: | ---: | ---: |
| `005.EDT` | 118 records | 117 records | +1 |
| `032.EDT` | 143 | 117 | +26 |
| `040.EDT` | 79 | 115 | -36 |
| `046.EDT` | 79 | 115 | -36 |
| `051.EDT` | 120 | 115 | +5 |
| `052.EDT` | 120 | 115 | +5 |
| `053.EDT` | 120 | 115 | +5 |
| `054.EDT` | 120 | 115 | +5 |
| `055.EDT` | 120 | 115 | +5 |
| `056.EDT` | 120 | 115 | +5 |
| `057.EDT` | 120 | 80 | +40 |
| `058.EDT` | 120 | 80 | +40 |
| `059.EDT` | 120 | 80 | +40 |
| `060.EDT` | 120 | 80 | +40 |
| `061.EDT` | 120 | 80 | +40 |
| `064.EDT` | 143 | 80 | +63 |

A positive difference is consistent with additional 1.13 quote slots, but this alone does not prove that all extra records were merely appended. Quote IDs must be validated before truncating.

`040.EDT` and `046.EDT` are especially important: the legacy Korean files contain fewer records than the vanilla reference, so they require reconstruction with vanilla fallback records rather than truncation.

## Legacy-only files excluded from the vanilla port

The following legacy files do not have a matching file in the Stracciatella reference set and are excluded from the initial vanilla localization port:

- `062.EDT`
- `149.EDT`
- `165.EDT`-`169.EDT`
- `snitch/023.edt`

These are treated as 1.13-specific until proven otherwise.

## Reference-only file

The Stracciatella reference set contains `200.EDT`, while the legacy Korean source does not. Do not fabricate a Korean version; allow the vanilla resource to provide the fallback until a verified translation source exists.

## Next step

1. Run the safe importer locally and commit the 53 additional matching EDT files.
2. Runtime-test several imported merc profiles using a clean vanilla JA2 game directory.
3. Build a record-aware conversion path for the 16 mismatched files, using vanilla records as fallback where necessary.
