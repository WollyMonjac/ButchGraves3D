"""Tiny vectorized SDF raymarcher for pre-rendered sprites (numpy).

World: x right, y up, z toward the camera. Units ~ 1 = one wall height.
"""
import numpy as np

# ------------------------------------------------------------------ noise

def _hash(ix, iy, iz, seed):
    n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ ((seed * 2654435761) & 0xffffffff)
    n = n & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    n = n ^ (n >> 16)
    return (n & 0xffff).astype(np.float64) / 65535.0


def vnoise(p, seed=0):
    """3D value noise in [0,1], p (n,3) already scaled."""
    i = np.floor(p).astype(np.int64)
    f = p - i
    u = f * f * (3 - 2 * f)
    res = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                h = _hash((i[:, 0] + dx) & 0xffffffff, (i[:, 1] + dy) & 0xffffffff, (i[:, 2] + dz) & 0xffffffff, seed)
                w = (u[:, 0] if dx else 1 - u[:, 0]) * (u[:, 1] if dy else 1 - u[:, 1]) * (u[:, 2] if dz else 1 - u[:, 2])
                res = res + h * w
    return res


def fbm(p, freq=1.0, octaves=3, seed=0):
    tot = 0.0
    amp = 1.0
    norm = 0.0
    for o in range(octaves):
        tot = tot + vnoise(p * (freq * 2 ** o), seed + o * 17) * amp
        norm += amp
        amp *= 0.5
    return tot / norm


def norm(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def rot(ax=0.0, ay=0.0, az=0.0):
    """Rotation matrix: rotate about x, then y, then z (radians)."""
    cx, sx = np.cos(ax), np.sin(ax)
    cy, sy = np.cos(ay), np.sin(ay)
    cz, sz = np.cos(az), np.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


# ------------------------------------------------------------------ primitives

class Prim:
    op = 'add'      # add | sub | int
    k = 0.0         # smoothness
    mat = None
    disp = None     # (amp, freq, seed)

    def __init__(self):
        pass

    def d(self, p):
        raise NotImplementedError

    def dist(self, p):
        d = self.d(p)
        if self.disp is not None:
            amp, fq, sd = self.disp
            d = d + (fbm(p, fq, 2, sd) - 0.5) * 2 * amp
        return d


def _local(p, c, R):
    q = p - c
    if R is not None:
        q = q @ R
    return q


class Sphere(Prim):
    def __init__(self, c, r):
        self.c = np.asarray(c, float); self.r = r

    def d(self, p):
        return np.linalg.norm(p - self.c, axis=1) - self.r


class Ellipsoid(Prim):
    def __init__(self, c, r, R=None):
        self.c = np.asarray(c, float); self.r = np.asarray(r, float); self.R = R

    def d(self, p):
        q = _local(p, self.c, self.R)
        k0 = np.linalg.norm(q / self.r, axis=1)
        k1 = np.linalg.norm(q / (self.r * self.r), axis=1)
        return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


class Cone(Prim):
    """Round cone / capsule between a (radius ra) and b (radius rb)."""
    def __init__(self, a, b, ra, rb=None):
        self.a = np.asarray(a, float); self.b = np.asarray(b, float)
        self.ra = ra; self.rb = ra if rb is None else rb

    def d(self, p):
        pa = p - self.a
        ba = self.b - self.a
        h = np.clip((pa @ ba) / (ba @ ba), 0, 1)
        return np.linalg.norm(pa - h[:, None] * ba[None, :], axis=1) - (self.ra + (self.rb - self.ra) * h)


class Box(Prim):
    def __init__(self, c, half, R=None, r=0.0):
        self.c = np.asarray(c, float); self.h = np.asarray(half, float); self.R = R; self.rr = r

    def d(self, p):
        q = np.abs(_local(p, self.c, self.R)) - (self.h - self.rr)
        out = np.linalg.norm(np.maximum(q, 0), axis=1)
        ins = np.minimum(np.max(q, axis=1), 0)
        return out + ins - self.rr


class Cyl(Prim):
    """Capped cylinder along local y."""
    def __init__(self, c, r, h, R=None, rr=0.0):
        self.c = np.asarray(c, float); self.r = r; self.hh = h; self.R = R; self.rr = rr

    def d(self, p):
        q = _local(p, self.c, self.R)
        dx = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2) - (self.r - self.rr)
        dy = np.abs(q[:, 1]) - (self.hh - self.rr)
        out = np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dy, 0) ** 2)
        return out + np.minimum(np.maximum(dx, dy), 0) - self.rr


class Torus(Prim):
    """Torus in local xz plane."""
    def __init__(self, c, R1, r, R=None):
        self.c = np.asarray(c, float); self.R1 = R1; self.r = r; self.R = R

    def d(self, p):
        q = _local(p, self.c, self.R)
        a = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2) - self.R1
        return np.sqrt(a * a + q[:, 1] ** 2) - self.r


class Func(Prim):
    def __init__(self, fn):
        self.fn = fn

    def d(self, p):
        return self.fn(p)


def P(prim, mat, k=0.0, op='add', disp=None):
    prim.mat = mat
    prim.k = k
    prim.op = op
    prim.disp = disp
    return prim


# ------------------------------------------------------------------ materials

class Mat:
    """albedo: rgb tuple or fn(p,n)->(n,3). glow: 0..1 emission (fullbright). spec: specular."""
    def __init__(self, col=(0.5, 0.5, 0.5), fn=None, glow=0.0, spec=0.0, shin=24.0, var=0.0, vfreq=8.0, seed=0,
                 glowfn=None, unlit=False):
        self.col = np.asarray(col, float)
        self.fn = fn
        self.glow = glow
        self.glowfn = glowfn
        self.spec = spec
        self.shin = shin
        self.var = var
        self.vfreq = vfreq
        self.seed = seed
        self.unlit = unlit

    def albedo(self, p, n):
        if self.fn is not None:
            return self.fn(p, n)
        c = np.tile(self.col, (len(p), 1))
        if self.var > 0:
            v = fbm(p, self.vfreq, 2, self.seed) - 0.5
            c = c * (1 + 2 * self.var * v)[:, None]
        return c

    def glowv(self, p, n):
        if self.glowfn is not None:
            return self.glowfn(p, n)
        return np.full(len(p), float(self.glow))


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


# ------------------------------------------------------------------ scene eval

def smin(a, b, k):
    if k <= 0:
        return np.minimum(a, b)
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def smax(a, b, k):
    return -smin(-a, -b, k)


def scene_eval(prims, p, want_mat=False):
    d = np.full(len(p), 1e9)
    mid = np.full(len(p), -1, dtype=np.int32)
    for i, pr in enumerate(prims):
        di = pr.dist(p)
        if pr.op == 'add':
            if want_mat:
                closer = di < d + pr.k * 0.25
                mid = np.where(closer, i, mid)
            d = smin(d, di, pr.k)
        elif pr.op == 'sub':
            nd = smax(d, -di, pr.k)
            if want_mat and pr.mat is not None:
                carved = (-di > d - 1e-4)
                mid = np.where(carved, i, mid)
            d = nd
        elif pr.op == 'int':
            d = smax(d, di, pr.k)
    if want_mat:
        return d, mid
    return d


# ------------------------------------------------------------------ render

class Light:
    def __init__(self, d, col, kind='dir', shadow=False):
        self.d = norm(d)
        self.col = np.asarray(col, float)
        self.kind = kind
        self.shadow = shadow


DEFAULT_LIGHTS = [
    Light((-0.55, 0.75, 0.65), (1.05, 0.98, 0.9), 'dir', True),     # key: upper left front
    Light((0.75, 0.25, -0.6), (0.55, 0.7, 1.15), 'rim'),             # cold moon rim
    Light((0.1, -1.0, 0.45), (0.7, 0.32, 0.1), 'dir'),               # orange under-glow
]


class Img:
    pass


def render(prims, W, H, cam_y, cam_h, ss=3, persp=True, fov_dist=6.0, lights=None, ambient=0.28,
           exposure=1.0, steps=110, shadows=True, ao=True, cam_x=0.0, cam_z_tilt=0.0, bg_ground=False, tspan=5.5, tstart=None):
    """Render prims into (H, W) image. Camera views the slab x in [-w/2, w/2], y in [cam_y - cam_h/2, cam_y + cam_h/2]
    (cam_h world units over H pixels). Returns Img with rgb (H,W,3) 0..1, alpha (H,W) bool, glow (H,W) bool."""
    lights = DEFAULT_LIGHTS if lights is None else lights
    Hs, Ws = H * ss, W * ss
    scale = cam_h / Hs
    jj, ii = np.mgrid[0:Hs, 0:Ws]
    sx = (ii + 0.5 - Ws / 2) * scale + cam_x
    sy = (Hs / 2 - (jj + 0.5)) * scale + cam_y
    n = Hs * Ws
    if persp:
        eye = np.array([cam_x, cam_y + cam_z_tilt, fov_dist])
        tgt = np.stack([sx.ravel(), sy.ravel(), np.zeros(n)], 1)
        D = tgt - eye[None, :]
        D /= np.linalg.norm(D, axis=1)[:, None]
        O = np.tile(eye, (n, 1))
        t = np.full(n, max(0.02, fov_dist - 2.5) if tstart is None else tstart)
    else:
        O = np.stack([sx.ravel(), sy.ravel(), np.full(n, 3.0)], 1)
        D = np.tile(np.array([0, 0, -1.0]), (n, 1))
        t = np.full(n, 0.5)
    tmax = t + tspan
    active = np.ones(n, bool)
    hit = np.zeros(n, bool)
    for it in range(steps):
        idx = np.nonzero(active)[0]
        if len(idx) == 0:
            break
        p = O[idx] + D[idx] * t[idx, None]
        d = scene_eval(prims, p)
        t[idx] += d * 0.8
        done = d < 0.0012
        hit[idx[done]] = True
        far = t[idx] > tmax[idx]
        active[idx[done | far]] = False
    out = Img()
    rgb = np.zeros((n, 3))
    glow = np.zeros(n)
    hidx = np.nonzero(hit)[0]
    if len(hidx):
        p = O[hidx] + D[hidx] * t[hidx, None]
        e = 0.0025
        ks = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], float)
        nrm = np.zeros((len(hidx), 3))
        for k in ks:
            nrm += k[None, :] * scene_eval(prims, p + k[None, :] * e)[:, None]
        nrm /= np.linalg.norm(nrm, axis=1)[:, None] + 1e-12
        _, mid = scene_eval(prims, p, want_mat=True)
        V = -D[hidx]
        # ambient occlusion
        occ = np.ones(len(hidx))
        if ao:
            s = 0.0
            for h, w in ((0.015, 1.0), (0.04, 0.7), (0.08, 0.5), (0.15, 0.3)):
                dd = scene_eval(prims, p + nrm * h)
                s = s + np.maximum(h - dd, 0) * w / h
            occ = np.clip(1 - s * 0.38, 0.15, 1)
        alb = np.zeros((len(hidx), 3))
        spec = np.zeros(len(hidx))
        shin = np.full(len(hidx), 24.0)
        unlit = np.zeros(len(hidx), bool)
        for i, pr in enumerate(prims):
            m = mid == i
            if not m.any() or pr.mat is None:
                continue
            alb[m] = pr.mat.albedo(p[m], nrm[m])
            glow[hidx[m]] = pr.mat.glowv(p[m], nrm[m])
            spec[m] = pr.mat.spec
            shin[m] = pr.mat.shin
            unlit[m] = pr.mat.unlit
        light = np.tile(np.array([ambient, ambient, ambient * 1.08]), (len(hidx), 1)) * occ[:, None]
        for L in lights:
            if L.kind == 'rim':
                ndl = np.clip(nrm @ L.d, 0, 1)
                fr = (1 - np.clip(np.sum(nrm * V, 1), 0, 1)) ** 1.5
                light += (ndl * (0.35 + fr)) [:, None] * L.col[None, :]
            else:
                ndl = np.clip(nrm @ L.d, 0, 1)
                sh = np.ones(len(hidx))
                if L.shadow and shadows:
                    sh = soft_shadow(prims, p + nrm * 0.004, L.d)
                light += (ndl * sh)[:, None] * L.col[None, :] * occ[:, None] ** 0.5
                if True:
                    Hv = V + L.d[None, :]
                    Hv /= np.linalg.norm(Hv, axis=1)[:, None]
                    sp = np.clip(np.sum(nrm * Hv, 1), 0, 1) ** shin * spec * sh
                    light += sp[:, None] * L.col[None, :]
        c = alb * light * exposure
        c = np.where(unlit[:, None], alb, c)
        g = glow[hidx][:, None]
        c = c * (1 - g) + alb * g
        rgb[hidx] = c
    out.rgb_ss = rgb.reshape(Hs, Ws, 3)
    out.alpha_ss = hit.reshape(Hs, Ws)
    out.glow_ss = (glow > 0.5).reshape(Hs, Ws)
    # downsample
    def red(a):
        return a.reshape(H, ss, W, ss, *a.shape[2:]).sum(axis=(1, 3))
    cov = red(out.alpha_ss.astype(float))
    csum = red(out.rgb_ss * out.alpha_ss[..., None])
    out.rgb = np.clip(csum / np.maximum(cov, 1e-9)[..., None], 0, 1.4)
    out.alpha = cov >= (ss * ss) * 0.5
    out.glow = red(out.glow_ss.astype(float)) >= (ss * ss) * 0.4
    out.glow &= out.alpha
    out.W, out.H = W, H
    return out


def soft_shadow(prims, p, ld, steps=28, k=10.0):
    n = len(p)
    res = np.ones(n)
    t = np.full(n, 0.01)
    act = np.ones(n, bool)
    for i in range(steps):
        idx = np.nonzero(act)[0]
        if len(idx) == 0:
            break
        q = p[idx] + ld[None, :] * t[idx, None]
        d = scene_eval(prims, q)
        res[idx] = np.minimum(res[idx], np.clip(k * d / t[idx], 0, 1))
        t[idx] += np.clip(d, 0.01, 0.15)
        stop = (d < 0.001) | (t[idx] > 2.0)
        res[idx[d < 0.001]] = 0
        act[idx[stop]] = False
    return 0.25 + 0.75 * res


def to_rgba(img, glow_boost=True):
    out = np.zeros((img.H, img.W, 4), np.uint8)
    out[..., :3] = (np.clip(img.rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    out[..., 3] = np.where(img.alpha, 255, 0)
    return out
