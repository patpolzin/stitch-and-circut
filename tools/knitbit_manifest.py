#!/usr/bin/env python3
"""knitbit_manifest.py — pure-Python loader for the KnitBit trait manifest.

The manifest (assets/3d/knitbit_base/manifest.json) is the single source of
truth for the character builder: the base rig, every trait's source mesh + fit
transform, and the named preset loadouts. Both the Blender assembler
(build_character.py) and the legacy per-build script (fit_traits.py) read it via
this module, so the fit numbers live in exactly one place.

Deliberately stdlib-only (no bpy, no numpy): it must import cleanly outside
Blender so it can drive validation, CI checks, and any future non-Blender
builder frontend that just needs to know "what traits exist and how do they
mount." The Blender-specific mesh work lives in build_character.py.

CLI (no Blender needed):
    python3 tools/knitbit_manifest.py            # print the trait catalog
    python3 tools/knitbit_manifest.py --presets  # print preset loadouts
    python3 tools/knitbit_manifest.py --check     # validate the manifest
"""

import json
import os

ANTENNA_LEFT_SOCKET = "socket_head_left_antenna"
ANTENNA_RIGHT_SOCKET = "socket_head_right_antenna"


def _repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


ASSET_DIR = os.path.join(_repo_root(), "assets/3d/knitbit_base")
MANIFEST_PATH = os.path.join(ASSET_DIR, "manifest.json")


def load(path=MANIFEST_PATH):
    with open(path) as f:
        return json.load(f)


def traits_by_id(manifest):
    return {t["id"]: t for t in manifest["traits"]}


def traits_by_slot(manifest):
    out = {}
    for t in manifest["traits"]:
        out.setdefault(t["slot"], []).append(t)
    return out


class FitInstruction:
    """One resolved prop to mount onto the base: absolute source path, target
    socket (OR a bone, for a mesh-swap), and the fit transform. `mount:antenna_pair`
    and `mount:limb_pair` traits expand into two of these (left un-mirrored,
    right mirrored on x)."""

    __slots__ = (
        "name", "trait_id", "file", "socket",
        "scale_frac", "rotation_deg", "mirror_x", "offset_frac", "dynamic",
        "attach_bone", "hides_region",
    )

    def __init__(self, name, trait_id, file, socket,
                 scale_frac, rotation_deg, mirror_x, offset_frac, dynamic=None,
                 attach_bone=None, hides_region=None):
        self.name = name
        self.trait_id = trait_id
        self.file = file
        self.socket = socket
        self.scale_frac = scale_frac
        self.rotation_deg = tuple(rotation_deg)
        self.mirror_x = mirror_x
        self.offset_frac = tuple(offset_frac)
        # dynamic (free-hanging/pendulum) spec inherited from the trait's slot,
        # or None for a rigid attachment. build_character.py reads it to pivot
        # the node at the hook and stamp physics params into glTF extras.
        self.dynamic = dynamic
        # mesh-swap fields (mount:limb_pair). When set, `socket` is None and the
        # prop attaches directly to this bone (e.g. "Foot.L"); `hides_region`
        # names a manifest.mesh_regions key whose window build_character.py
        # deletes from the base mesh first (mirror_x picks the side), so the
        # base's own boot/hand geometry doesn't double up with the swap-in mesh.
        self.attach_bone = attach_bone
        self.hides_region = hides_region

    def __repr__(self):
        target = self.socket or f"bone:{self.attach_bone}"
        return (f"FitInstruction({self.name!r} <- {os.path.basename(self.file)} "
                f"@ {target} scale={self.scale_frac} rot={self.rotation_deg} "
                f"mirror_x={self.mirror_x} offset={self.offset_frac}"
                f"{' hides='+self.hides_region if self.hides_region else ''})")


def _instructions_for_trait(trait, dynamic=None):
    fit = trait["fit"]
    file_abs = os.path.join(ASSET_DIR, trait["file"])
    scale = fit["scale"]
    rot = fit.get("rotation_deg", [0, 0, 0])
    off = fit.get("offset_frac", [0, 0, 0])
    mount = trait.get("mount", "socket")

    if mount == "antenna_pair":
        return [
            FitInstruction(trait["id"] + "_left", trait["id"], file_abs,
                           ANTENNA_LEFT_SOCKET, scale, rot, False, off, dynamic),
            FitInstruction(trait["id"] + "_right", trait["id"], file_abs,
                           ANTENNA_RIGHT_SOCKET, scale, rot, True, off, dynamic),
        ]
    if mount == "limb_pair":
        bone = trait.get("attach_bone")
        hides = trait.get("hides")
        if not bone:
            raise ValueError(f"trait '{trait['id']}' has mount 'limb_pair' but no attach_bone set")
        # optional per-side override for asymmetric base meshes (the v2 base's
        # leg columns differ slightly L vs R). Authored in the SAME left-side
        # convention as offset_frac — x is still negated on application.
        off_r = fit.get("offset_frac_right", off)
        return [
            FitInstruction(trait["id"] + "_left", trait["id"], file_abs, None,
                           scale, rot, False, off, dynamic,
                           attach_bone=f"{bone}.L", hides_region=hides),
            FitInstruction(trait["id"] + "_right", trait["id"], file_abs, None,
                           scale, rot, True, off_r, dynamic,
                           attach_bone=f"{bone}.R", hides_region=hides),
        ]
    if mount == "socket":
        socket = trait.get("socket")
        if not socket:
            raise ValueError(f"trait '{trait['id']}' has mount 'socket' but no socket set")
        return [FitInstruction(trait["id"], trait["id"], file_abs,
                               socket, scale, rot, False, off, dynamic)]
    raise ValueError(f"trait '{trait['id']}' has unknown mount '{mount}'")


def resolve_loadout(manifest, loadout):
    """loadout: {slot: trait_id or None}. Returns a flat list[FitInstruction].
    Raises if a trait id is unknown or assigned to the wrong slot. A slot-level
    "dynamic" spec (free-hanging/pendulum) is attached to each of that slot's
    instructions."""
    by_id = traits_by_id(manifest)
    slots = manifest.get("slots", {})
    instrs = []
    for slot, trait_id in loadout.items():
        if trait_id is None:
            continue
        trait = by_id.get(trait_id)
        if trait is None:
            raise KeyError(f"trait '{trait_id}' (requested for slot '{slot}') "
                           f"is not in the manifest")
        if trait["slot"] != slot:
            raise ValueError(f"trait '{trait_id}' is slot '{trait['slot']}', "
                             f"not the requested '{slot}'")
        dynamic = slots.get(slot, {}).get("dynamic")
        instrs.extend(_instructions_for_trait(trait, dynamic))
    return instrs


def preset_names(manifest):
    return list(manifest.get("presets", {}))


def resolve_preset(manifest, name):
    """Returns (preview_stem, list[FitInstruction]) for a named preset."""
    presets = manifest.get("presets", {})
    if name not in presets:
        raise KeyError(f"preset '{name}' not in manifest "
                       f"(have: {', '.join(presets) or 'none'})")
    preset = presets[name]
    return preset.get("preview_stem", name), resolve_loadout(manifest, preset["loadout"])


def check(manifest):
    """Structural self-check. Returns a list of problem strings (empty == OK)."""
    problems = []
    sockets = set(manifest.get("sockets", []))
    regions = manifest.get("mesh_regions", {})
    by_id = {}
    for t in manifest["traits"]:
        tid = t["id"]
        if tid in by_id:
            problems.append(f"duplicate trait id '{tid}'")
        by_id[tid] = t
        # every trait must resolve to instructions with known sockets/bones
        try:
            for instr in _instructions_for_trait(t):
                if instr.socket is not None:
                    if sockets and instr.socket not in sockets:
                        problems.append(f"trait '{tid}' mounts on unknown socket '{instr.socket}'")
                elif not instr.attach_bone:
                    problems.append(f"trait '{tid}' has neither a socket nor an attach_bone")
                if instr.hides_region and instr.hides_region not in regions:
                    problems.append(f"trait '{tid}' hides unknown mesh_region '{instr.hides_region}'")
                if not os.path.exists(instr.file):
                    problems.append(f"trait '{tid}' source mesh missing: {instr.file}")
        except (ValueError, KeyError) as e:
            problems.append(str(e))
    # presets must reference known traits in the right slots
    for name, preset in manifest.get("presets", {}).items():
        try:
            resolve_loadout(manifest, preset["loadout"])
        except (ValueError, KeyError) as e:
            problems.append(f"preset '{name}': {e}")
    return problems


def _main():
    import sys
    manifest = load()
    args = sys.argv[1:]

    if "--check" in args:
        problems = check(manifest)
        if problems:
            print("MANIFEST CHECK FAILED:")
            for p in problems:
                print(f"  - {p}")
            sys.exit(1)
        print(f"manifest OK: {len(manifest['traits'])} traits, "
              f"{len(preset_names(manifest))} presets, all sources present")
        return

    if "--presets" in args:
        for name in preset_names(manifest):
            stem, instrs = resolve_preset(manifest, name)
            print(f"{name}  ({manifest['presets'][name].get('label', '')})  -> {stem}")
            for instr in instrs:
                target = instr.socket or f"bone:{instr.attach_bone}"
                hides = f"  [hides:{instr.hides_region}]" if instr.hides_region else ""
                print(f"    {target:26s} <- {instr.trait_id}"
                      f"{'  (mirrored)' if instr.mirror_x else ''}{hides}")
        return

    # default: the trait catalog, grouped by slot (builder-frontend view)
    by_slot = traits_by_slot(manifest)
    for slot, meta in manifest["slots"].items():
        print(f"[{slot}] {meta.get('label', '')}")
        for t in by_slot.get(slot, []):
            mount = t.get("mount", "socket")
            if mount == "antenna_pair":
                target = "antenna L+R"
            elif mount == "limb_pair":
                target = f"bone {t.get('attach_bone', '?')}.L+R  [hides:{t.get('hides', '?')}]"
            else:
                target = t.get("socket") or "?"
            print(f"    {t['id']:20s} {t.get('label', ''):16s} "
                  f"theme={t.get('theme', '?'):8s} -> {target}")


if __name__ == "__main__":
    _main()
