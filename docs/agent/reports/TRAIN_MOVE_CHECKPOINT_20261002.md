# Brief 34's owner checkpoint — moving the trains into this mod (2026-10-02)

Authority: [brief 34](../prompts/Train_Hub_Project/34_MOVE_INTO_MOD_high.md), "The owner's
checkpoint". Read at `27cc842`. Nothing has moved yet. The move waits for brief `33`, because 33
edits `tools/devmods/train_hub/tests/`, and for the owner's answers below (brief stops 1 and 2).
Executed model: Opus 5.5 (`claude-opus-5-5`), with two read-only Opus subagents (a dev-file
dependency map and an engine read on 1.1.1.406343).

**Owner's answers, 2026-10-02 (OI-41):** questions 2, 3 and 4 as recommended, with no save
scan. Question 1: three modules, but **station spoilage goes with the hub**. Stations stop
spoiling food only while the Train Hub module is on, and `60_StationSpoilage` moves to
`Code/TrainHub/`. Follow-up, same day: **Station rows is forced on while the Train Hub module
is on**, whatever its own toggle says. Where this report says otherwise, the answers govern.

## What the move has to work around (SOURCE, 1.1.1.406343)

- **Templates and models can ship from this mod without a game-file edit** (stop 3 does not
  fire). `ModDef:LoadItems` loads `Data/` and `SourceData/` by folder name, whatever `has_data`
  says (`CommonLua/Modding/Mod.lua:592-630`). Entities load from the metadata `entities` list
  (`ModItem.lua:671-711`), and the `.entjson`/`.mtljson` files name their meshes and materials
  by full `Mod/<id>/...` paths. Each template needs both its `Data/` preset and its generated
  class (`Building.lua:2695-2707`).
- **Every `Mod/SMR_TrainHubDev_20260918/` and `Mod/SMR_ElevatorStationDev_20260929/` string
  must become `Mod/SMR_CommunityOptInPack/`**: the 5 `.entjson`, 5 `.mtljson`, both templates'
  `SaveIn` and `display_icon`, and `20_TrainHub.lua:189`'s save check. A `SaveIn` left on a dev
  id binds the preset to the wrong mod (`ModItem.lua:2484-2494`, `Mod.lua:666`).
- **A Mod Editor save of this mod rewrites `metadata.lua` and `items.lua` and drops every
  comment** (`Mod.lua:973-993`, `:1035-1144`). It rebuilds `entities` only from EntitySpec items
  in `SourceData/ArtSpec-mod.lua` (`Mod.lua:816-827`). Without `SourceData/`, the list empties and
  the models stop loading. Both portals force that save on upload, so this mod must carry the
  merged `SourceData/`. The packer still skips it (`*/SourceData/*`).
- **The dev mods must be off before the moved modules load.** If both are on, hand-written
  classes such as `SMROptInTrainHub6Base` fail "Redefinition of class" and mix. Templates and
  entities go to whichever loaded last (`classes.lua:58-84`). Both dev mods are `optional_mod`,
  so the owner's dev saves load without a missing-mods prompt (`SavegameMetadata.lua:85-110`).
  Their ids stay in those saves' `active_mods` for good, which is harmless.
- **Ship size:** the textures the five entities reference come to 99,967,164 bytes raw (hub 12
  maps, depot 5; `find … -printf '%s'`). Four old-look `SMROptInElevatorStation_*` maps and the
  hub's two unused `_A_BlackGlass`/`_B_BlackMirror` RM maps are referenced by no entity and stay
  out. The 5 MB guard does not bind this mod (owner, 2026-09-21, spec §9 `OUR OWN GUARD`).

## Question 1 — the module list, option names and what each needs

Recommended: **three modules, as the brief's default.** The Register id is also the Mod Options key
and becomes contract (FIX_POLICY inventory row 8).

| Module | Register id / file | Mod Options name | Off means |
|---|---|---|---|
| Station rows | `StationRows` / `Opt_StationRows.lua` | Station import/export rows | Hubless stations show vanilla rows and get vanilla transport. Their settings stay stored, unused, and come back when the module is turned on. A live flip off restores vanilla desired amounts, as saving does now. |
| Train hub | `TrainHub` / `Opt_TrainHub.lua` | Train Hub | No new hubs in the build menu. Built hubs, their drones, upgrades and their network's rows keep working (owner, OI-19, 2026-10-01). |
| Elevator Depot | `ElevatorDepot` / `Opt_ElevatorDepot.lua` | Elevator Depot | No new halves in the build menu. A built pair keeps working. |

Where each dev file goes (dependency map: the subagent read, `27cc842`):

- **Station rows** get `40_TrainDistribution`, `45_TrainDistributionUI`, `10_TrainFloor`'s
  transient-claim helpers (40 returns early without them, `40:21`, `:61-64`), and
  **`60_StationSpoilage`**: it stops food spoiling in every vanilla station, a station
  behaviour. It gets a guard, because today it errors at load without the hub class
  (`60:16`). **Its alternative is a fourth toggle of its own**; say which.
- **Train hub** gets `20_TrainHub`, `30_TrainHubDrones`, the rest of `10_TrainFloor`,
  `70_TrainBay`, its template and its three entities.
- **Elevator Depot** gets `10_ElevatorDepotDev` (renamed file), its template and two
  entities. It needs nothing from the hub or the rows. Its rows UI is its own (`depot:1362`).

What each needs from another: the rows need nothing from the hub. Every hub reference in
40/45 is checked when called, so a hubless station takes the hubless path. The hub
needs the rows' code, because a hub's stations are set through the same rows. So **a hub's
network keeps its rows when Station rows is off**: they are part of the hub. The code always
loads, and only the gates differ. The depot and the rows know each other by one global name,
read when called (`40:73-81`, `45:81`, `depot:996`). Each works without the other.

## Question 2 — file layout (FIX_POLICY §8 says one module per `Opt_<id>.lua`)

The hub is 6,700 lines in seven files today. Recommended: **(a) one `Opt_<id>.lua` per module
holds its Register call and gate, and its parts keep their files in a folder named for the
module** (`Code/TrainHub/20_TrainHub.lua` …, `Code/StationRows/…`), listed in `metadata.lua` and
`items.lua` right after it. That needs §8's sentence widened to "one module per `Opt_<id>.lua`,
plus its own parts in `Code/<id>/`". The smokes keep loading the files they load now.
(b) Join each module into its one file. That keeps §8's wording but makes a ~5,600-line hub
file, and every smoke's loader changes.

## Question 3 — names in saves (ban 1)

Recommended: **keep every current name byte for byte**, including the three with `Dev` inside:
the class/template `SMROptInElevatorDepotDev`, its base `SMROptInElevatorDepotDevBase`, and the
upgrade id `SMROptInElevatorDepotDev_Capacity`. Players never see them. Keeping costs nothing:
the owner's dev saves load with this mod as they are.
Renaming means placed depots in those saves fall back to a native class without the depot's
behaviour (audit §1), unless an alias class is kept forever. That is the same contract under a
second name, and a rename to `SMROptInElevatorDepot` would also share the name of the depot's
entity. The hub names (`SMROptInTrainHub6`, `…Base`, the four upgrade ids, every `SMROptIn_*`
field, `HubTrain`, `SMROptInTrackRepair`) have no `Dev` and stay as they are.

**The historical name** `SMROptInElevatorStationDev` (`Building:SMROptInElevatorStationDev`,
the 2026-09-29 look stand-in, removed by `bfd748c`). Recommended: **no compatibility.** It was a
look prototype with no cargo, demolish-before-removal was in its own description, and no
retained save is known to hold one. An agent can scan your Relaunched saves for the string
(decoded first) if you want it proven rather than assumed. Say "scan" or "no".

## Question 4 — Mod Editor saves after the move

Your later template edits (icons, text) become saves of **this** mod, and each save rewrites
`metadata.lua` and `items.lua` without comments. Recommended: **you save as you do now, and the
agent who asked for the save restores the hand-written `metadata.lua`/`items.lua` from git.**
It keeps only what the save meant to change and regenerates the rest, then runs doccheck. Uploads
force the same save, so the release flow needs this step anyway. The alternative, never
saving this mod in the editor, would make template changes hand edits of generated files, which
the repo forbids.

## What the move then does without further rulings

Delegated by the brief, recorded here so you can veto:
- **Player text:** "(dev)" and "DEV ONLY" go; display names become "Elevator Depot" / "Elevator
  Depots". The descriptions are rewritten from the depot and hub as they behave now:
  - the depot's cabin legs and timing, 250/500 and the Expanded Depot upgrade;
  - the hub's power line, which stops promising six stations when Storage Hub raises its draw;
  - each module's removal note (§0).
  The hub icon file loses `_test` from its name. Each change goes through the editor's source
  and your save.
- **Not-player-visible renames, nothing persisted:**
  - log prefixes `[TrainHubDev]` to `[TrainHub]` and `[ElevatorDepotDev]` to `[ElevatorDepot]`,
    with the TestKit filters and 35's readings following;
  - the console table `SMRElevatorDepotDev` to `SMRElevatorDepot`, with its `40`/`45` lookups;
  - `20:189` reads this mod's id as well as the dev id.
- **Records:** D16-D18 for the three modules, and FIX_POLICY inventory rows for everything
  audit §1 found missing:
  - `SMROptIn_floor_hold`, the four depot fields, the depot upgrade id;
  - the `SMROptInTrackRepair` notification;
  - the class, template and persist-base names;
  - the dev mod ids left in saves;
  - the three new Register ids.
- **`tools/upload_preflight.py` widened (OI-18):**
  - admit the asset folders;
  - check that every `Mod/…` path inside them names this mod and resolves on disk;
  - check that every `entities` name has its `.entjson` and every shipped texture is used by a
    material;
  - keep a 5 MB ceiling on everything that is not an asset, so the transcript-junction guard
    stays;
  - accept the generated template files in `code`.

  doccheck's module-set gate learns the same.
- **The dev mods retire:** the folders are deleted, their junctions removed from the game's mod
  folder, and the smokes move with their modules.

**Audit findings left for later, with reasons.** D14(h)'s notification cold-load, L6 C5/C6, the
siding spawn and the conditional 19/21 membership are brief 35's to test, not this move's to
change. OI-27's drone map guard stays parked. The chained-hop tooltip was never built; building
it would be new behaviour. Storage's fixed +19 draw is a design question if you want it per
resource. **No behaviour change is planned or needed;** the spoilage guard and the save-id check
only keep current behaviour working in the new layout.
