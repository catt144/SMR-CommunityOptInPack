# DRONE_REBUILD_BUILD — one-off: build the D06 rebuild from the ratified spec

**One-off. Deletes itself in its close-out commit** (`git rm` this file). Any model; the
owner picks. **Start with `git log --oneline -10` + `git pull` in BOTH repos**
(`C:\Dev\SMR-OptInPack`, `C:\Dev\SMR-BugFixPack`) and in the TestKit
(`C:\Dev\SMR-BugFixPack-TestKit`). Staleness anchor: written 2026-09-01 at opt-in `870c3e0`
/ fix pack `3e224a7`; verify against `git log` before trusting any specific.

> ⛔⛔ **DO NOT START UNTIL THE OWNER HAS RATIFIED THE SPEC.** Fix-pack
> `docs/PLAYTEST_CHECKLIST.md` item **91** must carry a ruling line. Its body is
> `reports/DRONE_REBUILD_DESIGN_20260901.md` §9 ask 1. If item 91 is still open, **stop and
> say so** — that is the whole answer for this session. Nothing here is a prototype exception.

> ⚖️ **THE SPEC IS THE SINGLE DESIGN AUTHORITY.** `agent/reports/DRONE_REBUILD_DESIGN_20260901.md`
> decides the mechanism, the tier table, the guard, the wrapper set, the `Require` block, the
> disclaimer's substance and the playtest. **There is no re-design in this session.** If the
> spec is wrong about something, that is a stop condition (§6), not a licence to redesign —
> record it, correct the spec in the same commit, and say so loudly.

---

## 0 · Orient

1. `git log` + `git pull`, all three repos. Read `docs/agent/STATE.md` whole.
2. **Todo list before starting** — one item per commit-and-verify unit, one in progress,
   marked complete the moment each lands, expanded when a stage splits (`WORKFLOW.md`
   "Authoring a prompt" element 1). Stage 1's experiments are **three separate items**
   (E-4, E-8, the guard assertion) because each has its own run and its own result line.
3. ⛔ **PROBE HYGIENE GATE — this brief RUNS TESTS, so the gate binds** (`WORKFLOW.md`
   "⛔ Probe hygiene"). `tasklist | findstr Mars.exe` **as its own step** before any code
   edit. No result is recorded without the sweep, and every result commit carries a
   `PROBE SWEEP:` line.
4. Read the ratified spec whole, then §1's read path.

---

## 1 · Read path — file granularity (`WORKFLOW.md` element 8)

**This repo:** `agent/reports/DRONE_REBUILD_DESIGN_20260901.md` **WHOLE** (the authority) ·
`agent/reports/DRONE_BANDS_CLEAN_REVERT_20260901.md` §4.2 (V / P / 2-S / D) and §5 (the
experiment cards, with predictions) · `CLAUDE.md` (both bans) ·
`agent/FIX_POLICY.md` §1, §2 (F107 + F110 + F87), §3, §3a, §5 · `agent/bugs/D06.md` ·
`Code/Opt_DroneOverhaul.lua` (what you are replacing) · `Code/00_Core.lua`
(`Register` / `Require` / `IsActive` / `OnDataReady`) · facts `EF-059 060 069 070 071 072
073 074` + `EF-002 014 019 022 023 029 053 054 058 066` · `agent/facts/INDEX.md` scan.
**Fix pack:** `prompts/DRONE_PROJECT_PROMPT.md` §2 (settled points), §4 (build rules) ·
`reports/DRONE_PRIORITY_SYSTEM.md` §6 (landmines, now 8), §8, §9, §10 ·
`archive/DRONE_RESEARCH_BRIEF.md` (the disclaimer spec) · `PLAYTEST_CHECKLIST.md` items
83 / 84 / 91 / 92 / 93 **and their rulings** · `archive/PLAYTEST_ARCHIVE.md` ~line 3000
(the B2 protocol + the CAN/CANNOT lists).
**TestKit:** `Code/91_Stress.lua` (the v2 lifecycle harness the A/B uses) ·
`Code/60_Probes_Opt.lua` (`opt_gate` at `:26-39`; D12's vanilla-control clause at
`:490-494` is the model for the new probe).
**Src, read-only** (`A:\SteamLibrary\steamapps\common\Project Spark\ModTools\Src`, build
`1.0.7.396349`): `Lua/_TaskRequest.lua:53-83` · `CommonLua/TaskRequest.lua:14-32, :181-190,
:240-256, :305-340, :364-374` · `Lua/Buildings/DroneControl.lua:1-12, :105-123, :685-757` ·
`Lua/RequiresMaintenance.lua:38-100, :182-206, :245-330, :418-430` ·
`Lua/SupplyGridBreakable.lua:33-56` · `Lua/Passage.lua:485-491` ·
`Lua/Units/Drone.lua:564-645, :760-813, :898-941, :1000-1016, :1164-1264`.

---

## 2 · STAGE 1 — THE FIRST GATE: the experiments, before any module code

⛔ **No line of `Opt_DroneOverhaul.lua` is written until this stage closes.** Checklist item
92 must authorise the runs; if it does not, see §2.4.

Every card: **NEW GAME only** (`EF-055/056` — the 07-31 incident broke a live colony); a
**TEMPORARY** TestKit module marked `TEMPORARY` in its header and **deleted in the result
commit** (the doccheck TEMPORARY sweep enforces it); `tasklist | findstr Mars.exe` as its own
step; **predictions committed BEFORE the run**; polled reads paired with an event witness
(`EF-057`); `PROBE SWEEP:` line on the result commit; archive the raw log by name and cite it.

### 2.1 E-4 — what `Request_FindTask` reads (≈ 30 min, attended)

Card and predictions: bands report §5. **Sharpened by the spec §3.2** — the proxy carries the
**REAL** `under_construction`, and the assertion is now about *which* request comes back:

- (i) *bound vs keys* — set `const.TaskRequest.MaxBuildingPriority = 5` from the console on a
  NARROW hub, call `hub:FindTask(drone)` in a `pcall`. **Prediction: throws** (bound). Restore 3.
- (ii) *call-time vs cached* — the same read is the answer. **Prediction: call-time.**
- (iii) *a mod-built view is honoured* — build the spec §3.1 proxy (one T5 work request at
  `priority_queue[3]`, its demand at `demand_queues[3][res]`, **real** `supply_queues`,
  **real** `under_construction`, **real** `restrictor_tables`, `lap_start`/`lap_time`); break
  the generator; call `TaskRequestHub.FindTask(proxy, drone)`.
  **Prediction: the tier request comes back** (demand paired with a real supply in the demand
  phase; the work request in the work phase). Inspect `proxy.priority_queue[3].index` after the
  call — **does C write the cursor into our table?** Record the answer either way.
  ⚠️ **Also run it with a live construction site in range**, so §3.2's discard-and-continue path
  is exercised rather than assumed.

### 2.2 E-8 — a substituted pairing executes like a matcher-chosen one (≈ 40 min, attended)

Card: bands report §5. **Plus the review's added assertion:** the tier delivery **ARRIVES at the
tier building**. Prediction: claim succeeds → PickUp → Deliver → unload →
`StartWorkPhase(drone)` hands the repair to the deliverer → `malfunctioned = false`.
Falsifier: the claim fails and the drone takes the shipped miss path (`Sleep(1000)`,
`Drone:Work :902`).

### 2.3 The `EF-074` guard assertion (folded into E-8's sitting)

With the TEMPORARY guard installed, and a tier delivery in flight, raise a third building of the
same resource to **High**. **Prediction:** the delivery still arrives at the tier building.
**Then the carve-out:** make the tier destination unreachable mid-flight. **Prediction:** the
drone drops the delivery vanilla-style and does **not** loop — this is the `must_change`
carve-out of spec §2b rule 5, and it is the half that would hang a colony if it is wrong.

### 2.4 The branch this stage decides

| result | what the build becomes |
|---|---|
| E-4(iii) passes, E-8 passes | **V-a** — the spec as written |
| + E-4(ii) reads call-time | **V-b** permitted (spec §3.4 row 1). One C call instead of three; **owner-optional, not automatic** — V-a is the ratified default and V-b changes the const at runtime, so take it only if the owner wants it |
| E-4(iii) **fails** | **P** — finder pre-emption (spec §3.4 row 2). E-8 still governs |
| E-8 **fails** too | **2-S** — table surgery at band 3 (spec §3.4 row 3). R10 fails by definition; the disclaimer narrows to the one-band claim; **no experiment is owed to ship it** |
| checklist 92 says "none yet" | **STOP AND REPORT.** Do not build V on an unmeasured matcher, and do not quietly downgrade to 2-S without the owner — that is a product decision (spec §3.4's last row is item 91's question (a)) |

⛔ **If a result CONTRADICTS a prediction, the measurement wins.** Correct the spec's affected
cells and the bands report's affected cells **in the same commit**, and say so loudly in the
commit body and in the summary.

---

## 3 · STAGE 2 — the build, one piece, one commit

Per `DRONE_PROJECT_PROMPT.md` §4 and the spec §6. `Code/Opt_DroneOverhaul.lua` is rewritten:
claim gate **deleted**; the tiers, the three lifecycle wrappers, the `OnMsg.LoadGame` rebuild
and the `ImproveDemandRequest` guard **added**; moonlighting **kept per the owner's answer to
spec §9 ask 3**; `DroneReport()` kept and extended with tier depths and the new counters.

**Binding build rules, each with its cost of being ignored:**

- **File-scope install, per-call `IsActive` gate** (`FIX_POLICY` §5, the A2 lesson). An
  apply()-time install runs after flattening on a first mid-session enable and is invisible to
  derived classes until restart.
- **Inert for a foreign object before it touches one** (`FIX_POLICY` §2): the hubs-only
  `IsKindOf(self,"DroneHubBase")` gate and the `module_active()` check are the wrapper's first
  statements, before any field read, allocation or log.
- **Every handler re-checks BOTH the registry status AND `SMROptInPack_Disabled`** (the A1
  lesson) — handlers install unconditionally, so `Register`'s veto alone does not cover them.
- **The `Require` block is spec §6.1, verbatim.** Every `(class, method)` pair installed on or
  captured from appears in it (F107). **No per-game runtime global** — `LoadedMaps`, `UIColony`,
  `Cities` are `rawget` reads inside handlers (F110). `Drone.Idle` is **not** in the block.
- **The two `Opt_DroneOverhaul` rows leave `tools/harvest_wrap_targets.py`'s allowlist in the
  same commit.** `harvest_wrap_targets.py --check` GREEN with two fewer rows is the receipt, and
  it answers checklist 84 by construction — say so.
- **`OnMsg.LoadGame` runs inline**, never in a spawned thread (`EF-029`).
- **No class-level `GetPriorityForRequest` override anywhere** (`EF-069`). If a design pressure
  points at one, that is a stop condition.
- **No new persisted name** (ban 1). `l3_save_footprint.py` must still read exactly five.
- **Zero `SMRFixPack` references in executable code** (ban 2) — the persisted STRINGS the module
  keeps are data, not references.
- **Header states the layer** (`FIX_POLICY` §3a): every wrapper here is layer 3 or a synchronous
  layer-2-shaped pre-wrapper; the header says which and why, and carries the toggle semantics in
  both directions including a first mid-session enable.
- **The mandatory D06 header correction stays:** the old *"savegame footprint: none"* claim was
  false (F86 Site 2) and the header must not reinstate any version of it. Point at the spec §4
  statement instead.

**Loop, per `WORK_PROMPT.md` §3 / `WORKFLOW.md` "Per-fix discipline":** game-not-running check →
edit → Lua parse sweep → desk instruments → the A/B → the D06 entry updated **in the same
commit as the code** → `PROBE SWEEP:` line.

**Desk instruments — all GREEN before the build commit** (spec §8a):
`python tools/doccheck.py` (both repos) · `python tools/l2_reload_sim.py --strict` ·
`python tools/l3_save_footprint.py` · `python tools/harvest_wrap_targets.py --check` ·
`python tools/blocking_analysis.py` over the wrap set (reproduce spec §5's verdicts, and restate
the two hand adjudications — `RequiresMaintenance.Repair` AMBIGUOUS is a `BaseRover` name
collision; `DroneControl.AddBuilding/RemoveBuilding` BLOCKS is the tool's closure blindness).

---

## 4 · STAGE 3 — verification (owner-attended steps are marked ⚑)

1. **The A/B**, spec §8a: `91_Stress.lua` v2 lifecycle harness, B2 protocol, **REPRESENTATIVE
   conditions** — right-sized fleets, **no pre-filled depots**, real industrial density, a
   genuine demand surge. Same quicksave both legs, same `scope`/`n`/`seed`, ≥ **3 seeds**,
   normal-to-3× speed. Read the lifecycle decomposition, **not** total clearance time. Log the
   commander profile and the live drone stats with the numbers. ⚑
2. **The vanilla control**: the A/B's OFF leg is the control, and its conditions header must
   match the ON leg or `Compare()` flags it. A mismatched pair is not a verdict.
3. **The ONE playtest**, spec §8 steps 1–8, in one sitting. ⚑ Steps 7 (Mod-Manager disable +
   restart + load-clean) and 8 (both-configuration, `FIX_POLICY` §8) are the ones that turn the
   disclaimer's two gated sentences (spec §7) from designed into witnessed. **Until they run,
   those two sentences do not ship.**
4. **The D06 `RunAll` probe** — designed in spec §8a, **built only if checklist 83 authorises a
   TestKit edit** (the kit is SHARED with the fix pack). Its vanilla-control clause is mandatory
   and D12's is the model. If 83 is unruled, file the design and move on; do not touch the kit.
5. **PT-52's archival** — spec §7 gives the edit; it is the owner's checklist to apply. **Propose
   it, do not apply it.**

---

## 5 · Scope fence

**IN:** stage 1's experiments, the rebuild of `Code/Opt_DroneOverhaul.lua`, its `Require` block
and the two allowlist retirements, the D06 entry, the disclaimer text into
`MOD_DESCRIPTION.md` (owner's wording, spec §9 ask 5), the A/B, the playtest, the probe
**design**.
**OUT:** D08 · D09 · F77 · seed logistics (`FUTURE_IDEAS.md` #7, `DRONE_OVERHAUL_OPTIONS.md`
§I/§K) · any second module · sub-toggles of any kind (ONE TOGGLE, ALL OR NOTHING — settled
07-31) · TestKit edits without checklist 83 · applying PT-52's archival · the
`blocking_analysis.py` closure-blindness fix (filed, spec §11) · re-designing anything the spec
settled. **Found something interesting out of scope → file it, stop.**

---

## 6 · Stop conditions — permission, not failure

- **Checklist 91 is not ruled** → stop before stage 1; report and end.
- **Checklist 92 says "none yet"** → stop at §2.4's last row; do not build V unmeasured and do
  not silently fall back to 2-S.
- **An experiment contradicts a prediction** → the measurement wins; correct the spec and the
  bands report in the same commit and say so loudly.
- **The design drifts toward a persisted name, a function stored on a game object, a frame below
  a `Sleep`, a widened `const.TaskRequest` bound over a real hub, or anything that fails R3/R7**
  → that route is out by the owner's directive. Record why and take the next fallback.
- **A fact contradicts Src** → correct the fact (fix pack first), same commit.
- **The A/B cannot be run under representative conditions** (no suitable colony) → run it anyway
  and **label the leg's conditions honestly**; do not report a cheat-prepared result as a verdict
  (the B2 external-validity lesson is the reason this line exists).
- **A tier-table cell turns out to need a running game and no card covers it** → add the card,
  mark the cell, continue.

---

## 7 · What may NOT be claimed

- Any E-4 / E-8 / guard outcome that is not in an archived log, cited by name.
- Any tier-precedence **ordering** until playtest step 1 passes at n ≥ 3 (E-9's question).
- **"Clean revert"**, "uninstall-clean" or "nothing in your save" until step 3's legs 7 **and** 8
  both run clean. The design argument is complete; the witness is not.
- **"No behaviour change" for the `EF-074` guard** — it IS one (deliveries stop being traded up).
- **"The tiers are strict"** without "per hub poll" — a far hub's drone can take T4 while a near
  hub's T5 waits (spec §3.3 R10).
- A desk-derived anything as "verified"; the `blocking_analysis.py` verdicts are a static tool's
  output plus two hand adjudications.
- Counts not from `doccheck --emit-counts`.
- **That the module fixes the depot-last-resort behaviour.** It does not (`EF-059`); spec §2b
  rule 3 and the disclaimer both say so.

---

## 8 · Close-out

Code + entry in the same commit; experiment results in their own commits with their
`PROBE SWEEP:` lines and archived log names; the TEMPORARY TestKit module `git rm`'d in the
result commit; `MOD_DESCRIPTION.md` disclaimer landed with the owner's wording;
`STATE.md` kernel line updated (byte cap — **evict, do not compress**);
`archive/SESSION_LOG.md` leg (newest first, `tags:`); any new checklist asks filed on the fix
pack with their numbers on `STATE.md`'s open-decisions line; `doccheck` GREEN in **both** repos;
push both (and the TestKit if it was touched with checklist 83's go); **`git rm` THIS file in
the close-out commit and name the grave**
(`git show <sha>:docs/agent/prompts/DRONE_REBUILD_BUILD.md`).
The summary to the owner ends with what is still owed — the playtest steps not yet run, the
sentences not yet witnessed — not with "done".
