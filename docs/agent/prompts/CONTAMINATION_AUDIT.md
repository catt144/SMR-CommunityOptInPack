# CONTAMINATION_AUDIT — one-off: is this repo clear of fix-pack contamination, and does everything in it have a place here?

**One-off. Deletes itself in its close-out commit** (`git rm` this file). Any
model; the owner picks. **Start with `git log --oneline -10` + `git pull`.**
Staleness anchor: written 2026-08-31 at `ac47380`, the evening a second session
found the ported tools still speaking about the other mod — this audit is the
systematic version of that catch, over the whole repo.

**Why.** This repo was split out of `SMR-BugFixPack` on 2026-08-12 and has taken
two ports from it since (`agent/PROVENANCE.md` §1, §6). Every port carried some
of the donor's words along. Some of that is CONTRACT (save-contract strings),
some is HISTORY (records that must not be edited), some is a legitimate POINTER
(the owner's checklist lives there), and some is CONTAMINATION — instructions,
logic or player text that are about the other mod. This audit sorts every hit
into exactly one of those classes, fixes what may be fixed in a doc/tool pass,
and hands the rest to the owner as a list. It also asks the inverse question:
what is in this repo with no recorded reason to be here.

> ⛔ No behaviour change to any module. No edit to any persisted string. No edit
> to any archived record. Deletions are PROPOSED to the owner, never performed
> here (the only file this session deletes is itself).

## 0 · Orient and set up

1. `git log --oneline -10` + `git pull`. Read `docs/agent/STATE.md` whole.
2. Read path (file granularity): `CLAUDE.md` (the two bans — they define the
   contract class), `agent/PROVENANCE.md` §1 §2 §5 §6 (what came from where and
   what was deliberately kept), `docs/README.md` ("the two playtest files live in
   the fix pack", "where new things go"), `agent/WORKFLOW.md` "Layout" and the
   ADAPTED banner over "Release steps", `agent/FIX_POLICY.md` §3 (the prefix
   note) and §4-donor, `tools/doccheck.py` docstring (v4/v5 notes), `metadata.lua`,
   `items.lua`. Scan `agent/bugs/INDEX.md` and `agent/facts/INDEX.md`.
3. **Create the todo list before starting** — one item per pass and per commit
   below, one in progress at a time, marked the moment each completes.
4. Stale-probe gate: **N/A — this audit launches nothing and records no test.**
   If that changes, `WORKFLOW.md` "Probe hygiene" binds first.

## 1 · The classes — every hit lands in exactly one

| class | what it is | action |
|---|---|---|
| **CONTRACT** | the five persisted names `SMRFixPack_ack_notworking`, `_closed_to_new_residents`, `_no_homeless`, `_DroneSpeedDial`, `_DroneCarryDial` and the option/choice strings of PROVENANCE §2 rows 6–9, wherever they occur | ⛔ untouchable; count them, confirm each occurrence is in §2, and that no persisted-looking name exists outside §2 |
| **HISTORY** | `docs/archive/`, `agent/PROVENANCE.md`, SESSION_LOG, dated notes inside entries/facts/policies that say what happened, donor citations inside tool comments that describe the tool's own origin, commit messages | never edited; recorded as history in the report |
| **POINTER** | a live instruction that deliberately points at the fix pack: the owner's `PLAYTEST_CHECKLIST.md`/`PLAYTEST_HELP.md` (single-sourced there), the shared TestKit, `EF-` id allocation, `DRONE_PROJECT_PROMPT.md`, `PARKED_OPTIN_REFERENCES.md`, `GENERAL_USE_PROMPT.md`, the FIX_POLICY/WORKFLOW donor blocks that carry an explicit ADAPTED / N/A-here marker, "works with or without the Relaunched Fix Pack" in player text | legitimate; list them so the next audit does not re-derive them |
| **STALE** | a live instruction, tool comment, docstring, label or default that was true in the fix pack and is wrong or meaningless here, AND is not marked N/A/ADAPTED — e.g. a rule citing a fix-pack-only mechanism as if it were this mod's, a tool printing "fix pack", a default path or module name from the other tree, a count that is the other repo's | fix in this session (docs/tools only) or add the missing N/A marker; every fix cited in the report |
| **CONTAMINATION** | executable code referencing `SMRFixPack`/`[CommunityFixPack]`/`SMR_CommunityFixPack`/a `Fix_*` file other than as a CONTRACT string or a comment; player-facing text naming the other mod as if it were this one; tool LOGIC keyed to the other mod's namespace or files; a live doc instructing a session to act on the fix pack's tree from here | ⛔ code/player-text hits: STOP and report (§5); tool/doc hits: fix and cite |

## 2 · Pass A — the contamination sweep

Run the inventory and paste it into the report VERBATIM (counts per file, per
token). Tokens, at minimum:

```
grep -rn --include=*.lua --include=*.py --include=*.md --include=*.json -E \
  "SMRFixPack|CommunityFixPack|SMR_CommunityFixPack|SMR-BugFixPack|SMR-CommunityFixPack|[Ff]ix[ -][Pp]ack|\bFix_[A-Z]|\bF[0-9]{2,3}\b|\bC[0-9]{2}\b|the pack\b|76 files|75 modules|80 modules" \
  Code/ tools/ docs/ metadata.lua items.lua README.md CLAUDE.md LICENSE .claude/ \
  | grep -v "^docs/archive/"
```

Then, per surface, classify EVERY hit (a hit not in the table is an audit gap):

1. **`Code/`** — expected: the five CONTRACT strings (5 definitions + their
   comments), nothing else. Verify ban 2 mechanically: every `SMRFixPack` token
   is inside a string literal or a comment; `luaparser` can prove it (walk the
   AST for Name/Index nodes containing `SMRFixPack` — there must be none).
2. **`metadata.lua` / `items.lua`** — CONTRACT (rows 6–9) plus the deliberate
   "works with or without the Relaunched Fix Pack" sentences (POINTER). Anything
   else naming the other mod is CONTAMINATION.
3. **`tools/`** — for each file: provenance line = HISTORY; a comment describing
   the donor defect that motivated a check = HISTORY; a docstring, printed label,
   usage line, default path, module list or regex that is the other mod's =
   STALE (fix) or CONTAMINATION (fix). ⚠️ `doccheck.py`, `split_bugs.py`,
   `split_facts.py` carry N/A-marked migration halves on purpose (PROVENANCE §1)
   — confirm the marker is present and accurate, do not remove the code.
4. **`docs/agent/WORKFLOW.md`, `FIX_POLICY.md`, `README.md`, `STATE.md`,
   `prompts/`** — the live instructions. Read every hit in context and ask:
   *would a session following this line do something that belongs to the other
   mod?* Yes → STALE or CONTAMINATION, fix. No, and marked → POINTER. No, and
   unmarked donor prose → add the marker (ADAPTED / N/A here / fix-pack history).
5. **`docs/agent/bugs/`, `facts/`, `reports/`, `FUTURE_IDEAS.md`** — records.
   F-ids, C-ids and fix-pack module names inside a D-entry's narrative are
   HISTORY. A REPORT that is the other mod's evidence rather than this mod's is a
   Pass-B candidate, not a contamination fix. Facts describe the game and are
   shared by design (`docs/README.md`) — a fact is never contamination; a fact
   whose only content is a fix-pack module's behaviour is a Pass-B candidate.
6. **Player-visible strings** — `metadata.lua` title/description/last_changes,
   `00_Core.lua`'s dialog, the two rollover titles, every `Untranslated(`/`T(`
   site (`tools/l4_player_surfaces.py` lists them): each must name THIS mod or
   no mod. Cross-check `l4`'s count against your own grep.

## 3 · Pass B — does everything here have a place?

Walk the tree (`git ls-files`) and, for every file or self-contained block that
did not originate in this repo's own work, answer *why is this here* from the
records:

| verdict | meaning |
|---|---|
| **BELONGS** | serves this mod's purpose (opt-in behaviour modules, their records, the process that builds and ships them) — cite the use |
| **KEPT-N/A** | deliberately kept though not applicable, WITH a marker saying so (PROVENANCE §1/§6, a docstring, a banner) — confirm the marker exists and is still true |
| **ORPHAN** | no recorded reason to be here, or the recorded reason has lapsed |
| **OWNER** | belongs only if the owner says so (a parked idea whose routing here is an owner ruling counts as BELONGS — cite the ruling; one with no ruling is OWNER) |

Ask it at least of: every `tools/*.py` (e.g. `audit_preset_fields.py` found 0
preset-field writes here; `pack_list.py`/`flpk_extract.py` need a built `.fpk`;
`blocking_analysis.py` is cited by D06's F86 record); `00_Core.lua`'s `DataPatch`
runner (no `Opt_*` module calls it — PROVENANCE §5 calls the machinery "dormant,
not wrong": is that still the recorded position?); FIX_POLICY §4-donor and the
donor "Release steps" block; every `agent/reports/*.md`; every `FUTURE_IDEAS.md`
entry (each carries a routing ruling — #9 is titled "for the FIX PACK": find the
ruling that parked it here or mark it OWNER); every fact whose summary names a
fix-pack module; `.claude/settings.json`'s allowances; `README.md` (mod-facing)
and `LICENSE`.

⛔ **ORPHANs are proposed, not removed.** The report lists each with a proposed
disposition (delete / move to the fix pack / write the reason and keep) and the
owner decides — one checklist line per orphan, or one line for the whole list
if they are alike.

## 4 · Deliverables — in this order, each its own todo item

1. `docs/agent/reports/CONTAMINATION_AUDIT_<YYYYMMDD>.md`: the verbatim
   inventory; a table with one row per hit or per hit-group (file, line(s),
   token, class, action taken or proposed); the Pass-B table; the counts per
   class; the allowlist of POINTERs for the next audit. Provenance words per row
   (MEASURED for grep/AST results, SOURCE for a record you read, INFERRED for a
   judgment) — never a blanket claim over a table.
2. The STALE/CONTAMINATION fixes in docs and tools, each cited in the report.
   Parse-sweep any `.py` you touch by running it; `python tools/doccheck.py`
   GREEN.
3. Owner items on the fix pack's `docs/PLAYTEST_CHECKLIST.md` → "Decisions
   waiting on you" (one line + pointer each), and their numbers on `STATE.md`'s
   open-decisions line. `STATE.md` otherwise only if the kernel changed (byte
   caps; evict, don't compress).
4. A `docs/archive/SESSION_LOG.md` entry (newest first, `tags:` line) with the
   class counts and the report's path.
5. Close-out commit: report + fixes + `git rm docs/agent/prompts/CONTAMINATION_AUDIT.md`,
   `git commit -F <file>` (subject names the class counts, e.g.
   "audit: 0 contamination, 7 stale fixed, 3 orphans to owner"), push. Name the
   grave in the summary: `git show <sha>:docs/agent/prompts/CONTAMINATION_AUDIT.md`.

## 5 · Stop conditions — permission to report instead of pushing on

- A `SMRFixPack` reference in EXECUTABLE position (not a string, not a comment)
  — ban 2 is breached and the standalone claim is false. Record it with
  file:line and the AST evidence, do not edit the code, put it first in the
  report and on the checklist, and stop the code half of the audit there.
- A persisted-looking name (`SMRFixPack_*` / `SMROptInPack_*` written onto an
  object, a GameVar, a modifier id) not in PROVENANCE §2 — record, do not edit,
  owner.
- Player-facing text that names the other mod as if it were this one — the
  wording is the owner's (`WORK_PROMPT.md` §2); propose the corrected string,
  do not apply it.
- A fix that would need a module edit, a persisted-string edit, or a change to
  an archived record — propose it, do not make it.
- The inventory is larger than one context can classify honestly — split by
  surface, commit the report partial with a "NOT YET CLASSIFIED" section, and
  say so; an unclassified hit is never silently dropped.

## 6 · What may NOT be claimed

- "Clean" or "zero references" — the true statement is *N hits, all classified,
  0 CONTAMINATION, k STALE fixed, m POINTERs allowlisted*, with the table.
- Anything about the fix pack repo's own state — this audit reads it only to
  check that a POINTER resolves.
- That a record is wrong because it names the other mod — records are history.
- That an ORPHAN was removed — nothing is removed here but this prompt.
- A ban-2 verdict from grep alone — the AST walk is the evidence; grep is the
  inventory.
