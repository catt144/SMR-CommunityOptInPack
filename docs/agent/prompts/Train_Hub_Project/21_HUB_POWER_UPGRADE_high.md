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
- **Once per colony, like the other two** (owner, 2026-09-28, replacing the first per-hub
  ruling; spec §4.10, grep `all three hub upgrades work the same way`): *"buy once, and never
  have to buy again for future hubs."* It uses the other two's spent-hub claim. Bought once, it
  gives every hub, present and future, 150 power and ground heat, and every train cold immunity.
- Salvage or ruins switch it off, as they do the others. The hub is not rebuilt the normal way
  (owner, 2026-09-28).

## What exists to move (claims; re-derive)

- Brief 19, the warm network: `22f83ec`, report `reports/TRAIN_CARGO_WARM_20260928.md`. It is
  the Train Cargo speed chain, calling vanilla with `GetHeatAt` returning `MaxHeat` while the
  cargo modifier is applied.
- Brief 20, the hub heater: `0ed1d87`, report `reports/TRAIN_CARGO_HEATER_20260928.md`. It is
  vanilla `BaseHeater:ApplyHeat` driven by the cargo modifier's state.
- Both are gated on Train Cargo today. Re-gate both on the Power Upgrade. Keep the +25% speed
  gated on Train Cargo alone. Cold immunity, power and heat all follow **whether the colony's
  Power Upgrade is bought and on**, applied to every hub and train. Its heat
  reads Power, not Cargo. Leaving either on Train Cargo is a defect.
- The live panel, owner's screenshot 2026-09-28: the hub read **70** power production, and
  insufficient power during a cold wave. Find where the hub's production is set, make the base 75,
  and make the Power Upgrade add +75, for 150. Record the figures before and after.
- Template: slot 2's description currently says it "warms the network". Revert it, and add slot 3
  for the Power Upgrade. The owner's Mod Editor save regenerates the class and hash; check it
  with `cargo_upgrade_smoke.py --require-generated`, extended to cover slot 3.

## Done

- Desk tests: Train Cargo gives cargo and speed only, with no heat or cold effect. Power, once
  per colony, gives every hub 150 power (75 without it) and ground heat within range, and every
  train cold immunity; a hub built after the purchase gets them without buying. Toggling it
  off, or the owning hub's salvage or ruins, removes all three, as the other two upgrades do. Each test has a
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
raising the output needs a copied vanilla body, or if applying one colony purchase to every
hub conflicts with how vanilla stores upgrades.

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
- **Train speed with Power on one hub:** slot 6 `effective_speed` for moving trains is 5617 by
  mode both before the cold wave (dispatched at line 1998) and after it. The stream has almost no
  rows after t≈20.9M and was disarmed by an autosave at t=21715379 (line 5304), so it covers
  about 0.5 sol of cold. An earlier "to the end of the log" reading was wrong. The owner, by eye:
  they look right.
- **Cold with no Power on (owner turned it off; same log):** after `CheatStopDisaster` (line
  5451), a fresh cold wave (line 5619) and slot 6 re-armed (line 5911), trains on `GotoStation`
  drop from 5617/5612 to **3758/3754** by t≥23150000. The cold penalty is real and Power's removal
  of it is what held the 5617.
- **Seen, not predicted:** the panel reads consumption 10 on the hub with Power and 20 on the
  hub without it.

**Repair 2 (owner, 2026-09-28):** make Power once per colony, like the other two upgrades,
per the Authority clause above: every hub gets 150 and heat, and every train keeps its warm speed.
Cover it with mutations that fail a per-hub power or heat gate and a missed later-built hub.
The next sitting: buy Power on one hub, then check that both hubs read 150 and heat, that the
other hub shows it spent, and that slot 6 shows trains keeping warm speed in a cold wave with
Power on and slowing with it off. The consumption difference, 10 against 20, goes into the
report, explained or found wrong.

## Rerun after `1622b29` (owner, 2026-09-29, log `Mars.exe-20260929-12.03.53-6aad2d75.log`)

- Owner's Mod Editor save: `cargo_upgrade_smoke.py --require-generated` exit 0 ("Generated
  upgrade slots 2/3 and base power match source").
- Load (lines 282 and 283): both hubs `base 70000>75000, output 75000>75000`, so Power was off at load.
- Cold wave at line 332; slot 6 armed at line 617. Slot 3 at line 2008 lists only
  CapacityNetwork modifiers, and trains cruise without the Cargo bonus in this copy.
- **Power's train protection, PASS by slot 6:** moving `GotoStation` trains go from about
  **3000** in the cold (t 20.5M) to **4500 to 4507** after Power was bought (t ≥ 21.0M). 4500 is
  the warm speed without Cargo (5617 ≈ 4500 × 1.25; 3000 ≈ 4500 × 2/3, the same ratio as 3758 to
  5617).
- No console read in this log: both hubs at 150, their heat and the spent display rest on the
  owner's panels.

## Lifecycle

One-off. The orchestrator deletes it once its sitting passes. Briefs 19 and 20 were deleted when
this brief was written; their reports stay.
