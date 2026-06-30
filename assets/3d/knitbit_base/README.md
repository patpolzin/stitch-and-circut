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
| `knitbit_base_apose_textured.glb` | **Rig-ready base** — textured (PBR + emissive face), reposed to A-pose. Recommended base for rigging. |
| `knitbit_base_textured_unrigged.glb` | Natural standing-pose textured mesh (faithful render pose, no repose). |

Both GLBs are ~15 MB, single-mesh, textured (4 image maps, PBR metallic/roughness/normal
+ emissive green face). Neither contains a skeleton — see rigging status below.

## How the base was produced

1. Crop the turnaround into 4 clean views (done — see `refs/view_*.png`).
2. Higgsfield `multi_image_to_3d` (Meshy) with texturing + PBR → the two GLBs above.
   - `knitbit_base_textured_unrigged.glb`: default pose.
   - `knitbit_base_apose_textured.glb`: `pose_mode=a-pose` for a rig-friendly bind pose.

## Rigging status ⚠️

Higgsfield/Meshy **auto-rigging failed** on this character. `enable_rigging` returned an
un-skinned mesh, and the dedicated `3d_rigging` job failed three times (with and without
animation, with and without `pose_mode=a-pose`). Meshy's auto-rigger targets human
proportions; KnitBit's chibi shape (oversized head, short armored limbs fused to a wide
torso) falls outside what it can fit. This is a known limitation of automatic riggers on
stylized non-human characters, not a transient error.

**Rig the base in Blender or Mixamo instead** (the realistic production path for a
stylized hero asset anyway):

- **Mixamo:** upload `knitbit_base_apose_textured.glb`, place the rig markers manually
  (chin/wrists/elbows/knees/groin), let it auto-skin. Tolerates odd proportions better
  than Meshy. Export a rigged GLB/FBX.
- **Blender (full control):** import the A-pose mesh, build/Rigify the humanoid skeleton
  from spec §3, skin it, then add the named socket empties from spec §4 (see spec §8).

Target output to drop back here once rigged: `knitbit_base_rigged.glb` (+ an optional
`knitbit_base_idle.glb` for the idle validation clip).

The neutral base uses **charcoal** yarn; theme packs swap yarn color (spec §7).
