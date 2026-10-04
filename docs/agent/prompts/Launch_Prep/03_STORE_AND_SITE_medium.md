# 03 — Store surfaces and the shared site

Authority: owner 2026-10-02 requested store pages and shared-site integration; OI-42 approved
metadata description/summary. Reasoning: medium; evidence/product are settled upstream, while
copy/layout choices are delegated. Authored at `63424af`. Fire after 02; independent drafts
may be prepared earlier without claiming untested behaviour. No publication in this brief.

## Outcome and evidence

Store-ready Paradox/Steam copy, selected art/gallery, current public README and shared-site
pages, complete claim-to-source mapping and passing package gates. Give the owner a concrete
upload handoff through the release system. Choose plain player language and a small coherent
site structure, not a new feature design. Keep one live commit-and-verify item in progress.

Start `git log --oneline -5`, `git pull`, `git status --short` here and read status/log in
`B:/Dev/SMR/SMR-CommunityMods`; read its applicable instructions before writes. Use doc-editing,
rule-placement, smr-bug-library, prompt-authoring for continuations; CLAUDE, WORKFLOW,
FIX_POLICY and built RELEASE_SURFACES bind. Audit report has evidence/falsifying commands.
At `63424af` approved metadata omits D15, README names retired modules, image/gallery/ids are
absent and last_changes is split-era. Gameplay/Buildings tags exist. Site `fd31bcf` was clean
and already routed opt-in reports to shared issues; read current status before relying on it.

## Work

1. Execute OI-21's ruled tool route. Recommend local ports: donor scripts derive their own
   workflow and hard-code fix-pack captures. Different cwd does not adapt them. A donor
   parameterised route needs an exact external handoff; this brief grants no donor writes.
   Add local ports to the tool catalogue and sync declarations as applicable.
2. Preserve OI-42's approved meanings, include D15 in complete coverage, remove retired/parked
   claims from live surfaces. Keep standalone/default-off, content persistence and safe
   uninstall/restart/save instructions. Use upstream residual/rescue evidence, credits and
   FIX_POLICY §7 platform/achievement wording. Substantive new owner choices need review;
   do not reopen the approved summary merely for style or advertise clean removal/load-first.
3. Fill STORE_CARD_LIVE's explicit pre-publication state, metadata as authorised, UPLOAD_WORKFLOW
   Paradox/Steam backup blocks and first-release last_changes. Prove text parity while preserving
   portal markup. Outbox holds first-publish scope, not unpublished internal-fix history.
4. Prepare concrete preview candidates/gallery capture choices for OI-12 and apply the owner's
   selection. Use imagegen skill if generating/editing raster art. Gameplay claims use real
   captures. Wire fields and verify limits with current tools/source and portal rules. Exclude
   gallery/source-only files from packing while retaining upload access; preserve ignore parity.
5. Build a dedicated Opt-In site section (recommended `content/opt-in/`), each shipping module
   discoverable with its defaults and off/removal behaviour. Update nav, README mods table,
   site description, scoped landing/install/FAQ/modder/reporting passages and this mod's public
   README. Preserve fix-pack URLs/backend. Report-page disable-all advice needs a backed-up-save
   content-mod path. Only player content goes under `content/`, no included agent documents.
6. Reconcile donor PARKED_OPTIN_REFERENCES against today's product into an exact publish-day
   handoff. No wholesale stale restoration or donor edits. Donor metadata/store changes require
   its own owner release. No fake ids or early deployment of upcoming links.
7. Fill first-publish steps in UPLOAD_WORKFLOW: OI-44 listing/id check, account access, own console
   approval/platform choice, Paradox then Steam, gallery/styling, writeback and downloaded archive
   comparison. Ids assigned at creation get an explicit post-creation fill step, not a guess.

Read shared status/HEAD before writes and commits; never stash/commit another person's hunks.
For a conflict prepare an exact patch with base and coordinate. Review merged surface promises.
Commit each repo's exact paths separately; site commit does not deploy it.

## Scope and stops

In: local player text, assets and ruled tools, release records/package filters, shared site
content/nav/README. Out: module behaviour, donor/rescue writes, new report backend, Mod Editor,
packing/upload and site deployment.

1. Missing owner art/tool/portal decision: prepare concrete choices or named placeholders,
   file only the needed ask and finish independent work.
2. Claim lacks shipping/removal evidence: route to its owner; do not invent a public promise.
3. Shared changes cannot safely combine: preserve proposed patch/base and report the conflict.

## Verify and close

Run doccheck GREEN, parsecheck for Lua text changes, upload_preflight with zero FAIL before
handoff, pack_predict with member/byte reconciliation, and `python -m mkdocs build --strict`
in the site repo. Check rendering, links, copy parity and selected gallery. No certification
claim from local checks. Record owner actions and committed-but-undeployed site sha.
04 audits on a different owner-selected model. Append commits/evidence/owner actions and every
drift to 04; strike row, delete brief and push exact commits when deliverables are complete.

## Notes from upstream

**03A landed (`284d13f`), 2026-10-03; resume here.** What changed under you:
`python tools/store_parity.py` no longer has a report fallback and now checks the store card's
shape; the §3 blocks in `docs/UPLOAD_WORKFLOW.md` are the staged copy and the card stays
pre-publication until the close. The package gates run on a launch tree
(`python tools/release_batch.py assemble --out scratch/<dir>` for a dry one), not on the repo.
`UPLOAD_WORKFLOW.md`'s first-publish steps and §4/§5 order were rewritten (no listing
question; "stores done" → the agent adds real store links to the site's `## Get it` section
and the README → the owner deploys). Do not open a batch (`begin`): that is the release
prompt's §2, after your surfaces and 04's verdict. F6/F7's site and disclosure work is
still yours. The Arboretum now lives in `staging/` (`78eed20`).

**Owner 2026-10-03 (OI-49): the original Tripo hub model was the owner's own generation on a
paid plan; "we own the license for it."** The retained under-deck beds, stub pylons and feet
need no third-party credit or notice. Record the provenance where the credits and asset notes
live, attributed to the owner, and add no Tripo attribution line.

**04 audit `c1d8c7e`, 2026-10-03: preparation not accepted.** Read
`reports/FINAL_LAUNCH_AUDIT_20261003.md`. 03A owns release tools/lifecycle and an
actual launch package excluding held D19. Resume this link after 03A lands.
Your remaining unit is F6/F7: put both exact residual disclosures and the prior-art
credit on the maintained bodies/site/public README; reconcile module removal
sections and move the content-mod exception before the report page's disable-all
instruction. Resolve OI-49's actual provenance before assigning its notice.
OI-12 and OI-21 are closed; no listing exists (OI-44 answered half); 02 is closed;
01A's residue hold is lifted. Existing dial rescue is an unpublished contingency,
not a new launch upload or train recovery project (audit's archived owner ruling).
Recheck final surface claims against the accepted launch tree, then run parity,
preflight, render/link and site build checks and close this link. No publication.
The optional OI-51 preference is not a gate; if still unanswered when this brief
is consumed, rehome its checklist Home to the train report and permanent release
surface job. Keep the publish-day donor handoff, resolving its already-done site
clauses against the current site instead of restoring them again.

**Owner 2026-10-03: 01A's residue is accepted with disclosure ("a"); the launch residue hold is
lifted.** The serialized owners of the leftover class references stay UNKNOWN by choice. No save
reader or shared-kit work is commissioned. Ship both exact disclosure sentences from
`reports/SHIP_RESIDUAL_20261003.md` §"Residual dispositions and exact disclosure" alongside
OI-45's uninstall note, and make no clean-removal claim. 01A is deleted. **OI-50: the Arboretum
ships after launch** (recorded in `Launch_Prep/README.md`).

01A desk disposition committed at `b1c1e32`: see
`reports/SHIP_RESIDUAL_20261003.md`. The report gives
exact demolition/missing-class disclosure text and retains the existing bought-
upgrade sentence. Keep both class-owner paths and original native modifier effects
UNKNOWN; candidate modifier-id strings are not registrations. No clean-removal,
harmless-reference or train-recovery claim is supported. OI-45 stands. 01A's
stop-1 hold remains; apply disclosures under your existing surface authority without
calling the launch residue row passed. OI-50 is already ruled post-launch in the
chain README; do not reopen the older package-scope question below.

01 preparation is `0579b78`; `reports/SHIP_EVIDENCE_20261003.md` owns receipts,
checks and remaining obligations. Doccheck/store parity/checkable upload guards
passed. Claims remain conditional on 01A, owner provenance/package choices,
02's actual evidence and 04; no publication or new gameplay verdict.

01 evidence preparation, 2026-10-03: `reports/SHIP_EVIDENCE_20261003.md` owns
the build ledger, exact save/pack receipts and provenance inventory. Source pack
parity passed; accepted module/train tests remain scoped, never repeated. OI-43
warn is implemented, OI-11 guard and OI-13 comments landed, English-only launch
is recorded for OI-14. 02 now has a conditional plan; 01A owns the unresolved
native class-reference/modifier prerequisite. Launch remains held on unresolved
rows, including OI-50's Arboretum scope and OI-49's Tripo origin/notice.

Local maintained UPLOAD_WORKFLOW §3 blocks now carry the exact prior-art credit
line and bought-hub-upgrade residue sentence from that report; metadata was
regenerated and parity passed. These blocks supersede the report's historical
§3 copy. Mirror both sentences to the shared site's `content/opt-in/index.md`
under your sibling-write authority, and add the credit to public README. Resolve
OI-49 before final asset notices; the hub retains Tripo-derived under-deck mesh,
so do not call the whole asset wholly original. Keep the uninstall note last.
OI-51 is the optional once-per-load notice consolidation choice, not a new gate.
Check applicable existing dial-rescue availability with its sibling release
owner; this pass neither edits nor certifies train recovery.

**Owner 2026-10-03 (OI-44): no Opt-In listing exists on either store**; only the fix pack has
ever shipped. The first upload creates both listings, Paradox then Steam. The console-approval
step is still the owner's open half of OI-44. **OI-21: "keep the ports"**: `tools/paradox_card.py`,
`tools/store_screenshots.py` and `tools/store_parity.py` stay here; no fix-pack edits are needed.

**Owner ruling 2026-10-03 (OI-45): an uninstall note goes at the bottom of each store page.**
It tells the player to demolish every train hub and Elevator Depot before removing the mod.
Removal with them standing raises native Lua errors on load; removal after demolition restores
vanilla station requests (`TRAIN_FINAL_BATTERY_20261002.md`, B2). No recovery work is built.

Audit: preserve existing opt-in report routing, not a duplicate backend. Audit report names
every reviewed player surface and the publish-day donor dependency.

**Run status, 2026-10-03 (orchestrator, Claude Fable 5.1), fired out of order at `214f0ad`:**
landed the maintained store bodies, generated metadata description/change note, public README,
local tool ports, ignore parity, preview candidates and shot list, the shared site's Opt-In
section (committed, undeployed) and the donor publish-day handoff; report
`reports/STORE_AND_SITE_20261003.md`. **Still open, so this brief stays live and its row
unstruck:** OI-21's word, OI-44's listing/console facts, credits and residual lines from 01, and claim
acceptance after 01/02 land. (The release system was built later the same day: the blocks and
first-publish steps now live in `docs/UPLOAD_WORKFLOW.md`; report §11.) Re-run from this note:
apply selections, re-run `store_parity.py`, preflight to zero FAIL, then strike and delete.
