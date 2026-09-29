# Hub Power Upgrade: double reactor output and cold-wave protection, moved off Train Cargo

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/21_HUB_POWER_UPGRADE_high.md` in a fresh
session rooted at `B:\Dev\SMR\SMR-OptInPack`. Start with `git log --oneline -5`, `git status` and
`git pull`. Firing this means no sitting is running: the game reads the dev mod straight from
this repo.

## Authority (owner, 2026-09-28; settled)

Spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.10, grep `third hub upgrade, the
Power Upgrade`.
- **Train Cargo goes back to +100% cargo and +25% train speed only.** Its live-passed behaviour
  (2026-09-28) must not change.
- **A new, third hub upgrade: the Power Upgrade.** While it is on, it:
  - **raises the hub's power production from 75 to 150** (owner's figures: base 75, +75 with
    the upgrade; the base hub changes from today's 70 to 75);
  - heats the ground within the hub's drone service range (15 hexes, read from `work_radius`), as
    brief 20 built;
  - removes the trains' cold penalty, as brief 19 built.
- **Cost 30 Metals + 20 Electronics.** No tech.
- **Per hub**, not once per colony: each hub can buy it. So there is no spent-hub claim. The
  once-per-colony machinery of the other two upgrades must not apply to it.
- Salvage or ruins switch it off, as they do the others. The hub is not rebuilt the normal way
  (owner, 2026-09-28).

## What exists to move (claims; re-derive)

- Brief 19, the warm network: `22f83ec`, report `reports/TRAIN_CARGO_WARM_20260928.md`. It is
  the Train Cargo speed chain, calling vanilla with `GetHeatAt` returning `MaxHeat` while the
  cargo modifier is applied.
- Brief 20, the hub heater: `0ed1d87`, report `reports/TRAIN_CARGO_HEATER_20260928.md`. It is
  vanilla `BaseHeater:ApplyHeat` driven by the cargo modifier's state.
- Both are gated on Train Cargo today. Re-gate both on the Power Upgrade. Keep the +25% speed
  gated on Train Cargo alone. A train's cold immunity must follow **whether its colony has any
  hub with Power on**; decide and record whether that is right for a per-hub upgrade. Its heat
  reads Power, not Cargo. Leaving either on Train Cargo is a defect.
- The live panel, owner's screenshot 2026-09-28: the hub read **70** power production, and
  insufficient power during a cold wave. Find where the hub's production is set, make the base 75,
  and make the Power Upgrade add +75, for 150. Record the figures before and after.
- Template: slot 2's description currently says it "warms the network". Revert it, and add slot 3
  for the Power Upgrade. The owner's Mod Editor save regenerates the class and hash; check it
  with `cargo_upgrade_smoke.py --require-generated`, extended to cover slot 3.

## Done

- Desk tests: Train Cargo gives cargo and speed only, with no heat or cold effect. Power, per
  hub, gives 150 power (75 without it), ground heat within range and trains' cold immunity. Toggling it
  off, salvaging or ruins removes all three. A second hub can buy its own. Each test has a
  mutation that fails it. Run every train hub smoke and report members = passing + failing.
- No new persisted name, unless unavoidable: then stop, unless it goes on `FIX_POLICY`'s
  inventory with a reason.
- A short report, `docs/agent/reports/TRAIN_HUB_POWER_UPGRADE_<date>.md`, with a pointer under
  the §4.10 ruling. It holds the Mod Editor step and one combined attended cold-wave check of
  about five steps. Base it on brief 20's check, adding a power reading before and after. Name
  each slot by its function; console lines are acceptable (owner, 2026-09-27).

Run `python tools/doccheck.py` before each doc commit. Keep a live todo list before any write.

## Scope and stops

**In:** the three upgrade effects' gating, the reactor output, the template fields and the tests.
**Out:** hub movement, distribution, and the reactor's look (brief 17). Stop and report if
raising the output needs a copied vanilla body, or if per-hub ownership conflicts with how
vanilla stores upgrades.

Claim limit: desk PASS means the mocked vanilla agrees; the live claim is the cold-wave sitting.

References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md` (header first), skill `doc-editing`.

## Lifecycle

One-off. The orchestrator deletes it once its sitting passes. Briefs 19 and 20 were deleted when
this brief was written; their reports stay.
