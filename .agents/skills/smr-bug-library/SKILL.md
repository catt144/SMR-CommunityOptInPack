---
name: smr-bug-library
description: Read or file a module record, defect entry or engine fact in the Opt-In Modules repo — the cheapest-first route into docs/agent/bugs/ and docs/agent/facts/, which front-matter fields are load-bearing, and the filing procedure that passes doccheck first time. Use when looking up an entry ID (D/F/C or EF-NNN), checking whether something is known, or recording a new one.
---

# The module/bug library — reading and filing

`docs/agent/bugs/` holds this mod's **module records**, including retired modules and the Mod
Options enable surface. `docs/agent/facts/` holds the engine facts
(`EF-NNN`), mirrored from the fix pack. Both carry a **generated** `INDEX.md`.

⛔ **`EF-` ids are ALLOCATED BY THE FIX PACK** (`docs/agent/WORKFLOW.md`, reading path 2). File a
new fact in `C:\Dev\SMR-BugFixPack` first, then mirror it here at the same id and say so in both.
Minting an `EF-` number in this repo alone is what caused the 2026-08-16 collision.

## 1 · Reading — cheapest first, stop when you have the answer

0. **Ours-or-vanilla check:** `rg -l -F -- <keyword> Code/` searches this mod's runtime code
   first. Hits inspect ours; an empty literal search is a cheap vanilla lead and does **not** rule
   out aliases or indirect effects.
1. **`docs/agent/bugs/INDEX.md`** — small. One row usually answers "is this known, and
   what is its status". Read the row, not the entry.
2. **The entry's own section, by heading.** A narrow question needs only that section. The kernel's
   absence-proof rule governs negative searches.
3. **`docs/agent/facts/INDEX.md`** — grep it for a narrow question. To ask whether a fact still
   holds, use §3 rather than opening the fact at all.

## 2 · Front matter — load-bearing or not

| field | read it? |
|---|---|
| `status` + `status_source` | **yes** — `speced`, `tested-attended`, `cand`, `wontfix`, `parked`… |
| `derived_at:` (facts) | **yes** — the sha or game build it was derived against |
| `seq` / `row` | ordering; `seq` must stay contiguous |
| `updated` / `verified` | dates, not evidence |
| `row_status:` | **no. Read nothing from it.** |

`row_status:` is a frozen copy of the pre-split index row. doccheck reads **only its first word**
and deliberately tolerates that word disagreeing with `status` — a status that has advanced must be
free to leave it behind, so those `warn` lines are expected, not defects.

**Authoring warning:** the splitter emits only its `FRONT_FIELDS`; an invented front-matter key is
silently dropped on render. Put durable context in a supported field or the entry body.

## 3 · Is this fact still true?

`python tools/doccheck.py --emit-fingerprint` groups facts by `derived_at:` and says whether each
still describes what is installed. **HOLDS** needs no re-read — it is a routing aid, not a
verification of the claim's scope. **MOVED** means the citations point into a tree that is not on
disk; re-derive against the archived tree the entry names (`C:\Dev\SMR-SrcArchive\<build>\Src`),
never the live one. A fingerprint reading `(inferred from updated:)` was back-computed from a date,
so it is weaker evidence than a bare one.

⚠️ The game auto-updated to **1.1.0 + DLC on 2026-09-08**. Every fact and module comment written
before then cites a tree that is no longer installed.

## 4 · Filing

No scaffold command exists — copy the shape of a recent same-letter entry.

1. New `docs/agent/bugs/<ID>.md`: `id` matches the filename, `seq` continues without a gap,
   heading tag and `status` agree.
2. State the **control** — what would falsify the claim — not just the story. A cause without a
   control is a plausible story; this project files controls.
3. `python tools/doccheck.py --regen`, then `python tools/doccheck.py` until GREEN. `--regen`
   builds `INDEX.md` from **every entry on disk**, a peer's uncommitted ones included — check
   `git status docs/agent/` first and commit only your own paths.
4. Commit under the kernel's shared-tree and pathspec rules.

## 5 · What you may not do

Never move an entry's status to record your own opinion — a status word is evidence about what was
*tested*, and `tested-attended` means the owner watched it in the game. Never bulk-upgrade a legacy
bare `tested`. "Vanilla fixed it" is a claim: trace the replacement body in the archived tree for
the build you are comparing against before acting on it, because a rename reads as a deletion.

The kernel's MODULE FREEZE rule governs behaviour changes. Recording a finding does not change a
module's behaviour.
