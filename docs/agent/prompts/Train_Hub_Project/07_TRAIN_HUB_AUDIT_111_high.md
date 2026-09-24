# Train hub audit on 1.1.1 — why the trains locked up, and what else we missed

**One-off investigation.** Start it with `task docs/agent/prompts/Train_Hub_Project/07_TRAIN_HUB_AUDIT_111_high.md`
in a fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. It **blocks** the drones chain's link 5
(`03_Drones/5_SMOKE_medium.md`): that sitting is paused on it.

## Authority

Owner, 2026-09-23, in the L5 sitting, after the trains locked up: *"I want you to author an audit,
see if we missed anything, see if anything 1.1.1 is causing issues top to bottom check."* The
subject is **our train system on the installed build**: the train hub dev mod
(`tools/devmods/train_hub/`: `10_TrainFloor.lua`, `20_TrainHub.lua`, `30_TrainHubDrones.lua`, the
template, the XTemplate), the rail shaft dev mod (`tools/devmods/rail_shaft/`), both loaded in the
owner's game, and tonight's logs. Every owner ruling already recorded (spec §10, `03_Drones/DESIGN.md`
and its overtaken-by list, OI-rows in `docs/PLAYTEST_CHECKLIST.md`) is settled. The audit does not
re-argue one; a ruling that 1.1.1 has made unworkable is a finding for the owner.

Owner, same sitting: **fixing code that a closed link built belongs to whoever is working now**,
not to the closed link. So a defect this audit confirms, with a fix inside the scope below, is yours
to fix, test and commit. A design fault is not. Record it and route it to the owner.

## Start and staleness

`git log`, `git pull` both repos. Authored at the commit that adds this file (on `1b32bc8`).
`git diff --stat 1b32bc8..HEAD -- tools/devmods/` empty means the facts below hold. Otherwise,
read what moved first.

## Evidence so far (claims, each with its check)

1. **The trains locked up** in the owner's game after link 5's reload. The log is
   `C:\Users\stkot\AppData\Roaming\Surviving Mars Relaunched\logs\Mars.exe-20260923-23.38.53-6aad2d75.log`.
   Before Save A the owner fired **five** TestKit meteors (`SMRTK_FIRE action=meteor_single`,
   ids 31, 39, 43, 46, 49). After Load A, `HubRepairStatus()` read `repairs 0 under way, 0 waiting`,
   then one job after meteor id 71. Nothing yet says whether those five breaks were repaired,
   never became jobs, or were not on tracks at all. Check: `grep -n "SMRTK_FIRE\|\[TrainHubDev\] repair" <log>`.
   The earlier logs this evening are `...-21.19.58-...` and `...-22.13.30-...`.
2. **The 1.1.1 patch sweep never covered the dev mods.** `prompts/perma/gamepatch/1.1.1.405907_2026-09-23.md`
   ran `patchcheck.py --code Code` (this repo's shipping `Code/` only). Nothing has diffed
   `tools/devmods/*/Code` against 1.1.0.403908 → 1.1.1.405907. Both trees are archived under
   `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\`. Check: the outbox file's `Command` line.
3. **A silent train stall is already on record** in `reports/RAIL_SHAFT_PROTOTYPE.md` §5–§7 (item 0):
   hub-line trains that never touched the shaft stopped, with no log line, derived but **not measured**.
   Its three console steps (`Sweep`, `Routes`, `Unlink`) are in §6. `SMR_RailShaftDev_20260923`
   is loaded tonight (`grep -n "RailShaftDev\]" <log>`). That is a lead, not the answer.
4. **`Persist error: Attempt to persist a C function`** on every save in the 1.1.1-era logs (hash
   `6aad2d75`: 7 of today's logs), none in the 1.1.0-era `6a91a190` logs. Tonight's stack ends in a
   vanilla `DroneControl.deficit_thread` (`DroneControl.lua:134` on 1.1.1). The rail shaft
   report attributes the same error to the `MarkFlight` repeat thread. The two attributions
   disagree. Check: `grep -c "Persist error" <each log>` and the stack below each.
5. **Our wraps and hooks that sit on train or drone paths**, as leads only: the global `WaitWakeup`
   replacement for the hub dwell (`20_TrainHub.lua`, `install_hub_dwell`), the `Station`
   `ShouldAddRequestToCommandCenter` override and the hub registered as a controller of every far
   station (`register_remote_stations`), `FlyingDrone:CanBeControlled`, the hub's completion of a
   repair through `ConstructionGroupLeader:Complete()`. On 1.1.1 a track's `repair_cgs` is
   cleared only when its `elements_under_construction` is empty (`TrackElement.lua:915-933`), and
   `BreakTracks` lives in `Meteors.lua:713-727`.
6. **This sitting's own commits** are `cafcaea` (no orphan adoption), `5ec8048` (the notice has no ETA
   and clears when done), `1b32bc8` (engine `HandoffAt="outside"` default, receipt re-pinned). They
   are in scope like everything else.

## End state

1. **The lock-up's cause**, measured rather than derived where the game is needed. If the owner's game is
   open, hand them one paste-safe console read at a time (`prompt-authoring`'s console rules) and read
   the answer from the log yourself. Say which of these it is, or what else: an unrepaired break,
   the rail shaft's route fault, one of our hooks, or a 1.1.1 change.
2. **The top-to-bottom 1.1.1 audit** of both dev mods: every engine function, field, class, message and
   line citation they touch, checked on the installed tree against 1.1.0. Report each as holds,
   moved, changed or gone, with the line. Cover `patchcheck.py`'s own reach too: if it can take a dev
   mod's `Code/`, run it and record the command. Also cover what `DESIGN.md` and the L4 report say
   link 5 must see in the game, and whether each still can on 1.1.1.
3. **The logs**: every error, warning and silent gap in tonight's three logs, attributed to its
   owner (ours, the fix pack, TestKit, vanilla), including the `ArtSpecEditor.lua:573` error on each
   load and the persist error's real source.
4. **Fixes** for confirmed defects in scope, each its own commit with its smoke (`repair_smoke.py`,
   `flight_smoke.py`, `look_smoke.py`, `move_smoke.py`, `traffic_smoke.py` as they apply) green, and the
   clearance receipt re-pinned if `30_TrainHubDrones.lua` changes (the command is in the receipt).
5. **The report** `docs/agent/reports/TRAIN_HUB_AUDIT_111_20260923.md`: the cause, the audit table,
   the log attributions, the fixes, and what is left for the owner. Then, in the same commit as
   deleting this file and its README row:
   - Append to `03_Drones/5_SMOKE_medium.md`'s `## Notes from upstream` what the resumed sitting must
     re-check.
   - Append the drift to `03_Drones/6_QA_high.md`'s notes.
   - Route defects through `smr-bug-library`.

   If time runs out, drop item 3's non-train log lines first, then item 2's citation-only rows.

## Scope

In: both dev mods, their tests and receipts, tonight's logs, the archived 1.1.0 and 1.1.1 trees, owner
console reads. Out: this repo's shipping `Code/` (already swept), the fix pack's code (route there),
redesign, art.

## Stops

1. The cause needs a game state nobody can reproduce without the owner, and the owner is not at the
   keyboard. Write the report with the cause open, the console reads ready, and stop.
2. The fix is a design change, or it touches a persisted name (`FIX_POLICY` persisted-name inventory):
   record it, route it to the owner, do not build it.
3. The fault is in the fix pack or TestKit: route it to that repo's checklist with the evidence and stop there.

## Do not claim

"1.1.1 is clean for the train hub" from a patchcheck pass alone. Claim the rows you checked, on the
build you read them on, and name the ones you did not check.

## Lifecycle

One-off: delete this file and its row in `Train_Hub_Project/README.md` in the commit that lands
the report.
