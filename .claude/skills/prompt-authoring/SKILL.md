---
name: prompt-authoring
description: Write or revise an Opt-In Modules prompt or job brief for another session — short and decisive, with a live work list, scope, stops and a declared lifecycle.
---

# Author a prompt or job brief

Write for a capable worker that knows this repo. State the decision and the end state, hand over
judgement, and cut every line a named skill or the worker's own judgement already covers.

## Match the rails to the job

- **Investigation or module build** (find a cause, design or build a module change): give the evidence
  so far, the question or the done-condition, and the hard rules (`FIX_POLICY.md`, the reach rule,
  and any special rule the owner or an owner-and-agent design set). Then free rein: no read path,
  no step order, no prescribed hypothesis, no fence on what to open, run or explore. A lead is
  offered as a lead, never as the route.
- **Job** (perma prompts such as release, STATE eviction, a sweep, a prune): rails. Fixed order,
  named files, scope, checks, and a clear focus.
- Unsure which: it is an investigation if the answer is not known when the brief is written.
- **An effort over about two sessions** is a chain of briefs: read `docs/agent/support/CHAIN_METHOD.md`
  before splitting it.

## Every brief

- **Authority first.** Open with what the owner decided, as settled. The brief never re-argues it.
  For a module, that includes whether MODULE FREEZE is lifted for it.
- **End state.** For a job, numbered steps in order; if time or budget can run out, say what is
  dropped first.
- **Judgement handed over.** "Your call: A or B", not a branch per case. The worker does not ask the
  owner what it can decide; it records the call in the commit message.
- **Live work list** in the todo tool before any write: one item per commit-and-verify unit, one in
  progress, marked as each lands. A list written afterwards does not count.
- **Start and staleness.** `git log`, `git pull`, the authoring sha; an empty
  `git diff --stat <sha>..HEAD -- <paths>` means the brief's facts hold.
- **Facts only where the worker would re-derive them**, each with how it was measured and one
  command that could falsify it. For more records point at the bugs/facts `INDEX.md`.
- **Scope** in two lines, in and out; for an investigation, scope is the question, not the files.
  An out-of-scope finding goes in the report, not an edit.
- **Stops**, at most three, as permission to report instead of pushing on.
- **Do not claim:** the claim the evidence cannot carry, and the narrower true one to write instead.
- **Lifecycle:** a one-off is deleted when fired; a perma prompt stays.
- **Difficulty tag** in the filename: `_low` (light-to-moderate reasoning on a settled plan; never an
  investigation), `_medium`, `_high`, or `_fanout_level_<x>` (1–10) for subagent control. It is the
  owner's routing hint, not a gate: a brief never names a model or checks which one runs it.
- **Name skills, do not restate them:** `doc-editing`, `smr-bug-library`; house rules are `CLAUDE.md`.

## Shapes that fail

- **A shrink job that keeps by default.** Make deletion the default; survivors earn a home or a slot
  under a cap, with concrete examples of gaming the cap.
- **"Archive everything"** as the answer to hard triage. Say that content already recorded elsewhere
  is deleted, not re-archived.
- **"Already homed" proven by a heading match.** Require the body.
- **Subagent output used unchecked.** It is a claim until one command confirms what a cut or verdict
  rests on.
- **A worker grading its own rewrite of a rule document.** Require an inventory of requirements
  first, and a blind check that sees only the new text and the inventory.
- **A build brief for a state players cannot reach.** A defect that lives only in a save Steam and
  console cannot load stops before the brief and goes to the owner.

## Test and playtest briefs

- Include the probe sweep before testing (WORKFLOW, Probe hygiene). Its age is a trigger satisfied
  at the next playtest (ck184), never a reason to refuse work.
- **Every module owes a BOTH-CONFIGURATION test at ship** — with the fix pack installed and with it
  absent (`FIX_POLICY` §8), naming the version. A brief that tests one configuration is incomplete.
- For a content module, what the disable direction must do is set by `FIX_POLICY` §0 (it stops
  offering new instances; placed content may stay).
- A module's test must cover **both toggle directions**, including a mid-session enable and a
  mid-session disable, because that is the only surface a player has.
- Before asking the owner to build a fixture, have the worker look for an existing save that has it.
- A warmed-up save is the default; state only a deviation, such as reading immediately after load.
- Behaviour, timing, throughput and player-notice claims state the fixture's scarcity, fleet,
  density and layout, and report that colony, not a generalisation.
- Name every setup mutation; reject one that intersects the mechanism measured. A no-taint claim
  needs a clean current-build save; toolkit `CLEAN` is not an achievement verdict.
- A shortened `MapGameTimeRepeat` is restarted after the change and after every reload and proven
  live; a negative result is paired with a positive control.
- Salvage targets objects, not hexes; a bare red `Salvage` means nothing under the cursor is
  targetable.
- Label probe tallies with their build and name each SKIP. A MarsDebug pass is not retail evidence
  (EF-044). The TestKit is **shared with the fix pack** — a probe count is the whole suite's
  unless the brief says which share it means.
- Owner-typed console lines are one paste-safe line with no `--` comment: a bare expression for a
  read, `*r` for real-time or multi-statement work, `*g` for game-time work that yields. Make `nil`
  explicit, read presence from the file log, claim absence only after exit.
- Check console and toolkit names against the retail sandbox (EF-096). `ConsolePrint` silently
  rejects multiple or non-string arguments; an OS display measurement needs a DPI-aware tool.
- Grep logs with the FULL token `[CommunityOptInPack]`; the fix pack's tag is a different string
  and BOTH MODS LOADED is the rig's normal condition.
- A fix invalidates its own tests: rebase harm legs on the pre-fix body and rerun the whole suite.

Before handing off, read the brief as its worker: are the decision, end state, scope, stops and
done-condition findable without this conversation?
