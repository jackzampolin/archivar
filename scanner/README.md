# Archivar Scanner Service

Control software for the Archivar book scanner. Runs on a Raspberry Pi with a 7" touchscreen, managing dual USB cameras and streaming captured pages to a shelf-go server for OCR processing.

## Architecture

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│      Scanner (RPi)          │         │     Laptop (shelf-go)       │
│                             │   WiFi  │                             │
│  ┌───────────┐              │ ──────► │  ┌───────────────────────┐  │
│  │ Cameras   │──► capture   │  POST   │  │ Job Queue / Pipeline  │  │
│  └───────────┘    + send ───┼─────────┼─►│ OCR → Label → ePub    │  │
│                             │         │  └───────────────────────┘  │
│  ┌───────────┐              │         │                             │
│  │ Touchscreen│ status/     │ ◄───────│  Full UI + Storage          │
│  │    UI     │  preview     │         │                             │
│  └───────────┘              │         └─────────────────────────────┘
└─────────────────────────────┘
```

## Installation

```bash
# On the Raspberry Pi
cd scanner
pip install -e .
```

## Usage

```bash
# Run with default settings
scanner

# Run in kiosk mode (fullscreen on touchscreen)
scanner --kiosk

# Custom port
scanner --port 8000

# Debug mode
scanner --debug
```

## Features

- **Dual camera capture**: Captures left and right pages simultaneously
- **Live preview**: Real-time camera preview on touchscreen via WebSocket
- **Server discovery**: Finds shelf-go servers on the network via mDNS
- **Async upload**: Pages are queued and uploaded in the background
- **Touch-optimized UI**: Big buttons, clear status indicators

## UI Controls

- **CAPTURE**: Capture both pages (also: spacebar, 'b' key, or foot pedal)
- **Setup**: Configure cameras and server connection
- **New Book / End Book**: Start or end a scanning session

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space / B | Capture |
| Escape | Back / Cancel |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main UI |
| `/api/status` | GET | Scanner status |
| `/api/cameras` | GET | List available cameras |
| `/api/cameras/configure` | POST | Configure camera assignments |
| `/api/cameras/swap` | POST | Swap left/right cameras |
| `/api/servers` | GET | List discovered shelf servers |
| `/api/connect` | POST | Connect to a shelf server |
| `/api/session/start` | POST | Start a new book session |
| `/api/session/end` | POST | End current session |
| `/api/capture` | POST | Capture a page spread |

## Hardware Requirements

- Raspberry Pi 4 (4GB+ recommended)
- 7" Official Raspberry Pi Touchscreen (800x480)
- 2x Arducam 16MP USB Autofocus cameras
- USB foot pedal (optional, sends 'b' key)

## Configuration

The scanner auto-detects cameras and discovers shelf servers on the network. Manual configuration is available in the Setup screen.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black scanner/
ruff check scanner/
```
