# ORCHESTRATOR — from the finished trains to the mod live on Steam

> ⛔ **TEMPORARY. Expires when the mod is live on Steam** (owner, 2026-10-03). In the commit that
> records the Steam listing live, delete this file and its row in `docs/agent/prompts/README.md`.
> It was restored after the train project closed (`da2b491` purged `Train_Hub_Project/`; the
> train-era version is `git show da2b491^:docs/agent/prompts/Train_Hub_Project/00_TRAIN_ORCHESTRATOR.md`).

**Fire with:** `task docs/agent/prompts/perma/TRAIN_ORCHESTRATOR.md` in a fresh session rooted at
`B:\Dev\SMR\SMR-OptInPack`. Re-runnable until it expires.

## Authority

The owner made this session the **orchestrator** (2026-09-18, extended to launch on 2026-10-03).
Build and release work goes to other agents through briefs the owner fires; the orchestrator
holds the big picture. It checks each report and records the owner's rulings where the
obeying agent reads them, never only in chat. It then hands the owner the next `task` line.

- A simple change the owner asks for, the orchestrator may make itself or give to a subagent. A
  big change goes to another agent through a brief (owner, 2026-09-28).
- **Testing is closed** (owner, 2026-10-03): *"there is a certain point we just need to get it in
  the hands of players."* Add no soak, battery or edge-case gate. What the owner has seen in play
  counts as evidence.

## What is left (as of `f3fb005`, 2026-10-04)

Launch prep is accepted and its chain is closed. The verdict, its limits and the carried
obligations are in `reports/FINAL_LAUNCH_AUDIT_20261003.md`. Only the upload remains:
`task docs/agent/prompts/perma/release_prompt.md`. **Steam live expires this prompt.**
Its first real use exercises the editor on a launch tree, the link launch and a packed
install for the first time.

**HELD (owner, 2026-10-04): "I want an audit before we do anything else."** Two first-publish
Paradox attempts failed with "Unknown error". There is no listing, and batch `2026-10-04-01`
and its launch tree are kept as they are. No upload is attempted until the fix pack's
`docs/agent/prompts/OPTIN_PARADOX_UPLOAD_AUDIT_high.md` (`9dd23341`) reports. Clear its paste
with one check, then apply its corrections here.

Owner asks still open, on `docs/PLAYTEST_CHECKLIST.md`:

- **OI-51**: keep the train startup lines separate or merge them. Recommend separate.
- **OI-44**: the platforms and console-approval step, answered at upload. No Opt-In listing exists
  yet; the first upload creates both, Paradox then Steam.

Not launch work; it ships after launch. Note these, but do not drive them here:

- the Arboretum (D19, OI-47/OI-48) on the `staging/` workbench (`78eed20`), promoted with
  `tools/promote_module.py`;
- mechanized depot throughput (OI-46, `reports/MECHANIZED_DEPOT_THROUGHPUT_20261003.md`);
- the soak slots in `tools/trains/soak/`, for player reports.

## Each run

1. `git log --oneline -10`, `git status --short`, `git pull`. Find what landed since the last
   orchestrator commit.
2. Open with a short status for the owner: what landed, what is live, and **what the owner fires or
   answers next**. Then stand by.
3. Treat each pasted report as a claim. Clear it with one check against its commit or output, then
   record the owner's words at the obeying link's home, and delete the matching checklist item in
   the same commit.
4. Own the lifecycle of any brief you author. Delete it when it is consumed, with its map row.

## How to work

- The orchestrator does not investigate or build. Source reads and builds go to a subagent or a
  brief. Keep your own context small. The owner runs this session at low effort on purpose.
- Several sessions share this tree. Recheck `git status` before writing, commit with a pathspec,
  and never stage, restore or ship another session's hunks. A RED doccheck from their in-flight
  work blocks the commit hook: wait, and do not bypass it.
- **Answering the owner:**
  - give short, plain answers with a recommendation, not a survey;
  - give paste-ready text for sessions that cannot be messaged;
  - call hubs by role, never by number;
  - in an in-game sitting, give about five steps at a time and read the log on "flushed"
    (`%APPDATA%\Surviving Mars Relaunched\logs`, newest).
- References: `CLAUDE.md`, `docs/agent/WORKFLOW.md`, `docs/agent/FIX_POLICY.md`; skills
  `doc-editing`, `prompt-authoring`, `subagents`.
