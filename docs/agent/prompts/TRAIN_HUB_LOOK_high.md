# Train hub: the look pass — the concept art, in game, first cut

**LIVE, RESUMING STAGED (owner, 2026-09-21).** The rebuilt body and
concept maps are imported (`7c3e74c`) and the owner has looked: glow works, but the hub reads as
*"blue paint"* and blurry up close. Measured cause, spec §9 "The first concept import in game":
the maps are correctly compiled at vanilla's own format and size but almost unpainted — normal
97.9% flat, base colour 84.2% one value. The earlier zero-metalness RM claim is corrected by
the full histogram in spec §9. The owner's AI texturing trial found no usable tool and is closed; the look goes by bake onto our UVs. The owner's handoff package, the
pad direction and the four steps are in spec §9. The order is now theirs: **road surfaces first,
owner inspects, then structure, lights, fine normal.** Glass and the themed reactor stay deferred. Asset work in
`B:\Dev\SMR\SMR-Assets\trainhub\blender`, plus the owner's Mod
Editor import. Authoring shas: SMR-OptInPack `df6ef4c`, SMR-Assets `09bd145`. An empty
`git diff --stat 09bd145..HEAD -- trainhub/` and `git diff --stat df6ef4c..HEAD --
tools/devmods/train_hub/` mean this brief's facts hold.

**Step 1 delivered, assets `ea82ef4`:** `textures/pad/` has shared BC/NM/SI and
A_BlackGlass / B_BlackMirror RM variants. See spec §9 and the assets README's current handoff.
Every non-pad texel is unchanged; geometry/UV guards pass. **Owner, 2026-09-21: B is better, held
provisionally** (spec §9): if the glow lights make the reflections act up the road surface is
reopened, so the lights step judges glow lit at night on this surface. The map change needed the
importer run, which compiles the DDS.

## Authority

**The texture gate is LIFTED** (owner, 2026-09-21; spec §9 holds both rulings and what the gate
protected). The transitions convinced the owner and the model is final — *"everything fits and
nothing clips"* — and that final model is committed in both repos. Textures, materials and the
glass are now open work.

**OI-23, owner 2026-09-21: the first unwrap and panel separation are APPROVED.** Preserve every
piece's exact shape and position. The unwrap is scripted and deterministic; UV fingerprints must
fail on layout drift; the existing geometry proof must pass. The completed preparation is held
at the paired `hub-prepaint-uv-frozen-20260921` tags before any paint bake. Assets
`concept_freeze.json` is the baseline; `export_prep.py` checks it and exports separate body/glass
entities without baking. Use `concept_guard.verify_scene()` before every bake. The model is
frozen again: further geometry or UV changes are a stop. Spec §9 and `blender/README.md` carry
the commands and evidence.

**Iteration 1 prepared, 2026-09-21:** the centre exception below is implemented as a single plate
meeting six track legs. The prior geometry proof, exact unchanged-object hashes, crossing
silhouette/overlap checks, repeated UV fingerprint and body FBX round trip pass. The new freeze
is held at paired `hub-centre-uv-frozen-20260921` tags before rebaking. The body's maps in
`textures/concept/` now carry the relaid approach lights and continuous radiating floor curves.
The live work is one body re-import from `export/concept/SMROptInTrainHub6.fbx`, with the four
updated maps, then the owner's centre/day/night look. Follow the body-only handoff in
`blender/README.md`. The first import confirmed the SI slot; game glow acceptance remains open.
The older glass/reactor outputs are deferred, not current delivery; a later reactor pass must
regenerate its body-atlas sampling UVs. This is not in-game acceptance; the lifecycle still holds.

**Owner, 2026-09-21 — what this pass is.** *"Give me a good pass at bringing the concept art to life
and that we can see where we are. And iterate from there."* This is a **first cut to look at**, not a
finish. The owner will look at it in game and direct the next round. Do not polish past the point
where they can see the direction; do not hold the import to perfect a detail.

**Owner, same day — the glass.** *"I still want the glass for the loading platforms, the concept art
is wrong about that part, but I like the border and if we can add any of that blue glow into the
glass or around it that would be nice."* And: **leave the dome's glass out for now** — this pass does
the six siding platforms' glass only.

**The concept is the owner's two reference images**, placed 2026-09-21 in
`B:\Dev\SMR\SMR-Assets\trainhub\reference\`: **`Concept.png`** (a track close-up) and **`overall.png`**
(the whole hub). That folder is git-ignored and also holds the vanilla reference pack, whose
`README.md` maps every file in it and names the vanilla materials. In words, so you can tell
whether you have the right files: a **maglev read** — a near-black track deck carrying bright blue light strips down its
centre and flowing curved light lines across its surface, framed by clean off-white panels with blue
rim lighting along their edges; portals as white arches with glowing inner rings; the whole thing
reading bright and clean at distance, with the glow doing the work. ⛔ **Ask the owner if those two files are missing or do not match this. Do not invent the concept from this paragraph** — it is a check on the files,
not a substitute for them.

## Facts that decide how you author this (read 2026-09-21; spec §9 carries them with citations)

- **Self-illum is a supported map but a ONE-CHANNEL BC4 mask** (`GFXMaterial.lua:137`, `:1100`,
  archived 1.1.0.403908). It says *where* a surface glows, never what colour. Blue strips are blue in
  the base colour with white in the SI mask along the same shapes. Author them as clean shapes in
  both, because the shapes are what later passes and the glow logic both cut from. ⭐ Vanilla's own
  stations ship an `EM` map beside `BC`/`CM`/`NM`/`RM` (the reference pack's `README.md`, read from
  `Materials.fpk`), so the glowing-track look is the game's own, not something we are inventing.
- **The game modulates that glow from the working state already.** `WorkLightsOn/Off` are
  `SetSIModulation(200)` / `(0)` (`Lua/Buildings/Building.lua:1413-1419`) from `OnSetWorking`, so the
  hub darkens when it stops working with no code from us. Driving it per-siding is a later pass, not
  this one — but **keep each siding's glow on its own shapes in the mask** so that pass is possible.
- ⛔ **One material per mesh node, and a second node is discarded silently** (`SceneImport.lua:4023`,
  and MEASURED 2026-09-20, `_shared/IMPORTER_FACTS.md`). The body is one mesh with one material.
  Everything that is not the glass lives in those maps.
- ⭐ **The glass is a SEPARATE ATTACHED ENTITY, which is how vanilla builds every dome's glass:**
  `DomeBasic_Glass`, `DomeOval_Glass`, `DomeMega_Glass`, attached at the dome's `Origin`
  (`Lua/Buildings/Dome.lua:501`, `:3042-3075`). Its own entity means its own material, so its own
  transparency (`BlendType`) and its own SI. The hub already attaches visuals
  (`20_TrainHub.lua:1038-1057`), so the attach mechanism is in place.
- **The import copies textures into the mod as DDS.** Three 4096 maps were 44 MB. `PACK_MAX_BYTES` is
  5 MB and is **our own constant, not a platform limit** (spec §9), and the owner's ruling on ship
  size (OI-18) is still open. **Choose the smallest resolution that carries the look**, say what you
  chose and what it costs, and do not treat 4096 as the default.

## End state

1. **The body's maps bring the concept to life**: base colour, normal, roughness/metal, and the SI
   glow mask, built for the final geometry. The look is judged against the owner's references, not
   against vanilla.
2. **DEFERRED to a later session: glass on the six loading platforms**, as its own attached entity with its own material, with
   the border kept in the body and blue glow available in the glass, around it, or both. The glass
   geometry is the existing `SidingPanel_*` pieces, separated by the OI-23 exporter into
   `SMROptInTrainHub6Glass` with shape and position exact; reuse that frozen export.
3. **DEFERRED to a later session: the generator carries the theme too** (owner, 2026-09-21). The hub's reactor is a visual only:
   vanilla's `FusionReactor` entity attached as a `ShapeshifterAutoAttach`, scaled 75%, 45 m out
   (`20_TrainHub.lua:1033-1066`). Left alone it is the one vanilla-styled object in a themed hub.
   ⛔ **Never restyle vanilla's own material to achieve this** — that repaints every fusion reactor
   in the player's colony. The route is our own entity, themed, attached in its place: the same
   `ChangeEntity` call with our entity name, so the working-state FX and the offset logic are
   untouched. It is new geometry in a NEW entity, which does not disturb the frozen body mesh — the
   same shape of change as the glass. **Your call on how far to take it:** a simple themed form that
   reads right at distance beats an elaborate one, and the owner iterates. If a material can be
   shared between entities, share the body's rather than adding a third set of maps, and say whether
   that worked — it is likely but unverified.
4. ⛔ **No dome glass this pass** (owner). The dome stays as it is.
5. ⛔ **No further geometry or UV change after the centre restore point.** The owner-approved
   centre exception below is complete and refrozen; the generator is a new entity. The model is final and a mesh change spends the bake.
   If the look genuinely needs the model to move, that is a stop, not a decision.
6. **Leave the art editable, and say how.** The generating script stays the source of truth with its
   knobs named — strip width, hull colour, glow shapes — and every map is regenerated from it. Never
   hand-edit a baked file the next run overwrites: that is the 0.573 m platform-shift lesson
   (spec §9) in another form. **Your call whether the colour layer is also produced as a
   hand-editable source the owner can paint in an image editor**; the owner has asked what that would
   take, so if you judge it cheap, do it and say so.
7. **Give the owner ONE body import** from `blender\README.md`, a few steps at a time, naming the
   slot for each map. The first import confirmed BC, Normal, RM and SI in the editor-generated
   material, recorded in `_shared/IMPORTER_FACTS.md`. Do not hand the owner glass steps this pass.
8. **The owner looks in game, in day AND at night**, and directs the next round. Then iterate with
   them: small changes, one look each, until they say it is right.
9. **Record** in spec §9 and commit both repos with pathspecs. `doc-editing` first.

**Done means:** the owner can look at the hub in game and say the concept is on screen, and name
what to change next.

## Iteration 1 — the owner's first look in game (2026-09-21)

The body imported with all four maps and the owner looked at it. Two findings, both theirs.

1. ⛔ **Z-FIGHTING AT THE CENTRE CROSSING, and it is a geometry defect the paint exposed.** The
   generator builds each of the three lines as one box spanning the hub (`hub_skeleton.py:343-350`),
   so at the centre three boxes overlap with their top faces **all at `DECK_Z`** — coplanar, so the
   renderer flips per pixel and the owner sees a crawling stippled band. Untextured it was invisible
   because every surface was the same flat grey. No map can fix it.
   **Owner ruling, 2026-09-21: APPROVED to change this geometry**, an exception to the freeze for a
   defect, with shape and position preserved everywhere else and the geometry and UV proofs re-run.
   **Your call between merging the three beams into one solid at the centre and stopping them short
   of a single centre plate** — the plate is preferred if it can carry the centre floor design below,
   which is what the owner will be looking at. Re-bake and re-freeze after; the paint is generated
   from face identity, so a re-bake reproduces the look.
2. **The lighting layout is redesigned** (owner, same look; the concept has no dashes in the
   interior). In their words: *"have the dashes along the outer platform where the train meets up
   with the old vanilla track, and then as it heads towards our center track the two platform dashes
   merge together and ends in the tunnel, and then we have our floor design in the center."* So:
   - **dashes on the transition arms**, where a train is still on the vanilla track, one line per
     arm either side of the incoming track;
   - **inward, the two lines converge and MERGE into one**;
   - **the merged line runs into the tunnel portal and ENDS there**;
   - **no dashes inside the ring**: the centre carries the radiating floor design of `Concept.png`
     instead. The centre plate above is its natural home.

**Sequencing, owner 2026-09-21: the centre fix and the relaid lights FIRST, alone.** The glass and
the themed reactor are **DEFERRED to a later session** — *"if the glass is harder we can focus on the
center fix and another pass at the concept work and then deal with the other stuff."* Reason: the
centre fix rebuilds and re-imports the body regardless, so anything imported now is imported twice,
and the glass's one-time setup (a new Art Spec, a new material, and a blending option whose wording
nobody has seen) is the step most likely to throw a surprise. Until the glass entity exists the
sidings are bare frames, and until the reactor entity exists **the vanilla `FusionReactor` visual
remains** — both expected, neither a fault. Hand the owner ONE import round: the rebuilt body.

## Scope

In now: the proved centre fix, relaid body lights, body export/maps and one import/look round.
Deferred: the separate siding glass and themed reactor, their materials/imports and acceptance.
Out: the dome's glass; further body geometry/UV changes; vanilla's own materials; the movement Lua and its tunables; per-siding glow logic;
builds 4 and 5; the hub's economy; the ship-size ruling (OI-18 is the owner's).

## Stops

- **In the later glass session, the entity will not import or will not attach**: report what the importer said and what
  you tried. Do not fall back to putting the glass in the body mesh — that is the route already
  measured to fail.
- **The body re-import fails**: report the importer error and preserve the owner's existing setup.
- **The look cannot be reached without moving geometry**: report what you tried and what each looked
  like, with a render. The model is the owner's.

## Do not claim

Not that the concept is achieved, from a Blender render: a render is not the game's lighting, and
only the owner's eye in game closes it. Not that the glow "works" until it has been seen at night.
Claim what the owner saw, in which conditions, on which save.

## Lifecycle

One-off, but it **survives its first firing**: the owner iterates on the look with the same brief.
Delete it and its row in `docs/agent/prompts/README.md` when the owner accepts the look.
