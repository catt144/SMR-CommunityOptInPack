# Why the hub's mini reactor flashes unpainted on a game-speed change

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/17_REACTOR_FLASH_INVESTIGATION_medium.md`
in a fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Start with `git log --oneline -5`,
`git status` and `git pull`.

## What the owner saw (2026-09-28; spec §4.10, grep `mini reactor flashes unpainted`)

For a frame or two, the train hub's mini reactor draws brown and unpainted instead of its blue
reactor palette. It seems to be tied to changing game speed. The owner caught it only by
frame-stepping a screen recording. It is our model, not a vanilla building.

The reactor is a visual only. Per `Parked/TRAIN_HUB_LOOK_high.md` (grep `ShapeshifterAutoAttach`),
it is vanilla's `FusionReactor` entity attached as a `ShapeshifterAutoAttach`, scaled 75%, with its
palette set by our code in `tools/devmods/train_hub/Code/20_TrainHub.lua` (grep `eactor`). Treat
those details as claims and re-read them.

## The question

What makes the reactor lose its palette for a frame, and what is the smallest fix? Leads, not
prescriptions:
- **the owner's read, first:** *"honestly it sorta looks like a building covered in dust"*. Vanilla
  draws dust on buildings (the maintenance/dust-storm look). Check whether the attached reactor
  gets a building's dust state or dust material reset, or briefly fully dusted, when game speed
  changes, and whether the hub passes its own dust to its attaches;
- something re-creating or re-colouring attaches on a speed change or a `SetGameSpeed` message;
- a periodic re-apply of the palette with a gap between the reset and the set;
- the `FusionReactor` entity's own state or animation switching;
- the TestKit's slot 6 stream or another of our threads touching the hub.

Archived game source is at `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`; cite lines with
that build. Where the cause can only be confirmed in the game, write the owner **one short
attended check**: a slot press, or a slot plus a speed change, with a prediction. Avoid anything
that needs frame-stepping a recording.

## Done

A short report, `docs/agent/reports/TRAIN_HUB_REACTOR_FLASH_<date>.md`, with the cause (SOURCE or
MEASURED, labelled), the fix, and a pointer line under the sighting in spec §4.10. If the fix is
small, make it with a desk test that a mutation of the fix fails. Otherwise, describe it and stop.
Run `python tools/doccheck.py` before each doc commit. Keep a live todo list before any write.

## Scope and stops

**In:** the reactor attach and its palette. **Out:** the rest of the hub's look, the model and
textures (`B:\Dev\SMR\SMR-Assets`), train movement, and the train cargo upgrade (brief `16` is
editing `20_TrainHub.lua`, so keep your edit to the reactor's own code). Report anything outside
this scope without editing it.

Stop and report instead of continuing if:
- the cause is in the asset (entity or texture) rather than code;
- the fix would touch code brief `16` is changing.

Claim limit: a desk result cannot show what renders on screen. Say so, and leave the rendered
claim to the owner's check.

References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md` (header first), skills `doc-editing`,
`smr-bug-library`.

## Sitting (2026-09-28, log `Mars.exe-20260928-22.20.16-6aad2d75.log`)

Slot 2 armed on a `FusionReactor` with `dust=255` for 2000 ms and restored `dust=0` (lines
3330 to 3342). Owner: *"slot 2 is also correct, that's the exact look I think."* The game-speed
change watch has not been reported. The brief is kept until the owner accepts without "I think".

## Lifecycle

One-off. The orchestrator deletes it, with its README row, once the owner accepts the fix or the
finding.
