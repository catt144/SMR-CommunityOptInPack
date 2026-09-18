---
name: smr-orientation
description: Orient at the start of a session in the Relaunched Fix Pack Opt-In Modules repo — where the mod stands, where things live, the two bans, how to search the archive on purpose, and which numbers must be emitted rather than typed. Use when starting work here, picking up a handoff, or before quoting a count, build id, or status.
---

# Orientation — Relaunched Fix Pack: Opt-In Modules

An **opt-in behaviour mod** for *Surviving Mars: Relaunched*: a small set of modules that change
how the game plays, each **off (or at its base setting) until the player turns it on** in Options →
Mod Options. Three were RETIRED 2026-09-17 (owner); live counts come from doccheck. Patched at
runtime; no game files are modified. A **TRUE STANDALONE** — it works beside the Relaunched Fix
Pack and identically without it. ⛔ **NOT PUBLISHED.**

## 1 · The two bans

The canonical duties are in `CLAUDE.md`'s `Must_Read_Header`. The persisted-name inventory is
`docs/agent/FIX_POLICY.md` §3. Surviving `SMRFixPack` tokens in `Code/` are inventory strings, not
executable references; that distinction is the reason both bans coexist.

**MODULE FREEZE status:** the kernel rule applies. Drones were unfrozen 2026-08-31, and the
2026-09-17 ruling lifted it for `D06`/`D07`/`D12` only — all three are now RETIRED, so `D09` is the
only live unfrozen module.

## 2 · Where the project stands

- **`docs/agent/STATE.md`** — kernel status plus pointers, byte-capped. Read it when status IS the
  question, or when a task, a prompt or the owner calls for it. Its gates and holds bind you.
- **`docs/DECISIONS_OWED.md`** — this mod's own owner-decision list. Read it before asking the
  owner anything. ⚠️ Most of it was written before the game shipped 1.1.0; re-read citations.
- Count source: `python tools/doccheck.py --emit-counts`.
- Installed-build and fact-group source: `python tools/doccheck.py --emit-fingerprint`, backed by
  the Steam `.acf`.

## 3 · Where things live

`docs/README.md` is the map and `doccheck` enforces it — the root list is an allowlist checked in
both directions, so a new file at `docs/` root is a red build until the map names it too.

| | |
|---|---|
| module · defect truth | `docs/agent/bugs/` — one file per entry, **generated** `INDEX.md` |
| engine behaviour | `docs/agent/facts/` — `EF-NNN`, **generated** `INDEX.md` |
| process · code rules | `docs/agent/WORKFLOW.md` · `docs/agent/FIX_POLICY.md` |
| cross-repo drift | `tools/sync_from_fixpack.py` — declared adaptations and last donor sync |
| prompts | `docs/agent/prompts/` — `WORK_PROMPT.md` starts ordinary work; the map routes the rest |
| owner decisions | `docs/DECISIONS_OWED.md` (this mod's) |

A `GENERATED` banner on line 1 identifies an output governed by the kernel's generated-source rule.
Doccheck is RED if one drifts. `AGENTS.md` is the Codex byte copy of `CLAUDE.md`.

⚠️ **The human playtest file lives in the FIX PACK repo.** `docs/PLAYTEST_CHECKLIST.md` is
single-sourced in `C:\Dev\SMR-BugFixPack\docs\` because the owner plays ONE game with BOTH mods
loaded. `docs/README.md` says why. A decision that binds the FIX PACK still goes to its checklist;
a decision about THIS mod goes to `docs/DECISIONS_OWED.md`.

⛔ `docs/PLAYTEST_HELP.md` **no longer exists** — dissolved in the fix pack 2026-09-15 (`c91310f`),
its content consumed there. Records written before then cite it as live; read it out of git
(`git show c91310f^:docs/PLAYTEST_HELP.md`) rather than expecting a file.

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

`EF-` ids are allocated by the fix pack. The filing procedure lives in `smr-bug-library`.

## 6 · Harness, peers, commits

`CLAUDE.md` is the edited entry file; `AGENTS.md` is its generated Codex copy. The shared-tree,
commit and documentation-check duties are canonical in its header. The hook setup is
`git config core.hooksPath tools/hooks` once per clone.

⚠️ **CHEATS ENABLED** on the rig and **BOTH MODS LOADED** is the standing config (owner rule,
`docs/agent/WORKFLOW.md`). Grep logs with the FULL token `[CommunityOptInPack]`.
