# Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched

## Must_Read_Header
<!-- RULES -->
Rule: Read `Must_Read_Header` before editing a document that has one. [A3: pass]
Rule: Invoke the `doc-editing` skill before editing a document. [A3: pass]
Rule: Append to `docs/archive/` only; never rewrite or delete what is archived there. [A3: pass]
Rule: Edit a generated file's source and regenerate it, never the output. [A3: pass]
Rule: Run `python tools/doccheck.py` before committing documentation changes. [A3: pass]
Rule: Ask the owner for a decision in `docs/PLAYTEST_CHECKLIST.md` and record the ruling where the role that obeys it reads it. [A3: pass]
Rule: Treat the owner's instruction as authority that agent detection cannot override. [A3: pass]
Rule: Verify command output carrying its command and HEAD or build identifier once without rereading its sources. [A3: pass]
Rule: Treat any authored artifact or message other than the owner's instruction as a claim, cleared by one check rather than a re-derivation. [A3: pass]
Rule: Read volatile external values with a command every time. [A3: pass]
Rule: Read `docs/agent/STATE.md` and `docs/PLAYTEST_CHECKLIST.md` only when a task, a prompt or the owner calls for them; current work is pull, never session-start reading. [A3: pass]
Rule: Verify durable structural facts by fingerprint and rederive only groups that moved. [A3: pass]
Rule: Cite a game source line with the build it was read on, from that build's archived tree. [A3: pass]
Rule: Prove absence with a grep after decoding compressed inputs and count the presence side. [A3: pass]
Rule: Scope every verification command so contrary evidence could make it fail. [A3: pass]
Rule: Run a measurement before reporting it; mark `<<PENDING-RUN>>` any figure written before its command ran. [A3: pass]
Rule: Record every count with its command and filter and reconcile each total against its members. [A3: pass]
Rule: Record the executed model from the transcript at close-out. [A3: pass]
Rule: Attribute shared-tree work by commit and diff rather than author identity. [A3: pass]
Rule: Recheck shared paths before writing; commit with a pathspec unless partial hunks of a peer-shared file are staged, which a pathspec would discard. [A3: pass]
Rule: Read a bare donor file name, `F##`/`C##` id or `Fix_*.lua` inside an adapted clause as the fix pack's, resolving under `B:\Dev\SMR\SMR-BugFixPack` and not here. [A3: pass]
Rule: Change a shipping module's behaviour only under an owner ruling recorded for this mod. [A3: pass]
<!-- /RULES -->

An **opt-in behaviour mod**: a small set of modules that change how the game plays, each one
**off (or at its base setting) until the player turns it on** in Options → Mod Options.
Live count source: `python tools/doccheck.py --emit-counts`; three modules were
RETIRED 2026-09-17 (owner) and the shipped set is smaller than every pre-09-17 record says.
Patched at runtime; no game files are modified. It is a **TRUE STANDALONE** — it works with the
Relaunched Fix Pack installed, and identically without it. ⛔ **NOT PUBLISHED.** The tree map is
`docs/README.md`.

**The two bans are canonical rules in `docs/agent/FIX_POLICY.md`'s header**, read before any code
change. Their scope is:

1. **Persisted names are save contract.** This includes every `SMRFixPack_*` field and modifier id
   this mod still writes; the inventory and reason are in `docs/agent/FIX_POLICY.md`
   §"The persisted-name inventory".
2. **Executable references are absent.** The framework is this mod's own copy under
   `SMROptInPack`; persisted strings from item 1 are data, not references.

**MODULE FREEZE status:** the header rule applies. `D09` `DroneStatDials` was unfrozen first
(owner, 2026-08-31); `D06` was too and is now RETIRED/PARKED with `D07` + `D12` (owner,
2026-09-17). **Owner ruling 2026-09-18: the freeze is lifted on every remaining shipping
module** — `D02` `AcknowledgedWarnings`, `D03` `ResidencyControl`, `D04` `MultipleSuns`
(`D01` `ClassicRockets` was named too; it is RETIRED, OVERTAKEN, owner 2026-09-18). Nothing in
this mod is frozen. The header rule itself still applies: a
behaviour change still wants an owner ruling recorded for this mod — this lifts the freeze
gate, not the record-the-ruling duty.

**Names that are contract, not display.** The mod id `SMR_CommunityOptInPack`, the global
`SMROptInPack` and the log prefix `[CommunityOptInPack]` are UNCHANGED across both family renames
(2026-08-13 "Community Fix Pack: Opt-In Modules", 2026-08-17 "Relaunched Fix Pack: Opt-In
Modules"). Earlier records retain the older names and pre-split paths.

**Folder contract** (doccheck enforces it, in both directions). `docs/` root holds only
`PLAYTEST_CHECKLIST.md`, `FUTURE_IDEAS.md`, `PARKED_MODULES.md`, `README.md`, `agent/` and
`archive/`. Agent material is `docs/agent/` (`bugs/`, `facts/`, `reports/`, `prompts/`, `support/`,
STATE/WORKFLOW/FIX_POLICY).
Prompts: the map is `docs/agent/prompts/README.md`, whose own gate carries the prompt-map duty;
reusable ones live in `prompts/perma/`, and one-offs live at the prompt root until consumed.

**Where things are on this rig** (the owner's Windows machine; Linux/Proton paths differ).
Game install `A:\SteamLibrary\steamapps\common\Project Spark` — the folder is **not** named for the game.
Logs `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-*.log`, newest wins. Saves
`C:\Users\stkot\Saved Games\Surviving Mars Relaunched\<steamid>`; `%APPDATA%\Surviving Mars\<steamid>`
is a decoy, not the play history (`EF-110`).

> **Split out of `SMR-BugFixPack` @ `33d69f5` on 2026-08-12** (chain `split-optins`). Policies,
> engine facts, tooling and doc conventions came with it; declared local fact adaptations and the
> last donor sync live in `tools/sync_from_fixpack.py`. Pre-split records in the fix pack cite
> `Code/Opt_*.lua` paths in THAT repo and the `SMRFixPack` namespace.

⚠️ **Each mod has its own owner's list.** This mod's is `docs/PLAYTEST_CHECKLIST.md` (owner,
2026-09-12; the fix pack's name and rules since 2026-09-17). What binds the fix pack goes on
`B:\Dev\SMR\SMR-BugFixPack\docs\PLAYTEST_CHECKLIST.md`; `docs/README.md` says which classes. Live
playtest runs of this mod's modules go there too, because the owner plays ONE game with BOTH
mods loaded (owner, 2026-09-18).

Hook setup, once per clone: `git config core.hooksPath tools/hooks`. `python tools/doccheck.py
--regen` performs regeneration. Authoring `docs/agent/WORKFLOW.md` · code `docs/agent/FIX_POLICY.md`
· efforts over about two sessions `docs/agent/support/CHAIN_METHOD.md`. `AGENTS.md` is the generated
byte copy of this file for Codex.

The three trust classes are authority, derived fact, and authored claim; their duties are in the
header above.

**`docs/archive/` is hidden from a default `rg`** by a root `.rgignore` — a deliberate boundary, not
a deletion. Search it by naming it: `rg <term> docs/archive/`, or `rg --no-ignore <term>` for both.
`grep -r`, `git grep` and `git log` always see everything. An empty default search is the boundary
working.
