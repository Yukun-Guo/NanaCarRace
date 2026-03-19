# text-to-image-diffuser

PyTorch + Hugging Face Diffusers example: text→image training, validation, and Gradio demo.

This updated scaffold includes an accelerate-compatible training script, optional LoRA-style adapters (implemented as fine-tuning of UNet + text encoder), a synthetic dataset generator for quick smoke tests, and a Gradio demo.

Contents
- training/train_hf.py — HF-style training loop (supports caption-conditioning; UNet + text encoder fine-tuning)
- validation/sample.py — sampling/validation script
- demo/app.py — Gradio demo app (loads checkpoint and generates image)
- data/generate_synthetic.py — small synthetic dataset generator for smoke tests
- requirements.txt — Python deps
- configs/config.yaml — default training/validation settings
- .github/workflows/ci.yml — lint + smoke test workflow

Quick start (local)
1. Install deps (Python 3.10+):
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Generate a tiny synthetic dataset for a quick smoke run:
   python data/generate_synthetic.py

3. Train (single GPU or CPU):
   python training/train_hf.py --config configs/config.yaml

4. Run demo (after checkpoint saved):
   python demo/app.py --checkpoint outputs/checkpoint_100

Notes and next steps
- This scaffold intentionally avoids heavy dependencies like PEFT or WandB to keep CI fast.
- For larger-scale training use the official Hugging Face example scripts with accelerate launch and optional LoRA/PEFT support.

License: MIT
