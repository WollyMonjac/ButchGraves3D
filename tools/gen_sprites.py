#!/usr/bin/env python3
"""Render every SDF sprite to tools/spr/<name>.png (alpha 255 = normal, 128 = fullbright glow)
and tools/spr/meta.json with anchors. Usage: gen_sprites.py [name-filter ...] [--force]"""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
from PIL import Image
from sdf import *
import monsters as M
import props as PR
import weapons as WP

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spr')
PPU = 96
JOBS = []   # (name, kind, builder-spec)


def job(name, fn, w, h, y0=-0.03, ss=2, kind='world'):
    JOBS.append((name, fn, w, h, y0, ss, kind))


MON = {
    'zombie': (M.zombie, 84, 92, M.BLOOD),
    'scarecrow': (M.scarecrow, 104, 108, PR.Mat((0.7, 0.42, 0.08), var=0.3, vfreq=20)),
    'witch': (M.witch, 84, 110, M.BLOOD),
    'wraith': (M.wraith, 84, 92, None),
}
for nm, (fn, w, h, pool) in MON.items():
    for pose in ('walk1', 'walk2', 'attack', 'pain'):
        job('%s_%s' % (nm, pose), (nm, pose), w, h)
    job('%s_fall' % nm, (nm, 'fall'), 110, 100)
    job('%s_dead' % nm, (nm, 'dead'), 120, 52, y0=-0.05)
for pose in ('walk1', 'walk2', 'attack', 'pain'):
    job('boss_%s' % pose, ('boss', pose), 170, 186, ss=2)
job('boss_fall', ('boss', 'fall'), 190, 170)
job('boss_dead', ('boss', 'dead'), 210, 80, y0=-0.05)

ITEMS = [('candy', PR.candy, 40, 26), ('bucket', PR.bucket, 40, 40), ('brew', PR.brew, 32, 40), ('armor', PR.armor, 48, 44),
         ('bullets', PR.bullets, 32, 24), ('shells', PR.shells, 32, 22), ('pumpkins', PR.pumpkin_ammo, 48, 30),
         ('pk_shotgun', lambda: PR.gun_side('shotgun'), 64, 22), ('pk_tommy', lambda: PR.gun_side('tommy'), 64, 22),
         ('pk_launcher', lambda: PR.gun_side('launcher'), 64, 30),
         ('key_red', lambda: PR.skull_key((1.0, 0.18, 0.1)), 30, 34), ('key_blue', lambda: PR.skull_key((0.25, 0.55, 1.0)), 30, 34),
         ('key_gold', lambda: PR.skull_key((1.0, 0.85, 0.15)), 30, 34),
         ('jack', PR.jack, 44, 34), ('jack2', lambda: PR.jack(0.1, 5), 40, 30), ('candles', PR.candles, 44, 34),
         ('tree', PR.dead_tree, 150, 150), ('tomb', lambda: PR.tombstone(0, 1), 40, 52), ('tomb2', lambda: PR.tombstone(1, 2), 40, 52),
         ('cauldron', PR.cauldron, 56, 38), ('keg', PR.keg, 44, 42), ('skulls', PR.skull_pile, 48, 26), ('lamp', PR.lamppost, 30, 146),
         ('patch', PR.pumpkin_patch, 60, 28), ('gibs', PR.gibs, 80, 20),
         ('fireball1', lambda: PR.fireball(0), 30, 26), ('fireball2', lambda: PR.fireball(3), 30, 26),
         ('greenball1', lambda: PR.fireball(1, True), 30, 26), ('greenball2', lambda: PR.fireball(4, True), 30, 26),
         ('pbomb', lambda: PR.pumpkin_bomb(0.06), 22, 22)]
for nm, fn, w, h in ITEMS:
    job(nm, fn, w, h, y0=-0.02)
job('hanging', PR.skeleton_hanging, 50, 72, y0=0.3)

# ------------------------------------------------------------------ episodes 2 and 3
import monsters2 as M2
import props2 as P2
MON2 = {   # name: (model fn, w, h, fall fn, dead fn, fall size, dead size)
    'skel': (M2.skeleton, 100, 140, P2.skel_fall, P2.skel_dead, (110, 110), (80, 34)),
    'clown': (M2.clown, 100, 124, None, None, (130, 110), (130, 52)),
    'wolf': (M2.werewolf, 124, 124, None, None, (140, 120), (150, 60)),
    'bat': (M2.bat, 74, 52, P2.bat_fall, P2.bat_dead, (60, 70), (70, 30)),
    'vamp': (M2.vampire, 90, 108, P2.vamp_fall, P2.vamp_dead, (90, 90), (60, 30)),
    'giggles': (M2.giggles, 240, 200, P2.giggles_fall, P2.giggles_dead, (230, 200), (260, 80)),
    'count': (M2.count, 190, 150, P2.count_fall, P2.count_dead, (170, 120), (80, 36)),
}
for nm, (fn, w, h, ff, fd, fs, ds) in MON2.items():
    for pose in ('walk1', 'walk2', 'attack', 'pain'):
        job('%s_%s' % (nm, pose), (lambda fn=fn, pose=pose: fn(pose)), w, h)
    if ff is None:
        ff = (lambda fn=fn: PR.corpse_frames(fn)[0])
        fd = (lambda fn=fn: PR.corpse_frames(fn)[1])
    job('%s_fall' % nm, ff, fs[0], fs[1])
    job('%s_dead' % nm, fd, ds[0], ds[1], y0=-0.05)
for nm, fn, w, h in [('knife1', P2.knife1, 34, 24), ('knife2', P2.knife2, 30, 30), ('bolt1', lambda: M2.blood_bolt(0), 26, 26),
                     ('bolt2', lambda: M2.blood_bolt(1), 26, 26), ('jball', M2.juggling_bomb, 22, 26)]:
    job(nm, fn, w, h, y0=-0.02)
PROPS2 = dict(streetlamp=(40, 140), balloons=(50, 100), carousel=(80, 130), cotton=(70, 80), hydrant=(26, 34), trashcan=(34, 44),
              wreck=(96, 56), bulbs=(110, 100), clownhead=(70, 82), strongman=(56, 140), candelabra=(40, 100), coffin=(44, 92),
              cypress=(100, 150), tesla=(50, 100), tank=(50, 104), knight=(56, 130), cage=(40, 104), brazier=(36, 90), reeds=(44, 66),
              gargoyle=(56, 100))
for nm, (w, h) in PROPS2.items():
    job(nm, getattr(P2, nm), w, h, y0=-0.02)
for pose in ('stand', 'walk1', 'walk2', 'wind', 'swing', 'aim'):
    job('butch_' + pose, (lambda pose=pose: P2.butch(pose)), 84, 150)
for nm, fn, w, h in [('cs_pkhead', lambda: P2.pk_head(False), 52, 50), ('cs_pkhead2', lambda: P2.pk_head(True), 52, 50),
                     ('cs_kid', lambda: P2.kid(False), 40, 56), ('cs_kid2', lambda: P2.kid(True), 40, 56),
                     ('cs_car', P2.clown_car, 64, 50), ('cs_balloon', P2.balloon, 20, 40),
                     ('cs_cbat1', lambda: P2.count_bat(True), 74, 56), ('cs_cbat2', lambda: P2.count_bat(False), 74, 56),
                     ('cs_star', P2.star, 20, 24)]:
    job(nm, fn, w, h, y0=-0.02)

# ------------------------------------------------------------------ episode 4 (Halloween 2099)
import monsters3 as M3
import props3 as P3
MON3 = {   # name: (model fn, w, h, fall size, dead size)
    'frank': (M3.frankbot, 120, 130, (130, 120), (160, 60)),
    'drone': (M3.drone, 90, 76, (90, 80), (80, 30)),
    'cyborg': (M3.cyborg, 110, 104, (120, 100), (130, 52)),
    'spider': (M3.spider, 110, 64, (110, 70), (110, 50)),
    'prime': (M3.prime, 250, 210, (250, 210), (340, 124)),
}
for nm, (fn, w, h, fs, ds) in MON3.items():
    for pose in ('walk1', 'walk2', 'attack', 'pain'):
        job('%s_%s' % (nm, pose), (lambda fn=fn, pose=pose: fn(pose)), w, h)
    job('%s_fall' % nm, getattr(M3, nm + '_fall'), fs[0], fs[1])
    job('%s_dead' % nm, getattr(M3, nm + '_dead'), ds[0], ds[1], y0=-0.05)
for nm, fn, w, h in [('zap1', lambda: M3.zap_proj(0), 40, 36), ('zap2', lambda: M3.zap_proj(1), 40, 36),
                     ('laser1', lambda: M3.laser_proj(0), 30, 14), ('laser2', lambda: M3.laser_proj(1), 30, 14)]:
    job(nm, fn, w, h, y0=-0.02)
PROPS3 = dict(holotomb=(40, 60), neonjack=(50, 100), crate=(44, 44), toxic=(36, 44), robotarm=(50, 100), capsule=(44, 104),
              terminal=(40, 72), cables=(40, 100), telepad=(70, 56))
for nm, (w, h) in PROPS3.items():
    job(nm, getattr(P3, nm), w, h, y0=-0.02 if nm != 'cables' else 0.3)
for pose in ('carry', 'cwalk1', 'cwalk2', 'point', 'shrug', 'kick'):
    job('butch_' + pose, (lambda pose=pose: P2.butch(pose)), 84, 150)
for nm, fn, w, h in [('cs_doc', lambda: P3.doc('stand'), 64, 100), ('cs_docrant', lambda: P3.doc('rant'), 70, 100),
                     ('cs_docrun1', lambda: P3.doc('run1'), 64, 100), ('cs_docrun2', lambda: P3.doc('run2'), 64, 100),
                     ('cs_minibot1', lambda: P3.minibot(0), 30, 28), ('cs_minibot2', lambda: P3.minibot(1), 30, 28),
                     ('cs_portal1', lambda: P3.portal(0), 70, 100), ('cs_portal2', lambda: P3.portal(2), 70, 100),
                     ('cs_wreck', lambda: [P3._scaled(pr, 0.5, M3.V(0, 0, 0)) for pr in M3.prime_dead()], 170, 64),
                     ('cs_pksmash', P3.pk_smash, 90, 44), ('cs_nose', P3.nose, 14, 14), ('cs_goggles', P3.goggles, 24, 14)]:
    job(nm, fn, w, h, y0=-0.02)

# ------------------------------------------------------------------ episode 5 (Curse of the Jade Skull)
import monsters4 as M4
import props4 as P4
MON4 = {   # name: (model fn, w, h, fall size, dead size)
    'mummy': (M4.mummy, 90, 100, (110, 90), (130, 44)),
    'jaguar': (M4.jaguar, 120, 120, (130, 110), (150, 56)),
    'conq': (M4.conq, 110, 130, (120, 110), (110, 40)),
    'weeper': (M4.weeper, 90, 120, (90, 110), (110, 30)),
    'seven': (M4.seven, 240, 230, (250, 210), (300, 90)),
}
for nm, (fn, w, h, fs, ds) in MON4.items():
    for pose in ('walk1', 'walk2', 'attack', 'pain'):
        job('%s_%s' % (nm, pose), (lambda fn=fn, pose=pose: fn(pose)), w, h)
    job('%s_fall' % nm, getattr(M4, nm + '_fall'), fs[0], fs[1])
    job('%s_dead' % nm, getattr(M4, nm + '_dead'), ds[0], ds[1], y0=-0.05)
for nm, fn, w, h in [('dart1', lambda: M4.dart(0), 24, 10), ('dart2', lambda: M4.dart(1), 24, 10), ('shot1', lambda: M4.shot(0), 20, 12),
                     ('shot2', lambda: M4.shot(1), 20, 12), ('disc1', lambda: M4.disc(0), 30, 16), ('disc2', lambda: M4.disc(1), 30, 16),
                     ('rock', lambda: M4.rock(0), 16, 14), ('idol', P4.idol, 20, 26),
                     ('boulder_1', lambda: P4.boulder(0), 92, 92), ('boulder_2', lambda: P4.boulder(1), 92, 92)]:
    job(nm, fn, w, h, y0=-0.02)
PROPS4 = dict(kapok=(150, 160), palm=(100, 150), fern=(64, 40), olmec=(70, 80), jstatue=(40, 64), rack=(64, 70), ofrenda=(56, 64),
              torch=(26, 86), pillar=(30, 90), gold=(50, 24), tent=(110, 56))
for nm, (w, h) in PROPS4.items():
    job(nm, getattr(P4, nm), w, h, y0=-0.02)
job('vines', P4.vines, 40, 100, y0=0.3)
for nm, fn, w, h in [('cs_crane', lambda: P4.crane('stand'), 64, 100), ('cs_cranerant', lambda: P4.crane('rant'), 64, 110),
                     ('cs_cranerun1', lambda: P4.crane('run1'), 64, 100), ('cs_cranerun2', lambda: P4.crane('run2'), 64, 100),
                     ('cs_cranemelt1', lambda: P4.crane('melt1'), 64, 110), ('cs_cranemelt2', lambda: P4.crane('melt2'), 64, 110),
                     ('cs_shrunk', P4.shrunk, 30, 26), ('cs_jskull', P4.jskull, 20, 16), ('cs_rubble', P4.rubble, 70, 24),
                     ('cs_cranebones', P4.crane_bones, 60, 22)]:
    job(nm, fn, w, h, y0=-0.02)

# ------------------------------------------------------------------ cutscene close-up portraits (talking heads, Duke style)
import hero as HERO
PORTRAITS = [   # name, builder, w, h, cam_y, cam_h, lights
    ('cpbutch_1', lambda: HERO.bust('smirk'), 112, 140, -0.16, 0.66, 'hero'),
    ('cpbutch_2', lambda: HERO.bust('talk'), 112, 140, -0.16, 0.66, 'hero'),
    ('cpbutch_3', lambda: HERO.bust('grin'), 112, 140, -0.16, 0.66, 'hero'),
    ('cpgore_1', lambda: HERO.bust('grin', 2), 112, 140, -0.16, 0.66, 'hero'),
    ('cpgore_2', lambda: HERO.bust('talk', 2), 112, 140, -0.16, 0.66, 'hero'),
    ('cppk_1', lambda: P2.pk_head(False), 120, 120, 0.21, 0.5, None),
    ('cppk_2', lambda: P2.pk_head(True), 120, 120, 0.21, 0.5, None),
    ('cpkid_1', lambda: P2.kid(False), 110, 110, 0.36, 0.34, None),
    ('cpkid_2', lambda: P2.kid(True), 110, 110, 0.38, 0.38, None),
    ('cpgig_1', lambda: M2.giggles('walk1'), 120, 120, 1.2, 0.56, None),
    ('cpgig_2', lambda: M2.giggles('attack'), 120, 120, 1.2, 0.56, None),
    ('cpcount_1', lambda: P2.count_bat(True), 120, 100, 0.2, 0.3, None),
    ('cpcount_2', lambda: P2.count_bat(False), 120, 100, 0.2, 0.3, None),
    ('cpdoc_1', lambda: P3.doc('stand'), 110, 120, 0.66, 0.42, None),
    ('cpdoc_2', lambda: P3.doc('rant'), 110, 120, 0.66, 0.42, None),
    ('cpcrane_1', lambda: P4.crane('stand'), 110, 120, 0.7, 0.42, None),
    ('cpcrane_2', lambda: P4.crane('rant'), 110, 120, 0.7, 0.42, None),
    ('cpmelt_1', lambda: P4.crane('melt1'), 110, 120, 0.7, 0.42, None),
    ('cpmelt_2', lambda: P4.crane('melt2'), 110, 120, 0.7, 0.42, None),
    ('cpshrunk_1', lambda: P4.shrunk('smug'), 90, 90, 0.075, 0.17, None),
    ('cpshrunk_2', lambda: P4.shrunk('rant'), 90, 90, 0.075, 0.17, None),
    ('cpseven_1', lambda: M4.seven('walk1'), 120, 120, 1.62, 0.86, None),
    ('cpseven_2', lambda: M4.seven('attack'), 120, 120, 1.62, 0.86, None),
]
for nm, fn, w, h, cy, ch, li in PORTRAITS:
    JOBS.append((nm, fn, w, h, (cy, ch, li), 2, 'portrait'))

WPN = [('revolver', 0), ('revolver', 1), ('shotgun', 0), ('shotgun', 1), ('shotgun', 2), ('tommy', 0), ('tommy', 1), ('tommy', 2),
       ('launcher', 0), ('launcher', 1), ('shovel', 0), ('shovel', 1), ('shovel', 2)]
for nm, fr in WPN:
    job('w_%s%d' % (nm, fr), (nm, fr), 160, 96, kind='weapon')


def build(spec):
    if isinstance(spec, tuple):
        nm, pose = spec
        if nm == 'boss':
            fn = M.pumpking
            pool = PR.BLOOD if hasattr(PR, 'BLOOD') else M.BLOOD
            if pose == 'fall':
                return M.tilt_scene(fn('pain'), ang_z=0.4, shift=(0.05, -0.04, 0))
            if pose == 'dead':
                return [P(Ellipsoid((0, -0.005, 0.03), (0.6, 0.015, 0.25)), M.BLOOD, 0.0)] + \
                    M.tilt_scene(fn('pain'), ang_z=1.48, shift=(0.7, 0.13, 0))
            return fn(pose)
        fn, w, h, pool = MON[nm]
        if nm == 'wraith' and pose in ('fall', 'dead'):
            return PR.wraith_death(0 if pose == 'fall' else 1)
        if pose == 'fall':
            return PR.corpse_frames(fn, pool or M.BLOOD)[0]
        if pose == 'dead':
            return PR.corpse_frames(fn, pool or M.BLOOD)[1]
        return fn(pose)
    return spec()


def render_job(ji):
    name, spec, w, h, y0, ss, kind = JOBS[ji]
    t = time.time()
    if kind == 'portrait':
        cy, ch, li = y0
        lights = None
        if li == 'hero':
            lights = [Light((-0.6, 0.4, 0.6), (0.55, 0.5, 0.6), 'dir', True), Light((0.7, 0.3, -0.6), (0.9, 1.0, 1.4), 'rim'),
                      Light((0.3, -0.8, 0.6), (0.9, 0.4, 0.1), 'dir')]
        im = render(spec(), w, h, cam_y=cy, cam_h=ch, ss=ss, lights=lights, ambient=0.22 if lights else 0.28)
        gx, gy = w / 2.0, h
    elif kind == 'weapon':
        nm, fr = spec
        im = render(WP.weapon(nm, fr), w, h, cam_y=-0.12, cam_h=0.96, ss=ss, fov_dist=1.0, cam_z_tilt=0.12,
                    lights=WP.WEAPON_LIGHTS, tstart=0.05, tspan=3.0)
        gx, gy = w / 2.0, h          # anchor: bottom centre of virtual screen
    else:
        ps = build(spec)
        cam_h = h / PPU
        im = render(ps, w, h, cam_y=y0 + cam_h / 2, cam_h=cam_h, ss=ss)
        gx, gy = w / 2.0, (y0 + cam_h) * PPU
    rgb, glow = im.rgb, im.glow
    if (name.endswith('_fall') or name.endswith('_dead') or name == 'cs_wreck') and not name.startswith('wraith'):
        rgb = rgb.copy()
        rgb[glow] *= 0.22 if name.endswith('_dead') else 0.4
        glow = np.zeros_like(glow)
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    a[..., 3] = np.where(im.alpha, np.where(glow, 128, 255), 0)
    ys, xs = np.nonzero(a[..., 3])
    if len(ys) == 0:
        print('EMPTY', name)
        return name, None
    y0p, y1p, x0p, x1p = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    a = a[y0p:y1p, x0p:x1p]
    Image.fromarray(a, 'RGBA').save(os.path.join(OUT, name + '.png'))
    meta = [int(round(gx - x0p)), int(round(gy - y0p))]
    print('%-18s %3dx%-3d %.1fs' % (name, a.shape[1], a.shape[0], time.time() - t), flush=True)
    return name, meta


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    force = '--force' in sys.argv
    filt = [a for a in sys.argv[1:] if not a.startswith('--')]
    mp = os.path.join(OUT, 'meta.json')
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    todo = []
    for j in JOBS:
        nm = j[0]
        if filt and not any(f in nm for f in filt):
            continue
        if not force and not filt and os.path.exists(os.path.join(OUT, nm + '.png')) and nm in meta:
            continue
        todo.append(JOBS.index(j))
    print(len(todo), 'jobs', flush=True)
    t0 = time.time()
    with Pool(int(os.environ.get("SPR_PROCS", "2"))) as pool:
        for nm, m in pool.imap_unordered(render_job, todo):
            if m is not None:
                meta[nm] = m
                json.dump(meta, open(mp, 'w'), indent=0)
    print('done %.0fs' % (time.time() - t0))
