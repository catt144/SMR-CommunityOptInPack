# Brief 25 — the Elevator Depot: a train tunnel that dives under the elevator (rewritten by the orchestrator, 2026-09-30) · _high

## Authority and outcome

**Two builds missed the owner's picture. This rewrite carries the picture itself.** Look at the
three reference images in `B:\Dev\SMR\SMR-Assets\elevatorstation\reference\` before anything else:

- `concept_owner_20260930.png` — **the owner's concept**, what to build toward: vanilla's tunnel
  mouth, shrunk to train size, at one corner of the space elevator, blended in so it looks like
  one clean building.
- `rejected_1_vanilla_tunnel_beside.png` — build one: the vanilla tunnel at 75 % beside the
  elevator, bigger than the elevator, its mound swallowing a pad. Rejected.
- `rejected_2_box_tube_with_arrow.png` — build two: a plain box tube lying across a pad. Rejected.
  **The red arrow the owner drew marks where the tunnel goes** (on the orchestrator's reading: the
  front of the base, at the foot of the central ring between the two front pads; confirm it
  against the image, and ask the owner if it reads differently to you).

**The owner's words, 2026-09-30, the rule for this brief:** *"this is the concept I send in that I
wanted basically a shrunk tunnel in one of the corners of the elevator and blended in to look
natural and clean."* *"I am fine creating our own custom one, but the quality of the train hub is
the bar for a custom module. I am fine with using vanilla's tunnel if it works, or slightly
cleaned up and updated looks. But it also needs to look right. With the shrunk elevator the tunnel
is bigger than the elevator. We need to blend whatever design we are doing so that it sits high
enough for the train to go into it, and tapers down towards the ground to make it look like the
train is going under the elevator in its storage hold to offload and then up and back out."*

So the look is:

1. **A tunnel mouth, not a tube on top.** The train enters at track height at the elevator's edge
   and **goes down under the elevator** into its hold; the portal tapers down to the ground. The
   train vanishes because it goes below grade, not because a tube is long. Lead, not a ruling:
   `Train.lua:507-512` slides a train to a spot's full position, so `Stop` spots below grade may
   take the train down and out of sight with vanilla movement alone. Prove it or report it.
2. **Sized to the train**, smaller than the elevator, never competing with it.
3. **Blended into the elevator's base**: one building, a skirt or apron joining portal to plinth,
   no mound swallowing a pad, no art floating on a pad.
4. **Quality bar: the train hub** (`B:\Dev\SMR\SMR-Assets\trainhub\`). Vanilla's tunnel art at a
   smaller scale, cleaned up, is acceptable if it reaches that bar. A primitive is not.
5. The rest stands: the 75 % space elevator, D1 (the surface cabin goes down into the ground,
   the underground one up into the ceiling), D3 (a working vanilla station, trains drive in),
   D4 (the dome build on hold). Spec §11's rulings stand: trains never change maps; cargo does;
   vanilla's elevator is untouched; each mod works with the other absent.

**How to work so the third build lands** (the orchestrator's instruction, from the two misses):

- **Show before you import.** Render the candidate from the concept image's angle beside
  the concept, in the repo, and put the render in your report. The owner says yes or names the
  change. Only then the Mod Editor import. One import per accepted render, not one per idea.
- **Do not invent a different shape** to sidestep a problem (the box tube was one). If the
  concept cannot be met, stop 2 below: report the options with numbers and pictures.
- Record the owner's words verbatim in the report before changing anything.
- The method still holds (owner, 2026-09-20): rough and fast, no gate between the owner and
  something to look at. A render is faster than an import; that is why it comes first.

**Done when** the owner places the Elevator Depot on both maps in their normal game and sees:
- the elevator with the tunnel mouth at the marked corner, one clean building;
- the cabin running its rope with vanilla's sound, D1;
- **a vanilla train driving into the mouth, going down out of sight, and coming back up and out**;
and says the look is accepted, in words.

**Deferred to a later design pass, by the owner (2026-09-30), so they do not eat this brief:** the elevator's core shows bare sandy ground inside its ring, and the frame seen inside the core reads wrong (`reference/later_core_shows_sand.png`, `later_core_frame.png`). Owner: *"this is minor we can save it for another design pass"*. Note them in the report; do not work them.

**Not this brief** (the wiring brief, after acceptance): the cabin carrying cargo between maps,
per-resource modes, the depot's own drone crew, the underground twin and its placement rule. The
owner's rulings for that are in `reports/ELEVATOR_STATION_LOOK_20260929.md` §6.

## Start

Rewritten on top of OptInPack `63ae577` (the tube-on-pad import) and the SMR-Assets HEAD at that
time; the reference images are uncommitted there until the next Assets commit. Run `git log --oneline -3` and
`git pull` in both, and keep a live todo list, one item per commit-and-verify unit, one in
progress. Game build must be **25390750** (`python tools/doccheck.py --emit-fingerprint`). Check
whether the game runs before writing the dev mod's `Code/` (PowerShell:
`tasklist /FI "IMAGENAME eq Mars.exe"`; Git Bash mangles the `/FI`), and tell the owner a restart
is needed when it does. Commit a checkpoint before every Mod Editor session: an editor save
renumbers `mod_handle`s and regenerates the template, its class and `_EntityData`.

## What exists

**The dev mod** `tools/devmods/elevator_station/` (`SMR_ElevatorStationDev_20260929`, title
*DEV ONLY - Elevator Depot (look prototype)*), junctioned into the game as
`%APPDATA%\Surviving Mars Relaunched\Mods\SMR-ElevatorStationDev`.
- Template `SMROptInElevatorDepotDev` on entity `SMROptInElevatorDepot`, `object_class`
  `SMROptInElevatorDepotDevBase` = `{ "Station" }`, in Stations, instant, no power draw,
  `disabled_in_environment = set("Asteroid")`. The class adds itself to the `Station` city label
  in code, as the hub does.
- `Code/10_ElevatorDepotDev.lua`: `GameInit` dresses each depot (a `[ElevatorDepotDev] dressed
  ... elevator=true tunnel=false cabin=true ropes=N scale=75` log line), `Done`/`OnDestroyed`
  undress, `LoadGame` re-dresses; the cabin cycle thread stops at every save. Console:
  `SMRElevatorDepotDev.Report()` (each depot's map, hex, `label.Station`, the 14 spots against
  the design table, connector elements), `.Measure()` (camera, elevators, ceiling objects),
  `.Show()`, `.Set("key", value)` (re-dresses every depot), `.Redress()`, `.Preview(scale, mode,
  rope_m)`, `.PreviewTunnel(scale, lift_m, angle_deg, entity)`, `.ClearPreview()`.
  `SMRElevatorStationDev` is an alias. Layout keys: `scale`, `elevator_entity`, `elevator_x/y/z`,
  `elevator_angle` (30), `tunnel_entity` (false; a vanilla entity name brings that art back),
  `tunnel_x/y/lift/angle`, `rope_surface_m` (0), `rope_underground_m` (300), `travel_down_m`
  (60), `travel_up_m` (0 = the rope), `leg_ms`, `dwell_ms`, `tick_ms`, `cabin_on`.
- The dome entities' import items and materials stay (D4). The depot reuses the dome body's
  material `SMROptInElevatorStation` and its swatch atlas, so it needs no material of its own.

**The base entity and its pipeline** `B:\Dev\SMR\SMR-Assets\elevatorstation\blender\` (Blender 5.2,
headless; its `README.md` "The Elevator Depot" has the commands and the owner's one-entity import).
- `depot_build.py`: every number the owner's eye may move is a constant at its top (`SCALE`,
  `ELEVATOR_ANGLE`, the connector hex, `TUBE_X0/X1`, `TUBE_HALF_W`, `TUBE_FLOOR`,
  `TUBE_WALL_TOP`, `TUBE_APEX`, `PORTAL_D`, the beam profile, `STOP_X`, `SPAWN_X`, the ramp
  distances). It writes the FBX, `export/depot_proof.json` and the dev mod's import item.
- `verify_depot.py`: re-imports the FBX and re-derives the footprint and the turn its own way;
  restates the spot table as literals, so a drift in either file shows. **Update its literals with
  every layout change**, or it fails on purpose.
- A change lands as: edit the constants → build → verify → the owner re-imports (Mod Editor: the
  Art Spec's MeshSpec `mesh`, Open in Importer, Import, save the mod: one step, no new
  EntitySpec) → restart if `Code/` changed → look. The dev Lua's `layout` defaults and its
  `design_spots` table must follow the constants by hand.

**State at handoff, 2026-09-30.** The rejected tube is still the imported entity;
`Trackconnector1` was read at (−4000, 0, 800), within 0.001 units, on OptInPack `de9ac7c`.
The owner's rejection and replacement concept are recorded verbatim in the reports; do not ask
them to repeat that feedback. No train has driven in yet. The ceiling is still NOT MEASURED.

A separate rounded, descending portal candidate now sits **between** the pads, with the elevator
turned 90°. Open `SMR-Assets/elevatorstation/blender/review_descent/index.html`: concept beside
render, plus mouth/top views. The portal is actual export geometry; the elevator is a dimensioned
render-only proxy, so the exact vanilla-mesh join remains unverified. `depot_candidate.py` builds
only `ElevatorDepot_candidate.blend` and `export/candidate_descent/`; it does not touch the dev mod.
`verify_depot_candidate.py` re-imports that FBX: static PASS. Full commands, hashes, dimensions and
spot table are in [the 20260930 report](../../reports/ELEVATOR_DEPOT_LOOK_20260930.md).

**Next: OI-33, the owner's render decision.** The proposed below-grade movement layout is held:
`study_depot_departure.py` finds conservative train envelopes overlapping the roof at the proposed
departure ramp. This is a desk check of these spots, not an observed game collision or proof that
every vanilla layout fails. After the shape decision, finish the vanilla spot/swept-clearance work
under this brief's stops, synchronize the production builder/verifier and dev Lua, and checkpoint
before one import. No custom movement was written. The live Lua still matches the rejected import.

**Records.** `reports/ELEVATOR_DEPOT_LOOK_20260930.md` (candidate renders, export proof and the
departure hold); `reports/ELEVATOR_DEPOT_LOOK_20260929.md` (§1–§5 the first depot, §6 the first view,
the dressing fix and the tube shape, §7 the owner's concept); `reports/ELEVATOR_STATION_LOOK_20260929.md`
(the dome build and the owner's evening rulings). Brief 25's row is in this folder's `README.md`.

## Evidence

Sources are `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src` (build 25390750); re-derive any
line number with `grep -n` before you lean on it. Entity data is `Packs/BinAssets.fpk:entities.dat`
(sha256 `64b68206…`), decoded with `SMR-Assets/_shared/geometry/entities_dat.py` as in
`reports/CROSSING_SHAPE_20260929.md` §9; `depot_build.py` and `verify_depot.py` restate the
elevator's 19 `hex_shape` triangles from it.

**The elevator's platform** (100 % values; ×0.75 in game). A tripod: three round pads of radius
1630 centred 3084–3157 out at 30.3°, 150.2° and 269.8°, a core ring of radius 2011 (circles fitted
by least squares to the `hex_shape` arcs); bbox z −1841..889, so **nothing on the platform stands
above 6.7 m at 75 % while a train rides at 8 m**: only the tube hides a train. `ELEVATOR_ANGLE = 30`
puts the 150.2° pad's centre at (−2313, −8), on the track axis. A positive game angle turns
counter-clockwise in the game's (x, y): the hub's reactor at offset (3897, 2250), local angle 30,
faces the centre with attach angle 210 (`20_TrainHub.lua:1144, :1283`).

**Vanilla `Station` needs, read 2026-09-29** (`Lua/Buildings/Station.lua`, `Lua/TrainTransport.lua`,
`Lua/TrackElement.lua`, `Lua/Units/Train.lua`):
- Spots `Trackconnector<i>`/`Trackdirection<i>` (1..4, loops fixed, a missing spot is skipped),
  `Ramparrive<i>`, `Stop<i>`, `Spawn<i>`, `Rampdepart<i>`, `Sign<i>`. Slots pair 1↔2: a train
  parked at `Stop1` is counted at `Spawn2` within 1 m (`Station.lua:1162-1164`), so `Stop1` =
  `Spawn2` and `Stop2` = `Spawn1`. Arrival: element `Enter<n>` → `Ramparrive<i>` (teleport if
  more than 50 m away, `:1105`) → `Stop<i>` (slide). Departure by the same connector: teleport
  to `Spawn<i>` facing its angle, slide to `Rampdepart<i>`, then to the element (`:1184-1205`).
  Trains keep to the right of their heading: arriving (+x into the mouth) on the −y lane,
  departing on the +y lane (±335, vanilla's `Stop1` offset).
- A connector accepts a track only on its `Trackdirection` hex (`TrackElement.lua:345-348`), which
  must lie outside the footprint, while the connector hex must lie inside it (`Tracks.lua:19-24`).
  A connector whose direction hex is inside the footprint is harmless and unreachable: that is
  how `Trackconnector2` is buried at (1000, 0) with its direction at the origin.
- A `Station` subclass is not in `labels.Station` unless it adds itself (`Building.lua:436-442,
  458-463`); `Train.lua:94, :134` walk that label. Stations keep 10 hexes apart
  (`Station.lua:59`): the owner places the depot at least 100 m from another station.
- Trains slide to a spot's full position (`Train.lua:507-512`); the hub's proven spots sit at
  z 800 (`corpus/current_5002a49.entjson`), so the depot's do too.
- A placed building has **no `template_name` field** (`Building.lua:2701` sets it only on the
  `BuildingTemplates` wrapper): test a building with `IsKindOf`, never that field. This cost the
  first placement its visuals.

**Footprints do not scale with art.** The game reads exactly the inset hex faces drawn
(`IMPORTER_FACTS`: the hub predicted 66 and read 66). The tube shape is **21 hexes** by the centre
rule (17 elevator, 1 the connector hex, 3 both), derived twice (`depot_proof.json`,
`verify_depot.json`). Falsify: the `[ElevatorDepotDev]` footprint in game, or slot 6's read.

**The train's length decides the look.** Vanilla track runs 8 m up; the train's box in its own
frame is x −1332..2818 (41.5 m, one in-game `GetEntityBBox` read on an assembled object), which
the owner disputes at about two hexes. The tube from x −36 m to −8 m hides 28 m. Take the cheap
read first: a superimposed build cursor shows the 10 m hex grid.

**The importer.** One mesh node and one material per entity; `hex_shape` faces inset 0.9;
Blender (x, y) → game (−y, −x) × 100; a spot's game angle is −(Blender rot_z). The editor keeps no
mesh spec until an entity file exists (`ArtSpecEditor.lua:565-603`), reasserts `ScenePath` over a
drag, and its save can drop code lines from `metadata.lua`: check it after every session. All in
`_shared/IMPORTER_FACTS.md`.

**Tooling on this rig.** The Bash tool's heredocs break past about 60 quote-heavy lines: write
such files with the Write tool, then `sed -i 's/\r$//'` (or `python tools/doccheck.py --fix-eol`
in OptInPack) before running, hashing or committing. `python tools/parsecheck.py --dir
tools/devmods/elevator_station/Code` is the Lua syntax gate. The game log is
`%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-*.log`, newest wins; the depot prints as
`[ElevatorDepotDev]`.

## Scope

- **In:** the tunnel mouth's shape, size, position and its blend into the base, the descent under
  the elevator, the elevator's turn, scale and offset, the cabin, rope and timing, the train spots
  and the footprint, all by the owner's eye; the renders before each import; the placeable dev
  building on both maps with trains in, down and out; live tunables; the sitting.
- **Out:** cargo between maps, store modes and the drone crew; the twin and its placement rule;
  vanilla's elevator; hub code and the hub's asset; the rail shaft.

## Stops — report instead of continuing if

1. A train will not enter, go down, stop and come back out through the mouth with vanilla
   `Station` code (it refuses the route, teleports, clips or sticks). Report with the log; do not
   write custom train movement.
2. The concept cannot be met at the hub's quality bar without changing vanilla's platform art, or
   the train cannot be hidden by the descent. Report the options with numbers and renders; do not
   substitute a different shape.
3. The installed build is no longer 25390750.

## Claim limits

Do not claim the look is accepted or that cargo crosses maps: nothing in this brief moves cargo.
What the owner saw is claimed only from their words, screenshots and the log. You may claim what
`verify_depot.py` re-imports and `Report()` read.

## The sitting

Console lines, not SMRTK slots, with this reason: at TestKit `587f474` all six slots and Scratch
in `B:\Dev\SMR\SMR-BugFixPack-TestKit\Code\80_AgentSlots.lua` are bound to the live train-hub
sittings, and rebinding one breaks them; slot 6's train/station stream serves the train batch as
it is. The owner accepts console lines where no slot is free (2026-09-27). About five steps at a
time; the owner clicks and reads, you read the log. Output: `[ElevatorDepotDev]` lines after a
flush, a screenshot, any Lua error first.

- **B — surface look, after the accepted candidate is ready and imported.** Load the normal game;
  the placed depot re-dresses on load. Look by day at the portal and its join to the base;
  `SMRElevatorDepotDev.Report()`; flush. Ask what moves.
- **C — the train.** Drag a track from a line's end to the mouth; set one depot row to Import so
  trains have work; slot 6's stream on; watch one train enter, vanish, come back out; flush.
- **D — underground.** Switch maps, place one, `Measure()` then `Report()`, zoom fully out at the
  lowest pitch: the rope must vanish into the ceiling. Move `rope_underground_m` by `Set()`.
- **E — by eye.** `Set()` for what the Lua owns (scale, turn, offsets, rope, timing); the tube's
  geometry and the spots are constants in `depot_build.py`: regenerate, verify, one-step
  re-import. Bake what the owner keeps.

## Hand back

Commit with pathspecs in both repos. Append to `docs/agent/reports/ELEVATOR_DEPOT_LOOK_20260929.md`,
or start `ELEVATOR_DEPOT_LOOK_<date>.md` if the day's work outgrows a section, with: your commits
and design calls; the measured footprint, spot positions, tube dimensions, rope height and the
ceiling read; what the owner saw and said, verbatim; what you did not do. Update this brief's row
in `README.md` here, and this brief's *State at handoff* when you stop short of acceptance. Leave
the file for the orchestrator to park or delete once the owner accepts the look. Skills:
`doc-editing`, `prompt-authoring` (for the wiring brief's notes), `smr-session-close`. House rules
are in `CLAUDE.md`, code policy in `docs/agent/FIX_POLICY.md`.
