"""Textures and skies for episode 2 (town + carnival) and episode 3 (swamp + castle), plus the dawn sky for the E1 cutscene."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from textures import S, FONTS, _h, pnoise, pfbm, shade, col, blocks, grime, t_brick, t_stone, t_wood

J, I = np.mgrid[0:S, 0:S]
BLACKOPS = FONTS + '/fontsource-black-ops-one-5.3.0/package/files/black-ops-one-latin-400-normal.woff'
CREEP = FONTS + '/fontsource-creepster-5.3.0/package/files/creepster-latin-400-normal.woff'


def text_mask(txt, w, h, font=BLACKOPS, size=12):
    img = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(img)
    ft = ImageFont.truetype(font, size)
    bb = d.textbbox((0, 0), txt, font=ft)
    while bb[2] - bb[0] > w - 2 and size > 6:
        size -= 1
        ft = ImageFont.truetype(font, size)
        bb = d.textbbox((0, 0), txt, font=ft)
    d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], (h - (bb[3] - bb[1])) // 2 - bb[1]), txt, font=ft, fill=255)
    return np.array(img) > 110


def stripes_v(c1, c2, n=8, seed=0, fold=0.25):
    """Vertical canvas stripes with fold shading."""
    k = (I * n // S) % 2
    c = np.where((k == 0)[..., None], col(c1)[None, None, :], col(c2)[None, None, :])
    f = 0.75 + fold * np.cos((I % (S // n)) / (S // n) * 2 * np.pi) + 0.12 * pfbm(8, 3, seed)
    return c * f[..., None]


# ================================================================== episode 2: town + carnival

def t_shop(seed=40, sign='CANDY', lit='#ffb040'):
    c, _ = t_brick(seed, '#5a2a22')
    glow = np.zeros((S, S), bool)
    # sign board
    sb = (J >= 3) & (J < 15) & (I >= 2) & (I < 62)
    c[sb] = col('#1a1410') * (0.8 + 0.3 * pnoise(16, seed)[sb])[:, None]
    m = np.zeros((S, S), bool)
    m[4:14, 4:60] = text_mask(sign, 56, 10, BLACKOPS, 11)
    c[m] = col('#ff4020' if sign != 'DINER' else '#40e0ff'); glow |= m
    # shop window with warm light, crossbars and silhouettes of pumpkins in the display
    win = (J >= 20) & (J < 50) & (I >= 6) & (I < 58)
    frame = win & ((J < 22) | (J >= 48) | (I < 8) | (I >= 56) | (np.abs(I - 32) < 1))
    lightc = col(lit) * (0.75 + 0.35 * (1 - (J - 20) / 30))[..., None]
    c[win] = lightc[win]
    glow |= win & ~frame
    for x in (16, 28, 44):
        pk = ((I - x) ** 2 / 25 + (J - 45) ** 2 / 12) < 1
        c[pk & win] = col('#2a1004'); glow &= ~(pk & win)
        eyes = pk & (np.abs(J - 44) < 1) & ((np.abs(I - x + 2) < 1) | (np.abs(I - x - 2) < 1))
        c[eyes] = col('#ffe060'); glow |= eyes
    c[frame] = col('#2c1a10')
    # sill
    sill = (J >= 50) & (J < 53) & (I >= 4) & (I < 60)
    c[sill] = col('#6a6058') * (0.8 + 0.3 * pnoise(16, seed + 1)[sill])[:, None]
    return c, glow


def t_siding(seed=41, base='#4a6a68'):
    board = J // 8
    rnd = _h(board, board * 3, seed)
    h = (J % 8) / 8.0 + pfbm(8, 2, seed) * 0.2
    c = col(base)[None, None, :] * (0.65 + 0.35 * rnd)[..., None] * (0.75 + 0.4 * pfbm(16, 3, seed + 2))[..., None]
    # peeling paint shows grey wood
    peel = pfbm(6, 4, seed + 5) > 0.62
    c[peel] = col('#5a5048') * (0.7 + 0.4 * pnoise(32, seed + 6)[peel])[:, None]
    c[(J % 8) == 7] *= 0.4
    c = grime(c, seed + 3, 0.7)
    return c * (0.6 + 0.5 * shade(h, 2.5))[..., None], None


def t_tent(seed=42, c1='#b01818', c2='#e8e0d0'):
    c = stripes_v(c1, c2, 8, seed)
    stain = np.clip((pfbm(4, 4, seed + 3) - 0.55) * 3, 0, 1)
    c = c * (1 - stain[..., None] * 0.5) + col('#3a2a18') * stain[..., None] * 0.5
    return grime(c, seed + 1, 0.5), None


def t_booth(seed=43):
    c = stripes_v('#c02020', '#f0d040', 8, seed, 0.15)
    glow = np.zeros((S, S), bool)
    # counter (wood) bottom, dark opening with prizes, bulb border
    cnt = J >= 44
    wc, _ = t_wood(seed, '#5a3418', 8)
    c[cnt] = wc[cnt]
    op = (J >= 18) & (J < 44) & (I >= 6) & (I < 58)
    c[op] = col('#0c0808')
    # teddy-bear-ish prizes and a row of milk bottles
    for k, x in enumerate((14, 30, 46)):
        b = ((I - x) ** 2 + (J - 30) ** 2) < 30
        cc = ['#8a5a30', '#d04090', '#4080d0'][k]
        c[b & op] = col(cc) * 0.8
        hd = ((I - x) ** 2 + (J - 23) ** 2) < 12
        c[hd & op] = col(cc)
    for x in range(10, 56, 6):
        bt = (np.abs(I - x) < 2) & (J >= 38) & (J < 44)
        c[bt] = col('#e8e8e0')
    m = np.zeros((S, S), bool)
    m[4:15, 6:58] = text_mask('PRIZES', 52, 11, BLACKOPS, 11)
    c[m] = col('#fff0a0'); glow |= m
    for x in range(4, 62, 6):
        b = ((I - x) ** 2 + (J - 16) ** 2) < 3
        c[b] = col(['#ff3020', '#ffe040', '#40a0ff'][x // 6 % 3]); glow |= b
    return c, glow


def t_mirror(seed=44):
    """Warped funhouse mirror in a gilt frame."""
    c = np.zeros((S, S, 3))
    glow = np.zeros((S, S), bool)
    fr = (I < 5) | (I >= 59) | (J < 4) | (J >= 60)
    gold = col('#b08830') * (0.6 + 0.6 * pfbm(16, 2, seed))[..., None]
    w = np.sin(J / 64 * 2 * np.pi * 1.5) * 9 + np.sin(I / 64 * 2 * np.pi * 2) * 3
    v = (I + w) / 64.0
    band = 0.55 + 0.45 * np.sin(v * 2 * np.pi * 2.5)
    c[:] = (col('#8090a8') * band[..., None] + col('#e8f0ff') * (1 - band)[..., None] * 0.6)
    # distorted reflection of a figure (stretched dark silhouette)
    fig = (np.abs(I + w * 1.5 - 32) < 6 + 4 * np.sin(J / 8)) & (J > 14) & (J < 54)
    c[fig] = col('#2a2030') * 1.2
    head = ((I + w - 32) ** 2 / 64 + (J - 12) ** 2 / 20) < 1
    c[head] = col('#3a2830')
    c[fr] = gold[fr]
    glow |= ~fr
    return c, glow


def t_funwall(seed=45):
    """Hypnotic black/white spiral with a red zigzag band."""
    x, y = I - 32 + 0.5, J - 32 + 0.5
    r = np.sqrt(x * x + y * y); a = np.arctan2(y, x)
    sp = np.sin(a * 3 + r * 0.35) > 0
    c = np.where(sp[..., None], col('#e8e4d8')[None, None, :], col('#141018')[None, None, :]).astype(float)
    zz = np.abs(((I // 8) % 2) * 8 - (I % 8)) * 0 + np.abs((I % 16) - 8)
    band = (np.abs(J - 56 - zz * 0.4) < 3)
    c[band] = col('#c01818')
    c = c * (0.75 + 0.3 * pfbm(8, 3, seed))[..., None]
    return grime(c, seed, 0.4), None


def t_clownwall(seed=46):
    """Peeling mural: a giant grinning clown face."""
    c, _ = t_siding(seed, '#6a5a40')
    glow = np.zeros((S, S), bool)
    face = ((I - 32) ** 2 + (J - 30) ** 2) < 26 ** 2
    c[face] = col('#e8e0d0') * (0.8 + 0.25 * pfbm(8, 3, seed)[face])[:, None]
    for s in (-1, 1):
        e = ((I - 32 - s * 10) ** 2 + (J - 24) ** 2) < 25
        dia = (np.abs(I - 32 - s * 10) + np.abs(J - 24) * 0.7) < 9
        c[dia & face] = col('#1a1a2a')
        c[e] = col('#ffd020'); glow |= ((I - 32 - s * 10) ** 2 + (J - 24) ** 2) < 5
    nose = ((I - 32) ** 2 + (J - 32) ** 2) < 20
    c[nose] = col('#d01010')
    mouth = (((I - 32) ** 2) / 300 + ((J - 42) ** 2) / 30) < 1
    c[mouth] = col('#a00808')
    teeth = mouth & (((J == 39) | (J == 45)) & ((I % 4) < 2))
    c[teeth] = col('#f0f0e0')
    for s in (-1, 1):
        hair = ((I - 32 - s * 28) ** 2 + (J - 22) ** 2) < 120
        c[hair] = col('#e05010') * (0.7 + 0.4 * pnoise(16, seed + 3)[hair])[:, None]
    peel = pfbm(8, 4, seed + 9) > 0.66
    c[peel & face] *= 0.55
    return grime(c, seed + 1, 0.5), glow


def t_lightwall(seed=47):
    c, _ = t_wood(seed, '#3a2414', 8)
    glow = np.zeros((S, S), bool)
    for y in (12, 44):
        rail = np.abs(J - y) < 2
        c[rail] = col('#b08830') * 0.7
        for x in range(4, 64, 8):
            b = ((I - x) ** 2 + (J - y) ** 2) < 7
            cc = ['#ff4020', '#ffd040', '#40c0ff', '#60ff60'][(x // 8 + y // 32) % 4]
            c[b] = col(cc); glow |= b
    return c, glow


def t_bigtop(seed=48):
    c = stripes_v('#801010', '#d0a020', 8, seed, 0.2)
    rope = (np.abs(J - 8) < 2) | (np.abs(J - 58) < 2)
    tw = ((I + J) % 6) < 3
    c[rope] = np.where(tw[rope][:, None], col('#e0c060'), col('#806020'))
    return grime(c, seed, 0.4), None


def t_poster(seed=49):
    """Circus poster pasted on brick: MISTER GIGGLES."""
    c, _ = t_brick(seed, '#5a2a22')
    glow = np.zeros((S, S), bool)
    po = (I >= 8) & (I < 56) & (J >= 6) & (J < 58)
    c[po] = col('#e8d8a8') * (0.7 + 0.35 * pfbm(8, 3, seed)[po])[:, None]
    m = np.zeros((S, S), bool)
    m[8:18, 10:54] = text_mask('MISTER', 44, 10, CREEP, 12)
    m[46:56, 10:54] = text_mask('GIGGLES', 44, 10, CREEP, 12)
    c[m] = col('#b01010')
    face = ((I - 32) ** 2 + (J - 32) ** 2) < 110
    c[face & po] = col('#f0ece4')
    for s in (-1, 1):
        e = ((I - 32 - s * 5) ** 2 + (J - 29) ** 2) < 5
        c[e] = col('#101010')
    c[((I - 32) ** 2 + (J - 33) ** 2) < 6] = col('#d01010')
    smile = ((I - 32) ** 2 / 60 + (J - 37) ** 2 / 6) < 1
    c[smile] = col('#801010')
    hat = (np.abs(I - 32) < 6) & (J >= 16) & (J < 23) | (np.abs(I - 32) < 9) & (J >= 22) & (J < 24)
    c[hat] = col('#141010')
    torn = (pfbm(6, 4, seed + 4) > 0.67) & po
    c[torn] = t_brick(seed, '#5a2a22')[0][torn]
    return c, glow


def f_asphalt(seed=50):
    n = pfbm(16, 3, seed)
    c = col('#2a2a2c') * (0.7 + 0.5 * n)[..., None]
    specks = pnoise(64, seed + 1) > 0.75
    c[specks] *= 1.4
    cr = np.abs(pfbm(5, 3, seed + 2) - 0.5) < 0.012
    c[cr] *= 0.4
    line = (np.abs(I - 32) < 2) & ((J % 32) < 18)
    c[line] = col('#b09020') * (0.7 + 0.4 * n[line])[:, None]
    return c, None


def f_sidewalk(seed=51):
    n = pfbm(8, 3, seed)
    c = col('#6c6a66') * (0.75 + 0.4 * n)[..., None]
    gap = ((I % 32) == 0) | ((J % 32) == 0)
    c[gap] *= 0.45
    cr = np.abs(pfbm(4, 3, seed + 2) - 0.5) < 0.01
    c[cr] *= 0.5
    leaves = pfbm(10, 2, seed + 7) > 0.72
    c[leaves] = col('#8a4010') * (0.7 + 0.5 * pnoise(32, seed)[leaves])[:, None]
    return c, None


def f_sawdust(seed=52):
    n = pfbm(16, 3, seed)
    c = col('#9a7a48') * (0.7 + 0.45 * n)[..., None]
    sp = pnoise(64, seed + 3) > 0.7
    c[sp] = col('#c8a870')
    blood = pfbm(4, 4, seed + 8) > 0.68
    c[blood] = col('#4a0806')
    return c, None


def f_ceiltent(seed=53):
    c = stripes_v('#401010', '#6a5420', 8, seed, 0.3)
    return c * 0.8, None


# ================================================================== episode 3: swamp + castle

def t_castle(seed=60):
    c, _ = t_stone(seed, '#4a4652')
    big, u, v, mort, ed = blocks(21, 32, 16, 1, seed)
    c = c * (0.85 + 0.25 * _h(big, big * 5, seed))[..., None]
    return c, None


def t_curtain(seed=61):
    f = 0.55 + 0.45 * np.cos(I / 64 * 2 * np.pi * 6 + np.sin(J / 20) * 0.5)
    c = col('#7a0610') * f[..., None] * (0.8 + 0.3 * pfbm(8, 3, seed))[..., None]
    rope = (np.abs(J - 40 + np.abs(I - 32) * 0.15) < 1.5)
    c[rope] = col('#d0a030')
    top = J < 6
    c[top] = col('#b08830') * (0.7 + 0.4 * pnoise(16, seed)[top])[:, None]
    return c, None


def t_tapestry(seed=62):
    c, _ = t_castle(seed)
    glow = np.zeros((S, S), bool)
    ban = (I >= 12) & (I < 52) & (J >= 2) & (J < 56 + (np.abs(I - 32) < 20) * (6 - np.abs(I - 32) * 0.3))
    c[ban] = col('#6a0812') * (0.7 + 0.4 * pfbm(8, 3, seed)[ban])[:, None]
    edge = ban & ((I < 14) | (I >= 50))
    c[edge] = col('#c09030')
    # black bat emblem
    x, y = np.abs(I - 32), J - 28
    body = (x ** 2 / 9 + y ** 2 / 36) < 1
    wing = (y > -6) & (y < 6 - (x - 4) * 0.25) & (x < 17) & ~((np.abs(x - 10) < 3) & (y > 2)) & ~((np.abs(x - 15) < 2) & (y > 0))
    c[(body | wing) & ban] = col('#120808')
    for s in (-1, 1):
        e = ((I - 32 - s * 1.5) ** 2 + (J - 25) ** 2) < 1.2
        c[e] = col('#ff2010'); glow |= e
    return c, glow


def t_labwall(seed=63):
    tile = ((I % 16) == 0) | ((J % 16) == 0)
    c = col('#a8c0a8') * (0.75 + 0.3 * pfbm(8, 3, seed))[..., None]
    c[tile] = col('#4a5a4a')
    stain = np.clip((pfbm(4, 4, seed + 5) - 0.5) * 2.5, 0, 1)
    c = c * (1 - stain[..., None] * 0.6) + col('#3a4a18') * stain[..., None] * 0.6
    pipe = np.abs(J - 10) < 3
    c[pipe] = col('#7a5a30') * (0.6 + 0.6 * (1 - np.abs(J[pipe] - 10) / 3))[:, None]
    return grime(c, seed, 0.6), None


def t_machine(seed=64):
    c = col('#3a3e44') * (0.7 + 0.35 * pfbm(16, 3, seed))[..., None]
    glow = np.zeros((S, S), bool)
    pan = ((I % 32) < 1) | ((J % 32) < 1)
    c[pan] *= 0.5
    for (x, y) in ((14, 14), (46, 14)):
        d = ((I - x) ** 2 + (J - y) ** 2)
        c[d < 64] = col('#d8d0b0')
        c[d < 50] = col('#f0e8c8')
        needle = (np.abs((I - x) * 0.6 - (y - J)) < 1) & (d < 40) & (J <= y)
        c[needle] = col('#c01010')
        glow |= d < 50
    for k, x in enumerate(range(8, 60, 8)):
        b = ((I - x) ** 2 + (J - 40) ** 2) < 6
        c[b] = col(['#40ff60', '#ff3020', '#ffd040'][k % 3]); glow |= b
    for x in (16, 32, 48):
        lv = (np.abs(I - x) < 2) & (J >= 48) & (J < 60)
        c[lv] = col('#202020')
        kn = ((I - x) ** 2 + (J - 48) ** 2) < 8
        c[kn] = col('#c01010')
    return c, glow


def t_swampwood(seed=65):
    c, _ = t_wood(seed, '#3a3020', 5)
    moss = np.clip((pfbm(4, 4, seed + 4) - 0.45) * 3, 0, 1) * np.clip((J - 20) / 44, 0, 1)
    c = c * (1 - moss[..., None] * 0.8) + col('#3a5a20') * moss[..., None] * 0.8 * (0.7 + 0.5 * pnoise(32, seed)[..., None])
    return grime(c, seed + 2, 0.7), None


def t_rockmoss(seed=66):
    n = pfbm(4, 5, seed)
    h = n
    c = col('#4a4640') * (0.5 + 0.8 * n)[..., None]
    moss = np.clip((pfbm(5, 4, seed + 3) - 0.5) * 4, 0, 1)
    c = c * (1 - moss[..., None] * 0.7) + col('#2e4a1a') * moss[..., None] * 0.7
    strands = (pnoise(32, seed + 6, sx=32, sy=1) > 0.72) & (J < 30 + 20 * pnoise(8, seed + 7, sx=8, sy=1))
    c[strands] = col('#4a5a30') * 0.8
    return c * (0.5 + 0.7 * shade(h, 4.0))[..., None], None


def t_bars(seed=67):
    c = col('#0a0808') * np.ones((S, S, 3))
    c += (pfbm(8, 2, seed) * 0.06)[..., None]
    for x in range(4, 64, 10):
        b = np.abs(I - x) < 2.5
        c[b] = col('#3a3a40') * (0.6 + 0.8 * (1 - np.abs(I[b] - x) / 2.5))[:, None] * (0.7 + 0.4 * pnoise(16, seed)[b])[:, None]
    for y in (6, 58):
        b = np.abs(J - y) < 3
        c[b] = col('#2a2a30') * (0.8 + 0.4 * pnoise(16, seed + 1)[b])[:, None]
    rust = pfbm(10, 3, seed + 3) > 0.6
    c[rust & (c.sum(-1) > 0.3)] = col('#5a3018')
    return c, None


def f_water(seed=70):
    n = pfbm(4, 4, seed)
    r = np.sin((I + pfbm(4, 2, seed + 1) * 30) / 64 * 2 * np.pi * 3) * np.sin((J + pfbm(4, 2, seed + 2) * 30) / 64 * 2 * np.pi * 2)
    c = col('#1e3018') * (0.7 + 0.5 * n)[..., None]
    c += (np.clip(r, 0, 1) * 0.08)[..., None] * col('#a0c080')
    scum = pfbm(8, 3, seed + 4) > 0.64
    c[scum] = col('#4a6a20') * (0.7 + 0.4 * pnoise(32, seed)[scum])[:, None]
    return c, None


def f_mud(seed=71):
    n = pfbm(8, 4, seed)
    c = col('#3a2c1a') * (0.6 + 0.6 * n)[..., None]
    pud = pfbm(4, 3, seed + 3) > 0.62
    c[pud] = col('#20180e') + 0.05
    return c * (0.6 + 0.5 * shade(n, 3.0))[..., None], None


def f_marble(seed=72):
    k = ((I // 32) + (J // 32)) % 2
    v = np.abs(np.sin((I + J) / 7 + pfbm(4, 4, seed) * 9))
    a = col('#2a0c10') * (0.6 + 0.5 * v)[..., None]
    b = col('#1a1a1e') * (0.6 + 0.6 * v)[..., None]
    c = np.where((k == 0)[..., None], a, b)
    c[((I % 32) == 0) | ((J % 32) == 0)] *= 0.4
    return c, None


def f_redcarpet(seed=73):
    c = col('#6a0810') * (0.7 + 0.4 * pfbm(16, 3, seed))[..., None]
    w = (np.sin(I * 1.6) * np.sin(J * 1.6)) * 0.05
    c = c * (1 + w)[..., None]
    bd = (np.abs(I - 4) < 2) | (np.abs(I - 59) < 2)
    c[bd] = col('#c09030') * 0.85
    return c, None


def f_labtile(seed=74):
    c = col('#8a9a8a') * (0.75 + 0.3 * pfbm(8, 3, seed))[..., None]
    k = ((I // 16) + (J // 16)) % 2
    c[k == 1] *= 0.75
    c[((I % 16) == 0) | ((J % 16) == 0)] = col('#3a403a')
    goo = pfbm(4, 4, seed + 3) > 0.66
    c[goo] = col('#3a8a2a')
    return c, None


def f_ceilcastle(seed=75):
    c, _ = t_stone(seed, '#2e2c34')
    rib = (np.abs(I - 32) < 3) | (np.abs(J - 32) < 3)
    c[rib] = col('#4a4650') * (0.8 + 0.3 * pnoise(16, seed)[rib])[:, None]
    return c * 0.8, None


# ================================================================== skies

def _sky_base(W, H, top, mid, hor, seed):
    j, i = np.mgrid[0:H, 0:W]
    t = j / (H - 1)
    c = np.where((t < 0.6)[..., None], top + (mid - top) * (t / 0.6)[..., None], mid + (hor - mid) * ((t - 0.6) / 0.4)[..., None])
    rs = np.random.RandomState(seed)
    for k in range(150):
        x, y = rs.randint(0, W), rs.randint(0, int(H * 0.6))
        b = rs.uniform(0.3, 1.0)
        c[y, x] = c[y, x] * (1 - b) + np.array([1, 1, 0.95]) * b
    return c, i, j, rs


def _moon(c, i, j, W, mx, my, mr, mc, halo=26, rs=None):
    d = np.sqrt(((i - mx + W / 2) % W - W / 2) ** 2 + (j - my) ** 2)
    hl = np.clip(1 - (d - mr) / halo, 0, 1) ** 2 * (d >= mr)
    c = c + (mc - c) * (hl * 0.4)[..., None]
    moon = d < mr
    cr = np.zeros(c.shape[:2])
    rs = rs or np.random.RandomState(3)
    for k in range(10):
        cx, cy, rr = mx + rs.uniform(-mr * 0.6, mr * 0.6), my + rs.uniform(-mr * 0.6, mr * 0.6), rs.uniform(mr * 0.1, mr * 0.25)
        cr += np.exp(-((i - cx) ** 2 + (j - cy) ** 2) / (rr * rr)) * 0.25
    c[moon] = mc * (1 - cr[moon])[:, None]
    return c


def sky_carnival(W=512, H=100):
    c, i, j, rs = _sky_base(W, H, col('#04060c'), col('#10182a'), col('#3a2a40'), 21)
    c = _moon(c, i, j, W, 300, 28, 15, col('#c8f0a0'), 30, rs)
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    base = H - 6
    d.rectangle((0, base, W, H), fill=255)
    # ferris wheel
    fx, fy, fr = 120, base - 34, 30
    d.ellipse((fx - fr, fy - fr, fx + fr, fy + fr), outline=255, width=2)
    for k in range(12):
        a = k * math.pi / 6
        d.line((fx, fy, fx + math.cos(a) * fr, fy + math.sin(a) * fr), fill=255)
        d.rectangle((fx + math.cos(a) * fr - 2, fy + math.sin(a) * fr, fx + math.cos(a) * fr + 2, fy + math.sin(a) * fr + 4), fill=255)
    d.polygon([(fx - 14, base), (fx, fy), (fx + 14, base)], outline=255)
    # tents
    for (tx, tw, th) in ((200, 34, 22), (250, 50, 34), (420, 40, 26), (40, 30, 18)):
        d.polygon([(tx - tw, base), (tx, base - th), (tx + tw, base)], fill=255)
        d.line((tx, base - th, tx, base - th - 8), fill=255)
    # roller coaster track
    pts = [(330 + k * 4, base - 10 - 16 * abs(math.sin(k * 0.35))) for k in range(30)]
    d.line(pts, fill=255, width=2)
    for k in range(0, 30, 3):
        d.line((pts[k][0], pts[k][1], pts[k][0], base), fill=255)
    m = np.array(img) > 0
    c[m] = col('#05040a')
    glow = np.ones((H, W), bool)
    # string lights on the tents and wheel
    for k in range(60):
        x = rs.randint(0, W); y = rs.randint(base - 30, base)
        if m[min(y, H - 1), x]:
            c[y, x] = col(['#ff4020', '#ffe040', '#40c0ff', '#60ff60'][k % 4])
    for k in range(12):
        a = k * math.pi / 6
        x, y = int(fx + math.cos(a) * fr), int(fy + math.sin(a) * fr)
        c[max(0, y - 1):y + 1, x:x + 2] = col(['#ff4020', '#ffe040', '#40c0ff'][k % 3])
    return np.clip(c, 0, 1), glow


def sky_castle(W=512, H=100):
    c, i, j, rs = _sky_base(W, H, col('#060410'), col('#1c0e30'), col('#4a2048'), 31)
    c = _moon(c, i, j, W, 170, 36, 19, col('#f4f0e0'), 26, rs)
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    hill = [H - 8 - 10 * abs(math.sin(x / W * math.pi * 3)) for x in range(W)]
    d.polygon([(0, H)] + [(x, hill[x]) for x in range(W)] + [(W - 1, H)], fill=255)
    # castle on the crag
    cx = 330
    cy = int(hill[cx])
    d.rectangle((cx - 40, cy - 30, cx + 40, cy), fill=255)
    for (tx, tw, th) in ((-44, 8, 52), (44, 8, 52), (-14, 6, 44), (16, 9, 66)):
        d.rectangle((cx + tx - tw, cy - th, cx + tx + tw, cy), fill=255)
        d.polygon([(cx + tx - tw - 2, cy - th), (cx + tx, cy - th - 16), (cx + tx + tw + 2, cy - th)], fill=255)
    for k in range(-36, 40, 8):
        d.rectangle((cx + k, cy - 34, cx + k + 4, cy - 30), fill=255)
    m = np.array(img) > 0
    c[m] = col('#06030a')
    for (wx, wy) in ((cx - 30, cy - 18), (cx - 6, cy - 22), (cx + 10, cy - 50), (cx + 30, cy - 14), (cx - 44, cy - 40), (cx + 44, cy - 36)):
        c[wy:wy + 3, wx:wx + 2] = col('#ffb040')
    for k in range(18):
        bx, by = rs.randint(0, W), rs.randint(6, 55)
        for dx in range(-3, 4):
            yy_ = by + (abs(dx) == 1) * -1 + (abs(dx) >= 2) * (abs(dx) - 3)
            if 0 <= yy_ < H:
                c[yy_, (bx + dx) % W] = col('#020104')
    return np.clip(c, 0, 1), np.ones((H, W), bool)


def sky_dawn(W=512, H=100):
    j, i = np.mgrid[0:H, 0:W]
    t = j / (H - 1)
    top, mid, hor = col('#2a3a6a'), col('#c06a6a'), col('#ffc070')
    c = np.where((t < 0.55)[..., None], top + (mid - top) * (t / 0.55)[..., None], mid + (hor - mid) * ((t - 0.55) / 0.45)[..., None])
    sx, sy = 260, 74
    d = np.sqrt((i - sx) ** 2 + ((j - sy) * 1.2) ** 2)
    c = c + (col('#fff0a0') - c) * (np.clip(1 - d / 60, 0, 1) ** 2 * 0.6)[..., None]
    c[d < 13] = col('#fff4c0')
    rs = np.random.RandomState(41)
    for k in range(9):
        cy = rs.uniform(15, 60); cx = rs.uniform(0, W); ln = rs.uniform(40, 120)
        m = (np.abs(j - cy) < 3 + 2 * np.sin((i - cx) / 9)) & (((i - cx) % W) < ln)
        c[m] = c[m] * 0.6 + col('#ffb0a0') * 0.4
    img = Image.new('L', (W, H), 0)
    dd = ImageDraw.Draw(img)
    base = H - 6
    dd.rectangle((0, base, W, H), fill=255)
    for x0 in range(0, W, 46):
        hw = 14 + (x0 * 7) % 9
        hh = 14 + (x0 * 3) % 10
        dd.rectangle((x0 + 4, base - hh, x0 + 4 + hw * 2, base), fill=255)
        dd.polygon([(x0, base - hh), (x0 + 4 + hw, base - hh - 12), (x0 + 8 + hw * 2, base - hh)], fill=255)
    m = np.array(img) > 0
    c[m] = col('#1a1020')
    return np.clip(c, 0, 1), np.ones((H, W), bool)


WALLS2 = [
    ('shop', lambda: t_shop(40, 'CANDY', '#ffb040')), ('shop2', lambda: t_shop(54, 'DINER', '#a0e0ff')), ('siding', t_siding),
    ('siding2', lambda: t_siding(55, '#6a4a5a')), ('tent', t_tent), ('tent2', lambda: t_tent(56, '#3a2a80', '#d0b040')),
    ('booth', t_booth), ('mirror', t_mirror), ('funwall', t_funwall), ('clownwall', t_clownwall), ('lightwall', t_lightwall),
    ('bigtop', t_bigtop), ('poster', t_poster),
    ('castle', t_castle), ('curtain', t_curtain), ('tapestry', t_tapestry), ('labwall', t_labwall), ('machine', t_machine),
    ('swampwood', t_swampwood), ('rockmoss', t_rockmoss), ('bars', t_bars),
]
FLATS2 = [
    ('asphalt', f_asphalt), ('sidewalk', f_sidewalk), ('sawdust', f_sawdust), ('ceiltent', f_ceiltent),
    ('water', f_water), ('mud', f_mud), ('marble', f_marble), ('redcarpet', f_redcarpet), ('labtile', f_labtile),
    ('ceilcastle', f_ceilcastle),
]
SKIES2 = [('sky2', sky_carnival), ('sky3', sky_castle), ('sky4', sky_dawn)]
