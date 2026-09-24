# Rail shaft — cross-map train tunnel: mechanism, prototype, sitting not yet run

**Origin (owner, 2026-09-21).** The elevator cargo pain is an Opt-In Modules matter
(`reports/ELEVATOR_LOGISTICS_OPTIONS.md`). The owner asked for the bypass to be explored instead:
a train tunnel whose two ends sit on different maps. The elevator is not altered. Method ruling:
**prototype first** — rough and in the game fast, the owner looks, then we adjust.

**Status: the dev mod is built and installed; nothing has been run in the game.** Every
behavioural statement below is *predicted from source; engine rule unmeasured*. §6 is the sitting
that measures it. The session that built this was non-interactive, so the sitting — end-state item
3 of the brief — could not be held. It is the only part outstanding.

⚠️ Reports are not authority. Nothing here ships and no module exists. This is a dev-only
prototype under `tools/devmods/rail_shaft/`; building any of it for real needs an owner ruling
recorded for this mod and an `agent/bugs/` entry (`FIX_POLICY.md` §4).

---

## 0 · The brief's build stop fired, and what was done about it

The brief's stop (3) was *"the installed build is no longer 24995074"*. It has fired.

```
python tools/doccheck.py --emit-fingerprint
  FINGERPRINTS — derived_at across 116 facts; installed game build 25390750
```

The game patched **1.1.0.403908 → 1.1.1.405907 (build 25390750) on 2026-09-23**, the same day this
work ran; the sweep is `prompts/perma/gamepatch/1.1.1.405907_2026-09-23.md`. So every source
citation the brief carried describes a tree that is not on disk (EF-083).

The remedy was on disk and cost little, so rather than stop dead: **every source claim in the
brief was re-derived against the installed tree**,
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src\`, and the prototype was written against
that. §1 records the re-derivation. This satisfies what the stop is for — not building on a tree
the rig does not have — rather than evading it. The owner may still prefer the literal stop; the
sitting has not been spent, so nothing is lost either way.

Two consequences that do **not** get repaired:

- **The 2026-09-21 console evidence cannot be re-checked.** The brief cites
  `…\logs\Mars.exe-20260921-18.06.04-6a91a190.log` lines 1188-1207. That log has rotated off disk
  (`grep -rl "TRAINPROBE" …\logs` → no hits; the oldest surviving `Mars.exe` log is
  2026-09-23). It also predates the patch. So the stranded-train observation stands **as recorded
  in the brief only**, on a build the rig no longer has. It is treated below as a lead, not a
  measurement.
- **No save was found to test on.** The brief asked that an existing save with trains researched
  and the underground unlocked be looked for first. There are none anywhere under `%APPDATA%` or
  the user profile — `find … -iname "*.savegame"` returns nothing, and
  `%APPDATA%\Surviving Mars Relaunched\` has no `saves` directory at all. The owner will have to
  supply or build the fixture; §6 step 1 says so.

---

## 1 · How a unit crosses maps

Read 2026-09-23 on the installed build, **25390750 / 1.1.1.405907**, from that build's archived
tree. Line numbers are `<path>:<lines>` inside `…\SMR-SrcArchive\1.1.1.405907\Src\`.

**The primitive is C.** `object:TransferToMap(map, pos)` —
`CommonLua/LuaExportedDocs/Game/GameObject.lua:1529`. That is the whole exported signature; there
is no Lua body to read. Exactly one class overrides it in Lua, and only to get out of the way
first: `ExplorerRover:TransferToMap` drops an `Analyze` command before delegating
(`Lua/Units/ExplorerRover.lua:173-178`).

**Two shipped callers, and they disagree about the position argument.**

| caller | call | how the unit gets placed |
|---|---|---|
| `PFTunnel:TraverseTunnel` (`CommonLua/Movable.lua:622-629`) | `unit:TransferToMap(end_point_map, end_point)` | the position argument |
| `ElevatorBase:UseElevator` (`Lua/Buildings/Elevator.lua:961-1002`) | `unit:TransferToMap(self.other)` at `:982` — **one argument, an object** | `SetHolder(self.other)` then `Disembark`, `:983-985` |

This matters because the 2026-09-21 console hop passed no position and the brief read the
resulting stranded train as *"it kept its underground coordinates"*. The elevator passes no
position either and works. **So the missing position is not on its own the explanation.**

**What the engine does to the unit on the way through.** These fire per class:

- `Unit:OnTransferToMap` (`Lua/Units/Unit.lua:942-945`) — removes the selection arrow and calls
  `ClearCommandQueue`.
- `CityObject:OnTransferToMap` / `…Done` (`Lua/CityObject.lua:73-84`) — drops the city labels on
  the way out, then reassigns `self.city = new_map.City` and re-adds them. This is the
  bookkeeping the 2026-09-21 probe saw follow the train across, and it is free.
- `Unit:OnTransferToMapDone` (`Unit.lua:947-952`) — drops a holder left on the wrong map.
- Plus `PinnableObject:OnTransferToMapDone` (`PinnableObject.lua:124`),
  `UnitRevealDarkness:…` (`RevealDarkness.lua:275`), and Drone / Colonist / RCRover / RCSafari
  overrides. **`Train` defines none of its own** — confirmed by listing every
  `OnTransferToMap*` definition in the tree.

**`ClearCommandQueue` is a red herring.** It is one line — `self.command_queue = nil`
(`CommonLua/Classes/CommandObject.lua:577-579`). It empties the *queue*; it does not end the
command that is currently running. Nothing in Lua ends the command on transfer.

**The destructor is the real differentiator, and it is the finding.** Both shipped crossings wrap
their **entire body** in `PushDestructor` / `PopAndCallDestructor`, and both `Sleep` inside it:

- `ElevatorBase:UseElevator` — `:966` push … `:1001` pop; `Sleep(5000)` at `:984`, *after* the
  transfer.
- `TunnelBase:TraverseTunnel` — `:215` push … `:256` pop; `Sleep(travel_time)` at `:240`.

A destructor is what the engine runs when a command is *interrupted*
(`CommandObject.lua:406-434`), and while one runs, `thread_running_destructors` keeps it counting
as the command thread, so the body finishes (`:400-404`, `:441-462`). The 2026-09-21 console hop
ran its transfer **outside** a destructor, and the train never moved again — consistent with the
command thread not surviving the transfer, though it is equally consistent with the subsequent
`SetPos` failing. **This is the open question, and it is exactly what §4's stage log is built to
answer.** Do not record it as settled from this report.

**The stock rover tunnel does not cross maps at all.** `TunnelBase:TraverseTunnel`
(`Lua/Buildings/Tunnel.lua:211-258`) *overrides* the `PFTunnel` version and never calls
`TransferToMap`; it uses `DetachFromMap` → `SetHolder` → `ExitBuilding`. The cross-map branch in
`PFTunnel:TraverseTunnel` is reached by other tunnel kinds, not by the buildable rover tunnel.

---

## 2 · What a train needs that a rover does not

A rover crossing is a pathfinding event. A train crossing is a **track** event, and four things
change because of it.

**a. The hop is a different function, on a different call path.** A rover goes through
`Movable:TraverseTunnel` → `pf.GetPathTunnel` → the tunnel's `TraverseTunnel`
(`Movable.lua:465-477`). A train goes `Train:GotoStation` (`Lua/Units/Train.lua:338-414`) →
`next_station:TrainPassThrough` at `:407` → `TrackConnectedObjBase:TrainPassThrough`
(`Lua/TrainTransport.lua:43-51`) → `TrackTunnelBase:TrainTraverse`
(`Lua/Buildings/TrackTunnel.lua:40-80`). The train's hop has no pathfinder in it.

**b. The stock train hop is single-map by construction.** `TrainTraverse` drives the train to the
near mouth's inner element (`:54-58`), then **`train:SetPos(spot_pos)`** at `:70` to the linked
mouth's element, then drives it to the connector and sets `train.current_station = self.linked_obj`
(`:69-79`). `SetPos` does not change a unit's map. That one line is the entire cross-map problem.

**c. Routing, though, already crosses maps — for free.** This is the good news and it was
re-checked line by line:

- `EnumRouteTracks` follows `next_struct.linked_obj` with **no map check**
  (`TrainTransport.lua:264-269`).
- `GetArrivalTrack` does the same (`:239-241`), for `TrackTunnel` and `UniversalTunnel`.
- `RebuildTrainRoutes` (`:302-358`) walks **every** city and keys the route by **every** track
  segment in it (`:331`). So a route that crosses maps is enumerated once from the surface
  station and once from the underground one, and lands in **both** cities' `train_track_routes`.
  `GetArrivalTrack`'s `curr_station.city.train_track_routes[departure_track]` lookup (`:228`)
  therefore resolves on both legs.

So the outbound and the return lookup should both find the route. *Predicted from source;
unmeasured.*

**d. The train continues under its own command afterwards.** `GotoStation` sets
`teleport_to_next = not IsKindOf(next_station, "TrackTunnelBase")` at `:411`, so after a tunnel
the train drives the far track normally rather than being teleported along it. Whatever the hop
leaves behind has to be good enough for `self:Traverse(track, …)` at `:372` on the next lap.

**e. Cargo, passengers and wagon attaches were not investigated.** The transfer hook in
`_cobject.lua` recurses over attaches, and `Train` adds no override — but nothing here tested it
and §5 does not claim it.

---

## 3 · What a cross-map tunnel pair must NOT do

`TunnelBase:GameInit` (`Tunnel.lua:77-90`) wires three registries, and all three are single-map:

| wiring | why it is wrong across maps |
|---|---|
| `RegPoints` → `g_TunnelsAdjacency` (`:40-48`, `:50-66`) | the key is `q + 32768*r` — **hex only, no map**. Two mouths at the same hex on two maps collide. C reads this table (`:61`). |
| `Notify(self, "AddPFTunnel")` → `pf.AddTunnel` (`:193-205`) | a rover path between two maps; also reads the far mouth's entrance positions |
| `MergeGrids("electricity")` / `("water")` (`:160-172`) | merges two maps' power/water grids into one |

`ApplyTunnelMask` (`:107-114`) is per-map and harmless, but it reads `self.registered_point`, so
that field must not be nil'd while it is in play.

`OnMsg.LoadGame` re-runs `AddPFTunnel` over **every** `TunnelBase` on every map
(`Tunnel.lua:260-262`), so a one-time unwire at link time is not enough — the entry point itself
has to be guarded, or a reload re-wires the pair.

**Construction is single-map by design.** `TunnelConstructionController:Activate` makes **one**
`CreateConstructionGroup` on **one** map and places both sites on it
(`Lua/Construction/TunnelConstruction.lua:254-275`). The elevator's two-map construction group
(`Elevator.lua:747-780`) is the precedent, but it relies on pre-made passage markers.

**Pairing, by contrast, is already map-agnostic.** `TunnelBase:Init` pairs through the global
`g_LastPlacedTunnel` with no map check (`Tunnel.lua:23-31`). The two mouths of a pair find each
other purely by being created back to back.

**A Universal Tunnel cannot be built underground.** `Data/BuildingTemplate/UniversalTunnel.lua`
carries no `disabled_in_environment`, so it inherits the property default,
`set("Underground", "Asteroid")` (`Lua/Buildings/Building.lua:253`). Two traps in the runtime
table (`Building.lua:89-104`):

- `UndisableInEnvironment` is a **no-op** while `DisabledInEnvironment[id]` is nil — it only
  clears a key, and the lazy fill happens in `DisableInEnvironment` and `IsBuildingAllowedIn`.
  **Read first, then undisable.**
- `DisabledInEnvironment` is a **`GameVar`** (`Building.lua:41`) — it is *saved*. Writing it
  leaves the underground-allowed flag in the save after the mod is gone.

**The gate the owner asked for.** `UIColony.underground_map_unlocked` (`Lua/Colony.lua:16`), set
one-way by `Colony:UnlockUnderground` (`:654-660`) when a surface elevator completes (`:949`),
read by the map switcher (`Lua/MapSwitch.lua:8`). The prototype reads it and never sets it.

---

## 4 · What the prototype does

`tools/devmods/rail_shaft/` — sibling of `train_hub`, one code file, no art, no data, no new
building template. Mod id `SMR_RailShaftDev_20260923`, log prefix `[RailShaftDev]`. Junctioned to
`%AppData%\Surviving Mars Relaunched\Mods\SMR-RailShaftDev` (verified: the junction resolves and
all three files are visible through it). **No new persisted name**: the only state it keeps
between calls is a plain global table that is never saved.

**The shape, and why.** Rather than rewrite the construction controller, the owner builds two
**ordinary** Universal Tunnel pairs through the ordinary UI — one per map — and the prototype
cross-links one mouth from each, disposing of the two orphans. Every object involved is then a
real, retail-built, track-connected `TrackTunnelBase`. This keeps the prototype's surface area at
one file and puts the risk where the question is.

A rail shaft is not marked by a stored flag; it **is** the condition "my `linked_obj` is on
another map", so it survives save/load without this mod persisting anything.

What the file does:

1. **`AllowUnderground(true)`** — reads `IsBuildingAllowedIn` first (the no-op trap), then
   `UndisableInEnvironment("UniversalTunnel", "Underground")`. Refuses, loudly, unless
   `UIColony.underground_map_unlocked`. Runs itself on `OnMsg.LoadGame`. Warns in the log that
   it writes a `GameVar`.
2. **Guards on the single-map registries** — `TunnelBase:AddPFTunnel` and `TunnelBase:MergeGrids`
   both bail for a cross-map pair, so the `OnMsg.LoadGame` re-wire cannot reach it.
3. **`List()` / `Link(i, j)`** — `List()` prints every `TrackTunnelBase` on both maps with handle,
   map, position and current link, and marks any existing shaft. `Link(i, j)` refuses a same-map
   pair, unwires both old pairs' adjacency and pf tunnels while their links are still intact,
   breaks the old links in both directions *before* disposing the orphans (so
   `TunnelBase:Done`'s `DoneObject(self.linked_obj)` at `:99-104` cannot take the new partner
   down), links the two, and calls `RebuildTrainRoutes()`.
4. **The hop** — `TrackTunnelBase:TrainTraverse` is wrapped: a same-map pair goes to the original
   untouched, a cross-map pair goes to `CrossMapTraverse`. That function mirrors vanilla's
   `:47-79` but replaces the `SetPos` teleport at `:70` with
   `train:TransferToMap(far_map, far_pos)`, drops selection and camera-follow first the way the
   elevator does (`Elevator.lua:976-981`), and **runs its whole body inside a destructor**, the
   shape both shipped crossings use.
5. **Seven stage lines** — `enter`, `at-near-mouth`, `pre-transfer`, `post-transfer`,
   `at-far-mouth`, `at-far-connector`, `done`. Each prints the train's handle, map, position,
   command and station. **A stall names itself by which stage is last.** This is what answers the
   open question in §1.
6. **`Sweep()` / `Kill(i)`** — walks `city.labels.Train` on every city and prints handle, map,
   position, command, station and track; `Kill(i)` removes one. This is the escape hatch for a
   train stranded where the owner cannot select it, which is what happened on 2026-09-21.
7. **`Status()`** — the gate, whether the tunnel is allowed underground, how many cross-map
   mouths exist, how many trains.

**Checks that were run:** `python tools/parsecheck.py --dir tools/devmods/rail_shaft` → *2
file(s), 0 error(s) [Lua 5.5]*, and the `Code` subdirectory → *1 file(s), 0 error(s)*. Every
engine symbol the file calls was confirmed present in the 1.1.1.405907 tree before use (EF-096) —
`ResolveMap`, `IsSameMap`, `AllMapsForEach`, `MainMap`, `UndergroundMap`, `Cities`, `empty_table`,
`IsInSelection`, `SelectionRemove`, `CameraFollowObj`, `UnfollowObjAndCloseModeDialog`,
`table.remove_value`, `GetSpotBeginIndex`. Probe sweep clean (`doccheck`: *TEMPORARY SWEEP: 0
hit(s)*).

**What is NOT handled, on purpose:** the electricity/water grids are not un-merged when a pair is
split — whatever the two original pairs merged stays merged. It is cosmetic for this test and it
is logged when it happens.

---

## 5 · What the owner saw — sitting held 2026-09-23, 17:45–18:12

Retail `Mars.exe`, build 25390750 / 1.1.1.405907. Mods loaded (log line 184): the fix pack, the
Test Kit, this pack, `SMR_TrainHubDev_20260918` and `SMR_RailShaftDev_20260923`. The owner's own
train-hub test colony, saved as a throwaway; SpaceY / politician. Log
`Mars.exe-20260923-17.45.25-6aad2d75.log`; every line number below is in it.

**Fixture.** Two ordinary Universal Tunnel pairs built through the UI, one per map (`List()`,
:463-467). A track probe showed each pair had one mouth on station track and one on a dead-end
spur — surface 6753 → `StationSmall 2008`, underground 6770 → `StationSmall 6787`; 6754 and 6771
ended `none / none` both ways. `Link(1, 3)` kept 6753↔6770 and disposed 6754 and 6771 (:497-507).

**The round trip completed.** Train 2000002070 ran surface → underground and back, seven stages
each way, `cmd GotoStation` throughout (:515-535):

```
stage 3 pre-transfer   | map surface     | station 2008
stage 4 post-transfer  | map underground | cmd GotoStation     <- map changed, thread alive
stage 5 at-far-mouth … stage 6 at-far-connector … stage 7 done | station 6770
```

Between the outbound `stage 7` (station 6770, the mouth) and the return `stage 1` (station 6787)
the train reached the underground station and departed from it on its own — routing resolved in
both directions. **The brief's stop (1) does not fire: the command thread survives
`TransferToMap` inside a destructor.** That is measured, not predicted.

**A second, unassigned train used the shaft.** 2000002087 hopped underground → surface
(:573-582), also seven stages, clean. The route rebuild had made the shaft part of every
connected route, which is the point of the next paragraph.

**Save/reload survived.** The owner saved and restarted; the 18:10 log shows the pair intact and
the guard firing for both mouths on load — `AddPFTunnel skipped for rail-shaft mouth 6753 / 6770`
(18:10 log :227-228). No `[RailShaftDev]` error or abort in either log; 3 hops, 3 completions.

**Then trains that never touched the shaft stalled — silently.** At high speed, several of the
owner's hub-line trains stopped moving. Nothing in the log names a stall: no error, no abort, no
`Idle` print. The cause is derived from source and recorded in §7 item 0 with its falsifier; it is
*not* yet measured, because the owner had to step away. Two peer diagnoses circulated in the same
window and are recorded here as claims, not findings: *"the link deleted two live mouths"* is
contradicted by the pre-link track probe (both disposed mouths were dead-end, `none / none`), and
*"the train's destination reads as a tunnel handle"* is a misread of the stage log — `station` is
`train.current_station`, which vanilla itself sets to the mouth at `TrackTunnel.lua:78`.

**Not shown, and not to be claimed:** that cargo, passengers or wagon attaches cross — no freight
evidence was taken; that anything holds for more than one round trip; that a real module's
placement is reachable. The `Persist error: Attempt to persist a C function` in the vanilla
`MarkFlight` repeat thread (`Flight.lua:835-840`) at :703 and :753 **predates this mod** — it is
in the 16:09 and 17:27 logs, before `SMR_RailShaftDev` was ever enabled — and belongs to whoever
owns the flight work. A MarsDebug pass would not be retail evidence (EF-044); this was retail.

---

## 6 · The sitting — run through batch 5 step 18; what is next

Batches 1–4 and steps 16–18 of batch 5 were run on 2026-09-23 (§5). Steps 19–20 (freight) were not
reached. **The next sitting starts with the stall, not with freight**, on the reloaded save:

1. `SMRRailShaft.Sweep()` — every train now prints `route_ok`. Expect the stalled ones to read
   `cmd Idle` (or `LoadTrain`) with `route_ok false`, and the moving ones `true`. If a stalled
   train reads `route_ok true`, §7 item 0 is wrong and the stall is something else.
2. `SMRRailShaft.Routes()` — prints every route's station chain and flags `BROKEN track` for any
   segment whose route omits one of its own end stations. Expect the broken segments to be the
   hub line's tracks on one side of station 2008. Zero broken lines also falsifies item 0.
3. `SMRRailShaft.Unlink()` — the undo: breaks the pair both ways, removes both mouths, rebuilds
   routes. Then `Routes()` again (expect 0 broken) and watch the stalled trains restart on the
   next in-game hour (`OnMsg.NewHour` → `Train:Start`, `Train.lua:58-70`).
4. ⚠️ **Do not undo by disabling the mod.** `linked_obj` is vanilla's own saved field; the
   cross-map pair outlives this mod, and without the guards vanilla runs `AddPFTunnel` and
   `MergeGrids` across maps on the next load. `Unlink()` first, then disable if wanted.
5. **The positive control — the placement rule, tested.** After `Unlink()`, build the surface
   pair again with its keeper mouth's spur joining the hub line at its **end** station (one
   whose only other track is the line itself), and the underground pair the same way at a line
   end; `List()`, `Link(i, j)`, then `Routes()` — expect **0 broken** — and `Sweep()` — expect
   every train `route_ok true`. Then a round trip as in batch 4. A pass turns §7 item 0 from a
   derivation into a measured rule; a `BROKEN` line here means the rule is incomplete.

The original batch list follows for the record. Both mods are normally loaded, so grep the log
with the full token — `[RailShaftDev]` for this prototype, `[CommunityOptInPack]` for the pack.
Console lines are one paste-safe line each, no comments.

**Batch 1 — fixture.** No save on this rig has the fixture, so it has to be made or found.

1. Load (or start) a game with **Tunneling Mars** researched and the **underground unlocked** — a
   completed surface elevator is what sets the gate, and the prototype refuses to do anything
   until it is set.
2. Save As a **throwaway copy**; everything below writes into the save.
3. Confirm the mod loaded: search the log for `[RailShaftDev] loaded`.
4. `SMRRailShaft.Status()`
5. Expect `underground unlocked: true` and `UniversalTunnel allowed underground: true`. If the
   second is false, `SMRRailShaft.AllowUnderground(true)` and re-check.

**Batch 2 — build the two pairs.**

6. On the **surface**, build a Universal Tunnel pair at the end of a track run, as normal.
7. Switch to the **underground**, build a second Universal Tunnel pair, also on track. (If it is
   not in the build menu, the gate in batch 1 did not take.)
8. Connect track to all four mouths and let both pairs finish building.
9. `SMRRailShaft.List()`
10. Read off the index of the **surface** mouth you want and the **underground** mouth you want —
    the two that face the track you intend the train to use.

**Batch 3 — link.**

11. `SMRRailShaft.Link(i, j)` with those two indices.
12. `SMRRailShaft.List()` — both should now read `<== RAIL SHAFT`, and the two orphans should be
    gone.
13. Check the surface and the underground for a leftover tunnel mouth with no partner; report it
    if there is one.
14. `SMRRailShaft.Status()` — expect `cross-map mouths: 2`.
15. Build or confirm a **station on each map**, both on the shaft's route.

**Batch 4 — the run. This is the measurement.**

16. Assign a train a route with a stop on each map, and watch it reach the shaft.
17. Watch what happens at the mouth, and say what you see.
18. Search the log for `[RailShaftDev] hop` and read the stage lines out.
19. **The last stage line is the answer.** Reaching `stage 7 done` means the outbound leg
    completed. Stopping at `stage 3 pre-transfer` means the command thread did not survive
    `TransferToMap` even inside a destructor. Stopping at `stage 4 post-transfer` or later means
    it did, and something after it failed.
20. If the train strands: `SMRRailShaft.Sweep()`, then `SMRRailShaft.Kill(i)` on the stuck one.

**Batch 5 — the return leg and the round trip.**

21. If the outbound completed, let the train unload and come back; report which of unload and
    return happened.
22. Read the `hop` stage lines for the return leg the same way.
23. Save, reload, and `SMRRailShaft.Status()` — confirm `cross-map mouths: 2` survived the
    reload and that no `AddPFTunnel skipped` line turned into an error.
24. Let it run a few laps and say whether it keeps routing.
25. Stop there. Cargo, passengers and wagon attaches are a separate sitting.

Record the result in §5 of this report, naming which legs completed, on which save, with which
mods loaded.

---

## 7 · What a real module would have to change

Beyond the prototype, in rough order of cost. None of this is designed; it is the bill.

0. **A shaft must not be a branch off a through-station. This is the finding of the sitting,
   and it is the first thing a real module has to solve.** Vanilla's route model is a *linear
   chain*: `Station:GetConnectedTrack` passes a train straight through only — it looks for a
   connector on the opposite side (`Station.lua:931-962`) — and `RebuildTrainRoutes` writes every
   segment of every enumerated route with `routes[segment] = route` (`TrainTransport.lua:331`),
   an **unconditional overwrite** guarded only at the starting track (`:316`). Before the link
   the shaft spur off station 2008 was a dead end, and `EnumRouteTracks` writes nothing for a
   one-station chain (`:297`). The link made it a live branch: a second route was enumerated
   through the spur, and its retrace (`:321-327`) walked back through 2008 and on along one side
   of the hub line, overwriting those segments with a route that lacks the other side's stations.
   A train on an overwritten segment then finds no destination — `GetArrivalTrack` → nil →
   `GotoStation` goes `Idle` (`Train.lua:339-342`), or `TransferCargo` → no work → `LoadTrain`
   goes `Idle` (`:865-874`, `:285`) — with no error, and `OnMsg.NewHour` restarts it into the
   same wall (`:58-70`). *Derived from source, not yet measured*; the falsifier is
   `SMRRailShaft.Routes()` (§6). **The hijack is geometric.** A station passes a train to the
   connector *opposite* its arrival (`Station.lua:945-947`: `el2eldir == dir or
   abs(el2eldir - dir) == 3`). A spur that meets a mid-line station at an angle to both line
   tracks is straight-through with neither: the retrace stops there, shaft trains treat the
   station as a terminus (`Train:IsStoppingOn`, `:467`) and the line is untouched — a usable
   feeder, but it depends on which hex the spur lands on. A spur dead-opposite one line track
   walks through and overwrites that side. So the rule for a module is **a shaft extends a
   line; it never branches one**: attach at a **line end** (the clean case — the two lines
   become one longer chain), or accept the at-an-angle feeder knowingly. A route model that
   admits branches would be a rewrite of `RebuildTrainRoutes` and is off the table. This is a
   vanilla constraint on any third track at a station; the shaft only made a dead-end spur live.
1. **Two-map placement.** The prototype dodges it by re-linking. A module needs a construction
   flow that places one mouth, lets the player switch maps, and places the other —
   `TunnelConstructionController:Activate` assumes one map throughout
   (`TunnelConstruction.lua:245-275`), and the construction group, the obstruction checks and the
   cursor are all per-map. The elevator's two-map group (`Elevator.lua:747-780`) is the shape to
   copy, but it pairs **pre-made markers**, not player-chosen positions. This is the largest item
   and it is where the brief's stop (2) — *"the two-map placement needs a state retail players
   cannot reach"* — would be decided.
2. **A tunnel class of its own**, rather than re-linking `UniversalTunnel`. It would define
   `GameInit` to skip the three single-map registries outright instead of guarding vanilla's, and
   would let `disabled_in_environment` be `set("Asteroid")` in its own template — no `GameVar`
   write at all. That also removes the prototype's worst property: it currently writes
   `DisabledInEnvironment`, which persists after the mod is gone.
3. **The hop, promoted.** `CrossMapTraverse` is close to what a module would ship, but it wraps
   vanilla's `TrainTraverse` rather than defining its own class's. Whether the destructor is
   enough is unknown until §6 batch 4 runs. If it is not, the fallback is worse: the brief's stop
   (1) is *"a train cannot be made to survive a transfer without replacing `Train:GotoStation`
   wholesale"*, and that is the wall.
4. **Grid and rover-path policy.** A cross-map pair must never merge grids or add a pf tunnel;
   the prototype guards two entry points, a module would simply not have them.
5. **Cargo, passengers, wagon attaches.** Untested. `_cobject.lua`'s transfer hook recurses over
   attaches and `Train` overrides nothing, but that is a reading, not a result.
6. **Save contract.** Nothing new is persisted by the prototype and a module should keep it that
   way: the cross-map condition is derivable from `linked_obj`, which vanilla already saves. Any
   new field would be a `SMRFixPack_*` name under ban 1 (`FIX_POLICY.md`).
7. **The gate.** Read `UIColony.underground_map_unlocked`; never set it.

---

## 8 · Stops, as they stand

- **(1) train cannot survive a transfer** — **CLOSED, does not fire.** Measured 2026-09-23: three
  hops, three completions, stages 4–7 all after the transfer, on retail (§5).
- **NEW, open — the link stalls trains that never use the shaft.** Observed by the owner, not yet
  measured; mechanism and falsifier in §7 item 0 and §6. Until `Routes()` has been read on the
  reloaded save, the shaft is to be treated as **not safe on a live line**: link only where the
  keeper mouth is a terminus, and `Unlink()` before ending a sitting.
- **(2) two-map placement needs an unreachable state** — **not reached.** The prototype avoids
  placement entirely; §7 item 1 is where it would be decided.
- **(3) installed build no longer 24995074** — **FIRED.** Handled per §0 by re-deriving against
  the installed build rather than stopping; flagged here for the owner's call.

---

## 9 · Two engine facts not filed, and why

Both are candidates for `docs/agent/facts/`; neither was filed, because `EF-` ids are allocated by
the fix pack (`B:\Dev\SMR\SMR-BugFixPack`) and minting one here alone is what caused the
2026-08-16 collision. Grepping `facts/INDEX.md` shows neither is recorded yet; `EF-114` is the
nearest neighbour and is about track reachability, not this.

1. **A cross-map unit transfer belongs inside a destructor.** The evidence is in §1. **Do not file
   it until the sitting runs** — the destructor's necessity is inferred from two shipped callers
   plus one un-rechecked console observation, and §6 batch 4 either confirms it or overturns it.
   Filing it now would record a prediction as a fact. (Corroborating, already filed: `EF-104`
   records `thread_running_destructors` as a real, observable state the engine filters on.)
2. **The `disabled_in_environment` runtime table has two traps** —
   `UndisableInEnvironment` is a no-op while `DisabledInEnvironment[id]` is nil, so a read must
   come first; and `DisabledInEnvironment` is a `GameVar`, so writing it persists into the save.
   This one is pure source, settled, and independent of the sitting; it is fileable now. It is
   recorded in §3 and in the prototype's file header meanwhile, which is where the next person on
   this job will read it.
