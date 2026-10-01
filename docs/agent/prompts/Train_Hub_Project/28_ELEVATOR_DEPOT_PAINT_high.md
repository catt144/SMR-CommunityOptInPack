# Brief 28 — the Elevator Depot's paint pass, to production · _high

## Authority and outcome

The owner accepted the depot's shape on 2026-10-01: *"I did a full check of the desing, I think we
look good at this point. atleast until we get through testing and we do paint and final checks"*
(`reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md`, "The owner's acceptance"). This is that paint
pass. The owner, firing it: *"update the design prompt to fire paint work, get it production ready.
Probably match the general them of the train hub that we made while blending it in with the vanilla
elevator look."*

**The outcome:** the depot's own pieces (portal shell, apron and skirts, deck and pit, the core's
well, the underground receiver) leave their flat test swatches and carry finished maps (base
colour, normal, roughness/metal, the self-illumination mask), in **the train hub's theme**,
reading as part of **vanilla's Space Elevator at 75 %**, which they stand against. The shape stays
as accepted: a geometry change is a stop, not a decision. Spec §11 and the rulings carried in
parked brief `25` stand (the 75 % elevator, the portal, vanilla-station track ends, the hub as the
quality bar, vanilla's elevator untouched).

**Done when** the owner has seen the painted depot in their normal game, on both maps, by day and by
night, and said it is production ready, in words. Then this brief returns to the orchestrator.

**Yours to decide:** how the hub's theme carries over (its ivory hull, navy bands and blue glow
strips are the reference, not a template); how far each piece is taken; the resolution per map. Say
what you chose and why.

## Start

Authored at `48b4e63`. Run `git log --oneline -3` and `git pull` in this repo and SMR-Assets. Keep a
live todo list before any write, one item per commit-and-verify unit, one in progress. Build must be
**25579348** (`python tools/doccheck.py --emit-fingerprint`); cite source from that build's archived
tree under `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive`.

Read, in this order: spec §9 (the hub's asset facts and ship size) and §11; parked
`TRAIN_HUB_LOOK_high.md` "Facts that decide how you author this" and `01_TRAIN_HUB_STRUCTURE_high.md`
for how the hub's maps were made; parked `25_ELEVATOR_STATION_LOOK_high.md` "What exists" and
"Evidence" for the depot's pipeline (`SMR-Assets/elevatorstation/blender/`: `depot_build.py`,
`verify_depot.py`, the constants-then-verify-then-import loop); `SMR-Assets/_shared/IMPORTER_FACTS.md`.
The hub's art and bake scripts are in `SMR-Assets/trainhub/blender/`.

## Evidence (claims, each cleared by one check)

- The self-illumination map is a one-channel mask: it says where a surface glows, never its colour
  (`GFXMaterial.lua`; spec §9). The game dims it when the building stops working
  (`WorkLightsOn/Off`, `Building.lua`).
- One material per mesh node; a second node is discarded silently (`IMPORTER_FACTS.md`).
- The import copies textures into the mod as DDS. The 5 MB pack guard is the fix pack's and does not
  bind this mod (owner, 2026-09-21, spec §9): choose the resolution the look needs and report its raw
  size.
- The frame inside the core is vanilla's mesh, not an attach (brief 26's B1, `0d9e17a`). It stays.
- `verify_depot.py` is the desk gate for geometry; it must still pass after the paint work.

## Carried from brief 26 (its open items)

- **`receiver_z`**: the underground receiver's height is a guess and live-tunable
  (`SMRElevatorDepotDev.Set("receiver_z", n)`). Settle it by eye in this pass's sitting and bake it.
- **`Measure()` underground**: the nil-Z repair (`493f518`) still needs its native reading. Take it in
  the underground batch.
- **The core's frame**: ask the owner, against the painted core, whether it stays. Removing it changes
  vanilla's elevator: that is a stop if wanted.

## Scope

- In: the maps and materials of the depot's own entities (`SMROptInElevatorDepot`,
  `SMROptInElevatorDepotReceiver`), UV work they need without moving geometry, renders for the
  owner's yes, the Mod Editor import, the receiver height, the sitting.
- Out: geometry and footprint; vanilla's elevator, cabin, rope and track art (never restyle a vanilla
  material: it repaints every elevator in the colony); the depot's Lua behaviour and anything brief
  `27` owns; the hub's own art.

## Running beside brief 27

Brief `27` (the wiring) may be live; its row in this folder's `README.md` says. It owns
`tools/devmods/elevator_station/Code/10_ElevatorDepotDev.lua` and the template's behaviour fields. If
your work needs Lua, report it instead. **Do not run the depot's Mod Editor import while `27` is live**:
art, renders and the owner's yes go ahead in SMR-Assets; when you reach the import with `27` still
live, commit, write the import steps into your report and hand back to the orchestrator. Recheck
shared paths before every write.

## Stops — report instead of continuing if

1. The look needs geometry or the footprint to move.
2. A piece cannot reach the hub's quality bar without restyling vanilla's art.
3. The installed build is no longer 25579348.

## Claim limits

Do not claim production ready: only the owner's words do. Do not claim a look from a render; renders
earn the owner's yes before the import, and the game decides. Supported: `verify_depot.py`, the
importer's listing, `Report()` reads, the owner's words.

## The sitting

Render each piece from the owner's earlier screenshot angles (`SMR-Assets/elevatorstation/owner_feedback/`)
and put the renders in your report; get the owner's yes before the import. Commit a checkpoint before
the Mod Editor session and give the owner its steps a few at a time, naming the slot for each map. In
game: fresh placements on both maps, by day and by night, about five steps a batch, one prediction
per step; the owner clicks and reads, the orchestrator reads the log on flush. Console lines where no
SMRTK slot fits.

## Hand back

Report `docs/agent/reports/ELEVATOR_DEPOT_PAINT_20261001.md` (dated later if it slips): commits in
both repos, design calls, per piece the render, the maps and their sizes, what the owner said, the
import steps, the sitting batches, what you did not do. Commit with pathspecs in both repos. Update
this brief's row in this folder's `README.md`; do not delete or move this brief. Skills:
`doc-editing`, `smr-session-close`. House rules `CLAUDE.md`, process `docs/agent/WORKFLOW.md`, code
`docs/agent/FIX_POLICY.md`.
