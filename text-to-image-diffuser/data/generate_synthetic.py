"""Generate a tiny synthetic dataset of colored shapes with captions for CI/smoke tests."""
import os
from PIL import Image, ImageDraw
import json
import random

OUT_DIR = 'data/images'
os.makedirs(OUT_DIR, exist_ok=True)
lines = []
shapes = ['circle','square','triangle']
colors = ['red','green','blue','yellow']
for i in range(8):
    w=256
    h=256
    img = Image.new('RGB',(w,h),'white')
    draw = ImageDraw.Draw(img)
    shape = random.choice(shapes)
    color = random.choice(colors)
    if shape=='circle':
        draw.ellipse((60,60,196,196), fill=color)
    elif shape=='square':
        draw.rectangle((60,60,196,196), fill=color)
    else:
        draw.polygon([(128,48),(48,196),(208,196)], fill=color)
    name=f'synth_{i}.png'
    img.save(os.path.join(OUT_DIR,name))
    caption=f'A {color} {shape} on white background.'
    lines.append({'image':name,'caption':caption})

with open('data/captions.jsonl','w') as f:
    for l in lines:
        f.write(json.dumps(l)+'\n')
print('Wrote synthetic dataset with', len(lines), 'images')
