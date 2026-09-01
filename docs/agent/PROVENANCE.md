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

**Not carried, by decision:** the donor's sweep-chain folders and lens reports
(they are ITS evidence; this repo's lens sweep, if ever run, produces its own),
`GENERAL_USE_PROMPT.md` / `RELEASE*.md` / `POST_UPLOAD_CLOSE.md` /
`PUBLIC_SURFACE_SWEEP.md` / `SITE_AUDIT.md` (all bound to the fix pack's live
listing and site; this mod's launch session adapts them when it exists),
`UPLOAD_WORKFLOW.md` (owner file, single-sourced there like the playtest files).
