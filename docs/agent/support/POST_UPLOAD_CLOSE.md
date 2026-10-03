# Closing a confirmed upload

This is the close procedure consumed by `docs/agent/prompts/perma/release_prompt.md` §4.
It is not a prompt and it never uploads, repacks, opens the Mod Editor or calls a portal.
Adapted 2026-10-03 from the fix pack's procedure; the first-publish additions are the id
writeback, the store-card fill, the `optin-v…` tag and the donor publish-day handoff.

## Preconditions and receipts

Do not begin until the owner confirms the upload. The receipt asks only:

1. anything that looked wrong on either store;
2. whether the site published;
3. on a first publish, the two store page links and what Paradox said about platforms
   or approval.

Description auto-fill and the formatting paste are settled and are not asked per
release. Neither is a store page's version number (owner, 2026-09-23). `metadata.lua`'s
`version` is the only version tracked; the Steam changelog confirms an upload once a
`steam_id` exists.

## 1 · Verify from the tree

In a fresh session, run `git log --oneline -10`, `git pull`, and `git status --short`,
then read STATE and the outbox. Inspect:

```text
git diff -- metadata.lua items.lua
```

The writeback exposes the new fields: `version` (bumped by the upload save), `pdx_id`
and `pdx_version` on a Paradox upload, `steam_id` on a Steam upload, and possibly
`image`/screenshot paths rewritten. Compare them with STATE's marker and the outbox's
`Last released` line. A first publish shows ids that did not exist before; an update
shows the same ids and a moved `version`. A handoff sentence alone is not proof.

Count leading comment lines in both files before any commit. Zero means the editor
serializer stripped them and restoration is owed. A zero-hit command never proves the
comments are safe.

**Partial upload.** One id present and the other absent means one store is done. Record
it in STATE's marker, finish §2 for the files, and stop; the rest of this procedure runs
when the second store is confirmed.

## 2 · Preserve writeback, restore comments

Keep the upload's actual `version`, `pdx_id`, `pdx_version`, `steam_id` and every other
serializer writeback field. Never normalize or hand-set a version. Restore the
hand-written comments from the pre-upload tree in the same commit, in both
`metadata.lua` and `items.lua`, and re-run `python tools/store_parity.py`: the editor
re-serializes the description string, and the generated body must still equal the
`UPLOAD_WORKFLOW.md` §3 block byte for byte (if the serializer changed escaping, the
block is the source and `--write-metadata` restores the string).

Until this restoration is complete, no session may commit either file for another
reason. A commit naming a path takes the stripped working-tree copy and can bury the
commentary. Review the whole diff after restoration.

## 3 · Compare the downloaded package

Once a store serves the mod, run `python tools/pack_list.py <downloaded ModContent.fpk>
--tree .` against the tree at the packed commit and record members and bytes beside the
pre-upload `python tools/pack_predict.py .` figures. A difference is a finding, not a
note: name every file that differs. Do this per portal if the files differ.

## 4 · Finish the records

- `docs/agent/reports/STORE_CARD_LIVE.md`: record the as-published state per portal
  (date, `version` from the writeback, `pdx_id` / `steam_id`, the two page links from the
  receipt, the platform/approval words), and copy the two body blocks as published
  under their `#### 📋` headings so `store_parity.py` checks the card from then on.
- Tag: `git tag -a optin-v<major.minor.version> <packed-sha> -m "<store change note>"`
  and push the tag. The sha is the commit whose bytes were packed, not HEAD if records
  moved since. Never a `fixpack-*` name.
- Update STATE with what is live and remove the `UPLOAD OWED` marker.
- Append each outbox Pending entry to `docs/archive/RELEASE_HISTORY.md` under
  `### Released in v<major.minor.version> (date)`, set the outbox's `Last released`
  line, and leave Pending empty. Do this only after owner confirmation.
- Site: read the live deployment through `LIVE_SITE_READ.md`; if the owner has not
  published, record "site deployment owed" rather than inferring it from the commit.
- **First publish only:** the fix pack's parked opt-in references
  (`reports/STORE_AND_SITE_20261003.md` §7) become that repo's job now; file one item on
  the fix pack's `docs/PLAYTEST_CHECKLIST.md` in its format naming the live links and
  the §7 dispositions. Do not edit the fix pack's surfaces or metadata.
- Update any entry status whose existing policy is satisfied; do not infer play evidence
  from publication.
- Append the release leg to `docs/archive/SESSION_LOG.md` without rewriting older text.
- Re-run `python tools/doccheck.py --emit-counts`, then `python tools/doccheck.py`.
  Report counts only from that run and copy any warning verbatim.

Commit the writeback, restored comments and record changes with exact pathspecs. Report
what the Steam change note (or the receipt and writeback, before Steam exists) confirms,
the site status and the empty Pending ledger. Do not claim a portal result the owner did
not confirm.
