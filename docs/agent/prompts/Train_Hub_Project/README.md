# Train_Hub_Project/ — the train hub's briefs, in fire order

The numbers are the order. **Fire the lowest number that is not held.** `Parked/` is never fired
unless the owner reopens it. **Once a brief has fired and its work is done, the orchestrator
decides** (owner, 2026-09-21): park it in `Parked/` if it is kept for possible touch-up work, or
delete it. Its row here moves or goes in the same commit.
Start any of them with `task docs/agent/prompts/Train_Hub_Project/<file>`.

`00` is live; `03_Drones/` is closed reference. **No build brief is live.** Briefs 22 (hub storage)
and 26 (the depot's design pass) passed live 2026-10-01: 22 was deleted, 25 and 26 parked for the
paint pass; spec §4.10 and §11 hold the record. Briefs 10, 17 and 21 passed live and were deleted
2026-09-29. The wiring brief is next. Only one brief
that edits `20_TrainHub.lua` runs at a time.

The earlier `05`, the portal doors, was fired, built and then cut by the owner on 2026-09-22; its
survey stays in `reports/VANILLA_DOOR_ENTITIES_20260922.md`, its code in git at `8aef5de`.

| brief | what it is for | state |
|---|---|---|
| `00_TRAIN_ORCHESTRATOR.md` | The project lead. It reads build reports, keeps the spec current, briefs the next build, and never builds. | Standing; re-run as needed |
| `03_Drones/` | Build 4 reference: the hub's vanilla Wasps rise from the pit and use train doors; the owner rulings are in spec §10 "Drones L5". Only `DESIGN.md` and `README.md` remain. | **Closed, PASS WITH CORRECTIONS:** `reports/drones_chain/L6_QA_20260925.md`. C1–C6 / D14(g,h) are routed; smoke evidence is bounded, ship tests remain owed |

## `Parked/` — do not fire

| brief | why it is kept |
|---|---|
| `01_TRAIN_HUB_STRUCTURE_high.md` | The structure pass, A to C runs (2026-09-21/23): maps, seams, lights, glass, reactor palette — all kept. Its cost reading moved to `05`. Kept for its pipeline facts and measurements; spec §9 holds the record. |
| `TRAIN_HUB_MODEL_high.md` | The hub's **3D shape** (geometry and UVs). It is final at radius 6. Kept to reopen if the look ever needs the model to move. |
| `TRAIN_HUB_LOOK_high.md` | The **umbrella record of the whole look pass**: why the hub read as flat paint, the owner's order, the deferred stages (fine normal, glass, themed reactor). Its stages fire as their own briefs; `01` is the current one. It retires when the owner accepts the look. |
| `TRAIN_HUB_MOVE_high.md` | Train movement through the hub. It is finished and owner-accepted (2026-09-21). It may reopen only at the final pre-launch test, if the owner wants a move tweaked. |
| `RAIL_SHAFT_PROTOTYPE_high.md` | The rail shaft (trains crossing maps through a tunnel), parked 2026-09-29 when the owner ruled the Elevator Station instead (spec §11). Kept for its measured cross-map hop, its open stall attribution and its unfiled engine facts. The dev mod `SMR_RailShaftDev` was unjunctioned from the game 2026-09-30; its folder stays in `tools/devmods/rail_shaft/`. |
| `23_OI27_DRONE_MAP_GUARD_high.md` | OI-27's drone map guard (spec §10 ruling). Parked unfired 2026-09-29: only a cross-map tunnel can trigger it, and the Elevator Station makes none. Fire it if a rail shaft is ever linked again, or before loading the old shaft save with the hub. |
| `25_ELEVATOR_STATION_LOOK_high.md` | The Elevator Depot's first look pass: the portal between the pads, its import pipeline, the dev mod's console and the vanilla `Station` spot rules ("What exists", "Evidence"). Parked 2026-10-01 when brief 26's pass was accepted; the paint and final-checks pass starts from it. |
| `26_ELEVATOR_DEPOT_DESIGN_PASS_high.md` | The depot's second design pass, accepted by the owner 2026-10-01 *"until we get through testing and we do paint and final checks"* ([report](../../reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md#the-owners-acceptance-2026-10-01)). Kept for that paint pass: its open items are `Measure()`'s underground reading, the `receiver_z` tune and the core's vanilla frame. |
