"""Quick preview of sprite jobs at ss=1: python3 t_jobs.py out.png name1 name2 ..."""
import sys, numpy as np
from PIL import Image
from multiprocessing import Pool
import gen_sprites as G
from sdf import render, to_rgba

def one(n):
    name, spec, w, h, y0, ss, kind = [j for j in G.JOBS if j[0] == n][0]
    ps = G.build(spec)
    cam_h = h / G.PPU
    im = render(ps, w, h, cam_y=y0 + cam_h / 2, cam_h=cam_h, ss=1)
    a = to_rgba(im)
    return a

if __name__ == '__main__':
    names = sys.argv[2:]
    with Pool(2) as p:
        ims = p.map(one, names)
    W = sum(a.shape[1] for a in ims) + 4 * len(ims); H = max(a.shape[0] for a in ims)
    sheet = Image.new('RGBA', (W, H), (40, 30, 50, 255)); x = 0
    for a in ims:
        sheet.alpha_composite(Image.fromarray(a, 'RGBA'), (x, H - a.shape[0])); x += a.shape[1] + 4
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(sys.argv[1])
