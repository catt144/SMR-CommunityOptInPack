# Two load-time errors in the dev hub — fix both, prove both gone

## Authority

Owner, 2026-09-21, from their own reading of the game log after the concept import: fix these two.
Nothing in this mod is frozen (`CLAUDE.md`, owner 2026-09-18), and the dev mod
`tools/devmods/train_hub/` is dev-only and ships to nobody, so no persisted name and no ship gate
is at stake here. This is a code fix on a settled cause, not an investigation: both causes are
already measured and cited below.

Out of scope and NOT yours: the hub's look, its textures, the model, and the footprint-radius
question the owner is ruling on separately. Do not touch `SourceData/`, `Entities/`, `Meshes/` or
`Textures/`.

## Start

`git log`, `git pull`. Authored at `4126be3`. An empty
`git diff --stat 4126be3..HEAD -- tools/devmods/train_hub/Code/` means these facts still hold.

Put both fixes in the todo tool before the first write, one item per commit-and-verify unit.

## The two defects, both MEASURED 2026-09-21

Both were read from the owner's session log,
`%APPDATA%\Surviving Mars Relaunched\logs\MarsDebug.exe-20260921-12.40.03-6a91a1cb.log`, on game
build **1.1.0.403908**. Both fire on the dev mod's load path, every load.

**1 — Ambiguous inherit, line 161.**

```
[LUA ERROR] SMROptInTrainHubBase.ShouldShowNotConnectedToPowerGridSign
            ambiguously inherited from ElectricityProducer and ElectricityConsumer
```

`Station` already inherits `ElectricityConsumer` (`Station.lua:48-50`), and
`20_TrainHub.lua:95` adds `ElectricityProducer`. Both parents define the method
(`ElectricityConsumer.lua:171`, `ElectricityProducer.lua:18`), so `ResolveComplexInheritance`
cannot pick one. All four citations are that build's archived tree,
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src`.

⭐ **The same diamond was already solved once in this file:** `SMROptInTrainHubBase` overrides
`ShowUISectionElectricityGrid` at `20_TrainHub.lua:133` for exactly this reason. Read that override
before writing yours, and match whatever it decided about which parent's behaviour the hub wants.

**Your call:** which parent's sign the hub should show, or a hub-specific answer. The hub is the
single `+70/-10` power-grid object (spec §10), so it is both producer and consumer in practice —
decide what a player should see when it is off-grid, and record the reasoning in the commit
message, not only in code.

**2 — Engine assert from the dwell hook, line 275.**

```
A:\spark-release\HGE\luaQuery.cpp(725): ASSERT(m_pMap) failed
  [C](-1): method MapForEach
  CommonLua/Core/map.lua(1127): global AllMapsForEach
  Mods\SMR-TrainHubDev\Code\20_TrainHub.lua(80): global WaitWakeup
```

The `WaitWakeup` wrapper installed at `20_TrainHub.lua:76-89` calls `AllMapsForEach` on **every**
wakeup whose timeout falls in its window, including during the startup sequence when no map is
loaded. The guard at line 72 checks that the API *exists*; it does not check that a map does.

Note the wrapper is global and wraps a vanilla function, so it runs for every caller in the game,
not only for trains. Keep the fix cheap: the fast path must stay fast.

## Done when

- Both messages are absent from a fresh session log, and the hub still dwells and still shows its
  power state. A log with neither line, from a run that actually loaded a map and ran a train, is
  the evidence.
- ⛔ Grep the log with the full token — `[TrainHubDev]` for this mod's own prints, and the exact
  error strings above for the two defects. Both mods are loaded in the owner's rig as normal.
- Prove the absence: grep the presence side too. A run that produced no `[TrainHubDev]` lines at
  all proves nothing about the errors.

The owner runs the game; you do not. Prepare the change, say exactly what you need looked at, and
hand over a paste-safe console line if you need one read.

## Stops

- **The `ShouldShowNotConnectedToPowerGridSign` answer is not obvious from `:133`'s precedent.**
  Report both options with what each shows a player, and let the owner choose. It is a one-line
  difference to them.
- **A map guard cannot be made cheap** — for example, the only reliable test costs a call per
  wakeup on a hot path. Report the cost and the alternatives; do not silently accept a hot-path
  regression to remove an assert.

## Do not claim

Not that either error is "fixed" because the code looks right or a desktop harness passes: both are
load-time errors and only a real session log shows them gone. Not that the assert is harmless
because the game kept running — it is an assert on a debug build, and its absence is the bar.

⛔ Note the offline smoke `tools/devmods/train_hub/tests/traffic_smoke.py` currently FAILS on this
build for an unrelated reason recorded in `Parked/TRAIN_HUB_MOVE_high.md`; its `line_radii` print comes
from stubbed geometry and is not the game's number. Do not use it as your pass signal, and do not
"fix" it here.

## Lifecycle

Done when both errors are proven gone in an owner session log. Lifecycle: the orchestrator decides, once this is fired and done: park it in `Parked/` if it is kept for touch-up work, or delete it; either way its row in `README.md` follows (owner, 2026-09-21).
