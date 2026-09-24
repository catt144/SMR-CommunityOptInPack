# Drones chain, link 5 — the smoke with the owner

**Link 5 of the `03_Drones` chain** (`README.md`). **ATTENDED.** Runs after link 4. Read
`DESIGN.md` §5 and §6 and your `## Notes from upstream`. `git log`, `git pull` both repos first.

## Authority

Testing depth (owner): **a smoke test only** — the full prediction battery runs once, on the final
build. The sitting loads the standing save (`train_hub_base`), which has the stations, tracks and
lines prebuilt; only the hub is built each round. About five steps at a time. After an autosave the
owner re-presses the armed slot.

## End state

1. `DESIGN.md` §5's scenarios, in the owner's order, with the ETAs measured and recorded: a far
   break, save and reload mid-trip, completion and trains running again, a break with the hub short
   of stock, the hub toggled off, a drone near the hub doing ordinary drone work and never charging,
   the reassign buttons greyed, more than 30 jobs with 30 out, one destroyed, an autosave mid-trip.
2. **The owner's three 2026-09-22 cases**, which the design did not previously cover: dispatch with
   the maintenance gauge full (the hub malfunctioned), dispatch with the grid dead, and the hub
   **destroyed with drones out** — every orphan removed, a carried cube dropped rather than lost,
   nothing left running a dead hub's command, and a save-and-reload across it.
3. **What the 2026-09-23 design changes added**, each needing the game: the **fleet scaling tiers**
   (light load keeps a couple out, rising load launches more, falling load recalls them, never
   stranding a drone mid-job), with the owner dialling the thresholds by eye; a **reload during a
   flight**, which must continue the job from its deadline rather than blink the drone away; and, in
   whichever flight mode shipped, no drone lost to vanilla's `Idle` (`SMROptInHubFlight.Lost`)
   across a long run, including one left alone past the 60 s hold timeout.
4. `DESIGN.md` §6: whether a station can build a train with no repair drone out, and what the hub
   waits for if it cannot — with the owner's ruling on the acknowledgement launch if a drone is the
   missing piece.
5. The result recorded in the hub report and spec §10, and the owner's rulings where the role that
   obeys them reads them.

**Both configurations** (`FIX_POLICY` §8) and both toggle directions belong to the module's ship
test; this is a design smoke. Say plainly which of them this sitting did not cover.

## Live work list

One todo item per commit-and-verify unit.

## Scope

In: the sitting, the measurements, the records, small fixes the sitting forces. Out: redesign, new
mechanisms, art.

## Stops

1. A scenario cannot run because a fixture is missing: look for an existing save that has it before
   asking the owner to build one.
2. The sitting turns up a design fault rather than a bug: record it and route it to the owner; do
   not redesign live.

## Do not claim

Do not claim "repairs work" from one break. Claim the breaks, the distances, the ETAs and the
reload, in that order.

## Notes from upstream

### Audit handoff, 2026-09-24 — confirm rollback loads before resuming the smoke

Read `docs/agent/reports/TRAIN_HUB_AUDIT_111_20260923.md`, §8 before §6. The owner
tried the autosave and known-good templates: loader assertions, then CTD after
Ignore All. `3a0faff` is withdrawn; the exact legacy dwell closure is restored.
First confirm a fresh-process `train_hub_base` load with the original mods enabled,
without assertions or CTD;
do not save over the template, and exit if an assertion appears. The original
save defect is OPEN and `dwell_smoke.py` is RED. Old/new permanent compatibility
needs a migration and native old→new→save→reload controls before resuming saves.
The stall cause remains OPEN. Once loading works, preserve the stalled save and
give Sweep, Routes, Status and HubRepairStatus one at
a time before adding damage or clearing locks. The report has the next track and
thread reads. A successful toolkit SAVE line did not mean serialization was clean.

Then repeat the first repair to COMPLETION and observe trains moving, including
multiple breaks on one track, before advancing to the mid-trip reload. The earlier
status dumps were before the deadline. Recheck cargo with a full hub (1.1.1 changed
UnloadAll), actual flight arrival on quiet logs (path failure became quieter),
remote maintenance, cube survival on destruction, return-leg reload, all unrun
DESIGN/L4 scenarios and the conditional train-construction request read. OI-27
holds the cross-map drone policy; OI-26 stays as owner-ruled. The report explicitly
lists unadjudicated engine fields/citations and conditional nanite/split risks;
resolve those before treating the audit as full compatibility clearance.


### L3 handoff, 2026-09-23 — `OI-26` is yours to judge, in passing

The owner parked `OI-26` rather than staging it: the Wasp's fixed 7 m ride on engine-flown legs
stays as built, and you judge it **under real play** — if a train passes beneath a drone during
your scenarios, look; do not build a rig for it. The answers and the three-way consequence are in
`00_TRAIN_ORCHESTRATOR.md` under "Each run" step 3. Owner, 2026-09-23: *"i am leaning towards not
worth changing its state"*, so absence of a complaint across the smoke is a real answer.

### L4 handoff, 2026-09-23 — what shipped, and what the smoke must show

**Shipped** (`b556035` on `b1f62be`; report `L4_HUB_20260923.md`): the hub records a break on its
network as a job in `SMROptIn_track_work` (the one persisted name; the toggle lives inside it),
claims the cost on its own stock at dispatch, and at a persisted deadline pays the outstanding
demand and completes the site through the repair group leader; a Wasp flies out and back for the
look (adopted after a load); five standing Wasps scale with vanilla's load word; a destroyed hub
despawns every drone; the panel shows "Repair drones: N out / 30" and a track-repair toggle;
every Station on the graph has the hub as a controller for its two maintenance requests only.
Dials: `SetHubRepairTune(name, value)` or a table; `HubRepairStatus()` with the hub selected
prints the jobs, the fleet, the load and the dials.

**Before the sitting:** restart the game or reload the save. The owner's running game took the
uncommitted tree that registered every station request (the resource balancing seen 2026-09-23);
the committed filter re-files each far station once at load.

**The smoke must show, in this order, with `HubRepairStatus()` before and after each step:**
1. A far break (TestKit meteor): the job appears, the ETA notice shows with minutes, the stock's
   claim (Metals target down, actual unchanged), a Wasp rises from the pit and flies out; at the
   deadline the site completes, the stock drops by the outstanding cost at 50 % (100 % if
   SafeTransport is researched), trains run again. Read the deadline against the Wasp's arrival:
   the deadline is straight-line distance at the flight's Speed plus `LaunchTime` 12 s plus
   `WorkTime`; if the Wasp arrives long before or after it, move `LaunchTime` or `Speed`.
2. Save and reload mid-trip: the job survives with its deadline; a Wasp under an engine leg or
   hold is adopted and continues (no blink); one removed at save reappears from the pit if more
   than `MinVisualTime` 15 s remains; the site still completes on time. Autosave the same.
3. Drones and the hub on one site: a break inside ordinary drone range; whichever finishes first
   wins; if drones win, `HubRepairStatus()` shows the job gone and the Metals target restored.
4. Short stock: the job waits, the hub wears the no-resource sign, the panel line says "short of
   Metals"; deliver stock; it dispatches. Confirm nothing vanilla toggles that sign on the hub.
5. The toggle off: a new break waits; a repair under way completes; toggle on dispatches it.
   The player's switch off: the same for new dispatches. Malfunction (gauge full) and a dead grid:
   dispatch and completion continue.
6. Remote stations: a far station's maintenance no longer says "No Drone Hub in range"; a fleet
   Wasp flies there for the repair work; watch whether `Idle`'s go-home distance bounces it home
   repeatedly. And the negative: no cube hauling between stations (the 2026-09-23 fix).
7. The fleet: five idle near the hub; make load medium/high (work in the radius) and count 10 /
   20; let it fall and count the recalls (one per 15 s after 60 s low); a far idle drone goes home
   first; a drone with a cube is never recalled. The reassign buttons grey on every hub Wasp; a
   rocket cannot load one as cargo. Then `SetHubRepairTune("WaspPalette", "P4")` for the recolour
   ask (spec §9) and judge it; it applies to Wasps spawned after the call.
8. More than 30 jobs with 30 out: jobs wait; a waiting repair recalls a fleet drone at once.
9. A destroyed hub with drones out and one carrying a cube: every Wasp gone, the cube on the
   ground, nothing still flying; save and reload across it; the same after a salvage.
10. `DESIGN.md` §6, train construction with no repair drone out, and whether a far station's train
    construction waits on a drone the hub now supplies only for maintenance.
11. **Ask the owner** whether the FLEET must also launch from the pit: today fleet Wasps appear
    around the body as build 3's drones did (the repair flight does use the pit); the flight file
    would need a release entry point to hand a risen Wasp to vanilla's `Idle`.
12. **Look at the ring pillars on the exit** (`RingPillar_4`): the static measure at the settled
    lane reads −5 cm against a conservative Wasp box; the owner accepted the flown exit by eye.

## Lifecycle

Append anything unresolved into link 6's notes, then **delete this file and strike its row in
`README.md` in the same commit**.

### Sitting so far, 2026-09-23 (resume through the audit handoff above)

Done in the sitting, on `train_hub_base`, then `SMRTK_A.sav`:
- **Far break 1:** a job, the notice with "ETA 57 min", which is game minutes, about 28.5 s of game time. The Metals target went down with the actual unchanged (owner). The Wasp crossed the dome glass: the crest handoff was still the file default.
- **After Load A:** fleet 5, low. Meteor id 71 gave one job, `deadline 19814893`, 24463 ms left, the Wasp on a stock `FlightGoto` (log `Mars.exe-20260923-23.38.53`). Then the trains locked up and the owner called the audit.

Owner rulings, each built and committed:
- **Never adopt orphaned drones** (`cafcaea`). A fresh hub read fleet 9, and the recall deleted 4 adopted drones.
- **No ETA in the notice, and it clears when the repair is done** (`5ec8048`).
- **Fixing code that a closed link built is the working link's job** (the audit carries this too).

Also fixed: engine `HandoffAt="outside"` is now the default, with the receipt re-pinned (`1b32bc8`).

Not yet seen: whether the Wasp reached the break before or after completion, the mid-trip reload, and every later item. First diagnose the stall and repeat completion through the audit handoff above; then resume the mid-trip reload.
