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

RUN (Blender not installed in the agent container — run this locally):
    blender --background --python tools/rig_knitbit.py
    # optional overrides:
    blender --background --python tools/rig_knitbit.py -- \
        --in path/to/input.glb --out path/to/output.glb

NOTES
    - Bone positions are derived from the mesh bounding box using proportion
      fractions in LANDMARKS below. They are good estimates for a chibi biped;
      nudge them in Blender's edit mode if a joint deforms poorly, then re-export.
    - Skinning uses Blender's automatic (heat) weights. Armor plates read as
      near-rigid; the braided-yarn joint sections carry the blend — matching the
      soft "unravel" material from the game design.
    - Bone names follow the VRM/Mixamo-friendly Hips/Spine/Chest/Neck/Head +
      .L/.R limb convention so animation retargeting stays clean.
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
    in_path, out_path = DEFAULT_IN, DEFAULT_OUT
    it = iter(argv)
    for a in it:
        if a == "--in":
            in_path = next(it)
        elif a == "--out":
            out_path = next(it)
    return in_path, out_path


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

def skin(mesh_obj, arm_obj):
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    # Automatic (heat) weights.
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")


# --------------------------------------------------------------------------- #
# Sockets (spec section 4)
# --------------------------------------------------------------------------- #

def add_sockets(arm_obj, bounds):
    mn, mx, front_y = bounds
    height = mx.z - mn.z
    hw = (mx.x - mn.x) / 2.0
    depth = mx.y - mn.y
    cx = (mn.x + mx.x) / 2.0
    cy = (mn.y + mx.y) / 2.0
    back_y = cy + depth * 0.45

    def z(t):
        return mn.z + t * height

    # name -> (bone, world_location)
    sockets = {
        "head_top_center":   ("Head", Vector((cx, cy, mx.z))),
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
        if bone in arm_obj.data.bones:
            empty.parent = arm_obj
            empty.parent_type = "BONE"
            empty.parent_bone = bone
            # Set world position after parenting (Blender uses parent bone tail as origin).
            empty.matrix_world = _translation(loc)
        else:
            print(f"[rig] WARNING: bone '{bone}' missing for socket '{name}'")
            empty.location = loc
        created.append(name)
    print(f"[rig] added {len(created)} sockets")
    return created


def _translation(loc):
    from mathutils import Matrix
    return Matrix.Translation(loc)


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
        use_selection=False,
    )
    print(f"[rig] exported: {out_path}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    in_path, out_path = parse_args()
    print(f"[rig] input : {in_path}")
    print(f"[rig] output: {out_path}")
    clean_scene()
    mesh_obj = import_mesh(in_path)
    mn, mx = mesh_bounds(mesh_obj)
    print(f"[rig] bounds min={tuple(round(v,3) for v in mn)} max={tuple(round(v,3) for v in mx)}")
    arm_obj, bounds = build_armature(mn, mx)
    skin(mesh_obj, arm_obj)
    add_sockets(arm_obj, bounds)
    export(out_path)
    print("[rig] done. Verify joint deformation in Blender; nudge LANDMARKS/HW if needed.")


if __name__ == "__main__":
    main()
