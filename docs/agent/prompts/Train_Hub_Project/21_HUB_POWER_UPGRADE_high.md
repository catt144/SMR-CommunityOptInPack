# Hub Power Upgrade: hub power 75 to 150 and cold-wave protection, moved off Train Cargo

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

## Sitting findings (owner, 2026-09-28; goes back to the build)

1. **FAIL: hub power.** In the combined cold-wave sitting, hub `SMROptInTrainHub6(6430)` shows
   **Power production 145** and consumption 10 in its panel (owner's screenshot). The report
   predicts 75 without Power and 150 with it; 145 matches neither. The owner ruled it a fail and
   sent it back. The sitting continues, so later findings are added here.

2. **Log `Mars.exe-20260928-22.20.16-6aad2d75.log`, first flush (read by the orchestrator).**
   The console read's only output, at line 344 and before any cold wave, was `145 255 255 255`:
   power 145, with center, edge and outside heat all at 255. The panel's 145 is therefore the
   hub's own `GetUIPowerProduction()` and not a panel artefact. The cold wave was sent twice
   through TestKit's `SMRTK_DISASTER action=cold_wave setting=ColdWave_GameRule` (lines 731 and
   1130), not through the report's `CheatColdWave("ColdWave_High")`, and no heat read followed
   it. Slot 3 read three times (marks 94, 290 and 1017). All 15 trains show `cargo_cap=105000`,
   `nominal_speed=1500` and `turn_anim_speed=4500` each time, and the only modifier listed is
   `SMROptInTrainHub6_CapacityNetwork`. Slot 3 reads nominal speed, so it cannot show the cold
   penalty that step 1 predicts it shows. The step-1 train-speed check needs a reader that
   reports the effective speed, and a TestKit fix for that goes in the fix brief.

3. **Owner, by eye, during the cold wave (2026-09-28): the trains look right.** The second flush
   of the same log has no console read. Its only heat read is still the pre-cold one at line 344,
   so the ≤ 90 cold heat and the 75 on the hub without Power remain unmeasured.

4. **Console reads during the cold wave, same log.** Line 3382 (the other hub) reads
   `75 0 0 0`: 75 power and cold ground, as predicted. Line 3386 (the first hub) reads
   `145 255 255 0`: 145 power, the center and service edge warm, and cold just outside. That is
   Power's heat footprint, at the wrong power figure. The owner stopped the sitting here on
   2026-09-28 because the build goes back for repair first, and steps 2 to 5 are unrun.

**Repair asked for (owner, 2026-09-28):** the first hub must read 75 or 150, never 145. Find
where 145 comes from in the live save; the desk smokes pass, so they do not model it. Add each
train's *effective* speed, not nominal, to TestKit slot 6's live stream (owner, 2026-09-28: no
new slot), so the next sitting can watch the cold slowdown. The TestKit is shared with the fix
pack (`B:\Dev\SMR\SMR-BugFixPack-TestKit`). Then hand back for a rerun of the whole combined sitting.

## Rerun after `9bffa5c` / TestKit `4a31982` (owner, 2026-09-28, log `Mars.exe-20260928-22.57.28-6aad2d75.log`)

The owner's method: Power on one hub and off on the other, read before and after one cold wave.
- **Load repair:** lines 276 and 277 read `hub 6430 power base 70000>75000, output 75000>75000`
  and the same for 6495.
- **Power, PASS:** the panels read 150 on the hub with Power and 75 on the hub without it
  (owner's screenshots). The console reads during the cold wave: line 3357 (without Power) is
  `75 0 0 0`, and line 3363 (with Power) is `150 255 255 0`, heated at the center and the
  service edge and cold just outside.
- **Train speed:** slot 6 `effective_speed` for moving trains is 5617 by mode both before the
  cold wave (dispatched at line 1998) and to the end of the log (t 20525756 to 23045369).
  The owner, by eye: they look right.
- **Not yet shown:** that trains slow in the cold with no Power anywhere. Without that, the
  steady speed does not separate Power's colony protection from no cold penalty at all.
- **Seen, not predicted:** the panel reads consumption 10 on the hub with Power and 20 on the
  hub without it.

## Lifecycle

One-off. The orchestrator deletes it once its sitting passes. Briefs 19 and 20 were deleted when
this brief was written; their reports stay.
