# 03A — Repair the release lifecycle and isolate the launch package

Authority: owner launch preparation, the release-system standardisation grant,
and OI-50 (D19 ships after launch). Created by 04's failed terminal review at
`298ff9b`, 2026-10-03. Reasoning: high; recoverable release state and exact package
identity need adversarial controls. This is a correction link, not an upload.

## Outcome and starting evidence

An owner can perform first publication or an update, stop after either store,
and resume in a fresh session without duplicate releases or losing the actual
packed bytes. The launch artifact contains only the accepted launch modules.
04 must independently verify these corrections before the chain closes.

Start `git log --oneline -5`, `git pull`, `git status --short`; read
`reports/FINAL_LAUNCH_AUDIT_20261003.md`, especially F1–F5 and its evidence limits,
then the release prompt/support trio, owner workflow and applicable tool bodies.
Use smr-orientation, doc-editing, smr-bug-library, prompt-authoring and
rule-placement; CLAUDE, WORKFLOW, FIX_POLICY and CHAIN_METHOD bind. Sequential
work, no parallel agents. Keep one commit-and-verify unit in progress.

`python docs/archive/final_launch_audit_20261003/verify.py` reproduces the original
controls in isolated scratch files; an optional receipt path must be NEW (archive
is append-only). At the audit HEAD it captures the published-card TypeError,
missing-body false GREEN, and a real FLPK content mismatch with exit 0. It emits
observations rather than grading a future repair; add acceptance assertions.
Old results are in that directory's `receipt.json`.

## Live work list

| unit | initial state | acceptance |
|---|---|---|
| Correct parity/package gates and release recovery | pending | first-publish, ordinary update, partial upload, allocated-id-but-failed-upload and interrupted-close fixtures distinguish their states and pass the applicable checks |
| Prepare the exact launch artifact and its permanent handoff | pending | accepted membership reconciled across actual pack prediction, code/options/Data/generated lists, ignore filters and first-release outbox; held D19 work preserved; final gates run on those same inputs |

Delegate the implementation shape; the following are required outcomes, not a
prescribed state-file design:

- Repair `tools/store_parity.py`'s published-body call error. Missing one published
  body must fail. Distinguish staged copy from the last confirmed live copy so a
  legitimate update can be prepared without forging publication. Select the
  intended current blocks when dated history exists; remove the exhausted report
  fallback. Prove the failure controls as well as first-publish and update success.
- `tools/pack_list.py` must fail on byte differences, missing or extra members and
  unread/unextracted members, with an exact-match positive control. Respect the
  shared extractor rather than adding another decoder. Record adaptation in the
  local tool ledger; no silent donor fix.
- Fix half-done detection: ordinary Pending work after a prior live release is a
  new batch, not automatically an unfinished upload. Existing portal ids identify
  listings, not successful uploads of this batch. Pin a batch and pre-upload base,
  owner receipts, per-portal progress and package snapshots; resume idempotently.
  Never drain later/held Pending entries during a previous batch's close-out.
- Ground partial-upload and tagging instructions in archived 1.1.1.406343 source.
  Each upload packages again; Steam can allocate/save an id before upload, Paradox
  saves writeback after success. Remove the unsupported same-packed-file promise.
  Preserve each actual package and serializer output before restoring comments;
  reconcile intentional differences explicitly. Keep editor-owned versions and
  exact Opt-In release identity without claiming a comment-restored commit is
  byte-identical to an earlier pack. Reconcile WORKFLOW's `optin-<version>` with
  the permanent prompt's `optin-v<version>` spelling. No invented portal ids or
  storefront counters.
- Make first-publish sequencing executable: the owner chooses platforms at upload,
  rather than supplying an approval result before entering the upload workflow.
  The no-existing-listings answer is settled. After store creation, read ids,
  prepare/commit real links in the site and public README, then hand the owner the
  separate site-deployment step. No repeated auto-fill questions or portal actions.
- Resolve F1 under OI-50 without staging, restoring or shipping the held Arboretum
  hunks. Its runtime, generated template and Data source are already tracked, so
  merely using clean HEAD or omitting its Pending entry is insufficient. An
  isolated launch tree or a coherent packaging change is within the assembly job;
  choose the smallest sound solution and preserve the post-launch test build.
  Give the owner one unambiguous upload tree, with matching gates and snapshots.

## Scope and stops

In: local release tools, release procedures/maps/records, safe launch assembly,
and precise sibling handoffs. Out: runtime behaviour changes, gameplay, owner
Mod Editor/packing/upload, deployment and sibling writes.

1. Owner-only ruling or access is necessary: put the concrete ask on the proper
   checklist; complete independent work and retain this link.
2. A launch assembly would lose or alter the held work: preserve proposed changes
   and exact base, explain the conflict, and retain the dependency.
3. Primary evidence cannot establish package/publication identity: record the
   limit and a takeable correction; do not award an exact-byte or live verdict.

## Verify and close

Run the relevant negative controls, doccheck, store parity, upload preflight and
pack prediction on final release inputs. Review exact diffs; commit with pathspecs
(or reviewed partial index for shared files), push, and record receipt paths and
all drift in 04. Update sync adaptation declarations for local tool changes.
Delete this brief and strike its manifest row only when both units are complete.
Next owner kickoff is resumed `03_STORE_AND_SITE_medium.md`; then 04 verifies the
landed corrections on a different owner-selected model from their execution.
No automatic chain or release.
