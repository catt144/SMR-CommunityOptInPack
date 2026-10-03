#!/usr/bin/env python3
# Provenance: ported from SMR-BugFixPack @ 56d72579 on 2026-10-03; adapted: capture folder, five-shot MAP, WAITING rows, --list.
"""Build the store-gallery screenshots from the owner's captures, under the upload size limit.

The uploaders read `metadata.lua`'s screenshot1..5 and reject any file over
Steam's 1 MB or Paradox's 2 MB. The owner's PNGs run about 2 MB, so this
re-encodes each one as a JPEG under a 1,000,000-byte margin into
`store_screenshots/` at the repo root. The gallery order is screenshot1..5 in
`metadata.lua`, which is the order of MAP below. The folder is kept out of the
pack by `ignore_files` (`*/store_screenshots/*`), so the JPEGs never ship.

The captures come from `SMR-ScreenCaptures/optin_store`, a sibling of this
repo. A capture not yet dropped there prints WAITING and is skipped. The
owner's selection of the five shots is tracked on `docs/PLAYTEST_CHECKLIST.md`
OI-12.

    python tools/store_screenshots.py          encode every capture that is present
    python tools/store_screenshots.py --list   show what is in the capture folder

Exit 0 when every present file encodes under the limit (including when none is
present); exit 1 only when a present file cannot get under it.
"""
import os
import sys

# Console guard: the cp1252 default would die on a unicode path rather than on a finding.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The capture folder is this repo's sibling; a sibling-relative path survives a tree move.
SRC = os.path.join(os.path.dirname(ROOT), "SMR-ScreenCaptures", "optin_store")
OUT = os.path.join(ROOT, "store_screenshots")
LIMIT = 1_000_000  # Steam's cap is 1 MiB; keep a margin

# gallery order = screenshot1..5 in metadata.lua
MAP = [
    ("1_hub_day.png", "1_hub_day.jpg"),
    ("2_hub_panel.png", "2_hub_panel.jpg"),
    ("3_depot_pair.png", "3_depot_pair.jpg"),
    ("4_station_rows.png", "4_station_rows.jpg"),
    ("5_interests_popout.png", "5_interests_popout.jpg"),
]


def list_src():
    if not os.path.isdir(SRC):
        print(f"capture folder does not exist: {SRC}")
        return
    names = sorted(os.listdir(SRC))
    print(f"{SRC}: {len(names)} entries")
    for n in names:
        print("  " + n)


def encode():
    from PIL import Image  # imported late so --list works without Pillow

    ok = True
    made = False
    for src_name, out_name in MAP:
        src = os.path.join(SRC, src_name)
        if not os.path.isfile(src):
            print(f"WAITING  {src_name}  (owner capture not yet dropped in {SRC})")
            continue
        if not made:
            os.makedirs(OUT, exist_ok=True)
            made = True
        im = Image.open(src).convert("RGB")
        dst = os.path.join(OUT, out_name)
        for q in range(92, 49, -4):
            im.save(dst, "JPEG", quality=q, optimize=True, progressive=True)
            size = os.path.getsize(dst)
            if size <= LIMIT:
                break
        ok &= size <= LIMIT
        print(f"{out_name:<34} {im.size[0]}x{im.size[1]}  q={q}  {size:>9,} B  {'OK' if size <= LIMIT else 'TOO BIG'}")
    return ok


def main():
    if "--list" in sys.argv[1:]:
        list_src()
        sys.exit(0)
    sys.exit(0 if encode() else 1)


if __name__ == "__main__":
    main()
