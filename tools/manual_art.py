#!/usr/bin/env python3
"""Sprite tiles for MANUAL.md (docs/img/*.png): every monster, boss, weapon and pickup on a dark square.
Usage: python3 manual_art.py   (run after gen_sprites.py)"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(HERE, 'spr')
OUT = os.path.join(HERE, '..', 'docs', 'img')
BG = (27, 26, 32, 255)

TILES = {   # out name: (sprite, tile size)
    'ghoul': 'zombie_walk1', 'scarecrow': 'scarecrow_attack', 'wraith': 'wraith_walk1', 'witch': 'witch_attack',
    'skeleton': 'skel_walk1', 'clown': 'clown_attack', 'werewolf': 'wolf_walk1', 'bat': 'bat_walk1', 'bride': 'vamp_attack',
    'frankenbot': 'frank_walk1', 'drone': 'drone_walk1', 'cyberghoul': 'cyborg_attack', 'spider': 'spider_walk1',
    'mummy': 'mummy_walk1', 'jaguar': 'jaguar_attack', 'conquistador': 'conq_attack', 'weeper': 'weeper_walk1',
    'pumpkin_king': 'boss_attack', 'giggles': 'giggles_attack', 'count': 'count_attack', 'prime': 'prime_attack', 'seven': 'seven_attack',
    'candy': 'candy', 'bucket': 'bucket', 'brew': 'brew', 'armor': 'armor', 'bullets': 'bullets', 'shells': 'shells',
    'pumpkins': 'pumpkins', 'key_red': 'key_red', 'key_blue': 'key_blue', 'key_gold': 'key_gold', 'idol': 'idol', 'keg': 'keg',
    'toxic': 'toxic', 'telepad': 'telepad', 'boulder': 'boulder_1',
    'w_shovel': 'w_shovel0', 'w_revolver': 'w_revolver0', 'w_shotgun': 'w_shotgun0', 'w_tommy': 'w_tommy0', 'w_launcher': 'w_launcher0',
}


def tile(src, size, wide=False):
    im = Image.open(os.path.join(SPR, src + '.png')).convert('RGBA')
    a = im.split()[3].point(lambda v: 255 if v > 0 else 0)      # glow pixels (alpha 128) are solid too
    im.putalpha(a)
    tw, th = (size * 3 // 2, size) if wide else (size, size)
    pad = 6
    k = min((tw - 2 * pad) / im.width, (th - 2 * pad) / im.height)
    ki = int(k) if k >= 1 else k
    nw, nh = max(1, int(im.width * ki)), max(1, int(im.height * ki))
    im = im.resize((nw, nh), Image.NEAREST if k >= 1 else Image.LANCZOS)
    t = Image.new('RGBA', (tw, th), BG)
    t.alpha_composite(im, ((tw - nw) // 2, th - pad - nh if not wide else (th - nh) // 2 + 4))
    return t.convert('RGB')


def tex_img(name):
    """A 64x64 game texture as an image (the raw colours, before the game's palette)."""
    import numpy as np
    import textures as TX, textures2 as T2, textures3 as T3, textures4 as T4
    fns = dict(TX.WALLS + T2.WALLS2 + T3.WALLS3 + T4.WALLS4 + TX.FLATS + T2.FLATS2 + T3.FLATS3 + T4.FLATS4)
    c, _ = fns[name]()
    return Image.fromarray((np.clip(c, 0, 1) * 255 + 0.5).astype('uint8'), 'RGB')


def tex_tile(names):
    """One texture fills a 128 tile; two sit side by side on a dark tile."""
    if len(names) == 1:
        return tex_img(names[0]).resize((128, 128), Image.NEAREST)
    t = Image.new('RGB', (128, 128), BG[:3])
    for k, n in enumerate(names):
        t.paste(tex_img(n).resize((60, 60), Image.NEAREST), (3 + k * 64, 34))
    return t


def scene_tile(path, box):
    """A square crop of a game frame."""
    return Image.open(path).convert('RGB').crop(box).resize((128, 128), Image.LANCZOS)


def pickups_tile():
    t = Image.new('RGBA', (72, 72), BG)
    y = 4
    for n in ('pk_shotgun', 'pk_tommy', 'pk_launcher'):
        im = Image.open(os.path.join(SPR, n + '.png')).convert('RGBA')
        im.putalpha(im.split()[3].point(lambda v: 255 if v > 0 else 0))
        if im.width > 64:
            im = im.resize((64, im.height * 64 // im.width), Image.LANCZOS)
        t.alpha_composite(im, ((72 - im.width) // 2, y))
        y += im.height + 2
    return t.convert('RGB').resize((144, 144), Image.NEAREST)


EXTRA_TEX = {'lava': ['lava'], 'slime': ['slime'], 'swampwater': ['water'], 'conveyor': ['conv_e'], 'shock': ['shock'],
             'lever': ['switch', 'shiftwall'], 'plate': ['pplate', 'darts'], 'spikes': ['spikes'], 'river': ['river']}
ROOT = os.path.join(HERE, '..')
SCENES = {   # tile: (frame, crop box). docs/src frames come from test/sim/Flash.java:
    # Flash 1 20.5 22.5 3072 flash.png (a lightning flash), Flash 17 32.5 11.5 1024 pit.png 0 (the escape tunnel's pit)
    'lightning': (os.path.join(ROOT, 'docs', 'src', 'flash.png'), (10, 0, 210, 200)),
    'pit': (os.path.join(ROOT, 'docs', 'src', 'pit.png'), (20, 60, 220, 260)),
    'radio': (os.path.join(ROOT, 'screenshots', '33_the_fog.png'), (20, 0, 220, 200)),
    'otherworld': (os.path.join(ROOT, 'screenshots', '34_the_other_world.png'), (20, 40, 220, 240)),
    'trigger': (os.path.join(ROOT, 'screenshots', '31_the_boulder.png'), (20, 30, 220, 230)),
}


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for nm, names in EXTRA_TEX.items():
        tex_tile(names).save(os.path.join(OUT, nm + '.png'), optimize=True)
    for nm, (src, box) in SCENES.items():
        if os.path.exists(src):
            scene_tile(src, box).save(os.path.join(OUT, nm + '.png'), optimize=True)
    pickups_tile().save(os.path.join(OUT, 'weapon_pickups.png'), optimize=True)
    for nm, src in TILES.items():
        big = nm in ('pumpkin_king', 'giggles', 'count', 'prime', 'seven')
        wide = nm.startswith('w_')
        size = 192 if big else 128 if not (nm in ('candy', 'bucket', 'brew', 'armor', 'bullets', 'shells', 'pumpkins', 'idol')
                                          or nm.startswith('key_')) else 72
        t = tile(src, size, wide)
        t = t.resize((t.width * 2, t.height * 2), Image.NEAREST) if size <= 72 else t
        t.save(os.path.join(OUT, nm + '.png'), optimize=True)
    print('ok', len(TILES))
