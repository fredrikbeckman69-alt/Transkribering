// Premium Siri-like Transcription App
import { Client } from "https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js";

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

// Helper: Format speakers into dynamic HTML blocks
function renderTranscript() {
    transcriptionBox.innerHTML = '';

    transcriptData.segments.forEach((seg, index) => {
        const block = document.createElement('div');
        block.className = 'transcript-block';
        block.dataset.speaker = seg.speaker;

        const header = document.createElement('div');
        header.className = 'transcript-header';

        const speakerLabel = document.createElement('span');
        speakerLabel.className = 'speaker-label';
        // Check if there is a custom name stored for this speaker key, or use default
        const customName = document.getElementById(`input-${seg.speaker}`)?.value || seg.speaker;
        speakerLabel.textContent = customName;
        speakerLabel.id = `label-${seg.speaker}-${index}`; // Unique ID helper

        const timeLabel = document.createElement('span');
        timeLabel.className = 'timestamp';
        // seg.formatted_time should come from backend
        timeLabel.textContent = seg.formatted_time || "";

        header.appendChild(speakerLabel);
        header.appendChild(timeLabel);

        const textP = document.createElement('div');
        textP.className = 'transcript-text';
        textP.textContent = seg.text;

        block.appendChild(header);
        block.appendChild(textP);
        transcriptionBox.appendChild(block);
    });
}

function renderSpeakerControls() {
    speakerControls.innerHTML = '';

    transcriptData.unique_speakers.forEach(speaker => {
        const group = document.createElement('div');
        group.className = 'speaker-input-group';

        const label = document.createElement('label');
        label.textContent = speaker + ":";

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'speaker-name-input';
        input.value = speaker; // Default value is the ID key
        input.id = `input-${speaker}`;
        input.placeholder = "Ange namn";

        // Live update listener
        input.addEventListener('input', (e) => {
            const newName = e.target.value;
            // Update all labels in the transcript with this speaker code
            const blocks = document.querySelectorAll(`[data-speaker="${speaker}"] .speaker-label`);
            blocks.forEach(lbl => lbl.textContent = newName);
        });

        group.appendChild(label);
        group.appendChild(input);
        speakerControls.appendChild(group);
    });
}

function showResult(data) {
    if (data.error) {
        showStatus(`Fel: ${data.error}`, 'error');
        return;
    }

    // Store data globally
    // Data expected: { "segments": [...], "unique_speakers": [...] }
    transcriptData = data;

    // Render UI
    renderSpeakerControls();
    renderTranscript();

    outputContainer.classList.add('visible');
    outputContainer.style.display = 'block';

    // Smooth scroll to result
    outputContainer.scrollIntoView({ behavior: 'smooth' });
}

async function startTranscription() {
    if (!currentFile) {
        showStatus('Vänligen välj en ljudfil', 'error');
        return;
    }

    // Update UI state
    setLoading(true);
    outputContainer.classList.remove('visible');
    speakerControls.innerHTML = ''; // Clear prev
    transcriptionBox.innerHTML = ''; // Clear prev
    showStatus('Ansluter till Hugging Face...');

    try {
        // Connect to the Hugging Face Space
        const client = await Client.connect("zpo685d/svensk-transkribering");

        showStatus('Transkriberar... (Detta kan ta några minuter för långa filer)');

        // Run prediction
        // The API returns an object with 'data' array. Logic depends on app.py return type.
        // Gradio Interface usually returns data[0] as the output.
        // Endpoint found via client.view_api() is //transcribe_v2 (double slash required due to backend config)
        const result = await client.predict("//transcribe_v2", [
            currentFile,
        ]);

        const responseData = result.data[0];
        // Check if response is JSON (obj) or error string
        if (typeof responseData === 'string') {
            // Fallback if backend returned string error
            if (responseData.includes("❌")) throw new Error(responseData);
            // Should not happen with new JSON backend, but handle legacy:
            console.warn("Received string response, anticipated JSON.");
        }

        showResult(responseData);
        showStatus('Transkribering klar!');

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
