# Drones chain L3 — flight-look sitting, stopped again (motion)

Second stop in the same attended sitting. L2R's under-deck route (`L2R_EXITROUTE_20260922.md`)
was flown and not objected to on this pass; the new finding is how the drone moves along it, not
which lane it uses. Stopped again under `3_FLIGHTLOOK_low.md`'s Stop #1 before any constant was
judged: no file under `Code/` changed and no `SMROptInHubFlight` value moved from L2R's guesses.

## What was run

- Hub selected in `train_hub_base`; `*r SpawnHubDrone()` then `*r SendHubDroneTo(SelectedObj)`
  over the under-deck route L2R built.

## Owner's observation, verbatim

> It works but it doesn't feel fluid, the drones move in what feels natural ways. The move in
> sharp straight up and down lines and jerk around a bit

> Normal drones move in what feels natural ways. These move in sharp straight up and down lines
> and jerk around a bit

> I will want all its actions to feel more fluid, and less fly on a wire

## Why this stops L3, not just this reading

The shape is explained by the current code, not by any tunable value:

- `F.PitPoints` (`Code/30_TrainHubDrones.lua:49-69`) builds pure-vertical then pure-lateral
  waypoints — descend at constant XY to the under-deck cruise, move at constant Z to the outside
  point, climb at constant XY to transfer height — a rectilinear, axis-by-axis path with hard
  corners, never a curve.
- `F.Update` (`:265-299`) moves position by per-axis linear interpolation (`axis()`) between
  consecutive waypoints, and sets heading exactly once, instantly, at each segment boundary
  (`SetAngle` fires only `if a.step ~= step`, `:291-293`). There is no heading blend, velocity
  carry-over or banking across a corner.
- None of the eleven `SetHubDroneTune` names (`:428-437`) — heights, distances, `ClimbRate`,
  `Speed`, the three timers — touch curvature or heading blend; they only scale segment length
  and duration. No combination of them changes the path's shape from rectilinear to natural.

L2's own report already named this a known gap: "direct position sampling, not native flight
physics, banking or smooth pathfinding" (`L2_FLIGHT_20260922.md`). Fixing it is adding an
interpolation/banking mechanism, which this link's Authority excludes ("no redesign, no new
mechanism").

## Pointer for the rebuild: native drone movement (owner's ask)

The owner asked that this go to whoever rebuilds the flight driver: look at the game's own drone
movement code first, since an ordinary Wasp already moves the way the owner wants this one to.
Read on installed build 24995074, archived tree
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908`:

- `Flight.lua:764` — `FlyingObject`'s parents include `ComponentInterpolation` and
  `ComponentCurvature`, native engine components for smooth position interpolation and turning
  curvature. The console prototype's drone carries these components (it is a real `FlyingDrone`)
  but never uses them: `F.Update` drives it by calling `drone:SetPos(...)` directly every
  `SampleTime` tick instead.
- `Flight.lua:1037-1091`, `FlyingObject:FlightGoto` — the native per-tick flight driver. It calls
  an engine path solver (`Flight_Step`, `Flight_FindPathSync`) and reads a velocity vector
  (`GetVelocityVector`), rather than lerping between hand-picked waypoints.
- `FlyingDrone.lua:209-379`, `FlyingDrone:Goto`/`TerrainGoto` — how an ordinary Wasp reaches
  `FlightGoto`. This is the same class our repair drone already is.

**Not a claim that `FlightGoto` fits this route as-is**: OI-25's pit column and the under-deck
duck are geometry `FlightGoto`'s terrain/dome-aware pathing was not built for, and L2's report
already found "layers 3/2 cannot express the full ride solely through vanilla inputs/tail calls"
for parts of this flight. The rebuild's job is to find how much of the free-flight legs (the
outside climb/cruise/transfer, at least) can go through native interpolation/curvature or a
comparable heading-blend across corners, keeping the current hand-scripted waypoints only where
native pathing cannot express the route (the pit column, the under-deck duck, hidden tunnel
legs). Report which legs moved to native movement and which stayed scripted, and why.

## Handoff

Open question for the rebuild: make the drone's motion read as flight, not a segment lerp —
heading blend/banking through corners at minimum, ideally reusing `ComponentInterpolation`/
`ComponentCurvature` or `FlightGoto` where the route allows it. Whichever it settles, hand link 3
a fresh `## Notes from upstream` with the retained/changed constants before this sitting resumes.

## State

- No `Code/` file changed this sitting; L2R's route/topology stands, only motion is in question.
- `SMROptInHubFlight` values remain L2R's guesses.
- `03_Drones/README.md` and the project `README.md` are re-flagged blocked in this commit.
- `3_FLIGHTLOOK_low.md` is not deleted; its Lifecycle fires only on settled values.

## Drift and handoff inventory

| Finding / departure | Evidence | Home and next action | Disposition |
|---|---|---|---|
| Flight motion is rectilinear/instant-heading, not tunable | Owner's sitting observation (verbatim above); `F.Update`/`F.PitPoints` code read | Rebuilt link 2; consider native `ComponentInterpolation`/`ComponentCurvature`/`FlightGoto` | Stop #1 fired again; L3 blocked pending rebuild |

Execution recorded from the transcript: primary Claude Sonnet 5; no subagents.
