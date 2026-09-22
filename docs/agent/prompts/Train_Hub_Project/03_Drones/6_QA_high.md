# Drones chain, link 6 — terminal adversarial QA, fresh context

**Link 6, the last link of the `03_Drones` chain** (`README.md`). **Fresh context, and the owner
runs it on a different model from the links it audits.** Trust nothing forward: every earlier link's
report is a claim until you check it against the code, the commits and the logs.

Read `DESIGN.md`, this folder's `README.md`, and your `## Notes from upstream`. `git log`,
`git pull` both repos first.

## Authority

The chain method (`docs/agent/support/CHAIN_METHOD.md`): the terminal link audits every handoff that
landed, sweeps owed work, checks consistency, samples verdicts against primary evidence, and holds
the folder-empty gate. Its value on a clean run is certification plus residue, not rescue.

## End state

1. **Every handoff landed.** Each earlier link's notes reached the link that needed them, and what
   shipped matches what its report claims. Sample the strongest claim of each link against the code.
2. **The bans.** The persisted name is in the inventory, spelled the same in code and record, with
   its kind field for build 5; no executable reference crosses to the fix pack.
3. **`DESIGN.md` against the build:** each owner ruling either implemented, or explicitly recorded
   as overtaken with the owner's word behind it. The pad-to-pit change is the known one.
4. **Owed work swept:** what the smoke did not cover (both configurations, both toggle directions),
   anything routed to the owner still open, and every drift instance the links logged.
5. **The gate:** this folder holds only `DESIGN.md` and `README.md` when you are done. A link file
   still here means that link did not finish; say so rather than deleting it for them.
6. A verdict of PASS, PASS WITH CORRECTIONS or FAIL, with the corrections listed as work, and the
   kickoff line for whatever the owner has queued next, or a line saying nothing is queued.

## Live work list

One todo item per commit-and-verify unit.

## Scope

In: auditing this chain's work and records. Out: building, redesigning, or fixing what you find
beyond a one-line records correction — those become listed work, not your edits.

## Stops

1. A claim cannot be checked because its evidence was never committed: record it as unverifiable,
   which is a finding, not a blocker.
2. You find a fault that makes the build unsafe to keep: stop and route it to the owner with the
   evidence.

## Do not claim

Do not certify what you only read a report about. Name the command, or the file and line, behind
each verdict.

## Notes from upstream

*(every link appends drift instances and residue here)*

## Lifecycle

Your report is the chain's close-out. **Delete this file and strike its row in `README.md` in the
same commit**, leaving the folder at `DESIGN.md` + `README.md`.
