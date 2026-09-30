# Elevator Depot, the second design pass (brief 26), 2026-09-30

Build **25579348** (`python tools/doccheck.py --emit-fingerprint`, 1.1.1.406343). Source: the archived
tree `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343\Src`. Executed model: Claude Fable 5.1
(`claude-fable-5-1`), the brief's `_high` session. The game was running when the desk work started
(`tasklist`: `Mars.exe` PID 25584); nothing under `Code/` is loaded until the owner's restart.

**State: built, desk-verified, renders approved by the owner (2026-09-30: *"approved"*). Editor session
done, hub save done and smoke PASS. Sitting stopped in batch A on an open defect: a rope outlives its
deleted depot; two fixes did not remove it. The refired investigation checkpoint `493f518` supplies a
read-only CObject inventory and individual inspected-rope removal; the actual saved object still needs
that live inventory. See "Refired investigation" below.** No item is accepted
in the game yet: only the owner's words in their game do that.

## Commits

| repo | commit | what |
|---|---|---|
| SMR-Assets | `c5a8189` | `depot_build.py` (the design pass), `verify_depot.py`, `depot_design_render.py`, `compose_design_pass.py`, the rebuilt blend, exports, proofs, renders and sheets, README |
| SMR-OptInPack | `072f8f0` (code), this report in the commit after it | the dev Lua (signs, receiver, attach listing, `Report()` additions), the two import items, this report, brief 26's row |
| SMR-OptInPack | `493f518` | read-only prop inventory, guarded individual rope removal, terrain-relative `Measure()` repair and desk regression checks; native identification/removal/reload pending |

## The owner's words, recorded before anything changed

From brief 26, verbatim:
1. *"a random floating element"*; *"that tall slab is the same floating element"*.
2. *"the back of the tunnel … is see through"*.
3. *"at the very least it should just be like a black wall like the base game's tunnel, preferably it
   should look a little cleaner like a tunnel entrance that's going below ground just for some flavor."*
4. *"Broken segment, and I would prefer the track of our tunnel to look more like vanilla so it doesn't
   seem as odd."*
5. *"the tunnel should blend more in meeting the ground and kind of look like it's part of the elevator
   structure with its current blending, if possible."*
6. *"The elevator when it's below ground should look more like a shaft, not bare ground."* (The frame in
   the core, `owner_feedback/later_core_frame.png`, is part of this item: orchestrator, `6348d67`.)
7. *"All of these problems also exist on the below-ground version."*
8. *"when the elevator is moving and not at rest it shouldn't look like a shaft if possible, it should
   just look like a platform receiver of some sort."*

## What the facts turned out to be (three fact-finds, tier 2, cited to the 406343 tree)

- **The floating element is vanilla's station sign.** `Station:GameInit` (`Lua/Buildings/Station.lua:132`)
  calls `PlaceUnderconstructionSigns`, which hangs an `UnderconstructionSign` (entity
  `UnderconstructionSignCCP3`) on every `Sign<i>` spot (`Lua/UnderconstructionSign.lua:41-56`). Its mesh
  sits at x -362..-234, z **841..1326** relative to the spot (entities.dat): a hazard-striped block with a
  4.85 m panel, 8.4 m up. Our `Sign2` at (1000, 0) put it on the core rim; our `Sign1` at (-5000, 0) put it
  in the train's path. It hides only when its connector's track has 2+ elements
  (`TrackElement.lua:236-237`), which the owner's screenshots show did not happen.
- **The blue rectangle on the sand is our own `Selection` surface.** The approach strip (-5500..-3500,
  ±180) was in `Selection` and `Collision`; nothing in the Lua draws a connector outline, the connector's
  `TrackGridElement` is `efVisible`-cleared (`TrainTransport.lua:150`), and the strip's size and place
  match the outline exactly. The owner's close-up `later_core_frame.png` shows the same dotted blue
  contour hugging the pads: the selection contour. Hypothesis, settled by one sitting step (B4).
- **Vanilla's straight element** is `TrackCCP3`: one hex long (bbox x -519..517), 2.04 m wide, z
  **853..1069** over its `Enter` spots at 800 (`TrackElement.lua:19`; entities.dat). Pillars are code
  attaches, `TrackPillarCCP3_Base`, every third element and at ends (`TrackElement.lua:26-50, 443-453`).
  The line's last element sits on the direction hex, so it ends at -6000 + 517; our stub started at
  -4500. That one-hex gap is the "broken segment".
- **Below-grade geometry renders only through a `terrain_hole` surface.** Under a building the terrain is
  flattened, never holed (`Building.lua:1522-1545`); the hub's drone pit is a real shaft under z 0 made
  visible by an `eTerrainHole` surface in its entity, probed in game 2026-09-22 and accepted by the owner
  (*"I am fully happy with it"*; `SHUTTLE_HUB_PIT_20260922.md` §2-3, `TRAIN_LOGISTICS_DESIGN_20260917.md`
  :2737-2744). **Vanilla's `SpaceElevator` carries such a disc itself** (its `type 6` surface, r 1126..1180
  at 100 %): our attached copy cannot apply it, which is why the core showed sand.
- **The cabin at 75 %** is 10.3 × 10.75 m and hangs 2.45 m below its origin at rest (bbox z -327..1374 at
  100 %). The parked train's cargo tank roof is at hold -1400 + 479 = **-921**.

## Design calls

| call | why |
|---|---|
| `Sign2` spot dropped; `Sign1` kept, sign removed by the Lua (`layout.signs = false`; `true` puts vanilla's back) | connector 2 is buried, its sign can only float; `Sign1` keeps vanilla's end-of-track semantics for comparison |
| the approach strip stays in `Collision`, leaves `Selection` | picking the deck still selects the depot; the outline no longer lies on the sand |
| the deck starts at **-5485**, vanilla profile, dark top channel, one pillar at -4750 with vanilla's base | no gap, no plank; the owner asked for vanilla's look |
| a real pit under the interior and a well under the core, through a `terrain_hole` surface | the hub's accepted mechanism; vanilla's own elevator expects the hole |
| the rear cap at x -1560, 2.1 m inside the shell's end | vanilla's core ring wall (r 1508) intrudes into the shell's last 1.6 m; the cap now hides it (owner's render comment) |
| the pit floor follows the descent 3.54 m under the track; dark-grey walls; a **black** rear cap; blue guide lines; the box continues under the ring to a black end wall past the hold | reads as a ramp going below grade; the train is never visible under the ring (no hole there) |
| the well: r 4.55 m, floor **-8.8 m**, two blue rings, a plate under the ring's floor; the hole disc r 8.6 m (75 % of vanilla's) | the floor stays 41 cm above the parked train's roof; the cabin sinks through the black floor and is hidden |
| the receiver is a **second entity** (`SMROptInElevatorDepotReceiver`), attached by the Lua at `receiver_z` -300, underground only | one body cannot look different per map; the owner tunes its height live (`Set("receiver_z", …)`) |
| the plinth apron: 3.0 m out at the mouth tapering to 2.0 m, top at the skirt's own step (0.78 m), navy stripe, wings at the mouth | the pads' base band, continued |
| **the footprint gains six hexes** (row ±1 under the skirts, 24 → 30) | the hole strip must lie inside the building's own hexes (the hub's caution); the skirts already covered them; connector, direction, arrival and hold spots are unchanged |

Not changed: the approved exterior (every one of its 7,758 faces survives, checked), the connector
geometry, the train spots, the elevator's scale and turn, vanilla's elevator, tunnel and track art.

## Per item: the render, what changed, what the owner said

Renders: `SMR-Assets/elevatorstation/blender/review_design_pass/` (`index.html` shows each owner
screenshot beside the render from that angle; `sheet_*.png`). The portal, deck, pit, well, apron and
receiver are export geometry; the elevator is a dimensioned proxy; the ground is a plane with the
entity's hole cut out, which is what the game's hole grid should do. Blender lighting, not the game's.

| item | render | what changed | owner |
|---|---|---|---|
| 1 floating element | `sheet_1_floating_element_and_open_back.png` | `Sign2` gone from the entity; `Sign1`'s sign destroyed after `Station:GameInit` and on load | not yet seen |
| 2 open back | same sheet (right), `sheet_2_portal_interior.png` | one closed slab across the shell at **x -1560**, black inside, ivory outside, to 0.4 m below grade; the verifier's nine rays from behind all stop at x -1554. First cut sat at -1349, and the owner's look at that render: *"the back side looks a little un natural like its bleed through from the model behind it"*: vanilla's ring wall (r 1508 at 75 %) stands inside the shell's last 1.6 m, so the cap moved in front of it (Assets `718390f`) | render seen, cap moved; game not yet |
| 3 interior | `sheet_2_portal_interior.png`, `sheet_5_interior.png` | a dark-grey deck at grade for 5 m, then the pit floor descending with the track (3.54 m under it) to -11.5 m at the rear wall and -17.5 m under the hold, dark-grey walls, blue guide lines at wagon height, black rear cap, black end wall at +12 m | not yet seen |
| 4 track join | `sheet_3_track_join.png` | deck from -5485 to the mouth and on down the descent; 2.04 m wide, 8.53..10.69 m, dark channel on top, pillar at -4750 with vanilla's base; no approach strip in `Selection` | not yet seen |
| 5 blend | `sheet_4_blend_and_core.png` | the apron along both feet, wings at the mouth, navy stripe | not yet seen |
| 6 core shaft | same sheet (right) | the hole disc and the well; the frame inside the core: `Report()` now lists the elevator art's attaches with their z ranges, and `Set("elevator_hide", "<entity>")` removes a named one, if the frame is an attach (if it is baked into vanilla's mesh it stays; stop 1) | not yet seen |
| 7 underground too | the same entity on both maps | items 1-6 are the entity and the Lua, identical on both maps; the hole cuts the cave floor the same way (unproven there) | not yet seen |
| 8 receiver | `sheet_6_receiver.png` | grey landing floor 3 m down with a blue ring and three cradles; underground only; `receiver_z` live | not yet seen |

## Verification (desk; the in-game hole, the look and the train are the sitting's)

`blender --background --factory-startup --python-exit-code 1 --python verify_depot.py` →
`export/verify_depot.json`, **PASS** (`failures: []`). Read from that file:

| figure | value |
|---|---|
| footprint hexes (independent derivation = exported) | 30 |
| spots | 13 (Sign2 dropped), worst position error 9.5e-6 units |
| approved exterior faces preserved / design-pass faces added | 7,758 / 3,263 |
| `terrain_hole` faces / vertices, all inside footprint hexes | 64 / 89 |
| mouth headroom at lanes ±335 (roof - 1236) | 218 units, floor none |
| rays: threshold deck, ramp floor, hold floor, pit walls, rear cap (inside and 9 from behind), end wall, well floor, well wall, plate, deck top at -5000 and -3650, deck end at -5485, pillar foot, apron top and wing | all hit at the designed position with the designed facing |
| cargo tank envelope (±509) inside the pit solid below grade | none (the engine's ±545 touches the chamfer only where brief 25's liner is already narrower than the engine: 10 samples past x -2000, recorded) |
| roof clearance over the wagon top under the well | 26 units (the well's floor slab) |
| UVs outside / zero-area | 0 / 0 |
| receiver | one mesh, r ≤ 440, z -12..40, shared material, sha in the proof |
| dev Lua | `design_spots` = the 13 spots; `elevator_angle` 90; `signs = false`; `receiver_entity`, `receiver_z = -300` present |
| import items | 13 spots, surfaces `hex_shape`, `selection`, `collision`, `terrain_hole`; the receiver's item with its ScenePath and material |

`python tools/parsecheck.py --dir tools/devmods/elevator_station/Code`: 2 files, 0 errors.

## The editor session (owner), then the hub check

Also in `SMR-Assets/elevatorstation/blender/README.md`, "The owner's import for the design pass".

1. Start the game, **Mod Editor**, open **DEV ONLY - Elevator Depot (look prototype)**.
2. EntitySpec **`SMROptInElevatorDepot`** → MeshSpec `mesh` → **Open in Importer**. ScenePath
   `B:/Dev/SMR/SMR-Assets/elevatorstation/blender/export/SMROptInElevatorDepot.fbx`. The selectors should
   show 13 `-` spots and four surfaces, `terrain_hole` among them as a sibling of `Collision` (never nested
   under it: the hub's first try). If stale, RootNode → **Fill selectors**, material
   **SMROptInElevatorStation**. **Import.**
3. **Ctrl-Alt-A** → new EntitySpec id **`SMROptInElevatorDepotReceiver`**, Class Parents empty, Category
   Buildings → **Save the Art Spec** → its `mesh` → **Open in Importer** →
   `.../export/SMROptInElevatorDepotReceiver.fbx`, material **SMROptInElevatorStation** → **Import.**
4. **Save the mod.**
5. Open **DEV ONLY - Train Hub (Module B build)** (`SMR_TrainHubDev_20260918`) and **save it**: brief 22's
   fourth upgrade slot regenerates only on that save.
6. Quit. The agent runs `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated`
   (must PASS) and checks the depot mod's `metadata.lua` (both entities, three code lines) and
   `_EntityData.generated.lua`. Then restart.

## The sitting: batches, one prediction per step

Console lines where no SMRTK slot fits; about five steps a batch; the owner clicks and reads, the
orchestrator reads the log on flush. Fixture: **double hub+elev**. **Fresh placements** on both maps:
the footprint changed.

**A, editor session, restart, the hub check**
- A1 steps 1-6 above. Prediction: the importer lists `terrain_hole`; the smoke prints PASS with no "OWNER
  STEP OWED" line; `metadata.lua` lists both entities.
- A2 load the save; console `SMRElevatorDepotDev.Report()`. Prediction, per existing depot: the dressed
  line ends `receiver=false signs=0` (surface) / `receiver=true` (underground); the new line reads
  `terrain_hole=true bbox=…`, `entity imported`, `hexes=30`; then `elevator attach N entity=…` lines
  (this is where the core's frame gets its name, if it is an attach); no Lua error.
- A3 demolish the two old depots (their hexes predate the footprint change).

**B, surface**
- B1 place a fresh depot ≥ 100 m from other stations, connect the line. Prediction: `Report()` shows all
  13 spots MATCH; connector 1 carries a `TrackGridElement`.
- B2 the owner's first angle (behind the core). Prediction: no hazard block on the rim, no slab at the
  connector; the shell's back is closed.
- B3 the track angle. Prediction: the vanilla track meets our deck at the direction hex with no gap; the
  deck has a dark channel and one pillar; inside, a dark floor and a black back wall, the beam diving
  into a pit. Sand nowhere inside.
- B4 select the depot. Prediction: the blue contour hugs the pads and the shell's feet; no rectangle on
  the sand in front of the mouth. (If a rectangle still shows, the outline is not ours: report it.)
- B5 the top-down angle, one cabin cycle. Prediction: the apron reads with the pads' base band; in the
  core, dark walls and two blue rings, never sand; the cabin sinks into the well and vanishes below its
  floor; when it returns it rests in the ring as before. The frame: name it from A2, then
  `SMRElevatorDepotDev.Set("elevator_hide", "<entity>")` to compare.

**C, underground**
- C1 fresh placement, connect. Prediction: as B1.
- C2 B2-B4 again on the cave floor. Prediction: the same; the hole cuts the cave floor.
- C3 the core: the cabin at rest sits in the receiver; when it rises, the receiver shows (grey floor, blue
  ring, three cradles), not a shaft. Tune with `Set("receiver_z", -250)` / `-350`.
- C4 `Report()` on this map. Prediction: `receiver=SMROptInElevatorDepotReceiver (entity imported)`.

**D, brief 22's five steps** (`TRAIN_HUB_STORAGE_20260929.md`, "Short attended smoke"): old-save load
with slot 3; station pads with slot 4 and slot 6; the Storage Hub purchase; power and switch; full-depot
export. Predictions are in that report; the fixture is the owner's hub save with Capacity Network.

## What I did not do, and the risks the sitting carries

- **The terrain hole is unproven for this entity.** The hub's works; vanilla's elevator has one; ours is
  authored the same way. If the engine clips a hole to the footprint, ours lies inside it now. If the
  hole does not appear, the pit and well are hidden under flattened sand exactly as before, and the
  fallback is vanilla's own trick, a black deck at grade (the swatch exists; one constant).
- **The frame in the core** may be baked into vanilla's mesh; then it stays and shows against the well.
  Stop 1 territory if the owner wants it gone.
- **Brief 25's liner clips the train's engine past x -2000** (the approved shell narrows to 4.9 m at the
  rear; the engine is 5.45 m across the lanes). Pre-existing, not touched; the pit's chamfer follows the
  liner there and adds nothing beyond it. Recorded as `engine_inside_solid_below_grade_informational: 10`.
- **The receiver's fit** to the cabin's underside is a guess (55 cm under the cabin's lowest point at
  rest, cradles 30 high): `receiver_z` is live for that reason.
- The ring wall's real radius at 75 % is the footprint fit (1508), not a mesh measurement; if the art's wall is
  smaller, the cap simply sits 2 m early, sealed either way.
- The renders' elevator is a proxy; the dark ring floor's real height is unknown, so the well's plate
  (z -5..-15) and wall top (-5) may sit a little above or below vanilla's floor edge. Cheap to move.
- Not done: any wiring, drone crew, twin placement, train movement; the dome build; the rail shaft.

## Refired investigation, 2026-09-30

Executed model: Codex / GPT-6, as identified by this session's runtime; a more specific model identifier
is not exposed. Start: OptInPack `d7bd329`, Assets `2c47118`. `git log --oneline -3` and `git pull` ran
in both: OptInPack was current; Assets has no remote/upstream (`git remote -v` is empty), so its pull
reported no tracking information. Its existing untracked train-hub blend backups were left alone.
`python tools/doccheck.py --emit-fingerprint` read installed build **25579348** and was GREEN.
`tasklist /FI "IMAGENAME eq Mars.exe"` found no game process before the code write. No assets changed
and no new Mod Editor session is needed for this checkpoint.

### What is established, and what is not

- **LOG:** the prior failure is reproduced in the preserved
  [15:52 log](../../archive/elevator_rope_20260930/Mars.exe-20260930-15.52.26-6aba6e65.log):373,508:
  the existing `Sweep()` reports no removed props. The earlier
  [15:27 log](../../archive/elevator_rope_20260930/Mars.exe-20260930-15.27.38-6aba6e65.log):338,365
  records the two depots' `CheatDelete` operations, handles 7985 and 8404. These logs establish the
  actions, not the residual rope's identity or why it survived.
- **SOURCE, build 25579348 / archived `1.1.1.406343/Src`:**
  `Lua/_EntityData.generated.lua:20651-20658` gives `SpaceElevatorRope` no `class_parent`;
  `CommonLua/Classes/EntityClass.lua:9-12,50-65` supplies `EntityClass -> CObject`.
  `CommonLua/Classes/_object.lua:3-9` distinguishes `Object` with Lua storage from `CObject`.
  Thus the old `AllMapsForEach("map", "Object", ...)` excludes this generated rope class.
  The actual object's runtime `Object=false` reading remains the live confirmation.
- **SOURCE:** `CommonLua/Core/persist.lua:188-200` makes `DeleteOnLoadGame` a persisted list followed by
  destruction in `PersistPostLoad`; it does not prevent initial serialization. Clearing `gofPermanent`
  alone has not been proven to keep these visuals out of a save. The previous commit's "never saved"
  wording is not a verified guarantee. No further automatic migration was added on that assumption.
- **SOURCE + desk reproduction:** the handoff's scale/bbox explanation for `Measure()` was wrong.
  The recorded revision `0ba4a1e` has `o:GetPos():z() - ground` at line 354, the line named by the
  [12:23 log](../../archive/elevator_rope_20260930/Mars.exe-20260930-12.23.04-6aba6e65.log):4329.
  Terrain-relative positions lack an explicit Z. `CommonLua/LuaExportedDocs/Game/GameObject.lua:510-515`
  documents `GetVisualPos()` with terrain-resolved Z. The checkpoint uses it and the nil-Z fixture
  completes the measurement. The native ceiling measurement is still owed.
- **READ-ONLY SAVE CHECK:**
  `python docs/archive/elevator_rope_20260930/read_save_v2.py` assembled BPUL fragments, decompressed
  the ZSTD members, checked decoded lengths and the trailing frame-offset tables, and confirmed the
  original save hash unchanged:
  `58eeffe7f249a8ba03820d29bc31ed1969c59571e4cf86d1b6e4a69c1e7b2355`.
  Token filter `SpaceElevatorRope|SpaceElevatorCabin|SMROptInElevatorDepot|smr_depot_prop` found only
  depot-name tokens: **5 = 2 metadata + 3 persist + 0 persist.terrain + 0 screenshot**. A subsequent
  `rg -n -a --count 'SpaceElevatorRope|SpaceElevatorCabin|SMROptInElevatorDepot' scratch/elevator_rope_20260930/save_decoded`
  confirmed the positive side after decompression. Native object records are not decoded, so missing
  rope-name strings do **not** prove missing ropes. Revision 1 of the archived reader rejected the
  trailing offset table; revision 2 verifies it. Both are preserved; neither wrote the save.

### Checkpoint behavior and validation

`InspectProps()` visits `CObject`s across loaded maps and their attachments, deduplicates them, and
lists entities containing `Elevator`. Each row prints class, entity, object reference, map, logical and
visual positions, scale, parent, ownership, flags, `Object` membership and delete-on-load membership
(or `unavailable` if that table cannot be read). Ownership includes current depot rigs, previews and
vanilla `SpaceElevatorBase.pod/ropes`, whose source is `Lua/Buildings/SpaceElevator.lua:56-69` on the
same build. The census is read-only and retains its rows for the current loaded session.

`RemoveInspectedRope(index)` removes only that inspected object: entity `SpaceElevatorRope`, 75% scale,
underground, parentless and unowned, with map, position, entity and scale unchanged since inspection.
It re-reads ownership, prints the exact pre-delete row and `valid_after`, and rejects stale/owned rows.
It never runs on load. The older broad `Sweep()` remains unchanged while the actual residual is unknown.
The load handler clears inspection rows. Identifying a row in the owner's game precedes its removal.

Commands run at `d7bd329` plus the code/test diff committed as `493f518`:

| command | result and limit |
|---|---|
| `python tools/devmods/elevator_station/tests/props_smoke.py` | PASS, Lua 5.5: old Object filter omission reproduced; CObject census includes the rope; no census deletion; guards protect depot, preview, vanilla, attached, surface, non-75%, non-rope and stale objects; exact removal and repeat refusal; nil-Z measurement and load invalidation. Mock world, not native serialization. |
| `python tools/parsecheck.py --dir tools/devmods/elevator_station/Code` | PASS: 2 files = 2 parsed + 0 errors. |
| `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated` | PASS; generated upgrade fields still match. No hub code change. |
| `git diff --check`; commit hook `python tools/doccheck.py` | PASS; doccheck GREEN. |

### First live batch, before A3

Console use remains authorized by brief 26: the shared SMRTK slots carry the hub sitting and do not
have this new inventory. The owner clicks/reads; the agent reads the flushed log.

1. **R1 [NEVER RUN]:** start the game on checkpoint `493f518`, load **double hub+elev**, switch
   underground, run `SMRElevatorDepotDev.InspectProps()`, then SMRTK Sitting **Flush + copy**.
   Prediction: rope rows include `Object=false`; current attached ropes show their depot/parent, while
   a leftover at the reported bare-floor position has `owner=UNOWNED` and no parent. A failed prediction
   is new evidence, not permission to widen deletion. Native identity is still PENDING.
2. **R2 [NEVER RUN; depends on R1]:** the agent supplies the exact row index or indices from that run
   after reconciling map, position and ownership with the visible leftover. Run
   `SMRElevatorDepotDev.RemoveInspectedRope(index)` for those rows. Prediction: only the identified
   leftover disappears, with `valid_after false`; the existing depot and vanilla elevator retain
   their ropes/cabins. Re-running the census or reloading invalidates previously supplied indices.
3. **R3 [NEVER RUN]:** run `SMRElevatorDepotDev.InspectProps()` again and flush. Prediction: the removed
   rows are absent; owned ropes remain. Save under a new name, **double hub+elev rope check**, and reload
   that new save. The original remains available as the reproduction fixture.
4. **R4 [NEVER RUN]:** repeat the inventory and the bare-floor view after reload, then flush. Prediction:
   no rope returns at the repaired position and no new Lua error. Only this establishes a durable repair
   of the saved leftover; it does not establish prevention for fresh depots.
5. **R5 [NEVER RUN]:** resume A3, remove the old depots, and inspect before/after to check their attached
   ropes are destroyed. Then begin B/C's fresh placements and looks, followed by D's hub smoke.
   Prediction: fresh deletion leaves no unowned rope. Native save/cleanup behavior remains open until
   these observations pass.

### Open work and finding disposition

| finding/work | home and next action | disposition |
|---|---|---|
| saved rope, Object-filter omission, legacy persistence uncertainty | this section; R1 identifies, R2-R4 repair/verify, R5 tests current deletion | source issue established; native result pending |
| Measure nil-Z crash | checkpoint `493f518`; next underground `Measure()` | desk repaired, native reading pending |
| missing `Top` spot | brief 26's existing handoff; add at shell crown at the next needed re-import | deferred; no new import requested |
| receiver root `ReceiverOrigin` | existing handoff, Assets `2c47118`, already-imported item | settled; preserved |
| renders/import and hub save | this report's editor section and hub smoke above | settled; no repeated approval/save request |
| eight game looks and brief 22 smoke | B/C/D above, after R batch and A3 | owner acceptance remains open |

The inherited handoff was retained and linked to this section; no unhomed content was removed.
No fresh game run, original-save modification, geometry/import, vanilla-art change, movement change or
hub-code change occurred in this investigation checkpoint.
