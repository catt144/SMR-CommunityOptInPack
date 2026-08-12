# Fix Policy — how we patch

Rules for every module in this mod, in priority order. The goal: maximum
compatibility with other mods and future game patches, zero edits to game files.

> ## ⭐ ADAPTED COPY — read this ledger before you trust a clause
>
> Copied from `SMR-BugFixPack/docs/agent/FIX_POLICY.md` @ `33d69f5` on
> 2026-08-12 (chain `split-optins`). **Only what is listed here changed;
> everything else is the donor's text, and it binds unchanged:**
>
> 1. **§4 is INVERTED and rewritten.** The donor's §4 is "only fix proven,
>    reachable, UNINTENDED defects" — a rule for a pure bug-fix mod. This mod's
>    product IS opinionated behaviour, which is exactly what that rule sends
>    elsewhere. The new §4 states what may be built HERE; the donor's §4 is kept
>    **quoted in full underneath it**, because it is the reason these eight
>    modules were `Opt_` files in the first place, and it is still the rule that
>    decides whether a proposal belongs in that mod instead of this one.
> 2. **The namespace is renamed throughout** — `SMRFixPack.*` → `SMROptInPack.*`,
>    `SMRFixPack_Disabled` → `SMROptInPack_Disabled`. ⛔ **§3's `SMRFixPack_*`
>    field-naming rule is NOT renamed**: the fields this mod already writes are
>    save contract and keep the donor's prefix forever (`agent/PROVENANCE.md` §2).
> 3. **§4a (vanilla only), §5 (optional modules), §8 (release hygiene) carry
>    short marked notes** where the wording assumed one mod. Nothing is deleted.
> 4. §1, §2, §3, §3a, §6, §7 are **unchanged and fully binding** — they are
>    about the engine and about save safety, and this mod patches the same
>    engine and writes into the same saves.

## 1. Choose the least invasive technique that works

Ranked from most to least preferred:

1. **Data/preset patch** — mutate the preset field in place (e.g.
   `TraitPresets.DustSickness.daily_update_func = ...`,
   `TechDef.X[i].Amount = -20`). Do it in `OnMsg.ClassesPostprocess` (presets built)
   or at code load if the object already exists. Most compatible: other mods see the
   corrected data.
2. **Additive handler** — a new `OnMsg.<X>` alongside the broken one (OnMsg is
   additive; a dead original handler can stay). Used when the original can't fire at
   all (F23).
3. **Registry/table surgery** — adjust the stored entry another system reads
   (e.g. wrap slot FUNC of `PeriodicRepeatInfo["UndergroundMarsquake"]`). Leaves the
   scheduling machinery and any other wrappers intact.
4. **Wrap (chain) the original function** —
   ```lua
   local orig = Colonist.BoardVehicle
   function Colonist:BoardVehicle(...)
       local r1, r2 = orig(self, ...)
       if self.transport_ticket then self.transport_ticket.start_wait = GameTime() end
       return r1, r2
   end
   ```
   Always capture at apply time, always call `orig`, always pass through returns.
   If another mod wrapped first, we chain onto theirs — and vice versa.

   **4b. Global-function replacement** (its own technique, between 4 and 5 in
   preference; numbered 4b so existing §1.4/§1.5 citations stay valid) —
   assigning `_G[name] = replacement` for an existing global. Works because
   `ModEnvMeta.__newindex` rawsets non-blacklisted existing names into the
   real `_G`, and generated closures (script conditions, sequence code)
   resolve the name at call time (agent/facts/). Rules: plain assignment,
   NOT `rawset(_G, ...)` (that writes only the mod's own env); read the name
   back with `rawget(_G, name)` in apply() to confirm the write landed (F22
   does); prefer a chained wrapper (capture `orig`, delegate) over a body
   copy whenever the defect is hookable.
   **⚠️ Prefer a wrapper over a body copy even when both work — it degrades
   gracefully and a copy does not** (recorded 2026-07-31 by the F86 layer-3
   sweep). If a future game patch fixes the vanilla bug, a chained wrapper
   becomes a harmless no-op, whereas a §1.5 copy silently reinstates the old
   body's shape and can *undo the official fix*. Two shapes make a wrapper
   sufficient more often than it looks:
   * **the fix only needs to widen a result** — vanilla returns `true`/nil and
     you need `true` in more cases, so `local r = orig(...) if r then return r
     end return <extra case>` leaves every existing path identical **by
     construction**, which is stronger than a hand-verified byte-copy
     (`Colonist:ShouldLeaveForWork`, F04);
   * **the broken original is a verified no-op** — then a post-wrapper doing the
     correct work is enough (`Building:StopUpgradeModifiers` iterates a
     string-keyed table with `ipairs`, F03).
   Also check whether the shipped function **already takes the parameter you
   need**: `LandscapeConstructionSiteBase:GetClosestDests(drone, top_count)`
   accepts the bound its only caller never passes, so clamping it in a wrapper
   fixes F33 with zero copied logic.

5. **Full replacement** — only when the defect is mid-function and unhookable
   (F04, F09, F11, F12...). Rules:
   - Copy the shipped body **byte-identical except the minimal fix**, marked with
     `-- FIX:` comments on changed lines only.
   - Header comment must name source file + lines + game version the copy came from
     (the pinned build number, e.g. `1.0.7.396349` — not a date).
   - These are the fixes most likely to clash with other mods and rot on game
     patches — keep the list short and re-verify each game update (the fpk
     extraction diff is a release gate, WORKFLOW.md).
   - **"Reconstruction" sub-category:** a replacement whose body is NOT a
     byte-copy — the original is rebuilt from its observable contract (a
     file-local was inlined, a helper re-derived; F03/F04/F09 are of this
     kind). Allowed only when a byte-copy is impossible (file-local upvalues,
     generated code); the header must SAY it is a reconstruction and name
     what was re-derived, because the extraction-diff re-verify cannot
     compare it byte-for-byte — it needs a behavioral re-check instead.

## 2. Fail safe, never loud

Every fix goes through `SMROptInPack.Register(id, {title, apply})` (Code/00_Core.lua):

- `apply` runs under `pcall`; an error deactivates only that fix.
- Before patching, sanity-check the target still looks like the bug (function
  exists, table layout as expected). If not — the game likely hotfixed it —
  **return a string** (reason) instead of patching. Never assume; never error.
- **Self-check on the DECLARING class** (the F64 lesson): mod code runs before
  classes are flattened, so a classdef exposes only members it declares
  ITSELF — checking an inherited method on a subclass finds nil and silently
  deactivates the fix. Verify where the method is declared in Src and check
  that class.
- ⛔ **NO `apply()` MAY ASSUME A COLD BOOT (the F87 rule, 2026-07-31).** A mod is
  never auto-enabled: the player ticks it at the main menu of a process that is
  already running, the engine does an **in-place reload**
  (`ModsReloadItems` → `ReloadLua`, `Mod.lua:2145`), and our code loads with the
  **presets ALREADY loaded and the classes NOT yet built**. That is **every
  player's first run**, and it is the opposite of the cold boot every A/B leg we
  have ever run measures. Two binding consequences:
  * **Apply-time code may not CONSTRUCT a class or preset object** — no
    `Class:new{…}`, no `PlaceObj`, no class-table method call. Mod code always
    loads before flattening, so `Class.new` is nil; on a cold boot the pass
    usually returned early for lack of presets and hid it. `type(X) == "table"`
    does NOT prove a class is built — an unflattened classdef is a table too.
    Test what you are about to use (`type(X.new) == "function"`), and prefer
    `PlaceObj("Class", {…})`, which fails soft where `:new` throws.
  * **`OnMsg.DataLoaded` alone is NOT a sufficient trigger** — it does not fire
    on the enable path, so a fix hung off it is silently dead for that entire
    session. Use `SMROptInPack.DataPatch` (preset patches with the latch/heal
    contract) or `SMROptInPack.OnDataReady` (everything else); both fire on
    `ClassesBuilt` / `ModsReloaded` too, and both require the callback to be
    idempotent. The F87 sweep found three sites that had this bug.
  **Both paths must be tested** — a cold boot AND a run where the pack is
  enabled from the main menu. The second one is why F87 shipped.
- ⛔ **EVERY WRAPPER MUST BE INERT FOR A FOREIGN OBJECT BEFORE IT TOUCHES ONE**
  (adopted 2026-08-03, spec §7). A wrapper on a shared method is called for
  every object of every class that inherits it, including objects another mod
  created and objects our defect has nothing to do with. Decide "is this mine?"
  and hand the call straight to the original **before** reading a field,
  allocating, or logging — a wrapper that inspects first is already a behaviour
  change for everyone else, and it is the shape §4a bars us from shipping.
- Respect `SMROptInPack_Disabled["<id>"]` so users/other mods can veto single fixes.
- **Every `OnMsg` handler must re-check BOTH the registry status AND the veto
  itself** (the A1 lesson, audit 2026-07-29): handlers are installed at file
  scope unconditionally — Register's veto only skips apply() — so a handler
  that mutates state without re-checking `SMROptInPack_Disabled[id]` (and,
  where it heals status, without refusing to overwrite `"disabled"`) defeats
  the veto. Donor pattern: Fix_LastTransmissionStorage's patch() prologue.
- If the target can legitimately be absent before `DataLoaded` (presets,
  templates), track a `data_loaded` flag and only latch `inactive` after it
  has fired — before that, absence just means "not loaded yet" (the F75
  false-inactive lesson); after it, silence means reporting `active` forever
  on a target a future update removed (the B3 lesson). **On the enable path
  that flag can only come from the engine's own `DataLoaded` global**
  (`Dlc.lua:51/:663`, declared under `FirstLoad` so it survives a Lua reload) —
  the message never arrives. Both shared runners do this for you.

## 3. Savegame discipline

- No new persisted classes or GameVars unless unavoidable; if needed, name them
  `SMRFixPack_*` and tolerate their absence (loading a save made with the mod,
  after the mod is removed, must not break).
  ⛔ **YES, `SMRFixPack_` — that prefix is not a typo here and is not renamed
  to match this mod** (marked 2026-08-12, split): the five fields and modifier
  ids these modules already write went into players' saves under it, and a save
  contract outranks a tidy namespace. A NEW persisted name in this repo may use
  either prefix, but must then be added to `agent/PROVENANCE.md` §2, where it
  becomes equally unrenameable. See also `agent/facts/`, and the whole of §3a.
- Fixes must be sane on existing saves. If a bug left corrupt state behind
  (e.g. F03's leaked modifiers), the cleanup is a **separate, clearly marked
  one-shot `OnMsg.LoadGame` sweep**, conservative by default.
- Never break saves for players who later disable the mod.
- **Exit hygiene (owner, 2026-07-31): the pack ships with its exit paved.**
  Two standing deliverables, both ready BEFORE launch: a player-facing
  **uninstall procedure** ("update, load, save, then uninstall" — backed by
  the latched heal + migration passes, which clear our threads out of the
  save), and the **standalone save-rescue artifact** for saves that already
  lost the pack (the only console-viable remedy). Record + spec gate + open
  design question: **`agent/bugs/D13.md`**; plan: `F86_EXECUTION_PLAN.md` Phase 5.
  ⛔ The artifact is **specced only after Tiers 1+2 land and verify** — its
  target list is their output, never today's leak set. `[FAQ]`

### 3a. SAVE SAFETY — design so the save carries as little of us as possible, and the exit cleans the rest (HARD RULE, owner, 2026-07-31; framing set by the owner 2026-08-01)

**The stance (owner, 2026-08-01, verbatim):** *"we now know mod left overs are
an accepted fact, we will try to be above the normal but its not a lockout …
We just need to make sure our uninstall methods address them late."* By-value
thread serialisation is **documented, intentional engine design**
(`LuaSavegame.md.html`, quoted in agent/facts/) and the community's norm is to
accept and silence it (`PRIOR_ART_SURVEY.md`). This pack aims **above that
norm** — an engineered exit, not accidental residue — so §3a is a **design
discipline that minimises what the exit path must clean**, not a purity bar.

**⭐ THE THREE-TIER ETHOS (owner, 2026-08-01 — this is the goal §3a serves, and
it supersedes any "leave no trace" framing left elsewhere in the docs).** The
original game's own code spells the mechanism out; leftovers are an accepted
fact of modding this engine, not a failure. So we aim, **in this order**:

> 1. **Leave no trace.** Prefer a shape that puts nothing of ours in the save
>    at all — that is what the layer 3 → 2 → 1 ordering below exists to reach.
> 2. **Leave non-harmful trace.** Where something must persist, make it
>    **inert**: named, bounded, disclosed, and incapable of doing anything
>    after removal. An accepted residual.
> 3. **Leave harmful trace only when 1 and 2 are both unreachable** — and then
>    **fix it from outside**, with the uninstall/save-rescue tooling (**D13**)
>    that **ships at launch, alongside the pack**. A harmful residual is never
>    simply accepted; it is accepted *paired with its remedy*.

**⚖️ THE RELEASE GATE IS PER-SITE, NOT BLANKET (owner decision, 2026-08-01).**
There is no rule that all residue must be repaired in-pack before release, and
no rule that the cleaner excuses leaving it. **Every exposed site gets its own
recorded disposition:** repaired in-pack where a layer 3 or layer 2 route
exists, handed to the cleaner where one provably does not. **A complete
per-site disposition — every site, each with its call and the reason — is
required before release.** A site with no recorded disposition blocks release
by default; a site *with* one does not, whichever way it went.

**⛔ BUILD FIRST, DISPOSITION AFTER — the cleaner is NOT a scoping escape hatch
(owner, 2026-08-01, verbatim):** *"We will build everything now, regardless of
whether the cleaner exists now because we won't launch till it does. It doesn't
make sense to build a cleaner until we know everything it needs to clean and
how."* Two rules follow, and they bind:

> - **No site may be deferred to the cleaner in advance.** Build everything the
>   layer ordering allows, **now**, without waiting on D13 and without counting
>   on it. A cleaner hand-off is only a valid disposition **after** the in-pack
>   attempt has been made and the route proven absent — never as a prediction,
>   and never as a reason to descope.
> - **The cleaner is specced LAST, by construction.** Its target list is the
>   *output* of the build work: what remains once every reachable repair has
>   landed. That is why D13's spec is gated — not because it is low priority,
>   but because designing it earlier would mean designing against a residual set
>   we had not finished changing.

**Sequence, therefore:** build every reachable repair → the residue that
survives *is* the cleaner's target list → spec and build D13 against it →
launch. **Launch waits for D13; D13 does not wait for launch.**

Where dispositions are recorded: sites repaired in-pack are dispositioned by
the tier that repairs them (Tier 2 = chain prompt 5); the **complete
pre-release table is a D13 deliverable**, since D13 is what carries whatever
the pack could not.

⚠️ **And the table is built against D13's OWN derivation of the exposed set,
not against any count recorded in these docs** (owner, 2026-08-01). Every
figure on record is an open lower bound from a grep proven blind to
slot/global/preset assignments, and the builds have since changed the set —
so "every exposed site" can only be enumerated by re-deriving it at that
point. See the D13 entry in `agent/bugs/` for the requirement and the list of
places its result must correct.

**The mechanism, as finally established (measured + twice-adjudicated — this
opening states the CURRENT truth; earlier drafts' "empty `_ENV`" claim is
dead):** a savegame serialises **by value** everything reachable from the
persisted graph at write time. A mod function enters a save iff: **(a)** its
frame sits below a `Sleep`/`WaitMsg`/`WaitWakeup` on a blocked **game-time**
thread; **(b)** it is held in a live local/upvalue of ANY captured frame —
engine frames included (`Fix_CaveInsNoDisasters` is capturable this way,
inert because layer-2-shaped); or **(c)** it is stored in persisted state
(object fields, GameVar contents, notification closures). Purely synchronous
code that stores no function values is safe by construction; real-time
threads are never persisted; class tables, presets, `OnMsg` registrations and
UI windows are safe. And a captured orphan is NOT env-dead: its fallback env
falls through to real `_G`, so it resolves every vanilla global and loses
only mod-created names — a body touching `SMROptInPack.*` dies at that touch,
an all-vanilla body **keeps executing after uninstall** (bounded if it
self-limits, forever if it loops). `Fix_MeteorFrequency` killed a colony's
meteors permanently this way; `Opt_DroneOverhaul` leaked with its toggle OFF.
Every design must answer: *if this body is captured anyway, does it die,
expire, or run forever — and would anyone notice?*
(`F86_ADJUDICATION.md` §3.1/§5.1/§8; `agent/facts/`.)

**⛔ THE ORPHAN GATE (owner, 2026-07-31) — loud death is the BACKSTOP, not the
failure mechanism.** An orphan that dies at its first mod-name lookup dies at
an *accidental* point — wherever a logging call happens to sit — and can die
mid-work (`StormWedgeHeal` could strand `g_MeteorStormStop=true`). The designed
failure is:

> **Every mod-owned thread body opens each wake with an explicit orphan gate —
> `if not SMROptInPack then return end` — and resets any vanilla state it set
> BEFORE its first mod-created-name touch.** Reading a nil global is safe (only
> indexing/calling it throws), so the gate exits cleanly in an orphan: zero
> errors, zero half-done work, at a point we chose. Long loops re-check the
> gate after every yield. The global-lookup helper discipline stays underneath
> as the backstop: anything that slips past a gate still dies rather than
> running forever. (This supersedes the earlier "die loudly is the safer
> failure" framing — that loudness was an accident of the disproven by-name
> persistence belief, retroactively useful, never designed.)

**Choose the remedy in this order — 3 → 2 → 1. The ordering is binding.**

1. **Layer 3 — patch a synchronous input, keep vanilla's body.** ⭐ Best: the
   pack has no body in the save at all and the problem disappears for that
   module. Where a defect can be repaired by changing what a shipped function
   *reads* rather than replacing what it *does*, do that.
   ⚠️ **Scope the wrapper by the narrowest thing that actually separates the
   call sites, and enumerate every caller before choosing the key.** Keying on
   an argument is not automatically enough: `GetDisasterWarningTime` is called
   with the *same* meteor descriptor by both the `Meteors` and `MeteorStorm`
   threads, so a descriptor-keyed wrapper would silently change storm warning
   timing. `CurrentThread()` is available (not blacklisted) and global
   game-time threads are parked in a global of their own name, so
   `CurrentThread() == rawget(_G, "<Name>")` is a precise key where one is
   needed.
2. **Layer 2 — no mod code after a call that can block.** Do all work
   **before** the call, then `return orig(...)`. Then whether or not the frame
   is serialised, there is nothing left to execute after removal. This needs no
   engine guarantee, which is why it replaced the earlier "tail calls remove
   our frame" justification — that claim is **unobservable in this sandbox and
   must not be re-derived or re-tested** (a tail call has nothing after it, so
   a vanished frame and a surviving frame produce identical silence). Wrappers
   that genuinely need post-work must move it out of the command body into a
   message or periodic hook.
   *Residual, accepted:* an inert serialised function may sit in a save as dead
   weight; it executes nothing and no read available to us can see it.
3. **Layer 1 — `OnMsg.SaveGameStart` tear-down / `SaveGameDone` rebuild**, for
   what layers 3 and 2 cannot reach. Mods **do** get this hook (only
   `PersistSave` / `PersistLoad` / `PersistGatherPermanents` are blacklisted).
   **Build it last, and only for what survives the other two layers; every
   module that uses it needs its own A/B plus a long-interval soak.**
   ⚠️ **THE TRAP:** autosaves are the same `DoSaveGame` path and fire roughly
   once a sol, so a tear-down that *restarts* a loop would reset a 35–115 h
   meteor timer before it could ever expire — recreating PT-01's
   permanent-silence signature out of our own code. **Re-arm from a persisted
   deadline, never restart blind.**

**This binds new fixes as well as repairs.** Anything that replaces a blocking
body, wraps a command method, or creates its own game-time thread must state in
its header which layer it is on and why. Full analysis, the exposure list
(**13** after two same-day membership corrections — `DroneUnreachableForever`
in, `TrainCargoDumping` out, compliant `CaveInsNoDisasters` counted;
**re-derived 2026-08-01 by the five-shape Phase-1 enumeration, which confirmed
the 13 and classified one additional inert route-(c) preset-field site** —
`Fix_LastTransmissionStorage`'s `Condition.eval`, disclosed-no-build,
adjudication §4.4) and the per-module disposition:
`docs/agent/reports/SAVE_SAFETY_REDESIGN.md` and `agent/bugs/F86.md`.

## 4. What may be BUILT here — opinionated modules, proven and reachable

> ⭐ **REWRITTEN FOR THIS MOD 2026-08-12** (chain `split-optins`). The donor's
> §4 is quoted in full as **§4-donor** below — unchanged, still authoritative
> for the fix pack, and still the test that decides which of the two mods a
> proposal belongs in.

**The inversion, stated plainly:** the fix pack may only repair *unintended*
defects, and its §4 sends every opinion, preference and balance change
elsewhere. **This mod is that elsewhere.** A module here is allowed to be an
opinion. What it is NOT allowed to be is unproven, unreachable, on by default,
or silent about which it is.

Every module links to an `agent/bugs/` entry, and before it ships:

- **Say which it is, in the entry and in the file header.** Three kinds live
  here, and conflating them is how a "fix" ships as a preference:
  (a) a **behaviour change** the player chooses (D02, D03, D07, D12);
  (b) a **numeric dial** whose base position is byte-vanilla (D09);
  (c) a **repair the fix pack declined** because intent was ambiguous or the
  reading was a judgement call, shipped opt-in so the player decides (D01, D04's
  build-limit half). For (c), the entry must name what §4-donor's test found —
  "intentional", "ambiguous intent", "R3 latent" — rather than implying the fix
  pack overlooked it.
- **Reachability still binds, unchanged.** Enumerate the call sites, name the
  concrete player action, record the tier (R1 live · R2 conditional · R3
  latent-by-data · R4 unreachable · U unknown). A module nobody can reach is
  not made shippable by being optional. The `tested` bar is the donor's: the
  state was reached **by playing**, not by console surgery.
- **OFF (or base) by default is the shipping default and needs a reason to
  change**, not a reason to keep. Three of these eight move colonists between
  domes, re-home cohorts, or are labelled experimental; two add rows to the
  Dome infopanel. Installing this mod buys the *choice* — the Mod Options page
  IS the product. (Recommendation adopted at the split, 2026-08-12; the counter-
  argument — that a player who installed an opt-in mod already opted in — is
  recorded in the split design and is the owner's to revisit.)
- **A module OFF must be byte-for-byte vanilla BEHAVIOUR** — and that says
  nothing about the save. See §5's warning; it is the trap that produced two
  false save-cleanliness claims.
- **No cross-module dependency inside this mod, and none on the fix pack.**
  Every module stands alone with the other seven off, and the whole mod stands
  with the fix pack absent (the standalone invariant, `CLAUDE.md`). A module
  that would need another module's state is a design error, not a load-order
  problem.
- **Balance is not a free space.** "The player can turn it off" is not a licence
  to ship anything: a module still has to be *defensible* — a coherent rule a
  player can predict, not a pile of tuned constants. When intent is ambiguous,
  prefer the reading proven by sibling code in the same file, exactly as the
  donor requires, and then let the player choose it rather than choosing for
  them.
- **Evidence freshness:** re-check `git log` in BOTH repos between assembling a
  verdict and recording it. This project has twice been burned by writing
  against a stale snapshot, and the split doubled the number of trees a
  snapshot can go stale in.

### §4-donor — the fix pack's §4, kept verbatim (do not edit; the donor is authoritative for it)

⛔ **This is not dead text.** It is the rule that put these eight modules behind
toggles instead of shipping them as fixes, and it is the test a new proposal
still has to fail before it may live here: *if a defect passes the donor's §4,
it belongs in the fix pack as a plain fix, not here behind a toggle.*

> ## 4. Only fix proven, reachable, UNINTENDED defects
>
> > **AMENDED AND ADOPTED 2026-08-01.** This section replaces the three-sentence
> > "Only fix proven defects" rule with the reachability audit's drafted
> > amendment, applied verbatim from `REACHABILITY_AUDIT.md` §4. **Authority:**
> > the owner's blanket pre-clearance of 2026-08-01 (recorded in the project
> > chain's manifest, `docs/agent/prompts/project/README.md` — consumed with the
> > chain on 2026-08-03 and now in git history only), which clears the approval step for work
> > items derived from the audit-and-adjudication conversation — this adoption
> > named among them. **The blocker that held it back is gone:** the draft
> > contradicted itself while F49(a) shipped a no-op R4 rider against the new
> > "R4 does not ship" line; that guard was **stripped from `Fix_TrainMinors`
> > on 2026-08-01** (`agent/bugs/F49.md`; A/B code-gate leg ran clear), so the rule and the
> > shipped code now agree. **Live consequence on adoption:** F29 and F57(a) are
> > R3 defects fixed by §1.5 method replacements — the combination the R3 bullet
> > below now makes conditional on an explicit owner decision. Both entries
> > already anticipated this; the decision is routed and owed, not assumed
> > either way.
>
> Every fix links to an `agent/bugs/` entry with file:line evidence, **a recorded
> reachability tier, and a positive intent statement**. Before a fix ships:
>
> - **Intent first.** State why the shipped behaviour is unintended, citing
>   at least one hard tell: (1) player-reported harm; (2) dead code / dead
>   validation — a computed value discarded, a guard that cannot fire, a
>   message nothing emits; (3) sibling contradiction — the same author wrote
>   it correctly elsewhere; (4) self-contradiction within one function or
>   preset; (5) an explicit dev comment. **No tell → the defect claim is a
>   hypothesis, and it needs a keyboard observation before any fix is
>   written.** UI/affordance behaviours — anything whose wrongness lives in
>   hit-testing, cursor feedback, input modes, or whether two things are
>   separately addressable — are in this class BY DEFAULT: source reading
>   gives confident answers with no validity there (the F49(c) lesson). A
>   behaviour found intentional is tier **I**: record it, close it, write no
>   fix.
> - **Then reachability.** Enumerate every call site of the defective
>   function in Src; eliminate the ones that cannot execute the defective
>   body (class chain, guards, early returns, template data); for each
>   survivor name the concrete player action that produces the precondition.
>   Record the tier: R1 live · R2 conditional · R3 latent-by-data · R4
>   unreachable · U unknown (naming the observation that would settle it).
> - **Symmetry of proof.** Every tier states its evidence — an unenumerated
>   R1/R2 is exactly as unproven as an unstated R4, and more dangerous,
>   because "keep, it's live" is the verdict nobody revisits. **Every
>   lettered sub-item of a bundled fix is a separate audit subject**;
>   enumerating one item proves nothing about its siblings.
> - R1/R2 ship normally. **R3 ships only as a §1.1–§1.4 patch**; an R3 §1.5
>   full replacement needs an explicit user decision (the F24 lesson). **R4
>   does not ship**; record it `wontfix — unreachable` with the search that
>   proved it. **U ships only with the settling observation queued** as a
>   playtest item.
> - A `tested` status proves reachability only if the playtest reached the
>   state **by playing**; console surgery, `g_Consts` compression or `Cheat*`
>   calls prove the fix, not the path. A state producible **only by
>   console/debug injection is evidence for R4** (the PT-46 track lesson).
> - **Evidence freshness:** re-check `git log` between assembling a verdict
>   and recording it — playtest evidence lands continuously, and this
>   project has now twice been burned by writing against a stale snapshot.
> - No balance changes, no "improvements", no opinions — those belong in
>   other mods. When intent is ambiguous, prefer the reading proven by
>   sibling code in the same file (the F07/F08/F02 pattern).


## 4a. SCOPE — vanilla only. This mod never fixes other mods' problems. (HARD RULE, user, 2026-07-30)

> ⭐ **BINDS HERE UNCHANGED** (marked 2026-08-12, split). Read "this pack" as
> "this mod" throughout; the owner's rule was given about the project, not about
> one repository, and the WHO-BENEFITS test below is the same test. ⚠️ One
> sharpening the split makes necessary: **the Community Fix Pack is "another
> mod" for the purposes of this rule.** A module here may not exist to work
> around a fix-pack behaviour, and a fix-pack bug is reported and fixed there.

**Stated by the project owner, verbatim:** *"This mod does not fix bugs caused
from other mods. No agent should assume it does at any point going forward. The
only way that should be able to be changed is if an agent specifically asks me
to override as a one-off for something I specifically ask for."*

### The test is WHO BENEFITS — not how visible the problem is

Owner's clarification, same day: *"I don't want to fix things for other possible
mods. But if it's game code that could cause real problems for users now or in
the future even if they can't expressly see the issue, that is a real fix."*

**Ask one question: could a PLAYER be harmed by this — now, or after a future
game patch or DLC?**

- **Yes → it is a real fix. Ship it.** Invisibility is irrelevant. Latent is
  irrelevant. "No player has complained" is irrelevant. Silent corruption, a
  wrong number nobody has noticed yet, a branch that is benign only because
  today's shipped data happens to be benign — all of these are real fixes,
  because the harm lands on players the moment the data or the build moves.
- **No, the only conceivable beneficiary is another mod → do not ship it.**

**BARRED:**

1. **A bug caused by another mod.** Not ours. Never fix it, never work around
   it, never add a compatibility shim for it. If one is reported, record it and
   say whose it is.
2. **A vanilla bug reachable ONLY from mod code** — no shipped caller anywhere,
   so lighting it up needs **new calling code**, which only a mod can supply.
   Record it `wontfix` with the search that proved no shipped caller exists.
   *(This is tier **R4**. F28 is the worked example: `Research:ReplaceTech` has
   zero callers in all of Src.)*

**NOT BARRED — these are real fixes, ship them:**

3. **Shipped code that executes in ordinary play but whose defective branch is
   currently unreachable because of DATA.** The game runs the code; only the
   values keep it harmless. A patch, a DLC, or new story content can expose it
   without anyone touching a mod. *(Tier **R3**. F29's two items are the worked
   example — both execute live in every Dredgers playthrough and are benign only
   because the shipped presets pass default sampling parameters and
   already-ordered timings. F27, F31 and F43 are the same shape.)*

**The R4/R3 boundary is the whole rule:** R4 needs new *code* to become live —
mod territory, barred. R3 needs new *data* — which ships with patches and DLC,
so it is player territory, allowed.

**"For modder benefit" is no longer a valid reason to ship anything** — but do
not read a fix's own header or BUGS entry as authority on whether it is
mod-facing. **F29 described itself as a "mod-facing bundle" with "No shipped
user", and both claims were false** — the reachability audit found four live
shipped callers. Judge by enumeration, never by the entry's self-description
(the F49(c) lesson, applied to provenance).

**Override procedure — the ONLY one.** An agent that believes a specific case
warrants an exception must **ask the owner explicitly and get an explicit yes,
for that one case**. It is never inferred, never assumed from precedent, and
never carried forward to a second case. An existing shipped fix is NOT
precedent — one (F28) already violated this rule and was retired under it.

**Why this exists.** The pack shipped `Fix_ReplaceTechCount` (F28) against a
function with **zero callers in all of Src** — a 37-line copy of a shipped
method, carrying per-game-update re-verification cost forever, for a code path
no player can reach. It was not an accident: the entry said "No vanilla caller"
in its second line and it shipped anyway. That is the failure this rule stops.

## 5. Optional modules (`Opt_*`)

> ⭐ **THIS SECTION IS THIS MOD'S CORE SPEC** (marked 2026-08-12, split). In the
> donor it describes a minority of files; here it describes all eight. The
> install pattern, the dial addendum and the OFF-says-nothing-about-the-save
> warning are unchanged and mandatory. The only edit is the namespace.

Not bug fixes: opt-in behavior changes, off by default, one Mod Options
toggle each (`ModItemOptionToggle.name` == the Register id == the
`default_options` key — all three are load-bearing).

**Dial addendum (D09):** a module may instead expose `ModItemOptionChoice`
dials. Then the option names are NOT the Register id, the module registers
WITHOUT `optional` (00_Core's boolean reconciler must not manage it), and it
reconciles itself from `CurrentModOptions` on ApplyModOptions + CityStart +
PostLoadGame. The dial's base position must be byte-vanilla (module-owned
modifiers removed by id, including stale ones in loaded saves); choice
strings are load-bearing across items.lua / metadata `default_options` / the
module's own maps — byte-identical in all three.

- **Install pattern (mandatory — the A2 lesson, audit 2026-07-29):** hooks on
  class methods are installed at FILE SCOPE (classdef time, so they propagate
  through class flattening) and gate per call on `SMROptInPack.IsActive(id)`.
  An apply()-time install runs AFTER flattening on a first mid-session enable
  and is invisible to derived classes until restart. Donor:
  Opt_DroneOverhaul. Wraps that resolve at call time (a global function, a
  UI-template Init) may stay in apply() — say so in the header.
- Guard each file-scope install with the same existence checks apply() uses,
  so a missing target degrades to apply()'s reason string instead of erroring
  at classdef time.
- `apply()` keeps only self-checks and the opt-in check; it returns the same
  reason strings whether or not the hooks installed.
- `on_activate` / `on_deactivate` (both optional) run after a LIVE toggle
  flip only — use them exclusively for STATE that is not a call path (e.g.
  MultipleSuns' template flag); call-path behavior must come from the
  per-call gate, never from these hooks. They must be idempotent; failures
  are logged by the reconciler (B1 fix), not swallowed.
- Header must state the real toggle semantics (both directions, including
  the first mid-session enable) — and be updated when they change.
- Savegame footprint per §3; a module OFF must be byte-for-byte vanilla
  **behavior**.
  ⚠️ **AND THAT IS ALL IT MEANS — "off" says NOTHING about the save (added
  2026-08-01, after this bullet's neighbourly placement next to "savegame
  footprint" helped breed a false claim twice).** An optional module's hooks are
  installed at file scope / classdef time and only *gate* per call, so a module
  the player has switched off is still fully installed and still capturable:
  `Opt_DroneOverhaul` leaked into saves at 98 errors per session **with its own
  toggle OFF**, which is how F86 Site 2 was found. Never infer save-cleanliness
  from a toggle, in a claim or in a test — an uninstall question is only answered
  by Mod-Manager-disable or removal (measured equivalent, PT-20: 98 vs 98 on the
  same save). The three switches and what each one actually removes:
  `agent/facts/`, "OFF" IS THREE DIFFERENT THINGS.

## 6. Engine semantics that bind every fix

- **`error()` and `assert()` in mod code REPORT AND CONTINUE** — they do not
  unwind (agent/facts/). Never use them for control flow or guards; use
  early returns and reason strings. `pcall` still catches genuine runtime
  errors.
- **Localization stance:** a T value is a TABLE **in dev — in retail it is often
  a light userdata** (`Untranslated(s)` → `T{s, untranslated = true}`). Copied
  shipped bodies keep their `T(id, ...)` calls byte-identical; NEW player-visible
  strings from this pack use `Untranslated("...")` — the pack ships no loc tables
  today, and a raw Lua string where the UI expects a T value renders wrong or
  crashes (the F14 probe lesson). Log/console text stays plain strings.
  ⛔ **AND NEVER RE-USE A SHIPPED TRANSLATION ID TO CHANGE TEXT — IT IS A NO-OP
  IN RETAIL** (added 2026-08-02; this is not a style preference, it is why one of
  our shipped fixes never worked). `T(id, text)` returns `LocIdToLightUserdata(id)`
  and **discards your literal** whenever `TranslationTable[id]` exists, which in a
  retail build is always — English included, since English is a loaded table like
  every other language. `Fix_TechDescriptionBuilding` did exactly this and has
  never changed anything (**`agent/bugs/F98.md`**; F25 demoted, and **no longer citable as
  localisation precedent**).
  ⭐ **To ADD to existing localized text at zero cost in any language, concatenate:
  `shipped_T .. Untranslated("…")`** — supported on the retail userdata form and
  used by shipped code (`Workplace.lua:293`). Concat cannot *delete*, so
  correcting a wrong sentence still means replacing the whole string.
  Full mechanism, all four routes, and the queued live control: `agent/facts/`,
  "RE-USING A SHIPPED TRANSLATION ID …". ⭐ **Owner decision 2026-08-02: the pack
  WILL ship its own `ModItemLocTable` translations, post-release** — at which
  point this bullet is revisited, not before.
- **Logging:** every ModLog call escapes `%` (`msg:gsub("%%", "%%%%")`) —
  ModLog's print path formats the message a second time (00_Core.lua:24-30).

## 7. Console platforms (Xbox / PlayStation / MS Store)

- No developer console, no file access, no companion-mod path: the per-fix
  `SMROptInPack_Disabled` veto and every log/console surface (`ListFixes()`,
  reason strings, "report this log") are **invisible on console**. Fail-safe
  behavior must therefore never DEPEND on the player seeing a message —
  self-deactivation must be safe silently.
- Mod Options is the one universal surface (gamepad-native) — anything a
  console player must be able to steer goes there or nowhere.
- Any enabled mod blocks ALL achievements on those platforms (not on
  Steam/PC) — a storefront disclosure, not a code concern, but never write
  player-facing text that contradicts it.

## 8. Release hygiene

- One module per `Code/Opt_*.lua` file; file name matches the Register id
  (`Opt_<id>.lua`); every file listed explicitly in `metadata.lua` `code` AND
  in `items.lua`, in the same order (the Mod Editor regenerates `code` from
  `items.lua` alone).
  ⚠️ **N/A here: `Code/Fix_*.lua`.** The donor's line said "one fix per
  `Fix_*.lua`"; this repo ships no `Fix_` files, and a bug fix proposed here
  belongs in the fix pack (§4a).
- `00_Core.lua` must load first (list order in metadata controls load order).
- Before release: verify each target against the shipping `Packs\Lua.fpk`
  (see WORKFLOW.md), test each module in-game **in both configurations — with
  the Community Fix Pack installed and with it absent** (the standalone
  invariant), update agent/bugs/ statuses, credit prior art (ChoGGi's Fix Bugs
  mod documented several of these bug families for the original game).
- ⚠️ **The two mods ship as two products.** Each needs its own metadata,
  preview image, description, portal pass and console cert, and each release
  states which versions of the other it was tested beside.
