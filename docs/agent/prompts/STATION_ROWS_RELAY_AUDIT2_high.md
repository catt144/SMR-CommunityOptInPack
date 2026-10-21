# Station rows relay corrections: the final check pass

One-off. Authored 2026-10-21 at `3aa5402` by Claude Fable 5.1, the model that built the relay
change set and its corrections; run this on a different model, the owner's choice (CLAUDE.md:
execution and audit on different owner-selected models). Delete this file and its row in
`docs/agent/prompts/README.md` in the commit that records your verdict. Start with
`git log --oneline -3` and `git pull`; the gitStatus block in your context is a snapshot.

## Authority

The owner's rulings R1–R7 of 2026-10-21, recorded verbatim in `docs/agent/bugs/D16.md` (R7 beside
R1–R6, ruled by firing the corrections brief over the first audit's A1) and `docs/agent/bugs/D18.md`.
The first independent audit is §16 of `docs/agent/reports/STATION_ROWS_RELAY_20261021.md`; its
five items A1–A5 were built as corrections, recorded in §17. This pass judges those corrections
against §16's own wording and R1–R7, and the whole change set for regressions. It does not reopen
the rulings. The owner fires this prompt; firing it is the owner's action on `OI-54` in
`docs/PLAYTEST_CHECKLIST.md`, so your closing commit deletes that item.

## End state

A written verdict as §18 of the report, in the shape of §16: one verdict line (the change set is
confirmed as desk-verified, or corrections are still needed, each named), then evidence with the
command that produced each finding and its output. Your scripts and outputs archived under
`docs/archive/station_rows_audit2_20261021/`, runnable from the repo root. One line appended to the
build status lines in D16 and D18: `Audited <date> (<executed model, from the transcript>): <verdict>`.
`OI-54` deleted; this prompt deleted with its map row; doccheck GREEN; one commit with a pathspec.
No shipping code changes: a remaining defect is a finding for the owner's next brief. The verdict
makes nothing "tested"; that word waits on the game. A confirmed verdict is what releases v1.0.4
through `release_prompt.md`; say so in one line if you give it.

## What is being audited

The corrections, on top of the build `83149ea` that §16 audited:

| commit | unit |
|---|---|
| `eb1eaf9` | R7 recorded (D16, spec §4.7); A1: in `local_train_view`'s `part()` a member that is not the current station and not in `can_receive` gets no parts and no pool stock; the relay smoke's harness walk takes a per-edge transport mode and section 2c carries the first audit's two A1 fixtures |
| `7c2bc4c` | A2: the splitter is a file-level `water_fill(pool, slots)`, exported as `D.WaterFill`; shares floor (`mul_div_floor`, no bare division) and the remainder goes one unit at a time down the sorted order to slots below their room; room-less and weightless slots are filtered first; relay smoke section 3b |
| `3aa5402` | A3: the click handler and the slider's `OnScroll` call `D.Refresh()` first; A5: `D.Clear` removes the hub's outer table when the last entry goes; A4: the hubless Import/Export help names what the station keeps; the UI smoke carries both seam fixtures, the scroll variant, the A5 check and the A4 clause check |

The diff: `git diff 83149ea 3aa5402 -- Code/ tools/trains/`. The whole change set since the
release: `git diff optin-v1.0.3 3aa5402 -- Code/`. The build's records: §15 (the build), §16 (the
first audit), §17 (the corrections, with the calls made).

## Evidence you would otherwise re-derive

Each line carries its command; re-run before relying on it. Line numbers by `grep -n`.

- The first audit's battery at `3aa5402`: `python docs/archive/station_rows_audit_20261021/baseline.py`
  prints `RECONCILED: 19 commands; 19 passed; 0 failed`. Its one `[TrainHub] transient claim
  failed` line (in `food_stream_smoke.py`'s output) is in the archived `baseline_output.txt` too:
  a harness-caught message inside a passing test, not new.
- The first audit's witnesses against the corrected code:
  `python docs/archive/station_rows_audit_20261021/adversarial.py` now exits 1 at its chunk line
  90, the first A1 `COUNTEREXAMPLE` assertion (stock 30/30/0 after three trips), because that
  result no longer holds; its later witnesses (A2 at chunk line 106, A3, A4) are not reached by
  that script. The shipping smokes carry each as a positive assertion:
  `tools/trains/hub/tests/hubless_relay_smoke.py` sections 2c (A1: 0/60/0 and a 30 load) and 3b
  (A2: 1,1,0; 1667,1667,1666; 600 seeded cases summing to `min(pool, rooms)`);
  `tools/trains/hub/tests/distribution_ui_smoke.py` (A3 leave-hub keeps local Import 70, join-hub
  keeps hub Import 77, the scroll variant; A5 `rawget(h, D.FIELD) == nil` after the last clear;
  A4 no `never` clause beside the joining-station line).
- The relay smoke's walk is a harness double: `track.mode` per track, `track.modes[i]` per edge
  into member i restricting every member beyond, as the native walk does
  (`Lua/TrainTransport.lua:371-447`, 1.1.1.406343, build 25579348 per
  `python tools/doccheck.py --emit-fingerprint`). The first audit's `network()` builder in
  `adversarial.py` runs the native walk over fixture tracks and edges; it is the stronger check
  for A1 and is yours to port or re-run positively.
- The base game counts a station past a people-only leg in its line total and storage
  (`Lua/Units/Train.lua:884-895`) and gates only loading by transport mode (`:920`); R7 departs
  from that on purpose, for the hubless view only.
- doccheck at `3aa5402`: GREEN, `WRAP CHECK: 0 wrap site(s) outside Require`, `TEMPORARY SWEEP:
  0 hit(s)`; `python tools/parsecheck.py` 19 files, 0 errors. The first audit's `contract.py`
  persisted-name token set is the control for the bans.
- Further records: `docs/agent/bugs/INDEX.md`, `docs/agent/facts/INDEX.md`.

## What to judge

Judgment within the authority is yours: which fixtures to port, the order, the harness you
extend. The verdict must answer these, each with evidence:

1. **A1 against R7 and §16.2 A1.** With the native walk: the people-only tail, a leg under
   construction, a non-working station, the current station always in the balance, the pool
   excluding unreachable stock, both §16 fixtures, and the all-cargo control. Does any reachable
   member now lose a share it had, or any unreachable one keep one?
2. **A2 against §16.2 A2.** The first audit's rational oracle search re-run against
   `D.WaterFill`: pool-sum error 0, every slot at or below its room, deviation from the oracle at
   most one internal unit, the same answer on every call; three or more parts, zero rooms,
   held parts, a pool larger than the rooms. Termination with the filter.
3. **A3 against §16.2 A3.** The leave-hub and join-hub seams through the click, the scroll, the
   Ctrl+click broadcast (each destination's own set) and the broadcast-to-disabled path; the
   depot skip; a click while `train_track_routes` is `false`. Is one `D.Refresh()` per click a
   coherent snapshot, and what does it cost on a large colony (`D.Refresh` walks every hub's
   routes; say what you measured or that you did not)?
4. **A4 and A5.** The Import and Export clauses on a joining station against the pass-through
   line and the warning at 100; the hub network's help unchanged. The emptied outer hub table
   removed; nothing else in `SMROptIn_distribution` or `SMROptIn_station_rows` touched; the
   `{mode, percent}` shape unchanged; no new persisted name; no new wrapper (`D.Refresh` in a
   click is a call, not a wrap).
5. **Regressions.** §16.3's table still holds at `3aa5402`; the hub tree (`train_view`,
   `branch_need`, `child_need`, the hub branch of `UnloadAll`) byte-identical to `5ba8f3f`; the
   depot's wiring smoke; the three player cases of §16.4 as qualified there.
6. **The records.** §17, the D16/D18 lines and the outbox entry say what the diff does and no
   more; the status words `tested-attended` not moved; §16's "current records overstate" items
   resolved or still open.

## Scope

In: the three correction commits, the whole hubless change set since `optin-v1.0.3` for
regressions, and every claim made about them. Out: changing shipping code or tests (a finding
instead), the hub's allocation tree beyond item 5, the whole-old-assignment unload rule (the
recorded contract, §16.3), §8 (Brad's tunnels, Xeryx's carry dial), the store copy and the Mod
Options help wording (§15.2), packing and upload. Report outside findings; do not edit them.

## Stops

- `git diff --stat 3aa5402 HEAD -- Code/ tools/trains/` is not empty: the tree moved; report what
  moved before auditing.
- A finding needs a behaviour change R1–R7 do not cover: report the options, do not choose.
- A check the harness cannot express (engine scheduling, saves, drones, pixels, route rebuild
  timing): mark it NOT RUN in the verdict; never fill it with a claim.

## Claim limits

Supported: "audited against the archived native bodies and the harness doubles at `<sha>`; the
change set is confirmed as desk-verified" or "corrections still needed: <list>". Not supported:
tested in game, fixes any named player's save, any throughput, drone, panel or save-and-load
figure. Record the executed model from the transcript in §18; do not describe it as independent
unless it is not Claude Fable 5.1.

## References

Skills: `smr-orientation`, `smr-bug-library`, `doc-editing`, `smr-session-close`. House rules
`CLAUDE.md`; process `docs/agent/WORKFLOW.md`; code `docs/agent/FIX_POLICY.md`. The archive is
hidden from a default `rg`; name `docs/archive/` to search it.
