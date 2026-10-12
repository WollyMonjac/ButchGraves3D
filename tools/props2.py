"""Props for episodes 2/3, death frames for the new monsters, Butch's full body and cutscene actors (SDF)."""
import numpy as np
from sdf import *
from monsters import (limb, cloth, tilt_scene, TriPrism, Pumpkin, pumpkin_mat, jack_face, fire_mat, BONE, TEETH, MOUTH, BLOOD,
                      BLACK, FIREBALL, FIRE, STEM, EYE_YEL, GREENFIRE)
import monsters2 as M2
from monsters2 import V, OLD_BONE, STEEL, GOLD, GLOSS_RED, RUST, EYE_BLOOD, FANG, knife_prims
from props import IRON, BRASS, WOOD, DWOOD, STONE, FLAME, WAX, corpse_frames
import hero as HERO
from weapons import JACKET, GUNMETAL, GLOVE

GLASS_G = Mat((0.35, 1.0, 0.45), glow=1.0)
BULB = [Mat((1.0, 0.25, 0.2), glow=1.0), Mat((1.0, 0.85, 0.25), glow=1.0), Mat((0.35, 0.6, 1.0), glow=1.0), Mat((0.4, 1.0, 0.4), glow=1.0)]
ASH = Mat(fn=lambda p, n: np.tile(np.array([0.36, 0.34, 0.33]), (len(p), 1)) * (0.6 + 0.6 * fbm(p, 30, 2, 201))[:, None])
WHITE = Mat((0.92, 0.9, 0.86), var=0.08, vfreq=20, spec=0.3)


# ------------------------------------------------------------------ death frames

def skel_fall():
    return tilt_scene(M2.skeleton('pain'), ang_z=0.5, shift=(0.05, -0.04, 0))


def skel_dead():
    """Collapsed heap of bones with the skull on top."""
    ps = []
    rs = np.random.RandomState(5)
    for k in range(12):
        a = rs.uniform(0, np.pi); c = V(rs.uniform(-0.14, 0.14), 0.012 + rs.uniform(0, 0.02), rs.uniform(-0.05, 0.06))
        d = V(np.cos(a), rs.uniform(-0.1, 0.25), np.sin(a) * 0.3) * rs.uniform(0.05, 0.1)
        limb(ps, c - d, c + d, 0.011, 0.011, OLD_BONE, 0.004)
        ps.append(P(Sphere(c + d, 0.015), OLD_BONE, 0.004))
    M2_ribs = []
    for i in range(4):
        y = 0.03
        ps.append(P(Torus(V(-0.02, y + i * 0.012, -0.01 + i * 0.012), 0.05 - i * 0.004, 0.006, R=rot(1.3, 0.3, 0.2)), OLD_BONE, 0.002))
    hc = V(0.04, 0.07, 0.04)
    ps.append(P(Ellipsoid(hc, (0.06, 0.065, 0.064)), OLD_BONE, 0.0))
    for s in (-1, 1):
        ec = hc + V(s * 0.025, 0.0, 0.054)
        ps.append(P(Sphere(ec, 0.02), BLACK, 0.004, op='sub'))
    ps.append(P(Box(hc + V(0, -0.05, 0.05), (0.03, 0.006, 0.006)), TEETH, 0.0))
    return ps


def bat_fall():
    return tilt_scene(M2.bat('pain'), ang_z=1.2, shift=(0.02, -0.08, 0))


def bat_dead():
    return tilt_scene(M2.bat('walk2'), ang_x=-1.3, pivot=(0, 0.16, 0), shift=(0, -0.13, 0)) + \
        [P(Ellipsoid((0, 0.0, 0.0), (0.09, 0.006, 0.05)), BLOOD, 0.0)]


def vamp_fall():
    return tilt_scene(M2.vampire('pain'), ang_z=0.0, shift=(0, -0.2, 0)) + [P(Ellipsoid((0, 0.02, 0.0), (0.2, 0.03, 0.1)), ASH, 0.04)]


def ash_pile(w=0.2, cloth_mat=None, extra=None):
    ps = [P(Ellipsoid((0, 0.0, 0.0), (w, 0.05, w * 0.55)), ASH, 0.05, disp=(0.01, 20, 3))]
    ps.append(P(Cone((0.02, 0.0, 0.0), (0.0, 0.09, 0.0), w * 0.6, 0.02), ASH, 0.05, disp=(0.008, 25, 4)))
    if cloth_mat is not None:
        ps.append(P(Ellipsoid((-0.05, 0.02, 0.04), (w * 0.9, 0.025, w * 0.5)), cloth_mat, 0.02, disp=(0.012, 9, 5)))
    for s in (-1, 1):
        ps.append(P(Sphere((s * w * 0.6, 0.015, 0.05), 0.02), ASH, 0.01))
    if extra:
        ps += extra
    return ps


def vamp_dead():
    return ash_pile(0.17, cloth((0.86, 0.84, 0.8), seed=111, blood=0.2))


def giggles_fall():
    return tilt_scene(M2.giggles('pain'), ang_z=0.45, shift=(0.06, -0.05, 0))


def giggles_dead():
    return [P(Ellipsoid((0, -0.005, 0.03), (0.75, 0.015, 0.3)), BLOOD, 0.0)] + \
        tilt_scene(M2.giggles('pain'), ang_z=1.48, shift=(0.85, 0.2, 0))


def count_fall():
    return tilt_scene(M2.count('pain'), ang_z=0.0, shift=(0, -0.25, 0)) + [P(Ellipsoid((0, 0.03, 0.0), (0.3, 0.05, 0.15)), ASH, 0.05)]


def count_dead():
    capei = Mat((0.55, 0.03, 0.06), spec=0.6, shin=25)
    gem = Mat((1.0, 0.1, 0.1), glow=1.0)
    extra = [P(Cyl((0.08, 0.03, 0.12), 0.03, 0.006, R=rot(0.2, 0, 0)), GOLD, 0.0), P(Sphere((0.08, 0.036, 0.13), 0.013), gem, 0.0)]
    return ash_pile(0.28, capei, extra)


# ------------------------------------------------------------------ projectiles (frames)

def knife1():
    return M2.knife_proj(0)


def knife2():
    return M2.knife_proj(1)


# ------------------------------------------------------------------ E2 props: town and carnival

def streetlamp():
    ps = [P(Cyl((0, 0.02, 0), 0.06, 0.02), IRON, 0.01), P(Cone((0, 0.02, 0), (0, 1.25, 0), 0.03, 0.02), IRON, 0.02)]
    ps.append(P(Cone((0, 1.2, 0), (0.18, 1.3, 0), 0.016, 0.014), IRON, 0.02))
    ps.append(P(Cone((0.18, 1.3, 0), (0.22, 1.22, 0), 0.014, 0.012), IRON, 0.01))
    ps.append(P(Ellipsoid((0.22, 1.17, 0), (0.07, 0.03, 0.07)), IRON, 0.01))
    ps.append(P(Sphere((0.22, 1.13, 0.0), 0.045), Mat((1.0, 0.9, 0.6), glow=1.0), 0.0))
    return ps


def balloons():
    cols = [GLOSS_RED, Mat((0.95, 0.85, 0.1), spec=1.0, shin=60), Mat((0.15, 0.4, 0.95), spec=1.0, shin=60),
            Mat((0.2, 0.75, 0.25), spec=1.0, shin=60), Mat((0.75, 0.2, 0.75), spec=1.0, shin=60)]
    ps = [P(Cyl((0, 0.08, 0), 0.012, 0.08), WOOD, 0.0), P(Box((0, 0.17, 0.0), (0.04, 0.012, 0.012)), WOOD, 0.004)]
    rs = np.random.RandomState(4)
    for k in range(7):
        c = V(rs.uniform(-0.17, 0.17), rs.uniform(0.62, 0.9), rs.uniform(-0.08, 0.08))
        limb(ps, V(0, 0.17, 0), c - V(0, 0.08, 0), 0.0025, 0.0025, WHITE, 0.0)
        ps.append(P(Ellipsoid(c, (0.065, 0.078, 0.065)), cols[k % 5], 0.0))
    return ps


def carousel():
    """A cracked carousel horse impaled on a brass pole, eyes glowing."""
    paint = Mat(fn=lambda p, n: np.tile(np.array([0.88, 0.84, 0.76]), (len(p), 1)) *
                (0.65 + 0.4 * fbm(p, 20, 3, 211))[:, None] * (1 - 0.6 * (np.abs(fbm(p, 12, 2, 212) - 0.5) < 0.02))[:, None], spec=0.6)
    mane = Mat((0.65, 0.1, 0.12), var=0.3, vfreq=30, spec=0.5)
    saddle = Mat((0.2, 0.25, 0.65), var=0.2, vfreq=20, spec=0.6)
    ps = [P(Cyl((0, 0.03, 0), 0.12, 0.03), BRASS, 0.01), P(Cone((0, 0.0, 0), (0, 1.3, 0), 0.016, 0.016), BRASS, 0.0)]
    body = V(0, 0.62, 0.0)
    ps.append(P(Ellipsoid(body, (0.08, 0.1, 0.24)), paint, 0.04))
    ps.append(P(Ellipsoid(body + V(0, 0.09, -0.02), (0.07, 0.04, 0.09)), saddle, 0.02))
    nk = body + V(0, 0.14, 0.18)
    limb(ps, body + V(0, 0.04, 0.16), nk, 0.06, 0.045, paint, 0.04)
    hd = nk + V(0, 0.03, 0.08)
    limb(ps, nk, hd, 0.045, 0.035, paint, 0.03)
    for s in (-1, 1):
        ps.append(P(Sphere(hd + V(s * 0.03, 0.02, -0.02), 0.012), Mat((1.0, 0.2, 0.1), glow=1.0), 0.0))
        ps.append(P(Cone(nk + V(s * 0.02, 0.05, -0.03), nk + V(s * 0.03, 0.1, -0.04), 0.012, 0.002), paint, 0.006))
    ps.append(P(Ellipsoid(hd + V(0, -0.02, 0.05), (0.025, 0.02, 0.025)), BLACK, 0.004, op='sub'))
    for k in range(6):
        limb(ps, nk + V(0, 0.04 - k * 0.03, -0.03 - k * 0.025), nk + V(0, 0.07 - k * 0.04, -0.09 - k * 0.025), 0.022, 0.008, mane, 0.01)
    for (dx, dz, a) in ((-0.05, 0.15, 0.6), (0.05, 0.15, 0.2), (-0.05, -0.17, -0.4), (0.05, -0.17, -0.1)):
        top = body + V(dx, -0.05, dz)
        kn = top + V(0, -0.12, np.sin(a) * 0.08)
        limb(ps, top, kn, 0.03, 0.022, paint, 0.02)
        limb(ps, kn, kn + V(0, -0.1, np.sin(a * 2) * 0.06), 0.02, 0.018, paint, 0.01)
    from weapons import transform
    pole = ps[:2]
    horse = transform(ps[2:], rot(0, -1.25, 0), (0, 0.6, 0))     # turn the horse side-on (pole stays put)
    return pole + horse


def cotton():
    pink = Mat((1.0, 0.55, 0.75), var=0.2, vfreq=30)
    stripes = Mat(fn=lambda p, n: np.where((np.sin(p[:, 0] * 60) > 0)[:, None], np.array([[0.85, 0.1, 0.12]]), np.array([[0.92, 0.9, 0.85]])))
    ps = [P(Box((0, 0.3, 0), (0.22, 0.14, 0.14), r=0.02), stripes, 0.01)]
    for s in (-1, 1):
        ps.append(P(Cyl((s * 0.18, 0.08, 0.12), 0.08, 0.015, R=rot(0, 0, np.pi / 2)), IRON, 0.0))
    ps.append(P(Cone((0, 0.44, 0), (0, 0.7, 0), 0.02, 0.02), IRON, 0.0))
    ps.append(P(Cyl((0, 0.74, 0), 0.28, 0.02), stripes, 0.0))
    for k in range(3):
        c = V(-0.1 + k * 0.1, 0.52, 0.0)
        limb(ps, c - V(0, 0.08, 0), c, 0.006, 0.006, WHITE, 0.0)
        ps.append(P(Sphere(c + V(0, 0.05, 0), 0.06), pink, 0.0, disp=(0.008, 30, k)))
    return ps


def hydrant():
    red = Mat((0.7, 0.08, 0.06), var=0.2, vfreq=30, spec=0.6)
    ps = [P(Cyl((0, 0.12, 0), 0.06, 0.12), red, 0.01), P(Cyl((0, 0.02, 0), 0.08, 0.02), red, 0.01)]
    ps.append(P(Sphere((0, 0.25, 0), 0.06), red, 0.01))
    ps.append(P(Cyl((0, 0.3, 0), 0.015, 0.02), red, 0.0))
    for s in (-1, 1):
        ps.append(P(Cyl((s * 0.075, 0.16, 0), 0.026, 0.025, R=rot(0, 0, np.pi / 2)), red, 0.005))
    ps.append(P(Cyl((0, 0.16, 0.07), 0.03, 0.02, R=rot(np.pi / 2, 0, 0)), red, 0.005))
    return ps


def trashcan():
    galv = Mat(fn=lambda p, n: np.tile(np.array([0.55, 0.56, 0.58]), (len(p), 1)) * (0.65 + 0.4 * fbm(p, 14, 3, 221))[:, None] *
               (0.85 + 0.15 * np.sin(p[:, 1] * 90))[:, None], spec=0.8, shin=30)
    ps = [P(Cyl((0, 0.17, 0), 0.11, 0.17, rr=0.01), galv, 0.0)]
    ps.append(P(Cyl((0, 0.32, 0), 0.1, 0.17), BLACK, 0.0, op='sub'))
    ps.append(P(Cyl((0.1, 0.38, 0.03), 0.125, 0.012, R=rot(0.3, 0, -0.9)), galv, 0.0))
    ps.append(P(Ellipsoid((0, 0.33, 0.0), (0.09, 0.03, 0.09)), Mat((0.3, 0.26, 0.2), var=0.5, vfreq=30), 0.01))
    ps.append(P(Sphere((0.03, 0.36, 0.02), 0.04), pumpkin_mat(), 0.0))
    return ps


def wreck():
    """Burnt-out old car, front view, headlight still glowing."""
    paint = Mat(fn=lambda p, n: np.tile(np.array([0.35, 0.12, 0.08]), (len(p), 1)) * (0.5 + 0.6 * fbm(p, 8, 3, 231))[:, None], spec=0.4)
    tire = Mat((0.06, 0.06, 0.06), var=0.2, vfreq=40)
    ps = [P(Box((0, 0.22, 0), (0.42, 0.12, 0.3), r=0.06), paint, 0.03)]
    ps.append(P(Box((0, 0.42, -0.06), (0.32, 0.1, 0.2), r=0.06), paint, 0.04))
    ps.append(P(Box((0, 0.43, 0.1), (0.28, 0.06, 0.04), R=rot(0.6, 0, 0)), Mat((0.06, 0.08, 0.1), spec=1.0), 0.0))
    for s in (-1, 1):
        ps.append(P(Cyl((s * 0.36, 0.12, 0.14), 0.11, 0.05, R=rot(0, 0, np.pi / 2)), tire, 0.01))
        ps.append(P(Sphere((s * 0.28, 0.25, 0.3), 0.045), Mat((1.0, 0.95, 0.7), glow=1.0) if s > 0 else BLACK, 0.0))
    ps.append(P(Box((0, 0.2, 0.31), (0.2, 0.05, 0.01)), STEEL, 0.01))
    ps.append(P(Box((0, 0.33, 0.25), (0.36, 0.015, 0.08), R=rot(-0.5, 0.1, 0.05)), paint, 0.0))
    return ps


def bulbs():
    ps = []
    pts = [V(-0.5 + k * 0.1, 0.92 - 0.12 * np.sin(k / 10 * np.pi), 0) for k in range(11)]
    for k in range(10):
        limb(ps, pts[k], pts[k + 1], 0.004, 0.004, BLACK, 0.0)
    for k in range(1, 10):
        ps.append(P(Sphere(pts[k] + V(0, -0.03, 0), 0.022), BULB[k % 4], 0.0))
    return ps


def clownhead():
    """Funhouse entrance sculpture: giant clown head on a pedestal with glowing eyes."""
    skin = Mat((0.92, 0.9, 0.84), var=0.25, vfreq=6, spec=0.3)
    ps = [P(Box((0, 0.15, 0), (0.18, 0.15, 0.16), r=0.02), STONE, 0.01)]
    hc = V(0, 0.52, 0.02)
    ps.append(P(Sphere(hc, 0.22), skin, 0.0, disp=(0.006, 8, 2)))
    for s in (-1, 1):
        for k in range(5):
            ps.append(P(Sphere(hc + V(s * (0.21 + 0.03 * np.cos(k)), 0.05 + 0.05 * np.sin(k * 1.3), -0.04), 0.07),
                        Mat((0.15, 0.55, 0.2), var=0.3, vfreq=30), 0.04))
        ec = hc + V(s * 0.08, 0.06, 0.18)
        ps.append(P(Sphere(ec, 0.045), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.01), 0.025), Mat((1.0, 0.3, 0.1), glow=1.0), 0.0))
    ps.append(P(Sphere(hc + V(0, -0.02, 0.22), 0.05), GLOSS_RED, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.12, 0.17), (0.13, 0.05, 0.08)), MOUTH, 0.004, op='sub'))
    for i in range(7):
        x = (i - 3) * 0.035
        ps.append(P(Cone(hc + V(x, -0.08, 0.2), hc + V(x, -0.12, 0.21), 0.012, 0.001), FANG, 0.0))
    return ps


def strongman():
    """High striker: tall red/white pole with a bell, a mallet leaning on the base."""
    stripes = Mat(fn=lambda p, n: np.where((np.sin(p[:, 1] * 50) > 0)[:, None], np.array([[0.8, 0.1, 0.1]]), np.array([[0.92, 0.9, 0.85]])) *
                  (0.7 + 0.35 * fbm(p, 10, 2, 241))[:, None])
    ps = [P(Box((0, 0.06, 0), (0.16, 0.06, 0.12), r=0.01), WOOD, 0.01), P(Box((0, 0.7, -0.02), (0.05, 0.62, 0.025)), stripes, 0.0)]
    ps.append(P(Sphere((0, 1.36, 0.02), 0.06), BRASS, 0.0))
    ps.append(P(Box((0, 0.5, 0.012), (0.012, 0.4, 0.004)), BLACK, 0.0))
    ps.append(P(Box((0, 0.42, 0.02), (0.03, 0.015, 0.012)), Mat((1.0, 0.85, 0.2), glow=1.0), 0.0))
    limb(ps, V(0.2, 0.0, 0.08), V(0.12, 0.42, 0.1), 0.014, 0.014, WOOD, 0.0)
    ps.append(P(Cyl(V(0.11, 0.46, 0.1), 0.05, 0.09, R=rot(0, 0, np.pi / 2 + 0.2)), DWOOD, 0.01))
    return ps


# ------------------------------------------------------------------ E3 props: swamp and castle

def candelabra():
    ps = [P(Cyl((0, 0.02, 0), 0.09, 0.02), IRON, 0.01), P(Cone((0, 0.0, 0), (0, 0.75, 0), 0.02, 0.014), IRON, 0.01)]
    for s in (-1, 0, 1):
        top = V(s * 0.14, 0.82 + (0.06 if s == 0 else 0), 0)
        if s:
            limb(ps, V(0, 0.7, 0), V(s * 0.1, 0.72, 0), 0.01, 0.009, IRON, 0.01)
            limb(ps, V(s * 0.1, 0.72, 0), top - V(0, 0.04, 0), 0.009, 0.009, IRON, 0.01)
        ps.append(P(Cyl(top - V(0, 0.03, 0), 0.03, 0.008), IRON, 0.0))
        ps.append(P(Cyl(top + V(0, 0.02, 0), 0.016, 0.05), WAX, 0.004))
        ps.append(P(Ellipsoid(top + V(0, 0.1, 0), (0.012, 0.025, 0.012)), FLAME, 0.0))
    return ps


def coffin():
    """Upright open coffin with red satin lining and a skeleton inside."""
    sat = Mat((0.55, 0.04, 0.06), var=0.3, vfreq=25, spec=0.7)

    def prof(p, inset):
        x, y = p[:, 0], p[:, 1]
        w = np.where(y > 0.62, 0.17 - (y - 0.62) * 0.5, 0.12 + y * 0.08) - inset
        return np.maximum(np.abs(x) - w, np.abs(y - 0.45) - (0.45 - inset))
    ps = [P(Func(lambda p: np.maximum(prof(p, 0.0), np.abs(p[:, 2]) - 0.07)), DWOOD, 0.0)]
    ps.append(P(Func(lambda p: np.maximum(prof(p, 0.025), -(p[:, 2] + 0.04))), sat, 0.0, op='sub'))
    hc = V(0, 0.73, -0.01)
    ps.append(P(Ellipsoid(hc, (0.045, 0.05, 0.045)), OLD_BONE, 0.0))
    for s in (-1, 1):
        ps.append(P(Sphere(hc + V(s * 0.018, 0.0, 0.04), 0.014), BLACK, 0.003, op='sub'))
    for i in range(4):
        ps.append(P(Torus(V(0, 0.58 - i * 0.03, -0.015), 0.05 - i * 0.003, 0.005, R=rot(np.pi / 2, 0, 0)), OLD_BONE, 0.002))
    for s in (-1, 1):
        limb(ps, V(s * 0.06, 0.6, -0.01), V(s * 0.05, 0.36, 0.0), 0.009, 0.008, OLD_BONE, 0.004)
    return ps


def cypress():
    moss = Mat((0.35, 0.4, 0.28), var=0.4, vfreq=25)
    bark = Mat(fn=lambda p, n: np.tile(np.array([0.3, 0.26, 0.2]), (len(p), 1)) * (0.5 + 0.6 * fbm(p * V(3, 0.5, 3), 12, 3, 251))[:, None])
    ps = []
    def trunk_d(p):
        y = p[:, 1]
        r = 0.05 + 0.18 * np.exp(-y * 9) + 0.01 * np.sin(np.arctan2(p[:, 2], p[:, 0]) * 7)
        d = np.sqrt(p[:, 0] ** 2 + p[:, 2] ** 2) - r
        return np.maximum(d, np.maximum(-y, y - 1.3)) * 0.8
    ps.append(P(Func(trunk_d), bark, 0.0))
    rs = np.random.RandomState(8)
    for k in range(7):
        a = rs.uniform(0, 2 * np.pi); y0 = rs.uniform(0.7, 1.2)
        b0 = V(0, y0, 0); b1 = b0 + V(np.cos(a) * 0.32, rs.uniform(0.05, 0.2), np.sin(a) * 0.2)
        limb(ps, b0, b1, 0.03, 0.012, bark, 0.02)
        for m in range(3):
            t = 0.4 + m * 0.25
            c = b0 + (b1 - b0) * t
            ps.append(P(Cone(c, c + V(rs.uniform(-0.02, 0.02), -rs.uniform(0.15, 0.35), 0), 0.03, 0.005), moss, 0.02, disp=(0.008, 30, k * 3 + m)))
    ps.append(P(Ellipsoid((0, 1.3, 0), (0.25, 0.12, 0.2)), moss, 0.05, disp=(0.03, 10, 5)))
    return ps


def tesla():
    copper = Mat((0.75, 0.4, 0.2), var=0.2, vfreq=40, spec=0.9, shin=40)
    arc = Mat((0.7, 0.85, 1.0), glow=1.0)
    ps = [P(Cyl((0, 0.06, 0), 0.14, 0.06), IRON, 0.01), P(Cyl((0, 0.45, 0), 0.07, 0.34), copper, 0.0)]
    for k in range(8):
        ps.append(P(Torus((0, 0.15 + k * 0.08, 0), 0.075, 0.008), copper, 0.0))
    ps.append(P(Torus((0, 0.88, 0), 0.12, 0.045), STEEL, 0.0))
    rs = np.random.RandomState(9)
    for k in range(4):
        a = k * 1.6 + 0.3
        p0 = V(np.cos(a) * 0.12, 0.88, np.sin(a) * 0.12)
        pts = [p0]
        for m in range(4):
            pts.append(pts[-1] + V(np.cos(a) * 0.07 + rs.uniform(-0.04, 0.04), rs.uniform(-0.06, 0.08), np.sin(a) * 0.05))
        for m in range(4):
            limb(ps, pts[m], pts[m + 1], 0.006, 0.004, arc, 0.0)
    return ps


def tank():
    """Specimen tank: glass cylinder of glowing green fluid with a body floating inside."""
    fluid = Mat(fn=lambda p, n: np.tile(np.array([0.3, 0.95, 0.4]), (len(p), 1)) * (0.6 + 0.4 * fbm(p, 10, 2, 261))[:, None], glow=1.0)
    ps = [P(Cyl((0, 0.08, 0), 0.2, 0.08), IRON, 0.01), P(Cyl((0, 0.95, 0), 0.2, 0.05), IRON, 0.01)]
    ps.append(P(Cyl((0, 0.52, 0), 0.17, 0.38), fluid, 0.0))
    for s in (-1, 1):
        ps.append(P(Cyl((s * 0.17, 0.52, 0.05), 0.012, 0.38), STEEL, 0.0))
    skin = Mat((0.35, 0.45, 0.3), var=0.3, vfreq=20)
    skin = Mat((0.12, 0.3, 0.14), var=0.3, vfreq=20)
    hc = V(0.0, 0.7, 0.16)
    ps.append(P(Ellipsoid(hc, (0.045, 0.055, 0.03)), skin, 0.0))
    ps.append(P(Box(hc + V(0, -0.02, 0.025), (0.025, 0.004, 0.006)), BLACK, 0.0))
    ps.append(P(Ellipsoid(V(0, 0.46, 0.15), (0.075, 0.17, 0.03)), skin, 0.03))
    for s in (-1, 1):
        limb(ps, V(s * 0.07, 0.56, 0.15), V(s * 0.1, 0.36, 0.16), 0.018, 0.014, skin, 0.01)
    for k in range(3):
        ps.append(P(Sphere(V(-0.08 + k * 0.07, 0.3 + k * 0.17, 0.13), 0.01), WHITE, 0.0))
    return ps


def knight():
    plate = Mat(fn=lambda p, n: np.tile(np.array([0.55, 0.56, 0.6]), (len(p), 1)) * (0.6 + 0.5 * np.clip(n[:, 1] * 0.4 + 0.6, 0, 1))[:, None] *
                (0.8 + 0.3 * fbm(p, 20, 2, 271))[:, None], spec=1.1, shin=40)
    ps = [P(Box((0, 0.03, 0), (0.15, 0.03, 0.12)), STONE, 0.0)]
    for s in (-1, 1):
        limb(ps, V(s * 0.06, 0.06, 0), V(s * 0.06, 0.42, 0), 0.04, 0.045, plate, 0.02)
        ps.append(P(Sphere(V(s * 0.06, 0.26, 0.02), 0.045), plate, 0.01))
    ps.append(P(Ellipsoid((0, 0.62, 0), (0.13, 0.17, 0.09)), plate, 0.04))
    for s in (-1, 1):
        ps.append(P(Ellipsoid(V(s * 0.14, 0.74, 0), (0.06, 0.05, 0.06)), plate, 0.02))
        limb(ps, V(s * 0.15, 0.72, 0), V(s * 0.17, 0.5, 0.04), 0.035, 0.03, plate, 0.02)
    hc = V(0, 0.88, 0)
    ps.append(P(Cyl(hc, 0.065, 0.075, rr=0.03), plate, 0.0))
    ps.append(P(Box(hc + V(0, 0.015, 0.06), (0.04, 0.006, 0.02)), BLACK, 0.0, op='sub'))
    ps.append(P(Sphere(hc + V(0.02, 0.015, 0.05), 0.006), Mat((1.0, 0.1, 0.1), glow=1.0), 0.0))
    ps.append(P(Cone(V(0.17, 0.02, 0.08), V(0.17, 1.15, 0.08), 0.01, 0.01), DWOOD, 0.0))
    ps.append(P(TriPrism(V(0.2, 1.08, 0.08), (-0.03, -0.06), (0.06, 0.0), (-0.03, 0.06), 0.004), STEEL, 0.0))
    ps.append(P(Cone(V(0.17, 1.12, 0.08), V(0.17, 1.24, 0.08), 0.012, 0.001), STEEL, 0.0))
    return ps


def cage():
    ps = [P(Cone((0, 1.0, 0), (0, 0.98, 0), 0.01), IRON, 0.0)]
    limb(ps, V(0, 1.0, 0), V(0, 0.85, 0), 0.006, 0.006, IRON, 0.0)
    ps.append(P(Ellipsoid((0, 0.82, 0), (0.15, 0.06, 0.15)), IRON, 0.0))
    ps.append(P(Cyl((0, 0.45, 0), 0.15, 0.015), IRON, 0.0))
    for k in range(9):
        a = k * 2 * np.pi / 9
        limb(ps, V(np.cos(a) * 0.15, 0.45, np.sin(a) * 0.15), V(np.cos(a) * 0.14, 0.82, np.sin(a) * 0.14), 0.007, 0.007, IRON, 0.0)
    hc = V(0.02, 0.58, 0.03)
    ps.append(P(Ellipsoid(hc, (0.045, 0.05, 0.045)), OLD_BONE, 0.0))
    for s in (-1, 1):
        ps.append(P(Sphere(hc + V(s * 0.018, 0.0, 0.04), 0.014), BLACK, 0.003, op='sub'))
    limb(ps, V(-0.06, 0.48, 0.05), V(0.06, 0.62, 0.08), 0.008, 0.008, OLD_BONE, 0.0)
    limb(ps, V(-0.04, 0.49, 0.0), V(-0.07, 0.75, 0.06), 0.008, 0.008, OLD_BONE, 0.0)
    return ps


def brazier():
    ps = [P(Cone((0, 0.0, 0), (0, 0.5, 0), 0.05, 0.03), IRON, 0.01)]
    for s in range(3):
        a = s * 2.1
        limb(ps, V(0, 0.15, 0), V(np.cos(a) * 0.12, 0.0, np.sin(a) * 0.12), 0.012, 0.01, IRON, 0.01)
    ps.append(P(Cyl((0, 0.56, 0), 0.14, 0.06), IRON, 0.02))
    ps.append(P(Cyl((0, 0.62, 0), 0.12, 0.04), BLACK, 0.0, op='sub'))
    ps.append(P(Cone((0, 0.58, 0), (0.0, 0.85, 0.0), 0.12, 0.01), FIREBALL, 0.02, disp=(0.025, 12, 5)))
    return ps


def reeds():
    stalk = Mat((0.35, 0.4, 0.18), var=0.3, vfreq=30)
    cat = Mat((0.32, 0.2, 0.1), var=0.2, vfreq=40)
    ps = []
    rs = np.random.RandomState(12)
    for k in range(9):
        b = V(rs.uniform(-0.15, 0.15), 0, rs.uniform(-0.08, 0.08))
        t = b + V(rs.uniform(-0.08, 0.08), rs.uniform(0.35, 0.6), 0)
        limb(ps, b, t, 0.007, 0.003, stalk, 0.0)
        if k % 3 == 0:
            ps.append(P(Cone(t - V(0, 0.12, 0), t - V(0, 0.02, 0), 0.016, 0.016), cat, 0.004))
    return ps


def gargoyle():
    st = Mat(fn=lambda p, n: np.tile(np.array([0.45, 0.45, 0.48]), (len(p), 1)) * (0.55 + 0.55 * fbm(p, 14, 3, 281))[:, None])
    ps = [P(Box((0, 0.25, 0), (0.14, 0.25, 0.13), r=0.01), st, 0.01)]
    c = V(0, 0.65, 0.02)
    ps.append(P(Ellipsoid(c, (0.11, 0.13, 0.1)), st, 0.04))
    ps.append(P(Sphere(c + V(0, 0.15, 0.05), 0.07), st, 0.03))
    for s in (-1, 1):
        ps.append(P(TriPrism(c + V(s * 0.16, 0.05, -0.06), (-s * 0.06, -0.1), (s * 0.12, 0.16), (s * 0.06, -0.06), 0.012), st, 0.01))
        ps.append(P(Cone(c + V(s * 0.04, 0.2, 0.03), c + V(s * 0.08, 0.28, -0.01), 0.02, 0.003), st, 0.01))
        ps.append(P(Sphere(c + V(s * 0.025, 0.16, 0.11), 0.012), Mat((1.0, 0.25, 0.1), glow=1.0), 0.0))
        limb(ps, c + V(s * 0.08, -0.05, 0.05), V(s * 0.08, 0.5, 0.12), 0.03, 0.022, st, 0.02)
    ps.append(P(Ellipsoid(c + V(0, 0.11, 0.11), (0.035, 0.015, 0.02)), BLACK, 0.003, op='sub'))
    return ps


# ------------------------------------------------------------------ Butch Graves, full body (cutscenes)

DENIM = Mat(fn=lambda p, n: np.tile(np.array([0.2, 0.25, 0.38]), (len(p), 1)) * (0.7 + 0.4 * fbm(p, 25, 2, 291))[:, None], spec=0.15)
BOOT = Mat((0.12, 0.08, 0.06), var=0.2, vfreq=30, spec=0.5)
TANK = Mat((0.85, 0.83, 0.78), var=0.1, vfreq=20)
SHOVEL_M = Mat((0.5, 0.52, 0.55), var=0.25, vfreq=30, spec=0.8, shin=30)


def shovel_prims(ps, hand, d, up):
    d = norm(d); up = norm(up)
    side = norm(np.cross(d, up)); up2 = norm(np.cross(side, d))
    limb(ps, hand - d * 0.3, hand + d * 0.32, 0.014, 0.014, WOOD, 0.0)
    ps.append(P(Box(hand - d * 0.33, (0.045, 0.012, 0.012), R=np.stack([side, up2, d], 1)), WOOD, 0.004))
    blade = hand + d * 0.42
    ps.append(P(Box(blade, (0.075, 0.006, 0.1), R=np.stack([side, up2, d], 1), r=0.02), SHOVEL_M, 0.0))
    ps.append(P(Sphere(blade + d * 0.04 + up2 * 0.004, 0.02), Mat((0.3, 0.2, 0.12)), 0.01))   # dirt


def butch(pose='stand'):
    """Butch, full body, facing the camera. Poses: stand walk1 walk2 wind swing aim."""
    sw = {'walk1': -1, 'walk2': 1, 'cwalk1': -1, 'cwalk2': 1}.get(pose, 0)
    ps = []
    hip_y = 0.46
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.065, hip_y, 0)
        kn = hip + V(s * 0.012, -0.22, 0.05 * ls + 0.015)
        an = kn + V(0, -0.2, -0.03 * ls)
        if pose in ('wind', 'swing'):
            kn = hip + V(s * 0.04, -0.21, 0.04)
            an = kn + V(s * 0.03, -0.2, -0.02)
        if pose == 'kick':
            if s > 0:      # right leg swung up and out: a punt
                kn = hip + V(0.11, -0.07, 0.13)
                an = kn + V(0.15, 0.02, 0.12)
            else:
                kn = hip + V(-0.03, -0.21, -0.02)
                an = kn + V(-0.02, -0.2, -0.03)
        limb(ps, hip, kn, 0.058, 0.048, DENIM, 0.03)
        limb(ps, kn, an, 0.048, 0.042, DENIM, 0.02)
        ps.append(P(Ellipsoid(an + V(0, -0.025, 0.035), (0.045, 0.035, 0.075)), BOOT, 0.02))
    ps.append(P(Ellipsoid(V(0, hip_y + 0.03, 0), (0.12, 0.06, 0.08)), DENIM, 0.04))
    ps.append(P(Box(V(0, hip_y + 0.06, 0.06), (0.03, 0.02, 0.01), r=0.005), BRASS, 0.004))                 # belt buckle
    ps.append(P(Cyl(V(0, hip_y + 0.06, 0), 0.115, 0.018), Mat((0.15, 0.1, 0.06), spec=0.4), 0.01))
    twist = {'wind': -0.35, 'swing': 0.4}.get(pose, 0.0)
    ch = V(0, hip_y + 0.28, 0.0)
    R = rot(0, twist, 0)
    ps.append(P(Ellipsoid(V(0, hip_y + 0.15, 0.0), (0.12, 0.1, 0.075)), TANK, 0.05))
    ps.append(P(Box(ch, (0.16, 0.14, 0.09), R=R, r=0.07), JACKET, 0.07))
    ps.append(P(TriPrism(ch + V(0, 0.02, 0.08), (-0.05, 0.12), (0.05, 0.12), (0, -0.1), 0.02), TANK, 0.01))
    for s in (-1, 1):
        ps.append(P(Box(ch + V(s * 0.06, 0.05, 0.085), (0.025, 0.09, 0.012), R=rot(0, 0, s * 0.3), r=0.008), JACKET, 0.015))
    # head (reuse the HUD/title head model), slightly turned
    look = {'wind': -0.5, 'swing': 0.5, 'point': 0.35, 'shrug': -0.15, 'kick': 0.3}.get(pose, 0.0)
    head = HERO.head('grin' if pose in ('swing', 'aim', 'point', 'kick') else 'smirk', 0, look=look)
    HS = 0.8
    hpos = ch + V(0, 0.23, 0.01)
    for pr in head:
        pr_c = pr

        class Shift(Prim):
            def __init__(self, inner):
                self.inner = inner; self.op = inner.op; self.k = inner.k; self.mat = None; self.disp = None

            def d(self, p):
                return self.inner.dist((p - hpos) / HS) * HS
        w = Shift(pr_c)
        if pr_c.mat is not None:
            m = pr_c.mat

            class MS(Mat):
                def __init__(self, m):
                    self.m = m; self.spec = m.spec; self.shin = m.shin; self.unlit = m.unlit

                def albedo(self, p, n):
                    return self.m.albedo((p - hpos) / HS, n)

                def glowv(self, p, n):
                    return self.m.glowv((p - hpos) / HS, n)
            w.mat = MS(m)
        ps.append(w)
    # arms and props
    shl, shr = ch + R @ V(-0.17, 0.1, 0), ch + R @ V(0.17, 0.1, 0)
    if pose == 'wind':        # shovel cocked back over the right shoulder like a baseball bat
        hl, hr = ch + V(0.1, 0.12, 0.12), ch + V(0.16, 0.16, 0.08)
        shovel_prims(ps, (hl + hr) / 2, V(0.5, 0.6, -0.6), V(0, 0, 1))
    elif pose == 'swing':     # follow-through across the body
        hl, hr = ch + V(-0.16, 0.02, 0.18), ch + V(-0.1, 0.06, 0.22)
        shovel_prims(ps, (hl + hr) / 2, V(-1.0, 0.25, 0.2), V(0, 1, 0))
    elif pose == 'aim':       # boomstick fired into the air
        hl, hr = ch + V(-0.04, 0.3, 0.12), ch + V(0.06, 0.12, 0.14)
        a = hr + V(0, -0.03, 0)
        d = norm(V(-0.15, 1.0, 0.25))
        for s in (-1, 1):
            limb(ps, a + V(s * 0.012, 0, 0), a + d * 0.5 + V(s * 0.012, 0, 0), 0.012, 0.012, GUNMETAL, 0.004)
        limb(ps, a - d * 0.16, a + d * 0.05, 0.024, 0.02, WOOD, 0.01)
        tip = a + d * 0.52
        ps.append(P(Sphere(tip + d * 0.06, 0.06), FIREBALL, 0.0, disp=(0.02, 15, 3)))
    elif pose == 'kick':      # arms flung out for balance, shovel slung on the back
        hl, hr = shl + V(-0.22, 0.02, 0.06), shr + V(0.06, -0.24, -0.12)
        shovel_prims(ps, ch + V(0.02, 0.0, -0.13), V(-0.35, 1.0, -0.1), V(0, 0, 1))
    elif pose in ('carry', 'cwalk1', 'cwalk2'):      # both hands out front holding something; shovel slung on the back
        hl, hr = ch + V(-0.12, -0.04, 0.2), ch + V(0.12, -0.04, 0.2)
        shovel_prims(ps, ch + V(0.02, 0.0, -0.13), V(-0.35, 1.0, -0.1), V(0, 0, 1))
    elif pose == 'point':      # right arm pointing out to the side, shovel planted in the left hand
        hl, hr = shl + V(-0.06, -0.24, 0.1), shr + V(0.33, 0.07, 0.12)
        shovel_prims(ps, hl + V(0, 0.02, 0), V(-0.05, -1.0, 0.12), V(0, 0, 1))
        d = norm(hr - shr)
        limb(ps, hr, hr + d * 0.06, 0.012, 0.01, GLOVE, 0.004)
    elif pose == 'shrug':      # palms up, shovel leaning against the shoulder
        hl, hr = shl + V(-0.16, -0.12, 0.14), shr + V(0.16, -0.12, 0.14)
        shovel_prims(ps, ch + V(0.05, -0.05, -0.1), V(-0.35, 1.0, -0.15), V(0, 0, 1))
    else:
        a = 0.05 * sw
        hl, hr = shl + V(-0.04, -0.27, 0.06 + a), shr + V(0.05, -0.2, 0.12 - a)
        # shovel resting on the right shoulder
        shovel_prims(ps, hr + V(0, 0.02, 0), V(-0.2, 1.0, -0.45), V(0, 0, 1))
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.06, -0.06, -0.03)
        ps.append(P(Sphere(sh, 0.065), JACKET, 0.04))
        limb(ps, sh, el, 0.055, 0.048, JACKET, 0.03)
        limb(ps, el, hd, 0.048, 0.04, JACKET, 0.02)
        ps.append(P(Sphere(hd, 0.035), GLOVE, 0.01))
    return ps


# ------------------------------------------------------------------ cutscene props

def pk_head(talk=False):
    """The Pumpkin King's head, carved into a sulky porch jack-o-lantern."""
    pk = pumpkin_mat((0.85, 0.36, 0.05), seed=9)
    crown = Mat((0.85, 0.65, 0.2), var=0.2, vfreq=25, spec=0.9, shin=30)
    hc = V(0, 0.17, 0)
    r = 0.2
    ps = [P(Pumpkin(hc, r, squash=0.82, ribs=12, amp=0.09), pk, 0.0)]
    # grumpy half-closed eyes and a pouting (or yapping) mouth, all glowing
    for s in (-1, 1):
        ec = hc + V(s * 0.075, 0.035, r * 0.8)
        ps.append(P(TriPrism(ec, (-0.04, 0.0), (0.04, 0.0), (s * 0.03, 0.03 if s > 0 else 0.03), 0.06), FIRE, 0.004, op='sub'))
        ps.append(P(Box(hc + V(s * 0.075, 0.075, r * 0.85), (0.04, 0.008, 0.03), R=rot(0, 0, s * 0.35)), Mat((0.25, 0.1, 0.02)), 0.004))
    mo = 0.04 if talk else 0.015
    ps.append(P(Ellipsoid(hc + V(0, -0.07, r * 0.75), (0.07, mo, 0.06)), FIRE, 0.004, op='sub'))
    ps.append(P(Cone(hc + V(0, r * 0.7, 0), hc + V(0.02, r * 1.05, -0.01), 0.025, 0.018), STEM, 0.01))
    # crooked little crown
    cr = hc + V(0.02, r * 0.75, 0)
    ps.append(P(Torus(cr, r * 0.4, 0.014, R=rot(0, 0, 0.25)), crown, 0.0))
    for k in range(5):
        a = k * 2 * np.pi / 5 + 0.3
        b = cr + rot(0, 0, 0.25) @ V(np.cos(a) * r * 0.4, 0, np.sin(a) * r * 0.4)
        limb(ps, b, b + V(0.015, 0.06, 0), 0.014, 0.002, crown, 0.004)
    return ps


def kid(scared=False):
    """Trick-or-treater in a bedsheet ghost costume, holding a pumpkin pail."""
    sheet = Mat((0.95, 0.94, 0.92), var=0.08, vfreq=8, spec=0.1)
    ps = []
    def sheet_d(p):
        y = p[:, 1]
        t = np.clip(y / 0.4, 0, 1)
        rad = 0.11 - 0.03 * t
        ang = np.arctan2(p[:, 2], p[:, 0])
        d = np.sqrt(p[:, 0] ** 2 + (p[:, 2] / 0.8) ** 2) - (rad + 0.01 * np.sin(ang * 6 + y * 8))
        d = np.maximum(d, 0.02 - y + 0.015 * np.abs(np.sin(ang * 4)))
        d = np.maximum(d, y - 0.4)
        return d * 0.75
    ps.append(P(Func(sheet_d), sheet, 0.0))
    hc = V(0, 0.44, 0.0)
    ps.append(P(Sphere(hc, 0.085), sheet, 0.04))
    for s in (-1, 1):
        ps.append(P(Ellipsoid(hc + V(s * 0.03, 0.01 if not scared else 0.02, 0.075), (0.015, 0.02 if not scared else 0.026, 0.02)), BLACK, 0.003, op='sub'))
    ps.append(P(Ellipsoid(hc + V(0, -0.035, 0.08), (0.016, 0.008 if not scared else 0.02, 0.02)), BLACK, 0.003, op='sub'))
    for k in range(2):
        ps.append(P(Ellipsoid(V(-0.035 + k * 0.07, 0.015, 0.07), (0.022, 0.012, 0.035)), Mat((0.1, 0.1, 0.12), spec=0.4), 0.01))
    if scared:
        for s in (-1, 1):
            limb(ps, V(s * 0.08, 0.3, 0.02), V(s * 0.16, 0.48, 0.04), 0.03, 0.025, sheet, 0.02)
    else:
        limb(ps, V(0.08, 0.3, 0.02), V(0.12, 0.2, 0.08), 0.03, 0.025, sheet, 0.02)
        pc = V(0.13, 0.12, 0.1)
        ps.append(P(Pumpkin(pc, 0.06, squash=0.85, ribs=8, amp=0.06), pumpkin_mat(), 0.0))
        ps.append(P(Cyl(pc + V(0, 0.04, 0), 0.04, 0.02), BLACK, 0.0, op='sub'))
        ps.append(P(Torus(pc + V(0, 0.07, 0), 0.04, 0.004, R=rot(np.pi / 2, 0, 0)), BLACK, 0.0))
    return ps


def clown_car():
    body = Mat(fn=lambda p, n: np.where(((np.floor(p[:, 0] / 0.06) + np.floor(p[:, 1] / 0.06)) % 2 == 0)[:, None],
                                        np.array([[0.95, 0.85, 0.1]]), np.array([[0.2, 0.55, 0.95]])), spec=0.7, shin=40)
    tire = Mat((0.06, 0.06, 0.06), var=0.2, vfreq=40)
    ps = [P(Ellipsoid((0, 0.2, 0), (0.24, 0.13, 0.28)), body, 0.0)]
    ps.append(P(Ellipsoid((0, 0.31, -0.04), (0.17, 0.11, 0.16)), body, 0.04))
    ps.append(P(Box((0, 0.33, 0.1), (0.14, 0.06, 0.02), R=rot(0.5, 0, 0)), Mat((0.15, 0.2, 0.25), spec=1.0), 0.0))
    for s in (-1, 1):
        ps.append(P(Cyl((s * 0.21, 0.09, 0.16), 0.09, 0.04, R=rot(0, 0, np.pi / 2)), tire, 0.01))
        ps.append(P(Cyl((s * 0.21, 0.09, -0.16), 0.09, 0.04, R=rot(0, 0, np.pi / 2)), tire, 0.01))
        ps.append(P(Sphere((s * 0.13, 0.22, 0.27), 0.04), Mat((1.0, 0.95, 0.7), glow=1.0), 0.0))
    ps.append(P(Cone((0.18, 0.36, 0.08), (0.28, 0.42, 0.14), 0.012, 0.035), BRASS, 0.004))
    ps.append(P(Sphere((0.15, 0.36, 0.05), 0.03), GLOSS_RED, 0.0))
    ps.append(P(Sphere((0, 0.16, 0.3), 0.035), GLOSS_RED, 0.0))
    return ps


def balloon():
    ps = [P(Ellipsoid((0, 0.32, 0), (0.07, 0.085, 0.07)), GLOSS_RED, 0.0), P(Cone((0, 0.235, 0), (0, 0.22, 0), 0.006, 0.012), GLOSS_RED, 0.003)]
    for k in range(4):
        limb(ps, V(0.01 * np.sin(k * 1.4), 0.22 - k * 0.055, 0), V(0.01 * np.sin(k * 1.4 + 1.4), 0.165 - k * 0.055, 0), 0.0025, 0.0025, WHITE, 0.0)
    return ps


def count_bat(up=True):
    """The Count, shrunk into a tiny bat that still has his slicked hair and medallion."""
    ps = M2.bat('walk1' if up else 'walk2')
    hc = V(0, 0.22, 0.01)
    hair = Mat((0.04, 0.035, 0.04), spec=0.9, shin=40)
    ps.append(P(Ellipsoid(hc + V(0, 0.018, -0.005), (0.035, 0.022, 0.034)), hair, 0.004))
    ps.append(P(TriPrism(hc + V(0, 0.012, 0.03), (-0.01, 0.01), (0.01, 0.01), (0, -0.012), 0.005), hair, 0.002))
    ps.append(P(Cyl(V(0, 0.13, 0.04), 0.012, 0.003, R=rot(np.pi / 2, 0, 0)), GOLD, 0.0))
    ps.append(P(Sphere(V(0, 0.13, 0.045), 0.006), Mat((1.0, 0.1, 0.1), glow=1.0), 0.0))
    for s in (-1, 1):
        ps.append(P(TriPrism(hc + V(s * 0.04, -0.02, -0.02), (-s * 0.015, -0.02), (s * 0.02, -0.025), (s * 0.015, 0.03), 0.004),
                    Mat((0.55, 0.03, 0.06)), 0.004))
    return ps


def star():
    glow = Mat((1.0, 1.0, 0.85), glow=1.0)
    ps = [P(Sphere((0, 0.1, 0), 0.02), glow, 0.0)]
    for k in range(4):
        a = k * np.pi / 2
        limb(ps, V(0, 0.1, 0), V(np.cos(a) * 0.08, 0.1 + np.sin(a) * 0.08, 0), 0.012, 0.001, glow, 0.0)
    return ps
