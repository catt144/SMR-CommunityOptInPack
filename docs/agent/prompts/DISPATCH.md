# Dispatch — general-purpose orientation (model-agnostic) — written 2026-08-31

Adapted from the fix pack's `prompts/DISPATCH.md` (2026-08-29) for THIS repo.
Paste into a fresh Claude Code session for **ad-hoc work that is not a sitting**:
a code question, an investigation, a module check, a new finding, a new report, a
triage of something the owner noticed. **Any model; the owner picks per task.**
**Start with `git log --oneline -10` + `git pull`** — the tree moves and this
file, like every record, goes stale the moment another session commits.
Staleness anchor: **written 2026-08-31**; verify against `git log` before trusting
any specific it names.

> ⛔ **THIS IS AN ORIENTATION, NOT A LOGBOOK.** It carries no result, no status,
> no entry ID — those live in the entries, the checklist and `STATE.md`. The only
> edits it takes are corrections to its own instructions. A sitting's lesson goes
> to its proper home (see §3), never here.

> 🧭 **THIS IS THE CATCH-ALL. If the task has a dedicated prompt, SWITCH TO IT** —
> this one only orients and routes. The dedicated ones (§4): a **live playtest**,
> this mod's **launch**, a **multi-session effort**, a **STATE eviction**.
> Everything else — one question, one module, one report — is dispatch, and
> stays here.

You are doing focused, self-contained work in an **opt-in behaviour mod** for
Surviving Mars: Relaunched — eight modules that change how the game plays, each
OFF (or at base) until the player enables it in Options → Mod Options; patched at
runtime; a **true standalone** beside the Relaunched Fix Pack. The map is
`docs/README.md`; `CLAUDE.md` (auto-loaded) carries the two bans.

## 0 · Orient (before you touch anything)

1. `git log --oneline -10` + `git pull` — know what landed since this file's date.
2. **Read `docs/agent/STATE.md`** — the mandatory current-state kernel (gates,
   holds, counts, the launch obligation). Every session reads it.
3. Scan `docs/agent/bugs/INDEX.md` (the nine D-entries) and `docs/agent/facts/INDEX.md`
   — one-line rows, so you know what already exists (several engine behaviours are
   the opposite of what the code suggests). Open only the files the task touches.
4. ⚠️ **If — and only if — the task launches the retail game for a reading**, the
   STALE-PROBE GATE binds first: `grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/`,
   put it in your todo list, and CLEAN = zero hits (or every hit declared by this
   session's design). A pure investigation or a doc change launches nothing and
   skips this. The rig's NORMAL config is BOTH mods loaded (`WORKFLOW.md`).

## 1 · The bindings that never bend

- ⛔ **The two bans** (`CLAUDE.md`): persisted names are SAVE CONTRACT — every
  `SMRFixPack_*` field and modifier id this mod writes keeps its exact bytes
  (`agent/PROVENANCE.md` §2); and ZERO `SMRFixPack` references in executable
  code — the framework is this mod's own copy under `SMROptInPack`.
- **Never modify the game directory** (`A:\SteamLibrary\steamapps\common\Project
  Spark`). `ModTools\Src` is **read-only truth** for line numbers — cite it, never
  edit it. Check `Mars.exe` is NOT running (`tasklist`) before touching loadable
  code, in a separate step from the edit.
- **Any code you write is `FIX_POLICY.md`'s** — §4 what may be BUILT here (and
  §4-donor for why these modules are `Opt_`), §4a who-benefits, §3a save-safety,
  §2 enable-path / declaring-class / the F107 wrap rule / the F110 runtime-global
  rule, §1 fix-shape — and **judged by enumeration, never by an entry's own words.**
- ⛔ **Module freeze:** no behaviour change to any module without an owner ruling
  (`STATE.md`); `Opt_DroneOverhaul` carries the PT-52 freeze. A mechanical repair
  needs a re-verified A/B in the same commit.
- **Parse-sweep every Lua change** before you trust it: `python` + `luaparser`
  (`from luaparser import ast; ast.parse(open(f, encoding="utf-8-sig").read())`).
- **`python tools/doccheck.py` must be GREEN before any doc commit** (red blocks;
  set up once: `git config core.hooksPath tools/hooks`). It also enforces the
  STATE byte budget, `metadata.lua` load order and the F107 wrap check. Counts
  come from `doccheck.py --emit-counts`, **never hand-typed**.
- **Desk instruments before a launch:** `tools/l2_reload_sim.py --strict` (every
  module registers once across a ReloadLua), `tools/l8_hostile_input.py --strict`,
  `tools/l3_save_footprint.py --src <Src>` (the persisted-name census must still
  read exactly PROVENANCE §2's five names). Inventory: `agent/PROVENANCE.md` §6.
- **Commits:** `git commit -F <file>` (embedded quotes split under PS 5.1),
  project author config, then **push** — `WORKFLOW.md` "Layout": push what you
  commit, the same as the fix pack. ⛔ TestKit is local-only BY DESIGN.
- **Account state and counts: READ them, never assume** — the live
  `opt-in pack present: N/8 modules active` line and `SMROptInPack.ListFixes()`
  are the only valid reads.

## 2 · The judgment rules (the ones the project has been burned on)

- **Challenge the cause before filing.** The owner expects a *control*, not a
  plausible story; state the root cause only when a check pins it.
- **Recorded facts are claims too** — re-derive the ROUTE, not just the citations.
- **Never silently discount a log line.** "Not caused by our leg" is an attribution
  verdict, not a dismissal — report unexplained lines VERBATIM with their age.
  ⛔ Grep with the FULL bracketed token `[CommunityOptInPack]` — `Pack]` matches
  both mods.
- **"You can X" needs a route check** — verify a real user can walk the steps on
  each surface; a citation proving the mechanism exists is a different check.
- **Close cases completely.** "Refuted" requires the condition was SAMPLED, not
  that a count happened to be zero.
- **Design-flavoured calls go to the OWNER, not into an agent doc.** This mod's
  whole product is opinionated behaviour, so "should it do X?" is the owner's —
  route it to the fix pack's `docs/PLAYTEST_CHECKLIST.md` → "Decisions waiting on
  you" (single-sourced THERE, `docs/README.md` says why). Anything too big for
  the session gets FILED, never half-started. Ideas go to `docs/FUTURE_IDEAS.md`
  — a parking lot, NOT a backlog.

## 3 · Filing — where a result goes (`docs/README.md` "Where new things go")

- A **defect or module record** → `agent/bugs/<ID>.md` (`D##`). Derive the next id
  from the files (`seq = max(seq)+1`, `row = max(row)+1`), then **regenerate the
  INDEX** — GENERATED, never hand-edited: `split_bugs.load_from_dir()` +
  `render_index()` (mind the trailing newline), then `doccheck`.
- An **engine fact** → ⛔ numbered by the FIX PACK: file it there first (or reserve
  the next id there), mirror it here at the SAME id, regenerate the facts INDEX.
- A **report, plan, spec, audit, survey** → `agent/reports/`. Reports are NOT
  authority — when a report and an entry/fact disagree, the entry/fact wins.
- A **rule that binds future work** → `WORKFLOW.md` (process) or `FIX_POLICY.md`
  (code), never buried in a report.
- A **decision the owner must make** → the fix pack's checklist, never only here.
- A **session leg** → `archive/SESSION_LOG.md` (append-only, newest first).

## 4 · Route table — hand the task to its own prompt

| the task is really… | switch to |
|---|---|
| a LIVE playtest at the keyboard (both mods) | fix pack `prompts/GENERAL_USE_PROMPT.md` (single-sourced there) |
| this mod's LAUNCH — the whole thing | `agent/STATE.md` launch obligation → fix pack `reports/PARKED_OPTIN_REFERENCES.md` restore checklist, then the fix pack's `prompts/RELEASE.md` shape adapted (`WORKFLOW.md` "Release marking" + "Release steps") |
| the owner's mechanical pack+upload only | fix pack `docs/UPLOAD_WORKFLOW.md` (+ `reports/RELEASE_PORTAL_PREP.md`) — after `tools/upload_preflight.py` reports 0 FAIL |
| the drone system (D06 / D09 / the seed-logistics case) | `reports/DRONE_OVERHAUL_OPTIONS.md` + `reports/SEED_LOGISTICS_HANDOFF.md`; ⛔ parked per `FUTURE_IDEAS.md` #7 |
| an effort larger than ~2 sessions | `reports/CHAIN_METHOD.md` (propose a chain; commit the folder before link 1) |
| STATE is over its byte cap | `prompts/STATE_EVICTION.md` |

## 5 · End of session

Update `agent/STATE.md` **only if the current-state kernel actually changed** —
it is BYTE-capped by doccheck (warn 9 KiB / hard 18 KiB / 200 B per line), so
adding a line means evicting a resolved one to `archive/SESSION_LOG.md` in the
same commit; a doccheck WARN is copied VERBATIM into the owner summary; never
evict open gates, holds, owner decisions or the counts block. Route the session's
lesson to its §3 home. Then commit, push, summarize — and if work was FILED rather
than finished, say where.
