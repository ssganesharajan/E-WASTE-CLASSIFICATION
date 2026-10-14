/**
 * EcoSort IoT Cloud Dashboard - Industrial AI Telemetry & E-Waste Classification Client
 */

// Global State
const STATE = {
    isAuthenticated: false,
    currentUser: null,
    currentTab: 'tab-telemetry',
    sourceMode: 'esp32', // 'esp32' | 'webcam' | 'upload'
    esp32Url: 'http://10.111.211.153',
    isAutoPolling: false,
    pollInterval: null,
    webcamStream: null,
    uploadedFile: null,
    selectedModelFile: null,
    activeModelInfo: {},
    classesDb: [],
    history: [],
    stats: {}
};

const API_BASE = ''; // Same-origin when served from FastAPI

// =========================================================================
// Initialization
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initNavigation();
    initDeviceSelector();
    initUploadDropzone();
    initModelManager();
    initHardwareSettings();
    initActionButtons();
    initFullscreen();
    initCatalogFilters();
    initAuditLogControls();
    initImageModal();

    // Start HUD Clock
    setInterval(updateHudClock, 1000);

    // Initial Data Fetch
    checkAuthSession();
});

function updateHudClock() {
    const el = document.getElementById('hud-timestamp');
    if (el) {
        el.textContent = `SYNC: ${new Date().toISOString().slice(11, 19)} UTC`;
    }
}

// =========================================================================
// Authentication (Admin / 12345678)
// =========================================================================

function initAuth() {
    const loginForm = document.getElementById('login-form');
    const btnLogin = document.getElementById('btn-login-submit');
    const btnFillDemo = document.getElementById('btn-fill-demo');
    const btnLogout = document.getElementById('btn-logout');

    if (btnLogin) {
        btnLogin.addEventListener('click', handleLoginSubmit);
    }

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleLoginSubmit();
        });
    }

    if (btnFillDemo) {
        btnFillDemo.addEventListener('click', () => {
            document.getElementById('login-username').value = 'Admin';
            document.getElementById('login-password').value = '12345678';
            document.getElementById('login-error-alert').style.display = 'none';
        });
    }

    if (btnLogout) {
        btnLogout.addEventListener('click', handleLogout);
    }
}

function checkAuthSession() {
    const token = localStorage.getItem('ecosort_token');
    const userStr = localStorage.getItem('ecosort_user');

    if (token && userStr) {
        try {
            STATE.currentUser = JSON.parse(userStr);
            STATE.isAuthenticated = true;
            unlockDashboard(STATE.currentUser);
            loadInitialDashboardData();
            return;
        } catch (e) {
            console.error('Failed to parse user session:', e);
        }
    }

    // Default: Show login overlay
    showLoginOverlay();
}

async function handleLoginSubmit() {
    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const errorAlert = document.getElementById('login-error-alert');
    const errorText = document.getElementById('login-error-text');

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
        errorText.textContent = 'Please enter both User ID and Password.';
        errorAlert.style.display = 'flex';
        return;
    }

    try {
        const resp = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!resp.ok) {
            const errData = await resp.json();
            throw new Error(errData.detail || 'Authentication failed');
        }

        const data = await resp.json();
        localStorage.setItem('ecosort_token', data.token);
        localStorage.setItem('ecosort_user', JSON.stringify(data.user));

        STATE.isAuthenticated = true;
        STATE.currentUser = data.user;

        errorAlert.style.display = 'none';
        unlockDashboard(data.user);
        loadInitialDashboardData();

    } catch (err) {
        errorText.textContent = err.message || 'Invalid User ID or Password.';
        errorAlert.style.display = 'flex';
    }
}

function unlockDashboard(user) {
    document.getElementById('login-overlay').style.display = 'none';
    document.getElementById('app-container').style.display = 'flex';
    
    const userDisplay = document.getElementById('nav-user-display');
    if (userDisplay) {
        userDisplay.textContent = user.username || 'Admin';
    }
}

function showLoginOverlay() {
    document.getElementById('login-overlay').style.display = 'flex';
    document.getElementById('app-container').style.display = 'none';
}

function handleLogout() {
    if (!confirm('Are you sure you want to sign out?')) return;
    localStorage.removeItem('ecosort_token');
    localStorage.removeItem('ecosort_user');
    STATE.isAuthenticated = false;
    STATE.currentUser = null;

    // Stop streams
    if (STATE.webcamStream) stopWebcam();
    if (STATE.isAutoPolling) toggleAutoPolling();

    showLoginOverlay();
}

function loadInitialDashboardData() {
    checkSystemStatus();
    loadCatalogClasses();
    loadScanHistory();
    loadAnalytics();
    loadModelInfo();

    // Periodic health check
    setInterval(checkSystemStatus, 8000);
}

// =========================================================================
// Navigation & Tabs
// =========================================================================

function initNavigation() {
    const navButtons = document.querySelectorAll('.tb-nav-item');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            switchTab(targetTab);
            closeMobileNav();
        });
    });

    const btnNavUpload = document.getElementById('btn-nav-upload');
    if (btnNavUpload) {
        btnNavUpload.addEventListener('click', () => {
            switchTab('tab-telemetry');
            setSourceMode('upload');
            const fileInput = document.getElementById('file-input');
            if (fileInput && !STATE.uploadedFile) {
                fileInput.click();
            }
            closeMobileNav();
        });
    }

    const btnNavModel = document.getElementById('btn-nav-model');
    if (btnNavModel) {
        btnNavModel.addEventListener('click', () => {
            switchTab('tab-device-config');
            closeMobileNav();
        });
    }

    // Mobile Drawer Toggle
    const btnMobileMenu = document.getElementById('btn-mobile-menu');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');

    if (btnMobileMenu) {
        btnMobileMenu.addEventListener('click', () => {
            const sidebar = document.querySelector('.tb-sidebar');
            if (sidebar) sidebar.classList.toggle('mobile-open');
            if (sidebarBackdrop) sidebarBackdrop.classList.toggle('mobile-open');
        });
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', closeMobileNav);
    }
}

function closeMobileNav() {
    const sidebar = document.querySelector('.tb-sidebar');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.remove('mobile-open');
    if (sidebarBackdrop) sidebarBackdrop.classList.remove('mobile-open');
}

function switchTab(tabId) {
    STATE.currentTab = tabId;

    // Update active nav button
    document.querySelectorAll('.tb-nav-item').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
    });

    // Update active tab pane
    document.querySelectorAll('.tb-tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === tabId);
    });

    // Refresh context data
    if (tabId === 'tab-events') {
        loadScanHistory();
    } else if (tabId === 'tab-analytics') {
        loadAnalytics();
    } else if (tabId === 'tab-device-config') {
        loadModelInfo();
    } else if (tabId === 'tab-classes') {
        loadCatalogClasses();
    }
}

// =========================================================================
// Device & Mode Selector
// =========================================================================

function initDeviceSelector() {
    const deviceSelect = document.getElementById('device-select');
    if (deviceSelect) {
        deviceSelect.addEventListener('change', (e) => {
            const val = e.target.value;
            if (val === 'esp32-cam-01') {
                setSourceMode('esp32');
            } else if (val === 'webcam-local') {
                setSourceMode('webcam');
            } else if (val === 'manual-ingest') {
                setSourceMode('upload');
            }
        });
    }
}

window.setSourceMode = function(mode) {
    STATE.sourceMode = mode;

    // Update Dropdown
    const deviceSelect = document.getElementById('device-select');
    if (deviceSelect) {
        if (mode === 'esp32') deviceSelect.value = 'esp32-cam-01';
        else if (mode === 'webcam') deviceSelect.value = 'webcam-local';
        else if (mode === 'upload') deviceSelect.value = 'manual-ingest';
    }

    // Update Mode Buttons
    const btnEsp32 = document.getElementById('mode-btn-esp32');
    const btnWebcam = document.getElementById('mode-btn-webcam');
    const btnUpload = document.getElementById('mode-btn-upload');

    if (btnEsp32) btnEsp32.classList.toggle('active', mode === 'esp32');
    if (btnWebcam) btnWebcam.classList.toggle('active', mode === 'webcam');
    if (btnUpload) btnUpload.classList.toggle('active', mode === 'upload');

    // Update Viewports
    document.getElementById('viewport-esp32').style.display = mode === 'esp32' ? 'flex' : 'none';
    document.getElementById('viewport-webcam').style.display = mode === 'webcam' ? 'flex' : 'none';
    document.getElementById('viewport-upload').style.display = mode === 'upload' ? 'flex' : 'none';

    // Update Title
    const titleEl = document.getElementById('viewport-header-title');
    if (titleEl) {
        if (mode === 'esp32') titleEl.textContent = 'ESP32-CAM Optical Sensor Feed';
        else if (mode === 'webcam') titleEl.textContent = 'Local Web Camera Ingestion';
        else titleEl.textContent = 'Manual Image Ingestion & AI Classifier';
    }

    // Shutdown webcam if leaving
    if (mode !== 'webcam' && STATE.webcamStream) {
        stopWebcam();
    }

    // Update Action Button Text
    const analyzeBtnText = document.getElementById('analyze-btn-text');
    if (analyzeBtnText) {
        if (mode === 'esp32') {
            analyzeBtnText.textContent = 'Acquire Frame from ESP32 & Classify';
        } else if (mode === 'webcam') {
            analyzeBtnText.textContent = 'Capture Web Camera Frame & Classify';
        } else {
            analyzeBtnText.textContent = 'Classify Uploaded Image';
        }
    }
};

// =========================================================================
// Fullscreen Control
// =========================================================================

function initFullscreen() {
    const btn = document.getElementById('btn-fullscreen');
    if (btn) {
        btn.addEventListener('click', () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });
    }
}

// =========================================================================
// Webcam Stream Handler
// =========================================================================

const btnStartWebcam = document.getElementById('btn-start-webcam');
if (btnStartWebcam) {
    btnStartWebcam.addEventListener('click', startWebcam);
}

async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 1280 }, height: { ideal: 720 } }
        });
        STATE.webcamStream = stream;
        const video = document.getElementById('webcam-video');
        video.srcObject = stream;
        video.style.display = 'block';
        document.getElementById('webcam-placeholder').style.display = 'none';
    } catch (err) {
        alert('Could not access webcam: ' + err.message);
    }
}

function stopWebcam() {
    if (STATE.webcamStream) {
        STATE.webcamStream.getTracks().forEach(track => track.stop());
        STATE.webcamStream = null;
        document.getElementById('webcam-video').style.display = 'none';
        document.getElementById('webcam-placeholder').style.display = 'flex';
    }
}

function captureWebcamFrame() {
    const video = document.getElementById('webcam-video');
    const canvas = document.getElementById('webcam-canvas');
    if (!video || !video.videoWidth) return null;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.9);
}

// =========================================================================
// Upload & Drag-and-Drop Handler (Manual Image Ingest)
// =========================================================================

function initUploadDropzone() {
    const dropzone = document.getElementById('dropzone-area');
    const fileInput = document.getElementById('file-input');
    const btnBrowse = document.getElementById('btn-browse-file');
    const btnClear = document.getElementById('btn-clear-upload');
    const btnSample = document.getElementById('btn-load-sample');

    if (btnBrowse) {
        btnBrowse.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    if (dropzone) {
        dropzone.addEventListener('click', () => fileInput.click());
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleSelectedImageFile(e.target.files[0]);
            }
        });
    }

    if (btnClear) {
        btnClear.addEventListener('click', (e) => {
            e.stopPropagation();
            clearUploadPreview();
        });
    }

    if (btnSample) {
        btnSample.addEventListener('click', (e) => {
            e.stopPropagation();
            loadDemoSample(3); // Default demo PCB
        });
    }

    // Attach click events for all 10 demo class palette buttons
    const paletteBtns = document.querySelectorAll('.tb-palette-btn');
    paletteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const classId = parseInt(btn.getAttribute('data-class'), 10);
            loadDemoSample(classId);
        });
    });

    const viewportUpload = document.getElementById('viewport-upload');
    if (viewportUpload) {
        viewportUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            viewportUpload.classList.add('drag-active');
        });

        viewportUpload.addEventListener('dragleave', () => {
            viewportUpload.classList.remove('drag-active');
        });

        viewportUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            viewportUpload.classList.remove('drag-active');
            if (e.dataTransfer.files.length > 0) {
                handleSelectedImageFile(e.dataTransfer.files[0]);
            }
        });
    }
}

function handleSelectedImageFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload a valid image file (JPEG, PNG, WebP, BMP).');
        return;
    }
    STATE.uploadedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        const previewBox = document.getElementById('upload-preview-box');
        const previewImg = document.getElementById('upload-preview-img');
        const fileNameEl = document.getElementById('upload-file-name');
        const fileSizeEl = document.getElementById('upload-file-size');

        previewImg.src = e.target.result;
        fileNameEl.textContent = file.name;
        fileSizeEl.textContent = formatBytes(file.size);

        previewBox.style.display = 'flex';
        document.getElementById('dropzone-area').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function clearUploadPreview() {
    STATE.uploadedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('upload-preview-box').style.display = 'none';
    document.getElementById('dropzone-area').style.display = 'flex';
}

function loadDemoSample(classId = 3) {
    const canvas = document.createElement('canvas');
    canvas.width = 320;
    canvas.height = 240;
    const ctx = canvas.getContext('2d');

    // Neutral workbench background
    ctx.fillStyle = '#737373';
    ctx.fillRect(0, 0, 320, 240);

    const classNames = [
        'Battery', 'Cable_Wires', 'Charger', 'Circuit_Board',
        'Headphones', 'Keyboard_Mouse', 'Laptop_PC', 'Mobile_Phone',
        'Monitor_Display', 'Storage_HDD'
    ];
    const sampleName = classNames[classId] || 'E_Waste_Sample';

    if (classId === 0) { // Battery: cylindrical cell with red wrap and terminal
        ctx.fillStyle = '#dc2626';
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(110, 40, 100, 160, 12); else ctx.fillRect(110, 40, 100, 160);
        ctx.fill();
        ctx.fillStyle = '#d4d4d8';
        ctx.fillRect(135, 22, 50, 18);
        ctx.fillStyle = '#fbbf24';
        ctx.font = 'bold 13px sans-serif';
        ctx.fillText('Li-Ion 3.7V', 125, 120);
    } else if (classId === 1) { // Cable & Wires: multi-colored curving cords
        const colors = ['#ef4444', '#3b82f6', '#eab308', '#22c55e', '#18181b'];
        ctx.lineWidth = 6;
        for (let j = 0; j < 5; j++) {
            ctx.strokeStyle = colors[j];
            ctx.beginPath();
            ctx.moveTo(30, 40 + j * 35);
            ctx.bezierCurveTo(120, 10 + j * 40, 200, 180 - j * 30, 290, 140 + j * 20);
            ctx.stroke();
        }
    } else if (classId === 2) { // Charger: white cube wall adapter with metal prongs
        ctx.fillStyle = '#a1a1aa';
        ctx.fillRect(130, 25, 16, 35);
        ctx.fillRect(174, 25, 16, 35);
        ctx.fillStyle = '#f8fafc';
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(100, 60, 120, 130, 10); else ctx.fillRect(100, 60, 120, 130);
        ctx.fill();
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = '#0f172a';
        ctx.font = 'bold 11px sans-serif';
        ctx.fillText('65W GAN', 135, 125);
    } else if (classId === 3) { // Circuit Board / PCB: green solder mask + gold traces + microchips
        ctx.fillStyle = '#14532d';
        ctx.fillRect(40, 30, 240, 180);
        ctx.strokeStyle = '#22c55e';
        ctx.lineWidth = 3;
        for (let i = 0; i < 6; i++) {
            ctx.beginPath();
            ctx.moveTo(50, 45 + i * 26);
            ctx.lineTo(130, 45 + i * 26);
            ctx.lineTo(180, 65 + i * 24);
            ctx.lineTo(270, 65 + i * 24);
            ctx.stroke();
        }
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(120, 80, 80, 80);
        ctx.strokeStyle = '#cbd5e1';
        ctx.strokeRect(120, 80, 80, 80);
        ctx.fillStyle = '#00f5d4';
        ctx.font = 'bold 10px monospace';
        ctx.fillText('ECO-SORT AI', 128, 125);
    } else if (classId === 4) { // Headphones & Audio Gear: headband arc + dual ear cups
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 10;
        ctx.beginPath();
        ctx.arc(160, 110, 70, Math.PI, 0);
        ctx.stroke();
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        ctx.ellipse(85, 140, 24, 40, 0, 0, 2 * Math.PI);
        ctx.ellipse(235, 140, 24, 40, 0, 0, 2 * Math.PI);
        ctx.fill();
    } else if (classId === 5) { // Keyboard & Mouse: keycap grid
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(40, 60, 240, 120);
        ctx.fillStyle = '#475569';
        for (let r = 0; r < 4; r++) {
            for (let c = 0; c < 10; c++) {
                ctx.fillRect(48 + c * 23, 68 + r * 26, 18, 18);
            }
        }
    } else if (classId === 6) { // Laptop & Computer: clamshell display + keyboard deck
        ctx.fillStyle = '#090d16';
        ctx.fillRect(60, 30, 200, 95);
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.moveTo(35, 185);
        ctx.lineTo(285, 185);
        ctx.lineTo(260, 125);
        ctx.lineTo(60, 125);
        ctx.closePath();
        ctx.fill();
    } else if (classId === 7) { // Mobile Phone: vertical dark screen
        ctx.fillStyle = '#0a0a0f';
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(110, 20, 100, 200, 14); else ctx.fillRect(110, 20, 100, 200);
        ctx.fill();
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.fillStyle = '#334155';
        ctx.beginPath();
        ctx.arc(160, 32, 4, 0, 2 * Math.PI);
        ctx.fill();
    } else if (classId === 8) { // Monitor & Display: widescreen display + stand
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(40, 30, 240, 135);
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 4;
        ctx.strokeRect(40, 30, 240, 135);
        ctx.fillStyle = '#64748b';
        ctx.fillRect(152, 165, 16, 35);
        ctx.fillRect(120, 200, 80, 12);
    } else if (classId === 9) { // Storage HDD: metallic enclosure + circular platter
        ctx.fillStyle = '#94a3b8';
        ctx.fillRect(60, 30, 200, 180);
        ctx.fillStyle = '#e2e8f0';
        ctx.beginPath();
        ctx.arc(160, 120, 60, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = '#475569';
        ctx.beginPath();
        ctx.arc(160, 120, 18, 0, 2 * Math.PI);
        ctx.fill();
    }

    canvas.toBlob((blob) => {
        const file = new File([blob], `${sampleName.toLowerCase()}_sample.jpg`, { type: 'image/jpeg' });
        handleSelectedImageFile(file);
    }, 'image/jpeg', 0.92);
}

function loadDemoSampleImage() {
    loadDemoSample(3);
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(2) + ' MB';
}

// =========================================================================
// AI Neural Model Manager & Hot-Reload Hub
// =========================================================================

function initModelManager() {
    const modelDropzone = document.getElementById('model-dropzone');
    const modelFileInput = document.getElementById('model-file-input');
    const btnBrowseModel = document.getElementById('btn-browse-model');
    const btnClearModel = document.getElementById('btn-clear-selected-model');
    const btnUploadSubmit = document.getElementById('btn-upload-model-submit');
    const btnResetModel = document.getElementById('btn-reset-default-model');

    if (btnBrowseModel) {
        btnBrowseModel.addEventListener('click', (e) => {
            e.stopPropagation();
            modelFileInput.click();
        });
    }

    if (modelDropzone) {
        modelDropzone.addEventListener('click', () => modelFileInput.click());

        modelDropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            modelDropzone.classList.add('drag-active');
        });

        modelDropzone.addEventListener('dragleave', () => {
            modelDropzone.classList.remove('drag-active');
        });

        modelDropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            modelDropzone.classList.remove('drag-active');
            if (e.dataTransfer.files.length > 0) {
                handleSelectedModelFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (modelFileInput) {
        modelFileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleSelectedModelFile(e.target.files[0]);
            }
        });
    }

    if (btnClearModel) {
        btnClearModel.addEventListener('click', clearSelectedModel);
    }

    if (btnUploadSubmit) {
        btnUploadSubmit.addEventListener('click', handleModelUploadSubmit);
    }

    if (btnResetModel) {
        btnResetModel.addEventListener('click', handleModelReset);
    }
}

function handleSelectedModelFile(file) {
    if (!file.name.toLowerCase().endsWith('.tflite')) {
        alert('Please select a TensorFlow Lite model file with .tflite extension.');
        return;
    }
    STATE.selectedModelFile = file;

    const banner = document.getElementById('selected-model-banner');
    const nameEl = document.getElementById('selected-model-filename');
    const sizeEl = document.getElementById('selected-model-filesize');

    nameEl.textContent = file.name;
    sizeEl.textContent = `(${formatBytes(file.size)})`;
    banner.style.display = 'flex';
}

function clearSelectedModel() {
    STATE.selectedModelFile = null;
    document.getElementById('model-file-input').value = '';
    document.getElementById('selected-model-banner').style.display = 'none';
}

async function loadModelInfo() {
    try {
        const resp = await fetch(`${API_BASE}/api/model/info`);
        if (resp.ok) {
            const data = await resp.json();
            STATE.activeModelInfo = data;

            // Update DOM
            const nameEl = document.getElementById('model-info-name');
            const archEl = document.getElementById('model-info-arch');
            const sizeEl = document.getElementById('model-info-size');
            const resEl = document.getElementById('model-info-res');
            const navModel = document.getElementById('active-model-name-nav');
            const sidebarModel = document.getElementById('sidebar-model-name');

            if (nameEl) nameEl.textContent = data.model_name;
            if (archEl) archEl.textContent = data.architecture || 'YOLOv8 Classifier';
            if (sizeEl) sizeEl.textContent = data.size_formatted;
            if (resEl && data.input_shape) {
                if (data.input_layout === 'NCHW' || (data.input_shape.length === 4 && data.input_shape[1] === 3)) {
                    resEl.textContent = `${data.input_shape[2]} x ${data.input_shape[3]} (NCHW)`;
                } else if (data.input_shape.length === 4) {
                    resEl.textContent = `${data.input_shape[1]} x ${data.input_shape[2]} x ${data.input_shape[3]}`;
                } else {
                    resEl.textContent = data.resolution || '224 x 224';
                }
            }
            if (navModel) navModel.textContent = data.model_name;
            if (sidebarModel) sidebarModel.textContent = data.architecture ? data.architecture.replace(' (TFLite)', '') : data.model_name;
        }
    } catch (e) {
        console.error('Failed to load model info:', e);
    }
}

async function handleModelUploadSubmit() {
    const alertBox = document.getElementById('model-feedback-alert');
    if (!STATE.selectedModelFile) {
        alertBox.className = 'tb-feedback-alert tb-feedback-error';
        alertBox.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Please select or drop a .tflite model file first.';
        alertBox.style.display = 'flex';
        return;
    }

    alertBox.className = 'tb-feedback-alert tb-feedback-success';
    alertBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Validating model tensors and hot-reloading into runtime interpreter...';
    alertBox.style.display = 'flex';

    try {
        const formData = new FormData();
        formData.append('model_file', STATE.selectedModelFile);

        const resp = await fetch(`${API_BASE}/api/model/upload`, {
            method: 'POST',
            body: formData
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Model hot-reload failed');
        }

        const data = await resp.json();
        alertBox.className = 'tb-feedback-alert tb-feedback-success';
        alertBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> <strong>Success!</strong> ${data.message}`;

        clearSelectedModel();
        loadModelInfo();
        checkSystemStatus();

    } catch (err) {
        alertBox.className = 'tb-feedback-alert tb-feedback-error';
        alertBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <strong>Upload Failed:</strong> ${err.message}`;
    }
}

async function handleModelReset() {
    if (!confirm('Restore default factory MobileNetV2 e-waste classification model?')) return;
    const alertBox = document.getElementById('model-feedback-alert');

    try {
        const resp = await fetch(`${API_BASE}/api/model/reset`, { method: 'POST' });
        if (!resp.ok) throw new Error('Reset failed');
        const data = await resp.json();

        alertBox.className = 'tb-feedback-alert tb-feedback-success';
        alertBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${data.message}`;
        alertBox.style.display = 'flex';

        loadModelInfo();
        checkSystemStatus();
    } catch (err) {
        alertBox.className = 'tb-feedback-alert tb-feedback-error';
        alertBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${err.message}`;
        alertBox.style.display = 'flex';
    }
}

// =========================================================================
// Action Buttons & Classification Triggers
// =========================================================================

let streamAutoTimer = null;

function setStreamInterval(seconds) {
    if (streamAutoTimer) {
        clearInterval(streamAutoTimer);
        streamAutoTimer = null;
    }
    if (seconds > 0) {
        streamAutoTimer = setInterval(() => {
            if (STATE.sourceMode === 'esp32' || STATE.sourceMode === 'webcam') {
                handleTriggerAnalyze();
            }
        }, seconds * 1000);
    }
}

function initActionButtons() {
    const btnTrigger = document.getElementById('btn-trigger-analyze');
    if (btnTrigger) btnTrigger.addEventListener('click', handleTriggerAnalyze);

    const btnRefresh = document.getElementById('btn-refresh-feed');
    if (btnRefresh) btnRefresh.addEventListener('click', refreshEsp32Snapshot);

    const btnToggleStream = document.getElementById('btn-toggle-auto-stream');
    if (btnToggleStream) btnToggleStream.addEventListener('click', toggleAutoPolling);

    const intervalSelect = document.getElementById('stream-interval-select');
    if (intervalSelect) {
        intervalSelect.addEventListener('change', (e) => {
            const seconds = parseInt(e.target.value, 10);
            setStreamInterval(seconds);
        });
    }

    const btnExportCsv = document.getElementById('btn-export-csv');
    if (btnExportCsv) btnExportCsv.addEventListener('click', exportHistoryCSV);

    const btnExportJson = document.getElementById('btn-export-json');
    if (btnExportJson) btnExportJson.addEventListener('click', exportHistoryJSON);

    const btnPrintReport = document.getElementById('btn-print-report');
    if (btnPrintReport) btnPrintReport.addEventListener('click', printSustainabilityReport);

    const btnClearHistory = document.getElementById('btn-clear-history');
    if (btnClearHistory) btnClearHistory.addEventListener('click', clearHistory);
}

async function handleTriggerAnalyze() {
    setLoadingState(true);

    try {
        let result;
        if (STATE.sourceMode === 'esp32') {
            const resp = await fetch(`${API_BASE}/api/analyze-esp32`, { method: 'POST' });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || 'ESP32 capture failed.');
            }
            result = await resp.json();
        } else if (STATE.sourceMode === 'webcam') {
            const frameBase64 = captureWebcamFrame();
            if (!frameBase64) {
                throw new Error('Please activate the webcam first.');
            }
            const resp = await fetch(`${API_BASE}/api/analyze-base64`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: frameBase64, source: 'Web Camera' })
            });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || 'Webcam classification failed.');
            }
            result = await resp.json();
        } else if (STATE.sourceMode === 'upload') {
            if (!STATE.uploadedFile) {
                throw new Error('Please browse or drop an e-waste image file first.');
            }
            const formData = new FormData();
            formData.append('file', STATE.uploadedFile);
            const resp = await fetch(`${API_BASE}/api/analyze-upload`, {
                method: 'POST',
                body: formData
            });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || 'Image upload classification failed.');
            }
            result = await resp.json();
        }

        renderClassificationResult(result);
        loadScanHistory();
        loadAnalytics();

    } catch (err) {
        alert(`Telemetry Ingestion Error: ${err.message}`);
        setLoadingState(false);
    }
}

function setLoadingState(isLoading) {
    document.getElementById('results-empty').style.display = 'none';
    document.getElementById('results-content').style.display = isLoading ? 'none' : 'block';
    document.getElementById('results-loading').style.display = isLoading ? 'flex' : 'none';

    // Toggle Animated Laser Scan Overlay
    const laserScanner = document.getElementById('laser-scanner');
    if (laserScanner) {
        laserScanner.style.display = isLoading ? 'block' : 'none';
    }
}

function renderClassificationResult(data) {
    setLoadingState(false);

    const pred = data.prediction;

    // Badges & Latency
    document.getElementById('inference-time-badge').textContent = `${data.inference_time_ms} ms (${data.source})`;
    document.getElementById('kpi-ai-latency').textContent = `${data.inference_time_ms} ms`;
    document.getElementById('sidebar-latency').textContent = `${data.inference_time_ms} ms`;

    // Panel Details
    document.getElementById('res-icon').textContent = pred.icon || '📦';
    document.getElementById('res-category').textContent = pred.category;
    document.getElementById('res-name').textContent = pred.name;
    document.getElementById('res-confidence').textContent = pred.confidence_percent;

    // Hazard Badge
    const hazardTag = document.getElementById('res-hazard');
    hazardTag.textContent = `Hazard: ${pred.hazard_level}`;
    hazardTag.style.backgroundColor = pred.hazard_color + '22';
    hazardTag.style.color = pred.hazard_color;
    hazardTag.style.border = `1px solid ${pred.hazard_color}55`;

    // Description
    document.getElementById('res-description').textContent = pred.description;

    // Top-3 Probability Distribution Bars
    const topContainer = document.getElementById('top-predictions-list');
    topContainer.innerHTML = '';
    (data.top_predictions || []).forEach(item => {
        const row = document.createElement('div');
        row.className = 'tb-prob-row';
        row.innerHTML = `
            <span class="tb-prob-title">${item.icon || '📦'} ${item.name}</span>
            <div class="tb-bar-track">
                <div class="tb-bar-fill" style="width: ${Math.round(item.confidence * 100)}%;"></div>
            </div>
            <span class="tb-prob-num">${item.confidence_percent}</span>
        `;
        topContainer.appendChild(row);
    });

    // Recyclable Badges
    const recContainer = document.getElementById('res-recyclable-list');
    recContainer.innerHTML = '';
    (pred.recyclable_materials || []).forEach(mat => {
        const li = document.createElement('li');
        li.textContent = mat;
        recContainer.appendChild(li);
    });

    // Hazardous Badges
    const hazContainer = document.getElementById('res-hazardous-list');
    hazContainer.innerHTML = '';
    (pred.hazardous_substances || []).forEach(sub => {
        const li = document.createElement('li');
        li.textContent = sub;
        hazContainer.appendChild(li);
    });

    // Recycling Steps
    const stepsContainer = document.getElementById('res-steps-list');
    stepsContainer.innerHTML = '';
    (pred.recycling_steps || []).forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        stepsContainer.appendChild(li);
    });

    // Impact Footer
    document.getElementById('res-co2').textContent = `${pred.co2_savings_kg} kg`;
    document.getElementById('res-recovery').textContent = pred.material_recovery_rate || '90%';
    document.getElementById('res-reuse').textContent = pred.reuse_potential ? pred.reuse_potential.split(';')[0] : 'Recycling';
}

// =========================================================================
// ESP32 Live Stream & Polling
// =========================================================================

function refreshEsp32Snapshot() {
    const streamImg = document.getElementById('esp32-stream-img');
    const placeholder = document.getElementById('esp32-placeholder');

    streamImg.src = `${API_BASE}/api/esp32/camera?t=${new Date().getTime()}`;
    streamImg.onload = () => {
        streamImg.style.display = 'block';
        placeholder.style.display = 'none';
        document.getElementById('hud-status').textContent = 'STATUS: STREAMING';
    };
    streamImg.onerror = () => {
        streamImg.style.display = 'none';
        placeholder.style.display = 'flex';
        document.getElementById('hud-status').textContent = 'STATUS: OFFLINE';
    };
}

function toggleAutoPolling() {
    STATE.isAutoPolling = !STATE.isAutoPolling;
    const btn = document.getElementById('btn-toggle-auto-stream');

    if (STATE.isAutoPolling) {
        btn.classList.add('tb-btn-primary');
        btn.innerHTML = '<i class="fa-solid fa-pause"></i> Stop Polling';
        refreshEsp32Snapshot();
        STATE.pollInterval = setInterval(refreshEsp32Snapshot, 1500);
    } else {
        btn.classList.remove('tb-btn-primary');
        btn.innerHTML = '<i class="fa-solid fa-play"></i> Auto Poll Stream';
        clearInterval(STATE.pollInterval);
    }
}

// =========================================================================
// Hardware / IoT Settings & Ping
// =========================================================================

function initHardwareSettings() {
    const btnSaveUrl = document.getElementById('btn-save-esp32-url');
    const inputUrl = document.getElementById('input-esp32-url');
    const btnPing = document.getElementById('btn-test-ping');
    const btnPingQuick = document.getElementById('btn-ping-esp32');
    const cloudIngestInput = document.getElementById('cloud-ingest-url');
    const btnCopyCloudUrl = document.getElementById('btn-copy-cloud-url');

    // Auto-detect and populate cloud ingestion URL based on current host
    if (cloudIngestInput) {
        const detectedUrl = `${window.location.origin}/upload`;
        cloudIngestInput.value = detectedUrl;
    }

    if (btnCopyCloudUrl && cloudIngestInput) {
        btnCopyCloudUrl.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(cloudIngestInput.value);
                const originalHtml = btnCopyCloudUrl.innerHTML;
                btnCopyCloudUrl.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
                setTimeout(() => { btnCopyCloudUrl.innerHTML = originalHtml; }, 2000);
            } catch (err) {
                cloudIngestInput.select();
                document.execCommand('copy');
                alert('Copied Cloud Ingestion URL to clipboard!');
            }
        });
    }

    if (btnSaveUrl) {
        btnSaveUrl.addEventListener('click', async () => {
            const url = inputUrl.value.trim();
            if (!url) return;
            try {
                const resp = await fetch(`${API_BASE}/api/esp32/update-url`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                const data = await resp.json();
                STATE.esp32Url = data.current_url;
                document.getElementById('esp32-status-text').textContent = STATE.esp32Url.replace('http://', '');
                document.getElementById('hud-ip-display').textContent = STATE.esp32Url.replace('http://', '');
                document.getElementById('esp32-url-display').textContent = `Endpoint: ${STATE.esp32Url}/capture`;
                alert(data.message);
            } catch (e) {
                alert('Failed to update URL: ' + e.message);
            }
        });
    }

    const handlePing = async () => {
        const details = document.getElementById('ping-details-content');
        if (details) {
            details.innerHTML = '<p class="tb-text-muted"><i class="fa-solid fa-spinner fa-spin"></i> Executing ICMP/HTTP ping to ESP32-CAM node...</p>';
        }
        try {
            const resp = await fetch(`${API_BASE}/api/esp32/ping`);
            const data = await resp.json();
            if (data.online) {
                if (details) {
                    details.innerHTML = `
                        <p class="text-green"><i class="fa-solid fa-circle-check"></i> <strong>Node Active & Responding!</strong></p>
                        <p>Endpoint: <code>${data.url}</code></p>
                        <p>Round-Trip Latency: <strong>${data.latency_ms} ms</strong></p>
                    `;
                }
                document.getElementById('esp32-dot').className = 'tb-dot tb-dot-success';
                refreshEsp32Snapshot();
            } else {
                if (details) {
                    details.innerHTML = `
                        <p class="text-red"><i class="fa-solid fa-triangle-exclamation"></i> <strong>Node Unreachable</strong></p>
                        <p>Target: <code>${data.url}</code></p>
                        <small class="tb-text-muted">Ensure ESP32-CAM is powered and on the same WiFi subnet.</small>
                    `;
                }
                document.getElementById('esp32-dot').className = 'tb-dot tb-dot-danger';
            }
        } catch (e) {
            if (details) details.innerHTML = `<p class="text-red">Ping failed: ${e.message}</p>`;
        }
    };

    if (btnPing) btnPing.addEventListener('click', handlePing);
    if (btnPingQuick) btnPingQuick.addEventListener('click', handlePing);
}

// =========================================================================
// Backend Status & Data Fetchers
// =========================================================================

async function checkSystemStatus() {
    try {
        const resp = await fetch(`${API_BASE}/api/status`);
        if (resp.ok) {
            const data = await resp.json();
            document.getElementById('backend-status-text').textContent = 'Online';
            document.getElementById('esp32-status-text').textContent = data.esp32_cam_url.replace('http://', '');
            document.getElementById('hud-ip-display').textContent = data.esp32_cam_url.replace('http://', '');
            document.getElementById('input-esp32-url').value = data.esp32_cam_url;
            STATE.esp32Url = data.esp32_cam_url;

            if (data.active_model) {
                const navModel = document.getElementById('active-model-name-nav');
                const sidebarModel = document.getElementById('sidebar-model-name');
                if (navModel) navModel.textContent = data.active_model;
                if (sidebarModel) sidebarModel.textContent = data.active_model;
            }
        }
    } catch (e) {
        document.getElementById('backend-status-text').textContent = 'Offline';
    }
}

// =========================================================================
// Material Catalog & Dynamic Filter Engine
// =========================================================================

let catalogFilterHazard = 'all';
let catalogSearchQuery = '';

function initCatalogFilters() {
    const searchInput = document.getElementById('catalog-search-input');
    const filterChips = document.querySelectorAll('.tb-filter-chip');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            catalogSearchQuery = e.target.value.toLowerCase().trim();
            renderCatalog();
        });
    }

    filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
            filterChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            catalogFilterHazard = chip.getAttribute('data-filter') || 'all';
            renderCatalog();
        });
    });
}

async function loadCatalogClasses() {
    try {
        const resp = await fetch(`${API_BASE}/api/classes`);
        const data = await resp.json();
        STATE.classesDb = data.classes || [];

        renderCatalog();
        initBatchSimulator();
    } catch (e) {
        console.error('Failed to load classes catalog:', e);
    }
}

function renderCatalog() {
    const grid = document.getElementById('catalog-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const filtered = STATE.classesDb.filter(c => {
        const matchesHazard = (catalogFilterHazard === 'all') || (c.hazard_level === catalogFilterHazard);
        const textBlob = `${c.name} ${c.category} ${c.description} ${(c.recyclable_materials || []).join(' ')}`.toLowerCase();
        const matchesSearch = !catalogSearchQuery || textBlob.includes(catalogSearchQuery);
        return matchesHazard && matchesSearch;
    });

    if (filtered.length === 0) {
        grid.innerHTML = '<p class="tb-text-muted tb-text-center" style="grid-column: 1/-1; padding: 40px;"><i class="fa-solid fa-magnifying-glass"></i> No e-waste classes matching current filter.</p>';
        return;
    }

    filtered.forEach(c => {
        const card = document.createElement('div');
        card.className = 'tb-catalog-card';
        card.innerHTML = `
            <div class="tb-catalog-header">
                <span class="tb-catalog-icon">${c.icon || '📦'}</span>
                <span class="tb-hazard-badge" style="background:${c.hazard_color}22; color:${c.hazard_color}; border:1px solid ${c.hazard_color}55;">
                    ${c.hazard_level} Hazard
                </span>
            </div>
            <h3 class="tb-catalog-title">${c.name}</h3>
            <div class="tb-category-tag" style="margin-bottom:8px;">${c.category}</div>
            <p class="tb-catalog-desc">${c.description}</p>
            <div style="font-size:10px; margin-bottom:4px; color:var(--tb-text-dim);">
                <strong style="color:var(--tb-text-muted);">Key Materials:</strong> ${(c.recyclable_materials || []).slice(0, 3).join(', ')}
            </div>
            <div style="font-size:10px; color:var(--tb-cyan);">
                <strong>CO₂ Offset:</strong> ${c.co2_savings_kg} kg / unit
            </div>
        `;
        grid.appendChild(card);
    });
}

// =========================================================================
// Scan History Audit Logs & Image Inspection Modal
// =========================================================================

let auditSearchQuery = '';
let auditHazardFilter = 'all';

function initAuditLogControls() {
    const searchInput = document.getElementById('history-search-input');
    const hazardFilter = document.getElementById('history-hazard-filter');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            auditSearchQuery = e.target.value.toLowerCase().trim();
            renderHistoryTable();
        });
    }

    if (hazardFilter) {
        hazardFilter.addEventListener('change', (e) => {
            auditHazardFilter = e.target.value;
            renderHistoryTable();
        });
    }
}

async function loadScanHistory() {
    try {
        const resp = await fetch(`${API_BASE}/api/history?limit=50`);
        const data = await resp.json();
        STATE.history = data.history || [];

        renderHistoryTable();
    } catch (e) {
        console.error('Failed to load scan history:', e);
    }
}

function renderHistoryTable() {
    const tbody = document.getElementById('history-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    const filtered = STATE.history.filter(item => {
        const pred = item.prediction || {};
        const matchesHazard = (auditHazardFilter === 'all') || (pred.hazard_level === auditHazardFilter);
        const textBlob = `${pred.name || ''} ${pred.category || ''} ${item.source || ''}`.toLowerCase();
        const matchesSearch = !auditSearchQuery || textBlob.includes(auditSearchQuery);
        return matchesHazard && matchesSearch;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="tb-text-center tb-text-muted" style="padding: 40px;"><i class="fa-solid fa-folder-open"></i> No telemetry events matching current filter.</td></tr>';
        return;
    }

    filtered.forEach(item => {
        const pred = item.prediction || {};
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-family:var(--tb-font-mono); font-size:10px;">${item.timestamp}</td>
            <td><span class="tb-pill" style="font-size:10px;">${item.source}</span></td>
            <td>
                ${item.thumbnail ? 
                    `<img src="${item.thumbnail}" class="tb-thumb" alt="thumb" style="cursor:pointer;" title="Click to inspect optical frame" onclick="openImageModal('${item.thumbnail}', '${escapeHtml(pred.name || 'Sample')} (${pred.confidence_percent || ''})')">` : 
                    '<span class="tb-text-dim">No Frame</span>'}
            </td>
            <td><strong>${pred.icon || '📦'} ${pred.name || 'Unknown'}</strong></td>
            <td><span class="tb-category-tag">${pred.category || 'General'}</span></td>
            <td style="font-family:var(--tb-font-mono); font-weight:700; color:var(--tb-cyan);">${pred.confidence_percent || '0%'}</td>
            <td><span class="tb-hazard-badge" style="background:${pred.hazard_color || '#22c55e'}22; color:${pred.hazard_color || '#22c55e'};">${pred.hazard_level || 'Low'}</span></td>
            <td style="font-weight:700; color:var(--tb-emerald);">${pred.co2_savings_kg || 0} kg</td>
        `;
        tbody.appendChild(tr);
    });
}

function escapeHtml(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function initImageModal() {
    const modal = document.getElementById('image-modal');
    const closeBtn = document.getElementById('btn-close-modal');

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.style.display = 'none';
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display !== 'none') modal.style.display = 'none';
        });
    }
}

window.openImageModal = function(imgSrc, caption) {
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');
    const modalCaption = document.getElementById('modal-caption');

    if (modal && modalImg) {
        modalImg.src = imgSrc;
        if (modalCaption) modalCaption.textContent = caption || 'Optical Telemetry Capture Frame';
        modal.style.display = 'flex';
    }
};

// =========================================================================
// Cloud Analytics & Chart.js Visualizations
// =========================================================================

let CHARTS = {
    categories: null,
    hazard: null,
    timeline: null,
    materials: null
};

async function loadAnalytics() {
    try {
        const resp = await fetch(`${API_BASE}/api/stats`);
        const data = await resp.json();
        STATE.stats = data;

        // Sidebar & KPI Ribbon
        const elSideScans = document.getElementById('sidebar-total-scans');
        const elSideCo2 = document.getElementById('sidebar-co2-saved');
        const elKpiScans = document.getElementById('kpi-total-scans');
        const elKpiCo2 = document.getElementById('kpi-co2-savings');

        if (elSideScans) elSideScans.textContent = `${data.total_scans} items`;
        if (elSideCo2) elSideCo2.textContent = `${data.total_co2_saved_kg} kg`;
        if (elKpiScans) elKpiScans.textContent = data.total_scans;
        if (elKpiCo2) elKpiCo2.textContent = `${data.total_co2_saved_kg} kg`;

        // Analytics Tab Top KPIs
        const elStatsCo2 = document.getElementById('stats-total-co2');
        const elStatsItems = document.getElementById('stats-total-items');
        const elStatsHaz = document.getElementById('stats-hazardous-items');
        const elStatsTop = document.getElementById('stats-top-item');

        if (elStatsCo2) elStatsCo2.textContent = `${data.total_co2_saved_kg} kg`;
        if (elStatsItems) elStatsItems.textContent = data.total_scans;
        if (elStatsHaz) elStatsHaz.textContent = (data.hazard_distribution && data.hazard_distribution.High) ? data.hazard_distribution.High : 0;
        if (elStatsTop) elStatsTop.textContent = data.top_item || 'None';

        // Update Carbon Equivalencies
        updateCarbonEquivalencies(data.total_co2_saved_kg || 0);

        // Update Interactive Charts
        updateCharts(data);

    } catch (e) {
        console.error('Failed to load analytics:', e);
    }
}

function updateCarbonEquivalencies(totalCo2) {
    const km = (totalCo2 * 4.1).toFixed(1);
    const trees = (totalCo2 / 1.8).toFixed(1);
    const kwh = (totalCo2 * 2.4).toFixed(1);
    const phones = Math.round(totalCo2 * 120);

    const elKm = document.getElementById('eq-vehicle');
    const elTrees = document.getElementById('eq-trees');
    const elEnergy = document.getElementById('eq-energy');
    const elPhones = document.getElementById('eq-phones');

    if (elKm) elKm.textContent = `${km} km`;
    if (elTrees) elTrees.textContent = `${trees} mo`;
    if (elEnergy) elEnergy.textContent = `${kwh} kWh`;
    if (elPhones) elPhones.textContent = `${phones.toLocaleString()} units`;
}

function updateCharts(stats) {
    if (typeof Chart === 'undefined') return;

    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Inter', sans-serif";

    // 1. Categories Bar Chart
    const ctxCat = document.getElementById('chart-categories');
    if (ctxCat) {
        const catCounts = stats.category_counts || {};
        const labels = Object.keys(catCounts).length > 0 ? Object.keys(catCounts) : ['Keyboard & Mouse', 'Circuit Board', 'Mobile Phone', 'Laptop', 'Battery'];
        const values = Object.keys(catCounts).length > 0 ? Object.values(catCounts) : [4, 3, 2, 2, 1];

        if (CHARTS.categories) {
            CHARTS.categories.data.labels = labels;
            CHARTS.categories.data.datasets[0].data = values;
            CHARTS.categories.update();
        } else {
            CHARTS.categories = new Chart(ctxCat, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Ingested Units',
                        data: values,
                        backgroundColor: 'rgba(0, 245, 212, 0.7)',
                        borderColor: '#00f5d4',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { grid: { color: 'rgba(255, 255, 255, 0.04)' } },
                        y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: 'rgba(255, 255, 255, 0.04)' } }
                    }
                }
            });
        }
    }

    // 2. Hazard Doughnut Chart
    const ctxHaz = document.getElementById('chart-hazard');
    if (ctxHaz) {
        const hazDist = stats.hazard_distribution || { High: 0, Moderate: 0, Low: 0 };
        const hazData = [hazDist.High || 0, hazDist.Moderate || 0, hazDist.Low || 0];

        if (CHARTS.hazard) {
            CHARTS.hazard.data.datasets[0].data = hazData;
            CHARTS.hazard.update();
        } else {
            CHARTS.hazard = new Chart(ctxHaz, {
                type: 'doughnut',
                data: {
                    labels: ['High Hazard', 'Moderate Hazard', 'Low / Safe'],
                    datasets: [{
                        data: hazData.some(v => v > 0) ? hazData : [1, 2, 5],
                        backgroundColor: [
                            'rgba(239, 68, 68, 0.85)',
                            'rgba(245, 158, 11, 0.85)',
                            'rgba(16, 185, 129, 0.85)'
                        ],
                        borderColor: '#111827',
                        borderWidth: 3,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 12, padding: 14 } }
                    }
                }
            });
        }
    }

    // 3. Timeline Line Chart
    const ctxTime = document.getElementById('chart-timeline');
    if (ctxTime) {
        const historyReversed = [...(STATE.history || [])].reverse();
        let runningCo2 = 0;
        const timeLabels = historyReversed.map((item, idx) => item.timestamp ? item.timestamp.slice(11, 19) : `Scan #${idx + 1}`);
        const co2Points = historyReversed.map(item => {
            runningCo2 += (item.prediction ? item.prediction.co2_savings_kg : 0);
            return parseFloat(runningCo2.toFixed(2));
        });

        if (timeLabels.length === 0) {
            timeLabels.push('00:00:00');
            co2Points.push(0);
        }

        if (CHARTS.timeline) {
            CHARTS.timeline.data.labels = timeLabels;
            CHARTS.timeline.data.datasets[0].data = co2Points;
            CHARTS.timeline.update();
        } else {
            CHARTS.timeline = new Chart(ctxTime, {
                type: 'line',
                data: {
                    labels: timeLabels,
                    datasets: [{
                        label: 'Cumulative CO₂ Saved (kg)',
                        data: co2Points,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.15)',
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#10b981',
                        pointBorderColor: '#fff',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { color: 'rgba(255, 255, 255, 0.04)' } },
                        y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.04)' } }
                    }
                }
            });
        }
    }

    // 4. Materials Yield Composition
    const ctxMat = document.getElementById('chart-materials');
    if (ctxMat) {
        const matLabels = ['Copper (99.9%)', 'Precious Metals (Au/Ag/Pd)', 'Thermoplastics (ABS/PC)', 'Aluminum / Casings', 'Lithium / Cobalt Cells'];
        const matWeights = [35, 15, 25, 15, 10];

        if (!CHARTS.materials) {
            CHARTS.materials = new Chart(ctxMat, {
                type: 'polarArea',
                data: {
                    labels: matLabels,
                    datasets: [{
                        data: matWeights,
                        backgroundColor: [
                            'rgba(0, 187, 249, 0.7)',
                            'rgba(245, 158, 11, 0.7)',
                            'rgba(139, 92, 246, 0.7)',
                            'rgba(148, 163, 184, 0.7)',
                            'rgba(239, 68, 68, 0.7)'
                        ],
                        borderColor: '#111827',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }
                    },
                    scales: {
                        r: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { display: false } }
                    }
                }
            });
        }
    }
}

// =========================================================================
// Interactive Batch E-Waste Simulator
// =========================================================================

function initBatchSimulator() {
    const selectCat = document.getElementById('sim-category-select');
    const inputQty = document.getElementById('sim-quantity-input');
    const sliderQty = document.getElementById('sim-quantity-slider');

    if (selectCat && STATE.classesDb.length > 0 && selectCat.children.length === 0) {
        STATE.classesDb.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = `${c.icon || '📦'} ${c.name} (${c.co2_savings_kg} kg CO₂ / unit)`;
            selectCat.appendChild(opt);
        });
    }

    const runSim = () => {
        const catId = parseInt(selectCat ? selectCat.value : 0) || 0;
        const qty = parseInt(inputQty ? inputQty.value : 25) || 1;
        const classObj = STATE.classesDb.find(c => c.id === catId) || STATE.classesDb[0];

        if (classObj) {
            const totalCo2 = (classObj.co2_savings_kg * qty).toFixed(1);
            const metals = (classObj.recyclable_materials || []).slice(0, 3).join(', ');
            const route = classObj.reuse_potential ? classObj.reuse_potential.split(';')[0] : 'Standard Certified E-Waste Facility';

            const resCo2 = document.getElementById('sim-res-co2');
            const resMetals = document.getElementById('sim-res-metals');
            const resRoute = document.getElementById('sim-res-route');

            if (resCo2) resCo2.textContent = `${totalCo2} kg`;
            if (resMetals) resMetals.textContent = metals;
            if (resRoute) resRoute.textContent = route;
        }
    };

    if (selectCat) selectCat.addEventListener('change', runSim);
    if (inputQty) {
        inputQty.addEventListener('input', (e) => {
            if (sliderQty) sliderQty.value = e.target.value;
            runSim();
        });
    }
    if (sliderQty) {
        sliderQty.addEventListener('input', (e) => {
            if (inputQty) inputQty.value = e.target.value;
            runSim();
        });
    }

    runSim();
}

// =========================================================================
// History Clearing & Multi-Format Reporting Suite
// =========================================================================

async function clearHistory() {
    if (!confirm('Clear all telemetry audit logs?')) return;
    try {
        await fetch(`${API_BASE}/api/history/clear`, { method: 'POST' });
        loadScanHistory();
        loadAnalytics();
    } catch (e) {
        alert('Failed to clear logs: ' + e.message);
    }
}

function exportHistoryCSV() {
    if (STATE.history.length === 0) {
        alert('No audit logs to export.');
        return;
    }

    const headers = ['ID', 'Timestamp', 'Source', 'Item Name', 'Category', 'Confidence', 'Hazard Level', 'CO2 Offset (kg)', 'Recyclable Materials'];
    const rows = STATE.history.map(item => [
        item.id,
        item.timestamp,
        item.source,
        `"${item.prediction.name}"`,
        `"${item.prediction.category}"`,
        item.prediction.confidence_percent,
        item.prediction.hazard_level,
        item.prediction.co2_savings_kg,
        `"${(item.prediction.recyclable_materials || []).join('; ')}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `iot_ewaste_telemetry_log_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function exportHistoryJSON() {
    if (STATE.history.length === 0) {
        alert('No audit logs to export.');
        return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(STATE.history, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `iot_ewaste_telemetry_export_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
}

function printSustainabilityReport() {
    window.print();
}
