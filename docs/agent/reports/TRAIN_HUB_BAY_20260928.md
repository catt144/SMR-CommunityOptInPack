# Train bay — hub extras by need, recalled when idle (2026-09-28)

Brief `prompts/Train_Hub_Project/13_TRAIN_HUB_BAY_BUILD_high.md`; authority spec §4.8 ruling 9
(owner, 2026-09-28). Dev mod only. Game source is archived **1.1.1.405907**. **Desk-verified; live
smoke owed** to the orchestrator's sitting below. Nothing here was run in the game.

## What was built

`tools/devmods/train_hub/Code/70_TrainBay.lua` (commit `9947552`), registered in `metadata.lua`
and `items.lua`. The probe `50_TrainHubDispatchProbe.lua` is retired. `40_TrainDistribution.lua`
gains two read-only exports, `D.BranchNeed` and `D.ChildNeed`, with no change to its behaviour.
TestKit slot 3 is a bay read (kit commit `a4b122b`). No vanilla body is copied. Vanilla places,
loads, moves and stores every train.

| ruling 9 rule | how | rung |
|---|---|---|
| The bay is the colony pool | deploy with vanilla `TrackBase:AssignTrain` (`Track.lua:428-457`); recall with `Train:DestroySilent` (`Train.lua:157`, pool +1 by `OnDemolish` `:188`) | 1 |
| The player sees vanilla | `GetTrainsOnRoute` (`TrainTransport.lua:492`) wrapped to subtract the `HubTrain`s vanilla's own walk counted on that route. It skips a `seen`-table short circuit and never goes below 0. The cap gate (`Track.lua:423`), route counts and warnings therefore read vanilla trains only | 0 |
| Extras past the cap, up to 5 per hub route | for the hub's own `AssignTrain` call only, `TrackBase:CanAddVehicle` answers true (an in-memory entry, 1 s of game time); `TransportLinkChanged` (`StationsLink.lua:45`) then calls `ChangeClass("HubTrain")` on the new train | 0 |
| Deployed by need | brief 11's signal (below); one spawn per free arm per tick, every 10 game minutes | 0 |
| Recalled as soon as idle | `HubTrain:Idle` stores an empty extra the moment `LoadTrain` sets `Idle` (`Train.lua:285`); an extra with cargo keeps vanilla `Idle` | 1 |
| Empty extras stored at save | inside `PersistGame` (`Savegame.lua:853`): `DeleteOnLoadGame` (`persist.lua:197`) plus `City:AddPrefabs("Train", n, false)` (`City.lua:478`); both undone after the snapshot, and also on error | 1 |
| Loaded extras persist as `HubTrain` | `persist_baseclass = "Train"`; a missing class resolves to its base (`persist.lua:79,164`; `_cobject.lua:135`) | 5, ruling 9's residual |
| Auto-fill | on `TrainRoutesRebuilt` (`TrainTransport.lua:357`), a hub line whose station count grew owes one plain vanilla train from the pool, retried for 2 game hours | 1 |

## Calls delegated by the brief

- **The need rule.** For each hub line and each resource, sum `BranchNeed` over the line's
  hub-parented stations (brief 10's parent tree carries their off-hub branches). Cap deliveries by
  hub stock and collections by hub room. Loads are that sum divided by train capacity, rounded up.
  Extras wanted are the loads minus the line's vanilla trains, clamped to 0..5.
- **Idle threshold and hysteresis.** An extra is stored the moment it idles empty. If it carried no
  cargo at all since it spawned, that line's deploys pause for 2 game hours, because the need
  signal and vanilla's `TransferCargo` then disagree. Extras are never recalled on a need drop;
  vanilla ends them by giving them no work.
- **The save sequence is scoped to the snapshot, not to `SaveGameStart`/`SaveGameDone`.** Autosaves
  run game time between those messages, and bug-report saves skip them (the hub's own save guard
  records the same, `20_TrainHub.lua` header of `install_hub_save_guard`). No game time passes
  inside `PersistGame`, so a stored train cannot pick up cargo before the write.
- **Which empties are stored.** Trains in `LoadTrain` or `UnloadTrain` are skipped because
  colonists may be boarding or leaving. Stop 3 is not hit: a stored train has no cargo, no
  `assigned_resources` booking and no passengers.
- **Spawn position.** No edit to `20_TrainHub.lua`. At the desk, archived `GetSpawnPoint`
  (`Track.lua:206`) on the dev hub gives exactly the Stop spot of the arm where a parked train
  sits, facing out along that arm (72 cases). A spawned train's departure is the reversing-train
  path (`TrainDepart`, `station_arrival_track` nil). Whether the owner's "another loading
  platform" sighting matches this is for sitting step 1.

## Desk evidence

`python tools/devmods/train_hub/tests/bay_smoke.py` at HEAD `9947552`, exit 0, 7 PASS
[RAN 2026-09-28]: need exports; spawn spot; extras past the cap to 5 with the route reading 2/2;
recall and cooldown; save-time storing, load deletion through archived `Train:Done` with no cargo
dropped, error undo; the `Train:HubTrain` fallback; auto-fill. Two mutated copies of the bay code
(no hiding; no post-save undo) each fail it. Also passing at that tree: `distribution_smoke`
(22 PASS), `distribution_departure_smoke` (14), `distribution_ui_smoke` (4),
`distribution_slots_smoke` (4, with the rebound slot 3), `spoilage_smoke` (1), `capacity_smoke`
(PASS). `parsecheck` covers dev 8 files and TestKit 33, with 0 errors. `doccheck` is GREEN.
**Not tested:** the engine's `ChangeClass`, the real serializer, hub movement after a spawn, a live
departure, the in-game tick and every UI count.

## Sitting (for the orchestrator, attended; predictions written before boot)

This is a fresh boot with both mods and the TestKit, loading `build6_capacity_covered_pass3`.
Press slot 6 once so the stream runs the whole sitting. Every `[TrainBay]` line lands in the log.

1. **Spawn on its siding.** Pause, press slot 3, then slot 1 (empty every non-hub station), then
   slot 3 again. *Predict:* the second read shows `wanted` ≥ 1 on at least one BAY row, and
   `extras=0`. Unpause at normal speed. *Predict:* within 10 game minutes the log shows
   `[TrainBay] deploy train=<H> ... arm=<k>`, and the new train stands on arm k's siding where a
   parked train sits, facing out. *Stop:* it appears at the hub centre or on another arm.
2. **Departs and serves.** *Predict:* within about a fifth of a game hour, train H's stream rows
   read `command=GotoStation` on that line with cargo aboard. Later, the far station's stock rows
   change when it arrives. *Stop:* H stays on the siding for more than a game hour.
3. **Back to the bay when idle.** Press Scratch (balance every station) so the need goes away.
   *Predict:* each extra logs `[TrainBay] recall train=<H> ... worked=true` when it next idles
   empty, and a slot 3 read shows `pool` up by the recalls and `extras` down to 0. No "A Train was
   stored" notification appears, because the recall passes no reason.
4. **The count stays vanilla.** While extras are out (repeat step 1's slot 1 if needed), select a
   hub line's far station and open its Trains section. *Predict:* `<trains>/<max>` equals that
   line's BAY `vanilla`/`cap`, not vanilla + extras. On a line at the cap, the assign cursor says
   "Maximum number of Trains on this route".
5. **Save and reload through the pool.** With some extras out, save to a new slot. *Predict:* the
   log shows `[TrainBay] save: stored=<n> kept=<m>`, and slot 3 straight after reads the same pool
   and extras as before the save. Load that save from the menu and press slot 3. *Predict:* `pool`
   = pre-save pool + n, `extras` = m, then deploys by need as in step 1. Close the log and count
   the exact token `LUA ERROR`. *Predict:* 0.

The load without the mod is the ship test's, not this smoke's.

## Findings outside the fence (reported, not edited)

- Per-track counts are not hidden. `TrackBase:GetOverviewInfo` "Trains on Track"
  (`Track.lua:600-602`) and `Station:GetNumTrainsOnTracks` read `#assigned_vehicles`, so they
  include extras. Hiding them would need two UI wrappers.
- Colonist travel reads the hidden count. `GetTrainsOnRoute(track) > 0` gates colonist legs
  (`Colonist.lua:3562`, `ColonistTransport.lua:53`, `Dome.lua:403`), so a hub line whose only
  trains are extras plans no passenger trips.
- The player's "Available Trains" (the pool) drops while extras are out. This follows from ruling
  9's pool-as-bay rule, but the owner sees it move.
- `HubTrain` carries no `SMROptIn` prefix, by ruling 9. A different mod that defines a class of
  that name would collide.

## Close-out

Files: `70_TrainBay.lua` (new), `40_TrainDistribution.lua` (exports), `metadata.lua`,
`items.lua`, `50_TrainHubDispatchProbe.lua` (deleted), `tests/bay_smoke.py` (new),
`FIX_POLICY.md` inventory row 15, this report, one pointer under spec ruling 9; TestKit
`Code/80_AgentSlots.lua` slot 3. The work list was kept in the session's messages, one commit per
unit. No subagents. Executed model: Claude Fable 5.1 (`claude-fable-5-1`), as declared by this
session's environment.
