/**
 * Archivar Scanner - Touchscreen UI
 */

// State
const state = {
    connected: false,
    camerasReady: false,
    sessionActive: false,
    pageCount: 0,
    bookTitle: '',
    pendingUploads: 0,
};

// Socket.IO connection
let socket = null;

// DOM Elements
const elements = {};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    cacheElements();
    initSocket();
    initEventListeners();
    refreshStatus();
    refreshServers();
    refreshCameras();
});

function cacheElements() {
    elements.scanView = document.getElementById('scan-view');
    elements.settingsView = document.getElementById('settings-view');
    elements.connectionStatus = document.getElementById('connection-status');
    elements.serverName = document.getElementById('server-name');
    elements.bookTitle = document.getElementById('book-title');
    elements.pageCount = document.getElementById('page-count');
    elements.previewLeft = document.getElementById('preview-left');
    elements.previewRight = document.getElementById('preview-right');
    elements.placeholderLeft = document.getElementById('placeholder-left');
    elements.placeholderRight = document.getElementById('placeholder-right');
    elements.btnCapture = document.getElementById('btn-capture');
    elements.btnSettings = document.getElementById('btn-settings');
    elements.btnSession = document.getElementById('btn-session');
    elements.sessionBtnText = document.getElementById('session-btn-text');
    elements.btnBack = document.getElementById('btn-back');
    elements.serverList = document.getElementById('server-list');
    elements.cameraList = document.getElementById('camera-list');
    elements.serverIp = document.getElementById('server-ip');
    elements.serverPort = document.getElementById('server-port');
    elements.btnConnect = document.getElementById('btn-connect');
    elements.btnSwapCameras = document.getElementById('btn-swap-cameras');
    elements.btnDetectCameras = document.getElementById('btn-detect-cameras');
    elements.modalOverlay = document.getElementById('modal-overlay');
    elements.inputBookTitle = document.getElementById('input-book-title');
    elements.btnCancelBook = document.getElementById('btn-cancel-book');
    elements.btnStartBook = document.getElementById('btn-start-book');
    elements.toast = document.getElementById('toast');
}

function initSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('WebSocket connected');
    });

    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
    });

    socket.on('preview', (data) => {
        if (data.left) {
            elements.previewLeft.src = 'data:image/jpeg;base64,' + data.left;
            elements.previewLeft.classList.add('active');
            elements.placeholderLeft.classList.add('hidden');
        }
        if (data.right) {
            elements.previewRight.src = 'data:image/jpeg;base64,' + data.right;
            elements.previewRight.classList.add('active');
            elements.placeholderRight.classList.add('hidden');
        }
    });

    socket.on('capture', (data) => {
        if (data.success) {
            state.pageCount = data.page_count;
            elements.pageCount.textContent = state.pageCount;

            // Flash effect
            elements.previewLeft.classList.add('capture-flash');
            elements.previewRight.classList.add('capture-flash');
            setTimeout(() => {
                elements.previewLeft.classList.remove('capture-flash');
                elements.previewRight.classList.remove('capture-flash');
            }, 300);

            showToast('Captured pages ' + (data.page_count - 1) + ' & ' + data.page_count, 'success');
        } else {
            showToast('Capture failed: ' + data.error, 'error');
        }
    });

    socket.on('status', (data) => {
        updateStatus(data);
    });
}

function initEventListeners() {
    // Navigation
    elements.btnSettings.addEventListener('click', () => showView('settings'));
    elements.btnBack.addEventListener('click', () => showView('scan'));

    // Capture
    elements.btnCapture.addEventListener('click', capture);

    // Session
    elements.btnSession.addEventListener('click', handleSessionButton);
    elements.btnCancelBook.addEventListener('click', hideModal);
    elements.btnStartBook.addEventListener('click', startBook);
    elements.inputBookTitle.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') startBook();
    });

    // Server connection
    elements.btnConnect.addEventListener('click', connectManual);

    // Camera controls
    elements.btnSwapCameras.addEventListener('click', swapCameras);
    elements.btnDetectCameras.addEventListener('click', refreshCameras);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === ' ' || e.key === 'b') {
            e.preventDefault();
            if (!elements.btnCapture.disabled) {
                capture();
            }
        }
        if (e.key === 'Escape') {
            if (!elements.modalOverlay.classList.contains('hidden')) {
                hideModal();
            } else if (elements.settingsView.classList.contains('active')) {
                showView('scan');
            }
        }
    });
}

// View management
function showView(view) {
    elements.scanView.classList.remove('active');
    elements.settingsView.classList.remove('active');

    if (view === 'settings') {
        elements.settingsView.classList.add('active');
        refreshServers();
        refreshCameras();
    } else {
        elements.scanView.classList.add('active');
    }
}

// Status updates
async function refreshStatus() {
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        updateStatus(data);
    } catch (err) {
        console.error('Failed to get status:', err);
    }
}

function updateStatus(data) {
    state.connected = data.server_connected;
    state.camerasReady = data.cameras_ready;
    state.sessionActive = data.session_active;
    state.pageCount = data.page_count || 0;
    state.bookTitle = data.book_title || '';
    state.pendingUploads = data.pending_uploads || 0;

    // Update UI
    elements.connectionStatus.className = 'status-indicator ' +
        (state.connected ? 'connected' : 'disconnected');
    elements.serverName.textContent = data.server_url || 'Not connected';
    elements.bookTitle.textContent = state.sessionActive ? state.bookTitle : '-';
    elements.pageCount.textContent = state.pageCount;

    // Capture button state
    elements.btnCapture.disabled = !state.camerasReady || !state.sessionActive;

    // Session button
    if (state.sessionActive) {
        elements.sessionBtnText.textContent = 'End Book';
    } else {
        elements.sessionBtnText.textContent = 'New Book';
    }
}

// Helper to clear all children from an element
function clearChildren(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

// Helper to create a loading message
function createLoadingElement(message) {
    const div = document.createElement('div');
    div.className = 'loading';
    div.textContent = message;
    return div;
}

// Helper to create a server item element
function createServerItem(server) {
    const item = document.createElement('div');
    item.className = 'server-item';
    item.dataset.host = server.host;
    item.dataset.port = server.port;

    const content = document.createElement('div');

    const name = document.createElement('div');
    name.className = 'name';
    name.textContent = server.name;
    content.appendChild(name);

    const address = document.createElement('div');
    address.className = 'address';
    address.textContent = server.host + ':' + server.port;
    content.appendChild(address);

    item.appendChild(content);

    item.addEventListener('click', () => {
        connectToServer(server.host, server.port);
    });

    return item;
}

// Helper to create a camera item element
function createCameraItem(cam) {
    const item = document.createElement('div');
    item.className = 'camera-item';
    item.dataset.id = cam.device_id;

    const name = document.createElement('div');
    name.className = 'name';
    name.textContent = cam.name;
    item.appendChild(name);

    const address = document.createElement('div');
    address.className = 'address';
    address.textContent = 'Device ' + cam.device_id;
    item.appendChild(address);

    return item;
}

// Server discovery
async function refreshServers() {
    clearChildren(elements.serverList);
    elements.serverList.appendChild(createLoadingElement('Searching...'));

    try {
        const resp = await fetch('/api/servers');
        const data = await resp.json();

        clearChildren(elements.serverList);

        if (data.servers.length === 0) {
            elements.serverList.appendChild(createLoadingElement('No servers found'));
            return;
        }

        data.servers.forEach(server => {
            elements.serverList.appendChild(createServerItem(server));
        });
    } catch (err) {
        clearChildren(elements.serverList);
        elements.serverList.appendChild(createLoadingElement('Error searching'));
    }
}

async function connectToServer(host, port) {
    try {
        const resp = await fetch('/api/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ host, port: parseInt(port) })
        });
        const data = await resp.json();

        if (data.success) {
            showToast('Connected to server', 'success');
            refreshStatus();
            showView('scan');
        } else {
            showToast('Connection failed', 'error');
        }
    } catch (err) {
        showToast('Connection error', 'error');
    }
}

function connectManual() {
    const host = elements.serverIp.value.trim();
    const port = elements.serverPort.value || '8080';

    if (!host) {
        showToast('Enter server IP', 'error');
        return;
    }

    connectToServer(host, port);
}

// Camera management
async function refreshCameras() {
    clearChildren(elements.cameraList);
    elements.cameraList.appendChild(createLoadingElement('Detecting...'));

    try {
        const resp = await fetch('/api/cameras');
        const data = await resp.json();

        clearChildren(elements.cameraList);

        if (data.cameras.length === 0) {
            elements.cameraList.appendChild(createLoadingElement('No cameras found'));
            return;
        }

        data.cameras.forEach(cam => {
            elements.cameraList.appendChild(createCameraItem(cam));
        });

        // Auto-configure if we have exactly 2 cameras
        if (data.cameras.length >= 2) {
            configureCameras(data.cameras[0].device_id, data.cameras[1].device_id);
        }
    } catch (err) {
        clearChildren(elements.cameraList);
        elements.cameraList.appendChild(createLoadingElement('Error detecting'));
    }
}

async function configureCameras(leftId, rightId) {
    try {
        const resp = await fetch('/api/cameras/configure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ left: leftId, right: rightId })
        });
        const data = await resp.json();

        if (data.success) {
            state.camerasReady = true;
            refreshStatus();
        }
    } catch (err) {
        console.error('Failed to configure cameras:', err);
    }
}

async function swapCameras() {
    try {
        await fetch('/api/cameras/swap', { method: 'POST' });
        showToast('Cameras swapped', 'success');
    } catch (err) {
        showToast('Swap failed', 'error');
    }
}

// Capture
async function capture() {
    if (elements.btnCapture.disabled) return;

    elements.btnCapture.disabled = true;

    try {
        const resp = await fetch('/api/capture', { method: 'POST' });
        const data = await resp.json();

        if (!data.success && data.error) {
            showToast('Capture failed: ' + data.error, 'error');
        }
    } catch (err) {
        showToast('Capture error', 'error');
    }

    // Re-enable after short delay to prevent double-capture
    setTimeout(() => {
        elements.btnCapture.disabled = !state.camerasReady || !state.sessionActive;
    }, 500);
}

// Session management
function handleSessionButton() {
    if (state.sessionActive) {
        endSession();
    } else {
        showModal();
    }
}

function showModal() {
    elements.modalOverlay.classList.remove('hidden');
    elements.inputBookTitle.value = '';
    elements.inputBookTitle.focus();
}

function hideModal() {
    elements.modalOverlay.classList.add('hidden');
}

async function startBook() {
    const title = elements.inputBookTitle.value.trim() || 'Untitled';

    try {
        const resp = await fetch('/api/session/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        const data = await resp.json();

        if (data.success) {
            hideModal();
            showToast('Started: ' + title, 'success');
            refreshStatus();
        } else {
            showToast(data.error || 'Failed to start', 'error');
        }
    } catch (err) {
        showToast('Error starting book', 'error');
    }
}

async function endSession() {
    try {
        await fetch('/api/session/end', { method: 'POST' });
        showToast('Book session ended', 'success');
        refreshStatus();
    } catch (err) {
        showToast('Error ending session', 'error');
    }
}

// Toast notifications
function showToast(message, type) {
    elements.toast.textContent = message;
    elements.toast.className = 'toast' + (type ? ' ' + type : '');

    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, 3000);
}

// Periodic status refresh
setInterval(refreshStatus, 5000);
