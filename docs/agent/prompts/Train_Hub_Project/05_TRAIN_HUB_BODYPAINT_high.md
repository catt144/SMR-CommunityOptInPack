# Train hub: the final body paint — the reactor's feel on the whole structure

**LIVE, one-off.** The owner fires it; the orchestrator parks or deletes it once done. Authoring
state: OptInPack = the commit whose message starts "Brief 05: the body paint handoff"; assets
`264ed18`. Empty `git diff --stat <that sha>..HEAD -- tools/devmods/train_hub/
':!tools/devmods/train_hub/Code/30_TrainHubDrones.lua'` (that file is the drones chain's) and
`git diff --stat 264ed18..HEAD -- trainhub/` (SMR-Assets) mean this brief's facts hold. Start with
`git log`, `git pull` in both repos, then read spec §9 from "Owner asks, 2026-09-22 evening — the
frame line orange-red" to its end: that stretch is the record of every step since brief 01's C run,
with its numbers. Brief 01 (`Parked/01_TRAIN_HUB_STRUCTURE_high.md`) is history: the pipeline
facts, the seam and density measurements and the lights design live there and in spec §9.

## Authority

**Owner, 2026-09-23, looking at the reactor in game (palette P4: navy with polished steel and white
bands): *"Ok for our final paint. This looks so good I think I would like to see something like this
and its overall feel on the final structure."*** The reference is the owner's own screenshot,
`B:\Dev\SMR\SMR-Assets\trainhub\reference\reactor_P4_owner_paint_reference_20260923.png` (git-ignored
folder; ask the owner if it is missing). In words, so you can tell you have the right file: a deep
navy body with panel seams, broad off-white bands with a satin-to-polished finish (the ring band at
the top, a horizontal band at the base, white sleeves on the vertical bollards), dark metal
fittings, the blue trim edge glowing along the seam between navy and white. The navy reads much
darker in game than the raw tint RGB(18,32,78), because it is applied over vanilla's albedo: match
the screenshot by eye, not the number.

The owner has said this is the **last truly big job** and wants one handoff for it: this brief.

**What is HELD by value and does not move** (each an owner ruling, all in spec §9): the road
finish B (`PAD_BASE`, its RM) at every road texel; the deep blue (0,40,255) lines and dashes at
`THIN_SI` .4; the loading spots' frame line forest green `#1B5E20`; the bays gunmetal + yellow
border + three-cube decal (candidate A); the floor plate near-white with the hex relief, dark trim
and deep blue edge strip (the owner said "floor and racks look good"); the siding and dome glass
(clear, roughness .45, no line); every light; the reactor palette P4. Geometry, UVs and spots are
frozen (`concept_freeze.json`; `concept_guard.verify_scene()` before every bake). Nothing in the
Lua changes for this brief.

**What this brief paints:** everything else on the body atlas — the ring's outer and inner faces,
the portal housings, throats, sills and hoods, the dome ribs, the pillars and their caps, the
under-deck, the deck's non-road surfaces, the arm beams' sides, the crown boss and lens ring, the
siding frames' non-line faces. Today they are the warm off-white `SHELL` (#D9D4CA) with brushed
`SILVER` trim, the 2026-09-21 handoff package's palette: that palette is superseded by this ruling.

## End state

1. **A first pass in the game** (prototype first: the owner adjusts by eye): navy panels with
   seams where the reactor has them, off-white bands where the reactor has bands, polished finish
   on the bands, dark fittings. Your call which body groups are navy and which are band: the
   reactor's logic is horizontal bands at the top edge and the base, and white sleeves on vertical
   members — read the ring, the portal hoods and the pillars that way, and say what you chose. The
   blue line work already present on the ring and hoods should sit on the navy/white boundary the
   way the reactor's blue edge does; if it cannot without moving a line (lines are held), say so.
2. **Finish, not just colour:** the reactor reads premium because the bands are polished
   (roughness low, metal high on the white, per-object colorization of vanilla's material). On our
   maps that is the RM: pick the band roughness/metal to match by eye, remembering pass 1's lesson
   (silver at .22/.90 read as a "blurry chrome blob"; .40/.75 held). Navy: satin, low metal.
3. **Seams crisp at the owner's inspection zoom**, as the atlas allows: 14 texels/m on the body at
   the current sizes (BC 4096 supersampled, NM/RM/SI 4096); painted lines that cross the texel
   grid jag, straight island-aligned splits do not (spec §9, pass 3). Prefer colour splits along
   island rows/columns and mesh edges; a curve gets a wider, softer transition on purpose.
4. **Proofs, every run:** `validate_structure.py` PASS 0 failures with the held groups by value
   (extend it per group for the new colours the way the frame line and bays were added — by
   value, gated on the bake proof's own knobs so every held set still validates); the road, lines,
   frames, bays and floor byte-checked or value-checked unmoved; `prove_previous_production.py`
   135/135 and `--legacy` 99/99; `verify_crown_pass.py`; `verify_rim_bleed.py`. Record each proof's
   status line with its command.
5. **One owner texture compile** per pass (paint is texture-only; the body material's four TGA
   paths do not change). Then the owner's look: sector overview and close, day and night. Take
   `snapshot_hub.py hub-bodypaint-<n>-<date>` when they say keep. Iterate as they direct.
6. **Then, and only then, the whole-hub cost reading** (brief 01's step 7, still `<<PENDING-RUN>>`
   in spec §9 "Hub off against on cost"): the owner's reading, same save, fixed camera, hub on
   screen, no trains in view, hub on against off (a stopped hub destroys all its lights and its
   trains), `SMR-Assets\trainhub\blender\gpu_sample.ps1 -Label <label> -Note '<save, camera>'`
   for GPU memory and 3D utilisation (the 120 fps cap hides cost in the frame rate). Report the
   light count with it: `look_smoke.py` gives 144 by day, 163 at night in the shipping defaults.

Done means: the owner looks at the painted hub and says it has the reactor's feel, or names what
stops it, and the cost reading is recorded.

## Facts you would otherwise re-derive

- **The knobs** are in `paint_concept.py` (`SHELL`, `SHELL_ROUGH/METAL`, `SILVER`,
  `SILVER_ROUGH/METAL`, `PORTAL_INSERT`, `HULL`, the per-group painters) and `bake_structure.py`
  (sizes, the proof's KNOBS record, `--legacy-*` flags that reproduce earlier sets byte for byte).
  Bake: `blender --background export/concept/TrainHub_prepaint.blend --python-exit-code 1 --python
  bake_structure.py`, about 190 s for both variants; the prepaint blend must be the body-only one
  (`export_prep.py -- --body-only` first, as 9abe3de's chain shows). Falsify: run it and read
  `export/structure/bake_proof.json`.
- **Groups and masks:** the bake writes `export/structure/group_mask.npy` (2048) and the siding
  pass left 4096 face masks under `export/siding/production/`; texel counts per group come from
  those, SI core = SI ceiling 102. Falsify: `python validate_structure.py` prints the group rows.
- **The validator's second-colour design** is per group, resolved from the bake proof's own knob
  (`knob_colour()` in `validate_structure.py`); a new painted colour joins the same way.
- **The Mod Editor's save drops `Code/30_TrainHubDrones.lua` from `metadata.lua`'s code list**
  every time (five times so far). Restore the line before committing the editor's output; commit
  the dev mod by pathspec. Falsify: `grep -c 30_TrainHubDrones tools/devmods/train_hub/metadata.lua`
  after any save.
- **Restore points:** `snapshot_hub.py <name>` (paired tags + a copy of the git-ignored maps and DDS
  under `B:\Dev\SMR\SMR-Shared\SMR-HubBackups\<name>\`). The last kept state before this brief is
  `hub-green-glass-20260922` (restore point 4); restore point 5 is owed once the owner keeps the
  glass roughness, and the next worker takes it first if it is still missing.
- **The old glass maps, seams sets and `structure_before_*` atlases** are dead sets awaiting the
  owner's word to delete; do not delete them.

## Scope

In: the body atlas's BC, NM, RM and SI for the groups named above, the validator's by-value pins
for the new colours, the two sheets and spec §9, one texture compile per pass, the cost reading.
Out: geometry, UVs, spots, the road and its lines, the frames' line, the bays, the floor, the
glass, every light, the Lua, the reactor. Out-of-scope findings go in the report.

## Stops (report instead of pushing on)

1. A band/navy split the owner wants cannot be made crisp without moving a UV island or a held
   line: show the softest version and the island change it would take.
2. The bake proof or a held-set proof fails after your change and the cause is not your knob.
3. The cost reading shows the lights visibly cost frame rate on the owner's rig: report the count
   and the reading and stop at the largest count that holds.

## Do not claim

Do not claim it has the reactor's feel from a Blender render. Claim the maps you built, the knobs,
the raw sizes, the proofs, and what the owner said in game.

## Deliver

1. Todo list first, one item per commit-and-verify unit.
2. About five steps at a time in a live sitting; the owner watches your context. If they ask you
   to split off, finish the unit in progress, take a restore point if anything is kept, and write
   the next run's brief yourself with `prompt-authoring`: the todo list as it stands, the commits and
   tags, what the owner kept or ruled, and every decision the next worker would otherwise re-derive.
   Point at this brief and the spec; do not restate them.
3. Record in spec §9 with `doc-editing`; commit both repos with pathspecs.
