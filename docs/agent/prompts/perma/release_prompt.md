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
- **One batch, one launch tree.** `python tools/release_batch.py` pins a batch in
  `docs/agent/support/RELEASE_BATCH.json`: its base commit, its exact Pending entries, a
  hashed launch tree exported from that commit, each portal's package snapshot and owner
  receipt, and the close steps. The owner uploads from the launch tree
  (`B:\Dev\SMR\SMR-OptInPack-launch`), never from the working repo, because the editor
  packs every file under the mod folder: uncommitted work, a peer's hunks and held modules
  would ship. Read the tool's header before the first release.
- Never copy, move or reuse a `fixpack-*` tag or a fix-pack portal id. This mod's mark
  is an annotated `optin-v<major.minor.version>` tag on the batch's **base commit**,
  created only after the owner confirms both uploads. The tag names the source the launch
  tree was exported from. It does not claim that commit's bytes equal a package: each
  package's identity is its snapshot hash in the batch record.
- Ids are read, never typed: `pdx_id`, `steam_id` and their version fields arrive in the
  editor's writeback. Before the first confirmed upload every id is a named gap. An id
  identifies a listing. It is not evidence that this batch was uploaded there.
- A zero-hit verification is a failure. Record the expected presence count before an
  edit and require the post-edit command to find the expected members.
- Do not track, report or ask for the version number either store page shows (owner,
  2026-09-23). `metadata.lua`'s `version` is the only version this project tracks, and
  the newest `Update:` entry on the Steam changelog
  (`steamcommunity.com/sharedfiles/filedetails/changelog/<steam_id>`, id from the
  writeback) confirms an upload happened. Before the first Steam upload there is no
  changelog to read; the owner's confirmation and the writeback are the receipt.
- Description auto-fill and the formatting paste are settled (owner, 2026-09-12). No
  listing of this mod exists before the first upload (owner, 2026-10-03). None of these
  is asked again.
- Never claim "ready to publish" as a verdict. The handoff says "ready to upload" and
  lists what the owner still does.

## 0 · Orient: read the release state, do not infer it

1. Run `git log --oneline -10`, `git pull`, and `git status --short`; the same in
   `B:/Dev/SMR/SMR-CommunityMods`. Never stash or commit another seat's hunks.
2. Run `python tools/release_batch.py status` and act on what it prints:

   | state | meaning | go to |
   |---|---|---|
   | `IDLE` | nothing staged, nothing open | stop; there is nothing to release |
   | `NEW_BATCH` | Pending entries and no open batch. This is true after a live release too: later Pending work is a new batch, never an unfinished upload | §1 |
   | `PREPARED` | a batch is pinned and nothing was uploaded | §2's handoff, after `verify` |
   | `UPLOADING` | upload activity with no confirmed portal: an allocated `steam_id`, a Paradox writeback, a snapshot, or a failed receipt | §3 |
   | `PARTIAL` | exactly one portal has the owner's receipt | §3 |
   | `CLOSE_OWED` | both portals confirmed; the listed close steps remain | §4 |

3. Read `RELEASE_OUTBOX.md`, `docs/agent/support/RELEASE_SURFACES.md`,
   `POST_UPLOAD_CLOSE.md`, `LIVE_SITE_READ.md` and `docs/UPLOAD_WORKFLOW.md`.
4. Start a live five-item list: derive batch; prepare and verify surfaces; hand off and
   HOLD; verify and close after upload; clear records and finish. Exactly one unfinished
   item is in progress.
5. Run `python tools/doccheck.py --emit-counts`; carry no stored count.

## 1 · Derive the batch and prepare every required surface

The batch is the committed `### Pending` entries in `RELEASE_OUTBOX.md` that this release
carries. An entry whose work is held out of this release is named with `--hold` at
`begin` and stays Pending. Use `docs/agent/support/RELEASE_SURFACES.md` to update the
player-facing surfaces, rewrite this version's change note, regenerate `metadata.lua`'s
body and run the gates. There is no standing reply, comment, discussion or tracker step.

### 1a · First publish: the preconditions table

The first run of this prompt also checks these, and stops at the first that is not
met, naming it in the handoff rather than working around it:

| precondition | where it is proven |
|---|---|
| Shipping evidence accepted: every emitted module has entry status matching its attendance, both §8 configurations recorded with the released fix-pack version (or the owner's waiver), final `Lua.fpk` targets verified on the command-read build | `reports/SHIP_EVIDENCE_20261003.md`, the final audit's accepted verdict, `docs/agent/bugs/INDEX.md` |
| Save exit and residual disclosure agree with the measured residual set; OI-45's demolish-first note is on both store bodies and the site | `FIX_POLICY` §3/§3a, `reports/SHIP_RESIDUAL_20261003.md`, `docs/UPLOAD_WORKFLOW.md` §3, `content/opt-in/index.md` |
| Credits and provenance in player text where owed | `reports/SHIP_EVIDENCE_20261003.md`; `LICENSE` |
| Preview `image` and gallery `screenshot1..5` wired from the owner's selection | `reports/STORE_SCREENSHOTS_20261003.md`; the preflight run |
| `python tools/release_selftest.py`, `python tools/store_parity.py`, `python tools/upload_preflight.py <launch tree>` and `python tools/doccheck.py` report zero FAIL; `python -m mkdocs build --strict` clean in the site repo; site Opt-In pages committed | the gate runs |
| Publish-day donor handoff prepared (parked fix-pack references, routed to the fix pack's own release, never restored early) | `reports/STORE_AND_SITE_20261003.md` §7 |

The platform choice and any approval step on Paradox Mods are the owner's actions at
upload (`docs/UPLOAD_WORKFLOW.md` §0). They are reported afterwards, not required before
the handoff.

Commit the prepared release words with exact pathspecs. Do not touch version fields. Do
not continue while doccheck, `store_parity.py` or `upload_preflight.py` reports a failure.

## 2 · Pin the batch, hand off, then HOLD

1. `python tools/release_batch.py begin` (add `--hold "<heading text>"` per held entry).
   It refuses while a batch is open, and while a `HELD_OUT` row in the tool names a path
   the base commit no longer tracks: remove a stale row in the same commit that moved the
   work. Commit `docs/agent/support/RELEASE_BATCH.json`.
2. `python tools/release_batch.py verify` and, on the launch tree it names,
   `python tools/upload_preflight.py <launch tree>`, `python tools/pack_predict.py <launch tree>`
   and `python tools/store_parity.py --metadata <launch tree>/metadata.lua`. Reconcile the
   registered modules, option items, Data templates and generated files that `verify`
   prints against the batch's entries. These runs, on this tree, are the release gates;
   a GREEN on the working repo is not.
3. Tell the owner "ready to upload", state the batch and the change note, name every
   owner-only step that remains (first publish: §0 of the owner file), and point to
   `docs/UPLOAD_WORKFLOW.md`.
4. Say exactly how to resume: **"Say 'paradox done' after the Paradox upload and 'stores
   done' after Steam. I keep each package, read the ids and version from the writeback,
   and put the real store links on the site before you publish it."**

Leave Pending intact, touch no version field, create no tag. The batch record is the
resumable marker; STATE carries no release marker. This is a pause, not completion.

## 3 · Owner upload, one portal at a time

The owner follows `docs/UPLOAD_WORKFLOW.md`: Paradox first, Steam second. Each upload
builds its own package and deletes the previous one, so per portal, as the owner reports
it and before the next upload starts:

1. `python tools/release_batch.py snapshot <portal>` keeps the package and the editor's
   `metadata.lua`/`items.lua`. If the package is already gone, record that limit in the
   batch receipt; never claim an exact package for that portal.
2. `python tools/release_batch.py receipt <portal> uploaded|failed "<the owner's words>"`.
3. `python tools/release_batch.py status`, and commit the batch record.

The owner's receipt is the upload evidence. A new `steam_id` is not: the game allocates
and saves it before it packs. A Paradox `pdx_id`/`pdx_version` writeback is written only
after the publish call succeeded, by source; record it as that, and still take the receipt.

**Failed or interrupted upload.** Keep the batch and the launch tree as they are: an
allocated id lives only in the launch tree's `metadata.lua` until the close merges it, and
a rebuilt tree would create a second listing. The owner retries from the same tree; the
retry's package is a new snapshot. A forced editor save in between bumps `version`; the
close records the values the snapshots show rather than hiding them.

The receipt after both stores is only: anything that looked wrong on either store, and, on
a first publish, the two store links and what Paradox said about platforms or approval.

## 4 · Close, often in a fresh session

Run §0, then execute `docs/agent/support/POST_UPLOAD_CLOSE.md` from the first close step
`status` lists as owed. Verify from the batch record, the snapshots and the receipts; do
not trust a handoff claim by itself.

The repo's `metadata.lua` and `items.lua` were never opened by the editor, so their
comments are intact; the close copies the writeback fields into them. Until that commit
lands, no session rebuilds or deletes the launch tree.

## 5 · Drain only this batch

`python tools/release_batch.py drain` moves exactly the batch's pinned entries to
`docs/archive/RELEASE_HISTORY.md` under `### Released in v<major.minor.version> (date)`
and sets the outbox's `Last released` line. It refuses until both portals have the owner's
receipt, appends the history section once however often it runs, and leaves every later or
held Pending entry where it is. Never clear the outbox by hand or at "ready to upload".

## 6 · Finish

Finish the release records through `POST_UPLOAD_CLOSE.md` (store card, real store links
on the site and README, the `optin-v…` tag, the site deployment read through
`LIVE_SITE_READ.md`), run `python tools/release_batch.py close`, run doccheck, and commit
with exact paths. On the first publish, hand the donor publish-day job to the fix pack's
own release as one item appended to `B:\Dev\SMR\SMR-BugFixPack\docs\PLAYTEST_CHECKLIST.md`
in that file's format. That item is the only donor write this prompt makes; the fix
pack's surfaces, metadata and store text are not edited. Report what the Steam change
note (or, before Steam exists, the writeback and receipt) confirms, the site status and
which Pending entries remain. Do not claim a release step the owner did not confirm.
