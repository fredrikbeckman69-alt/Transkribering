// Vi använder vår lokala python-server som proxy för att undvika CORS-problem
const API_URL = "/api/transcribe";
// const PROXY_URL = "https://corsproxy.io/?";
// const TARGET_URL = "https://router.huggingface.co/hf-inference/models/KBLab/whisper-large-v3-swedish";

// DOM Elements
const tokenInput = document.getElementById('api-token');
const settingsBtn = document.getElementById('settings-btn');
const settingsPanel = document.getElementById('settings-panel');
const connectionStatus = document.getElementById('connection-status');
const fileInput = document.getElementById('audio-file');
const fileDropArea = document.getElementById('drop-area');
const selectedFileMsg = document.getElementById('selected-file-msg');
const fileMsg = document.getElementById('file-msg');
const transcribeBtn = document.getElementById('transcribe-btn');
const outputContainer = document.getElementById('output-container');
const transcriptionText = document.getElementById('transcription-text');
const statusMsg = document.getElementById('status-msg');

let currentFile = null;

// Initialize
function init() {
    // Check for file protocol
    if (window.location.protocol === 'file:') {
        showStatus('⚠️ Varning: Du kör appen lokalt direkt från fil (file://). Transkribering kommer troligen blockeras av webbläsaren. Använd start_app.bat för att testa lokalt, eller ladda upp filerna till en webbserver.', 'error');
    }

    // Load token from local storage if valid
    const savedToken = localStorage.getItem('hf_token');
    if (savedToken) {
        tokenInput.value = savedToken;
        updateConnectionStatus(true);
    } else {
        updateConnectionStatus(false);
        // We leave the panel hidden by default so it looks cleaner
        // Users can open settings if they fail without token
    }

    setupEventListeners();
}

function updateConnectionStatus(isConnected) {
    if (isConnected) {
        connectionStatus.innerHTML = '<span class="status-dot"></span> Kopplad till KB Whisper';
        connectionStatus.classList.add('connected');
    } else {
        connectionStatus.innerHTML = '<span class="status-dot"></span> Ej ansluten (Körs anonymt)';
        connectionStatus.classList.remove('connected');
    }
}

function setupEventListeners() {
    // Settings toggle
    settingsBtn.addEventListener('click', () => {
        settingsPanel.classList.toggle('hidden');
    });

    // Token input updates status
    tokenInput.addEventListener('input', () => {
        const hasToken = tokenInput.value.trim().length > 0;
        updateConnectionStatus(hasToken);
        // Button is always enabled now if file exists
        transcribeBtn.disabled = !currentFile;

        if (hasToken) {
            localStorage.setItem('hf_token', tokenInput.value.trim());
        } else {
            localStorage.removeItem('hf_token');
        }
    });

    // Drag and drop effects
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, unhighlight, false);
    });

    // Handle file drop
    fileDropArea.addEventListener('drop', handleDrop, false);

    // Handle file input change
    fileInput.addEventListener('change', handleFiles, false);

    // Transcribe button
    transcribeBtn.addEventListener('click', startTranscription);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    fileDropArea.classList.add('drag-over');
}

function unhighlight() {
    fileDropArea.classList.remove('drag-over');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFileSelect(files);
}

function handleFiles() {
    handleFileSelect(this.files);
}

function handleFileSelect(files) {
    if (files.length > 0) {
        currentFile = files[0];
        updateFileUI(currentFile.name);
    }
}

function updateFileUI(filename) {
    selectedFileMsg.textContent = `Selected: ${filename}`;
    selectedFileMsg.style.display = 'block';
    fileMsg.style.display = 'none';
    transcribeBtn.disabled = !currentFile;
}

tokenInput.addEventListener('input', () => {
    const hasToken = tokenInput.value.trim().length > 0;
    updateConnectionStatus(hasToken);

    // Button depends only on file, not token
    transcribeBtn.disabled = !currentFile;

    if (hasToken) {
        localStorage.setItem('hf_token', tokenInput.value.trim());
    } else {
        localStorage.removeItem('hf_token');
    }
});

async function startTranscription() {
    const token = tokenInput.value.trim();

    // Token is optional for some models/tiers, but recommended
    // if (!token) {
    //    showStatus('Please enter a valid API Token', 'error');
    //    return;
    // }

    if (!currentFile) {
        showStatus('Please select a file', 'error');
        return;
    }

    // Save token if provided
    if (token) {
        localStorage.setItem('hf_token', token);
    }

    // Update UI state
    setLoading(true);
    outputContainer.classList.remove('visible');
    transcriptionText.textContent = '';
    showStatus(token ? 'Transkriberar...' : 'Transkriberar (utan token)...');

    try {
        const result = await query(currentFile, token);

        if (result.error) {
            throw new Error(result.error);
        }

        const text = result.text;
        showResult(text);

    } catch (error) {
        console.error('Transcription error:', error);
        let msg = `Fel: ${error.message || 'Misslyckades'}`;
        if (!token && error.message.includes('401')) {
            msg += ' (Prova att lägga in en API Token i inställningarna)';
        }
        showStatus(msg, 'error');
    } finally {
        setLoading(false);
    }
}

async function query(file, token) {
    const headers = {
        "Content-Type": "application/octet-stream",
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(API_URL, {
        headers: headers,
        method: "POST",
        body: file,
    });

    const result = await response.json();
    return result;
}

function setLoading(isLoading) {
    if (isLoading) {
        transcribeBtn.disabled = true;
        transcribeBtn.innerHTML = '<span class="loading"></span> Transcribing...';
    } else {
        transcribeBtn.disabled = false;
        transcribeBtn.textContent = 'Start Transcription';
    }
}

function showResult(text) {
    transcriptionText.textContent = text;
    outputContainer.classList.add('visible');

    // Auto scroll to results
    outputContainer.scrollIntoView({ behavior: 'smooth' });
}

function showStatus(message, type = 'info') {
    statusMsg.textContent = message;
    statusMsg.className = 'status-msg ' + (type === 'error' ? 'status-error' : '');
}

// Kickoff
init();
