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
- Recommended: port here; both donor tools currently select fix-pack inputs from their own paths.
Home: `docs/agent/prompts/RELEASE_SYSTEM_high.md`

### OI-14 · opened 2026-09-18 · launch
Does your 2026-08-02 ruling that the fix pack ships its own `ModItemLocTable` translations extend to this mod?
- Apply the answer to the shipping strings, including the train modules; the pre-train inventory is out of date.
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
- The freeze was lifted on 2026-09-18; this remains a code-change decision and still needs an A/B.
- (a) leave it until the file's next planned edit; (b) do it at the launch session. OI-04's edit has since landed.
- Recommended: (a).
Home: `docs/agent/FIX_POLICY.md`, `docs/agent/bugs/D04.md`

### OI-43 · opened 2026-10-02 · launch
Should this mod warn when a player loads a save with it disabled or missing?
- Recommended: set `optional_mod` to false before first publication; built hubs and depots need the uninstall steps.
- Keeping true suppresses the warning for everyone, including players with placed content.
- False restores the engine warning for new saves, even if no content was built; it does not repair a save.
- Existing saves marked optional need loading and saving with the changed mod enabled before that warning can help.
- Say "warn" or "keep optional". A content-dependent warning would need a separate design.
Home: `docs/agent/reports/LAUNCH_PREP_AUDIT_20261002.md`, `docs/agent/prompts/Launch_Prep/01_SHIP_EVIDENCE_high.md`

### OI-44 · opened 2026-10-02 · launch
Are there already Opt-In listings to use? What console approval steps does your Paradox account offer?
- Recommended: use existing Opt-In drafts if any; otherwise create listings at first upload, Paradox then Steam.
- Give existing links only if they exist; newly assigned ids will be read from the editor's writeback.
- Confirm platform choices and any Xbox/PlayStation approval step for this mod; fix-pack approval is not its receipt.
- Login, any required Workshop agreement and actual approval are yours; no account secrets are needed in the repo.
Home: `docs/agent/prompts/RELEASE_SYSTEM_high.md`, `docs/agent/reports/LAUNCH_PREP_AUDIT_20261002.md`

### OI-45 · opened 2026-10-03 · launch
At launch, accept demolish-first removal, or require recovery for saves with hubs/depots still standing?
- Recommended: retain the demolish-first limitation and explicit disclosure; assess residual references in launch prep.
- Removing the mod with its buildings standing raised five native Lua errors in the 2026-10-03 sitting.
- The separate content-free B2 request-restoration check passed; class-reference warnings remain for investigation.
- This is a launch-prep choice, not a gate on the passed train battery (owner `ddf14cc`).
- Say "demolish first" or "require recovery work"; OI-43 separately covers the missing-mod warning.
Home: `docs/agent/reports/TRAIN_FINAL_BATTERY_20261002.md`, `docs/agent/prompts/Launch_Prep/01_SHIP_EVIDENCE_high.md`

## Run

### OI-12 · opened 2026-09-18 · launch
When this mod heads for upload, choose its preview art and the gameplay screenshots for its store pages.
- The launch-prep worker prepares concrete preview candidates and a gallery proposal for your selection.
- Preflight failed only on preview at audit HEAD `63424af` (2026-10-02); no gallery is declared yet.
- Paradox rejects a mod with no `image` / `preview.png` before packing.
- Limits: at most 1 MB for Steam, 2 MB for Paradox.
Home: `docs/agent/WORKFLOW.md`, `docs/agent/prompts/Launch_Prep/03_STORE_AND_SITE_medium.md`
