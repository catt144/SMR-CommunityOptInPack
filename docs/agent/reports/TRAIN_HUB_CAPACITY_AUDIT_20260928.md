# Brief 14 — build-tier audit of the two low-effort builds of 2026-09-28

Brief `prompts/Train_Hub_Project/14_AUDIT_LOW_EFFORT_BUILDS_high.md`, fired at `4ac2685`. Executed
model: Claude Fable 5.1 (`claude-fable-5-1`). The capacity change was built on Opus and the guard on
Sonnet. Source reads were made on 1.1.1.405907, from `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`.
A desk PASS means the mocked vanilla bodies agree. It does not mean the change works in the game.

## 1. Capacity salvage/rebuild — **PASS WITH FIXES**, verified in the worktree, NOT merged

Branch `worktree-agent-af033497203ef0c8a`. `37b9e30` is the builder's change committed unchanged.
`0ec0631` holds the audit fixes. **Not merged:** the merge waits for the owner to say no sitting is
running, because the game reads the dev mod from `main` through a junction.

| check | command | exit / result |
|---|---|---|
| desk test, builder's code | `python tools/devmods/train_hub/tests/capacity_smoke.py` at `37b9e30` | 0, PASS |
| builder's six mutations (salvage stop, rebuild transfer, off-state carry, ruins guard, position match, load fixup) | scripted replace, run, restore | each 1 |
| desk test after the fixes | same, at `0ec0631` | 0, PASS |
| eight mutations (the six plus ruins toggle guard and map match) | same script | each 1 |
| drift claim: `capacity_smoke.py` unchanged between `a0768c5` and `main`, and `20_TrainHub.lua` changed only by `HealCargoColumns` and its call | `git diff a0768c5 main --stat -- tools/devmods/train_hub/` and the file diff | holds |
| clean carry onto `main` | `git merge-tree --write-tree main worktree-agent-af033497203ef0c8a` | 0 |
| merged tree | throwaway detached merge `e74e0bc`: `capacity_smoke.py` and all 16 `tests/*_smoke.py` | all 0; worktree removed |
| no new persisted name; no SMRFixPack reference | the test's static gates (writes only `upgrade_on_off_state`) and a read of the diff | holds |
| builder's citations | `Building.lua:910-919`, `:1788-1810`; `ConstructionSite.lua:1724-1745`; `BaseBuilding.lua:2`; `classes.lua:1847` | all hold |

**Defect fixed (ruling b, "keeping an off toggle off").** A Ctrl+click on the upgrade from a spent
hub B broadcasts `enable = not B.upgrade_on_off_state[id]`, which is true, to every hub of the class
(`sectionUpgrades.generated.lua:69-92`). `BroadcastAction` filters on `GetUIInteractionState`
(`BaseBuilding.lua:541-552`), and `Destroy` never clears it. So ruins left OFF flipped to ON. The
modifier guard kept the bonus off, but the rebuild then came back ON. Fix: the hub's own
`ToggleUpgradeOnOff` refuses this upgrade while `destroyed` and otherwise passes through to
`Building.ToggleUpgradeOnOff`.

**Hardening (judgment call).** The rebuild's ruins match now also requires the same map.
`UIColony.labels` spans every map, and the Infopanel copy path (`Infopanel.lua:501-510`) calls
`ApplyCopyParams` on a fresh placement.

**Weighed, no change needed:**
- **Rebuild window.** The ruins hold the claim until `ConstructionSite:Complete` runs
  `ApplyCopyParams` (`:1737`) and then `DoneObject`s them (`:1744`). A cancelled rebuild leaves the
  ruins holding it.
- **Second hub while ruins stand.** Ruins keep the `Station` label until `Done`
  (`CityObject.lua:35-38`), so a second hub is refused.
- **Once per colony.** The ruins' `upgrades_built` is cleared before the new hub's `ApplyUpgrade`,
  so the upgrade is never held twice or doubled twice. `ApplyUpgrade` charges nothing.
- **Destroyed rather than salvaged.** `DestroyBuildingImmediate` reaches the same `OnDemolish`
  (`Building.lua:1464-1489`; countdown 0 in `Demolishable.lua:90-133`). The hub's meteor guard
  already prevents meteor destruction.
- **Save/load.**
  - Owner on or off: vanilla state.
  - Ruins: the load fixup turns the modifiers off again, which is idempotent (`Modifiers.lua:321-324`).
  - Mid-rebuild: the site keeps `rebuild` and `copy_params`.
- **Ruins without `orig_state`.** They get no `ApplyCopyParams` (nil `copy_params`), so the claim is
  released at `Done`. Every hub ruin comes from `Destroy`, which always writes `orig_state`
  (`Building.lua:1602`).

**Not verified:** anything live. Also unverified: the new hub's own 480 capacity, which depends on
the engine applying a label modifier to a later label member, not modelled; `ApplyUpgrade`'s
`UpdateWorking` and `Msg("BuildingUpgraded")` on a hub not yet `GameInit`-ed; and whether
`AdjustBuildPos` keeps the site's x,y equal to the ruins'. The in-game steps are filed as an
addendum to `TRAIN_HUB_CAPACITY_20260926.md`. They correct the train figures for the fixture's
+50% cargo tech (63000/18 base, 105000/30 doubled), and add a Ctrl+click on the off ruins in step 5.

**Slot 6 does not show capacities** (TestKit `a4b122b`). It streams stock, cargo and passenger
count only. Station cap: slot 4. Train caps and the upgrade rows: only `read()`, which is behind
slot 2's fill. A read-only slot for `read()` is needed; it was not added (TestKit out of scope).

## 2. Doc-checker COLLAPSE gate — **PASS WITH FIXES**, on `main`

| check | command | exit / result |
|---|---|---|
| GREEN at HEAD `4ac2685` | `python tools/doccheck.py` | 0; COLLAPSE PASS, 230 files |
| RED on the incident | `git show 7d7d0c2:docs/agent/prompts/Train_Hub_Project/README.md` in place (3,918 B, 0 newlines), then `git checkout --` | 1; COLLAPSE RED |
| file list | `git ls-files "*.md"` against a plain `.md$` filter; `.MD`/`.markdown` | 230 = 230; 0 |
| builder's floor | size and `wc -l` of every tracked `*.md` | tightest file over 500 B: `docs/agent/support/README.md`, 621 B / 11 lines |
| after the fix | `python tools/doccheck.py` at `3dfe682`; `check_collapse` with an empty list stubbed | 0 GREEN; RED |

**Fix, `3dfe682`:** an empty file list printed "PASS — 0 tracked *.md file(s)", a gate that could
not fail. Zero files read is now RED. The git-did-not-run path keeps its "not checked" line, the
same house pattern as `eol_report`. No threshold moved.

## Outside findings, not edited

- **Pre-existing, 2026-09-26 design.** A Ctrl+click on the upgrade from spent hub B while the live
  owner A is OFF turns A **on**: `enable` is computed from B's empty state. B shows no switch, but
  its broadcast switches the owner. This ruling does not cover it; it needs an owner call.
- **A fresh worktree's doccheck is RED on LOCAL.** `local/README.md` lists the ignored
  `local/retired-modules/`, which exists only in the main checkout. I created it empty in this
  worktree so the pre-commit hook could run.
- **Correction to `0ec0631`'s message.** It cites the ruins' `DoneObject` at
  `ConstructionSite.lua:1739-1742`; the line is `:1744`.
