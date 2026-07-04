#!/usr/bin/env blender --background --python
"""
fit_traits.py — Attach the pilot trait props to the rigged KnitBit base's sockets
and export assembled preview GLBs (docs/KnitBit-Base-Spec.md build-order step 4).

WHY THIS EXISTS
    Proves the socket system from docs/KnitBit-Base-Spec.md (section 4) actually
    works before building the full ~300-trait library. The pilot table in the
    spec has 3 options per slot; they are assembled here as three full-body
    builds, one option per slot each:

      pilot      Phase A picks (antenna pair, helmet panel, chest icon,
                 belt charm, backpack)
      variant_b  Phase B "tech" set: scout-camera antenna pair, smooth panel,
                 wrench chest icon, coin charm, headphones
      variant_c  Phase B "garden" set: leaf antenna pair, yarn patch panel,
                 leaf chest icon, flower charm, watering can (first use of a
                 hand-grip socket)

INPUT   assets/3d/knitbit_base/knitbit_base_rigged.glb        (base + armature + sockets)
        assets/3d/knitbit_base/traits/pilot/*.glb              (15 pilot props)
OUTPUT  assets/3d/knitbit_base/knitbit_pilot_preview[_b|_c].glb
        assets/3d/knitbit_base/knitbit_pilot_preview[_b|_c]_front.png
        assets/3d/knitbit_base/knitbit_pilot_preview[_b|_c]_side.png

RUN:
    blender --background --python tools/fit_traits.py

NOTES
    - Props are known-off-model in one way: the base mesh's head already has
      antenna nubs sculpted into it (baked in from the source photo), so the
      antenna props will visually double up there. This pilot is about proving
      socket *placement mechanics*, not final art polish — see the spec's
      section 4/6 notes on this.
    - Each prop is a plain (non-skinned) mesh, so it's simply object-parented to
      its target socket_<name> empty — no repeat of the base rig's skin/exporter
      crash class, since these never touch skinning at all.
    - PROPS config below holds per-prop target size (fraction of character
      height) and an optional rotation hint. Both are the first things to tune
      if a render shows a prop mis-scaled or mis-oriented.
"""

import bpy
import os
import math


def _repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


ASSET_DIR = os.path.join(_repo_root(), "assets/3d/knitbit_base")
BASE_GLB = os.path.join(ASSET_DIR, "knitbit_base_rigged.glb")
TRAIT_DIR = os.path.join(ASSET_DIR, "traits/pilot")

# CHAR_HEIGHT/HW come from the base mesh bounds printed by tools/rig_knitbit.py
# (min=(-0.738,-0.371,-0.957) max=(0.733,0.373,0.954), Blender Z-up).
CHAR_HEIGHT = 1.911
HW = 0.735

# name -> (source glb, socket empty name, target size as fraction of CHAR_HEIGHT,
#          rotation hint in degrees (x, y, z), mirror-x,
#          local offset (x, y, z) in socket space as fractions of CHAR_HEIGHT)
# The offset surface-mounts props whose socket sits at the mesh surface apex —
# props are scaled about their center, so without it half the prop floats
# outside the body (the "helmet on top of the helmet" bug on head_top_center).
# DESIGN RULE (user-confirmed): the oversized monitor head IS the helmet, with
# the faceplate as its front. head_top_center carries only thin low-profile
# surface details — never helmet/dome-shaped geometry.
PROPS_PILOT = {
    "antenna_left": ("antenna.glb", "socket_head_left_antenna", 0.10, (0, 0, 0), False, (0, 0, 0)),
    "antenna_right": ("antenna.glb", "socket_head_right_antenna", 0.10, (0, 0, 0), True, (0, 0, 0)),
    # Flat access-panel plate lying on the head crown: modest plate size, small
    # sink so the plate edges bite into the curved crown instead of hovering.
    # (socket_head_top_center itself now sits at the sampled TRUE crown height —
    # see crown_height() in rig_knitbit.py — not the bbox top/antenna tips.)
    # chest_icon's old (90,0,0) and backpack's old (0,0,180) hints predate the
    # quaternion fix in fit_prop — they never applied, and both props render
    # correctly in their imported orientation, so they are now explicit (0,0,0).
    "helmet_panel": ("helmet_panel.glb", "socket_head_top_center", 0.15, (0, 0, 0), False, (0, 0, -0.01)),
    "chest_icon": ("chest_icon.glb", "socket_chest_center", 0.11, (0, 0, 0), False, (0, 0, 0)),
    "belt_charm": ("belt_charm.glb", "socket_belt_front", 0.09, (0, 0, 0), False, (0, 0, 0)),
    "backpack": ("backpack.glb", "socket_back_center", 0.42, (0, 0, 0), False, (0, 0, 0)),
}

# Phase B "tech" set. The headphones are one mesh spanning both ear cups, so
# they mount as a single unit over the crown (head_top_center) rather than as
# separate cups on the side sockets — an arched band is a low-profile topper,
# not helmet/dome geometry, so the section 1 rule holds.
PROPS_VARIANT_B = {
    # The headphone band crosses the crown at antenna height, so the two props
    # are separated on two fronts: the scout antennae get a 20-deg outward (Y)
    # lean (symmetric under the mirrored -x scale, unlike an X tilt whose sense
    # the mirror flips) to move their stalks off the band's descending legs, and
    # the band itself is raised and widened below (see headphones) so its arch
    # clears the antenna tips. 0.13 (vs the pilot's 0.10) also lifts the camera
    # modules clear of the base's baked-in antenna nubs.
    "antenna_left": ("antenna_scout.glb", "socket_head_left_antenna", 0.13, (0, 20, 0), False, (0, 0, 0)),
    "antenna_right": ("antenna_scout.glb", "socket_head_right_antenna", 0.13, (0, 20, 0), True, (0, 0, 0)),
    "helmet_panel": ("panel_smooth.glb", "socket_head_top_center", 0.15, (0, 0, 0), False, (0, 0, -0.01)),
    "chest_icon": ("chest_wrench.glb", "socket_chest_center", 0.11, (0, 0, 0), False, (0, 0, 0)),
    "belt_charm": ("charm_coin.glb", "socket_belt_front", 0.09, (0, 0, 0), False, (0, 0, 0)),
    # 0.62 + a higher mount (z offset -0.11 vs -0.18): a bigger band arcs wider
    # around the head and its apex + legs ride above the outward-leaned antenna
    # tips instead of slicing through them.
    "headphones": ("headphones.glb", "socket_head_top_center", 0.62, (0, 0, 0), False, (0, 0, -0.11)),
}

# Phase B "garden" set. The watering can is the first handheld: it parents to
# the right hand-grip socket instead of a surface socket.
PROPS_VARIANT_C = {
    # 0.13 (vs the pilot's 0.10) so the leaf tips clear the base's baked-in
    # antenna nubs instead of hiding inside them.
    "antenna_left": ("antenna_leaf.glb", "socket_head_left_antenna", 0.13, (0, 0, 0), False, (0, 0, 0)),
    "antenna_right": ("antenna_leaf.glb", "socket_head_right_antenna", 0.13, (0, 0, 0), True, (0, 0, 0)),
    "helmet_panel": ("panel_yarn.glb", "socket_head_top_center", 0.15, (0, 0, 0), False, (0, 0, -0.01)),
    # This badge reconstructed lying flat (emblem up) unlike the wrench badge,
    # which imports already standing: +90 X pitches the emblem to face front —
    # verified against -90/180 (they show the plain back or an edge).
    "chest_icon": ("chest_leaf.glb", "socket_chest_center", 0.11, (90, 0, 0), False, (0, 0, 0)),
    "belt_charm": ("charm_flower.glb", "socket_belt_front", 0.09, (0, 0, 0), False, (0, 0, 0)),
    "watering_can": ("watering_can.glb", "socket_right_hand_grip", 0.16, (0, 0, 0), False, (0, 0, 0)),
}

# build name -> (props table, output file stem)
BUILDS = {
    "pilot": (PROPS_PILOT, "knitbit_pilot_preview"),
    "variant_b": (PROPS_VARIANT_B, "knitbit_pilot_preview_b"),
    "variant_c": (PROPS_VARIANT_C, "knitbit_pilot_preview_c"),
}


def clean_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.armatures, bpy.data.objects):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def import_glb(path):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.context.scene.objects if o not in before]


def find_socket(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        print(f"[fit] WARNING: socket '{name}' not found in base scene")
    return obj


def longest_dimension(obj):
    coords = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    return max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def fit_prop(prop_name, filename, socket_name, target_frac, rot_deg, mirror_x, offset_frac):
    socket = find_socket(socket_name)
    if socket is None:
        return None

    path = os.path.join(TRAIT_DIR, filename)
    objs = import_glb(path)
    meshes = [o for o in objs if o.type == "MESH"]
    if not meshes:
        print(f"[fit] WARNING: no mesh imported from {filename}")
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    prop = bpy.context.view_layer.objects.active
    prop.name = f"trait_{prop_name}"

    dim = longest_dimension(prop)
    target = target_frac * CHAR_HEIGHT
    scale = (target / dim) if dim > 1e-6 else 1.0
    if mirror_x:
        scale = -scale

    prop.parent = socket
    prop.parent_type = "OBJECT"
    # Deliberately leave matrix_parent_inverse at its default identity: we WANT
    # the socket's world transform to apply on top of the prop's local
    # loc/rot/scale below (matrix_world = socket.matrix_world @ local_matrix).
    # Setting matrix_parent_inverse = socket.matrix_world.inverted() (the usual
    # "parent without moving the child" idiom) would cancel that out and drop
    # every prop at the scene's absolute origin instead of at its socket.
    prop.location = tuple(f * CHAR_HEIGHT for f in offset_frac)
    # The glTF importer leaves objects in QUATERNION rotation mode, where
    # assigning rotation_euler is silently ignored — every rot hint before this
    # fix was a no-op and props simply kept their imported orientation. Compose
    # the hint ON TOP of that imported orientation via quaternions instead:
    # hint (0,0,0) keeps a prop exactly as it imports (the old de-facto
    # behavior), and a nonzero hint now actually turns the prop.
    base_q = prop.matrix_basis.to_quaternion()
    prop.rotation_mode = "QUATERNION"
    hint_q = mathutils.Euler(tuple(math.radians(d) for d in rot_deg)).to_quaternion()
    prop.rotation_quaternion = hint_q @ base_q
    prop.scale = (scale, abs(scale), abs(scale))
    bpy.context.view_layer.update()
    sock_pos = tuple(round(v, 3) for v in socket.matrix_world.translation)
    prop_pos = tuple(round(v, 3) for v in prop.matrix_world.translation)
    print(f"[fit] {prop_name}: dim={dim:.3f} -> scale={scale:.3f} @ socket '{socket_name}' "
          f"socket_world={sock_pos} prop_world={prop_pos}")
    return prop


def setup_render(engine="BLENDER_EEVEE_NEXT"):
    scene = bpy.context.scene
    try:
        scene.render.engine = engine
    except TypeError:
        print(f"[fit] render engine '{engine}' unavailable, falling back to BLENDER_WORKBENCH")
        scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1200
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("PreviewWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.55, 0.45, 0.38, 1)  # neutral warm studio tone
        bg.inputs[1].default_value = 1.0
    scene.world = world

    light = bpy.data.lights.new("KeyLight", type="SUN")
    light.energy = 3.0
    light_obj = bpy.data.objects.new("KeyLight", light)
    bpy.context.collection.objects.link(light_obj)
    light_obj.rotation_euler = (math.radians(55), 0, math.radians(35))

    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.type = "ORTHO"
    cam_data.sensor_fit = "VERTICAL"
    # Ortho scale guarantees full-body framing regardless of camera distance —
    # more reliable than tuning perspective FOV/distance by hand.
    cam_data.ortho_scale = CHAR_HEIGHT * 1.3
    cam_obj = bpy.data.objects.new("PreviewCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    print(f"[fit] camera: type={cam_data.type} sensor_fit={cam_data.sensor_fit} "
          f"ortho_scale={cam_data.ortho_scale:.3f} res={scene.render.resolution_x}x{scene.render.resolution_y}")
    return cam_obj


# height_frac is relative to the mesh center (z=0): the base spans roughly
# -0.96..0.95, so aiming at 0 with ortho_scale 1.3*CHAR_HEIGHT frames the whole
# body. (The original 0.42 aimed at the chest and cropped everything below the
# belt out of frame — belt charms and handheld props were unverifiable.)
def render_view(cam_obj, angle_deg, out_path, distance=4.0, height_frac=0.0):
    rad = math.radians(angle_deg)
    x = distance * math.sin(rad)
    y = -distance * math.cos(rad)
    z = CHAR_HEIGHT * height_frac
    cam_obj.location = (x, y, z)
    direction = mathutils.Vector((0, 0, CHAR_HEIGHT * height_frac)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    print(f"[fit] cam loc={tuple(round(v,3) for v in cam_obj.location)} "
          f"rot={tuple(round(math.degrees(v),1) for v in cam_obj.rotation_euler)}")
    bpy.context.scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"[fit] rendered: {out_path}")


def export(out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_skins=True,
        export_animations=False,
        export_extras=True,
        use_selection=False,
    )
    print(f"[fit] exported: {out_path}")


def build_preview(build_name, props, out_stem):
    print(f"[fit] === build '{build_name}' -> {out_stem} ===")
    clean_scene()
    import_glb(BASE_GLB)

    fitted = []
    for prop_name, (filename, socket_name, target_frac, rot_deg, mirror_x, offset_frac) in props.items():
        result = fit_prop(prop_name, filename, socket_name, target_frac, rot_deg, mirror_x, offset_frac)
        if result:
            fitted.append(prop_name)
    print(f"[fit] fitted {len(fitted)}/{len(props)} props: {fitted}")

    export(os.path.join(ASSET_DIR, out_stem + ".glb"))

    cam = setup_render()
    render_view(cam, angle_deg=25, out_path=os.path.join(ASSET_DIR, out_stem + "_front.png"))
    render_view(cam, angle_deg=90, out_path=os.path.join(ASSET_DIR, out_stem + "_side.png"))
    return fitted


def main():
    global mathutils
    import mathutils  # noqa: F824 (bpy module, only importable once Blender is running)

    import sys
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    selected = argv or list(BUILDS)

    print(f"[fit] base: {BASE_GLB}")
    for build_name in selected:
        props, out_stem = BUILDS[build_name]
        build_preview(build_name, props, out_stem)

    print("[fit] done.")


if __name__ == "__main__":
    main()
