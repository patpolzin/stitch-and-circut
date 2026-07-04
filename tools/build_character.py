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


def longest_dimension(obj):
    coords = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    xs = [c.x for c in coords]
    ys = [c.y for c in coords]
    zs = [c.z for c in coords]
    return max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def fit_instruction(instr):
    """Mount one km.FitInstruction onto its socket in the current scene.

    The fit mechanics (scale-to-target, object-parent-to-socket, surface-mount
    offset, and the QUATERNION-mode rotation compose) are the exact ones proven
    in the Phase A/B pilot; the numbers now come from the manifest, not code."""
    socket = find_socket(instr.socket)
    if socket is None:
        return None

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

    prop.parent = socket
    prop.parent_type = "OBJECT"
    # Leave matrix_parent_inverse at identity so the socket's world transform
    # applies on top of the prop's local loc/rot/scale (matrix_world =
    # socket.matrix_world @ local_matrix); the usual inverse idiom would drop
    # every prop back at the scene origin instead of at its socket.
    prop.location = tuple(f * CHAR_HEIGHT for f in instr.offset_frac)
    # The glTF importer leaves objects in QUATERNION mode, where assigning
    # rotation_euler is silently ignored. Compose the manifest hint ON TOP of
    # the imported orientation via quaternions: hint (0,0,0) keeps the prop as
    # imported, a nonzero hint actually turns it.
    base_q = prop.matrix_basis.to_quaternion()
    prop.rotation_mode = "QUATERNION"
    hint_q = mathutils.Euler(tuple(math.radians(d) for d in instr.rotation_deg)).to_quaternion()
    prop.rotation_quaternion = hint_q @ base_q
    prop.scale = (scale, abs(scale), abs(scale))
    bpy.context.view_layer.update()
    sock_pos = tuple(round(v, 3) for v in socket.matrix_world.translation)
    prop_pos = tuple(round(v, 3) for v in prop.matrix_world.translation)
    print(f"[build] {instr.name}: dim={dim:.3f} -> scale={scale:.3f} "
          f"@ '{instr.socket}' socket_world={sock_pos} prop_world={prop_pos}")
    return prop


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
    import_glb(BASE_GLB)

    fitted = []
    for instr in instructions:
        if fit_instruction(instr):
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
