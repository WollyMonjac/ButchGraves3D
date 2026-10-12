"""Episode 4: VOLTAGE OF THE DAMNED (levels 13..16) and the ending cutscene set (level 104).

New gadgets (see gen_levels.Level): teleporter pads (tele), shifting walls (shiftw: sink when a lever is pulled) and
shifting floors (shiftf: a wall rises there when a lever is pulled), levers (lever), conveyor belts (conv_n/s/e/w flats)
and shock floors (shock flat: deadly every few seconds)."""
import random
import numpy as np
from gen_levels import Level, NORTH, EAST, SOUTH, WEST, WALLS, FLATS


def pillar_maze(L, ox, oy, ni, nj, seed, wall='server', skip=(), loops=0.12, floor=None):
    """Carve a 2-wide-corridor maze: nodes are 2x2 open cells at (ox + 4i, oy + 4j), pillars of `wall` between them.
    Nodes in `skip` are left out of the maze (to be connected by hand). Returns the set of open edges."""
    rnd = random.Random(seed)
    nodes = [(i, j) for i in range(ni) for j in range(nj) if (i, j) not in skip]
    start = nodes[0]
    seen = {start}
    stack = [start]
    edges = set()
    while stack:
        i, j = stack[-1]
        nb = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if (i + di, j + dj) in nodes and (i + di, j + dj) not in seen]
        if not nb:
            stack.pop()
            continue
        n = rnd.choice(nb)
        edges.add(frozenset(((i, j), n)))
        seen.add(n)
        stack.append(n)
    # a few extra openings so it is not a perfect tree (loops let you outrun spiders)
    for (i, j) in nodes:
        for di, dj in ((1, 0), (0, 1)):
            n = (i + di, j + dj)
            if n in nodes and rnd.random() < loops:
                edges.add(frozenset(((i, j), n)))
    # paint: everything a wall, then open nodes and edges
    x1, y1 = ox + 4 * (ni - 1) + 1, oy + 4 * (nj - 1) + 1
    L.block(ox, oy, x1, y1, wall)
    fl = floor or L.flr[oy, ox]
    for (i, j) in nodes:
        x, y = ox + 4 * i, oy + 4 * j
        L.region(x, y, x + 1, y + 1, *fl)
    for e in edges:
        (i, j), (k, l) = sorted(e)
        x, y = ox + 4 * i, oy + 4 * j
        if k > i:
            L.region(x + 2, y, x + 3, y + 1, *fl)
        else:
            L.region(x, y + 2, x + 1, y + 3, *fl)
    return edges


def node(ox, oy, i, j):
    return ox + 4 * i, oy + 4 * j


# ================================================================== LEVEL 13: Neon Graveyard

def level13():
    L = Level('NEON GRAVEYARD', 'Episode 4 - Neo-Hollow, 2099', 56, 48, sky='sky5', music=17, fog=(16, 6, 26), fogk=15, lightning=0)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'techwall2')
    # start plaza (south-west) with the shotgun right in front of you
    L.region(2, 38, 12, 45, 'plate', 'sky', 12, out=True)
    L.start = (5.5, 43.5, NORTH)
    L.put('shotgun', 5, 40); L.put('shells', 9, 40); L.put('bullets', 3, 44); L.put('neonjack', 2, 38); L.put('neonjack', 12, 38)
    L.put('crate', 11, 44); L.put('crate', 11, 45); L.put('candy', 10, 42)
    # the holo-cemetery
    L.region(2, 18, 30, 36, 'grass', 'sky', 13, out=True)
    L.block(2, 37, 30, 37, 'neonwall')
    L.region(6, 37, 8, 37, 'plate', 'sky', 12, out=True)
    for x in (4, 7, 10, 24, 27):
        for y in (20, 23, 33):
            L.put('holotomb', x, y)
    for (x, y) in ((3, 29), (29, 19), (29, 35), (21, 19)):
        L.put('neonjack', x, y)
    L.put('crate', 15, 34); L.put('toxic', 22, 34); L.put('toxic', 23, 35); L.put('keg', 9, 28)
    L.put('spider', 6, 26); L.put('spider', 9, 31, 1); L.put('spider', 26, 30); L.put('spider', 25, 27, 2)
    L.put('frank', 22, 22); L.put('drone', 8, 21); L.put('drone', 26, 31, 1); L.put('cyborg', 4, 32, 2); L.put('frank', 28, 26, 1)
    L.put('candy', 3, 19); L.put('bullets', 29, 30); L.put('shells', 13, 35); L.put('candy', 20, 35); L.put('bucket', 29, 21)
    # the tech mausoleum (red key)
    L.room(12, 23, 20, 31, 'circuit', 'plate', 'techceil', 14)
    L.door(16, 31)
    L.put('capsule', 13, 24); L.put('capsule', 19, 24); L.put('terminal', 16, 24); L.put('key_red', 16, 26)
    L.put('frank', 14, 28); L.put('cyborg', 18, 28, 1); L.put('spider', 16, 29, 2); L.put('shells', 13, 30); L.put('candy', 19, 30)
    # maintenance tunnel behind the cemetery wall (secret)
    L.room(13, 37, 23, 45, 'techwall2', 'grate', 'darkceil', 16)
    L.door(18, 37, secret='techwall2')
    L.put('armor', 18, 41); L.put('pumpkins', 15, 43); L.put('bucket', 21, 43); L.put('cables', 14, 39); L.put('cables', 22, 39)
    L.put('spider', 16, 40, 1); L.put('spider', 20, 44, 2)
    # red door into the factory yard
    L.region(31, 27, 31, 27, 'plate', 'sky', 13, out=True)
    L.region(33, 27, 33, 27, 'plate', 'sky', 13, out=True)
    L.door(32, 27, key='red')
    L.region(34, 18, 52, 36, 'plate', 'sky', 13, out=True)
    L.block(34, 37, 52, 37, 'hazard')
    for (x, y) in ((38, 21), (39, 21), (38, 22), (47, 30), (48, 30), (47, 31)):
        L.put('crate', x, y)
    for (x, y) in ((42, 33), (43, 33), (44, 34), (36, 25), (51, 22)):
        L.put('toxic', x, y)
    L.put('robotarm', 41, 26); L.put('robotarm', 46, 22); L.put('neonjack', 34, 18); L.put('neonjack', 52, 18)
    L.put('cyborg', 44, 26); L.put('cyborg', 37, 33, 1); L.put('frank', 49, 25); L.put('drone', 40, 29); L.put('drone', 50, 33, 1)
    L.put('spider', 45, 20); L.put('spider', 36, 30, 2); L.put('drone', 44, 19, 2)
    L.put('candy', 35, 35); L.put('bullets', 51, 35); L.put('shells', 35, 19); L.put('candy', 51, 19)
    # teleporter from the yard to the walled-off old cemetery (north-west) and back
    L.tele(50, 34, 0, 6, 13, NORTH)
    L.block(2, 16, 30, 17, 'neonwall')
    L.region(2, 2, 24, 15, 'grass', 'sky', 14, out=True)
    L.block(25, 2, 30, 15, 'techwall2')
    L.room(9, 2, 15, 7, 'crypt', 'flagstone', 'ceilstone', 15)
    L.door(12, 7)
    L.put('key_blue', 12, 4); L.put('candles', 10, 3); L.put('candles', 14, 3); L.put('frank', 12, 5, 1)
    for (x, y) in ((4, 4), (4, 8), (18, 4), (18, 8), (21, 11), (8, 11)):
        L.put('tomb' if (x + y) % 2 else 'tomb2', x, y)
    L.put('tree', 22, 3); L.put('tree', 3, 14); L.put('jack', 6, 6); L.put('jack2', 20, 13)
    L.put('spider', 6, 9); L.put('spider', 16, 11); L.put('spider', 20, 6, 1); L.put('drone', 10, 12); L.put('frank', 19, 9)
    L.put('cyborg', 3, 10, 2); L.put('bullets', 23, 14); L.put('candy', 2, 2); L.put('shells', 23, 2)
    L.tele(22, 14, 1, 47, 34, WEST)
    # stash behind the old cemetery's east wall (secret)
    L.room(25, 3, 30, 8, 'techwall2', 'plate', 'techceil', 15)
    L.door(25, 5, secret='techwall2')
    L.put('tommy', 28, 5); L.put('bullets', 29, 7); L.put('candy', 27, 7)
    # blue door, then the shock-floor gauntlet up to the Frankentech gate
    L.region(40, 6, 46, 16, 'shock', 'techceil', 14)
    for (x, y) in ((41, 13), (45, 10), (41, 7), (43, 15)):
        L.region(x, y, x, y, 'plate', 'techceil', 14)
    L.walls(39, 5, 47, 17, 'hazard')
    L.door(43, 17, key='blue')
    L.put('candy', 45, 10); L.put('drone', 43, 9, 1)
    L.room(38, 1, 48, 5, 'techwall', 'plate', 'techceil', 13)
    L.region(43, 5, 43, 5, 'plate', 'techceil', 13)
    L.exitw(43, 1)
    L.put('frank', 40, 3); L.put('frank', 46, 3, 2); L.put('terminal', 39, 2); L.put('terminal', 47, 2)
    L.walls(0, 0, W - 1, H - 1, 'techwall2')
    L.exitw(43, 1)
    return L


# ================================================================== LEVEL 14: The Assembly Line

def level14():
    L = Level('THE ASSEMBLY LINE', 'Episode 4 - Frankentech Industries', 56, 48, sky=None, music=18, fog=(10, 8, 16), fogk=15)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'techwall')
    # loading dock (start)
    L.region(2, 40, 14, 46, 'plate', 'techceil', 14)
    L.start = (8.5, 44.5, NORTH)
    L.put('crate', 2, 46); L.put('crate', 3, 46); L.put('crate', 2, 45); L.put('crate', 14, 41); L.put('shells', 12, 45)
    L.put('bullets', 4, 41); L.put('toxic', 13, 46)
    L.region(7, 38, 9, 39, 'plate', 'techceil', 14)
    # hall 1: three belts carrying parts north
    L.region(2, 20, 26, 37, 'plate', 'techceil', 14)
    for x0 in (5, 12, 19):
        L.region(x0, 21, x0 + 1, 36, 'conv_n', 'techceil', 14)
    for (x, y) in ((4, 24), (7, 30), (11, 26), (14, 33), (18, 23), (21, 29)):
        L.put('robotarm', x, y)
    for (x, y) in ((3, 35), (24, 21), (24, 36), (10, 21)):
        L.put('crate', x, y)
    L.put('toxic', 16, 25); L.put('toxic', 9, 34); L.put('capsule', 25, 28); L.put('capsule', 25, 32)
    L.put('frank', 9, 27); L.put('cyborg', 16, 30); L.put('cyborg', 23, 24, 1); L.put('spider', 3, 22); L.put('spider', 22, 34, 1)
    L.put('drone', 15, 22, 1); L.put('frank', 22, 26, 2)
    L.put('candy', 2, 30); L.put('shells', 16, 36); L.put('bullets', 24, 33); L.put('candy', 10, 36)
    # sorting room (north-west): rows of belts shoving you toward the shock strip; red key on the platform
    L.region(14, 17, 14, 19, 'plate', 'techceil', 14)
    L.door(14, 18)
    L.region(2, 4, 26, 16, 'plate', 'techceil', 14)
    for y, d in ((6, 'conv_e'), (7, 'conv_e'), (8, 'conv_w'), (9, 'conv_w'), (11, 'conv_e'), (12, 'conv_e'), (13, 'conv_w'), (14, 'conv_e')):
        L.region(4, y, 21, y, d, 'techceil', 14)
    L.region(10, 10, 14, 10, 'plate', 'techceil', 14)
    L.region(22, 5, 25, 15, 'shock', 'techceil', 14)
    L.put('key_red', 12, 10)
    L.put('drone', 8, 5); L.put('drone', 18, 15, 1); L.put('spider', 6, 10); L.put('spider', 17, 10); L.put('spider', 12, 13, 2)
    L.put('frank', 3, 15); L.put('terminal', 2, 4); L.put('terminal', 3, 4); L.put('shells', 26, 4); L.put('bucket', 2, 10)
    # red door into the paint shop: a belt loop around the walls, spray booths, toxic waste
    L.door(27, 30, key='red')
    L.region(28, 20, 53, 40, 'grate', 'darkceil', 15)
    L.region(29, 21, 52, 21, 'conv_e', 'darkceil', 15)
    L.region(52, 21, 52, 39, 'conv_s', 'darkceil', 15)
    L.region(29, 39, 52, 39, 'conv_w', 'darkceil', 15)
    L.region(29, 22, 29, 39, 'conv_n', 'darkceil', 15)
    L.room(40, 26, 46, 32, 'hazard', 'plate', 'techceil', 15)
    L.door(43, 32)
    L.put('key_blue', 43, 28); L.put('cyborg', 41, 30); L.put('frank', 45, 28, 1); L.put('candy', 45, 31)
    L.room(32, 24, 36, 28, 'glasstank', 'plate', 'techceil', 15)
    L.door(34, 28)
    L.put('bucket', 34, 26); L.put('drone', 33, 25, 2)
    for (x, y) in ((38, 35), (39, 36), (38, 37), (48, 24), (49, 25), (31, 32)):
        L.put('toxic', x, y)
    for (x, y) in ((48, 35), (48, 36), (35, 33), (44, 36)):
        L.put('crate', x, y)
    L.put('tommy', 33, 36); L.put('bullets', 35, 37)
    L.put('frank', 49, 30); L.put('cyborg', 37, 31); L.put('cyborg', 46, 35, 1); L.put('drone', 40, 23); L.put('drone', 50, 37, 1)
    L.put('spider', 31, 23); L.put('spider', 50, 23); L.put('spider', 31, 37, 2); L.put('drone', 36, 22, 2)
    L.put('shells', 51, 30); L.put('candy', 30, 30); L.put('pumpkins', 47, 38)
    # secret: paint store room off the south wall
    L.room(44, 41, 52, 46, 'techwall', 'plate', 'techceil', 15)
    L.door(48, 41, secret='techwall')
    L.region(48, 40, 48, 40, 'grate', 'darkceil', 15)
    L.put('armor', 46, 44); L.put('brew', 50, 44); L.put('pumpkins', 48, 45)
    # blue door, the control corridor (the lever drops the barrier ahead... and raises walls behind you, and opens the robot lockers)
    L.region(38, 8, 42, 18, 'plate', 'techceil', 15)
    L.region(40, 19, 40, 19, 'plate', 'techceil', 15)
    L.door(40, 19, key='blue')
    L.lever(37, 13)
    for x in range(38, 43):
        L.shiftw(x, 9)
        L.shiftf(x, 17)
    for (x0, y0) in ((33, 11), (44, 11), (33, 15), (44, 15)):         # robot lockers
        L.region(x0, y0, x0 + 2, y0 + 1, 'plate', 'techceil', 16)
        for xx in ((36, 37) if x0 < 38 else (43,)):
            L.region(xx, y0, xx, y0 + 1, 'plate', 'techceil', 16)
            L.shiftw(xx, y0); L.shiftw(xx, y0 + 1)
    L.put('frank', 34, 11); L.put('cyborg', 45, 12); L.put('cyborg', 34, 16, 1); L.put('frank', 45, 15, 1)
    L.put('candy', 38, 14); L.put('shells', 42, 12)
    # exit lift
    L.region(38, 2, 42, 8, 'plate', 'techceil', 13)
    L.exitw(40, 1)
    L.put('terminal', 38, 2); L.put('terminal', 42, 2); L.put('drone', 40, 4, 1)
    L.walls(0, 0, W - 1, H - 1, 'techwall')
    L.exitw(40, 1)
    return L


# ================================================================== LEVEL 15: The Circuit Maze

def level15():
    L = Level('THE CIRCUIT MAZE', 'Episode 4 - The Mainframe', 48, 40, sky=None, music=19, fog=(4, 8, 18), fogk=16)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'techwall2')
    DARK = ('grate', 'darkceil', 16)
    # Z0: start hub (south-west) with a lever
    L.region(1, 29, 11, 38, 'plate', 'techceil', 14)
    L.start = (3.5, 37.5, NORTH)
    L.block(5, 31, 6, 32, 'server'); L.block(8, 35, 9, 36, 'monitors')
    L.lever(0, 34)
    L.put('shells', 2, 30); L.put('bullets', 10, 37); L.put('candy', 10, 30); L.put('terminal', 11, 33)
    # Z1: the west server maze (red key in the north-west node, behind a shifting wall)
    ox, oy = 1, 1
    pillar_maze(L, ox, oy, 5, 7, seed=1513, skip={(0, 0)}, floor=DARK)
    L.region(1, 1, 2, 2, *DARK)
    L.shiftw(3, 1); L.shiftw(4, 1); L.shiftw(3, 2); L.shiftw(4, 2)
    L.region(19, 1, 20, 26, *DARK); L.block(19, 1, 20, 26, 'server')
    L.put('key_red', 1, 1)
    L.lever(0, 21)
    # Z0 <-> Z1: open now, closes when a lever is pulled
    L.region(1, 27, 2, 28, *DARK)
    for (x, y) in ((1, 28), (2, 28)):
        L.shiftf(x, y)
    # Z1 -> Z2: opens when a lever is pulled
    for (x, y) in ((19, 13), (20, 13), (19, 14), (20, 14)):
        L.shiftw(x, y)
    # Z2: the core: shock floor around a reactor column, teleporter to the east stacks, launcher
    L.region(21, 12, 33, 27, 'plate', 'techceil', 14)
    L.region(24, 16, 30, 23, 'shock', 'techceil', 14)
    L.block(26, 18, 28, 20, 'glasstank')
    L.region(27, 21, 27, 21, 'plate', 'techceil', 14)
    L.put('armor', 27, 22)
    L.lever(34, 20)
    L.put('launcher', 22, 26); L.put('pumpkins', 23, 26); L.put('capsule', 21, 12); L.put('capsule', 33, 12)
    L.put('terminal', 33, 27); L.put('candy', 21, 20)
    L.tele(32, 14, 0, 37, 14, EAST)
    # Z2 <-> Z0: long dark corridor along the south, open only in the first state
    L.region(21, 28, 22, 37, *DARK)
    L.region(12, 36, 20, 37, *DARK)
    L.shiftf(21, 29); L.shiftf(22, 29)
    # trap room (only reachable by teleporter): spiders! and a pad home
    L.region(14, 29, 19, 34, 'plate', 'techceil', 15)
    L.tele(16, 31, 1, 4, 30, EAST)
    # Z3: east stacks
    pillar_maze(L, 36, 13, 3, 7, seed=1517, floor=('grate', 'darkceil', 15))
    L.lever(46, 30)
    L.tele(44, 13, 2, 31, 16, WEST)
    # blue key room behind the red door
    L.room(23, 29, 35, 38, 'circuit', 'plate', 'techceil', 15)
    L.door(35, 33, key='red')
    L.put('key_blue', 25, 37); L.put('capsule', 24, 30); L.put('capsule', 33, 30); L.put('bucket', 29, 37)
    # Z2 -> Z4: north passage with a shifting floor and the blue door
    L.region(30, 5, 31, 11, *DARK)
    L.region(32, 5, 34, 6, *DARK)
    L.shiftf(30, 10); L.shiftf(31, 10)
    L.region(36, 1, 46, 10, 'plate', 'techceil', 13)
    L.door(35, 5, key='blue')
    L.exitw(41, 0)
    L.put('terminal', 36, 1); L.put('terminal', 46, 1); L.put('capsule', 36, 10); L.put('capsule', 46, 10)
    # a dead end in the west maze holds a teleporter... into the spider room
    tx, ty = node(1, 1, 2, 6)
    L.tele(tx, ty, 3, 18, 33, WEST)
    # monsters
    for (i, j, kind, sk) in ((1, 1, 'spider', 0), (3, 1, 'cyborg', 0), (2, 3, 'spider', 0), (4, 4, 'frank', 0), (0, 4, 'spider', 1),
                             (3, 5, 'drone', 0), (1, 5, 'cyborg', 1), (4, 1, 'spider', 2), (0, 2, 'spider', 2), (1, 0, 'frank', 1)):
        x, y = node(1, 1, i, j)
        L.put(kind, x + 1, y)
    L.put('frank', 23, 14); L.put('drone', 31, 25); L.put('cyborg', 22, 22, 1); L.put('drone', 24, 13, 1); L.put('frank', 31, 21, 2)
    for (x, y, sk) in ((14, 29, 0), (19, 29, 0), (14, 34, 0), (19, 34, 1), (17, 29, 1), (15, 32, 2)):
        L.put('spider', x, y, sk)
    L.put('bucket', 18, 34)
    for (i, j, kind, sk) in ((1, 1, 'drone', 0), (0, 3, 'spider', 0), (2, 3, 'cyborg', 0), (1, 5, 'frank', 0), (2, 6, 'spider', 1),
                             (0, 6, 'drone', 1), (2, 2, 'cyborg', 2)):
        x, y = node(36, 13, i, j)
        L.put(kind, x + 1, y)
    L.put('frank', 28, 33); L.put('cyborg', 31, 35, 1); L.put('spider', 26, 32, 2)
    L.put('frank', 38, 4); L.put('drone', 44, 6); L.put('cyborg', 41, 8, 1)
    # supplies tucked into maze corners
    for (ox_, oy_, i, j, kind) in ((1, 1, 4, 0, 'shells'), (1, 1, 0, 6, 'candy'), (1, 1, 4, 6, 'bullets'), (1, 1, 2, 2, 'candy'),
                                   (36, 13, 2, 0, 'shells'), (36, 13, 0, 6, 'bucket'), (36, 13, 2, 4, 'bullets'), (36, 13, 1, 2, 'candy')):
        x, y = node(ox_, oy_, i, j)
        L.put(kind, x, y + 1)
    L.walls(0, 0, W - 1, H - 1, 'techwall2')
    L.lever(0, 34); L.lever(0, 21); L.lever(46, 30)
    L.exitw(41, 0)
    return L


# ================================================================== LEVEL 16: Frankenstein Prime

def level16():
    L = Level('FRANKENSTEIN PRIME', 'Episode 4 - The Reactor', 44, 44, sky=None, music=20, fog=(4, 14, 8), fogk=12, flags=1)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'techwall')
    L.region(2, 2, W - 3, H - 10, 'plate', 'techceil', 13)
    # a moving walkway around the arena edge (clockwise)
    L.region(2, 2, W - 4, 2, 'conv_e', 'techceil', 13)
    L.region(W - 3, 2, W - 3, H - 11, 'conv_s', 'techceil', 13)
    L.region(3, H - 10, W - 3, H - 10, 'conv_w', 'techceil', 13)
    L.region(2, 3, 2, H - 10, 'conv_n', 'techceil', 13)
    # the reactor in the middle, ringed by a shock floor
    L.region(18, 14, 25, 21, 'shock', 'techceil', 12)
    L.block(20, 16, 23, 19, 'glasstank')
    # cover pillars
    for (x, y) in ((8, 8), (35, 8), (8, 27), (35, 27), (14, 31), (29, 31)):
        L.block(x, y, x + 1, y + 1, 'server')
    # start corridor (south)
    L.room(16, H - 9, 27, H - 2, 'techwall', 'grate', 'darkceil', 13)
    L.door(21, H - 9)
    L.start = (21.5, H - 3.5, NORTH)
    L.put('bucket', 17, H - 3); L.put('shells', 26, H - 3); L.put('pumpkins', 17, H - 7); L.put('bullets', 26, H - 7)
    L.put('armor', 21, H - 4); L.put('launcher', 24, H - 5)
    # supplies (respawn)
    L.put('shells', 4, 4); L.put('bullets', 39, 4); L.put('bucket', 4, 33); L.put('pumpkins', 39, 33); L.put('candy', 12, 18)
    L.put('candy', 31, 18); L.put('shells', 21, 29); L.put('bullets', 21, 7); L.put('toxic', 10, 30); L.put('toxic', 33, 30)
    L.put('toxic', 10, 6); L.put('toxic', 33, 6)
    for (x, y) in ((5, 12), (38, 12), (5, 24), (38, 24)):
        L.put('capsule', x, y)
    L.put('robotarm', 15, 5); L.put('robotarm', 28, 5); L.put('terminal', 21, 3); L.put('terminal', 22, 3)
    # Frankenstein Prime and its little helpers
    L.put('prime', 21, 9)
    L.put('spider', 10, 10); L.put('spider', 33, 10); L.put('drone', 21, 26, 1); L.put('drone', 6, 20, 2)
    L.extra_groups = ('spider', 'drone')
    return L


# ================================================================== cutscene set: reactor (west) + Butch's porch (east)

def cut4():
    L = Level('REACTOR', '', 48, 18, sky='sky4', music=16, fog=(10, 18, 10), fogk=9)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'techwall')
    # reactor hall
    L.region(1, 1, 22, 16, 'plate', 'techceil', 11)
    L.block(1, 1, 22, 2, 'machine')
    L.block(9, 3, 9, 3, 'glasstank'); L.block(14, 3, 14, 3, 'glasstank')
    L.put('tesla', 3, 5); L.put('tesla', 20, 5); L.put('capsule', 4, 10); L.put('capsule', 19, 12); L.put('cables', 7, 6)
    L.put('cables', 17, 7); L.put('terminal', 2, 14)
    # Butch's porch at dawn (same layout as the episode 1 ending, 24 cells east)
    L.block(24, 0, 47, 17, 'hedge')
    L.region(25, 1, 46, 16, 'grass', 'sky', 10, out=True)
    L.block(28, 1, 43, 5, 'siding')
    for x in (31, 40):
        L.setw(x, 5, 'window')
    L.setw(35, 5, 'door'); L.setw(36, 5, 'door')
    L.region(29, 6, 42, 8, 'woodfloor', 'sky', 10, out=True)
    L.region(34, 9, 37, 16, 'dirt', 'sky', 10, out=True)
    L.put('patch', 28, 10); L.put('patch', 43, 10); L.put('tree', 26, 3); L.put('tree', 45, 4); L.put('jack', 30, 7); L.put('jack2', 41, 7)
    L.walls(0, 0, W - 1, H - 1, 'techwall')
    L.start = (11.5, 14.0, NORTH)
    L.extra_groups = ('butch', 'cs', 'cpbutch', 'cpdoc', 'cppk', 'cpgore')
    return L


LEVELS3 = [level13, level14, level15, level16]
CUTS3 = [cut4]
