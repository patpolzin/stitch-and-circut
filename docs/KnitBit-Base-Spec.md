# KnitBit Base Spec — Canonical Production Reference

> Single source of truth for the neutral base **KnitBit** ("Bit") used in *Stitch &
> Circuit*. Every trait, theme, and accessory must preserve the Species DNA below.
> This document is the production-side companion to the art in
> `assets/3d/knitbit_base/`.

Status: **Phase 1 — Neutral Base.** The 300-trait library is intentionally *not* built
yet. Prove the base body + skeleton + sockets first, then expand.

---

## 1. Species DNA (fixed rules)

Every KnitBit, regardless of theme, obeys these:

| Element | Rule |
| --- | --- |
| Body type | Short chibi humanoid robot |
| Height feel | Roughly 4 ft tall (toy-like proportions) |
| Head | Oversized rounded monitor / helmet head |
| Face | Black pixel-display screen |
| Expression | Bright pixel eyes + simple pixel mouth |
| Body | Compact armored torso, chunky boots, sturdy limbs |
| Material | Gunmetal / dark charcoal plated shell |
| Internal structure | **Visible braided yarn**, never cable |
| Yarn (base) | **Dark charcoal** (themes swap this — see §7) |
| Mood | Friendly, collectible, retro-futurist, cozy-tech |
| Rig | Humanoid biped skeleton (VRM-compatible) |
| Style | Toy-like, premium, detailed, readable silhouette |

### Avoid (hard "no" list)
No human skin · no realistic human face · no exposed wires · no thin cables · no
hyper-realistic mech proportions · no adult-tall body · no weapon · no aggressive
military styling · no extra limbs · no wheels · no animal body · no complicated costume ·
no theme accessory on the neutral base.

### Neutral base prompt (canonical)
> A short chibi humanoid robot character called a KnitBit, with an oversized rounded
> rectangular monitor head, black pixel-display faceplate, friendly glowing pixel eyes
> and smile, compact armored torso, chunky boots, small sturdy robot hands, and visible
> braided yarn forming the inner limbs and neck. Dark gunmetal armor plating with subtle
> scuffs, bevels, screws, panel seams, soft retro-futuristic toy-like proportions. Yarn
> visible in the arms, legs, torso gaps, and neck, clearly reading as soft braided yarn
> rather than cables. No accessories, no theme costume, no backpack, no handheld item, no
> hat. Neutral base body only. Full body standing pose, clean studio background.

---

## 2. Reference views

Canonical art lives in `assets/3d/knitbit_base/refs/`:

| File | View | Purpose |
| --- | --- | --- |
| `knitbit_neutral_front.png` | Front portrait | Main modeling + PFP reference |
| `knitbit_turnaround.png` | 4-view sheet | Source of the cropped views below |
| `view_front.png` | Front | Modeling / silhouette |
| `view_three_quarter.png` | 3/4 front | Style + silhouette |
| `view_side.png` | Side | Head depth, boot depth, hand placement |
| `view_back.png` | Back | Backpack socket, rear plating, back yarn |
| `theme_pixel_green.png` / `theme_maker_gold.png` / `theme_scout_teal.png` | Themed mockups | Style reference only — **not** the base |

---

## 3. Base skeleton (canonical)

One canonical humanoid biped skeleton. Keep it humanoid (even though Bit is a robot) for
VRM compatibility and animation retargeting later.

```
Root
└─ Hips
   └─ Spine
      └─ Chest
         ├─ Neck
         │  └─ Head
         ├─ Left Shoulder ─ Left Upper Arm ─ Left Lower Arm ─ Left Hand
         └─ Right Shoulder ─ Right Upper Arm ─ Right Lower Arm ─ Right Hand
   ├─ Left Upper Leg ─ Left Lower Leg ─ Left Foot
   └─ Right Upper Leg ─ Right Lower Leg ─ Right Foot
```

Auto-rigging (Higgsfield) produces a standard humanoid skeleton; exact bone names may
differ. Retarget/rename to the list above in Blender so all downstream tooling is stable.

---

## 4. Socket map (first production map)

Sockets are empty transform nodes parented to the nearest bone. They are the known
attachment points every accessory connects to. **Higgsfield does not create these — add
them in Blender after rigging** (see §8).

| Socket | Parent bone | Used for |
| --- | --- | --- |
| `head_top_center` | Head | helmet top panels, patches, small hats |
| `head_left_antenna` | Head | left antenna |
| `head_right_antenna` | Head | right antenna |
| `head_left_side` | Head | headphone left cup, ear modules |
| `head_right_side` | Head | headphone right cup, ear modules |
| `faceplate` | Head | expression sprites / display effects |
| `chest_center` | Chest | chest icon, screen, badge |
| `belt_front` | Hips | belt buckle, central charm |
| `belt_left` | Hips | pouches, small tools |
| `belt_right` | Hips | pouches, small tools |
| `back_center` | Chest | backpack, cape, cloak, tank pack |
| `left_hand_grip` | Left Hand | handheld item |
| `right_hand_grip` | Right Hand | handheld item |
| `left_boot_front` | Left Foot | boot decal |
| `right_boot_front` | Right Foot | boot decal |

---

## 5. Trait attachment methods

Not all traits attach the same way. Keeping the right method per trait keeps the rig
stable.

| Trait type | Method |
| --- | --- |
| Antennas | Socketed mesh |
| Chest icons | Socketed mesh or decal |
| Belt charms | Socketed mesh (optional simple physics) |
| Backpacks | Socketed mesh |
| Handheld items | Socketed to hand grip |
| Boots | Skinned / mesh-swapped lower-leg + foot part |
| Hands | Skinned hand-mesh swap |
| Yarn color | Material swap |
| Face expression | Sprite / shader swap |
| Surface decals | Texture / decal layer |

---

## 6. Build order

Prove the base before scaling traits:

0. Finalize KnitBit visual DNA *(this doc, §1)*
1. Build neutral base KnitBit ✅ *(art + 3D base)*
2. Build front / 3-4 / side / back reference sheet ✅
3. Define skeleton + socket map ✅ *(§3–4; sockets applied in Blender)*
4. Validate one small **pilot** accessory set *(next)*
5. Build the full Master Trait Diagram sheet
6. Produce trait families by category
7. Produce theme packs
8. Build compatibility + rarity rules

### Pilot trait batch (step 4 — small, to prove the modular system)
| Slot | Options |
| --- | --- |
| Antenna | Classic bulbs · scout cameras · leaf tips |
| Helmet top panel | Smooth · reinforced · yarn patch |
| Chest icon | Star · wrench · leaf |
| Belt charm | Coin · gear · flower |
| Accessory | Backpack · headphones · watering can |

---

## 7. Theme color legend

Neutral base = charcoal yarn. Themes are produced later by swapping yarn color (material
swap) plus theme-specific socketed accessories. Label colors below double as the
artist/generation reference for each family.

| Theme | Label / accent color |
| --- | --- |
| Neutral / Base | White or light gray (charcoal yarn) |
| Scout | Teal |
| Tank | Burnt orange |
| Arcade | Hot pink |
| Maker | Golden yellow |
| Wizard | Purple |
| Music | Electric blue |
| Ghost | Mint cyan |
| Pixel | Neon green |
| Garden | Leaf green with pink accent |

---

## 8. Rigging & sockets (Blender)

**Status: done.** Higgsfield/Meshy produced an excellent *textured* base mesh
(`assets/3d/knitbit_base/knitbit_base_apose_textured.glb`) but its **auto-rigger failed**
on KnitBit's chibi proportions (oversized head + short armored limbs fused to a wide
torso) — three `3d_rigging` attempts failed. Auto-riggers target human proportions, so the
rig was built directly with `tools/rig_knitbit.py` (Blender, `bpy`), producing:

- `assets/3d/knitbit_base/knitbit_base_rigged.glb` — the humanoid skeleton (20 bones,
  exactly the §3 hierarchy) + the 15 §4 socket empties, static bind pose.
- `assets/3d/knitbit_base/knitbit_base_idle.glb` — the same rig with a 1-second procedural
  idle clip (chest sway + head counter-nod), proving the skeleton deforms end to end.

Re-run any time the source mesh changes:

```
blender --background --python tools/rig_knitbit.py
```

(Needs numpy in Blender's Python for the glTF addon — `apt-get install python3-numpy` if
using the Debian/Ubuntu `apt` Blender package, which links the system Python.)

### How the script rigs it

1. Imports `knitbit_base_apose_textured.glb`, builds the §3 humanoid armature (bone
   positions derived from the mesh bounds via `LANDMARKS`/`HW`).
2. **Skinning fallback chain**, honestly documented because it matters for quality:
   - Tries Blender's automatic (heat) weights first — **failed on 100% of vertices**
     (0/28996) on this mesh. Heat diffusion needs a connected mesh surface; this
     AI-generated sculpt has many disconnected shells (screws, bolts, panel trim) it
     can't bridge.
   - Falls back to **envelope weighting** (geometric distance to bone segments, no
     connectivity requirement) — covered **27649/28996 vertices (95.4%)** with real
     blended weights.
   - Any vertex still unweighted (**1347, 4.6%**) gets a rigid nearest-bone assignment.
     This also works around a Blender 4.0.2 glTF-exporter bug (`add_neutral_bones`
     crashes if any vertex has zero total bone weight).
3. Adds the §4 socket empties, **object-parented** to the armature (bone-parenting them
   crashes the same exporter bug when combined with an unweighted `Root` bone) with the
   intended attach bone stored as a glTF `extras.attach_bone` custom property. Re-parent
   to the live bone downstream for animated attachment.
4. Exports the static rigged GLB, then adds the idle clip and exports it separately.

### If a joint deforms poorly

The 4.6% rigid-fallback vertices are the most likely spot for a visible hard edge at a
joint. Open `knitbit_base_rigged.glb` in Blender and weight-paint the affected area by
hand, or first try nudging `LANDMARKS`/`HW` in the script (better bone placement reduces
how many vertices need the fallback) and re-run.

Sockets are additive — they don't alter the mesh or skin weights, so the base stays stable
as the trait library grows.

---

## 9. Production sheet discipline

Keep two sheet types separate:

| Sheet | Purpose |
| --- | --- |
| Master Trait Diagram Sheet | All parts by category + theme color. Planning / style approval. |
| Production Part Sheets | One category at a time (antennas, boots, hands, belts, charms…). Clean 3D conversion. |

Do not cram every production part onto one mega-sheet — pieces end up too small and
inconsistent to isolate for 3D conversion.
