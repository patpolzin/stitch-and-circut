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


def in_window(co, region, mirror_x, pad=0.0):
    """pad > 0 grows the window, pad < 0 shrinks it. The split uses a small
    positive pad for the limb parts and a negative one for the core so BOTH
    keep the exact-boundary rim vertices (created by bisect_region_planes) —
    without the overlap, faces straddling the boundary are dropped from both
    parts and the seam shows as a torn ring when a limb part is visible."""
    for w in [region] + list(region.get("extra", ())):
        x_lo, x_hi = w["x_min"], w["x_max"]
        if mirror_x:
            x_lo, x_hi = -x_hi, -x_lo
        z_max = w.get("z_max")
        if (x_lo - pad <= co.x <= x_hi + pad
                and (z_max is None or co.z <= z_max + pad)):
            return True
    return False


def bisect_region_planes(obj, regions):
    """Slice the body with a clean plane at every region-window boundary so
    no face straddles a split boundary (same trick as the assembler's
    hide_mesh_region — coarse yarn triangles otherwise leave ragged seams)."""
    import bmesh
    import mathutils
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    inv = obj.matrix_world.inverted()
    planes = []
    for key in REGION_PARTS:
        for w in [regions[key]] + list(regions[key].get("extra", ())):
            for x in (w["x_min"], w["x_max"]):
                planes.append(((x, 0, 0), (1, 0, 0)))
                planes.append(((-x, 0, 0), (1, 0, 0)))
            if w.get("z_max") is not None:
                planes.append(((0, 0, w["z_max"]), (0, 0, 1)))
    for co_w, no_w in planes:
        bmesh.ops.bisect_plane(
            bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
            plane_co=inv @ mathutils.Vector(co_w),
            plane_no=(inv.to_3x3() @ mathutils.Vector(no_w)),
            clear_inner=False, clear_outer=False)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


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

    # Conform the leg collar to the boot_classic cuff tube BEFORE splitting,
    # so the boots-equipped state shows yarn touching the cuff rim all around
    # (see build_character.conform_collar). The collar verts live above the
    # foot window's z_max and therefore end up in base_core.
    armature = bc.find_armature(objs)
    for instr in km.resolve_loadout(M, {"boots": "boot_classic"}):
        tmp = bc.fit_instruction(instr, body, armature, hidden=None)
        if tmp is not None:
            bc.conform_collar(body, tmp, instr.mirror_x)
            bpy.data.objects.remove(tmp, do_unlink=True)

    regions = M["mesh_regions"]
    bisect_region_planes(body, regions)
    EPS = 5e-4
    parts = ["base_core"]
    for key, (name_l, name_r) in REGION_PARTS.items():
        region = regions[key]
        for name, mirror in ((name_l, False), (name_r, True)):
            part = duplicate(body, name)
            delete_verts(part, lambda co, r=region, mi=mirror: in_window(co, r, mi, pad=EPS))
            parts.append(name)
            print(f"[web] split part '{name}': {len(part.data.vertices)} verts")
    # core = body minus the strict interior of every region window; the
    # boundary rim loop stays in BOTH core and parts so the seam is closed
    def in_any(co):
        for key in REGION_PARTS:
            for mirror in (False, True):
                if in_window(co, regions[key], mirror, pad=-EPS):
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


def write_manifest(parts, piece_meta, face_entries=None):
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
        "face": {"file": "face_screen.glb", "bone": "Head",
                 "expressions": face_entries or []},
        "presets": {name: p["loadout"] for name, p in M["presets"].items()},
    }
    path = os.path.join(WEB, "manifest.web.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[web] wrote {path}")


# face screen overlay: covers the baked-in static face so the editor (and any
# runtime that loads it) can play the animated expression sprites on a live
# texture. Rect probed from the v2 head: the CRT glass bulges forward across
# x +/-0.270, z 0.235..0.660 - calibrated by flooding the overlay canvas magenta in the editor and reading the residuals against the bezel (the glass runs much higher than the eye glyphs suggest). The CRT glass curves back toward the bezel and the raycast follows it.
FACE_RECT = {"x0": -0.310, "x1": 0.310, "z0": 0.210, "z1": 0.600}
FACE_GRID = (44, 34)
FACE_OFFSET = 0.006   # how far the overlay floats in front of the glass
FACE_SRC = os.path.join(os.path.dirname(ASSET), "..", "2d", "knitbit_face", "normalized")


def build_face_screen():
    """Shrinkwrap a UV-gridded plane onto the faceplate glass and export it as
    web/face_screen.glb (attach bone: Head). The editor drives its texture with
    a canvas playing the expression sprites; rounded corners come from the
    canvas alpha, so the mesh itself is a plain rectangle."""
    import math
    from mathutils.bvhtree import BVHTree
    bc.clean_scene()
    objs = bc.import_glb(IDLE_GLB)
    body = bc.find_body(objs)
    deps = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(body, deps)

    nx, nz = FACE_GRID
    r = FACE_RECT
    verts, uvs, faces = [], [], []
    misses = 0
    for j in range(nz):
        for i in range(nx):
            u, w = i / (nx - 1), j / (nz - 1)
            x = r["x0"] + (r["x1"] - r["x0"]) * u
            z = r["z0"] + (r["z1"] - r["z0"]) * w
            hit = bvh.ray_cast(mathutils.Vector((x, -0.9, z)),
                               mathutils.Vector((0, 1, 0)), 1.2)
            if hit[0] is None:
                misses += 1
                y = -0.36
            else:
                y = hit[0].y
            verts.append((x, y - FACE_OFFSET, z))
            uvs.append((u, w))
    for j in range(nz - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces.append((a, a + 1, a + nx + 1, a + nx))

    mesh = bpy.data.meshes.new("face_screen")
    mesh.from_pydata(verts, [], faces)
    uvl = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            uvl.data[li].uv = uvs[mesh.loops[li].vertex_index]
    mesh.update()
    obj = bpy.data.objects.new("face_screen", mesh)
    bpy.context.collection.objects.link(obj)
    mat = bpy.data.materials.new("FaceScreen")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
        bsdf.inputs["Roughness"].default_value = 0.4
    obj.data.materials.append(mat)
    obj["knitbit_attach_bone"] = "Head"
    for o in list(bpy.context.scene.objects):
        if o is not obj:
            bpy.data.objects.remove(o, do_unlink=True)
    export_glb(os.path.join(WEB, "face_screen.glb"), animations=False,
               selection=[obj])
    print(f"[web] face_screen: {nx}x{nz} grid shrinkwrapped "
          f"({misses} ray misses)")


def copy_face_sprites():
    """Copy the normalized expression sprites into web/face/ and return the
    manifest entries. Order matches the BitExpression enum in the game."""
    import shutil
    order = ["idle", "happy", "thinking", "scared", "effort", "starEyes",
             "confused", "lowBattery", "startled", "relieved"]
    out_dir = os.path.join(WEB, "face")
    os.makedirs(out_dir, exist_ok=True)
    entries = []
    for name in order:
        src = os.path.join(FACE_SRC, name + ".png")
        if not os.path.exists(src):
            print(f"[web] WARNING: face sprite missing: {src}")
            continue
        shutil.copyfile(src, os.path.join(out_dir, name + ".png"))
        entries.append({"id": name, "file": f"face/{name}.png"})
    print(f"[web] face sprites: {len(entries)} copied")
    return entries


def main():
    global mathutils
    import mathutils  # noqa: F841
    bc.mathutils = mathutils
    os.makedirs(WEB, exist_ok=True)
    parts = build_base()
    piece_meta = build_pieces()
    build_face_screen()
    face_entries = copy_face_sprites()
    write_manifest(parts, piece_meta, face_entries)
    print("[web] done.")


if __name__ == "__main__":
    main()
