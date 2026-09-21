# Train hub: the last transition — the slide onto the loading siding

**LIVE, fire when ready.** Owns `tools/devmods/train_hub/Code/20_TrainHub.lua`. Authoring sha:
SMR-OptInPack `d363aa8`. An empty `git diff --stat d363aa8..HEAD -- tools/devmods/train_hub/` means
this brief's code facts hold; if it is not empty, read the diff before trusting the line numbers.

⚠️ **This brief replaces a long-running one that the owner stopped** (2026-09-21). Everything else in
the movement work is DONE and accepted by the owner in game — the transition in, the transition out,
the exit slide and vanilla handoff, the six-siding rejoin, the 6 s dwell and the cold-start power
fix. **One transition is left, and it is the whole job.** The dev mod's uncommitted model re-import
is the owner's and not yours.

## Authority

**Owner, 2026-09-21, the fault, in their words.** *"I keep telling astra the train needs to go
further along the track before it does the slide over, it instead keeps changing the speed of the
slide over without moving it further up. So now jerking over after multiple attempts at fixing it
and still hasn't moved past at all."* The owner attributes this to a previous agent's exhausted
context, not to a hard problem. **Read the code before you believe any account of it, including
this one.**

**Owner, same day — what they want, in order.**
1. **Undo the slide's speed damage first: the lateral move onto the siding must read at the same
   rate as the outer slide**, the one a train already does coming in off the vanilla track, which
   the owner accepted. That is the reference feel. Match it.
2. **Then move the onset further along the train's travel** — it runs straight further before any
   lateral motion begins.

## What the code does now, and why the owner kept getting a speed change

Three functions, all in `20_TrainHub.lua`:
- **`HubSlideTrain` (`:528`) is the accepted outer slide** and your reference: eight steps of 150 ms
  on a smoothstep curve with `SetAcceleration(0)`, a purely lateral move at a fixed rate. It does
  not consult distance, speed or run length.
- **`HubSidingCurve` (`:565`) is the siding transition**: the same eight-step smoothstep, but
  longitudinal, driven through `HubMoveTrain` with a computed speed per step.
- ⛔ **`HubMoveOntoSiding` (`:588`) holds the defect.** It scales the approach speed by the run
  length: `speed = GetNominalMoveSpeed() / 3 * Min(run, 12 m) / 12 m`, where
  `run = HubSidingEntryDistance - HubParkDistance`. With today's 19 m and 11 m the run is 8 m, so
  the train approaches at a **third of the intended speed**. Its comment says this preserves the
  lateral easing time when the onset moves inward. That is the mechanism the owner has been fighting:
  **every time they asked for the onset to move, the code answered by changing the speed instead**,
  and the compounding left the jerk they see now.

**The geometry, so you do not invert it.** `HubCentrePosition(idx, distance)` (`:553`) measures
**from the hub centre outward**. A train arrives from outside and travels inward, so a **smaller**
`HubSidingEntryDistance` means the lateral motion starts **later** in the train's travel, which is
what the owner is asking for. Today: pause 48 m, entry 19 m, park 11 m, lateral offset 4.5 m.

## End state

1. **The lateral rate is the outer slide's, and it no longer depends on where the onset sits.**
   Delete the run-length speed scaling. A change to the onset must move the position and nothing
   else — that is the property the owner has been asking for and has not got.
2. **The onset moves further along the travel**, as one named tunable the owner moves live. Give
   them a starting value you believe, not today's.
3. **No jerk at the join.** ⚠️ An earlier owner ruling (2026-09-20) said to fold the slide into the
   braking, never stop-then-slide-then-stop. The owner's 2026-09-21 instruction above is later and
   governs where they conflict: **the rate must match the outer slide.** Your call how — keep it
   rolling if that can match the rate, or use the outer slide's own profile if it cannot. Say which
   you chose and why in the commit message.
4. **Nothing else changes.** The other transitions are accepted. Do not retune the pause, the exit
   slide, the rejoin, the dwell or the park distance because the code reads better that way.
5. **Smoke it with the owner**, about five steps: a train arrives, runs straight past the old onset,
   slides on at the outer slide's rate, parks, loads, and leaves. Autosave disarms a crossing watch —
   the owner re-presses the slot. The owner tunes the onset live; bring it ready to change.
6. **Record** in the hub report and spec §10, and commit with pathspecs. `doc-editing` first.

**Done means:** the owner watches the slide onto the siding and says it looks like the outer one,
and moving the onset moves where it happens without changing how fast it happens.

## Scope

In: `20_TrainHub.lua`'s siding entry path, its tunables, the sitting, the records.
Out: every other transition; the model and any re-import; textures; builds 4 and 5; the oracle.

## Stops

- **The rate cannot match the outer slide while the train is still moving forward**, and matching it
  needs the train to stop: report that with what each looked like, and let the owner choose. It is
  a one-line difference to them and a design question to you.
- **Removing the speed scaling breaks vanilla's reservation or occupancy contract** (hub report
  §"Build 3b", "Reservation contract"): report the break, do not repair it by restoring the scaling.

## Do not claim

Not that the transition "works" from a desktop harness or a log: it is a look, and only the owner's
eye closes it. Not that the jerk is gone because the code is simpler — claim what the smoke showed,
from the owner's view, at normal, fast and fastest speed.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` when the owner's smoke is
recorded.
