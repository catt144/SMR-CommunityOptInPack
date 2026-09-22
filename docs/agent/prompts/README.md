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

## Root — live one-offs

| prompt | declared class | state |
|---|---|---|
| `RELEASE_SYSTEM_high.md` | `prompt` | **LIVE, fire when ready.** Build this repo's release system on the fix pack's (owner, 2026-09-18): `UPLOAD_WORKFLOW.md`, `release_prompt.md`, `RELEASE_OUTBOX.md`, `RELEASE_HISTORY.md` and the three release support docs under the fix pack's names, a first-publish path, and this mod's steps on the shared site `B:\Dev\SMR\SMR-CommunityMods` (read-only for the build) |
| `RAIL_SHAFT_PROTOTYPE_high.md` | `prompt` | **LIVE, fire when ready** (owner, 2026-09-21). Research how a unit crosses maps (the elevator's transfer path) and build a throwaway dev mod for a train tunnel whose two ends sit on different maps — the elevator bypass from `reports/ELEVATOR_LOGISTICS_OPTIONS.md`. Carries the source citations and the 2026-09-21 console result: a train did change map and city, kept its old coordinates, and stranded mid-hop. Dev-only, prototype first; nothing ships |
| `DRONE_REBUILD_BUILD_high.md` | `prompt` | ⛔ **LIVE, NOT FIRED — HELD, and its subject is PARKED.** `D06 DroneOverhaul` was RETIRED/PARKED 2026-09-17 (owner) and no longer ships. This brief and the spec it builds from were written against **1.0.7** and are **NOT re-based** on 1.1.0, which deleted `CalcLapTime` — the instrument the design's numbers came from. ⛔ Do not fire it: it must be re-based before its owner asks (spec §9) can go on `docs/PLAYTEST_CHECKLIST.md` (`bugs/D06.md`). Kept, not archived, because the owner parked the module rather than killing it |

## Chain folders

| chain | declared class | state |
|---|---|---|
| `Train_Hub_Project/` | `live` | The train hub project (Module B): its standing orchestrator and its build briefs, numbered in fire order, with `Parked/` for briefs that are not to be fired. Its own `README.md` says what each is for and which is next. ⛔ Temporary: the whole folder goes when the trains project is complete and tested (owner, 2026-09-18) |

A chain folder appears here while its links are live and leaves `prompts/` when the
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
