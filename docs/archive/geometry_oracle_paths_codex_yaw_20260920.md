# Geometry oracle paths run, 2026-09-20: blind Codex derivation (yaw)

Model gpt-5.6-sol, OpenAI Codex v0.149.1, `codex exec --skip-git-repo-check --sandbox workspace-write`, reasoning effort high. The model was given the prompt below and verbatim excerpts of the named files from `C:\Dev\SMR-SrcArchive\1.1.0.403908\Src\Lua` (and, for the yaw run, `corpus/lua_current_6123ae7.lua` lines 166-187, 247-253, 265-269), with no hint of the answer. Judged in `docs/agent/reports/GEOMETRY_ORACLE_20260919.md` §11.

## Prompt

```
You are analysing Lua source excerpts from a game (Surviving Mars: Relaunched, train DLC). The files in this directory are verbatim excerpts: Train_excerpt.lua, Station_excerpt.lua (the game), and ModStation_excerpt.lua (a mod's station class that computes its named spots in code; `opposite(idx)` maps 1<->2, 3<->4, 5<->6, and each connector idx lies on a straight line out from the station centre, with connector idx and opposite(idx) on opposite sides of the centre). Read all of them. Do not search the internet. Work only from these files.

Facts you may take as given: angles are arc-minutes (10800 = 180 degrees). CalcOrientation(a, b) is the heading of the vector from a to b. SetPos(pos, time) interpolates the object's position over `time` and does not change its orientation. "Yaw" below means the heading the train model faces.

Questions. Answer each from the code, citing file and line numbers from the excerpt headers for every step.
Q1. While a train moves along a straight track (Train:WaitTraverseElement, the non-curved branch), what is its yaw set to, relative to its direction of travel?
Q2. During Station:TrainArrive (element -> Ramparrive spot -> Stop spot), does anything change the train's yaw? What yaw does it hold while it slides, relative to the heading it arrived with?
Q3. During Station:TrainDepart onto a DIFFERENT track than it arrived on (Stop -> Rampdepart<j> -> the departure element's Enter spot), does anything change the train's yaw before it reaches the departure element? What yaw does it hold during those two slides? When is its yaw next set, and to what?
Q4. During Station:TrainDepart onto the SAME track it arrived on: what position and what yaw is the train given first? For the mod station class, express that yaw relative to the direction from the station centre toward connector idx (the connector it is about to leave through).
Q5. During Station:TrainTraverse (pass-through), what yaw does the train hold while it slides to the departure element?
State any assumption your answers need that the excerpts do not settle (for example what WaitChangeDir does when its yaw argument is nil).

Write your full answer to a file named answer.md in this directory, and also print it.
```

## Answer (verbatim)

### Train/station yaw analysis

#### Q1 — Straight-track traversal

`Train:Traverse` uses `step = 1` when travelling from the track's start station and begins at element 1; in the other direction it uses `step = -1` and begins at the last element (`Train_excerpt.lua`, Units/Train.lua 649–652). `WaitTraverseElement` then moves from `elements[element_idx]` toward `elements[element_idx + step]`, specifically to the latter's direction-dependent `Enter` spot (`Train_excerpt.lua`, Units/Train.lua 522–523, 555; 665–666, 672–674).

In the non-curved branch, immediately before the positional interpolation, the code sets

- `yaw = round(el:GetAngle() + 10800, 3600)` for `step == 1`; and
- `yaw = round(el:GetAngle(), 3600)` for `step == -1`.

That follows directly from the conditional 10800 offset and `SetRollPitchYaw` call (`Train_excerpt.lua`, Units/Train.lua 578–585). Thus the code flips the element angle by 180 degrees when the train traverses in the increasing-index direction and does not flip it in the decreasing-index direction.

Under the track-element convention that `el:GetAngle()` points in the decreasing-index direction, this is **the direction of travel in both directions**: decreasing traversal uses the element angle directly, while increasing traversal adds 180 degrees. The excerpts do not independently define which indexed direction `el:GetAngle()` denotes, so the strictly excerpt-proven result is the formula above. If the asset convention were instead that `GetAngle()` points in the increasing-index direction, the formula would face the train 180 degrees opposite its travel. The remaining answers call the formula above the “straight-track travel yaw”; under the intended/decreasing-index convention, it is aligned with travel.

After that explicit yaw set, the move uses `SetPos`, and `WaitChangeDir` is called with a nil yaw (`Train_excerpt.lua`, Units/Train.lua 583–587). A nil `final_yaw` is replaced with the current rounded yaw, so this pitch adjustment does not request another heading (`Train_excerpt.lua`, Units/Train.lua 470–476).

#### Q2 — `Station:TrainArrive`

**There is no deliberate yaw change.** The station identifies `Ramparrive<trackidx>` and `Stop<trackidx>` (`Station_excerpt.lua`, Buildings/Station.lua 1097–1103). It either teleports position to `Ramparrive` with `SetPos`, or slides there with `GotoSpot(..., final_pitch = 0, ...)`, and then slides to `Stop` with another `GotoSpot(..., final_pitch = 0)` (`Station_excerpt.lua`, Buildings/Station.lua 1105–1114). By the stated semantics, the direct `SetPos` changes no orientation.

Inside `GotoSpot`, the destination affects position, acceleration, and pitch; when a final pitch is supplied, it calls `WaitChangeDir(..., final_yaw = nil, ...)` (`Train_excerpt.lua`, Units/Train.lua 507–518). `WaitChangeDir` reads the current yaw, rounds it to a 3600-arc-minute increment, and substitutes that same value when `final_yaw` is nil; consequently `changed_yaw` is false (`Train_excerpt.lua`, Units/Train.lua 470–476). It only calculates/interpolates a different yaw when `changed_yaw` is true (`Train_excerpt.lua`, Units/Train.lua 482–495).

Therefore, during both the element-to-`Ramparrive` and `Ramparrive`-to-`Stop` motion, the train holds **the heading with which it arrived**. More precisely, if a pitch interpolation occurs, the implementation uses the arrival yaw rounded to a multiple of 3600 arc-minutes in its `SetRollPitchYaw` calls (`Train_excerpt.lua`, Units/Train.lua 471–476, 486–502); normally the preceding straight-track code has already rounded yaw that way (`Train_excerpt.lua`, Units/Train.lua 581–583).

#### Q3 — Departing on a different track

Because the departure connector `idx` differs from `train.station_arrival_track`, the same-track reversal block is skipped, including its only station-side `SetAngle` call (`Station_excerpt.lua`, Buildings/Station.lua 1184–1195).

The train then makes two moves: `Stop` to `Rampdepart<idx>`, followed by `Rampdepart<idx>` to the departure element's direction-selected `Enter` spot (`Station_excerpt.lua`, Buildings/Station.lua 1197–1205). The first call omits `final_pitch`, so `GotoSpot` only starts the positional interpolation and sleeps; it returns before `WaitChangeDir` (`Train_excerpt.lua`, Units/Train.lua 507–516). The second supplies `final_pitch = 0`, so it reaches `WaitChangeDir`, but passes a nil yaw (`Train_excerpt.lua`, Units/Train.lua 517–518); as above, nil means the current rounded yaw, not a heading calculated from the destination (`Train_excerpt.lua`, Units/Train.lua 470–476).

Therefore **nothing reorients the train toward the different departure track before it reaches that track element**. It holds its arrival heading through both slides (subject only to the same possible 3600-arc-minute rounding during the second slide). That heading has no fixed relationship to the different connector's outbound direction.

For a straight departure element, its yaw is next deliberately set when `WaitTraverseElement` begins the following element-to-element traversal: it sets the straight-track travel yaw before calling `SetPos`, namely rounded `el:GetAngle() + 10800` for `step == 1`, or rounded `el:GetAngle()` for `step == -1` (`Train_excerpt.lua`, Units/Train.lua 578–587). Under the track-angle convention stated in Q1, that is the new track's direction of travel.

Two branch qualifications are visible in the excerpt. If `teleport_to_next` is true, the straight branch first calls `SetAngle(starting_angle)`—where `starting_angle` may have been computed from the start element toward the station's `Trackdirection` spot—and then the valid-element block immediately applies the formula above (`Train_excerpt.lua`, Units/Train.lua 573–583; 654–662). If the current element is curved instead of straight, the other branch changes yaw over that traversal by plus or minus 60 degrees through `WaitChangeDir` (`Train_excerpt.lua`, Units/Train.lua 538–551).

#### Q4 — Departing on the same track

When `idx == train.station_arrival_track`, the very first special handling looks up `Spawn<idx>`. If that spot exists, it immediately puts the train at that spot's position and sets the train's angle to that spot's angle (`Station_excerpt.lua`, Buildings/Station.lua 1184–1194). Thus the first state is:

- **position:** `GetSpotPos(Spawn<idx>)`;
- **yaw:** `GetSpotAxisAngle(Spawn<idx>)`'s angle.

For the mod station, a synthetic `Spawn<idx>` computes its position using `connector_idx = opposite(idx)`, not `idx`; any `sevenths` scaling keeps the computed point on the centre-to-that-point line (`ModStation_excerpt.lua`, mod Lua 166–177). `GetSpotAxisAngle` returns `synthetic_spot_angle` for a synthetic spot (`ModStation_excerpt.lua`, mod Lua 265–269). Because `Spawn` is neither `Stop` nor `Ramparrive`, that angle is `CalcOrientation(center, spawn_pos)` (`ModStation_excerpt.lua`, mod Lua 180–187).

Given that `opposite(idx)` lies on the opposite side of the centre, the mod therefore initially places the train on the `opposite(idx)` side and gives it a yaw **from the centre toward `opposite(idx)`**. Relative to the direction from the centre toward connector `idx`, that yaw is **180 degrees opposite**. The subsequent two station slides are the same `GotoSpot` calls discussed in Q3 and contain no new directional yaw (`Station_excerpt.lua`, Buildings/Station.lua 1197–1205; `Train_excerpt.lua`, Units/Train.lua 507–518), so it retains that reversed heading until track traversal next resets/turns it, subject to the rounding qualification above.

#### Q5 — `Station:TrainTraverse` pass-through

For pass-through, the station selects the departure element and its direction-dependent `Enter` spot, then calls `train:GotoSpot(departure_el, enter_spot)` without a `final_pitch` or yaw argument (`Station_excerpt.lua`, Buildings/Station.lua 1085–1092). With `final_pitch` absent, `GotoSpot` performs the positional interpolation and returns before calling `WaitChangeDir` (`Train_excerpt.lua`, Units/Train.lua 507–518).

Consequently, the train holds **exactly the yaw with which it entered the station/pass-through operation** while it slides to the departure element. The pass-through code does not align it to the departure track; if arrival and departure headings differ, it keeps the stale arrival yaw until later track traversal changes it.

#### Assumptions and limits

- The excerpts completely settle nil-yaw handling: `WaitChangeDir` substitutes its rounded initial yaw (`Train_excerpt.lua`, Units/Train.lua 470–476). No external assumption is needed for that behavior.
- Translating the Q1 formula into “aligned” versus “opposite” physical travel requires the omitted definition of a track element's `GetAngle()` direction. I use the decreasing-index convention above; the exact formula is valid without it.
- I assume `SetAngle(angle)` sets the train's yaw to `angle`, and that opaque calls shown here (for example `StopInterpolation`, acceleration/speed helpers, and station bookkeeping) have no hidden yaw side effects. I also assume no concurrent or unexcerpted code reorients the train during these synchronous routines.
