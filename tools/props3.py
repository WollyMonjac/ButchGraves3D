"""Episode 4 (Halloween 2099) props and cutscene actors. Feet at y=0, facing +z."""
import numpy as np
from sdf import *
from monsters import limb, cloth, tilt_scene, TriPrism, Pumpkin, pumpkin_mat, jack_face, BONE, BLACK, MOUTH
from monsters2 import V, STEEL, GLOSS_RED
from monsters3 import GUNMETAL, GREENMETAL, CHROME, COPPER, HAZARD, ZAPGLOW, ZAPCORE, NEON_GRN, RUBBER, EYE_CYAN, doctor_head, metal
from props import tombstone, STONE

HOLO = Mat((0.35, 0.95, 1.0), glow=1.0)
NEON_OR = Mat((1.0, 0.55, 0.12), glow=1.0)
NEON_PK = Mat((1.0, 0.3, 0.75), glow=1.0)
TOXGLOW = Mat((0.55, 1.0, 0.2), glow=1.0)
SCREEN = Mat((0.3, 1.0, 0.5), glow=1.0)
GLASSC = Mat((0.55, 0.75, 0.8), spec=1.4, shin=70)
COAT = Mat((0.93, 0.93, 0.9), var=0.08, vfreq=20, spec=0.2)
PANTS = Mat((0.18, 0.16, 0.2), var=0.15, vfreq=25)
SKIN = Mat((0.85, 0.7, 0.6), var=0.1, vfreq=30, spec=0.3)


def holotomb():
    """Holographic gravestone floating over a metal emitter base."""
    ps = [P(Cyl((0, 0.03, 0), 0.12, 0.03), GUNMETAL, 0.01), P(Cyl((0, 0.065, 0), 0.08, 0.008), HOLO, 0.0)]
    out = []
    for pr in tombstone(0, 3)[:-1]:            # drop the dirt mound
        if pr.mat is STONE:
            pr.mat = HOLO
        out.append(pr)
    return ps + [_lift(pr, 0.09) for pr in out]


def _lift(pr, dy):
    class L(Prim):
        def __init__(s, inner):
            s.inner = inner; s.op = inner.op; s.k = inner.k; s.mat = inner.mat; s.disp = None

        def d(s, p):
            return s.inner.dist(p - V(0, dy, 0))
    w = L(pr)
    if pr.mat is not None:
        m = pr.mat

        class MS(Mat):
            def __init__(s, m):
                s.m = m; s.spec = m.spec; s.shin = m.shin; s.unlit = m.unlit

            def albedo(s, p, n):
                return s.m.albedo(p - V(0, dy, 0), n)

            def glowv(s, p, n):
                return s.m.glowv(p - V(0, dy, 0), n)
        w.mat = MS(m)
    return w


def neonjack():
    """Neon jack-o-lantern sign on a pole."""
    ps = [P(Cyl((0, 0.02, 0), 0.07, 0.02), GUNMETAL, 0.01)]
    limb(ps, V(0, 0.02, 0), V(0, 0.55, 0), 0.018, 0.015, GUNMETAL, 0.0)
    c = V(0, 0.72, 0.02)
    # outline tube of the pumpkin (ellipse in the xy plane) + stem + face, all neon
    n = 28
    for k in range(n):
        a0, a1 = k * 2 * np.pi / n, (k + 1) * 2 * np.pi / n
        r0 = 0.16 * (1 + 0.06 * np.cos(a0 * 5)); r1 = 0.16 * (1 + 0.06 * np.cos(a1 * 5))
        p0 = c + V(np.cos(a0) * r0 * 1.2, np.sin(a0) * r0, 0); p1 = c + V(np.cos(a1) * r1 * 1.2, np.sin(a1) * r1, 0)
        ps.append(P(Cone(p0, p1, 0.011, 0.011), NEON_OR, 0.0))
    limb(ps, c + V(0, 0.15, 0), c + V(0.03, 0.22, 0), 0.01, 0.01, NEON_GRN, 0.0)
    for s in (-1, 1):
        e = c + V(s * 0.07, 0.04, 0)
        for (a, b) in (((-0.035, -0.02), (0.035, -0.02)), ((0.035, -0.02), (0, 0.035)), ((0, 0.035), (-0.035, -0.02))):
            ps.append(P(Cone(e + V(a[0], a[1], 0), e + V(b[0], b[1], 0), 0.008, 0.008), NEON_OR, 0.0))
    for k in range(6):
        x0 = -0.1 + k * 0.04
        ps.append(P(Cone(c + V(x0, -0.05 - 0.02 * (k % 2), 0), c + V(x0 + 0.04, -0.05 - 0.02 * ((k + 1) % 2), 0), 0.008, 0.008), NEON_OR, 0.0))
    ps.append(P(Box(c + V(0, 0, -0.02), (0.2, 0.17, 0.008)), Mat((0.06, 0.06, 0.08)), 0.0))
    return ps


def crate():
    ps = [P(Box((0, 0.17, 0), (0.17, 0.17, 0.17), r=0.012), GUNMETAL, 0.0)]
    for s in (-1, 1):
        ps.append(P(Box((s * 0.155, 0.17, 0.17), (0.018, 0.17, 0.006)), HAZARD, 0.0))
        ps.append(P(Box((0, 0.17 + s * 0.155, 0.17), (0.17, 0.018, 0.006)), HAZARD, 0.0))
    ps.append(P(Box((0, 0.17, 0.172), (0.06, 0.03, 0.004)), Mat((0.9, 0.9, 0.85)), 0.0))
    ps.append(P(Box((0, 0.17, 0.174), (0.045, 0.012, 0.004)), Mat((0.1, 0.1, 0.1)), 0.0))
    return ps


def toxic():
    """Leaking barrel of glowing toxic waste. Explodes when shot."""
    def fn(p, n):
        c = np.tile(np.array([0.85, 0.7, 0.1]), (len(p), 1)) * (0.7 + 0.4 * fbm(p, 20, 2, 41))[:, None]
        y = p[:, 1]
        band = (np.abs(y - 0.08) < 0.012) | (np.abs(y - 0.28) < 0.012)
        c[band] = np.array([0.25, 0.25, 0.25])
        # trefoil on the front
        x = p[:, 0]; yy = y - 0.18
        r = np.sqrt(x * x + yy * yy); a = np.arctan2(yy, x)
        tre = (r < 0.055) & (r > 0.015) & (np.cos(3 * (a - np.pi / 2)) > 0.3) | (r < 0.01)
        c[(p[:, 2] > 0.05) & tre] = np.array([0.08, 0.08, 0.08])
        return c
    ps = [P(Cyl((0, 0.18, 0), 0.11, 0.18), Mat(fn=fn, spec=0.6, shin=25), 0.0)]
    ps.append(P(Cyl((0, 0.36, 0), 0.085, 0.006), TOXGLOW, 0.0))
    ps.append(P(Ellipsoid((0.05, 0.37, 0.02), (0.03, 0.02, 0.03)), TOXGLOW, 0.01))
    ps.append(P(Cone((0.09, 0.3, 0.06), (0.11, 0.02, 0.09), 0.012, 0.02), TOXGLOW, 0.01))
    ps.append(P(Ellipsoid((0.12, 0.0, 0.12), (0.09, 0.008, 0.07)), TOXGLOW, 0.0))
    return ps


def robotarm():
    """Industrial robot arm frozen mid-weld."""
    ps = [P(Cyl((0, 0.05, 0), 0.16, 0.05), HAZARD, 0.01), P(Cyl((0, 0.13, 0), 0.1, 0.04), GUNMETAL, 0.01)]
    j1 = V(0, 0.2, 0); j2 = V(0.12, 0.62, 0.06); j3 = V(-0.05, 0.86, 0.18)
    ps.append(P(Sphere(j1, 0.08), CHROME, 0.02))
    limb(ps, j1, j2, 0.06, 0.05, Mat((0.95, 0.6, 0.1), spec=0.7, shin=30), 0.02)
    ps.append(P(Sphere(j2, 0.06), CHROME, 0.02))
    limb(ps, j2, j3, 0.045, 0.035, Mat((0.95, 0.6, 0.1), spec=0.7, shin=30), 0.02)
    ps.append(P(Sphere(j3, 0.04), CHROME, 0.01))
    tip = j3 + V(-0.02, -0.1, 0.06)
    limb(ps, j3, tip, 0.02, 0.012, GUNMETAL, 0.006)
    ps.append(P(Sphere(tip + V(0, -0.02, 0.01), 0.022), ZAPCORE, 0.0, disp=(0.008, 30, 2)))
    limb(ps, j1 + V(0.05, 0.02, -0.04), j2 + V(0.02, -0.08, -0.04), 0.01, 0.01, RUBBER, 0.0)
    return ps


def capsule():
    """Glass stasis tube with glowing green fluid and a floating specimen silhouette."""
    ps = [P(Cyl((0, 0.06, 0), 0.17, 0.06), GUNMETAL, 0.01), P(Cyl((0, 0.94, 0), 0.17, 0.06), GUNMETAL, 0.01)]
    for k in range(4):
        a = k * np.pi / 2 + np.pi / 4
        limb(ps, V(np.cos(a) * 0.15, 0.1, np.sin(a) * 0.15), V(np.cos(a) * 0.15, 0.9, np.sin(a) * 0.15), 0.012, 0.012, CHROME, 0.0)

    def fn(p, n):
        x, y = p[:, 0], p[:, 1]
        c = np.tile(np.array([0.3, 0.85, 0.45]), (len(p), 1)) * (0.65 + 0.45 * fbm(p, 9, 2, 61))[:, None]
        body = ((x / 0.045) ** 2 + ((y - 0.74) / 0.05) ** 2 < 1)              # head
        body |= ((x / 0.07) ** 2 + ((y - 0.56) / 0.13) ** 2 < 1)              # torso
        body |= (np.abs(np.abs(x) - 0.03) < 0.022) & (y > 0.2) & (y < 0.48)      # legs
        body |= (np.abs(np.abs(x) - 0.085 - (0.66 - y) * 0.15) < 0.016) & (y > 0.42) & (y < 0.66)   # arms
        c[body & (p[:, 2] > 0)] = np.array([0.04, 0.16, 0.08])
        eyes = (((np.abs(x) - 0.017) / 0.009) ** 2 + ((y - 0.75) / 0.006) ** 2 < 1)
        c[eyes & (p[:, 2] > 0)] = np.array([1.0, 0.3, 0.2])
        return c
    ps.append(P(Cyl((0, 0.5, 0), 0.14, 0.38), Mat(fn=fn, glow=1.0), 0.0))
    ps.append(P(Box((0.08, 0.6, 0.14), (0.012, 0.25, 0.004)), Mat((0.9, 1.0, 1.0), glow=1.0), 0.0))   # glass glint
    for k in range(5):
        ps.append(P(Sphere((0.06 * np.sin(k * 2.1) + 0.04, 0.3 + k * 0.12, 0.13), 0.012), Mat((0.75, 1.0, 0.8), glow=1.0), 0.0))
    return ps


def _scaled(pr, s, off):
    class L(Prim):
        def __init__(q, inner):
            q.inner = inner; q.op = inner.op; q.k = inner.k * s; q.mat = inner.mat; q.disp = None

        def d(q, p):
            return q.inner.dist((p - off) / s) * s
    w = L(pr)
    return w


def terminal():
    ps = [P(Box((0, 0.28, 0), (0.15, 0.28, 0.1), r=0.015), GUNMETAL, 0.0)]
    ps.append(P(Box((0, 0.6, -0.02), (0.15, 0.1, 0.08), R=rot(-0.25, 0, 0), r=0.015), GREENMETAL, 0.01))
    ps.append(P(Box((0, 0.61, 0.06), (0.12, 0.075, 0.004), R=rot(-0.25, 0, 0)), Mat(fn=lambda p, n: np.where(
        ((np.floor(p[:, 1] * 120) % 3) == 0)[:, None], np.array([[0.05, 0.25, 0.1]]), np.array([[0.3, 1.0, 0.5]])), glow=1.0), 0.0))
    ps.append(P(Box((0, 0.48, 0.1), (0.13, 0.015, 0.04), R=rot(0.2, 0, 0), r=0.004), Mat((0.15, 0.15, 0.17)), 0.0))
    for k in range(4):
        ps.append(P(Sphere((-0.1 + k * 0.065, 0.36, 0.1), 0.012), [Mat((1, 0.2, 0.2), glow=1.0), Mat((1, 0.85, 0.2), glow=1.0),
                                                                   Mat((0.3, 1, 0.4), glow=1.0), Mat((0.3, 0.6, 1), glow=1.0)][k], 0.0))
    for k in range(3):
        ps.append(P(Box((0, 0.12 + k * 0.06, 0.1), (0.12, 0.004, 0.003)), BLACK, 0.0))
    return ps


def cables():
    """Bundle of cables hanging from the ceiling, one sparking."""
    ps = []
    rs = np.random.RandomState(7)
    for k in range(6):
        x = rs.uniform(-0.12, 0.12); z = rs.uniform(-0.04, 0.04)
        ln = rs.uniform(0.3, 0.6)
        pts = [V(x, 1.0, z)]
        for j in range(5):
            t = (j + 1) / 5
            pts.append(V(x + np.sin(t * 2 + k) * 0.03, 1.0 - ln * t, z + 0.01 * j))
        m = [RUBBER, Mat((0.7, 0.1, 0.1), spec=0.4), Mat((0.15, 0.25, 0.6), spec=0.4), Mat((0.85, 0.75, 0.1), spec=0.4)][k % 4]
        for a, b in zip(pts, pts[1:]):
            ps.append(P(Cone(a, b, 0.012, 0.012), m, 0.006))
        if k == 2:
            ps.append(P(Sphere(pts[-1] + V(0, -0.02, 0), 0.03), ZAPCORE, 0.0, disp=(0.012, 30, 5)))
    return ps


def telepad():
    """Teleporter pad (tilted toward the viewer) with rising rings of light."""
    ps = [P(Cyl((0, 0.02, 0), 0.32, 0.02), GUNMETAL, 0.006), P(Torus((0, 0.042, 0), 0.25, 0.018), Mat((0.75, 0.35, 1.0), glow=1.0), 0.0)]
    ps.append(P(Torus((0, 0.042, 0), 0.14, 0.012), Mat((0.4, 0.9, 1.0), glow=1.0), 0.0))
    for k in range(8):
        a = k * np.pi / 4
        ps.append(P(Box((np.cos(a) * 0.29, 0.04, np.sin(a) * 0.29), (0.02, 0.01, 0.02), R=rot(0, -a, 0)), HAZARD, 0.0))
    from weapons import transform
    ps = transform(ps, rot(0.55, 0, 0), V(0, 0.0, 0))
    for k, (y, r) in enumerate(((0.16, 0.2), (0.3, 0.16), (0.42, 0.11))):
        ps.append(P(Torus((0, y, 0), r, 0.008, R=rot(0.55, 0, 0)), Mat((0.55, 0.85, 1.0), glow=1.0), 0.0))
    return ps


# ------------------------------------------------------------------ cutscene actors

def doc(pose='stand'):
    """Dr. Viktor Franken: small, lab coat, goggles, Einstein hair. Poses: stand, rant, run1, run2."""
    ps = []
    sw = {'run1': -1, 'run2': 1}.get(pose, 0)
    lean = 0.12 if pose.startswith('run') else 0.0
    hip_y = 0.36
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.05, hip_y, 0)
        kn = hip + V(0, -0.17, 0.09 * ls + 0.02)
        an = kn + V(0, -0.16, -0.06 * ls)
        limb(ps, hip, kn, 0.036, 0.03, PANTS, 0.02)
        limb(ps, kn, an, 0.03, 0.026, PANTS, 0.02)
        ps.append(P(Ellipsoid(an + V(0, -0.015, 0.03), (0.03, 0.022, 0.055)), Mat((0.1, 0.07, 0.05), spec=0.6), 0.01))
    ch = V(0, hip_y + 0.17, lean * 0.4)
    # lab coat: long flared cone from the shoulders to the knees
    ps.append(P(Cone(ch + V(0, 0.08, 0), V(0, hip_y - 0.18, lean * 0.1 - 0.02), 0.075, 0.12), COAT, 0.03))
    ps.append(P(Box(ch + V(0, 0.0, 0.06), (0.006, 0.12, 0.01)), Mat((0.6, 0.6, 0.6)), 0.0))
    ps.append(P(TriPrism(ch + V(0, 0.07, 0.065), (-0.03, 0.04), (0.03, 0.04), (0, -0.04), 0.01), Mat((0.75, 0.1, 0.1)), 0.004))   # red tie
    hc = ch + V(0, 0.2, 0.02 + lean * 0.3)
    doctor_head(ps, hc, 1.6, 'mad' if pose in ('rant', 'run1', 'run2') else 'calm')
    shl, shr = ch + V(-0.09, 0.07, 0), ch + V(0.09, 0.07, 0)
    if pose == 'rant':
        hl, hr = shl + V(-0.1, 0.18, 0.04), shr + V(0.1, 0.18, 0.04)
    elif pose.startswith('run'):
        hl, hr = shl + V(-0.04, -0.06, 0.12 * sw + 0.04), shr + V(0.04, -0.06, -0.12 * sw + 0.04)
    else:
        hl, hr = shl + V(-0.03, -0.17, 0.04), shr + V(0.05, -0.1, 0.1)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.03, -0.03, -0.02)
        limb(ps, sh, el, 0.03, 0.027, COAT, 0.02)
        limb(ps, el, hd, 0.027, 0.024, COAT, 0.02)
        ps.append(P(Sphere(hd, 0.022), Mat((0.85, 0.85, 0.3), spec=0.5), 0.01))     # rubber gloves
    if pose == 'stand':      # remote control with a big red button
        ps.append(P(Box(shr + V(0.05, -0.08, 0.13), (0.02, 0.035, 0.012), r=0.004), GUNMETAL, 0.004))
        ps.append(P(Sphere(shr + V(0.05, -0.06, 0.145), 0.012), Mat((1, 0.15, 0.1), glow=1.0), 0.0))
    from weapons import transform
    return ps if lean == 0 else transform(ps, rot(lean, 0, 0), V(0, 0, 0))


def minibot(pose=0):
    """Tiny robot with one big eye on a wheel: the doctor's 'ultimate creation'."""
    ps = [P(Cyl((0, 0.04, 0), 0.04, 0.018, R=rot(0, 0, np.pi / 2)), RUBBER, 0.004)]
    ps.append(P(Box((0, 0.11, 0), (0.05, 0.05, 0.045), r=0.015), GREENMETAL, 0.01))
    ps.append(P(Cyl((0, 0.115, 0.045), 0.03, 0.006, R=rot(np.pi / 2, 0, 0)), CHROME, 0.0))
    ps.append(P(Sphere((0, 0.115, 0.05), 0.02), Mat((0.4, 1, 1), glow=1.0), 0.0))
    ps.append(P(Sphere((0.006, 0.12, 0.066), 0.006), BLACK, 0.0))
    limb(ps, V(0, 0.16, 0), V(0.01 * pose, 0.21, 0), 0.004, 0.003, CHROME, 0.0)
    ps.append(P(Sphere((0.01 * pose, 0.215, 0), 0.01), Mat((1, 0.2, 0.2), glow=1.0), 0.0))
    for s in (-1, 1):
        limb(ps, V(s * 0.05, 0.12, 0), V(s * 0.08, 0.1 + 0.04 * pose * s, 0.03), 0.008, 0.006, CHROME, 0.0)
        ps.append(P(Sphere(V(s * 0.08, 0.1 + 0.04 * pose * s, 0.03), 0.012), GUNMETAL, 0.0))
    return ps


def portal(ph=0):
    """Swirling time portal (fullbright)."""
    def fn(p, n):
        x, y = p[:, 0], p[:, 1] - 0.5
        r = np.sqrt(x * x + y * y) + 1e-6
        a = np.arctan2(y, x)
        sw = np.sin(a * 3 + r * 40 + ph * 1.3)
        c1 = np.array([0.55, 0.2, 1.0]); c2 = np.array([0.3, 1.0, 0.6]); c3 = np.array([1.0, 1.0, 1.0])
        t = (sw * 0.5 + 0.5)[:, None]
        c = c1[None] * (1 - t) + c2[None] * t
        core = np.clip(1 - r / 0.12, 0, 1)[:, None]
        return c * (1 - core) + c3[None] * core
    ps = [P(Ellipsoid((0, 0.5, 0), (0.3, 0.42, 0.03)), Mat(fn=fn, glow=1.0), 0.0)]
    ps.append(P(Torus((0, 0.5, 0), 0.32, 0.02, R=rot(np.pi / 2, 0, 0) @ np.diag([1, 1, 1])), Mat((0.85, 0.6, 1.0), glow=1.0), 0.0)) if False else None
    for k in range(10):
        a = k * 2 * np.pi / 10 + ph * 0.3
        ps.append(P(Sphere((np.cos(a) * 0.31, 0.5 + np.sin(a) * 0.43, 0.0), 0.02), Mat((0.85, 0.7, 1.0), glow=1.0), 0.0))
    return ps


# ------------------------------------------------------------------ gory cutscene props

def pk_smash():
    """The Pumpkin King's head after a field goal into a tombstone: shell shards, seeds, pulp and blood."""
    rs = np.random.RandomState(13)
    pk = pumpkin_mat((0.85, 0.36, 0.05), seed=9)
    pulp = Mat((0.95, 0.55, 0.1), var=0.3, vfreq=30, spec=0.5)
    gore = Mat((0.55, 0.02, 0.02), spec=0.9, shin=40)
    ps = [P(Ellipsoid((0, 0.0, 0.02), (0.34, 0.012, 0.18)), gore, 0.0), P(Ellipsoid((0.05, 0.004, 0.0), (0.22, 0.018, 0.12)), pulp, 0.02)]
    # the back half of the head, cracked open like an egg, plus big shell shards standing in the mess
    hc = V(-0.03, 0.09, -0.04)
    ps.append(P(Pumpkin(hc, 0.15, squash=0.82, ribs=12, amp=0.09), pk, 0.0))
    ps.append(P(Box(hc + V(0.05, 0.1, 0.12), (0.16, 0.12, 0.12), R=rot(0.5, 0.3, 0.4)), pk, 0.0, op='sub'))
    ps.append(P(Ellipsoid(hc + V(0.02, 0.0, 0.05), (0.11, 0.09, 0.08)), pulp, 0.02))
    for k in range(9):
        a = rs.uniform(0, 2 * np.pi); d = rs.uniform(0.1, 0.3)
        c = V(np.cos(a) * d, 0.03, np.sin(a) * d * 0.5 + 0.04)
        ps.append(P(Ellipsoid(c, (rs.uniform(0.03, 0.06), rs.uniform(0.025, 0.05), rs.uniform(0.01, 0.02)), R=rot(rs.uniform(-0.6, 0.6), a, rs.uniform(-0.5, 0.5))), pk, 0.01))
    for k in range(14):
        c = V(rs.uniform(-0.25, 0.25), 0.012, rs.uniform(-0.1, 0.14))
        ps.append(P(Ellipsoid(c, (0.01, 0.004, 0.006), R=rot(0, rs.uniform(0, 3), 0)), Mat((0.95, 0.9, 0.7)), 0.0))
    # what is left of the crown
    ps.append(P(Torus((-0.12, 0.02, 0.05), 0.06, 0.012, R=rot(0.5, 0, 0.3)), Mat((0.85, 0.65, 0.2), spec=0.9, shin=30), 0.0))
    return ps


def nose():
    return [P(Sphere((0, 0.04, 0), 0.04), GLOSS_RED, 0.0)]


def goggles():
    brass = Mat((0.3, 0.25, 0.15), spec=0.7)
    ps = []
    for s in (-1, 1):
        ps.append(P(Torus((s * 0.03, 0.02, 0), 0.022, 0.006, R=rot(np.pi / 2, 0, 0)), brass, 0.0))
        ps.append(P(Cyl((s * 0.03, 0.02, 0), 0.02, 0.003, R=rot(np.pi / 2, 0, 0)), Mat((0.6, 0.9, 1.0), glow=1.0), 0.0))
    limb(ps, V(-0.01, 0.02, 0), V(0.01, 0.02, 0), 0.004, 0.004, brass, 0.0)
    limb(ps, V(-0.052, 0.02, 0), V(-0.08, 0.01, -0.03), 0.004, 0.004, RUBBER, 0.0)
    limb(ps, V(0.052, 0.02, 0), V(0.08, 0.01, -0.03), 0.004, 0.004, RUBBER, 0.0)
    return ps
