---
name: smr-orientation
description: Orient at the start of a session in the Relaunched Fix Pack Opt-In Modules repo — where the mod stands, where things live, the two bans, how to search the archive on purpose, and which numbers must be emitted rather than typed. Use when starting work here, picking up a handoff, or before quoting a count, build id, or status.
---

# Orientation — Relaunched Fix Pack: Opt-In Modules

An **opt-in behaviour mod** for *Surviving Mars: Relaunched*: a small set of modules that change
how the game plays, each **off (or at its base setting) until the player turns it on** in Options →
Mod Options. ⛔ Never hand-type how many — three were RETIRED 2026-09-17 (owner). Patched at
runtime; no game files are modified. A **TRUE STANDALONE** — it works beside the Relaunched Fix
Pack and identically without it. ⛔ **NOT PUBLISHED.**

## 1 · The two bans, before you touch anything

1. **PERSISTED NAMES ARE SAVE CONTRACT.** Every string that ever entered a savegame keeps its
   EXACT bytes — including the five `SMRFixPack_*` fields and modifier ids this mod still writes.
   Renaming one is FORBIDDEN. Inventory: `docs/agent/PROVENANCE.md` §2.
2. **ZERO `SMRFixPack` references in executable code.** The framework is this mod's own copy under
   `SMROptInPack`. The surviving tokens in `Code/` are the persisted STRINGS of ban 1 — data, not
   references. That distinction is the whole rule.

⛔ **MODULE FREEZE:** no behaviour change to any module without an owner ruling. Drones were unfrozen
2026-08-31, and the 2026-09-17 ruling lifted it for `D06`/`D07`/`D12` only — all three are now
RETIRED, so `D09` is the only live drone module; everything else is still frozen.

## 2 · Where the project stands

- **`docs/agent/STATE.md`** — kernel status plus pointers, byte-capped. Read it when status IS the
  question, or when a task, a prompt or the owner calls for it. Its gates and holds bind you.
- **`docs/DECISIONS_OWED.md`** — this mod's own owner-decision list. Read it before asking the
  owner anything. ⚠️ Most of it was written before the game shipped 1.1.0; re-read citations.
- **Never hand-type a count.** `python tools/doccheck.py --emit-counts` prints them.
- **Never hand-type the game build.** `python tools/doccheck.py --emit-fingerprint` reads the
  installed build from the Steam `.acf` and says which fact groups still describe what is on disk.

## 3 · Where things live

`docs/README.md` is the map and `doccheck` enforces it — the root list is an allowlist checked in
both directions, so a new file at `docs/` root is a red build until the map names it too.

| | |
|---|---|
| module · defect truth | `docs/agent/bugs/` — one file per entry, **generated** `INDEX.md` |
| engine behaviour | `docs/agent/facts/` — `EF-NNN`, **generated** `INDEX.md` |
| process · code rules | `docs/agent/WORKFLOW.md` · `docs/agent/FIX_POLICY.md` |
| what came from where | `docs/agent/PROVENANCE.md` — the port ledger |
| prompts | `docs/agent/prompts/` — `WORK_PROMPT.md` starts any work; one-offs delete themselves |
| owner decisions | `docs/DECISIONS_OWED.md` (this mod's) |

A `GENERATED` banner on line 1 means **edit the source, never the file**. doccheck is RED if a
generated file drifted. `AGENTS.md` is a byte copy of `CLAUDE.md` for Codex — never edit it.

⚠️ **The two human playtest files live in the FIX PACK repo.** `docs/PLAYTEST_CHECKLIST.md` and
`docs/PLAYTEST_HELP.md` are single-sourced in `C:\Dev\SMR-BugFixPack\docs\` because the owner plays
ONE game with BOTH mods loaded. `docs/README.md` says why. A decision that binds the FIX PACK still
goes to its checklist; a decision about THIS mod goes to `docs/DECISIONS_OWED.md`.

## 4 · The archive boundary

`docs/archive/` is append-only history, kept **out of a default ripgrep** by a root `.rgignore` so
ordinary searches return only live hits. A boundary, not a deletion — search it on purpose when
*"we may already have learned this in an archived report"*:

```
rg <term> docs/archive/     the archive alone — naming the path defeats the filter
rg --no-ignore <term>       live + archive in one pass
```

`grep -r`, `git grep` and `git log` ignore `.rgignore` entirely. A default search coming back empty
is the boundary working, not a missing file.

## 5 · Before trusting a line citation

⚠️ **The game auto-updated to 1.1.0 + DLC on 2026-09-08 and overwrote `ModTools\Src`.** Facts and
module comments written before then cite line numbers in a tree that is no longer on disk. Both
trees are archived: `C:\Dev\SMR-SrcArchive\1.0.7.396349\Src` and `…\1.1.0.403908\Src` (`EF-083`).
`--emit-fingerprint` says which `derived_at:` groups HOLD and which MOVED; re-derive only what
moved, against the tree the entry names.

⛔ **`EF-` ids are ALLOCATED BY THE FIX PACK.** File a new fact there first, mirror it here at the
same id, and say so in both. Never mint an `EF-` number in this repo alone.

## 6 · Harness, peers, commits

`CLAUDE.md` is the edited entry file; `AGENTS.md` is its byte copy for Codex. Both vendors work
this tree, sometimes at once: re-check `git log` and `git status` before a shared write, and
identify a peer's work by sha and diff, never by author (there is one git identity). Stage exact
paths and commit with a pathspec — `git commit -F <msgfile> -- <paths>` — never `-a`, never a bare
`-m` (PowerShell 5.1 splits `-m` on embedded quotes). doccheck must be GREEN; a hook enforces it
(`git config core.hooksPath tools/hooks`, once per clone).

⚠️ **CHEATS ENABLED** on the rig and **BOTH MODS LOADED** is the standing config (owner rule,
`docs/agent/WORKFLOW.md`). Grep logs with the FULL token `[CommunityOptInPack]`.
