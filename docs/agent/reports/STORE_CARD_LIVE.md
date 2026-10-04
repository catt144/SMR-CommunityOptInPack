# Store card — what is live on each portal

The record of the published store pages, kept by
`docs/agent/support/POST_UPLOAD_CLOSE.md` §4 after each owner-confirmed upload. The
**source** of the store body is `docs/UPLOAD_WORKFLOW.md` §3; `metadata.lua` is generated
from it (`python tools/store_parity.py --write-metadata`). This file never leads: it
records what the portals were given.

## State: PRE-PUBLICATION (2026-10-03)

**Nothing is live.** The mod has never been uploaded. There is no Paradox Mods id, no
Steam Workshop id, no page link, no platform approval receipt and no published body.
Until the first confirmed upload this file carries no copy of the body on purpose
(RELEASE_SYSTEM's authority: no byte-parity rule on an empty draft), so
`store_parity.py` checks the two generated copies and that this card holds no body.

| portal | id | page | version live | platforms / approval | body as published |
|---|---|---|---|---|---|
| Paradox Mods | none yet (read from `pdx_id` after the upload) | none yet | none | owner's choice at upload (OI-44) | none |
| Steam Workshop | none yet (read from `steam_id` after the upload) | none yet | none | PC | none |

**Prepared, not live:** the body blocks in `docs/UPLOAD_WORKFLOW.md` §3 (title, short
summary, Paradox plain text, Steam BBCode, first-release change note), the site section
`content/opt-in/` at site commit `d87c700` (undeployed), the public `README.md`.

## Markup, per portal

- **Paradox Mods** stores the description as HTML. The auto-fill arrives as plain text
  without headings or line breaks; `python tools/paradox_card.py` renders the §3 block
  (first line as the heading, ALL-CAPS lines bold, one paragraph per line, URLs linked)
  for a Ctrl+A / Ctrl+C paste. Unverified until the first upload: whether the server
  truncates a body of this length. The fix pack's longer body was accepted whole.
- **Steam Workshop** renders BBCode: `[h2]`, `[b]`, `[i]`, `[list]`/`[olist]` with `[*]`,
  `[url=…]`. The §3 Steam block uses only those.
- **Both** auto-fill title, short summary, tags (Gameplay, Buildings), change note and,
  once declared, `image` and `screenshot1..5` from `metadata.lua`.

## Links block (filled at close-out)

| link | value | confirmed by |
|---|---|---|
| Paradox Mods page | none yet | owner receipt, first publish |
| Steam Workshop page | none yet | owner receipt, first publish |
| Steam changelog | `steamcommunity.com/sharedfiles/filedetails/changelog/<steam_id>` once `steam_id` exists | writeback |
| Site section | `https://catt144.github.io/SMR-CommunityMods/opt-in/` | `LIVE_SITE_READ.md` after the owner deploys |
| Repository | `https://github.com/catt144/SMR-CommunityOptInPack` | public now |

## After the first upload

`POST_UPLOAD_CLOSE.md` §5 changes the state heading above to `## State: LIVE since <date>`,
fills the two tables, and writes the as-published bodies in one `## Current live copy`
section, under the headings `#### 📋 Paradox Mods — description (plain text, paste as-is)`
and `#### 📋 Steam Workshop — description (BBCode, paste as-is)`. That section is the last
confirmed live copy: `store_parity.py` requires it whole on a live card, reports when the
staged blocks differ from it, and `--confirm-live` requires them equal at close-out. A
later release moves the previous bodies into a dated
`## ⭐ <date> — <what changed on the page>` section and replaces the current copy; the tool
never selects a history section.
