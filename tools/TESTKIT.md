# The Test Kit — arming, running and reading a measurement leg

**Reader: a worker seat with this repo open.** This is the pack-side view of the
companion mod that measures the pack. It tells you what to reach for, and — the
part that costs sessions when it is missing — **what a verdict from it licenses.**

The kit itself is `C:\Dev\SMR-BugFixPack-TestKit`, a separate repo with **no
remote, local-only by design and settled**. Never raise a push there as owed, and
never commit in it from a pack lane. Its own `README.md` is the build-state
document; this file is the durable part, and it is here because the kit is
unreachable to anyone not sitting at that machine.

The in-game toolkit — panel, pages, agent slots — is [`SMRTK.md`](SMRTK.md).
The unattended arming harness is [`arming/README.md`](arming/README.md).
Probe **hygiene** — the stale-probe sweep, the `TEMPORARY` marker, the
`PROBE SWEEP:` commit line — is policy and lives in
`docs/agent/WORKFLOW.md`, "Probe hygiene". Read it before a sitting; it is not
restated here.

```
mklink /J "%AppData%\Surviving Mars Relaunched\Mods\SMR-BugFixPack-TestKit" C:\Dev\SMR-BugFixPack-TestKit
```

Enable it in the Mod Manager alongside whichever packs the leg needs. Open the
console with Enter / Alt-Shift-C, or the toolkit with Ctrl-Shift-F11.
Each pack's own junction and its console status line (`SMRFixPack.ListFixes()` /
`SMROptInPack.ListFixes()`) are in that repo's `docs/agent/WORKFLOW.md`, "Install for testing".

## What it provides

| call | what it is for |
|---|---|
| `SMRTest.RunAll()` | one probe per fix, printing `PASS`/`FAIL`/`SKIP`/`ERROR` |
| `SMRTest.<ProbeId>()` · `SMRTest.List()` | one probe · every probe's name |
| `SMRTest.Log.<Name>(true/false)` · `SMRTest.Loggers()` | observability wrappers that print what a system decided (work-shift verdicts, meteor cadence, drone churn, lander cargo requests) |
| `SMRTest.Report*()` | one-shot savegame reports: residence reservations, broken track repair sites, train prefab counter |
| `SMRTest.Stress.*` | `Targets`, `Break`, `Report`, `Compare`, `HealAll`, `Stop` — the deterministic dispatch harness |

⛔ **Turn every logger off when its leg ends.** A logger left armed writes into
the next leg's log and is indistinguishable there from the thing being measured.

The regression harness is not `RunAll` — it is **`RunAll` run twice**, once with
the fix pack **disabled** (expect FAILs: the bugs reproduce) and once **enabled**
(expect PASSes). One leg alone is half an answer. Resolve every helper name
against the kit's current source before you use it; a name recorded in a prior
brief is a claim about a tree that has since moved.

## ⭐ One kit, three mods — a leg that quotes one line describes a third of the rig

The `Opt_` modules live in `SMR-OptInPack` (count: its `python tools/doccheck.py --emit-counts`); a third mod, `SMR-CommunitySaveRescue`,
cleans up after both. **The kit is not forked** — it serves all three, and a probe
change is made once, in it.

| | fix pack | opt-in mod | save rescue |
|---|---|---|---|
| registry read | `SMRTest.FixStatus(id)` | `SMRTest.OptStatus(id)` | `SMRTest.RescueStatus(id)` (its registry is `modules`, not `fixes` — a cleaner has no fixes) |
| "not there" guard | `SMRTest.FixMissing(id)` → **FAIL** | `SMRTest.OptMissing(id)` → ⛔ **SKIP** | `SMRTest.RescueMissing(id)` → ⛔ **SKIP** |
| source attribution | `SMRTest.FromFixPack(fn)` | `SMRTest.FromOptInPack(fn)` | — (the rescue installs no wrappers) |
| `RunAll` gate line | `fix pack present: %d/%d fixes active` | `opt-in pack present: %d/%d modules active` | `save-rescue present: %d/%d modules active` |

- ⛔ **`RunAll` prints all three lines.** They are separate lines rather than one
  merged line so that every existing grep for `fix pack present:` keeps working.
- ⛔ **`OptMissing` and `RescueMissing` SKIP, never FAIL.** A leg run with only the
  fix pack installed is a legitimate configuration, and eight probes screaming FAIL
  at it would train everyone to ignore them. A module that IS registered and did
  not come up still FAILs.
- ⛔ **Grep logs with the FULL bracketed token** — `[CommunityFixPack]` vs
  `[CommunityOptInPack]` vs `[CommunitySaveRescue]`. `Pack]` matches two of them.
- ⛔ **The `SMRFixPack_*` string literals inside the opt-in probes are NOT stale.**
  Those field names and modifier ids entered players' savegames before the split
  and keep their exact bytes forever; a probe "helpfully" renamed to match the new
  namespace would pass against a broken build. `FromFixPack` and `FromOptInPack`
  are each deliberately narrow for the same reason: a mix-up reads FALSE rather
  than accidentally true.
- ⛔ **The rescue probes never touch the real save.** The clean pass walks `Cities`
  and `UIColony`; a forced pass on a live colony would really strip 1200+ real
  timestamps and really remove a Drone dial's boost from the session in progress.
  Every probe that exercises the pass stubs a synthetic city and colony through
  `WithGlobals` first. The meteor-restart half is deliberately not exercised when
  the thread is dead — proving it would mean re-rolling the owner's real 35–115 h
  timer. That leg belongs to a fixture save, not to the suite.

## Probe kinds — what each verdict is evidence of

| kind | what it measures |
|---|---|
| `behavior` | drives the patched code with synthetic input; a real fixed/unfixed discriminator, no gameplay needed |
| `install` | asserts the patched function now comes from the fix pack — used where calling the real code would fire a disaster, complete a milestone, … |
| `state` | inspects the loaded savegame; SKIPs when the save has no relevant objects |
| `manual` | always SKIPs, printing its setup steps |
| `retired` | the module is GONE because 1.1.0 fixed the defect itself. The body still observes the defect **on vanilla**, so the verdict reads backwards |

`retired`, spelled out, because it is the one that gets misread:
`PASS` = vanilla really did fix it, the REMOVE verdict confirmed in-game ·
`FAIL` = the defect is still there, so a REMOVE was **wrong** and players lost a
fix — a finding, never a probe bug · `ERROR` = the stubs are 1.0.7-shaped and
1.1.0 moved the function under them, which is evidence of **nothing**. Guarded by
`SMRTest.FixRetired`, which inverts `FixMissing`: a registered module is the failure.

⛔ **A `retired` probe must give the SAME verdict pack-off and pack-on.** It
measures vanilla, and no module of ours is involved on either leg. A leg where
the two disagree is itself the finding, not a flaky probe.

## ⛔ Read before trusting a verdict — three ways to be confidently wrong

All three produced a *confident* wrong verdict in this project. The second and
third are repaired and stay listed because the failure shape recurs.

1. **A probe whose `run` falls off the end returns nil, and `SMRTest.Run` turns
   nil into SKIP with an empty message** (`00_TestCore.lua`). It reads as a
   deliberate skip, not a missing verdict, and it silently cost wave 6 its entire
   automated coverage until 2026-07-29. Every probe needs an explicit
   `return "PASS", …`. Audit by comparing `Register(` and `return "PASS"` counts
   per wave file. **A baseline leg can never catch it** — the `FixMissing` guard
   returns FAIL before the tail runs — so only a FIXED leg can.
2. **A probe that reads its own baseline from live state.** `DroneStatDials` took
   `local base_carry = consts.DroneResourceCarryAmount` and asserted `base_carry + 1`,
   which holds only when the account's dial already sits at base. Mod Options dials
   are **account-persistent**, so a playtest that left a dial off-base FAILed the
   probe against a healthy pack — observed 2026-07-30, `DroneResourceCarryAmount
   3 → 2 (want 4)` while the module logged `applied` and the leg had zero
   `[CommunityFixPack]` error lines — and it could false-PASS the same way.
   Repaired 2026-07-30 by forcing both dials to base through the real Apply path,
   taking the baseline from that state and restoring the leg's entry values.
   ⭐ **A probe must set the ambient state its verdict depends on, never read it and hope.**
3. **A probe that asserts our MECHANISM breaks the moment the mechanism changes
   branch.** Four instances at once, repaired 2026-09-09: 1.1.0 made three modules
   reach their result a different way and each module was healthy while its probe
   reported a confident `FAIL` — `SaintBlessing` no longer rewrites
   `Saint.modify_trait`; `PayloadTemplateRefill` moved its stamp inside a real-time
   thread the probe stubbed to a no-op; `ShelterReflex` lost half (a) on purpose.
   A fourth, `GeneForging`, asserted through an injected `unit.city.colony` that
   1.1.0's now-parameterless `GetRareTraitChance` stopped reading at all — that one
   **could not pass in any research state.** All four read as regressions and none
   was one. The related shape is a probe whose stubs match the OLD signature:
   `LandscapeUnitFilter` and `VacuumWalks` raised `ERROR`, which at least does not
   impersonate a regression.
   ⭐ **Assert the OUTCOME, not the mechanism.** Ask "does the player-visible result
   hold?", never "did we install the wrapper we installed last year?". An `install`
   probe is the deliberate exception, and it is deliberate precisely because
   calling the real code would be worse.

⭐ A fourth shape lives one folder over and is the same class: a probe calling a
`SMRTest` helper its own file never aliased compiles fine, then indexes a nil at
run time and dies mid-measurement. `tools/aliascheck.py` is the static check for
it; `tools/parsecheck.py` proves a file PARSES and nothing more.

## Unattended legs

An unattended in-game measurement is armed through `tools/arm_leg.ps1` against a
manifest in `tools/arming/legs/`. Its rules, its gates, and the failure behind
each one are [`arming/README.md`](arming/README.md) — read it rather than
improvising, and note in particular that **every payload lands in the kit, never
in the fix pack** (the pack ships zero diagnostic code), and that an armed tree
is deliberately uncommittable: a `TEMPORARY` marker anywhere in `Code/` or the
kit's `Code/` makes `doccheck` RED and the pre-commit hook blocks. **If doccheck
is RED and you cannot see why, you are still armed.**

⚠️ Before any leg on 1.1.0: `EF-079` — 1.0.7 saves cannot load on 1.1.0, and every
payload in `arming/` was written against 1.0.7 fixtures, so a 1.1.0 leg needs a
colony provisioned from scratch (hours). ⛔ `Mars.exe` must not be running when you
arm or disarm; you share one game with other sessions and with the owner.
⚠️ A log copied while the game is RUNNING is a PARTIAL log — re-copy after the
process exits before quoting any count or rate. That produced two wrong counts on
2026-09-08: a "1" that was 6, and a "30" that was 157.
