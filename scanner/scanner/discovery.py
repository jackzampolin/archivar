"""mDNS/Zeroconf discovery for finding shelf-go servers on the network."""

import logging
import socket
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

from zeroconf import ServiceBrowser, ServiceListener, Zeroconf

logger = logging.getLogger(__name__)

# Service type for shelf-go servers
SHELF_SERVICE_TYPE = "_shelf._tcp.local."


@dataclass
class DiscoveredServer:
    """A discovered shelf-go server."""
    name: str
    host: str
    port: int
    addresses: list[str]

    @property
    def display_name(self) -> str:
        """Human-readable name for UI."""
        return self.name.replace("._shelf._tcp.local.", "")


class ShelfServiceListener(ServiceListener):
    """Listener for shelf-go service announcements."""

    def __init__(self, on_found: Callable[[DiscoveredServer], None],
                 on_removed: Callable[[str], None]):
        self.on_found = on_found
        self.on_removed = on_removed
        self._zeroconf: Optional[Zeroconf] = None

    def set_zeroconf(self, zc: Zeroconf):
        self._zeroconf = zc

    def add_service(self, zc: Zeroconf, service_type: str, name: str):
        """Called when a service is discovered."""
        info = zc.get_service_info(service_type, name)
        if info:
            addresses = [socket.inet_ntoa(addr) for addr in info.addresses]
            server = DiscoveredServer(
                name=name,
                host=info.server or addresses[0] if addresses else "unknown",
                port=info.port,
                addresses=addresses
            )
            logger.info(f"Discovered shelf server: {server.display_name} at {server.host}:{server.port}")
            self.on_found(server)

    def remove_service(self, zc: Zeroconf, service_type: str, name: str):
        """Called when a service is removed."""
        logger.info(f"Shelf server removed: {name}")
        self.on_removed(name)

    def update_service(self, zc: Zeroconf, service_type: str, name: str):
        """Called when a service is updated."""
        # Treat update as a new discovery
        self.add_service(zc, service_type, name)


class ServerDiscovery:
    """Handles discovery of shelf-go servers on the local network."""

    def __init__(self):
        self._zeroconf: Optional[Zeroconf] = None
        self._browser: Optional[ServiceBrowser] = None
        self._servers: dict[str, DiscoveredServer] = {}
        self._lock = threading.Lock()
        self._callbacks: list[Callable[[list[DiscoveredServer]], None]] = []

    def start(self):
        """Start listening for shelf-go servers."""
        if self._zeroconf is not None:
            return

        self._zeroconf = Zeroconf()
        listener = ShelfServiceListener(
            on_found=self._on_server_found,
            on_removed=self._on_server_removed
        )
        listener.set_zeroconf(self._zeroconf)

        self._browser = ServiceBrowser(
            self._zeroconf,
            SHELF_SERVICE_TYPE,
            listener
        )
        logger.info("Started shelf server discovery")

    def stop(self):
        """Stop listening for servers."""
        if self._zeroconf:
            self._zeroconf.close()
            self._zeroconf = None
            self._browser = None
        logger.info("Stopped shelf server discovery")

    def _on_server_found(self, server: DiscoveredServer):
        """Handle discovered server."""
        with self._lock:
            self._servers[server.name] = server
            self._notify_callbacks()

    def _on_server_removed(self, name: str):
        """Handle removed server."""
        with self._lock:
            if name in self._servers:
                del self._servers[name]
                self._notify_callbacks()

    def _notify_callbacks(self):
        """Notify all callbacks of server list change."""
        servers = list(self._servers.values())
        for callback in self._callbacks:
            try:
                callback(servers)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def on_servers_changed(self, callback: Callable[[list[DiscoveredServer]], None]):
        """Register a callback for server list changes."""
        self._callbacks.append(callback)

    @property
    def servers(self) -> list[DiscoveredServer]:
        """Get list of currently discovered servers."""
        with self._lock:
            return list(self._servers.values())

    def scan_manual(self, hosts: list[str], port: int = 8080,
                    timeout: float = 2.0) -> list[DiscoveredServer]:
        """
        Manually scan a list of hosts for shelf-go servers.
        Useful when mDNS isn't working or for direct IP connection.
        """
        import requests

        found = []
        for host in hosts:
            try:
                resp = requests.get(
                    f"http://{host}:{port}/health",
                    timeout=timeout
                )
                if resp.status_code == 200:
                    server = DiscoveredServer(
                        name=f"shelf@{host}",
                        host=host,
                        port=port,
                        addresses=[host]
                    )
                    found.append(server)
                    logger.info(f"Found shelf server at {host}:{port}")
            except requests.RequestException:
                pass

        return found

    def scan_subnet(self, base_ip: str = "192.168.1", port: int = 8080,
                    timeout: float = 0.5) -> list[DiscoveredServer]:
        """
        Scan a subnet for shelf-go servers.
        Warning: This can be slow. Use mDNS when possible.
        """
        import concurrent.futures
        import requests

        def check_host(ip: str) -> Optional[DiscoveredServer]:
            try:
                resp = requests.get(f"http://{ip}:{port}/health", timeout=timeout)
                if resp.status_code == 200:
                    return DiscoveredServer(
                        name=f"shelf@{ip}",
                        host=ip,
                        port=port,
                        addresses=[ip]
                    )
            except requests.RequestException:
                pass
            return None

        found = []
        hosts = [f"{base_ip}.{i}" for i in range(1, 255)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(check_host, host): host for host in hosts}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    found.append(result)

        return found
