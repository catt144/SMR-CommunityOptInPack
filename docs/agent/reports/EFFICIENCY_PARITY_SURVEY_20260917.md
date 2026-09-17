# Efficiency parity with the fix pack — survey, 2026-09-17

**Status: PARTIAL. The measurements below are taken and reusable; the central question is
UNANSWERED and the analysis that would answer it was stopped mid-run by the owner.**

Written at HEAD `0c52767`, after the day's harness port (`PROVENANCE.md` §8). The owner asked what
it would cost to bring this repo to the documentation efficiency the fix pack reached in the
fortnight after 2026-09-01 — "the rules structure, the minimal, what does an agent need to know".

⚠️ **Every figure here is a measurement of a moving tree.** Re-run the commands before quoting any
of it; the fix pack was committing the same day this was taken.

## 1 · The gap, measured

Fix pack at its HEAD `e6ec192`; this repo at `0c52767`.

| | fix pack | here | ratio |
|---|---|---|---|
| `docs/agent/STATE.md` | **745 B** / 15 lines | 9,002 B / 99 lines | 12.1× |
| `docs/agent/WORKFLOW.md` | 18,187 B / 287 lines | **76,915 B / 1,207 lines** | 4.2× |
| `docs/agent/FIX_POLICY.md` | 28,719 B / 400 lines | 45,752 B / 707 lines | 1.6× |
| `CLAUDE.md` | 3,916 B | 6,034 B | 1.5× |
| repo-side push set | 4,872 B | 15,036 B | 3.1× |
| named doccheck gates | 32 | 16 | 2× |

⚠️ **Method, because the two available ones disagree.** Every byte figure above is **LF-normalised**
(`len(open(p,'rb').read().replace(b"\r\n",b"\n"))`) — the same measure `doccheck`'s `lf_bytes` uses,
so these numbers match its PUSH SET line. A plain `wc -c` on this repo counts CRLF and reads ~1%
higher (`CLAUDE.md` 6,113, `STATE.md` 9,101); do not mix the two. Line counts are `wc -l`. Gates via
`grep -oE '"[A-Z][A-Z ]+:' tools/doccheck.py | sort -u`. The donor's own PUSH SET line reads
19,841 B because it includes a 14,969 B `MEMORY.md` from outside its repo; the row above is
repo-side on both sides, since this repo has no memory file.

⭐ **The comparison is not confounded by subject matter: the fix pack is the BIGGER project** —
roughly 187 defect entries and ~46 shipping modules against this repo's 9 entries and 5 modules. It
covers strictly more ground in a quarter of the bytes.

## 2 · The four mechanisms that produce it

Read off the donor's `tools/doccheck.py` and its `docs/agent/STATE.md` on 2026-09-17.

**(a) STATE is PULL, with a gate in front of it.** The donor's STATE is 15 lines and has **no
gates-and-holds section at all**: current version, previous version, `Owner OWES: none.`,
`STILL OPEN: none.` Its four-test admission door (harm · reach · gate · volatility, AND-ed) is
already ported here into `prompts/perma/STATE_EVICTION.md`; what is NOT ported is
`check_state_admission` (donor `doccheck.py:1551`, ~30 lines plus a `state_added_lines()` git-diff
helper), which on any commit that adds a STATE line **prints the added lines beside the four
questions**. Its own docstring is the design: *"This gate CANNOT judge a line… It makes the
judgement unavoidable at the moment of the write… A PASS here is not approval."* Paired with the
donor's owner ruling (2026-09-15) that **opening a session is not a call for status**, so sessions
stop paying for STATE at boot.

**(b) The rules-header model.** Every binding duty is one canonical `Rule:` line inside exactly one
`## Must_Read_Header` / `<!-- RULES -->` block. Donor constants at `doccheck.py:138-162`; checks
`check_rule_headers` and the placement scan at ~`:2253-2390` (~190 lines together). It REDs on:
a duplicate duty **anywhere in the repo** (normalised, case-folded), a `Rule:` line in `STATE.md`,
a `Rule:` line on a generated or archived surface, and malformed style (bold, emoji, or the words
MUST / NEVER / ALWAYS). Header byte caps are 1,024 warn / 2,048 hard for doc-local headers and
2,560 / 3,072 for the `CLAUDE.md` kernel — the kernel got its own cap after one shared cap forced
correct rules to be compressed and the compression broke four of them (donor `396d7f2`).

**(c) Gates replacing prose** — 32 named checks against this repo's 16. A duty a machine catches is
cited, not restated. Gate 3 of the admission door is exactly this rule.

**(d) Skills as pull-loaded knowledge** — already ported here (`PROVENANCE.md` §8).

## 3 · ⛔ The correction that changes the estimate

**The rules structure is a deduplication-and-authority mechanism, not the size lever.** The donor's
own census artifact — `docs/agent/reports/RULES_HEADERS_INVENTORY.json`, 829 KB — classified **852
rule-shaped sentences**:

```
global: 16    doc-local: 30    redundant: 20    dead: 6    task-local: 780
```

**780 of 852 stayed as prose in their task documents.** Its `WORKFLOW.md` contributed 123
task-local against only 10 global; its `FIX_POLICY.md` contributed 100 task-local and 1 doc-local.
So promoting rules did NOT take that `WORKFLOW.md` from large to 18 KB.

⇒ **What did is UNKNOWN and is the open question.** Do not build an estimate on the rules migration
alone; a plan that assumes it is the shrink lever will underestimate the prose work and overestimate
what the tooling buys.

## 4 · This repo's scale

A proxy count of rule-shaped lines (`grep -cE '⛔|⚠️|\bMUST\b|\bNEVER\b|\bALWAYS\b|^\s*[-*] \*\*[A-Z]'`)
over `CLAUDE.md`, `docs/README.md`, `STATE.md`, `WORKFLOW.md`, `FIX_POLICY.md` and
`prompts/perma/*.md`:

| file | lines |
|---|---|
| `docs/agent/WORKFLOW.md` | 97 |
| `docs/agent/FIX_POLICY.md` | 38 |
| `docs/agent/STATE.md` | 23 |
| `prompts/perma/DISPATCH.md` | 19 |
| `prompts/perma/WORK_PROMPT.md` | 14 |
| `prompts/perma/KNOWLEDGE_SYNC_PASS.md` | 9 |
| `docs/README.md` | 7 |
| `CLAUDE.md` | 6 |
| `prompts/perma/STATE_EVICTION.md` | 2 |
| **total** | **215** |

⚠️ **A proxy, not a census.** It counts emphasis markup, so it over-counts warnings that state no
duty and under-counts duties written in plain prose. It is a sizing aid only: ~215 against the
donor's 852 over a larger doc set is the right order for the project's size.

## 5 · ⛔ THE OPEN QUESTION — what is in this repo's extra ~76 KB?

`WORKFLOW.md` is 4.2× the donor's and `FIX_POLICY.md` 1.6×, on a smaller project. **Nobody has
looked at what that content actually is.** An `Explore` agent was dispatched on exactly this and
**STOPPED BY THE OWNER before it reported** — no partial result survives, and nothing in this repo
was changed by it.

The brief it was given, worth reusing verbatim: read both of the donor's documents in full and work
out the *shape* that keeps them small (section structure, what a rule looks like, what they refuse
to hold, where the detail went instead — `docs/agent/support/`, entries, facts, reports, or a gate
that replaced prose); classify this repo's two equivalents against that shape; and read
`git log --oneline -- docs/agent/WORKFLOW.md docs/agent/FIX_POLICY.md` in the donor from 2026-09-01
onward, whose commit messages are unusually descriptive and should name the method.

Expected buckets, to be confirmed or corrected with byte counts and named examples: narrative and
history belonging in an entry, `archive/SESSION_LOG.md` or a report; duties duplicated across the
two files or with `CLAUDE.md`; rationale a gate now enforces mechanically; content about the three
modules retired 2026-09-17; and genuinely load-bearing rules with no other home.

⛔ **What a naive shrink would destroy.** This repo's versions carry things the donor's do not:
the two bans (persisted names are save contract; zero `SMRFixPack` references in executable code),
`FIX_POLICY` §4 **inverted** for a mod whose product IS opinionated modules with the donor's §4 kept
verbatim as §4-donor, the §5 dial addendum for D09, and the both-configuration ship test. Any plan
must name these as protected before it cuts.

## 6 · Cost, as far as it can honestly be given

**Tooling — cheap, mechanical, low risk.** Porting `check_state_admission` (~40 lines with its
helper) and the rules-header pair (~190 lines) is about one session; four gates were ported this way
on 2026-09-17 without incident. The donor's checklist-shaped gates (`WAITING`, `STILL OPEN`,
`CHECKLIST` 30-day staleness) need adapting from its `PLAYTEST_CHECKLIST.md` to this repo's
`DECISIONS_OWED.md` — call it a second session.

**Census — the irreducible part, and it is the owner's.** The donor's gate says why in its own
docstring: *"An untagged sentence cannot be classified reliably by syntax, so this check
deliberately does not pretend to find one. The one-time census and owner adjudication supply that
semantic half."* Classifying ~215 sentences into global / doc-local / redundant / dead / task-local
is judgement, and **`redundant` and `dead` are owner rulings** — that is what the donor's
`[A3: pass]` tags record. ⛔ Those tags were deliberately NOT copied into this repo's `CLAUDE.md`
(`PROVENANCE.md` §8): that audit ran on the donor's text, not ours.

**Prose — NOT ESTIMABLE until §5 is answered.** Whether it is two sessions or six depends entirely
on the bucket split.

## 7 · One cheap win, available independently of all of it

This repo's `STATE.md` still titles itself *"the one mandatory read"* — the pre-overhaul framing.
The donor's reads *"pull; read it when a task, a prompt or the owner calls for status"*. Flipping
it is a one-line change plus an owner ruling, and STATE is the single largest per-session cost in
the repo (9,002 B of a 15,036 B push set). ✅ **The ask is FILED as `DECISIONS_OWED.md` OI-08**,
carrying the caveat that matters: this repo's STATE still holds live 1.1.0 holds the fix pack's
holds nowhere, so flipping the title without routing them would hide live holds rather than move
them. OI-08 recommends porting `check_state_admission` and running one eviction under the door
first.

## 8 · What this report does NOT claim

No claim about what the donor's shrink method was (§5). No claim that the rules migration would
shrink this repo's documents (§3 says the donor's own numbers argue it would not). No claim that
~215 is a census (§4). No byte figure for what is evictable here. Nothing here was measured in a
running game, and nothing here is a behaviour claim about any module.
