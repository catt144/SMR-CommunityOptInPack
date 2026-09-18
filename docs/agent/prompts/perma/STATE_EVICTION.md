# STATE_EVICTION — standing cleanup prompt

Carried 2026-08-31 from the fix pack's `prompts/STATE_EVICTION.md` (designed
2026-08-18 with the owner, checklist 42). Fired by the owner whenever doccheck
WARNs on STATE.md's size, or on their own call. One session, docs only, no code.

**The problem this prompt exists for:** STATE.md is the one mandatory read, so
every close-out is tempted to wedge its verdicts there — presence in STATE has
felt like the only guaranteed audience. Left alone, the file compounds (the fix
pack's hit 71,077 bytes while satisfying a 60-line budget; this repo's line 28
had grown to 1,734 bytes by 2026-08-31 — lines become walls). The cure is not a
summary pass; it is enforcing the push/pull boundary below.

**Formatting (owner ruling 2026-08-18): most efficient and safest, nothing
else.** doccheck's byte caps do the reading-cost job, so format purely for
machine safety: one fact per line, every line under the 200-byte per-line cap,
stable IDs (`D##`/`EF-###`/item numbers) so grep lands, no decorative prose,
and NEVER widen or pack lines to satisfy any budget — if content doesn't fit,
evict, don't compress.

## The boundary — what earns push (stays in STATE)

STATE is a kernel: **status + pointer, never derivation.** Five sections only:

1. **Now** — current position and next action. No supersession chains: if a
   sentence needs "superseded by", the superseded half is history — evict it.
2. **Hazards / gates** — admission test, applied per line: *it names an action
   an agent could take unattended, states the rail, and points to the detail.*
   Anything that fails the test is orientation, not a hazard — evict it.
   Headline is push; the evidence behind it is pull.
3. **Rules in force** — owner rulings still binding, one line each, dated,
   with a pointer to where they were made. A ruling fully discharged or
   recorded in a policy doc (FIX_POLICY/WORKFLOW) needs only the pointer.
4. **Open owner decisions** — item ids + five-word gists; bodies live in
   `docs/DECISIONS_OWED.md` (this mod's own list since 2026-09-12), except the
   three that bind the FIX PACK and stayed on its `docs/PLAYTEST_CHECKLIST.md`.
5. **Build state** — ⛔ NOT STORED. Counts and the game build are PULLED:
   `--emit-counts`, `--emit-fingerprint`. A stored number goes stale in silence.

Everything else is pull: `SESSION_LOG` (history), `agent/reports/` (evidence),
`agent/bugs/` + `agent/facts/` (module/fact truth), git graves.

## The admission door — every section, all four tests

Carried from the fix pack's `prompts/perma/STATE_EVICTION.md` on 2026-09-17 (owner ruling there,
2026-09-15; donor @ `e6ec192`). It **replaces** the per-line hazard test in section 2 above
and extends to every section: a section name grants no admission.

**A line enters STATE only by passing ALL FOUR tests. AND-ed, never OR-ed. One failure is enough.**
A pass on one test cannot rescue a failure on another, and applying a subset is not an admission
review. Required structural text and protected parser dependencies are identified explicitly, never
waved through as passing status.

**1 · HARM — name the victim.** Who is worse off, and can the next command make them whole? A
mechanism is not a victim. Floor: moderate. A silent harm outranks a loud one of the same size.
"Files get deleted" is not harm if nobody wanted them.

**2 · REACH — both halves must answer *everyone*.**
- **(a) Whose job is this?** If you can name a role, it belongs in that role's doc.
- **(b) Who needs to know this?** Not everyone means it belongs where they are. **Self-consuming
  chain work never passes (b)** — by construction its knowledge dies with the chain. Do not weigh
  that class case by case.

A destructive rail is role-gated by construction. An epistemic rail that binds every session can
pass both halves; it still needs the other two tests. An unfinished task for one role fails reach
even while its status can change.

**3 · GATE — can a machine catch it?** Then cite the gate instead of restating the duty. If a
machine *could* and nothing does, the entry is a placeholder and the real deliverable is the check.
A placeholder still needs the other tests; when the check lands, the restated duty leaves.
*Worked example, 2026-09-17:* the wrap-site allowlist and the load-order constraints were two
multi-line STATE entries; doccheck prints both every run, so they collapsed to one line naming the
gate and the file that holds the list.

**4 · VOLATILITY — can the thing's state still change?** Settled means it is a record, not state.
Receipts, tombstones, immutable facts and closed chains do not become status by passing harm, reach
or gate. The *current* version can change; when it changes, the previous version changes too. A
line that moves only when another STATE line moves is still state; a line that never moves is not.
Passing volatility alone does not admit anything.

## Procedure

1. Read STATE.md whole. Read the newest SESSION_LOG entry to match its voice.
2. Note the current HEAD sha — it becomes the grave:
   `git show <sha>:docs/agent/STATE.md` is the full pre-eviction file, forever.
3. Prepend ONE SESSION_LOG entry (below the preamble; archive entries are
   never edited): a digest of each closed effort being evicted — a few lines
   each, dated, with pointers to its reports/graves — opening with a
   `tags:` line listing every D##/EF-###/item-## the entry touches, so
   future greps land here. **Move, never delete: every evicted claim must be
   closed, or have a home + pointer.**
4. Rewrite STATE.md to the kernel. Keep the mandatory-read header, the grave
   pointer, and the read-path pointers.
5. Verify: `python tools/doccheck.py` GREEN (it enforces the warn/hard byte
   caps and the per-line cap); every hazard passes the admission test; no
   "superseded"/"⇒" chains remain; open decisions match the checklist; the
   emitted block is byte-identical to `--emit-counts` output.
6. Measure the clean file (bytes; tokens ≈ bytes/2 for emoji-dense prose to
   bytes/4 for plain text) and put the numbers in the report to the owner,
   beside the pre-eviction size.
7. Commit (boring subject) and push.

## Rules

- Fresh context preferred: the evicting session should not be the session
  whose material is being evicted.
- The eviction is judged by what a fresh session NEEDS at boot, not by what
  past sessions were proud of. When in doubt whether something is still
  load-bearing, it stays one more cycle and gets flagged in the report.
- Owner-facing asks follow `CLAUDE.md`'s canonical route and never live only in STATE.
