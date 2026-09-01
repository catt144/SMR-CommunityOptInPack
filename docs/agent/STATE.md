# Project State — the one mandatory read

Current only, rewritten in place; history newest-first in `docs/archive/SESSION_LOG.md`.
Module truth `agent/bugs/INDEX.md` · engine facts `agent/facts/INDEX.md` · doc map `docs/README.md`.
Authoring `agent/WORKFLOW.md` · code `agent/FIX_POLICY.md` · what came from where `agent/PROVENANCE.md`.
Pre-2026-08-31 STATE (the long form): `git show e8d8cee:docs/agent/STATE.md`.

## Now
- BUILT 2026-08-12, VERIFIED IN GAME the same evening: `8/8` beside the fix pack; `8/8` with it
  UNINSTALLED; fix pack `74/74` with this mod absent. Audit CLOSED 08-12, everything SUSTAINED.
- Save contract PROVED 08-12: five persisted names read back off 4 real saves under exact
  `SMRFixPack_` bytes; write→save→reload broke 0 of 3 fields (`archive/SESSION_LOG.md`, 08-12).
- ⛔ NOT PUBLISHED. 2026-08-17 (owner): the fix pack launched ALONE ("its not ready imo");
  every player-facing reference to this mod was PARKED (fix pack `reports/PARKED_OPTIN_REFERENCES.md`).
- 2026-08-31 READINESS PASS: tooling/process parity with the fix pack @ `bec2e06` restored.
  Report `agent/reports/READINESS_REVIEW_0831.md`; ledger `agent/PROVENANCE.md` §6.
- ⇒ NEXT: nothing owed until this mod's launch session. That session owes, in order (report §6):
  1. walk the restore checklist — ~46 parked passages across the fix pack repo + `SMR-CommunityMods`;
     the fix pack's `metadata.lua` change = its version bump + re-upload; re-measure, doccheck, `mkdocs --strict`;
  2. preview art → `preview.png` + `'image'` in `metadata.lua` (owner, checklist 85);
     `python tools/upload_preflight.py` FAILS on exactly this today (16 checked, 1 FAIL);
  3. in-game boot check: eight modules report once each after a Mod-Manager `ReloadLua`
     (desk half PASSED 08-31, `tools/l2_reload_sim.py --strict`; its falsifier reproduces the 08-17 doubling);
  4. both-configuration ship test — with the fix pack and with it absent (`FIX_POLICY` §8), naming the version;
  5. tag `optin-v1.0.0` at upload (`agent/WORKFLOW.md` "Release marking").

## Build state — `python tools/doccheck.py --emit-counts`, never hand-typed
```
BUILD STATE (emitted by tools/doccheck.py)
- modules: 8 registered (1 default-active, 7 optional-gated files)
- Code/*.lua files: 9
- TestKit probes: 100 (shared kit — serves both mods)
- BUGS index rows: 0 F + 9 D + 0 C
```
The 1 default-active is `DroneStatDials` (registers WITHOUT `optional`, active at base dials = vanilla, armed).
Game pinned **1.0.7.396349** (`EF-014`).
Probe count is the SHARED suite's (94 excluding the 6 rescue probes). This mod owns **9** of them —
8 in `60_Probes_Opt.lua` + `ClassicRockets` in wave 3; D06 `DroneOverhaul` has NONE (report §5).
Gate MEASURED `8/8` beside the fix pack, `1/8` at fresh defaults (owner's 08-12 18:30 log — the only recording).

## Gates and holds
- ⛔ PERSISTED NAMES ARE SAVE CONTRACT — the five `SMRFixPack_*` fields/modifier ids keep their bytes
  forever (`agent/PROVENANCE.md` §2); renaming one is FORBIDDEN. `l3_save_footprint.py` §3 must read exactly those five.
- ⛔ ZERO `SMRFixPack` references in executable code: the surviving tokens in `Code/` are the five
  persisted STRINGS (5 definitions, 6 comments) — data, not references. AST-PROVEN 09-01: 0 `Name` nodes
  carry the token (`reports/CONTAMINATION_AUDIT_20260901.md`; 817 hits classified, 0 contamination).
- ⛔ MODULE FREEZE: no behaviour change to any module without an owner ruling.
  ⚖️ DRONES UNFROZEN 2026-08-31 (owner, verbatim "Un freeze drones"): `Opt_DroneOverhaul` (D06) and
  `Opt_DroneStatDials` (D09) are open to design + playtest work under FIX_POLICY, A/B per change;
  PT-52's freeze is LIFTED (its test still needs the rewrite from the approved plan). Entry point:
  fix pack `prompts/DRONE_PROJECT_PROMPT.md` §3 — the design decision is the owner's next call.
  Not touched by this ruling: `FUTURE_IDEAS.md` #7 (gleaner/pairing) stays parked post-launch until said otherwise.
- ⛔ `EF-055`/`EF-056`: junction pull = real uninstall; a campaign COPY still runs its autosave
  rotation (pre-copy autosaves first, outside the save folder).
- ⚠️ CHEATS ENABLED on the rig; BOTH MODS LOADED is the standing config (owner rule, `agent/WORKFLOW.md`).
  Grep logs with the FULL token `[CommunityOptInPack]`.
- ✅ Re-tick SPENT (owner 08-12): enabled, 7 toggles on, dials `5x`/`+2`; nothing owed.
- ✅ Remote PUBLIC 08-13 (`github.com/catt144/SMR-CommunityOptInPack`); title "Relaunched Fix Pack:
  Opt-In Modules" (family renamed 08-17, checklist 36); id/global/log tag UNCHANGED; v1.0.0; default-OFF RATIFIED.
- ⭐ 08-16 (owner): the farm/seed-logistics case is THIS HOUSE'S — `reports/SEED_LOGISTICS_HANDOFF.md`,
  `DRONE_OVERHAUL_OPTIONS.md` §I/§K; PARKED per `FUTURE_IDEAS.md` #7, post-launch, one decision at a time.
- ⭐ 08-20 (owner, checklist 37 Q1): the fix pack's two `00_Core.lua` repairs (`2f077e8`) MIRRORED —
  `update_suspect` cleared on success, `Register` guarded against re-registration.
  Neither verified in a running game HERE; the guard is desk-verified 08-31 (`l2_reload_sim.py`);
  the `ctx.heal` clear is pre-emptive (no `Opt_*` calls `DataPatch`).
- ⚖️ 08-31 WRAP CHECK (F107 rule, `FIX_POLICY` §2): 3 pre-rule sites allowlisted with Src citations —
  `Opt_DroneOverhaul` (`Drone.CleanUnreachables`, `TaskRequestHub.FindTask`), `Opt_MultipleSuns`
  (`SolarPanelBase.GameInit`). Require-block additions = owner (checklist 84).
- ⚖️ 08-31 LOAD ORDER enforced by doccheck: CohortHousing < NoHomeless (`Colonist:FindEmigrationDome`),
  ResidencyControl < NoHomeless (`ChooseDome`) — the shipped nesting; reordering is a behaviour change.
- ⚠️ 08-31 HOSTILE INPUT (`l8_hostile_input.py`): a foreign `SMROptInPack = true` / `_Disabled = true` /
  throwing `__index` kills module files at load — the donor's L8 verdict on the same Core;
  adjudication inherited (fix pack `reports/L8_ADVERSARIAL_MAP.md`); not a launch blocker there.
- ⚠️ 08-31 TESTKIT GAPS FILED, none edited (report §5): no opt-only run mode; D06 unprobed;
  `98_EnablePathLeg` hardcodes the fix pack's id; `FixtureCarry` blind to D09's modifiers;
  no vanilla controls for D01–D04/D07/D09. Owner (checklist 83).
- ⚖️ 09-01 (owner): fix pack is LAUNCHED + in MAINTENANCE; this mod is its own product. The site
  `SMR-CommunityMods` is SHARED by both mods (own repo). Its opt-in restore (46 parked passages) runs
  on PUBLISH DAY, never before — silence over "coming soon" (fix pack `PARKED_OPTIN_REFERENCES.md`).
- ⛔ 08-31 FACTS: re-synced from the fix pack @ `bec2e06` (68 files); this repo's old `EF-057`/`EF-058`
  are now `EF-061`/`EF-062`. `EF-` ids are ALLOCATED BY THE FIX PACK from now on
  (`agent/WORKFLOW.md` reading path 2; ratify = checklist 86).

## Open owner decisions — bodies in the FIX PACK's `docs/PLAYTEST_CHECKLIST.md` → "Decisions waiting on you"
- 83 TestKit edits for this mod's coverage · 84 Require pairs for the 3 allowlisted wrap sites ·
  85 preview art · 86 ratify EF-id allocation rule ·
  88 `FUTURE_IDEAS.md` #9 routing · 89 `Code/` comment-only wording sweep · 90 loc-table ruling scope (audit 09-01).
