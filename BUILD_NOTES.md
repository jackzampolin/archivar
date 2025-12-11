# Archivar Book Scanner Build Notes

## Project Goal
Build an Archivar book scanner from the open-source CAD files, modernizing components where needed and sourcing everything in the US.

---

## Camera Decision

**Chosen: Arducam 16MP USB Autofocus Camera (x2)**
- Amazon: https://www.amazon.com/Arducam-Autofocus-Computer-Microphone-Windows/dp/B08S347RJ7
- Price: ~$52 each ($104 total)
- Resolution: 16MP (4656x3496)
- Interface: USB (plug-and-play with Raspberry Pi)
- Features: Autofocus, built-in microphone

**Why this over original Canon cameras:**
- Original design used Canon PowerShot ELPH 160 / IXUS 160 (2015 era, 20MP)
- Those cameras are discontinued and hard to find
- Arducam is modern, available, USB-native (no CHDK hacking needed)
- 16MP is plenty for book scanning (even 600dpi scans get downsampled for OCR)
- USB cameras work directly with Raspberry Pi without CSI ribbon cables

**Note:** May want to search Thingiverse/Printables for 3D printed enclosures for Arducam cameras.

---

## CAD Files Status

### Main Structure Options

| File | Material | Size (mm) | Status |
|------|----------|-----------|--------|
| `proto116_laser_18mm.dxf` | 18mm plywood | 2578 x 1794 | Too large for 4x8 sheet (2440x1220mm) |
| `proto117_laser_8mm.dxf` | 8mm plywood | ~4990 x 2424 | Too large, sandwich option |
| `proto117_laser_10mm.dxf` | 10mm plywood | ~4990 x 2424 | Too large, sandwich option |

### Lighting Module
| File | Material | Status |
|------|----------|--------|
| `proto116_laserteile_4mm.dxf` | 4mm plywood | Needs review, SendCutSend has 3.2mm |

### TODO: Re-nesting
The DXF files need to be re-nested to fit on standard 4x8 (2440x1220mm) sheets. Options:
1. Use DeepNest (free online nesting tool)
2. Manual CAD work in FreeCAD/LibreCAD
3. Contact a laser cutting service that offers nesting

---

## SendCutSend Material Considerations

**Available plywood thicknesses at SendCutSend:**
- 3.2mm (close to 4mm needed for lighting)
- 6.3mm
- 9mm
- 12mm

**Thickness Strategy:**
- For 18mm: Use 9mm x2, glue together
- For 4mm lighting module: Use 3.2mm (slightly thinner)
- For 8mm+10mm sandwich: Use 9mm x2 (slightly different but should work)

---

## Bill of Materials (US Sourcing)

### Structure & Mechanics

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Plywood sheets | 9mm, 4x8 ft | 2-4 | For main structure (glue for 18mm) |
| Plywood sheet | 3.2mm | 1 | For lighting module |
| Aluminum profile | 20x20mm, ~500mm | 2 | Camera rail |
| Linear bearings | For 20x20 profile | 4 | Camera adjustment |
| Threaded rod | M8, ~400mm | 2 | Height adjustment |
| Nuts & bolts | M4, M5, M8 assorted | Various | Assembly |
| Wood screws | Various sizes | Box | Structure assembly |
| Wood glue | Titebond or similar | 1 | Laminating 9mm sheets |

### Electronics

| Item | Spec | Qty | Source | Price |
|------|------|-----|--------|-------|
| Arducam 16MP USB | Autofocus | 2 | Amazon | $104 |
| Raspberry Pi 4 | 4GB+ | 1 | Various | ~$55 |
| Pi 7" Touchscreen | Official | 1 | Various | ~$70 |
| USB Foot Pedal | Tiardey/similar | 1 | Amazon | ~$15 |
| GU10 Light Fixtures | Spot mount | 2 | Amazon | ~$20 |
| LED Bulbs | SORAA MR16-GU10 7.5W or equivalent | 2 | Amazon | ~$30 |
| Power supply | For Pi + lights | 1 | Various | ~$15 |
| USB Hub | Powered, 4+ ports | 1 | Amazon | ~$20 |

### Glass

| Item | Spec | Qty | Notes |
|------|------|-----|-------|
| Glass panes | 3mm TVG, 416x305mm, edges beveled, one long edge 50° bevel | 2 | Custom order from local glass shop |

### Optional/Nice-to-have

| Item | Notes |
|------|-------|
| Lenticular lens sheet | 10LPI 3.25mm - reduces glare (original design had this) |
| 3D printed camera mounts | Search Thingiverse for Arducam enclosures |
| Cable management | Zip ties, cable clips |

---

## Software Stack

The scanner will integrate with the **Shelf** project:
- `/Users/johnzampolin/go/src/github.com/jackzampolin/shelf`
- Vision-powered book digitization pipeline
- Converts scanned images to ePub
- Uses Claude for OCR and content structuring

---

## Next Steps

1. [ ] Re-nest DXF files to fit 4x8 sheets (use DeepNest or similar)
2. [ ] Order materials from SendCutSend once nesting is complete
3. [ ] Order Arducam cameras (2x) from Amazon
4. [ ] Order Raspberry Pi 4 + touchscreen
5. [ ] Get glass panes cut locally
6. [ ] Source remaining hardware (aluminum profile, bearings, fasteners)
7. [ ] Assemble and integrate with Shelf software

---

## Reference Links

- Original Archivar forum thread: https://diybookscanner.org/forum/viewtopic.php?f=14&t=3452
- Arducam 16MP: https://www.amazon.com/Arducam-Autofocus-Computer-Microphone-Windows/dp/B08S347RJ7
- SendCutSend: https://app.sendcutsend.com
- DeepNest (nesting tool): https://deepnest.io
