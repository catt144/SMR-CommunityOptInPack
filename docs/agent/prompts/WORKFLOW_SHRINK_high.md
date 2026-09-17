# Shrink `docs/agent/WORKFLOW.md` toward the fix pack's shape — one-off, deletes itself when fired

**Authored 2026-09-17 at `8192a63`.** Staleness check before you trust anything below:

```sh
git log --oneline -5 && git pull
git diff --stat 8192a63..HEAD -- docs/agent/WORKFLOW.md CLAUDE.md docs/agent/prompts/ .claude/skills/
```

Empty diff ⇒ every figure and citation here holds. Non-empty ⇒ re-measure the section table in §3
with the command in §2 before cutting anything.

---

## 1 · Authority — settled, do not re-argue

⚖️ **Owner ruling 2026-09-17 (`docs/DECISIONS_OWED.md` OI-09), recorded in the `doc-editing` skill:**
**agent-facing documents MAY be machine-tuned hard.** `WORKFLOW.md` is agent-facing. Content already
recorded elsewhere is **DELETED, not re-archived**. Retire silently — no dated note, no
strikethrough, no "superseded by", no pointer. `git log -S` holds deleted text; the reasoning goes
in the commit message.

⚖️ **Owner ask, same day, verbatim:** *"its also a monolith, I would like it to be more similar to
smr pack"* — the fix pack, `C:\Dev\SMR-BugFixPack\docs\agent\WORKFLOW.md`.

⛔ **MODULE FREEZE is untouched by this job.** You are editing documentation only. No `Code/`, no
`items.lua`, no `metadata.lua`, no persisted name, no probe.

---

## 2 · The end state

`docs/agent/WORKFLOW.md` reads like the fix pack's: **a routing surface, not a container.** The
donor's is 18,187 B / 287 lines and covers a strictly larger project (≈187 defect entries, ≈46
shipping modules, against this repo's 9 and 5).

**Target: at or under 30,000 B, with no requirement lost.** That is roughly a 40% cut from today's
50,718 B. ⛔ **The target is a cap, not the goal** — a document that hits 30,000 B by deleting a
binding rule has failed the job, and one that lands at 33,000 B with every requirement homed has
passed it. Say in your final commit which one you did.

Re-measure, never hand-type:

```sh
python .claude/baseline.py | grep WORKFLOW      # LF-normalised bytes, the same unit doccheck uses
python tools/doccheck.py                        # must be GREEN before every commit; the hook enforces it
```

---

## 3 · What is actually in there — measured 2026-09-17 at `8192a63`

Byte census of our sections against the donor's equivalents. **This is the survey's §5 question,
already answered — do not re-derive it, verify it with the staleness check in the header.**

| our section | bytes | the donor's same section |
|---|---|---|
| Release steps | 6,475 | 1,146 |
| ⛔ Probe hygiene | 5,823 | 1,958 |
| Testing checklist per fix | 4,489 | 2,056 |
| Binding authoring rules | 3,829 | **none — its `CLAUDE.md` rules header** |
| Authoring a prompt / job brief | 3,693 | 338 (the rest is in its `prompt-authoring` skill) |
| Reading path for a new session | 3,172 | **none — its kernel + skills** |
| ⛔ BOTH MODS LOADED | 2,924 | 861 |
| ⛔ Cheats on playtest saves | 2,790 | 858 |
| `[FAQ]` tag | 2,772 | 365 |
| Release marking | 2,690 | 1,054 |
| banner / preamble | 2,742 | 304 |
| Layout | 2,101 | 1,796 |
| ⛔ Log review | 2,028 | 502 |
| Install for testing | 1,164 | 473 |
| Per-fix discipline | 1,001 | 607 |
| fpk verification | 954 | *(its "After a game patch", 3,085)* |

**The 29,108 B Co-runs section is already gone** — moved verbatim to `docs/agent/support/CO_RUNS.md`
at `8192a63`, leaving a six-line pointer. That was 49% of the original gap and it is **not** work
you have to repeat. It is also the pattern to copy: *a section becomes a pointer; the detail becomes
a pull file.*

### The three buckets, in the order they pay off

1. **Duplication of things this repo now has elsewhere.** ⭐ **Start here — it is the cheapest and
   the least judgement.** On 2026-09-17 this repo ported the donor's `CLAUDE.md` rules header and
   its five `.claude/skills/`. The donor has **no** "Reading path" and **no** "Binding authoring
   rules" section *because its kernel and skills carry them.* Ours still has both, 7,001 B between
   them, written before the port. ⛔ **Prove the body, not the heading** — for each rule, open the
   kernel or the skill and confirm the duty is actually there before deleting the prose.
2. **Detail that belongs in a pull file** — the Co-runs pattern again. `docs/agent/support/` now
   exists and the folder contract names it (`CLAUDE.md`, `docs/README.md` "Where new things go").
   The test for `support/` versus `reports/`: **would a leg that ignored it be wrong?** If yes it is
   protocol and goes to `support/`; reports are explicitly not authority (`WORK_PROMPT.md` §5).
   Release steps, Probe hygiene and the testing checklist are the candidates.
3. **Narrative and history inside a rule.** Most sections are 1.5–3× the donor's because each rule
   carries the story of the miss that produced it. Keep the rule and the one clause that makes it
   obeyable; a dated incident is `docs/archive/SESSION_LOG.md` material, and if it is already
   recorded there it is **deleted, not re-archived**.

---

## 4 · Method

**Deletion is the default.** Each surviving line earns a reason, a home, or a slot under the cap.
Do not defend cuts line by line — that is how the donor's own attempt never got past "down enough".

⛔ **Gaming the cap, concretely — all four are failures, not clever:**

- moving 10 KB into `support/` that nobody will ever pull, to make one number smaller;
- compressing four rules into one dense sentence that satisfies the byte count and is no longer
  obeyable — the donor did exactly this under a shared byte cap and **broke four rules** (its
  `396d7f2`);
- deleting a rule because a *heading* elsewhere matches it;
- re-archiving settled content the ruling says to delete.

**Do the inventory before you rewrite.** Build a requirements inventory of every binding duty in
today's `WORKFLOW.md` — one line each, with where it will live afterwards. Then cut against the
inventory. ⛔ **Do not grade your own rewrite from memory of the old text:** re-read the inventory
against the *new* file only, and report any duty you cannot find.

⚠️ **Re-derive every line citation after each prune.** Citations die the moment surrounding text
moves. The donor found six worklist items and an entire authored brief already executed because of
this; this session found two entry citations left one hop short by a single section move, and a
"(68 at 2026-08-31)" fact count that had been 107 for weeks. It costs one grep.

⛔ **Anything you move is moved VERBATIM, and you prove it**, as `8192a63` did:

```sh
git show HEAD:docs/agent/WORKFLOW.md > "$SCRATCH/wf_old.md"   # then diff the extracted span
```

Skills carry the rest: **`doc-editing` before any documentation edit** (it holds the OI-09 ruling,
the protected list and the archive rules), `smr-orientation` for placement and counts. House rules
are `CLAUDE.md`. Do not restate them here.

---

## 5 · ⛔ Protected — these do not get cut, whatever the byte count says

Named by the efficiency survey §5 as what a naive shrink destroys, and re-affirmed by OI-09:

- **The two bans** — persisted names are save contract; zero `SMRFixPack` references in executable
  code.
- **`FIX_POLICY` §4 INVERTED** for a mod whose product IS opinionated modules, with the donor's §4
  kept verbatim as **§4-donor**. (That is `FIX_POLICY.md`, out of scope here — listed so you do not
  "tidy" a WORKFLOW clause that depends on it.)
- **The §5 dial addendum for D09**, and the **both-configuration ship test** (`FIX_POLICY` §8).
- **The ADAPTED-COPY banner's six clauses** at the top of `WORKFLOW.md`. They are what stops a
  session reading a donor clause as this repo's. Clause 6 in particular carries the only surviving
  method from a deleted 261 KB audit. Compress the prose if you can; do not drop a clause.
- **Every owner ruling with its date and condition** — the cheats rule, BOTH MODS LOADED, probe
  hygiene's ARM gate, the log-review rule, sign-off tiers. A rule may become terser. It may not lose
  *who ruled it and when*, because that is what makes it binding rather than advice.

---

## 6 · Scope

**In:** `docs/agent/WORKFLOW.md`; new files under `docs/agent/support/`; the map row in
`docs/README.md` and the folder contract in `CLAUDE.md` if you add a `support/` file; repointing
citations that your own cuts break.

**Out:** `FIX_POLICY.md`, `STATE.md`, `PROVENANCE.md`, `DECISIONS_OWED.md`, `docs/agent/bugs/`,
`docs/agent/facts/`, and `Code/` in every form. ⛔ **`docs/agent/facts/` is a VERBATIM mirror of the
fix pack's and a re-sync is a straight overwrite** — if a fact cites a WORKFLOW section you moved,
leave the fact alone and say so in the commit; the donor's WORKFLOW has the same section names.
An out-of-scope finding goes in the commit message or `DECISIONS_OWED.md`, not into an edit.

---

## 7 · Stops — permission to report instead of pushing on

1. **A duty has no home but `WORKFLOW.md`, and keeping it blows the cap.** Keep the duty, miss the
   cap, say so. The cap is never the reason a rule dies.
2. **A cut would need an owner ruling** — a rule whose wording is itself an owner decision, or
   anything touching a player-facing string. Write the option up in `docs/DECISIONS_OWED.md` as the
   next `OI-` number and stop on that item.
3. **The inventory does not fit one session.** Commit the inventory and the bucket-1 cut, then
   propose a chain (`reports/CHAIN_METHOD.md`). ⛔ Do not start a rewrite you cannot finish — a
   half-rewritten rule document is worse than the monolith.

---

## 8 · Do not claim

- ❌ *"No requirement was lost."* ✅ *"Every duty in the inventory was found in the new text, by a
  re-read against the inventory alone"* — and name any you could not place.
- ❌ *"Matches the fix pack."* ✅ the measured byte figure from `.claude/baseline.py`, and which
  sections are still larger than the donor's.
- ❌ *"Archived for safety."* Under OI-09, content recorded elsewhere is **deleted**. If you
  archived instead, say which content and why the ruling did not apply to it.
- ❌ any count you did not emit. `python tools/doccheck.py --emit-counts`.

---

## 9 · Lifecycle

⛔ **One-off.** When this job is fired, `git rm` this file **and delete its row from
`docs/agent/prompts/README.md` in the same commit** — no tombstone, no struck-through row. doccheck's
PROMPT MAP gate holds both directions and reds on either half. The outcome lives in the commit
messages and in `PROVENANCE.md` if you add a `support/` file.
