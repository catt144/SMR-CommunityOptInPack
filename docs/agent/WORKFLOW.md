# Development Workflow

> ## ⭐ ADAPTED COPY — read this ledger before you trust a clause
>
> Copied from `SMR-BugFixPack/docs/agent/WORKFLOW.md` @ `33d69f5` on 2026-08-12
> (chain `split-optins`). **Every harness rule is kept VERBATIM and binds here:**
> probe hygiene and its ARM gate, the resolution cross-check, leg design, the
> log-review rule ("never silently discount a line"), the cheats rule, the
> co-run protocol, the prompt/brief authoring requirements, EF-047/048/049/050,
> the PowerShell 5.1 hazards, the parse sweep, the `PROBE SWEEP:` line.
>
> **What changed, and nothing else:**
>
> 1. **Layout + Install for testing** — re-pointed at this repo, its junction
>    (`SMR-OptInPack`), its mod name and its console helper
>    (`SMROptInPack.ListFixes()`). ⭐ The TestKit is SHARED, not copied.
> 2. **The namespace** — `SMRFixPack.*` → `SMROptInPack.*` throughout. ⛔ NOT
>    the persisted `SMRFixPack_*` field names (`agent/PROVENANCE.md` §2).
> 3. **Reading path** — the two human playtest files live in the FIX PACK repo
>    and are named with their full path; the fact count is this repo's.
> 4. **BOTH MODS LOADED** — installed as this repo's twin of the donor's clause.
> 5. **Release steps** — kept in full, with a marked block saying which bullets
>    are N/A here and which apply. Nothing deleted.
>
> Where a clause says "the pack", read "this mod" — except where it names the
> Community Fix Pack explicitly, which after the split is a DIFFERENT product.

## Reading path for a new session

1. `docs/agent/STATE.md` — current state: authoritative build counts, open
   owner decisions, next gates (`CLAUDE.md`, auto-loaded, points here).
   Session history lives in `docs/archive/SESSION_LOG.md` (append-only,
   newest first).
2. `docs/agent/facts/INDEX.md` — one row per proven engine behavior (several
   are the opposite of what the code suggests). Scan all 54 rows so you know
   what exists; OPEN the fact files your job touches and read them before
   writing or reviewing any module. Reading all 54 files as a matter of course
   is the cost the 2026-08-03 restructure removed — don't reinstate it.
   ⚠️ **This folder is a COPY of the fix pack's, taken 2026-08-12** and the two
   diverge from that date on: a fact learned here should usually be carried
   across, and a fact learned there will not appear here by itself.
3. `docs/agent/bugs/INDEX.md` — the defect tracker's entry point: status,
   priority and evidence label per row; the entry file carries the narrative.
   Update the ENTRY in the same change that adds or edits a fix. **`INDEX.md`
   is GENERATED — never hand-edit it.** A status still lives in two places, but
   both are now inside the entry file: front-matter `status:` and the heading
   tag. doccheck goes red if they disagree, and red on a stale INDEX.
4. `docs/agent/FIX_POLICY.md` — how we patch. Binding for every fix.
5. ⚠️ **`C:\Dev\SMR-BugFixPack\docs\PLAYTEST_CHECKLIST.md`** — the owner's live
   playtest queue, the reporting protocol and **"Decisions waiting on you"**;
   its companion `PLAYTEST_HELP.md` (same folder) carries the ground rules,
   console facts, the verified command table, Test Kit helpers and save-fixture
   recipes. **Both are single-sourced in the FIX PACK repo on purpose** — the
   owner plays one game with both mods loaded, and `docs/README.md` explains
   the decision. An owner decision arising from work HERE still goes THERE.

## Binding authoring rules (adopted 2026-08-03, DOC_STRUCTURE_REVIEW → spec §7)

Recommendations until this date; **binding from it.** They are cheap at write
time and each one is named after the miss it prevents.

1. **Execution markers (R2).** Every console line, lever or command printed in a
   human doc carries `[RAN <date>, log <name>]` or `[NEVER RUN]`. Unmarked, a
   never-executed snippet reads exactly like a proven one — the PT-61 near-miss
   was a gate that would have parked a whole attended sitting.
2. **Provenance words (R3).** Load-bearing claims in entries, specs and briefs
   are prefixed **MEASURED / SOURCE / INFERRED / INHERITED / GUESS**, and **the
   ROUTE sentence is tagged separately from its citations** ("therefore the only
   way is…" is a different claim from the lines it cites — the project has been
   wrong about a route while every cited line was right, twice). ⛔ **A blanket
   verification claim over a table is banned: the tag goes per row.**
3. **TAKEABLE-WHEN on routed items (R5).** Routing names the owner prompt AND
   the precondition ("needs a suite run" / "a colony with the law enacted" /
   "the owner at the keyboard"). An item whose precondition is a *situation*
   goes to the checklist as a rider immediately, not to a prompt that will
   forward it again.
4. **Archive load-bearing logs (R8).** If a leg's numbers will be cited by a
   status flip, copy the log into the repo in the SAME commit. The game's
   rotation cap is ~20 files and it has already eaten founding measurements.
   Cannot be applied retroactively, which is the whole argument for now.
   ⛔ **`.gitignore` line 2 is `*.log`, so the archive copy needs
   `git add -f`** — a plain `git add` drops it SILENTLY and the commit looks
   complete (one commit shipped with a false archive claim before this was
   caught, 2026-08-03).
5. **Owner-decision mirroring (R10).** Every item needing the owner's call is
   mirrored into `docs/PLAYTEST_CHECKLIST.md` → "Decisions waiting on you"
   (one line + pointer), and struck the moment it is decided. **An owner
   decision recorded only in an entry or a report is not considered asked.**

Two mechanical rules that came with the same restructure:

6. **`INDEX.md` in `agent/bugs/` and `agent/facts/` is GENERATED.** Edit the
   entry or fact file; doccheck regenerates the index and goes red on any
   difference, and red when front-matter `status:` and the heading tag disagree.
   **Edit order for a status flip** (adopted 2026-08-03, standing-prompts
   redesign O4): front-matter `status:` first — the index regenerates from
   it — then the heading tag to match, in the same edit. A red doccheck means
   you stopped halfway.
7. **Run `python tools/doccheck.py` before committing doc changes** — red
   blocks. One-time setup: `git config core.hooksPath tools/hooks`.
8. **STATE.md's 60-line cap comes with an eviction rule** (adopted 2026-08-03,
   standing-prompts redesign O7). To add a line at the cap, evict in the same
   commit: resolved or superseded material moves to
   `docs/archive/SESSION_LOG.md` (append-only, newest-first). Evict history,
   never obligations — open gates, holds, owner decisions and the counts
   block stay.

## Layout

- **Dev repo (this folder):** `C:\Dev\SMR-OptInPack` — git-versioned, canonical.
  Remote `github.com/catt144/SMR-CommunityOptInPack`, **public** by owner ruling
  2026-08-13 (chain rule 9's "no remote unasked" was satisfied by asking). Push
  what you commit, the same as the fix pack.
- **Companion mod, a separate product:** `C:\Dev\SMR-BugFixPack` (Community Fix
  Pack, remote `github.com/catt144/SMR-CommunityFixPack`). Shares no files with
  this repo. Its `docs/archive/` holds all pre-2026-08-12 history, and its
  `docs/PLAYTEST_CHECKLIST.md` / `PLAYTEST_HELP.md` are the owner's two files
  for BOTH mods.
- **Game install:** `A:\SteamLibrary\steamapps\common\Project Spark`
  (Surviving Mars: Relaunched; "Project Spark" is the Steam folder codename).
- **Shipped Lua source (read-only reference):** `<game>\ModTools\Src`
  (`Lua\`, `CommonLua\`, `Data\`, `DLC\`). We never modify anything under the
  game folder.
- **Mod install point:** `%AppData%\Surviving Mars Relaunched\Mods\SMR-OptInPack`
  — a directory junction into the dev repo (see below), so edits are live. The
  fix pack has its own junction (`SMR-BugFixPack`) beside it.
- **Companion TestKit** (never shipped): `C:\Dev\SMR-BugFixPack-TestKit`
  (own git repo, local-only by decision — see its README). ⭐ **ONE kit serves
  BOTH mods** — it is not forked, and a probe change is made once, there. This
  mod's surface in it is `SMRTest.OptStatus` / `SMRTest.OptMissing` /
  `SMRTest.FromOptInPack`; `OptMissing` SKIPs (never FAILs) when this mod is
  simply not installed.

## Install for testing

```powershell
New-Item -ItemType Directory -Force "$env:APPDATA\Surviving Mars Relaunched\Mods" | Out-Null
New-Item -ItemType Junction -Path "$env:APPDATA\Surviving Mars Relaunched\Mods\SMR-OptInPack" -Target "C:\Dev\SMR-OptInPack"
```

Then enable "Community Fix Pack: Opt-In Modules" in the game's Mod Manager (working title —
`agent/PROVENANCE.md` §3). After editing Lua, restart the game.
⛔ **A Mod-Manager disable takes effect only after a FULL PROCESS RESTART**, and
re-enabling the owner's mods is the owner's call, not an agent's. **Opt-module first-enable caveat is FIXED (audit 2026-07-29):**
hooks now install at file scope, so a first mid-session Mod Options enable
works without a relaunch.

In-game checks: console `SMROptInPack.ListFixes()` prints each module's status
(active / inactive+reason / disabled / error). The fix pack's own
`SMRFixPack.ListFixes()` still exists in ITS env when it is installed — two
registries, two log prefixes (`[CommunityOptInPack]` vs `[CommunityFixPack]`).
⛔ **Grep logs with the full bracketed token**: `Pack]` matches both.

## Per-fix discipline

1. Every fix links to an `agent/bugs/` entry with file:line evidence (FIX_POLICY §4).
2. Before patching, re-verify the target against the cited Src lines; the
   apply() self-check then guards it at runtime and returns a reason string
   (never errors) if a game update changed it.
3. Parse sweep before any commit that touches Lua: python + `luaparser`,
   `ast.parse(open(f, encoding='utf-8-sig').read())` over every edited file —
   a syntax error in ANY listed file breaks the whole pack at load.
4. One commit per fix or tight group; agent/bugs/ updated in the same commit;
   MOD_DESCRIPTION.md updated in the same commit as the code change it
   describes.

## fpk verification — RELEASE GATE, re-run after every game update

All agent/bugs/ line numbers come from `ModTools\Src`; the game executes
`Packs\Lua.fpk` + `Data.fpk`. **Parity is PROVEN for the current build
(1.0.7.396349, extraction diff 2026-07-29): 2,250/2,256 shipped Lua files
byte-identical to Src; the 5 divergences are engine/tooling only** (details in
agent/facts/). The discipline guards *future* updates:

1. After every game patch, re-extract `Packs\Lua.fpk` (FLPK container, zstd
   per file) and diff against the new Src tree; re-verify every replacement
   fix's target function byte-for-byte (the ~29 full replacements are the
   pack's patch-rot exposure — C1 in `docs/archive/AUDIT_FINDINGS.md`).
2. Runtime self-checks stay mandatory in every apply() regardless (existence/
   layout checks only — the sandbox has no introspection; they catch renamed/
   removed targets, NOT an edited same-named function — hence step 1).

## ⛔ Probe hygiene — HARD GATE before ANY testing (owner, 2026-08-01)

**No test session — attended or unattended — starts, and NO result is
recorded, until the stale-probe sweep has run and reported clean.** Stale
probes are how false facts got recorded: leftover instrumentation logs, hooks
messages, creates threads, and contaminates both the measurement and the log
it is read from (the 2026-07-31 probes were still armed days after their
questions were answered).

**The sweep (mechanical, one command):**

```
grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/
```

**CLEAN =** zero hits, **or** every hit is a probe that THIS session's test
design explicitly declares it needs — named in the brief and in the todo
list. Anything else: the session repairs first (delete the file + its
metadata/items lines, commit) or stops and reports.

**The rules that make this work:**

1. **Every temporary probe/experiment file MUST carry the literal word
   `TEMPORARY` in its header comment** — that is what the sweep greps for.
   A temp probe without the marker is itself a defect: file it on sight.
2. **A probe is STALE the moment its answer is recorded.** Deletion belongs
   in the SAME commit that records the answer (docs-never-lag, applied to
   instrumentation).
3. **The sweep result is part of the record:** every commit that flips a
   agent/bugs/ status, records a MEASURED fact, or reports a PASS/FAIL carries a
   `PROBE SWEEP:` line — either `clean` or `armed: <files>, declared by
   <test>`. **A result commit without that line is invalid and gets
   re-verified before anything builds on it.**
4. Both repos are in scope (the pack AND the TestKit) — the
   `GetPriorityForRequest` experiment that seeded agent/facts/ lived in the
   PACK's code list.
5. ⛔ **A PROBE FILE IS PRESENT IN `Code/` ONLY WHILE ITS RUN IS ACTUALLY
   HAPPENING** (owner decision, 2026-08-04 — *"I want to do whatever is safest,
   I do not want to get back into the situations where armed probes start
   giving us false problems or issues"*). **Placing the file and running are the
   same act; deleting it and recording the answer are the same commit.** There
   is no state in between, and therefore no armed probe can outlive the sitting
   that needed it.

   **What made this a decision rather than an observation.** `doccheck.py`'s
   `temporary_sweep()` (`tools/doccheck.py:501-517`) implements only the FIRST
   half of the CLEAN definition above — any marker in `Code/` is red, no
   declared-probe exception — and `tools/hooks/pre-commit` blocks on red. So a
   session may legitimately declare a probe but **cannot commit anything while
   it is armed**, which collides with the co-run rule that all prep is committed
   before the owner sits down. Found by co-run #0 (2026-08-04), the first job to
   arm a probe since doccheck landed. **The tool was NOT loosened, deliberately:
   a hatch a hurried session can open without saying so re-creates the
   2026-07-31 incident exactly.** ⛔ **`--no-verify` is not an alternative** —
   the hook documents its meaning as *"the docs are inconsistent, I know"*,
   which is a false statement when the only red is a declared probe.

   **How prep works under this rule, and it costs nothing.** Everything else
   commits normally and early: the staged save copy, the measure-moments list,
   the entry and checklist edits, and **the probe's source itself as a fenced
   code block in the session's own brief or spec**. Docs are not swept (the
   sweep walks `Code/` and TestKit `Code/` only), and a probe parked in a doc is
   **inert by construction** — the mod loads only files listed in
   `metadata.lua` `code`, all of which live under `Code/`, so a file that is not
   there cannot arm anything, log anything, or contaminate a measurement. At the
   sitting: write the file into `Code/`, add its metadata line, parse sweep,
   run. Then delete both in the commit that records the answer, per rule 2.

   **If the sitting slips, nothing is stranded and nothing is armed** — which is
   the whole point.

   ⚖️ **In force. The owner-requested recheck RAN 2026-08-04 (corun-rig prompt
   4) and the rule STANDS as written.** The diagnosis re-verified from primary
   sources (`temporary_sweep()` really has no conditional path,
   `tools/doccheck.py:501-517`; the hook really blocks on red; the CLEAN clause
   reads as quoted). The one claim the diagnosis had left unverified is now
   SOURCE-verified: **`ModDef:LoadCode` executes only the files listed in
   `metadata.lua` `code`** — both of its loops iterate `ipairs(self.code)`,
   no directory is scanned (`Mod.lua:490-521`) — so a parked probe is inert by
   construction in the strong form, not merely the outside-`Code/` form. The
   feared cost does not exist: the parse sweep is location-independent
   (measured GREEN on a parked path during co-run #1 prep), and the declined
   one-time override measured what any hatch would buy — **0.4 s of machine
   time and zero owner time** — against a red doccheck in the history and a
   live disarm deadline. No hatch is recommended; none was built.
   Two things the rule does NOT say, so nobody reads them into it: it does not
   ban long-lived instrumentation (that belongs in `90_Loggers.lua` behind an
   explicit toggle, permanent and non-`TEMPORARY` by design — the file exists
   and is the established home), and it does not excuse skipping the parse
   sweep — which runs at the sitting, on the real file, before the launch,
   exactly as before.

## Testing checklist per fix

**Leg-design rules (adopted 2026-08-04, from the first campaign sittings —
relocated here from the standing prompt, which is instructions, not a
logbook):**
- **An "objective counter" is only objective if it can FAIL, and it needs a
  liveness witness beside it.** PT-62's loop check counted a delivery the
  flagged dome was *required* to receive, so it could not fail; F11's `nil`
  reading only meant something because `#units` and `holder` were read in the
  same breath, ruling out an empty list and a call that never fired.
- **When a test's trigger is a selection you cannot steer, delete the lottery:**
  invoke the shipped call site directly on a chosen target and settle the
  selection half by reconstructing the pool and reading it (F11's
  `SetCommand("EnterTransporter", …)` is verbatim the shipped caller's body —
  an unrunnable rider became a five-minute answer costing zero expeditions).
- ⛔ **A negative result must state the CONDITION it sampled, not just the
  count** (adopted 2026-08-04, co-run #1 correction C10). "Absence under N
  cycles is a rate bound" holds only if the condition the claim needs was
  actually present in those N cycles; absence of a never-sampled condition is
  not a negative result at all. The breach that earned this: a pre-registered
  corner-slam prediction was recorded REFUTED, with a confident false reason,
  when its y-axis condition had never been sampled — one 64 s re-run sampled
  it and confirmed the prediction to the pixel. The rate-bound rule is about
  counts; this one is about conditions; a verdict needs both.
- **Gates on owner actions DETECT the condition; they never ask for a typed
  token as the primary signal** (co-run #1, found by the owner). Run 1's brief
  told the owner to type a gate the code did not contain — the run proceeded
  without them and only the owner noticed. Run 2 polled until the condition
  itself held (cursor actually reading out of range) and could neither be
  mis-documented nor missed. Typed gates still work as a convenience
  (`GATE 1 RELEASED by owner`); they are one more thing to keep in sync.

1. Load a save (or new game) where the bug reproduces; confirm reproduction
   with the mod disabled.
2. Enable mod; confirm fixed behavior.
3. Confirm no error spam in the log (`%AppData%\Surviving Mars Relaunched\logs`).
4. Save with mod enabled → **disable the pack in the MOD MANAGER** → load: game
   must not break (PT-20 shape; FIX_POLICY §3).
   ⛔ **NOT a Mod Options toggle, ever.** A toggled-off module still has its
   hooks installed and its env present, so a captured frame resolves
   `SMROptInPack`, reads inactive and no-ops — **the load reads clean by
   construction whether or not the module leaks.** `Opt_DroneOverhaul` leaked at
   98 errors/session with its own toggle OFF; that is how F86 Site 2 was found.
   Mod-Manager-disable is measured equivalent to a real uninstall (PT-20: 98 vs
   98 on the same save). `agent/facts/`, "OFF" IS THREE DIFFERENT THINGS.
5. Set the entry's status to `tested` in `agent/bugs/<ID>.md` — front matter
   AND heading tag — per the checklist's reporting protocol. Not INDEX.md.

The TestKit's `SMRTest.RunAll()` A/B pair (baseline vs full pack) is the
regression harness; run it as pre-flight when STATUS says one is owed.

### ⛔ Log review: NEVER silently discount a line (owner rule, 2026-08-01)

**Two facts about how legs actually run, and they change what a log is** (full
reasoning: `BUG_LIST_AUDIT.md` §10.6f(i); the same session provisioning is why
our test colonies are heavily loaded before any agent starts):

- **The owner does not close or refresh a game session unless a leg calls for
  it**, so a flushed log typically covers **1–6 hours of continuous play**.
- **The owner reviews the errors WITH the agent** and pushes back when a line
  does not fit the test. That has happened rarely — and **every time it has, it
  turned up a VANILLA defect that was not on our list.** The practice has paid
  for itself; it is not ceremony.

**The rule, and it is the whole point:**

> **"Not caused by our leg" is an ATTRIBUTION verdict, never a reason to stop
> looking.** Locating an error in time answers *"did we cause this?"* — it does
> **not** answer *"what is it, then?"* Collapsing those two is how a discovery
> gets thrown away.

**So: report every unexplained line, state its age, and let the owner decide.**
Do not reason privately that a line is hours older than the leg and therefore
irrelevant, and do not summarise it away as noise. If something is out of the
ordinary, **stop and say so** before continuing the leg.

**Why this works, stated precisely.** The agent writes its predictions before
the run (PT-58's P1–P7 shape) and so knows what it *should* see and why; the
owner independently reviews everything the agent saw and does not know what to
expect. **Anything outside the prediction is signal by construction** — and the
one party able to recognise it is the one being asked not to file it away
quietly. A log that only ever confirms the prediction has been read for the
prediction, not read.

**Corollary worth acting on:** since the logs span hours of ordinary play, **old
logs hold evidence no leg was designed to collect.** Mining them for `[LUA
ERROR]` of any origin is cheap and has a track record.

### ⛔ Cheats on playtest saves are the NORMAL condition, not a deviation (owner rule, 2026-08-12)

**Adopted mid-sitting during `corun-pt60`, in the owner's own words, after a leg
flagged six `ObjCheat CheatFill` markers as if they needed defending:**

> *"We really need a standing rule that these saves are play testing saves with
> colonies that are over sized and underindustrialized. They cannot support
> themselves so cheats are needed to keep the colonies alive and functional. So
> filling food, and maintance materials are needed for the game to run without
> all the colonists dieing or buildings breaking. And unless a chain truely
> needs a no cheat setup we will continue to have to use it, and we will need to
> prep a save with alot of reasouces if we need a no cheat run"*

**What binds, for every future leg:**

1. **The baseline expectation is that cheats WILL appear in a playtest log.**
   Every save in the owner's folder is a heavily-loaded test colony built to
   exercise defects, not a balanced economy — it cannot feed or maintain itself.
   `CheatFill` on food and maintenance resources is **life support for the
   fixture**, and without it the colony dies or its buildings break, which
   destroys the very state the leg was provisioned to read.
2. **Still count them, still name them, still put the reason in the log** —
   the reporting duty is unchanged (`git`-archived logs are the record). What
   changes is the FRAMING: a cheat marker is **attributed**, not excused, and
   **⛔ ask for the reason ONCE.** (`corun-batch-2`'s own ledger records that
   the cheat disclosure took three asks; that is the failure mode this rule
   retires.)
3. **⛔ A cheat is only a confound if the reading intersects what it changed,
   and the agent must NAME the intersection or state there is none.** "Cheats
   were used" is not by itself a caveat on a verdict — e.g. filled storages do
   not touch track shells, dome-Saint modifiers, colony `label_modifiers` or a
   field on `DroneControl`, so PT-60's P8/P9 readings were unaffected and said
   so.
4. **A leg that genuinely needs a no-cheat run must DECLARE it in its brief and
   PREP a resource-rich save in advance.** It cannot be improvised on an
   existing playtest save, and it may not be satisfied by asking the owner to
   stop using cheats on a colony that needs them to survive. Provisioning that
   save is prep-side work with a stated cost, like any other fixture.

**Why this is a rule and not a note:** the owner has now justified the same
practice across multiple sittings, and every re-ask spends the one resource the
co-run model exists to protect. See also the standing fixture rule — playtest
saves are PROVISIONED before an agent ever reads them, so their state is never
"fresh".

### ⛔ BOTH MODS LOADED is the rig's NORMAL condition (owner rule 2026-08-12 — ⚖️ ACTIVE since the `split-optins` terminal audit, same date)

> ⭐ **THIS REPO'S TWIN of the fix pack's clause, installed at the split**
> (2026-08-12). It is the SAME rule, read from this side: an
> `[CommunityFixPack]` line in one of THIS mod's legs is expected background,
> attributed and never flagged as foreign. Both copies were activated together
> by the split chain's terminal audit, 2026-08-12.

**The owner's words, given while the `split-optins` chain was authored:**
*"Once we get it seperated I will keep the opt ins loaded in as they make
testing easier. So the agents should be aware of that, and it shouldn't be an
issue because we should be compatible as well."*

**What binds, for every leg after the split chain closes:**

1. **The baseline rig configuration is BOTH mods enabled** — the fix pack AND
   the standalone opt-in mod. A gate read shows two registries. ⭐ **MEASURED
   BASELINE (cell a2, 2026-08-12, audit-recounted from the fix pack's
   `archive/spa2_Mars.exe-20260812-18.44.24.log`): `fix pack present: 74/74` ·
   `opt-in pack present: 8/8` · suite `78 PASS / 0 FAIL / 10 SKIP / 0 ERROR`
   of 88; load order `1:SMR_CommunityFixPackTestKit 2:SMR_CommunityFixPack
   3:SMR_CommunityOptInPack` (enable order, `EF-054` — THIS mod's wrappers sit
   OUTERMOST).** Every "the pack" claim names WHICH pack. A fix-pack line
   in one of this mod's legs is expected background: attributed, never flagged
   as foreign.
2. **Same confound rule as cheats:** a loaded opt-in module is only a confound
   where the reading intersects what it changes (D09 dials touch drone
   speed/carry; NoHomeless/CohortHousing move colonists; MultipleSuns touches
   build limits) — **name the intersection or state there is none.** "The
   opt-in mod was loaded" is not by itself a caveat.
3. **A leg that genuinely needs the opt-in mod OFF must DECLARE it in its
   brief** — and budget the toggle honestly: a Mod-Manager disable takes
   effect only after a FULL PROCESS RESTART (D13's four-states rule), and the
   re-enable is handed back to the owner like any pack re-enable.
4. **The standing configuration is also the compatibility soak.** The owner's
   ordinary testing IS continuous both-mods exposure; any cross-mod
   interference that survives the split chain's matrix will surface here
   first — whole-log reviews watch for it as a named class, and a hit routes
   to BOTH repos' records.

⚖️ **ACTIVATED 2026-08-12 by the `split-optins` terminal audit, in BOTH
repos.** Pre-split single-pack gate reads are history, quotable never.

## Co-runs — attended experiment legs with the labor inverted (adopted 2026-08-04, owner)

**Why this exists.** The owner's attended time is the scarcest resource in the
project, and by 2026-08-04 the playtest load had grown to where one clean
playtest a day was a good day — most of the burn was setup, deviations and
trigger-fishing, none of which needs a human. A **co-run** splits an attended
leg along the actual skill line: **the agent drives the game** (launch, save
staging, scenario scripting, amplification loops, log reads) and **the owner is
on call, not on duty** — present for the minutes where eyes on the screen or a
judgment call are genuinely needed, and free otherwise.

⭐ **WHAT THE GOAL ACTUALLY IS, IN THE OWNER'S OWN WORDS (2026-08-04) — read
this before optimising anything:** *"As much that can be optimized while not
reducing quality it probably the better framing of it. Keep a good balance of
quality and minimal time investment as there is only one of me."* And, on the
same day: *"This whole method isn't to take me completely out of the loop, its
to take my time commitment to a more reasonable level and streamline."*

> **The owner's time is the OBJECTIVE to minimise. QUALITY is the CONSTRAINT
> that binds.** Optimise their involvement as hard as it will go — and stop
> exactly where going further would cost evidence quality, not one step before.

Both failure modes are real and this rule names both:

- ⛔ **Do not buy time savings with evidence.** If removing the owner from a
  moment means the finding gets weaker — an unwitnessed behaviour, a forced path
  standing in for an organic one, a verdict nobody competent to disagree ever
  saw — **the saving is not available.** Route the item; do not quietly
  downgrade what it proves. This is the reading "minimise owner contact" gets
  wrong.
- ⛔ **Do not spend an hour of engineering to dodge thirty seconds of their
  hands.** Asking is legitimate when the ask genuinely beats the alternative on
  the quality/time trade — say what you need, why, and how long it takes them,
  in the measure-moments list up front and batched with moments they are already
  sitting for. But asking is **not free and not a default**: every ask competes
  with the ones that actually need eyes.
- **"Needs the owner" is a precondition to route** (a TAKEABLE-WHEN rider),
  never a reason to descope. They stay in the loop by design; what changed is
  that they are no longer doing the setup.
- ⛔ **AN OWNER OVERRIDE IS A COURSE CHANGE, NOT A VARIANCE TO MANAGE (owner
  rule, 2026-08-05):** *"My time is valuable and is a major concern. But if I
  decide to over ride and follow a lead, a session shouldn't remind me nearly
  every message that we should get back on track. Which makes trouble shooting
  hard when I am trying to keep track of what I have sent to it to check and
  what I have not."* And the owner's leads are not a tolerated cost — they are
  a **proven discovery channel** (owner, same day: past leads *"found multiple
  new bugs or changed the outcome of our tests"* — the record agrees: even the
  2026-08-05 lead the owner scored as a miss on its own target banked `F101`
  and both F99 samples, and earlier leads produced the F02 watchdog challenge
  that overturned a false-positive reading and the D07 staleness catch). Treat
  a lead as first-class work to instrument and witness, not a detour to wait
  out. Two binding halves:
  - **State the plan's position ONCE when the deviation starts** (so the
    remaining legs are on record), then drop it. No back-on-track reminders
    until the lead closes, the owner asks, or the sitting is ending. The
    time-is-the-objective rule above is about *authoring* cheap sittings —
    it is never license to nag the owner off their own lead.
  - **During the deviation the session carries the bookkeeping**: a live
    ledger of what has been handed to the owner to check, what came back, and
    what is still outstanding — that is the tracking the reminders were
    breaking. The owner troubleshoots; the session keeps the score.

⛔ **And do not report owner-minutes saved as if zero were the target.** Report
cost against promise. A sitting that came in under its promise is a measurement,
not an achievement.

**Route an item to a co-run when:**

1. **Setup is heavy, the measure is short** — hours to build the exact scenario,
   five minutes to observe it (the F11-conversion watch, staged fixtures);
2. **The trigger is intermittent or unknown** — the agent amplifies (loop the
   suspect path, sweep the timing, force the upstream condition repeatedly)
   until the thing shows, while the owner watches for what only eyes can see
   (C41's vanishing picker is the poster child);
3. **A C-side wall needs a live measurement** — ordering/tie-break questions
   settle in one launched-game console read and need no eyes at all; they ride
   along free in any co-run sitting.

**Protocol (binding):**

- **All prep is unattended and happens BEFORE the owner sits down**: scripts
  written, save copy staged, and the brief carries a **measure-moments list** —
  each moment says what the owner will look at and what verdict words to say.
  The owner's attended cost is the sum of the measure moments, nothing else.
  ⚠️ **"Scripts written" means written and committed AS TEXT IN THE BRIEF, not
  placed in `Code/`** — probe hygiene rule 5 (owner, 2026-08-04). The file lands
  in `Code/` at the sitting and dies in the commit that records the answer, so a
  slipped sitting can never leave a probe armed.
- **Runs use a designated COPY of a provisioned save, never the campaign
  save** (FIX_POLICY §3a discipline applies to experiments, not just fixes).
- **The probe-hygiene hard gate applies unchanged** — sweep before, probes
  deleted in the commit that records their answer.
- ⛔ **The forced-vs-organic rule (the F99 lesson):** forcing an *upstream
  condition* is legitimate when the *measured path* stays organic (force the
  meteor, let the drones repair); forcing the path under test measures the
  forcing, not the game. Every co-run finding **names what was forced**.
  Forced repro establishes MECHANISM; evidence upgrades to organic-witnessed
  still require an organic sighting.
- **Batch aggressively.** One sitting should drain every co-run-ready rider
  plus all ride-along console reads — the launch and warm-up are the fixed
  cost; unattended-measurable items in the same sitting are free.
- ⛔ **Arming/disarming edits are a script FILE run by the shell, never an
  inline one-liner through PowerShell** (co-run #1, correction C11: an inline
  edit's quoting was mangled, the `metadata.lua` line was silently not added,
  and the game launched unarmed — caught only by reading the tool output).
  Same hazard class as `git commit -m`; same remedy shape as `-F <file>`.
  ⚠️ **C11 corollary (unattended-1, I2): a script file is not enough if its
  OUTPUT is piped** — `… | Select-Object -First N` terminates the upstream
  pipeline and can kill the arming script before its write executes. The game
  launched unarmed and sat 8 minutes doing nothing, and the owner spotted it
  before the run's own outside bound did. ⇒ **ARM GATE, binding:** before
  every launch the launcher reads `metadata.lua` and the probe files back OFF
  DISK and refuses to launch unarmed. Cost of the whole failure class: 8 min
  → 0.2 s.
- ⛔ **Harness-defect classes from unattended-1 (2026-08-04; 8-entry ledger,
  0 of them the game's fault — 3 of 7 parse-GREEN, Src-verified parked probes
  still produced wrong answers on their first run). Every brief guards
  against these:**
  1. **Resolution cross-check before launch** — diff the helper names USED
     against the names DEFINED (one command). A parse sweep is a *syntax*
     verdict, not a resolution one: `U1.ErrorWatchNote` was called by all 7
     payloads and never existed; every cycle would have died as
     `PAYLOAD ERROR`.
  2. **A completion counter names its liveness WITNESS in the brief**
     (leg-design rule 1, now a brief-authoring requirement): leg C's counter
     was true on its first evaluation and scored 4 organic repairs having
     observed none. The witness (damage actually seen before the wait) is
     what let the re-run's 4/4 mean something.
  3. **`pcall`'s result is always captured and printed** — two probes
     discarded it, and in leg E that turned 34 raises into a confident false
     sentence about vegetation: a swallowed raise and a nil return print
     identically.
  4. **Per-chain facts never live in per-process flags** — every cycle is a
     fresh process; `save_proven=false` made a leg abort citing a proof that
     had PASSED. Gate on the live check (list-before/list-after), or on the
     recorded, archived fact — never on process state.
- **Close-out runs `git status` in BOTH repos.** No gate anywhere checks the
  TestKit's working tree (measured 2026-08-04: a true, verified record sat
  stranded there for a day and surfaced only because a co-run happened to look),
  and a co-run touches both repos by construction. A stranded edit is a finding
  to route, never something to quietly commit or discard.
  ⛔ **And close-out LISTS THE SAVE DIRECTORY against the brief's expected
  survivors (adopted 2026-08-10)** — the git gate never looks there, and the
  same four staged saves were falsely recorded deleted by TWO independent
  sessions (batch-1's audit and batch-2's prep) before batch-2's sitting made
  the listing part of close-out and the audit re-checked it hours later
  (deletion held). A "deleted" claim without a directory listing after it is
  not a record.
  ⛔ **AND A LISTING PROVES THE DELETION HAPPENED, NEVER THAT IT HELD (measured
  2026-08-11, `agent/facts/EF-051`): Steam Cloud restores deleted savegames at
  the next launch** — 14 of them came back, written before the game process even
  started, with creation stamps from tonight and modification dates a week old.
  That is what the two "failed" close-outs were: they deleted the files and
  Steam put them back.
  ✅ **RETIRED 2026-08-11 (`corun-pt15` terminal audit).** The owner unticked
  cloud saves 2026-08-11 ("Steam settings done") and **two post-untick launches
  are now sampled** — the owner's own (09:47, nothing restored, every directory
  delta reconciled by NAME) and the PT-15 sitting's (15:09, all 14 strays still
  absent at the audit's re-listing, 59 `.sav` reconciled by name). Close-outs
  may again record **"gone — verified by a NAMED listing"**. ⛔ Two clauses
  survive the retirement: **(1) baselines and listings are NAMES, never a
  count** — a count cannot survive one play session (two autosave rotations and
  three creations net to +1 and hide both movements — `EF-051`); **(2) the
  restore *signature* (fresh `CreationTime`, old `LastWriteTime`) is not
  diagnostic once anyone has byte-copied a save** (`Copy-Item` produces the
  same shape). A stray ever returning re-opens `EF-051` and this clause with it.
  ⚠️ **HOLD 2026-08-12 (owner action, deliberate and temporary): Steam Cloud is
  back ON** — the owner re-ticked it for an independent test of their own and
  *"will inform an agent when I turn it back off"*. While it is ON the restore
  mechanism is ARMED: close-outs record **"deleted, listing verified" — never
  "gone"** — and a returning stray is EF-051's measured mechanism, owner-armed
  (attribute it, inventory it for the post-untick cleanup, never file it as a
  finding). This is a dated suspension of the retirement, not a re-opening;
  the retirement resumes when the owner reports the re-untick and one
  post-untick listing verifies.
- ⛔ **Attended-sitting classes from `corun-batch-1` (2026-08-05; 8-entry
  ledger, first BATCHED attended sitting — the classes the unattended ledger
  could not see). Every attended brief guards against these:**
  1. **Prep re-verifies every briefed entry's status against
     `PLAYTEST_ARCHIVE.md`, not the entry alone** — "recorded facts are claims
     too" RECURRED despite being a standing rule: D07's entry was 5 days stale
     against the archive, prep inherited it, wrote a false SKIP line, and the
     brief repeated it to the owner twice before the owner corrected it from
     memory. A guardrail that failed twice is a broken guardrail; the archive
     cross-check is the repair.
  2. **Every measure moment names the instrument that FINDS its subject**, and
     prep confirms the subject still exists at sitting time — M1 was budgeted
     3 minutes and consumed ~25 because its measured fixture (23 Seniors
     against 31 free slots) had evaporated and no instrument could locate a
     replacement subject among 184 candidates.
  3. **Instruments added mid-chain obey the same witness discipline as legs.**
     The sitting's own reader printed "PREDICTION 10 FALSIFIED — a DEFECT to
     file" twice off single snapshots with no settling window, and a
     before/after helper stored whatever `SelectedObj` happened to be
     (a `LifeSupportGridElement`) without a type check. Both are the
     liveness-witness rule applied to legs but not to the day's own tooling.
  4. **The rig has no input path into a running game** — a console-driven
     attended sitting means the owner types every line, which the
     measure-moments model does not count. Until an input path exists, an
     attended brief's estimate must budget the console driving, not just the
     eyes/hands moments.
  5. **A parked `.ps1` needs a BOM** — PS 5.1 reads a no-BOM `.ps1` as ANSI
     and em-dashes break the parse (exact mirror of the earlier
     BOM-where-unwanted defect; the same file class fails in both directions).
  6. **Static-audit sweeps over-claim**: two scripted audits produced four
     distinct false-positive classes; only per-candidate source reading may
     file. Claim only what was read.
- ⛔ **Attended-sitting classes from `corun-batch-2` (2026-08-10; 14-entry
  ledger, 0 the game's fault — and rules 1 and 3 above BOTH recurred: prep
  inherited nothing and still briefed three wrong facts, because the failures
  were its own readers, not staleness). Every attended brief also guards
  against these:**
  1. **Every owner-typed console line is pre-flighted for THREAD CONTEXT, not
     just resolution** — four `Sleep()`-carrying entry points were briefed
     bare, and the bare console has no thread context (`PLAYTEST_HELP.md`);
     a resolution gate cannot see this. The `*r` prefix is part of the
     briefed line, never assumed.
  2. **The brief names the LOAD MECHANISM for every staged copy** —
     `Copy-Item` duplicates the display name, so staged saves are
     indistinguishable in the in-game load list; loading is a console
     `CB2.Load("<filename>")` line, and the brief budgets it.
  3. **Engine-name resolution is part of the pre-flight** — three reader
     defects in ONE function (`DefenceTowerBase`→`MDSLaser`, a `MapGet` key
     returning non-table, a guessed field name) each printed a plausible
     zero forever, and a gate that only resolves the harness's own namespace
     (G1) sees none of them. Every engine label/key/field a reader consumes
     gets one live read at confirm time.
  4. **A leg whose measure crosses its own save takes a reading IMMEDIATELY
     before the save, inside the same call** (run 1 of the keystone was void
     for want of one — and cost the leg a full re-run); **a leg that ANSWERS
     a popup counts the outcome's named target BEFORE answering** (the reply
     text names it for free; only a leftover save rescued the card).
  5. **Save liveness is witnessed by the file system, not the API** —
     `Savegame.ListForTag` regressed from proven (57→58) to non-table on the
     same build six days later ([[EF-049]]). On-disk size/mtime + load-back.
  6. **Absence verdicts never come from a mid-session log read** — the engine
     flushes a large tail only at exit ([[EF-047]]); a mid-sitting instrument
     recorded "zero output" whose five lines are all in the final log. Read
     for PRESENCE mid-session; read for ABSENCE only in the archived file.
  7. **A process-mutation leg states its RESTART requirement, and a
     `ReadConditions`-class gate precedes every post-mutation reading** — a
     Mod-Manager disable without a full restart leaves code live with its
     permanent gone (D13's fourth OFF state); the gate is the only reason a
     clean log of the pack RUNNING was not banked as a clean uninstall.
     ⛔ **AMENDED 2026-08-11, after this rule failed a second time: THE GATE
     RUNS AT THE TOP OF EVERY RUN, AND IT MUST *STOP* THE RUN, NOT MERELY
     PRINT.** As written it bound a reading taken after a mutation *inside* a
     sitting; it said nothing about a process that simply STARTS in the mutated
     state because a previous sitting left it there. `unattended-2` run 1 did
     exactly that — `corun-batch-2`'s leg T had disabled the pack the day
     before, `ReadConditions` printed `pack=0/0 active`, and the payload carried
     on for six more steps taking readings about code that never ran. **A gate
     whose only output is a line in a log is not a gate**; the same rule failing
     twice in two different ways is the rule being under-specified, not the
     sessions being careless. Mechanised in the run harness as
     `RequirePackLoaded`, whose default is to stop.
  8. **Source line numbers in a brief are marked Src-verified or
     trust-carried** — an unmarked line number reads as verified and is not.
  9. **A brief that wants a module dark states HOW it goes dark**: the
     `SMROptInPack_Disabled` console veto covers only D12/F97-class modules —
     **D03/D07 consult only `IsActive`** (owner decision 2026-08-10: the limit
     is recorded, not coded; a leg using the lever there silently runs live
     and reads as a fix failure).
- ⛔ **Attended-sitting classes from `corun-pt15` (2026-08-11; the mystery
  sitting's ledger, 0 the game's fault). Every attended brief also guards
  against these:**
  1. **No stop-orders while a time-sensitive gate is open.** An agent
     instruction to hold ("STOP — do not answer yet") is an INTERVENTION in
     game state, not a pause: the wisp-choice popup does not hold game time,
     the clock ran from night into afternoon while the agent read source, and
     the organic reading died on an empty trap (`Change(0)`, APPLICABLE=false).
     Before asking the owner to hold anything, read the clock and the gate's
     own timeout behaviour — or take the reading first and hold afterwards.
  2. **An owner-facing instruction that depends on UI state is marked
     eyes-verified or source-derived** — second occurrence of the class that
     produced F85's dead F9-rebind advice: this chain's brief and payload menu
     both said "call TrapRead BEFORE the choice", which is impossible at the
     keyboard (the choice modal locks the console — owner, verbatim, on the
     F07 entry). A source-derived instruction is a claim; the brief says so.
  3. **Every owner verbatim spoken at a measure moment is pushed through the
     harness note primitive (`*.Note(...)`) the moment it is spoken.** This
     sitting archived one of four owner quotes (F85's); the other three exist
     only in the session transcript, and the terminal audit had to rule on a
     `tested` grant whose verdict the archived log cannot show. Transcript
     quotes remain quotable — chat is where the owner speaks, and owner
     rulings have always been recorded from it — but a log-resident quote is
     re-readable forever, and the sitting prompt mandates the relay.
- ⭐ **Adopted 2026-08-11 (owner — `DOC_STRUCTURE_REVIEW` R4 + R7; R9/R14
  dropped). Two binding evidence rules for every leg and entry:**
  1. **R4 — a state-transition claim carries a save/reload ROUND-TRIP step.**
     "X changed and stays changed" is two claims; the second needs the
     round trip taken and read, or the entry says PRE-RELOAD ONLY.
  2. **R7 — a verdict evidences its EFFECT, not its execution.** "The call
     returned ok" or "the pass ran" is not a PASS; the reading that shows the
     intended effect (the count moved, the state persisted, the line printed)
     is. A verdict without an effect reading is demoted to an execution note.
     ⚖️ *(Amended 2026-08-10: the sitting's "no `ModTools\Src` on this
     machine" was WRONG — Src exists at
     `A:\SteamLibrary\steamapps\common\Project Spark\ModTools\Src`; the
     Relaunched Steam installdir is literally `Project Spark` (EF-014), which
     is why every folder-name search missed it. Live Src checks ARE available
     to sittings; the marking rule stands because trust-carried lines still
     occur.)*

**Checklist convention:** riders whose precondition is this mode are tagged
**TAKEABLE IN a co-run** (a rider class alongside TAKEABLE WHEN). Sessions
scoping work route "needs hours of observation" items there instead of parking
them.

**The rig's capability envelope** (measured 2026-08-04, co-runs #0 and #1 —
four launches; run procedure and cost model: `PLAYTEST_HELP.md` "The co-run
rig". The founding spec, `CORUN_RIG_SPEC.md`, was consumed at chain close and
survives in git — `git show 93088ba:docs/agent/prompts/corun-rig/CORUN_RIG_SPEC.md`):

- **PROVEN by execution:** agent-driven Steam launch (no picker interposes;
  launch→log 1–5.2 s across four launches, no room for a human click);
  staged-copy load by FILENAME from a `CreateRealTimeThread`; a loaded save
  arrives PAUSED and readiness is synchronous with `LoadGame`'s return;
  speed set/read-back; scripted state reads; amplification loops (20-cycle
  forced-open loop, 300-sample 5 Hz poll, 238 s 1 Hz poll); multi-launch
  sittings with each run authored from the previous one's log; per-line
  flush + mid-session agent log reads.
  ⭐ **PROVEN 2026-08-04 by unattended-1 cycle 0, the primitive nobody had ever
  called: an in-run SAVE.** `SaveGame(display, {savename=…, silent=true,
  no_screenshot=true})` from a real-time thread returned `err=false`, the file
  appeared to `Savegame.ListForTag("savegame")` (57→58 tagged files), and
  `LoadGame` brought it back live with the pack still reading 81/81 — a full
  write→list→reload round trip, log
  `docs/archive/u1c0_Mars.exe-20260804-16.37.16.log`. ⛔ `save_as_last` is never
  passed (it would repoint the owner's *Continue* button); deletion stays
  agent-side with the game closed, because the mod environment has no
  file-delete primitive at all (`io`, `os` and `AsyncFileDelete` are all
  `ModEnvBlacklist` keys). **Save/reload legs are now inside the envelope.**
  ⭐ **PROVEN 2026-08-04 by the full unattended-1 batch: the 7-cycle
  unattended shape itself** — 7 good launches ≈ 9 min of machine time, owner
  cost = the kickoff word. Component costs off the logs' own `Lua` markers
  (EF-045's instrument): boot→menu **19.0–19.4 s** (the largest fixed cost —
  batch legs per launch), cold load **9.6–10.1 s**, repeat load same map
  **5.8–6.0 s**, save **0.58–0.63 s** across 5 saves.
- **Still UNPROVEN (say so when planning):** the watchdog under a real wedge
  (proven present, never fired — ⛔ unattended-1's 8-minute unarmed stall was
  a probe that never STARTED, so that run is NOT the watchdog's first test
  and must not be quoted as one). **DESCOPED, not pending:** Mod-Manager /
  main-menu driving (blacklisted — the enable click stays human, P8 shape),
  MarsDebug unattended automation (modal asserts make debug legs attended BY
  CONSTRUCTION), OS-level input injection.
- **Stays ORGANIC-ONLY by rule:** reachability claims, organic-witnessed
  evidence upgrades, feel/severity judgments, the owner's own campaign.

**Routing any piece of work — unattended, co-run, or playtest (the triage;
owner asked 2026-08-04).** Start at the cheapest mode that does not weaken
the evidence — the owner's time is the objective, quality the constraint —
and route UP only for the moments that genuinely need a human:

1. **UNATTENDED** — every measure in the leg is a log-readable fact on a
   staged copy: scripted state reads, forced-mechanism traces, amplification
   counts, A/B probe-suite legs. No eyes, no hands, no judgment anywhere in
   the measure. Evidence ceiling: MECHANISM / probe-verified — never
   `tested`, never an organic upgrade.
   ⚖️ **Execution shape (owner rule, 2026-08-04): a truly unattended item
   runs as a TWO-PROMPT chain — a volume-tier (Opus) prompt executes, a
   top-tier (Fable) prompt audits adversarially against the archived logs.
   Batched unattended work runs as a FULL chain: volume-tier prompts
   throughout (top tier mid-chain only where something is genuinely
   complicated), always closed by a terminal top-tier audit.** Placement
   lives in filenames; prompt bodies stay model-neutral
   (`CHAIN_METHOD.md` §2.10 / §4.0). Chain mechanics — inbox/outbox,
   self-consumption, folder-empty done-condition — apply at every size.
   **Two hand-off conventions (owner, 2026-08-04):** (a) the terminal
   audit's owner report ENDS with the kickoff line for the next queued
   chain (source: STATE's NEXT pointer; if nothing is queued, say so) — the
   owner starts every chain by hand, and a report that does not say what to
   start next leaves them searching. (b) **Mid-chain escalation offer:** if
   an item routed unattended turns out to need eyes or hands after all, the
   discovering prompt routes it to the owner WITH an offer — insert an
   attended co-run prompt into this chain immediately before the terminal
   audit (measure-moments list, prep per rule 5, cost stated). Owner
   accepts → the prompt is authored and gets a manifest row, and the chain
   ends with a prepped sitting; owner declines or does not answer → the
   item becomes a **TAKEABLE IN a co-run** rider on the checklist and the
   chain continues without it. The terminal audit is the last prompt
   either way.
2. **CO-RUN** — scriptable except for NAMED moments needing human **eyes**
   (witnessing behaviour), **hands** (cursor parking, launch or Mod-Manager
   clicks, console lines at unscheduled moments), or an in-the-moment
   **judgment call**. The owner attends those moments only; batch every
   co-run-ready rider and ride-along read into the same sitting.
3. **PLAYTEST (attended sitting)** — the evidence itself must be a human at
   the keyboard: `tested` grants, behavioural/feel/severity claims (the
   EXTERNAL VALIDITY rule), win-calls, anything judged live and throughout.
4. **ORGANIC-ONLY stays a rider** (TAKEABLE WHEN): reachability claims,
   organic-witnessed evidence upgrades, symptoms that must arise in real
   play. Never scheduled, never rigged — the situation arises or it doesn't.

Tie-breakers: if forcing the upstream would answer a DIFFERENT question than
the one asked (reachability, upgrades), the item is 3 or 4 no matter how
cheap the rig makes the forced version. If the only human need is hands for
seconds, that is a co-run moment, not a sitting. When scoping any new test,
name its mode in the brief; a leg that cannot say which mode it is has not
said what its evidence will be.

**Sign-off tiers: ✅ ADOPTED 2026-08-04 (owner, in their own hand on the
checklist — `----Approved` on the tiers item; integrated by the unattended-1
terminal audit).** Standing policy for every leg from here on:

- **Tier A — WITNESS.** The owner's eyes genuinely add information the log
  cannot carry; they attend the measure moment. Unchanged from before.
- **Tier B — EVIDENCE CARD.** Log-demonstrable; the owner quick-reads a
  one-screen card — scenario, forced-vs-organic, the raw before/after log
  lines, run conditions, the one-sentence falsifier — and OKs it. Sub-class
  **HANDS-ONLY**: a leg needing the owner's hands (a click, a cursor park)
  but not their eyes — they do the named act, then read the card as Tier B.
- **Tier C — DELEGATED.** Mechanically self-verifying (the probe-suite
  class): ships on the suite verdict; the owner gets a one-line digest per
  batch and keeps the veto.
- **Visible demotion:** when a designed-A item's card turns out strictly
  stronger than the eyes, the demotion is stated ON the card and applies to
  the NEXT instance — never silently.

⛔ **What adoption does NOT carry, in the item's own words:** *"`tested` still
means a pass at the keyboard per WORKFLOW, and no already-granted status is
reclassified."* Neither moves. ⚠️ The tiers are a *sign-off* axis, not this
routing axis: the triage above says who is present during a leg; the tiers
say what the owner reads afterwards. Owner-facing record of the decision:
`PLAYTEST_CHECKLIST.md` "Decisions waiting on you", 2026-08-04.

## Release steps

> ## ⚠️ ADAPTED — what applies to THIS mod, bullet by bullet (2026-08-12, split)
>
> The section below is the donor's, kept in full rather than rewritten, because
> the shape of a release is identical and the traps in it were paid for. Read it
> with these five corrections:
>
> 1. **APPLIES:** owner preview/screenshots/portal pass · `metadata.lua` version
>    + `last_changes` · the Mod-Editor upload round-trip rule (`items.lua` and
>    `metadata.lua` `code` change together, same order) · "the TestKit must NOT
>    be uploaded" · the probe-number recount in any player-facing claim · the
>    ChoGGi/LukeH prior-art credit.
> 2. **⛔ ADD, and it is this mod's release blocker:** the DISPLAY NAME is still
>    a placeholder. Sweep every site in `agent/PROVENANCE.md` §3 in one commit
>    before upload, and state in the description that the mod works with or
>    without the Community Fix Pack.
> 3. **N/A HERE — `MOD_DESCRIPTION.md`**: the frozen draft, its four
>    `[DRAFT NOTE]` markers and the "judgment calls" wording item live in the
>    FIX PACK's `docs/archive/`. This mod needs its OWN description, written
>    from `agent/bugs/`, and the owner owes its wording exactly once.
> 4. **N/A HERE — the four save-exit gates** below (uninstall procedure, the
>    D13 save-rescue artifact, the residual disclosure, the post-update
>    five-shape re-enumeration) are the FIX PACK's release blockers. ⚠️ **But
>    D13 covers BOTH mods by owner ruling — one artifact** — so this mod's
>    residue is inside that scope and its numbers must be re-derived over THIS
>    tree, never inherited.
> 5. **⛔ ADD:** ship-testing is TWO configurations, not one — with the fix pack
>    installed and with it absent (FIX_POLICY §8). A release note says which fix
>    pack version it was tested beside.
> 6. **⛔ ADD:** the Drone dials' uninstall instruction ("set both dials to base
>    before uninstalling") is MANDATORY in the store description — a non-base
>    dial persists its boost into a save loaded without this mod.

- Owner tasks first: preview image (PDX ≤2 MB / Steam ≤1 MB), screenshots,
  portal rules check for console publishing (`docs/archive/AUDIT_FINDINGS.md` plan 2.5).
- metadata.lua: bump `version_major`/`version_minor`, refresh `last_changes`.
  `short_description`, `ignore_files`, `optional_mod` are already in place
  (audit 2.1). `lua_revision` stays 350453.
- MOD_DESCRIPTION.md: delete the `[DRAFT NOTE]` markers; do NOT promise the
  ClassicRockets export half; sync the fix list with agent/bugs/ statuses.
  ⭐ **Add the "judgment calls" section** (owner ADOPTED the relabel proposal
  2026-08-04: F55, F40, F73(b), F70, F97 presented as design-judgment repairs,
  not plain bugs) — ⚠️ **its wording is OWED BY THE OWNER** and must be asked
  for if it does not exist yet; the checklist line tracks it.
  **Recount the probe number** quoted in the "What we can promise, and what we
  can't" block — it moves whenever a wave file gains or loses a probe, and a
  stale number there is a false claim in player-facing text. Authoritative count
  is in `agent/STATE.md`.
- **Drone overhaul, if it has shipped by then:** its design-drift disclaimer is
  MANDATORY (owner requirement — spec in `docs/archive/DRONE_RESEARCH_BRIEF.md`). Do not
  publish the module without it.
- Upload via the in-game Mod Editor (Paradox Mods / Steam Workshop). The
  editor round-trip is SAFE since audit 2.2: items.lua carries one
  `ModItemCode` per Code/ file in metadata order, so SaveDef regenerates the
  same `code` list. If a Code/ file is ever added/removed/reordered, update
  BOTH metadata.lua `code` AND items.lua in the same commit, same order.
- The TestKit must NOT be uploaded.
- Credit ChoGGi (Fix Bugs) + LukeH (Martian Express) as prior art — and the
  prior-art survey (`docs/agent/reports/PRIOR_ART_SURVEY.md`) backs the save-safety claim in
  player-facing text.
- **Save-exit gates (owner, 2026-07-31 — release blockers alongside the fpk
  diff):**
  1. the **uninstall procedure** is published in MOD_DESCRIPTION ("update,
     load, save, then uninstall", backup-first) and is true (latched heal +
     rains migration shipped and verified);
  2. the **standalone save-rescue artifact** (`agent/bugs/` **D13**) is built and
     tested, ready to publish (the only console-viable remedy). ⛔ Its spec is
     GATED on Tier 1/2 landing and verifying — scoped against their measured
     output, never today's leak set. ⚠️ **A second shipped artifact doubles
     this checklist**: it needs its OWN metadata, preview image, description,
     PDX portal pass and console cert, plus a version-skew statement (which
     pack versions' residue it handles) and proof its own residue is zero —
     budget the release window accordingly;
  3. the **residual disclosure** (inert layer-2 residue; irreversible-history
     class) appears wherever save-cleanliness is claimed;
  4. after EVERY game update, alongside the fpk extraction diff, **re-run the
     five-shape exposure enumeration** (class-method / table-slot / global
     assignment / preset-field / own-thread) — a live game means persisted-body
     version skew is a standing failure mode, not a launch-time one.

## Authoring a prompt / job brief — required elements

Every brief written for another session (`*_PROMPT.md`, `*_BRIEF.md`,
`*_REVIEW.md`) must include these. They are not optional polish; each one exists
because its absence cost this project something.

**1. A live progress list — REQUIRED, and required to stay current.**

The owner reads the session's todo list to decide **when to step in** — whether
there is time to start a playtest, whether to wait, whether a job is nearly
done. A list that is created and then not maintained is worse than no list,
because it actively misleads that decision.

So every brief must instruct the agent to:

- **Create a todo list covering the whole job before starting.**
- **⚠️ GRANULARITY: one item per commit-and-verify unit — this is the rule that
  actually matters.** If a stage produces its own commit, or its own
  verification run, it is its own item. Never bundle several of those behind one
  checkbox. *Observed failure, Phase 4, 2026-07-31:* the list carried
  `S6a-d: Require migration in 4 waves` as a **single** item covering four
  waves, four commits and four legs — so the owner saw the list at S4 and the
  next time it moved it read "final phase", with no signal across the longest
  stretch of the job. Per-item discipline cannot fix a list that is coarser than
  the work.
- **If a stage turns out to contain more units than the brief anticipated,
  expand it in the list at that moment** — do not carry one checkbox through
  work you have already discovered is four things.
- **Mark each item complete the moment it completes** — before starting the
  next one, never as a batch at the end. "I'll tidy the list later" is the
  failure mode.
- Keep **exactly one item in progress** at a time.
- **Rewrite the list when reality diverges** — if a stage splits, grows, or
  turns out unnecessary, the list changes. A stale item is a wrong answer to
  the owner's question.
- Put **useful state in the item text** where it is short and stable (which
  stage, what the last verification read), so the list answers "where are we"
  without the owner reading the transcript.

**2. `git log` + `git pull` first**, and a named commit to check staleness
against — briefs go stale the moment another session commits.

**3. An explicit scope fence** — what is in, what is out, and what to do with
something interesting found out of scope (**file it, do not fix it**).

**4. Stop conditions** — the situations where reporting beats pushing through,
stated as permission, not as failure.

**5. What may NOT be claimed** — for any brief that ends in a verdict or a
certification. An agent that cannot cite evidence for a claim must say the
narrower true thing instead.

**6. Whether the brief deletes itself.** One-off jobs delete their brief on
completion (precedent: the popup audit). Re-runnable ones say plainly that they
do not.

**7. The stale-probe gate — for any brief that runs or records a test.** The
brief must instruct: run the probe sweep (the hard gate above) BEFORE testing,
put the sweep line in the todo list, and refuse to record results without it.
A brief that omits this is non-compliant; add the gate before running it.

**8. The read path, declared** (adopted 2026-08-03, standing-prompts redesign
O1). Name the files the job requires — file granularity, not folders — and the
index (`agent/bugs/INDEX.md` / `agent/facts/INDEX.md`) that finds more. "Read
the whole folder" is not a read path: every stale reading instruction the
restructure report catalogued was a folder-granularity one, and a brief that
names its files is one whose staleness the next session can check against git.

## `[FAQ]` — the tag for "a player will ask about this"

Owner intends to write an FAQ doc at some point. Rather than start one early
(and rather than let the material scatter), **tag the source of truth in place**
with the literal marker `[FAQ]` and collect it later:

```
grep -rn "\[FAQ\]" docs/ Code/
```

Rules that keep the tag worth having:

- Put it on the **entry that already explains the thing** — an `agent/bugs/` entry, a
  parked item, a module header. Never create a doc just to hold a tag.
- Tag **behaviour a player could reasonably mistake for a bug**, or a question
  the design deliberately answers "no" to. Not every quirk.
- A `[FAQ]` tag is **not work and not a promise** — it is a bookmark. Writing
  the FAQ is a launch-time task, and tagging things is not progress toward it.
- If the tagged behaviour is later changed or fixed, **remove the tag** in the
  same commit, or the FAQ inherits a stale answer.

Currently tagged (re-derived from `grep -rn "\[FAQ\]" docs/ Code/` on
2026-08-01 — the previous list named a tag in `MOD_DESCRIPTION.md` that did not
exist):

- D01's parked-rocket activation limitation — `agent/bugs/` D01 entry +
  `FUTURE_IDEAS.md` entry 2.
- The save-repair framework's honest limits — `FUTURE_IDEAS.md` entry 4.
- "Put the mod back" as advice for a damaged save, and its F88 caveat —
  `agent/bugs/` F88 entry.
- The uninstall procedure and the standalone save-rescue artifact —
  `agent/bugs/` D13 + `FIX_POLICY.md` §3a + `F86_EXECUTION_PLAN.md` Phase 5.
- **Why we make a fuss about the savegame footprint at all** — the documented
  engine behaviour (mod code is serialised into saves by design) and the
  community norm we deliberately exceed: `MOD_DESCRIPTION.md`, added
  2026-08-01 from `PRIOR_ART_SURVEY.md` §1/§2/§4.
- **The no-precedent uninstall claim** — `MOD_DESCRIPTION.md`, added
  2026-08-01 but **written conditionally and marked do-not-publish until F86
  Tier 1 lands and verifies** (`PRIOR_ART_SURVEY.md` §6). A tag on a claim
  that is not yet true has to say so.
