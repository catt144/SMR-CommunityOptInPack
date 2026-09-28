# Hub dispatch — can the hub put a parked train onto another of its lines? (2026-09-27)

Brief `prompts/Train_Hub_Project/11_TRAIN_HUB_DISPATCH_INVESTIGATION_high.md`; spec §4.8 ruling 7
(owner, 2026-09-27). An investigation record: feasibility, evidence, a design sketch and a cost.
No dispatcher is built. Game source is archived **1.1.1.405907** unless a line says otherwise.

## Answer

**Yes, by source, and half of it is already measured.** A train standing at the hub is bound to a
line by exactly one thing, its `track` field plus membership in that track's `assigned_vehicles`,
and vanilla rewrites that binding itself on every hop. Reassigning it at the hub with vanilla's own
primitive and handing the train back to vanilla's `LoadTrain` makes it evaluate, load for and
travel the new line; nothing in route rebuilds, save fixups or load re-derives the old line.

- **MEASURED (build 3b, 2026-09-20, game 1.1.0.403908, lane-era movement code):** a parked hub train
  reassigned to a 60° line and to a 120° line departed on the requested arm and finished on that
  track. That leg forced `GotoStation` with a chosen destination; it did not let `LoadTrain` choose.
- **SOURCE, desk only:** vanilla's own loading decision on the reassigned track, and the train
  staying on the new line afterwards. The throwaway prototype below closes exactly this half in
  one sitting. **<<PENDING-RUN>>** until the orchestrator runs it.
- **Not a wall anywhere.** 5c (trains driving through hubs) is not needed for dispatch.

## Evidence

Each row is one claim with its class and the line it rests on.

| # | claim | class | where |
|---|---|---|---|
| 1 | `Train:AssignToTrack(track)` only moves the train between tracks' `assigned_vehicles` and sets `self.track` | SOURCE | `Units/Train.lua:220-228` |
| 2 | Vanilla reassigns the track on **every hop**: `GotoStation` calls `AssignToTrack(track)` for each departure track it walks | SOURCE | `Train.lua:357` |
| 3 | The next station, the through track and the arrival track are all read from `self.track`; no other field names the line | SOURCE | `Train.lua:150-155` (`GetNextStation`), `:208-218` (`GetArrivalTrack`), `:238` |
| 4 | `LoadTrain` refuses a source station that is not an end of `self.track`; the hub is an end of every arm's `TrackBase`, so any hub line passes | SOURCE | `Train.lua:232`; `Buildings/Track.lua:339-355` (`GetDestStation` asserts the station is an end) |
| 5 | `LoadTrain` then evaluates the through track of `self.track` (`GetConnectedTrack(self.track, "check dest")`, the opposite arm on the hub) and falls back to `self.track`; both are the **new** line's route. The inbound check reads `self.track.assigned_vehicles`, so it too follows the new line | SOURCE | `Train.lua:237-262`; `Buildings/Station.lua:931-962` |
| 6 | `TransferCargo` resolves the route from the track (`train_track_routes[track]`) and sums trains in that route; a moved train is counted on the new line | SOURCE | `Train.lua:862-908` |
| 7 | **Vanilla itself writes `train.track` raw** when a track's start station flips after load, and re-parks the train | SOURCE | `Tracks.lua:990-1022` (`reset_train_on_free_station`), called from `:1024-1044` |
| 8 | Vanilla's placement of a new train on a line is: cap gate `AddTransportLink`, then `AssignToTrack`, `AddOccupyingTrain`, `Start()` | SOURCE | `Track.lua:428-457` (`AssignTrain`); `StationsLink.lua:32-49` |
| 9 | `AddTransportLink` / `RemoveTransportLink` act on the **same** `assigned_vehicles` list, gate on `CanAddVehicle`, and only message `UpdateWarningSigns` | SOURCE | `StationsLink.lua:36-49`; `Station.lua:1411-1416`; `Track.lua:423-426` |
| 10 | Nothing re-derives a train's track later: `RebuildTrainRoutes` touches routes and colonists' `work_route` only; the train fixups prune invalid trains and restart deadlocked ones | SOURCE | `TrainTransport.lua:302-358`; `Train.lua:1100-1117` |
| 11 | A deleted track destroys **its** trains, so a moved train follows the new track's life, not the old one's | SOURCE | `Track.lua:69-76,159-166` |
| 12 | `track` is a persisted object reference; a reassignment survives save/load as vanilla-shaped state | SOURCE (read, not measured in the serializer) | `Train.lua:44` default; `Tracks.lua:990-1022` is the vanilla precedent for writing it |
| 13 | The vanilla cap on a line is per **route**: `max_trains = num_stations` (2 or more), and `CanAddVehicle` is `trains < cap`; the per-track `max_vehicles` only feeds the infopanel row | SOURCE | `TrainTransport.lua:492-537`; `Track.lua:65,423-426,601` |
| 14 | The hub's `TrainDepart` already routes from the **arrival** arm (`station_arrival_track`) to whatever arm the handed track sits on: siding rejoin, centre pivot for non-opposite arms, slide out, then vanilla traverse | SOURCE (dev mod) | `20_TrainHub.lua:825-844`, `:779-823` (`HubRouteTrain`), `:645-650` (`HubTurnPoint`: no pivot when `(a-b)%3==0`) |
| 15 | `TrainPassThrough` reassigns the train to the departure track before moving | SOURCE (dev mod) | `20_TrainHub.lua:854` |
| 16 | Hub occupancy is keyed by the **arrival** arm and is not disturbed by a track change; `HubExitClear` lets a train leave on an arm whose only occupant is parked on its siding | SOURCE (dev mod) | `20_TrainHub.lua:589-599`, `:531-546` (`GetOccupyingTrain`, own-`LoadTrain` exemption) |
| 17 | 60° and 120° departures from a parked hub train completed live after `AssignToTrack` + `at_spawn_track` + `GotoStation(dest)`; the smoke asserted `train.track == departure connector's track_obj` afterwards | MEASURED 2026-09-20 | slot source `tools/devmods/train_hub/tests/80_AgentSlots.lua.txt` (slot 3); driver `tests/98_TrainHub3bSmoke.lua.txt:163`; log `docs/archive/TRAIN_HUB_3B_Mars.exe-20260920-04.22.55-6a91a190.log` lines 701 (stage 2, arm 2 → 5), 1118 (stage 3, arm 2 → 3), 1554 (stage 4, reverse) |
| 18 | That log's one `[LUA ERROR]` is the known startup `ArtSpecEditor.lua:573`, not the movement | MEASURED | `grep -n "LUA ERROR"` on that log: 1 hit, line 181; 1,577 lines |
| 19 | The movement was rewritten to centre riding after 3b (spec §10, 2026-09-20/21). The other-line pivot on the **current** code has no live record I could find | ABSENCE, grep | `grep -n "60°\|120°\|other-line\|pivot"` over `TRAIN_HUB_SITTING_20260919.md` and `TRAIN_HUB_AUDIT_111_20260923.md`: 0 hits; spec lines 3440-3512 name only the siding trials |
| 20 | Assigned cargo stays aboard whole if its station is not on the new line (`UnloadAll` unloads assigned entries whole or keeps them) | SOURCE | `Train.lua:787-831`; the live case is spec §4.8 ruling 6 (train 2000001844, 98 aboard all sitting) |
| 21 | Brief 10's routing reads the line from the train's track, so a moved train gets the new line's orders; the need functions it would feed a dispatcher are **local** | SOURCE (dev mod) | `40_TrainDistribution.lua:164-176` (`line_managed`), `:397-507` (`train_view`), `:326-350` (`branch_need`, `child_need`, both `local`) |

Arm pairing for the six-connector hub: `hub_connector_directions = {4,1,3,0,2,5}` (`20_TrainHub.lua:3384`),
so arms (1,2), (3,4), (5,6) are the three lines; 3b's arm 2 → 5 is 60°, 2 → 3 is 120°.

## The throwaway prototype (built, not run)

`tools/devmods/train_hub/Code/50_TrainHubDispatchProbe.lua`, registered in `metadata.lua`. No
thread, no persisted field, no wrapper; it mutates only on an explicit call. `Run(train)` takes a
train parked at a hub in `Idle` or `LoadTrain`, with no assigned cargo and no passengers, picks
another hub line whose route has vanilla room (an unoccupied arm preferred), and performs vanilla's
own placement order: `RemoveTransportLink` on the old track, `AddTransportLink` on the new (the cap
gate), `AssignToTrack`, then `Train:Start()`, which is the `NewHour` restart path into `LoadTrain`
(`Train.lua:64-70,133-140`). It sets neither `at_spawn_track` nor a destination: vanilla chooses.
`Read(train)` prints command, station, track and its two end stations, arrival arm, cargo, next
station, and whether the train is still on the dispatched route. `Forget()` allows a second `Run`.

TestKit: slot 3 of `80_AgentSlots.lua` (shared kit, `SMR-BugFixPack-TestKit`) is rebound from the
finished capacity build's ruins-clear to this probe: the first press on a train parked at the hub
runs it (paused), later presses on that train read it. Slots 1-2 and 4-6 are unchanged, so brief 10's
slot 4/5 reads stand. Desk: `parsecheck.py` on the dev tree (7 files, 0 errors), the TestKit tree
(33 files, 0 errors) and the shipping tree (5 files, 0 errors); `distribution_slots_smoke.py`,
which executes the slot file under lupa, passes with the rebinding. Console equivalents:

```lua
SMROptInHubDispatchProbe.Read(SelectedObj)   -- [NEVER RUN]
SMROptInHubDispatchProbe.Run(SelectedObj)    -- [NEVER RUN]
```

### Sitting steps for the orchestrator (five), from `build6_capacity_covered_pass3`

Fresh boot, both mods and the TestKit. Predictions are written before the run.

1. Load, pause, run Scratch. Select a train parked at the hub that shows no cargo; read it with the
   console `Read` line. Predict `at_hub=true at_station=true assigned=false passengers=0` and a
   `hub_idx` naming its arm; note that arm and the train handle.
2. With that train selected and the game paused, press **slot 3**. Predict
   `SMRTK_ACTION action=slot_3 status=OK` with `new_idx` different from `old_idx`, `new_station` a
   station handle, `command_after=LoadTrain`. A `REFUSED` with "no other hub line with vanilla route
   room" means every other line is at `num_stations` trains: pick another parked train or another
   hub, and relay it.
3. Unpause at normal speed and watch the deck: predict the train leaves the siding, pivots at the
   centre when the new arm is 60° or 120° from its arrival arm (no pivot for the opposite arm), and
   runs out the **new** arm within about a fifth of an hour of game time (`LoadTrain`'s wait,
   `Train.lua:281`). Once it is off the deck press slot 3 again (it reads now): predict
   `command=GotoStation`, `track` equal to `dispatched_to_track`, `next_station` equal to
   `dispatched_to_station`, `on_dispatched_line=true`, `arrival_idx=nil`.
4. Let it arrive and turn around once. At the far station press slot 3: predict `station` equal to
   `dispatched_to_station` and `on_dispatched_line=true`. When it is next parked at the hub, press
   slot 3: predict `hub_idx` on the **new** line's arm pair and `on_dispatched_line=true`, and that
   it departs again on that line without a further dispatch.
5. Close the log and count the exact token `LUA ERROR`. Predict 0. **Stop conditions:** the train
   stands at the hub centre for more than a game hour, teleports, or vanilla stores it (the "A Train
   was stored" notification, `Train.lua:157-186`): keep the log and relay the train handle, arm
   pair and last slot read.

## Design sketch, if the sitting passes

**Hook.** One chained wrapper on `Train:LoadTrain` (declaring class `Train`, `Train.lua:230`), in a
new hub-module file. Before the vanilla body: if `current_station` is a hub, `at_station`, no
`assigned_resources`, no passengers, not `is_stopping`, ask the hub for a line; if it names one other
than the current, perform the placement order above without `Start()`, then call the body. That is
the decision point vanilla itself uses (`Start` → `LoadTrain`, `UnloadTrain` → `LoadTrain`); nothing
of vanilla is copied, and a train the hub leaves alone runs the untouched body.

**The need signal.** Per hub line (one route through the hub, found through the hub's connector
tracks and `train_track_routes`), per resource, over every station on that route except the hub plus
each one's off-hub children from brief 10's parent tree:
deliveries wanted = Σ max(branch_need, 0), capped by what the hub can actually supply (its supply
target); collections wanted = Σ max(−branch_need, 0), capped by hub room (its demand target).
The line's **need in loads** is that sum divided by `train.max_shared_storage`, rounded up. This
reuses the exact numbers brief 10's stops obey, so the dispatcher never sends a train the stop
arithmetic will then refuse. ⛔ It needs `branch_need` and `child_need` exported from
`40_TrainDistribution.lua` (a fenced file; a few lines, reported here, not edited).

**Release rule.** Score each line as need-in-loads minus trains already on its route
(`GetTrainsOnRoute`). A train at the hub moves to the highest-scoring other line only if that score
is at least one load better than its current line's and `track:CanAddVehicle()` holds; ties and
small differences keep the train where it is, so lines do not churn. A quiet line with zero need
keeps no resident train; when its need appears, the next train that finishes at the hub goes there,
serves it and returns, which is the owner's "topped up by an occasional train". A busy line
accumulates trains up to vanilla's route cap.

**How many trains a line may hold.** Vanilla's own cap, `num_stations` on the route (2 for a spoke
line, 3 with both arms attached), enforced through `AddTransportLink`. No new cap in the first
build; a per-line ceiling is an owner control for later if wanted.

**Chained lines that never touch the hub** keep their own trains by construction: the dispatcher
only touches trains standing at the hub and only tracks attached to the hub's connectors.

**Brief 10's forwarding.** Unchanged per stop. What changes is which train visits a hub line and how
often, so the chained legs (Metals reaching 2012 and 6243 through 2012, the untouched dial holding
at 10) must be witnessed again under dispatch. The per-stop floors, pins and the full-hub refusal are
dispatcher-independent (ruling 7).

**§4.9, trains the hub builds.** `ConstructTrainInternal` places a finished train only when exactly
one connected route has room, else it becomes a prefab (`Station.lua:589-607`). With the score above
the hub can call `track:AssignTrain(hub)` on the neediest line with room, which solves §4.9's
"placing" gap with the same signal. A train the player places on any hub line is dispatchable from
its first stop at the hub.

**Save rung (§4.8's ladder): 1.** The reassignment is vanilla-shaped state written through vanilla's
own primitive; a save loaded without the mod has the train serving whichever line it was last put
on, exactly as if the player had placed it there. The decision itself is computed per call, rung 0.
Optional per-line settings would live in the hub's existing table, rung 2, already accepted.

**Patch exposure.** One new wrapper (`Train:LoadTrain`), reads of `GetTrainsOnRoute`,
`CanAddVehicle`, `AddTransportLink`, `RemoveTransportLink`, `AssignToTrack`, and brief 10's exported
need; no body copy. Estimate, not a measurement: one file of roughly 150 to 250 lines plus a
five-line export in `40_TrainDistribution.lua`.

**What the owner sees and controls.** Nothing to set in the first build, in keeping with the
2026-09-26 ruling that the hub's card carries no controls: the visible effect is trains at the hub
leaving on different arms as lines need them. Two optional controls later, if wanted: a per-line
"keep N trains" number and a "do not dispatch" hold, both in the hub's table.

**Hazards the build must carry.** (a) Only empty trains are moved, else assigned cargo strands
(row 20); with ruling 6's hub-first dump in place most trains at the hub qualify. (b) A single-arm
line whose arm holds a parked train makes `LoadTrain:258` skip the reverse evaluation, so the
dispatcher skips lines whose only arm is occupied, as the probe does. (c) Hysteresis of one load
against churn. (d) Never exceed `CanAddVehicle`.

## Cost the owner can weigh (estimates, labelled)

- **Build:** one session at the desk (the wrapper, the score, a smoke on the archived bodies reusing
  `distribution_departure_smoke.py`'s doubles) plus one attended sitting. ESTIMATE.
- **What it forces re-testing in 5d:** the live legs that depend on line service and timing: chained
  Metals through 2012 to 6243, the untouched-dial hold on every spoke, and one sol at speed for
  `LUA ERROR`. Not re-tested: per-stop arithmetic (floors, pins, full-hub refusal), which ruling 7
  already separates.
- **What it does not cost:** no route-model change, no 5c, no movement change in `20_TrainHub.lua`
  (row 14), no new persisted name.

## Findings outside the fence (reported, not edited)

- `40_TrainDistribution.lua:326-350`: `branch_need` and `child_need` are `local`; the dispatcher
  needs them as `D.BranchNeed` / `D.ChildNeed`. Brief 10's file.
- `20_TrainHub.lua`: no change needed for dispatch. The other-line pivot path (`HubTurnPoint`)
  is exercised in normal play only by pass-throughs on opposite arms, so its first live use on the
  current centre-riding code is this prototype's step 3.

## Not claimed

- Not "the hub can dispatch": shown are the source chain above, the 3b measurement of forced
  60°/120° departures on the older movement code and game 1.1.0.403908, and a built prototype whose
  live result is owed.
- No cost above is a measurement.

## Close-out

Files: `tools/devmods/train_hub/Code/50_TrainHubDispatchProbe.lua` (new), `metadata.lua` (one code
entry), this report, spec §4.8 ruling 7 (one-line pointer); TestKit `Code/80_AgentSlots.lua` slot 3.
The session had no todo tool; the work list was kept in this report's sections instead. No
subagents. Executed model: Claude Fable 5.1 (`claude-fable-5-1`), as declared by this session.
