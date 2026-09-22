# Drones chain, link 5 — the smoke with the owner

**Link 5 of the `03_Drones` chain** (`README.md`). **ATTENDED.** Runs after link 4. Read
`DESIGN.md` §5 and §6 and your `## Notes from upstream`. `git log`, `git pull` both repos first.

## Authority

Testing depth (owner): **a smoke test only** — the full prediction battery runs once, on the final
build. The sitting loads the standing save (`train_hub_base`), which has the stations, tracks and
lines prebuilt; only the hub is built each round. About five steps at a time. After an autosave the
owner re-presses the armed slot.

## End state

1. `DESIGN.md` §5's scenarios, in the owner's order, with the ETAs measured and recorded: a far
   break, save and reload mid-trip, completion and trains running again, a break with the hub short
   of stock, the hub toggled off, a drone near the hub doing ordinary drone work and never charging,
   the reassign buttons greyed, more than 30 jobs with 30 out, one destroyed, an autosave mid-trip.
2. `DESIGN.md` §6: whether a station can build a train with no repair drone out, and what the hub
   waits for if it cannot — with the owner's ruling on the acknowledgement launch if a drone is the
   missing piece.
3. The result recorded in the hub report and spec §10, and the owner's rulings where the role that
   obeys them reads them.

**Both configurations** (`FIX_POLICY` §8) and both toggle directions belong to the module's ship
test; this is a design smoke. Say plainly which of them this sitting did not cover.

## Live work list

One todo item per commit-and-verify unit.

## Scope

In: the sitting, the measurements, the records, small fixes the sitting forces. Out: redesign, new
mechanisms, art.

## Stops

1. A scenario cannot run because a fixture is missing: look for an existing save that has it before
   asking the owner to build one.
2. The sitting turns up a design fault rather than a bug: record it and route it to the owner; do
   not redesign live.

## Do not claim

Do not claim "repairs work" from one break. Claim the breaks, the distances, the ETAs and the
reload, in that order.

## Notes from upstream

*(link 4 appends here: what shipped, what the smoke must cover, the persisted name)*

## Lifecycle

Append anything unresolved into link 6's notes, then **delete this file and strike its row in
`README.md` in the same commit**.
