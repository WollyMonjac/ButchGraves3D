"""Butch Graves himself: HUD faces and title-screen bust (SDF)."""
import numpy as np
from sdf import *
from monsters import BLOOD, BLACK, TEETH, TriPrism
from weapons import JACKET, GUNMETAL, WOOD

SKIN = Mat(fn=lambda p, n: np.tile(np.array([0.8, 0.56, 0.42]), (len(p), 1)) * (0.88 + 0.2 * fbm(p, 25, 2, 3))[:, None]
           * (1 - 0.35 * np.clip((p[:, 1] - 0.0) * -10 + 0.25, 0, 1) * (fbm(p, 120, 1, 9) > 0.45)[:, None].ravel())[:, None], spec=0.25, shin=20)
HAIR = Mat((0.12, 0.09, 0.07), var=0.35, vfreq=90)
WHITE = Mat((0.95, 0.94, 0.9), spec=0.6, shin=40)
IRIS = Mat((0.25, 0.45, 0.65), spec=0.9, shin=60)
TANK = Mat((0.85, 0.83, 0.78), var=0.1, vfreq=20)
SCAR = Mat((0.62, 0.36, 0.32))
CANDY = Mat(fn=lambda p, n: np.where((np.sin(p[:, 0] * 300 + p[:, 1] * 300) > 0)[:, None], np.array([[0.95, 0.3, 0.1]]), np.array([[0.98, 0.95, 0.9]])), spec=0.8, shin=50)


def stubble_skin():
    def fn(p, n):
        c = np.tile(np.array([0.8, 0.56, 0.42]), (len(p), 1)) * (0.88 + 0.2 * fbm(p, 25, 2, 3))[:, None]
        jaw = np.clip((-0.035 - p[:, 1]) * 30, 0, 1) * (p[:, 1] > -0.1) * (p[:, 2] > 0.0)
        dots = fbm(p, 160, 1, 9) > 0.5
        c = c * (1 - 0.45 * (jaw * dots))[:, None]
        return c
    return Mat(fn=fn, spec=0.25, shin=20)


def head(expr='smirk', blood=0, look=0.0):
    """Head centred at origin (eyes ~ y=0.02). expr: smirk|grin|hurt|ouch|dead."""
    sk = stubble_skin()
    ps = []
    ps.append(P(Ellipsoid((0, 0.0, 0), (0.078, 0.1, 0.085)), sk, 0.0))
    ps.append(P(Box((0, -0.06, 0.02), (0.06, 0.035, 0.055), r=0.03), sk, 0.04))      # square jaw
    ps.append(P(Ellipsoid((0, -0.05, 0.04), (0.045, 0.04, 0.05)), sk, 0.03))
    for s in (-1, 1):
        ps.append(P(Ellipsoid((s * 0.08, 0.0, -0.005), (0.012, 0.025, 0.018)), sk, 0.01))          # ears
        ps.append(P(Ellipsoid((s * 0.045, -0.025, 0.06), (0.025, 0.015, 0.02)), sk, 0.02))         # cheekbones
    # brow ridge
    brow_drop = {'smirk': 0.0, 'grin': 0.004, 'hurt': -0.006, 'ouch': -0.01, 'dead': 0.0}[expr]
    ps.append(P(Box((0, 0.035, 0.07), (0.058, 0.01, 0.014), r=0.008), sk, 0.02))
    # nose
    ps.append(P(Cone((0, 0.02, 0.08), (0, -0.025, 0.098), 0.01, 0.016), sk, 0.012))
    # eye sockets & eyes
    for s in (-1, 1):
        ec = np.array([s * 0.03, 0.012, 0.068])
        ps.append(P(Ellipsoid(ec, (0.019, 0.011 if expr not in ('ouch',) else 0.004, 0.012)), BLACK, 0.004, op='sub'))
        if expr != 'dead':
            ps.append(P(Sphere(ec + np.array([0, 0, -0.007]), 0.0125), WHITE, 0.0))
            ps.append(P(Sphere(ec + np.array([look * 0.006, 0, 0.0035]), 0.0062), IRIS, 0.0))
        else:
            ps.append(P(Box(ec + np.array([0, 0, 0.004]), (0.01, 0.0015, 0.004), R=rot(0, 0, 0.6)), BLACK, 0.0))
            ps.append(P(Box(ec + np.array([0, 0, 0.004]), (0.01, 0.0015, 0.004), R=rot(0, 0, -0.6)), BLACK, 0.0))
        # thick eyebrows (angled: tough/angry)
        ang = s * (0.25 if expr in ('smirk', 'grin') else -0.2)
        ps.append(P(Box((s * 0.031, 0.034 + brow_drop, 0.083), (0.02, 0.005, 0.006), R=rot(0, 0, ang)), HAIR, 0.003))
    # mouth
    if expr == 'grin':
        ps.append(P(Ellipsoid((0.005, -0.058, 0.082), (0.03, 0.009, 0.02)), BLACK, 0.003, op='sub'))
        ps.append(P(Box((0.005, -0.054, 0.08), (0.026, 0.004, 0.006)), TEETH, 0.0))
    elif expr in ('hurt', 'ouch'):
        ps.append(P(Ellipsoid((0, -0.06, 0.082), (0.022, 0.008 if expr == 'hurt' else 0.012, 0.02)), BLACK, 0.003, op='sub'))
        ps.append(P(Box((0, -0.055, 0.079), (0.018, 0.003, 0.006)), TEETH, 0.0))
    elif expr == 'dead':
        ps.append(P(Ellipsoid((0, -0.06, 0.082), (0.02, 0.01, 0.02)), BLACK, 0.003, op='sub'))
    else:
        ps.append(P(Box((0.008, -0.058, 0.088), (0.022, 0.0025, 0.01), R=rot(0, 0, 0.12)), BLACK, 0.002, op='sub'))
        # candy-corn lollipop stick in the corner of the mouth
        ps.append(P(Cone((0.028, -0.057, 0.09), (0.058, -0.068, 0.112), 0.0028, 0.0028), WHITE, 0.0))
        ps.append(P(Cyl((0.066, -0.071, 0.118), 0.02, 0.006, R=rot(np.pi / 2 - 0.3, 0.5, 0)), CANDY, 0.0))
    # buzz cut hair
    hc = Ellipsoid((0, 0.03, -0.012), (0.083, 0.08, 0.088))
    def hair_d(p):
        return np.maximum(hc.d(p), np.maximum(0.045 - p[:, 1] + np.clip(-p[:, 2], 0, 1) * 0.6, 0.0) if False else
                          np.maximum(hc.d(p), (0.05 - p[:, 1]) - np.clip(-p[:, 2] - 0.02, 0, 1) * 1.5))
    ps.append(P(Func(hair_d), HAIR, 0.006, disp=(0.002, 90, 2)))
    # scar across left brow
    ps.append(P(Box((-0.032, 0.02, 0.083), (0.003, 0.02, 0.004), R=rot(0, 0, 0.3)), SCAR, 0.002))
    # neck + jacket collar + tank top
    ps.append(P(Cone((0, -0.08, -0.01), (0, -0.16, -0.01), 0.045, 0.052), sk, 0.03))
    ps.append(P(Ellipsoid((0, -0.2, -0.01), (0.15, 0.06, 0.08)), TANK, 0.03))
    for s in (-1, 1):
        ps.append(P(Box((s * 0.09, -0.19, 0.0), (0.06, 0.06, 0.07), R=rot(0, 0, s * 0.4), r=0.02), JACKET, 0.03))
    # blood
    if blood >= 1:
        ps.append(P(Ellipsoid((-0.04, 0.045, 0.072), (0.012, 0.02, 0.01)), BLOOD, 0.004))
        ps.append(P(Cone((-0.04, 0.03, 0.075), (-0.045, -0.02, 0.08), 0.004, 0.003), BLOOD, 0.003))
    if blood >= 2:
        ps.append(P(Ellipsoid((0.045, -0.035, 0.07), (0.016, 0.012, 0.01)), BLOOD, 0.004))
        ps.append(P(Cone((0.0, -0.035, 0.1), (0.002, -0.07, 0.095), 0.004, 0.003), BLOOD, 0.003))
        ps.append(P(Ellipsoid((0.02, 0.06, 0.06), (0.03, 0.02, 0.03)), BLOOD, 0.006))
    return ps


FACES = [('face0', 'smirk', 0), ('face1', 'hurt', 1), ('face2', 'ouch', 2), ('facegrin', 'grin', 0), ('facedead', 'dead', 2)]


def bust():
    """Title-screen hero: head plus shoulders, shotgun resting on the right shoulder."""
    ps = head('smirk', 0)
    out = []
    for pr in ps:
        out.append(pr)
    # broad shoulders & jacket
    out.append(P(Ellipsoid((0, -0.24, -0.02), (0.23, 0.06, 0.09)), JACKET, 0.05, disp=(0.003, 20, 4)))
    out.append(P(Box((0, -0.4, -0.02), (0.2, 0.14, 0.09), r=0.07), JACKET, 0.07))
    for s in (-1, 1):
        out.append(P(Ellipsoid((s * 0.2, -0.27, -0.02), (0.075, 0.08, 0.085)), JACKET, 0.05))
    out.append(P(TriPrism((0, -0.27, 0.07), (-0.05, 0.05), (0.05, 0.05), (0, -0.09), 0.02), TANK, 0.01))
    for s in (-1, 1):
        out.append(P(Box((s * 0.045, -0.3, 0.075), (0.022, 0.09, 0.012), R=rot(0, 0, s * 0.3), r=0.008), JACKET, 0.015))
    # shotgun over right shoulder (barrels pointing up-back)
    a = np.array([0.16, -0.38, 0.06]); b = np.array([0.08, 0.18, -0.06])
    d = norm(b - a)
    side = np.array([1.0, 0, 0])
    for s in (-1, 1):
        out.append(P(Cone(a + side * s * 0.012, b + side * s * 0.012, 0.012, 0.012), GUNMETAL, 0.004))
    out.append(P(Cone(a - d * 0.02, a + d * 0.2, 0.024, 0.02), WOOD, 0.01))
    return out
