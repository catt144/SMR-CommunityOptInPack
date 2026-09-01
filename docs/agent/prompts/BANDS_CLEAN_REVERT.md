# BANDS_CLEAN_REVERT — one-off: can the drone overhaul add priority bands 4–5 AND revert to vanilla cleanly on its own, with no Save Rescue mod?

**One-off. Deletes itself in its close-out commit** (`git rm` this file). Any
model; the owner picks. **Start with `git log --oneline -10` + `git pull` in
BOTH repos** (`C:\Dev\SMR-OptInPack`, `C:\Dev\SMR-BugFixPack`). Staleness
anchor: written 2026-09-01 at `c5e6340` (opt-in) / `c337e5c` (fix pack), the
day the owner reopened the drone project after the 08-31 unfreeze. Verify
against `git log` before trusting any specific below.

> ⛔ **This is a research-and-design job. NO module is built or changed. NO
> persisted string is touched. NO real save is loaded by any experiment.** The
> D06 design decision stays the OWNER's (fix pack `prompts/DRONE_PROJECT_PROMPT.md`
> §3) — this job changes the INPUTS to that decision, and may recommend, but
> does not make it. The only file this session deletes is itself.

## Why — the problem, stated for someone who has never seen it

**The product.** `Opt_DroneOverhaul` (D06) is the biggest module in this mod:
an opt-in redesign of how drones choose work. Its shipped v1 (a "closest fleet
claims first" gate) was measured as inert — hauling is 88% of repair time and
v1 exempts hauling. The owner ruled a **rebuild** on 2026-07-31. The rebuild's
shape (owner-directed, NOT approved to build) is a **priority-band scheme**:

| Band | Set by | Contents |
|---|---|---|
| **5** | auto | *malfunctioned* life-support producers (MOXIE, Electrolyzer, Water Extractor, Micro-G Water Extractor, Moisture Vaporator) + the grid/dome tier vanilla already elevates |
| **4** | auto | every other *malfunctioned* building |
| 3 / 2 / 1 | player | supply allocation — the arrows, default 2 |
| 0 | engine | storage depots |

Plus a data-patched default of 3 for the four food-service buildings. The
rationale is on the D06 entry and in the fix pack's `DRONE_PRIORITY_SYSTEM.md`:
vanilla's whole priority system is five integers `-1..3`; ordinary building
maintenance has no override and inherits the player's supply arrows; the devs'
own rule ("life-support-critical repairs are urgent") was applied to pipes and
dome fractures and never to the buildings that make the air.

**What the 2026-07-31 sitting proved, and what it found.** The C matcher
**honours** bands 4–5 (Q1 — on a NEW game, haul and work legs both measured).
But three constraints stand between the scheme and shipping:

1. **Q2 — hub queue tables are PERSISTED, allocated once at construction
   (`TaskRequestHub:Init`, `CommonLua/TaskRequest.lua:242-256`) and never on
   load.** Widening the range on an existing save made vanilla's own loops
   index `supply_queues[4]` = nil in every `FindTask`, froze every drone and
   wrote tens of millions of log lines (fix pack `DRONE_PRIORITY_SYSTEM.md` §8).
   ⇒ any real deployment must top up every existing `DroneControl` (hubs,
   rockets, RC rovers — the mix-in walk, `EF-053`) before anything calls
   `FindTask`.
2. **§9 — uninstall is silent but LOSSY.** A widened save loads into vanilla
   with zero errors (narrow loops over wide tables never visit keys 4–5), but
   any request sitting at 4/5 at save time is **stranded**; the heal path
   (`OnMsg.DepositsSpawned` → re-register every hub) **expires on a
   fully-scanned map**, which is exactly when a player removes a mod.
3. **§10 — the duplicate leak, with the mod INSTALLED.** `DroneControl:RemoveBuilding`
   loops `for priority = -1, MaxBuildingPriority` over a **file-local pinned at
   3** (`Lua/Buildings/DroneControl.lua:8`, `:735`) that mod code cannot reach, so a
   routine re-registration heals the building but never removes its old band-4
   entry — measured `4 → 6`, n=1. Bands 4–5 accumulate dead references without
   bound.

The three options written up for the owner (fix pack `DRONE_PROJECT_PROMPT.md`
§3): **(1)** keep bands 4–5 + a `LoadGame` sweep + a FULL REPLACEMENT of
`DroneControl:RemoveBuilding` + the cleanup mod as the uninstall remedy;
**(2)** work inside `-1..3` (clean data, loses the 5-vs-3-vs-player distinction);
**(3)** a merged-view overlay — bands held in non-persisted mod tables, merged
into what `Request_FindTask` sees — unproven and unscoped.

**What we are trying to solve — the question of this job.** The owner wants
the bands **and** a module that *cleans up after itself*: turning it off in Mod
Options = vanilla instantly; disabling or uninstalling the mod = a save that
loads in vanilla with **no errors, no stranded work, no orphaned data, no
captured frames, no closures, nothing a second mod has to fix** — without
requiring a new game. `SMR-CommunitySaveRescue` exists (fix pack D13, `tested`
08-14) and it is a *remedy*, not a licence: the standing rule is *make the mod
clean* (D06 entry, the cleanup-mod conditions; `FIX_POLICY` §3a). Since 07-31
the project has learned a great deal about saves, frames, seams and flattening
(`EF-019/022/023/053/054/058/059/060`, F86's whole arc, the L3/L8 lenses, the
Save Rescue's own inventory of what residue actually looks like). **Has any of
it opened a route to "bands 4–5 with clean revert" that the three options
missed?** And — asked deliberately — **is there a mechanism nobody has proposed
that gets the urgency the bands are for by a different road?**

## 0 · Orient and set up

1. `git log --oneline -10` + `git pull`, both repos. Read this repo's
   `docs/agent/STATE.md` whole (the two bans, the drone unfreeze, open owner
   items 83/84/87).
2. **Create the todo list before starting** — one item per section below and
   per commit; one in progress at a time; marked the moment each completes;
   rewritten when the job diverges (`WORKFLOW.md` "Authoring a prompt" element 1).
3. **Stale-probe gate** — this job is DESK-ONLY by default and records no test.
   ⚠️ If the owner authorises an experiment (§5), the gate binds first:
   `grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/` in the todo
   list, CLEAN or every hit declared by the experiment's design; every result
   commit carries a `PROBE SWEEP:` line (`WORKFLOW.md` "Probe hygiene"). Also:
   `tasklist | findstr Mars.exe` as its own step before touching loadable code;
   throwaway save or new game ONLY — the 07-31 incident broke a live colony.

## 1 · Read path — file granularity; the two INDEX files find more

**This repo (`SMR-OptInPack`).** `CLAUDE.md` (ban 1: any NEW persisted name is
save contract forever — this bounds every candidate; ban 2). `agent/FIX_POLICY.md`
§1 (technique tiers, §1.5 replacements), §3 + §3a (save safety — the hard rule
and the layer ordering), §5 (opt-in shape), §6. `agent/bugs/D06.md` whole (the
plan of record: rebuild decision, all four gate answers, the cleanup-mod
conditions, the B2 A/B and its caveats, the F86 Site 2 repair). `agent/bugs/D09.md`
(a module that DOES revert cleanly by id — the reconcile-on-load pattern, and
the one residue it leaves). `agent/reports/DRONE_OVERHAUL_OPTIONS.md` (A–H, the
D08 layers and their risk table, §I/§K). `agent/reports/SEED_LOGISTICS_HANDOFF.md`.
`docs/FUTURE_IDEAS.md` #7. Facts — mandatory opens: `EF-002` ("OFF" is three
things), `EF-019` (game-time threads persist), `EF-022` (a closure on an object
enters the save), `EF-023` (what a save captures — the real rule), `EF-053`
(mix-in class walk finds every `DroneControl`), `EF-054` (inter-mod load order),
`EF-058` (flattened-class trap + its scope clause: file-scope installs
propagate), `EF-059` (depot last-resort rule), `EF-060` (the `FindTask` seam +
the flag-constrained finders). Scan `agent/facts/INDEX.md` for anything else
about persist, threads, `OnMsg`, queues. `Code/Opt_DroneOverhaul.lua` (the v1
seams and the F86 header). `Code/00_Core.lua` (`Register`, `IsActive`, the
`_Disabled` veto, `OnDataReady`). `tools/l3_save_footprint.py`,
`tools/l2_reload_sim.py`, `tools/blocking_analysis.py` (what each can prove
about a candidate at the desk; `agent/PROVENANCE.md` §6).

**Fix pack (`SMR-BugFixPack`).** `docs/agent/prompts/DRONE_PROJECT_PROMPT.md`
(§2 settled points, §3 the options, §8 what may not be claimed).
`docs/agent/reports/DRONE_PRIORITY_SYSTEM.md` — §3 (priority baked at insert),
§6 (landmines, esp. 4: instance-level flattening of `GetPriorityForRequest`),
§8 §9 §10 whole. `docs/archive/DRONE_RESEARCH_BRIEF.md` (the disclaimer spec
and the ONE-playtest rule). `docs/agent/bugs/F86.md` (frames in saves, the
per-site gate, PT-58). `docs/agent/bugs/D13.md` + `docs/agent/reports/D13_EXPOSED_SET.md`
(what residue the project has actually catalogued). `docs/agent/reports/SAVE_SAFETY_REDESIGN.md`
(the adopted layer ordering 3→2→1 and the tear-down-on-save discussion).
`docs/agent/reports/L3_SAVE_FOOTPRINT.md`, `L8_ADVERSARIAL_MAP.md`,
`PRIOR_ART_SURVEY.md` (what other mods do about revert — prior art counts).
`docs/agent/bugs/C47.md`, `C48.md` (the seed case — the same seam).
`docs/archive/PLAYTEST_ARCHIVE.md` ~line 3000 (the PT-52 snapshot: the B2
protocol and the CAN/CANNOT judging lists — the future verification leg is
derived from them). `docs/PLAYTEST_CHECKLIST.md` "Decisions waiting on you"
items 83, 84, 87.

**Save Rescue (`C:\Dev\SMR-CommunitySaveRescue`).** `README.md` and its `Code/`
— read it as an inventory of *what residue the project already knows how to
find and remove*. A candidate whose residue the Rescue would have to learn is a
candidate that fails this job's question.

**Game source — read-only truth, cite `file:line`, re-derive ROUTES not just
citations** (`A:\SteamLibrary\steamapps\common\Project Spark\ModTools\Src`, build
`1.0.7.396349`): `CommonLua/TaskRequest.lua` (`:15-30` bounds + `ClassesPreprocess`;
`:53-59` class member `priority`; `:170-187` `SetPriority`/`GetPriorityForRequest`;
`:242-256` `Init`; `:310-320` `_InternalAddRequest`; `:344-374` `RemoveBuilding`/
`_InternalRemoveRequest`); `Lua/_TaskRequest.lua` (`:54-83` the finders and
`FindTask` — SPOT-CHECKED 2026-09-01 while writing this brief: `:71` is
`local Request_FindTask_C = Request_FindTask`, i.e. the C matcher is a **global,
reachable from mod code**, and `:73-76` passes **only** `priority_queue`,
`supply_queues`, `demand_queues`, `under_construction`, `restrictor_tables`,
`ResourceUnits`, the agent's `unreachable_buildings`, `flags`, `agent` — **no
priority bounds**. So how C discovers the key range (table keys? the `const`
group? a compiled constant?) is the open question under option 3 — re-derive
it, do not inherit this note); `Lua/Buildings/DroneControl.lua` (`:8`, `:107-123` deficits,
`:315-325`, `:692-693` `AddBuilding`, `:730-760` `RemoveBuilding`, `:779-785`
`ReconnectTaskRequesters`); `Lua/RequiresMaintenance.lua` (`:41`, `:82`, `:94`,
`:190`, `:418-426`); `Lua/SupplyGridBreakable.lua:48-56`; `Lua/Passage.lua:485-491`;
`Lua/Units/Drone.lua` (`:560-640` Idle, `:879-896` CleanUnreachables, `:898-938`
Work, `:940-1014` PickUp); `Lua/DroneHub.lua:188-198` (`DepositsSpawned`);
`CommonLua/Savegame.lua` (`:1043` `Msg("SaveGameStart", params)` and what runs
between it and the persist walk; `SaveGameDone` likewise); `CommonLua/Core/persist.lua` (`:157-165`
permanents; how tables, functions and thread stacks are gathered);
`CommonLua/Classes/Mod.lua:1430-1440` (`ModMsgBlacklist`); `CommonLua/Core/classes.lua`
(~`:988` flattening, `OnMsg.Autorun`). Anything else a candidate touches.

## 2 · The rubric — what "clean revert" means here, row by row

Every candidate mechanism gets THIS table, every cell filled from a citation
(Src `file:line`, an `EF-` fact, a measured log) or marked **UNKNOWN — needs
experiment E-n** (§5). No blanket claims over a table.

| row | question | pass condition |
|---|---|---|
| R1 | Mod Options toggle OFF | behaviour byte-vanilla on the next call; nothing left elevated |
| R2 | `SMROptInPack_Disabled` veto | same as R1 (file-scope installers: `EF-002`) |
| R3 | Mod-Manager disable / uninstall, save made with bands ACTIVE | vanilla load: **0 `[LUA ERROR]`**, no `Unpersist missing permanent` that matters, no captured frame (F86), no closure on any object (`EF-022`), no request stranded in a key vanilla never iterates, no widened table that vanilla could ever index-nil on |
| R4 | Existing saves (hubs, rockets, rovers built under vanilla) | works without a new game; the Q2 top-up is safe and happens before any `FindTask` |
| R5 | Persisted footprint | ZERO new persisted names (ban 1). `tools/l3_save_footprint.py` still reads exactly the five. If a candidate needs a marker, it fails this row — say so |
| R6 | Duplicate leak (§10) | closed, and by what: wrapper / replacement / never entering the real tables |
| R7 | Save Rescue dependency | the Rescue has NOTHING to do for this module. If it must learn something, name it and the candidate fails the job's question |
| R8 | Patch-rot exposure | which vanilla functions are wrapped (chained) vs replaced (§1.5); which are hot (`FindTask` fires constantly — per-call work must be tiny, `EF-060`) |
| R9 | Flattening | `EF-058`: installed at file scope pre-flattening, or on every carrier class; how proven |
| R10 | Preserves the design's DISTINCTION | 5 vs 4 vs player-3 still distinguishable to the matcher — or state what collapses |
| R11 | Interaction with F77, D09, the fix pack's wrappers on the same seams (`EF-054`), shuttles/rovers/rockets sharing `DroneControl` | named or "none, because …" |

## 3 · Part A — the evidence delta since 2026-07-31

Before designing anything, list **every fact, tool, ruling or measurement
dated after 2026-07-31** that bears on the bands question, one line each with
its source, and say for each what it changes about options 1/2/3. At minimum
consider: `EF-023` (the real capture rule) and F86's per-site repair pattern
(synchronous seams); `EF-058`'s scope clause (file-scope installs propagate
through flattening — this may retire §6 landmine 4 for a class-level
`GetPriorityForRequest`); `EF-053` (one walk reaches every `DroneControl`);
`EF-060` (the finders accept `required_flags`/`ignore_flags` — a second
dimension the matcher already honours); `EF-059`; the `SaveGameStart` correction
(mods DO get a pre-save hook — the tear-down-on-save scheme is implementable);
the Save Rescue's existence and inventory; the standalone split (this mod no
longer shares a configuration matrix with 68 default fixes); the l2/l3/l8 desk
instruments; the 08-31 unfreeze. **A "no delta" answer is a valid answer** —
say it plainly rather than inflating a fact into a route.

## 4 · Part B — the candidates. Re-examine the three, then brainstorm past them

**B1 — re-examine, with the delta applied.** For each of options 1/2/3 fill
the §2 rubric. Specific checks the record already asks for and nobody has run:

- **Is the duplicate leak really unreachable by a wrapper?** `DRONE_PRIORITY_SYSTEM.md`
  §10 says "nothing smaller than a full replacement reaches the constant". But
  the trapped entries live in `hub.priority_queue[4]` etc. — plain Lua tables a
  post-wrapper on `DroneControl:RemoveBuilding` can iterate itself for
  `4..MaxBuildingPriority`, and `TaskRequestHub:RemoveBuilding` /
  `_InternalRemoveRequest` loop the WIDENED module locals. Read `:730-760` and
  say whether a chained post-wrapper closes the leak without replacing anything.
- **Tear-down-on-save.** With `OnMsg.SaveGameStart` reaching mods: can the
  module re-file every elevated request into `-1..3` and drop keys 4–5 from
  every `DroneControl` BEFORE the persist walk, then rebuild after
  `SaveGameDone`? Read `Savegame.lua` for what runs between the message and the
  write, whether the message is synchronous, and whether game-time threads are
  paused. Cost per save = one `ReconnectTaskRequesters` per hub? Is that
  acceptable? Does it strand anything mid-command (a drone already claimed a
  band-4 request — what happens to its claim when the request re-files)?
- **The top-up on load** (R4): which `OnMsg` fires before any drone thread can
  call `FindTask` on a loaded save? Walk with `AllMapsForEach(true, "DroneControl", …)`
  (`EF-053`); add `[4]`,`[5]` tables; is the add itself persisted-state-safe
  (an empty widened table in a later vanilla load = silent, §9)?
- **Option 3's real cost.** `FindTask` hands `Request_FindTask` (a global)
  the three queue tables and NO bounds (`_TaskRequest.lua:71-76`, spot-checked
  above). Two readings, and the §8 incident does not separate them: C walks
  the table keys it is given, or C reads `const.TaskRequest.MaxBuildingPriority`
  itself. If keys: a wrapper can call the global directly with a **shadow view**
  (mod-side tables, transient, weak-keyed, widened) and the real hub tables
  never widen — R3/R4/R6 pass by construction, and the top-up disappears. If
  the const: say what that forces (the const must be widened globally, which is
  the §8 crash on any un-topped-up hub). E-4 decides it; design E-4 so one run
  distinguishes the two.

**B2 — brainstorm. Be creative here; this is what the owner asked for.** The
bands are a *means*; the end is "broken life-support gets fixed first, broken
things before routine hauling, and the player's arrows go back to meaning
supply allocation". Propose **at least eight distinct mechanisms** that reach
that end, including ones that abandon widening the range entirely. For each:
one paragraph of mechanism with the seam named, then the §2 rubric, then an
honest kill-or-keep. Seeds — extend, don't stop at these:

1. **Urgency as a pre-emption at the `FindTask` seam, not as data.** The
   module keeps a transient "urgent" set (malfunctioned buildings by the Q3
   class tests, rebuilt from `is_malfunctioned` and the maintenance-phase
   messages, weak-keyed). The chained `FindTask` wrapper first asks the ENGINE'S
   OWN finders (`FindSupplyRequest`/`FindDemandRequest`, `EF-060`) for a pairing
   that serves an urgent building this agent can reach; if found, return it in
   vanilla shape; else `orig_findtask`. Priority data untouched, nothing
   persisted, uninstall = the matcher reverts instantly (the D06 safety class).
   Cost: per-call work on a hot seam — bound it (a per-hub "urgent count = 0"
   fast path). Does a demand request need a supply pairing the finder can make
   without the C matcher? Is `max_units=1` on work requests respected via
   `CanAssignUnit`?
2. **"Urgent while broken" inside `-1..3` by re-registration.** Class-level
   `GetPriorityForRequest` override (installed at file scope, `EF-058` scope
   clause) returning 3 for a malfunctioned building's maintenance requests; a
   handler on the malfunction flip and on repair that re-registers the building
   so the new priority takes (priority is baked at insert, §3). Loses 5-vs-3;
   can a second dimension restore it — the finders' flags, `supply_dist_modifier`,
   `rfWaitToFill`, the request `max_units`, the hub's restrictor tables, anything
   the matcher demonstrably honours (`EF-059` proves flags outrank distance)?
3. **Two-pass FindTask with a proxy hub.** Call `orig_findtask` on a shim
   object whose `priority_queue`/`supply_queues`/`demand_queues` hold ONLY the
   elevated requests (keyed inside `-1..3`, e.g. all at 3), then on the real hub.
   Does `FindTask` touch `self` beyond the three tables (lap-time bookkeeping
   `_TaskRequest.lua:77-81`)? Are requests allowed to sit in two tables at once
   (vanilla already files one request in every covering hub — yes?)?
4. **Shadow queues + tail-call hygiene on the drone side.** A pre-hook on the
   idle path that serves the urgent set directly (the moonlighting pattern
   generalised, `SetCommand("Work"/"PickUp", …)`), installed on a synchronous
   seam only — and check whether a Lua proper tail call (`return orig(self)`)
   leaves NO frame for the persist walk to capture (`EF-023`; if unmeasured,
   design E-n for it).
5. **Widen the range but never let 4–5 reach a save**: the tear-down-on-save
   from B1, made the primary design rather than a mitigation; enumerate every
   way a save can be written without `SaveGameStart` (autosave, quicksave,
   crash dumps, cloud) and whether each fires the message.
6. **Widen per hub, on demand, and un-widen on exit**: allocate 4–5 only while
   a hub has an elevated request and remove the keys the moment it has none;
   what does `ReconnectTaskRequesters` do to that mid-flight?
7. **Reverse the elevation — DEMOTE routine traffic instead of promoting
   urgent work.** If everything non-urgent is filed at a lower band while
   broken buildings stay at the player's value, the ordering is the same and
   nothing sits above 3. What breaks (depots at 0, the player's 1)?
8. **Borrow the devs' own mechanism**: `BreakableSupplyGridElement` and
   `PassageGridElement` return 3 for their repair requests via the class
   override — extend EXACTLY that pattern to the five producers + the
   malfunction predicate, and accept band 3. Then ask what the honest
   disclaimer says and whether the owner's "distinction" requirement is a
   requirement or a preference — write it as a question, not an answer.
9. Anything else: `OnMsg`s the record has not used, engine hooks on request
   creation (`Request_New`, `_TaskRequest.lua:154`), the `supply_dist_modifier`
   lever measured in C48 (distance multiplies — could a *negative* or tiny
   modifier act as urgency within a band?), the elevator/`MapSharedDepot`
   registration override as a precedent for per-class registration policy,
   deficit tables (`DroneControl.lua:107-123`) and what shuttles would see.

Mark every idea **IDEA** (unproven) vs **FINDING** (cited). Keep the two words
apart in every sentence.

## 5 · Experiments — designed, priced, NOT run unless the owner says so

For each rubric cell left UNKNOWN, write an experiment card: the question, the
fixture (new game or throwaway copy — never a real save; fix pack `EF-056`
autosave ritual), the temporary module (marked `TEMPORARY`, deleted in the
result commit), the exact console reads, the **prediction committed before the
run**, and what each outcome settles. Candidates the record already implies:
E-1 does `SaveGameStart` run synchronously before the persist walk with threads
paused; E-2 does a tail call leave a frame in a persisted coroutine; E-3 does a
post-wrapper on `DroneControl:RemoveBuilding` clear band-4 entries (re-measure
§10's `4 → 6` on a clean fixture — n=1 today); E-4 what `FindTask` passes to C
and whether a shadow view is honoured; E-5 the top-up walk on a loaded save,
before the first `FindTask`. Estimate attended minutes per card. Running any of
them is an owner call — put the ask on the checklist (§7).

## 6 · Deliverables — in this order, each its own todo item

1. `docs/agent/reports/DRONE_BANDS_CLEAN_REVERT_<YYYYMMDD>.md`: the problem
   (§"Why", compressed); Part A's delta list; Part B — every candidate with its
   §2 table; a ranked shortlist with the trade-offs measured, not argued; the
   experiment cards; **the verdict on the job's question**, in one of three
   forms and no other: *"YES — mechanism X passes every rubric row from
   citations alone"* / *"YES IF — X passes pending E-n, E-m"* / *"NO — every
   route fails row R-k because …"*. Provenance words per claim (SOURCE /
   MEASURED / INFERRED / IDEA).
2. Any fact you find contradicted by Src today: correct the fact file in the
   same commit and say so (fix pack first for a NEW fact — `EF-` ids are
   allocated there; mirror here at the same id).
3. One line appended to the fix pack's `prompts/DRONE_PROJECT_PROMPT.md` §3
   pointing at the report (it is the re-runnable drone prompt and is updated
   in place after every drone session — do not rewrite its options).
4. Owner asks on the fix pack's `docs/PLAYTEST_CHECKLIST.md` → "Decisions
   waiting on you" (next number; one line + pointer each): the design decision
   restated with the new inputs; which experiments to run; anything the
   brainstorm turned into a design question. Their numbers on `STATE.md`'s
   open-decisions line; `STATE.md` otherwise only if the kernel changed (byte
   cap — evict, don't compress; `prompts/STATE_EVICTION.md`).
5. `docs/archive/SESSION_LOG.md` entry (newest first, `tags:` line) with the
   verdict form and the report path. `python tools/doccheck.py` GREEN in both
   repos.
6. Close-out commit: report + fact corrections + `git rm docs/agent/prompts/BANDS_CLEAN_REVERT.md`,
   `git commit -F <file>` (subject carries the verdict form, e.g. "drones:
   bands + clean revert — YES IF, 2 experiments owed"), push; the fix pack's
   edits in their own commit, pushed. Name the grave in the summary:
   `git show <sha>:docs/agent/prompts/BANDS_CLEAN_REVERT.md`.

## 7 · Scope fence

**IN:** the bands-and-revert question; the evidence delta; candidate
mechanisms and their rubric; experiment design. **OUT:** building or changing
any module; the D06 decision itself; D09; F77; the seed-logistics designs
(§I/§K — read them for seams, do not design them); the TestKit (checklist 83);
launch prep; anything D12/D07. **Found something interesting out of scope →
file it** (an entry line with evidence, or `FUTURE_IDEAS.md`) and stop.

## 8 · Stop conditions — permission to report instead of pushing on

- A candidate needs a **new persisted name** (a field on an object, a GameVar,
  a modifier id, a marker) — record it as failing R5, do not design around ban 1.
- A candidate needs a **function stored on a game object** (`EF-022`) or a
  hook whose frame sits below a `Sleep` (F86) — record, kill.
- A rubric cell can only be filled by a **running game** — write the card, ask.
- A fact in `agent/facts/` **contradicts Src today** — correct it in the same
  commit; do not build on either silently.
- The Src path is missing or the build is not `1.0.7.396349` (`EF-014`).
- The job is bigger than one context — split at Part A / Part B; propose a
  chain (`reports/CHAIN_METHOD.md`), commit the folder before link 1.

## 9 · What may NOT be claimed

- **"Clean revert"** for any candidate without every §2 row filled from a
  citation or an owner-run experiment. A row filled by reasoning is INFERRED and
  the verdict form is *YES IF*, never *YES*.
- **Band ordering inside or between bands** — Q1 proved consumption, not
  precedence (n=1 suggestive signal, `D06.md`).
- **The duplicate leak's magnitude** (`4 → 6`, once) or that a wrapper closes it
  — until E-3 or a Src route that names every loop.
- **"No behaviour change"** from a desk instrument; a desk PASS is
  *desk-derived*, never *verified*.
- **Which option the owner should pick.** Rank, recommend, show the trade-offs
  — the pick goes on the checklist, and a recommendation recorded only in the
  report is not considered asked.
- Any count not emitted by `doccheck --emit-counts`; any probe total that is
  not the shared suite's, labelled as such.
