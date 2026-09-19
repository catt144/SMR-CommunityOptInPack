# Train hub build — design record, pre-boot predictions and sitting script

**Authority.** Owner rulings 2026-09-18, spec §10
(`TRAIN_LOGISTICS_DESIGN_20260917.md`); brief `docs/agent/prompts/TRAIN_HUB_BUILD_high.md`.
**Status: UNVERIFIED.** Pack `886926b`, TestKit `adda373`. Parse-checked only
(`python tools/parsecheck.py --dir tools/devmods/train_hub/Code` → 2 files, 0 errors; TestKit 33
files, 0 errors). Nothing below has run in game. Every source line was read on 1.1.0.403908
(`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src`). **Smoke-tested 2026-09-19** with the owner; see
§"Sitting result". The full battery was cut to a smoke test by owner ruling (spec §10).

## Where the code lives, and why

A separate dev mod, `tools/devmods/train_hub/` (mod id `SMR_TrainHubDev_20260918`), not `Code/`.
- **The packaging Stop triggers for `Code/`.** `tools/upload_preflight.py:188-196` ("predicted
  pack holds only shipping files") admits only `Code/*.lua`, `metadata.lua`, `items.lua`,
  `LICENSE` and the preview image. It refuses `Data/BuildingTemplate/*.lua` and any entity folder
  as NON-SHIPPING. Its next guard, `:203-211`, lists `Code/` non-recursively, so a
  `Code/BuildingTemplate/*.generated.lua` named in `metadata.lua` fails as "listed but absent".
  The tool was not changed. **Owner decision owed** before the hub moves into the shipping mod.
- `items.lua` and `metadata.lua` carry another session's uncommitted work.
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

## Not claimed

"Routing works" is never the claim; the claim is N routes exchanging cargo through one hub in
the tested colony. "The reserve works" needs predictions 7, 9 and 10 together: the ledger's
`reserve_took_by_train=0`, the waiting site, and the payment from stock.
