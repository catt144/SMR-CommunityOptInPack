# Fix Policy — how we patch

## Must_Read_Header
<!-- RULES -->
Rule: Keep §4-donor verbatim and unedited; it is the fix pack's text and it is what decides whether a proposal belongs in that mod rather than this one. [A3: pass]
Rule: Read §4 as inverted for this mod, whose product is opinionated behaviour, and apply §1, §2, §3, §3a, §6 and §7 as the donor wrote them. [A3: pass]
Rule: Do not build a fix for a version players cannot play; a defect that lives only in a save Steam and console cannot load stops before the build brief. [A3: pass]
Rule: Preserve the exact bytes of every persisted name listed in `docs/agent/FIX_POLICY.md` §"The persisted-name inventory". [A3: pass]
Rule: Keep executable code free of `SMRFixPack` references; persisted-name strings are data and exempt. [A3: pass]
<!-- /RULES -->

Rules for every module in this mod, in priority order. Goal: maximum compatibility with other
mods and future game patches, zero edits to game files.

> **Adapted from the Relaunched Fix Pack.** Shared sections follow the donor's current policy;
> executable framework names use this repo's `SMROptInPack` namespace, while persisted names keep
> their exact historical bytes. §4 is inverted, and §4a, §5 and §8 state this mod's product rules.
> §0, the risk standard, exists only here and never applies to the fix pack.
> Donor §2a is omitted because this core has `Require.test`, not the donor's `probe` API. Donor
> §2b is omitted because this repo has neither its manifest headers nor `bodycheck.py`/`luafn.py`.

## 0. Risk standard: a content mod, not a fix mod (owner ruling, 2026-09-19)

⛔ **This section applies to the Opt-In Modules mod ONLY. It never applies to the Relaunched Fix
Pack**, whose players expect it to exist cleanly and remove cleanly. Do not port it to the fix
pack, cite it there, or read the fix pack's standards through it.

The owner, 2026-09-19: this is an opt-in content mod, and a player installing content accepts a
different risk surface than one installing a bug fix. We strive to be as clean as possible, but
we are not limited to it the way the fix pack is. It covers **every module in this mod** (owner),
the behaviour modules as well as content such as the train hub.

- **Clean removal is an aim, not a gate.** §3a's tiers remain the design order. A module may leave
  its content in a save when removed (placed buildings, their persisted state) where that is the
  cost of the feature; say so in the module's description.
- **Disabling a content module** mid-session stops it offering new instances; existing placed
  content may stay. §8's both-configuration run, with the fix pack installed and absent, still
  binds.
- **The two bans in the header still bind an agent's own work.** Where something is truly only
  achievable by crossing one, or by accepting a residual, an agent may **offer** that option to
  the owner with its risk scope stated; it never adopts it itself. The owner decides, and the
  ruling is recorded where the obeying role reads it.
- **Choosing between options:** if a safe option is as good as an unsafe one, the safe one always
  wins. An unsafe option may be considered only when it gives a much better product, or does
  something the safe option cannot. The aim is the best product for the player.

## 1. Choose the least invasive technique that works

Ranked from most to least preferred. Take the first that repairs the defect.

1. **Data/preset patch** — mutate the preset field in place, in `OnMsg.ClassesPostprocess`
   or at code load if the object already exists. Other mods see the corrected data.
2. **Additive handler** — a new `OnMsg.<X>` beside the broken one, when the original cannot
   fire at all (F23). OnMsg is additive; a dead original handler can stay.
3. **Registry/table surgery** — change the stored entry another system reads (a
   `PeriodicRepeatInfo` slot, for example) and leave the machinery and other wrappers intact.
4. **Wrap (chain) the original** — capture `orig` at apply time, always call it, always pass
   every return through. If another mod wrapped first, chain onto theirs.
   - A post-hook enumerates the wrapped function's CALLERS, not its callees. For each caller
     ask: does it keep using the state my hook just published? A hook that acts on freed
     capacity is the dangerous shape, because the enclosing operation usually freed it for
     itself. Such a caller needs a guard keyed on its own state, not a later cleanup pass (F59).
   - Work deferred into a game-time thread rides in the player's save (EF-019). Deferral is
     allowed but is a §3a decision. The thread body has zero upvalues and takes its state as
     thread arguments, and the orphan gate `if not SMROptInPack then return end` is the FIRST
     statement after its only yield, before any vanilla state is touched. Never rely on the
     engine's `__unpersisted_function__` fallback in place of the gate.

   **4b. Global-function replacement** — between 4 and 5 in preference. Assign
   `_G[name] = replacement` (EF-017); never `rawset(_G, ...)`, which writes only the mod's own
   env (EF-009). Read the name back with `rawget(_G, name)` in apply() to confirm the write landed.
   - Prefer a chained wrapper over a body copy whenever the defect is hookable, even when both
     work: when a game patch fixes the bug a wrapper becomes a no-op, while a copy reinstates
     the old body and undoes the official fix. Two shapes make a wrapper sufficient more often
     than it looks: widening a result (`local r = orig(...) if r then return r end return <extra>`
     keeps every existing path identical by construction, F04), and a broken original that is
     a verified no-op, where a post-wrapper does the work (F03).
   - Check whether the shipped function already takes the parameter you need; clamp it in a
     wrapper instead of copying (F33).
5. **Full replacement** — only when the defect is mid-function and unhookable.
   - Copy the shipped body byte-identical except the minimal fix; `-- FIX:` comments on the
     changed lines only.
   - The header names the source file, lines and the pinned game build number (not a date).
   - Keep the list short; every replacement is re-verified on each game update (the extraction
     diff is a release gate, WORKFLOW).
   - A **reconstruction** (a body rebuilt from its observable contract, not a byte-copy) is
     allowed only when a byte-copy is impossible: file-local upvalues, generated code. Its
     header says it is a reconstruction and names what was re-derived, because its re-verify
     must be behavioural, not a byte diff.

## 2. Fail safe, never loud

Every fix goes through `SMROptInPack.Register(id, {title, apply})` (`Code/00_Core.lua`). `apply`
runs under `pcall`; an error deactivates only that fix.

- Before patching, sanity-check the target still looks like the bug (function exists, table
  layout as expected). If not, return a reason string instead of patching. Never assume, never
  error.
- Self-check on the DECLARING class. Mod code runs before classes are flattened, so a classdef
  exposes only members it declares itself; an inherited method checked on a subclass reads nil
  and silently deactivates the fix (F64). Verify where Src declares the method.
- Every `(class, method)` pair a module installs on or captures from appears in that module's
  own `Require` block, and a capture takes the original from the class that DECLARES the
  method. `Require` validates only what is declared, so an undeclared capture is a nil `prev`
  on every boot (F107). `tools/harvest_wrap_targets.py --check`, run by doccheck, goes RED on a
  capture-and-install site whose pair is missing; a full replacement with no capture is
  outside the check and relies on the inline sanity-check above. An allowlist entry there that
  carries a defect id is a receipt for an open case, never a permanent waiver.
- No `apply()` may assume a cold boot. Enabling the pack at the main menu is an in-place
  reload with presets already loaded and classes not yet built, and it is every player's first
  run (EF-025). So:
  - Apply-time code never constructs a class or preset object: no `Class:new{...}`, no
    `PlaceObj`, no class-table method call. `type(X) == "table"` does not prove a class is
    built; test `type(X.new) == "function"`, and prefer `PlaceObj("Class", {...})`, which
    fails soft where `:new` throws.
  - `OnMsg.DataLoaded` alone is not a trigger; it does not fire on the enable path. Use
    `SMROptInPack.DataPatch` for preset patches and `SMROptInPack.OnDataReady` for everything else.
    Both fire on `ClassesBuilt` / `ModsReloaded` too, so the callback must be idempotent.
  - Test both paths: a cold boot AND a run where the pack is enabled from the main menu (F87).
- Every wrapper is inert for a foreign object before it touches one. A wrapper on a shared
  method runs for every object of every class that inherits it, other mods' objects included.
  Decide "is this mine?" and hand the call to `orig` before reading a field, allocating or
  logging; a wrapper that inspects first is already a behaviour change for everyone else (§4a).
- Respect `SMROptInPack_Disabled["<id>"]`, the per-fix veto for users and other mods.
- Every `OnMsg` handler re-checks BOTH the registry status AND the veto itself (the A1 rule).
  Handlers install at file scope unconditionally and Register's veto only skips `apply()`,
  so a handler that mutates state without re-reading `SMROptInPack_Disabled[id]` defeats the
  veto. A handler that heals status never overwrites `"disabled"`.
- A target that can legitimately be absent before `DataLoaded` (presets, templates): track a
  `data_loaded` flag and latch `inactive` only after it fired. Before, absence means "not
  loaded yet" (F75); after, silence means reporting `active` forever on a removed target. On
  the enable path the flag can come only from the engine's `DataLoaded` global, because the
  message never arrives. Both shared runners do this for you.
- Never `Require` a per-game runtime global at apply time. `apply()` runs at the menu, so
  `Cities`, `UIColony`, `UICity`, `MainCity` or a map object is legitimately nil there, and
  the self-check would read it as "game code changed" and disable the fix on every boot
  (F110). `Require` is for what a game update could remove and that exists at apply time:
  engine globals, built classes, `(class, method)` pairs. A per-game global is a runtime
  condition: `rawget(_G, "Cities")` plus a `type(...) == "table"` guard inside the handler.

## 3. Savegame discipline

- No new persisted classes or GameVars unless unavoidable. A necessary persisted name tolerates
  its own absence so a save made with this mod loads after removal.
- A new persisted name may use `SMRFixPack_*` or `SMROptInPack_*`, but it is added to the
  inventory below and becomes equally unrenameable.
- Modules are sane on existing saves. Cleanup of state left behind is a separate, clearly marked,
  conservative one-shot `OnMsg.LoadGame` sweep.
- Never break saves for players who later disable the mod.
- The release ships with its exit paved: the player-facing uninstall procedure and the applicable
  standalone save-rescue artifact are ready before launch. The shared exit record and spec live in
  the fix pack's D13; its target list is the final residual set, never a predicted one. `[FAQ]`

### The persisted-name inventory — save contract

Every value below keeps its exact bytes forever. A removed writer does not release its name, and
nothing restores a writer merely to make a count agree. Rows for retired D06, D07 and D12 remain
contract. New persisted names join this table.

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

Rows 6–9 remain byte contract even though the mod-id change reset the owner's stored preferences
once. A vanilla field written by a module is not a new persisted name, but its save effect still
receives the §3/§3a analysis.

### 3a. Save safety — the save carries as little of us as possible, and the exit cleans the rest

By-value thread serialisation is documented, intentional engine design (EF-027), and mod
leftovers are an accepted fact of this engine. This pack aims above that norm with an
engineered exit, so §3a is a design discipline that minimises what the exit path must clean,
not a purity bar.

**The three-tier ethos, in order.** It supersedes any "leave no trace" framing elsewhere.
1. Leave no trace: prefer a shape that puts nothing of ours in the save at all; the layer
   ordering below exists to reach it.
2. Leave non-harmful trace: where something must persist, make it inert — named, bounded,
   disclosed, and incapable of doing anything after removal. An accepted residual.
3. Leave harmful trace only when 1 and 2 are both unreachable, and then fix it from outside
   with the save-rescue tooling (D13). A harmful residual is never simply accepted; it is
   accepted paired with its remedy.

**Disposition is per-site.** Every exposed site gets its own recorded disposition: repaired
in-pack where a layer 3 or layer 2 route exists, handed to the cleaner where one provably does
not. No site is deferred to the cleaner in advance: a hand-off is a valid disposition only
after the in-pack attempt was made and the route proven absent, never as a prediction or a
reason to descope. The authoritative exposed set and every disposition:
`reports/D13_EXPOSED_SET.md` §7, derived over both shipped trees, never an inherited count. A
new capturable site is dispositioned there.

**The mechanism (EF-023).** A mod function enters a save iff (a) its frame sits below a yield
on a blocked game-time thread, (b) it is held in a live local or upvalue of any captured frame,
or (c) it is stored in persisted state; synchronous code that stores no function values is safe
by construction. A captured orphan is not env-dead: an all-vanilla body keeps executing after
uninstall, bounded if it self-limits, forever if it loops. Every design answers: if this body
is captured anyway, does it die, expire or run forever, and would anyone notice?

**The orphan gate.** Every mod-owned thread body opens each wake with
`if not SMROptInPack then return end` and resets any vanilla state it set BEFORE its first
mod-created-name touch, so an orphan exits cleanly at a point we chose: zero errors, zero
half-done work. Long loops re-check the gate after every yield. The global-lookup helper
discipline stays underneath as the backstop: anything that slips past a gate dies rather than
running forever. Loud death is the backstop, not the failure mechanism.

**Choose the remedy in this order, 3 → 2 → 1. The ordering is binding.**

1. **Layer 3 — patch a synchronous input, keep vanilla's body.** The pack then has no body in
   the save at all. Where a defect can be repaired by changing what a shipped function reads
   rather than what it does, do that. Scope the wrapper by the narrowest thing that actually
   separates the call sites, and enumerate every caller before choosing the key: an argument
   is not automatically enough when two threads pass the same descriptor. `CurrentThread()` is
   available and global game-time threads are parked in a global of their own name, so
   `CurrentThread() == rawget(_G, "<Name>")` is a precise key where one is needed.
2. **Layer 2 — no mod code after a call that can block.** Do all work before the call, then
   `return orig(...)`; whether or not the frame is serialised, nothing is left to execute after
   removal. Post-work that is genuinely needed moves out of the command body into a message
   or periodic hook. This needs no engine guarantee; the earlier "tail calls remove our frame"
   claim is unobservable in this sandbox and is not re-derived or re-tested. Accepted
   residual: an inert serialised function that executes nothing.
3. **Layer 1 — `OnMsg.SaveGameStart` tear-down / `SaveGameDone` rebuild**, for what layers 3
   and 2 cannot reach (mods get this hook, EF-024). Build it last, only for what survives the
   other two layers; every module using it needs its own A/B plus a long-interval soak. The
   trap: autosaves take the same `DoSaveGame` path about once a sol, so a tear-down that
   restarts a loop resets a long timer before it can expire. Re-arm from a persisted deadline,
   never restart blind.

This binds new fixes as well as repairs. Anything that replaces a blocking body, wraps a
command method, or creates its own game-time thread states in its header which layer it is on
and why. Background: `reports/SAVE_SAFETY_REDESIGN.md`, F86.

## 4. What may be built here — opinionated modules, proven and reachable

The fix pack ships only unintended defects; this mod is where a player may choose an opinion. A
module here may be opinionated, but not unproven, unreachable, default-on or unclassified.

Every module links to an `agent/bugs/` entry and, before it ships:

- State in the entry and file header whether it is a behaviour choice, a numeric dial whose base
  is byte-vanilla, or a repair the donor declined because intent was ambiguous or a judgement call.
  The last kind names the donor verdict rather than implying the fix pack overlooked it.
- Enumerate callers, name the player action, and record R1 live · R2 conditional · R3
  latent-by-data · R4 unreachable · U unknown. Optionality does not make an unreachable module
  shippable; `tested` proves reachability only when play reached the state without debug surgery.
- Ship OFF or at base by default unless the owner changes that rule. OFF/base is byte-vanilla
  behaviour and says nothing about save cleanliness.
- Keep no cross-module dependency and no dependency on the fix pack. Each module works with the
  others off, and this mod works with the fix pack absent.
- Make balance behaviour coherent and predictable. "The player can turn it off" is not a licence
  for arbitrary constants; when intent is ambiguous, prefer sibling-code evidence and let the
  player make the final choice.

### §4-donor — the fix pack's §4, kept verbatim

This is the routing test: a defect that passes it belongs in the fix pack as a plain fix, not here
behind a toggle.

> ## 4. Only fix proven, reachable, UNINTENDED defects
>
> Every fix links to an `agent/bugs/` entry with file:line evidence, a recorded reachability
> tier and a positive intent statement. Before a fix ships:
>
> - **Intent first.** State why the shipped behaviour is unintended, citing at least one hard
>   tell: (1) player-reported harm; (2) dead code or dead validation — a computed value
>   discarded, a guard that cannot fire, a message nothing emits; (3) sibling contradiction —
>   the same author wrote it correctly elsewhere; (4) self-contradiction within one function or
>   preset; (5) an explicit dev comment. No tell → the defect claim is a hypothesis and needs a
>   keyboard observation before any fix is written. UI and affordance behaviours (hit-testing,
>   cursor feedback, input modes, whether two things are separately addressable) are hypotheses
>   by default: source reading has no validity there (F49). A behaviour found intentional is
>   tier **I**: record it, close it, write no fix.
> - **Then reachability.** Enumerate every call site of the defective function in Src;
>   eliminate the ones that cannot execute the defective body (class chain, guards, early
>   returns, template data); for each survivor name the concrete player action that produces
>   the precondition. Record the tier: R1 live · R2 conditional · R3 latent-by-data · R4
>   unreachable · U unknown, naming the observation that would settle it.
> - **Symmetry of proof.** Every tier states its evidence; an unenumerated R1/R2 is as unproven
>   as an unstated R4, and more dangerous, because "keep, it's live" is never revisited. Every
>   lettered sub-item of a bundled fix is a separate audit subject.
> - R1/R2 ship normally. R3 ships only as a §1.1–§1.4 patch; an R3 §1.5 replacement needs an
>   explicit owner decision (F24). R4 does not ship: record it `wontfix — unreachable` with the
>   search that proved it. U ships only with the settling observation queued as a playtest item.
> - A `tested` status proves reachability only if the playtest reached the state by playing.
>   Console surgery, `g_Consts` compression or `Cheat*` calls prove the fix, not the path; a
>   state producible only by console or debug injection is evidence for R4.
> - Re-check `git log` between assembling a verdict and recording it; playtest evidence lands
>   continuously.
> - No balance changes, no improvements, no opinions; those belong in other mods. When intent
>   is ambiguous, prefer the reading proven by sibling code in the same file.

## 4a. Scope: vanilla only

- Fix a defect only when a player could be harmed by it, now or after a game patch or DLC.
  Invisible, latent or unreported harm counts; "no player has complained" does not.
- Never fix or work around a defect another mod causes, or one whose only beneficiary is
  another mod. Only an owner one-off override, for something the owner asked for, changes
  this: ask explicitly and get an explicit yes for that one case, never inferred, never from
  precedent, never carried to a second case. An existing shipped fix is not precedent.

The test is who benefits, not how visible the problem is:

1. **Barred: a bug caused by another mod.** Never fix it, never work around it, never add a
   compatibility shim. If one is reported, record it and say whose it is.
2. **Barred: a vanilla bug reachable only from mod code.** No shipped caller anywhere, so
   lighting it up needs new calling code that only a mod can supply. Tier R4: record it
   `wontfix` with the search that proved no shipped caller exists (F28).
3. **Not barred: shipped code that runs in ordinary play whose defective branch is
   unreachable only because of data.** A patch, a DLC or new content can expose it without
   anyone touching a mod. Tier R3: a real fix (F29, F27, F31, F43).

R4 needs new code to become live: mod territory, barred. R3 needs new data, which ships with
patches and DLC: player territory, allowed. "For modder benefit" is never a reason to ship,
and a fix's own header or entry is not authority on whether it is mod-facing: judge by caller
enumeration, never by self-description (F29 called itself mod-facing and had four live callers).

**This-repo application:** the Relaunched Fix Pack is another mod for this test. A module here does
not work around fix-pack behaviour; report and fix that defect there.

## 5. Optional modules (`Opt_*`)

This section is the live specification for every shipping module.

An optional module is an opt-in behaviour change, off by default, with one Mod Options toggle:
`ModItemOptionToggle.name` == the Register id == the `default_options` key, all three
load-bearing. A module may instead expose `ModItemOptionChoice` dials (D09): then the option
names are not the Register id, the module registers without `optional` and reconciles itself
from `CurrentModOptions` on ApplyModOptions, CityStart and PostLoadGame, its base position is
byte-vanilla (module-owned modifiers removed by id, stale ones in loaded saves included), and
the choice strings are byte-identical across items.lua, metadata `default_options` and the
module's own maps.

- Hooks on class methods are installed at FILE SCOPE (classdef time, so they propagate through
  flattening) and gate per call on `SMROptInPack.IsActive(id)`; an apply()-time install is
  invisible to derived classes until restart. A wrap that resolves at call time (a global
  function, a UI-template Init) may stay in apply(); the header says so.
- Each file-scope install carries the same existence checks apply() uses, so a missing target
  degrades to apply()'s reason string instead of erroring at classdef time.
- apply() keeps only self-checks and the opt-in check, and returns the same reason strings
  whether or not the hooks installed.
- `on_activate` / `on_deactivate` run after a LIVE toggle flip only. Use them for state that is
  not a call path; call-path behaviour comes from the per-call gate. They are idempotent, and
  the reconciler logs their failures.
- The header states the real toggle semantics in both directions, including the first
  mid-session enable, and is updated when they change.
- Savegame footprint per §3, and a module OFF is byte-for-byte vanilla BEHAVIOUR. That is all
  "off" means: file-scope hooks stay installed and capturable with the toggle off, so never
  infer save-cleanliness from a toggle, in a claim or a test. An uninstall question is answered
  only by a Mod-Manager disable followed by a full process restart, or by removal; a disable
  followed only by a return to the main menu measures a mixed state, with the code live and
  the mod's persisted permanent already gone (PT-20 redo, 2026-08-14; the switches: EF-002).

## 6. Engine semantics that bind every fix

- `error()` and `assert()` in mod code report and continue; they do not unwind (EF-008).
  Never use them for control flow or guards; use early returns and reason strings. `pcall`
  still catches genuine runtime errors.
- Localisation: a T value is a table in dev and often a light userdata in retail. Copied
  shipped bodies keep their `T(id, ...)` calls byte-identical. New player-visible strings use
  `Untranslated("...")`; a raw Lua string where the UI expects a T value renders wrong or
  crashes (F14). Log and console text stays plain strings.
  - Never re-use a shipped translation id to change text: `T(id, text)` discards the literal
    whenever the id is in the loaded table, which in retail is always (EF-039, F98). F25 is not
    citable as localisation precedent.
  - To add to existing localised text, concatenate `shipped_T .. Untranslated("...")`; concat
    cannot delete, so correcting a wrong sentence still means replacing the whole string.
- The fix pack's future `ModItemLocTable` decision does not bind this mod; OI-14 remains open.
- Logging goes through `SMROptInPack.Log`, which escapes `%` for ModLog's second format pass; a
  direct `ModLog` call must escape it itself (`msg:gsub("%%", "%%%%")`).

## 7. Console platforms (Xbox / PlayStation / MS Store)

- No developer console, no file access, no companion-mod path: the `SMROptInPack_Disabled`
  veto and every log or console surface (`ListFixes()`, reason strings, "report this log") are
  invisible on console. Fail-safe behaviour never depends on the player seeing a message;
  self-deactivation is safe silently.
- Mod Options is the one universal, gamepad-native surface; anything a console player must be
  able to steer goes there or nowhere.
- Any enabled mod blocks all achievements on exactly PlayStation, Xbox and the Microsoft
  Store, and the pack can neither cause nor avoid it (EF-106). Player-facing text says
  "Steam and other PC versions", never "PC": Game Pass is a PC platform and IS blocked. Never
  write text that contradicts that disclosure.

## 8. Release hygiene

- One module per `Code/Opt_*.lua` file; the filename is `Opt_<Register id>.lua`. List every
  module explicitly in `metadata.lua` `code` and `items.lua`, in the same order.
- `00_Core.lua` loads first. Metadata's `code` order is the intra-mod order. Inter-mod order is
  the player's enable order (EF-054); require no position and give no player-facing load-order
  instruction.
- Before release, verify each target against the shipping `Packs\Lua.fpk`, test each module in
  game, update its D-entry status, and credit relevant prior art.
- Run the complete shipping test twice: with the Relaunched Fix Pack installed and with it absent.
  Record which released fix-pack version was tested.
- Treat the two mods as separate products: each has its own metadata, preview image, description,
  portal pass and console certification.
