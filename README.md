# Qwen3-TTS Pro: Cinematic Production Studio 🎬🎧

![Studio Interface](assets/studio_interface.png)

## 👤 Main Developer
**Ahmed Hassn** ([GitHub](https://github.com/ahmedahmed20008669))

---

## 📖 What's New: The Cinematic Pro Upgrade
This repository has been upgraded to a **Cinematic Production Studio**. It now goes beyond simple text-to-speech by offering a full multi-character casting engine with high-fidelity control over dramatic timing and acoustic perspective.

### 🌟 Core Cinematic Features:
1.  **Multi-Character Casting**: Define a cast of characters in JSON format. The engine automatically switches voices based on your script.
2.  **Screenplay Pro Parsing**: Supports the `[Character - Voice, Emotion]` tag format for granular, inline directing.
3.  **The Interruption Engine**: Handles the `—` (em-dash) naturally. It abruptly cuts the currently speaking character and speeds up the next character's entry for realistic "cutting off" dialogue.
4.  **Acoustic Solo Mode**: Use `(Solo)` to trigger a **close-mic proximity effect**. This makes internal monologues or whispers sound intimate and "inside the head" rather than projected.

---

## 💡 Creative Ideas & Use Cases
The Cinematic Pro Studio opens up professional-grade audio production for:
*   **Audiobook Dramatization**: Render entire scenes with different narrators and character voices in one pass.
*   **NPC Dialogue Systems**: Create realistic, interrupted conversations for game characters.
*   **Podcast Ads & Skits**: Direct multi-voice skits with precise emotional shifts.
*   **Shadow Coaching**: Use internal monologues `(Solo)` to contrast what a character says vs. what they think.
*   **Dynamic Documentaries**: Switch between formal narration and emotional "eye-witness" quotes seamlessly.

---

## 🔬 Technical Deep Dive
### 1. The Interruption Mechanism
When the parser detects an em-dash (`—`), it applies a 150ms hard-cut to the generated audio buffer and reduces the inter-segment silence from 400ms to 100ms. This simulates the overlapping response of a real conversation.

### 2. Proximity Effect (Solo)
The `(Solo)` marker injects specific acoustic instructions into the Qwen3-TTS prompt, requesting lower gain-variance and increased breathiness, simulating a voice actor standing inches from a cardioid microphone.

---

## 🎮 Installation & Quickstart

### 1. Clone & Setup
```bash
git clone https://github.com/ahmedahmed20008669/Qwen3-TTS-Studio-Fine-Tunned.git
cd Qwen3-TTS-Studio-Fine-Tunned
pip install -r requirements.txt
```

### 2. Launch the Studio
```bash
python app.py
```

### 3. Directing Your Scene
1.  **Define Your Cast**: Add characters to the JSON panel (e.g., `Elena`, `Julian`, `Marcus`).
2.  **Write the Script**: Use tags like `[Elena - Sexy, Cold]` and markers like `(Solo)` or `—`.
3.  **Render**: Get individual segment previews and a final compiled master.

---

## 🤝 Credits
Built upon the foundational models and research by the [Alibaba Qwen Team](https://github.com/QwenLM/Qwen3-TTS). Special thanks to the open-source community for the 12Hz quantization breakthroughs.

## ⚖️ License
Released under the **Apache-2.0 License**.