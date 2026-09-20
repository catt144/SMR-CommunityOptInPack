# Train hub build — design record, pre-boot predictions and sitting script

**Authority.** Owner rulings 2026-09-18, spec §10
(`TRAIN_LOGISTICS_DESIGN_20260917.md`); brief `docs/agent/prompts/TRAIN_HUB_BUILD_high.md`.
**Centre/transition prototype, 2026-09-20: implemented; owner smoke pending.**
`TRAIN_HUB_MOVE_high.md` owns the current movement. The lane-era build 3b results below are
historical; they do not validate this prototype. See §"Centre/transition prototype" below.
**Status: BUILD 3 SMOKE PASS.** The following original prediction block began at pack `886926b`,
TestKit `adda373`, parse-checked only
(`python tools/parsecheck.py --dir tools/devmods/train_hub/Code` → 2 files, 0 errors; TestKit 33
files, 0 errors). Every source line was read on 1.1.0.403908
(`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src`). Builds 1 and 3 were smoke-tested 2026-09-19 with
the owner; see §"Sitting result" and §"Build 3". The full battery was cut to a smoke test by
owner ruling (spec §10).

## Where the code lives, and why

A separate dev mod, `tools/devmods/train_hub/` (mod id `SMR_TrainHubDev_20260918`), not `Code/`.
- **The packaging Stop triggers for `Code/`.** `tools/upload_preflight.py:188-196` ("predicted
  pack holds only shipping files") admits only `Code/*.lua`, `metadata.lua`, `items.lua`,
  `LICENSE` and the preview image. It refuses `Data/BuildingTemplate/*.lua` and any entity folder
  as NON-SHIPPING. Its next guard, `:203-211`, lists `Code/` non-recursively, so a
  `Code/BuildingTemplate/*.generated.lua` named in `metadata.lua` fails as "listed but absent".
  The tool was not changed. **Owner decision owed** before the hub moves into the shipping mod.
- The module-off answer below is a proposal, not a ruling.

The class and field names are already the permanent ones, so the move is a file move plus
`SMROptInPack.Register`, a `Require` block for the three captures (`Train.TransferCargo`,
`GridConstructionController.Activate`, `ConstructionController.UpdateConstructionObstructors`)
and the toggle. The prototype under `tools/prototypes/train_hub/` is untouched; disable it for
the sitting.

**Deploy for a sitting** (the prototype's was a link of the same kind):
`cmd /c mklink /D "%APPDATA%\Surviving Mars Relaunched\Mods\SMR-TrainHubDev" C:\Dev\SMR-OptInPack\tools\devmods\train_hub`,
then enable "DEV ONLY - Train Hub (Module B build)" and disable "DEV ONLY - Train Hub Prototype".

## Structure and names

`SMROptInTrainHubBase` (`Station` + `DroneControl`; geometry, drones, reserve, cargo display) →
`SMROptInTrainHub6Base` (connector table `{0,3,1,4,2,5}`, `last_connector_idx = 6`) → template
`SMROptInTrainHub6`.

**Names that reach a save (ban 1), to join `FIX_POLICY` §"The persisted-name inventory" when the
hub first touches a kept save:**

| exact bytes | kind |
|---|---|
| `SMROptInTrainHub6` | template id, the placed object's class, a city label |
| `SMROptInTrainHub6Base` | the six's `object_class`, a city label, and the persist base |
| `SMROptInTrainHub6Base:SMROptInTrainHub6` | the object's persist key (`persist.lua:163-165`) |
| `SMROptInTrainHub4`, `SMROptInTrainHub4Base` | **RESERVED for the four-connector hub; not built** |
| `SMROptIn_floor_hold` | field on hub objects: `{ [res] = { req, amount } }` |

`persist_baseclass` is the object class, which is what the Mod Editor generates
(`Composite.lua:522-523`). The prototype's hand-written `"Station"` was not carried over: an
editor round-trip would have changed the key under a kept save. The four is
`hub_connector_directions = {0,3,1,4}`, `last_connector_idx = 4`, its own template and sitting.

**The asset swap is the template's `entity`.** Code asks the body first and computes only what
it lacks: connector spots (`Trackconnector1` on the body wins), the charging point
(`RechargeStationPlatform` auto-attaches win), cargo pallets (below). The coloured line markers
go when the body carries its own spots.

## Drone-controller spike: HOLDS from source (INFERRED, not run)

- Precedent is closer than the brief's: `ElevatorBase` is a Building with `DroneControl`
  (`Elevator.lua:561-590`); `DroneHubBase` is `TaskRequester` + `DroneControl` (`DroneHub.lua:1-2`).
- A member-by-member comparison of the two parent chains found these shared names. `Init`,
  `GameInit`, `Done`, `BuildingUpdate`, `OnSetWorking`, `OnDestroyed`, `AddToCityLabels` and
  `RemoveFromCityLabels` are combined methods (`Building.lua:1-12`, `CityObject.lua:8-9`), so both
  bodies run. `building_update_time`, `accept_requester_connects`, `OnPinClicked` and
  `GetSelectionRadiusScale` are not; the base pins each.
- `DroneControl:SpawnDrone` is an empty override point (`DroneControl.lua:725`). Drones are placed
  around the body as `SpawnDronesAround` does (`:244-255`), because the stand-in has no drone door.
- Charging: `AttachedRechargeStations.Init` (`AttachedRechargeStations.lua:2-29`) builds vanilla
  `NotBuildingRechargeStation` objects on the body's `RechargeStationPlatform` attaches. The
  stand-in has none, so one platform is attached on the first hex outside the footprint between
  lines 1 and 3. No new persisted class.
- Choices: 2 starting drones; work radius = longest line + 2 hexes (8 on the stand-in, whose
  radii were `5 6 5 4 4 4`); no range slider; no hub-only filter. **`CanCommandDrones` ignores
  malfunction**, unlike `DroneHub.lua:150-153`: a remote hub's drones exist to repair it.
- **Found on the way:** a template whose `object_class` is not `"Station"` never joins the
  `Station` label (`Building.lua:435-447`). Vanilla walks that label to free a train's platform
  (`Train.lua:94,134`), broadcast a resource toggle (`Station.lua:1023`) and route passengers.
  The hub now joins it. This is why the prototype's slot 1 read `hubs=0`.
- Not built: a drone section on the infopanel. `customDroneHub` is conditioned on `DroneHubBase`.

## Maintenance reserve

**Vanilla already pays a station's maintenance from its own stock:** `Station:SelfService`
(`Station.lua:493-511`) moves the maintenance resource from the supply request to the maintenance
request every update. A train cannot do the repair work that follows
(`RequiresMaintenance.lua` `StartWorkPhase`), which is what the hub's drones are for.

**The floor is a claim the hub holds on its own supply request.** `request:AssignUnit(amount)`
(`_TaskRequest.lua:391-392`) lowers `GetTargetAmount` and leaves the stock. `Train:TransferCargo`
reads the target at all three places that decide what leaves (`Train.lua:836-1020`: `available`,
`forbidden_excess`, the execution pass's `stored`), and the C-side task finder pairs drones
against it. So the held amount is invisible to trains, drones and shuttles, and stays in stock
and on the infopanel. **`TransferCargo` is wrapped, not replaced** (`FIX_POLICY` §1.4); a mid-body
edit would have been a §1.5 full replacement.

Hook points, all in `tools/devmods/train_hub/Code/`:
- `10_TrainFloor.lua` `Train:TransferCargo` wrapper: a station with no `GetTrainExportFloor`
  takes the first-line fast path. Otherwise it calls `UnloadAll` first, so cargo this train
  brings counts toward the floor, then tops up standing holds, or takes **transient** holds
  released after the call. The transient shape is Module A's trains-only export floor. No
  station asks for it yet, so it is **not exercised**.
- `20_TrainHub.lua` `GetTrainExportFloor(res)`: 2 × `maintenance_resource_amount` = 10 Metals,
  standing. `OnAfterRequestUpdate` (vanilla calls it after every stock change,
  `MultiResourceCubeVisuals.lua:434,454,466`) reconciles the hold. `BuildingUpdate`, while
  `maintenance_phase == "demand"`: release, call vanilla `SelfService`, hold again, with no yield.
- Module A generalises it by answering `GetTrainExportFloor(res)` per resource from its own field.

Known limits: a hold is forgotten, never released, if vanilla replaces the request
(`MultiResourceCubeVisuals.lua:395-399`); a debug build's task-request registry is bypassed by
calling `AssignUnit` directly.

## Storage and cargo display

`max_storage_per_resource = 240000`, one value in
`Data/BuildingTemplate/SMROptInTrainHub6.lua` (and its generated twin). **Capacity share:** the
balancer settles at capacity shares (§7.2 T2), so on a route of two 60-unit ends and the hub, the
hub holds 240/360 of that route's stock. A player will see it.

**The grid sizes itself.** `RecalculateDerivedMaxZ` (`MultiResourceDepot.lua:119-141`) sets
`max_z = ceil(max_storage / (min_columns × 1000))` from `GetTotalStorageColumns`, which is
pallets × `max_x` × `max_y` (12 × 5). Doubling storage doubles stack height on the same pallets.
Spot source: on the stand-in, vanilla's attached `StorageDepotFood` sub-models and their `Box1`
spot (`Station.lua:1214-1262`). For the asset, which has beds and no sub-models, the base reads
the body's own `Box1` spot range and turns each bed's grid to its spot. That branch cannot run
on the stand-in. Six beds would give 360 columns; at about 15 resources that is 24 columns and
`max_z` 10.

## Why the prototype read Metals `enabled=false` (from source)

`IsResourceEnabled` is "the demand request is not `rfSuspended`" (`MultiResourceDepot.lua:242-247`).
One writer sets that flag: `MultiResourceDepotBase:SetAcceptResource` (`:264-273`). Its callers
for a station are the storage row's click (`sectionStorageRow.generated.lua:43,50,55`) and the
`labels.Station` broadcast, which could not reach the prototype hub. INFERRED: the hub's own
Metals row was clicked. The sitting checks the new hub reads `en=true` untouched.

## Module off: proposal, owner to rule

**Off means no new hubs; built hubs keep working, reserve and drones included.** The classes and
the wrapper load whatever the toggle says, so a save with hubs always loads. The wrapper does
nothing at a station that is not a hub. The toggle only hides the template from the build menu,
by a preset patch (`FIX_POLICY` §1.1) that leaves nothing in the save. `MultipleSuns` already
ships this shape. **Removing the whole mod with hubs standing is not safe** and needs the drone
dials' kind of disclosure: demolish hubs first.

## Predictions, written before boot

Times are operator limits, not measurements. Stop on the first Lua error or unexpected taint.

1. **Boot — Scratch.** `status=OK`, `hub_class_loaded=true`, `floor_core_loaded=true`, log lines
   `[TrainHubDev] train export floor loaded` and `hub classes loaded`. Normal 10 s, abort 30 s.
2. **Placement across track (R2-a).** Dragging the ghost across existing track and placing on
   open ground leaves the error count at its boot value; the log has no `l_GetSpotBeginIndex`.
   Three coloured lines follow the ghost. Normal 30 s, abort 90 s.
3. **Slot 2 on the finished hub.** `connectors=6 in_footprint=6 direction_free=6
   valid_elements=6 in_station_label=true work_radius=8 valid_chargers=1`, `drones=2` within one
   game minute, `floor=10`, `errors` unchanged; `hub_cubes` shows `depot_submodels ≥ 1` and a
   `max_z` about twice a large station's. `serves_itself=true`. Normal 10 s, abort 30 s.
4. **Metals enabled.** Slot 2's station line reads `Metals=… en=true` with no row clicked.
5. **Cubes.** Slot 3 on the hub: `cubes_after − cubes_before = 60`, and stacks visibly rise.
   Slot 4: `hub_cubes_after=0`, stacks gone, `held=0 offered=0`.
6. **Slot 1 lists the hub.** `hubs=1 stations_missing_from_label=0`, three routes through it
   once six tracks and three trains exist.
7. **Crossing — slot 5.** After slot 4 then slot 3 at one line-1 end, the trigger fires with
   `crossing_route` = a route other than the source's, `crossing_out > other_in +
   crossing_own_in`, `reserve_took_by_train=0`. `wrap_floor_calls` rises. Normal six sols, abort
   eighteen. A save only costs a re-press: `rearms` and `blind_ms` rise.
8. **Waste Rock — slot 5 again.** Fires with `resource=WasteRock` and a positive `train_out`.
9. **Reserve — slot 6, first press.** `stock=10 held=10 offered=0`. With trains running and a
   Metals construction site inside the hub's radius, stock stays 10 and the site waits.
10. **Self-maintenance — slot 6, second press.** Fires with `stock_after=5`, `phases`
    `demand>work>false` (demand may be too brief to catch: `work>false` also passes),
    `own_worker` a drone, `foreign_worker=none`. Normal one sol, abort three.
11. **Reload working.** After a TestKit save and load: slot 2 repeats prediction 3's line with
    `valid_chargers=1`, the same drones, `held` = min(10, stock); trains still stop; error count
    unchanged.
12. **Teardown.** Vanilla salvage with tracks and trains attached: 0 Lua errors, six clean track
    ends, drones orphaned or adopted, no charger left standing.

## Sitting script

The orchestrator relays one batch at a time. Drones stay on. Do not save while a witness is
armed unless the step says so.

**Batch 1 — boot and place.**
1. Create the link above, start the game, enable the dev mod, disable the prototype mod, load
   `Japan Sol 490` (or a fresh colony). Pass: it loads with no error dialog.
2. Agent tab → Scratch. Pass: prediction 1. Send back: nothing; the log has it.
3. Open the build menu → Stations → "Train Hub". Drag the ghost across an existing track, then
   over open flat ground at least 10 hexes from any station. Pass: three coloured lines follow
   the ghost and the status bar's error count does not move. Send back: a screenshot of the ghost.
4. Place it and complete it (World → completion). If there is no power near it, select it and
   use Selected → More → `NoConsumption`. Pass: it finishes and stands working.
5. Select the hub → slot 2. Pass: prediction 3 and 4. Send back: whether two drones are standing
   by it and whether a charging pad is visible outside the body between the red and green lines.

**Batch 2 — cargo on show, tracks, trains.**
6. Hub selected → slot 3. Pass: stacks rise on the hub's pallets. Send back: a screenshot, and
   whether the stacks poke through the roof.
7. Slot 4. Pass: the stacks vanish.
8. Build six end stations, each 10+ hexes from the hub, and one track from each coloured end
   (click the arrow hex). Reusing sitting 2's six lines is fine if they still stand.
9. One train per line (select an end station and use its Spawn Train cheat, or assign prefabs).
10. Slot 1. Pass: prediction 6. Send back: nothing.

**Batch 3 — crossing and Waste Rock.**
11. Slot 4, then select ONE end station on the red line → slot 3.
12. Slot 5. The game runs until the witness pauses it. If an autosave disarms it (armed count
    drops to 0), press slot 5 again. Pass: prediction 7. Send back: the sol it paused on.
13. Slot 5 again. Pass: prediction 8. If nothing fires in six sols, press Cancel target and say so.
14. Slot 1. Send back: nothing.

**Batch 4 — reserve and self-maintenance.**
15. Select the hub → slot 6 (first press). Pass: prediction 9's numbers.
16. Place any building that costs Metals within two hexes of the hub's edge and leave it
    unbuilt. Run two sols at speed. Pass: the site still waits for Metals and the hub still
    shows 10. Send back: what the site shows. Then slot 3 on the hub. Pass: the site gets built
    and the hub never shows less than 10.
17. **Pause the game.** Slot 4, select the hub → slot 6 twice (prime, then maintain); the
    second press unpauses by itself. Pass: prediction 10. Send
    back: whether a hub drone was seen working on the hub.

**Batch 5 — reload and teardown.**
18. With trains running and cargo in the hub, Saves → Save A, then Load A.
19. Select the hub → slot 2, then slot 1. Pass: prediction 11.
20. Run one sol. Pass: trains still stop at the hub; error count unchanged.
21. Salvage the hub with everything attached. Pass: prediction 12. Send back: a screenshot.
22. Sitting → Flush + copy; Read taint; Read eligibility.

## Sitting result, 2026-09-19 (MEASURED; one colony)

Log `Mars.exe-20260918-23.44.18-6a91a190.log`; game 403908, pack `886926b`, TestKit source
`7cd3504`; save `SpaceY Sol 20` (all research done), sols 22–46; mods: fix pack, TestKit, this
mod, the dev hub (prototype off). The owner placed and wired the hub before the sitting, onto an
existing network: two routes, not three, one of which passes the hub twice.

| # | result |
|---|---|
| 1 | PASS: both `[TrainHubDev]` lines; Scratch `status=OK hub_class_loaded=true floor_core_loaded=true` |
| 2 | PASS on the owner's screenshot: three line markers follow the ghost; no `GetSpotBeginIndex` in the log |
| 3 | PASS: `connectors=6 in_footprint=6 direction_free=6 valid_elements=6 connected_tracks=6 in_station_label=true work_radius=8 valid_chargers=1 drones=2 serves_itself=true errors=0`, `depot_submodels=10 max_z=8`. `floor=7`, not 10: Building Codes' 30% cut makes a maintenance 3.5 Metals (owner's screenshot); the prediction's fixed 10 was wrong |
| 4 | PASS: `Metals=… en=true` unclicked |
| 5 | PASS: slot 3 `cubes_before=117 cubes_after=177`; slot 4 `177 → 0`, `held=0 offered=0` |
| 6 | PASS for `hubs=1 stations_missing_from_label=0`; 2 routes, from the network's layout |
| 7 | NOT PROVED by the witness; see below. The ledger shows R2 `train_out=4`, `train_in=0` |
| 8, 9 | not run (smoke test) |
| 10 | SEEN unprompted: `last_serviced` moved to 31723108, points to 2200, hub stock fell by exactly 3.5 unexplained, `reserve_took_by_train=0`. The ledger's `maintenance_paid` stayed 0: it missed the phase change |
| 11 | PASS: after Save A / Load A, slot 2 identical to before the save |
| 12 | PASS for `hubs=0 errors=0`, six end stations intact. `trains` fell 4 → 1: the three docked at the hub went with it. Unknown whether vanilla does the same for a docked station |

**Findings for the next build:**
- **The crossing witness cannot prove a crossing here** (TestKit, not the hub). In a gap-free
  run (`blind_ms=0`) it still booked `other_in=74` Metals against `train_in R1=71`, so R2's 4 out
  never exceeded it. It appears to miss train unloads at ultra speed. Autosaves, which the game
  cannot turn off, add more unexplained stock. It needs fixing before the final build's battery.
- **Drones showing "Controlled by: None" near the hub**: unresolved. The hub kept
  `drones=2` throughout; the owner had cheat-deleted `DroneHub(1986)` just before, orphaning its
  drones. Check on the next build.
- Idle trains park at the hub once the network balances; three sat there at once.
- Seen in passing, not this mod's: `MarsDebug.exe-20260919-02.26.52-6a91a1cb.log:189`
  `[LUA ERROR] Failed to load items.lua for mod Community Fix Pack — Test Kit` (the Mod Editor
  session). The TestKit is the fix pack's; told to the owner 2026-09-19, not filed there.

## Build 2, 2026-09-19 (PRE-BOOT)

**Authority.** The owner's 2026-09-19 sitting rulings in spec §10: radius 10; build the tentative
slider to 20 if it needs no unjustified persisted field; show drone count, load and service area;
smoke-test this design pass. The imported `SMROptInTrainHub6` asset is present.

**Build calls.** The slider is built, from 10 through 20. It uses vanilla `work_radius`, already a
persisted `DroneNode` template property, and vanilla's non-saving `UIWorkRadius` mirror; it adds no
persisted name. A hub saved by build 1 at radius 8 is raised to the new minimum 10 on load. Later
slider choices inside 10–20 survive through `work_radius`.

The infopanel keeps vanilla's `sectionServiceArea` and slider by setting `show_service_area = true`.
Its custom section reuses the vanilla Drone Hub translations and presentation for count and load;
it omits prefab controls and ordered-drone text, which this hub does not implement.

The editable BuildingTemplate source now names entity `SMROptInTrainHub6`. Its generated companion
still names the stand-in until the next Mod Editor save, so a `ClassesPostprocess` bridge applies the
source value in this dev build without editing generated output. The asset's six connector and six
direction spots win individually. `Ramparrive`, `Stop`, `Spawn` and `Rampdepart`, which the import
lacks, stay synthetic; construction `Sign` spots stay absent. The six body `Box1` spots select the
previously unrun body-pallet cube branch. The charger remains the code-created vanilla pad.

**Desktop gates, MEASURED before boot.** `python tools/parsecheck.py --dir
tools/devmods/train_hub/Code` read 3 listed Lua files and returned 0 errors. `python
C:/Dev/SMR-OptInPack/tools/parsecheck.py --dir Code`, from the TestKit repo, read 33 listed Lua
files and returned 0 errors. The stale-probe command
`C:\Program Files\Git\usr\bin\grep.exe -rln TEMPORARY Code/
../SMR-BugFixPack-TestKit/Code/ tools/devmods/train_hub/Code/` returned 0 hits, exit 1. TestKit
`80_AgentSlots.lua` now carries only this smoke: asset/tracks/trains, drone UI/radius, fill and empty
every live station resource, a staged vanilla-station salvage witness, the dome link, and boot.

The decoded `Entities/SMROptInTrainHub6.entjson` spot sweep was also measured. `rg -n
'Ramparrive|Rampdepart|Stop|Spawn|Sign'` returned 0 hits, exit 1. The positive-side `rg -o` filter
for `idle|Box1|Top|Trackconnector[1-6]|Trackdirection[1-6]|Workdrone` returned 26 hits, reconciled
as 1 idle + 6 Box1 + 1 Top + 6 connectors + 6 directions + 6 Workdrone = 26. This proves what the
Lua must source from the body and what it must continue to synthesize; it does not prove the spots'
runtime alignment.

### Build 2 smoke — predictions and sitting script

Stop on the first Lua error. Stop the asset swap if its connector axes or deck height do not meet
the tracks. Times below are operator limits, not measurements.

**Batch 1 — boot, place, UI (about five steps).** Start one colony of the owner's choice with both
packs, TestKit and the dev hub enabled. Scratch: both dev-mod load lines, both class flags true,
eligibility `UNAVAILABLE:sandbox`, and no Lua error (10 s normal, 30 s abort). Place and complete a
fresh hub: imported body, six portals on the hex axes, track deck meeting each stub. Select it and
run slot 1: entity `SMROptInTrainHub6`, six real connectors and directions, 24 synthetic operating
spots, six `Box1` spots, radius 10, two drones, 0 errors. The infopanel visibly shows drone count,
load and service area; a nearby drone visibly says `Controlled by: Train Hub`. Move the slider to
20, run slot 2, then return it to 10 and run slot 2 again; `work_radius`, `UIWorkRadius` and the
selection ring agree (5 s normal, 15 s abort at each end).

**Batch 2 — six lines, cargo and dome.** Attach all six ends to six vanilla end stations and put a
train on every line. Let trains stop at the hub, then slot 1 reads six connected tracks, at least
one train at the hub and no error. Slot 3 fills every resource the station exposes; send a
screenshot and inspect every bed against the ring and hoods. Slot 4 empties it; the cubes disappear.
Place or use a populated dome inside station range, select it and run slot 6: reciprocal hub link
and at least one hub route. Watch one colonist board from that dome; the model has no door by owner
ruling (10 s normal, 30 s abort for each slot).

**Batch 3 — reload and teardown.** Put the slider at 20, save and reload. Scratch then slots 1 and 2:
the asset, six connections, trains, drones and radius 20 remain, with no error; return the slider to
10. With a train stopped at a vanilla station, run slot 5, salvage that station through vanilla UI,
then run slot 5 again: station invalid, every snapshotted docked train invalid, error delta 0. With
trains stopped at the hub, salvage the hub: trains at it disappear, six end stations remain, 0 Lua
errors. End with Flush + copy, Read taint and Read eligibility.

**Status:** READY FOR OWNER SMOKE. Nothing in this section claims an in-game pass yet.

## Build 3, 2026-09-19 (SMOKE PASS; one colony)

**Rig and evidence.** Game 1.1.0.403908, save `SpaceY Sol 23`, with the opt-in mod, fix pack,
TestKit and train-hub dev mod loaded. The closing evidence is
`Mars.exe-20260919-20.33.45-6a91a190.log`, slot 1 ids 116/121 and slot 2 ids 124/127 after the
save/load at lines 504-554. The only Lua error in the process was the already-known Mod Editor
boot error at `CommonLua/Editor/ArtSpecEditor.lua:573`; the hub slots reported `errors=0`.

**Asset and attachment.** The final import is `5002a49`, on the textured import `d07a457`: 66
outline hexes (61 for the ring and five for the reactor lobe), a 0.9 inset, the inner pillar ring
cut, and cargo spots aimed onto the six beds. All six live line radii were 4; after the owner
reconnected one incomplete track, `connected_tracks=6`, `grid_connected_stations=6` and
`grid_mismatches=0`. The obsolete untracked `shrink_footprint_probe.py` was deleted. `Textures/`
and `Fallbacks/` remain deliberately ignored and were not committed.

**Height and width, measured only:**

| measurement | game units |
|---|---:|
| vanilla running-surface z | 10800 |
| connector z | 10800 |
| stub top z | 10800 |
| vanilla element x width | 1000 |
| vanilla element y width | 204 |

These track/stub measurements caused no Lua change. `6123ae7` was the separate, already-committed
synthetic train-spot deck correction.

**Power.** The regenerated template no longer contains duplicate electricity declarations, while
`20_TrainHub.lua` still supplied `power_production=70000` and `power_consumption=10000`. The merged
fixture grid read 140000 produced, 55000 consumed and 85000 wasted. Its other production was seven
Stirling Generators at 10000 each. It contained no cable elements (`grid_reaches_cables=false`),
so this sitting proves the hub's surplus reaches the six merged station grids, not colony cables.
If one of those merged grids also contains a cable element, the same shared grid carries the
surplus to it; that conditional was not exercised here.

**Drones and UI.** The prefab-button/custom-section attempt and the radius slider were removed.
The hub held a fixed work, UI and selection radius of 15 with one range overlay; its Power grid
section was absent. Two hub-controlled drones worked for the owner with no charger, and each read
`battery_max=8000000`, `battery=8000000`. The only object on the old charging spot was one
non-selectable `RechargeStationPlatform`, two hexes away, retained as build 4's launch-pad model.
The 75% `FusionReactor` visual remained at offset `(3897,2250,0)`; it is visual only, while the hub
is the grid producer.

**Storage and the 19/21 count.** The source and editor-generated template both use
`max_storage_per_resource=150000`. Slot 3 filled 19 request-backed resources from 1879 to 2850
cubes, 150 per resource, with `max_z=9`; the owner reported no beam or portal-train clipping. The
21 count is the nominal `storable_resources`/`TransportableResourceIds` list. `BlackCube` and
`MysteryResource` were the two absent request types. Vanilla creates requests only for a resource
whose preset is enabled (`MultiResourceDepot.lua:409-412`, game build 1.1.0.403908), so 19 is the
live storage contract for this colony and 21 is the candidate list, not a conflicting cube count.

**Reload.** With the hub full, save/load preserved 66 hexes, six connections, all six merged
station grids, the 2850 cubes, +70/-10 hub power, two full hub drones, no charger, the launch-pad
model, fixed radius 15 and one overlay. The owner visually cleared the overlay, drone work and
full-stack clearance. No fresh salvage leg was run in build 3. Train arrival/departure behaviour is
deliberately not fixed here. The four established current cases transfer unchanged to build 3b:

- arrival/load uses the exposed synthetic interior move;
- straight-through departure crosses the open interior;
- another-line departure visibly slides or shifts toward that portal;
- same-arrival-track departure jumps to the far side, then floats back.

The owner moved their full rework to `TRAIN_HUB_TRAINS_high.md` (build 3b).

**Verdict:** build 3's smoke passed. Build 3b is released; build 4 remains held behind it.

## Build 3b, 2026-09-20

**Authority:** `TRAIN_HUB_TRAINS_high.md`; the owner additionally authorised unattended game
launches and save loads in this session, then specified the newest manual save because older
fixtures contain an incompatible mesh. Baseline: `SpaceY Sol 21.savegame.sav`, modified
2026-09-20 03:27:33 local, selected with `Get-ChildItem` on the fix pack's `saves/game/` junction,
sorted by `LastWriteTime`. Task-created mid-crossing saves are separate files. Existing saves
were copied before launch to `%TEMP%/SMRTrainHub3b-20260920-035736/`.

**Implemented, not an owner's visual acceptance:** corrected connector table `{4,1,3,0,2,5}`;
`SMROptInTrainFloor.HubParkDistance` is **20 m**; track-step-derived
arrival/departure lanes; own-line reservations; a saved crossing owner; lane-intersection
waypoints with a timed centre turn. Same-line Spawn equals Stop and faces outward; reversal
then follows a smooth lateral join to the departure lane instead of teleporting between lanes.
That short lane join and the centre pivot still need the owner's judgement. No mesh or scaling
change, no Train method replacement, no routing-graph or economy change.

**Parking choice (visual, provisional):** compared 17, 20 and 23 m with the native hex overlay,
paused on the same stopped train. At 17 m its nose sat closer to the crossing; 23 m hid more of
the cargo tail behind the portal. Chose 20 m for the owner's review. Native screenshots
`C:/Dev/SMR-ScreenCaptures/SMRTK_0054.png`, `0055.png`, `0056.png` show those positions;
the adjusted train is upper-left, not the legacy traversal paused lower-right. Their hashes,
labels and source logs are in the native evidence manifest below. R-TRAIN stays disputed;
the clean parts/grid read is in `GEOMETRY_ORACLE_20260919.md` §13.

**Reservation contract (SOURCE, archived 1.1.0.403908):** `Train.lua:258` must see its own
reverse platform free, so only its own `LoadTrain` thread is exempted from its reservation.
`Track.lua:433,453` still blocks spawning on an occupied Stop/Spawn. Arrival checks at
`Train.lua:621` and recovery at `Tracks.lua:995,1017` see the own-line reservation. Cleanup at
`Train.lua:95,136` reaches the hub override. `Train.lua:823-835` declares `ChangePlatform`;
`rg -n 'ChangePlatform\(' C:/Dev/SMR-SrcArchive/1.1.0.403908/Src -g '*.lua'` returned that
declaration alone (RAN this session). Old opposite-key reservations are rebuilt from the train's
arrival connector, not checked against a moved Spawn position. The crossing waits for an
in-progress arrival and blocks new arrivals while occupied. A stopped train on the incoming
lane also blocks a pass-through; if the owner's fixture exposes that stop condition, the brief's
through-waits-versus-moving-the-stop decision remains theirs.

Load migration moves only genuinely parked trains to the new Stop/Spawn before showing the
colony. It recognises `trains_traversing` from saved vanilla frames and waits for their existing
release. A departing parked train remains `at_station` while waiting for the crossing and its
outgoing track. A new pass-through assigns its outgoing track before its first movement yield;
otherwise a parked departure could take that exit while the through train was crossing.

**Save contract:** `SMROptIn_hub_crossing`, a Train reference, is in `FIX_POLICY`'s inventory.
An interrupted valid train keeps the lock until existing cleanup removes it; an interrupted
thread does not prove an empty crossing. The bounded movement frames are a content residual;
removal with hubs standing remains unsupported. The tunable resets at boot; choose its lasting
value in Lua after the visual sitting.

**Desktop check:** `python tools/devmods/train_hub/tests/traffic_smoke.py` executes the actual
hub methods and archived vanilla arrival/GotoSpot bodies against mocked native geometry and
time. It checks rotated hubs, both track start/end orders, arrival lanes, reverse eligibility,
spawn exclusion, old reservation keys, park retuning, exclusive acquisition, interruption,
release and invalid-object cleanup. Its route records feed the unchanged oracle's `_two_train`
method. This is a width-only spatial prediction; the oracle CLI still models the old single
slide and cannot interpret these routes. No claim of native interpolation, mesh clearance,
train length or a physical save test follows from this desktop check.

**RAN:** `python tools/devmods/train_hub/tests/traffic_smoke.py --output
docs/archive/TRAIN_HUB_3B_TRAFFIC_20260920.json` at HEAD `3071a9a` plus the recorded source
hashes. [Result and members](../../archive/TRAIN_HUB_3B_TRAFFIC_20260920.json): 72 lane/reservation
cases (6 rotations × 2 start/end orders × 6 connectors), 66 executed routes (36 departures +
30 pass-throughs), concurrency assertions passed. TWO-TRAIN compared 1995 eligible route pairs:
1320 within the 416-unit width + 675 clear. Each pair is enumerated; same-arrival alternatives
are excluded as in the unchanged oracle. This establishes why the lock matters, not that two
physical meshes never touch. No disputed train length enters this calculation.

**Native smoke, game 1.1.0.403908, both packs loaded, final 20 m code:**

| case | evidence | result |
|---|---|---|
| straight, connector 2 → 1 | [04.27.01 log](../../archive/TRAIN_HUB_3B_Mars.exe-20260920-04.27.01-6a91a190.log), stage 1 | departure completes; correct outgoing track; lock released |
| 60° line, connector 2 → 5 | [04.22.55 log](../../archive/TRAIN_HUB_3B_Mars.exe-20260920-04.22.55-6a91a190.log), stage 2 | departure completes after crossing save/reload |
| 120° line, connector 2 → 3 | same log, stage 3 | departure completes; correct outgoing track; lock released |
| reverse, connector 2 → 2 | same log, stage 4 | waits for prior traffic, then completes; lock released |
| parked + crossing save/reload | same log, `RELOAD_LOCK_OK`, `RELOAD_PARKED_OK` | crossing train `2000001576` and parked train `2000001577` preserved; crossing resumes and releases |

These are forced native-command geometry fixtures: slot 3 assigns an outgoing track and starts
vanilla `GotoStation`. The save leg also holds a parked train in native `Idle` and uses native
`AssignTrain` to create a spare on a free hub line (one prefab supplied only if needed). Those
setup mutations are logged; they do not establish automatic destination choice or throughput.
The old-save traverser is allowed to finish before that spare setup. Every leg reloads the
newest owner manual save; the save test writes `Hub3bSmoke_MID_1789892612.savegame.sav` separately.
The earlier 17 m natural-traffic leg observed an arrival and straight departure; it is historical
evidence, not a final-20-m visual pass. Other connectors have desktop coverage only.

**Evidence and cleanup:** `python tools/devmods/train_hub/tests/record_evidence.py` ran after
exit, at HEAD `3071a9a`, and produced the [native manifest](../../archive/TRAIN_HUB_3B_NATIVE_20260920.json).
It archives 8 logs (members and SHA-256s listed), hashes 55 native screenshots (local originals,
not checked-in binaries), and compares every backed-up original `*.sav`: **56/56 unchanged**.
The final two logs each contain only the already-known startup `ArtSpecEditor.lua:573` error;
no new runtime error, and every final stage's `RESULT` is true. Earlier diagnostic failures are
retained: nil-Z formatting in the first slot read; a caught `HexGridRender.lua:44` failure after
loading a save while a procedural grid was still active. The slots now format nil Z; the driver
restores the grid after each screenshot. These were diagnostic failures, not passing legs.
The manifest's error list counts `[LUA ERROR]` lines; caught driver failures remain in `RESULT`.

Temporary drivers are disarmed with `arm_leg.ps1 -Mode disarm`; shared TestKit metadata is
restored exactly. Only its prepared `80_AgentSlots.lua` remains changed, matching the inert
source under `tools/devmods/train_hub/tests/`. No TestKit commit was made from this pack lane.
The parked smoke driver currently runs stage 1; the final other-line/save leg used `{2,3,4}`
in its Boot loop, with the same hub code. Drivers remain inert outside an explicitly armed run.

Final desktop gates: dev-hub parse, shipping parse and shared-TestKit parse passed; doccheck
GREEN in both repos. `rg -n 'TEMPORARY' Code C:/Dev/SMR-BugFixPack-TestKit/Code
tools/devmods/train_hub/Code` returned no matches with those installed source paths present.
The unchanged whole-CRLF archive warnings remain; archives are append-only. The prepared slots
remain intentionally uncommitted in the shared TestKit, with their source committed here.
Opt-In doccheck warnings after staging, verbatim (the new manifest also retains Windows EOL):

```text
  WARN docs/archive/TRAIN_HUB_3B_NATIVE_20260920.json
  WARN docs/archive/train_hub_gate_20260920.json
  WARN docs/archive/train_hub_gate_baseline_20260920.json
  WARN  M Code/80_AgentSlots.lua
```

Raw log whitespace is retained. Manifest SHA-256s describe the original log bytes; Git's text
attributes normalise CRLF on storage. `git diff --cached --check` is clean for authored code
and documents when raw `docs/archive/*.log` evidence is excluded.

**Owner controls, installed in the shared TestKit's `80_AgentSlots.lua`:** 1 reads lanes and
traffic; 2 moves parked trains 1 m inward; 5 moves them 1 m outward; 3 sends the selected parked
train straight / by a 60° line / by a 120° line / back along its incoming line on successive
successful presses; 4 arms a pause at the next crossing; 6 reads the selected train and every
attached part; Scratch reads boot, taint and eligibility. Parking setup requires pause and a
single hub; it explicitly repositions parked trains. Departure setup assigns the requested
outgoing track and starts vanilla `GotoStation`. It is a geometry fixture, not an economy or
route-balancing test. Autosave disarms the crossing watch; re-press slot 4 afterwards.

**Owner sitting, first batch:** start the game and load the newest owner manual save, not a
task-created `Hub3bSmoke_MID` save. The Slots & notes tab is ready.

1. Pause, select the hub and run Scratch, then slot 1. Inspect the stopped train at 20 m.
2. Use 2/5 to tune inward/outward if needed; judge the train against the hex grid, then slot 6.
3. Run slot 3 for straight departure; watch the deck and portal join from ground level.
4. With a parked train ready, successive slot-3 runs cover 60° and 120° exits; judge whether the
   timed pivot reads as a train turning. Then try the reverse and its short lane join.
5. Watch two arrivals/through trains together and the outside queue. Slot 4 pauses on the next
   crossing; re-arm after autosave. Record visible contact, crabbing or a blocked-through case.

**Remaining:** the owner's parked position, turn/portal judgement and queue appearance. The
parked-plus-crossing save/load is mechanically passed above; revisit it if visual work changes
the movement. A source/offline pass does not meet the brief's visual done-condition. The
fix-pack owner list carries this sitting; Build 4 stays held.
The one-off prompt stays live until that smoke is recorded. Executed model: GPT-6 (Codex), as
identified by this session's instructions; no more specific runtime model id is supplied.
No subagents were used.

**Owner sitting, 2026-09-20 (first batch, steps 1-3 only; orchestrator's read of a live, partial
log).** `Mars.exe-20260920-12.02.29-6a91a190.log`, save `SpaceY Sol 21` at sol 22, game 403908, both
packs, the TestKit and the dev mod; one Lua error, the known startup `ArtSpecEditor.lua:573`. Slot 2
was pressed seven times and slot 5 never: park distance 2000 to 1300, so **13 m by the owner's eye**
(*"that seems about right to me?"*), a runtime value that resets at boot. Slot 6 on
`Train(2000001573)` read `TrainCCP3` bbox x -1332 to 2818 with two `PointLight` attaches only;
its verdict stayed DISPUTED and the owner's hex measurement governs. **By eye the parked train was
"technically on the line but most of it hanging off the line"**: it rides the 289-unit lane and the
deck is on the centreline. Steps 4-5 (departures, turns, reverse, queue) were **not run**: the owner
redirected the design to centre riding with a transition at the stub (spec §9) and ruled the method
quick and iterative. The lane build is therefore mechanically passed and visually unaccepted, and
13 m is a lane-era figure to be judged again on the centre.

## Centre/transition prototype, 2026-09-20

**Authority:** `TRAIN_HUB_MOVE_high.md`, owner 2026-09-20: function before texture, centre
riding inside, stop on the arm then slide sideways, mirror on exit, tune by eye. Started from
HEAD `293f92c674e1964429ca6aa00d7e0ff6bfd69bb8`. The entity, mesh and dev metadata were already
modified at task start; this change does not author or commit them. The installed dev-mod
link resolves to this workspace. No oracle or prediction battery was run.

**Implemented, not visually accepted:** `HubTransitionPauseDistance = 45 * guim` is a
provisional distance from the centre, not a train-length calculation. `HubParkDistance =
13 * guim` carries the owner's lane-era starting value onto the centre for a new judgement.
Both reset at a full restart. `Ramparrive` and `Rampdepart` remain on the connected vanilla
lane; `Stop`, `Spawn`, the interior run and pivot are centred. Hub-local `TrainArrive` stops
on the arm, follows the previous normalized smoothstep sideways with fixed rail-facing yaw,
then runs to Stop. Departure reverses that sequence. Through trains use the same transitions.
Stop-to-stop runs accelerate to an intermediate point and brake to their destination; they
do not ask the constant-acceleration solver to move between two zero velocities. The slide
uses game-time interpolation. No `Train.lua` wrap or additional persisted state was added.

**Reservations:** arrival owns the existing crossing lock until parked. A pending inbound
reservation also keeps another arrival outside; parking retains its own-line reservation.
The existing own-LoadTrain-thread exemption and spawn exclusion remain. Other-line motion
pivots at the centre; the same-line reverse flips in place. Saved movement frames remain the
previously accepted content residual. A stopped-plus-crossing reload of this version is owed.

**Cold start:** creation, load and the hub's `SetWorking` synchronize production from
`ui_working`, malfunction and destruction, independently of grid availability. Calling the
base setter first preserves all combined callbacks; synchronizing even when working stays
false observes switching off and malfunction while unpowered. The modifiable-value callback
also restores this gate after the parent's update. SOURCE: archived 1.1.0.403908,
`Lua/Buildings/BaseBuilding.lua:434-467`, `Lua/ElectricityProducer.lua:27-28,64-67`,
`Lua/Modifiers.lua:20-26`. Output and consumption amounts are unchanged. Native cold start
without the fixture's Stirling supply has not been run.

**RAN at the authoring HEAD above, with the working diff:**
`python tools/devmods/train_hub/tests/move_smoke.py` passed mocked arrival/queue/reservation,
reverse exit, other-line traversal and cold-start/off/malfunction control flow. It reuses the
old smoke's engine stubs at the current connector radius without invoking its oracle or
case sweep. `python tools/parsecheck.py --dir tools/devmods/train_hub/Code` and
`python tools/parsecheck.py --dir C:/Dev/SMR-BugFixPack-TestKit/Code` passed. These checks do not
show native interpolation, cargo loading, serialization or visual clearance. The old
`traffic_smoke.py` executable checks lane-era expectations and is not this version's gate.
`python tools/doccheck.py` is GREEN in both pack repositories. The fix-pack owner item ck206
and its sitting pointer now lead to this prototype and preserve the remaining native checks.

**Prepared owner smoke, first batch (in progress):** restart the game with the dev hub and shared
TestKit enabled; use the current owner fixture, not a `Hub3bSmoke_MID` save. The manual saves
`train_hub_base` and `train_hub_base_agent` were present in `C:/Dev/SMR-BugFixPack/saves/game`
when listed by modification time this session. Shared `80_AgentSlots.lua` matches the source
in this repo's tests folder; no driver is armed at load. The shared file remains uncommitted
in the TestKit, as before. All setup actions are logged.

1. Pause, select the hub, run Scratch and slot 1; inspect the centreline park at 13 m.
2. Slot 6 switches the tuning target between pause and park (starts on pause). Slots 2/5
   subtract/add 1 m. Park tuning repositions parked trains; pause tuning affects the next
   trip. Tune only while paused with no arriving or crossing train.
3. Watch an arrival at normal speed: tail clears vanilla, stop, sideways slide, inward run.
   Report the pause distance and whether the tail clears too early or too late.
4. Watch loading at Stop, then slot 3's first successful press sends a straight departure.
   Watch its centre run, outward slide and return to vanilla's lane.
5. Repeat the cycle at fast and fastest. Report the visible result before the next batch.

**Owner visual feedback, 2026-09-20:** the owner reports the movement stops about 1.5-2 hexes
too late and supplied a screenshot showing the train at the portal. The initial 30 m pause
is rejected by eye; the next trial moves the pause outward to 45 m (15 m earlier on arrival).
This is a tunable trial, not a measured correction or accepted tail-clearance position.
The current game's value can be moved with slot 5 while pause tuning is selected; slot 1
reads the actual value. Park remains 13 m. This also moves the mirrored exit slide outward.

**Exit contact and scope ruling, 2026-09-20:** the owner supplied screenshots of trains
driving into each other on exit and requested waiting outside when the intended exit lane
is occupied, while permitting a train to load and return along its own line. After the
loading-direction question, the owner instructed: "continue with your movement based work,
and wrap it up the best you can. Then I am going to make some changes for the next pass for
loading / queueing". Full queueing/loading policy is therefore deferred to that owner pass.

**Movement guard implemented:** `HubExitClear` checks the hub's own-line reservation as well
as vanilla's outgoing-track exclusion. Both through admission and crossing acquisition use
it. A train's own reservation permits a same-line reverse; a different parked train blocks
the exit. Through trains wait at vanilla's outside endpoint before hub movement, not at a
new queue position on the arm. Already-loaded departures wait at their existing park.
This is an occupied-exit guard, not FIFO scheduling or a loading-intent decision. No new
saved queue or `Train.lua` wrap is installed. SOURCE: archived 1.1.0.403908,
`Lua/Buildings/Track.lua:357-365` deliberately excludes parked trains; `Lua/Units/Train.lua:238-261`
chooses a stopping train's onward/reverse work during loading. INFERRED limitation: mutually
blocked loaded departures can remain waiting; how to resolve them belongs to the next policy pass.

**Flushed evidence:** copied the live file (partial, game still running) to
[`train_hub_move_queue_partial_20260920_183901.log`](../../archive/train_hub_move_queue_partial_20260920_183901.log)
using `Copy-Item` from `%APPDATA%/Surviving Mars Relaunched/logs/Mars.exe-20260920-18.39.01-6a91a190.log`.
`Get-FileHash` SHA-256: `74EB003DB1D79DE907B3B74BEE050A8970F013E6D9C6E86C758ECC11CF9C78EA`.
The `SMRTK_FINGERPRINT` at id 109 names game 403908, `train_hub_base`, both packs and the kit/dev hub.
The last successful tuning record, id 124, sets pause to 3700; id 129 records the successful flush.
Thus the live session had not yet reached the 45 m trial. The earlier tuning refusals explicitly
say the crossing was occupied. The log's traffic dump predates the screenshot report and does not
identify the colliding pair; the owner's screenshots and report are the visual evidence.

**RAN with the guard diff on HEAD `a657e6447067bc0261caaaac9ebee3634f87a824`:**
`python tools/devmods/train_hub/tests/move_smoke.py` passes the existing movement/power checks
and the regression reproducing vanilla's parked exemption, blocked through admission, waiting
without moving or claiming the crossing, the blocker's own-line reverse, continued exclusion
while it is on the outgoing track, and release when that track clears.
`python tools/parsecheck.py --dir tools/devmods/train_hub/Code` passes. Native visual acceptance
of this guard is still owed; the test uses mocked movement and simulates the far-end arrival.

**Still owed:** owner acceptance of those movements and both distances; subsequent slot-3
60°/120°/reverse departures; two-train outside waiting; a save/reload with one train parked
and one crossing (slot 4 watches a crossing, autosave disarms it); cold start with the
Stirling supply removed or disabled. Build 4 and textures remain held. Keep the MOVE prompt
and its map row until the owner's smoke is recorded. The owner feedback above is the first
visual result; the remaining smoke has not been reported.

Executed model: GPT-6 (Codex), as identified by the session instructions; the transcript
provides no more specific runtime id. No subagents were used.

## Not claimed

"Routing works" is never the claim; the claim is N routes exchanging cargo through one hub in
the tested colony. "The reserve works" needs predictions 7, 9 and 10 together: the ledger's
`reserve_took_by_train=0`, the waiting site, and the payment from stock.
