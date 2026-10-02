# Train_Hub_Project/ — the train hub's briefs, in fire order

The numbers are the order. **Fire the lowest number that is not held.** `Parked/` is never fired
unless the owner reopens it. **Once a brief has fired and its work is done, the orchestrator
decides** (owner, 2026-09-21): park it in `Parked/` if it is kept for possible touch-up work, or
delete it. Its row here moves or goes in the same commit.
Start any of them with `task docs/agent/prompts/Train_Hub_Project/<file>`.

`00` is live; `03_Drones/` is closed reference. **`30` and `31` (the audit, report `reports/TRAIN_AUDIT_20261002.md`) closed 2026-10-02 and were
deleted, as was `32` (the icon, closed 2026-10-02). `33` and `34` may fire now; `35` after 33-34.**
`33`-`35` are the project's last briefs (authored 2026-10-02). Briefs 22 (hub storage),
26 (the depot's design), 27 (its wiring), 28 (its paint pass) and 29 passed live 2026-10-01 and were
deleted, 25 parked; spec §4.10 and §11, the reports and OI-38 hold the record and what is open. Briefs 10, 17 and 21 passed live and were deleted
2026-09-29. Only one brief
that edits `20_TrainHub.lua` runs at a time.

The earlier `05`, the portal doors, was fired, built and then cut by the owner on 2026-09-22; its
survey stays in `reports/VANILLA_DOOR_ENTITIES_20260922.md`, its code in git at `8aef5de`.

| brief | what it is for | state |
|---|---|---|
| `00_TRAIN_ORCHESTRATOR.md` | The project lead. It reads build reports, keeps the spec current, briefs the next build, and never builds. | Standing; re-run as needed |
| `03_Drones/` | Build 4 reference: the hub's vanilla Wasps rise from the pit and use train doors; the owner rulings are in spec §10 "Drones L5". Only `DESIGN.md` and `README.md` remain. | **Closed, PASS WITH CORRECTIONS:** `reports/drones_chain/L6_QA_20260925.md`. C1–C6 / D14(g,h) are routed; smoke evidence is bounded, ship tests remain owed |
| `33_TESTKIT_CROSSING_WITNESS_high.md` | Fix the shared TestKit's crossing witness (misses train unloads at ultra speed) so the battery can rest a crossing verdict on it. | **Ready** |
| `34_MOVE_INTO_MOD_high.md` | Remove the dev tags: station rows, the hub and the Elevator Depot move into this mod as opt-in modules, with OI-18's widened preflight; the owner's checkpoint on the module list and save names first. | **Ready** (its owner checkpoint first) |
| `35_FINAL_BATTERY_high.md` | The final full battery on the shipping layout, both configurations and toggle directions; its pass completes the project and purges this folder. | Held until `33`-`34` close |

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
