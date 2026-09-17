# Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched

## Must_Read_Header
<!-- RULES -->
Rule: Read `Must_Read_Header` before editing a document that has one.
Rule: Invoke the `doc-editing` skill before editing a document; `smr-orientation` when status, placement or a count is the question; `smr-bug-library` before reading or filing an entry or fact.
Rule: Append to `docs/archive/` only; never rewrite or delete what is archived there.
Rule: Edit a generated file's source and regenerate it, never the output (`INDEX.md` in `bugs/` and `facts/`, `AGENTS.md`).
Rule: Run `python tools/doccheck.py` before committing documentation changes.
Rule: Ask the owner for a decision about THIS mod in `docs/DECISIONS_OWED.md`, and record the ruling where the role that obeys it reads it; a decision binding the FIX PACK goes to its `docs/PLAYTEST_CHECKLIST.md`.
Rule: Treat the owner's instruction as authority that agent detection cannot override.
Rule: Treat any authored artifact or message other than the owner's instruction as a claim, cleared by one check rather than a re-derivation.
Rule: Read volatile external values — the installed game build, counts, HEAD — with a command every time.
Rule: Never hand-type a count; `python tools/doccheck.py --emit-counts` prints them.
Rule: Cite a game source line only with the build it was read on, from the archived tree for that build.
Rule: Prove absence with a grep and count the presence side; never read a file to prove a negative.
Rule: Run a measurement before reporting it; mark `<<PENDING-RUN>>` any figure written before its command ran.
Rule: Attribute shared-tree work by commit and diff rather than author identity, and recheck shared paths before writing.
Rule: Commit with a pathspec — `git commit -F <msgfile> -- <paths>` — never `-a`, never a bare `-m`.
<!-- /RULES -->

An **opt-in behaviour mod**: a small set of modules that change how the game plays, each one
**off (or at its base setting) until the player turns it on** in Options → Mod Options.
⛔ Never hand-type how many — `python tools/doccheck.py --emit-counts`; three modules were
RETIRED 2026-09-17 (owner) and the shipped set is smaller than every pre-09-17 record says.
Patched at runtime; no game files are modified. It is a **TRUE STANDALONE** — it works with the
Relaunched Fix Pack installed, and identically without it. ⛔ **NOT PUBLISHED.** Map of the tree: `docs/README.md`.

**⛔ The two bans, before you touch anything:**

1. **PERSISTED NAMES ARE SAVE CONTRACT.** Any string that ever entered a savegame keeps its EXACT
   bytes — including every `SMRFixPack_*` field and modifier id this mod still writes. They look
   like the other mod's names and they are not renameable. Inventory + the reason:
   `docs/agent/PROVENANCE.md` §"The persisted-name inventory". Renaming one is FORBIDDEN.
2. **ZERO `SMRFixPack` references in executable code.** The framework is this mod's own copy under
   `SMROptInPack`. No cross-mod `Require`, no load-order assumption, no shared file. (The persisted
   STRINGS in ban 1 are data, not references — that is the whole distinction.)

⛔ **MODULE FREEZE:** no behaviour change to any shipping module without an owner ruling. `D09`
`DroneStatDials` is unfrozen (owner, 2026-08-31). `D06` was too and is now RETIRED/PARKED with
`D07` + `D12` (owner, 2026-09-17) — retiring them WAS the ruling; nothing else is unfrozen.

⚠️ **The game auto-updated to 1.1.0 + DLC on 2026-09-08 and overwrote `ModTools\Src`.** Records
written before then cite a tree that is not installed. Both trees are archived at
`C:\Dev\SMR-SrcArchive\{1.0.7.396349,1.1.0.403908}\Src` (`EF-083`);
`python tools/doccheck.py --emit-fingerprint` says which fact groups still HOLD.

**Names that are contract, not display.** The mod id `SMR_CommunityOptInPack`, the global
`SMROptInPack` and the log prefix `[CommunityOptInPack]` are UNCHANGED across both family renames
(2026-08-13 "Community Fix Pack: Opt-In Modules", 2026-08-17 "Relaunched Fix Pack: Opt-In
Modules"). Earlier records use the older names — translate mentally, do not edit records.

> **Split out of `SMR-BugFixPack` @ `33d69f5` on 2026-08-12** (chain `split-optins`). Policies,
> engine facts, tooling and doc conventions came with it — `docs/agent/PROVENANCE.md` says what came
> from where, at which sha, and what was adapted. Pre-split records in the fix pack cite
> `Code/Opt_*.lua` paths in THAT repo and the `SMRFixPack` namespace.

**Folder contract** (doccheck enforces it, in both directions). `docs/` root holds only
`DECISIONS_OWED.md`, `FUTURE_IDEAS.md`, `README.md`, `agent/` and `archive/`. Agent material is
`docs/agent/` (`bugs/`, `facts/`, `reports/`, `prompts/`, `support/`, STATE/WORKFLOW/FIX_POLICY/PROVENANCE).
`support/` holds BINDING protocol pulled out of a routing document — authority, unlike `reports/`.
Prompts: the map is `docs/agent/prompts/README.md`, reusable ones live in `prompts/perma/`, and
a consumed one-off deletes itself AND its map row — doccheck gates that both ways.
`docs/archive/` is append-only. `INDEX.md` in `bugs/` and `facts/` is GENERATED (line-1 banner) —
`python tools/doccheck.py --regen`.

⚠️ **The human playtest file lives in the FIX PACK repo.** `PLAYTEST_CHECKLIST.md` is single-sourced
in `C:\Dev\SMR-BugFixPack\docs\` because the owner plays ONE game with BOTH mods loaded;
`docs/README.md` says why. ⛔ Its companion `PLAYTEST_HELP.md` was DISSOLVED there on 2026-09-15
(`c91310f`) and its content consumed — every reference to it in this repo was a dead pointer until
2026-09-17. This mod's own owner decisions live here, in `docs/DECISIONS_OWED.md` (owner, 2026-09-12).

**`docs/archive/` is hidden from a default `rg`** by a root `.rgignore` — a deliberate boundary, not
a deletion. Search it by naming it: `rg <term> docs/archive/`, or `rg --no-ignore <term>` for both.
`grep -r`, `git grep` and `git log` always see everything. An empty default search is the boundary
working.

Hook setup, once per clone: `git config core.hooksPath tools/hooks`. Authoring
`docs/agent/WORKFLOW.md` · code `docs/agent/FIX_POLICY.md` · efforts over about two sessions
`docs/agent/reports/CHAIN_METHOD.md`. `AGENTS.md` is a generated byte copy of this file for Codex —
never edit it.
