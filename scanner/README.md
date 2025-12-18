# Scanner Service

RPi touchscreen app for capturing book pages and streaming to shelf-go.

## Usage

```bash
pip install -e .
scanner --kiosk    # Fullscreen on touchscreen
scanner --debug    # Development mode
```

## Controls

| Input | Action |
|-------|--------|
| CAPTURE button | Capture both pages |
| Space / B / Foot pedal | Capture both pages |
| Setup | Configure cameras and server |

## Hardware

- Raspberry Pi 4 + 7" touchscreen
- 2x Arducam 16MP USB cameras
- USB foot pedal (optional)
