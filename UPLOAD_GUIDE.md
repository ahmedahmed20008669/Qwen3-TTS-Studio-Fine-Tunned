# Professional GitHub Upload Guide: Large AI Models 🚀

Because your fine-tuned model files (Safetensors) are very large (several GBs), you cannot upload them using standard GitHub commands. You must use **Git LFS (Large File Storage)**.

### Step 1: Install Git LFS
If you don't have it yet, run this in your terminal:
```bash
git lfs install
```

### Step 2: Initialize & Track Large Files
Navigate to your project folder and tell Git to handle large AI files:
```bash
git init
git lfs track "*.safetensors"
git lfs track "*.bin"
git add .gitattributes
```

### Step 3: Add your Files & Documentation
Copy the contents of `GITHUB_README.md` into your main `README.md`, then add everything:
```bash
git add .
git commit -m "Initial commit: Fine-tuned Qwen3-TTS 1.7B with Emotional Identity Lock"
```

### Step 4: Create GitHub Repository
1. Go to [GitHub.com](https://github.com) and create a new repository called `Qwen3-TTS-Studio`.
2. Do **not** initialize with a README (you already have one).

### Step 5: Push to GitHub
Replace `YOUR_USERNAME` with your real name and run:
```bash
git remote add origin https://github.com/YOUR_USERNAME/Qwen3-TTS-Studio.git
git branch -M main
git push -u origin main
```

---

### 🔥 Pro Tip: Use Hugging Face for the Weights
If GitHub LFS gives you any trouble (they have storage limits), it is "industry standard" to:
1. Upload the **code** to GitHub.
2. Upload the **large weights** to [Hugging Face](https://huggingface.co).
3. Put a link to Hugging Face in your GitHub README.
