# 30 — Station rows without a hub (build, design pass)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/30_STATION_ROWS_WITHOUT_HUB_high.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Reasoning: high (design within a ruling, save
safety, vanilla train loading).

## Authority (settled; do not reopen)

The owner, 2026-10-02, after finding that underground stations show vanilla panels because no hub
is on their network: *"I want to give the import / export / and sliders options even without the
hub. Some people may never watn to use the hub. But everyone wnats the sliders back, and the import
/ export options make those sliders much more effective"*. Recorded in spec
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.7 (grep `the rows go on every station`).

## Outcome

Every vanilla train station (`IsKindOf "Station"`, the Elevator Depot excluded as now) carries the
§4.7 rows (per-resource state cycle, native title, inline slider) whether or not a hub serves it,
and vanilla trains honour them. A station on a hub's network behaves exactly as it does today
(§4.8). A player who never builds a hub gets the rows; the code path for a hubless station must not
need a hub to exist, so the later move brief can ship Module A (stations) apart from Module B (the
hub). Done when: the rows draw and act on a hubless station in game, the hub smokes still pass, and
the owner has passed the smoke sitting.

## What is already known (claims; one check each)

- Why rows are missing today: `45_TrainDistributionUI.lua`'s `network(st)` requires `D.HubFor(st)`;
  every hook falls back to vanilla without a hub (agent read at `8f181fc`; re-derive lines with
  `grep -n "HubFor" tools/devmods/train_hub/Code/4*.lua`). The hub's track graph never crosses the
  depot pair, so underground stations have no hub.
- The row's control writes to **the hub's table** (spec grep `Storage location and UI location are
  independent`). A hubless station needs another home for its settings: your design call.
- Vanilla already carries most of Module A, unwired: `transport_policy[res]` with `accept`/`send`
  branches in `Station:SetDesiredAmount`; the import cap and the missing export floor are in spec
  §4.2-§4.5 (the six vanilla paths that rewrite desired amounts, and the alias trap in §4.6). The
  hub build already solved floors and pins for its own stations; reuse what fits.
- The owner's live fixture: the current game's underground network has a hubless vanilla
  `StationBig` (9702 in the 2026-10-02 log) on the line to the depot's underground half; its SMRTK
  stock rows read `target=none`. Re-read the newest `Mars.exe-*.log` rather than trusting this.

## Constraints

- **The save rule for claims** (spec grep `The save rule for claims`): no station may be left
  crippled in a save after the mod is removed. This binds hubless settings fully, including any use
  of vanilla's own persisted `transport_policy`.
- **Persisted names are save contract** (`docs/agent/FIX_POLICY.md` header). Name every new
  persisted field in your report for the inventory at ship.
- Which states a hubless row offers (Balanced has a hub meaning in §4.8's table) and what happens to
  a station's settings when it joins or leaves a hub network are your calls; record them in the
  commit message and the report for the owner to judge by eye.
- §4.7's look stands: native parts only, the slider inside the row's line, no added height.
- Movement is finished; dispatch and loading policy beyond honouring the rows are out (spec §10).

## Scope

In: the rows and their effect on hubless stations; the hubless/hub seam; the depot's twinless
infotip (below). Out: the rest of the Elevator Depot, hub dispatch, train movement, the shipping move. Report anything else you find; do not edit it.

## Also: the depot's missing "No surface twin" infotip (owner, 2026-10-02: "fold it into 30")

A defect found in the same sitting, in `tools/devmods/elevator_station/`. Brief 27's accepted
design (spec §11): a depot half that loses its twin works as a plain station, and its panel's
infotip adds *"No surface twin: the cabin is idle and this half works as a plain station; the
setting is kept for the next surface depot."* (grep `No surface twin` in
`docs/agent/reports/ELEVATOR_DEPOT_WIRING_20261001.md`). Live 2026-10-02, after Load A and the
surface half's salvage, the log has `no pair: surface none underground 9041` and the half works as
a plain station, but the line **never appeared** (owner: *"This message didn't come up with the
station destroyed"*; log `Mars.exe-20261002-00.07.14-6aba6e65.log`, the panel opened twice on 9041
after the salvage, 0 "LUA ERROR"). Whether the surface half's mirror wording fails the same way is
yours to check. Fix it without changing pairing or plain-station behaviour. Done when the line
shows in game and OI-38's E5 rest passes in the same sitting: place a new surface depot; it takes
the old settings (`pair formed: surface <new> underground <U>`, Scratch reads
`underground_panel=matches copy=current`). The depot's `tests/wiring_smoke.py` fails at HEAD for a
known, unrelated reason (its hub `fit_title` check predates `b551930`); bring it up to date if it
blocks you, and say so.

## Work method

- `git log --oneline -5` and `git pull` first; authored at `8f181fc`+ (the commit adding this
  brief). Only one brief editing `20_TrainHub.lua` runs at a time; none other is live.
- Use the todo tool before any write: one item per commit-and-verify unit, one in progress.
- Quick and iterative (owner, 2026-09-20): get it in game rough, the owner dials it in by eye. A
  design pass gets a **smoke** only (spec §10); the full battery waits for the final build.
- The sitting: preload SMRTK slots (`tools/SMRTK.md`), about five steps a batch, predictions from
  your build, hubs named by role. The orchestrator guides the owner through it; write the steps in
  your report.
- References: `CLAUDE.md`, `docs/agent/WORKFLOW.md`, `docs/agent/FIX_POLICY.md`; skills
  `doc-editing` for doc edits, `smr-bug-library` for engine facts (`docs/agent/facts/INDEX.md`).

## Stops (report instead of continuing)

1. The save rule cannot be met for hubless settings without leaving state a removed mod cannot undo.
2. The hubless path would change how a station on a hub's network behaves.
3. Vanilla train loading cannot honour import caps or export floors without owning the scheduler
   (spec §4.4 "Reserve").

## Claim limits

"Works without a hub" means seen in game on a hubless station, not inferred from the code path.

## Lifecycle

One-off. The orchestrator deletes or parks it when its work is done; do not move it yourself.
