#!/usr/bin/env python3
"""Build the four levels programmatically, validate them and write res/l1..l4.bin plus preview PNGs."""
import os, json, struct
from collections import deque
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'res')
info = json.load(open(os.path.join(HERE, 'pack_info.json')))
WALLS = {n: i for i, n in enumerate(info['walls'])}
FLATS = {n: i for i, n in enumerate(info['flats'])}
SKY = 255

# thing types (must match Java World constants)
T = dict(zombie=1, scarecrow=2, wraith=3, witch=4, boss=5,
         candy=10, bucket=11, brew=12, armor=13, bullets=14, shells=15, pumpkins=16, shotgun=17, tommy=18, launcher=19,
         key_red=20, key_blue=21, key_gold=22,
         jack=30, jack2=31, candles=32, tree=33, tomb=34, tomb2=35, hanging=36, cauldron=37, keg=38, skulls=39, lamp=40,
         patch=41, gibs=42)
# flags
F_DOOR, F_SECRET, F_EXIT, F_HURT, F_KRED, F_KBLUE, F_KGOLD, F_OUT = 1, 2, 4, 8, 16, 32, 64, 128


class Level:
    def __init__(self, name, sub, w, h, sky=0, music=1, fog=(16, 8, 24), fogk=18, lightning=0, ambient_out=12):
        self.name, self.sub, self.w, self.h = name, sub, w, h
        self.sky, self.music, self.fog, self.fogk, self.lightning = sky, music, fog, fogk, lightning
        self.wall = np.zeros((h, w), int)          # 0 = empty, else tex+1
        self.flr = np.zeros((h, w), int)
        self.ceil = np.zeros((h, w), int)
        self.light = np.full((h, w), 16, int)
        self.flag = np.zeros((h, w), int)
        self.things = []                            # (type, x, y, minskill)
        self.start = (1.5, 1.5, 0)
        self.ambient_out = ambient_out

    # ---------- painting helpers
    def region(self, x0, y0, x1, y1, flr, ceil, light, out=False, hurt=False):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.wall[y, x] = 0
                self.flr[y, x] = FLATS[flr]
                self.ceil[y, x] = SKY if ceil == 'sky' else FLATS[ceil]
                self.light[y, x] = light
                self.flag[y, x] = (F_OUT if out or ceil == 'sky' else 0) | (F_HURT if hurt else 0)

    def walls(self, x0, y0, x1, y1, tex):
        for x in range(x0, x1 + 1):
            self.setw(x, y0, tex); self.setw(x, y1, tex)
        for y in range(y0, y1 + 1):
            self.setw(x0, y, tex); self.setw(x1, y, tex)

    def block(self, x0, y0, x1, y1, tex):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.setw(x, y, tex)

    def setw(self, x, y, tex):
        self.wall[y, x] = WALLS[tex] + 1
        self.flag[y, x] &= F_OUT

    def room(self, x0, y0, x1, y1, wtex, flr, ceil, light, out=False, hurt=False):
        """Walls on the border, region inside."""
        self.region(x0 + 1, y0 + 1, x1 - 1, y1 - 1, flr, ceil, light, out, hurt)
        self.walls(x0, y0, x1, y1, wtex)

    def door(self, x, y, key=None, secret=None):
        fl = F_DOOR
        tex = 'door'
        if key == 'red':
            fl |= F_KRED; tex = 'door_red'
        if key == 'blue':
            fl |= F_KBLUE; tex = 'door_blue'
        if key == 'gold':
            fl |= F_KGOLD; tex = 'door_gold'
        if secret:
            fl |= F_SECRET; tex = secret
        # the door cell is floor-like (takes floor/ceil/light from neighbours), with a wall texture used for the slab
        nb = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for (nx, ny) in nb:
            if self.wall[ny, nx] == 0:
                self.flr[y, x] = self.flr[ny, nx]; self.ceil[y, x] = self.ceil[ny, nx]; self.light[y, x] = self.light[ny, nx]
                break
        self.wall[y, x] = WALLS[tex] + 1
        self.flag[y, x] = fl

    def exitw(self, x, y):
        self.wall[y, x] = WALLS['exit'] + 1
        self.flag[y, x] = F_EXIT

    def put(self, kind, x, y, skill=0):
        self.things.append((T[kind], x + 0.5, y + 0.5, skill))

    def putf(self, kind, x, y, skill=0):
        self.things.append((T[kind], x, y, skill))

    # ---------- validation & output
    def solid(self, x, y):
        return self.wall[y, x] != 0 and not (self.flag[y, x] & F_DOOR)

    def validate(self):
        h, w = self.h, self.w
        for x in range(w):
            assert self.wall[0, x] and self.wall[h - 1, x], ('open border', self.name, x)
        for y in range(h):
            assert self.wall[y, 0] and self.wall[y, w - 1], ('open border', self.name, y)
        # doors need walls on two opposite sides and open on the other two
        for y in range(h):
            for x in range(w):
                if self.flag[y, x] & F_DOOR:
                    ew = self.solid(x - 1, y) and self.solid(x + 1, y)
                    ns = self.solid(x, y - 1) and self.solid(x, y + 1)
                    assert ew != ns, ('door orientation', self.name, x, y, ew, ns)
                    if ew:
                        assert self.wall[y - 1, x] == 0 and self.wall[y + 1, x] == 0, ('door blocked', self.name, x, y)
                    else:
                        assert self.wall[y, x - 1] == 0 and self.wall[y, x + 1] == 0, ('door blocked', self.name, x, y)
        # things must be on open cells
        solid_things = {T['tree'], T['tomb'], T['tomb2'], T['cauldron'], T['keg'], T['lamp']}
        blocked = np.zeros((h, w), bool)
        for t, x, y, s in self.things:
            cx, cy = int(x), int(y)
            assert self.wall[cy, cx] == 0, ('thing in wall', self.name, t, x, y)
            if t in solid_things:
                blocked[cy, cx] = True
        sx, sy, sa = self.start
        assert self.wall[int(sy), int(sx)] == 0

        def reach(keys):
            seen = np.zeros((h, w), bool)
            q = deque([(int(sx), int(sy))]); seen[int(sy), int(sx)] = True
            while q:
                x, y = q.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if seen[ny, nx] or blocked[ny, nx]:
                        continue
                    wv, fl = self.wall[ny, nx], self.flag[ny, nx]
                    if wv and not (fl & F_DOOR):
                        continue
                    if fl & F_KRED and 'red' not in keys: continue
                    if fl & F_KBLUE and 'blue' not in keys: continue
                    if fl & F_KGOLD and 'gold' not in keys: continue
                    seen[ny, nx] = True
                    q.append((nx, ny))
            return seen
        keys = set()
        for it in range(4):
            seen = reach(keys)
            for t, x, y, s in self.things:
                if seen[int(y), int(x)]:
                    if t == T['key_red']: keys.add('red')
                    if t == T['key_blue']: keys.add('blue')
                    if t == T['key_gold']: keys.add('gold')
        seen = reach(keys)
        exits = [(x, y) for y in range(h) for x in range(w) if self.flag[y, x] & F_EXIT]
        ok_exit = any(seen[y + dy, x + dx] for (x, y) in exits for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                      if 0 <= x + dx < w and 0 <= y + dy < h)
        bosses = [t for t in self.things if t[0] == T['boss']]
        assert ok_exit or bosses, ('exit unreachable', self.name)
        unreach = [(t, x, y) for t, x, y, s in self.things if not seen[int(y), int(x)] and t not in solid_things]
        return keys, unreach

    def write(self, fname):
        out = bytearray(b'L')
        out += struct.pack('>b', 1)
        for s in (self.name, self.sub):
            b = s.encode()
            out += struct.pack('>h', len(b)) + b
        out += struct.pack('>BBBBBBBB', self.sky, self.music, self.fog[0], self.fog[1], self.fog[2], self.fogk, self.lightning, 0)
        out += struct.pack('>BB', self.w, self.h)
        sx, sy, sa = self.start
        out += struct.pack('>hhh', int(sx * 16), int(sy * 16), sa)
        for arr in (self.wall, self.flr, self.ceil, self.light, self.flag):
            out += arr.astype(np.uint8).tobytes()
        out += struct.pack('>h', len(self.things))
        for t, x, y, s in self.things:
            out += struct.pack('>Bhhb', t, int(x * 16), int(y * 16), s)
        with open(os.path.join(RES, fname), 'wb') as f:
            f.write(out)
        return len(out)

    def preview(self, fname):
        pal = np.array(info['pal'])
        s = 8
        img = np.zeros((self.h * s, self.w * s, 3), np.uint8)
        cols = {T['zombie']: (120, 200, 80), T['scarecrow']: (255, 140, 0), T['wraith']: (180, 230, 255), T['witch']: (160, 60, 200),
                T['boss']: (255, 0, 0)}
        for y in range(self.h):
            for x in range(self.w):
                if self.wall[y, x]:
                    c = (110, 100, 90)
                    if self.flag[y, x] & F_DOOR: c = (200, 160, 60)
                    if self.flag[y, x] & F_KRED: c = (255, 40, 40)
                    if self.flag[y, x] & F_KBLUE: c = (60, 90, 255)
                    if self.flag[y, x] & F_KGOLD: c = (255, 220, 0)
                    if self.flag[y, x] & F_SECRET: c = (150, 0, 150)
                    if self.flag[y, x] & F_EXIT: c = (0, 255, 0)
                else:
                    l = 1 - self.light[y, x] / 40
                    c = (40 * l, 60 * l, 40 * l) if self.flag[y, x] & F_OUT else (60 * l, 50 * l, 40 * l)
                    if self.flag[y, x] & F_HURT: c = (60, 140, 30) if self.flr[y, x] == FLATS['slime'] else (170, 60, 10)
                img[y * s:(y + 1) * s, x * s:(x + 1) * s] = c
        for t, x, y, sk in self.things:
            c = cols.get(t, (240, 240, 120) if t < 30 else (130, 130, 160))
            px, py = int(x * s), int(y * s)
            r = 3 if t < 30 else 2
            img[max(0, py - r):py + r, max(0, px - r):px + r] = c
        px, py = int(self.start[0] * s), int(self.start[1] * s)
        img[py - 3:py + 3, px - 3:px + 3] = (255, 255, 255)
        Image.fromarray(img).resize((self.w * s * 2, self.h * s * 2), Image.NEAREST).save(os.path.join(HERE, 'out', fname))


NORTH, EAST, SOUTH, WEST = 3072, 0, 1024, 2048

# ================================================================== LEVEL 1: Dead End Cemetery


def level1():
    L = Level('DEAD END CEMETERY', 'Night 1 - Hollow Creek', 44, 36, sky=0, music=1, fog=(14, 8, 26), fogk=17, lightning=1)
    W, H = L.w, L.h
    L.region(1, 1, W - 2, H - 2, 'grass', 'sky', 13, out=True)
    L.walls(0, 0, W - 1, H - 1, 'brick')
    # dirt paths
    L.region(5, 18, 6, 29, 'dirt', 'sky', 12, out=True)          # shack -> north
    L.region(5, 17, 33, 18, 'dirt', 'sky', 12, out=True)         # east-west path
    L.region(6, 11, 7, 17, 'dirt', 'sky', 12, out=True)          # to mausoleum
    L.region(31, 12, 32, 30, 'dirt', 'sky', 12, out=True)        # to patch and chapel
    # caretaker shack (start)
    L.room(1, 29, 10, 34, 'wood', 'woodfloor', 'ceilwood', 12)
    L.door(5, 29)
    L.start = (5.5, 32.5, NORTH)
    L.put('candy', 2, 33); L.put('bullets', 9, 33); L.put('candles', 9, 30); L.put('bucket', 2, 30)
    # mausoleum (red key door, exit inside)
    L.room(1, 1, 13, 10, 'crypt', 'flagstone', 'ceilstone', 18)
    L.block(4, 3, 4, 4, 'stone'); L.block(10, 3, 10, 4, 'stone'); L.block(4, 7, 4, 8, 'stone'); L.block(10, 7, 10, 8, 'stone')
    L.door(7, 10, key='red')
    L.exitw(1, 5)
    L.put('candles', 2, 2); L.put('candles', 2, 9); L.put('candles', 12, 2); L.put('candles', 12, 9)
    L.put('skulls', 7, 3); L.put('hanging', 7, 6); L.put('shells', 12, 5); L.put('wraith', 8, 4, 1); L.put('zombie', 11, 7)
    # pumpkin patch (hedges) with the red key
    L.room(24, 1, 38, 11, 'hedge', 'dirt', 'sky', 11, out=True)
    L.region(31, 11, 32, 11, 'dirt', 'sky', 12, out=True)       # gap in the hedge
    L.walls(24, 1, 38, 1, 'brick')
    for (x, y) in ((26, 3), (29, 3), (33, 3), (36, 3), (26, 6), (36, 6), (27, 9), (35, 9)):
        L.put('patch', x, y)
    L.put('jack', 28, 5); L.put('jack2', 34, 5); L.put('jack', 31, 9)
    L.put('key_red', 31, 3)
    L.put('scarecrow', 27, 4); L.put('scarecrow', 35, 4); L.put('scarecrow', 31, 7, 1); L.put('zombie', 25, 9, 2)
    # secret nook behind the hedge (east)
    L.room(38, 1, 42, 7, 'hedge', 'grass', 'sky', 9, out=True)
    L.walls(38, 1, 42, 1, 'brick'); L.walls(42, 1, 42, 7, 'brick')
    L.door(38, 4, secret='hedge')
    L.put('brew', 40, 3); L.put('armor', 40, 5); L.put('jack2', 41, 2)
    # chapel ruin (south-east)
    L.room(28, 24, 42, 34, 'stone', 'flagstone', 'ceilwood', 16)
    L.door(28, 29)
    L.block(32, 26, 32, 27, 'stone'); L.block(37, 26, 37, 27, 'stone'); L.block(32, 31, 32, 32, 'stone'); L.block(37, 31, 37, 32, 'stone')
    L.put('candles', 40, 29); L.put('skulls', 35, 25); L.put('bucket', 41, 25); L.put('bullets', 41, 33)
    L.put('shells', 30, 33); L.put('wraith', 35, 29); L.put('zombie', 40, 32, 1); L.put('hanging', 34, 29)
    # window in the chapel back wall
    L.setw(42, 29, 'window')
    # graveyard: tombstone rows, trees, lamps, lights, zombies
    for row, y in enumerate((13, 21, 25)):
        for x in range(14, 27, 3):
            L.put('tomb' if (x + row) % 2 else 'tomb2', x, y)
    for (x, y) in ((18, 6), (21, 9), (15, 3), (20, 2), (9, 14), (36, 14), (24, 31), (16, 33), (39, 20)):
        L.put('tree', x, y)
    for (x, y) in ((8, 16), (16, 19), (26, 19), (30, 16), (8, 25), (33, 22)):
        L.put('lamp', x, y)
    for (x, y) in ((12, 13), (22, 24), (17, 29), (27, 13), (36, 18)):
        L.put('jack' if (x + y) % 2 else 'jack2', x, y)
    # open grave with the shotgun (north-centre)
    L.put('gibs', 18, 4); L.put('shotgun', 17, 4); L.put('skulls', 20, 4); L.put('jack', 16, 5)
    L.put('zombie', 15, 7); L.put('zombie', 20, 7); L.put('zombie', 18, 10, 1)
    L.put('zombie', 11, 20); L.put('zombie', 20, 15); L.put('zombie', 24, 23); L.put('zombie', 14, 27, 1)
    L.put('zombie', 22, 30); L.put('zombie', 36, 21, 2); L.put('zombie', 27, 28); L.put('scarecrow', 39, 14, 1)
    L.put('zombie', 30, 7, 2)
    # pickups around
    L.put('candy', 12, 18); L.put('candy', 25, 16); L.put('bullets', 22, 18); L.put('shells', 14, 23)
    L.put('candy', 37, 16); L.put('bullets', 3, 12); L.put('candy', 3, 22); L.put('keg', 12, 23); L.put('keg', 27, 22)
    return L

# ================================================================== LEVEL 2: Blackwood Manor


def level2():
    L = Level('BLACKWOOD MANOR', 'Night 2 - The Cult House', 48, 44, sky=0, music=2, fog=(8, 4, 10), fogk=15, lightning=1)
    W, H = L.w, L.h
    L.region(1, 1, W - 2, H - 2, 'grass', 'sky', 13, out=True)
    L.walls(0, 0, W - 1, H - 1, 'brick')
    # front courtyard (south)
    L.region(1, 33, W - 2, H - 2, 'grass', 'sky', 13, out=True)
    L.region(22, 33, 25, H - 2, 'dirt', 'sky', 12, out=True)
    L.start = (23.5, 41.5, NORTH)
    for (x, y) in ((19, 36), (28, 36), (19, 40), (28, 40)):
        L.put('lamp', x, y)
    for (x, y) in ((6, 36), (12, 40), (36, 37), (42, 40), (4, 41)):
        L.put('tree', x, y)
    L.put('jack', 21, 34); L.put('jack2', 26, 34); L.put('patch', 10, 35); L.put('patch', 38, 35)
    L.put('zombie', 10, 38); L.put('zombie', 37, 39); L.put('scarecrow', 41, 35, 1); L.put('candy', 30, 41); L.put('bullets', 16, 41)
    L.put('tomb', 44, 36); L.put('tomb2', 44, 39); L.put('tomb', 3, 36)
    # manor shell
    L.block(1, 1, W - 2, 32, 'brick')
    # grand hall (centre)
    L.room(15, 18, 32, 31, 'wallpaper', 'checker', 'ceilwood', 15)
    L.region(23, 31, 23, 31, 'checker', 'ceilwood', 15)
    L.door(23, 32)
    for (x, y) in ((18, 20), (29, 20)):
        L.block(x, y, x, y, 'wood')
    L.block(18, 28, 18, 28, 'wood'); L.block(29, 28, 29, 28, 'wood')
    L.setw(20, 18, 'portrait'); L.setw(27, 18, 'portrait'); L.setw(15, 25, 'portrait'); L.setw(32, 25, 'portrait')
    L.put('candles', 16, 19); L.put('candles', 31, 19); L.put('candles', 16, 30); L.put('candles', 31, 30)
    L.put('hanging', 23, 24); L.put('wraith', 20, 23); L.put('wraith', 27, 23); L.put('zombie', 23, 29, 1)
    L.put('bucket', 17, 25); L.put('shells', 30, 25)
    # west wing: library with blue key, secret room
    L.room(2, 18, 15, 31, 'bookshelf', 'carpet', 'ceilwood', 17)
    L.door(15, 22)
    for y in (21, 24, 27):
        L.block(5, y, 11, y, 'bookshelf')
    L.put('key_blue', 3, 30); L.put('witch', 8, 29); L.put('wraith', 12, 20, 1); L.put('candles', 13, 30); L.put('candles', 3, 19)
    L.put('bullets', 8, 19); L.put('candy', 13, 26); L.put('skulls', 3, 25)
    L.room(2, 12, 9, 18, 'bookshelf', 'woodfloor', 'ceilwood', 14)
    L.door(5, 18, secret='bookshelf')
    L.put('launcher', 4, 14); L.put('pumpkins', 7, 14); L.put('brew', 5, 16); L.put('jack', 3, 13)
    # east wing: dining room with tommy gun
    L.room(32, 18, 45, 31, 'wallpaper2', 'carpet', 'ceilwood', 15)
    L.door(32, 29)
    L.block(36, 23, 41, 26, 'wood')            # long table
    L.setw(45, 21, 'window'); L.setw(45, 28, 'window')
    L.put('tommy', 38, 21); L.put('witch', 42, 29); L.put('zombie', 35, 30); L.put('wraith', 43, 20, 1)
    L.put('candles', 34, 22); L.put('candles', 43, 25); L.put('cauldron', 39, 29); L.put('bullets', 34, 27); L.put('candy', 43, 30)
    # north gallery corridor
    L.room(8, 12, 40, 18, 'wallpaper', 'woodfloor', 'ceilwood', 16)
    L.setw(8, 15, 'wallpaper')
    L.door(23, 18)
    for x in (12, 18, 28, 34):
        L.setw(x, 12, 'portrait')
    for x in (15, 21, 25, 31, 37):
        L.setw(x, 12, 'window')
    L.put('candles', 10, 13); L.put('candles', 38, 13); L.put('zombie', 14, 15); L.put('witch', 33, 15, 1); L.put('wraith', 26, 14)
    L.put('shells', 39, 16); L.put('candy', 9, 16)
    # kitchen (north-west of gallery)
    L.room(32, 4, 45, 12, 'wood', 'flagstone', 'ceilwood', 15)
    L.door(36, 12)
    L.put('cauldron', 38, 7); L.put('keg', 33, 5); L.put('keg', 44, 5); L.put('zombie', 42, 9); L.put('witch', 34, 8, 2)
    L.put('bucket', 44, 11); L.put('pumpkins', 33, 11)
    # blue door -> crypt stairs with exit (north)
    L.room(14, 4, 26, 12, 'stone', 'flagstone', 'ceilstone', 19)
    L.door(20, 12, key='blue')
    L.exitw(20, 4)
    L.put('candles', 15, 5); L.put('candles', 25, 5); L.put('skulls', 17, 8); L.put('skulls', 23, 8)
    L.put('scarecrow', 16, 10, 1); L.put('scarecrow', 24, 10); L.put('wraith', 20, 7)
    return L

# ================================================================== LEVEL 3: Bone Catacombs


def level3():
    L = Level('THE BONE CATACOMBS', 'Night 3 - Under Blackwood', 48, 48, sky=255, music=3, fog=(2, 6, 2), fogk=22)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'skullwall')
    def corr(x0, y0, x1, y1, light=19):
        L.region(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), 'bones', 'ceilstone', light)
    def chamber(x0, y0, x1, y1, light=17, flr='flagstone', tex='stone'):
        L.room(x0, y0, x1, y1, tex, flr, 'ceilstone', light)
    # start crypt (south-west)
    chamber(2, 38, 10, 45, 15)
    L.start = (6.5, 43.5, NORTH)
    L.put('candles', 3, 44); L.put('candles', 9, 39); L.put('bullets', 9, 44); L.put('candy', 3, 39)
    L.door(6, 38)
    corr(5, 30, 7, 37)
    # hub ossuary
    chamber(3, 22, 17, 30, 17, 'bones', 'skullwall')
    L.region(5, 30, 7, 30, 'bones', 'ceilstone', 19)
    L.block(8, 25, 12, 27, 'skullwall')
    L.put('skulls', 7, 24); L.put('skulls', 14, 28); L.put('hanging', 5, 27); L.put('candles', 15, 23)
    L.put('zombie', 10, 23); L.put('zombie', 14, 25); L.put('wraith', 5, 24, 1); L.put('shells', 4, 29)
    # corridor east to slime hall
    corr(17, 26, 27, 27)
    L.region(17, 26, 17, 27, 'bones', 'ceilstone', 19)
    # slime hall (hurt floor)
    chamber(27, 20, 40, 33, 18, 'flagstone', 'stone')
    L.region(29, 22, 38, 31, 'slime', 'ceilstone', 14, hurt=True)
    L.region(29, 26, 38, 27, 'flagstone', 'ceilstone', 16)        # bridge
    L.region(33, 22, 34, 31, 'flagstone', 'ceilstone', 16)
    L.region(27, 26, 27, 27, 'bones', 'ceilstone', 18)
    L.put('cauldron', 28, 21); L.put('witch', 36, 23); L.put('witch', 31, 30, 1); L.put('zombie', 37, 27)
    L.put('pumpkins', 39, 21); L.put('candy', 28, 32); L.put('bucket', 39, 32)
    # launcher shrine (north of slime hall)
    L.region(33, 15, 34, 19, 'bones', 'ceilstone', 18)
    L.region(33, 20, 34, 20, 'flagstone', 'ceilstone', 16)
    chamber(29, 9, 38, 15, 15)
    L.region(33, 15, 34, 15, 'bones', 'ceilstone', 18)
    L.put('launcher', 33, 11); L.put('jack', 30, 10); L.put('jack', 37, 10); L.put('pumpkins', 30, 14); L.put('scarecrow', 36, 13)
    L.put('scarecrow', 31, 12, 1)
    # gold key crypt (east, past slime)
    L.region(41, 26, 44, 27, 'bones', 'ceilstone', 18)
    L.region(40, 26, 40, 27, 'flagstone', 'ceilstone', 16)
    chamber(41, 18, 46, 25, 16)
    L.region(42, 25, 43, 25, 'bones', 'ceilstone', 18)
    L.put('key_gold', 44, 19); L.put('candles', 42, 19); L.put('wraith', 43, 22); L.put('zombie', 45, 23, 1); L.put('shells', 42, 24)
    # north corridor from hub to gold door
    corr(9, 12, 10, 21)
    L.region(9, 21, 10, 22, 'bones', 'ceilstone', 19)
    corr(9, 11, 21, 12)
    L.put('zombie', 10, 15); L.put('zombie', 16, 11, 1); L.put('candy', 21, 12); L.put('bullets', 9, 18)
    # secret alcove off the north corridor
    chamber(3, 12, 8, 17, 13)
    L.door(8, 14, secret='skullwall')
    L.put('brew', 5, 14); L.put('armor', 4, 16); L.put('candles', 4, 13)
    # gold door and the harvest altar (exit)
    L.region(22, 11, 22, 11, 'bones', 'ceilstone', 18)
    L.region(24, 9, 25, 11, 'bones', 'ceilstone', 18)
    chamber(24, 2, 36, 8, 14, 'flagstone', 'pumpkinwall')
    L.region(24, 8, 25, 8, 'flagstone', 'ceilstone', 14)
    L.door(23, 11, key='gold')
    L.exitw(30, 2)
    L.put('jack', 26, 3); L.put('jack2', 34, 3); L.put('candles', 30, 4); L.put('scarecrow', 27, 6); L.put('scarecrow', 33, 6)
    L.put('wraith', 30, 6, 1); L.put('bucket', 35, 7)
    # south-east crypt loop with extra loot
    corr(12, 31, 13, 40)
    L.region(12, 30, 13, 30, 'bones', 'ceilstone', 19)
    chamber(14, 36, 24, 45, 17, 'bones', 'skullwall')
    L.region(14, 39, 14, 40, 'bones', 'ceilstone', 18)
    L.put('zombie', 18, 38); L.put('zombie', 22, 43); L.put('witch', 20, 41, 2); L.put('keg', 16, 43); L.put('keg', 23, 37)
    L.put('bullets', 22, 38); L.put('candy', 15, 44); L.put('hanging', 19, 40)
    return L

# ================================================================== LEVEL 4: The Pumpkin King


def level4():
    L = Level("THE PUMPKIN KING'S PATCH", 'Night 4 - Blood Moon', 40, 42, sky=1, music=4, fog=(30, 4, 2), fogk=12, lightning=1)
    W, H = L.w, L.h
    L.region(1, 1, W - 2, H - 2, 'dirt', 'sky', 11, out=True)
    L.walls(0, 0, W - 1, H - 1, 'pumpkinwall')
    # start alcove (south)
    L.room(15, 35, 24, 40, 'stone', 'flagstone', 'ceilstone', 13)
    L.door(19, 35)
    L.start = (19.5, 38.5, NORTH)
    L.put('bucket', 16, 39); L.put('shells', 23, 39); L.put('pumpkins', 16, 36); L.put('bullets', 23, 36); L.put('armor', 19, 39)
    # lava pools
    for (x0, y0, x1, y1) in ((5, 8, 10, 13), (29, 8, 34, 13), (6, 25, 11, 29), (28, 25, 33, 29), (17, 15, 22, 17)):
        L.region(x0, y0, x1, y1, 'lava', 'sky', 4, hurt=True)
    # pillars of flesh
    for (x, y) in ((12, 18), (27, 18), (12, 30), (27, 30), (19, 22), (19, 8)):
        L.block(x, y, x + 1, y + 1, 'flesh')
    # side walls of pumpkins
    L.block(1, 19, 4, 21, 'pumpkinwall'); L.block(35, 19, 38, 21, 'pumpkinwall')
    for (x, y) in ((8, 4), (31, 4), (4, 16), (35, 16), (8, 33), (31, 33), (14, 12), (25, 12)):
        L.put('jack' if (x + y) % 2 else 'jack2', x, y)
    for (x, y) in ((3, 3), (36, 3), (3, 38), (36, 38), (14, 27), (25, 27)):
        L.put('tree', x, y)
    for (x, y) in ((16, 4), (23, 4), (6, 22), (33, 22)):
        L.put('patch', x, y)
    # supply caches in the corners
    L.put('brew', 2, 2); L.put('pumpkins', 37, 2); L.put('pumpkins', 2, 33); L.put('bucket', 37, 33)
    L.put('shells', 2, 16); L.put('bullets', 37, 16); L.put('candy', 13, 25); L.put('candy', 26, 25); L.put('shells', 19, 28)
    L.put('keg', 15, 20); L.put('keg', 24, 20); L.put('keg', 10, 34); L.put('keg', 29, 34)
    # the Pumpkin King and his court
    L.put('boss', 19, 11)
    L.put('scarecrow', 9, 18); L.put('scarecrow', 30, 18); L.put('witch', 6, 6, 1); L.put('witch', 33, 6, 1)
    L.put('zombie', 14, 31); L.put('zombie', 25, 31); L.put('wraith', 19, 26); L.put('zombie', 4, 30, 2); L.put('zombie', 35, 30, 2)
    return L


if __name__ == '__main__':
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    for k, fn in enumerate((level1, level2, level3, level4)):
        L = fn()
        keys, unreach = L.validate()
        n = L.write('l%d.bin' % (k + 1))
        L.preview('map%d.png' % (k + 1))
        mons = sum(1 for t in L.things if t[0] < 10)
        print('level', k + 1, L.name, 'bytes', n, 'things', len(L.things), 'monsters', mons, 'keys', keys, 'unreachable', unreach)
