# Drones chain, link 3 — the owner tunes the flight by eye

**Link 3 of the `03_Drones` chain** (`README.md`). **ATTENDED: the owner is at the keyboard.**
Read `DESIGN.md` and your `## Notes from upstream`. `git log`, `git pull` both repos first.

## Authority

The owner's method (2026-09-20): rough and in the game fast, then dialled in by eye. Link 2 built
the flight behind named constants; this sitting sets them. No redesign, no new mechanism.

## End state

1. About **five steps at a time** for the owner, and a console tuner for each constant, the way the
   arm-light tuner works (`SetHubLightTune` is the pattern).
2. The owner judges, in one sitting: hover height over the track, travel speed, the launch and the
   landing, the work pose at the break, and clearance at a station, the hub's hoods, a portal and a
   tunnel.
3. Every value the owner settles becomes the new default in `Code/30_TrainHubDrones.lua` and is
   committed, with the owner's own words for why in the commit message.
4. The game cannot turn autosave off: after one, the owner re-presses the armed slot.

## Live work list

One todo item per commit-and-verify unit.

## Scope

In: the tuner, the sitting, the settled constants, the record. Out: `20_TrainHub.lua`, dispatch,
economy, art, anything the owner did not ask for in the sitting.

## Stops

1. The flight is wrong in a way tuning cannot fix: stop the sitting, record what the owner saw, and
   hand it back to a rebuilt link 2 rather than patching live.
2. The owner runs out of time: commit what is settled, and say in your notes which constants are
   still the agent's guess.

## Do not claim

Do not claim a value is the owner's unless they said so in the sitting; relay their words verbatim.

## Notes from upstream

- L2 implementation/report: `docs/agent/reports/drones_chain/L2_FLIGHT_20260922.md`.
  OI-25 is approved: offset floor/rim column `point(-310,180,0)`, exit local z +1000.
- Console [NEVER RUN in game]: select the hub, `SpawnHubDrone()`; select a track element/site,
  `SendHubDroneTo(SelectedObj)`; `ReturnHubDrone()` lands/removes it. Read
  `SMROptInHubFlight.Status()` for the absolute arrival/work/removal deadlines.
- Tuner [NEVER RUN in game]: `SetHubDroneTune("HoverHeight", 300)` after landing. Other names:
  `Speed=6000`, `LaunchTime=3000`, `LandingTime=3000`, `WorkTime=5000`. Height is engine units
  above rail origins; speed units/game second; times game ms. These defaults are guesses.
  `Palette=false` is deliberately untuned; the report explains the optional four-colour array.
- Required native checks: station connector spans, hoods, pit, portals and a tunnel, with the
  worst measured clearance/location recorded. L2 has no live clearance result. Mesh checkpoint
  `24ffa82` changed L1's geometry input; do not promote the old margins to current clearance.
  Tunnel concealment uses the deeper inner enter spot, an approximation to verify by eye.
- After a Mod Editor import confirm metadata still lists `Code/30_TrainHubDrones.lua`. If not,
  stop and provide that one-line registration fix; never merge its code into `20_TrainHub.lua`.
  Concurrent commit `24ffa82` includes the line but is not import-survival evidence.
- Saves cancel the console visual. Relaunch/re-send after autosave; L4 owns persisted resume.
  Mocked smoke passed; native rendering, animation, AI suppression and palette remain untested.

### L2R handoff, 2026-09-22

The under-deck route is implemented; resume this sitting. Read
`docs/agent/reports/drones_chain/L2R_EXITROUTE_20260922.md` and its receipt. Earlier L2 defaults
above are historical. OI-25's floor → rim → +1000 crest stays; then the drone lowers in that
column to +300, exits beneath the deck toward local XY `(-7794,-4500)`, climbs outside the
footprint to +2500, and transfers above the hub onto the track centreline. Return reverses it.
`SpawnHubDrone` still waits at the crest until sent. Judge that retained rise/lower visually.

Tuneable defaults (all guesses): `UnderDeckHeight=300`, `OutwardDistance=9000`, `ClimbRate=1500`,
`TransferHeight=2500`, `OverTrackHeight=1200`, `HoverHeight=300`, `FixHeight=100`, `Speed=6000`,
`LaunchTime=3000`, `LandingTime=3000`, `WorkTime=5000`. Use `SetHubDroneTune` after landing.
Track ride height is `OverTrackHeight + HoverHeight`: the former is a guessed train envelope,
the latter a buffer. Watch a train pass directly below the drone; no measured train height
supports these numbers. At the target, verify descent to +100, work there, then climb back.

Static source-mesh minimum is 0.347332 m at the column's siding edge (excluding the intentional
0.24 m floor separation); low outward margin is 0.792286 m at RingClamp_1. These are conservative
level-Wasp envelope bounds, not a native verdict. Check cargo stacks, crown light/attachments,
hoods, the pit, other stations and tunnel arches/concealment at the higher ride height.
Record worst live margin/location; never tune the exit into a train portal.

Import warning is now observed: `d48871e` removed the flight code entry. L2R restores it in
metadata, but the next editor import still owes a survival check. If absent again, stop under
this brief's existing import instruction. Save cancellation/relaunch and L4 resume duties stand.

### L2M handoff, 2026-09-22

Resume the attended sitting with motion build `74b1e4a`. Read
`docs/agent/reports/drones_chain/L2M_MOTION_20260922.md`. The route and normal arrival/work/removal
offsets stand. The motion now rounds ordinary corners with shared velocity, eases required
reversals/stops, filters heading and bank, and uses native timed position/rotation interpolation.
It does not use FlightGoto or ComponentCurvature. Early recall brakes along the curve and
retraces it; its new removal deadline includes that braking. No native flight ran in L2M.

All existing tuners remain; none was retired. New GUESS defaults: `TurnRadius=300` (maximum
corner trim in engine units), `BlendTime=400`, `AccelTime=400`, `HeadingTime=400` (game ms),
`BankAngle=180` (angle minutes, 3 degrees; 0 disables, maximum 300). Use the same
`SetHubDroneTune` after landing. Speed/ClimbRate now set nominal deadline budgets; eased
starts/stops can peak at 4/3 nominal rate. All defaults still need your visual verdict.

MEASURED source-mesh bound including bank, rounding and up to 100-game-ms interpolation:
**0.123799 m at Ring on the under-deck leg**, receipt `tests/motion_clearance_receipt.json`
under the dev hub. Pit-floor bound is 0.142959 m; crest-side example is 0.247822 m at Siding_1.
The report gives commands, hashes, filters and remaining geometry exclusions. This is a
conservative hull result, not live clearance. Rerun it after changing path/bank constants or art.

Still owed: judge fluidity/heading lag, bank direction, reversals and game-speed changes; the
passing-train height check, full route through stations/hoods/portals/tunnels, work pose, worst
live clearance/location, native command suppression, save cancellation/relaunch, and import
survival. Another texture import removed the code-list entry; concurrent `061d6cb` restored it.
Check the next import explicitly. L4 still owns persisted resume and economic deadlines.

### L2M2 handoff, 2026-09-22

Resume the attended sitting with motion build `d77efa4` plus `6d89b1a` (signed `BankAngle`) and
`b84f106` (**required**: `d77efa4` alone raises `HGE::l_SetAcceleration: Expected integer` on
`SpawnHubDrone`, EF-116). Read `docs/agent/reports/drones_chain/L2M2_FLUIDITY_20260922.md`,
its correction section first. **Step zero, before any drone:** paste
`*r print(7/2, 7*1.0/2, math.type(7/2))`; expect `3  3.5  integer`. Any other output, or any
`[SMRTK] SMRTK_ERROR` from `30_TrainHubDrones.lua`, stops the sitting under Stop 1 with the line
pasted verbatim; nothing is tuned on a build that errors. The route is
L2R's; the driver is new: the engine flies every chord (one timed `SetPos` + `SetAcceleration`
per chord, at most 333 ms, chained from a game-time thread), corners are rounded inside their own
legs and flown at the speed their radius allows, straights run a physical speed profile, the crest
reversal is a parabola through rest, and the landing decelerates to rest before any state change.
The L2M handoff above is historical; its `TurnRadius=300`, `BlendTime`, `AccelTime`,
`HeadingTime` and `SampleTime` no longer exist or mean the same thing.

Dials, all GUESS defaults, `SetHubDroneTune` after the drone lands: `Accel=1200` (units per game
second squared: how hard it speeds up, brakes and corners; the main feel dial), `TurnRadius=1500`
(units: how far before and after a waypoint a corner is rounded; 15 m), `BankAngle=900` (angle
minutes of lean in a turn, -2700..2700; **negative flips the lean direction** if it leans out of
turns, 0 disables), `Speed=6000` and `ClimbRate=1500` (caps, units per game second), heights and
distances unchanged (`HoverHeight`, `OverTrackHeight`, `FixHeight`, `UnderDeckHeight`,
`OutwardDistance`, `TransferHeight`), `WorkTime=5000`. **Retired:** `LaunchTime`, `LandingTime`,
`BlendTime`, `AccelTime`, `HeadingTime`, `SampleTime`. The launch and landing now take what
`ClimbRate` and `Accel` give them (about 3.3 s for the 30 m column). Every dial moves the
visual's own duration, so the console deadlines move with it; L4 derives from the plan offsets.

Five steps for the owner, with an ordinary Wasp in frame for comparison (a Drone Hub's Wasp
working nearby, or any Wasp on the map): (1) select the built hub in `train_hub_base`,
`*r SpawnHubDrone()`, and watch the rise: it should speed up, slow into the crest and hang there
without a jolt or a stop-start. (2) Select a track element two or three stations out,
`*r SendHubDroneTo(SelectedObj)`, and watch the exit in order: the dive to the lane, the swing out
under the deck, the run out, the climb, the crossing back over the hub, the S-drop onto the
track; name any hitch, pause or kink by place. (3) Watch the arrival: it slows into the pose
above the break, comes to rest, then the work animation starts; then the return and the landing
in the pit. (4) Run the same trip at normal, fast and fastest game speed: the motion should
scale, not stutter. (5) After it lands, dial `Accel` first, then `TurnRadius` and `BankAngle`,
re-sending after each change; record the values you settle with your own words.

MEASURED source-mesh bound for the new chords (per-span commanded roll, chords cut at span
boundaries): **0.240 m at PitFloor_1** (the intentional floor separation), 0.3435 m at Siding_1
on the crest-to-lane corner, 0.792 m at RingClamp_1 along the lane, over 4.4 m everywhere outside
the footprint; `tests/motion_clearance_receipt.json`. Conservative hull bounds, not live
clearance; rerun the export and measurement after changing any path dial or the art.

Still owed here, unchanged: fluidity and bank direction by eye, the passing-train height check,
full route through stations, hoods, portals and a tunnel, the work pose, worst live clearance,
native command suppression, save cancellation and relaunch, import survival (the code-list line
was restored a third time in `5f3c3de`; check it after the next import).

### L2E handoff, 2026-09-23 — the engine flies the middle

Resume on `9a540dd` (report `docs/agent/reports/drones_chain/L2E_ENGINEFLIGHT_20260923.md`), on the
installed **1.1.1.405907**. Step zero stands (`*r print(7/2, 7*1.0/2, math.type(7/2))` → `3  3.5
integer`). The flight now has two implementations behind one console switch; the default is the
owner's redirect. `SetHubDroneMode("engine")` / `SetHubDroneMode("scripted")`, optionally with a
second argument `"crest"` (default) or `"outside"`; it applies to the **next** `SpawnHubDrone`, so
an A/B is `ReturnHubDrone()`, switch, `SpawnHubDrone()`. `SMROptInHubFlight.Status()` shows `mode`,
`stage` and the drone's live `command`; `SMROptInHubFlight.Lost` names whatever took a drone away.

**Engine mode, what is whose.** Ours: the pit rise to the crest hold, the work pose at the break
(`FixHeight`, `WorkTime`), the pit descent, and with `"outside"` L2R's under-deck exit to the
outside point. The engine's: the leg from the handoff to the break and the leg back, as a stock
`FlightGoto` at the Wasp's own 7 m ride, its own speed, curves and bank — none of `Speed`,
`ClimbRate`, `Accel`, `TurnRadius`, `BankAngle` apply to those legs (they still shape our ends).
The handoff after each engine leg is a stock hold the drone keeps by itself; the driver takes it
back within a quarter second. New dial: `HoldTimeout=60000` (game ms; not a feel value).

**What the owner is asked to judge, in order.** (1) The handoff at the crest: does the engine's
first spline out of the hold clip the ring, hoods or deck? If it does, `SetHubDroneMode("engine",
"outside")` and judge again — that is the fallback the report describes under Stop 2, and the
owner's word decides which handoff ships. (2) The engine's ride height over the track with a train
passing beneath: 7 m above the flight surface is class-static and cannot be tuned; `OI-26` on the
checklist asks the ruling. (3) The return arrival: the engine stops above the hub's stamp and our
descent drops through the column; judge that drop. (4) The work descent and climb at the break,
now vertical from the engine's arrival height. (5) Then the A/B against `"scripted"` in the same
sitting: the owner's words for which ships.

**Saves.** An engine leg or hold now survives an autosave (no blink, no relaunch needed); only our
scripted motion still cancels. After a load the prototype sweeps its own leftovers. Watch for a
greyed drone landing at an arrival: that is vanilla `Idle` winning, which the mock says cannot
happen; `Status().command` and `Lost` are the evidence to record. The drone's infopanel line
during an engine leg is expected to read "Unknown"; cosmetic.

## Lifecycle

Append the settled values into link 4's notes, then **delete this file and strike its row in
`README.md` in the same commit**.
