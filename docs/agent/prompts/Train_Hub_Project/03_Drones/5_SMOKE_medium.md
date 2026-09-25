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

### Audit handoff, 2026-09-24 — siding and save fixes pass the owner fixture

Read `docs/agent/reports/TRAIN_HUB_AUDIT_111_20260923.md`, §§8–12 before §6. The owner
tried the autosave and known-good templates: loader assertions, then CTD after
Ignore All. `3a0faff` is withdrawn; the exact legacy dwell closure is restored.
The template and `Autosave Sol 31(3)` rollback controls passed (`10.45.34` and
`10.49.56-6aad2d75.log`). Native reads identified opposite siding reservations
mutually blocking departure despite runnable tracks and a clear crossing.
HubExitClear now recognizes completed siding parking; the regression rejects
the old guard. After restarting, the owner confirmed the trains are unstuck.
Physical contact/clearance was not explicitly confirmed. The snapshot guard
`102f5f0` now passes the owner's legacy-load, 128× autosave/reload, new manual-save
and full-restart/manual-load controls (§§11–12). The closed writer log has no
persist/load/crash failure markers; the fresh-load prefix is also clear of those
markers. The existing ArtSpec startup error and Braze network failures remain.
ck215 is consumed. This did not test repair-drone adoption mid-flight, ambiguous
pre-wrapper saves or the ship matrix. Preserve the protected inputs. The report has runnable
track/thread probes if another stall occurs; the completed probes need no replay.
A successful toolkit SAVE line did not mean serialization was clean.

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

Not yet seen: whether the Wasp reached the break before or after completion, the mid-trip reload, and every later item. The siding stall and reported save failure now pass their owner controls; repeat repair completion through the audit handoff above, then resume the mid-trip reload.

### Sitting, 2026-09-24 (resumed after `07`, fixed build)

Seen by the owner:
- Two breaks on one track: both repaired, the line cleared.
- A track reaching the hub only through other stations: dispatched, the train on it stopped then ran again.
- Menu save right after dispatch, then reload: the repair still completed. That save logged 0 persist errors (log `Mars.exe-20260924-12.35.05`). An autosave is not yet seen.

Measured (log `Mars.exe-20260924-17.07.20`), with move_speed 8960 from the owner's 5x dial and techs:
- One break at 1457 m straight line. The pit launch took 3944 ms; the leg out was 1371 m in 18784 ms (7296 units/s); the leg back 7310 units/s. An earlier leg flew 7382 / 7465.
- The old deadline (12000 + dist/16000 + 7000) landed 5.4 s after arrival. Its launch and speed errors cancelled.

Owner rulings, built:
- The Wasp's panel shows its trip (`a40db90`).
- A meteor damages the hub and never destroys it (`5cfaee6`). Mystery bombardment stays vanilla.
- **Option A:** the deadline follows the live Wasp speed x 80 % plus a 4 s launch (`459629e`).

Print-only instruments: `9fe42cd` (dispatch and completion), `6cad16c` (leg speed).

Noticed:
- A meteor beside the hub destroyed it (before `5cfaee6`), and vanilla stored a train bound for it.
- The ruin's magenta icon is brief 06's uncommitted `display_icon` test path, not ours. Routed to 06's session through the owner.

Still to run: the meteor beside the hub on the fixed build, the panel lines, short stock, toggle/switch/malfunction/dead grid, remote stations, fleet tiers, >30 jobs, destroyed hub with drones (a salvage now, since meteors no longer destroy it), §6 train construction, an autosave, the owner asks (fleet pit launch, ring pillars, OI-27).

### Sitting, 2026-09-24 continued (log `Mars.exe-20260924-17.18.02` to `-21.01.51`)

Passed, seen by the owner and checked in the log:
- **Drones and the hub on one site (item 3).** The hub's 5 standing Wasps went to a break 170 m out: vanilla asks one drone per broken element (`ConstructionSite.lua:727`, 1000 build points each), capped at 10. The hub's flight finished it first. Owner: **keep the flight inside the radius too** ("simpler and less surfaces to break").
- **A meteor on the hub.** It malfunctioned and its own drones repaired it.
- **Short stock.** The job waited with the missing-stock sign after `68ad91b`. Vanilla's `BrokenTracks` notification is shown on every break (`TrainDisasterHandling.lua:114-118`) and was left as it is.
- **The flight as the authority.** A far break completes during the Wasp's work stage ("0 ms after the deadline, stage work", on four trips).
- **A despawned Wasp.** It was relaunched in 1.8 s and the repair completed at the new Wasp's work.
- **A save/reload mid-trip.** The adopted Wasp completed at its work.
- **A malfunctioned hub.** It dispatched and completed.
- **Persist errors:** 0 in every log of the sitting.

Owner rulings, built:
- A break the hub is repairing reads drone-covered while its switch and toggle are on (`c2294af`).
- The site completes at the Wasp's work end (`47a5ca6`).
- **The flight is the authority; the deadline is only a fallback** (`c764ea4`). This overtakes `DESIGN.md` §2 "the timer is the only authority".
- **A repair under way always has a live Wasp; a lost one is relaunched** (`89330ed`). `MinVisualTime` is removed, so L4's handoff item 2 wording above is overtaken, and adoption always resumes "out".

Bug fixed: dispatch now waits for the site's resource requests (`68ad91b`).

Measured leg speeds at move_speed 8960: 6990-7465 units/s on long legs, 2145 on an 80 m hop.

### Handoff, 2026-09-24 late (context limit; the owner is about to ask for a partial backtrack)

HEAD is `dba55af`. The icon brief's peer work is uncommitted in the tree (`metadata.lua`, the template and its generated companion, `UI/`). It is not this link's; commit by pathspec.

**Every change since the last notes is its own commit, so a backtrack can revert by sha.** Newest first; "seen" means the owner saw it in play:
- `dba55af`: the fleet launches from the pit and recalls land back in it. `LaunchSpacing` is 300 ms ("a swarm coming out to assist"). New flight entry points `F.Release`, `F.Recall` and `F.OnReleased`. **Not yet seen.**
- `7ddb822`: the fleet moves in chunks 5/10/20/30. It keeps `Buffer10` 2 / `Buffer20` 5 / `Buffer30` 10 idle, grows one chunk per `LoadWindow`, and recalls one idle Wasp at a time. `ForceFleet` is the console probe. **Seen:** 10, then 20.
- `458f1fc`: the panel's "Drones load" line shows the fleet meter. **Seen** ("Heavy" at 10).
- `3955ab5`: the fleet's own 60 s idle-drone meter, with vanilla's thresholds. Vanilla's `GetDroneLoad` is a 12-game-hour average (`_GameConst.lua:94-98`) and read "low" with every drone busy.
- `c73a286`: the hub's Drones section and Track-repair toggle are built in `sectionCustom:Init`; the runtime XTemplate was registered but never rendered. **Seen and passed:** the toggle off/on, the switch off/on, a far station's maintenance serviced (log `Mars.exe-20260924-21.44.09`).

Explained, not changed:
- The "Construction not serviced by drones" rows were stale while the game was paused (`t` constant); vanilla refreshes them through game-time `Notify`, and they cleared on unpause.
- The dome outside the 15-hex ring is genuinely uncovered.
- "Not enough Power" was the owner's unbuilt power lines.

Open owner question: the growth gate is one chunk per 60 s window. I offered to restart the meter at each jump and require 15 s instead. **Unanswered.**

Still to run:
- `WaspPalette` "P4", for the owner to judge.
- More than 30 jobs (item 8), now against the 25-Wasp fleet plus 5 reserved.
- Save/reload across a demolished hub (the rest of item 9 passed 2026-09-25, below).
- `DESIGN.md` §6 train construction (item 10).
- An autosave mid-trip.
- Cargo unloading with the hub full (the audit: 1.1.1 changed `UnloadAll`).
- The ring pillars by eye (item 12).
- OI-26 in passing.

Not covered by this sitting: both configurations and both toggle directions of the ship test.

Close-out still owed by the final link-5 session:
- The result into the hub report and spec §10, with the rulings from all three notes sections, where the role that obeys them reads them.
- This file deleted with its README row, per Lifecycle.

### Sitting, 2026-09-25 (log `Mars.exe-20260925-13.34.56`)

Owner rulings:
- **Wasps leave and come home through a train door** (`3c47ce2`). This partly backtracks the pit launch in `dba55af`: the rise out of the pit stays, then the Wasp crosses to the hub's centre and runs out along a door's track at 2 m above the rail. One Wasp takes the door nearest its break; a swarm uses every door, in shuffled order, before any door repeats. Occasional clipping of trains is accepted. `ExitVia="deck"` restores the under-deck exit. `DoorRideHeight` and `DoorOutDistance` are guesses, for the owner to set by eye. No clearance against the mesh has been measured for the door route.
- **A far station gets maintenance only; its upgrades are not the hub's.** The owner's words: "lets leave it just wanted to check". An upgrade files two `rfUpgrade` demand requests and connects them to its command centres (`Building.lua:2094-2124` on 1.1.1.405907). The Station filter refuses them to an out-of-range hub, so an upgrade at a far station waits for a vanilla drone controller. This confirms the 2026-09-23 maintenance-only ruling for upgrades.

- **A demolished hub's ruin stays until a vanilla controller clears it.** The hub despawns its Wasps when destroyed (2026-09-22), so it cannot clear its own ruin; the owner chose to keep this, as vanilla does for any ruin.
- **The fleet steps 5 → 15 → 25, and the last 5 of 30 are held for repair flights** (`cf14791`). Owner: "it feels bad under heavy work. so 5 stays default then it jumps to 15, and then the next jump goes to 25. And the extra 5 are reserved for drone repair dispatches". Dials `Chunk2`, `Chunk3`, `RepairReserve`; the idle buffers 2 / 5 / 10 now follow the chunks. The growth gate, still one jump per 60 s window, stays an open question. **Seen:** a heavy build test on the new steps, "it works fine" (log `Mars.exe-20260925-14.14.01`, no mod error).

Seen by the owner (log `Mars.exe-20260925-13.43.07`):
- **Item 9 on a demolish.** A true salvage cannot remove the hub: a demolish leaves a ruin. Demolished with Wasps out: every Wasp was gone and the cubes were on the ground. The log shows a 1161 m repair dispatched at t=33912099 just before; the despawn prints nothing. Save/reload across it was not reported.
- **Growth and recall on real load.** The TestKit `CheatDelete` of the old hub left a `ResourceStockpileLR`; hauling it grew the fleet to 20 (the old steps) at 128× speed. The quick-build of the new hub deleted the pile, as vanilla's cheat path does (`ConstructionSite:OnQuickBuild` → `DestroyStockpilesUnderneath`, `ConstructionSite.lua:1682-1683`, `:1637-1643` on 1.1.1.405907); a normal build moves the piles out (`:129`). The fleet then recalled to 5.

- **The door launch and recall** (`3c47ce2`): the growing fleet leaves through several doors, and recalls come home through doors. Owner: "1 is correct".
- **Recalls take idle Wasps only:** a recall of 5 after work took no busy or cube-carrying Wasp (owner, by eye).
- **A save and load mid-trip on the door build** (slot A): the repair still completed. The autosave is still owed: it runs vanilla's own `RequestAutosave(GetAutosaveName())` (`CommonLua/Savegame.lua:1555` on 1.1.1.405907), which can be called from the console.

Bug, fixed in `ad5113b`: `door_count` crashed the flight driver. The engine's `GetSpotBeginIndex` raises "Invalid spot" on a name the body lacks; it does not return -1. The game ran the broken build until it restarted.

Not yet seen: the door launch in play.
