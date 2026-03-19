import argparse
import torch
import gradio as gr
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
    device = cfg.demo.device if torch.cuda.is_available() else 'cpu'

    model_id = cfg.train.pretrained_model_name_or_path
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16 if device=='cuda' else torch.float32).to(device)
    if args.checkpoint:
        try:
            state = torch.load(f"{args.checkpoint}/unet.pt", map_location=device)
            pipe.unet.load_state_dict(state)
            print('Loaded checkpoint')
        except Exception as e:
            print('Could not load checkpoint:', e)

    def gen(prompt, steps=25, scale=7.5):
        img = pipe(prompt, guidance_scale=scale, num_inference_steps=int(steps)).images[0]
        return img

    demo = gr.Interface(fn=gen, inputs=[gr.Textbox(label='Prompt'), gr.Slider(5,50,value=25,label='Steps'), gr.Slider(1.0,15.0,value=7.5,step=0.1,label='Guidance')], outputs='image', title='Text→Image Diffuser Demo')
    demo.launch(server_port=cfg.demo.port, share=False)

if __name__=='__main__':
    main()
