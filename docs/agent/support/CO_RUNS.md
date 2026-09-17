# Co-runs — attended experiment legs with the labor inverted (adopted 2026-08-04, owner)

**Binding when a batch is tested attended.** Moved out of `docs/agent/WORKFLOW.md`
on 2026-09-17 so that document is a routing surface again: at 27,546 B this section was
37% of it and 49% of its whole gap against the fix pack, whose own WORKFLOW carries the
co-run protocol as a four-line pointer to `support/CO_RUNS.md`. ⛔ **The body below is
VERBATIM — nothing was rewritten, summarised or dropped in the move.** Sign-off tiers
stayed behind in `WORKFLOW.md` as their own section, exactly as the donor keeps them,
because they bind every leg and not only a co-run.

⚠️ This is BINDING PROTOCOL, not a report. It is pulled rather than pushed — read it when
a leg is actually being run attended. `docs/agent/reports/` is explicitly *not* authority
(`WORK_PROMPT.md` §5); this file is, which is why it is not filed there.

---


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
     bare, and the bare console has no thread context (established in the fix
     pack's `PLAYTEST_HELP.md`, dissolved 2026-09-15 — `git show c91310f^:docs/PLAYTEST_HELP.md`);
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
four launches; run procedure and cost model were in the fix pack's
`PLAYTEST_HELP.md` "The co-run rig", dissolved 2026-09-15 —
`git show c91310f^:docs/PLAYTEST_HELP.md`. The founding spec, `CORUN_RIG_SPEC.md`, was consumed at chain close and
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
