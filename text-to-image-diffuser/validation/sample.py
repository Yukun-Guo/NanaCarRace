import argparse
import torch
from diffusers import StableDiffusionPipeline
from omegaconf import OmegaConf


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--config', default='configs/config.yaml')
    p.add_argument('--checkpoint', default=None)
    return p.parse_args()


def main():
    args = parse_args()
    cfg = OmegaConf.load(args.config)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    model_id = cfg.train.pretrained_model_name_or_path
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16 if device=='cuda' else torch.float32).to(device)
    if args.checkpoint:
        # Minimal: try to load unet weights if present
        try:
            state = torch.load(f"{args.checkpoint}/unet.pt", map_location=device)
            pipe.unet.load_state_dict(state)
            print('Loaded checkpoint')
        except Exception as e:
            print('Could not load checkpoint:', e)

    prompt = "A fantasy landscape painting, trending on artstation"
    image = pipe(prompt, guidance_scale=7.5, num_inference_steps=25).images[0]
    image.save('validation_sample.png')
    print('Saved validation_sample.png')

if __name__=='__main__':
    main()
