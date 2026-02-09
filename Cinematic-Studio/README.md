# Qwen3-TTS: Cinematic Pro-Studio 🎬🎭

![Cinematic Studio Interface](assets/studio_interface.png)

## 👤 Main Developer
**Ahmed Hassn** ([GitHub](https://github.com/ahmedahmed20008669))

---

## 🎭 The Multi-Character Casting Engine
The **Cinematic Pro-Studio** is a high-end implementation of Qwen3-TTS designed for dramatic audio production. It allows you to direct complex scenes with multiple characters, emotional nuances, and natural conversational timing.

### 🌟 Key Cinematic Features:
*   **Multi-Character Casting**: Define a cast of characters in JSON format. The engine automatically switches voices based on your script.
*   **Em-Dash Interruption Engine**: Handles the `—` (em-dash) naturally. Dialogue is abruptly cut and the next speaker entry is accelerated for realistic "cutting off" effects.
*   **Proximity Effect (Solo)**: Use the `(Solo)` tag to trigger an intimate, close-mic acoustic delivery—perfect for internal monologues.
*   **Dynamic Emotional Scaling**: Direct characters inline using `[Name - Voice, Emotion]` tags.

---

## 📂 Version Navigation
*   **🚀 [View Version 1: Emotional Identity Lock (Root)](../README.md)**: Optimized for single-character consistency.
*   **🎬 [View Version 2: Cinematic Pro-Studio (Current)](README.md)**: Optimized for multi-character drama.

---

## 🎮 How to Run
1. Ensure dependencies are installed (`pip install -r ../requirements.txt`).
2. Navigate to this directory: `cd Cinematic-Studio`
3. Launch the studio: `python app.py`

---

## 🛠️ Technical Details
*   **Model**: Qwen3-TTS-12Hz-1.7B
*   **Precision**: BF16 (Cuda Optimized)
*   **Features**: RVQ 12Hz Compression, 16 CPU Threading, Semantic Interruption Logic.

---

## 🤝 Credits & License
Built by Ahmed Hassn. Based on Qwen3-TTS. Licensed under Apache-2.0.