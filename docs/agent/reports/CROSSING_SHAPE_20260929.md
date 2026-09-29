# Cross-map rail crossing beside the hub — shape investigation

Brief: [24_ELEVATOR_SHAPE_INVESTIGATION_high.md](../prompts/Train_Hub_Project/24_ELEVATOR_SHAPE_INVESTIGATION_high.md).
Desk investigation, 2026-09-29. Repository evidence at
`e5bacf432d9fe904320f72da52333ea971f2daa5`; `git log --oneline -3` and `git pull`
ran before the investigation; pull reported **Already up to date**. Installed game:
**1.1.1.405907, Steam build 25390750**, read with
`python tools/doccheck.py --emit-fingerprint` (GREEN). No game was launched or commanded.

This is evidence and a recommendation for the coordinator's audit, not a build ruling.
Only this report is changed. The spec, brief, owner decisions and both dev mods remain the
inputs. SOURCE means the cited source establishes the mechanism; LOG means an accessible
log establishes that observation; INFERRED means a design consequence or prediction.
None means a shape has been shown to work or be safe in the game.

## 1. Recommendation and the comparison stop

**INFERRED — recommend prototyping a separate rail terminal at each end of an existing
vanilla elevator, paired by reading that elevator's `other` reference.** Call this **H,
the elevator rail attachment**, to distinguish it from changing the elevator itself.
The elevator continues to own its passage, unit transport, depot, power and maintenance.
The crossing owns the rail terminals, track connection and train transfer. Trains pass through
with their cargo; there is no intermediate train resource buffer. The hub is an optional
station at the end of the surface line, never the crossing's controller or prerequisite.

The decisive desk advantage over G is **adoption in an established colony**. SOURCE S1/S2:
an occupied passage refuses a second elevator, and the vanilla elevator template sets
`can_demolish = false` and `can_refab = false`. Offering a second elevator beside the first
in the build menu cannot serve a colony whose usable passages already have elevators.
H can, in principle, read those existing pairs without changing their saved objects.

H is a **proposed read-only tie-in**, not a finding that terminals fit around vanilla's
asset. Its construction interface must belong to the terminals: no new button, upgrade,
connector, parent class, wrapped method, template edit or saved field on vanilla's elevator
is assumed. A terminal can discover a nearby valid elevator and its reciprocal partner;
the crossing can retain its own association if necessary. The association's precise save
contract is a build task, not permission to add a field now. If construction or operation
turns out to require modifying the elevator, that is an owner decision against 2026-09-21.

**Brief stop 2 applies to the final product choice:** the desk cannot establish that H's
terminal footprint leaves usable rail approaches and ordinary elevator access on both maps.
That may make H worse than an integrated custom elevator. The smallest comparison sitting
is §8.1. Until it is read, H is the recommended *next prototype*, G is the integrated
alternative, and there is no unconditional winning shape or build authorization here.
Stop 1 did not fire: the measured installed build matches the brief.

| Shape | Evidence for it | Evidence against it / work it still needs | Desk disposition |
|---|---|---|---|
| **F: independent train shaft** | The existing prototype supplies the actual hop implementation. Its historical report records a round trip. A purpose-built shaft could choose positions independently of elevator passages and serve ordinary stations without a hub. | SOURCE S3/S4 and dev shaft: stock tunnel construction is single-map; the prototype avoids the placement problem by re-linking finished pairs. It inherits unsuitable tunnel registries and leaves harmful cross-map links after removal. Arbitrary two-map placement, a new class and save handling remain work. No normal underground access while locked. | Keep as the transfer experiment and as the fallback if passage-bound rail cannot fit. Do not promote the present dev mod into a product. |
| **G: our own complete rail elevator** | SOURCE S1/S2: elevator placement creates both halves; surface completion can unlock the underground. One player purchase could provide the ordinary elevator and train connection. An integrated asset can reserve rail clearance deliberately. | Occupied passages block adoption. Both stock assets lack rail spots (§3). The raw multiple-inheritance recipe runs incompatible tunnel lifecycle code. Vanilla hardcodes the two elevator entities during placement/linking. Missing-class fallback depends on the generated persistence key, and says nothing about train frames or dangling rail endpoints. | Strong integrated alternative, especially for a fresh colony, but substantially more than “copy elevator plus one wrap.” |
| **Directly retrofit vanilla Elevator** | Could reach already placed elevators without a second building footprint. Their native `other` already identifies the destination map. | Adding rail to the elevator object requires connector creation/geometry, train-facing methods and route recognition; stock assets supply none of the rail spots. Changing `Elevator`/`ElevatorBase`, its template, asset, inherited methods or saved state changes vanilla's elevator. It also applies the change to elevators the player did not choose to convert unless explicitly gated. | Requires an owner ruling against 2026-09-21. No such ruling is inferred from this investigation request. |
| **H: separate rail terminals using a vanilla elevator pair** | Reuses a completed pair in an old save; reads `other`, map identity and working state; avoids duplicating the elevator's depot, labels, unit commands and grid lifecycle. Can be built and operated with the hub absent. | Needs room for terminals and approach track, a normal construction/link interface and its own persistence/removal design. Rail routing and train transfer are still custom work. It deliberately requires a usable vanilla elevator; it does not unlock the underground itself. | Recommended prototype, conditional on §8.1. A functional association, not an object attachment that silently adds parts/state to vanilla's elevator. |
| **Transfer cargo between two stations without transferring the train** | INFERRED: would avoid a train's cross-map command. | Creates a new freight buffer/allocator and does not deliver the owner's train pass-through. Duplicates distribution work and changes the product. | Not recommended. |

F's recorded positive result supports investigating the transfer primitive, not choosing F's
construction or save architecture. The round-trip and reload logs named in its report are no
longer in the live log directory; no copy was found among the named archive evidence.
They are **inherited observations**, not LOG findings re-established by this investigation.

## 2. Evidence coordinates

Every game-source citation below is in the archived tree
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/`, **build 25390750**.
Paths and line numbers refer to that tree, not the live `ModTools/Src` tree. §9 contains
the checks and the binary-data probe. Dev-code paths are under this repo at the HEAD above.

| ID | Source, build 25390750 | What it establishes |
|---|---|---|
| S1 | `Data/BuildingTemplate/Elevator.lua:7-8,15,25,30-40`; `Lua/BuildingTemplate/Elevator.generated.lua:4-9,16-17,37-44`; `Lua/Buildings/SurfacePassage.lua:14-27` | Native elevator identity, environment allowance, occupied-passage exclusion, no ordinary demolition/refab, generated fallback to `ElevatorBase`. |
| S2 | `Lua/Buildings/Elevator.lua:577-665,694-732,761-794`; `Lua/Colony.lua:654-662,947-950`; `Lua/MapSwitch.lua:7-11` | Elevator lifecycle, hardcoded entities and paired construction; native unlock and the map-switch gate. |
| S3 | `Lua/Buildings/Tunnel.lua:1-31,40-114,160-208,260-262`; `Lua/Construction/TunnelConstruction.lua:245-275` | Tunnel pairing, hex-only adjacency, grid/pf wiring and teardown; explicit load callback; one-map construction. |
| S4 | `Lua/Buildings/TrackTunnel.lua:1-79`; `Lua/TrainTransport.lua:10-50,82-155,227-357`; `Lua/Buildings/Track.lua:320-336` | Rail-mouth ancestry, connectors, traversal, tunnel classification and route enumeration/rebuild. |
| S5 | `Lua/Buildings/Station.lua:931-962`; `Lua/Units/Train.lua:338-414,453-467,862-874` | Opposite-connector continuation, the non-stopping tunnel path, train command continuation and route-dependent cargo allocation. |
| S6 | `Lua/Buildings/Elevator.lua:371-398,464-483,509-535,961-1002,1055-1099`; `Lua/Units/Unit.lua:942-951`; `Lua/CityObject.lua:73-83`; `CommonLua/Classes/_cobject.lua:157-171` | Elevator-owned cross-map services, native transfer call and city/attach bookkeeping. |
| S7 | `CommonLua/Core/classes.lua:1882-1916,1957-2013,2064-2083`; `CommonLua/PropertyObject.lua:1743-1744`; `CommonLua/Classes/_object.lua:22` | `Init`, `Done`, `GameInit` composition; a child method does not erase the ancestor's contribution; class-specific composition filters exist. |
| S8 | `CommonLua/Classes/Composite.lua:391-416,496-524`; `CommonLua/Classes/_cobject.lua:125-137`; `CommonLua/Core/persist.lua:73-84` | Generated parents and persistence base; missing-class resolution uses the encoded base, not an arbitrary surviving ancestor. |
| S9 | `Lua/Buildings/Building.lua:41,89-103,253,460-466`; `Lua/Buildings/Elevator.lua:613-619`; `Lua/Units/Colonist.lua:3575-3587,3695-3704`; `Lua/Buildings/Dome.lua:356,424`; `Lua/Buildings/Station.lua:384` | Saved environment overrides; exact class label versus the `Elevator` label/type used by passenger systems. |
| S10 | `Lua/RandomMap/RandomMapGenerator_Picard.lua:131-198`; `Lua/Buildings/SurfacePassage.lua:128-154` | Generator targets two successful pairs but can exhaust markers or fail placement; the count is not a universal guarantee. |
| S11 | `CommonLua/Classes/CommandObject.lua:400-462,577-579`; `CommonLua/Modding/Mod.lua:1559-1568,1647-1667` | Running-destructor thread identity, queue clearing, persisted mod environment and fallback environment. |
| S12 | `CommonLua/Savegame.lua:337-370,783-786,853-860,1004-1023,1035-1059,1117-1127,1141-1152`; `CommonLua/Classes/XDef/SilentSaveScreen.generated.lua:20` | Save-start precedes asynchronous work; persistence happens in `PersistGame`; silent saves do not block game time; in-memory and bug-report paths bypass the ordinary messages. |
| S13 | `Lua/Buildings/Track.lua:423-456` | Route-cap check and native train assignment consume a prefab at line 436. |

The source mechanisms cited in S3's construction span and S12's metadata span are included
in the verification in §9; older report line numbers are not silently carried forward.

## 3. Option G's unverified list, resolved as far as the desk permits

**Rail spots — SOURCE, decoded shipping asset data at build 25390750.** The in-memory FLPK
and ZSTD extraction of `Packs/BinAssets.fpk:entities.dat`, decoded with the existing
`SMR-Assets/_shared/geometry/entities_dat.py`, gives:

| Entity | Decoded spots | Matching `Trackconnector` / `Trackdirection` spots | Other spots |
|---|---:|---:|---:|
| `ElevatorSurface` | 63 | 0 | 63 |
| `ElevatorUnderground` | 60 | 0 | 60 |
| `TrainTunnel` — positive control | 27 | 2 (`Trackconnector0`, `Trackdirection0`) | 25 |

Filter, members and assertions are in §9's executed probe. Decoded data SHA-256:
`64b682061315fab9e9bb1c21be6f29f5953ef90451b43c1574bbb0b0a05a434d`.
An `rg` over the decoded spot names is negative for each elevator and positive for the
tunnel. This is not a native `HasSpot` or visual-clearance test. G needs its own/synthetic
rail geometry, including the inner track element, not just an entrance animation. S4's
connector code loops beyond the declared one connector in several methods; merely setting
`first_connector_idx = last_connector_idx = 0` is insufficient to make missing-spot calls safe.

**The diamond — SOURCE establishes an unsafe unmodified recipe; the corrected class is
unbuilt.** `{ "Elevator", "TrackTunnelBase" }` also inherits `TunnelBase`. S7 combines
the lifecycle methods, so defining a new `GameInit` does not suppress S3's tunnel initializer.
That initializer pairs via `g_LastPlacedTunnel`, registers mapless adjacency and installs
pf/grid wiring; its destructor uses a different pair field and removes its partner.
It coexists with elevator pairing through `passage.other.elevator` / `other`, entity changes,
shared-depot setup and elevator teardown. Common ancestors being deduplicated does not
make these different lifecycle contributions equivalent.

There is a source-supported way to investigate class-local composition:
`CombineMethodRemoveMethod(method_name, custom_class, "TunnelBase")` (S7). It is not a
tested implementation. Plain methods such as `MergeGrids`, `Destroy`, connector creation,
`OnTrackPowerReconnected`, `ApplyTunnelMask` and the transfer also need explicit ownership.
**A subclass-only `AddPFTunnel` override is insufficient:** S3's load handler invokes
`Tunnel.AddPFTunnel` directly for every `TunnelBase`, bypassing that override. A retained
`TrackTunnelBase` ancestry needs a guarded load path as well. This applies to G and H's/F's
custom rail mouths, not only to the elevator diamond.

**Passages — SOURCE/decoded map data, no promised colony count.** S10 requests two successes;
the loop can finish with fewer. The bundled-map probe in §9 decodes the FLPK and Lua
bytecode instead of grepping compressed packs. It finds the stock underground marker
templates; its `LOADK` counts are reference counts, not live passage counts. A hand-authored,
custom or already occupied map does not inherit a guarantee of two available elevator sites.
The build therefore needs the actual valid reciprocal pairs and occupancy, not a constant.
Reading those in the chosen save is the smallest remaining sitting step. User Workshop maps
and saves were not decoded in this investigation.

**Two additional corrections to G's bill:**

- SOURCE S2 forces `ElevatorSurface` / `ElevatorUnderground` during construction and again
  when linking, destroying/recreating attaches. A template's custom entity alone will not
  preserve custom rail art or attached connectors. G must account for those paths on its
  own class; H avoids changing that lifecycle by keeping terminals separate.
- SOURCE S8 supports fallback to `Elevator` only if the saved key actually encodes
  `Elevator:<custom class>`. With `object_class = <our combined base>`, generation instead
  encodes that custom base, which is absent with the mod. There is no recursive search for
  a vanilla ancestor. `object_class = "Elevator"` plus a suitable generated component shape
  is a candidate, not proof that the proposed hybrid has that key. Even a correct class
  fallback leaves rail elements, train references, assets and captured functions to audit.

SOURCE S9 also confirms G's need for concrete `Elevator` ancestry and explicit `Elevator`
label membership/removal. `ElevatorBase` alone and the new template's class label do not
satisfy every vanilla passenger lookup. H leaves those vanilla objects and labels in place.

## 4. Rechecking C1–C9 against the current dev code

Dev paths in this table are relative to `tools/devmods/`; their line numbers were read at
the HEAD in the introduction. The leads are split where their mechanisms and conclusions
have different evidence.

| Claim | Finding and evidence |
|---|---|
| **C1 — hub graph crosses maps and commands far stations** | **SOURCE, confirmed.** `train_hub/Code/20_TrainHub.lua:2375-2442` queues the reciprocal `linked_obj` at 2426-2427 without a map guard. `register_remote_stations:2461-2476`, called at 3211, calls `AddCommandCenter` for reachable Stations. Membership affects real maintenance requests; it is not merely a UI list. |
| **C2 — wrong-map drone flight** | **SOURCE mechanism; INFERRED native outcome.** `30_TrainHubDrones.lua:315-325` follows the far mouth in scripted routing. Current default is **engine** mode at 82: `F.Site:333-340` returns the target's coordinates; `leg:851-856` issues local `FlightGoto(point(x,y))`. The active mode need not fly through the shaft at all. Both paths lack a target-map boundary. A wrong-map repair visual/work admission is predicted, not observed here. OI-27's rejection must happen before work/payment/flight, and cover resumed jobs too. |
| **C3 — Link overwrites hub-line routes** | **SOURCE rebuild; conditional INFERRED damage.** `rail_shaft/Code/10_RailShaft.lua:291` calls `RebuildTrainRoutes`; S4 writes a route to every segment unconditionally at 331. S5's straight/opposite geometry determines overlap. Rebuilding is necessary and is not itself proof of corruption. Do not attribute the old stall to this. The settled empty-opposite hub connector provides a terminating line, not permission to branch a through-line. |
| **C4 — free train after rebuild** | **Refuted as phrased, SOURCE.** `70_TrainBay.lua:36-42,133-152` keys by sorted station handles and owes a fill when an arm's station count grows. Replacing route table identity alone does not qualify; a changed key without count growth does not qualify. `:99-109` checks the pool, free arm and route cap, then calls native `AssignTrain`; S13 decrements the pool. A shaft that adds a far station can consume an available prefab. There is no free-train creation established by this code. |
| **C5 — distribution includes far-map stations** | **SOURCE, conditional on reachability, confirmed.** `40_TrainDistribution.lua:64-115` assigns owners from `HubTrackGraph` and builds parents/children from `hub.city.train_track_routes`. City-owned route tables can contain far-map stations (S4); “City state” does not mean map-local contents. The code does not reject far-map members. Also, a surface city's routes need not contain every entirely underground feeder line, so this is not proof of a complete colony-wide distribution tree. |
| **C6 — mid-hop save probably crashes without shaft mod** | **Exposure established; crash not established.** `10_RailShaft.lua:306-382` runs a closure under `PopAndCallDestructor` and sleeps at 340 and 374. It closes over helper functions, `RS`, tracks, mouths and map data. S11 and the historical EF-023/EF-027 observations identify the capture risk. Captured upvalues can survive, and the missing-mod environment falls back to native globals (S11); there is no automatic implication that this orphan crashes. The hub's actual `luaSPersist.cpp` failure was a different saved-waiter binding problem (§6), not a shaft no-mod experiment. |
| **C7 — removing shaft mod leaves pair and strands trains** | **SOURCE residual; INFERRED failure mode.** Pair links are native saved `linked_obj` fields (`10_RailShaft.lua:285-286`), not removed by uninstall. Vanilla then uses S4's `SetPos`, which cannot provide the cross-map transfer. S3's load callback can reintroduce pf wiring. A stalled, misplaced or broken train is predicted; which outcome occurs has not been measured. Grid reconnection is another exposure, not a claim that `LoadGame` itself calls `MergeGrids`. |
| **C8 — environment table mutated on unlocked load** | **SOURCE and LOG, confirmed.** `10_RailShaft.lua:141-175` reads/fills the entry then clears its `Underground` key on each qualifying load; S9 makes the table a GameVar. Live log `Mars.exe-20260928-12.06.47-6aad2d75.log:244,362,440` prints the action. Idempotent repeated clearing is still persistent state. `AllowUnderground(false)` changes build permission only; it neither unlinks mouths nor disables hooks, and the next unlocked load calls true again. |
| **C9 — no shared wrap, therefore load order irrelevant** | **Narrow SOURCE observation; conclusion not proved.** Shaft wraps `TunnelBase.AddPFTunnel`, `TunnelBase.MergeGrids`, `TrackTunnelBase.TrainTraverse` at 180-196/385-391. The hub source search has no write to those targets; its `TrackTunnelBase` uses are graph predicates. Both nevertheless share native routes, trains, stations and load messages. Disjoint direct wraps do not prove commutative initialization, save loading or gameplay. Both mod orders remain in the final battery. |

**No runtime module OFF exists in the shaft dev mod.** Its hooks install at file scope.
The dev mods are separate ModDefs; `optional_mod = true` is not a Mod Options toggle.
The product's module-state rows below are requirements/proposals, not claims that those
controls already exist in these prototypes.

## 5. State matrix

Classifications are desk judgments: **safe candidate** means a bounded design with no
identified interaction in that state, *not safe in-game*; **unsafe candidate** means a
specific unresolved hazard; **impossible** names the missing prerequisite. All player
behavior for H is **INFERRED**, since H is unbuilt. Current-dev exceptions are explicit.

“Unlocked but untouched” means **no underground rail/station development**. Strictly no
underground building at all is not the normal elevator-unlock sequence: paired construction
places the far half, and surface completion unlocks (S2). A saved true flag without a valid
elevator pair is a separate state and must not satisfy H's capability check.

### Loaded and enabled combinations

| Loaded/enabled | Underground | What the player sees | Hub action | Crossing H action and classification |
|---|---|---|---|---|
| Hub alone | Locked | Surface hub and ordinary train network. | Ordinary hub work on its map. | Absent. **Safe candidate** for the crossing interaction; no claim of full hub validation. |
| Hub alone | Unlocked, untouched | Same surface network; ordinary elevator if built. | No far rail network to enroll. | Absent. **Safe candidate**; unlocking alone is not a rail connection. |
| Hub alone | In use | Hub/local rail plus ordinary elevator service. | Local service; any independent underground hub serves its own map. | No cross-map train service. **Safe candidate only without old crossing residue**; removal rows below govern a save that once contained one. |
| Crossing alone | Locked | Vanilla elevator remains the way to unlock; rail attachment unavailable with a clear reason. | Absent. | No terminal admission, route or unlock write. **Crossing impossible** until the pair and unlock exist; dormant module is a **safe candidate**. G differs: its own elevator could be the first unlock. |
| Crossing alone | Unlocked, untouched | Rail terminals may be planned at a valid completed pair; incomplete rail reports “no connected station/route.” | Absent. | No train is sent into a dead far end. **Dormancy is a safe candidate; transport impossible** until ordinary stations/tracks exist on both sides. No automatic colonization or free train. |
| Crossing alone | In use | Ordinary station → terminal → far terminal → ordinary station. | Absent. | Native train route plus crossing-owned transfer; elevator continues ordinary service. **Unsafe/unproven candidate** until geometry, freight and save tests pass. Hub code is not required. |
| Both | Locked | Surface hub still useful; elevator progression unchanged. | Continues local work. | Dormant as above. **Safe candidate** for the interaction; do not require `UndergroundMap.City` to exist just because a mod is loaded. |
| Both | Unlocked, untouched | Surface hub and optional incomplete terminal project. | Local work continues. | No route or membership from the unlock flag alone. **Safe candidate** while dormant. Present shaft dev mod nevertheless mutates environment permission on unlocked load (C8). |
| Both | In use | Dedicated hub terminus on an arm with its opposite empty; underground station/line at the far end. | Drone work remains on the hub's map. Train membership/distribution follow the future owner choice, not OI-27 by inference. | **Unsafe candidate with current dev code** (C1/C2 and unresolved saves). Desired H is unproven. C3 topology checks and the ordinary prefab-funded bay behavior apply. |

### State changes in an existing save

These transitions apply to every applicable loaded/enabled row above. “Off” and “removed”
are separate operations; keeping class code resident is what lets existing content continue.

| Transition | Player-visible result and each module's responsibility | Desk classification |
|---|---|---|
| Enable hub while crossing is already in use | New hub placement becomes available; crossing continues between ordinary stations. Adding a hub changes native station topology; hub recomputes its chosen membership/distribution view and local work. | **Safe candidate only after those guards exist**; current shared graph would enroll far work. No automatic conversion of crossing terminals into hubs. |
| Disable hub module while crossing remains enabled | Existing placed content may remain under FIX_POLICY §0; hide new hub instances. Crossing keeps its own route/transfer capability. What existing hubs retain is the hub module's content-off contract. | **Unbuilt transition**, not evidence that removing the hub's code is harmless. Crossing must not read the hub's enable flag to decide whether it can transfer a train. |
| Enable crossing, underground locked | Show the ordinary prerequisite; hub behavior unchanged. Do not set `underground_map_unlocked`, create hidden construction or alter vanilla build permissions. | **Safe candidate**; transport **impossible**. |
| Enable crossing, unlocked with/without far rail | Reconcile existing valid pairs and terminals; build no trains or stations automatically. A completed pair without a far rail destination stays unavailable to trains. | **Safe candidate** while dormant; operation remains unproven. |
| Disable crossing module while a train is crossing | Proposed content-off contract: hide new terminals, retain code/service for placed terminals, let the active passage finish. Hub continues local work. A separate “close this link” action would stop admissions, drain, then rebuild routes. | **Unsafe** if implemented as unconditional hook bypass to vanilla `TrainTraverse`, immediate deletion, or breaking the pair under the command. “Off stops all existing service” is a different owner choice. |
| Unlock underground after loading either/both modules | Hub stays useful. H notices native `UndergroundUnlocked` or rechecks prerequisites; terminal placement also checks a valid completed pair, maps and construction state. | **Safe candidate** for reconciliation. Current shaft only enables underground construction on load or explicit `AllowUnderground`, not on the unlock message. |
| Add either mod to a save that never contained it | No old custom frames/content to adopt. Hub remains local; H recognizes an existing vanilla pair without converting its objects. | **Safe candidate for initialization**, native add-mod test still owed. Installation does not create a rail route. |
| Remove crossing mod; terminals/pair or active train remain | Hub must tolerate an absent crossing API, but it cannot repair an invalid saved route/endpoint. Current F leaves native cross-map mouths and altered environment permission; H/G removal behavior is unbuilt. | **Unsafe candidate**, including a train at a station if its future route still uses the removed crossing. No claim of clean uninstall for any shape. |
| Remove hub mod; crossing remains | Crossing logic must still serve ordinary stations, but a line ending at a missing hub does not magically acquire a vanilla destination. Remove/replace the hub through its supported exit and reconnect ordinary stations before claiming independence. | **Unsafe candidate for a save with placed hubs/frames**; **safe architectural candidate** for a crossing line that never contained a hub. Hub independence is not hub migration. |
| Remove both mods, or disable them in Mod Manager and restart | No resident crossing or hub handlers. All saved buildings, links, requests, active frames and assets must have their own dispositions. | **Unsafe/unmeasured** for saves containing either feature. Returning only to the menu is not the no-mod control (FIX_POLICY §5). |
| Re-add after a no-mod load/save | Reconcile what actually survived; do not assume old custom classes, labels, links or frames can be reconstructed. | **Unmeasured**. Retain the original pre-removal save for testing; an earlier successful load is not round-trip migration evidence. |
| Pair becomes invalid, map unavailable, track breaks, or elevator stops working | H rejects new admissions before beginning a hop; hub local work remains independent. Completion/recovery of an admitted train needs an explicit crossing-owned path. | **Unsafe candidate until interruption handling is built/tested**. An elevator working-state check is an H design proposal; source reading does not establish a train policy for vanilla's elevator. |

## 6. Saving while a train is inside the crossing

The prototype's “inside” is not a stock elevator holder/manifest. The train is still in
its rail command, sleeping on the approach or exit movement inside a custom destructor
(`10_RailShaft.lua:328-382`). `current_station` becomes the far mouth only at 378, after
the exit sleep; arrival-track membership is removed at 379. The map transfer occurs at 361.

| Snapshot/load condition | Evidence and expected obligation | Desk classification |
|---|---|---|
| Save before transfer, reload same code | SOURCE: sleeping closure contains the far endpoint and route objects. INFERRED: it can resume the pending transfer; exact native thread/map behavior not measured. | **Unproven**; log train handle, map, command, cargo/passengers and track reservations before/after. |
| Save after transfer but before station/assignment cleanup, reload same code | SOURCE: map/city may already be far-side while `current_station` and arrival assignment still describe the near side. INFERRED: normal resume must finish exactly once and release traversal/track occupancy. | **Unproven**, a distinct check from saving a linked pair at rest. |
| Reload with a runtime module option OFF but code resident | Content-off proposal preserves continuation for existing content. Gate new construction/admission separately from finishing an admitted train. | **Unbuilt**; simply testing the option at every wake can strand a train halfway through bookkeeping. |
| Reload with crossing code absent | C6/C7: serialized helpers might run; future traversal falls back to same-map vanilla code and guards are absent. A missing-class fallback cannot repair all of those independent references. | **Unsafe candidate; crash is not proved.** |
| Reload with hub code absent | Crossing might resume its own hop, but its pending destination or train thread may still refer to the hub. | **Unsafe candidate** if the saved route/frame involves a hub; no conclusion follows from crossing independence. |
| Autosave/quicksave overlaps a hop or new admission | SOURCE S12: a `SaveGameStart` handler is separated from the snapshot by real-time/asynchronous work, while the silent screen does not block game time. | A one-time drain in the start handler is **not sufficient**. Any proposed save-time normalization needs an admission gate held through completion, plus a disposition for bypass save paths. |

Re-derived EF-070 caveat: in **this build**, screenshot `WaitRenderMode` calls occur
**after** `PersistGame` (`Savegame.lua:1006` versus 1017/1020). Do not repeat the old fact's
specific “four yields before persistence” argument from its moved source tree. The remaining
`Savegame._Wrap` waits and asynchronous metadata save still prevent treating SaveGameStart
as an atomic snapshot boundary. The fact file is left unedited by this report-only task.

LOG control for the hub precedent: archived
`docs/archive/train_hub_load_crash_20260924/Mars.exe-20260924-10.42.33-6aad2d75.log:113`
records the `luaSPersist.cpp(1272)` assertion. The later `...10.49.56...log:255,323-330`
records locked underground and the listed trains with `route_ok true`. This is evidence
against making the shaft overwrite story the default diagnosis; it is not the missing
shaft-session save and does not settle that earlier stall.

For a build brief, FIX_POLICY §3a's remedy ordering still applies. Investigate synchronous
native inputs/delegation before a custom yielding transfer; a destructor gives command
continuity, not save cleanliness. A custom hop needs its own interruption, orphan and save
disposition. H does not escape that cost by reading a vanilla elevator.

## 7. Touch list and design facts for the build brief

### Share through these seams

| Concern | Seam and ownership | Basis |
|---|---|---|
| Physical train connection | Native track elements and reciprocal `linked_obj` on crossing-owned mouths; native city route tables. Hub remains a Station endpoint. Rebuild once the pair/topology is coherent, then native `TrainRoutesRebuilt` notifies consumers. | **SOURCE S4/S5; INFERRED integration design.** Neither module writes the other's route cache. |
| Map identity | Object map identity (`GetMap` / `IsSameMap`), with validity checks; never infer a map from XY or a City-owned table. | **SOURCE C1/C2/S4; INFERRED guard placement.** Train topology may cross maps; work topology stops at the boundary. |
| Underground readiness | Read native unlock and map/pair existence. `UndergroundUnlocked` and load/construction events are reconciliation opportunities; a use-time check is still needed. | **SOURCE S2.** A true flag alone proves neither a far station nor a valid elevator. |
| H's elevator relationship | Read the vanilla elevator's reciprocal `other`, map, validity and current working state. Store any required terminal association on crossing-owned state, not the elevator. | **SOURCE S2/S6; INFERRED H design.** Uses a native pair even with the hub absent. |
| Optional extra coordination | Prefer native topology/messages. If an additional capability is necessary, resolve a runtime function only after checking its existence and arguments; absent provider means no extra capability. Recompute caches on load. | **INFERRED.** No hard reference to `SMROptInTrainFloor`, `SMRRailShaft` or a peer's custom class in a save is needed merely for cooperation. An API cannot substitute for the absent physical crossing. |
| Train identity/cargo/passengers | The existing vanilla Train and native cargo operations; crossing supplies only transport between endpoints. | **SOURCE S5/S6; INFERRED design.** Freight conservation and passenger/attach transfer still require §8. |

### Keep these separate

| Do not share | Reason and evidence |
|---|---|
| Hub repair jobs, drone-task controller registration, targets or flight legs across maps | **Owner authority OI-27**, spec §10 lines 3762-3766, settles repair work/targets/flights. **INFERRED from C1/C2:** physical drone-task registration, saved pending jobs and dispatch/payment need that boundary too; checking only `F.Route` misses default engine flight. This does not decide logical train membership. |
| One graph for repair eligibility and distribution membership | **INFERRED from C1/C5 and OI-27's limited scope.** `D.Refresh` currently calls the same `HubTrackGraph`. Putting the drone map cut into that shared answer silently chooses a distribution policy. Separate the graph's purpose or filter work consumers; do not settle the open policy by implementation accident. |
| Vanilla tunnel's cross-map pf/hex/grid wiring | **SOURCE S3.** XY-only adjacency and tunnel `SetPos` are not a cross-map transport abstraction. A new mouth cannot depend on a guard installed by the *other* dev mod. |
| A blanket prohibition on elevator cross-map grids | **SOURCE S6 corrects that proposed prohibition.** `MapPassageLinked:MergeGrids` deliberately handles cross-map elevator connections. Retain vanilla elevator services; exclude the separate tunnel machinery. |
| Elevator shared depot, desire settings or cargo manifests as a train buffer | **INFERRED from the owner's pass-through direction and S6.** The ordinary elevator's shared depot can remain; trains do not deposit into it. This avoids coupling train throughput to the elevator's depot slider or duplicating distribution. |
| Global `DisabledInEnvironment` mutation for vanilla UniversalTunnel | **SOURCE C8/S9.** It affects builds unrelated to the chosen crossing and persists. A new terminal's own environment template plus prerequisites is the proposed seam. |
| Hub object, drone function or peer callback in crossing persistence | **INFERRED from S8/S11.** A peer being optional must not leave the crossing needing that peer's class/function to load. A train whose destination is a removed hub still needs an explicit exit; this is not cured by avoiding a callback. |
| Turning OFF as permission to delete a live pair or use stock tunnel movement | **SOURCE C6/C7; INFERRED lifecycle consequence.** A train can be between map transfer and assignment cleanup. Resident content, closing a route and uninstalling code are different operations. |

### Membership and distribution: options left to the owner

All rows keep repair drones on their own map. None is selected by this report.

| Policy | Consequence |
|---|---|
| Far stations are not hub members and have no hub distribution settings | Clearest geographic boundary. A train can still connect a local hub to a normal far station under native rail rules; the cargo allocator needs an explicit boundary behavior so the unmanaged end is not accidentally treated as a hub-controlled order. |
| Far stations are members for train distribution, but never drone service | Preserves useful one-hub freight control across the crossing. Requires a distinct train graph, working cross-city parent/child discovery, saved setting reconciliation when the crossing closes, and clear maintenance ownership. C5 shows the present tree is not automatically a complete cross-city network. |
| Membership is informational across maps; distribution belongs to a hub on each map | Exposes the link without letting a surface hub set far station targets. Needs explicit handoff/ownership at the boundary and conflict rules when both maps have hubs. A hub on the far map is an optional distribution choice, not a crossing prerequisite. |

The bay's ordinary fill when a route gains a station (C4) is a separate consequence to
show the owner during the sitting. Do not suppress the route message or call it a free
train to avoid making that behavior visible.

### Build-brief inputs and their evidence class

These are bounded findings/proposed acceptance conditions for the crossing job. They do
not create canonical repo rules or override an owner decision.

| Input | Evidence class |
|---|---|
| Keep the settled terminating hub arm with its opposite empty; do not introduce a routing branch. | **Owner authority 2026-09-23; proven from source S4/S5** explains the linear route model. |
| A rail-enabled unlock flag alone does not establish a transport route. Require valid endpoints and a reachable destination before train admission. | **Proven from source S2/S4; inferred admission design.** |
| Separate train topology from local drone eligibility; preserve same-map tunnels. | **Owner authority OI-27; proven from source C1/C2/C5.** |
| Raw G inheritance and a subclass-only pf override are insufficient. | **Proven from source S3/S7.** |
| The vanilla elevator has no native rail spot pair in the decoded entity records. | **Proven from shipping asset data**, §3/§9; native spot/clearance check still owed. |
| Do not budget a guaranteed free passage or promise replacement of an occupied elevator. | **Proven from source S1/S10; decoded map data in §9.** |
| Rebuild notification may spend an existing train prefab when the route gains a station. | **Proven from source C4/S13**, native timing unmeasured. |
| The dev shaft changes underground build permission on an unlocked load. | **Proven from source C8 and log** named there, build 25390750. |
| Treat a blocked custom hop as save-exposed, including its helpers; define recovery for each snapshot phase. | **Inferred from S11/S12 and historical EF-023/EF-027**, not a new current-build serialization measurement. |
| H should read vanilla elevator state and own only its rail content; G should own its elevator specialization. | **Inferred architecture**, pending the shape sitting and owner choice. |

## 8. Smallest sittings and coordinator handoff

### 8.1 Shape comparison — settle stop 2 first

On a throwaway copy with a working vanilla elevator and the hub available, use the existing
dev shaft to place ordinary trial mouths and approach track beside the elevator on both maps.
Inspect the entrance, rover/colonist path, construction footprint, rail direction and visible
train clearance. Connect the surface line to the hub's settled empty-opposite arm and the
far line to an ordinary station; read the shaft's existing `Routes()` and `Sweep()` diagnostics
before and after linking. Those diagnostic reads are **proposed here, not run this session**.
The trial mouths are a space/track experiment, not an implementation of H's automatic pairing.

Acceptance for comparison: rail can reach both proposed terminal positions while the ordinary
elevator remains usable, and the dedicated line has consistent endpoint membership without
changing other hub lines. Failure of that fit is the reason to prefer an integrated G asset
or a freely placed F shaft. Also enumerate actual reciprocal elevator passages and occupancy
on this save; do not spend a presumed spare entrance. Leave the dev mod enabled as the owner
directed. Pair removal, if needed, is the dev mod's explicit unlink on the throwaway, not
disabling its code.

### 8.2 Transport and lifecycle checks after the shape is chosen

These are the smallest distinct observations, to fold into crossing sittings and the owner's
one final combined battery rather than schedule a separate hub battery now.

| Unknown | Smallest observation/control |
|---|---|
| Cargo, passengers, attached wagons and transfer bookkeeping | One loaded outbound and return trip; compare resource totals, passenger handles/tickets, attached wagon/map identities and city labels. Keep an ordinary same-map tunnel leg as the control. The old stage log alone measured none of those payloads. |
| Mid-hop same-code save/load | One save at the near-side sleep and one at the far-side sleep, then full restart/load; verify one completion, correct map/city, live route, released reservations and conserved payload. Repeat a silent save while admission is active. |
| Mid-hop code removal | After a build supplies its declared exit/fallback, load a copy of each phase save with crossing removed and a full process restart. Record resume/error/stall and endpoint residue. The hub's prior assertion is not this test. |
| OI-27 without deciding distribution | A local hub linked to a far broken track/station plus a same-map tunnel control: no far work admission, payment, controller assignment or flight, including after load; local control still receives work. Inspect distribution membership separately. |
| G lifecycle, if chosen | Minimal two-half build on a free passage; inspect generated class ancestry/persistence key, pair identities, labels and ordinary elevator use. Save/reload, then a supported removal test. Test a normal tunnel alongside it to detect `g_LastPlacedTunnel`/load-registry contamination. |
| Optionality and route notifications | Crossing with ordinary stations and no hub; hub without a crossing; both with the underground locked, unused and in use; both mod orders; add/remove copies only after lifecycle exits exist. Check the bay's prefab balance as a far station joins the route. |

### 8.3 Findings left in this report for the coordinator

| Finding/block | Evidence/home in this report | Next actor/action | Disposition |
|---|---|---|---|
| Shape H versus G/F; vanilla retrofit boundary | §§1,3,8.1 | Coordinator audits, then the owner compares the terminal fit and chooses the shape. If any elevator mutation is proposed, route that precise change to this mod's owner list against 09-21. | Unresolved, preserved here; no ruling edited or assumed. |
| Drone graph leaks into membership/distribution | C1/C2/C5, §7 | Brief 23/coordinator: implement the already ruled work boundary without silently choosing far-map distribution. | Source finding; no code edited. |
| Far-map membership/distribution choices | §7 option table | Coordinator presents the independent choice to the owner through this mod's owner list. | Open by explicit brief instruction. |
| Removed code and phase-specific save exposure | C6/C7, §6 | Crossing build: disposition each exposed site under FIX_POLICY §3a, then native tests. | Inferred harm; no crash or clean-uninstall claim. |
| Environment permission residual | C8, S9 | Crossing build excludes the dev mutation; any cleanup of existing saves needs its own scope. | Source/log finding retained; vanilla state untouched here. |
| Stale source/claims in earlier reports and EF-070 | §§3,4,6 | Coordinator's audit and normal fact/report owners decide follow-up filing; EF ids remain donor-allocated. | Corrections recorded here only, as brief 24 requires. |

The brief assigns audit on a different model to the orchestrator. That audit has not been
performed here. No checklist, fact entry, spec, prompt or archive is changed to bypass it.

## 9. Commands, controls and limits

The evidence reads used `rg -n` and numbered UTF-8 Python slices of the paths in S1–S13,
the C-table and the supplied reports. Useful exact searches executed in this investigation:

```powershell
git log --oneline -3
git pull
git rev-parse HEAD
git status --short
python tools/doccheck.py --emit-fingerprint
rg -n 'linked_obj|HubTrackGraph' tools/devmods/train_hub/Code/20_TrainHub.lua
rg -n 'F.Route|F.Site|FlightGoto|Mode =|STOCK_LEG' tools/devmods/train_hub/Code/30_TrainHubDrones.lua
rg -n 'HubTrackGraph|train_track_routes|function D.Refresh' tools/devmods/train_hub/Code/40_TrainDistribution.lua
rg -n 'route_key|take_snapshot|try_fill|AssignTrain' tools/devmods/train_hub/Code/70_TrainBay.lua
rg -n 'TunnelBase|AddPFTunnel|MergeGrids|SMRRailShaft|TrainRoutesRebuilt|RebuildTrainRoutes|ApplyModOptions|ModItemOption' tools/devmods/train_hub/Code tools/devmods/train_hub/items.lua tools/devmods/rail_shaft/items.lua
rg -n 'luaSPersist|route_ok|underground is locked' docs/archive/train_hub_load_crash_20260924 -g '*.log'
```

Read-only inline Python also checked the specifically named 09-23 logs under
`%APPDATA%/Surviving Mars Relaunched/logs/` (both absent) and read each `Mars.exe-*.log`
for `[RailShaftDev]` plus `allowed underground = true`, `hop train` or
`AddPFTunnel skipped`. C8 names a surviving positive file and its lines. No absence of
shaft activity throughout the owner's entire history is claimed. The live C8 log can rotate;
its source mechanism is independently cited, and no status was upgraded from that log.

The following is the reproducible **read-only desk probe** used for compressed evidence.
It runs in ordinary Python, creates no files and runs nothing in the owner's game.
It uses this repo's FLPK parser, the shared asset decoder, and the donor's bytecode reader.
Tool source revisions read during the investigation: SMR-Assets
`2dcb019bab82eadde637dd1e9f275015d9365a5a`; donor
`19e774c1a471bd02981592df16f4af7527e71322`.

```python
# crossing-shape-binary-check
from pathlib import Path
from unittest.mock import patch
import collections, hashlib, io, json, mmap, re, struct, subprocess, sys

sys.path[:0] = [str(Path('tools').resolve()),
    'B:/Dev/SMR/SMR-Assets/_shared/geometry',
    'B:/Dev/SMR/SMR-BugFixPack/tools']
import flpk_extract as fx
import entities_dat as ed
import l7_env_map as lm

packs = Path('A:/SteamLibrary/steamapps/common/Project Spark/Packs')

def members(buf):
    assert buf[:4] == b'FLPK'
    off = struct.unpack_from('<I', buf, 12)[0]
    size = struct.unpack_from('<I', buf, 20)[0]
    result = []
    fx.parse_table(buf, off, size, off, '', result)
    return result

def unpack(buf, entry):
    name, flag, off, size = entry
    data = buf[off:off + size]
    if flag == 16:
        return data
    assert flag == 48 and data[:4] == b'ZSTD', name
    want = struct.unpack_from('<I', data, 4)[0]
    hdr = struct.unpack_from('<I', data, 12)[0]
    n = (hdr - 16) // 4
    starts = [hdr] + list(struct.unpack_from('<%dI' % n, data, 16))
    parts = []
    for a, b in zip(starts, starts[1:] + [len(data)]):
        chunk = data[a:b]
        parts.append(fx.zstandard.ZstdDecompressor().stream_reader(
            io.BytesIO(chunk)).read() if chunk.startswith(fx.ZMAGIC) else chunk)
    result = b''.join(parts)[:want]
    assert len(result) == want, name
    return result

with (packs / 'BinAssets.fpk').open('rb') as f, mmap.mmap(
        f.fileno(), 0, access=mmap.ACCESS_READ) as buf:
    data = unpack(buf, next(e for e in members(buf) if e[0] == 'entities.dat'))
assert hashlib.sha256(data).hexdigest() == (
    '64b682061315fab9e9bb1c21be6f29f5953ef90451b43c1574bbb0b0a05a434d')
with patch('builtins.open', lambda *a, **kw: io.BytesIO(data)):
    records = ed.read_entities('memory')
for name, expected in [('ElevatorSurface', (63, 0)),
                       ('ElevatorUnderground', (60, 0)), ('TrainTunnel', (27, 2))]:
    names = [s['name'] or '' for s in records[name]['spots']]
    matching = [s for s in names if re.search(r'Track(connector|direction)', s)]
    found = subprocess.run(['rg', '-n', 'Trackconnector|Trackdirection'],
        input='\n'.join(names), text=True, capture_output=True)
    assert found.returncode == (0 if matching else 1), found.stderr
    assert (len(names), len(matching)) == expected, (name, names)
    assert len(names) == len(matching) + len([s for s in names if s not in matching])
    print(name, 'spots', len(names), 'rail', len(matching),
          'other', len(names) - len(matching), 'members', matching)

def lua_proto(data):
    # The shipping header omits two standard Lua 5.3 size bytes.
    # Consume the header actually measured here, then use the existing reader.
    assert data[:15] == bytes.fromhex('1b4c7561530019930d0a1a0a040408')
    reader = lm.Reader(data)
    reader.i = 32
    proto = lm.read_proto(reader, (4, 8, 4, 8, 8), None)
    assert reader.i == len(data), proto.source
    return proto

targets = ('SurfacePassage', 'UndergroundPassage', 'SurfacePassageMarker')
maps_read, candidates = [], []
for p in sorted((packs / 'Maps').glob('*.fpk')):
    with p.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as buf:
        entries = members(buf)
        meta = next((e for e in entries if e[0] == 'mapdata.lua'), None)
        if not meta:
            continue
        proto = lua_proto(unpack(buf, meta))
        maps_read.append(p.name)
        if 'Underground' not in proto.consts:
            continue  # literal metadata candidate scope, not a playability claim
        objects = lua_proto(unpack(buf, next(e for e in entries if e[0] == 'objects.lua')))
        counts = {t: 0 for t in targets}
        for word in objects.code:
            if word & 63 == 1:  # Lua 5.3 LOADK, main chunk only
                value = objects.consts[word >> 14]
                if isinstance(value, str) and value in counts:
                    counts[value] += 1
        strings = '\n'.join(c for c in objects.consts if isinstance(c, str))
        grep = subprocess.run(['rg', '--crlf', '-n', '^SurfacePassage$|^UndergroundPassage$|^SurfacePassageMarker$'],
            input=strings, text=True, capture_output=True)
        present = [t for t in targets if t in objects.consts]
        assert grep.returncode == (0 if present else 1), (p.name, present, grep.stderr)
        candidates.append((p.name, counts))
        print(p.name, 'main LOADK references', counts, 'decoded grep', grep.returncode)
assert len(maps_read) == len(set(maps_read))
print('mapdata parsed', len(maps_read), 'literal Underground candidates', len(candidates),
      'remaining', len(maps_read) - len(candidates))
groups = collections.Counter(c['SurfacePassageMarker'] for _, c in candidates)
assert sum(groups.values()) == len(candidates)
print('candidate marker-reference groups', dict(groups))
```

Probe result at build 25390750: asset rows match §3. The map filter selects **17** of
**142** parsed `mapdata.lua` members, leaving **125** outside that literal filter.
The selected members reconcile as `BlankUnderground_01..04`,
`BlankUnderground_GroundZero_01..04`, `BlankUnderground_ImpassableHighGround_01..04`,
`PrefabBlankUnderground_01..04`, and `PrefabUnderground_01` (4 + 4 + 4 + 4 + 1).
The first four groups each have two main-chunk marker references per member; the final
prefab has none: **16 + 1 = 17**. These are decoded bytecode references, not generated
pair totals, available sites or live objects. The source generator's failure branch and
per-passage occupancy remain the relevant design facts.

Validation: the embedded binary probe **PASS**; all game-source files in S1–S13 match
their archived `MANIFEST.sha256`, and the cited spans are within those files; report link,
scope and UTF-8/LF checks **PASS**; `python tools/doccheck.py` **GREEN**. The decoded-map
grep uses `--crlf` so the Windows text pipe retains a valid positive control. No game tests,
loaded-save inspection, freight test, mid-hop save/load, no-mod load, both-order run,
H construction or G hybrid-class instance were run.

Executed agent: **Codex, identified as GPT-6 in this session's instructions**. A more
specific runtime model identifier and effort are not exposed in the transcript; none is
invented. No subagents were used. The coordinator's different-model audit remains owed.
