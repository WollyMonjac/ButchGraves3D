"""Preview: python3 t_props4.py -> out/p4.png"""
import sys, numpy as np
from PIL import Image
from sdf import *
import props4 as P4, monsters4 as M4
items = [('kapok', P4.kapok, 150, 160), ('palm', P4.palm, 100, 150), ('fern', P4.fern, 64, 40), ('vines', P4.vines, 40, 100),
         ('olmec', P4.olmec, 70, 80), ('jstatue', P4.jstatue, 40, 64), ('rack', P4.rack, 64, 70), ('ofrenda', P4.ofrenda, 56, 64),
         ('torch', P4.torch, 26, 86), ('pillar', P4.pillar, 30, 90), ('gold', P4.gold, 50, 24), ('tent', P4.tent, 110, 56),
         ('boulder', P4.boulder, 92, 92), ('idol', P4.idol, 20, 26), ('crane', P4.crane, 64, 100), ('crane_rant', lambda: P4.crane('rant'), 64, 110),
         ('melt', lambda: P4.crane('melt2'), 64, 110), ('shrunk', P4.shrunk, 30, 26), ('jskull', P4.jskull, 20, 16),
         ('dart', lambda: M4.dart(0), 24, 10), ('shot', lambda: M4.shot(0), 20, 12), ('disc', lambda: M4.disc(0), 30, 16), ('rock', lambda: M4.rock(0), 16, 14)]
filt = sys.argv[1:]
ims = []
for nm, fn, w, h in items:
    if filt and nm not in filt: continue
    im = render(fn(), w, h, cam_y=h / 96 / 2 - 0.02 if nm != 'vines' else 0.3 + h / 96 / 2, cam_h=h / 96, ss=1)
    ims.append(to_rgba(im))
W = sum(a.shape[1] + 4 for a in ims); H = max(a.shape[0] for a in ims)
sheet = Image.new('RGBA', (W, H), (40, 30, 50, 255)); x = 0
for a in ims:
    sheet.alpha_composite(Image.fromarray(a, 'RGBA'), (x, H - a.shape[0])); x += a.shape[1] + 4
sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save('out/p4.png')
