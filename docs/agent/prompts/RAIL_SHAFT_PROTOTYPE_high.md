# Rail shaft — research the map transfer, build a throwaway prototype · _high

> **STATE 2026-09-23 — partly consumed; only the sitting is left. Do not redo the research.**
> The research and the prototype are done and recorded in
> `docs/agent/reports/RAIL_SHAFT_PROTOTYPE.md`; the dev mod is built, parses, and is junctioned in
> at `tools/devmods/rail_shaft/`. **Stop (3) fired**: the game patched to 1.1.1.405907 / build
> **25390750** on 2026-09-23, so every source citation below describes a tree the rig no longer
> has. Rather than stop dead, every claim was re-derived against the installed tree and the report
> carries the new line numbers — read §1-§3 of the report, not the "What is already known" section
> below, which is now superseded. The 2026-09-21 log this brief cites has rotated off disk and
> cannot be re-checked. **What is owed: the sitting**, written out step by step as report §6, plus
> recording its result in report §5. Fire this brief only for that.

**Decided (owner, 2026-09-21).** The elevator cargo pain is an Opt-In Modules matter
(`docs/agent/reports/ELEVATOR_LOGISTICS_OPTIONS.md`). The owner now wants the bypass explored: a
train tunnel whose two ends sit on different maps, so a surface train runs down to the underground.
The elevator is **not** altered. Console testing is on hold: *"author a small prototype mod that
tests this properly, and explore the mechanism the elevator uses to transfer things and see if we
can reverse-engineer that for the tunnel."* Owner's method ruling: **prototype first** — rough and in
the game fast, the owner looks, then we adjust. No polish, no art, no gates between the owner and
something they can watch.

This is a **dev-only prototype**, not a module: nothing ships, nothing enters `Code/`, no module
record. MODULE FREEZE is lifted repo-wide and is not in play. `FIX_POLICY.md` still shapes the
design notes you leave for a real build.

## End state
1. A dev mod under `tools/devmods/rail_shaft/` (sibling of `train_hub`; junction it into
   `%AppData%\Surviving Mars Relaunched\Mods`) that lets the owner build a cross-map train tunnel
   and watch a train go down, unload, and come back — or shows exactly where it stops.
2. A report, `docs/agent/reports/RAIL_SHAFT_PROTOTYPE.md`: how a map transfer works for a unit,
   what a train needs that a rover does not, what the prototype does, what the owner saw, and what
   a real module would have to change. Append a short **option F** pointer to the elevator report.
3. One sitting with the owner, steps in batches of about five, then the result recorded.
Commit each with a pathspec. If time runs out, drop the report polish first, never the sitting.

Keep a live todo list. Start: `git log -3`, `git pull`; authoring sha `4ec0ed0`. An empty
`git diff --stat 4ec0ed0..HEAD -- docs/agent/reports/ELEVATOR_LOGISTICS_OPTIONS.md` and an
installed `buildid 24995074` (`python tools/doccheck.py --emit-fingerprint`) mean the facts below
hold. Cite from `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src\`.

## What is already known (each is a claim; one check clears it)

**Source, read 2026-09-21.**
- The game ships a train tunnel. `UniversalTunnel` (buildable) and `TrackTunnel` (hidden) both use
  `TrackTunnelBase` (`Lua/Buildings/TrackTunnel.lua`). The hop, `TrainTraverse` `:40-79`, drives the
  train into one mouth, `SetPos`-teleports it to the linked mouth, drives it out and sets
  `train.current_station`. It runs inside the train's own `GotoStation` command thread
  (`Lua/Units/Train.lua:338-413`, call at `:405`), which then carries on along the far track.
- Route building follows `linked_obj` with no map check (`Lua/TrainTransport.lua:251-300`,
  `Lua/Buildings/Track.lua:320-335`); `RebuildTrainRoutes` (`:302-358`) fills every city's
  `train_track_routes`. Routes and station lookups are otherwise per city
  (`TrainTransport.lua:227`, `Train.lua:94`, `:134`, `:839`).
- The engine's base tunnel already knows the cross-map case:
  `PFTunnel:TraverseTunnel` calls `unit:TransferToMap(end_point_map, end_point)`
  (`CommonLua/Movable.lua:620-627`). The signature is `(map, pos)`; shipped callers also pass an
  object on the target map (`Lua/Buildings/Elevator.lua:960`, `Lua/Units/Unit.lua:1025-1026`).
- The elevator's crossing is `ElevatorBase:UseElevator` (`Elevator.lua:939-979`): the whole body
  runs in `PushDestructor` / `PopAndCallDestructor`, and does `LeadIn` → `OnEnterElevator` →
  `TransferToMap(self.other)` → `SetHolder` → `Sleep` → `Disembark` → `OnLeaveElevator`. The stock
  rover tunnel uses the same destructor shape (`Lua/Buildings/Tunnel.lua:211-258`). `Train` is a
  `Unit` (`Vehicle`, `Unit.lua:1070`) and has destructors.
- Transfer hooks that fire per class: `_cobject.lua:157-170` (recursive over attaches),
  `CityObject.lua:73-84` (city and labels), `Unit.lua:934-944` (clears the command queue, drops a
  holder on the wrong map), `PinnableObject.lua:124`, `RevealDarkness.lua:275`, plus Drone,
  Colonist and RCRover overrides. `Train` defines none of its own.
- A stock tunnel's power/water link and rover path are single-map: `g_TunnelsAdjacency` is keyed on
  hex with no map (`Tunnel.lua:40-66`, read by C), and `pf.AddTunnel` (`:193-205`). A cross-map pair
  must skip both. Stock pairing and construction are single-map (`Tunnel.lua:23-31`,
  `Lua/Construction/TunnelConstruction.lua:254`); the elevator's two-map construction group is the
  precedent (`Elevator.lua:747-780`), but it relies on pre-made passage markers.
- `UniversalTunnel` cannot be built underground: the template leaves `disabled_in_environment` at
  its default, `set("Underground","Asteroid")` (`Lua/Buildings/Building.lua:252`); track and
  stations override it to Asteroid only. Runtime table: `DisableInEnvironment` /
  `UndisableInEnvironment` / `IsBuildingAllowedIn` (`Building.lua:89-104`).
- The gate the owner asked for exists: `UIColony.underground_map_unlocked` (`Lua/Colony.lua:16`),
  set one-way by `Colony:UnlockUnderground()` when a surface elevator completes (`:940-944`), read
  by the map switcher (`Lua/MapSwitch.lua:7-12`). Read it; never set it.

**Measured in the owner's game, 2026-09-21** (log
`%AppData%\Surviving Mars Relaunched\logs\Mars.exe-20260921-18.06.04-6a91a190.log`, lines
1188-1207; grep `TRAINPROBE|POSPROBE`). Two `UniversalTunnel` pairs, one per map, cross-linked from
the console; a console pre-hook called `train:TransferToMap(linked_obj)` with **no position**, then
the stock hop.
- The train (handle 2000002165) changed map and city: underground → surface. Transfer works on a
  train and the city bookkeeping follows.
- It kept its underground coordinates — (362000, 280873) against the underground mouth at
  (360000, 280584) — and never finished the hop: `current_station` and `track` still underground,
  command label `GotoStation`, position unchanged between two probes. No Lua error was logged.
- The owner cannot select it, so cannot demolish it. It is stranded in that throwaway save.
- A rewritten hop that passes the far mouth's position and runs in a destructor was written but
  **never run**. Whether the command thread survives a transfer is therefore still open.
- The console there has no `debug` library, and it does not log typed lines.

## The question
How does a unit actually cross maps here, and what is the smallest change that carries a train —
with cargo, passengers and wagon attaches — through a tunnel to the other map, keeps it routing,
and brings it back? Free rein on what to read, run or instrument. The console hop above is a lead,
not the route. Your call on the prototype's shape: a new tunnel template of our own (underground
allowed, no grid link, no rover path, two-map placement) or the cheapest thing that gets a train
across for the owner to watch first. Gate building on `underground_map_unlocked`. Give the
prototype a way to find and remove a stranded train (a label sweep is enough), and a logged line at
each stage of the hop so a stall names itself.

**Scope.** In: the cross-map train tunnel prototype, the transfer mechanism, the sitting. Out:
edits to either pack's `Code/`, the elevator, the train hub dev mod (a peer is working in
`tools/devmods/train_hub/` — recheck shared paths before writing), art.
**Stops** — report instead of pushing on if: (1) a train cannot be made to survive a transfer
without replacing `Train:GotoStation` wholesale; (2) the two-map placement needs a state retail
players cannot reach; (3) the installed build is no longer 24995074.
**Do not claim** "trains can run between maps". Write what was seen: which legs of the round trip
completed, on which save, with which mods loaded, and that routing, cargo and passengers beyond
that run are untested. A MarsDebug pass is not retail evidence (EF-044).

**Sitting notes.** Use a throwaway copy of a save with trains researched and the underground
unlocked; look for one before asking the owner to build it. Probe sweep first (WORKFLOW, Probe
hygiene). Owner-typed console lines follow `prompt-authoring`'s console rules. Both mods are
normally loaded; grep with the full `[CommunityOptInPack]` token. Skills: `doc-editing` before the
report, `smr-bug-library` if a finding is an engine fact worth filing.

**Lifecycle:** one-off; delete this brief and its map row when fired.
