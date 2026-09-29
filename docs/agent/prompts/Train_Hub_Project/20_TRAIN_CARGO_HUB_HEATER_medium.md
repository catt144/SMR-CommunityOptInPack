# Train Cargo Upgrade: the hub heats the ground within its drone range

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/20_TRAIN_CARGO_HUB_HEATER_medium.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Start with `git log --oneline -5`,
`git status` and `git pull`. Firing this means no sitting is running: the game reads the dev mod
straight from this repo.

## Authority (owner, 2026-09-28; settled)

Spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.10, grep `heats the ground`. While
the Train Cargo Upgrade is on, **the hub warms the ground within its own drone service range**,
the way a Subsurface Heater does. The owner recalls that range as 20; read the real value, and
use the hub's actual drone range, whatever it is. This comes on top of brief 19's warm network,
built in `22f83ec` with its sitting still owed, which removes the trains' cold penalty.
No upkeep was stated beyond the hub's own. Pick the cheapest faithful mechanism, and record the
call in the commit.

## Leads (claims; re-derive)

- Vanilla heaters register on the heat grid (`Heat.lua`, `heaters`; the spec's §10 heated-track
  candidate, grep `a heated`). `SubsurfaceHeater` is the reference building. Read how it declares
  its heat and range, and how a building is added to or removed from the heat grid.
- The upgrade's on/off, salvage and ruins states are already tracked for its modifiers and the
  speed chain in `tools/devmods/train_hub/Code/20_TrainHub.lua`. The heater must follow the same
  states: on only while the upgrade is applied, and off when it is toggled off, salvaged or in
  ruins.
- The hub's drone range: the hub is its own drone controller (grep `DroneControl`/`work_radius`
  or similar in `20_TrainHub.lua` and its template).

## Done

- In a cold wave, ground within the hub's range reads warm (heat above vanilla's cold threshold)
  while the upgrade is on, and cold again when it is off. There is no new persisted name, unless
  the heat grid persists something by itself: check, and stop if it would write a new saved
  name. `FIX_POLICY` rules apply (header first).
- If the template description changes, hand the owner the Mod Editor save, checked with
  `cargo_upgrade_smoke.py --require-generated`.
- A desk test with a mutation that fails it. Run every train hub smoke and report members =
  passing + failing.
- A short report, `docs/agent/reports/TRAIN_CARGO_HEATER_<date>.md`, with a pointer under the
  §4.10 ruling and an attended check of about three steps. **Combine it with brief 19's
  cold-wave check** (`reports/TRAIN_CARGO_WARM_20260928.md`, "Attended check"), so the owner runs
  one sitting for both. Name each slot by its function. A console line is acceptable for forcing
  the cold wave or reading heat at a spot (owner, 2026-09-27).

Run `python tools/doccheck.py` before the doc commit. Keep a live todo list before any write.

## Scope and stops

**In:** the hub's heater tied to Train Cargo, its description, and its tests. **Out:** hub
movement, the speed chain's behaviour (brief 19), and drones' or rovers' own cold penalties, which
the heat covers anyway. Stop and report if the heat grid cannot be driven without copying a
vanilla body, or if it needs a resource upkeep the owner has not ruled on.

Claim limit: desk PASS means the mocked vanilla agrees; the live claim is the cold-wave sitting.

References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md`, skill `doc-editing`.

## Lifecycle

One-off. The orchestrator deletes it with brief 19, and their README rows, once the combined
sitting passes.
