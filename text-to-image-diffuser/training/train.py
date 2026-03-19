import argparse
import os
import random
from omegaconf import OmegaConf
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms
from tqdm import tqdm

from diffusers import UNet2DConditionModel, AutoencoderKL, DDPMScheduler, StableDiffusionPipeline
from transformers import CLIPTokenizer, CLIPTextModel

# Minimal dataset loader expecting captions.jsonl lines with {"image":"...","caption":"..."}
class CaptionedImageDataset(Dataset):
    def __init__(self, images_root, captions_file, image_size=512):
        import json
        self.images_root = images_root
        with open(captions_file, 'r') as f:
            self.items = [json.loads(l) for l in f if l.strip()]
        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        it = self.items[idx]
        path = os.path.join(self.images_root, it['image'])
        image = Image.open(path).convert('RGB')
        pixel = self.transform(image)
        return {'pixel_values': pixel, 'caption': it.get('caption','')}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=str, default='configs/config.yaml')
    return p.parse_args()


def main():
    args = parse_args()
    cfg = OmegaConf.load(args.config)
    os.makedirs(cfg.train.output_dir, exist_ok=True)

    ds = CaptionedImageDataset(cfg.train.dataset.images_root, cfg.train.dataset.captions_file, cfg.train.image_size)
    dl = DataLoader(ds, batch_size=cfg.train.train_batch_size, shuffle=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # NOTE: For a real project use Hugging Face Diffusers training utilities (example simplified)
    # Load tokenizer and text encoder
    tokenizer = CLIPTokenizer.from_pretrained('openai/clip-vit-large-patch14')
    text_encoder = CLIPTextModel.from_pretrained('openai/clip-vit-large-patch14').to(device)

    # Load autoencoder and UNet from pretrained checkpoint
    vae = AutoencoderKL.from_pretrained(cfg.train.pretrained_model_name_or_path, subfolder='vae').to(device)
    unet = UNet2DConditionModel.from_pretrained(cfg.train.pretrained_model_name_or_path, subfolder='unet').to(device)

    optimizer = torch.optim.AdamW(unet.parameters(), lr=cfg.train.learning_rate)

    global_step = 0
    for epoch in range(100000):
        for batch in tqdm(dl):
            captions = batch['caption']
            # Tokenize
            enc = tokenizer(captions, padding='max_length', truncation=True, max_length=77, return_tensors='pt')
            input_ids = enc.input_ids.to(device)
            with torch.no_grad():
                text_embeds = text_encoder(input_ids)[0]

            pixel_values = batch['pixel_values'].to(device)
            # Convert images to latents via VAE
            with torch.no_grad():
                latents = vae.encode(pixel_values).latent_dist.sample() * 0.18215

            # Sample noise and timesteps
            noise = torch.randn_like(latents)
            scheduler = DDPMScheduler()
            timesteps = torch.randint(0, scheduler.num_train_timesteps, (latents.shape[0],), device=device).long()
            noisy_latents = latents + noise

            # Predict noise with unet (conditioning omitted for brevity)
            pred = unet(noisy_latents, timesteps, encoder_hidden_states=text_embeds).sample
            loss = torch.nn.functional.mse_loss(pred, noise)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            global_step += 1
            if global_step % cfg.train.logging_steps == 0:
                print(f"step {global_step} loss {loss.item():.4f}")
            if global_step % cfg.train.save_steps == 0:
                out = os.path.join(cfg.train.output_dir, f"checkpoint_{global_step}")
                os.makedirs(out, exist_ok=True)
                # Save minimal weights
                torch.save(unet.state_dict(), os.path.join(out, 'unet.pt'))
                print(f"Saved checkpoint to {out}")
            if global_step >= cfg.train.max_train_steps:
                print("Done training")
                return

if __name__ == '__main__':
    main()
