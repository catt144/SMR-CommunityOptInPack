#!/usr/bin/env python3
"""Annotate the owner's captures for the store gallery: crop, callout boxes, arrows, a title strip.

Reads `tools/store_annotations.json` (the editable spec) and writes one
1920x1080 PNG per entry into the gallery drop folder, plus `contact_sheet.png`
showing them all at thumbnail width. The originals are opened read-only and
never written; the tool refuses to write into the capture folder.

Every coordinate in the spec is in SOURCE-CAPTURE pixels, so a position can be
read straight off the original in any image viewer:

    crop      [x0, y0, x1, y1]  the part of the capture that is kept
    callouts  color   yellow (click here / how-to), green (feature), red (caution)
              head    bold uppercase headline
              sub     list of plain lines under it (optional)
              at      [x, y] centre of the box
              to      list of [x, y] arrow targets (optional, one arrow each)
              circle  [x, y, r] ring round a small button (optional)
    strip     title (left, bold) and note (right) on the bar under the picture

The crop is scaled to the full width; the strip takes what is left of the
height, so a crop near 1.95:1 gives a strip of about 96 px.

    python tools/annotate_screenshots.py              annotate every entry
    python tools/annotate_screenshots.py --only NAME  one entry (its `out` name), no contact sheet

Then `python tools/store_screenshots.py` encodes the five gallery names under
the store limit.
"""
import json
import math
import os
import sys

# Console guard: the cp1252 default would die on a unicode path rather than on a finding.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "tools", "store_annotations.json")

W, H = 1920, 1080
SS = 2  # the overlay is drawn at 2x and scaled down, which is the antialiasing
COLORS = {"yellow": (255, 221, 0), "green": (46, 224, 70), "red": (238, 62, 50)}
BOX_FILL = (16, 16, 18, 238)
STRIP_FILL = (14, 17, 24)
STRIP_LINE = (214, 120, 58)
FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
HEAD_PX, SUB_PX = 46, 32
THUMB_W = 600  # the store's thumbnail width, near enough; the contact sheet is the readability check


def font(bold, px):
    from PIL import ImageFont

    for name in (("arialbd.ttf", "segoeuib.ttf") if bold else ("arial.ttf", "segoeui.ttf")):
        path = os.path.join(FONT_DIR, name)
        if os.path.isfile(path):
            return ImageFont.truetype(path, px)
    return ImageFont.load_default(px)


def box_edge(cx, cy, hw, hh, tx, ty):
    """Where the line from the box centre to the target leaves the box."""
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    t = min(hw / abs(dx) if dx else math.inf, hh / abs(dy) if dy else math.inf)
    return cx + dx * t, cy + dy * t


def arrow(draw, p0, p1, color, width, head_len, head_w):
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    ux, uy = math.cos(ang), math.sin(ang)
    bx, by = p1[0] - ux * head_len, p1[1] - uy * head_len
    draw.line([p0, (bx, by)], fill=color, width=width)
    draw.polygon([p1, (bx - uy * head_w / 2, by + ux * head_w / 2),
                  (bx + uy * head_w / 2, by - ux * head_w / 2)], fill=color)


def annotate(entry, captures):
    from PIL import Image, ImageDraw

    src = Image.open(os.path.join(captures, entry["source"])).convert("RGB")
    x0, y0, x1, y1 = entry["crop"]
    k = W / (x1 - x0)
    pic_h = round((y1 - y0) * k)
    if pic_h > H:
        raise SystemExit(f"{entry['out']}: crop is taller than 16:9; widen it or trim its height")
    canvas = Image.new("RGB", (W, H), STRIP_FILL)
    canvas.paste(src.crop((x0, y0, x1, y1)).resize((W, pic_h), Image.LANCZOS), (0, 0))

    def pt(p):  # source pixels -> overlay pixels
        return (p[0] - x0) * k * SS, (p[1] - y0) * k * SS

    over = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    f_head, f_sub = font(True, HEAD_PX * SS), font(False, SUB_PX * SS)
    pad_x, pad_y, gap, border = 26 * SS, 18 * SS, 8 * SS, 6 * SS

    boxes = []
    for c in entry.get("callouts", []):
        lines = [(c["head"].upper(), f_head)] + [(s, f_sub) for s in c.get("sub", [])]
        sizes = [d.textbbox((0, 0), t, font=f) for t, f in lines]
        heights = [f.size * 1.18 for _, f in lines]
        bw = max(b[2] - b[0] for b in sizes) + 2 * pad_x
        bh = sum(heights) + gap * (len(lines) - 1) + 2 * pad_y
        boxes.append((c, lines, heights, bw, bh, pt(c["at"])))

    # arrows first, so each box covers its own arrow's tail
    for c, _, _, bw, bh, (cx, cy) in boxes:
        col = COLORS[c["color"]]
        for target in c.get("to", []):
            tx, ty = pt(target)
            start = box_edge(cx, cy, bw / 2 - border, bh / 2 - border, tx, ty)
            arrow(d, start, (tx, ty), (0, 0, 0, 150), 20 * SS, 52 * SS, 54 * SS)
            arrow(d, start, (tx - 3 * SS * math.cos(math.atan2(ty - cy, tx - cx)),
                             ty - 3 * SS * math.sin(math.atan2(ty - cy, tx - cx))),
                  col + (255,), 13 * SS, 44 * SS, 42 * SS)
        if "circle" in c:
            qx, qy = pt(c["circle"][:2])
            r = c["circle"][2] * k * SS
            d.ellipse([qx - r, qy - r, qx + r, qy + r], outline=col + (255,), width=border)

    for c, lines, heights, bw, bh, (cx, cy) in boxes:
        col = COLORS[c["color"]]
        d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2],
                            radius=18 * SS, fill=BOX_FILL, outline=col + (255,), width=border)
        y = cy - bh / 2 + pad_y
        for (text, f), h in zip(lines, heights):
            d.text((cx, y + h / 2), text, font=f, fill=(255, 255, 255, 255), anchor="mm")
            y += h + gap

    # the title strip under the picture
    strip = entry.get("strip", {})
    d.line([(0, pic_h * SS), (W * SS, pic_h * SS)], fill=STRIP_LINE + (255,), width=4 * SS)
    mid = (pic_h + (H - pic_h) / 2 + 2) * SS
    d.text((40 * SS, mid), strip.get("title", ""), font=font(True, 44 * SS),
           fill=(255, 255, 255, 255), anchor="lm")
    d.text(((W - 40) * SS, mid), strip.get("note", ""), font=font(False, 30 * SS),
           fill=(190, 198, 210, 255), anchor="rm")

    canvas = Image.alpha_composite(canvas.convert("RGBA"), over.resize((W, H), Image.LANCZOS))
    return canvas.convert("RGB"), H - pic_h


def contact_sheet(made, out_dir):
    from PIL import Image, ImageDraw

    cols, label_h, pad = 3, 44, 16
    th = round(THUMB_W * H / W)
    rows = math.ceil(len(made) / cols)
    sheet = Image.new("RGB", (cols * (THUMB_W + pad) + pad, rows * (th + label_h + pad) + pad), (30, 32, 38))
    d = ImageDraw.Draw(sheet)
    f = font(True, 24)
    for i, (name, im) in enumerate(made):
        x = pad + (i % cols) * (THUMB_W + pad)
        y = pad + (i // cols) * (th + label_h + pad)
        sheet.paste(im.resize((THUMB_W, th), Image.LANCZOS), (x, y))
        d.text((x + 4, y + th + label_h / 2), name, font=f, fill=(235, 235, 235), anchor="lm")
    path = os.path.join(out_dir, "contact_sheet.png")
    sheet.save(path, optimize=True)
    print(f"{'contact_sheet.png':<28} {sheet.size[0]}x{sheet.size[1]}  {len(made)} images")
    return path


def main():
    args = sys.argv[1:]
    only = args[args.index("--only") + 1] if "--only" in args else None
    with open(SPEC, encoding="utf-8") as fh:
        spec = json.load(fh)
    captures, out_dir = spec["captures"], spec["out"]
    if os.path.normcase(os.path.abspath(captures)) == os.path.normcase(os.path.abspath(out_dir)):
        raise SystemExit("the drop folder is the capture folder; originals are read-only")
    os.makedirs(out_dir, exist_ok=True)
    made = []
    for entry in spec["images"]:
        if only and entry["out"] != only:
            continue
        im, strip_h = annotate(entry, captures)
        im.save(os.path.join(out_dir, entry["out"]), optimize=True)
        made.append((entry["out"], im))
        print(f"{entry['out']:<28} from {entry['source']}  strip {strip_h} px  "
              f"{len(entry.get('callouts', []))} callouts")
    if not made:
        raise SystemExit(f"no entry named {only}")
    if not only:
        contact_sheet(made, out_dir)


if __name__ == "__main__":
    main()
