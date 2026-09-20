# The geometry problem: make it stop failing in front of the owner

**LIVE, fire when ready. Fire it before build 3b** (`TRAIN_HUB_TRAINS_high.md`): 3b is pure train
choreography, which is the sharpest instance of this problem, and 3b is where a wrong guess costs
the owner an evening. Nothing here changes mod behaviour, so it runs safely beside a held build.

## Authority

**Owner, 2026-09-19.** Every failure in the train hub so far has been one species: a coordinate or
transform mismatch between Blender space, the Mod Editor's importer, the game's hex grid and
vanilla's own spot conventions. The footprint read as 85 hexes instead of 61; four of six lines
could not attach; cargo cubes landed beside their beds; trains dropped through the deck to the
floor; trains slide across the open interior and jump to the far side on departure; the stub's
width went unmeasured until build 3; a height "fault" was ruled by eye that measurement says does
not exist. **None were logic bugs. All were geometry.** Each was caught the same expensive way: the
owner's eyes, in game, after a manual Mod Editor re-import.

The owner's ruling: **this is the part that must not fail, and it is worth real effort to fix
properly.** `FIX_POLICY` §0 sets this mod's risk standard. Neither ban is engaged: this ships no
game code and adds no persisted state.

## The outcome the owner is buying

A geometry mistake is found **from files on disk, in seconds, before a re-import and before a
sitting** — with a verdict specific enough to act on and honest about which of its rules are
shaky. Today that loop runs through the owner's evening, and that is the thing being bought out.

Everything below this line except **the bar** is the orchestrator's sketch. It is offered so you do
not start cold, not as the route.

## The bar — this part is not yours to move

Two standards, because both were learned the hard way. They constrain honesty, not method: any
approach you choose must meet them.

**1. It must retrodict the failures already paid for.** A harness that only agrees with today's
working files proves nothing. The known corpus, with evidence in
`docs/agent/reports/TRAIN_HUB_SITTING_20260919.md` and `TRAIN_HUB_BUILD_20260918.md`:

- the pre-inset entity read as **85** outline hexes, four lines at radius 5 and two at 4;
- the current entity reads **66**, radii 4 × 6 (the in-game slot dump agrees);
- the pre-fix Box spots put **1 to 5** of 60 cubes on a bed; the current ones put **60**;
- the pre-`6123ae7` synthetic spots put trains on the **ground**, a deck height below the beam;
- the current spots reproduce the owner's observations: the interior slide, the far-side jump on a
  same-track departure, the sideways shift into the portal legs.

⛔ **Do not tune a model until the numbers fit.** A case that will not reproduce **is the finding**:
report the gap and what would close it. A model fitted to its own answers is the single failure this
work exists to prevent, and it would be worse than no model at all.

**2. A rule is triangulated, not derived once.** Every failure above came from a rule known from a
single source. A rule is trusted only with **two independent derivations that agree** — the game
source, the entity file, an in-game dump, a vanilla asset read the same way. Where they disagree,
or only one exists, the rule is `UNCONFIRMED` and so is every verdict resting on it.

**Correlated error is what this standard exists to catch**, so two derivations are independent
only to the degree the things producing them differ — different evidence, and workers differing
in kind rather than merely in instance. Two passes sharing a blind spot agree for the wrong
reason, which is how a single-source rule came to be trusted in the first place.
**Prefer to separate producing a derivation from clearing it.** The worker that built a rule is
its worst judge, and the corpus above is deliberately a set of known answers so that clearing
one costs a check rather than a re-derivation — a judge does not need to be able to do the work
it is judging. Delegated work returns as a **claim**, never a result: confirm what a verdict
rests on before it enters, and say in the report which derivations were independent of which,
and how. Whether to fan out, how wide and along which cuts is yours.

## Where you may overrule us

Explicitly open. If you take any of these, say so and say why — a changed plan with its reasoning
is a better outcome than a faithful one that misses the point.

- **The instrument.** The sketch below is a file-reading predictor. If the real answer is a
  headless game harness, a TestKit probe, a Blender-side check, making the import deterministic,
  removing the hand step, or something we have not thought of — take it.
- **The framing.** If "predict the geometry" is the wrong cut and the true root cause is elsewhere
  (the pipeline's hand steps, the two coordinate conventions existing at all, the hub's design
  fighting the engine), say that. The owner would rather hear it now than after 3b.
- **The scope.** If a narrow instrument that kills 80% of the risk beats a general one, build the
  narrow one and say what it leaves uncovered.
- **The facts below**, including anything in `IMPORTER_FACTS.md`. They are measurements, not
  gospel; each carries its falsifier for exactly this reason. Overturning one is a result.
- **Any part of the sketch**, including whether the invariants are the right cuts.

## Measured rules, so you do not re-derive them

Provenance for each: `C:\Dev\SMR-Assets\_shared\IMPORTER_FACTS.md`.

- **Importer axis mapping**: Blender `(x, y)` m → game `(-y, -x)` × 100, after the pipeline's 30°
  turn (`export_prep.py` `TURN_DEG`). MEASURED from the first import. Falsifier: a spot in
  `Entities/SMROptInTrainHub6.entjson` the mapping misplaces.
- **Spot angle**: a Blender spot's `rot_z` becomes the game angle `330 - rot_z`. MEASURED
  2026-09-19; the seed script reproduces all six Box spots from it.
- **Cargo grid**: columns along the spot's game angle, rows 90° on; a bed is 12 × 5 = 60 columns
  (`Station.lua:99-100`); a layer is 1.01 m; `max_z` derived
  (`MultiResourceDepot.lua:RecalculateDerivedMaxZ`). MEASURED from a console dump of five cubes.
- **`Train:GotoSpot` is a straight timed slide**, not pathing: `SetPos(spot_pos, move_time)`, pitch
  only, no yaw (`Train.lua:507-519`). This is why the choreography is predictable at all, and why
  it shows in a building 80 m across.
- **Vanilla's choreography**: arrive → `Ramparrive<k>` → `Stop<k>`; depart on `j` →
  `Rampdepart<j>` → the element's `Enter1/2`; depart on the arrival track → `SetPos(Spawn<k>)` +
  `SetAngle`, then `Rampdepart<k>` (`Station.lua:1085-1118`, `:1183-1207`).
- **Our spots are computed, not modelled**: `20_TrainHub.lua` `synthetic_spot_pos`,
  `kind_sevenths`, `train_deck_height`. Read the Lua's own numbers; never copy them.
- **Track element**: `bbox_xy=1000x204`, `bbox_z=-1726..1069`; vanilla's train level and ours are
  equal, `stub=10800:running=10800` on all six lines (build 3's `track_height_rows`).

- **The hub's geometry exists as named parameters, not only as triangles**: `hub_skeleton.py`
  in `C:\Dev\SMR-Assets\trainhub\blender\` holds `RING_PROFILE`, `RING_PILLAR_R`, `PILLAR_AT`,
  `PILLAR_R`, `BEAM_W`, `BEAM_H`, `DECK_Z`, `BAY_D/LEN/DEPTH`, `FOOTPRINT_R`, `HEX`. The ring is a
  turned profile, the pillars are discs at computed angles, the beams are boxes — so anything you
  want to test against them can be analytic rather than a mesh intersection, if that serves you.
  Falsifier: a parameter that disagrees with the exported mesh (`verify_look_pass.py` compares
  the built scene against a preserved baseline and would have caught it).

**The seed.** Three scripts that already did this and were right:
`C:\Dev\SMR-Assets\_shared\geometry\` — footprint and cargo predicted from the entity file before
an import, and the cargo rule fitted from five observed cubes. Its `README.md` says what each one
proved. Build on them, rewrite them, or discard them.

## The orchestrator's sketch — take it or replace it

A harness reading the entity file and the hub's Lua, giving an independent verdict per invariant:
footprint (hexes, inset, line radii); spots (world position and angle as the game reads them);
cargo (where a bed's 60 cubes land); train choreography (path per line, per departure kind);
clearance (those paths against ring, legs, pillars, beams, stacks, dome); two-train overlap in
space and time; lane alignment against the incoming element's own spots. Runnable from the command
line, non-zero exit on failure, machine-readable output beside the human one, rules' provenance in
the output, and a selftest that breaks each invariant deliberately — an oracle nobody has tried to
fool is not an oracle.

**Placement: your call, in the commit message.** `C:\Dev\SMR-Assets\_shared\geometry\` fits the
cross-mod purpose and holds the seed; this repo's `tools/` brings doccheck's compile and catalog
discipline. Whatever you build must not need this repo's tree to run.

## Done means

The owner can change the hub's geometry or its spot Lua and learn whether it is right **without
launching the game** — and the instrument has already shown it catches the five failures that were
previously caught by eye. Plus a report answering 3b's geometry questions ahead of it: the lane
offset; where a train actually goes today, per line and per departure kind; which of those paths
cross the ring, the legs or the stacks; whether two trains can meet. Numbers, each with the rule it
rests on and whether that rule is confirmed. `IMPORTER_FACTS.md` carries anything newly measured.

If you conclude the outcome is better served another way, **that report is the deliverable** — with
the evidence, and what you would build instead.

## Scope

In: whatever meets the outcome, plus the report. Out: changing the hub's geometry, its spot Lua, or
the Blender pipeline — a fault you find goes to 3b or the look pass, so this stays a measuring
instrument and not a second cook. Say so if that boundary is what is wrong.

## Stops

- A rule has one derivation and no second without the game: mark it `UNCONFIRMED`, say what
  in-game measurement would confirm it, carry on.
- Something needs state no file holds: say exactly what to measure, in one paste-safe console line
  the owner can run.
- **The approach is wrong.** Report the reasoning and what to do instead. This is a result, not a
  failure, and the owner would rather have it early.

## Do not claim

Not "the hub's geometry is correct". Claim what was predicted, which rules it rests on, which are
`UNCONFIRMED`, and which of the five known failures were reproduced. A prediction is not an
observation, and nothing here runs the game.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` when the work and its
report land. What you build is permanent; its home decides which repo's conventions keep it.
