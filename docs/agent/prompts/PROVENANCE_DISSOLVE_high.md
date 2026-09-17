# Dissolve `docs/agent/PROVENANCE.md` — rehome what is live, script what is mechanical, delete the rest

**Authored 2026-09-17 at `1ae0d85`.** Staleness check before trusting a figure below:

```sh
git log --oneline -5 && git pull
git diff --stat 1ae0d85..HEAD -- docs/agent/PROVENANCE.md docs/agent/facts/ tools/ items.lua metadata.lua
```

Empty diff ⇒ every measurement here holds. Non-empty ⇒ re-run the two commands in §2 first.

---

## 1 · Authority — settled, do not re-argue

⚖️ **Owner, 2026-09-17, verbatim:** *"I would honestly like it to just go away. If it has usual
info find a home for the useful parts, if it syncs facts, engine info or other stuff we need from
the main pack while can't that just be a script on a cron job?"*

⚖️ **OI-09 (`docs/DECISIONS_OWED.md`):** agent-facing documents may be machine-tuned hard; content
already recorded elsewhere is **DELETED, not re-archived**. Retire silently. `PROVENANCE.md` is
agent-facing.

⛔ **The file is going away. That is decided.** What is open is only *where each live piece lands*
and *what the sync tool checks* — both yours to decide as you go, recorded in the commit message.

⛔ **MODULE FREEZE is not in play** — but see stop 1: two SHIPPING files cite this document.

---

## 2 · The measurement that makes this small

**Run both before you start; they are the premise of the whole job.**

```sh
diff -rq docs/agent/facts C:\Dev\SMR-BugFixPack\docs\agent\facts    # expect exactly 3
python .claude/baseline.py | grep PROVENANCE
```

On 2026-09-17 the first printed **3 differing files out of 107+**, and all three are the
already-declared local adaptations:

| file | why it differs | is that deliberate? |
|---|---|---|
| `EF-062.md` | its `FUTURE_IDEAS` pointer is adapted to this repo | ✅ yes, the only content adaptation |
| `INDEX.md` | GENERATED here from local front matter | ✅ yes, by construction |
| `_preamble.md` | carries this repo's dated copy note | ✅ yes |

⭐ **This is the finding the job rests on.** The port ledger — §1 and §5–§9, **15,599 B, 53% of the
file** — exists to answer one question: *is a re-sync from the fix pack a straight overwrite, or
would it destroy a local adaptation?* The answer is **three declared exceptions**. Fifteen kilobytes
of dated narrative describing what a constant can state in three lines and a command can verify.

It also grows about 5 KB per port, forever. Four ports so far.

---

## 3 · Where the live content goes

Section sizes measured 2026-09-17. **Everything not listed here is deleted, not archived.**

| section | B | disposition |
|---|---|---|
| **§2** persisted-name inventory | 6,543 | ⛔ **`docs/agent/support/SAVE_CONTRACT.md`.** Highest-stakes move in the job — see stop 1 |
| **§6** the tooling ledger | 3,988 | → `tools/README.md` (exists since `4eaf9ae`; its prose is hand-authored, its rows generated). **Repoint the ~10 script headers that cite `PROVENANCE §6`** — they are why `tools/README.md` echoes that string ten times |
| **§4** how to run the suite | 1,503 | → `docs/agent/support/` or WORKFLOW's testing section. Your call. It is the only home for `SMRTest.OptStatus`/`OptMissing`/`FromOptInPack`, the SKIP-not-FAIL rule, the two gate lines and the full-token grep rule |
| §1, §5, §7, §8, §9 | 15,599 | the port ledger → **§4 of this brief** (a tool + a gate), then DELETE |
| **§3** display-name sweep | 1,617 | DELETE. Settled 2026-08-13, the strings were swept the same day and no longer exist, one of them in `Opt_NoHomeless.lua` which was deleted 2026-09-17. It also carries a `~~strikethrough~~` tombstone of exactly the kind this repo bans elsewhere |

⛔ **`support/` not `reports/`** — reports are explicitly not authority (`WORK_PROMPT.md` §5) and
save contract is. The test is in `docs/README.md` "Where new things go".

---

## 4 · The sync tool — and why a GATE beats a cron

✅ **ALREADY BUILT, 2026-09-17 — `tools/sync_from_fixpack.py`.** You do not have to write it.
It is read-only in both repos, and it carries the ledger as declared constants:

- `LOCAL_ADAPTATIONS` — the three files the fact mirror is ALLOWED to differ in. **This is what
  §1 and §5–§9 of `PROVENANCE.md` reduced to once measured.** A row is a promise the difference is
  deliberate; anything differing that is not listed is the finding.
- `LAST_SYNC` — the donor sha this repo last synced from. Move it when a sync completes, in the
  same commit.
- `DONOR_OWNED_FILES` / `DONOR_ID` — WORKFLOW banner clause 6 as data, so donor-owned names are
  counted rather than reported as breakage.

Three passes: `--facts` (mirror drift vs the declared adaptations), `--donor-log` (what changed on
a shared surface since `LAST_SYNC`), `--citations` (does this repo hold what it cites). It never
writes, stages or copies: applying a change is a human act with a commit message, because "does
this subject apply to us" is judgement.

⛔ **What is still owed on the tool.** It has **no falsifier**, and this repo's own rule is that a
gate only ever seen passing has not been tested (`tools/README.md`; `rule_headers_selftest.py` is
the worked example). If you wire it into doccheck, write `tools/sync_from_fixpack_selftest.py`
first — planted unexpected drift must fire, planted declared drift must stay silent, with a
negative control. While it stays owner-fired rather than gated, that is a recommendation, not a
blocker.

**On the cron question, answered rather than deflected.** The owner's shape — a prompt they fire
after changing the main pack, calling this helper — is right, and better than a gate:

- it runs **when the owner knows something changed**, which is the only moment the interesting
  half ("did the fix pack learn something we need?") is answerable at all;
- that half is **judgement and cannot be scripted** — the helper finds candidates, the session
  decides. A gate can only ever do the mechanical part;
- a cron that **auto-applies** would overwrite authority files unattended: landing a donor change
  into a dirty tree mid-session, or silently reverting a local adaptation someone meant to keep.
  Facts are truth here. ⛔ Do not build that.
- a doccheck gate on `--facts --strict` is still available later and costs nothing, but it needs
  the falsifier above first.

⚠️ `prompts/perma/KNOWLEDGE_SYNC_PASS.md` already does a *manual* cross-repo sweep and is broader
than this tool (it checks dangling citations, not just fact drift). **Do not delete or rewrite it.**
Add one line pointing at the new tool for the part now mechanical.

---

## 5 · The citation surface — 39 files, and two of them ship

`grep -rlE 'PROVENANCE' --include='*.md' --include='*.py' --include='*.lua' .` (excluding
`docs/archive/`) returned **39 files** on 2026-09-17. Every one must resolve when you are done.

⛔ **The two that ship, both citing §2 as save/account-contract authority:**

- `items.lua:32` — *"THESE NINE OPTION NAMES AND EVERY CHOICE STRING ARE ACCOUNT/SAVE CONTRACT and
  keep their exact bytes (docs/agent/PROVENANCE.md §2)"*
- `metadata.lua:67` — *"ALL NINE KEYS AND VALUES ARE LIFTED FROM THE FIX PACK BYTE-FOR-BYTE
  (docs/agent/PROVENANCE.md §2, rows 6-9)"*

`metadata.lua:4` and `:18` also cite §3 and the file generally.

⚠️ **`docs/agent/facts/_preamble.md` cites it too** — and that file is part of the near-verbatim
fact mirror. Editing it widens the drift your own new tool measures. Either declare the edit in
`LOCAL_ADAPTATIONS` in the same commit, or leave the citation and say why.

⚠️ **Skills and the kernel cite it**: `CLAUDE.md`/`AGENTS.md`, `smr-orientation`, `doc-editing`,
`doc-surgeon`, all four perma prompts. `AGENTS.md` and `.agents/skills/` are GENERATED — edit the
source and `--regen`, never the mirror.

⚠️ Entries `D06`, `D07`, `D12` cite it for retired modules' persisted names. Those rows outlive
their modules and must still resolve after the move.

---

## 6 · Method

`doc-editing` before any documentation edit — it carries OI-09, the protected list and the
archive rules. `smr-orientation` for placement and counts. House rules are `CLAUDE.md`.

⛔ **Anything you move is moved VERBATIM and you prove it**, as `8192a63` did with `CO_RUNS.md`:
extract the span from `git show HEAD:docs/agent/PROVENANCE.md` and diff it against the new file.
For §2 this is not a nicety — it is a table of strings that are save contract.

⚠️ **Re-derive every citation after each step.** This is the trap that has now bitten this project
four times in one day; §5 is 39 chances to repeat it.

---

## 7 · Scope

**In:** `docs/agent/PROVENANCE.md`; new files under `docs/agent/support/`; `tools/README.md`,
`tools/sync_facts.py`, its selftest, and the script headers citing §6; `docs/README.md` and
`CLAUDE.md` where they name the file; every citation in §5.

**Out:** module behaviour, persisted-name VALUES, `docs/agent/bugs/` and `facts/` content beyond
the citation repoints, and `KNOWLEDGE_SYNC_PASS.md`'s own sweep.

---

## 8 · Stops — at most three

1. ⛔ **The two shipping files.** Repointing a comment in `items.lua` / `metadata.lua` is zero
   behaviour change, but they ship, and the `DECISIONS_OWED` item 89 precedent treats a
   comment-only edit to a shipping file as the owner's call. **Do the rest, leave those two, and
   ask** — one line in `DECISIONS_OWED.md` as the next `OI-` number. ⛔ Do not delete
   `PROVENANCE.md` while two shipping files still point at it: land the new home first, ask, and
   let the deletion follow the ruling.
2. **The sync tool wants to grow past a drift report** — bidirectional sync, auto-commit,
   conflict resolution. Stop and report. The tool's job is to answer one question.
3. **A §2 row cannot be proven to have moved intact.** Stop. A save-contract string is the one
   thing in this repo that cannot be repaired after the fact.

---

## 9 · Do not claim

- ❌ *"Nothing was lost."* ✅ *"every §2 row and §4 rule was diffed against `git show HEAD:` and is
  byte-identical at its new home"*, naming anything that is not.
- ❌ *"The sync is automated."* ✅ what the gate checks, what `--apply` does, and that applying is
  a human action.
- ❌ *"39 citations updated."* ✅ the re-run grep, showing zero unresolved.
- ❌ any count you did not emit — `python tools/doccheck.py --emit-counts`, `.claude/baseline.py`.

---

## 10 · Lifecycle

⛔ **One-off.** `git rm` this file **and delete its row from `docs/agent/prompts/README.md` in the
same commit** that lands the result — no tombstone. doccheck's PROMPT MAP gate holds both
directions. If stop 1 parks the job, the brief STAYS and its row gains a one-line state note.
