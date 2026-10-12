"""Episode 4 (Halloween 2099) robots: SDF models. Feet at y=0, facing +z. 1 unit = wall height."""
import numpy as np
from sdf import *
from monsters import limb, cloth, tilt_scene, TriPrism, Pumpkin, pumpkin_mat, jack_face, fire_mat, rot_skin, BONE, TEETH, MOUTH, \
    BLOOD, BLACK, EYE_RED, EYE_GRN, FIRE
from monsters2 import V, OLD_BONE, STEEL, GOLD, FANG, GLOSS_RED, RUST

# ------------------------------------------------------------------ materials
def metal(base=(0.45, 0.5, 0.48), seed=0, var=0.25, spec=0.9):
    base = np.asarray(base)

    def fn(p, n):
        v = fbm(p, 14, 3, seed)
        c = base[None, :] * (0.65 + 0.55 * v)[:, None]
        scr = (np.abs(fbm(p * V(1, 4, 1), 40, 1, seed + 3) - 0.5) < 0.02)
        c[scr] *= 1.3
        return c * (0.75 + 0.35 * np.clip(n[:, 1] * 0.5 + 0.6, 0, 1))[:, None]
    return Mat(fn=fn, spec=spec, shin=35)


GUNMETAL = metal((0.3, 0.32, 0.36), 301)
GREENMETAL = metal((0.36, 0.5, 0.36), 302)
CHROME = metal((0.7, 0.72, 0.78), 303, spec=1.4)
COPPER = Mat((0.78, 0.42, 0.2), var=0.2, vfreq=40, spec=1.0, shin=40)
HAZARD = Mat(fn=lambda p, n: np.where((np.sin((p[:, 0] + p[:, 1]) * 90) > 0)[:, None], np.array([[0.95, 0.75, 0.1]]),
                                      np.array([[0.08, 0.08, 0.08]])), spec=0.5)
ZAPGLOW = Mat((0.55, 0.85, 1.0), glow=1.0)
ZAPCORE = fire_mat((1.0, 1.0, 1.0), (0.5, 0.85, 1.0), (0.1, 0.3, 1.0), seed=31)
EYE_CYAN = Mat((0.4, 1.0, 1.0), glow=1.0)
NEON_GRN = Mat((0.45, 1.0, 0.35), glow=1.0)
RUBBER = Mat((0.07, 0.07, 0.08), var=0.2, vfreq=40, spec=0.4)


def bolt_pair(ps, c, r, glowmat=NEON_GRN):
    """Frankenstein neck bolts, glowing at the tips."""
    for s in (-1, 1):
        a = c + V(s * r, 0, 0)
        b = a + V(s * 0.05, 0, 0)
        ps.append(P(Cyl((a + b) / 2, 0.018, 0.026, R=rot(0, 0, np.pi / 2)), CHROME, 0.004))
        ps.append(P(Sphere(b + V(s * 0.006, 0, 0), 0.014), glowmat, 0.0))


# ------------------------------------------------------------------ FRANKEN-BOT

def frankbot(pose='walk1'):
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.46
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.09, hip_y, 0)
        kn = hip + V(s * 0.015, -0.22, 0.05 * ls + 0.02)
        an = kn + V(0, -0.2, -0.03 * ls)
        limb(ps, hip, kn, 0.06, 0.055, GUNMETAL, 0.02)
        ps.append(P(Sphere(kn, 0.06), CHROME, 0.01))
        limb(ps, kn, an, 0.055, 0.05, GREENMETAL, 0.02)
        ps.append(P(Box(an + V(0, -0.03, 0.04), (0.06, 0.035, 0.1), r=0.015), RUBBER, 0.01))
    ps.append(P(Box(V(0, hip_y + 0.05, 0), (0.14, 0.07, 0.09), r=0.03), GUNMETAL, 0.03))
    ch = V(0, hip_y + 0.3, 0.0)
    ps.append(P(Box(ch, (0.21, 0.18, 0.13), r=0.05), GREENMETAL, 0.05))
    # chest vents and a glowing reactor gauge
    for k in range(3):
        ps.append(P(Box(ch + V(-0.09, 0.06 - k * 0.045, 0.125), (0.05, 0.008, 0.01)), BLACK, 0.0))
    ps.append(P(Cyl(ch + V(0.07, 0.02, 0.12), 0.05, 0.012, R=rot(np.pi / 2, 0, 0)), CHROME, 0.0))
    ps.append(P(Cyl(ch + V(0.07, 0.02, 0.13), 0.036, 0.01, R=rot(np.pi / 2, 0, 0)), NEON_GRN, 0.0))
    ps.append(P(Box(ch + V(0, -0.14, 0.13), (0.12, 0.02, 0.01)), HAZARD, 0.0))
    # tesla coil shoulders
    for s in (-1, 1):
        sh = ch + V(s * 0.23, 0.12, -0.02)
        ps.append(P(Sphere(sh, 0.09), GUNMETAL, 0.03))
        limb(ps, sh + V(0, 0.05, -0.03), sh + V(s * 0.03, 0.2, -0.05), 0.02, 0.016, COPPER, 0.0)
        for k in range(3):
            ps.append(P(Torus(sh + V(s * 0.012, 0.09 + k * 0.035, -0.04), 0.028, 0.007), COPPER, 0.0))
        ps.append(P(Sphere(sh + V(s * 0.035, 0.22, -0.05), 0.025), ZAPGLOW, 0.0))
    # flat-topped Frankenstein head, welded seams, neck bolts
    hc = ch + V(0, 0.27, 0.02)
    if pose == 'pain':
        hc = hc + V(0.04, -0.01, -0.03)
    limb(ps, ch + V(0, 0.15, 0), hc - V(0, 0.06, 0), 0.05, 0.05, GUNMETAL, 0.02)
    ps.append(P(Box(hc, (0.085, 0.1, 0.085), r=0.025), GREENMETAL, 0.0))
    ps.append(P(Box(hc + V(0, 0.095, 0), (0.09, 0.012, 0.09), r=0.005), GUNMETAL, 0.005))      # flat top
    ps.append(P(Box(hc + V(0, 0.035, 0.08), (0.08, 0.014, 0.014), r=0.006), GUNMETAL, 0.006))  # heavy brow
    for s in (-1, 1):
        ps.append(P(Box(hc + V(s * 0.035, 0.012, 0.083), (0.022, 0.006, 0.006)), EYE_GRN, 0.0))
    mo = 0.02 if pose == 'attack' else 0.008
    ps.append(P(Box(hc + V(0, -0.05, 0.08), (0.05, 0.008 + mo, 0.012)), BLACK, 0.003, op='sub'))
    for k in range(5):
        ps.append(P(Box(hc + V((k - 2) * 0.02, -0.05, 0.08), (0.004, 0.012 + mo, 0.006)), CHROME, 0.0))
    ps.append(P(Box(hc + V(0.0, 0.06, 0.086), (0.06, 0.003, 0.003), R=rot(0, 0, 0.1)), BLACK, 0.0))           # seam
    for k in range(4):
        ps.append(P(Box(hc + V(-0.04 + k * 0.027, 0.06, 0.088), (0.002, 0.008, 0.003)), CHROME, 0.0))      # staples
    bolt_pair(ps, hc + V(0, -0.07, 0), 0.07)
    # arms with clamp hands
    shl, shr = ch + V(-0.25, 0.08, 0), ch + V(0.25, 0.08, 0)
    if pose == 'attack':
        hl, hr = shl + V(0.08, 0.05, 0.3), shr + V(-0.08, 0.05, 0.3)
    elif pose == 'pain':
        hl, hr = shl + V(-0.12, 0.1, 0.06), shr + V(0.14, -0.05, 0.06)
    else:
        hl, hr = shl + V(-0.03, -0.3 + 0.03 * sw, 0.12), shr + V(0.03, -0.3 - 0.03 * sw, 0.12)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.05, -0.04, -0.03)
        limb(ps, sh, el, 0.055, 0.05, GUNMETAL, 0.02)
        ps.append(P(Sphere(el, 0.05), CHROME, 0.01))
        limb(ps, el, hd, 0.05, 0.045, GREENMETAL, 0.02)
        d = norm(hd - el)
        ps.append(P(Box(hd + d * 0.03, (0.05, 0.05, 0.05), r=0.015), GUNMETAL, 0.01))
        for f in (-1, 1):
            limb(ps, hd + d * 0.05 + V(f * 0.03, 0, 0), hd + d * 0.12 + V(f * 0.035, -0.02, 0), 0.016, 0.012, CHROME, 0.004)
    if pose == 'attack':
        ps.append(P(Sphere((hl + hr) / 2 + V(0, 0.02, 0.06), 0.07), ZAPCORE, 0.0, disp=(0.015, 20, 5)))
    return ps


# ------------------------------------------------------------------ JACK-O-DRONE

def drone(pose='walk1'):
    ps = []
    c = V(0, 0.16, 0)
    tilt = {'pain': 0.6, 'attack': 0.15}.get(pose, 0.32)
    pk = pumpkin_mat((0.95, 0.45, 0.08), seed=311)
    ps.append(P(Pumpkin(c, 0.125, squash=0.85, ribs=10, amp=0.07), pk, 0.0))
    jack_face(ps, c, 0.125, fierce=1.6, glowmat=Mat((1.0, 0.15, 0.08), glow=1.0), mouth_open=1.4 if pose == 'attack' else 0.9)
    # metal skull cap with an antenna
    ps.append(P(Ellipsoid(c + V(0, 0.07, -0.01), (0.07, 0.03, 0.07)), GUNMETAL, 0.01))
    limb(ps, c + V(0.02, 0.09, -0.02), c + V(0.04, 0.17, -0.03), 0.004, 0.003, CHROME, 0.0)
    ps.append(P(Sphere(c + V(0.04, 0.175, -0.03), 0.01), Mat((1.0, 0.2, 0.2), glow=1.0), 0.0))
    # four rotor arms (blurred discs)
    ph = 0.4 if pose == 'walk2' else 0.0
    for k in range(4):
        a = k * np.pi / 2 + np.pi / 4 + ph
        e = c + V(np.cos(a) * 0.2, 0.07, np.sin(a) * 0.13)
        limb(ps, c + V(np.cos(a) * 0.07, 0.05, np.sin(a) * 0.05), e, 0.01, 0.008, GUNMETAL, 0.004)
        ps.append(P(Cyl(e + V(0, 0.02, 0), 0.08, 0.005), Mat((0.55, 0.55, 0.6), var=0.3, vfreq=30, spec=0.6), 0.0))
        ps.append(P(Cyl(e + V(0, 0.01, 0), 0.012, 0.012), CHROME, 0.0))
    # laser cannon under the chin
    lc = c + V(0, -0.1, 0.04)
    limb(ps, c + V(0, -0.07, 0.0), lc, 0.02, 0.016, GUNMETAL, 0.006)
    limb(ps, lc, lc + V(0, -0.01, 0.06), 0.012, 0.01, CHROME, 0.0)
    ps.append(P(Sphere(lc + V(0, -0.01, 0.07), 0.018 if pose == 'attack' else 0.009), Mat((1.0, 0.2, 0.15), glow=1.0), 0.0))
    from weapons import transform
    return transform(ps, rot(tilt, 0, tilt * 0.6), c)


# ------------------------------------------------------------------ CYBER-GHOUL (zombie + machinery)

def cyborg(pose='walk1'):
    import monsters as M
    ps = M.zombie(pose)
    hip_y = 0.40
    ph = {'walk1': 0.0, 'walk2': 1.0, 'attack': 0.5, 'pain': 0.5}.get(pose, 0.5)
    sw = (ph - 0.5) * 2
    lean = 0.06 if pose != 'pain' else -0.05
    chest = V(0.0, hip_y + 0.22, lean)
    neck = chest + V(0.0, 0.07, 0.01)
    hc = neck + V(0.015, 0.075, 0.03 + lean * 0.4)
    if pose == 'pain':
        hc = hc + V(0.04, -0.01, -0.04)
    # steel jaw plate, cyber eye, cables to a back pack
    ps.append(P(Box(hc + V(0, -0.055, 0.035), (0.042, 0.022, 0.03), r=0.01), CHROME, 0.006))
    ps.append(P(Cyl(hc + V(-0.026, 0.006, 0.058), 0.018, 0.008, R=rot(np.pi / 2, 0, 0)), GUNMETAL, 0.0))
    ps.append(P(Sphere(hc + V(-0.026, 0.006, 0.064), 0.011), Mat((1.0, 0.1, 0.05), glow=1.0), 0.0))
    ps.append(P(Box(chest + V(0, 0.0, -0.1), (0.08, 0.1, 0.04), r=0.015), GUNMETAL, 0.01))
    for s in (-1, 1):
        limb(ps, hc + V(s * 0.05, -0.02, -0.03), chest + V(s * 0.05, 0.08, -0.1), 0.007, 0.007, RUBBER, 0.003)
    # steel skull plate with rivets
    ps.append(P(Ellipsoid(hc + V(0.0, 0.035, -0.005), (0.058, 0.04, 0.058)), CHROME, 0.006))
    for k in range(5):
        a = -1.2 + k * 0.6
        ps.append(P(Sphere(hc + V(np.sin(a) * 0.05, 0.03, np.cos(a) * 0.05), 0.006), GUNMETAL, 0.0))
    # chainsaw arm held out in front, angled so it reads from the front
    sh_r = chest + V(0.12, 0.04, -0.01)
    if pose == 'attack':
        hr, d = sh_r + V(0.05, 0.16, 0.1), norm(V(-0.15, 0.85, 0.5))
    elif pose == 'pain':
        hr, d = sh_r + V(0.1, -0.16, 0.02), norm(V(0.5, -0.8, 0.2))
    else:
        hr, d = sh_r + V(0.06, -0.1 - 0.02 * sw, 0.12), norm(V(0.55, -0.25, 0.75))
    limb(ps, sh_r, hr, 0.035, 0.03, GUNMETAL, 0.01)
    up = norm(np.cross(d, V(0, 0, 1)) + V(0, 1e-3, 0)) if abs(d[2]) < 0.9 else V(0, 1, 0)
    side = norm(np.cross(d, up)); up = norm(np.cross(side, d))
    R = np.stack([side, up, d], 1)
    ps.append(P(Box(hr + d * 0.02, (0.04, 0.045, 0.055), R=R, r=0.012), HAZARD, 0.01))
    bar0, bar1 = hr + d * 0.06, hr + d * 0.3
    ps.append(P(Box((bar0 + bar1) / 2, (0.008, 0.03, 0.12), R=R, r=0.006), CHROME, 0.0))
    ps.append(P(Cyl(bar1, 0.03, 0.009, R=R @ rot(0, 0, np.pi / 2)), CHROME, 0.004))
    nb = 11
    for k in range(nb):
        t = k / (nb - 1)
        p = bar0 + (bar1 - bar0) * t
        for sg in (-1, 1):
            ps.append(P(Cone(p + up * sg * 0.028, p + up * sg * 0.042 + d * 0.008, 0.007, 0.001), STEEL, 0.0))
    return ps


# ------------------------------------------------------------------ SKULL-SPIDER

def spider(pose='walk1'):
    ps = []
    c = V(0, 0.13, 0)
    if pose == 'pain':
        c = c + V(0.02, 0.02, -0.02)
    ps.append(P(Ellipsoid(c + V(0, -0.01, -0.06), (0.09, 0.05, 0.1)), GUNMETAL, 0.02))
    ps.append(P(Ellipsoid(c + V(0, 0.03, -0.12), (0.06, 0.04, 0.06)), HAZARD, 0.02))
    # skull riding on top, red eye glow
    sc = c + V(0, 0.07, 0.05)
    ps.append(P(Ellipsoid(sc, (0.06, 0.06, 0.065)), OLD_BONE, 0.0))
    ps.append(P(Ellipsoid(sc + V(0, -0.035, 0.03), (0.04, 0.03, 0.035)), OLD_BONE, 0.02))
    for s in (-1, 1):
        ec = sc + V(s * 0.024, 0.0, 0.055)
        ps.append(P(Sphere(ec, 0.019), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.006), 0.009), Mat((1.0, 0.1, 0.05), glow=1.0), 0.0))
    mo = 0.025 if pose == 'attack' else 0.008
    jaw = sc + V(0, -0.06 - mo, 0.03)
    ps.append(P(Ellipsoid(jaw, (0.036, 0.014, 0.028)), CHROME, 0.004))
    for i in range(5):
        x = (i - 2) * 0.011
        ps.append(P(Box(sc + V(x, -0.05, 0.06 - abs(x) * 0.3), (0.004, 0.008, 0.004)), TEETH, 0.0))
    # eight jointed legs
    ph = {'walk1': 0, 'walk2': 1}.get(pose, 0)
    for s in (-1, 1):
        for k in range(4):
            base = c + V(s * 0.06, -0.01, 0.04 - k * 0.045)
            spread = (k - 1.5) * 0.35
            lift = 0.04 if (k + ph + (s > 0)) % 2 == 0 else 0.0
            if pose == 'attack' and k == 0:
                knee = base + V(s * 0.12, 0.14, 0.08)
                foot = knee + V(s * 0.02, 0.06, 0.1)
            else:
                knee = base + V(s * 0.13, 0.08 + lift, np.sin(spread) * 0.08)
                foot = knee + V(s * 0.08, -0.2 - (0.0 if lift == 0 else -0.03), np.sin(spread) * 0.1)
            limb(ps, base, knee, 0.02, 0.016, GUNMETAL, 0.004)
            ps.append(P(Sphere(knee, 0.021), CHROME, 0.002))
            limb(ps, knee, foot, 0.016, 0.006, CHROME, 0.002)
    return ps


# ------------------------------------------------------------------ BOSS 4: FRANKENSTEIN PRIME (mech + Dr. Franken in the cockpit)

def doctor_head(ps, hc, s=1.0, expr='mad'):
    skin = Mat((0.85, 0.7, 0.6), var=0.1, vfreq=30, spec=0.3)
    hair = Mat((0.95, 0.95, 0.92), var=0.2, vfreq=40)
    ps.append(P(Ellipsoid(hc, V(0.045, 0.05, 0.045) * s), skin, 0.0))
    ps.append(P(Cone(hc + V(0, 0.0, 0.04) * s, hc + V(0, -0.02, 0.07) * s, 0.01 * s, 0.006 * s), skin, 0.006 * s))
    for k in range(9):
        a = -1.6 + k * 0.4
        st = hc + V(np.sin(a) * 0.035, 0.03, np.cos(a) * 0.02 - 0.015) * s
        en = st + V(np.sin(a) * 0.05, 0.03 + 0.02 * (k % 2), -0.01) * s
        ps.append(P(Cone(st, en, 0.014 * s, 0.003 * s), hair, 0.01 * s))
    for sd in (-1, 1):
        g = hc + V(sd * 0.018, 0.012, 0.042) * s
        ps.append(P(Torus(g, 0.014 * s, 0.004 * s, R=rot(np.pi / 2, 0, 0)), Mat((0.3, 0.25, 0.15), spec=0.7), 0.0))
        ps.append(P(Sphere(g, 0.011 * s), Mat((0.6, 0.9, 1.0), glow=1.0), 0.0))
    mo = 0.012 if expr == 'mad' else 0.004
    ps.append(P(Ellipsoid(hc + V(0, -0.028, 0.042) * s, V(0.016, mo, 0.01) * s), MOUTH, 0.002, op='sub'))
    ps.append(P(Box(hc + V(0, -0.045, 0.03) * s, V(0.02, 0.01, 0.01) * s, r=0.005 * s), hair, 0.004 * s))   # goatee


def prime(pose='walk1', pilot=True):
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.7
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.17, hip_y, 0)
        kn = hip + V(s * 0.04, -0.33, 0.06 * ls + 0.06)
        an = kn + V(0, -0.3, -0.04 * ls)
        limb(ps, hip, kn, 0.1, 0.085, GUNMETAL, 0.03)
        ps.append(P(Sphere(kn, 0.1), CHROME, 0.02))
        limb(ps, kn, an, 0.085, 0.075, GREENMETAL, 0.03)
        limb(ps, kn + V(s * 0.07, 0, -0.02), an + V(s * 0.06, 0.1, -0.02), 0.025, 0.025, CHROME, 0.0)   # piston
        ps.append(P(Box(an + V(0, -0.05, 0.06), (0.11, 0.05, 0.16), r=0.025), RUBBER, 0.02))
    ps.append(P(Box(V(0, hip_y + 0.06, 0), (0.25, 0.1, 0.15), r=0.05), GUNMETAL, 0.04))
    ch = V(0, hip_y + 0.42, 0.0)
    ps.append(P(Box(ch, (0.34, 0.28, 0.2), r=0.09), GREENMETAL, 0.07))
    # glass cockpit dome in the chest with the doctor inside
    dc = ch + V(0, 0.02, 0.17)
    ps.append(P(Sphere(dc, 0.15), BLACK, 0.01, op='sub'))
    ps.append(P(Torus(dc + V(0, 0, 0.0), 0.15, 0.022, R=rot(np.pi / 2, 0, 0)), CHROME, 0.0))
    if pilot:
        ps.append(P(Ellipsoid(dc + V(0, -0.08, -0.03), (0.08, 0.05, 0.05)), Mat((0.92, 0.92, 0.9), var=0.1, vfreq=20), 0.02))   # lab coat
        doctor_head(ps, dc + V(0, 0.0, -0.02), 1.15, 'mad' if pose == 'attack' else 'calm')
    else:       # empty seat, sparking wires
        ps.append(P(Box(dc + V(0, -0.04, -0.08), (0.08, 0.1, 0.03), r=0.02), RUBBER, 0.01))
        for k in range(3):
            limb(ps, dc + V(-0.05 + k * 0.05, 0.1, -0.06), dc + V(-0.04 + k * 0.04, 0.02, 0.0), 0.006, 0.006, [COPPER, RUBBER, GLOSS_RED][k], 0.0)
    ps.append(P(Sphere(dc + V(0, 0.0, -0.03), 0.14), Mat((0.3, 0.9, 0.5), glow=0.0, spec=1.2, shin=60), 0.0, op='int') if False else
              P(Sphere(dc + V(0.06, 0.07, 0.11), 0.018), Mat((0.95, 1.0, 1.0), glow=1.0), 0.0))      # glass glint
    for k in range(4):
        ps.append(P(Box(ch + V(-0.22 + k * 0.03, -0.18, 0.2), (0.008, 0.06, 0.01)), BLACK, 0.0))
    ps.append(P(Box(ch + V(0, -0.24, 0.19), (0.2, 0.025, 0.012)), HAZARD, 0.0))
    # tesla shoulders with arcs
    for s in (-1, 1):
        sh = ch + V(s * 0.38, 0.18, -0.02)
        ps.append(P(Sphere(sh, 0.14), GUNMETAL, 0.04))
        limb(ps, sh + V(0, 0.08, -0.04), sh + V(s * 0.05, 0.36, -0.07), 0.03, 0.024, COPPER, 0.0)
        for k in range(4):
            ps.append(P(Torus(sh + V(s * 0.02, 0.14 + k * 0.05, -0.055), 0.045, 0.01), COPPER, 0.0))
        ps.append(P(Sphere(sh + V(s * 0.055, 0.39, -0.07), 0.045), ZAPCORE, 0.0, disp=(0.01, 25, 3 + s)))
    # the Frankenstein head on top
    hc = ch + V(0, 0.42, 0.0)
    if pose == 'pain':
        hc = hc + V(0.06, -0.02, -0.04)
    limb(ps, ch + V(0, 0.25, 0), hc - V(0, 0.1, 0), 0.09, 0.08, GUNMETAL, 0.03)
    ps.append(P(Box(hc, (0.14, 0.16, 0.13), r=0.04), GREENMETAL, 0.0))
    ps.append(P(Box(hc + V(0, 0.15, 0), (0.15, 0.02, 0.14), r=0.008), GUNMETAL, 0.006))
    ps.append(P(Box(hc + V(0, 0.055, 0.125), (0.13, 0.022, 0.022), r=0.01), GUNMETAL, 0.008))
    for s in (-1, 1):
        ps.append(P(Box(hc + V(s * 0.055, 0.02, 0.13), (0.035, 0.01, 0.01)), EYE_GRN, 0.0))
    mo = 0.035 if pose == 'attack' else 0.012
    ps.append(P(Box(hc + V(0, -0.08, 0.125), (0.08, 0.012 + mo, 0.02)), BLACK, 0.004, op='sub'))
    for k in range(7):
        ps.append(P(Box(hc + V((k - 3) * 0.022, -0.08, 0.125), (0.006, 0.016 + mo, 0.008)), CHROME, 0.0))
    for k in range(5):
        ps.append(P(Box(hc + V(-0.06 + k * 0.03, 0.1, 0.135), (0.003, 0.012, 0.004)), CHROME, 0.0))
    bolt_pair(ps, hc + V(0, -0.1, 0), 0.12)
    # arms: big clamp hands, lightning when attacking
    shl, shr = ch + V(-0.4, 0.08, 0), ch + V(0.4, 0.08, 0)
    if pose == 'attack':
        hl, hr = shl + V(-0.15, 0.32, 0.16), shr + V(0.15, 0.34, 0.16)
    elif pose == 'pain':
        hl, hr = shl + V(-0.2, -0.05, 0.12), shr + V(0.18, 0.1, 0.08)
    else:
        hl, hr = shl + V(-0.06, -0.45 - 0.04 * sw, 0.14), shr + V(0.06, -0.45 + 0.04 * sw, 0.14)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.08, -0.05, -0.05)
        limb(ps, sh, el, 0.09, 0.08, GUNMETAL, 0.03)
        ps.append(P(Sphere(el, 0.085), CHROME, 0.02))
        limb(ps, el, hd, 0.08, 0.07, GREENMETAL, 0.03)
        d = norm(hd - el)
        ps.append(P(Box(hd + d * 0.05, (0.08, 0.08, 0.08), r=0.025), GUNMETAL, 0.02))
        for f in (-1, 1):
            limb(ps, hd + d * 0.09 + V(f * 0.05, 0, 0), hd + d * 0.2 + V(f * 0.06, -0.03, 0), 0.025, 0.02, CHROME, 0.006)
        if pose == 'attack':
            ps.append(P(Sphere(hd + d * 0.22 + V(0, 0.05, 0), 0.08), ZAPCORE, 0.0, disp=(0.02, 18, 7 + s)))
    return ps


def zap_proj(seed=0):
    ps = [P(Sphere((0, 0.07, 0), 0.055), ZAPCORE, 0.0, disp=(0.016, 22, 40 + seed))]
    for k in range(5):
        a = seed * 0.8 + k * 1.25
        p0 = V(0, 0.07, 0)
        p1 = p0 + V(np.cos(a) * 0.1, np.sin(a) * 0.09, 0)
        p2 = p1 + V(np.cos(a + 0.7) * 0.04, np.sin(a + 0.7) * 0.04, 0)
        limb(ps, p0, p1, 0.008, 0.004, ZAPGLOW, 0.0)
        limb(ps, p1, p2, 0.004, 0.002, ZAPGLOW, 0.0)
    return ps


# ------------------------------------------------------------------ death frames
OIL = Mat((0.04, 0.04, 0.05), spec=1.2, shin=60)


def frank_fall():
    return tilt_scene(frankbot('pain'), ang_z=0.55, shift=(0.05, -0.03, 0))


def frank_dead():
    ps = [P(Ellipsoid((0.0, -0.005, 0.02), (0.36, 0.012, 0.16)), OIL, 0.0)]
    ps += tilt_scene(frankbot('pain'), ang_z=1.5, shift=(0.42, 0.1, 0))
    for k, (x, z) in enumerate(((-0.3, 0.12), (0.34, 0.1), (0.05, 0.16))):     # loose bolts and a gear
        ps.append(P(Torus((x, 0.012, z), 0.02, 0.008), CHROME if k else COPPER, 0.0))
    return ps


def drone_fall():
    from weapons import transform
    return transform(drone('pain'), rot(0.4, 0, 0.9), V(0, 0.16, 0))


def drone_dead():
    ps = [P(Ellipsoid((0.0, -0.004, 0.0), (0.16, 0.01, 0.1)), OIL, 0.0)]
    pk = pumpkin_mat((0.75, 0.33, 0.06), seed=312)
    c = V(0, 0.08, 0)
    ps.append(P(Pumpkin(c, 0.11, squash=0.6, ribs=10, amp=0.08), pk, 0.0))
    jack_face(ps, c, 0.11, fierce=1.6, glowmat=Mat((0.25, 0.05, 0.02)), mouth_open=0.6)
    for k, (a, x) in enumerate(((0.4, -0.16), (-0.3, 0.17))):
        limb(ps, V(x * 0.4, 0.06, 0), V(x, 0.02, 0.05), 0.01, 0.008, GUNMETAL, 0.004)
        ps.append(P(Cyl(V(x, 0.02, 0.05), 0.06, 0.004, R=rot(a, 0, a)), Mat((0.5, 0.5, 0.55), spec=0.6), 0.0))
    return ps


def cyborg_fall():
    from props import corpse_frames
    return corpse_frames(cyborg)[0]


def cyborg_dead():
    from props import corpse_frames
    return corpse_frames(cyborg, BLOOD)[1]


def spider_fall():
    return tilt_scene(spider('pain'), ang_z=0.9, pivot=(0, 0.13, 0), shift=(0, -0.02, 0))


def spider_dead():
    ps = [P(Ellipsoid((0.0, -0.004, 0.0), (0.18, 0.01, 0.1)), OIL, 0.0)]
    return ps + tilt_scene(spider('pain'), ang_z=np.pi, pivot=(0, 0.13, 0), shift=(0, -0.06, 0))


def prime_fall():
    return tilt_scene(prime('pain'), ang_z=0.35, shift=(0.1, -0.08, 0))


def prime_dead():
    ps = [P(Ellipsoid((0.0, -0.005, 0.03), (0.8, 0.014, 0.3)), OIL, 0.0)]
    return ps + tilt_scene(prime('pain', pilot=False), ang_z=1.5, shift=(0.98, 0.2, 0))


def laser_proj(seed=0):
    red = Mat((1.0, 0.25, 0.2), glow=1.0)
    core = Mat((1.0, 0.85, 0.8), glow=1.0)
    ps = [P(Cone((-0.06, 0.05, 0), (0.06, 0.05, 0), 0.016 + 0.004 * seed, 0.016 + 0.004 * seed), red, 0.0),
          P(Cone((-0.05, 0.05, 0.01), (0.05, 0.05, 0.01), 0.008, 0.008), core, 0.0)]
    return ps
