# The distribution centre — second pass

**LIVE: pass 2** (2026-09-26). Pass 1 is `5afdbe6`, its receipt
`reports/TRAIN_DISTRIBUTION_BUILD_20260926.md`. It reached the brief's first stop correctly: with
the claim mechanism as specified, a floor of 20 left 60 or 36 depending on the sink, and returning
trains took no more. The feature is unbuilt. This pass starts from that stop, from the orchestrator's
source reads below, and from two owner rulings taken today. Read spec §4.1 through §4.9 of
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` before the first write; §4.8 carries every
ruling and is what this brief obeys.

⚠️ **A parallel brief is live.** `08_TRAIN_HUB_CAPACITY_high.md` owns `20_TrainHub.lua` and the
building template; its desk half is committed (`c6108c9`, `daef3ec`) and its attended smoke waits on
the owner. You must not edit `20_TrainHub.lua` — not one line. The Scope section is a hard fence.
"Keeping off the hub file" says how you hold hub state anyway.

## Authority

- ⚖️ **Owner, 2026-09-24 and 2026-09-26, the whole of §4.8.** Per-resource, never per-station. The
  hub is the sink and the source. State on the hub, controls in each station's own resource row: two
  checkboxes and a slider, neither checked is balanced, import and export mutually exclusive. No
  presets, no "suggest", no overview. A full hub refuses. An uncovered spoke gets the train half only
  and its row says so; link 4's maintenance-only filter stays shut.
- ⚖️ **Owner, 2026-09-26: the save boundary may be crossed for this feature, minimally** (§4.8
  "Owner ruling, 2026-09-26: the save boundary"). *"this peice we are working on is a corner stone
  for the mod, its the single most requested thing the community wants … if we hit a wall where to
  achieve our goals we have to contaminate saves we will. The goal then becomes contaminate minimally
  to achieve our goal"*. You no longer stop to offer a crossing. You take the **lowest rung of §4.8's
  ladder that achieves the goal**, and your report says which rung each part reached and what
  measurement showed the rung below could not do it. Rung 4 or 5 also goes in the module description.
- ⚖️ **OI-31 is retired by delegation, not by a yes.** The owner's direction is the most control for
  the least contamination. Within that, **the route is yours**, in this order of preference, and you
  do not come back between steps: (1) transient lies told to vanilla's own arithmetic inside the
  `TransferCargo` call we already wrap; (2) an amount-only allocation that hands its number to
  vanilla's own `Train:LoadResourceForStation`, so every saved byte is vanilla-written (rung 1). A
  copied `TransferCargo` body is still a stop.
- `FIX_POLICY` §0, §1's technique ranking and §2 (the alias rule, gated by
  `tools/harvest_wrap_targets.py --check`) apply. Both bans bind. Testing depth: **a smoke test
  only**; the full battery runs once, on the final build. Method: small and rough, then dial in by eye.

## What the orchestrator read in the source — claims to confirm, not re-derive

All from the archived **1.1.1.405907** tree, `Src/Lua/`. Each is a source read; where it says
MEASURED it is from pass 1's harness or the owner's 2026-09-25 sitting. Re-derive every line with
`grep -n` before you cite it.

1. **The law behind the stop: retained = slider + vanilla's share.** `Units/Train.lua:929-951`:
   `needed = MulDivRound(total, my_storage, line_storage)` is the source's capacity-proportional
   entitlement to the line's stock; `load_amount = Min(target − stored, available − needed)`. A claim
   shrinks `available` (via `AssignUnit`, engine) and leaves `needed` alone, so the two **stack**. Pass
   1's rows (100/100 → keeps 60; 100/400 → keeps 36) are `20 + 40` and `20 + 16` exactly. A claim can
   only ever make a station keep *more* than vanilla would.
2. **`needed` is computed only for an enabled source.** `Train.lua:929-932`:
   `if station:IsResourceEnabled(res) and res_data.storage[res] > 0 then needed = …`. `available` is
   computed whenever the line desires the resource (`:934`), regardless of the source's own state. So a
   source that *answers* disabled for that one resource, inside that one call, has `needed = 0` and a
   claim of `floor` retains exactly `floor`. **This is the first thing to test.** Side effect: the
   source's capacity and dial leave the line totals for that evaluation (`:886-900`), so every other
   station's share rises — the right direction for an exporter feeding a hub, but measure it.
3. **Persistent "disabled" is NOT your export mode.** `Buildings/MultiResourceDepot.lua:265-274`:
   turning a resource off puts `rfSuspended` on the demand request and `rfPostInQueue` on the supply
   — drones stop delivering and actively carry it away. That is the owner's export table inverted on
   the drone half. It also flips the train policy to `"send"` (`Buildings/Station.lua:1078-1082`). So
   the enabled-state lie must be **transient and per resource**, never the saved toggle.
4. **Import may be share-bounded too.** The fill target is
   `target = MulDivRound(total, dest_storage, line_storage)`, capped at the destination's max
   (`Train.lua:943-946`); opening demand raises a different bound (`:949`), not that one. **Unmeasured.**
   Measure the ceiling before designing import; if it binds, the same family of lies (the destination
   answering a larger capacity for that call) is the first candidate.
5. **Everything that decides is Lua; only the ledger is engine.** The arithmetic, the line walk
   (`TrainTransport.lua:371`), the priority lanes (`Train.lua:729-731`) and the loading loop are
   script. `AssignUnit` / `UnassignUnit` / `GetTargetAmount` / `GetActualAmount` / `Request_New` have
   no Lua definition anywhere in `Lua/` or `CommonLua/` and are C++: callable, not changeable. The
   station's capacity getter is `MultiResourceCubeVisuals:GetMaxStorage` (`:571`), Lua — the §4.6
   alias-trap class, so any wrap goes on the declaring class. `IsResourceEnabled`'s declaring class
   is yours to find.
6. **Share-aware claims are the fallback for the shrink direction:** claim `slider − needed`, computing
   `needed` with vanilla's own formula over the same walk. Exact above the share, a patch-tracking
   duty (gate it by source hash), and still walled below the share. Prefer item 2.
7. **Pass 1's fixture was the worst case, not the owner's game.** Equal-capacity twins make the share
   half the stock. On the owner's lines the hub (240, 480 after brief 08) dwarfs a 60-cap spoke: the
   share is about a fifth. **Build the desk fixture in that shape**, and keep the equal-twin case as the
   adversarial one.

## Keeping off the hub file

The precedent is `SMROptIn_floor_hold`: a field on hub objects owned entirely by `10_TrainFloor.lua`
(`local FIELD = …`), not declared in the `SMROptInTrainHubBase` class table. Verify with
`grep -n SMROptIn_floor_hold tools/devmods/train_hub/Code/`, then own your field the same way from
your own file. One persisted name covers the feature (§4.8, rung 2). The header inventory comment in
`20_TrainHub.lua` is owed: **report the exact line, do not write it** — the orchestrator lands it
after brief `08` closes.

## ⚠️ The parallel brief changes your blast radius

§4.5's `OnModifiableValueChanged` → `UpdateRequestCapacity` rewrites every resource's desired amounts
from the dial on a capacity change. Brief `08`'s upgrade raises `max_storage_per_resource` on **every
station at once** (spec §4.10), so that rewrite becomes a network-wide event. Store every floor and
amount relative to the live `GetMaxStorage(res)` (§4.7) and re-apply after each of §4.5's six paths.
Your desk smoke drives `OnModifiableValueChanged` network-wide from the harness; you do not need
`08`'s code.

## End state

1. **The export floor binds exactly**, at any slider value, on the hub-sized fixture and on the
   equal-twin one, via the lowest rung that does it (item 2 first). The pass-1 rows reproduce as the
   control, then the fix makes retained = slider.
2. **The import ceiling is measured** (item 4) and, if it binds, lifted by the same family; if it does
   not, say so with the numbers.
3. **Balanced pins to the number** — vanilla with both sides claimed at the slider.
4. **A full hub refuses** that resource.
5. **The drone half is the baseline numbers**, written only through vanilla's own
   `Station:SetDesiredAmount` path (rung 1) and re-derived from the hub's table on load. OI-29
   (owner, 2026-09-25: "yes") already admits the baseline into the save; the residual is a station
   that behaves as last set until the player touches its dial, and the description says so.
6. **State on the hub**, one persisted name, from your own file.
7. **UI in its own section on the station card** — ⚖️ owner, 2026-09-26, in the sitting, reversing the
   in-row placement (spec §4.7 holds the ruling and the owner's words). Vanilla's resource rows are
   left untouched. One import/export section attached to `ipBuilding`, with its own Basic · Advanced ·
   Delicacies · Other tabs. ⚖️ **It must look native** (owner, later the same sitting; spec §4.7
   holds the words): each resource is **one vanilla three-state cycle row modelled on the dome's
   births toggle** (`sectionDome.lua`) — one click cycles Balanced → Export → Import, changing the
   hex frame, glyph, title text and rollover — with vanilla's `InfopanelSlider` at full width and the
   value plus `stored/max` in the right title. Native parts only: no hand-built text, checkboxes or
   buttons, no custom colours or fonts. Help is the **game's own `?` icon**
   (`UI/InfopanelRemaster/encyclopedia.png`) at the **right-hand end of the section header**, on
   hover only — no standing popup over controls. If per-state title text proves impossible, the
   owner's fallback is custom `IM` / `EX` / `BAL` icons with a key on each tab (spec §4.7). An uncovered station shows its no-drones line at the top of the
   section. The hub's card gets nothing. Infopanel XTemplates are UI data; nothing of ours persists
   there. The pass-2 row controls come out.
8. **Survives §4.5's six rewrite paths and §4.6's alias trap**, including the network-wide capacity
   change above; `harvest_wrap_targets.py --check` passes.
9. **Desk smoke** extending `distribution_smoke.py`: both fixtures; all three modes; the floor
   binding; the import ceiling; a full hub; each rewrite path; the network-wide doubling; save/load
   with a lie mid-call (it must not be there at `SaveGameStart`); an uncovered station. Rerun the whole
   existing suite plus `python tools/parsecheck.py`, preserving every output with its command and HEAD.
   The existing traffic-smoke failure pass 1 recorded separately stays recorded, not silently fixed.
10. **The attended smoke with the owner** (below), then a build report, spec §4.8 folded, the session
    log archived byte-for-byte under `docs/archive/train_distribution_<date>/`, and the rung table:
    one row per part, its rung, the measurement that closed the rung below. Hand back to the
    orchestrator.

## The attended smoke, from the owner's seat

Preload every reading into TestKit slots under `tools/SMRTK.md` before launch. **The owner clicks;
they do not type.** A hand-typed console line or a wait measured in real minutes each needs a stated
reason no slot can do it. Use the standing `train_hub_base` fixture and do not save over it (spec §10
"The standing test save"). Read the console yourself from the newest
`%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-*.log` when the owner says "flushed". After an
autosave the owner re-presses the armed slot. About **five steps at a time**.

Cover, in this order: the boxes and slider on a covered station; **export draining to the floor and
stopping there** — the pass-1 failure, now the headline; import filling and holding at the slider; a
covered station's drone half working both ways; an uncovered station doing the train half only with
its row saying so; the hub filling and refusing; a save/reload with modes set and a train
mid-transfer. Ask the owner whether the rows **read** right and whether the modes do what they expect
by eye.

## Start

`git log`, `git status`, `git pull --ff-only`. Authored on `daef3ec`. An empty
`git diff --stat daef3ec..HEAD -- tools/devmods/train_hub/Code/10_TrainFloor.lua tools/devmods/train_hub/Code/40_TrainDistribution.lua`
means the code facts above hold; otherwise re-derive every cited line with `grep -n`. Brief `08`
commits to this tree at the same time: `git pull --ff-only` before **every** commit, commit with a
pathspec, and re-read `metadata.lua` immediately before each write to it. Put the work in the todo
tool before the first write, one item per commit-and-verify unit.

## Scope

**In:** `Code/40_TrainDistribution.lua`, `Code/10_TrainFloor.lua`, a new UI file of your own naming
under `Code/`, `tests/distribution_smoke.py` and any test beside it, `metadata.lua`, TestKit slots,
the sitting, `FIX_POLICY`'s inventory row for your persisted name, spec §4.8, your own report.

**Out:** ⛔ `Code/20_TrainHub.lua`, the building template and `Code/30_TrainHubDrones.lua`. The
Capacity Network Upgrade itself (brief `08`). Presets, "suggest", any overview. Train construction or
placement at the hub (§4.9). Routing 5c/5d. The shipping `Code/` tree. `FIX_POLICY` §8's
both-configuration ship test, owed for the whole hub and not yours to discharge. Report anything
outside this fence without editing it.

## Stops

- Neither the transient route nor amount-only allocation through vanilla's own loader can make the
  slider true, and the only thing left is a copied `TransferCargo` body: report the measurements, not
  the copy.
- A part needs rung 5 (our own persisted class referenced from a vanilla object): report the part,
  the rung-4 attempt and its measurement, before writing it.
- The section cannot be attached to vanilla stations' `ipBuilding` panel the way the TestKit's is:
  report what was tried, with a screenshot, before placing controls anywhere else.

## Do not claim

- ⛔ Not "the distribution centre works". Claim the modes measured, on the stations tested, in that
  colony, with the drone coverage each actually had.
- ⛔ Not "save-safe". Claim the rung each part reached, by the ladder, with the residual named.
- ⛔ Not that the drone half works on uncovered spokes; by ruling it does nothing there.
- ⛔ Not a balance result; nothing here is tuned.
- ⛔ Not that it survives the Capacity Network Upgrade in play; only the harness-driven rewrite. The
  live pairing is the orchestrator's to schedule once both briefs land.

## Lifecycle

Done when the attended smoke is recorded and spec §4.8 carries the result and the rung table. The
orchestrator then parks or deletes this brief and moves its row in `README.md` in one commit (owner,
2026-09-21). Build agents do not delete or move their own brief.
