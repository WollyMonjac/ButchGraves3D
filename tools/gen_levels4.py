"""Episode 5: CURSE OF THE JADE SKULL (levels 17..20) and the ending cutscene set (level 105).

New gadgets (see gen_levels.Level): pits (jump them; sprint for the 2-wide ones), pressure plates ('pplate' flat) with dart
traps (darter), spike floors ('spikes' flat: up a while, down a while), the river ('river' flat: wading is slow), the golden
idol (the gold key of the temple, and the level trigger), boulders (drop and roll when the level triggers), trigger walls
(trigwall: flip when the level triggers) and ambushers (put(..., ambush=True): appear when the level triggers).
Level flags: 1 respawning pickups (boss arena), 2 the radio (static when monsters are near), 4 the Other World (the red key
sounds the siren and the town rusts)."""
from gen_levels import Level, NORTH, EAST, SOUTH, WEST, WALLS, FLATS, TEX

E_, S_, W_, N_ = 0, 1, 2, 3          # gadget directions (east, south, west, north)
DAYFOG = (34, 46, 24)                # the jungle's shade: distance darkens toward deep green


def jungle(L, x0, y0, x1, y1, light=2, flr='jgrass'):
    L.region(x0, y0, x1, y1, flr, 'sky', light, out=True)


# ================================================================== LEVEL 17: The Lost Temple

def level17():
    L = Level('THE LOST TEMPLE', 'Episode 5 - Xochitlan, Day of the Dead', 56, 52, sky='sky6', music=21, fog=DAYFOG, fogk=8)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'foliage')
    # ---- the professor's camp (start, south-west)
    jungle(L, 3, 40, 18, 49)
    L.start = (10.5, 47.5, NORTH)
    L.put('tent', 5, 42); L.put('tent', 15, 42); L.put('torch', 8, 44); L.put('torch', 13, 44)
    L.put('keg', 3, 48); L.put('keg', 4, 49); L.put('keg', 17, 49)
    L.put('shotgun', 15, 44); L.put('shells', 17, 46); L.put('bullets', 4, 46); L.put('candy', 12, 49)
    for (x, y) in ((3, 40), (18, 40), (11, 41)):
        L.put('palm', x, y)
    L.put('fern', 7, 47); L.put('fern', 16, 48)
    # ---- jungle trail north, across a stream
    jungle(L, 9, 30, 14, 39, 3)
    L.region(4, 33, 30, 34, 'river', 'sky', 3, out=True)          # the stream (wading is slow)
    L.region(10, 33, 11, 34, 'planks', 'sky', 3, out=True)         # a plank bridge
    L.put('kapok', 13, 37); L.put('fern', 9, 36); L.put('vines', 12, 31)
    L.put('jaguar', 6, 32); L.put('jaguar', 20, 35, 1); L.put('candy', 4, 35); L.put('bullets', 28, 32); L.put('mummy', 12, 37, 1)
    jungle(L, 4, 32, 30, 32, 3); jungle(L, 4, 35, 30, 36, 3)
    L.put('palm', 24, 36); L.put('fern', 27, 35); L.put('kapok', 16, 32)
    # ---- west glade with the old head (and a secret stash behind the leaves)
    jungle(L, 2, 22, 8, 31, 3)
    L.put('olmec', 5, 25); L.put('mummy', 4, 29); L.put('fern', 7, 23); L.put('shells', 3, 23); L.put('jaguar', 6, 27)
    L.room(0, 13, 7, 21, 'foliage', 'jgrass', 'sky', 4, out=True)
    L.door(5, 21, secret='foliage')
    L.put('brew', 3, 16); L.put('armor', 5, 15); L.put('gold', 2, 18); L.put('gold', 6, 17)
    # ---- the ruins plaza in front of the temple
    jungle(L, 9, 18, 47, 29, 2)
    L.region(18, 18, 46, 20, 'tfloor', 'sky', 2, out=True)
    L.region(31, 21, 33, 29, 'tfloor', 'sky', 2, out=True)        # the old causeway (the boulder's lane)
    for (x, y) in ((14, 21), (24, 21), (40, 21), (14, 27), (44, 27)):
        L.put('pillar', x, y)
    L.put('olmec', 20, 25); L.put('olmec', 44, 23)
    L.put('jstatue', 29, 19); L.put('jstatue', 35, 19)
    for (x, y) in ((10, 19), (26, 28), (38, 28), (46, 19)):
        L.put('kapok', x, y)
    for (x, y) in ((17, 24), (23, 28), (37, 24), (42, 26), (11, 25)):
        L.put('fern', x, y)
    L.put('vines', 18, 19); L.put('vines', 45, 20)
    # thickets and tumbled walls break up the plaza (the causeway, x 31-33, stays clear for the boulder)
    L.block(12, 22, 13, 23, 'foliage'); L.block(36, 25, 38, 26, 'foliage'); L.block(21, 20, 22, 21, 'vinestone')
    L.block(27, 21, 27, 22, 'vinestone'); L.block(41, 22, 41, 23, 'vinestone'); L.block(17, 27, 18, 28, 'foliage')
    L.put('mummy', 22, 23); L.put('jaguar', 37, 22); L.put('mummy', 26, 25, 1); L.put('jaguar', 15, 23, 2)
    L.put('mummy', 41, 25); L.put('jaguar', 12, 21, 1); L.put('mummy', 16, 20); L.put('mummy', 45, 25, 1); L.put('jaguar', 29, 26, 2)
    L.put('candy', 46, 28); L.put('shells', 10, 28); L.put('bullets', 28, 23); L.put('bucket', 36, 27); L.put('bullets', 39, 28)
    L.put('shells', 23, 16); L.put('shells', 44, 19)
    # the jungle strikes back when the idol is lifted
    L.put('jaguar', 24, 26, ambush=True); L.put('jaguar', 40, 24, ambush=True); L.put('jaguar', 13, 26, 1, ambush=True)
    L.put('mummy', 44, 21, 1, ambush=True); L.put('jaguar', 28, 22, 2, ambush=True)
    # ---- the temple
    L.block(14, 1, 42, 17, 'tstone')
    # entry hall (west)
    L.region(17, 13, 23, 16, 'tfloor', 'tceil', 14)
    L.region(20, 17, 20, 17, 'tfloor', 'tceil', 12)                # open archway
    L.put('torch', 17, 13); L.put('torch', 23, 13); L.put('jstatue', 18, 16); L.put('jstatue', 22, 16)
    L.put('mummy', 20, 14); L.put('candy', 17, 16); L.put('mummy', 22, 15, 1)
    L.setw(16, 14, 'glyphs'); L.setw(24, 14, 'glyphs'); L.setw(19, 12, 'mural'); L.setw(21, 12, 'mural')
    # secret treasure room behind the glyph wall (west of the entry hall)
    L.room(14, 12, 16, 16, 'tstone', 'tfloor', 'tceil', 12)
    L.region(15, 13, 15, 15, 'tfloor', 'tceil', 12)
    L.door(16, 15, secret='glyphs')
    L.put('tommy', 15, 13); L.put('gold', 15, 14); L.put('bullets', 15, 15)
    # the hall of darts: pressure plates across the floor, dart traps in both walls
    L.region(19, 5, 21, 12, 'tfloor', 'tceil', 15)
    for x in (19, 20, 21):
        L.flr[10, x] = FLATS['pplate']; L.flr[7, x] = FLATS['pplate']
    L.darter(19, 10, E_); L.darter(21, 9, W_); L.darter(19, 7, E_); L.darter(21, 6, W_)
    L.put('vines', 20, 8); L.put('shells', 19, 5); L.put('torch', 19, 11); L.put('jaguar', 20, 6, 1)
    # tomb gallery: mummies, and a spike floor
    L.region(18, 2, 26, 4, 'tfloor', 'tceil', 15)
    L.region(22, 2, 24, 4, 'spikes', 'tceil', 15)
    L.put('mummy', 19, 3); L.put('mummy', 25, 2, 1); L.put('mummy', 25, 4); L.put('torch', 18, 2); L.put('mummy', 21, 2, 2)
    L.put('candy', 26, 2); L.put('vines', 21, 3)
    # the idol chamber
    L.room(27, 1, 37, 10, 'goldwall', 'tfloor', 'tceil', 10)
    L.door(27, 3)
    L.trigwall(26, 3)                                              # ...and when the idol goes, the way back seals
    L.put('torch', 28, 2); L.put('torch', 36, 2); L.put('torch', 28, 9); L.put('torch', 36, 9)
    L.put('gold', 29, 5); L.put('gold', 35, 5); L.put('gold', 30, 8); L.put('gold', 34, 8)
    L.put('jstatue', 29, 3); L.put('jstatue', 35, 3)
    L.put('idol', 32, 5)
    L.boulder(32, 2, S_)
    # the escape tunnel: sealed until the idol is taken, one cell wide, a pit and a plate on the way
    L.trigwall(32, 10, 'tfloor', 'tceil', 14)
    L.region(32, 11, 32, 16, 'tfloor', 'tceil', 14)
    L.region(32, 17, 32, 17, 'tfloor', 'sky', 4, out=True)
    L.pit(32, 13, 32, 13)
    L.flr[15, 32] = FLATS['pplate']
    L.darter(32, 15, E_)
    # ---- the gold seal (east): the river dock and the way on
    L.room(48, 18, 54, 26, 'tstone', 'planks', 'sky', 3, out=True)
    L.door(48, 22, key='gold')
    L.region(49, 19, 53, 25, 'planks', 'sky', 3, out=True)
    L.region(52, 20, 53, 24, 'river', 'sky', 3, out=True)
    L.setw(54, 21, 'falls'); L.setw(54, 22, 'falls'); L.setw(54, 23, 'falls')
    L.exitw(51, 18)
    L.put('torch', 49, 19); L.put('torch', 49, 25); L.put('bucket', 50, 24); L.put('shells', 50, 20)
    L.walls(0, 0, W - 1, H - 1, 'foliage')
    return L


def check_trigger(L):
    """After the idol is lifted (trigger walls flipped), the exit must still be reachable from where the idol stood
    (validate() asserts it)."""
    from gen_levels import TNAME
    saved = L.wall.copy(), L.flag.copy(), L.start
    idol = None
    for t, x, y, s in L.things:
        if TNAME[t] == 'trigwall':
            cx, cy = int(x), int(y)
            L.wall[cy, cx] = 0 if L.wall[cy, cx] else WALLS['tstone'] + 1
            if L.wall[cy, cx]:                  # a door that now opens onto the new wall is just a wall
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    L.flag[cy + dy, cx + dx] &= ~1
        if TNAME[t] == 'idol':
            idol = (x, y)
    L.start = (idol[0], idol[1], 0)
    L.validate()
    L.wall[:] = saved[0]
    L.flag[:] = saved[1]
    L.start = saved[2]


# ================================================================== LEVEL 18: River of Bones

def level18():
    L = Level('RIVER OF BONES', "Episode 5 - The Conquistadors' Fort", 60, 50, sky='sky6', music=22, fog=DAYFOG, fogk=8)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'foliage')
    # ---- the river, east to the falls (wade it: slow), with a muddy bank on both sides
    L.region(2, 22, 57, 25, 'river', 'sky', 3, out=True)
    jungle(L, 2, 21, 44, 21, 3, 'jmud')
    jungle(L, 2, 26, 35, 26, 3, 'jmud')
    # ---- camp on the south bank (start)
    jungle(L, 2, 27, 9, 36)
    L.start = (5.5, 34.5, NORTH)
    L.put('tent', 3, 29); L.put('torch', 8, 31); L.put('keg', 2, 36); L.put('keg', 3, 36)
    L.put('bullets', 8, 35); L.put('candy', 2, 32); L.put('shells', 7, 28); L.put('palm', 9, 27)
    jungle(L, 10, 29, 13, 34, 3, 'jmud')
    # ---- the village on stilts
    jungle(L, 14, 27, 34, 37, 2)
    L.region(14, 28, 34, 29, 'jmud', 'sky', 2, out=True)
    L.region(22, 30, 23, 37, 'jmud', 'sky', 2, out=True)
    L.room(15, 30, 20, 35, 'hut', 'planks', 'thatch', 13)
    L.door(18, 30)
    L.put('bucket', 16, 34); L.put('shells', 19, 33); L.put('mummy', 17, 32, 1)
    L.room(25, 31, 30, 36, 'hut', 'planks', 'thatch', 13)
    L.door(27, 31)
    L.put('bullets', 29, 35); L.put('candy', 26, 35); L.put('jaguar', 28, 33)
    # a stash under the floorboards of the south-west hut (secret)
    L.room(15, 35, 20, 37, 'hut', 'planks', 'thatch', 12)
    L.region(16, 36, 19, 36, 'planks', 'thatch', 12)
    L.door(17, 35, secret='hut')
    L.put('armor', 16, 36); L.put('pumpkins', 19, 36)
    for (x, y) in ((14, 27), (33, 31), (24, 37), (31, 37)):
        L.put('palm', x, y)
    L.put('fern', 21, 33); L.put('fern', 33, 35); L.put('torch', 21, 30); L.put('torch', 31, 30); L.put('rack', 24, 28)
    L.put('jaguar', 20, 28); L.put('jaguar', 33, 28, 1); L.put('mummy', 32, 34); L.put('conq', 23, 35, 2); L.put('jaguar', 21, 36, 2)
    L.put('candy', 34, 36); L.put('shells', 14, 33)
    # ---- the bridge to the fort's red gate
    L.region(22, 22, 23, 25, 'planks', 'sky', 3, out=True)
    # ---- the conquistadors' fort (north bank)
    L.block(10, 1, 41, 20, 'vinestone')
    L.door(22, 20, key='red')
    L.region(12, 9, 38, 19, 'jmud', 'sky', 3, out=True)
    L.region(20, 9, 25, 19, 'tfloor', 'sky', 3, out=True)
    for (x, y) in ((15, 12), (33, 12)):
        L.put('rack', x, y)
    L.put('ofrenda', 27, 10); L.put('torch', 13, 10); L.put('torch', 37, 10); L.put('torch', 19, 18); L.put('torch', 26, 18)
    L.block(16, 15, 17, 16, 'tstone'); L.block(30, 15, 31, 16, 'tstone')
    L.put('conq', 14, 17); L.put('conq', 35, 17); L.put('conq', 23, 12, 1); L.put('mummy', 29, 13); L.put('jaguar', 18, 13)
    L.put('conq', 31, 10, 2); L.put('mummy', 12, 14, 1); L.put('jaguar', 36, 14, 1)
    L.put('candy', 12, 19); L.put('bullets', 38, 19); L.put('shells', 25, 14); L.put('candy', 38, 9)
    # armory (tommy gun)
    L.room(12, 2, 19, 8, 'tstone', 'tfloor', 'tceil', 14)
    L.door(16, 8)
    L.put('tommy', 15, 4); L.put('bullets', 13, 3); L.put('bullets', 18, 3); L.put('conq', 13, 6, 1); L.put('torch', 18, 7)
    # barracks
    L.room(21, 2, 28, 8, 'tstone', 'planks', 'tceil', 14)
    L.door(24, 8)
    L.put('conq', 22, 4); L.put('conq', 27, 4, 1); L.put('shells', 22, 7); L.put('candy', 27, 7); L.put('keg', 25, 3)
    # the chapel (blue key) - and a stash behind its wall paintings (secret)
    L.room(30, 2, 39, 8, 'adobe', 'tfloor', 'tceil', 13)
    L.door(34, 8)
    L.setw(33, 2, 'mural'); L.setw(36, 2, 'mural')
    L.put('ofrenda', 34, 3); L.put('key_blue', 35, 5); L.put('shells', 31, 7); L.put('mummy', 31, 4); L.put('mummy', 38, 6, 1); L.put('mummy', 32, 7, 2)
    L.room(39, 2, 41, 6, 'adobe', 'tfloor', 'tceil', 12)
    L.region(40, 3, 40, 5, 'tfloor', 'tceil', 12)
    L.door(39, 4, secret='mural')
    L.put('brew', 40, 3); L.put('pumpkins', 40, 5)
    # ---- blue door: the spike cave, up to the falls
    L.region(39, 15, 40, 15, 'tfloor', 'sky', 4, out=True)
    L.door(41, 15, key='blue')
    L.block(42, 10, 57, 19, 'vinestone')
    L.region(42, 11, 56, 18, 'tfloor', 'tceil', 16)
    L.region(45, 11, 46, 18, 'spikes', 'tceil', 16)
    L.region(50, 11, 51, 18, 'spikes', 'tceil', 16)
    L.block(48, 11, 48, 13, 'vinestone'); L.block(48, 16, 48, 18, 'vinestone')
    L.put('torch', 43, 11); L.put('torch', 43, 18); L.put('torch', 55, 11); L.put('vines', 47, 15); L.put('vines', 53, 13)
    L.put('mummy', 44, 13); L.put('jaguar', 53, 15); L.put('mummy', 55, 17, 1); L.put('candy', 47, 11); L.put('shells', 52, 18)
    # the falls overlook (exit)
    jungle(L, 51, 2, 57, 9, 3, 'jmud')
    L.region(53, 9, 54, 10, 'tfloor', 'tceil', 14)
    for x in range(51, 58):
        L.setw(x, 1, 'falls')
    L.setw(58, 3, 'falls'); L.setw(58, 4, 'falls'); L.setw(58, 6, 'falls'); L.setw(58, 7, 'falls')
    L.exitw(58, 5)
    L.put('conq', 52, 3); L.put('conq', 56, 8, 1); L.put('bucket', 51, 8); L.put('torch', 57, 2)
    # ---- the canyon: ledges over a chasm, out to the shrine with the red key
    jungle(L, 35, 30, 38, 32, 3, 'jmud')
    jungle(L, 36, 28, 57, 48, 20, 'jmud')
    L.pit(36, 28, 57, 48)
    for (x0, y0, x1, y1) in ((39, 30, 42, 32), (44, 29, 46, 33), (49, 30, 52, 34), (49, 36, 53, 39), (48, 42, 54, 43)):
        jungle(L, x0, y0, x1, y1, 4, 'jmud')
    jungle(L, 36, 30, 38, 32, 3, 'jmud')
    L.put('conq', 45, 31); L.put('conq', 51, 37, 1); L.put('candy', 52, 32); L.put('shells', 53, 38)
    # the shrine
    L.room(47, 44, 55, 48, 'tstone', 'tfloor', 'tceil', 15)
    L.door(51, 44)
    for x in (49, 50, 51, 52, 53):
        L.flr[46, x] = FLATS['pplate']
    L.darter(48, 46, E_); L.darter(54, 45, W_); L.darter(48, 47, E_)
    L.put('key_red', 51, 47); L.put('torch', 48, 45); L.put('torch', 54, 47); L.put('gold', 53, 47); L.put('gold', 49, 45)
    # the rope bridge home (west door of the shrine)
    L.door(47, 46)
    L.region(36, 46, 46, 46, 'planks', 'sky', 6, out=True)
    jungle(L, 34, 37, 35, 46, 4, 'jmud')
    L.put('fern', 34, 44)
    L.walls(0, 0, W - 1, H - 1, 'foliage')
    return L


# ================================================================== LEVEL 19: The Fog

def level19():
    L = Level('THE FOG', 'Episode 5 - San Lazaro, Midnight', 56, 56, sky='sky7', music=23, fog=(150, 150, 146), fogk=64, flags=2 | 4)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'adobe')
    L.extra_tex = ('rust', 'rustwin', 'rustgrate', 'rustfloor', 'sky8')
    def street(x0, y0, x1, y1):
        L.region(x0, y0, x1, y1, 'jmud', 'sky', 2, out=True)
    # ---- streets
    street(26, 17, 29, 54)                 # main street, from the town gate to the plaza
    L.start = (27.5, 52.5, NORTH)
    street(4, 38, 51, 41)                  # cross street
    street(6, 10, 8, 41)                   # west street
    street(46, 10, 48, 41)                 # east street (to the cemetery gate)
    street(6, 10, 18, 12)                  # north lanes to the plaza
    street(37, 10, 48, 12)
    # ---- the plaza: altars for the dead, candles, ghosts of soldiers
    L.region(16, 17, 39, 30, 'tfloor', 'sky', 2, out=True)
    L.region(16, 13, 18, 16, 'jmud', 'sky', 2, out=True)
    L.region(37, 13, 39, 16, 'jmud', 'sky', 2, out=True)
    for (x, y) in ((19, 20), (36, 20), (19, 27), (36, 27)):
        L.put('ofrenda', x, y)
    for (x, y) in ((22, 23), (33, 23), (22, 25), (33, 25)):
        L.put('candles', x, y)
    L.put('pillar', 27, 24); L.put('pillar', 28, 24); L.put('rack', 24, 29); L.put('rack', 31, 29)
    L.put('weeper', 17, 18); L.put('conq', 34, 26); L.put('mummy', 21, 28, 1); L.put('weeper', 38, 29, 2)
    L.put('candy', 16, 30); L.put('shells', 39, 17)
    # ---- houses (adobe, barred windows, dark inside)
    def house(x0, y0, x1, y1, dx, dy, light=12):
        L.room(x0, y0, x1, y1, 'adobe', 'planks', 'thatch', light)
        L.door(dx, dy)
    for x in (10, 14, 20, 34, 40, 44):
        L.setw(x, 37, 'adobewin'); L.setw(x, 42, 'adobewin')
    for y in (15, 21, 33, 47):
        L.setw(25, y, 'adobewin'); L.setw(30, y, 'adobewin')
    house(9, 42, 16, 49, 12, 42)
    L.put('bullets', 10, 48); L.put('candy', 15, 43); L.put('mummy', 13, 46)
    house(18, 42, 25, 49, 21, 42)
    L.put('shells', 24, 48); L.put('weeper', 19, 47, 1); L.put('candles', 22, 45)
    house(30, 42, 38, 50, 34, 42)
    L.put('launcher', 31, 48); L.put('pumpkins', 37, 49); L.put('conq', 36, 45)
    house(40, 42, 45, 48, 42, 42)
    L.put('bucket', 43, 47); L.put('mummy', 41, 45, 2)
    house(9, 31, 16, 37, 12, 37)
    L.put('shells', 10, 32); L.put('candles', 15, 32)
    house(30, 31, 38, 37, 34, 37)
    L.put('bullets', 37, 32); L.put('weeper', 31, 33)
    # a back room behind the first house's hearth (secret)
    L.room(9, 49, 16, 53, 'adobe', 'planks', 'thatch', 11)
    L.region(10, 50, 15, 52, 'planks', 'thatch', 11)
    L.door(12, 49, secret='adobe')
    L.put('brew', 11, 51); L.put('armor', 14, 51)
    # wanderers in the fog
    L.put('mummy', 27, 44); L.put('weeper', 7, 25); L.put('mummy', 47, 30); L.put('conq', 7, 39, 1); L.put('weeper', 47, 14, 1)
    L.put('mummy', 28, 33, 2); L.put('candy', 8, 20); L.put('bullets', 46, 24); L.put('candy', 50, 39)
    # ---- the church: the red key on the altar, the crypt (blue door) behind it
    L.room(19, 4, 36, 16, 'adobe', 'tfloor', 'tceil', 12)
    L.door(27, 16)
    for x in (23, 32):
        for y in (7, 10, 13):
            L.put('pillar', x, y)
    for x in (25, 26, 29, 30):
        L.setw(x, 4, 'mural')
    L.put('ofrenda', 27, 6); L.put('candles', 25, 6); L.put('candles', 30, 6); L.put('key_red', 28, 7)
    L.put('candles', 20, 5); L.put('candles', 35, 5); L.put('bucket', 20, 15); L.put('shells', 35, 15)
    L.room(24, 1, 31, 4, 'tstone', 'tfloor', 'tceil', 16)
    L.door(27, 4, key='blue')
    L.exitw(27, 1)
    L.put('candles', 25, 2); L.put('candles', 30, 2)
    # ---- the cemetery behind the red gate, the blue key in the mausoleum
    L.door(49, 20, key='red')
    L.region(50, 4, 54, 36, 'jgrass', 'sky', 3, out=True)
    for y in (13, 17, 21, 25, 29, 33):
        L.put('tomb' if y % 8 == 1 else 'tomb2', 51, y); L.put('tomb2' if y % 8 == 1 else 'tomb', 53, y)
    L.put('torch', 50, 11); L.put('torch', 54, 11); L.put('candy', 52, 35)
    L.room(49, 3, 55, 9, 'tstone', 'tfloor', 'tceil', 14)
    L.door(52, 9)
    L.put('key_blue', 52, 5); L.put('candles', 50, 4); L.put('candles', 54, 4)
    L.put('weeper', 52, 26); L.put('mummy', 51, 15, 1)
    # ---- the Other World: what comes out when the siren sounds
    for (t, x, y, sk) in (('weeper', 22, 14, 0), ('weeper', 33, 12, 1), ('conq', 20, 22, 0), ('conq', 35, 24, 0), ('mummy', 27, 27, 0),
                          ('mummy', 28, 36, 1), ('weeper', 27, 46, 0), ('mummy', 47, 18, 0), ('weeper', 7, 33, 1), ('conq', 47, 39, 2),
                          ('mummy', 52, 19, 0), ('weeper', 51, 31, 0), ('mummy', 53, 10, 1), ('conq', 17, 29, 2)):
        L.put(t, x, y, sk, ambush=True)
    L.put('shells', 27, 30); L.put('bullets', 48, 36); L.put('candy', 18, 17); L.put('shells', 8, 30); L.put('bullets', 27, 20)
    L.put('shells', 21, 10); L.put('bullets', 50, 22); L.put('shells', 47, 33); L.put('bullets', 31, 36); L.put('candy', 34, 10)
    L.walls(0, 0, W - 1, H - 1, 'adobe')
    return L


# ================================================================== LEVEL 20: Xibalba

def level20():
    L = Level('XIBALBA', 'Episode 5 - The Place of Fear', 46, 46, sky='sky8', music=24, fog=(40, 6, 4), fogk=11, flags=1)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'xstone')
    L.region(2, 2, W - 3, 35, 'xfloor', 'sky', 7, out=True)
    # rivers of fire with stone bridges
    L.region(2, 13, W - 3, 14, 'xlava', 'sky', 3, out=True, hurt=True)
    L.region(2, 25, W - 3, 26, 'xlava', 'sky', 3, out=True, hurt=True)
    for x0 in (7, 21, 36):
        L.region(x0, 13, x0 + 2, 14, 'xfloor', 'sky', 6, out=True)
    for x0 in (12, 30):
        L.region(x0, 25, x0 + 2, 26, 'xfloor', 'sky', 6, out=True)
    # the abyss at the edges
    L.pit(2, 17, 3, 22); L.pit(42, 17, 43, 22)
    # pillars for cover
    for (x, y) in ((10, 6), (34, 6), (10, 30), (34, 30), (17, 19), (27, 19)):
        L.block(x, y, x + 1, y + 1, 'xstone')
    for (x, y) in ((4, 4), (41, 4), (4, 33), (41, 33), (16, 3), (29, 3)):
        L.put('torch', x, y)
    L.put('rack', 20, 3); L.put('rack', 25, 3); L.put('rack', 6, 10); L.put('rack', 39, 10)
    # start passage
    L.room(17, 36, 28, 44, 'xstone', 'xfloor', 'tceil', 12)
    L.door(22, 36)
    L.start = (22.5, 42.5, NORTH)
    L.put('bucket', 18, 43); L.put('shells', 27, 43); L.put('pumpkins', 18, 38); L.put('bullets', 27, 38)
    L.put('armor', 22, 41); L.put('launcher', 25, 40); L.put('torch', 18, 37); L.put('torch', 27, 37)
    # supplies (they come back)
    L.put('shells', 4, 8); L.put('bullets', 41, 8); L.put('bucket', 4, 30); L.put('pumpkins', 41, 30); L.put('candy', 15, 22)
    L.put('candy', 30, 22); L.put('shells', 22, 32); L.put('bullets', 22, 17); L.put('keg', 8, 20); L.put('keg', 37, 20)
    # Seven Death and his court
    L.put('seven', 22, 7)
    L.put('mummy', 8, 9); L.put('mummy', 37, 9); L.put('jaguar', 22, 22, 1); L.put('jaguar', 6, 28, 2)
    L.extra_groups = ('mummy', 'jaguar')
    return L


# ================================================================== cutscene set: the altar of Xibalba (west) + the jungle at dawn (east)

def cut5():
    L = Level('XIBALBA', '', 48, 18, sky='sky6', music=16, fog=(60, 22, 12), fogk=6)
    W, H = L.w, L.h
    L.block(0, 0, W - 1, H - 1, 'xstone')
    # the altar cavern: lit by lava and torches, bright enough to see who does what
    L.region(1, 1, 22, 16, 'xfloor', 'tceil', 3)
    L.region(1, 1, 2, 16, 'xlava', 'tceil', 1)
    L.region(21, 1, 22, 16, 'xlava', 'tceil', 1)
    L.put('rack', 6, 2); L.put('rack', 17, 2); L.put('torch', 5, 6); L.put('torch', 18, 5); L.put('pillar', 5, 12); L.put('pillar', 19, 14)
    L.put('torch', 9, 2); L.put('torch', 14, 2); L.put('jstatue', 8, 4); L.put('jstatue', 15, 4)
    # the jungle at dawn, in front of the temple
    L.block(24, 0, 47, 17, 'foliage')
    L.region(25, 6, 46, 16, 'jgrass', 'sky', 4, out=True)
    L.block(25, 1, 46, 5, 'tstone')
    for x in (30, 33, 38, 41):
        L.setw(x, 5, 'vinestone')
    L.setw(34, 5, 'glyphs'); L.setw(37, 5, 'glyphs')
    L.region(35, 2, 36, 5, 'tfloor', 'tceil', 30)
    L.put('torch', 33, 6); L.put('torch', 38, 6); L.put('kapok', 27, 8); L.put('kapok', 44, 9); L.put('palm', 29, 13)
    L.put('palm', 42, 14); L.put('fern', 31, 9); L.put('fern', 40, 8); L.put('tent', 44, 13); L.put('vines', 34, 6)
    L.walls(0, 0, W - 1, H - 1, 'xstone')
    L.start = (11.5, 14.0, NORTH)
    L.extra_groups = ('butch', 'cs', 'cpbutch', 'cpcrane', 'cpseven', 'cpmelt', 'cpgore', 'cpshrunk')
    return L


LEVELS4 = [level17, level18, level19, level20]
CUTS4 = [cut5]
