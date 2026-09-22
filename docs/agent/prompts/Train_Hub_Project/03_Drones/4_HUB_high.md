# Drones chain, link 4 — the hub half: dispatch, the pending list, the save guard

**Link 4 of the `03_Drones` chain** (`README.md`). ⛔ **HELD until the structure pass is out of
`tools/devmods/train_hub/Code/20_TrainHub.lua`** — check `git log` on that file and the structure
brief (`../01_TRAIN_HUB_STRUCTURE_high.md`) before you start; only one brief edits it at a time.

Read `DESIGN.md` — it is the whole design and it is settled — and your `## Notes from upstream`,
which links 1, 2 and 3 wrote. `git log`, `git pull` both repos first.

## Authority

`DESIGN.md`'s owner rulings, unchanged. The flight already exists and is tuned
(`Code/30_TrainHubDrones.lua`): **you call it, you do not rebuild it.** This link is the hub's half —
everything in `DESIGN.md` §§1, 2, 4 and the save guard — plus the persisted name.

**Both bans bind** (`FIX_POLICY.md`). This build adds persisted state: name the pending-repair list
once, permanently, with the kind field build 5 needs, and add it to the persisted-name inventory in
the same commit.

## End state

`DESIGN.md` §1 (dispatch and reachability), §2 (completion at the deadline, the outstanding cost
only), §4 (the infopanel line and the track-repair toggle), the save guard, the `CanBeControlled`
wrap and the no-free-drone-leak backstop — built on the flight link's calls, with the smoke left to
link 5.

`FIX_POLICY` §0 sets the disable direction for content. The toggle is tested in both directions in
link 5, not here.

## Live work list

One todo item per commit-and-verify unit, before any write.

## Scope

In: `20_TrainHub.lua`, the persisted name and its inventory row, the panel, the toggle, the tests
that run offline. Out: the flight file's internals, art, the entity, the model, build 5's track
construction (design the list for it; ship only the repair kind).

## Stops

1. The structure pass is still in `20_TrainHub.lua`: wait or report, never edit alongside it.
2. A second persisted name turns out to be unavoidable: stop and route the name to the owner.
3. The completion path cannot charge the outstanding cost without double-paying: report the
   measurement rather than shipping a guess.

## Do not claim

Do not claim the repair works from an offline run. Claim the code path, the persisted shape, and
what link 5's sitting still has to show.

## Notes from upstream

- **Link-1 evidence:** `docs/agent/reports/drones_chain/L1_SURVEY_20260922.md`; engine facts
  `EF-112`–`EF-115`; verbatim lenses under `docs/agent/reports/drones_chain/agents/`.
- **Reachability:** `ForEachConnectedTrack` is one-hop and calls `GetDestStation`, which rejects a
  track while `elements_under_construction` is nonempty. A break creates exactly such a site, so
  that helper can hide the broken edge and everything beyond it. Build an explicit hub-rooted BFS
  with visited station/tunnel nodes and visited tracks, using physical `GetStartStation` /
  `GetEndStation` owners across existing broken tracks plus reciprocal tunnel `linked_obj` edges.
  Cached routes, `CanTrainsRun` and a nil helper result are not repair reachability.
- **Graph smoke owed:** component before/after a connecting break, far side still reachable for
  repair, independent remote component excluded, then a tunnel and a station cycle. Log endpoint
  owners, repair group, `elements_under_construction` and visited sets.
- **Completion:** use the live repair construction-group leader's dynamic `Complete()` after
  validating the site and outstanding cost. It dispatches to each `TrackConstructionSite:Complete`,
  which restores/reconnects the broken element. `DESIGN.md`'s generic
  `ConstructionSite:Complete()` citation is an imprecise body reference; do not call that base body
  directly or synthesize a drone work request.
- **Work/accounting boundary:** controller radius governs automatic request discovery; track graph
  membership does not. Station maintenance material can self-fill, but the `repair` work request
  still needs a worker; dust is cleared by maintenance and has no separate clean request. Ship only
  the work kinds `DESIGN.md` authorizes and keep each material/work/completion path explicit.
- **Save guard:** `EF-023`/`EF-027` establish by-value command-thread persistence;
  `EF-024`/`EF-030` establish start/done hooks including autosave; `EF-070` establishes that game
  time can run before the persist walk. Persist only pending data plus absolute deadline. Raise a
  save gate, synchronously remove track visuals/commands, make every spawner honor the gate until
  `SaveGameDone`, then re-arm from remaining deadline even after a failed save. Load validates and
  does the same; never restart a full trip. Manual-save, autosave, reload, failed-save and long-soak
  A/B remain owed.
- **Control:** chain `Drone:CanBeControlled`; after calling the captured original, return false only
  when the live `command_center` is a train hub and otherwise return the original result. That one
  gate greys both reassign buttons. Keep the no-free-drone backstop separate.
- Links 2 and 3 still owe the flight API and owner-tuned constants below this block.

## Lifecycle

Append what the smoke must cover into link 5's notes, then **delete this file and strike its row in
`README.md` in the same commit**.
