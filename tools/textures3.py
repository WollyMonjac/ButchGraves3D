"""Episode 4 (Halloween 2099) textures: tech walls, conveyor belts, shock floors, shifting maze walls, levers, neon city sky.
Each returns (rgb float SxSx3, glow bool SxS)."""
import math
import numpy as np
from PIL import Image, ImageDraw
from textures import S, _h, pnoise, pfbm, shade, col, grime
from textures2 import text_mask, BLACKOPS, _sky_base, _moon

J, I = np.mgrid[0:S, 0:S]
Z = lambda: np.zeros((S, S), bool)


def metal_panels(seed, base, ph=32, pw=32, rivets=True, bevel=0.35):
    """Brushed metal panels with bevelled seams and rivets."""
    u, v = I % pw, J % ph
    ed = np.minimum(np.minimum(u, pw - 1 - u), np.minimum(v, ph - 1 - v))
    pid = (I // pw) * 7 + (J // ph) * 13
    rnd = _h(pid, pid * 3, seed)
    brush = pnoise(4, seed, sx=2, sy=40) * 0.15
    h = np.clip(ed / 3.0, 0, 1) + brush
    c = col(base)[None, None, :] * (0.78 + 0.3 * rnd)[..., None] * (0.85 + 0.25 * pfbm(8, 3, seed + 1))[..., None]
    c = c * (0.62 + 0.55 * shade(h, 2.0))[..., None]
    c[ed == 0] *= 0.35
    if rivets:
        for (x, y) in ((3, 3), (pw - 4, 3), (3, ph - 4), (pw - 4, ph - 4)):
            r = ((u - x) ** 2 + (v - y) ** 2) < 2.2
            c[r] = col('#c8ccd0') * 0.9
            c[r & ((u - x) + (v - y) > 0)] *= 0.55
    return c


def t_techwall(seed=80):
    c = metal_panels(seed, '#5a6470')
    glow = Z()
    strip = (J >= 28) & (J < 32)
    c[strip] = col('#1a1e24')
    lit = strip & (J >= 29) & (J < 31) & ((I % 16) < 13)
    c[lit] = col('#60f0ff')
    glow |= lit
    return grime(c, seed, 0.35), glow


def t_techwall2(seed=81):
    c = metal_panels(seed, '#3c4048', 16, 32)
    glow = Z()
    vent = (J >= 40) & (J < 56) & (I >= 8) & (I < 56)
    c[vent] = col('#141618')
    slats = vent & ((J % 3) == 0)
    c[slats] = col('#4a5058')
    for x in (12, 52):
        lamp = ((I - x) ** 2 + (J - 12) ** 2) < 7
        c[lamp] = col('#ff7020'); glow |= lamp
    return grime(c, seed, 0.5), glow


def t_circuit(seed=82):
    c = col('#0c2a18') * (0.75 + 0.4 * pfbm(8, 3, seed))[..., None]
    glow = Z()
    rs = np.random.RandomState(seed)
    img = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(img)
    nodes = []
    for k in range(14):
        x, y = rs.randint(2, 62), rs.randint(2, 62)
        nodes.append((x, y))
        x2 = x + rs.choice([-1, 1]) * rs.randint(6, 22)
        y2 = y + rs.choice([-1, 1]) * rs.randint(6, 22)
        d.line((x, y, x2, y), fill=255)
        d.line((x2, y, x2, y2), fill=255)
        nodes.append((x2, y2))
    m = np.array(img) > 0
    m |= np.roll(m, 32, 1) & (pnoise(4, seed + 3) > 0.6)
    c[m] = col('#c08a3a')
    for k, (x, y) in enumerate(nodes):
        nd = ((I - x) ** 2 + (J - y) ** 2) < 3.5
        if k % 3 == 0:
            c[nd] = col('#60ff80'); glow |= nd
        else:
            c[nd] = col('#e0c070')
    chip = (I >= 22) & (I < 42) & (J >= 22) & (J < 38)
    c[chip] = col('#18181c') * (0.9 + 0.2 * pnoise(16, seed + 5)[chip])[:, None]
    for x in range(23, 42, 3):
        c[(np.abs(I - x) < 1) & ((J == 20) | (J == 21) | (J == 38) | (J == 39))] = col('#c0c0c0')
    return c, glow


def t_neonwall(seed=83):
    from textures import t_brick
    c, _ = t_brick(seed, '#2a2a3a')
    c *= 0.7
    glow = Z()
    m = Z()
    m[6:22, 2:62] = text_mask('FRANKEN', 60, 16, BLACKOPS, 14)
    m2 = Z()
    m2[24:36, 8:56] = text_mask('TECH', 48, 12, BLACKOPS, 12)
    outline = lambda mm: (np.roll(mm, 1, 0) | np.roll(mm, -1, 0) | np.roll(mm, 1, 1) | np.roll(mm, -1, 1)) & ~mm
    c[outline(m)] = col('#ff40c0'); glow |= outline(m)
    c[outline(m2)] = col('#40f0ff'); glow |= outline(m2)
    # neon pumpkin
    r = np.sqrt((I - 32) ** 2 / 1.3 + (J - 49) ** 2)
    ring = np.abs(r - 9) < 1.0
    c[ring] = col('#ff9020'); glow |= ring
    for s in (-1, 1):
        e = (np.abs(I - 32 - s * 4) + np.abs(J - 47) * 1.5) < 2.2
        c[e] = col('#ff9020'); glow |= e
    mouth = (np.abs(J - 52) < 1) & (np.abs(I - 32) < 5)
    c[mouth] = col('#ff9020'); glow |= mouth
    return c, glow


def t_server(seed=84, purple=False):
    c = col('#16181c') * (0.8 + 0.3 * pfbm(8, 2, seed))[..., None]
    glow = Z()
    rs = np.random.RandomState(seed)
    unit = J // 8
    sep = (J % 8) == 0
    c[sep] = col('#2c3038')
    rails = (I < 4) | (I >= 60)
    c[rails] = col('#3a3e46')
    holes = rails & ((J % 4) == 2) & ((I == 1) | (I == 62))
    c[holes] = col('#0a0a0a')
    for u in range(8):
        y = u * 8 + 4
        for k in range(6):
            x = 8 + k * 4
            led = (np.abs(I - x) < 1) & (np.abs(J - y) < 1)
            if rs.rand() < 0.6:
                c[led] = col(['#40ff60', '#ffb020', '#40c0ff'][rs.randint(3)]); glow |= led
            else:
                c[led] = col('#203020')
        slot = (J >= y - 2) & (J <= y + 1) & (I >= 34) & (I < 56)
        c[slot] = col('#08080a')
        c[slot & ((I % 3) == 0)] = col('#24282e')
    if purple:          # shifting walls: marked by a purple frame and arrows so the player learns to spot them
        fr = (I < 3) | (I >= 61) | (J < 3) | (J >= 61)
        c[fr] = col('#b040ff'); glow |= fr
        for y0 in (20, 40):
            ar = (np.abs(I - 32) < (J - y0) * 0.9 + 1) & (J >= y0) & (J < y0 + 7)
            c[ar] = col('#d080ff'); glow |= ar
    return c, glow


def t_hazard(seed=85):
    c = metal_panels(seed, '#4a4c50', 32, 64, rivets=False)
    band = J >= 40
    st = ((I + J) // 8) % 2 == 0
    c[band & st] = col('#e8b818') * (0.8 + 0.3 * pnoise(16, seed)[band & st])[:, None]
    c[band & ~st] = col('#141414')
    c[J == 40] = col('#2a2a2a')
    return grime(c, seed + 1, 0.6), None


def t_glasstank(seed=86):
    c = metal_panels(seed, '#3a4048', 64, 64, rivets=False)
    glow = Z()
    win = (I >= 10) & (I < 54) & (J >= 6) & (J < 58)
    fluid = col('#30d060') * (0.6 + 0.5 * pfbm(4, 3, seed + 2))[..., None]
    c[win] = fluid[win]
    glow |= win
    body = (((I - 32) / 7.0) ** 2 + ((J - 20) / 7.5) ** 2 < 1) | ((((I - 32) / 10.0) ** 2 + ((J - 38) / 13.0) ** 2) < 1) \
        | ((np.abs(np.abs(I - 32) - 5) < 3) & (J > 46) & (J < 58))
    c[body & win] = col('#0a2a14')
    eyes = ((np.abs(I - 32) - 3) ** 2 + (J - 19) ** 2 * 3) < 2
    c[eyes] = col('#ff4020')
    for k in range(6):
        b = ((I - 14 - k * 6) ** 2 + (J - 50 + k * 7 % 40) ** 2) < 2
        c[b & win] = col('#c0ffc8')
    frame = win & ((I < 12) | (I >= 52) | (J < 8) | (J >= 56))
    c[frame] = col('#5a6068'); glow &= ~frame
    glint = win & (np.abs((I - 18) - (J - 10) * 0.3) < 1.2) & (J < 40)
    c[glint] = col('#e0fff0')
    return c, glow


def t_monitors(seed=87):
    c = col('#202428') * (0.8 + 0.3 * pfbm(8, 2, seed))[..., None]
    glow = Z()
    for (x0, y0, kind) in ((3, 4, 0), (33, 4, 1), (3, 34, 2), (33, 34, 0)):
        scr = (I >= x0 + 2) & (I < x0 + 26) & (J >= y0 + 2) & (J < y0 + 24)
        bez = (I >= x0) & (I < x0 + 28) & (J >= y0) & (J < y0 + 26) & ~scr
        c[bez] = col('#3a3e44')
        lines = ((J - y0) % 2) == 0
        if kind == 0:            # jack-o-lantern face
            base = col('#103018')
            c[scr] = base
            cx, cy = x0 + 14, y0 + 13
            e = scr & ((np.abs(I - cx + 5) + np.abs(J - cy + 3) < 3) | (np.abs(I - cx - 5) + np.abs(J - cy + 3) < 3)
                       | ((np.abs(J - cy - 4) < 2) & (np.abs(I - cx) < 7) & ((I % 3) != 0)))
            c[e] = col('#60ff70')
        elif kind == 1:          # oscilloscope
            c[scr] = col('#081820')
            wave = scr & (np.abs(J - (y0 + 13 + 6 * np.sin((I - x0) * 0.6))) < 1.0)
            c[wave] = col('#60e0ff')
        else:                    # skull x-ray
            c[scr] = col('#0a1010')
            sk = scr & ((((I - x0 - 14) / 6.0) ** 2 + ((J - y0 - 11) / 7.0) ** 2) < 1)
            c[sk] = col('#a0e0e0')
            for s in (-1, 1):
                c[scr & (((I - x0 - 14 - s * 2.5) ** 2 + (J - y0 - 11) ** 2) < 2.5)] = col('#0a1010')
        c[scr & lines] *= 0.7
        glow |= scr
    return c, glow


def t_switch(seed=88, down=False):
    c = metal_panels(seed, '#4a5058', 64, 64)
    glow = Z()
    plate = (I >= 18) & (I < 46) & (J >= 10) & (J < 54)
    c[plate] = col('#2a2c30') * (0.9 + 0.2 * pnoise(16, seed + 1)[plate])[:, None]
    slot = (np.abs(I - 32) < 2) & (J >= 16) & (J < 48)
    c[slot] = col('#08080a')
    ky = 44 if down else 20
    arm = (np.abs(I - 32) < 2) & (J >= min(32, ky)) & (J <= max(32, ky))
    c[arm] = col('#a0a4a8')
    knob = ((I - 32) ** 2 + (J - ky) ** 2) < 14
    c[knob] = col('#d02010') if not down else col('#20c040')
    c[knob & ((I - 32) + (J - ky) < -2)] *= 1.4
    light = ((I - 32) ** 2 + (J - 6) ** 2) < 6
    c[light] = col('#ff3020') if not down else col('#40ff60')
    glow |= light
    st = (J >= 56) & ((((I + J) // 4) % 2) == 0)
    c[st] = col('#e8b818')
    c[(J >= 56) & ~st] = col('#151515')
    return c, glow


def t_techdoor(seed=89):
    c = metal_panels(seed, '#6a7078', 64, 32, rivets=False)
    glow = Z()
    st = ((J < 8) | (J >= 56)) & ((((I + J) // 6) % 2) == 0)
    c[(J < 8) | (J >= 56)] = col('#151515')
    c[st] = col('#e8b818')
    win = (I >= 22) & (I < 42) & (J >= 14) & (J < 30)
    c[win] = col('#40c8e0') * (0.7 + 0.3 * (1 - (J - 14) / 16.0))[..., None][win]
    glow |= win
    c[(np.abs(I - 32) < 1) & (J >= 8) & (J < 56)] = col('#202428')
    for y in (40, 46):
        c[(J == y) & (I > 8) & (I < 56)] *= 0.5
    return c, glow


# ------------------------------------------------------------------ flats

def f_plate(seed=90):
    c = col('#5a5e64') * (0.78 + 0.3 * pfbm(8, 3, seed))[..., None]
    a = ((I % 8) - 4) * 0.7 + ((J % 8) - 4)
    b = ((I % 8) - 4) * 0.7 - ((J % 8) - 4)
    dia = ((np.abs(a) < 1.2) & ((I // 8 + J // 8) % 2 == 0)) | ((np.abs(b) < 1.2) & ((I // 8 + J // 8) % 2 == 1))
    c[dia] *= 1.35
    c[((I % 32) == 0) | ((J % 32) == 0)] *= 0.45
    return grime(c, seed, 0.4), None


def f_grate(seed=91):
    c = col('#3a3e44') * (0.8 + 0.3 * pfbm(8, 2, seed))[..., None]
    hole = ((I % 6) >= 2) & ((J % 6) >= 2)
    c[hole] = col('#0c0e10') * (0.6 + 0.6 * pnoise(8, seed + 2)[hole])[:, None]
    glow = hole & (pnoise(4, seed + 5) > 0.72)
    c[glow] = col('#30ff60') * 0.6
    c[((I % 32) == 0) | ((J % 32) == 0)] = col('#5a6068')
    return c, glow


def conveyor(direction):
    """Belt with chevrons pointing along the travel direction (n: -y, s: +y, e: +x, w: -x), rollers at the sides."""
    c = col('#202224') * (0.8 + 0.3 * pnoise(16, 92, sx=4, sy=32))[..., None]
    glow = Z()
    # chevrons pointing up (north) in a 16-texel cycle, 4 columns wide
    v = J % 16
    u = np.abs((I % 32) - 16)
    chev = (np.abs(v - 4 - u * 0.5) < 2.0) & (u < 11) & (I >= 4) & (I < 60)
    c[chev] = col('#f0c020')
    c[chev & (np.abs(v - 4 - u * 0.5) < 0.8)] = col('#ffe060')
    side = (I < 4) | (I >= 60)
    c[side] = col('#5a5e64') * (0.7 + 0.4 * ((J % 4) < 2))[side][:, None]
    c[(J % 8) == 0] *= 0.7
    if direction == 's':
        c, glow = c[::-1], glow[::-1]
    elif direction == 'e':
        c, glow = np.rot90(c, -1).copy(), np.rot90(glow, -1).copy()
    elif direction == 'w':
        c, glow = np.rot90(c, 1).copy(), np.rot90(glow, 1).copy()
    return c, glow


def f_shock(seed=93, on=True):
    c = col('#2a3038') * (0.8 + 0.3 * pfbm(8, 2, seed))[..., None]
    glow = Z()
    grid = ((I % 16) < 2) | ((J % 16) < 2)
    c[grid] = col('#101418')
    if on:
        rs = np.random.RandomState(seed)
        img = Image.new('L', (S, S), 0)
        d = ImageDraw.Draw(img)
        for k in range(7):
            x, y = rs.randint(0, 64), rs.randint(0, 64)
            pts = [(x, y)]
            for s in range(6):
                x += rs.randint(-8, 9); y += rs.randint(-8, 9)
                pts.append((x, y))
            d.line(pts, fill=255, width=1)
        m = np.array(img) > 0
        halo = (np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)) & ~m
        c[halo] = col('#3070ff')
        c[m] = col('#e0f4ff')
        c[grid] = col('#40a0ff')
        glow |= m | halo | grid
    else:
        c[grid] = col('#1a2a40')
    # yellow warning border corners
    st = ((I < 3) | (I >= 61) | (J < 3) | (J >= 61)) & ((((I + J) // 4) % 2) == 0)
    c[st] = col('#e8b818')
    return c, glow


def f_techceil(seed=94):
    c = metal_panels(seed, '#3a3e44', 32, 32)
    glow = Z()
    lamp = (I >= 8) & (I < 24) & (J >= 8) & (J < 24)
    c[lamp] = col('#d8f0ff')
    glow |= lamp
    return c, glow


def f_darkceil(seed=95):
    c = col('#1c1e22') * (0.8 + 0.3 * pfbm(8, 2, seed))[..., None]
    for y in (10, 30, 50):
        p = np.abs(J - y) < 4
        c[p] = col('#4a4e56') * (0.5 + 0.7 * (1 - np.abs(J[p] - y) / 4.0))[:, None]
    for x in (0, 32):
        c[(np.abs(I - x) < 2)] = col('#2a2c30')
    return c, None


def f_shiftflr(seed=96):
    c, _ = f_plate(seed)
    c = c * 0.8
    glow = Z()
    fr = (I < 3) | (I >= 61) | (J < 3) | (J >= 61)
    st = fr & ((((I + J) // 4) % 2) == 0)
    c[st] = col('#9030e0')
    glow |= st
    return c, glow


# ------------------------------------------------------------------ sky: Neo-Hollow skyline

def sky_neon(W=512, H=100):
    c, i, j, rs = _sky_base(W, H, col('#05030c'), col('#1a0a30'), col('#4a1050'), 51)
    c = _moon(c, i, j, W, 380, 26, 13, col('#d0ffe0'), 24, rs)
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    base = H - 4
    d.rectangle((0, base, W, H), fill=255)
    tops = []
    x = 0
    while x < W:
        bw = rs.randint(10, 26)
        bh = rs.randint(14, 52)
        if rs.rand() < 0.15:
            bh += 20
        d.rectangle((x, base - bh, x + bw, base), fill=255)
        if rs.rand() < 0.3:
            d.line((x + bw // 2, base - bh, x + bw // 2, base - bh - 8), fill=255)
        tops.append((x, bw, bh))
        x += bw + rs.randint(0, 4)
    m = np.array(img) > 0
    c[m] = col('#07050e')
    glow = np.ones((H, W), bool)
    # lit windows and neon roof trims
    for (x0, bw, bh) in tops:
        for yy in range(base - bh + 3, base - 2, 3):
            for xx in range(x0 + 2, x0 + bw - 1, 3):
                if rs.rand() < 0.35:
                    c[yy, xx % W] = col(['#ffd060', '#60e0ff', '#ff60c0', '#a0ff80'][rs.randint(4)]) * rs.uniform(0.5, 1.0)
        if rs.rand() < 0.5:
            c[base - bh, x0:min(W, x0 + bw + 1)] = col(['#ff40c0', '#40f0ff', '#b060ff'][rs.randint(3)])
    # flying car tail lights
    for k in range(14):
        xx, yy = rs.randint(0, W), rs.randint(20, 60)
        c[yy, xx:xx + 2] = col('#ff4040')
    return np.clip(c, 0, 1), glow


WALLS3 = [('techwall', t_techwall), ('techwall2', t_techwall2), ('circuit', t_circuit), ('neonwall', t_neonwall),
          ('server', t_server), ('shiftwall', lambda: t_server(97, True)), ('hazard', t_hazard), ('glasstank', t_glasstank),
          ('monitors', t_monitors), ('switch', t_switch), ('switch2', lambda: t_switch(88, True)), ('techdoor', t_techdoor)]
FLATS3 = [('plate', f_plate), ('grate', f_grate), ('conv_n', lambda: conveyor('n')), ('conv_s', lambda: conveyor('s')),
          ('conv_e', lambda: conveyor('e')), ('conv_w', lambda: conveyor('w')), ('shock', f_shock), ('shockoff', lambda: f_shock(93, False)),
          ('techceil', f_techceil), ('darkceil', f_darkceil), ('shiftflr', f_shiftflr)]
SKIES3 = [('sky5', sky_neon)]
