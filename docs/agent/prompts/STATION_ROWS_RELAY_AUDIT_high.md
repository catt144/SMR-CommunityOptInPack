# Station rows relay build: the independent audit

One-off. Authored 2026-10-21 at `504b08f` by Claude Fable 5.1, the model that built what you
are auditing; run this on a different model, the owner's choice (CLAUDE.md: execution and audit
on different owner-selected models). Delete this file and its row in
`docs/agent/prompts/README.md` in the commit that records your verdict. Start with
`git log --oneline -3` and `git pull`; the gitStatus block in your context is a snapshot.

## Authority

The owner's rulings R1–R6 of 2026-10-21, recorded verbatim in `docs/agent/bugs/D16.md` and
`docs/agent/bugs/D18.md` (the rule also in `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`
§4.7). The audit judges the build against them and against the report's §14; it does not reopen
them. The owner fires this prompt; firing it is the owner's action on `OI-53` in
`docs/PLAYTEST_CHECKLIST.md`, so your closing commit deletes that item.

## End state

A written verdict as §16 of `docs/agent/reports/STATION_ROWS_RELAY_20261021.md`, in the shape of
its §11 and §13: a one-line verdict (the build is confirmed as desk-verified, or corrections are
needed, each named), then evidence, each finding carrying the command that produced it and its
output. Your own scripts and their outputs archived under `docs/archive/station_rows_audit_20261021/`,
runnable from the repo root. One line appended to the build status line in D16 and D18:
`Audited <date> (<executed model, from the transcript>): <verdict>`. `OI-53` deleted. This prompt
deleted with its map row. doccheck GREEN; one commit with a pathspec. No shipping code changes: a
correction is a finding for the owner's next brief, not an edit here. The verdict does not make
anything "tested": that word still waits on the game.

## What is being audited

The five commits after `5ba8f3f`, all on `main`:

| commit | unit |
|---|---|
| `8490c5e` | R1–R6 recorded; the report, its four archive folders and the build prompt filed |
| `a731a20` | `Code/StationRows_40_TrainDistribution.lua`: the archived revision-b prototype ported whole; `hubless_smoke.py`'s two dial-pin assertions flipped; `tools/trains/hub/tests/hubless_relay_smoke.py` promoted from `proposal_check.py` |
| `00e2dff` | `Code/StationRows_45_TrainDistributionUI.lua`: the Default state and the click defaults (R4); `D.Clear` in the 40 file; `distribution_ui_smoke.py` |
| `83149ea` | `Code/ElevatorDepot_10_ElevatorDepot.lua`: unset targets Import 100 / Export 0 (R5), Export help; the stations' Import/Export help and the joining-station tooltip line; `wiring_smoke.py` |
| `504b08f` | records only: outbox entry, D16/D18 build lines, `OI-53`, the report's §15, session log |

The code diff: `git diff 5ba8f3f 83149ea -- Code/ tools/trains/`. The build's own record of its
calls is the report's §15.1; its claim limits §15.3.

## Evidence you would otherwise re-derive

Each line carries the command that measured it; re-run before relying on it.

- The 40 file at `a731a20` is the archived prototype plus comments: stripping comments from both
  leaves only four blank lines (`diff <(git show a731a20:Code/StationRows_40_TrainDistribution.lua
  | sed 's/[ \t]*--.*$//') <(sed 's/[ \t]*--.*$//'
  docs/archive/station_rows_proposal_20261021b/StationRows_40_TrainDistribution.proposal.lua)`).
  The prototype's sha256 is `336e911d…` (`sha256sum` the archived file); the file before the port,
  `b0de6db1…255e`, equals tag `optin-v1.0.3` (`git show optin-v1.0.3:Code/StationRows_40_TrainDistribution.lua | sha256sum`).
  After `a731a20` the 40 file gained only `D.Clear` (`git diff --stat a731a20 83149ea -- Code/StationRows_40_TrainDistribution.lua`: 28 insertions).
- The desk checks, from the repo root, all PASS at `83149ea`: `python tools/trains/hub/tests/hubless_relay_smoke.py`;
  in `tools/trains/hub/tests`: `hubless_smoke.py`, `hubless_slots_smoke.py`, `distribution_ui_smoke.py`,
  `module_gates_smoke.py`, `distribution_smoke.py`, `distribution_slots_smoke.py`,
  `distribution_departure_smoke.py`, `export_pairing_smoke.py`, `export_pairing_slots_smoke.py`,
  `cargo_view_smoke.py`, `crossing_witness_smoke.py`, `food_stream_smoke.py`, `station_visuals_smoke.py`;
  `python tools/trains/depot/tests/wiring_smoke.py`, `props_smoke.py`, `revision_smoke.py`;
  `python tools/parsecheck.py` (19 files, 0 errors); `python tools/doccheck.py` GREEN with
  `WRAP CHECK: 0 wrap site(s) outside Require` and `TEMPORARY SWEEP: 0 hit(s)`.
- The harness: `tools/trains/hub/tests/distribution_smoke.py` runs archived native Train and
  Station bodies (pinned at 1.1.1.405907, parity-checked against 1.1.1.406343, installed build
  25579348 per `python tools/doccheck.py --emit-fingerprint`) over request and route doubles. Its
  `ForEachStationAlongTrack` double ignores a `"break"` return and the fixture's colony label is
  the first line's member list (a station added to the label sits on that route). The relay smoke
  overrides the walk with a per-track transport mode and the native `"break"`.
- Engine names the port relies on, in `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343\Src`,
  re-derive with `grep -n`: `TrackConnectedObjBase:ForEachConnectedTrack(callback, ...)` passing
  `(track, destination)` (`Lua/TrainTransport.lua:68`); `ForEachTrainInRoute` (`:485`);
  `Msg("TrainRoutesRebuilt")` (`:357`); `routes[segment] = route`, the route a station list with
  `.edges` and `.loop` (`:328-332`, `:371-373`); `ForEachStationAlongTrack`'s callback receiving
  `(station, transport_mode)` and stopping on `"break"`, a people-only or under-construction edge
  (`:371-447`); `Station:GetResAcceptIcon` returning `resource_storing.tga` (`Lua/Buildings/Station.lua:1003-1004`);
  `city.train_track_routes` defaulting to `false` (`Lua/City.lua:33`).
- The prior independent legs and what they found are the report's §11 and §13; their scripts are
  under `docs/archive/station_rows_review_20261021/` and `station_rows_second_review_20261021/`.
  §13's `second_check.py` was written against the first prototype and stops at its first witness
  on revision b (§14.2); its fixtures are still usable inputs.
- Further records: `docs/agent/bugs/INDEX.md`, `docs/agent/facts/INDEX.md`.

## What to judge

Judgment within the authority is yours: which counterexamples to try, the order, the harness
you extend. The verdict must answer these, each with evidence:

1. **The rule as built against §14.1 and R1.** Weights and rooms per part; water-filling
   (termination, rounding with three or more parts, the handle-sorted order); inbound reservations
   counted once; the pool counting cargo aboard every train on the route; an Import on a station
   of one line never giving; a joining station's relay room. Find a counterexample or say the
   search that found none.
2. **Joining lines (R1's definition).** `D.IsJunction`: distinct route objects, the native walk
   reaching a cargo-capable station, a people-only or under-construction leg not counting, the
   cache cleared by `D.Refresh` (at most a second) and `TrainRoutesRebuilt`; loop routes where a
   station appears twice; three or more routes through one station; `train_track_routes` still
   `false` (the UI calls `D.IsJunction` from a click).
3. **The depot (R2, R3, R5).** A depot line takes the view with the rows module off; a depot
   half's row at load and at unload (loose cargo capped, a whole old assignment kept aboard,
   Export refusing, a lone half native); the dropped dial pin; an unset target now 100 or 0 on
   hub-managed depots too (`D.HubEntry` reads `D.Target` on the hub path): what an existing hub
   network with an untouched depot does on load.
4. **The UI (R4).** The cycle Default, Export, Import, Not accepted, Default; a saved Balanced
   row; the click defaults (100 on a hub network and on a hubless station of one cargo line, 50
   on a joining station); the slider keeping Export and Import and making Balanced from Default;
   `D.Clear` clearing only the active set and keeping the dormant one (hub set when hub-owned,
   local when not; emptied tables removed); Ctrl+click copying Default (clearing) and the
   broadcast-to-disabled path; Not accepted keeping the saved row. Read the hub seam: a station
   leaving or joining a hub between a click and the next.
5. **The three player cases** (the report's §1, §4, §12.4 and §14.3): does the build remove the
   mechanism each report described, and does any claim in the outbox entry, D16, D18 or §15
   promise more than the desk supports?
6. **The bans and the contract** (`docs/agent/FIX_POLICY.md` header): no new persisted name,
   the `{mode, percent}` shape unchanged, Default as absence; no executable `SMRFixPack`
   reference; no new wrapper on a vanilla method (`OnMsg.TrainRoutesRebuilt` is an additive
   handler; `Train:UnloadAll` and `Train:TransferCargo` were wrapped before); the hub's allocation
   tree untouched (`train_view`, `branch_need`, `child_need`, the hub branch of `UnloadAll`).
7. **The records.** D16, D18, the outbox entry, the spec §4.7 and §15 say what the diff does and
   no more; the status words `tested-attended` were not moved.

## Scope

In: the five commits' diff and every claim made about it. Out: changing shipping code or tests
(a correction is a finding), the hub's allocation tree beyond item 6, Brad's tunnels and Xeryx's
carry dial (§8), the store copy and the Mod Options help wording (§15.2, the release prompt's),
packing and upload. Report outside findings; do not edit them.

## Stops

- `git diff --stat 83149ea HEAD -- Code/ tools/trains/` is not empty: the tree moved after the
  build; report what moved before auditing.
- A finding needs a behaviour change the rulings do not cover: report the options, do not choose.
- A check the harness cannot express (engine scheduling, saves, drones, pixels): mark it NOT RUN
  in the verdict; never fill it with a claim.

## Claim limits

Supported: "audited against the archived native bodies and the harness doubles at `<sha>`; the
build is confirmed as desk-verified" or "corrections needed: <list>". Not supported: tested in
game, fixes any named player's save, any throughput, drone, panel or save-and-load figure. Record
the executed model from the transcript in §16; do not describe it as independent unless it is
not Claude Fable 5.1.

## References

Skills: `smr-orientation`, `smr-bug-library`, `doc-editing`, `smr-session-close`. House rules
`CLAUDE.md`; process `docs/agent/WORKFLOW.md`; code `docs/agent/FIX_POLICY.md`. The archive is
hidden from a default `rg`; name `docs/archive/` to search it.
