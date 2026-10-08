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
    if kind == 'weapon':
        nm, fr = spec
        im = render(WP.weapon(nm, fr), w, h, cam_y=-0.12, cam_h=0.96, ss=ss, fov_dist=1.0, cam_z_tilt=0.12,
                    lights=WP.WEAPON_LIGHTS, tstart=0.05, tspan=3.0)
        gx, gy = w / 2.0, h          # anchor: bottom centre of virtual screen
    else:
        ps = build(spec)
        cam_h = h / PPU
        im = render(ps, w, h, cam_y=y0 + cam_h / 2, cam_h=cam_h, ss=ss)
        gx, gy = w / 2.0, (y0 + cam_h) * PPU
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = (np.clip(im.rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    a[..., 3] = np.where(im.alpha, np.where(im.glow, 128, 255), 0)
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
    with Pool(2) as pool:
        for nm, m in pool.imap_unordered(render_job, todo):
            if m is not None:
                meta[nm] = m
                json.dump(meta, open(mp, 'w'), indent=0)
    print('done %.0fs' % (time.time() - t0))
