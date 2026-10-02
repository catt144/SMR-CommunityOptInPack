# 34b — Export rows take only a storage's excess (fix build)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/34b_EXPORT_KEEPS_DESIRED_high.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`, **after brief `34`'s code move has landed**
(the station rows then live in this mod; editing the dev copy would collide with the move).
Reasoning: high (vanilla drone request priorities against a storage's desired amount).

## Authority and outcome

The owner, 2026-10-02, after a live test: with a resource's station row on **Export**, drones
*"drain everything ... including resource pads that have a desired amount set. ... I expect drones
to fill the station of all the excess up to the desired amount."* Spec
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.8's mode table already says Export
drones haul *"the area's excess in"*; the ruling under it (grep `Export takes only the excess`)
defines excess: **stock above that storage's own Desired Amount.** That is settled; do not reopen it.

Outcome: an Export row's drones fill the station only from stock above each source storage's
Desired Amount, and a storage at or under its Desired Amount loses nothing to the row. Import,
Balanced, Not accepted and the trains' side behave as before. Done when the change is committed
with a desk check, a preloaded smoke is ready, and the owner has run it and seen a storage hold its
Desired Amount beside an Export row.

## Evidence (owner's screenshots, 2026-10-02, build at `e223b25` or later)

- `StationSmall(10650)`, row `Food · Export` 16.5/120, Trains 0.
- `StorageFood(1067)`, Desired Amount 50, holding **8.2/180**: drained below 50 while the
  Export row was still filling.
- Balanced rows were seen to fill only once every other storage was full. The owner reads that as
  intended (vanilla); it is out of scope.

## Your judgment

The approach is yours: where the drain comes from (the row's demand priority, the request
amounts, how vanilla moves stock depot-to-depot) and the narrowest change that honours the ruling.
Stores with no Desired Amount of their own (producers' output, any depot without the slider):
match what vanilla's depot-to-depot moves do with them, and record the call and its source lines
(with the build read) in the commit message. The owner checks it by eye at the smoke.

## Work list and start

Use the todo tool before any write; one item per commit-and-verify unit, one in progress.
Start: `git log --oneline -5`, `git pull`; authored at `e223b25` (+ this brief's commit). Confirm
34's move has landed before editing; if it has not, stop (below).

## Scope

In: the Export row's drone-side sourcing, on stations with and without a hub. Out: trains'
loading, Import and Balanced behaviour, the depot's rows, anything 34 or 35 owns. Report outside
findings without editing.

## Testing

A design pass: smoke only (spec §10). Preload it into SMRTK slots (`tools/SMRTK.md`); the owner
clicks and does not type. Name each slot's function beside its number, call hubs by role, and
write predictions before boot. The smoke shows one storage with a Desired Amount set, holding at
or above it beside an Export row that keeps filling from storage above Desired, with Run until at
top speed rather than owner minutes of watching. An autosave disarms a slot; say to re-press it.
`FIX_POLICY` §8's both-configuration run belongs to brief `35`.

## Stops (report instead of continuing)

1. Brief 34's move has not landed.
2. Honouring the ruling needs a persisted-name change or crosses a ban in `FIX_POLICY`'s header.
3. Vanilla gives drones no way to respect a source's Desired Amount without rewriting its request
   system; report the options and their costs.

## Claim limits

A desk check proves the code path, not the behaviour: say "desk-verified", not "fixed", until the
owner's smoke passes.

## References and lifecycle

`CLAUDE.md`, `docs/agent/WORKFLOW.md`, `docs/agent/FIX_POLICY.md`; `smr-bug-library` for engine
facts you file (`docs/agent/facts/INDEX.md`, `docs/agent/bugs/INDEX.md`); `doc-editing` for any doc.
Report to `docs/agent/reports/` and tell the orchestrator. The orchestrator owns this brief's
lifecycle; do not move or delete it.
