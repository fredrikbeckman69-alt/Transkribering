import gradio as gr
import requests
import os

import torch
from transformers import pipeline

# Initialize model (lazy loading or global loading)
# For Spaces, global loading at startup is usually better to avoid delay on first request
# But requires more startup time.
print("Loading model...", flush=True)
MODEL_NAME = "KBLab/kb-whisper-large"
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = pipeline("automatic-speech-recognition", model=MODEL_NAME, device=device)
print(f"Model loaded on {device}", flush=True)

def transcribe_audio(audio_file):
    """
    Transcribe audio using local KBLab Whisper model
    """
    if audio_file is None:
        return "❌ Vänligen ladda upp en ljudfil först."
    
    try:
        # Pipeline handles file reading and preprocessing
        # Enable chunking for long audio files (>30s)
        result = pipe(audio_file, chunk_length_s=30, return_timestamps=True)
        
        if "text" in result:
            return f"✅ Transkribering:\n\n{result['text']}"
        else:
            return f"⚠️ Oväntat svar: {result}"
            
    except Exception as e:
        return f"❌ Ett fel uppstod: {str(e)}"

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
            output_text = gr.Textbox(
                label="📝 Resultat",
                lines=15,
                placeholder="Transkriberingen visas här..."
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
        outputs=output_text
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
