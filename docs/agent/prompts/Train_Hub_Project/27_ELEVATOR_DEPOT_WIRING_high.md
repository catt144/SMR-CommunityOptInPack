# Brief 27 — the Elevator Depot's wiring · _high

## Authority and outcome

The depot's look passed (owner, 2026-10-01: briefs 25 and 26 parked for the paint pass). This
brief makes the pair **work**: cargo crosses between the surface and the underground on the
owner's rulings below, in the dev mod `tools/devmods/elevator_station/`. Spec §11 holds every
ruling with the owner's words; `reports/ELEVATOR_STATION_LOOK_20260929.md` §6 (its closing
"Yes to all" and the placement ruling) holds the 2026-09-29 ones. **Settled; do not reopen:**

1. **Per-trip loads.** Each half has its own storage and the cabin carries the cargo; nothing
   crosses while it travels. This supersedes the 09-29 morning table's "one store, shared".
2. **Row modes** as at every station (Import / Export / Balanced / Not accepted) on the depot's own
   rows. The depot owns the setting; the hub reads it. Import on a half gathers that resource on
   its own map for the cabin; Export hands it out on its map; Not accepted is never carried.
3. **Mirrored link** (owner, 2026-10-01). One setting per resource for the pair: surface Import =
   underground Export, and the reverse. The owner: *"if you change one on the above ground it
   should be match the below ground one, since importing on the above ground means you are trying
   to get those resourced below ground"*. Changing either half's row sets its twin's (the
   orchestrator's reading, given to the owner). The underground half gets the rows; the owner
   found it has none today.
4. **One pair per colony**, each half placed anywhere on its own map by the player, in either order;
   needs the underground unlocked; balanced by cost and unlock. This supersedes the morning table's
   placement within a vanilla elevator's service area and the automatic twin: there is **no range
   rule**.
5. **Timer.** One leg per game hour on a fixed schedule, down then up, repeating. Capacity is the
   balancing knob; leg time, pause and capacity stay live tunables.
6. **Drone Access** (owner, 2026-10-01): a toggle on **both** halves beside the existing Shuttle
   Access one, **default off**. Off, drones from drone hubs do not service the depot's storage.
   Stations keep vanilla drone service. The owner's reason: a drone hub covering both stations and
   the elevator runs at heavy load *"trying to balance the stations and the elevator even though
   the trains should be doing the work"*.
7. **Passengers need no depot code.** The owner watched the chain end to end on 2026-10-01: train
   to the depot, walk to vanilla's elevator, down, board an underground station. Keep it working.
8. **Independence.** Vanilla's elevator is not altered. The depot works without the hub, and the
   hub serves it like any member station. Either mod works alone in every underground state
   (`reports/CROSSING_SHAPE_20260929.md` §2 S1/S2/S6, §5, §7).

**Yours to recommend, with reasons in the report; the owner rules from it:**
- how the one-pair limit is enforced (vanilla's `build_once` counts by template);
- what a surviving half does when the other is demolished;
- the depot's own drone crew, if any, given rule 6 (09-29: *"agent can make its best choice and
  we can balanced from there"*);
- the vanilla elevator's per-resource marks (red X, green arrow, ticks): modes or stock state? If
  they are modes, match the depot rows' vocabulary to them so both panels read the same way.

**Done when** the owner's attended smoke passes in their fixture: a resource set to Import on one
half crosses on the hourly cabin and is handed out on the other; the mirror holds from either
panel; Drone Access off keeps hub drones away and on lets them in; the passenger chain still works.
Then this brief returns to the orchestrator.

## Start

Authored at `4a2652f`. Run `git log --oneline -3` and `git pull` in this repo and SMR-Assets. Keep
a live todo list before any write, one item per commit-and-verify unit, one in progress. Build must
be **25579348** (`python tools/doccheck.py --emit-fingerprint`); cite source from that build's
archived tree under `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive`. Check whether the game runs before
writing `Code/` (`tasklist /FI "IMAGENAME eq Mars.exe"`). Commit a checkpoint before any Mod Editor
session.

Read spec §11 whole, then `reports/ELEVATOR_DEPOT_DESIGN_PASS_20260930.md` for the dev mod's current
state, and `Parked/25_ELEVATOR_STATION_LOOK_high.md` "What exists" for its console and pipeline.

## Evidence (claims, each cleared by one check)

- The four modes live today in the hub dev mod's `tools/devmods/train_hub/Code/40_TrainDistribution.lua`.
  The depot needs them without the hub and one owner of each row when the hub is present.
- Vanilla's Space Elevator runs one course per Sol, each leg a game hour
  (`SpaceElevatorTripInterval`, `travel_time` in `SpaceElevator.lua`; re-derive the lines with `rg -n`).
- Vanilla's `MapSharedDepot` (`Lua/Buildings/Elevator.lua`) is a cross-map shared store: a source of
  mechanism, never a reason to drop rule 1.
- The passenger chain rides `LabelsConnectedToStations.Elevator = "all"` (`Building.lua`, 3843-3850 on
  406343): the depot being a `Station` is what lets it work.
- The depot already shows a Shuttle Access toggle (SMR-Assets
  `elevatorstation/owner_feedback/drone_access_01_shuttle_access_toggle.png`).
- Further records: `docs/agent/bugs/INDEX.md`, `docs/agent/facts/INDEX.md`.

## Scope

- In: the pair's cargo, rows and mirror, the hourly cabin, Drone Access on both halves, the one-pair
  limit, a half's demolition, the recommendations above, the sitting script.
- Out: the look (parked brief 26), train movement, vanilla's elevator and stations, passengers, the
  hub's upgrade texts, moving anything into the shipping layout. If the hub must change to read the
  depot's rows, report it; do not edit hub code.

## Stops — report instead of continuing if

1. A ruling cannot be met without altering vanilla's elevator or writing custom train movement.
2. The installed build is no longer 25579348.
3. The passenger chain or the either-mod-alone requirement breaks and the repair needs a ruling.

## Claim limits

Every new saved field is a persisted name (ban 1, `FIX_POLICY.md`): list each in the report. Do not
claim `FIX_POLICY` §8's ship or toggle test: this is a dev mod, and those belong to the final
battery. Do not claim passengers re-verified unless the sitting watched them. Supported: desk tests,
`Report()` reads, the log, and the owner's words.

## The sitting

Smoke depth (spec §10): one prediction per step, about five steps a batch, the owner clicks and the
orchestrator reads the log on flush. Preload SMRTK slots where a slot fits (`tools/SMRTK.md`); a
console line needs a stated reason no slot fits. Use the time controls, not owner minutes, to reach
the hourly legs. The fixture is the owner's underground save with both depots and the vanilla
elevator; ask the owner to name it. A Mod Editor save, if a template changes, gets step-by-step owner
instructions and the check that proves it landed.

## Hand back

Report `docs/agent/reports/ELEVATOR_DEPOT_WIRING_20261001.md` (dated later if it slips): commits,
design calls, the four recommendations, the persisted names, the sitting batches, what you did not
do. Commit with pathspecs in both repos. Update this brief's row in this folder's `README.md`; do not
delete or move this brief. Skills: `doc-editing`, `smr-bug-library`, `smr-session-close`. House
rules `CLAUDE.md`, process `docs/agent/WORKFLOW.md`, code `docs/agent/FIX_POLICY.md`.
