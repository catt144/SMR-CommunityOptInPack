# 34 — Remove the dev tags: the train modules move into this mod (build)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/34_MOVE_INTO_MOD_high.md` in a fresh
session rooted at `B:\Dev\SMR\SMR-OptInPack`, **after briefs `30`, `31` and `32` close**. Reasoning:
high (module structure, save contract, assets, release tooling). If the work runs past about two
sessions, split it per `docs/agent/support/CHAIN_METHOD.md` and tell the orchestrator.

## Authority and outcome

The owner, 2026-10-01: *"remove its dev tags"* means the audit, then **a brief moving the hub and
the Elevator Depot out of their dev mods into this mod as modules**, carrying OI-18's ruling to
**widen `tools/upload_preflight.py`** so their templates and models can ship (spec
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §11, grep `Remove its dev tags`; ship size
§9, grep `OUR OWN GUARD`). The owner, 2026-10-02: station rows go on every station **with or
without a hub**, because *"Some people may never watn to use the hub"* (§4.7, grep `the rows go on
every station`), so the station rows must ship usable with the hub never built.

Outcome: this mod ships the station rows, the train hub and the Elevator Depot as opt-in modules
under `FIX_POLICY` §8 (one `Code/Opt_<id>.lua` per module, listed in `metadata.lua` and `items.lua`
in the same order, off until the player turns it on), with their templates, entities and assets,
no "(dev)" or "DEV ONLY" text anywhere a player sees, and the dev mods
(`tools/devmods/train_hub/`, `tools/devmods/elevator_station/`) retired. Done when doccheck and
every smoke pass on the shipping layout, `upload_preflight.py` passes the real pack, and the owner
has seen the three modules load from this mod in game. The full battery is brief `35`'s.

## The owner's checkpoint (before any code moves)

**Answered 2026-10-02 (OI-41):** the proposal `docs/agent/reports/TRAIN_MOVE_CHECKPOINT_20261002.md`
stands, with two changes: **station spoilage goes with the hub module**, not the rows, and
**Station rows is forced on while the Train Hub module is on**. The rulings
are in spec §10's last list (grep `Brief 34's checkpoint`) and FIX_POLICY §8.

Write a short proposal for the orchestrator to put to the owner, and wait for the yes:
- **The module list and option names.** The default shape is three modules: station rows
  (Module A), the train hub (Module B, with its drones, distribution, bay and floor), and the
  Elevator Depot. Say where `60_StationSpoilage.lua` and each other dev file goes, and what each
  module needs from another (the station rows must not need the hub).
- **Names that are in saves.** Building classes and template ids (for example
  `SMROptInElevatorDepotDev`, `SMROptInTrainHub6`) and every persisted field are save contract once
  shipped (ban 1). The owner's own playtest saves use the dev names: propose keep or rename, with
  what each costs those saves. This is the owner's call.
  Include the historical one the audit found (`TRAIN_AUDIT_20261002.md` §1): `bfd748c` replaced
  `SMROptInElevatorStationDev` with `SMROptInElevatorDepotDev`; whether a retained save holds the
  old name is unverified.

## What is known (claims; one check each)

- The audit report from brief `31` (`docs/agent/reports/TRAIN_AUDIT_20261002.md`, at `ba357e2`) lists the persisted
  names, the spec-against-code gaps and what the battery must carry. Fold its findings into this
  move or name the ones you leave, with reasons.
- The dev mods' ids are `SMR_TrainHubDev_20260918` and `SMR_ElevatorStationDev_20260929` (the
  2026-10-02 log's `SMRTK_FINGERPRINT`). Their templates are generated from Mod Editor saves: edit
  sources and have the owner save, never hand-edit generated output.
- Depot text to rewrite for players: the build-menu description still says "DEV ONLY", "once an
  hour" and nothing of the upgrade (owner's screenshot, 2026-10-02). Write it from the depot as it
  now behaves (spec §11's last blocks).
- Every new module gets its record (`docs/agent/bugs/`, skill `smr-bug-library`) and every persisted
  name its row in `FIX_POLICY` §"The persisted-name inventory".

## Scope and method

In: the move, the module split, player-facing text, the preflight widening, the records. Out:
behaviour changes (none are ruled; report any you find), movement, loading policy. `git log
--oneline -5` and `git pull` first; authored at `58ebf7e`+. Use the todo tool before any write, one
item per commit-and-verify unit. Ban 2: no `SMRFixPack` executable references; the framework is
`SMROptInPack`. Write the owner's Mod Editor steps where a save is needed. References: `CLAUDE.md`,
`docs/agent/WORKFLOW.md`, `docs/agent/FIX_POLICY.md`; skills `doc-editing`, `smr-bug-library`.

## Stops

1. The owner has not answered the checkpoint.
2. A persisted name would change without the owner's ruling.
3. The assets cannot ship from this mod without a game-file edit or a pack the game will not load.

## Lifecycle

One-off; the orchestrator deletes it when done.
