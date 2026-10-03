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

### OI-46 · opened 2026-10-03
Should mechanized depot throughput become a post-launch module, and which shape do you want?
- Recommended: fixed ×5, off by default; 250-unit hidden IO pad, up to 25 units per crane landing.
- The smaller design keeps five units in flight and transfers extra at landing; look and motion code stay vanilla.
- A literal larger in-flight load needs a separate accounting/recovery design; it is not certified by this report.
- Choose fixed boost, base/×2/×5/×10 dial, stricter cargo design, or park; estimates are 2–3 or 3–4 sessions.
- Authorize its new option contract and retaining over-capacity pad stock on OFF until it drains; no cargo field needed.
Home: `docs/agent/reports/MECHANIZED_DEPOT_THROUGHPUT_20261003.md`

### OI-21 · opened 2026-09-19 · launch
When this mod publishes, do its store tools come from the fix pack or get ported here?
- Ported here 2026-10-03 as the prepared choice (Launch_Prep/03, no ruling yet): `tools/paradox_card.py`,
  `tools/store_screenshots.py` and the new `tools/store_parity.py`. Reversible.
- The donor's copies select fix-pack inputs from their own paths; "run from the fix pack" needs donor edits.
- Say "keep the ports" (closes this) or "run from the fix pack" (ports deleted; donor parameterised there).
- The old fix-pack listing drafts are history; the maintained copy is `reports/STORE_AND_SITE_20261003.md` §3.
Home: `docs/agent/prompts/perma/release_prompt.md`, `docs/agent/reports/STORE_AND_SITE_20261003.md`

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
Home: `docs/agent/prompts/perma/release_prompt.md`, `docs/agent/reports/LAUNCH_PREP_AUDIT_20261002.md`

## Run

### OI-12 · opened 2026-09-18 · launch
When this mod heads for upload, choose its preview art and the gameplay screenshots for its store pages.
- Preview: three candidates in `local/store_art_candidates/` (A hub + lettering, B hub and depot, C hub plain),
  from the shipped icon renders; pick one by name or supply your own art. None is wired yet.
- Gallery: five captures with the toolkit hidden, named in `reports/STORE_AND_SITE_20261003.md` §5, dropped in
  `B:\Dev\SMR\SMR-ScreenCaptures\optin_store\`; `python tools/store_screenshots.py` encodes them under 1 MB.
- Preflight fails only on preview at `214f0ad` (2026-10-03); Paradox rejects a mod with no `image` before packing.
- Limits: at most 1 MB for Steam, 2 MB for Paradox.
Home: `docs/agent/WORKFLOW.md`, `docs/agent/reports/STORE_AND_SITE_20261003.md`
