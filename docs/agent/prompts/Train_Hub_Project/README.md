# Train_Hub_Project/ — the train hub's briefs, in fire order

The numbers are the order. **Fire the lowest number that is not held.** `Parked/` is never fired
unless the owner reopens it. **Once a brief has fired and its work is done, the orchestrator
decides** (owner, 2026-09-21): park it in `Parked/` if it is kept for possible touch-up work, or
delete it. Its row here moves or goes in the same commit.
Start any of them with `task docs/agent/prompts/Train_Hub_Project/<file>`.

`00`, `02` to `05` are live (`01` is parked, done; the earlier `05`, the portal doors, was fired, built and then cut by the owner on
2026-09-22; its survey stays in `reports/VANILLA_DOOR_ENTITIES_20260922.md`, its code in git at
`8aef5de`). Only one brief that edits `tools/devmods/train_hub/Code/20_TrainHub.lua` runs
at a time: `02`, `03_Drones/`'s link 4 and `04`; `05` touches no Lua. The drones chain's
links 2-3 stay out of that file by design, so they run beside the structure pass.

| brief | what it is for | state |
|---|---|---|
| `00_TRAIN_ORCHESTRATOR.md` | The project lead. It reads build reports, keeps the spec current, briefs the next build, and never builds. | Standing; re-run as needed |
| `02_TRAIN_HUB_LOADERRORS_low.md` | Two errors that fire every time the dev hub loads. A small code fix with its cause already found. | Live, fire any time; Lua one-at-a-time |
| `03_Drones/` | Build 4: the hub's drones, **as a mini chain** (owner, 2026-09-22). Vanilla Wasps launched from the pit, repairing broken track out on the network from the hub's stock. Its `DESIGN.md` holds the settled design; its numbered links each outbox what the next needs, so the link that waits for the structure pass starts fully briefed. Its own `README.md` is the manifest. | **Link 2E is next** (unattended: owner redirect 2026-09-23 — the engine paths everything between our pit launch and return, under stock commands only). Link 3 then A/Bs it against the scripted flight, preserved at tag `drones-scripted-flight-20260923`; link 4 waits for `20_TrainHub.lua` and gained the fleet load-scaling ask |
| `04_TRAIN_HUB_BUILDTRACK_high.md` | Build 5: the same drones build new track from the hub's stock, using `03`'s pending list. | Held until `03`'s smoke is recorded |
| `05_TRAIN_HUB_BODYPAINT_high.md` | **The final body paint** — the reactor's P4 feel (navy panels, polished off-white bands) on every body surface not held by an owner ruling; then the whole-hub GPU cost reading that closes the look pass. | **Live: fire in a fresh session** (owner, 2026-09-23); Lua untouched, so it runs beside `02` and the drones chain |

## `Parked/` — do not fire

| brief | why it is kept |
|---|---|
| `01_TRAIN_HUB_STRUCTURE_high.md` | The structure pass, A to C runs (2026-09-21/23): maps, seams, lights, glass, reactor palette — all kept. Its cost reading moved to `05`. Kept for its pipeline facts and measurements; spec §9 holds the record. |
| `TRAIN_HUB_MODEL_high.md` | The hub's **3D shape** (geometry and UVs). It is final at radius 6. Kept to reopen if the look ever needs the model to move. |
| `TRAIN_HUB_LOOK_high.md` | The **umbrella record of the whole look pass**: why the hub read as flat paint, the owner's order, the deferred stages (fine normal, glass, themed reactor). Its stages fire as their own briefs; `01` is the current one. It retires when the owner accepts the look. |
| `TRAIN_HUB_MOVE_high.md` | Train movement through the hub. It is finished and owner-accepted (2026-09-21). It may reopen only at the final pre-launch test, if the owner wants a move tweaked. |
