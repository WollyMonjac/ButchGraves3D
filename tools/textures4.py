"""Episode 5 (Curse of the Jade Skull) textures: jungle temple ruins, a stilt village, a fog-bound mission town and its
rusted "other world" twin, the red stone of Xibalba. Plus chasms, spike traps, a flowing river, and three skies.
Each returns (rgb float SxSx3, glow bool SxS)."""
import math
import numpy as np
from PIL import Image, ImageDraw
from textures import S, _h, pnoise, pfbm, shade, col, grime, blocks

J, I = np.mgrid[0:S, 0:S]
Z = lambda: np.zeros((S, S), bool)


def moss(c, seed, amt=0.6, thr=0.55, tint='#3a5a1c'):
    m = np.clip((pfbm(3, 3, seed) - thr) * 5, 0, 1) * amt
    speck = pnoise(32, seed + 5) > 0.6
    t = col(tint) * (0.7 + 0.5 * speck)[..., None]
    return c * (1 - m[..., None]) + t * m[..., None]


def stone_blocks(seed, base, bh=21, bw=32, off=16, mort='#1c1e16'):
    bid, u, v, mo, ed = blocks(bh, bw, off, 1, seed)
    rnd = _h(bid, bid * 7, seed)
    n = pfbm(8, 3, seed)
    h = np.where(mo, 0.0, 0.45 + 0.55 * np.clip(ed / 4.0, 0, 1)) + n * 0.45
    c = col(base)[None, None, :] * (0.72 + 0.38 * rnd)[..., None] * (0.72 + 0.5 * n)[..., None]
    c = np.where(mo[..., None], col(mort)[None, None, :], c)
    cr = np.abs(pfbm(6, 3, seed + 7) - 0.5) < 0.011
    c[cr] *= 0.45
    return c, h


# ------------------------------------------------------------------ walls

def t_tstone(seed=140):
    """Big weathered temple blocks, moss creeping down from the top."""
    c, h = stone_blocks(seed, '#7a7a66')
    c = moss(c, seed + 3, 0.75, 0.5)
    drip = np.clip(1 - J / 40.0, 0, 1) * (pnoise(16, seed + 9, sx=16, sy=2) > 0.55)
    c = c * (1 - drip[..., None] * 0.5) + col('#2c4a14') * (drip[..., None] * 0.5)
    return grime(c, seed, 0.45) * (0.5 + 0.65 * shade(h, 3.0))[..., None], None


def glyph_mask(seed, x0, y0, w, h):
    """A stylised Maya glyph block: a rounded cartouche with a face or abstract bars inside."""
    rs = np.random.RandomState(seed)
    m = np.zeros((S, S))
    u, v = (I - x0) / w, (J - y0) / h
    inside = (u > 0) & (u < 1) & (v > 0) & (v < 1)
    edge = inside & ((u < 0.12) | (u > 0.88) | (v < 0.12) | (v > 0.88))
    m[edge] = 0.6
    kind = rs.randint(3)
    if kind == 0:      # face: eye, nose scroll, mouth
        eye = ((u - 0.35) ** 2 + (v - 0.38) ** 2) < 0.012
        pupil = ((u - 0.37) ** 2 + (v - 0.38) ** 2) < 0.003
        nose = (np.abs(u - 0.55) < 0.06) & (v > 0.3) & (v < 0.6)
        mouth = (np.abs(v - 0.72) < 0.05) & (u > 0.3) & (u < 0.75)
        m[inside & (eye | nose | mouth)] = 1.0
        m[inside & pupil] = 0.2
    elif kind == 1:    # bar-and-dot numeral
        for k in range(rs.randint(1, 4)):
            bar = (np.abs(v - (0.62 + k * 0.1 - 0.1)) < 0.03) & (u > 0.22) & (u < 0.78)
            m[inside & bar] = 1.0
        for k in range(rs.randint(1, 4)):
            dot = ((u - (0.3 + k * 0.2)) ** 2 + (v - 0.32) ** 2) < 0.006
            m[inside & dot] = 1.0
    else:              # spiral
        ang = np.arctan2(v - 0.5, u - 0.5)
        r = np.sqrt((u - 0.5) ** 2 + (v - 0.5) ** 2)
        sp = np.abs(((r * 14 - ang / np.pi) % 2) - 1) < 0.35
        m[inside & sp & (r < 0.36)] = 1.0
    return m


def t_glyphs(seed=141):
    c, h = stone_blocks(seed, '#86806a', 32, 32, 0)
    rel = glyph_mask(seed, 3, 3, 26, 26) + glyph_mask(seed + 1, 35, 3, 26, 26) + \
        glyph_mask(seed + 2, 3, 35, 26, 26) + glyph_mask(seed + 3, 35, 35, 26, 26)
    h = h + rel * 0.55
    c = c * (1 - 0.18 * (rel > 0))[..., None]
    c = moss(c, seed + 5, 0.45, 0.62)
    return grime(c, seed, 0.4) * (0.45 + 0.7 * shade(h, 4.0))[..., None], None


def t_darts(seed=142):
    """A carved serpent face with a row of dark holes: the dart trap's tell."""
    c, h = stone_blocks(seed, '#7c7662', 32, 32, 0)
    u, v = (I - 32) / 30.0, (J - 30) / 26.0
    face = (u ** 2 + v ** 2) < 1
    h = h + face * 0.35
    for s in (-1, 1):
        eye = ((I - 32 - s * 12) ** 2 / 30.0 + (J - 20) ** 2 / 14.0) < 1
        h = h + eye * 0.3
        c[eye] = col('#4a4436')
    fang = ((np.abs(I - 32) > 14) & (np.abs(I - 32) < 18) & (J > 34) & (J < 46))
    h = h + fang * 0.3
    for k in range(5):
        hole = ((I - (16 + k * 8)) ** 2 + (J - 38) ** 2) < 4.5
        c[hole] = col('#060504')
        h = h - hole * 0.6
    c = moss(c, seed + 2, 0.4, 0.62)
    return grime(c, seed, 0.4) * (0.45 + 0.7 * shade(h, 3.5))[..., None], None


def leaves(seed, base='#1e4a16', light='#4e8a2a', dark='#081806', n=70, size=(9, 4)):
    rs = np.random.RandomState(seed)
    c = col(dark) * (0.6 + 0.6 * pfbm(8, 3, seed))[..., None]
    h = np.zeros((S, S))
    for k in range(n):
        x, y = rs.uniform(0, 64), rs.uniform(0, 64)
        a = rs.uniform(-1.6, 1.6)
        L, Wd = rs.uniform(size[0] * 0.7, size[0] * 1.4), rs.uniform(size[1] * 0.7, size[1] * 1.3)
        dx = ((I - x + 32) % 64) - 32; dy = ((J - y + 32) % 64) - 32
        uu = dx * np.cos(a) + dy * np.sin(a); vv = -dx * np.sin(a) + dy * np.cos(a)
        m = (uu / L) ** 2 + (vv / Wd) ** 2 < 1
        t = np.clip(uu / L * 0.5 + 0.5, 0, 1)
        tone = col(base) * (1 - t)[..., None] + col(light) * t[..., None]
        vein = m & (np.abs(vv) < 0.6)
        c[m] = tone[m] * rs.uniform(0.7, 1.15)
        c[vein] *= 0.75
        h[m] = 0.5 + 0.5 * (1 - (uu[m] / L) ** 2)
    return c, h


def t_foliage(seed=143):
    """A solid wall of jungle: big glossy leaves, fern fronds, a few red flowers."""
    c, h = leaves(seed)
    c2, h2 = leaves(seed + 1, '#2a5a1a', '#6aa034', '#000000', 40, (13, 5))
    m = h2 > 0
    c[m] = c2[m]; h[m] = h2[m] + 0.2
    rs = np.random.RandomState(seed)
    for k in range(5):
        x, y = rs.randint(0, 64), rs.randint(0, 64)
        fl = (((I - x + 32) % 64 - 32) ** 2 + ((J - y + 32) % 64 - 32) ** 2) < 4
        c[fl] = col(['#d02818', '#f07818', '#e8c020'][k % 3])
    return c * (0.55 + 0.6 * shade(h, 3.0))[..., None], None


def t_vinestone(seed=144):
    c, h = stone_blocks(seed, '#6e6c5c')
    c = moss(c, seed + 1, 0.5, 0.55)
    rs = np.random.RandomState(seed)
    for k in range(7):
        x0 = rs.uniform(0, 64)
        y1 = rs.uniform(30, 64)
        ph = rs.uniform(0, 6)
        xs = x0 + 2.5 * np.sin(J / 7.0 + ph)
        vine = (np.abs(((I - xs + 32) % 64) - 32) < 1.3) & (J < y1)
        c[vine] = col('#2a5014') * (0.8 + 0.4 * pnoise(16, seed + k)[vine])[:, None]
        h = h + vine * 0.4
        for y in range(4, int(y1), 7):
            lf = (((I - x0 - 3 * np.sin(y / 7.0 + ph) + 32) % 64 - 32 - 2.5) ** 2 / 6 + (J - y) ** 2 / 2) < 1
            c[lf] = col('#3e7a1e')
            h = h + lf * 0.3
    for k in range(4):
        x, y = rs.randint(0, 64), rs.randint(10, 60)
        fl = ((I - x) ** 2 + (J - y) ** 2) < 3
        c[fl] = col('#f08020') if k % 2 else col('#e83070')
    return grime(c, seed, 0.3) * (0.5 + 0.6 * shade(h, 3.0))[..., None], None


def t_hut(seed=145):
    """Bamboo poles lashed together, a band of thatch at the top."""
    n = pfbm(6, 3, seed)
    x = I % 8
    pole = np.minimum(x, 7 - x)
    h = np.clip(pole / 3.5, 0, 1) ** 0.5
    rnd = _h(I // 8, I // 8 * 3, seed)
    c = col('#9a8040') * (0.7 + 0.35 * rnd)[..., None] * (0.75 + 0.4 * n)[..., None]
    node = (J % 21) < 2
    c[node] *= 0.6
    h = h - node * 0.2
    c[x == 0] = col('#2a1c0a')
    for y in (14, 44):
        tie = (np.abs(J - y) < 2)
        c[tie] = col('#5a3a18') * (0.8 + 0.3 * n[tie])[:, None]
    th = J < 10
    thatch = col('#8a7030') * (0.6 + 0.6 * pnoise(32, seed + 4, sx=48, sy=4))[..., None]
    c[th] = thatch[th]
    return grime(c, seed, 0.5) * (0.55 + 0.6 * shade(h, 2.5))[..., None], None


def t_adobe(seed=146, window=False, other=False):
    """Cracked whitewashed mission wall over mud brick (fog town). other=True: its rusted other-world twin."""
    n = pfbm(6, 4, seed)
    c = col('#c8c0b0') * (0.75 + 0.3 * n)[..., None]
    bid, u, v, mo, ed = blocks(10, 20, 10, 1, seed)
    flake = np.clip((pfbm(4, 3, seed + 3) - 0.56) * 6, 0, 1)
    brick = col('#8a5a3a') * (0.7 + 0.4 * _h(bid, bid, seed))[..., None]
    brick = np.where(mo[..., None], col('#4a3020')[None, None, :], brick)
    c = c * (1 - flake[..., None]) + brick * flake[..., None]
    cr = np.abs(pfbm(5, 3, seed + 8) - 0.5) < 0.01
    c[cr] *= 0.4
    h = n * 0.4 + flake * -0.3
    glow = Z()
    if window:
        win = (np.abs(I - 32) < 12) & (J > 14) & (J < 46)
        arch = ((I - 32) ** 2 + (J - 20) ** 2 < 144) & (J <= 20)
        w = (win & (J > 20)) | arch
        frame = w & ~((np.abs(I - 32) < 10) & (J > 16) & (J < 44) & (((I - 32) ** 2 + (J - 20) ** 2 < 100) | (J > 20)))
        c[w] = col('#0c0c10')
        bars = w & ~frame & ((I - 32) % 5 == 0)
        c[frame | bars] = col('#3a2a1c') if not other else col('#5a2a14')
        h = h + frame * 0.3
    if other:
        # flesh-coloured rust, dried blood runs, rivets
        r = pfbm(5, 4, seed + 20)
        c = c * 0.25 + col('#5a2a14') * (0.5 + 0.8 * r)[..., None] * 0.75
        run = (pnoise(16, seed + 21, sx=24, sy=2) > 0.62) & (J > 8)
        c[run] = col('#3a0604') * (0.7 + 0.5 * r[run])[:, None]
        riv = ((I % 16) == 3) & ((J % 16) == 3)
        c[riv] = col('#a07050')
        c[(I % 32) == 0] *= 0.4
    return grime(c, seed, 0.45) * (0.55 + 0.55 * shade(h, 2.5))[..., None], glow


def t_rustgrate(seed=148):
    """Other world: chain-link fence over a dark void with something red behind it."""
    n = pfbm(6, 3, seed)
    c = col('#120404') * (0.6 + 0.8 * pfbm(3, 3, seed + 2))[..., None]
    glow = Z()
    blob = pfbm(3, 3, seed + 5) > 0.62
    c[blob] = col('#4a0a06') * (0.6 + 0.6 * n[blob])[:, None]
    d1 = ((I + J) % 8) < 1
    d2 = ((I - J) % 8) < 1
    wire = d1 | d2
    c[wire] = col('#7a5a40') * (0.5 + 0.6 * n[wire])[:, None]
    post = (I % 32) < 3
    c[post] = col('#5a3a28') * (0.6 + 0.5 * n[post])[:, None]
    return c, glow


def t_xstone(seed=149):
    """Xibalba: black volcanic blocks with skulls set into the mortar and red light seeping through the cracks."""
    c, h = stone_blocks(seed, '#3a2a28', 16, 32, 16, '#100606')
    glow = Z()
    cr = np.abs(pfbm(5, 3, seed + 4) - 0.5) < 0.014
    c[cr] = col('#ff3010')
    glow |= cr
    for (x, y) in ((16, 8), (48, 24), (16, 40), (48, 56)):
        sk = ((I - x) ** 2 / 36.0 + (J - y) ** 2 / 30.0) < 1
        c[sk] = col('#c8bc98') * (0.7 + 0.3 * pfbm(8, 2, seed)[sk])[:, None]
        h = h + sk * 0.6
        for s in (-1, 1):
            e = ((I - x - s * 2.2) ** 2 + (J - y + 1) ** 2) < 2.2
            c[e] = col('#ff4010'); glow |= e
        mo = (np.abs(I - x) < 3) & (np.abs(J - y - 4) < 1)
        c[mo] = col('#201810')
    return c * (0.5 + 0.6 * shade(h, 3.0))[..., None], glow


def t_goldwall(seed=150):
    """The inner sanctum: gold plates with jade inlays and a sun disc."""
    bid, u, v, mo, ed = blocks(32, 32, 0, 1, seed)
    n = pfbm(8, 3, seed)
    h = 0.5 + 0.5 * np.clip(ed / 4.0, 0, 1) + n * 0.2
    c = col('#c09020') * (0.75 + 0.4 * n)[..., None]
    c[mo] = col('#3a2a08')
    lx, ly = I % 32, J % 32
    r = np.sqrt((lx - 16) ** 2 + (ly - 16) ** 2)
    ring = (r > 7) & (r < 10)
    jade = r <= 6
    rays = (r > 10) & (r < 14) & ((np.arctan2(ly - 16, lx - 16) * 8 / np.pi % 2) < 1)
    c[ring | rays] = col('#f0c840')
    c[jade] = col('#2a9a6a') * (0.7 + 0.5 * n[jade])[:, None]
    h = h + ring * 0.3 + rays * 0.2 + jade * 0.4
    return c * (0.5 + 0.7 * shade(h, 3.0))[..., None], None


def t_falls(seed=151):
    """A waterfall face: vertical white-green streaks (scrolled downwards in the game)."""
    s1 = pnoise(16, seed, sx=24, sy=3)
    s2 = pnoise(8, seed + 3, sx=12, sy=2)
    c = col('#3a6a6a') * (0.6 + 0.6 * s1)[..., None]
    foam = s1 * 0.6 + s2 * 0.5 > 0.78
    c[foam] = col('#d8f0e8') * (0.8 + 0.2 * s2[foam])[:, None]
    mid = (s1 > 0.55) & ~foam
    c[mid] = col('#78a8a0')
    return c, None


def t_ofrendawall(seed=152):
    """A Day of the Dead mural on adobe: a big sugar skull wreathed in marigolds."""
    c, glow = t_adobe(seed)
    sk = ((I - 32) ** 2 / 300.0 + (J - 28) ** 2 / 260.0) < 1
    jaw = (np.abs(I - 32) < 11) & (J > 34) & (J < 48)
    m = sk | jaw
    c[m] = col('#f0ece0')
    for s in (-1, 1):
        eye = ((I - 32 - s * 8) ** 2 + (J - 26) ** 2) < 26
        c[eye] = col('#1a1a20')
        petal = eye & (((I - 32 - s * 8) ** 2 + (J - 26) ** 2) > 12)
        c[petal] = col('#e83070') if s < 0 else col('#20a0d0')
        c[((I - 32 - s * 8) ** 2 + (J - 26) ** 2) < 3] = col('#f0d020')
    nose = (np.abs(I - 32) < 2) & (J > 31) & (J < 36)
    c[nose] = col('#1a1a20')
    teeth = jaw & ((I % 4) == 0) & (J > 38)
    c[teeth] = col('#2a2a2a')
    c[jaw & (np.abs(J - 41) < 1)] = col('#2a2a2a')
    rs = np.random.RandomState(seed)
    for k in range(26):
        a = k / 26 * 2 * np.pi
        x, y = 32 + np.cos(a) * 27, 30 + np.sin(a) * 25
        fl = ((I - x) ** 2 + (J - y) ** 2) < rs.uniform(5, 9)
        c[fl] = col('#f08010') * rs.uniform(0.8, 1.1)
        c[((I - x) ** 2 + (J - y) ** 2) < 1.5] = col('#c04008')
    return c, glow


# ------------------------------------------------------------------ flats

def f_jgrass(seed=160):
    n1 = pfbm(4, 3, seed)
    n2 = pnoise(32, seed + 3)
    c = col('#2e5a1a') * (0.55 + 0.7 * n1)[..., None]
    blades = n2 > 0.62
    c[blades] = col('#4a8226') * (0.9 + 0.4 * n1[blades])[:, None]
    dirt = np.clip((pfbm(3, 3, seed + 9) - 0.6) * 4, 0, 1)
    c = c * (1 - dirt[..., None]) + col('#4a3a1e') * (0.7 + 0.5 * n2)[..., None] * dirt[..., None]
    rs = np.random.RandomState(seed)
    for k in range(6):
        x, y = rs.randint(0, 64), rs.randint(0, 64)
        fl = (((I - x + 32) % 64 - 32) ** 2 + ((J - y + 32) % 64 - 32) ** 2) < 2.5
        c[fl] = col(['#f0d020', '#e83070', '#f0f0e0'][k % 3])
    return c * (0.75 + 0.4 * shade(n1 * 0.5 + n2 * 0.3, 2.0))[..., None], None


def f_mud(seed=161):
    n = pfbm(4, 4, seed)
    c = col('#5a4426') * (0.6 + 0.6 * n)[..., None]
    pud = pfbm(3, 3, seed + 4) > 0.64
    c[pud] = col('#2a2418') * (0.8 + 0.4 * n[pud])[:, None]
    rim = (pfbm(3, 3, seed + 4) > 0.6) & ~pud
    c[rim] *= 0.75
    tracks = (np.abs(((I + 3 * np.sin(J / 6.0)) % 22) - 11) < 1) & (pnoise(8, seed + 6) > 0.5)
    c[tracks] *= 0.7
    return c * (0.7 + 0.4 * shade(n, 2.0))[..., None], None


def f_tfloor(seed=162):
    c, h = stone_blocks(seed, '#8a8470', 32, 32, 16)
    lx, ly = I % 32, J % 32
    st = (np.abs(lx - 16) < 9) & (np.abs(ly - 16) < 9) & ~((np.abs(lx - 16) < 7) & (np.abs(ly - 16) < 7))
    h = h + st * 0.25
    c = moss(c, seed + 2, 0.4, 0.6)
    return c * (0.55 + 0.55 * shade(h, 3.0))[..., None], None


def f_pplate(seed=172):
    """A pressure plate: a temple flagstone sunk a finger's width, with a worn glyph (darts fly when you step on it)."""
    c, h = stone_blocks(seed, '#8a8470', 32, 32, 16)
    c = moss(c, seed + 2, 0.3, 0.62)
    pl = (np.abs(I - 32) < 22) & (np.abs(J - 32) < 22)
    edge = pl & ~((np.abs(I - 32) < 20) & (np.abs(J - 32) < 20))
    h = h - pl * 0.25
    c[edge] = col('#2a2820')
    inner = pl & ~edge
    c[inner] = c[inner] * 0.7 + col('#a88050') * 0.3       # a warmer, newer-looking slab than the floor around it
    r = np.sqrt((I - 32.0) ** 2 + (J - 32.0) ** 2)
    sp = (np.abs(((r * 0.6 - np.arctan2(J - 32.0, I - 32.0) / np.pi) % 2) - 1) < 0.3) & (r < 15)
    c[sp] = col('#6a2a18')                                 # the glyph, picked out in old red paint
    return c * (0.55 + 0.55 * shade(h, 3.0))[..., None], None


def f_planks(seed=163):
    n = pfbm(6, 3, seed)
    y = J % 11
    rnd = _h(J // 11, J // 11 * 5, seed)
    grain = pnoise(4, seed + 2, sx=2, sy=40) * 0.3
    c = col('#6a4a26') * (0.65 + 0.4 * rnd)[..., None] * (0.75 + 0.35 * n + grain)[..., None]
    gap = y == 0
    c[gap] = col('#140c04')
    nail = ((I % 32) == 4) & ((y == 3) | (y == 8))
    c[nail] = col('#2a2a2a')
    return grime(c, seed, 0.3), None


def f_water(seed=164):
    """River water (scrolled in the game)."""
    n1 = pnoise(8, seed, sx=4, sy=8)
    n2 = pnoise(16, seed + 3, sx=8, sy=16)
    c = col('#1e4a46') * (0.6 + 0.6 * n1)[..., None]
    rip = np.abs(n2 - 0.5) < 0.04
    c[rip] = col('#6aa8a0')
    hl = (n1 * 0.6 + n2 * 0.5) > 0.86
    c[hl] = col('#c8e8e0')
    return c, None


def f_pit(seed=165):
    """A chasm: rock ledges at the rim falling away into black and a little mist far below."""
    n = pfbm(6, 3, seed)
    c = col('#020203') * (0.6 + 0.6 * n)[..., None]
    mist = pfbm(3, 3, seed + 3)
    m = np.clip((mist - 0.55) * 3, 0, 1) * 0.35
    c = c * (1 - m[..., None]) + col('#2a3a34') * m[..., None]
    return c, None


def f_spikes(seed=166, on=True):
    c, h = stone_blocks(seed, '#6a665a', 16, 16, 8)
    glow = Z()
    lx, ly = I % 16, J % 16
    hole = ((lx - 8) ** 2 + (ly - 8) ** 2) < 7
    c[hole] = col('#0a0806')
    if on:
        tip = ((lx - 8) ** 2 + (ly - 8) ** 2) < 5
        c[tip] = col('#b8b0a0') * (0.6 + 0.6 * np.clip(1 - np.sqrt((lx[tip] - 7) ** 2 + (ly[tip] - 7) ** 2) / 4, 0, 1))[:, None]
        blood = tip & (pnoise(8, seed + 2) > 0.62)
        c[blood] = col('#6a0a06')
    # carved border so the trap reads even when the spikes are down
    br = (I < 2) | (I >= 62) | (J < 2) | (J >= 62)
    c[br] = col('#3a3628')
    return c * (0.6 + 0.5 * shade(h, 2.5))[..., None], glow


def f_rustfloor(seed=167):
    """Other world: rusted grating over a red-black drop."""
    n = pfbm(6, 3, seed)
    c = col('#1a0404') * (0.6 + 0.7 * pfbm(3, 3, seed + 1))[..., None]
    bar = ((I % 6) < 2) | ((J % 16) < 2)
    c[bar] = col('#6a3a22') * (0.5 + 0.7 * n[bar])[:, None]
    stain = pfbm(4, 3, seed + 7) > 0.66
    c[stain & bar] = col('#3a0804')
    return c, None


def f_thatch(seed=168):
    s = pnoise(32, seed, sx=48, sy=4)
    c = col('#7a6028') * (0.55 + 0.6 * s)[..., None]
    c[(J % 16) < 1] = col('#3a2a10')
    return c, None


def f_tceil(seed=169):
    c, h = stone_blocks(seed, '#4a4840', 32, 32, 0, '#141410')
    return c * (0.6 + 0.4 * shade(h, 2.0))[..., None], None


def f_xlava(seed=170):
    """Xibalba's floor: black rock with rivers of molten red (a hurt floor in the game)."""
    n = pfbm(4, 4, seed)
    cr = np.abs(pfbm(4, 3, seed + 2) - 0.5)
    c = col('#140806') * (0.6 + 0.8 * n)[..., None]
    hot = cr < 0.07
    c[hot] = np.where((cr[hot] < 0.03)[:, None], col('#ffd040'), col('#ff3008'))
    return c * (0.6 + 0.6 * shade(n, 3))[..., None], hot


def f_xfloor(seed=171):
    c, h = stone_blocks(seed, '#4a3028', 32, 32, 16, '#120606')
    glow = Z()
    lx, ly = I % 32, J % 32
    sun = (np.sqrt((lx - 16) ** 2 + (ly - 16) ** 2) - 9) ** 2 < 2
    c[sun] = col('#8a1a08')
    return c * (0.55 + 0.55 * shade(h, 3.0))[..., None], glow


# ------------------------------------------------------------------ skies

def _tile_noise(i, j, W, H, cx, cy, seed, oct=4):
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


def sky_jungle(W=512, H=100):
    """Hot afternoon over the jungle: blue sky, towering clouds, a stepped pyramid and a smoking volcano on the horizon,
    and an ominous storm front with a skull-shaped hole in it (it's still Halloween)."""
    j, i = np.mgrid[0:H, 0:W]
    t = j / (H - 1)
    top, hor = col('#2a6ad0'), col('#b8d8e8')
    c = top + (hor - top) * (t ** 1.3)[..., None]
    cn = _tile_noise(i, j, W, H, 10, 3, 61)
    band = np.exp(-((t - 0.55) / 0.3) ** 2)
    cm = np.clip((cn - 0.48) * 3.5, 0, 1) * band
    lit = np.clip(1 - j / (H * 0.8), 0, 1)
    cloud = col('#f4f4f0') * (0.75 + 0.25 * lit)[..., None]
    c = c * (1 - cm[..., None]) + cloud * cm[..., None]
    # storm front on one side
    storm = np.clip(1 - np.abs(((i - 380 + W / 2) % W) - W / 2) / 110.0, 0, 1) * np.clip(1 - t * 1.2, 0, 1)
    sc = _tile_noise(i, j, W, H, 16, 4, 66)
    sm = np.clip(storm * (0.6 + sc), 0, 1) * 0.85
    c = c * (1 - sm[..., None]) + col('#3a3a48') * sm[..., None]
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    # pyramid and volcano: both run all the way down behind the canopy, so they never float above the treeline
    px, base = 140, H - 14
    d.rectangle((px - 52, base, px + 52, H), fill=255)
    for k in range(6):
        w = 46 - k * 7
        d.rectangle((px - w, base - k * 6 - 6, px + w, base - k * 6), fill=255)
    d.rectangle((px - 6, base - 44, px + 6, base - 36), fill=255)
    d.polygon([(300, base), (338, base - 30), (352, base - 30), (396, base), (410, H), (286, H)], fill=255)
    m = np.array(img) > 0
    c[m] = col('#4a5a5a') * (0.8 + 0.2 * (j[m] / H))[:, None]
    smoke = np.exp(-((i - 345 - (base - 30 - j) * 0.4) ** 2) / (40 + (base - j) * 3.0)) * (j < base - 30)
    c = c * (1 - smoke[..., None] * 0.55) + col('#8a8a88') * (smoke[..., None] * 0.55)
    # endless canopy
    can = H - 22 - 9 * _tile_noise(i, j, W, H, 40, 1, 70, 3)[0]     # a deep canopy band over the bases
    sil = j > can[None, :]
    c[sil] = col('#16361a') * (0.7 + 0.6 * _tile_noise(i, j, W, H, 64, 8, 71, 2)[sil])[:, None]
    # birds
    rs = np.random.RandomState(5)
    for k in range(10):
        x, y = rs.randint(0, W), rs.randint(15, 50)
        c[y, x % W] = c[y, (x + 2) % W] = col('#1a1a1a')
        c[y - 1, (x + 1) % W] = col('#1a1a1a')
    return np.clip(c, 0, 1), np.ones((H, W), bool)


def sky_fog(W=512, H=100, other=False):
    """Silent white fog (or, in the other world, a rust-red murk)."""
    j, i = np.mgrid[0:H, 0:W]
    t = j / (H - 1)
    n = _tile_noise(i, j, W, H, 8, 3, 81)
    if other:
        c = col('#1a0402') + (col('#4a0c06') - col('#1a0402')) * (t ** 1.5)[..., None]
        c = c * (0.7 + 0.5 * n)[..., None]
    else:
        c = col('#8a8c8c') + (col('#b8bab8') - col('#8a8c8c')) * t[..., None]
        c = c * (0.92 + 0.12 * n)[..., None]
        # the ghost of a church steeple through the murk
        img = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(img)
        d.rectangle((300, 52, 312, 99), fill=255)
        d.polygon([(298, 52), (306, 30), (314, 52)], fill=255)
        d.rectangle((305, 22, 307, 32), fill=255)
        d.rectangle((302, 25, 310, 27), fill=255)
        m = np.array(img) > 0
        c[m] = c[m] * 0.82
    return np.clip(c, 0, 1), np.ones((H, W), bool)


WALLS4 = [('tstone', t_tstone), ('glyphs', t_glyphs), ('darts', t_darts), ('foliage', t_foliage), ('vinestone', t_vinestone),
          ('hut', t_hut), ('adobe', t_adobe), ('adobewin', lambda: t_adobe(147, True)), ('rust', lambda: t_adobe(146, False, True)),
          ('rustwin', lambda: t_adobe(147, True, True)), ('rustgrate', t_rustgrate), ('xstone', t_xstone), ('goldwall', t_goldwall),
          ('falls', t_falls), ('mural', t_ofrendawall)]
FLATS4 = [('jgrass', f_jgrass), ('jmud', f_mud), ('tfloor', f_tfloor), ('pplate', f_pplate), ('planks', f_planks), ('river', f_water),
          ('pit', f_pit),
          ('spikes', f_spikes), ('spikesoff', lambda: f_spikes(166, False)), ('rustfloor', f_rustfloor), ('thatch', f_thatch),
          ('tceil', f_tceil), ('xlava', f_xlava), ('xfloor', f_xfloor)]
SKIES4 = [('sky6', sky_jungle), ('sky7', sky_fog), ('sky8', lambda: sky_fog(other=True))]
