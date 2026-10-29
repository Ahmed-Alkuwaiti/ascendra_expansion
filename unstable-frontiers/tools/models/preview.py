"""python3 preview.py <creature> <out_dir>: renders the creature's poses (preview renders, not screenshots)."""
import importlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
from render import render
name, out = sys.argv[1], sys.argv[2]
mod = importlib.import_module(name)
m, anims = mod.write()
tex = Image.open(os.path.join(mod.OUT, f'textures/entity/{getattr(mod, "NAME", name)}.png'))
os.makedirs(out, exist_ok=True)
shots = [('rest', None, 0, 215), ('rest_side', None, 0, 270), ('rest_back', None, 0, 35)]
for a in anims:
    shots.append((a.name.split('.')[-1], a, a.length * 0.45, 215))
tiles = []
for label, a, t, yaw in shots:
    p = os.path.join(out, f'{name}_{label}.png')
    render(m, tex, p, anim=a, t=t, yaw=yaw, size=420, label=f'{name} {label} (render)')
    tiles.append(Image.open(p))
cols = 4
sheet = Image.new('RGB', (cols * 420, ((len(tiles) + cols - 1) // cols) * 420), (20, 20, 26))
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % cols) * 420, (i // cols) * 420))
sheet.save(os.path.join(out, f'{name}_sheet.png'))
print('sheet', len(tiles))
