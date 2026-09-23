# Drones chain L2E — the engine flies the middle; we own the ends and the commands

Unattended build, 2026-09-23, commissioned by the owner's redirect after flying `b84f106`:
*"build the function that basically besides our launch and return parts the engine handles that
pathing and we handle the commands."* Landed as `9a540dd` on `16a69e3`. **No game was driven by
this link.** Every claim below is the code, the mocked smoke and the archived source of the
installed build **25390750 / 1.1.1.405907** (`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`).
The scripted flight is untouched behind the switch and at tag `drones-scripted-flight-20260923`.

## What ships (`tools/devmods/train_hub/Code/30_TrainHubDrones.lua`, `Mode = "engine"` by default)

| leg | who flies it | how |
|---|---|---|
| pit floor → rim → crest (OI-25's column) | ours | the L2M2 chords, unchanged |
| the stand-ready hold at the crest | the drone itself | stock `WaitUninterruptable(HoldTimeout)`, re-armed by our driver at half its timeout |
| crest → break (`HandoffAt="crest"`) | the engine | `SetCommand("FlightGoto", point(x, y))`, the 2D shape `FlyingDrone:Goto` hands the same call; class-static `hover_height` 7 m |
| crest → under-deck lane → outside point (`HandoffAt="outside"`) | ours | L2R's exit chords, then the engine from the outside point |
| arrival → work pose (`FixHeight` above the break) → work → back to the arrival height | ours | vertical chords; the arrival height is the engine's own, so the return leg starts from a height the solver chose |
| break → crest column (or outside point) | the engine | the same stock command |
| the engine's return arrival → crest → rim → floor, `LandingEnd`, removed | ours | chords from wherever the engine stopped; `outside` re-enters the lane and keeps OI-25's crest reversal |

Only three values are ever written into the drone's `command`: `"FlightGoto"`,
`"WaitUninterruptable"` and `false`. Both names are shipped engine methods
(`Lua/Flight.lua:1182`; `CommonLua/Classes/CommandObject.lua:168`). No class is wrapped, no
per-instance function is placed, no mod field persists. The smoke's static gate refuses any other
first argument to `SetCommand`/`QueueCommand` and any class assignment.

## How the handoff race is won, and what proves it

**The race.** `CommandThreadProc` (`CommandObject.lua:212-292`) runs a finished command's queue and
then `Idle` in the same thread with no yield between; `Drone:Idle` (`Drone.lua:656-714`) greys the
drone, sets `idle`, seeks tasks and self-issues `GoHome` past `distance_to_provoke_go_home_cmd`.
Any watcher that polls after the command ends has already lost.

**The win.** Every leg is issued as `SetCommand("FlightGoto", xy)` immediately followed by
`QueueCommand("WaitUninterruptable", HoldTimeout)` (`CommandObject.lua:359` appends because the
current command is not `Idle`). When the flight ends, the queue runs before `Idle` is even chosen
(`:262-278`), and `WaitUninterruptable` is `ExecuteUninterruptable(WaitMsg, self, timeout)`
(`:168`): the drone holds itself at the arrival hover. Our driver polls every `PollTime` (250 game
ms), sees `command == "WaitUninterruptable"`, and takes the drone back with `InterruptWait()`
(`Msg(self)`, `:172`) then `SetCommand(false)`. The order matters: `DoSetCommand` (`:309-347`)
defers a new command behind an uninterruptable wait until the wait ends, so the interrupt comes
first. `Idle` is reachable only by the hold's timeout, which needs the driver to be absent for a
full `HoldTimeout` (60 s game). That timeout is deliberate: it is exactly what a save loaded
without the mod does with the drone, which then becomes an ordinary Wasp.

**The proof, mocked.** The smoke models `SetCommand`, `QueueCommand`, `InterruptWait`, the
queue-then-Idle order and the deferral, and counts `Idle` as a leak. Over the full engine trip:
2 legs, 2 queued holds, every hold taken back within one poll, `Idle` never entered; the crest
hold outlives three timeouts without idling; a driver stalled past the timeout does lose the drone
to `Idle` and the next look removes it, `SMROptInHubFlight.Lost == "Idle"`. The 1.1.1 tree is read
in the same run for the two method definitions and the loop order, and the archived `FlightGoto`
body is executed with a solver spy. **Untested in game:** whether the real `WaitMsg` wakes and the
real thread ordering behave as modelled; a real `Idle` would show as a greyed drone landing at
the arrival, and `Lost` names it.

## Save verdict (End state 5)

Engine-driven legs **do not need the save guard**. The hazard the guard exists for is our own
game-time driver (EF-023), and a drone under `FlightGoto` or the stock hold has none: its command
thread is the engine's and persists with the object (`Flight.lua:1176-1181`: a resumed thread
continues its flight, a restarted one re-requests the path from the current position). So at
`SaveGameStart` the driver is deleted and those drones stay; at `SaveGameDone` the driver restarts
with its records intact in memory. If a leg ends during the save's own yields (EF-070), the queued
hold keeps the drone until the driver is back.

**What still needs it:** scripted motion — the rise, the exit, the work pose, the descent. Those
drones have no thread at all in the save and would load frozen in the air, so they are removed at
`SaveGameStart` as before. The blink is now confined to a few seconds of scripted motion per trip.
**Load:** records are memory, so `LoadGame` sweeps prototype leftovers (a `FlyingDrone` whose
controller is a train hub and that `hub.drones` does not hold), leaving fleet Wasps and other
controllers alone. L4 replaces the sweep with adoption from the persisted deadline.

## The switch (End state 4)

`SetHubDroneMode("engine"|"scripted", "crest"|"outside")` at the console, no reload. It applies to
the next `SpawnHubDrone`, so an A/B is Return, switch, Spawn. `SetHubDroneTune` gains
`HoldTimeout`; `PollTime` is not a dial. `SMROptInHubFlight.Status()` reports `mode`, `stage`,
`handoff` and the drone's current `command`.

## The three stops, assessed

1. **A mod-owned command name** was not needed. Not hit.
2. **Engine pathing clear of the hub** cannot be decided here. The solver flies over the flight
   cache surface (`Flight.lua:99`), which stamps marked buildings (`:597-790`, `mark_flags` =
   visible + grids + collision) and adds a clearance cone. A leg started at the crest, inside the
   hub's stamp, begins below that surface; where the first spline segment goes is the C++
   component's. The smoke models the pessimistic case (the hub stamped 30 m high): the return leg
   arrives 37 m up over the crest and our descent chords go straight down the column through
   whatever is above it. `HandoffAt="outside"` exists so link 3 can move the handoff outside the
   footprint without a rebuild. Link 3 reports what it did, with the leg.
3. **The 7 m class-static hover** is the ride height of every engine leg, above the flight surface
   at each point: over a marked track it is 7 m above the track's stamp, over open ground 7 m above
   terrain. Whether that clears a side-hanging train is an owner ruling; `OI-26` asks it.

## Not claimed

Not fluidity, not "like vanilla", not save safety from the smoke, not clearance. The receipt
(`tests/motion_clearance_receipt.json`) was re-measured for the new source hash and bounds the
scripted chords only: 78 legs, all margins identical to `b84f106`'s, worst 0.240 m at PitFloor_1.
Engine legs are unbounded by it. The drone's infopanel during an engine leg shows whatever
`Getui_command` (`Drone.lua:3168`) makes of `"FlightGoto"` and `"WaitUninterruptable"`, most
likely "Unknown"; cosmetic, noted for link 4's panel work.

## Drift and handoff inventory

| finding / departure | evidence | home / next action | disposition |
|---|---|---|---|
| `20_TrainHub.lua` and `look_smoke.py` were modified in the working tree by a peer during this link | `git status` at commit time | committed by pathspec; neither touched | No drift in the flight files |
| HEAD moved `bccd16b` → `16a69e3` (Spec 9) mid-link | `git log` | staleness diff on `Code`/`tests` still empty | Brief's facts held |
| A recall at the spawn instant errored (empty plan indexed) in both modes | `run_plan` before `9a540dd` | fixed and tested in `9a540dd` | Pre-existing edge, corrected |
| `DespawnNow` not adopted despite the brief's preference | `DroneControl.lua:729-733` asserts `hub.drones` membership; the prototype never enters it | `DoneObject` kept; L4's fleet uses `KillDrone` | Recorded for L4 |
| The 1.1.0 archive path in the smoke's solver spy replaced by 1.1.1 | `flight_smoke.py` | done | Citation drift closed |
| Blender wrote the receipt CRLF | `doccheck` EOL warn | normalised to LF before commit | Resolved |

Executed model from the transcript: **Claude Fable 5.1**. No subagents.
