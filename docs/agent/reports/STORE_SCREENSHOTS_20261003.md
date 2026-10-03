# Store screenshots: the annotated gallery set (OI-12), 2026-10-03

The owner's nine captures were annotated into seven store images: four of the five gallery slots
and three alternates. OI-12 stays open for the owner's pick of preview and gallery.

## How to change an image

1. Edit `tools/store_annotations.json`. Every coordinate is in source-capture pixels, so a
   position can be read off the original in any image viewer. The spec's fields are described in
   the header of `tools/annotate_screenshots.py`.
2. Run `python tools/annotate_screenshots.py` (`--only <name>.png` for one image).
3. Run `python tools/store_screenshots.py` to encode the five gallery names under the store limit.

Output goes to `B:\Dev\SMR\SMR-ScreenCaptures\optin_store\`; the review sheet is
`contact_sheet.png` there. The originals in `C:\Users\stkot\OneDrive\Pictures\Screenshots\2026-10\`
are only read.

## Owner ruling taken during the run

Owner, 2026-10-03: "you can leave the fixpack cheats in the screen captures, its not a big deal.
People will understand that its a dev screen capture". The Tool Kit section of an infopanel may
therefore stay in a store image. The crops were chosen for framing, not to hide it; the
`SMR | CLEAN` status bar happens to fall outside every crop.

## The set

| file | source capture | callouts (headline: subtext) |
|---|---|---|
| `1_hub_day.png` | `Mars_7Mb20CUq85.jpg` | TRAIN HUB: A junction where three train lines cross and cargo changes lines. · NETWORK STORAGE: Stores resources for the stations on its lines. |
| `2_hub_panel.png` | `Mars_iTEL18iLdk.jpg` | UPGRADES: The hub has upgrades of its own. · ITS OWN DRONES: They build and repair track. · STORAGE: Holds resources for the stations on its lines. |
| `3_depot_pair.png` | `Mars_reimzMptEd.jpg` | ELEVATOR DEPOT: Links surface and underground train lines. · CAPACITY UPGRADE: One upgrade doubles its capacity. · IMPORT OR EXPORT: Import goes down. Export comes up. |
| `4_station_rows.png` | `Mars_frY9H1j8On.jpg` | EVERY TRAIN STATION: Works with or without a Train Hub. · SET EACH RESOURCE: Import, Export, Balanced or Not accepted, with a target slider. |
| `alt_multiple_suns.png` | `Mars_8ncwKdJphr.jpg` | MORE THAN ONE ARTIFICIAL SUN: Solar panels connect to whichever sun covers them. |
| `alt_mod_options.png` | `Mars_YdVfdJljli.jpg` | A SWITCH FOR EVERY MODULE: Each one is off, or at its base setting, until you turn it on. · TWO DRONE DIALS: Drone speed and Drone carry capacity. |
| `alt_drone_dials.png` | `Mars_HzpuTAMc3u.jpg` | DRONE CARRY CAPACITY: Drones carry more on every trip. · TWO DIALS IN MOD OPTIONS: Drone speed and Drone carry capacity. |

Every callout restates a sentence of the maintained store copy (`docs/UPLOAD_WORKFLOW.md` §3).
No callout gives a number that a dial or an upgrade changes, none mentions removal, and none names
a retired or parked module.

Not annotated: `Mars_HDe39h94qp.jpg` (the Drone speed choices) and `Mars_HdHx7MHeRO.jpg` (the
Drone carry capacity choices). Both are usable, but `alt_mod_options.png` already shows the two
dials on one page.

## What is still owed

- **Slot 5, `5_interests_popout.png`, has no capture.** It needs a placed service building
  selected (an Electronics Store fits the store copy's example), with the infopanel's "Interests"
  section visible and its popout open.
- **`3_depot_pair.png` shows the surface half only.** A capture of the underground half would
  complete the pair, as a second image or a replacement.
- **No capture shows Acknowledged warnings.** A still cannot show a warning staying quiet, so it
  is left to the store text unless the owner wants a shot of the dismissed notification.
- The three `alt_*` images are in the drop folder but outside `store_screenshots.py`'s five-name
  MAP. To use one in the gallery, rename it to a slot name or change the MAP.

## Gate output

`python tools/store_screenshots.py`, at HEAD `9330ca4` plus this work:

```
1_hub_day.jpg                      1920x1080  q=92    509,699 B  OK
2_hub_panel.jpg                    1920x1080  q=92    517,673 B  OK
3_depot_pair.jpg                   1920x1080  q=92    433,399 B  OK
4_station_rows.jpg                 1920x1080  q=92    488,582 B  OK
WAITING  5_interests_popout.png  (owner capture not yet dropped in B:\Dev\SMR\SMR-ScreenCaptures\optin_store)
```

`python tools/upload_preflight.py`: 33 checked, 1 FAIL, 1 UNCHECKABLE. The FAIL is
`PDX image non-empty`, the preview the owner has yet to pick (OI-12); the UNCHECKABLE is the
Paradox login. Screenshots: "none declared — allowed", because `metadata.lua` does not name
`screenshot1..5` until the owner picks.
