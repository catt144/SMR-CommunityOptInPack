# Build this repo's release system on the fix pack's

**Authored 2026-09-18** by the fix-pack coordinator seat, after the owner-list rename
(`DECISIONS_OWED.md` → `PLAYTEST_CHECKLIST.md`) landed at `3903eb0`.

```sh
git log --oneline -8 && git pull && python tools/doccheck.py | tail -1
git -C C:/Dev/SMR-BugFixPack log --oneline -5 -- docs/UPLOAD_WORKFLOW.md docs/agent/prompts/perma/release_prompt.md docs/agent/support/
```

## Authority — settled

⚖️ **Owner, 2026-09-18:** *"this repo needs its own release system and prompt. The public site
through github will be shared but it was pre designed that way so that shouldn't be to much of a
prompt."*

⚖️ **Owner, 2026-09-17:** this repo standardises on the fix pack (`C:\Dev\SMR-BugFixPack`), which it
was forked from — same folder and file names wherever the function is the same, same rules and
workflow; only repo-specific content differs. Where the fix pack has no name for something this
repo needs, stop and report; do not coin one.

⚖️ **Human docs are the owner's.** `docs/UPLOAD_WORKFLOW.md` is read by the owner at upload time:
write it for them, plainly, in the fix pack's shape. Agent-facing files may be tuned hard.

## What exists to copy

The fix pack's release system, all read-only to you:

| file | job |
|---|---|
| `docs/UPLOAD_WORKFLOW.md` | the owner's upload procedure and the store-card paste backups (its header rules say which bytes must match) |
| `docs/agent/prompts/perma/release_prompt.md` | the release job an agent runs |
| `docs/agent/prompts/perma/RELEASE_OUTBOX.md` | pending player-facing changes, with header rules; emptied only by a release |
| `docs/archive/RELEASE_HISTORY.md` | where released outbox entries go |
| `docs/agent/support/RELEASE_SURFACES.md`, `POST_UPLOAD_CLOSE.md`, `LIVE_SITE_READ.md` | the surfaces a release touches, the close-out after an upload, and how to read a live store page |

The shared site is `B:\Dev\SMR\SMR-CommunityMods` (MkDocs, `docs_dir: content`). Its README already
frames it as one site for every mod in the family, with a "The mods this site documents" table.
Today it has no opt-in page. The fix pack's `RELEASE_SURFACES.md` §2 is the site procedure for a fix
list; this mod's equivalent is a module list.

## End state

1. The files above exist here under the same names and paths, with this repo's content: this
   mod's id, its module set, its portals, and its not-yet-published state. The first upload is a
   **first publish**, not an update: the procedure must say what differs for it. For example,
   `last_changes` and the store ids do not exist yet.
2. The release prompt's site steps cover this mod's pages in the shared site: where its module
   list lives, its nav entry, its row in the site README's mods table, and the site's own
   deployment being the owner's act. Design it so the fix pack's release and this one never edit
   the same site file blind; say how.
3. The fork's rules and gates match the fix pack's for these files:
   - `UPLOAD_WORKFLOW.md` and `RELEASE_OUTBOX.md` carry the fix pack's header rules, adapted only
     where this repo differs, and join `RULE_HEADER_DOCS`.
   - The prompts-folder rule regains the fix pack's `RELEASE_OUTBOX.md` clause, which was dropped
     in `38b4e7c` only because the outbox did not exist.
   - `docs/README.md`'s map and doccheck's ROOT expectation gain `UPLOAD_WORKFLOW.md`.
   - The prompt map gains the perma rows.
   - WORKFLOW's "Release" and "Release marking" sections point at the new files.
4. `python tools/doccheck.py` is GREEN. `python tools/upload_preflight.py` runs, and its one known
   FAIL, the missing preview image, stays reported.

**Your call:** whether `docs/agent/reports/STORE_CARD_LIVE.md` exists before a first publish, or
the rule that names it waits for one. Record the reason.

## Known, not yours to fix

`metadata.lua`'s description still says "Eight opt-in modules" and names three modules retired on
2026-09-17, and `items.lua`/`metadata.lua` comments count nine options where there are six. That is
this mod's shipping content. Make sure the release procedure catches this class of drift (the
store body against the module set), and list it in your report. Do not edit it.

## Scope

**In:** the files named above in this repo, `docs/README.md`, WORKFLOW's two release sections,
`tools/doccheck.py` wiring, and the prompt map.
**Out:** `metadata.lua`, `items.lua`, `Code/`, and every file in `B:\Dev\SMR\SMR-CommunityMods`. The
site repo has another person's uncommitted edits, and player-facing pages for an unpublished mod
are the first release's job, not this build's. Read it; do not write it.

## Stops

1. A step needs a store id, portal account detail or site decision only the owner has: write the
   step with a named gap and list it.
2. A fix-pack release rule that cannot apply to a mod that has never shipped: keep it out, list
   it, and say why.

## Do not claim

- ❌ *"Ready to release."* ✅ what a first publish still needs from the owner, as a list.

## Lifecycle

One-off. `git rm` this file and delete its row in `docs/agent/prompts/README.md` in the commit that
lands the result.
