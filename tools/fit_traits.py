#!/usr/bin/env blender --background --python
"""fit_traits.py — DEPRECATED thin shim, kept for its documented command.

Superseded by tools/build_character.py, which assembles ANY loadout from the
trait manifest (assets/3d/knitbit_base/manifest.json) instead of carrying its
own hardcoded per-build fit dicts. The fit numbers that used to live here now
live once, in the manifest.

This shim remains only so the previously-documented command still works and
rebuilds the three canonical preset previews (pilot, variant_b, variant_c):

    blender --background --python tools/fit_traits.py            # all 3 presets
    blender --background --python tools/fit_traits.py -- variant_b   # one preset

New work should call build_character.py directly — it also takes custom
`slot=trait` loadouts and `out=`/`outdir=` options. To inspect the manifest
without Blender: `python3 tools/knitbit_manifest.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_character as bc  # noqa: E402
import knitbit_manifest as km  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    presets = argv or km.preset_names(bc.MANIFEST)
    print(f"[fit] deprecated shim -> build_character for presets: {presets}")
    # Hand off to build_character.main(), which imports mathutils, defaults the
    # output dir to the asset dir, fits, exports, and renders each preset.
    sys.argv = [sys.argv[0], "--"] + presets
    bc.main()


if __name__ == "__main__":
    main()
