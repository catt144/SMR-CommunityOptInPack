# Station rows relay: the audit's corrections (A1–A5)

One-off. Authored 2026-10-21 at `963810a` by Claude Fable 5.1 from the independent audit in
`docs/agent/reports/STATION_ROWS_RELAY_20261021.md` §16 (Codex), which found corrections needed
in the v1.0.4 build (§15; commits `8490c5e`…`83149ea`). Delete this file and its row in
`docs/agent/prompts/README.md` in the commit that closes the work. Start with
`git log --oneline -3` and `git pull`; the gitStatus block in your context is a snapshot.

## Authority

R1–R6 of 2026-10-21 stand as recorded in `docs/agent/bugs/D16.md` and `D18.md`. §16's A2, A3, A4
and A5 are corrections within them (an implementation that does not yet do what the ruling says,
and help that contradicts it). A1 is not: the base game's own allocator counts a station past a
people-only leg in its line total and storage (archived 1.1.1.406343 `Lua/Units/Train.lua:884-895`,
every station on the inclusive bidirectional walk; loading alone is gated by transport mode at
`:920`), so excluding such a station goes one step past "as the base game balances". The owner
rules it by firing this prompt; record it first, verbatim, in `docs/agent/bugs/D16.md` beside
R1–R6 and in the train spec §4.7, before any code moves:

- **R7** On a line with no Train Hub, a station this train cannot deliver to on its walk, because
  a people-only leg or a leg under construction lies between, takes no part in the balance: it
  has no reserve or relay part and its stock is not in the pool. Its own row still governs it
  when a train reaches it. (The alternative, not taken: keep the base game's dilution, where such
  a station's store and stock count and its share strands at the source.)

The 2026-09-26 row shape and click order stand. The hub's own allocation path is out of scope.
The whole-old-assignment rule at unload (§16.3 "Depot unload") is the recorded contract; it is
not a correction here.

## End state

A1–A5 corrected and desk-verified: every `COUNTEREXAMPLE` and the `OBSERVE Clear` line of the
audit's `docs/archive/station_rows_audit_20261021/adversarial.py` is now a `PASS` assertion in a
shipping smoke, its fixture kept; every smoke in §16.1's B list still passes; `parsecheck` and
doccheck GREEN. Records: a §17 build record in the report (commits, calls made, claim limits,
the executed model), the D16/D18 build lines extended with the corrected revision's sha, the
outbox entry's language checked against what the desk supports. A fresh audit is owed before any
release claim: re-author the audit prompt from `git show 922a22c:docs/agent/prompts/STATION_ROWS_RELAY_AUDIT_high.md`,
updated to the new commits and §17, map it, and put one `OI-` item on `docs/PLAYTEST_CHECKLIST.md`
for the owner to fire it on a model other than yours. No pack, no upload, no player reply, nothing
"tested".

## Evidence you would otherwise re-derive

Re-derive line numbers with `grep -n`; an empty `git diff --stat` does not validate them.
Abbreviations: SR = `Code/StationRows_40_TrainDistribution.lua`, UI = `Code/StationRows_45_TrainDistributionUI.lua`.

- **A1 (R7).** In `local_train_view` (SR, `grep -n "local function local_train_view"`), `members`
  comes from the inclusive bidirectional walk and `can_receive` from the flags-0 walk with
  `mode ~= "people"`; `part()` and `line_of()` loop over `members`, so a station past a people-only
  leg gets reserve/relay parts and its stock enters the pool; only `order()`'s caller applies
  `can_receive`. The native walk (`Lua/TrainTransport.lua:371-447`, 406343) continues past a
  people-only edge with the transport mode marked and stops at an edge under construction, so
  `members` can hold stations `can_receive` never will. The current station itself is never in
  `can_receive` and must stay in the balance (its stock, its floor). Audit fixtures: `adversarial.py`
  lines near `ts[1].members.edges[2].tracks[1].transport_mode='people'` (two cases: Export 0 source
  60, cargo receiver 0, people-only receiver 0, three trips, expect the cargo receiver to fill;
  Default source 60, empty Import 100, people-only station holding 60, expect a 30 load). They run
  406343's native `ForEachStationAlongTrack`; the relay smoke's harness walk takes a per-track
  `mode` only, so extend it or port the audit's fixture builder.
- **A2.** `line_of()` rounds each slot's share with `MulDivRound(remaining, s.w, total_w)`
  independently (two sites, `grep -n "MulDivRound(remaining"`), so the shares' sum can exceed the
  pool by up to about half a unit per slot; the handle sort fixes order, not the remainder. Witness:
  pool 2 internal units, orders 1 + 1 and a floor of 1 (`COUNTEREXAMPLE rounding`). A correction
  apportions the integer remainder in the sorted order while keeping every slot at or below its
  room; the audit's rational oracle search (`PASS water-fill search seed20261021`) is the control
  to keep passing, and conservation (`max pool-sum error`) should read 0 after the fix.
- **A3.** The click handler (UI, `Station.ToggleAcceptResource = function`) reads `D.RowState`,
  whose `D.Get` and `default_percent`'s `D.HubFor` use the ownership cache (SR `D.HubFor`,
  refreshed only when a second has passed), while `D.Set` and `D.Clear` call `D.Refresh()` first;
  a hub graph change inside that second lets a click choose from the old set and write the new
  one. The slider's `OnScroll` reads the same way. The seam predates the build
  (`contract.py` shows it at `5ba8f3f`); R4 changes what is written. One ownership snapshot per
  click and per scroll: refresh, then read, choose and write. Audit fixtures: the two
  `COUNTEREXAMPLE UI … seam` cases (leave-hub: cached Export 0 click must not write Import 100
  into a dormant local Import 70; join-hub: cached local Default click must not overwrite a saved
  hub Import 77 with Export 0).
- **A4.** UI `local_help.import` says trains "never take it away" and `local_help.export` "never
  deliver here"; on a joining station the rollover then appends the pass-through sentence. Scope
  the clauses to what the station keeps (its number) or write the junction rule into the
  joining-station text; the audit's check invokes the installed `ResourceRolloverText` and looks
  for both clauses together. Player text: the owner's build-menu tone, one or two short sentences.
- **A5.** `D.Clear` (SR) removes an emptied per-station table and an emptied local table but
  leaves `SMROptIn_distribution = {}` on the hub when the last station's entry goes (`OBSERVE
  Clear`). Remove the empty outer table too; inert data, same persisted name, no shape change.
- The build's harness notes are in §15.1 and the audit's in §16.1; the records' current wording
  is in `git show 963810a` (the audit rewrote the outbox entry and D16's description).
- Further records: `docs/agent/bugs/INDEX.md`, `docs/agent/facts/INDEX.md`.

## Live work list

One item per commit-and-verify unit, one in progress at a time, in your todo tool or the
closing report.

1. R7 recorded (D16, spec §4.7); A1 in the 40 file; the audit's two A1 fixtures as assertions in
   `tools/trains/hub/tests/hubless_relay_smoke.py` (or a sibling smoke of your naming); every
   relay and hubless smoke, `parsecheck`, doccheck.
2. A2: remainder apportionment in `line_of()`; the rounding witness and the oracle search as
   assertions; the same battery.
3. A3 and A5 in the 45 and 40 files; the two seam fixtures and the Clear observation as
   assertions in `distribution_ui_smoke.py`; `module_gates_smoke.py`, the UI and hubless smokes.
4. A4: the help text and the audit's clause check as an assertion.
5. §17, the D16/D18 lines, the outbox language, the re-authored audit prompt and its `OI-` item,
   close-out through `smr-session-close`; this prompt deleted with its map row.

Judgment within the authority is yours: the apportionment method, where the fixtures live, the
help wording, the order of units 2–4. Record calls in commit messages, not questions to the owner.

## Scope

In: the five audit items, their tests and records, the re-authored audit prompt. Out: the hub's
allocation tree, the whole-old-assignment unload rule, §8 (Brad's tunnels, Xeryx's carry dial),
the store copy and the Mod Options help wording (§15.2), packing and upload. Report outside
findings; do not edit them.

## Stops

- `git diff --stat 83149ea HEAD -- Code/ tools/trains/` is not empty at start: the tree moved
  after the audit; report what moved before touching anything.
- A correction would need a behaviour change R1–R7 do not cover, a new persisted name or a new
  wrapper on a vanilla method: report the options.
- An audit fixture cannot be expressed in the shipping harness after a reasonable port: keep it
  as an archived check with its command recorded in §17 and say so; do not drop the assertion.

## Claim limits

Supported: "corrected and desk-verified against the archived native bodies at `<sha>`; audit
pending". Not supported: tested in game, fixes any named player's save, any figure about
throughput, drones, the panel or save and load.

## Audit

Execution and audit on different owner-selected models; the build and this brief are Claude
Fable 5.1's. Hand the owner the re-authored audit prompt; nothing enters D16 or D18 as tested
before it returns, and release waits on it.

## References

Skills: `smr-orientation`, `smr-bug-library`, `doc-editing`, `smr-session-close`,
`prompt-authoring` (for the audit prompt). House rules `CLAUDE.md`; process
`docs/agent/WORKFLOW.md`; code `docs/agent/FIX_POLICY.md`, whose header bans this work must not
touch. The archive is hidden from a default `rg`; name `docs/archive/` to search it.
