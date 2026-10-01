# Train_Hub_Project/ — the train hub's briefs, in fire order

The numbers are the order. **Fire the lowest number that is not held.** `Parked/` is never fired
unless the owner reopens it. **Once a brief has fired and its work is done, the orchestrator
decides** (owner, 2026-09-21): park it in `Parked/` if it is kept for possible touch-up work, or
delete it. Its row here moves or goes in the same commit.
Start any of them with `task docs/agent/prompts/Train_Hub_Project/<file>`.

`00` is live; `03_Drones/` is closed reference. **`28`, the depot's paint pass, is the live brief.** Brief 27 (the depot's wiring) passed live
2026-10-01 and was deleted; its report and OI-38 hold what is open. Briefs 22 (hub storage) and 26 (the depot's design pass)
passed live 2026-10-01: 22 and 26 were deleted (26's open items are in `28`), 25 parked; spec §4.10 and §11 hold the record. Briefs 10, 17 and 21 passed live and were deleted
2026-09-29. Only one brief
that edits `20_TrainHub.lua` runs at a time.

The earlier `05`, the portal doors, was fired, built and then cut by the owner on 2026-09-22; its
survey stays in `reports/VANILLA_DOOR_ENTITIES_20260922.md`, its code in git at `8aef5de`.

| brief | what it is for | state |
|---|---|---|
| `00_TRAIN_ORCHESTRATOR.md` | The project lead. It reads build reports, keeps the spec current, briefs the next build, and never builds. | Standing; re-run as needed |
| `03_Drones/` | Build 4 reference: the hub's vanilla Wasps rise from the pit and use train doors; the owner rulings are in spec §10 "Drones L5". Only `DESIGN.md` and `README.md` remain. | **Closed, PASS WITH CORRECTIONS:** `reports/drones_chain/L6_QA_20260925.md`. C1–C6 / D14(g,h) are routed; smoke evidence is bounded, ship tests remain owed |
| `28_ELEVATOR_DEPOT_PAINT_high.md` | The Elevator Depot's paint pass to production: finished maps on the depot's own pieces in the train hub's theme, blended with vanilla's 75 % Space Elevator; carries brief 26's open items (receiver height, underground `Measure()`, the core's frame). Its Mod Editor import waits while `27` is live. | **Live, renders passed (owner, 2026-10-01: "pass"), the Mod Editor import next, then the sitting** (run A 2026-10-01: maps built, Assets `c660d60`..`ad93c4f`, dev mod `cffb57a`; the owner: another pass, the depot reads plain beside their blue-banded elevator. Run B 2026-10-01: route A, a colourisation mask marked as vanilla's elevator is, so the colony scheme paints the depot as it paints the elevator; Assets `635022e`..`8b53ab3`, the material source gains `Colorization` and `Colors = 3`; renders in Space_Y and the default scheme; report `reports/ELEVATOR_DEPOT_PAINT_20261001.md` "Run B". With `27` closed, 28 set the template's three palette names in the Data source and the Lua hand that paints the attached elevator, cabin, ropes and receiver with the colony palette (the generated template regenerates at the editor save; `wiring_smoke` PASS against the pre-29 hub file, its §10b is `29`'s). The owner's word on the renders: "pass"; OI-39 closed) |
| `29_HUB_TITLE_AND_DEPOT_COST_medium.md` | Two small owner rulings (2026-10-01): port the depot's long-title fix (`1122115`) to the hub's `fit_title`, and propose a depot-half cost below vanilla's elevator for the owner's yes. Stays out of the depot's files while `28` is live. | **Run 2026-10-01, the owner's yes owed on the cost** (hub port `b551930`, the hub smokes PASS, desk only, the in-game look is OI-38's; cost proposed at 5 Concrete / 2 Metals / 1 Machine Parts and 10000 build points per half, against vanilla's 10/5/2 for both sides; the depot's `wiring_smoke.py` §10b now fails on its hub-floor assertion and is owed to the next brief in the depot's tests; report `reports/HUB_TITLE_AND_DEPOT_COST_20261001.md`) |

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
