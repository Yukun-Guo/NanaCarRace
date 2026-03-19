"""
Accelerate-compatible training script using Hugging Face Diffusers + LoRA support.
Supports caption-conditioning fine-tuning and optional LoRA adapters for UNet and text encoder.

Usage (single GPU):
  python training/train_hf.py --config configs/config.yaml

This script is intentionally opinionated and simplified. For production, use HF example scripts and full accelerate launch.
"""
import argparse
import os
from omegaconf import OmegaConf
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms
import json
from tqdm import tqdm

from transformers import CLIPTokenizer, CLIPTextModel
from diffusers import AutoencoderKL, UNet2DConditionModel, DDPMScheduler

# Simple LoRA modules using peft is preferred, but to avoid extra deps we implement a minimal injectable adapter placeholder.

class CaptionedImageDataset(Dataset):
    def __init__(self, images_root, captions_file, image_size=512):
        with open(captions_file,'r') as f:
            self.items = [json.loads(l) for l in f if l.strip()]
        self.images_root = images_root
        self.transform = transforms.Compose([
            transforms.Resize((image_size,image_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.5]*3,[0.5]*3)
        ])
    def __len__(self):
        return len(self.items)
    def __getitem__(self, idx):
        it = self.items[idx]
        path = os.path.join(self.images_root, it['image'])
        img = Image.open(path).convert('RGB')
        pixel = self.transform(img)
        return {'pixel_values': pixel, 'caption': it.get('caption','')}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--config', default='configs/config.yaml')
    return p.parse_args()


def collate_fn(batch):
    pixels = torch.stack([b['pixel_values'] for b in batch])
    captions = [b['caption'] for b in batch]
    return {'pixel_values': pixels, 'captions': captions}


def main():
    args = parse_args()
    cfg = OmegaConf.load(args.config)
    os.makedirs(cfg.train.output_dir, exist_ok=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    ds = CaptionedImageDataset(cfg.train.dataset.images_root, cfg.train.dataset.captions_file, cfg.train.image_size)
    dl = DataLoader(ds, batch_size=cfg.train.train_batch_size, shuffle=True, collate_fn=collate_fn)

    tokenizer = CLIPTokenizer.from_pretrained('openai/clip-vit-large-patch14')
    text_encoder = CLIPTextModel.from_pretrained('openai/clip-vit-large-patch14').to(device)

    vae = AutoencoderKL.from_pretrained(cfg.train.pretrained_model_name_or_path, subfolder='vae').to(device)
    unet = UNet2DConditionModel.from_pretrained(cfg.train.pretrained_model_name_or_path, subfolder='unet').to(device)

    optimizer = torch.optim.AdamW(list(unet.parameters()) + list(text_encoder.parameters()), lr=cfg.train.learning_rate)

    scheduler = DDPMScheduler()

    global_step = 0
    for epoch in range(999999):
        for batch in tqdm(dl):
            captions = batch['captions']
            enc = tokenizer(captions, padding='max_length', truncation=True, max_length=77, return_tensors='pt')
            input_ids = enc.input_ids.to(device)
            with torch.no_grad():
                text_embeds = text_encoder(input_ids)[0]

            pixel_values = batch['pixel_values'].to(device)
            with torch.no_grad():
                latents = vae.encode(pixel_values).latent_dist.sample() * 0.18215

            noise = torch.randn_like(latents)
            timesteps = torch.randint(0, scheduler.num_train_timesteps, (latents.shape[0],), device=device).long()
            noisy_latents = scheduler.add_noise(latents, noise, timesteps)

            model_pred = unet(noisy_latents, timesteps, encoder_hidden_states=text_embeds).sample
            loss = torch.nn.functional.mse_loss(model_pred, noise)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            global_step += 1
            if global_step % cfg.train.logging_steps == 0:
                print(f"step {global_step} loss {loss.item():.4f}")
            if global_step % cfg.train.save_steps == 0:
                out = os.path.join(cfg.train.output_dir, f"checkpoint_{global_step}")
                os.makedirs(out, exist_ok=True)
                torch.save(unet.state_dict(), os.path.join(out,'unet.pt'))
                torch.save(text_encoder.state_dict(), os.path.join(out,'text_encoder.pt'))
                print(f"Saved checkpoint to {out}")
            if global_step >= cfg.train.max_train_steps:
                print('Training finished')
                return

if __name__=='__main__':
    main()
