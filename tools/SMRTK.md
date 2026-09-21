# SMRTK — the in-game toolkit, and preloading a sitting for it

**Reader: a worker seat with this repo open.** SMRTK is the panel the owner and an
attending agent drive at the keyboard, plus the six agent slots a preparing seat
loads *before* the game starts. Those are two different jobs and this file covers
both, in that order.

The probe harness — `SMRTest.RunAll`, verdict semantics, the ways a probe lies —
is [`TESTKIT.md`](TESTKIT.md). The unattended arming harness is
[`arming/README.md`](arming/README.md).

It lives in `B:\Dev\SMR\SMR-BugFixPack-TestKit`, a separate repo with **no remote,
local-only by design and settled**. Never raise a push there as owed. A pack lane
does not commit in it.

Open it with the SMR status bar (bottom-right) or **Ctrl-Shift-F11**; the bar
carries taint, armed count, errors and Quiet at a glance. There are **no popout
menus** — owner ruling, ck183. Selected controls also appear in the selected
object's infopanel, and the Selected page is its fallback.

## The panel

Seven pages, grouped by task. Tabs share a scrolling body; status and evidence
controls stay visible when the body collapses.

| tab (page id) | controls |
|---|---|
| Sitting | Read taint, Read eligibility; MARK, Flush + copy, Clear screen, Verbose, Screenshot + Mark, Stop disaster; the speed ladder and Cancel target stay in the top rows. **Verbose** shows or hides the game's on-screen console log, which every result line already reaches through `ConsolePrint`; it lights green while that log is visible and reads the real state, so opening the console lights it too. Off at boot on purpose (EF-097) |
| Run | target sol, the four triggers (sol, first Lua error, selected field, next rocket), Run until / cancel, shared field watch |
| Selected | curated methods led by Quick build on a construction site, grouped More Cheat / AsyncCheat methods, field watch, colonist traits, dump and pins |
| Slots & notes (`Agent`) | six numbered slots plus Scratch, note, pin A/B/C readout |
| World | disasters and cursor-armed meteors, quiet, fix / malfunction all, completion, rocket transit skip, supplies, people, research, domes |
| Saves | Save / Load / Override load A/B/C; process session and loaded provenance |
| Probes & logs (`Kit`) | gated probes (alphabetical picker), logger toggles, print tap, console, fingerprint, snapshot / diff, log tail |

Selected has source-name capacity **106/106**: 22 curated names and 84 More names
(72 `Cheat`, 12 `AsyncCheat`). ⛔ **That is not 106 simultaneous buttons and not a
complete replacement of vanilla's menu** — the current object's supported subset
determines its rows, and Add Dust chooses one alternative. More retains native
suffix labels. Editor/debug-dependent actions may be unavailable on retail. An old
selection or an active mechanized-depot animation refuses the affected action.
Delete and Destroy differ; test them on sacrificial objects.

⛔ **No achievement reset, runtime string compiler, arbitrary file reader or
vanilla eligibility verdict is available to this mod** (`EF-094`, `EF-096`).

### Evidence and taint

Every toolkit action writes a primary `[SMRTK] SMRTK_<Verb>` record, plus any
distinct auxiliary mark, state or persistence evidence. **These are intentional
test actions; never ask the owner to justify one.**

⛔ **Taint `CLEAN`/`TAINTED` is separate from `UNAVAILABLE:sandbox` eligibility.
No-taint does not prove eligibility.** End every boot with a `taint_read` *and* an
`eligibility` dispatch, so the boot's negative is a sample and not an absence.

Save/load/map changes disarm active work; load and map change clear pins. Save
provenance stores scalar attempt counters and the last record, not callbacks or
pin objects. A foreign-session load requires explicit Override — which still reads
metadata and never bypasses native load failure. Field watches poll scalars in
game time and cannot see every intermediate value. ⚠️ **Quiet and the DustDevils
logger conflict**: disarm Quiet before invoking console loggers.

### File map

| path | role |
|---|---|
| `Code/00_TestCore.lua` | probes and legacy console bootstrap/fallbacks |
| `Code/[1-6]*_Probes_*.lua` | the probe waves — [`TESTKIT.md`](TESTKIT.md) |
| `Code/70_SMRTK_Core.lua` | registry/dispatch, logger/ring, taint, console, click capture and persistence |
| `Code/71_SMRTK_Panel.lua` | shared fixed panel, pages and hotkey |
| `Code/72_SMRTK_World.lua` | World actions |
| `Code/73_SMRTK_Infopanel.lua` | Selected section/More and dock menus |
| `Code/74_SMRTK_Agent.lua` | `Bind`/`BindScratch`, pins, triggers, note and screenshot |
| `Code/75_SMRTK_Saves.lua` | native guarded save/load and provenance |
| `Code/76_SMRTK_Kit.lua` | probe preflight, loggers and evidence views |
| `Code/80_AgentSlots.lua` | **sitting-owned bindings, rewritten per sitting** — the rest of this file |
| `Code/90_Loggers.lua` | observability toggles and read-only state |
| `Code/91_Stress.lua` | the deterministic dispatch harness behind `SMRTest.Stress.*` |
| `Code/9[5-9]_*.lua` | leg support: auto-run flag, force-inactive, enable-path, fixture carry |
| `metadata.lua` | the explicit code list — **an unlisted file does not load** |

---

# Preloading a sitting — `80_AgentSlots.lua`

**Pull-only.** Use this half only when a sitting brief calls for preloaded slots.
`80_AgentSlots.lua` is agent-owned, rewritten for the next sitting, and **never
edited by a build link.** None of it is a fix and none of it ships.

## Read and scope

Read `docs/agent/STATE.md`, the sitting brief and its upstream notes, the
Cheats-on-playtest-saves section of `docs/agent/WORKFLOW.md`, `CLAUDE.md`'s
header, the `prompt-authoring`
skill's playtest instructions, `docs/agent/facts/EF-096.md` for sandbox reach, and
the kit's own `README.md`. Inspect 70's dispatch and 74's `Bind`/`Trigger` APIs
plus the **current** `80_AgentSlots.lua`. ⛔ **A prior binding is a claim, not
today's sitting.** Read the installed source for every new mutation leaf, and
inherit a matching build identity with `python tools/doccheck.py --emit-fingerprint`.

**IN:** the sitting-owned `Code/80_AgentSlots.lua`, its predictions, and the
brief's handoff. **OUT:** pack runtime, version and metadata; toolkit build files;
portal APIs; achievement and account state; live UI prototyping. Route defects to
the brief's report and fixing link. Never touch a peer's unstaged work.

## Pull-only helper reference

⛔ **Resolve every one of these against the current TestKit source before use.**
Logger state and toggles are `SMRTest.Loggers()` plus
`SMRTest.Log.{Meteors,DroneChurn,AutoCargo,CargoReady,WorkShift}(true|false)`;
one-shot reports are `SMRTest.Report{BrokenTrack,Reservations,Trains}()`; the
deterministic dispatch harness is `SMRTest.Stress.{Targets,Break,Report,Compare,
HealAll,Stop}`; the suite entry is `SMRTest.RunAll()`. Turn every logger off when
its leg ends.

For an attended MarsDebug `[install]` pass: fully close the game; arm
`Code/96_AutoRunFlag.lua` and its `SMRTest_AutoRunSetupOnly = true` switch; then
use Steam's **debugging mode for mod creators** launch choice. Expect vanilla
modal asserts and choose **Ignore All**. At the ready colony, require
`SMRTest.EnableIntrospection(debug)` to return `true`, then run
`*r SMRTest.RunAll()` and `FlushLogFile()`. Disarm both lines afterwards. ⛔ This
is a build-specific measurement (`EF-044`), **never a substitute for retail results.**

## Construction

Keep a todo list, one item per commit-and-verify unit: fixture and leaf reads;
slot bindings and predictions; gates, commit and handoff. Recheck log, pull/status
and active sessions in **both** repos. Run `tasklist /FI "IMAGENAME eq Mars.exe"`
separately before any `Code/` write; if the game is running, finish independent
document preparation and wait for it to close.

Rewrite 80 for this sitting using real `SMRTK.Bind(n, label, fn, opts)` functions,
slots 1–6 and optionally `SMRTK.BindScratch`. ⛔ **No strings compiled at runtime,
no load-time mutation, no automatic arms, no detached mutation threads.** Every leg
is **MARK → set up → act → DUMP → MARK**. Validate fixture, map, selection and pins
before mutation; a refusal must be `false, reason`, **not a success-shaped no-op**.
Give each slot a plain label and a named prediction. More than six legs may share a
slot only through an explicit documented stage — never silently overwrite a binding.

`ctx.sel` is the current selection, `ctx.pin` holds the A/B/C refs, `ctx.cursor` is
the current or captured map point, `ctx.state` survives armed phases, and
`ctx.mark` writes a distinct MARK. Validate `IsValid` on each use. Use registered
Run/Arm/Fire inside the executing thread; the dispatcher writes the primary result
and checks taint. Auxiliary DUMP fields go through `ctx.log("DUMP", fields)`.
Return useful after-state fields and **never print your own primary result**.
Register triggers disarmed; predicates are read-only, non-yielding and unlogged.
Lua's effect field is `["do"]`, not bare `do`. Document game-time cadence and
paused limitations.

For armed clicks use 74's shared listener contract with `on_click`/`on_disarm` and
explicit once-click versus repeat behaviour. Right-click cancels; save/load/map
change disarms; load and map change clear pins. Rebinding an armed slot refuses.
Callbacks and pin refs are not serialized. Save/load operations need real-time
context, and native stamp/completion requires running game time. Do not invent a
fit-test flag.

## Predictions and handoff

Write numbered predictions **before boot**: the exact SMRTK verb, action, status
and expected fields, the first-screen witness, the normal time and a 3× abort time.
⛔ **Generated ids, handles, session nonces and game time are variables, never
invented literals.** Preserve numeric MARK return indices for copying across later
marks and screenshots; string `CopySince` accepts only the current label. ⚠️ **A
truncated ring copy cannot replace the complete archived boot log.**

Declare clean-fixture needs and resource provisioning cost. No-taint is necessary
but eligibility stays `UNAVAILABLE:sandbox` on build 24995074. Stop on unexpected
taint, engine errors or mutation; **do not rerun to obtain a preferred verdict.**
Keep predictions separate from play evidence; no status promotion without
witnessing the leg.

📌 **Still owed:** the first sitting after TestKit `f5fa650` (smrtk 99's Code link,
2026-09-15, desk-only) also witnesses its four changes, each a prediction — a
mechanized depot's fill/empty record carries `before`/`after` numbers; the field
editor on Selected and Run reads dark text on a light box; a watch on a field the
object lacks is REFUSED naming the field, and 08b item 9's unrun leg then arms on a
field it HAS and fires; no console log overlay appears at boot. **Record each as
witnessed or NOT RUN, by name.**

Partial record, 2026-09-18 (the opt-in train-tests sitting, TestKit `8c69aff`–`adfe3ee`, after
`f5fa650`). **Field editor: NOT MET, from two owner screenshots only, not a log.** The Selected
page's box showed the `command` hint as white text on a light box. Depot fill/empty `before`/`after`,
the missing-field refusal and the boot overlay: NOT RUN. All four stay owed for a deliberate
sitting. Owner's words 2026-09-18, not a boot witness: *"nothing showing when i click things like it is
now"* — consistent with no overlay at boot; the item stays owed.

📌 **Still owed, from the 2026-09-17/18 maintenance round** (TestKit `82d4577`, `382c667`, `6b7edad`,
desk-only; the reasoning is in each leaf's comment block). **Record each as witnessed or NOT RUN, by name.**

- `open_domes` returns `terraforming = N parameter(s) set to 100%` and `law = Policy_OpenDomes
  activated`, and the domes open. ⚠️ Glass that stays shut while `law` reads activated is
  `Dome:UpdateOpenCloseState`'s `GetOpenAirBuildings` gate (`Dome.lua:1770-1780`) — a finding, not a
  dead leaf. During an active cold wave, *"It's too cold"* charges should stop ([EF-108](../docs/agent/facts/EF-108.md);
  how soon is untraced).
- `close_domes` returns the law deactivated and every parameter reduced by 10 points.
- `fill_storages` on a colony with a rocket returns `filled`, `skipped_rockets` of at least 1 and
  `failed`, and does not abort.
- **Group actions on a box-drag selection** (added 2026-09-20 on the owner's ask, kit `3abab0a`).
  Box-drag many units of one class; the Selected page then shows a `Group: <class> x<n>` section
  instead of the per-object leaves. Press **Group read** first: it mutates nothing and returns the
  member count, a `by_command` tally and the battery range. Then the mutating ones, each shown only
  when a member supports it: Delete all, Drain batteries, Recharge batteries, Malfunction all,
  Repair all, Dust all, Clean all. Expect `failed = 0`, and `skipped` above 0 only where a member
  genuinely lacks the call. Delete clears the selection on purpose (the wrapper asserts on a group
  of one). ⚠️ Recharge re-commands a drone left in `NoBattery`; if a drained drone stays down after
  it, that is the finding. Reassign, Salvage, Priority and On/Off are vanilla's own buttons on the
  multi-select panel and were deliberately not duplicated.
- `empty_storages` (**added 2026-09-20 on the owner's ask**, World page, beside Fill all storages)
  returns `emptied`, `skipped_rockets` and `failed = 0`, and the depots read empty. It is the fill
  leaf mirrored: same sweep, same rocket exclusion, same per-object `pcall`. ⚠️ The rocket exclusion
  here is **precautionary, not measured** — rockets do not override `CheatEmpty`, so they would run
  `UniversalStorageDepotBase.ClearAllResources`, which guards the supply side and then indexes
  `self.demand[resource]` unguarded (`StorageDepot.lua:735-751`, 1.1.0.403908): the same nil-demand
  shape that aborted the fill sweep. A `failed` above 0 names a depot class that still throws.
- Quick build on a pipe or cable run, and on a dome, where two presses may be needed. The leaf's comment
  block in `73_SMRTK_Infopanel.lua` says why each differs from the colony-wide cheat.
- **Verbose** lights green and shows the on-screen log, and its own press shows a `verbose=on` line;
  opening the console lights it too; `[_]` at the right end of the top row still shows whole.

Witnessed 2026-09-17, owner's words: `breakthroughs_reveal_all`, the tech point leaves, and Quick build
on an ordinary construction site.

## Probe preflight

If probes are needed, run the exact desktop stale-probe sweep — the procedure is
`docs/agent/WORKFLOW.md`, "Probe hygiene" — before trusting them; every hit must be
declared needed or made unavailable. Preload the sweep's actual command, output,
exit code and hit names, both HEADs, the check time and the brief **into the slot's
real function**. At invocation set session, sitting and game from live state, then
use `SMRTK.ProbePreflight`; ⛔ **no stale or empty invented attestation.** Any load
or map change expires it. Inspect 76 for the current evidence schema.

⭐ **The gate cannot see the tree's HEAD, so the sweep's own freshness is what keeps
the stamp honest.** The 24-hour window (WORKFLOW's ck184 gate, ruled 2026-09-15) is
calibrated against an 08b attestation that passed after five hours against a
*different* tree. An agent may recommend a sweep outside playtesting only if it can
give the reason and name the harm; **recommending is all it may do.** No agent,
gate or kit code refuses a boot, a `RunAll`, an upload or any other work over a
sweep's age, and none overrides the owner — a gate, not a hard rule.

## Gates, then the one line to the owner

```
python tools/parsecheck.py --dir B:/Dev/SMR/SMR-BugFixPack-TestKit/Code --quiet
python tools/doccheck.py
rg -n 'NetSyncEvent|LogCheatUsed' B:/Dev/SMR/SMR-BugFixPack-TestKit/Code -g '7*_SMRTK*.lua' -g '80_AgentSlots.lua'
rg -n '^\s*print\(' B:/Dev/SMR/SMR-BugFixPack-TestKit/Code -g '7*_SMRTK*.lua' -g '80_AgentSlots.lua'
```

doccheck GREEN; both `rg` runs zero matched lines, exit 1. ⛔ **An error is not a
negative gate** — include a positive installed-source control so a broken command
cannot read as a clean sweep. Recheck diff and status, stage exact paths, and
commit with `-F` plus a pathspec (shared hunks follow `CLAUDE.md`'s header). The
TestKit has no remote; push pack docs if they changed. Quote doccheck WARNs
verbatim in the handoff.

Then give the owner **one line**: *"start the game; the Slots & notes tab is loaded"*.
Relay the slot labels, the predictions path and both HEADs to the attending agent;
that agent reads and logs results and archives evidence. ⛔ **Do not ask the owner
to paste commands already provisioned in slots.**
