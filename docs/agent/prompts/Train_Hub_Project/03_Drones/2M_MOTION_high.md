# Drones chain, link 2M — the motion layer: make it fly, not ride a wire

**Link 2M of the `03_Drones` chain** (`README.md`), commissioned by the orchestrator after link 3's
sitting stopped a second time. Read, in this order: `DESIGN.md` (settled design), link 3's motion
report `docs/agent/reports/drones_chain/L3_FLIGHTLOOK_MOTION_20260922.md`, link 2R's
`L2R_EXITROUTE_20260922.md`, link 2's `L2_FLIGHT_20260922.md`, this folder's `README.md` (OI-25 and
both blocked notes), then your `## Notes from upstream` below. `git log`, `git pull` both repos.

⛔ **Not yours:** `tools/devmods/train_hub/Code/20_TrainHub.lua` (link 4's, and the structure pass
is in it), and all art — `Entities/`, `Meshes/`, `SourceData/`, `Textures/`, and everything under
`B:\Dev\SMR\SMR-Assets\trainhub\`. Your file is `Code/30_TrainHubDrones.lua`.

## Authority

**Owner, 2026-09-22, in the sitting:**

> "It works but it doesn't feel fluid, the drones move in what feels natural ways. The move in
> sharp straight up and down lines and jerk around a bit"
>
> "Normal drones move in what feels natural ways. These move in sharp straight up and down lines
> and jerk around a bit"
>
> "I will want all its actions to feel more fluid, and less fly on a wire"

**The route is not in question.** L2R's under-deck topology was flown and not objected to: the pit
column, the under-deck duck, the outside climb, the over-track centreline ride and the descent to
fix height all stand. **This link changes how the drone moves along that route, and nothing else.**

**The owner's own ask for the method:** look at the game's own drone movement first, because an
ordinary Wasp already moves the way they want this one to. Link 3 cited the way in, on installed
build 24995074 from the archived tree `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908`:
`FlyingObject`'s parents include `ComponentInterpolation` and `ComponentCurvature`
(`Flight.lua:764`); `FlyingObject:FlightGoto` (`Flight.lua:1037-1091`) is the native per-tick
driver over an engine path solver and a velocity vector; `FlyingDrone:Goto` / `TerrainGoto`
(`FlyingDrone.lua:209-379`) is how an ordinary Wasp gets there. **Our drone is already a real
`FlyingDrone` carrying those components and uses none of them:** `F.Update` hand-drives it with a
per-axis `SetPos` every `SampleTime` tick and snaps `SetAngle` once at each corner.

This is an investigation with a build at the end. **How much of the ride can ride the native
system is your finding, not a given** — link 3 was explicit that it is not claiming `FlightGoto`
fits as-is, and link 2 already found that parts of this route cannot be expressed through vanilla
inputs alone. Answer it with the source and a test, then build the answer.

## End state

1. **The verdict, leg by leg.** For each leg — pit column, under-deck duck, outside climb and
   transfer, over-track cruise, descent to fix height, work, return, landing, and the hidden tunnel
   legs — say whether it moves to native movement (interpolation, curvature, a velocity-driven
   driver, or `FlightGoto` itself) or stays hand-scripted, **and why**. Free rein on the mechanism;
   a hybrid is expected, and "scripted but with a proper heading and velocity blend" is a legitimate
   answer for a leg native pathing cannot express.
2. **The motion reads as flight.** At minimum, across every corner in every leg: heading blends
   instead of snapping, speed carries through instead of restarting, and the axis-by-axis
   rectilinear shape is gone. Banking where the native components give it.
3. **Clearance survives the smoothing.** Rounding a corner eats the margin L2R measured against the
   deck underside, the pillars, the beds and the hoods. Re-measure the smoothed path against the
   same envelopes and report the new worst case and where — a curve that clips is worse than a jerk
   that does not.
4. **The deadline stays the authority.** Link 4 drives arrival, work and removal from persisted
   absolute deadlines; a native path solver may not be frame-deterministic. Keep the deadline
   governing: the visual may vary, the times may not. Say exactly how you preserved that, and what
   happens if the native driver arrives early or late.
5. **The drone's own AI stays suppressed.** Handing movement to a vanilla entry point risks handing
   over the destination, a command thread or charge-seeking with it. Prove it did not: no vanilla
   command may take our drone off our route.
6. **Constants.** Keep the tunables that still mean something, retire the ones the new mechanism
   makes meaningless (say which, by name), and add what link 3 now needs to tune by eye — turn
   radius or blend time, acceleration, bank. Defaults are your guess; say so.
7. **`tests/flight_smoke.py` updated** for what mocks can hold — waypoint order, clearance envelopes,
   deadline arithmetic, and no single-tick heading jump — and a plain statement of what only the
   game can judge. Fluidity is not in that set.
8. A report in `docs/agent/reports/drones_chain/`, the outcome in spec §10.

## Live work list

One todo item per commit-and-verify unit, before any write.

## Scope

In: `Code/30_TrainHubDrones.lua`'s motion layer and constants, its offline smoke, the report,
spec §10. Out: the route's topology and lane (settled), `20_TrainHub.lua`, dispatch, economy,
persisted state, art, geometry, and any train-awareness or lane-guard logic.

## Stops

1. The native system cannot be driven along our waypoints without its own pathing or AI overriding
   the route: report what it did, with the call path, and deliver the blended-scripted motion
   instead — that still answers the owner's ask.
2. Smoothing cannot hold clearance somewhere on the route: report the numbers and the options. The
   portals are still not an answer, and the geometry is the owner's to move.
3. The deadline cannot be preserved under a native driver: stop, because link 4 rests on it.

## Do not claim

Do not claim the motion feels fluid, or natural, from code or the offline smoke — only the owner's
eye settles that, in link 3. Do not claim a native component is in use unless you can name the call
path that reaches it; "the class inherits it" is not use.

## Notes from upstream

- **Link 3, motion (`L3_FLIGHTLOOK_MOTION_20260922.md`):** nothing was tuned in either sitting;
  every `SMROptInHubFlight` value is still L2R's guess. The route was flown and not objected to.
  The eleven `SetHubDroneTune` names (`:428-437`) scale segment length and duration only; none
  touches curvature or heading blend.
- **Link 2R (`L2R_EXITROUTE_20260922.md`):** the under-deck route, its clearances and the
  low-before-outside-climb order are settled and proved against mocks at flight source SHA256
  `8edffe9c…`; fixture deadlines arrival 10981, work end 16981, removal 27962 game ms, 13 created =
  13 removed. No native behaviour or clearance verdict follows from that smoke.
- **The metadata code-list line** for `Code/30_TrainHubDrones.lua` was silently removed once by an
  import (`git show d48871e -- tools/devmods/train_hub/metadata.lua`) and L2R restored it. It is
  still not import-survival evidence: check it again after the owner's next Mod Editor import, and
  never merge the flight code into `20_TrainHub.lua` to dodge the problem.
- **Link 2 (`L2_FLIGHT_20260922.md`)** named this gap itself: "direct position sampling, not native
  flight physics, banking or smooth pathfinding", and found that layers 3/2 cannot express the full
  ride through vanilla inputs and tail calls alone. Start from that finding rather than re-deriving
  it, and say where you confirmed or overturned it.
- **Still owed by link 3 when it resumes** (do not consume these): the train-pass height check, the
  full-route flight, the work pose, import survival, and behaviour across a save.

## Lifecycle

Append the settled motion, the retained and retired constants and what is left to judge into
`3_FLIGHTLOOK_low.md` §"Notes from upstream" as a fresh dated block; append drift to `6_QA_high.md`;
then **delete this file and remove its row from `README.md` in the same commit** (the prompt-map
gate rejects tombstones, so remove the row, do not strike it).
