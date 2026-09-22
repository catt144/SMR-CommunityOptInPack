# Drones survey: work kinds and connected-track graph

Derived against the archived game source at `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src`. All source citations below refer to that tree and version **1.1.0.403908**. The parent supplied Steam build **24995074**; this investigation verified the cited archive files against its manifest, not the running game or Steam installation.

Repository HEAD when investigation began: `d8a5ca8bdf598fb60e205e01bc7a61f654e5b53d`, emitted by `git rev-parse HEAD`. This was a read-only investigation; no files or commits were written.

`SOURCE` means the archived call path establishes the behavior. `INFERRED` means a conclusion or implementation implication drawn from those paths. `MEASURED` is reserved for executed checks. No game behavior was measured.

## Findings that affect the build

**SOURCE:** `ForEachConnectedTrack` is a local connector iterator, not a network traversal. It calls `TrackBase:GetDestStation`, which rejects every track with elements under construction. Breaking a track creates such construction-site elements. Therefore, using this iterator alone to find repairs can hide the broken track and everything reached through it.

**SOURCE:** Vanilla station upkeep has separate material-delivery and repair-work phases. A station can supply its maintenance material from its own depot without a drone. This still leaves a repair work request that requires a worker; the self-service call does not perform the work.

**SOURCE + MEASURED:** Ordinary track pieces have construction/repair sites, not building-maintenance requests. Separate drone dust-cleaning work was not found in the searched source. Building maintenance completion resets dust visuals; the surviving `clean` names do not establish an independent cleaning job.

**SOURCE:** Controller range primarily limits automatic request discovery. `Drone:Work` does not itself check `work_radius`. Manual commands can bypass the controller’s task search but still require request assignment, a successful vanilla approach, and fulfillment. “Not automatically serviced outside coverage” is supported; “a drone cannot perform any work outside coverage” is too broad.

## Work kinds and their actual paths

### Automatic dispatch and the range boundary

The automatic path is:

1. `DroneControl:ConnectTaskRequesters` calls `FindTaskRequesters`, which searches `TaskRequester` objects within the node’s hex work radius and recursively includes working extenders. Eligible requesters connect to the controller.  
   **SOURCE:** `Lua/Buildings/DroneControl.lua:375-416`.

2. A requester connecting itself uses `FindDroneNodes`, whose filter is `node.work_radius >= HexAxialDistance(...)`; `ConnectToBuildingCommandCenters` connects the resulting controllers. Dome coverage and `AncientArtifactInterfaceBase` are explicit alternative connection paths.  
   **SOURCE:** `Lua/_TaskRequest.lua:286-323`.

3. `TaskRequester:AddCommandCenter` requires `center.accept_requester_connects`, avoids duplicate controller entries, and calls `center:AddBuilding(self)`. `AddBuilding` inserts the requester’s requests into the controller’s queues.  
   **SOURCE:** `CommonLua/TaskRequest.lua:149-161`, `:298-305`, `:321-348`.

4. `Drone:Idle` requires a valid controller. Ordinarily it calls `TryTakeTask` only when `command_center:CanCommandDrones()`; the ordinary `DroneControl` implementation returns `self.working`. `TryTakeTask` calls the controller’s `FindTask` and dispatches either `Work` or `PickUp`.  
   **SOURCE:** `Lua/Units/Drone.lua:672-704`, `:593-610`; `Lua/Buildings/DroneControl.lua:288-290`.

5. `TaskRequestHub:FindTask` passes that controller’s request queues, construction state, restrictors, and the drone’s unreachable-building table to the native task finder.  
   **SOURCE:** `Lua/_TaskRequest.lua:73-85`.

**INFERRED:** A remote track site or station absent from every relevant controller connection will not become an ordinary automatic assignment merely because a Wasp flies beside it or its hub belongs to the same track network. Track connectivity is not used by this dispatch path.

These qualifications matter:

- **SOURCE — groups:** Construction coverage is effectively group coverage. Connecting an individual construction-site member connects its group leader; the leader owns the requests. The group leader also connects through its members. A covered member can therefore allow work on a group extending outside the drawn radius.  
  `Lua/Buildings/ConstructionSite.lua:1250-1266`, `:2580-2585`, `:689-716`.

- **SOURCE — approach fallback:** `ConstructionGroupLeader:DroneApproach` delegates to a group member. `TrackConstructionSite:DroneApproach` first attempts the construction-group elements, then tries other built or under-construction elements of the same track as alternative work positions. This is physical approach fallback after assignment, not a new network-wide source of assignments.  
  `Lua/Buildings/ConstructionSite.lua:2611-2616`; `Lua/Buildings/TrackElement.lua:656-715`.

- **SOURCE — repairing the controller:** Before ordinary task search, `Drone:Idle` explicitly services its own malfunctioned non-rover controller’s maintenance demand or work request, even though the controller may not currently command ordinary work. Supply still has to be found for the demand phase.  
  `Lua/Units/Drone.lua:682-694`.

- **SOURCE — movement restriction differs from work radius:** `Drone:UpdateRestrictArea` applies `GetDroneRestrictRadius(self)` around the controller. It does not pass `controller.work_radius`. This is a separate movement constraint.  
  `Lua/Units/Drone.lua:232-245`.

- **SOURCE — manual dispatch:** Manual construction and maintenance interactions directly issue `Work`, `PickUp`, or `Deliver`, bypassing `FindTask`. They still depend on resources, request slots, source validity, and approach success.  
  `Lua/Units/Drone.lua:2341-2355`, `:2820-2832`, `:3087-3089`.

**LIMITATION:** Native request assignment and pathfinding internals are not fully implemented in these Lua files. A manually commanded Wasp’s exact attainable distance and landing behavior need a game probe. This report does not treat the absence of a Lua radius test as proof of arbitrary-distance execution.

### What vanilla can do

| Target and work | Established vanilla path | Outside automatic controller coverage |
|---|---|---|
| Broken track element | Construction-group materials, then `construct` work, then group/member completion | No ordinary automatic assignment unless the group is connected through another covered member or an alternative controller connection |
| New track construction | The same construction request machinery | Same restriction; new construction is separate from the repair-only shipping scope |
| Station maintenance supply | Drone pickup/delivery; station can also transfer its own stock into the maintenance demand | Local station self-service can fill demand without a drone; remote drone delivery does not automatically arise from track connectivity |
| Station malfunction repair / maintenance work | `maintenance_work_request`, resource key `repair`, then `RequiresMaintenance:Repair()` | Requires an assigned worker; stock and network connectivity alone do not complete it |
| Station dust removal | Maintenance completion clears accumulated maintenance and dust visuals | No separate automatic dust-cleaning job was established |
| Ordinary intact track upkeep / dust cleaning | No ordinary maintenance or cleaning request found for track pieces | There is no established job to dispatch |
| Track/universal tunnel routine maintenance | No maintenance resource configured in the examined vanilla tunnel templates; inherited default is `no_maintenance` | No ordinary recurring maintenance job established |
| Station storage and train-building material deliveries | Supply/demand requests and the standard pickup/delivery paths | No automatic drone assignment without coverage; self-service can supply train construction from station stock |
| Station upgrade deliveries | Upgrade demand requests, then building upgrade completion logic | Subject to ordinary delivery coverage; upgrades are not automatically part of the owner’s maintenance/repair/upkeep/cleaning authorization |
| Rebuilding or clearing a destroyed connector building | Explicit rebuild creates a construction site; explicit clearing creates a clear-work request | Subject to construction/work coverage; do not silently dispatch destructive clearing |
| Repair/recharge of another disabled drone | Separate `FindDroneToRepair` / `RepairDrone` path | Special proximity search described below; this is not an infrastructure request obtained through the track graph |

### Broken track: construction, not `RequiresMaintenance`

**SOURCE:** `TrackGridElement` includes `Constructable` and `TaskRequester`, but does not inherit `RequiresMaintenance`. It has `auto_connect = false`. `TrackBase` inherits `Building`, but neither its declaration nor the generated `Track` template configures a maintenance resource; the inherited maintenance default is `no_maintenance`.

Citations:

- `Lua/Buildings/TrackElement.lua:139-174`.
- `Lua/Buildings/Track.lua:26-54`.
- `Lua/BuildingTemplate/Track.generated.lua`.
- `Lua/RequiresMaintenance.lua:18-26`, `:97-99`.

**SOURCE:** `TrackBase:BreakTrackElement` creates a construction group for `TrackGridElement`, places a construction site, cross-links the original element and site through `.broken`, and hides the original element. It sets the group cost multiplier and applies the researched `SafeTransport` discount.

`Lua/Buildings/Track.lua:623-650`.

**SOURCE:** The normal meteor caller excludes endpoint and station elements, groups affected elements by track, inserts the repair group into `track.repair_cgs`, and emits `TrackBroken(track, true)`.

`Lua/Meteors.lua:713-734`.

**SOURCE:** Construction materials and work belong to the group leader. `GatherConstructionResources` creates positive resource demands and an initially empty `construct` work request. `StartConstructionPhase` fills the work request only when resource demands are satisfied. `DroneUnloadResource` can immediately send the delivering drone to that work request.

`Lua/Buildings/ConstructionSite.lua:689-716`, `:1532-1545`, `:1579-1604`.

**SOURCE:** Actual work follows:

`Drone:Work` → request assignment → `ApproachWrapper` → request fulfillment → target `DroneWork` → `ContinuousTask` → completion destructor.

- `Lua/Units/Drone.lua:983-1022`.
- `Lua/Buildings/ConstructionSite.lua:1465-1476`.

The destructor calls `Complete()` only when the site is no longer waiting for resources and is constructed.

**SOURCE:** For grouped track repairs, the dynamically dispatched completion path is:

`ConstructionGroupLeader:Complete()` → each `TrackConstructionSite:Complete()`.

It is not the implementation body of generic `ConstructionSite:Complete` cited loosely in DESIGN.

- Group completion iterates and completes members: `Lua/Buildings/ConstructionSite.lua:2659-2705`.
- Track member completion restores the original broken element’s visibility and clears its broken links: `Lua/Buildings/TrackElement.lua:841-887`.
- When all construction elements are gone it processes/reconnects tracks, clears repair groups, and emits the repaired `TrackBroken` message: `Lua/Buildings/TrackElement.lua:895-915`.

**INFERRED:** The owner’s deadline-based implementation should identify the correct repair-group leader and use its normal completion dispatch. It must account for outstanding construction demands before doing so. These completion methods do not themselves require a drone `w_request` or a synthesized worker table, but invoking completion prematurely bypasses the caller’s normal “funded and constructed” conditions.

**SOURCE:** A train caught on the broken element is destroyed through `DestroySilent("track")`; repairing the track does not repair or resurrect that train.

`Lua/TrainDisasterHandling.lua:1-26`.

### Station maintenance and malfunction repair

**SOURCE:** Both station templates configure Metals maintenance. `Station` enables maintenance-point and dust accumulation.

- `Lua/BuildingTemplate/StationSmall.generated.lua:29`.
- `Lua/BuildingTemplate/StationBig.generated.lua:29-30`.
- `Lua/Buildings/Station.lua:48-72`.

**SOURCE:** `InitMaintenanceRequests` creates `maintenance_work_request` with work resource `"repair"` and, when required, a separate `maintenance_resource_request`. Maintenance normally starts after accumulated points reach the threshold and is prevented while the building is shrouded in rubble.

`Lua/RequiresMaintenance.lua:64-99`, `:153-184`.

**SOURCE:** `RequestMaintenance` selects demand or work phase. Demand adds the required material amount. When its actual amount reaches zero, `MaintenanceDroneUnload` calls `StartWorkPhase(drone)`. Work phase adds accumulated maintenance points to the repair work request.

`Lua/RequiresMaintenance.lua:187-210`, `:494-505`, `:616-623`.

**SOURCE:** `RequiresMaintenance:DroneWork` requires the exact maintenance work request and asserts `maintenance_phase == "work"`. Its completion destructor calls `Repair` only when the target remains valid, its phase is still `"work"`, and its request is exhausted.

`Lua/RequiresMaintenance.lua:655-682`.

**SOURCE:** `Repair` resets maintenance state and clears malfunction. Resetting maintenance sets accumulated points and dust visuals to zero.

`Lua/RequiresMaintenance.lua:397-425`, `:480-491`.

#### The self-service exception

**SOURCE:** `Station:BuildingUpdate` calls `SelfService`. During maintenance demand, `SelfService` transfers from its own supply request to its maintenance demand request. That transfer invokes `DroneLoadResource(nil, ...)` and `DroneUnloadResource(nil, ...)`.

`Lua/Buildings/Station.lua:482-510`.

The unload path reaches maintenance bookkeeping through:

`Station:DroneUnloadResource` → `MultiResourceDepotBase:DroneUnloadResource` → `Building:DroneUnloadResource` → `MaintenanceDroneUnload`.

- `Lua/Buildings/Station.lua:662-673`.
- `Lua/Buildings/MultiResourceDepot.lua:208-214`.
- `Lua/Buildings/Building.lua:2413-2429`.
- `Lua/RequiresMaintenance.lua:616-623`.

**SOURCE:** `StartWorkPhase` commands immediate work only when its argument is a `DroneBase`. Its comment explicitly distinguishes material delivery by trains/shuttles from repair work.

`Lua/RequiresMaintenance.lua:196-205`.

**INFERRED:** A stocked remote station can satisfy its material phase and remain stuck in maintenance work. Sending material alone is not a complete remote maintenance solution.

### Dust cleaning

**SOURCE:** For buildings, dust visuals represent maintenance points. `CleanNeeded()` simply calls `RepairNeeded()`, which tests malfunction.

- `Lua/RequiresMaintenance.lua:18-19`, `:51`, `:231-233`.
- `Lua/Buildings/Building.lua:1061-1068`.

**MEASURED:** The decoded archive search described below found no `AddWorkRequest`/`AddRequest` line producing `clean`, nor a `clean_work_request`/`work_request...clean` line. Its positive control returned the `CleanNeeded` method and `DroneCleanAmount` declarations/use.

**SOURCE:** `DroneResourceUnits.clean` exists, but is only evidence of a registered work-unit name, not of a target creating such work. `Building:DroneWork` dispatches clearing, refabrication, or maintenance; its ordinary maintenance case uses the repair request.

`Lua/Units/Drone.lua:784`; `Lua/Buildings/Building.lua:1892-1919`.

**INFERRED:** Report ordinary station dust cleaning as an effect of maintenance, not a separately supported remote job. Do not dispatch a synthetic `"clean"` request merely because a constant exists.

**LIMITATION:** The absence check covers the searched Lua archive and explicit request-producing spellings. It does not prove that arbitrary runtime modifications, native code, or subsequently loaded mods cannot create a differently constructed request.

### Track connectors, tunnels, and additional work

**SOURCE:** The concrete connected-building families found in the source are `Station` and `TrackTunnelBase`; generated `TrackTunnel` and `UniversalTunnel` both inherit the latter. A building being nearby, electrically connected, or served by a station is not sufficient to make it a track connector.

- `Lua/Buildings/Station.lua:48-57`.
- `Lua/Buildings/TrackTunnel.lua:1-4`.
- `Lua/BuildingTemplate/TrackTunnel.generated.lua:4-9`.
- `Lua/BuildingTemplate/UniversalTunnel.generated.lua:4-9`.

**SOURCE:** `TunnelBase` inherits `Building` but sets `accumulate_dust = false`; neither examined track-tunnel template declares maintenance resources. The inherited `no_maintenance` default prevents ordinary malfunction through `SetMalfunction`.

- `Lua/Buildings/Tunnel.lua:5-20`.
- `Lua/RequiresMaintenance.lua:22`, `:97-99`, `:374-376`.

Exceptional scripted maintenance can change the resource, initialize requests, and accumulate maintenance points. That is conditional behavior, not evidence that ordinary track tunnels regularly need repair.

`Lua/RequiresMaintenance.lua:581-601`.

**SOURCE:** Stations have normal storage requests and explicit train-construction material requests. Their self-service path also feeds train construction from station stock. Train construction begins when the station is working, a queue entry exists, construction has not started, and its internal construction material counters meet the costs; the function does not require a drone argument.

`Lua/Buildings/Station.lua:464-469`, `:489-528`, `:541-547`, `:662-668`.

**LIMITATION / OWNER PROBE:** This does not overturn the owner’s observed “train construction needs a drone.” Log the actual blocking state in the standing test save: `working`, construction queue, `trains_in_construction`, `construct_train_start`, construction material counters, both construction demands, maintenance phase/work request, and supply target amounts. Repeat after the proposed acknowledgement. A request or inherited working-state condition may explain the observed stop; source existence alone does not establish which state the live hub reaches.

**SOURCE:** Both station templates include Expanded Warehousing upgrades. `StartUpgradeConstruction` creates `rfUpgrade` resource demands and reconnects the building; fulfilling all upgrade demands invokes the upgrade completion path.

- `Lua/BuildingTemplate/StationSmall.generated.lua:19-27`.
- `Lua/BuildingTemplate/StationBig.generated.lua:19-27`.
- `Lua/Buildings/Building.lua:2063-2107`, `:2432-2450`.

**INFERRED:** These are real drone deliveries available to local vanilla AI. They are not automatically authorized remote upkeep simply because the destination is a station.

**SOURCE:** Explicit rebuilding creates a construction site over a destroyed building. Explicit destroyed-building clearing creates `clear_work_request`, and completing that work removes the building.

`Lua/Buildings/Building.lua:1768-1804`, `:1810-1832`, `:1862-1866`, `:1892-1905`.

**SOURCE:** Refabrication has its own work request and requires eligibility plus `PrefabRefab`; track/universal tunnel templates explicitly disable it. Treat refabrication as conditional destructive work, not remote maintenance.

`Lua/Buildings/Building.lua:3732-3750`; tunnel generated templates `:16`.

**SOURCE:** Track demolition directly returns resources, destroys track elements, and disconnects stations; it is not an ordinary maintenance drone work request.

`Lua/Buildings/Track.lua:248-283`.

**SOURCE:** Broken-drone rescue is a separate exception to request-queue discovery. `FindDroneToRepair` searches same-map broken drones, excludes occupied/dead/unthawable/shrouded targets, and compares distance from the searching drone against a bound initialized from the controller’s `work_radius`. `RepairDrone` then requires a successful `GotoUnitSpot` and performs recharge or repair.

`Lua/Units/Drone.lua:321-343`, `:593-597`; `Lua/Units/DroneBase.lua:324-368`.

**INFERRED:** This is a real “other drone work” path, but a disabled unit standing near a track has not thereby become a connector-owned infrastructure target. The owner’s remote-track scope should not be widened silently to arbitrary nearby units, depots, cables, pools, or buildings.

### Why vanilla `Work` is not a hovering track-work presentation API

**SOURCE:** `Drone:Work` assigns and fulfills a request, populates `w_request`, `target`, resource, and amount fields, installs destructors, then runs the target’s actual work method after vanilla approach succeeds.

`Lua/Units/Drone.lua:983-1022`.

**SOURCE:** `ContinuousTask` uses battery, faces the target, starts work effects, plays states, and repeatedly subtracts from the request.

`Lua/Units/Drone.lua:798-824`.

**SOURCE:** Pickup/delivery similarly assigns supply/demand requests, approaches the source and destination, fulfills requests, carries resources, and invokes the target load/unload callbacks. A delivery can change to a better demand or fail/drop its assignment when the original destination becomes unreachable.

`Lua/Units/Drone.lua:1116-1145`, `:1156-1169`, `:1195-1212`, `:1366-1416`, `:1443-1478`.

**INFERRED:** A timer-authoritative hovering repair drone should use the researched animation/effect presentation separately from these mutating request commands. Calling `Work` solely to display activity risks ordinary approach, battery use, duplicate work, and completion racing the deadline. Broader remote maintenance needs its own specified material and work accounting; the source does not supply a single “perform all track upkeep remotely” operation.

## The graph and isolated networks

### Endpoint accessors

**SOURCE:** The actual endpoint getters are at `Track.lua:194-199`; the `:104` reference in the brief is a caller.

```lua
function TrackBase:GetStartStation()
    return self.start_el and self.start_el.station
end

function TrackBase:GetEndStation()
    return self.end_el and self.end_el.station
end
```

They return endpoint ownership, without checking working state, damage, construction, power, or whether the owner is literally a `Station` class.

`UpdateEndElements` selects the first and last built elements; connector creation records `station = self` on its connector element.

- `Lua/Buildings/Track.lua:559-565`.
- `Lua/TrainTransport.lua:116-142`.

**SOURCE:** `GetDestStation(start_station)` is more restrictive: it returns false if elements are under construction, then requires both endpoint owners, then returns the opposite endpoint. Passing an unrelated object reaches an assertion.

`Lua/Buildings/Track.lua:339-354`.

### What `ForEachConnectedTrack` does

**SOURCE:** `TrackConnectedObjBase:ForEachConnectedTrack` enumerates the object’s connector indices. For each connector it resolves the hex-grid element, its `track_obj`, and `track:GetDestStation(self)`. It calls the callback only for a valid destination that is not being destructed and is not itself.

The callback receives `(track, destination, ...)`. Returning `"break", value` stops enumeration and returns `value`; normal completion returns nil.

- `Lua/TrainTransport.lua:68-80`.
- Connector lookup: `Lua/TrainTransport.lua:176-182`.
- Station connector bounds: `Lua/Buildings/Station.lua:61-62`.
- Tunnel connector bounds: `Lua/Buildings/TrackTunnel.lua:3-4`.

**SOURCE:** The iterator contains no recursive walk and no visited set. It does not itself deduplicate tracks. It also does not explicitly reject a nonworking destination or test `CanTrainsRun`; those restrictions occur in other operations.

**INFERRED:** A hub-wide repair search requires its own visited-node and visited-track sets. Recursive use of the helper without such sets can repeatedly revisit station cycles. A callback return of nil does not mean “disconnected”: nil is also normal completion after successful callbacks. Collect callback results explicitly.

### Why breaks disappear from that iterator

The established sequence is:

1. `BreakTrackElement` places a construction site with `track_obj = self`.  
   `Lua/Buildings/Track.lua:630-643`.

2. `TrackConstructionSite` inherits `TrackGridElement` and sets `is_construction_site = true`.  
   `Lua/Buildings/TrackElement.lua:620-630`.

3. `TrackGridElement:Init` inserts a construction-site element into `track_obj.elements_under_construction`.  
   `Lua/Buildings/TrackElement.lua:185-188`.

4. `GetDestStation` returns false while that array is nonempty.  
   `Lua/Buildings/Track.lua:339-342`.

5. `ForEachConnectedTrack` gets no valid destination and suppresses the callback.  
   `Lua/TrainTransport.lua:68-78`.

**SOURCE:** The normal meteor break excludes endpoints and connector-owned elements, so it leaves endpoint ownership available while disabling the ordinary destination lookup.

`Lua/Meteors.lua:713-725`.

**INFERRED:** Reachability for a flying repair drone must use physical connector/endpoint relationships across an existing broken track, rather than train-runnable relationships. Otherwise the repair dispatcher treats a break as disconnection and cannot satisfy the owner’s requirement to cross earlier breaks.

A suitable implementation basis is `ForEachConnectorElement` or explicit connector enumeration → valid `track_obj` → physical start/end owners, with separate validity, destruction, and visited checks. Distinguish existing broken track from genuinely unfinished new track; this survey does not authorize treating all construction as repair.

### Tunnels are explicit additional edges

**SOURCE:** A tunnel pair is linked through reciprocal `linked_obj` references. `TrackTunnelBase:GetConnectedTrack` resolves the linked mouth’s connector element and returns its track.

- `Lua/Buildings/Tunnel.lua:23-30`.
- `Lua/Buildings/TrackTunnel.lua:7-9`.

**SOURCE:** `GetNextConnectedStation` skips through tunnel pairs. It uses a local `seen` table, rejects an invalid linked mouth, and gets the first connected destination from the far mouth. A mouth leading nowhere produces false/nil.

`Lua/Buildings/Track.lua:319-336`.

**SOURCE:** That `seen` table stops repeated tunnel processing. On encountering a previously seen tunnel, the loop exits and returns the current object; the function does not explicitly normalize every cycle into “unreachable.”

**INFERRED:** A physical repair traversal must add valid `linked_obj` edges itself and mark both mouths visited. Following ordinary track endpoints alone stops at the near mouth. Calling `GetNextConnectedStation` also inherits the damaged-track filtering of `ForEachConnectedTrack`.

**SOURCE:** Vanilla’s `disconnect_track_power` demonstrates an actual recursive network walk: it checks/marks `visited[station]`, iterates connected tracks, recurses into their destinations, and separately recurses into a tunnel’s linked mouth.

`Lua/Buildings/Station.lua:1357-1371`.

### Train routes are not the owner’s full repair graph

**SOURCE:** `Station:GetConnectedTrack(current_track, check_dest)` chooses another track by connector alignment. It does not enumerate all branches of a station.

`Lua/Buildings/Station.lua:931-960`.

**SOURCE:** `EnumRouteTracks` follows that aligned continuation and tunnel transitions. It detects a route loop by returning to the starting station with the starting continuation track, rather than using a general graph visited set.

`Lua/TrainTransport.lua:251-299`.

**SOURCE:** `RebuildTrainRoutes` initially requires `track:CanTrainsRun()`. `TrackBroken` triggers route rebuilding. `ForEachStationAlongTrack` walks a cached route, maintains station visitation, and filters construction, transport mode, and nonworking stations.

- `Lua/TrainTransport.lua:302-336`, `:360-362`, `:371-454`.
- `TrackBase:CanTrainsRun`: `Lua/Buildings/Track.lua:371-372`.

**INFERRED:** Cached train routes and passenger reachability are unsuitable as the authority for repairs across all station branches, malfunctioned stations, and broken track. They describe train operation, not everything a flying repair drone following existing track could physically reach.

### Exactly what an isolated network returns

**SOURCE / INFERRED from the iterator:**

- An unconnected station’s connector stubs do not yield a valid opposite endpoint. Its callback collection is empty; the iterator itself returns nil.
- A complete remote station network isolated from the hub is internally connected. Calling its own station’s iterator can produce tracks normally. There is no returned `isolated = true` flag.
- A traversal rooted at the hub excludes that remote network because it has no chain of physical connector and tunnel edges from the hub.
- A broken first edge can also make the ordinary iterator’s collection empty. Therefore emptiness from `ForEachConnectedTrack` does not distinguish actual isolation from a broken connection.
- A track with no opposite connector owner is excluded by `GetDestStation`, even when some track elements exist.
- Power-grid membership, geometric proximity, and another station’s service radius are not replacements for track-connector membership.

**SOURCE:** Station warning text uses the helper: no callback produces “Not connected to other Stations”; a separate path sets the broken-chain sign.

`Lua/Buildings/Station.lua:1310-1333`, `:1344-1354`.

**INFERRED:** Those warnings are not reliable evidence of physical isolation during track damage. The same helper filters damaged edges.

## Executed checks and falsification commands

### Archive integrity

**MEASURED:** Each path in the following explicit list matched its entry in `MANIFEST.sha256`; a mismatch would throw. This checks the relevant archived bytes without using a live, potentially overwritten source tree.

```powershell
$s = 'B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.0.403908/Src'
$manifest = Get-Content 'B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.0.403908/MANIFEST.sha256'
$checkedFiles = @(
  'Lua/Buildings/Track.lua',
  'Lua/Buildings/TrackElement.lua',
  'Lua/Buildings/Station.lua',
  'Lua/TrainTransport.lua',
  'Lua/RequiresMaintenance.lua',
  'Lua/Units/Drone.lua',
  'Lua/_TaskRequest.lua',
  'CommonLua/TaskRequest.lua',
  'Lua/Buildings/ConstructionSite.lua',
  'Lua/Buildings/DroneControl.lua',
  'Lua/Buildings/TrackTunnel.lua'
)
foreach ($rel in $checkedFiles) {
  $line = @($manifest | Where-Object { $_.EndsWith('  ' + $rel) })
  if ($line.Count -ne 1) { throw "manifest entry not unique: $rel" }
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $s $rel)).Hash.ToLowerInvariant()
  if ($hash -ne $line[0].Substring(0,64)) { throw "fingerprint mismatch: $rel" }
  "$rel PASS $hash"
}
```

Representative emitted fingerprints:

- `Track.lua`: `a0a41002af7b078570badb1043bf97627712b374f2fda911d29b32942615d9fb`
- `TrackElement.lua`: `42a2ebb7dea6cfcbadcfeb27ef0cce0fcf3ec14b7abaaa098ae98809783701b7`
- `Station.lua`: `f2677c28d0c1cd6d3fdccafb91ace5d5d4e941af7e73831fb3b44999081dc871`
- `TrainTransport.lua`: `73b75c68bfe4599e291c3d0bb45e75dce0097f4c53d195ba00e4a9634a6aacb9`

### Cleaning absence with a positive control

**MEASURED:** Executed against the explicitly named decoded source tree with hidden/ignore filtering disabled:

```powershell
$archiveInputs = @(rg --files --hidden --no-ignore "$s" `
  -g '*.zip' -g '*.gz' -g '*.zst' -g '*.lz4' -g '*.hpk' -g '*.xz' -g '*.7z')
if ($LASTEXITCODE -gt 1) { throw 'archive input search failed' }

$producerHits = @(rg -n --hidden --no-ignore `
  '(?i)(AddWorkRequest.*clean|AddRequest.*clean|clean_work_request|work_request.*clean)' `
  "$s" -g '*.lua')
if ($LASTEXITCODE -gt 1) { throw 'producer search failed' }

$presenceHits = @(rg -n --hidden --no-ignore 'DroneCleanAmount|CleanNeeded' "$s" -g '*.lua')
if ($LASTEXITCODE -ne 0) { throw 'presence control missing' }

$presenceHits
[pscustomobject]@{
  Build = '1.1.0.403908'
  CompressedInputs = $archiveInputs.Count
  CleanProducerLines = $producerHits.Count
  CleanPresenceLines = $presenceHits.Count
}
if ($archiveInputs.Count -ne 0 -or $producerHits.Count -ne 0 -or $presenceHits.Count -ne 4) {
  throw 'absence/presence conclusion needs review'
}
```

Emitted result: compressed-input filenames **0**, matching clean-producer lines **0**, positive-control lines **4**. The positive members reconcile as:

- `Lua/__const.lua:591`
- `Lua/__const.lua:592`
- `Lua/Buildings/Building.lua:1066`
- `Lua/Units/Drone.lua:784`

No compressed inputs of the listed types required decoding within this already extracted source tree.

### Broken-edge premise check

**MEASURED:** Executed and emitted `GraphFilterPremises=PASS`:

```powershell
$iterator = (Get-Content "$s/Lua/TrainTransport.lua")[67..79] -join "`n"
$dest = (Get-Content "$s/Lua/Buildings/Track.lua")[338..354] -join "`n"
$init = (Get-Content "$s/Lua/Buildings/TrackElement.lua")[184..188] -join "`n"

if ($iterator -notmatch 'track:GetDestStation\(self\)' `
  -or $iterator -match 'self:ForEachConnectedTrack' `
  -or $dest -notmatch '(?s)#self.elements_under_construction > 0 then\s+return false' `
  -or $init -notmatch 'self.is_construction_site and self.track_obj.elements_under_construction') {
  throw 'graph-filter premise changed'
}
'GraphFilterPremises=PASS'
```

This is a scoped source check, not a runtime graph test.

### Search lenses used to find contrary paths

The investigation searched definitions, callers, aliases, generated templates, and relevant parent classes. These read-only commands are useful falsifiers when source fingerprints move:

```powershell
rg -n 'ForEachConnectedTrack|GetStartStation|GetEndStation|GetConnectedTrack|GetNextConnectedStation' "$s"
rg -n 'TrackConnectedObjBase|TrackTunnelBase|first_connector_idx|last_connector_idx' "$s/Lua" -g '*.lua'
rg -n 'BreakTrackElement|repair_cgs|TrackBroken' "$s/Lua" -g '*.lua'
rg -n 'DroneWork|maintenance_work_request|maintenance_resource_request|CleanNeeded|SetExceptionalCircumstancesMaintenance' "$s/Lua" -g '*.lua'
rg -n 'ConnectToCommandCenters|FindDroneNodes|AddCommandCenter|FindTask|RequestAssignUnit' "$s/Lua" "$s/CommonLua" -g '*.lua'
```

Search results must be followed through their cited producer → dispatch → approach → completion paths; a matching function name is not a capability proof.

## Probes and implementation notes to carry forward

**INFERRED — required graph smoke:** In the standing save, record a hub-rooted physical component and the ordinary iterator results before and after breaking a connecting track. The broken track and the previously connected far side must remain repair-reachable; an independent remote network must remain excluded. Repeat across a tunnel pair and a station cycle. Log object handles, endpoint owners, `.broken` links, group leaders, `elements_under_construction`, and the visited sets. This would falsify the proposed physical traversal if endpoint or tunnel ownership does not remain as source predicts.

**INFERRED — maintenance probe:** Put a maintained station beyond all automatic drone coverage with available maintenance stock. Observe self-service demand completion, the remaining work request, and whether a deliberately assigned vanilla Wasp can approach and finish it. Repeat with a blocked landing/work location. This distinguishes material accounting, automatic discovery, and physical work capability.

**INFERRED — track-group boundary probe:** Place a repair group with a member in coverage and another outside it; log which controller owns the group leader’s requests and where the drone actually works. Repeat with no covered member. This checks the group and fallback exceptions instead of assuming each repaired hex must be inside the radius.

**INFERRED — train-building probe:** Preserve the owner’s requested stock/no-drone test and report the request or working-state condition that actually blocks it. Do not declare the acknowledgement sufficient merely because train construction has a visual drone effect.

**INFERRED — scope for link 4:** Model physical track reachability separately from train routes, request coverage, and current power/working state. Keep repair jobs tied to exact live repair groups and revalidate them at completion. Treat station maintenance supply, station repair work, and construction-site completion as distinct accounting/completion paths. The source settles their mechanisms; it does not settle a safe custom hovering implementation for all of them.

Executed model recorded from the active transcript: **GPT-6, Codex**. No more specific backend variant was exposed to this investigator.
