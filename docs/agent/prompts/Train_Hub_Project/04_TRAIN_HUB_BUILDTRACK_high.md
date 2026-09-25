# Train hub build 5: the hub builds track — second pass

**LIVE: pass 2** (2026-09-25). Pass 1 is `ad7d202`, its receipt
`reports/TRAIN_HUB_BUILDTRACK_20260925.md`. Its attended smoke was stopped after case 2 and the
owner sent the build back: spec §10 "Build 5 attended smoke, 2026-09-25" (`984be33`) is the record
this pass starts from. It is build 4's mechanism (`03_Drones/DESIGN.md`, the hub half in
`20_TrainHub.lua`) with a second trigger, on the pending list `SMROptIn_track_work` and its `kind`
field. Only one brief edits `20_TrainHub.lua` at a time; none other is live.

## Authority

- **Owner, 2026-09-19.** The hub **builds new track** from its own stock by dispatching its repair
  Wasps to the construction sites. **The gate: a line starts only once it is connected to the hub's
  network**; one placed where the hub cannot reach waits, and starts when the network grows to touch
  it. Cost is the normal element cost. Testing depth: a smoke test only.
- Build 4's rulings carry over (spec §10 "Drones L5" overtakes older wording): the feature must not
  replace one pain point with another, vanilla Wasps from the pit, engine flight. Both bans bind.
- ⚖️ **Owner, 2026-09-25, "1 is fine": the game's own group accounting.** Vanilla splits a placed
  line into construction groups (5 elements each in the smoke); only a group's leader holds its cost
  and work requests and its `Complete()` finishes the group (`ConstructionSite.lua:32,2671`,
  `Tracks.lua:460-474`, 1.1.1.405907; `reports/TRAIN_HUB_BUILDTRACK_BLOCKER_20260925.md`). **One job
  per native group**: pay its outstanding cost from stock, complete the leader after a build time
  scaled to its element count. Splitting, repricing or finishing single elements is not authorised.
  A stock-out signs the hub and waits.
- ⚖️ **Owner, 2026-09-25, in the smoke: "I think repairs take priority and we just increase the
  drone cap to 60 that should be plenty."** `Floor.HubRepairTune.MaxDrones` 30 → 60 (it counts the
  fleet and track flights together); the fleet chunks 5 / 15 / 25 are an earlier owner ruling and
  stay, so the added slots go to track work. **A repair dispatches before any queued build**, and
  builds never take the repair reserve. No frame-rate check (owner: a vanilla Drone Hub runs 120).
- ⚖️ **Owner, 2026-09-25: reworked networks are a core case, not an edge.** *"highly likely to
  happen with players as well as resource piles deplete and they change their bases around"* —
  cutting a line, extending or re-joining an existing track, re-routing to a moved station.

## What the smoke found (spec §10 has the log lines)

- **Case 1 PASS**: a fresh line from a hub stub to a far station outside every drone range; 23
  groups, 110 elements, 23 dispatched and done, no error.
- **Case 2 FAIL**: the owner cut a connected track and extended it with an unfinished section to a
  new station. Nothing was queued (`0 waiting`). Station 7042, joined to the hub's track, reads OFF
  in `HubTrackGraph`. Both its connector tracks printed `from false false to false false unbuilt 0
  broken 0`: `GetStartStation`/`GetEndStation` read `start_el.station`/`end_el.station`
  (`Buildings/Track.lua:194-200`) and return false on these tracks, so the station-to-station walk
  dead-ends, and the unfinished section sits on neither of 7042's track objects. That is the
  evidence, not a diagnosis: the worked cause is yours to find.
- Cases 3 and 4 were not run.

## End state

1. **Discovery and reachability survive reworked networks.** A connected unfinished section is
   queued, and stations beyond reworked track stay on the hub's network, whatever shape the player's
   edit leaves the track objects in. Establish from source and a live read what a cut-and-extended
   track actually looks like before choosing the fix. Check whether **repairs** share the blind
   spot, and fix them in the same pass if so.
2. **`MaxDrones` 60 and repair priority**, as ruled above.
3. **Desk smoke that models reworked track** (a track with no station at an end, a mixed track, an
   unfinished section hanging off a finished one), not only fresh station-to-station lines. A fix
   invalidates its own tests: rerun the whole suite (`buildtrack_smoke.py`, `flight_smoke.py`,
   `move_smoke.py`, `repair_smoke.py`) and preserve the outputs with HEAD.
4. **The attended smoke with the owner, all four cases from the start**, about five steps at a
   time: (1) a fresh line with no drone coverage, and a longer one for timing; (2) a line that
   waits, then starts on connection, **and** the cut-and-extend rework that failed; (3) a line whose
   middle an ordinary Drone Hub covers, with a forced stock-out at work end, then refill; (4)
   save/reload mid-job including a full restart, and the Track work toggle off/on mid-session. Ask
   the owner how the chunked fill-in looks and whether a line's total time feels right
   (`BuildTimePerElement` is the dial). Read console output from the newest
   `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-*.log` yourself when the owner says
   "flushed". `MaxDrones` set by console does not survive a restart.
5. **Record** in the build report and spec §10, with the session log archived byte-for-byte under
   `docs/archive/train_hub_build5_20260925/`; then hand back to the orchestrator.

The inherited drones-QA items C1–C6 and D14(g,h) keep the dispositions in the pass-1 report's
table; carry each with its trigger.

**Done means:** all four cases pass in the owner's game, the reworked-network case included, with
lines, element counts, times and the reload recorded.

## Start

`git log`, `git pull`. Authored on `10053e1`; an empty `git diff --stat 10053e1..HEAD --
tools/devmods/train_hub/Code/` means the code facts above hold. Put the work in the todo tool
before the first write, one item per commit-and-verify unit.

## Scope

In: the dev mod's track-work code and tests, TestKit slots (`tools/SMRTK.md`), the sitting, the records.
Out: building stations, drone flight, Module A, routing, the Capacity Network Upgrade (spec §4.10, not
authorised). Tunnels follow build 4's hide-and-show rule. Sittings use `train_hub_base` without saving over it (spec §10 "The standing test save").

## Stops

- The fix needs a new persisted name (ban 1): report before writing it.
- The fix needs a change to one job per native group, or taking over a group's accounting: report.
- A reworked track's state cannot be read reliably from Lua: report what was read and how.

## Do not claim

"Reworked networks work" from the one cut-and-extend the owner made. Claim the rework shapes the
smoke covered, in that colony.

## Lifecycle

Done when its smoke is recorded. The orchestrator then parks it in `Parked/` or deletes it, with its
row in `README.md` (owner, 2026-09-21).
