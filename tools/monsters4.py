"""Episode 5 (Curse of the Jade Skull) monsters: SDF models. Feet at y=0, facing +z. 1 unit = wall height."""
import numpy as np
from sdf import *
from monsters import limb, ribs, cloth, tilt_scene, TriPrism, fire_mat, BONE, TEETH, MOUTH, BLOOD, BLACK, EYE_RED, EYE_GRN, \
    EYE_YEL, HAIR
from monsters2 import V, OLD_BONE, RUST, STEEL, GOLD, GLOSS_RED

# ------------------------------------------------------------------ materials

def bandage(seed=0, base=(0.78, 0.72, 0.56)):
    base = np.asarray(base)

    def fn(p, n):
        # wraps: diagonal bands around the body, dirty and stained
        t = p[:, 1] * 70 + p[:, 0] * 18 + np.sin(p[:, 2] * 40) * 2.0
        band = 0.78 + 0.22 * np.abs(np.sin(t))
        gap = np.abs(np.sin(t)) < 0.12
        v = fbm(p, 20, 3, seed)
        c = base[None, :] * (band * (0.7 + 0.45 * v))[:, None]
        c[gap] *= 0.45
        stain = fbm(p, 6, 3, seed + 4) > 0.64
        c[stain] = c[stain] * 0.6 + np.array([0.3, 0.22, 0.1]) * 0.4
        return c
    return Mat(fn=fn, spec=0.1, shin=10)


def pelt(seed=0):
    """Jaguar pelt: tawny gold with black rosettes."""
    def fn(p, n):
        v = fbm(p, 10, 3, seed)
        c = np.tile(np.array([0.78, 0.5, 0.16]), (len(p), 1)) * (0.75 + 0.35 * v)[:, None]
        q = p * 38.0
        cell = np.floor(q)
        f = q - cell - 0.5
        h = np.sin(cell[:, 0] * 12.9898 + cell[:, 1] * 78.233 + cell[:, 2] * 37.719) * 43758.5453
        jit = (h - np.floor(h)) * 0.3
        r = np.sqrt((f ** 2).sum(1)) + jit * 0.2
        ring = (r > 0.26) & (r < 0.38)
        dot = r < 0.1
        c[ring | dot] = np.array([0.08, 0.05, 0.03])
        belly = n[:, 2] > 0.75
        c[belly & ~(ring | dot)] = c[belly & ~(ring | dot)] * 0.6 + np.array([0.9, 0.85, 0.7]) * 0.4
        return c
    return Mat(fn=fn, spec=0.25, shin=16)


def jade(seed=0, base=(0.18, 0.62, 0.42)):
    base = np.asarray(base)

    def fn(p, n):
        v = fbm(p, 12, 3, seed)
        vein = np.abs(fbm(p, 18, 2, seed + 2) - 0.5) < 0.03
        c = base[None, :] * (0.6 + 0.6 * v)[:, None]
        c[vein] = c[vein] * 0.5 + np.array([0.75, 0.95, 0.85]) * 0.5
        return c
    return Mat(fn=fn, spec=1.2, shin=50)


SKIN_BROWN = Mat((0.48, 0.3, 0.18), var=0.15, vfreq=30, spec=0.3)
OBSIDIAN = Mat((0.05, 0.05, 0.07), spec=1.6, shin=70)
WOOD = Mat((0.38, 0.24, 0.12), var=0.25, vfreq=40, spec=0.2)
FEATHER_G = Mat(fn=lambda p, n: np.tile(np.array([0.1, 0.62, 0.32]), (len(p), 1)) * (0.6 + 0.6 * fbm(p, 40, 2, 9))[:, None], spec=0.6)
FEATHER_R = Mat((0.85, 0.12, 0.08), var=0.2, vfreq=40, spec=0.5)
FEATHER_B = Mat((0.1, 0.35, 0.85), var=0.2, vfreq=40, spec=0.5)
CLOTH_RED = cloth((0.62, 0.08, 0.06), seed=91, torn=0.66)
LINEN_W = cloth((0.84, 0.83, 0.8), seed=93, torn=0.7)
EYE_JADE = Mat((0.4, 1.0, 0.6), glow=1.0)
JADEFIRE = fire_mat((0.85, 1.0, 0.9), (0.3, 1.0, 0.5), (0.0, 0.4, 0.2), seed=95)
GHOST_EYE = Mat((0.7, 0.9, 1.0), glow=1.0)


def feather(ps, base, tip, w, mat, tipmat=None):
    """A long flat feather from base to tip."""
    d = tip - base
    L = np.linalg.norm(d)
    d = d / L
    side = norm(np.cross(d, V(0, 0, 1)) + V(1e-4, 0, 0))
    up = norm(np.cross(side, d))
    R = np.stack([side, up, d], 1)
    ps.append(P(Ellipsoid((base + tip) / 2, (w, 0.006, L / 2), R=R), mat, 0.0))
    if tipmat is not None:
        ps.append(P(Ellipsoid(tip - d * L * 0.12, (w * 0.8, 0.007, L * 0.12), R=R), tipmat, 0.0))


def scaled_about(pr, s, pivot):
    """The same primitive, s times bigger around a pivot point."""
    class L(Prim):
        def __init__(q, inner):
            q.inner = inner; q.op = inner.op; q.k = inner.k * s; q.mat = inner.mat; q.disp = None

        def d(q, p):
            return q.inner.dist((p - pivot) / s + pivot) * s
    return L(pr)


def humanoid_legs(ps, hip_y, sw, mat_up, mat_lo, foot_mat, w=0.05, crouch=0.0):
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.06, hip_y, 0)
        knee = hip + V(s * 0.012, -0.2 + crouch * 0.05, 0.06 * ls + 0.03 + crouch * 0.06)
        foot = V(s * 0.07, 0.035, -0.03 * ls - 0.005)
        limb(ps, hip, knee, w, w * 0.8, mat_up, 0.02)
        limb(ps, knee, foot, w * 0.78, w * 0.6, mat_lo, 0.02)
        ps.append(P(Ellipsoid(foot + V(0, -0.012, 0.03), (0.035, 0.022, 0.06)), foot_mat, 0.02))


# ------------------------------------------------------------------ MUMMY

def mummy(pose='walk1'):
    wrap = bandage(5)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.41
    humanoid_legs(ps, hip_y, sw, wrap, wrap, wrap, 0.05)
    lean = 0.05 if pose != 'pain' else -0.06
    chest = V(0, hip_y + 0.24, lean)
    ps.append(P(Ellipsoid(V(0, hip_y + 0.04, 0), (0.09, 0.07, 0.065)), wrap, 0.03))
    ps.append(P(Ellipsoid(V(0, hip_y + 0.13, lean * 0.5), (0.08, 0.09, 0.06)), wrap, 0.05))
    ps.append(P(Ellipsoid(chest, (0.115, 0.085, 0.07)), wrap, 0.05))
    # a rotten hole in the wrappings: dried flesh and a rib or two
    ps.append(P(Sphere(chest + V(-0.045, -0.02, 0.07), 0.03), Mat((0.24, 0.16, 0.08)), 0.01, op='sub'))
    ribs(ps, chest + V(-0.05, 0.0, 0.035), 0.035, OLD_BONE, n=2)
    hc = chest + V(0.0, 0.16, 0.03 + lean * 0.3)
    if pose == 'pain':
        hc = hc + V(0.03, 0.0, -0.05)
    limb(ps, chest + V(0, 0.05, 0), hc, 0.04, 0.035, wrap, 0.02)
    ps.append(P(Ellipsoid(hc, (0.064, 0.074, 0.066)), wrap, 0.02, disp=(0.004, 40, 2)))
    # one eye peering through a gap in the wraps, the other socket dark
    ps.append(P(Box(hc + V(0, 0.008, 0.058), (0.05, 0.012, 0.012)), BLACK, 0.004, op='sub'))
    ps.append(P(Sphere(hc + V(0.022, 0.008, 0.052), 0.01), EYE_YEL, 0.0))
    ps.append(P(Sphere(hc + V(-0.022, 0.008, 0.052), 0.005), Mat((0.5, 0.4, 0.1), glow=1.0), 0.0))
    mo = 0.03 if pose == 'attack' else 0.012
    ps.append(P(Ellipsoid(hc + V(0, -0.038, 0.058), (0.026, mo, 0.02)), BLACK, 0.004, op='sub'))
    for i in range(4):
        x = (i - 1.5) * 0.011
        ps.append(P(Box(hc + V(x, -0.038 + mo * 0.6, 0.06), (0.004, 0.006, 0.003)), TEETH, 0.0))
    # arms stretched out in front (the classic shamble)
    shl, shr = chest + V(-0.13, 0.05, 0), chest + V(0.13, 0.05, 0)
    if pose == 'attack':
        hl, hr = shl + V(0.03, 0.12, 0.27), shr + V(-0.03, 0.15, 0.27)
    elif pose == 'pain':
        hl, hr = shl + V(-0.12, 0.08, 0.05), shr + V(0.1, -0.15, 0.04)
    else:
        a = 0.025 * sw
        hl, hr = shl + V(0.02, 0.0 + a, 0.3), shr + V(-0.02, -0.02 - a, 0.3)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.02, -0.02, 0)
        ps.append(P(Sphere(sh, 0.042), wrap, 0.04))
        limb(ps, sh, el, 0.036, 0.03, wrap, 0.02)
        limb(ps, el, hd, 0.03, 0.026, wrap, 0.02)
        ps.append(P(Ellipsoid(hd, (0.028, 0.022, 0.03)), wrap, 0.01))
        d = norm(hd - el)
        for f in range(4):
            off = V((f - 1.5) * 0.013, 0, 0)
            limb(ps, hd + off * 0.6, hd + off * 1.2 + d * 0.05 + V(0, -0.015, 0), 0.008, 0.006, wrap, 0.004)
        # a loose bandage hanging from the forearm
        lo = el + (hd - el) * 0.5
        limb(ps, lo + V(0, -0.02, 0), lo + V(s * 0.02, -0.17, -0.02), 0.012, 0.01, wrap, 0.0)
    # trailing strip from the hip
    limb(ps, V(0.07, hip_y, 0.03), V(0.11, 0.08, 0.0), 0.014, 0.011, wrap, 0.0)
    return ps


# ------------------------------------------------------------------ JAGUAR WARRIOR

def macuahuitl(ps, hand, d, up, length=0.32):
    """Wooden paddle club edged with obsidian blades."""
    d = norm(d)
    side = norm(np.cross(d, norm(up)))
    up2 = norm(np.cross(side, d))
    R = np.stack([side, up2, d], 1)
    limb(ps, hand - d * 0.03, hand + d * 0.06, 0.012, 0.012, WOOD, 0.0)
    c = hand + d * (0.06 + length / 2)
    ps.append(P(Box(c, (0.012, 0.05, length / 2), R=R, r=0.008), WOOD, 0.0))
    for k in range(6):
        t = 0.1 + k * 0.15
        p = hand + d * (0.06 + length * t)
        for sg in (-1, 1):
            ps.append(P(Box(p + up2 * sg * 0.056, (0.005, 0.016, 0.018), R=R), OBSIDIAN, 0.0))


def jaguar_head(ps, hc, mat, pose):
    ps.append(P(Ellipsoid(hc, (0.078, 0.066, 0.072)), mat, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.024, 0.062), (0.05, 0.036, 0.048)), mat, 0.025))        # broad muzzle
    for s in (-1, 1):
        ps.append(P(Ellipsoid(hc + V(s * 0.022, -0.03, 0.1), (0.022, 0.017, 0.012)), Mat((0.9, 0.82, 0.66), var=0.1, vfreq=40), 0.006))  # whisker pads
        for k in range(3):
            limb(ps, hc + V(s * 0.03, -0.03 + k * 0.006, 0.1), hc + V(s * 0.09, -0.04 + k * 0.012, 0.09), 0.0015, 0.0008, Mat((0.1, 0.1, 0.1)), 0.0)
    ps.append(P(TriPrism(hc + V(0, -0.006, 0.108), (-0.016, 0.008), (0.016, 0.008), (0, -0.01), 0.012), Mat((0.12, 0.06, 0.05), spec=0.6), 0.003))   # nose
    for s in (-1, 1):
        ps.append(P(Cone(hc + V(s * 0.05, 0.045, -0.005), hc + V(s * 0.07, 0.1, -0.015), 0.03, 0.006), mat, 0.012))        # ears
        ps.append(P(Cone(hc + V(s * 0.052, 0.05, 0.005), hc + V(s * 0.068, 0.092, -0.004), 0.016, 0.003), Mat((0.15, 0.08, 0.06)), 0.004))
        ec = hc + V(s * 0.03, 0.018, 0.058)
        ps.append(P(Sphere(ec, 0.013), BLACK, 0.003, op='sub'))
        ps.append(P(Ellipsoid(ec + V(0, 0, -0.004), (0.01, 0.007, 0.006)), EYE_YEL, 0.0))
    mo = 0.035 if pose == 'attack' else 0.012
    ps.append(P(Ellipsoid(hc + V(0, -0.05 - mo * 0.5, 0.07), (0.03, 0.008 + mo * 0.5, 0.03)), MOUTH, 0.004, op='sub'))
    for s in (-1, 1):
        ps.append(P(Cone(hc + V(s * 0.02, -0.04, 0.09), hc + V(s * 0.02, -0.068, 0.095), 0.006, 0.001), TEETH, 0.0))
        ps.append(P(Cone(hc + V(s * 0.018, -0.07 - mo, 0.088), hc + V(s * 0.018, -0.046 - mo, 0.092), 0.005, 0.001), TEETH, 0.0))


def jaguar(pose='walk1'):
    """A jaguar warrior of Xibalba: half man, half cat, with an obsidian-edged club and a crest of quetzal feathers."""
    fur = pelt(7)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.4
    crouch = 0.6 if pose == 'attack' else 0.3
    humanoid_legs(ps, hip_y, sw, fur, fur, fur, 0.058, crouch)
    # loincloth and belt
    ps.append(P(Box(V(0, hip_y - 0.06, 0.06), (0.055, 0.075, 0.008), R=rot(0.15, 0, 0), r=0.004), CLOTH_RED, 0.0))
    ps.append(P(Torus(V(0, hip_y + 0.02, 0), 0.085, 0.016, R=np.eye(3)), GOLD, 0.0))
    lean = 0.08 if pose != 'pain' else -0.04
    chest = V(0, hip_y + 0.26, lean)
    ps.append(P(Ellipsoid(V(0, hip_y + 0.06, 0), (0.095, 0.08, 0.07)), fur, 0.04))
    ps.append(P(Ellipsoid(chest, (0.14, 0.1, 0.085)), fur, 0.06))
    # gold pectoral
    ps.append(P(Cyl(chest + V(0, 0.01, 0.08), 0.04, 0.008, R=rot(np.pi / 2, 0, 0)), GOLD, 0.0))
    ps.append(P(Cyl(chest + V(0, 0.01, 0.088), 0.02, 0.006, R=rot(np.pi / 2, 0, 0)), jade(4), 0.0))
    hc = chest + V(0, 0.17, 0.04)
    if pose == 'pain':
        hc = hc + V(0.04, -0.01, -0.05)
    limb(ps, chest + V(0, 0.06, 0), hc, 0.05, 0.045, fur, 0.03)
    head = []
    jaguar_head(head, hc, fur, pose)
    ps += [scaled_about(pr, 1.35, hc) for pr in head]
    # quetzal feather crest
    for k in range(7):
        a = -0.9 + k * 0.3
        b = hc + V(np.sin(a) * 0.03, 0.06, -0.03)
        t = hc + V(np.sin(a) * 0.14, 0.2 + 0.03 * np.cos(a * 2), -0.08)
        feather(ps, b, t, 0.018, FEATHER_G, FEATHER_R if k % 2 else FEATHER_B)
    # tail
    limb(ps, V(0, hip_y, -0.05), V(0.06, hip_y - 0.12, -0.18), 0.022, 0.018, fur, 0.01)
    limb(ps, V(0.06, hip_y - 0.12, -0.18), V(0.14, hip_y - 0.18, -0.16), 0.018, 0.012, fur, 0.01)
    # arms: club in the right hand, claws on the left
    shl, shr = chest + V(-0.15, 0.05, 0), chest + V(0.15, 0.05, 0)
    if pose == 'attack':
        hl, hr = shl + V(-0.05, 0.05, 0.25), shr + V(0.04, 0.32, 0.02)
        cd, cu = V(-0.4, 0.75, 0.3), V(1, 0, 0)
    elif pose == 'pain':
        hl, hr = shl + V(-0.12, 0.1, 0.05), shr + V(0.16, -0.08, 0.02)
        cd, cu = V(0.7, -0.4, 0.2), V(0, 1, 0)
    else:
        a = 0.03 * sw
        hl, hr = shl + V(-0.02, -0.2 + a, 0.12), shr + V(0.05, -0.12 - a, 0.16)
        cd, cu = V(0.2, 0.55, 0.8), V(0, 1, 0)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.05, -0.03, -0.02)
        ps.append(P(Sphere(sh, 0.05), fur, 0.04))
        limb(ps, sh, el, 0.045, 0.038, fur, 0.03)
        limb(ps, el, hd, 0.036, 0.03, fur, 0.02)
        ps.append(P(Torus(el + (hd - el) * 0.7, 0.032, 0.008, R=rot(np.pi / 2, 0, 0)), GOLD, 0.0))
        ps.append(P(Ellipsoid(hd, (0.03, 0.025, 0.03)), fur, 0.01))
        if s < 0:
            d = norm(hd - el)
            for f in range(4):
                off = V((f - 1.5) * 0.014, 0, 0)
                limb(ps, hd + off + d * 0.02, hd + off * 1.2 + d * 0.055 + V(0, -0.02, 0), 0.005, 0.001, TEETH, 0.002)
    macuahuitl(ps, hr, cd, cu, 0.24)
    return ps


# ------------------------------------------------------------------ SKELETON CONQUISTADOR

def morion(ps, hc, mat):
    """The crested, upturned-brim helmet of a Spanish conquistador."""
    ps.append(P(Ellipsoid(hc + V(0, 0.035, 0), (0.07, 0.05, 0.075)), mat, 0.0))
    def brim(p):
        q = p - (hc + V(0, 0.01, 0))
        r = np.sqrt((q[:, 0] / 1.0) ** 2 + (q[:, 2] / 1.35) ** 2)
        y_edge = 0.03 * (q[:, 2] / 0.12) ** 2           # brim curls up front and back
        d1 = np.abs(q[:, 1] - y_edge) - 0.006
        d2 = r - 0.095
        return np.maximum(d1, d2) * 0.8
    ps.append(P(Func(brim), mat, 0.004))
    ps.append(P(Ellipsoid(hc + V(0, 0.09, 0), (0.008, 0.035, 0.07)), mat, 0.006))    # comb
    ps.append(P(Cone(hc + V(0, 0.1, -0.02), hc + V(0, 0.16, -0.06), 0.006, 0.002), FEATHER_R, 0.0))


def conq(pose='walk1'):
    """A conquistador who came for the temple gold three hundred years ago and never left."""
    bone = OLD_BONE
    sash = cloth((0.55, 0.06, 0.06), seed=97, torn=0.6)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.42
    lean = 0.03 if pose != 'pain' else -0.04
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.05, hip_y, 0)
        knee = hip + V(s * 0.008, -0.2, 0.06 * ls + 0.01)
        ank = knee + V(0, -0.19, -0.03 * ls - 0.005)
        limb(ps, hip, knee, 0.017, 0.013, bone, 0.01)
        ps.append(P(Sphere(knee, 0.021), bone, 0.01))
        limb(ps, knee, ank, 0.014, 0.011, bone, 0.01)
        # tall leather boots
        limb(ps, knee + V(0, -0.04, 0), ank + V(0, -0.02, 0), 0.03, 0.028, Mat((0.2, 0.12, 0.06), var=0.2, vfreq=30, spec=0.4), 0.0)
        ps.append(P(Ellipsoid(ank + V(0, -0.02, 0.03), (0.03, 0.02, 0.055)), Mat((0.16, 0.1, 0.05)), 0.01))
    ps.append(P(Ellipsoid(V(0, hip_y + 0.02, 0), (0.075, 0.042, 0.04)), bone, 0.01))
    # baggy rotten breeches
    for s in (-1, 1):
        ps.append(P(Ellipsoid(V(s * 0.05, hip_y - 0.05, 0.005), (0.045, 0.08, 0.045)), cloth((0.3, 0.2, 0.12), seed=98, torn=0.6), 0.02))
    for k in range(4):
        ps.append(P(Sphere(V(0, hip_y + 0.05 + k * 0.032, -0.015 + lean * k / 7), 0.014), bone, 0.004))
    c = V(0, hip_y + 0.25, lean)
    # rusted breastplate with a hole blown through it
    ps.append(P(Box(c + V(0, 0.03, 0.01), (0.1, 0.1, 0.04), r=0.035), RUST, 0.01))
    ps.append(P(Ellipsoid(c + V(0, 0.0, 0.045), (0.08, 0.1, 0.03)), RUST, 0.02))              # the belly ridge
    ps.append(P(Box(c + V(0, 0.03, 0.08), (0.004, 0.09, 0.01)), STEEL, 0.004))
    for s in (-1, 1):
        ps.append(P(Ellipsoid(c + V(s * 0.12, 0.1, 0.0), (0.05, 0.03, 0.05)), RUST, 0.01))     # pauldrons
    ps.append(P(Sphere(c + V(0.045, 0.0, 0.075), 0.026), BLACK, 0.004, op='sub'))           # a musket hole clean through
    ribs(ps, c + V(0.045, 0.02, 0.05), 0.025, bone, n=2)
    ps.append(P(Box(c + V(0, -0.08, 0.05), (0.11, 0.02, 0.05), R=rot(0, 0, 0.3), r=0.01), sash, 0.0))
    for k in range(3):
        ps.append(P(Sphere(c + V(0, 0.13 + k * 0.022, 0.0), 0.012), bone, 0.004))
    hc = c + V(0.0, 0.23, 0.02)
    if pose == 'pain':
        hc = hc + V(0.035, -0.01, -0.03)
    ps.append(P(Ellipsoid(hc, (0.06, 0.066, 0.065)), bone, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.035, 0.03), (0.042, 0.035, 0.038)), bone, 0.02))
    for s in (-1, 1):
        ec = hc + V(s * 0.025, 0.0, 0.054)
        ps.append(P(Sphere(ec, 0.021), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.008), 0.009), Mat((1.0, 0.55, 0.15), glow=1.0), 0.0))
    ps.append(P(TriPrism(hc + V(0, -0.024, 0.06), (-0.009, -0.008), (0.009, -0.008), (0, 0.01), 0.02), BLACK, 0.0, op='sub'))
    jo = 0.03 if pose == 'attack' else 0.012
    jaw = hc + V(0, -0.068 - jo, 0.028)
    ps.append(P(Ellipsoid(jaw, (0.038, 0.016, 0.03)), bone, 0.004))
    for i in range(6):
        x = (i - 2.5) * 0.0105
        ps.append(P(Box(hc + V(x, -0.052, 0.058 - abs(x) * 0.25), (0.0042, 0.008, 0.004), r=0.0015), TEETH, 0.0))
    # a scraggly beard still hanging on
    for k in range(5):
        a = -0.5 + k * 0.25
        st = jaw + V(np.sin(a) * 0.03, -0.005, 0.02)
        limb(ps, st, st + V(np.sin(a) * 0.01, -0.06 - 0.01 * (k % 2), 0.0), 0.006, 0.002, Mat((0.25, 0.22, 0.2)), 0.004)
    morion(ps, hc + V(0, 0.02, 0), STEEL if pose != 'pain' else RUST)
    # arms holding an arquebus
    shl, shr = c + V(-0.115, 0.095, 0), c + V(0.115, 0.095, 0)
    if pose == 'attack':
        gun0, gd = c + V(0.03, 0.12, 0.02), norm(V(-0.05, 0.02, 1.0))      # shouldered, aimed at you
    elif pose == 'pain':
        gun0, gd = c + V(0.1, -0.05, 0.05), norm(V(0.7, 0.5, 0.4))
    else:
        gun0, gd = c + V(0.08, -0.04, 0.04), norm(V(-0.55, 0.65, 0.45))   # held across the body
    stock = gun0 - gd * 0.12
    muzzle = gun0 + gd * 0.42
    limb(ps, stock, gun0 + gd * 0.12, 0.018, 0.014, WOOD, 0.004)
    limb(ps, gun0 + gd * 0.05, muzzle, 0.009, 0.009, Mat((0.3, 0.3, 0.32), spec=0.9, shin=40), 0.0)
    ps.append(P(Torus(muzzle, 0.011, 0.004, R=np.stack([norm(np.cross(gd, V(0, 1, 0))), V(0, 1, 0), gd], 1) @ rot(np.pi / 2, 0, 0)), RUST, 0.0))
    hr, hl = gun0 - gd * 0.02, gun0 + gd * 0.2
    # arms: puffed, slashed doublet sleeves down to the elbow, then bare bone and a leather gauntlet cuff; the elbows stick
    # out to the sides so the arms read in the silhouette instead of vanishing behind the gun
    sleeve = cloth((0.46, 0.1, 0.08), seed=99, torn=0.4)
    cuff = Mat((0.24, 0.15, 0.07), var=0.2, vfreq=30, spec=0.3)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.075, -0.07, -0.01)
        ps.append(P(Sphere(sh, 0.036), sleeve, 0.012))
        limb(ps, sh, el, 0.036, 0.027, sleeve, 0.014)
        for k in range(3):                                 # the slashes: yellow lining showing through
            q = sh + (el - sh) * (0.25 + k * 0.25)
            ps.append(P(Sphere(q + V(0, 0, 0.03), 0.009), Mat((0.85, 0.7, 0.2)), 0.004))
        ps.append(P(Sphere(el, 0.022), bone, 0.006))
        limb(ps, el, hd, 0.02, 0.017, bone, 0.006)
        limb(ps, el + (hd - el) * 0.55, el + (hd - el) * 0.88, 0.026, 0.025, cuff, 0.004)
        ps.append(P(Ellipsoid(hd, (0.024, 0.019, 0.024)), bone, 0.006))
    if pose == 'attack':
        ps.append(P(Sphere(muzzle + gd * 0.04, 0.035), fire_mat(seed=96), 0.0, disp=(0.012, 25, 4)))
        ps.append(P(Sphere(muzzle + gd * 0.09 + V(0, 0.02, 0), 0.04), Mat((0.85, 0.85, 0.82), var=0.3, vfreq=20), 0.02, disp=(0.012, 15, 5)))
    return ps


# ------------------------------------------------------------------ THE WEEPING WOMAN

def weeper(pose='walk1'):
    """A drowned bride drifting through the fog, long black hair over her face, wailing."""
    gown = Mat(fn=lambda p, n: np.tile(np.array([0.86, 0.87, 0.9]), (len(p), 1)) * (0.55 + 0.5 * fbm(p, 7, 3, 41))[:, None] *
               (0.6 + 0.4 * np.clip((p[:, 1] - 0.0) / 0.7, 0, 1))[:, None], spec=0.2)
    skin = Mat((0.62, 0.68, 0.74), var=0.12, vfreq=30, spec=0.3)
    ps = []
    sway = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    base = 0.06

    def body_d(p):
        y = p[:, 1]
        t = np.clip((y - base) / 0.58, 0, 1)
        rad = 0.07 + 0.11 * (1 - t) ** 1.6
        ang = np.arctan2(p[:, 2], p[:, 0])
        wav = np.sin(ang * 7 + y * 14 + sway * 1.3) * 0.02 * (1 - t)
        cx = 0.04 * sway * (1 - t) ** 2
        d = np.sqrt((p[:, 0] - cx) ** 2 + (p[:, 2] / 0.75) ** 2) - (rad + wav)
        strands = np.abs(np.sin(ang * 4 + 0.7)) ** 3
        hem = base - 0.08 * strands + 0.05 * (fbm(p * np.array([1, 0, 1]), 11, 2, 7) - 0.5)
        d = np.maximum(d, hem - y)
        d = np.maximum(d, y - 0.66)
        return d * 0.65
    ps.append(P(Func(body_d), gown, 0.0))
    ps.append(P(Ellipsoid(V(0, 0.62, 0), (0.09, 0.06, 0.06)), gown, 0.04))           # shoulders / bodice
    hc = V(0, 0.74, 0.01)
    if pose == 'pain':
        hc = hc + V(0.03, -0.01, -0.04)
    if pose == 'attack':
        hc = hc + V(0, 0.02, -0.03)             # head thrown back to wail
    limb(ps, V(0, 0.64, 0), hc, 0.025, 0.022, skin, 0.01)
    ps.append(P(Ellipsoid(hc, (0.05, 0.062, 0.052)), skin, 0.0))
    # the face: just a gaping black mouth and two pin-prick eyes behind the hair
    mo = 0.04 if pose == 'attack' else 0.014
    ps.append(P(Ellipsoid(hc + V(0, -0.03, 0.045), (0.018, mo, 0.02)), BLACK, 0.003, op='sub'))
    for s in (-1, 1):
        ps.append(P(Sphere(hc + V(s * 0.02, 0.012, 0.046), 0.006), GHOST_EYE, 0.0))
    # long wet black hair hanging over the face and down to the waist
    hair = Mat((0.04, 0.04, 0.05), var=0.3, vfreq=60, spec=0.9, shin=50)
    for k in range(15):
        a = -1.3 + k * (2.6 / 14)
        st = hc + V(np.sin(a) * 0.045, 0.05, np.cos(a) * 0.04 - 0.005)
        if abs(a) < (0.7 if pose == 'attack' else 0.5):        # the hair parts over the face (wide when she screams)
            continue
        ln = 0.26 + 0.06 * ((k * 7) % 3) + (0.08 if abs(a) > 0.8 else 0.0)
        en = st + V(np.sin(a) * 0.03 + sway * 0.015, -ln, np.cos(a) * 0.03 + 0.015)
        mid = (st + en) / 2 + V(0, 0, 0.02 * np.cos(a))
        limb(ps, st, mid, 0.016, 0.012, hair, 0.01)
        limb(ps, mid, en, 0.012, 0.004, hair, 0.006)
    # arms reaching out, long fingers
    rch = 0.12 if pose == 'attack' else 0.0
    sw = {'walk1': 0.03, 'walk2': -0.03}.get(pose, 0.0)
    for s in (-1, 1):
        sh = V(s * 0.09, 0.62, 0.0)
        el = sh + V(s * 0.04, -0.04 + rch * 0.5, 0.12 + rch * 0.3)
        hd = el + V(-s * 0.03, 0.03 + rch * 0.6 + s * sw, 0.15 + rch * 0.4)
        if pose == 'pain':
            hd = el + V(s * 0.08, 0.12, -0.02)
        limb(ps, sh, el, 0.03, 0.022, gown, 0.02)
        limb(ps, el, hd, 0.016, 0.012, skin, 0.008)
        dd = norm(hd - el)
        for f in range(4):
            off = V((f - 1.5) * 0.012, 0, 0)
            limb(ps, hd + off * 0.5, hd + off * 1.2 + dd * 0.07 + V(0, -0.02, 0), 0.004, 0.0015, skin, 0.003)
    # a bouquet of dead marigolds pinned to her bodice, a dark stain spreading under it
    ps.append(P(Ellipsoid(V(0.03, 0.56, 0.06), (0.03, 0.05, 0.01)), Mat((0.2, 0.04, 0.03)), 0.01))
    for k in range(4):
        ps.append(P(Sphere(V(0.02 + (k % 2) * 0.018, 0.6 - (k // 2) * 0.016, 0.07), 0.011), Mat((0.85, 0.42, 0.06), var=0.3, vfreq=40), 0.0))
    # a crown of dead marigolds
    for k in range(7):
        a = -1.2 + k * 0.4
        ps.append(P(Sphere(hc + V(np.sin(a) * 0.05, 0.05, np.cos(a) * 0.035), 0.012), Mat((0.6, 0.35, 0.08), var=0.3, vfreq=40), 0.0))
    return ps


# ------------------------------------------------------------------ BOSS 5: SEVEN DEATH, LORD OF XIBALBA

def seven(pose='walk1', skull=True):
    """Professor Crane after the Jade Skull got him: a giant skeleton king of polished jade, a headdress of quetzal plumes,
    a jaguar-skin cape, an obsidian club, and the Jade Skull itself blazing in his left hand."""
    jb = jade(51)
    ps = []
    S = 1.85
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.42 * S
    lean = 0.04 if pose != 'pain' else -0.06
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.06, 0.42, 0) * S
        knee = hip + V(s * 0.01, -0.2, 0.06 * ls + 0.02) * S
        ank = knee + V(0, -0.19, -0.03 * ls) * S
        limb(ps, hip, knee, 0.022 * S, 0.017 * S, jb, 0.01)
        ps.append(P(Sphere(knee, 0.027 * S), GOLD, 0.01))
        limb(ps, knee, ank, 0.018 * S, 0.014 * S, jb, 0.01)
        ps.append(P(Torus(ank + V(0, 0.02, 0) * S, 0.02 * S, 0.006 * S), GOLD, 0.0))
        for f in range(3):
            o = V(s * 0.004 + (f - 1) * 0.013, -0.012, 0.0) * S
            limb(ps, ank + o * 0.5, ank + o + V(0, -0.002, 0.065) * S, 0.007 * S, 0.004 * S, jb, 0.004)
    ps.append(P(Ellipsoid(V(0, hip_y + 0.02 * S, 0), V(0.08, 0.045, 0.045) * S), jb, 0.01))
    ps.append(P(Box(V(0, hip_y - 0.05 * S, 0.045 * S), V(0.04, 0.06, 0.006) * S, R=rot(0.12, 0, 0), r=0.004), CLOTH_RED, 0.0,
                disp=(0.004, 30, 5)))
    ps.append(P(Torus(V(0, hip_y + 0.01 * S, 0), 0.075 * S, 0.01 * S, R=np.eye(3)), GOLD, 0.0))
    for k in range(7):
        ps.append(P(Sphere(V(0, hip_y + (0.05 + k * 0.032) * S, (-0.015 + lean * k / 7) * S), 0.016 * S), jb, 0.004))
    c = V(0, hip_y + 0.25 * S, lean * S)
    ribs(ps, c + V(0, 0.06, 0.0) * S, 0.11 * S, jb, n=5)
    # a jaguar-skin mantle over the shoulders
    for sd in (-1, 1):
        ps.append(P(Ellipsoid(c + V(sd * 0.1, 0.11, -0.03) * S, V(0.06, 0.035, 0.06) * S, R=rot(0, 0, -sd * 0.35)), pelt(53), 0.02))
    ps.append(P(Ellipsoid(c + V(0, 0.08, -0.07) * S, V(0.13, 0.07, 0.025) * S), pelt(53), 0.03, disp=(0.006, 12, 3)))
    # gold sun pectoral with jade centre
    ps.append(P(Cyl(c + V(0, 0.06, 0.07) * S, 0.055 * S, 0.008 * S, R=rot(np.pi / 2, 0, 0)), GOLD, 0.0))
    ps.append(P(Cyl(c + V(0, 0.06, 0.08) * S, 0.03 * S, 0.006 * S, R=rot(np.pi / 2, 0, 0)), EYE_JADE, 0.0))
    for s in (-1, 1):
        limb(ps, c + V(0, 0.1, 0.04) * S, c + V(s * 0.12, 0.1, 0.0) * S, 0.011 * S, 0.01 * S, jb, 0.004)
    for k in range(3):
        ps.append(P(Sphere(c + V(0, 0.13 + k * 0.022, 0.0) * S, 0.014 * S), jb, 0.004))
    hc = c + V(0.0, 0.24, 0.02) * S
    if pose == 'pain':
        hc = hc + V(0.035, -0.01, -0.04) * S
    ps.append(P(Ellipsoid(hc, V(0.066, 0.07, 0.07) * S), jb, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.035, 0.03) * S, V(0.044, 0.036, 0.04) * S), jb, 0.02))
    for s in (-1, 1):
        ec = hc + V(s * 0.027, 0.0, 0.057) * S
        ps.append(P(Sphere(ec, 0.023 * S), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.008) * S, 0.012 * S), EYE_JADE, 0.0))
        ps.append(P(Cyl(hc + V(s * 0.07, -0.01, 0.0) * S, 0.022 * S, 0.006 * S, R=rot(0, 0, np.pi / 2)), GOLD, 0.0))   # ear spools
    ps.append(P(TriPrism(hc + V(0, -0.024, 0.064) * S, (-0.01 * S, -0.009 * S), (0.01 * S, -0.009 * S), (0, 0.011 * S), 0.02 * S), BLACK, 0.0, op='sub'))
    jo = 0.05 if pose == 'attack' else 0.014
    jaw = hc + V(0, -0.07 - jo, 0.028) * S
    ps.append(P(Ellipsoid(jaw, V(0.04, 0.017, 0.031) * S), jb, 0.004))
    for i in range(6):
        x = (i - 2.5) * 0.0105
        ps.append(P(Box(hc + V(x, -0.054, 0.06 - abs(x) * 0.25) * S, V(0.0042, 0.008, 0.004) * S, r=0.0015), GOLD, 0.0))
        ps.append(P(Box(jaw + V(x * 0.95, 0.013, 0.025 - abs(x) * 0.25) * S, V(0.004, 0.007, 0.004) * S, r=0.0015), GOLD, 0.0))
    # headdress: gold band and a great fan of quetzal plumes
    ps.append(P(Torus(hc + V(0, 0.045, 0) * S, 0.066 * S, 0.012 * S, R=np.eye(3)), GOLD, 0.0))
    ps.append(P(Cyl(hc + V(0, 0.07, 0.06) * S, 0.022 * S, 0.006 * S, R=rot(np.pi / 2, 0, 0)), EYE_JADE, 0.0))
    for k in range(11):
        a = -1.3 + k * 0.26
        b = hc + V(np.sin(a) * 0.05, 0.07, -0.03) * S
        t = hc + V(np.sin(a) * 0.24, 0.15 + 0.07 * np.cos(a), -0.1) * S
        feather(ps, b, t, 0.022 * S, FEATHER_G, [FEATHER_R, FEATHER_B, GOLD][k % 3])
    # arms: obsidian club in the right hand, the Jade Skull in the left
    shl, shr = c + V(-0.125, 0.095, 0) * S, c + V(0.125, 0.095, 0) * S
    if pose == 'attack':
        el_l, hl = shl + V(-0.08, 0.1, 0.06) * S, shl + V(-0.04, 0.28, 0.1) * S
        el_r, hr = shr + V(0.08, 0.1, 0.04) * S, shr + V(0.06, 0.28, 0.1) * S
        cd, cu = V(0.3, 0.9, -0.2), V(1, 0, 0)
    elif pose == 'pain':
        el_l, hl = shl + V(-0.09, -0.06, 0.03) * S, shl + V(-0.16, 0.06, 0.06) * S
        el_r, hr = shr + V(0.08, -0.08, 0.03) * S, shr + V(0.15, 0.04, 0.08) * S
        cd, cu = V(0.7, 0.5, 0.2), V(0, 1, 0)
    else:
        a = 0.04 * sw
        el_l, hl = shl + V(-0.04, -0.1, 0.06 + a) * S, shl + V(0.02, -0.08, 0.2 + a) * S
        el_r, hr = shr + V(0.03, -0.11, 0.06 - a) * S, shr + V(0.02, -0.14, 0.18 - a) * S
        cd, cu = V(0.2, 0.3, 1.0), V(0, 1, 0)
    for sh, el, hd in ((shl, el_l, hl), (shr, el_r, hr)):
        ps.append(P(Sphere(sh, 0.026 * S), GOLD, 0.006))
        limb(ps, sh, el, 0.016 * S, 0.013 * S, jb, 0.006)
        ps.append(P(Sphere(el, 0.019 * S), jb, 0.004))
        limb(ps, el, hd, 0.013 * S, 0.011 * S, jb, 0.006)
        ps.append(P(Torus(el + (hd - el) * 0.75, 0.017 * S, 0.006 * S, R=rot(np.pi / 2, 0, 0)), GOLD, 0.0))
        ps.append(P(Sphere(hd, 0.016 * S), jb, 0.004))
    macuahuitl(ps, hr, cd, cu, 0.32 * S)
    if skull:
        sk = hl + V(0, 0.06, 0.02) * S
        ps.append(P(Ellipsoid(sk, V(0.04, 0.042, 0.042) * S), EYE_JADE, 0.0))
        for s in (-1, 1):
            ps.append(P(Sphere(sk + V(s * 0.016, 0.004, 0.034) * S, 0.012 * S), BLACK, 0.002, op='sub'))
        ps.append(P(Box(sk + V(0, -0.025, 0.03) * S, V(0.02, 0.006, 0.01) * S), BLACK, 0.0, op='sub'))
        if pose == 'attack':
            ps.append(P(Sphere(sk + V(0, 0.02, 0.02) * S, 0.07 * S), JADEFIRE, 0.0, disp=(0.02, 18, 9)))
    return ps


# ------------------------------------------------------------------ projectiles

def dart(seed=0):
    """A blowgun dart with a red feather tuft (flying left to right)."""
    ps = [P(Cone(V(-0.07, 0.05, 0), V(0.06, 0.05, 0), 0.004, 0.0015), WOOD, 0.0),
          P(Cone(V(0.05, 0.05, 0), V(0.075, 0.05, 0), 0.003, 0.0005), STEEL, 0.0)]
    for k in range(5):
        a = k * 1.25 + seed * 0.6
        ps.append(P(Cone(V(-0.07, 0.05, 0), V(-0.1, 0.05 + np.sin(a) * 0.014, np.cos(a) * 0.014), 0.006, 0.002), FEATHER_R, 0.0))
    return ps


def shot(seed=0):
    """A musket ball trailing smoke and sparks."""
    smoke = Mat((0.8, 0.8, 0.78), var=0.3, vfreq=20)
    ps = [P(Sphere(V(0, 0.05, 0), 0.016), Mat((0.25, 0.25, 0.27), spec=1.0, shin=50), 0.0),
          P(Sphere(V(0, 0.05, 0), 0.026), fire_mat(seed=97 + seed), 0.0, disp=(0.008, 30, 2 + seed))]
    for k in range(3):
        ps.append(P(Sphere(V(-0.03 - k * 0.025, 0.05 + 0.008 * np.sin(k + seed), 0), 0.014 + k * 0.005), smoke, 0.01))
    return ps


def disc(seed=0):
    """A spinning obsidian disc rimmed with jade fire."""
    a = seed * 0.6
    R = rot(np.pi / 2 - 0.5, a, 0)
    ps = [P(Cyl(V(0, 0.06, 0), 0.05, 0.007, R=R), OBSIDIAN, 0.0),
          P(Torus(V(0, 0.06, 0), 0.05, 0.009, R=R @ rot(np.pi / 2, 0, 0)), JADEFIRE, 0.0, disp=(0.006, 30, 4 + seed))]
    for k in range(6):
        b = k * np.pi / 3 + a
        ps.append(P(Cone(V(np.cos(b) * 0.05, 0.06 + np.sin(b) * 0.05 * 0.45, 0), V(np.cos(b) * 0.07, 0.06 + np.sin(b) * 0.07 * 0.45, 0),
                         0.01, 0.001), OBSIDIAN, 0.0))
    return ps


def rock(seed=0):
    m = Mat((0.42, 0.38, 0.32), var=0.4, vfreq=12, seed=seed)
    return [P(Sphere(V(0, 0.07, 0), 0.06), m, 0.0, disp=(0.02, 9, 3 + seed))]


# ------------------------------------------------------------------ death frames

def mummy_fall():
    return tilt_scene(mummy('pain'), ang_z=0.55, shift=(0.05, -0.02, 0))


def mummy_dead():
    dust = Mat((0.5, 0.44, 0.32), var=0.3, vfreq=12)
    ps = [P(Ellipsoid((0.0, -0.004, 0.02), (0.32, 0.014, 0.14)), dust, 0.0)]
    return ps + tilt_scene(mummy('pain'), ang_z=1.5, shift=(0.38, 0.06, 0))


def jaguar_fall():
    return tilt_scene(jaguar('pain'), ang_z=0.6, shift=(0.06, -0.03, 0))


def jaguar_dead():
    ps = [P(Ellipsoid((0.0, -0.005, 0.02), (0.34, 0.012, 0.15)), BLOOD, 0.0)]
    return ps + tilt_scene(jaguar('pain'), ang_z=1.5, shift=(0.4, 0.06, 0))


def conq_fall():
    return tilt_scene(conq('pain'), ang_z=0.6, shift=(0.05, -0.02, 0))


def conq_dead():
    """A heap of bones under a dented helmet."""
    bone = OLD_BONE
    ps = []
    rs = np.random.RandomState(3)
    for k in range(14):
        a = V(rs.uniform(-0.2, 0.2), 0.012, rs.uniform(-0.08, 0.08))
        b = a + V(rs.uniform(-0.12, 0.12), 0.0, rs.uniform(-0.05, 0.05))
        limb(ps, a, b, 0.011, 0.009, bone, 0.0)
    sc = V(-0.06, 0.05, 0.05)
    ps.append(P(Ellipsoid(sc, (0.055, 0.055, 0.055)), bone, 0.0))
    for s in (-1, 1):
        ps.append(P(Sphere(sc + V(s * 0.022, 0.0, 0.046), 0.017), BLACK, 0.004, op='sub'))
    morion(ps, V(0.1, 0.0, 0.0), RUST)
    limb(ps, V(-0.25, 0.012, -0.05), V(0.15, 0.012, -0.08), 0.009, 0.009, Mat((0.3, 0.3, 0.32), spec=0.9), 0.0)   # the musket
    return ps


def weeper_fall():
    return tilt_scene(weeper('pain'), 0.0, 0.0, shift=(0, -0.2, 0))


def weeper_dead():
    """She sinks away, leaving a sodden gown, a tangle of hair and a puddle of black water."""
    gown = Mat((0.7, 0.72, 0.76), var=0.4, vfreq=7)
    ps = [P(Ellipsoid((0, -0.003, 0), (0.3, 0.012, 0.16)), Mat((0.05, 0.07, 0.08), spec=1.4, shin=60), 0.0)]
    ps.append(P(Ellipsoid((-0.02, 0.025, 0), (0.18, 0.03, 0.1)), gown, 0.04, disp=(0.012, 9, 3)))
    hair = Mat((0.04, 0.04, 0.05), var=0.3, vfreq=60, spec=0.9, shin=50)
    for k in range(8):
        a = k * 0.8
        limb(ps, V(0.08, 0.03, 0.0), V(0.08 + np.cos(a) * 0.12, 0.012, np.sin(a) * 0.06), 0.01, 0.004, hair, 0.004)
    for k in range(5):
        ps.append(P(Sphere(V(-0.1 + k * 0.05, 0.015, 0.06 * ((k % 2) * 2 - 1)), 0.012), Mat((0.6, 0.35, 0.08)), 0.0))
    return ps


def seven_fall():
    return tilt_scene(seven('pain'), ang_z=0.35, shift=(0.1, -0.06, 0))


def seven_dead():
    """The lord of Xibalba in pieces: a heap of jade bones, the plumes, the club, and the Jade Skull rolled free."""
    jb = jade(51)
    ps = []
    rs = np.random.RandomState(7)
    for k in range(22):
        a = V(rs.uniform(-0.55, 0.55), 0.02, rs.uniform(-0.2, 0.2))
        b = a + V(rs.uniform(-0.2, 0.2), 0.0, rs.uniform(-0.08, 0.08))
        limb(ps, a, b, 0.022, 0.018, jb, 0.0)
    sc = V(-0.2, 0.1, 0.08)
    ps.append(P(Ellipsoid(sc, (0.13, 0.13, 0.13)), jb, 0.0))
    for s in (-1, 1):
        ps.append(P(Sphere(sc + V(s * 0.05, 0.0, 0.11), 0.04), BLACK, 0.004, op='sub'))
    for k in range(7):
        a = -1.0 + k * 0.33
        feather(ps, V(0.15, 0.03, -0.05), V(0.15 + np.sin(a) * 0.35, 0.02, -0.1 + np.cos(a) * 0.1), 0.04, FEATHER_G,
                [FEATHER_R, FEATHER_B][k % 2])
    ps.append(P(Ellipsoid(V(0.45, 0.07, 0.12), (0.07, 0.072, 0.072)), Mat((0.4, 1.0, 0.6), glow=1.0), 0.0))
    return ps
