#!/usr/bin/env python3
"""
Archivar Scanner - Main entry point

This is the control software for the Archivar book scanner.
It runs on a Raspberry Pi with a touchscreen and dual USB cameras,
capturing page spreads and sending them to a shelf-go server for processing.

Usage:
    scanner                    # Run with defaults (port 5000)
    scanner --port 8000        # Custom port
    scanner --debug            # Enable debug mode
    scanner --kiosk            # Launch in kiosk mode (fullscreen chromium)
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import time
from typing import Optional

# Configure logging before importing app modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger('scanner')


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Archivar Scanner - Book scanning control software'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to listen on (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--kiosk',
        action='store_true',
        help='Launch in kiosk mode (fullscreen browser)'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )
    return parser.parse_args()


def launch_kiosk(url: str) -> Optional[subprocess.Popen]:
    """Launch Chromium in kiosk mode for touchscreen display."""
    try:
        # Check if we're on a system with a display
        display = os.environ.get('DISPLAY')
        if not display:
            logger.warning("No DISPLAY set, skipping kiosk mode")
            return None

        # Launch Chromium in kiosk mode
        cmd = [
            'chromium-browser',
            '--kiosk',
            '--noerrdialogs',
            '--disable-infobars',
            '--disable-session-crashed-bubble',
            '--disable-restore-session-state',
            '--incognito',
            url
        ]

        logger.info(f"Launching kiosk browser: {url}")
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except FileNotFoundError:
        logger.warning("Chromium not found, trying firefox")
        try:
            cmd = ['firefox', '--kiosk', url]
            return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            logger.error("No suitable browser found for kiosk mode")
            return None
    except Exception as e:
        logger.error(f"Failed to launch kiosk browser: {e}")
        return None


def open_browser(url: str):
    """Open the default browser to the scanner UI."""
    import webbrowser
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.warning(f"Could not open browser: {e}")


def main():
    """Main entry point."""
    args = parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    # Import app here to avoid circular imports
    from .app import run_server, cameras, client, uploader, discovery

    url = f"http://localhost:{args.port}"
    browser_proc: Optional[subprocess.Popen] = None

    # Handle shutdown gracefully
    def shutdown(signum, frame):
        logger.info("Shutting down...")

        # Close browser if we launched it
        if browser_proc:
            browser_proc.terminate()

        # Cleanup resources
        if cameras:
            cameras.close()
        if uploader:
            uploader.stop()
        if discovery:
            discovery.stop()

        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Launch browser after a short delay (give server time to start)
    def delayed_browser_launch():
        time.sleep(1.5)
        if args.kiosk:
            nonlocal browser_proc
            browser_proc = launch_kiosk(url)
        elif not args.no_browser:
            open_browser(url)

    if not args.no_browser or args.kiosk:
        import threading
        threading.Thread(target=delayed_browser_launch, daemon=True).start()

    # Print startup info
    logger.info("=" * 50)
    logger.info("  Archivar Scanner")
    logger.info("=" * 50)
    logger.info(f"  UI: {url}")
    logger.info(f"  Mode: {'Kiosk' if args.kiosk else 'Normal'}")
    logger.info("=" * 50)
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("")

    # Run the server
    run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
