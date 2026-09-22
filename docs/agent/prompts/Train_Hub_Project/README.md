# Train_Hub_Project/ — the train hub's briefs, in fire order

The numbers are the order. **Fire the lowest number that is not held.** `Parked/` is never fired
unless the owner reopens it. **Once a brief has fired and its work is done, the orchestrator
decides** (owner, 2026-09-21): park it in `Parked/` if it is kept for possible touch-up work, or
delete it. Its row here moves or goes in the same commit.
Start any of them with `task docs/agent/prompts/Train_Hub_Project/<file>`.

`00` to `05` are live. Only one brief that edits `tools/devmods/train_hub/Code/20_TrainHub.lua` runs
at a time: `02`, `03`, `04`, `05`, and `01`'s structure lights step.

| brief | what it is for | state |
|---|---|---|
| `00_TRAIN_ORCHESTRATOR.md` | The project lead. It reads build reports, keeps the spec current, briefs the next build, and never builds. | Standing; re-run as needed |
| `01_TRAIN_HUB_STRUCTURE_high.md` | **The hub's look, now.** Textures on everything except the finished road: ring, portals, ribs, supports, rails and trim. It fixes the blurry, jagged seams and rib bands, then adds the structure's own lights, then takes one GPU reading of the whole hub, on against off. | **NEXT, fire now** |
| `02_TRAIN_HUB_LOADERRORS_low.md` | Two errors that fire every time the dev hub loads. A small code fix with its cause already found. | Live, fire any time; Lua one-at-a-time |
| `03_TRAIN_HUB_DRONES_high.md` | Build 4: the hub's drones. Vanilla Wasps launched from a pad under the hub, repairing broken track out on the network from the hub's stock. Unbuilt beyond a few test drones: deploy, movement, the retextured storage and pad, dispatch, the pending list. | Live, **after the look** |
| `04_TRAIN_HUB_BUILDTRACK_high.md` | Build 5: the same drones build new track from the hub's stock, using `03`'s pending list. | Held until `03`'s smoke is recorded |
| `05_TRAIN_HUB_DOORS_high.md` | **Portal doors from vanilla door entities** (owner, 2026-09-22): the owner's five-minute in-game look at the survey's candidates, then two or more door styles attached to the six portals in Lua, opened by an approaching train and closed behind it, with the door plane the portal rebuild must fit. Survey: `reports/VANILLA_DOOR_ENTITIES_20260922.md`. | Live, fire now; runs beside `01`'s portal rebuild; Lua one-at-a-time |

## `Parked/` — do not fire

| brief | why it is kept |
|---|---|
| `TRAIN_HUB_MODEL_high.md` | The hub's **3D shape** (geometry and UVs). It is final at radius 6. Kept to reopen if the look ever needs the model to move. |
| `TRAIN_HUB_LOOK_high.md` | The **umbrella record of the whole look pass**: why the hub read as flat paint, the owner's order, the deferred stages (fine normal, glass, themed reactor). Its stages fire as their own briefs; `01` is the current one. It retires when the owner accepts the look. |
| `TRAIN_HUB_MOVE_high.md` | Train movement through the hub. It is finished and owner-accepted (2026-09-21). It may reopen only at the final pre-launch test, if the owner wants a move tweaked. |
