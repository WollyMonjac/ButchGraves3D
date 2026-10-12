"""SDF models for episodes 2 and 3. Feet at y=0, facing +z (toward camera). 1 unit = wall height."""
import numpy as np
from sdf import *
from monsters import (limb, ribs, cloth, tilt_scene, TriPrism, fire_mat, BONE, TEETH, MOUTH, BLOOD, EYE_RED, EYE_GRN,
                      EYE_YEL, BLACK, FIREBALL)

V = lambda *a: np.array(a, float)

# ------------------------------------------------------------------ shared materials
OLD_BONE = Mat(fn=lambda p, n: np.tile(np.array([0.84, 0.79, 0.64]), (len(p), 1)) *
               (0.72 + 0.4 * fbm(p, 22, 3, 71))[:, None] * (1 - 0.35 * (fbm(p, 9, 2, 72) > 0.62))[:, None], spec=0.25, shin=20)
RUST = Mat(fn=lambda p, n: np.where((fbm(p, 30, 2, 73) > 0.5)[:, None], np.array([[0.48, 0.24, 0.1]]), np.array([[0.4, 0.4, 0.42]])) *
           (0.7 + 0.5 * fbm(p, 60, 2, 74))[:, None], spec=0.6, shin=30)
EYE_ICE = Mat((0.45, 0.85, 1.0), glow=1.0)
EYE_BLOOD = Mat((1.0, 0.1, 0.05), glow=1.0)
FANG = Mat((0.95, 0.93, 0.85), spec=0.8, shin=50)
GLOSS_RED = Mat((0.85, 0.05, 0.04), spec=1.0, shin=60)
GLOVE_W = Mat((0.92, 0.9, 0.86), var=0.08, vfreq=30, spec=0.3)
STEEL = Mat(fn=lambda p, n: np.tile(np.array([0.62, 0.64, 0.7]), (len(p), 1)) * (0.65 + 0.5 * np.clip(n[:, 1] * 0.5 + 0.6, 0, 1))[:, None],
            spec=1.3, shin=45)
GOLD = Mat((0.9, 0.68, 0.2), var=0.12, vfreq=30, spec=1.0, shin=40)
BLOODFIRE = fire_mat((1.0, 0.75, 0.7), (1.0, 0.15, 0.1), (0.45, 0.0, 0.02), seed=5)


def knife_prims(ps, base, d, up, length=0.12, w=0.016):
    """Kitchen knife from base (handle end) along d."""
    d = norm(d); up = norm(up)
    side = norm(np.cross(d, up))
    h1 = base + d * 0.045
    limb(ps, base, h1, 0.009, 0.009, Mat((0.12, 0.08, 0.06), spec=0.3), 0.0)
    tip = h1 + d * length
    # blade: thin box from h1 to tip, tapering via a cone
    R = np.stack([side, up, d], 1)
    ps.append(P(Box((h1 + tip) / 2 + up * w * 0.3, (0.003, w, length / 2), R=R, r=0.002), STEEL, 0.0))
    ps.append(P(Cone(tip - d * 0.02 + up * w * 0.3, tip, 0.012, 0.001), STEEL, 0.006))


# ------------------------------------------------------------------ SKELETON (Bonehead)

def skeleton(pose='walk1'):
    bone = OLD_BONE
    rag = cloth((0.3, 0.22, 0.14), seed=61, torn=0.62)
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
        ps.append(P(Sphere(knee + V(0, 0.002, 0.016), 0.014), bone, 0.004))     # kneecap
        limb(ps, knee, ank, 0.014, 0.011, bone, 0.01)
        ps.append(P(Sphere(ank, 0.016), bone, 0.006))
        for f in range(3):
            o = V(s * 0.004 + (f - 1) * 0.011, -0.012, 0.0)
            limb(ps, ank + o * 0.5 + V(0, -0.002, 0.0), ank + o + V(0, -0.002, 0.06), 0.006, 0.004, bone, 0.004)
    # pelvis
    ps.append(P(Ellipsoid(V(0, hip_y + 0.02, 0), (0.075, 0.042, 0.04)), bone, 0.01))
    ps.append(P(Ellipsoid(V(0, hip_y + 0.0, 0.03), (0.032, 0.03, 0.06)), BLACK, 0.006, op='sub'))
    # rag loincloth
    ps.append(P(Box(V(0, hip_y - 0.035, 0.04), (0.05, 0.05, 0.006), R=rot(0.12, 0, 0), r=0.004), rag, 0.0, disp=(0.004, 30, 3)))
    # spine
    for k in range(7):
        ps.append(P(Sphere(V(0, hip_y + 0.05 + k * 0.032, -0.015 + lean * k / 7), 0.014), bone, 0.004))
    c = V(0, hip_y + 0.25, lean)
    ps.append(P(Box(c + V(0, -0.01, 0.06), (0.009, 0.06, 0.006), r=0.004), bone, 0.004))
    ribs(ps, c + V(0, 0.06, 0.0), 0.1, bone, n=5)
    for s in (-1, 1):
        limb(ps, c + V(0, 0.1, 0.04), c + V(s * 0.11, 0.1, 0.0), 0.009, 0.008, bone, 0.004)       # clavicle
        ps.append(P(Ellipsoid(c + V(s * 0.085, 0.07, -0.03), (0.04, 0.05, 0.012), R=rot(0, 0, s * 0.3)), bone, 0.004))  # scapula
    # neck + skull
    for k in range(3):
        ps.append(P(Sphere(c + V(0, 0.13 + k * 0.022, 0.0), 0.012), bone, 0.004))
    hc = c + V(0.0, 0.23, 0.02)
    if pose == 'pain':
        hc = hc + V(0.035, -0.01, -0.03)
    ps.append(P(Ellipsoid(hc, (0.064, 0.069, 0.068)), bone, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.035, 0.03), (0.042, 0.035, 0.038)), bone, 0.02))
    for s in (-1, 1):
        ec = hc + V(s * 0.026, 0.0, 0.056)
        ps.append(P(Sphere(ec, 0.022), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.008), 0.0095), EYE_ICE, 0.0))
        ps.append(P(Ellipsoid(hc + V(s * 0.045, -0.02, 0.03), (0.012, 0.012, 0.02)), bone, 0.006))   # cheekbones
    ps.append(P(TriPrism(hc + V(0, -0.024, 0.063), (-0.009, -0.008), (0.009, -0.008), (0, 0.01), 0.02), BLACK, 0.0, op='sub'))
    # crack across the cranium
    ps.append(P(Box(hc + V(-0.02, 0.04, 0.04), (0.002, 0.025, 0.03), R=rot(0.3, 0, 0.6)), BLACK, 0.0, op='sub'))
    jo = 0.045 if pose == 'attack' else 0.012
    jaw = hc + V(0, -0.07 - jo, 0.028)
    ps.append(P(Ellipsoid(jaw, (0.038, 0.016, 0.03)), bone, 0.004))
    for i in range(6):
        x = (i - 2.5) * 0.0105
        ps.append(P(Box(hc + V(x, -0.054, 0.06 - abs(x) * 0.25), (0.0042, 0.008, 0.004), r=0.0015), TEETH, 0.0))
        ps.append(P(Box(jaw + V(x * 0.95, 0.013, 0.025 - abs(x) * 0.25), (0.004, 0.007, 0.004), r=0.0015), TEETH, 0.0))
    # arms
    shl, shr = c + V(-0.115, 0.095, 0), c + V(0.115, 0.095, 0)
    if pose == 'attack':
        el_l, hl = shl + V(-0.07, -0.08, 0.09), shl + V(-0.02, -0.06, 0.2)
        el_r, hr = shr + V(0.08, 0.12, 0.02), shr + V(0.02, 0.27, 0.06)
    elif pose == 'pain':
        el_l, hl = shl + V(-0.09, -0.06, 0.03), shl + V(-0.15, 0.06, 0.06)
        el_r, hr = shr + V(0.08, -0.08, 0.03), shr + V(0.14, 0.05, 0.08)
    else:
        a = 0.04 * sw
        el_l, hl = shl + V(-0.02, -0.12, 0.04 + a), shl + V(0.0, -0.22, 0.1 + a)
        el_r, hr = shr + V(0.03, -0.11, 0.06 - a), shr + V(0.02, -0.12, 0.2 - a)
    for sh, el, hd in ((shl, el_l, hl), (shr, el_r, hr)):
        ps.append(P(Sphere(sh, 0.02), bone, 0.006))
        limb(ps, sh, el, 0.013, 0.011, bone, 0.006)
        ps.append(P(Sphere(el, 0.016), bone, 0.004))
        limb(ps, el, hd, 0.011, 0.009, bone, 0.006)
        d = norm(hd - el)
        ps.append(P(Sphere(hd, 0.013), bone, 0.004))
        for f in range(4):
            off = V((f - 1.5) * 0.008, 0, 0)
            limb(ps, hd + off, hd + off * 1.4 + d * 0.045 + V(0, -0.012, 0), 0.0045, 0.003, bone, 0.002)
    # rusty cutlass in the right hand
    if pose == 'attack':
        d, up = V(-0.25, 1.0, -0.15), V(0, 0, 1)
    elif pose == 'pain':
        d, up = V(0.6, 0.6, 0.2), V(0, 0, 1)
    else:
        d, up = V(0.15, 0.25, 1.0), V(0, 1, 0)
    d = norm(d)
    side = norm(np.cross(d, norm(up)))
    up2 = norm(np.cross(side, d))
    limb(ps, hr - d * 0.02, hr + d * 0.04, 0.009, 0.009, Mat((0.2, 0.12, 0.06)), 0.0)
    ps.append(P(Box(hr + d * 0.045, (0.03, 0.006, 0.006), R=np.stack([side, up2, d], 1)), RUST, 0.0))
    blade_c = hr + d * 0.2
    ps.append(P(Box(blade_c + up2 * 0.008, (0.004, 0.022, 0.16), R=np.stack([side, up2, d], 1), r=0.002), STEEL, 0.0))
    ps.append(P(Box(blade_c + up2 * 0.012 + side * 0.002, (0.004, 0.012, 0.1), R=np.stack([side, up2, d], 1), r=0.002), RUST, 0.0))
    ps.append(P(Sphere(hr + d * 0.36 + up2 * 0.012, 0.016), RUST, 0.012))
    return ps


# ------------------------------------------------------------------ CLOWN

def clown_skin():
    """White greasepaint with a red painted grin and blue diamonds over the eyes (world coords; head at hc)."""
    return Mat((0.95, 0.94, 0.9), var=0.05, vfreq=40, spec=0.35, shin=30)


def polka(base, dot, dot2, cell=0.058, r=0.013, seed=0):
    base, dot, dot2 = np.asarray(base), np.asarray(dot), np.asarray(dot2)

    def fn(p, n):
        q = p / cell
        ci = np.floor(q[:, 0] + 0.5 * np.floor(q[:, 1]))
        cj = np.floor(q[:, 1])
        fx = q[:, 0] + 0.5 * np.floor(q[:, 1]) - ci - 0.5
        fy = q[:, 1] - cj - 0.5
        d = np.sqrt(fx * fx + fy * fy) * cell
        alt = ((ci + cj) % 2) == 0
        c = np.tile(base, (len(p), 1))
        m = d < r
        c[m & alt] = dot
        c[m & ~alt] = dot2
        dirt = fbm(p, 9, 3, seed + 3)
        c = c * (0.6 + 0.45 * dirt)[:, None]
        b = fbm(p, 7, 3, seed + 9)
        bm = np.clip((b - 0.53) * 9, 0, 1)[:, None]
        return c * (1 - bm) + np.array([0.35, 0.02, 0.02])[None, :] * bm
    return Mat(fn=fn, spec=0.2)


def clown(pose='walk1'):
    suit = polka((0.72, 0.66, 0.48), (0.7, 0.06, 0.05), (0.12, 0.18, 0.55), seed=81)
    skin = clown_skin()
    paint = Mat((0.8, 0.03, 0.04), spec=0.6, shin=40)
    blue = Mat((0.15, 0.3, 0.85), spec=0.5)
    hair = Mat((0.95, 0.35, 0.05), var=0.35, vfreq=50)
    shoe = Mat((0.75, 0.06, 0.05), spec=0.8, shin=40)
    ruffm = Mat((0.95, 0.94, 0.92), var=0.1, vfreq=30)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.4
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.06, hip_y, 0)
        knee = hip + V(s * 0.012, -0.19, 0.05 * ls + 0.02)
        ank = knee + V(0, -0.17, -0.03 * ls)
        limb(ps, hip, knee, 0.06, 0.05, suit, 0.03)
        limb(ps, knee, ank, 0.05, 0.045, suit, 0.03)
        ps.append(P(Cyl(ank + V(0, 0.01, 0), 0.05, 0.012), ruffm, 0.01))
        # giant shoes
        ps.append(P(Ellipsoid(ank + V(s * 0.01, -0.025, 0.07), (0.05, 0.03, 0.11)), shoe, 0.02))
    # baggy body
    ps.append(P(Ellipsoid(V(0, hip_y + 0.08, 0.0), (0.14, 0.12, 0.1)), suit, 0.05))
    ps.append(P(Ellipsoid(V(0, hip_y + 0.24, 0.0), (0.12, 0.1, 0.08)), suit, 0.06))
    for k in range(3):
        ps.append(P(Sphere(V(0, hip_y + 0.13 + k * 0.07, 0.093 - k * 0.006), 0.018), Mat((0.95, 0.85, 0.2), spec=0.6), 0.004))
    # ruff collar
    rc = V(0, hip_y + 0.34, 0.0)
    for k in range(12):
        a = k * 2 * np.pi / 12
        ps.append(P(Ellipsoid(rc + V(np.cos(a) * 0.075, 0.0, np.sin(a) * 0.06), (0.04, 0.02, 0.035), R=rot(0, -a, 0)), ruffm, 0.01))
    # head
    hc = V(0, hip_y + 0.43, 0.02)
    if pose == 'pain':
        hc = hc + V(0.035, -0.01, -0.03)
    ps.append(P(Ellipsoid(hc, (0.07, 0.078, 0.07)), skin, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.04, 0.03), (0.055, 0.04, 0.045)), skin, 0.02))
    # blue diamonds over the eyes, dark sockets, yellow pupils
    for s in (-1, 1):
        ec = hc + V(s * 0.028, 0.01, 0.062)
        ps.append(P(Box(ec + V(0, 0.004, -0.002), (0.013, 0.024, 0.006), R=rot(0, 0, s * 0.25)), BLACK, 0.002))
        ps.append(P(Sphere(ec + V(0, 0, 0.004), 0.015), BLACK, 0.003, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.003), 0.0085), EYE_YEL, 0.0))
        ps.append(P(Box(hc + V(s * 0.03, 0.04, 0.06), (0.014, 0.0035, 0.004), R=rot(0, 0, -s * 0.35)), BLACK, 0.002))  # angry brows
    # red nose
    ps.append(P(Sphere(hc + V(0, -0.012, 0.08), 0.022), GLOSS_RED, 0.0))
    # painted red grin + open mouth with sharp teeth
    mo = 0.034 if pose == 'attack' else 0.021
    mcen = hc + V(0, -0.052, 0.066)
    ps.append(P(Ellipsoid(mcen + V(0, 0, -0.004), (0.05, 0.018 + mo * 0.5, 0.012)), paint, 0.004))
    for s in (-1, 1):
        ps.append(P(Cone(mcen + V(s * 0.04, 0.0, -0.002), mcen + V(s * 0.06, 0.05, -0.012), 0.009, 0.003), paint, 0.004))
        ps.append(P(Cone(mcen + V(s * 0.045, -0.005, -0.004), mcen + V(s * 0.05, -0.03, -0.006), 0.005, 0.002), paint, 0.003))
    ps.append(P(Ellipsoid(mcen + V(0, 0, 0.004), (0.038, mo, 0.02)), MOUTH, 0.003, op='sub'))
    for i in range(7):
        x = (i - 3) * 0.0105
        ps.append(P(Cone(mcen + V(x, mo * 0.9, 0.0), mcen + V(x, mo * 0.9 - 0.012, 0.002), 0.004, 0.0005), FANG, 0.0))
        ps.append(P(Cone(mcen + V(x, -mo * 0.9, 0.0), mcen + V(x, -mo * 0.9 + 0.011, 0.002), 0.004, 0.0005), FANG, 0.0))
    # bald top, wild tufts of hair at the sides
    for s in (-1, 1):
        for k in range(6):
            a = k * 0.8
            c = hc + V(s * (0.07 + 0.02 * np.cos(a)), 0.015 + 0.03 * np.sin(a), -0.01 + 0.02 * np.sin(a * 1.7))
            ps.append(P(Sphere(c, 0.032), hair, 0.025, disp=(0.008, 30, 7 + k)))
    # arms
    shl, shr = V(-0.13, hip_y + 0.3, 0), V(0.13, hip_y + 0.3, 0)
    if pose == 'attack':
        hl = shl + V(-0.08, -0.06, 0.14); hr = shr + V(0.1, 0.2, -0.06)
    elif pose == 'pain':
        hl = shl + V(-0.12, 0.05, 0.05); hr = shr + V(0.12, 0.04, 0.05)
    else:
        hl = shl + V(-0.05, -0.12 - 0.02 * sw, 0.1); hr = shr + V(0.04, -0.16 + 0.02 * sw, 0.14)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.04, -0.03, -0.02)
        limb(ps, sh, el, 0.045, 0.04, suit, 0.03)
        limb(ps, el, hd, 0.04, 0.035, suit, 0.02)
        ps.append(P(Cyl(hd - norm(hd - el) * 0.01, 0.04, 0.01, R=rot(np.pi / 2, 0, 0)), ruffm, 0.01))
        ps.append(P(Sphere(hd + norm(hd - el) * 0.025, 0.03), GLOVE_W, 0.01))
    # knife in the right hand
    if pose == 'attack':
        knife_prims(ps, hr + V(0, 0.03, 0), V(0.2, 1.0, 0.1), V(0, 0, 1))
    else:
        knife_prims(ps, hr + V(0, 0.0, 0.03), V(0.1, -0.6, 0.8), V(0, 1, 0))
    # red balloon on a string from the left hand
    if pose != 'pain':
        bc = hl + V(-0.04, 0.42, -0.04)
        limb(ps, hl + V(0, 0.02, 0), bc + V(0, -0.075, 0), 0.0025, 0.0025, Mat((0.9, 0.9, 0.9)), 0.0)
        ps.append(P(Ellipsoid(bc, (0.065, 0.075, 0.065)), GLOSS_RED, 0.0))
        ps.append(P(Cone(bc + V(0, -0.075, 0), bc + V(0, -0.09, 0), 0.006, 0.012), GLOSS_RED, 0.004))
    return ps


# ------------------------------------------------------------------ WEREWOLF

def fur_mat(base=(0.3, 0.25, 0.2), seed=91):
    base = np.asarray(base)

    def fn(p, n):
        v = fbm(p * V(1, 3, 1), 30, 3, seed)
        c = base[None, :] * (0.55 + 0.75 * v)[:, None]
        grey = np.clip((fbm(p, 6, 2, seed + 5) - 0.5) * 3, 0, 1)[:, None]
        c = c * (1 - grey * 0.5) + np.array([0.35, 0.33, 0.32]) * grey * 0.5
        return c
    return Mat(fn=fn, spec=0.15, shin=12)


def werewolf(pose='walk1'):
    fur = fur_mat()
    belly = fur_mat((0.5, 0.46, 0.4), 93)
    hide = Mat((0.18, 0.15, 0.14), var=0.25, vfreq=30, spec=0.3)
    nose = Mat((0.04, 0.03, 0.03), spec=1.0, shin=50)
    claw = Mat((0.2, 0.18, 0.15), spec=0.6)
    denim = cloth((0.2, 0.25, 0.38), seed=95, torn=0.55)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    FD = (0.008, 70, 3)       # fur displacement
    hip_y = 0.43
    lunge = 0.08 if pose == 'attack' else 0.0
    # digitigrade legs
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.08, hip_y, 0)
        knee = hip + V(s * 0.02, -0.15, 0.1 + 0.05 * ls)
        hock = knee + V(0, -0.15, -0.09 - 0.03 * ls)
        paw = hock + V(0, -0.12, 0.05)
        limb(ps, hip, knee, 0.075, 0.055, fur, 0.04, disp=FD)
        limb(ps, knee, hock, 0.05, 0.03, fur, 0.03, disp=FD)
        limb(ps, hock, paw, 0.03, 0.028, fur, 0.02, disp=FD)
        ps.append(P(Ellipsoid(paw + V(0, -0.005, 0.03), (0.04, 0.02, 0.055)), hide, 0.02))
        for f in range(3):
            o = V((f - 1) * 0.022, -0.01, 0.075)
            limb(ps, paw + o * 0.6, paw + o + V(0, -0.01, 0.025), 0.007, 0.002, claw, 0.004)
    # torn shorts
    ps.append(P(Ellipsoid(V(0, hip_y + 0.02, 0), (0.15, 0.08, 0.1)), denim, 0.04))
    # massive hunched torso
    ch = V(0, hip_y + 0.27, 0.06 + lunge)
    ps.append(P(Ellipsoid(V(0, hip_y + 0.12, 0.02 + lunge * 0.5), (0.13, 0.11, 0.1)), fur, 0.06, disp=FD))
    ps.append(P(Ellipsoid(ch, (0.19, 0.13, 0.13)), fur, 0.08, disp=FD))
    ps.append(P(Ellipsoid(ch + V(0, -0.03, 0.08), (0.12, 0.09, 0.06)), belly, 0.05, disp=FD))
    # hump of shoulders
    ps.append(P(Ellipsoid(ch + V(0, 0.08, -0.06), (0.2, 0.09, 0.1)), fur, 0.07, disp=FD))
    # head
    hc = ch + V(0, 0.14, 0.08 + lunge * 0.5)
    if pose == 'pain':
        hc = hc + V(0.05, 0.03, -0.06)
    limb(ps, ch + V(0, 0.06, 0.0), hc, 0.07, 0.06, fur, 0.05, disp=FD)
    ps.append(P(Ellipsoid(hc, (0.085, 0.075, 0.08)), fur, 0.02, disp=FD))
    for s in (-1, 1):       # shaggy cheek ruff widens the face
        ps.append(P(Ellipsoid(hc + V(s * 0.075, -0.035, 0.0), (0.045, 0.05, 0.05)), belly, 0.03, disp=(0.01, 50, 7)))
    # long snout angled down toward the viewer
    sn0, sn1 = hc + V(0, -0.02, 0.06), hc + V(0, -0.075, 0.15)
    limb(ps, sn0, sn1, 0.045, 0.03, fur, 0.03, disp=(0.004, 70, 4))
    ps.append(P(Ellipsoid(sn1 + V(0, 0.012, 0.012), (0.022, 0.016, 0.014)), nose, 0.006))
    for s in (-1, 1):
        e0 = hc + V(s * 0.055, 0.05, -0.02)
        limb(ps, e0, e0 + V(s * 0.045, 0.11, -0.01), 0.032, 0.004, fur, 0.01)
        ps.append(P(Cone(e0 + V(0, 0.01, 0.02), e0 + V(s * 0.04, 0.09, 0.012), 0.018, 0.003), Mat((0.35, 0.2, 0.2)), 0.004))
        ec = hc + V(s * 0.035, 0.012, 0.068)
        ps.append(P(Sphere(ec, 0.015), BLACK, 0.003, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.002), 0.011), EYE_YEL, 0.0))
        ps.append(P(Box(ec + V(0, 0.02, 0.004), (0.024, 0.008, 0.012), R=rot(0, 0, -s * 0.45)), fur, 0.006))
    # jaws gaping under the snout
    jo = 0.07 if pose == 'attack' else 0.03
    jaw0 = hc + V(0, -0.07 - jo * 0.3, 0.05)
    jaw1 = hc + V(0, -0.1 - jo, 0.13)
    limb(ps, jaw0, jaw1, 0.03, 0.018, fur, 0.02)
    ps.append(P(Ellipsoid((jaw1 + sn1) / 2 + V(0, 0.0, 0.01), (0.025, 0.012 + jo * 0.4, 0.03)), MOUTH, 0.004))
    for s in (-1, 1):
        for k in range(3):
            t_ = 0.35 + k * 0.25
            top = sn0 + (sn1 - sn0) * t_ + V(s * 0.022 * (1 - t_ * 0.4), -0.03, 0.01)
            ps.append(P(Cone(top, top + V(0, -0.022 - (0.012 if k == 2 else 0), 0.004), 0.0055, 0.0008), FANG, 0.0))
            bot = jaw0 + (jaw1 - jaw0) * (0.35 + k * 0.25) + V(s * 0.016, 0.014, 0.008)
            ps.append(P(Cone(bot, bot + V(0, 0.02, 0.0), 0.005, 0.0008), FANG, 0.0))
    # drool
    ps.append(P(Cone(jaw1 + V(0.01, -0.005, -0.01), jaw1 + V(0.012, -0.05, -0.01), 0.003, 0.002), Mat((0.75, 0.8, 0.85), spec=1.0), 0.004))
    # arms with long claws
    shl, shr = ch + V(-0.2, 0.06, -0.01), ch + V(0.2, 0.06, -0.01)
    if pose == 'attack':
        hl, hr = shl + V(-0.12, 0.2, 0.18), shr + V(0.12, 0.24, 0.2)
    elif pose == 'pain':
        hl, hr = shl + V(-0.16, 0.0, 0.05), shr + V(0.15, -0.08, 0.02)
    else:
        hl, hr = shl + V(-0.04, -0.3 + 0.03 * sw, 0.14), shr + V(0.04, -0.3 - 0.03 * sw, 0.16)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.07, -0.04, -0.04)
        limb(ps, sh, el, 0.07, 0.055, fur, 0.04, disp=FD)
        limb(ps, el, hd, 0.055, 0.04, fur, 0.03, disp=FD)
        ps.append(P(Ellipsoid(hd, (0.04, 0.03, 0.04)), hide, 0.02))
        d = norm(hd - el)
        for f in range(4):
            off = V((f - 1.5) * 0.018, 0, 0)
            k1 = hd + d * 0.04 + off * 1.3
            limb(ps, hd + off * 0.5, k1, 0.01, 0.008, hide, 0.006)
            limb(ps, k1, k1 + d * 0.06 + V(0, -0.025, 0.0), 0.007, 0.0012, claw, 0.002)
    return ps


# ------------------------------------------------------------------ VAMPIRE BAT

def bat(pose='walk1'):
    fur = fur_mat((0.2, 0.14, 0.12), 101)
    memb = Mat(fn=lambda p, n: np.tile(np.array([0.28, 0.11, 0.1]), (len(p), 1)) *
               (0.55 + 0.5 * fbm(p, 14, 2, 103))[:, None] *
               (1 - 0.45 * (np.abs(fbm(p, 9, 2, 104) - 0.5) < 0.025))[:, None], spec=0.3, shin=20)
    bonew = Mat((0.25, 0.17, 0.14), spec=0.3)
    ps = []
    c = V(0, 0.16, 0)
    up = {'walk1': 1, 'walk2': -1, 'attack': 0.4, 'pain': 0.6}.get(pose, 1)
    ps.append(P(Ellipsoid(c, (0.04, 0.055, 0.035)), fur, 0.02, disp=(0.004, 80, 5)))
    hc = c + V(0, 0.06, 0.01)
    if pose == 'pain':
        hc = hc + V(0.015, -0.01, -0.01)
    ps.append(P(Sphere(hc, 0.033), fur, 0.02, disp=(0.003, 80, 6)))
    ps.append(P(Ellipsoid(hc + V(0, -0.008, 0.028), (0.016, 0.012, 0.014)), Mat((0.3, 0.18, 0.17), spec=0.4), 0.008))
    for s in (-1, 1):
        e0 = hc + V(s * 0.02, 0.022, -0.004)
        ps.append(P(TriPrism(e0, (-0.014, 0.0), (0.014, 0.0), (s * 0.012, 0.05), 0.005), memb, 0.006))
        ec = hc + V(s * 0.014, 0.006, 0.027)
        ps.append(P(Sphere(ec, 0.007), EYE_BLOOD, 0.0))
    mo = 0.014 if pose == 'attack' else 0.006
    ps.append(P(Ellipsoid(hc + V(0, -0.02, 0.03), (0.012, mo, 0.01)), MOUTH, 0.003, op='sub'))
    for s in (-1, 1):
        f = hc + V(s * 0.007, -0.018, 0.034)
        ps.append(P(Cone(f, f + V(0, -0.016, 0.0), 0.0035, 0.0005), FANG, 0.0))
    # wings: arm, three finger bones, membrane triangles (front view)
    for s in (-1, 1):
        sh = c + V(s * 0.03, 0.03, 0)
        if up > 0.5:
            wr = sh + V(s * 0.1, 0.07, 0.0)
            tips = [wr + V(s * 0.12, 0.08, 0), wr + V(s * 0.15, -0.02, 0), wr + V(s * 0.1, -0.1, 0)]
        elif up < 0:
            wr = sh + V(s * 0.1, -0.06, 0.02)
            tips = [wr + V(s * 0.13, 0.02, 0), wr + V(s * 0.11, -0.08, 0), wr + V(s * 0.05, -0.14, 0)]
        else:
            wr = sh + V(s * 0.09, 0.02, 0.05)
            tips = [wr + V(s * 0.1, 0.06, 0.02), wr + V(s * 0.13, -0.03, 0.02), wr + V(s * 0.08, -0.1, 0.02)]
        limb(ps, sh, wr, 0.008, 0.006, bonew, 0.004)
        for t in tips:
            limb(ps, wr, t, 0.004, 0.002, bonew, 0.002)
        hip = c + V(s * 0.015, -0.045, 0)
        for (a_, b_) in ((tips[0], tips[1]), (tips[1], tips[2]), (tips[2], hip), (hip, sh)):
            tri = [wr, a_, b_]
            ctr = sum(tri) / 3
            ps.append(P(TriPrism(ctr, tuple(tri[0][:2] - ctr[:2]), tuple(tri[1][:2] - ctr[:2]), tuple(tri[2][:2] - ctr[:2]), 0.003),
                        memb, 0.004))
        # scalloped trailing edge: bites out between finger tips
        for k in range(len(tips) - 1):
            mid = (tips[k] + tips[k + 1]) / 2
            ctr = (mid * 2 + wr) / 3
            ps.append(P(Sphere(mid + (mid - wr) * 0.12 + (ctr - mid) * 0.0, np.linalg.norm(tips[k] - tips[k + 1]) * 0.33), memb, 0.0, op='sub'))
    # feet
    for s in (-1, 1):
        f = c + V(s * 0.012, -0.055, 0)
        limb(ps, f, f + V(s * 0.004, -0.025, 0.004), 0.005, 0.003, bonew, 0.003)
    return ps


# ------------------------------------------------------------------ VAMPIRE BRIDE

def vampire(pose='walk1'):
    gown = cloth((0.86, 0.84, 0.8), seed=111, blood=0.12)
    skin = Mat(fn=lambda p, n: np.tile(np.array([0.82, 0.84, 0.9]), (len(p), 1)) * (0.8 + 0.25 * fbm(p, 20, 2, 112))[:, None], spec=0.35, shin=25)
    hair = Mat((0.05, 0.04, 0.05), var=0.4, vfreq=60, spec=0.4)
    lips = Mat((0.35, 0.02, 0.05), spec=0.8)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    lift = 0.04

    def gown_d(p):
        y = p[:, 1] - lift
        t = np.clip(y / 0.48, 0, 1)
        rad = 0.15 - 0.08 * t
        ang = np.arctan2(p[:, 2], p[:, 0])
        cx = sw * 0.02 * (1 - t)
        d = np.sqrt((p[:, 0] - cx) ** 2 + (p[:, 2] / 0.8) ** 2) - (rad + 0.012 * np.sin(ang * 7 + y * 9 + sw))
        strands = np.abs(np.sin(ang * 6 + 0.7)) ** 3
        hem = 0.0 - 0.05 * strands + 0.05 * fbm(p * V(1, 0, 1), 12, 2, 6)
        d = np.maximum(d, hem - y)
        d = np.maximum(d, y - 0.5)
        return d * 0.7
    ps.append(P(Func(gown_d), gown, 0.0))
    ch = V(0, lift + 0.56, 0.0)
    ps.append(P(Ellipsoid(ch, (0.085, 0.09, 0.06)), gown, 0.05))
    ps.append(P(Ellipsoid(ch + V(0, 0.07, 0.01), (0.07, 0.035, 0.045)), skin, 0.03))       # bare shoulders
    hc = ch + V(0, 0.17, 0.02)
    if pose == 'pain':
        hc = hc + V(-0.035, -0.01, -0.03)
    limb(ps, ch + V(0, 0.08, 0), hc, 0.024, 0.024, skin, 0.02)
    ps.append(P(Ellipsoid(hc, (0.05, 0.062, 0.054)), skin, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.04, 0.02), (0.03, 0.025, 0.03)), skin, 0.02))
    for s in (-1, 1):
        ec = hc + V(s * 0.02, 0.008, 0.045)
        ps.append(P(Sphere(ec, 0.013), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.003), 0.0075), EYE_BLOOD, 0.0))
    mo = 0.022 if pose == 'attack' else 0.006
    ps.append(P(Ellipsoid(hc + V(0, -0.034, 0.045), (0.016, 0.006 + mo * 0.5, 0.012)), lips, 0.003))
    ps.append(P(Ellipsoid(hc + V(0, -0.034, 0.05), (0.012, 0.002 + mo * 0.45, 0.012)), MOUTH, 0.002, op='sub'))
    for s in (-1, 1):
        f = hc + V(s * 0.007, -0.03, 0.052)
        ps.append(P(Cone(f, f + V(0, -0.014 - mo * 0.2, 0.0), 0.003, 0.0004), FANG, 0.0))
    # long black hair
    for i in range(15):
        a = -1.7 + i * 0.24
        st = hc + V(np.sin(a) * 0.05, 0.035, np.cos(a) * 0.035 - 0.025)
        en = st + V(np.sin(a) * 0.05, -0.3 - 0.04 * (i % 3), -0.03)
        limb(ps, st, (st + en) / 2 + V(np.sin(a) * 0.02, 0, 0), 0.012, 0.009, hair, 0.012)
        limb(ps, (st + en) / 2 + V(np.sin(a) * 0.02, 0, 0), en, 0.009, 0.004, hair, 0.01)
    ps.append(P(Ellipsoid(hc + V(0, 0.03, -0.01), (0.056, 0.045, 0.058)), hair, 0.01))
    # arms
    shl, shr = ch + V(-0.085, 0.06, 0), ch + V(0.085, 0.06, 0)
    if pose == 'attack':
        hl, hr = shl + V(-0.08, 0.0, 0.12), shr + V(0.02, 0.06, 0.26)
    elif pose == 'pain':
        hl, hr = shl + V(-0.07, 0.12, 0.03), shr + V(0.07, 0.12, 0.03)
    else:
        hl, hr = shl + V(-0.04, -0.1, 0.17 + 0.02 * sw), shr + V(0.04, -0.1, 0.17 - 0.02 * sw)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.03, -0.04, -0.01)
        limb(ps, sh, el, 0.022, 0.018, skin, 0.015)
        limb(ps, el, hd, 0.018, 0.014, skin, 0.012)
        ps.append(P(Sphere(hd, 0.017), skin, 0.008))
        d = norm(hd - el)
        for f in range(4):
            off = V((f - 1.5) * 0.009, 0, 0)
            limb(ps, hd + off, hd + off * 1.4 + d * 0.05 + V(0, -0.012, 0), 0.004, 0.0015, skin, 0.003)
    if pose == 'attack':
        ps.append(P(Sphere(hr + V(0, 0.03, 0.05), 0.04), BLOODFIRE, 0.0, disp=(0.008, 25, 11)))
    return ps


# ------------------------------------------------------------------ BOSS 2: Mister Giggles the ringmaster

def giggles(pose='walk1'):
    coat = Mat(fn=lambda p, n: np.tile(np.array([0.62, 0.06, 0.07]), (len(p), 1)) * (0.6 + 0.55 * fbm(p, 10, 3, 121))[:, None], spec=0.45, shin=20)
    shirt = cloth((0.9, 0.88, 0.82), seed=124, blood=0.12)
    stripes = Mat(fn=lambda p, n: np.where((np.sin(p[:, 0] * 140) > 0)[:, None], np.array([[0.9, 0.88, 0.84]]), np.array([[0.08, 0.07, 0.08]])) *
                  (0.75 + 0.3 * fbm(p, 8, 2, 122))[:, None])
    hatm = Mat((0.06, 0.05, 0.06), var=0.15, vfreq=12, spec=0.4)
    skin = clown_skin()
    paint = Mat((0.8, 0.03, 0.04), spec=0.6, shin=40)
    hair = Mat((1.0, 0.45, 0.08), var=0.35, vfreq=40)
    shoe = Mat((0.1, 0.4, 0.15), spec=0.8, shin=40)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.55
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.1, hip_y, 0)
        knee = hip + V(s * 0.015, -0.26, 0.06 * ls + 0.02)
        ank = knee + V(0, -0.24, -0.04 * ls)
        limb(ps, hip, knee, 0.075, 0.062, stripes, 0.04)
        limb(ps, knee, ank, 0.062, 0.052, stripes, 0.03)
        ps.append(P(Ellipsoid(ank + V(s * 0.015, -0.03, 0.11), (0.075, 0.04, 0.16)), shoe, 0.03))
    # enormous belly in a red tailcoat
    bc = V(0, hip_y + 0.2, 0.05)
    ps.append(P(Ellipsoid(bc + V(0, 0.04, -0.05), (0.28, 0.25, 0.2)), coat, 0.06))
    waist = Mat(fn=lambda p, n: np.where((np.sin(p[:, 0] * 90) > 0.6)[:, None], np.array([[0.55, 0.42, 0.12]]), np.array([[0.16, 0.05, 0.18]])) *
                (0.7 + 0.4 * fbm(p, 9, 2, 126))[:, None], spec=0.5, shin=25)
    ps.append(P(Ellipsoid(bc + V(0, -0.01, 0.06), (0.15, 0.22, 0.17)), waist, 0.04))
    ps.append(P(Ellipsoid(bc + V(0, 0.19, 0.12), (0.06, 0.06, 0.05)), shirt, 0.02))
    for k in range(4):
        ps.append(P(Sphere(bc + V(0, 0.12 - k * 0.075, 0.225 - abs(k - 1) * 0.012), 0.016), GOLD, 0.003))
    for s_ in (-1, 1):      # lapels
        ps.append(P(Box(bc + V(s_ * 0.13, 0.1, 0.13), (0.035, 0.16, 0.03), R=rot(0.2, s_ * 0.5, -s_ * 0.2), r=0.01), coat, 0.03))
    for k in range(4):
        ps.append(P(Sphere(bc + V(0, 0.16 - k * 0.1, 0.205 - abs(k - 1.5) * 0.015), 0.018), GOLD, 0.004))
    # coat tails behind the legs
    for s in (-1, 1):
        ps.append(P(Box(V(s * 0.12, hip_y - 0.12, -0.12), (0.08, 0.2, 0.012), R=rot(0.15, 0, s * 0.1), r=0.01), coat, 0.02))
    # shoulders, bow tie
    ch = bc + V(0, 0.27, -0.02)
    ps.append(P(Ellipsoid(ch, (0.24, 0.1, 0.14)), coat, 0.07))
    bt = ch + V(0, 0.04, 0.13)
    for s in (-1, 1):
        ps.append(P(TriPrism(bt + V(s * 0.035, 0, 0), (-s * 0.035, 0.0), (s * 0.035, 0.03), (s * 0.035, -0.03), 0.015), GLOSS_RED, 0.004))
    ps.append(P(Sphere(bt, 0.016), GLOSS_RED, 0.0))
    # big head
    hc = ch + V(0, 0.22, 0.04)
    if pose == 'pain':
        hc = hc + V(0.06, -0.02, -0.05)
    r = 0.15
    ps.append(P(Ellipsoid(hc, (r, r * 1.05, r * 0.95)), skin, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.08, 0.05), (r * 0.8, r * 0.55, r * 0.6)), skin, 0.04))
    for s in (-1, 1):
        ec = hc + V(s * 0.06, 0.03, r * 0.82)
        ps.append(P(TriPrism(ec + V(0, 0, -0.008), (-0.035, 0.0), (0.035, 0.0), (0, s * 0.0 + 0.05), 0.01), Mat((0.15, 0.25, 0.8)), 0.003))
        ps.append(P(TriPrism(ec + V(0, 0, -0.008), (-0.035, 0.0), (0.035, 0.0), (0, -0.04), 0.01), Mat((0.15, 0.25, 0.8)), 0.003))
        ps.append(P(Sphere(ec + V(0, 0, 0.012), 0.022), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, 0.0), 0.014), EYE_BLOOD, 0.0))
        ps.append(P(Box(hc + V(s * 0.065, 0.09, r * 0.8), (0.035, 0.007, 0.008), R=rot(0, 0, -s * 0.45)), BLACK, 0.003))
    ps.append(P(Sphere(hc + V(0, -0.01, r * 0.98), 0.04), GLOSS_RED, 0.0))
    # ear-to-ear grin with shark teeth
    mo = 0.06 if pose == 'attack' else 0.035
    mc = hc + V(0, -0.1, r * 0.72)
    ps.append(P(Ellipsoid(mc + V(0, 0, -0.01), (0.12, 0.03 + mo * 0.5, 0.03)), paint, 0.006))
    ps.append(P(Ellipsoid(mc + V(0, 0, 0.01), (0.1, mo, 0.05)), MOUTH, 0.004, op='sub'))
    for i in range(11):
        x = (i - 5) * 0.017
        yy = mo * 0.9 * (1 - (x / 0.1) ** 2 * 0.5)
        ps.append(P(Cone(mc + V(x, yy, 0.012), mc + V(x, yy - 0.022, 0.016), 0.007, 0.0008), FANG, 0.0))
        ps.append(P(Cone(mc + V(x, -yy, 0.012), mc + V(x, -yy + 0.02, 0.016), 0.006, 0.0008), FANG, 0.0))
    # frizzy hair tufts
    for s in (-1, 1):
        for k in range(7):
            a = k * 0.75
            c = hc + V(s * (r + 0.02 * np.cos(a)), 0.03 + 0.04 * np.sin(a), -0.02 + 0.03 * np.sin(a * 1.5))
            ps.append(P(Sphere(c, 0.045), hair, 0.03, disp=(0.012, 25, 9 + k)))
    # top hat, cocked
    hb = hc + V(0.02, r * 0.85, -0.01)
    R = rot(0.05, 0, -0.18)
    ps.append(P(Cyl(hb, 0.17, 0.008, R=R), hatm, 0.0))
    ps.append(P(Cyl(hb + R @ V(0, 0.13, 0), 0.105, 0.13, R=R), hatm, 0.01))
    ps.append(P(Cyl(hb + R @ V(0, 0.035, 0), 0.108, 0.025, R=R), coat, 0.0))
    # arms: knives fanned in each hand when attacking
    shl, shr = ch + V(-0.25, 0.0, 0), ch + V(0.25, 0.0, 0)
    if pose == 'attack':
        hl, hr = shl + V(-0.16, 0.22, 0.12), shr + V(0.16, 0.24, 0.12)
    elif pose == 'pain':
        hl, hr = shl + V(-0.2, -0.05, 0.1), shr + V(0.2, 0.08, 0.0)
    else:
        hl, hr = shl + V(-0.08, -0.32 - 0.03 * sw, 0.16), shr + V(0.08, -0.32 + 0.03 * sw, 0.18)
    for sh, hd, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd) / 2 + V(s * 0.08, -0.05, -0.04)
        limb(ps, sh, el, 0.07, 0.06, coat, 0.04)
        limb(ps, el, hd, 0.06, 0.05, coat, 0.03)
        ps.append(P(Cyl(hd - norm(hd - el) * 0.01, 0.055, 0.015, R=rot(np.pi / 2, 0, 0)), shirt, 0.01))
        ps.append(P(Sphere(hd + norm(hd - el) * 0.04, 0.05), cloth((0.92, 0.9, 0.86), seed=125 + s, blood=0.2), 0.02))
        if pose == 'attack':
            for k in range(3):
                knife_prims(ps, hd + norm(hd - el) * 0.06, V(s * (0.2 + 0.35 * (k - 1)), 1.0, 0.25), V(0, 0, 1), 0.15, 0.02)
    if pose != 'attack':
        # cane in the right hand
        cb = hr + V(0, 0, 0.04)
        limb(ps, cb + V(0, -0.45, 0.05), cb + V(0, 0.08, 0), 0.012, 0.012, hatm, 0.0)
        ps.append(P(Sphere(cb + V(0, 0.1, 0), 0.03), GOLD, 0.0))
    return ps


# ------------------------------------------------------------------ BOSS 3: Count Hollowfang

def count(pose='walk1'):
    capeo = Mat((0.05, 0.04, 0.06), var=0.25, vfreq=10, spec=0.35, shin=15)
    capei = Mat(fn=lambda p, n: np.tile(np.array([0.55, 0.03, 0.06]), (len(p), 1)) * (0.6 + 0.5 * fbm(p, 9, 2, 131))[:, None], spec=0.6, shin=25)
    suit = Mat((0.07, 0.06, 0.08), var=0.2, vfreq=20, spec=0.3)
    vest = Mat((0.4, 0.04, 0.06), var=0.2, vfreq=25, spec=0.5)
    shirt = Mat((0.88, 0.86, 0.82), var=0.08, vfreq=20)
    skin = Mat(fn=lambda p, n: np.tile(np.array([0.7, 0.74, 0.8]), (len(p), 1)) * (0.78 + 0.25 * fbm(p, 18, 2, 132))[:, None], spec=0.35, shin=22)
    hair = Mat((0.04, 0.035, 0.04), var=0.2, vfreq=80, spec=0.9, shin=40)
    gem = Mat((1.0, 0.1, 0.1), glow=1.0)
    ps = []
    sw = {'walk1': -1, 'walk2': 1}.get(pose, 0)
    hip_y = 0.5
    for s, ls in ((-1, sw), (1, -sw)):
        hip = V(s * 0.07, hip_y, 0)
        knee = hip + V(s * 0.01, -0.24, 0.05 * ls + 0.01)
        ank = knee + V(0, -0.23, -0.03 * ls)
        limb(ps, hip, knee, 0.055, 0.045, suit, 0.03)
        limb(ps, knee, ank, 0.045, 0.038, suit, 0.02)
        ps.append(P(Ellipsoid(ank + V(0, -0.02, 0.05), (0.04, 0.025, 0.08)), Mat((0.03, 0.03, 0.03), spec=1.0, shin=50), 0.02))
    # slender torso
    ch = V(0, hip_y + 0.36, 0.0)
    ps.append(P(Ellipsoid(V(0, hip_y + 0.12, 0), (0.1, 0.14, 0.075)), suit, 0.05))
    ps.append(P(Ellipsoid(ch, (0.15, 0.13, 0.09)), suit, 0.06))
    ps.append(P(Box(ch + V(0, -0.12, 0.07), (0.055, 0.2, 0.02), r=0.02), vest, 0.03))
    ps.append(P(Box(ch + V(0, 0.02, 0.08), (0.03, 0.09, 0.015), r=0.01), shirt, 0.02))
    # medallion
    md = ch + V(0, -0.05, 0.1)
    limb(ps, ch + V(-0.05, 0.1, 0.07), md, 0.004, 0.004, GOLD, 0.0)
    limb(ps, ch + V(0.05, 0.1, 0.07), md, 0.004, 0.004, GOLD, 0.0)
    ps.append(P(Cyl(md, 0.032, 0.006, R=rot(np.pi / 2, 0, 0)), GOLD, 0.0))
    ps.append(P(Sphere(md + V(0, 0, 0.006), 0.014), gem, 0.0))
    # head
    hc = ch + V(0, 0.25, 0.02)
    if pose == 'pain':
        hc = hc + V(0.04, -0.015, -0.04)
    limb(ps, ch + V(0, 0.1, 0), hc, 0.035, 0.032, skin, 0.03)
    ps.append(P(Ellipsoid(hc, (0.06, 0.075, 0.066)), skin, 0.0))
    ps.append(P(Ellipsoid(hc + V(0, -0.05, 0.022), (0.036, 0.035, 0.04)), skin, 0.025))     # long chin
    for s in (-1, 1):
        ps.append(P(Ellipsoid(hc + V(s * 0.038, -0.022, 0.038), (0.014, 0.012, 0.016)), skin, 0.008))   # cheekbones
        ps.append(P(Cone(hc + V(s * 0.055, 0.0, -0.005), hc + V(s * 0.09, 0.04, -0.03), 0.014, 0.002), skin, 0.008))  # pointed ears
        ec = hc + V(s * 0.023, 0.012, 0.055)
        ps.append(P(Sphere(ec, 0.014), BLACK, 0.004, op='sub'))
        ps.append(P(Sphere(ec + V(0, 0, -0.004), 0.0085), EYE_BLOOD, 0.0))
        ps.append(P(Box(hc + V(s * 0.025, 0.033, 0.06), (0.018, 0.004, 0.006), R=rot(0, 0, -s * 0.4)), hair, 0.002))
    ps.append(P(Cone(hc + V(0, 0.015, 0.06), hc + V(0, -0.018, 0.08), 0.007, 0.012), skin, 0.008))     # hooked nose
    mo = 0.022 if pose == 'attack' else 0.006
    ps.append(P(Ellipsoid(hc + V(0, -0.04, 0.055), (0.024, 0.004 + mo * 0.5, 0.014)), MOUTH, 0.003, op='sub'))
    for s in (-1, 1):
        f = hc + V(s * 0.011, -0.036, 0.06)
        ps.append(P(Cone(f, f + V(0, -0.02 - mo * 0.3, 0.002), 0.0042, 0.0004), FANG, 0.0))
    # slicked hair with widow's peak
    hd = Ellipsoid(hc + V(0, 0.022, -0.008), (0.063, 0.062, 0.068))
    def hair_d(p):
        q = p - hc
        peak = 0.035 - np.abs(q[:, 0]) * 0.9
        return np.maximum(hd.d(p), (peak - q[:, 1]) - np.clip(-q[:, 2] - 0.01, 0, 1) * 2.0)
    ps.append(P(Func(hair_d), hair, 0.004))
    # high collar
    for s in (-1, 1):
        ps.append(P(TriPrism(hc + V(s * 0.085, -0.05, -0.05), (-s * 0.04, -0.06), (s * 0.05, -0.07), (s * 0.04, 0.12), 0.01), capei, 0.01))
    # arms
    shl, shr = ch + V(-0.16, 0.06, 0), ch + V(0.16, 0.06, 0)
    if pose == 'attack':
        hl, hr = shl + V(-0.3, 0.22, 0.06), shr + V(0.3, 0.24, 0.06)
    elif pose == 'pain':
        hl, hr = shl + V(-0.08, 0.1, 0.12), shr + V(0.1, 0.12, 0.1)
    else:
        hl, hr = shl + V(-0.03, -0.28 - 0.02 * sw, 0.1), shr + V(0.05, -0.12, 0.2)
    for sh, hd_, s in ((shl, hl, -1), (shr, hr, 1)):
        el = (sh + hd_) / 2 + V(s * 0.05, -0.05, -0.03)
        limb(ps, sh, el, 0.045, 0.038, suit, 0.03)
        limb(ps, el, hd_, 0.038, 0.03, suit, 0.02)
        ps.append(P(Sphere(hd_, 0.026), skin, 0.01))
        d = norm(hd_ - el)
        for f in range(4):
            off = V((f - 1.5) * 0.013, 0, 0)
            k1 = hd_ + d * 0.04 + off * 1.2
            limb(ps, hd_ + off * 0.6, k1, 0.0065, 0.0055, skin, 0.004)
            limb(ps, k1, k1 + d * 0.05 + V(0, -0.01, 0), 0.0055, 0.001, Mat((0.15, 0.12, 0.12), spec=0.6), 0.002)
    # cape: hangs behind, or spreads like bat wings in the attack pose
    if pose == 'attack':
        for s in (-1, 1):
            hd_ = hl if s < 0 else hr
            neck = ch + V(s * 0.06, 0.12, -0.06)
            tips = [hd_ + V(0, 0.04, -0.03), hd_ + V(s * 0.1, -0.25, -0.05), V(s * 0.42, 0.25, -0.07), V(s * 0.28, 0.06, -0.07)]
            pts = [neck, tips[0], tips[2], tips[1], tips[3], V(s * 0.1, 0.05, -0.07)]
            for k in range(1, len(pts) - 1):
                a, b, cc = pts[0], pts[k], pts[k + 1]
                ctr = (a + b + cc) / 3
                ps.append(P(TriPrism(ctr, tuple(a[:2] - ctr[:2]), tuple(b[:2] - ctr[:2]), tuple(cc[:2] - ctr[:2]), 0.008),
                            capei, 0.01))
                ps.append(P(TriPrism(ctr + V(0, 0, -0.016), tuple(a[:2] - ctr[:2]), tuple(b[:2] - ctr[:2]), tuple(cc[:2] - ctr[:2]), 0.008),
                            capeo, 0.01))
        ps.append(P(Sphere(hr + V(0.0, 0.05, 0.06), 0.045), BLOODFIRE, 0.0, disp=(0.01, 22, 13)))
        ps.append(P(Sphere(hl + V(0.0, 0.05, 0.06), 0.045), BLOODFIRE, 0.0, disp=(0.01, 22, 14)))
    else:
        def cape_d(p):
            y = p[:, 1]
            t = np.clip((y - 0.02) / 0.95, 0, 1)
            rad = 0.27 - 0.12 * t + 0.02 * np.sin(np.arctan2(p[:, 2], p[:, 0]) * 8 + y * 5 + sw)
            dd = np.sqrt(p[:, 0] ** 2 + ((p[:, 2] + 0.02) / 0.75) ** 2)
            shell = np.abs(dd - rad) - 0.012
            front = p[:, 2] - (0.03 - 0.12 * (1 - t))         # open at the front
            d = np.maximum(shell, front)
            hem = 0.03 + 0.04 * np.abs(np.sin(np.arctan2(p[:, 2], p[:, 0]) * 5))
            d = np.maximum(d, hem - y)
            d = np.maximum(d, y - 0.97)
            return d * 0.7
        ps.append(P(Func(cape_d), capeo, 0.0))
        ps.append(P(Ellipsoid(ch + V(0, 0.08, -0.04), (0.2, 0.06, 0.11)), capeo, 0.04))
    return ps


# ------------------------------------------------------------------ projectiles

def knife_proj(frame=0):
    ps = []
    if frame == 0:
        knife_prims(ps, V(-0.09, 0.05, 0), V(1, 0, 0), V(0, 1, 0), 0.12, 0.02)
    else:
        knife_prims(ps, V(0.02, 0.0, 0), V(-0.3, 1, 0), V(0, 0, 1), 0.12, 0.02)
    return ps


def blood_bolt(seed=0):
    ps = [P(Sphere((0, 0.05, 0), 0.045), BLOODFIRE, 0.0, disp=(0.012, 18, 20 + seed))]
    for k in range(3):
        a = seed * 1.3 + k * 2.1
        ps.append(P(Sphere((np.cos(a) * 0.05, 0.05 + np.sin(a) * 0.04, -0.03), 0.018), BLOODFIRE, 0.0))
    return ps


def juggling_bomb():
    stripes = Mat(fn=lambda p, n: np.where((np.sin(np.arctan2(p[:, 2], p[:, 0]) * 4) > 0)[:, None],
                                           np.array([[0.9, 0.1, 0.1]]), np.array([[0.95, 0.85, 0.1]])), spec=0.9, shin=40)
    ps = [P(Sphere((0, 0.06, 0), 0.055), stripes, 0.0)]
    ps.append(P(Cone((0, 0.11, 0), (0.02, 0.15, 0.0), 0.006, 0.005), Mat((0.3, 0.25, 0.2)), 0.0))
    ps.append(P(Sphere((0.022, 0.155, 0.0), 0.014), FIREBALL, 0.0))
    return ps
