# KnitBit Base — 3D Asset Folder

Canonical neutral base KnitBit ("Bit") 3D assets and reference art.
Production spec: [`docs/KnitBit-Base-Spec.md`](../../../docs/KnitBit-Base-Spec.md).

## Contents

| Path | What |
| --- | --- |
| `refs/knitbit_neutral_front.png` | Clean neutral front portrait (modeling/PFP reference) |
| `refs/knitbit_turnaround.png` | Original 4-view turnaround sheet |
| `refs/view_front.png` `view_three_quarter.png` `view_side.png` `view_back.png` | Cropped single-view images fed to multi-view 3D generation |
| `refs/theme_*.png` | Themed style mockups (Pixel/Maker/Scout) — style reference only, not the base |
| `knitbit_base_rigged.glb` | _Pending_ — textured, humanoid-rigged base mesh |
| `knitbit_base_idle.glb` | _Pending_ — idle-animation rig validation |

## How the base is produced

1. Crop the turnaround into 4 clean views (done — see `refs/view_*.png`).
2. Higgsfield `multi_image_to_3d` with rigging + texturing → `knitbit_base_rigged.glb`.
3. Attach one idle clip (`animation_actions` + `enable_animation`) to validate the rig.
4. In Blender: rename bones to the canonical skeleton and add named socket empties
   (see spec §3, §4, §8).

The neutral base uses **charcoal** yarn; theme packs swap yarn color (spec §7).
