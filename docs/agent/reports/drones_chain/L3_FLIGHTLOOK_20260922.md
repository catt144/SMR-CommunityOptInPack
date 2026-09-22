# Drones chain L3 — flight-look sitting, stopped before tuning

Attended sitting opened 2026-09-22 against the L2 console prototype
(`Code/30_TrainHubDrones.lua`, OI-25 pit geometry). Stopped under this link's own Stop #1
before any constant was judged or changed: the finding is a route/mechanism question, which
`3_FLIGHTLOOK_low.md`'s authority excludes ("no redesign, no new mechanism"), not a value
`SetHubDroneTune` can settle. No file under `Code/` was edited; no value in
`SMROptInHubFlight` changed from L2's guesses (`HoverHeight=300`, `Speed=6000`,
`LaunchTime=3000`, `LandingTime=3000`, `WorkTime=5000`).

## What was run

- Hub built and selected in `train_hub_base`; `*r SpawnHubDrone()` at the console.
- The drone lifted from `Pitfloor` through `Pitrim` to the exit column and hovered near the
  hub's central hoods, then near one of the hub's track-entrance portal arches. Two owner
  screenshots were reviewed live; not archived by this report.
- `*r ReturnHubDrone()` to clear the console visual before stopping.

## Owner's observation, verbatim

> So it comes out and hovers up, but its either going to have to fly out of one of the portals
> where it risks hitting and clipping through a train. or it needs to come out and through the
> bottom of the hub before it heads to a track

> It has room all around, its more about pathfinding and the best way to design that path
> right now

> just make sure we solve is it exiting from the space under, or using the train entrance
> portals

No clearance or hover-height defect was reported at the archway or against a train's profile
("room all around"); the open question is which physical lane the flight mechanism should use
to leave the hub, not how high it flies in either lane.

## Why this stops L3, not just this reading

`3_FLIGHTLOOK_low.md`'s Authority is tuning the named constants L2 built behind; its Stop #1
is exactly a flight that is wrong in a way tuning cannot fix. The two candidate exits — through
a train-entrance portal (a lane trains also use, the owner's clipping-risk read) or a separate
path under the hub deck — are alternate implementations of `F.Route`/`F.PitPoints`
(`Code/30_TrainHubDrones.lua`), which is link 2's mechanism, not a link 3 tunable. Judging
`HoverHeight` or any other constant against either candidate route would be tuning against a
path the owner has not settled, so no constant was judged this sitting.

## Handoff to a rebuilt link 2

Open question for the rebuild, in the owner's words: is the drone's route out of the hub the
space under the hub, or the train entrance portals? Whichever the rebuild settles (or an owner
ruling that a shared portal lane is acceptable), it should leave link 3 a route that does not
put the drone and a train in the same portal lane at the same time, recorded in a fresh
`## Notes from upstream` in `3_FLIGHTLOOK_low.md` before this sitting resumes.

## State

- `3_FLIGHTLOOK_low.md` is **not** deleted: its Lifecycle fires only once values are settled,
  which did not happen here. It stays in the chain, blocked on the rebuilt link 2.
- `03_Drones/README.md` and `Train_Hub_Project/README.md` are updated in this commit to show
  link 3 blocked pending the rebuild, per "Route, never drop."

## Drift and handoff inventory

| Finding / departure | Evidence | Home and next action | Disposition |
|---|---|---|---|
| Hub exit route is a mechanism/redesign question, not a tunable constant | Owner's sitting observation (verbatim above) | Rebuilt link 2; `F.Route`/`F.PitPoints` in `Code/30_TrainHubDrones.lua` | Stop #1 fired; L3 blocked pending rebuild |

Execution recorded from the transcript: primary Claude Sonnet 5; no subagents.
