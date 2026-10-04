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

**03A release corrections, 2026-10-03 (Claude Fable 5.1, `claude-fable-5-1`, from this
session's system prompt; no subagents). Commits: `284d13f` (tools and procedures), then the
commit carrying this note (launch assembly proof and close).** Receipts:
`archive/release_corrections_20261003/`. Verify these independently; this seat graded none
of its own claims beyond the commands named.

What landed, with the command that would falsify each:

- **F2** `tools/store_parity.py`: arity error gone; the report fallback removed; the source
  blocks are the STAGED copy and the card's `## Current live copy` section the last CONFIRMED
  LIVE copy. Preparation reports a difference and does not fail on it; `--confirm-live` (close)
  requires equality. A live card missing a body, a card with no `## State:` line and a
  pre-publication card holding a body all fail. Dated history is never selected.
- **F3** `tools/pack_list.py`: `reconcile()` exits 1 on changed bytes, missing, extra and
  unread members; `--allow-differ` names declared exceptions. Extraction is still
  `flpk_extract.extract`. Adaptation declared in `sync_from_fixpack.TOOLS_ADAPTED`; the
  donor's copy is unchanged and still exits 0 (takeable: propose it through the knowledge-sync pass).
- **F1/F4** `tools/release_batch.py` (state `support/RELEASE_BATCH.json`): a batch pins its
  base commit, its Pending headings, a hashed launch tree exported from that commit, per-portal
  package snapshots and owner receipts, and its close steps. `status` separates NEW_BATCH,
  PREPARED, UPLOADING, PARTIAL and CLOSE_OWED; an id is never read as an upload; `drain` moves
  only the pinned entries and is idempotent.
- **F5** `UPLOAD_WORKFLOW.md`, `release_prompt.md`, `POST_UPLOAD_CLOSE.md`: no listing
  question; platforms chosen at upload and reported after; "stores done" → agent puts real ids
  and links on the site and README → owner deploys → "site published". Preconditions cite
  durable reports. Zero-FAIL wording replaces "5/5". Donor handoff is one checklist item, the
  only donor write.
- Falsifier for all of it: `python tools/release_selftest.py` (53 legs: parity, package,
  batch states including first publish, partial upload, allocated-id-failed-upload,
  interrupted close, later Pending during the hold, ordinary update). The audit's own
  `verify.py` now shows `different_bytes` exit 1 and `matching_control` exit 0.

Drift and decisions to challenge, every one:

- **The launch tree is permanent, not a D19 workaround.** Every upload comes from
  `B:\Dev\SMR\SMR-OptInPack-launch`, a sibling folder exported from the batch's base commit,
  and the owner re-points the Mods junction with `release_batch.py link launch|repo`. Reason:
  the packer walks files, so the working repo ships whatever is in it. This adds two owner
  commands and a snapshot line to `UPLOAD_WORKFLOW.md` under 03A's assembly delegation, with
  no separate owner ruling. `link` was exercised on a scratch junction only; the real Mods
  link was not touched and the editor has never opened a launch tree.
- **The staging workbench session ran beside this one** and moved the Arboretum out of this
  mod's tree. Its `78eed20` moved D19 to `staging/` (ignored by the packer) while this link was
  mid-flight, so the held `metadata.lua`/`items.lua` hunks the brief describes no longer exist
  and `release_batch.HELD_OUT` ships empty; the mechanism and its selftest legs remain for the
  next held module. The Arboretum's `### Pending` entry is still an uncommitted hunk in the
  outbox and was kept out of `284d13f` by partial index. `begin` reads the committed outbox, so
  it cannot enter a batch until someone commits it; when that happens it needs `--hold`.
- **Tag contract changed.** `optin-v<major.minor.version>` (the donor's `fixpack-v1.0.0`
  spelling) on the batch's BASE commit; WORKFLOW's `optin-<version>` and "packed commit" are
  gone. No commit is claimed byte-identical to a package; package identity is the snapshot
  sha256 in the batch record.
- **STATE carries no release marker any more**; the batch record is the resumable state.
- **The comment-restoration step is gone** because the editor never opens the repo's files;
  the close copies writeback fields by hand. `release_batch.py writeback` parses scalars and
  the `code`/`ignore_files`/`entities` lists only; other tables and `items.lua` are a hand diff.
- **Source claims, not observations:** each upload repackages (`GedModEditor.lua:678`, `:770`),
  Steam saves a new id before packing (`SteamWorkshop.lua:17-22`), Paradox saves ids after the
  publish call (`ParadoxMods.lua:171-177`), all read on the archived 1.1.1.406343 tree. The
  temp package path `%LOCALAPPDATA%\Temp\Surviving Mars Relaunched\ModUpload\Pack\ModContent.fpk`
  comes from the fix pack's `reports/RELEASE_PORTAL_PREP.md`; that folder does not exist on the
  rig today, so it is unverified on this build. `snapshot` refuses when the file is absent and
  the procedure records the limit instead of an exact-package claim.
- `Textures/` and `Fallbacks/` are git-ignored and ship; the launch tree copies them from the
  working tree and hashes them, with no commit identity.
- `store_parity.fenced_block` now refuses a fence that belongs to a later heading; the card's
  Steam copy is compared byte for byte at `--confirm-live` (it was word-normalised).
  `pack_list --tree` now walks with `pack_predict.predict()` instead of its own `os.walk`.
- The audit's three parity fixtures in `verify.py` all exit 1 now: they carry no `## State:`
  line, so the new card contract rejects them, including the old pre-publication control. The
  acceptance cases live in `release_selftest.py`.
- `release_selftest.py` is run by the release procedure (§1a), not by doccheck: the peer
  session was editing `doccheck.py`'s gate list at the time. Takeable: add it as a
  `required_selftest` and give both new tools a `TOOL_GROUPS` row.
- **No batch is open.** Resumed 03 still changes the store blocks, so `begin` belongs to the
  release prompt's §2. The assembly proof here is a dry run of HEAD.

Launch assembly proof at `284d13f` (`archive/release_corrections_20261003/receipt.json`,
command `python docs/archive/release_corrections_20261003/receipt.py <new file>`): dry
assembly 90 members; predicted pack **75 files** = 19 Code + 2 Data + 54 other, identical in
membership to the working repo's prediction; **7 registered modules** (AcknowledgedWarnings,
DroneStatDials, ElevatorDepot, MultipleSuns, ServiceInterestTags, StationRows, TrainHub) = the
outbox FIRST PUBLICATION entry's D02/D04/D09/D15/D16/D17/D18; 8 option items = 8
`default_options` keys (six toggles, two dials); `code` list 19 = packed Code 19; 3 generated
files; 2 Data templates; 18 ignore filters; token `Arboretum` 0 hits in the launch tree against
5 files in `staging/` as the presence control. On that tree: preflight exit 0, store parity
exit 0, selftest exit 0; `--confirm-live` exits 1 on the pre-publication card, as it must.
`audit_controls_after.json` is the audit's own `verify.py` on the repaired tools. This is a
proof of the mechanism on today's HEAD, not the accepted launch package: no editor, portal,
junction swap or real package was involved.

**Owner 2026-10-03 (OI-49): the original Tripo hub model was the owner's own generation on a
paid plan; "we own the license for it."** The retained under-deck beds, stub pylons and feet
need no third-party credit or notice. Record the provenance where the credits and asset notes
live, attributed to the owner, and add no Tripo attribution line.

**This link ran at `298ff9b`, 2026-10-03, and rejected preparation (`c1d8c7e`).** Durable
record: `reports/FINAL_LAUNCH_AUDIT_20261003.md`; independent source/log checks
and concrete tool falsifiers: `archive/final_launch_audit_20261003/`.
03A now owns F1–F5 (launch artifact and release lifecycle/gates); 03 owns F6/F7
(disclosures/credits/site and OI-49). They run before this review resumes. Preserve
all accepted owner evidence; no repeat of the battery, warning or residual reader.
Recheck changed inputs and unresolved claims, not the accepted battery again.
The audit transcript identifies gpt-6-astra, also used for 01/brief authoring:
fresh context here does not discharge the different-model whole-chain condition.
The owner selects the final independent review model after corrections land.

**Owner 2026-10-03: 01A's residue is accepted with disclosure ("a"); the launch residue hold is
lifted.** The serialized owners of the leftover class references stay UNKNOWN by choice. No save
reader or shared-kit work is commissioned. Ship both exact disclosure sentences from
`reports/SHIP_RESIDUAL_20261003.md` §"Residual dispositions and exact disclosure" alongside
OI-45's uninstall note, and make no clean-removal claim. 01A is deleted. **OI-50: the Arboretum
ships after launch** (recorded in `Launch_Prep/README.md`).

**02 closed by the owner, 2026-10-03; its prompt is deleted.**

- **E-P and E-A** (Mod Options enable, live roundtrip, cold persistence, fix pack absent) are
  **cleared on the owner's play**. The owner has used Mod Options in both configurations
  throughout development (memory rule: owner play is evidence).
- **W-NEW PASS, owner-attended, guided by the orchestrator session.** A native save `WARNTEST`
  was written with `optional_mod` false (`0579b78`). It was loaded after a full restart with
  Opt-In disabled, and showed the native dialog "The following mods are missing or outdated:
  Relaunched Fix Pack: Opt-In Modules. Some features may not work." with Load anyway / Cancel
  (owner screenshot). W-OLD and W-refresh were not run; the owner scratched them.
- **No log was archived for this check;** the evidence is the owner's screenshot.

01A desk evidence committed at `b1c1e32`:
`reports/SHIP_RESIDUAL_20261003.md` and `archive/ship_residual_20261003/` preserve
exact hashes/metadata/token offsets, candidate modifier strings, source hashes and
capability searches. Stop 1: original class owners and modifier registrations/effects
remain UNKNOWN; no game/kit changes, native result or audit. 01A remains live.
Audit its concrete shared-kit contract before accepting implemented bindings;
post-load paths do not prove serialized ownership and current sync/fixups can alter
registrations. The report carries exact disclosures for 03.

Drift: the first instrument assumed literal SPCONRT at offset zero and a metadata.lua
member; it failed closed. Preserved v2 reads savegame_metadata and records the mgvs
prefix; decoded persist contains no literal SPCONRT, with residual tokens as positive
controls. This refutes the assumed marker, not the matching fixture identity.
A source-locator path typo was corrected before citing Building.lua. No graph tags
were guessed. OI-50/checklist and older 02 prerequisite still ask a question already
settled by `7f9c0e6`/`0ff4a85`; README's post-launch D19 ruling governs. Historical
STATE train/build claims likewise do not override command-read evidence. Existing
Arboretum/release working-tree edits and kit slots were preserved. Execution model
exposed in this transcript is GPT-6; independent different-model audit remains owed.

01's prepared evidence/plan is committed at `0579b78`; its lifecycle close consumes
01 with graph work owned by 01A and owner decisions at OI-49/OI-50. The report is
`reports/SHIP_EVIDENCE_20261003.md`. Review the actual commit diff: shared Arboretum
work was excluded via partial hunks, although the working-tree checks included it.

01 close checks: doccheck initially failed only on the unstaged moved gamepatch
path; staging the byte-identical move restored GREEN. Archived engine-diff
whitespace is intentionally preserved. Metadata's former "no warning / one dial
caveat" comment was corrected alongside the granted OI-43 flag. A final sequential
second-seat reread confirmed all plan corrections; implementation/binding review
still precedes any sitting. These are desk checks, not new gameplay evidence.

01 evidence prep, 2026-10-03: `reports/SHIP_EVIDENCE_20261003.md`, archive
`ship_evidence_20261003/`, and new 01A residual prerequisite. Review all of these
drift instances: default gamepatch command now compares the newer identical
pair, so historic work required explicit old/new inputs; the BuildMenu diff also
has mouse-leave delegation omitted by the original lead; D19 uncommitted test
content is present in the emitted package set (OI-50), not certified by the old
launch scope; removed OI asks had unperformed actions, now implemented/homed;
source sigcheck is noisy and is not a semantic PASS; Save B contains colony
upgrade receipt as well as both class tokens, but native graph owners remain
UNKNOWN; existing rescue is dial-era only, no train coverage; Tripo-derived
under-deck geometry remains and lacks origin/plan evidence (OI-49); site credit/
residue parity remains 03's work, local maintained blocks/metadata now updated.

Sequential second-seat plan findings were corrected: blocked AccountStorage
access, weak one-row transition predicate, missing W executable-absence gate,
paused save completion, class-token/object conflation, post-load modifier
reconstruction and optional-flag refresh. Recheck final implemented kit bindings
before any sitting; the source specification alone is not a runnable installed
kit. An early commentary inference of changed save-extension code was withdrawn;
existing explicit Override load is the cross-process route, menu discovery is
still unproved. No train battery/soak reopened, no game launch, no sibling edits.
Root execution is gpt-6-astra (transcript recorded in report); this terminal
audit still needs the owner's different model selection.

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
