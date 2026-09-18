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

### OI-04 · opened 2026-09-17
`MultipleSuns` (D04): 1.1.0 unbinds panels when a sun is demolished and never re-tests the other sun. Fix or document?
- 1.1.0's new `ArtificialSunBase:Done` clears every panel bound to the removed sun without checking another.
- With two overlapping suns, demolishing one leaves panels dark until the next load, when the module relinks them.
- (a) add a `Done`-side relink mirroring the load sweep; (b) document it; (c) leave it for launch day.
- Recommended: (b), the same shape as D01's parked-rocket limit you accepted on 2026-07-30.
- Desk-read only. Falsifier: two overlapping suns, demolish one; if the survivor's panels stay lit, nothing to decide.
Home: `docs/agent/bugs/D04.md`, `docs/agent/reports/MODULE_REVALIDATION_1_1_0.md`

### OI-03 · opened 2026-09-17
`ResidencyControl` (D03): its tourist exemption is dead on 1.1.0. Repair it, or accept that tourists are refused?
- `ChooseDome` now takes the colonist, not a traits table, so the module's Tourist guard is always false.
- Closed domes now refuse tourists too, while the row's rollover still says Tourists are unaffected.
- (a) repair the guard, one line; (b) accept it and reword the rollover; (c) leave it for launch day.
- Recommended: (a); the exemption was a deliberate call (hotel rooms are not residency). A frozen-module edit.
- Desk-read only. Falsifier: close a dome and land a Tourist it is the only choice for; if they check in, this is wrong.
Home: `docs/agent/bugs/D03.md`, `docs/agent/reports/MODULE_REVALIDATION_1_1_0.md`

### OI-01 · opened 2026-09-17
`ClassicRockets` (D01) is overtaken by 1.1.0 and now points the other way. Retire it, narrow it, or leave it?
- 1.1.0 refuels a player rocket parked with no destination, which was the module's whole feature.
- What it still reaches is Trade, TradePad and Rival rockets, which 1.1.0 excludes on purpose.
- (a) retire it, D01 stays the record; (b) add a guard so it never fires on 1.1.0; (c) leave it as it is.
- Recommended: (a). A removed toggle's leftover Mod Options key is inert (revalidation report §10.1).
- Desk-read only, and off by default. Falsifier: with it on, park a player rocket, then a Trade rocket.
Home: `docs/agent/bugs/D01.md`, `docs/agent/reports/MODULE_REVALIDATION_1_1_0.md`

## Run

### OI-12 · opened 2026-09-18 · launch
When this mod heads for upload, make its preview art: `tools/upload_preflight.py` FAILs only on that.
- Paradox rejects a mod with no `image` / `preview.png` before packing.
- Limits: at most 1 MB for Steam, 2 MB for Paradox.
Home: `docs/agent/WORKFLOW.md`
