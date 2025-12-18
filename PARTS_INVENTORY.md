# Archivar Book Scanner - Parts Inventory

This document cross-references the PDF technical drawings with the DXF laser cut files.

---

## Summary

| DXF File | Material | Parts Count | Status |
|----------|----------|-------------|--------|
| proto116_laser_18mm.dxf | 18mm plywood | ~25 unique parts | Single-layer design |
| proto117_laser_8mm.dxf | 8mm plywood | ~18 unique parts | Sandwich design (8mm layer) |
| proto117_laser_10mm.dxf | 10mm plywood | ~22 unique parts | Sandwich design (10mm layer) |
| proto116_laserteile_4mm.dxf | 4mm plywood | ~8 unique parts | Lighting module |

**Design Options:**
- **Option A (proto116):** Single 18mm plywood + 4mm lighting module
- **Option B (proto117):** Sandwich of 8mm + 10mm plywood (=18mm total) + 4mm lighting module

---

## Plywood Parts - Cross Reference

### Main Structure (18mm or 8+10mm sandwich)

| Part # | German Name | English Name | Dimensions (mm) | Qty | In 18mm DXF | In 8mm DXF | In 10mm DXF |
|--------|-------------|--------------|-----------------|-----|-------------|------------|-------------|
| 100 | bildschirmplatte | Screen plate | 710 x 166 | 1 | Y | Y | Y |
| 101 | füße | Feet | 94 x 44.5 | 4 | Y | Y | Y |
| 104 | hebel_kurz | Short lever | ~80mm | 4 | Y | Y | Y |
| 105 | hebel_lang | Long lever | ~100mm | 4 | Y | Y | Y |
| 106 | seitenplatte | Side plate | 416 x 740 | 2 | Y | Y | Y |
| 107 | seitenteil_wagen | Carriage side | - | 2 | Y | Y | Y |
| 200 | wagen_basis | Carriage base | 456 x 216 | 1 | Y | Y (8mm) | Y (10mm) |
| 201 | wagenflügel | Carriage wing | 355 x 291.5 | 2 | Y | Y | Y |
| 202 | wagenwinkel_links | Left carriage angle | - | 4 | Y | Y (8mm) | Y (10mm) |
| 204 | spanngriff | Clamp handle (star knob) | ~60mm dia | 6 | Y | Y (8mm) | Y (8mm) |
| 205 | spannstück_wagen | Carriage clamp piece | 113.5 x 30 | 4 | Y | Y | Y |
| 300 | kamerabefestigung | Camera mount | 416 x 71 | 2 | Y | Y | Y |
| 301 | frontplatte | Front plate (V-cradle) | 746 x 560.8 | 1 | Y | Y | Y |
| 302 | verstrebung | Support brace | 416 x 71 | 2 | Y | - | - |
| 409 | dose / lampenführung | Lamp guide body | 380 x 80 | 2 | Y | Y | Y |

### Additional Parts in Sandwich Design (8+10mm only)

| Part Name | Description | In 8mm | In 10mm |
|-----------|-------------|--------|---------|
| holzeinlage_griff | Handle wood insert | Y | Y |
| holzflach_basisprofil_innen | Base profile inner wood flat | Y | Y |
| holzflach_wagenprofil_innen_2 | Carriage profile inner wood flat | Y | Y |

### Lighting Module (4mm plywood)

| Part # | German Name | English Name | Qty | In 4mm DXF |
|--------|-------------|--------------|-----|------------|
| 400 | lampenplatte_unten | Bottom lamp plate | 2 | Y |
| 401 | lampenplatte_mitte | Middle lamp plate | 2 | Y |
| 402 | lampenplatte_oben | Top lamp plate | 2 | Y |
| 403 | dachplatte | Roof plate | 2 | Y |
| 404 | frontplatte_lichtmodul | Light module front plate | 2 | Y |
| 405 | umlenkplatte_groß | Large deflector plate | 2 | Y |
| 406 | fenster | Window | 2 | Y |
| 407 | umlenkplatte_klein | Small deflector plate | 2 | Y |
| 408 | dose | Socket/housing | 2 | Y |
| - | plättchen | Small plates | 4 | Y |

---

## Aluminum/Metal Parts (Not in DXF - Buy or Machine)

| Part # | German Name | English Name | Dimensions | Qty | Source |
|--------|-------------|--------------|------------|-----|--------|
| 509 | wagenprofil | Carriage profile | 710mm, 25x25mm square tube | 2 | Buy & cut |
| 510 | basisprofil | Base profile | 710mm, 30x30mm square tube | 2 | Buy, drill & cut |
| 511 | rohr | Tube (handle) | 752.2mm, Ø25mm round tube | 1 | Buy & cut |
| 512 | aluwinkel | Aluminum angle | 250mm, 20x40mm angle | 2 | Buy & machine |

---

## Hardware & Fasteners (Buy)

| Part # | German Name | English Name | Spec | Qty |
|--------|-------------|--------------|------|-----|
| 500 | rampa_muffe_M4.1 | M4 threaded insert | M4 Rampa | ~8 |
| 501 | rampa_muffe_M8 | M8 threaded insert | M8 Rampa | ~12 |
| 502 | schraube_M4x20 | M4x20 screw | M4x20 | ~8 |
| 503 | schraube_M8x40 | M8x40 screw | M8x40 | ~8 |
| 504 | rändelschraube_M4x20 | M4x20 knurled screw | M4x20 thumb | ~4 |
| 505 | scheibe_M4 | M4 washer | M4 | ~8 |
| 506 | scheibe_M8 | M8 washer | M8 | ~16 |
| 102 | formrohrverbinder_klein | Small tube connector | For 25x25 profile | 4 |
| 103 | formrohrverbinder_groß | Large tube connector | For 30x30 profile | 4 |
| 114 | formrohrverbinder_griff | Handle tube connector | For grip bar | 2 |

---

## Other Materials

| Item | German | English | Spec | Qty |
|------|--------|---------|------|-----|
| 513 | epdm-gummistreifen | EPDM rubber strip | 312mm x 20mm | 6 strips |
| 513 | dichtprofil_aluwinkel | Seal profile for angle | Rubber | ~1m |
| - | filzstreifen | Felt strip | For glass edge | ~1m |
| - | Glas | Glass panes | 3mm TVG, 416x305mm, beveled edges | 2 |

---

## DXF Layer Analysis

### proto116_laser_18mm.dxf (18mm single layer)
Key part layers identified:
- `bildschirmplatte_1` - Screen plate
- `füße_1` - Feet (multiple copies)
- `seitenplatte_1` - Side plates
- `frontplatte_301` - Front V-cradle
- `wagen_basis_200` - Carriage base
- `wagenflügel_1` - Carriage wings
- `wagenwinkel_links_202` - Left carriage angles
- `spanngriff` - Star knobs
- `spannstück_wagen` - Clamp pieces
- `kamerabefestigung` - Camera mounts
- `hebel_kurz_104` / `hebel_lang_105` - Levers
- `dose_409` - Lamp guide bodies

### proto117_laser_8mm.dxf (8mm sandwich layer)
Contains thinner versions of main parts plus:
- `holzeinlage_griff` - Handle inserts
- `holzflach_basisprofil_innen` - Inner base profile pieces
- `holzflach_wagenprofil_innen_2` - Inner carriage profile pieces

### proto117_laser_10mm.dxf (10mm sandwich layer)
Contains complementary thicknesses plus assembly reference layers

### proto116_laserteile_4mm.dxf (4mm lighting module)
- `lampenplatte_unten_400` - Bottom lamp plate
- `lampenplatte_mitte_401` - Middle lamp plate
- `lampenplatte_oben_402` - Top lamp plate
- `dachplatte_1_1` - Roof plate
- `frontplatte_lichtmodul_404` - Light module front
- `umlenkplatte_groß_405` - Large deflector
- `umlenkplatte_klein_1_1` - Small deflector
- `fenster_406` - Window
- `dose_1_408` - Socket/housing
- `plättchen` - Small plates

---

## Recommended Build Approach

### For US Sourcing with SendCutSend:

**Option 1: Use proto116 (18mm single layer)**
- Simpler assembly (single layer)
- SendCutSend has 12mm max plywood, so use 9mm x2 glued
- Need to re-nest parts to fit 4x8 sheets

**Option 2: Use proto117 (8+10mm sandwich)**
- More complex (two layers per part)
- SendCutSend has 9mm (close to both 8mm and 10mm)
- Could use 9mm for both layers (18mm total when glued)

**Lighting Module:**
- Use 3.2mm plywood (SendCutSend's closest to 4mm)
- Slightly thinner but should work

---

## Extracted Individual Parts

Individual part DXF files have been extracted to `CAD/individual_parts/` using the script `scripts/extract_dxf_parts.py`.

**Folder Structure:**
```
CAD/individual_parts/
├── 01_main_frame/       # Side plates, front plate, screen plate, feet, levers
│   ├── 18mm/            # For proto116 single-layer build
│   ├── 8mm/             # For proto117 sandwich build (layer 1)
│   └── 10mm/            # For proto117 sandwich build (layer 2)
├── 02_carriage/         # Book carriage and clamp parts
├── 03_camera_mount/     # Camera mounting plates
├── 04_lighting_module/  # Lamp plates, deflectors, windows
│   ├── 4mm/             # Main lighting parts
│   └── 10mm/            # Reference parts
└── 05_profile_inserts/  # Wood inserts for aluminum profiles (sandwich only)
```

**Total: 74 individual DXF files**

To re-nest for laser cutting:
1. Choose your build option (18mm single or 8+10mm sandwich)
2. Gather DXF files from the appropriate thickness folders
3. Use DeepNest (https://deepnest.io) to pack onto 4x8 sheets
4. Export nested layout for SendCutSend or your laser cutting service

---

## PDF Drawing Reference

The `CAD/drawings_all.pdf` contains 18 pages of detailed part drawings with:
- Precise dimensions
- Hole locations and diameters
- Assembly instructions (in German: "Bearbeitungsablauf")
- Part numbers matching this inventory

Key pages:
- Page 1: Part 100 (bildschirmplatte)
- Page 2: Part 101 (füße)
- Page 5: Part 106 (seitenplatte)
- Page 7: Part 200 (wagen_basis)
- Page 8: Part 201 (wagenflügel)
- Page 11: Part 300 (kamerabefestigung)
- Page 12: Part 301 (frontplatte)
- Page 14: Part 409 (lampenführung)
