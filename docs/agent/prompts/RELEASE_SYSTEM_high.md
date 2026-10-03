# Build the Opt-In release system — first publish and later updates

**Fire first:** `task docs/agent/prompts/RELEASE_SYSTEM_high.md`. May run now; publication waits
for train brief 35 and `Launch_Prep/`. Reasoning: high, because donor authority and this content
mod's first-publish lifecycle differ. Revised 2026-10-02 at `63424af` by the launch audit.

## Authority and outcome

Owner, 2026-09-18: “this repo needs its own release system and prompt. The public site through
github will be shared but it was pre designed that way so that shouldn't be to much of a prompt.”
Owner, 2026-09-17: standardise on the fix pack's names, rules and workflow where the function is
the same; only product-specific content differs. Owner, 2026-10-02: full launch preparation,
including store pages, shared site and the release workflow/prompt. Those decisions are settled.

Build this repo's release system using the current donor at `B:/Dev/SMR/SMR-BugFixPack`, read-only.
Done means an agent can prepare a first publish or an update, hand off to the owner, resume after
upload, preserve editor writeback and close all records without inventing a store id or a receipt.
The owner's UPLOAD_WORKFLOW stays plain and in the donor's shape. Delegate implementation and
prose choices within that outcome; record calls in the commit.

## Work and evidence

Start `git log --oneline -5`, `git pull`, `git status --short`; read
`docs/agent/reports/LAUNCH_PREP_AUDIT_20261002.md`. Its evidence table supplies commands and
falsifiers. Recheck donor HEAD and relevant changed inputs. Maintain a live work list in the
session tool or a report, one commit-and-verify unit in progress.

SOURCE at audit HEAD: metadata contains approved description/summary, stale `last_changes`,
patch version 0, true `optional_mod`, and train assets. It is not the 2026-09-18 module set.
MEASURED: `python tools/upload_preflight.py` fails only for missing preview at `63424af`;
its asset checks pass. Re-run rather than assuming that stays the only failure.

Create these donor-named files and wire their real consumers:

- `docs/UPLOAD_WORKFLOW.md`: owner procedure and maintained paste blocks. Mark absent art,
  ids, console receipts and not-yet-produced card text as preparation gaps, never live copy.
- `docs/agent/prompts/perma/release_prompt.md` and `RELEASE_OUTBOX.md`: first-publish Pending
  inventory, later player-facing deltas, owner hold/resume and confirmed-upload-only draining.
- `docs/archive/RELEASE_HISTORY.md`: append-only history, without invented releases.
- `docs/agent/support/RELEASE_SURFACES.md`, `POST_UPLOAD_CLOSE.md`, `LIVE_SITE_READ.md`:
  product-specific surfaces, writeback/comment recovery, archive comparison, tags and actual
  deployed-source/live-page verification. The last name is the donor's site protocol.

Wire ROOT expectations, required rule headers, outbox class/prompt map, docs/support maps,
WORKFLOW Release/Release marking and applicable `sync_from_fixpack.py` exemptions. Retain donor
names; if no donor name exists for a required standing function, report that gap rather than
coining a parallel system. Define the pre-publication state of `STORE_CARD_LIVE.md`; chain 03
fills actual store copy. Do not create a contradictory byte-parity rule for empty drafts.

The procedure must cover:

- First creation on Paradox then Steam: distinct ids, editor saves/writeback, account/visibility
  checks, own platform/console approval, gallery and styling; later updates use those ids.
  Preserve settled description auto-fill and formatting loss; no per-release repeat question.
- Initial major/minor are already decided. Reconcile WORKFLOW's old agent major/minor edit step
  with the donor's current editor-owned version rule under standardisation authority. Preserve
  writeback; never copy a `fixpack-*` tag or reset a version to make portals agree.
- Exact metadata/items pre-upload baseline, comment restoration after the editor, actual packed
  bytes versus serializer changes for each portal, annotated Opt-In release tag and downloaded
  `pack_list.py` reconciliation. A store counter is not an upload receipt.
- Local shipping-evidence ledger, both configurations with released fix-pack version, final
  `Lua.fpk` verification, save exit/rescue, credits, own art/listings/certification and preflight.
  Replace WORKFLOW's stale whole-pack 5 MB statement with the actual OI-18 asset-aware guard.
- The shared site's module pages, nav, README mods row and shared install/FAQ/reporting text.
  Read sibling status/HEAD before writing and again before commit; never absorb others' dirty
  hunks. Site deployment is the owner's act after store pages. Chain 03 builds these surfaces.
- Publish-day routing of donor `PARKED_OPTIN_REFERENCES.md` against current facts, not verbatim
  restoration. Donor metadata/store changes require that repo's release, not this upload.
- HOLD with Pending intact and a resumable marker; after owner confirmation verify writeback,
  actual Steam change note, receipts/site state, restore comments, archive Pending, close records.

OI-21's tool-location choice and OI-44's first-listing/console facts may remain explicit gaps;
they do not block the rest of the procedure. Port no tools without OI-21's ruling.

## Scope and stops

In: local release documents, maps, WORKFLOW release sections and required mechanical gate/sync
wiring. Out: shipping code, metadata/items, store prose/art, sibling writes, game/Mod Editor,
portal API calls and publishing.

1. A copied procedure requires crossing FIX_POLICY's persisted-name or executable-reference
   bans: report the exact conflict; do not silently adapt it into runtime code.
2. An owner-only fact/decision or absent donor function name prevents a complete step: leave a
   named gap, file a question only if it needs the owner, and finish independent work.
3. A conflict in owner authority cannot be resolved by scope/date: preserve both and route the
   narrow decision; do not rewrite authority as implementation preference.

## Verify and hand off

Use doc-editing, prompt-authoring, rule-placement, smr-bug-library; house rules CLAUDE,
process WORKFLOW, code/release rules FIX_POLICY. Read destination headers. Run doccheck GREEN
and upload preflight, recording remaining failures without calling the release ready. Review
first-creation, partial-upload and fresh-session-resume paths as worker and owner. Copy no donor
counts or ids. Audit on a different owner-selected model in Launch_Prep's terminal link before
acceptance. Put result commits/gaps and every drift instance in upstream notes of 01 and 04.

Recheck shared paths/log/status, commit exact paths and push per WORKFLOW. Delete this one-off
and its map row only when built; update sync pointers that named this live brief in that change.
Report “release machinery built; these launch inputs remain”, never “ready to publish”.

## Notes from upstream

Launch_Prep/03 ran before this brief (owner fire, 2026-10-03). Lift, do not redo:

- **Maintained store copies** are in `docs/agent/reports/STORE_AND_SITE_20261003.md` §3 under the
  donor's exact headings (`#### 📋 Paradox Mods — description (plain text, paste as-is)`,
  `#### 📋 Steam Workshop — description (BBCode, paste as-is)`, `#### 📋 Short summary`,
  `#### 📋 Change note`). Move them into `docs/UPLOAD_WORKFLOW.md` §3; `tools/store_parity.py`
  then reads the default source and its fallback note disappears. `STORE_CARD_LIVE.md`'s
  pre-publication state can point at those blocks rather than duplicate them.
- `metadata.lua` `description`/`last_changes` are generated by `python tools/store_parity.py
  --write-metadata`; make that the rule in RELEASE_SURFACES §3 in place of the donor's prose
  byte-match duty, and wire `store_parity.py` into the release gates beside preflight.
- **First-publish steps** (OI-44 listing check, platform/console approval, Paradox then Steam,
  gallery/styling, writeback with post-creation id fill, downloaded-archive comparison, site last)
  are drafted in the report §6 for the owner file.
- The outbox's first Pending entry is the report's change note; nothing earlier shipped.
- Tools ported (OI-21 stop 1): `paradox_card.py --source`, `store_screenshots.py` (drop folder
  `SMR-ScreenCaptures/optin_store`, five-shot map), `store_parity.py`; grouped under "Launch" in
  `tools/doccheck.py` `TOOL_GROUPS`; `*/store_screenshots/*` is in `ignore_files` and
  `pack_predict.IGNORE`.
- Publish-day donor handoff (parked references reconciled) is the report §7; route it through
  the fix pack's `release_prompt.md` at first publication, never earlier.
