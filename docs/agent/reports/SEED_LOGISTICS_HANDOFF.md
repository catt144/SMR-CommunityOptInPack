# Seed-logistics handoff — the farm case, the measured mechanism, and the drone-logic designs this house now owns

**Written 2026-08-16, on the owner's ruling, verbatim:**

> *"as much as I want to fix this since it is bug territory in practice even if
> not logic, this I think has to be in opt in as its tinkering with drone logic
> in a way that manipulates it that could have other non bug related
> complications. I want you to hand all of this off to the opt in mod."*

This completes the boundary drawn the day before (*"I am not going to
manipulate drone behavior on a bug fix mod"*). ⇒ **Everything below is THIS
repo's to build, post-launch, one owner decision at a time (FUTURE_IDEAS hard
rule). The fix pack keeps the measurement records (`C47.md`, `C48.md`) and
never grows code for this family.**

---

## 1. The farm issue, whole — what was measured and what it means

Compressed from the fix pack's `agent/bugs/C47.md` + `C48.md`; every number
below is re-emittable from archived logs in that repo (`archive/c47*`,
`c48veg_*`, `c48brake_*`, `c48pair1/2_*`), and every leg's predictions were
committed and pushed before its launch.

**The symptom (owner, organic, 2026-08-15):** an Open Farm on a terraforming
speed-run throws endless *"waiting for Seeds"* popups with voiceover beside a
FULL seeds depot and idle drones. Reproduced attended: 52% of samples stalled,
true buffer zeros, banner witnessed on screen.

**The template half (`C47`)**: Open Farm is the only template of 287 that
tuned its consumption cadence (tick 2.0 h → 0.3 h) without sizing its buffer
(inherits the 5,000 default; its sibling ForestationPlant sets 10,000). Real
but NOT the driver — the buffer only matters because of what follows. C47's
one open thread — the owner's 1x-vs-speed observation — stays in the fix pack
(descending-ladder control designed, unrun).

**The mechanism (`C48`), characterized by elimination — four experiments, the
owner's controls doing the heavy lifting:**

1. **Distance is innocent.** The devs' own scattered-source brake
   (`supply_dist_modifier = 150`, the SurfaceDeposit number) was applied to
   ALL 3,390 live vegetation seed offers, provably rebaked into their requests
   — routing unchanged (the 280-crumb wall stood; zero bulk arrivals).
2. **The demand side is innocent — the owner's diner experiment.** A new
   diner in the worst-traffic cluster was bulk-filled to 100% in seconds by
   five drones from four sources, including a final sub-load top-up ⇒
   `rfWaitToFill` on consumption demand is a one-resource-unit rounding
   guard, not a gate.
3. **Bucket order is innocent.** Hub queue census: veg offers at p1, depot
   supplies mostly p0, a few at p2/p3 — and the higher-bucket depots also
   never won.
4. ⭐⭐⭐ **The pairing itself, witnessed (leg `c48-pairing`, 2026-08-16): a
   log-only wrapper on `TaskRequestHub:FindTask` — the sole Lua seam every
   pairing crosses (`_TaskRequest.lua:72-83`) — recorded 985 supply+demand
   decisions.** Seeds: **non-depot sources won 479 of 479; in 399 (83%) a
   fully-stocked ASSIGNABLE depot sat NEARER to the drone and lost** (specimen:
   41,915 flown for one bush's 280 while a depot offered everything at 5,733).
   Food: same law wherever loose food existed (81% nearer-depot losses among
   non-depot picks); depots served the remaining 46% because loose food RUNS
   OUT. Loose seeds never do.

⇒ **THE RULE: the drone matchmaker treats `rfStorageDepot`-flagged supplies
(stamped on every depot supply AND demand, `StorageDepot.lua:67-68, 466-467`)
as a strict reserve of last resort — any non-depot source wins regardless of
distance; distance only tie-breaks within a class.** Deliberate machinery;
sensible on normal maps (clear the ground, spend from producers, bank
surplus); **degenerates on terraformed maps into "depots never"**, because the
loose seed supply is infinite ⇒ farms crumb-fed 280 at a time (~90% per-trip
capacity waste at carry 3) beside warehouses that even **restock themselves
from the same bushes** (125 of 479 pairings delivered INTO depots — why the
colony's 12.4M hoard grows).

**Facts corrected/established along the way** (filed as fix pack `EF-058/059/
060`): `desired_amount` withholds nothing from the supply side (every depot
offered stored-in-full; it governs rebalancing targets — the owner's reading,
confirmed with data); grown crop hexes offer **Food** through the same
vegetation requesters (the "food off the ground" observation); mega-dome food
venues drain at farm rates (a Diner measured ~48,000/sol) and thrive on bulk
deliveries; drone carry reaches 3 in VANILLA (Artificial Muscles + the Ancient
Artifact upgrade), so the rig's +2 dial reproduces a reachable state.

⚖️ **Status of the case: "bug territory in practice even if not logic"** — the
owner's words and the record's verdict. No fix-pack repair exists or will.

---

## 2. The drone-logic designs this house now owns

All default-OFF, post-launch, un-parked one at a time. Report sections
`DRONE_OVERHAUL_OPTIONS.md` §I/§K hold the engineering detail; this is the map.

⛔⛔ **FIRST, THE OPTION THAT IS DEAD BEFORE ANYONE REACHES FOR IT — the
"just size the buffer" shape (fix pack `C47.md` shape 1). OWNER, 2026-08-16:**
*"I don't think a buffer will fix it because they don't fill the current buffer
as of now."* It is the cheapest-looking fix in the whole family and it is
**refuted by this case's own numbers**: 134 deliveries, not one a full drone
trip, 83.6% exactly 280 against a 3000 capacity, while the farm never reached
the 5000 it already had (minima 305–605 unattended; true zeros attended). A
ceiling you never touch does nothing when raised. ⚠️ And the obvious rebuttal —
that `consumption_max_storage` also sizes the demand REQUEST — dies on §1's own
finding: 479/479 Seeds pairings chose landscape over storage, so a larger ask
buys more 280-crumbs, not bulk trips. **It is a delivery-rate problem wearing a
storage problem's clothes.** The same ruling retired the fix pack's "don't fix
C47 while C48 is open" caution: a buffer that cannot fill cannot mask anything.
⇒ Every design below fixes the TRIP or the CHOICE. None of them fixes the
BUFFER, and that is deliberate.

* **§I — the seeds-only GLEANER** (filed 2026-08-15, unchanged by every twist
  of the case, because it fixes the TRIP, not the choice): after a pickup
  below capacity, top up from nearby same-resource offers before delivering,
  via the vanilla `dont_chain_deliver` seam. ~10× fewer trips for the same
  seed flow. Guards: stop cap, radius, lowest-priority-resources-only.
* **§J — the distance brake: DEAD**, refuted by intervention 2026-08-15. Kept
  as a tombstone so nobody rebuilds it.
* **§K — PAIRING POLICY at the FindTask seam ("depots are the supply
  interface")** — NEW, the owner's two rules from 2026-08-16:
  1. ground/veg crumbs get REDIRECTED to depot demand (banking); if no depot
     has room in range, prefer fallback-to-original over suppression (FindTask
     returns the drone's single best task, so suppression idles the drone) —
     and note the rule is self-limiting anyway: full depots stop the banking
     naturally.
  2. consumers get fed from DEPOT supplies only, with a **mandatory
     starvation fallback** (if no depot supply resolves, serve the original
     pairing — never starve a building to enforce a doctrine).
  Mechanism: wrap `FindTask`, and when a pairing violates policy, re-ask the
  ENGINE'S OWN finders with class constraints — `FindSupplyRequest` /
  `FindDemandRequest` take **`ignore_flags` / `required_flags` straight into
  the C finder** (`_TaskRequest.lua:54-69`), so distance/reachability/claims
  stay the engine's arithmetic. Scoping is one line: `OpenFarmBase` only
  (surgical v1, recommended) vs every `DoesHaveConsumption()` consumer
  (colony-wide doctrine; the data says food already works, so it buys less
  and risks more). Precedent: the D06 core claim gate already wraps this seam
  in this repo.
* **§K-probe — the FLAG-BRAND experiment, the cheap first step**: add
  `rfStorageDepot` to the vegetation requesters themselves ⇒ the matcher's own
  reserve semantics makes bushes co-equal with depots, distance finally
  decides, and the depot beside the farm wins with no wrapper at all. One flag
  per requester, self-propagating through requester churn (measured: the
  population turns over in hours). ⚠️ Unknown C-side special-casing of the
  flag (shuttles, rebalancing, UI) ⇒ MUST run as a staged-copy leg with the
  existing instruments before anyone trusts it.
* **The composition**: gleaner (efficient landscape→depot banking) + §K
  (bulk depot→consumer serving) = the complete economy the owner described.
  Each piece also stands alone.

**Build discipline carried over from the measurement chain:** staged copies of
`C47FARM` only (fix pack `EF-056` autosave pre-copy ritual), predictions
committed and pushed before any launch, arm-script gates (parked instrument
sources live in the fix pack's `docs/agent/prompts/c48-brake/` +
`c48-pairing/` and in git history), byte-identical save contract, and the
flattened-class lesson: **patch every carrier class and prove wiring on live
instances** (fix pack `EF-058`).

## 3. What the fix pack keeps

`C47.md` (the buffer/cadence record + the owner's open speed question and its
designed descending-ladder control) · `C48.md` (the full measurement record) ·
the archived logs · `EF-055..060` · the wave-11 template probe (permanent,
tests no fix). ⛔ No fix-pack code for this family, ever, per the two rulings.
