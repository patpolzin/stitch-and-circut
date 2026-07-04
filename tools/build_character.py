#!/usr/bin/env blender --background --python
"""build_character.py — manifest-driven KnitBit character assembler.

Reads the trait manifest (assets/3d/knitbit_base/manifest.json via
tools/knitbit_manifest.py), mounts a chosen trait per slot onto the rigged base,
and exports an assembled GLB + front/side verification renders. This is the
builder-scaffold successor to fit_traits.py: instead of hardcoded per-build
dicts, it takes any loadout, so a future character-builder UI can drive it by
writing a loadout and calling this.

RUN (Blender required for the mesh work; args go after `--`):

    # rebuild every named preset in the manifest
    blender --background --python tools/build_character.py

    # rebuild specific presets
    blender --background --python tools/build_character.py -- variant_b variant_c

    # build a custom loadout (any subset of slots), naming the output stem
    blender --background --python tools/build_character.py -- \
        antenna=antenna_scout chest_icon=chest_leaf accessory=acc_watering_can \
        out=my_bit

    # send preset builds somewhere other than the asset dir (e.g. to validate
    # without touching the committed previews)
    blender --background --python tools/build_character.py -- variant_b outdir=/tmp/verify

To inspect the manifest itself without Blender, use tools/knitbit_manifest.py.
"""

import bpy
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knitbit_manifest as km  # noqa: E402

MANIFEST = km.load()
ASSET_DIR = km.ASSET_DIR
BASE_GLB = os.path.join(ASSET_DIR, MANIFEST["base"]["rig"])
CHAR_HEIGHT = MANIFEST["base"]["char_height"]


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
        print(f"[build] WARNING: socket '{name}' not found in base scene")
    return obj


def find_body(objs):
    meshes = [o for o in objs if o.type == "MESH"]
    return max(meshes, key=lambda o: len(o.data.vertices)) if meshes else None


def find_armature(objs):
    return next((o for o in objs if o.type == "ARMATURE"), None)


def longest_dimension(obj):
    coords = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    return max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def hide_mesh_region(body_obj, region, mirror_x):
    """Delete base-mesh vertices inside a manifest.mesh_regions window via
    bmesh, so a mesh-swap trait's replacement doesn't double up with the base's
    own geometry there (boots/hands — see docs/KnitBit-Base-Spec.md section 10).
    Windows are stored for the LEFT (+x) side; mirror_x flips to -x for the
    right. Runs on the imported base mesh in memory only — the committed base
    GLB is never touched."""
    import bmesh
    x_lo, x_hi = region["x_min"], region["x_max"]
    if mirror_x:
        x_lo, x_hi = -x_hi, -x_lo
    z_max = region.get("z_max")

    bm = bmesh.new()
    bm.from_mesh(body_obj.data)
    bm.verts.ensure_lookup_table()
    to_delete = []
    for v in bm.verts:
        co = body_obj.matrix_world @ v.co
        if x_lo <= co.x <= x_hi and (z_max is None or co.z <= z_max):
            to_delete.append(v)
    bmesh.ops.delete(bm, geom=to_delete, context='VERTS')
    bm.to_mesh(body_obj.data)
    bm.free()
    body_obj.data.update()
    print(f"[build] hid mesh_region x=[{x_lo:.3f},{x_hi:.3f}]"
          f"{f' z<={z_max:.3f}' if z_max is not None else ''}: {len(to_delete)} verts removed")


def fit_instruction(instr, body_obj=None, armature_obj=None, hidden=None):
    """Mount one km.FitInstruction in the current scene: onto a socket empty
    for a normal attachment, or directly at a bone head for a mesh-swap
    (instr.attach_bone set, instr.socket None) — after first hiding the base's
    own geometry in that region so the swap doesn't double up with it.

    The fit mechanics (scale-to-target, object-parent, surface-mount offset,
    and the QUATERNION-mode rotation compose) are the exact ones proven in the
    Phase A/B pilot; the numbers now come from the manifest, not code."""
    if instr.hides_region and hidden is not None:
        key = (instr.hides_region, instr.mirror_x)
        if key not in hidden:
            hide_mesh_region(body_obj, MANIFEST["mesh_regions"][instr.hides_region], instr.mirror_x)
            hidden.add(key)

    if instr.socket is not None:
        parent_obj = find_socket(instr.socket)
        if parent_obj is None:
            return None
        base_location = mathutils.Vector((0, 0, 0))
    else:
        if armature_obj is None or instr.attach_bone not in armature_obj.data.bones:
            print(f"[build] WARNING: bone '{instr.attach_bone}' not found for '{instr.name}'")
            return None
        parent_obj = armature_obj
        bone = armature_obj.data.bones[instr.attach_bone]
        base_location = armature_obj.matrix_world @ bone.head_local

    objs = import_glb(instr.file)
    meshes = [o for o in objs if o.type == "MESH"]
    if not meshes:
        print(f"[build] WARNING: no mesh imported from {instr.file}")
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    prop = bpy.context.view_layer.objects.active
    prop.name = f"trait_{instr.name}"

    dim = longest_dimension(prop)
    target = instr.scale_frac * CHAR_HEIGHT
    scale = (target / dim) if dim > 1e-6 else 1.0
    if instr.mirror_x:
        scale = -scale

    prop.parent = parent_obj
    prop.parent_type = "OBJECT"
    # Leave matrix_parent_inverse at identity so the parent's world transform
    # applies on top of the prop's local loc/rot/scale (matrix_world =
    # parent.matrix_world @ local_matrix); the usual inverse idiom would drop
    # every prop back at the scene origin instead of at its target. For a
    # socket, local space IS the socket's own position (offset only); for a
    # bone attach, the bone head is the base position and offset fine-tunes it.
    prop.location = base_location + mathutils.Vector(tuple(f * CHAR_HEIGHT for f in instr.offset_frac))
    # The glTF importer leaves objects in QUATERNION mode, where assigning
    # rotation_euler is silently ignored. Compose the manifest hint ON TOP of
    # the imported orientation via quaternions: hint (0,0,0) keeps the prop as
    # imported, a nonzero hint actually turns it.
    base_q = prop.matrix_basis.to_quaternion()
    prop.rotation_mode = "QUATERNION"
    rx, ry, rz = instr.rotation_deg
    if instr.mirror_x:
        # The X-mirror (negative x-scale below) happens BEFORE rotation in
        # Blender's TRS order. For the mirrored instance to be the true mirror
        # image of the unmirrored one (not just the same rotation replayed on
        # flipped geometry), the applied rotation must be the X-mirror's
        # conjugate of the hint: R_right = Mx @ R_left @ Mx. Verified
        # algebraically (and holds for ANY Euler composition order, since
        # conjugation distributes over a matrix product term-by-term): this
        # conjugate negates the Y and Z components and leaves X unchanged.
        # (An earlier version of this fix only negated Z; antenna_scout's
        # small Y-lean happened to look fine either way because a thin stalk
        # is nearly rotationally symmetric about its own axis, which masked
        # the missing Y negation — re-verified after this fix, still correct.)
        ry, rz = -ry, -rz
    hint_q = mathutils.Euler((math.radians(rx), math.radians(ry), math.radians(rz))).to_quaternion()
    prop.rotation_quaternion = hint_q @ base_q
    prop.scale = (scale, abs(scale), abs(scale))
    bpy.context.view_layer.update()

    if instr.dynamic:
        _make_dynamic(prop, instr.dynamic)

    target_label = instr.socket or f"bone:{instr.attach_bone}"
    prop_pos = tuple(round(v, 3) for v in prop.matrix_world.translation)
    print(f"[build] {instr.name}: dim={dim:.3f} -> scale={scale:.3f} "
          f"@ '{target_label}' base_world={tuple(round(v,3) for v in base_location)} prop_world={prop_pos}"
          f"{'  [dynamic]' if instr.dynamic else ''}{'  [hides:'+instr.hides_region+']' if instr.hides_region else ''}")
    return prop


def _make_dynamic(prop, dyn):
    """Rig a free-hanging charm for runtime pendulum swing: move the object
    origin to the hook (top-center of the bbox) so the node pivots there, and
    stamp the physics params onto the node's glTF extras (knitbit_* custom
    props, exported because export_extras=True). The runtime (game spring/verlet
    system) reads these to swing the charm about the hook when the body moves.
    The mesh does not move — only the pivot/origin and metadata change — so the
    rest-pose render is identical."""
    import json
    # world-space top-center of the charm = the hook
    wc = [prop.matrix_world @ mathutils.Vector(c) for c in prop.bound_box]
    top_z = max(c.z for c in wc)
    cx = sum(c.x for c in wc) / 8.0
    cy = sum(c.y for c in wc) / 8.0
    hook = mathutils.Vector((cx, cy, top_z))
    # move origin to the hook without moving the mesh
    prev = tuple(bpy.context.scene.cursor.location)
    bpy.context.scene.cursor.location = hook
    bpy.ops.object.select_all(action="DESELECT")
    prop.select_set(True)
    bpy.context.view_layer.objects.active = prop
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.context.scene.cursor.location = prev
    # stamp physics metadata -> node.extras
    prop["knitbit_dynamic"] = True
    prop["knitbit_pivot"] = dyn.get("pivot", "hook_top")
    prop["knitbit_attach_bone"] = dyn.get("attach_bone", "Hips")
    prop["knitbit_swing"] = json.dumps({
        k: dyn[k] for k in ("type", "stiffness", "damping", "max_angle_deg", "axes")
        if k in dyn
    })
    bpy.context.view_layer.update()


def setup_render(engine="BLENDER_EEVEE_NEXT"):
    scene = bpy.context.scene
    try:
        scene.render.engine = engine
    except TypeError:
        print(f"[build] render engine '{engine}' unavailable, falling back to BLENDER_WORKBENCH")
        scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1200
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("PreviewWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.55, 0.45, 0.38, 1)
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
    cam_data.ortho_scale = CHAR_HEIGHT * 1.3
    cam_obj = bpy.data.objects.new("PreviewCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    return cam_obj


def render_view(cam_obj, angle_deg, out_path, distance=4.0, height_frac=0.0):
    rad = math.radians(angle_deg)
    cam_obj.location = (distance * math.sin(rad), -distance * math.cos(rad), CHAR_HEIGHT * height_frac)
    direction = mathutils.Vector((0, 0, CHAR_HEIGHT * height_frac)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"[build] rendered: {out_path}")


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
    print(f"[build] exported: {out_path}")


def build(instructions, out_stem, out_dir, render=True):
    print(f"[build] === {out_stem} ({len(instructions)} props) ===")
    clean_scene()
    base_objs = import_glb(BASE_GLB)
    body_obj = find_body(base_objs)
    armature_obj = find_armature(base_objs)
    hidden = set()  # (region_key, mirror_x) already hidden this build, avoid re-deleting

    fitted = []
    for instr in instructions:
        if fit_instruction(instr, body_obj, armature_obj, hidden):
            fitted.append(instr.name)
    print(f"[build] fitted {len(fitted)}/{len(instructions)}: {fitted}")

    export(os.path.join(out_dir, out_stem + ".glb"))
    if render:
        cam = setup_render()
        render_view(cam, 25, os.path.join(out_dir, out_stem + "_front.png"))
        render_view(cam, 90, os.path.join(out_dir, out_stem + "_side.png"))
    return fitted


def _parse_args(argv):
    """Split `--` args into: preset names, custom slot=trait pairs, and options
    (out=..., outdir=...)."""
    presets, loadout, opts = [], {}, {}
    for tok in argv:
        if "=" in tok:
            key, val = tok.split("=", 1)
            if key in ("out", "outdir", "render"):
                opts[key] = val
            else:
                loadout[key] = val
        else:
            presets.append(tok)
    return presets, loadout, opts


def main():
    global mathutils
    import mathutils  # noqa: F824 (importable only once Blender is running)

    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    presets, loadout, opts = _parse_args(argv)
    out_dir = opts.get("outdir", ASSET_DIR)
    render = opts.get("render", "1") not in ("0", "false", "no")

    print(f"[build] base: {BASE_GLB}")
    print(f"[build] outdir: {out_dir}")

    if loadout:
        # one custom character from explicit slot=trait pairs
        instrs = km.resolve_loadout(MANIFEST, loadout)
        build(instrs, opts.get("out", "knitbit_custom_preview"), out_dir, render)

    # named presets (default to all if neither presets nor a custom loadout given)
    if not presets and not loadout:
        presets = km.preset_names(MANIFEST)
    for name in presets:
        stem, instrs = km.resolve_preset(MANIFEST, name)
        build(instrs, stem, out_dir, render)

    print("[build] done.")


if __name__ == "__main__":
    main()
