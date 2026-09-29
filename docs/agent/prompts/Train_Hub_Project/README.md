# Train_Hub_Project/ — the train hub's briefs, in fire order

The numbers are the order. **Fire the lowest number that is not held.** `Parked/` is never fired
unless the owner reopens it. **Once a brief has fired and its work is done, the orchestrator
decides** (owner, 2026-09-21): park it in `Parked/` if it is kept for possible touch-up work, or
delete it. Its row here moves or goes in the same commit.
Start any of them with `task docs/agent/prompts/Train_Hub_Project/<file>`.

`00` is live; `03_Drones/` is closed reference. **`22` is the live build brief**: the owner's
pre-audit fix list (station cargo display, hub storage 1,000/2,000, the Storage Hub upgrade; owner,
2026-09-29). Briefs 10 (5d routing), 17 (reactor flash) and 21 (Power Upgrade) passed live and were
deleted 2026-09-29; spec §4.8 ruling 10, §4.10 and their reports hold the record. Only one brief
that edits `20_TrainHub.lua` runs at a time.

The earlier `05`, the portal doors, was fired, built and then cut by the owner on 2026-09-22; its
survey stays in `reports/VANILLA_DOOR_ENTITIES_20260922.md`, its code in git at `8aef5de`.

| brief | what it is for | state |
|---|---|---|
| `00_TRAIN_ORCHESTRATOR.md` | The project lead. It reads build reports, keeps the spec current, briefs the next build, and never builds. | Standing; re-run as needed |
| `22_HUB_STORAGE_FIXES_high.md` | Owner 2026-09-29, pre-audit fix list: upgraded stations show no cargo; hub base storage 1,000 (2,000 with Capacity Network); a fourth, once-per-colony Storage Hub upgrade to 4,000 (60 Metals + 30 Machine Parts, +19 power while on). | **Built, desk-tested**; Mod Editor save and attended smoke owed: [report](../../reports/TRAIN_HUB_STORAGE_20260929.md) |
| `23_OI27_DRONE_MAP_GUARD_high.md` | OI-27 (owner, 2026-09-29): hub repair drones get no work, target or flight leg across a cross-map tunnel (a rail shaft). Same-map tunnels, hub membership and distribution unchanged. | Ready to fire; its smoke folds into the crossing's sittings |
| `RAIL_SHAFT_PROTOTYPE_high.md` | The rail shaft (cross-map train crossing, options F/G), taken into this project (owner, 2026-09-29, "since their surfaces touch"). The orchestrator's live handoff: settled rulings, where it stands, the work list through F vs G. Not fired as a build; builds are cut from it. | Live, orchestrator-held; deleted when F vs G is ruled and any module has its own brief |
| `03_Drones/` | Build 4 reference: the hub's vanilla Wasps rise from the pit and use train doors; the owner rulings are in spec §10 "Drones L5". Only `DESIGN.md` and `README.md` remain. | **Closed, PASS WITH CORRECTIONS:** `reports/drones_chain/L6_QA_20260925.md`. C1–C6 / D14(g,h) are routed; smoke evidence is bounded, ship tests remain owed |

## `Parked/` — do not fire

| brief | why it is kept |
|---|---|
| `01_TRAIN_HUB_STRUCTURE_high.md` | The structure pass, A to C runs (2026-09-21/23): maps, seams, lights, glass, reactor palette — all kept. Its cost reading moved to `05`. Kept for its pipeline facts and measurements; spec §9 holds the record. |
| `TRAIN_HUB_MODEL_high.md` | The hub's **3D shape** (geometry and UVs). It is final at radius 6. Kept to reopen if the look ever needs the model to move. |
| `TRAIN_HUB_LOOK_high.md` | The **umbrella record of the whole look pass**: why the hub read as flat paint, the owner's order, the deferred stages (fine normal, glass, themed reactor). Its stages fire as their own briefs; `01` is the current one. It retires when the owner accepts the look. |
| `TRAIN_HUB_MOVE_high.md` | Train movement through the hub. It is finished and owner-accepted (2026-09-21). It may reopen only at the final pre-launch test, if the owner wants a move tweaked. |
