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

- L2 implementation/report: `docs/agent/reports/drones_chain/L2_FLIGHT_20260922.md`.
  OI-25 is approved: offset floor/rim column `point(-310,180,0)`, exit local z +1000.
- Console [NEVER RUN in game]: select the hub, `SpawnHubDrone()`; select a track element/site,
  `SendHubDroneTo(SelectedObj)`; `ReturnHubDrone()` lands/removes it. Read
  `SMROptInHubFlight.Status()` for the absolute arrival/work/removal deadlines.
- Tuner [NEVER RUN in game]: `SetHubDroneTune("HoverHeight", 300)` after landing. Other names:
  `Speed=6000`, `LaunchTime=3000`, `LandingTime=3000`, `WorkTime=5000`. Height is engine units
  above rail origins; speed units/game second; times game ms. These defaults are guesses.
  `Palette=false` is deliberately untuned; the report explains the optional four-colour array.
- Required native checks: station connector spans, hoods, pit, portals and a tunnel, with the
  worst measured clearance/location recorded. L2 has no live clearance result. Mesh checkpoint
  `24ffa82` changed L1's geometry input; do not promote the old margins to current clearance.
  Tunnel concealment uses the deeper inner enter spot, an approximation to verify by eye.
- After a Mod Editor import confirm metadata still lists `Code/30_TrainHubDrones.lua`. If not,
  stop and provide that one-line registration fix; never merge its code into `20_TrainHub.lua`.
  Concurrent commit `24ffa82` includes the line but is not import-survival evidence.
- Saves cancel the console visual. Relaunch/re-send after autosave; L4 owns persisted resume.
  Mocked smoke passed; native rendering, animation, AI suppression and palette remain untested.

## Lifecycle

Append the settled values into link 4's notes, then **delete this file and strike its row in
`README.md` in the same commit**.
