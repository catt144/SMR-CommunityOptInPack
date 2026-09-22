# Train hub: portal doors from vanilla door entities

**LIVE, one-off.** The owner fires it; the orchestrator parks or deletes it once done. Authoring
state: OptInPack `HEAD` of this commit, assets `3d5c11e`, tag `hub-uv-refrozen-20260922` in both
repos. `git log`, `git pull` in both first. Runs in parallel with `01`'s portal rebuild in
SMR-Assets; this brief edits `20_TrainHub.lua`, so it holds while `02` or `03` has that file open
(`git log -- tools/devmods/train_hub/`).

## Authority

- **Owner, 2026-09-22: reuse a vanilla door that already animates, scaled to fit the portal
  mouth, opening as a train approaches and closing behind it.** No animation is authored; a
  vanilla entity is attached and driven. *"if there are any doors we could reuse from the game
  that would function and resize it to fit, that would be amazing."*
- The survey is `docs/agent/reports/VANILLA_DOOR_ENTITIES_20260922.md` (desk, nothing seen in
  game): every candidate, its states, size, travel and the console line to place it. Read it
  whole before anything else. Its facts are cited claims; each one you rest a build on gets one
  check in game, not a re-derivation.
- **Attaching anything to the shipping hub is a behaviour change**: the ruling above is the
  owner's, recorded here and in spec §9; record the door chosen and its knobs in spec §9 too.
- The portals are being rebuilt in SMR-Assets under `01` §"Pass 3" (generated portal, two mouth
  candidates, a door plane ~0.4 m behind the lip named `PortalFrame_*`). **The door plane's size
  follows the door the owner picks**, not the other way round: once the owner has chosen, report
  the door's world width × height at its chosen scale and the plane it needs, so the orchestrator
  sets the portal's opening to it.

## End state

1. **The owner's five-minute look, first.** The survey's §6 lines A-E place `ElevatorSurfaceDoor`
   (native and at 33%), `TunnelEntranceDoor`, `MarsAssembly_Door_01` and `TrainTunnelUniversalDoor`
   in a row in front of the selected object, opened. Give the owner the paste-safe lines (one per
   candidate, the close, the cleanup), collect what they saw and their pick, and record the five
   reads the survey owes (one slab or two, the assembly door single or a pair, `IsAnimLooping`,
   clipping when scaled, which door the owner photographed). If none fits by eye, stop 1.
2. **Candidates in the mod.** A `hub_door_*` block in `20_TrainHub.lua` in the pattern of the arm
   lights (`hub_light_*`): a table of door styles (entity, scale, offset from the portal's door
   plane, which way it retracts), a `hub_door_style` knob, one door per portal attached at Origin
   with a computed offset on the portal's axis (the six portal directions are the same six the
   lights use; the door plane's radial distance is a constant you read from the portal design —
   until `01`'s portal lands, use the current opening at 30.1 m and say so). `DeleteOnLoadGame`,
   recreated from `GameInit`, `heal_after_load` and `OnSetWorking`; **a stopped hub destroys its
   doors** like its lights; no persisted class or saved field; detail class Essential. Build at
   least two styles the owner can switch by knob without an import.
3. **Driven by trains.** Open when a train approaches a portal, close behind it; your call how the
   approach is read (the hub's own routing already knows which portal a train is heading for —
   `HubTransitionPauseDistance`, `Floor.HubParkDistance` and the movement code in the same file
   are the leads), and how long "behind it" is. Ref-counted `Open`/`Close` (survey §4.7): one door
   per portal, opened and closed by the same train, never left open by an interrupted move
   (a train destroyed mid-transit, a save/load mid-open — the door is recreated closed).
4. **Smoke.** Extend `tests/look_smoke.py` with the door count and lifecycle (six on, zero off,
   idempotent, foreign attachments untouched) and a mocked open/close by a passing train.
5. **The owner looks in game:** a train through each portal, day and night, and says keep or
   change. Then record in spec §9 with `doc-editing`, commit with a pathspec.

## Leads, not the route

- The survey's recommendation: `ElevatorSurfaceDoor` (height 12.93 m native, 19.46 m wide, drops
  11 m straight down in 600 ms; the portal mouth widens or the slab's outer thirds bury in the
  collar) or `TunnelEntranceDoor` at 33% (6.6 × 2.2 m, the rover tunnel's own door, the only one
  with its own sounds). Retraction scales with `SetScale`: the ground under a portal must take
  the drop, or the door must retract upward — check whether any candidate can be placed upside
  down (a 180° attach angle about the portal axis) so it rises into the collar instead.
- Doors are silent unless `DoorWithFX`; a subclass of ours that adds a sound is a later touch.
- `CreateGameTimeThread` defers (EF-029); read a door's state only from inside the thread.

## Scope

In: the door block in `20_TrainHub.lua`, its smoke, the console lines for the owner, the door
plane report for the portal. Out: the portal geometry and maps (SMR-Assets, `01`), the lights,
routing and movement code beyond reading where a train is, any vanilla file.

## Stops (report instead of pushing on)

1. No candidate fits by the owner's eye after the five-minute look.
2. An attached, scaled door does not play its `opening` state, or plays it wrong (survey §4.4 is
   inferred, not measured).
3. A train's approach cannot be read without editing the movement code that `Parked/
   TRAIN_HUB_MOVE_high.md` holds as finished.

## Do not claim

Do not claim a door "works" from the mock. Claim the entity, scale and offset built, the mocked
lifecycle, and what the owner saw through which portal.

## Deliver

Todo list first, one item per commit-and-verify unit; design smoke only; about five steps at a
time; the B-run rule of `01` §Deliver 4 applies if the owner calls it.
