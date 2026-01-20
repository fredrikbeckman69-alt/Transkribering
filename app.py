import gradio as gr
import requests
import os
import imageio_ffmpeg
# Add ffmpeg to path
os.environ["PATH"] += os.pathsep + os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())

import torch
from transformers import pipeline
from pyannote.audio import Pipeline
import numpy as np

# check system endpoint
# ...

# Initialize Whisper model
print("Loading Whisper model...", flush=True)
MODEL_NAME = "KBLab/kb-whisper-small"
# Force CPU for stability on free tier
device = "cpu" 
pipe = pipeline("automatic-speech-recognition", model=MODEL_NAME, device=device)
print(f"Whisper loaded on {device}", flush=True)

# Initialize Diarization Pipeline
print("Loading Diarization pipeline...", flush=True)
auth_token = os.environ.get("HF_TOKEN")
try:
    diarization_pipe = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=auth_token
    )
    if diarization_pipe:
        # Move to device (CPU)
        diarization_pipe.to(torch.device(device))
        print("Diarization loaded successfully.", flush=True)
    else:
        print("Diarization likely failed to load (None returned). Check HF_TOKEN capabilities.", flush=True)
except Exception as e:
    print(f"Failed to load Diarization: {e}. Check if you accepted terms for 'pyannote/speaker-diarization-3.1' on HF.", flush=True)
    diarization_pipe = None

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def merge_transcription(whisper_chunks, diarization):
    # Merge Whisper chunks with Diarization speakers
    segments = []
    unique_speakers = set()
    
    # Iterate over whisper chunks
    for chunk in whisper_chunks:
        text = chunk.get("text", "").strip()
        start = chunk.get("timestamp", [0, 0])[0]
        end = chunk.get("timestamp", [0, 0])[1]
        
        if end is None: end = start + 2.0 # Fallback
        
        # Find dominant speaker in this timeframe
        speaking_durations = {}
        
        # If diarization failed or is None, skip overlap check
        if diarization:
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                # Check overlap
                seg_start = turn.start
                seg_end = turn.end
                
                overlap_start = max(start, seg_start)
                overlap_end = min(end, seg_end)
                
                if overlap_end > overlap_start:
                    dur = overlap_end - overlap_start
                    speaking_durations[speaker] = speaking_durations.get(speaker, 0) + dur
        
        # Find max
        if speaking_durations:
            best_speaker = max(speaking_durations, key=speaking_durations.get)
        else:
            best_speaker = "Unknown"
        
        unique_speakers.add(best_speaker)
        segments.append({
            "start": start,
            "end": end,
            "speaker": best_speaker,
            "text": text,
            "formatted_time": format_time(start)
        })
    
    return {
        "segments": segments,
        "unique_speakers": sorted(list(unique_speakers))
    }

def transcribe_audio(audio_file):
    """
    Transcribe audio using local KBLab Whisper model + Pyannote Diarization
    Returns JSON object for frontend processing.
    """
    if audio_file is None:
        return {"error": "Ingen fil uppladdad"}
    
    try:
        # 1. Transcribe (Whisper)
        print(f"Starting Whisper transcription for {audio_file}...", flush=True)
        whisper_result = pipe(audio_file, chunk_length_s=30, return_timestamps=True)
        text_raw = whisper_result.get("text", "")
        chunks = whisper_result.get("chunks", [])
        
        if not text_raw:
             return {"error": "Ingen text kunde identifieras"}

        # 2. Diarize (Pyannote)
        diarization = None
        if diarization_pipe:
            print("Starting Speaker Diarization...", flush=True)
            try:
                diarization = diarization_pipe(audio_file)
            except Exception as e_dia:
                print(f"Diarization failed: {e_dia}", flush=True)
                # Continue without diarization
        
        # 3. Merge & Return JSON
        result_json = merge_transcription(chunks, diarization)
        return result_json
            
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return {"error": str(e)}

# Custom CSS with Apple Siri gradient and glassmorphism
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --siri-gradient: linear-gradient(90deg, #D6249F 0%, #FD5949 33%, #285AEB 66%, #0071E3 100%);
    --siri-glow: radial-gradient(circle at 50% 50%, rgba(40, 90, 235, 0.15), transparent 70%);
    --glass-bg: rgba(255, 255, 255, 0.7);
    --glass-border: rgba(0, 0, 0, 0.1);
    --primary-color: #0071E3;
    --success-color: #34C759;
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

.gradio-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
    font-family: 'Inter', sans-serif !important;
}

.gradio-container::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: var(--siri-glow);
    pointer-events: none;
    z-index: 0;
    opacity: 0.6;
}

h1, .gr-markdown h1 {
    background: var(--siri-gradient) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    font-size: 3rem !important;
    margin-bottom: 0.5rem !important;
}

.gr-box {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08) !important;
}

.gr-button-primary {
    background: var(--primary-color) !important;
    border: none !important;
    border-radius: 980px !important;
    font-weight: 600 !important;
    padding: 16px 24px !important;
    box-shadow: 0 4px 12px rgba(0, 113, 227, 0.2) !important;
    transition: all 0.2s ease !important;
}

.gr-button-primary:hover {
    background: #0077ED !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0, 113, 227, 0.3) !important;
}

.gr-input, .gr-textbox {
    border-radius: 12px !important;
    border: 1.5px solid var(--glass-border) !important;
    transition: all 0.2s ease !important;
}

.gr-input:focus, .gr-textbox:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1) !important;
}

.gr-file-upload {
    border: 2px dashed var(--glass-border) !important;
    border-radius: 20px !important;
    background: rgba(255, 255, 255, 0.9) !important;
    transition: all 0.3s ease !important;
}

.gr-file-upload:hover {
    border-color: var(--primary-color) !important;
    background: rgba(0, 113, 227, 0.03) !important;
    transform: translateY(-2px) !important;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.96) translateY(10px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

.gradio-container > div {
    animation: fadeIn 0.6s ease-out !important;
}
"""

# Create Gradio interface with premium design
with gr.Blocks(title="Svensk Transkribering", theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown(
        """
        # 🎙️ Svensk Transkribering
        
        AI-driven tal-till-text med **KBLab Whisper** - optimerad för svenska!
        
        ### Hur man använder:
        1. Ladda upp en ljudfil
        2. Klicka "Transkribera"
        3. Vänta på resultatet (första gången kan ta 20-30 sekunder)
        """
    )
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                label="🎵 Ljudfil",
                type="filepath",
                sources=["upload"]
            )
            transcribe_btn = gr.Button("🚀 Transkribera", variant="primary", size="lg")
        
        with gr.Column():
            # Changed to JSON output for frontend compatibility
            output_json = gr.JSON(
                label="📝 Resultat Data"
            )
    
    gr.Markdown(
        """
        ---
        **Tips:** 
        - Första gången kan ta 20-30 sekunder (modellen startas)
        - Bäst resultat med tydligt tal på svenska
        - Stöder mp3, wav, m4a och andra ljudformat
        """
    )
    
    # Connect button to function (no token input needed)
    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[audio_input],
        outputs=output_json,
        api_name="/transcribe_v2"
    )

    with gr.Tab("System Check (Debug)"):
        sys_btn = gr.Button("Check FFmpeg")
        sys_out = gr.Textbox(label="System Info")
        
        def check_system():
            import subprocess
            try:
                # Check ffmpeg
                cmd = "ffmpeg -version"
                output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT).decode()
                return f"✅ FFmpeg found:\n{output[:200]}..."
            except Exception as e:
                return f"❌ FFmpeg error: {str(e)}\n\nPATH: {os.environ.get('PATH')}"
        
        sys_btn.click(check_system, outputs=sys_out, api_name="/sys_info")

# Launch the app
if __name__ == "__main__":
    demo.launch()
