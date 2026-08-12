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
