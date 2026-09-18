# Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched

## Must_Read_Header
<!-- RULES -->
Rule: Read `Must_Read_Header` before editing a document that has one.
Rule: Put a duty binding every agent in this file's `Must_Read_Header`, a duty binding one document in that document's own header, and state each duty exactly once; prose cites a rule and does not restate it.
Rule: Read a bare donor file name, `F##`/`C##` id or `Fix_*.lua` inside an adapted clause as the fix pack's, resolving under `C:\Dev\SMR-BugFixPack` and not here.
Rule: Invoke the `doc-editing` skill before editing a document; `smr-orientation` when status, placement or a count is the question; `smr-bug-library` before reading or filing an entry or fact.
Rule: Preserve the exact bytes of every persisted name listed in `docs/agent/PROVENANCE.md` §"The persisted-name inventory".
Rule: Keep executable code free of `SMRFixPack` references; persisted-name strings are data and exempt.
Rule: Change a shipping module's behaviour only under an owner ruling recorded for this mod.
Rule: Append to `docs/archive/` only; never rewrite or delete what is archived there.
Rule: Edit a generated file's source and regenerate it, never the output (`INDEX.md` in `bugs/` and `facts/`, `AGENTS.md`).
Rule: Run `python tools/doccheck.py` before committing documentation changes.
Rule: Ask the owner for a decision about THIS mod in `docs/DECISIONS_OWED.md`, and record the ruling where the role that obeys it reads it; a decision binding the FIX PACK goes to its `docs/PLAYTEST_CHECKLIST.md`.
Rule: Treat the owner's instruction as authority that agent detection cannot override.
Rule: Treat any authored artifact or message other than the owner's instruction as a claim, cleared by one check rather than a re-derivation.
Rule: Read volatile external values — the installed game build, counts, HEAD — with a command every time.
Rule: Cite a game source line only with the build it was read on, from the archived tree for that build.
Rule: Prove absence with a grep and count the presence side; never read a file to prove a negative.
Rule: Run a measurement before reporting it; mark `<<PENDING-RUN>>` any figure written before its command ran.
Rule: Attribute shared-tree work by commit and diff rather than author identity.
Rule: Recheck shared paths before writing.
Rule: Commit with a pathspec — `git commit -F <msgfile> -- <paths>` — never `-a`, never a bare `-m`.
<!-- /RULES -->

An **opt-in behaviour mod**: a small set of modules that change how the game plays, each one
**off (or at its base setting) until the player turns it on** in Options → Mod Options.
Live count source: `python tools/doccheck.py --emit-counts`; three modules were
RETIRED 2026-09-17 (owner) and the shipped set is smaller than every pre-09-17 record says.
Patched at runtime; no game files are modified. It is a **TRUE STANDALONE** — it works with the
Relaunched Fix Pack installed, and identically without it. ⛔ **NOT PUBLISHED.** Map of the tree: `docs/README.md`.

**The two bans are canonical rules in the header above.** Their scope is:

1. **Persisted names are save contract.** This includes every `SMRFixPack_*` field and modifier id
   this mod still writes; the inventory and reason are in `docs/agent/PROVENANCE.md`
   §"The persisted-name inventory".
2. **Executable references are absent.** The framework is this mod's own copy under
   `SMROptInPack`; persisted strings from item 1 are data, not references.

**MODULE FREEZE status:** the header rule applies. `D09` `DroneStatDials` is unfrozen (owner,
2026-08-31). `D06` was too and is now RETIRED/PARKED with `D07` + `D12` (owner, 2026-09-17);
nothing else is unfrozen.

⚠️ **The game auto-updated to 1.1.0 + DLC on 2026-09-08 and overwrote `ModTools\Src`.** Records
written before then cite a tree that is not installed. Both trees are archived at
`C:\Dev\SMR-SrcArchive\{1.0.7.396349,1.1.0.403908}\Src` (`EF-083`);
`python tools/doccheck.py --emit-fingerprint` says which fact groups still HOLD.

**Names that are contract, not display.** The mod id `SMR_CommunityOptInPack`, the global
`SMROptInPack` and the log prefix `[CommunityOptInPack]` are UNCHANGED across both family renames
(2026-08-13 "Community Fix Pack: Opt-In Modules", 2026-08-17 "Relaunched Fix Pack: Opt-In
Modules"). Earlier records retain the older names and pre-split paths.

> **Split out of `SMR-BugFixPack` @ `33d69f5` on 2026-08-12** (chain `split-optins`). Policies,
> engine facts, tooling and doc conventions came with it — `docs/agent/PROVENANCE.md` says what came
> from where, at which sha, and what was adapted. Pre-split records in the fix pack cite
> `Code/Opt_*.lua` paths in THAT repo and the `SMRFixPack` namespace.

**Folder contract** (doccheck enforces it, in both directions). `docs/` root holds only
`DECISIONS_OWED.md`, `FUTURE_IDEAS.md`, `README.md`, `agent/` and `archive/`. Agent material is
`docs/agent/` (`bugs/`, `facts/`, `reports/`, `prompts/`, `support/`, STATE/WORKFLOW/FIX_POLICY/PROVENANCE).
`support/` holds BINDING protocol pulled out of a routing document — authority, unlike `reports/`.
Prompts: the map is `docs/agent/prompts/README.md`, reusable ones live in `prompts/perma/`, and
one-offs live at the prompt root until consumed. The prompt map and generated-file duties are in
the header above; `python tools/doccheck.py --regen` performs regeneration.

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
`docs/agent/reports/CHAIN_METHOD.md`. `AGENTS.md` is the generated byte copy of this file for Codex.
