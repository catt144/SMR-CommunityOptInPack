# Playtest checklist — the owner's list

## Must_Read_Header
<!-- RULES -->
Rule: Admit an item only when its next action is the owner's: a ruling in words, or a test only the owner can run. [A3: pass]
Rule: Write each item as `### OI-<n> · opened <date>`, its ask, at most six bullet lines and a `Home:` line. [A3: pass]
Rule: Never change an item's opened date; at 30 days old it is purged or archived, however recently it was touched, unless its heading ends ` · launch`, which marks a launch obligation. [A3: pass]
Rule: Delete an item in the commit that records the owner's action on it. [A3: pass]
<!-- /RULES -->

What waits on your word or your hands for the opt-in mod, and nothing else. doccheck enforces the
format and the age. Ids are `OI-<n>` so they never collide with the fix pack's `ck<n>`; what binds
the fix pack goes on its own checklist. A launch obligation waits for this mod's launch, which is
unscheduled, so it does not age.

## Decide

### OI-21 · opened 2026-09-19 · launch
When this mod publishes, do its store tools come from the fix pack or get ported here?
- `paradox_card.py` and `store_screenshots.py` are declared not ported; this mod is unpublished (`metadata.lua` v0).
- The fix pack holds this mod's listing drafts: `RELEASE_DESCRIPTION_OPTIN.md`, `STORE_OPTIN.md`,
  and the opt-in strings in `STORE_METADATA_STRINGS.md`; recheck all at launch.
- Say "run from the fix pack" or "port at launch".
Home: `docs/agent/prompts/RELEASE_SYSTEM_high.md`

### OI-14 · opened 2026-09-18 · launch
Does your 2026-08-02 ruling that the fix pack ships its own `ModItemLocTable` translations extend to this mod?
- This mod's `Code/` has 10 `Untranslated(` sites: rollover titles, policy rows, the stand-down dialog.
- `FUTURE_IDEAS.md` #4(b) hangs on the answer.
- Say "both", "fix pack only", or "decide at its launch".
Home: `docs/agent/FIX_POLICY.md`

### OI-13 · opened 2026-09-18 · launch
May an agent sweep four `Code/` comments that still call this mod "the pack", comments only?
- `00_Core.lua:497`, `:536`, `:558` and `Opt_ResidencyControl.lua:63`, re-read on 2026-09-18.
- Zero behaviour change and a parse sweep after, but it edits module files, so it is yours.
- Say "sweep" or "leave as history".
Home: `docs/agent/WORKFLOW.md`

### OI-11 · opened 2026-09-18 · launch
Name `Opt_MultipleSuns`'s `SolarPanelBase.GameInit` capture in its `Require` block, or leave it allowlisted?
- The F107 wrap check allowlists it: the class declares the method, so `prev` is real and nothing is broken.
- Naming it is a code edit to a frozen module and needs an A/B. D06's two sites left with that module.
- (a) leave it until the file's next planned edit — OI-04 (a) would be one; (b) do it at the launch session.
- Recommended: (a).
Home: `docs/agent/FIX_POLICY.md`, `docs/agent/bugs/D04.md`

## Run

### OI-38 · opened 2026-10-01
When you next sit on the depot's final build, run brief 27's steps that 2026-10-01 left out.
- E3-E5: salvage a half with cargo aboard, then place a new twin (the survivor rule).
- C4: the cabin art at normal speed on both cores.
- D5: toggling Drone Access on one half leaves the twin's button unchanged.
- The scripted up-leg read (slot 6 then slot 2 with an Export row); today's up legs rest on your words.
- The long-title fix (`1122115`) and the hub tooltips' power icon, once brief 28's editor save lands.
Home: `docs/agent/reports/ELEVATOR_DEPOT_WIRING_20261001.md`

### OI-12 · opened 2026-09-18 · launch
When this mod heads for upload, make its preview art: `tools/upload_preflight.py` FAILs only on that.
- Paradox rejects a mod with no `image` / `preview.png` before packing.
- Limits: at most 1 MB for Steam, 2 MB for Paradox.
Home: `docs/agent/WORKFLOW.md`
