# 35 — The final full battery on the shipping layout (attended test)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/35_FINAL_BATTERY_high.md` in a fresh
session rooted at `B:\Dev\SMR\SMR-OptInPack`, **now**: 33, 34, 34b and 34c closed 2026-10-02. Reasoning: high
(a full prediction battery across modules and configurations).

## Authority and outcome

The owner, 2026-09-19: a design pass gets a smoke; **the full prediction battery runs once, on the
final build** (spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §10). `FIX_POLICY` §8:
the complete shipping test runs **with the Relaunched Fix Pack installed and with it absent**, and
§0 defines the toggle test for content; both toggle directions. Outcome: one battery script, run
with the owner, whose verdicts decide whether the train project is complete. Done when every
module the owner keeps has passed in both configurations and both toggle directions, or the owner
has parked or cut it; the report names the released fix-pack version tested.

**Owner rulings, 2026-10-03.**

- **The fix-pack-absent (A) configuration is waived.** See `FIX_POLICY` §8 and
  `TRAIN_FIXPACK_OVERLAP_20261003.md`. Run the P configuration only.
- **F65's case is accepted as vanilla.** Without the fix pack, a station on 1-2 pieces of track
  from a hub does not share its power. Do not predict otherwise.
- **Trim the P batteries to what has never been seen live.** The owner, on the remaining batches:
  *"most of this has been witness as working in a dozen or more runs during build and testing"*.
  These already passed live: B0 in P (2026-10-03), the crossings (brief 33, check 2), Export rows
  and the hub refusal (34b, sittings 1-2), the modules loading from this mod (brief 34), and the
  quiet log. Put the never-witnessed items to the orchestrator (OI-38's up-leg read at least)
  before issuing more batches.
- **B0 in P also passed the quiet complete log**: `Mars.exe-20261003-01.04.09` ended at
  `Debug::Done()` with only 6 once-per-load train lines and 0 repeating lines, across 3 bounded
  hours and every module toggle.
- **The console opens only inside a loaded game**, not at the main menu (owner, 2026-10-03). To
  load the fixture copy, load any save, then run `*r LoadGame("FINAL35_P_20261002.savegame.sav")`.
- **The B1-B6 witness review is ruled** (report `TRAIN_FINAL_BATTERY_20261002.md`, grep
  `remaining witness review`). **B1** (OI-38's up-leg read) is approved: run its five-step batch.
  **B3** and **B6** are cleared on the owner's witness: tested during hub design, B3 for the
  elevator too. **B5** is skipped (*"pretty minor if its just a notification"*). **B2** keeps only
  full-mod removal restoring vanilla requests. **B4** keeps only upgrades through zero hubs, then
  a replacement, and over-capacity stock after OFF. The owner struck the other B2 and B4 items on
  the orchestrator's recommendation, spoilage with TrainHub OFF included. **The battery is B1,
  then those three checks.**
- **Rows forced on.** With TrainHub ON and StationRows OFF, slot 11 still showed StationRows
  `inactive` although the rows worked. Explain the forced-on mechanism in the report.

## What the battery carries

- Each module's predictions from its spec sections (§4.7, §4.8, §4.10, §10, §11; §4.9 is rejected design, record only) and its build reports,
  restated for the shipping layout from brief `34`. Treat predictions written before 2026-09-28 as
  possibly stale: re-derive them.
- Every in-game check the audit (`docs/agent/reports/TRAIN_AUDIT_20261002.md` §2) says the smokes miss.
- The crossing verdicts on brief `33`'s witness.
- OI-38's last step on `docs/PLAYTEST_CHECKLIST.md`: the scripted up-leg read (the train
  stream, then the up-leg read with an Export row; slot numbers from the current `80_AgentSlots.lua`), on the final up-leg loading.
- No train ever appears in the hub (spec §4.8 ruling 10, grep `no train ever`): brief 34b cut
  auto-fill and made the hub refuse add-train. Trains are added at a station. Check it once.
- 34b's results (report `TRAIN_34B_PLAN_20261002.md`): Export rows keep each depot's Desired Amount
  through the FindTask pairing filter, with no reverse block; the hub refuses add-train. Its STREAM
  slot and cargo trap stay preloaded for reuse.
- **A quiet log** (`FIX_POLICY` §8, grep `development diagnostics`): with `SMROptInPack.TrainTrace`
  off (the default), the log holds no repeating train trace lines (`5ad1ff3`). A check that reads a
  refusal, pair or cabin line sets the switch first.
- **Movement is finished** (owner, 2026-09-21). It may reopen once, here, if the owner wants moves
  tweaked; that goes to `Parked/TRAIN_HUB_MOVE_high.md`, never as a gate.

## Method

`git log --oneline -5` and `git pull` first; authored at `58ebf7e`+. Keep a work list (the todo
tool if the session has one, else in the report). Preload SMRTK slots (`tools/SMRTK.md`): the owner clicks, they do not type, and each
hand-typed console line needs a stated reason no slot covers it. About five steps a batch,
predictions beside each, hubs named by role. Slot bindings change each sitting: read the current
`80_AgentSlots.lua`. An autosave disarms a watch, and the owner re-presses the slot. The orchestrator guides the owner and
reads the log on each "flushed". Apply `docs/agent/WORKFLOW.md`'s test-design rules. A failure is a
recorded verdict and a routed fix, not a retry for a preferred result. References: `CLAUDE.md`,
`docs/agent/FIX_POLICY.md`; skills `doc-editing`, `smr-bug-library`.

## Scope

In: testing and recording. Out: fixes (each failure goes to the orchestrator for a brief).

## Stops

1. A module cannot be tested in one configuration (for example, the fix pack will not load): report
   which, and what the owner must decide.

## Lifecycle

One-off. When the battery passes, the orchestrator deletes the whole `Train_Hub_Project/` folder and
its row in `docs/agent/prompts/README.md` in one commit (owner, 2026-09-18).
