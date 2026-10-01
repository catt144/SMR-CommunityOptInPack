# Brief 29: the hub's long-title fix and the depot's cost proposal (2026-10-01)

Brief: `docs/agent/prompts/Train_Hub_Project/29_HUB_TITLE_AND_DEPOT_COST_medium.md`. Started at
`aabbad1`; `git pull` printed "Already up to date". Build **25579348** (`python tools/doccheck.py
--emit-fingerprint`: "installed game build 25579348"). Source cited from the archived tree
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343` (Steam `25579348`, per that archive's README row).
Executed model: Claude Opus 5.5 (`claude-opus-5-5`), from the session's system prompt.

## Commits

| sha | what |
|---|---|
| `b551930` | The hub's `fit_title` gets the depot's true ceiling and its 2-unit guard. The hub's `distribution_ui_smoke.py` runs both `fit_title`s side by side. |
| this commit | This report and the brief's row in `Train_Hub_Project/README.md`. |

## 1. The hub's long-title fix (done; desk-verified only)

**The port.** `tools/devmods/train_hub/Code/45_TrainDistributionUI.lua` gets `FIT_SLACK = 2` and
`mul_div_ceil` (`MulDivRound`, then up by one if it rounded down). Both are byte-for-byte the depot's from
`1122115`. The two `math.ceil(x * 1000 / s)` lines in `fit_title` become `mul_div_ceil(x, 1000, s) +
FIT_SLACK`. No caller changed: `update_row` still calls `fit_title(row.idSectionTitle)`. Stop 1 did not fire.

**Shape: a matching copy, not a shared helper.** The two dev mods are independent. The depot reads
nothing of the hub, and the hub reads the depot only through `rawget(_G, "SMRElevatorDepotDev")`. A shared
helper would tie one mod's load order to the other's for eight lines. Instead, the hub smoke checks that
the two copies stay equal.

**The smoke.** `distribution_ui_smoke.py` has a new `long_title_fit()`. It takes the hub's slice and the
depot's slice (`FIT_SLACK` … end of `fit_title`, read-only from each file) and refuses a bare `/` or
`//` in either. It loads both into one environment where `Max`/`MulDivRound` accept integers only, as
the engine's do (EF-116). It runs both on the depot smoke's mock titles: four titles × scales 800..2200
in steps of 50, so 116 cases. Each box is scaled to pixels the way XWindow does it (ScaleXY per value,
truncating). For every case it requires that the hub's and the depot's min width, max width and max
height are equal, and that the hub's box holds two lines and the widest word. The title-height
assertion in the existing native-wrap block moves from 48 to 50 (44 + `FIT_SLACK` 2 + padding 4).

Commands, run from `tools/devmods/train_hub/tests/` (final runs at the commit's tree):

- `python distribution_ui_smoke.py`: all five PASS lines; the new one prints
  `PASS long titles: the hub fit_title gives the Elevator Depot answers and holds two lines and the
  widest word at every scale 800..2200 ( 116 cases, integer-only helpers, no bare /)`.
- **Control, the check can fail:** with the new hub code but the floor put back (`q * c > a * b then
  q = q - 1`, `FIT_SLACK` 0), `python -c "import distribution_ui_smoke as m; m.long_title_fit()"` raised
  `hub and depot differ at scale 800: Exotic Minerals · Not accepted (hub 154/76, depot 154/78)`. The
  HEAD hub file also fails the full smoke, at the title-height assertion (48 ≠ 50). The working file
  was restored after each control (`git diff --stat` 17+/2-, as before).
- Every hub smoke: `for f in *_smoke.py; do python $f; echo $?; done` printed exit **0** for all 25
  (`art_spec` … `train_spawn`).
- `python bay_fixes_suite.py --output <scratch>` exits **1** with `"traffic_baseline_matches": false`.
  With the HEAD hub file restored it exits **1** with the same key, so this is not caused by the
  port. The suite does not read `45_TrainDistributionUI.lua` (`grep -c` 0). The failure was there
  before this brief and is not investigated here.

**Owed, outside this brief's scope:** `tools/devmods/elevator_station/tests/wiring_smoke.py` §10b
asserts that the hub *still has* the floor (`hub_fit.count(' / ') == 2`, then `hub_short_cases > 0`).
After `b551930` it fails at the first of those: `AssertionError: the hub fit_title has two
divisions`. It is a depot file, and brief `28` is live in the depot's files, so it was not touched. The
fix is to drop or invert §10b's hub assertions, because the hub smoke now carries the comparison.
Route it to whichever brief next holds the depot's tests.

**Not claimed:** any in-game look. OI-38 carries that look.

## 2. The depot's construction cost (proposal; the owner's yes is owed)

### What vanilla charges (build 25579348, archived 1.1.1.406343)

- **Elevator template** `Data/BuildingTemplate/Elevator.lua`: `construction_cost_Concrete = 10000`,
  `construction_cost_Metals = 5000`, `construction_cost_MachineParts = 2000` (`:9-11`), so **10
  Concrete, 5 Metals, 2 Machine Parts**; `build_points = 20000` (`:5`); `electricity_consumption =
  5000` (`:21`); maintenance Machine Parts (`:29`); `only_build_on_snapped_locations`, snap target
  `ElevatorPassage` (`:31`, `:40`), so it needs an Underground Entrance site.
- **That price buys both sides.** `ElevatorBase:PlaceConstructionSite` places one site per map in a
  single construction group (`Lua/Buildings/Elevator.lua:762-784`). Only the group leader gathers
  resources (`Lua/Buildings/ConstructionSite.lua:701-702`, "only main guy from the group distributes
  requests"). The leader's cost is `construction_cost_multiplier` (default 100, "groups cost exactly as
  much as 1 element") × the template cost (`ConstructionSite.lua:2499`, `:2548-2550`). One side's
  power is zeroed so the pair draws 5 kW once (`Elevator.lua:717-719`).
- For comparison, the stations the depot is built on: **StationSmall** 20 Concrete, 10 Metals, 5
  Machine Parts, 2000 build points (`Data/BuildingTemplate/StationSmall.lua:5-9`); **StationBig** 50
  / 30 / 10 (`StationBig.lua:7-9`).
- **The depot today** is `instant_build = true`, `build_points = 1000`, with no cost and 0 power
  (`tools/devmods/elevator_station/Code/BuildingTemplate/SMROptInElevatorDepotDev.generated.lua:11-12`,
  `:28`).

### Proposed, per half (template units ×1000)

| field | per half | the pair | vanilla elevator (both sides) |
|---|---|---|---|
| `construction_cost_Concrete` | **5000** (5) | 10 | 10 |
| `construction_cost_Metals` | **2000** (2) | 4 | 5 |
| `construction_cost_MachineParts` | **1000** (1) | 2 | 2 |
| `build_points` | **10000**, with `instant_build` off | 20000 | 20000 |

**The reasons.**

- **Each half is below the elevator in every resource**, as the owner ruled. Each half is also below
  vanilla's elevator side by side, since vanilla pays one price for both sides.
- **The pair costs no more than one elevator** (10/4/2 against 10/5/2). The depot does less. It is
  cargo only: no colonists, vehicles, power or water pass through, while vanilla's elevator does all
  four (the template's description, `Elevator.lua` template `:14`; the grid elements,
  `Lua/Buildings/Elevator.lua:739-760`). It moves 42 units an hour in one cabin, while
  vanilla's elevator is a shared depot that both maps' drones reach at once. So a pair should not
  cost more than the elevator.
- **It is not much cheaper either.** The depot needs no Underground Entrance: it is sited freely on
  both maps. One pair per colony (build-once per map) and the underground unlock are its real gates.
  Halving the elevator, with Metals rounded down, keeps it a small, early purchase without making it
  free.
- **Build time instead of instant build.** 10000 points per half gives 20000 for the pair, the
  elevator's figure. Drones requested scale with build points (`ConstructionSite.lua:727`, 10 max),
  so each half is a short, normal build. If the owner wants the depot to stay instant, drop this row:
  the resources stand without it.
- **Worth the owner's eye:** each half is also a train station, and at 5/2/1 it costs a quarter of
  `StationSmall` (20/10/5). Build-once per map caps any use of the depot as a cheap station at one per
  map, so this is not proposed as a reason to raise the price.

**Alternative, if the owner wants the pair to cost more than one elevator:** 7 / 3 / 1 per half (pair
14 / 6 / 2). That is still below the elevator per half.

Not written into the template. Brief `28` holds the depot's Mod Editor session. After the owner's
yes, the numbers go to whichever brief next saves the depot. Power and maintenance are not part of
this proposal: the brief asks for construction cost only. The depot draws 0 kW today.

## What I did not do

- No depot file touched (`items.lua` and `metadata.lua` show as modified in the tree; those are brief
  `28`'s, unstaged, untouched). That includes `wiring_smoke.py` §10b, owed above.
- No in-game check of the hub title (OI-38).
- No template write of the cost; no power, maintenance or tech-gate proposal.
- No investigation of `bay_fixes_suite.py`'s `traffic_baseline_matches: false`, which was already
  failing at HEAD.
- No STATE, checklist or bug-library edit. Nothing in this brief makes an engine fact that is not
  already filed: EF-116 covers the division.
