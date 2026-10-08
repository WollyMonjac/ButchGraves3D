import numpy as np
from PIL import Image
from textures import *
allt = WALLS + FLATS
cols = 8
rows = (len(allt) + cols - 1) // cols
sheet = np.zeros((rows * 66, cols * 66, 3))
for k, (nm, fn) in enumerate(allt):
    c, g = fn()
    sheet[(k // cols) * 66:(k // cols) * 66 + 64, (k % cols) * 66:(k % cols) * 66 + 64] = np.clip(c, 0, 1)
Image.fromarray((sheet * 255).astype(np.uint8)).resize((cols * 66 * 2, rows * 66 * 2), Image.NEAREST).save('out/tex.png')
for k in (0, 1):
    c, g = sky(k)
    Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)).resize((1024, 200), Image.NEAREST).save('out/sky%d.png' % k)
