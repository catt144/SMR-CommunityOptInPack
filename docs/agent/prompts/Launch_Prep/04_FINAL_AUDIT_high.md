# 04 — Adversarial backward audit of launch preparation

Authority: owner 2026-10-02 launch preparation and CHAIN_METHOD's independent terminal review.
Reasoning: high; challenge coverage/handoffs. Authored at `63424af`. Run in fresh context on a
different owner-selected model from execution and brief authoring. Fire after upstream completion.

## Outcome and method

An independently checked ledger states accepted preparation, owner upload actions remaining and
anything blocking the permanent release prompt. “Ready to publish” is not the verdict.
An incomplete chain stays live with owned corrections. Start `git log --oneline -5`, `git pull`,
`git status --short`; read chain README and audit report, then landed commits/primary evidence.
Keep one live commit-and-verify item in progress. Use doc-editing, smr-bug-library,
smr-orientation and prompt-authoring for corrections; CLAUDE/WORKFLOW/FIX_POLICY/release support
bind. Read headers before writes. Re-run volatile inputs; a forward GREEN is not proof of claims.

## Audit questions

- Does RELEASE_SYSTEM implement first publish and updates, owner HOLD/resume, editor version/id/
  comment preservation, downloaded-package comparison, exact Opt-In tags, outbox/history and
  every gate/map? Can a fresh session recover a partial upload without duplicating releases?
- Does each emitted shipping member have source and configuration evidence? Check 35's log-backed
  train results/dispositions without repeating its battery; inherit D15's accepted conditions
  only while they hold. D-entry status matches attendance; D14 launch residue is owned.
- Are actual shipping Lua.fpk/Data inputs verified on the command-read build with moved groups
  resolved and pending gamepatch work consumed? Fingerprint/parser alone cannot pass this.
- Do save exit, optional flag/old-save limits and applicable rescue coverage agree with measured
  residue and owner decisions? Do not waive an unfulfilled rescue duty. Do standalone and content
  persistence claims agree everywhere?
- Are OI-11/12/13/14/21/38 and OI-43/44 genuinely owed, or removed with action at its proper home?
  No repeated auto-fill questions or tracking storefront counters.
- Are both store bodies, summary, gallery, preview, tags, changelog, public README, module pages,
  nav/README mods row and install/FAQ/report text coherent? No retired modules, phantom ids or
  certification claims. Credits/provenance and asset/editor-round-trip/ignore guards hold.
- Does each donor publish-day obligation have an exact handoff/release owner, without early
  restoration or silent donor edits? Is site deployment separate from commits?

Sample consequential claims against archived source/logs, not just summaries; examine every
upstream drift instance. Choose independent falsifiers when conclusions have only confirming
checks. Record contrary evidence and uncertainty, never erase it.

## Scope and stops

In: independent review, local report corrections and owned continuations. Out: publishing,
silent behaviour fixes, sibling writes and repeating whole accepted batteries.

1. Shipping gap/invalid claim needs build or test: route with falsifier and retain chain until
   correction and independent verification land.
2. Owner-only ruling/access is needed: file concrete question on the right checklist, preserve
   dependency and finish independent audit work.
3. Primary evidence cannot substantiate a status: state the limit, not a substitute PASS.

## Close

Run doccheck, upload preflight and required site/render/link checks on final inputs; repeat only
for changed inputs or unresolved concerns. Review exact diffs/status in involved repos. Report
local checks and owner actions with evidence/limits, not portal success. When agent preparation
is accepted and upload obligations live in the permanent system, write the durable verdict,
remove this file and exhausted folder/parent row, commit exact paths and push. No unfinished
obligation may vanish. End with `task docs/agent/prompts/perma/release_prompt.md` as the owner's
next kickoff, or the exact corrective brief if prep remains blocked. No automatic chain/upload.

## Notes from upstream

Initial drift: old release brief's metadata/pack assumptions; public README; WORKFLOW version
and size prose versus donor/OI-18; OI-11 freeze language; OI-14 string count; STATE build/testing
generalisations; description missing D15; donor backup-delivery prose versus settled auto-fill;
parked donor text versus current modules; saved optional flag fallback. Audit report has evidence.

Train final close-out (2026-10-03): use `TRAIN_FINAL_BATTERY_20261002.md` and its
final-result receipt. Battery PASS is owner-scoped, with A waived and explicit
skips/strikes; no broad all-cases-pass claim. 01 owns the non-gating TestKit,
class-reference and OI-45 exit findings. Check that its downstream handling keeps
these evidence boundaries: the issued native-menu load instruction was wrong;
station 10531 is underground; the removal process first loaded a content-bearing
save with five errors, then the correct content-free Save B without later errors
in the captured prefix; both hub and depot class warnings survived deletion.
Zero-hub inheritance is OWNER, stock retention is measured across paired rows.
The removal log was open at capture. No whole-process clean or recovery claim.

03 store-and-site run, 2026-10-03 (Claude Fable 5.1; fired by the owner at `214f0ad`, before
RELEASE_SYSTEM, 01 and 02; subagents: site pages on Opus 5.5, tool ports on Sonnet 5.5, both
reviewed and corrected by the orchestrator). Report `reports/STORE_AND_SITE_20261003.md`.
Drift and decisions to examine, every one:

- **Out-of-order fire.** 03's fill targets (`docs/UPLOAD_WORKFLOW.md`, `STORE_CARD_LIVE.md`,
  outbox) do not exist; the maintained store bodies, first-release change note and first-publish
  steps live in the report §3/§6. `tools/store_parity.py` reads `docs/UPLOAD_WORKFLOW.md` by
  default and falls back to the report with a printed note; `paradox_card.py` takes `--source`.
  Check the release-system build lifts them and removes the fallback's reason to exist.
- **OI-21 executed under stop 1, unruled:** local ports of `paradox_card.py` and
  `store_screenshots.py`; OI-21 rewritten to "keep" or "run from the fix pack".
- **`metadata.lua` `description` is now the whole store body** (lede = OI-42 text with one D15
  clause inserted; sections; OI-45 note last), generated from the Paradox block by
  `store_parity.py --write-metadata`; `last_changes` is the first-release note. Was widening the
  approved paragraph into a sectioned body a copy/layout call (03's delegation) or a reopening?
  The approved sentences are byte-preserved inside it; judge that.
- **`*/store_screenshots/*`** added to `ignore_files` and `pack_predict.IGNORE` (17 filters now).
  `image` and `screenshot1..5` were wired 2026-10-03 (`reports/STORE_SCREENSHOTS_20261003.md`);
  confirm with `python tools/upload_preflight.py`.
- **Claims rest on pre-01/02 evidence only** (report §4 map). The site's acknowledged-warnings
  "in your save" line and the modders page's prefix warning come from code and FIX_POLICY §3, not
  from the store body; the orchestrator kept them after reading the source. Credits and the
  §3 row-18 hub-upgrade residual disclosure are routed to 01, not written.
- **Site commit `d87c700`** in `SMR-CommunityMods` (this repo: `736e6e6` work, then the records commit): `content/opt-in/`
  (two pages), nav, `site_description`, README row, scoped edits to index/install/faq/
  for-modders/report. `mkdocs build --strict` clean. **Not deployed.** The landing still leads
  with the fix pack by design.
- `python tools/sync_from_fixpack.py --tools` reports `upload_preflight.py` DIFFERS undeclared
  and `doccheck.py` RECHECK — both pre-existing (OI-18's 2026-10-02 adaptation was never
  declared); left for the knowledge-sync pass, named here so it is not lost.
- The imagegen skill the brief names is not installed; preview candidates are Pillow composites
  of the shipped icon renders (`local/store_art_candidates/`), not gameplay captures. No clean
  capture of the final hub/depot look exists in the owner's drop folder; a shot list was issued.

**Release system built 2026-10-03 by the same seat that ran 03** (owner instruction: *"build
the upload_workflow first draft and get everything setup so the release prompt only has to
polish"*). Record: `reports/STORE_AND_SITE_20261003.md` §11; the root brief is consumed
(`git log --diff-filter=D -- docs/agent/prompts/RELEASE_SYSTEM_high.md`). Your first audit
question now has concrete targets: `docs/UPLOAD_WORKFLOW.md`, `perma/release_prompt.md` (§0
half-done detection, §1a preconditions, §3 partial upload), `perma/RELEASE_OUTBOX.md`,
`support/RELEASE_SURFACES.md`, `support/POST_UPLOAD_CLOSE.md`, `support/LIVE_SITE_READ.md`,
`reports/STORE_CARD_LIVE.md`, `tools/store_parity.py`. Decisions to challenge: the store body
is generated from the owner file (not three hand-kept copies); the card holds no body before
publication; `outbox` class accepted by a one-row override in doccheck; WORKFLOW's release
text rewritten under the standardisation authority (old agent major/minor step removed,
5 MB statement replaced by the OI-18 ceiling). Execution and authoring were one model.
