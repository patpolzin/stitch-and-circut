#!/usr/bin/env blender --background --python
"""export_web_bundle.py — build the web-optimized character-editor bundle.

The committed source assets are far too heavy for a live browser editor (the
raw hand piece alone is 32k verts + ~13.5 MB of textures; a full assembled GLB
is ~95 MB). This exporter produces `assets/3d/knitbit_base/web/`:

- base.glb — the Idle-animated rigged base with the body SPLIT into named,
  individually toggleable parts (base_core, base_hand_l/r, base_foot_l/r,
  same skinning, same mesh_regions windows the mesh-swap hide uses). The
  editor equips boots/hands by toggling part visibility — no client-side
  vertex surgery. Textures capped at 1024.
- piece_<trait_id>.glb — every manifest trait, FIT (exact build_character
  placement), baked to world space, decimated to a web-friendly poly count,
  textures capped at 512, with knitbit_attach_bone/knitbit_hides extras on
  each mesh node. The editor loads a piece and `bone.attach()`es each mesh
  to its named bone, so it rides the skeleton and every animation for free.
- manifest.web.json — everything the editor needs: slots, traits, per-piece
  attachments, hideable base parts, theme colors, animation name.

RUN:
    blender --background --python tools/export_web_bundle.py
"""

import bpy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knitbit_manifest as km  # noqa: E402
import build_character as bc  # noqa: E402

M = km.load()
ASSET = km.ASSET_DIR
WEB = os.path.join(ASSET, "web")
IDLE_GLB = os.path.join(ASSET, "knitbit_base_idle.glb")

BASE_TEX = 1024
PIECE_TEX = 512
PIECE_TRIS = 9000

REGION_PARTS = {"hand": ("base_hand_l", "base_hand_r"),
                "foot": ("base_foot_l", "base_foot_r")}


def in_window(co, region, mirror_x):
    x_lo, x_hi = region["x_min"], region["x_max"]
    if mirror_x:
        x_lo, x_hi = -x_hi, -x_lo
    z_max = region.get("z_max")
    return x_lo <= co.x <= x_hi and (z_max is None or co.z <= z_max)


def delete_verts(obj, keep):
    """Delete every vertex of obj for which keep(world_co) is False."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    doomed = [v for v in bm.verts if not keep(obj.matrix_world @ v.co)]
    bmesh.ops.delete(bm, geom=doomed, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def duplicate(obj, name):
    dup = obj.copy()
    dup.data = obj.data.copy()
    dup.name = name
    bpy.context.collection.objects.link(dup)
    return dup


def shrink_images(cap):
    for img in bpy.data.images:
        w, h = img.size
        if w > cap or h > cap:
            img.scale(min(w, cap), min(h, cap))
            print(f"[web] image '{img.name}' {w}x{h} -> {tuple(img.size)}")


def decimate(obj, target_tris):
    tris = len(obj.data.polygons)
    if tris <= target_tris:
        return
    mod = obj.modifiers.new("Decim", "DECIMATE")
    mod.ratio = target_tris / tris
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print(f"[web] decimated '{obj.name}' {tris} -> {len(obj.data.polygons)} tris")


def export_glb(path, animations, selection=None):
    bpy.ops.object.select_all(action="DESELECT")
    if selection:
        for o in selection:
            o.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_skins=True,
        export_animations=animations,
        export_extras=True,
        use_selection=bool(selection),
    )
    print(f"[web] exported {path} ({os.path.getsize(path)/1e6:.1f} MB)")


def build_base():
    bc.clean_scene()
    objs = bc.import_glb(IDLE_GLB)
    body = bc.find_body(objs)
    body.name = "base_core"

    regions = M["mesh_regions"]
    parts = ["base_core"]
    for key, (name_l, name_r) in REGION_PARTS.items():
        region = regions[key]
        for name, mirror in ((name_l, False), (name_r, True)):
            part = duplicate(body, name)
            delete_verts(part, lambda co, r=region, mi=mirror: in_window(co, r, mi))
            parts.append(name)
            print(f"[web] split part '{name}': {len(part.data.vertices)} verts")
    # core = body minus every region window
    def in_any(co):
        for key in REGION_PARTS:
            for mirror in (False, True):
                if in_window(co, regions[key], mirror):
                    return True
        return False
    delete_verts(body, lambda co: not in_any(co))
    print(f"[web] base_core: {len(body.data.vertices)} verts")

    shrink_images(BASE_TEX)
    export_glb(os.path.join(WEB, "base.glb"), animations=True)
    return parts


def build_pieces():
    """Fit every trait onto a fresh base, bake each prop to world space, stamp
    editor extras, optimize, and export one piece file per trait."""
    bc.clean_scene()
    objs = bc.import_glb(bc.BASE_GLB)
    body = bc.find_body(objs)
    armature = bc.find_armature(objs)
    base_names = {o.name for o in bpy.context.scene.objects}

    piece_meta = {}
    for trait in M["traits"]:
        instrs = km.resolve_loadout(M, {trait["slot"]: trait["id"]})
        attachments = []
        meshes = []
        for instr in instrs:
            # hidden=None -> skip base vertex hiding; the base is discarded here
            prop = bc.fit_instruction(instr, body, armature, hidden=None)
            if not prop:
                continue
            bone = bc.resolve_attach_bone(instr)
            # For the dynamic charm the editor needs the hook pivot in world
            # space (the baked mesh no longer carries a meaningful origin).
            if instr.dynamic:
                prop["knitbit_pivot_pos"] = list(prop.matrix_world.translation)
            bc.bake_world(prop)
            prop["knitbit_attach_bone"] = bone or ""
            attachments.append({"node": prop.name, "bone": bone})
            meshes.append(prop)
        hides = []
        if trait.get("hides"):
            hides = list(REGION_PARTS.get(trait["hides"], ()))
        piece_meta[trait["id"]] = {"attachments": attachments, "hides": hides,
                                   "meshes": meshes}

    # everything is fitted; drop the base so only pieces remain, then optimize
    for o in list(bpy.context.scene.objects):
        if o.name in base_names:
            bpy.data.objects.remove(o, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.images, bpy.data.materials):
        for b in list(block):
            if b.users == 0:
                block.remove(b)
    shrink_images(PIECE_TEX)
    for tid, meta in piece_meta.items():
        for mesh_obj in meta["meshes"]:
            decimate(mesh_obj, PIECE_TRIS)

    for tid, meta in piece_meta.items():
        export_glb(os.path.join(WEB, f"piece_{tid}.glb"), animations=False,
                   selection=meta["meshes"])
    return piece_meta


def write_manifest(parts, piece_meta):
    slots = {}
    for key, slot in M["slots"].items():
        slots[key] = {"label": slot.get("label", key)}
        if slot.get("dynamic"):
            dyn = {k: v for k, v in slot["dynamic"].items() if k != "comment"}
            slots[key]["dynamic"] = dyn
    traits = []
    for t in M["traits"]:
        meta = piece_meta[t["id"]]
        traits.append({
            "id": t["id"], "slot": t["slot"], "label": t.get("label", t["id"]),
            "theme": t.get("theme", "neutral"),
            "file": f"piece_{t['id']}.glb",
            "attachments": [{"node": a["node"], "bone": a["bone"]}
                            for a in meta["attachments"]],
            "hides": meta["hides"],
        })
    themes = {k: v for k, v in M["themes"].items() if not k.startswith("_")}
    # yarn colorways: produced by tools/make_yarn_colorways.py, which drops the
    # runtime textures next to the bundle (web/yarn_<id>.jpg) and the entry
    # list in textures/colorways.json. Optional so the export still works on a
    # checkout that never ran the colorway tool.
    colorways = []
    cw_path = os.path.join(ASSET, "textures", "colorways.json")
    if os.path.exists(cw_path):
        with open(cw_path) as f:
            colorways = json.load(f)
        missing = [c["file"] for c in colorways
                   if not os.path.exists(os.path.join(WEB, c["file"]))]
        if missing:
            print(f"[web] WARNING: colorway textures missing: {missing}")
    out = {
        "base": {"file": "base.glb", "animation": "Idle",
                 "parts": parts, "char_height": M["base"]["char_height"]},
        "slots": slots,
        "traits": traits,
        "themes": themes,
        "colorways": colorways,
        "presets": {name: p["loadout"] for name, p in M["presets"].items()},
    }
    path = os.path.join(WEB, "manifest.web.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[web] wrote {path}")


def main():
    global mathutils
    import mathutils  # noqa: F841
    bc.mathutils = mathutils
    os.makedirs(WEB, exist_ok=True)
    parts = build_base()
    piece_meta = build_pieces()
    write_manifest(parts, piece_meta)
    print("[web] done.")


if __name__ == "__main__":
    main()
