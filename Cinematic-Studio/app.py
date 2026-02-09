import torch
import gradio as gr
import numpy as np
import os
import re
import time
import gc
import soundfile as sf
import json
from qwen_tts import Qwen3TTSModel

torch.set_num_threads(16)
torch.set_float32_matmul_precision("high")

DEVICE = "cuda:0"
DTYPE = torch.bfloat16

OUTPUT_DIR = "outputs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("Initializing Qwen3-TTS Cinematic Pro-Studio...")

def load_model(ckpt):
    print(f"Loading {ckpt}...")
    attn_impl = "sdpa" if torch.cuda.is_available() else None
    return Qwen3TTSModel.from_pretrained(ckpt, device_map=DEVICE, dtype=DTYPE, attn_implementation=attn_impl)

design_model = load_model("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
base_model = load_model("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
print("All models loaded successfully.")

LANGUAGES = ["Auto", "Chinese", "English", "Japanese", "Korean", "German", "French", "Russian", "Portuguese", "Spanish", "Italian"]

# 
#  ENHANCED CINEMATIC PARSER
# 

def parse_advanced_script(script_text, character_dict):
    """
    Robust cinematic parser for multi-character scripts.
    Handles:
    - [Name - Description, Emotion] (Solo) Dialogue
    - Name: Dialogue
    - Solo: Name's internal thoughts
    - Em-dash () for interruptions
    """
    segments = []
    lines = script_text.strip().split("\n")
    
    # Patterns
    bracket_tag_pattern = re.compile(r"^\[\s*([^\]]+)\s*\]") # Matches [ Name - Voice, Emotion ]
    old_school_pattern = re.compile(r"^([A-Za-z_]+):\s*(.+)$") # Matches Name: Dialogue
    solo_narrative_pattern = re.compile(r"^Solo:\s*([A-Za-z_]+).s\s+(.+)$", re.IGNORECASE)
    solo_inline_pattern = re.compile(r"\(Solo[^)]*\)", re.IGNORECASE)
    tag_cleaner = re.compile(r"\[([^\]]+)\]")
    
    current_line_speaker = None

    for line in lines:
        line = line.strip()
        if not line: continue
        
        speaker_name = None
        dialogue = ""
        emotion = "Neutral"
        voice_style = ""
        is_solo = False
        
        # 1. Try Bracket Tag Format: [Elena - Sexy, Cold] (Solo) "Hello..."
        bracket_match = bracket_tag_pattern.match(line)
        if bracket_match:
            full_tag = bracket_match.group(1)
            dialogue = line[bracket_match.end():].strip()
            
            # Parse the tag: "Name - Voice, Emotion"
            if " - " in full_tag:
                name_part, attr_part = full_tag.split(" - ", 1)
                speaker_name = name_part.strip()
                attrs = [a.strip() for a in attr_part.split(",")]
                if len(attrs) >= 2:
                    voice_style = ", ".join(attrs[:-1])
                    emotion = attrs[-1]
                else:
                    emotion = attrs[0]
            else:
                speaker_name = full_tag.strip()
        
        # 2. Try Solo Narrative Format: Solo: Sarah's Internal Monologue
        elif solo_narrative_pattern.match(line):
            solo_match = solo_narrative_pattern.match(line)
            speaker_name = solo_match.group(1)
            dialogue = f"({solo_match.group(2)})"
            emotion = "Introspective"
            is_solo = True
            
        # 3. Try Old-School Format: Sarah: "Hello..."
        elif old_school_pattern.match(line):
            old_match = old_school_pattern.match(line)
            speaker_name = old_match.group(1)
            dialogue = old_match.group(2)
            
        # If we found a speaker, process the segment
        if speaker_name:
            current_line_speaker = speaker_name
            
            # Handle inline (Solo) markers
            if solo_inline_pattern.search(dialogue) or "solo" in emotion.lower():
                is_solo = True
                dialogue = solo_inline_pattern.sub("", dialogue).strip()
            
            # Cleanup dialogue
            dialogue = dialogue.strip("\"' ")
            
            # Look for sub-emotions like [Whispering] inside the line
            inner_tags = tag_cleaner.findall(dialogue)
            if inner_tags:
                emotion = inner_tags[-1]
                dialogue = tag_cleaner.sub("", dialogue).strip()
            
            # Check for interruptions: ends with em-dash (U+2014) or --
            is_interrupted = dialogue.endswith("") or dialogue.endswith("--")
            if is_interrupted:
                dialogue = dialogue.rstrip("-").strip()
            
            # Resolve voice identity
            char_settings = character_dict.get(speaker_name, {})
            if isinstance(char_settings, str):
                base_voice = char_settings
            else:
                base_voice = char_settings.get("voice", f"A voice for {speaker_name}")
            
            final_voice = f"{base_voice}. Style: {voice_style}" if voice_style else base_voice
            
            if dialogue:
                segments.append({
                    "speaker": speaker_name,
                    "text": dialogue,
                    "voice": final_voice,
                    "emotion": emotion,
                    "is_solo": is_solo,
                    "is_interrupted": is_interrupted
                })
        elif current_line_speaker:
            # Multi-line dialogue continuation
            # Repeat the logic for the same speaker
            # (Simplified for brevity, usually just append text to last segment)
            if segments:
                segments[-1]["text"] += " " + line.strip()

    return segments

def build_pro_instruct(voice, emotion, is_solo):
    if is_solo:
        return f"Voice Identity: {voice}. Delivery: Internal monologue, whispery close-mic feel. Emotion: {emotion}."
    return f"Voice Identity: {voice}. Delivery Emotion: {emotion}."

# 
#  GENERATION ENGINE
# 

def generate_cinematic_pro(script, language, char_json, progress=gr.Progress(track_tqdm=True)):
    try:
        chars = json.loads(char_json)
    except:
        return None, None, "Error: Invalid JSON"
    
    segments = parse_advanced_script(script, chars)
    if not segments: return None, None, "Error: No segments"
    
    master = []
    sr = 24000
    last_speaker = None
    
    with torch.inference_mode():
        for i, seg in enumerate(segments):
            speaker = seg["speaker"]
            instruct = build_pro_instruct(seg["voice"], seg["emotion"], seg["is_solo"])
            
            progress((i/len(segments)), desc=f"{speaker} | {seg['emotion']}")
            
            # Multi-character pacing
            if last_speaker and last_speaker != speaker:
                # 0.1s cut if interrupted, else 0.4s natural gap
                gap = 0.1 if segments[i-1]["is_interrupted"] else 0.4
                master.append(np.zeros(int(sr * gap), dtype=np.float32))
            
            wavs, current_sr = design_model.generate_voice_design(text=seg["text"], language=language, instruct=instruct)
            sr = current_sr
            audio = wavs[0]
            
            # Abrupt cutoff effect
            if seg["is_interrupted"] and len(audio) > int(sr * 0.15):
                audio = audio[:-int(sr * 0.15)]
            
            master.append(audio)
            yield (sr, audio), None, f"Rendering: {speaker}"
            last_speaker = speaker
            
        final_wav = np.concatenate(master)
        path = os.path.join(OUTPUT_DIR, f"prod_{time.strftime('%H%M%S')}.wav")
        sf.write(path, final_wav, sr)
        yield (sr, master[-1]), (sr, final_wav), f" Saved: {path}"

# 
#  UI
# 

DEFAULT_CHARS = json.dumps({
    "Elena": {"voice": "British woman, sexy, cold, high-status voice"},
    "Julian": {"voice": "Deep, rugged male, hesitant, dark tones"},
    "Marcus": {"voice": "Formal, clipped, neutral male chauffeur"}
}, indent=2)

DEFAULT_SCRIPT = """[ Elena - British, Sexy, Cold] (Solo) The leather of the backseat was cold... but the man sitting three inches away from me was radiating enough heat to melt the glass partition.

[Julian - Deep, Rugged, Hesitant] "You didn't tell me where we were"

[Elena - Sharp, Playful] "Does it matter? You got in the car, Julian. That's the part that counts."

[Julian - Intense, Frustrated] "It matters when I have a gallery to"

[Elena - Silencing, Sultry] "Shh... You're thinking about the paintings again. The paintings are boring. You are not."

[Marcus - Formal, Clipped, Neutral] (via Intercom) "Pardon the intrusion, Madam. There is a police checkpoint two blocks ahead. Should I reroute?"

[Elena - Annoyed, Cold] "Do I look like I want to sit in traffic, Marcus? Take the bridge."

[Marcus - Submissive] "Understood, Madam. Adjusting course now."

[Julian - Solo/Internal] (Deep, Gritty) (Solo) She didn't even look at the driver. She didn't look at the road. She just kept those dark, predatory eyes on me.

[Elena - Intimate, Low] "You're very quiet, Julian. Is the bridge too... public for you?"

[Julian - Breathless] "I'm just wondering if you ever"

[Elena - Fast Interruption] "Never."

[Julian - Confused] "You didn't even let me finish the question."

[Elena - Knowing, Smug] "The answer is always 'never.' I never regret... and I never play fair."

[Marcus - Formal] "We are approaching the bridge, Madam. Estimated arrival at the estate is ten minutes."

[Elena - Dominant] "Make it five, Marcus. My guest is... losing his patience."
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple")) as app:
    gr.Markdown("#  Qwen3-TTS Pro: Cinematic Production Studio")
    with gr.Row():
        with gr.Column(scale=1):
            char_input = gr.Code(label="Characters (JSON)", language="json", value=DEFAULT_CHARS, lines=10)
        with gr.Column(scale=2):
            script_input = gr.Textbox(label="Cinematic Script", value=DEFAULT_SCRIPT, lines=14)
            render_btn = gr.Button(" Render Cinematic Production", variant="primary", size="lg")
    
    with gr.Row():
        live_audio = gr.Audio(label="Live Preview", type="numpy")
        master_audio = gr.Audio(label="Final Production", type="numpy")
    
    status = gr.Textbox(label="Status")
    render_btn.click(generate_cinematic_pro, [script_input, gr.State("English"), char_input], [live_audio, master_audio, status])

if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=8000)