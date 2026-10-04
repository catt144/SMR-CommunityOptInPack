# Final launch-preparation audit — 2026-10-03

Authority: owner invocation of `Launch_Prep/04_FINAL_AUDIT_high.md`.
Started at `298ff9b76d6fca4293da9d8e5c734537cb691bd2`; `git pull` was up to date.
Scope: independent backward audit, local documentation corrections and owned
continuations. No gameplay, upload, deployment or sibling writes.

## Live work list

| commit-and-verify unit | state | evidence / owner |
|---|---|---|
| Audit primary evidence and release recovery; correct local records and route remaining preparation | COMPLETE in `c1d8c7e` | source/log and negative-control receipts; doccheck GREEN in the commit hook; 03A owns release corrections, 03 owns surfaces, 04 rechecks after both land |

## Initial contrary evidence

- `git diff -- metadata.lua items.lua docs/agent/prompts/perma/RELEASE_OUTBOX.md`
  shows held Arboretum additions. Owner OI-50 excludes D19 from first publication.
  `python tools/doccheck.py --emit-counts` emits eight registered modules in the
  working tree, including Arboretum. `python tools/pack_predict.py .` includes its
  runtime, generated template and Data source. An accepted launch package cannot
  be inferred from GREEN on these inputs. Preserve the held work.
- `UPLOAD_WORKFLOW.md` still asks whether listings exist despite the recorded
  owner answer that neither exists. `STATE.md` still says the train run is owed
  and no verification has occurred on 1.1.0; those lines contradict the landed
  evidence and owner dispositions.
- `SHIP_RESIDUAL_20261003.md`'s exact class-reference disclosure has not reached
  the maintained store blocks. Link 03 remains live; its pending preparation is
  not made complete by link 04 being invoked.

## Verdict

**Preparation not accepted.** Preserve the accepted shipping/gameplay evidence and
the owner's residue disposition. The actual launch artifact, release lifecycle
and unfinished public surfaces prevent the permanent release handoff. 03 and 04
remain live; corrective link **03A** precedes resumed 03 and resumed 04. No game
battery, residual reader, recovery build or portal action was run by this audit.

Executed model: **gpt-6-astra**, from `turn_context.payload.model` in
`C:/Users/stkot/.codex/sessions/2026/10/03/rollout-2026-10-03T20-53-25-01a10466-c21b-7441-abf1-68fce3fe6f1d.jsonl`.
An inline Python JSONL scan matched the exact user task `04_FINAL_AUDIT_high.md`
and emitted the model set. No subagents. This is fresh context, and independent
of the Claude release-system execution; **it is not a different model from 01
and the audit-brief authoring**. The chain's final different-model condition
remains for the owner's resumed terminal review, not an invented PASS here.

## Findings and corrective owners

### F1 — The current package violates the post-launch D19 ruling

MEASURED at audit HEAD with the original held diff: doccheck GREEN emits
**8 registered modules** = AcknowledgedWarnings + MultipleSuns + DroneStatDials +
ServiceInterestTags + StationRows + TrainHub + ElevatorDepot + Arboretum.
Command: `python tools/doccheck.py --emit-counts`; membership control:
`rg -n 'Register\(' Code -g 'Opt_*.lua'` with module-local ID constants resolved.
The owner's accepted launch set is that list **without Arboretum** (OI-50).

`python tools/pack_predict.py .` includes `Code/Opt_Arboretum.lua`,
`Code/BuildingTemplate/SMROptInArboretum.generated.lua` and
`Data/BuildingTemplate/SMROptInArboretum.lua`. `git ls-files '*Arboretum*'` confirms
all are already tracked in `0ff4a85`. A clean HEAD alone does not remove them:
the packer walks files, not only metadata's code list. The held metadata/items
hunks additionally load it, and its held `### Pending` entry would join the
release prompt's unfiltered batch. Neither code-list omission nor leaving the
held hunks unstaged establishes a launch package.

**Owner: 03A.** Prepare a coherent launch tree/package without losing the held
test build. Falsifier: the actual predicted launch members, options, Data and
generated lists or release batch still contain D19. Run final gates on that exact
tree; do not advertise the working-tree GREEN as launch acceptance.

### F2 — Store parity breaks after first publication and blocks updates

MEASURED control in `archive/final_launch_audit_20261003/receipt.json`:
`python docs/archive/final_launch_audit_20261003/verify.py` creates isolated cards
from the real maintained bodies. A complete matching LIVE card raises
`TypeError: main.<locals>.check() takes 3 positional arguments but 4 were given`.
A LIVE card missing one body returns exit 0 and labels itself pre-publication.
The empty pre-publication control passes legitimately. Production files were
not changed by these controls.

SOURCE: even after correcting the call arity, comparing the last published card
to new staged copy before upload makes an ordinary changed-body update fail.
Rewriting that card to get GREEN would falsify what is live. Also `fenced_block`
chooses the first heading, while the card's later-release procedure appends dated
sections: later published blocks do not become the selected current copy. The
report fallback remains in `store_parity.py` after its report blocks were moved;
its original reason to exist is exhausted.

**Owner: 03A.** Separate preparation parity from confirmed publication checks;
reject partial/malformed live cards and select current published bodies explicitly.
Controls: first publication, staged update with older live copy, confirmed update,
missing body and a damaged word. Preserve history and remove the dead fallback.

### F3 — Downloaded-package comparison returns success on different bytes

MEASURED: the audit constructs a real minimal FLPK containing `items.lua`, then
runs production `pack_list.py --tree` through its production reader/extractor.
Different bytes produce `CONTENT: 0 byte-identical to disk, 1 differ` and
`DIFFERS items.lua`, **exit 0**. Identical bytes produce the expected success.
Both outputs are archived in `receipt.json`. SOURCE: its return predicate checks
missing/extra names only, and unread extraction members are skipped.

**Owner: 03A**, local tool correction and declared adaptation; donor change remains
a separate handoff. Controls: changed bytes, missing/extra/unread members must
fail; exact names and bytes must pass. The current prose says differences are
findings, which mitigates a careful manual read but does not make exit 0 a guard.

### F4 — Release recovery confuses listing identity, pending work and upload state

SOURCE scenarios against `perma/release_prompt.md` §0/§3/§5 and
`support/POST_UPLOAD_CLOSE.md`:

- After a completed release, STATE says live. Add an ordinary Pending change.
  §0 calls that an already-half-done release and routes to close-out instead of
  deriving a new batch. No upload occurred in this scenario.
- On an update, both ids already exist, so an id-presence test cannot tell which
  portal received the new batch. On first creation, Steam can save its id before
  the package/upload attempt; an id alone cannot prove even the first upload.
- The HOLD marker has no pinned batch/base/package identity. An interruption or
  a new Pending entry during HOLD leaves §5 clearing *every* Pending entry; the
  current held D19 entry is a concrete unrelated batch member.
- The procedure promises the second portal uses the same packed file, but the
  actual uploader calls `CreatePackageForUpload` for each upload. Its temporary
  folder is cleared, Paradox saves writeback after success, and first Steam
  creation saves the newly allocated id before packaging.
- Tagging a commit "whose bytes were packed" is not supported by any retained
  package snapshot or pre-comment-restoration receipt. Restoring comments and
  preserving later portal ids can create intentional differences from earlier
  packed metadata. A final working tree is not an exact receipt for both portals.
- Tag spelling also drifts: WORKFLOW's `optin-` plus version differs from the
  permanent prompt/support's `optin-v<version>`. Reconcile the exact naming
  contract together with the artifact identity, rather than creating both.

Game source is the hash-verified archived **1.1.1.406343 / build 25579348** tree:
`CommonLua/Classes/GedModEditor.lua:678` (package construction, temporary cleanup),
`:770` (prepare → package → upload); `CommonLua/Platforms/steam/SteamWorkshop.lua:17`
(create id and SaveWholeMod before upload); `CommonLua/Libs/Paradox/ParadoxMods.lua:171`
(ids/version writeback and SaveWholeMod after success). These are source claims,
not portal observations. `source_receipt.json` includes the archived bodies;
this audit verifies their hashes against the current shipping pack receipt.

**Owner: 03A.** Pin the batch/base and per-portal artifact/owner receipt; preserve
serializer output before restoring comments; make resume and drain idempotent.
Prove partial first upload, partial update, allocated-id/failed-upload, ordinary
new update and interrupted close. Keep editor-owned version fields and the
Opt-In tag family; never fabricate exact byte identity or infer success from ids.

### F5 — First-publish procedure has impossible ordering and settled questions

`UPLOAD_WORKFLOW.md` still asks whether drafts exist. Owner `deabb8f`/03 notes
already establishes no Opt-In listing exists; only platform/approval action
remains at OI-44. The release preconditions require the approval/platform facts
*before* handoff, while the owner learns the approval step at upload. Describe
the unresolved owner action explicitly instead of blocking entry to its workflow.

The owner is told to publish the site and check live store links before reporting
"uploaded". The agent learns the assigned ids at that report, and no earlier
agent step inserts those ids into the site's "Get it" placeholder or the public
README. The post-upload close fills STORE_CARD but does not explicitly update
those player destinations. This first-publish cycle cannot complete as written.

**Owner: 03A.** Add a store-completion/ids handoff, commit actual site and README
links, then hand back the separate deployment action. Link the permanent
preconditions to durable reports rather than deleted 01/02 briefs. Describe
current checks as zero FAIL, not a fixed "5/5" count (the current output includes
an INFO row). Preserve the settled auto-fill/formatting observations and no
storefront-counter tracking.

### F6 — Disclosures and credits have not reached all public surfaces

SOURCE comparison of `UPLOAD_WORKFLOW.md`, metadata, this repo's public README,
site `d87c700` and the exact residual report:

- The bought-upgrade sentence and ChoGGi/LukeH credit are on both maintained
  store bodies and generated metadata. The class-reference/no-clean-removal
  disclosure accepted by the owner is absent there.
- The site and public README have neither residual disclosure nor the scoped
  prior-art credit. Train module sections should carry or directly point at
  the full removal limitations; StationRows retains inert row settings too.
- `content/report.md` first tells players to disable every mod, restart and load,
  then gives the placed-content exception. Move the exception before that action
  so following the first instruction does not test unsafe removal inadvertently.
- OI-49 remains unanswered: the current hub retains Tripo-derived under-deck
  geometry. This audit does not infer plan/origin, prescribe a license or claim
  the entire asset is original.

**Owner: resumed 03; OI-49 is the owner's existing concrete question.** Apply both
exact disclosures, prior-art credit and applicable provenance notice under the
existing copy authority, then render/check parity and links. Keep OI-45's final
uninstall section. No sibling edit is within 04's scope and none was made here.

### F7 — Record drift and donor handoff need final reconciliation

Corrected locally in this audit: D05 now records E-P/E-A and W-NEW owner evidence
with its limits; D17/D18, FIX_POLICY and the residual report record the accepted
UNKNOWN and lifted hold. SHIP_EVIDENCE distinguishes its historical proposed
tests from owner-closed work. Removed STATE's false train-owed and unreverified
build lines; their evidence lives in the entries and reports. These role-specific,
dated chain statements fail the STATE door's reach/volatility tests; no new chain
todo was inserted there.

SOURCE: `STORE_AND_SITE_20261003.md` §7 maps the donor's P1–P40 and housekeeping
classes to keep/drop/adapt outcomes and the donor release owner. Some clauses
marked restore-at-publication (FAQ/modders routing) already appear in `d87c700`.
Do not restore them twice. The donor-owned metadata/store companion text remains
that mod's own release, after live Opt-In links exist. No donor publication was
implied by local copy. The permanent release prompt's "file on donor checklist"
versus "do not edit the fix pack" needs one explicit, scoped handoff route.

**Owners:** 03 reconciles the exact §7 site rows and rehomes optional OI-51 if its
prompt closes; 03A makes the permanent donor handoff executable. The existing
knowledge-sync prompt retains the declared drift review (`upload_preflight.py`
adaptation and doccheck recheck); do not conceal it with a declaration-only PASS.

## Accepted evidence and its limits

### Current source inputs and module coverage

`verify.py` independently verifies the existing full decoded-source receipt once:
the installed Lua/Data pack hashes still match, every archived member's SHA-256
and length matches, membership is nonempty/unique, and the current Steam build
is `25579348`. Totals reconcile to the original receipt's exact lists:
**Lua/CommonLua 2374/2374; Data 2192/2192**. No fingerprint-only or parser-only
semantic claim is substituted. Re-decoding unchanged hash-identical packs adds
no new evidence; the original receipt preserves the decoding command and body
comparison. Older unrelated fact groups remain MOVED, not blanket-promoted.

The archived `moved_bodies.diff` was read: RequiresMaintenance adds completion
of demand; Colony adds NoPolitics tech hiding; MarsGameEffects adds display
name; BuildMenu adds both the nil-template guard and mouse-leave delegation.
Those changes do not replace the accepted mod semantics. The 405907/406343
archive equality and explicit old/new historic comparison account for the
default patch command selecting the newer identical pair. The pending gamepatch
file was moved byte-identically to `gamepatch/done/` in `0579b78`; verdicts live
in D02/D04/D09 and SHIP_EVIDENCE, not in the consumed request. Sigcheck's noisy
lexical result is not used as semantic evidence.

| member/surface | accepted evidence / independent condition check |
|---|---|
| D02 | Owner play and both-configuration ruling retained. `git diff f3d6c78 -- Code/Opt_AcknowledgedWarnings.lua` empty. No status promotion. |
| D04 | Same owner scope retained. Reviewed `git diff 82369ec 0579b78 -- Code/Opt_MultipleSuns.lua`: comment and granted Require pair only; guard receipt includes absent-target and missing-declaration controls. |
| D09 | Owner play/both configurations and existing base cleanup accepted; `git diff f3d6c78 -- Code/Opt_DroneStatDials.lua` empty. |
| D15 | Attended acceptance remains conditional on unchanged implementation/no new donor overlap. `git diff 102aad0 -- Code/Opt_ServiceInterestTags.lua` empty; named-hook search still absent in donor Code with positive matches here. No new persistence or uninstall claim. |
| D16/D17/D18 | Owner-scoped battery, P release 1.0.26 and A waiver retained; gameplay files unchanged since evidence preparation. Arboretum is the only later Code addition in `git diff 0579b78 -- Code`. |
| D05 / warning | E-P/E-A cleared on owner play, W-NEW owner-witnessed dialog after full restart with mod disabled (`deabb8f`). W-OLD/W-refresh scratched; no archived log or newly reviewed screenshot in this audit. Owner testimony is accepted without invented instrument evidence. |
| D14 | Open remains correct. B5 skipped, B3/B6 owner-cleared, other B2/B4 items struck; individual source/desk limits remain. Recurrence routes to shared playtest owner; no new launch battery or soak. |
| D19 | Post-launch by owner OI-50. Its presence in the current package is F1, not accepted launch evidence. |

D15 named-hook control: inline Python over each `Code/**/*.lua` searched
`GetServiceDescription|sectionVisitors|sectionFoodService|IsOneOfInterests|ServiceInterestsList|GetServiceList|InfopanelSection|ipBuilding`,
asserting positive members here and no members in donor `30dacada`. This is a
scoped overlap check, not a proof of every possible cross-mod interaction.
Accepted legacy configuration claims retain the versions/limits their owner
records give; no missing historical version number is invented.

### Train primary evidence

`verify.py` checks each archived final log's hash, bytes, lines and **every**
receipt filter against newly selected member lines, not just stored counts. It
also checks every before/after stock member against its actual log line and
asserts equal stock/time with capacity 4000000 → 2000000. The **38** paired
object/resource keys reconcile to the stock receipt's member list and filter
(`1122..1976` versus `1977..2828`). This preserves B4's measured stock verdict;
zero-hub upgrade inheritance remains OWNER, not a slot reading.

The removal log has **5** earlier Lua errors at 213/265/286/336/372, and **0** in
the second-load window **404–481**. The positive control is the native-match,
mod-absent station read at 478; the retained class warnings are at 424/426.
Station 10531 is underground. The prefix ends before shutdown; no whole-process
clean verdict. The issued native-menu instruction was wrong and the explicit
filename load succeeded; save-menu discoverability remains unproved. No B1
arrival, stock comparison or waiver was turned into a broad all-cases pass.

### Save exit and existing rescue

The preserved Save B SHA-256 still matches
`b07a3cebc193c6eb129aa25e7e22da815cb152253f201a69282a4ae86dccd7d6`.
The archived decoded receipt distinguishes class/modifier **tokens** from native
objects, owning paths or registered effects. The failed literal-SPCONRT assumption
is retained beside v2's mgvs-prefixed decode; it does not refute the fixture.
Current adoption/fixups can change modifier registrations after native load, so
post-load values cannot establish original serialized ownership.

Owner `298ff9b` accepted that UNKNOWN with disclosure and ended 01A; owner OI-45
requires demolition and commissions no train recovery. That decision is
recorded where the obeying role reads it. No unfulfilled reader is retained as a
hidden gate; no clean-removal claim replaces it. Newly saved optional=false
warning behavior does not imply old optional=true saves warn or get repaired.

Read-only rescue check: sibling HEAD
`5d653a1c7b65a5f5e22a0697e25b7f634fb20021`, clean status; local 0.1.0 artifact
exists. Its `Code/10_SaveRescue.lua` ROWS names the exact DroneSpeedDial,
DroneCarryDial and acknowledgement fields; the mod-present stand-down uses
`SMROptInPack`. It supplies no train recovery. The donor D13 record preserves
its attended acceptance and version-skew limits; the later `e08ba62` change
renamed player text and explicitly routes a dialogue re-witness if published.

The apparent publication duty is settled by the actual owner's **2026-08-14
item 17** in donor `docs/archive/PLAYTEST_ARCHIVE.md:14451`: hold rescue in reserve,
publish only if post-release reports show players stuck with dial residue;
build does not mean publish, and dialogue wording is reconsidered if triggered.
Thus the applicable artifact exists as the owner's contingency; it is neither
owed a launch upload nor advertised as available train recovery. The dormant
publication/text-review obligation stays at donor D13 and the rescue tree.
No new rescue waiver or sibling edit was made.

## Owner-item reconciliation

| item | current disposition and home |
|---|---|
| OI-11 | Require pair implemented and allowlist exception removed in `0579b78`; D04 owns the ruling and guard evidence. No stale freeze. |
| OI-12 | Owner selected preview/gallery; fields wired and local image checks pass. `STORE_SCREENSHOTS_20261003.md` owns selection; no new art ask. |
| OI-13 | Comment-only sweep in core/MultipleSuns, inspected in `0579b78`; no behavior change. |
| OI-14 | English-only launch in FIX_POLICY §6, future translation home FUTURE_IDEAS §4(b); no old string count used. |
| OI-21 | Owner keeps local ports; their execution-before-ruling drift is historical, not an outstanding ask. |
| OI-38 | Accepted scripted UP leg and owner scope in train report; no additional soak or crossing-ledger proof commissioned. |
| OI-43 | false implemented; W-NEW owner pass; old-save/refresh controls scratched and their limits retained. |
| OI-44 | No listings exists is settled. Platform choice/approval and actual accounts remain owner upload actions, not agent portal success. |
| OI-49 | Still owed: actual Tripo asset origin/plan. Existing checklist item is concrete; do not duplicate it. |
| OI-50 | Settled post-launch D19; assemble a conforming artifact, do not ask again. |
| OI-51 | Optional startup-notice consolidation, not a launch gate. Current behavior stays without a new ruling/build. |

## Upstream drift review

| upstream instance | disposition in this audit |
|---|---|
| Old metadata/pack assumptions; public README; WORKFLOW version/size | Current README covers intended launch modules; OI-18 asset ceiling and editor-owned versions carried forward. Current package differs through F1; exact-byte/tag procedure still F4. |
| Freeze, string-count, STATE testing/build generalisations | Owner authority/command emissions govern; stale STATE lines removed; no reopened freeze or historical count. |
| Missing D15 in lede; sectioned body versus approved paragraph | Delegated coverage/layout work accepted: byte comparison of `63424af:metadata.lua` with the current first paragraph after removing only its inserted D15 clause is equal; summary is equal too. `736e6e6` adds full module detail and keeps OI-45 last. No substantive reopening identified. |
| Donor auto-fill/backups and storefront counters | Owner observations remain settled. No fresh auto-fill test or matching-counter project; F5 removes repeated listing asks. |
| Report fallback and out-of-order 03/system build | Bodies moved to owner workflow; source-of-truth design accepted. Dead fallback and live-card failures owned by 03A. |
| Ports before OI-21, map/outbox-class/gates wiring | Later owner ruling keeps ports; doccheck checks maps/headers/classes. Tool execution after publication still failed F2/F3 despite GREEN. |
| Imagegen unavailable in 03; composite candidates and final gameplay images | Historical candidates are not gameplay evidence. Final owner-selected preview and annotated captures inspected visually here; no generated gameplay claim. |
| Ignore filter/gallery/editor round-trip guards | Existing guards pass on the mixed tree; gallery is excluded from packing and accessible to upload fields. Actual launch membership remains F1. |
| Credits, hub retained Tripo geometry, missing residue parity | General credit grounded in prior art; F6/ OI-49 remain. Do not call under-deck mesh wholly original. |
| Default gamepatch pair, BuildMenu mouse-leave omission, noisy sigcheck | Explicit historic pair and full diff preserved; actual current pack hashes rechecked. No signature-only semantic PASS. |
| Shared Arboretum partial staging and held package scope | `0579b78` excludes held hunks; `0ff4a85` later tracks D19 files; owner excludes launch. F1 captures the resulting packaging gap. |
| Exact Save B class/upgrade tokens, decoder marker failure, source-path typo | Receipt hashes hold; corrected archived source path/body is used. Tokens are not graph edges, candidate ids not registrations; owner accepted UNKNOWN. |
| Plan AccountStorage, weak transition predicate, absence gate, paused save, modifier reconstruction, optional refresh | Proposed 02 plan was corrected upstream, then owner closed its accepted cells and scratched the rest. No claim the unimplemented kit bindings ran. |
| Wrong native-menu instruction and inferred SaveGameExt change | Explicit cross-process Override/native filename route is known; extension-change inference withdrawn. No save-menu discovery claim or shared-kit reader work. |
| Train station map, earlier removal errors, open log, stock/inheritance distinction | All retained in the primary-evidence result above; no whole-process clean or train recovery claim. |
| D14 residue / scoped B3/B5/B6 | Current D14 disposition is owned and remains open; no conversion of skipped or struck cases to passes. |
| Tool sync deviations and donor parked restoration | Existing knowledge-sync owner retained; publish-day §7 requires current-site reconciliation, F7. No silent donor edits. |
| Same execution/authoring model | Transcript recorded; different-model whole-chain acceptance remains owed after corrections. No refusal to perform this review and no false independence claim. |

## Local checks and deployment boundary

Initial working-tree gates at audit HEAD: doccheck GREEN; upload preflight
**43 checked, 0 FAIL, 1 UNCHECKABLE** (Paradox login); store parity's current
pre-publication branch **6 rows, 0 FAIL** (including one INFO). These do not
exercise publication, and the independent controls found failures above.

Pack prediction: **78 files, 102626941 raw bytes** = **575462 non-asset +
102051479 asset**; members reconcile as root 4 + Code 21 + Data 3 + Entities 5 +
Fallbacks 17 + Materials 4 + Meshes 5 + Textures 17 + UI 2. Command/filter:
`python tools/pack_predict.py .`, entire emitted included list and top-directory
buckets; `upload_preflight.py` supplies asset/non-asset split. This is the mixed
working tree, not compressed size and not the accepted launch package.

`python tools/paradox_card.py --check` finds the expected lede and section
headings. Preview and the owner's contact sheet were visually reviewed; the
selected annotated captures support their scoped callouts. No artwork changed.
`TagGameplay` and `TagBuildings` are the current metadata tags; no portal
approval/certification was inferred from them.

Site HEAD `d87c7005484b5736829e3db1a94999370d46c498`, clean status before/after:
`python -m mkdocs build --strict --site-dir B:/Dev/SMR/SMR-OptInPack/scratch/final-launch-site`
exited 0, no strict-build error. Material printed its generic MkDocs 2.0 advisory;
this is not a site validation failure. An HTMLParser read of the built Opt-In,
index/install/FAQ/modders/report pages checked **287 local link occurrences**,
reconciled to `site_links.json`'s complete members, with no missing files/fragments;
the intended module anchors are present. This is structural render/link checking,
not a browser screenshot or an external form submission. Report backend unchanged.

Fresh public GETs of GitHub's deployments API and each candidate's status endpoint
identify latest successful Pages deployment `e541ca50ffa099e87ef5dd5899a5f2a018e664cc`
(deployment 6716860015); the independent Opt-In public URL returns HTTP 404.
Thus the local site addition is still undeployed. The web reader could not fetch
these URLs; Python urllib's public requests supplied the reading. No workflow was
run. Read command: `/repos/catt144/SMR-CommunityMods/deployments?environment=github-pages&per_page=5`,
then each `statuses_url?per_page=3`, and
`https://catt144.github.io/SMR-CommunityMods/opt-in/`. This observation is dated to
this audit, not a cached future deployment claim.

Final gate receipt is `archive/final_launch_audit_20261003/final_checks.json`:
all listed commands exited 0, including read-only sync (whose exit 0 does not
clear its candidate rows). The original doccheck subprocess capture used UTF-8
replacement decoding for its platform-encoded text; decorative glyphs are lossy,
while the ASCII verdicts, counts and warning paths remain readable. A later
strict-UTF-8 doccheck receipt at commit preserves the full text.
Sync still reports undeclared preflight divergence and doccheck RECHECK, plus
new donor desk-tool candidates and local `annotate_screenshots.py`; the existing
knowledge-sync job owns applicability decisions. None is silently ported here.
Final status was re-read in all involved repos: the site/rescue trees remain
clean; donor dirty paths remain its existing checklist/report work. This audit's
commit excludes `metadata.lua`, `items.lua` and `RELEASE_OUTBOX.md` entirely.
Owner actions
remaining are OI-49, upload-time accounts/platforms, both actual store uploads,
formatting and eventual separate site deployment. None was performed here.

## Close

Audit/correction handoff committed as `c1d8c7e`. The following records-only commit
pins that result in 03/04 and completes this work list. Handoff byte measurements
use `archive/final_launch_audit_20261003/handoff_sizes.py` and its receipt against
the startup HEAD: **33771 → 42520 bytes, +8749**, reconciled to the complete
member list. No handoff is removed.

All audit findings are either corrected in local records or assigned to the live
03A/03/04 passages above; no owner decision is duplicated and no obligation is
dropped. Existing frozen-row, archive-EOL and shared-TestKit warnings remain
report-only; complete command output is retained in the gate receipts.

Next owner kickoff: `task docs/agent/prompts/Launch_Prep/03A_RELEASE_CORRECTIONS_high.md`.
Then resume 03 and independently re-run 04 on changed inputs and unresolved
findings. The permanent release prompt is not yet the next kickoff.
