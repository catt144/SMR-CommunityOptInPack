# Train hub: the look pass — the concept art, in game, first cut

**LIVE, fire when ready.** Asset work in `C:\Dev\SMR-Assets\trainhub\blender`, plus the owner's Mod
Editor import. Authoring shas: SMR-OptInPack `17defc8`, SMR-Assets `54eb84d`. An empty
`git diff --stat 54eb84d..HEAD -- trainhub/` and `git diff --stat 17defc8..HEAD --
tools/devmods/train_hub/` mean this brief's facts hold.

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
the commands and evidence. The live work is now maps, materials, reactor, attachment and import.

**Owner, 2026-09-21 — what this pass is.** *"Give me a good pass at bringing the concept art to life
and that we can see where we are. And iterate from there."* This is a **first cut to look at**, not a
finish. The owner will look at it in game and direct the next round. Do not polish past the point
where they can see the direction; do not hold the import to perfect a detail.

**Owner, same day — the glass.** *"I still want the glass for the loading platforms, the concept art
is wrong about that part, but I like the border and if we can add any of that blue glow into the
glass or around it that would be nice."* And: **leave the dome's glass out for now** — this pass does
the six siding platforms' glass only.

**The concept is the owner's two reference images**, placed 2026-09-21 in
`C:\Dev\SMR-Assets\trainhub\reference\`: **`Concept.png`** (a track close-up) and **`overall.png`**
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
2. **Glass on the six loading platforms**, as its own attached entity with its own material, with
   the border kept in the body and blue glow available in the glass, around it, or both. The glass
   geometry is the existing `SidingPanel_*` pieces, separated by the OI-23 exporter into
   `SMROptInTrainHub6Glass` with shape and position exact; reuse that frozen export.
3. **The generator carries the theme too** (owner, 2026-09-21). The hub's reactor is a visual only:
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
5. ⛔ **No further geometry or UV change after the OI-23 restore point.** The glass split and first
   scripted unwrap are complete; the generator is a new entity. The model is final and a mesh change spends the bake.
   If the look genuinely needs the model to move, that is a stop, not a decision.
6. **Leave the art editable, and say how.** The generating script stays the source of truth with its
   knobs named — strip width, hull colour, glow shapes — and every map is regenerated from it. Never
   hand-edit a baked file the next run overwrites: that is the 0.573 m platform-shift lesson
   (spec §9) in another form. **Your call whether the colour layer is also produced as a
   hand-editable source the owner can paint in an image editor**; the owner has asked what that would
   take, so if you judge it cheap, do it and say so.
7. **Export, and give the owner the Mod Editor import steps** from `blender\README.md`, a few at a
   time, naming the slot for each map. ⚠️ **Whether the editor exposes the SI slot for our material
   type is unverified** — the format supports it; the UI is unconfirmed. Find out on this import and
   record it in `_shared/IMPORTER_FACTS.md`.
8. **The owner looks in game, in day AND at night**, and directs the next round. Then iterate with
   them: small changes, one look each, until they say it is right.
9. **Record** in spec §9 and commit both repos with pathspecs. `doc-editing` first.

**Done means:** the owner can look at the hub in game and say the concept is on screen, and name
what to change next.

## Scope

In: the body's four maps, the glass entity, the themed generator entity, their materials, the
export, the import steps, the owner's looks and the iterations that follow.
Out: the dome's glass; the body's geometry and UVs; vanilla's own materials; the movement Lua and its tunables; per-siding glow logic;
builds 4 and 5; the hub's economy; the ship-size ruling (OI-18 is the owner's).

## Stops

- **The glass entity will not import or will not attach**: report what the importer said and what
  you tried. Do not fall back to putting the glass in the body mesh — that is the route already
  measured to fail.
- **The Mod Editor offers no SI slot** for our material: report it with what the material panel
  shows. The look then lands without glow this round, which is worth seeing on its own.
- **The look cannot be reached without moving geometry**: report what you tried and what each looked
  like, with a render. The model is the owner's.

## Do not claim

Not that the concept is achieved, from a Blender render: a render is not the game's lighting, and
only the owner's eye in game closes it. Not that the glow "works" until it has been seen at night.
Claim what the owner saw, in which conditions, on which save.

## Lifecycle

One-off, but it **survives its first firing**: the owner iterates on the look with the same brief.
Delete it and its row in `docs/agent/prompts/README.md` when the owner accepts the look.
