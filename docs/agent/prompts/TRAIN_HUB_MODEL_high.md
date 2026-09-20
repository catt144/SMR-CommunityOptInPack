# Train hub model: longer stubs and the transition platforms

**LIVE, fire when ready.** Asset work in `C:\Dev\SMR-Assets\trainhub\blender`. Authoring shas:
SMR-OptInPack `3c79ddd`, SMR-Assets `66240ae` (its `README.md` carried a peer's uncommitted edit;
leave it). An empty `git diff --stat <sha>..HEAD` on `trainhub/` and `tools/devmods/train_hub/`
means these facts hold.

## Authority

**Owner, 2026-09-20, on method — this governs how you work.** *"I don't want to go through a bunch
of lets make it perfect prompts, I want to get the model work done. Inspect it, and then do a quick
prototype of the actions and then we can dial it in to perfection."* So: **a quick, inspectable
model, not a finished one.** Rough is right. No battery, no oracle re-run, no redesign proposals, no
texture polish. The owner inspects, then a separate short brief prototypes the train movement, then
everything is tuned by eye. If a choice is cheap to change later, make it and move on.

**Owner, same day — use the owner's hands where that is quicker.** The owner does not know Blender
but will follow instructions, and asked that this be weighed against an agent scripting, rendering,
inspecting and scripting again. Your call, per step. The likely split: what must be exact stays
scripted (the footprint hexes, the connector and spot positions, anything on the hex lattice); what
is judged by eye (an arm's width and inner edge, where a deck ends, how it meets the portal) is
faster if the owner drags it in the viewport until it looks right. When you hand the owner a step,
give click-by-click instructions for Blender 5.2, a few at a time, naming the object to select and
the key to press, and say what done looks like. **Then read the result back out of the `.blend`
(`probe_geometry.py` is the pattern) and write it into the generator's constants**: the generator
rebuilds the file, so a hand edit that lives only in the `.blend` is lost on the next run.

**Owner, same day — the design** (spec §9, "Deck under the lanes" to the end of that block; read it,
it is short). Trains ride beside the vanilla rail and on top of the centre of our track.
1. **Each stub goes out one more hex**, two in all: the owner measured the stub at exactly one hex
   and a train at about two. The connector moves out with it.
2. **Transition platforms:** at each line's end the platform wraps round the stub's two side hexes
   and runs **two hexes further out past the stub's end**, one arm each side, **leaving a one-hex
   path between the arms** for the vanilla track to reach the stub. Start there; the owner may want
   one hex more, so make the arm length one constant.
3. **Height:** the stub is already very close to the train's underside. No lift. A train rides
   289 units (2.89 m) off the line, to the right of its travel, so each arm's deck sits under that.
4. The look the owner has in mind is a maglev feel. Not this brief: leave the materials as they are.

## End state

1. **The generator** (`hub_skeleton.py`; `HEX`, `FOOTPRINT_R`, `BEAM_W`, `DECK_Z`, `PLATFORMS` are
   the constants nearest this) builds the longer stubs and the twelve arms, with the footprint
   (`hex_shape`) covering the stub hexes and the arm hexes and **not** the centre row past the
   connector. The hub's Lua takes each connector from the outline: the last footprint hex along the
   centre row (`line_radii`, `20_TrainHub.lua:115`; `Tracks.lua:19-24`, 1.1.0.403908), so that row
   must end at the new stub and every arm hex must stay off it. Your call on the exact hex set, the
   arm's width and its inner edge; a vanilla track pillar stands under the rail in the path between
   the arms and the arm must not swallow it.
2. **Renders for the owner to inspect**, before anything is imported: a top view with the hex grid
   and the footprint drawn on it, one line's end from above and from ground level, and the whole hub.
   Put a box of about 20 m by 4 m where a train rides, beside the path and on the stub, so the fit is
   visible. Stop here and hand the renders to the owner.
3. **After the owner's go:** export, and give the owner the Mod Editor re-import steps from
   `blender\README.md`. The old assets path is already a junction to `C:\Dev\SMR-Assets\trainhub`
   (the orchestrator did it 2026-09-20, owner's order); work at the real path, never the old name.
4. **One in-game look, not a test:** the hub places, and a vanilla track laid down a path between two
   arms attaches to the stub. `20_TrainHub.lua` belongs to build 3b: touch it only if placement or
   attachment fails, the smallest change that works, and say so. Trains will still ride the old
   lanes; that is the next brief's job, not a fault.
5. **Record** what was built and what the owner said in spec §9, and commit both repos with
   pathspecs. `doc-editing` before the doc edit.

The owner's fixture saves (`train_hub_base`, `train_hub_base_agent`, spec §10) have tracks laid to
today's connectors; the longer stub needs each line's last element removed. That is the owner's edit,
saved under a new name. Never overwrite a save.

## Scope

In: the generator, renders, export, the junction, the footprint, the record.
Out: train movement, park distance, textures and the maglev look, the hub's economy, the oracle,
the four-connector hub, builds 4 and 5.

## Stops

- **The footprint cannot leave the path open** (the importer or the game closes the one-hex path, or
  a connector lands on an arm hex): report the hex set you tried and what the game did.
- **The arms collide with the ring, a pillar or a storage bed** in a way a constant cannot fix:
  report with a render; do not redesign the body.

## Do not claim

Not that trains use the platforms: nothing moves differently until the movement prototype. Claim what
the renders show and, after import, that the hub placed and a track attached, on the save you used.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` when step 5 is committed.
