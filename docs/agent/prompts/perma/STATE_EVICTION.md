# STATE_EVICTION — pull-only cleanup job

Use when a task, prompt or the owner calls for STATE cleanup, or when doccheck
warns on its size. One session, docs only, no code or playtests. This is a
reusable prompt: keep it after execution. Designed in the fix pack 2026-08-18
with the owner; the complete admission door below was ruled there on
2026-09-15. This revision was authored against `3d53b48`; check changed sources
before inheriting its facts. The original design record is the owner's
conversation and the fix pack's first-run SESSION_LOG entry.

**The problem this prompt exists for:** `docs/agent/STATE.md` is pull-only but
highly shared when current status is called for, so close-outs are tempted to
wedge verdicts there. Left alone, it compounds; the cure is enforcing the
admission door below, not compressing history into denser lines.

**Formatting (owner ruling 2026-08-18, checklist 42): most efficient and
safest, nothing else.** doccheck's byte caps do the reading-cost job, so
format purely for machine safety: one fact per line, every line under the
per-line byte cap, stable IDs (`D##`/`EF-###`/`OI-##`/item numbers) so grep
lands, no decorative prose, and NEVER widen or pack lines to satisfy any
budget — if content doesn't fit, evict, don't compress.

## The admission door — every section

STATE is a kernel: **status + pointer, never derivation.** Apply the complete
door to **every existing or proposed line in every section**: Now, Build state,
Holds, Open owner decisions and any future section.
A section name grants no admission. Required structural text and protected
parser dependencies must be identified explicitly, never called passing status.

**Owner ruling, 2026-09-15: a line enters STATE only by passing ALL FOUR tests.
AND-ed, never OR-ed. One failure is enough.** A pass on one test cannot rescue
a failure on another, and applying only a subset is not an admission review.

**1 · HARM — name the victim.** Who is worse off, and can the next command make
them whole? A mechanism is not a victim. Floor: moderate. A silent harm
outranks a loud one of the same size. "Files get deleted" is not harm if nobody
wanted them.

**2 · REACH — both halves must answer everyone.**

- **(a) Whose job is this?** If you can name a role, it belongs in that role's
  doc. Only an answer of *everyone* survives.
- **(b) Who needs to know this?** Not everyone means it belongs where they are.
  **Self-consuming chain work never passes (b)** — by construction its
  knowledge dies with the chain, so no future reader needs it carried in the
  kernel. Do not weigh that class case by case.

A destructive rail is role-gated by construction. An epistemic rail that
binds every session can pass both reach questions; it still needs the other
tests. An unfinished task for one role fails reach even while its status can
change.

**3 · GATE — can a machine catch it?** Then cite the gate instead of restating
the duty. If a machine *could* and nothing does, the entry is a placeholder
and the real deliverable is the check. A placeholder still needs to pass the
other tests; when the check lands, the restated duty leaves.

**4 · VOLATILITY — can the thing's state still change?** Settled means it is a
record, not state. Receipts, tombstones, immutable facts and closed chains
do not become status by passing harm, reach or gate. The current version can
change; when it changes, the previous version changes too. A line that moves
only when another STATE line moves is still state; a line that never moves is
not. Passing volatility alone does not admit it.

For admitted content, keep governing pointers to one dated line linked to the
ruling's body; open owner decisions use item ids and five-word gists, with
the ask itself in `docs/PLAYTEST_CHECKLIST.md`, in that file's format.
These formats do not exempt either category from the door.

### Authority preserved here

The source is the fix pack's gitignored `.claude/DECISIONS.md`, 2026-09-15 entries
"THE STATE ADMISSION TEST, COMPLETE" and "THE VOLATILITY TEST". This prompt
holds the durable door; executing it does not require that local file.
The owner's words are preserved verbatim:

> "This shoud also be part of the admintions test if its a job it should be asked Whose job if it
> doesn't = Everyone it failes. Who needs to know = Everyone? (including self consuming chain work)
> No? then it fails"

> "I think that is another good admissions test. The current state of something is something that
> implies its state can change. A current version can change. if a current version changes the
> previous version changes"

## Homes for refused content

Name the destination and open its actual passage before cutting; a matching
heading is not proof. If the content is absent, put it at its proper home in
the same change as the cut. No line stays merely because it has no home.

- Role-specific duties and documented routes belong in that role's document.
- Module records and immutable engine facts belong in their entry under
  `docs/agent/bugs/` or `docs/agent/facts/`; discover entries through a scoped
  `rg -n` lookup in the respective `INDEX.md`, then read the actual passage.
- Closed efforts and dated evidence belong in their report or
  `docs/archive/SESSION_LOG.md`. Chain findings stay in the chain's own record.
- Owner decisions belong in `docs/PLAYTEST_CHECKLIST.md`, in that file's format.
- A purged file needs no tombstone: `git log -S` retains its history.

A sweep may elevate a rule into its proper home, never retire one. Cutting
a duplicate does not revoke its source ruling or erase an open obligation.

Pull build counts with `python tools/doccheck.py --emit-counts` when needed;
they are no longer stored in STATE (the fix pack owner's scope override,
2026-09-15, its `docs/archive/PLAYTEST_ARCHIVE.md` "STATE cleanup scope override — 2026-09-15").

## Scratch sweep — files 14 days old

Owner decision, 2026-09-21 (ported the same day from the fix pack, which
landed the rule first): `scratch/` is the git-ignored home for agent and
subagent working files; nothing else sweeps it, so this prompt does, every run.

1. Run `python tools/doccheck.py` and read its `SCRATCH:` line for the current
   count and the oldest file's age.
2. Delete every file directly under `scratch/` whose mtime is 14 days old or
   older; never delete `README.md`. Sum the bytes reclaimed as you go.
3. Report what was deleted — each name and its size — and the total bytes
   reclaimed, or report there was nothing to sweep.
4. Read the same run's `PARENT FILES` line and report every name it lists.
   Never delete there: that folder holds the owner's other projects, and
   removing anything from it is the owner's call, not this prompt's.

## Scope and stopping conditions

Review the whole STATE file and the destination passages needed for its cuts.
Do not start game work, change owner-debt status or migrate a parser dependency
as a side effect. Stop on shared-path changes, uncertain authority, a needed
home beyond existing authorization, or a conflicting machine requirement;
record the exact conflict and proposed resolution. Use an existing owner
override within its scope; do not ask for the same authorization again.

Before execution, keep a live work list covering the whole job: one item per
commit-and-verify unit, exactly one in progress. Split it as work splits and
mark each unit complete with its result. Out-of-scope findings go to their
task's record; discovery alone does not authorize their repair.

For inherited facts, record the fact, measurement command, HEAD/build and one
falsifier. Start with `git diff --stat 3d53b48..HEAD -- tools/doccheck.py docs/agent/STATE.md`;
unchanged sources need no re-derivation, and changed groups need a scoped check.
At that baseline build counts come from `--emit-counts`, and
`python tools/doccheck.py --emit-counts` can falsify that claim.
A changed implementation invalidates its old test evidence: rerun the affected
suite, not only the formerly failing check.

## Procedure

1. Start with `git log` and `git pull --ff-only`; resolve a stale baseline before
   editing. Read `docs/agent/STATE.md` whole. Read the newest entry in
   `docs/archive/SESSION_LOG.md` to match its voice.
2. Run the scratch sweep (below). It is independent of STATE's content and
   needs no commit — `scratch/` is git-ignored — so it runs every time this
   procedure runs, not only when named separately.
3. Note the current HEAD sha — it becomes the grave:
   `git show <sha>:docs/agent/STATE.md` is the full pre-eviction file, forever.
4. Judge every line under all four tests; record each refusal's verified home
   and every survivor's basis. Preserve conditions and open obligations.
   Prepend ONE SESSION_LOG entry (below the preamble; archive entries are
   never edited): a digest of each closed effort being evicted — a few lines
   each, dated, with pointers to its reports/graves — opening with a
   `tags:` line listing every D##/EF-###/OI-##/item-## the entry touches, so
   future greps land here. **Every evicted payload must have a verified home;
   being closed alone is not a destination.**
5. Rewrite STATE.md to the admitted status. Keep its pull/read-path notice.
   Record the grave in the eviction report; remove empty section headings with
   their content.
6. Verify: `python tools/doccheck.py` GREEN (it enforces the warn/hard byte
   caps and the per-line cap); every retained status line in every section
   passes all four tests; structural/parser exceptions are identified; no
   "superseded" chains remain; open decisions match `docs/PLAYTEST_CHECKLIST.md`.
7. Measure the clean file in bytes and put the before/after numbers in the
   report to the owner.
8. Commit (boring subject) and push.

Report what left, its verified homes, what stayed and why. Do not claim "STATE
is clean" or "GREEN therefore admitted": doccheck checks structure and bytes,
not whether prose passes this door. A homeless line is unresolved work, never
a successful disposition or a reason to admit it. Owner-facing asks live in
`docs/PLAYTEST_CHECKLIST.md`, never only here or in STATE.
