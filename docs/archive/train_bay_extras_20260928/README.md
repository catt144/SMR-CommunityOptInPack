# Retired hub extras — 2026-09-28

Owner authority: train design §4.8 ruling 10. These are the pre-cut bytes from
`389ae1e` (unchanged by `50cec6b`). Restore into the same dev-mod paths to investigate
a future design; the tests expect that location and the archived 1.1.1.405907 source
tree. This is reference code, outside the mod's load list.

`Code/70_TrainBay.lua` contains need checks, a capped deployment from the colony pool,
the hidden route count and cap bypass, `HubTrain` conversion, idle recall, and
snapshot-only storing of empty extras. It also contains the auto-fill and siding
placement retained in the live file. `tests/bay_smoke.py` exercises the pool, route
count, need exports, recall and save/load fallback. `bay_gates_smoke.py` adds the
vanilla-working, settle, persistence and shared-route guards. `bay_spawn_smoke.py`
checks final placement after class conversion as well as vanilla auto-fill.

Build history: `9947552` (bay), `989bd56` (vanilla-first dispatch), `9b58888`
(final siding placement), `378bd39` (subsequent bay work). Read the diffs before
reviving any part. Reports: `docs/agent/reports/TRAIN_HUB_BAY_20260928.md` and
`docs/agent/reports/TRAIN_BAY_FIXES_20260928.md`. The latter records desk results
and leaves its revised dispatch, final placement and save/load attended smoke owed;
those desk results do not establish native behavior. The reported earlier live
spawn discrepancy's native cause remained unresolved.

The cut keeps `HubTrain` as a bare subclass of `Train` with `persist_baseclass =
"Train"`, because old loaded extras can be saved under that name. They now use vanilla
Idle and route counts; loaded cargo and passengers are retained. Old empty extras
already marked for deletion still use vanilla's delete-on-load list and the pool
credit already in their snapshot. No deployment, recall or save writer remains.

The stack-display fix `9ed5f4f` and distribution exports remain live. A future builder
must reconcile this snapshot with later movement, distribution and save contracts;
copying the whole old file back would reinstate the retired behavior.
