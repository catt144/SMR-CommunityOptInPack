# Train_Hub_Project/ — the train hub's briefs, in fire order

The numbers are the order. **Fire the lowest number that is not held.** `Parked/` is never fired
unless the owner reopens it. **Once a brief has fired and its work is done, the orchestrator
decides** (owner, 2026-09-21): park it in `Parked/` if it is kept for possible touch-up work, or
delete it. Its row here moves or goes in the same commit.
Start any of them with `task docs/agent/prompts/Train_Hub_Project/<file>`.

`00` is live; `03_Drones/` is closed reference. **`10` is the live build brief**: 5d routing,
so stations chained to the hub obey their rows (owner, 2026-09-27); its stranded-cargo repair passed live
2026-09-27; its chained Export/Import legs are still owed. The train bay (ruling 9) was built by `13`,
audited alongside by `14` and fixed by `15`, all deleted 2026-09-28; ruling 10 then cut the hub extras
to an archive and asked for a second train upgrade, which **`16`** builds. `09`, the distribution centre,
is built, passed live on every hub-line station and deleted (2026-09-27); spec §4.7/§4.8 and
`reports/TRAIN_DISTRIBUTION_PASS2_20260926.md` hold its record. `10` owns `10_TrainFloor.lua` and the
distribution files; only one brief that edits `20_TrainHub.lua` runs at a time.

The earlier `05`, the portal doors, was fired, built and then cut by the owner on 2026-09-22; its
survey stays in `reports/VANILLA_DOOR_ENTITIES_20260922.md`, its code in git at `8aef5de`.

| brief | what it is for | state |
|---|---|---|
| `00_TRAIN_ORCHESTRATOR.md` | The project lead. It reads build reports, keeps the spec current, briefs the next build, and never builds. | Standing; re-run as needed |
| `10_TRAIN_HUB_ROUTING_5D_high.md` | 5d cargo routing, spec §6 OPTION 5 and the §4.8 rulings of 2026-09-27: stations chained to the hub through another station's line obey their distribution rows, forwarded hop by hop. No route-model change. Owns `10_TrainFloor.lua`, `40_TrainDistribution.lua` and `45_TrainDistributionUI.lua`. | **LIVE**; chained Export/Import legs owed |
| `16_TRAIN_EXTRAS_CUT_AND_CARGO_UPGRADE_high.md` | Spec ruling 10 and §4.10 (owner 2026-09-28): archive then cut the hub extras (keep auto-fill and siding placement), build the Train Cargo Upgrade (+100% cargo, +25% speed, 40 Metals + 20 Polymers). | **Built; Mod Editor save and attended smoke owed.** `reports/TRAIN_CARGO_UPGRADE_20260928.md`; orchestrator retires after the sitting passes. |
| `03_Drones/` | Build 4 reference: the hub's vanilla Wasps rise from the pit and use train doors; the owner rulings are in spec §10 "Drones L5". Only `DESIGN.md` and `README.md` remain. | **Closed, PASS WITH CORRECTIONS:** `reports/drones_chain/L6_QA_20260925.md`. C1–C6 / D14(g,h) are routed; smoke evidence is bounded, ship tests remain owed |

## `Parked/` — do not fire

| brief | why it is kept |
|---|---|
| `01_TRAIN_HUB_STRUCTURE_high.md` | The structure pass, A to C runs (2026-09-21/23): maps, seams, lights, glass, reactor palette — all kept. Its cost reading moved to `05`. Kept for its pipeline facts and measurements; spec §9 holds the record. |
| `TRAIN_HUB_MODEL_high.md` | The hub's **3D shape** (geometry and UVs). It is final at radius 6. Kept to reopen if the look ever needs the model to move. |
| `TRAIN_HUB_LOOK_high.md` | The **umbrella record of the whole look pass**: why the hub read as flat paint, the owner's order, the deferred stages (fine normal, glass, themed reactor). Its stages fire as their own briefs; `01` is the current one. It retires when the owner accepts the look. |
| `TRAIN_HUB_MOVE_high.md` | Train movement through the hub. It is finished and owner-accepted (2026-09-21). It may reopen only at the final pre-launch test, if the owner wants a move tweaked. |
