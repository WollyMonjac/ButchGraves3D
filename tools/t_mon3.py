"""Quick preview: python3 t_mon2.py name W H [ss]  -> out/m3_<name>.png (walk1 walk2 attack pain)."""
import time, sys, numpy as np
from PIL import Image
from sdf import *
import monsters3 as M2
fn = getattr(M2, sys.argv[1])
W, H = int(sys.argv[2]), int(sys.argv[3])
ss = int(sys.argv[4]) if len(sys.argv) > 4 else 1
poses = sys.argv[5].split(',') if len(sys.argv) > 5 else ['walk1', 'walk2', 'attack', 'pain']
t = time.time(); ims = []
for pose in poses:
    im = render(fn(pose), W, H, cam_y=H / 96 / 2 - 0.01, cam_h=H / 96, ss=ss)
    a = to_rgba(im); a[im.glow, :3] = np.minimum(255, a[im.glow, :3].astype(int) + 40)
    ims.append(a)
print(sys.argv[1], '%.1fs' % (time.time() - t))
sheet = Image.new('RGBA', (W * len(ims), H), (40, 30, 50, 255))
for i, a in enumerate(ims): sheet.alpha_composite(Image.fromarray(a, 'RGBA'), (i * W, 0))
sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save('out/m3_%s.png' % sys.argv[1])
