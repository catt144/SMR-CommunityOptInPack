# PROVENANCE — what came from where, and what may never change

This repo was **split out of `SMR-BugFixPack` on 2026-08-12** by the chain
`docs/agent/prompts/split-optins/` (prompt 3, the build). Nothing here was
written from scratch except this page, `STATE.md`, `docs/README.md`,
`CLAUDE.md`, the mod-facing `README.md` and `metadata.lua`/`items.lua`.

**Source shas, pinned at the port:**

| repo | path | sha at port | remote |
|---|---|---|---|
| Community Fix Pack | `C:\Dev\SMR-BugFixPack` | `33d69f5d8412a3924a53b93de38f00f1c23e3866` | `github.com/catt144/SMR-CommunityFixPack` |
| TestKit (shared, never shipped) | `C:\Dev\SMR-BugFixPack-TestKit` | `d8e1fbf56c4a7be4913fbdc34f2bc9b96b7c07c5` | none — local only by decision |

⚠️ **Both shas are pre-split HEADs.** The commits that PERFORMED the split land
after them in the fix pack's history; `git log --oneline` there, around
2026-08-12, is the other half of this record.

---

## 1. The port ledger

`VERBATIM` = byte-identical copy. `ADAPTED` = copied, then the listed edits.

| artifact here | from | how | what changed |
|---|---|---|---|
| `Code/00_Core.lua` | `Code/00_Core.lua` | ADAPTED | whole-file token rename `SMRFixPack` → `SMROptInPack` (which also carries `_Disabled`/`_Optional`), then five literal adaptations: log prefix `:27`, mod id `:64` + `:401`, dialog title/body `:512-514`, and the veto-log line `:412`. ⛔ The rename is the WHOLE file, not a listed subset — `:270` (`rawget(_G,"SMRFixPack_Disabled")`) and `:384` (the bare global) would crash every `Register` with the fix pack absent if they were left alone |
| `Code/Opt_*.lua` ×8 | same names | ADAPTED | the same token rename, plus: `Opt_DroneOverhaul`'s CLONED logger prefix (its own `[CommunityFixPack]` literal, not Core's), the two infopanel rollover titles that name the mod (`Opt_ResidencyControl`, `Opt_NoHomeless`), `Opt_DroneStatDials`' `ApplyModOptions` mod-id guard, and the eight header comments pointing at the Mod Options page. **No behaviour edit of any kind** |
| `docs/agent/facts/` (53 + `INDEX.md` + `_preamble.md`) | same | VERBATIM | whole-folder copy; `_preamble.md` gained the dated copy note. **EF-054 (inter-mod load order) was written in the same session and exists identically in BOTH repos** |
| `docs/agent/bugs/D01…D07, D09, D12` | same names | ADAPTED | bodies byte-preserved; front matter renumbered (`seq`/`row` 1..9 here) with the donor's numbers kept as `donor_seq`/`donor_row`. The fix pack keeps a TOMBSTONE entry at each id pointing here |
| `docs/agent/FIX_POLICY.md` | same | ADAPTED | §4 inverted for a mod whose product IS opinionated modules — the fix pack's §4 is kept quoted in full as §4-donor, because it is the reason these modules were `Opt_` in the first place. Everything else stands, with `SMRFixPack.*` → `SMROptInPack.*` |
| `docs/agent/WORKFLOW.md` | same | ADAPTED | all harness stacks kept verbatim (probe hygiene, ARM gate, log-review rule, cheats rule, co-run protocol, prompt-authoring rules); Layout/Install re-pointed at this repo and its junction; release steps marked N/A-or-adapted in place; the BOTH-MODS-LOADED clause installed as this repo's twin |
| `docs/agent/reports/CHAIN_METHOD.md` | same | VERBATIM | method, not content |
| `docs/agent/reports/DRONE_OVERHAUL_OPTIONS.md` | same | VERBATIM (moved) | D06/D09's design study; the fix pack keeps a one-line pointer |
| `tools/doccheck.py` | same | ADAPTED | four differences, all recorded in its own v4 docstring: the `SMROptInPack.Register(` needle; the optional/default-active arithmetic repair; the three MOVED stubs dropped (not faked); the probe count labelled SHARED |
| `tools/split_bugs.py` | same | ADAPTED | index-header prose only (this repo never held a `docs/BUGS.md`). The migration half is N/A and kept, so one parser defines the entry format in both repos |
| `tools/split_facts.py` | same | ADAPTED | docstring N/A note only — its `render_index` must keep reproducing the copied facts `INDEX.md` byte-for-byte |
| `tools/blocking_analysis.py` | same | VERBATIM | `Opt_DroneOverhaul`'s F86 Tier-2 record depends on its verdict staying re-runnable |
| `tools/hooks/pre-commit` | same | VERBATIM | enable once: `git config core.hooksPath tools/hooks` |
| `LICENSE`, `.gitignore`, `.gitattributes` | same | VERBATIM | — |

**Deliberately NOT copied:** `docs/archive/` (append-only; history stays where
it happened), `docs/PLAYTEST_CHECKLIST.md` + `docs/PLAYTEST_HELP.md` (single-
sourced in the fix pack by design — `docs/README.md` says why), the 73 `Fix_*`
modules and `90_SaveSanitizer.lua`, and the fix pack's `docs/BUGS.md` /
`docs/STATUS.md` / `docs/agent/ENGINE_FACTS.md` MOVED stubs (this repo has no
pre-restructure history to resolve).

---

## 2. ⛔ The persisted-name inventory — SAVE CONTRACT, verbatim

**Every string below has entered savegames or account storage. It keeps its
EXACT bytes forever, `SMRFixPack_` prefix and all.** They were written by these
modules while they lived in the fix pack; a rename would orphan live state in
every existing save (a policy row silently resetting, a drone boost stranded
under an id nothing removes). Renaming one is FORBIDDEN in this repo without a
migration heal, which is not built and is out of scope here.

| # | exact bytes | kind | written at | read at |
|---|---|---|---|---|
| 1 | `SMRFixPack_ack_notworking` | field on `Building` objects | `Opt_AcknowledgedWarnings.lua` (`obj[FLAG] = true`), cleared on recovery | same file |
| 2 | `SMRFixPack_closed_to_new_residents` | field on `Dome`/`MicroGHabitatBase` | `Opt_ResidencyControl.lua` via `building:TogglePolicy(FLAG, broadcast)` → shipped `Community:SetPolicyState` | same file |
| 3 | `SMRFixPack_no_homeless` | field on `Dome`/`MicroGHabitatBase` | `Opt_NoHomeless.lua` (`TogglePolicy`, and its bespoke `SetPolicyState` broadcast) | same file |
| 4 | `SMRFixPack_DroneSpeedDial` | **label-modifier id** in `UIColony.label_modifiers["Drone"]`, holding a vanilla `Modifier` object | `Opt_DroneStatDials.lua` | same id (replace/remove) |
| 5 | `SMRFixPack_DroneCarryDial` | as above, label `Consts` | `Opt_DroneStatDials.lua` | same |
| 6 | `"1x (base)"` `"2x"` `"3x"` `"5x"` | dial choice values | `metadata.lua` `default_options`, `items.lua` `ChoiceList`, the module's own map | the module's decode map |
| 7 | `"+0 (base)"` `"+1"` `"+2"` | as above | as above | as above |
| 8 | `ClassicRockets` `AcknowledgedWarnings` `ResidencyControl` `MultipleSuns` `DroneOverhaul` `CohortHousing` `NoHomeless` | Mod-Options toggle keys **and** `Register` ids | `metadata.lua`, `items.lua`, each module's `Register` | `SMROptInPack.OptionEnabled` |
| 9 | `DroneSpeedDial` `DroneCarryDial` | Mod-Options choice keys (**not** `Register` ids) | `metadata.lua`, `items.lua` | the module, directly |

Rows 6–9 are keyed under the **mod id**, and the mod id DID change
(`SMR_CommunityFixPack` → `SMR_CommunityOptInPack`), so the player's saved
values do not carry across: every toggle comes up OFF and both dials at base
once, and the owner re-ticks their preferences in one visit to Mod Options.
Rows 6–9 keep their bytes anyway — every doc, probe and console line names
them, and there is nothing to buy by churning them.

**Provably never persisted, so the rename was safe:** `SMRFixPack_Optional` /
`SMRFixPack_Disabled` (now `SMROptInPack_*`) — plain `_G` tables built with
`rawget(_G,…) or {}` at load, never written onto an object, never in
`PersistableGlobals`. `Opt_DroneOverhaul`'s caches (module locals, weak keys).
`Opt_MultipleSuns`' file locals and its `build_once` preset write (presets are
rebuilt from data every load). The `rawset(self, "ProcessToggle", …)` in both
UI rows (an `InfopanelActiveSection` **window** instance, not a game object).
**No named threads. No GameVars.**

⛔ **2026-09-17 — THREE OF THESE NAMES NOW BELONG TO MODULES THAT NO LONGER SHIP,
AND NOT ONE ROW LEAVES THIS TABLE.** The owner retired `Opt_DroneOverhaul` (D06,
PARKED), `Opt_CohortHousing` (D07, DEAD) and `Opt_NoHomeless` (D12, DEAD); the files,
their `items.lua` entries and their `metadata.lua` keys are deleted. The strings are
**save contract and history**, and deleting a row would teach the next session that a
name is renameable once its writer is gone. It is not. Specifically:

- **Row 3, `SMRFixPack_no_homeless`, is a REAL FIELD already written onto `Dome` /
  `MicroGHabitatBase` objects** in every save where the policy was switched on. This mod
  is UNPUBLISHED, so the only such saves are the owner's own test saves; the fix pack's
  Save Rescue (its `D13`) already targets these keys. With the module gone nothing reads
  the field, so the residue is **inert** — stated, not assumed
  (`reports/MODULE_REVALIDATION_1_1_0.md` §10.2).
- **Row 8** still lists `DroneOverhaul`, `CohortHousing` and `NoHomeless` as Mod-Options
  toggle keys and `Register` ids. Their keys linger in `AccountStorage.ModOptions` and are
  **read by nothing** — the engine never clears a removed key and the UI does not render
  it, so no crash and no reset of the player's other toggles (§10.1 of the same report;
  it wants an `EF-` fact, which the FIX PACK allocates).
- Rows 1, 2, 4, 5 belong to modules that still ship. Nothing else changed.

Code for the three: ⛔ **git is the record** — restore sha **`cc846e4`**.

⚠️ `Opt_MultipleSuns` DOES leave persisted state on `SolarPanelBase` objects —
the **vanilla** `artificial_sun` member, written through the shipped
`SetArtificialSun` with a vanilla value. Not ours, not renameable, not our
footprint. Its header's "Savegame footprint: none" means "no NEW names".

---

## 3. Placeholder sites — ✅ the display name is DECIDED and SWEPT

✅ **DECIDED (owner, 2026-08-13): `"Community Fix Pack: Opt-In Modules"`** —
family-prefixed so the two mods sort together in mod lists, which also serves
the Paradox-Mods discoverability observation (keyword search broken there;
shared naming lets the fix pack surface its sibling). **Swept the same day, one
pass, every site below (15 occurrences, 11 files), parse sweep GREEN.** The
mod id / global / log tag are unchanged (code + save contract). Historical
table — the working title `"Community Opt-In Pack"` occupied these sites from
the 2026-08-12 split until the sweep:

| site | string |
|---|---|
| `metadata.lua` | `'title'`, `'description'`, `'short_description'`, `'last_changes'` |
| `Code/00_Core.lua` C1 dialog | `Untranslated("Community Opt-In Pack")` + the dialog body's "…check for a new version of the Community Opt-In Pack" |
| `Code/Opt_ResidencyControl.lua` | rollover title `"Residency Policy (Community Opt-In Pack)"` |
| `Code/Opt_NoHomeless.lua` | rollover title `"Dedicated Dome Policy (Community Opt-In Pack)"` |
| all 8 modules' headers | the comment `Options → Mod Options → Community Opt-In Pack` |
| `README.md`, `CLAUDE.md`, `docs/` | prose |

✅ **The GitHub remote is DECIDED and LIVE (owner, 2026-08-13): PUBLIC**, at
`github.com/catt144/SMR-CommunityOptInPack`, matching the fix pack's setup. All
6 commits pushed; `main` tracks `origin/main`. Still owner-owned and open: the
**store description** (launch prep). ~~The display name placeholders~~ —
decided and swept 2026-08-13, see above.

---

## 4. How to run the suite (rule 8: answerable from this repo alone)

The **TestKit is a separate, never-shipped local repo at
`C:\Dev\SMR-BugFixPack-TestKit`**, and ONE kit serves BOTH mods. It is not
duplicated here — a second kit would be a second set of probe verdicts to
reconcile.

* Install both mods as directory junctions under
  `%AppData%\Surviving Mars Relaunched\Mods\` (this repo's is
  `SMR-OptInPack`), plus the TestKit's own junction; enable them in the Mod
  Manager. Full recipe: `docs/agent/WORKFLOW.md` → "Install for testing".
* Probe hygiene is a HARD GATE before any testing —
  `docs/agent/WORKFLOW.md` → "Probe hygiene", including the parked-instrument
  rule, the ARM gate and the `PROBE SWEEP:` line every result commit carries.
* **This mod's registry surface in the kit** is `SMRTest.OptStatus(id)` /
  `SMRTest.OptMissing(id)` (the fix pack's is `FixStatus`/`FixMissing`), and
  `SMRTest.FromOptInPack(fn)` recognises source paths from this repo.
  ⛔ `OptMissing` returns **SKIP**, never FAIL, when the whole opt-in registry
  is absent — a mod that is legitimately not installed is not a failing suite.
* `SMRTest.RunAll()` prints **two** gate lines, one per mod:
  `fix pack present: %d/%d fixes active` and
  `opt-in pack present: %d/%d modules active`. ⛔ Grep logs with the FULL
  bracketed token (`[CommunityOptInPack]` / `[CommunityFixPack]`) — `Pack]`
  matches both.
* In-game console: `SMROptInPack.ListFixes()` prints every module's status.

---

## 5. What the fix pack kept, and what it lost

It lost the 8 `Opt_*.lua` files, their `items.lua` entries, its whole
`default_options` block (so it no longer appears in Options → Mod Options at
all) and the `code` rows that loaded them. It KEPT `00_Core.lua` unchanged —
the `optional` machinery in it is now dormant, not wrong, and it is the one file
every remaining fix depends on. Its own bug entries stay there; the nine that
moved here left tombstones behind.

---

## 8. The fourth port — 2026-09-17 tooling/process parity (donor @ `e6ec192`)

The fix pack spent the fortnight after 09-01 rebuilding how a session works there — skills, a rules
header on the entry file, a generated Codex mirror, a search boundary, and doccheck growing from
810 to 2,907 lines. ⛔ **None of that reasoning was re-opened here.** This port carried the
artifacts and adapted their paths, names and examples to this mod; where a donor rule cites a
fix-pack-only surface (its `PLAYTEST_CHECKLIST.md`, its `prompts/perma/` tree, its `support/`
folder) the row says what replaced it.

| artifact here | how | what changed / what it proves here |
|---|---|---|
| `.claude/skills/smr-orientation/` | ADAPTED | this mod's product description, the two bans, MODULE FREEZE, the 1.1.0 hazard, the `EF-`-ids-are-the-fix-pack's rule, and the split-checklist caveat replace the donor's equivalents |
| `.claude/skills/smr-bug-library/` | ADAPTED | `D`-entry counts and this repo's index sizes; the donor's `F`/`C` framing kept because both letters are still legal here |
| `.claude/skills/doc-editing/` | ADAPTED | donor text plus a section this repo needs and the donor does not: the persisted names, pre-split/pre-rename records and the archive are not rewritable by a doc edit |
| `.claude/skills/prompt-authoring/` | ADAPTED | donor text; `support/CHAIN_METHOD.md` → `reports/CHAIN_METHOD.md`, the both-configuration ship test and the both-toggle-directions rule added, the shared-TestKit caveat added |
| `.claude/skills/smr-session-close/` | ADAPTED | the routing table splits owner calls three ways (this mod → `DECISIONS_OWED.md`; the shared kit / `EF-` ids / fix-pack features → its checklist) |
| `.rgignore` | VERBATIM (one comment line changed) | the `docs/archive/` search boundary. Tested here: a default `rg` returns live hits only |
| `CLAUDE.md` | ADAPTED | donor's `Must_Read_Header` `<!-- RULES -->` block, rewritten for this repo's duties. ⛔ the donor's `[A3: pass]` audit tags were NOT copied — that audit ran on its text, not ours |
| `AGENTS.md` | NEW, GENERATED | byte copy of `CLAUDE.md`; `--regen` writes it, `check_agents_mirror` reds on drift |
| `tools/doccheck.py` `--regen` | NEW | the donor has had it since the split; this repo could detect index drift and not fix it. Writes `bugs/INDEX.md`, `facts/INDEX.md`, `AGENTS.md` |
| `tools/doccheck.py` `--emit-fingerprint` | ADAPTED | donor's function and `.acf` read verbatim; the sha row says "fix-pack shas" because facts are allocated there, so they do not resolve in this clone |
| `tools/doccheck.py` PUSH SET | ADAPTED | budget 24 KiB not 40 — this repo's push set is two files, not four (no `GENERAL_USE_PROMPT.md` here) |
| `docs/agent/facts/` | VERBATIM (re-sync) | 68 → **107** files @ donor `e6ec192`. Every shared fact gained `derived_at:`; 33 new, incl. the 1.1.0 facts (`EF-083`). ⛔ **`EF-062`'s `FUTURE_IDEAS` pointer is the ONLY local adaptation** — a re-sync is otherwise a straight overwrite |
| `docs/agent/prompts/perma/STATE_EVICTION.md` | ADAPTED | the donor's 2026-09-15 four-test admission door (harm · reach · gate · volatility) added to this repo's existing boundary section |
| `docs/agent/prompts/README.md` + `perma/` | ADAPTED | the donor's gated prompt map (reorganised there 2026-09-11): `perma/` vs root one-offs vs chain folders, declared classes, and the no-tombstones rule. Four prompts moved into `perma/`; the one live one-off gained the `_high` difficulty suffix `prompt-authoring` already mandated. ⛔ The donor's `ledger-exception` class and migration-allowance machinery were NOT carried — this repo has no such ledger and no debt, and a class nothing can legally declare is a trap |
| `tools/doccheck.py` PROMPT MAP + SKILLS gates | ADAPTED | both directions of the prompt map; skills mirrored byte-for-byte to `.agents/skills/`. ⛔ The donor's per-skill byte caps were NOT carried: it tore them down itself (its owner ruling 2026-09-14) because a skill body is PULL, and re-introducing them here would be an agent picking numbers the owner never set |
| `.claude/agents/doc-surgeon.md` | ADAPTED | the donor's mechanical-edit subagent; repo path swapped, and three rules added that the donor does not need — keep CRLF, never touch a persisted name, `docs/archive/` is append-only |
| `docs/agent/STATE.md` | APPLIED | the donor's ruling that counts are pulled, never stored, applied here: the stored BUILD STATE block (which had gone stale — 100 probes vs 97, "game pinned 1.0.7") is now a pull pointer |

**What was NOT ported, and why.** The donor's `docs/agent/support/` tree (its `CHAIN_METHOD.md`
lives in `reports/` here), its `prompts/perma/` split (this repo has five prompts, not a tree), its
`.claude/agents/doc-surgeon.md` and its `.claude/` working corpus (a live chain's scratch, not an
artifact), and the rest of its 2,097 new doccheck lines — most of which check surfaces this repo
does not have (its checklist's `opened:` dates, its STATE admission parser, its stub files).

## 7. The third port — 2026-09-12, one dangling citation closed (donor @ `85d95cb`)

Not a pass, a single repair. A knowledge inventory run in the fix pack found that
**five files in THIS repo cite `DRONE_PRIORITY_SYSTEM` by name and the file was not
here** — `agent/bugs/D06.md`, `agent/facts/EF-071.md`,
`agent/prompts/DRONE_REBUILD_BUILD.md`, `agent/reports/DRONE_REBUILD_DESIGN_20260901.md`
and `agent/reports/DRONE_BANDS_CLEAN_REVERT_20260901.md`. The D06 drone rebuild is
live work, so this was a live dependency gap, not historical residue.

| artifact here | how | what it proves here |
|---|---|---|
| `docs/agent/reports/DRONE_PRIORITY_SYSTEM.md` | **VERBATIM** | the vanilla drone task-priority breakdown (research 2026-07-31) that the D06 design and build docs cite by section. Byte-identical to the donor: md5 `58fc77176fa811fb3e057457a60e7fa8`, 30,544 B, 565 lines. Donor `SMR-BugFixPack` @ `85d95cb` |

⛔ The donor keeps its copy — the fix pack cites it too. Two byte-identical copies is
the intended state; if either is edited, re-sync rather than diverge.

## 6. The second port — 2026-08-31 readiness pass (donor @ `bec2e06`)

The fix pack kept building after the split; this pass carried across what it
grew, measured against THIS tree. Report: `agent/reports/READINESS_REVIEW_0831.md`.
Donor sha for every row: `SMR-BugFixPack` @ `bec2e06d` (v5 closed, 2026-08-30).

| artifact here | how | what changed / what it proves here |
|---|---|---|
| `tools/doccheck.py` (v5) | ADAPTED | four donor checks carried: STATE **byte** budget (9 KiB warn / 18 KiB hard / 200 B line), `tested-attended`/`-unattended` vocabulary, `LOAD_ORDER_RULES` (this repo's two shared-symbol orders), `wrap_targets_check`. `GENERAL_USE` cap kept, N/A |
| `tools/harvest_wrap_targets.py` | ADAPTED | `SMROptInPack.Require` needle; allowlist emptied then refilled with the 3 sites verified benign at Src 2026-08-31 (`Opt_DroneOverhaul` ×2, `Opt_MultipleSuns`) |
| `tools/upload_preflight.py`, `pack_list.py`, `flpk_extract.py`, `l7_env_map.py` | VERBATIM | generic; preflight FAILS here on the missing `image` (the launch gate) |
| `tools/pack_predict.py` | ADAPTED | `CONTENT_PREFIX` = this mod's id |
| `tools/l2_reload_sim.py` | REWRITTEN | the donor's is bound to four DataPatch fixtures (N/A: no `Opt_*` calls DataPatch); this one loads the whole `code` list twice and checks registration; `--core --expect-doubling` is its falsifier (pre-guard core `2cedf7d~1` REPRODUCES the 08-17 doubling) |
| `tools/l3_save_footprint.py` | ADAPTED | `NAMED_STATE` matches BOTH prefixes (persisted names keep `SMRFixPack_`), rows labelled by the token found; `REGISTER`/`resolved` renamed |
| `tools/l4_player_surfaces.py`, `l5_containment.py`, `l6_reachability.py`, `audit_preset_fields.py` | ADAPTED | token rename only; donor `Fix_*` citations in comments left as its history |
| `tools/l6_promise_map.py` | ADAPTED | token rename + `Opt_` added to the filename derivation; census 5 (site fix list) N/A while parked |
| `tools/l8_hostile_input.py` | ADAPTED | token rename; module trio = `Opt_ClassicRockets`, `Opt_DroneStatDials`, `Opt_NoHomeless`; control case vetoes `ClassicRockets` |
| `tools/l8_deference_map.py` | NOT PORTED | quarantined in the donor (TA-3) until repaired there |
| `docs/agent/reports/CHAIN_METHOD.md` | VERBATIM (re-sync) | method, not content — §5a and the commit-the-folder rule arrive |
| `docs/agent/facts/` | VERBATIM (re-sync) | 7 donor-updated shared facts taken whole (EF-008/023/039/051/054/055/056); EF-057…068 added; this repo's old EF-057/058 are now EF-061/062 (their donor ids). ⛔ ids are allocated by the fix pack from here on (`WORKFLOW.md` reading path 2) |
| `docs/agent/prompts/DISPATCH.md`, `STATE_EVICTION.md` | ADAPTED | this repo's paths, bans, route table; the playtest prompt stays single-sourced in the fix pack |
| `docs/agent/WORKFLOW.md`, `FIX_POLICY.md` | ADAPTED | rules carried, each marked with its donor date and this repo's state at adoption (listed in the report §4) |
| `.claude/settings.json` | ADAPTED | the donor's read-only git allowances, plus this repo's |

**Hardened the same evening (2026-08-31, after a second session hit it):** every
tool forces UTF-8 stdout (the Windows console is cp1252 and the tools print
⛔/⭐/§ — `l3` died on its own §7 line), the multi-line PORTED headers shrank to
one provenance line pointing here, docstrings and printed labels now say "this
mod" rather than "the pack", and `l3 --src` refuses a path with no `Lua/` under
it BEFORE printing (a wrong path had produced a silent all-absent census).

**Not carried, by decision:** the donor's sweep-chain folders and lens reports
(they are ITS evidence; this repo's lens sweep, if ever run, produces its own),
`GENERAL_USE_PROMPT.md` / `RELEASE*.md` / `POST_UPLOAD_CLOSE.md` /
`PUBLIC_SURFACE_SWEEP.md` / `SITE_AUDIT.md` (all bound to the fix pack's live
listing and site; this mod's launch session adapts them when it exists),
`UPLOAD_WORKFLOW.md` (owner file, single-sourced there like the playtest files).
