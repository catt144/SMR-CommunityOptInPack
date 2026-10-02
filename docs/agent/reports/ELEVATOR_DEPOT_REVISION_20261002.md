# Elevator Depot follow-up — brief 30, 2026-10-02

Built and desk-verified; the attended smoke below is pending. Authority: the owner's
four-item request and train spec §11's 2026-10-02 rulings, `01a8b98`..`384b18d`.
The earlier station-row sitting A/B/C passed (`9b05edc` and its report); this smoke
covers the subsequent depot work. B3–B4 also supply OI-38's remaining scripted up-leg read.

`git pull` ran first at `384b18d`, already current. Shared-tree documentation then
advanced to `d5d72f0`; attribution is the diff, not its author. Executed model:
Codex (GPT-6 per session instructions; exact backend model id not exposed).
Installed build read by `python tools/doccheck.py --emit-fingerprint`: **25579348**.
Native source below is from `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`.

## What changed

The orphan animation was a fallback to the old display cycle in `start_cycle`.
The schedule follower now stays alive without a twin, parks either cabin at that
half's landing, ends moving FX and resumes following real legs when a pair forms.
The explicit developer display-cycle toggle is still available.

Both legs sort their eligible rows by destination stock plus promised incoming
stock; ties use resource id. Down legs consider Import, up legs Export. Loading
and delivery are bounded by physical room and unreserved demand. Cargo already
aboard also consumes cabin space and destination need. A carrier can still fill
the destination while the cabin travels: cargo that no longer fits stays aboard
and returns, as before. No new standing reservation or train scheduler is added.

The cabin carries **250 units per leg**, shared across resources. Each half stores
**250 per resource**. Native upgrade slot **1**, **Expanded Depot**, costs **10 Metals
and 10 Concrete** and raises both figures to **500**. Either half can order it;
the twin cannot order a duplicate while it is being built. The purchase is shared
by the pair, cannot be toggled off, survives one half's replacement and is lost if
both halves are removed. Existing stock is retained when capacities reconcile.
Only the original buyer carries the native numeric tier receipt for spent-resource
refunds; the twin and replacements cannot duplicate that refund.

Capacity Network's station-storage modifier is excluded only on this depot;
other stations, hubs and unrelated modifiers retain their behavior. The depot's
250/500 ruling therefore also holds in the owner's upgraded hub fixture.

The missing train controls came from native `sectionCustom`: it checks the exact
building class, then its exact `object_class`, without following Station ancestry
(`Lua/XDef/sectionCustom.generated.lua:14`). The depot now aliases the native
`customStation` section, including Construct Train, Send out Train and its train
readout. Their native actions and enable conditions are reused. Construction can
automatically assign the train when only one eligible line exists
(`Lua/Buildings/Station.lua:579`); Send out Train needs an available train.

**No Mod Editor save is needed.** The authored base class supplies the upgrade
properties; the current generated building class inherits them. Native
`UpgradableBuilding.lua:67` can inject raw zero costs on descendants, so startup,
load and placement also publish the two costs on the final runtime class. The
smoke checks both inheritance and those shadowing zeros. No generated file was edited.

Save contract addition: `SMROptInElevatorDepotDev_Capacity`, the upgrade id stored
in vanilla `upgrades_built`, `upgrade_on_off_state`, `upgrade_modifiers`,
`upgrade_id_to_modifiers`, the colony's `unlocked_upgrades` and the native construction receipt. No new saved field,
class, modifier object or thread is introduced. Add this id alongside the depot's
existing pending inventory when moving the dev mod to shipping. The existing
`SMROptIn_depot_cabin` name and cargo schema remain unchanged.

## Desk evidence

Executed against `d5d72f0` plus this change:

- `python tools/devmods/elevator_station/tests/revision_smoke.py` — PASS. Executes
  the depot plus archived native upgrade, cost, resize and panel functions. Checks
  orphan rest/FX/resume on both maps; lowest-stock priority and reservation/room
  bounds both ways; 250/500 loads and storage; cost and shared purchase; replacement;
  hub modifier isolation; both native train buttons; generated-class inheritance;
  staged setup/read/watch slots, including stale runs and automatic train assignment.
  It also runs the existing `wiring_smoke.py` checks.
- `python tools/devmods/elevator_station/tests/props_smoke.py` — PASS.
- `python tools/devmods/train_hub/tests/hubless_slots_smoke.py` — PASS. The earlier
  station-row slot 5 now replaces its stale run instead of refusing it.
- `python tools/parsecheck.py --dir tools/devmods/elevator_station/Code --quiet`
  and the same command with `--dir B:/Dev/SMR/SMR-BugFixPack-TestKit/Code` — PASS.

The harness prints its command, HEAD and the SHA-256 of each archived native input.
Engine request/world/window behavior is doubled. Real panel layout, physical art,
train construction/assignment and native save serialization remain live checks;
these desk results do not establish them. The final shipping battery stays separate.

## Preloaded slots

Installed `B:/Dev/SMR/SMR-BugFixPack-TestKit/Code/80_AgentSlots.lua` is the staged
`tests/80_AgentSlots_depot.lua.txt` followed by `tests/80_AgentSlots_revision.lua.txt`
from `tools/devmods/elevator_station/`, with an active header. Nothing arms at load.
The dev mod and TestKit junctions point at these working trees. Mars.exe was closed
before writing the installed code.

| Slot | Action |
|---|---|
| 1 | Prepare Import needs, then run to the down departure at Ultra |
| 2 | Run to next cabin arrival at Ultra |
| 3 / Scratch | Read selected half and twin: capacity, cargo, upgrade, trains, art |
| 4 | Prepare Export needs, then run to the up departure at Ultra |
| 5 | Replace old run; finish selected depot upgrade/train, otherwise watch one hour |
| 6 | Run to next departure at Ultra |

Each run pauses itself. Slot 5 replaces this sitting's old watches, including the
earlier station-row watch; 2 and 6 do likewise. A save or map change disarms a run:
pause and re-press its slot. A deadline or new-error result is evidence to inspect,
not a PASS. Upgrade/train waits have a six-game-hour deadline.

Slots 1/4 are explicit, tainted fixture setup: **Save B first**. They replace Metals
and Concrete stocks and cabin cargo, set other rows to Not accepted and turn Drone
Access off. They require a working pair, the surface selected, and no reservation
on the fixture resources. A reservation refusal makes no changes: run the next
arrival, pause and retry. Before/after and removed cargo are logged. Slot 3 uses
raw resource amounts (250000 means 250); arrival/departure watches use tenths
(2500 means 250). No owner console typing is needed.

## Smoke A — orphan rests, replacement resumes

1. Start the game, load the paired fixture, pause and **Save B**. Open Slots & notes.
2. Order salvage on the surface half. Select the surviving underground depot,
   pause and press **5**. It runs at Ultra and pauses after an hour without a twin.
3. Watch that cabin resting at its landing; press **3**. Expect `twin=none`,
   `art_moving=false`, `art_settled=true` and `art_changes=0` in the hour result.
4. Place and complete a new surface half. Selected → Quick build may complete the
   construction site. Select the completed half and press **6**.
5. After departure, press **5** and watch the cabin during that hour. At the pause,
   press **3**, then **Flush + copy**. A cycling orphan or a stationary paired cabin fails A.

## Smoke B — destination need, both directions

1. Pause on the surface depot and press **1**. It stocks both source rows to 250,
   leaves Concrete at 240 underground and Metals empty, then pauses at departure.
   Expect down cargo **250 Metals, 0 Concrete**: the empty row wins.
2. Press **2**. At arrival, underground Metals is at most 250; Concrete remains
   at most 250 (normally 240). Competing trains can change stock; use the captured
   departure/arrival readings, not just a later infopanel.
3. With the surface selected and paused, press **4**. It prepares the mirror Export
   fixture and pauses on the up leg. Expect **250 Metals, 0 Concrete** aboard.
4. Press **2**. Expect surface Metals at most 250 and Concrete at most 250.
5. Press **3**, then **Flush + copy**. Taking nearly-full Concrete ahead of empty
   Metals or overfilling either destination fails B. Keep these reads for OI-38.

## Smoke C — capacity and its purchase

1. Pause, select either half and press **3**: cabin 250, storage 250000; resource
   rows show capacity 250. The twin dump must agree, even with Capacity Network on.
2. Hover **Expanded Depot** in the first upgrade slot: verify **10 Metals and
   10 Concrete**, then order it. Use a half within drone range with those materials
   available; construction service works with Drone Access off.
3. Press **5**. Expect `upgrade_complete`; a deadline records an unfinished order.
4. Press **3**, open the other half's panel and press **3** there. Expect cabin 500,
   storage 500000 on both, rows showing 500, and the same purchase already built.
5. Return to the surface, pause and press **1**. At departure expect **500 Metals**
   aboard. **Flush + copy**. A second charge, hub doubling to 1000 or only one half
   reaching 500 fails C.

## Smoke D — a depot builds and assigns its train

1. Select the surface depot connected directly to the serving hub, within drone
   range with Metals/Electronics available. Verify **Construct Train** and
   **Send out Train** are present. Click Construct Train once while paused.
2. Press **5**. Expect `train_complete`, a smaller construction queue and either
   an available train or an increased `line_trains` reading.
3. If the train remains available, click **Send out Train**, then the depot's
   connected track. If it already joined that sole eligible line automatically,
   check it there; that is vanilla's successful assignment path.
4. Repeat the build/run/assignment on the underground half. Both panels must offer
   the native controls; a disabled Send out Train with no spare train is expected.
5. Press **3**, **Flush + copy**, then **Load B** to discard this smoke's fixture
   changes. Missing controls, a construction error or failure to join the line
   leaves D open.

## Close-out

The new depot icon is separate follow-on work, already recorded in spec §11.
The four behavior items await this smoke; the older A/B/C results remain passed.
The shared TestKit's other working changes are outside this diff and stay local.

TestKit sitting commit: `7c3781b` (local only, per `tools/SMRTK.md`). Installed slot
bytes matched the staged composition by assertion; SHA-256:
`96e51d423e8f9961ce5b1ec1f2bd48553a16bc38872c18ab47791fdcd7d6aaff`.
`python tools/doccheck.py` was GREEN after that commit. Its remaining warnings,
verbatim, reconcile with `git -C B:/Dev/SMR/SMR-BugFixPack-TestKit status --short`:

```text
  WARN  M Code/70_SMRTK_Core.lua
  WARN  M Code/72_SMRTK_World.lua
  WARN  M Code/74_SMRTK_Agent.lua
  WARN  M Code/76_SMRTK_Kit.lua
  WARN  M ONBOARDING.md
  WARN  M README.md
```

The SMRTK `rg` gates for `NetSyncEvent|LogCheatUsed` and `^\s*print\(` over
`7*_SMRTK*.lua` plus `80_AgentSlots.lua` each returned no matches (exit 1).
The positive installed-source control, `rg -n -F 'local T = SMRTK'` on the loaded
slot file, found its base and overlay at lines 11 and 264. `doccheck`'s temporary
probe sweep was clean. No runtime PASS is claimed for the new sitting.

## Sitting (2026-10-02, guided by the orchestrator)

Log `Mars.exe-20261002-12.28.11-6aba6e65.log`, read on each "flushed"; "LUA ERROR" count 0.
Desk at `000b498`: every `tools/devmods/*/tests/*_smoke.py` by exit code, 30 files = 28 PASS +
2 FAIL (`train_hub/tests/cargo_slots_smoke.py`, `distribution_slots_smoke.py`, both "attempt to
index a boolean value"; not depot code, routed to the audit). SMRTK Load A refused (`foreign
session`); the owner loaded the fixture directly and Save B succeeded first.

- **Smoke A: PASS.** Orphan hour on 9041: `orphan=true art_moving=false art_settled=true
  art_changes=0`. New surface 10908 paired, the cabin ran down then up, the paired watch ended
  `art_moving=true`.
- **Smoke B: PASS**, after a fixture workaround. Slot 1 first refused twice (`Metals or Concrete is
  reserved by a carrier`), once right after a cabin arrival, so the reservations were the line's
  trains; **the owner turned the underground ordinary station off**, and slot 1 then ran. Down leg:
  surface 250/250, underground Concrete 240 and Metals 0, loaded `Metals=250000` only; arrival
  underground Metals 250, Concrete 240. Up leg (slot 4): loaded `Metals=250000` only; arrival surface
  Metals 250, Concrete 240. No destination overfilled. The reservation refusal on a busy line is a
  slot papercut, not a depot defect.
- **Smoke C: PASS.** Before: both halves `cabin_capacity=250 storage=250000 cost_metals=10000
  cost_concrete=10000 upgrade=false`. Slot 5 `verdict=upgrade_complete` on surface 10908; the
  underground 9041 then read `upgrade=true cabin_capacity=500 storage=500000`, never 1000. At 500
  the down leg loaded `Metals=500000` (slot 1) and the up leg `Metals=500000` (slot 4). Charged once
  in the owner's word: *"just once"*.
- **Smoke D: PASS in the owner's word.** *"Done trains constructed and could add them to the
  line"*, on both halves. The log holds no `train_complete` reading: slot 3 refused four presses
  with `pause first`, and slot 5 was not pressed.

**Brief 30 closed on this sitting** (orchestrator, 2026-10-02). Open papercuts, not depot defects:
slots 1/4 refuse while the line's trains hold reservations (the owner switched the underground
station off to run B); the two failing hub slot smokes above.
