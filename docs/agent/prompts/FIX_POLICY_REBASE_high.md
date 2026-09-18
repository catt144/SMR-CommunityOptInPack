# Rebase `docs/agent/FIX_POLICY.md` on the fix pack's, and cut it to what it requires

**Authored 2026-09-17 at `cdce060`** by the fix-pack coordinator seat. The provenance dissolution
has landed: its source file and prompt-map row are gone, and its persisted-name inventory is now
in this file's §3.

```sh
git log --oneline -8 && git pull && python tools/doccheck.py | tail -1
git -C C:/Dev/SMR-BugFixPack log --oneline -3 -- docs/agent/FIX_POLICY.md
```

## Authority — settled

⚖️ **Owner, 2026-09-17:** this repo standardises on the fix pack (`C:\Dev\SMR-BugFixPack`), which it
was forked from on 2026-08-12. *"Same folder names, same file names wherever possible. The only
things that should be different are the repo specific things"* … *"the same rules and structure
there. The same overall workflow and feel."* And of this file specifically: it *"needs work"*.

⚖️ **OI-09:** agent-facing documents may be machine-tuned hard; content already recorded elsewhere is
deleted, not re-archived. Retire silently — no dated note, no strikethrough, no pointer.

## The measurement

Both files have the same section skeleton (§1, §2, §3/§3a, §4, §4a, §5–§8). Measured at the
authoring sha with `wc -lc`: **this file 713 lines / 46,111 B; the fix pack's 400 / 28,719 B.** The
fix pack's got there on 2026-09-16 (`5c1f001`, 791 → 401 lines, then `60763b9`, a blind check that
found 120/120 obligations present). Read both commit bodies in the fix pack before starting: they
are the method, and the calls they record are the kind you will face. This file never received that
prune, and it also lacks the fix pack's §2a (branch guards) and §2b (pinned-defect manifest).

## End state

1. **Where a section's duty is the same in both repos, the fix pack's current text, verbatim.**
   Do not re-argue the wording; the fix pack's has months of use behind it. Where this file carries
   a clause the fix pack lacks and it is general, it is a proposal to the fix pack: list it in your
   report and cut it here.
2. **What is genuinely about this mod stays, pruned:** §4 (what may be BUILT here), §4a's
   who-benefits test, `Opt_*` module policy, and the persisted-name rows already in §3 —
   ⛔ those rows are save contract and move **byte-identical** (prove it with a diff against the
   commit that landed them).
3. **§4-donor is refreshed, verbatim, to the fix pack's current §4.** A header rule here protects it
   (*"Keep §4-donor verbatim and unedited; it is the fix pack's text…"*), and the fix pack rewrote
   that §4 on 2026-09-16, so the frozen copy already fails the rule's intent. A byte-for-byte refresh
   from the fix pack's HEAD satisfies it; prove it with a diff. Nothing else in §4-donor changes.
4. **§2a and §2b are your call**, per rule: adopt verbatim where they bind a runtime patch here,
   omit with a one-line reason where they are fix-specific. If you adopt one, the header rule that
   lists the sections applied "as the donor wrote them" gains its number in the same commit — the
   one rule-line edit this brief licenses.
5. **Section numbers and cited sub-rule ids stay**, as the fix pack's prune kept them, so citations
   elsewhere survive. Grep this repo for `FIX_POLICY` line citations and repoint any your edit breaks.
6. **Do not touch the `Must_Read_Header` rules block** — the coordinator seat is mirroring the rules
   separately. Prose-level duplicates of a header rule are cut.

**Method, fixed:** before editing, write an inventory of every normative item in the current file
(outside `docs/`: this session's scratch space) and give each a disposition — kept, taken from the
fix pack, homed elsewhere (name the place and check its body, not its heading), or cut with a reason.
After editing, a separate agent or session that sees **only the new file and the inventory** grades every item
PRESENT / WEAKENED / ABSENT, and reports any new obligation. Fix what it finds, and report its
result verbatim in the commit message. You do not grade your own rewrite.

## Scope

**In:** `docs/agent/FIX_POLICY.md`, and citations elsewhere that your edit breaks.
**Out:** `Code/`, `items.lua`, `metadata.lua`, persisted-name values, the rules block, `DECISIONS_OWED.md`.

## Stops

1. A fix-pack passage contradicts a live owner ruling here (`DECISIONS_OWED.md` or a recorded
   `OI-` ruling) — keep this repo's text for that passage and report the conflict.
2. A persisted-name row cannot be shown byte-identical after the move.
3. The rebase would change what a shipping module is allowed to do — that is an owner ruling.

## Do not claim

- ❌ *"Nothing was lost."* ✅ the blind grader's tally against the inventory, with its method.
- ❌ *"Mirrors the fix pack."* ✅ which sections are verbatim, which diverge, and the reason for each.

## Lifecycle

One-off. `git rm` this file and delete its row in `docs/agent/prompts/README.md` in the commit that
lands the result.
