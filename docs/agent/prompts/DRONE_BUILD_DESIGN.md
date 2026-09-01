# DRONE_BUILD_DESIGN — one-off: the rebuild's design spec + build brief, under the hard constraint "no uninstall mod required"

**One-off. Deletes itself in its close-out commit** (`git rm` this file). Any
model; the owner picks. **Start with `git log --oneline -10` + `git pull` in
BOTH repos** (`C:\Dev\SMR-OptInPack`, `C:\Dev\SMR-BugFixPack`). Staleness
anchor: written 2026-09-01, the session after opt-in `0674ed6` / fix pack
`0a4b02a` (the bands report and its review); verify against `git log` before
trusting any specific. **This prompt DESIGNS and BRIEFS. It does not build** —
the build runs from the brief this job writes, in its own session, after the
owner's one-line ratification (§6).

> ⚖️ **The owner's directive behind this job (2026-09-01, this repo's session
> record):** determine the best build-out of the D06 rebuild **in a way that
> does not require the Save Rescue / any uninstall mod**, and produce the
> definitive layout table for demands and tiers. That directive makes rubric
> rows R3 and R7 (below) HARD constraints, not trade-offs: a candidate that
> leaves anything for a second mod to clean is out, whatever else it wins.

## Why — one paragraph of problem

D06's v1 (closest-fleet claim gate) measured inert; the owner ruled a rebuild
2026-07-31 shaped as urgency tiers — broken life-support first, then broken
anything, above the player's supply arrows — and 2026-09-01's
`reports/DRONE_BANDS_CLEAN_REVERT_20260901.md` (the mandatory first read)
established: bands 4–5 **as persisted data fail uninstall by measurement**;
the surviving routes hold the tiers in **transient structures the matcher is
shown** (V "view tiers" / P "finder pre-emption"), with **2-S table surgery at
band 3** as the citation-complete floor and **D** (the devs' tier on the five
producers) as its narrowest form. Two matcher cells are unproven (E-4, E-8 —
checklist 92), and the review filed a fifth fact the design must absorb:
`EF-074`, the `ImproveDemandRequest` hijack.

## 0 · Orient

1. `git log` + `git pull`, both repos. Read `docs/agent/STATE.md` whole.
2. **Todo list before starting** — one item per deliverable and per commit,
   one in progress, marked as completed the moment each lands, expanded when a
   stage splits (`WORKFLOW.md` "Authoring a prompt" element 1).
3. Stale-probe gate: **desk job — N/A unless the owner has run or runs
   experiments alongside**; if any test result is recorded this session, the
   gate binds first (`WORKFLOW.md` "Probe hygiene"; `tasklist | findstr
   Mars.exe` as its own step).
4. **Branch on the experiment state (checklist 92):**
   - **E-4 and E-8 have results** → design to them: V-a confirmed = V-a; E-4(ii)
     call-time = V-b allowed; E-4 failed = P; E-8 failed too = 2-S. Cite the
     archived logs by name.
   - **Not run** → design **V-a** as primary with **P** as the recorded fallback
     and **2-S** as the floor, and put E-4/E-8 (+ the `EF-074` guard assertion)
     at the TOP of the build brief as its **first gate**: the build session runs
     them before writing module code, and the brief names the switch it flips
     if they fail. Do not block this job on them; do not claim their outcome.

## 1 · Read path — file granularity

**This repo:** `reports/DRONE_BANDS_CLEAN_REVERT_20260901.md` WHOLE (rubric,
§4.2 V/P/2-S/D, §5 cards, §8 review addendum). `CLAUDE.md` (both bans).
`agent/FIX_POLICY.md` §1, §2 (F107 Require rule), §3, §3a, §4, §5.
`agent/bugs/D06.md` (plan of record; settled: claim gate DROPPED, ONE toggle,
D09 separate, hauling is the 88%). `agent/bugs/D09.md` (the dial pattern).
`Code/Opt_DroneOverhaul.lua` (what the rebuild replaces), `Code/00_Core.lua`.
Facts: `EF-059` `EF-060` `EF-069` `EF-070` `EF-071` `EF-072` `EF-073` `EF-074`
(the design's spine), plus `EF-002/019/022/023/029/053/054/058` (safety),
`EF-014` (build pin). `agent/facts/INDEX.md` scan.
**Fix pack:** `prompts/DRONE_PROJECT_PROMPT.md` (§2 settled points; §4 build
rules — the disclaimer, the ONE playtest, PT-52's archival);
`reports/DRONE_PRIORITY_SYSTEM.md` §3 §5 §6 (now 8 landmines) §8–§10;
`archive/DRONE_RESEARCH_BRIEF.md` (disclaimer spec); `PLAYTEST_CHECKLIST.md`
items 83/84/91/92/93 and their rulings if made; `archive/PLAYTEST_ARCHIVE.md`
~line 3000 (B2 protocol + CAN/CANNOT lists — the playtest rewrite's seed).
**TestKit:** `Code/91_Stress.lua` (the v2 lifecycle harness the A/B uses),
`Code/60_Probes_Opt.lua` (the probe suite the new D06 probe joins; D12's
vanilla-control clause is the model).
**Src** (read-only; re-derive routes): the files the bands report §3 cites —
`CommonLua/TaskRequest.lua`, `Lua/_TaskRequest.lua`,
`Lua/Buildings/DroneControl.lua`, `Lua/RequiresMaintenance.lua`,
`Lua/SupplyGridBreakable.lua`, `Lua/Passage.lua`, `Lua/Units/Drone.lua`
(incl. `:760-812` `ImproveDemandRequest`, `:1164-1175` Deliver), plus whatever
the chosen mechanism touches.

## 2 · Deliverable 1 — the DESIGN SPEC (`agent/reports/DRONE_REBUILD_DESIGN_<YYYYMMDD>.md`)

The spec's core is **THE TIER × DEMAND LAYOUT TABLE** — the single answer to
"who is served first, on which leg, fed from where, and what does turning it
off leave". Fill THIS skeleton (every cell cited to Src or an `EF-`; a cell
that needs a run says which experiment; add rows before dropping any):

| tier | contents — the predicate, as a Src-citable test | legs elevated | supply side | `EF-074` guard | revert: toggle OFF / uninstall |
|---|---|---|---|---|---|
| **T5** | malfunctioned life-support producers: `IsKindOf("AirProducer"/"WaterProducer")` AND `is_malfunctioned` (exactly 5 templates, Q3a) — **plus vanilla's own band-3 grid/dome repair legs** (`BreakableSupplyGridElement`/`PassageGridElement` repair+fracture requests), kept ABOVE T4 so the rebuild never outranks a dome breach with a broken Mall | maintenance **demand** (the haul IS the repair — the 88 %) + **work** | real `supply_queues` — `EF-059`'s depot-last-resort law untouched (say so explicitly) | guarded (this column is the fact's checklist: how, per leg) | nothing / nothing — the tier is a view (`EF-072`), the real filing is vanilla's |
| **T4** | every other `RequiresMaintenance` with `is_malfunctioned` (the `:41` "no work possible" split — broken, not degrading) | demand + work | same | guarded | same |
| **3** | the player's High; vanilla's pipes/dome (their own override); ⚖ the **food-service default 3** data patch (`ServiceWorkplace` + Food demand = exactly 4; Q4: class default, omitted from saves, clean revert) — its OWN sub-decision row in §6, buildable independently | vanilla | vanilla | n/a (real band) | data patch: reverts by Q4; nothing else |
| **2** | default arrows; **routine maintenance top-up stays here** (`is_need_maintenance` without malfunction is a supply question — the owner's split) | vanilla | vanilla | n/a | n/a |
| **1** | player Low; vegetation offers (class `priority = 1`, `EF-060`) | vanilla | vanilla | n/a | n/a |
| **0 / −1** | depots (`GetPriorityForRequest` base case); RCTransport own supplies (`RCTransport.lua:217-223`) | untouched | untouched | n/a | n/a |
| **construction** | unfiltered at its vanilla band — swarming is desirable; state it as a decision, not an omission | untouched | untouched | n/a | n/a |

And under the table, the demand-side rules as prose rows: which demand is
elevated (the building's `maintenance_resource_request`, only while
`is_malfunctioned`); what feeds it (any real supply — depots still last resort,
`EF-059`; write the player-visible consequence honestly); the `EF-074` guard
mechanism (chained wrapper on `ImproveDemandRequest` declining improvement for
tier-tracked demands — sync seam — or the `do_not_improve_req` route; pick one,
cite it); hub self-repair precedence kept (`Drone.lua:594-606` runs first);
**rockets/rovers per checklist 93's answer** (unruled → default "hubs only",
v1's gate, `Opt_DroneOverhaul.lua:185`, and say it is a default); shuttles
untouched (`EF-073` corollary); what happens under a dust storm (many T4
entries — the per-call budget, priced).

**The spec also carries, each its own section:**
1. **Mechanism** — the chosen candidate with the report's 11-row rubric
   re-printed and every cell's citation re-checked (not inherited); the tier
   sets' lifecycle (maintained on `SetMalfunction`/`Repair`/`DisableMaintenance`
   wrappers — all sync — rebuilt on `OnMsg.LoadGame` from `is_malfunctioned`);
   the fast path ("both tiers empty" = one table read); duplicates-by-design
   (`max_units = 1` makes double-presence safe — cite it).
2. **Savegame footprint statement** (FIX_POLICY §3/§3a shape): expected ZERO new
   persisted names — `l3` still reads exactly five; the argument per structure
   via `EF-072`'s only-route rule; what E-4(iii) still has to witness (does C
   retain a reference to a view table).
3. **What replaces v1, file by file** — the rebuild lands as ONE piece: claim
   gate deleted (settled), moonlighting KEEP or DROP with a recommendation and
   the reasoning (it serves saturated-neighbour ground the tiers do not),
   `DroneReport()` kept and extended to print tier depths; the `Require` pairs
   for every wrapped `(class, method)` (F107; today's allowlist rows retire —
   checklist 84 interplay, name it).
4. **The disclaimer draft** (research-brief spec: what was done, the limits,
   the off-ramp; now writable honestly — the footprint statement above IS its
   substance). Player-visible wording is the owner's (§6).
5. **The ONE playtest** replacing PT-52 (numbered steps, one sitting: tier
   precedence n≥3, the `EF-074` guard live, a dust-storm surge, OFF-flip
   mid-session, Mod-Manager-disable + restart + load-clean, both-config §8) —
   plus PT-52's archival as deprecated-by-redesign, written as checklist edits
   for the owner to apply, not applied here.
6. **The A/B + probe plan**: the `91_Stress.lua` v2 lifecycle A/B under
   REPRESENTATIVE conditions (right-sized fleets, no pre-filled depots — the
   B2 external-validity lesson, D06 entry); a D06 `RunAll` probe design with a
   **vanilla control clause** (D12's is the model; checklist 83 item 4 — needs
   the owner's go, it is the shared kit); the desk checks (`l2 --strict`, `l3`,
   `harvest_wrap_targets --check`, parse sweep) listed as the build's exit
   gate.

## 3 · Deliverable 2 — the BUILD BRIEF (`agent/prompts/DRONE_REBUILD_BUILD.md`)

A one-off brief the BUILD session runs from (it deletes itself when the build
lands). It must carry the eight `WORKFLOW.md` "Authoring a prompt" elements,
and: the E-4/E-8/`EF-074`-guard gate at the TOP per §0.4's branch; the spec as
its single design authority (no re-design in the build session); the loop from
`WORK_PROMPT.md` §3 (game-not-running check, parse sweep, desk instruments,
A/B with vanilla control, entry updated in the same commit, `PROBE SWEEP:`
line); the owner-attended steps marked as such; and the stop conditions of §5
below copied in.

## 4 · Scope fence

**IN:** the spec, the table, the brief, the checklist asks. **OUT:** building
any of it; running experiments (unless the owner says so mid-session — then
the probe-hygiene gate binds); D09; F77; seed logistics (§I/§K — the tier
table must not absorb them); the TestKit edits themselves (design the probe,
don't touch the shared kit — checklist 83); PT-52's actual archival (owner's
checklist, propose the edit). Found something out of scope → file it, stop.

## 5 · Stop conditions

- A tier-table cell can only be filled by a running game and no experiment
  card covers it — add the card, mark the cell, continue.
- The design drifts toward a persisted name, a function on a game object, a
  frame below a `Sleep`, or anything R3/R7 — that candidate is out by the
  owner's directive; record why, take the next.
- E-4/E-8 results exist and CONTRADICT the report's predictions — the spec
  follows the measurements; correct the report's affected cells in the same
  commit and say so loudly.
- A fact contradicts Src today — correct the fact (fix pack first), same commit.
- Checklist 91/93 turn out RULED in a way that conflicts with this prompt's
  defaults — the ruling wins; re-read it before the table is drawn.

## 6 · Owner asks — on the fix pack's checklist, one line + pointer each

1. **Ratify the spec** (mechanism + tier table) — supersedes/answers item 91;
   nothing is built until this line.
2. Food-service default 3: in the rebuild, separate, or dropped.
3. Moonlighting: keep or drop (with the spec's recommendation).
4. Item 92/93 confirmations if still open (experiments; hubs-only default).
5. The disclaimer's final player-facing wording.

## 7 · What may NOT be claimed

- Any E-4/E-8 outcome not in an archived log; any tier-precedence ordering
  (E-9 territory); "clean revert" beyond the report's YES-IF form until the
  build's own A/B and §8 both-config test run.
- "No behaviour change" for the `EF-074` guard — it IS a behaviour change
  (deliveries stop being traded up); the spec says so and prices it.
- A desk-derived anything as "verified"; counts not from `doccheck
  --emit-counts`.

## 8 · Close-out

Spec + brief committed (`git commit -F`, `PROBE SWEEP:` line — `clean`, this
job runs nothing); checklist asks filed, their numbers on `STATE.md`'s
open-decisions line; `STATE.md` kernel line updated (byte cap; evict, don't
compress); `archive/SESSION_LOG.md` leg (newest first, `tags:`); `doccheck`
GREEN both repos; push both; `git rm` THIS file in the close-out commit and
name the grave (`git show <sha>:docs/agent/prompts/DRONE_BUILD_DESIGN.md`).
Summary to the owner ends with the ratification ask, not with "done".
