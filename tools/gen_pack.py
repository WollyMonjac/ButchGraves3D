#!/usr/bin/env python3
"""Build the asset pack res/d.bin (palette, trig tables, textures, sprites), HUD/title PNGs and src/Res.java."""
import os, json, struct, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textures as TX

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ROOT, 'res')
SRC = os.path.join(ROOT, 'src')
SPR = os.path.join(HERE, 'spr')
FONTS = '/home/claude/fonts'
NORMAL = 223          # palette indices 1..223 shaded
FB0 = 224             # 224..254 fullbright
NFB = 31

# ------------------------------------------------------------------ collect images (rgb float, glow mask, alpha)

images = []   # dict(name, kind, rgb(H,W,3) 0..1, alpha bool, glow bool, ox, oy, dither)


def add(name, kind, rgb, alpha, glow, ox=0, oy=0, dither=False):
    images.append(dict(name=name, kind=kind, rgb=np.clip(rgb, 0, 1), alpha=alpha, glow=glow & alpha, ox=ox, oy=oy, dither=dither))


WALL_NAMES = [n for n, f in TX.WALLS]
FLAT_NAMES = [n for n, f in TX.FLATS]
for n, f in TX.WALLS + TX.FLATS:
    c, g = f()
    add(n, 'tex', c, np.ones((64, 64), bool), np.zeros((64, 64), bool) if g is None else g)
for k in (0, 1):
    c, g = TX.sky(k)
    add('sky%d' % k, 'sky', c, np.ones(c.shape[:2], bool), np.zeros(c.shape[:2], bool), dither=True)

meta = json.load(open(os.path.join(SPR, 'meta.json')))
SPRITE_ORDER = []
for n in sorted(meta):
    im = np.array(Image.open(os.path.join(SPR, n + '.png')).convert('RGBA')).astype(float)
    a = im[..., 3]
    add(n, 'spr', im[..., :3] / 255, a > 0, (a > 0) & (a < 200), meta[n][0], meta[n][1])
    SPRITE_ORDER.append(n)

# ------------------------------------------------------------------ 2D effects


def fx_explosion(k, size=64):
    j, i = np.mgrid[0:size, 0:size]
    cx = cy = size / 2
    d = np.sqrt((i - cx) ** 2 + (j - cy) ** 2) / (size / 2)
    ang = np.arctan2(j - cy, i - cx)
    n = TX.pfbm(4, 3, 40 + k, size=size)
    r = [0.45, 0.75, 0.95, 1.0][k]
    edge = r * (0.75 + 0.35 * n + 0.08 * np.sin(ang * 7 + k))
    alpha = d < edge
    t = np.clip(d / np.maximum(edge, 1e-3), 0, 1)
    heat = (1 - t) * [1.0, 0.95, 0.7, 0.35][k] + n * 0.35
    c = np.zeros((size, size, 3))
    stops = [(0.0, (0.25, 0.05, 0.02)), (0.3, (0.75, 0.15, 0.02)), (0.55, (1.0, 0.5, 0.05)), (0.8, (1.0, 0.85, 0.3)), (1.0, (1.0, 1.0, 0.85))]
    for a0, a1 in zip(stops, stops[1:]):
        m = (heat >= a0[0]) & (heat < a1[0] + (a1[0] == 1.0))
        f = ((heat - a0[0]) / (a1[0] - a0[0]))[m][:, None]
        c[m] = np.array(a0[1]) * (1 - f) + np.array(a1[1]) * f
    c[heat >= 1.0] = (1.0, 1.0, 0.85)
    smoke = alpha & (heat < 0.18 + 0.1 * k)
    c[smoke] = np.array([0.18, 0.14, 0.12]) * (0.7 + 0.6 * n[smoke])[:, None]
    glow = alpha & ~smoke
    return c, alpha, glow


for k in range(4):
    c, a, g = fx_explosion(k)
    add('fx_boom%d' % (k + 1), 'spr', c, a, g, 32, 52)


def fx_blob(size, colr, seed, rough=0.35, glow=False, ring=False):
    j, i = np.mgrid[0:size, 0:size]
    cx = cy = (size - 1) / 2
    d = np.sqrt((i - cx) ** 2 + (j - cy) ** 2) / (size / 2)
    n = TX.pfbm(2, 2, seed, size=size)
    alpha = d < (0.75 + rough * (n - 0.5) * 2)
    if ring:
        alpha &= d > 0.35
    c = np.tile(np.array(colr), (size, size, 1)) * (0.7 + 0.5 * (1 - d))[..., None] * (0.8 + 0.4 * n)[..., None]
    return c, alpha, alpha if glow else np.zeros_like(alpha)


c, a, g = fx_blob(12, (0.6, 0.58, 0.55), 3); add('fx_puff1', 'spr', c, a, g, 6, 10)
c, a, g = fx_blob(16, (0.45, 0.43, 0.42), 4, ring=True); add('fx_puff2', 'spr', c, a, g, 8, 13)
c, a, g = fx_blob(10, (1.0, 0.85, 0.3), 5, 0.5, True); add('fx_spark', 'spr', c, a, g, 5, 8)
c, a, g = fx_blob(14, (0.55, 0.03, 0.02), 6, 0.6); add('fx_blood1', 'spr', c, a, g, 7, 12)
c, a, g = fx_blob(18, (0.45, 0.02, 0.02), 7, 0.7, ring=True); add('fx_blood2', 'spr', c, a, g, 9, 15)
c, a, g = fx_blob(14, (0.5, 1.0, 0.35), 8, 0.5, True); add('fx_green', 'spr', c, a, g, 7, 12)
c, a, g = fx_blob(16, (0.55, 0.95, 1.0), 9, 0.5, True); add('fx_ecto', 'spr', c, a, g, 8, 13)
for n in ('fx_boom1', 'fx_boom2', 'fx_boom3', 'fx_boom4', 'fx_puff1', 'fx_puff2', 'fx_spark', 'fx_blood1', 'fx_blood2', 'fx_green', 'fx_ecto'):
    SPRITE_ORDER.append(n)

# ------------------------------------------------------------------ palette


def build_palette():
    norm_px = []
    glow_px = []
    for im in images:
        a, g = im['alpha'], im['glow']
        px = im['rgb'][a & ~g]
        w = 1 if im['kind'] != 'sky' else 1
        if im['kind'] == 'spr':
            px = np.repeat(px, 3, axis=0)    # favour sprite colours (monsters must look good)
        norm_px.append(px)
        glow_px.append(im['rgb'][g])
    norm_px = np.concatenate(norm_px)
    glow_px = np.concatenate(glow_px)

    def quant(px, n):
        px8 = (np.clip(px, 0, 1) * 255).astype(np.uint8)
        rs = np.random.RandomState(0)
        if len(px8) > 400000:
            px8 = px8[rs.choice(len(px8), 400000, replace=False)]
        w = int(math.ceil(math.sqrt(len(px8))))
        buf = np.zeros((w * w, 3), np.uint8)
        buf[:len(px8)] = px8
        buf[len(px8):] = px8[:w * w - len(px8)] if len(px8) >= w * w - len(px8) else px8[0]
        img = Image.fromarray(buf.reshape(w, w, 3), 'RGB')
        q = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT, kmeans=4, dither=Image.Dither.NONE)
        pal = np.array(q.getpalette()[:n * 3]).reshape(-1, 3)
        return pal
    p1 = quant(norm_px, NORMAL)
    p2 = quant(glow_px, NFB)
    pal = np.zeros((256, 3), int)
    pal[1:1 + len(p1)] = p1
    pal[FB0:FB0 + len(p2)] = p2
    return pal, len(p1), len(p2)


PAL, n1, n2 = build_palette()
print('palette', n1, n2)
PALF = PAL.astype(float) / 255


def nearest(px, lo, hi):
    """Map rgb pixels (N,3, 0..1) to palette indices in [lo, hi)."""
    p = PALF[lo:hi]
    out = np.zeros(len(px), np.int32)
    for s in range(0, len(px), 20000):
        blk = px[s:s + 20000]
        # perceptual-ish weights
        d = (((blk[:, None, :] - p[None, :, :]) * np.array([0.9, 1.2, 0.7])) ** 2).sum(-1)
        out[s:s + 20000] = d.argmin(1) + lo
    return out


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


def index_image(im):
    H, W = im['alpha'].shape
    rgb = im['rgb'].copy()
    if im['dither']:
        b = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
        rgb = np.clip(rgb + b[..., None] * 0.035, 0, 1)
    idx = np.zeros((H, W), np.int32)
    a, g = im['alpha'], im['glow']
    n = a & ~g
    if n.any():
        idx[n] = nearest(rgb[n], 1, 1 + n1)
    if g.any():
        idx[g] = nearest(rgb[g], FB0, FB0 + n2)
    return idx


# ------------------------------------------------------------------ trig tables

ANG = 4096
SIN_Q = [int(round(math.sin(i * 2 * math.pi / ANG) * 65536)) for i in range(ANG // 4 + 1)]
ATAN = [int(round(math.atan(i / 1024.0) * ANG / (2 * math.pi))) for i in range(1025)]

# ------------------------------------------------------------------ write d.bin

tex_imgs = [im for im in images if im['kind'] in ('tex', 'sky')]
spr_imgs = {im['name']: im for im in images if im['kind'] == 'spr'}


def write():
    out = bytearray()
    out += b'BG3D'
    out += struct.pack('>h', 1)
    for c in PAL:
        out += bytes([int(c[0]), int(c[1]), int(c[2])])
    out += struct.pack('>h', len(SIN_Q))
    for v in SIN_Q:
        out += struct.pack('>i', v)
    out += struct.pack('>h', len(ATAN))
    for v in ATAN:
        out += struct.pack('>h', v)
    out += struct.pack('>h', len(tex_imgs))
    for im in tex_imgs:
        idx = index_image(im)
        H, W = idx.shape
        out += struct.pack('>hh', W, H)
        out += idx.T.astype(np.uint8).tobytes()      # column-major
    out += struct.pack('>h', len(SPRITE_ORDER))
    for n in SPRITE_ORDER:
        im = spr_imgs[n]
        idx = index_image(im)
        H, W = idx.shape
        out += struct.pack('>hhhh', W, H, im['ox'], im['oy'])
        out += idx.T.astype(np.uint8).tobytes()
    with open(os.path.join(RES, 'd.bin'), 'wb') as f:
        f.write(out)
    print('d.bin', len(out))


def java_name(n):
    return n.upper().replace('-', '_')


def write_res_java():
    L = ['// Generated by tools/gen_pack.py - do not edit.', 'final class Res {']
    L.append('  static final int FB0 = %d;' % FB0)
    for k, im in enumerate(tex_imgs):
        L.append('  static final int T_%s = %d;' % (java_name(im['name']), k))
    L.append('  static final int NTEX = %d;' % len(tex_imgs))
    for k, n in enumerate(SPRITE_ORDER):
        L.append('  static final int S_%s = %d;' % (java_name(n), k))
    L.append('  static final int NSPR = %d;' % len(SPRITE_ORDER))
    L.append('}')
    with open(os.path.join(SRC, 'Res.java'), 'w') as f:
        f.write('\n'.join(L) + '\n')


# ------------------------------------------------------------------ HUD + title PNGs

def hud_digits(height, name):
    ft = ImageFont.truetype(FONTS + '/fontsource-black-ops-one-5.3.0/package/files/black-ops-one-latin-400-normal.woff', int(height * 1.25))
    chars = '0123456789%/'
    cells = []
    for ch in chars:
        bb = ft.getbbox(ch)
        w = bb[2] - bb[0] + 4
        h = height + 4
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).text((2 - bb[0], 2 - bb[1] + (height - (bb[3] - bb[1]))), ch, font=ft, fill=255)
        cells.append(np.array(m) > 110)
    cw = max(c.shape[1] for c in cells)
    H = cells[0].shape[0]
    atlas = np.zeros((H, cw * len(cells), 4), np.uint8)
    for k, m in enumerate(cells):
        h, w = m.shape
        yy = np.linspace(0, 1, h)[:, None]
        col = np.zeros((h, w, 3))
        col[..., 0] = 255
        col[..., 1] = (230 - 150 * yy) * np.ones((1, w))
        col[..., 2] = (90 - 80 * yy) * np.ones((1, w))
        o = np.zeros_like(m)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                o |= np.roll(np.roll(m, dy, 0), dx, 1)
        o &= ~m
        x0 = k * cw + (cw - w) // 2
        blk = atlas[:, x0:x0 + w]
        blk[o] = (30, 6, 2, 255)
        blk[m, :3] = col[m].astype(np.uint8)
        blk[m, 3] = 255
    Image.fromarray(atlas, 'RGBA').save(os.path.join(RES, name))
    return cw, H


def hud_icons():
    """Small ARGB icons (16px): health, armor, bullets, shells, pumpkins, keys x3, plus 12px versions via scaling in Java."""
    icons = []
    def sprite_icon(n, size=16):
        im = Image.open(os.path.join(SPR, n + '.png')).convert('RGBA')
        a = np.array(im)
        a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
        im = Image.fromarray(a, 'RGBA')
        im.thumbnail((size, size), Image.LANCZOS)
        a = np.array(im)
        a[..., 3] = np.where(a[..., 3] > 100, 255, 0)
        out = np.zeros((size, size, 4), np.uint8)
        y0 = (size - a.shape[0]) // 2; x0 = (size - a.shape[1]) // 2
        out[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
        m = out[..., 3] > 0
        o = np.zeros_like(m)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                o |= np.roll(np.roll(m, dy, 0), dx, 1)
        o &= ~m
        out[o] = (10, 4, 2, 255)
        return out
    names = ['bucket', 'armor', 'bullets', 'shells', 'pumpkins', 'key_red', 'key_blue', 'key_gold', 'jack']
    row = np.concatenate([sprite_icon(n) for n in names], axis=1)
    Image.fromarray(row, 'RGBA').save(os.path.join(RES, 'icons.png'))
    # midlet icon
    ic = sprite_icon('jack', 32)
    Image.fromarray(ic, 'RGBA').save(os.path.join(RES, 'icon.png'))
    Image.fromarray(sprite_icon('jack', 16), 'RGBA').save(os.path.join(RES, 'icon16.png'))


def logo(width, name):
    """BUTCH GRAVES 3D logo: dripping bloody Nosifer title + Creepster subtitle."""
    S = 4
    W = width * S
    ft1 = ImageFont.truetype(FONTS + '/fontsource-nosifer-5.3.0/package/files/nosifer-latin-400-normal.woff', 22 * S)
    ft2 = ImageFont.truetype(FONTS + '/fontsource-creepster-5.3.0/package/files/creepster-latin-400-normal.woff', 30 * S)
    def text_mask(txt, ft, w):
        bb = ft.getbbox(txt)
        m = Image.new('L', (bb[2] - bb[0] + 8 * S, bb[3] - bb[1] + 8 * S), 0)
        ImageDraw.Draw(m).text((4 * S - bb[0], 4 * S - bb[1]), txt, font=ft, fill=255)
        r = w / m.width
        if r < 1:
            m = m.resize((w, int(m.height * r)), Image.LANCZOS)
        return m
    m1 = text_mask('BUTCH GRAVES', ft2, W)
    m2 = text_mask('3D', ft1, int(W * 0.42))
    H = m1.height + m2.height + 4 * S
    canvas = Image.new('L', (W, H), 0)
    canvas.paste(m1, ((W - m1.width) // 2, 0))
    canvas.paste(m2, ((W - m2.width) // 2, m1.height - 2 * S))
    small = canvas.resize((width, H // S), Image.LANCZOS)
    m = np.array(small) > 100
    h, w = m.shape
    yy = np.linspace(0, 1, h)[:, None]
    col = np.zeros((h, w, 3))
    top = m.copy(); top[m1.height // S:] = False
    col[..., 0] = 255 - 60 * yy
    col[..., 1] = np.where(top, 140 - 110 * yy, 30 + 20 * yy)
    col[..., 2] = np.where(top, 10, 10)
    # "3D" in blood red
    bot = m & ~top
    col[bot] = np.array([200, 10, 10]) * (1.1 - 0.5 * yy[np.nonzero(bot)[0]])
    out = np.zeros((h, w, 4), np.uint8)
    o = np.zeros_like(m)
    for dy in (-1, 0, 1, 2):
        for dx in (-1, 0, 1):
            o |= np.roll(np.roll(m, dy, 0), dx, 1)
    o &= ~m
    out[o] = (0, 0, 0, 255)
    out[m, :3] = np.clip(col[m], 0, 255).astype(np.uint8)
    out[m, 3] = 255
    Image.fromarray(out, 'RGBA').save(os.path.join(RES, name))


def title_bg():
    """160x120 title background: moonlit graveyard, painted procedurally."""
    W, H = 160, 200
    c, g = TX.sky(0, W=512, H=120)
    img = Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)).crop((40, 0, 200, 120))
    bg = Image.new('RGB', (W, H), (6, 3, 10))
    bg.paste(img, (0, 0))
    d = ImageDraw.Draw(bg)
    rs = np.random.RandomState(3)
    # ground and graves
    d.rectangle((0, 112, W, H), fill=(8, 6, 10))
    for k in range(9):
        x = rs.randint(0, W); y = rs.randint(112, 150); s = rs.randint(6, 12)
        d.rectangle((x - s // 2, y - s, x + s // 2, y), fill=(14, 12, 18))
        d.ellipse((x - s // 2, y - s - s // 2, x + s // 2, y - s + s // 2), fill=(14, 12, 18))
    # glowing pumpkins
    for (x, y) in ((22, 150), (138, 156), (110, 140)):
        d.ellipse((x - 7, y - 6, x + 7, y + 6), fill=(200, 80, 10))
        d.polygon([(x - 4, y - 2), (x - 2, y - 4), (x - 1, y - 1)], fill=(255, 220, 80))
        d.polygon([(x + 4, y - 2), (x + 2, y - 4), (x + 1, y - 1)], fill=(255, 220, 80))
        d.line((x - 4, y + 2, x + 4, y + 2), fill=(255, 220, 80), width=2)
    bust = Image.open(os.path.join(SPR, 'hero_bust.png')).convert('RGBA')
    bgr = bg.convert('RGBA')
    bgr.alpha_composite(bust, ((W - bust.width) // 2, H - bust.height))
    bgr.convert('RGB').save(os.path.join(RES, 'title.png'))
    for nm in ('face0', 'face1', 'face2', 'facegrin', 'facedead'):
        for sz in (24, 36):
            Image.open(os.path.join(SPR, 'hero_%s_%d.png' % (nm, sz))).save(os.path.join(RES, '%s_%d.png' % (nm, sz)))


if __name__ == '__main__':
    write()
    write_res_java()
    print('hud digits', hud_digits(10, 'dig10.png'), hud_digits(16, 'dig16.png'))
    hud_icons()
    logo(120, 'logo120.png'); logo(176, 'logo176.png'); logo(230, 'logo230.png')
    title_bg()
    json.dump({'walls': WALL_NAMES, 'flats': FLAT_NAMES, 'pal': PAL.tolist()}, open(os.path.join(HERE, 'pack_info.json'), 'w'))
    # preview of the quantized sprites/textures
    prev = []
    for n in ('zombie_walk1', 'scarecrow_attack', 'boss_walk1', 'witch_attack', 'wraith_walk1', 'fx_boom2', 'jack'):
        idx = index_image(spr_imgs[n])
        rgb = PAL[idx].astype(np.uint8)
        a = (idx > 0)
        im = np.zeros(idx.shape + (4,), np.uint8); im[..., :3] = rgb; im[..., 3] = a * 255
        prev.append(Image.fromarray(im, 'RGBA'))
    Wt = sum(p.width + 4 for p in prev); Ht = max(p.height for p in prev)
    sh = Image.new('RGBA', (Wt, Ht), (30, 20, 40, 255)); x = 0
    for p in prev:
        sh.alpha_composite(p, (x, Ht - p.height)); x += p.width + 4
    sh.resize((Wt * 2, Ht * 2), Image.NEAREST).save(os.path.join(HERE, 'out', 'quant_prev.png'))
