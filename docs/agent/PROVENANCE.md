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

## 3. Placeholder sites — the display name is an OWNER decision

`"Community Opt-In Pack"` is a working title. Every player-visible site
carrying it, to be swept in one pass at launch prep:

| site | string |
|---|---|
| `metadata.lua` | `'title'`, `'description'`, `'short_description'`, `'last_changes'` |
| `Code/00_Core.lua` C1 dialog | `Untranslated("Community Opt-In Pack")` + the dialog body's "…check for a new version of the Community Opt-In Pack" |
| `Code/Opt_ResidencyControl.lua` | rollover title `"Residency Policy (Community Opt-In Pack)"` |
| `Code/Opt_NoHomeless.lua` | rollover title `"Dedicated Dome Policy (Community Opt-In Pack)"` |
| all 8 modules' headers | the comment `Options → Mod Options → Community Opt-In Pack` |
| `README.md`, `CLAUDE.md`, `docs/` | prose |

Also owner-owned and still open: the **GitHub remote** (this is a LOCAL git repo
until the owner asks for one — never create a public remote unasked) and the
store description.

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
