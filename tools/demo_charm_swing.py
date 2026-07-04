#!/usr/bin/env blender --background --python
"""demo_charm_swing.py — visual proof that the belt charm hangs from its hook and
swings as a pendulum.

The belt charm is rigged as a DYNAMIC attachment (build_character.py sets its
node origin to the hook and stamps swing params into glTF extras; the real,
motion-reactive swing is driven by the game runtime). This script bakes a
representative damped-pendulum swing about that hook so the behavior can be seen
without the engine: it keyframes the charm's rotation about its origin, exports
an animated GLB, and renders a filmstrip across one swing.

RUN:
    blender --background --python tools/demo_charm_swing.py

OUT:
    assets/3d/knitbit_base/knitbit_charm_swing_demo.glb        (animated)
    assets/3d/knitbit_base/knitbit_charm_swing_demo.png        (filmstrip)
"""

import bpy
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knitbit_manifest as km  # noqa: E402

ASSET = km.ASSET_DIR
PREVIEW = os.path.join(ASSET, "knitbit_pilot_preview.glb")   # gear charm, origin at hook
OUT_GLB = os.path.join(ASSET, "knitbit_charm_swing_demo.glb")
OUT_STRIP = os.path.join(ASSET, "knitbit_charm_swing_demo.png")
FPS = 24
DUR = 60          # frames (2.5 s)
STRIP_FRAMES = [1, 8, 16, 24, 34, 46]   # frames sampled into the filmstrip


def find_charm():
    return next((o for o in bpy.context.scene.objects
                 if o.type == "MESH" and o.name.startswith("trait_charm")), None)


def keyframe_swing(charm):
    """Damped pendulum about the hook: a decaying sine on X (front-back) plus a
    smaller, phase-shifted Y (side-side), so it reads as a natural swing settling
    to rest. Amplitude/decay mirror the manifest's belt_charm.dynamic feel."""
    charm.rotation_mode = "XYZ"
    base = tuple(charm.rotation_euler)
    amp_x = math.radians(22.0)   # max_angle_deg from the manifest
    amp_y = math.radians(9.0)
    decay = 2.1
    freq = 2.4
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = DUR
    for f in range(1, DUR + 1):
        t = (f - 1) / FPS
        env = math.exp(-decay * t)
        rx = base[0] + amp_x * env * math.sin(2 * math.pi * freq * t)
        ry = base[1] + amp_y * env * math.sin(2 * math.pi * freq * t + 0.7)
        charm.rotation_euler = (rx, ry, base[2])
        charm.keyframe_insert("rotation_euler", frame=f)


def setup_render():
    import mathutils
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x = 420
    sc.render.resolution_y = 520
    cam_d = bpy.data.cameras.new("c"); cam_d.type = "ORTHO"; cam_d.sensor_fit = "VERTICAL"; cam_d.ortho_scale = 0.5
    cam = bpy.data.objects.new("c", cam_d); bpy.context.collection.objects.link(cam); sc.camera = cam
    tgt = mathutils.Vector((-0.203, 0, -0.40)); ang = math.radians(-40)
    cam.location = (tgt.x + 4*math.sin(ang), tgt.y - 4*math.cos(ang), tgt.z + 0.05)
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()


def export_anim():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=OUT_GLB, export_format="GLB", export_yup=True,
                              export_animations=True, export_extras=True, use_selection=False)
    print(f"[swing] exported animated GLB: {OUT_GLB}")


def render_frames(tmpdir):
    """Render the sampled swing frames to PNGs (no PIL — Blender's Python lacks
    it). tools/demo_charm_swing.py is followed by an external assembly step that
    stitches these into OUT_STRIP with system Python's Pillow."""
    for f in STRIP_FRAMES:
        bpy.context.scene.frame_set(f)
        p = os.path.join(tmpdir, f"f{f:03d}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
    print(f"[swing] rendered {len(STRIP_FRAMES)} frames to {tmpdir}: "
          f"{','.join(str(f) for f in STRIP_FRAMES)}")


def main():
    global mathutils
    import mathutils  # noqa: F841
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=PREVIEW)
    charm = find_charm()
    if charm is None:
        print("[swing] ERROR: no trait_charm node found in preview")
        return
    print(f"[swing] charm '{charm.name}' origin(world)="
          f"{tuple(round(v,3) for v in charm.matrix_world.translation)} (should be the hook)")
    keyframe_swing(charm)
    export_anim()
    setup_render()
    tmp = os.environ.get("SWING_FRAMES_DIR", os.path.join(os.path.dirname(OUT_STRIP), "_swingframes"))
    os.makedirs(tmp, exist_ok=True)
    render_frames(tmp)
    print("[swing] done.")


if __name__ == "__main__":
    main()
