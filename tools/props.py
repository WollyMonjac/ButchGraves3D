"""SDF models for pickups, decorations, projectiles and death/gib frames."""
import numpy as np
from sdf import *
from monsters import *

GLASS_HL = Mat((0.95, 0.97, 1.0), spec=1.0, shin=60)
IRON = Mat((0.22, 0.22, 0.24), var=0.25, vfreq=30, spec=0.6, shin=30)
RUST = Mat((0.36, 0.2, 0.12), var=0.35, vfreq=25, spec=0.2)
BRASS = Mat((0.85, 0.65, 0.25), var=0.1, vfreq=30, spec=0.9, shin=40)
SILVER = Mat((0.85, 0.87, 0.92), var=0.05, vfreq=30, spec=1.0, shin=50)
WOOD = Mat((0.42, 0.27, 0.14), var=0.3, vfreq=18, spec=0.15)
DWOOD = Mat((0.24, 0.15, 0.08), var=0.3, vfreq=18)
STONE = Mat(fn=lambda p, n: np.tile(np.array([0.55, 0.55, 0.57]), (len(p), 1)) * (0.65 + 0.5 * fbm(p, 12, 3, 4))[:, None]
            * (1 - 0.5 * np.clip((fbm(p, 5, 2, 9) - 0.6) * 5, 0, 1))[:, None] + np.clip((fbm(p, 7, 2, 12) - 0.62) * 4, 0, 1)[:, None] * np.array([[0.0, 0.12, 0.0]]))
CARD_RED = Mat((0.62, 0.1, 0.08), var=0.15, vfreq=15)
FLAME = Mat(fn=lambda p, n: np.tile(np.array([1.0, 0.8, 0.3]), (len(p), 1)) * (0.85 + 0.3 * np.clip(n[:, 2], 0, 1))[:, None], glow=1.0)
WAX = Mat((0.92, 0.88, 0.75), var=0.08, vfreq=30, spec=0.3)
SLIME = Mat((0.4, 1.0, 0.25), glow=1.0)


def stripes(c1, c2, freq=60, axis=0):
    c1, c2 = np.asarray(c1), np.asarray(c2)
    def fn(p, n):
        s = np.sin(p[:, axis] * freq + p[:, 1] * freq * 0.6) > 0
        return np.where(s[:, None], c1[None, :], c2[None, :])
    return Mat(fn=fn, spec=0.6, shin=40)

# ------------------------------------------------------------------ pickups

def candy():
    ps = []
    for (c, col1, col2, ang) in (((0.0, 0.045, 0.02), (0.9, 0.35, 0.05), (0.98, 0.9, 0.8), 0.2),
                                  ((-0.03, 0.035, -0.04), (0.55, 0.15, 0.7), (0.2, 0.9, 0.3), -0.4)):
        c = np.asarray(c)
        R = rot(0, 0, ang)
        ax = R @ np.array([1.0, 0, 0])
        ps.append(P(Ellipsoid(c, (0.055, 0.032, 0.032), R=R), stripes(col1, col2, 90), 0.0))
        for s in (-1, 1):
            b = c + ax * s * 0.05
            ps.append(P(Cone(b, b + ax * s * 0.035, 0.01, 0.028), Mat(col1, spec=0.7, shin=40, var=0.1), 0.0))
    return ps


def bucket():
    orange = np.array([1.0, 0.5, 0.05])
    def fn(p, n):
        c = np.tile(orange, (len(p), 1)) * (0.85 + 0.2 * np.clip(n[:, 2], 0, 1))[:, None]
        x, y = p[:, 0], p[:, 1]
        front = p[:, 2] > 0.02
        eye = (np.abs(np.abs(x) - 0.035) < 0.018 - (y - 0.09) * 0.4) & (y > 0.075) & (y < 0.105)
        mouth = (np.abs(x) < 0.055) & (y > 0.035 + 0.02 * (np.abs(x) / 0.055) ** 2) & (y < 0.055 + 0.012 * np.cos(x * 120))
        m = front & (eye | mouth)
        c[m] = np.array([0.05, 0.03, 0.02])
        return c
    ps = [P(Cyl((0, 0.07, 0), 0.085, 0.07, rr=0.02), Mat(fn=fn, spec=0.6, shin=30), 0.0)]
    ps.append(P(Cyl((0, 0.135, 0), 0.07, 0.03), BLACK, 0.0, op='sub'))
    rs = np.random.RandomState(4)
    cols = [(0.9, 0.1, 0.1), (0.3, 0.2, 0.8), (0.95, 0.85, 0.2), (0.2, 0.8, 0.3), (0.9, 0.9, 0.9), (0.5, 0.15, 0.6)]
    for i in range(14):
        a = rs.uniform(0, 6.28); r = rs.uniform(0, 0.06)
        c = (np.cos(a) * r, 0.135 + rs.uniform(0, 0.03) + (0.06 - r) * 0.4, np.sin(a) * r)
        if i % 2:
            ps.append(P(Sphere(c, 0.017), Mat(cols[i % 6], spec=0.8, shin=40), 0.0))
        else:
            ps.append(P(Box(c, (0.022, 0.01, 0.012), R=rot(0, a, 0.3)), stripes(cols[i % 6], (1, 1, 1), 120), 0.0))
    ps.append(P(Torus((0, 0.17, 0), 0.08, 0.005, R=rot(1.4, 0, 0)), BLACK, 0.0))
    return ps


def brew():
    liquid = Mat(fn=lambda p, n: np.tile(np.array([0.85, 0.3, 1.0]), (len(p), 1)) * (0.6 + 0.6 * np.clip(n[:, 2], 0, 1) ** 2)[:, None], glow=1.0)
    ps = [P(Sphere((0, 0.085, 0), 0.075), liquid, 0.0)]
    ps.append(P(Cyl((0, 0.17, 0), 0.022, 0.035), Mat((0.5, 0.6, 0.7), spec=1.0, shin=60), 0.01))
    ps.append(P(Cyl((0, 0.215, 0), 0.026, 0.016), WOOD, 0.0))
    ps.append(P(Ellipsoid((-0.03, 0.12, 0.06), (0.012, 0.02, 0.008)), GLASS_HL, 0.0))
    # little skull label
    ps.append(P(Sphere((0, 0.09, 0.07), 0.018), BONE, 0.004))
    for s in (-1, 1):
        ps.append(P(Sphere((s * 0.007, 0.093, 0.086), 0.005), BLACK, 0.0, op='sub'))
    return ps


def armor():
    olive = Mat(fn=lambda p, n: np.tile(np.array([0.24, 0.26, 0.2]), (len(p), 1)) * (0.75 + 0.4 * fbm(p, 16, 2, 6))[:, None]
                * (1 - 0.35 * (np.abs(np.sin(p[:, 1] * 70)) < 0.15))[:, None], spec=0.3)
    ps = []
    ps.append(P(Box((0, 0.17, 0), (0.12, 0.13, 0.045), r=0.04), olive, 0.0))
    ps.append(P(Ellipsoid((0, 0.32, 0.0), (0.06, 0.05, 0.06)), BLACK, 0.02, op='sub'))
    for s in (-1, 1):
        ps.append(P(Ellipsoid((s * 0.13, 0.27, 0), (0.05, 0.08, 0.06)), BLACK, 0.02, op='sub'))
    # skull emblem
    sk = np.array([0, 0.19, 0.045])
    ps.append(P(Ellipsoid(sk, (0.035, 0.038, 0.012)), BONE, 0.005))
    for s in (-1, 1):
        ps.append(P(Sphere(sk + np.array([s * 0.013, 0.004, 0.01]), 0.009), BLACK, 0.0, op='sub'))
    ps.append(P(Box(sk + np.array([0, -0.04, 0.0]), (0.02, 0.008, 0.01)), BONE, 0.003))
    # straps & buckles
    for s in (-1, 1):
        ps.append(P(Box((s * 0.08, 0.1, 0.047), (0.012, 0.01, 0.004)), BRASS, 0.0))
    return ps


def bullets():
    ps = [P(Box((0, 0.045, 0), (0.07, 0.045, 0.045), r=0.004), CARD_RED, 0.0)]
    ps.append(P(Box((0, 0.09, 0.0), (0.062, 0.02, 0.037)), BLACK, 0.0, op='sub'))
    for i in range(4):
        for j in range(2):
            c = np.array([-0.045 + i * 0.03, 0.075, -0.015 + j * 0.03])
            ps.append(P(Cyl(c, 0.011, 0.012), BRASS, 0.0))
            ps.append(P(Cone(c + np.array([0, 0.01, 0]), c + np.array([0, 0.035, 0]), 0.011, 0.003), SILVER, 0.0))
    # label stripe
    ps.append(P(Box((0, 0.04, 0.046), (0.05, 0.015, 0.002)), Mat((0.95, 0.85, 0.5)), 0.0))
    return ps


def shells():
    ps = []
    for i, (x, y, z) in enumerate(((-0.04, 0.02, 0.02), (0.0, 0.02, 0.02), (0.04, 0.02, 0.02), (-0.02, 0.058, 0.0), (0.02, 0.058, 0.0))):
        c = np.array([x, y, z])
        R = rot(np.pi / 2, 0, 0)
        ps.append(P(Cyl(c, 0.019, 0.05, R=R, rr=0.004), Mat((0.75, 0.08, 0.06), spec=0.5, shin=30), 0.0))
        ps.append(P(Cyl(c + np.array([0, 0, 0.042]), 0.02, 0.012, R=R), BRASS, 0.0))
    return ps


def pumpkin_bomb(r=0.05, lit=True, fuse=True):
    ps = [P(Pumpkin((0, r * 0.85, 0), r, 0.82, 8, 0.08), pumpkin_mat(seed=13), 0.0)]
    jack_face(ps, np.array([0, r * 0.85, 0]), r, fierce=1.2)
    if fuse:
        top = np.array([0, r * 1.55, 0])
        ps.append(P(Cone(top, top + np.array([0.01, r * 0.5, 0.0]), r * 0.12, r * 0.08), IRON, 0.0))
        if lit:
            ps.append(P(Sphere(top + np.array([0.012, r * 0.62, 0]), r * 0.22), FIREBALL, 0.0, disp=(r * 0.08, 60, 2)))
    return ps


def pumpkin_ammo():
    ps = [P(Box((0, 0.04, 0), (0.1, 0.04, 0.06), r=0.006), Mat(fn=lambda p, n: np.tile(np.array([0.45, 0.3, 0.16]), (len(p), 1)) *
                                                                (0.7 + 0.4 * fbm(p * np.array([1, 8, 1]), 20, 2, 3))[:, None]), 0.0)]
    for x in (-0.06, 0.0, 0.06):
        for pr in pumpkin_bomb(0.04, lit=False):
            if hasattr(pr, 'c'):
                pass
        sub = pumpkin_bomb(0.04, lit=False)
        ps += tilt_scene(sub, 0, 0, shift=(x, 0.075, 0.0))
    return ps


def gun_side(kind):
    """Weapon pickup lying sideways (viewed from the side)."""
    ps = []
    if kind == 'shotgun':
        for dy in (0.0, 0.022):
            ps.append(P(Cyl((0.08, 0.05 + dy, 0), 0.012, 0.16, R=rot(0, 0, np.pi / 2)), IRON, 0.0))
        ps.append(P(Box((-0.1, 0.055, 0), (0.05, 0.022, 0.016), R=rot(0, 0, -0.1), r=0.008), WOOD, 0.0))
        ps.append(P(Box((-0.2, 0.04, 0), (0.06, 0.03, 0.015), R=rot(0, 0, -0.25), r=0.01), WOOD, 0.0))
        ps.append(P(Box((-0.04, 0.05, 0), (0.03, 0.025, 0.017), r=0.004), IRON, 0.0))
    elif kind == 'tommy':
        ps.append(P(Cyl((0.12, 0.06, 0), 0.014, 0.1, R=rot(0, 0, np.pi / 2)), IRON, 0.0))
        ps.append(P(Cyl((0.07, 0.06, 0), 0.02, 0.05, R=rot(0, 0, np.pi / 2)), IRON, 0.0, disp=(0.002, 200, 3)))
        ps.append(P(Box((-0.04, 0.065, 0), (0.07, 0.025, 0.018), r=0.006), IRON, 0.0))
        ps.append(P(Cyl((-0.01, 0.025, 0), 0.05, 0.016, R=rot(np.pi / 2, 0, 0)), IRON, 0.0))
        ps.append(P(Box((-0.16, 0.05, 0), (0.07, 0.025, 0.015), R=rot(0, 0, -0.2), r=0.01), WOOD, 0.0))
        ps.append(P(Box((0.06, 0.035, 0), (0.012, 0.03, 0.014), R=rot(0, 0, 0.3), r=0.006), WOOD, 0.0))
    elif kind == 'launcher':
        ps.append(P(Cyl((0.0, 0.07, 0), 0.05, 0.2, R=rot(0, 0, np.pi / 2)), Mat((0.28, 0.32, 0.2), var=0.2, vfreq=20, spec=0.4), 0.0))
        ps.append(P(Cyl((0.2, 0.07, 0), 0.056, 0.02, R=rot(0, 0, np.pi / 2)), pumpkin_mat(), 0.0))
        ps.append(P(Cyl((0.22, 0.07, 0), 0.04, 0.03, R=rot(0, 0, np.pi / 2)), BLACK, 0.0, op='sub'))
        ps.append(P(Box((-0.02, 0.01, 0), (0.015, 0.035, 0.015), r=0.005), DWOOD, 0.0))
        for x in (-0.12, 0.1):
            ps.append(P(Torus((x, 0.07, 0), 0.052, 0.006, R=rot(0, 0, np.pi / 2)), BRASS, 0.0))
    return ps


def skull_key(color):
    gem = Mat(color, glow=1.0)
    ps = []
    sk = np.array([0, 0.2, 0])
    ps.append(P(Ellipsoid(sk, (0.04, 0.045, 0.04)), BRASS, 0.0))
    ps.append(P(Ellipsoid(sk + np.array([0, -0.03, 0.01]), (0.026, 0.022, 0.025)), BRASS, 0.01))
    for s in (-1, 1):
        ps.append(P(Sphere(sk + np.array([s * 0.016, 0.004, 0.035]), 0.012), gem, 0.0, op='sub'))
        ps.append(P(Sphere(sk + np.array([s * 0.016, 0.004, 0.028]), 0.01), gem, 0.0))
    ps.append(P(Cyl(sk + np.array([0, -0.1, 0]), 0.009, 0.06), BRASS, 0.0))
    for y in (-0.13, -0.15):
        ps.append(P(Box(sk + np.array([0.018, y, 0]), (0.012, 0.006, 0.005)), BRASS, 0.0))
    ps.append(P(Torus(sk + np.array([0, -0.05, 0]), 0.016, 0.005), BRASS, 0.0))
    return ps

# ------------------------------------------------------------------ decorations

def jack(r=0.12, seed=2):
    hc = np.array([0, r * 0.8, 0])
    ps = [P(Pumpkin(hc, r, 0.8, 10, 0.08), pumpkin_mat(seed=seed), 0.0)]
    jack_face(ps, hc, r, fierce=1.0 + 0.3 * (seed % 2))
    ps.append(P(Cone(hc + np.array([0, r * 0.7, 0]), hc + np.array([0.02, r * 1.1, -0.01]), 0.016, 0.01), STEM, 0.01))
    return ps


def candles():
    ps = []
    for (x, z, h) in ((-0.05, 0.0, 0.16), (0.03, 0.03, 0.12), (0.06, -0.04, 0.2), (-0.02, -0.05, 0.09)):
        ps.append(P(Cyl((x, h / 2, z), 0.018, h / 2), WAX, 0.004, disp=(0.002, 50, int(h * 100))))
        for k in range(2):
            a = k * 2.5 + x * 50
            ps.append(P(Cone((x + np.cos(a) * 0.017, h - 0.005, z + np.sin(a) * 0.017), (x + np.cos(a) * 0.019, h - 0.04, z + np.sin(a) * 0.019), 0.005, 0.003), WAX, 0.004))
        ps.append(P(Cone((x, h + 0.008, z), (x, h + 0.045, z), 0.009, 0.001), FLAME, 0.0))
    ps.append(P(Ellipsoid((0, 0.005, -0.01), (0.12, 0.008, 0.08)), WAX, 0.02))
    return ps


def dead_tree(seed=1):
    bark = Mat(fn=lambda p, n: np.tile(np.array([0.24, 0.2, 0.17]), (len(p), 1)) *
               (0.6 + 0.6 * fbm(p * np.array([4, 1, 4]), 18, 2, seed))[:, None])
    rs = np.random.RandomState(seed)
    ps = []

    def branch(a, d, length, r, depth):
        b = a + d * length
        ps.append(P(Cone(a, b, r, r * 0.65), bark, 0.02 if depth < 2 else 0.005))
        if depth >= 4 or r < 0.006:
            return
        n = 2 if depth > 0 else 3
        for i in range(n):
            ang = rs.uniform(0.35, 0.9) * (1 if i % 2 else -1)
            twist = rs.uniform(-1.2, 1.2)
            nd = rot(twist * 0.4, twist, ang) @ d
            nd = norm(nd + np.array([0, 0.25, 0]))
            branch(b, nd, length * rs.uniform(0.55, 0.75), r * 0.6, depth + 1)
    # trunk with roots
    ps.append(P(Cone((0, 0, 0), (0.02, 0.55, 0), 0.07, 0.045), bark, 0.0, disp=(0.008, 20, seed)))
    for i in range(4):
        a = i * 1.6 + 0.3
        ps.append(P(Cone((0, 0.05, 0), (np.cos(a) * 0.14, -0.01, np.sin(a) * 0.14), 0.035, 0.01), bark, 0.04))
    branch(np.array([0.02, 0.5, 0]), norm(np.array([0.1, 1, 0])), 0.3, 0.04, 0)
    return ps


def tombstone(kind=0, seed=0):
    ps = []
    tilt = rot(0, 0, 0.06 * (1 if seed % 2 else -1))
    if kind == 0:
        ps.append(P(Box((0, 0.17, 0), (0.12, 0.17, 0.035), R=tilt, r=0.008), STONE, 0.0, disp=(0.003, 30, seed)))
        ps.append(P(Cyl((0, 0.33, 0), 0.12, 0.035, R=tilt @ rot(np.pi / 2, 0, 0)), STONE, 0.01, disp=(0.003, 30, seed)))
        # engraved cross + RIP lines
        ps.append(P(Box((0, 0.3, 0.035), (0.008, 0.05, 0.006), R=tilt), BLACK, 0.0, op='sub'))
        ps.append(P(Box((0, 0.32, 0.035), (0.03, 0.008, 0.006), R=tilt), BLACK, 0.0, op='sub'))
        for i, w in enumerate((0.07, 0.05, 0.06)):
            ps.append(P(Box((0, 0.18 - i * 0.035, 0.035), (w, 0.005, 0.005), R=tilt), BLACK, 0.0, op='sub'))
    else:
        ps.append(P(Box((0, 0.24, 0), (0.025, 0.24, 0.025), R=tilt, r=0.005), STONE, 0.0, disp=(0.003, 30, seed)))
        ps.append(P(Box((0, 0.36, 0), (0.12, 0.025, 0.025), R=tilt, r=0.005), STONE, 0.005, disp=(0.003, 30, seed + 1)))
        ps.append(P(Box((0, 0.03, 0), (0.08, 0.03, 0.06), r=0.006), STONE, 0.01))
    # dirt mound
    ps.append(P(Ellipsoid((0, 0.0, 0.12), (0.13, 0.04, 0.18)), Mat((0.22, 0.16, 0.1), var=0.3, vfreq=20), 0.03))
    return ps


def skeleton_hanging():
    ps = []
    top = np.array([0, 1.0, 0])
    ps.append(P(Cyl((0, 0.95, 0), 0.006, 0.06), IRON, 0.0))
    neck = np.array([0, 0.86, 0])
    ps.append(P(Cone(top, neck + np.array([0, 0.03, 0]), 0.004, 0.004), Mat((0.55, 0.45, 0.3), var=0.2), 0.0))
    hc = neck + np.array([0.0, -0.005, 0.02])
    ps.append(P(Ellipsoid(hc, (0.045, 0.05, 0.046)), BONE, 0.0))
    ps.append(P(Ellipsoid(hc + np.array([0, -0.035, 0.015]), (0.03, 0.02, 0.03)), BONE, 0.01))
    for s in (-1, 1):
        ps.append(P(Sphere(hc + np.array([s * 0.017, 0.005, 0.038]), 0.013), BLACK, 0.003, op='sub'))
    ps.append(P(Cone(neck, neck + np.array([0, -0.33, 0]), 0.012, 0.012), BONE, 0.0))
    for i in range(5):
        y = neck[1] - 0.07 - i * 0.032
        ps.append(P(Torus((0, y, 0), 0.06 - i * 0.004, 0.006, R=rot(0.25, 0, 0)), BONE, 0.0))
    pelvis = neck + np.array([0, -0.33, 0])
    ps.append(P(Ellipsoid(pelvis, (0.06, 0.03, 0.035)), BONE, 0.0))
    for s in (-1, 1):
        sh = neck + np.array([s * 0.07, -0.05, 0])
        el = sh + np.array([s * 0.03, -0.14, 0.02])
        hd = el + np.array([0, -0.13, 0.03])
        ps.append(P(Cone(sh, el, 0.008, 0.007), BONE, 0.003))
        ps.append(P(Cone(el, hd, 0.007, 0.006), BONE, 0.003))
        hip = pelvis + np.array([s * 0.035, -0.01, 0])
        kn = hip + np.array([s * 0.01, -0.2, 0.01])
        ft = kn + np.array([0, -0.19, 0.0])
        ps.append(P(Cone(hip, kn, 0.01, 0.008), BONE, 0.003))
        ps.append(P(Cone(kn, ft, 0.008, 0.007), BONE, 0.003))
    return ps


def cauldron():
    ps = [P(Sphere((0, 0.14, 0), 0.15), IRON, 0.0)]
    ps.append(P(Box((0, 0.3, 0), (0.2, 0.08, 0.2)), BLACK, 0.0, op='sub'))
    ps.append(P(Torus((0, 0.22, 0), 0.13, 0.016), IRON, 0.0))
    ps.append(P(Cyl((0, 0.205, 0), 0.125, 0.006), SLIME, 0.0, disp=(0.004, 40, 3)))
    for (x, z, r) in ((0.03, 0.04, 0.02), (-0.05, 0.0, 0.016), (0.02, -0.06, 0.014)):
        ps.append(P(Sphere((x, 0.215, z), r), SLIME, 0.0))
    for a in (0.5, 2.6, 4.7):
        ps.append(P(Cone((np.cos(a) * 0.1, 0.06, np.sin(a) * 0.1), (np.cos(a) * 0.13, 0.0, np.sin(a) * 0.13), 0.02, 0.012), IRON, 0.01))
    # embers under it
    for i in range(5):
        a = i * 1.3
        ps.append(P(Sphere((np.cos(a) * 0.06, 0.012, np.sin(a) * 0.06), 0.02), FIRE2, 0.0))
    return ps


def keg():
    def fn(p, n):
        c = np.tile(np.array([0.45, 0.27, 0.13]), (len(p), 1))
        ang = np.arctan2(p[:, 2], p[:, 0])
        c *= (0.7 + 0.35 * fbm(p * np.array([1, 6, 1]), 25, 2, 7))[:, None]
        c *= (0.75 + 0.25 * (np.abs(np.sin(ang * 9)) > 0.12))[:, None]
        # skull & crossbones on front
        x, y = p[:, 0], p[:, 1]
        front = p[:, 2] > 0.06
        sk = (x ** 2 / 0.03 ** 2 + (y - 0.2) ** 2 / 0.032 ** 2) < 1
        holes = ((np.abs(x) - 0.012) ** 2 + (y - 0.205) ** 2) < 0.008 ** 2
        bones = (np.abs(np.abs(x) - (y - 0.13) * 1.6) < 0.007) & (np.abs(y - 0.12) < 0.035)
        bones |= (np.abs(np.abs(x) + (y - 0.11) * 1.6) < 0.007) & (np.abs(y - 0.12) < 0.035)
        m = front & (sk | bones) & ~holes
        c[m] = np.array([0.92, 0.9, 0.8])
        return c
    ps = []
    def body(p):
        r = 0.11 + 0.02 * np.cos((p[:, 1] - 0.16) / 0.16 * 1.4)
        dxz = np.sqrt(p[:, 0] ** 2 + p[:, 2] ** 2) - r
        dy = np.abs(p[:, 1] - 0.16) - 0.16
        return np.maximum(dxz, dy)
    ps.append(P(Func(body), Mat(fn=fn, spec=0.2), 0.0))
    for y in (0.04, 0.28):
        ps.append(P(Torus((0, y, 0), 0.118, 0.008), IRON, 0.0))
    ps.append(P(Cone((0.02, 0.32, 0.03), (0.04, 0.37, 0.05), 0.006, 0.004), Mat((0.75, 0.7, 0.55)), 0.0))
    return ps


def skull_pile():
    rs = np.random.RandomState(3)
    ps = []
    pos = [(-0.07, 0.04, 0.0), (0.07, 0.04, 0.02), (0.0, 0.04, 0.07), (0.0, 0.11, 0.02), (-0.08, 0.035, -0.08), (0.08, 0.035, -0.06)]
    for i, c in enumerate(pos):
        c = np.asarray(c)
        R = rot(rs.uniform(-0.3, 0.3), rs.uniform(-0.8, 0.8), rs.uniform(-0.3, 0.3))
        f = R @ np.array([0, 0, 1.0])
        ps.append(P(Ellipsoid(c, (0.045, 0.045, 0.05), R=R), BONE, 0.0))
        ps.append(P(Ellipsoid(c + f * 0.03 + np.array([0, -0.03, 0]), (0.03, 0.02, 0.025), R=R), BONE, 0.005))
        side = R @ np.array([1.0, 0, 0])
        for s in (-1, 1):
            ps.append(P(Sphere(c + f * 0.04 + side * s * 0.017 + np.array([0, 0.005, 0]), 0.012), BLACK, 0.002, op='sub'))
    ps.append(P(Cone((-0.15, 0.01, 0.05), (0.12, 0.015, 0.1), 0.01, 0.01), BONE, 0.0))
    return ps


def lamppost():
    glass = Mat((1.0, 0.85, 0.45), glow=1.0)
    ps = [P(Cyl((0, 0.6, 0), 0.018, 0.6), IRON, 0.0)]
    ps.append(P(Cyl((0, 0.04, 0), 0.05, 0.04, rr=0.01), IRON, 0.01))
    ps.append(P(Box((0, 1.27, 0), (0.05, 0.07, 0.05), r=0.01), glass, 0.0))
    for s in (-1, 1):
        for t in (-1, 1):
            ps.append(P(Box((s * 0.05, 1.27, t * 0.05), (0.007, 0.075, 0.007)), IRON, 0.0))
    ps.append(P(Cone((0, 1.34, 0), (0, 1.42, 0), 0.075, 0.005), IRON, 0.0))
    ps.append(P(Box((0, 1.2, 0), (0.065, 0.01, 0.065)), IRON, 0.0))
    return ps


def pumpkin_patch():
    ps = []
    for (x, z, r, sd) in ((-0.1, 0.0, 0.09, 1), (0.08, 0.03, 0.07, 2), (0.0, -0.1, 0.06, 3)):
        hc = np.array([x, r * 0.78, z])
        ps.append(P(Pumpkin(hc, r, 0.78, 10, 0.08), pumpkin_mat(seed=sd), 0.0))
        ps.append(P(Cone(hc + np.array([0, r * 0.7, 0]), hc + np.array([0.015, r * 1.05, 0]), 0.012, 0.008), STEM, 0.005))
    for i in range(6):
        a = i * 1.1
        ps.append(P(Cone((np.cos(a) * 0.05, 0.01, np.sin(a) * 0.05), (np.cos(a) * 0.2, 0.005, np.sin(a) * 0.2), 0.006, 0.004), Mat((0.2, 0.35, 0.1), var=0.2), 0.0))
    return ps

# ------------------------------------------------------------------ projectiles

def fireball(seed=0, green=False):
    m = GREENFIRE if green else FIREBALL
    ps = [P(Sphere((0, 0.08, 0), 0.055), m, 0.0, disp=(0.012, 25, seed))]
    for i in range(5):
        a = i * 1.25 + seed
        ps.append(P(Cone((np.cos(a) * 0.03, 0.08 + np.sin(a) * 0.03, -0.02), (np.cos(a) * 0.09, 0.08 + np.sin(a) * 0.09, -0.06), 0.025, 0.003), m, 0.03))
    return ps


def gibs(seed=1):
    rs = np.random.RandomState(seed)
    meat = Mat((0.45, 0.06, 0.05), var=0.3, vfreq=30, spec=0.6, shin=30)
    ps = [P(Ellipsoid((0, 0.0, 0), (0.28, 0.012, 0.18)), BLOOD, 0.0)]
    for i in range(9):
        c = (rs.uniform(-0.18, 0.18), rs.uniform(0.01, 0.04), rs.uniform(-0.1, 0.1))
        ps.append(P(Ellipsoid(c, (rs.uniform(0.02, 0.045), rs.uniform(0.015, 0.03), rs.uniform(0.02, 0.04)), R=rot(0, rs.uniform(0, 3), 0)), meat, 0.01, disp=(0.006, 40, i)))
    for i in range(3):
        a = np.array([rs.uniform(-0.15, 0.1), 0.02, rs.uniform(-0.08, 0.08)])
        ps.append(P(Cone(a, a + np.array([rs.uniform(0.06, 0.1), 0.01, rs.uniform(-0.03, 0.03)]), 0.008, 0.008), BONE, 0.0))
        ps.append(P(Sphere(a, 0.012), BONE, 0.004))
    ps.append(P(Ellipsoid((0.05, 0.035, 0.0), (0.04, 0.035, 0.035)), BONE, 0.0))
    ps.append(P(Sphere((0.06, 0.04, 0.03), 0.01), BLACK, 0.0, op='sub'))
    return ps


def corpse_frames(fn, pool=BLOOD, pool_r=(0.3, 0.012, 0.14)):
    """Return (falling, dead) scenes for a monster function."""
    base = fn('pain')
    fall = tilt_scene(base, ang_z=0.55, pivot=(0, 0, 0), shift=(0.05, -0.02, 0))
    dead = tilt_scene(fn('pain'), ang_z=1.48, pivot=(0, 0, 0), shift=(0.36, 0.06, 0))
    dead = [P(Ellipsoid((0.0, -0.005, 0.02), pool_r), pool, 0.0)] + dead
    return fall, dead


def wraith_death(stage):
    base = wraith('pain')
    if stage == 0:
        return tilt_scene(base, 0.0, 0.0, shift=(0, -0.18, 0))
    ecto = Mat((0.45, 0.9, 0.95), glow=1.0)
    shroud = Mat((0.4, 0.44, 0.5), var=0.4, vfreq=7)
    ps = [P(Ellipsoid((0, 0.0, 0), (0.24, 0.012, 0.14)), ecto, 0.0)]
    ps.append(P(Ellipsoid((-0.03, 0.03, 0), (0.17, 0.035, 0.1)), shroud, 0.04, disp=(0.012, 9, 3)))
    sc = np.array([0.06, 0.07, 0.03])
    ps.append(P(Ellipsoid(sc, (0.045, 0.05, 0.046)), BONE, 0.0))
    for s in (-1, 1):
        ps.append(P(Sphere(sc + np.array([s * 0.018, 0.008, 0.038]), 0.015), BLACK, 0.003, op='sub'))
    return ps
