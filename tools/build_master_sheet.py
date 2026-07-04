#!/usr/bin/env python3
"""build_master_sheet.py — compose the KnitBit Master Trait Diagram (spec §9).

The single planning / style-approval sheet: every trait category with its option
thumbnails, each tagged by theme color, plus the full theme palette legend and
the planned-but-not-built categories. Fully manifest-driven — reads
manifest.json + the thumbnails from tools/render_trait_thumbs.py — so it
regenerates as the library grows.

Deliberately NOT a Production Part Sheet (spec §9): this is the wide overview for
planning, not the clean one-category-at-a-time sheet used for 3D conversion.

RUN (needs the thumbs; render them first):
    blender --background --python tools/render_trait_thumbs.py
    python3 tools/build_master_sheet.py
OUT:
    assets/3d/knitbit_base/knitbit_master_trait_diagram.png
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knitbit_manifest as km  # noqa: E402

M = km.load()
ASSET = km.ASSET_DIR
THUMBS = os.path.join(ASSET, "thumbs")
OUT = os.path.join(ASSET, "knitbit_master_trait_diagram.png")

# palette
BG = (255, 255, 255)
BAND = (243, 244, 246)
INK = (26, 29, 33)
MUTED = (107, 114, 128)
LINE = (222, 226, 230)
CELL = (250, 250, 251)

W = 1680
PAD = 40
CELL_W, CELL_H = 300, 300
THUMB = 220

# planned categories not yet built (spec §5/§6 + builder gaps)
PLANNED = [
    "Boots (mesh-swap)", "Hands (mesh-swap)", "Belt pouches", "Boot decals",
    "Surface decals", "Capes / cloaks", "Ear modules", "Faceplate FX",
]


def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
        "/usr/share/fonts/truetype/liberation/LiberationSans%s.ttf" % ("-Bold" if bold else ""),
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_TITLE = font(46, True)
F_SUB = font(20)
F_H = font(28, True)
F_LABEL = font(20, True)
F_SMALL = font(17)
F_TINY = font(15)


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))


def paste_thumb(base, path, x, y, box):
    if not os.path.exists(path):
        return
    im = Image.open(path).convert("RGBA")
    im.thumbnail((box, box), Image.LANCZOS)
    ox = x + (box - im.width) // 2
    oy = y + (box - im.height) // 2
    base.paste(im, (ox, oy), im)


def text_center(d, cx, y, s, f, fill):
    w = d.textlength(s, font=f)
    d.text((cx - w / 2, y), s, font=f, fill=fill)


def measure_height():
    slots = M["slots"]
    h = PAD + 70 + 40                      # header
    h += 40                                # base strip label area handled in header
    for _ in slots:
        h += 44 + CELL_H + 24              # slot band + row
    h += 60 + 90                           # planned section
    h += 60 + 150                          # theme legend
    h += PAD
    return h


def main():
    themes = M["themes"]
    by_slot = km.traits_by_slot(M)
    H = measure_height()
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    y = PAD
    # ---- header ----
    d.text((PAD, y), "KnitBit — Master Trait Diagram", font=F_TITLE, fill=INK)
    d.text((PAD, y + 56), "Every trait category × theme color. Planning / style-approval sheet — "
                          "generated from manifest.json.", font=F_SUB, fill=MUTED)
    # base thumb top-right
    paste_thumb(img, os.path.join(THUMBS, "base.png"), W - PAD - 150, y - 10, 150)
    text_center(d, W - PAD - 75, y + 132, "neutral base", F_TINY, MUTED)
    y += 70 + 40

    # ---- category rows ----
    for slot_key, slot in M["slots"].items():
        d.rectangle([PAD, y, W - PAD, y + 40], fill=BAND)
        d.text((PAD + 14, y + 8), slot.get("label", slot_key).upper(), font=F_H, fill=INK)
        # dynamic tag
        if slot.get("dynamic"):
            tag = "dynamic · swings"
            tw = d.textlength(tag, font=F_SMALL)
            d.text((W - PAD - tw - 14, y + 11), tag, font=F_SMALL, fill=(180, 90, 30))
        y += 44
        opts = by_slot.get(slot_key, [])
        x = PAD
        for t in opts:
            d.rectangle([x, y, x + CELL_W, y + CELL_H], fill=CELL, outline=LINE)
            paste_thumb(img, os.path.join(THUMBS, t["id"] + ".png"), x + (CELL_W - THUMB) // 2, y + 16, THUMB)
            text_center(d, x + CELL_W / 2, y + THUMB + 26, t.get("label", t["id"]), F_LABEL, INK)
            # theme dot + name
            th = themes.get(t.get("theme", "neutral"), {})
            acc = hx(th.get("accent", "#C9CDD2"))
            d.ellipse([x + CELL_W/2 - 58, y + THUMB + 52, x + CELL_W/2 - 44, y + THUMB + 66], fill=acc, outline=LINE)
            text_center(d, x + CELL_W / 2 + 6, y + THUMB + 50, th.get("label", t.get("theme", "")), F_SMALL, MUTED)
            x += CELL_W + 20
        y += CELL_H + 24

    # ---- planned categories ----
    d.rectangle([PAD, y, W - PAD, y + 40], fill=BAND)
    d.text((PAD + 14, y + 8), "PLANNED CATEGORIES (not yet built)", font=F_H, fill=INK)
    y += 60
    cx = PAD
    for name in PLANNED:
        w = d.textlength(name, font=F_SMALL) + 28
        if cx + w > W - PAD:
            cx = PAD
            y += 46
        d.rounded_rectangle([cx, y, cx + w, y + 34], radius=17, fill=(237, 239, 242), outline=LINE)
        d.text((cx + 14, y + 7), name, font=F_SMALL, fill=MUTED)
        cx += w + 12
    y += 90

    # ---- theme legend ----
    d.rectangle([PAD, y, W - PAD, y + 40], fill=BAND)
    d.text((PAD + 14, y + 8), "THEME COLOR LEGEND (§7 — yarn material-swap + theme accessories)",
           font=F_H, fill=INK)
    y += 58
    order = [k for k in themes if k != "_comment"]
    col_w = (W - 2 * PAD) // 5
    for i, key in enumerate(order):
        th = themes[key]
        col = i % 5
        row = i // 5
        cxx = PAD + col * col_w
        cyy = y + row * 66
        acc = hx(th.get("accent", "#C9CDD2"))
        d.rounded_rectangle([cxx, cyy, cxx + 46, cyy + 46], radius=8, fill=acc, outline=LINE)
        if th.get("accent2"):
            d.rounded_rectangle([cxx + 32, cyy + 26, cxx + 52, cyy + 46], radius=6, fill=hx(th["accent2"]), outline=LINE)
        d.text((cxx + 60, cyy + 4), th.get("label", key), font=F_LABEL, fill=INK)
        d.text((cxx + 60, cyy + 28), th.get("accent", ""), font=F_TINY, fill=MUTED)

    img.save(OUT)
    print(f"[master] wrote {OUT} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
