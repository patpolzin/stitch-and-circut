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
| Head | Oversized rounded monitor / helmet head — **the head IS the helmet**; there is no separate helmet, and nothing helmet-shaped is ever attached on top of it |
| Face | Black pixel-display screen — the animated faceplate is the helmet-head's front |
| Expression | Bright pixel eyes + simple pixel mouth |
| Body | Compact armored torso, chunky boots, sturdy limbs |
| Material | Gunmetal / dark charcoal plated shell |
| Internal structure | **Visible braided yarn**, never cable |
| Yarn (base) | **Dark charcoal** (themes swap this — see §7) |
| Yarn look | Soft, plush, **knitted/braided wool** — matte fibers with visible braid stitches. Never wire, coil, cable, or metal spring. |
| Plating/yarn balance | Plating is **interwoven** with the yarn: armor on chest, shoulders, forearms, pelvis, shins/boots; yarn shows in joints, upper arms, thighs and torso gaps — structure without hiding the knit (v2 base). |
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
| `head_top_center` | Head | **low-profile surface details only** — thin panels, patches, small toppers. Never helmet- or dome-shaped geometry (the head IS the helmet, see §1) |
| `head_left_antenna` | Head | left antenna |
| `head_right_antenna` | Head | right antenna |
| `head_left_side` | Head | headphone left cup, ear modules |
| `head_right_side` | Head | headphone right cup, ear modules |
| `faceplate` | Head | expression sprites / display effects |
| `chest_center` | Chest | chest icon, screen, badge |
| `belt_front` | Hips | belt buckle; charms (offset in the manifest to hang off the **right hip** with the hook clipped onto the belt band and the body dangling free of the thigh; charms are a **dynamic/swinging** attachment — see §10) |
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
4. Validate one small **pilot** accessory set ✅ *(Phase A done — see below)*
5. Build the full Master Trait Diagram sheet ✅ *(see §9 — generated from the manifest)*
6. Produce trait families by category *(started — boots + hands mesh-swap proven, see §10)*
7. Produce theme packs
8. Build compatibility + rarity rules

### Pilot trait batch (step 4 — small, to prove the modular system)

**Status: Phase A done.** One option per slot was generated, converted to 3D, and
socket-fitted to prove the attachment mechanics work before spending on the rest of the
table below.

**Status: Phase A + Phase B done.** All three options in every slot are now
generated, converted to 3D, and socket-fitted. They are assembled into three
full-body preview builds (one option per slot each) to prove the whole slot
table works modularly, not just one pick:

| Slot | Options | Phase A pick | Phase B variants |
| --- | --- | --- | --- |
| Antenna | Classic bulbs · scout cameras · leaf tips | ✅ Classic bulb (pair) | ✅ scout camera, ✅ leaf tip |
| Helmet top panel | Smooth · reinforced · yarn patch | ✅ Reinforced | ✅ smooth, ✅ yarn patch |
| Chest icon | Star · wrench · leaf | ✅ Star | ✅ wrench, ✅ leaf |
| Belt charm | Coin · gear · flower | ✅ Gear | ✅ coin, ✅ flower |
| Accessory | Backpack · headphones · watering can | ✅ Backpack | ✅ headphones, ✅ watering can |

**Three assembled builds** (`tools/fit_traits.py` now takes build names as
args; run with none to build all three):

| Build | Preview stem | Set |
| --- | --- | --- |
| `pilot` | `knitbit_pilot_preview` | Phase A picks |
| `variant_b` | `knitbit_pilot_preview_b` | "tech": scout-camera antennae, smooth panel, wrench icon, coin charm, headphones |
| `variant_c` | `knitbit_pilot_preview_c` | "garden": leaf antennae, yarn-patch panel, leaf icon, flower charm, watering can |

`variant_c`'s watering can is the **first handheld** to exercise a hand-grip
socket (`socket_right_hand_grip`) rather than a surface/head socket — proving
that attachment path too. `variant_b`'s headphones mount as a single band unit
over `socket_head_top_center` (an arched topper is low-profile, not dome
geometry, so the §1 rule holds).

**Pipeline:** Higgsfield `generate_image` (concept art, styled to the DNA in §1) →
`image_to_3d` (textured + PBR mesh per prop, no rigging needed — static props) →
`tools/build_character.py` (Blender: imports the rigged base + each prop, scales to a
per-prop target size, **object-parents** the prop to its `socket_<name>` empty, exports
the assembled scene, and renders two verification angles under Xvfb since this container
has no display). The per-prop fit values feeding that last step now live in the trait
manifest — see §10.

**Result:** `assets/3d/knitbit_base/knitbit_pilot_preview.glb` — base + all 6 props
(antenna is a mirrored pair), each correctly parented to its socket, confirmed both
structurally (parent/child graph parsed from the glTF) and visually (rendered PNGs).
Antenna, helmet panel, chest icon, and backpack all placed and scaled well; the backpack
in particular is correctly hidden from the front and reads clearly on the back in profile.

**Known issue 1 (belt charm):** the belt charm's source photo included a hanging chain
link, which `image_to_3d` reconstructed as small disconnected geometry near the main gear
body — visible as a stray floating fragment in the render. Tried and reverted an automatic
"keep largest connected mesh island" cleanup (`bpy.ops.mesh.separate(type='LOOSE')`): these
meshes are naturally composed of hundreds to thousands of disconnected micro-patches
(normal for dense hard-surface reconstructions, not just this one prop), so "largest
island" cut real geometry off *every* prop rather than just removing the stray chain.

**Known issue 2 (helmet panel — "helmet on top of the helmet," fixed):** the original
"reinforced helmet top panel" concept prompt drifted into a **complete helmet dome**, and
`image_to_3d` faithfully reconstructed it; combined with an oversized fit scale (0.34 of
character height) and center-on-socket mounting at the head's apex, the pilot preview
showed a second helmet stacked on the head — violating the §1 rule that **the head IS the
helmet** (there is no separate helmet; the animated faceplate is its front). Fixed by:
regenerating the concept as an explicitly flat, thin access-panel plate (with "NOT a
helmet, NOT a dome" anti-drift language), reconverting, shrinking the fit to 0.15, and
adding a per-prop surface-mount offset in `tools/fit_traits.py` so the plate hugs the
crown. §1 and the §4 socket map now codify the rule.

**Known issue 3 (chest badge + belt charm floating off the body, fixed):** the same
bbox-fraction placement bug as issue 2, on the front axis. `chest_center`, `belt_front`,
`faceplate`, and the boot-front sockets were placed at fractions of the whole-mesh
bounding-box front — but the bbox front belongs to the head/boot extremes, not the local
torso surface, so the star badge floated 0.095 and the gear charm 0.135 in front of the
body. Fixed by generalizing the crown sampler into `surface_extreme()` in
`tools/rig_knitbit.py`: every surface-mounted socket now samples the actual mesh surface
near its own position (crown, faceplate, chest, belt front/sides, boot fronts). The belt
*side* sockets needed one extra guard — the A-pose hands hang at hip height, so the side
sampling caps its x-range at 0.5·half-width to find the hip flank (±0.23) instead of the
hand (±0.73).

**Known issue 4 (rotation hints were silently ignored, fixed in Phase B):** the
glTF importer leaves every imported prop in `QUATERNION` rotation mode, in which
assigning `obj.rotation_euler` is a **no-op** — so every `rot_deg` hint in the
Phase A `PROPS` table did nothing, and the props happened to look right only
because their imported orientation already matched. Phase B's leaf chest badge
imported lying flat (emblem up) and so needed a real +90° X pitch to face front,
which exposed the bug. Fixed in `fit_prop()` by switching the prop to
`QUATERNION` mode and composing the hint **on top of** the imported orientation
(`rotation_quaternion = hint_q @ base_q`). Hint `(0,0,0)` now reproduces the old
de-facto "keep as imported" behavior, so the two stale Phase-A hints that never
applied (`chest_icon` 90°, `backpack` 180°) were reset to `(0,0,0)` to match what
was actually rendering. **Verify a prop's rest orientation** (render it in
isolation) before assuming a hint is needed — reconstructions of the same slot
don't share a rest pose (the wrench badge imports standing, the leaf badge flat).

**Known issue 5 (headphones ∩ antennae, fixed):** in `variant_b` the headphone
band arcs across the crown at exactly the height the scout-camera antennae reach,
so the band sliced through the camera modules. Fixed by separating the two props
on two fronts: a **20° outward (Y) lean** on the antennae (symmetric under the
mirrored −x scale — an X-axis tilt is *not*, because the left/right antenna
sockets carry mirror-opposite base orientations, so an X tilt clears one side and
buries the other), plus **raising and widening the band** (scale 0.55→0.62, mount
offset −0.18→−0.11) so its arch rides above the antenna tips. General rule: when
two crown props share `head_top_center`-ish space, prefer symmetric Y-lean +
resize over per-side rotation.

**Pipeline takeaways for future concept art:**
- Keep prop reference photos free of incidental dangling/chained elements — the
  reconstruction includes whatever's in frame.
- Image models drift toward the *object category* in the prompt ("helmet panel" → a
  helmet). Describe the wrong interpretations explicitly ("NOT a dome...") and **visually
  verify every concept image before paying for 3D conversion**.
- **Never place surface-mounted sockets at bounding-box fractions** — sample the mesh
  surface local to the socket (see `surface_extreme()`); bbox extremes belong to whatever
  protrudes furthest, not the mounting surface.
- **Rotation hints only apply after switching the prop out of QUATERNION mode** (see
  issue 4). Render each new prop in isolation to read its true rest orientation before
  guessing a hint; sibling reconstructions of the same slot do not share one.
- **Two props on the same crown socket must be deconflicted deliberately** (see issue 5),
  favouring mirror-symmetric adjustments (outward Y-lean, resize) over per-side tilts.

**Individual pilot prop assets:** `assets/3d/knitbit_base/traits/pilot/*.glb` — 15
textured, unrigged props (Phase A's `{antenna, helmet_panel, chest_icon, belt_charm,
backpack}` plus Phase B's `{antenna_scout, antenna_leaf, panel_smooth, panel_yarn,
chest_wrench, chest_leaf, charm_coin, charm_flower, headphones, watering_can}`), ready to
socket-fit onto future base exports the same way.

**Phase B: done.** All 10 remaining variants generated, converted, fitted into the
`variant_b`/`variant_c` builds, and validated both structurally (every `trait_*` node
parented to its `socket_*`, parsed from the glTF) and visually (rendered front + side).

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
- `assets/3d/knitbit_base/knitbit_base_idle.glb` — the same rig with **three named
  animation clips** authored as stashed NLA tracks so they export as separate glTF
  animations (all verified to move bones on a fresh import):
  - **Idle** (2s loop) — hip weight-shift + chest sway + head counter-nod + arm swing
  - **Wave** (1.5s) — right arm raise + forearm wave, slight head tilt
  - **Bounce** (1s) — springy hop (Hips bone-local lift) with arm/head follow-through

The v2 base (regenerated 2026-07 for the soft-yarn + interwoven-plating art direction,
same silhouette/pose via reference-image-guided generation) ships with **charcoal yarn
baked in as the canonical default**. The source generation uses saturated crimson yarn on
purpose: `tools/make_yarn_colorways.py` hue-keys the crimson into a yarn mask, bakes the
charcoal default back into `knitbit_base_apose_textured.glb`, and emits one recolored
1024px texture per §7 theme into `web/yarn_<theme>.jpg` (plus `textures/colorways.json`,
picked up by the web export and the editor's "Yarn color" swatch row).

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

### Master Trait Diagram — generated

**Status: done (pilot library).** The Master Trait Diagram is produced from the
manifest, not hand-laid-out, so it stays in sync as traits are added:

```
blender --background --python tools/render_trait_thumbs.py   # 1 isolated thumb per trait
python3 tools/build_master_sheet.py                          # compose the sheet
```

- `tools/render_trait_thumbs.py` renders every `manifest.traits` entry (and the
  base) to a consistent transparent-background thumbnail in
  `assets/3d/knitbit_base/thumbs/`.
- `tools/build_master_sheet.py` composes `knitbit_master_trait_diagram.png`: each
  trait **category** with its option thumbnails, every option tagged by its
  **theme color** (from the new `manifest.themes` block — the §7 legend as data),
  a `dynamic · swings` marker on categories with a `dynamic` block, the **planned
  categories** not yet built, and the full **theme palette legend** with hexes.

This is the wide planning/style-approval overview. The per-category Production
Part Sheets (for clean 3D conversion) are still produced one category at a time
as each family is built (step 6).

---

## 10. Character builder (manifest + assembler)

The bridge from "traits proven one-by-one in Blender" to "a tool can assemble any
character." Three pieces:

| File | Role |
| --- | --- |
| `assets/3d/knitbit_base/manifest.json` | **Single source of truth.** The base rig, every trait's source mesh + fit transform (scale / rotation / offset / mount), and named preset loadouts. |
| `tools/knitbit_manifest.py` | Pure-Python loader (stdlib only, **no Blender**). Resolves a loadout `{slot: trait_id}` into concrete mount instructions; expands `antenna_pair` traits into a left + mirrored-right pair. Runnable as a CLI to inspect/validate the manifest. |
| `tools/build_character.py` | Blender assembler. Reads the manifest, mounts a chosen trait per slot onto the base, exports an assembled GLB + front/side renders. Takes named presets **or** an arbitrary `slot=trait` loadout. |

**Why a manifest.** The fit numbers (per-prop scale, the leaf badge's +90° pitch,
the scout antenna's outward lean, the headphone band's raised mount) used to be
duplicated across hardcoded Python dicts. They now live once, as data. Any
frontend — a future web/GUI builder, a batch renderer, the game's own loader — can
read `manifest.json` to know what traits exist, how they group into slots, and how
each mounts, without touching Blender. `tools/knitbit_manifest.py --check`
validates every trait resolves to a known socket with its source mesh present.

**Usage.**
```
# inspect the catalog / presets / validate — no Blender needed
python3 tools/knitbit_manifest.py            # traits grouped by slot
python3 tools/knitbit_manifest.py --presets  # what each preset mounts where
python3 tools/knitbit_manifest.py --check     # structural validation

# assemble (Blender). Args after `--`:
blender --background --python tools/build_character.py                 # all presets
blender --background --python tools/build_character.py -- variant_b    # one preset
blender --background --python tools/build_character.py -- \            # custom mix
    antenna=antenna_scout helmet_panel=panel_yarn chest_icon=chest_star \
    belt_charm=charm_flower accessory=acc_backpack out=mashup
```
`tools/fit_traits.py` is now a deprecated shim that just delegates the three
canonical presets to `build_character.py`.

**Validated.** The manifest-driven builder reproduces all three preset builds'
socket graphs exactly (parsed from the glTF) and pixel-for-pixel in render, and a
never-a-preset cross-theme mashup (scout antennae + yarn crown patch + star badge +
flower charm + backpack) assembles cleanly — proving the mix-and-match path.

**Adding a trait** (once its `.glb` is in `traits/`): append one object to
`manifest.traits` with its `slot`, `file`, `mount`/`socket`, and `fit` block; run
`--check`; assemble a loadout that uses it. No code change — the fit is data.

### Dynamic (free-hanging) attachments — belt charms swing

Belt charms are not rigidly fixed: they **hang from their hook and swing** when
the character moves. This is expressed as data + rig setup, with the actual
motion driven at runtime:

- **Placement** — the shared belt-charm `offset_frac` hangs the charm off the
  character's **right hip** (~87% of the way toward `socket_belt_right`, away from
  center-front), with the hanger ring **clipped onto the belt band** and the body
  **dangling free of the thigh**. The depth is tuned to the minimum proudness that
  clears the thigh's forward bulge (leg front ≈ −0.154 below the belt), found by
  probing the base mesh — pull back any further and the charm intersects the leg;
  push forward and it juts off the front.
- **Swing rig** — the `belt_charm` slot carries a `dynamic` block (pivot
  `hook_top`, attach bone `Hips`, pendulum stiffness/damping/max-angle). For any
  dynamic trait, `build_character.py` moves the charm **node's origin to the hook**
  (so it pivots there) and writes the params to the node's glTF **extras**
  (`knitbit_dynamic`, `knitbit_pivot`, `knitbit_attach_bone`, `knitbit_swing`).
  The runtime (the game's spring/verlet system, `game/lib/physics/verlet_rope.dart`)
  reads these to swing the charm about the hook as the hips move. Static preview
  renders show the rest pose; moving the origin does **not** move the mesh.
- **Demo** — `tools/demo_charm_swing.py` bakes a representative damped-pendulum
  swing about the hook and emits `knitbit_charm_swing_demo.glb` (animated) +
  `knitbit_charm_swing_demo.png` (filmstrip) as visual proof the charm hangs and
  swings correctly. This is a canned demo; the real swing is motion-reactive at
  runtime.

Adding another free-hanging trait later (a keychain, a dangling tool) is just a
slot with a `dynamic` block — no code change.

### Mesh-swap traits — boots + hands (mount:limb_pair)

**Status: proven (one option each — `boot_classic`, `hand_classic`).** Unlike every
socketed prop above, boots and hands **replace** base geometry rather than sit on
top of it (spec §5: "Skinned / mesh-swapped lower-leg + foot part" / "Skinned
hand-mesh swap"). Without removing the base's own baked-in boot/hand first, a
replacement would double up with it — the same class of bug as the original
helmet-on-helmet issue. Two new pieces make this work, both driven entirely by
manifest data (no rig regeneration):

- **`manifest.mesh_regions`** — absolute vertex windows (`x_min`/`x_max`, optional
  `z_max`) that isolate the foot and hand geometry on the base mesh, measured by
  probing `knitbit_base_rigged.glb`'s actual vertex positions per limb (histogram
  the vertex count by z-band within an x-window restricted to one limb — the
  window alone cleanly isolates the hand in the A-pose; the boot additionally
  needs a z cutoff since its x-window overlaps the torso at higher z). Windows are
  stored for the LEFT (+x) side; the right mirrors by negating x_min/x_max. A
  region may carry `extra` windows (same format) for geometry the primary box
  can't isolate. **The cut is plane-bisected, not just vertex-deleted**: the
  builder first slices the mesh with a clean plane at every window boundary
  (`bmesh.ops.bisect_plane`), then deletes the inside — deleting whole vertices
  out of the coarse yarn triangulation leaves a ragged zigzag boundary that hung
  visibly above the v2 boot cuffs until this fix. The v2 foot cut sits at the
  leg's narrow waist (z −0.50): cut lower and the base's sculpted boot-top flare
  survives and pokes past the replacement cuff.
- **`mount:limb_pair`** traits carry `attach_bone` (a bone name **without** the
  `.L`/`.R` suffix, e.g. `"Foot"`) and `hides` (a `mesh_regions` key). The loader
  expands one trait into two `FitInstruction`s (`attach_bone="Foot.L"`/`"Foot.R"`,
  mirrored) with no `socket` — `build_character.py` recognizes a `None` socket as
  "attach directly to this bone" instead of a socket empty, reading the bone's
  head position straight from the imported armature (no new sockets or a
  `rig_knitbit.py` regeneration needed). Before mounting, it deletes any base
  vertex inside the `hides` window via `bmesh` (in memory, per build — the
  committed base GLB is never modified), then places the replacement at the bone
  head plus the trait's usual `offset_frac`.

**Two things had to be *right*, not just present, for this to look correct** —
both found and fixed while fitting the real assets, not anticipated in advance:

1. **A yaw is not symmetric under `mirror_x` the way the belt-charm's Y-lean is.**
   Blender's TRS order applies the X-mirror scale *before* rotation, so naively
   reusing the same rotation hint for both mirrored instances is only correct if
   the rotation is about the mirror axis itself. Verified algebraically (holds for
   any Euler composition order, since conjugation distributes over a matrix
   product term-by-term): the mirrored instance needs `Y` and `Z` **negated**,
   `X` unchanged (`R_right = M_x · R_left · M_x`). `fit_instruction()` now applies
   this automatically for every mirrored instruction. Without it, the boot's toe
   rotation that faces the left foot forward pointed the naively-mirrored right
   boot's toe **backward** — confirmed both by matrix algebra and by an isolated
   top-down render of the boot mesh before wiring it in. (An earlier pass of this
   fix only negated Z; re-verified against the antenna_scout Y-lean afterward —
   still correct, because a thin antenna stalk is nearly rotationally symmetric
   about its own axis, which had been masking the missing Y negation.)
2. **A flat z-plane cut through organic, non-flat mesh geometry leaves stray
   flaps.** The yarn-textured shin isn't a smooth cylinder, so a single global
   `z_max` leaves a few low points not caught by the average cutoff, visible as
   small ragged flaps past the boot cuff. Fixed by widening/raising the window
   until the flaps were minimal — a **very small** residual flap can still peek
   out on the inner-facing side of each leg in some views. Documented and
   accepted rather than chased further, the same way Phase A documented the
   belt-charm's stray chain-link fragment rather than fully solving it: both are
   inherent AI-reconstruction/flat-cut artifacts, not code bugs.
3. **`offset_frac`'s X component wasn't mirrored, and this shipped once before
   being caught.** `offset_frac` is added as a plain world-space translation
   (`base_location + offset_frac·CHAR_HEIGHT`), outside the rotation/mirror-scale
   math above, and unlike rotation it needs only a straightforward reflection
   (negate X, keep Y/Z) for the mirrored instance to be a true mirror position —
   but the code applied the **same** unmirrored offset to both sides. Every prior
   trait's `offset_frac.x` happened to be `0` (antenna, belt charm, boots), so this
   was never exercised until the hand's nonzero `x` offset shipped: the left hand
   looked plausible, the right hand's wrist visibly floated off its own forearm,
   because the same `+x` nudge that (partially) helped the left pushed the right
   the wrong way. Fixed by negating `offset_frac.x` for every mirrored instruction,
   the same way rotation was already handled.

**Fit values were derived, not eyeballed, where the math was tractable — but
"derived" is not the same as "correct on the first try," and the hand's position
specifically needed a second, harder pass:**
- Boot yaw (`rotation_deg` z=-90): found by rendering the isolated boot mesh from
  directly above at four candidate yaws and reading which one pointed the toe
  toward the character's front (-Y).
- Hand **orientation** (`rotation_deg`): the fist's local knuckle direction (-Y,
  read off isolated front/side renders) needs to end up along the `Hand.L` bone's
  actual head→tail direction — computed exactly with
  `mathutils.Vector.rotation_difference()` rather than guessed by eye, and this
  part was correct from the first real-pipeline render.
- Hand **position** (`offset_frac`) was not correct at first, for two compounding
  reasons: the offset-mirror bug above (issue 3), and an initial offset far too
  small in magnitude. Like the boot, the `Hand.L` bone head sits **inside** the
  hidden `mesh_regions.hand` window (`x=0.689`, well within `[0.5, 0.8]`), so the
  visible forearm stump ends noticeably further back toward the elbow than the
  bone head — placing the wrist cap AT the bone head with no/a small offset
  leaves it floating well clear of the stump. This was under-corrected in the
  first pass (a small nudge that merely looked plausible from one misleading
  crop angle) and only became obvious once a wide, unclipped render showed both
  wrists visibly disconnected from their arms. Fixed the same rigorous way as the
  boot: measured the actual remaining stump vertices closest to the bone's own
  axis line, measured the placed hand mesh's own wrist-face position for several
  candidate offsets along the bone direction, and picked the offset (roughly
  10% of the bone's length, back toward the elbow) where the two numbers meet.

Both traits are wired into the `pilot` preset only for now (not `variant_b`/`_c`)
— `variant_c`'s watering can holds in the hand, and a closed-fist replacement
mesh's visual compatibility with a held item hasn't been checked yet.

### Animated (game-ready) export — the rigged customized KnitBit

**Status: built + verified.** The static preview GLBs above are QA artifacts only:
they export with **no animation** and every trait as an unskinned node, so under
any skeleton animation the body moves and all attached pieces (including the
character's own boots and hands) stay frozen. The product the platform actually
needs — *a rigged customized KnitBit the user can take into games* — is the
animated mode:

```
blender --background --python tools/build_character.py -- pilot anim=1
# -> knitbit_pilot_preview_anim.glb  (rigged, Idle clip included)
```

`anim=1` builds on `knitbit_base_idle.glb`, **bakes every fitted prop to world
space** (glTF viewers ignore a skinned mesh's node transform — placement must
live in the vertices and bind matrices; mirrored instances get their inverted
winding flipped back), **rigid-weights every vertex to the prop's attach bone**
(socket empties carry `attach_bone` extras from the rig script; `limb_pair`
traits carry the bone directly), and exports **with** the Idle clip.

Verified the way an engine sees it — fresh import of the exported GLB:
- all 10 pilot props move with their bones through the Idle clip;
- a first check flagged boots/charm "frozen", which turned out to be the Idle
  clip simply not animating Hips/Feet (it is a chest-sway + head-nod clip);
  manually posing those bones proved all bindings follow (deltas 0.05–0.15).

Every build also emits `<stem>_pfp.png` — a square 512 head-and-shoulders
portrait at a 3/4 angle (framed wide enough for tall head traits like the
headphone band): the **profile picture** applied to the user's account.
`glb=0` renders without re-exporting GLBs.

### Web bundle + live character editor

**Status: built + verified end-to-end.** The raw assets are far too heavy for a
browser editor (one prop: 32k verts + ~13.5 MB textures; one assembled GLB:
~95 MB). `tools/export_web_bundle.py` produces `assets/3d/knitbit_base/web/`
(~20 MB for the whole library):

| File | Contents |
| --- | --- |
| `base.glb` (4 MB) | Idle-animated rigged base, body **split into named toggleable parts** (`base_core`, `base_hand_l/r`, `base_foot_l/r`, cut along the same `mesh_regions` windows) — the editor equips boots/hands by toggling part visibility, no client-side vertex surgery. Textures ≤1024. |
| `piece_<trait>.glb` (0.6–1.4 MB each) | Every trait, exact builder placement, baked to world space, decimated to ≤9k tris, textures ≤512, `knitbit_attach_bone`/pivot extras on each node. |
| `manifest.web.json` | Slots, traits (file/attachments/hides), themes, **colorways**, presets — everything the editor needs. |
| `web/yarn_<theme>.jpg` + `web/tiles/*.jpg` | Runtime yarn colorway textures (11, from `tools/make_yarn_colorways.py`) and 160px photo tiles (from the trait thumbs) for the editor's tile grid. |

`demos/knitbit_builder.html` (three.js, vendored in `demos/vendor/`) is the
customization platform prototype, **v2 UI** per user direction — no dropdowns:
a **tab bar** (one tab per slot) over a **photo tile grid** (thumb per trait +
a "None" tile, selected ring), a **Yarn color** swatch row (runtime
`material.map` swap to the colorway textures), a per-slot **Accent color**
tint row, and **Idle / Wave / Bounce** clip buttons (AnimationMixer crossfade).
The KnitBit **stands in 3D with the Idle clip looping**, **live updates** as
tiles are clicked (pieces `bone.attach()`ed via rest-pose matrices so equipping
is animation-time independent; mesh-swap traits toggle base part visibility),
the belt charm swings on a **runtime pendulum**, and **"Save look & take
profile picture"** captures a square portrait and applies it to the profile
widget (+ download). Run `python3 -m http.server` at the repo root and open
`/demos/knitbit_builder.html`.

v2 also hardens the failure modes behind the earlier "boots and gloves missing"
report: piece/fetch failures show a visible error banner (plus an explicit
"serve over http://" message under `file://`), bone lookups fall back to
GLTFLoader's sanitized names (`Foot.L` → `FootL` — the v1 root cause), base
parts are hidden **only after** a piece successfully attaches (a failed boot
load can never leave the character footless), and `window.__KB.debug()` exposes
piece/part visibility for automated assertions.

Verified with headless Chromium (Playwright, `e2e` run 2026-07): zero failures;
base feet/hands hidden with 2 boot + 2 hand meshes visible; idle motion and the
Wave clip confirmed by pixel-diff; tab+tile equip (scout antenna); yarn
colorway swap changes 80k torso pixels; accent tint applied; PFP capture
(357 KB) applied to the profile. Two earlier bugs this harness caught remain
documented: `scene.add(light).position.set(...)` translated the whole scene,
and a second `WebGLRenderer` captured an empty PFP (separate GL context).

### Not yet built (future builder work)
- **More boot/hand options**: only one pick exists per slot so far (matching how
  Phase A proved one option per slot before Phase B scaled to three) — the
  mechanism is proven, the library isn't.
- **Boots/hands + a held item in the same preset**: needs a look at whether a
  closed-fist hand mesh reads correctly around a handheld prop (`variant_c`).
- **Theme material-swap** (§7): yarn/accent color is a material change, not a mesh —
  a `theme` field already tags each trait; the assembler doesn't yet apply a palette.
- **Compatibility / rarity rules** (build-order step 8): the data layer that says
  which traits may coexist and how often — a natural companion file to the manifest.
- **Large GLBs → Git LFS:** assembled preview GLBs exceed GitHub's 50 MB warning;
  move `*.glb` to LFS before the library grows. (The web bundle side-steps this —
  its 20 MB total is committed fine — but the raw previews still trip it.)
- **Editor → account wiring**: the builder prototype captures the PFP and applies
  it to a mock profile widget; persisting the loadout + PFP to a real user
  account/backend (and handing the `anim=1` GLB to games) is platform work.
- **Richer idle**: the current clip is chest-sway + head-nod only (the editor
  adds a small procedural hip bob). A fuller authored idle (weight shift, foot
  roll) means extending `tools/rig_knitbit.py`'s clip and re-exporting the base.
