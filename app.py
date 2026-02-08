import torch
import gradio as gr
import numpy as np
import os
import re
import time
import gc
import soundfile as sf
import threading
from qwen_tts import Qwen3TTSModel

# ⚡ Performance & Stability
torch.set_num_threads(16)
torch.set_float32_matmul_precision('high')

DEVICE = "cuda:0"
DTYPE = torch.bfloat16

# Ensure outputs directory exists
OUTPUT_DIR = "outputs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"Initializing Qwen3-TTS Emotional-Lock Engine (16 CPU Threads)...")

# Helper to load models
def load_model(ckpt):
    print(f"Loading {ckpt}...")
    attn_impl = "sdpa" if torch.cuda.is_available() else None
    model_wrapper = Qwen3TTSModel.from_pretrained(
        ckpt,
        device_map=DEVICE,
        dtype=DTYPE,
        attn_implementation=attn_impl,
    )
    return model_wrapper

# Load models
design_model = load_model("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
base_model = load_model("Qwen/Qwen3-TTS-12Hz-1.7B-Base")

print("All models loaded successfully.")

LANGUAGES = ["Auto", "Chinese", "English", "Japanese", "Korean", "German", "French", "Russian", "Portuguese", "Spanish", "Italian"]

def parse_universal_text(text):
    """
    Splits text into segments based on [] tags.
    Every tag triggers a new segment for instant emotional shifts.
    """
    segments = []
    active_directives = {}
    tag_pattern = r"(\[[^\]]+\])"
    parts = re.split(tag_pattern, text)
    current_text_buffer = ""
    
    for part in parts:
        if not part: continue
        
        if part.startswith("[") and part.endswith("]"):
            if current_text_buffer.strip():
                segments.append({
                    'text': current_text_buffer.strip(),
                    'directives': active_directives.copy(),
                    'pause_after': False
                })
                current_text_buffer = ""
            
            tag_content = part.strip("[]").strip()
            tag_lower = tag_content.lower()
            
            if tag_lower == "pause":
                if segments:
                    segments[-1]['pause_after'] = True
                continue
                
            if ":" in tag_content:
                key, val = tag_content.split(":", 1)
                active_directives[key.strip().lower()] = val.strip()
            else:
                active_directives["mood"] = tag_content
        else:
            current_text_buffer += part
            
    if current_text_buffer.strip():
        segments.append({
            'text': current_text_buffer.strip(),
            'directives': active_directives.copy(),
            'pause_after': False
        })
        
    return segments

def build_locked_instruct(base_identity, segment_directives):
    """
    Strict Template: Identity first, then segment-specific emotion.
    This locks the voice character while allowing emotional shifts.
    """
    emotion = segment_directives.get('mood', 'Neutral')
    # Filter out identity-related keys from directives to keep them in base_identity only
    other_details = [f"{k.capitalize()}: {v}" for k,v in segment_directives.items() if k != 'mood']
    
    instruct = f"Voice Identity: {base_identity}. Delivery Emotion: {emotion}."
    if other_details:
        instruct += " Additional Tones: " + ", ".join(other_details)
    return instruct

def generate_emotional_locked(text, language, base_identity, mode="design", ref_audio=None, progress=gr.Progress(track_tqdm=True)):
    """
    Generates audio with Emotional Identity Lock.
    Voice character remains consistent while emotions shift per tag.
    """
    if not text.strip():
        return None, None, "Error: Text is empty"
    
    torch.cuda.empty_cache()
    gc.collect()
    
    try:
        segments = parse_universal_text(text)
        if not segments:
            return None, None, "Error: No text content found"
            
        master_audio = []
        sr = 24000
        voice_prompt = None
        total_segments = len(segments)
        
        if mode == "clone":
            if ref_audio is None:
                return None, None, "Error: Need reference audio"
            voice_prompt = base_model.create_voice_clone_prompt(ref_audio=ref_audio, x_vector_only_mode=False)

        with torch.inference_mode():
            for i, seg in enumerate(segments):
                # 🔒 Emotional Identity Lock Prompt
                instruct = build_locked_instruct(base_identity, seg['directives'])
                
                # Update Progress
                progress((i / total_segments), desc=f"🎬 Rendering Segment {i+1}/{total_segments} | Emotion: {seg['directives'].get('mood', 'Neutral')}")
                
                if mode == "design":
                    wavs, current_sr = design_model.generate_voice_design(
                        text=seg['text'],
                        language=language,
                        instruct=instruct,
                    )
                else:
                    wavs, current_sr = base_model.generate_voice_clone(
                        text=seg['text'],
                        language=language,
                        instruct=instruct,
                        voice_clone_prompt=voice_prompt,
                    )
                
                sr = current_sr
                segment_wav = wavs[0]
                master_audio.append(segment_wav)
                
                # Yield Live Preview
                yield (sr, segment_wav), None, f"Listening to Segment {i+1}/{total_segments}..."
                
                if seg['pause_after']:
                    silence = np.zeros(int(sr * 0.8), dtype=np.float32)
                    master_audio.append(silence)
            
            # 🏁 Final Master Compilation
            progress(0.95, desc="Compiling Master Audio...")
            final_wav = np.concatenate(master_audio)
            
            # Save to outputs
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"qween_{mode}_{timestamp}.wav"
            filepath = os.path.join(OUTPUT_DIR, filename)
            sf.write(filepath, final_wav, sr)
            
            progress(1.0, desc="Complete!")
            yield (sr, master_audio[-1]), (sr, final_wav), f"✅ Saved to: {filepath}"
            
    except Exception as e:
        yield None, None, f"Error: {str(e)}"
    finally:
        torch.cuda.empty_cache()

# Gradio Wrappers
def design_wrapper(text, language, identity):
    yield from generate_emotional_locked(text, language, identity, mode="design")

def clone_wrapper(text, language, identity, ref_audio):
    yield from generate_emotional_locked(text, language, identity, mode="clone", ref_audio=ref_audio)

# UI
with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple", secondary_hue="indigo")) as app:
    gr.Markdown("# 🎭 Qwen3-TTS Pro: Emotional Identity Lock")
    gr.Markdown("The **Voice Identity** defines the character (accent, pitch, gender). Tags `[]` shift the **Emotion** without changing the person speaking.")
    
    with gr.Tabs():
        with gr.TabItem("🎨 AI Voice Design"):
            with gr.Row():
                with gr.Column(scale=2):
                    design_text = gr.Textbox(
                        label="Script with Emotional Tags", lines=8, 
                        value="[Whispering] I'm so glad you're here. [Pause] [Excited] Tonight is going to be amazing!",
                    )
                    design_lang = gr.Dropdown(label="Language", choices=LANGUAGES, value="Auto")
                    design_identity = gr.Textbox(
                        label="Voice Identity (The Character)", lines=2, 
                        value="A soft-spoken British woman with a gentle tone.",
                        placeholder="Define the consistent voice character here..."
                    )
                    design_btn = gr.Button("🎬 Render with Identity Lock", variant="primary")
                with gr.Column(scale=3):
                    gr.Markdown("### 🔊 Live Stream")
                    design_live = gr.Audio(label="Current Emotion", type="numpy", interactive=False)
                    gr.Markdown("### 🏆 Final Compiled Master")
                    design_master = gr.Audio(label="Locked-Voice Production", type="numpy", interactive=False)
                    design_status = gr.Textbox(label="Studio Status", interactive=False)

        with gr.TabItem("👤 Pro Voice Cloning"):
            with gr.Row():
                with gr.Column(scale=2):
                    clone_text = gr.Textbox(
                        label="Script with Emotional Tags", lines=8, 
                        value="[Serious] We have a problem. [Pause] [Relieved] But wait, I think I found a solution.",
                    )
                    clone_lang = gr.Dropdown(label="Language", choices=LANGUAGES, value="Auto")
                    clone_identity = gr.Textbox(label="Style Instructions", lines=2, value="Clear and expressive.")
                    clone_ref = gr.Audio(label="Reference Audio (Voice Identity)", type="filepath")
                    clone_btn = gr.Button("🎧 Clone with Emotional Shifts", variant="primary")
                with gr.Column(scale=3):
                    clone_live = gr.Audio(label="Current Segment", type="numpy", interactive=False)
                    clone_master = gr.Audio(label="Final Master", type="numpy", interactive=False)
                    clone_status = gr.Textbox(label="Studio Status", interactive=False)

    design_btn.click(design_wrapper, [design_text, design_lang, design_identity], [design_live, design_master, design_status])
    clone_btn.click(clone_wrapper, [clone_text, clone_lang, clone_identity, clone_ref], [clone_live, clone_master, clone_status])

if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=8000)
