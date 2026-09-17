# Project State — the one mandatory read

Current only, rewritten in place; history newest-first in `docs/archive/SESSION_LOG.md`.
Module truth `agent/bugs/INDEX.md` · engine facts `agent/facts/INDEX.md` · doc map `docs/README.md`.
Authoring `agent/WORKFLOW.md` · code `agent/FIX_POLICY.md` · what came from where `agent/PROVENANCE.md`.
Pre-2026-08-31 STATE (the long form): `git show e8d8cee:docs/agent/STATE.md`.

## Now
- BUILT + VERIFIED IN GAME 2026-08-12 ON 1.0.7: `8/8` beside the fix pack, `8/8` with it uninstalled,
  fix pack `74/74` with this mod absent; save contract PROVED off 4 real saves. Audit CLOSED, SUSTAINED.
  Evidence `archive/SESSION_LOG.md` 08-12 + `agent/PROVENANCE.md` §2. ⛔ None of it re-run on 1.1.0.
- ⛔ NOT PUBLISHED. 2026-08-17 (owner): the fix pack launched ALONE ("its not ready imo");
  every player-facing reference to this mod was PARKED (fix pack `reports/PARKED_OPTIN_REFERENCES.md`).
- 2026-08-31 READINESS PASS: tooling/process parity with the fix pack @ `bec2e06` restored.
  Report `agent/reports/READINESS_REVIEW_0831.md`; ledger `agent/PROVENANCE.md` §6.
- ⚖️ 09-01 (owner, verbatim "the opt in modules has not fully tested yet"): TESTING PRECEDES LAUNCH. Owed:
  a. D01 `tested-attended` since 09-01; D02/D03/D04/D09 PASSED pre-split. Grants and limits are in the entries.
  b. D06/D07/D12 RETIRED 09-17 (hold below); PT-62's owed remainder left with D12 — moot, not passed.
  c. FIX_POLICY §8 both-config test is owed at ship for EVERY module, on the shipping build.
- ⇒ THEN the launch session owes five steps IN ORDER — the list is `agent/reports/READINESS_REVIEW_0831.md`
  §6 (restore checklist · preview art · in-game reload check · both-config ship test · `optin-v1.0.0` tag).
  ⛔ It was written on 1.0.7 and has no 1.1.0 re-verification step; add one before walking it.
  ⚠️ `python tools/upload_preflight.py` FAILS today on the missing preview art (owner, DECISIONS_OWED 85).

## Build state — PULLED, never stored here
⛔ Counts are NOT kept in this file (donor ruling 2026-09-15): a stored number goes stale in silence.
Pull them: `python tools/doccheck.py --emit-counts`. Game build: `--emit-fingerprint` reads the .acf.
The 1 default-active module is `DroneStatDials` (registers WITHOUT `optional`, base dials = vanilla, armed).
The probe count is the SHARED suite's, not this mod's share. Gate MEASURED `8/8` beside the fix pack,
`1/8` at fresh defaults (owner's 08-12 18:30 log — the only recording), when EIGHT modules shipped.
⚠️ Every measurement above predates 1.1.0; see the version hold below.

## Gates and holds
- ⛔ PERSISTED NAMES ARE SAVE CONTRACT — the five `SMRFixPack_*` fields/modifier ids keep their bytes
  forever (`agent/PROVENANCE.md` §2); renaming one is FORBIDDEN. `l3_save_footprint.py` §3 must read exactly those five.
- ⛔ ZERO `SMRFixPack` references in executable code: the surviving tokens in `Code/` are the five
  persisted STRINGS (5 definitions, 6 comments) — data, not references. AST-PROVEN 09-01: 0 `Name` nodes
  carry the token (`reports/CONTAMINATION_AUDIT_20260901.md`; 817 hits classified, 0 contamination).
- ⛔ MODULE FREEZE: no behaviour change to any module without an owner ruling.
  ⚖️ DRONES UNFROZEN 2026-08-31 (owner, verbatim "Un freeze drones"): D09 `DroneStatDials` is open to
  design + playtest work under FIX_POLICY, A/B per change. D06 was too, and is now RETIRED/PARKED (below).
  ⛔ The D06 rebuild spec `reports/DRONE_REBUILD_DESIGN_20260901.md` and brief `prompts/DRONE_REBUILD_BUILD_high.md`
  were written against 1.0.7 and are NOT re-based; DECISIONS_OWED 94 then 92 still gate any build.
- ⛔ `EF-055`/`EF-056`: junction pull = real uninstall; a campaign COPY still runs its autosave
  rotation (pre-copy autosaves first, outside the save folder).
- ⚠️ CHEATS ENABLED on the rig; BOTH MODS LOADED is the standing config (owner rule, `agent/WORKFLOW.md`).
  Grep logs with the FULL token `[CommunityOptInPack]`.
- ✅ Remote PUBLIC 08-13 (`github.com/catt144/SMR-CommunityOptInPack`); title "Relaunched Fix Pack:
  Opt-In Modules" (family renamed 08-17, checklist 36); id/global/log tag UNCHANGED; v1.0.0; default-OFF RATIFIED.
- ⭐ 08-16 (owner): the farm/seed-logistics case is THIS HOUSE'S but PARKED post-launch
  (`FUTURE_IDEAS.md` #7; `reports/SEED_LOGISTICS_HANDOFF.md`, `DRONE_OVERHAUL_OPTIONS.md` §I/§K).
- ⭐ 08-20 (owner, checklist 37 Q1): the fix pack's two `00_Core.lua` repairs (`2f077e8`) MIRRORED
  (`update_suspect` clear, `Register` re-registration guard). NEITHER verified in a running game here.
- ⚖️ 08-31 WRAP CHECK + LOAD ORDER are MACHINE-GATED — doccheck prints both every run; never type
  the numbers. Lists live in `tools/harvest_wrap_targets.py` and
  `tools/doccheck.py`; rationale `FIX_POLICY` §2. Reordering is a behaviour change; Require-block
  additions = owner (DECISIONS_OWED 84).
- ⚠️ 08-31 HOSTILE INPUT (`l8_hostile_input.py`): a foreign `SMROptInPack = true` / `_Disabled = true` /
  throwing `__index` kills module files at load — the donor's L8 verdict on the same Core;
  adjudication inherited (fix pack `reports/L8_ADVERSARIAL_MAP.md`); not a launch blocker there.
- ⚠️ 08-31 TESTKIT GAPS FILED, none edited (report §5): no opt-only run mode; `98_EnablePathLeg`
  hardcodes the fix pack's id; `FixtureCarry` blind to D09's modifiers; no vanilla controls.
  ⛔ 09-17 ADDED: probes `CohortHousing`/`NoHomeless` + `OptionsMenuOptIn`'s WANT list are ORPHANED by the
  retirement. Kit is SHARED — DO NOT EDIT; owner (fix pack checklist 83). This is the ruling's open fallout.
- ⚖️ 09-01 (owner): fix pack is LAUNCHED + in MAINTENANCE; this mod is its own product. The site
  `SMR-CommunityMods` is SHARED by both mods (own repo). Its opt-in restore (46 parked passages) runs
  on PUBLISH DAY, never before — silence over "coming soon" (fix pack `PARKED_OPTIN_REFERENCES.md`).
- ⛔ FACTS: re-synced from the fix pack @ `e6ec192` on 2026-09-17 (107 files, was 68 @ `bec2e06`);
  this repo's old `EF-057`/`EF-058` are `EF-061`/`EF-062`. `EF-` ids are ALLOCATED BY THE FIX PACK
  (`agent/WORKFLOW.md` reading path 2; ratify = checklist 86). Only `EF-062`'s FUTURE_IDEAS pointer
  is adapted locally; everything else is a byte copy, so a re-sync is a straight overwrite.
- ⛔ 2026-09-08 THE GAME MOVED TO 1.1.0 + DLC (build 24995074) and overwrote `ModTools\Src`.
  `--emit-fingerprint`: 56 facts MOVED, 31 HOLD. Both trees archived at `C:\Dev\SMR-SrcArchive`
  (`EF-083`). ⛔ NOTHING in this repo — module, probe, gate, test result — has been re-verified on 1.1.0.
- ⛔ 2026-09-17 `ClassicRockets` (D01) IS OBSOLETE ON 1.1.0 AND NOW INVERTS ITS OWN INTENT.
  Vanilla `UniversalRocketBase:GetFuelResourceRequest` (`1.1.0.403908/Src/Lua/UniversalRocket.lua:1891-1895`)
  now returns the full ration for a player-controlled rocket with no `arrival_loc` unless
  `IsSpecialAutomode()`; on 1.0.7 (`:1639-1642`) it returned 0. The module fires only when the shipped
  answer is 0, so its whole remaining reach is the Trade/TradePad/Rival rockets 1.1.0 deliberately excludes.
  Retire/rewrite = owner (MODULE FREEZE); the ask is OI-01, still OPEN. The other 7 were re-read 09-17:
  `reports/MODULE_REVALIDATION_1_1_0.md`; OI-03 (D03 dead tourist guard) and OI-04 (D04 sun-removal gap) OPEN.
- ⚖️ 2026-09-17 THREE MODULES RETIRED (owner): D06 PARKED, D07 + D12 DEAD; files + `items.lua` +
  `metadata.lua` entries DELETED. ⛔ Git is the record — restore sha `cc846e4`; the untracked copies at
  `C:\Dev\SMR-OptInPack-archive\` are convenience, not record. Entries D06/D07/D12 carry dated sections;
  consequences + the two engine findings `reports/MODULE_REVALIDATION_1_1_0.md` §10. Historical `status:`
  words KEPT. ⛔ PROVENANCE §2 rows STAY — 3 names outlive their module. ⚠️ D12's DEFECT SURVIVES 1.1.0
  verbatim; reviving = port `exclusive_trait` → `filter_residents`, not un-delete.
- ⚖️ 2026-09-17 TOOLING/PROCESS PARITY re-ported from the fix pack @ `e6ec192`: five `.claude/skills/`,
  the `.rgignore` archive boundary, the `CLAUDE.md` rules header + generated `AGENTS.md`,
  and doccheck `--regen` / `--emit-fingerprint` / PUSH SET. Ledger: `agent/PROVENANCE.md` §6.

## Open owner decisions — bodies in `docs/DECISIONS_OWED.md`
- ⚖️ 09-12 (owner, fix-pack checklist 167): this mod's decisions moved HERE. Items 84, 85, 89–97
  are in `docs/DECISIONS_OWED.md` verbatim; 83 (shared TestKit), 86 (EF-id rule), 88 (a fix-pack
  feature) stayed on the fix pack's `docs/PLAYTEST_CHECKLIST.md` because they bind IT.
- ⚖️ 09-17: OI-02/OI-05/OI-06/OI-07 CLOSED by the retirement ruling and deleted. OPEN: OI-01, OI-03,
  OI-04, 84, 85, 89–97. ⛔ 94 + 92 are still specified against 1.0.7 — do not rule them until re-based.
- ⛔ Nothing there is owed while this mod is not launching, and it was written pre-1.1.0 —
  re-read every citation against the archived 1.1.0 tree before acting on any of them.
