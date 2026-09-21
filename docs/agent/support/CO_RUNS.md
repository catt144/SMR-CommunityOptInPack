# Co-runs — attended experiment legs with the labor inverted

Binding when a co-run applies. The sign-off tiers that bind every leg are in `WORKFLOW.md`.

## Objective

A co-run splits an attended leg along the
actual skill line: the agent performs preparation, launch driving, save staging,
scenario scripting, amplification and log reads; the owner attends only the
named moments that genuinely need eyes, hands or judgment.

The owner's time is the objective to minimise; evidence quality is the binding
constraint. Do not replace an organic observation with a forced path, an
attended verdict with an unwitnessed one, or a competent disagreement with an
agent-only assertion. Conversely, do not spend an hour of engineering to avoid
seconds of owner input. State each ask, why it is needed and its expected cost in
the measure-moments list, and batch it with moments the owner already attends.
Report attended cost against the promise, never “minutes saved” as an
achievement.

## When to use a co-run

Route an item here when setup is heavy but the human measure is short; when an
intermittent trigger can be amplified while the measured path remains organic;
or when a scripted leg and a brief visual or judgment call share one boot. A
need for the owner is a routing precondition, not a reason to descope the item.

Use the cheapest mode that preserves the requested evidence:

1. **Unattended:** every result is log-readable on a staged copy. Its ceiling is
   mechanism/probe evidence, never `tested` or organic-witnessed. Author and
   close unattended chains through `docs/agent/support/CHAIN_METHOD.md`.
2. **Co-run:** setup and objective reads are scriptable, but named moments need
   human eyes, hands or judgment. Batch every ready rider and free console read.
3. **Attended playtest:** the evidence is continuous human play, feel, severity
   or a `tested` grant.
4. **Organic-only:** reachability, organic upgrades and naturally arising
   symptoms go to the checklist's `## Run` as `When …` items; never rig them into
   a different claim. Those items are purged at 30 days old, so an organic test
   that did not arise in time is gone, not waiting.

Forcing an upstream condition is allowed when the path under test remains
organic. Every result names what was forced. Forcing the measured path proves
the forcing, not the game.

## Preparation and sitting protocol

- Maintain a live todo/ledger: one item per commit-and-verify unit, exactly one
  in progress, plus every owner check handed out, returned or still outstanding.
- Finish all preparation before the owner sits down. The brief carries the
  scripts as text and a measure-moments list giving each owner action, its
  instrument and exact verdict words. Temporary probes enter `Code/` only for
  the sitting and leave in the result commit.
- Use a designated copy of a provisioned save, never the campaign file; reach
  saves through the fix pack repo's `saves/game`, `saves/backup` and `saves/reporters`. Loading
  a copy still runs that campaign's autosave: before any such load, byte-copy
  every autosave and inventory it by name (`EF-056`). Name the exact load route
  for each staged copy; duplicate display names are not a route.
- Run the probe-hygiene preflight required by `WORKFLOW.md` before any test that
  uses probes. Record the command, output, exit status, hit names, pack/TestKit
  HEADs and check time. A stale sweep is handled under the current ck184 rule;
  it never authorises an agent to block unrelated work or override the owner.
- Batch aggressively: launch and warm-up are fixed costs. Unattended reads that
  fit the same boot ride free, but no rider may delay or weaken a measure moment.
- Budget console driving when it is needed. Every owner-typed console line is
  preflighted for thread context as well as symbol resolution; the
  `prompt-authoring` skill's playtest instructions own the paste-safe `*r`/`*g`
  forms. Never assume a bare console supplies a yielding thread.
- Give every subject a locating instrument and confirm it still exists at
  sitting time. A completion counter names its liveness witness. Mid-chain
  readers and helpers obey the same witness and type checks as the main leg.
- Resolve every harness helper used against the helpers defined before launch,
  and live-read every engine class, label, key or field consumed by a reader.
  Parse success proves syntax, not resolution. Capture and print both returns of
  every `pcall`; do not let a swallowed raise look like `nil`.
- A fact that spans launches cannot live only in a process flag. Gate on the
  live check or a durable archived result.
- If a measure crosses a save, take its before-reading immediately before that
  save in the same call. If a popup is answered, record its named target before
  answering. A state-transition or effect verdict needs round-trip persistence
  and an effect read, not merely a successful call.
- Prove save liveness with on-disk size/mtime and load-back, not only
  `Savegame.ListForTag`. Read mid-session logs for presence only; absence claims
  wait for the archived post-exit log (`EF-047`).
- Any process-state mutation states its restart requirement. A conditions gate
  runs at the top of every affected process and stops the run on mismatch; a
  printed warning followed by measurements is not a gate. A request for a dark
  module names the mechanism that actually makes that module dark.
- Mark source line numbers as source-verified or trust-carried. Static sweeps
  generate candidates only; a defect claim requires per-candidate source read.

Arming and disarming use a script file, never an inline PowerShell edit. On
PowerShell 5.1 the parked script needs a BOM. Do not pipe its output through an
early-terminating filter. Immediately before launch, the ARM gate reads the
metadata entry and probe files back from disk and refuses an unarmed launch.

## Owner-led deviations

An owner override is a course change, not a variance to manage (owner,
2026-08-05): *"My time is valuable and is a major concern. But if I decide to
over ride and follow a lead, a session shouldn't remind me nearly every message
that we should get back on track. Which makes trouble shooting hard when I am
trying to keep track of what I have sent to it to check and what I have not."*

Never end a reply with elapsed time, the quoted estimate or a nudge back to the
list: it makes it hard for the owner to track what they have sent to check. State the
plan's position once when the deviation starts, then stop until the lead closes,
the owner asks, or the sitting ends.
Keep the ledger of what the owner has checked and what remains. The lead is
first-class work: instrument and witness it.

Do not issue a stop order while a time-sensitive gate remains open; take the
reading first or establish the gate's timeout. Mark UI-dependent instructions
as eyes-verified or source-derived. Relay every owner verdict through the
harness note primitive when spoken so the archived evidence retains it.

## Close-out

1. Disarm and remove every temporary probe and metadata entry; run the scoped
   stale-probe sweep and the required parse/doc gates.
2. Check `git status` in both the opt-in pack and TestKit repositories. A stranded
   edit is a finding to route, never permission to commit or discard it.
3. Delete staged saves and reconcile the save directory by **name**, never by a
   count. Reconcile every autosave against the pre-copies. Current cloud history
   and the reopen condition live in `EF-051`; any unexpected return reopens it.
4. Archive the complete post-exit log and use it for negative findings. Attribute
   every unexplained line; “not caused by this leg” is not a dismissal.
5. Keep predictions separate from results, list SKIPs by name, and promote no
   status without the evidence tier and attendance the entry requires.

## Capability boundary

The rig has proven agent-driven Steam launch, filename-based staged loads from a
real-time thread, speed set/read-back, scripted state reads, amplification loops,
multi-launch sittings, log flush/read, and a save/list/load-back round trip.

**Launch mechanics** (measured 2026-08-04 over four launches): with the game
closed, stage the designated save copy in the signed-in account's numeric save
folder and load it by filename, not its duplicated display name. Arm the
committed probe file and metadata entry at the sitting, verify both from disk,
then launch with `& "c:\program files (x86)\steam\steam.exe" -applaunch 3215050`
and no `-smrautorun`. From a real-time thread with its own watchdog, poll for the
pre-game menu, call `LoadGame("<COPY>.savegame.sav", {})`, set and read back game
speed because the save arrives paused, then allow the measured 15-second settle
before game-time work. Time the load from the engine's own log and the cycle from
shutdown; `RealTime()` deltas do not survive a loading screen (`EF-045`). Disarm
and remove the staged copy during the normal close-out.

Anything older than this summary is recovered from the founding spec, which was
consumed at chain close and survives only in the fix pack's git:
`git -C B:/Dev/SMR/SMR-BugFixPack show 93088ba:docs/agent/prompts/corun-rig/CORUN_RIG_SPEC.md`. Do not infer a
mechanism from this summary.

Still unproven: the watchdog firing under a real wedge. Deliberately outside the
envelope: Mod-Manager/main-menu automation, unattended MarsDebug (modal asserts
make it attended), and OS-level input injection. Organic reachability, feel and
the owner's campaign remain outside scripted evidence by definition.
