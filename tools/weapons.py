"""First-person weapon models. Camera eye at (0,0,1) looking -z; view plane z=0 spans
x in [-0.8, 0.8] (160 virtual px), y in [-0.6, 0.6]."""
import numpy as np
from sdf import *
from monsters import FIREBALL, BONE, BLOOD, pumpkin_mat, jack_face, Pumpkin
from props import IRON, BRASS, SILVER, WOOD, DWOOD

GLOVE = Mat((0.09, 0.08, 0.08), var=0.2, vfreq=40, spec=0.35, shin=20)
SKIN = Mat(fn=lambda p, n: np.tile(np.array([0.78, 0.55, 0.4]), (len(p), 1)) * (0.85 + 0.25 * fbm(p, 30, 2, 5))[:, None], spec=0.15)
JACKET = Mat(fn=lambda p, n: np.tile(np.array([0.28, 0.17, 0.1]), (len(p), 1)) * (0.65 + 0.5 * fbm(p, 14, 3, 8))[:, None], spec=0.3, shin=12)
CHROME = Mat(fn=lambda p, n: np.tile(np.array([0.5, 0.52, 0.58]), (len(p), 1)) * (0.6 + 0.6 * np.clip(n[:, 1] * 0.5 + 0.5, 0, 1))[:, None], spec=1.4, shin=40)
GUNMETAL = Mat((0.2, 0.21, 0.24), var=0.15, vfreq=30, spec=0.8, shin=35)
OLIVE = Mat((0.27, 0.31, 0.18), var=0.2, vfreq=15, spec=0.4, shin=20)
DIRT = Mat((0.28, 0.2, 0.12), var=0.4, vfreq=30)

WEAPON_LIGHTS = [
    Light((-0.4, 0.7, 0.6), (1.0, 0.95, 0.88), 'dir', True),
    Light((0.6, 0.3, -0.7), (0.5, 0.6, 1.0), 'rim'),
    Light((0.0, -0.8, 0.6), (0.45, 0.25, 0.12), 'dir'),
]


def frame_axes(fwd, up_hint=(0, 1, 0)):
    f = norm(fwd)
    side = norm(np.cross(np.asarray(up_hint, float), -f))
    up = np.cross(-f, side)
    # local x = side, y = up, z = -fwd  (columns)
    return np.stack([side, up, -f], 1)


def fist(ps, c, R, mat=GLOVE, s=1.0, thumb_side=-1):
    """Fist gripping a handle along local y. R columns: x side, y up(grip axis), z back (toward eye)."""
    c = np.asarray(c, float)
    L = lambda v: c + R @ (np.asarray(v, float) * s)
    ps.append(P(Box(L((0, 0, 0.025)), np.array([0.042, 0.05, 0.03]) * s, R=R, r=0.018 * s), mat, 0.02))
    for i in range(4):
        y = 0.036 - i * 0.024
        ps.append(P(Cone(L((thumb_side * -0.04, y, 0.03)), L((thumb_side * -0.045, y, -0.035)), 0.015 * s, 0.013 * s), SKIN if i < 2 else mat, 0.012))
        ps.append(P(Cone(L((thumb_side * -0.045, y, -0.035)), L((thumb_side * 0.0, y, -0.05)), 0.013 * s, 0.012 * s), SKIN, 0.01))
    ps.append(P(Cone(L((thumb_side * 0.035, 0.04, 0.02)), L((thumb_side * 0.03, 0.065, -0.03)), 0.016 * s, 0.013 * s), SKIN, 0.012))
    return L((0, -0.06, 0.08))   # wrist position


def arm(ps, wrist, elbow, r=0.06):
    ps.append(P(Cone(wrist, elbow, r * 0.75, r), JACKET, 0.03, disp=(0.006, 18, 3)))
    ps.append(P(Torus(wrist + norm(elbow - wrist) * 0.03, r * 0.72, 0.012, R=frame_axes(elbow - wrist) @ rot(np.pi / 2, 0, 0)), JACKET, 0.01))


def flash(ps, tip, d, size=0.12, seed=0, n=7):
    rs = np.random.RandomState(seed)
    ps.append(P(Sphere(tip + d * size * 0.3, size * 0.45), FIREBALL, 0.0, disp=(size * 0.12, 30, seed)))
    R = frame_axes(d)
    for i in range(n):
        a = i * 2 * np.pi / n + rs.uniform(-0.3, 0.3)
        v = R @ np.array([np.cos(a), np.sin(a), 0.0])
        ln = size * rs.uniform(0.9, 1.6)
        ps.append(P(Cone(tip + d * size * 0.2, tip + v * ln + d * size * 0.5, size * 0.22, 0.004), FIREBALL, 0.03))
    ps.append(P(Cone(tip, tip + d * size * 1.6, size * 0.3, 0.01), FIREBALL, 0.03))


def transform(ps, R, pivot):
    """Rigidly rotate a list of prims about pivot (uses tilt_scene machinery)."""
    from monsters import tilt_scene
    # tilt_scene takes euler; build generic wrapper here instead
    pv = np.asarray(pivot, float)

    class Wrap(Prim):
        def __init__(self, inner):
            self.inner = inner; self.op = inner.op; self.k = inner.k; self.disp = None; self.mat = inner.mat

        def d(self, p):
            return self.inner.dist((p - pv) @ R + pv)
    out = []
    for pr in ps:
        w = Wrap(pr)
        if pr.mat is not None:
            m = pr.mat

            class MW(Mat):
                def __init__(self, m):
                    self.m = m; self.spec = m.spec; self.shin = m.shin; self.unlit = m.unlit

                def albedo(self, p, n):
                    return self.m.albedo((p - pv) @ R + pv, n @ R)

                def glowv(self, p, n):
                    return self.m.glowv((p - pv) @ R + pv, n @ R)
            w.mat = MW(m)
        out.append(w)
    return out

# ------------------------------------------------------------------ revolver


def revolver(frame=0):
    ps = []
    d = norm(np.array([-0.42, 0.1, -1.0]))
    R = frame_axes(d)
    base = np.array([0.1, -0.33, 0.25])          # rear of frame
    L = lambda v: base + R @ np.asarray(v, float)
    # frame and cylinder
    ps.append(P(Box(L((0, 0.0, -0.06)), (0.035, 0.045, 0.08), R=R, r=0.01), CHROME, 0.0))
    cyl_c = L((0, 0.0, -0.08))
    def drum(p):
        q = (p - cyl_c) @ R
        rr = np.sqrt(q[:, 0] ** 2 + q[:, 1] ** 2)
        ang = np.arctan2(q[:, 1], q[:, 0])
        flute = 0.006 * (np.cos(ang * 6) > 0.6)
        d1 = rr - (0.052 - flute)
        return np.maximum(d1, np.abs(q[:, 2]) - 0.045)
    ps.append(P(Func(drum), CHROME, 0.004))
    ps.append(P(Cyl(L((0, 0.018, -0.3)), 0.022, 0.18, R=R @ rot(np.pi / 2, 0, 0)), CHROME, 0.01))
    ps.append(P(Box(L((0, 0.045, -0.44)), (0.006, 0.012, 0.02), R=R), CHROME, 0.0))
    ps.append(P(Cyl(L((0, 0.018, -0.48)), 0.012, 0.02, R=R @ rot(np.pi / 2, 0, 0)), Mat((0.02, 0.02, 0.02)), 0.0, op='sub'))
    ps.append(P(Box(L((0, 0.06, 0.02)), (0.01, 0.018, 0.012), R=R @ rot(-0.5, 0, 0)), GUNMETAL, 0.0))
    # grip
    gR = R @ rot(-0.35, 0, 0)
    gc = L((0, -0.08, 0.04))
    ps.append(P(Box(gc, (0.03, 0.07, 0.035), R=gR, r=0.012), WOOD, 0.01))
    ps.append(P(Torus(L((0, -0.04, -0.04)), 0.028, 0.006, R=R @ rot(0, 0, np.pi / 2)), CHROME, 0.0))
    wr = fist(ps, gc + gR @ np.array([0, 0.0, 0.0]), gR, s=1.05, thumb_side=-1)
    arm(ps, wr, wr + np.array([0.12, -0.25, 0.3]))
    if frame == 1:
        tip = L((0, 0.018, -0.5))
        flash(ps, tip, d, 0.11, seed=3)
        ps = transform(ps, rot(-0.12, 0, 0.03), base + np.array([0, -0.1, 0.1]))
    return ps

# ------------------------------------------------------------------ shotgun (double barrel)


def shotgun(frame=0):
    ps = []
    d = norm(np.array([-0.3, 0.1, -1.0]))
    R = frame_axes(d)
    base = np.array([0.06, -0.36, 0.28])
    L = lambda v: base + R @ np.asarray(v, float)
    for s in (-1, 1):
        ps.append(P(Cyl(L((s * 0.024, 0.02, -0.33)), 0.024, 0.3, R=R @ rot(np.pi / 2, 0, 0)), GUNMETAL, 0.004))
        ps.append(P(Cyl(L((s * 0.024, 0.02, -0.64)), 0.016, 0.03, R=R @ rot(np.pi / 2, 0, 0)), Mat((0.01, 0.01, 0.01)), 0.0, op='sub'))
    ps.append(P(Box(L((0, 0.045, -0.33)), (0.006, 0.006, 0.29), R=R), GUNMETAL, 0.004))
    ps.append(P(Sphere(L((0, 0.052, -0.6)), 0.007), BRASS, 0.0))
    ps.append(P(Box(L((0, -0.02, -0.32)), (0.04, 0.025, 0.12), R=R, r=0.012), WOOD, 0.01))
    ps.append(P(Box(L((0, 0.005, -0.02)), (0.05, 0.04, 0.06), R=R, r=0.012), GUNMETAL, 0.006))
    for s in (-1, 1):
        ps.append(P(Sphere(L((s * 0.025, 0.035, 0.03)), 0.01), CHROME, 0.0))
    gR = R @ rot(-0.3, 0, 0)
    gc = L((0, -0.07, 0.06))
    ps.append(P(Box(gc, (0.032, 0.06, 0.05), R=gR, r=0.015), WOOD, 0.01))
    wr = fist(ps, gc, gR, s=1.05, thumb_side=-1)
    arm(ps, wr, wr + np.array([0.16, -0.22, 0.28]))
    # left hand under fore-end
    lc = L((0, -0.055, -0.3))
    lR = R @ rot(np.pi / 2, 0, 0)
    wl = fist(ps, lc, R @ rot(-1.3, 0.2, 0), s=1.0, thumb_side=1)
    arm(ps, wl, wl + np.array([-0.3, -0.25, 0.3]))
    if frame == 1:
        for s in (-1, 1):
            flash(ps, L((s * 0.024, 0.02, -0.66)), d, 0.13, seed=4 + s)
        ps = transform(ps, rot(-0.16, 0, 0.02), base + np.array([0, -0.15, 0.1]))
    elif frame == 2:
        ps = transform(ps, rot(0.55, 0.25, -0.35), base + np.array([0, -0.1, 0.0]))
    return ps

# ------------------------------------------------------------------ tommy gun


def tommy(frame=0):
    ps = []
    d = norm(np.array([-0.32, 0.08, -1.0]))
    R = frame_axes(d)
    base = np.array([0.08, -0.34, 0.26])
    L = lambda v: base + R @ np.asarray(v, float)
    # receiver
    ps.append(P(Box(L((0, 0.01, -0.1)), (0.035, 0.035, 0.14), R=R, r=0.01), GUNMETAL, 0.0))
    # finned barrel
    fc = L((0, 0.015, -0.33))
    def fins(p):
        q = (p - fc) @ R
        rr = np.sqrt(q[:, 0] ** 2 + q[:, 1] ** 2)
        f = 0.007 * (np.sin(q[:, 2] * 260) > 0.2)
        return np.maximum(rr - (0.022 + f), np.abs(q[:, 2]) - 0.1)
    ps.append(P(Func(fins), GUNMETAL, 0.0))
    ps.append(P(Cyl(L((0, 0.015, -0.48)), 0.012, 0.06, R=R @ rot(np.pi / 2, 0, 0)), GUNMETAL, 0.0))
    ps.append(P(Box(L((0, 0.012, -0.55)), (0.02, 0.02, 0.015), R=R, r=0.005), GUNMETAL, 0.0))
    # drum magazine
    ps.append(P(Cyl(L((0, -0.08, -0.13)), 0.075, 0.025, R=R @ rot(0, 0, np.pi / 2)), GUNMETAL, 0.006))
    ps.append(P(Cyl(L((0.027, -0.08, -0.13)), 0.02, 0.006, R=R @ rot(0, 0, np.pi / 2)), BRASS, 0.0))
    # vertical fore-grip
    fg = L((0, -0.07, -0.3))
    fR = R @ rot(-0.2, 0, 0)
    ps.append(P(Box(fg, (0.022, 0.06, 0.025), R=fR, r=0.012), WOOD, 0.006))
    wl = fist(ps, fg + fR @ np.array([0, -0.01, 0]), fR, s=1.0, thumb_side=1)
    arm(ps, wl, wl + np.array([-0.32, -0.25, 0.28]))
    # pistol grip + right hand
    gR = R @ rot(-0.35, 0, 0)
    gc = L((0, -0.07, 0.02))
    ps.append(P(Box(gc, (0.026, 0.06, 0.03), R=gR, r=0.01), WOOD, 0.01))
    wr = fist(ps, gc, gR, s=1.05, thumb_side=-1)
    arm(ps, wr, wr + np.array([0.16, -0.24, 0.28]))
    # cocking knob
    ps.append(P(Sphere(L((0.0, 0.05, -0.05)), 0.012), CHROME, 0.0))
    if frame in (1, 2):
        flash(ps, L((0, 0.012, -0.58)), d, 0.1 if frame == 1 else 0.075, seed=5 + frame, n=5 + frame)
        ps = transform(ps, rot(-0.06 * frame, 0, 0.01 * (frame * 2 - 3)), base + np.array([0, -0.1, 0.1]))
    return ps

# ------------------------------------------------------------------ pumpkin launcher


def launcher(frame=0):
    ps = []
    d = norm(np.array([-0.25, 0.06, -1.0]))
    R = frame_axes(d)
    base = np.array([0.24, -0.3, 0.22])
    L = lambda v: base + R @ np.asarray(v, float)
    tube_c = L((0, 0.04, -0.25))
    ps.append(P(Cyl(tube_c, 0.085, 0.3, R=R @ rot(np.pi / 2, 0, 0), rr=0.01), OLIVE, 0.0))
    for z in (-0.05, -0.42):
        ps.append(P(Torus(L((0, 0.04, z)), 0.088, 0.012, R=R @ rot(np.pi / 2, 0, 0)), BRASS, 0.0))
    # jack-o-lantern muzzle
    mz = L((0, 0.04, -0.56))
    ps.append(P(Cyl(mz, 0.1, 0.04, R=R @ rot(np.pi / 2, 0, 0), rr=0.02), pumpkin_mat(seed=21), 0.006))
    ps.append(P(Cyl(L((0, 0.04, -0.6)), 0.068, 0.05, R=R @ rot(np.pi / 2, 0, 0)), Mat((0.02, 0.01, 0.0)) if frame == 0 else FIREBALL, 0.0, op='sub'))
    # painted teeth on muzzle ring (small boxes)
    for i in range(6):
        a = i * np.pi / 3 + 0.5
        ps.append(P(Box(L((np.cos(a) * 0.075, 0.04 + np.sin(a) * 0.075, -0.6)), (0.012, 0.012, 0.01), R=R @ rot(0, 0, a)), Mat((0.05, 0.03, 0.02)), 0.0))
    # sight
    ps.append(P(Box(L((-0.06, 0.13, -0.2)), (0.01, 0.03, 0.04), R=R, r=0.004), GUNMETAL, 0.0))
    ps.append(P(Sphere(L((-0.06, 0.165, -0.2)), 0.012), Mat((1.0, 0.2, 0.05), glow=1.0), 0.0))
    # grips
    gR = R @ rot(-0.25, 0, 0)
    gc = L((0, -0.08, -0.08))
    ps.append(P(Box(gc, (0.026, 0.06, 0.03), R=gR, r=0.01), GUNMETAL, 0.01))
    wr = fist(ps, gc, gR, s=1.1, thumb_side=-1)
    arm(ps, wr, wr + np.array([0.18, -0.25, 0.25]))
    fg = L((0, -0.08, -0.32))
    ps.append(P(Box(fg, (0.024, 0.055, 0.028), R=gR, r=0.01), GUNMETAL, 0.01))
    wl = fist(ps, fg, gR, s=1.05, thumb_side=1)
    arm(ps, wl, wl + np.array([-0.35, -0.22, 0.28]))
    if frame == 1:
        flash(ps, L((0, 0.04, -0.66)), d, 0.16, seed=9, n=8)
        ps = transform(ps, rot(-0.1, 0, 0.0), base + np.array([0, -0.1, 0.1]))
    return ps

# ------------------------------------------------------------------ shovel


def shovel(frame=0):
    ps = []
    steel = Mat(fn=lambda p, n: np.tile(np.array([0.55, 0.56, 0.6]), (len(p), 1)) * (0.7 + 0.45 * fbm(p, 20, 3, 4))[:, None]
                + np.clip((fbm(p, 8, 2, 11) - 0.58) * 4, 0, 1)[:, None] * np.array([[-0.2, -0.35, -0.38]]), spec=0.9, shin=25)
    # handle from bottom-right (near) up to blade at upper right
    if frame == 0:
        h0 = np.array([0.42, -0.62, 0.35]); h1 = np.array([0.3, 0.05, -0.15])
    elif frame == 1:
        h0 = np.array([0.5, -0.6, 0.3]); h1 = np.array([0.52, 0.15, -0.2])
    else:
        h0 = np.array([0.25, -0.55, 0.32]); h1 = np.array([-0.25, -0.15, -0.35])
    dvec = norm(h1 - h0)
    ps.append(P(Cone(h0, h1, 0.022, 0.02), WOOD, 0.0, disp=(0.002, 60, 4)))
    # blade: flat spade, normal facing camera-ish
    R = frame_axes(dvec, up_hint=(0, 0, 1))
    bc = h1 + dvec * 0.13
    def blade(p):
        q = (p - bc) @ R
        # local: x side, y = along handle? frame_axes uses -fwd as z, so along-handle is -z
        u, v, w = q[:, 0], -q[:, 2], q[:, 1]
        width = 0.085 * np.clip(1 - np.maximum(v - 0.04, 0) / 0.11, 0, 1) ** 0.6
        dx = np.abs(u) - width
        dy = np.abs(v) - 0.12
        dz = np.abs(w + 0.02 * (u / 0.09) ** 2) - 0.006
        return np.maximum(np.maximum(dx, dy), dz)
    ps.append(P(Func(blade), steel, 0.004))
    ps.append(P(Cone(h1 - dvec * 0.03, bc - dvec * 0.06, 0.028, 0.024), steel, 0.01))
    if frame == 2:
        ps.append(P(Ellipsoid(bc + dvec * 0.06, (0.05, 0.03, 0.02), R=R), BLOOD, 0.01))
    else:
        ps.append(P(Ellipsoid(bc + dvec * 0.08, (0.04, 0.02, 0.012), R=R), DIRT, 0.01))
    # hands on handle
    fR = frame_axes(dvec, up_hint=(1, 0, 0))
    fR = np.stack([fR[:, 1], dvec, np.cross(fR[:, 1], dvec)], 1)
    w1 = fist(ps, h0 + dvec * 0.12, fR, s=1.1, thumb_side=-1)
    arm(ps, w1, w1 + np.array([0.15, -0.25, 0.3]))
    w2 = fist(ps, h0 + dvec * 0.45, fR, s=1.05, thumb_side=1)
    arm(ps, w2, w2 + np.array([-0.3, -0.3, 0.3]))
    return ps


def place(ps, k, src, dst):
    """Scale scene by k about src and move src to dst."""
    src = np.asarray(src, float); dst = np.asarray(dst, float)

    class Wrap(Prim):
        def __init__(self, inner):
            self.inner = inner; self.op = inner.op; self.k = inner.k * k; self.disp = None; self.mat = inner.mat

        def d(self, p):
            return self.inner.dist(src + (p - dst) / k) * k
    out = []
    for pr in ps:
        w = Wrap(pr)
        if pr.mat is not None:
            m = pr.mat

            class MW(Mat):
                def __init__(self, m):
                    self.m = m; self.spec = m.spec; self.shin = m.shin; self.unlit = m.unlit

                def albedo(self, p, n):
                    return self.m.albedo(src + (p - dst) / k, n)

                def glowv(self, p, n):
                    return self.m.glowv(src + (p - dst) / k, n)
            w.mat = MW(m)
        out.append(w)
    return out


PLACE = {
    'revolver': (2.9, (0.1, -0.33, 0.25), (0.34, -0.42, 0.0)),
    'shotgun': (2.6, (0.06, -0.36, 0.28), (0.3, -0.46, 0.05)),
    'tommy': (2.7, (0.08, -0.34, 0.26), (0.3, -0.44, 0.02)),
    'launcher': (2.2, (0.24, -0.3, 0.22), (0.38, -0.4, 0.1)),
    'shovel': (1.5, (0.4, -0.5, 0.3), (0.42, -0.62, 0.3)),
}


def weapon(name, frame):
    fn = {'revolver': revolver, 'shotgun': shotgun, 'tommy': tommy, 'launcher': launcher, 'shovel': shovel}[name]
    k, s, d = PLACE[name]
    return place(fn(frame), k, s, d)
