# Community Opt-In Pack — Surviving Mars: Relaunched

⚠️ **"Community Opt-In Pack" is a PLACEHOLDER display name** (owner call at
launch prep). The mod id `SMR_CommunityOptInPack`, the global `SMROptInPack`
and the log prefix `[CommunityOptInPack]` are the working names this repo was
built with; every player-visible site that carries the placeholder is listed in
`docs/agent/PROVENANCE.md`.

An **opt-in behaviour mod**: eight modules that change how the game plays, each
one **off (or at its base setting) until the player turns it on** in Options →
Mod Options. Patched at runtime; no game files are modified. It is a
**TRUE STANDALONE** — it works with the Community Fix Pack installed, and
identically without it. Map of the tree: `docs/README.md`. **Mandatory read,
every session: `docs/agent/STATE.md`** — build state, open gates, active holds.

> **Split out of `SMR-BugFixPack` @ `33d69f5` on 2026-08-12** (chain
> `split-optins`). Policies, engine facts, tooling and doc conventions came
> with it — `docs/agent/PROVENANCE.md` says what came from where, at which sha,
> and what was adapted. Pre-split records in the fix pack cite `Code/Opt_*.lua`
> paths in THAT repo and the `SMRFixPack` namespace; translate mentally, do not
> edit records.

**⛔ The two bans, before you touch anything:**

1. **PERSISTED NAMES ARE SAVE CONTRACT.** Any string that ever entered a
   savegame keeps its EXACT bytes — including every `SMRFixPack_*` field and
   modifier id this mod still writes. They look like the other mod's names and
   they are not renameable. Inventory + the reason: `docs/agent/PROVENANCE.md`
   §"The persisted-name inventory". Renaming one is FORBIDDEN.
2. **ZERO `SMRFixPack` references in executable code.** The framework is this
   mod's own copy under `SMROptInPack`. No cross-mod `Require`, no load-order
   assumption, no shared file. (The persisted STRINGS in ban 1 are data, not
   references — that is the whole distinction.)

**Folder contract** (doccheck enforces it). `docs/` root holds ONLY
`FUTURE_IDEAS.md`, `README.md`, `agent/` and `archive/`. Agent material is
`docs/agent/` (`bugs/`, `facts/`, `reports/`, `prompts/`,
STATE/WORKFLOW/FIX_POLICY/PROVENANCE); `docs/archive/` is append-only, never
edited. **`INDEX.md` in `bugs/`+`facts/` is GENERATED — edit the entry or fact
file, never the index** (line-1 banner).

Before committing doc changes run `python tools/doccheck.py`; red blocks. Set up
once: `git config core.hooksPath tools/hooks`. **Owner decisions go in the FIX
PACK's `docs/PLAYTEST_CHECKLIST.md` → "Decisions waiting on you"** (that file is
deliberately single-sourced there — `docs/README.md` says why), never only in an
agent doc. Authoring `docs/agent/WORKFLOW.md` · code `docs/agent/FIX_POLICY.md`
· efforts over ~2 sessions `docs/agent/reports/CHAIN_METHOD.md`.
