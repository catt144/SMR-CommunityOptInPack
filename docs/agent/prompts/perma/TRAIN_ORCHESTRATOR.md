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

## What is left (as of `239ff10`, 2026-10-03)

Launch chain, fired in order. Its map and rulings are in `Launch_Prep/README.md`, plus each link's
`## Notes from upstream`:

1. `task docs/agent/prompts/Launch_Prep/03_STORE_AND_SITE_medium.md`, resumed. Store copy, the shared
   site and the public README, credits (OI-49: the owner's own paid-plan model), and both residue
   disclosure sentences next to OI-45's uninstall note.
2. `task docs/agent/prompts/Launch_Prep/04_FINAL_AUDIT_high.md`, on a **different model** from the ones
   that ran 03A and 03. If it fails, its corrections handoff is the next fire, as 03A was.
3. `task docs/agent/prompts/perma/release_prompt.md`, the upload. **Steam live expires this prompt.**

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
