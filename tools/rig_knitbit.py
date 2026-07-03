#!/usr/bin/env blender --background --python
"""
rig_knitbit.py — Auto-rig the neutral base KnitBit ("Bit") in Blender.

WHY THIS EXISTS
    Higgsfield/Meshy auto-rigging fails on KnitBit's chibi proportions (oversized
    head + short armored limbs fused to a wide torso). This script builds the
    canonical humanoid skeleton from docs/KnitBit-Base-Spec.md (section 3), skins
    the mesh with automatic weights, and adds the named attachment sockets
    (spec section 4) — producing a real rigged GLB to build the trait system on.

INPUT   assets/3d/knitbit_base/knitbit_base_apose_textured.glb   (canonical A-pose)
OUTPUT  assets/3d/knitbit_base/knitbit_base_rigged.glb
        assets/3d/knitbit_base/knitbit_base_idle.glb   (same rig + a procedural idle clip)

RUN:
    blender --background --python tools/rig_knitbit.py
    # optional overrides:
    blender --background --python tools/rig_knitbit.py -- \
        --in path/to/input.glb --out path/to/output.glb

    Requires Blender's bundled Python to have numpy (needed by the glTF I/O addon):
    apt-get install python3-numpy   (if using the apt 'blender' package on Debian/Ubuntu,
    which links the system Python rather than bundling its own).

NOTES
    - Bone positions are derived from the mesh bounding box using proportion
      fractions in LANDMARKS below. They are good estimates for a chibi biped;
      nudge them in Blender's edit mode if a joint deforms poorly, then re-export.
    - Skinning tries automatic (heat) weights first, falls back to envelope
      weights if heat fails broadly (common on hard-surface meshes with many
      disconnected shells — screws, bolts, panel trim — which the heat solver
      can't bridge), then does a rigid nearest-bone assignment for any vertex
      still unweighted. See skin() for details and why the last step also
      works around a Blender 4.0.2 glTF-exporter crash (add_neutral_bones).
    - Bone names follow the VRM/Mixamo-friendly Hips/Spine/Chest/Neck/Head +
      .L/.R limb convention so animation retargeting stays clean.
    - Socket empties are object-parented to the armature (not bone-parented —
      that combination also crashes the exporter) with the intended bone name
      stored as a custom property (`attach_bone`, exported as glTF `extras`).
      Re-parent to the live bone in-engine/downstream for animated attachment.
"""

import bpy
import sys
import os
# `Vector`/`Matrix` come from Blender's `mathutils`, bound at module load below
# (see `_get_vector()`); they are unavailable until bpy is running.


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

def _repo_root():
    # tools/rig_knitbit.py -> repo root is one level up
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)

DEFAULT_IN = os.path.join(_repo_root(), "assets/3d/knitbit_base/knitbit_base_apose_textured.glb")
DEFAULT_OUT = os.path.join(_repo_root(), "assets/3d/knitbit_base/knitbit_base_rigged.glb")
DEFAULT_IDLE_OUT = os.path.join(_repo_root(), "assets/3d/knitbit_base/knitbit_base_idle.glb")
IDLE_FPS = 30
IDLE_FRAMES = 30  # 1-second loop

# Approximate real-world height (m). KnitBit "feels" ~4ft. Only affects scale hints.
HEIGHT_METERS = 1.2

# Vertical landmarks as fractions of total height (0 = feet bottom, 1 = head top).
# Tuned for chibi proportions (short legs, oversized head). Tweak as needed.
LANDMARKS = {
    "foot":       0.00,
    "ankle":      0.05,
    "knee":       0.18,
    "hip":        0.30,
    "spine":      0.38,
    "chest":      0.46,
    "shoulder":   0.50,
    "neck":       0.54,
    "head":       0.60,   # neck/head joint
    "head_top":   1.00,
}

# Horizontal fractions of half-width (hw). +x = character LEFT (Blender .L).
HW = {
    "leg_x":      0.28,   # leg centre offset
    "shoulder_x": 0.55,   # shoulder joint from spine
    "elbow_x":    0.80,   # A-pose elbow (down & out)
    "wrist_x":    0.94,
    "hand_x":     1.00,
}


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def _get_vector():
    from mathutils import Vector as V
    return V

Vector = _get_vector()  # noqa: F811  (override the shim import above)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    in_path, out_path, idle_out_path = DEFAULT_IN, DEFAULT_OUT, DEFAULT_IDLE_OUT
    it = iter(argv)
    for a in it:
        if a == "--in":
            in_path = next(it)
        elif a == "--out":
            out_path = next(it)
        elif a == "--idle-out":
            idle_out_path = next(it)
    return in_path, out_path, idle_out_path


def clean_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.armatures, bpy.data.objects):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def import_mesh(path):
    if not os.path.exists(path):
        raise SystemExit(f"[rig] input GLB not found: {path}")
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise SystemExit("[rig] no mesh found in imported GLB")
    # Join in case the import produced multiple parts.
    bpy.ops.object.select_all(action="DESELECT")
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = "KnitBit"
    return obj


def mesh_bounds(obj):
    """World-space min/max corners after glTF's Y-up -> Z-up import."""
    coords = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


# --------------------------------------------------------------------------- #
# Armature
# --------------------------------------------------------------------------- #

def build_armature(mn, mx):
    height = mx.z - mn.z
    hw = (mx.x - mn.x) / 2.0
    depth = mx.y - mn.y
    cx = (mn.x + mx.x) / 2.0
    cy = (mn.y + mx.y) / 2.0
    front_y = cy - depth * 0.5   # character front (feet/face point here)

    def z(t):
        return mn.z + t * height

    def P(x_frac_hw, t, y=None):
        return Vector((cx + x_frac_hw * hw, cy if y is None else y, z(t)))

    L = LANDMARKS

    arm = bpy.data.armatures.new("KnitBitArmature")
    arm_obj = bpy.data.objects.new("KnitBitArmature", arm)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones

    def bone(name, head, tail, parent=None, connect=False):
        b = eb.new(name)
        b.head = head
        b.tail = tail
        if parent:
            b.parent = eb[parent]
            b.use_connect = connect
        return b

    # Spine chain (centered)
    bone("Root",  P(0, L["foot"]),  P(0, L["hip"]))
    bone("Hips",  P(0, L["hip"]),   P(0, L["spine"]), "Root")
    bone("Spine", P(0, L["spine"]), P(0, L["chest"]), "Hips", True)
    bone("Chest", P(0, L["chest"]), P(0, L["neck"]),  "Spine", True)
    bone("Neck",  P(0, L["neck"]),  P(0, L["head"]),  "Chest", True)
    bone("Head",  P(0, L["head"]),  P(0, L["head"] + 0.30 * (1 - L["head"]) + 0.10, None),
         "Neck", True)
    # Head tail a bit into the big head volume:
    eb["Head"].tail = P(0, min(0.80, L["head"] + 0.20))

    # Limbs, built for +x (left) then mirrored to -x (right).
    for side, s in (("L", 1.0), ("R", -1.0)):
        conn = f".{side}"
        # Arm (A-pose: down & out)
        bone(f"Shoulder{conn}",
             P(0.06 * s, L["shoulder"]),
             P(HW["shoulder_x"] * s, L["shoulder"]), "Chest")
        bone(f"UpperArm{conn}",
             P(HW["shoulder_x"] * s, L["shoulder"]),
             P(HW["elbow_x"] * s, L["spine"]), f"Shoulder{conn}", True)
        bone(f"LowerArm{conn}",
             P(HW["elbow_x"] * s, L["spine"]),
             P(HW["wrist_x"] * s, L["hip"] + 0.01), f"UpperArm{conn}", True)
        bone(f"Hand{conn}",
             P(HW["wrist_x"] * s, L["hip"] + 0.01),
             P(HW["hand_x"] * s, L["hip"] - 0.03), f"LowerArm{conn}", True)
        # Leg
        bone(f"UpperLeg{conn}",
             P(HW["leg_x"] * s, L["hip"]),
             P(HW["leg_x"] * s, L["knee"]), "Hips")
        bone(f"LowerLeg{conn}",
             P(HW["leg_x"] * s, L["knee"]),
             P(HW["leg_x"] * s, L["ankle"]), f"UpperLeg{conn}", True)
        bone(f"Foot{conn}",
             P(HW["leg_x"] * s, L["ankle"]),
             Vector((cx + HW["leg_x"] * s * hw, front_y, z(L["foot"]) + 0.02)),
             f"LowerLeg{conn}", True)

    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj, (mn, mx, front_y)


# --------------------------------------------------------------------------- #
# Skinning
# --------------------------------------------------------------------------- #

def skin(mesh_obj, arm_obj, hw):
    def do_parent(ptype):
        bpy.ops.object.select_all(action="DESELECT")
        mesh_obj.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type=ptype)

    total = len(mesh_obj.data.vertices)

    # Attempt 1: automatic (heat) weights. Works well on connected, mostly-manifold
    # meshes but can fail broadly on hard-surface meshes with many disconnected
    # shells (screws, bolts, panel trim) — common in AI-generated sculpts.
    do_parent("ARMATURE_AUTO")
    unweighted = count_unweighted_vertices(mesh_obj, arm_obj)
    print(f"[rig] heat weighting: {total - unweighted}/{total} vertices weighted")

    if unweighted > total * 0.5:
        # Attempt 2: envelope weights — geometric distance to bone segments, no
        # mesh-connectivity requirement, gives real blending (unlike a hard
        # nearest-bone fallback). Requires bone envelope radii to be widened
        # from Blender's tiny defaults to actually reach the mesh surface.
        print("[rig] heat weighting failed broadly (mesh likely has disconnected "
              "shells); retrying with envelope weighting")
        for m in [m for m in mesh_obj.modifiers if m.type == "ARMATURE"]:
            mesh_obj.modifiers.remove(m)
        for vg in list(mesh_obj.vertex_groups):
            mesh_obj.vertex_groups.remove(vg)
        mesh_obj.parent = None
        set_bone_envelopes(arm_obj, hw)
        do_parent("ARMATURE_ENVELOPE")
        unweighted = count_unweighted_vertices(mesh_obj, arm_obj)
        print(f"[rig] envelope weighting: {total - unweighted}/{total} vertices weighted")

    # Final safety net: any vertex still unweighted (e.g. isolated geometry no
    # envelope reached) gets a rigid nearest-bone assignment. This also avoids
    # Blender's glTF exporter (4.0.2) crashing: it hits a 'neutral bone' fallback
    # path with an AttributeError (add_neutral_bones) whenever any vertex has
    # zero total bone weight.
    fix_unweighted_vertices(mesh_obj, arm_obj)


def set_bone_envelopes(arm_obj, hw):
    """Widen bone envelope radius/distance from Blender's tiny defaults so
    ARMATURE_ENVELOPE weighting actually reaches the mesh surface. Scaled off
    the character's half-width so it works across mesh scale changes."""
    radius = hw * 0.35
    distance = hw * 0.25
    for b in arm_obj.data.bones:
        b.head_radius = radius
        b.tail_radius = radius
        b.envelope_distance = distance


def count_unweighted_vertices(mesh_obj, arm_obj):
    bone_names = {b.name for b in arm_obj.data.bones}
    group_index_to_bone = {vg.index for vg in mesh_obj.vertex_groups if vg.name in bone_names}
    count = 0
    for v in mesh_obj.data.vertices:
        total = sum(g.weight for g in v.groups if g.group in group_index_to_bone)
        if total <= 1e-4:
            count += 1
    return count


def fix_unweighted_vertices(mesh_obj, arm_obj):
    """Assign any vertex still left with zero bone weight to its nearest bone
    (rigid, no blending). Guarantees exporter compatibility even after the
    heat/envelope attempts above; see skin() for why this matters."""
    bones = arm_obj.data.bones
    segments = [(b.name, Vector(b.head_local), Vector(b.tail_local)) for b in bones]

    def closest_bone(co):
        best_name, best_dist = None, None
        for name, head, tail in segments:
            seg = tail - head
            seg_len2 = seg.length_squared
            t = 0.0 if seg_len2 < 1e-9 else max(0.0, min(1.0, (co - head).dot(seg) / seg_len2))
            closest = head + seg * t
            d = (co - closest).length_squared
            if best_dist is None or d < best_dist:
                best_dist, best_name = d, name
        return best_name

    bone_names = {b.name for b in bones}
    vg_by_name = {vg.name: vg for vg in mesh_obj.vertex_groups}
    group_index_to_bone = {vg.index for vg in mesh_obj.vertex_groups if vg.name in bone_names}

    fixed = 0
    for v in mesh_obj.data.vertices:
        total = sum(g.weight for g in v.groups if g.group in group_index_to_bone)
        if total <= 1e-4:
            name = closest_bone(v.co)
            vg = vg_by_name.get(name)
            if vg is None:
                vg = mesh_obj.vertex_groups.new(name=name)
                vg_by_name[name] = vg
                group_index_to_bone.add(vg.index)
            vg.add([v.index], 1.0, "REPLACE")
            fixed += 1
    print(f"[rig] fallback nearest-bone assignment: {fixed} vertices")


# --------------------------------------------------------------------------- #
# Sockets (spec section 4)
# --------------------------------------------------------------------------- #

def crown_height(mesh_obj, mn, mx):
    """True helmet-crown apex: max z of vertices near the head's center column.
    The whole-mesh bounding-box top (mx.z) is the tip of the baked-in antenna
    balls, ~0.1 above the actual helmet surface — placing head_top_center
    there floats every top-mounted prop in mid-air (the follow-on bug behind
    the "helmet on top of the helmet" report). Antenna nubs sit at ~±0.45·hw
    in x, so sampling within a small central radius avoids them."""
    hw = (mx.x - mn.x) / 2.0
    cx = (mn.x + mx.x) / 2.0
    cy = (mn.y + mx.y) / 2.0
    radius = hw * 0.2
    mw = mesh_obj.matrix_world
    best = None
    for v in mesh_obj.data.vertices:
        co = mw @ v.co
        if abs(co.x - cx) < radius and abs(co.y - cy) < radius:
            if best is None or co.z > best:
                best = co.z
    if best is None:
        print("[rig] WARNING: crown sampling found no central vertices; using bbox top")
        return mx.z
    print(f"[rig] crown height: {best:.3f} (bbox top {mx.z:.3f}, "
          f"delta {mx.z - best:.3f} = baked antenna tips)")
    return best


def add_sockets(arm_obj, bounds, mesh_obj):
    mn, mx, front_y = bounds
    height = mx.z - mn.z
    hw = (mx.x - mn.x) / 2.0
    depth = mx.y - mn.y
    cx = (mn.x + mx.x) / 2.0
    cy = (mn.y + mx.y) / 2.0
    back_y = cy + depth * 0.45
    crown_z = crown_height(mesh_obj, mn, mx)

    def z(t):
        return mn.z + t * height

    # name -> (bone, world_location)
    sockets = {
        "head_top_center":   ("Head", Vector((cx, cy, crown_z))),
        "head_left_antenna": ("Head", Vector((cx + hw * 0.45, cy, z(0.95)))),
        "head_right_antenna":("Head", Vector((cx - hw * 0.45, cy, z(0.95)))),
        "head_left_side":    ("Head", Vector((cx + hw * 0.88, cy, z(0.70)))),
        "head_right_side":   ("Head", Vector((cx - hw * 0.88, cy, z(0.70)))),
        "faceplate":         ("Head", Vector((cx, front_y * 0.95, z(0.68)))),
        "chest_center":      ("Chest", Vector((cx, front_y * 0.85, z(0.46)))),
        "belt_front":        ("Hips", Vector((cx, front_y * 0.8, z(0.30)))),
        "belt_left":         ("Hips", Vector((cx + hw * 0.5, cy, z(0.30)))),
        "belt_right":        ("Hips", Vector((cx - hw * 0.5, cy, z(0.30)))),
        "back_center":       ("Chest", Vector((cx, back_y, z(0.50)))),
        "left_hand_grip":    ("Hand.L", Vector((cx + hw * 1.0, cy, z(0.28)))),
        "right_hand_grip":   ("Hand.R", Vector((cx - hw * 1.0, cy, z(0.28)))),
        "left_boot_front":   ("Foot.L", Vector((cx + hw * 0.28, front_y, z(0.03)))),
        "right_boot_front":  ("Foot.R", Vector((cx - hw * 0.28, front_y, z(0.03)))),
    }

    created = []
    for name, (bone, loc) in sockets.items():
        empty = bpy.data.objects.new(f"socket_{name}", None)
        empty.empty_display_type = "PLAIN_AXES"
        empty.empty_display_size = 0.05
        bpy.context.collection.objects.link(empty)
        if bone not in arm_obj.data.bones:
            print(f"[rig] WARNING: bone '{bone}' missing for socket '{name}'")
        # Object-parent to the armature (NOT bone-parent): Blender's glTF exporter
        # (4.0.2) crashes in add_neutral_bones when empties are bone-parented onto
        # an armature that also has an unweighted bone (our Root). Object-parenting
        # avoids the crash. The intended attach bone is preserved as a custom
        # property so downstream tooling can re-parent it to the live bone for
        # animated attachment (see docs/KnitBit-Base-Spec.md section 4/8).
        empty.parent = arm_obj
        empty.parent_type = "OBJECT"
        empty.matrix_parent_inverse = arm_obj.matrix_world.inverted()
        empty.location = loc
        empty["attach_bone"] = bone
        created.append(name)
    print(f"[rig] added {len(created)} sockets")
    return created


# --------------------------------------------------------------------------- #
# Idle animation (rig validation)
# --------------------------------------------------------------------------- #

def add_idle_animation(arm_obj):
    """A minimal procedural idle loop (chest sway + counter head nod) purely to
    exercise the rig end-to-end — proves the skeleton/skin deform without
    breaking. Not meant as final animation quality."""
    import math

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = IDLE_FRAMES
    scene.render.fps = IDLE_FPS

    bpy.ops.object.select_all(action="DESELECT")
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")

    def kf(bone_name, frame, euler_deg):
        pb = arm_obj.pose.bones[bone_name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = tuple(math.radians(d) for d in euler_deg)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    mid = IDLE_FRAMES // 2
    kf("Chest", 1, (0, 0, 0))
    kf("Chest", mid, (2, 0, 0))
    kf("Chest", IDLE_FRAMES, (0, 0, 0))
    kf("Head", 1, (0, 0, 0))
    kf("Head", mid, (-1.5, 0, 0))
    kf("Head", IDLE_FRAMES, (0, 0, 0))

    bpy.ops.object.mode_set(mode="OBJECT")
    if arm_obj.animation_data and arm_obj.animation_data.action:
        arm_obj.animation_data.action.name = "Idle"
    scene.frame_set(1)
    print(f"[rig] added idle animation ({IDLE_FRAMES} frames @ {IDLE_FPS}fps)")


# --------------------------------------------------------------------------- #
# Export
# --------------------------------------------------------------------------- #

def export(out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_skins=True,
        export_animations=True,
        export_extras=True,  # preserve custom props (socket attach_bone) as glTF extras
        use_selection=False,
    )
    print(f"[rig] exported: {out_path}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    in_path, out_path, idle_out_path = parse_args()
    print(f"[rig] input : {in_path}")
    print(f"[rig] output: {out_path}")
    clean_scene()
    mesh_obj = import_mesh(in_path)
    mn, mx = mesh_bounds(mesh_obj)
    print(f"[rig] bounds min={tuple(round(v,3) for v in mn)} max={tuple(round(v,3) for v in mx)}")
    arm_obj, bounds = build_armature(mn, mx)
    hw = (mx.x - mn.x) / 2.0
    skin(mesh_obj, arm_obj, hw)
    add_sockets(arm_obj, bounds, mesh_obj)
    export(out_path)

    add_idle_animation(arm_obj)
    export(idle_out_path)
    print(f"[rig] idle output: {idle_out_path}")

    print("[rig] done. Verify joint deformation in Blender; nudge LANDMARKS/HW if needed.")


if __name__ == "__main__":
    main()
