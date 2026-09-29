# Brief 25 — the Elevator Station's look, before any wiring · _high

## Authority and outcome

**Owner ruling, 2026-09-29**, in spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`
§11: the surface-to-underground crossing is an **Elevator Station pair with one shared store;
trains never change maps**. Read §11's table first; do not reopen it.

The owner's order, same day: *"Lets start with design before wiring, thats going to be the
hardest peice because it needs visual confirmation. The code for this should be significantly
easier, with everything we know."* **This brief is the look only.** The shared store, placement
rules and the underground twin are a later brief.

The look, from §11:

- A small version of the hub dome.
- A storage facility at its centre.
- A cargo-lift column rising from it. Underground, the column reaches into the cave ceiling, like
  the space elevator's line, so the building reads as a cargo elevator with tracks for trains.
- Track ends the same as a vanilla station's: one connector at each end. Trains stay outside the
  dome; there is no drive-through.
- A small footprint, because the underground is tight.

Done when the owner can **place the model on both maps in their normal game and look at it**.
Give it a minimal placeable building: no store, no range rule, no twin. Its track connectors sit
where a vanilla station's do, so the wiring brief inherits working geometry. Hand the owner
renders plus a short viewing sitting (SMRTK slots, `tools/SMRTK.md`). The owner then accepts the
look or gives adjustments by eye, and you iterate. The method (owner, 2026-09-20): rough and fast,
the owner dials it in; no gate between the owner and something to look at.

## Start

Authored at the orchestrator commit that added this file. Run `git log --oneline -3` and
`git pull` first. Keep a live todo list, one item per commit-and-verify unit, one in progress.

## Evidence

- **The hub's look work is the precedent.** Pipeline and facts are in spec §9 and the parked briefs
  `Parked/TRAIN_HUB_MODEL_high.md`, `Parked/TRAIN_HUB_LOOK_high.md` and
  `Parked/01_TRAIN_HUB_STRUCTURE_high.md` (maps, seams, lights, glass, reactor palette). The Blender
  source is `B:\Dev\SMR\SMR-Assets\trainhub\blender\` (Blender 5.2, headless). Derive the small
  dome from it; do not change the hub's own asset.
- **Measure cheaply first** (owner, 2026-09-20). A superimposed build cursor shows the 10 m hex
  grid in game. An agent-derived length once cost a gated build (`GEOMETRY_ORACLE_20260919.md`
  §13). The geometry oracle `B:\Dev\SMR\SMR-Assets\_shared\geometry\hub_oracle.py` is a spot
  check; its `--train-length-m` default carries the disputed 41.5 m.
- **Vanilla parts to match or echo.**
  - The vanilla station's entity and track spots, which the connectors must match.
  - The elevator's underground half.
  - The space elevator's tether look.
  - Decode entity data with `SMR-Assets/_shared/geometry/entities_dat.py`; the method is in
    `reports/CROSSING_SHAPE_20260929.md` §3/§9.
- **Cave ceiling height varies.** Check it near the elevators on the underground map, and size
  the column so it never visibly stops short. Report what you measured.
- **Where it can be built.** An underground build needs its own environment template. Never write
  the global `DisabledInEnvironment` (report §7).

## Scope

- In: the model, its materials, a minimal placeable dev building on both maps, the renders, and
  the viewing sitting.
- Out:
  - the store, the elevator range rule and the twin (the next brief);
  - vanilla's elevator;
  - hub code and the hub's asset;
  - the rail shaft (parked).

## Stops — report instead of continuing if

1. Matching the vanilla station's connector spots would force a footprint too large for the
   owner's "small".
2. Building underground needs vanilla's elevator or a global setting changed.
3. The installed build is no longer 25390750 (`python tools/doccheck.py --emit-fingerprint`).

## Claim limits

Do not claim the look is accepted; only the owner accepts it. Supported: which renders and which
in-game views the owner has seen, and what they said.

## Hand back

Commit with a pathspec. Report in `docs/agent/reports/ELEVATOR_STATION_LOOK_20260929.md`:

- your commits, the renders' paths and your design calls;
- the measured footprint, connector positions and column height;
- the viewing sitting;
- what you did not do.

Do not delete or move this brief. Skills: `doc-editing`. House rules are in `CLAUDE.md`, code
policy in `docs/agent/FIX_POLICY.md`.
