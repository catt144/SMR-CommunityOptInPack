# The crossing witness — brief 33, 2026-10-02

Authority: [brief 33](../prompts/Train_Hub_Project/33_TESTKIT_CROSSING_WITNESS_high.md), from the
orchestrator's owner-authorised sweep (2026-09-28). Code and desk evidence: `c06349e`, authored on
`27cc842`..`a199e3c` (peer commits `43f4c0e`, `a199e3c` touch none of these paths). Installed build
read by `python tools/doccheck.py --emit-fingerprint`: **25579348**. Game source is cited from
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`. Executed model: Opus 5.5 (`claude-opus-5-5`).

**Outcome:** a witness the final battery can rest its crossing verdicts on. Desk smoke: PASS, and it
can fail. The attended check below is still to run. Stop 1 does not fire, because the new witness separates train
transfers from drone, cabin and autosave stock changes exactly, by bracketing the transfer calls.

## What a crossing verdict proves now (the call)

**Both crossings, as two separate verdicts.** Spec §11 moved cargo between maps onto the Elevator
Depot (trains never change maps; the cabin carries cargo), and the hub still joins lines on one map.
These are different transfers, which audit `TRAIN_AUDIT_20261002.md` §2 already requires the
witness to tell apart. Brief 35 rests "Hub logistics: cross-route cargo" on slot 8 and
"Elevator Depot: cargo crosses" on slot 9.

- **Hub route-to-route**, per hub and resource. Route B's trains loaded more at the hub than
  every source except another route's trains could supply:
  `out[B] > stock0 + other_in + drone_in + cabin_in + in[B] + in[unknown route]`.
- **Depot map-to-map**, per direction and resource. Two links must both hold:
  - At the origin half, the cabin took more than non-train sources could supply:
    `cabin_out > stock0 + other_in + drone_in + cabin_in`.
  - At the destination half, its trains loaded more than non-cabin sources could supply:
    `sum(train_out) > stock0 + other_in + drone_in + sum(train_in)`.

Each excess is a lower bound on the crossed units. Under the old rule, a timeout was taken as no
crossing. Here a timeout is `verdict=deadline`, with event counts, so a run without train visits
cannot read as a refusal.

## Why the 2026-09-18 witness could not prove one

It lived in TestKit `adda373`'s `80_AgentSlots.lua` (since overwritten) and polled each train's
`assigned_resources[hub]` for a fall to zero. Three leaks:

- Vanilla `Train:UnloadAll` also unloads cargo assigned to *other* stations, and cargo with no
  assignment, at every stop (`Lua/Units/Train.lua:787-831`). Those unloads were booked `other_in`,
  which explains `other_in=74` against `train_in R1=71`.
- A train whose route table no longer matched the arm-time list was skipped (`if r and ...`).
- The rule `out > other_in + own_in` ignored the hub's stock at arm. The desk counterexample H2
  shows it calling a crossing that never happened.

## The witness

The witness is `tools/devmods/train_hub/tests/80_AgentSlots_crossing.lua.txt` (SHA-256
`669de93b…a02`), an overlay binding slots 7-10 only.

**The brackets.** It wraps these calls on every class that resolves to them, at arm time:

- the train's `UnloadAll` and `LoadResourceForStation`;
- the station's `DroneUnloadResource` and `DroneLoadResource`;
- the depot module's `Tick`.

Following EF-058, slot 7 proves the wiring off live trains and stations. Each bracket checkpoints
the watched stations' stock (every hub and both depot halves, on both maps) on entry and on exit.
The entry gap is booked `other`, and the bracket's own delta goes to its category. These are the
only stock writers:

| Writer | Where it writes station stock (1.1.1.406343 unless noted) |
|---|---|
| Train | `LoadResourceForStation` and `unload_cargo` (`Train.lua:744-831`) |
| Drone | `Station.lua:662-688`, `MultiResourceDepot.lua:201-215` |
| Cabin | Only inside the depot module's `Tick` (`deliver`/`load_cabin`) |
| The hub's own construction jobs | Outflows only (`20_TrainHub.lua:2745-2764`) |

The smoke pins each of these source facts and fails if one changes.

**Saves.** The wrappers stay installed and keep recording while a run is disarmed. A save, an
autosave or Ultra therefore costs polls only. Stock moved outside any bracket is booked `other`,
which can only raise the bar.

**Controls.** A broken control ends a run as `control_broken`, never as a proof:

- `train_mismatch`: the train's own cargo change against the station's;
- `cabin_mismatch`: cabin cargo against both halves;
- `stuck`: a bracket that never closed;
- wiring completeness.

**Limit.** At one station, "other" flows of opposite sign inside one checkpoint gap net against
each other. A gap is at most 250 game ms with no bracketed event there.

**Names.** `HUB_CLASSES` and `DEPOT_MODULES` are the only names the witness looks up.
`SMRElevatorDepot`, brief 34's proposed rename (`TRAIN_MOVE_CHECKPOINT_20261002.md`), is already
listed before the dev name. A miss reports unwired; it never passes silently.

## Desk evidence

`python tools/devmods/train_hub/tests/crossing_witness_smoke.py` at `c06349e`: exit 0. Transfers
run through the archived vanilla `Train.lua` bodies and the hub dev mod's real `UnloadAll`/`TransferCargo`.

**Hub cases:**

- **PASS cases:**
  - H1: pass-through and unassigned cargo is booked to R1, and R2 crosses 25.
  - H5: Ultra with no polls, 13 events, crosses 15.
  - H6: a save while blind; an unexplained +7 is booked `other_in`, the bar rises, and 20 cross.
  - H7: the real `TransferCargo` path is booked to R2.
- **FAIL (counterexample) cases:**
  - H2: starting stock.
  - H3: a route reloading its own delivery, until it takes 5 more.
  - H4: drone stock.
- **Controls:**
  - H8: a train load the train never receives gives `control_broken`, `train_mismatch=10`.
  - A loaded save ends the books.

**Depot cases:**

- D1: down-crossing proved, both links 30.
- D2: refused when link 1 is missing.
- D3: refused when link 2 is missing.
- D4: a leaking cabin gives `cabin_mismatch=30`.

**Six mutations rejected**, each at its intended assertion:

- the entry checkpoint removed;
- starting stock removed from the bar;
- the route's own unloads removed;
- drone stock removed;
- the cabin left unwrapped;
- the 2026-09-18 assigned-only rule.

The cabin in this smoke is a stand-in with the real module's shape.

**Not tested at the desk:** the engine's class flattening, trigger threads, real drones, real saves
and the real cabin. The attended check covers them.

**Carried from the audit (§7) and brief 30:**

- `cargo_slots_smoke.py` and `distribution_slots_smoke.py` now read
  `80_AgentSlots_upgrades.lua.txt`, a byte copy of TestKit `587f474`'s slots (SHA-256
  `58af931e…3c04`; the only kit version carrying all three markers they test). They no longer
  read the shared kit's live file, and both exit 0.
- **Brief 30's papercut.** Depot fixture slots 1/4 (`80_AgentSlots_revision.lua.txt`) no longer
  refuse while carriers hold reservations. They never take stock promised to a carrier and never
  fill room promised to one. They log `reserved=` (origin out/in, destination out/in, raw) and
  predict the cabin's load from what is left. `revision_smoke.py` checks that prediction (220 / 10
  under a reservation) against the real depot `load_cabin`.
- Every `tools/devmods/*/tests/*_smoke.py`, by exit code: **31 = 3 elevator + 28 hub, all exit 0**.

**Ruled out:** a fixture slot cannot feed a depot crossing proof. Its stock is written directly,
so it is booked `other` and link 1 cannot pass on it. A depot crossing needs trains to deliver to
the origin half.

## Handoff

- **Brief 34:** if the move renames the hub class or the depot module, extend `HUB_CLASSES` /
  `DEPOT_MODULES`. Repoint `crossing_witness_smoke.py`'s `source_checks` (dev-mod paths,
  `local D = SMRElevatorDepotDev`) and its runtime file list at the moved files.
- **Brief 35:**
  - Load `80_AgentSlots_depot.lua.txt` + `80_AgentSlots_revision.lua.txt` +
    `80_AgentSlots_crossing.lua.txt` (as installed for this check).
  - Run slot 7 before any crossing reading.
  - Quote each verdict with its controls.

## The attended check (preloaded; predictions written before boot)

Installed as TestKit `8837c4b` (`Code/80_AgentSlots.lua`, built from the staged files at pack `4433c2f`; kit gates clean).

**Fixture.** The owner's colony needs:

- a hub with at least two routes moving one resource across it;
- a depot pair whose rows send a resource that surface trains deliver and underground trains carry
  away (or the reverse).

Slots 1-6 and Scratch are brief 30's depot slots; 7-10 are the witness.
`<<PENDING-RUN>>` until the owner runs it. Normal time is up to 2 game hours per run at Ultra. Each
run stops itself at 12 game hours (`deadline`).

1. Pause, then press **slot 7, "Crossing witness: start the ledger + wiring proof"**. Expected:
   - `wiring_ok=true`, `trains_wired` = `trains`, `watched_wired` = `watched`, `hubs` ≥ 1;
   - `depot_module=SMRElevatorDepotDev`, `cabin_wired=true`, `depot_pair=true`;
   - one `crossing_watch` DUMP line per watched station.
2. Press **slot 8, "Run until a hub route-to-route crossing is proved"**. It pauses with:
   - `verdict=proved`, `crossing=hub`, a `resource`, a `route` `Rn` and its `route_path`;
   - `crossed_at_least` > 0;
   - `train_mismatch=0 cabin_mismatch=0 stuck=0`.

   If an autosave interrupts the run, re-press slot 8: `rearms` ≥ 1, and the ledger is kept.
3. Press **slot 9, "Run until a depot map-to-map crossing is proved"**. It pauses with:
   - `verdict=proved`, `crossing=depot_down` or `depot_up`;
   - `cabin_took_train_cargo` > 0 and `trains_took_cabin_cargo` > 0;
   - `cabin_events` > 0, both mismatches 0.

   A `deadline` result with `train_events` > 0 means the rows moved nothing that trains delivered.
   That is a fixture gap, not a witness pass or fail.
4. Press **Save A**, then re-press slot 8 or 9. Expected: `rearms` one higher, `blind_ms` > 0,
   `train_events` still counting from step 1 (no reset).
5. Pause, then press **slot 10, "Read the crossing ledger"**. Expected:
   - `hub_verdict` and `depot_verdict` as found in steps 2-3;
   - `controls_ok=true`;
   - `crossing_route` and `crossing_ledger` DUMP lines.

   Negative control in the same read: a resource the hub receives from only one route shows
   `hub_excess` ≤ 0.

**Optional, brief 30's papercut.** On a busy line, Save B and select the surface half. Press
**slot 1**. Expected:

- no refusal, and a `reserved=` field;
- the departure run the slot arms pauses with `aboard_Metals = expected_metals / 100` (tenths
  against raw), and the same for Concrete.
