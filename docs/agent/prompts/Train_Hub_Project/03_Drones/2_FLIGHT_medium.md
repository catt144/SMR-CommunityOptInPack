# Drones chain, link 2 — the flight prototype, in its own file

**Link 2 of the `03_Drones` chain** (`README.md`). Read `DESIGN.md` (settled design) and your
`## Notes from upstream` below, which link 1 wrote. `git log`, `git pull` both repos first.

⛔ **You do not open `tools/devmods/train_hub/Code/20_TrainHub.lua`.** It belongs to the hub link
(4) and to the structure pass running in parallel. Your code lives in a NEW file,
`tools/devmods/train_hub/Code/30_TrainHubDrones.lua`. Registering it in `metadata.lua`'s code list
is the one shared edit you make: the Mod Editor rewrites that file on the owner's imports, so
confirm the entry survives an import and say so in your report.

⚠️ The structure pass also owns the dev mod's `Entities/`, `Meshes/`, `SourceData/` and `Textures/`,
and everything in SMR-Assets. Touch none of them. No model, no texture, no spot.

## Authority

The owner, 2026-09-22: the flight and pathing half is built now, ahead of the hub half, so the hub
link starts with movement that already works. `DESIGN.md` §3 is the ride: **a vanilla Wasp, hovering
over the track**, following the track's element positions, never drone pathing, clear of the
side-hanging trains, one height value. Tunnels behave as `DESIGN.md` describes.

**The pit, not the pad** — the owner's ruling on the launch point is in the chain README. If it is
still open when you start, ask before building the launch, or build it behind a knob and say so.

## End state

A console-driven prototype, no dispatch and no economy:

1. `SpawnHubDrone()` puts a Wasp at the launch point and lifts it off; `ReturnHubDrone()` flies it
   back, lands it and removes it. Both from the console, both idempotent.
2. `SendHubDroneTo(<track element or break>)` flies it along the track's elements at a speed
   constant, plays the work state at the far end for a set time, and comes back. The travel time is
   a deadline you compute and report, so link 4 can drive it from persisted state later.
3. **Clearance proven, not assumed:** stations, the hub's hoods, the portals and a tunnel. Report
   the worst clearance you measured and where.
4. Battery topped up so the drone never seeks a charger (`DESIGN.md`; link 1 gives the thresholds).
5. Everything reads from constants at the top of the file, named for what the owner will tune by eye
   in link 3: hover height, speed, launch and landing time, work time.
6. An offline check of what can be checked without the game, in the shape of
   `tools/devmods/train_hub/tests/look_smoke.py` or one of your own; say plainly what only the game
   can answer.

## Live work list

One todo item per commit-and-verify unit, before any write.

## Scope

In: `Code/30_TrainHubDrones.lua`, its `metadata.lua` code-list line, your own tests, the report.
Out: `20_TrainHub.lua`, dispatch, the pending list, persisted state, any art or entity file, the
hub's economy and UI.

## Stops

1. A Wasp cannot be made to follow track element positions without drone pathing: report with what
   you tried; the design rests on it.
2. The code list will not hold a new file across the owner's import: report and hand the owner the
   one-line fix rather than moving your code into `20_TrainHub.lua`.

## Do not claim

Do not claim the flight looks right, or that clearance holds, from code or an offline check. Claim
the constants, the measured times, and what the owner still has to see.

## Notes from upstream

*(link 1 appends here: work-kind names, `DroneWork` animation and effect names, battery thresholds,
the pit's measured launch point and clearances)*

## Lifecycle

Append what link 3 must tune and what link 4 must call into their notes, then **delete this file and
strike its row in `README.md` in the same commit**.
