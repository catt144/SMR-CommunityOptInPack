# The geometry oracle: predict what the game will do, before the game shows it

**LIVE, fire when ready. Fire it before build 3b** (`TRAIN_HUB_TRAINS_high.md`): 3b is pure train
choreography, which is exactly what this predicts, and 3b is where a wrong guess costs the owner an
evening. This build changes no mod behaviour, so it can run beside a held build safely.

## Authority

**Owner, 2026-09-19.** Every failure in the train hub so far has been one species: a coordinate or
transform mismatch between Blender space, the Mod Editor's importer, the game's hex grid and
vanilla's own spot conventions. The footprint read as 85 hexes instead of 61; four of six lines
could not attach; cargo cubes landed beside their beds; trains dropped through the deck to the
floor; trains slide across the open interior and jump to the far side on departure; the stub's
width was never measured until build 3; a height "fault" was ruled by eye that measurement says
does not exist. **None were logic bugs. All were geometry.** Each was caught the same expensive
way: the owner's eyes, in game, after a manual Mod Editor re-import.

The owner's ruling: **this is the part that must not fail, so build it the instrument it lacks.**
Twice it already worked — the footprint check and the cargo-grid fix were predicted from the entity
file, and the game then agreed first try. Those scripts are kept as the seed, in
`C:\Dev\SMR-Assets\_shared\geometry\` (`README.md` there says what each one proved).

`FIX_POLICY` §0 sets this mod's risk standard. Neither ban is engaged: this build ships no game
code and adds no persisted state.

## The job

A harness that answers, **from files on disk alone**, what the game will do with a piece of geometry,
so a mistake is found before a re-import and before a sitting. Its invariants are independent, and
each is a separate verdict:

- **Footprint**: hexes, count, the inset, the six line radii, whether the lattice reading matches.
- **Spots**: every spot's world position and angle **as the game will read them**, through the
  measured importer mapping.
- **Cargo**: where a bed's 60 cubes land, and how many are on the bed.
- **Train choreography**: each train's path through the hub, per line and per departure kind.
- **Clearance**: those paths against the ring wall, portal legs, pillars, beams, cargo stacks, dome.
- **Two trains**: whether two paths overlap in space and time.
- **Lane alignment**: our arrival/departure spots against the incoming track element's own spots.

## Measured rules it starts from (each with how it was learned, and a falsifier)

Full list and provenance: `C:\Dev\SMR-Assets\_shared\IMPORTER_FACTS.md`.

- **Importer axis mapping**: Blender `(x, y)` m → game `(-y, -x)` × 100, after the pipeline's 30°
  turn (`export_prep.py` `TURN_DEG`). MEASURED from the first import. Falsifier: any spot in
  `Entities/SMROptInTrainHub6.entjson` that the mapping misplaces.
- **Spot angle**: a Blender spot's `rot_z` becomes the game angle `330 - rot_z`. MEASURED
  2026-09-19; the seed script reproduces all six Box spots from it.
- **Cargo grid**: columns run along the spot's game angle, rows 90° on; a bed is 12 × 5 = 60
  columns (`Station.lua:99-100`); a layer is 1.01 m; `max_z` is derived
  (`MultiResourceDepot.lua:RecalculateDerivedMaxZ`). MEASURED from a console dump of five cubes.
- **`Train:GotoSpot` is a straight timed slide**, not pathing: `SetPos(spot_pos, move_time)` with
  pitch handling only, no yaw (`Train.lua:507-519`). This is why the whole choreography is
  predictable, and why it shows in a building 80 m across.
- **Vanilla's choreography**: arrive → `Ramparrive<k>` → `Stop<k>`; depart on `j` → `Rampdepart<j>`
  → the element's `Enter1/2`; depart on the arrival track → `SetPos(Spawn<k>)` + `SetAngle`, a
  teleport, then `Rampdepart<k>` (`Station.lua:1085-1118`, `:1183-1207`).
- **Our spots are computed, not modelled**: `20_TrainHub.lua` `synthetic_spot_pos`, `kind_sevenths`,
  `train_deck_height`. The harness must read them from the Lua's own numbers, not a copy.
- **Track element**: `bbox_xy=1000x204`, `bbox_z=-1726..1069`; the vanilla train level and ours are
  equal, `stub=10800:running=10800` on all six lines (build 3's slot dump, `track_height_rows`).

## The bar: it must retrodict the failures we already saw

**A harness that only agrees with the current, working files proves nothing.** Before any prediction
about 3b is believed, it must reproduce the known corpus from the files and observations that
produced them — each is recorded with its evidence in
`docs/agent/reports/TRAIN_HUB_SITTING_20260919.md` and `TRAIN_HUB_BUILD_20260918.md`:

1. the pre-inset entity read as **85** outline hexes, with four lines at radius 5 and two at 4;
2. the current entity reads **66**, radii 4 × 6 (in-game slot dump agrees);
3. the pre-fix Box spots put **1 to 5** of 60 cubes on a bed; the current ones put **60**;
4. the pre-`6123ae7` synthetic spots put trains on the **ground**, a full deck height below the beam;
5. the current spots reproduce what the owner saw: the interior slide, the far-side jump on a
   same-track departure, the sideways shift into the portal legs.

⛔ **Do not tune the model until the numbers fit.** If a case cannot be retrodicted, that is the
finding: report the gap and what measurement would close it. A model fitted to its own answers is
the one failure this build exists to prevent.

## Rules must be triangulated, not derived once

Every failure above came from a rule known from a single source. A rule enters the harness only
with **two independent derivations that agree** — from the game source, from the entity file, from
an in-game dump, or from a vanilla asset read the same way. Where they disagree, or only one
exists, the rule is marked `UNCONFIRMED` in the output and every verdict resting on it is marked
too. **This is where fan-out earns its keep**: independent derivation by separate workers is worth
more than one worker checking twice. Your call how many and along which cuts.

## End state

1. **The harness runs from the command line** on a named entity file plus the hub's Lua, prints one
   verdict per invariant, and exits non-zero on a failure. Machine-readable output beside the
   human one.
2. **Its rules carry their provenance** in the output: what was measured, when, and which of the two
   derivations agreed.
3. **The retrodiction corpus is a test**, run every time, each case named. A case it cannot
   reproduce is reported, not silently dropped.
4. **A selftest** in the repo's style: break each invariant deliberately and prove the harness
   catches it. An oracle nobody has tried to fool is not an oracle.
5. **3b's questions answered ahead of it**, as a report: the lane offset; where a train actually
   goes today per line and per departure kind; which of those paths cross the ring, the legs or the
   stacks; whether two trains can meet. Numbers, with the rule each rests on.
6. **`IMPORTER_FACTS.md` updated** with anything newly measured or newly triangulated.
7. **Placement: your call, recorded in the commit message.** `C:\Dev\SMR-Assets\_shared\geometry\`
   fits its cross-mod purpose and its seed; this repo's `tools/` gives it doccheck's compile and
   catalog discipline. It must not require this repo's tree to run.

**Done means:** a change to the hub's geometry or its spot Lua can be checked in seconds, from
disk, with a verdict per invariant and its rules' provenance — and the harness has already shown it
catches the five failures we paid for in evenings.

## Scope

In: the harness, its rules, its corpus, its selftest, `IMPORTER_FACTS.md`, and a report answering
3b's geometry questions. Out: changing the hub's geometry, its spot Lua, or the Blender pipeline —
this build predicts, it does not fix. A geometry fault it finds goes in the report for 3b or the
look pass.

## Stops

- A rule has only one derivation and no second is available without the game: mark it
  `UNCONFIRMED`, say what in-game measurement would confirm it, and carry on.
- A retrodiction case needs state no file holds (a train's length or speed, an element's lane
  offset): report exactly what must be measured, in one paste-safe console line the owner can run.
- The choreography depends on vanilla code the harness would have to re-implement wholesale rather
  than read: report the boundary instead of guessing at it.

## Do not claim

Not "the hub's geometry is correct". Claim what the harness predicts, which rules it rests on,
which of those are `UNCONFIRMED`, and which of the five known failures it reproduced. A prediction
is not an observation, and this build runs no game.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` when the harness and its
report land. The harness itself is permanent; its home decides which repo's conventions keep it.
