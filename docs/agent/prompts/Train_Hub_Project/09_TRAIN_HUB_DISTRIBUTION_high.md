# The distribution centre — first pass

**LIVE** (owner, 2026-09-26: *"while capacity is running we need to get the distribution center
built"*). This is Module A's A1+A2 with the hub as the sink. The design is settled in spec §4.8 of
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`; §4.7 settles the UI, §4.5 lists six paths
your values must survive, §4.6 is the alias trap, §4.3 names which parts are UI-only and which is
genuinely new. **Read §4.1 through §4.9 before the first write.** They carry the mechanism, the
decisions already taken and the owner's 2026-09-25 sitting that measured the three things this
design rested on. Do not re-derive any of it.

⚠️ **A parallel brief is live.** `08_TRAIN_HUB_CAPACITY_high.md` runs at the same time and **owns
`20_TrainHub.lua` exclusively**. You must not edit that file — not one line, not a comment. The
Scope section is a hard fence. See "Keeping off the hub file" for how you hold hub state anyway.

## Authority

- ⚖️ **Owner, 2026-09-24, the whole of §4.8.** Per-resource, never per-station. The hub is the sink
  and the source: it takes what the spokes do not want and feeds each spoke what it does. State
  lives **on the hub**, not on vanilla stations. Controls live in **each station's own card**, in the
  resource row the panel already draws. Storage location and UI location are independent.
- ⚖️ **Owner, 2026-09-26: full player control, no automatic anything.** *"I don't want auto selected
  presets, I want to give full control to players everything is check the import box, check the
  export box, or no check and balanced. And the slider"*. So: **two checkboxes and a slider per
  resource row.** Neither box checked **is** balanced. **No sector presets, no "suggest" pre-tick,
  no central overview** — all three §4.8 interaction ideas are refused for this pass. Import and
  export are mutually exclusive; checking one clears the other.
- ⚖️ **Owner, 2026-09-26: an uncovered spoke gets the train half only, and the row says so.** A
  station with no Drone Controller in range keeps working on the train side; the drone half simply
  does nothing there, and the row shows that there are no drones in range. ⛔ **This does not reopen
  link 4's filter**: the hub's fleet stays maintenance-only for far stations
  (`20_TrainHub.lua`, re-derive with `grep -n`), because joining every request turned the fleet into
  a resource balancer between stations. Do not make the hub's Wasps serve these modes at distance.
- ⚖️ **Owner, 2026-09-26: a full hub refuses.** When the hub fills, it stops accepting that resource
  rather than letting §3's capacity-share rule push stock back out and bounce an exporter
  (drained, refilled, drained). The excess sits at the spoke and the player sees a full hub.
- ⚖️ **Owner, 2026-09-25: OI-29 closed, "yes".** The drone-side questions were answered with no code,
  so this work starts from those results rather than re-measuring them.
- `FIX_POLICY` §0 (content-mod risk standard), §1's technique ranking and §2 (the alias rule, gated
  by `tools/harvest_wrap_targets.py --check`) apply. Both bans bind.
- Testing depth (owner, 2026-09-19): a **smoke test only**. The full battery runs once, on the final
  build. **Method (owner, 2026-09-20): small and rough, then dial in by eye.** No gate, battery or
  analysis run stands between the owner and a rough thing they can look at.

## What is already measured — do not re-derive

From the owner's sitting of 2026-09-25 (spec §4.8 "Owner's sitting"; log archived under
`docs/archive/train_distribution_20260925/`):

- **The transient claim path runs natively: PASS.** On StationSmall 2008 the drones' view read
  supply target 60 while the train's view read 48; import made the train's supply target 0.
  `native calls=8`, no error.
- **Drones respond to the baseline numbers: PASS.** Station 6243 went 10.5 → 60 when export was set
  by hand (supply desired 60, demand desired 0) and its depot filled it immediately.
- **`accept` is real: PASS.** Station 2011 drained to 0 while its depot reached 310, about 2.3× the
  control's rate — loose, because train deliveries were not controlled.
- ⛔ **Draining to the export floor is STILL UNPROVEN.** In that sitting vanilla's capacity share took
  only 26 of the available stock, so the floor never had to bind. §4.3 is explicit that the export
  floor is **the one genuinely new thing**: the train reads
  `available = Min(supply:GetTargetAmount(), supply:GetActualAmount())` and never subtracts a floor.
  This pass has to make the floor bind and then show it binding.
- **Defect in the existing file, fix it here:** `40_TrainDistribution.lua`'s `print_view` divides by
  a global `ResourceScale` that the game never defines — vanilla keeps it file-local. Use
  `const.ResourceScale` (`ResourcesFormatting.lua:6`). The offline harness defined the global, so
  `Status` failed only in game.

## Keeping off the hub file

The hub's per-station, per-resource table must live on the hub object, and `20_TrainHub.lua` is
brief `08`'s. **The precedent that makes this possible is `SMROptIn_floor_hold`**: it is a field on
hub objects owned entirely by `10_TrainFloor.lua` (`local FIELD = "SMROptIn_floor_hold"`), and it is
**not** declared in the `SMROptInTrainHubBase` class table. Verify that with
`grep -n SMROptIn_floor_hold tools/devmods/train_hub/Code/` before you rely on it, then own your
field the same way from your own file. One persisted name covers the whole feature (§4.8).

The one thing you owe `20_TrainHub.lua` is its header inventory comment, which lists each field and
the file that owns it. **Do not write it yourself.** Report the exact line you want added; the
orchestrator lands it after brief `08` closes.

## ⚠️ The parallel brief changes your blast radius

§4.5's rewrite path `MultiResourceDepotBase:OnModifiableValueChanged` → `UpdateRequestCapacity`
fires on a capacity change and then **rewrites every resource's desired amounts from the dial,
whatever the policy says**. Until now that meant one building at a time, via Expanded Warehousing.
Brief `08` is building the **Capacity Network Upgrade**, which raises `max_storage_per_resource` by
100% on **every station in the colony at once** (spec §4.10). So that rewrite becomes a
network-wide event that will land on every configured station in the same frame.

Therefore, per §4.7: **store every floor and amount relative to the live `GetMaxStorage(res)`, and
re-apply after each of §4.5's six paths.** Your desk smoke must include a network-wide capacity
doubling, not just a single-station one. You do not need brief `08`'s code to test this — drive
`OnModifiableValueChanged` directly in the harness.

## End state

1. **Three modes per resource per station**, with the owner's control: an import checkbox, an export
   checkbox, and the slider. Neither checked is balanced. The modes behave as §4.8's table says:

   | mode | local DRONES | TRAINS | the slider is |
   |---|---|---|---|
   | Export | keep it full — haul the area's excess in | drain it, never deliver | the minimum to keep |
   | Import | keep it empty — distribute out to the area | fill it, never take away | the amount always kept |
   | Balanced (unchecked) | vanilla | vanilla, pinned to the number | the number to hold |

   The lever is one, with two views: **baseline request numbers are what the drones see; a transient
   claim applied inside the train's evaluation and released at once is what the trains see.** The
   balancer is not touched.
2. **The export floor binds.** A train leaves the slider's amount behind. This is the new work, in
   the already-wrapped `Train:TransferCargo` path (`10_TrainFloor.lua`, re-derive the lines).
3. **A full hub refuses** that resource, as ruled above.
4. **State on the hub**, one persisted name, owned from your own file. Removing the mod removes the
   hub and every trace of the feature.
5. **UI in the station card's existing resource rows** (§4.7): same visual weight as the parts
   already there, not a new section. The panel's Basic / Advanced / Delicacies / Other grouping and
   its `stored/max` readouts stay intact. An uncovered station's row shows that there are no drones
   in range. Infopanel XTemplates are UI data; nothing of ours persists there. The hub's own card
   gets **nothing** this pass.
6. **Survives §4.5's six rewrite paths and §4.6's alias trap**, including the network-wide capacity
   change above.
7. ⛔ **The save rule for claims.** Requests are saved, so a standing claim on a vanilla station
   could persist into a save and outlive the mod, leaving a station quietly crippled with nobody to
   undo it. **Prefer transient claims.** Where a standing claim is genuinely needed for the drone
   view, release every claim at `SaveGameStart` and re-apply after — the shape the hub's reserve
   reconcile and the drones' save guard already use.
8. **Desk smoke.** Extend the existing `distribution_smoke.py` work: all three modes, the floor
   binding, a full hub refusing, each of §4.5's six rewrite paths, the network-wide capacity
   doubling, the alias trap, save/load with claims outstanding, and an uncovered station. Rerun the
   whole existing suite plus `python tools/parsecheck.py` and
   `python tools/harvest_wrap_targets.py --check`, preserving every output with its command and HEAD.
9. **The attended smoke with the owner** (below).
10. **Record** in a build report under `docs/agent/reports/`, fold the result into spec §4.8, and
    archive the session log byte-for-byte under a new `docs/archive/train_distribution_<date>/`.
    Then hand back to the orchestrator.

## The attended smoke, from the owner's seat

Preload every reading into TestKit slots under `tools/SMRTK.md` before launch. **The owner clicks;
they do not type.** A hand-typed console line or a wait measured in real minutes each needs a stated
reason no slot can do it — owner time is the cost being minimised. Use the standing
`train_hub_base` fixture and do not save over it (spec §10 "The standing test save"). Read the
console yourself from the newest `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-*.log` when the
owner says "flushed". After an autosave the owner re-presses the armed slot. About **five steps at a
time**.

Cover, in this order: the boxes and slider on a covered station; export draining to the floor and
stopping there (the unproven one — make it bind); import filling and holding at the slider; a
station with drone coverage showing the drone half working both ways; an uncovered station doing the
train half only with its row saying so; the hub filling and refusing; and a save/reload with modes
set and a train mid-transfer.

Ask the owner whether the rows **read** right and whether the modes do what they expect by eye. That
is the dial worth their time.

## Start

`git log`, `git status`, `git pull --ff-only`. Authored on `d2e3a78`. An empty
`git diff --stat d2e3a78..HEAD -- tools/devmods/train_hub/Code/10_TrainFloor.lua tools/devmods/train_hub/Code/40_TrainDistribution.lua`
means the code facts above hold; otherwise re-derive every cited line with `grep -n`. Because brief
`08` is committing to this tree at the same time, `git pull --ff-only` before **every** commit and
commit with a pathspec. Put the work in the todo tool before the first write, one item per
commit-and-verify unit.

## Scope

**In:** `Code/40_TrainDistribution.lua`, `Code/10_TrainFloor.lua`, a new UI file of your own naming
under `Code/`, `tests/distribution_smoke.py` and any new test beside it, `metadata.lua` (re-read
immediately before each write), TestKit slots, the sitting, `FIX_POLICY`'s inventory row for your
persisted name, spec §4.8, your own report.

**Out:** ⛔ `Code/20_TrainHub.lua` and `Code/30_TrainHubDrones.lua` — brief `08` owns the first and
neither is yours. Also out: the Capacity Network Upgrade itself (spec §4.10, brief `08`); sector
presets, the "suggest" pre-tick and any central overview (refused by the owner today); train
construction or placement at the hub (spec §4.9, not authorised); routing 5c/5d; the shipping
`Code/` tree (this stays a dev mod); and `FIX_POLICY` §8's both-configuration ship test, which is
owed for the whole hub and is not this brief's to discharge.

Report anything you find outside this fence without editing it.

## Stops

- The export floor cannot be made to bind without taking over vanilla's capacity-share arithmetic
  (`Units/Train.lua:921-952`): report what you measured and what the takeover would cost, before
  writing it. That arithmetic is existing measured behaviour.
- The drone view needs a **standing** claim on a vanilla station that cannot be released at
  `SaveGameStart` and re-applied: report before writing it. This is the save rule's hard edge.
- The station card's resource row cannot carry two checkboxes and a slider at the panel's own visual
  weight: report what the row can hold, with a screenshot, before inventing a new section.

## Do not claim

- ⛔ Not "the distribution centre works". Claim the modes measured, on the stations tested, in that
  colony, with the drone coverage each one actually had.
- ⛔ Not that the drone half works on uncovered spokes. By the owner's ruling it does nothing there;
  say so.
- ⛔ Not a balance result. The slider's numbers are the player's, and nothing here is tuned.
- ⛔ Not that it survives the Capacity Network Upgrade in play. Brief `08` is unfinished while you
  work; you can only claim the harness-driven rewrite. The live pairing is the orchestrator's to
  schedule once both land.
- ⛔ Not a ship-test pass.

## Lifecycle

Done when the attended smoke is recorded and spec §4.8 carries the result. The orchestrator then
parks or deletes this brief and moves its row in `README.md` in one commit (owner, 2026-09-21).
Build agents do not delete or move their own brief.
