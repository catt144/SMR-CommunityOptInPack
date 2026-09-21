# prompts/ — the map

## Must_Read_Header
<!-- RULES -->
Rule: Keep `docs/agent/prompts/` to mapped prompts, its README map, mapped live-chain evidence and README files; put supporting documents in `docs/agent/support/`. [A3: pass]
<!-- /RULES -->

Structure carried from the fix pack's `prompts/README.md` on 2026-09-17
(donor @ `e6ec192`); its own map was reorganised 2026-09-11 by owner ask.

**Rule-placement answer — a guard.** `tools/doccheck.py`'s **PROMPT MAP** gate checks the declared
class and both directions of the mapped structure. It cannot decide whether prose actually makes a
session do a job: the human classification and map-description review remain.

| where | what | lifecycle |
|---|---|---|
| **`perma/`** | reusable standing prompts | `prompt-authoring` |
| root `*.md` | live one-off prompts, not yet fired or kept by an owner ruling | `prompt-authoring` |
| chain folders | live multi-link efforts; mapped evidence and README files may stay while live | `support/CHAIN_METHOD.md` |

**This map lists live prompts only.** A fired one-off leaves no tombstone; its outcome already
lives in its report or entry, and the grave is available through
`git log --diff-filter=D -- docs/agent/prompts/` (append `<name>` for one file). The PROMPT MAP
gate rejects a struck row or a file/row mismatch.

The `declared class` values below are gate inputs, not conclusions inferred from filenames.

## `perma/` — standing prompts

| prompt | declared class | use it for |
|---|---|---|
| `WORK_PROMPT.md` | `prompt` | **START HERE for any work on this mod** — designing or changing a module, building one, investigating engine behaviour, docs, tooling, launch prep. Re-runnable; routes to the task skills |
| `DISPATCH.md` | `prompt` | live-issue triage: a player report, a field bug, something the owner noticed in play. ⚠️ Scope is issues **once the mod is live**, and it is not (owner, 2026-08-31) |
| `STATE_EVICTION.md` | `prompt` | requested STATE cleanup or a doccheck size warning; apply the complete four-part admission door (harm · reach · gate · volatility, AND-ed) to every section and verify refused content's homes |
| `gamepatch/` (README, `done/`) | `outbox` | after a game patch: the fix pack's `GAME_PATCH_PROMPT.md` leaves one entry per patch here, even when nothing is flagged; read the newest, run its command, file verdicts, move it to `done/` (its README) |
| `KNOWLEDGE_SYNC_PASS.md` | `prompt` | does this repo hold what it cites, and what it needs? A re-runnable cross-repo sweep against the fix pack: acts on what it decides, recommends the rest, and carries out what the owner agrees |
| `TRAIN_ORCHESTRATOR.md` | `prompt` | the train logistics project's standing lead: review build agents' reports, keep the spec current, brief the next build. ⛔ **Temporary:** purge it when the trains project is complete and tested (owner, 2026-09-18) |

## Root — live one-offs

| prompt | declared class | state |
|---|---|---|
| `RELEASE_SYSTEM_high.md` | `prompt` | **LIVE, fire when ready.** Build this repo's release system on the fix pack's (owner, 2026-09-18): `UPLOAD_WORKFLOW.md`, `release_prompt.md`, `RELEASE_OUTBOX.md`, `RELEASE_HISTORY.md` and the three release support docs under the fix pack's names, a first-publish path, and this mod's steps on the shared site `B:\Dev\SMR\SMR-CommunityMods` (read-only for the build) |
| `TRAIN_HUB_LOOK_high.md` | `prompt` | **LIVE, RESUMING STAGED (owner, 2026-09-21).** Body and concept maps imported; glow works but the hub reads as flat "blue paint" — measured: normal 97.9% flat, base colour 84.2% one value, RM mostly nonmetallic (corrected by the full histogram in spec §9), at vanilla's own format and size. The AI texturing trial is closed (no usable tool). Owner's order, spec §9: road surfaces as polished black glass first; pad B chosen provisionally (owner, 2026-09-21; assets `ea82ef4`, spec §9), reopened if glow lights spoil the reflections, then structure, lights, fine normal. Glass and themed reactor stay deferred. Survives until owner accepts the look |
| `TRAIN_HUB_STRUCTURE_high.md` | `prompt` | **LIVE, fire AFTER the lights brief's paint half lands** (owner, 2026-09-21). Look step 2: the hub structure (ring, portals, ribs, supports, rails, trim) built to a premium, wonder-scale bar: BaseColor 4096 supersampled, other maps 2048, crisp panel seams, road untouched by value; one importer run; restore point on the owner's keep. Deleted when fired |
| `TRAIN_HUB_MOVE_high.md` | `prompt` | **LIVE, fire when ready — REWRITTEN 2026-09-21 for a fresh agent.** All the movement work is done and accepted except one transition: the slide onto the loading siding. The previous agent answered every "start it further along the track" with a speed change, leaving a jerk. Two jobs: delete the run-length speed scaling in `HubMoveOntoSiding` so the lateral rate matches the accepted outer slide, then move the onset later in the travel as a live tunable |
| `TRAIN_HUB_MODEL_high.md` | `prompt` | **LIVE but idle: the model is FINAL** (owner, 2026-09-21: everything fits and nothing clips), tagged `hub-model-final-untextured` in both repos. Passes 1–3 are imported and accepted: longer stubs, twelve transition arms, six loading sidings sized 25.5 m by 5.5 m after a parked car overhung 23.0. Kept only for the geometry it records and a stop to reopen if the look pass needs the model to move |
| `TRAIN_HUB_REPAIR_high.md` | `prompt` | ⛔ **HELD until the movement prototype's smoke is recorded (`TRAIN_HUB_MOVE_high.md`).** Build 4: the hub's on-demand repair drones (owner, 2026-09-19): vanilla Wasps under the hub, a constant 30, never charging; anything a drone does within 15 hexes, track repair along the connected network beyond it, paid from the hub's stock on a persisted deadline, with a save guard for track mode. Adds one persisted name |
| `TRAIN_HUB_BUILDTRACK_high.md` | `prompt` | ⛔ **HELD until build 4's smoke is recorded.** Build 5: the hub builds new track from stock through build 4's completion path (owner, 2026-09-19), sequentially from the connected end; a line does not start until one end station is on the hub's network, and starts when it becomes connected. No new persisted name if build 4's list carries the kind |
| `FIX_D02_D03_D04_1_1_0_medium.md` | `prompt` | **LIVE, fire when ready.** Owner-ruled 2026-09-18: repair D03's dead tourist guard (`OI-03` (a)), build D04's sun-removal relink (`OI-04` (a), overriding its own recommendation), and widen D02's split notification-id set (`OI-17` (a)). All three designs and citations are in the brief; none has been run in the game yet |
| `TRAIN_HUB_LOADERRORS_low.md` | `prompt` | **LIVE, fire when ready.** Two errors the owner found in the 2026-09-21 session log, both firing on the dev hub's load path every load: `SMROptInTrainHubBase.ShouldShowNotConnectedToPowerGridSign` ambiguously inherited from `ElectricityProducer` and `ElectricityConsumer`, and an `ASSERT(m_pMap)` from the `WaitWakeup` wrapper calling `AllMapsForEach` with no map loaded. Causes measured and cited; dev-mod only, no persisted name, no ship gate |
| `RAIL_SHAFT_PROTOTYPE_high.md` | `prompt` | **LIVE, fire when ready** (owner, 2026-09-21). Research how a unit crosses maps (the elevator's transfer path) and build a throwaway dev mod for a train tunnel whose two ends sit on different maps — the elevator bypass from `reports/ELEVATOR_LOGISTICS_OPTIONS.md`. Carries the source citations and the 2026-09-21 console result: a train did change map and city, kept its old coordinates, and stranded mid-hop. Dev-only, prototype first; nothing ships |
| `DRONE_REBUILD_BUILD_high.md` | `prompt` | ⛔ **LIVE, NOT FIRED — HELD, and its subject is PARKED.** `D06 DroneOverhaul` was RETIRED/PARKED 2026-09-17 (owner) and no longer ships. This brief and the spec it builds from were written against **1.0.7** and are **NOT re-based** on 1.1.0, which deleted `CalcLapTime` — the instrument the design's numbers came from. ⛔ Do not fire it: it must be re-based before its owner asks (spec §9) can go on `docs/PLAYTEST_CHECKLIST.md` (`bugs/D06.md`). Kept, not archived, because the owner parked the module rather than killing it |

## Chain folders

*None live.* A chain folder appears here while its links are live and leaves `prompts/` when the
effort closes (`agent/support/CHAIN_METHOD.md` is the method for an effort over about two sessions).

## Authoring

Invoke the **`prompt-authoring`** skill. It carries the shape: authority first, end state, judgement
handed over, a live work list, scope in two lines, at most three stops, a declared lifecycle, and
the difficulty suffix — `_low`, `_medium`, `_high`, `_fanout_level_<x>` — which is the owner's
routing hint, never a gate, and never names a model.

New reusable prompts live in `perma/`; new one-offs live at the root. The `prompt-authoring` skill
owns their lifecycle.

⚠️ **The playtest prompt is single-sourced in the FIX PACK** — `prompts/perma/GENERAL_USE_PROMPT.md`
there is for a live playtest at the keyboard, because the owner plays one game with both mods
loaded. `docs/README.md` says why.
