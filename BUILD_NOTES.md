# Build Decisions

Hardware decisions made for this build. See `BOM.csv` for full parts list with links.

## Camera: Arducam 16MP USB Autofocus

Chosen over original Canon PowerShot ELPH 160 because:
- Canon cameras discontinued (2015 era)
- Arducam is USB-native (no CHDK firmware hacking)
- Autofocus simplifies software
- 16MP sufficient for OCR workloads

## Material Strategy (SendCutSend)

SendCutSend available thicknesses: 3.2mm, 6.3mm, 9mm, 12mm

| Original spec | Substitute | Notes |
|---------------|------------|-------|
| 18mm plywood | 9mm x2 | Glue together |
| 4mm lighting | 3.2mm | Slightly thinner |
| 8mm+10mm sandwich | 9mm x2 | Close enough |

## CAD File Sizes

The original DXF files exceed standard 4x8 sheet size (2440x1220mm):

| File | Size (mm) |
|------|-----------|
| proto116_laser_18mm.dxf | 2578 x 1794 |
| proto117_laser_8mm.dxf | ~4990 x 2424 |
| proto117_laser_10mm.dxf | ~4990 x 2424 |

Parts have been extracted to `CAD/individual_parts/` and organized for ordering in `CAD/sendcutsend_order/`.

## Links

- [Original Archivar forum thread](https://diybookscanner.org/forum/viewtopic.php?f=14&t=3452)
- [Arducam 16MP](https://www.amazon.com/Arducam-Autofocus-Computer-Microphone-Windows/dp/B08S347RJ7)
- [SendCutSend](https://app.sendcutsend.com)
- [DeepNest (nesting tool)](https://deepnest.io)
