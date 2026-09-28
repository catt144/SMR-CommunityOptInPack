# Train Cargo Upgrade: trains ignore the cold while it is on

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/19_TRAIN_CARGO_WARM_NETWORK_medium.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Start with `git log --oneline -5`,
`git status` and `git pull`. Firing this brief means no sitting is running: the game reads the dev
mod straight from this repo.

## Authority (owner, 2026-09-28; settled)

Spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.10, grep `also warms the network`:
while the Train Cargo Upgrade is on, **trains take no cold penalty**. That is on top of its
existing +100% cargo and +25% speed, which passed live on 2026-09-28. Its scope is the same as
the upgrade's: every train in the colony. It is not a new upgrade and not a new modifier slot.

## Starting facts (claims; re-derive line numbers with `grep -n`)

- Vanilla `Train:GetNominalMoveSpeed` (archived 1.1.1.405907, `Units/Train.lua` ~:593-614) applies
  ×1/3 below heat 90, or ×2/3 with Safe Transport, before the law. Brief 16's chain in
  `tools/devmods/train_hub/Code/20_TrainHub.lua` multiplies the result by 125/100 after vanilla.
  Its report says cold reductions apply before this multiplier.
  See `docs/agent/reports/TRAIN_CARGO_UPGRADE_20260928.md`.
- TestKit slot 3 (read upgrades, train capacities and speed) already reports nominal speed.

## Done

- With the upgrade on, a train in the cold reads the same nominal speed as a warm one, and the
  +25% still applies. With it off, or salvaged, vanilla's cold penalty returns. Other arguments
  and returns are preserved, and no body is copied (`FIX_POLICY` §2). There is no new persisted
  name.
- The template's description mentions the warm network. If that changes template fields, hand
  the owner the Mod Editor save, as brief 16 did, with `cargo_upgrade_smoke.py
  --require-generated` as the check.
- A desk test in `cargo_upgrade_smoke.py`, or a sibling, covering cold on, cold off, and cold
  with Safe Transport, with a mutation that fails it. Every train hub smoke is then run and
  reported as members = passing + failing (`traffic_smoke` may still be under brief 18).
- A short report, `docs/agent/reports/TRAIN_CARGO_WARM_<date>.md`, with a pointer under the
  §4.10 ruling and an attended check of about three steps. Name each slot by its function. If a
  console line is the only way to force a cold state, say so; that is acceptable (owner,
  2026-09-27).

Run `python tools/doccheck.py` before the doc commit. Keep a live todo list before any write.

## Scope and stops

**In:** the upgrade's speed chain, its description, and its tests. **Out:** hub movement, the
heat grid, drones and rovers, and `traffic_smoke.py` (brief 18). Stop and report if removing the
penalty needs more than adjusting the returned speed, for example if cold also changes
`turn_anim_speed` or train movement elsewhere in a way the chain cannot reach.

Claim limit: desk PASS means the mocked vanilla agrees; a cold wave in the game is the live claim.

References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md` (header first), skill `doc-editing`.

## Lifecycle

One-off. The orchestrator deletes it, with its README row, once its check passes.
