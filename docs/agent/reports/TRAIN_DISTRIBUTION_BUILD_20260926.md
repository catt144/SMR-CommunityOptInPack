# Distribution first pass — capacity-share stop

Brief: `prompts/Train_Hub_Project/09_TRAIN_HUB_DISTRIBUTION_high.md`.
Tested base: `ceb568ffc6edf400f59d0c5f74548a085b268a2c` plus this commit's diff.
Executed model: GPT-6, as identified in the session instructions; no more specific
executed model identifier was exposed in the transcript. No subagents.

## Result

**MEASURED, desk only:** the claim-only mechanism does not deliver the requested
drain-to-floor behavior. The brief's first stop applies before building the feature.
No attended smoke ran and no game session log was created. The distribution centre
remains unbuilt; the brief remains live.

The independent `Status` defect is fixed: `print_view` uses `const.ResourceScale`.
The harness now gives the archived vanilla body its file-local scale and leaves the
nonexistent global undefined, so it can no longer conceal this defect.

## Stop witness

`python tools/devmods/train_hub/tests/distribution_smoke.py` [RAN 2026-09-26,
log `docs/archive/train_distribution_20260926/distribution_smoke.log`] runs the
archived **1.1.1.405907** `Lua/Units/Train.lua` bodies with request doubles.
It installs the measured export drone desired amounts, configures an export floor,
loads, delivers the cargo, returns empty and evaluates again. The destination is a
capacity-adjusted station double, not the hub implementation.

| Source capacity | Sink capacity | Initial source/sink stock | Floor | Source after delivery | Next load |
|---|---|---|---|---|---|
| 100 | 100 | 80 / 0 | 20 | 60 | 0 |
| 100 | 400 | 80 / 0 | 20 | 36 | 0 |

**SOURCE:** archived build 1.1.1.405907, `Lua/Units/Train.lua:921-952`:
`needed` is the source's capacity share; the load is bounded by
`available - needed` and the destination's capacity-share deficit.
The stock claim reduces `available`, but does not reduce `needed`.

**INFERRED:** with equal capacities and total stock 80, the source share is 40.
Even removing the floor claim cannot make the enabled source drain below 40 by this
path (the harness's vanilla control measures exactly 40). A claim of 20 makes the
effective retained amount 60. Merely adjusting the claim cannot reach the requested
20 in that fixture. The larger sink reduces the share to 16, but the current claim
still leaves 36. Raising drone desired amounts does not change these shares.

This is a stop on the specified claim-only mechanism, not proof that every chained
wrapper or input adaptation is impossible. No allocation takeover was written.

## Decision and cost

**Proposed, not authorised:** permit configured resources to use their mode and
slider as train allocation targets instead of capacity parity. Keep vanilla behavior
for unconfigured resources and stations. Prefer a narrow chained intervention if
one works; do not presume a copied `TransferCargo` body is necessary.

This expands ownership from availability claims to allocation: source retention,
destination targets, existing incoming reservations and hub refusal must agree.
Changing effective capacity or enabled state only during train evaluation is another
candidate, but changes route totals and the forbidden-resource branch; it is not an
equivalent claim-only implementation. Either approach needs explicit allocation
tests and re-verification against future train-body changes. A full body replacement,
if ultimately necessary, would additionally carry the policy's source-copy upkeep.

Owner decision: OI-31. Alternative: retain proportional balancing, accepting that the
slider is only a reserve and export may stop above it; that changes the requested
product and is not adopted here.

## Verification and handback

**MEASURED:** existing `tests/*smoke.py` scripts plus parsecheck and the wrap-target
check produced 10 passes and 1 failure. Command, HEAD and unmodified captured output
are in `docs/archive/train_distribution_20260926/`; `verification.txt` reconciles
every member and terminal exit. Distribution, art, construction, dwell, flight,
look, movement, repair, parsecheck and wrap-target checks passed.

**MEASURED, outside this brief:** `traffic_smoke.py` failed with `-10800 != 0` in
its arrival assertions. Its harness and `20_TrainHub.lua` match HEAD; it does not load
the changed distribution implementation or harness. See `traffic_smoke.log` and
`verification.txt`. Route to the hub/orchestrator; no fenced file was changed.

No UI, saved field, claims save guard, metadata or TestKit slots were added. There is
therefore no hub-header inventory line owed. After the owner settles allocation,
resume brief 09: hub-owned state, station rows, mode behavior, rewrite/alias and
network-capacity smoke, save safety, then the attended sitting. Native floor binding,
coverage, hub refusal and save/reload remain untested. The existing inbound-cargo
limitation remains reproduced by the distribution harness and needs that design too.
The parallel Capacity Network Upgrade and the both-configuration ship test are not
discharged by this work.
