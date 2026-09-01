# Readiness review — 2026-08-31: this workspace against the fix pack's tooling, tests and process

**Question asked (owner):** *how ready is this workspace for work, and which of the
fix pack's tools, tests, auditing, chain method and processes should apply here.*
**Method:** inventory both repos (`C:\Dev\SMR-BugFixPack` @ `bec2e06`, this repo @
`e8d8cee`), diff every shared artefact against the split sha `33d69f5`, run every
candidate tool against THIS tree, and port what earns its place. Every count below
was emitted by a tool or a `git` command in this session; nothing is hand-typed.

⚠️ Reports are not authority. Where this disagrees with `agent/bugs/`, `agent/facts/`,
`WORKFLOW.md` or `FIX_POLICY.md`, those win.

---

## 1 · Verdict

**Ready for work — after this pass.** Before it, the repo was a faithful but frozen
2026-08-12 snapshot of the fix pack's method: doccheck GREEN, hook enabled, tree clean,
and every improvement the fix pack made in the following 19 days absent. The three
material gaps were (a) a **fact-id collision** that made cross-repo `EF-` citations
ambiguous, (b) **no release gate** — the one generic tool that runs here
(`upload_preflight`) FAILS on a missing preview image nobody had recorded, and
(c) **no desk instrument** for the one lifecycle defect this repo has MEASURED
(double registration after `ReloadLua`), which STATE listed as unverified.

What did NOT need porting: the chain method (re-synced verbatim), probe hygiene, the
both-mods rule, save-safety policy — all already here and current.

## 2 · Measured state before the pass

| surface | finding | evidence |
|---|---|---|
| doccheck / hook | GREEN; `core.hooksPath=tools/hooks` set; `main == origin/main`; tree clean | `python tools/doccheck.py --emit-counts`, `git status -sb` |
| toolchain on this machine | `luaparser 4.1.0`, `lupa 2.8`, Src at `A:\…\ModTools\Src` all present — every donor instrument is runnable here | `pip list`, `ls` |
| STATE.md | 60/60 lines but 4 lines over 200 B (line 28 = 1,734 B); counts block said 94 probes, doccheck emits **100** | doccheck v4 vs v5 |
| SESSION_LOG | one entry (08-12) though STATE recorded 08-13/16/17/20 events | `docs/archive/SESSION_LOG.md` |
| facts | 58 here vs 68 there; **7 shared facts updated in the fix pack after the split, not carried** (EF-008/023/039/051/054/055/056); **id collision**: this repo's EF-057/058 (2026-08-16) ≠ the fix pack's EF-057/058 (08-15/08-19); this repo's two were the fix pack's EF-061/062 | `cmp` per file; `git log --diff-filter=A` |
| tools | 5 here vs 20 there; the 14 missing include the whole L2–L8 audit ladder, the F107 wrap check, the three release gates | `find tools/` |
| doccheck drift | donor gained: STATE byte budget (08-18), `tested-attended/-unattended` vocabulary (08-15), `LOAD_ORDER_RULES` (08-17), F107 wrap check (08-24) | `git diff 33d69f5..HEAD -- tools/doccheck.py` |
| process docs | WORKFLOW missing "Release marking — tags, not branches", the 08-24 probe rule, the byte-budget rule 8; FIX_POLICY missing F107 + F110; CHAIN_METHOD missing §5a (fan-out rule) + commit-the-folder rule; `prompts/` EMPTY (donor: 13 standing/one-off prompts) | header diffs, `grep` |
| `.claude/settings.json` | absent (donor: 4 read-only git allowances) | `ls` |
| upload preflight | **FAIL 1/16**: `image` empty/missing — no `preview.png` in this repo; the upload is rejected before packing (`ParadoxMods.lua:39`) | `upload_preflight.py C:\Dev\SMR-OptInPack` |

## 3 · What was ported, and what each run found

Ledger with shas and edits: `agent/PROVENANCE.md` §6. Tool outputs are in this
session's scratch; the load-bearing lines are reproduced here.

| tool | port | run against this tree — result |
|---|---|---|
| `doccheck.py` v5 | 4 checks carried | GREEN after STATE reflow; **LOAD ORDER: 2 constraints checked** (CohortHousing<NoHomeless on `Colonist:FindEmigrationDome`, ResidencyControl<NoHomeless on `ChooseDome` — the two orders `metadata.lua` had only as a comment); **WRAP CHECK: 0 outside Require, 3 allowlisted** |
| `harvest_wrap_targets.py` | namespace, allowlist emptied then refilled | 24 declared entries / 17 pairs / 8 classes. **3 capture+install sites with no Require pair**: `Opt_DroneOverhaul` → `Drone.CleanUnreachables` (declared Drone.lua:879), `TaskRequestHub.FindTask` (_TaskRequest.lua:72); `Opt_MultipleSuns` → `SolarPanelBase.GameInit` (SolarPanel.lua:8). Each captured class DECLARES the method → `prev` is real → benign; allowlisted with citations (the donor's own pre-rule precedent). Naming the pairs in Require blocks = code edit to frozen modules → owner (checklist 84) |
| `upload_preflight.py` | verbatim | 16 checked · **1 FAIL (image)** · 1 UNCHECKABLE (PDX login). Everything else passes incl. `code` == disk and `items.lua` order |
| `pack_predict.py` | content prefix | 12 files would pack; `*/tools/*` now excludes 21 (was 8 at launch prep) — `ignore_files` still covers it |
| `pack_list.py`, `flpk_extract.py` | verbatim | not run — need a built `.fpk` (post-upload check) |
| `l2_reload_sim.py` | **rewritten for this repo** (donor's is DataPatch-fixture-bound; no `Opt_*` calls DataPatch) | **PASS**: all 8 register exactly once across a simulated `ReloadLua`, 1 verdict line per id per load, 0 files dead. **Control REPRODUCED**: the pre-guard `00_Core.lua` (`git show 2cedf7d~1`) yields 16 order entries, every id twice — the 2026-08-17 "NoHomeless, NoHomeless" dialog's mechanism. This is the desk half of the boot check STATE owes; the in-game half is still owed |
| `l3_save_footprint.py` | both prefixes, label fix | §3 NAMED STATE reads **exactly the five persisted names of PROVENANCE §2** plus the two framework globals; §4 GAMEVARS: none; §6 no SaveGame hooks (as designed — no layer-1 tear-down needed); §7 one "foreign" field `update_suspect` — an over-report: `entry` is `SMROptInPack.fixes[id]` (mod table, never persisted) |
| `l4_player_surfaces.py` | namespace | 17 `Untranslated` sites (Core dialog, D03/D12 rollovers), 22 log sites, 48 verdict strings of which 31 match `UpdateSuspects`' substrings and **17 reach the dialog unmatched** — informational; same shape the donor's L4 adjudicated |
| `l5_containment.py` | namespace | 106 file-scope statements (10 calls, 36 to read); entry-point census runs. Adjudication of rows: not done in this pass — it is a lens sweep's job, and this pass ported the instrument, not the sweep |
| `l6_promise_map.py` | namespace + `Opt_` prefix | census 1 identity: 8/8 ids match filenames; census 2 package: metadata == items == disk, order equal; census 4: every module has a bugs entry; census 5 (site fix list): N/A while the mod's passages are parked |
| `l6_reachability.py` | namespace | 4 global replacements (`ChooseDome` 8 uses in 5 files; `SuppressNotification` 1 use — F85 shape, read it) and 9 members; `Community.CanAcceptNewColonists`, `TaskRequestHub.FindTask`, `Colonist.FindEmigrationDome` have ≤3 sites tree-wide — triage rows, already read by their entries |
| `l7_env_map.py` | verbatim (generic) | runs; global map emitted from the compiler |
| `l8_hostile_input.py` | namespace + module trio | CONTROLs pass (documented form vetoes exactly `ClassicRockets`; nothing set vetoes nothing). Hostile values kill module FILES at load: `SMROptInPack_Disabled = true`, `SMROptInPack = true`, `SMROptInPack = {}`, a throwing `__index`. **Identical to the donor's L8 verdict** — `00_Core.lua` is the same code — and inherits its adjudication (`SMR-BugFixPack/docs/agent/reports/L8_ADVERSARIAL_MAP.md`); the fix pack shipped with it |
| `audit_preset_fields.py` | namespace | selftest 8/8; **0 preset-field writes** in this tree (`Opt_MultipleSuns`' `build_once` write goes through a template table the census does not class as a preset container — read `Opt_MultipleSuns.lua:93-114` if that ever matters) |
| `l8_deference_map.py` | **NOT ported** | quarantined in the donor (misses `local orig = Name` captures); may not be cited until repaired there |
| `blocking_analysis.py`, `split_*.py` | already here | unchanged |

## 4 · Process carried

- **WORKFLOW.md**: rule 8 → byte budget; "Release marking — tags, not branches"
  (`optin-` prefix, this repo's junction/worktree names, H-02 version rule);
  Release steps bullets 7–8 (preflight 0 FAIL; the parked-passages restore walk);
  the 2026-08-24 probe rule (production route + independent expectation), with the
  honest note that only D12's clause 1 is a vanilla control today; the **EF-id
  allocation rule** (fix pack allocates; this repo mirrors); a tools pointer.
- **FIX_POLICY.md** §2: the F107 rule and the F110 rule, each adapted with this repo's
  own state (three allowlisted sites; `Opt_DroneStatDials` already does the F110
  pattern with `UIColony`).
- **CHAIN_METHOD.md**: re-synced VERBATIM (adds §5a sequential-vs-parallel, the
  commit-the-folder rule, the cross-repo premise row).
- **prompts/**: `DISPATCH.md` (this repo's orientation + route table) and
  `STATE_EVICTION.md` (the byte-budget cleanup procedure). `GENERAL_USE_PROMPT.md`
  stays single-sourced in the fix pack with the playtest files.
- **facts/**: re-synced from `bec2e06` — 7 updated shared facts taken verbatim
  (this repo's copies were the pre-split text; the donor's are supersets), EF-057…068
  added, this repo's old 057/058 now live at 061/062 (their donor ids), all
  references updated (`FUTURE_IDEAS.md`).
- **`.claude/settings.json`**: the read-only git allowances for all three repos.

## 5 · TestKit — filed, not edited (shared kit; kit edits need a launch to verify)

Survey of `C:\Dev\SMR-BugFixPack-TestKit` (100 probes; 94 excluding the 6 rescue
probes — the denominator STATE's "8 of 94" used). This mod's coverage:

| gap | where | why it matters |
|---|---|---|
| **9 probes, not 8**: `ClassicRockets` lives in `30_Probes_Wave3.lua:88`, the other 8 in `60_Probes_Opt.lua` | counts | STATE's "8 probes" undercounts by one |
| **D06 `Opt_DroneOverhaul` has NO `RunAll` probe** — measured only by the manual `91_Stress.lua` two-leg harness | `91_Stress.lua:11-15` | the one experimental module is the one with no automatic verdict |
| **No opt-in-only run mode**: `RunAll(kind_filter)` filters on `kind`, never on owner; a standalone leg prints ~85 fix-pack FAILs around 8 real verdicts | `00_TestCore.lua:456` | the true-standalone leg is readable only by hand |
| **Enable-path leg hardcodes the fix pack**: `PACK_ID = "SMR_CommunityFixPack"` | `98_EnablePathLeg.lua:54` | this mod's normal first-run path (tick at the main menu → in-place `ReloadLua`) has never been measured for THIS mod by that leg — and it is exactly the F87/double-Register territory |
| **`FixtureCarry` is blind to D09's residue**: channel 5 hardcodes `SMRFixPack_F35_`; channel 4 walks `city.labels`, not `colony.label_modifiers` | `99_FixtureCarry.lua:164-186` | a stale `SMRFixPack_DroneSpeedDial`/`CarryDial` modifier in a fixture is invisible |
| **No vanilla-control clauses** for D01–D04/D07/D09 (only D12 clause 1 has one) | `60_Probes_Opt.lua:491-495` | a game patch that repairs one upstream leaves the probe passing over a no-op module — the 08-24 rule's exact failure shape |
| No save-footprint / reload-persistence probe for this mod (the rescue mod has `SaveRescueSelfClean`) | `65_Probes_Rescue.lua:329-361` | dial persistence across a reload is untested by the suite |
| `OptionsMenuFixPack` is the only opt probe that NEEDS the fix pack loaded (SKIPs otherwise) | `60_Probes_Opt.lua:987` | correct; recorded so nobody reads its SKIP as a defect |

⇒ Owner decision **83** (fix pack checklist): authorise the kit edits. None was made
here — an unverified change to the shared kit is a change to both mods' suites.

## 6 · What is still owed before this mod uploads (in order)

1. Walk the restore checklist — fix pack `reports/PARKED_OPTIN_REFERENCES.md`
   (~46 passages; the fix pack's `metadata.lua` change = its version bump).
2. Preview art → `preview.png` + `'image'` in `metadata.lua` (owner, checklist 85);
   `upload_preflight.py` must then report 0 FAIL.
3. The in-game half of the reload check: eight `applied`/`inactive` lines once each
   after a Mod-Manager `ReloadLua` (the desk half PASSED here; `l2_reload_sim.py`).
4. Both-configuration ship test (with the fix pack, and with it absent) —
   `FIX_POLICY` §8; note which fix pack version it was tested beside.
5. Tag `optin-v1.0.0` at upload (`WORKFLOW.md` "Release marking").

## 7 · Owner decisions raised (mirrored on the fix pack's checklist, R10)

83 TestKit edits for this mod's coverage · 84 name the three allowlisted wrap pairs
in Require blocks (frozen-module code edits, need an A/B) · 85 preview art ·
86 ratify the EF-id allocation rule.
