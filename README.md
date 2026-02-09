# Qwen3-TTS Studio Suite 🎧🚀

Welcome to the **Qwen3-TTS Studio**, a collection of professional-grade speech synthesis tools powered by the 12Hz RVQ 1.7B model. This repository contains two distinct studio projects tailored for different production needs.

## 👤 Main Developer
**Ahmed Hassn** ([GitHub](https://github.com/ahmedahmed20008669))

---

## 📂 Project Navigation

### 1. [Emotional Identity Lock (Root)](app.py)
The original studio engine focused on **Voice Character Consistency**.
*   **Best for**: Podcasts, Narrations, and single-character audiobooks.
*   **Feature**: Defines one voice identity and shifts emotions mid-script without the character "drifting."
*   **How to Run**: `python app.py` (from the root).

### 2. [Cinematic Pro-Studio (Sub-Project)](Cinematic-Studio/)
A high-end **Multi-Character Casting Engine** for complex dramatic productions.
*   **Best for**: Audio Dramas, NPC Conversations, and Screenplays.
*   **Feature**: Multi-character casting, em-dash (`—`) interruption handling, and `(Solo)` internal monologues with proximity effect.
*   **How to Run**: `cd Cinematic-Studio && python app.py`.

---

## 🛠️ Installation
```bash
git clone https://github.com/ahmedahmed20008669/Qwen3-TTS-Studio-Fine-Tunned.git
cd Qwen3-TTS-Studio-Fine-Tunned
pip install -r requirements.txt
```

---

## 🤝 Credits
Built upon the foundational models and research by the [Alibaba Qwen Team](https://github.com/QwenLM/Qwen3-TTS).

## ⚖️ License
Released under the **Apache-2.0 License**.