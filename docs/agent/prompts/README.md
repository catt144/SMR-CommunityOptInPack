# prompts/ — the map

## Must_Read_Header
<!-- RULES -->
Rule: Keep `docs/agent/prompts/` to mapped prompts, its README map, and mapped live-chain evidence and README files; put supporting documents in `docs/agent/reports/`.
Rule: A prompt is reachable from this map or it does not exist; every row names a file on disk and every file on disk has a row.
Rule: Delete a consumed one-off AND its row here in the same commit. Never leave a tombstone.
<!-- /RULES -->

Structure carried from the fix pack's `prompts/README.md` on 2026-09-17
(`agent/PROVENANCE.md` §8); its own map was reorganised 2026-09-11 by owner ask.

**Rule-placement answer — a guard.** `tools/doccheck.py`'s **PROMPT MAP** gate checks the declared
class and both directions of the mapped structure. It cannot decide whether prose actually makes a
session do a job: the human classification and map-description review remain.

| where | what | lifecycle |
|---|---|---|
| **`perma/`** | reusable standing prompts | update in place; they are never deleted after a run |
| root `*.md` | live one-off prompts, not yet fired or kept by an owner ruling | `git rm` the file **and delete its row here, in the same commit**, when fired or consumed |
| chain folders | live multi-link efforts; mapped evidence and README files may stay while live | leave `prompts/` when closed |

⛔ **This map lists LIVE prompts only — no tombstones.** A fired one-off leaves here entirely: no
struck-through row, no "removed/consumed" prose. The outcome already lives in its report or entry,
and the grave is one command away — `git log --diff-filter=D -- docs/agent/prompts/` (append
`<name>` for one file). doccheck's **PROMPT MAP** gate holds both directions, and a struck row is
RED. A row that outlives its file is how a next session fires spent work.

The `declared class` values below are gate inputs, not conclusions inferred from filenames.

## `perma/` — standing prompts

| prompt | declared class | use it for |
|---|---|---|
| `WORK_PROMPT.md` | `prompt` | **START HERE for any work on this mod** — designing or changing a module, building one, investigating engine behaviour, docs, tooling, launch prep. Re-runnable; names the five skills |
| `DISPATCH.md` | `prompt` | live-issue triage: a player report, a field bug, something the owner noticed in play. ⚠️ Scope is issues **once the mod is live**, and it is not (owner, 2026-08-31) |
| `STATE_EVICTION.md` | `prompt` | requested STATE cleanup or a doccheck size warning; apply the complete four-part admission door (harm · reach · gate · volatility, AND-ed) to every section and verify refused content's homes |
| `KNOWLEDGE_SYNC_PASS.md` | `prompt` | does this repo hold what it cites, and what it needs? A re-runnable cross-repo sweep against the fix pack, not a one-off |

## Root — live one-offs

| prompt | declared class | state |
|---|---|---|
| `WORKFLOW_SHRINK_high.md` | `prompt` | ⛔ **LIVE, NOT FIRED.** Shrink `agent/WORKFLOW.md` toward the fix pack's shape under the owner's OI-09 ruling that agent docs may be cut hard. Carries the measured section-by-section census (the efficiency survey's §5 question, answered), the three buckets, the protected list and a 30,000 B cap that is explicitly not the goal. The 29,108 B Co-runs move is already done at `8192a63` and is the pattern to copy |
| `DRONE_REBUILD_BUILD_high.md` | `prompt` | ⛔ **LIVE, NOT FIRED — HELD, and its subject is PARKED.** `D06 DroneOverhaul` was RETIRED/PARKED 2026-09-17 (owner) and no longer ships. This brief and the spec it builds from were written against **1.0.7** and are **NOT re-based** on 1.1.0, which deleted `CalcLapTime` — the instrument the design's numbers came from. ⛔ Do not fire it: it must be re-based before `DECISIONS_OWED` 94 then 92 can even be ruled on. Kept, not archived, because the owner parked the module rather than killing it |

## Chain folders

*None live.* A chain folder appears here while its links are live and leaves `prompts/` when the
effort closes (`agent/reports/CHAIN_METHOD.md` is the method for an effort over about two sessions).

## Authoring

Invoke the **`prompt-authoring`** skill. It carries the shape: authority first, end state, judgement
handed over, a live work list, scope in two lines, at most three stops, a declared lifecycle, and
the difficulty suffix — `_low`, `_medium`, `_high`, `_fanout_level_<x>` — which is the owner's
routing hint, never a gate, and never names a model.

**New prompts:** a reusable one goes in `perma/`; a one-off goes in the root and, when consumed,
deletes **both** itself and its row above in the commit that lands its result.

⚠️ **The playtest prompt is single-sourced in the FIX PACK** — `prompts/perma/GENERAL_USE_PROMPT.md`
there is for a live playtest at the keyboard, because the owner plays one game with both mods
loaded. `docs/README.md` says why.
