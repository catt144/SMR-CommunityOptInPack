# The crossing witness — brief 33, 2026-10-02

Authority: [brief 33](../prompts/Train_Hub_Project/33_TESTKIT_CROSSING_WITNESS_high.md), from the
orchestrator's owner-authorised sweep (2026-09-28). Code and desk evidence: `c06349e`, then v2 at
`75d1f88` after the first attended check. Peer commits in between touch none of these paths.
Installed build read by `python tools/doccheck.py --emit-fingerprint`: **25579348**. Game source is
cited from `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`. Executed model: Opus 5.5
(`claude-opus-5-5`).

**Outcome:** a witness the final battery can rest its crossing verdicts on. Desk smoke: PASS, and it
can fail. Attended check 1 (2026-10-02): the wiring and the save passed; the verdicts were blocked
by a witness defect, fixed in v2. **Attended check 2 (2026-10-02, v2): PASS.** Both crossings were
proved (net), and the controls named a real cargo duplication (see "Attended check 2"). Stop 1 does not fire:
the witness separates train transfers from drone, cabin and autosave stock changes exactly, by
bracketing the transfer calls.

## What a crossing verdict proves now (the call)

**Both crossings, as two separate verdicts.** Spec §11 moved cargo between maps onto the Elevator
Depot (trains never change maps; the cabin carries cargo), and the hub still joins lines on one map.
These are different transfers, which audit `TRAIN_AUDIT_20261002.md` §2 already requires the
witness to tell apart. Brief 35 rests "Hub logistics: cross-route cargo" on slot 8 and
"Elevator Depot: cargo crosses" on slot 9.

**Each verdict has two bounds and names the one that proved it** (`bound=strict|net`).

- **Strict:** the take exceeds every non-crossing source *including the starting stock*.
  - **Hub route-to-route**, per hub and resource. Route B's trains loaded more at the hub than
    every source except another route's trains could supply:
    `out[B] > stock0 + other_in + drone_in + cabin_in + in[B] + in[unknown route]`.
  - **Depot map-to-map**, per direction and resource. Two links must both hold:
    - at the origin half: `cabin_out > stock0 + other_in + drone_in + cabin_in`;
    - at the destination half: `sum(train_out) > stock0 + other_in + drone_in + sum(train_in)`.
- **Net:** a stocked station can never clear the strict bound. Attended check 1's hubs held about
  2000 of every resource. The net bound comes from the conservation identity at the station,
  `out[B] − in[B] = Σ other routes (in − out) + nontrain_net − (stock − stock0)`:
  - hub: `(out[B] − in[B]) − drawdown − max(nontrain_net, 0) − max(in[?] − out[?], 0) > 0`;
  - link 1: `(cabin_out − cabin_in) − drawdown − max(other_net + drone_net, 0) > 0`;
  - link 2: `(Σ train_out − Σ train_in) − drawdown − max(other_net + drone_net, 0) > 0`;
  - where `drawdown = max(stock0 − stock, 0)`.

  A positive net excess is a lower bound on the *other routes'* (or the cabin's, or the trains')
  net delivery that the take matched. Cargo crossed as a net flow, not drawn from the starting stock.

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
- The rule `out > other_in + own_in` ignored the hub's stock at arm. Desk case H2 shows it calling
  40 crossed where at most 20 did.

## The witness

The witness is `tools/devmods/train_hub/tests/80_AgentSlots_crossing.lua.txt`, an overlay binding
slots 7-10 only.

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

The smoke pins each of these source facts and fails if one changes. A drone load sleeps in its
presentation (`MultiResourceDepot.lua:192-199`), so drone brackets hold no nesting counter across
that yield. Train and cabin brackets do not yield.

**Saves.** The wrappers stay installed and keep recording while a run is disarmed. A save, an
autosave or Ultra therefore costs polls only. Stock moved outside any bracket is booked `other`,
which can only raise the bar.

**Controls:**

- `train_mismatch` (a train's own cargo change against the station's) and `cabin_mismatch` (cabin
  cargo against both halves) **taint** their station and resource. No verdict uses a tainted
  resource. The first eight mismatches are logged with the call, train, both deltas, stock and
  capacity (`crossing_mismatch` DUMP lines).
- `stuck` counts brackets a poll found open.
- Wiring completeness.
- `controls_ok` is true only with all of these zero.

**Limit.** At one station, "other" flows of opposite sign inside one checkpoint gap net against
each other. A gap is at most 250 game ms with no bracketed event there.

**Names.** `HUB_CLASSES` and `DEPOT_MODULES` are the only names the witness looks up.
`SMRElevatorDepot`, brief 34's proposed rename (`TRAIN_MOVE_CHECKPOINT_20261002.md`), is already
listed before the dev name. A miss reports unwired; it never passes silently.

## Desk evidence

`python tools/devmods/train_hub/tests/crossing_witness_smoke.py` at `75d1f88`: exit 0. Transfers run
through the archived vanilla `Train.lua` bodies and the hub dev mod's real `UnloadAll`/`TransferCargo`.

**Hub cases:**

- **PASS cases:**
  - H1: pass-through and unassigned cargo is booked to R1; R2 crosses 25, strict.
  - H2: starting stock 50, A delivers 20, B takes 40. Strict refuses (−10); net proves 20.
  - N1: a hub holding 400, A 30, B 25: net 25.
  - H5: Ultra with no polls, 13 events, 15.
  - H6: a save while blind; an unexplained +7 is booked `other_in`, and 20 cross.
  - H7: the real `TransferCargo` path is booked to R2.
  - Y1: a drone load yields mid-call while a poll and a train unload run. `stuck=0`, strict 15,
    net 20.
- **FAIL (counterexample) cases:**
  - N2: pure drawdown.
  - H3: a route reloading its own delivery, until it takes 5 more.
  - H4: drone stock.
- **Controls:**
  - H8: a train load the train never receives taints the hub's Metals. No verdict; the mismatch
    line names `LoadResourceForStation`, train 0, station −10.
  - A loaded save ends the books.

**Depot cases:**

- D1: down-crossing, strict, both links 30.
- D3: a stocked destination: strict refuses, net proves 30.
- D2: refused when link 1 is missing.
- D3n: refused when link 2 is pure drawdown.
- D4: a leaking cabin gives `cabin_mismatch=30`, two halves tainted.

**Eight mutations rejected**, each at its intended assertion:

- the entry checkpoint removed;
- starting stock removed from the strict bar;
- the route's own unloads removed;
- drone stock removed;
- the cabin left unwrapped;
- the 2026-09-18 assigned-only rule;
- the net bound without drawdown;
- a drone bracket held open across its yield.

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
- Every `tools/devmods/*/tests/*_smoke.py`, by exit code at `75d1f88`: **31 = 3 elevator + 28 hub,
  all exit 0**.

**Ruled out:** a fixture slot cannot feed a depot crossing proof. Its stock is written directly,
so it is booked `other` and link 1 cannot pass on it. A depot crossing needs trains to deliver to
the origin half.

## Attended check 1 (2026-10-02, TestKit `8837c4b`)

Log `%APPDATA%/Surviving Mars Relaunched/logs/Mars.exe-20261002-14.39.26-6aba6e65.log`, lines
321-619, read after the owner's "flushed".

| Step | Result |
|---|---|
| 1 Wiring | **PASS**. `wiring_ok=true trains=17 trains_wired=17 watched=4 watched_wired=4 hubs=2 cabin_wired=true depot_pair=true` (line 336) |
| 2 Hub | **BLOCKED.** `verdict=control_broken stuck=1 train_mismatch=0` after 141 polls (line 357) |
| 3 Depot | **BLOCKED.** Three presses, each `control_broken` at once (`stuck=2`; lines 374, 392, 477). The last also had `train_mismatch=2` |
| 4 Save | **PASS**. `rearms=3 blind_ms=191010`, with `train_events` 30 → 291 and the ledger kept (line 477) |
| 5 Read | **PASS** as a read. `controls_ok=false hub_verdict=none depot_verdict=none` |

**What blocked steps 2 and 3:**

- **`stuck`.** The drone bracket held the nesting counter across the load presentation's `Sleep`.
  The poll reset it, and the bracket then closed to −1. The counter was cumulative, so every
  re-arm fired at once.
- **`train_mismatch=2`.** Unlocalized: v1 logged no details. The underground half's WasteRock stood
  at 250/250, the one full row.

**What the ledger itself showed.** Every row reconciles: for example, surface Concrete
24 + 53 delivered − 77 cabin = 0. Two further points:

- **The strict hub bound could not be cleared:** hub 6430's starting stock was 1993 Concrete and
  3974 Metals. Its Metals came in 79 on R6 and went out 52 on R1 while stock rose 24. The net bound
  proves 52.
- **No depot crossing occurred in the window:**
  - Link 1 held (surface Concrete: 53 train-delivered, cabin took 77).
  - Underground trains on R5 *delivered* to the underground half (WasteRock 157) and took almost
    nothing away.
  - Under the net bound, Herbs would have shown link 1 = 1 and link 2 = 3.

Both blockers are fixed in v2 (`75d1f88`), and the stocked-hub gap gets the net bound.

## Handoff

- **Brief 34:** if the move renames the hub class or the depot module, extend `HUB_CLASSES` /
  `DEPOT_MODULES`. Repoint `crossing_witness_smoke.py`'s `source_checks` (dev-mod paths,
  `local D = SMRElevatorDepotDev`) and its runtime file list at the moved files.
- **Brief 35:**
  - Load `80_AgentSlots_depot.lua.txt` + `80_AgentSlots_revision.lua.txt` +
    `80_AgentSlots_crossing.lua.txt` (as installed for this check).
  - Run slot 7 before any crossing reading.
  - Quote each verdict with its bound and controls.
  - Any `crossing_mismatch` line is a finding to explain.

## Attended check 2 (predictions written before boot; result below)

**Result, 2026-10-02.** Log `Mars.exe-20261002-15.30.19-6aba6e65.log` (save "Double Hub+elev Built
Under2", sol 51, `pack_version=26`, fix pack present 45/45). No `LUA ERROR`.

| Step | Result |
|---|---|
| 1 Wiring | **PASS** as predicted (line 340) |
| 2 Hub | **PASS**. `verdict=proved bound=net crossing=hub`: hub 6430 Concrete on R1, `crossed_at_least=4` at the pause and 8 at the read; `stuck=0` (line 370) |
| 3 Depot | **PASS**. `verdict=proved bound=net crossing=depot_down`, Herbs, link 1 = 1 and link 2 = 3; `stuck=0` (line 396) |
| 4 Save | Not repeated. The save path is unchanged from v1, which passed it in check 1 |
| 5 Read | **PASS**. Both verdicts as found, `stuck=0`, `cabin_mismatch=0`; `controls_ok=false` only for the finding below (owner's paste) |

**Finding: one unit of cargo appears from nothing on an unload.** Two `crossing_mismatch` lines,
the same train and call (`Train(2000002659)`, `UnloadAll` at hub 6430 on R1, game time 35860002):

- Food: train −12, hub +13.
- Sugar: train −16, hub +17.

Only food resources are affected, one unit each. The witness tainted both rows and no verdict used
them.

Hypothesis, unconfirmed: the train's food cargo spoiled in transit, which lowered its
`stockpiled_amount` but not its `assigned_resources`. Vanilla `UnloadAll` then credits the station
with the whole assigned amount (`unload_cargo`, `Train.lua:779-783`). This is outside brief 33's
scope (hub, depot and vanilla code). It is routed to the orchestrator as a defect to brief, and as
a control brief 35 will see again.
 Installed as TestKit `69d5af6` (built at pack `7870319`; kit gates clean). The write landed while a new Mars.exe was booting: run this check in a game started after that commit.

**Fixture.** The same colony as check 1, or any with:

- a hub joining two routes that move one resource;
- a depot pair whose rows send a resource that one map's trains deliver and the other map's trains
  carry away.

Slots 1-6 and Scratch are brief 30's depot slots; 7-10 are the witness. Normal time is up to 2 game
hours per run at Ultra; each run stops itself at 12 game hours (`deadline`).

1. Pause, then press **slot 7, "Crossing witness: start the ledger + wiring proof"**. Expected as
   in check 1: `wiring_ok=true`, `trains_wired` = `trains`, `watched_wired` = `watched`,
   `cabin_wired=true`, `depot_pair=true`.
2. Press **slot 8, "Run until a hub route-to-route crossing is proved"**. It pauses with:
   - `verdict=proved crossing=hub` and `bound=net` (check 1's stocked hubs; `strict` only on a
     near-empty one);
   - `crossed_at_least` > 0, and `stuck=0`.

   Check 1's flows predict hub 6430 Metals or Concrete within check 1's own window (`elapsed_ms` 227010).
3. Press **slot 9, "Run until a depot map-to-map crossing is proved"**. It pauses with:
   - `verdict=proved`, `crossing=depot_down` or `depot_up`;
   - both link values > 0, and `stuck=0`.

   A `deadline` with `train_events` > 0 means no resource was both delivered on one map and taken
   on the other. That is a fixture gap, not a witness pass or fail.
4. Press **Save A**, then re-press slot 8 or 9. Expected: `rearms` one higher, `blind_ms` > 0, and
   the ledger kept.
5. Pause, then press **slot 10, "Read the crossing ledger"**. Expected:
   - `hub_verdict` and `depot_verdict` as found;
   - `stuck=0`;
   - per-row `hub_net_excess` and the `_net` link values.

   If `train_mismatch` > 0, the `crossing_mismatch` lines name the call and the row; it taints only
   that row. Negative control in the same read: a resource the hub only loses to spoilage shows a
   negative `hub_net_excess` (check 1: Bread −842 strict).

**Optional, brief 30's papercut.** On a busy line, Save B and select the surface half. Press
**slot 1**. Expected:

- no refusal, and a `reserved=` field;
- the departure run the slot arms pauses with `aboard_Metals = expected_metals / 100` (tenths
  against raw), and the same for Concrete.
