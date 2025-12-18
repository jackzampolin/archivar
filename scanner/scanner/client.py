"""HTTP client for communicating with shelf-go server."""

import logging
import requests
import threading
from dataclasses import dataclass
from queue import Queue, Empty
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)

# Timeout for HTTP requests
REQUEST_TIMEOUT = 30


class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ServerInfo:
    """Information about a shelf-go server."""
    host: str
    port: int
    name: str = "shelf"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


@dataclass
class UploadResult:
    """Result of an image upload."""
    success: bool
    page_number: int
    job_id: Optional[str] = None
    error: Optional[str] = None


class ShelfClient:
    """Client for shelf-go server communication."""

    def __init__(self):
        self.server: Optional[ServerInfo] = None
        self.status = ConnectionStatus.DISCONNECTED
        self.book_id: Optional[str] = None
        self._session = requests.Session()

    def connect(self, host: str, port: int = 8080) -> bool:
        """Connect to a shelf-go server."""
        self.server = ServerInfo(host=host, port=port)
        self.status = ConnectionStatus.CONNECTING

        try:
            # Check server health
            resp = self._session.get(
                f"{self.server.base_url}/health",
                timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 200:
                self.status = ConnectionStatus.CONNECTED
                logger.info(f"Connected to shelf server at {self.server.base_url}")
                return True
            else:
                self.status = ConnectionStatus.ERROR
                logger.error(f"Server returned {resp.status_code}")
                return False
        except requests.RequestException as e:
            self.status = ConnectionStatus.ERROR
            logger.error(f"Failed to connect to server: {e}")
            return False

    def disconnect(self):
        """Disconnect from the server."""
        self.server = None
        self.book_id = None
        self.status = ConnectionStatus.DISCONNECTED

    def check_connection(self) -> bool:
        """Check if still connected to server."""
        if not self.server:
            return False

        try:
            resp = self._session.get(
                f"{self.server.base_url}/health",
                timeout=5
            )
            connected = resp.status_code == 200
            self.status = ConnectionStatus.CONNECTED if connected else ConnectionStatus.ERROR
            return connected
        except requests.RequestException:
            self.status = ConnectionStatus.ERROR
            return False

    def start_book(self, title: str = "Untitled") -> Optional[str]:
        """Start a new book scanning session."""
        if not self.server or self.status != ConnectionStatus.CONNECTED:
            logger.error("Not connected to server")
            return None

        try:
            resp = self._session.post(
                f"{self.server.base_url}/api/books",
                json={"title": title, "source": "scanner"},
                timeout=REQUEST_TIMEOUT
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                self.book_id = data.get("id")
                logger.info(f"Started book: {self.book_id}")
                return self.book_id
            else:
                logger.error(f"Failed to start book: {resp.status_code}")
                return None
        except requests.RequestException as e:
            logger.error(f"Failed to start book: {e}")
            return None

    def upload_page(self, image_data: bytes, page_number: int) -> UploadResult:
        """Upload a scanned page image."""
        if not self.server or self.status != ConnectionStatus.CONNECTED:
            return UploadResult(
                success=False,
                page_number=page_number,
                error="Not connected to server"
            )

        if not self.book_id:
            return UploadResult(
                success=False,
                page_number=page_number,
                error="No active book session"
            )

        try:
            # Upload image as multipart form data
            files = {
                'image': (f'page_{page_number:04d}.jpg', image_data, 'image/jpeg')
            }
            data = {
                'book_id': self.book_id,
                'page_number': page_number
            }

            resp = self._session.post(
                f"{self.server.base_url}/api/pages",
                files=files,
                data=data,
                timeout=REQUEST_TIMEOUT
            )

            if resp.status_code in (200, 201):
                result = resp.json()
                return UploadResult(
                    success=True,
                    page_number=page_number,
                    job_id=result.get("job_id")
                )
            else:
                return UploadResult(
                    success=False,
                    page_number=page_number,
                    error=f"Server returned {resp.status_code}"
                )

        except requests.RequestException as e:
            return UploadResult(
                success=False,
                page_number=page_number,
                error=str(e)
            )

    def get_status(self) -> dict:
        """Get detailed server status."""
        if not self.server:
            return {"connected": False}

        try:
            resp = self._session.get(
                f"{self.server.base_url}/status",
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                data["connected"] = True
                return data
            return {"connected": False}
        except requests.RequestException:
            return {"connected": False}


class AsyncUploader:
    """Handles asynchronous image uploads with a queue."""

    def __init__(self, client: ShelfClient):
        self.client = client
        self._queue: Queue[tuple[bytes, int]] = Queue()
        self._worker: Optional[threading.Thread] = None
        self._running = False
        self._pending_count = 0
        self._lock = threading.Lock()
        self._results: list[UploadResult] = []

    def start(self):
        """Start the upload worker thread."""
        if self._worker is not None:
            return

        self._running = True
        self._worker = threading.Thread(target=self._upload_worker, daemon=True)
        self._worker.start()
        logger.info("Upload worker started")

    def stop(self):
        """Stop the upload worker thread."""
        self._running = False
        if self._worker:
            self._worker.join(timeout=5)
            self._worker = None
        logger.info("Upload worker stopped")

    def queue_upload(self, image_data: bytes, page_number: int):
        """Queue an image for upload."""
        with self._lock:
            self._pending_count += 1
        self._queue.put((image_data, page_number))
        logger.debug(f"Queued page {page_number} for upload")

    def _upload_worker(self):
        """Worker thread that processes upload queue."""
        while self._running:
            try:
                image_data, page_number = self._queue.get(timeout=0.5)
            except Empty:
                continue

            result = self.client.upload_page(image_data, page_number)

            with self._lock:
                self._pending_count -= 1
                self._results.append(result)
                # Keep only last 100 results
                if len(self._results) > 100:
                    self._results = self._results[-100:]

            if result.success:
                logger.info(f"Uploaded page {page_number}")
            else:
                logger.error(f"Failed to upload page {page_number}: {result.error}")

    @property
    def pending_count(self) -> int:
        """Number of uploads pending."""
        with self._lock:
            return self._pending_count

    @property
    def recent_results(self) -> list[UploadResult]:
        """Get recent upload results."""
        with self._lock:
            return list(self._results)
