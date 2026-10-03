# Release — prepare, hold for the owner, then close

Run this prompt when the owner asks to publish this mod for the first time or to ship
an update. It owns the whole release lifecycle, including the work after the owner's
upload. A release is not finished at the handoff.

> ⛔ The agent never packs, uploads, opens the Mod Editor, or calls a portal API.
> The owner performs every portal action through `docs/UPLOAD_WORKFLOW.md`.

Built 2026-10-03 on the fix pack's release prompt (owner standardisation, 2026-09-17),
with a first-publish path this mod needs and the fix pack never did. Use `doc-editing`
and `smr-bug-library`; `CLAUDE.md`, `docs/agent/WORKFLOW.md` and `FIX_POLICY.md` bind.

## Release rails

- Never hand-set `metadata.lua`'s `version`, `version_major` or `version_minor`. The
  initial 1.0 is already in the file (owner, 2026-08-14); the editor's upload save owns
  `version` from the first upload on, and a hand-set value can double-bump. Other
  deliberate edits to `metadata.lua`, such as the store body (regenerated from
  `docs/UPLOAD_WORKFLOW.md` §3 by `python tools/store_parity.py --write-metadata`),
  `last_changes`, the gated code list and the art fields, are ordinary work.
- Never copy, move or reuse a `fixpack-*` tag or a fix-pack portal id. This mod's mark
  is an annotated `optin-v<major.minor.version>` tag on the commit whose bytes were
  packed, created only after the owner confirms the upload (`POST_UPLOAD_CLOSE.md`).
- Ids are read, never typed: `pdx_id`, `steam_id` and their version fields arrive in the
  editor's writeback. Before the first confirmed upload every id is a named gap.
- A zero-hit verification is a failure. Record the expected presence count before an
  edit and require the post-edit command to find the expected members.
- Do not track, report or ask for the version number either store page shows (owner,
  2026-09-23). `metadata.lua`'s `version` is the only version this project tracks, and
  the newest `Update:` entry on the Steam changelog
  (`steamcommunity.com/sharedfiles/filedetails/changelog/<steam_id>`, id from the
  writeback) confirms an upload happened. Before the first Steam upload there is no
  changelog to read; the owner's confirmation and the writeback are the receipt.
- Never claim "ready to publish" as a verdict. The handoff says "ready to upload" and
  lists what the owner still does.

## 0 · Orient and expose the full lifecycle

1. Run `git log --oneline -10`, `git pull`, and `git status --short`; the same in
   `B:/Dev/SMR/SMR-CommunityMods`. Never stash or commit another seat's hunks.
2. Read `docs/agent/STATE.md`, `RELEASE_OUTBOX.md`, `docs/agent/support/RELEASE_SURFACES.md`,
   `POST_UPLOAD_CLOSE.md`, `LIVE_SITE_READ.md` and `docs/UPLOAD_WORKFLOW.md`.
3. Start a live five-item list: derive batch; prepare and verify surfaces; hand off and
   HOLD; verify and close after upload; clear records and finish. Exactly one unfinished
   item is in progress.
4. Run `python tools/doccheck.py --emit-counts`; carry no stored count.
5. **Is a release already half done?** Any of these means close-out is owed and §4 runs
   before anything new: STATE carries an `UPLOAD OWED` marker; `git diff -- metadata.lua
   items.lua` shows writeback fields (`pdx_id`, `steam_id`, `version` moved) or zero
   leading comment lines; the outbox's Pending is non-empty while STATE says the
   release is live; a `steam_id` exists and its changelog is newer than the outbox's
   `Last released` line. A fresh session resolves that release through §4; it never
   prepares a second one on top.

## 1 · Derive the batch and prepare every required surface

The batch is exactly the filled `### Pending` entries in `RELEASE_OUTBOX.md`. Use
`docs/agent/support/RELEASE_SURFACES.md` to update the player-facing surfaces, rewrite
this version's change note, regenerate `metadata.lua`'s body and run the gates. There is
no standing reply, comment, discussion or tracker step.

### 1a · First publish: the preconditions table

The first run of this prompt also checks these, and stops at the first that is not
met, naming it in the handoff rather than working around it:

| precondition | where it is proven |
|---|---|
| Shipping evidence accepted: every emitted module has entry status matching its attendance, both §8 configurations recorded with the released fix-pack version (or the owner's waiver), final `Lua.fpk` targets verified on the command-read build | `Launch_Prep/01`'s ledger and `02`'s results, then `04`'s verdict; `docs/agent/bugs/INDEX.md` |
| Save exit and residual disclosure agree with the measured residual set; OI-45's demolish-first note is on both store bodies and the site | `FIX_POLICY` §3/§3a, `01`'s residue work, `docs/UPLOAD_WORKFLOW.md` §3, `content/opt-in/index.md` |
| Credits and provenance in player text where owed | `01` work item 5; `LICENSE` |
| Preview `image` and gallery `screenshot1..5` wired from the owner's selection; `python tools/upload_preflight.py` zero FAIL | OI-12; the preflight run |
| Owner's listing and platform facts recorded (existing drafts or none; platforms; approval step) | OI-44; `docs/UPLOAD_WORKFLOW.md` §0 |
| `python tools/store_parity.py` 5/5; `python tools/doccheck.py` GREEN; `python -m mkdocs build --strict` clean in the site repo; site Opt-In pages committed | the gate runs |
| Publish-day donor handoff prepared (parked fix-pack references, routed to the fix pack's own release, never restored early) | `reports/STORE_AND_SITE_20261003.md` §7 |

Commit the prepared release words with exact pathspecs. Do not touch version fields. Do
not continue while doccheck, `store_parity.py` or `upload_preflight.py` reports a failure.

## 2 · Hand off, then HOLD

Tell the owner "ready to upload", state the batch and the change note, name every
owner-only step that remains (first publish: §0 of the owner file), and point to
`docs/UPLOAD_WORKFLOW.md`. The owner uploads Paradox first and Steam second, restores
the store formatting, then publishes the site.

Before yielding:

1. Say exactly how to resume: **"When both stores show the mod, say 'uploaded' and I
   will read the ids and version from the writeback, restore the comments, compare the
   downloaded package, update STATE and clear the outbox."**
2. Replace STATE's NEXT line with one resumable marker:
   `v<major.minor> UPLOAD OWED (first publish | update) → then release_prompt.md §4 close-out`.
3. Leave Pending intact, touch no version field, create no tag.

This is a pause, not completion. Wait for the owner's confirmation.

## 3 · Owner upload

The owner follows `docs/UPLOAD_WORKFLOW.md`. The receipt is only: anything that looked
wrong on either store, whether the site published, and, on a first publish, the two
store links and what Paradox said about platforms or approval. Description auto-fill
and the formatting paste are settled facts, not questions, and neither is a store
page's version number (Release rails).

**Partial upload.** If the owner reports Paradox done and Steam not (or the reverse),
record it in STATE's marker (`PARADOX DONE, STEAM OWED`), keep Pending intact, run §4
only for the writeback preservation (comments must be restored before any other commit
touches `metadata.lua` or `items.lua`), and hold again. The owner finishes the second
store with the same packed file; a forced editor save in between bumps `version`, which
the close-out records as two version values for one release rather than hiding it.

## 4 · Resume, often in a fresh session

After the owner confirms the upload, read `docs/agent/support/POST_UPLOAD_CLOSE.md` and
execute it. In a fresh session, run §0's Git commands and read the tree, outbox and
owner receipt again. Verify the upload from the writeback, the downloaded package and
the receipts; do not trust a handoff claim by itself.

The Mod Editor writeback strips the comments from `metadata.lua` and `items.lua`. Until
the close procedure restores them while preserving the new ids and version fields, no
session may commit either file for another reason.

## 5 · Clear the outbox only after confirmation

Only after the owner confirms the upload and §4 verifies it, append every Pending entry
to `docs/archive/RELEASE_HISTORY.md` under `### Released in v<major.minor.version>
(date)`, set the outbox's `Last released` line, and leave Pending empty. The outbox holds
only what has not shipped; this prevents a change shipping twice. Never clear the outbox
at "ready to upload".

## 6 · Finish

Re-emit counts, finish the release records (`STORE_CARD_LIVE.md` with the as-published
state and ids, the `optin-v…` tag, the site deployment read through `LIVE_SITE_READ.md`),
remove the STATE marker, run doccheck, and commit the close-out with exact paths. On the
first publish, hand the donor publish-day job to the fix pack's own release prompt as a
written ask on that repo's checklist; do not edit the fix pack. Report what the Steam
change note (or, before Steam exists, the writeback and receipt) confirms, the site
status and that Pending is empty. Do not claim a release step the owner did not confirm.
