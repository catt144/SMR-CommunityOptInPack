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

*(links 1, 2 and 3 append here: the network graph and save hooks, the flight file's API, the
constants the owner settled)*

## Lifecycle

Append what the smoke must cover into link 5's notes, then **delete this file and strike its row in
`README.md` in the same commit**.
