import numpy as np
from PIL import Image
import textures2 as T2
ims = []
for n, f in T2.WALLS2 + T2.FLATS2:
    c, g = f()
    ims.append((n, (np.clip(c, 0, 1) * 255).astype(np.uint8)))
cols = 8
rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGB', (cols * 68, rows * 68), (20, 20, 20))
for k, (n, a) in enumerate(ims):
    sh.paste(Image.fromarray(a), ((k % cols) * 68, (k // cols) * 68))
sh.resize((sh.width * 2, sh.height * 2), Image.NEAREST).save('out/tex2.png')
sk = [f()[0] for n, f in T2.SKIES2]
im = np.concatenate([(np.clip(s, 0, 1) * 255).astype(np.uint8) for s in sk], 0)
Image.fromarray(im).save('out/sky2.png')
print([n for n, a in ims])
