// Premium Siri-like Transcription App
import { Client } from "https://cdn.jsdelivr.net/npm/@gradio/client@0.1.4/dist/index.min.js";

// DOM Elements
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
    setupEventListeners();
}

function setupEventListeners() {
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

    // Handle click on drop area to trigger file input
    fileDropArea.addEventListener('click', () => fileInput.click());

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
    selectedFileMsg.textContent = `Vald fil: ${filename}`;
    selectedFileMsg.style.display = 'block';
    fileMsg.style.display = 'none';
    transcribeBtn.disabled = false;
}

async function startTranscription() {
    if (!currentFile) {
        showStatus('Vänligen välj en ljudfil', 'error');
        return;
    }

    // Update UI state
    setLoading(true);
    outputContainer.classList.remove('visible');
    transcriptionText.textContent = '';
    showStatus('Ansluter till Hugging Face...');

    try {
        // Connect to the Hugging Face Space
        const client = await Client.connect("zpo685d/svensk-transkribering");

        showStatus('Transkriberar... (Detta kan ta några minuter för långa filer)');

        // Run prediction
        // The API returns an object with 'data' array. Logic depends on app.py return type.
        // Gradio Interface usually returns data[0] as the output.
        // Endpoint found via client.view_api() is /transcribe_v2
        const result = await client.predict("/transcribe_v2", [
            currentFile,
        ]);

        // Result format from Gradio client
        const transcription = result.data[0];

        if (transcription) {
            // Remove the "✅ Transkribering:" prefix if it exists in the output to keep it clean
            const cleanText = transcription.replace('✅ Transkribering:\n\n', '');
            showResult(cleanText);
            showStatus('Transkribering klar!');
        } else {
            throw new Error("Ingen text returnerades");
        }

    } catch (error) {
        console.error('Transcription error:', error);
        showStatus(`Fel: ${error.message}`, 'error');
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    if (isLoading) {
        transcribeBtn.disabled = true;
        transcribeBtn.innerHTML = '<span class="loading"></span> Bearbetar...';
    } else {
        transcribeBtn.disabled = !currentFile;
        transcribeBtn.textContent = 'Transkribera igen';
    }
}

function showResult(text) {
    transcriptionText.textContent = text;
    outputContainer.classList.add('visible');
    outputContainer.scrollIntoView({ behavior: 'smooth' });
}

function showStatus(message, type = 'info') {
    statusMsg.textContent = message;
    statusMsg.className = 'status-msg ' + (type === 'error' ? 'status-error' : '');
}

// Kickoff
init();
