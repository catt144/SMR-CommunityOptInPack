# Arboretum — custom model, staffing, upgrades and display beds: continue the owner's look

One-off. Authored 2026-10-04 at `81c75a5`; rewritten as a handoff 2026-10-05 at `0de88e6`;
checkpoint committed 2026-10-21 on the owner's instruction, unaudited. Delete this file and its row in
`docs/agent/prompts/README.md` in the commit that closes the work.

## Where it stands

The owner has the Arboretum in the game: a small glass dome on the Large Garden's footprint with a
visible Seeds pile, and has been steering it by eye. Since their last look the planting was
rebuilt round three display beds and the building became a staffed service with three upgrades.
The owner saw it in a colony on 2026-10-05 and ruled twice (D19): colonists walk through the glass,
and the upgrade beds look worse than the base Herb; *"do a plus our own"*. Built since, not yet
imported: a collision ring on the pavilion, beds always in bloom that grow by scale and tint per
variety, and three custom bloom entities. Details in the report's last section.

Read, in this order: [D19](../bugs/D19.md) (every owner ruling, verbatim, dated; the authority),
then [the report](../reports/ARBORETUM_MODEL_20261004.md) from §"Import, readback and menu loads"
to its end (what was measured, what was not, what is stale). §"Agreed design" below is the design
those rulings add up to.

**Checkpoint committed, nothing audited.** The owner chose to import and play before the
different-model audit, and on 2026-10-21 asked for the current state to be committed (*"it has
kept the tree dirty for awhile now"*); the audit still covers everything in those commits. Trees:

- `SMR-OptInPack`: `staging/` (module code, template, tools, imported assets), `docs/`
  (D19, this file, the report, FIX_POLICY row 36, `docs/archive/arboretum_model_20261005*/`).
- `SMR-Assets`: `arboretum/blender/` (pavilion builder, verifier, previews, crop survey) and
  `arboretum/blooms/` (the three bloom clumps); exports whitelisted in `.gitignore`.
- `SMR-BugFixPack-TestKit`: `Code/80_AgentSlots.lua` (the sitting slots), committed there.

## Live work

1. **In progress: the import round and the owner's look.** The owner imports the pavilion and the
   three blooms (steps at the end of this file), then the hand restore, activation, readback and
   menu loads run, then the look: door routing, beds growing and tinting, and the first batch's
   still-owed readings (panel, jobs, showpieces). Fold their words into D19 and the report.
2. Bring the records and tools level with the code (list under "Known stale").
3. The different-model audit of the whole tree, on the owner's model pick, then commit.
4. Close: consume this prompt.

## Agreed design (owner, 2026-10-05; words in D19)

Prototype first: rough and in the game; every number is a named constant the owner will move.

- Staffed service, no required specialization, 2 workers per shift. Performance: unstaffed 100
  (the large park's); staffed with Seeds 125 with one worker, 150 with both, or the workers' own
  when higher; staffed without Seeds 100. Never shuts for lack of Seeds or staff.
- Seeds are used by the staff: 1 per staffed shift, none unstaffed; store 30.
- Upgrades: Service Bots (full staff with no colonists, with the tech); Seasonal Blooms (visitors
  gain Comfort, Melancholics also Sanity; beds grow and rotate; +1 Seed a shift); Rare Specimens
  (Comfort 15 to 20, more capacity, showpieces on the two `Specimen` spots; +1 Seed a shift).
- Three display beds (`Cropbed` spots, clear 800 circles): the base building shows Herb in bloom;
  with Seasonal Blooms each bed grows a crop over one sol, holds at its bloom stage, and is
  replanted with the next variety next sol, staggered by a third of a sol. Base-game crops only.
- The two `Specimen` spots (clear 500 circles) hold a small shrub group until Rare Specimens
  replaces it with the showpiece.
- About 10 trees at the dome end and wing tips, a shrub border, benches by the paths, fewer and
  warmer lights. Interests: Relaxation, Exercise, Playing, Social.
- No vanilla method is replaced; everything is on the Arboretum's own class.

Decisions the build made that the owner has been told but not yet answered: capacity 14 per
shift (42 a sol; 60 with Rare Specimens); Rare Specimens alone costs 2 Seeds a shift; beds pause
growing as well as replanting while untended; the showpiece is `CropApples`; upgrade costs (bots
10 Electronics, Blooms 5 and Specimens 10 Polymers), Blooms and Specimens need no tech.

Open with the owner: the Melancholic line in the interest popout (a shipped module's display, so
it wants its own ruling); whether Service Bots should give more than staff; OI-47 (category) and
OI-48 (footprint, one per dome) on this mod's checklist.

## What each import round needs (learned the hard way; details in the report)

- After the builder runs, the owner re-imports **both** entities (ArtSpec, Importer, Import on
  each, save, close). The builder rewrites both FBX files every time.
- The editor save rewrites `staging/metadata.lua` and `items.lua`. Restore the hand files from
  git and add back the `entities` list and `"Code/_EntityData.generated.lua"`; then
  `activate_model.py --activate`, `generate.py --check`, `deskcheck.py`, `tools/workbench.py`.
  Until then the workbench gate is red and a stray DEV ONLY options page appears.
- `readback.py <fbx dump>` compares the compiled entities with the export proof (the dump is
  `blender --background --factory-startup --python SMR-Assets/arboretum/blender/dump_fbx.py --
  <export folder> <out.json>`).
- Menu loads: `staging/tools/arboretum/prepare_boot.py <leg> --original <order>` and the fix
  pack's `arm_leg.ps1`; `scratch/arboretum_boot/run_leg.ps1` is the runner. Mars.exe restarts
  itself through Steam, so wait on the process name. `present_on` removes the fix pack for the
  next start and `absent_on` puts the captured order back: never run one without the other.
- A changed class or footprint makes placed Arboretums stale: the owner demolishes first.

## Known stale

- `readback.py` and `activate_model.py` know the pavilion and glass only; the three bloom
  entities need a readback after their import.
- `SMR-Assets` `verify_arboretum.py`'s SIE line check fails against editor-saved import files
  (one field per line); it passes on the builder's output. Format only.
- `staging/tools/arboretum/slots.lua.txt` slots 4 to 7 measure Seeds per visit and expect the
  building to stop when empty; both are no longer the design.
- `staging/items.lua` option help still describes the per-visit building.
- The report's earlier sections say things later sections replace; its top status lines point
  the way. ck223 on the fix pack's checklist is the old Seeds-per-visit sitting.

## Stops

- A change that would replace a vanilla method or add a persisted callback: report the options.
- Anything outside `staging/`, the Assets `arboretum/` folder and the Arboretum's records.
- The production mod, promotion out of `staging/`, the store copy, the fix pack: not this work.

## Claim limits

Supported: "in the workbench at `<sha>` plus working tree; menu-load checked with the fix pack
present and absent; owner look: <their words>". Not supported: done, ready to ship, audited, any
Seeds-per-sol figure, fit in every dome, or anything about workers, upgrades, bed growth or save
and load until the owner has seen it.

## Next batch for the owner (handed over 2026-10-05, not yet run)

Import, in the workbench Mod Editor, then save once and close: the pavilion (ArtSpec, Importer,
Import; scene path unchanged; the glass needs no re-import), then `SMROptInArboretumBloomSpike`,
`SMROptInArboretumBloomRound`, `SMROptInArboretumBloomLow` with the glass's steps (ArtSpec: exact
name, Class Parents empty, mesh `mesh`, state `idle`; Importer: scene
`B:/Dev/SMR/SMR-Assets/arboretum/blooms/export/<name>.fbx`, Material `<name>`). Tell the agent
before launching the game: the hand restore, activation, readback and menu loads come first.

Then, old Arboretum demolished and a new one placed:

1. Watch colonists arriving from the back and leaving towards the far side: do they use the door?
2. Without the upgrade: Herb at full size.
3. With Seasonal Blooms: each bed small at replant, grown past the bed edge by its mid-morning,
   then held; a new colour or shape each sol, beds a third of a sol apart.
4. Still owed from the first batch: the panel (workers, performance, Seeds, upgrades), whether
   colonists take the two jobs, the showpieces replacing the shrubs under Rare Specimens.

Send back: screenshots, what the panel reads, and anything that looks wrong.

## References

Skills: `smr-orientation`, `doc-editing`, `subagents`, `smr-session-close`. House rules
`CLAUDE.md`; code `docs/agent/FIX_POLICY.md`, header first (row 36 holds the new saved names).
Game source: `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/`, cited with the build.
Importer facts: `SMR-Assets/_shared/IMPORTER_FACTS.md`.
