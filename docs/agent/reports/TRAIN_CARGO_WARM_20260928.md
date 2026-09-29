# Train Cargo Upgrade: warm network — 2026-09-28

Brief: `prompts/Train_Hub_Project/19_TRAIN_CARGO_WARM_NETWORK_medium.md`. Authority: owner,
2026-09-28, train design §4.10 (grep `also warms the network`). **Built and desk-checked in
`22f83ec`. The owner's Mod Editor save for the description and the attended check are owed.**
No game launch is claimed. A desk PASS means only that the mocked vanilla agrees.

## Change

- **Speed chain** (`Code/20_TrainHub.lua`, the Train Cargo Upgrade's `GetNominalMoveSpeed`
  wrapper). While the upgrade's modifier is applied, vanilla is called with the global
  `GetHeatAt` returning `const.MaxHeat` for that one call. The real function is restored
  afterwards, under `pcall`, so an error restores it too. The ×125/100 applies after that, as
  before.
  - Vanilla's cold branch (1.1.1.405907 `Units/Train.lua:602-605`) is its only heat read.
  - `turn_anim_speed` is derived from the same `move_speed` (`:612`).
  - So a cold train reads **exactly** the warm speed, with vanilla's own tech, law and rounding.
  - Undoing ×1/3 after the fact would miss by rounding (1000/3 → 333 → 999).
  - Off, salvaged, ruins or a foreign city: vanilla is called unchanged and cold applies.
  - No body copy, no new `Require` pair, no new persisted name. Every argument and return is
    passed through.
- **Stop check (brief): not triggered.** The only other `SafeTransport` reads are repair cost
  (`Buildings/Track.lua:653`) and breakage odds (`TrainDisasterHandling.lua:9`). Neither is a
  cold effect on movement. `grep -n -i "heat|freez|frozen|cold"` over `Units/Train.lua`,
  `Buildings/Station.lua` and `Buildings/Track*.lua` finds no other heat read.
- **Description** (authored `Data/BuildingTemplate/SMROptInTrainHub6.lua`, `upgrade2_description`)
  now reads: "…+25% speed to every <em>Train</em>, and warms the network: trains take no cold
  penalty. …". The generated companion was not hand-edited.

## Desk evidence

`python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py` at `22f83ec` passes. Its fixture
has Faster Trains, Vacuum Rail and the +33% law all on, which gives a warm vanilla speed of 1995.

| state | nominal speed |
|---|---|
| upgrade on, warm | 2494 |
| upgrade on, cold | 2494 |
| upgrade on, cold with Safe Transport | 2494 |
| upgrade on, cold, no tech | 875 |
| upgrade off, cold with Safe Transport | 1330 |
| upgrade off, cold | 665 |
| upgrade off, warm | 1995 |

- When cold, both returns equal the warm ones. The extra returns, and the element argument
  passed to the prior wrapper, survive.
- `GetHeatAt` is the real function again after each call, including after a forced error.
- The two new mutations are rejected: `warm network` (drop the warm call) and `heat restore`
  (skip the restore). So are the six from brief 16.

`--require-generated` now also requires the generated `upgrade2_description` to match the authored
one. **It fails until the owner's Mod Editor save**, by design. The normal run prints
`OWNER STEP OWED`.

Every `tools/devmods/train_hub/tests/*_smoke.py`, each run with `python <file>` and scored on exit
code, at `22f83ec` with a clean tree: **21 members = 21 passing + 0 failing.**

## Owner Mod Editor step

Open the Train Hub dev mod in the Mod Editor. Confirm slot 2's description carries the
warm-network sentence, **save the mod**, and restart the game. The agent's check afterwards is
`python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated`.

## Attended check (about three steps) — [NEVER RUN for this build]

Run the combined sitting in `TRAIN_CARGO_HEATER_20260928.md` instead of a separate
warm-network sitting; it preserves the train check below and adds hub ground heat.

Load a copy of a save that has the Train Cargo Upgrade on and a train standing on open ground,
away from heaters and domes. Both mods and the TestKit are loaded.

1. **Force the cold.** Pause. Open the console and enter `CheatColdWave("ColdWave_High")`
   (vanilla `ColdWave.lua:319-333`). No slot covers this, so the console line is the route
   (owner, 2026-09-27). Unpause for about half a sol, then pause again.
2. **Read on, then off.** Press slot **3 (read upgrades, train capacities and nominal speed)**:
   the standing train's speed equals its warm reading, ×1.25 included. Toggle the Train Cargo
   Upgrade off on its owner hub. Press slot 3 again: speed drops to vanilla's cold value, ⅓ of
   the warm pre-upgrade speed, or ⅔ with Safe Transport. That drop is what proves the spot is
   cold. If there is no drop, the spot is still warm: wait longer or pick another train.
3. **Restore and close.** Toggle the upgrade back on and press slot 3: the warm reading returns.
   Enter `CheatStopDisaster()` and review new Lua errors with the agent.

## Handoff

- **Owner actions:** the Mod Editor save and the check above. Because the sitting runs both
  mods, the check belongs on the fix pack's owner list, as brief 16's did (ck219). That routing
  is left to the orchestrator.
- **Out of scope, unchanged:** hub movement, the heat grid, drones and rovers, and
  `traffic_smoke.py`.
- **Executed model:** Claude Fable 5.1 (`claude-fable-5-1`). No subagents.
