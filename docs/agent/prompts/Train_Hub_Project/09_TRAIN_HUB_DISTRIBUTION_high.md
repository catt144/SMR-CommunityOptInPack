# The distribution centre — pass 3: the covered-station fix

**LIVE: pass 3** (2026-09-27), for a fresh session. Passes 1 and 2 built the feature. The dev mod
is `tools/devmods/train_hub/`, and your files are `Code/40_TrainDistribution.lua`,
`Code/45_TrainDistributionUI.lua` and `Code/10_TrainFloor.lua`. The owner's live sittings of
2026-09-27 passed every mode on uncovered stations. They also turned up one fault, which this pass
fixes: **a station inside a drone hub's range throws a division by zero in vanilla's train loading
code**. Read spec §4.7 and §4.8 of `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` (every
ruling, the save-boundary ladder, both sittings' results) and
`docs/agent/reports/TRAIN_DISTRIBUTION_PASS2_20260926.md` (the mechanism, the rung table, the desk
suite) before the first write.

## Authority

- ⚖️ **Spec §4.8 in full (owner, 2026-09-24/26).** Per-resource modes with the hub as sink and
  source, state on the hub, a full hub refuses, and an uncovered spoke gets the train half only. The
  save boundary may be crossed **minimally**, at the lowest rung of §4.8's ladder that works. The
  current build sits at rung 2 with one persisted name, `SMROptIn_distribution`, and this pass adds
  no new one.
- ⚖️ **Spec §4.7, the UI (owner, 2026-09-26/27), is built and accepted by eye.** It covers the
  four-state hex cycle on vanilla's rows, per-state titles, the slider in the row's line, **no drag
  bubble**, titles that wrap only between words, Ctrl + click copying **state and slider value**
  without advancing, and the 80% shrink floor. Change the UI only to fix a fault.
- `FIX_POLICY` §0, §1's technique ranking and §2 (the alias rule, gated by
  `tools/harvest_wrap_targets.py --check`) apply, and both bans bind. Testing depth is **smoke only**.
  Method: small and rough.

## The fault — orchestrator's reading, a claim to confirm by desk reproduction

Sitting log `docs/archive/train_distribution_20260926/sittings/Mars.exe-20260927-12.55.25-6aad2d75.log`
(on disk, untracked; its receipt is beside it) holds **20× `[LUA ERROR] Division by zero`**, from its
line 1762 on. Every one has this stack: vanilla `Lua/Units/Train.lua(946)` ← `TrainTransport.lua(448)
ForEachStationAlongTrack` ← `Train.lua(913)` ← `10_TrainFloor.lua(92) WithTransientClaims` ←
`40_TrainDistribution.lua(244)`. Locals: `station` = the hub (`SMROptInTrainHub6`), `res = Metals`,
`storage = 0`, `available = 53`, `target = nil`. Setup: the owner quick-built a Drone Hub and a
Metals depot next to spoke 2007 (`covered=true`), and drones moved **fractional** stock (22.6 at the
spoke, 113.5 at the hub). There were no errors in any uncovered run.

The reading, against the archived **1.1.1.405907** `Src/Lua/Units/Train.lua` (re-derive with
`grep -n`):
- Vanilla builds `res_data` by adding `GetResDesiredAmount(res) / scale` and
  `GetMaxStorage(res) / scale` for each enabled station on the line (the loop near `:886-900`).
- `:946` then divides by `res_data.storage[res]` whenever `res_data.desired[res] > 0`.
- `train_view` in `40_TrainDistribution.lua` answers `{ enabled = order > 0, capacity = order }`,
  and `Station:GetResDesiredAmount` answers `const.ResourceScale` for any enabled row.
- The engine uses integer division (EF-116 in `docs/agent/facts/`; lupa does not reproduce it), so
  an `order` under 1000 adds 0 to storage while desire adds 1, and the loader divides by zero.
- Confirm or overturn this with a desk case before fixing. Check `Train:UnloadAll`'s answers for the
  same shape.

## End state

1. **A desk reproduction of the fault** with a sub-unit order: it fails before the fix and passes
   after. The suite's harness must model integer division where the engine does, or the case proves
   nothing.
2. **The fix**, so that no answered row can report desire without at least one whole unit of
   capacity. The approach is your judgement, at the same rung. Exports, imports, Balanced and the
   full-hub refusal must still measure as before; the existing cases are the control.
3. **The whole suite rerun** plus `python tools/parsecheck.py` and `harvest_wrap_targets.py
   --check`, with every output preserved with its command and HEAD. The known `traffic_smoke`
   failure (`-10800 != 0`) stays recorded, not silently fixed.
4. **Next-sitting predictions** appended to `TRAIN_DISTRIBUTION_PASS2_20260926.md`, for the
   **covered drain/fill leg**, the one leg of spec §4.8 not yet witnessed. The build's own tooltip
   text states what it should show: in Import, local drones may drain the station toward zero; in
   Export, local drones fill the station and trains take anything above the floor; in Balanced, the
   slider is the drones' desired amount.
   - **The fixture:** from `build6_capacity`, which has no drone coverage at any station, the owner
     quick-builds a Drone Hub and a Metals depot beside a network spoke, then saves it once under a
     new name. Name that save in the predictions.
   - **Sitting mechanics:** the orchestrator runs the sitting with the owner and relays results; you
     do not attend. Preload slots under `tools/SMRTK.md`; slot 4 reads only Metals now. The owner
     accepts a console line where no slot fits (2026-09-27). The orchestrator's generic read is:
     `local D,s,r=SMROptInTrainDistribution,SelectedObj,"Metals"; local m,p,c=D.RowState(s,r); print("DISTREAD",s.handle,r,m,p,c,s.supply[r] and s.supply[r]:GetActualAmount(),D.HasDroneCoverage(s))`
   - **Predictions must include zero `LUA ERROR` lines** across a run of at least one sol at top
     speed with fractional stock in play.
5. **Hand back** with the commit and a short relay the orchestrator can read in one pass.

## Start

`git log --oneline -5`, `git status`, `git pull --ff-only`. Authored on `6759fc4`. Put the work in
the todo tool before the first write, one item per commit-and-verify unit. Commit with a pathspec.

## Scope

**In:** `Code/40_TrainDistribution.lua`, `Code/45_TrainDistributionUI.lua`, `Code/10_TrainFloor.lua`,
the distribution tests under `tests/`, TestKit slots, `TRAIN_DISTRIBUTION_PASS2_20260926.md`, and
spec §4.8's result lines.

**Out:** ⛔ `Code/20_TrainHub.lua` and `Code/30_TrainHubDrones.lua`. The header inventory line for
`SMROptIn_distribution` is already landed. Also out: the Capacity Network Upgrade, train
construction or placement (§4.9), routing, the shipping `Code/` tree, and `FIX_POLICY` §8's
both-configuration ship test, which is owed for the whole hub and is not yours. Report anything
outside this fence without editing it.

## Stops

- The fix needs a rung above 2, or a copied vanilla body: report the measurement before writing it.
- The desk harness cannot reproduce the fault: report what it took to try, and do not ship a guess.

## Do not claim

- ⛔ Not "the covered case works". Claim the desk reproduction and fix; the live leg is the
  orchestrator's.
- ⛔ Not "save-safe". Claim the rung, with the residual named.

## Lifecycle

Done when the fix and predictions are committed and handed back. The orchestrator runs the sitting,
then parks or deletes this brief and moves its row in `README.md` in one commit (owner, 2026-09-21).
Build agents do not delete or move their own brief.
