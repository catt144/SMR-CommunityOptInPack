# Geometry oracle, paths run: make the path model answer build 3b's questions

**LIVE, fire when ready.** Runs A and B measured the spots and the rules; the oracle's *path* model
still routes trains the way neither the game nor the corrected table does, so the three verdicts that
depend on paths print numbers nobody may use. This run closes that gap. Everything under "State" is
committed and is a claim cleared by one check each — do not re-derive it.

Authoring shas: SMR-OptInPack `54fccbd`, SMR-Assets `015bc64`. `git diff --stat <sha>..HEAD --
_shared/geometry/` empty in SMR-Assets means this brief's facts hold.

## Authority

**Owner, 2026-09-20: the oracle is extended first, and build 3b is re-scoped afterwards on its
numbers.** The orchestrator (`perma/TRAIN_ORCHESTRATOR.md`) rewrites 3b's brief from your report;
you do not write it and you do not build 3b.

Standing, from run A (owner, 2026-09-19): a geometry mistake is found from files on disk before a
re-import; a rule is trusted only with two independent derivations that agree; never tune a model
until the numbers fit; never clear a rule with the worker that produced it. One model family per
independent derivation — Codex CLI is available as GPT (`codex exec --skip-git-repo-check --sandbox
workspace-write -C <dir> - < prompt.txt`). An agent may launch the game itself and the owner is not
a required participant (`tools/SMRTK.md`, `978768b`); this run is expected to be desk work, and the
in-game smoke belongs to 3b.

**Note the shape of this job:** the rules below are already measured. You are implementing them in
the path model, not deriving them. Any rule you find you still need is new, and the two-derivation
standard applies to it in full.

## State (committed; each is a claim, one check clears it)

- **Instrument:** `C:\Dev\SMR-Assets\_shared\geometry\hub_oracle.py`, SMR-Assets `015bc64`; `corpus/`
  with `EXPECTED.json`; the README there says how to run it. `--corpus` **24/24** and `--selftest`
  **6/6** on the committed file, re-run by run B's judge. Keep both green; they are your regression net.
- **Report:** `docs/agent/reports/GEOMETRY_ORACLE_20260919.md` (this repo). §0 is the root-cause
  finding, §3 build 3b's geometry questions, §4 the routed findings, §10 run B's addendum. Read §10
  first: it states this run's starting point and why it stopped where it did.
- **The table is wrong** (report §0, §4 item 1). `SMROptInTrainHub6Base.hub_connector_directions =
  {0,3,1,4,2,5}` in `20_TrainHub.lua`; the imported body's connectors 1..4 lie on hex directions
  `4,1,3,0` (5 and 6 are right). MEASURED in game 2026-09-19: all 24 synthetic spots and six
  connectors matched the file-side prediction with zero delta
  (`docs/archive/geometry_oracle_slot6_Mars.exe-20260919-23.01.18-6a91a190.log`). The corrected table
  is `{4,1,3,0,2,5}`; `CanBuildOver` (`20_TrainHub.lua:329`) reads it too.
- **The lane offset is 289 units** (HexSize/2), `Enter1` left of the element's angle and `Enter2`
  right. Three agreeing derivations: the in-game slot 6 read, the vanilla file (`TrackPillarCCP3`,
  report §9), and the oracle's own LANE run (§10).
- **The element-angle rule** (MEASURED, slot 6, both logs): an element's angle is the *track's*, shared
  by both ends of a line — elements 1 and 2 at 60°, 3 and 4 at 180°, 5 and 6 at 120°. So `Enter1` is on
  the left looking outward at connectors 2, 3 and 5, and on the right at 1, 4 and 6.
- **The spot choice** (SOURCE, `Train.lua:665`, 1.1.0.403908): a train takes
  `"Enter" .. ((step == 1) and "1" or "2")` by its direction of travel along the track, so an arrival
  and a departure at one connector use *different* spots.
- **The train is 4150 × 416 × 432 units** (41.5 m × 4.16 m × 4.32 m), MEASURED four times in game, and
  it is **not centred on its origin along its length** (1332 one way, 2818 the other) — report §10.
  The oracle's sweep still centres the rectangle on the path point, which is up to 743 units of
  along-path error.
- **What the oracle does today, and the game does not** (§10): it applies the offsets in each
  connector's *outward* frame and routes every path through `Enter1`. The numbers CHOREOGRAPHY,
  CLEARANCE and TWO-TRAIN print under `--element-spots` (1438 of 1995 in run B) are **not to be
  used**; the fixture file carries the same warning.
- **Fixtures:** `corpus/current_5002a49.entjson`, `corpus/lua_current_6123ae7.lua`,
  `corpus/element_spots_measured_20260919.json`, and the look-pass work-file snapshot named in §10.
- Measured rules live in `_shared/IMPORTER_FACTS.md`; more records are in the bugs/facts `INDEX.md`.

## Work list (one commit-and-verify unit each; live in the todo tool before your first write)

1. **The element-angle rule in the path model.** Replace the outward-frame assumption with the
   track angle each element actually carries. The three verdicts' numbers change; that is the point.
2. **The arrival/departure spot choice.** A path into a connector and a path out of it pick
   different Enter spots, per `Train.lua:665`. Model the direction of travel, not a fixed spot.
3. **Re-run with the corrected table.** `{4,1,3,0,2,5}` as the model's input — a what-if, not an edit
   to the mod. Report what build 3b still has to solve once the table is right: the crossing lock,
   the ring-wall pass-through, the same-track Spawn (report §4 items 2 and 3), and whatever items 1
   and 2 newly expose or clear. **This is the run's deliverable**; the rest serves it.
4. **The off-centre sweep, if items 1–3 leave budget.** The 743-unit along-path error above. Drop
   this first if time runs short, and say so in the report.
5. **Close.** `smr-session-close`. The report is the home: add a dated addendum (§11) in the same
   shape as §10 — what changed, what it was measured or derived from, and what may now be used.
   Delete this file and its row in `docs/agent/prompts/README.md` in the commit that lands item 3.

## Scope

**In:** the oracle's path model in SMR-Assets, its corpus and selftest, and the report addendum here.
**Out:** editing `20_TrainHub.lua` (the table fix is build 3b's, and 3b owns that file); writing or
re-scoping 3b's brief; the hub's geometry, the asset, the pipeline and the look pass.

## Stops

- **The path model needs a rule that is not measured.** Report its shape and what would settle it;
  do not invent one and do not tune until the numbers fit.
- **The corrected table leaves a verdict failing in a way that implies an asset or body change.**
  That is the owner's call, through the orchestrator. Report it.
- **`--corpus` or `--selftest` cannot be kept green.** Report what broke rather than relaxing them.

## Do not claim

Not "trains behave", not "the hub's geometry is correct", and not that the corrected table fixes
3b. No train movement has been watched since `6123ae7`. Every number you produce is a **prediction**
from measured spots under source-read rules. The narrower true claim: *"under the corrected table
and the measured lane rules, the model predicts X; it is unwatched."*

## Lifecycle

One-off. Delete this file and its map row when item 3 lands.
