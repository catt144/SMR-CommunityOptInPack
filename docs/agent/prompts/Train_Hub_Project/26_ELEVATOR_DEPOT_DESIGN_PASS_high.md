# Brief 26 — the Elevator Depot's second design pass, from the owner's list · _high

## Authority and outcome

The depot passed its sitting on 2026-09-30 as a test model on both maps (look, cabin, sound,
rope, trains: `reports/ELEVATOR_DEPOT_LOOK_20260930.md`, "Sitting"). The owner then walked the
model and named the fixes below, with screenshots. **This brief is that list, nothing more**
(owner: *"I think that is plenty for one design pass, we can eval after that"*). Spec §11 and the
rulings in brief `25` stand: the 75 % space elevator, the train-sized portal between the pads
that dives under the elevator, vanilla-station track ends, the hub as the quality bar, vanilla's
elevator untouched. Do not reopen the shape.

Reference images are in `B:\Dev\SMR\SMR-Assets\elevatorstation\owner_feedback\` (the `designpass_*`
files carry the owner's arrows). Look at each before touching its item.

**The list, in the order to work it.** The owner's words are the rule; the rest is the
orchestrator's reading.

1. **Floating element in the train's path.** A hazard-striped block hovers at the core-to-pad
   junction (`designpass_01_floating_element_and_open_back.png`, first arrow) and the same object,
   seen from the track, is a tall flat slab standing in the mouth in front of the wagons
   (`designpass_02_portal_interior.png`). Owner: *"a random floating element"*; *"that tall slab
   is the same floating element"*. Find what it is (an attach, a spot-placed prop, a leftover of
   the dev dressing) and remove or seat it. First, because it sits where the train goes.
2. **The portal's back is see-through.** From behind (`designpass_01…`, second arrow) and from
   inside (`designpass_02…`) the rear face is open. Owner: *"the back of the tunnel … is see
   through"*.
3. **The portal's interior: back wall and floor.** Inside, the floor is bare red sand. Owner:
   *"at the very least it should just be like a black wall like the base game's tunnel, preferably
   it should look a little cleaner like a tunnel entrance that's going below ground just for some
   flavor."* Minimum: an opaque dark back wall. Preferred: an interior that reads as a ramp going
   below grade (floor, walls, the descent), at the hub's quality.
4. **The track join at the mouth.** The vanilla track stops short of the portal, a flat
   plank-like stub sticks out of the mouth, and a blue rectangle outline lies on the ground
   between them (`designpass_03_broken_track_segment.png`). Owner: *"Broken segment, and I would
   prefer the track of our tunnel to look more like vanilla so it doesn't seem as odd."* The
   depot's own track piece is vanilla track (rail profile, pillars) and meets the line's last
   element with no gap, no plank and no stray outline. The connector geometry in brief 25 (the
   `Trackconnector`/`Trackdirection` hexes) is the constraint; the look must follow it, not move it
   without a reason in the report.
5. **The portal's blend into the base.** (`designpass_04_blend_and_core_shaft.png`, first arrow.)
   Owner: *"the tunnel should blend more in meeting the ground and kind of look like it's part of
   the elevator structure with its current blending, if possible."* The portal meets the ground
   the way the pads do, with a skirt or apron that reads as the same structure.
6. **The core on the surface when the cabin is down.** The central ring shows sand through its
   hole (`designpass_04…`, second arrow). Owner: *"The elevator when it's below ground should
   look more like a shaft, not bare ground."* A shaft: dark opening and shaft walls, never terrain. The frame seen inside the core
   (`owner_feedback/later_core_frame.png`, the earlier deferred item) is part of this item.
7. **All of the above on the underground depot too.** Owner: *"All of these problems also exist
   on the below-ground version."* Fix both; the sitting checks both.
8. **The core underground while the cabin is away.** Owner: *"when the elevator is moving and not
   at rest it shouldn't look like a shaft if possible, it should just look like a platform
   receiver of some sort."* Underground, the core is a landing bay waiting for the platform, not
   an open shaft. Read as: at rest, the cabin sits in the receiver; travelling, the receiver is
   visible and empty. If the owner's wording (*"plaftorm recivered"*) reads differently to you,
   ask before building it.

**How to work** (from brief 25, unchanged): render each item from the owner's screenshot angle
beside that screenshot, put the render in your report, and get the owner's yes before the Mod
Editor import. Expose what the owner will tune by eye; bake what they keep. Do not substitute a
different shape to sidestep a problem; if an item cannot be met at the hub's quality bar, report
the options with renders and numbers. Record the owner's words verbatim before changing anything.

**Done when** the owner has seen all eight in their normal game on both maps and said which are
accepted, in words. Then this brief goes back to the orchestrator.

## Folded in: the one editor session (owner, 2026-09-30)

Owner: *"If we are going through the full editor and import, design should just be folded into
it."* When the owner does the Mod Editor import for this pass, the same session also **saves the
train hub dev mod `SMR_TrainHubDev`** (title the hub's, not the depot's): brief `22`'s fourth
upgrade slot regenerates only on that save, and
`python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated` must PASS
before the restart. Put that step in your editor instructions to the owner, and run the check.
Brief `22`'s five smoke steps (`reports/TRAIN_HUB_STORAGE_20260929.md`, "Short attended smoke")
then run in this pass's sitting, after the look checks. Fixture: the owner's save **double
hub+elev** (two hubs, Capacity Network, a vanilla elevator, the depot pair placed).


## Handoff, 2026-09-30 evening (session 1 of this brief; the owner refired it for a thorough investigation)

**Where it stands.** Built, desk-verified, renders **approved by the owner** (*"approved"*; render gate
cleared, do not ask again). The owner's Mod Editor session is done: the depot mesh with the
`terrain_hole` surface and the receiver entity are imported (OptInPack `e3e0832`), the hub mod's save
for brief 22 is done and `cargo_upgrade_smoke.py --require-generated` PASSes (`468d74d`). The game
loads both mods clean; on load the depots dress `surface … ropes=0 receiver=false signs=0` and
`underground … ropes=4 receiver=true signs=0`. Report:
`reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md` (facts, design calls, verify figures, sitting
batches A-D). Renders and sheets: `SMR-Assets/elevatorstation/blender/review_design_pass/index.html`.
Assets commits `c5a8189`, `718390f`, `2c47118`; OptInPack `072f8f0`, `09507b0`, `f20212d`, `e68d374`,
`e3e0832`, `468d74d`, `0811edf`, `7e84783`.

**Open defect, first thing to investigate: a rope that outlives its depot.** Owner's screenshots,
underground map: a single rope standing on bare cave floor with no depot under it, after the depot
there was deleted earlier in the day (TestKit `selected_delete method=CheatDelete`, log
`Mars.exe-20260930-15.27.38`). It survives every reload of the owner's save **double hub+elev**, so
it is written into the save. Two fixes did NOT remove it (`0811edf`, `7e84783`): rope tiles now ride
as attachments, our props clear `gofPermanent`, a sweeper deletes props of invalid depots, and
`SMRElevatorDepotDev.Sweep()` also deletes parentless `SpaceElevatorRope`/`SpaceElevatorCabin`
objects with no vanilla `SpaceElevator` within 100 m. With the rope on screen the sweep printed
`swept 0 props of gone depots and 0 orphaned props` (log `Mars.exe-20260930-15.52.26:373`). Leads,
untested: (a) the sweep enumerates `AllMapsForEach("map", "Object", …)`; if the rope's class derives
from `CObject` only, it is never visited: enumerate `"CObject"` and match on `GetEntity()`; (b) the
rope may be the only thing left of an older, already-saved rig (surface `rope_surface_m` is 0, so
it is the underground one's, 4 tiles of 208 m at 75 %); (c) identify it directly in the console:
the object under the cursor, its class, entity, parent, `GetGameFlags` (permanent?), position, then
`DoneObject` it and save. Do not guess again: name the object first, then fix, then verify with a
reload. The old depots in that save are still placed (their hexes predate the footprint change) and
must be deleted for fresh placements; the sitting has not gone past batch A.

**Smaller findings, routed here, not yet filed:** a `[LUA ERROR] 10_ElevatorDepotDev.lua:354 attempt
to perform arithmetic on a nil value` in `Measure()` from the orchestrator's 12:23 sitting log (an
object with no scale or bbox in the sweep; not touched); vanilla prints `Missing spot 'Top' in
'SMROptInElevatorDepotDev'` when a depot is selected (its warning signs want a `Top` spot: add one
at the shell's crown at the next re-import); the receiver's import item first said `Origin` while
its FBX root is `ReceiverOrigin` (fixed in the generator, Assets `2c47118`; the editor's saved item
already says `ReceiverOrigin`). The two previous hub-save failures were the owner saving only the
depot mod; the hub's plain save works as it always did.

**Then continue with batch A step 3 onward** (report, "The sitting"), on the owner's schedule.

### Refired checkpoint, 2026-09-30: live identification next

OptInPack `493f518` adds `SMRElevatorDepotDev.InspectProps()` (read-only, CObject census with ownership)
and individual `RemoveInspectedRope(index)`, guarded against owned/attached/stale objects. The source
confirms the old `Object` sweep excludes the generated rope class, but the actual saved object still
needs its live row before removal. The report's
[Refired investigation](../../reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md#refired-investigation-2026-09-30)
holds the source evidence, desk checks and first live batch R1-R5. **Start at R1, then return to A3.**
No Mod Editor session is needed. `Measure()`'s line-354 failure was nil `GetPos():z()`, rather than the
handoff's scale/bbox lead; the checkpoint uses terrain-resolved `GetVisualPos()` and passes that desk
case. Native removal, save/reload, fresh-depot deletion and B/C/D acceptance remain open. The render
approval, successful imports and hub save remain settled; `Top` still waits for the next needed import.

## Start

Read brief `25_ELEVATOR_STATION_LOOK_high.md` "What exists" and "Evidence" first: the dev mod
`tools/devmods/elevator_station/`, its console (`SMRElevatorDepotDev.Report/Measure/Set/…`), the
Blender pipeline `B:\Dev\SMR\SMR-Assets\elevatorstation\blender\` (`depot_build.py`,
`verify_depot.py`, the constants-then-verify-then-import loop), the importer facts, and the
vanilla `Station` spot rules. Run `git log --oneline -3` and `git pull` in both repos; keep a live
todo list, one item per commit-and-verify unit, one in progress. Build must be **25579348**
(`python tools/doccheck.py --emit-fingerprint`); source is the archived tree for that build.
Check whether the game runs before writing `Code/` (`tasklist /FI "IMAGENAME eq Mars.exe"` in
PowerShell). Commit a checkpoint before every Mod Editor session.

## Scope

- In: the eight items, on both maps; renders; the dev mod's dressing and constants; the editor
  session including the hub mod's save; the sitting (look checks, then brief 22's steps).
- Out: the wiring (shared store, rows, drone crew, twin placement); the train's movement (it is
  vanilla station movement; if an item needs it changed, stop 1); vanilla's elevator, tunnel and
  track art as files; hub code; the rail shaft.

## Stops — report instead of continuing if

1. An item needs custom train movement or a change to vanilla's elevator or track.
2. An item cannot be met at the hub's quality bar without changing the shape ruled in spec §11.
3. The installed build is no longer 25579348.

## Claim limits

Do not claim an item is accepted; only the owner's words do. Do not claim the pass is complete
while any item is unseen in the game. Supported: what `verify_depot.py` re-imports, what
`Report()` and `Measure()` read, and what the owner said.

## The sitting

Console lines where no SMRTK slot fits (owner, 2026-09-27); about five steps at a time; the
owner clicks and reads, the orchestrator reads the log on flush. Batches: (A) editor session,
restart, the hub check; (B) surface: fresh placement, each item from its screenshot angle, cabin
down and the core; (C) underground: the same, cabin away and the receiver; (D) brief 22's five
steps. Write the batches into your report with one prediction per step.

## Hand back

Commit with pathspecs in both repos. Report in `docs/agent/reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md`
(or dated later if it slips): commits and design calls; per item, the render, what changed and
what the owner said; the editor-session steps; the sitting batches; what you did not do. Update
this brief's row in this folder's `README.md`. Do not delete or move this brief. Skills:
`doc-editing`, `smr-session-close`. House rules `CLAUDE.md`, code policy
`docs/agent/FIX_POLICY.md`.
