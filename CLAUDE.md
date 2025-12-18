# Archivar

DIY book scanner hardware + software for digitizing physical books.

## What This Is

A laser-cut plywood book scanner (based on David Smutny's open-source design) with modernized electronics and software. The scanner captures page spreads which are sent to [shelf-go](https://github.com/jackzampolin/shelf-go) for OCR processing into ePubs/audiobooks.

## Repository Structure

```
archivar/
├── scanner/          # RPi touchscreen control software (Python/Flask)
├── src/archivar/     # DXF file processing library
├── scripts/          # Build tools (part extraction)
├── notebooks/        # DXF visualization experiments
├── CAD/              # Laser-cut design files (DXF)
├── reference/        # Hardware specs from original design
├── Logo/             # Branding assets
└── BOM.csv           # Bill of materials
```

## Key Components

**scanner/** - Flask + SocketIO app for the 7" RPi touchscreen. Controls dual USB cameras, streams pages to shelf-go server. Run with `scanner --kiosk`.

**src/archivar/** - Python library for loading DXF files and converting 2D profiles to 3D geometry using build123d. Install with `pip install -e .`

**CAD/** - Original DXF files for laser cutting. Two build options: single 18mm layer or 8mm+10mm sandwich.

## Hardware

- Raspberry Pi 4 (4GB+) with 7" touchscreen
- 2x Arducam 16MP USB autofocus cameras
- Laser-cut plywood frame
- GU10 LED lighting

## Information Hygiene

This repo follows strict temporal boundaries:

| Zone | Contains | Location |
|------|----------|----------|
| Past | How we got here | Git history, closed issues |
| Present | What works now | Working tree |
| Future | What we might do | GitHub issues |

**No TODOs in code.** Create an issue instead.
**No stale comments.** Delete or update.
**No speculative docs.** Plans live in GitHub issues.

## Development

```bash
# Scanner service
cd scanner && pip install -e . && scanner

# DXF library
pip install -e . && python -c "from archivar import load_dxf"
```

## Related

- [shelf-go](https://github.com/jackzampolin/shelf-go) - OCR pipeline that processes scanned pages
- [Original Archivar thread](https://diybookscanner.org/forum/viewtopic.php?f=14&t=3452)
