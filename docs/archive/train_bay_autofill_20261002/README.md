# Retired auto-fill and hub siding placement — 2026-10-02

Owner authority: train design §4.8 ruling 10, the 2026-10-02 amendments (`cfc2065`): *"If the
add train is something the player needs to do that is also fine. I don't want it to be a
complicated thing, and I don't want them spawned in the hub."* Brief 34b cut auto-fill and the
hub-side siding placement; the live `Code/TrainHub_70_TrainBay.lua` keeps the `HubTrain` class
(persisted name, `FIX_POLICY` row 15) and adds the hub's add-train refusal.

These are the pre-cut bytes at `b4106ce` (the file as brief 34 moved it; identical to the dev
copy at `4433c2f`). `Code/70_TrainBay.lua` holds the route snapshot, the owed window, the
ten-minute tick, `try_fill` (which assigned on the hub's arm) and the `TransportLinkChanged`
handler that moved a hub-spawned train onto the computed siding through
`Floor.HubSpawnLocation` (removed from `Code/TrainHub_20_TrainHub.lua` in the same commit; it
had no other caller). `tests/` holds the archived-body fixture (reads the 1.1.1.405907 tree),
`train_fill_smoke.py` (auto-fill, pool and old-snapshot compatibility) and `train_spawn_smoke.py`
(siding geometry and the placement handler). Restore into `Code/` and `tools/trains/hub/tests/`
to investigate a future design; the fixture expects that location.

Build history: `9947552` (bay), `989bd56` (vanilla-first dispatch), `9b58888` (siding placement),
`378bd39`, the 2026-09-28 extras cut (`docs/archive/train_bay_extras_20260928/`, whose README
describes the live file as it then was), brief 34's move, and this cut. Reports:
`docs/agent/reports/TRAIN_34B_PLAN_20261002.md` (why the cut is the simpler choice and how the
hub refuses) and `TRAIN_BAY_FIXES_20260928.md`.
