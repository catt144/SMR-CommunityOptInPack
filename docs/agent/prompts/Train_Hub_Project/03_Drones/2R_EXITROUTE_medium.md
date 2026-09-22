# Drones chain, link 2R — the exit route: out under the deck, not through the portals

**Link 2R of the `03_Drones` chain** (`README.md`), commissioned by the orchestrator after link 3's
sitting stopped. Read `DESIGN.md` (settled design), link 3's report
(`docs/agent/reports/drones_chain/L3_FLIGHTLOOK_20260922.md`) and link 2's
(`L2_FLIGHT_20260922.md`), then your `## Notes from upstream` below. `git log`, `git pull` both
repos first.

⛔ **You do not open `tools/devmods/train_hub/Code/20_TrainHub.lua`** (link 4's, and the structure
pass is in it), and you touch no art: `Entities/`, `Meshes/`, `SourceData/`, `Textures/` and all of
`B:\Dev\SMR\SMR-Assets\trainhub\` belong to the structure pass. Your file is
`tools/devmods/train_hub/Code/30_TrainHubDrones.lua`.

## Authority

**Owner ruling, 2026-09-22: the drones leave and re-enter UNDER THE DECK, never through the train
portals.** In the sitting the owner said it plainly:

> "So it comes out and hovers up, but its either going to have to fly out of one of the portals
> where it risks hitting and clipping through a train. or it needs to come out and through the
> bottom of the hub before it heads to a track"
>
> "It has room all around, its more about pathfinding and the best way to design that path right
> now"

The ruling settles it: the under-deck lane. It is the space the owner already accepted when they
took the hangar under the deck (spec §9: drones fly out under about 6 m of headroom), and it never
shares a lane with a train, so **no lane guard, no waiting on train traffic, and no arbitration
logic is to be built**. A portal exit is not a fallback; if the under-deck lane cannot be made to
work, that is a stop, not a licence to use the arches.

OI-25 stands: the offset floor/rim column `point(-310,180,0)`, exit local z `+1000`. Everything else
link 2 built stays — the console driver, `Create` / `Send` / `Update` / `Remove`, the deadlines, the
save-start teardown. **This link changes the route, not the mechanism.**

## End state

1. **`F.PitPoints` and `F.Route` rebuilt for the under-deck lane:** pit floor → rim → an under-deck
   cruise height → outward between the pillars, clear of the hub's footprint → then the climb to
   the track hover height, outside the hub's envelope. The return is the reverse, and lands on the
   pit floor. The track-following half of `F.Route` is kept as it is.
2. **Clearance measured, not assumed**, and reported with the worst case and where it was: the deck
   underside, the gap the drone flies between (ring pillars, the seven centre pillars, the six cargo
   beds, the ring wall), and the outbound climb clear of the hoods and the portal arches. Spec §9's
   BVH numbers are a starting point, not your result: the mesh changed in `24ffa82`.
3. **New constants at the top of the file, named for link 3 to tune by eye:** the under-deck cruise
   height, the outward distance before the climb, and the climb rate, alongside link 2's existing
   `HoverHeight`, `Speed`, `LaunchTime`, `LandingTime`, `WorkTime`. Defaults are your best guess and
   say so.
4. **The offline smoke updated** (`tools/devmods/train_hub/tests/flight_smoke.py`) so the route's
   waypoints and the no-portal rule are checked without the game, and say plainly what only the
   game can answer.
5. A short report in `docs/agent/reports/drones_chain/`, and the ruling recorded in spec §10.

## Live work list

One todo item per commit-and-verify unit, before any write.

## Scope

In: `Code/30_TrainHubDrones.lua`'s route, its constants, its offline smoke, the report, spec §10.
Out: `20_TrainHub.lua`, dispatch, economy, persisted state, art, geometry, the model, and any lane
guard or train-awareness logic.

## Stops

1. The under-deck lane cannot clear the pillars, the beds or the deck underside anywhere in a wedge:
   stop and report with the measured numbers and the options (a different exit wedge, a lower cruise
   height, a geometry ask). The portals are not the answer, and the model is the owner's to move.
2. The drone cannot be made to fly a waypoint path at all without drone pathing: report; the design
   rests on it.

## Do not claim

Do not claim the route is clear, or that it looks right, from the offline smoke. Claim the
waypoints, the measured margins and the constants, and leave the verdict to link 3's sitting.

## Notes from upstream

- **Link 3 (`L3_FLIGHTLOOK_20260922.md`):** nothing was tuned; every constant is still link 2's
  guess. No clearance defect was seen — the owner said "room all around" — so this is a routing
  question only. Link 3 resumes on your settled route.
- **Link 2 (`L2_FLIGHT_20260922.md`):** the API and the console driver are proven against mocks
  only; native rendering, animation, AI suppression and palette are untested. Saves cancel the
  console visual; link 4 owns persisted resume.
- The metadata code-list line for `Code/30_TrainHubDrones.lua` entered history in `24ffa82`, which
  is not import-survival evidence. Confirm it survives the owner's next Mod Editor import.

## Lifecycle

Append the settled route, its waypoints and the tunable constants into
`3_FLIGHTLOOK_low.md` §"Notes from upstream" (a fresh block, dated), append any drift to
`6_QA_high.md`, then **delete this file and strike its row in `README.md` in the same commit**.
