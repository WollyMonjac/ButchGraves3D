"""Episode 5 (Curse of the Jade Skull) props, pickups and cutscene actors. Feet at y=0, facing +z."""
import numpy as np
from sdf import *
from monsters import limb, cloth, tilt_scene, TriPrism, fire_mat, BONE, BLACK, MOUTH, TEETH, FIRE
from monsters2 import V, STEEL, GOLD, OLD_BONE
from monsters4 import jade, pelt, feather, FEATHER_G, FEATHER_R, FEATHER_B, WOOD, OBSIDIAN, EYE_JADE, JADEFIRE, scaled_about

FLAME = fire_mat(seed=121)
MOSSY = Mat(fn=lambda p, n: np.where((fbm(p, 6, 3, 141) > 0.58)[:, None], np.array([[0.24, 0.36, 0.14]]), np.array([[0.48, 0.47, 0.4]])) *
        (0.6 + 0.5 * fbm(p, 20, 3, 142))[:, None], spec=0.15)
TSTONE = Mat(fn=lambda p, n: np.tile(np.array([0.52, 0.5, 0.42]), (len(p), 1)) * (0.6 + 0.5 * fbm(p, 16, 3, 143))[:, None], spec=0.15)
BARK = Mat(fn=lambda p, n: np.tile(np.array([0.42, 0.36, 0.28]), (len(p), 1)) * (0.6 + 0.5 * fbm(p * V(3, 0.6, 3), 14, 3, 144))[:, None])
LEAF = Mat(fn=lambda p, n: np.tile(np.array([0.16, 0.42, 0.12]), (len(p), 1)) * (0.6 + 0.6 * fbm(p, 18, 3, 145))[:, None], spec=0.5, shin=20)
LEAF2 = Mat(fn=lambda p, n: np.tile(np.array([0.24, 0.52, 0.16]), (len(p), 1)) * (0.7 + 0.5 * fbm(p, 22, 3, 146))[:, None], spec=0.5, shin=20)
MARIGOLD = Mat((0.98, 0.55, 0.06), var=0.25, vfreq=50)
KHAKI = Mat((0.62, 0.55, 0.38), var=0.15, vfreq=30, spec=0.15)
TWEED = Mat(fn=lambda p, n: np.tile(np.array([0.42, 0.3, 0.2]), (len(p), 1)) * (0.75 + 0.3 * (np.sin(p[:, 0] * 300) * np.sin(p[:, 1] * 300) > 0))[:, None], spec=0.1)
SKIN = Mat((0.88, 0.7, 0.58), var=0.1, vfreq=30, spec=0.3)
CANVAS = Mat((0.72, 0.66, 0.5), var=0.2, vfreq=12)


def leaf(ps, base, tip, w, mat=LEAF, droop=0.0):
    """A long tropical leaf from base to tip, drooping at the end."""
    mid = (base + tip) / 2 + V(0, -droop * 0.5, 0)
    for a, b, ww in ((base, mid, w), (mid, tip + V(0, -droop, 0), w * 0.8)):
        d = b - a
        L = np.linalg.norm(d)
        d = d / L
        side = norm(np.cross(d, V(0, 1, 0)) + V(1e-4, 0, 0))
        up = norm(np.cross(side, d))
        R = np.stack([side, up, d], 1)
        ps.append(P(Ellipsoid((a + b) / 2, (ww, 0.006, L / 2), R=R), mat, 0.004))


# ------------------------------------------------------------------ jungle vegetation

def kapok(seed=3):
    """A giant buttressed jungle tree with a dense crown and hanging lianas."""
    rs = np.random.RandomState(seed)
    ps = []
    def trunk_d(p):
        y = p[:, 1]
        ang = np.arctan2(p[:, 2], p[:, 0])
        flare = np.exp(-y * 7) * (0.12 + 0.08 * np.abs(np.sin(ang * 2.5)) ** 4)
        r = 0.08 + flare + 0.006 * np.sin(ang * 9 + y * 6)
        d = np.sqrt(p[:, 0] ** 2 + p[:, 2] ** 2) - r
        return np.maximum(d, np.maximum(-y, y - 1.25)) * 0.8
    ps.append(P(Func(trunk_d), BARK, 0.0))
    for k in range(5):
        a = rs.uniform(0, 2 * np.pi); y0 = rs.uniform(0.9, 1.2)
        b0 = V(0, y0, 0); b1 = b0 + V(np.cos(a) * 0.3, rs.uniform(0.08, 0.2), np.sin(a) * 0.2)
        limb(ps, b0, b1, 0.035, 0.015, BARK, 0.02)
    for k in range(9):
        a = rs.uniform(0, 2 * np.pi)
        c = V(np.cos(a) * rs.uniform(0.1, 0.35), rs.uniform(1.25, 1.45), np.sin(a) * rs.uniform(0.05, 0.2))
        ps.append(P(Ellipsoid(c, (rs.uniform(0.14, 0.22), rs.uniform(0.08, 0.12), 0.14)), LEAF if k % 2 else LEAF2, 0.06, disp=(0.025, 14, k)))
    for k in range(5):
        x = rs.uniform(-0.3, 0.3)
        top = V(x, 1.3, rs.uniform(-0.05, 0.12))
        limb(ps, top, top + V(rs.uniform(-0.03, 0.03), -rs.uniform(0.5, 0.95), 0.02), 0.007, 0.006, Mat((0.24, 0.34, 0.12)), 0.0)
    return ps


def palm(seed=5):
    ps = []
    rs = np.random.RandomState(seed)
    pts = [V(0, 0, 0)]
    for k in range(8):
        t = (k + 1) / 8
        pts.append(V(0.12 * t ** 2, t * 1.2, 0.0))
    ring = Mat(fn=lambda p, n: np.tile(np.array([0.46, 0.38, 0.28]), (len(p), 1)) * (0.7 + 0.3 * (np.sin(p[:, 1] * 110) > 0))[:, None])
    for k in range(8):
        limb(ps, pts[k], pts[k + 1], 0.045 - k * 0.002, 0.043 - k * 0.002, ring, 0.01)
    top = pts[-1]
    for k in range(9):
        a = k * 2 * np.pi / 9 + rs.uniform(-0.2, 0.2)
        tip = top + V(np.cos(a) * 0.42, rs.uniform(-0.25, 0.0), np.sin(a) * 0.3)
        leaf(ps, top, tip, 0.05, LEAF2 if k % 2 else LEAF, 0.12)
    for k in range(3):
        ps.append(P(Sphere(top + V(rs.uniform(-0.04, 0.04), -0.05, 0.05), 0.03), Mat((0.35, 0.26, 0.12), spec=0.4), 0.0))
    return ps


def fern(seed=7):
    """A clump of big ferns and elephant-ear leaves (not solid)."""
    rs = np.random.RandomState(seed)
    ps = []
    for k in range(11):
        a = k * 2 * np.pi / 11 + rs.uniform(-0.2, 0.2)
        L = rs.uniform(0.2, 0.32)
        leaf(ps, V(0, 0.02, 0), V(np.cos(a) * L, rs.uniform(0.15, 0.32), np.sin(a) * L * 0.6), rs.uniform(0.035, 0.05),
             LEAF if k % 2 else LEAF2, rs.uniform(0.05, 0.12))
    for k in range(2):
        ps.append(P(Sphere(V(rs.uniform(-0.08, 0.08), 0.2, rs.uniform(0.0, 0.08)), 0.02), Mat((0.95, 0.2, 0.3), var=0.2, vfreq=40), 0.0))
    return ps


def vines(seed=9):
    """Lianas and creepers hanging from the canopy or a temple ceiling."""
    rs = np.random.RandomState(seed)
    ps = []
    for k in range(6):
        x = rs.uniform(-0.15, 0.15)
        z = rs.uniform(-0.05, 0.05)
        y1 = rs.uniform(0.0, 0.4)
        ph = rs.uniform(0, 6)
        prev = V(x, 1.0, z)
        for m in range(8):
            y = 1.0 - (1.0 - y1) * (m + 1) / 8
            cur = V(x + 0.03 * np.sin(y * 8 + ph), y, z)
            limb(ps, prev, cur, 0.009, 0.008, Mat((0.22, 0.36, 0.12), var=0.2, vfreq=30), 0.004)
            if m % 2 == 1:
                leaf(ps, cur, cur + V(0.06 * (1 if m % 4 == 1 else -1), -0.02, 0.03), 0.02, LEAF2, 0.02)
            prev = cur
    return ps


# ------------------------------------------------------------------ ruins

def olmec():
    """A colossal stone head half swallowed by the jungle."""
    st = MOSSY
    ps = [P(Ellipsoid(V(0, 0.36, 0), (0.3, 0.34, 0.27)), st, 0.0, disp=(0.008, 10, 4))]
    ps.append(P(Box(V(0, 0.04, 0), (0.3, 0.06, 0.26), r=0.04), st, 0.05))
    hc = V(0, 0.38, 0.0)
    # helmet band
    ps.append(P(Ellipsoid(hc + V(0, 0.2, -0.02), (0.31, 0.12, 0.27)), st, 0.03))
    ps.append(P(Box(hc + V(0, 0.12, 0.22), (0.26, 0.025, 0.04), r=0.01), st, 0.02))
    # heavy-lidded eyes, broad nose, thick lips
    for s in (-1, 1):
        ps.append(P(Ellipsoid(hc + V(s * 0.1, 0.04, 0.22), (0.06, 0.025, 0.03)), st, 0.02))
        ps.append(P(Ellipsoid(hc + V(s * 0.1, 0.03, 0.235), (0.045, 0.012, 0.02)), BLACK, 0.004, op='sub'))
        ps.append(P(Ellipsoid(hc + V(s * 0.29, 0.0, 0.0), (0.04, 0.1, 0.06)), st, 0.03))      # ears
    ps.append(P(Ellipsoid(hc + V(0, -0.05, 0.27), (0.08, 0.06, 0.05)), st, 0.03))
    ps.append(P(Ellipsoid(hc + V(0, -0.17, 0.25), (0.13, 0.04, 0.04)), st, 0.02))
    ps.append(P(Box(hc + V(0, -0.17, 0.29), (0.1, 0.006, 0.02)), BLACK, 0.0, op='sub'))
    # vines draped over it
    for k in range(4):
        x = -0.2 + k * 0.13
        limb(ps, V(x, 0.62, 0.05), V(x + 0.03, 0.2, 0.27), 0.012, 0.01, Mat((0.22, 0.36, 0.12)), 0.004)
    return ps


def jstatue():
    """A stone jaguar crouched on a pedestal, eyes of jade."""
    st = TSTONE
    ps = [P(Box(V(0, 0.15, 0), (0.15, 0.15, 0.13), r=0.01), st, 0.0)]
    for k in range(3):
        ps.append(P(Box(V(0, 0.08 + k * 0.08, 0.13), (0.15, 0.004, 0.004)), BLACK, 0.0, op='sub'))
    b = V(0, 0.38, 0)
    ps.append(P(Ellipsoid(b, (0.1, 0.09, 0.13)), st, 0.04))
    for s in (-1, 1):
        limb(ps, b + V(s * 0.06, -0.02, 0.07), V(s * 0.06, 0.3, 0.12), 0.03, 0.028, st, 0.02)
        ps.append(P(Ellipsoid(V(s * 0.06, 0.31, 0.14), (0.03, 0.015, 0.035)), st, 0.01))
    hc = b + V(0, 0.13, 0.08)
    ps.append(P(Ellipsoid(hc, (0.075, 0.07, 0.07)), st, 0.03))
    ps.append(P(Ellipsoid(hc + V(0, -0.025, 0.055), (0.045, 0.035, 0.04)), st, 0.02))
    for s in (-1, 1):
        ps.append(P(Cone(hc + V(s * 0.05, 0.04, -0.01), hc + V(s * 0.065, 0.1, -0.02), 0.028, 0.006), st, 0.01))
        ps.append(P(Sphere(hc + V(s * 0.028, 0.012, 0.06), 0.011), EYE_JADE, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.05, 0.07), (0.03, 0.012, 0.02)), BLACK, 0.004, op='sub'))
    for s in (-1, 1):
        ps.append(P(Cone(hc + V(s * 0.015, -0.04, 0.08), hc + V(s * 0.015, -0.07, 0.085), 0.006, 0.001), TSTONE, 0.0))
    limb(ps, b + V(0, 0.0, -0.12), b + V(0.12, 0.12, -0.12), 0.02, 0.012, st, 0.01)
    return ps


def rack():
    """A tzompantli: a wooden rack strung with rows of skulls."""
    ps = []
    for x in (-0.28, 0.28):
        limb(ps, V(x, 0, 0), V(x, 0.62, 0), 0.025, 0.022, WOOD, 0.0)
    for k in range(3):
        y = 0.2 + k * 0.17
        limb(ps, V(-0.3, y, 0), V(0.3, y, 0), 0.009, 0.009, WOOD, 0.0)
        for m in range(5):
            sc = V(-0.2 + m * 0.1, y, 0.0)
            ps.append(P(Ellipsoid(sc, (0.04, 0.045, 0.042)), OLD_BONE, 0.0))
            ps.append(P(Ellipsoid(sc + V(0, -0.025, 0.02), (0.026, 0.022, 0.025)), OLD_BONE, 0.01))
            for s in (-1, 1):
                ps.append(P(Sphere(sc + V(s * 0.016, 0.004, 0.036), 0.012), BLACK, 0.003, op='sub'))
    return ps


def ofrenda():
    """A Day of the Dead altar: a cloth-draped table heaped with marigolds, candles, sugar skulls and pan de muerto."""
    ps = [P(Box(V(0, 0.18, 0), (0.24, 0.18, 0.12), r=0.01), Mat((0.75, 0.15, 0.4), var=0.1, vfreq=20), 0.0)]
    ps.append(P(Box(V(0, 0.36, 0.0), (0.26, 0.01, 0.14), r=0.005), Mat((0.95, 0.92, 0.85)), 0.0))
    ps.append(P(Box(V(0, 0.46, -0.06), (0.2, 0.1, 0.06), r=0.01), Mat((0.85, 0.5, 0.15), var=0.1, vfreq=20), 0.0))
    # papel picado edge
    for k in range(9):
        ps.append(P(Box(V(-0.22 + k * 0.055, 0.33, 0.125), (0.022, 0.03, 0.003)),
                    Mat([(0.9, 0.2, 0.5), (0.2, 0.6, 0.9), (0.95, 0.75, 0.1)][k % 3]), 0.0))
    for k, (x, z) in enumerate(((-0.17, 0.06), (0.17, 0.06), (-0.12, -0.06), (0.12, -0.06))):
        h = 0.08 + 0.03 * (k % 2)
        y0 = 0.37 if k < 2 else 0.56
        ps.append(P(Cyl(V(x, y0 + h / 2, z), 0.014, h / 2), Mat((0.95, 0.92, 0.8)), 0.0))
        ps.append(P(Cone(V(x, y0 + h + 0.006, z), V(x, y0 + h + 0.04, z), 0.008, 0.001), FLAME, 0.0))
    for k, x in enumerate((-0.06, 0.06)):
        sc = V(x, 0.41, 0.06)
        ps.append(P(Ellipsoid(sc, (0.035, 0.038, 0.035)), Mat((0.96, 0.95, 0.92)), 0.0))
        for s in (-1, 1):
            ps.append(P(Sphere(sc + V(s * 0.014, 0.006, 0.03), 0.01), Mat([(0.9, 0.2, 0.5), (0.2, 0.6, 0.9)][k]), 0.0))
    rs = np.random.RandomState(4)
    for k in range(22):
        ps.append(P(Sphere(V(rs.uniform(-0.24, 0.24), rs.choice([0.38, 0.57]), rs.uniform(-0.12, 0.12)), rs.uniform(0.016, 0.024)), MARIGOLD,
                    0.0, disp=(0.004, 60, k)))
    ps.append(P(Ellipsoid(V(0.0, 0.58, -0.04), (0.05, 0.03, 0.04)), Mat((0.75, 0.45, 0.2), var=0.2, vfreq=30), 0.0))    # bread
    return ps


def torch():
    """A torch on a carved post."""
    ps = [P(Box(V(0, 0.28, 0), (0.035, 0.28, 0.035), r=0.008), TSTONE, 0.0)]
    ps.append(P(Cone(V(0, 0.56, 0), V(0, 0.66, 0), 0.03, 0.05), WOOD, 0.004))
    ps.append(P(Cone(V(0, 0.64, 0), V(0, 0.84, 0), 0.055, 0.008), FLAME, 0.02, disp=(0.018, 14, 3)))
    return ps


def pillar():
    """A broken carved stela, the top snapped off."""
    st = MOSSY
    ps = [P(Box(V(0, 0.04, 0), (0.12, 0.04, 0.12), r=0.01), st, 0.0)]
    def body(p):
        q = p - V(0, 0.45, 0)
        d = np.maximum(np.abs(q[:, 0]) - 0.09, np.abs(q[:, 2]) - 0.08)
        top = 0.42 + 0.06 * np.sin(p[:, 0] * 30) * np.cos(p[:, 2] * 25)
        return np.maximum(np.maximum(d, -(p[:, 1] - 0.05)), p[:, 1] - (0.45 + top)) * 0.85
    ps.append(P(Func(body), st, 0.01))
    for k in range(5):
        y = 0.18 + k * 0.13
        ps.append(P(Box(V(0, y, 0.08), (0.06, 0.04, 0.006)), BLACK, 0.002, op='sub'))
        ps.append(P(Box(V(0, y, 0.075), (0.04, 0.025, 0.006)), st, 0.002))
    return ps


def gold():
    """Spilled treasure: coins, a chalice, a jade mask."""
    rs = np.random.RandomState(6)
    ps = [P(Ellipsoid(V(0, 0.0, 0), (0.22, 0.06, 0.14)), GOLD, 0.0, disp=(0.008, 40, 2))]
    for k in range(14):
        ps.append(P(Cyl(V(rs.uniform(-0.22, 0.22), rs.uniform(0.0, 0.07), rs.uniform(-0.12, 0.14)), 0.018, 0.003,
                        R=rot(rs.uniform(-1, 1), 0, rs.uniform(-1, 1))), GOLD, 0.0))
    ps.append(P(Cone(V(0.1, 0.04, 0.02), V(0.1, 0.16, 0.02), 0.02, 0.045), GOLD, 0.0))
    ps.append(P(Cyl(V(0.1, 0.16, 0.02), 0.04, 0.008), BLACK, 0.0, op='sub'))
    ps.append(P(Ellipsoid(V(-0.08, 0.08, 0.06), (0.05, 0.06, 0.02)), jade(141), 0.0))
    for s in (-1, 1):
        ps.append(P(Sphere(V(-0.08 + s * 0.02, 0.09, 0.078), 0.009), BLACK, 0.0, op='sub'))
    return ps


def tent():
    """Professor Crane's expedition tent with a lantern and a crate of plunder."""
    def body(p):
        x, y, z = p[:, 0], p[:, 1], p[:, 2]
        d = np.maximum(np.abs(x) * 0.62 + y - 0.5, -y)
        return np.maximum(d, np.abs(z) - 0.3) * 0.8
    ps = [P(Func(body), CANVAS, 0.0, disp=(0.004, 20, 3))]
    ps.append(P(TriPrism(V(0, 0.0, 0.31), (-0.2, 0.0), (0.2, 0.0), (0.0, 0.34), 0.02), BLACK, 0.0, op='sub'))
    limb(ps, V(-0.5, 0.0, 0.32), V(0, 0.5, 0.32), 0.006, 0.006, Mat((0.6, 0.55, 0.4)), 0.0)
    ps.append(P(Box(V(0.32, 0.07, 0.25), (0.08, 0.07, 0.06), r=0.005), WOOD, 0.0))
    ps.append(P(Cyl(V(-0.3, 0.06, 0.32), 0.025, 0.04), Mat((0.25, 0.25, 0.2), spec=0.8), 0.0))
    ps.append(P(Sphere(V(-0.3, 0.07, 0.34), 0.018), Mat((1.0, 0.85, 0.4), glow=1.0), 0.0))
    return ps


# ------------------------------------------------------------------ gadgets and pickups

def boulder(ph=0):
    """The great rolling stone: a carved skull of grey basalt (two frames, rotated)."""
    st = Mat(fn=lambda p, n: np.tile(np.array([0.5, 0.47, 0.42]), (len(p), 1)) * (0.55 + 0.55 * fbm(p, 9, 3, 151))[:, None], spec=0.1)
    c = V(0, 0.46, 0)
    a = ph * 0.5
    R = rot(a, 0, 0)
    ps = [P(Sphere(c, 0.45), st, 0.0, disp=(0.015, 7, 3))]
    # carved face rotates with the roll
    for s in (-1, 1):
        e = c + R @ V(s * 0.16, 0.08, 0.38)
        ps.append(P(Sphere(e, 0.1), BLACK, 0.01, op='sub'))
    ps.append(P(TriPrism(c + R @ V(0, -0.05, 0.43), (-0.04, -0.04), (0.04, -0.04), (0, 0.05), 0.06), BLACK, 0.0, op='sub'))
    for k in range(6):
        t = c + R @ V(-0.15 + k * 0.06, -0.2, 0.4)
        ps.append(P(Box(t, (0.022, 0.035, 0.05), R=R), BLACK, 0.005, op='sub'))
    for k in range(4):
        b = rot(0, 0, k * 0.8 + a) @ V(0.44, 0, 0)
        ps.append(P(Box(c + b * 0.98, (0.02, 0.02, 0.2)), BLACK, 0.0, op='sub'))
    return ps


def idol():
    """The golden fertility idol, sitting on nothing in particular."""
    g = Mat((1.0, 0.78, 0.22), var=0.1, vfreq=40, spec=1.4, shin=50)
    ps = [P(Ellipsoid(V(0, 0.1, 0), (0.06, 0.08, 0.05)), g, 0.0)]
    hc = V(0, 0.21, 0.01)
    ps.append(P(Ellipsoid(hc, (0.05, 0.048, 0.045)), g, 0.02))
    for s in (-1, 1):
        ps.append(P(Sphere(hc + V(s * 0.018, 0.005, 0.04), 0.01), BLACK, 0.002, op='sub'))
        limb(ps, V(s * 0.05, 0.12, 0.02), V(s * 0.025, 0.08, 0.05), 0.016, 0.014, g, 0.01)
        ps.append(P(Ellipsoid(V(s * 0.03, 0.025, 0.02), (0.025, 0.02, 0.035)), g, 0.01))
    ps.append(P(Box(hc + V(0, -0.025, 0.04), (0.018, 0.004, 0.005)), BLACK, 0.0, op='sub'))
    ps.append(P(Sphere(hc + V(0, 0.05, 0.0), 0.012), EYE_JADE, 0.0))
    return ps


def jskull():
    """The Jade Skull."""
    ps = [P(Ellipsoid(V(0, 0.07, 0), (0.06, 0.064, 0.064)), EYE_JADE, 0.0)]
    ps.append(P(Ellipsoid(V(0, 0.04, 0.03), (0.04, 0.03, 0.035)), EYE_JADE, 0.01))
    for s in (-1, 1):
        ps.append(P(Sphere(V(s * 0.024, 0.075, 0.052), 0.017), BLACK, 0.003, op='sub'))
    ps.append(P(TriPrism(V(0, 0.05, 0.062), (-0.008, -0.007), (0.008, -0.007), (0, 0.009), 0.02), BLACK, 0.0, op='sub'))
    for i in range(5):
        ps.append(P(Box(V((i - 2) * 0.012, 0.025, 0.06), (0.004, 0.008, 0.004)), BLACK, 0.0, op='sub'))
    return ps


def dart_proj(seed=0):
    from monsters4 import dart
    return dart(seed)


# ------------------------------------------------------------------ cutscene actor: Professor Mortimer Crane

def crane_head(ps, hc, s=1.0, expr='smug', melt=0):
    """Pith helmet, monocle, waxed moustache. melt 1-2: the face sliding off the skull (gory ending)."""
    skin = SKIN
    if melt == 0:
        ps.append(P(Ellipsoid(hc, V(0.045, 0.052, 0.046) * s), skin, 0.0))
        ps.append(P(Cone(hc + V(0, 0.0, 0.04) * s, hc + V(0, -0.015, 0.068) * s, 0.012 * s, 0.006 * s), skin, 0.006 * s))
        for sd in (-1, 1):
            ps.append(P(Sphere(hc + V(sd * 0.018, 0.012, 0.04) * s, 0.006 * s), BLACK, 0.0))
            limb(ps, hc + V(0, -0.02, 0.05) * s, hc + V(sd * 0.04, -0.016, 0.044) * s, 0.008 * s, 0.002 * s, Mat((0.3, 0.2, 0.12)), 0.004 * s)
        ps.append(P(Torus(hc + V(0.018, 0.012, 0.046) * s, 0.012 * s, 0.002 * s, R=rot(np.pi / 2, 0, 0)), GOLD, 0.0))
        mo = 0.014 if expr in ('rant', 'scream') else 0.004
        ps.append(P(Ellipsoid(hc + V(0, -0.032, 0.042) * s, V(0.014, mo, 0.01) * s), MOUTH, 0.002, op='sub'))
    else:
        # the jade light strips the flesh away: a skull with drooping, dripping skin
        ps.append(P(Ellipsoid(hc, V(0.045, 0.05, 0.046) * s), BONE, 0.0))
        for sd in (-1, 1):
            ps.append(P(Sphere(hc + V(sd * 0.018, 0.008, 0.04) * s, 0.014 * s), BLACK, 0.003, op='sub'))
            ps.append(P(Sphere(hc + V(sd * 0.018, 0.008, 0.036) * s, 0.006 * s), EYE_JADE, 0.0))
        ps.append(P(Ellipsoid(hc + V(0, -0.04, 0.035) * s, V(0.022, 0.02, 0.012) * s), BLACK, 0.002, op='sub'))
        flesh = Mat((0.62, 0.25, 0.18), var=0.3, vfreq=40, spec=0.8, shin=40)
        drop = 0.02 * melt
        for k in range(7):
            a = -1.2 + k * 0.4
            st = hc + V(np.sin(a) * 0.04, 0.0 - drop, np.cos(a) * 0.035) * s
            limb(ps, st, st + V(0, -(0.04 + 0.03 * melt + 0.01 * (k % 3)), 0.005) * s, 0.012 * s, 0.004 * s, flesh, 0.006 * s)
        ps.append(P(Ellipsoid(hc + V(0, -0.07 - drop, 0.02) * s, V(0.04, 0.02, 0.03) * s), flesh, 0.01 * s))
    # pith helmet
    ps.append(P(Ellipsoid(hc + V(0, 0.04, -0.004) * s, V(0.056, 0.04, 0.06) * s), Mat((0.9, 0.86, 0.72), var=0.08, vfreq=20), 0.0))
    ps.append(P(Ellipsoid(hc + V(0, 0.025, 0) * s, V(0.085, 0.008, 0.09) * s), Mat((0.86, 0.82, 0.68), var=0.08, vfreq=20), 0.004 * s))
    ps.append(P(Torus(hc + V(0, 0.03, 0) * s, 0.055 * s, 0.006 * s), Mat((0.35, 0.25, 0.15)), 0.0))


def crane(pose='stand'):
    """Professor Mortimer Crane: tweed jacket, khaki breeches, puttees, pith helmet. Poses: stand, rant (holding the skull
    up), run1, run2, melt1, melt2 (gory ending)."""
    ps = []
    sw = {'run1': -1, 'run2': 1}.get(pose, 0)
    lean = 0.12 if pose.startswith('run') else 0.0
    hip_y = 0.4
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.05, hip_y, 0)
        kn = hip + V(0, -0.19, 0.09 * ls + 0.02)
        an = kn + V(0, -0.18, -0.06 * ls)
        limb(ps, hip, kn, 0.042, 0.032, KHAKI, 0.02)
        limb(ps, kn, an, 0.03, 0.028, Mat((0.38, 0.3, 0.2), var=0.2, vfreq=40), 0.02)        # puttees
        ps.append(P(Ellipsoid(an + V(0, -0.015, 0.03), (0.03, 0.022, 0.055)), Mat((0.25, 0.15, 0.08), spec=0.6), 0.01))
    ch = V(0, hip_y + 0.18, lean * 0.4)
    ps.append(P(Ellipsoid(ch + V(0, -0.04, 0), (0.1, 0.13, 0.07)), TWEED, 0.04))
    ps.append(P(Ellipsoid(ch + V(0, -0.12, 0.01), (0.105, 0.06, 0.075)), TWEED, 0.03))
    ps.append(P(TriPrism(ch + V(0, 0.05, 0.066), (-0.03, 0.04), (0.03, 0.04), (0, -0.05), 0.01), Mat((0.92, 0.9, 0.85)), 0.004))   # shirt
    ps.append(P(TriPrism(ch + V(0, 0.05, 0.072), (-0.012, 0.035), (0.012, 0.035), (0, 0.015), 0.01), Mat((0.6, 0.1, 0.1)), 0.0))   # bow tie
    limb(ps, ch + V(-0.07, 0.07, 0.03), ch + V(0.08, -0.12, 0.06), 0.008, 0.008, Mat((0.35, 0.22, 0.12)), 0.0)   # satchel strap
    hc = ch + V(0, 0.17, 0.02 + lean * 0.3)
    melt = {'melt1': 1, 'melt2': 2}.get(pose, 0)
    crane_head(ps, hc, 1.5, 'rant' if pose in ('rant', 'run1', 'run2') else 'smug', melt)
    shl, shr = ch + V(-0.11, 0.07, 0), ch + V(0.11, 0.07, 0)
    if pose in ('rant', 'melt1', 'melt2'):
        hl, hr = shl + V(-0.04, 0.16, 0.08), shr + V(0.04, 0.24, 0.06)
    elif pose.startswith('run'):
        hl, hr = shl + V(-0.04, -0.06, 0.12 * sw + 0.04), shr + V(0.03, 0.02, 0.1)
    else:
        hl, hr = shl + V(-0.03, -0.17, 0.04), shr + V(0.04, -0.06, 0.12)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.03, -0.03, -0.02)
        limb(ps, sh, el, 0.032, 0.028, TWEED, 0.02)
        limb(ps, el, hd, 0.028, 0.024, TWEED, 0.02)
        ps.append(P(Sphere(hd, 0.02), SKIN, 0.01))
    # the Jade Skull in his right hand (glowing in the rant and melt poses)
    sk = hr + V(0, 0.06, 0.02)
    for pr in jskull():
        ps.append(_moved(pr, sk - V(0, 0.05, 0), 0.7))
    if pose in ('rant', 'melt1', 'melt2'):
        ps.append(P(Sphere(sk, 0.06 + 0.02 * melt), JADEFIRE, 0.0, disp=(0.015, 18, 3 + melt)))
    from weapons import transform
    return ps if lean == 0 else transform(ps, rot(lean, 0, 0), V(0, 0, 0))


def _moved(pr, off, s):
    """A copy of a primitive scaled by s about the origin and moved to off."""
    class L(Prim):
        def __init__(q, inner):
            q.inner = inner; q.op = inner.op; q.k = inner.k * s; q.mat = inner.mat; q.disp = None

        def d(q, p):
            return q.inner.dist((p - off) / s) * s
    return L(pr)


def shrunk(expr='rant'):
    """Classic ending: all that is left of Professor Crane, a shrunken head in a pith helmet, grumbling."""
    ps = []
    crane_head(ps, V(0, 0.06, 0), 0.9, expr)
    for k in range(5):
        a = -0.6 + k * 0.3
        limb(ps, V(np.sin(a) * 0.03, 0.02, 0.0), V(np.sin(a) * 0.035, -0.0, 0.0), 0.004, 0.003, Mat((0.2, 0.15, 0.1)), 0.0)
    return ps


def crane_bones():
    """Gory ending: what the skull left of Professor Crane - a heap of bones and tweed in a red puddle, helmet on top."""
    rs = np.random.RandomState(4)
    ps = [P(Ellipsoid(V(0, 0.0, 0), (0.24, 0.012, 0.15)), Mat((0.42, 0.02, 0.02), spec=0.9, shin=60), 0.0)]
    for k in range(9):
        a = V(rs.uniform(-0.16, 0.16), 0.022, rs.uniform(-0.08, 0.08))
        ang = rs.uniform(0, np.pi)
        limb(ps, a, a + V(np.cos(ang), 0.15 * rs.uniform(-1, 1), np.sin(ang)) * rs.uniform(0.09, 0.16), 0.013, 0.011, BONE, 0.004)
    for k in range(4):                                         # a ribcage, tipped over
        c = V(0.05, 0.05, 0.0)
        ps.append(P(Torus(c + V(k * 0.025, 0, 0), 0.05 - k * 0.005, 0.006, R=rot(0, np.pi / 2, 0.3)), BONE, 0.004))
    ps.append(P(Box(V(-0.02, 0.03, 0.06), (0.09, 0.012, 0.05), R=rot(0, 0.4, 0.1), r=0.01), TWEED, 0.02))   # the jacket
    sk = V(-0.09, 0.05, 0.03)
    ps.append(P(Ellipsoid(sk, (0.045, 0.048, 0.046)), BONE, 0.0))
    for sd in (-1, 1):
        ps.append(P(Sphere(sk + V(sd * 0.018, 0.008, 0.04), 0.013), BLACK, 0.003, op='sub'))
    ps.append(P(Ellipsoid(sk + V(0, 0.02, -0.004), (0.06, 0.04, 0.065)), Mat((0.9, 0.86, 0.72), var=0.08, vfreq=20), 0.0))
    ps.append(P(Ellipsoid(sk + V(0, 0.005, 0), (0.09, 0.008, 0.095)), Mat((0.86, 0.82, 0.68), var=0.08, vfreq=20), 0.004))
    return ps


def rubble():
    rs = np.random.RandomState(2)
    ps = []
    for k in range(9):
        ps.append(P(Sphere(V(rs.uniform(-0.3, 0.3), rs.uniform(0.02, 0.1), rs.uniform(-0.1, 0.1)), rs.uniform(0.05, 0.1)), TSTONE, 0.02,
                    disp=(0.02, 9, k)))
    return ps
