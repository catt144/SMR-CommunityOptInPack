# Drones chain, link 2M2 — the motion, again: it must read as flight

**Link 2M2 of the `03_Drones` chain** (`README.md`), commissioned after the owner flew L2M's build.
Read, in this order: L2M's report `docs/agent/reports/drones_chain/L2M_MOTION_20260922.md` (what it
built and why), link 3's two stop reports (`L3_FLIGHTLOOK_20260922.md`,
`L3_FLIGHTLOOK_MOTION_20260922.md`), `DESIGN.md`, this folder's `README.md`, then your
`## Notes from upstream` below. `git log`, `git pull` both repos.

⛔ **Not yours:** `Code/20_TrainHub.lua` (link 4's, and the structure pass is in it), and all art —
`Entities/`, `Meshes/`, `SourceData/`, `Textures/`, and everything under
`B:\Dev\SMR\SMR-Assets\trainhub\`. Your file is `Code/30_TrainHubDrones.lua`.

## Authority

**Owner, 2026-09-22, having flown L2M's build (`74b1e4a`):**

> "Its studdered very bad coming out, the flight path is sorta better but still pretty sharp on the
> angles and its kinda glitchy / suttery when it lands to do the repair sequence. I needs the be,
> natural, fluid, and respemble flight."

Three faults, in the owner's order: **a bad stutter on the way out of the pit**; **corners still too
sharp**; **glitchy, juddery landing into the repair sequence**. The bar is one sentence: it must be
natural, fluid, and resemble flight.

**The route is settled and is not in question** (L2R): the pit column, the under-deck duck, the
outside climb, the over-track centreline ride, the descent to fix height. L2M's own verdict —
scripted planning with native *timed interpolation* for rendering, `SetCurvature(false)` and
`SetAcceleration(0)`, and a fresh timed `SetPos` every sample tick — **did not clear the bar, and is
not a constraint you inherit.** Reopen that verdict. L2M's clearance receipt, its Bezier work and its
tunables are evidence to use or discard, not a floor.

**The reference is in the game, not in our code.** An ordinary Wasp already moves the way the owner
wants. Fly one beside ours and match what it does: what it calls, how often it calls it, and what it
leaves to the engine. **If ours writes a position every tick and a vanilla Wasp does not, that
difference is the finding.**

**Orchestrator's call, 2026-09-22 — the deadline is a fence, not a leash** (the owner may overturn
it, and if they do, say so in your report). Earlier links held the drone to an exact position at
every instant, which is what forced per-tick position writes. It is not required. The repair's
authority is link 4's persisted deadline; the visual only has to **not outlast it**. So the engine
may own the flight and arrive a little early — the drone then holds, hovers or settles — and your
job is to make it never arrive late. Trade positional exactness for fluidity wherever that trade
buys motion the owner accepts.

## End state

1. **The three faults gone**, each addressed explicitly in the report: the exit stutter, the corner
   sharpness, the landing-into-repair judder. Say what caused each one — measured or reasoned from
   the code — and what you changed.
2. **The mechanism decided again, from the game's own behaviour**: how much the engine owns
   (curvature, acceleration, velocity, a native goto, long timed moves) against what stays scripted,
   and why, leg by leg. Both of L2M's disabled components (`ComponentCurvature`, acceleration) are
   back on the table; so is issuing one long engine-owned move per leg instead of a write per tick.
3. **The landing and work sequence is one continuous motion:** decelerate into the pose and hold;
   no animation, FX or state change may fire into an unfinished blend, and nothing may snap.
4. **Clearance re-measured** against the same envelopes and receipt shape L2M used
   (`tests/motion_clearance_receipt.json`): a curve that clips is worse than a jerk that does not.
   Report the new worst case and where.
5. **Tunables the owner can judge by eye**, named and defaulted to your best guess, with the ones
   you retired listed by name. Keep `SetHubDroneTune` as the way in.
6. **`tests/flight_smoke.py` updated** for what mocks can hold, plus one plain paragraph for the
   owner: **five steps or fewer** telling them what to fly and what to watch, with a vanilla Wasp in
   frame for comparison.
7. A report in `docs/agent/reports/drones_chain/`, the outcome in spec §10.

## Leads, not the route

Each of these is a suspicion from the code, not a verdict. Confirm or kill them.

- **The stutter:** `F.Update` issues a fresh timed `SetPos` every `SampleTime` tick, so each tick
  restarts an interpolation the previous tick had just begun, and the 100-game-ms prediction window
  rides on top. The owner's rig runs at a 120 fps cap, so frame time and tick time do not divide
  evenly. Check what a vanilla Wasp's call rate actually is.
- **The sharp corners:** L2M's rounding is bounded by `TurnRadius` (300 engine units, a guess) and
  by keeping every curve inside the original leg's hull, so the trim may simply be too small to see.
  A wider curve costs clearance; measure before dismissing it.
- **The landing judder:** cubic braking to an exact work origin, followed by the vanilla construct
  animation and FX, with yaw and roll still settling through their own interpolation.
- **The crest reversal** is designed to reach zero velocity in the shaft. That may read as a stall
  rather than flight; a gentler crest, or a shaped hold, may be better.

## Live work list

One todo item per commit-and-verify unit, before any write.

## Scope

In: the motion layer of `Code/30_TrainHubDrones.lua`, its constants, its smoke, the clearance
receipt, the report, spec §10. Out: the route's topology and lane, `20_TrainHub.lua`, dispatch,
economy, persisted state, art, geometry, train-awareness.

## Stops

1. The engine will not own the flight without taking the route or the destination with it: report
   the call path, and deliver the best hand-driven motion you can — but not another build that only
   moves the corner radius.
2. Fluid motion cannot hold the clearance envelope somewhere: report the numbers and the options.
   The geometry is the owner's to move.
3. The deadline cannot be kept as a fence (the visual would run late): stop; link 4 rests on it.

## Do not claim

Do not claim fluid, natural or flight-like from code, a smoke or a render — the owner's eye is the
only verdict, and this is the second build to be sent back. Do not claim a native component is in
use unless you can name the call path that reaches it.

## Notes from upstream

- **L2M (`L2M_MOTION_20260922.md`, build `74b1e4a`):** scripted Bezier spans, C1 at ordinary
  corners, eased reversals, filtered heading and bank, rendered through timed `SetPos` /
  `SetRollPitchYaw`; `SetCurvature(false)` and `SetAcceleration(0)` are explicit. Its source verdict
  was that `FlightGoto` and `FlyingDrone:Goto` own their own path and arrival, so it declined them
  to keep the exact route and deadline contract. **The fence ruling above removes that reason.**
  Defaults it left, all guesses: `TurnRadius=300`, `BlendTime=400`, `AccelTime=400`,
  `HeadingTime=400`, `BankAngle=180` (angle minutes).
- **Clearance as it stands:** conservative source-mesh bound 0.123799 m at Ring on the under-deck
  leg, 0.142959 m at the pit floor, 0.247822 m at Siding_1 near the crest
  (`tests/motion_clearance_receipt.json`). Not live clearance.
- **Still owed by link 3, do not consume:** the passing-train height check, the full route through
  stations, hoods, portals and tunnels, the work pose, worst live clearance, native command
  suppression, save cancellation and relaunch, and import survival.
- **The metadata code-list line** for `Code/30_TrainHubDrones.lua` has now been removed by an
  importer three times (`d48871e`, then again before `061d6cb`, then `5f3c3de`) and restored each
  time. Check it after every import; never merge the flight code into `20_TrainHub.lua` to dodge it.
- **Model note for the record only:** the owner is routing this link to a higher-tier model than the
  one that built L2M. Nothing in this brief checks or depends on which model runs it.

## Lifecycle

Append the settled motion, the retained and retired constants, and the five-step watch list into
`3_FLIGHTLOOK_low.md` §"Notes from upstream" as a fresh dated block; append drift to `6_QA_high.md`;
then **delete this file and remove its row from `README.md` in the same commit** (the map gate
rejects tombstones).
