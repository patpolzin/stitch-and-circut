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
| `knitbit_base_apose_textured.glb` | **Canonical source mesh** — textured (PBR + emissive face), A-pose, unrigged. Input to the rig script. |
| `knitbit_base_textured_unrigged.glb` | ⚠️ **Deprecated** — natural standing pose, but the generation **dropped the head side "ear" plates** (the round cups on the sides of the head), so it is off-model. Kept only for reference. |
| `knitbit_base_rigged.glb` | ✅ **Rigged base** — humanoid skeleton (20 bones, spec §3) + 15 named sockets (spec §4), static bind pose, textures intact. Build the trait system on this. |
| `knitbit_base_idle.glb` | ✅ Same rig with a 1-second procedural idle clip (chest sway + head counter-nod) — validates the skeleton deforms cleanly end to end. |

The two source GLBs are ~15 MB, single-mesh, textured (4 image maps, PBR
metallic/roughness/normal + emissive green face). The rigged GLBs are ~16 MB.

## How the base was produced

1. Crop the turnaround into 4 clean views (done — see `refs/view_*.png`).
2. Higgsfield `multi_image_to_3d` (Meshy) with texturing + PBR → the two source GLBs.
   - `knitbit_base_textured_unrigged.glb`: default pose (deprecated, see above).
   - `knitbit_base_apose_textured.glb`: `pose_mode=a-pose` for a rig-friendly bind pose.
3. `tools/rig_knitbit.py` (Blender, run in-container) → `knitbit_base_rigged.glb` +
   `knitbit_base_idle.glb`.

## Rigging status ✅

Higgsfield/Meshy **auto-rigging failed** on this character three times (`enable_rigging`
returned an un-skinned mesh; the dedicated `3d_rigging` job failed with/without animation,
with/without `pose_mode=a-pose`). Meshy's auto-rigger targets human proportions; KnitBit's
chibi shape (oversized head, short armored limbs fused to a wide torso) falls outside what
it can fit. So the rig was built directly with Blender via `tools/rig_knitbit.py`:

```
blender --background --python tools/rig_knitbit.py
```

(If your `blender` build links the system Python rather than bundling its own — true of the
Debian/Ubuntu `apt` package — it needs numpy for the glTF I/O addon: `apt-get install
python3-numpy`.)

The script imports `knitbit_base_apose_textured.glb`, builds the spec-§3 humanoid armature
(20 bones, positions derived from the mesh bounds), skins it, adds the spec-§4 socket
empties, and writes both GLBs above. Skinning quality, honestly:

- Blender's **automatic (heat) weights failed on every vertex** (0/28996) — the mesh has
  many disconnected shells (screws, bolts, panel trim, typical of AI-generated hard-surface
  sculpts) that the heat solver can't bridge.
- The script automatically **falls back to envelope weighting**, which doesn't need mesh
  connectivity: this covered **27649/28996 vertices (95.4%)** with real blended weights.
- The remaining **1347 vertices (4.6%)** got a rigid nearest-bone assignment (no blending)
  as a final safety net.

**Net result:** a working, exportable rig where the large majority of the mesh deforms with
smooth blending, but a joint or two may show a harder edge where the rigid fallback landed.
If a joint looks wrong, open `knitbit_base_rigged.glb` in Blender, weight-paint the affected
area by hand, and re-export (or nudge `LANDMARKS`/`HW` in the script and re-run first — a
better bone placement can also reduce how many vertices need the fallback).

The neutral base uses **charcoal** yarn; theme packs swap yarn color (spec §7).

## Pilot trait batch (spec §6 build-order step 4) ✅ Phase A

| Path | What |
| --- | --- |
| `traits/pilot/antenna.glb` | Classic bulb antenna (used as a mirrored pair) |
| `traits/pilot/helmet_panel.glb` | Reinforced helmet top panel |
| `traits/pilot/chest_icon.glb` | Star chest badge |
| `traits/pilot/belt_charm.glb` | Gear belt charm (has a small stray chain-link artifact — see spec §6) |
| `traits/pilot/backpack.glb` | Backpack |
| `knitbit_pilot_preview.glb` | All 6 props (antenna pair + 4 others) socket-fitted onto `knitbit_base_rigged.glb` |
| `knitbit_pilot_preview_front.png` / `_side.png` | Rendered verification (Blender Workbench under Xvfb — no display in this container) |

Built with `tools/fit_traits.py`:

```
xvfb-run -a blender --background --python tools/fit_traits.py
```

(`xvfb-run` is only needed for the render step; the fit + export runs headless without
it, but the script always attempts both.) Each prop is a plain static mesh, so it's
**object-parented** to its target socket empty — no rigging/skinning involved, so none of
the base rig's exporter-crash class applies here.

Full writeup, including the parenting bug that put every prop at the scene origin before
the fix (identity vs. cancelling `matrix_parent_inverse`), and the reverted mesh-cleanup
attempt, is in `docs/KnitBit-Base-Spec.md` §6.
