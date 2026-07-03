#!/usr/bin/env python3
"""
normalize_face_sprites.py — Turn the raw generated expression sprites into an
engine-ready, uniformly-framed set + packed sprite sheet (Phase 3a).

WHY THIS EXISTS
    The 10 expression sprites in assets/2d/knitbit_face/ were generated
    individually and vary in faceplate framing/zoom (some faces fill the frame,
    some sit small inside a rendered bezel). Engines want uniform cells: same
    canvas, same content scale, consistent centering, clean black background
    (the faceplate is a black screen, so black — not transparency — is the
    correct paintable base for the faceplate UV).

WHAT IT DOES
    For each expression_<name>.png:
      1. Detect the glowing face glyphs: pixels where the green channel
         dominates red/blue by a RELATIVE margin (not absolute brightness —
         lowBattery is intentionally dim and must stay dim).
      2. Crop to the glyphs' bounding box + margin.
      3. Scale to fit a uniform content box (preserving aspect) and composite
         centered on a pure-black square cell.
    Then packs all cells into a 5x2 sprite sheet + JSON manifest mapping each
    BitExpression enum value to its pixel rect.

OUTPUT
    assets/2d/knitbit_face/normalized/<name>.png          (one 512px cell each)
    assets/2d/knitbit_face/knitbit_face_sheet.png         (2560x1024, 5x2 grid)
    assets/2d/knitbit_face/knitbit_face_sheet.json        (manifest)
    assets/2d/knitbit_face/normalized_contact_sheet.png   (labeled review montage)

RUN
    python3 tools/normalize_face_sprites.py
"""

import json
import os

from PIL import Image, ImageDraw

CELL = 512               # output cell size (square)
CONTENT_FRAC = 0.78      # face glyphs are scaled to fit this fraction of the cell
GREEN_DOMINANCE = 30     # G must exceed max(R, B) by this much to count as glyph
MIN_GREEN = 24           # ...and be at least this bright (rejects near-black noise)
GRID_COLS, GRID_ROWS = 5, 2

# order defines sheet layout; names match BitExpression enum values in
# game/lib/characters/bit_character.dart (file names use snake_case)
EXPRESSIONS = [
    ("idle", "expression_idle.png"),
    ("happy", "expression_happy.png"),
    ("thinking", "expression_thinking.png"),
    ("scared", "expression_scared.png"),
    ("effort", "expression_effort.png"),
    ("starEyes", "expression_star_eyes.png"),
    ("confused", "expression_confused.png"),
    ("lowBattery", "expression_low_battery.png"),
    ("startled", "expression_startled.png"),
    ("relieved", "expression_relieved.png"),
]


def _repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


FACE_DIR = os.path.join(_repo_root(), "assets/2d/knitbit_face")
OUT_DIR = os.path.join(FACE_DIR, "normalized")
SHEET_PNG = os.path.join(FACE_DIR, "knitbit_face_sheet.png")
SHEET_JSON = os.path.join(FACE_DIR, "knitbit_face_sheet.json")
CONTACT = os.path.join(FACE_DIR, "normalized_contact_sheet.png")


def glyph_bbox(img):
    """Bounding box of green-glow glyph pixels (relative dominance test)."""
    rgb = img.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if g >= MIN_GREEN and g - max(r, b) >= GREEN_DOMINANCE:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if maxx < 0:
        return None
    return (minx, miny, maxx + 1, maxy + 1)


def glow_mask_composite(img, bbox):
    """Crop the glyph region and composite onto pure black, keeping only the
    green glow (kills bezel reflections/backgrounds inside the crop). The glow
    halo around glyphs is dimmer than the dominance threshold, so the mask is
    built from a soft variant: keep any pixel where green exceeds red/blue at
    all, weighted by how much."""
    rgb = img.convert("RGB").crop(bbox)
    w, h = rgb.size
    src = rgb.load()
    out = Image.new("RGB", (w, h), (0, 0, 0))
    dst = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            excess = g - max(r, b)
            if excess > 0 and g >= 8:
                # keep the pixel; soft-scale very weak excess so halo fades out
                k = min(1.0, excess / 40.0)
                dst[x, y] = (int(r * k), int(g * k) if k < 1.0 else g, int(b * k))
    return out


def normalize(src_path):
    img = Image.open(src_path)
    bbox = glyph_bbox(img)
    if bbox is None:
        raise SystemExit(f"[normalize] no glyphs detected in {src_path}")
    # margin: 4% of the glyph box's larger side
    m = int(0.04 * max(bbox[2] - bbox[0], bbox[3] - bbox[1]))
    bbox = (max(0, bbox[0] - m), max(0, bbox[1] - m),
            min(img.width, bbox[2] + m), min(img.height, bbox[3] + m))
    content = glow_mask_composite(img, bbox)

    target = int(CELL * CONTENT_FRAC)
    scale = target / max(content.size)
    new_size = (max(1, round(content.width * scale)),
                max(1, round(content.height * scale)))
    content = content.resize(new_size, Image.LANCZOS)

    cell = Image.new("RGB", (CELL, CELL), (0, 0, 0))
    cell.paste(content, ((CELL - content.width) // 2, (CELL - content.height) // 2))
    return cell


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cells = {}
    for name, fname in EXPRESSIONS:
        src = os.path.join(FACE_DIR, fname)
        cell = normalize(src)
        out = os.path.join(OUT_DIR, f"{name}.png")
        cell.save(out)
        cells[name] = cell
        print(f"[normalize] {name}: {fname} -> normalized/{name}.png")

    # sprite sheet + manifest
    sheet = Image.new("RGB", (GRID_COLS * CELL, GRID_ROWS * CELL), (0, 0, 0))
    manifest = {
        "sheet": os.path.basename(SHEET_PNG),
        "cell_size": CELL,
        "grid": {"cols": GRID_COLS, "rows": GRID_ROWS},
        "enum": "BitExpression (game/lib/characters/bit_character.dart)",
        "frames": {},
    }
    for i, (name, _) in enumerate(EXPRESSIONS):
        col, row = i % GRID_COLS, i // GRID_COLS
        x, y = col * CELL, row * CELL
        sheet.paste(cells[name], (x, y))
        manifest["frames"][name] = {"x": x, "y": y, "w": CELL, "h": CELL,
                                    "col": col, "row": row}
    sheet.save(SHEET_PNG)
    with open(SHEET_JSON, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[normalize] sheet: {SHEET_PNG} ({sheet.width}x{sheet.height})")
    print(f"[normalize] manifest: {SHEET_JSON}")

    # labeled contact sheet for review
    label_h = 40
    contact = Image.new("RGB", (GRID_COLS * CELL, GRID_ROWS * (CELL + label_h)),
                        (24, 24, 24))
    draw = ImageDraw.Draw(contact)
    for i, (name, _) in enumerate(EXPRESSIONS):
        col, row = i % GRID_COLS, i // GRID_COLS
        x, y = col * CELL, row * (CELL + label_h)
        contact.paste(cells[name], (x, y))
        draw.text((x + 12, y + CELL + 10), name, fill=(180, 255, 180))
    contact.save(CONTACT)
    print(f"[normalize] contact sheet: {CONTACT}")


if __name__ == "__main__":
    main()
