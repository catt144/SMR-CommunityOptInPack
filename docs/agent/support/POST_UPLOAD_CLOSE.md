# Closing a confirmed upload

This is the close procedure consumed by `docs/agent/prompts/perma/release_prompt.md` §4.
It is not a prompt and it never uploads, repacks, opens the Mod Editor or calls a portal.
Adapted 2026-10-03 from the fix pack's procedure; this mod's differences are the pinned
batch and launch tree (`tools/release_batch.py`), the per-portal package snapshots, the
store-links step before the site is published, and the donor publish-day handoff.

Every step is safe to repeat. `python tools/release_batch.py status` lists the close
steps still owed; a fresh session resumes at the first of them.

## Preconditions and receipts

Do not begin until both portals carry the owner's receipt (`status` reads `CLOSE_OWED`).
With one portal confirmed the state is `PARTIAL`: keep the batch, the launch tree and
Pending as they are, and hold. The receipt asks only:

1. anything that looked wrong on either store;
2. on a first publish, the two store page links and what Paradox said about platforms
   or approval.

Description auto-fill and the formatting paste are settled and are not asked per
release. Neither is a store page's version number (owner, 2026-09-23). `metadata.lua`'s
`version` is the only version tracked; the Steam changelog confirms an upload once a
`steam_id` exists.

## 1 · Verify from the batch record

Run `git log --oneline -10`, `git pull`, `git status --short`, then:

```text
python tools/release_batch.py status
python tools/release_batch.py verify
python tools/release_batch.py writeback
```

`verify` must show the launch tree unchanged apart from the editor's `metadata.lua` and
`items.lua`; any other changed, missing or extra file is a finding to resolve before
anything is merged. `writeback` lists each field the editor's copy holds that the repo's
does not: `version` (bumped by the upload save), `pdx_id` and `pdx_version` after a
Paradox publish, `steam_id` after Steam allocated a listing. A first publish shows ids
that did not exist; an update shows the same ids and a moved `version`. A row it marks as
not a writeback field is explained, never copied blind.

## 2 · Merge the writeback into the repo

Copy the editor-owned fields from the launch tree's `metadata.lua` into the repo's
`metadata.lua`, by hand, leaving every comment in place. Never normalise or hand-set a
version: the values are the editor's. Compare the kept `items.lua` snapshot with the
repo's; the editor rewrites it without comments, and only a real item change is carried.
Then run `python tools/store_parity.py`: if the serializer changed the description's
escaping, the `UPLOAD_WORKFLOW.md` §3 block is the source and `--write-metadata` restores
the string.

Commit both files with exact pathspecs (a reviewed partial index if a peer's hunks sit in
either), then `python tools/release_batch.py mark writeback <sha>`.

The repo commit now holds the ids, version and comments. It is not byte-identical to any
uploaded package, and nothing here says it is: Paradox's package was built before its ids
were written, and both packages carry the editor's comment-free files.

## 3 · Compare each package

For each portal's kept snapshot, and for a package downloaded from a store once one
serves the mod:

```text
python tools/pack_list.py <ModContent.fpk> --tree <launch tree> --allow-differ metadata.lua --allow-differ items.lua
```

Exit 0 is the only pass: every member read, names equal, bytes equal apart from the two
declared editor files. For those two, diff the package's copy against the snapshot's
serializer output and name each difference with its cause (ids written after the package
was built; a forced save between the portals). Record members, bytes and the snapshot
hashes beside the pre-upload `python tools/pack_predict.py <launch tree>` figures. A
portal with no snapshot and no download has no package verdict; say so.

## 4 · Store links, then the site

First publish, and whenever a link changes:

1. Read `pdx_id` and `steam_id` from the merged `metadata.lua`; take the page links from
   the owner's receipt and check each carries the id read.
2. Put the real links in the site's Opt-In `## Get it` section
   (`B:\Dev\SMR\SMR-CommunityMods\content\opt-in\index.md`) and this repo's public
   `README.md`. Run `python -m mkdocs build --strict` there. Commit each repo with exact
   pathspecs after reading its status.
3. Hand the owner the separate deployment step (`docs/UPLOAD_WORKFLOW.md` §4). The site
   is not live until they run it; read the result through `LIVE_SITE_READ.md` and record
   "site deployment owed" until then.

## 5 · Finish the records

- `docs/agent/reports/STORE_CARD_LIVE.md`: set `## State: LIVE since <date>`, fill the
  portal and links tables from the writeback and the receipt, and write the two bodies as
  published under `## Current live copy` with their `#### 📋` headings. On a later release
  move the previous bodies into a dated `## ⭐ <date> — <what changed>` section and replace
  the current copy. Then `python tools/store_parity.py --confirm-live` must pass.
- Tag: `git tag -a optin-v<major.minor.version> <base sha> -m "<store change note>"`, the
  base and version being the batch's, the message also naming each portal's snapshot
  sha256. Push the tag, then `python tools/release_batch.py mark tag <name>`. Never a
  `fixpack-*` name.
- `python tools/release_batch.py drain` (release prompt §5).
- Update STATE with what is live.
- **First publish only:** the fix pack's parked opt-in references
  (`reports/STORE_AND_SITE_20261003.md` §7) become that repo's job now. Append one item
  to `B:\Dev\SMR\SMR-BugFixPack\docs\PLAYTEST_CHECKLIST.md` in its format, naming the live
  links and the §7 dispositions, after reading that repo's status. That item is the only
  donor write; its surfaces, metadata and store text are not edited.
- Update any entry status whose existing policy is satisfied; do not infer play evidence
  from publication.
- Append the release leg to `docs/archive/SESSION_LOG.md` without rewriting older text.
- `python tools/release_batch.py close`, then `python tools/doccheck.py --emit-counts` and
  `python tools/doccheck.py`. Report counts only from that run and copy any warning
  verbatim.

Commit with exact pathspecs. Report what the Steam change note (or the receipt and
writeback, before Steam exists) confirms, each package verdict or its stated limit, the
site status and which Pending entries remain. Do not claim a portal result the owner did
not confirm.
