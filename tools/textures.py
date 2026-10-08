"""Procedural 64x64 tileable textures and skies. Each returns (rgb float HxWx3, glow bool HxW)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

S = 64
FONTS = '/home/claude/fonts'


def _h(ix, iy, seed):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + seed * 2246822519) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def pnoise(cells, seed, size=S, sx=None, sy=None):
    """Periodic value noise over a size x size tile with `cells` cells per side."""
    cx = cells if sx is None else sx
    cy = cells if sy is None else sy
    j, i = np.mgrid[0:size, 0:size]
    x = i / size * cx
    y = j / size * cy
    ix = np.floor(x).astype(np.int64); iy = np.floor(y).astype(np.int64)
    fx = x - ix; fy = y - iy
    ux = fx * fx * (3 - 2 * fx); uy = fy * fy * (3 - 2 * fy)
    a = _h(ix % cx, iy % cy, seed); b = _h((ix + 1) % cx, iy % cy, seed)
    c = _h(ix % cx, (iy + 1) % cy, seed); d = _h((ix + 1) % cx, (iy + 1) % cy, seed)
    return (a * (1 - ux) + b * ux) * (1 - uy) + (c * (1 - ux) + d * ux) * uy


def pfbm(base, oct, seed, size=S, sx=None, sy=None):
    t = 0; amp = 1; nrm = 0
    for o in range(oct):
        t = t + pnoise(base * 2 ** o, seed + o * 31, size, None if sx is None else sx * 2 ** o, None if sy is None else sy * 2 ** o) * amp
        nrm += amp; amp *= 0.5
    return t / nrm


def shade(h, strength=2.5, ld=(-0.6, -0.7, 0.55)):
    """Lambert shading from a periodic height map (light from top-left)."""
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * strength
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * strength
    n = np.stack([-gx, -gy, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    l = np.array(ld, float); l /= np.linalg.norm(l)
    return np.clip(n @ l, 0, 1) / l[2]


def col(hexs):
    hexs = hexs.lstrip('#')
    return np.array([int(hexs[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def blocks(bh, bw, offset, mortar=1, seed=0, jitter=0, size=S):
    """Running-bond blocks. Returns id map, local u, v (0..1), mortar mask, edge distance."""
    j, i = np.mgrid[0:size, 0:size]
    row = j // bh
    off = (row % 2) * offset
    x = (i + off) % size
    colid = x // bw
    bid = row * 100 + colid
    u = (x % bw) / bw
    v = (j % bh) / bh
    ed = np.minimum(np.minimum(x % bw, bw - 1 - x % bw), np.minimum(j % bh, bh - 1 - j % bh))
    mort = ed < mortar
    return bid, u, v, mort, ed


def grime(rgb, seed, amount=0.5):
    """Vertical streaks + dark noise."""
    s = pnoise(8, seed, sx=16, sy=2)
    n = pfbm(4, 3, seed + 3)
    f = 1 - amount * 0.5 * np.clip((s - 0.5) * 2, 0, 1) - amount * 0.4 * np.clip(0.45 - n, 0, 1) * 2
    return rgb * f[..., None]


def blood_splat(rgb, seed, cx, cy, r, glow=None):
    rs = np.random.RandomState(seed)
    j, i = np.mgrid[0:S, 0:S]
    m = np.zeros((S, S), bool)
    for k in range(9):
        a = rs.uniform(0, 6.28); d = rs.uniform(0, r)
        x, y, rr = cx + np.cos(a) * d, cy + np.sin(a) * d, rs.uniform(1.0, r * 0.45)
        m |= ((i - x) ** 2 + (j - y) ** 2) < rr * rr
    for k in range(5):
        x = cx + rs.uniform(-r * 0.8, r * 0.8)
        ln = rs.uniform(r, r * 3)
        m |= (np.abs(i - x) < 0.8) & (j > cy) & (j < cy + ln)
    c = col('#5a0806') * (0.8 + 0.4 * pnoise(16, seed)[..., None])
    rgb[m] = c[m]
    return rgb

# ------------------------------------------------------------------ walls


def t_brick(seed=1, base='#6e2c22'):
    bid, u, v, mort, ed = blocks(8, 16, 8, 1)
    rnd = _h(bid, bid * 7, seed)
    h = np.where(mort, 0.0, 0.6 + 0.4 * np.clip(ed / 2.0, 0, 1)) + pfbm(8, 2, seed) * 0.25
    c = col(base)[None, None, :] * (0.65 + 0.55 * rnd)[..., None]
    c = c * (0.8 + 0.4 * pfbm(16, 2, seed + 4))[..., None]
    c = np.where(mort[..., None], col('#3a3632')[None, None, :] * (0.7 + 0.5 * pnoise(32, seed + 5))[..., None], c)
    moss = np.clip((pfbm(4, 3, seed + 9) - 0.55) * 4, 0, 1)
    c = c * (1 - moss[..., None] * 0.6) + col('#2c4a1a') * moss[..., None] * 0.6
    c = grime(c, seed + 2, 0.6)
    return c * (0.55 + 0.6 * shade(h))[..., None], None


def t_stone(seed=2, base='#6c6a66'):
    bid, u, v, mort, ed = blocks(16, 32, 16, 1, seed)
    rnd = _h(bid, bid * 3, seed)
    n = pfbm(8, 3, seed)
    h = np.where(mort, 0.0, 0.5 + 0.5 * np.clip(ed / 3.0, 0, 1)) + n * 0.5
    c = col(base)[None, None, :] * (0.7 + 0.4 * rnd)[..., None] * (0.7 + 0.5 * n)[..., None]
    c = np.where(mort[..., None], col('#252320')[None, None, :], c)
    # cracks
    cr = np.abs(pfbm(6, 3, seed + 7) - 0.5) < 0.012
    c[cr] *= 0.4
    moss = np.clip((pfbm(3, 3, seed + 11) - 0.58) * 5, 0, 1)
    c = c * (1 - moss[..., None] * 0.7) + col('#33501e') * moss[..., None] * 0.7
    c = grime(c, seed, 0.5)
    return c * (0.5 + 0.65 * shade(h, 3.0))[..., None], None


def t_wood(seed=3, base='#4a2e1a', planks=6):
    j, i = np.mgrid[0:S, 0:S]
    pw = S // planks
    pid = i // pw
    rnd = _h(pid, pid * 5, seed)
    grain = pnoise(4, seed, sx=4, sy=1) * 0.3 + np.sin((i % pw) * 0.9 + pfbm(4, 2, seed + pid[0, 0]) * 9) * 0.08
    knots = np.zeros((S, S))
    rs = np.random.RandomState(seed)
    for k in range(3):
        x, y = rs.randint(0, S), rs.randint(0, S)
        d = np.sqrt(((i - x + 32) % 64 - 32) ** 2 + (((j - y + 32) % 64 - 32) * 0.4) ** 2)
        knots += np.exp(-d * d / 6) * 0.5
    edge = (i % pw == 0) | (i % pw == pw - 1)
    h = np.where(edge, 0.0, 0.7) + grain + pnoise(16, seed + 2) * 0.15
    c = col(base)[None, None, :] * (0.7 + 0.5 * rnd)[..., None] * (0.8 + grain * 1.2 - knots)[..., None]
    c[edge] *= 0.35
    # nails
    for y in (6, 58):
        nail = ((i % pw - pw // 2) ** 2 + (j - y) ** 2) < 2.2
        c[nail] = col('#7a7670')
    c = grime(c, seed + 1, 0.4)
    return c * (0.6 + 0.5 * shade(h, 2.0))[..., None], None


def t_wallpaper(seed=4):
    j, i = np.mgrid[0:S, 0:S]
    base = col('#4a1f4c')
    # damask motif: mirrored flourishes from a function of local coords
    x = (i % 32) - 16; y = (j % 32) - 16
    ax = np.abs(x)
    m1 = (((ax - 6) ** 2) / 20 + ((y + 2) ** 2) / 60) < 1
    m2 = ((ax ** 2) / 8 + ((y - 7) ** 2) / 10) < 1
    m3 = (np.abs(ax - 9 + y * 0.4) < 1.2) & (np.abs(y) < 9)
    m4 = ((ax ** 2) / 3 + ((y + 11) ** 2) / 6) < 1
    mot = m1 | m2 | m3 | m4
    c = np.tile(base, (S, S, 1)) * (0.8 + 0.3 * pfbm(8, 2, seed))[..., None]
    c[mot] = col('#7a3a6e') * (0.85 + 0.25 * pnoise(16, seed + 1)[mot])[:, None]
    # vertical pinstripes between motifs
    c[(i % 32) == 0] *= 0.7
    # wainscot (lower 22 px dark wood panel) with rail
    wy = j >= 42
    wd, _ = t_wood(seed + 9, '#3a2010', planks=4)
    c[wy] = wd[wy] * 0.9
    rail = (j >= 40) & (j < 43)
    c[rail] = col('#5e3a1c') * (1.2 - (j[rail] - 40) * 0.2)[:, None]
    # water stains / mold
    stain = np.clip((pfbm(3, 3, seed + 5) - 0.55) * 3, 0, 1)
    c = c * (1 - stain[..., None] * 0.5) + col('#3c3420') * stain[..., None] * 0.4
    c = grime(c, seed, 0.35)
    if seed % 2 == 0:
        c = blood_splat(c, seed + 20, 40, 18, 6)
    return c, None


def t_bookshelf(seed=5):
    j, i = np.mgrid[0:S, 0:S]
    rs = np.random.RandomState(seed)
    c = np.zeros((S, S, 3))
    glow = None
    shelf_h = 16
    shelf = (j % shelf_h) >= shelf_h - 3
    wd, _ = t_wood(seed + 3, '#4a2a14', planks=2)
    c[:] = col('#120a06')
    x = 0
    palette = ['#5a1414', '#1c3a1c', '#1a2448', '#4a3a14', '#3a1a3a', '#2a2a2a', '#5a3018', '#16302e']
    for row in range(4):
        x = 0
        while x < S:
            w = rs.randint(2, 5)
            hgt = rs.randint(8, 13)
            cc = col(palette[rs.randint(len(palette))]) * rs.uniform(0.7, 1.3)
            y1 = row * shelf_h + shelf_h - 3
            y0 = y1 - hgt
            if rs.rand() < 0.12:
                x += w
                continue
            for xx in range(x, min(S, x + w)):
                sh = 0.7 + 0.5 * np.sin((xx - x + 0.5) / w * np.pi)
                c[y0:y1, xx] = cc * sh
                c[y0 + 2:y0 + 3, xx] = col('#c8a040') * sh * 0.8
                c[y1 - 3:y1 - 2, xx] = col('#c8a040') * sh * 0.8
            x += w
    c[shelf] = wd[shelf] * 1.1
    c[(j % shelf_h) == shelf_h - 3] *= 1.4
    # side posts
    post = (i < 3) | (i >= 61)
    c[post] = wd[post]
    # cobweb corner
    web = ((i - 3) ** 2 + (j - 0) ** 2 < 120) & ((np.abs(np.arctan2(j, i - 3) * 6 % 1 - 0.5) < 0.06) | (np.sqrt((i - 3) ** 2 + j ** 2) % 4 < 0.6))
    c[web] = c[web] * 0.4 + 0.5
    return c, glow


def t_portrait(seed=6):
    c, _ = t_wallpaper(seed + 1)
    j, i = np.mgrid[0:S, 0:S]
    glow = np.zeros((S, S), bool)
    # gold frame 12..52 x 6..54
    x0, x1, y0, y1 = 12, 52, 5, 40
    fr = (i >= x0) & (i < x1) & (j >= y0) & (j < y1)
    inner = (i >= x0 + 4) & (i < x1 - 4) & (j >= y0 + 4) & (j < y1 - 4)
    gold = col('#b08a30') * (0.7 + 0.6 * pnoise(16, seed)[..., None])
    c[fr] = gold[fr]
    bev = fr & ~inner & (((i - x0) < 2) | ((j - y0) < 2))
    c[bev] *= 1.35
    # painting: dark background, pale ghostly face with glowing eyes
    cx, cy = 32, 22
    pc = np.tile(col('#1a1410'), (S, S, 1)) * (0.7 + 0.6 * pfbm(8, 2, seed + 3))[..., None]
    face = ((i - cx) ** 2 / 64 + (j - cy) ** 2 / 110) < 1
    pc[face] = col('#b8b0a0') * (0.6 + 0.35 * (1 - (i[face] - cx + 4) ** 2 / 90))[:, None]
    hair = ((i - cx) ** 2 / 110 + (j - cy + 3) ** 2 / 120) < 1
    pc[hair & ~face] = col('#2a1a10')
    body = (j > cy + 9) & (np.abs(i - cx) < (j - cy - 4) * 1.2)
    pc[body] = col('#2a1020') * 1.2
    for s in (-1, 1):
        sock = ((i - cx - s * 3.5) ** 2 + (j - cy + 1) ** 2) < 5
        pc[sock] = col('#100808')
        ey = ((i - cx - s * 3.5) ** 2 + (j - cy + 1) ** 2) < 1.6
        pc[ey] = col('#ff3020')
        glow |= inner & ey
    mouth = (np.abs(i - cx) < 2.5) & (np.abs(j - cy - 6) < 1)
    pc[mouth] = col('#300808')
    c[inner] = pc[inner]
    # blood drips from the frame
    c = blood_splat(c, seed + 3, 40, 40, 3)
    return c, glow


def t_skullwall(seed=7):
    j, i = np.mgrid[0:S, 0:S]
    n = pfbm(6, 3, seed)
    c = np.tile(col('#3a3024'), (S, S, 1)) * (0.6 + 0.6 * n)[..., None]
    h = n * 0.4
    rs = np.random.RandomState(seed)
    # skulls on a staggered grid (tileable 4x4 of 16px cells)
    for gy in range(4):
        for gx in range(4):
            cx = gx * 16 + 8 + (gy % 2) * 8 + rs.uniform(-1, 1)
            cy = gy * 16 + 8 + rs.uniform(-1, 1)
            dx = ((i - cx + 32) % 64) - 32
            dy = ((j - cy + 32) % 64) - 32
            sk = (dx ** 2 / 30 + (dy + 1) ** 2 / 28) < 1
            jaw = (dx ** 2 / 12 + (dy - 5) ** 2 / 6) < 1
            m = sk | jaw
            hh = np.clip(1 - (dx ** 2 / 30 + (dy + 1) ** 2 / 28), 0, 1) ** 0.5
            h = np.where(m, 0.6 + 0.6 * hh, h)
            bone = col('#cfc4a4') * rs.uniform(0.75, 1.05)
            c[m] = bone * (0.7 + 0.4 * pnoise(32, seed + gx)[m])[:, None]
            for s in (-1, 1):
                e = ((dx - s * 2.3) ** 2 + (dy + 0.5) ** 2) < 3.2
                c[e] = col('#100a06'); h = np.where(e, 0.2, h)
            nose = (np.abs(dx) < 0.9) & (dy > 2) & (dy < 3.6)
            c[nose] = col('#100a06')
            teeth = (np.abs(dy - 5) < 0.6) & (np.abs(dx) < 3) & ((np.floor(dx + 10) % 2) == 0)
            c[teeth] = col('#2a2010')
    c = grime(c, seed, 0.5)
    return c * (0.5 + 0.6 * shade(h, 3.0))[..., None], None


def t_hedge(seed=8):
    n1 = pfbm(8, 3, seed)
    n2 = pnoise(32, seed + 4)
    h = n1 * 0.6 + n2 * 0.5
    c = col('#1e3a16') * (0.5 + 0.9 * n1)[..., None]
    c = np.where((n2 > 0.7)[..., None], col('#3c6a26') * (0.8 + 0.4 * n1)[..., None], c)
    c = np.where((n2 < 0.25)[..., None], col('#0c1a08')[None, None, :], c)
    # some dead brown patches
    dead = np.clip((pfbm(3, 2, seed + 9) - 0.62) * 5, 0, 1)
    c = c * (1 - dead[..., None]) + col('#4a3a1a') * (0.6 + 0.6 * n2)[..., None] * dead[..., None]
    return c * (0.55 + 0.6 * shade(h, 3.0))[..., None], None


def t_pumpkinwall(seed=9):
    j, i = np.mgrid[0:S, 0:S]
    c = np.tile(col('#1a0e06'), (S, S, 1))
    h = np.zeros((S, S))
    glow = np.zeros((S, S), bool)
    rs = np.random.RandomState(seed)
    for gy in range(3):
        for gx in range(3):
            cx = gx * 21.33 + 10.6 + (gy % 2) * 10.6
            cy = gy * 21.33 + 11
            dx = ((i - cx + 32) % 64) - 32
            dy = ((j - cy + 32) % 64) - 32
            r = 10.5
            m = (dx ** 2 + (dy * 1.15) ** 2) < r * r
            ang = np.arctan2(dy, dx)
            rib = 0.7 + 0.3 * np.abs(np.cos(ang * 4 + 0.0 * dx))
            hh = np.clip(1 - (dx ** 2 + (dy * 1.15) ** 2) / (r * r), 0, 1) ** 0.5
            h = np.where(m, hh, h)
            pc = col('#c85a0a') * (0.55 + 0.5 * hh * rib)[..., None] * rs.uniform(0.8, 1.1)
            c[m] = pc[m]
            ribline = m & (np.abs(np.sin(dx / (1 + hh * 3) * 1.6)) < 0.18)
            c[ribline] *= 0.6
            lit = rs.rand() < 0.7
            face = np.zeros((S, S), bool)
            for s in (-1, 1):
                face |= (np.abs(dx - s * 4) < (2.2 - (dy + 2) * 0.55)) & (dy < -0.5) & (dy > -4.5)
            face |= (np.abs(dx) < 6) & (dy > 2) & (dy < 4.5 + 1.5 * np.cos(dx * 1.6)) & (dy > 2 + 0.06 * dx ** 2)
            face &= m
            if lit:
                c[face] = col('#ffd040') * (0.85 + 0.3 * rs.uniform())
                glow |= face
            else:
                c[face] = col('#200a02')
            stem = (np.abs(dx) < 1.2) & (dy < -r + 1.5) & (dy > -r - 1.5)
            c[stem] = col('#3a3010')
    return c * (0.6 + 0.5 * shade(h, 4.0))[..., None], glow


def t_door(seed=10, emblem=None):
    j, i = np.mgrid[0:S, 0:S]
    c, _ = t_wood(seed, '#3a2412', planks=5)
    glow = np.zeros((S, S), bool)
    # iron bands
    for y in (8, 54):
        band = (j >= y) & (j < y + 5)
        c[band] = col('#2a2a2c') * (0.8 + 0.4 * pnoise(32, seed + y)[band])[:, None]
        c[band & (j == y)] *= 1.6
        for x in range(4, 64, 12):
            rv = ((i - x) ** 2 + (j - y - 2) ** 2) < 2.5
            c[rv] = col('#8a8680')
    # frame border
    edge = (i < 3) | (i > 60)
    c[edge] *= 0.45
    if emblem is None:
        # iron ring knocker
        ring = np.abs(np.sqrt((i - 32) ** 2 + (j - 34) ** 2) - 5) < 1.1
        c[ring] = col('#6a6660')
        boss = ((i - 32) ** 2 + (j - 28) ** 2) < 6
        c[boss] = col('#4a4640')
    else:
        ec = col(emblem)
        # skull emblem plate
        plate = ((i - 32) ** 2 / 110 + (j - 31) ** 2 / 130) < 1
        c[plate] = col('#2a2622') * 1.2
        sk = ((i - 32) ** 2 / 36 + (j - 29) ** 2 / 40) < 1
        jaw = ((i - 32) ** 2 / 14 + (j - 36) ** 2 / 8) < 1
        c[sk | jaw] = col('#d8ccaa')
        for s in (-1, 1):
            e = ((i - 32 - s * 2.6) ** 2 + (j - 29) ** 2) < 3.6
            c[e] = ec
            glow |= e
        rim = (np.abs(np.sqrt((i - 32) ** 2 / 110 + (j - 31) ** 2 / 130) - 1) < 0.1)
        c[rim] = ec * 0.9
        glow |= rim
    return c, glow


def t_doorframe(seed=12):
    c, _ = t_stone(seed, '#58524a')
    j, i = np.mgrid[0:S, 0:S]
    c[(i % 16) < 2] *= 0.5
    return c, None


def t_exit(seed=13):
    c, _ = t_stone(seed, '#5a5650')
    j, i = np.mgrid[0:S, 0:S]
    glow = np.zeros((S, S), bool)
    # EXIT sign box
    box = (i >= 8) & (i < 56) & (j >= 6) & (j < 22)
    c[box] = col('#140404')
    img = Image.new('L', (48, 16), 0)
    d = ImageDraw.Draw(img)
    ft = ImageFont.truetype(FONTS + '/fontsource-black-ops-one-5.3.0/package/files/black-ops-one-latin-400-normal.woff', 13)
    bb = d.textbbox((0, 0), 'EXIT', font=ft)
    d.text(((48 - (bb[2] - bb[0])) // 2 - bb[0], (16 - (bb[3] - bb[1])) // 2 - bb[1]), 'EXIT', font=ft, fill=255)
    t = np.array(img) > 110
    sub = np.zeros((S, S), bool)
    sub[6:22, 8:56] = t
    c[sub] = col('#ff2a14')
    glow |= sub
    # lever plate with jack-o-lantern button
    plate = (i >= 20) & (i < 44) & (j >= 28) & (j < 58)
    c[plate] = col('#3a3a3e') * (0.8 + 0.3 * pnoise(16, 3)[plate])[:, None]
    c[plate & ((i == 20) | (j == 28))] *= 1.5
    pk = ((i - 32) ** 2 + ((j - 43) * 1.15) ** 2) < 64
    c[pk] = col('#d86010') * (0.7 + 0.4 * (1 - ((i[pk] - 30) ** 2 + (j[pk] - 40) ** 2) / 90))[:, None]
    face = pk & (((np.abs(i - 29) < 2) | (np.abs(i - 35) < 2)) & (np.abs(j - 41) < 1.5) | ((np.abs(i - 32) < 4.5) & (np.abs(j - 46.5) < 1)))
    c[face] = col('#ffe060')
    glow |= face
    return c, glow


def t_window(seed=14):
    c, _ = t_stone(seed, '#4e4a46')
    j, i = np.mgrid[0:S, 0:S]
    glow = np.zeros((S, S), bool)
    # gothic arch window 16..48 x 8..60
    cx = 32
    arch = ((np.abs(i - cx) < 15) & (j > 22) & (j < 58)) | (((i - cx) ** 2 + (j - 22) ** 2) < 225)
    arch &= j > 6
    inner = ((np.abs(i - cx) < 12) & (j > 22) & (j < 55)) | (((i - cx) ** 2 + (j - 22) ** 2) < 144)
    c[arch] = col('#2a2622')
    # stained glass: lead lines + colored cells
    rs = np.random.RandomState(seed)
    cells = (np.floor((i - cx + 12) / 6) + np.floor((j - 8) / 7) * 5 + np.floor((i + j) / 9) * 3).astype(int)
    pal = ['#c02018', '#2040c0', '#d0a020', '#20a040', '#8030b0', '#e06010']
    gc = np.zeros((S, S, 3))
    for k in np.unique(cells[inner]):
        m = inner & (cells == k)
        gc[m] = col(pal[rs.randint(len(pal))]) * rs.uniform(0.7, 1.0)
    # moon showing through (pale circle)
    moon = ((i - 37) ** 2 + (j - 18) ** 2) < 30
    gc[moon & inner] = col('#f0e8c0')
    lead = inner & ((np.abs((i - cx + 12) % 6) < 0.8) | (np.abs((j - 8) % 7) < 0.8) | (np.abs((i + j) % 9) < 0.7))
    c[inner] = gc[inner]
    c[lead] = col('#101010')
    glow |= inner & ~lead
    return c, glow


def t_crypt(seed=15):
    """Stone with carved cross relief (mausoleum)."""
    c, _ = t_stone(seed, '#605c58')
    j, i = np.mgrid[0:S, 0:S]
    cross = ((np.abs(i - 32) < 4) & (j > 10) & (j < 56)) | ((np.abs(j - 24) < 4) & (np.abs(i - 32) < 16))
    edge = cross & ~(((np.abs(i - 32) < 3) & (j > 11) & (j < 55)) | ((np.abs(j - 24) < 3) & (np.abs(i - 32) < 15)))
    c[cross] *= 1.25
    c[edge & ((i < 32) | (j < 24))] *= 1.3
    c[edge & ((i >= 32) & (j >= 24))] *= 0.55
    return c, None


def t_flesh(seed=16):
    n = pfbm(4, 4, seed)
    v = np.abs(pfbm(5, 3, seed + 3) - 0.5) < 0.03
    h = n
    c = col('#6a1410') * (0.5 + 0.9 * n)[..., None]
    c[v] = col('#2a0606')
    glow = np.zeros((S, S), bool)
    j, i = np.mgrid[0:S, 0:S]
    # glowing pustules
    rs = np.random.RandomState(seed)
    for k in range(4):
        x, y = rs.randint(6, 58), rs.randint(6, 58)
        m = ((i - x) ** 2 + (j - y) ** 2) < 5
        c[m] = col('#ffb020'); glow |= m
    return c * (0.5 + 0.7 * shade(h, 4.0))[..., None], glow

# ------------------------------------------------------------------ flats


def f_grass(seed=20):
    n1 = pfbm(4, 3, seed)
    n2 = pnoise(32, seed + 3)
    c = col('#283416') * (0.55 + 0.8 * n1)[..., None]
    blades = n2 > 0.66
    c[blades] = col('#3e4a20') * (0.9 + 0.4 * n1[blades])[:, None]
    dirt = np.clip((pfbm(3, 3, seed + 9) - 0.55) * 4, 0, 1)
    c = c * (1 - dirt[..., None]) + col('#3a2c1a') * (0.7 + 0.5 * n2)[..., None] * dirt[..., None]
    # fallen leaves
    rs = np.random.RandomState(seed)
    j, i = np.mgrid[0:S, 0:S]
    for k in range(9):
        x, y = rs.randint(0, 64), rs.randint(0, 64)
        a = rs.uniform(0, 3)
        dx = ((i - x + 32) % 64) - 32; dy = ((j - y + 32) % 64) - 32
        u = dx * np.cos(a) + dy * np.sin(a); v = -dx * np.sin(a) + dy * np.cos(a)
        m = (u ** 2 / 6 + v ** 2 / 2) < 1
        c[m] = col(['#8a3a10', '#a06018', '#6a2a0c', '#a08020'][k % 4]) * rs.uniform(0.6, 1.0)
    return c * (0.75 + 0.4 * shade(n1 * 0.5 + n2 * 0.3, 2.0))[..., None], None


def f_dirt(seed=21):
    n = pfbm(4, 4, seed)
    p = pnoise(32, seed + 2)
    c = col('#4a3824') * (0.6 + 0.7 * n)[..., None]
    peb = p > 0.8
    c[peb] = col('#7a7064') * (0.8 + 0.3 * n[peb])[:, None]
    return c * (0.7 + 0.45 * shade(n * 0.6 + (p > 0.8) * 0.4, 2.5))[..., None], None


def f_flagstone(seed=22, base='#545250'):
    j, i = np.mgrid[0:S, 0:S]
    bid, u, v, mort, ed = blocks(32, 32, 16, 1)
    rnd = _h(bid, bid * 3, seed)
    n = pfbm(8, 3, seed)
    h = np.where(mort, 0.0, 0.6 + 0.4 * np.clip(ed / 3, 0, 1)) + n * 0.3
    c = col(base) * (0.65 + 0.45 * rnd)[..., None] * (0.7 + 0.5 * n)[..., None]
    c[mort] = col('#1a1816')
    cr = np.abs(pfbm(5, 3, seed + 4) - 0.5) < 0.012
    c[cr] *= 0.45
    moss = np.clip((pfbm(3, 3, seed + 9) - 0.6) * 4, 0, 1)
    c = c * (1 - moss[..., None] * 0.6) + col('#2c3c18') * moss[..., None] * 0.6
    return c * (0.6 + 0.5 * shade(h, 3))[..., None], None


def f_woodfloor(seed=23):
    c, _ = t_wood(seed, '#4a3018', planks=4)
    return np.transpose(c, (1, 0, 2)), None


def f_carpet(seed=24):
    j, i = np.mgrid[0:S, 0:S]
    x = (i % 32) - 16; y = (j % 32) - 16
    c = np.tile(col('#5a0c10'), (S, S, 1)) * (0.8 + 0.3 * pnoise(32, seed))[..., None]
    diamond = np.abs(np.abs(x) + np.abs(y) - 10) < 1.5
    c[diamond] = col('#b08a30')
    inner = (np.abs(x) + np.abs(y)) < 5
    c[inner] = col('#1a2a4a')
    dot = (np.abs(x) + np.abs(y)) < 2
    c[dot] = col('#c09040')
    border = (np.abs(x) > 14) | (np.abs(y) > 14)
    c[border] = col('#2a0608')
    # wear
    wear = np.clip((pfbm(3, 3, seed + 5) - 0.55) * 3, 0, 1)
    c = c * (1 - wear[..., None] * 0.4)
    return grime(c, seed, 0.2), None


def f_checker(seed=25):
    j, i = np.mgrid[0:S, 0:S]
    chk = ((i // 16) + (j // 16)) % 2 == 0
    n = pfbm(4, 3, seed)
    vein = np.abs(pfbm(6, 3, seed + 2) - 0.5) < 0.02
    c = np.where(chk[..., None], col('#b8b4ac') * (0.85 + 0.2 * n)[..., None], col('#1c1a1e') * (0.8 + 0.6 * n)[..., None])
    c[vein & chk] *= 0.7
    c[vein & ~chk] = col('#4a4650')
    grout = ((i % 16) == 0) | ((j % 16) == 0)
    c[grout] *= 0.6
    c = blood_splat(c, seed, 44, 20, 5)
    return c, None


def f_slime(seed=26):
    n = pfbm(4, 3, seed)
    b = pnoise(16, seed + 3)
    c = col('#2a8a18') * (0.5 + 0.8 * n)[..., None]
    glow = (n > 0.62) | (b > 0.8)
    c[glow] = col('#90ff50') * (0.8 + 0.3 * n[glow])[:, None]
    bub = np.abs(b - 0.75) < 0.03
    c[bub] = col('#d0ffb0')
    glow |= bub
    return c, glow


def f_lava(seed=27):
    n = pfbm(4, 4, seed)
    cr = np.abs(pfbm(5, 3, seed + 2) - 0.5)
    c = col('#1a0c08') * (0.6 + 0.8 * n)[..., None]
    hot = cr < 0.05
    c[hot] = np.where((cr[hot] < 0.022)[:, None], col('#ffe080'), col('#ff5010'))
    glow = hot
    return c * (0.6 + 0.6 * shade(n, 3))[..., None], glow


def f_ceilwood(seed=28):
    j, i = np.mgrid[0:S, 0:S]
    c, _ = t_wood(seed, '#2e1c10', planks=8)
    beam = (j % 32) < 8
    bw, _ = t_wood(seed + 1, '#3a2414', planks=2)
    bw = np.transpose(bw, (1, 0, 2))
    c[beam] = bw[beam] * 1.2
    c[(j % 32) == 8] *= 0.3
    # cobwebs
    web = (np.abs(((i + j) % 23) - 11) < 0.5) & (pnoise(4, seed + 7) > 0.6)
    c[web] = c[web] * 0.3 + 0.45
    return c, None


def f_ceilstone(seed=29):
    return f_flagstone(seed, '#3e3c3a')


def f_bones(seed=30):
    c, _ = f_dirt(seed)
    c *= 0.8
    j, i = np.mgrid[0:S, 0:S]
    rs = np.random.RandomState(seed)
    for k in range(10):
        x, y = rs.uniform(0, 64), rs.uniform(0, 64)
        a = rs.uniform(0, 3.14)
        ln = rs.uniform(4, 9)
        dx = ((i - x + 32) % 64) - 32; dy = ((j - y + 32) % 64) - 32
        u = dx * np.cos(a) + dy * np.sin(a); v = -dx * np.sin(a) + dy * np.cos(a)
        m = (np.abs(u) < ln) & (np.abs(v) < 0.9)
        m |= ((np.abs(u) - ln) ** 2 + (np.abs(v) - 0.8) ** 2) < 1.4
        c[m] = col('#c8bc9c') * rs.uniform(0.7, 1.0)
    for k in range(2):
        x, y = rs.uniform(8, 56), rs.uniform(8, 56)
        sk = ((i - x) ** 2 + (j - y) ** 2) < 12
        c[sk] = col('#d0c4a4')
        for s in (-1, 1):
            c[((i - x - s * 1.5) ** 2 + (j - y) ** 2) < 1.2] = col('#140c06')
    return c, None

# ------------------------------------------------------------------ sky


def sky(kind=0, W=512, H=100):
    j, i = np.mgrid[0:H, 0:W]
    t = j / (H - 1)
    if kind == 0:
        top, mid, hor = col('#05030c'), col('#1c0c30'), col('#6a2a3a')
        mc = col('#f2ecd0')
    else:
        top, mid, hor = col('#0c0204'), col('#3a0608'), col('#a83010')
        mc = col('#ff8a30')
    c = np.where((t < 0.6)[..., None], top + (mid - top) * (t / 0.6)[..., None], mid + (hor - mid) * ((t - 0.6) / 0.4)[..., None])
    glow = np.ones((H, W), bool)
    # stars
    rs = np.random.RandomState(7 + kind)
    for k in range(160):
        x, y = rs.randint(0, W), rs.randint(0, int(H * 0.6))
        b = rs.uniform(0.4, 1.0)
        c[y, x] = c[y, x] * (1 - b) + np.array([1, 1, 0.95]) * b
    # big moon with glow halo and craters
    mx, my, mr = 150, 30, 19
    d = np.sqrt(((i - mx + W / 2) % W - W / 2) ** 2 + (j - my) ** 2)
    halo = np.clip(1 - (d - mr) / 26, 0, 1) ** 2 * (d >= mr)
    c = c + (mc - c) * (halo * 0.35)[..., None]
    moon = d < mr
    mn = pfbm(4, 3, 3, size=W)[:H, :] if False else None
    cr = np.zeros((H, W))
    for k in range(9):
        cx, cy, rr = mx + rs.uniform(-12, 12), my + rs.uniform(-12, 12), rs.uniform(2, 5)
        cr += np.exp(-((i - cx) ** 2 + (j - cy) ** 2) / (rr * rr)) * 0.25
    shadeing = 1 - 0.25 * np.clip(((i - mx) + (j - my)) / mr, 0, 1)
    c[moon] = mc * (1 - cr[moon])[:, None] * shadeing[moon][:, None]
    # wispy clouds
    cl = pfbm(6, 4, 11 + kind, size=W)[:H, :] if False else None
    yy = j / H
    def tile_noise(cx, cy, seed, oct=4):
        tot = 0; amp = 1; nrm = 0
        for o in range(oct):
            fx, fy = cx * 2 ** o, cy * 2 ** o
            x = i / W * fx; y = j / H * fy
            ix = np.floor(x).astype(np.int64); iy = np.floor(y).astype(np.int64)
            ux = x - ix; uy = y - iy
            ux = ux * ux * (3 - 2 * ux); uy = uy * uy * (3 - 2 * uy)
            a = _h(ix % fx, iy, seed + o); b = _h((ix + 1) % fx, iy, seed + o)
            cc = _h(ix % fx, iy + 1, seed + o); dd = _h((ix + 1) % fx, iy + 1, seed + o)
            tot = tot + ((a * (1 - ux) + b * ux) * (1 - uy) + (cc * (1 - ux) + dd * ux) * uy) * amp
            nrm += amp; amp *= 0.5
        return tot / nrm
    cn = tile_noise(12, 4, 31 + kind)
    band = np.exp(-((yy - 0.45) / 0.22) ** 2)
    cm = np.clip((cn - 0.5) * 3, 0, 1) * band
    ccol = col('#2a1838') if kind == 0 else col('#2a0604')
    rim = col('#9a7ab0') if kind == 0 else col('#e06020')
    lit = np.clip(1 - np.abs(i - mx) / 140, 0, 1) * np.clip(1 - np.abs(j - my) / 60, 0, 1)
    cc = ccol * (1 - lit[..., None] * 0.3) + rim * (lit[..., None] * 0.6)
    c = c * (1 - cm[..., None] * 0.85) + cc * (cm[..., None] * 0.85)
    # distant hills silhouette
    hill = H - 10 - 9 * tile_noise(6, 1, 50 + kind, 3)[0] - 4 * np.sin(np.arange(W) / W * 2 * np.pi * 3)
    sil = j > hill[None, :]
    c[sil] = col('#07040a') if kind == 0 else col('#100202')
    # dead trees, church spire and a haunted house on the horizon
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    def tree(x, y, h, depth=0, ang=-90):
        import math
        x2 = x + math.cos(math.radians(ang)) * h; y2 = y + math.sin(math.radians(ang)) * h
        d.line((x, y, x2, y2), fill=255, width=max(1, int(3 - depth)))
        if depth < 4:
            for da in (-28 - rs.uniform(0, 15), 25 + rs.uniform(0, 15)):
                tree(x2, y2, h * rs.uniform(0.55, 0.75), depth + 1, ang + da)
    for x in (40, 260, 330, 470):
        tree(x, hill[x] + 2, rs.uniform(9, 14))
    hx = 380
    hy = int(hill[hx]) + 2
    d.rectangle((hx - 18, hy - 20, hx + 18, hy), fill=255)
    d.polygon([(hx - 22, hy - 20), (hx, hy - 34), (hx + 22, hy - 20)], fill=255)
    d.rectangle((hx + 8, hy - 42, hx + 16, hy - 20), fill=255)
    d.polygon([(hx + 6, hy - 42), (hx + 12, hy - 52), (hx + 18, hy - 42)], fill=255)
    sx = 90
    sy = int(hill[sx]) + 2
    d.rectangle((sx - 6, sy - 22, sx + 6, sy), fill=255)
    d.polygon([(sx - 7, sy - 22), (sx, sy - 40), (sx + 7, sy - 22)], fill=255)
    d.line((sx, sy - 44, sx, sy - 38), fill=255); d.line((sx - 2, sy - 42, sx + 2, sy - 42), fill=255)
    m = np.array(img) > 0
    c[m] = col('#07040a') if kind == 0 else col('#100202')
    # lit windows of the haunted house
    for (wx, wy) in ((hx - 11, hy - 12), (hx - 3, hy - 12), (hx + 5, hy - 12), (hx - 7, hy - 5), (hx + 11, hy - 32)):
        c[wy:wy + 3, wx:wx + 2] = col('#ffc040')
    # bats
    for k in range(7):
        bx, by = rs.randint(0, W), rs.randint(8, 50)
        for dx in range(-3, 4):
            yy_ = by + (abs(dx) == 1) * -1 + (abs(dx) >= 2) * (abs(dx) - 3)
            if 0 <= yy_ < H:
                c[yy_, (bx + dx) % W] = col('#020104')
        c[by, bx] = col('#020104')
    return np.clip(c, 0, 1), glow


WALLS = [
    ('brick', t_brick), ('stone', t_stone), ('wood', t_wood), ('wallpaper', t_wallpaper), ('bookshelf', t_bookshelf),
    ('portrait', t_portrait), ('skullwall', t_skullwall), ('hedge', t_hedge), ('pumpkinwall', t_pumpkinwall),
    ('door', lambda: t_door(10)), ('door_red', lambda: t_door(10, '#ff2a1a')), ('door_blue', lambda: t_door(10, '#3a8aff')),
    ('door_gold', lambda: t_door(10, '#ffd020')), ('doorframe', t_doorframe), ('exit', t_exit), ('window', t_window),
    ('crypt', t_crypt), ('flesh', t_flesh), ('wallpaper2', lambda: t_wallpaper(5)),
]
FLATS = [
    ('grass', f_grass), ('dirt', f_dirt), ('flagstone', f_flagstone), ('woodfloor', f_woodfloor), ('carpet', f_carpet),
    ('checker', f_checker), ('slime', f_slime), ('lava', f_lava), ('ceilwood', f_ceilwood), ('ceilstone', f_ceilstone),
    ('bones', f_bones),
]
