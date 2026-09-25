# Distribution centre — the console prototype: does the mechanism work at all?

**LIVE, one-off. The owner fires it; the orchestrator parks or deletes it once done.** `git log`,
`git pull` first. Authoring sha: OptInPack `69f7cc5`. This is an investigation with a small build at
the end, not a feature: **nothing here ships, nothing persists, and no UI is written.**

⛔ **File fence — the drones chain's link 5 is running in parallel.** You do NOT open
`Code/20_TrainHub.lua`, `Code/30_TrainHubDrones.lua` or `tests/repair_smoke.py`; they are link 5's
and it is editing them today. You also touch no art. **Yours:** `Code/10_TrainFloor.lua`, a new
`Code/40_TrainDistribution.lua`, a new test of your own, and `metadata.lua`'s registration line.
Register the new file **as a mod item**, the way `30_TrainHubDrones` was registered in `6574794` —
that commit is the root cause fix for five silently dropped code lines, so do not invent a second
way. Re-check the entry after any import.

## Authority

The owner's design, spec §4.8 (2026-09-24) — read §4.8 and §4.9 in
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` before anything else. The design is settled
on paper and **explicitly not authorised to be built**. Three things in it have never been shown to
work, everything else rests on them, and this brief exists to settle all three in one sitting:

1. **The transient claim path has never executed.** `Train:TransferCargo` is already wrapped for a
   per-call claim (`10_TrainFloor.lua`), and no station has ever requested one. Does a transient
   claim make **trains see a different number from drones**? That is the whole design.
2. **Do drones actually respond to the baseline numbers** the way §4.8's table assumes — demand open
   pulls the area's excess in, supply available above a floor lets them distribute outward?
3. **`transport_policy = "accept"` (import) has no measured drone effect** (§4.3, §7.2: the fixture
   had no consumer in drone range). Does it do anything, with a consumer present?

**Where the owner's own game says the honest answer may be "only half of it".** Remote stations in
their colony sit outside any command centre (§4.8's precondition), so on an uncovered spoke there
are no drones to respond at all. Say plainly which of your results needed local drone coverage.

## End state

1. **`Code/40_TrainDistribution.lua`**, console-driven, no persistence, no UI, no save hooks:
   a call that sets a mode (`export` / `import` / `balanced`) and a slider for one resource on one
   selected station, and a status read that prints, for that station and resource, what a **train**
   would see and what a **drone** would see, side by side. Your call on the API shape and names.
2. **The three questions answered**, each with what you ran and what you saw. A "no" is as valuable
   as a "yes" here: if trains and drones cannot be made to see different numbers, the design's export
   and import modes collapse into one, and the owner needs to know that before any UI is drawn.
3. **A ≤ 5-step console script for the owner**, in their session's terms: which station to select,
   what to type, what to watch, and what each outcome means. The owner runs it when their drone
   testing frees the game; you do not get a sitting of your own.
4. **What can be proven without the game, proven without it**, and a plain statement of what only
   the game can answer. Mocks cannot show drone behaviour: do not let a green test stand in for it.
5. The result in spec §4.8 under a dated heading, with MEASURED / SOURCE / INFERRED on every claim.

## Leads, not the route

- `10_TrainFloor.lua:6-38` is the standing-claim mechanism (the station claims its own supply
  request, lowering the `GetTargetAmount` every hauler reads); `:168-198` is the train-side wrap
  that exists to support the transient shape.
- §4.5's six vanilla paths rewrite desired amounts, and §4.6's alias trap governs any wrap of the
  request registration. Both apply to the real feature; say whether they bit the prototype.
- The hub's own maintenance reserve is a standing claim in production today, so its behaviour is a
  working reference for what a claim does to trains, drones and the panel.

## Scope

In: the new file, `10_TrainFloor.lua`, your own test, the registration line, the report, spec §4.8.
Out: the three fenced files, UI, persistence, the hub's own state, the station cards, anything that
ships, and the design decisions themselves — they are the owner's and are recorded.

## Stops

1. A transient claim cannot be made to work at all: stop and report. That is a design-level answer,
   not a failure, and it is worth more than a workaround.
2. The fenced files turn out to be unavoidable: stop and hand it back rather than editing them
   while link 5 is in flight.
3. Answering needs the game and the owner's sitting is not available: deliver the build plus the
   five-step script, and say which questions remain open.

## Do not claim

Do not claim the distribution centre works, or is feasible, from this prototype — it tests the
mechanism, not the design. Do not claim a drone response from a mock. Do not claim `accept` works
without a consumer in drone range.

## Lifecycle

One-off. Report, record in spec §4.8, then the orchestrator parks or deletes it.
