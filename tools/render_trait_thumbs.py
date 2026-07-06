#!/usr/bin/env blender --background --python
"""render_trait_thumbs.py — render every manifest trait (and the base) in
isolation to a consistent square thumbnail, for the Master Trait Diagram.

Manifest-driven: one thumb per trait id, framed the same way on a light neutral
background, so tools/build_master_sheet.py can compose them into the category
sheet. Re-run whenever the trait library changes.

RUN:
    blender --background --python tools/render_trait_thumbs.py
OUT:
    assets/3d/knitbit_base/thumbs/<trait_id>.png   (+ base.png)
"""

import bpy
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knitbit_manifest as km  # noqa: E402

M = km.load()
ASSET = km.ASSET_DIR
OUT = os.path.join(ASSET, "thumbs")
RES = 400


def clean():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blk in (bpy.data.meshes, bpy.data.objects, bpy.data.cameras, bpy.data.lights):
        for b in list(blk):
            if b.users == 0:
                blk.remove(b)


def frame_and_render(path, three_quarter=True):
    import mathutils
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        return
    coords = [o.matrix_world @ mathutils.Vector(c) for o in meshes for c in o.bound_box]
    lo = mathutils.Vector((min(c.x for c in coords), min(c.y for c in coords), min(c.z for c in coords)))
    hi = mathutils.Vector((max(c.x for c in coords), max(c.y for c in coords), max(c.z for c in coords)))
    center = (lo + hi) / 2
    span = max((hi - lo).x, (hi - lo).y, (hi - lo).z)

    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x = RES
    sc.render.resolution_y = RES
    sc.render.film_transparent = True  # transparent bg -> composited on the sheet

    cam_d = bpy.data.cameras.new("c"); cam_d.type = "ORTHO"; cam_d.sensor_fit = "AUTO"
    cam_d.ortho_scale = span * 1.25
    cam = bpy.data.objects.new("c", cam_d); bpy.context.collection.objects.link(cam); sc.camera = cam
    ang = math.radians(28) if three_quarter else 0.0
    elev = math.radians(14)
    dist = span * 3 + 2
    cam.location = (center.x + dist*math.sin(ang)*math.cos(elev),
                    center.y - dist*math.cos(ang)*math.cos(elev),
                    center.z + dist*math.sin(elev))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()

    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    global mathutils
    import mathutils  # noqa: F841
    os.makedirs(OUT, exist_ok=True)

    # base
    clean()
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSET, M["base"]["rig"]))
    # hide socket empties / armature; keep mesh only (workbench ignores empties anyway)
    frame_and_render(os.path.join(OUT, "base.png"))
    print("[thumbs] base")

    for t in M["traits"]:
        clean()
        bpy.ops.import_scene.gltf(filepath=os.path.join(ASSET, t["file"]))
        frame_and_render(os.path.join(OUT, t["id"] + ".png"))
        print(f"[thumbs] {t['id']}")
    print("[thumbs] done.")


if __name__ == "__main__":
    main()
