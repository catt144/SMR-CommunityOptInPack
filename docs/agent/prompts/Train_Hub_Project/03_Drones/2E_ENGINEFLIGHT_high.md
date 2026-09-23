# Drones chain, link 2E — the engine flies it; we own the ends and the commands

**Link 2E of the `03_Drones` chain** (`README.md`). Unattended. `DESIGN.md` is the settled design;
read it and this brief's facts before opening code. `git log`, `git pull` both repos first.

## Authority

**Owner, 2026-09-23, having flown the scripted flight** (`b84f106`): *"It is better now, still not
nearly as clean as vanilla but its useable."* Then the redirect, verbatim: *"build the function
that basically besides our launch and return parts the engine handles that pathing and we handle
the commands."*

So: **our code keeps the pit launch, the stand-ready hold and the pit return. Between them the
engine paths the drone. We own the commands.** The route topology (L2R, under the deck) and OI-25's
column are settled and not reopened. Nothing in this mod is frozen (`CLAUDE.md`, owner 2026-09-18).

**The scripted implementation is preserved** at tag `drones-scripted-flight-20260923` and stays
restorable — the owner's words: *"just incase we need to snap back to it, if we are unhappy with it
and want to stick to handling flight on our own."* You do not need to keep it working in the file,
but you must not make it unrecoverable.

Full context, every fact below with its falsifier, and the two proposals source already ruled out:
`docs/agent/reports/drones_chain/L3_FLIGHTLOOK_HYBRID_20260923.md`. Read it; it exists so you do
not re-derive this.

## End state

1. **The ends are ours, the middle is the engine's.** Pit launch through OI-25's column to the
   stand-ready hold, and the return descent, stay scripted. Every leg between them is flown by the
   engine under a **stock** command.
2. **No mod-owned command name is ever written onto a vanilla drone.** This is the standing
   protection: a save made with the mod and loaded without it must leave nothing but an ordinary
   Wasp. If you cannot meet the end state without one, that is Stop 1.
3. **The handoff is won in both directions.** When a stock command ends, vanilla's next stop is
   `Idle` — which lands the drone, greys it, seeks tasks and can self-issue `GoHome`. Our code takes
   the drone back before that fires. Say in the report how you won that race and what proves it.
4. **The owner can switch implementations at the console without a reload**, so link 3 can A/B the
   two in one sitting. Mechanism is your call; without this the owner cannot judge the change.
5. **A save verdict.** State whether engine-driven legs need the save guard at all. The hazard the
   guard exists for is our own game-time driver thread (EF-023), not the drone, and `DESIGN.md:55-56`
   already lets vanilla-driven busy drones stay in the save as ordinary Wasps. If they do not need
   it, say so and say what still does.
6. **The smoke covers the new surface** and still refuses a bare `/` (EF-116's gate). Gates:
   `python tools/devmods/train_hub/tests/flight_smoke.py`, `python tools/parsecheck.py`,
   `python tools/doccheck.py`.

## Live work list

One todo item per commit-and-verify unit, one in progress, marked as each lands. A list written
after the writes does not count.

## Start and staleness

Authoring sha `eedb69b`. An empty
`git diff --stat eedb69b..HEAD -- tools/devmods/train_hub/Code tools/devmods/train_hub/tests`
means this brief's facts hold. The game patched to **1.1.1.405907 / build 25390750** mid-chain;
read source from `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`, not the 1.1.0 tree that
earlier chain reports cite.

## Facts you would otherwise re-derive

Verified on the installed tree, 2026-09-23. The report above carries a falsifier command for each.

- The hub **is already a `DroneControl`** (`20_TrainHub.lua:95`), so vanilla fleet and command
  machinery applies to it directly.
- A mid-air `SetCommand` **re-plans from current velocity** (`FlyingDrone.lua:50`
  `start_dir_obj = true`, consumed at `Flight.lua:512`) — a recall curves away, it does not stop dead.
- Only **disabling** commands defer to landing via `run_cmd_on_land` (`FlyingDrone.lua:148-154`).
  A recall is not one, so it interrupts cleanly mid-air.
- `GoHome(min, max, pos, ui_str_override, clear_space)` (`Drone.lua:717-748`) takes an **arbitrary
  position**, parks at a random spot 30–50 m from it, and grabs tasks en route unless `clear_space`.
- **`Idle` is not a hold** (`FlyingDrone.lua:393-396`; `Drone.lua:656-714`). The hold is the
  *absence* of a command — which is what `init_with_command = false` already gives.
- `hover_height` is **class-static, per-instance overrides ignored by design** (`Flight.lua:175`;
  `FlyingDrone.lua:47` = `7*guim`). Engine-flown legs ride at 7 m. There is no per-drone override.
- Teardown: `DespawnNow` routes through `command_center:KillDrone` (`Drone.lua:3027`);
  `DespawnAtHub` does `DropCarriedResource()` then destroys (`:2162`). Prefer these over a bare
  `DoneObject`, which skips the controller's bookkeeping.

## Scope

**In:** `tools/devmods/train_hub/Code/30_TrainHubDrones.lua`, its smoke and receipts, the
implementation switch, the report.

**Out:** `20_TrainHub.lua` and everything in it (link 4's, and only one brief edits that file at a
time); dispatch, economy, the pending list, persisted state; fleet load-scaling (recorded for link
4); art and assets; the owner's visual verdict (link 3's).

## Stops

1. **The end state needs a mod-owned command on a vanilla drone.** Report the exact reason and
   stop. Do not write one and do not merge flight code into `20_TrainHub.lua`.
2. **Engine pathing cannot be kept clear of the hub structure** on its own routes — it clips, or it
   refuses the under-deck geometry. Report what it did, with the leg.
3. **The 7 m class-static hover breaks the owner's "above the trains" requirement** on every
   engine-driven leg. That is an owner ruling, not something to engineer around: report it.

## Do not claim

Do not claim the result *feels* like vanilla, is fluid, or is natural — that is the owner's eye in
link 3, and this link drives no game. Do not claim save safety from the smoke: it executes the Lua
under mocks, and cannot render or serialize. Write the narrower true claim: which legs are engine-
flown, what the handoff does, and what remains untested in game.

## Lifecycle

One-off. Append what link 3 needs into its `## Notes from upstream` — the switch, the new dials,
what the owner is being asked to judge — then **delete this file and remove its row in `README.md`
in the same commit**.
