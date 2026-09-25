# Distribution mechanism prototype — 2026-09-25

Scope: brief `Train_Hub_Project/07_DISTRIBUTION_PROTOTYPE_high.md`, invoked by the
owner. Executed model: GPT-6 (the identity exposed in this transcript; no more
specific model identifier was supplied). This is a partial mechanism experiment,
not permission to build the distribution-centre design.

**MEASURED, offline only:** the existing transient floor path ran against the
archived train balancer with request doubles. Claims changed the target read
inside the call, left actual stock alone until vanilla moved cargo, and released
afterward. **INFERRED:** this supports trying the native mechanism; it does not
establish that native requests accept the claim or that drones behave as intended.

**SOURCE:** the delivered `40_TrainDistribution.lua` has `Set`, `Status`, and
`Reset`. Configuration is local to the loaded code, per station/resource, and its
slider is a percentage of live capacity. It rejects hub/reserve stations. The
train wrapper claims configured members of the evaluated route, including
destinations when a train is elsewhere. The drone desired amounts are sampled
synchronously and restored; they are **not installed for drone scheduling**.

**SOURCE, scope conflict:** the brief says “nothing persists” and “no save hooks”,
while spec §4.8 identifies requests as saved state and requires save cleanup for
standing claims. Keeping changed native desired amounts or claims between calls
does not meet that constraint. No such baseline or `transport_policy` write was
left active. OI-29 asks whether a disposable session without saving is acceptable.
Until the owner answers, baseline/drone and `accept` work remains blocked. This is
an implementation constraint, not a revision of the owner's design.

## Evidence and answers

**MEASURED, offline:** command
`python tools/devmods/train_hub/tests/distribution_smoke.py`, source/build and
HEAD printed by the command; receipt
`docs/archive/train_distribution_20260925/offline.log`. The test loads exact
delimited archived `Train:TransferCargo`, `LoadResourceForStation`, and `UnloadAll`
bodies, with explicit doubles for requests, objects and route iteration. It never
loads the fenced hub/drone files. The deliberate failure messages exercise cleanup.

| Question | Answer and limit |
|---|---|
| Does a transient claim create different views? | **MEASURED, offline:** with supply actual/target 80, holding 20 yields target 60 inside the call and restores it afterward. `Status` samples real requests when run in game, but that native run is **unperformed**. |
| Do drones respond to the baseline? | **INFERRED, untested:** cannot be answered by this harness. Baseline samples restore before drones can schedule. Needs an authorized lasting baseline, a working local controller, idle drones, local excess for export and a real consumer for import. |
| Does `transport_policy = "accept"` affect drones? | **SOURCE / untested:** archived `Station.lua:974-983` translates it to supply desired 0 / demand desired capacity when `SetDesiredAmount` actually runs. The prototype does not set that policy. Needs a consumer and a controlled native comparison. |

**MEASURED, offline:** these are named assertions in the same command/receipt,
using equal station capacities of 100 and resource units rather than raw scale:

| Fixture | Observed result |
|---|---|
| Vanilla source 80 / destination 0 | Source 40; cargo 40. |
| Existing transient supply floor 20, source 80 / destination 0 | Source 60; cargo 20; claim released. It does not drain to 20. |
| Destination configured export | New cargo admission blocked in the modeled request path, including when the train is at another station. |
| Source configured import | No new outgoing load in the modeled request path. |
| Empty destination configured import, source 80 | Cargo 40, not a fill to capacity 100. |
| Empty destination balanced to 20%, source 80 | Cargo 20; the train's own demand reservation survives prototype cleanup. |
| Export floor 20, initially empty source, already reserved inbound cargo 10 | Inbound 10 unloads, then 5 reloads; source ends at 5. The pre-call claim does not cover new stock. |

**SOURCE:** all new game citations here use
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src` (installed build identity
checked with `python tools/doccheck.py --emit-fingerprint` on 2026-09-25).
`Lua/Units/Train.lua:921-951` subtracts a capacity share after reading available
supply; `:944-952` limits destination load by its share and demand target.
`Lua/Units/Train.lua:787-825` credits an existing reservation when unloading;
`TransferCargo` calls that unload at `:872`. The wrapper does not cancel existing
assignments or recompute its supply claim after that unload.

**INFERRED:** the simple claim envelope is insufficient for the entire mode table.
It can hide availability but cannot make the vanilla balancer drain to a floor or
fill every importer. Existing cargo also needs a separate design. No scheduler,
unload, hub-state or design workaround was introduced.

**MEASURED, offline:** assertions also cover rejected claims, genuine runtime
failure cleanup, nil return positions, another hauler's reservations, the existing
standing-reserve helper, invalid input, resource disable, and capacity-relative
slider recalculation. The no-cargo native fixtures pass `train_inbound=true` to
keep vanilla's no-work return away from `#boarding_colonists` on nil in stock Lua;
the engine's nil semantics are outside this harness.

## Rewrite paths and registration

**SOURCE:** §4.5's rewrite paths cannot overwrite the prototype's local percentage.
Every call resolves the current requests and capacity again. It deliberately does
not keep baseline desired values installed, so it does not solve reapplication
after the vanilla rewrites. **SOURCE:** no request-registration hook was added;
§4.6's captured alias was avoided, not repaired or validated for a future feature.

**MEASURED, offline:** the new `ModItemCode` is in `items.lua`, following the
registration mechanism of `6574794`. The test's `--regen-code` option regenerates
the explicit metadata code entries from that source, preserving generated
preset/entity entries. The editor still owns its hash and generated data. Normal
test mode fails on registration drift; run it after any import/editor save.
The pre-existing metadata version/save/hash changes are outside this task.

## Owner console script — next available game session

**INFERRED, experiment instructions:** use a test colony with a vanilla spoke
connected to the hub and a working cargo train. Select the vanilla spoke, not the
hub. Stock and demand must allow a cargo movement. Covered and uncovered spokes
can both test train-side request numbers; only a covered spoke with a local
producer/consumer can later test drone responses. All console calls below are
**[NEVER RUN in game]**; their API paths were exercised in the offline harness.

1. At your next normal restart, load the updated dev mod. After an editor import,
   confirm the `40_TrainDistribution` code item remains. Select the spoke and type
   `SMROptInTrainDistribution.Set(SelectedObj, "Metals", "export", 20)`.
2. Type `SMROptInTrainDistribution.Status(SelectedObj, "Metals")`. `CURRENT` is what
   drones currently see; `DRONE SAMPLE` is the proposed baseline, restored at once;
   `TRAIN SAMPLE` is the claimed view. With unclaimed stock above the floor, train
   supply target should be lower; export train demand target should be zero. Equal
   targets may mean no available stock or a refused native claim, not success.
3. Let a train call at either end, then repeat `Status`. The `native calls` value
   should increase and current targets should not retain the prototype's claim.
   Actual stock and genuine cargo reservations may change. No call increase means
   the train path was not exercised. Existing inbound cargo can still unload.
4. Type `SMROptInTrainDistribution.Set(SelectedObj, "Metals", "import", 20)`, then
   `Status` as above; repeat with `"balanced"`. Import's sampled supply target
   should be zero; balanced caps sampled demand room at its slider. Observe train
   activity, but do not expect exact filling or draining from the capacity-share
   balancer. Do not interpret unchanged drone behaviour as a baseline test: no
   lasting drone baseline or `accept` policy was installed.
5. Type `SMROptInTrainDistribution.Reset()` to disarm all entries. Keep the log and
   note which station had local drone coverage. Drone-baseline and `accept` tests
   remain for the OI-29 decision and a consumer-present fixture.

**SOURCE, lifecycle:** the brief remains live for its orchestrator to park/delete.
No game sitting was taken. Native claim semantics and all drone observations remain
open; this report does not declare the distribution centre working or feasible.
The native run is routed to fix-pack checklist ck218; OI-29 remains this mod's
baseline-scope decision. **MEASURED:** the offline command, `python tools/parsecheck.py`,
`git diff --check`, and `python tools/doccheck.py` passed; the fix-pack checklist
routing also passed that repository's doccheck after adding its required local Home.
