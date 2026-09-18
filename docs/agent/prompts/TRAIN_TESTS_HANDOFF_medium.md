# Train logistics — run the no-code tests, then decide the prototype

## Authority

- `docs/PLAYTEST_CHECKLIST.md` **OI-10 is OPEN.** MODULE FREEZE holds: this job writes no
  module code and builds no prototype.
- Owner direction, 2026-09-18: run the spec's §7 tests **before** any prototype build. The
  owner runs the in-game checks; you prepare, interpret and record.
- The spec is `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`. §7 holds the procedures
  (T1–T4), §10 the prototype shape, and §9 the asset-pipeline read. It is desk-read only.

## Start

`git log --oneline -3`, `git pull`. This brief and the spec's §7/§9/§10 landed in the commit
after `c7b7a00`, and `git log -1 --format=%h -- docs/agent/prompts/TRAIN_TESTS_HANDOFF_medium.md`
names it. If `git diff --stat <that sha>..HEAD -- docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md docs/PLAYTEST_CHECKLIST.md`
is empty, the spec's facts hold as written. Put the end state in the todo tool before any write.

## End state

1. **Fixture.** Look for an existing save with a working train line before asking the owner to
   build one. It must be disposable, not a campaign save (spec §7's common setup). Run the probe
   sweep first (`WORKFLOW.md`, probe hygiene). These are tests of vanilla behaviour: neither mod
   touches trains, so the standing both-mods-loaded rig does not intersect them. Say so when you
   record the results.
2. **T1, T2, T3 with the owner**, in that order. T4 is optional. For each, record the fixture's
   layout, fleet, stock levels and station spacing, and report that colony, not a
   generalisation.
3. **Record the results in spec §7 in place:** what was observed, and `[RAN <date>, log <name>]`
   on every console line that actually ran. Replace `<<PENDING-RUN>>` only for what ran.
4. **Re-scope from the results.** T2 decides §10's shape: if it passed, the prototype's question
   narrows to more than four connectors; if it failed, re-scope OPTION 5 before anything else.
   If T1 or T3 contradicts §4, correct §4.
5. **OI-10.** If the results change the ask, edit it within the checklist's entrance gate: at
   most six bullet lines and a `Home:` line.
6. **Only if the owner rules OI-10 for the prototype**, author the build prompt from spec §10
   with `prompt-authoring`, as a new root one-off. If they do not, stop at step 5.

If time runs out, drop T4 first, then step 6.

## Your call

How to read each result, whether it corrects §4 or §5, and how to word the re-scope. Record the
call in the commit message.

## Scope

In: running and recording §7 T1–T4, and amending the spec and OI-10 to match.
Out: any `Code/` edit, shared-TestKit work beyond what `tools/TESTKIT.md` and `tools/SMRTK.md` allow (the fix pack's permissions), and the Codex
capability comparison, which is the owner's own action (see Loose ends).

## Stops

- A console line fails in the sandbox: record it and report. Do not route around it with mod code.
- T2 fails: stop before any prototype work, and put the re-scope to the owner.
- Anything needs a `Code/` edit, or TestKit work those two files do not allow: stop. That is an
  owner call.

## Do not claim

- "Module A works" from T3. The true, narrower claim is that vanilla's unwired policy branch
  behaves as read when driven by hand in this fixture.
- "Interchange works" in general from T2. Report the one colony tested.

## Loose ends

- The owner may run a Codex capability comparison on asset work. The draft question is at
  `C:\Users\stkot\AppData\Local\Temp\claude\c--Dev-SMR-OptInPack\03db6355-770f-4d42-87ee-b45043f495b5\scratchpad\CODEX_ASSET_CAPABILITY_QUESTION.md`.
  That is a temp path and may be gone; spec §9 carries everything needed to regenerate it. If the
  owner reports Codex's answers, record the comparison in spec §9. The discriminating questions are
  scripted Blender and whether a mod can reference a packed mesh.

## Lifecycle

One-off. Delete this file and its map row in `README.md` once the tests are recorded and either
the prototype build prompt exists or the owner has deferred it.
