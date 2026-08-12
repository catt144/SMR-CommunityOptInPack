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
