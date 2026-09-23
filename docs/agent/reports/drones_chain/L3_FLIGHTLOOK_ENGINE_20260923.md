# Drones chain L3 — the attended sitting that settled the flight on engine mode

Attended sitting, 2026-09-23, owner at the keyboard, resuming on `9a540dd` (L2E) and the installed
**1.1.1.405907**. No A/B was flown in the end: the owner flew engine mode, found and fixed what was
wrong with it, and then ruled the scripted flight out of contention by removing its only remaining
justification. Five commits landed. `OI-26` was parked rather than answered.

## What the owner flew, and what they said

| moment | owner, verbatim |
|---|---|
| first engine trip, `HandoffAt="crest"` | *"For the return it brought it above the dome and dropped it right through what will be glass as soon as I do our next mesh import"* |
| the under-deck lane | *"It drives right through this resource pallet coming out and going back."* |
| the speed of our own legs | *"it needs to do it at drone speed not the very slow crawl"* |
| the re-aimed lane at drone speed | *"Ok that was good."* |
| `OI-26` | *"Lets park that until we get everything else built and running thats alot of poking and proding for something that might basically be unnoticible under real conditions and i am leaning towards not worth changing its state"* |
| the 2026-09-19 follow-the-track ruling | *"Not unless we have another reason to go back to our flight path, it would have to be that plus something else. Right now that reason is the only reason for our own flight path."* |
| registering the hub as a remote station's controller | *"Ok that should be fine."* |

## The three faults found, and why none was a rebuild

**1. The crest handoff crosses the dome shell, both directions.** Not tunable, and not an art
setting. `Flight.lua:1043` assigns every spline control point `flight_cache:GetHeight(xy) +
hover_height`, so a vanilla flight cannot clip — every point is *defined* as above the surface, and
the cone padding (`mark_cone_slope`, `Flight.lua:12`) is what makes vanilla drones look like they
navigate carefully around obstacles. The hub is marked correctly: the owner saw the engine park the
drone **above** the dome, which only happens if the stamp includes it. What breaks the guarantee is
that we hand over from **inside** the stamp — the spline starts at crown + 7 m, the drone is ~30 m
below it, and the segment between them is the one thing nothing pins to the surface. Vanilla never
generates it, because a Wasp is never inside a building. `HandoffAt="outside"` removes the segment.

The owner proposed twice that the engine should see the asset and route out through it. It cannot:
the flight cache reduces every object to a single column of `maxz` over a bbox radius
(`Flight.lua:597-618`), so there is no interior and no door, and the solver's only dome logic
filters *landing spots* inside a closed dome (`Flight.lua:887-905`). Adding the glass raises the
column, which makes the crossing worse rather than better.

**2. The under-deck lane was aimed at a pallet.** Measured in game from the hub's own `Box1` spots
(console dump, log `Mars.exe-20260923-16.09.06`): six pallets on r = 2492 at 40.7 + 60n degrees, pit
rim local (-1000,-577), so the gaps centre on 10.7 + 60n. `ExitDirection` was (-866,-500) = 210
degrees — 10.7 degrees off pallet 0 at 220.7. The old comment aimed at a 30-degree *pillar* gap,
which is offset from the pallet ring. The lane passed 0.73 m from pallet 0's centre, and near no
other pallet, matching the single pallet the owner saw hit both ways. Re-aimed to 184 degrees:
1.21 m from pallet 0, 1.25 m from pallet 1. `ExitDirectionX/Y` joined the tuner so the owner can
sweep the bearing without a reload. `7e02763`.

**3. Our legs ran at 6 m/s beside the engine's 16.** `Speed` was 6000 against `FlyingDrone`'s
`move_speed = 16*guim` (`FlyingDrone.lua:42`), which is why our legs read as a crawl next to the
engine's. `Accel = 1200` was the real bottleneck: 13 s to reach 16 m/s, so short legs never
approached the cap. Settled at `Speed=16000`, `Accel=8000`, `ClimbRate=8000`. `bfa664f`.

## A correction to L2E: engine-leg speed is reachable

L2E reported that none of `Speed`, `ClimbRate`, `Accel`, `TurnRadius`, `BankAngle` applies to engine
legs. True of our dials, but too blunt as a statement about the engine. `hover_height` is genuinely
class-static with per-instance overrides ignored by design (`Flight.lua:175`) — that is `OI-26`'s
premise and it stands. `move_speed` is different: it is a `modifiable = true` property
(`DroneBase.lua:16`), and `FlyingObject:OnModifiableValueChanged` pushes a change into that one
object's flight component (`Flight.lua:1015-1019`); the migration path confirms "the current
per-object dynamics (modifiers included) enter the persisted component" (`Flight.lua:1422`). Vanilla
uses exactly this for dust devils (`DroneBase.lua:291`) and rough terrain (`RCRover.lua:92`).

So engine-leg speed **can** be controlled per drone via `ObjectModifier`. Not built, and not
proposed: a modifier is mod-owned state on a vanilla drone, and a drone saved mid-leg would carry
it. Recorded here so a later link does not re-derive it as impossible.

## The import bug, root-caused after five occurrences

`metadata.lua`'s `code` list is **generated from the item tree in `items.lua`**, which held
`ModItemCode` entries for `20_TrainHub` and `10_TrainFloor` only. `30_TrainHubDrones.lua` existed on
disk and had only ever been hand-written into `metadata.lua`, so every editor save rebuilt the list
without it. Five restorations (`d48871e`, `061d6cb`, `5f3c3de`, `2b64304`, `37e3dca`) treated the
symptom. Fixed at source in `6574794`.

doccheck's `MODULE SETS` gate did not catch any of them because it reads `REPO/Code`,
`REPO/items.lua` and `REPO/metadata.lua` — the shipping mod — and never looks at
`tools/devmods/train_hub/` (`doccheck.py:75`, `:2200-2204`). The owner ruled against extending it:
the hub ships soon, the root mod is already guarded, and the extension would be built for a
directory about to stop mattering. **Migration note for whoever does the ship move:** the drones
file needs a `ModItemCode` in the ROOT `items.lua`, not a hand-added line in the root
`metadata.lua`. The root gate will catch it — but only if nobody "fixes" it by editing the output.

## Rulings recorded, and where

- **`OI-26` parked, not closed** (`cc3c7fd`). Its next action is still the owner's, so it stays on
  the checklist; its condition moved from "stage a train in link 3" to "judge under real play in
  link 5", and its Home to `00_TRAIN_ORCHESTRATOR.md`. Engine mode ships as built meanwhile.
  Recorded there as three-way rather than the two the item was opened with: accept 7 m, take the
  flight back (scripted, tag `drones-scripted-flight-20260923`), or give the drone a `FlyingDrone`
  subclass with a higher `hover_height` — which keeps the engine flying but ends the "it is just a
  vanilla Wasp" protection (`Flight.lua:186-200` registers flight params per descendant class).
- **"Follow the track" stops binding on its own** (`ffff0e6`). `DESIGN.md`'s "Beyond it, track work
  only" clause described the old model as current and now states the engine legs. The scope of
  track work and the reachability graph (both owner, 2026-09-19) are unchanged; **their enforcement
  point moved to dispatch**. That is the load-bearing consequence: reachability used to be a
  property of the flight, and engine flight can physically reach an isolated network, so link 4
  must refuse an off-graph target because nothing downstream will.
- **Remote stations get the hub as a controller** (link 4). `station:AddCommandCenter(hub)` for
  every station on the connected graph. `Building:IsOutsideCommandRange` tests list membership, not
  distance (`Building.lua:853-858`), and `GetMaintenanceStuckReason` reads the same list
  (`RequiresMaintenance.lua:297-300`), so this is an honest satisfy rather than a bluff — the same
  call vanilla makes from its hex-circle sweep (`DroneControl.lua:466-468`), with connectivity as
  the criterion instead of proximity. It may remove the need for station-upkeep dispatch entirely.
- **A standing fleet of five at idle** (link 4), superseding the "like 2" low tier. Safe to leave
  vanilla: `TryTakeTask` draws only from the drone's own `command_center` (`Drone.lua:708`), and
  past `distance_to_provoke_go_home_cmd` `Idle` sends a far drone home rather than into other work
  (`Drone.lua:710-712`). The owner ruled out the two residual `Idle` branches from the design: the
  site's cost is reserved at dispatch (`DESIGN.md:110`) so a repair drone flies out empty, and a
  drone servicing a malfunctioned hub is intended (`DESIGN.md:23`, `:45`).

## Not claimed

Scripted mode was never spawned in this sitting, so nothing here rests on a side-by-side
comparison, and the owner never said the words "engine ships" — engine mode stands by the rulings
above. Pallet clearance is computed to **spot centres**, not to loaded stacks; the owner's "not
clipping any when they are full" is unverified and no stack dimensions were obtained. No train
passed beneath a drone, so nothing is known about the 7 m ride in practice. The work pose at the
break was never judged. No `Idle` leak was seen, but no long run was made either.

## Drift and handoff inventory

| finding / departure | evidence | home / next action | disposition |
|---|---|---|---|
| Batch 1 told the owner to press `ReturnHubDrone()` after the work; the trip self-completes and there was nothing to press | brief batch 1 vs `30_TrainHubDrones.lua:748-750` | corrected in the sitting | Agent error, no build impact |
| Recall-then-tune silently refused: `ReturnHubDrone` leaves `active` set, so three `SetHubDroneTune` calls returned false and `SpawnHubDrone` handed back the old drone | owner: *"it didn't take it outside just sitting in the same spot"* | `ClearAll()` first from then on, with returns printed | Cost one trip; no code change |
| `print(ClearAll())` printed nothing — the function has no return | owner report | corrected | Agent error |
| Agent looked for the game log in `Surviving Mars` and told the owner it could not read it; the live build logs to `Surviving Mars Relaunched` | owner: *"agents should always be able to see the log ourput path"* | found and used | Agent error, recorded at the owner's insistence |
| A peer committed the owner's dome-glass import (`37e3dca`) mid-sitting, moving HEAD and rewriting `metadata.lua` under the agent | `git log`, file mtimes | pathspec commits throughout | No collision |
| `DESIGN.md`'s "Save guard for track mode" paragraph is stale — L2E's verdict supersedes it, and link 4 already carries the current instruction | `ffff0e6` commit message | left as-is; it is the owner's settled design and no ruling was asked | **Open**, flagged to the owner, link 6 |

Executed model from the transcript: **Claude Opus 5**. No subagents.
