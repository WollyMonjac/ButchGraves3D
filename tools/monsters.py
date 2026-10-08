"""SDF models for monsters. Feet at y=0, facing +z (toward camera). 1 unit = wall height."""
import numpy as np
from sdf import *

# ------------------------------------------------------------------ shared materials

def rot_skin(base=(0.50, 0.56, 0.40), seed=1):
    base = np.asarray(base)
    bruise = np.array([0.38, 0.28, 0.32])
    dark = np.array([0.22, 0.24, 0.16])

    def fn(p, n):
        v = fbm(p, 9.0, 3, seed)
        v2 = fbm(p, 26.0, 2, seed + 5)
        c = base[None, :] * (0.78 + 0.44 * v2)[:, None]
        m = np.clip((v - 0.55) * 6, 0, 1)[:, None]
        c = c * (1 - m) + bruise[None, :] * m
        m2 = np.clip((0.33 - v) * 8, 0, 1)[:, None]
        c = c * (1 - m2) + dark[None, :] * m2
        # veins
        vein = np.abs(fbm(p * np.array([1, 2.5, 1]), 14.0, 2, seed + 9) - 0.5) < 0.018
        c[vein] = c[vein] * 0.55 + np.array([0.15, 0.05, 0.12]) * 0.45
        return c
    return Mat(fn=fn, spec=0.18, shin=18)


def cloth(base, seed=3, torn=None, under=None, blood=0.0):
    base = np.asarray(base)

    def fn(p, n):
        v = fbm(p, 14.0, 3, seed)
        c = base[None, :] * (0.7 + 0.6 * v)[:, None]
        # weave
        w = (np.sin(p[:, 0] * 260) * np.sin(p[:, 1] * 260)) * 0.05
        c = c * (1 + w)[:, None]
        if blood > 0:
            b = fbm(p, 6.0, 3, seed + 40)
            bm = np.clip((b - (0.62 - blood)) * 10, 0, 1)[:, None]
            c = c * (1 - bm) + np.array([0.32, 0.03, 0.02])[None, :] * bm
        if torn is not None:
            t = fbm(p, 7.0, 3, seed + 20)
            hole = t > torn
            if under is not None and hole.any():
                c[hole] = under.albedo(p[hole], n[hole])
            edge = (t > torn - 0.03) & ~hole
            c[edge] *= 0.55
        return c
    return Mat(fn=fn)


BONE = Mat((0.86, 0.82, 0.68), var=0.12, vfreq=20, spec=0.25)
TEETH = Mat((0.88, 0.84, 0.62), var=0.15, vfreq=40, spec=0.4)
MOUTH = Mat((0.22, 0.02, 0.02), spec=0.5, shin=40)
BLOOD = Mat((0.42, 0.02, 0.02), var=0.2, vfreq=20, spec=0.6, shin=40)
EYE_RED = Mat((1.0, 0.22, 0.06), glow=1.0)
EYE_GRN = Mat((0.55, 1.0, 0.25), glow=1.0)
EYE_YEL = Mat((1.0, 0.85, 0.2), glow=1.0)
BLACK = Mat((0.03, 0.02, 0.02))
HAIR = Mat((0.12, 0.11, 0.09), var=0.3, vfreq=60)


def limb(prims, a, b, ra, rb, mat, k=0.04, disp=None):
    prims.append(P(Cone(a, b, ra, rb), mat, k, disp=disp))


def ribs(prims, c, w, mat, n=4, k=0.01):
    """Exposed ribs: thin curved capsules across the chest front."""
    c = np.asarray(c, float)
    for i in range(n):
        y = c[1] - i * 0.032
        ww = w * (1 - i * 0.08)
        for s in (-1, 1):
            a = c + np.array([s * 0.012, y - c[1], 0.02])
            m = c + np.array([s * ww * 0.6, y - c[1] - 0.008, 0.0])
            e = c + np.array([s * ww, y - c[1] - 0.02, -0.05])
            prims.append(P(Cone(a, m, 0.009, 0.008), mat, k))
            prims.append(P(Cone(m, e, 0.008, 0.007), mat, k))


# ------------------------------------------------------------------ ZOMBIE (Ghoul)

def zombie(pose='walk1'):
    """Rotting ghoul in torn clothes reaching for you."""
    skin = rot_skin()
    shirt = cloth((0.24, 0.25, 0.30), seed=4, torn=0.67, under=skin, blood=0.04)
    pants = cloth((0.26, 0.2, 0.14), seed=7, torn=0.7, under=skin, blood=0.05)
    ps = []
    ph = {'walk1': 0.0, 'walk2': 1.0, 'attack': 0.5, 'pain': 0.5, 'idle': 0.5}.get(pose, 0.5)
    sw = (ph - 0.5) * 2  # -1..1 leg swing
    hip_y = 0.40
    lean = 0.06 if pose != 'pain' else -0.05
    tilt = 0.0
    # legs
    for s, ls in ((-1, sw), (1, -sw)):
        hip = np.array([s * 0.055, hip_y, 0.0])
        knee = hip + np.array([s * 0.01, -0.19, 0.06 * ls + 0.02])
        foot = knee + np.array([s * 0.008, -0.19, -0.03 * ls - 0.01])
        limb(ps, hip, knee, 0.052, 0.042, pants)
        limb(ps, knee, foot, 0.040, 0.032, pants if s < 0 else skin)
        ps.append(P(Ellipsoid(foot + np.array([0, -0.005, 0.03]), (0.036, 0.022, 0.06)), skin, 0.02))
    # torso (hunched forward)
    pelvis = np.array([0, hip_y + 0.03, 0.0])
    chest = np.array([0.0, hip_y + 0.22, lean])
    ps.append(P(Ellipsoid(pelvis, (0.095, 0.07, 0.065)), pants, 0.03))
    ps.append(P(Ellipsoid((0, hip_y + 0.11, lean * 0.5), (0.085, 0.09, 0.06)), shirt, 0.05))
    ps.append(P(Ellipsoid(chest, (0.11, 0.08, 0.07)), shirt, 0.05))
    # exposed ribs through a torn hole on the left chest
    ribs(ps, chest + np.array([0.035, 0.035, 0.055]), 0.05, BONE, n=3)
    ps.append(P(Sphere(chest + np.array([0.04, 0.0, 0.07]), 0.035), MOUTH, 0.0, op='sub'))
    # neck & head
    neck = chest + np.array([0.0, 0.07, 0.01])
    head_c = neck + np.array([0.015, 0.075, 0.03 + lean * 0.4])
    if pose == 'pain':
        head_c = head_c + np.array([0.04, -0.01, -0.04])
    limb(ps, chest + np.array([0, 0.03, 0]), head_c, 0.035, 0.03, skin)
    ps.append(P(Ellipsoid(head_c, (0.066, 0.074, 0.066)), skin, 0.02, disp=(0.005, 30, 3)))
    ps.append(P(Ellipsoid(head_c + np.array([0, -0.035, 0.035]), (0.045, 0.03, 0.03)), skin, 0.02))
    # brow ridge & cheekbones
    ps.append(P(Ellipsoid(head_c + np.array([0, 0.012, 0.045]), (0.05, 0.016, 0.02)), skin, 0.01))
    # jaw hanging open
    jaw_open = 0.07 if pose == 'attack' else 0.045
    jaw = head_c + np.array([0.0, -0.05 - jaw_open * 0.5, 0.03])
    ps.append(P(Ellipsoid(jaw, (0.04, 0.022, 0.035)), skin, 0.015))
    # mouth cavity
    ps.append(P(Ellipsoid(head_c + np.array([0, -0.035 - jaw_open * 0.3, 0.06]), (0.026, 0.012 + jaw_open * 0.35, 0.03)), MOUTH, 0.005, op='sub'))
    # teeth
    for i in range(5):
        x = (i - 2) * 0.01
        ps.append(P(Box(head_c + np.array([x, -0.03, 0.055 - abs(x) * 0.3]), (0.0042, 0.008, 0.004), r=0.002), TEETH, 0.0))
        ps.append(P(Box(jaw + np.array([x * 0.9, 0.012 + jaw_open * 0.15, 0.03 - abs(x) * 0.3]), (0.004, 0.007, 0.004), r=0.002), TEETH, 0.0))
    # eye sockets & glowing eyes
    for s in (-1, 1):
        ec = head_c + np.array([s * 0.025, 0.004, 0.056])
        ps.append(P(Sphere(ec, 0.02), BLACK, 0.006, op='sub'))
        ps.append(P(Sphere(ec + np.array([0, 0, -0.006]), 0.012), EYE_RED, 0.0))
    # nose hole
    ps.append(P(Ellipsoid(head_c + np.array([0, -0.014, 0.062]), (0.008, 0.01, 0.01)), BLACK, 0.0, op='sub'))
    # stringy hair
    for i in range(7):
        a = -0.8 + i * 0.27
        st = head_c + np.array([np.sin(a) * 0.05, 0.05, np.cos(a) * 0.02 - 0.02])
        en = st + np.array([np.sin(a) * 0.04, -0.09 - 0.02 * (i % 2), -0.01])
        ps.append(P(Cone(st, en, 0.006, 0.003), HAIR, 0.01))
    # arms
    sh_l = chest + np.array([-0.12, 0.04, -0.01])
    sh_r = chest + np.array([0.12, 0.04, -0.01])
    if pose == 'attack':
        hl = sh_l + np.array([-0.06, 0.2, 0.08])
        hr = sh_r + np.array([0.06, 0.24, 0.12])
        el = sh_l + np.array([-0.08, 0.08, 0.04])
        er = sh_r + np.array([0.08, 0.1, 0.05])
    elif pose == 'pain':
        hl = sh_l + np.array([-0.08, -0.05, 0.12])
        hr = sh_r + np.array([0.1, -0.2, 0.02])
        el = sh_l + np.array([-0.06, -0.08, 0.06])
        er = sh_r + np.array([0.05, -0.12, 0.0])
    else:
        a = 0.03 * sw
        hl = sh_l + np.array([0.02, -0.02 + a, 0.28])
        hr = sh_r + np.array([-0.01, -0.12 - a, 0.22])
        el = sh_l + np.array([-0.01, -0.06, 0.13])
        er = sh_r + np.array([0.02, -0.1, 0.1])
    for sh, el_, hd, s in ((sh_l, el, hl, -1), (sh_r, er, hr, 1)):
        ps.append(P(Sphere(sh, 0.04), shirt, 0.04))
        limb(ps, sh, el_, 0.034, 0.028, shirt if s < 0 else skin, 0.02)
        limb(ps, el_, hd, 0.027, 0.022, skin, 0.015, disp=(0.003, 40, 5))
        # clawed hand: palm + 4 long fingers
        ps.append(P(Ellipsoid(hd, (0.026, 0.02, 0.024)), skin, 0.01))
        fwd = norm(hd - el_)
        for f in range(4):
            off = np.array([(f - 1.5) * 0.013, -0.006 * abs(f - 1.5), 0.0])
            tip = hd + fwd * 0.05 + off * 1.4 + np.array([0, -0.02, 0])
            ps.append(P(Cone(hd + off * 0.7, tip, 0.0075, 0.004), skin, 0.006))
            ps.append(P(Cone(tip, tip + fwd * 0.015 + np.array([0, -0.012, 0]), 0.004, 0.0015), BONE, 0.0))
    # blood drool & wounds
    ps.append(P(Cone(jaw + np.array([0.008, -0.01, 0.03]), jaw + np.array([0.012, -0.06, 0.04]), 0.006, 0.003), BLOOD, 0.008))
    ps.append(P(Ellipsoid(chest + np.array([-0.04, -0.1, 0.06]), (0.03, 0.045, 0.01)), BLOOD, 0.01))
    return ps


def tilt_scene(ps, ang_z=0.0, ang_x=0.0, pivot=(0, 0, 0), shift=(0, 0, 0)):
    """Wrap a scene so it is rotated about pivot (used for falling/death frames)."""
    R = rot(ang_x, 0, ang_z)
    pv = np.asarray(pivot, float)
    sh = np.asarray(shift, float)

    class Wrap(Prim):
        def __init__(self, inner):
            self.inner = inner
            self.op = inner.op
            self.k = inner.k
            self.mat = inner.mat
            self.disp = None

        def d(self, p):
            q = (p - pv - sh) @ R + pv
            return self.inner.dist(q)

    # materials see world p; patch albedo by mapping back too
    out = []
    for pr in ps:
        w = Wrap(pr)
        if pr.mat is not None:
            m = pr.mat

            class MW(Mat):
                def __init__(self, m):
                    self.m = m
                    self.spec = m.spec
                    self.shin = m.shin
                    self.unlit = m.unlit

                def albedo(self, p, n):
                    return self.m.albedo((p - pv - sh) @ R + pv, n @ R)

                def glowv(self, p, n):
                    return self.m.glowv((p - pv - sh) @ R + pv, n @ R)
            w.mat = MW(m)
        out.append(w)
    return out


# ------------------------------------------------------------------ pumpkin helpers

def tri2d(px, py, a, b, c):
    """Signed distance to a 2D triangle (vectorized)."""
    p = np.stack([px, py], 1)
    a, b, c = (np.asarray(v, float) for v in (a, b, c))
    e0, e1, e2 = b - a, c - b, a - c
    v0, v1, v2 = p - a, p - b, p - c

    def seg(v, e):
        h = np.clip((v @ e) / (e @ e), 0, 1)
        return v - h[:, None] * e[None, :]
    pq0, pq1, pq2 = seg(v0, e0), seg(v1, e1), seg(v2, e2)
    s = np.sign(e0[0] * e2[1] - e0[1] * e2[0])
    d0 = np.stack([np.sum(pq0 * pq0, 1), s * (v0[:, 0] * e0[1] - v0[:, 1] * e0[0])], 1)
    d1 = np.stack([np.sum(pq1 * pq1, 1), s * (v1[:, 0] * e1[1] - v1[:, 1] * e1[0])], 1)
    d2 = np.stack([np.sum(pq2 * pq2, 1), s * (v2[:, 0] * e2[1] - v2[:, 1] * e2[0])], 1)
    dmin = np.minimum(np.minimum(d0[:, 0], d1[:, 0]), d2[:, 0])
    smin_ = np.minimum(np.minimum(d0[:, 1], d1[:, 1]), d2[:, 1])
    return -np.sqrt(dmin) * np.sign(smin_)


class TriPrism(Prim):
    """Triangle in local xy (center c), extruded along z from z0 to z1 (world z offsets)."""
    def __init__(self, c, a, b, cc, depth):
        self.c = np.asarray(c, float); self.a = a; self.b = b; self.cc = cc; self.dep = depth

    def d(self, p):
        q = p - self.c
        d2 = tri2d(q[:, 0], q[:, 1], self.a, self.b, self.cc)
        dz = np.abs(q[:, 2]) - self.dep
        return np.maximum(d2, dz)


class Pumpkin(Prim):
    def __init__(self, c, r, squash=0.8, ribs=10, amp=0.07):
        self.c = np.asarray(c, float); self.r = r; self.sq = squash; self.ribs = ribs; self.amp = amp

    def d(self, p):
        q = p - self.c
        q = q * np.array([1, 1 / self.sq, 1])
        ang = np.arctan2(q[:, 2], q[:, 0])
        rr = self.r * (1 - self.amp * np.abs(np.sin(ang * self.ribs / 2)) ** 0.6)
        ln = np.linalg.norm(q, axis=1)
        # flatten the poles a bit (dimples top/bottom)
        dim = np.exp(-((q[:, 0] ** 2 + q[:, 2] ** 2) / (self.r * 0.25) ** 2)) * self.r * 0.12
        return (ln - rr + dim * (np.abs(q[:, 1]) > 0)) * self.sq


def pumpkin_mat(base=(0.95, 0.45, 0.06), seed=2):
    base = np.asarray(base)

    def fn(p, n):
        v = fbm(p, 10.0, 3, seed)
        c = base[None, :] * (0.72 + 0.5 * v)[:, None]
        # darker in the rib grooves (use normal variation proxy via noise along angle)
        ang = np.arctan2(p[:, 2], p[:, 0])
        g = (np.abs(np.sin(ang * 5)) ** 0.5)
        c = c * (0.75 + 0.25 * g)[:, None]
        rot_ = np.clip((fbm(p, 5.0, 3, seed + 7) - 0.66) * 8, 0, 1)[:, None]
        c = c * (1 - rot_) + np.array([0.25, 0.18, 0.06])[None, :] * rot_
        return c
    return Mat(fn=fn, spec=0.35, shin=20)


FIRE = Mat((1.0, 0.72, 0.18), glow=1.0)
FIRE2 = Mat((1.0, 0.45, 0.05), glow=1.0)
STEM = Mat((0.32, 0.28, 0.1), var=0.3, vfreq=30)


def jack_face(ps, hc, r, fierce=1.0, glowmat=FIRE, z_front=None, mouth_open=1.0):
    """Carve a jack-o-lantern face into a pumpkin centered hc with radius r."""
    zf = hc[2] + r * 0.75 if z_front is None else z_front
    for s in (-1, 1):
        ec = hc + np.array([s * r * 0.38, r * 0.18, 0])
        ec[2] = zf
        # angry slanted triangle eyes
        a = (-r * 0.2, -r * 0.12)
        b = (r * 0.2, -r * 0.12)
        c = (s * r * 0.16 * fierce, r * 0.2)
        if s < 0:
            a, b = (-r * 0.22, -r * 0.14), (r * 0.18, -r * 0.05 * fierce)
        else:
            a, b = (-r * 0.18, -r * 0.05 * fierce), (r * 0.22, -r * 0.14)
        ps.append(P(TriPrism(ec, a, b, (s * r * 0.06, r * 0.18), r * 0.5), glowmat, 0.004, op='sub'))
    # nose
    nc = hc.copy(); nc[2] = zf; nc = nc + np.array([0, -r * 0.05, 0])
    ps.append(P(TriPrism(nc, (-r * 0.08, -r * 0.08), (r * 0.08, -r * 0.08), (0, r * 0.06), r * 0.5), glowmat, 0.003, op='sub'))
    # jagged grin
    mc = hc + np.array([0, -r * 0.38, 0]); mc[2] = zf - r * 0.05
    ps.append(P(Ellipsoid(mc, (r * 0.62, r * 0.17 * mouth_open + 0.004, r * 0.6)), glowmat, 0.004, op='sub'))
    return mc


# ------------------------------------------------------------------ SCARECROW (Gourdhead)

def scarecrow(pose='walk1'):
    burlap = Mat(fn=lambda p, n: np.tile(np.array([0.58, 0.46, 0.3]), (len(p), 1)) *
                 (0.75 + 0.35 * fbm(p, 14, 2, 3) + 0.08 * np.sin(p[:, 0] * 300) * np.sin(p[:, 1] * 300))[:, None])
    denim = cloth((0.18, 0.22, 0.34), seed=11)
    patch = cloth((0.5, 0.12, 0.1), seed=12)
    straw = Mat((0.86, 0.72, 0.32), var=0.25, vfreq=40)
    pk = pumpkin_mat()
    hatm = Mat((0.36, 0.26, 0.14), var=0.25, vfreq=12)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.40
    for s, ls in ((-1, sw), (1, -sw)):
        hip = np.array([s * 0.06, hip_y, 0])
        knee = hip + np.array([s * 0.012, -0.2, 0.05 * ls])
        foot = knee + np.array([0, -0.18, -0.03 * ls])
        limb(ps, hip, knee, 0.055, 0.048, denim)
        limb(ps, knee, foot, 0.048, 0.044, denim)
        # straw sticking out of the cuffs
        for k in range(5):
            a = k * 1.25
            st = foot + np.array([np.cos(a) * 0.03, 0.02, np.sin(a) * 0.03])
            limb(ps, st, st + np.array([np.cos(a) * 0.05, -0.04, np.sin(a) * 0.05]), 0.006, 0.002, straw, 0.0)
        ps.append(P(Ellipsoid(foot + np.array([0, 0.0, 0.02]), (0.04, 0.02, 0.05)), hatm, 0.02))
    # sack torso with overalls bib
    ps.append(P(Ellipsoid((0, hip_y + 0.04, 0), (0.1, 0.08, 0.07)), denim, 0.04))
    ps.append(P(Ellipsoid((0, hip_y + 0.2, 0.0), (0.12, 0.14, 0.075)), burlap, 0.05, disp=(0.006, 25, 4)))
    ps.append(P(Box((0, hip_y + 0.14, 0.06), (0.07, 0.07, 0.02), r=0.01), denim, 0.02))
    ps.append(P(Box((0.035, hip_y + 0.12, 0.08), (0.025, 0.025, 0.006), r=0.003), patch, 0.004))
    # rope belt
    ps.append(P(Torus((0, hip_y + 0.07, 0), 0.098, 0.012), straw, 0.01))
    # shoulders: crossbar stick
    sh_y = hip_y + 0.3
    ps.append(P(Cone((-0.3, sh_y, -0.02), (0.3, sh_y, -0.02), 0.014), Mat((0.3, 0.2, 0.1), var=0.3, vfreq=40), 0.0))
    # arms: sleeves stuffed with straw
    if pose == 'attack':
        hl = np.array([-0.26, sh_y - 0.02, 0.05]); hr = np.array([0.22, sh_y + 0.22, 0.1])
    elif pose == 'pain':
        hl = np.array([-0.24, sh_y + 0.08, 0.02]); hr = np.array([0.24, sh_y + 0.1, 0.02])
    else:
        hl = np.array([-0.28, sh_y - 0.06 - 0.02 * sw, 0.04]); hr = np.array([0.28, sh_y - 0.06 + 0.02 * sw, 0.04])
    for hd, s in ((hl, -1), (hr, 1)):
        sh = np.array([s * 0.1, sh_y, 0])
        mid = (sh + hd) / 2 + np.array([0, -0.02, 0])
        limb(ps, sh, mid, 0.045, 0.04, burlap if s < 0 else patch, 0.03)
        limb(ps, mid, hd, 0.04, 0.034, burlap, 0.02)
        for k in range(7):
            a = k * 0.9
            d = norm(hd - mid)
            st = hd + d * 0.01
            tip = st + d * 0.07 + np.array([np.cos(a) * 0.03, np.sin(a) * 0.035, np.sin(a * 1.7) * 0.02])
            limb(ps, st, tip, 0.007, 0.002, straw, 0.0)
    if pose == 'attack':
        ps.append(P(Sphere(hr + np.array([0, 0.07, 0.02]), 0.055), FIREBALL, 0.0, disp=(0.012, 22, 9)))
    # neck straw tuft
    for k in range(9):
        a = k * 0.7
        st = np.array([0, sh_y + 0.02, 0])
        limb(ps, st, st + np.array([np.cos(a) * 0.07, 0.03, np.sin(a) * 0.06]), 0.008, 0.002, straw, 0.0)
    # pumpkin head
    hc = np.array([0.0, sh_y + 0.14, 0.01])
    tiltx = 0.0
    if pose == 'pain':
        hc = hc + np.array([0.03, -0.01, -0.02])
    r = 0.12
    ps.append(P(Pumpkin(hc, r, squash=0.82, ribs=10, amp=0.08), pk, 0.0))
    jack_face(ps, hc, r, fierce=1.3, mouth_open=1.6 if pose == 'attack' else 1.0)
    # teeth in the grin
    for i in range(4):
        x = (i - 1.5) * r * 0.28
        top = (i % 2 == 0)
        y = hc[1] - r * 0.3 if top else hc[1] - r * 0.46
        ps.append(P(Box((x, y, hc[2] + r * 0.7), (r * 0.05, r * 0.07, r * 0.12)), pk, 0.0))
    ps.append(P(Cone(hc + np.array([0, r * 0.7, 0]), hc + np.array([0.02, r * 1.15, -0.01]), 0.018, 0.012), STEM, 0.01))
    # floppy torn hat
    hatc = hc + np.array([-0.01, r * 0.62, -0.01])
    ps.append(P(Cyl(hatc, 0.19, 0.006, R=rot(0.15, 0, 0.12)), hatm, 0.0, disp=(0.01, 9, 5)))
    ps.append(P(Cone(hatc, hatc + np.array([0.03, 0.12, -0.02]), 0.085, 0.045), hatm, 0.02, disp=(0.006, 12, 6)))
    ps.append(P(Sphere(hatc + np.array([0.13, -0.01, 0.12]), 0.05), BLACK, 0.0, op='sub'))
    return ps


# ------------------------------------------------------------------ WRAITH (ghost)

def fire_mat(core=(1.0, 0.97, 0.7), mid=(1.0, 0.62, 0.1), edge=(0.85, 0.15, 0.02), seed=0):
    core, mid, edge = np.asarray(core), np.asarray(mid), np.asarray(edge)

    def fn(p, n):
        f = np.clip(n[:, 2], 0, 1) ** 1.5 + (fbm(p, 30, 2, seed) - 0.5) * 0.5
        f = np.clip(f, 0, 1)[:, None]
        c = np.where(f > 0.5, mid + (core - mid) * (f - 0.5) * 2, edge + (mid - edge) * f * 2)
        return c
    return Mat(fn=fn, glow=1.0)


FIREBALL = fire_mat()
GREENFIRE = fire_mat((0.9, 1.0, 0.8), (0.45, 1.0, 0.25), (0.05, 0.45, 0.1), seed=3)


def wraith(pose='walk1'):
    shroud = Mat(fn=lambda p, n: np.tile(np.array([0.5, 0.56, 0.62]), (len(p), 1)) *
                 (0.5 + 0.55 * fbm(p, 7, 3, 21))[:, None] * (0.55 + 0.45 * np.clip((p[:, 1] - 0.05) / 0.6, 0, 1))[:, None], spec=0.15)
    skull = Mat((0.9, 0.9, 0.88), var=0.15, vfreq=25, spec=0.3)
    dark = Mat((0.02, 0.02, 0.04))
    eye = Mat((0.45, 0.95, 1.0), glow=1.0)
    ps = []
    sway = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    base = 0.1
    def body_d(p):
        y = p[:, 1]
        t = np.clip((y - base) / 0.56, 0, 1)
        rad = 0.13 - 0.04 * t + 0.06 * (1 - t) ** 2
        ang = np.arctan2(p[:, 2], p[:, 0])
        wav = np.sin(ang * 6 + y * 10 + sway) * 0.022 * (1 - t)
        cx = 0.035 * sway * (1 - t) ** 2
        d = np.sqrt((p[:, 0] - cx) ** 2 + (p[:, 2] / 0.7) ** 2) - (rad + wav)
        # long ragged streamers at the hem
        strands = np.abs(np.sin(ang * 5 + 1.3)) ** 3
        hem = base - 0.09 * strands + 0.05 * (fbm(p * np.array([1, 0, 1]), 11, 2, 3) - 0.5)
        d = np.maximum(d, hem - y)
        d = np.maximum(d, y - 0.62)
        return d * 0.65
    ps.append(P(Func(body_d), shroud, 0.0))
    # hood
    hc = np.array([0.0, 0.69, 0.0])
    ps.append(P(Ellipsoid(hc + np.array([0, 0.02, -0.02]), (0.105, 0.12, 0.1)), shroud, 0.06, disp=(0.006, 16, 2)))
    ps.append(P(Ellipsoid(hc + np.array([0, -0.01, 0.07]), (0.075, 0.095, 0.08)), dark, 0.03, op='sub'))
    # skull inside the hood
    sc = hc + np.array([0, -0.005, 0.03])
    ps.append(P(Ellipsoid(sc, (0.052, 0.062, 0.055)), skull, 0.0))
    for s in (-1, 1):
        ec = sc + np.array([s * 0.022, 0.012, 0.045])
        ps.append(P(Sphere(ec, 0.021), dark, 0.004, op='sub'))
        ps.append(P(Sphere(ec + np.array([0, -0.002, -0.006]), 0.006), eye, 0.0))
    ps.append(P(TriPrism(sc + np.array([0, -0.012, 0.055]), (-0.008, -0.008), (0.008, -0.008), (0, 0.008), 0.02), dark, 0.0, op='sub'))
    # long unhinged screaming jaw
    mo = 0.075 if pose == 'attack' else 0.05
    jaw = sc + np.array([0, -0.045 - mo * 0.6, 0.02])
    ps.append(P(Ellipsoid(jaw, (0.032, 0.02, 0.03)), skull, 0.01))
    ps.append(P(Ellipsoid(sc + np.array([0, -0.04 - mo * 0.35, 0.045]), (0.022, mo * 0.5, 0.03)), dark, 0.006, op='sub'))
    for i in range(4):
        x = (i - 1.5) * 0.01
        ps.append(P(Box(sc + np.array([x, -0.035, 0.045]), (0.0035, 0.007, 0.004)), TEETH, 0.0))
        ps.append(P(Box(jaw + np.array([x, 0.014, 0.022]), (0.0035, 0.007, 0.004)), TEETH, 0.0))
    # arms with long bony claws
    rch = 0.12 if pose == 'attack' else 0.0
    for s in (-1, 1):
        sh = np.array([s * 0.11, 0.58, 0.0])
        el = sh + np.array([s * 0.08, -0.05, 0.08 + rch * 0.4])
        hd = el + np.array([-s * 0.02, 0.03 + rch * 0.7, 0.12 + rch])
        if pose == 'pain':
            hd = el + np.array([s * 0.06, 0.13, -0.03])
        limb(ps, sh, el, 0.055, 0.05, shroud, 0.04, disp=(0.01, 13, 7))
        limb(ps, el, hd, 0.02, 0.014, skull, 0.01)
        dd = norm(hd - el)
        for f in range(4):
            off = np.array([(f - 1.5) * 0.017, 0, 0])
            k1 = hd + dd * 0.05 + off * 1.4
            tip = k1 + dd * 0.06 + np.array([0, -0.025, 0.01])
            limb(ps, hd + off * 0.5, k1, 0.0055, 0.004, skull, 0.004)
            limb(ps, k1, tip, 0.004, 0.0012, skull, 0.002)
    return ps


# ------------------------------------------------------------------ WITCH

def witch(pose='walk1'):
    skin = Mat(fn=lambda p, n: np.tile(np.array([0.45, 0.62, 0.3]), (len(p), 1)) * (0.75 + 0.4 * fbm(p, 18, 2, 31))[:, None], spec=0.2)
    dress = cloth((0.14, 0.1, 0.18), seed=33)
    hatm = Mat((0.1, 0.08, 0.12), var=0.2, vfreq=10)
    band = Mat((0.45, 0.1, 0.5), var=0.1)
    hair = Mat((0.08, 0.07, 0.07), var=0.3, vfreq=50)
    wood = Mat((0.3, 0.2, 0.12), var=0.35, vfreq=30)
    orb = Mat((0.5, 1.0, 0.3), glow=1.0)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    # long skirt (cone) with ragged hem
    def skirt(p):
        y = p[:, 1]
        t = np.clip(y / 0.42, 0, 1)
        rad = 0.17 - 0.09 * t
        cx = sw * 0.015 * (1 - t)
        d = np.sqrt((p[:, 0] - cx) ** 2 + (p[:, 2] / 0.8) ** 2) - rad
        hem = 0.01 + 0.04 * fbm(p * np.array([1, 0, 1]), 11, 2, 4)
        d = np.maximum(d, hem - y)
        d = np.maximum(d, y - 0.45)
        return d * 0.75
    ps.append(P(Func(skirt), dress, 0.0))
    ps.append(P(Ellipsoid((0, 0.5, 0.0), (0.085, 0.13, 0.065)), dress, 0.05))
    ps.append(P(Torus((0, 0.43, 0), 0.075, 0.012), band, 0.01))
    # head
    hc = np.array([0.0, 0.69, 0.03])
    if pose == 'pain':
        hc = hc + np.array([-0.03, -0.01, -0.02])
    limb(ps, (0, 0.6, 0), hc, 0.03, 0.03, skin, 0.02)
    ps.append(P(Ellipsoid(hc, (0.052, 0.062, 0.055)), skin, 0.02))
    # long crooked nose with wart, pointed chin
    limb(ps, hc + np.array([0, 0.005, 0.045]), hc + np.array([0.005, -0.03, 0.105]), 0.014, 0.005, skin, 0.01)
    ps.append(P(Sphere(hc + np.array([0.012, -0.012, 0.075]), 0.007), skin, 0.003))
    limb(ps, hc + np.array([0, -0.04, 0.03]), hc + np.array([0.004, -0.085, 0.06]), 0.02, 0.006, skin, 0.015)
    # glowing eyes
    for s in (-1, 1):
        ec = hc + np.array([s * 0.022, 0.012, 0.045])
        ps.append(P(Sphere(ec, 0.013), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + np.array([0, 0, -0.004]), 0.008), EYE_GRN, 0.0))
    # cackling mouth
    mo = 0.016 if pose == 'attack' else 0.008
    ps.append(P(Ellipsoid(hc + np.array([0, -0.035, 0.05]), (0.024, mo, 0.02)), MOUTH, 0.004, op='sub'))
    for i in range(3):
        ps.append(P(Box(hc + np.array([(i - 1) * 0.013, -0.03, 0.05]), (0.004, 0.006, 0.004)), TEETH, 0.0))
    # stringy hair
    for i in range(11):
        a = -1.4 + i * 0.28
        st = hc + np.array([np.sin(a) * 0.05, 0.03, np.cos(a) * 0.02 - 0.03])
        en = st + np.array([np.sin(a) * 0.05, -0.2 - 0.03 * (i % 3), -0.02])
        limb(ps, st, en, 0.009, 0.004, hair, 0.01)
    # pointy hat
    brim = hc + np.array([0, 0.045, -0.005])
    ps.append(P(Cyl(brim, 0.15, 0.005, R=rot(0.12, 0, 0.08)), hatm, 0.0))
    tip = brim + np.array([-0.07, 0.3, -0.06])
    mid = brim + np.array([0.01, 0.16, -0.01])
    limb(ps, brim, mid, 0.07, 0.04, hatm, 0.01)
    limb(ps, mid, tip, 0.04, 0.008, hatm, 0.02)
    ps.append(P(Cyl(brim + np.array([0, 0.018, 0]), 0.071, 0.01, R=rot(0.12, 0, 0.08)), band, 0.0))
    # arms: left holds staff, right claws / casts
    shl, shr = np.array([-0.09, 0.6, 0]), np.array([0.09, 0.6, 0])
    if pose == 'attack':
        hl = shl + np.array([-0.05, 0.02, 0.18]); hr = shr + np.array([0.04, 0.03, 0.2])
    elif pose == 'pain':
        hl = shl + np.array([-0.1, 0.05, 0.02]); hr = shr + np.array([0.1, 0.08, 0.0])
    else:
        hl = shl + np.array([-0.06, -0.12, 0.1]); hr = shr + np.array([0.05, -0.08 + 0.02 * sw, 0.14])
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + np.array([s * 0.04, -0.05, -0.02])
        limb(ps, sh, el, 0.035, 0.03, dress, 0.03)
        limb(ps, el, hd, 0.03, 0.02, dress, 0.02)
        ps.append(P(Sphere(hd, 0.018), skin, 0.01))
        dd = norm(hd - el)
        for f in range(4):
            off = np.array([(f - 1.5) * 0.01, 0, 0])
            limb(ps, hd + off, hd + dd * 0.05 + off * 1.5 + np.array([0, -0.01, 0]), 0.005, 0.002, skin, 0.004)
    # staff in left hand
    st0 = hl + np.array([0, -0.4, -0.02]); st1 = hl + np.array([0.0, 0.22, 0.02])
    limb(ps, st0, st1, 0.012, 0.01, wood, 0.0, disp=(0.004, 30, 8))
    for k in range(3):
        a = k * 2.1
        limb(ps, st1, st1 + np.array([np.cos(a) * 0.04, 0.05, np.sin(a) * 0.04]), 0.008, 0.003, wood, 0.0)
    ps.append(P(Sphere(st1 + np.array([0, 0.04, 0]), 0.03 if pose != 'attack' else 0.038), orb, 0.0))
    if pose == 'attack':
        ps.append(P(Sphere(hr + np.array([0, 0.02, 0.05]), 0.035), GREENFIRE, 0.0, disp=(0.008, 25, 3)))
    return ps


# ------------------------------------------------------------------ BOSS: the Pumpkin King

def pumpking(pose='walk1'):
    flesh = Mat(fn=lambda p, n: np.tile(np.array([0.42, 0.1, 0.06]), (len(p), 1)) *
                (0.65 + 0.6 * fbm(p, 8, 3, 51))[:, None], spec=0.3, shin=16)
    robe = cloth((0.08, 0.06, 0.07), seed=55, blood=0.08)
    vine = Mat((0.16, 0.28, 0.08), var=0.3, vfreq=20, spec=0.2)
    crown = Mat((0.85, 0.65, 0.2), var=0.2, vfreq=25, spec=0.9, shin=30)
    horn = Mat((0.18, 0.13, 0.1), var=0.25, vfreq=15, spec=0.3)
    pk = pumpkin_mat((0.85, 0.36, 0.05), seed=9)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    S = 1.0
    # legs under tattered robe
    def robe_d(p):
        y = p[:, 1]
        t = np.clip(y / 0.6, 0, 1)
        rad = 0.3 - 0.12 * t
        cx = sw * 0.03 * (1 - t)
        ang = np.arctan2(p[:, 2], p[:, 0])
        d = np.sqrt((p[:, 0] - cx) ** 2 + (p[:, 2] / 0.7) ** 2) - (rad + 0.02 * np.sin(ang * 9 + y * 6))
        hem = 0.02 + 0.08 * fbm(p * np.array([1, 0, 1]), 7, 2, 14)
        d = np.maximum(d, hem - y)
        d = np.maximum(d, y - 0.66)
        return d * 0.7
    ps.append(P(Func(robe_d), robe, 0.0))
    for s in (-1, 1):
        ps.append(P(Ellipsoid((s * 0.1 + sw * s * 0.02, 0.04, 0.12), (0.07, 0.04, 0.09)), horn, 0.02))
    # massive torso
    ch = np.array([0, 0.86, 0.02])
    ps.append(P(Ellipsoid((0, 0.68, 0), (0.18, 0.14, 0.12)), flesh, 0.06))
    ps.append(P(Ellipsoid(ch, (0.25, 0.17, 0.14)), flesh, 0.08, disp=(0.01, 14, 3)))
    # pecs / abs ridges
    for s in (-1, 1):
        ps.append(P(Ellipsoid(ch + np.array([s * 0.09, 0.01, 0.1]), (0.1, 0.07, 0.05)), flesh, 0.04))
    for i in range(3):
        for s in (-1, 1):
            ps.append(P(Ellipsoid((s * 0.04, 0.72 + i * 0.05, 0.11), (0.035, 0.022, 0.025)), flesh, 0.02))
    # glowing cracks on chest: thin glowing veins
    for i in range(5):
        a = np.array([np.sin(i * 1.7) * 0.12, 0.8 + i * 0.03, 0.135])
        b = a + np.array([np.cos(i * 2.3) * 0.08, 0.04, -0.01])
        ps.append(P(Cone(a, b, 0.006, 0.003), FIRE2, 0.0))
    # vines wrapping torso
    for i in range(4):
        a0 = i * 1.6
        pts = [np.array([np.cos(a0 + t * 3) * 0.24, 0.62 + t * 0.35, np.sin(a0 + t * 3) * 0.16]) for t in np.linspace(0, 1, 6)]
        for k in range(5):
            limb(ps, pts[k], pts[k + 1], 0.014, 0.012, vine, 0.01)
    # spiked shoulder pads
    for s in (-1, 1):
        sp = ch + np.array([s * 0.26, 0.08, -0.01])
        ps.append(P(Ellipsoid(sp, (0.11, 0.07, 0.1)), horn, 0.04))
        for k in range(3):
            base = sp + np.array([s * (0.02 + k * 0.04), 0.05, (k - 1) * 0.04])
            limb(ps, base, base + np.array([s * 0.05, 0.12, 0.0]), 0.025, 0.002, horn, 0.01)
    # arms
    if pose == 'attack':
        hands = [ch + np.array([-0.45, 0.35, 0.18]), ch + np.array([0.45, 0.4, 0.2])]
    elif pose == 'pain':
        hands = [ch + np.array([-0.38, -0.05, 0.25]), ch + np.array([0.36, 0.02, 0.3])]
    else:
        hands = [ch + np.array([-0.4, -0.3 - 0.03 * sw, 0.15]), ch + np.array([0.4, -0.28 + 0.03 * sw, 0.18])]
    for s, hd in zip((-1, 1), hands):
        sh = ch + np.array([s * 0.26, 0.05, 0])
        el = (sh + hd) / 2 + np.array([s * 0.08, -0.05, -0.04])
        limb(ps, sh, el, 0.075, 0.065, flesh, 0.05)
        limb(ps, el, hd, 0.065, 0.05, flesh, 0.04, disp=(0.006, 18, 2))
        ps.append(P(Ellipsoid(hd, (0.06, 0.05, 0.055)), flesh, 0.03))
        dd = norm(hd - el)
        for f in range(4):
            off = np.array([(f - 1.5) * 0.028, 0, 0])
            k1 = hd + dd * 0.06 + off * 1.3
            tip = k1 + dd * 0.06 + np.array([0, -0.03, 0.02])
            limb(ps, hd + off * 0.6, k1, 0.016, 0.012, flesh, 0.01)
            limb(ps, k1, tip, 0.011, 0.002, BONE, 0.0)
        if pose == 'attack':
            ps.append(P(Sphere(hd + dd * 0.1 + np.array([0, 0.08, 0]), 0.08), FIREBALL, 0.0, disp=(0.02, 14, 4 + s)))
    # neck & giant flaming pumpkin head
    hc = ch + np.array([0, 0.3, 0.04])
    if pose == 'pain':
        hc = hc + np.array([0.05, -0.02, -0.03])
    limb(ps, ch + np.array([0, 0.1, 0]), hc, 0.08, 0.07, flesh, 0.05)
    r = 0.2
    ps.append(P(Pumpkin(hc, r, squash=0.82, ribs=12, amp=0.09), pk, 0.02))
    jack_face(ps, hc, r, fierce=1.6, mouth_open=1.9 if pose == 'attack' else 1.3)
    for i in range(6):
        x = (i - 2.5) * r * 0.2
        top = (i % 2 == 0)
        y = hc[1] - r * 0.27 if top else hc[1] - r * 0.52
        ps.append(P(Box((x, y, hc[2] + r * 0.72), (r * 0.04, r * 0.08, r * 0.14)), pk, 0.0))
    # horns & crown
    for s in (-1, 1):
        b0 = hc + np.array([s * r * 0.7, r * 0.45, -0.02])
        b1 = b0 + np.array([s * 0.12, 0.08, -0.02])
        b2 = b1 + np.array([s * 0.03, 0.14, 0.02])
        limb(ps, b0, b1, 0.045, 0.03, horn, 0.03)
        limb(ps, b1, b2, 0.03, 0.004, horn, 0.01)
    cr = hc + np.array([0, r * 0.72, -0.01])
    ps.append(P(Torus(cr, r * 0.55, 0.018), crown, 0.0))
    for k in range(7):
        a = k * 2 * np.pi / 7 + 0.2
        b = cr + np.array([np.cos(a) * r * 0.55, 0, np.sin(a) * r * 0.55])
        limb(ps, b, b + np.array([0, 0.09 + 0.03 * (k % 2), 0]), 0.018, 0.002, crown, 0.004)
    # flames licking out of the crown
    ps.append(P(Cone(hc + np.array([0, r * 0.6, 0]), hc + np.array([0.02, r * 1.4, 0]), 0.07, 0.01), FIREBALL, 0.04, disp=(0.02, 12, 6)))
    return ps
