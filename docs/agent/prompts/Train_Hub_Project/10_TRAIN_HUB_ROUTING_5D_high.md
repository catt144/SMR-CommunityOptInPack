# 5d routing — chained stations obey their rows

**LIVE** (2026-09-27), for a fresh session. The distribution centre is built and has passed live
on every station whose train line reaches the hub (spec §4.8; brief 09, finished and deleted).
This build extends it to the stations the owner's network actually has: **stations chained to the
hub through another station's line.** In the test colony, 6243's only line goes to 2012, and 2012
has its own line to the hub. Big station 2009 has one line to a small station that connects to the
hub, and a second line straight to the hub. Today a train on a line without the hub gets vanilla
behaviour, so those stations ignore their rows.

Read before the first write:
- spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.7, §4.8 (every ruling, including
  the 2026-09-27 block), §5.2–§5.3 and §6 OPTION 5;
- `docs/agent/reports/TRAIN_DISTRIBUTION_PASS2_20260926.md` for the mechanism, the rung table and
  the desk suite you extend.

## Authority

- ⚖️ **Owner, 2026-09-27 (spec §4.8 rulings 1–2):**
  - *"they are all part of the hubs network and it should reach them. The only exception should be
    stations that are not connected to the hub in any way"*;
  - **build 5d routing next.**
- ⚖️ **5d as the spec defines it** (§6 OPTION 5): *cargo routing, not train routing.* Every line
  stays its own linear route with its own trains. A routing layer sends each load toward the next
  station on the path to where it is wanted. **No route-model change**; §5.2's three blockers stay
  untouched.
- ⚖️ **The rest of §4.8 binds unchanged:**
  - per-resource modes; the hub is the holder and the source;
  - Balanced is the hub's pin (over goes back, under is filled);
  - an untouched row is Balanced at vanilla's dial;
  - local drones stay free; a full hub refuses;
  - the save ladder at its lowest working rung, currently rung 2 with one persisted name,
    `SMROptIn_distribution`.

  §4.7's UI is accepted; this build needs no UI change beyond what a chained row's tooltip must
  say.
- `FIX_POLICY` §0, §1's technique ranking and §2 (gated by `tools/harvest_wrap_targets.py --check`)
  apply, and both bans bind. Testing depth is smoke only. **Method: small and rough, in the game
  fast** (owner, 2026-09-20). The owner judges by eye; do not polish ahead of a look.

## What is already there — claims to confirm with one check each

- **Membership is already transitive.** `D.Refresh` in `40_TrainDistribution.lua` walks each hub's
  `HubTrackGraph()` and records an owner hub for every station in it. `D.HubFor` returns it, which
  is why chained stations already show the controls.
- **Enforcement is per stop and needs the hub on the train's line.** `train_view` returns nothing
  unless the hub is among the stops of the current train's line, and `line_has_hub` gates pass 4's
  defaults the same way. The live sign was `D.CallsFor` reading 0 at every chained station (third
  sitting, log receipt under `docs/archive/train_distribution_20260926/sittings/`).
- **The spec's lead, not a prescription:** per-hop forwarding in `TransferCargo`, possibly through
  vanilla's unused `ttPrioShortage` lane (archived 1.1.1.405907 `Lua/Units/Train.lua`, `local
  ttPrioShortage = 2`; re-derive with `grep -n`). The route is yours.

## The design question you answer first

On a line without the hub, which station stands in for it, and how does a load in transit avoid
being pinned where it lands?
- In the owner's shapes, the station on the line that is nearer the hub (2012 for 6243) is the next
  hop. Its own row wants to hold 10, so a forwarded load must pass through it rather than be kept.
- Settle the forwarding rule in a short note at the top of your report: hop choice, transit stock,
  what counts as "wanted", and how Balanced, Export, Import and a full hub read along a chain. Then
  build it.
- **Do not come back for a ruling on a choice the authority above already covers.** Record your
  calls in the commit message.

## End state

1. **A chained station obeys its row through forwarding.**
   - Export and Balanced excess reach the hub hop by hop.
   - Import and Balanced shortfall are filled from the hub hop by hop.
   - An untouched chained row holds vanilla's dial.
   - Stations with no connection to the hub keep vanilla.
2. **Intermediate stations pass loads on and keep their own row's number**, allowing for in-transit
   stock. How much transit stock may sit there is your call; name it.
3. **No new persisted name unless a rung measurably requires it** (§4.8's ladder). Take the lowest
   rung that works and record which rung each part reached, with the measurement that closed the
   rung below.
4. **Desk cases** in the distribution suite, on archived train bodies with the engine's integer
   division (EF-116):
   - the owner's two shapes (a one-hop chain, and a big station with both a chained line and a
     direct one);
   - each mode along a chain;
   - a full hub;
   - a disconnected pair staying vanilla;
   - the existing cases as the control.

   Rerun the whole suite plus `python tools/parsecheck.py` and `harvest_wrap_targets.py --check`,
   preserving outputs with command and HEAD. The known `traffic_smoke` failure (`-10800 != 0`) stays
   recorded.
5. **Next-sitting predictions** appended to your own report, from `build6_capacity_covered_pass3`
   (the owner's current fixture; 6243, 2012, 2009 and its small station are the chained witnesses):
   - chained untouched spokes settle at their dial;
   - one chained Export and one chained Import reach their numbers;
   - zero `LUA ERROR` across at least one sol at top speed.

   The orchestrator runs the sitting with the owner and relays results; you do not attend. Preload
   slots under `tools/SMRTK.md` (slot 4 already reads a whole station). A console line is acceptable
   where no slot fits (owner, 2026-09-27).
6. **A report**, `docs/agent/reports/TRAIN_ROUTING_5D_<date>.md`, with the forwarding rule, the rung
   table and the predictions. Spec §4.8 gets a short pointer. Hand back with the commit and a relay
   the orchestrator can read in one pass.

## Start

`git log --oneline -5`, `git status`, `git pull --ff-only`. Authored on the commit that adds this
brief. Put the work in the todo tool before the first write, one item per commit-and-verify unit.
Commit with a pathspec.

## Scope

**In:** `Code/40_TrainDistribution.lua`, `Code/45_TrainDistributionUI.lua` (chained-row tooltip
text only), `Code/10_TrainFloor.lua`, a new routing file of your own under `Code/` if that is
cleaner (register it in `metadata.lua`), the distribution tests, TestKit slots, your report and
spec §4.8's pointer.

**Out:**
- ⛔ `Code/20_TrainHub.lua` and `Code/30_TrainHubDrones.lua`. If a new persisted name lands, report
  the exact header-inventory line and the orchestrator writes it.
- The route model: no trains driving through a hub; that is 5c. Colonist routing (5b).
- Multi-hub forwarding, from one hub's network to another's. The test colony has one hub. Design
  the hop rule so it does not preclude that, but do not build it.
- Drone behaviour, the Capacity Network Upgrade, train construction or placement (§4.9), the
  shipping `Code/` tree, and `FIX_POLICY` §8's both-configuration ship test.

Report anything outside this fence without editing it.

## Stops

- Forwarding needs a route-model change, or a copied vanilla `TransferCargo` body: report the
  measurement and the attempt.
- A part needs rung 4 or 5 (§4.8's ladder): report the part, the lower-rung attempt and its
  measurement before writing it.
- Forwarding makes an existing direct-line case measure differently from its passed live result:
  report the case.

## Do not claim

- ⛔ Not "routing works across a network". Claim the shapes measured, in the colony tested.
- ⛔ Not multi-hub routing.
- ⛔ Not "save-safe". Claim the rung each part reached, with the residual named.

## Lifecycle

A one-off. Done when the build and predictions are committed and handed back. The orchestrator runs
the sitting, then parks or deletes this brief and moves its row in `README.md` in one commit
(owner, 2026-09-21). Build agents do not delete or move their own brief.
