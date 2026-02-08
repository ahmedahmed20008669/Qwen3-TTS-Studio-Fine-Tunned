# Qwen3-TTS: Fine-Tuned 1.7B Emotional & Clinical Speech Engine 🎧🔥

![Qwen3-TTS Pro Interface](C:\Users\ahmed\.gemini\antigravity\brain\b1421854-451d-4f12-8a71-8333ce6495c9\media__1770594598839.png)

This repository contains a professional-grade fine-tuning and inference suite for the **Qwen3-TTS 12Hz 1.7B** model. It has been specifically optimized for **Voice Identity Locking** and **Granular Emotional Control**, allowing for cinematic-quality speech synthesis with consistent vocal characters.

## 🚀 Key Features

*   **Emotional Identity Lock**: Strictly separates voice character (accent, pitch, gender) from delivery (emotions). The identity remains 100% consistent even during extreme shifts (e.g., whispering to shouting).
*   **Granular Segmenting Engine**: Real-time rendering that "cuts" on every tag. Hear emotional shifts instantly as they render.
*   **High-Fidelity 12Hz RVQ**: Uses 12Hz Residual Vector Quantization for crystal-clear acoustic reproduction.
*   **Hardware Supercharged**: Optimized for RTX 40-series GPUs using **SDPA** and **FlashAttention-2** with 16-thread CPU coordination.
*   **Pro-Save Architecture**: Automatic timestamped `.wav` exports for every generation.

---

## 🔬 The Mathematics & Architecture

### 1. Acoustic Modeling
The model operates on a **12Hz Discrete Codec Space**. Instead of continuous mel-spectrograms, it predicts discrete acoustic tokens sampled at 12Hz.
*   **Vector Quantization**: Uses a hierarchical codebook where the first level (Codec 0) defines the base acoustic structure and subsequent levels refine the detail.
*   **Objective Function**:
    $$L_{total} = L_{cross\_entropy} + 0.3 \times L_{sub\_talker}$$
    The training maximizes the log-likelihood of the next acoustic token given the text embeddings and previous codec tokens.

### 2. Speaker Injection Mechanism
During Fine-tuning (SFT), we lock the speaker identity by:
1.  Extracting a high-dimensional **Speaker Embedding** from reference audio.
2.  Injecting this embedding into a reserved weight slot (Index `3000`) in the `codec_embedding` layer.
3.  This ensures the model treats the "Character" as a fundamental part of its acoustic vocabulary.

---

## 🛠️ The Fine-Tuning Process

The fine-tuning follows a **Supervised Fine-Tuning (SFT)** approach optimized for single-speaker stability.

1.  **Data Preparation**:
    *   Audio is tokenized into 12Hz indices using `prepare_data.py`.
    *   Dataset format: `{"audio": "tgt.wav", "text": "...", "ref_audio": "ref.wav"}`.
2.  **Training Logic**:
    *   Optimizer: **AdamW** (Weight Decay: 0.01).
    *   Learning Rate: `2e-5` to `2e-6` for high stability.
    *   Precision: **Bfloat16 (Mixed)** using `accelerate`.
3.  **Checkpoints**:
    *   Speaker embeddings are detatched and saved into the final `model.safetensors` weight index `3000`.

---

## 💻 Code Structure

*   `app.py`: The "Hollywood Studio" Pro-Gradio interface.
*   `qwen_tts/`: Core model logic and inference wrappers.
*   `finetuning/`:
    *   `sft_12hz.py`: The main fine-tuning script.
    *   `dataset.py`: Memory-efficient data loader.
    *   `prepare_data.py`: Acoustic codec extractor.

---

## 🎮 How to Use

### Installation
```bash
pip install torch soundfile gradio qwen-tts accelerate
```

### Running the Studio
```bash
python app.py
```

### The "Identity Lock" Prompting
To maintain a perfect voice while shifting emotions, the engine uses a dual-instruction format:
*   **Voice Identity**: "A deep, raspy voice of a tired cowboy."
*   **Emotional Tags**: Use `[Whispering]`, `[Angry]`, or `[Excited]` anywhere in your script. The tags only affect the *mood*, not the *man*.

---

## 💾 Hardware Requirements
*   **GPU**: 12GB+ VRAM (Optimized for RTX 4070 SUPER).
*   **CPU**: 16 Threads for optimal inference coordination.
*   **RAM**: 32GB recommended.

---

## ⚖️ License
Released under the **Apache-2.0 License**. Based on the research and models by the **Alibaba Qwen Team**.
