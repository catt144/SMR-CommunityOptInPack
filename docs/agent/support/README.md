# support/ — prompt-supporting documents

Protocols and references used by prompts live here when they are not themselves
fired to make a session do a job. Prompts keep explicit pointers to the support
they consume; this map is updated when a supporting document lands.

| file | purpose |
|---|---|
| `README.md` | this purpose and destination map |
| `CHAIN_METHOD.md` | how to build a multi-session effort as a self-consuming chain of briefs: shape, difficulty tags, folder, links, terminal QA |
| `CO_RUNS.md` | binding situational protocol for co-runs: route, prepare, conduct and close attended experiment legs |
| `LIVE_SITE_READ.md` | read-only route for identifying the newest successful Pages deployment and checking this mod's live pages without publishing |
| `POST_UPLOAD_CLOSE.md` | non-fireable procedure for closing an owner-confirmed upload: writeback fields merged, each package compared, store links to the site, store card, tag and history; every step repeatable |
| `RELEASE_BATCH.json` | the release state `tools/release_batch.py` writes and reads: the open batch's base commit, entries, launch-tree manifest, per-portal snapshots and receipts, close steps, and closed batches. Never hand-edited |
| `RELEASE_SURFACES.md` | non-fireable procedure for applying an outbox batch to this mod's player-facing surfaces (site section, README, generated store body) and passing the pre-upload gates |
