# Session log — append-only, newest first

⛔ **Append-only. Never edited, never reordered, never deleted.** Current state
belongs in `docs/agent/STATE.md` (rewritten in place); this file is what
happened, in the order it happened.

⚠️ **This log starts at the split.** Everything before 2026-08-12 happened in
`C:\Dev\SMR-BugFixPack` and its `docs/archive/SESSION_LOG.md`, which does NOT
move — history stays where it happened. The eight modules here carry years of
that history in their entries (`docs/agent/bugs/`) and in the fix pack's
archive; `docs/agent/PROVENANCE.md` is the bridge between the two records.

---

## 2026-08-12 — the split chain's terminal audit SUSTAINS this repo, and the no-retraining test passes from these files alone

**The audit (run from the fix pack's chain folder, which it emptied at close)
re-derived every claim this repo's STATE makes** — all nine matrix logs
byte-compared identical and read whole; every suite tally recounted from verdict
lines; the standalone claim re-proven by the auditor's own greps (this mod `8/8`
with `SMRFixPack` nil in the process; the fix pack `74/74` with `SMROptInPack`
nil); all five persisted names re-derived from THIS repo's shipped `Code/` and
matched name-by-name to the save readings (three instance flags read off 4 real
saves; both dial modifier ids read with their own `prop`/`percent`/`amount`
fields; cell (e)'s write→save→reload returned identical handle sets, 0 of 3
fields broke); `EF-055`'s junction route re-derived from Src leg by leg. The one
in-game ERROR of the whole matrix was a TestKit fixture gap (repaired in the
kit), not this mod. **The WORKFLOW both-mods clause is now ACTIVE** (twin
activated in the fix pack the same close).

**The no-retraining acceptance test (owner requirement 3) — run with the fix
pack's docs closed, answered from THIS repo alone, every answer cited:**

1. *Build state?* → `docs/agent/STATE.md` counts block (8 registered / 9
   `Code/*.lua` / 88 shared probes / 0 F + 9 D + 0 C), emitted by
   `python tools/doccheck.py --emit-counts`, which ran GREEN here during the test.
2. *Policies — fix, doc, probe hygiene?* → `docs/agent/FIX_POLICY.md` (adapted
   copy whose header ledger names exactly what changed vs the donor — §4
   inverted, namespace renamed, §3's field-prefix rule deliberately NOT renamed)
   and `docs/agent/WORKFLOW.md` (probe-hygiene hard gate, `TEMPORARY` sweep,
   ARM gate, leg-design rules — all present in the adapted copy).
3. *Each module's record and where its history lives?* →
   `docs/agent/bugs/INDEX.md` (9 rows, statuses); each entry carries
   `donor_seq`/`donor_row` and a `from:` line naming the donor file AND sha
   (verified on D09: `from: SMR-BugFixPack docs/agent/bugs/D09.md @ 0efb87e`);
   `CLAUDE.md`'s split note says pre-split history stays in the donor repo.
4. *How to run the suite and read a gate?* → `docs/agent/PROVENANCE.md` §4
   ("How to run the suite"), written for exactly this question: junction
   install recipe pointer, the shared-TestKit location, `SMRTest.RunAll()`'s
   two gate lines, `SMROptInPack.ListFixes()`, and the full-bracketed-token
   grep rule. `docs/agent/WORKFLOW.md` "Install for testing" carries the recipe.
5. *What is banned?* → `CLAUDE.md`'s two bans (persisted renames; `SMRFixPack`
   references in executable code) + `docs/agent/STATE.md` gates (no behaviour
   change; `Opt_DroneOverhaul` frozen per PT-52).
6. *Provenance of every ported artifact?* → `docs/agent/PROVENANCE.md` §1 (the
   port ledger, per file, with shas), §2 (the persisted-name inventory), §3
   (placeholder display-name sites), §5 (what the fix pack kept and lost).

**Verdict: PASS — no answer required the donor repo.** One deliberate
exception stands and is documented where it belongs: owner decisions are
single-sourced in the fix pack's `PLAYTEST_CHECKLIST.md` (`CLAUDE.md` says so,
with the reason in `docs/README.md`) — that is a design choice, not a gap.

**Standing state after the audit:** the rig's NORMAL config is BOTH mods loaded
(measured baseline `74/74` + `8/8` · `78/0/10/0` of 88, WORKFLOW clause active);
the owner's re-tick is spent (dials `5x`/`+2`); open owner calls (display name,
default-OFF ratification, GitHub remote) live on the fix pack's checklist.
**NEXT for this repo: nothing owed by it.** The D13 chain (one save-rescue
artifact covering BOTH mods) runs from the fix pack and will read this tree.

---

## 2026-08-12 — the modules and their records arrive; the repo is a complete mod (commits 2-4)

`00_Core.lua` ported under `SMROptInPack` (whole-file token rename FIRST, then
five literal adaptations — the QA gate's MUST-FIX 1: `:270`/`:384` read the veto
table by NAME and a literal copy would have nil-indexed at every `Register` with
the fix pack absent). Then the 8 modules, namespace edits only, every file's
line count unchanged. Then `metadata.lua`/`items.lua`, with all nine
`default_options` keys and the whole option-item block lifted byte-for-byte out
of the donor — account contract, never retyped. Then the nine entries
(D01–D07, D09, D12), bodies byte-preserved, renumbered `seq`/`row` 1..9 with the
donor's numbers kept as `donor_seq`/`donor_row`; the fix pack keeps a tombstone
at each id.

⛔ The save contract was CHECKED, not assumed: the port classified every
`SMRFixPack_*` token before renaming anything and counted each persisted name
before and after — all five identical.

Two sites the design's disposition table had not listed, found by reading:
`Opt_DroneOverhaul` carries its OWN cloned logger with its own
`[CommunityFixPack]` literal, and two modules name the mod in player-visible
infopanel rollover titles. Both adapted; both recorded for the terminal audit.

⚠️ Deviation with its ruling: the design specified version fields `0/1/0`, which
under its own field order reads 1.0.0, not the "pre-release" the same sentence
asks for. Built as **0.1.0**. `PackVersion` is unused by all eight modules.

Static acceptance only — parse sweeps, doccheck green, counts matching the
design's predictions exactly (9 / 8 / 7 / 1). **Nothing has been launched.**

---

## 2026-08-12 — the repo exists (chain `split-optins`, prompt 3, commit 1)

Scaffold only: `CLAUDE.md`, the doc map, `STATE.md`, `PROVENANCE.md`, adapted
`WORKFLOW.md` + `FIX_POLICY.md`, `reports/CHAIN_METHOD.md`, the whole
`agent/facts/` copy (53 facts + EF-054, written the same session and living in
both repos), and the ported `tools/` with hooks enabled. **No `Code/`, no
`metadata.lua`, no `items.lua`** — the framework and the 8 modules land in the
next commits of the same session, and `STATE.md` says so in the open.

Source: `SMR-BugFixPack` @ `33d69f5`, TestKit @ `d8e1fbf`. Ported `doccheck.py`
carries four deliberate differences from the donor's (its own v4 docstring
lists them), one of which is a real arithmetic repair the donor also needed:
the optional-module count was a bare substring match that also hit a COMMENT,
and `default_active` was a hard-coded constant.
