# Train hub build 6: the Capacity Network Upgrade

**LIVE** (owner, 2026-09-26, answering OI-30: *"lets do capacity"*). The design is settled in
spec §4.10 of `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` — read it before the first
write; it holds every ruling, the vanilla mechanism with its SOURCE lines, and the stacking
arithmetic the owner already accepted. Do not re-derive it and do not reopen it.

⚠️ **A parallel brief is live.** `09_TRAIN_HUB_DISTRIBUTION_high.md` runs at the same time on a
**disjoint file set**. You own `20_TrainHub.lua`; it owns `10_TrainFloor.lua` and
`40_TrainDistribution.lua` and must never touch yours. The Scope section below is a hard fence, not
a preference. `metadata.lua` is the one file you both write: re-read it immediately before each
write, and commit with a pathspec.

## Authority

- ⚖️ **Owner, 2026-09-26: build it.** OI-30 is answered. Build 5 closed on 2026-09-26
  (`reports/TRAIN_HUB_BUILDTRACK_20260925.md`), so `20_TrainHub.lua` is free.
- ⚖️ **Owner, 2026-09-25, all of spec §4.10.** **One** upgrade, not two — *"since I might do some
  other upgrades and I don't want to burn multiple slots on that"* — using all three of its modifier
  slots. The hub is included: *"give a 100% upgrade to the hub as well"*. Its five numbered rulings
  bind: once per colony, vanilla on power, re-buyable after demolition, no tech, 20 Metals +
  20 Concrete.
- ⚖️ **Owner, 2026-09-25, on the stacked totals** (small station 180 with Expanded Warehousing, a
  train 126 with both cargo techs): *"those numbers look good to me as boosts without going
  overboard on release"*. Vanilla's additive-then-multiply arithmetic stands; do not try to make
  percentages multiply.
- `FIX_POLICY` §0 (content-mod risk standard) and §1's technique ranking apply. Both bans bind.
- Testing depth (owner, 2026-09-19): a design pass gets a **smoke test only**. The full prediction
  battery runs once, on the final build.

## End state

1. **One upgrade on the hub's building template**, three modifier slots, each targeting `city`:

   | slot | label | modifier | effect |
   |---|---|---|---|
   | 1 | `Station` | `max_storage_per_resource` +100% | small 60→120, big 120→240, hub 240→480 |
   | 2 | `Train` | `max_shared_storage` +100% | 42→84 |
   | 3 | `Train` | `max_colonists_to_transport` +100% | 12→24 |

   Cost `upgrade1_upgrade_cost_Metals = 20000` and `…_Concrete = 20000`. The label choice is
   load-bearing and already reasoned in §4.10: `Station`, not `StationSmall`/`StationBig`, because
   the hub joins the `Station` class label itself and the split labels would leave it out. Verify
   that join still holds in `SMROptInTrainHubBase:AddToCityLabels` with `grep -n` before relying on it.
2. **Unlocked from the start, with no tech touched.** Our own Lua calls `UIColony:UnlockUpgrade`;
   the tech tree is not edited (owner ruling 4: 1.1.x rebalances techs frequently).
3. **Once per colony.** A second hub reads the upgrade as already spent — the panel asks the
   building's `IsUpgradeUnlocked` / `HasUpgrade`, which the hub class owns
   (`XDef/sectionUpgrades.generated.lua`, re-derive the lines). Two hubs must never give +200%.
4. **Re-buyable after the owning hub is demolished**, with no automatic transfer. Vanilla's
   `StopUpgradeModifiers` from `Building:Done` already removes the modifiers; confirm it, don't
   reimplement it.
5. **Power stays vanilla.** The bonus holds while the hub stands, working or not. Only demolition or
   the player's own `ToggleUpgradeOnOff` removes it.
6. **Nothing in the hub treats 240 as a constant.** Sweep `20_TrainHub.lua`, and read-only sweep the
   other hub files, for hard-coded `240000`. The cargo stacks keep their capped 150 look
   (`hub_visual_storage`, owner `ca586d1`); the hub's `OnModifiableValueChanged` is a combined
   method, so vanilla's live resize must still run through it.
7. **The upgrade id joins the persisted-name inventory** in `FIX_POLICY` §"The persisted-name
   inventory", with its kind, writer and reader. It persists in `upgrades_built` and the colony's
   unlock list. This is expected and authorised by §4.10 — it is not a reason to stop.
8. **Desk smoke.** A `capacity_smoke.py` beside the existing suites covering: the three modifiers
   applied and removed; a live station resizing through `OnModifiableValueChanged`; a second hub
   refused; demolition releasing; toggle off and on; the over-capacity drop (demand goes to 0, no
   stock lost). A fix invalidates its own tests — rerun the whole existing suite
   (`buildtrack_smoke.py`, `flight_smoke.py`, `move_smoke.py`, `repair_smoke.py`) plus
   `python tools/parsecheck.py`, and preserve every output with its command and HEAD.
9. **The attended smoke with the owner**, about five steps at a time (see below).
10. **Record** in a build report under `docs/agent/reports/`, fold the result into spec §4.10, and
    archive the session log byte-for-byte under a new `docs/archive/train_hub_capacity_<date>/`.
    Then hand back to the orchestrator.

## ⚠️ What your upgrade does to the parallel brief

§4.5's rewrite path `MultiResourceDepotBase:OnModifiableValueChanged` → `UpdateRequestCapacity`
fires on a capacity change and then **rewrites every resource's desired amounts from the dial,
whatever the policy says**. Until now that fired one building at a time, via Expanded Warehousing.
Your upgrade fires it on **every station in the colony at once**, which is a new blast radius for
that path and the thing brief `09` has to survive.

You do not have to solve that for them — they have the same note and test it from the harness. But
**do not suppress or narrow that rewrite** to make your own numbers look tidy: it is existing
measured behaviour (§7.2 P3b, measured live 2026-09-18). If you find yourself wanting to, that is a
report, not a change.

## The template half

The upgrade fields live in `Code/BuildingTemplate/SMROptInTrainHub6.generated.lua`, whose header says
the BuildingTemplate Editor generates it. **The Mod Editor's save is the source of truth**
(the precedent is `f71a3c2`, "the template regenerated by the Mod Editor's save"). Decide the route
yourself and say which you took in the commit message: either ask the owner for one Mod Editor save,
or write the fields and have the owner re-save so the generated bytes and `metadata.lua`'s
`code_hash` agree. Do not leave the tree claiming a hand edit is a generated one.

## The attended smoke, from the owner's seat

Preload every reading into TestKit slots under `tools/SMRTK.md` before launch. **The owner clicks;
they do not type.** A hand-typed console line or a watch measured in real minutes each needs a
stated reason no slot can do it. Use the standing `train_hub_base` fixture and do not save over it
(spec §10 "The standing test save"). Read the console yourself from the newest
`%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-*.log` when the owner says "flushed". The game
cannot turn autosave off: after one, the owner re-presses the armed slot.

1. The upgrade is offered on the hub's card from the start, no tech, at 20 Metals + 20 Concrete.
2. Build it; read a small station, a big station and the hub before and after in one slot dump.
3. Read a train's cargo and passenger capacity before and after.
4. Toggle it off and on; then save, reload and read again.
5. A second hub reads the upgrade as spent; demolish the owner hub and confirm the bonus is gone and
   a hub can buy it again.

Ask the owner whether the boost **feels** right in play — that is the dial worth their time, and
§4.10's numbers are their own accepted figures, not a measured balance result.

## Start

`git log`, `git status`, `git pull --ff-only`. Authored on `d2e3a78`. An empty
`git diff --stat d2e3a78..HEAD -- tools/devmods/train_hub/Code/ docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`
means the code and spec facts above hold; if it is not empty, re-derive every cited line with
`grep -n` before using it. Put the work in the todo tool before the first write, one item per
commit-and-verify unit.

## Scope

**In:** `Code/20_TrainHub.lua`, `Code/BuildingTemplate/SMROptInTrainHub6.generated.lua`, a new
`tests/capacity_smoke.py`, `metadata.lua` (re-read before each write), TestKit slots, the sitting,
`FIX_POLICY`'s inventory row, spec §4.10, your own report.

**Out:** `Code/10_TrainFloor.lua`, `Code/40_TrainDistribution.lua` and anything in the distribution
centre (spec §4.8/§4.9) — brief `09` owns all of it and is running now. Also out: a second or third
hub upgrade, techs, Module A, routing, the shipping `Code/` tree (this stays a dev mod), and the
project-wide `FIX_POLICY` §8 both-configuration ship test, which is owed for the whole hub and is
not this brief's to discharge.

## Stops

- Three modifier slots cannot carry all three effects, or the `Station` label does not in fact
  include the hub: report the read before designing around it.
- "Once per colony" cannot be expressed through the hub class's own `IsUpgradeUnlocked` /
  `HasUpgrade` answers without a new colony-level persisted name: report before writing one.
- The hub's combined `OnModifiableValueChanged` cannot pass vanilla's resize through while keeping
  the 150 cargo look: report both behaviours you measured.

## Do not claim

- ⛔ Not "the capacity upgrade is balanced". §4.10's figures are the owner's accepted design numbers.
  Claim the modifiers applied, the values measured, and the owner's reaction in that colony.
- ⛔ Not "it survives removal cleanly". §4.10 already records that removing the mod leaves the
  modifiers to vanilla's `SavegameFixups.RemoveLeakedUpgradeModifiers`, once per save. State that
  limit; it is the hub's general uninstall problem, not yours to solve.
- ⛔ Not a ship-test pass. No both-configuration run is in scope.

## Lifecycle

Done when the attended smoke is recorded and spec §4.10 carries the result. The orchestrator then
parks or deletes this brief and moves its row in `README.md` in one commit (owner, 2026-09-21).
Build agents do not delete or move their own brief.
