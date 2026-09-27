# The distribution centre — pass 4: untouched rows are real Balanced

**LIVE: pass 4** (2026-09-27), for a fresh session. The dev mod is `tools/devmods/train_hub/`, and
your files are `Code/40_TrainDistribution.lua`, `Code/45_TrainDistributionUI.lua` and
`Code/10_TrainFloor.lua`. Every mode has passed live, including a station with drones in range after
pass 3's divide-by-zero fix (`d568983`). This pass closes the one gap the owner found: **a row the
player never touched reads "Balanced" but runs vanilla's even-out-by-storage-size spread.** Read spec
§4.7 and §4.8 of `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` (every ruling, the
save-boundary ladder, all three sittings) and `docs/agent/reports/TRAIN_DISTRIBUTION_PASS2_20260926.md`
(mechanism, rung table, desk suite, pass 3) before the first write.

## Authority

- ⚖️ **Owner rulings of 2026-09-27 in spec §4.8, "Owner rulings, 2026-09-27, over that sitting".**
  This pass carries out rulings 3, 4 and 5:
  - **Balanced is the hub's pin.** Stock above the number goes to the hub, and stock below it is
    filled from the hub.
  - **Local drones stay free in every mode.**
  - **An untouched row is real Balanced at vanilla's dial:** the player's own dial, 10 units by
    default, not a fixed percentage.

  This reverses pass 2's "unconfigured resources retain vanilla behavior". Stations off the hub's
  network keep vanilla.
- **Ruling 1 (network = every station chained to the hub) and ruling 2 (5d routing next) are NOT
  this pass.** Chained stations whose train line never reaches the hub need forwarding; that is a
  separate routing build. Keep the current rule that enforcement acts at a stop whose line includes
  the hub.
- The rest of §4.8 (per-resource modes, the hub as sink and source, a full hub refuses, the ladder
  at its lowest working rung with rung 2 and one persisted name, `SMROptIn_distribution`) and §4.7's
  accepted UI stand. `FIX_POLICY` §0, §1's technique ranking and §2 (gated by
  `tools/harvest_wrap_targets.py --check`) apply, and both bans bind. Testing depth is smoke only.
  Method: small and rough.

## The evidence

Third sitting, closed log `Mars.exe-20260927-18.04.23-6aad2d75.log` (the orchestrator archives it
under `docs/archive/train_distribution_20260926/sittings/`). Every slot-4 read was taken at one
paused moment after about 3 sols on `build6_capacity_covered_pass3`:
- Untouched stations 2008, 2011, 2012, 6243 and 1994 read `mode=vanilla percent=unset
  supply_desired=10000` and held **40–49** Metals of 120, while their rows showed "Balanced ~8%". The
  hub held 177 of 480, the same ~37% fill: vanilla's capacity-share spread.
- The call counter (`D.CallsFor`) read 0 at every station except 2007 and the hub.
- 2009, configured Balanced 4%, held 80. Its line to a small station never reaches the hub, which
  is the routing gap and not this pass's to fix.

## End state

1. **An untouched resource row on a hub-network station behaves as Balanced at the station's live
   vanilla dial** (`desired_amount`), in the same train arithmetic that configured Balanced uses.
   Over the dial, trains take the excess to the hub; under it, trains fill from the hub. The dial is
   an absolute amount, and the row's shown percentage stays derived from it, as today.
2. **No new persisted state for untouched rows.** They must not write hub-table entries just by
   existing; the default is computed from the live dial. If that proves impossible at rung 2, stop
   (below).
3. **Configured rows, disabled rows and stations off the network are unchanged.** The existing desk
   cases are the control.
4. **Desk cases:** a line with untouched spokes holds each at its dial, with the rest at the hub; the
   dial is moved and the hold follows; a network doubling (capacity upgrade) keeps the absolute dial.
   Rerun the whole suite plus `python tools/parsecheck.py` and `harvest_wrap_targets.py --check`,
   preserving every output with its command and HEAD. The known `traffic_smoke` failure
   (`-10800 != 0`) stays recorded.
5. **Next-sitting predictions**, appended to the pass-2 report, from `build6_capacity_covered_pass3`:
   - untouched spokes on hub lines settle at **10**, the hub holds the rest;
   - configured rows still behave as measured;
   - zero `LUA ERROR` over at least one sol at top speed.

   The orchestrator runs the sitting with the owner; you do not attend. Preload slots under
   `tools/SMRTK.md`. A console line is acceptable where no slot fits (owner, 2026-09-27). Slot 4 on
   one station already dumps every configured row; make it report untouched rows as their effective
   Balanced amount, so one press reads the whole station.
6. **Hand back** with the commit and a short relay the orchestrator can read in one pass.

## Start

`git log --oneline -5`, `git status`, `git pull --ff-only`. Authored on `d568983` plus the spec
rulings commit. Put the work in the todo tool before the first write, one item per commit-and-verify
unit. Commit with a pathspec.

## Scope

**In:** `Code/40_TrainDistribution.lua`, `Code/45_TrainDistributionUI.lua`, `Code/10_TrainFloor.lua`,
the distribution tests under `tests/`, TestKit slots, the pass-2 report, and spec §4.8's result lines.

**Out:** ⛔ `Code/20_TrainHub.lua` and `Code/30_TrainHubDrones.lua`. Also out: 5d routing and any
forwarding between lines; drone behaviour (ruling 4 keeps it vanilla); the Capacity Network Upgrade;
train construction or placement (§4.9); the shipping `Code/` tree; and `FIX_POLICY` §8's
both-configuration ship test. Report anything outside this fence without editing it.

## Stops

- Untouched-as-Balanced needs persisted state per station, or a rung above 2: report the
  measurement before writing it.
- The change alters a configured row's measured behaviour and no rung-2 route avoids that: report
  the case.

## Do not claim

- ⛔ Not "the whole network obeys its rows". Chained stations off hub lines wait for 5d.
- ⛔ Not "save-safe". Claim the rung, with the residual named.

## Lifecycle

Done when the change and predictions are committed and handed back. The orchestrator runs the
sitting, then parks or deletes this brief and moves its row in `README.md` in one commit (owner,
2026-09-21). Build agents do not delete or move their own brief.
