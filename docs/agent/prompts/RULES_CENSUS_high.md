# The rules census — classify every rule-shaped line, then place it by tier

**Authored 2026-09-17 at `b641212`.** Staleness check before trusting a figure:

```sh
git log --oneline -5 && git pull
git diff --stat b641212..HEAD -- CLAUDE.md docs/ tools/doccheck.py
python .claude/baseline.py | grep RULE-PROXY      # re-emit; never quote the table below as current
```

---

## 1 · Authority — settled, do not re-argue

⚖️ **Owner, 2026-09-17:** *"all rules that all agents need to know live in a single unified
document, no duplication. Rules that only pertain to docs only live in that doc with a rules header.
And a rule in the unified doc that explains the rule about the rules header."* And: *"I want all our
rules to match the same requirements that its needs to meet"* — the fix pack's.

⚖️ **Owner, 2026-09-17, on who may purge a rule:** *"before we run into an issue with a rule cannot
be purged by an agent, I authored the rules test so it carries my authority."*

⇒ ⭐ **THE TEST'S VERDICT IS THE OWNER'S RULING.** Applying it is executing a decision, not making
one. You do not need to come back for a rule the test disposes of — including `redundant` and
`dead`. Record the verdict and its evidence in the commit message.

⛔ **The delegation is to the TEST, not to your judgement.** A rule is purged because the test
disposes of it, never because it reads as unnecessary. Where the test does not decide — the shapes
in §4 conflict, or a (b) incident check is inconclusive — that is the boundary of the delegation
and it goes to the owner (§10 stop 1). The protected list in §6 and the two bans are outside the
test's reach entirely.

⚖️ **The model is the donor's `docs/agent/reports/DOC_RULES_ARCHITECTURE.md` (2026-09-14)**, read
from `C:\Dev\SMR-BugFixPack`. ⛔ Read it before you start. Three tiers, defined by **when they load**:

| tier | home | loads | carries |
|---|---|---|---|
| **1 · permanent** | `CLAUDE.md`, mirrored byte-identical to `AGENTS.md` | mechanically, every session, both vendors | only duties binding **every** session regardless of task |
| **2 · local** | one block per **folder**, or per doc where a doc is genuinely unique | when an agent works there | duties governing edits to that material |
| **3 · task** | a skill in `.claude/skills/` | on invocation | procedure for a named task |

✅ **Already done at `b641212`** — do not redo: the tier-1 meta-rule, the donor-names duplicate
promoted out of two banners, `FIX_POLICY`'s tier-2 header, and the gate at 3 blocks / 22 rules.

⛔ **MODULE FREEZE is not in play.** Documentation and `tools/doccheck.py` constants only.

---

## 2 · ⛔ Sequencing — this runs BEFORE `PROVENANCE_DISSOLVE_high.md`

The owner ruled this order on 2026-09-17 because the dissolve folds `PROVENANCE` §2 into
`FIX_POLICY` §3 and repoints citations in `STATE.md` — both surfaces this census rewrites. Census
first means the dissolve lands into settled structure.

⛔ **Do NOT triage `docs/agent/PROVENANCE.md`.** It is already condemned by its own brief, and its
§2 is a table of frozen strings — **data, not rules**. Touching it here duplicates that job and
creates a merge conflict with it. Leave it entirely alone, including its citations.

---

## 3 · The measured scope

Re-emit before using. At `b641212` the proxy read **127 lines** across nine files:

| file | proxy lines | note |
|---|---|---|
| `docs/agent/FIX_POLICY.md` | 38 | the biggest pool; has a tier-2 header already |
| `docs/agent/STATE.md` | 24 | ⛔ see §5 — its charter allows **zero** |
| `prompts/perma/DISPATCH.md` | 19 | |
| `prompts/perma/WORK_PROMPT.md` | 14 | |
| `prompts/perma/KNOWLEDGE_SYNC_PASS.md` | 12 | |
| `docs/README.md` | 10 | the map; read by agents and the owner |
| `CLAUDE.md` | 7 | tier 1 itself — check for duties still in its prose |
| `prompts/perma/STATE_EVICTION.md` | 2 | |
| `docs/agent/WORKFLOW.md` | 1 | already shrunk at `1ae0d85` |

⚠️ **It is a PROXY, not a census.** It counts emphasis markup, so it over-counts warnings that
state no duty and under-counts duties written in plain prose. **That under-count is the half that
matters** — a duty in flat prose is exactly what this job exists to find. Do not treat 127 as the
denominator.

---

## 4 · ⛔ THE RULE-PLACEMENT TEST — pass it or be purged

⚖️ **Owner, 2026-09-17: "all rules need to pass the rules test, or they get purged."** Purged
means DELETED, under OI-09, not archived and not softened into a note.

The test is the donor's `docs/agent/reports/RULE_PLACEMENT_TEST.md` (owner design session,
2026-09-14). ⛔ **Read it in full before classifying anything.** One question, asked of every
rule-shaped sentence:

> ## What actually stops this, if not the reader's memory?

⛔ **Not "is this important?"** — importance is why the documents grew. The answer places the rule,
and usually deletes it.

| what actually stops it | disposition |
|---|---|
| **Structure** — the reader cannot perform the action at all | **delete the rule** |
| **A guard** — a machine already catches it | **one-line pointer to the gate**, never a restatement |
| **Nothing, and it has been violated in practice** | ⛔ **it was never a rule. It is a wish** — DEAD |
| **Nothing, and it binds exactly one job** | that job's **skill or brief** |
| **Already a recorded fact with a canonical home** | delete the prose, **keep the fact** |
| **Nothing, binds every session, no guard is possible** | tier 1 — ⚠️ this list should be very short |

⭐ **The finding that justifies the whole job**, in the donor's words: *an unenforced rule is
indistinguishable from a deleted one, except that it still costs every agent that reads it.* Its
worked case: a rule sat in a document for six weeks, was broken in the most important field leg the
project had run, the breaking was **correct**, and no agent ever flagged it — because nothing was
ever going to check.

### The four shapes that should not be rules — and they do NOT share a disposition

| shape | meaning | disposition |
|---|---|---|
| **(a) CANNOT** | structurally impossible for the reader | **delete** |
| **(b) WOULD NOT** | possible, but contrary to how an agent operates | ⛔ **incident check REQUIRED — see below** |
| **(c) WRONG READER** | the actor is not this document's audience | **move it, do not delete** |
| **(d) NOT A RULE** | information in the imperative; requires no action | engine fact → file it as an `EF-` **in the fix pack first**; lesson → pull-only reference. Never tier 1 |

### ⛔ (b) is the branch that can delete an EARNED rule — run its falsifier

The discriminator is **not** "would a well-behaved agent do this?" It is **"has this actually
happened?"** A rule can look exactly like something no careful agent would ever do, and exist
precisely because one did. The donor's counter-case: *"never `git checkout --` as a restore"* reads
as gratuitous, and an agent there did it and destroyed an uncommitted rewrite. Cutting it would
have deleted a receipt.

- **A recorded incident exists → KEEP**, and keep the incident attached to it.
- **No incident and no guard → cut.**

⇒ **Mechanical first pass:** every rule carrying neither an incident nor a guard is a *candidate* —
not a verdict.

⚠️ **The (b) yield is expected to be small, and you may not report a small yield as a measured
one.** The donor's two keyword passes over this genre returned one hit, and it says plainly that
two greps do not bound a class defined by meaning. **Read for this; do not grep for it.**

### ⛔ Duplicates are found by MEANING, not by string

Cluster by **what the rule requires of the reader**, not by its wording, its name or the artifact
it mentions. Two rules naming different files, in different documents, under different headings,
can impose the same duty — and a grep cannot see it. The donor's inventory found only near-verbatim
pairs precisely because semantic duplication was never sought.

### ⭐ This applies to the rules already in the headers

All 22 canonical rules at `b641212` are in scope, **including the three added that day** (the
tier-1 meta-rule, the donor-names rule, and `FIX_POLICY`'s two). They were placed under the
architecture but **never put through this test.** Run it on them like everything else; a kernel
rule that fails is purged like any other.

### What the donor's numbers predict

Its census classified 852 sentences: **global 16 · doc-local 30 · redundant 20 · dead 6 ·
task-local 780.** Seven hundred and eighty stayed as prose in their task documents. ⇒ A census that
promotes most of what it touches has mis-classified. **Promotion is the exception; the common
outcomes are "stays as task prose" and "purged."**

⭐ **`redundant` and `dead` are yours to execute** under the owner's 2026-09-17 delegation (§1) —
the test decides them, you apply it. ⛔ **The evidence is still owed, in the commit message**, and it
is what makes the verdict auditable rather than asserted: for `redundant`, both locations quoted and
the shared duty stated in your own words; for `dead`, the incident check that was run and the proof
nothing reaches it. A purge recorded without its evidence is indistinguishable from a deletion by
preference.

⚠️ **The delegation removes a queue; it does not lower the bar.** The (b) falsifier above is the
guard against over-purging, and it binds hardest now that nobody downstream will catch a wrong cut.

## 5 · `STATE.md` goes to zero rules

The donor's spec is explicit, and its reasoning applies here unchanged: STATE's own charter is
*status + pointer, never derivation*, so by that charter it carries no rules — and carrying them is
why it keeps pressing its byte cap. Ours holds 24 rule-shaped lines against a cap it sat 9 bytes
under earlier today.

Every rule leaves STATE for its tier. **Status, pointers, holds, owes and the counts pointer stay.**

⛔ The eviction door binds: `prompts/perma/STATE_EVICTION.md`, four tests AND-ed, and
`doccheck`'s `STATE ADMISSION` gate prints the added lines beside the questions on any commit that
adds one. ⚠️ Several of STATE's lines are **live 1.1.0 holds** with no other home yet — that is the
caveat `DECISIONS_OWED` OI-08 raises. A hold with nowhere to go **stays**, and you say so.

---

## 6 · ⛔ The two traps the donor paid for

**A per-doc header where a folder already states the rule ENCODES the redundancy.** The donor's
standing proposal was 16 headers; its own measurement cut that to **seven**, because eleven were in
`prompts/perma/` and `prompts/README.md` already stated the rule once for all of them. Hoisting
each file's copy into its own header would have made nine permanent copies of one line — the exact
failure the work existed to end. ⇒ **This repo's `prompts/README.md` already carries 3 rules for the
whole folder.** A perma prompt gets its own header only if it carries a duty that is genuinely its
alone. `docs/agent/` has **no folder README**; creating one is a legitimate tier-2 home if the
duties justify it, and is not required.

**Working papers must not land in the documents being censused.** The donor's rules audit put
842,551 B of JSON into `docs/` — more than the archival had removed, so the de-bloat was net
negative and nobody noticed. ⇒ **Every inventory, worksheet and intermediate list goes in
`.claude/`**, which is gitignored here except `skills/` and `agents/`. `.claude/baseline.py` is the
worked example.

---

## 7 · What a canonical rule must satisfy

Enforced mechanically by `check_rule_headers` (`tools/doccheck.py`), proven by
`tools/rule_headers_selftest.py` — 13 cases including a negative control:

- lives inside exactly one `## Must_Read_Header` / `<!-- RULES -->` block, in a document named in
  `RULE_HEADER_DOCS`;
- reads `Rule: <one imperative sentence>.` — **no bold, no emoji, and none of MUST / NEVER /
  ALWAYS.** A rule that has to shout has not been written precisely enough, and the shouting does
  not survive being quoted somewhere else;
- states **one** duty, unique repo-wide after whitespace and case folding — a duplicate is RED;
- never in `STATE.md`, never on a generated or archived surface;
- header byte caps: 1,024 warn / 2,048 hard for a doc-local block, 2,560 / 3,072 for the kernel.

⛔ **Adding a file to `RULE_HEADER_DOCS` forces it to grow a block** — the gate REDs if it has none.
Add the constant and the block in the same commit.

⚠️ **The kernel cap is not a compression target.** The donor broke four rules compressing them to
fit one shared cap (`396d7f2`); that is why the kernel has its own. If the kernel would exceed
3,072 B, something in it is not tier 1 — re-classify rather than compress.

---

## 8 · The `[A3: pass]` tag — ask, do not assume

The donor suffixes every canonical rule with `[A3: pass]`, recording that its owner adjudicated that
sentence in its one-time census. ⛔ **It was deliberately not copied here** (`PROVENANCE.md` §8):
that audit ran on its text. ⭐ The owner's 2026-09-17 delegation changes the basis: a rule this
census puts through the owner-authored test and KEEPS has been adjudicated, which is what the tag
records. Ask whether to adopt it; `RULE_STYLE_RE` in `tools/doccheck.py` carries the one-line change that reinstates
it, and the constant says so. Do not add the tag to a rule the owner has not ruled on.

---

## 9 · Scope

**In:** `CLAUDE.md`/`AGENTS.md`, `docs/README.md`, `docs/agent/STATE.md`, `FIX_POLICY.md`,
`WORKFLOW.md`, `prompts/README.md`, `prompts/perma/*.md`, `.claude/skills/*`, and
`RULE_HEADER_DOCS` in `tools/doccheck.py`.

**Out:** `docs/agent/PROVENANCE.md` (§2 above), `docs/agent/bugs/`, `docs/agent/facts/` — the facts
folder is a verbatim mirror and a re-sync overwrites local edits — `docs/archive/`, `docs/agent/
reports/`, and all of `Code/`, `items.lua`, `metadata.lua`.

⛔ **A skill must earn its existence.** Owner's bar, quoted in the donor's spec: *"it needs to meet
the requirements of the skill does something"* — no skill created merely to host a rule. Tier 3 is
for procedure, and this repo's five skills already exist.

---

## 10 · Stops — at most three

1. **The test does not decide.** Two shapes in §4 conflict, or a (b) incident check is
   inconclusive — you can show neither an incident nor its absence. That is the boundary of the
   delegation: KEEP the rule, file the question under the next `OI-` number in
   `docs/DECISIONS_OWED.md`, and carry on with the rest. ⛔ An undecidable rule is never purged on
   the balance of probability.
2. **A STATE line is a live 1.1.0 hold with no other home.** It stays. Say which and why, rather
   than inventing a home or deleting a hold.
3. **The census does not fit one session.** Commit the inventory in `.claude/` and the
   uncontroversial promotions, then propose a chain (`reports/CHAIN_METHOD.md`). ⛔ Do not leave
   half a document's rules migrated — a partly-migrated rule set is worse than an unmigrated one,
   because neither location is now authoritative.

---

## 11 · Do not claim

- ❌ *"No duty was lost."* ✅ *"every sentence classified `global` or `doc-local` was found at its
  new home by a re-read against the inventory alone"*, naming any you could not place.
- ❌ *"Deduplicated."* ✅ the count of copies removed, with both original locations quoted.
- ❌ *"STATE is clean."* ✅ how many rule-shaped lines remain, and for each, why it had no home.
- ❌ a proxy figure as a census total (§3). ❌ any count you did not emit.

---

## 12 · Lifecycle

⛔ **One-off.** `git rm` this file **and delete its row from `docs/agent/prompts/README.md` in the
same commit** that lands the result — no tombstone; doccheck's PROMPT MAP gate holds both
directions. If a stop parks it, the brief STAYS and its row gains a one-line state note.
