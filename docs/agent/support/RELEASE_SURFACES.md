# Preparing player-facing release surfaces

This is the surface-update procedure consumed by
`docs/agent/prompts/perma/release_prompt.md` §1. It is not a prompt or a separate
release front door. Adapted 2026-10-03 from the fix pack's procedure; what differs is
this mod's surfaces (module pages, not a fix list; no count word; store art fields) and
the generated store body.

## 1 · Inputs and scope

- The filled Pending entries in `docs/agent/prompts/perma/RELEASE_OUTBOX.md` are the
  batch. The corresponding module entries in `docs/agent/bugs/` are authority for claims;
  owner rulings recorded there or in `FIX_POLICY.md` bind the wording.
- Run `python tools/doccheck.py --emit-counts` before writing any figure. Record the
  command, filter and members that reconcile each total. This mod's store body carries no
  module count; do not introduce one.
- An internal change that never reached a player has no surface. Do not invent a module
  page change, a store claim or a change-note line for it.
- Write the symptom and the behaviour in player language, in vanilla's build-menu tone
  (`FIX_POLICY` §8). Use "error", not "crash", for a caught Lua error. Never a developer
  hedge ("unverified", "not witnessed") on a public surface; scope belongs in the entry.
- Platform wording is `FIX_POLICY` §7's: "Steam and other PC versions", never "PC".
- Never advertise clean removal, a load-order position or a rescue tool. The removal
  story is the two-step uninstall (dials to base and save; demolish hubs and depots and
  save) and the residual disclosure the measured residual set supports.

## 2 · Site and repository surfaces

Work in `B:\Dev\SMR\SMR-CommunityMods` only after reading its `git status --short` and
`git log --oneline -3`. Do not overwrite, stash or commit another person's dirty file;
commit this mod's paths only, and recheck status before the commit.

For an added, retired or materially respecified module or behaviour:

1. Update `content/opt-in/modules.md` in the module's section (what it does, default,
   when turned off, what it leaves in a save) and `content/opt-in/index.md` where the
   change touches installing, uninstalling or platform behaviour.
2. Search every content page for promises the change falsifies, including the fix-pack
   pages that point at this mod (`index.md`, `install.md`, `faq.md`, `for-modders.md`,
   `report.md`). A retirement can leave a named promise behind.
3. Check `mkdocs.yml`'s nav and `site_description`, and the site `README.md` mods row.
4. Check this repo's public `README.md`, the GitHub front page: module table, uninstall
   steps, console line.
5. Run `python -m mkdocs build --strict` in the site repo and require a clean build.

Committing the site repository does not deploy it. Deployment is the owner's act
(`docs/UPLOAD_WORKFLOW.md` §4); `LIVE_SITE_READ.md` says how to read what is live.

## 3 · Store bodies and shipped strings

The store body has one source and two generated copies:

- **Source:** the paste blocks in `docs/UPLOAD_WORKFLOW.md` §3 (Title, Short summary,
  Paradox plain text, Steam BBCode, Change note). Edit here.
- **Generated:** `metadata.lua`'s `description` and `last_changes`, written by
  `python tools/store_parity.py --write-metadata`. `short_description` is edited by hand
  only when the batch changes one of its claims.
- **Record:** `docs/agent/reports/STORE_CARD_LIVE.md` holds the last confirmed live copy.
  The §3 blocks are the staged copy; while an update is prepared the two differ, and the
  card is never rewritten to match before the owner confirms the upload.

`python tools/store_parity.py` proves Paradox block == `metadata.lua` description byte
for byte, Steam block == the same words with markup stripped, summary and change note
matching, one Steam `[h2]` per ALL-CAPS Paradox section, and a store card well formed for
its declared state. Zero FAIL is required. It reports, and does not fail on, a staged body
that differs from the live one; `--confirm-live` is the close-out's check.

The section order is fixed: the approved lede paragraph (OI-42 text), THE MODULES, YOUR
SAVE, AND REMOVING THE MOD, PLAYING ON XBOX, PLAYSTATION OR THE MICROSOFT STORE, BUGS,
QUESTIONS AND MORE DETAIL, and **BEFORE YOU UNINSTALL last** (owner, 2026-10-03, OI-45:
the uninstall note sits at the bottom of each store page). A newly featured item gets
its own ALL-CAPS section before the site section, never after the uninstall note.

Rewrite the change note for this release from the Pending entries. It is a per-version
store change note, not rolling copy. Keep it terse. Keep `items.lua` and the
`metadata.lua` code list aligned, but never edit a version field.

**Art fields.** `image` is the preview (`Mod/SMR_CommunityOptInPack/preview.png` at the
repo root, under 1 MB); `screenshot1..5` are the gallery files `tools/store_screenshots.py`
writes into `store_screenshots/`, which `ignore_files` keeps out of the pack. A change to
either is a surface change and gets a Pending line. Tags stay `TagGameplay` and
`TagBuildings` unless the owner rules otherwise.

## 4 · Gates and handoff

Before the release prompt hands off:

1. Reconcile every claim against its entry; no new behaviour claim without an entry or
   ruling behind it.
2. `python tools/doccheck.py` GREEN (after `--regen` if a generated file moved).
3. `python tools/store_parity.py` zero FAIL; `python tools/release_selftest.py` zero FAIL.
4. `python -m mkdocs build --strict` clean in the site repo.
5. Commit each repository with exact pathspecs and report what is committed but not
   yet public.
6. The package gates run on the launch tree, after the release prompt's §2 pins the batch:
   `python tools/release_batch.py verify`, `python tools/upload_preflight.py <launch tree>`
   zero FAIL, and `python tools/pack_predict.py <launch tree>` members and bytes reconciled
   and recorded. The working repo's result is not the package's.

The owner then follows `docs/UPLOAD_WORKFLOW.md`: mod upload and store-page formatting on
both portals; the agent then puts the real store links on the site; the owner publishes
the site last. The agent performs no portal or deployment action.
