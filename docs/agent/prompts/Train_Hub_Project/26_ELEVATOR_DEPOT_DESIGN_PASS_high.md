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


## Refire, 2026-09-30 evening: sitting B stopped; the three fixes are at the desk

The orchestrator-guided surface sitting stopped on code and art faults; the record and the
owner's words are in the report's
[Sitting B](../../reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md#sitting-b-surface-2026-09-30-evening-orchestrator-guided-stopped-code-and-art-owed)
section, screenshots in SMR-Assets `owner_feedback/sittingB_*`. All three are fixed at the desk and
recorded, with the evidence, in the report's
[three faults](../../reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md#sitting-bs-three-faults-fixed-at-the-desk-2026-09-30-late-evening)
section: `Report()` calls `GetEntityOutlineShape` as the global it is (`5a24b04`); the liner now faces
the tunnel, because the game culls back faces and the roof slopes away from the mouth, so every
camera under its plane saw through both sheets (`cbfac1f`, Assets; the mesh data had not changed
between imports, the angles had); the cabin is not drawn below the well's floor
(`cabin_hide_below`, `5a24b04`). A lip under grade beside the pit answers the saw-teeth; the stray
lines and the wedge are the roof's absence. The art changed, so in order: (1) the owner looks at
sheets 7-9 in `review_design_pass/index.html` and says yes or no in words (owner, 2026-10-01: *"Those
look good"*: done; do not ask again); (2) the editor
steps in that report section (the depot mesh only, which also carries the handoff's deferred `Top`
spot, `fffa61e`; no receiver, no hub save), then restart; (3) resume B from B1 with `Report()` as the
first read.

## Handoff, 2026-09-30 close-out

Resume **B/C's visual checks on both maps, then D's hub smoke** in the
[design-pass report](../../reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md#the-sitting-batches-one-prediction-per-step).
The eight design items above still need the owner's in-game acceptance. Keep this prompt in place
(owner, 2026-09-30: "Ok do your close out but don't remove the prompt").

Renders are approved; the depot and receiver imports (`e3e0832`) and hub save with generated smoke
PASS (`468d74d`, rechecked at `493f518`) are settled. Assets are at `cbfac1f`, which changes the depot
mesh, so one depot-only Mod Editor import is owed (the refire section above). Renders:
`SMR-Assets/elevatorstation/blender/review_design_pass/index.html`.

The rope blocker is resolved by the owner's "flushed, everything is working correctly now".
The current replacement depots and clean native census are recorded in the report's
[Owner confirmation](../../reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md#owner-confirmation-and-clean-current-fixture),
committed in `d627f3b`. Continue from that state without repeating the rope exercise.
`Measure()`'s nil-Z repair (`493f518`) still needs its native underground ceiling reading.

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
