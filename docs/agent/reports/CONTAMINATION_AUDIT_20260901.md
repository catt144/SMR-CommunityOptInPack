# Contamination audit — 2026-09-01: every fix-pack reference in this repo, sorted into one of five classes

**Prompt:** `docs/agent/prompts/CONTAMINATION_AUDIT.md` (one-off, consumed by this commit —
`git show d3d9053:docs/agent/prompts/CONTAMINATION_AUDIT.md`). **Tree audited:** `d3d9053`
(the prompt's own commit; `git pull` = already up to date). **Method:** one grep inventory
(§A, pasted verbatim), every hit classified by an explicit per-file/per-line rule set (§B, the
script's output), the ban-2 question answered by a `luaparser` AST walk rather than by grep, and
a second pass over `git ls-files` asking *why is this here* of everything that did not originate
in this repo's own work.

⚠️ Reports are not authority. Where this disagrees with `agent/bugs/`, `agent/facts/`,
`WORKFLOW.md`, `FIX_POLICY.md` or `PROVENANCE.md`, those win.

## 1 · The answer, in the only form the prompt allows

**817 hits, all classified. 0 CONTAMINATION. 16 STALE fixed (+ 12 out-of-inventory stale lines
marked, §3). 4 STALE proposed (comment-only, `Code/`, owner item 89). 29 CONTRACT, every one a
§2 name. 175 POINTERs allowlisted (§6). 572 HISTORY. 21 hits are the prompt's own text.**

| class | hits | provenance |
|---|---|---|
| HISTORY | 572 | MEASURED (grep) + SOURCE (each file's banner/front matter read) |
| POINTER | 175 | MEASURED + SOURCE (each target resolved under `C:\Dev\SMR-BugFixPack`, §6) |
| CONTRACT | 29 | MEASURED (regex over the five exact names; every occurrence ⊂ PROVENANCE §2 rows 1–5) |
| SELF-PROMPT | 21 | MEASURED (the prompt file, deleted in this commit) |
| STALE-FIXED | 16 | MEASURED before/after (§3) |
| STALE-PROPOSED | 4 | INFERRED (comment wording in `Code/`; module edit = owner) |
| **CONTAMINATION** | **0** | MEASURED (AST, §2.1) + SOURCE (every player string read, §2.6) |
| total | 817 | |

Per-file breakdown and the per-hit table: §B. Not claimed: "clean", "zero references", anything
about the fix pack repo's own state (§8).

## 2 · Pass A — the contamination sweep, surface by surface

### 2.1 `Code/` — 73 hits: 11 CONTRACT, 58 HISTORY, 4 STALE-PROPOSED (comments), 0 CONTAMINATION

**Ban 2, proven by AST (MEASURED).** `luaparser` 4.1.0 parsed all 9 `Code/*.lua`; the walk
visited **2,943 `Name` nodes** (identifiers in executable position: variables, fields, function
names) and found **0** containing `SMRFixPack`. Control: 90 `Name` nodes contain `SMROptInPack`,
so the walker sees names. **5 `String` nodes** contain the token — the five persisted names.
Script: this session's scratchpad `ast_ban2.py`; re-derivable in one line per file:
`[n.id for n in ast.walk(ast.parse(src)) if isinstance(n, astnodes.Name) and "SMRFixPack" in n.id]`.

**Persisted-name census (MEASURED, regex over every line incl. comments):**

| token | code lines | comment lines | in PROVENANCE §2? |
|---|---|---|---|
| `SMRFixPack_ack_notworking` | `Opt_AcknowledgedWarnings.lua:68` | `:58` | row 1 ✓ |
| `SMRFixPack_closed_to_new_residents` | `Opt_ResidencyControl.lua:67` | `:60`, `Opt_NoHomeless.lua:52` | row 2 ✓ |
| `SMRFixPack_no_homeless` | `Opt_NoHomeless.lua:205` | `:53`, `:197` | row 3 ✓ |
| `SMRFixPack_DroneSpeedDial` | `Opt_DroneStatDials.lua:64` | `:48` | row 4 ✓ |
| `SMRFixPack_DroneCarryDial` | `Opt_DroneStatDials.lua:65` | `:48` | row 5 ✓ |
| `SMROptInPack_Disabled` / `_Optional` | 39 sites | — | §2 "provably never persisted" (plain `_G` tables) ✓ |

= 5 definitions + 6 comment lines, exactly STATE's gate line. **No persisted-looking name exists
outside §2** — no `GameVar(`, no named thread, no other `SMRFixPack_*`/`SMROptInPack_*` token
(`l3_save_footprint.py` §3 reads the same five; its output is byte-identical before and after
this session's edit to it).

**The 58 HISTORY hits** are F-ids/C-ids and donor module names inside comments that describe a
lesson (`F87`, `F75`, `F64`, `F86 Site 2`, `Fix_LastTransmissionStorage` as the DataPatch donor,
`Fix_SecondArtificialSun` absorbed into D04 …), the three `MIRRORED 2026-08-20 from the fix pack`
notes, and the mod's own display name in 11 header/dialog/rollover sites (it contains "Fix Pack"
by owner decision — counted POINTER in §B, see 2.6).

**The 4 STALE-PROPOSED hits** say "the pack" meaning this mod: `00_Core.lua:497` ("from the
pack's target-changed/install-failed conventions"), `:536` ("never claims the rest of the pack is
verified"), `:558` ("print what the pack did this session"), `Opt_ResidencyControl.lua:63` ("with
the module (or the pack) removed"). Plus one out-of-inventory comment found by the `[FAQ]` grep:
`Opt_NoHomeless.lua:319` points FAQ guidance at the fix pack's frozen `MOD_DESCRIPTION.md`. All
comment-only; all correct in meaning to a reader who applies WORKFLOW's "read 'the pack' as 'this
mod'"; **none edited** (a module-file edit is the owner's — checklist 89).

### 2.2 `metadata.lua` / `items.lua` — 13 hits: 5 POINTER, 8 HISTORY, 0 CONTAMINATION

POINTER: the title (`:13`), the description's and short description's "Works with or without
the Relaunched Fix Pack" (`:14`, `:15`), `last_changes` "split out of the Relaunched Fix Pack"
(`:19`), and `items.lua:2`'s Mod-Options path naming this mod (SOURCE: all four strings read in
full; each names THIS mod or the sibling as a separate product). HISTORY: the rename/split/
`ignore_files` comments (`:5,6,11,16,39,46,82`, `items.lua:3`). CONTRACT rows 6–9 (the nine option
keys and the seven choice strings) are present byte-for-byte in both files (MEASURED against
PROVENANCE §2) — they do not carry the `SMRFixPack` token and so do not appear in the grep.

### 2.3 `tools/` — 91 hits: 4 STALE-FIXED, 27 POINTER, 60 HISTORY, 0 CONTAMINATION (+1 fixed outside the inventory)

| file | verdict | detail |
|---|---|---|
| `l5_containment.py:109`, `:174` | **STALE → FIXED** | MEASURED: `SAFE_RHS` and the `decl-fn` test still said `SMRFixPack` — the 08-31 token rename missed both regexes, and the comment two lines above (`:106`) already said `SMROptInPack.*`. Effect before the fix: every `function SMROptInPack.X()` and `local x = SMROptInPack.Y` at file scope was bucketed `check`. After: **`throw risk: call=10, check=36→17, no=60→79`**; exactly 19 rows left the "needs a source read" list (14 `decl-fn`, 3 `local`, 1 `field-assign`, 1 `onmsg`), no other line of the output moved |
| `harvest_wrap_targets.py:178` | **STALE → FIXED** | `_NOT_CLASSES` listed `SMRFixPack` as a known non-class, so a stray `local prev = SMRFixPack.X` capture would have been SKIPPED silently. Removed; in this repo such a capture is a ban-2 breach and must surface. `--check` output byte-identical before/after (MEASURED) |
| `l3_save_footprint.py:188` | **STALE → FIXED** | a `SMRFixPack…` RECEIVER (a write INTO the other mod's table) was bucketed `modtable` beside this mod's own. Now only `SMROptInPack` is; a foreign receiver falls through to the visible default bucket. The persisted-NAME regex `NAMED_STATE` (`:95`) keeps both prefixes on purpose (PROVENANCE §6) — POINTER. Full output byte-identical before/after (MEASURED) |
| `tools/hooks/pre-commit:2` | **STALE → FIXED (out of inventory)** | header read "SMR-BugFixPack pre-commit hook"; the file has no extension so the inventory's `--include` globs never saw it. Label now names this repo and its VERBATIM provenance |
| `doccheck.py` | KEPT-N/A markers CONFIRMED | `--verify-split` / `--verify-facts-split` (`:744`, `:749`) say "N/A in this repo (kept from the donor)"; `GENERAL_USE_PROMPT.md` cap (`:19-20`, `:89-96`) says single-sourced in the fix pack; the MOVED-stubs clause (`:98-103`) says DROPPED, not faked; `TESTKIT` default path (`:61`) and the printed SHARED note (`:559`) are POINTERs to the shared kit. F97/F107/`- 7` comments describe the donor defect that motivated a check = HISTORY. `BUGS = …/BUGS.md` (`:64`) is referenced only by the N/A `--verify-split` path (SOURCE) |
| `split_bugs.py`, `split_facts.py` | KEPT-N/A markers CONFIRMED and accurate | docstrings (`:9-19` / `:9-14`) name the live halves doccheck imports and mark the migration halves N/A; the frozen tables (`STRUCTURAL`, `HEADLESS_ROWS`, `GROUPED_FILES`, `EXPECTED_ORPHANS`) are inside that marked block — 13 hits POINTER. `split_bugs.py:576` is this repo's own index-header prose |
| `l6_reachability.py`, `l5` §3 header, `l6_promise_map.py:135`, `pack_predict.py:11`, `upload_preflight.py:3`, `l2_reload_sim.py:14`, `harvest…:7,143-168`, `doccheck` traps | HISTORY | donor defect ids used as shape vocabulary ("F28 shape", "F85 shape", "the F87 shape") — the same ids FIX_POLICY/WORKFLOW bind rules to here; a comment naming the measurement's origin (`SWEEP_LEDGER.md` seed note); provenance lines. INFERRED: shared vocabulary, not a label about the other mod |
| `l7_env_map.py:58` | POINTER | usage example points at the shared TestKit tree |
| 9 × `# Provenance: carried from the fix pack 2026-08-31` | HISTORY | one line each, per the 08-31 hardening |

### 2.4 Live instructions — `WORKFLOW.md` 65, `FIX_POLICY.md` 68, `README.md` 4, `STATE.md` 19, `CLAUDE.md` 9, `prompts/` 33, `PROVENANCE.md` 37, `.claude/settings.json` 4

Every hit read in context against the question *would a session following this line do
something that belongs to the other mod?* (SOURCE: both files read whole).

- **WORKFLOW.md** — 37 POINTER (the ADAPTED banner's own rules; Layout's companion-repo,
  junction and TestKit paths; the BOTH-MODS-LOADED clause and its measured baseline; Release
  marking's tag prefixes and the ④ sheet; the release-steps ADAPTED items), 24 HISTORY (F-/C-id
  lessons inside verbatim harness rules), **4 STALE-FIXED** (`:989` the ADAPTED item 2 that still
  called the display name "a placeholder" and "this mod's release blocker" — DONE 08-13/08-17,
  now struck and marked; `:1160-1161`, `:1169` the `[FAQ]` "currently tagged" list, which is the
  donor's of 2026-08-01 and names F88/D13/`MOD_DESCRIPTION.md` — now marked as the donor's, with
  this repo's list re-derived from `grep -rn "\[FAQ\]"` beside it). **Out of inventory (no token
  on the line) but stale and now marked:** `:190-191` "MOD_DESCRIPTION.md updated in the same
  commit" (N/A here — this mod's player text is `metadata.lua`/`items.lua`); `:295-296`
  "`90_Loggers.lua` … the file exists and is the established home" (FALSE: MEASURED, no such
  file in this repo **or** in the fix pack); `:1033` `DRONE_RESEARCH_BRIEF.md` (a THIS-mod
  obligation — D06 lives here — whose spec is in the fix pack's archive; path qualified). Bare
  donor file names cited by verbatim clauses (`BUG_LIST_AUDIT.md` `:369`, `PLAYTEST_ARCHIVE.md`
  `:675`, `AUDIT_FINDINGS.md` `:204`/`:1018`, `PRIOR_ART_SURVEY.md` `:1042`, `CORUN_RIG_SPEC.md`
  `:808`, `MOD_DESCRIPTION.md` `:1022`/`:1046`, the "~29 full replacements" count `:203`) are
  covered by **one new banner clause (6)** rather than 9 inline edits — nothing deleted.
- **FIX_POLICY.md** — 27 POINTER (banner rules; §3's marked `SMRFixPack_` note; §4/§4a/§5/§8's
  adapted text naming the fix pack as the other product; §4-donor verbatim), 33 HISTORY (F-id
  lessons), **8 STALE-FIXED**: `:186`, `:296`, `:305`, `:372`, `:652-653` bare `Fix_*` /
  `F98.md` names → covered by **new banner item 5**; `:576` §4a's "Why this exists — the pack
  shipped `Fix_ReplaceTechCount`" where "the pack" IS the fix pack (the §4a note says to read
  "this pack" as "this mod", which would invert this paragraph) → inline marker; `:660` the
  2026-08-02 "the pack WILL ship `ModItemLocTable`" ruling, given about the fix pack twelve days
  before the split → marked UNASKED for this mod, owner item 90.
- **README.md (docs), STATE.md, CLAUDE.md, prompts/DISPATCH · WORK_PROMPT · STATE_EVICTION,
  .claude/settings.json** — all POINTER or HISTORY: every one names the fix pack as the other
  product, points at the single-sourced checklist/help/prompts, or states the two bans. The four
  `settings.json` allowances are read-only `git` commands in the sibling repos — WORKFLOW's
  co-run close-out rule ("`git status` in BOTH repos") needs them. `CLAUDE.md:3,6,20,23` are the
  rename/split history. 0 STALE.
- **PROVENANCE.md** — the ledger: 37 hits HISTORY except the §2 table's five exact names
  (CONTRACT, 5). It IS the record of what came from where; nothing in it instructs.

### 2.5 Records — `bugs/` 125, `facts/` 156, `reports/` 87, `FUTURE_IDEAS.md` 38: HISTORY, 0 CONTAMINATION

F-ids, C-ids, `Fix_*` names, `[CommunityFixPack]` log lines, `SMR_CommunityFixPack` in a
measured load order, `SMRFixPack.*` in pre-split narrative — all history inside records that
are never edited (SOURCE: `docs/README.md` "records are history"; `_preamble.md` for facts).
CONTRACT occurrences inside records (D02/D03/D06/D09/D12, PROVENANCE §2, EF-002) are the five
exact names cited by the entries that write them — 24 of the 29. Pass-B candidates found here:
`FUTURE_IDEAS.md` #9 (§4, OWNER); `EF-013`/`EF-002` describe the shared framework in the donor's
namespace (§4, BELONGS by the re-sync rule — "amend both or neither").
`READINESS_REVIEW_0831.md:101` carries `SMRFixPack_F35_` — a fix-pack TestKit fixture prefix
quoted as a kit gap; not a persisted name of this mod (HISTORY).

### 2.6 Player-visible strings — every site names THIS mod or no mod (SOURCE, all read)

`tools/l4_player_surfaces.py` TEXT census: **17 `Untranslated(` sites**, 0 `T(`; my grep:
`00_Core.lua` 2 + `Opt_NoHomeless.lua` 7 + `Opt_ResidencyControl.lua` 8 = **17** (MEASURED,
counts agree). The two that name a mod: `00_Core.lua:552-554` (dialog title + "check for a new
version of the Relaunched Fix Pack: Opt-In Modules"), `Opt_ResidencyControl.lua:147` and
`Opt_NoHomeless.lua:747` (rollover titles "… (Relaunched Fix Pack: Opt-In Modules)") — this
mod. The 13 others are policy-row labels naming no mod. `metadata.lua` title/description/
short_description/last_changes: this mod, plus "works with or without the Relaunched Fix Pack"
(the sibling as a separate product — POINTER by the prompt's own table). `items.lua` `Help`
strings: no mod named. Log prefix `[CommunityOptInPack]` at `00_Core.lua:27` and the cloned
logger `Opt_DroneOverhaul.lua:280`; mod-id guards `00_Core.lua:64`, `:441`,
`Opt_DroneStatDials.lua:143` all read `SMR_CommunityOptInPack` (MEASURED). **No player-facing
text names the other mod as if it were this one → no §5 stop condition fired.**

## 3 · Fixes made this session (docs/tools only), each re-run

| file | change | verification |
|---|---|---|
| `tools/l5_containment.py` | `SAFE_RHS` and the `decl-fn` regex: `SMRFixPack` → `SMROptInPack`, with a dated comment | parse OK; output re-run, delta = the 19 rows in §2.3, nothing else |
| `tools/harvest_wrap_targets.py` | `SMRFixPack` removed from `_NOT_CLASSES`, reason commented | parse OK; `--check` output byte-identical; doccheck WRAP CHECK unchanged (0 red, 3 allowlisted) |
| `tools/l3_save_footprint.py` | `modtable` receiver = `SMROptInPack` only, reason commented | parse OK; full output byte-identical (89 lines) |
| `tools/hooks/pre-commit` | header label names this repo + VERBATIM provenance | hook still runs doccheck (GREEN) |
| `docs/agent/WORKFLOW.md` | banner clause 6 (bare donor names + counts are the fix pack's); N/A marker on per-fix bullet 4 (`MOD_DESCRIPTION.md`); N/A marker on the `90_Loggers.lua` claim; release-steps ADAPTED item 2 struck as DONE; `DRONE_RESEARCH_BRIEF.md` path qualified; `[FAQ]` list marked donor's + this repo's re-derived list | doccheck GREEN; nothing deleted |
| `docs/agent/FIX_POLICY.md` | banner item 5 (bare donor names are the fix pack's); §4a "Why this exists" marked fix-pack history; §6 loc ruling marked UNASKED for this mod (item 90) | doccheck GREEN; nothing deleted |
| `docs/agent/STATE.md` | ban-2 gate line gains the AST proof; open-decisions line gains 88–90 | 6,893 B (warn 9,216), every line ≤ 200 B |
| `docs/archive/SESSION_LOG.md` | one entry, newest first, `tags:` line | append-only respected |

**Not edited, by the prompt's fence:** any `Code/*.lua` (§2.1's four comments → owner item 89);
any persisted string; any archived record; `FUTURE_IDEAS.md` (a record; #9 → owner item 88);
any fact (re-sync rule).

## 4 · Pass B — does everything here have a place?

Walked `git ls-files` (135 files). Everything under `docs/agent/bugs/` (9 + INDEX), `facts/`
(68 + INDEX + preamble), the eight `Opt_*.lua`, `metadata.lua`, `items.lua`, `README.md`,
`CLAUDE.md`, `docs/README.md`, `STATE.md`, `PROVENANCE.md` is this repo's own product or its
record — BELONGS, not re-argued. The items the prompt asked about by name:

| artefact | verdict | why (provenance) |
|---|---|---|
| `tools/blocking_analysis.py` | BELONGS | SOURCE: cited by `Opt_DroneOverhaul.lua:92` ("`tools/blocking_analysis.py` reports it `clear`") — D06's F86 Tier-2 record depends on the verdict staying re-runnable (PROVENANCE §1) |
| `tools/audit_preset_fields.py` | BELONGS (negative-evidence instrument) | MEASURED 08-31: 0 preset-field writes here — that "this mod writes no preset fields" is a claim the tool proves on every run; L1/L6/L8 named preset fields as unswept territory (its own header). INFERRED: keep |
| `tools/pack_list.py`, `flpk_extract.py` | BELONGS (launch) | SOURCE: WORKFLOW release-steps ADAPTED item 7 names both for the post-download byte reconciliation; `EF-063` uses `flpk_extract` on language packs |
| `tools/upload_preflight.py`, `pack_predict.py`, `l7_env_map.py` | BELONGS | SOURCE: STATE launch obligation 2 (preflight FAILS on the missing image — the gate); PROVENANCE §6 |
| `tools/l2`…`l8`, `harvest_wrap_targets.py` | BELONGS | SOURCE: PROVENANCE §6 rows, each with what it proves HERE; `l2` rewritten for this repo's one measured lifecycle defect; `harvest` runs inside doccheck |
| `tools/doccheck.py` `--verify-split`, `--verify-facts-split` | KEPT-N/A ✓ | marker present and accurate (`:744`, `:749`, docstring `:34-35`) |
| `tools/split_bugs.py` migration half, `split_facts.py` migration half | KEPT-N/A ✓ | markers present (`:9-19`, `:9-14`) and accurate: doccheck imports `parse_front`/`load_from_dir`/`render_index` every run (MEASURED: INDEX regeneration is GREEN) |
| `tools/hooks/pre-commit` | BELONGS | the commit gate; `git config core.hooksPath tools/hooks` |
| `00_Core.lua` `DataPatch` runner | KEPT-N/A ✓ | MEASURED: no `Opt_*` calls `DataPatch` (`Opt_MultipleSuns.lua:198` calls `OnDataReady`, which shares the trigger plumbing). Markers present: STATE ("the `ctx.heal` clear is pre-emptive (no `Opt_*` calls `DataPatch`)"), `l2_reload_sim.py` docstring, `00_Core.lua:267-269` ("no caller in this repo (measured …)"). PROVENANCE §5's "dormant, not wrong" is about the FIX PACK's `optional` machinery, not this — the recorded position for this repo's runner is the STATE line, and it is still true. The next module to patch a preset needs it (FIX_POLICY §2, the F87 rule) |
| FIX_POLICY §4-donor | BELONGS | SOURCE: banner item 1 — "the test a new proposal still has to fail before it may live here"; marked verbatim/do-not-edit |
| WORKFLOW "Release steps" donor block | KEPT-N/A ✓ (per bullet) | ADAPTED banner items 1–8 say which bullets apply; item 2 was stale and is now struck (§3) |
| `reports/CHAIN_METHOD.md` | BELONGS | method, not content (PROVENANCE §1, §6); WORKFLOW's unattended-chain rule cites its §2.10/§4.0 |
| `reports/DRONE_OVERHAUL_OPTIONS.md` | BELONGS | D06/D09's design study, MOVED here (fix pack keeps a pointer); §I/§K are the owner-routed farm case (STATE 08-16) |
| `reports/SEED_LOGISTICS_HANDOFF.md` | BELONGS | owner ruling 2026-08-16 verbatim in its header: "hand all of this off to the opt in mod" |
| `reports/READINESS_REVIEW_0831.md` | BELONGS | this repo's own evidence (the 08-31 pass) |
| `FUTURE_IDEAS.md` #1–#8, #10 | BELONGS | each carries its routing ruling: the 08-14 move order (#1–#6, #5 re-ruled 08-14 "opt in territory"), 08-15/08-16 rulings (#7), 08-16 on-the-spot ruling (#8), #10 parked as an opt-in design decision (its text says why it cannot enter the fix pack) |
| **`FUTURE_IDEAS.md` #9** | **OWNER** | SOURCE: titled "for the FIX PACK"; its own routing sentence is an analogy ("same routing as #5"), and the 08-14 order covered "anything that's possible opt ins" — a per-fix toggle page for the fix pack is neither an opt-in module nor a bug. It also carries a fix-pack release rider (`MOD_DESCRIPTION.md` "in the console") and cites `agent/prompts/COVERAGE_SWEEP_SMRCF.md`, deleted in the fix pack at `2d2cae1` (MEASURED). Proposed dispositions: keep here / move to the fix pack's `FUTURE_IDEAS.md` / delete — **checklist 88** |
| facts whose summary names the framework in the donor's namespace (`EF-013` "every fix goes through `SMRFixPack.Register`", `EF-002` rows) | BELONGS (verbatim copy) | SOURCE: `docs/README.md` — facts describe the game/engine and are shared; the re-sync rule ("amend both or neither", `_preamble.md`) forbids a local rename. Read with CLAUDE.md's translate-mentally note. Not a Pass-B candidate: the fact is about the registry this mod also runs |
| `.claude/settings.json` | BELONGS | six read-only `git` allowances in the three sibling repos; WORKFLOW's close-out rule requires `git status` in both |
| `README.md` (mod-facing), `LICENSE` | BELONGS | name this mod; LICENSE's NOTICE about `-- FIX`-marked copied lines is true here (MEASURED: 8 `-- FIX` lines across `00_Core`, `Opt_DroneOverhaul`, `Opt_MultipleSuns`) |

**ORPHAN: 0. OWNER: 1 (#9). KEPT-N/A: 4, all with accurate markers.** Nothing was removed.

## 5 · Owner items raised (mirrored on the fix pack's `PLAYTEST_CHECKLIST.md`, R10)

- **88** — `FUTURE_IDEAS.md` #9 routing (keep here / move / delete).
- **89** — `Code/` comment-only wording sweep: `00_Core.lua:497`, `:536`, `:558`,
  `Opt_ResidencyControl.lua:63` ("the pack" = this mod), `Opt_NoHomeless.lua:319` (points at the
  fix pack's frozen `MOD_DESCRIPTION.md`). Zero behaviour change, parse sweep after; a module-file
  edit is the owner's.
- **90** — does the 2026-08-02 `ModItemLocTable` ruling (given about the fix pack) extend to this
  mod's 17 `Untranslated(` sites? `FUTURE_IDEAS.md` #4(b) hangs on it.

## 6 · POINTER allowlist — legitimate live references, so the next audit does not re-derive them

All resolved this session under `C:\Dev\SMR-BugFixPack` @ `99f9bb2` (MEASURED, `test -e`):

| pointer | where it is cited here | resolves |
|---|---|---|
| `docs/PLAYTEST_CHECKLIST.md`, `docs/PLAYTEST_HELP.md` (single-sourced) | CLAUDE, docs/README, WORKFLOW reading path 5, STATE, prompts, FUTURE_IDEAS | ✓ |
| `docs/UPLOAD_WORKFLOW.md`, `reports/RELEASE_PORTAL_PREP.md` | DISPATCH route table, WORKFLOW release marking | ✓ |
| `prompts/GENERAL_USE_PROMPT.md`, `prompts/DRONE_PROJECT_PROMPT.md`, `prompts/RELEASE.md` | WORK_PROMPT, DISPATCH, STATE | ✓ |
| `reports/PARKED_OPTIN_REFERENCES.md` (the restore checklist) | STATE, WORKFLOW item 8, WORK_PROMPT | ✓ |
| `reports/L8_ADVERSARIAL_MAP.md`, `reports/L5_CONTAINMENT_MAP.md` (models) | STATE, `l5` docstring | ✓ |
| `reports/STORE_METADATA_STRINGS.md` | `metadata.lua:11` | ✓ |
| `reports/D13_EXPOSED_SET.md`, `bugs/D13.md` (one artefact covers both mods) | FIX_POLICY §3/§3a, WORKFLOW release steps | ✓ |
| `reports/DOC_RESTRUCTURE_SPEC.md`, `DOC_STRUCTURE_REVIEW.md`, `BUG_LIST_AUDIT.md`, `PRIOR_ART_SURVEY.md`, `REACHABILITY_AUDIT.md`, `SAVE_SAFETY_REDESIGN.md`, `F86_ADJUDICATION.md`, `F86_EXECUTION_PLAN.md`; `archive/AUDIT_FINDINGS.md`, `PLAYTEST_ARCHIVE.md`, `MOD_DESCRIPTION.md`, `DRONE_RESEARCH_BRIEF.md` | verbatim clauses in WORKFLOW/FIX_POLICY (now covered by the banner clauses) | ✓ all present |
| `bugs/C47.md`, `C48.md`, `D10.md`, `D11.md`, `F56.md`, `F84.md`, `F98.md`, `F101.md`, `F104.md`, `F107.md`, `F86.md` | FUTURE_IDEAS, DRONE_OVERHAUL_OPTIONS, SEED_LOGISTICS_HANDOFF, FIX_POLICY | ✓ |
| the shared TestKit `C:\Dev\SMR-BugFixPack-TestKit` (`SMRTest.OptStatus`/`OptMissing`/`FromOptInPack`) | PROVENANCE §4, WORKFLOW Layout, doccheck `TESTKIT`, `l7` usage, prompts' stale-probe gate, `settings.json` | ✓ |
| `EF-` id allocation by the fix pack | WORKFLOW reading path 2, docs/README, WORK_PROMPT | rule, ratify = checklist 86 |
| "works with or without the Relaunched Fix Pack" | `metadata.lua` ×2, `README.md`, CLAUDE, FIX_POLICY §8, WORKFLOW item 5 | player text, deliberate |
| this mod's display name "Relaunched Fix Pack: Opt-In Modules" | `metadata.lua`, `00_Core.lua:1,552,554`, 8 module headers, 2 rollover titles, README, CLAUDE, WORKFLOW install step | owner decision 08-13 + rename 08-17 (PROVENANCE §3) |
| `[CommunityFixPack]` as expected background in this mod's legs | WORKFLOW BOTH-MODS-LOADED, PROVENANCE §4 | owner rule 08-12 |
| fix-pack `archive/*.log` measured baselines | WORKFLOW `:466-469`, DRONE_OVERHAUL_OPTIONS §I/§K, SEED_LOGISTICS_HANDOFF | evidence stays where it happened |

**Pointers that no longer resolve (inside records, so noted, not edited):** `agent/prompts/COVERAGE_SWEEP_SMRCF.md` (FUTURE_IDEAS #9 — deleted in the fix pack at `2d2cae1`); `SWEEP_LEDGER.md` (`pack_predict.py:11`, a measurement's origin note — not found under `docs/agent/reports/` there); `90_Loggers.lua` (WORKFLOW — no such file in either repo, now marked).

## 7 · Inventory gaps (what the grep could not see)

- Files without a matching extension: `tools/hooks/pre-commit` (found by reading `tools/` whole; fixed).
- Stale lines carrying none of the tokens: WORKFLOW `:190`, `:204`, `:295`, `:369`, `:675`, `:806-808`, `:1018`, `:1033`, `:1042`; `Opt_NoHomeless.lua:319` (found by reading the two live docs whole and by the `[FAQ]` grep). A future audit should add `MOD_DESCRIPTION|90_Loggers|PLAYTEST_ARCHIVE|BUG_LIST_AUDIT|AUDIT_FINDINGS|PRIOR_ART_SURVEY` to the token list.
- The `\bC[0-9]{2}\b` token also matches co-run correction ids (`C10`, `C11`) and audit item ids (`C1`, `C2`) that are not bug entries — classified HISTORY on reading, but a count from the grep alone over-reports C-entry citations.

## 8 · What is NOT claimed

- Not "clean" and not "zero references": **817 hits, all classified, 0 CONTAMINATION, 16 STALE
  fixed, 175 POINTERs allowlisted**, with the table in §B.
- Nothing about the fix pack repo's own state beyond "these paths exist there at `99f9bb2`" (§6).
- That any record is wrong for naming the other mod — records are history (§2.5).
- That an ORPHAN was removed — none was found, and nothing but the prompt was deleted.
- A ban-2 verdict from grep — the AST walk (§2.1) is the evidence; the grep is the inventory.
- That the tool fixes changed any verdict a report has relied on: `l3` and `harvest` outputs are
  byte-identical; `l5`'s 19 re-bucketed rows were over-reports of `SMROptInPack.*` declarations,
  and no lens report in this repo has yet been written from `l5` (its docstring says so).

---

## Appendix B · Every hit, classified (script `classify.py`; rules are explicit per file/line)

Text is truncated at 110 characters; the verbatim lines are in Appendix A.

| class | hits |
|---|---|
| HISTORY | 572 |
| POINTER | 175 |
| CONTRACT | 29 |
| SELF-PROMPT | 21 |
| STALE-FIXED | 16 |
| STALE-PROPOSED | 4 |
| **total** | **817** |

| file | CONTRACT | HISTORY | POINTER | STALE-FIXED | STALE-PROPOSED | SELF-PROMPT |
|---|---|---|---|---|---|---|
| `docs/agent/FIX_POLICY.md` | 0 | 33 | 27 | 8 | 0 | 0 |
| `docs/agent/WORKFLOW.md` | 0 | 24 | 37 | 4 | 0 | 0 |
| `docs/FUTURE_IDEAS.md` | 0 | 38 | 0 | 0 | 0 | 0 |
| `docs/agent/PROVENANCE.md` | 5 | 32 | 0 | 0 | 0 | 0 |
| `docs/agent/bugs/D06.md` | 2 | 30 | 0 | 0 | 0 | 0 |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 0 | 30 | 0 | 0 | 0 | 0 |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 1 | 25 | 0 | 0 | 0 | 0 |
| `Code/00_Core.lua` | 0 | 19 | 3 | 0 | 3 | 0 |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 0 | 0 | 0 | 0 | 0 | 21 |
| `tools/doccheck.py` | 0 | 14 | 6 | 0 | 0 | 0 |
| `docs/agent/bugs/D12.md` | 4 | 16 | 0 | 0 | 0 | 0 |
| `docs/agent/STATE.md` | 0 | 0 | 19 | 0 | 0 | 0 |
| `docs/agent/prompts/WORK_PROMPT.md` | 0 | 0 | 18 | 0 | 0 | 0 |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 0 | 18 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-066.md` | 0 | 16 | 0 | 0 | 0 | 0 |
| `tools/split_bugs.py` | 0 | 2 | 13 | 0 | 0 | 0 |
| `docs/agent/facts/EF-023.md` | 0 | 15 | 0 | 0 | 0 | 0 |
| `docs/agent/bugs/D02.md` | 3 | 11 | 0 | 0 | 0 | 0 |
| `docs/agent/bugs/D05.md` | 0 | 13 | 0 | 0 | 0 | 0 |
| `docs/agent/prompts/DISPATCH.md` | 0 | 0 | 13 | 0 | 0 | 0 |
| `docs/agent/reports/CHAIN_METHOD.md` | 0 | 13 | 0 | 0 | 0 | 0 |
| `Code/Opt_NoHomeless.lua` | 4 | 5 | 2 | 0 | 0 | 0 |
| `docs/agent/bugs/D04.md` | 0 | 11 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-002.md` | 0 | 11 | 0 | 0 | 0 | 0 |
| `metadata.lua` | 0 | 7 | 4 | 0 | 0 | 0 |
| `docs/agent/bugs/D09.md` | 1 | 9 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-065.md` | 0 | 10 | 0 | 0 | 0 | 0 |
| `Code/Opt_MultipleSuns.lua` | 0 | 8 | 1 | 0 | 0 | 0 |
| `tools/l3_save_footprint.py` | 0 | 2 | 6 | 1 | 0 | 0 |
| `docs/agent/bugs/D03.md` | 2 | 7 | 0 | 0 | 0 | 0 |
| `docs/agent/bugs/D07.md` | 0 | 9 | 0 | 0 | 0 | 0 |
| `CLAUDE.md` | 0 | 4 | 5 | 0 | 0 | 0 |
| `docs/agent/facts/EF-039.md` | 0 | 8 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/INDEX.md` | 0 | 8 | 0 | 0 | 0 | 0 |
| `Code/Opt_AcknowledgedWarnings.lua` | 2 | 4 | 1 | 0 | 0 | 0 |
| `tools/harvest_wrap_targets.py` | 0 | 6 | 0 | 1 | 0 | 0 |
| `docs/agent/facts/EF-054.md` | 0 | 7 | 0 | 0 | 0 | 0 |
| `Code/Opt_ResidencyControl.lua` | 2 | 1 | 2 | 0 | 1 | 0 |
| `tools/l5_containment.py` | 0 | 3 | 1 | 2 | 0 | 0 |
| `tools/l6_reachability.py` | 0 | 6 | 0 | 0 | 0 | 0 |
| `docs/agent/bugs/D01.md` | 0 | 6 | 0 | 0 | 0 | 0 |
| `Code/Opt_DroneOverhaul.lua` | 0 | 5 | 0 | 0 | 0 | 0 |
| `Code/Opt_DroneStatDials.lua` | 3 | 1 | 1 | 0 | 0 | 0 |
| `docs/agent/facts/EF-055.md` | 0 | 5 | 0 | 0 | 0 | 0 |
| `Code/Opt_ClassicRockets.lua` | 0 | 3 | 1 | 0 | 0 | 0 |
| `docs/README.md` | 0 | 0 | 4 | 0 | 0 | 0 |
| `.claude/settings.json` | 0 | 0 | 4 | 0 | 0 | 0 |
| `docs/agent/facts/EF-006.md` | 0 | 3 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-013.md` | 0 | 3 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-025.md` | 0 | 3 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-028.md` | 0 | 3 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-046.md` | 0 | 3 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-057.md` | 0 | 3 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-063.md` | 0 | 3 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-068.md` | 0 | 3 | 0 | 0 | 0 | 0 |
| `tools/l2_reload_sim.py` | 0 | 2 | 0 | 0 | 0 | 0 |
| `tools/l6_promise_map.py` | 0 | 2 | 0 | 0 | 0 | 0 |
| `tools/pack_predict.py` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-001.md` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-019.md` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-021.md` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-022.md` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-029.md` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-048.md` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-058.md` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-064.md` | 0 | 2 | 0 | 0 | 0 | 0 |
| `docs/agent/prompts/STATE_EVICTION.md` | 0 | 0 | 2 | 0 | 0 | 0 |
| `items.lua` | 0 | 1 | 1 | 0 | 0 | 0 |
| `README.md` | 0 | 0 | 2 | 0 | 0 | 0 |
| `Code/Opt_CohortHousing.lua` | 0 | 0 | 1 | 0 | 0 | 0 |
| `tools/audit_preset_fields.py` | 0 | 1 | 0 | 0 | 0 | 0 |
| `tools/l4_player_surfaces.py` | 0 | 1 | 0 | 0 | 0 | 0 |
| `tools/l7_env_map.py` | 0 | 0 | 1 | 0 | 0 | 0 |
| `tools/l8_hostile_input.py` | 0 | 1 | 0 | 0 | 0 | 0 |
| `tools/split_facts.py` | 0 | 1 | 0 | 0 | 0 | 0 |
| `tools/upload_preflight.py` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/bugs/INDEX.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-004.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-005.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-007.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-008.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-010.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-012.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-014.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-017.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-020.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-024.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-027.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-030.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-034.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-036.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-038.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-040.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-041.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-042.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-044.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-051.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-059.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-061.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/EF-062.md` | 0 | 1 | 0 | 0 | 0 | 0 |
| `docs/agent/facts/_preamble.md` | 0 | 1 | 0 | 0 | 0 | 0 |

| file | line | class | text |
|---|---|---|---|
| `Code/00_Core.lua` | 1 | POINTER | -- Relaunched Fix Pack: Opt-In Modules — core registry. |
| `Code/00_Core.lua` | 61 | HISTORY | -- never guess — an unkeyed restart is exactly F88's defect (F86 Tier 1). |
| `Code/00_Core.lua` | 76 | HISTORY | -- otherwise masquerade as "game update changed it" (how F64 shipped broken). |
| `Code/00_Core.lua` | 166 | HISTORY | -- requires (the F22 donor): plain assignment reaches the real _G through |
| `Code/00_Core.lua` | 191 | HISTORY | -- generalises the Fix_LastTransmissionStorage donor; the F75, B3 and A1 |
| `Code/00_Core.lua` | 201 | HISTORY | -- `run()` at apply time is a NO-OP by design since F87 (see below) — the runner |
| `Code/00_Core.lua` | 208 | HISTORY | --   * ctx.classes_built — nothing runs before flattening (F87); |
| `Code/00_Core.lua` | 211 | HISTORY | --   * ctx.data_loaded — sites gate their missing-target latch on it (the F75 |
| `Code/00_Core.lua` | 223 | HISTORY | -- F87 (2026-07-31): the runner no longer does work at apply time, and it owns |
| `Code/00_Core.lua` | 231 | HISTORY | -- Fix_DustSicknessBiorobots threw exactly there. |
| `Code/00_Core.lua` | 261 | HISTORY | -- MIRRORED 2026-08-20 from the fix pack's `Code/00_Core.lua` (2f077e8), |
| `Code/00_Core.lua` | 262 | HISTORY | -- on the owner's ruling (fix-pack checklist 37 Q1). Same leak as |
| `Code/00_Core.lua` | 274 | HISTORY | -- F87: never before flattening. `g_Classes` is NOT a usable test here — |
| `Code/00_Core.lua` | 285 | HISTORY | -- That is the F87 failure mode (silently unfixed), so own the error the |
| `Code/00_Core.lua` | 301 | HISTORY | -- enable path as "presets not loaded yet" and never fire (the F75 gap again). |
| `Code/00_Core.lua` | 332 | HISTORY | -- WITHOUT the runner's latch/heal contract (F87 sweep, 2026-07-31 — it found |
| `Code/00_Core.lua` | 374 | HISTORY | -- ⛔ MIRRORED 2026-08-20 from the fix pack's `Code/00_Core.lua` (2f077e8), |
| `Code/00_Core.lua` | 375 | HISTORY | -- owner ruling (fix-pack checklist 37 Q1). `Require` marks |
| `Code/00_Core.lua` | 404 | HISTORY | -- ⛔ MIRRORED 2026-08-20 from the fix pack's `Code/00_Core.lua` (2f077e8), |
| `Code/00_Core.lua` | 405 | HISTORY | -- owner ruling (fix-pack checklist 37 Q1). The append below used to be |
| `Code/00_Core.lua` | 497 | STALE-PROPOSED | -- from the pack's target-changed/install-failed conventions. Opt-in state, |
| `Code/00_Core.lua` | 536 | STALE-PROPOSED | -- never claims the rest of the pack is verified; the after-every-patch |
| `Code/00_Core.lua` | 552 | POINTER | Untranslated("Relaunched Fix Pack: Opt-In Modules"), |
| `Code/00_Core.lua` | 554 | POINTER | "%d of this mod's modules found that the game code they patch has changed — usually after a game update — a... |
| `Code/00_Core.lua` | 558 | STALE-PROPOSED | -- Console helper: print what the pack did this session. |
| `Code/Opt_AcknowledgedWarnings.lua` | 3 | POINTER | -- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles |
| `Code/Opt_AcknowledgedWarnings.lua` | 17 | HISTORY | -- is a building entombed by a landscaping lake (F30) — re-nags every 4 game |
| `Code/Opt_AcknowledgedWarnings.lua` | 35 | HISTORY | --     one-shot adds where dismissal already holds — F32 trace). |
| `Code/Opt_AcknowledgedWarnings.lua` | 39 | HISTORY | -- captured as a file-local there, so replacement globals are seen — the F22 |
| `Code/Opt_AcknowledgedWarnings.lua` | 58 | CONTRACT | -- Savegame footprint (FIX_POLICY §3): `SMRFixPack_ack_notworking = true` on |
| `Code/Opt_AcknowledgedWarnings.lua` | 68 | CONTRACT | local FLAG = "SMRFixPack_ack_notworking" |
| `Code/Opt_AcknowledgedWarnings.lua` | 94 | HISTORY | -- mod-load time (the F75 lesson) — do not "verify" the preset here. The |
| `Code/Opt_ClassicRockets.lua` | 3 | POINTER | -- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles |
| `Code/Opt_ClassicRockets.lua` | 21 | HISTORY | -- behaviour get it here, opt-in, so the pack itself stays a pure bug-fix mod |
| `Code/Opt_ClassicRockets.lua` | 53 | HISTORY | -- already answers, including F69's asteroid-lander reserve, falls through |
| `Code/Opt_ClassicRockets.lua` | 60 | HISTORY | -- same machinery as F50, F68, F70 and F71. It is deliberately left for a design |
| `Code/Opt_CohortHousing.lua` | 3 | POINTER | -- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; the |
| `Code/Opt_DroneOverhaul.lua` | 42 | HISTORY | --     preserved for free (the F73 "pre-wrap only" rule is for command bodies |
| `Code/Opt_DroneOverhaul.lua` | 74 | HISTORY | -- ⚠️ F86 SITE 2 — the "saves load identically without it" claim this header used |
| `Code/Opt_DroneOverhaul.lua` | 79 | HISTORY | -- thread, and on the next load without the pack each one threw |
| `Code/Opt_DroneOverhaul.lua` | 87 | HISTORY | -- F86 TIER-2 REPAIR (2026-08-01, owner carve-out pre-granted): the hook moved to |
| `Code/Opt_DroneOverhaul.lua` | 216 | HISTORY | -- Idle itself (F86 Site 2 — see the header). Same trigger, same order, but |
| `Code/Opt_DroneStatDials.lua` | 3 | POINTER | -- Two Mod Options dropdowns (Options → Mod Options → Relaunched Fix Pack: Opt-In Modules): |
| `Code/Opt_DroneStatDials.lua` | 48 | CONTRACT | -- ("SMRFixPack_DroneSpeedDial" / "SMRFixPack_DroneCarryDial") in UIColony's |
| `Code/Opt_DroneStatDials.lua` | 64 | CONTRACT | local SPEED_MOD_ID = "SMRFixPack_DroneSpeedDial" |
| `Code/Opt_DroneStatDials.lua` | 65 | CONTRACT | local CARRY_MOD_ID = "SMRFixPack_DroneCarryDial" |
| `Code/Opt_DroneStatDials.lua` | 76 | HISTORY | -- Pre-flattening rules (ENGINE_FACTS, the F64 lesson — and this module's own |
| `Code/Opt_MultipleSuns.lua` | 3 | POINTER | -- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles |
| `Code/Opt_MultipleSuns.lua` | 19 | HISTORY | -- UIColony.labels). PT-26 (2026-07-27) proved that makes the pack's original |
| `Code/Opt_MultipleSuns.lua` | 20 | HISTORY | -- F39 fix unreachable dead code in an unmodded game: two suns can never |
| `Code/Opt_MultipleSuns.lua` | 30 | HISTORY | --      after DataLoaded — the GlobalMap is EMPTY at mod-load time, the F75 |
| `Code/Opt_MultipleSuns.lua` | 34 | HISTORY | --      at all and this lift used to be skipped for the session — F87). The |
| `Code/Opt_MultipleSuns.lua` | 39 | HISTORY | --   2. BINDING FIX (absorbed from the deleted Fix_SecondArtificialSun.lua, |
| `Code/Opt_MultipleSuns.lua` | 101 | HISTORY | -- FIX (F39, absorbed): the shipped body only ever tested |
| `Code/Opt_MultipleSuns.lua` | 145 | HISTORY | -- "active"), which OnMsg handlers must re-check themselves (the F75 lesson). |
| `Code/Opt_MultipleSuns.lua` | 192 | HISTORY | -- F87 sweep: this used to hang off DataLoaded/DataChanged alone, and neither |
| `Code/Opt_NoHomeless.lua` | 3 | POINTER | -- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; the |
| `Code/Opt_NoHomeless.lua` | 52 | CONTRACT | --     SMRFixPack_closed_to_new_residents (D03) off → children can still migrate in |
| `Code/Opt_NoHomeless.lua` | 53 | CONTRACT | --     SMRFixPack_no_homeless             (D12) on  → graduates are pushed out |
| `Code/Opt_NoHomeless.lua` | 59 | HISTORY | -- outside with no dome dies (F53 territory); that failure mode is made |
| `Code/Opt_NoHomeless.lua` | 153 | HISTORY | -- narrow reading was immune to the CAPACITY-CHURN mechanism (BUGS.md C40) — a |
| `Code/Opt_NoHomeless.lua` | 197 | CONTRACT | -- Savegame footprint (FIX_POLICY §3): `SMRFixPack_no_homeless` on the |
| `Code/Opt_NoHomeless.lua` | 205 | CONTRACT | local FLAG = "SMRFixPack_no_homeless" |
| `Code/Opt_NoHomeless.lua` | 217 | HISTORY | -- `Fix_DustDevilSpawnGate` checks both (`:332-334`), which is why its A/B |
| `Code/Opt_NoHomeless.lua` | 615 | HISTORY | -- Strings are Untranslated (F98, 2026-08-02): re-using a shipped translation id |
| `Code/Opt_NoHomeless.lua` | 747 | POINTER | self:SetRolloverTitle(Untranslated("Dedicated Dome Policy (Relaunched Fix Pack: Opt-In Modules)")) |
| `Code/Opt_NoHomeless.lua` | 808 | HISTORY | -- F100: the old string said "game update changed the Workforce mixin?" |
| `Code/Opt_ResidencyControl.lua` | 3 | POINTER | -- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles |
| `Code/Opt_ResidencyControl.lua` | 24 | HISTORY | -- forced quarantine — the F61 entry records the survey; the pack's earlier F61 |
| `Code/Opt_ResidencyControl.lua` | 60 | CONTRACT | -- Savegame footprint (FIX_POLICY §3): `SMRFixPack_closed_to_new_residents` on |
| `Code/Opt_ResidencyControl.lua` | 63 | STALE-PROPOSED | -- flag loads fine with the module (or the pack) removed. |
| `Code/Opt_ResidencyControl.lua` | 67 | CONTRACT | local FLAG = "SMRFixPack_closed_to_new_residents" |
| `Code/Opt_ResidencyControl.lua` | 147 | POINTER | self:SetRolloverTitle(Untranslated("Residency Policy (Relaunched Fix Pack: Opt-In Modules)")) |
| `tools/audit_preset_fields.py` | 1 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/doccheck.py` | 12 | HISTORY | split, carried across from SMR-BugFixPack @ bec2e06 — (1) STATE.md is |
| `tools/doccheck.py` | 17 | HISTORY | `metadata.lua`'s `code` list are enforced, not just commented; (4) the F107 |
| `tools/doccheck.py` | 20 | POINTER | single-sourced in the fix pack (docs/README.md). |
| `tools/doccheck.py` | 23 | HISTORY | SMR-BugFixPack @ 33d69f5. Four deliberate differences, each recorded in |
| `tools/doccheck.py` | 29 | HISTORY | would have read 67 on the post-split fix-pack side); (3) the three STUBS are |
| `tools/doccheck.py` | 33 | HISTORY | fix pack emits and is labelled so it can never read as a second suite. |
| `tools/doccheck.py` | 60 | HISTORY | # is the SAME number the fix pack's doccheck emits, not a second suite. |
| `tools/doccheck.py` | 61 | POINTER | TESTKIT = os.environ.get("SMR_TESTKIT", r"C:\Dev\SMR-BugFixPack-TestKit") |
| `tools/doccheck.py` | 73 | HISTORY | # defeated — single lines grew into thousand-word walls (the fix pack's hit |
| `tools/doccheck.py` | 92 | POINTER | # the fix pack and only checked if someone ever copies it here. |
| `tools/doccheck.py` | 105 | HISTORY | # Index rows. Trap (a): this pattern also matches a rate table inside the F97 |
| `tools/doccheck.py` | 106 | HISTORY | # entry (`\| F97 \| **50%** (gate fails) \| ...`) — dedupe by ID, keep the FIRST. |
| `tools/doccheck.py` | 110 | HISTORY | # their own `###` sub-headings (e.g. F97's "### THE UNINSTALL LOG..."), so the |
| `tools/doccheck.py` | 121 | HISTORY | # ⚖️ Owner ruling 2026-08-15 (fix-pack checklist 26b), carried 2026-08-31: |
| `tools/doccheck.py` | 546 | HISTORY | # `- 7` was accidentally right only while the pack held exactly 7 gated |
| `tools/doccheck.py` | 559 | POINTER | out.append("NOTE: the TestKit at %s is SHARED with the fix pack — the " |
| `tools/doccheck.py` | 636 | HISTORY | # Provenance of the rules: INHERITED from the fix pack's order, MEASURED as the |
| `tools/doccheck.py` | 703 | HISTORY | """FIX_POLICY §2, the F107 rule (donor 2026-08-24, here 2026-08-31): every |
| `tools/doccheck.py` | 744 | POINTER | "which only exists in SMR-BugFixPack's history") |
| `tools/doccheck.py` | 749 | POINTER | "SMR-BugFixPack's history") |
| `tools/harvest_wrap_targets.py` | 2 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/harvest_wrap_targets.py` | 7 | HISTORY | the fix pack, where the tool was born, had estimated "~60" and measured 105). A hand-typed list is a silent... |
| `tools/harvest_wrap_targets.py` | 143 | HISTORY | # --check: the F107 rule (this repo's FIX_POLICY §2; adopted in the fix pack |
| `tools/harvest_wrap_targets.py` | 150 | HISTORY | # (the fix pack's F107: a module captured a leaf class's method while declaring |
| `tools/harvest_wrap_targets.py` | 158 | HISTORY | # F107 records that limitation); a hit is real. RED means: add the pair to the |
| `tools/harvest_wrap_targets.py` | 168 | HISTORY | # module and sits with the owner (fix-pack checklist, 2026-08-31 items). |
| `tools/harvest_wrap_targets.py` | 178 | STALE-FIXED | _NOT_CLASSES = {"SMROptInPack", "SMRFixPack", "SMRTest", "_G"} |
| `tools/l2_reload_sim.py` | 3 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/l2_reload_sim.py` | 14 | HISTORY | mirrored here from the fix pack's repair (2f077e8) and STATE records it as |
| `tools/l3_save_footprint.py` | 2 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/l3_save_footprint.py` | 17 | POINTER | 3. NAMED STATE   — every `SMRFixPack_*` / `SMROptInPack_*` token: the |
| `tools/l3_save_footprint.py` | 95 | POINTER | NAMED_STATE = re.compile(r'\b(?:SMRFixPack\|SMROptInPack)_(\w+)') |
| `tools/l3_save_footprint.py` | 99 | HISTORY | # second hid two of the fix pack's PostLoadGame passes from the load-order |
| `tools/l3_save_footprint.py` | 188 | STALE-FIXED | if resolved.startswith(("SMROptInPack", "SMRFixPack")): |
| `tools/l3_save_footprint.py` | 278 | POINTER | # (`local FLAG = "SMRFixPack_..."`), so these two scan the code line |
| `tools/l3_save_footprint.py` | 343 | POINTER | print("--- 3. NAMED STATE (persisted `SMRFixPack_*` + framework `SMROptInPack_*`) " + "-" * 8) |
| `tools/l3_save_footprint.py` | 385 | POINTER | # 7. ⭐ MOD-AUTHORED PERSISTED KEYS — the census the `SMRFixPack_*` token |
| `tools/l3_save_footprint.py` | 429 | POINTER | conv = ("SMRFixPack_" in field) or ("SMROptInPack_" in field) |
| `tools/l4_player_surfaces.py` | 2 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/l5_containment.py` | 2 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/l5_containment.py` | 26 | HISTORY | 3. DEFERRED   — the F87 shape: modules whose actual repair work happens AFTER |
| `tools/l5_containment.py` | 38 | POINTER | adjudication belongs in a lens report made by reading the line (the fix pack's |
| `tools/l5_containment.py` | 109 | STALE-FIXED | r"=\s*(\{\|\"\|'\|\d\|true\|false\|nil\|rawget\s*\(\|SMRFixPack[.\[]\|function\b)" |
| `tools/l5_containment.py` | 174 | STALE-FIXED | r"^function\s+(OnMsg\|SMRFixPack)\.", body) else "check" |
| `tools/l5_containment.py` | 274 | HISTORY | print("=== 3 . DEFERRED-WORK (F87) SET — work that happens after apply returns ===") |
| `tools/l6_promise_map.py` | 2 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/l6_promise_map.py` | 135 | HISTORY | QUOTED IN A HEADER counted as a real site — a fix-pack module's header was the |
| `tools/l6_reachability.py` | 2 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/l6_reachability.py` | 5 | HISTORY | The L6 lens question: "Dead-coded targets: is F85 the only one? Its |
| `tools/l6_reachability.py` | 14 | HISTORY | ⛔ A count is a triage instrument, not a verdict. 0 callers is the F28 shape |
| `tools/l6_reachability.py` | 15 | HISTORY | and 1-2 callers is where the F85 shape hides; both are printed for reading, and |
| `tools/l6_reachability.py` | 192 | HISTORY | flag = "  <- ZERO shipped uses (F28 shape)" if uses <= 0 else ( |
| `tools/l6_reachability.py` | 193 | HISTORY | "  <- FEW — read every one (F85 shape)" if uses <= 2 else "") |
| `tools/l7_env_map.py` | 58 | POINTER | python tools/l7_env_map.py --tree ../SMR-BugFixPack-TestKit |
| `tools/l8_hostile_input.py` | 3 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/pack_predict.py` | 2 | HISTORY | # Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| `tools/pack_predict.py` | 11 | HISTORY | seed note in the fix pack's SWEEP_LEDGER.md), `?` is one char. Case-insensitive is NOT |
| `tools/split_bugs.py` | 9 | HISTORY | PORTED 2026-08-12 (split-optins prompt 3) from SMR-BugFixPack @ 33d69f5. |
| `tools/split_bugs.py` | 38 | POINTER | entries carry their own `##`/`###` sub-headings (F97's rate-question |
| `tools/split_bugs.py` | 39 | POINTER | block, D12's "WHAT D12 SHIPS", F86/F87's `> ##` quotes). |
| `tools/split_bugs.py` | 41 | POINTER | FOLLOWS the C41 entry and is not part of it. |
| `tools/split_bugs.py` | 50 | POINTER | 35 INDEX ROWS HAVE NO HEADING OF THEIR OWN — C02 and 34 IDs whose text lives |
| `tools/split_bugs.py` | 53 | POINTER | the generated INDEX can still carry all 151 rows; C02, which has no entry text |
| `tools/split_bugs.py` | 84 | POINTER | # A grouped section's members are its `- **C12 ...` bullets. |
| `tools/split_bugs.py` | 106 | POINTER | {"C02"} |
| `tools/split_bugs.py` | 112 | POINTER | # stated range ("C12-C31") is STALE — it holds C12 through C38 — so the FILE |
| `tools/split_bugs.py` | 114 | POINTER | GROUPED_FILES = {"C03": "C03-C11", "C12": "C12-C38"} |
| `tools/split_bugs.py` | 117 | POINTER | EXPECTED_ORPHANS = {"C02"} |
| `tools/split_bugs.py` | 276 | POINTER | # The F97 rate table also starts its lines with `\| F97 \|`; it lives inside |
| `tools/split_bugs.py` | 428 | POINTER | # C01 and the two grouped headings carry no tag; the row is all |
| `tools/split_bugs.py` | 516 | POINTER | "**C02 has an index row and no entry text anywhere in BUGS.md** (verified", |
| `tools/split_bugs.py` | 576 | HISTORY | "entries moved here from SMR-BugFixPack (split-optins, 2026-08-12); " |
| `tools/split_facts.py` | 9 | HISTORY | PORTED 2026-08-12 (split-optins prompt 3) from SMR-BugFixPack @ 33d69f5. |
| `tools/upload_preflight.py` | 3 | HISTORY | WHY THIS EXISTS (2026-08-17). The fix pack reached its upload sitting with no |
| `docs/agent/bugs/D01.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D01.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D01.md` | 59 | HISTORY | Options → Mod Options since D05, or via the pre-load `SMRFixPack_Optional` override; the |
| `docs/agent/bugs/D01.md` | 73 | HISTORY | citation corrected by the QA audit 2026-07-25) — so there is no refuel spam. F69's asteroid-lander reserve ... |
| `docs/agent/bugs/D01.md` | 78 | HISTORY | means editing the same machinery as F50, F68, F70 and F71 — with no way to test the result |
| `docs/agent/bugs/D01.md` | 105 | HISTORY | auto-offload into rockets — that answer decides whether F56's behavior rides |
| `docs/agent/bugs/D01.md` | 109 | HISTORY | *The export half now also owns F56.* F56 (auto RC Transports never offload rockets) closed |
| `docs/agent/bugs/D02.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D02.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D02.md` | 18 | HISTORY | Spun out of F32's close (2026-07-26, user decision) — read that entry for the full trace. |
| `docs/agent/bugs/D02.md` | 31 | HISTORY | acknowledgment at all. An unfixable building — F30's lake-entombed case is the |
| `docs/agent/bugs/D02.md` | 48 | HISTORY | Ack set persisted as an absent-tolerant `SMRFixPack_*` handle set (policy §3). |
| `docs/agent/bugs/D02.md` | 50 | HISTORY | where dismissal already holds (F32 trace). |
| `docs/agent/bugs/D02.md` | 57 | HISTORY | Notifications.lua, so replacements are seen — F22 precedent): `SuppressNotification` |
| `docs/agent/bugs/D02.md` | 59 | CONTRACT | listed building with `SMRFixPack_ack_notworking = true` and SKIPS the shipped whole-id |
| `docs/agent/bugs/D02.md` | 85 | CONTRACT | * **Save/reload:** the `SMRFixPack_ack_notworking` member persists — flagged |
| `docs/agent/bugs/D02.md` | 108 | HISTORY | Found during the fix pack's `C47` attended sitting, where the module was running |
| `docs/agent/bugs/D02.md` | 129 | HISTORY | \| **permanently broken** — never recovers \| survives \| ✅ stays quiet. This is the case the module exists... |
| `docs/agent/bugs/D02.md` | 139 | HISTORY | one.** The fix pack's `C47` records "debounce the notification, not the |
| `docs/agent/bugs/D02.md` | 142 | HISTORY | exactly the case that complaint is about. Cross-referenced on `C47`. |
| `docs/agent/bugs/D02.md` | 143 | HISTORY | 2. ✅ **It also means D02 could not have contaminated the `C47` measurements**, |
| `docs/agent/bugs/D02.md` | 147 | CONTRACT | `SMRFixPack_ack_notworking` **nil on all 38 objects**), *and* recovery would |
| `docs/agent/bugs/D03.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D03.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D03.md` | 18 | HISTORY | Filed 2026-07-27 (user decision, out of PT-14/F61's close — read that entry first). The |
| `docs/agent/bugs/D03.md` | 22 | HISTORY | load-bearing for Wildfire/RogueDome, see F61), the trait filter (indirect, trait-based, |
| `docs/agent/bugs/D03.md` | 25 | CONTRACT | * **Flag:** `SMRFixPack_closed_to_new_residents` set directly on the Dome object — |
| `docs/agent/bugs/D03.md` | 48 | HISTORY | ways), own playtest item, opt-in via `SMRFixPack_Optional.ResidencyControl` |
| `docs/agent/bugs/D03.md` | 70 | CONTRACT | * Flag `SMRFixPack_closed_to_new_residents` on the Dome object, absent-tolerant (§3). |
| `docs/agent/bugs/D03.md` | 73 | HISTORY | UI row needs eyes-on — it is the pack's first added infopanel row). |
| `docs/agent/bugs/D03.md` | 87 | HISTORY | ## ⚖️ 2026-08-10 (owner decision) — the `SMRFixPack_Disabled` console veto does NOT cover this module, and ... |
| `docs/agent/bugs/D03.md` | 89 | HISTORY | Only `IsActive` is consulted here; the veto lever exists for D12/F97-class |
| `docs/agent/bugs/D04.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D04.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D04.md` | 17 | HISTORY | ### D04 — Multiple Artificial Suns — absorbs F39  `[tested 2026-07-27 (PT-50 PASS in full, archive): Code/O... |
| `docs/agent/bugs/D04.md` | 29 | HISTORY | Filed 2026-07-27 (user decision, out of PT-26/F39's premise finding — read F39 first). |
| `docs/agent/bugs/D04.md` | 32 | HISTORY | F39's second-sun binding fix unreachable dead code in the default pack — but players DO |
| `docs/agent/bugs/D04.md` | 34 | HISTORY | `labels.ArtificialSun[1]` panel-binding bug. This module makes the pack's story honest: |
| `docs/agent/bugs/D04.md` | 37 | HISTORY | **Design — strictly additive, off by default (`SMRFixPack_Optional.MultipleSuns`, |
| `docs/agent/bugs/D04.md` | 44 | HISTORY | * **Binding fix:** the whole of `Fix_SecondArtificialSun.lua` moves in unchanged — the |
| `docs/agent/bugs/D04.md` | 52 | HISTORY | game-free leg as the F61 deletion so the renumbering happens once. |
| `docs/agent/bugs/D04.md` | 62 | HISTORY | re-fired `DataChanged(false)` re-asserts idempotently — F75 lesson; the handlers gate on |
| `docs/agent/bugs/D04.md` | 63 | HISTORY | the registry status, which covers both the opt-in flag and the `SMRFixPack_Disabled` |
| `docs/agent/bugs/D04.md` | 64 | HISTORY | veto). The F39 wrapper + LoadGame sweep moved in unchanged; `Fix_SecondArtificialSun.lua` |
| `docs/agent/bugs/D05.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D05.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D05.md` | 19 | HISTORY | enable route — "type `SMRFixPack_Optional = {...}` in the MAIN MENU console" — |
| `docs/agent/bugs/D05.md` | 23 | HISTORY | inside `SMRFixPack.Register`'s immediate `apply`, at **mod code load during game |
| `docs/agent/bugs/D05.md` | 27 | HISTORY | nicety: the pack targets Steam Workshop AND Paradox Mods, and **Paradox Mods |
| `docs/agent/bugs/D05.md` | 31 | HISTORY | `Mod.lua:590-604`) put the pack on **Options → Mod Options** (page def |
| `docs/agent/bugs/D05.md` | 37 | HISTORY | `Mod.lua:473-475` — it is what makes the page list the pack; normally written |
| `docs/agent/bugs/D05.md` | 44 | HISTORY | * **00_Core bridge (D05):** `SMRFixPack.OptionEnabled(id)` = pre-load |
| `docs/agent/bugs/D05.md` | 45 | HISTORY | `SMRFixPack_Optional[id]` OR the saved toggle — the gate line in all four |
| `docs/agent/bugs/D05.md` | 46 | HISTORY | Opt_ files. `SMRFixPack.IsActive(id)` — consulted by every optional module's |
| `docs/agent/bugs/D05.md` | 55 | HISTORY | `on_deactivate`; defs now retained in `SMRFixPack.defs` for reconciliation. |
| `docs/agent/bugs/D05.md` | 75 | HISTORY | repaired same day:** `SMRFixPack.ListFixes()` crashed ("attempt to concatenate |
| `docs/agent/bugs/D05.md` | 77 | HISTORY | 2026-07-25 F75/F18 status-relabel repairs clear their entry detail with |
| `docs/agent/bugs/D05.md` | 79 | HISTORY | (Fix_IndependenceTerraforming.lua:88, Fix_LastTransmissionStorage.lua:165), |
| `docs/agent/bugs/D06.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D06.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D06.md` | 18 | HISTORY | *(Heading line restored by the popup-audit session 2026-07-30 — the F84 filing |
| `docs/agent/bugs/D06.md` | 19 | HISTORY | commit `21b92cb` had spliced F84's text into this heading, leaving D06's whole |
| `docs/agent/bugs/D06.md` | 20 | HISTORY | entry living under F84. Content untouched.)* |
| `docs/agent/bugs/D06.md` | 22 | HISTORY | > ⚠️ **SAVE-SAFETY SURGERY LANDED ON THIS MODULE 2026-08-01 (chain prompt 5, F86 |
| `docs/agent/bugs/D06.md` | 23 | HISTORY | > Tier 2) — it is NOT drone work and changes NO drone behaviour.** F86 Site 2 was |
| `docs/agent/bugs/D06.md` | 27 | HISTORY | > 'SMRFixPack')` on the next load without the pack — **80** on the 2026-08-01 |
| `docs/agent/bugs/D06.md` | 35 | HISTORY | > Full record: the F86 entry's Site 2 block. Verification: PT-58. |
| `docs/agent/bugs/D06.md` | 40 | HISTORY | > 2026-07-31). It is re-runnable and owns D06, D08, D09, F77, the drone queue |
| `docs/agent/bugs/D06.md` | 50 | HISTORY | drones are the one part of the pack that has been iterated piece-by-piece, and |
| `docs/agent/bugs/D06.md` | 216 | HISTORY | >   moves the overhaul **out of the Community Fix Pack** into its own mod. |
| `docs/agent/bugs/D06.md` | 217 | HISTORY | > - The Fix Pack's own promise is unaffected: the pack stays save-safe and |
| `docs/agent/bugs/D06.md` | 220 | HISTORY | >   a standalone mod has no configuration matrix to multiply against the pack's |
| `docs/agent/bugs/D06.md` | 247 | HISTORY | > *the only thing that can occupy that window*. Full detail: ENGINE_FACTS + F86. |
| `docs/agent/bugs/D06.md` | 254 | HISTORY | > *by the pack itself*. **A second mod is the one thing that can occupy that |
| `docs/agent/bugs/D06.md` | 255 | HISTORY | > window.** It runs on `OnMsg.LoadGame` — in a world where the pack is already |
| `docs/agent/bugs/D06.md` | 269 | HISTORY | >    would rot as the pack changes. |
| `docs/agent/bugs/D06.md` | 284 | HISTORY | >   pack and **without** us shipping a risky migration inside the pack itself. |
| `docs/agent/bugs/D06.md` | 285 | HISTORY | >   That is a materially different posture from "we would have to patch the pack |
| `docs/agent/bugs/D06.md` | 414 | HISTORY | > (recorded on the fix pack's checklist, item 87, and in `STATE.md`). Drone |
| `docs/agent/bugs/D06.md` | 424 | HISTORY | replaced by **ONE multi-step playtest**, not a family of them. **PT-10 (F55) is |
| `docs/agent/bugs/D06.md` | 425 | HISTORY | NOT frozen** — different subject, shipped default-on fix. F77's defect is real |
| `docs/agent/bugs/D06.md` | 435 | HISTORY | COLLISION between the `Inventor` profile and D06/D09/F77; the interaction is |
| `docs/agent/bugs/D06.md` | 447 | CONTRACT | `colony:SetLabelModifier`: `SMRFixPack_DroneSpeedDial` on label **`Drone`** |
| `docs/agent/bugs/D06.md` | 448 | CONTRACT | prop `move_speed`, and `SMRFixPack_DroneCarryDial` on label **`Consts`** prop |
| `docs/agent/bugs/D06.md` | 455 | HISTORY | - **D06 and F77 reference no power, maintenance or `disable_*` property at all** |
| `docs/agent/bugs/D06.md` | 465 | HISTORY | working-flag flapping, so **F77's trigger should be rare or absent there** — |
| `docs/agent/bugs/D06.md` | 466 | HISTORY | a quiet F77 half on an Inventor save is not evidence the fix does nothing. |
| `docs/agent/bugs/D06.md` | 467 | HISTORY | *(Inference from the effect data; not observed. Run the F77 half on a |
| `docs/agent/bugs/D06.md` | 674 | HISTORY | in `Idle` at save time serialised it — **F86 Site 2, 98 errors per session, and it |
| `docs/agent/bugs/D06.md` | 693 | HISTORY | 3. **Telemetry** — `SMRFixPack.DroneReport()` (always available, module on or off): |
| `docs/agent/bugs/D06.md` | 701 | HISTORY | iteration knobs. Shipped alongside: **F77**'s `Fix_ExtenderFlapChurn` (default-on |
| `docs/agent/bugs/D07.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D07.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D07.md` | 34 | HISTORY | - **Bonus finding — live corroboration of F79.** Children in the cohort dome |
| `docs/agent/bugs/D07.md` | 36 | HISTORY | the mechanism F79 describes: `Dome:GetService` is passage-only, so |
| `docs/agent/bugs/D07.md` | 72 | HISTORY | **→ save with it ON and reload with the pack disabled in the MOD MANAGER**). |
| `docs/agent/bugs/D07.md` | 73 | HISTORY | ⚠️ **METHOD CORRECTED 2026-08-01 — a toggle CANNOT answer an uninstall question.** With the module merely s... |
| `docs/agent/bugs/D07.md` | 118 | HISTORY | cover it (work commutes are unaffected by F79; only service-seeking |
| `docs/agent/bugs/D07.md` | 122 | HISTORY | composition), F79/F80 (train findings from the same sitting), the |
| `docs/agent/bugs/D07.md` | 214 | HISTORY | ## ⚖️ 2026-08-10 (owner decision) — the `SMRFixPack_Disabled` console veto does NOT cover this module, and ... |
| `docs/agent/bugs/D07.md` | 216 | HISTORY | Only `IsActive` is consulted here; the veto lever exists for D12/F97-class |
| `docs/agent/bugs/D09.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D09.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D09.md` | 35 | HISTORY | (`Mods["SMR_CommunityFixPack"].options.DroneSpeedDial`) instead of the values |
| `docs/agent/bugs/D09.md` | 40 | HISTORY | `applied`, zero `[CommunityFixPack]` error/inactive/disabled lines, and the only |
| `docs/agent/bugs/D09.md` | 43 | HISTORY | thread on load was DEAD — restarting with the fixed body` lines are F02's |
| `docs/agent/bugs/D09.md` | 74 | HISTORY | **zero** `[CommunityFixPack]` error/inactive lines — a probe defect, never a |
| `docs/agent/bugs/D09.md` | 105 | CONTRACT | `SMRFixPack_DroneSpeedDial` / `SMRFixPack_DroneCarryDial`. Choice values |
| `docs/agent/bugs/D09.md` | 126 | HISTORY | **1/61/15/0** (dial probe FAILs "fix pack not loaded" by design) · default |
| `docs/agent/bugs/D09.md` | 134 | HISTORY | `Modifier.new` at file scope — the F64 pre-flattening trap (`new` is |
| `docs/agent/bugs/D09.md` | 141 | HISTORY | first leg run after the F28 removal and after the probe repair, and it clears |
| `docs/agent/bugs/D09.md` | 145 | HISTORY | `73/73` rather than a default-config `67/73`. Zero `[CommunityFixPack]` |
| `docs/agent/bugs/D12.md` | 10 | HISTORY | row_status: "**speced — no status beyond `speced` is claimed until PT-62 completes. BUILT 2026-08-02 (chain... |
| `docs/agent/bugs/D12.md` | 15 | HISTORY | from: "SMR-BugFixPack docs/agent/bugs/D12.md @ 0efb87e, moved 2026-08-12" |
| `docs/agent/bugs/D12.md` | 53 | HISTORY | colony-wide. Filed as **`C40`** with the five-link route. |
| `docs/agent/bugs/D12.md` | 57 | HISTORY | * It does **NOT** overturn the premise. C40 is a second, independent **producer** |
| `docs/agent/bugs/D12.md` | 118 | HISTORY | ⚠️ **What it costs versus narrow:** narrow was immune to the C40 capacity churn. |
| `docs/agent/bugs/D12.md` | 186 | HISTORY | still owed must not read that as "the pack is not ready" — the pack is not |
| `docs/agent/bugs/D12.md` | 415 | HISTORY | out, which is why the pack never produced this. ⚠️ **Lesson for the instrument, |
| `docs/agent/bugs/D12.md` | 493 | CONTRACT | \| `SMRFixPack_closed_to_new_residents` (D03, existing) \| **off** \| children can still migrate in \| |
| `docs/agent/bugs/D12.md` | 494 | CONTRACT | \| `SMRFixPack_no_homeless` (D12, new) \| **on** \| graduates are pushed out before they pile up \| |
| `docs/agent/bugs/D12.md` | 507 | HISTORY | put outside with no dome dies (F53 territory) — this is the one failure mode |
| `docs/agent/bugs/D12.md` | 528 | CONTRACT | * Savegame footprint per FIX_POLICY §3: `SMRFixPack_no_homeless` on the |
| `docs/agent/bugs/D12.md` | 530 | HISTORY | it and a save carrying it loads fine with the module or the pack removed. |
| `docs/agent/bugs/D12.md` | 551 | HISTORY | it ON, reload with the pack disabled in the MOD MANAGER, clean load.** |
| `docs/agent/bugs/D12.md` | 552 | HISTORY | ⚠️ **METHOD CORRECTED 2026-08-01 — a toggle CANNOT answer an uninstall question.** With the module merely s... |
| `docs/agent/bugs/D12.md` | 575 | HISTORY | `SMRFixPack_Disabled.NoHomeless` lever) need it. |
| `docs/agent/bugs/D12.md` | 581 | CONTRACT | `*r local bad = 0 for _, city in ipairs(Cities) do for _, c in ipairs(city.labels.Colonist or empty_table) ... |
| `docs/agent/bugs/D12.md` | 633 | HISTORY | [CommunityFixPack] NoHomeless: self-check targets Community but Workforce declares |
| `docs/agent/bugs/D12.md` | 635 | HISTORY | [CommunityFixPack] NoHomeless: inactive (Community.HasFreeWorkplacesAround not found |
| `docs/agent/bugs/D12.md` | 639 | HISTORY | [CommunityFixPack] NoHomeless: applied |
| `docs/agent/bugs/D12.md` | 642 | HISTORY | **This is the F64 lesson repeating** — the same mistake `Fix_BombardmentSpread`'s |
| `docs/agent/bugs/INDEX.md` | 7 | HISTORY | entries moved here from SMR-BugFixPack (split-optins, 2026-08-12); each entry's front |
| `docs/agent/facts/EF-001.md` | 20 | HISTORY | finds nil and silently deactivates the fix. F64 shipped broken this way |
| `docs/agent/facts/EF-001.md` | 27 | HISTORY | `Fix_LanderCargoRatchet.lua(124)` (the pack's pre-build replacement, baked |
| `docs/agent/facts/EF-002.md` | 10 | HISTORY | (established 2026-08-01 from the F86 Site 2 mechanism + PT-58; the project had |
| `docs/agent/facts/EF-002.md` | 11 | HISTORY | been using "off" loosely and it matters to F86 and to D13). Ranked by what they |
| `docs/agent/facts/EF-002.md` | 16 | HISTORY | \| **Mod Options toggle** (optional modules) \| **YES** — wrappers stay installed and pass through at call ... |
| `docs/agent/facts/EF-002.md` | 17 | HISTORY | \| **`SMRFixPack_Disabled[id]`** user veto \| **depends on where the module installs** — `Register` returns... |
| `docs/agent/facts/EF-002.md` | 22 | HISTORY | the pack **off** in the Mod Manager does **not** reset its Mod Options; turning |
| `docs/agent/facts/EF-002.md` | 34 | HISTORY | ⭐ Silver lining worth knowing: an all-toggles-ON run is the leg F87's residual |
| `docs/agent/facts/EF-002.md` | 38 | HISTORY | is the whole of F86.** With any toggle off the environment still exists, so a |
| `docs/agent/facts/EF-002.md` | 39 | HISTORY | captured frame resumes, resolves `SMRFixPack`, reads inactive and no-ops |
| `docs/agent/facts/EF-002.md` | 48 | HISTORY | player had the pack toggled off. The only state that keeps frames out of a save |
| `docs/agent/facts/EF-002.md` | 57 | HISTORY | (read off `SMRFixPack.IsActive`, `00_Core.lua:39-42`); and that the |
| `docs/agent/facts/EF-002.md` | 58 | HISTORY | `SMRFixPack_Disabled` veto blocks capture for apply()-time installers but not |
| `docs/agent/facts/EF-004.md` | 13 | HISTORY | mod's options (the TestKit driving the fix pack's dials) must go through |
| `docs/agent/facts/EF-005.md` | 11 | HISTORY | as crashes. `/` truncates (integer division); that is what makes F12's |
| `docs/agent/facts/EF-006.md` | 14 | HISTORY | the pack's `rawget(_G, "X")` pattern works; `_G` maps to the env, but NEW |
| `docs/agent/facts/EF-006.md` | 16 | HISTORY | `SMRFixPack`/`SMRTest` are cross-mod and console visible; `Msg`/`OnMsg` are |
| `docs/agent/facts/EF-006.md` | 17 | HISTORY | filtered only for persist/debug messages. The fix pack Code/ uses no |
| `docs/agent/facts/EF-007.md` | 19 | HISTORY | engine's "Mod Flagged" warning; the game and the fix pack were unaffected. |
| `docs/agent/facts/EF-008.md` | 19 | HISTORY | This project's only measurement of an assert reaching a log is `C43`, taken on |
| `docs/agent/facts/EF-010.md` | 12 | HISTORY | numbers are exactly this, by design. `GetStaticMsgNames()` (F06 probe) is a |
| `docs/agent/facts/EF-012.md` | 11 | HISTORY | pre-wrapped (F73). |
| `docs/agent/facts/EF-013.md` | 4 | HISTORY | summary: "Mod registry: every fix goes through `SMRFixPack.Register(id, {title" |
| `docs/agent/facts/EF-013.md` | 9 | HISTORY | - Mod registry: every fix goes through `SMRFixPack.Register(id, {title, apply})` |
| `docs/agent/facts/EF-013.md` | 11 | HISTORY | deactivate gracefully; `SMRFixPack_Disabled` = user veto; `SMRFixPack.ListFixes()` |
| `docs/agent/facts/EF-014.md` | 29 | HISTORY | genuine engine C export. F12's fix checks for it at apply time. |
| `docs/agent/facts/EF-017.md` | 14 | HISTORY | `rawget(_G, ...)` in apply() to confirm the write landed — F22 does. |
| `docs/agent/facts/EF-019.md` | 10 | HISTORY | audit 2026-07-30; the F83 investigation briefly assumed the opposite and |
| `docs/agent/facts/EF-019.md` | 23 | HISTORY | thread and LOST in an RT thread (the F83 family); "no MakeThreadPersistable" |
| `docs/agent/facts/EF-020.md` | 29 | HISTORY | reason to own one. (Worked example of the trap: chain prompt 7 declined C23 |
| `docs/agent/facts/EF-021.md` | 16 | HISTORY | closures included — observed, F83) and GT waiters persist (above); an open |
| `docs/agent/facts/EF-021.md` | 19 | HISTORY | `CanSaveGame` has no popup clause; see F85 for the rebind edge). |
| `docs/agent/facts/EF-022.md` | 24 | HISTORY | any reference to `SMRFixPack.*` inside it would index nil after uninstall. |
| `docs/agent/facts/EF-022.md` | 35 | HISTORY | `Fix_MeteorFrequency` was caught red-handed (F86). |
| `docs/agent/facts/EF-023.md` | 20 | HISTORY | two — `Fix_MeteorFrequency` and `Fix_RainsDeadlock` (fixed in Tier 1), |
| `docs/agent/facts/EF-023.md` | 21 | HISTORY | `Fix_MeteorStormWedge` and `Fix_ExtenderFlapChurn` (fixed 2026-08-13), plus |
| `docs/agent/facts/EF-023.md` | 22 | HISTORY | an inline site in `Fix_CrystalMysteryHang`. The belief itself is false, as |
| `docs/agent/facts/EF-023.md` | 34 | HISTORY | ONLY the names its own mod creates** (`SMRFixPack` is nil after uninstall |
| `docs/agent/facts/EF-023.md` | 38 | HISTORY | bounded if it self-limits (`Fix_CrystalMysteryHang`'s frozen 10-sol |
| `docs/agent/facts/EF-023.md` | 39 | HISTORY | deadline), forever if it loops (`Fix_RainsDeadlock`'s `fixed_loop` is |
| `docs/agent/facts/EF-023.md` | 49 | HISTORY | ⚠️ **CORRECTED 2026-07-31 (F86 adjudication): that clause is not the whole |
| `docs/agent/facts/EF-023.md` | 57 | HISTORY | `Fix_CaveInsNoDisasters`' wrapper sits in the `info` local the engine's |
| `docs/agent/facts/EF-023.md` | 66 | HISTORY | (F86 adjudication + owner, 2026-07-31): do not measure this and do not |
| `docs/agent/facts/EF-023.md` | 74 | HISTORY | corrections~~): **`agent/bugs/F86.md`**. ⛔ **COUNT SUPERSEDED 2026-08-13 by |
| `docs/agent/facts/EF-023.md` | 77 | HISTORY | "13" was an open lower bound over capturable code in the fix pack only; the |
| `docs/agent/facts/EF-023.md` | 82 | HISTORY | belief (`Fix_MeteorFrequency`, `Fix_RainsDeadlock`) were rewritten with their |
| `docs/agent/facts/EF-023.md` | 90 | HISTORY | rewrote and of nothing else: `Fix_MeteorStormWedge:138-141` and |
| `docs/agent/facts/EF-023.md` | 91 | HISTORY | `Fix_ExtenderFlapChurn`'s whole "Savegame note" still stated the disproven |
| `docs/agent/facts/EF-023.md` | 92 | HISTORY | model, and `Fix_CrystalMysteryHang` carried the F06 sentence inline. All |
| `docs/agent/facts/EF-024.md` | 28 | HISTORY | (2026-08-01, F86 Phase 0 §0.2 — `autosave=true err=false` observed twice). |
| `docs/agent/facts/EF-025.md` | 10 | HISTORY | AND IT IS THE ONE EVERY PLAYER GETS FIRST** (measured 2026-07-31, F87; source |
| `docs/agent/facts/EF-025.md` | 22 | HISTORY | for that entire session** — three of ours were (F87 sweep). |
| `docs/agent/facts/EF-025.md` | 35 | HISTORY | made `HasTrait:new` throw in `Fix_DustSicknessBiorobots` (F87). |
| `docs/agent/facts/EF-027.md` | 17 | HISTORY | these functions, however, will use their new versions."* So F86's mechanism |
| `docs/agent/facts/EF-028.md` | 4 | HISTORY | summary: "THE SAVE/LOAD HOOK SURFACE — enumerated 2026-07-31 (F86 round 2), so no design discovers hooks on... |
| `docs/agent/facts/EF-028.md` | 9 | HISTORY | - **THE SAVE/LOAD HOOK SURFACE — enumerated 2026-07-31 (F86 round 2), so no |
| `docs/agent/facts/EF-028.md` | 19 | HISTORY | can't-save bug, invisible on console, worse than F86) → |
| `docs/agent/facts/EF-029.md` | 10 | HISTORY | statement continues** (MEASURED 2026-08-01, F86 Phase 0 §0.1, owner at the |
| `docs/agent/facts/EF-029.md` | 37 | HISTORY | the first iteration. The F02 wrapper's defer-when-`rawget(_G,"Meteors")`-falsy |
| `docs/agent/facts/EF-030.md` | 10 | HISTORY | the autosave path with `autosave=true`** (MEASURED 2026-08-01, F86 Phase 0 |
| `docs/agent/facts/EF-034.md` | 26 | HISTORY | C18 on 2026-08-02** — that held only for `Building:AddToCityLabels` read |
| `docs/agent/facts/EF-036.md` | 16 | HISTORY | Proven 2026-08-02 while grading C30: `OrbitalProbe:Done` clears its label |
| `docs/agent/facts/EF-038.md` | 18 | HISTORY | a wrong figure on 2026-08-02: an F82 estimate assumed 20×, computed 3.3 sols |
| `docs/agent/facts/EF-039.md` | 12 | HISTORY | the fact that makes `Fix_TechDescriptionBuilding` a shipped no-op (**BUGS F98**) |
| `docs/agent/facts/EF-039.md` | 56 | HISTORY | discarded, this entry is right, and `F98` is a shipped no-op as stated. |
| `docs/agent/facts/EF-039.md` | 63 | HISTORY | reading `C51` would need (see `EF-063` for the 30-second way to check |
| `docs/agent/facts/EF-039.md` | 69 | HISTORY | * **Route 1 read forwards — a REPOINTED id.** `C51` pointed a control at an |
| `docs/agent/facts/EF-039.md` | 77 | HISTORY | * **Route 1 as a BORROWED id in a `T{tag, context}`.** `C50`'s bullet — a |
| `docs/agent/facts/EF-039.md` | 82 | HISTORY | the pack, with the number still resolving. |
| `docs/agent/facts/EF-039.md` | 84 | HISTORY | directions**: it destroys a replacement literal (the `F98` no-op, measured |
| `docs/agent/facts/EF-039.md` | 87 | HISTORY | *for reusing text*, which is exactly what `C50`/`C51` were built on. |
| `docs/agent/facts/EF-040.md` | 30 | HISTORY | * ⚠️ **Why it was worth 4000 draws to settle:** F97's headline claim is that a |
| `docs/agent/facts/EF-041.md` | 11 | HISTORY | Recorded 2026-08-02 by the F76 design pass, which was sent to confirm the |
| `docs/agent/facts/EF-042.md` | 10 | HISTORY | PC it equals the whole screen.** MEASURED 2026-08-02 (F76 sitting, M1): |
| `docs/agent/facts/EF-044.md` | 18 | HISTORY | retail (F98's whole mechanism, `agent/bugs/F98.md`). ⚠️ Corollary: a |
| `docs/agent/facts/EF-046.md` | 32 | HISTORY | right-edge rather than corner. Live example and disposition: `agent/bugs/C41.md`. |
| `docs/agent/facts/EF-046.md` | 36 | HISTORY | exactly on the cursor — that is what F76's M1/M2 measured, and it is why |
| `docs/agent/facts/EF-046.md` | 37 | HISTORY | F76's "coordinate-space mismatch" mechanism was correctly refuted. The |
| `docs/agent/facts/EF-048.md` | 18 | HISTORY | \| `GetSpentTimeAverageInHours` (2026-08-05, F21) \| **a `T()` object** \| |
| `docs/agent/facts/EF-048.md` | 22 | HISTORY | false negative forever and cannot print anything else — the F21 |
| `docs/agent/facts/EF-051.md` | 48 | HISTORY | re-enable the pack; all three were on disk again by **01:57:47**, creation |
| `docs/agent/facts/EF-054.md` | 35 | HISTORY | not assume it loads after (or before) another. Both the Community Fix Pack and the |
| `docs/agent/facts/EF-054.md` | 45 | HISTORY | * **A player's rig, 6 mods** (the F104 reporter's log |
| `docs/agent/facts/EF-054.md` | 47 | HISTORY | `SMR_CommunityFixPack, dwAWmXz, iooW34Y, QfCw4mN, DLav7z7` — **the fix pack |
| `docs/agent/facts/EF-054.md` | 50 | HISTORY | (`Mars.exe-20260823-22.05.52`): the fix pack first again. |
| `docs/agent/facts/EF-054.md` | 58 | HISTORY | ⚠️ **The first real ordering CONFLICT also arrived and was NOT ours:** F104's |
| `docs/agent/facts/EF-054.md` | 61 | HISTORY | clause was not needed. See `F104`. |
| `docs/agent/facts/EF-054.md` | 93 | HISTORY | the pack loads third. ⚖️ **OWNER RULING 2026-08-16: *"lets note this and see if |
| `docs/agent/facts/EF-055.md` | 101 | HISTORY | * **Result, twice:** the def loads (`Loaded mod def Relaunched Fix Pack: |
| `docs/agent/facts/EF-055.md` | 120 | HISTORY | pulls the **fix pack's** junction to install the packed build. On this |
| `docs/agent/facts/EF-055.md` | 129 | HISTORY | appdata` with all 75 modules applied and no re-tick anywhere |
| `docs/agent/facts/EF-055.md` | 130 | HISTORY | (`SWEEP_FINDINGS.md` LR-F19). ⇒ the loss clause binds **when a launch runs |
| `docs/agent/facts/EF-055.md` | 148 | HISTORY | DECLARED DEPENDENCIES, and neither the fix pack, the opt-in mod nor the Test |
| `docs/agent/facts/EF-057.md` | 4 | HISTORY | summary: "⛔⛔ A SAMPLED EXTREMUM IS NOT AN EXTREMUM — a polled series bounds NOTHING between its samples, so... |
| `docs/agent/facts/EF-057.md` | 9 | HISTORY | - **The defect this generalises, and it reversed a headline verdict.** The C47 |
| `docs/agent/facts/EF-057.md` | 37 | HISTORY | - ⚠️ Same family as the recorded-facts-are-claims-too rule and the C47 leg's own |
| `docs/agent/facts/EF-058.md` | 4 | HISTORY | summary: "⛔⛔ THE FLATTENED-CLASS TRAP BITES METHOD WRAPPERS TOO — patching a base class's method intercepts... |
| `docs/agent/facts/EF-058.md` | 20 | HISTORY | ⇒ A patch installed at a mod file's scope, or inside a `SMRFixPack.Register` |
| `docs/agent/facts/EF-059.md` | 4 | HISTORY | summary: "⭐⭐⭐ THE DRONE MATCHMAKER TREATS `rfStorageDepot`-FLAGGED SUPPLIES AS A STRICT LAST RESORT — any n... |
| `docs/agent/facts/EF-061.md` | 64 | HISTORY | the 2026-08-31 re-sync; `EF-061` since — ids are allocated in the fix pack and |
| `docs/agent/facts/EF-062.md` | 79 | HISTORY | the 2026-08-31 re-sync; `EF-062` since — ids are allocated in the fix pack and |
| `docs/agent/facts/EF-063.md` | 38 | HISTORY | prove it is not systemic.** Worked example (`C51`): the Universal Rocket's |
| `docs/agent/facts/EF-063.md` | 47 | HISTORY | carries every language, so the fix adds no English anywhere (`C51`). |
| `docs/agent/facts/EF-063.md` | 50 | HISTORY | who is not playing in English (`C50`). `EF-039` route 3, |
| `docs/agent/facts/EF-064.md` | 4 | HISTORY | summary: "⛔ `ProtectedPropertyObject` DOES NOT PROTECT ANYTHING IN RETAIL — `__newindex` asserts on an unde... |
| `docs/agent/facts/EF-064.md` | 41 | HISTORY | The failure was in the "therefore". See `C52`, where the real cause turned out |
| `docs/agent/facts/EF-065.md` | 4 | HISTORY | summary: "⛔⛔ THE ENGINE ITSELF SHOWS THE PLAYER A MESSAGE BOX NAMING OUR MOD — but only on ONE of its two r... |
| `docs/agent/facts/EF-065.md` | 11 | HISTORY | enumerated 17 screen call sites in `Code/` and concluded the pack "mints no |
| `docs/agent/facts/EF-065.md` | 54 | HISTORY | from `SMRFixPack.fixes`/`order` only when the throw precedes its `Register` |
| `docs/agent/facts/EF-065.md` | 63 | HISTORY | `Mod/SMR_CommunityFixPack/` in run B exactly as unpacked — re-derived by the |
| `docs/agent/facts/EF-065.md` | 80 | HISTORY | * **F104** — Passage Network's `CreateDomeNetworks` returns nothing, vanilla |
| `docs/agent/facts/EF-065.md` | 82 | HISTORY | `Fix_ShuttleTransportCache.lua(86)`. ⭐ Reproduced on the owner's rig, |
| `docs/agent/facts/EF-065.md` | 88 | HISTORY | * **F105** — a vanilla `LandscapeConstructionSite` defect; our frame is |
| `docs/agent/facts/EF-065.md` | 89 | HISTORY | `Fix_MilestoneCrash.lua(73)`. Reporter's log |
| `docs/agent/facts/EF-065.md` | 94 | HISTORY | `Mod Flagged:` and `Relaunched Fix Pack`, single `OK`. Position and whether it |
| `docs/agent/facts/EF-065.md` | 97 | HISTORY | This fact previously recorded that as *not derivable from Lua*. F104's throw |
| `docs/agent/facts/EF-066.md` | 4 | HISTORY | summary: "⭐⭐ A BUILT CLASS'S `Init` IS NEVER THE FUNCTION ANYONE ASSIGNED — `Init`/`Done` are COMBINED meth... |
| `docs/agent/facts/EF-066.md` | 20 | HISTORY | 4 sitting: `C51` wrapped ONLY `customUniversalRocket` (`link4de_*`: "wrapped |
| `docs/agent/facts/EF-066.md` | 23 | HISTORY | `Fix_LocalizedUIText.lua` repaired nothing; this mechanism is why. |
| `docs/agent/facts/EF-066.md` | 45 | HISTORY | keeps its own function and the parent wrap never runs there. `C51`'s rocket |
| `docs/agent/facts/EF-066.md` | 52 | HISTORY | MEASUREMENT THE SAME DAY** (`F106`, closed; log |
| `docs/agent/facts/EF-066.md` | 56 | HISTORY | overriding or not, and named `Fix_SmallLandscapeSites` (F33) a suspect |
| `docs/agent/facts/EF-066.md` | 57 | HISTORY | no-op. **The premise "post-ClassesBuilt" is false.** `SMRFixPack.Register` |
| `docs/agent/facts/EF-066.md` | 65 | HISTORY | builder's member copy, not `ClassesPreprocess`'s composition). F33 measured |
| `docs/agent/facts/EF-066.md` | 69 | HISTORY | `SMRFixPack.DataPatch` waits for `ClassesBuilt` (`00_Core.lua:334`). |
| `docs/agent/facts/EF-066.md` | 72 | HISTORY | every `{class, method}` target the pack declares: |
| `docs/agent/facts/EF-066.md` | 80 | HISTORY | declares both interaction methods `Fix_RocketInteractGuard` wraps on |
| `docs/agent/facts/EF-066.md` | 82 | HISTORY | both `GetWorkNot*Reason` that `Fix_ShuttleHubOffAvailable` wraps on |
| `docs/agent/facts/EF-066.md` | 88 | HISTORY | * ⚠️ **THE REAL DEFECT THE SWEEP FOUND IS THE MIRROR IMAGE — `F107`.** Because |
| `docs/agent/facts/EF-066.md` | 89 | HISTORY | the pack wraps classdefs, a module that captures `local prev = C.Method` on a |
| `docs/agent/facts/EF-066.md` | 91 | HISTORY | holds only its own members and has no metatable). `Fix_LandscapeCostRefresh` |
| `docs/agent/facts/EF-066.md` | 93 | HISTORY | `F107`. Static audit: the pack's only instance. ⇒ **the authoring rule this |
| `docs/agent/facts/EF-068.md` | 34 | HISTORY | had run, and filed "Steam has neither F105 nor F108" as an owner decision. |
| `docs/agent/facts/EF-068.md` | 48 | HISTORY | present: `Fix_LandscapeCostRefresh.lua` (F105) and |
| `docs/agent/facts/EF-068.md` | 49 | HISTORY | `Fix_ExtractorStaffedPerformance.lua` (F108). Its packed `metadata.lua` reads |
| `docs/agent/facts/INDEX.md` | 28 | HISTORY | \| EF-013 \| Mod registry: every fix goes through `SMRFixPack.Register(id, {title \| — \| 2026-07-29 \| 4 \... |
| `docs/agent/facts/INDEX.md` | 43 | HISTORY | \| EF-028 \| THE SAVE/LOAD HOOK SURFACE — enumerated 2026-07-31 (F86 round 2), so no design discovers hooks... |
| `docs/agent/facts/INDEX.md` | 72 | HISTORY | \| EF-057 \| ⛔⛔ A SAMPLED EXTREMUM IS NOT AN EXTREMUM — a polled series bounds NOTHING between its samples,... |
| `docs/agent/facts/INDEX.md` | 73 | HISTORY | \| EF-058 \| ⛔⛔ THE FLATTENED-CLASS TRAP BITES METHOD WRAPPERS TOO — patching a base class's method interce... |
| `docs/agent/facts/INDEX.md` | 74 | HISTORY | \| EF-059 \| ⭐⭐⭐ THE DRONE MATCHMAKER TREATS `rfStorageDepot`-FLAGGED SUPPLIES AS A STRICT LAST RESORT — an... |
| `docs/agent/facts/INDEX.md` | 79 | HISTORY | \| EF-064 \| ⛔ `ProtectedPropertyObject` DOES NOT PROTECT ANYTHING IN RETAIL — `__newindex` asserts on an u... |
| `docs/agent/facts/INDEX.md` | 80 | HISTORY | \| EF-065 \| ⛔⛔ THE ENGINE ITSELF SHOWS THE PLAYER A MESSAGE BOX NAMING OUR MOD — but only on ONE of its tw... |
| `docs/agent/facts/INDEX.md` | 81 | HISTORY | \| EF-066 \| ⭐⭐ A BUILT CLASS'S `Init` IS NEVER THE FUNCTION ANYONE ASSIGNED — `Init`/`Done` are COMBINED m... |
| `docs/agent/facts/_preamble.md` | 12 | HISTORY | prompt 3) from `SMR-BugFixPack` @ `33d69f5` — all 53 facts, this preamble and |
| `docs/agent/FIX_POLICY.md` | 8 | HISTORY | > Copied from `SMR-BugFixPack/docs/agent/FIX_POLICY.md` @ `33d69f5` on |
| `docs/agent/FIX_POLICY.md` | 19 | HISTORY | > 2. **The namespace is renamed throughout** — `SMRFixPack.*` → `SMROptInPack.*`, |
| `docs/agent/FIX_POLICY.md` | 20 | HISTORY | >    `SMRFixPack_Disabled` → `SMROptInPack_Disabled`. ⛔ **§3's `SMRFixPack_*` |
| `docs/agent/FIX_POLICY.md` | 40 | HISTORY | all (F23). |
| `docs/agent/FIX_POLICY.md` | 63 | HISTORY | back with `rawget(_G, name)` in apply() to confirm the write landed (F22 |
| `docs/agent/FIX_POLICY.md` | 67 | HISTORY | gracefully and a copy does not** (recorded 2026-07-31 by the F86 layer-3 |
| `docs/agent/FIX_POLICY.md` | 76 | HISTORY | (`Colonist:ShouldLeaveForWork`, F04); |
| `docs/agent/FIX_POLICY.md` | 79 | HISTORY | string-keyed table with `ipairs`, F03). |
| `docs/agent/FIX_POLICY.md` | 83 | HISTORY | fixes F33 with zero copied logic. |
| `docs/agent/FIX_POLICY.md` | 86 | HISTORY | (F04, F09, F11, F12...). Rules: |
| `docs/agent/FIX_POLICY.md` | 96 | HISTORY | file-local was inlined, a helper re-derived; F03/F04/F09 are of this |
| `docs/agent/FIX_POLICY.md` | 110 | HISTORY | - **Self-check on the DECLARING class** (the F64 lesson): mod code runs before |
| `docs/agent/FIX_POLICY.md` | 116 | HISTORY | APPEAR IN THAT MODULE'S OWN `Require` BLOCK (the F107 rule — adopted in the |
| `docs/agent/FIX_POLICY.md` | 117 | HISTORY | fix pack 2026-08-24, carried here 2026-08-31).** `Require` validates what the |
| `docs/agent/FIX_POLICY.md` | 119 | HISTORY | next door: the fix pack's `Fix_LandscapeCostRefresh` required the declaring |
| `docs/agent/FIX_POLICY.md` | 122 | HISTORY | declared — and `prev` was nil on every boot (fix-pack F107). Had the |
| `docs/agent/FIX_POLICY.md` | 127 | HISTORY | method (the F64 lesson above). Statically enforced for the shape that can |
| `docs/agent/FIX_POLICY.md` | 139 | HISTORY | - ⛔ **NEVER `Require` A PER-GAME RUNTIME GLOBAL AT APPLY TIME (the F110 rule — |
| `docs/agent/FIX_POLICY.md` | 140 | HISTORY | fix pack 2026-08-30, carried here 2026-08-31).** `apply()`/`Require` run at |
| `docs/agent/FIX_POLICY.md` | 151 | HISTORY | - ⛔ **NO `apply()` MAY ASSUME A COLD BOOT (the F87 rule, 2026-07-31).** A mod is |
| `docs/agent/FIX_POLICY.md` | 170 | HISTORY | idempotent. The F87 sweep found three sites that had this bug. |
| `docs/agent/FIX_POLICY.md` | 171 | HISTORY | **Both paths must be tested** — a cold boot AND a run where the pack is |
| `docs/agent/FIX_POLICY.md` | 172 | HISTORY | enabled from the main menu. The second one is why F87 shipped. |
| `docs/agent/FIX_POLICY.md` | 186 | STALE-FIXED | the veto. Donor pattern: Fix_LastTransmissionStorage's patch() prologue. |
| `docs/agent/FIX_POLICY.md` | 189 | HISTORY | has fired — before that, absence just means "not loaded yet" (the F75 |
| `docs/agent/FIX_POLICY.md` | 199 | POINTER | `SMRFixPack_*` and tolerate their absence (loading a save made with the mod, |
| `docs/agent/FIX_POLICY.md` | 201 | POINTER | ⛔ **YES, `SMRFixPack_` — that prefix is not a typo here and is not renamed |
| `docs/agent/FIX_POLICY.md` | 208 | HISTORY | (e.g. F03's leaked modifiers), the cleanup is a **separate, clearly marked |
| `docs/agent/FIX_POLICY.md` | 211 | POINTER | - **Exit hygiene (owner, 2026-07-31): the pack ships with its exit paved.** |
| `docs/agent/FIX_POLICY.md` | 216 | POINTER | lost the pack (the only console-viable remedy). Record + spec gate + open |
| `docs/agent/FIX_POLICY.md` | 244 | POINTER | >    that **ships at launch, alongside the pack**. A harmful residual is never |
| `docs/agent/FIX_POLICY.md` | 280 | POINTER | the pack could not. |
| `docs/agent/FIX_POLICY.md` | 296 | STALE-FIXED | engine frames included (`Fix_CaveInsNoDisasters` is capturable this way, |
| `docs/agent/FIX_POLICY.md` | 305 | STALE-FIXED | self-limits, forever if it loops). `Fix_MeteorFrequency` killed a colony's |
| `docs/agent/FIX_POLICY.md` | 372 | STALE-FIXED | `Fix_LastTransmissionStorage`'s `Condition.eval`, disclosed-no-build, |
| `docs/agent/FIX_POLICY.md` | 380 | POINTER | analysis at `docs/agent/reports/SAVE_SAFETY_REDESIGN.md` and `agent/bugs/F86.md` |
| `docs/agent/FIX_POLICY.md` | 381 | POINTER | in the fix pack repo. |
| `docs/agent/FIX_POLICY.md` | 387 | POINTER | > for the fix pack, and still the test that decides which of the two mods a |
| `docs/agent/FIX_POLICY.md` | 390 | POINTER | **The inversion, stated plainly:** the fix pack may only repair *unintended* |
| `docs/agent/FIX_POLICY.md` | 402 | POINTER | (c) a **repair the fix pack declined** because intent was ambiguous or the |
| `docs/agent/FIX_POLICY.md` | 422 | POINTER | - **No cross-module dependency inside this mod, and none on the fix pack.** |
| `docs/agent/FIX_POLICY.md` | 424 | POINTER | with the fix pack absent (the standalone invariant, `CLAUDE.md`). A module |
| `docs/agent/FIX_POLICY.md` | 438 | POINTER | ### §4-donor — the fix pack's §4, kept verbatim (do not edit; the donor is authoritative for it) |
| `docs/agent/FIX_POLICY.md` | 443 | POINTER | it belongs in the fix pack as a plain fix, not here behind a toggle.* |
| `docs/agent/FIX_POLICY.md` | 455 | POINTER | > > contradicted itself while F49(a) shipped a no-op R4 rider against the new |
| `docs/agent/FIX_POLICY.md` | 456 | POINTER | > > "R4 does not ship" line; that guard was **stripped from `Fix_TrainMinors` |
| `docs/agent/FIX_POLICY.md` | 457 | POINTER | > > on 2026-08-01** (`agent/bugs/F49.md`; A/B code-gate leg ran clear), so the rule and the |
| `docs/agent/FIX_POLICY.md` | 458 | POINTER | > > shipped code now agree. **Live consequence on adoption:** F29 and F57(a) are |
| `docs/agent/FIX_POLICY.md` | 477 | POINTER | >   gives confident answers with no validity there (the F49(c) lesson). A |
| `docs/agent/FIX_POLICY.md` | 492 | POINTER | >   full replacement needs an explicit user decision (the F24 lesson). **R4 |
| `docs/agent/FIX_POLICY.md` | 505 | POINTER | >   sibling code in the same file (the F07/F08/F02 pattern). |
| `docs/agent/FIX_POLICY.md` | 513 | POINTER | > sharpening the split makes necessary: **the Relaunched Fix Pack is "another |
| `docs/agent/FIX_POLICY.md` | 515 | POINTER | > around a fix-pack behaviour, and a fix-pack bug is reported and fixed there. |
| `docs/agent/FIX_POLICY.md` | 546 | HISTORY | *(This is tier **R4**. F28 is the worked example: `Research:ReplaceTech` has |
| `docs/agent/FIX_POLICY.md` | 554 | HISTORY | without anyone touching a mod. *(Tier **R3**. F29's two items are the worked |
| `docs/agent/FIX_POLICY.md` | 557 | HISTORY | already-ordered timings. F27, F31 and F43 are the same shape.)* |
| `docs/agent/FIX_POLICY.md` | 565 | HISTORY | mod-facing. **F29 described itself as a "mod-facing bundle" with "No shipped |
| `docs/agent/FIX_POLICY.md` | 568 | HISTORY | (the F49(c) lesson, applied to provenance). |
| `docs/agent/FIX_POLICY.md` | 574 | HISTORY | precedent — one (F28) already violated this rule and was retired under it. |
| `docs/agent/FIX_POLICY.md` | 576 | STALE-FIXED | **Why this exists.** The pack shipped `Fix_ReplaceTechCount` (F28) against a |
| `docs/agent/FIX_POLICY.md` | 629 | HISTORY | toggle OFF**, which is how F86 Site 2 was found. Never infer save-cleanliness |
| `docs/agent/FIX_POLICY.md` | 644 | POINTER | strings from this pack use `Untranslated("...")` — the pack ships no loc tables |
| `docs/agent/FIX_POLICY.md` | 646 | HISTORY | crashes (the F14 probe lesson). Log/console text stays plain strings. |
| `docs/agent/FIX_POLICY.md` | 652 | STALE-FIXED | every other language. `Fix_TechDescriptionBuilding` did exactly this and has |
| `docs/agent/FIX_POLICY.md` | 653 | STALE-FIXED | never changed anything (**`agent/bugs/F98.md`**; F25 demoted, and **no longer citable as |
| `docs/agent/FIX_POLICY.md` | 660 | STALE-FIXED | "RE-USING A SHIPPED TRANSLATION ID …". ⭐ **Owner decision 2026-08-02: the pack |
| `docs/agent/FIX_POLICY.md` | 687 | POINTER | belongs in the fix pack (§4a). |
| `docs/agent/FIX_POLICY.md` | 691 | POINTER | the Relaunched Fix Pack installed and with it absent** (the standalone |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 1 | SELF-PROMPT | # CONTAMINATION_AUDIT — one-off: is this repo clear of fix-pack contamination, and does everything in it ha... |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 9 | SELF-PROMPT | **Why.** This repo was split out of `SMR-BugFixPack` on 2026-08-12 and has taken |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 29 | SELF-PROMPT | the fix pack", "where new things go"), `agent/WORKFLOW.md` "Layout" and the |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 42 | SELF-PROMPT | \| **CONTRACT** \| the five persisted names `SMRFixPack_ack_notworking`, `_closed_to_new_residents`, `_no_h... |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 44 | SELF-PROMPT | \| **POINTER** \| a live instruction that deliberately points at the fix pack: the owner's `PLAYTEST_CHECKL... |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 45 | SELF-PROMPT | \| **STALE** \| a live instruction, tool comment, docstring, label or default that was true in the fix pack... |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 46 | SELF-PROMPT | \| **CONTAMINATION** \| executable code referencing `SMRFixPack`/`[CommunityFixPack]`/`SMR_CommunityFixPack... |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 55 | SELF-PROMPT | "SMRFixPack\|CommunityFixPack\|SMR_CommunityFixPack\|SMR-BugFixPack\|SMR-CommunityFixPack\|[Ff]ix[ -][Pp]ac... |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 63 | SELF-PROMPT | comments), nothing else. Verify ban 2 mechanically: every `SMRFixPack` token |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 65 | SELF-PROMPT | AST for Name/Index nodes containing `SMRFixPack` — there must be none). |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 67 | SELF-PROMPT | "works with or without the Relaunched Fix Pack" sentences (POINTER). Anything |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 79 | SELF-PROMPT | unmarked donor prose → add the marker (ADAPTED / N/A here / fix-pack history). |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 81 | SELF-PROMPT | F-ids, C-ids and fix-pack module names inside a D-entry's narrative are |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 85 | SELF-PROMPT | whose only content is a fix-pack module's behaviour is a Pass-B candidate. |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 106 | SELF-PROMPT | `blocking_analysis.py` is cited by D06's F86 record); `00_Core.lua`'s `DataPatch` |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 112 | SELF-PROMPT | fix-pack module; `.claude/settings.json`'s allowances; `README.md` (mod-facing) |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 116 | SELF-PROMPT | disposition (delete / move to the fix pack / write the reason and keep) and the |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 131 | SELF-PROMPT | 3. Owner items on the fix pack's `docs/PLAYTEST_CHECKLIST.md` → "Decisions |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 144 | SELF-PROMPT | - A `SMRFixPack` reference in EXECUTABLE position (not a string, not a comment) |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 148 | SELF-PROMPT | - A persisted-looking name (`SMRFixPack_*` / `SMROptInPack_*` written onto an |
| `docs/agent/prompts/CONTAMINATION_AUDIT.md` | 164 | SELF-PROMPT | - Anything about the fix pack repo's own state — this audit reads it only to |
| `docs/agent/prompts/DISPATCH.md` | 3 | POINTER | Adapted from the fix pack's `prompts/DISPATCH.md` (2026-08-29) for THIS repo. |
| `docs/agent/prompts/DISPATCH.md` | 29 | POINTER | runtime; a **true standalone** beside the Relaunched Fix Pack. The map is |
| `docs/agent/prompts/DISPATCH.md` | 41 | POINTER | STALE-PROBE GATE binds first: `grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/`, |
| `docs/agent/prompts/DISPATCH.md` | 49 | POINTER | `SMRFixPack_*` field and modifier id this mod writes keeps its exact bytes |
| `docs/agent/prompts/DISPATCH.md` | 50 | POINTER | (`agent/PROVENANCE.md` §2); and ZERO `SMRFixPack` references in executable |
| `docs/agent/prompts/DISPATCH.md` | 58 | POINTER | §2 enable-path / declaring-class / the F107 wrap rule / the F110 runtime-global |
| `docs/agent/prompts/DISPATCH.md` | 67 | POINTER | STATE byte budget, `metadata.lua` load order and the F107 wrap check. Counts |
| `docs/agent/prompts/DISPATCH.md` | 75 | POINTER | commit, the same as the fix pack. ⛔ TestKit is local-only BY DESIGN. |
| `docs/agent/prompts/DISPATCH.md` | 95 | POINTER | route it to the fix pack's `docs/PLAYTEST_CHECKLIST.md` → "Decisions waiting on |
| `docs/agent/prompts/DISPATCH.md` | 112 | POINTER | - A **decision the owner must make** → the fix pack's checklist, never only here. |
| `docs/agent/prompts/DISPATCH.md` | 120 | POINTER | \| a LIVE playtest at the keyboard (both mods) \| fix pack `prompts/GENERAL_USE_PROMPT.md` (single-sourced ... |
| `docs/agent/prompts/DISPATCH.md` | 121 | POINTER | \| this mod's LAUNCH — the whole thing \| `agent/STATE.md` launch obligation → fix pack `reports/PARKED_OPT... |
| `docs/agent/prompts/DISPATCH.md` | 122 | POINTER | \| the owner's mechanical pack+upload only \| fix pack `docs/UPLOAD_WORKFLOW.md` (+ `reports/RELEASE_PORTAL... |
| `docs/agent/prompts/STATE_EVICTION.md` | 3 | POINTER | Carried 2026-08-31 from the fix pack's `prompts/STATE_EVICTION.md` (designed |
| `docs/agent/prompts/STATE_EVICTION.md` | 70 | POINTER | - Owner-facing asks always live in the fix pack's checklist, never only here |
| `docs/agent/prompts/WORK_PROMPT.md` | 13 | POINTER | > and the fix pack's checklist. The only edits this file takes are corrections |
| `docs/agent/prompts/WORK_PROMPT.md` | 17 | POINTER | > **issues once the mod is live** (player reports, field bugs); the fix pack's |
| `docs/agent/prompts/WORK_PROMPT.md` | 24 | POINTER | Options; patched at runtime over the mod's own copy of the pack framework |
| `docs/agent/prompts/WORK_PROMPT.md` | 25 | POINTER | (`SMROptInPack`); a true standalone beside the Relaunched Fix Pack. Not yet |
| `docs/agent/prompts/WORK_PROMPT.md` | 27 | POINTER | **persisted names are save contract** (every `SMRFixPack_*` field/modifier id |
| `docs/agent/prompts/WORK_PROMPT.md` | 28 | POINTER | keeps its bytes — `agent/PROVENANCE.md` §2) and **zero `SMRFixPack` references |
| `docs/agent/prompts/WORK_PROMPT.md` | 44 | POINTER | first — `grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/`, in the |
| `docs/agent/prompts/WORK_PROMPT.md` | 53 | POINTER | \| **drone work** (D06 overhaul, D09 dials, `FUTURE_IDEAS.md` #7) \| UNFROZEN 2026-08-31. ⛔ Do not build an... |
| `docs/agent/prompts/WORK_PROMPT.md` | 56 | POINTER | \| **tooling** \| `tools/` inventory + what each proves: `agent/PROVENANCE.md` §6. Port from the fix pack w... |
| `docs/agent/prompts/WORK_PROMPT.md` | 57 | POINTER | \| **launch prep** \| `STATE.md` "NEXT" (the ordered list), `WORKFLOW.md` "Release marking" + "Release step... |
| `docs/agent/prompts/WORK_PROMPT.md` | 60 | POINTER | \| **a live issue / a live playtest** \| `prompts/DISPATCH.md` / fix pack `GENERAL_USE_PROMPT.md` \| |
| `docs/agent/prompts/WORK_PROMPT.md` | 67 | POINTER | neutrally with the trade-offs measured, put the ask on the fix pack's |
| `docs/agent/prompts/WORK_PROMPT.md` | 86 | POINTER | installed named in the module's `Require` block (F107); never `Require` a |
| `docs/agent/prompts/WORK_PROMPT.md` | 87 | POINTER | per-game global (F110); `SMROptInPack_Disabled` honoured in every handler. |
| `docs/agent/prompts/WORK_PROMPT.md` | 93 | POINTER | 5. **A/B in the TestKit** (`C:\Dev\SMR-BugFixPack-TestKit`, shared, local-only): |
| `docs/agent/prompts/WORK_PROMPT.md` | 125 | POINTER | - An engine fact → fix pack `EF-###` first, mirrored here at the same id. |
| `docs/agent/prompts/WORK_PROMPT.md` | 144 | POINTER | - "Standalone" or "works without the fix pack" for a change not run in BOTH |
| `docs/agent/prompts/WORK_PROMPT.md` | 156 | POINTER | lesson to its §5 home, never here. Owner asks → the fix pack's checklist. |
| `docs/agent/PROVENANCE.md` | 3 | HISTORY | This repo was **split out of `SMR-BugFixPack` on 2026-08-12** by the chain |
| `docs/agent/PROVENANCE.md` | 12 | HISTORY | \| Community Fix Pack \| `C:\Dev\SMR-BugFixPack` \| `33d69f5d8412a3924a53b93de38f00f1c23e3866` \| `github.c... |
| `docs/agent/PROVENANCE.md` | 13 | HISTORY | \| TestKit (shared, never shipped) \| `C:\Dev\SMR-BugFixPack-TestKit` \| `d8e1fbf56c4a7be4913fbdc34f2bc9b96... |
| `docs/agent/PROVENANCE.md` | 16 | HISTORY | after them in the fix pack's history; `git log --oneline` there, around |
| `docs/agent/PROVENANCE.md` | 27 | HISTORY | \| `Code/00_Core.lua` \| `Code/00_Core.lua` \| ADAPTED \| whole-file token rename `SMRFixPack` → `SMROptInP... |
| `docs/agent/PROVENANCE.md` | 28 | HISTORY | \| `Code/Opt_*.lua` ×8 \| same names \| ADAPTED \| the same token rename, plus: `Opt_DroneOverhaul`'s CLONE... |
| `docs/agent/PROVENANCE.md` | 30 | HISTORY | \| `docs/agent/bugs/D01…D07, D09, D12` \| same names \| ADAPTED \| bodies byte-preserved; front matter renu... |
| `docs/agent/PROVENANCE.md` | 31 | HISTORY | \| `docs/agent/FIX_POLICY.md` \| same \| ADAPTED \| §4 inverted for a mod whose product IS opinionated modu... |
| `docs/agent/PROVENANCE.md` | 34 | HISTORY | \| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` \| same \| VERBATIM (moved) \| D06/D09's design study; th... |
| `docs/agent/PROVENANCE.md` | 38 | HISTORY | \| `tools/blocking_analysis.py` \| same \| VERBATIM \| `Opt_DroneOverhaul`'s F86 Tier-2 record depends on i... |
| `docs/agent/PROVENANCE.md` | 44 | HISTORY | sourced in the fix pack by design — `docs/README.md` says why), the 73 `Fix_*` |
| `docs/agent/PROVENANCE.md` | 45 | HISTORY | modules and `90_SaveSanitizer.lua`, and the fix pack's `docs/BUGS.md` / |
| `docs/agent/PROVENANCE.md` | 54 | HISTORY | EXACT bytes forever, `SMRFixPack_` prefix and all.** They were written by these |
| `docs/agent/PROVENANCE.md` | 55 | HISTORY | modules while they lived in the fix pack; a rename would orphan live state in |
| `docs/agent/PROVENANCE.md` | 62 | CONTRACT | \| 1 \| `SMRFixPack_ack_notworking` \| field on `Building` objects \| `Opt_AcknowledgedWarnings.lua` (`obj[... |
| `docs/agent/PROVENANCE.md` | 63 | CONTRACT | \| 2 \| `SMRFixPack_closed_to_new_residents` \| field on `Dome`/`MicroGHabitatBase` \| `Opt_ResidencyContro... |
| `docs/agent/PROVENANCE.md` | 64 | CONTRACT | \| 3 \| `SMRFixPack_no_homeless` \| field on `Dome`/`MicroGHabitatBase` \| `Opt_NoHomeless.lua` (`TogglePol... |
| `docs/agent/PROVENANCE.md` | 65 | CONTRACT | \| 4 \| `SMRFixPack_DroneSpeedDial` \| **label-modifier id** in `UIColony.label_modifiers["Drone"]`, holdin... |
| `docs/agent/PROVENANCE.md` | 66 | CONTRACT | \| 5 \| `SMRFixPack_DroneCarryDial` \| as above, label `Consts` \| `Opt_DroneStatDials.lua` \| same \| |
| `docs/agent/PROVENANCE.md` | 73 | HISTORY | (`SMR_CommunityFixPack` → `SMR_CommunityOptInPack`), so the player's saved |
| `docs/agent/PROVENANCE.md` | 79 | HISTORY | **Provably never persisted, so the rename was safe:** `SMRFixPack_Optional` / |
| `docs/agent/PROVENANCE.md` | 80 | HISTORY | `SMRFixPack_Disabled` (now `SMROptInPack_*`) — plain `_G` tables built with |
| `docs/agent/PROVENANCE.md` | 97 | HISTORY | ✅ **DECIDED (owner, 2026-08-13): `"Community Fix Pack: Opt-In Modules"`** — |
| `docs/agent/PROVENANCE.md` | 100 | HISTORY | shared naming lets the fix pack surface its sibling). **Swept the same day, one |
| `docs/agent/PROVENANCE.md` | 116 | HISTORY | `github.com/catt144/SMR-CommunityOptInPack`, matching the fix pack's setup. All |
| `docs/agent/PROVENANCE.md` | 126 | HISTORY | `C:\Dev\SMR-BugFixPack-TestKit`**, and ONE kit serves BOTH mods. It is not |
| `docs/agent/PROVENANCE.md` | 138 | HISTORY | `SMRTest.OptMissing(id)` (the fix pack's is `FixStatus`/`FixMissing`), and |
| `docs/agent/PROVENANCE.md` | 143 | HISTORY | `fix pack present: %d/%d fixes active` and |
| `docs/agent/PROVENANCE.md` | 145 | HISTORY | bracketed token (`[CommunityOptInPack]` / `[CommunityFixPack]`) — `Pack]` |
| `docs/agent/PROVENANCE.md` | 151 | HISTORY | ## 5. What the fix pack kept, and what it lost |
| `docs/agent/PROVENANCE.md` | 164 | HISTORY | The fix pack kept building after the split; this pass carried across what it |
| `docs/agent/PROVENANCE.md` | 166 | HISTORY | Donor sha for every row: `SMR-BugFixPack` @ `bec2e06d` (v5 closed, 2026-08-30). |
| `docs/agent/PROVENANCE.md` | 175 | HISTORY | \| `tools/l3_save_footprint.py` \| ADAPTED \| `NAMED_STATE` matches BOTH prefixes (persisted names keep `SM... |
| `docs/agent/PROVENANCE.md` | 181 | HISTORY | \| `docs/agent/facts/` \| VERBATIM (re-sync) \| 7 donor-updated shared facts taken whole (EF-008/023/039/05... |
| `docs/agent/PROVENANCE.md` | 182 | HISTORY | \| `docs/agent/prompts/DISPATCH.md`, `STATE_EVICTION.md` \| ADAPTED \| this repo's paths, bans, route table... |
| `docs/agent/PROVENANCE.md` | 190 | HISTORY | mod" rather than "the pack", and `l3 --src` refuses a path with no `Lua/` under |
| `docs/agent/PROVENANCE.md` | 196 | HISTORY | `PUBLIC_SURFACE_SWEEP.md` / `SITE_AUDIT.md` (all bound to the fix pack's live |
| `docs/agent/reports/CHAIN_METHOD.md` | 8 | HISTORY | classed as intractable — F86 save-safety (discovery to verified repair of both |
| `docs/agent/reports/CHAIN_METHOD.md` | 45 | HISTORY | existed (C23 → F97 shipped at a fraction of its approved cost); a route |
| `docs/agent/reports/CHAIN_METHOD.md` | 46 | HISTORY | recorded *"verified feasible"* did not exist (F46, correctly declined); |
| `docs/agent/reports/CHAIN_METHOD.md` | 58 | HISTORY | the unlock.** "Build it, but it's not locked — the QA reviews it" (F97) |
| `docs/agent/reports/CHAIN_METHOD.md` | 71 | HISTORY | the terminal QA) independently validated the pack's evidence base AND |
| `docs/agent/reports/CHAIN_METHOD.md` | 72 | HISTORY | surfaced findings the informed record had missed (the F55 intent tell). |
| `docs/agent/reports/CHAIN_METHOD.md` | 113 | HISTORY | \| Routing without preconditions \| two items hopped 3 prompts each (a suite-run debt; C40's enacted-law ne... |
| `docs/agent/reports/CHAIN_METHOD.md` | 115 | HISTORY | \| Briefs staler than entries \| prompt 7's brief contradicted the C33 entry it described \| briefs cite en... |
| `docs/agent/reports/CHAIN_METHOD.md` | 120 | HISTORY | \| ⛔ A seal the standing rules defeat (f11-f99 chain, 2026-08-03) \| the sealed prompt 1 was force-fed seal... |
| `docs/agent/reports/CHAIN_METHOD.md` | 124 | HISTORY | \| ⛔ A run's preconditions include state a PREVIOUS chain mutated, and the unblock is owner-only (unattende... |
| `docs/agent/reports/CHAIN_METHOD.md` | 126 | HISTORY | \| ⛔ An attended sitting is a priority queue the owner may reorder live, and the brief's minutes model does... |
| `docs/agent/reports/CHAIN_METHOD.md` | 128 | HISTORY | \| ⛔ Evidence the terminal audit cannot re-read: owner verbatims that live only in the session transcript (... |
| `docs/agent/reports/CHAIN_METHOD.md` | 295 | HISTORY | the work.** L1 and L2 both read all 76 files. A lens is *a different question |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 8 | HISTORY | > telemetry `SMRFixPack.DroneReport()`), and `Code/Fix_ExtenderFlapChurn.lua` |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 9 | HISTORY | > (F77, default-on). See the D06 entry in BUGS.md. Registration-H, H-v2 |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 13 | HISTORY | DroneControl bullet + F77): *"what is even feasible if we want an optional overhaul |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 44 | HISTORY | priority is preserved for free.) The F73 "pre-wrap only" fact applies to command |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 87 | HISTORY | unreachable cache exactly as vanilla does; F55's fix already retires those). Perf: |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 152 | HISTORY | order unknowable, rule 1), the yield bought nothing; and it perturbs F50/F68/F71 |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 174 | HISTORY | **Risk: MEDIUM-HIGH.** Reset mid-command is the F50 churn primitive — used |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 201 | HISTORY | at the declaring class (F64 apply-check lesson applies). |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 274 | HISTORY | * **F77 debounce** (extender flap churn) — a plain repair, ships as `Fix_*` regardless |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 275 | HISTORY | of the overhaul decision; sketch on the F77 entry. Without it, any overhaul fights |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 277 | HISTORY | * **`SMRFixPack.DroneReport()`** — console/TestKit telemetry: per hub — handle, class, |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 309 | HISTORY | 7. **F77 fix** — separate `Fix_`, ships with the next wave independent of all above. |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 316 | HISTORY | machinery in the game — hubs, rovers, and the rocket cargo path (F50/F68/F70/F71) all |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 317 | HISTORY | run through these queues. Whatever subset is approved must re-pass the F50 |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 318 | HISTORY | rocket-churn and F55 unreachable scenarios, plus a new probe set (moonlight |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 516 | HISTORY | `are_requesters_connected` guard semantics. Debounce rebuilds using the F77 |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 549 | HISTORY | re-registration → F77 debounce. |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 648 | HISTORY | # I + J — seed-supply routing pair (added 2026-08-15 out of the fix pack's C47/C48 measurement chain) |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 652 | HISTORY | `C47`/`C48` seed-routing family lives HERE, in this house, behind this pack's |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 653 | HISTORY | default-OFF convention — the fix pack gets, at most, data-shaped repairs, and |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 654 | HISTORY | only after `C48` is ruled. This section is the standing record of that boundary. |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 656 | HISTORY | **Provenance.** The fix pack's `C48` leg (2026-08-15, `archive/c48veg_*` in that |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 728 | HISTORY | population churns fast — the C48 ladder watched it move 3,583 → 3,457 → |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 734 | HISTORY | the routing — the fix pack's planned intervention leg tests exactly this |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 737 | HISTORY | * ⛔⛔ **REFUTED 2026-08-15, the same evening, by that leg** (fix pack |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 753 | HISTORY | un-parking is an owner decision after launch. Cross-reference: fix pack |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 754 | HISTORY | `agent/bugs/C47.md` + `C48.md` (the measurements), this repo's `D02.md` (the |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 767 | HISTORY | carrying 985 decisions on 2026-08-16, fix pack `archive/c48pair2_*`): |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 795 | HISTORY | ⛔ **Engineering lessons that BIND any build here** (fix pack `EF-058/060`): |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | 809 | HISTORY | existing pairing-log instruments (fix pack `docs/agent/prompts/c48-pairing/`) |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 1 | HISTORY | # Readiness review — 2026-08-31: this workspace against the fix pack's tooling, tests and process |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 4 | HISTORY | fix pack's tools, tests, auditing, chain method and processes should apply here.* |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 5 | HISTORY | **Method:** inventory both repos (`C:\Dev\SMR-BugFixPack` @ `bec2e06`, this repo @ |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 18 | HISTORY | 2026-08-12 snapshot of the fix pack's method: doccheck GREEN, hook enabled, tree clean, |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 19 | HISTORY | and every improvement the fix pack made in the following 19 days absent. The three |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 37 | HISTORY | \| facts \| 58 here vs 68 there; **7 shared facts updated in the fix pack after the split, not carried** (E... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 38 | HISTORY | \| tools \| 5 here vs 20 there; the 14 missing include the whole L2–L8 audit ladder, the F107 wrap check, t... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 39 | HISTORY | \| doccheck drift \| donor gained: STATE byte budget (08-18), `tested-attended/-unattended` vocabulary (08-... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 40 | HISTORY | \| process docs \| WORKFLOW missing "Release marking — tags, not branches", the 08-24 probe rule, the byte-... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 61 | HISTORY | \| `l6_reachability.py` \| namespace \| 4 global replacements (`ChooseDome` 8 uses in 5 files; `SuppressNot... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 63 | HISTORY | \| `l8_hostile_input.py` \| namespace + module trio \| CONTROLs pass (documented form vetoes exactly `Class... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 75 | HISTORY | allocation rule** (fix pack allocates; this repo mirrors); a tools pointer. |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 76 | HISTORY | - **FIX_POLICY.md** §2: the F107 rule and the F110 rule, each adapted with this repo's |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 77 | HISTORY | own state (three allowlisted sites; `Opt_DroneStatDials` already does the F110 |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 83 | HISTORY | stays single-sourced in the fix pack with the playtest files. |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 92 | HISTORY | Survey of `C:\Dev\SMR-BugFixPack-TestKit` (100 probes; 94 excluding the 6 rescue |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 99 | HISTORY | \| **No opt-in-only run mode**: `RunAll(kind_filter)` filters on `kind`, never on owner; a standalone leg p... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 100 | HISTORY | \| **Enable-path leg hardcodes the fix pack**: `PACK_ID = "SMR_CommunityFixPack"` \| `98_EnablePathLeg.lua:... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 101 | CONTRACT | \| **`FixtureCarry` is blind to D09's residue**: channel 5 hardcodes `SMRFixPack_F35_`; channel 4 walks `ci... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 104 | HISTORY | \| `OptionsMenuFixPack` is the only opt probe that NEEDS the fix pack loaded (SKIPs otherwise) \| `60_Probe... |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 106 | HISTORY | ⇒ Owner decision **83** (fix pack checklist): authorise the kit edits. None was made |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 111 | HISTORY | 1. Walk the restore checklist — fix pack `reports/PARKED_OPTIN_REFERENCES.md` |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 112 | HISTORY | (~46 passages; the fix pack's `metadata.lua` change = its version bump). |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 117 | HISTORY | 4. Both-configuration ship test (with the fix pack, and with it absent) — |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 118 | HISTORY | `FIX_POLICY` §8; note which fix pack version it was tested beside. |
| `docs/agent/reports/READINESS_REVIEW_0831.md` | 121 | HISTORY | ## 7 · Owner decisions raised (mirrored on the fix pack's checklist, R10) |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 13 | HISTORY | rule). The fix pack keeps the measurement records (`C47.md`, `C48.md`) and |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 20 | HISTORY | Compressed from the fix pack's `agent/bugs/C47.md` + `C48.md`; every number |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 30 | HISTORY | **The template half (`C47`)**: Open Farm is the only template of 287 that |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 33 | HISTORY | but NOT the driver — the buffer only matters because of what follows. C47's |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 34 | HISTORY | one open thread — the owner's 1x-vs-speed observation — stays in the fix pack |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 37 | HISTORY | **The mechanism (`C48`), characterized by elimination — four experiments, the |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 73 | HISTORY | **Facts corrected/established along the way** (filed as fix pack `EF-058/059/ |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 83 | HISTORY | owner's words and the record's verdict. No fix-pack repair exists or will. |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 93 | HISTORY | "just size the buffer" shape (fix pack `C47.md` shape 1). OWNER, 2026-08-16:** |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 103 | HISTORY | storage problem's clothes.** The same ruling retired the fix pack's "don't fix |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 104 | HISTORY | C47 while C48 is open" caution: a buffer that cannot fill cannot mask anything. |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 147 | HISTORY | `C47FARM` only (fix pack `EF-056` autosave pre-copy ritual), predictions |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 149 | HISTORY | sources live in the fix pack's `docs/agent/prompts/c48-brake/` + |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 152 | HISTORY | instances** (fix pack `EF-058`). |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 154 | HISTORY | ## 3. What the fix pack keeps |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 156 | HISTORY | `C47.md` (the buffer/cadence record + the owner's open speed question and its |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 157 | HISTORY | designed descending-ladder control) · `C48.md` (the full measurement record) · |
| `docs/agent/reports/SEED_LOGISTICS_HANDOFF.md` | 159 | HISTORY | tests no fix). ⛔ No fix-pack code for this family, ever, per the two rulings. |
| `docs/agent/STATE.md` | 9 | POINTER | - BUILT 2026-08-12, VERIFIED IN GAME the same evening: `8/8` beside the fix pack; `8/8` with it |
| `docs/agent/STATE.md` | 10 | POINTER | UNINSTALLED; fix pack `74/74` with this mod absent. Audit CLOSED 08-12, everything SUSTAINED. |
| `docs/agent/STATE.md` | 12 | POINTER | `SMRFixPack_` bytes; write→save→reload broke 0 of 3 fields (`archive/SESSION_LOG.md`, 08-12). |
| `docs/agent/STATE.md` | 13 | POINTER | - ⛔ NOT PUBLISHED. 2026-08-17 (owner): the fix pack launched ALONE ("its not ready imo"); |
| `docs/agent/STATE.md` | 14 | POINTER | every player-facing reference to this mod was PARKED (fix pack `reports/PARKED_OPTIN_REFERENCES.md`). |
| `docs/agent/STATE.md` | 15 | POINTER | - 2026-08-31 READINESS PASS: tooling/process parity with the fix pack @ `bec2e06` restored. |
| `docs/agent/STATE.md` | 18 | POINTER | 1. walk the restore checklist — ~46 parked passages across the fix pack repo + `SMR-CommunityMods`; |
| `docs/agent/STATE.md` | 19 | POINTER | the fix pack's `metadata.lua` change = its version bump + re-upload; re-measure, doccheck, `mkdocs --strict`; |
| `docs/agent/STATE.md` | 24 | POINTER | 4. both-configuration ship test — with the fix pack and with it absent (`FIX_POLICY` §8), naming the version; |
| `docs/agent/STATE.md` | 39 | POINTER | Gate MEASURED `8/8` beside the fix pack, `1/8` at fresh defaults (owner's 08-12 18:30 log — the only record... |
| `docs/agent/STATE.md` | 42 | POINTER | - ⛔ PERSISTED NAMES ARE SAVE CONTRACT — the five `SMRFixPack_*` fields/modifier ids keep their bytes |
| `docs/agent/STATE.md` | 44 | POINTER | - ⛔ ZERO `SMRFixPack` references in executable code: the surviving tokens in `Code/` are the five |
| `docs/agent/STATE.md` | 50 | POINTER | fix pack `prompts/DRONE_PROJECT_PROMPT.md` §3 — the design decision is the owner's next call. |
| `docs/agent/STATE.md` | 57 | POINTER | - ✅ Remote PUBLIC 08-13 (`github.com/catt144/SMR-CommunityOptInPack`); title "Relaunched Fix Pack: |
| `docs/agent/STATE.md` | 61 | POINTER | - ⭐ 08-20 (owner, checklist 37 Q1): the fix pack's two `00_Core.lua` repairs (`2f077e8`) MIRRORED — |
| `docs/agent/STATE.md` | 65 | POINTER | - ⚖️ 08-31 WRAP CHECK (F107 rule, `FIX_POLICY` §2): 3 pre-rule sites allowlisted with Src citations — |
| `docs/agent/STATE.md` | 72 | POINTER | adjudication inherited (fix pack `reports/L8_ADVERSARIAL_MAP.md`); not a launch blocker there. |
| `docs/agent/STATE.md` | 74 | POINTER | `98_EnablePathLeg` hardcodes the fix pack's id; `FixtureCarry` blind to D09's modifiers; |
| `docs/agent/STATE.md` | 76 | POINTER | - ⛔ 08-31 FACTS: re-synced from the fix pack @ `bec2e06` (68 files); this repo's old `EF-057`/`EF-058` |
| `docs/agent/WORKFLOW.md` | 5 | HISTORY | > Copied from `SMR-BugFixPack/docs/agent/WORKFLOW.md` @ `33d69f5` on 2026-08-12 |
| `docs/agent/WORKFLOW.md` | 17 | POINTER | > 2. **The namespace** — `SMRFixPack.*` → `SMROptInPack.*` throughout. ⛔ NOT |
| `docs/agent/WORKFLOW.md` | 18 | POINTER | >    the persisted `SMRFixPack_*` field names (`agent/PROVENANCE.md` §2). |
| `docs/agent/WORKFLOW.md` | 25 | POINTER | > Where a clause says "the pack", read "this mod" — except where it names the |
| `docs/agent/WORKFLOW.md` | 26 | POINTER | > Relaunched Fix Pack (pre-2026-08-17 records: "Community Fix Pack") explicitly, |
| `docs/agent/WORKFLOW.md` | 41 | HISTORY | ⚠️ **This folder is a COPY of the fix pack's, taken 2026-08-12** and the two |
| `docs/agent/WORKFLOW.md` | 49 | HISTORY | the fix pack @ `bec2e06` (this repo's two became `EF-061`/`EF-062`, their |
| `docs/agent/WORKFLOW.md` | 50 | HISTORY | donor ids). From now on: a fact learned HERE is filed in the fix pack FIRST |
| `docs/agent/WORKFLOW.md` | 61 | POINTER | 5. ⚠️ **`C:\Dev\SMR-BugFixPack\docs\PLAYTEST_CHECKLIST.md`** — the owner's live |
| `docs/agent/WORKFLOW.md` | 114 | HISTORY | 2026-08-18, fix-pack checklist 42, carried here 2026-08-31; the 2026-08-03 |
| `docs/agent/WORKFLOW.md` | 131 | POINTER | what you commit, the same as the fix pack. |
| `docs/agent/WORKFLOW.md` | 132 | POINTER | - **Companion mod, a separate product:** `C:\Dev\SMR-BugFixPack` (Relaunched Fix |
| `docs/agent/WORKFLOW.md` | 133 | POINTER | Pack, remote `github.com/catt144/SMR-CommunityFixPack`). Shares no files with |
| `docs/agent/WORKFLOW.md` | 144 | POINTER | fix pack has its own junction (`SMR-BugFixPack`) beside it. |
| `docs/agent/WORKFLOW.md` | 146 | HISTORY | budget, load order, the F107 wrap check), the release gates |
| `docs/agent/WORKFLOW.md` | 152 | POINTER | - **Companion TestKit** (never shipped): `C:\Dev\SMR-BugFixPack-TestKit` |
| `docs/agent/WORKFLOW.md` | 166 | POINTER | Then enable "Relaunched Fix Pack: Opt-In Modules" in the game's Mod Manager (the |
| `docs/agent/WORKFLOW.md` | 175 | POINTER | (active / inactive+reason / disabled / error). The fix pack's own |
| `docs/agent/WORKFLOW.md` | 176 | POINTER | `SMRFixPack.ListFixes()` still exists in ITS env when it is installed — two |
| `docs/agent/WORKFLOW.md` | 177 | POINTER | registries, two log prefixes (`[CommunityOptInPack]` vs `[CommunityFixPack]`). |
| `docs/agent/WORKFLOW.md` | 221 | POINTER | grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/ |
| `docs/agent/WORKFLOW.md` | 242 | POINTER | 4. Both repos are in scope (the pack AND the TestKit) — the |
| `docs/agent/WORKFLOW.md` | 308 | HISTORY | flagged dome was *required* to receive, so it could not fail; F11's `nil` |
| `docs/agent/WORKFLOW.md` | 313 | HISTORY | selection half by reconstructing the pool and reading it (F11's |
| `docs/agent/WORKFLOW.md` | 317 | HISTORY | compute its expectation with the fix's own logic** (adopted in the fix pack |
| `docs/agent/WORKFLOW.md` | 320 | HISTORY | patched cannot fail on a broken dispatch (the fix pack's F33 probe printed |
| `docs/agent/WORKFLOW.md` | 323 | HISTORY | (its C50 probe). So: dispatch through the production route (an |
| `docs/agent/WORKFLOW.md` | 332 | HISTORY | count** (adopted 2026-08-04, co-run #1 correction C10). "Absence under N |
| `docs/agent/WORKFLOW.md` | 352 | POINTER | 4. Save with mod enabled → **disable the pack in the MOD MANAGER** → load: game |
| `docs/agent/WORKFLOW.md` | 358 | HISTORY | 98 errors/session with its own toggle OFF; that is how F86 Site 2 was found. |
| `docs/agent/WORKFLOW.md` | 451 | POINTER | > ⭐ **THIS REPO'S TWIN of the fix pack's clause, installed at the split** |
| `docs/agent/WORKFLOW.md` | 453 | POINTER | > `[CommunityFixPack]` line in one of THIS mod's legs is expected background, |
| `docs/agent/WORKFLOW.md` | 464 | POINTER | 1. **The baseline rig configuration is BOTH mods enabled** — the fix pack AND |
| `docs/agent/WORKFLOW.md` | 466 | POINTER | BASELINE (cell a2, 2026-08-12, audit-recounted from the fix pack's |
| `docs/agent/WORKFLOW.md` | 467 | POINTER | `archive/spa2_Mars.exe-20260812-18.44.24.log`): `fix pack present: 74/74` · |
| `docs/agent/WORKFLOW.md` | 469 | POINTER | 2026-08-13 (fix pack `archive/rs_r0_*`): `78 PASS / 0 FAIL / 16 SKIP / |
| `docs/agent/WORKFLOW.md` | 473 | POINTER | load order `1:SMR_CommunityFixPackTestKit 2:SMR_CommunityFixPack |
| `docs/agent/WORKFLOW.md` | 475 | POINTER | OUTERMOST).** Every "the pack" claim names WHICH pack. A fix-pack line |
| `docs/agent/WORKFLOW.md` | 543 | HISTORY | 2026-08-05 lead the owner scored as a miss on its own target banked `F101` |
| `docs/agent/WORKFLOW.md` | 544 | HISTORY | and both F99 samples, and earlier leads produced the F02 watchdog challenge |
| `docs/agent/WORKFLOW.md` | 565 | HISTORY | five minutes to observe it (the F11-conversion watch, staged fixtures); |
| `docs/agent/WORKFLOW.md` | 569 | HISTORY | (C41's vanishing picker is the poster child); |
| `docs/agent/WORKFLOW.md` | 588 | HISTORY | - ⛔ **The forced-vs-organic rule (the F99 lesson):** forcing an *upstream |
| `docs/agent/WORKFLOW.md` | 598 | HISTORY | inline one-liner through PowerShell** (co-run #1, correction C11: an inline |
| `docs/agent/WORKFLOW.md` | 602 | HISTORY | ⚠️ **C11 corollary (unattended-1, I2): a script file is not enough if its |
| `docs/agent/WORKFLOW.md` | 739 | POINTER | clean log of the pack RUNNING was not banked as a clean uninstall. |
| `docs/agent/WORKFLOW.md` | 745 | POINTER | exactly that — `corun-batch-2`'s leg T had disabled the pack the day |
| `docs/agent/WORKFLOW.md` | 755 | POINTER | `SMROptInPack_Disabled` console veto covers only D12/F97-class modules — |
| `docs/agent/WORKFLOW.md` | 771 | HISTORY | produced F85's dead F9-rebind advice: this chain's brief and payload menu |
| `docs/agent/WORKFLOW.md` | 774 | HISTORY | F07 entry). A source-derived instruction is a claim; the brief says so. |
| `docs/agent/WORKFLOW.md` | 777 | HISTORY | sitting archived one of four owner quotes (F85's); the other three exist |
| `docs/agent/WORKFLOW.md` | 822 | POINTER | `LoadGame` brought it back live with the pack still reading 81/81 — a full |
| `docs/agent/WORKFLOW.md` | 922 | POINTER | ## Release marking — tags, not branches (adopted in the fix pack 2026-08-17, carried 2026-08-31) |
| `docs/agent/WORKFLOW.md` | 950 | POINTER | - The prefix is `optin-` (the fix pack's is `fixpack-`, the rescue's `rescue-`); |
| `docs/agent/WORKFLOW.md` | 954 | POINTER | and never by hand (the fix pack's H-02): every Mod Editor save runs |
| `docs/agent/WORKFLOW.md` | 956 | POINTER | - Record portal version → commit sha on the fix pack's ④ sheet |
| `docs/agent/WORKFLOW.md` | 957 | POINTER | (`SMR-BugFixPack/docs/agent/reports/RELEASE_PORTAL_PREP.md`) in the same pass. |
| `docs/agent/WORKFLOW.md` | 989 | STALE-FIXED | >    without the Relaunched Fix Pack. |
| `docs/agent/WORKFLOW.md` | 1000 | POINTER | > 5. **⛔ ADD:** ship-testing is TWO configurations, not one — with the fix pack |
| `docs/agent/WORKFLOW.md` | 1009 | POINTER | >    no `image` field and no `preview.png` (the fix pack's is |
| `docs/agent/WORKFLOW.md` | 1014 | POINTER | >    checklist in the fix pack's `reports/PARKED_OPTIN_REFERENCES.md` (~46 |
| `docs/agent/WORKFLOW.md` | 1025 | HISTORY | 2026-08-04: F55, F40, F73(b), F70, F97 presented as design-judgment repairs, |
| `docs/agent/WORKFLOW.md` | 1160 | STALE-FIXED | - "Put the mod back" as advice for a damaged save, and its F88 caveat — |
| `docs/agent/WORKFLOW.md` | 1161 | STALE-FIXED | `agent/bugs/` F88 entry. |
| `docs/agent/WORKFLOW.md` | 1169 | STALE-FIXED | 2026-08-01 but **written conditionally and marked do-not-publish until F86 |
| `docs/FUTURE_IDEAS.md` | 8 | HISTORY | owner decision on the fix pack's `docs/PLAYTEST_CHECKLIST.md`. |
| `docs/FUTURE_IDEAS.md` | 12 | HISTORY | future ideas doc … want [the fix pack's] folder reserved for only bug related |
| `docs/FUTURE_IDEAS.md` | 13 | HISTORY | items."* The six entries below moved here whole from the fix pack's |
| `docs/FUTURE_IDEAS.md` | 15 | HISTORY | only bug-related parking. **The fix pack file's HARD RULE travels with them |
| `docs/FUTURE_IDEAS.md` | 22 | HISTORY | # Parked items (all moved 2026-08-14 from the fix pack's FUTURE_IDEAS.md) |
| `docs/FUTURE_IDEAS.md` | 129 | HISTORY | string cannot be replaced** — re-using its id discards the replacement (**F98**, |
| `docs/FUTURE_IDEAS.md` | 133 | HISTORY | is our own `ModItemLocTable` — the F84/D10 work already parked to post-release. |
| `docs/FUTURE_IDEAS.md` | 135 | HISTORY | **Where the material lives.** F98 and F84 entries in the FIX PACK's |
| `docs/FUTURE_IDEAS.md` | 136 | HISTORY | `agent/bugs/` (that half of the material stays fix-pack-side); the append route |
| `docs/FUTURE_IDEAS.md` | 138 | HISTORY | light-userdata form, shipped precedent `Workplace.lua:293`) is recorded on F98. |
| `docs/FUTURE_IDEAS.md` | 173 | HISTORY | **Where the material lives.** `F101.md` (`wontfix`) in the FIX PACK's |
| `docs/FUTURE_IDEAS.md` | 184 | HISTORY | **To un-park.** Launch first, then an explicit owner decision. F101 stays |
| `docs/FUTURE_IDEAS.md` | 185 | HISTORY | `wontfix` in the fix pack either way — the fix pack never grows a cheat surface. |
| `docs/FUTURE_IDEAS.md` | 189 | HISTORY | ## 6. D01 export half — standing PreciousMetals demand (+ F56 auto-offload) |
| `docs/FUTURE_IDEAS.md` | 195 | HISTORY | dialog. It also **owns F56** (auto RC Transports never offload into rockets), |
| `docs/FUTURE_IDEAS.md` | 199 | HISTORY | **What it relates to.** `Opt_ClassicRockets` (this repo); F56 (fix pack |
| `docs/FUTURE_IDEAS.md` | 201 | HISTORY | F50/F68/F70/F71. |
| `docs/FUTURE_IDEAS.md` | 209 | HISTORY | thresholds). *(In the fix pack file this sat under "proposed for parking, |
| `docs/FUTURE_IDEAS.md` | 224 | HISTORY | **What.** Two complementary drone-judgment options born out of the fix pack's |
| `docs/FUTURE_IDEAS.md` | 225 | HISTORY | `C47`/`C48` farm investigation: **(I) a seeds-only cargo top-up** — after a |
| `docs/FUTURE_IDEAS.md` | 232 | HISTORY | ⚖️ **Why it is parked HERE and may never touch the fix pack — owner ruling |
| `docs/FUTURE_IDEAS.md` | 243 | HISTORY | **Where the material lives.** That report section; fix pack `agent/bugs/C47.md` |
| `docs/FUTURE_IDEAS.md` | 244 | HISTORY | + `C48.md` (the measurements); this repo's `D02.md` (the flapping boundary from |
| `docs/FUTURE_IDEAS.md` | 248 | HISTORY | also hangs on the fix pack's brake-intervention leg — if that refutes the |
| `docs/FUTURE_IDEAS.md` | 252 | HISTORY | and fix pack `agent/bugs/C48.md`). |
| `docs/FUTURE_IDEAS.md` | 297 | HISTORY | precisely why this is not a fix-pack item. |
| `docs/FUTURE_IDEAS.md` | 314 | HISTORY | cannot enter the fix pack. Severity is feel, not function — the law is |
| `docs/FUTURE_IDEAS.md` | 322 | HISTORY | fix pack as `EF-061`/`EF-062` — amend both or neither. This entry keeps only |
| `docs/FUTURE_IDEAS.md` | 339 | HISTORY (Pass-B: OWNER — FUTURE_IDEAS #9) | **What.** A player-facing on/off switch per fix in the **fix pack** (not this |
| `docs/FUTURE_IDEAS.md` | 341 | HISTORY (Pass-B: OWNER — FUTURE_IDEAS #9) | listing the modules with checkboxes. Parked HERE and not in the fix pack's own |
| `docs/FUTURE_IDEAS.md` | 349 | HISTORY (Pass-B: OWNER — FUTURE_IDEAS #9) | - the `SMRFixPack_Disabled` veto is read at mod load (`00_Core.lua:384-388`), |
| `docs/FUTURE_IDEAS.md` | 354 | HISTORY (Pass-B: OWNER — FUTURE_IDEAS #9) | - ⛔ the fix pack has **no Mod Options page at all**, and the reason matters: |
| `docs/FUTURE_IDEAS.md` | 358 | HISTORY (Pass-B: OWNER — FUTURE_IDEAS #9) | ⇒ The argument gets stronger as the pack grows: 75 modules today, and the |
| `docs/FUTURE_IDEAS.md` | 391 | HISTORY | of diagnosing a fix-pack field report (`SMR-BugFixPack` `agent/bugs/F104.md`, |
| `docs/FUTURE_IDEAS.md` | 456 | HISTORY | landed on us. See `EF-065` in the fix pack. |
| `docs/FUTURE_IDEAS.md` | 498 | HISTORY | Fix pack `docs/agent/bugs/F104.md` (full derivation, the live stack capture, the |
| `docs/FUTURE_IDEAS.md` | 500 | HISTORY | Fix pack `docs/agent/facts/EF-065.md` (why the wrong mod gets named). |
| `docs/FUTURE_IDEAS.md` | 508 | HISTORY | read is an inference. ⚖️ **Fix pack ruling 2026-08-23 (owner):** naming the mod |
| `docs/README.md` | 4 | POINTER | `SMR-BugFixPack`'s tree so one set of habits serves both repos. **Human docs at |
| `docs/README.md` | 31 | POINTER | `C:\Dev\SMR-BugFixPack\docs\`** and are NOT duplicated here. |
| `docs/README.md` | 51 | POINTER | `_preamble.md`, **copied whole from the fix pack @ `33d69f5` on 2026-08-12 and |
| `docs/README.md` | 55 | POINTER | fix pack** (`agent/WORKFLOW.md`, reading path 2): file a new fact there first, |
| `metadata.lua` | 5 | HISTORY | -- ⭐ FAMILY RENAMED (owner, 2026-08-17, fix-pack checklist 36): "Community |
| `metadata.lua` | 6 | HISTORY | -- Fix Pack" → "Relaunched Fix Pack" across the whole set, before any upload; |
| `metadata.lua` | 11 | HISTORY | -- description draft in the fix-pack repo's STORE_METADATA_STRINGS.md |
| `metadata.lua` | 13 | POINTER | 'title', "Relaunched Fix Pack: Opt-In Modules", |
| `metadata.lua` | 14 | POINTER | 'description', "Eight opt-in modules for Surviving Mars: Relaunched — every one of them off, or at its vani... |
| `metadata.lua` | 15 | POINTER | 'short_description', "Eight opt-in gameplay modules, all off or at base until you enable them in Mod Option... |
| `metadata.lua` | 16 | HISTORY | -- Split out of the Community Fix Pack on 2026-08-12: these eight modules |
| `metadata.lua` | 19 | POINTER | 'last_changes', "Initial release: the eight optional modules, split out of the Relaunched Fix Pack into the... |
| `metadata.lua` | 39 | HISTORY | -- ⭐ THREE PATTERNS ADDED 2026-08-14 AT LAUNCH PREP (fix-pack chain |
| `metadata.lua` | 46 | HISTORY | -- ⚠️ `LICENSE` is NOT excluded, deliberately — see the fix pack's note. |
| `metadata.lua` | 82 | HISTORY | -- relative order they had in the fix pack: CohortHousing before NoHomeless |
| `items.lua` | 2 | POINTER | -- (Options → Mod Options → Relaunched Fix Pack: Opt-In Modules). Moved here from the |
| `items.lua` | 3 | HISTORY | -- Community Fix Pack on 2026-08-12 with the split; the entries below are |
| `README.md` | 1 | POINTER | # Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched |
| `README.md` | 9 | POINTER | **It works with or without the Relaunched Fix Pack.** The two mods are separate |
| `CLAUDE.md` | 1 | POINTER | # Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched |
| `CLAUDE.md` | 3 | HISTORY | ✅ **Display name DECIDED (owner, 2026-08-13): "Community Fix Pack: Opt-In |
| `CLAUDE.md` | 6 | HISTORY | fix-pack checklist 36): now "Relaunched Fix Pack: Opt-In Modules"** — live |
| `CLAUDE.md` | 16 | POINTER | **TRUE STANDALONE** — it works with the Relaunched Fix Pack installed, and |
| `CLAUDE.md` | 20 | HISTORY | > **Split out of `SMR-BugFixPack` @ `33d69f5` on 2026-08-12** (chain |
| `CLAUDE.md` | 23 | HISTORY | > and what was adapted. Pre-split records in the fix pack cite `Code/Opt_*.lua` |
| `CLAUDE.md` | 24 | POINTER | > paths in THAT repo and the `SMRFixPack` namespace; translate mentally, do not |
| `CLAUDE.md` | 30 | POINTER | savegame keeps its EXACT bytes — including every `SMRFixPack_*` field and |
| `CLAUDE.md` | 34 | POINTER | 2. **ZERO `SMRFixPack` references in executable code.** The framework is this |
| `.claude/settings.json` | 6 | POINTER | "PowerShell(git -C C:\\Dev\\SMR-BugFixPack worktree list)", |
| `.claude/settings.json` | 7 | POINTER | "PowerShell(git -C C:\\Dev\\SMR-BugFixPack branch -a)", |
| `.claude/settings.json` | 8 | POINTER | "PowerShell(git -C C:\\Dev\\SMR-BugFixPack-TestKit worktree list)", |
| `.claude/settings.json` | 9 | POINTER | "PowerShell(git -C C:\\Dev\\SMR-BugFixPack-TestKit branch -a)" |

---

## Appendix A · The inventory, verbatim (tree `d3d9053`, 817 lines)

Command, run from the repo root (`docs/archive/` excluded by the trailing filter):

```
grep -rn --include=*.lua --include=*.py --include=*.md --include=*.json -E \n  "SMRFixPack|CommunityFixPack|SMR_CommunityFixPack|SMR-BugFixPack|SMR-CommunityFixPack|[Ff]ix[ -][Pp]ack|Fix_[A-Z]|F[0-9]{2,3}|C[0-9]{2}|the pack|76 files|75 modules|80 modules" \n  Code/ tools/ docs/ metadata.lua items.lua README.md CLAUDE.md LICENSE .claude/ \n  | grep -v "^docs/archive/"
```

```
Code/00_Core.lua:1:-- Relaunched Fix Pack: Opt-In Modules — core registry.
Code/00_Core.lua:61:-- never guess — an unkeyed restart is exactly F88's defect (F86 Tier 1).
Code/00_Core.lua:76:-- otherwise masquerade as "game update changed it" (how F64 shipped broken).
Code/00_Core.lua:166:-- requires (the F22 donor): plain assignment reaches the real _G through
Code/00_Core.lua:191:-- generalises the Fix_LastTransmissionStorage donor; the F75, B3 and A1
Code/00_Core.lua:201:-- `run()` at apply time is a NO-OP by design since F87 (see below) — the runner
Code/00_Core.lua:208:--   * ctx.classes_built — nothing runs before flattening (F87);
Code/00_Core.lua:211:--   * ctx.data_loaded — sites gate their missing-target latch on it (the F75
Code/00_Core.lua:223:-- F87 (2026-07-31): the runner no longer does work at apply time, and it owns
Code/00_Core.lua:231:-- Fix_DustSicknessBiorobots threw exactly there.
Code/00_Core.lua:261:			-- MIRRORED 2026-08-20 from the fix pack's `Code/00_Core.lua` (2f077e8),
Code/00_Core.lua:262:			-- on the owner's ruling (fix-pack checklist 37 Q1). Same leak as
Code/00_Core.lua:274:		-- F87: never before flattening. `g_Classes` is NOT a usable test here —
Code/00_Core.lua:285:		-- That is the F87 failure mode (silently unfixed), so own the error the
Code/00_Core.lua:301:	-- enable path as "presets not loaded yet" and never fire (the F75 gap again).
Code/00_Core.lua:332:-- WITHOUT the runner's latch/heal contract (F87 sweep, 2026-07-31 — it found
Code/00_Core.lua:374:		-- ⛔ MIRRORED 2026-08-20 from the fix pack's `Code/00_Core.lua` (2f077e8),
Code/00_Core.lua:375:		-- owner ruling (fix-pack checklist 37 Q1). `Require` marks
Code/00_Core.lua:404:	-- ⛔ MIRRORED 2026-08-20 from the fix pack's `Code/00_Core.lua` (2f077e8),
Code/00_Core.lua:405:	-- owner ruling (fix-pack checklist 37 Q1). The append below used to be
Code/00_Core.lua:497:-- from the pack's target-changed/install-failed conventions. Opt-in state,
Code/00_Core.lua:536:-- never claims the rest of the pack is verified; the after-every-patch
Code/00_Core.lua:552:			Untranslated("Relaunched Fix Pack: Opt-In Modules"),
Code/00_Core.lua:554:				"%d of this mod's modules found that the game code they patch has changed — usually after a game update — and switched themselves off for safety.\n\nModules that cannot detect such changes may still need attention: if the game was recently updated, check for a new version of the Relaunched Fix Pack: Opt-In Modules.\n\nSwitched off: %s", #suspects, list)))
Code/00_Core.lua:558:-- Console helper: print what the pack did this session.
Code/Opt_AcknowledgedWarnings.lua:3:-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles
Code/Opt_AcknowledgedWarnings.lua:17:-- is a building entombed by a landscaping lake (F30) — re-nags every 4 game
Code/Opt_AcknowledgedWarnings.lua:35:--     one-shot adds where dismissal already holds — F32 trace).
Code/Opt_AcknowledgedWarnings.lua:39:-- captured as a file-local there, so replacement globals are seen — the F22
Code/Opt_AcknowledgedWarnings.lua:58:-- Savegame footprint (FIX_POLICY §3): `SMRFixPack_ack_notworking = true` on
Code/Opt_AcknowledgedWarnings.lua:68:local FLAG = "SMRFixPack_ack_notworking"
Code/Opt_AcknowledgedWarnings.lua:94:		-- mod-load time (the F75 lesson) — do not "verify" the preset here. The
Code/Opt_ClassicRockets.lua:3:-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles
Code/Opt_ClassicRockets.lua:21:-- behaviour get it here, opt-in, so the pack itself stays a pure bug-fix mod
Code/Opt_ClassicRockets.lua:53:-- already answers, including F69's asteroid-lander reserve, falls through
Code/Opt_ClassicRockets.lua:60:-- same machinery as F50, F68, F70 and F71. It is deliberately left for a design
Code/Opt_CohortHousing.lua:3:-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; the
Code/Opt_DroneOverhaul.lua:42:--     preserved for free (the F73 "pre-wrap only" rule is for command bodies
Code/Opt_DroneOverhaul.lua:74:-- ⚠️ F86 SITE 2 — the "saves load identically without it" claim this header used
Code/Opt_DroneOverhaul.lua:79:-- thread, and on the next load without the pack each one threw
Code/Opt_DroneOverhaul.lua:87:-- F86 TIER-2 REPAIR (2026-08-01, owner carve-out pre-granted): the hook moved to
Code/Opt_DroneOverhaul.lua:216:	-- Idle itself (F86 Site 2 — see the header). Same trigger, same order, but
Code/Opt_DroneStatDials.lua:3:-- Two Mod Options dropdowns (Options → Mod Options → Relaunched Fix Pack: Opt-In Modules):
Code/Opt_DroneStatDials.lua:48:-- ("SMRFixPack_DroneSpeedDial" / "SMRFixPack_DroneCarryDial") in UIColony's
Code/Opt_DroneStatDials.lua:64:local SPEED_MOD_ID = "SMRFixPack_DroneSpeedDial"
Code/Opt_DroneStatDials.lua:65:local CARRY_MOD_ID = "SMRFixPack_DroneCarryDial"
Code/Opt_DroneStatDials.lua:76:-- Pre-flattening rules (ENGINE_FACTS, the F64 lesson — and this module's own
Code/Opt_MultipleSuns.lua:3:-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles
Code/Opt_MultipleSuns.lua:19:-- UIColony.labels). PT-26 (2026-07-27) proved that makes the pack's original
Code/Opt_MultipleSuns.lua:20:-- F39 fix unreachable dead code in an unmodded game: two suns can never
Code/Opt_MultipleSuns.lua:30:--      after DataLoaded — the GlobalMap is EMPTY at mod-load time, the F75
Code/Opt_MultipleSuns.lua:34:--      at all and this lift used to be skipped for the session — F87). The
Code/Opt_MultipleSuns.lua:39:--   2. BINDING FIX (absorbed from the deleted Fix_SecondArtificialSun.lua,
Code/Opt_MultipleSuns.lua:101:			-- FIX (F39, absorbed): the shipped body only ever tested
Code/Opt_MultipleSuns.lua:145:-- "active"), which OnMsg handlers must re-check themselves (the F75 lesson).
Code/Opt_MultipleSuns.lua:192:-- F87 sweep: this used to hang off DataLoaded/DataChanged alone, and neither
Code/Opt_NoHomeless.lua:3:-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; the
Code/Opt_NoHomeless.lua:52:--     SMRFixPack_closed_to_new_residents (D03) off → children can still migrate in
Code/Opt_NoHomeless.lua:53:--     SMRFixPack_no_homeless             (D12) on  → graduates are pushed out
Code/Opt_NoHomeless.lua:59:-- outside with no dome dies (F53 territory); that failure mode is made
Code/Opt_NoHomeless.lua:153:-- narrow reading was immune to the CAPACITY-CHURN mechanism (BUGS.md C40) — a
Code/Opt_NoHomeless.lua:197:-- Savegame footprint (FIX_POLICY §3): `SMRFixPack_no_homeless` on the
Code/Opt_NoHomeless.lua:205:local FLAG = "SMRFixPack_no_homeless"
Code/Opt_NoHomeless.lua:217:-- `Fix_DustDevilSpawnGate` checks both (`:332-334`), which is why its A/B
Code/Opt_NoHomeless.lua:615:-- Strings are Untranslated (F98, 2026-08-02): re-using a shipped translation id
Code/Opt_NoHomeless.lua:747:			self:SetRolloverTitle(Untranslated("Dedicated Dome Policy (Relaunched Fix Pack: Opt-In Modules)"))
Code/Opt_NoHomeless.lua:808:			  -- F100: the old string said "game update changed the Workforce mixin?"
Code/Opt_ResidencyControl.lua:3:-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05; toggles
Code/Opt_ResidencyControl.lua:24:-- forced quarantine — the F61 entry records the survey; the pack's earlier F61
Code/Opt_ResidencyControl.lua:60:-- Savegame footprint (FIX_POLICY §3): `SMRFixPack_closed_to_new_residents` on
Code/Opt_ResidencyControl.lua:63:-- flag loads fine with the module (or the pack) removed.
Code/Opt_ResidencyControl.lua:67:local FLAG = "SMRFixPack_closed_to_new_residents"
Code/Opt_ResidencyControl.lua:147:			self:SetRolloverTitle(Untranslated("Residency Policy (Relaunched Fix Pack: Opt-In Modules)"))
tools/audit_preset_fields.py:1:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/doccheck.py:12:split, carried across from SMR-BugFixPack @ bec2e06 — (1) STATE.md is
tools/doccheck.py:17:`metadata.lua`'s `code` list are enforced, not just commented; (4) the F107
tools/doccheck.py:20:single-sourced in the fix pack (docs/README.md).
tools/doccheck.py:23:SMR-BugFixPack @ 33d69f5. Four deliberate differences, each recorded in
tools/doccheck.py:29:would have read 67 on the post-split fix-pack side); (3) the three STUBS are
tools/doccheck.py:33:fix pack emits and is labelled so it can never read as a second suite.
tools/doccheck.py:60:# is the SAME number the fix pack's doccheck emits, not a second suite.
tools/doccheck.py:61:TESTKIT = os.environ.get("SMR_TESTKIT", r"C:\Dev\SMR-BugFixPack-TestKit")
tools/doccheck.py:73:# defeated — single lines grew into thousand-word walls (the fix pack's hit
tools/doccheck.py:92:# the fix pack and only checked if someone ever copies it here.
tools/doccheck.py:105:# Index rows. Trap (a): this pattern also matches a rate table inside the F97
tools/doccheck.py:106:# entry (`| F97 | **50%** (gate fails) | ...`) — dedupe by ID, keep the FIRST.
tools/doccheck.py:110:# their own `###` sub-headings (e.g. F97's "### THE UNINSTALL LOG..."), so the
tools/doccheck.py:121:# ⚖️ Owner ruling 2026-08-15 (fix-pack checklist 26b), carried 2026-08-31:
tools/doccheck.py:546:    # `- 7` was accidentally right only while the pack held exactly 7 gated
tools/doccheck.py:559:        out.append("NOTE: the TestKit at %s is SHARED with the fix pack — the "
tools/doccheck.py:636:# Provenance of the rules: INHERITED from the fix pack's order, MEASURED as the
tools/doccheck.py:703:    """FIX_POLICY §2, the F107 rule (donor 2026-08-24, here 2026-08-31): every
tools/doccheck.py:744:                         "which only exists in SMR-BugFixPack's history")
tools/doccheck.py:749:                         "SMR-BugFixPack's history")
tools/harvest_wrap_targets.py:2:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/harvest_wrap_targets.py:7:the fix pack, where the tool was born, had estimated "~60" and measured 105). A hand-typed list is a silent under-sweep, and an
tools/harvest_wrap_targets.py:143:# --check: the F107 rule (this repo's FIX_POLICY §2; adopted in the fix pack
tools/harvest_wrap_targets.py:150:# (the fix pack's F107: a module captured a leaf class's method while declaring
tools/harvest_wrap_targets.py:158:# F107 records that limitation); a hit is real. RED means: add the pair to the
tools/harvest_wrap_targets.py:168:    # module and sits with the owner (fix-pack checklist, 2026-08-31 items).
tools/harvest_wrap_targets.py:178:_NOT_CLASSES = {"SMROptInPack", "SMRFixPack", "SMRTest", "_G"}
tools/l2_reload_sim.py:3:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/l2_reload_sim.py:14:    mirrored here from the fix pack's repair (2f077e8) and STATE records it as
tools/l3_save_footprint.py:2:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/l3_save_footprint.py:17:  3. NAMED STATE   — every `SMRFixPack_*` / `SMROptInPack_*` token: the
tools/l3_save_footprint.py:95:NAMED_STATE = re.compile(r'\b(?:SMRFixPack|SMROptInPack)_(\w+)')
tools/l3_save_footprint.py:99:# second hid two of the fix pack's PostLoadGame passes from the load-order
tools/l3_save_footprint.py:188:    if resolved.startswith(("SMROptInPack", "SMRFixPack")):
tools/l3_save_footprint.py:278:            # (`local FLAG = "SMRFixPack_..."`), so these two scan the code line
tools/l3_save_footprint.py:343:    print("--- 3. NAMED STATE (persisted `SMRFixPack_*` + framework `SMROptInPack_*`) " + "-" * 8)
tools/l3_save_footprint.py:385:    # 7. ⭐ MOD-AUTHORED PERSISTED KEYS — the census the `SMRFixPack_*` token
tools/l3_save_footprint.py:429:            conv = ("SMRFixPack_" in field) or ("SMROptInPack_" in field)
tools/l4_player_surfaces.py:2:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/l5_containment.py:2:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/l5_containment.py:26:  3. DEFERRED   — the F87 shape: modules whose actual repair work happens AFTER
tools/l5_containment.py:38:adjudication belongs in a lens report made by reading the line (the fix pack's
tools/l5_containment.py:109:    r"=\s*(\{|\"|'|\d|true|false|nil|rawget\s*\(|SMRFixPack[.\[]|function\b)"
tools/l5_containment.py:174:                        r"^function\s+(OnMsg|SMRFixPack)\.", body) else "check"
tools/l5_containment.py:274:    print("=== 3 . DEFERRED-WORK (F87) SET — work that happens after apply returns ===")
tools/l6_promise_map.py:2:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/l6_promise_map.py:135:    QUOTED IN A HEADER counted as a real site — a fix-pack module's header was the
tools/l6_reachability.py:2:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/l6_reachability.py:5:The L6 lens question: "Dead-coded targets: is F85 the only one? Its
tools/l6_reachability.py:14:⛔ A count is a triage instrument, not a verdict. 0 callers is the F28 shape
tools/l6_reachability.py:15:and 1-2 callers is where the F85 shape hides; both are printed for reading, and
tools/l6_reachability.py:192:        flag = "  <- ZERO shipped uses (F28 shape)" if uses <= 0 else (
tools/l6_reachability.py:193:            "  <- FEW — read every one (F85 shape)" if uses <= 2 else "")
tools/l7_env_map.py:58:    python tools/l7_env_map.py --tree ../SMR-BugFixPack-TestKit
tools/l8_hostile_input.py:3:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/pack_predict.py:2:# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
tools/pack_predict.py:11:seed note in the fix pack's SWEEP_LEDGER.md), `?` is one char. Case-insensitive is NOT
tools/split_bugs.py:9:PORTED 2026-08-12 (split-optins prompt 3) from SMR-BugFixPack @ 33d69f5.
tools/split_bugs.py:38:            entries carry their own `##`/`###` sub-headings (F97's rate-question
tools/split_bugs.py:39:            block, D12's "WHAT D12 SHIPS", F86/F87's `> ##` quotes).
tools/split_bugs.py:41:            FOLLOWS the C41 entry and is not part of it.
tools/split_bugs.py:50:  35 INDEX ROWS HAVE NO HEADING OF THEIR OWN — C02 and 34 IDs whose text lives
tools/split_bugs.py:53:  the generated INDEX can still carry all 151 rows; C02, which has no entry text
tools/split_bugs.py:84:# A grouped section's members are its `- **C12 ...` bullets.
tools/split_bugs.py:106:    {"C02"}
tools/split_bugs.py:112:# stated range ("C12-C31") is STALE — it holds C12 through C38 — so the FILE
tools/split_bugs.py:114:GROUPED_FILES = {"C03": "C03-C11", "C12": "C12-C38"}
tools/split_bugs.py:117:EXPECTED_ORPHANS = {"C02"}
tools/split_bugs.py:276:    # The F97 rate table also starts its lines with `| F97 |`; it lives inside
tools/split_bugs.py:428:            # C01 and the two grouped headings carry no tag; the row is all
tools/split_bugs.py:516:        "**C02 has an index row and no entry text anywhere in BUGS.md** (verified",
tools/split_bugs.py:576:        "entries moved here from SMR-BugFixPack (split-optins, 2026-08-12); "
tools/split_facts.py:9:PORTED 2026-08-12 (split-optins prompt 3) from SMR-BugFixPack @ 33d69f5.
tools/upload_preflight.py:3:WHY THIS EXISTS (2026-08-17). The fix pack reached its upload sitting with no
docs/agent/bugs/D01.md:15:from: "SMR-BugFixPack docs/agent/bugs/D01.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D01.md:59:Options → Mod Options since D05, or via the pre-load `SMRFixPack_Optional` override; the
docs/agent/bugs/D01.md:73:citation corrected by the QA audit 2026-07-25) — so there is no refuel spam. F69's asteroid-lander reserve is untouched — the wrapper only acts when the
docs/agent/bugs/D01.md:78:means editing the same machinery as F50, F68, F70 and F71 — with no way to test the result
docs/agent/bugs/D01.md:105:auto-offload into rockets — that answer decides whether F56's behavior rides
docs/agent/bugs/D01.md:109:*The export half now also owns F56.* F56 (auto RC Transports never offload rockets) closed
docs/agent/bugs/D02.md:15:from: "SMR-BugFixPack docs/agent/bugs/D02.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D02.md:18:Spun out of F32's close (2026-07-26, user decision) — read that entry for the full trace.
docs/agent/bugs/D02.md:31:acknowledgment at all. An unfixable building — F30's lake-entombed case is the
docs/agent/bugs/D02.md:48:Ack set persisted as an absent-tolerant `SMRFixPack_*` handle set (policy §3).
docs/agent/bugs/D02.md:50:where dismissal already holds (F32 trace).
docs/agent/bugs/D02.md:57:Notifications.lua, so replacements are seen — F22 precedent): `SuppressNotification`
docs/agent/bugs/D02.md:59:listed building with `SMRFixPack_ack_notworking = true` and SKIPS the shipped whole-id
docs/agent/bugs/D02.md:85:* **Save/reload:** the `SMRFixPack_ack_notworking` member persists — flagged
docs/agent/bugs/D02.md:108:Found during the fix pack's `C47` attended sitting, where the module was running
docs/agent/bugs/D02.md:129:| **permanently broken** — never recovers | survives | ✅ stays quiet. This is the case the module exists for — the `F30` entombed-building archetype named in its own header |
docs/agent/bugs/D02.md:139:   one.** The fix pack's `C47` records "debounce the notification, not the
docs/agent/bugs/D02.md:142:   exactly the case that complaint is about. Cross-referenced on `C47`.
docs/agent/bugs/D02.md:143:2. ✅ **It also means D02 could not have contaminated the `C47` measurements**,
docs/agent/bugs/D02.md:147:   `SMRFixPack_ack_notworking` **nil on all 38 objects**), *and* recovery would
docs/agent/bugs/D03.md:15:from: "SMR-BugFixPack docs/agent/bugs/D03.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D03.md:18:Filed 2026-07-27 (user decision, out of PT-14/F61's close — read that entry first). The
docs/agent/bugs/D03.md:22:load-bearing for Wildfire/RogueDome, see F61), the trait filter (indirect, trait-based,
docs/agent/bugs/D03.md:25:* **Flag:** `SMRFixPack_closed_to_new_residents` set directly on the Dome object —
docs/agent/bugs/D03.md:48:  ways), own playtest item, opt-in via `SMRFixPack_Optional.ResidencyControl`
docs/agent/bugs/D03.md:70:* Flag `SMRFixPack_closed_to_new_residents` on the Dome object, absent-tolerant (§3).
docs/agent/bugs/D03.md:73:UI row needs eyes-on — it is the pack's first added infopanel row).
docs/agent/bugs/D03.md:87:## ⚖️ 2026-08-10 (owner decision) — the `SMRFixPack_Disabled` console veto does NOT cover this module, and that limit is RECORDED rather than coded
docs/agent/bugs/D03.md:89:Only `IsActive` is consulted here; the veto lever exists for D12/F97-class
docs/agent/bugs/D04.md:15:from: "SMR-BugFixPack docs/agent/bugs/D04.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D04.md:17:### D04 — Multiple Artificial Suns — absorbs F39  `[tested 2026-07-27 (PT-50 PASS in full, archive): Code/Opt_MultipleSuns.lua (opt-in, off by default); night signature matched the banked baseline both sectors, sunless panels 0 at night, reload clean, limit off/on live via the D05 Mod Options toggle; PT-55 PASS 2026-07-30 — see the binding-timing note below]`
docs/agent/bugs/D04.md:29:Filed 2026-07-27 (user decision, out of PT-26/F39's premise finding — read F39 first).
docs/agent/bugs/D04.md:32:F39's second-sun binding fix unreachable dead code in the default pack — but players DO
docs/agent/bugs/D04.md:34:`labels.ArtificialSun[1]` panel-binding bug. This module makes the pack's story honest:
docs/agent/bugs/D04.md:37:**Design — strictly additive, off by default (`SMRFixPack_Optional.MultipleSuns`,
docs/agent/bugs/D04.md:44:* **Binding fix:** the whole of `Fix_SecondArtificialSun.lua` moves in unchanged — the
docs/agent/bugs/D04.md:52:  game-free leg as the F61 deletion so the renumbering happens once.
docs/agent/bugs/D04.md:62:re-fired `DataChanged(false)` re-asserts idempotently — F75 lesson; the handlers gate on
docs/agent/bugs/D04.md:63:the registry status, which covers both the opt-in flag and the `SMRFixPack_Disabled`
docs/agent/bugs/D04.md:64:veto). The F39 wrapper + LoadGame sweep moved in unchanged; `Fix_SecondArtificialSun.lua`
docs/agent/bugs/D05.md:15:from: "SMR-BugFixPack docs/agent/bugs/D05.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D05.md:19:enable route — "type `SMRFixPack_Optional = {...}` in the MAIN MENU console" —
docs/agent/bugs/D05.md:23:inside `SMRFixPack.Register`'s immediate `apply`, at **mod code load during game
docs/agent/bugs/D05.md:27:nicety: the pack targets Steam Workshop AND Paradox Mods, and **Paradox Mods
docs/agent/bugs/D05.md:31:  `Mod.lua:590-604`) put the pack on **Options → Mod Options** (page def
docs/agent/bugs/D05.md:37:  `Mod.lua:473-475` — it is what makes the page list the pack; normally written
docs/agent/bugs/D05.md:44:* **00_Core bridge (D05):** `SMRFixPack.OptionEnabled(id)` = pre-load
docs/agent/bugs/D05.md:45:  `SMRFixPack_Optional[id]` OR the saved toggle — the gate line in all four
docs/agent/bugs/D05.md:46:  Opt_ files. `SMRFixPack.IsActive(id)` — consulted by every optional module's
docs/agent/bugs/D05.md:55:  `on_deactivate`; defs now retained in `SMRFixPack.defs` for reconciliation.
docs/agent/bugs/D05.md:75:repaired same day:** `SMRFixPack.ListFixes()` crashed ("attempt to concatenate
docs/agent/bugs/D05.md:77:2026-07-25 F75/F18 status-relabel repairs clear their entry detail with
docs/agent/bugs/D05.md:79:(Fix_IndependenceTerraforming.lua:88, Fix_LastTransmissionStorage.lua:165),
docs/agent/bugs/D06.md:15:from: "SMR-BugFixPack docs/agent/bugs/D06.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D06.md:18:*(Heading line restored by the popup-audit session 2026-07-30 — the F84 filing
docs/agent/bugs/D06.md:19:commit `21b92cb` had spliced F84's text into this heading, leaving D06's whole
docs/agent/bugs/D06.md:20:entry living under F84. Content untouched.)*
docs/agent/bugs/D06.md:22:> ⚠️ **SAVE-SAFETY SURGERY LANDED ON THIS MODULE 2026-08-01 (chain prompt 5, F86
docs/agent/bugs/D06.md:23:> Tier 2) — it is NOT drone work and changes NO drone behaviour.** F86 Site 2 was
docs/agent/bugs/D06.md:27:> 'SMRFixPack')` on the next load without the pack — **80** on the 2026-08-01
docs/agent/bugs/D06.md:35:> Full record: the F86 entry's Site 2 block. Verification: PT-58.
docs/agent/bugs/D06.md:40:> 2026-07-31). It is re-runnable and owns D06, D08, D09, F77, the drone queue
docs/agent/bugs/D06.md:50:drones are the one part of the pack that has been iterated piece-by-piece, and
docs/agent/bugs/D06.md:216:>   moves the overhaul **out of the Community Fix Pack** into its own mod.
docs/agent/bugs/D06.md:217:> - The Fix Pack's own promise is unaffected: the pack stays save-safe and
docs/agent/bugs/D06.md:220:>   a standalone mod has no configuration matrix to multiply against the pack's
docs/agent/bugs/D06.md:247:> *the only thing that can occupy that window*. Full detail: ENGINE_FACTS + F86.
docs/agent/bugs/D06.md:254:> *by the pack itself*. **A second mod is the one thing that can occupy that
docs/agent/bugs/D06.md:255:> window.** It runs on `OnMsg.LoadGame` — in a world where the pack is already
docs/agent/bugs/D06.md:269:>    would rot as the pack changes.
docs/agent/bugs/D06.md:284:>   pack and **without** us shipping a risky migration inside the pack itself.
docs/agent/bugs/D06.md:285:>   That is a materially different posture from "we would have to patch the pack
docs/agent/bugs/D06.md:414:> (recorded on the fix pack's checklist, item 87, and in `STATE.md`). Drone
docs/agent/bugs/D06.md:424:replaced by **ONE multi-step playtest**, not a family of them. **PT-10 (F55) is
docs/agent/bugs/D06.md:425:NOT frozen** — different subject, shipped default-on fix. F77's defect is real
docs/agent/bugs/D06.md:435:COLLISION between the `Inventor` profile and D06/D09/F77; the interaction is
docs/agent/bugs/D06.md:447:  `colony:SetLabelModifier`: `SMRFixPack_DroneSpeedDial` on label **`Drone`**
docs/agent/bugs/D06.md:448:  prop `move_speed`, and `SMRFixPack_DroneCarryDial` on label **`Consts`** prop
docs/agent/bugs/D06.md:455:- **D06 and F77 reference no power, maintenance or `disable_*` property at all**
docs/agent/bugs/D06.md:465:   working-flag flapping, so **F77's trigger should be rare or absent there** —
docs/agent/bugs/D06.md:466:   a quiet F77 half on an Inventor save is not evidence the fix does nothing.
docs/agent/bugs/D06.md:467:   *(Inference from the effect data; not observed. Run the F77 half on a
docs/agent/bugs/D06.md:674:in `Idle` at save time serialised it — **F86 Site 2, 98 errors per session, and it
docs/agent/bugs/D06.md:693:3. **Telemetry** — `SMRFixPack.DroneReport()` (always available, module on or off):
docs/agent/bugs/D06.md:701:iteration knobs. Shipped alongside: **F77**'s `Fix_ExtenderFlapChurn` (default-on
docs/agent/bugs/D07.md:15:from: "SMR-BugFixPack docs/agent/bugs/D07.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D07.md:34:- **Bonus finding — live corroboration of F79.** Children in the cohort dome
docs/agent/bugs/D07.md:36:  the mechanism F79 describes: `Dome:GetService` is passage-only, so
docs/agent/bugs/D07.md:72:**→ save with it ON and reload with the pack disabled in the MOD MANAGER**).
docs/agent/bugs/D07.md:73:⚠️ **METHOD CORRECTED 2026-08-01 — a toggle CANNOT answer an uninstall question.** With the module merely switched off the mod env is still present and the hooks are still installed, so any captured frame resolves `SMRFixPack`, reads inactive and no-ops: **it reads clean by construction, whether or not the module leaks.** `Opt_DroneOverhaul` leaked at 98 errors/session with its own toggle OFF — that is how F86 Site 2 was found. Use **Mod-Manager-disable** (measured equivalent to a real uninstall, PT-20: 98 vs 98 on the same save). `ENGINE_FACTS.md`, "OFF" IS THREE DIFFERENT THINGS.
docs/agent/bugs/D07.md:118:  cover it (work commutes are unaffected by F79; only service-seeking
docs/agent/bugs/D07.md:122:composition), F79/F80 (train findings from the same sitting), the
docs/agent/bugs/D07.md:214:## ⚖️ 2026-08-10 (owner decision) — the `SMRFixPack_Disabled` console veto does NOT cover this module, and that limit is RECORDED rather than coded
docs/agent/bugs/D07.md:216:Only `IsActive` is consulted here; the veto lever exists for D12/F97-class
docs/agent/bugs/D09.md:15:from: "SMR-BugFixPack docs/agent/bugs/D09.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D09.md:35:(`Mods["SMR_CommunityFixPack"].options.DroneSpeedDial`) instead of the values
docs/agent/bugs/D09.md:40:`applied`, zero `[CommunityFixPack]` error/inactive/disabled lines, and the only
docs/agent/bugs/D09.md:43:thread on load was DEAD — restarting with the fixed body` lines are F02's
docs/agent/bugs/D09.md:74:   **zero** `[CommunityFixPack]` error/inactive lines — a probe defect, never a
docs/agent/bugs/D09.md:105:  `SMRFixPack_DroneSpeedDial` / `SMRFixPack_DroneCarryDial`. Choice values
docs/agent/bugs/D09.md:126:  **1/61/15/0** (dial probe FAILs "fix pack not loaded" by design) · default
docs/agent/bugs/D09.md:134:  `Modifier.new` at file scope — the F64 pre-flattening trap (`new` is
docs/agent/bugs/D09.md:141:  first leg run after the F28 removal and after the probe repair, and it clears
docs/agent/bugs/D09.md:145:  `73/73` rather than a default-config `67/73`. Zero `[CommunityFixPack]`
docs/agent/bugs/D12.md:10:row_status: "**speced — no status beyond `speced` is claimed until PT-62 completes. BUILT 2026-08-02 (chain prompt 10) as `Opt_NoHomeless`; PT-62 PARTLY RUN (core seam + suite + exemption established; P4/P6/P12/P13 owed); ⭐ ADJUDICATED 2026-08-03 (chain-12 QA, job 9): the build STANDS — all five live-review decisions upheld, the veto's D07-independence verified from code.** ⚠️ **CODE CHANGED AGAIN 2026-08-03 AFTER that adjudication (owner-approved): the FREE-WORK DOOR.** The symmetric veto built on 2026-08-02 refused `need_work` — which is exactly the set vanilla moves toward an open job (`better_work`, `Colonist.lua:2679`), so a flagged dome could never be STAFFED from outside and its services would go dark unreplaced. Derived from Src, never observed. A flagged dome now neither pushes out nor refuses anyone while it holds a free workplace they could take, applied on BOTH sides because an entry-only door re-creates the PT-62 loop in miniature; `count_movable` and the rollover carry it, and the stale narrow-reading registry title was corrected in the same pass. **The re-run gains P14** (does an open slot in a flagged dome FILL) — the one unmeasured assumption in the build, and `movable 0` on a recruiting dome is the door WORKING, not a miss Premise RE-DERIVED first: the tie is byte-verbatim in pinned Src and the [S36] \"1.0 fixed homelessness\" claim is FALSE for this half. The open question is DECIDED — ⚠️ row re-synced 2026-08-03 (it had frozen the superseded first design; caught by doccheck's first baseline run): the rule is vanilla's **`need_work` predicate, NEITHER specced option** (\"narrow\" was built first and falsified live the same evening — entry §4); `C40`, filed en route, supplied the third reason (entry)"
docs/agent/bugs/D12.md:15:from: "SMR-BugFixPack docs/agent/bugs/D12.md @ 0efb87e, moved 2026-08-12"
docs/agent/bugs/D12.md:53:colony-wide. Filed as **`C40`** with the five-link route.
docs/agent/bugs/D12.md:57:* It does **NOT** overturn the premise. C40 is a second, independent **producer**
docs/agent/bugs/D12.md:118:⚠️ **What it costs versus narrow:** narrow was immune to the C40 capacity churn.
docs/agent/bugs/D12.md:186:   still owed must not read that as "the pack is not ready" — the pack is not
docs/agent/bugs/D12.md:415:out, which is why the pack never produced this. ⚠️ **Lesson for the instrument,
docs/agent/bugs/D12.md:493:| `SMRFixPack_closed_to_new_residents` (D03, existing) | **off** | children can still migrate in |
docs/agent/bugs/D12.md:494:| `SMRFixPack_no_homeless` (D12, new) | **on** | graduates are pushed out before they pile up |
docs/agent/bugs/D12.md:507:  put outside with no dome dies (F53 territory) — this is the one failure mode
docs/agent/bugs/D12.md:528:* Savegame footprint per FIX_POLICY §3: `SMRFixPack_no_homeless` on the
docs/agent/bugs/D12.md:530:  it and a save carrying it loads fine with the module or the pack removed.
docs/agent/bugs/D12.md:551:it ON, reload with the pack disabled in the MOD MANAGER, clean load.**
docs/agent/bugs/D12.md:552:⚠️ **METHOD CORRECTED 2026-08-01 — a toggle CANNOT answer an uninstall question.** With the module merely switched off the mod env is still present and the hooks are still installed, so any captured frame resolves `SMRFixPack`, reads inactive and no-ops: **it reads clean by construction, whether or not the module leaks.** `Opt_DroneOverhaul` leaked at 98 errors/session with its own toggle OFF — that is how F86 Site 2 was found. Use **Mod-Manager-disable** (measured equivalent to a real uninstall, PT-20: 98 vs 98 on the same save). `ENGINE_FACTS.md`, "OFF" IS THREE DIFFERENT THINGS.
docs/agent/bugs/D12.md:575:   `SMRFixPack_Disabled.NoHomeless` lever) need it.
docs/agent/bugs/D12.md:581:   `*r local bad = 0 for _, city in ipairs(Cities) do for _, c in ipairs(city.labels.Colonist or empty_table) do local d = c.emigration_dome if d and d.SMRFixPack_no_homeless then bad = bad + 1 end end end ConsolePrint(print_format("heading INTO a flagged dome", bad))`
docs/agent/bugs/D12.md:633:[CommunityFixPack] NoHomeless: self-check targets Community but Workforce declares
docs/agent/bugs/D12.md:635:[CommunityFixPack] NoHomeless: inactive (Community.HasFreeWorkplacesAround not found
docs/agent/bugs/D12.md:639:[CommunityFixPack] NoHomeless: applied
docs/agent/bugs/D12.md:642:**This is the F64 lesson repeating** — the same mistake `Fix_BombardmentSpread`'s
docs/agent/bugs/INDEX.md:7:entries moved here from SMR-BugFixPack (split-optins, 2026-08-12); each entry's front
docs/agent/facts/EF-001.md:20:    finds nil and silently deactivates the fix. F64 shipped broken this way
docs/agent/facts/EF-001.md:27:    `Fix_LanderCargoRatchet.lua(124)` (the pack's pre-build replacement, baked
docs/agent/facts/EF-002.md:10:  (established 2026-08-01 from the F86 Site 2 mechanism + PT-58; the project had
docs/agent/facts/EF-002.md:11:  been using "off" loosely and it matters to F86 and to D13). Ranked by what they
docs/agent/facts/EF-002.md:16:  | **Mod Options toggle** (optional modules) | **YES** — wrappers stay installed and pass through at call time (`SMRFixPack.IsActive`, `00_Core.lua:39-42`) | yes | **YES** | no |
docs/agent/facts/EF-002.md:17:  | **`SMRFixPack_Disabled[id]`** user veto | **depends on where the module installs** — `Register` returns before `run_apply` (`00_Core.lua:384-388`), so an apply()-time installer never hooks; a **FILE-SCOPE** installer (e.g. `Opt_DroneOverhaul` parts 1-2) has already hooked before `Register` is reached, and the veto only flips its status | yes | apply()-installers: no · file-scope installers: **YES** | no |
docs/agent/facts/EF-002.md:22:  the pack **off** in the Mod Manager does **not** reset its Mod Options; turning
docs/agent/facts/EF-002.md:34:  ⭐ Silver lining worth knowing: an all-toggles-ON run is the leg F87's residual
docs/agent/facts/EF-002.md:38:  is the whole of F86.** With any toggle off the environment still exists, so a
docs/agent/facts/EF-002.md:39:  captured frame resumes, resolves `SMRFixPack`, reads inactive and no-ops
docs/agent/facts/EF-002.md:48:  player had the pack toggled off. The only state that keeps frames out of a save
docs/agent/facts/EF-002.md:57:  (read off `SMRFixPack.IsActive`, `00_Core.lua:39-42`); and that the
docs/agent/facts/EF-002.md:58:  `SMRFixPack_Disabled` veto blocks capture for apply()-time installers but not
docs/agent/facts/EF-004.md:13:  mod's options (the TestKit driving the fix pack's dials) must go through
docs/agent/facts/EF-005.md:11:  as crashes. `/` truncates (integer division); that is what makes F12's
docs/agent/facts/EF-006.md:14:  the pack's `rawget(_G, "X")` pattern works; `_G` maps to the env, but NEW
docs/agent/facts/EF-006.md:16:  `SMRFixPack`/`SMRTest` are cross-mod and console visible; `Msg`/`OnMsg` are
docs/agent/facts/EF-006.md:17:  filtered only for persist/debug messages. The fix pack Code/ uses no
docs/agent/facts/EF-007.md:19:  engine's "Mod Flagged" warning; the game and the fix pack were unaffected.
docs/agent/facts/EF-008.md:19:  This project's only measurement of an assert reaching a log is `C43`, taken on
docs/agent/facts/EF-010.md:12:  numbers are exactly this, by design. `GetStaticMsgNames()` (F06 probe) is a
docs/agent/facts/EF-012.md:11:  pre-wrapped (F73).
docs/agent/facts/EF-013.md:4:summary: "Mod registry: every fix goes through `SMRFixPack.Register(id, {title"
docs/agent/facts/EF-013.md:9:- Mod registry: every fix goes through `SMRFixPack.Register(id, {title, apply})`
docs/agent/facts/EF-013.md:11:  deactivate gracefully; `SMRFixPack_Disabled` = user veto; `SMRFixPack.ListFixes()`
docs/agent/facts/EF-014.md:29:  genuine engine C export. F12's fix checks for it at apply time.
docs/agent/facts/EF-017.md:14:  `rawget(_G, ...)` in apply() to confirm the write landed — F22 does.
docs/agent/facts/EF-019.md:10:  audit 2026-07-30; the F83 investigation briefly assumed the opposite and
docs/agent/facts/EF-019.md:23:  thread and LOST in an RT thread (the F83 family); "no MakeThreadPersistable"
docs/agent/facts/EF-020.md:29:  reason to own one. (Worked example of the trap: chain prompt 7 declined C23
docs/agent/facts/EF-021.md:16:  closures included — observed, F83) and GT waiters persist (above); an open
docs/agent/facts/EF-021.md:19:  `CanSaveGame` has no popup clause; see F85 for the rebind edge).
docs/agent/facts/EF-022.md:24:    any reference to `SMRFixPack.*` inside it would index nil after uninstall.
docs/agent/facts/EF-022.md:35:    `Fix_MeteorFrequency` was caught red-handed (F86).
docs/agent/facts/EF-023.md:20:    two — `Fix_MeteorFrequency` and `Fix_RainsDeadlock` (fixed in Tier 1),
docs/agent/facts/EF-023.md:21:    `Fix_MeteorStormWedge` and `Fix_ExtenderFlapChurn` (fixed 2026-08-13), plus
docs/agent/facts/EF-023.md:22:    an inline site in `Fix_CrystalMysteryHang`. The belief itself is false, as
docs/agent/facts/EF-023.md:34:    ONLY the names its own mod creates** (`SMRFixPack` is nil after uninstall
docs/agent/facts/EF-023.md:38:    bounded if it self-limits (`Fix_CrystalMysteryHang`'s frozen 10-sol
docs/agent/facts/EF-023.md:39:    deadline), forever if it loops (`Fix_RainsDeadlock`'s `fixed_loop` is
docs/agent/facts/EF-023.md:49:    ⚠️ **CORRECTED 2026-07-31 (F86 adjudication): that clause is not the whole
docs/agent/facts/EF-023.md:57:    `Fix_CaveInsNoDisasters`' wrapper sits in the `info` local the engine's
docs/agent/facts/EF-023.md:66:    (F86 adjudication + owner, 2026-07-31): do not measure this and do not
docs/agent/facts/EF-023.md:74:    corrections~~): **`agent/bugs/F86.md`**. ⛔ **COUNT SUPERSEDED 2026-08-13 by
docs/agent/facts/EF-023.md:77:    "13" was an open lower bound over capturable code in the fix pack only; the
docs/agent/facts/EF-023.md:82:    belief (`Fix_MeteorFrequency`, `Fix_RainsDeadlock`) were rewritten with their
docs/agent/facts/EF-023.md:90:    rewrote and of nothing else: `Fix_MeteorStormWedge:138-141` and
docs/agent/facts/EF-023.md:91:    `Fix_ExtenderFlapChurn`'s whole "Savegame note" still stated the disproven
docs/agent/facts/EF-023.md:92:    model, and `Fix_CrystalMysteryHang` carried the F06 sentence inline. All
docs/agent/facts/EF-024.md:28:    (2026-08-01, F86 Phase 0 §0.2 — `autosave=true err=false` observed twice).
docs/agent/facts/EF-025.md:10:  AND IT IS THE ONE EVERY PLAYER GETS FIRST** (measured 2026-07-31, F87; source
docs/agent/facts/EF-025.md:22:    for that entire session** — three of ours were (F87 sweep).
docs/agent/facts/EF-025.md:35:    made `HasTrait:new` throw in `Fix_DustSicknessBiorobots` (F87).
docs/agent/facts/EF-027.md:17:  these functions, however, will use their new versions."* So F86's mechanism
docs/agent/facts/EF-028.md:4:summary: "THE SAVE/LOAD HOOK SURFACE — enumerated 2026-07-31 (F86 round 2), so no design discovers hooks one at a time again."
docs/agent/facts/EF-028.md:9:- **THE SAVE/LOAD HOOK SURFACE — enumerated 2026-07-31 (F86 round 2), so no
docs/agent/facts/EF-028.md:19:    can't-save bug, invisible on console, worse than F86) →
docs/agent/facts/EF-029.md:10:  statement continues** (MEASURED 2026-08-01, F86 Phase 0 §0.1, owner at the
docs/agent/facts/EF-029.md:37:    the first iteration. The F02 wrapper's defer-when-`rawget(_G,"Meteors")`-falsy
docs/agent/facts/EF-030.md:10:  the autosave path with `autosave=true`** (MEASURED 2026-08-01, F86 Phase 0
docs/agent/facts/EF-034.md:26:  C18 on 2026-08-02** — that held only for `Building:AddToCityLabels` read
docs/agent/facts/EF-036.md:16:  Proven 2026-08-02 while grading C30: `OrbitalProbe:Done` clears its label
docs/agent/facts/EF-038.md:18:  a wrong figure on 2026-08-02: an F82 estimate assumed 20×, computed 3.3 sols
docs/agent/facts/EF-039.md:12:  the fact that makes `Fix_TechDescriptionBuilding` a shipped no-op (**BUGS F98**)
docs/agent/facts/EF-039.md:56:    discarded, this entry is right, and `F98` is a shipped no-op as stated.
docs/agent/facts/EF-039.md:63:    reading `C51` would need (see `EF-063` for the 30-second way to check
docs/agent/facts/EF-039.md:69:    * **Route 1 read forwards — a REPOINTED id.** `C51` pointed a control at an
docs/agent/facts/EF-039.md:77:    * **Route 1 as a BORROWED id in a `T{tag, context}`.** `C50`'s bullet — a
docs/agent/facts/EF-039.md:82:      the pack, with the number still resolving.
docs/agent/facts/EF-039.md:84:    directions**: it destroys a replacement literal (the `F98` no-op, measured
docs/agent/facts/EF-039.md:87:    *for reusing text*, which is exactly what `C50`/`C51` were built on.
docs/agent/facts/EF-040.md:30:  * ⚠️ **Why it was worth 4000 draws to settle:** F97's headline claim is that a
docs/agent/facts/EF-041.md:11:  Recorded 2026-08-02 by the F76 design pass, which was sent to confirm the
docs/agent/facts/EF-042.md:10:  PC it equals the whole screen.** MEASURED 2026-08-02 (F76 sitting, M1):
docs/agent/facts/EF-044.md:18:  retail (F98's whole mechanism, `agent/bugs/F98.md`). ⚠️ Corollary: a
docs/agent/facts/EF-046.md:32:  right-edge rather than corner. Live example and disposition: `agent/bugs/C41.md`.
docs/agent/facts/EF-046.md:36:  exactly on the cursor — that is what F76's M1/M2 measured, and it is why
docs/agent/facts/EF-046.md:37:  F76's "coordinate-space mismatch" mechanism was correctly refuted. The
docs/agent/facts/EF-048.md:18:  | `GetSpentTimeAverageInHours` (2026-08-05, F21) | **a `T()` object** |
docs/agent/facts/EF-048.md:22:  false negative forever and cannot print anything else — the F21
docs/agent/facts/EF-051.md:48:  re-enable the pack; all three were on disk again by **01:57:47**, creation
docs/agent/facts/EF-054.md:35:  not assume it loads after (or before) another. Both the Community Fix Pack and the
docs/agent/facts/EF-054.md:45:  * **A player's rig, 6 mods** (the F104 reporter's log
docs/agent/facts/EF-054.md:47:    `SMR_CommunityFixPack, dwAWmXz, iooW34Y, QfCw4mN, DLav7z7` — **the fix pack
docs/agent/facts/EF-054.md:50:    (`Mars.exe-20260823-22.05.52`): the fix pack first again.
docs/agent/facts/EF-054.md:58:  ⚠️ **The first real ordering CONFLICT also arrived and was NOT ours:** F104's
docs/agent/facts/EF-054.md:61:  clause was not needed. See `F104`.
docs/agent/facts/EF-054.md:93:  the pack loads third. ⚖️ **OWNER RULING 2026-08-16: *"lets note this and see if
docs/agent/facts/EF-055.md:101:  * **Result, twice:** the def loads (`Loaded mod def Relaunched Fix Pack:
docs/agent/facts/EF-055.md:120:    pulls the **fix pack's** junction to install the packed build. On this
docs/agent/facts/EF-055.md:129:  appdata` with all 75 modules applied and no re-tick anywhere
docs/agent/facts/EF-055.md:130:  (`SWEEP_FINDINGS.md` LR-F19). ⇒ the loss clause binds **when a launch runs
docs/agent/facts/EF-055.md:148:  DECLARED DEPENDENCIES, and neither the fix pack, the opt-in mod nor the Test
docs/agent/facts/EF-057.md:4:summary: "⛔⛔ A SAMPLED EXTREMUM IS NOT AN EXTREMUM — a polled series bounds NOTHING between its samples, so 'the value never reached X' may only be claimed from an event or reason that FIRES at X, never from the min/max of the samples. MEASURED on C47 (2026-08-15): three unattended runs polled two farm buffers every 500 real ms, read minima 305–605 of 5000, and recorded 'the buffer never reached 0' as a FAILED prediction — but every one of the same runs' 2/0/4 notification adds carried `reason=Consumption`, and `GetWorkNotPossibleReason` returns that reason ONLY when `CanConsume()` is false, i.e. stored == 0 (`Building.lua:611-613`, `HasConsumption.lua:366-368`) ⇒ the buffer hit a true zero between samples on every add and the verdict was BACKWARDS. The attended sitting then sampled real zeros directly (2 of 121 at 2 s). The reversal was the owner's, not the agent's. Rule: pair every polled extremum with an event/reason witness coded to the boundary, and write 'the SAMPLED minimum was N', never 'the minimum was N'"
docs/agent/facts/EF-057.md:9:- **The defect this generalises, and it reversed a headline verdict.** The C47
docs/agent/facts/EF-057.md:37:- ⚠️ Same family as the recorded-facts-are-claims-too rule and the C47 leg's own
docs/agent/facts/EF-058.md:4:summary: "⛔⛔ THE FLATTENED-CLASS TRAP BITES METHOD WRAPPERS TOO — patching a base class's method intercepts NOTHING when DefineClass has flattened the function into subclass tables (`classes.lua:988`); a wrapper must be installed on EVERY class whose lookup resolves to the shipped function, and the wiring must be PROVEN off live instances before any number is trusted. ⚖️ AMENDED 2026-08-19 (link 8): THE TRAP IS KEYED ON INSTALL TIME RELATIVE TO `Msg(\"Autorun\")`, and all four bites were RUNTIME-installed instruments (probe/console), never mod-load-time patches — mod code executes at `autorun.lua:423`'s direct `ModsLoadCode()` call, strictly BEFORE `classes.lua`'s `function OnMsg.Autorun()` flattens, so a patch installed at file scope or inside a `Register` apply is COPIED DOWN into the subclasses and is safe by construction; the fix pack's 50 method patches are all on that side (75/75 `Register` calls at column 0). ⛔ This narrows nothing for an install made after flattening, which is every instrument this project has ever written. MEASURED 2026-08-16 (c48-pairing launch 1): a log wrapper on `TaskRequestHub.FindTask` alone saw **0 of 25,184** calls across a 10-game-hour window because `DroneHub.FindTask` etc. are flattened copies; the repair patched **48** carrier classes (scan g_Classes for `cls.FindTask == shipped_fn`, remember own-key-vs-inherited per class for an exact restore) and printed a wiring proof — 19/19 live hubs resolving to the wrapper — before the window opened. Fourth bite of the classes.lua:988 family (wave-11 probe rawget, sampler class read, EF-057's note); the value-field converse: writing a CLASS field (the c48-brake `supply_dist_modifier`) works when written to the exact class instances belong to"
docs/agent/facts/EF-058.md:20:  ⇒ A patch installed at a mod file's scope, or inside a `SMRFixPack.Register`
docs/agent/facts/EF-059.md:4:summary: "⭐⭐⭐ THE DRONE MATCHMAKER TREATS `rfStorageDepot`-FLAGGED SUPPLIES AS A STRICT LAST RESORT — any non-depot source (vegetation offer, loose pile, producer output) wins the pairing REGARDLESS of distance; distance only tie-breaks within a class. MEASURED 2026-08-16 at the FindTask seam, 985 witnessed pairings (`archive/c48pair2_*`): Seeds chose non-depot 479/479 with a NEARER fully-stocked ASSIGNABLE depot losing in 399 (specimen: 41,915 flown for one bush's 280 past a depot offering 180,000 at 5,733); Food obeyed the same law wherever loose food existed (81% nearer-depot losses) and used depots for the remainder (46%) only because loose food is finite. Alternatives eliminated by experiment: distance (the 150 brake, applied 100%, changed nothing), demand-side gating (a new diner bulk-filled to exactly 100% incl. a sub-load top-up ⇒ consumption's `rfWaitToFill` is a one-resource-unit rounding guard, not a carry gate), queue-bucket order (veg sits p1, depots mostly p0 with some p2/p3 — the HIGHER-bucket depots also lost). Both depot requests are branded (`StorageDepot.lua:67-68,466-467`). Corollaries, all measured: `desired_amount` withholds NOTHING from the supply side (every depot offered stored-in-full; it steers depot-to-depot rebalancing — the owner's reading, confirmed); depots RESTOCK THEMSELVES from the landscape through the same rule (125/479 pairings delivered INTO depots — a colony banks bush seeds it will never serve from storage); grown crop hexes offer FOOD via the same VegetationTaskRequesters; mega-dome food venues drain at farm rates (a Diner ~48,000/sol) and thrive on bulk. ⇒ on terraformed maps 'depots last' degenerates into 'depots never' for Seeds — the C47/C48 crumb-feeding, characterized"
docs/agent/facts/EF-061.md:64:  the 2026-08-31 re-sync; `EF-061` since — ids are allocated in the fix pack and
docs/agent/facts/EF-062.md:79:  the 2026-08-31 re-sync; `EF-062` since — ids are allocated in the fix pack and
docs/agent/facts/EF-063.md:38:  prove it is not systemic.** Worked example (`C51`): the Universal Rocket's
docs/agent/facts/EF-063.md:47:    carries every language, so the fix adds no English anywhere (`C51`).
docs/agent/facts/EF-063.md:50:    who is not playing in English (`C50`). `EF-039` route 3,
docs/agent/facts/EF-064.md:4:summary: "⛔ `ProtectedPropertyObject` DOES NOT PROTECT ANYTHING IN RETAIL — `__newindex` asserts on an undeclared key and then `rawset`s it on the very next line (`CommonLua/PropertyObject.lua:1819-1823`), and by `EF-008` an assert does not unwind. So a write to a key the class never declared SUCCEEDS and execution continues to the next statement. The same shape applies to `__index` (`:1813-1817`), which asserts and then returns the class value anyway. ⇒ never explain a downstream failure as 'the protected-object assert halted it', and never read a missing class-field declaration as a behavioural cause; it is a diagnostic aid for developer builds only. This refuted another mod's stated mechanism for the Mod Manager screenshot bug (`C52`) while every line it cited was correct"
docs/agent/facts/EF-064.md:41:  The failure was in the "therefore". See `C52`, where the real cause turned out
docs/agent/facts/EF-065.md:4:summary: "⛔⛔ THE ENGINE ITSELF SHOWS THE PLAYER A MESSAGE BOX NAMING OUR MOD — but only on ONE of its two routes, and neither has a call site in our code. (a) any UNCAUGHT Lua error whose message OR call stack contains our `content_path` reaches `ReportModLuaError` (`Mod.lua:2958-2993`, live in retail because the block is gated `if not Platform.asserts`), which `ModPrint`s `Error in mod <title> (id …)` and pops `CreateMessageBox(\"Warning\", \"Mod-related problem detected in the game logic. Try disabling the mods…\") + \"Mod Flagged: <title>\"` — once per mod id per process; (b) any throw at a code file's FILE SCOPE is caught by `pdofile`'s pcall (`lib.lua:242-251`), collected by `ModDef:LoadCode` (`:490-520`) — ⛔ CORRECTED 2026-08-19 (terminal audit): the (b) BOX IS DEAD CODE ON THIS TITLE — display is gated on `ModsPreGameMenuOpen` (init false, set nowhere) or `Msg(\"PreGameMenuOpen\")`, which SM's `Lua/init.lua:1` override never raises (same mechanism as EF-055) ⇒ a file-scope throw is LOG-ONLY and the player sees NOTHING. `content_path` is configuration-INVARIANT (`Mod/SMR_CommunityFixPack/` packed and unpacked, `Mod.lua:1755-1758`), so (a) behaves identically in run B. MEASURED NEGATIVE 2026-08-19 is SPENT: surface (a) FIRED IN THE FIELD TWICE ON 2026-08-23/24 (F104 Passage Network, F105 vanilla landscape site) — both pass-through frames, NEITHER our defect; the box wording is now observed and OnLuaError IS confirmed raised for a thread error. The causing mod can be unnameable: PN had already returned one line before the throw. Response options: checklist 73"
docs/agent/facts/EF-065.md:11:  enumerated 17 screen call sites in `Code/` and concluded the pack "mints no
docs/agent/facts/EF-065.md:54:  from `SMRFixPack.fixes`/`order` only when the throw precedes its `Register`
docs/agent/facts/EF-065.md:63:  `Mod/SMR_CommunityFixPack/` in run B exactly as unpacked — re-derived by the
docs/agent/facts/EF-065.md:80:  * **F104** — Passage Network's `CreateDomeNetworks` returns nothing, vanilla
docs/agent/facts/EF-065.md:82:    `Fix_ShuttleTransportCache.lua(86)`. ⭐ Reproduced on the owner's rig,
docs/agent/facts/EF-065.md:88:  * **F105** — a vanilla `LandscapeConstructionSite` defect; our frame is
docs/agent/facts/EF-065.md:89:    `Fix_MilestoneCrash.lua(73)`. Reporter's log
docs/agent/facts/EF-065.md:94:    `Mod Flagged:` and `Relaunched Fix Pack`, single `OK`. Position and whether it
docs/agent/facts/EF-065.md:97:    This fact previously recorded that as *not derivable from Lua*. F104's throw
docs/agent/facts/EF-066.md:4:summary: "⭐⭐ A BUILT CLASS'S `Init` IS NEVER THE FUNCTION ANYONE ASSIGNED — `Init`/`Done` are COMBINED methods: `OnMsg.ClassesPreprocess` collects every classdef's own `Init` along each hierarchy and writes back a NEW composed closure per class (`classes.lua:1602-1676`), so a classdef-time wrapper on a PARENT is captured into every descendant's composition (why C51's one wrap reached the Zeus rocket, measured on a German screen) AND an identity check on a built class's `Init` reads \"neither ours nor the original\" on EVERY boot with ZERO other mods — the wave-12 probe's \"a later mod has chained on top of ours\" names a cause that cannot be the cause, and a wrapper genuinely lost pre-build would produce the SAME reassuring reading. Identity checks stay valid on plain methods and `_G` functions (copied by reference, never recomposed; wave-13 compared clean). ⭐ SWEPT AT LAST, MEASURED 2026-08-24 (`archive/f106_*.log`, probe `DispatchReach`): the pack declares **105** (class, method) targets — not ~60 — and 97 of them reach every descendant; the 66 (+1,328 multi-parent) unreached classes are shipped SUBCLASSES THAT RE-DECLARE the method, this watch's original question, failure mode under-coverage and never new harm. ⛔ Instantiation is NOT measured, so that is a reach gap and never a broken-fix count. ⛔ The 2026-08-24 \"post-ClassesBuilt copy misses everything\" sharpening is WITHDRAWN — `Register` applies inline at file-load time, so plain-method wraps patch CLASSDEFS and the builder copies ours down (F106 closed as refuted, F33 clean). ⚠️ The mirror-image defect that timing DOES cause is real and filed: capturing `prev` off a class that does not declare the method yields nil (`F107`)"
docs/agent/facts/EF-066.md:20:    4 sitting: `C51` wrapped ONLY `customUniversalRocket` (`link4de_*`: "wrapped
docs/agent/facts/EF-066.md:23:    `Fix_LocalizedUIText.lua` repaired nothing; this mechanism is why.
docs/agent/facts/EF-066.md:45:    keeps its own function and the parent wrap never runs there. `C51`'s rocket
docs/agent/facts/EF-066.md:52:    MEASUREMENT THE SAME DAY** (`F106`, closed; log
docs/agent/facts/EF-066.md:56:    overriding or not, and named `Fix_SmallLandscapeSites` (F33) a suspect
docs/agent/facts/EF-066.md:57:    no-op. **The premise "post-ClassesBuilt" is false.** `SMRFixPack.Register`
docs/agent/facts/EF-066.md:65:    builder's member copy, not `ClassesPreprocess`'s composition). F33 measured
docs/agent/facts/EF-066.md:69:    `SMRFixPack.DataPatch` waits for `ClassesBuilt` (`00_Core.lua:334`).
docs/agent/facts/EF-066.md:72:    every `{class, method}` target the pack declares:
docs/agent/facts/EF-066.md:80:    declares both interaction methods `Fix_RocketInteractGuard` wraps on
docs/agent/facts/EF-066.md:82:    both `GetWorkNot*Reason` that `Fix_ShuttleHubOffAvailable` wraps on
docs/agent/facts/EF-066.md:88:  * ⚠️ **THE REAL DEFECT THE SWEEP FOUND IS THE MIRROR IMAGE — `F107`.** Because
docs/agent/facts/EF-066.md:89:    the pack wraps classdefs, a module that captures `local prev = C.Method` on a
docs/agent/facts/EF-066.md:91:    holds only its own members and has no metatable). `Fix_LandscapeCostRefresh`
docs/agent/facts/EF-066.md:93:    `F107`. Static audit: the pack's only instance. ⇒ **the authoring rule this
docs/agent/facts/EF-068.md:34:    had run, and filed "Steam has neither F105 nor F108" as an owner decision.
docs/agent/facts/EF-068.md:48:    present: `Fix_LandscapeCostRefresh.lua` (F105) and
docs/agent/facts/EF-068.md:49:    `Fix_ExtractorStaffedPerformance.lua` (F108). Its packed `metadata.lua` reads
docs/agent/facts/INDEX.md:28:| EF-013 | Mod registry: every fix goes through `SMRFixPack.Register(id, {title | — | 2026-07-29 | 4 | [EF-013.md](EF-013.md) |
docs/agent/facts/INDEX.md:43:| EF-028 | THE SAVE/LOAD HOOK SURFACE — enumerated 2026-07-31 (F86 round 2), so no design discovers hooks one at a time again. | 2026-07-31 | 2026-07-31 | 26 | [EF-028.md](EF-028.md) |
docs/agent/facts/INDEX.md:72:| EF-057 | ⛔⛔ A SAMPLED EXTREMUM IS NOT AN EXTREMUM — a polled series bounds NOTHING between its samples, so 'the value never reached X' may only be claimed from an event or reason that FIRES at X, never from the min/max of the samples. MEASURED on C47 (2026-08-15): three unattended runs polled two farm buffers every 500 real ms, read minima 305–605 of 5000, and recorded 'the buffer never reached 0' as a FAILED prediction — but every one of the same runs' 2/0/4 notification adds carried `reason=Consumption`, and `GetWorkNotPossibleReason` returns that reason ONLY when `CanConsume()` is false, i.e. stored == 0 (`Building.lua:611-613`, `HasConsumption.lua:366-368`) ⇒ the buffer hit a true zero between samples on every add and the verdict was BACKWARDS. The attended sitting then sampled real zeros directly (2 of 121 at 2 s). The reversal was the owner's, not the agent's. Rule: pair every polled extremum with an event/reason witness coded to the boundary, and write 'the SAMPLED minimum was N', never 'the minimum was N' | 2026-08-15 | 2026-08-15 | 31 | [EF-057.md](EF-057.md) |
docs/agent/facts/INDEX.md:73:| EF-058 | ⛔⛔ THE FLATTENED-CLASS TRAP BITES METHOD WRAPPERS TOO — patching a base class's method intercepts NOTHING when DefineClass has flattened the function into subclass tables (`classes.lua:988`); a wrapper must be installed on EVERY class whose lookup resolves to the shipped function, and the wiring must be PROVEN off live instances before any number is trusted. ⚖️ AMENDED 2026-08-19 (link 8): THE TRAP IS KEYED ON INSTALL TIME RELATIVE TO `Msg("Autorun")`, and all four bites were RUNTIME-installed instruments (probe/console), never mod-load-time patches — mod code executes at `autorun.lua:423`'s direct `ModsLoadCode()` call, strictly BEFORE `classes.lua`'s `function OnMsg.Autorun()` flattens, so a patch installed at file scope or inside a `Register` apply is COPIED DOWN into the subclasses and is safe by construction; the fix pack's 50 method patches are all on that side (75/75 `Register` calls at column 0). ⛔ This narrows nothing for an install made after flattening, which is every instrument this project has ever written. MEASURED 2026-08-16 (c48-pairing launch 1): a log wrapper on `TaskRequestHub.FindTask` alone saw **0 of 25,184** calls across a 10-game-hour window because `DroneHub.FindTask` etc. are flattened copies; the repair patched **48** carrier classes (scan g_Classes for `cls.FindTask == shipped_fn`, remember own-key-vs-inherited per class for an exact restore) and printed a wiring proof — 19/19 live hubs resolving to the wrapper — before the window opened. Fourth bite of the classes.lua:988 family (wave-11 probe rawget, sampler class read, EF-057's note); the value-field converse: writing a CLASS field (the c48-brake `supply_dist_modifier`) works when written to the exact class instances belong to | 2026-08-19 | 2026-08-19 | 49 | [EF-058.md](EF-058.md) |
docs/agent/facts/INDEX.md:74:| EF-059 | ⭐⭐⭐ THE DRONE MATCHMAKER TREATS `rfStorageDepot`-FLAGGED SUPPLIES AS A STRICT LAST RESORT — any non-depot source (vegetation offer, loose pile, producer output) wins the pairing REGARDLESS of distance; distance only tie-breaks within a class. MEASURED 2026-08-16 at the FindTask seam, 985 witnessed pairings (`archive/c48pair2_*`): Seeds chose non-depot 479/479 with a NEARER fully-stocked ASSIGNABLE depot losing in 399 (specimen: 41,915 flown for one bush's 280 past a depot offering 180,000 at 5,733); Food obeyed the same law wherever loose food existed (81% nearer-depot losses) and used depots for the remainder (46%) only because loose food is finite. Alternatives eliminated by experiment: distance (the 150 brake, applied 100%, changed nothing), demand-side gating (a new diner bulk-filled to exactly 100% incl. a sub-load top-up ⇒ consumption's `rfWaitToFill` is a one-resource-unit rounding guard, not a carry gate), queue-bucket order (veg sits p1, depots mostly p0 with some p2/p3 — the HIGHER-bucket depots also lost). Both depot requests are branded (`StorageDepot.lua:67-68,466-467`). Corollaries, all measured: `desired_amount` withholds NOTHING from the supply side (every depot offered stored-in-full; it steers depot-to-depot rebalancing — the owner's reading, confirmed); depots RESTOCK THEMSELVES from the landscape through the same rule (125/479 pairings delivered INTO depots — a colony banks bush seeds it will never serve from storage); grown crop hexes offer FOOD via the same VegetationTaskRequesters; mega-dome food venues drain at farm rates (a Diner ~48,000/sol) and thrive on bulk. ⇒ on terraformed maps 'depots last' degenerates into 'depots never' for Seeds — the C47/C48 crumb-feeding, characterized | 2026-08-16 | 2026-08-16 | 30 | [EF-059.md](EF-059.md) |
docs/agent/facts/INDEX.md:79:| EF-064 | ⛔ `ProtectedPropertyObject` DOES NOT PROTECT ANYTHING IN RETAIL — `__newindex` asserts on an undeclared key and then `rawset`s it on the very next line (`CommonLua/PropertyObject.lua:1819-1823`), and by `EF-008` an assert does not unwind. So a write to a key the class never declared SUCCEEDS and execution continues to the next statement. The same shape applies to `__index` (`:1813-1817`), which asserts and then returns the class value anyway. ⇒ never explain a downstream failure as 'the protected-object assert halted it', and never read a missing class-field declaration as a behavioural cause; it is a diagnostic aid for developer builds only. This refuted another mod's stated mechanism for the Mod Manager screenshot bug (`C52`) while every line it cited was correct | — | 2026-08-16 | 41 | [EF-064.md](EF-064.md) |
docs/agent/facts/INDEX.md:80:| EF-065 | ⛔⛔ THE ENGINE ITSELF SHOWS THE PLAYER A MESSAGE BOX NAMING OUR MOD — but only on ONE of its two routes, and neither has a call site in our code. (a) any UNCAUGHT Lua error whose message OR call stack contains our `content_path` reaches `ReportModLuaError` (`Mod.lua:2958-2993`, live in retail because the block is gated `if not Platform.asserts`), which `ModPrint`s `Error in mod <title> (id …)` and pops `CreateMessageBox("Warning", "Mod-related problem detected in the game logic. Try disabling the mods…") + "Mod Flagged: <title>"` — once per mod id per process; (b) any throw at a code file's FILE SCOPE is caught by `pdofile`'s pcall (`lib.lua:242-251`), collected by `ModDef:LoadCode` (`:490-520`) — ⛔ CORRECTED 2026-08-19 (terminal audit): the (b) BOX IS DEAD CODE ON THIS TITLE — display is gated on `ModsPreGameMenuOpen` (init false, set nowhere) or `Msg("PreGameMenuOpen")`, which SM's `Lua/init.lua:1` override never raises (same mechanism as EF-055) ⇒ a file-scope throw is LOG-ONLY and the player sees NOTHING. `content_path` is configuration-INVARIANT (`Mod/SMR_CommunityFixPack/` packed and unpacked, `Mod.lua:1755-1758`), so (a) behaves identically in run B. MEASURED NEGATIVE 2026-08-19 is SPENT: surface (a) FIRED IN THE FIELD TWICE ON 2026-08-23/24 (F104 Passage Network, F105 vanilla landscape site) — both pass-through frames, NEITHER our defect; the box wording is now observed and OnLuaError IS confirmed raised for a thread error. The causing mod can be unnameable: PN had already returned one line before the throw. Response options: checklist 73 | 2026-08-19 | 2026-08-24 | 98 | [EF-065.md](EF-065.md) |
docs/agent/facts/INDEX.md:81:| EF-066 | ⭐⭐ A BUILT CLASS'S `Init` IS NEVER THE FUNCTION ANYONE ASSIGNED — `Init`/`Done` are COMBINED methods: `OnMsg.ClassesPreprocess` collects every classdef's own `Init` along each hierarchy and writes back a NEW composed closure per class (`classes.lua:1602-1676`), so a classdef-time wrapper on a PARENT is captured into every descendant's composition (why C51's one wrap reached the Zeus rocket, measured on a German screen) AND an identity check on a built class's `Init` reads "neither ours nor the original" on EVERY boot with ZERO other mods — the wave-12 probe's "a later mod has chained on top of ours" names a cause that cannot be the cause, and a wrapper genuinely lost pre-build would produce the SAME reassuring reading. Identity checks stay valid on plain methods and `_G` functions (copied by reference, never recomposed; wave-13 compared clean). ⭐ SWEPT AT LAST, MEASURED 2026-08-24 (`archive/f106_*.log`, probe `DispatchReach`): the pack declares **105** (class, method) targets — not ~60 — and 97 of them reach every descendant; the 66 (+1,328 multi-parent) unreached classes are shipped SUBCLASSES THAT RE-DECLARE the method, this watch's original question, failure mode under-coverage and never new harm. ⛔ Instantiation is NOT measured, so that is a reach gap and never a broken-fix count. ⛔ The 2026-08-24 "post-ClassesBuilt copy misses everything" sharpening is WITHDRAWN — `Register` applies inline at file-load time, so plain-method wraps patch CLASSDEFS and the builder copies ours down (F106 closed as refuted, F33 clean). ⚠️ The mirror-image defect that timing DOES cause is real and filed: capturing `prev` off a class that does not declare the method yields nil (`F107`) | 2026-08-24 | 2026-08-24 | 88 | [EF-066.md](EF-066.md) |
docs/agent/facts/_preamble.md:12:prompt 3) from `SMR-BugFixPack` @ `33d69f5` — all 53 facts, this preamble and
docs/agent/FIX_POLICY.md:8:> Copied from `SMR-BugFixPack/docs/agent/FIX_POLICY.md` @ `33d69f5` on
docs/agent/FIX_POLICY.md:19:> 2. **The namespace is renamed throughout** — `SMRFixPack.*` → `SMROptInPack.*`,
docs/agent/FIX_POLICY.md:20:>    `SMRFixPack_Disabled` → `SMROptInPack_Disabled`. ⛔ **§3's `SMRFixPack_*`
docs/agent/FIX_POLICY.md:40:   all (F23).
docs/agent/FIX_POLICY.md:63:   back with `rawget(_G, name)` in apply() to confirm the write landed (F22
docs/agent/FIX_POLICY.md:67:   gracefully and a copy does not** (recorded 2026-07-31 by the F86 layer-3
docs/agent/FIX_POLICY.md:76:     (`Colonist:ShouldLeaveForWork`, F04);
docs/agent/FIX_POLICY.md:79:     string-keyed table with `ipairs`, F03).
docs/agent/FIX_POLICY.md:83:   fixes F33 with zero copied logic.
docs/agent/FIX_POLICY.md:86:   (F04, F09, F11, F12...). Rules:
docs/agent/FIX_POLICY.md:96:     file-local was inlined, a helper re-derived; F03/F04/F09 are of this
docs/agent/FIX_POLICY.md:110:- **Self-check on the DECLARING class** (the F64 lesson): mod code runs before
docs/agent/FIX_POLICY.md:116:  APPEAR IN THAT MODULE'S OWN `Require` BLOCK (the F107 rule — adopted in the
docs/agent/FIX_POLICY.md:117:  fix pack 2026-08-24, carried here 2026-08-31).** `Require` validates what the
docs/agent/FIX_POLICY.md:119:  next door: the fix pack's `Fix_LandscapeCostRefresh` required the declaring
docs/agent/FIX_POLICY.md:122:  declared — and `prev` was nil on every boot (fix-pack F107). Had the
docs/agent/FIX_POLICY.md:127:  method (the F64 lesson above). Statically enforced for the shape that can
docs/agent/FIX_POLICY.md:139:- ⛔ **NEVER `Require` A PER-GAME RUNTIME GLOBAL AT APPLY TIME (the F110 rule —
docs/agent/FIX_POLICY.md:140:  fix pack 2026-08-30, carried here 2026-08-31).** `apply()`/`Require` run at
docs/agent/FIX_POLICY.md:151:- ⛔ **NO `apply()` MAY ASSUME A COLD BOOT (the F87 rule, 2026-07-31).** A mod is
docs/agent/FIX_POLICY.md:170:    idempotent. The F87 sweep found three sites that had this bug.
docs/agent/FIX_POLICY.md:171:  **Both paths must be tested** — a cold boot AND a run where the pack is
docs/agent/FIX_POLICY.md:172:  enabled from the main menu. The second one is why F87 shipped.
docs/agent/FIX_POLICY.md:186:  the veto. Donor pattern: Fix_LastTransmissionStorage's patch() prologue.
docs/agent/FIX_POLICY.md:189:  has fired — before that, absence just means "not loaded yet" (the F75
docs/agent/FIX_POLICY.md:199:  `SMRFixPack_*` and tolerate their absence (loading a save made with the mod,
docs/agent/FIX_POLICY.md:201:  ⛔ **YES, `SMRFixPack_` — that prefix is not a typo here and is not renamed
docs/agent/FIX_POLICY.md:208:  (e.g. F03's leaked modifiers), the cleanup is a **separate, clearly marked
docs/agent/FIX_POLICY.md:211:- **Exit hygiene (owner, 2026-07-31): the pack ships with its exit paved.**
docs/agent/FIX_POLICY.md:216:  lost the pack (the only console-viable remedy). Record + spec gate + open
docs/agent/FIX_POLICY.md:244:>    that **ships at launch, alongside the pack**. A harmful residual is never
docs/agent/FIX_POLICY.md:280:the pack could not.
docs/agent/FIX_POLICY.md:296:engine frames included (`Fix_CaveInsNoDisasters` is capturable this way,
docs/agent/FIX_POLICY.md:305:self-limits, forever if it loops). `Fix_MeteorFrequency` killed a colony's
docs/agent/FIX_POLICY.md:372:`Fix_LastTransmissionStorage`'s `Condition.eval`, disclosed-no-build,
docs/agent/FIX_POLICY.md:380:analysis at `docs/agent/reports/SAVE_SAFETY_REDESIGN.md` and `agent/bugs/F86.md`
docs/agent/FIX_POLICY.md:381:in the fix pack repo.
docs/agent/FIX_POLICY.md:387:> for the fix pack, and still the test that decides which of the two mods a
docs/agent/FIX_POLICY.md:390:**The inversion, stated plainly:** the fix pack may only repair *unintended*
docs/agent/FIX_POLICY.md:402:  (c) a **repair the fix pack declined** because intent was ambiguous or the
docs/agent/FIX_POLICY.md:422:- **No cross-module dependency inside this mod, and none on the fix pack.**
docs/agent/FIX_POLICY.md:424:  with the fix pack absent (the standalone invariant, `CLAUDE.md`). A module
docs/agent/FIX_POLICY.md:438:### §4-donor — the fix pack's §4, kept verbatim (do not edit; the donor is authoritative for it)
docs/agent/FIX_POLICY.md:443:it belongs in the fix pack as a plain fix, not here behind a toggle.*
docs/agent/FIX_POLICY.md:455:> > contradicted itself while F49(a) shipped a no-op R4 rider against the new
docs/agent/FIX_POLICY.md:456:> > "R4 does not ship" line; that guard was **stripped from `Fix_TrainMinors`
docs/agent/FIX_POLICY.md:457:> > on 2026-08-01** (`agent/bugs/F49.md`; A/B code-gate leg ran clear), so the rule and the
docs/agent/FIX_POLICY.md:458:> > shipped code now agree. **Live consequence on adoption:** F29 and F57(a) are
docs/agent/FIX_POLICY.md:477:>   gives confident answers with no validity there (the F49(c) lesson). A
docs/agent/FIX_POLICY.md:492:>   full replacement needs an explicit user decision (the F24 lesson). **R4
docs/agent/FIX_POLICY.md:505:>   sibling code in the same file (the F07/F08/F02 pattern).
docs/agent/FIX_POLICY.md:513:> sharpening the split makes necessary: **the Relaunched Fix Pack is "another
docs/agent/FIX_POLICY.md:515:> around a fix-pack behaviour, and a fix-pack bug is reported and fixed there.
docs/agent/FIX_POLICY.md:546:   *(This is tier **R4**. F28 is the worked example: `Research:ReplaceTech` has
docs/agent/FIX_POLICY.md:554:   without anyone touching a mod. *(Tier **R3**. F29's two items are the worked
docs/agent/FIX_POLICY.md:557:   already-ordered timings. F27, F31 and F43 are the same shape.)*
docs/agent/FIX_POLICY.md:565:mod-facing. **F29 described itself as a "mod-facing bundle" with "No shipped
docs/agent/FIX_POLICY.md:568:(the F49(c) lesson, applied to provenance).
docs/agent/FIX_POLICY.md:574:precedent — one (F28) already violated this rule and was retired under it.
docs/agent/FIX_POLICY.md:576:**Why this exists.** The pack shipped `Fix_ReplaceTechCount` (F28) against a
docs/agent/FIX_POLICY.md:629:  toggle OFF**, which is how F86 Site 2 was found. Never infer save-cleanliness
docs/agent/FIX_POLICY.md:644:  strings from this pack use `Untranslated("...")` — the pack ships no loc tables
docs/agent/FIX_POLICY.md:646:  crashes (the F14 probe lesson). Log/console text stays plain strings.
docs/agent/FIX_POLICY.md:652:  every other language. `Fix_TechDescriptionBuilding` did exactly this and has
docs/agent/FIX_POLICY.md:653:  never changed anything (**`agent/bugs/F98.md`**; F25 demoted, and **no longer citable as
docs/agent/FIX_POLICY.md:660:  "RE-USING A SHIPPED TRANSLATION ID …". ⭐ **Owner decision 2026-08-02: the pack
docs/agent/FIX_POLICY.md:687:  belongs in the fix pack (§4a).
docs/agent/FIX_POLICY.md:691:  the Relaunched Fix Pack installed and with it absent** (the standalone
docs/agent/prompts/CONTAMINATION_AUDIT.md:1:# CONTAMINATION_AUDIT — one-off: is this repo clear of fix-pack contamination, and does everything in it have a place here?
docs/agent/prompts/CONTAMINATION_AUDIT.md:9:**Why.** This repo was split out of `SMR-BugFixPack` on 2026-08-12 and has taken
docs/agent/prompts/CONTAMINATION_AUDIT.md:29:   the fix pack", "where new things go"), `agent/WORKFLOW.md` "Layout" and the
docs/agent/prompts/CONTAMINATION_AUDIT.md:42:| **CONTRACT** | the five persisted names `SMRFixPack_ack_notworking`, `_closed_to_new_residents`, `_no_homeless`, `_DroneSpeedDial`, `_DroneCarryDial` and the option/choice strings of PROVENANCE §2 rows 6–9, wherever they occur | ⛔ untouchable; count them, confirm each occurrence is in §2, and that no persisted-looking name exists outside §2 |
docs/agent/prompts/CONTAMINATION_AUDIT.md:44:| **POINTER** | a live instruction that deliberately points at the fix pack: the owner's `PLAYTEST_CHECKLIST.md`/`PLAYTEST_HELP.md` (single-sourced there), the shared TestKit, `EF-` id allocation, `DRONE_PROJECT_PROMPT.md`, `PARKED_OPTIN_REFERENCES.md`, `GENERAL_USE_PROMPT.md`, the FIX_POLICY/WORKFLOW donor blocks that carry an explicit ADAPTED / N/A-here marker, "works with or without the Relaunched Fix Pack" in player text | legitimate; list them so the next audit does not re-derive them |
docs/agent/prompts/CONTAMINATION_AUDIT.md:45:| **STALE** | a live instruction, tool comment, docstring, label or default that was true in the fix pack and is wrong or meaningless here, AND is not marked N/A/ADAPTED — e.g. a rule citing a fix-pack-only mechanism as if it were this mod's, a tool printing "fix pack", a default path or module name from the other tree, a count that is the other repo's | fix in this session (docs/tools only) or add the missing N/A marker; every fix cited in the report |
docs/agent/prompts/CONTAMINATION_AUDIT.md:46:| **CONTAMINATION** | executable code referencing `SMRFixPack`/`[CommunityFixPack]`/`SMR_CommunityFixPack`/a `Fix_*` file other than as a CONTRACT string or a comment; player-facing text naming the other mod as if it were this one; tool LOGIC keyed to the other mod's namespace or files; a live doc instructing a session to act on the fix pack's tree from here | ⛔ code/player-text hits: STOP and report (§5); tool/doc hits: fix and cite |
docs/agent/prompts/CONTAMINATION_AUDIT.md:55:  "SMRFixPack|CommunityFixPack|SMR_CommunityFixPack|SMR-BugFixPack|SMR-CommunityFixPack|[Ff]ix[ -][Pp]ack|\bFix_[A-Z]|\bF[0-9]{2,3}\b|\bC[0-9]{2}\b|the pack\b|76 files|75 modules|80 modules" \
docs/agent/prompts/CONTAMINATION_AUDIT.md:63:   comments), nothing else. Verify ban 2 mechanically: every `SMRFixPack` token
docs/agent/prompts/CONTAMINATION_AUDIT.md:65:   AST for Name/Index nodes containing `SMRFixPack` — there must be none).
docs/agent/prompts/CONTAMINATION_AUDIT.md:67:   "works with or without the Relaunched Fix Pack" sentences (POINTER). Anything
docs/agent/prompts/CONTAMINATION_AUDIT.md:79:   unmarked donor prose → add the marker (ADAPTED / N/A here / fix-pack history).
docs/agent/prompts/CONTAMINATION_AUDIT.md:81:   F-ids, C-ids and fix-pack module names inside a D-entry's narrative are
docs/agent/prompts/CONTAMINATION_AUDIT.md:85:   whose only content is a fix-pack module's behaviour is a Pass-B candidate.
docs/agent/prompts/CONTAMINATION_AUDIT.md:106:`blocking_analysis.py` is cited by D06's F86 record); `00_Core.lua`'s `DataPatch`
docs/agent/prompts/CONTAMINATION_AUDIT.md:112:fix-pack module; `.claude/settings.json`'s allowances; `README.md` (mod-facing)
docs/agent/prompts/CONTAMINATION_AUDIT.md:116:disposition (delete / move to the fix pack / write the reason and keep) and the
docs/agent/prompts/CONTAMINATION_AUDIT.md:131:3. Owner items on the fix pack's `docs/PLAYTEST_CHECKLIST.md` → "Decisions
docs/agent/prompts/CONTAMINATION_AUDIT.md:144:- A `SMRFixPack` reference in EXECUTABLE position (not a string, not a comment)
docs/agent/prompts/CONTAMINATION_AUDIT.md:148:- A persisted-looking name (`SMRFixPack_*` / `SMROptInPack_*` written onto an
docs/agent/prompts/CONTAMINATION_AUDIT.md:164:- Anything about the fix pack repo's own state — this audit reads it only to
docs/agent/prompts/DISPATCH.md:3:Adapted from the fix pack's `prompts/DISPATCH.md` (2026-08-29) for THIS repo.
docs/agent/prompts/DISPATCH.md:29:runtime; a **true standalone** beside the Relaunched Fix Pack. The map is
docs/agent/prompts/DISPATCH.md:41:   STALE-PROBE GATE binds first: `grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/`,
docs/agent/prompts/DISPATCH.md:49:  `SMRFixPack_*` field and modifier id this mod writes keeps its exact bytes
docs/agent/prompts/DISPATCH.md:50:  (`agent/PROVENANCE.md` §2); and ZERO `SMRFixPack` references in executable
docs/agent/prompts/DISPATCH.md:58:  §2 enable-path / declaring-class / the F107 wrap rule / the F110 runtime-global
docs/agent/prompts/DISPATCH.md:67:  STATE byte budget, `metadata.lua` load order and the F107 wrap check. Counts
docs/agent/prompts/DISPATCH.md:75:  commit, the same as the fix pack. ⛔ TestKit is local-only BY DESIGN.
docs/agent/prompts/DISPATCH.md:95:  route it to the fix pack's `docs/PLAYTEST_CHECKLIST.md` → "Decisions waiting on
docs/agent/prompts/DISPATCH.md:112:- A **decision the owner must make** → the fix pack's checklist, never only here.
docs/agent/prompts/DISPATCH.md:120:| a LIVE playtest at the keyboard (both mods) | fix pack `prompts/GENERAL_USE_PROMPT.md` (single-sourced there) |
docs/agent/prompts/DISPATCH.md:121:| this mod's LAUNCH — the whole thing | `agent/STATE.md` launch obligation → fix pack `reports/PARKED_OPTIN_REFERENCES.md` restore checklist, then the fix pack's `prompts/RELEASE.md` shape adapted (`WORKFLOW.md` "Release marking" + "Release steps") |
docs/agent/prompts/DISPATCH.md:122:| the owner's mechanical pack+upload only | fix pack `docs/UPLOAD_WORKFLOW.md` (+ `reports/RELEASE_PORTAL_PREP.md`) — after `tools/upload_preflight.py` reports 0 FAIL |
docs/agent/prompts/STATE_EVICTION.md:3:Carried 2026-08-31 from the fix pack's `prompts/STATE_EVICTION.md` (designed
docs/agent/prompts/STATE_EVICTION.md:70:- Owner-facing asks always live in the fix pack's checklist, never only here
docs/agent/prompts/WORK_PROMPT.md:13:> and the fix pack's checklist. The only edits this file takes are corrections
docs/agent/prompts/WORK_PROMPT.md:17:> **issues once the mod is live** (player reports, field bugs); the fix pack's
docs/agent/prompts/WORK_PROMPT.md:24:Options; patched at runtime over the mod's own copy of the pack framework
docs/agent/prompts/WORK_PROMPT.md:25:(`SMROptInPack`); a true standalone beside the Relaunched Fix Pack. Not yet
docs/agent/prompts/WORK_PROMPT.md:27:**persisted names are save contract** (every `SMRFixPack_*` field/modifier id
docs/agent/prompts/WORK_PROMPT.md:28:keeps its bytes — `agent/PROVENANCE.md` §2) and **zero `SMRFixPack` references
docs/agent/prompts/WORK_PROMPT.md:44:   first — `grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/`, in the
docs/agent/prompts/WORK_PROMPT.md:53:| **drone work** (D06 overhaul, D09 dials, `FUTURE_IDEAS.md` #7) | UNFROZEN 2026-08-31. ⛔ Do not build any part of the overhaul until the owner picks among the three options in the fix pack's `prompts/DRONE_PROJECT_PROMPT.md` §3; a time-boxed feasibility pass on option 3 is allowed if the owner asks. Designs: `reports/DRONE_OVERHAUL_OPTIONS.md`, `SEED_LOGISTICS_HANDOFF.md`. Log the commander profile with any measurement (D06 entry) |
docs/agent/prompts/WORK_PROMPT.md:56:| **tooling** | `tools/` inventory + what each proves: `agent/PROVENANCE.md` §6. Port from the fix pack with a ledger row; every instrument is an over-reporter — adjudicate a row by reading the source line, never by the count |
docs/agent/prompts/WORK_PROMPT.md:57:| **launch prep** | `STATE.md` "NEXT" (the ordered list), `WORKFLOW.md` "Release marking" + "Release steps" bullets 1–8, `tools/upload_preflight.py` 0 FAIL, the fix pack's `reports/PARKED_OPTIN_REFERENCES.md` restore walk |
docs/agent/prompts/WORK_PROMPT.md:60:| **a live issue / a live playtest** | `prompts/DISPATCH.md` / fix pack `GENERAL_USE_PROMPT.md` |
docs/agent/prompts/WORK_PROMPT.md:67:  neutrally with the trade-offs measured, put the ask on the fix pack's
docs/agent/prompts/WORK_PROMPT.md:86:   installed named in the module's `Require` block (F107); never `Require` a
docs/agent/prompts/WORK_PROMPT.md:87:   per-game global (F110); `SMROptInPack_Disabled` honoured in every handler.
docs/agent/prompts/WORK_PROMPT.md:93:5. **A/B in the TestKit** (`C:\Dev\SMR-BugFixPack-TestKit`, shared, local-only):
docs/agent/prompts/WORK_PROMPT.md:125:- An engine fact → fix pack `EF-###` first, mirrored here at the same id.
docs/agent/prompts/WORK_PROMPT.md:144:- "Standalone" or "works without the fix pack" for a change not run in BOTH
docs/agent/prompts/WORK_PROMPT.md:156:lesson to its §5 home, never here. Owner asks → the fix pack's checklist.
docs/agent/PROVENANCE.md:3:This repo was **split out of `SMR-BugFixPack` on 2026-08-12** by the chain
docs/agent/PROVENANCE.md:12:| Community Fix Pack | `C:\Dev\SMR-BugFixPack` | `33d69f5d8412a3924a53b93de38f00f1c23e3866` | `github.com/catt144/SMR-CommunityFixPack` |
docs/agent/PROVENANCE.md:13:| TestKit (shared, never shipped) | `C:\Dev\SMR-BugFixPack-TestKit` | `d8e1fbf56c4a7be4913fbdc34f2bc9b96b7c07c5` | none — local only by decision |
docs/agent/PROVENANCE.md:16:after them in the fix pack's history; `git log --oneline` there, around
docs/agent/PROVENANCE.md:27:| `Code/00_Core.lua` | `Code/00_Core.lua` | ADAPTED | whole-file token rename `SMRFixPack` → `SMROptInPack` (which also carries `_Disabled`/`_Optional`), then five literal adaptations: log prefix `:27`, mod id `:64` + `:401`, dialog title/body `:512-514`, and the veto-log line `:412`. ⛔ The rename is the WHOLE file, not a listed subset — `:270` (`rawget(_G,"SMRFixPack_Disabled")`) and `:384` (the bare global) would crash every `Register` with the fix pack absent if they were left alone |
docs/agent/PROVENANCE.md:28:| `Code/Opt_*.lua` ×8 | same names | ADAPTED | the same token rename, plus: `Opt_DroneOverhaul`'s CLONED logger prefix (its own `[CommunityFixPack]` literal, not Core's), the two infopanel rollover titles that name the mod (`Opt_ResidencyControl`, `Opt_NoHomeless`), `Opt_DroneStatDials`' `ApplyModOptions` mod-id guard, and the eight header comments pointing at the Mod Options page. **No behaviour edit of any kind** |
docs/agent/PROVENANCE.md:30:| `docs/agent/bugs/D01…D07, D09, D12` | same names | ADAPTED | bodies byte-preserved; front matter renumbered (`seq`/`row` 1..9 here) with the donor's numbers kept as `donor_seq`/`donor_row`. The fix pack keeps a TOMBSTONE entry at each id pointing here |
docs/agent/PROVENANCE.md:31:| `docs/agent/FIX_POLICY.md` | same | ADAPTED | §4 inverted for a mod whose product IS opinionated modules — the fix pack's §4 is kept quoted in full as §4-donor, because it is the reason these modules were `Opt_` in the first place. Everything else stands, with `SMRFixPack.*` → `SMROptInPack.*` |
docs/agent/PROVENANCE.md:34:| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | same | VERBATIM (moved) | D06/D09's design study; the fix pack keeps a one-line pointer |
docs/agent/PROVENANCE.md:38:| `tools/blocking_analysis.py` | same | VERBATIM | `Opt_DroneOverhaul`'s F86 Tier-2 record depends on its verdict staying re-runnable |
docs/agent/PROVENANCE.md:44:sourced in the fix pack by design — `docs/README.md` says why), the 73 `Fix_*`
docs/agent/PROVENANCE.md:45:modules and `90_SaveSanitizer.lua`, and the fix pack's `docs/BUGS.md` /
docs/agent/PROVENANCE.md:54:EXACT bytes forever, `SMRFixPack_` prefix and all.** They were written by these
docs/agent/PROVENANCE.md:55:modules while they lived in the fix pack; a rename would orphan live state in
docs/agent/PROVENANCE.md:62:| 1 | `SMRFixPack_ack_notworking` | field on `Building` objects | `Opt_AcknowledgedWarnings.lua` (`obj[FLAG] = true`), cleared on recovery | same file |
docs/agent/PROVENANCE.md:63:| 2 | `SMRFixPack_closed_to_new_residents` | field on `Dome`/`MicroGHabitatBase` | `Opt_ResidencyControl.lua` via `building:TogglePolicy(FLAG, broadcast)` → shipped `Community:SetPolicyState` | same file |
docs/agent/PROVENANCE.md:64:| 3 | `SMRFixPack_no_homeless` | field on `Dome`/`MicroGHabitatBase` | `Opt_NoHomeless.lua` (`TogglePolicy`, and its bespoke `SetPolicyState` broadcast) | same file |
docs/agent/PROVENANCE.md:65:| 4 | `SMRFixPack_DroneSpeedDial` | **label-modifier id** in `UIColony.label_modifiers["Drone"]`, holding a vanilla `Modifier` object | `Opt_DroneStatDials.lua` | same id (replace/remove) |
docs/agent/PROVENANCE.md:66:| 5 | `SMRFixPack_DroneCarryDial` | as above, label `Consts` | `Opt_DroneStatDials.lua` | same |
docs/agent/PROVENANCE.md:73:(`SMR_CommunityFixPack` → `SMR_CommunityOptInPack`), so the player's saved
docs/agent/PROVENANCE.md:79:**Provably never persisted, so the rename was safe:** `SMRFixPack_Optional` /
docs/agent/PROVENANCE.md:80:`SMRFixPack_Disabled` (now `SMROptInPack_*`) — plain `_G` tables built with
docs/agent/PROVENANCE.md:97:✅ **DECIDED (owner, 2026-08-13): `"Community Fix Pack: Opt-In Modules"`** —
docs/agent/PROVENANCE.md:100:shared naming lets the fix pack surface its sibling). **Swept the same day, one
docs/agent/PROVENANCE.md:116:`github.com/catt144/SMR-CommunityOptInPack`, matching the fix pack's setup. All
docs/agent/PROVENANCE.md:126:`C:\Dev\SMR-BugFixPack-TestKit`**, and ONE kit serves BOTH mods. It is not
docs/agent/PROVENANCE.md:138:  `SMRTest.OptMissing(id)` (the fix pack's is `FixStatus`/`FixMissing`), and
docs/agent/PROVENANCE.md:143:  `fix pack present: %d/%d fixes active` and
docs/agent/PROVENANCE.md:145:  bracketed token (`[CommunityOptInPack]` / `[CommunityFixPack]`) — `Pack]`
docs/agent/PROVENANCE.md:151:## 5. What the fix pack kept, and what it lost
docs/agent/PROVENANCE.md:164:The fix pack kept building after the split; this pass carried across what it
docs/agent/PROVENANCE.md:166:Donor sha for every row: `SMR-BugFixPack` @ `bec2e06d` (v5 closed, 2026-08-30).
docs/agent/PROVENANCE.md:175:| `tools/l3_save_footprint.py` | ADAPTED | `NAMED_STATE` matches BOTH prefixes (persisted names keep `SMRFixPack_`), rows labelled by the token found; `REGISTER`/`resolved` renamed |
docs/agent/PROVENANCE.md:181:| `docs/agent/facts/` | VERBATIM (re-sync) | 7 donor-updated shared facts taken whole (EF-008/023/039/051/054/055/056); EF-057…068 added; this repo's old EF-057/058 are now EF-061/062 (their donor ids). ⛔ ids are allocated by the fix pack from here on (`WORKFLOW.md` reading path 2) |
docs/agent/PROVENANCE.md:182:| `docs/agent/prompts/DISPATCH.md`, `STATE_EVICTION.md` | ADAPTED | this repo's paths, bans, route table; the playtest prompt stays single-sourced in the fix pack |
docs/agent/PROVENANCE.md:190:mod" rather than "the pack", and `l3 --src` refuses a path with no `Lua/` under
docs/agent/PROVENANCE.md:196:`PUBLIC_SURFACE_SWEEP.md` / `SITE_AUDIT.md` (all bound to the fix pack's live
docs/agent/reports/CHAIN_METHOD.md:8:classed as intractable — F86 save-safety (discovery to verified repair of both
docs/agent/reports/CHAIN_METHOD.md:45:   existed (C23 → F97 shipped at a fraction of its approved cost); a route
docs/agent/reports/CHAIN_METHOD.md:46:   recorded *"verified feasible"* did not exist (F46, correctly declined);
docs/agent/reports/CHAIN_METHOD.md:58:   the unlock.** "Build it, but it's not locked — the QA reviews it" (F97)
docs/agent/reports/CHAIN_METHOD.md:71:   the terminal QA) independently validated the pack's evidence base AND
docs/agent/reports/CHAIN_METHOD.md:72:   surfaced findings the informed record had missed (the F55 intent tell).
docs/agent/reports/CHAIN_METHOD.md:113:| Routing without preconditions | two items hopped 3 prompts each (a suite-run debt; C40's enacted-law need) | every routed item carries **TAKEABLE WHEN <condition>**; situation-gated items go to the checklist as riders, not to prompts |
docs/agent/reports/CHAIN_METHOD.md:115:| Briefs staler than entries | prompt 7's brief contradicted the C33 entry it described | briefs cite entries; sessions act on the ENTRY, and the brief says so |
docs/agent/reports/CHAIN_METHOD.md:120:| ⛔ A seal the standing rules defeat (f11-f99 chain, 2026-08-03) | the sealed prompt 1 was force-fed sealed material BEFORE it opened its own prompt: `CLAUDE.md` makes STATE.md a mandatory whole-file read (its F11/F99 paragraphs were sealed), and chain rule 1's `git log --oneline -10` prints the sealed commits' subject lines. The attestation was honest and the damage was contained (everything AGREEING with the anchor was discounted; only anchor-contradicting findings were counted) — but the seal was structurally unholdable | seal at the SOURCE, not the reader: before the chain starts, EXTRACT the sealed STATE.md paragraphs into a sealed side-file and leave a one-line pointer in STATE.md; prescribe a subject-hiding staleness check in the sealed prompt (`git log --format=%h -10` + `git pull`); and keep the attestation requirement — a broken seal honestly mapped (what leaked, what it anchors) preserved most of this second opinion's value |
docs/agent/reports/CHAIN_METHOD.md:124:| ⛔ A run's preconditions include state a PREVIOUS chain mutated, and the unblock is owner-only (unattended-2, 2026-08-11 — the first Opus-builds/Fable-audits chain that SHIPPED code) | The night's first launch read `pack=0/0 active`: corun-batch-2's leg T had disabled the pack in the Mod Manager a day earlier and no close-out owned the re-enable. The payload had no run-condition gate, so six steps banked readings about code that never executed; the unblock was one human click, unscriptable (`AccountStorage`/`SaveAccountStorage`/`ModsReloadItems` all ModEnvBlacklist keys, no console at the main menu), owner asleep. The executor spent the dead time on a **declared HARNESS REHEARSAL** — the mode flipped by the arm script and read back off disk, a `MODE` banner in the log, every verdict-bearing line stamped `VOID` — which proved the three-load/two-round-trip flow and both fresh harness fixes (EF-050's verbatim savename, the new gate). The owner's re-run then verified all four items in a single shot; the terminal audit sustained every verdict. | **Authoring:** a chain whose run depends on externally-mutable state (mod enabled, cloud sync, account settings) gates on that state AT RUN TOP, and the gate STOPS the run (WORKFLOW batch-2 rule 7 as amended 2026-08-11); any leg that mutates such state HANDS THE RESTORE BACK to the owner explicitly in its close-out. **Method:** when a run blocks on an owner-only unblock, don't park — prove the instrument with a declared-VOID rehearsal (mode armed by script and read off disk, bannered in the log, verdict lines stamped so the log can never be quoted as a measurement) so the unblocked re-run is single-shot instead of a second night of harness archaeology. |
docs/agent/reports/CHAIN_METHOD.md:126:| ⛔ An attended sitting is a priority queue the owner may reorder live, and the brief's minutes model does not survive contact (corun-batch-1, 2026-08-05 — the first BATCHED attended sitting) | The sitting ran 2 of its 5 legs and ~2 h of owner time against a ~24-minute promise — but most of the overrun was the owner deliberately chasing their own leads (the F99 hunt, the dev-cheat exploration), which produced the sitting's best finds (`F101`, both F99 samples) and which the owner then ruled an **override, not scored against the estimate**. The rig's own genuine miss was separable and small in kind but large in effect: one moment budgeted at 3 min took ~25 because its prep-measured fixture had evaporated (nothing re-confirmed it at sitting time, and no instrument could find a replacement subject). Structurally, the rig has no input path into a running game, so every console line was the owner's hands — a cost class the measure-moments model cannot see. | Three halves. **Authoring:** an attended brief is a PRIORITY QUEUE, not a schedule — order legs so a truncated sitting still banks the decider first, and treat owner deviation as a feature to absorb (witness discipline applies to whatever runs, planned or not), never a variance to explain away; once the owner overrides onto a lead, state the plan's position once and then stop — no per-message back-on-track reminders, and the session keeps the sent/checked/outstanding ledger so the owner does not have to (owner rule 2026-08-05, verbatim in WORKFLOW Co-runs). **Estimating:** re-confirm every fixture AT SITTING TIME, name a subject-finder instrument per moment, and budget console-driving explicitly until the rig has an input path (all binding in `WORKFLOW.md` Co-runs). **Scoring:** separate owner-directed deviation from rig misses before scoring anything — and only the owner may rule their own time out of scope. |
docs/agent/reports/CHAIN_METHOD.md:128:| ⛔ Evidence the terminal audit cannot re-read: owner verbatims that live only in the session transcript (corun-pt15, 2026-08-11 — the first chain designed to reach a `tested` grant) | The sitting gathered four owner verbatims at measure moments and pushed exactly ONE through the harness's log-note primitive (F85's); the other three — including the verdict backing F07's `tested` grant — exist only in the session transcript. The sitting flagged this honestly and deferred the grant ruling to the audit rather than assuming, which is the right half of the pattern; the audit sustained the grant (owner eyes attended the measure moment, the quote is verbatim on the entry, everything forced is named in the grant) but had to rule on evidence it could not re-read, and a future re-audit never can. | Two halves. **Authoring:** the sitting prompt MANDATES relaying every owner verbatim through the log-note primitive the moment it is spoken (now binding in `WORKFLOW.md` Co-runs, corun-pt15 rule 3) — chat stays where the owner speaks and transcript quotes stay quotable, but a log-resident quote is re-readable forever. **Method:** when a sitting knows a grant's provenance is mixed, deferring the ruling to the terminal audit WITH the exposure stated (the notes' "the audit should rule on it rather than assume") is the correct move — keep it; an upstream prompt that grades its own strongest claim is the failure shape. |
docs/agent/reports/CHAIN_METHOD.md:295:the work.** L1 and L2 both read all 76 files. A lens is *a different question
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:8:> telemetry `SMRFixPack.DroneReport()`), and `Code/Fix_ExtenderFlapChurn.lua`
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:9:> (F77, default-on). See the D06 entry in BUGS.md. Registration-H, H-v2
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:13:DroneControl bullet + F77): *"what is even feasible if we want an optional overhaul
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:44:   priority is preserved for free.) The F73 "pre-wrap only" fact applies to command
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:87:unreachable cache exactly as vanilla does; F55's fix already retires those). Perf:
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:152:order unknowable, rule 1), the yield bought nothing; and it perturbs F50/F68/F71
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:174:**Risk: MEDIUM-HIGH.** Reset mid-command is the F50 churn primitive — used
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:201:at the declaring class (F64 apply-check lesson applies).
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:274:* **F77 debounce** (extender flap churn) — a plain repair, ships as `Fix_*` regardless
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:275:  of the overhaul decision; sketch on the F77 entry. Without it, any overhaul fights
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:277:* **`SMRFixPack.DroneReport()`** — console/TestKit telemetry: per hub — handle, class,
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:309:7. **F77 fix** — separate `Fix_`, ships with the next wave independent of all above.
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:316:machinery in the game — hubs, rovers, and the rocket cargo path (F50/F68/F70/F71) all
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:317:run through these queues. Whatever subset is approved must re-pass the F50
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:318:rocket-churn and F55 unreachable scenarios, plus a new probe set (moonlight
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:516:  `are_requesters_connected` guard semantics. Debounce rebuilds using the F77
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:549:  re-registration → F77 debounce.
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:648:# I + J — seed-supply routing pair (added 2026-08-15 out of the fix pack's C47/C48 measurement chain)
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:652:`C47`/`C48` seed-routing family lives HERE, in this house, behind this pack's
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:653:default-OFF convention — the fix pack gets, at most, data-shaped repairs, and
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:654:only after `C48` is ruled. This section is the standing record of that boundary.
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:656:**Provenance.** The fix pack's `C48` leg (2026-08-15, `archive/c48veg_*` in that
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:728:  population churns fast — the C48 ladder watched it move 3,583 → 3,457 →
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:734:  the routing — the fix pack's planned intervention leg tests exactly this
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:737:* ⛔⛔ **REFUTED 2026-08-15, the same evening, by that leg** (fix pack
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:753:un-parking is an owner decision after launch. Cross-reference: fix pack
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:754:`agent/bugs/C47.md` + `C48.md` (the measurements), this repo's `D02.md` (the
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:767:carrying 985 decisions on 2026-08-16, fix pack `archive/c48pair2_*`):
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:795:⛔ **Engineering lessons that BIND any build here** (fix pack `EF-058/060`):
docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md:809:existing pairing-log instruments (fix pack `docs/agent/prompts/c48-pairing/`)
docs/agent/reports/READINESS_REVIEW_0831.md:1:# Readiness review — 2026-08-31: this workspace against the fix pack's tooling, tests and process
docs/agent/reports/READINESS_REVIEW_0831.md:4:fix pack's tools, tests, auditing, chain method and processes should apply here.*
docs/agent/reports/READINESS_REVIEW_0831.md:5:**Method:** inventory both repos (`C:\Dev\SMR-BugFixPack` @ `bec2e06`, this repo @
docs/agent/reports/READINESS_REVIEW_0831.md:18:2026-08-12 snapshot of the fix pack's method: doccheck GREEN, hook enabled, tree clean,
docs/agent/reports/READINESS_REVIEW_0831.md:19:and every improvement the fix pack made in the following 19 days absent. The three
docs/agent/reports/READINESS_REVIEW_0831.md:37:| facts | 58 here vs 68 there; **7 shared facts updated in the fix pack after the split, not carried** (EF-008/023/039/051/054/055/056); **id collision**: this repo's EF-057/058 (2026-08-16) ≠ the fix pack's EF-057/058 (08-15/08-19); this repo's two were the fix pack's EF-061/062 | `cmp` per file; `git log --diff-filter=A` |
docs/agent/reports/READINESS_REVIEW_0831.md:38:| tools | 5 here vs 20 there; the 14 missing include the whole L2–L8 audit ladder, the F107 wrap check, the three release gates | `find tools/` |
docs/agent/reports/READINESS_REVIEW_0831.md:39:| doccheck drift | donor gained: STATE byte budget (08-18), `tested-attended/-unattended` vocabulary (08-15), `LOAD_ORDER_RULES` (08-17), F107 wrap check (08-24) | `git diff 33d69f5..HEAD -- tools/doccheck.py` |
docs/agent/reports/READINESS_REVIEW_0831.md:40:| process docs | WORKFLOW missing "Release marking — tags, not branches", the 08-24 probe rule, the byte-budget rule 8; FIX_POLICY missing F107 + F110; CHAIN_METHOD missing §5a (fan-out rule) + commit-the-folder rule; `prompts/` EMPTY (donor: 13 standing/one-off prompts) | header diffs, `grep` |
docs/agent/reports/READINESS_REVIEW_0831.md:61:| `l6_reachability.py` | namespace | 4 global replacements (`ChooseDome` 8 uses in 5 files; `SuppressNotification` 1 use — F85 shape, read it) and 9 members; `Community.CanAcceptNewColonists`, `TaskRequestHub.FindTask`, `Colonist.FindEmigrationDome` have ≤3 sites tree-wide — triage rows, already read by their entries |
docs/agent/reports/READINESS_REVIEW_0831.md:63:| `l8_hostile_input.py` | namespace + module trio | CONTROLs pass (documented form vetoes exactly `ClassicRockets`; nothing set vetoes nothing). Hostile values kill module FILES at load: `SMROptInPack_Disabled = true`, `SMROptInPack = true`, `SMROptInPack = {}`, a throwing `__index`. **Identical to the donor's L8 verdict** — `00_Core.lua` is the same code — and inherits its adjudication (`SMR-BugFixPack/docs/agent/reports/L8_ADVERSARIAL_MAP.md`); the fix pack shipped with it |
docs/agent/reports/READINESS_REVIEW_0831.md:75:  allocation rule** (fix pack allocates; this repo mirrors); a tools pointer.
docs/agent/reports/READINESS_REVIEW_0831.md:76:- **FIX_POLICY.md** §2: the F107 rule and the F110 rule, each adapted with this repo's
docs/agent/reports/READINESS_REVIEW_0831.md:77:  own state (three allowlisted sites; `Opt_DroneStatDials` already does the F110
docs/agent/reports/READINESS_REVIEW_0831.md:83:  stays single-sourced in the fix pack with the playtest files.
docs/agent/reports/READINESS_REVIEW_0831.md:92:Survey of `C:\Dev\SMR-BugFixPack-TestKit` (100 probes; 94 excluding the 6 rescue
docs/agent/reports/READINESS_REVIEW_0831.md:99:| **No opt-in-only run mode**: `RunAll(kind_filter)` filters on `kind`, never on owner; a standalone leg prints ~85 fix-pack FAILs around 8 real verdicts | `00_TestCore.lua:456` | the true-standalone leg is readable only by hand |
docs/agent/reports/READINESS_REVIEW_0831.md:100:| **Enable-path leg hardcodes the fix pack**: `PACK_ID = "SMR_CommunityFixPack"` | `98_EnablePathLeg.lua:54` | this mod's normal first-run path (tick at the main menu → in-place `ReloadLua`) has never been measured for THIS mod by that leg — and it is exactly the F87/double-Register territory |
docs/agent/reports/READINESS_REVIEW_0831.md:101:| **`FixtureCarry` is blind to D09's residue**: channel 5 hardcodes `SMRFixPack_F35_`; channel 4 walks `city.labels`, not `colony.label_modifiers` | `99_FixtureCarry.lua:164-186` | a stale `SMRFixPack_DroneSpeedDial`/`CarryDial` modifier in a fixture is invisible |
docs/agent/reports/READINESS_REVIEW_0831.md:104:| `OptionsMenuFixPack` is the only opt probe that NEEDS the fix pack loaded (SKIPs otherwise) | `60_Probes_Opt.lua:987` | correct; recorded so nobody reads its SKIP as a defect |
docs/agent/reports/READINESS_REVIEW_0831.md:106:⇒ Owner decision **83** (fix pack checklist): authorise the kit edits. None was made
docs/agent/reports/READINESS_REVIEW_0831.md:111:1. Walk the restore checklist — fix pack `reports/PARKED_OPTIN_REFERENCES.md`
docs/agent/reports/READINESS_REVIEW_0831.md:112:   (~46 passages; the fix pack's `metadata.lua` change = its version bump).
docs/agent/reports/READINESS_REVIEW_0831.md:117:4. Both-configuration ship test (with the fix pack, and with it absent) —
docs/agent/reports/READINESS_REVIEW_0831.md:118:   `FIX_POLICY` §8; note which fix pack version it was tested beside.
docs/agent/reports/READINESS_REVIEW_0831.md:121:## 7 · Owner decisions raised (mirrored on the fix pack's checklist, R10)
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:13:rule). The fix pack keeps the measurement records (`C47.md`, `C48.md`) and
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:20:Compressed from the fix pack's `agent/bugs/C47.md` + `C48.md`; every number
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:30:**The template half (`C47`)**: Open Farm is the only template of 287 that
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:33:but NOT the driver — the buffer only matters because of what follows. C47's
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:34:one open thread — the owner's 1x-vs-speed observation — stays in the fix pack
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:37:**The mechanism (`C48`), characterized by elimination — four experiments, the
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:73:**Facts corrected/established along the way** (filed as fix pack `EF-058/059/
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:83:owner's words and the record's verdict. No fix-pack repair exists or will.
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:93:"just size the buffer" shape (fix pack `C47.md` shape 1). OWNER, 2026-08-16:**
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:103:storage problem's clothes.** The same ruling retired the fix pack's "don't fix
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:104:C47 while C48 is open" caution: a buffer that cannot fill cannot mask anything.
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:147:`C47FARM` only (fix pack `EF-056` autosave pre-copy ritual), predictions
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:149:sources live in the fix pack's `docs/agent/prompts/c48-brake/` +
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:152:instances** (fix pack `EF-058`).
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:154:## 3. What the fix pack keeps
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:156:`C47.md` (the buffer/cadence record + the owner's open speed question and its
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:157:designed descending-ladder control) · `C48.md` (the full measurement record) ·
docs/agent/reports/SEED_LOGISTICS_HANDOFF.md:159:tests no fix). ⛔ No fix-pack code for this family, ever, per the two rulings.
docs/agent/STATE.md:9:- BUILT 2026-08-12, VERIFIED IN GAME the same evening: `8/8` beside the fix pack; `8/8` with it
docs/agent/STATE.md:10:  UNINSTALLED; fix pack `74/74` with this mod absent. Audit CLOSED 08-12, everything SUSTAINED.
docs/agent/STATE.md:12:  `SMRFixPack_` bytes; write→save→reload broke 0 of 3 fields (`archive/SESSION_LOG.md`, 08-12).
docs/agent/STATE.md:13:- ⛔ NOT PUBLISHED. 2026-08-17 (owner): the fix pack launched ALONE ("its not ready imo");
docs/agent/STATE.md:14:  every player-facing reference to this mod was PARKED (fix pack `reports/PARKED_OPTIN_REFERENCES.md`).
docs/agent/STATE.md:15:- 2026-08-31 READINESS PASS: tooling/process parity with the fix pack @ `bec2e06` restored.
docs/agent/STATE.md:18:  1. walk the restore checklist — ~46 parked passages across the fix pack repo + `SMR-CommunityMods`;
docs/agent/STATE.md:19:     the fix pack's `metadata.lua` change = its version bump + re-upload; re-measure, doccheck, `mkdocs --strict`;
docs/agent/STATE.md:24:  4. both-configuration ship test — with the fix pack and with it absent (`FIX_POLICY` §8), naming the version;
docs/agent/STATE.md:39:Gate MEASURED `8/8` beside the fix pack, `1/8` at fresh defaults (owner's 08-12 18:30 log — the only recording).
docs/agent/STATE.md:42:- ⛔ PERSISTED NAMES ARE SAVE CONTRACT — the five `SMRFixPack_*` fields/modifier ids keep their bytes
docs/agent/STATE.md:44:- ⛔ ZERO `SMRFixPack` references in executable code: the surviving tokens in `Code/` are the five
docs/agent/STATE.md:50:  fix pack `prompts/DRONE_PROJECT_PROMPT.md` §3 — the design decision is the owner's next call.
docs/agent/STATE.md:57:- ✅ Remote PUBLIC 08-13 (`github.com/catt144/SMR-CommunityOptInPack`); title "Relaunched Fix Pack:
docs/agent/STATE.md:61:- ⭐ 08-20 (owner, checklist 37 Q1): the fix pack's two `00_Core.lua` repairs (`2f077e8`) MIRRORED —
docs/agent/STATE.md:65:- ⚖️ 08-31 WRAP CHECK (F107 rule, `FIX_POLICY` §2): 3 pre-rule sites allowlisted with Src citations —
docs/agent/STATE.md:72:  adjudication inherited (fix pack `reports/L8_ADVERSARIAL_MAP.md`); not a launch blocker there.
docs/agent/STATE.md:74:  `98_EnablePathLeg` hardcodes the fix pack's id; `FixtureCarry` blind to D09's modifiers;
docs/agent/STATE.md:76:- ⛔ 08-31 FACTS: re-synced from the fix pack @ `bec2e06` (68 files); this repo's old `EF-057`/`EF-058`
docs/agent/WORKFLOW.md:5:> Copied from `SMR-BugFixPack/docs/agent/WORKFLOW.md` @ `33d69f5` on 2026-08-12
docs/agent/WORKFLOW.md:17:> 2. **The namespace** — `SMRFixPack.*` → `SMROptInPack.*` throughout. ⛔ NOT
docs/agent/WORKFLOW.md:18:>    the persisted `SMRFixPack_*` field names (`agent/PROVENANCE.md` §2).
docs/agent/WORKFLOW.md:25:> Where a clause says "the pack", read "this mod" — except where it names the
docs/agent/WORKFLOW.md:26:> Relaunched Fix Pack (pre-2026-08-17 records: "Community Fix Pack") explicitly,
docs/agent/WORKFLOW.md:41:   ⚠️ **This folder is a COPY of the fix pack's, taken 2026-08-12** and the two
docs/agent/WORKFLOW.md:49:   the fix pack @ `bec2e06` (this repo's two became `EF-061`/`EF-062`, their
docs/agent/WORKFLOW.md:50:   donor ids). From now on: a fact learned HERE is filed in the fix pack FIRST
docs/agent/WORKFLOW.md:61:5. ⚠️ **`C:\Dev\SMR-BugFixPack\docs\PLAYTEST_CHECKLIST.md`** — the owner's live
docs/agent/WORKFLOW.md:114:   2026-08-18, fix-pack checklist 42, carried here 2026-08-31; the 2026-08-03
docs/agent/WORKFLOW.md:131:  what you commit, the same as the fix pack.
docs/agent/WORKFLOW.md:132:- **Companion mod, a separate product:** `C:\Dev\SMR-BugFixPack` (Relaunched Fix
docs/agent/WORKFLOW.md:133:  Pack, remote `github.com/catt144/SMR-CommunityFixPack`). Shares no files with
docs/agent/WORKFLOW.md:144:  fix pack has its own junction (`SMR-BugFixPack`) beside it.
docs/agent/WORKFLOW.md:146:  budget, load order, the F107 wrap check), the release gates
docs/agent/WORKFLOW.md:152:- **Companion TestKit** (never shipped): `C:\Dev\SMR-BugFixPack-TestKit`
docs/agent/WORKFLOW.md:166:Then enable "Relaunched Fix Pack: Opt-In Modules" in the game's Mod Manager (the
docs/agent/WORKFLOW.md:175:(active / inactive+reason / disabled / error). The fix pack's own
docs/agent/WORKFLOW.md:176:`SMRFixPack.ListFixes()` still exists in ITS env when it is installed — two
docs/agent/WORKFLOW.md:177:registries, two log prefixes (`[CommunityOptInPack]` vs `[CommunityFixPack]`).
docs/agent/WORKFLOW.md:221:grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/
docs/agent/WORKFLOW.md:242:4. Both repos are in scope (the pack AND the TestKit) — the
docs/agent/WORKFLOW.md:308:  flagged dome was *required* to receive, so it could not fail; F11's `nil`
docs/agent/WORKFLOW.md:313:  selection half by reconstructing the pool and reading it (F11's
docs/agent/WORKFLOW.md:317:  compute its expectation with the fix's own logic** (adopted in the fix pack
docs/agent/WORKFLOW.md:320:  patched cannot fail on a broken dispatch (the fix pack's F33 probe printed
docs/agent/WORKFLOW.md:323:  (its C50 probe). So: dispatch through the production route (an
docs/agent/WORKFLOW.md:332:  count** (adopted 2026-08-04, co-run #1 correction C10). "Absence under N
docs/agent/WORKFLOW.md:352:4. Save with mod enabled → **disable the pack in the MOD MANAGER** → load: game
docs/agent/WORKFLOW.md:358:   98 errors/session with its own toggle OFF; that is how F86 Site 2 was found.
docs/agent/WORKFLOW.md:451:> ⭐ **THIS REPO'S TWIN of the fix pack's clause, installed at the split**
docs/agent/WORKFLOW.md:453:> `[CommunityFixPack]` line in one of THIS mod's legs is expected background,
docs/agent/WORKFLOW.md:464:1. **The baseline rig configuration is BOTH mods enabled** — the fix pack AND
docs/agent/WORKFLOW.md:466:   BASELINE (cell a2, 2026-08-12, audit-recounted from the fix pack's
docs/agent/WORKFLOW.md:467:   `archive/spa2_Mars.exe-20260812-18.44.24.log`): `fix pack present: 74/74` ·
docs/agent/WORKFLOW.md:469:   2026-08-13 (fix pack `archive/rs_r0_*`): `78 PASS / 0 FAIL / 16 SKIP /
docs/agent/WORKFLOW.md:473:   load order `1:SMR_CommunityFixPackTestKit 2:SMR_CommunityFixPack
docs/agent/WORKFLOW.md:475:   OUTERMOST).** Every "the pack" claim names WHICH pack. A fix-pack line
docs/agent/WORKFLOW.md:543:  2026-08-05 lead the owner scored as a miss on its own target banked `F101`
docs/agent/WORKFLOW.md:544:  and both F99 samples, and earlier leads produced the F02 watchdog challenge
docs/agent/WORKFLOW.md:565:   five minutes to observe it (the F11-conversion watch, staged fixtures);
docs/agent/WORKFLOW.md:569:   (C41's vanishing picker is the poster child);
docs/agent/WORKFLOW.md:588:- ⛔ **The forced-vs-organic rule (the F99 lesson):** forcing an *upstream
docs/agent/WORKFLOW.md:598:  inline one-liner through PowerShell** (co-run #1, correction C11: an inline
docs/agent/WORKFLOW.md:602:  ⚠️ **C11 corollary (unattended-1, I2): a script file is not enough if its
docs/agent/WORKFLOW.md:739:     clean log of the pack RUNNING was not banked as a clean uninstall.
docs/agent/WORKFLOW.md:745:     exactly that — `corun-batch-2`'s leg T had disabled the pack the day
docs/agent/WORKFLOW.md:755:     `SMROptInPack_Disabled` console veto covers only D12/F97-class modules —
docs/agent/WORKFLOW.md:771:     produced F85's dead F9-rebind advice: this chain's brief and payload menu
docs/agent/WORKFLOW.md:774:     F07 entry). A source-derived instruction is a claim; the brief says so.
docs/agent/WORKFLOW.md:777:     sitting archived one of four owner quotes (F85's); the other three exist
docs/agent/WORKFLOW.md:822:  `LoadGame` brought it back live with the pack still reading 81/81 — a full
docs/agent/WORKFLOW.md:922:## Release marking — tags, not branches (adopted in the fix pack 2026-08-17, carried 2026-08-31)
docs/agent/WORKFLOW.md:950:- The prefix is `optin-` (the fix pack's is `fixpack-`, the rescue's `rescue-`);
docs/agent/WORKFLOW.md:954:  and never by hand (the fix pack's H-02): every Mod Editor save runs
docs/agent/WORKFLOW.md:956:- Record portal version → commit sha on the fix pack's ④ sheet
docs/agent/WORKFLOW.md:957:  (`SMR-BugFixPack/docs/agent/reports/RELEASE_PORTAL_PREP.md`) in the same pass.
docs/agent/WORKFLOW.md:989:>    without the Relaunched Fix Pack.
docs/agent/WORKFLOW.md:1000:> 5. **⛔ ADD:** ship-testing is TWO configurations, not one — with the fix pack
docs/agent/WORKFLOW.md:1009:>    no `image` field and no `preview.png` (the fix pack's is
docs/agent/WORKFLOW.md:1014:>    checklist in the fix pack's `reports/PARKED_OPTIN_REFERENCES.md` (~46
docs/agent/WORKFLOW.md:1025:  2026-08-04: F55, F40, F73(b), F70, F97 presented as design-judgment repairs,
docs/agent/WORKFLOW.md:1160:- "Put the mod back" as advice for a damaged save, and its F88 caveat —
docs/agent/WORKFLOW.md:1161:  `agent/bugs/` F88 entry.
docs/agent/WORKFLOW.md:1169:  2026-08-01 but **written conditionally and marked do-not-publish until F86
docs/FUTURE_IDEAS.md:8:owner decision on the fix pack's `docs/PLAYTEST_CHECKLIST.md`.
docs/FUTURE_IDEAS.md:12:future ideas doc … want [the fix pack's] folder reserved for only bug related
docs/FUTURE_IDEAS.md:13:items."* The six entries below moved here whole from the fix pack's
docs/FUTURE_IDEAS.md:15:only bug-related parking. **The fix pack file's HARD RULE travels with them
docs/FUTURE_IDEAS.md:22:# Parked items (all moved 2026-08-14 from the fix pack's FUTURE_IDEAS.md)
docs/FUTURE_IDEAS.md:129:string cannot be replaced** — re-using its id discards the replacement (**F98**,
docs/FUTURE_IDEAS.md:133:is our own `ModItemLocTable` — the F84/D10 work already parked to post-release.
docs/FUTURE_IDEAS.md:135:**Where the material lives.** F98 and F84 entries in the FIX PACK's
docs/FUTURE_IDEAS.md:136:`agent/bugs/` (that half of the material stays fix-pack-side); the append route
docs/FUTURE_IDEAS.md:138:light-userdata form, shipped precedent `Workplace.lua:293`) is recorded on F98.
docs/FUTURE_IDEAS.md:173:**Where the material lives.** `F101.md` (`wontfix`) in the FIX PACK's
docs/FUTURE_IDEAS.md:184:**To un-park.** Launch first, then an explicit owner decision. F101 stays
docs/FUTURE_IDEAS.md:185:`wontfix` in the fix pack either way — the fix pack never grows a cheat surface.
docs/FUTURE_IDEAS.md:189:## 6. D01 export half — standing PreciousMetals demand (+ F56 auto-offload)
docs/FUTURE_IDEAS.md:195:dialog. It also **owns F56** (auto RC Transports never offload into rockets),
docs/FUTURE_IDEAS.md:199:**What it relates to.** `Opt_ClassicRockets` (this repo); F56 (fix pack
docs/FUTURE_IDEAS.md:201:F50/F68/F70/F71.
docs/FUTURE_IDEAS.md:209:thresholds). *(In the fix pack file this sat under "proposed for parking,
docs/FUTURE_IDEAS.md:224:**What.** Two complementary drone-judgment options born out of the fix pack's
docs/FUTURE_IDEAS.md:225:`C47`/`C48` farm investigation: **(I) a seeds-only cargo top-up** — after a
docs/FUTURE_IDEAS.md:232:⚖️ **Why it is parked HERE and may never touch the fix pack — owner ruling
docs/FUTURE_IDEAS.md:243:**Where the material lives.** That report section; fix pack `agent/bugs/C47.md`
docs/FUTURE_IDEAS.md:244:+ `C48.md` (the measurements); this repo's `D02.md` (the flapping boundary from
docs/FUTURE_IDEAS.md:248:also hangs on the fix pack's brake-intervention leg — if that refutes the
docs/FUTURE_IDEAS.md:252:and fix pack `agent/bugs/C48.md`).
docs/FUTURE_IDEAS.md:297:  precisely why this is not a fix-pack item.
docs/FUTURE_IDEAS.md:314:cannot enter the fix pack. Severity is feel, not function — the law is
docs/FUTURE_IDEAS.md:322:fix pack as `EF-061`/`EF-062` — amend both or neither. This entry keeps only
docs/FUTURE_IDEAS.md:339:**What.** A player-facing on/off switch per fix in the **fix pack** (not this
docs/FUTURE_IDEAS.md:341:listing the modules with checkboxes. Parked HERE and not in the fix pack's own
docs/FUTURE_IDEAS.md:349:- the `SMRFixPack_Disabled` veto is read at mod load (`00_Core.lua:384-388`),
docs/FUTURE_IDEAS.md:354:- ⛔ the fix pack has **no Mod Options page at all**, and the reason matters:
docs/FUTURE_IDEAS.md:358:⇒ The argument gets stronger as the pack grows: 75 modules today, and the
docs/FUTURE_IDEAS.md:391:of diagnosing a fix-pack field report (`SMR-BugFixPack` `agent/bugs/F104.md`,
docs/FUTURE_IDEAS.md:456:   landed on us. See `EF-065` in the fix pack.
docs/FUTURE_IDEAS.md:498:Fix pack `docs/agent/bugs/F104.md` (full derivation, the live stack capture, the
docs/FUTURE_IDEAS.md:500:Fix pack `docs/agent/facts/EF-065.md` (why the wrong mod gets named).
docs/FUTURE_IDEAS.md:508:read is an inference. ⚖️ **Fix pack ruling 2026-08-23 (owner):** naming the mod
docs/README.md:4:`SMR-BugFixPack`'s tree so one set of habits serves both repos. **Human docs at
docs/README.md:31:`C:\Dev\SMR-BugFixPack\docs\`** and are NOT duplicated here.
docs/README.md:51:`_preamble.md`, **copied whole from the fix pack @ `33d69f5` on 2026-08-12 and
docs/README.md:55:fix pack** (`agent/WORKFLOW.md`, reading path 2): file a new fact there first,
metadata.lua:5:	-- ⭐ FAMILY RENAMED (owner, 2026-08-17, fix-pack checklist 36): "Community
metadata.lua:6:	-- Fix Pack" → "Relaunched Fix Pack" across the whole set, before any upload;
metadata.lua:11:	-- description draft in the fix-pack repo's STORE_METADATA_STRINGS.md
metadata.lua:13:	'title', "Relaunched Fix Pack: Opt-In Modules",
metadata.lua:14:	'description', "Eight opt-in modules for Surviving Mars: Relaunched — every one of them off, or at its vanilla base setting, until you turn it on in Options → Mod Options. Rockets that keep requesting fuel while parked, acknowledged \"not working\" warnings, a per-Dome \"closed to new residents\" policy, more than one Artificial Sun, a closest-hub-first Drone dispatch overhaul (experimental), automatic cohort housing for Seniors and Children, a Nursery/Retirement Dome policy, and two Drone stat dials (speed, carry capacity). Nothing is patched on disk: the mod wraps the game's own Lua at runtime, and a module you leave off behaves exactly like the unmodded game. Works with or without the Relaunched Fix Pack. ⚠️ Set both Drone dials back to base and then save before uninstalling — setting them to base clears the boost from the colony you are playing, and saving is what clears it from the file.",
metadata.lua:15:	'short_description', "Eight opt-in gameplay modules, all off or at base until you enable them in Mod Options. Applied at runtime, no game files modified. Works with or without the Relaunched Fix Pack.",
metadata.lua:16:	-- Split out of the Community Fix Pack on 2026-08-12: these eight modules
metadata.lua:19:	'last_changes', "Initial release: the eight optional modules, split out of the Relaunched Fix Pack into their own mod.",
metadata.lua:39:	-- ⭐ THREE PATTERNS ADDED 2026-08-14 AT LAUNCH PREP (fix-pack chain
metadata.lua:46:	-- ⚠️ `LICENSE` is NOT excluded, deliberately — see the fix pack's note.
metadata.lua:82:	-- relative order they had in the fix pack: CohortHousing before NoHomeless
items.lua:2:-- (Options → Mod Options → Relaunched Fix Pack: Opt-In Modules). Moved here from the
items.lua:3:-- Community Fix Pack on 2026-08-12 with the split; the entries below are
README.md:1:# Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched
README.md:9:**It works with or without the Relaunched Fix Pack.** The two mods are separate
CLAUDE.md:1:# Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched
CLAUDE.md:3:✅ **Display name DECIDED (owner, 2026-08-13): "Community Fix Pack: Opt-In
CLAUDE.md:6:fix-pack checklist 36): now "Relaunched Fix Pack: Opt-In Modules"** — live
CLAUDE.md:16:**TRUE STANDALONE** — it works with the Relaunched Fix Pack installed, and
CLAUDE.md:20:> **Split out of `SMR-BugFixPack` @ `33d69f5` on 2026-08-12** (chain
CLAUDE.md:23:> and what was adapted. Pre-split records in the fix pack cite `Code/Opt_*.lua`
CLAUDE.md:24:> paths in THAT repo and the `SMRFixPack` namespace; translate mentally, do not
CLAUDE.md:30:   savegame keeps its EXACT bytes — including every `SMRFixPack_*` field and
CLAUDE.md:34:2. **ZERO `SMRFixPack` references in executable code.** The framework is this
.claude/settings.json:6:      "PowerShell(git -C C:\\Dev\\SMR-BugFixPack worktree list)",
.claude/settings.json:7:      "PowerShell(git -C C:\\Dev\\SMR-BugFixPack branch -a)",
.claude/settings.json:8:      "PowerShell(git -C C:\\Dev\\SMR-BugFixPack-TestKit worktree list)",
.claude/settings.json:9:      "PowerShell(git -C C:\\Dev\\SMR-BugFixPack-TestKit branch -a)"
```
