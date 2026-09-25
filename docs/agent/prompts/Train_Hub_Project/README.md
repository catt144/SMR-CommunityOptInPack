# Train_Hub_Project/ — the train hub's briefs, in fire order

The numbers are the order. **Fire the lowest number that is not held.** `Parked/` is never fired
unless the owner reopens it. **Once a brief has fired and its work is done, the orchestrator
decides** (owner, 2026-09-21): park it in `Parked/` if it is kept for possible touch-up work, or
delete it. Its row here moves or goes in the same commit.
Start any of them with `task docs/agent/prompts/Train_Hub_Project/<file>`.

`00`, `02` to `07` are live (`01` is parked, done; the earlier `05`, the portal doors, was fired, built and then cut by the owner on
2026-09-22; its survey stays in `reports/VANILLA_DOOR_ENTITIES_20260922.md`, its code in git at
`8aef5de`). Only one brief that edits `tools/devmods/train_hub/Code/20_TrainHub.lua` runs
at a time: `02`, `03_Drones/`'s link 4 and `04`; `05` and `06` touch no Lua. The drones chain's
links 2-3 stay out of that file by design, so they run beside the structure pass.

| brief | what it is for | state |
|---|---|---|
| `00_TRAIN_ORCHESTRATOR.md` | The project lead. It reads build reports, keeps the spec current, briefs the next build, and never builds. | Standing; re-run as needed |
| `02_TRAIN_HUB_LOADERRORS_low.md` | Two errors that fire every time the dev hub loads. A small code fix with its cause already found. | Live, fire any time; Lua one-at-a-time |
| `03_Drones/` | Build 4 reference: the hub's vanilla Wasps rise from the pit and use train doors; the owner rulings are in spec §10 "Drones L5". Only `DESIGN.md` and `README.md` remain. | **Closed, PASS WITH CORRECTIONS:** `reports/drones_chain/L6_QA_20260925.md`. C1–C6 / D14(g,h) are routed; smoke evidence is bounded, ship tests remain owed |
| `04_TRAIN_HUB_BUILDTRACK_high.md` | Build 5: the same drones build new track from the hub's stock, using `03`'s pending list. | Its hold is lifted: `03`'s smoke is recorded (L5 report, 2026-09-25). Fire when the owner says |
| `05_TRAIN_HUB_BODYPAINT_high.md` | **The final body paint** — the reactor's P4 feel (navy panels, polished off-white bands) on every body surface not held by an owner ruling; then the whole-hub GPU cost reading that closes the look pass. | **Paint KEPT (owner, 2026-09-23; restore point 6). Live for its step 6, the cost reading, and the Wasp palette judgement handed over from drones link 5 (owner, 2026-09-25)** |
| `06_TRAIN_HUB_ICON_medium.md` | **A build-menu icon of the hub's own** (owner, 2026-09-23: the vanilla large-station icon "just looks like another station"): a 232 × 100 render of the painted hub in vanilla's icon style, the template's `display_icon` pointed at it, the owner's pick in the menu. | **Live: fire any time; no Lua** |
| `07_DISTRIBUTION_PROTOTYPE_high.md` | **The distribution centre's console prototype** (spec §4.8, design only): does a transient claim make trains and drones see different numbers, do drones respond to the baseline numbers, and does `accept` do anything with a consumer in range. No UI, no persistence, nothing ships. | **Live: fire any time.** Its fence out of `20_TrainHub.lua`, `30_TrainHubDrones.lua` and `repair_smoke.py` held while the drones chain's link 5 ran; link 5 closed 2026-09-25, and the one-Lua-brief-at-a-time rule above still applies |

## `Parked/` — do not fire

| brief | why it is kept |
|---|---|
| `01_TRAIN_HUB_STRUCTURE_high.md` | The structure pass, A to C runs (2026-09-21/23): maps, seams, lights, glass, reactor palette — all kept. Its cost reading moved to `05`. Kept for its pipeline facts and measurements; spec §9 holds the record. |
| `TRAIN_HUB_MODEL_high.md` | The hub's **3D shape** (geometry and UVs). It is final at radius 6. Kept to reopen if the look ever needs the model to move. |
| `TRAIN_HUB_LOOK_high.md` | The **umbrella record of the whole look pass**: why the hub read as flat paint, the owner's order, the deferred stages (fine normal, glass, themed reactor). Its stages fire as their own briefs; `01` is the current one. It retires when the owner accepts the look. |
| `TRAIN_HUB_MOVE_high.md` | Train movement through the hub. It is finished and owner-accepted (2026-09-21). It may reopen only at the final pre-launch test, if the owner wants a move tweaked. |
