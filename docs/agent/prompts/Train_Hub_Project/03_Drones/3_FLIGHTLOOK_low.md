# Drones chain, link 3 — the owner tunes the flight by eye

**Link 3 of the `03_Drones` chain** (`README.md`). **ATTENDED: the owner is at the keyboard.**
Read `DESIGN.md` and your `## Notes from upstream`. `git log`, `git pull` both repos first.

## Authority

The owner's method (2026-09-20): rough and in the game fast, then dialled in by eye. Link 2 built
the flight behind named constants; this sitting sets them. No redesign, no new mechanism.

## End state

1. About **five steps at a time** for the owner, and a console tuner for each constant, the way the
   arm-light tuner works (`SetHubLightTune` is the pattern).
2. The owner judges, in one sitting: hover height over the track, travel speed, the launch and the
   landing, the work pose at the break, and clearance at a station, the hub's hoods, a portal and a
   tunnel.
3. Every value the owner settles becomes the new default in `Code/30_TrainHubDrones.lua` and is
   committed, with the owner's own words for why in the commit message.
4. The game cannot turn autosave off: after one, the owner re-presses the armed slot.

## Live work list

One todo item per commit-and-verify unit.

## Scope

In: the tuner, the sitting, the settled constants, the record. Out: `20_TrainHub.lua`, dispatch,
economy, art, anything the owner did not ask for in the sitting.

## Stops

1. The flight is wrong in a way tuning cannot fix: stop the sitting, record what the owner saw, and
   hand it back to a rebuilt link 2 rather than patching live.
2. The owner runs out of time: commit what is settled, and say in your notes which constants are
   still the agent's guess.

## Do not claim

Do not claim a value is the owner's unless they said so in the sitting; relay their words verbatim.

## Notes from upstream

*(link 2 appends here: the constants, what each does, how to call the tuner)*

## Lifecycle

Append the settled values into link 4's notes, then **delete this file and strike its row in
`README.md` in the same commit**.
