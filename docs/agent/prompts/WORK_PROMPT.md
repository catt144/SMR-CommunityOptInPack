# Work prompt — the start-here for ANY work on this mod (model-agnostic) — written 2026-08-31

Paste into a fresh Claude Code session for ordinary development work: designing
or changing a module, building a new one, investigating engine behaviour,
writing or fixing docs, tooling, launch prep. **Any model; the owner picks per
task.** Re-runnable; it does NOT delete itself. **Start with
`git log --oneline -10` + `git pull`** — the tree moves and this file goes stale
the moment another session commits. Staleness anchor: **written 2026-08-31 at
`6f002cb`**; verify against `git log` before trusting any specific it names.

> ⛔ **INSTRUCTIONS, NOT A LOGBOOK** (doccheck caps this file at 220 lines). No
> result, status or entry id lives here — those go to the entries, `STATE.md`
> and the fix pack's checklist. The only edits this file takes are corrections
> to its own instructions.

> 🧭 Two sibling prompts exist for narrower jobs: `prompts/DISPATCH.md` is for
> **issues once the mod is live** (player reports, field bugs); the fix pack's
> `prompts/GENERAL_USE_PROMPT.md` is for a **live playtest at the keyboard**.
> Everything else starts here.

**What you are working on.** An opt-in behaviour mod for Surviving Mars:
Relaunched — eight modules (D01–D07, D09, D12) that change how the game plays,
each OFF or at its base setting until the player enables it in Options → Mod
Options; patched at runtime over the mod's own copy of the pack framework
(`SMROptInPack`); a true standalone beside the Relaunched Fix Pack. Not yet
published. Map: `docs/README.md`. `CLAUDE.md` (auto-loaded) carries the two bans:
**persisted names are save contract** (every `SMRFixPack_*` field/modifier id
keeps its bytes — `agent/PROVENANCE.md` §2) and **zero `SMRFixPack` references
in executable code**.

## 0 · Orient — every session, before touching anything

1. `git log --oneline -10` + `git pull`.
2. **Read `docs/agent/STATE.md` whole** — the mandatory kernel: what is built,
   what is frozen, what the launch owes, which owner decisions are open.
3. Scan `docs/agent/bugs/INDEX.md` (nine entries) and `docs/agent/facts/INDEX.md`
   (one row per proven engine behaviour — several are the opposite of what the
   code suggests). Open only the entry/fact files the job touches.
4. **Create the todo list for the whole job before starting** — one item per
   commit-and-verify unit, one in progress at a time, marked the moment each
   completes, rewritten when reality diverges (`WORKFLOW.md` "Authoring a
   prompt" element 1). The owner reads it to decide when to step in.
5. ⚠️ **Only if the job launches the retail game:** the stale-probe gate binds
   first — `grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/`, in the
   todo list, CLEAN = zero hits or every hit declared by this job's design. The
   rig's NORMAL config is BOTH mods loaded and cheats on (`WORKFLOW.md`).

## 1 · Route by the kind of work

| the work is… | it runs under |
|---|---|
| **changing a module's behaviour, or building a new one** | `FIX_POLICY.md` §4 (what may be BUILT here — opinionated, proven, reachable), §4a (who benefits), §3a (save safety), §2 (fail safe), §1 (technique). Design-flavoured questions are the **owner's** (§2 below). Every change ships with an A/B (§3 below) and its entry updated in the same commit. ⛔ Module freeze in force except where `STATE.md` says lifted |
| **drone work** (D06 overhaul, D09 dials, `FUTURE_IDEAS.md` #7) | UNFROZEN 2026-08-31. ⛔ Do not build any part of the overhaul until the owner picks among the three options in the fix pack's `prompts/DRONE_PROJECT_PROMPT.md` §3; a time-boxed feasibility pass on option 3 is allowed if the owner asks. Designs: `reports/DRONE_OVERHAUL_OPTIONS.md`, `SEED_LOGISTICS_HANDOFF.md`. Log the commander profile with any measurement (D06 entry) |
| **investigating engine behaviour / answering a question** | `ModTools\Src` is read-only truth — cite `file:line`, re-derive the ROUTE not just the citations. A proven fact becomes an `EF-` file — ⛔ numbered by the FIX PACK first, mirrored here at the same id |
| **docs** | `docs/README.md` "Where new things go"; both `INDEX.md` are GENERATED; `python tools/doccheck.py` GREEN before commit (hook blocks red) |
| **tooling** | `tools/` inventory + what each proves: `agent/PROVENANCE.md` §6. Port from the fix pack with a ledger row; every instrument is an over-reporter — adjudicate a row by reading the source line, never by the count |
| **launch prep** | `STATE.md` "NEXT" (the ordered list), `WORKFLOW.md` "Release marking" + "Release steps" bullets 1–8, `tools/upload_preflight.py` 0 FAIL, the fix pack's `reports/PARKED_OPTIN_REFERENCES.md` restore walk |
| **an effort over ~2 sessions** | `reports/CHAIN_METHOD.md` — propose a chain; commit the folder before link 1 |
| **STATE over its byte cap** | `prompts/STATE_EVICTION.md` |
| **a live issue / a live playtest** | `prompts/DISPATCH.md` / fix pack `GENERAL_USE_PROMPT.md` |

## 2 · What is the owner's, not yours

- **Any design-flavoured call** — "should this module do X", "is that a defect
  or a rebalance", a new module's scope, a drone option. This mod's product IS
  opinionated behaviour, so these are owner rulings. Write the options up
  neutrally with the trade-offs measured, put the ask on the fix pack's
  `docs/PLAYTEST_CHECKLIST.md` → "Decisions waiting on you" (single-sourced
  THERE — `docs/README.md` says why), one line + pointer, and stop. **A decision
  recorded only in an entry or report is not considered asked.**
- **Lifting a freeze, changing a persisted name, uploading, renaming anything
  with a save or log contract** — never without the ruling in writing.
- **The wording of anything a player reads** (store text, dialog copy, the
  design-drift disclaimer for a drone rebuild).

## 3 · How a code change is done here — the loop

1. `tasklist | findstr Mars.exe` — the game is NOT running (a separate step
   from the edit; the junction makes the checked-out tree the running mod).
2. Read the module whole and its entry (`agent/bugs/D##.md`), then the facts it
   cites. Enumerate the target's call sites in Src (`FIX_POLICY` §4 reachability
   tiers: R1/R2 ship, R3 only as a patch, R4 does not ship, U needs a reading).
3. Edit under `FIX_POLICY`: wrapper inert for foreign objects before it reads a
   field; no cold-boot assumption (`apply` may run on the enable path, presets
   loaded and classes NOT built); every `(class, method)` pair captured or
   installed named in the module's `Require` block (F107); never `Require` a
   per-game global (F110); `SMROptInPack_Disabled` honoured in every handler.
4. **Parse sweep**: `python -c "from luaparser import ast; ast.parse(open(F, encoding='utf-8-sig').read())"`
   over every edited file. Then the desk instruments that apply:
   `tools/l2_reload_sim.py --strict` (registration across a ReloadLua),
   `tools/l3_save_footprint.py --src <Src>` (still exactly the five persisted
   names), `tools/harvest_wrap_targets.py --check` (doccheck runs it too).
5. **A/B in the TestKit** (`C:\Dev\SMR-BugFixPack-TestKit`, shared, local-only):
   the probe lives in `Code/60_Probes_Opt.lua`, reaches the code the way
   production does, computes its expectation independently of the module's own
   arithmetic, and carries a **vanilla control clause** (D12 clause 1 is the
   model). A leg with the module OFF and one with it ON; SKIP/PASS sets read BY
   NAME; grep with the full token `[CommunityOptInPack]`. Archive the log with
   `git add -f` in the same commit if a status flip cites it.
6. Update the entry (front-matter `status:` first, then the heading tag),
   `doccheck --emit-counts`, commit with `git commit -F <file>` carrying a
   `PROBE SWEEP:` line, push (`WORKFLOW.md` "Layout": push what you commit).
7. Status words: `tested-attended` (owner at the keyboard) / `tested-unattended`
   (real launches, no screen-event claims); bare `tested` is legacy, never new.

## 4 · Judgment rules the project has paid for

- **Challenge the cause before filing** — a control, not a plausible story.
- **Recorded facts are claims too** — the project has been wrong about a route
  with every cited line correct, twice.
- **Never silently discount a log line**; report the unexplained ones verbatim
  with their age. "Not ours" is an attribution verdict, not a dismissal.
- **"You can X" needs a route check** on the surface a player actually uses.
- **A negative result states the CONDITION it sampled**, not just the count.
- **Cheats on the rig are normal** — name the intersection with the reading or
  state there is none. Both mods loaded is normal — say WHICH pack every time.
- **File, don't fix, out of scope** — an entry line with the evidence, then stop.
  Ideas go to `docs/FUTURE_IDEAS.md`, a parking lot, NOT a backlog.

## 5 · Filing — where a result goes

- A defect or module record → `agent/bugs/D##.md` (next `seq`/`row` from the
  files), then regenerate the INDEX (`split_bugs.load_from_dir()` +
  `render_index()`, trailing newline) and `doccheck`.
- An engine fact → fix pack `EF-###` first, mirrored here at the same id.
- A report, plan, spec, audit → `agent/reports/` (not authority — entries win).
- A binding rule → `WORKFLOW.md` (process) or `FIX_POLICY.md` (code).
- A session leg → `archive/SESSION_LOG.md` (append-only, newest first, `tags:`).

## 6 · Stop conditions — permission to report instead of pushing on

- The next step needs an owner ruling (§2) — write it up, ask, stop.
- A test needs the owner at the keyboard, or a save fixture that does not exist.
- The edit would touch a persisted name, a `Register` id, the mod id, the log
  tag, or a module under a freeze `STATE.md` still shows.
- A fact in `agent/facts/` contradicts what Src says today — correct the fact
  in the same commit and say so; do not build on either silently.
- The job is bigger than one context — propose a chain (`CHAIN_METHOD.md`).

## 7 · What may NOT be claimed

- `tested-*` for anything not run in the retail game; a desk simulator PASS is
  "desk-verified", never "verified".
- "Standalone" or "works without the fix pack" for a change not run in BOTH
  configurations (`FIX_POLICY` §8).
- Any count not emitted by `doccheck --emit-counts`; any probe total that is
  not the shared suite's, labelled as such.
- "Save-safe" without the `l3` census and the entry's §3a shape statement.
- A verdict for a screen event from an unattended leg.

## 8 · Close-out

Update `agent/STATE.md` only if the kernel changed (byte-capped: adding a line
means evicting a resolved one to `archive/SESSION_LOG.md` in the same commit;
copy any doccheck WARN verbatim into the owner summary). Route the session's
lesson to its §5 home, never here. Owner asks → the fix pack's checklist.
`doccheck` GREEN, commit, push, summarise — and if work was FILED rather than
finished, say where.
