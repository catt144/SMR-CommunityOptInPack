# Geometry oracle paths run, 2026-09-20: blind Codex derivation (lane)

Model gpt-5.6-sol, OpenAI Codex v0.149.1, `codex exec --skip-git-repo-check --sandbox workspace-write`, reasoning effort high. The model was given the prompt below and verbatim excerpts of the named files from `C:\Dev\SMR-SrcArchive\1.1.0.403908\Src\Lua` (and, for the yaw run, `corpus/lua_current_6123ae7.lua` lines 166-187, 247-253, 265-269), with no hint of the answer. Judged in `docs/agent/reports/GEOMETRY_ORACLE_20260919.md` §11.

## Prompt

```
You are analysing Lua source excerpts from a game (Surviving Mars: Relaunched, train DLC). The files in this directory are verbatim excerpts: Train_excerpt.lua, Station_excerpt.lua, TrackElement_excerpt.lua, Tracks_excerpt.lua, TrainTransport_excerpt.lua. Read all of them. Do not search the internet. Work only from these files and the facts below.

Facts you may take as given:
- Angles are in arc-minutes (10800 = 180 degrees), counter-clockwise, in a right-handed x/y plane. CalcOrientation(a, b) is the heading of the vector from a to b.
- A straight track element (a TrackGridElement) has two named spots in its own frame: "Enter1" at 289 units to the LEFT of the element's angle (at +90 degrees from it) and "Enter2" at 289 units to the RIGHT of it (at -90 degrees), both at the element's hex centre along its axis. Exit1/Exit2 are analogous and only used on curved elements.
- A station owns one "connector element" per track connection; it is the element at the station's end of that track (the first or the last entry of track.elements). track.start_el is track.elements[1] after ProcessTrackElements.
- Consider only straight track near the station.

Questions. Answer each from the code, citing file and line numbers from the excerpt headers for every step of your reasoning.
Q1. For a straight, fully connected track, which way does a connector element's angle point relative to the track's element order (toward elements[1], or toward elements[#elements])? Consider both the case where the station's connector element is elements[1] and the case where it is the last element.
Q2. A train ARRIVES at a station along a track and reaches the station's connector element. Which named spot (Enter1 or Enter2) of that element does it arrive on, as a function of whether the station is the track's start station or its end station? Then say on which side of the train's own direction of travel (left or right, looking the way it is moving) that spot lies, in each of the two cases.
Q3. A train DEPARTS a station onto a track (Station:TrainDepart). Same two sub-questions: which named spot, per case, and which side of its direction of travel (it is moving away from the station).
Q4. A train passes through a station without stopping (Station:TrainTraverse). Which spot of the departure connector element does it go to, and on which side of its outgoing direction of travel is it?
Q5. Is the side (left/right of travel) you found in Q2-Q4 the same in every case, or does it depend on which end of the track the station is at? State any assumption your answer needs that the excerpts do not settle.

Write your full answer to a file named answer.md in this directory, and also print it.
```

## Answer (verbatim)

### Train connector orientation and lane-side analysis

#### Q1. Direction of a straight connector element's angle

`ProcessTrackElements` calls the ordering routine and then defines `track.start_el` as `elements[1]` and `track.end_el` as `elements[#elements]` (`Tracks_excerpt.lua`, lines 818–822). In that ordering routine, the initial endpoint is put at index 1 and its connections are cleared (`Tracks_excerpt.lua`, lines 571–579). As the path is extended, the old last element gets a connection to the new element, while the new element's first connection points back to the old last element (`Tracks_excerpt.lua`, lines 598–604). The possible whole-list reversal, together with reversal of two-entry connection lists, is handled at lines 626–635.

For a straight element, `GetTrackAngle` uses `connections[1]` and computes `direction = CalcOrientation(c1, self)` (`TrackElement_excerpt.lua`, lines 80–85 and 117). It returns that direction unchanged only for the element at `track.elements[1]`; every other straight element gets an additional 10800 (180 degrees) (`TrackElement_excerpt.lua`, lines 118–121). Connector orientation uses `GetTrackAngle` once the connector has more than one connection and assigns the result as the element angle (`TrainTransport_excerpt.lua`, lines 103–112).

Therefore the angle of every straight connector points in the **decreasing-index direction, toward `elements[1]`**:

- If the station connector is `elements[1]`, its first track connection is toward `elements[2]`. `CalcOrientation(c1, self)` is consequently the direction from `elements[2]` back toward `elements[1]`, and the special case returns it without adding 180 degrees (`TrackElement_excerpt.lua`, lines 117–119).
- If the station connector is `elements[#elements]`, its first track connection is back toward `elements[#elements-1]`. The initially calculated direction is from that previous element toward the last element; because this is not `elements[1]`, adding 180 degrees reverses it, so the final angle points back toward `elements[1]` (`TrackElement_excerpt.lua`, lines 117–121).

Thus the answer is the same at both ends: the connector angle points toward the `elements[1]` end of the ordered track. At the first connector that means toward/out through the first end; at the last connector it means inward along the track toward the preceding elements.

#### Q2. Arrival at a station

`Train:Traverse` sets `step = 1` when the train departed the track's start station and `step = -1` otherwise; it starts at index 1 for `step = 1` and at the last index for `step = -1` (`Train_excerpt.lua`, lines 649–652). It selects `Enter1` for `step = 1` and `Enter2` for `step = -1` (`Train_excerpt.lua`, lines 665–666). On a straight element, traversal moves to that named spot on `next_el`, and the loop advances by `step` until the far endpoint is reached (`Train_excerpt.lua`, lines 522–523, 554–555, 590, and 668–673).

Hence:

- Arrival at the **end station**: the train came from the start station with `step = 1`, so it reaches the end connector on **`Enter1`**.
- Arrival at the **start station**: the train came from the end station with `step = -1`, so it reaches the start connector on **`Enter2`**.

By Q1, the connector angle points toward decreasing indices. On arrival at the end, travel toward increasing indices is opposite the element angle; `Enter1`, which is left of the element angle, is therefore **right of the train's direction of travel**. On arrival at the start, travel toward decreasing indices agrees with the element angle; `Enter2` is directly **right of the train's direction of travel**. The yaw calculation independently reflects these two travel directions: traversal adds 180 degrees for `step = 1` and adds nothing for `step = -1` (`Train_excerpt.lua`, lines 578–583).

#### Q3. Departure from a station (`Station:TrainDepart`)

`Station:TrainDepart` computes `step = 1` when this station is the departure track's start station and `step = -1` otherwise, then selects `Enter1` for `step = 1` and `Enter2` for `step = -1` (`Station_excerpt.lua`, lines 1197–1201). It moves the train first to the station's `Rampdepart` spot and then to that spot on the connector element (`Station_excerpt.lua`, lines 1202–1205).

Therefore:

- Departure from the **start station**: **`Enter1`**. Outgoing travel is toward increasing indices, opposite the connector angle, so the spot that is left of the angle is **right of travel**.
- Departure from the **end station**: **`Enter2`**. Outgoing travel is toward decreasing indices, in the connector-angle direction, so this spot is **right of travel**.

The special same-track reversal only resets the train to the station's `Spawn` position and angle before this common connector-selection logic; it does not change the `step`/`Enter` choice (`Station_excerpt.lua`, lines 1185–1196).

#### Q4. Passing through a station (`Station:TrainTraverse`)

For the departure track, `Station:TrainTraverse` uses exactly the same rule: `step = 1` when the station is the departure track's start station and `step = -1` otherwise, and it goes to `Enter1` or `Enter2`, respectively (`Station_excerpt.lua`, lines 1085–1091).

Thus the departure connector target is:

- **`Enter1`** if the traversed station is the departure track's start station; it is **right of the outgoing direction of travel**.
- **`Enter2`** if the traversed station is the departure track's end station; it is also **right of the outgoing direction of travel**.

#### Q5. Is the side consistent?

Yes. In every case in Q2–Q4, the selected connector spot is on the **right-hand side of the train's direction of travel**. The named spot changes with the station's end of the ordered track—`Enter1` for motion toward increasing indices and `Enter2` for motion toward decreasing indices—but the physical side of travel does not.

This left/right conclusion assumes that, at the connector, “direction of travel” is the tangent direction of the straight track: increasing element order for `step = 1`, decreasing order for `step = -1`. That is the direction used by track traversal and its yaw logic (`Train_excerpt.lua`, lines 649–666 and 578–583), but the excerpts do not provide the station models' `Rampdepart`, `Ramparrive`, `Spawn`, and `Trackdirection` spot coordinates. Consequently, the code proves the named connector spots unconditionally; describing them as right of the *instantaneous station-to-connector interpolation segment* additionally assumes that the station ramp joins the straight track tangentially. It also assumes connector orientation is performed after track processing has normalized the ordered track connections, as implied by `ProcessTrackElements` establishing the endpoints (`Tracks_excerpt.lua`, lines 818–822) and `OrientConnectorElements` then deriving and setting the connector angle (`TrainTransport_excerpt.lua`, lines 103–112).
