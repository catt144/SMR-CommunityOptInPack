# Train hub `traffic_smoke.py` repair — 2026-09-28

Brief: `prompts/Train_Hub_Project/18_TRAFFIC_SMOKE_REPAIR_medium.md`. Authority: owner,
2026-09-28, *"lets get this done"*; movement accepted 2026-09-21. **Verdict: the test was
stale; the code is right. Test repaired in `3d328c4`; no file under
`tools/devmods/train_hub/Code/` changed.** Desk evidence only (mocked engine in lupa).

## Why it failed (`-10800 != 0`)

Two stale inputs, both from 2026-09-20:

1. **Wrong arrival path.** `3ec2f0b` gave the hub its own `SMROptInTrainHubBase:TrainArrive`
   (entry, lane slide, siding). Vanilla calls it by method dispatch
   (1.1.0.403908 `Train.lua:390`, `next_station:TrainArrive(self, track)`), so vanilla
   `Station:TrainArrive` never runs on the hub. The smoke kept calling `Station.TrainArrive`
   directly.
2. **Retired geometry.** Its mock body put connectors 4 hexes (40 m) out. `ac6458d` set the
   transition pause at 48 m for the longer body, with connectors at 60 m (`move_smoke.py` asserts
   `60*guim`). On the 40 m mock the pause lies outside the connector. The first arrival leg ran
   outward: rotation 0, start-side hub, connector 1, segment 1 of 2 went from about 40 m to
   48 m, at −10800′ against the parked yaw.

The history agrees. The current smoke, run against old `Code/`, passes at `3ec2f0b~1` and at
`b02db74`. It fails from `3ec2f0b` on: first `578 != 0`, then `-10800 != 0` at every later
commit that touched the hub file, up to `f556ee8` (2026-09-24).

## What changed in the test

- The smoke now runs `h:TrainArrive` on `move_smoke.py`'s six-hex body. The shared `STUBS`
  string is unchanged, because `move_smoke.py` imports it.
- **Assertion, kept strong.** The old check wanted every arrival segment along the final yaw. The
  owner-accepted sideways slides (the lane slide and the siding slide, eight 150 ms samples each)
  can never meet that. `arrival_heading` replaces it and requires all of these:
  - no turn on arrival;
  - parked within 2′ of inward;
  - no segment moving backwards by more than 2 units;
  - every non-slide leg within 5′ of the line;
  - a forward total above 0;
  - parked at `Stop<k>` to within 2;
  - at least 10 segments.
  It runs on all 72 cases (6 rotations × both track ends × 6 connectors).
- **Mutations, 216, all rejected, each for its own reason** (72 cases each):
  - `pause_beyond_connector` (the −10800 shape) fails as "moved backwards";
  - `backs_in` fails as "parked facing … off inward";
  - `turns_on_arrival` fails as "arrival turned".
- **Routes** (66 stop and pass paths, which feed the oracle) had also gone stale behind the arrival
  failure:
  - `HubRouteTrain` now ends on vanilla's `WaitTraverseElement` leg, so the smoke carries
    `move_smoke.py`'s track fixture.
  - One correction to that fixture: an element's angle faces its track's start station, because
    vanilla faces `el:GetAngle()+10800` when `step==1` (1.1.0.403908 `Train.lua:589-591`).
    `move_smoke.py` builds only end-side hubs, where that angle is outward.
  - The route end is now the next element's `Enter1`, and the final yaw is compared mod 21600.

## Results

`python tools/devmods/train_hub/tests/traffic_smoke.py` at `3d328c4`: `PASS: 72 lane/reservation
cases; 216 arrival mutations rejected; 66 executed routes; concurrency assertions passed.`

Every `tools/devmods/train_hub/tests/*_smoke.py`, each run with `python <file>` and scored on exit
code, at `3d328c4` with a clean tree: **21 members = 21 passing + 0 failing.**
No other smoke depended on the stale expectation.

Limits: mocked engine; no game launch. The route paths now differ from pre-09-20 evidence
files, so the oracle's two-train counts are not comparable with older runs.
