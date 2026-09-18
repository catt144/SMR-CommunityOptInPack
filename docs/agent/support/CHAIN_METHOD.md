# Chain method — building a multi-session effort

For an effort over about two sessions. Each link is a brief written per the `prompt-authoring` skill;
this adds the chain structure.

## What a chain is

Many focused links, each sized to finish well inside one session, numbered in a folder that works as
a self-consuming queue. Each link ends by appending its handoff notes to the link that owns them,
committing, and deleting its own file in the same commit. An empty folder is the done-condition. The
last link is always an adversarial backward QA in fresh context that trusts nothing forward.

The two rules to keep if everything else is lost: **finishing is the only way a link can
disappear, and every discovery goes to a written owner, never a memory. End every chain with a
fresh-context adversary whose job is to disbelieve it.**

## Authoring

1. **Shape before link 1.** Converting mid-flight throws away a ledger built on the old shape.
   - **Sequential** when discovery compounds: a sweep, a hunt, anything where the next link needs to
     see what the last one found or where "go where the last one did not" is the stopping rule.
   - **Parallel** when verifying a fixed finding set, or when blinding matters: parallel agents cannot
     read findings that do not exist yet. Never run fixes in parallel on a shared core file.
   - **Hybrid** for a large effort: parallel find-only lenses → synthesis that hunts the cross-lens
     pattern ("what did every lens assume?") → a short sequential stage on the two or three questions
     nobody asked → an independent adversarial ruling on the verdict.
2. **Difficulty, not models.** The owner chooses every model; nothing in a chain names one. The
   authoring agent tags each link's filename with the reasoning it needs. The tag is a routing hint,
   not a gate: a link never checks or refuses the model it runs on.
   - `_low`: light-to-moderate reasoning on a settled plan: a pre-planned build, doc work, a records
     close-out, a scripted leg. Models at this tier reason but do not dig far, so a link that
     investigates is never `_low`. No link is sized for a no-reasoning model; none is used.
   - `_medium`: real judgement, but inside a settled design (a spec-guided build, a leg with
     predictions), or a bounded investigation. An investigation whose answer steers a design is
     `_high`.
   - `_high`: where errors compound or independence matters (the spec, a design adjudication, the
     highest-risk build, the terminal QA). If more than half the chain is `_high`, the decomposition
     is wrong: the specs are not carrying enough of the load.
   - **Fan-out.** A link suited to subagent control (a broad hunt, many parallel lenses, a batch of
     independent tasks) stays one link, not split, and its filename ends `_fanout_level_<x>` in place
     of the low/medium/high tag. The suffix goes on each fan-out link, never on the chain folder.
     The authoring agent sets `x`, 1–10, by how hard the orchestration is: how many subagents, how
     dependent their work is, and how much judgement the synthesis needs. Every agent can spawn
     subagents, but not every agent organises, tasks and manages them equally well; the level is
     what the owner routes on.
   - The link that runs a fan-out picks each subagent's model for its task: a light-to-moderate model
     for work on a settled plan (doc work, a pre-planned build, a scripted read), a deep-reasoning
     model for anything that investigates or needs judgement. An investigating subagent never gets
     the lighter model.
   - A fan-out brief is tool-neutral ("a judgement-capable subagent", no vendor tool names), and its
     coordination is git-visible: it commits its plan and each subagent's verbatim report as it goes,
     under `reports/<chain>/agents/`, marks unrun subagents NOT RUN, and a resumed run continues from
     what is committed. The terminal QA can only judge what was committed.
   - Link bodies stay vendor- and model-neutral.
   - Unattended work is at least a chain of two: one link executes, another audits it.
3. **The folder.** `docs/agent/prompts/<effort>/`, plus a row in the `prompts/README.md` "Chain
   folders" table (doccheck `PROMPT MAP` checks it). **Commit the folder before any link fires**:
   self-deletion and restores both assume git, and silently no-op on an untracked file.
4. **The README manifest.** A table of number · file · difficulty tag · attended? · what it drains.
   Each link's close-out strikes its OWN row in its deletion commit; a manifest no link owns goes
   stale.
5. **Chain rules in the README**, short: the inbox/outbox convention; route, never drop; self-split at
   a clean commit boundary into a continuation that is a full chain member, never pushing to the edge
   of a context window; every drift instance appended to the terminal QA's evidence list, however
   small (a silently corrected instance is destroyed evidence); defects filed through `smr-bug-library`;
   the commit convention; any sealed documents.
6. **Each link body** is a normal brief (authority, end state, live work list, staleness, facts,
   scope, stops, do-not-claim) plus a `## Notes from upstream` section later links append into, and
   the instruction to delete itself.
   - A link that investigates or builds gets the evidence, the question and the hard rules, then free
     rein. A link that runs a job (a sweep, a records close-out) gets rails.
   - "Do not re-derive the design" never means "do not verify the route": a builder re-checks that the
     route still exists, and tags spec details MEASURED / SOURCE / INFERRED.
   - A brief cites the entry it acts on, and the worker acts on the entry, not the brief.
   - A link that needs the owner's hands is marked attended up front; split attended and unattended
     halves when authoring.
7. **Ordering.** Strict only where work products interfere; otherwise declare links independent.
8. **The terminal link, always.** Adversarial backward QA in fresh context, tagged `_high`; the
   owner runs it on a different model or vendor from the one that ran the legs or wrote their
   briefs. It audits every handoff landed, sweeps owed work, checks consistency, samples verdicts
   against primary evidence, and holds the folder-empty gate. Budget it generously. Its value on a
   self-correcting run is certification plus residue, not rescue; an upstream link that grades its
   own strongest claim is the failure shape.

## Running

- **Owner decisions** are packaged with a recommendation and routed to `docs/PLAYTEST_CHECKLIST.md`
  in that file's item format. Provisional approval ("build it, not locked, the QA reviews") keeps work
  moving without turning a judgement call into a fait accompli. The owner may act on a routed ask at
  any time, or inject a decision mid-chain through a link's upstream notes; a link that depends on an
  ask still being open re-reads the world instead of trusting the handoff.
- **Situation-gated items** (a test that waits for a game state) go to the checklist's `## Run` as a
  `When …` item, not into a link.
- **Predictions before runs.** Every leg writes numbered predictions, and for a matrix cell the
  premises the prediction rests on, which the harness reads at run top beside the result.
- **Externally mutable state** (mod enabled, account settings, cloud sync) is gated at run top, and the
  gate stops the run. A leg that mutates such state hands the restore back to the owner explicitly.
- **Blocked on an owner-only unblock:** do not park. Prove the instrument with a declared-VOID
  rehearsal (mode armed by script and read back from disk, bannered in the log, verdict lines stamped
  VOID) so the real run is single-shot.
- **Evidence.** Any log a status flip or verdict cites is archived in the citing commit, whoever
  produced it; game logs rotate at about 20 files. A voided log is kept beside the good one.
- **Attended sittings** follow `docs/agent/support/CO_RUNS.md`: a priority queue, not a schedule;
  fixtures re-confirmed at sitting time; owner verbatims relayed into the log as they are spoken.
- **Consumed files name their git grave** (`git show <sha>:<path>`) where their content is folded into
  standing docs. Restore a damaged file from that grave or a copy, never with `git checkout --`.
- **Chain to chain.** The owner starts every chain by hand. The terminal QA's report ends with the
  kickoff line for the next queued chain, or says none is queued. When an unattended item turns out to
  need the owner, the discovering link offers an attended co-run inserted before the terminal QA;
  declined, the item goes to the checklist.

## Common shapes

- **Large project:** measurements first → a spec that closes its decisions → builds split by unit →
  attended legs with predictions → records close-out → terminal QA.
- **Audit:** sweep links over the target (about ten items each, graded verdicts) → a decision package
  per contested item, routed to the owner → a sealed blind control in parallel → fix batch →
  verification legs → terminal QA that weighs the blind control against the informed record.

## Blind controls (optional, proven)

A fresh session derives the effort's conclusions with the record off-limits, sealed from every link but
the terminal QA, which examines it against the informed record. Seal at the source, not the reader:
move sealed material out of anything a link reads by default into a sealed side-file, prescribe a
subject-hiding staleness check (`git log --format=%h -10`), and require each link to attest what it saw.
A broken seal mapped honestly still keeps most of the control's value.

## Kill-gated build chain (proven 2026-08-04)

For building on unproven capability. An inventory link bins every primitive PROVEN / VERIFIED-IN-SRC /
UNKNOWN, and nothing is planned on an unbinned one. A walking-skeleton link runs the smallest end-to-end
proof with predictions and abort thresholds written first, and may kill the chain; the terminal link
carries a pre-written reduced form (post-mortem, route the respec-or-abandon decision, empty the folder)
so a kill has somewhere to land. A payload link builds only on what the skeleton proved. PASS WITH
CORRECTIONS is a verdict class, and a declined mid-chain grant is best handed back as a measurement.
