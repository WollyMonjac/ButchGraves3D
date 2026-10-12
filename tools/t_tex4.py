import numpy as np
from PIL import Image
from textures4 import *
allt = WALLS4 + FLATS4
cols = 7
rows = (len(allt) + cols - 1) // cols
sheet = np.zeros((rows * 66, cols * 66, 3))
for k, (nm, fn) in enumerate(allt):
    c, g = fn()
    sheet[(k // cols) * 66:(k // cols) * 66 + 64, (k % cols) * 66:(k % cols) * 66 + 64] = np.clip(c, 0, 1)
Image.fromarray((sheet * 255).astype(np.uint8)).resize((cols * 66 * 3, rows * 66 * 3), Image.NEAREST).save('out/tex4.png')
sk = []
for nm, fn in SKIES4:
    c, g = fn()
    sk.append(np.clip(c, 0, 1))
Image.fromarray((np.concatenate(sk, 0) * 255).astype(np.uint8)).resize((1024, 600), Image.NEAREST).save('out/sky4.png')
