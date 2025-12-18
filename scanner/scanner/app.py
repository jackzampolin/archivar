"""Flask application for scanner touchscreen UI."""

import logging
import os
import threading
import time
from typing import Optional

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from .camera import DualCameraController, CaptureResult
from .client import ShelfClient, AsyncUploader, ConnectionStatus
from .discovery import ServerDiscovery, DiscoveredServer

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
app.config['SECRET_KEY'] = 'scanner-secret-key'

# Initialize SocketIO with gevent for WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Global state (initialized in create_app)
cameras: Optional[DualCameraController] = None
client: Optional[ShelfClient] = None
uploader: Optional[AsyncUploader] = None
discovery: Optional[ServerDiscovery] = None

# Scanner state
scanner_state = {
    'page_count': 0,
    'book_title': 'Untitled',
    'session_active': False,
}


def create_app() -> Flask:
    """Create and configure the Flask application."""
    global cameras, client, uploader, discovery

    # Initialize components
    cameras = DualCameraController()
    client = ShelfClient()
    uploader = AsyncUploader(client)
    discovery = ServerDiscovery()

    # Start background services
    discovery.start()
    uploader.start()

    # Start preview streaming thread
    preview_thread = threading.Thread(target=_preview_stream_loop, daemon=True)
    preview_thread.start()

    return app


def _preview_stream_loop():
    """Background thread that streams camera previews via WebSocket."""
    while True:
        if cameras and cameras.is_ready:
            try:
                left_preview, right_preview = cameras.get_previews()
                socketio.emit('preview', {
                    'left': left_preview,
                    'right': right_preview
                })
            except Exception as e:
                logger.error(f"Preview error: {e}")
        time.sleep(0.1)  # ~10 FPS preview


# =============================================================================
# HTTP Routes
# =============================================================================

@app.route('/')
def index():
    """Main scanner UI."""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """Get current scanner status."""
    return jsonify({
        'cameras_ready': cameras.is_ready if cameras else False,
        'server_connected': client.status == ConnectionStatus.CONNECTED if client else False,
        'server_url': client.server.base_url if client and client.server else None,
        'page_count': scanner_state['page_count'],
        'book_title': scanner_state['book_title'],
        'session_active': scanner_state['session_active'],
        'pending_uploads': uploader.pending_count if uploader else 0,
    })


@app.route('/api/cameras')
def api_cameras():
    """Get available cameras."""
    if not cameras:
        return jsonify({'cameras': []})

    detected = cameras.detect_cameras()
    return jsonify({
        'cameras': [
            {'device_id': c.device_id, 'name': c.name}
            for c in detected
        ]
    })


@app.route('/api/cameras/configure', methods=['POST'])
def api_configure_cameras():
    """Configure camera assignments."""
    data = request.json
    left_id = data.get('left')
    right_id = data.get('right')

    if left_id is None or right_id is None:
        return jsonify({'error': 'Must specify left and right camera IDs'}), 400

    success = cameras.configure(int(left_id), int(right_id))
    return jsonify({'success': success})


@app.route('/api/cameras/swap', methods=['POST'])
def api_swap_cameras():
    """Swap left and right cameras."""
    if cameras:
        cameras.swap_cameras()
    return jsonify({'success': True})


@app.route('/api/servers')
def api_servers():
    """Get discovered shelf servers."""
    if not discovery:
        return jsonify({'servers': []})

    return jsonify({
        'servers': [
            {'name': s.display_name, 'host': s.host, 'port': s.port}
            for s in discovery.servers
        ]
    })


@app.route('/api/connect', methods=['POST'])
def api_connect():
    """Connect to a shelf server."""
    data = request.json
    host = data.get('host')
    port = data.get('port', 8080)

    if not host:
        return jsonify({'error': 'Must specify host'}), 400

    success = client.connect(host, int(port))
    return jsonify({
        'success': success,
        'status': client.status.value
    })


@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    """Disconnect from shelf server."""
    if client:
        client.disconnect()
    scanner_state['session_active'] = False
    return jsonify({'success': True})


@app.route('/api/session/start', methods=['POST'])
def api_start_session():
    """Start a new book scanning session."""
    data = request.json or {}
    title = data.get('title', 'Untitled')

    if not client or client.status != ConnectionStatus.CONNECTED:
        return jsonify({'error': 'Not connected to server'}), 400

    book_id = client.start_book(title)
    if book_id:
        scanner_state['session_active'] = True
        scanner_state['book_title'] = title
        scanner_state['page_count'] = 0
        return jsonify({'success': True, 'book_id': book_id})
    else:
        return jsonify({'error': 'Failed to start book session'}), 500


@app.route('/api/session/end', methods=['POST'])
def api_end_session():
    """End the current scanning session."""
    scanner_state['session_active'] = False
    return jsonify({'success': True})


@app.route('/api/capture', methods=['POST'])
def api_capture():
    """Capture a page spread (both cameras)."""
    if not cameras or not cameras.is_ready:
        return jsonify({'error': 'Cameras not ready'}), 400

    if not scanner_state['session_active']:
        return jsonify({'error': 'No active scanning session'}), 400

    result = cameras.capture()

    if result.success:
        page_num = scanner_state['page_count']

        # Queue uploads
        if result.left_image:
            uploader.queue_upload(result.left_image, page_num)
        if result.right_image:
            uploader.queue_upload(result.right_image, page_num + 1)

        scanner_state['page_count'] += 2

        # Notify via WebSocket
        socketio.emit('capture', {
            'success': True,
            'page_count': scanner_state['page_count']
        })

        return jsonify({
            'success': True,
            'pages_captured': [page_num, page_num + 1],
            'total_pages': scanner_state['page_count']
        })
    else:
        socketio.emit('capture', {
            'success': False,
            'error': result.error
        })
        return jsonify({'error': result.error}), 500


# =============================================================================
# WebSocket Events
# =============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info("Client connected")
    emit('status', {
        'cameras_ready': cameras.is_ready if cameras else False,
        'server_connected': client.status == ConnectionStatus.CONNECTED if client else False,
        'page_count': scanner_state['page_count'],
    })


@socketio.on('capture')
def handle_capture_event():
    """Handle capture request via WebSocket."""
    # Trigger capture through the API
    with app.test_request_context():
        result = api_capture()
        # Response is sent via the 'capture' emit in api_capture


@socketio.on('ping')
def handle_ping():
    """Handle ping for connection keep-alive."""
    emit('pong')


def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """Run the scanner server."""
    create_app()
    logger.info(f"Starting scanner server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)
