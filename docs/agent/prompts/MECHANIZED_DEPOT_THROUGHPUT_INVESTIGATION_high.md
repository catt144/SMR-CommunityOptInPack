# Mechanized depot throughput: can a module make it faster without changing its look?

**Fire with:** `task docs/agent/prompts/MECHANIZED_DEPOT_THROUGHPUT_INVESTIGATION_high.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Reasoning: high (engine reading behind a design
decision; the size answer decides whether this joins the launch set).

## Authority and outcome

The owner, 2026-10-03, during the pre-launch soak: a vanilla Mechanized Depot (the big crane depot)
holding 3,667 Machine Parts at Desired Amount 100, in range of a drone hub and of a train station
whose Machine Parts row is **Export**, drains into the station, but only a couple of cubes at a time
from its output pad. The owner watched it work. **It is a vanilla throughput limit, not a block
by this mod.** Do not re-investigate that.

The owner's idea for a new opt-in module: **keep the depot's look exactly the same**, and give the
crane and the platforms a hidden larger capacity, so it is smoother, faster and more impactful.
The pads still draw their normal handful of cubes, and the crane animation is unchanged. The extra
amount lives in the logic only.

Outcome: a report the owner can decide from, covering feasibility, the mechanism and the size. It
should answer:

1. **Where the limit lives.** Find the input/output buffer capacities, the crane's batch size
   and cycle timing, and how drones see the pads' supply and demand requests.
2. **Whether the pad cubes are drawn per unit of stock.** If they are, say how to cap the drawing
   at the vanilla count while the logic holds more, and how hard that is.
3. **Whether the change can be made per depot and reversibly.** Use class constants, per-object
   overrides or a wrapped method; state which, without replacing vanilla code wholesale. Check
   it against `FIX_POLICY`'s wrap and toggle rules.
4. **What happens when the module is switched OFF** with an oversized pad or crane load. Check
   whether the excess returns to main storage or simply drains. Compare the owner's ruling that
   stock above a reduced capacity is retained (train battery B4, `TRAIN_FINAL_BATTERY_20261002.md`,
   grep `over-capacity`).
5. **Save safety.** List what would persist and whether any new persisted name is needed (see the
   persisted-name inventory in `FIX_POLICY`).
6. **Shape and size.** Weigh a fixed boost against a dial (×2/×5/×10, like `D09` DroneStatDials).
   Estimate the build in sessions, and name the risks that could make it larger.
7. **Interactions.** Cover this mod's StationRows Export pairing (34b's FindTask filter), shuttles,
   and the fix pack, if it touches mechanized depots.

## Evidence

- `EF-102` (`docs/agent/facts/EF-102.md`): `MechanizedDepot` is **not** a `StorageDepot`. Its
  parents are `Building, StockpileController, ResourceStockpileBase, ElectricityConsumer` at
  `StorageDepot.lua:834`, with ~12 shipped `MechanizedDepot*` subclasses and its own
  `storable_resources`. That was read on 1.1.0; re-read it on the current build.
- Current game build: 1.1.1.406343. Cite every game source line with the build it was read on,
  from that build's archived tree (`CLAUDE.md`).
- Further records: `docs/agent/facts/INDEX.md`, `docs/agent/bugs/INDEX.md`.

## Method

`git log --oneline -3` and `git pull` first; authored at `e04735a`. Keep a work list (the todo tool
if the session has one, else in the report). The route is yours. A cheap in-game measurement beats
a derived figure: if a fact can be read with one console line in a loaded save, say so and hand the
owner paste-ready text rather than deriving it. Prove absence with a grep and count the presence
side. References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md`, `docs/agent/WORKFLOW.md`; skills
`smr-bug-library` (file any new engine fact) and `doc-editing`.

## Scope

In: reading, measuring and reporting, plus filing engine facts you establish. Out: building the
module or editing `Code/`. Report anything outside the question without editing it.

## Stops

1. The look cannot be kept: the pad visuals or crane are bound to the stock amount in a way a
   module cannot cap. Report that, with the evidence and the nearest workable alternative.
2. The change needs vanilla code replaced wholesale, or a new persisted name. Report it as the
   owner's decision, and do not design around it.

## Claim limits

A desk reading supports "feasible as designed"; it does not support "works in play". Mark every
throughput figure as derived or measured.

## Deliverable and lifecycle

Write the report to `docs/agent/reports/MECHANIZED_DEPOT_THROUGHPUT_<date>.md`, commit it, and give
the owner a short verdict: feasible or not, the mechanism, the size, and your recommendation on
launch versus post-launch. This is a one-off: delete this prompt and its row in
`docs/agent/prompts/README.md` in the same commit as the report.
