# Train Cargo Upgrade and extras cut — 2026-09-28

Brief: `prompts/Train_Hub_Project/16_TRAIN_EXTRAS_CUT_AND_CARGO_UPGRADE_high.md`.
Authority: train design §4.8 ruling 10 and §4.10, owner 2026-09-28.
**Built and desk-checked; Mod Editor regeneration and attended smoke are owed.**
No game launch, native save/load, or attended acceptance is claimed.

## Changes

- `4614075`: archived the extras and their tests under
  `docs/archive/train_bay_extras_20260928/`. The live `70_TrainBay.lua` keeps auto-fill
  and final siding placement. Need, deployment, recall, hidden counts and snapshot
  storing are removed. The stack-display fix and distribution exports are retained.
- `HubTrain` remains a bare `Train` subclass with `persist_baseclass = "Train"`.
  Old loaded extras keep their cargo/passengers and use vanilla Idle and route counts.
  Existing routes can remain over the cap until trains are stored. Old snapshots already
  credited their empty extras to the pool; vanilla's delete-on-load list still deletes
  those objects. No new save writer or migration changes that credit.
- `1fb6785`: Train Cargo Upgrade, `SMROptInTrainHub6_TrainCargo`, in template slot 2:
  +100% `Train.max_shared_storage`, city label target; 40 Metals + 20 Polymers.
  Ownership and the audited salvage/rebuild path now take either upgrade ID. Each
  upgrade has an independent once-per-colony claim. Power follows vanilla; a spent-hub
  broadcast is inert. Salvage stops bonuses but keeps the claim; rebuilding carries
  the original on/off state; clearing ruins permits re-buy.
- `Train:GetNominalMoveSpeed` is chained, with both returned speed and turn-animation
  speed multiplied by 125/100 after vanilla computes them. Other arguments/returns
  are preserved. The boost reads the owner's applied cargo modifier on the train's
  city, including toggle, ruin and deletion behavior; there is no new saved speed field.
- Shared TestKit commit `19824ae`: slot **3 (read upgrades, train capacities and nominal
  speed)** replaces the retired bay read. It pauses nothing and changes no stock or
  upgrade state; pause before pressing. Slot **6 (stream every train and station)**
  remains the continuous movement/stock stream. Slot 3 supplies its missing capacities.

The capacity merge was already present at entry (`7dcef3e` including `0ec0631` and
`9fcdabc`). `git merge-base --is-ancestor 0ec0631 HEAD` succeeded and `capacity_smoke.py`
passed at `389ae1e`. The clean worktree at `9fcdabc` and its fully merged branch were
removed. Concurrent `50cec6b` corrected the task/map's stale merge instruction; its
diff touched only project briefs/map and was preserved.

## Evidence and boundaries

SOURCE: archived **1.1.1.405907**,
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`.
`grep -n -A 8 'properties =' Lua/Units/Train.lua` confirms the modifiable cargo and
passenger properties at :21-24; nominal speed is not among them. `grep -n -A 23
'function Train:GetNominalMoveSpeed' Lua/Units/Train.lua` re-read :593-614:
Faster Trains, Vacuum Rail, cold/Safe Transport and the law precede the animation
speed. These were source reads, not live speed measurements.

SOURCE/INFERRED: hub movement at `20_TrainHub.lua`'s `HubMoveTrain`, siding helpers
and departure (:630-825 at `1fb6785`) already derives speeds from that method and
calculates acceleration/time for its fixed geometry. This change edits none of those
paths. That supports using the boost without rebuilding hub movement; visual timing,
animation and native passage still need the smoke below.

MEASURED at desk: `python scratch/run_cargo_smokes.py` at `1fb6785` plus the report
commit's test additions, filter `sorted(Path("tools/devmods/train_hub/tests").glob("*_smoke.py"))`:
**20 members = 19 exit 0 + 1 exit 1**. Each member, command, HEAD and output is in
`docs/archive/train_cargo_upgrade_20260928/`; `summary.json` reconciles the total
against its named members. The runner is archived there too. `traffic_smoke.py` is
the sole failure, `-10800 != 0`, matching the task's known pre-existing failure.
The full suite is therefore not green.

`capacity_smoke.py` retains its original lifecycle checks. `cargo_upgrade_smoke.py`
executes the archived vanilla upgrade and speed bodies over mocked labels/modifiers;
it checks independent claims, cancelled construction, spent clicks, power, toggle,
salvage, map/position guards, rebuild on/off, load, clearing and re-buy. In-memory
mutations of speed, animation, salvage, ownership, rebuild and off-state carry all
fail. `cargo_slots_smoke.py` executes the actual shared slot and rejects calls to
stock/toggle writers and the UI's allocating HasUpgrade method.

`train_fill_smoke.py` checks auto-fill, route cap and pool retry, the retained class,
loaded cargo/passengers, and old delete-on-load snapshots through vanilla's
`PersistPostLoad`. `train_spawn_smoke.py` rejects a missing placement mutation.
These tests mock the engine and do not load an actual old save. Native label insertion,
Mod Editor output, concurrent engine scheduling and real save compatibility remain
unverified. Normal capacities and upgrade results are not live acceptance.

MEASURED figures from `cargo_upgrade_smoke.py` (resource scale 1000):

| Train configuration | Cargo units | Passengers |
|---|---:|---:|
| Base | 42 | 12 |
| Capacity Network only | 84 | 24 |
| Capacity Network + Train Cargo | 126 | 24 |
| Both + fixture's +50% cargo tech | 147 | 24 without passenger tech |

The fixture's passenger tech is separate: an existing +50% passenger bonus yields
30 with Capacity Network, unchanged when Train Cargo is bought. Cargo stacks by
addition, not repeated doubling. The test speed fixture reads 700 → 875 without
Faster Trains; 1000 → 1250 with it; 1500 → 1875 with Vacuum Rail; the law's 1995
becomes 2494 after rounding. Cold reductions occur before this upgrade's multiplier.

## Owner Mod Editor step

The authored fields are in `tools/devmods/train_hub/Data/BuildingTemplate/SMROptInTrainHub6.lua`.
The generated companion and `metadata.lua`'s `code_hash` were not hand-written.
Open the Train Hub dev mod in the Mod Editor, confirm template slot 2 is **Train Cargo
Upgrade**, +100% cargo, 40 Metals and 20 Polymers, then **save the mod** to regenerate
the class and hash together. Restart the game before the smoke.

Agent verification after that save: `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py
--require-generated`. This deliberately fails now on missing `upgrade2_id`; it will
require the generated numeric/id fields to match the authored source. Inspect the
actual editor diff and hash; passing the normal desk smoke does not satisfy this step.
The template description includes the +25% speed supplied by the runtime wrapper.

## Attended smoke — not run

Use a copy of an existing hub/bay save with a working hub line, another hub, trains,
and a reachable external depot holding the upgrade resources. Both mods and the
TestKit loaded are the standing configuration. Keep the original save as a control.
Every slot press below is **[NEVER RUN for this build]**.

1. **Start the stream and take the baseline.** After the Mod Editor save/restart,
   load the copy and immediately press slot **6 (stream every train and station)**.
   Pause and press slot **3 (read upgrades, train capacities and nominal speed)**.
   With Capacity Network on, expect its existing cargo/passenger and station bonuses;
   Train Cargo is unbuilt. An old loaded extra retains cargo/passengers, counts as
   a train, and no new extra deployment/recall/save-storing logs appear.
2. **Buy cargo and watch a trip.** Build Train Cargo using the hub's upgrade button
   and the external depot. Pause for slot **3 (read upgrades, train capacities and
   nominal speed)**: cargo rises by 42 units (105 → 147 with the fixture's +50% tech),
   station/passenger capacities stay unchanged, and the new cargo modifier is applied.
   Unpause at normal speed and watch a loaded trip through the hub. Stop for a jump,
   misplaced spawn, jam or movement error. With a spare pooled train, connect a new
   station: any auto-fill must obey the normal cap and spawn on the arm's siding.
3. **Toggle and ownership control.** Pause with one train stationary; slot **3 (read
   upgrades, train capacities and nominal speed)** before/after toggling Train Cargo
   off/on must show exactly a +25% rounded speed change at unchanged heat/tech/law,
   and a 42-unit cargo difference. Toggle it off, then Ctrl+click its spent row on
   the other hub: the owner stays off. Restore it on from its owner. Switching the
   hub off for power must leave bonuses applied; restore normal power afterwards.
4. **Salvage and rebuild.** Salvage the cargo owner, leaving ruins. Pause for slot
   **3 (read upgrades, train capacities and nominal speed)**: cargo/speed bonuses are
   off, claim held, other hub cannot buy it. Rebuild and read again: on returns once.
   Repeat after leaving the upgrade off: rebuilt remains off. If both upgrades were
   on that hub, each must retain its own on/off state. Clearing the ruins instead
   must release the claim and allow buying on the other hub.
5. **Save/load and close the log.** Save to a new slot with loaded trains, reload,
   and re-press slot **6 (stream every train and station)** because saves/loads stop
   it. Pause for slot **3 (read upgrades, train capacities and nominal speed)**:
   claim, toggle and capacities agree with the saved state without doubling; legacy
   cargo/passengers survive. Review new Lua errors and the stream with the agent.

An old snapshot that actually used the retired empty-extra delete list needs that
specific save to exercise it live; loading a newer empty colony is not that control.
The no-mod load and both-configuration release checks remain ship-test obligations.

## Handoff

Owner actions: Mod Editor save and the smoke above, routed to the fix pack's owner
list **ck219** because the sitting uses both mods. Brief 16 remains for the orchestrator's
lifecycle decision after the sitting passes. No new owner design decision is needed.
Out of scope: the known traffic smoke failure, distribution routing, and the owner's
unpainted flicker sighting; none was changed here.

Executed model: GPT-6 (Codex), as identified by the session instructions; no more
specific executed model ID or effort was exposed. No subagents. The live work list
was maintained in session commentary by commit-and-verify unit. PROBE SWEEP: clean.
