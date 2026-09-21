# Train hub model: longer stubs and the transition platforms

**LIVE, fire when ready.** Asset work in `B:\Dev\SMR\SMR-Assets\trainhub\blender`. Authoring shas:
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

## Pass 2 — the loading sidings (owner, 2026-09-20; pass 1's stubs and arms are imported and accepted)

**Why.** A train that loads inside the hub occupies the running line, so when its exit is blocked it
must either sit there blocking its own line and the crossing, or reverse out into the lane the next
arrival needs. A siding removes the choice: the train loads and waits off the running line, and a
through train can pass while it does.

⛔ **Bake the owner's platform offset into the generator FIRST, before any regenerate** (verified
2026-09-20 by the orchestrator). The pass-1 arms overlapped the track beam: a deck centred on the lane
at 2.89 m and 3.4 m wide has its inner edge at 1.19 m, inside the beam's 1.75 m edge. The owner moved
all twelve 0.573 m outward across their own line, so the inner edge is flush with the beam, and that
is what was exported and imported. **It lives only in `TrainHub_work.blend` as object locations on
`Platform_1..12`; `hub_skeleton.py:344` still reads `off = PLATFORM_LANE_OFFSET`.** Regenerating as
it stands puts every arm back into the beam. Replace that line with
`off = BEAM_W / 2.0 + PLATFORM_W / 2.0` (3.45 m, 13 mm inside the owner's 3.463) and keep
`PLATFORM_LANE_OFFSET = 2.89` as the documented lane position; after the rebuild the locations return
to zero. Two consequences are deliberate — do not "fix" them: the deck is no longer centred under the
train (the beam carries its inner side), and past the connector a strip of deck overhangs cells
outside the footprint, which does not block a track because placement reads `hex_shape`.

Also known, not yours to chase: `verify_build3_source.py` fails naming `Pillar_8..13`. It fails on
the committed blend too; it is a stale build-2 guard from before the owner's 2026-09-19 inner-ring
cut. `TrainHub_work_Owner_edit.blend` (untracked) is an earlier owner save with no platform moves —
build from `TrainHub_work.blend` and leave the owner's file where it is.

**Pass 1 is uncommitted and goes in with your step 5:** in SMR-Assets `hub_skeleton.py`,
`verify_look_pass.py`, `export/look_pass_source_proof.json`, `TrainHub_work.blend` and the new
`render_transition_previews.py`; in SMR-OptInPack the three files the owner's import rewrote,
`tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson`,
`Meshes/SMROptInTrainHub6_mesh.sub_0.hgrm` and `metadata.lua`. The orchestrator ran the untextured
export (`export_prep_untextured.py`) and the owner imported it: `importer_result.log` Result OK, 25
spots, 0 colliders, 724 surfaces.

**Build six loading sidings, one per internal spur.**
- **Placement:** beside each spur, all with the **same rotational handedness** (all clockwise of
  their own spur), so the two sidings of a through line land on opposite sides of it and the Lua is
  one sign flipped by connector index, not a per-line table.
- **Attached to the track beam, cantilevered. No pillar under it** (owner): the interior is busy
  already and it should read as part of the track.
- **Deck top at 8 m**, level with the track, and long enough to hold a whole train (about two hexes
  by the owner's hex measurement; R-TRAIN is DISPUTED, so size it by eye, never from 41.5 m).
- **Keep it inside about 23 m radius.** The cargo beds are centred 26.75 m out on the wedge midline,
  14.9 m by 6.6 m (`BAY_D`, `BAY_LEN`, `BAY_DEPTH`), so they span roughly 23.5 to 30 m radially and
  their near corner comes within about 6.5 m of the line. The beds are on the ground because the cube
  stacks are tall, and a deck at 8 m out there would have stacks growing through it.
- **Look: a clean glass deck with a metal border** (owner). No panel seams — the owner compared
  vanilla's big dome, which is ribbed and panelled, with the PassageHub's clean shell, and wants the
  clean read here. Ribbed stays right for our own dome, which is a separate question and not this pass.
- **The panel goes in the body mesh, opaque** (owner, 2026-09-20, after the first import): the importer
  keeps one mesh node and silently discards any other (`_shared/IMPORTER_FACTS.md`), so the separate
  glass node did not survive. Real glass is a texture-pass question, gated.

⛔ **Rough is right, and this is the owner's instruction** (2026-09-20): *"not extreme effort in
getting it exact since we know now I can human-eye any gaps and give you movement parameters. The
focus is getting the models in, I do the fine adjustments."* Get the sidings in, exported and
imported. Do not iterate on millimetres, do not re-render to compare options, and do not hold the
import for a gap the owner can see and correct in one pass.

Pass 2 then follows End state steps 3 to 5 below — export, the owner's import, one in-game look,
record and commit. **It skips step 2's render gate**: the owner inspects it in the game, not in a
render. The junction is already in place.

## Pass 3 — the sidings are too small for a train, seen in game (owner, 2026-09-20)

Pass 2 is imported and the owner looked at a train parked on a siding. Three faults, all theirs,
all dimensions: **the car overhangs the deck's outer edge**; **the deck ends before the car does**;
and **the cargo pallets are where the car and the deck want to be** — which is Pass 2's own
"keep it inside about 23 m radius" note coming true, the bed stacks growing through the deck.

⛔ **The inner end does not move. The owner tried it and ruled it out** (2026-09-20): *"extending
out platform closer to the hub won't do it, its gonna just eat into either the track or the tunnel
entrance."* Take the length outward instead. This also protects the inner end's clearance from the
neighbouring spur, which an inward extension would have eaten.

The owner's first cut, to be looked at and not defended — **the owner adjusts by eye afterwards**:
1. **`SIDING_W` 4.0 → about 5.5 m**, outward, away from the spur. This fixes the overhang and buys
   clearance from a train passing on the running line, because it parks the train further out. The
   owner flagged that pass as *"really tight"*.
2. **`SIDING_TO` 23.0 → about 25.5 m**, the owner's *"not by a lot"*.
3. **The cargo beds stay where they are unless the deck actually reaches them.** ⛔ The owner
   corrected an orchestrator proposal to move them (2026-09-20): *"this is what needs to extend
   outward not the hub."* The deck grows; the hub does not. The beds are `BAY_D` = 26.75 m on the
   wedge midline, `BAY_LEN` 14.9 m by `BAY_DEPTH` 6.6 m, spanning about 23.5 to 30 m radially with
   their near corner about 6.5 m off the line, so a 25.5 m by 5.5 m deck does run into that zone and
   the owner saw stacks and deck meeting. Report what overlaps after the deck is sized; the owner
   raised *"shift the resource pallets slightly"* as a possibility, not an instruction, so a bed move
   is theirs to rule on with the overlap in front of them. If one is needed, it is small and lateral,
   never a redesign of the bays.

**No Lua change, and do not open `20_TrainHub.lua`** — it belongs to `TRAIN_HUB_MOVE_high.md`, which
is live. The bed positions are entity `Box1` spots that the import carries, and the hub reads the
cube grid off the spot (`GetCubePosRelative`, 12 cubes along the spot's +X and 5 rows along its +Y),
so moving the spot moves the stacks with it.

Then the same tail as Pass 2: export, the owner's import, one in-game look, record in spec §9,
commit with pathspecs. Skip the render gate; the owner judges it in the game.

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
   arms attaches to the stub. `20_TrainHub.lua` belongs to `TRAIN_HUB_MOVE_high.md`: touch it only if placement or
   attachment fails, the smallest change that works, and say so. Trains will not use the sidings yet; that is
   `TRAIN_HUB_MOVE_high.md`'s job, not a fault.
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
