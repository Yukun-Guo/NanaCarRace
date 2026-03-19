Push instructions

1. On your machine, create the GitHub repo (if not already) named `text-to-image-diffuser`.
2. From this workspace folder (where these files are), run:

   git init
   git add .
   git commit -m "Initial scaffold: training, validation, demo"
   git branch -M main
   git remote add origin git@github.com:YOUR_USERNAME/text-to-image-diffuser.git
   git push -u origin main

Replace the remote URL as appropriate (https or ssh). If you prefer HTTPS:
   git remote add origin https://github.com/YOUR_USERNAME/text-to-image-diffuser.git

3. To run locally (recommended in a virtualenv):
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

4. Prepare dataset: create data/images/ and data/captions.jsonl (each line JSON {"image":"file.jpg","caption":"..."})

5. Train (example):
   python training/train.py --config configs/config.yaml

6. Run demo after training checkpoint appears:
   python demo/app.py --checkpoint outputs/checkpoint_100

Notes:
- This scaffold is minimal and intended for example/demo purposes. For production-quality training, use Hugging Face's `train_text_to_image_lora.py` style utilities, full accelerate configs, and careful dataset preprocessing.
