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

## 2026-09-01 — the bands report reviewed: held, one gap (EF-074); its findings become facts EF-070–074; the build-design one-off is written

tags: D06 drones facts EF-070 EF-071 EF-072 EF-073 EF-074 review prompts

Review of `reports/DRONE_BANDS_CLEAN_REVERT_20260901.md` against Src, then durability work on
the owner's order ("update all the facts it found so we don't lose anything"):
- **Every SOURCE delta re-verified and HELD** (the `:94` flatten verbatim; class-table functions
  not permanents; the 07-31 experiment widened only the group const; autosave unpaused with ≥4
  yields). **One gap found:** `Drone:ImproveDemandRequest` can trade a tier-chosen delivery up to
  routine band-3 traffic mid-flight (`Drone.lua:766`, `:1013-1014`, `:1164-1175`) — V/P/E need a
  guard; E-8's card gains the assertion. Report §8 addendum; verdict/ranking unchanged.
- **Facts filed** (fix pack first, mirrored here): `EF-070` autosave/quicksave unpaused before the
  persist walk · `EF-071` C reads the `const.TaskRequest` bound, not table keys · `EF-072`
  FindTask's nine inputs + the persist walk's only-route rule · `EF-073` the band lives in the
  queue key · `EF-074` the hijack. `DRONE_PRIORITY_SYSTEM.md` §6 landmine 8 (fix pack commit).
- **D06 tag/row refreshed** — they had said "4 gates owed, playtest FROZEN" for a month after both
  moved (gates answered 07-31, freeze lifted 08-31). Third entry-lags-body instance.
- **`prompts/DRONE_BUILD_DESIGN.md` written** (one-off, self-consuming): design spec + THE tier ×
  demand layout table + build brief, under the owner's hard constraint — no uninstall mod (R3/R7
  hard); branches on whether E-4/E-8 have run; owner ratifies the spec before any build.
Not done: the experiments (owner, checklist 92); any code.

---

## 2026-09-01 — drones: bands 4–5 + clean revert — YES IF (view tiers), two matcher experiments owed; EF-069 filed

tags: D06 drones EF-069 reports checklist-91 checklist-92 checklist-93 desk-only

One-off `prompts/BANDS_CLEAN_REVERT.md` (consumed; `git show ba6c3b7:docs/agent/prompts/BANDS_CLEAN_REVERT.md`).
Desk only — no module touched, no save loaded, no probe run (`PROBE SWEEP: clean`). Report:
`agent/reports/DRONE_BANDS_CLEAN_REVERT_20260901.md` — the evidence delta since 07-31 (23 lines), the
three options and fourteen brainstormed mechanisms each against an 11-row clean-revert rubric, seven
experiment cards with committed predictions, and the verdict.
- **Verdict: YES IF** — "view tiers" (the elevated requests handed to the C matcher in transient mod-built
  tables, tier by tier, before the hub's real tables; nothing widened, nothing persisted) fills every rubric
  row from citations except two matcher cells (E-4, E-8). Bands 4–5 as PERSISTED data: NO (R3/R7 fail by the
  07-31 §9 measurements). Option 2 reverts clean only by table surgery (R10 fails).
- **Three SOURCE findings the record lacked:** (1) the 07-31 v1 experiment (TestKit `f617576`) widened only the
  `const.TaskRequest` group and C still nil-indexed narrow tables ⇒ the matcher reads the group bound, not the
  keys (corroborated by Haemimont's 2018 Lua mirror of the matcher); (2) autosave/quicksave do not pause game
  time and ≥4 yields sit between `SaveGameStart` and `EngineSaveGame` ⇒ tear-down-on-save cannot hold its
  invariant; (3) `RequiresMaintenance.lua:94` copies the class's `GetPriorityForRequest` onto every
  no-maintenance building and class-table functions are not permanents ⇒ a class-level override enters saves
  by value via vanilla — **EF-069** (allocated in the fix pack, mirrored here).
- Fix pack, own commit: EF-069 + INDEX; `DRONE_PRIORITY_SYSTEM.md` corrected in place (§4 a fourth override,
  `RCTransport.lua:217`; §6 landmine 4 amended; §10's "requires a full replacement" withdrawn — a pre-wrapper
  closes the leak); `DRONE_PROJECT_PROMPT.md` §3 pointer; checklist items 91–93.
- Web prior art: no published mod widens the range or overrides the method; the devs shipped and removed a
  one-band maintenance urgency in 2018 (`maintenance_request_is_highest_prio`, field still at `:53`).
Not done: any experiment (owner, item 92); the decision (item 91); D06 entry untouched (plan of record unchanged).

---

## 2026-09-01 — the three stale entries catch up with the fix pack's checklist: D07 and D01 `tested-attended`, D12's tag stops owing P4/P6

tags: D07 D12 D01 STATE reconciliation testing-debt

`WORK_PROMPT.md` session against `STATE.md` "Now" a/b/d (owner 09-01, testing precedes launch).
Desk work only — no game launch, no code touched, no new claim; every flip is a record catching
up with a result the fix pack's `PLAYTEST_CHECKLIST.md` / `archive/` already carried.
- **D07** `built` → `tested-attended`. The tag said E's uninstall half was unrun; the checklist's PT-53
  block has said RAN CLEAN 2026-08-10 (`corun-batch-2` leg T) for three weeks. Re-read the RAW log
  (`cb2uninstall_Mars.exe-20260810-17.20.20.log`): save written with the pack (`Unpersist missing
  permanent: Mod/SMR_CommunityFixPack`), sitting read `CohortHousing: applied`, full restart,
  `pack=0/0 active`, **0 `[LUA ERROR]`**, ~7 min sim. E's precedence half stays UNMEASURED (fixture
  unholdable 08-05; its design question ruled 08-11). Stated on the entry: pre-split run, transfers
  on zero persisted state; §8 ship test still owed. Third time this entry lagged the archive.
- **D12** stays `speced` (owner disposition 08-03 item 2). Tag + row said "P4/P6 owed"; the entry's own
  08-03 re-run section and the checklist's PT-62 header say PASSED (23 → 0, overpop cleared). Owed
  now reads P12 · P13 · P14 · split counter through a landing · longer `Clark #1` watch.
- **D01** `opt-in` → `tested-attended`: PT-55 closed in full 07-30 at the keyboard; the tag had opened
  with `opt-in fix` since 08-01. Bookkeeping, no new claim.
- Fix pack checklist: PT-53's status header now says nothing runnable remains, pointing here.
Not done: anything needing the keyboard (D12 P12–P14 + landing; D06 design decision, checklist 83).

---

## 2026-09-01 — contamination audit: every fix-pack reference sorted, 0 contamination, the l5 lens found mis-renamed

tags: tools WORKFLOW FIX_POLICY item-88 item-89 item-90

One-off (`prompts/CONTAMINATION_AUDIT.md`, consumed; `git show d3d9053:docs/agent/prompts/CONTAMINATION_AUDIT.md`).
Inventory at `d3d9053`: **817 grep hits** over Code/, tools/, docs/ (archive excluded), metadata,
items, README, CLAUDE, LICENSE, .claude — every one classified: **572 HISTORY · 175 POINTER ·
29 CONTRACT · 16 STALE fixed · 4 STALE proposed (Code/ comments, owner) · 21 the prompt's own · 0
CONTAMINATION.** Ban 2 proven by AST, not grep: `luaparser` over all 9 `Code/*.lua`, 2,943 `Name`
nodes walked, **0** carry `SMRFixPack`; the 5 string literals are the persisted names. Every
persisted-looking token in `Code/` is in PROVENANCE §2. Player-visible strings (17 `Untranslated(`
sites, l4's count = grep's) name this mod or no mod.

**Fixed.** `l5_containment.py`: two regexes still said `SMRFixPack` (the 08-31 rename missed them)
so every `SMROptInPack.*` file-scope declaration read `check` — after: check 36→17, no 60→79,
19 rows re-bucketed, nothing else moved. `harvest_wrap_targets.py`: `SMRFixPack` dropped from the
not-a-class set so a stray capture off it would be REPORTED, not skipped (output unchanged).
`l3_save_footprint.py`: only `SMROptInPack` is a `modtable` receiver (output unchanged).
`tools/hooks/pre-commit`: header named the other repo. WORKFLOW/FIX_POLICY: one banner clause each
— bare donor file names (`BUG_LIST_AUDIT.md`, `PLAYTEST_ARCHIVE.md`, `MOD_DESCRIPTION.md`,
`Fix_*.lua`, F-/C-ids, D13 …) resolve in the fix pack, not here — plus inline N/A markers on the
`MOD_DESCRIPTION.md` per-fix bullet, the `90_Loggers.lua` claim (no such file in either repo), the
release-steps "display name is a placeholder" item (DONE 08-13/08-17), the `DRONE_RESEARCH_BRIEF.md`
path, the donor's 08-01 `[FAQ]` list (this repo's re-derived), §4a's F28 history, §6's loc ruling.

**Pass B.** Every tracked file has a recorded reason to be here. 0 ORPHAN. KEPT-N/A confirmed with
markers present: doccheck `--verify-split*`, `split_bugs`/`split_facts` migration halves, the
`DataPatch` runner in `00_Core.lua` (no `Opt_*` caller; `OnDataReady` is live). 1 OWNER:
`FUTURE_IDEAS.md` #9 (a fix-pack feature parked here by analogy, no ruling) → checklist 88.
Also to the owner: 89 (comment-only `Code/` wording, five sites) and 90 (does the 08-02 loc-table
ruling extend to this mod). Nothing in `Code/`, no persisted string and no archived record was edited.

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
