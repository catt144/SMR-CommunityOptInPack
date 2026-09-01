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

## 2026-08-31 (late) — the ported tools are made to survive a Windows console, and stop talking about the other mod

tags: tools

A second session, started from the new prompt, hit `l3_save_footprint.py` dying
with a cp1252 `UnicodeEncodeError` on its own ⭐ line and read its docstrings as
being about the fix pack. Both true: the readiness pass ran every tool under
`PYTHONIOENCODING=utf-8` and never saw the crash, and the donor narrative was
left in place "as history". That session added the stdout guard to seven tools
(uncommitted); this one kept those edits, guarded the remaining six, trimmed the
port headers to one provenance line, rewrote docstrings and printed labels to
this mod's terms, and made `l3 --src` fail fast on a path with no `Lua/` under it
(it had scanned 0 files and reported every field "absent" — a false census). All
13 tools re-run under a plain cp1252 pipe: 0 `UnicodeEncodeError`. The fix
pack's own copies of `l3`/`l4`/`l5` still lack the guard — noted, not touched.

---

## 2026-08-31 — the readiness pass: the fix pack's 19 days of tooling and process are carried across, measured against this tree

tags: D01 D02 D03 D04 D06 D07 D09 D12 EF-008 EF-023 EF-039 EF-051 EF-054 EF-055 EF-056 EF-057 EF-058 EF-061 EF-062 EF-068 item-83 item-84 item-85 item-86

**Asked (owner):** how ready is this workspace for work, and which of the fix
pack's tools, tests, auditing, chain method and processes belong here. **Answer:**
`agent/reports/READINESS_REVIEW_0831.md`; port ledger `agent/PROVENANCE.md` §6.

**Measured before the pass.** doccheck GREEN, hook set, tree clean, `main ==
origin/main` — and every improvement the fix pack made after the split absent:
doccheck 4 checks behind (byte budget, `tested-attended`, load order, the F107 wrap
check); 14 of 20 tools missing; WORKFLOW/FIX_POLICY/CHAIN_METHOD behind their
donors; `prompts/` empty; **the two fact sets had COLLIDED** — this repo minted
`EF-057`/`EF-058` on 08-16 for facts the fix pack holds as `EF-061`/`EF-062`, while
its own `EF-057`/`EF-058` are different facts; 7 shared facts were updated there and
never carried. STATE's counts block said 94 probes (doccheck: 100) and its line 28
had grown to 1,734 bytes.

**Carried.** doccheck v5 (the four checks); `harvest_wrap_targets` (namespace);
`upload_preflight`, `pack_list`, `flpk_extract`, `l7_env_map` verbatim;
`pack_predict` (prefix); `l3`/`l4`/`l5`/`l6`×2/`audit_preset_fields`/`l8_hostile_input`
(token rename, module lists); `l2_reload_sim` REWRITTEN for this repo's one measured
lifecycle defect. Facts re-synced whole from `bec2e06` (68). CHAIN_METHOD verbatim.
WORKFLOW: byte-budget rule 8, "Release marking — tags, not branches" (`optin-`),
release-step bullets 7–8, the 08-24 probe rule, the EF-id allocation rule.
FIX_POLICY §2: F107 + F110. `prompts/DISPATCH.md`, `STATE_EVICTION.md`.
`.claude/settings.json`. STATE.md rewritten to the kernel (one fact per line).

**Found by running the instruments here.** `upload_preflight`: **1 FAIL** — no
`image`/`preview.png`, the portal rejects before packing. `harvest --check`: 3
capture+install sites with no Require pair (`Opt_DroneOverhaul` ×2, `Opt_MultipleSuns`);
each captured class DECLARES the method at Src (Drone.lua:879, _TaskRequest.lua:72,
SolarPanel.lua:8) → benign, allowlisted with citations, Require additions routed to
the owner. `l2_reload_sim --strict`: **PASS**, 8 register once across a reload;
**control REPRODUCED** — the pre-guard core (`2cedf7d~1`) yields 16 order entries,
the 08-17 "NoHomeless, NoHomeless" mechanism. `l3` §3: exactly PROVENANCE §2's five
persisted names, no GameVars. `l8`: hostile `SMROptInPack = true` / `_Disabled = true`
kill module files — identical to the donor's L8 on the same Core; adjudication
inherited. `l6_promise_map`: identity 8/8, package lists equal and ordered.
`audit_preset_fields`: 0 preset-field writes.

**TestKit — surveyed, FILED, not edited** (shared kit; edits need a launch): 9 opt
probes not 8 (`ClassicRockets` is in wave 3); D06 has no `RunAll` probe; no
opt-only run mode; `98_EnablePathLeg` hardcodes the fix pack's id; `FixtureCarry`
blind to D09's modifiers; only D12 clause 1 is a vanilla control.

**Owner decisions raised** (fix pack checklist, R10): 83 kit edits · 84 Require
pairs · 85 preview art · 86 ratify EF-id allocation. Nothing was pushed to a portal;
no module's behaviour changed; no Lua under `Code/` was edited.

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
