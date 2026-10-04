# Arboretum — a custom model from borrowed game assets, with a visible Seeds supply

One-off. Authored 2026-10-04 at `81c75a5` (SMR-Assets at `2b9f196`). Delete this file and its row
in `docs/agent/prompts/README.md` in the commit that closes the work.

## The owner's decision

Owner, 2026-10-04, after the D19 audit passed: the Arboretum should not stay on the Large Garden
art. *"I would like to do a custom model, something similar to this, we can alter it with assets we
can borrow from the game. And it will need space for a seeds supply for it to consume."* The look
target is `B:\Dev\SMR\SMR-Assets\arboretum\concept\arboretum_concept_dusk.png`: a glass pavilion
with a raised central glass dome on a ring, two long rounded glass wings on spoke ribs, a framed
entrance with leaf panels, and planted interior paths with trees, flowering shrubs, rocks and
benches.

On the Seeds supply, the owner showed two vanilla services
(`SMR-Assets\arboretum\owner_feedback\stock_ref_*.jpg`): the Art Store shows stored Polymers as
loose cubes on its lawn, and the Grocer shows stacked crates on a pad beside it. *"Looks like the
game does a mix of both. So space depending we can do either."* Choose by space.

Method (owner, 2026-09-20, standing): **prototype first.** Rough, in the game fast; the owner
adjusts by eye and gives you numbers. No millimetre iteration, no rendering option sets for a
pick, no gate between the owner and something they can look at. Function before texture: flat
materials on this pass; a paint pass waits for the owner's word.

Record this ruling in D19 for this mod (CLAUDE.md's header wants behaviour changes ruled there).

## End state

The owner places an Arboretum in a dome and sees the new model: glass pavilion read from the
normal camera, drones delivering Seeds to a visible stock that shows the building's stored Seeds,
and colonists visiting. The owner judges it by eye and the report records what they said.

Completion evidence: the owner's screenshots in `SMR-Assets\arboretum\owner_feedback\`; a menu-load
check of the workbench with the new entity, fix pack present and absent, in the method of
`docs/agent/reports/ARBORETUM_BUILD_20261003.md`; a report `docs/agent/reports/ARBORETUM_MODEL_<date>.md`.

## Live work

1. Investigate (below) and record what the model must carry. Commit findings in the report.
2. Rough model: a scripted Blender builder and verifier under `SMR-Assets\arboretum\blender\`,
   in the train hub's and Elevator Depot's manner. Flat materials.
3. Import into the workbench and wire D19's template to the new entity; menu-load check.
4. Owner look sitting: preloaded slots, the owner places, watches stock and visitors, adjusts.

One item in progress; keep the list in your todo tool or the report.

## What you need to find out

Your approach and read path. Read game source on build **1.1.1.406343** from
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/` and cite it with that build.

- **Visible stock.** How the Grocer (`ShopsFood`) and Art Store (`ShopsJewelry`) display stored
  consumption resources: which spots, surfaces or template fields drive the crate pad and the
  loose cubes, and whether D19's native consumption gets that display for free from an entity
  that carries the same thing. D19 claims no vanilla method is replaced; keep that true.
- **What the class needs from its entity.** Spots and surfaces D19's class uses for building,
  outline, visitors, entrance, drone delivery and the stock (the build report's attempt-2 finding:
  a garden's Build surface differs from other buildings').
- **Borrowing game assets.** Two routes, your call or a mix: kitbash vanilla meshes in Blender
  (game art stays local and uncommitted, per the SMR-Assets README), or attach vanilla entities
  (trees, shrubs, benches, lamps, glass) to the custom entity at runtime. Find what the engine
  supports for a mod entity.
- **Where the entity lives.** D19's code is in the `staging/` workbench mod. `tools/promote_module.py`
  refuses custom-model promotion (shared ArtSpec/entities merge). Import into the workbench;
  promotion is not this brief's work.
- **Save contract.** If the new entity's name or any new field is written to a save, add it to
  `docs/agent/FIX_POLICY.md` §"The persisted-name inventory" before it ships.

Start from: `SMR-Assets\_shared\IMPORTER_FACTS.md` (pull-only; read before building, exporting or
importing), the train hub and Elevator Depot builders in SMR-Assets, and
`docs/agent/reports/ELEVATOR_DEPOT_LOOK_20260930.md` and `STAGING_WORKBENCH_20261003.md` here.

## Footprint

Not ruled: OI-48 (footprint and one per dome) is still open on the owner's checklist. Start on the
Large Garden's footprint so the existing placement evidence carries and it fits where a Large
Garden fits; a bigger footprint like the concept's is the owner's call after seeing it. Expose
size or proportion as something the owner can move, not a number you derive.

## Owner-attended steps

Mod Editor imports and the look sitting need the owner. Hand them over about five steps at a
time. In the game, preload the work into SMRTK slots (`tools/SMRTK.md`): the owner clicks, does not
type, and reads the building's and the dome's infopanels, not individual colonists. Advance time
with Run until at top speed. The editor stores absolute import paths and reasserts them over a
drag (IMPORTER_FACTS); set the path on disk with the editor closed.

## Scope

In: the Arboretum's model, its spots and stock display, D19's template entity, the workbench
import, the owner's look sitting.
Out: balance numbers, the service category (OI-47), promotion out of `staging/`, the paint pass,
the build-menu icon, the store copy, the fix pack. Report findings outside scope; do not edit them.

## Stops

- Visible stock needs a replaced vanilla method or a new persisted callback: report the options.
- The engine will not run D19's service class on a mod-imported entity in a dome.
- The workbench cannot carry an imported entity without a production ArtSpec change.

## Claim limits

Not supported: "Arboretum done", "ready to ship", any Seeds-per-sol figure (still ck223's), or a
fit claim for every dome. Supported: "custom model in the workbench at `<sha>`; menu-load checked;
owner look: <their words>".

## Unattended runs

Execution and audit are on different owner-selected models, and nothing enters the record unaudited.

## References

Skills: `smr-orientation`, `smr-bug-library`, `doc-editing`, `smr-session-close`. House rules
`CLAUDE.md`; process `docs/agent/WORKFLOW.md`; code `docs/agent/FIX_POLICY.md`, header first.
Assets commit in `B:\Dev\SMR\SMR-Assets` with a pathspec. Records: D19, `docs/agent/bugs/INDEX.md`,
`docs/agent/facts/INDEX.md`.
