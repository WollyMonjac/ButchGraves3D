"""Episodes 2 and 3 (levels 5..12) and the cutscene sets (levels 101..103)."""
import numpy as np
from gen_levels import Level, NORTH, EAST, SOUTH, WEST


def brighten(L, k):
    L.light = np.maximum(L.light - k, 0)
    return L


# ================================================================== EPISODE 2: CARNIVAL OF CARNAGE

def level5():
    L = Level('MAIN STREET MAYHEM', 'Episode 2 - Downtown Hollow Creek', 54, 40, sky='sky2', music=6, fog=(10, 10, 22), fogk=16)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'siding')
    L.region(1, 16, 44, 23, 'sidewalk', 'sky', 12, out=True)
    L.region(1, 18, 44, 21, 'asphalt', 'sky', 13, out=True)
    L.start = (2.5, 19.5, EAST)
    L.put('shotgun', 6, 19); L.put('streetlamp', 6, 17)          # the boomstick, right where you start
    # candy shop (shotgun)
    L.room(5, 8, 15, 15, 'wood', 'checker', 'ceilwood', 14)
    L.door(10, 15)
    L.put('shells', 10, 10); L.put('shells', 7, 9); L.put('candy', 13, 13); L.put('jack', 6, 9); L.put('jack2', 14, 9)
    L.put('candles', 6, 14); L.put('zombie', 8, 12); L.put('zombie', 13, 11, 1); L.put('clown', 11, 9, 2)
    # diner (red key behind the counter)
    L.room(19, 5, 33, 15, 'siding2', 'checker', 'ceilwood', 14)
    L.door(26, 15)
    L.block(21, 9, 31, 9, 'wood')
    L.put('key_red', 26, 7); L.put('clown', 22, 7); L.put('clown', 30, 7, 1); L.put('zombie', 23, 12); L.put('zombie', 30, 13)
    L.put('skel', 26, 11, 2); L.put('bullets', 20, 14); L.put('candy', 32, 6); L.put('candles', 20, 6); L.put('candles', 32, 12)
    # alley and the back lot
    L.region(36, 5, 37, 15, 'asphalt', 'sky', 15, out=True)
    L.region(34, 1, 52, 5, 'asphalt', 'sky', 14, out=True)
    L.put('wreck', 41, 3); L.put('trashcan', 36, 8); L.put('trashcan', 37, 12); L.put('trashcan', 50, 2)
    L.put('skel', 44, 2); L.put('skel', 48, 4); L.put('skel', 39, 2, 1); L.put('clown', 51, 4, 1)
    L.put('bullets', 35, 1); L.put('candy', 46, 1); L.put('shells', 52, 5)
    # secret garage off the lot
    L.room(46, 6, 52, 12, 'brick', 'woodfloor', 'ceilwood', 15)
    L.door(49, 6, secret='brick')
    L.put('brew', 48, 9); L.put('armor', 51, 10); L.put('bullets', 47, 11); L.put('jack', 51, 7)
    # hardware store (red door, blue key)
    L.room(5, 24, 21, 34, 'brick', 'woodfloor', 'ceilwood', 15)
    L.door(13, 24, key='red')
    L.block(8, 27, 17, 27, 'wood'); L.block(8, 30, 17, 30, 'wood')
    L.put('key_blue', 18, 32); L.put('witch', 15, 32, 1); L.put('clown', 7, 32); L.put('clown', 18, 26)
    L.put('skel', 10, 29); L.put('skel', 14, 29, 1); L.put('shells', 6, 25); L.put('bucket', 20, 33); L.put('candles', 6, 33)
    # town park
    L.region(23, 25, 42, 37, 'grass', 'sky', 13, out=True)
    L.region(30, 24, 34, 24, 'sidewalk', 'sky', 12, out=True)
    L.block(31, 30, 33, 32, 'lightwall')
    for (x, y) in ((25, 27), (40, 27), (25, 35), (40, 35), (36, 33)):
        L.put('tree', x, y)
    for (x, y) in ((29, 29), (35, 29), (29, 33), (35, 33)):
        L.put('streetlamp', x, y)
    L.put('balloons', 27, 31); L.put('balloons', 38, 31); L.put('patch', 24, 31)
    L.put('zombie', 26, 29); L.put('zombie', 39, 29); L.put('zombie', 33, 36); L.put('clown', 37, 26); L.put('witch', 24, 36, 2)
    L.put('candy', 41, 36); L.put('bullets', 32, 26); L.put('keg', 28, 36)
    # carnival gate at the east end (blue door, exit)
    L.room(45, 14, 52, 25, 'lightwall', 'sawdust', 'ceiltent', 13)
    L.door(45, 19, key='blue')
    L.exitw(52, 19)
    L.put('strongman', 50, 16); L.put('balloons', 50, 23); L.put('bulbs', 48, 19); L.put('clown', 49, 17); L.put('clown', 49, 22)
    L.put('skel', 47, 21, 2); L.put('candy', 46, 24)
    # street dressing (after the rooms so the facades win)
    for x in range(1, 45):
        if L.wall[15, x] and not (L.flag[15, x] & 1):
            L.setw(x, 15, ['brick', 'siding', 'siding2'][x // 5 % 3])
        if L.wall[24, x] and not (L.flag[24, x] & 1):
            L.setw(x, 24, ['siding2', 'brick', 'siding'][x // 6 % 3])
    for x in (7, 13):
        L.setw(x, 15, 'shop')
    for x in (21, 23, 29, 31):
        L.setw(x, 15, 'shop2')
    for x in (3, 34, 41):
        L.setw(x, 15, 'poster')
    for x in (3, 26, 38):
        L.setw(x, 24, 'poster')
    for x in (6, 16, 29, 38):
        L.put('streetlamp', x, 16)
    for x in (11, 21, 42):
        L.put('streetlamp', x, 23)
    L.put('wreck', 20, 19); L.put('hydrant', 14, 23); L.put('hydrant', 33, 16); L.put('trashcan', 3, 16); L.put('trashcan', 43, 23)
    L.put('balloons', 40, 16)
    L.put('zombie', 9, 19); L.put('zombie', 17, 21); L.put('zombie', 30, 18); L.put('zombie', 38, 20, 1)
    L.put('clown', 25, 20); L.put('clown', 42, 18, 1); L.put('skel', 34, 21); L.put('skel', 22, 17, 2)
    L.put('candy', 18, 17); L.put('bullets', 28, 22)
    return L


def level6():
    L = Level('THE MIDWAY', 'Episode 2 - Professor Giggles\' Carnival', 56, 50, sky='sky2', music=7, fog=(12, 8, 20), fogk=15)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'tent')
    # entrance plaza and the midway
    L.region(21, 41, 34, 48, 'dirt', 'sky', 12, out=True)
    L.start = (27.5, 46.5, NORTH)
    L.region(24, 10, 31, 41, 'sawdust', 'sky', 12, out=True)
    L.put('balloons', 22, 42); L.put('balloons', 33, 42); L.put('cotton', 23, 47); L.put('streetlamp', 32, 47)
    L.put('candy', 33, 47); L.put('bullets', 22, 47)
    # game booths lining the midway
    for y in range(12, 40, 4):
        L.setw(23, y, 'booth'); L.setw(32, y, 'booth')
        L.setw(23, y + 1, 'tent2'); L.setw(32, y + 1, 'tent2')
    for y in (14, 22, 30, 38):
        L.put('bulbs', 24, y); L.put('bulbs', 31, y)
    for y in (18, 26, 34):
        L.put('streetlamp', 24, y); L.put('streetlamp', 31, y)
    L.put('strongman', 30, 12); L.put('cotton', 25, 28); L.put('balloons', 30, 36)
    L.put('clown', 26, 36); L.put('clown', 29, 30); L.put('clown', 27, 20, 1); L.put('skel', 25, 24); L.put('skel', 30, 16)
    L.put('zombie', 28, 26, 1); L.put('clown', 26, 13, 2)
    L.put('shells', 25, 33); L.put('candy', 30, 22); L.put('bullets', 25, 17)
    # carousel ring (west) with the red key
    L.region(5, 26, 20, 40, 'sawdust', 'sky', 12, out=True)
    L.region(21, 32, 23, 33, 'sawdust', 'sky', 12, out=True)
    L.block(12, 32, 13, 33, 'lightwall')
    for k, (x, y) in enumerate(((9, 29), (16, 29), (18, 33), (16, 37), (9, 37), (7, 33))):
        L.put('carousel', x, y)
    L.put('key_red', 12, 35); L.put('clown', 7, 28); L.put('clown', 18, 38); L.put('skel', 10, 39); L.put('skel', 17, 27, 1)
    L.put('witch', 6, 39, 1); L.put('bucket', 5, 26); L.put('shells', 20, 40); L.put('keg', 14, 28); L.put('keg', 8, 35)
    # freak show tent (red door): tommy gun and the gold key
    L.room(4, 8, 20, 22, 'tent2', 'sawdust', 'ceiltent', 15)
    L.region(21, 15, 23, 15, 'sawdust', 'sky', 12, out=True)
    L.door(20, 15, key='red')
    for (x, y) in ((7, 11), (11, 11), (15, 11), (7, 18), (15, 18)):
        L.put('cage', x, y)
    L.put('tommy', 11, 15); L.put('key_gold', 6, 20); L.put('bullets', 17, 20); L.put('candles', 5, 9); L.put('candles', 19, 21)
    L.put('skel', 8, 14); L.put('skel', 14, 14); L.put('skel', 12, 19, 1); L.put('witch', 17, 10); L.put('wraith', 9, 20, 2)
    # haunted house ride (east): dark maze with ghosts
    L.room(34, 10, 52, 32, 'siding2', 'woodfloor', 'ceilwood', 18)
    L.region(32, 21, 33, 21, 'sawdust', 'sky', 12, out=True)
    L.door(34, 21)
    for (x0, y0, x1, y1) in ((37, 12, 37, 19), (37, 23, 37, 30), (40, 15, 47, 15), (40, 18, 40, 27), (43, 21, 49, 21),
                             (43, 24, 43, 30), (46, 24, 50, 24), (46, 27, 46, 30), (50, 12, 50, 18)):
        L.block(x0, y0, x1, y1, 'funwall')
    L.put('wraith', 39, 13); L.put('wraith', 45, 19); L.put('wraith', 48, 29, 1); L.put('clown', 42, 28); L.put('skel', 48, 13)
    L.put('zombie', 35, 30); L.put('skel', 51, 22, 2)
    L.put('shells', 49, 14); L.put('bucket', 41, 23); L.put('candles', 35, 11); L.put('candles', 51, 31); L.put('hanging', 44, 17)
    L.put('jack', 38, 31)
    # secret: the ride's maintenance room
    L.room(46, 32, 52, 38, 'wood', 'woodfloor', 'ceilwood', 16)
    L.door(49, 32, secret='siding2')
    L.put('brew', 48, 35); L.put('armor', 51, 36); L.put('pumpkins', 47, 37)
    # funhouse entrance (gold door) and the exit
    L.room(20, 2, 35, 9, 'funwall', 'checker', 'ceiltent', 14)
    L.door(27, 9, key='gold')
    L.exitw(27, 2)
    L.put('clownhead', 22, 4); L.put('clownhead', 33, 4); L.put('balloons', 23, 8); L.put('balloons', 32, 8)
    L.put('clown', 25, 5); L.put('clown', 30, 5); L.put('skel', 27, 7, 1)
    L.put('candy', 21, 7)
    return L


def level7():
    L = Level('THE FUNHOUSE', 'Episode 2 - Laugh Till You Die', 48, 48, sky=None, music=8, fog=(14, 4, 18), fogk=18)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'funwall')
    # entrance
    L.room(19, 40, 29, 46, 'clownwall', 'checker', 'ceiltent', 14)
    L.start = (24.5, 44.5, NORTH)
    L.put('balloons', 20, 41); L.put('balloons', 28, 41); L.put('bullets', 20, 45); L.put('candy', 28, 45)
    L.door(24, 40)
    # hall of mirrors: a grid maze, blue key in the far corner
    L.room(3, 22, 29, 39, 'mirror', 'checker', 'ceiltent', 15)
    for y in range(24, 38, 3):
        for x in range(5, 28, 3):
            if (x * 7 + y * 3) % 5 != 0:
                L.block(x, y, x, y, 'mirror')
    L.region(24, 39, 24, 39, 'checker', 'ceiltent', 15)
    L.put('key_blue', 4, 23); L.put('clown', 10, 26); L.put('clown', 22, 30); L.put('clown', 7, 35, 1); L.put('skel', 16, 33)
    L.put('skel', 25, 25, 1); L.put('wraith', 13, 28, 2); L.put('witch', 4, 37)
    L.put('shells', 28, 23); L.put('candy', 16, 38); L.put('bullets', 4, 30)
    # clown room (east) with the red key
    L.room(30, 8, 44, 24, 'booth', 'woodfloor', 'ceiltent', 14)
    L.room(29, 24, 44, 38, 'clownwall', 'sawdust', 'ceiltent', 15)
    L.door(29, 31)
    L.block(36, 30, 38, 32, 'lightwall')
    L.put('key_red', 37, 26); L.put('clown', 33, 27); L.put('clown', 41, 28); L.put('clown', 34, 36); L.put('clown', 42, 35, 1)
    L.put('skel', 39, 34, 2); L.put('bucket', 43, 37); L.put('balloons', 31, 25); L.put('clownhead', 43, 31); L.put('keg', 32, 34)
    # prize room (red door): pumpkin launcher
    L.door(37, 24, key='red')
    L.block(33, 11, 33, 17, 'lightwall'); L.block(41, 11, 41, 17, 'lightwall')
    L.put('launcher', 37, 14); L.put('pumpkins', 35, 10); L.put('pumpkins', 39, 18); L.put('witch', 31, 9); L.put('witch', 43, 19, 1)
    L.put('skel', 36, 17); L.put('skel', 39, 10, 1); L.put('candy', 43, 9)
    # tunnel of terror: north corridor from the mirror hall (blue door) to the exit
    L.region(7, 18, 8, 21, 'checker', 'ceiltent', 17)
    L.door(7, 22, key='blue')
    L.room(3, 4, 27, 17, 'funwall', 'checker', 'ceiltent', 18)
    L.region(7, 17, 8, 17, 'checker', 'ceiltent', 17)
    for x in (6, 12, 18, 24):
        L.block(x, 7, x, 13, 'clownwall')
    L.exitw(15, 4)
    L.put('wraith', 9, 10); L.put('wraith', 21, 10); L.put('clown', 15, 15); L.put('skel', 26, 5); L.put('skel', 4, 5, 1)
    L.put('zombie', 15, 8, 2); L.put('candles', 4, 16); L.put('candles', 26, 16); L.put('shells', 26, 15); L.put('candy', 4, 15)
    # secret: a hidden mirror leads to a stash
    L.room(27, 2, 34, 7, 'mirror', 'checker', 'ceiltent', 16)
    L.door(27, 5, secret='funwall')
    L.put('brew', 32, 4); L.put('armor', 30, 5); L.put('bullets', 31, 6)
    return L


def level8():
    L = Level('THE BIG TOP', 'Episode 2 - Mister Giggles', 44, 44, sky=None, music=9, fog=(24, 6, 6), fogk=12, flags=1)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'bigtop')
    L.region(2, 2, W - 3, H - 9, 'sawdust', 'ceiltent', 12)
    # round-ish tent: cut the corners
    for k in range(5):
        L.block(2, 2 + k, 6 - k, 2 + k, 'bigtop'); L.block(W - 7 + k, 2 + k, W - 3, 2 + k, 'bigtop')
        L.block(2, H - 10 - k, 6 - k, H - 10 - k, 'bigtop'); L.block(W - 7 + k, H - 10 - k, W - 3, H - 10 - k, 'bigtop')
    # start: backstage alley (south)
    L.room(16, H - 9, 27, H - 2, 'lightwall', 'woodfloor', 'ceilwood', 13)
    L.door(21, H - 9)
    L.start = (21.5, H - 3.5, NORTH)
    L.put('bucket', 17, H - 3); L.put('shells', 26, H - 3); L.put('pumpkins', 17, H - 7); L.put('bullets', 26, H - 7)
    L.put('armor', 21, H - 4)
    # tent poles and bleachers
    for (x, y) in ((12, 12), (31, 12), (12, 27), (31, 27)):
        L.block(x, y, x, y, 'lightwall')
    L.block(8, 18, 9, 21, 'wood'); L.block(34, 18, 35, 21, 'wood')
    L.block(18, 6, 25, 6, 'wood')
    # the ring
    for (x, y) in ((16, 14), (27, 14), (16, 25), (27, 25), (21, 12), (21, 27)):
        L.put('bulbs', x, y)
    L.put('balloons', 5, 10); L.put('balloons', 38, 10); L.put('balloons', 5, 30); L.put('balloons', 38, 30)
    L.put('strongman', 4, 20); L.put('cotton', 39, 20)
    # supplies (respawn in this arena)
    L.put('shells', 4, 6); L.put('bullets', 39, 6); L.put('bucket', 7, 33); L.put('pumpkins', 36, 33); L.put('candy', 21, 9)
    L.put('candy', 21, 31); L.put('shells', 14, 20); L.put('bullets', 29, 20); L.put('keg', 17, 17); L.put('keg', 26, 22)
    # Mister Giggles and his troupe
    L.put('giggles', 21, 10)
    L.put('clown', 10, 8); L.put('clown', 33, 8); L.put('skel', 9, 30); L.put('skel', 34, 30, 1); L.put('clown', 21, 22, 2)
    L.extra_groups = ('clown', 'skel')
    return L


# ================================================================== EPISODE 3: BITE NIGHT

def level9():
    L = Level('BLACKWATER BAYOU', 'Episode 3 - The Swamp Road', 56, 52, sky='sky3', music=10, fog=(10, 16, 14), fogk=15, lightning=1)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'rockmoss')
    L.region(1, 1, W - 2, H - 2, 'water', 'sky', 14, out=True, hurt=True)
    # mud islands
    for (x0, y0, x1, y1) in ((2, 40, 14, 49), (16, 32, 28, 44), (31, 36, 44, 48), (4, 20, 18, 31), (22, 18, 36, 28), (40, 16, 53, 32),
                             (8, 4, 24, 14), (30, 3, 46, 12)):
        L.region(x0, y0, x1, y1, 'mud', 'sky', 13, out=True)
    # boardwalks between them
    for (x0, y0, x1, y1) in ((14, 44, 16, 45), (28, 40, 31, 41), (10, 31, 11, 40), (18, 24, 22, 25), (36, 22, 40, 23),
                             (46, 12, 47, 16), (15, 14, 16, 20), (24, 7, 30, 8), (37, 28, 38, 36)):
        L.region(x0, y0, x1, y1, 'woodfloor', 'sky', 13, out=True)
    # start: the boat dock
    L.start = (4.5, 47.5, NORTH)
    L.put('bullets', 3, 48); L.put('candy', 6, 49); L.put('reeds', 12, 48); L.put('cypress', 9, 42)
    L.put('shotgun', 5, 44)          # on the dock, in plain sight
    # fisherman's shack (shotgun)
    L.room(18, 34, 26, 41, 'swampwood', 'woodfloor', 'ceilwood', 14)
    L.door(22, 41)
    L.put('shells', 22, 37); L.put('bucket', 19, 35); L.put('candles', 25, 35); L.put('zombie', 20, 39); L.put('zombie', 24, 38, 1)
    L.put('bat', 19, 43); L.put('bat', 26, 43); L.put('reeds', 17, 33); L.put('cypress', 27, 42)
    # south-east island: werewolf den
    L.put('wolf', 38, 42); L.put('wolf', 33, 46, 1); L.put('bat', 42, 38); L.put('cypress', 41, 46); L.put('cypress', 32, 38)
    L.put('bucket', 43, 47); L.put('shells', 34, 40); L.put('reeds', 44, 37)
    # west island with the voodoo shack (red key)
    L.room(5, 21, 13, 29, 'swampwood', 'woodfloor', 'ceilwood', 15)
    L.door(10, 29)
    L.put('key_red', 7, 23); L.put('witch', 11, 24); L.put('zombie', 7, 27); L.put('candles', 12, 22); L.put('skulls', 8, 25)
    L.put('cauldron', 9, 23)
    L.put('cypress', 15, 22); L.put('cypress', 16, 29); L.put('bat', 14, 26); L.put('wolf', 16, 25, 2)
    # central island: ruined chapel
    L.room(25, 19, 33, 27, 'castle', 'flagstone', 'sky', 13, out=True)
    L.door(25, 24); L.door(33, 22)
    L.put('tommy', 29, 23); L.put('coffin', 26, 20); L.put('coffin', 32, 20); L.put('vamp', 29, 21); L.put('candelabra', 26, 26)
    L.put('candelabra', 32, 26); L.put('bat', 29, 26, 1)
    L.put('cypress', 23, 19); L.put('cypress', 35, 27); L.put('zombie', 24, 27); L.put('bullets', 34, 19)
    # east island
    L.put('wolf', 46, 20); L.put('wolf', 50, 28); L.put('bat', 44, 25); L.put('bat', 51, 18, 1); L.put('witch', 52, 30, 1)
    L.put('cypress', 42, 18); L.put('cypress', 49, 24); L.put('cypress', 52, 17); L.put('reeds', 41, 30)
    L.put('candy', 52, 31); L.put('shells', 41, 17); L.put('keg', 45, 29)
    # secret: the hermit's hut on the north-east
    L.room(48, 3, 54, 9, 'swampwood', 'woodfloor', 'ceilwood', 15)
    L.door(48, 6, secret='swampwood')
    L.region(47, 6, 47, 6, 'mud', 'sky', 13, out=True)
    L.region(46, 6, 47, 12, 'mud', 'sky', 13, out=True)
    L.put('brew', 51, 5); L.put('armor', 53, 8); L.put('bullets', 50, 8)
    # north: the castle road gate (red door) with the exit
    L.put('cypress', 10, 6); L.put('cypress', 21, 12); L.put('reeds', 13, 13); L.put('wolf', 18, 8); L.put('bat', 12, 10)
    L.put('zombie', 22, 5, 1); L.put('candy', 9, 13)
    L.put('vamp', 38, 6); L.put('wolf', 42, 9, 1); L.put('bat', 33, 9); L.put('cypress', 45, 4); L.put('shells', 31, 4)
    L.room(34, 0, 42, 3, 'castle', 'flagstone', 'ceilcastle', 14)
    L.door(38, 3, key='red')
    L.exitw(38, 0)
    L.walls(0, 0, W - 1, H - 1, 'rockmoss')
    L.exitw(38, 0)
    return brighten(L, 4)


def level10():
    L = Level('THE MAD LAB', 'Episode 3 - Under Castle Hollowfang', 48, 48, sky=None, music=11, fog=(6, 14, 8), fogk=15)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'labwall')
    # entry stairs from the swamp road
    L.room(8, 26, 40, 39, 'labwall', 'labtile', 'ceilcastle', 15)
    L.room(20, 39, 28, 46, 'castle', 'flagstone', 'ceilcastle', 15)
    L.start = (24.5, 44.5, NORTH)
    L.put('candy', 21, 45); L.put('shells', 27, 45); L.put('candelabra', 21, 41); L.put('candelabra', 27, 41)
    L.door(24, 39)
    # specimen hall
    for x in range(11, 39, 4):
        L.put('tank', x, 28); L.put('tank', x, 37)
    L.block(18, 31, 30, 34, 'machine')
    L.put('zombie', 12, 32); L.put('zombie', 36, 32); L.put('skel', 15, 35); L.put('skel', 33, 30); L.put('wolf', 24, 29, 1)
    L.put('zombie', 24, 36, 1); L.put('wolf', 10, 30, 2); L.put('bullets', 9, 38); L.put('candy', 39, 27); L.put('shells', 39, 38)
    # generator room (west): tesla coils, blue key
    L.room(2, 12, 16, 25, 'machine', 'labtile', 'ceilcastle', 16)
    L.door(10, 26 - 1)
    L.region(10, 26, 10, 26, 'labtile', 'ceilcastle', 15)
    for (x, y) in ((5, 15), (13, 15), (5, 22), (13, 22)):
        L.put('tesla', x, y)
    L.put('key_blue', 9, 14); L.put('witch', 4, 18); L.put('skel', 11, 19); L.put('skel', 7, 23, 1); L.put('vamp', 14, 13, 2)
    L.put('bucket', 15, 24); L.put('bullets', 3, 24)
    # operating theatre (east): launcher, red key
    L.room(32, 12, 46, 25, 'labwall', 'labtile', 'ceilcastle', 16)
    L.door(38, 25)
    L.region(38, 26, 38, 26, 'labtile', 'ceilcastle', 15)
    L.block(37, 17, 39, 19, 'machine')
    L.put('launcher', 34, 14); L.put('pumpkins', 44, 14); L.put('key_red', 44, 23); L.put('wolf', 41, 15); L.put('wolf', 35, 22, 1)
    L.put('vamp', 43, 20); L.put('zombie', 33, 18); L.put('tank', 45, 17); L.put('tesla', 33, 24)
    # cells (blue door): prisoners turned skeletons
    L.room(2, 2, 21, 11, 'bars', 'flagstone', 'ceilcastle', 18)
    L.door(9, 11, key='blue')
    L.region(9, 12, 9, 12, 'labtile', 'ceilcastle', 16)
    for x in range(6, 20, 5):
        L.block(x, 2, x, 6, 'castle')
    L.put('skel', 4, 4); L.put('skel', 9, 4); L.put('skel', 14, 4); L.put('skel', 19, 4, 1); L.put('cage', 12, 9)
    L.put('brew', 20, 9); L.put('bullets', 3, 9)
    # secret: behind a lab panel
    L.room(21, 2, 30, 9, 'machine', 'labtile', 'ceilcastle', 16)
    L.door(21, 6, secret='bars')
    L.put('armor', 26, 5); L.put('pumpkins', 28, 7); L.put('candy', 25, 8)
    # red door -> the stairs up into the castle (exit)
    L.room(32, 2, 46, 11, 'castle', 'flagstone', 'ceilcastle', 15)
    L.door(39, 11, key='red')
    L.region(39, 12, 39, 12, 'labtile', 'ceilcastle', 16)
    L.exitw(39, 2)
    L.put('vamp', 35, 5); L.put('vamp', 43, 5, 1); L.put('bat', 39, 7); L.put('bat', 37, 4); L.put('bat', 41, 4, 2)
    L.put('candelabra', 33, 3); L.put('candelabra', 45, 3); L.put('candy', 45, 10)
    return brighten(L, 5)


def level11():
    L = Level('CASTLE HOLLOWFANG', 'Episode 3 - The Count\'s Home', 56, 56, sky='sky3', music=12, fog=(12, 6, 16), fogk=14)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'castle')
    # courtyard (start, open sky)
    L.region(18, 40, 37, 53, 'flagstone', 'sky', 13, out=True)
    L.start = (27.5, 51.5, NORTH)
    L.put('gargoyle', 19, 41); L.put('gargoyle', 36, 41); L.put('brazier', 22, 47); L.put('brazier', 33, 47)
    L.put('bat', 24, 43); L.put('bat', 31, 44); L.put('wolf', 27, 42, 1); L.put('candy', 19, 52); L.put('bullets', 36, 52)
    L.put('shells', 27, 49)
    # great hall
    L.room(14, 22, 41, 39, 'curtain', 'marble', 'ceilcastle', 15)
    L.door(27, 39)
    L.region(16, 24, 39, 37, 'redcarpet', 'ceilcastle', 15)
    for (x, y) in ((18, 26), (37, 26), (18, 35), (37, 35)):
        L.block(x, y, x, y, 'castle')
    for x in (14, 41):
        for y in (26, 34):
            L.setw(x, y, 'tapestry')
    for x in (20, 26, 29, 35):
        L.setw(x, 22, 'window')
    L.put('candelabra', 16, 24); L.put('candelabra', 39, 24); L.put('candelabra', 16, 37); L.put('candelabra', 39, 37)
    L.put('knight', 21, 23); L.put('knight', 34, 23)
    L.put('vamp', 22, 30); L.put('vamp', 33, 30); L.put('skel', 27, 26); L.put('skel', 20, 34, 1); L.put('wolf', 35, 34)
    L.put('vamp', 27, 33, 2); L.put('bucket', 39, 30); L.put('shells', 16, 30)
    # west wing: library-crypt with coffins (red key)
    L.room(2, 22, 14, 39, 'castle', 'flagstone', 'ceilcastle', 17)
    L.door(14, 30)
    for y in (25, 29, 33, 37):
        L.put('coffin', 4, y); L.put('coffin', 11, y)
    L.put('key_red', 7, 24); L.put('vamp', 7, 30); L.put('skel', 5, 35); L.put('skel', 10, 27); L.put('bat', 8, 36, 1)
    L.put('candles', 3, 23); L.put('bullets', 12, 38)
    # east wing: armory (red door) -> blue key
    L.room(41, 22, 53, 39, 'castle', 'marble', 'ceilcastle', 16)
    L.door(41, 30, key='red')
    for y in (24, 28, 32, 36):
        L.put('knight', 52, y)
    L.put('key_blue', 51, 38); L.put('wolf', 46, 26); L.put('wolf', 47, 35); L.put('skel', 50, 30, 1); L.put('witch', 44, 37)
    L.put('pumpkins', 43, 23); L.put('candy', 44, 33)
    # north gallery (blue door) -> gold key
    L.room(2, 10, 14, 21, 'castle', 'marble', 'ceilcastle', 16)
    L.room(14, 10, 41, 22, 'tapestry', 'redcarpet', 'ceilcastle', 16)
    L.door(27, 22, key='blue')
    for x in (20, 26, 29, 35):
        L.setw(x, 22, 'window')
    for x in range(17, 40, 5):
        L.block(x, 13, x, 18, 'castle')
    for x in (15, 40):
        L.put('candelabra', x, 11)
    L.put('key_gold', 39, 19); L.put('vamp', 19, 15); L.put('vamp', 35, 15); L.put('bat', 24, 12); L.put('bat', 29, 19)
    L.put('wolf', 31, 12, 1); L.put('skel', 22, 19, 2); L.put('bucket', 16, 19); L.put('shells', 37, 11)
    # secret: behind a tapestry
    L.door(14, 15, secret='tapestry')
    L.put('brew', 6, 14); L.put('armor', 9, 18); L.put('bullets', 4, 19); L.put('candelabra', 11, 11)
    # gold door -> the tower stairs (exit)
    L.room(20, 2, 35, 10, 'castle', 'flagstone', 'ceilcastle', 14)
    L.door(27, 10, key='gold')
    L.exitw(27, 2)
    L.put('gargoyle', 21, 3); L.put('gargoyle', 34, 3); L.put('vamp', 24, 6); L.put('vamp', 31, 6, 1); L.put('bat', 27, 4)
    L.put('candy', 34, 8)
    return brighten(L, 3)


def level12():
    L = Level('THE COUNT\'S THRONE', 'Episode 3 - Count Hollowfang', 44, 44, sky='sky3', music=13, fog=(14, 4, 18), fogk=12, lightning=1,
              flags=1)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'castle')
    L.region(2, 2, W - 3, H - 9, 'marble', 'sky', 13, out=True)
    # start: the tower stair (south)
    L.room(16, H - 9, 27, H - 2, 'castle', 'flagstone', 'ceilcastle', 13)
    L.door(21, H - 9)
    L.start = (21.5, H - 3.5, NORTH)
    L.put('bucket', 17, H - 3); L.put('shells', 26, H - 3); L.put('pumpkins', 17, H - 7); L.put('bullets', 26, H - 7)
    L.put('armor', 21, H - 4)
    # throne dais (north), pillars, braziers
    L.region(15, 2, 28, 7, 'redcarpet', 'sky', 12, out=True)
    L.block(20, 2, 23, 3, 'curtain')
    for (x, y) in ((8, 10), (35, 10), (8, 26), (35, 26), (15, 18), (28, 18)):
        L.block(x, y, x, y, 'castle')
    for (x, y) in ((6, 6), (37, 6), (6, 31), (37, 31), (21, 14), (21, 24)):
        L.put('brazier', x, y)
    for (x, y) in ((4, 15), (39, 15), (4, 22), (39, 22)):
        L.put('coffin', x, y)
    L.put('gargoyle', 13, 3); L.put('gargoyle', 30, 3)
    # supplies (respawn)
    L.put('shells', 3, 3); L.put('bullets', 40, 3); L.put('bucket', 3, 33); L.put('pumpkins', 40, 33); L.put('candy', 12, 18)
    L.put('candy', 31, 18); L.put('shells', 21, 30); L.put('bullets', 21, 10); L.put('keg', 10, 30); L.put('keg', 33, 30)
    # Count Hollowfang and his brood
    L.put('count', 21, 6)
    L.put('bat', 10, 8); L.put('bat', 33, 8); L.put('vamp', 6, 20); L.put('vamp', 37, 20, 1); L.put('wolf', 21, 28, 2)
    L.extra_groups = ('bat', 'wolf')
    return brighten(L, 3)


# ================================================================== cutscene sets

def cut1():
    """Dawn on Butch's porch: house front to the north, porch, front yard."""
    L = Level('PORCH', '', 24, 18, sky='sky4', music=16, fog=(60, 40, 40), fogk=8)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'hedge')
    L.region(1, 1, W - 2, H - 2, 'grass', 'sky', 10, out=True)
    L.block(4, 1, 19, 5, 'siding')
    for x in (7, 16):
        L.setw(x, 5, 'window')
    L.setw(11, 5, 'door'); L.setw(12, 5, 'door')
    L.region(5, 6, 18, 8, 'woodfloor', 'sky', 10, out=True)
    L.region(10, 9, 13, 16, 'dirt', 'sky', 10, out=True)
    L.put('patch', 4, 10); L.put('patch', 19, 10); L.put('tree', 2, 3); L.put('tree', 21, 4); L.put('jack', 6, 7); L.put('jack2', 17, 7)
    L.start = (11.5, 15.0, NORTH)
    L.extra_groups = ('butch', 'cs', 'cpbutch', 'cppk', 'cpkid', 'cpgore')
    return L


def cut2():
    """The Big Top ring after the show."""
    L = Level('RING', '', 24, 20, sky=None, music=16, fog=(20, 8, 8), fogk=10)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'bigtop')
    L.region(1, 1, W - 2, H - 2, 'sawdust', 'ceiltent', 11)
    L.block(1, 1, 22, 2, 'lightwall')
    L.put('bulbs', 8, 4); L.put('bulbs', 15, 4); L.put('balloons', 3, 4); L.put('balloons', 20, 4); L.put('strongman', 19, 5)
    L.start = (11.5, 16.0, NORTH)
    L.extra_groups = ('butch', 'cs', 'giggles', 'clown', 'cpbutch', 'cpgig', 'cpgore')
    return L


def cut3():
    """Castle rooftop under the moon."""
    L = Level('ROOF', '', 24, 20, sky='sky3', music=16, fog=(14, 6, 20), fogk=10)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'castle')
    L.region(1, 1, W - 2, H - 2, 'marble', 'sky', 11, out=True)
    L.put('gargoyle', 3, 3); L.put('gargoyle', 20, 3); L.put('brazier', 6, 8); L.put('brazier', 17, 8)
    L.start = (11.5, 16.0, NORTH)
    L.extra_groups = ('butch', 'cs', 'bat', 'cpbutch', 'cpcount', 'cpgore')
    return L


LEVELS2 = [level5, level6, level7, level8, level9, level10, level11, level12]
CUTS = [cut1, cut2, cut3]
