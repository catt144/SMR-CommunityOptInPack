# Train hub: a build-menu icon of its own

**LIVE, one-off.** The owner fires it; the orchestrator parks or deletes it once done. Authoring
state: OptInPack = the commit whose message starts "Brief 06: the build-menu icon"; assets
`a5535fb`. Empty `git diff --stat <that sha>..HEAD -- tools/devmods/train_hub/Data/
tools/devmods/train_hub/UI/` and `git diff --stat a5535fb..HEAD -- trainhub/` (SMR-Assets) mean
this brief's facts hold. Start with `git log`, `git pull` in both repos, then spec §9 from "Body
paint, run 1" to its end.

## Authority

**Owner, 2026-09-23, in the build menu with the painted hub behind it: *"Our icon in the build
menu just looks like another station. Can we have a custom icon?"*** — asked and answered yes the
same sitting: the agent makes the image, the owner picks. The hub's look is KEPT as of restore
point 6 `hub-bodypaint-1-20260923` and does not move for this; the icon is a picture of it.

## End state

1. **The wiring, verified on the source before any art.** The template
   `tools/devmods/train_hub/Data/BuildingTemplate/SMROptInTrainHub6.lua` line `display_icon`
   carries vanilla's `UI/IconsRemaster/Buildings/large_train_station.png`. Read on
   `C:\Dev\SMR-SrcArchive\1.1.0.403908\Src` how a mod-local image path resolves for that field
   (the editor's own saved presets and `CurrentModPath` are the two forms seen elsewhere) and
   cite the line with the build. Then prove it with a throwaway solid-colour PNG in the mod
   before the real art exists: if the menu shows it, the path form is settled.
2. **The art: two or three variants.** A 232 × 100 RGBA image in vanilla's icon style (both
   vanilla train icons are under `SMR-Assets\trainhub\reference\`, `IconsRemaster__Buildings__*`,
   232 × 100, for style, angle and margins). Subject: the hub as kept — navy ring, white bands, the
   dome and six arms — rendered from the Blender preview scene (`render_concept.py` is the
   camera and lighting precedent; `export/structure_seams/preview.blend` carries the maps) on a
   transparent background, scaled down last. Your call on angle and framing; vary exactly that
   between variants and say what each is.
3. **The owner's pick, in the build menu.** Each variant installed in turn (or all three under
   different template ids if that is cheaper), a screenshot beside the vanilla station icon at
   the same zoom, the owner's word. Iterate as they direct.
4. **Ship the pick:** the PNG in the dev mod, the source (blend camera, script, the full-size
   render) in `SMR-Assets\trainhub\icon\`, the template line changed, the Mod Editor save
   checkpointed with the drones code-list line checked (`grep -c 30_TrainHubDrones
   tools/devmods/train_hub/metadata.lua` must print 1). Record in spec §9 with `doc-editing`;
   commit both repos with pathspecs.

Done means: the owner sees an icon that reads as the hub and says keep. Budget runs out: ship one
variant the owner has seen rather than three they have not.

## Scope

In: the one PNG, its source, the one template field, the record. Out: the hub's look, the Lua,
the encyclopedia image (a separate field; note in the report if the owner wants it too), every
other mod item.

## Stops

1. The mod-local path form cannot be found on the source and the throwaway PNG does not show:
   report the forms tried and stop; do not ship a vanilla path.
2. The editor's save changes anything beyond `metadata.lua` and the template: stop and report the
   diff before committing.

## Do not claim

Do not claim the icon reads well from a Blender render or a scaled preview. Claim what the owner
said looking at it in the build menu.

## Deliver

Todo list first, one item per commit-and-verify unit. About five steps at a time in a live
sitting. Report with the commits, the cited source line for the path form, and the owner's words.
