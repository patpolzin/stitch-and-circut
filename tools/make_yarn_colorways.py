#!/usr/bin/env python3
"""Yarn mask + colorway generator for the KnitBit base.

The v2 neutral base is generated with deliberately CRIMSON yarn so the yarn
is hue-separable from the matte gray plating and the green pixel face. This
tool:

  1. extracts the baked baseColor texture from the raw (crimson) GLB,
  2. hue-keys the crimson yarn into a soft mask (with morphological closing
     and edge feathering so plating edges don't halo),
  3. recolors the yarn region per theme (luminance-preserving HSV transfer,
     so the knit braid shading survives recoloring) producing one texture per
     manifest theme + the charcoal DNA default + the original "reference red",
  4. re-embeds the charcoal texture into the GLB via headless Blender and
     writes the canonical `knitbit_base_apose_textured.glb` (committed base
     stays on-DNA charcoal per docs/KnitBit-Base-Spec.md section 1).

Usage:
  python3 tools/make_yarn_colorways.py <raw_crimson.glb>

Outputs (relative to assets/3d/knitbit_base/):
  textures/base_color_crimson.png   extracted source texture
  textures/yarn_mask.png            feathered yarn mask (white = yarn)
  textures/base_color_charcoal.png  charcoal-default full texture
  web/yarn_<theme>.jpg              1024px runtime colorway maps (charcoal,
                                    red, scout, tank, arcade, maker, wizard,
                                    music, ghost, pixel, garden)
  knitbit_base_apose_textured.glb   canonical charcoal base (overwritten)

Requires: PIL + numpy (system python), blender on PATH (re-embed step).
"""
import colorsys
import json
import os
import struct
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.join(ROOT, "assets", "3d", "knitbit_base")
TEX_DIR = os.path.join(BASE_DIR, "textures")
WEB_DIR = os.path.join(BASE_DIR, "web")
CANONICAL_GLB = os.path.join(BASE_DIR, "knitbit_base_apose_textured.glb")

# Hue window for the crimson key (degrees) + saturation/value floors.
HUE_LO, HUE_HI = 335.0, 25.0
SAT_MIN, VAL_MIN = 0.30, 0.10

# id -> (label, hex or None-for-source-passthrough, saturation override)
# Hexes match manifest.json themes[*].accent; charcoal matches the DNA.
COLORWAYS = [
    ("charcoal", "Charcoal (default)", "#303136", 0.07),
    ("red",      "Reference Red",      None,      None),   # passthrough
    ("scout",    "Scout Teal",         "#1FA6A0", None),
    ("tank",     "Tank Burnt Orange",  "#C4622D", None),
    ("arcade",   "Arcade Hot Pink",    "#FF2D95", None),
    ("maker",    "Maker Gold",         "#E7B416", None),
    ("wizard",   "Wizard Purple",      "#7A3FC4", None),
    ("music",    "Music Electric Blue","#2D7DFF", None),
    ("ghost",    "Ghost Mint",         "#7FE0D4", 0.45),
    ("pixel",    "Pixel Neon Green",   "#38E655", None),
    ("garden",   "Garden Leaf",        "#4FA82E", None),
]
WEB_SIZE = 1024

# Plating skins: a second recolor axis over the ENAMEL shells (everything the
# yarn mask doesn't own that is bright and desaturated). `prefix` is the web
# filename prefix for that skin's colorway set; capsule keeps the historical
# `yarn_` prefix so existing editors don't break. Porcelain is the mockup-D
# "porcelain tech" look (refs/restyle_d_porcelain_tech.png): near-white pearl
# shells, dark accents untouched.
PLATINGS = [
    ("capsule",   "Capsule (default)", "#D9D5CC", None, None),
    ("porcelain", "Porcelain",         "#F2F1F4", "#F2F1F4", 0.02),
]


def extract_basecolor(glb_path):
    """Return (PIL.Image baseColor, image_name) from a GLB's material 0."""
    data = open(glb_path, "rb").read()
    assert data[:4] == b"glTF", "not a GLB"
    jlen = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + jlen])
    bstart = 20 + jlen + 8
    mat = gltf["materials"][0]
    tex_i = mat["pbrMetallicRoughness"]["baseColorTexture"]["index"]
    img_i = gltf["textures"][tex_i]["source"]
    img = gltf["images"][img_i]
    bv = gltf["bufferViews"][img["bufferView"]]
    off = bstart + bv.get("byteOffset", 0)
    raw = data[off:off + bv["byteLength"]]
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
        f.write(raw)
        tmp = f.name
    pil = Image.open(tmp).convert("RGB")
    pil.load()
    os.unlink(tmp)
    return pil, img.get("name", f"image_{img_i}")


def rgb_to_hsv_arrays(a):
    """a: float32 HxWx3 in [0,1] -> (hue degrees, sat, val) arrays."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1)
    mn = a.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    hue = np.zeros_like(mx)
    m = mx == r
    hue[m] = ((g - b)[m] / d[m]) % 6
    m = mx == g
    hue[m] = (b - r)[m] / d[m] + 2
    m = mx == b
    hue[m] = (r - g)[m] / d[m] + 4
    hue *= 60.0
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return hue, sat, mx


def enhance_yarn(src, mask):
    """Strand-definition pass inside the yarn mask: wide-radius local contrast
    separates the plies, and pixels darker than their neighborhood (the
    grooves between strands) are pushed further down — the braid reads as
    clearly partitioned strands instead of soft lumps."""
    a = np.asarray(src).astype(np.float32) / 255
    m = (np.asarray(mask).astype(np.float32) / 255)[..., None]
    blur = np.asarray(src.filter(ImageFilter.GaussianBlur(6))).astype(np.float32) / 255
    boosted = np.clip(blur + (a - blur) * 2.2, 0, 1)
    groove = np.clip((blur.mean(-1, keepdims=True) - a.mean(-1, keepdims=True)) * 3.0, 0, 1)
    boosted = boosted * (1 - groove * 0.45)
    out = a * (1 - m) + boosted * m
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def extract_normal(glb_path):
    """Return (PIL.Image normal map, found) from material 0, or (None, False)."""
    data = open(glb_path, "rb").read()
    jlen = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + jlen])
    bstart = 20 + jlen + 8
    mat = gltf["materials"][0]
    if "normalTexture" not in mat:
        return None, False
    img_i = gltf["textures"][mat["normalTexture"]["index"]]["source"]
    bv = gltf["bufferViews"][gltf["images"][img_i]["bufferView"]]
    off = bstart + bv.get("byteOffset", 0)
    raw = data[off:off + bv["byteLength"]]
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
        f.write(raw)
        tmp = f.name
    pil = Image.open(tmp).convert("RGB")
    pil.load()
    os.unlink(tmp)
    return pil, True


def amplify_normal(nm, mask, amp=2.0):
    """Steepen normal-map slopes inside the yarn mask so strand grooves catch
    light — the geometry doesn't change, but each ply shades individually."""
    n = np.asarray(nm).astype(np.float32) / 255 * 2 - 1
    m = np.asarray(mask.resize(nm.size, Image.BILINEAR)).astype(np.float32)[..., None] / 255
    n[..., 0] *= (1 + (amp - 1) * m[..., 0])
    n[..., 1] *= (1 + (amp - 1) * m[..., 0])
    n /= np.sqrt((n ** 2).sum(-1, keepdims=True)).clip(1e-6)
    return Image.fromarray(((n + 1) / 2 * 255).astype(np.uint8))


def build_plating_mask(src, yarn_mask):
    """Enamel-shell mask: bright, desaturated pixels OUTSIDE the yarn mask.
    Excludes the dark accents and the screen so a plating recolor keeps the
    two-tone read."""
    a = np.asarray(src).astype(np.float32) / 255
    _, sat, val = rgb_to_hsv_arrays(a)
    ym = np.asarray(yarn_mask).astype(np.float32) / 255
    hard = (sat < 0.30) & (val > 0.35) & (ym < 0.5)
    mask = Image.fromarray((hard * 255).astype(np.uint8))
    mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return mask.filter(ImageFilter.GaussianBlur(1.2))


def build_mask(src):
    """Hue-key crimson -> closed, feathered mask image (L, white = yarn)."""
    a = np.asarray(src).astype(np.float32) / 255.0
    hue, sat, val = rgb_to_hsv_arrays(a)
    hard = (((hue < HUE_HI) | (hue > HUE_LO))
            & (sat > SAT_MIN) & (val > VAL_MIN))
    mask = Image.fromarray((hard * 255).astype(np.uint8))
    # closing: fill pinholes inside braid shadows without growing the border
    mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    # feather so recolor blends at plating edges instead of haloing
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    return mask


def recolor(src, mask, hex_color, sat_override=None):
    """Luminance-preserving recolor of the masked yarn region."""
    a = np.asarray(src).astype(np.float32) / 255.0
    alpha = (np.asarray(mask).astype(np.float32) / 255.0)[..., None]
    _, _, val = rgb_to_hsv_arrays(a)

    tr, tg, tb = (int(hex_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    th, ts, tv = colorsys.rgb_to_hsv(tr, tg, tb)
    if sat_override is not None:
        ts = sat_override

    hard = alpha[..., 0] > 0.5
    v_mean = float(val[hard].mean()) if hard.any() else 0.5
    v_out = np.clip(val * (tv / max(v_mean, 1e-3)), 0.0, 1.0)

    # HSV -> RGB with constant hue/sat, per-pixel value (vectorized)
    c = v_out * ts
    x = c * (1 - abs((th * 6.0) % 2 - 1))
    m = v_out - c
    z = np.zeros_like(c)
    idx = int(th * 6.0) % 6
    rgb_by_sextant = [(c, x, z), (x, c, z), (z, c, x),
                      (z, x, c), (x, z, c), (c, z, x)]
    rr, gg, bb = rgb_by_sextant[idx]
    out = np.stack([rr + m, gg + m, bb + m], axis=-1)

    blended = a * (1 - alpha) + out * alpha
    return Image.fromarray((np.clip(blended, 0, 1) * 255).astype(np.uint8))


REEMBED_TEMPLATE = r"""
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath={src!r})
new_img = bpy.data.images.load({tex!r})
new_img.name = "base_color_charcoal"
nm_path = {nm!r}
new_nm = None
if nm_path:
    new_nm = bpy.data.images.load(nm_path)
    new_nm.name = "normal_yarn_amplified"
    new_nm.colorspace_settings.name = "Non-Color"
replaced = 0
nm_replaced = 0
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image is not None:
            for link in mat.node_tree.links:
                if (link.from_node == node
                        and link.to_socket.name == "Base Color"):
                    node.image = new_img
                    replaced += 1
                if (new_nm is not None and link.from_node == node
                        and link.to_node.type == "NORMAL_MAP"):
                    node.image = new_nm
                    nm_replaced += 1
print(f"[reembed] baseColor nodes replaced: {{replaced}}, normal: {{nm_replaced}}")
assert replaced >= 1, "no Base Color texture node found"
bpy.ops.export_scene.gltf(filepath={dst!r}, export_format="GLB",
                          export_yup=True, export_apply=False)
print("[reembed] wrote", {dst!r})
"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    raw_glb = os.path.abspath(sys.argv[1])
    os.makedirs(TEX_DIR, exist_ok=True)
    os.makedirs(WEB_DIR, exist_ok=True)

    src, name = extract_basecolor(raw_glb)
    print(f"[colorways] baseColor '{name}' {src.size[0]}x{src.size[1]}")
    src.save(os.path.join(TEX_DIR, "base_color_crimson.png"))

    mask = build_mask(src)
    cover = np.asarray(mask).astype(np.float32).mean() / 255.0
    print(f"[colorways] yarn mask coverage: {cover * 100:.1f}%")
    if not 0.05 < cover < 0.60:
        sys.exit(f"[colorways] mask coverage {cover:.2f} outside sane range "
                 "- hue window needs retuning for this texture")
    mask.save(os.path.join(TEX_DIR, "yarn_mask.png"))

    # strand definition BEFORE recoloring, so the charcoal default and every
    # colorway inherit the partitioned-braid look
    src = enhance_yarn(src, mask)
    print("[colorways] yarn strand-definition pass applied")
    nm, has_nm = extract_normal(raw_glb)
    nm_path = None
    if has_nm:
        nm_amp = amplify_normal(nm, mask)
        nm_path = os.path.join(TEX_DIR, "normal_yarn_amplified.png")
        nm_amp.save(nm_path)
        print("[colorways] normal map amplified in yarn region")

    # plating skins: recolor the enamel shells once per plating, then run the
    # yarn colorways over each -> full plating x colorway matrix
    plating_mask = build_plating_mask(src, mask)
    plating_mask.save(os.path.join(TEX_DIR, "plating_mask.png"))
    pcover = np.asarray(plating_mask).astype(np.float32).mean() / 255.0
    print(f"[colorways] plating mask coverage: {pcover * 100:.1f}%")

    cw_entries = []
    plating_entries = []
    for p_id, p_label, p_swatch, p_hex, p_sat in PLATINGS:
        base_tex = src if p_hex is None else recolor(src, plating_mask, p_hex, p_sat)
        prefix = "yarn_" if p_id == "capsule" else f"{p_id}_"
        plating_entries.append(
            {"id": p_id, "label": p_label, "hex": p_swatch, "prefix": prefix})
        for cw_id, label, hex_color, sat in COLORWAYS:
            full = base_tex if hex_color is None else recolor(base_tex, mask, hex_color, sat)
            if p_id == "capsule" and cw_id == "charcoal":
                full.save(os.path.join(TEX_DIR, "base_color_charcoal.png"))
            web = full.resize((WEB_SIZE, WEB_SIZE), Image.LANCZOS)
            fname = f"{prefix}{cw_id}.jpg"
            web.save(os.path.join(WEB_DIR, fname), quality=88)
            if p_id == "capsule":
                cw_entries.append({"id": cw_id, "label": label,
                                   "hex": hex_color or "#C0344B", "file": fname})
        print(f"[colorways] wrote {len(COLORWAYS)} textures for plating '{p_id}' "
              f"(web/{prefix}*.jpg)")

    with open(os.path.join(TEX_DIR, "colorways.json"), "w") as f:
        json.dump({"colorways": cw_entries, "platings": plating_entries}, f, indent=1)
    print(f"[colorways] wrote textures/colorways.json "
          f"({len(cw_entries)} colorways x {len(plating_entries)} platings)")

    # Re-embed charcoal into the canonical GLB via headless Blender.
    script = REEMBED_TEMPLATE.format(
        src=raw_glb,
        tex=os.path.join(TEX_DIR, "base_color_charcoal.png"),
        nm=nm_path,
        dst=CANONICAL_GLB)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(script)
        tmp = f.name
    try:
        r = subprocess.run(
            ["xvfb-run", "-a", "blender", "--background", "--python", tmp],
            capture_output=True, text=True, timeout=600)
        for line in r.stdout.splitlines():
            if "[reembed]" in line or "Error" in line:
                print(line)
        if r.returncode != 0 or "[reembed] wrote" not in r.stdout:
            sys.exit(f"[colorways] blender re-embed FAILED (rc={r.returncode})\n"
                     + r.stderr[-2000:])
    finally:
        os.unlink(tmp)
    size_mb = os.path.getsize(CANONICAL_GLB) / 1e6
    print(f"[colorways] canonical charcoal base written: "
          f"{CANONICAL_GLB} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
