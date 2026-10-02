# Launch-prep audit — what this mod still needs before it can publish (investigation)

**Fire with:** `task docs/agent/prompts/LAUNCH_PREP_AUDIT_high.md` in a fresh session rooted at
`B:\Dev\SMR\SMR-OptInPack`. It may fire now. It reads, writes one report and authors briefs; it
changes no code, no store text and nothing in another repo.

Reasoning: high. This is a cross-repo comparison with the fix pack's release system, plus a
sequencing plan.

## Authority and outcome

The owner, 2026-10-02: *"we will need a full launch prep audit. Because the site will need to be
merged with relaunched fix pack on smr community mods, the store pages need build, and likely the
release prompt will need updated. And we will need a release workflow doc just like the fix
packs."* The launch scope is settled; do not reopen it.

When this is done:

- a report in `docs/agent/reports/` lists everything this mod needs before it can publish, what
  exists for each item, the gap, and the owner decision each item waits on;
- the work is split into briefs authored in fire order, with the `prompt-authoring` skill;
- the owner's questions are filed in `docs/PLAYTEST_CHECKLIST.md`.

## Cover at least these

1. **The release workflow doc and the release prompt.** The fix pack's system lives in
   `B:\Dev\SMR\SMR-BugFixPack` (`UPLOAD_WORKFLOW.md`, `release_prompt.md`, the release outbox, and
   `docs/agent/support/RELEASE_SURFACES.md`, `POST_UPLOAD_CLOSE.md`, `LIVE_SITE_READ.md`).
   [`RELEASE_SYSTEM_high.md`](RELEASE_SYSTEM_high.md) was authored 2026-09-18 to copy that system
   here and has never fired. It predates the train modules (D16-D18). Decide whether it fires as
   written, gets revised, or is replaced by your briefs. If it is revised or replaced, do that in
   the same commit as your briefs and update its row in this folder's `README.md`.
2. **The shared site**, `B:\Dev\SMR\SMR-CommunityMods` (MkDocs). The opt-in pages must merge into
   the site the Relaunched Fix Pack already uses: the module pages, the nav entry, the row in the
   README's mods table, and how the release prompt keeps them in step. The site repo has had
   another person's uncommitted edits, so read it and do not write to it. Run `git status` there
   and report what you see.
3. **The store pages** (every storefront the fix pack publishes to): description,
   short description, preview image, screenshots, tags, changelog, and the portal and console
   steps. `metadata.lua`'s description and short description were approved 2026-10-02 (OI-42).
   `last_changes` still describes the split-era module set.
4. **`optional_mod = true`** in `metadata.lua`. It suppresses the missing-mods warning when a save
   loads without the mod. That was safe when every module removed cleanly; built hubs and depots
   now stay in a save (`FIX_POLICY` §0). Lay out the options for the owner and the evidence for
   each.
5. **Every open launch item** in `docs/PLAYTEST_CHECKLIST.md` (OI-21, the store tools, among
   them) and every launch obligation in `FIX_POLICY` §8: the both-configuration ship test, the
   `Lua.fpk` verification, D-entry status, credits, separate-product metadata. For each, say
   whether it is done, owed, or owned by a named brief.
6. **The upload itself**: `tools/upload_preflight.py`, which was widened for the train modules by
   OI-18 at `5aa529d`, and the pack's ignore list. The trains finish with brief 35 in
   `Train_Hub_Project/`; sequence launch after it, and do not duplicate its battery.

## Scope

In: reading this repo, the fix pack and the site; the report; briefs in `docs/agent/prompts/`;
checklist items.

Out: editing code, `metadata.lua`, store text, the site repo or the fix pack repo; publishing
anything.

## Stops (report instead of continuing)

1. A finding needs a store id, account detail or site decision that only the owner has. File it
   as a checklist question and carry on with the rest.
2. A fix-pack release file contradicts this repo's two bans (`FIX_POLICY` header) when copied.
   Report the conflict; do not adapt it silently.

## Claim limits

"Ready to publish" is not yours to claim. The report says what is owed and who owes it.

## Work list and references

Keep a work list, one item per commit-and-verify unit: in the todo tool if the session has one,
otherwise in the report. Start with `git log --oneline -5` and `git pull`. This brief was authored
at `e6f285a`.

House rules are in `CLAUDE.md`, process in `docs/agent/WORKFLOW.md`, code and release rules in
`docs/agent/FIX_POLICY.md` (§8 includes the player-text rule). Use the skills `prompt-authoring`,
`doc-editing` and `smr-orientation`. Run `python tools/doccheck.py` before committing. When you
finish, tell the owner which brief fires first. Delete this brief when it has fired and its
briefs are authored.
