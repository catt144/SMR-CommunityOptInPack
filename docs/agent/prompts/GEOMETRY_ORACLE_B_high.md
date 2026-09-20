# Geometry oracle, run B: finish the measurements and judge the last worker

**LIVE, fire when ready.** Run A (2026-09-19 evening) built and committed the instrument and its
report; it ran out of context with one worker still out and two reads still owed. This brief is
the handoff. Everything below "State" is settled and committed; do not re-derive it.

## Authority

Owner, 2026-09-19 (`GEOMETRY_ORACLE_high.md`, consumed): a geometry mistake is found from files
on disk before a re-import; a rule is trusted only with two independent derivations that agree;
never tune a model until the numbers fit. Owner, same evening: an agent may launch the game
itself and the owner is not a required participant (`tools/SMRTK.md`, `978768b`). Working method
the owner set for run A: build through opus subagents and judge their returns yourself; one model
family per independent derivation (Codex CLI is GPT-5.4:
`codex exec --skip-git-repo-check --sandbox workspace-write -C <dir> - < prompt.txt`); never clear
a rule with the worker that produced it.

## State (committed; treat as claims cleared by one check each)

- Instrument: `C:\Dev\SMR-Assets\_shared\geometry\hub_oracle.py` (SMR-Assets `d990f48`, `0e73021`),
  `corpus/` with `EXPECTED.json`; `--corpus` 17/17, `--selftest` 6/6, both re-run by run A's judge
  on the committed file. README there says how to run it.
- Report: `docs/agent/reports/GEOMETRY_ORACLE_20260919.md` (this repo, the commit that deleted
  `GEOMETRY_ORACLE_high.md`). Its §2 table lists every rule, both derivations, and status.
- Measured in game 2026-09-19: all 24 synthetic spots and six connectors equal the file-side
  prediction (zero delta) — `docs/archive/geometry_oracle_readings_20260919.log`,
  `docs/archive/geometry_oracle_slot6_Mars.exe-20260919-23.01.18-6a91a190.log`. Lane: each
  connector element's `Enter1`/`Enter2` are 289 units left/right of the track centreline at the
  connector hex centre (HexSize/2), z = the deck. The finding (`hub_connector_directions`
  wrong for indices 1–4) is in the report §0 and in `TRAIN_HUB_TRAINS_high.md`'s hold block.
- TestKit slot 6 `geometry_reads` (kit `bd32d30`) takes the read with no selection and logs it on
  LoadGame when a hub exists. Known defect: it prints `pos=` empty for elements; the Enter
  midpoint supplies the position.
- `_shared/IMPORTER_FACTS.md` carries the newly measured rules (spot angle made precise, +X arrow
  at a − 90°, integer 866 row, hex_shape centre rule and corner ambiguity, element on its hex,
  50 m arrival teleport).

## Work list (one commit-and-verify unit each)

1. **The decoder's return.** An Opus agent was decoding vanilla `BinAssets.fpk:entities.dat`
   (scratch `…\scratchpad\entdecode\` of run A's session; the extracted pack is in
   `…\scratchpad\packs\BinAssets\`; re-extract with `tools/flpk_extract.py`'s `extract()` if the
   scratch is gone). If `C:\Dev\SMR-Assets\_shared\geometry\entities_dat.py` exists or the agent's
   findings are recoverable, judge them against the anchors before anything uses them:
   `TrackPillarCCP3` bbox 1000×204, z −1726..1069; its `Enter1`/`Enter2` at (0, ±289, 800) in the
   element frame (measured, slot 6); `TrainStationLargeCCP3` outline 95 hexes and line radii
   5 6 5 4 4 4; `FusionReactor` outline 7; `TrackPillarCCP3` outline 1. A decode that passes gives
   R-LANE and R-FOOT their vanilla-file second derivation: run the oracle's R-FOOT rule on the
   vanilla hex_shape triangles and compare with 95 / 7 / 1. Commit in SMR-Assets with its anchors
   in the message; if it fails, say what decoded and what did not, and stop there.
2. **LANE verdict with the measured offset.** Run
   `python hub_oracle.py --entity corpus/current_5002a49.entjson --lua corpus/lua_current_6123ae7.lua --element-spots <json> --workfile-snapshot ../../trainhub/blender/export/lookpass_workfile_geometry.json`
   with `{"Enter1": [0, 289, 0], "Enter2": [0, -289, 0]}` (read the oracle's `--element-spots`
   handling first; the offsets are in the element's frame, x along its angle). Record the LANE
   section's numbers in the report's §3 (a short addendum, dated) and re-run `--corpus` and
   `--selftest` after any change to the oracle.
3. **The train's size.** Slot 6 with a train on the map, or `print(GetEntityBBox("TrainCCP3"))`
   (`Train.lua:38`); put the bbox into `--train-width-m`/`--train-length-m` defaults only if the
   owner's reads confirm them, and drop R-TRAIN from UNCONFIRMED in the report.
4. **Close.** `smr-session-close`: the report is the home for everything above; `STATE.md` was not
   touched by run A. Delete this file and its row in `docs/agent/prompts/README.md` in the commit
   that lands item 2 or 3, whichever is last.

## Scope

In: items 1–4 and their records. Out: changing the hub's geometry, the spot Lua or the pipeline
(3b's re-scope is the orchestrator's, `perma/TRAIN_ORCHESTRATOR.md`); the look pass.

## Stops

- The decoder's anchors do not pass and the fix is not obvious: report what decoded, stop.
- The oracle's LANE code needs more than the JSON to use the offset: report the shape, stop.

## Do not claim

Not "trains behave" or "the hub's geometry is correct": every choreography number is a prediction
from measured spots under source-read rules; no train movement has been watched since `6123ae7`.

## Lifecycle

One-off. Delete this file and its map row when items 1–4 land.
