"""Shared definitions for the asset packer and the level builder.

Thing type ids must match the constants in src/W.java (checked by gen_pack.py, which reads W.java).
Sprites are loaded per level in groups: COMMON sprites live in d.bin and are always in memory, every
other sprite belongs to a group (monster sets by name prefix, other props one group each)."""

# ------------------------------------------------------------------ thing types (level file ids)
THINGS = dict(
    # monsters
    zombie=1, scarecrow=2, wraith=3, witch=4, boss=5, skel=6, clown=7, wolf=8, bat=9, vamp=10, giggles=11, count=12,
    frank=13, drone=14, cyborg=15, spider=16, prime=17,
    mummy=18, jaguar=19, conq=20, weeper=21, seven=22,
    # pickups
    candy=30, bucket=31, brew=32, armor=33, bullets=34, shells=35, pumpkins=36, shotgun=37, tommy=38, launcher=39,
    key_red=40, key_blue=41, key_gold=42, idol=43,
    # decoration (E1)
    jack=44, jack2=45, candles=46, tree=47, tomb=48, tomb2=49, hanging=50, cauldron=51, keg=52, skulls=53, lamp=54,
    patch=55, gibs=56,
    # decoration (E2: town + carnival)
    streetlamp=57, balloons=58, carousel=59, cotton=60, hydrant=61, trashcan=62, wreck=63, bulbs=64, clownhead=65,
    strongman=66,
    # decoration (E3: swamp + castle)
    candelabra=67, coffin=68, cypress=69, tesla=70, tank=71, knight=72, cage=73, brazier=74, reeds=75, gargoyle=76,
    # decoration and gadgets (E4: Halloween 2099)
    holotomb=77, neonjack=78, crate=79, toxic=80, robotarm=81, capsule=82, terminal=83, cables=84, tpad=85, tdest=86,
    # decoration and gadgets (E5: the jungle)
    kapok=87, palm=88, fern=89, vines=90, olmec=91, jstatue=92, rack=93, ofrenda=94, torch=95, pillar=96, gold=97,
    tent=98, boulder=99, darter=100, trigwall=101,
    # cutscene actor (sprite chosen by script)
    actor=150,
)
PICKUPS = {'candy', 'bucket', 'brew', 'armor', 'bullets', 'shells', 'pumpkins', 'shotgun', 'tommy', 'launcher', 'key_red',
           'key_blue', 'key_gold', 'idol'}
MONSTERS = {'zombie', 'scarecrow', 'wraith', 'witch', 'boss', 'skel', 'clown', 'wolf', 'bat', 'vamp', 'giggles', 'count',
            'frank', 'drone', 'cyborg', 'spider', 'prime', 'mummy', 'jaguar', 'conq', 'weeper', 'seven'}
BOSSES = {'boss', 'giggles', 'count', 'prime', 'seven'}
SOLID_DECOR = {'tree', 'tomb', 'tomb2', 'cauldron', 'keg', 'lamp', 'streetlamp', 'carousel', 'cotton', 'hydrant', 'trashcan',
               'wreck', 'strongman', 'candelabra', 'coffin', 'cypress', 'tesla', 'tank', 'knight', 'brazier', 'gargoyle',
               'holotomb', 'neonjack', 'crate', 'toxic', 'robotarm', 'capsule', 'terminal', 'kapok', 'palm', 'olmec', 'jstatue',
               'rack', 'ofrenda', 'torch', 'pillar', 'tent', 'boulder'}

# sprites that are always loaded (in d.bin): weapons, effects, pickups, projectiles, small common props
COMMON_PREFIX = ('w_', 'fx_')
COMMON = {'candy', 'bucket', 'brew', 'armor', 'bullets', 'shells', 'pumpkins', 'pk_shotgun', 'pk_tommy', 'pk_launcher',
          'key_red', 'key_blue', 'key_gold', 'fireball1', 'fireball2', 'greenball1', 'greenball2', 'pbomb',
          'knife1', 'knife2', 'bolt1', 'bolt2', 'jball', 'jack', 'jack2', 'candles', 'keg', 'gibs', 'skulls',
          'zap1', 'zap2', 'laser1', 'laser2', 'dart1', 'dart2', 'shot1', 'shot2', 'disc1', 'disc2', 'rock'}
# monster / actor sprite sets: every sprite whose name starts with '<prefix>_' is in group <prefix>
SET_PREFIX = ('zombie', 'scarecrow', 'wraith', 'witch', 'boss', 'skel', 'clown', 'wolf', 'bat', 'vamp', 'giggles', 'count',
              'frank', 'drone', 'cyborg', 'spider', 'prime', 'butch', 'cs', 'cpbutch', 'cppk', 'cpkid', 'cpgig', 'cpcount',
              'cpdoc', 'cpgore', 'mummy', 'jaguar', 'conq', 'weeper', 'seven', 'boulder', 'cpcrane', 'cpmelt', 'cpseven',
              'cpshrunk')
# extra groups a thing needs at runtime (boss summons)
THING_EXTRA = {'boss': ['zombie', 'wraith'], 'giggles': ['clown', 'skel'], 'count': ['bat', 'wolf'], 'prime': ['spider', 'drone'],
               'seven': ['mummy', 'jaguar']}
# decoration things whose sprite group is not simply their own name
THING_GROUP = {'jack': None, 'jack2': None, 'candles': None, 'keg': None, 'skulls': None, 'gibs': None, 'tpad': 'telepad',
               'tdest': None, 'darter': None, 'trigwall': None, 'idol': 'idol'}

# always-loaded textures (doors, exits)
COMMON_TEX = {'door', 'door_red', 'door_blue', 'door_gold', 'doorframe', 'exit'}


def sprite_group(name):
    """Group name of a sprite, or None if it is common."""
    if name in COMMON or name.startswith(COMMON_PREFIX):
        return None
    for p in SET_PREFIX:
        if name.startswith(p + '_'):
            return p
    return name


def thing_groups(kind):
    """Sprite groups a thing type needs (list of group names)."""
    if kind in THING_GROUP:
        g = THING_GROUP[kind]
        return [] if g is None else [g]
    if kind in PICKUPS:
        return []                       # pickups are common
    if kind == 'actor':
        return []
    return [kind] + THING_EXTRA.get(kind, [])
