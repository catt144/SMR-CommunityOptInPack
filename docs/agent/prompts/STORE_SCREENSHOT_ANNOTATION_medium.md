# Store screenshots: annotate the owner's captures with arrows and feature blurbs

**Fire with:** `task docs/agent/prompts/STORE_SCREENSHOT_ANNOTATION_medium.md` in a fresh session
rooted at `B:\Dev\SMR\SMR-OptInPack`. Reasoning: medium (visual judgement and claim accuracy; no
engine work).

## Authority and outcome

The owner, 2026-10-03: go through the screenshots they took and add **arrows and short info
blurbs** that highlight the features: storage, what each module does, upgrades, and so on. These
become the store gallery for OI-12 (`docs/PLAYTEST_CHECKLIST.md`). The owner fine-tunes by eye
(prototype first). Get a rough, good-looking set in front of them quickly rather than a perfect one.

Done when the owner has a reviewable set of annotated images in the gallery drop folder, each under
the store limits, plus a contact sheet showing them all, and the annotation is reproducible from a
script and an editable spec so the owner's tweaks are one edit and one re-run.

## Inputs

- **The captures:** `C:\Users\stkot\OneDrive\Pictures\Screenshots\2026-10\`, nine `Mars_*.jpg`
  files taken 2026-10-02 and 2026-10-03 (`ls` it again; the owner may add more). **Read-only:**
  never modify, rename or delete an original.
- **The gallery plan:** `docs/agent/reports/STORE_AND_SITE_20261003.md` §5. It gives the five-shot
  list (`1_hub_day` … `5_interests_popout`), the drop folder
  `B:\Dev\SMR\SMR-ScreenCaptures\optin_store\`, and `python tools/store_screenshots.py`, which
  encodes the drop folder under 1 MB into `store_screenshots/`. Limits: 1 MB per image for Steam,
  2 MB for Paradox; `python tools/upload_preflight.py` enforces them.
- **What the blurbs may claim:** the maintained store copy (`STORE_AND_SITE_20261003.md` §3 and
  `docs/UPLOAD_WORKFLOW.md` §3's paste blocks), the module records `docs/agent/bugs/D16.md`-`D18.md`
  and the other shipping `D` entries, and the in-game strings in `Code/`. A blurb states what the
  shipping build does. It must not advertise clean removal: the owner ruled demolish-first, OI-45.
  It must not mention retired or parked modules (`docs/PARKED_MODULES.md`).

## Work

1. Look at every capture. Note what it shows, whether it is usable (no SMR Tool Kit panel, debug
   overlay, dev-only or retired content, or personal information), and which shot-list slot it
   fills best. Captures may cover a feature the shot list lacks; propose those as alternates.
2. Write the annotation as a script plus a spec, for example JSON with each image's crop, arrows
   (from, to), callout boxes (anchor, text) and title strip. Put the script under `tools/` with a
   `tools/README.md` catalogue row (doccheck reconciles `tools/*.py` against it). Pillow is
   available.
3. **Style.** Use one consistent look across the set: a clean sans font; callouts with a
   semi-opaque dark panel and a thin accent border in a colour that reads against Mars terrain
   (the game UI's cyan/blue suits); arrows with a clear head and a subtle shadow. Keep callouts
   off the thing being shown and off the game UI the shot exists to show. At most about three
   callouts per image. Text must stay readable at the store's thumbnail size: check by
   downscaling to about 600 px wide.
4. **Text.** Use the game's own tone (build-menu style): one or two short sentences, with
   keywords emphasised visually rather than shouted. Give no numbers that a dial or upgrade
   changes. Name modules as players see them in Mod Options.
5. Write annotated PNGs to the drop folder with the shot-list names, plus `contact_sheet.png` (all
   images in a grid with their names). Then run `python tools/store_screenshots.py` and
   `python tools/upload_preflight.py`, and report their output.
6. Hand the owner the contact sheet's path, a table (file, source capture, callout texts), and
   which slots are still unfilled, with the exact shot each would need.

Keep a work list (the todo tool if the session has one). `git log --oneline -3` and `git pull`
first; authored at `de0366c`. References: `CLAUDE.md`, `docs/agent/WORKFLOW.md`; skills
`doc-editing` (for any doc you touch) and `smr-bug-library` (to look up module records).

## Scope

In: selecting, cropping, annotating, encoding and reporting; the new tool and its catalogue row.
Out: choosing the preview image or wiring `metadata.lua`'s `image` (the owner's OI-12 pick), any
store-copy rewrite, uploading, and any `Code/` change.

## Stops

1. Fewer than three captures are usable. Report which slots need new shots and exactly what each
   should show, and annotate what is usable.
2. A feature claim cannot be confirmed from the inputs above. Leave that callout out and list it
   for the owner, rather than guessing.

## Lifecycle

One-off. Commit the tool, spec and report (`docs/agent/reports/STORE_SCREENSHOTS_<date>.md`), but
not the images: the drop folder is outside the repo, and `store_screenshots/` is excluded from the
pack. Delete this prompt and its row in `docs/agent/prompts/README.md` in the same commit. Leave
OI-12 open for the owner's pick.
