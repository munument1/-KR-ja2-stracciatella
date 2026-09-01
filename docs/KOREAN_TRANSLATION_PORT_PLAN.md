# Korean translation port plan

This is the execution order for moving the existing JA2 1.13 Korean translation into JA2-Stracciatella without importing 1.13-only gameplay data.

## Phase A — Structural coverage

1. Keep one Korean counterpart for every `*-eng.json` externalized string family used by the Korean resource version.
2. Run `tools/korean/audit_translation_coverage.py` after every string change.
3. Treat placeholder, key and array-length mismatches as build blockers.

## Phase B — Reuse the existing Korean corpus

Use the existing `JA2_7609_Korean_Translation_Extracted` corpus as the translation memory. Match by exact English source first, then review ambiguous duplicates by symbol/context.

Priority order for `translation-kor.json`:

1. New Game / options / save-load
2. tactical UI and combat messages
3. strategic map and assignments
4. A.I.M. / M.E.R.C. / IMP
5. Bobby Ray / shipments / dealers
6. laptop/email/files/insurance/florist
7. credits and low-frequency messages

Never change placeholder count or order while importing a translation.

## Phase C — EDT runtime data

### MercEdt

Import files proven vanilla-compatible first. Files with a record-count difference must be rebuilt at record level instead of copied wholesale.

### NPCData

Compare every legacy Korean file against the vanilla resource file by record size/count and profile mapping before copying.

### BinaryData

Prioritize player-visible long-form resources:

- IMP text
- A.I.M. history/policies/alumni
- help
- laptop files
- flower shop text
- credits
- bios and item descriptions

## Phase D — Stracciatella-only text

Translate strings that have no legacy 1.13 equivalent separately. `tooltips-kor.json` is the first completed example.

## Phase E — Runtime sweep

A release candidate must be tested through these screens/paths:

- launcher / main menu
- New Game / game options
- IMP male and female creation
- A.I.M. hire and profile pages
- M.E.R.C.
- Bobby Ray ordering and shipments
- tactical combat and inventory
- strategic map and assignments
- recruitable rebels and normal NPC dialogue
- help / email / files / florist / insurance
- save/load
- end-game/credits

Any English string seen during the sweep must be traced back to its owning resource and added to the audit.
