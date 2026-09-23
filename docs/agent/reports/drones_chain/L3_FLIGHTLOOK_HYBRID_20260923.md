# Drones chain L3 — the motion verdict, and the owner's turn to engine pathing

Attended sitting, 2026-09-23, on motion build `b84f106` (L2M2, EF-116 fix included). The owner
flew it and then redirected the design. This report carries the verdict, the owner's decisions and
every engine fact verified during the sitting, so the commissioned work does not re-derive them.
No constant was tuned; no `Code/` file was edited by this link.

Source facts below were read from the **installed** build 25390750 / **1.1.1.405907**
(`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`). The game patched from 1.1.0.403908
mid-chain, so every earlier chain report's citation is against a tree that is no longer installed;
`python tools/doccheck.py --emit-fingerprint` reports all fact groups MOVED.

## The verdict on scripted flight

Owner, verbatim: *"It is better now, still not nearly as clean as vanilla but its useable."*

That state is preserved as the annotated tag **`drones-scripted-flight-20260923`** (at `eedb69b`;
flight source is `b84f106`'s). Restore the flight file alone with:

```
git checkout drones-scripted-flight-20260923 -- tools/devmods/train_hub/Code/30_TrainHubDrones.lua
```

## The owner's question, and why it was a good one

Owner, verbatim: *"Why do we even need our own movement pathing, why can't we let the engine do
its normal movement process and just basically letting them be normal drones but with our actualy
code changes for their behavior and abilties over riding the non movement parts"*

Answered from source rather than from the existing reports:

- **Near the hub this is already the design.** `DESIGN.md`: inside the 15-hex radius they do
  anything a drone does, through vanilla's own AI.
- **Beyond it, three things blocked it.** The owner's own 2026-09-19 ruling (follow the track,
  *"never drone pathing, so it cannot cut across open ground"*); `hover_height` being **class-static
  with per-instance overrides ignored by design** (`Flight.lua:175`; `FlyingDrone.lua:47` =
  `7*guim`), so no +15 m ride above trains; and the solver owning its own spline to a single
  destination at rest (`avg_spline_dist = 30*guim`), which cannot ride a rail, duck a deck or
  transit a tunnel as designed.
- **Plus the deadline contract**: `DESIGN.md` End state 2 makes the persisted timer the only
  authority, and a solver-owned path has no ETA knowable at dispatch.

## Owner decisions taken in this sitting, 2026-09-23

1. **Build the hybrid.** Our code keeps the launch and the return (the OI-25 pit sequence and the
   stand-ready hold); the engine paths between them; we own the commands. Commissioned as
   `2E_ENGINEFLIGHT_high.md`.
2. **Keep the scripted flight restorable** — the tag above — *"just incase we need to snap back to
   it, if we are unhappy with it and want to stick to handling flight on our own."*
3. **Fleet scaling by load** (new, recorded for link 4): with up to 30 drones allowed, launch only
   what the work needs — *"if drone load is at low maybe we only have like 2 out there and if it
   goes to medium we launch X more drones, high we launch X more drones. And as it dials back down
   we bring X drones back into the bay?"* Appended to `4_HUB_high.md`.

## Verified engine facts, each with what would falsify it

All line numbers are 1.1.1.405907 unless noted. Commands run from that `Src` root.

| fact | source | falsifier |
|---|---|---|
| The train hub **is already a `DroneControl`**, so vanilla fleet machinery applies | `20_TrainHub.lua:95` `__parents = { "Station", "DroneControl", "ElectricityProducer" }` | `grep -n "__parents" tools/devmods/train_hub/Code/20_TrainHub.lua` |
| Flight params incl. `hover_height` are class-static; per-instance overrides ignored by design | `Flight.lua:175`; `FlyingDrone.lua:47` | `grep -n "per-instance overrides are ignored" Lua/Flight.lua` |
| A mid-air `SetCommand` **re-plans from current velocity**, not from a stop | `FlyingDrone.lua:50` `start_dir_obj = true`, consumed at `Flight.lua:512` | `grep -n "start_dir_obj" Lua/Units/FlyingDrone.lua Lua/Flight.lua` |
| Only **disabling** commands defer to landing (`run_cmd_on_land`); a recall is not one | `FlyingDrone.lua:148-154`, `:127-135` | `sed -n '148,154p' Lua/Units/FlyingDrone.lua` |
| `GoHome(min,max,pos,…)` accepts an **arbitrary position**; parks randomly 30–50 m from it; takes tasks en route unless `clear_space` | `Drone.lua:717-748` | `sed -n '717,748p' Lua/Units/Drone.lua` |
| **`Idle` is not "hold"**: lands the flyer, greys it, seeks tasks, and self-issues `GoHome` past `distance_to_provoke_go_home_cmd` | `FlyingDrone.lua:393-396`; `Drone.lua:656-714` | `sed -n '656,714p' Lua/Units/Drone.lua` |
| Commands resume **as threads**, not from the `command` field; nothing at load re-issues from it | `CommandObject.lua:349` (field) vs `:356` (thread); EF-023, EF-027 | `grep -n "PostLoad\|command_thread" CommonLua/Classes/CommandObject.lua` |
| `DespawnNow` routes through `command_center:KillDrone`; `DespawnAtHub` does `DropCarriedResource()` then destroys; `CheatDespawn` adds `SelectObj(false)` | `Drone.lua:3027-3037`, `:2162-2190` | `sed -n '3027,3037p' Lua/Units/Drone.lua` |
| `DroneControl` already provides `drones`, `SpawnDrone`, `KillDrone`, **`GetIdleDronesCount()`** | `Lua/Buildings/DroneControl.lua:99, 725, 729, 992` | `grep -n "GetIdleDronesCount" Lua/Buildings/DroneControl.lua` |

## Two owner proposals that source ruled out

**A command set at save time that persists but does not run live.** Fails twice: EF-070 —
autosave/quicksave run with game time **unpaused** and ≥4 yields sit between `Msg("SaveGameStart")`
and the persist walk, so the command genuinely starts executing in the live session (and two save
paths skip the messages entirely); and commands resume by **thread**, so writing `command` as a
bare field without `SetCommand` yields a drone that loads with a stale label and no thread — inert,
not commanded.

**An armed "kill switch" that fires when we lose control.** The removal half already exists
(`F.Remove` → `DoneObject`; `OnMsg.SaveGameStart` → `F.ClearAll`), and is exactly why the console
drone vanishes on every autosave. What cannot exist is a switch that fires while our code is *not*
running — EF-070's two message-skipping save paths, a save loaded without the mod, a crash. The
protection there is not a switch: it is that the drone is a plain vanilla Wasp with nothing of ours
on it. **That is the standing argument against ever writing a mod-owned command onto one.**

## Consequences recorded for the commissioned work

- **The autosave blink is a prototype gap, not the design.** `DESIGN.md:52-56` and `4_HUB_high.md`
  both already commit to re-arming at `SaveGameDone` *and* on load. The prototype does the removal
  half only, because link 4 owns persisted resume.
- **Engine-driven legs may need no save guard at all.** The hazard the guard exists for is the
  mod's own game-time driver thread (EF-023), not the drone. `DESIGN.md:55-56` already lets busy
  vanilla-driven drones *"stay in the save as vanilla Wasps."* A drone under a stock command has no
  mod thread, so it may persist untouched — no removal, no re-arm, no blink. `2E` must state a
  verdict on this.
- **The handoff is a race, not a wrap.** When a stock command ends, vanilla's next stop is `Idle`,
  which is the whole leak list. Our code must take the drone back before that fires.

## Still owed from link 3, unchanged

Fluidity/bank verdict on whichever implementation ships, the passing-train height check, the full
route through stations/hoods/portals/tunnels, work pose, worst live clearance and location, native
command suppression, save cancellation and relaunch, and import survival.

## Drift and handoff inventory

| finding / departure | evidence | home / next action | disposition |
|---|---|---|---|
| Game patched 1.1.0.403908 → 1.1.1.405907 mid-chain | `doccheck --emit-fingerprint`: all fact groups MOVED | Queued sweep `prompts/perma/gamepatch/1.1.1.405907_2026-09-23.md` | Facts in this report re-read on the installed tree |
| `max_sleep` moved 333 → 600 between builds | `FlyingDrone.lua:36` | L2M2 cited 333; L6 | Citation drift, no behavioural conclusion changed |
| Code-list line dropped by an import a third time during this sitting, self-restored before commit | `metadata.lua` working-tree diff | Link 3's standing import check | Observed and cleared; no edit landed from this link |
| Design redirected mid-sitting to engine pathing | Owner's words above | `2E_ENGINEFLIGHT_high.md` | Commissioned |
| Fleet load-scaling raised | Owner's words above | `4_HUB_high.md` notes | Recorded for link 4 |

Executed model from the transcript: **Claude Opus 5 (1M context)**; earlier legs of the same
sitting ran on Claude Sonnet 5. No subagents.
