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

### OI-51 · opened 2026-10-03
Keep the accepted train startup notices separate, or combine them into one load line?
- The quiet-log sitting passed; this is a store-work preference, not another launch test gate.
- Combining them would need its own scoped code action; this evidence pass leaves the notices alone.
Home: `docs/agent/prompts/Launch_Prep/03_STORE_AND_SITE_medium.md`, `docs/agent/reports/TRAIN_FINAL_BATTERY_20261002.md`

### OI-47 · opened 2026-10-03
Should the Arboretum keep its own service category, adding Comfort alongside Parks?
- The test build uses a separate category; it does not compete with Hanging Gardens for Parks coverage.
- The Parks-specific Hippie bonus consequently does not apply to it.
Home: `docs/agent/bugs/D19.md`, `docs/agent/reports/ARBORETUM_BUILD_20261003.md`

### OI-48 · opened 2026-10-03
Should the Arboretum keep a normal garden footprint and the one-per-dome limit?
- The test build uses the vanilla Large Garden model and leaves the spire slot free.
- Its appearance and balance are starting values for you to judge in game.
Home: `docs/agent/bugs/D19.md`, `docs/agent/reports/ARBORETUM_BUILD_20261003.md`

### OI-46 · opened 2026-10-03
Should mechanized depot throughput become a post-launch module, and which shape do you want?
- Recommended: fixed ×5, off by default; 250-unit hidden IO pad, up to 25 units per crane landing.
- The smaller design keeps five units in flight and transfers extra at landing; look and motion code stay vanilla.
- A literal larger in-flight load needs a separate accounting/recovery design; it is not certified by this report.
- Choose fixed boost, base/×2/×5/×10 dial, stricter cargo design, or park; estimates are 2–3 or 3–4 sessions.
- Authorize its new option contract and retaining over-capacity pad stock on OFF until it drains; no cargo field needed.
Home: `docs/agent/reports/MECHANIZED_DEPOT_THROUGHPUT_20261003.md`

### OI-44 · opened 2026-10-02 · launch
Which platforms will you choose on Paradox Mods, and what console approval step does it show?
- No Opt-In listing exists yet; the first upload creates both, Paradox then Steam.
- The fix pack's approval does not carry over; login, any Workshop agreement and approval are yours.
Home: `docs/agent/prompts/perma/release_prompt.md`, `docs/agent/reports/LAUNCH_PREP_AUDIT_20261002.md`

## Run
