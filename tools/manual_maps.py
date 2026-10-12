#!/usr/bin/env python3
"""Draw the level maps for MANUAL.md (docs/maps/l<n>.png): walls, floors, hazards, doors, keys, weapons, secrets
(numbered stars), teleporters, start and exit. Usage: python3 manual_maps.py   (run after gen_levels.py)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_levels as GL, gen_levels2 as G2, gen_levels3 as G3, gen_levels4 as G4, defs

OUT = os.path.join(HERE, '..', 'docs', 'maps')
S = 8
TN = {v: k for k, v in defs.THINGS.items()}
FN = {v: k for k, v in GL.FLATS.items()}
WN = {v: k for k, v in GL.WALLS.items()}
F_DOOR, F_SECRET, F_EXIT, F_HURT, F_KRED, F_KBLUE, F_KGOLD, F_OUT = 1, 2, 4, 8, 16, 32, 64, 128
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 9)
FONT_S = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 8)

BG = (21, 20, 26)
WALL = (58, 55, 66)
WALL_EDGE = (92, 88, 102)
IN = (112, 104, 92)
OUTD = (78, 104, 64)
FLOOR = {'lava': (214, 86, 26), 'xlava': (214, 86, 26), 'slime': (92, 160, 44), 'water': (44, 104, 98), 'river': (45, 121, 168),
         'pit': (0, 0, 0), 'pplate': (224, 192, 48), 'spikes': (176, 176, 196), 'spikesoff': (176, 176, 196), 'shock': (60, 120, 255),
         'shiftflr': (154, 80, 224)}
DOOR = (192, 138, 58)
KEYC = {'red': (232, 48, 48), 'blue': (58, 106, 255), 'gold': (255, 210, 31)}
SECRET = (200, 64, 255)
EXIT = (48, 224, 96)


def draw_level(num, L):
    H, W = L.h, L.w
    img = Image.new('RGB', (W * S, H * S), BG)
    d = ImageDraw.Draw(img)
    open_ = L.wall == 0
    for y in range(H):
        for x in range(W):
            x0, y0 = x * S, y * S
            box = (x0, y0, x0 + S - 1, y0 + S - 1)
            f = L.flag[y, x]
            if L.wall[y, x]:
                wn = WN.get(L.wall[y, x] - 1, '')
                if f & F_EXIT:
                    d.rectangle(box, fill=EXIT)
                elif f & F_SECRET:
                    d.rectangle(box, fill=SECRET)
                elif f & F_DOOR:
                    c = KEYC['red'] if f & F_KRED else KEYC['blue'] if f & F_KBLUE else KEYC['gold'] if f & F_KGOLD else DOOR
                    d.rectangle(box, fill=c)
                    d.rectangle(box, outline=(20, 16, 10))
                elif wn == 'shiftwall':
                    d.rectangle(box, fill=FLOOR['shiftflr'])
                    d.line((x0, y0, x0 + S - 1, y0 + S - 1), fill=(60, 20, 90))
                elif wn in ('switch', 'switch2'):
                    d.rectangle(box, fill=(240, 240, 240))
                    d.ellipse((x0 + 2, y0 + 2, x0 + S - 3, y0 + S - 3), fill=(30, 30, 30))
                else:
                    edge = any(0 <= x + dx < W and 0 <= y + dy < H and open_[y + dy, x + dx]
                               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    d.rectangle(box, fill=WALL_EDGE if edge else WALL)
                continue
            fn = FN.get(L.flr[y, x], '')
            c = FLOOR.get(fn)
            if c is None and fn.startswith('conv_'):
                c = (200, 162, 40)
            if c is None:
                c = OUTD if f & F_OUT else IN
                if f & F_HURT:
                    c = (150, 60, 20)
            d.rectangle(box, fill=c)
            if fn in ('spikes', 'spikesoff'):
                for k in range(0, S, 3):
                    d.point((x0 + k, y0 + k), fill=(90, 90, 110))
                    d.point((x0 + S - 1 - k, y0 + k), fill=(90, 90, 110))
            if fn.startswith('conv_'):
                cx, cy = x0 + S // 2, y0 + S // 2
                dx, dy = {'conv_n': (0, -1), 'conv_s': (0, 1), 'conv_e': (1, 0), 'conv_w': (-1, 0)}[fn]
                d.line((cx - dx * 2, cy - dy * 2, cx + dx * 2, cy + dy * 2), fill=(90, 60, 10))
                d.point((cx + dx * 2 - dy, cy + dy * 2 - dx), fill=(90, 60, 10))
                d.point((cx + dx * 2 + dy, cy + dy * 2 + dx), fill=(90, 60, 10))
    # things
    def dot(x, y, col, r=3, label=None, fg=(0, 0, 0), font=FONT_S):
        cx, cy = int(x * S), int(y * S)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=(0, 0, 0))
        if label:
            d.text((cx, cy), label, font=font, fill=fg, anchor='mm')
    secrets = []
    for y in range(H):
        for x in range(W):
            if L.flag[y, x] & F_SECRET:
                secrets.append((x, y))
    things = [(TN[t[0]], t[1], t[2], int(t[3])) for t in L.things]
    pads = {}
    for k, x, y, s in things:
        if k == 'tpad':
            ch = (s >> 2) & 7
            dot(x, y, (180, 120, 255), 4, str(ch + 1))
        elif k == 'tdest':
            ch = (s >> 2) & 7
            cx, cy = int(x * S), int(y * S)
            d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), outline=(210, 160, 255), width=2)
        elif k in ('key_red', 'key_blue', 'key_gold'):
            dot(x, y, KEYC[k[4:]], 4, 'K', (0, 0, 0) if k != 'key_blue' else (255, 255, 255))
        elif k == 'idol':
            dot(x, y, KEYC['gold'], 5, 'I')
        elif k in ('shotgun', 'tommy', 'launcher'):
            dot(x, y, (255, 150, 40), 5, {'shotgun': 'B', 'tommy': 'T', 'launcher': 'L'}[k])
        elif k == 'brew':
            dot(x, y, (255, 110, 230), 3)
        elif k == 'armor':
            dot(x, y, (235, 235, 220), 3)
        elif k == 'boulder':
            dot(x, y, (150, 140, 120), 6, 'O', (40, 30, 20))
        elif k == 'darter':
            dot(x, y, (230, 40, 40), 2)
    for n, (x, y) in enumerate(secrets, 1):
        cx, cy = x * S + S // 2, y * S + S // 2
        r = 7
        pts = []
        import math
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=SECRET, outline=(255, 255, 255))
        d.text((cx + 9, cy - 1), str(n), font=FONT, fill=(255, 255, 255), anchor='lm', stroke_width=2, stroke_fill=(0, 0, 0))
    sx, sy = L.start[0], L.start[1]
    dot(sx, sy, (255, 255, 255), 5, 'S')
    for y in range(H):
        for x in range(W):
            if L.flag[y, x] & F_EXIT:
                d.text((x * S + S // 2, y * S + S // 2), 'X', font=FONT_S, fill=(0, 60, 20), anchor='mm')
    # trim the solid border, then scale up
    ys, xs = np.nonzero(open_ | (L.flag & (F_DOOR | F_EXIT) > 0))
    x0, x1, y0, y1 = max(0, xs.min() - 1), min(W, xs.max() + 2), max(0, ys.min() - 1), min(H, ys.max() + 2)
    img = img.crop((x0 * S, y0 * S, x1 * S, y1 * S))
    img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)      # sharp on high-density screens
    img.save(os.path.join(OUT, 'l%d.png' % num), optimize=True)
    return secrets


def legend():
    items = [('Start', 'S'), ('Exit', 'X'), ('Door', 'door'), ('Red / blue / gold door', 'keydoors'), ('Skull key', 'key'),
             ('Secret wall (numbered)', 'secret'), ('Weapon (Boomstick, Tommy, Launcher)', 'weapon'), ("Witch's Brew / armor", 'brew'),
             ('Teleporter pad / arrival', 'tele'), ('Lever / shifting wall', 'lever'), ('Conveyor belt / shock floor', 'conv'),
             ('Lava, slime, swamp water (they hurt)', 'hurt'), ('River (slow) / pit', 'river'),
             ('Pressure plate, dart trap / spikes', 'plate'), ('Golden idol / boulder', 'idol')]
    W, rowh = 300, 18
    img = Image.new('RGB', (W, rowh * len(items) + 8), BG)
    d = ImageDraw.Draw(img)
    for i, (txt, kind) in enumerate(items):
        y = 4 + i * rowh + rowh // 2
        x = 14

        def sq(xx, col):
            d.rectangle((xx - 5, y - 5, xx + 5, y + 5), fill=col, outline=(0, 0, 0))

        def ci(xx, col, lab=None, fg=(0, 0, 0)):
            d.ellipse((xx - 5, y - 5, xx + 5, y + 5), fill=col, outline=(0, 0, 0))
            if lab:
                d.text((xx, y), lab, font=FONT_S, fill=fg, anchor='mm')
        if kind == 'S': ci(x, (255, 255, 255), 'S')
        elif kind == 'X': sq(x, EXIT); d.text((x, y), 'X', font=FONT_S, fill=(0, 60, 20), anchor='mm')
        elif kind == 'door': sq(x, DOOR)
        elif kind == 'keydoors': sq(x, KEYC['red']); sq(x + 14, KEYC['blue']); sq(x + 28, KEYC['gold'])
        elif kind == 'key': ci(x, KEYC['red'], 'K'); ci(x + 14, KEYC['blue'], 'K', (255, 255, 255)); ci(x + 28, KEYC['gold'], 'K')
        elif kind == 'secret': sq(x, SECRET)
        elif kind == 'weapon': ci(x, (255, 150, 40), 'B'); ci(x + 14, (255, 150, 40), 'T'); ci(x + 28, (255, 150, 40), 'L')
        elif kind == 'brew': ci(x, (255, 110, 230)); ci(x + 14, (235, 235, 220))
        elif kind == 'tele': ci(x, (180, 120, 255), '1'); d.ellipse((x + 9, y - 5, x + 19, y + 5), outline=(210, 160, 255), width=2)
        elif kind == 'lever': sq(x, (240, 240, 240)); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(30, 30, 30)); sq(x + 14, FLOOR['shiftflr'])
        elif kind == 'conv': sq(x, (200, 162, 40)); sq(x + 14, FLOOR['shock'])
        elif kind == 'hurt': sq(x, FLOOR['lava']); sq(x + 14, FLOOR['slime']); sq(x + 28, FLOOR['water'])
        elif kind == 'river': sq(x, FLOOR['river']); sq(x + 14, (0, 0, 0))
        elif kind == 'plate': sq(x, FLOOR['pplate']); ci(x + 14, (230, 40, 40)); sq(x + 28, FLOOR['spikes'])
        elif kind == 'idol': ci(x, KEYC['gold'], 'I'); ci(x + 14, (150, 140, 120), 'O')
        d.text((x + 40, y), txt, font=FONT, fill=(230, 230, 230), anchor='lm')
    img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
    img.save(os.path.join(OUT, 'legend.png'), optimize=True)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    LV = GL.LEVELS + G2.LEVELS2 + G3.LEVELS3 + G4.LEVELS4
    for num, fn in enumerate(LV, 1):
        L = fn()
        for kind, x, y in GL.EXTRA_LOOT.get(num, []):
            L.put(kind, x, y)
        sec = draw_level(num, L)
        print(num, L.name, 'secrets', sec)
    legend()
