# Station rows and the Elevator Depot without a hub: build the relay fix

One-off. Authored 2026-10-21 at `5ba8f3f` by Claude Fable 5.1 from the triage, two independent
checks and the desk-checked prototype in
`docs/agent/reports/STATION_ROWS_RELAY_20261021.md` (§12 the proposal, §13 its second check,
§14 revision b, which answers §13). Delete this file and its row in
`docs/agent/prompts/README.md` in the commit that closes the work. Start with
`git log --oneline -3` and `git pull`; the gitStatus block in your context is a snapshot.

## Authority

The owner's rulings of 2026-10-21, given by firing this prompt, on the six decisions in the
report's §12.6 as amended by §14.3. Record them first, verbatim from this list, in
`docs/agent/bugs/D16.md` and `docs/agent/bugs/D18.md`, and the rule in the train spec
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.7 beside the 2026-10-05 ruling, before
any code moves (`CLAUDE.md`: a shipping module's behaviour changes only under a recorded ruling):

- **R1** On a line with no Train Hub, a row keeps its amount for its own station; what a
  station holds beyond that balances with the line as the base game balances, split by weight
  and water-filled (§14.1), so cargo for other lines passes through a station that joins lines.
  A station joins lines when it can exchange cargo on two or more routes. The reserve wins: a
  full Import or Balanced on a joining station leaves no room to pass cargo through.
- **R2** A line with an Elevator Depot takes this view whatever the Station rows toggle says, as
  a hub's network takes its rows; a depot half's row enters through the hub's existing read,
  for loading and for unloading.
- **R3** The depot-line dial pin of 2026-10-05, an agent's call, is dropped.
- **R4** A click to Import sets 100, or 50 on a station that joins lines and is not on a hub;
  a click to Export sets 0; a click to Default clears the row in the set being edited. The
  slider from Default makes Balanced at its value; from Export or Import it keeps the mode.
  Rows already saved keep their numbers.
- **R5** The depot's unset slider targets take the same defaults, Import 100 and Export 0, on
  every depot including hub-managed ones, in place of the dial percentage.
- **R6** Stock above an Export or Balanced number drains to untouched neighbours instead of
  stranding.

The 2026-09-26 row shape and click order stand. The hub's own allocation path is out of scope.

## End state

v1.0.4 staged: the three player reports in the report's §1 (Erion, Xeryx, TheGodUncle) are
closed by one change set, desk-verified, with a `### Pending` entry in
`docs/agent/prompts/perma/RELEASE_OUTBOX.md`, D16 and D18 updated, doccheck GREEN, and the
built diff handed to the owner for the independent audit (the owner runs it on a model of their
choice; nothing of this enters the record as tested until that audit returns). No pack, no
upload, no player reply: those are the owner's, through `release_prompt.md` afterwards.

## Evidence you would otherwise re-derive

- The transport core already exists as a prototype of `Code/StationRows_40_TrainDistribution.lua`
  with a diff against the shipping file, under
  `docs/archive/station_rows_proposal_20261021b/` (prototype sha256 `336e911d…`; shipping file
  `b0de6db1…255e`, equal to tag `optin-v1.0.3`). Its `proposal_check.py` passes there and is the
  test to promote; `hubless_smoke_on_proposal.py` shows the shipped `hubless_smoke.py` flipping
  exactly two assertions, the ones encoding the dropped dial pin. Re-derive both by running
  them from the repo root before you touch anything; a different result is a stop.
- The rule, the weights and rooms, and the junction definition are written out in the report's
  §14.1 with §12.2's table; the desk numbers to reproduce are §14.2.
- Vanilla's allocator reads and the depot's policy mapping are cited in §4.3 and §11 against the
  archived tree `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343\Src` (installed build
  25579348; confirm with `python tools/doccheck.py --emit-fingerprint`). Re-derive any line number
  you cite with `grep -n`; an empty diff does not validate it.
- The depot's row help lives in `Code/ElevatorDepot_10_ElevatorDepot.lua` (`surface_help`); its
  unset target in `D.Target`; the station rows' cycle, defaults and help in
  `Code/StationRows_45_TrainDistributionUI.lua` (`following`, `D.RowState`, `local_help`). The
  existing `D.Reset` in the 40 file clears both the local and the hub set; R4's clear must not.
- Player-facing text follows the owner's build-menu tone: one or two short sentences, `<em>`
  keywords, no numbers the row already shows. The three lines the report asks for are in its
  §12.5 item 7 and §12.6a.
- Further records: `docs/agent/bugs/INDEX.md`, `docs/agent/facts/INDEX.md`.

## Live work list

One item per commit-and-verify unit, one in progress at a time, kept in your todo tool or in
the closing report.

1. Record R1–R6 (D16, D18, spec §4.7); doccheck GREEN.
2. The transport core: the archived diff into the 40 file, cleaned of its prototype comments and
   written in the file's own voice; `hubless_smoke.py`'s two assertions updated;
   `proposal_check.py` promoted to `tools/trains/hub/tests/` under a name of your choosing with
   its temp-folder indirection removed; `module_gates_smoke.py`, the parse sweep, doccheck.
3. Defaults and the Default state (R4) in the 45 file, with a scoped clear; the joining-station
   default reads the 40 file's `D.IsJunction`; `distribution_ui_smoke.py` extended.
4. The depot's unset targets (R5) and its Export help; the stations' Import and Export help and
   the joining-station tooltip line; `wiring_smoke.py` expectations for the new defaults.
5. Outbox entry, D16 and D18 status lines, close-out through `smr-session-close`; this prompt
   deleted with its map row.

Judgment within the authority is yours: naming, the help wording, test layout, the order of
units 3 and 4. Record calls in commit messages, not questions to the owner.

## Scope

In: the hubless allocation and unload path, the row UI defaults and clear, the depot's defaults
and help, their tests and records. Out: the hub's allocation tree and its junction concerns
(§11), Brad's tunnel report and Xeryx's carry dial (§8), the store copy, packing and upload;
report outside findings, do not edit them.

## Stops

- The archived checks do not reproduce at your HEAD, or the shipping 40 file no longer equals
  `optin-v1.0.3`.
- A unit would need a new persisted name, a new wrapper on a vanilla method, or a change to the
  hub's tree: report the options.
- A desk control in §14.2 fails after the clean-up and the cause is in the rule, not the port.

## Claim limits

Supported: "built and desk-verified against the archived native bodies at `<sha>`; audit
pending". Not supported: tested in game, fixes any named player's save, or any figure about
throughput, drones, the panel or save and load until the audit and the owner's play say so.

## Audit

Execution and audit on different owner-selected models. Hand the owner the built diff and the
test commands; the audit judges the port against §14 and the three player cases. No result
enters D16 or D18 as tested before it returns.

## References

Skills: `smr-orientation`, `smr-bug-library`, `doc-editing`, `smr-session-close`. House rules
`CLAUDE.md`; process `docs/agent/WORKFLOW.md`; code `docs/agent/FIX_POLICY.md`, whose header
bans (persisted names, executable references) this work must not touch.
