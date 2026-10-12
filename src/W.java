import java.io.DataInputStream;

/** World state and gameplay: level, player, monsters, weapons, projectiles, doors, pickups, particles. */
final class W {
    // ------------------------------------------------------------------ map
    static final int F_DOOR = 1, F_SECRET = 2, F_EXIT = 4, F_HURT = 8, F_KRED = 16, F_KBLUE = 32, F_KGOLD = 64, F_OUT = 128;
    static final byte[] wall = new byte[4096], flr = new byte[4096], cel = new byte[4096], flag = new byte[4096], seen = new byte[4096];
    static final int[] door = new int[4096], light = new int[4096], baseLight = new int[4096];
    static final byte[] flick = new byte[4096], dstate = new byte[4096];
    static final short[] dtime = new short[4096];
    static final byte[] push = new byte[4096];      // secret pushwalls: slide direction 0 +x, 1 -x, 2 +y, 3 -y
    static int skyTex = -1, level, skill = 1, lightning, lvMusic, lvFlags, mapW, mapH;
    static final int LF_RESPAWN = 1;      // level flag: pickups come back (boss arenas)
    static final int LF_RADIO = 2;        // level flag: Butch's pocket radio crackles when monsters are near (the fog)
    static final int LF_OTHER = 4;        // level flag: the red key drags the town into the Other World
    static String lvName = "", lvSub = "";
    static int fogR, fogG, fogB;

    // ------------------------------------------------------------------ thing types
    // (ids must match tools/defs.py; gen_pack.py checks them)
    static final int ZOMBIE = 1, SCARE = 2, WRAITH = 3, WITCH = 4, BOSS = 5, SKEL = 6, CLOWN = 7, WOLF = 8, BAT = 9, VAMP = 10,
            GIGGLES = 11, COUNT = 12, FRANK = 13, DRONE = 14, CYBORG = 15, SPIDER = 16, PRIME = 17,
            MUMMY = 18, JAGUAR = 19, CONQ = 20, WEEPER = 21, SEVEN = 22, NMON = 23;
    static final int CANDY = 30, BUCKET = 31, BREW = 32, ARMOR = 33, BULLETS = 34, SHELLS = 35, PUMPKINS = 36, SHOTGUN = 37,
            TOMMY = 38, LAUNCHER = 39, KEYR = 40, KEYB = 41, KEYG = 42, IDOL = 43;
    static final int JACK = 44, JACK2 = 45, CANDLES = 46, TREE = 47, TOMB = 48, TOMB2 = 49, HANGING = 50, CAULDRON = 51, KEG = 52,
            SKULLS = 53, LAMP = 54, PATCH = 55, GIBS = 56;
    static final int STREETLAMP = 57, BALLOONS = 58, CAROUSEL = 59, COTTON = 60, HYDRANT = 61, TRASHCAN = 62, WRECK = 63, BULBS = 64,
            CLOWNHEAD = 65, STRONGMAN = 66;
    static final int CANDELABRA = 67, COFFIN = 68, CYPRESS = 69, TESLA = 70, TANK = 71, KNIGHT = 72, CAGE = 73, BRAZIER = 74, REEDS = 75,
            GARGOYLE = 76;
    static final int HOLOTOMB = 77, NEONJACK = 78, CRATE = 79, TOXIC = 80, ROBOTARM = 81, CAPSULE = 82, TERMINAL = 83, CABLES = 84,
            TPAD = 85, TDEST = 86;
    // episode 5 (jungle): decoration, then the gadgets (boulder, dart trap, fog spawn point)
    static final int KAPOK = 87, PALM = 88, FERN = 89, VINES = 90, OLMEC = 91, JSTATUE = 92, RACK = 93, OFRENDA = 94, TORCH = 95,
            PILLAR = 96, GOLD = 97, TENT = 98, BOULDER = 99, DARTER = 100, TRIGWALL = 101;
    static final int FIREBALL = 110, GREENBALL = 111, BOSSBALL = 112, PBOMB = 113, KNIFE = 114, BOLT = 115, JBALL = 116, ZAP = 117,
            LASER = 118, DART = 119, SHOT = 120, DISC = 121, ROCK = 122;
    static final int FX_BOOM = 130, FX_PUFF = 131, FX_BLOOD = 132, FX_SPARK = 133, FX_GREEN = 134, FX_ECTO = 135, FX_SMOKE = 136,
            FX_ZAP = 137, FX_DUST = 138;
    static final int ACTOR = 150;
    static final int NTYPE = 160;
    static final int TF_SOLID = 1, TF_SHOOT = 2, TF_MON = 4, TF_PICK = 8, TF_TRANS = 16, TF_BRIGHT = 32, TF_PROJ = 64, TF_FX = 128;
    static final int[] tfl = new int[NTYPE], tspr = new int[NTYPE], tscale = new int[NTYPE], trad = new int[NTYPE], tlight = new int[NTYPE];

    static void defType(int t, int fl, int s, int scale, int rad, int lightStr) {
        tfl[t] = fl; tspr[t] = s; tscale[t] = scale; trad[t] = rad; tlight[t] = lightStr;
    }

    static {
        int R = 18000;
        defType(ZOMBIE, TF_SOLID | TF_SHOOT | TF_MON, Res.S_ZOMBIE_WALK1, 256, R, 0);
        defType(SCARE, TF_SOLID | TF_SHOOT | TF_MON, Res.S_SCARECROW_WALK1, 256, R, 0);
        defType(WRAITH, TF_SOLID | TF_SHOOT | TF_MON | TF_TRANS, Res.S_WRAITH_WALK1, 256, R, 0);
        defType(WITCH, TF_SOLID | TF_SHOOT | TF_MON, Res.S_WITCH_WALK1, 256, R, 0);
        defType(BOSS, TF_SOLID | TF_SHOOT | TF_MON, Res.S_BOSS_WALK1, 256, 40000, 0);
        defType(SKEL, TF_SOLID | TF_SHOOT | TF_MON, Res.S_SKEL_WALK1, 256, 16000, 0);
        defType(CLOWN, TF_SOLID | TF_SHOOT | TF_MON, Res.S_CLOWN_WALK1, 256, R, 0);
        defType(WOLF, TF_SOLID | TF_SHOOT | TF_MON, Res.S_WOLF_WALK1, 256, 22000, 0);
        defType(BAT, TF_SOLID | TF_SHOOT | TF_MON, Res.S_BAT_WALK1, 256, 12000, 0);
        defType(VAMP, TF_SOLID | TF_SHOOT | TF_MON, Res.S_VAMP_WALK1, 256, 17000, 0);
        defType(GIGGLES, TF_SOLID | TF_SHOOT | TF_MON, Res.S_GIGGLES_WALK1, 256, 42000, 0);
        defType(COUNT, TF_SOLID | TF_SHOOT | TF_MON, Res.S_COUNT_WALK1, 256, 30000, 0);
        defType(FRANK, TF_SOLID | TF_SHOOT | TF_MON, Res.S_FRANK_WALK1, 256, 22000, 0);
        defType(DRONE, TF_SOLID | TF_SHOOT | TF_MON, Res.S_DRONE_WALK1, 256, 14000, 0);
        defType(CYBORG, TF_SOLID | TF_SHOOT | TF_MON, Res.S_CYBORG_WALK1, 256, R, 0);
        defType(SPIDER, TF_SOLID | TF_SHOOT | TF_MON, Res.S_SPIDER_WALK1, 256, 15000, 0);
        defType(PRIME, TF_SOLID | TF_SHOOT | TF_MON, Res.S_PRIME_WALK1, 256, 42000, 0);
        defType(CANDY, TF_PICK, Res.S_CANDY, 420, 0, 0);
        defType(BUCKET, TF_PICK, Res.S_BUCKET, 360, 0, 0);
        defType(BREW, TF_PICK, Res.S_BREW, 380, 0, 0);
        defType(ARMOR, TF_PICK, Res.S_ARMOR, 340, 0, 0);
        defType(BULLETS, TF_PICK, Res.S_BULLETS, 400, 0, 0);
        defType(SHELLS, TF_PICK, Res.S_SHELLS, 420, 0, 0);
        defType(PUMPKINS, TF_PICK, Res.S_PUMPKINS, 380, 0, 0);
        defType(SHOTGUN, TF_PICK, Res.S_PK_SHOTGUN, 330, 0, 0);
        defType(TOMMY, TF_PICK, Res.S_PK_TOMMY, 330, 0, 0);
        defType(LAUNCHER, TF_PICK, Res.S_PK_LAUNCHER, 300, 0, 0);
        defType(KEYR, TF_PICK, Res.S_KEY_RED, 400, 0, 4);
        defType(KEYB, TF_PICK, Res.S_KEY_BLUE, 400, 0, 4);
        defType(KEYG, TF_PICK, Res.S_KEY_GOLD, 400, 0, 4);
        defType(JACK, 0, Res.S_JACK, 300, 0, 11);
        defType(JACK2, 0, Res.S_JACK2, 300, 0, 10);
        defType(CANDLES, 0, Res.S_CANDLES, 300, 0, 9);
        defType(TREE, TF_SOLID, Res.S_TREE, 256, 14000, 0);
        defType(TOMB, TF_SOLID, Res.S_TOMB, 300, 16000, 0);
        defType(TOMB2, TF_SOLID, Res.S_TOMB2, 300, 14000, 0);
        defType(HANGING, 0, Res.S_HANGING, 256, 0, 0);
        defType(CAULDRON, TF_SOLID, Res.S_CAULDRON, 300, 20000, 9);
        defType(KEG, TF_SOLID | TF_SHOOT, Res.S_KEG, 300, 16000, 0);
        defType(SKULLS, 0, Res.S_SKULLS, 300, 0, 0);
        defType(LAMP, TF_SOLID, Res.S_LAMP, 256, 9000, 12);
        defType(PATCH, 0, Res.S_PATCH, 300, 0, 0);
        defType(GIBS, 0, Res.S_GIBS, 256, 0, 0);
        defType(STREETLAMP, TF_SOLID, Res.S_STREETLAMP, 256, 9000, 12);
        defType(BALLOONS, 0, Res.S_BALLOONS, 256, 0, 0);
        defType(CAROUSEL, TF_SOLID, Res.S_CAROUSEL, 256, 15000, 0);
        defType(COTTON, TF_SOLID, Res.S_COTTON, 256, 20000, 0);
        defType(HYDRANT, TF_SOLID, Res.S_HYDRANT, 300, 9000, 0);
        defType(TRASHCAN, TF_SOLID, Res.S_TRASHCAN, 300, 12000, 0);
        defType(WRECK, TF_SOLID, Res.S_WRECK, 256, 30000, 6);
        defType(BULBS, 0, Res.S_BULBS, 256, 0, 8);
        defType(CLOWNHEAD, TF_SOLID, Res.S_CLOWNHEAD, 256, 20000, 6);
        defType(STRONGMAN, TF_SOLID, Res.S_STRONGMAN, 256, 14000, 0);
        defType(CANDELABRA, TF_SOLID, Res.S_CANDELABRA, 256, 10000, 10);
        defType(COFFIN, TF_SOLID, Res.S_COFFIN, 256, 15000, 0);
        defType(CYPRESS, TF_SOLID, Res.S_CYPRESS, 256, 16000, 0);
        defType(TESLA, TF_SOLID, Res.S_TESLA, 256, 15000, 12);
        defType(TANK, TF_SOLID, Res.S_TANK, 256, 18000, 9);
        defType(KNIGHT, TF_SOLID, Res.S_KNIGHT, 256, 14000, 0);
        defType(CAGE, 0, Res.S_CAGE, 256, 0, 0);
        defType(BRAZIER, TF_SOLID, Res.S_BRAZIER, 256, 12000, 12);
        defType(REEDS, 0, Res.S_REEDS, 256, 0, 0);
        defType(GARGOYLE, TF_SOLID, Res.S_GARGOYLE, 256, 16000, 0);
        defType(HOLOTOMB, TF_SOLID | TF_BRIGHT, Res.S_HOLOTOMB, 300, 14000, 7);
        defType(NEONJACK, TF_SOLID, Res.S_NEONJACK, 256, 9000, 11);
        defType(CRATE, TF_SOLID, Res.S_CRATE, 300, 20000, 0);
        defType(TOXIC, TF_SOLID | TF_SHOOT, Res.S_TOXIC, 300, 15000, 6);
        defType(ROBOTARM, TF_SOLID, Res.S_ROBOTARM, 256, 16000, 6);
        defType(CAPSULE, TF_SOLID, Res.S_CAPSULE, 256, 16000, 10);
        defType(TERMINAL, TF_SOLID, Res.S_TERMINAL, 256, 14000, 7);
        defType(CABLES, 0, Res.S_CABLES, 256, 0, 0);
        defType(TPAD, TF_BRIGHT, Res.S_TELEPAD, 256, 0, 12);
        defType(TDEST, 0, -1, 256, 0, 0);
        defType(FIREBALL, TF_PROJ | TF_BRIGHT, Res.S_FIREBALL1, 300, 8000, 0);
        defType(GREENBALL, TF_PROJ | TF_BRIGHT, Res.S_GREENBALL1, 300, 8000, 0);
        defType(BOSSBALL, TF_PROJ | TF_BRIGHT, Res.S_FX_BOOM1, 230, 12000, 0);
        defType(PBOMB, TF_PROJ, Res.S_PBOMB, 400, 9000, 0);
        defType(KNIFE, TF_PROJ, Res.S_KNIFE1, 300, 7000, 0);
        defType(BOLT, TF_PROJ | TF_BRIGHT, Res.S_BOLT1, 320, 9000, 0);
        defType(JBALL, TF_PROJ, Res.S_JBALL, 380, 9000, 0);
        defType(ZAP, TF_PROJ | TF_BRIGHT, Res.S_ZAP1, 360, 10000, 0);
        defType(LASER, TF_PROJ | TF_BRIGHT, Res.S_LASER1, 300, 7000, 0);
        defType(FX_ZAP, TF_FX | TF_BRIGHT, Res.S_FX_ZAP, 380, 0, 0);
        defType(FX_BOOM, TF_FX | TF_BRIGHT, Res.S_FX_BOOM1, 520, 0, 0);
        defType(FX_PUFF, TF_FX, Res.S_FX_PUFF1, 256, 0, 0);
        defType(FX_BLOOD, TF_FX, Res.S_FX_BLOOD1, 300, 0, 0);
        defType(FX_SPARK, TF_FX | TF_BRIGHT, Res.S_FX_SPARK, 256, 0, 0);
        defType(FX_GREEN, TF_FX | TF_BRIGHT, Res.S_FX_GREEN, 360, 0, 0);
        defType(FX_ECTO, TF_FX | TF_BRIGHT, Res.S_FX_ECTO, 360, 0, 0);
        defType(FX_SMOKE, TF_FX | TF_TRANS, Res.S_FX_SMOKE1, 420, 0, 0);
        defType(FX_DUST, TF_FX | TF_TRANS, Res.S_FX_SMOKE1, 330, 0, 0);
        defType(ACTOR, 0, -1, 256, 0, 0);
        // ---- episode 5: the jungle
        defType(MUMMY, TF_SOLID | TF_SHOOT | TF_MON, Res.S_MUMMY_WALK1, 256, R, 0);
        defType(JAGUAR, TF_SOLID | TF_SHOOT | TF_MON, Res.S_JAGUAR_WALK1, 256, R, 0);
        defType(CONQ, TF_SOLID | TF_SHOOT | TF_MON, Res.S_CONQ_WALK1, 256, R, 0);
        defType(WEEPER, TF_SOLID | TF_SHOOT | TF_MON | TF_TRANS, Res.S_WEEPER_WALK1, 256, 16000, 0);
        defType(SEVEN, TF_SOLID | TF_SHOOT | TF_MON, Res.S_SEVEN_WALK1, 256, 40000, 0);
        defType(IDOL, TF_PICK, Res.S_IDOL, 380, 0, 5);
        defType(KAPOK, TF_SOLID, Res.S_KAPOK, 256, 22000, 0);
        defType(PALM, TF_SOLID, Res.S_PALM, 256, 10000, 0);
        defType(FERN, 0, Res.S_FERN, 256, 0, 0);
        defType(VINES, 0, Res.S_VINES, 256, 0, 0);
        defType(OLMEC, TF_SOLID, Res.S_OLMEC, 256, 24000, 0);
        defType(JSTATUE, TF_SOLID, Res.S_JSTATUE, 256, 15000, 0);
        defType(RACK, TF_SOLID, Res.S_RACK, 256, 20000, 0);
        defType(OFRENDA, TF_SOLID, Res.S_OFRENDA, 256, 20000, 9);
        defType(TORCH, TF_SOLID, Res.S_TORCH, 256, 8000, 12);
        defType(PILLAR, TF_SOLID, Res.S_PILLAR, 256, 15000, 0);
        defType(GOLD, 0, Res.S_GOLD, 256, 0, 0);
        defType(TENT, TF_SOLID, Res.S_TENT, 256, 30000, 0);
        defType(BOULDER, TF_SOLID, Res.S_BOULDER_1, 256, 30000, 0);
        defType(DARTER, 0, -1, 256, 0, 0);
        defType(TRIGWALL, 0, -1, 256, 0, 0);
        defType(DART, TF_PROJ, Res.S_DART1, 300, 6000, 0);
        defType(SHOT, TF_PROJ | TF_BRIGHT, Res.S_SHOT1, 300, 7000, 0);
        defType(DISC, TF_PROJ | TF_BRIGHT, Res.S_DISC1, 340, 10000, 0);
        defType(ROCK, TF_PROJ, Res.S_ROCK, 420, 9000, 0);
    }

    // ------------------------------------------------------------------ difficulty (index = skill 0 easy, 1 normal, 2 hard)
    static final int[] SK_DMG = {50, 100, 130};         // damage the player takes, %
    static final int[] SK_HP = {85, 100, 125};          // monster health, %
    static final int[] SK_BOSSHP = {60, 100, 120};      // boss health, %
    static final int[] SK_COOL = {140, 100, 85};        // monster attack cooldowns, %
    static final int[] SK_PSPD = {85, 100, 110};        // enemy projectile speed, %
    static final int[] SK_AMMO = {100, 100, 100};       // ammo per pickup, %
    static final int[] SK_KEEP = {50, 70, 55};          // % of the level's candy pickups that are placed (not in boss arenas;
                                                        // easy halves the damage you take, so it needs fewer of them)
    static final int[] SK_KEEP_AMMO = {55, 70, 80};     // % of the level's ammo pickups that are placed (hard has more and
                                                        // tougher monsters, so it keeps the most)
    static final int[] SK_RESPAWN = {400, 600, 900};    // boss-arena pickups come back after this many ticks
    static final int[] SK_SUMMON = {520, 340, 280};     // ticks between boss summons
    static final int[] SK_SUMMAX = {4, 6, 7};           // bosses stop summoning when this many monsters are alive

    // monster tables (index by type)       -  zomb scare wraith witch  PK  skel clown wolf  bat  vamp  giggl count frank drone cybrg spidr prime mummy jagr conq weepr seven
    static final int[] M_HP =    {0,   55,   90,   60,   100, 1700,   50,   70,  150,   20,  110, 2500, 2100,  170,   40,   90,   30, 2400,  110,  70,  60,  70, 2400};
    static final int[] M_SPD =   {0, 2300, 2000, 4000, 1900, 2600, 3300, 2200, 3000, 4600, 2400, 2300, 2800, 1700, 3400, 3500, 5000, 2100, 1700, 4300, 2100, 2900, 2200};
    static final int[] M_MELEE = {0,    8,    8,    9,    7,   18,    9,    7,   14,    4,    8,   20,   18,   12,    0,   12,    5,   22,   13,  11,   9,  10,   18};
    static final int[] M_PAIN =  {0,  190,  110,  150,   90,   18,  170,  150,   70,  220,  100,   14,   16,   60,  170,  120,  210,   10,   60, 150, 160, 120,   12};
    static final int[] M_PROJ = {0, 0, FIREBALL, 0, GREENBALL, BOSSBALL, 0, KNIFE, 0, 0, BOLT, KNIFE, BOLT, ZAP, LASER, 0, 0, ZAP, 0, 0, SHOT, 0, DISC};
    static final int[] M_RCH =   {0,    0,   18,    0,   18,    8,    0,   14,    0,    0,   16,    7,    7,   16,   12,    0,    0,    6,    0,   0,  10,   0,    8};
    static final int[] M_HOVER = {0,    0,    0, 9000,    0,    0,    0,    0,    0, 22000, 2500,   0,    0,    0, 24000,   0,    0,    0,    0,   0,   0, 5000,   0};
    static final int[][] M_SPR = {null,
            {Res.S_ZOMBIE_WALK1, Res.S_ZOMBIE_WALK2, Res.S_ZOMBIE_ATTACK, Res.S_ZOMBIE_PAIN, Res.S_ZOMBIE_FALL, Res.S_ZOMBIE_DEAD},
            {Res.S_SCARECROW_WALK1, Res.S_SCARECROW_WALK2, Res.S_SCARECROW_ATTACK, Res.S_SCARECROW_PAIN, Res.S_SCARECROW_FALL, Res.S_SCARECROW_DEAD},
            {Res.S_WRAITH_WALK1, Res.S_WRAITH_WALK2, Res.S_WRAITH_ATTACK, Res.S_WRAITH_PAIN, Res.S_WRAITH_FALL, Res.S_WRAITH_DEAD},
            {Res.S_WITCH_WALK1, Res.S_WITCH_WALK2, Res.S_WITCH_ATTACK, Res.S_WITCH_PAIN, Res.S_WITCH_FALL, Res.S_WITCH_DEAD},
            {Res.S_BOSS_WALK1, Res.S_BOSS_WALK2, Res.S_BOSS_ATTACK, Res.S_BOSS_PAIN, Res.S_BOSS_FALL, Res.S_BOSS_DEAD},
            {Res.S_SKEL_WALK1, Res.S_SKEL_WALK2, Res.S_SKEL_ATTACK, Res.S_SKEL_PAIN, Res.S_SKEL_FALL, Res.S_SKEL_DEAD},
            {Res.S_CLOWN_WALK1, Res.S_CLOWN_WALK2, Res.S_CLOWN_ATTACK, Res.S_CLOWN_PAIN, Res.S_CLOWN_FALL, Res.S_CLOWN_DEAD},
            {Res.S_WOLF_WALK1, Res.S_WOLF_WALK2, Res.S_WOLF_ATTACK, Res.S_WOLF_PAIN, Res.S_WOLF_FALL, Res.S_WOLF_DEAD},
            {Res.S_BAT_WALK1, Res.S_BAT_WALK2, Res.S_BAT_ATTACK, Res.S_BAT_PAIN, Res.S_BAT_FALL, Res.S_BAT_DEAD},
            {Res.S_VAMP_WALK1, Res.S_VAMP_WALK2, Res.S_VAMP_ATTACK, Res.S_VAMP_PAIN, Res.S_VAMP_FALL, Res.S_VAMP_DEAD},
            {Res.S_GIGGLES_WALK1, Res.S_GIGGLES_WALK2, Res.S_GIGGLES_ATTACK, Res.S_GIGGLES_PAIN, Res.S_GIGGLES_FALL, Res.S_GIGGLES_DEAD},
            {Res.S_COUNT_WALK1, Res.S_COUNT_WALK2, Res.S_COUNT_ATTACK, Res.S_COUNT_PAIN, Res.S_COUNT_FALL, Res.S_COUNT_DEAD},
            {Res.S_FRANK_WALK1, Res.S_FRANK_WALK2, Res.S_FRANK_ATTACK, Res.S_FRANK_PAIN, Res.S_FRANK_FALL, Res.S_FRANK_DEAD},
            {Res.S_DRONE_WALK1, Res.S_DRONE_WALK2, Res.S_DRONE_ATTACK, Res.S_DRONE_PAIN, Res.S_DRONE_FALL, Res.S_DRONE_DEAD},
            {Res.S_CYBORG_WALK1, Res.S_CYBORG_WALK2, Res.S_CYBORG_ATTACK, Res.S_CYBORG_PAIN, Res.S_CYBORG_FALL, Res.S_CYBORG_DEAD},
            {Res.S_SPIDER_WALK1, Res.S_SPIDER_WALK2, Res.S_SPIDER_ATTACK, Res.S_SPIDER_PAIN, Res.S_SPIDER_FALL, Res.S_SPIDER_DEAD},
            {Res.S_PRIME_WALK1, Res.S_PRIME_WALK2, Res.S_PRIME_ATTACK, Res.S_PRIME_PAIN, Res.S_PRIME_FALL, Res.S_PRIME_DEAD},
            {Res.S_MUMMY_WALK1, Res.S_MUMMY_WALK2, Res.S_MUMMY_ATTACK, Res.S_MUMMY_PAIN, Res.S_MUMMY_FALL, Res.S_MUMMY_DEAD},
            {Res.S_JAGUAR_WALK1, Res.S_JAGUAR_WALK2, Res.S_JAGUAR_ATTACK, Res.S_JAGUAR_PAIN, Res.S_JAGUAR_FALL, Res.S_JAGUAR_DEAD},
            {Res.S_CONQ_WALK1, Res.S_CONQ_WALK2, Res.S_CONQ_ATTACK, Res.S_CONQ_PAIN, Res.S_CONQ_FALL, Res.S_CONQ_DEAD},
            {Res.S_WEEPER_WALK1, Res.S_WEEPER_WALK2, Res.S_WEEPER_ATTACK, Res.S_WEEPER_PAIN, Res.S_WEEPER_FALL, Res.S_WEEPER_DEAD},
            {Res.S_SEVEN_WALK1, Res.S_SEVEN_WALK2, Res.S_SEVEN_ATTACK, Res.S_SEVEN_PAIN, Res.S_SEVEN_FALL, Res.S_SEVEN_DEAD}};
    static final int ST_IDLE = 0, ST_CHASE = 1, ST_ATK = 2, ST_PAIN = 3, ST_DIE = 4, ST_DEAD = 5;

    static boolean isMon(int t) { return t > 0 && t < NMON; }

    static boolean isBoss(int t) { return t == BOSS || t == GIGGLES || t == COUNT || t == PRIME || t == SEVEN; }

    static int cool(int c) { return c * SK_COOL[skill] / 100; }

    static int bossIdx = -1, bossMax = 1, bossType;

    // ------------------------------------------------------------------ things
    static final int MAXT = 240;
    static int nt;
    static final int[] tType = new int[MAXT], tX = new int[MAXT], tY = new int[MAXT], tZ = new int[MAXT], tVX = new int[MAXT],
            tVY = new int[MAXT], tVZ = new int[MAXT], tSt = new int[MAXT], tTim = new int[MAXT], tHp = new int[MAXT],
            tCool = new int[MAXT], tAnim = new int[MAXT], tAux = new int[MAXT], tOwn = new int[MAXT];
    static final boolean[] tLos = new boolean[MAXT];

    // ------------------------------------------------------------------ player
    static int bobAmp;
    static int px, py, pa, pz, pvz, pvx, pvy, health, armor, keys, weapons, weapon, pendingWeapon = -1, bob, bobPhase, turnHeld;
    static final int[] ammo = new int[3];
    static final int[] AMAX = {200, 50, 30};
    static final int[] WAMMO = {-1, 0, 1, 0, 2};
    static int wTim, wFrame, wRaise, wSwitch, hurtTim, kills, totalKills, secrets, totalSecrets, ticks, deadTim;
    static boolean dead, onGround = true, exitHit;
    static int flashDmg, flashPick, kick, shake;
    static int noiseX = -1, noiseY, noiseT;
    static int lightningT, lightningBoost, thunderT, bossDeadT = -1;
    static int lastVoiceTick = -999, lowHpWarn;

    // ------------------------------------------------------------------ particles
    static final int MAXP = 96;
    static int np;
    static final int[] pX = new int[MAXP], pY = new int[MAXP], pZ = new int[MAXP], pVX = new int[MAXP], pVY = new int[MAXP],
            pVZ = new int[MAXP], pC = new int[MAXP], pL = new int[MAXP];
    static int P_RED, P_DRED, P_YEL, P_GREEN, P_ORANGE, P_GREY, P_CYAN, P_BONE;

    // ------------------------------------------------------------------ rng
    static int seed = 12345;

    static int rnd() {
        seed = seed * 1103515245 + 12345;
        return (seed >>> 8) & 0xffffff;
    }

    static int rnd(int n) { return n <= 1 ? 0 : rnd() % n; }

    static int rr(int lo, int hi) { return lo + rnd(hi - lo + 1); }

    // ================================================================== level loading

    static void initColors() {
        P_RED = E.nearest(0x8a0a06, 1, Res.FB0);
        P_DRED = E.nearest(0x4a0402, 1, Res.FB0);
        P_GREY = E.nearest(0x707070, 1, Res.FB0);
        P_YEL = E.nearest(0xffd040, Res.FB0, 255);
        P_ORANGE = E.nearest(0xff6010, Res.FB0, 255);
        P_GREEN = E.nearest(0x80ff40, Res.FB0, 255);
        P_CYAN = E.nearest(0x80e0ff, Res.FB0, 255);
        P_BONE = E.nearest(0xd8d0b0, 1, Res.FB0);
    }

    static void load(int lv) throws java.io.IOException {
        level = lv;
        sndWeapon = -1;
        DataInputStream in = new DataInputStream(G.open("/l" + lv + ".bin"));
        in.readByte();
        in.readByte();
        lvName = in.readUTF();
        lvSub = in.readUTF();
        int sky = in.readUnsignedByte();
        lvMusic = in.readUnsignedByte();
        fogR = in.readUnsignedByte(); fogG = in.readUnsignedByte(); fogB = in.readUnsignedByte();
        E.fogK = in.readUnsignedByte();
        lightning = in.readUnsignedByte();
        lvFlags = in.readUnsignedByte();
        int ng = in.readUnsignedByte();
        int[] groups = new int[ng];
        int ngk = 0;
        for (int k = 0; k < ng; k++) {
            int g = in.readShort();
            // cutscene portraits only the chosen cutscene style needs (saves memory)
            if (G.gore ? (g == Res.G_S_CPKID || g == Res.G_S_CPSHRUNK) : (g == Res.G_S_CPGORE || g == Res.G_S_CPMELT)) continue;
            groups[ngk++] = g;
        }
        if (ngk < ng) { int[] g2 = new int[ngk]; System.arraycopy(groups, 0, g2, 0, ngk); groups = g2; }
        nt = 0;                         // drop old things before their sprites are unloaded
        E.require(groups);
        mapW = in.readUnsignedByte();
        mapH = in.readUnsignedByte();
        int sx = in.readShort(), sy = in.readShort(), sa = in.readShort();
        skyTex = sky == 255 ? -1 : sky;
        for (int i = 0; i < 4096; i++) {
            wall[i] = (byte) (Res.T_DOORFRAME + 1); flr[i] = (byte) Res.T_DOORFRAME; cel[i] = (byte) Res.T_DOORFRAME; flag[i] = 0;
            seen[i] = 0; door[i] = 0; baseLight[i] = 20; flick[i] = 0; dstate[i] = 0; dtime[i] = 0; push[i] = 0;
        }
        byte[] row = new byte[mapW];
        for (int a = 0; a < 5; a++) {
            for (int y = 0; y < mapH; y++) {
                in.readFully(row);
                for (int x = 0; x < mapW; x++) {
                    int c = (y << 6) | x;
                    if (a == 0) wall[c] = row[x];
                    else if (a == 1) flr[c] = row[x];
                    else if (a == 2) cel[c] = row[x];
                    else if (a == 3) baseLight[c] = row[x] & 255;
                    else flag[c] = row[x];
                }
            }
        }
        int n = in.readShort();
        nt = 0;
        np = 0;
        totalKills = 0;
        totalSecrets = 0;
        nDoors = 0;
        for (int i = 0; i < 4096; i++) {
            if ((flag[i] & F_SECRET) != 0) totalSecrets++;
            if ((flag[i] & F_DOOR) != 0 && nDoors < doorList.length) doorList[nDoors++] = (short) i;
        }
        // read every thing first: the thinning below needs to know which room each pickup is in
        int[] rt = new int[n], rx = new int[n], ry = new int[n];
        for (int i = 0; i < n; i++) {
            rt[i] = in.readUnsignedByte();
            rx[i] = in.readShort() << 12;
            ry[i] = in.readShort() << 12;
            rt[i] |= (in.readByte() & 255) << 8;      // skill byte (with the teleporter channel/direction bits)
        }
        boolean thin = (lvFlags & LF_RESPAWN) == 0;
        short[] room = thin ? rooms() : null;
        int[] left = null, got = null;
        if (thin) {
            int nr = 0;
            for (int c = 0; c < 4096; c++) if (room[c] >= nr) nr = room[c] + 1;
            left = new int[nr + 1];
            got = new int[nr + 1];
            for (int i = 0; i < n; i++) if (pickKind(rt[i] & 255) >= 0 && ((rt[i] >> 8) & 3) <= skill) left[room[cellOf(rx[i], ry[i])] + 1]++;
        }
        int[] keep = new int[5];
        for (int k = 0; k < 5; k++) keep[k] = 50 + k * 9;
        nPend = 0;
        idolLevel = false;
        for (int i = 0; i < n; i++) {
            int t = rt[i] & 255;
            int x = rx[i], y = ry[i];
            int sk = (byte) (rt[i] >> 8);
            int aux = (sk >> 2) & 31;         // teleporter channel (bits 2-4) and exit direction (bits 5-6)
            sk &= 3;
            if (sk > skill) continue;
            if (skill == 0 && isMon(t) && !isBoss(t) && (i % 3) == 2) continue;
            if ((rt[i] & 0x8000) != 0 && isMon(t)) {
                // bit 7: an ambush. It stays out of the world until the level's trigger (the idol, the red key)
                if (nPend < pendT.length) { pendT[nPend] = t; pendX[nPend] = x; pendY[nPend] = y; nPend++; totalKills++; }
                continue;
            }
            int pk = pickKind(t);
            if (pk >= 0 && thin) {            // thin out health and ammo pickups (fewer on harder settings)
                int r = room[cellOf(x, y)] + 1;
                left[r]--;
                keep[pk] += pk < 2 ? SK_KEEP[skill] : SK_KEEP_AMMO[skill];
                // ...but a room never loses all of its loot: its last pickup stays (paid for by later ones)
                if (keep[pk] < 100 && (got[r] > 0 || left[r] > 0 || r == 0)) continue;
                keep[pk] -= 100;
                got[r]++;
            }
            int k = spawn(t, x, y);
            if (k >= 0 && (t == TPAD || t == TDEST || t == BOULDER || t == DARTER)) tAux[k] = aux;
            if (t == IDOL) idolLevel = true;
            if (k >= 0 && (tfl[t] & TF_MON) != 0) totalKills++;
        }
        in.close();
        px = sx << 12; py = sy << 12; pa = sa & 4095; pz = 0; pvz = 0; pvx = 0; pvy = 0;
        kills = 0; secrets = 0; ticks = 0; dead = false; deadTim = 0; exitHit = false; bossDeadT = -1; bossIdx = -1;
        flashDmg = 0; flashPick = 0; kick = 0; hurtTim = 0; wTim = 0; wFrame = 0; wRaise = 0; wSwitch = 0; pendingWeapon = -1;
        noiseX = -1; lightningT = 200 + rnd(300); lightningBoost = 0; thunderT = 0; lowHpWarn = 0;
        keys = 0;
        sprint = false; stamina = 1000; teleT = 0; shockOn = false; shockT = 120; mazeState = 0; mazeT = -100; mazeTold = false;
        swR = -1; stompTold = false;
        fallT = 0; safeX = px; safeY = py; plateCell = -1; plateT = 0; spikeOn = false; spikeT = 90; spikeHit = 8;
        radioT = 40; radioLvl = 0; otherT = -1; triggered = false; crushT = 0; painT = -1000;
        nMaze = 0;
        for (int c = 0; c < 4096; c++) {
            boolean sw = wall[c] == (byte) (Res.T_SHIFTWALL + 1);
            if ((sw || flr[c] == (byte) Res.T_SHIFTFLR) && nMaze < mazeList.length) { mazeList[nMaze++] = (short) c; flr[c] = (byte) Res.T_SHIFTFLR; }
        }
        E.resetAnim();
        bakeLights();
        E.setFog(fogR, fogG, fogB);
        flowCell = -1;
    }

    static int pickKind(int t) {
        return t == CANDY ? 0 : t == BUCKET ? 1 : t == BULLETS ? 2 : t == SHELLS ? 3 : t == PUMPKINS ? 4 : -1;
    }

    static int cellOf(int x, int y) {
        return ((y >> 16) << 6) | (x >> 16);
    }

    /** Room number of every open cell (-1 for walls and doors): open cells joined by walls and doors. */
    static short[] rooms() {
        short[] room = new short[4096];
        short[] st = new short[4096];
        for (int c = 0; c < 4096; c++) room[c] = -1;
        short n = 0;
        for (int c = 0; c < 4096; c++) {
            if (room[c] >= 0 || wall[c] != 0 || (flag[c] & F_DOOR) != 0) continue;
            int sp = 0;
            st[sp++] = (short) c;
            room[c] = n;
            while (sp > 0) {
                int k = st[--sp];
                for (int j = 0; j < 4; j++) {
                    int m = j == 0 ? ((k & 63) > 0 ? k - 1 : -1) : j == 1 ? ((k & 63) < 63 ? k + 1 : -1)
                            : j == 2 ? k - 64 : k + 64;
                    if (m < 0 || m >= 4096 || room[m] >= 0 || wall[m] != 0 || (flag[m] & F_DOOR) != 0) continue;
                    room[m] = n;
                    st[sp++] = (short) m;
                }
            }
            n++;
        }
        return room;
    }

    /** Pre-compute light from jack-o-lanterns, candles, lamps and cauldrons (with line of sight). */
    static void bakeLights() {
        for (int i = 0; i < nt; i++) {
            int str = tlight[tType[i]];
            if (str == 0) continue;
            int cx = tX[i] >> 16, cy = tY[i] >> 16, r = str >= 11 ? 4 : 3;
            int tt = tType[i];
            boolean flame = tt == JACK || tt == JACK2 || tt == CANDLES || tt == CAULDRON || tt == CANDELABRA || tt == BRAZIER
                    || tt == TORCH || tt == OFRENDA;
            for (int y = cy - r; y <= cy + r; y++)
                for (int x = cx - r; x <= cx + r; x++) {
                    if (x < 0 || y < 0 || x > 63 || y > 63) continue;
                    int dx = (x << 16) + 32768 - tX[i], dy = (y << 16) + 32768 - tY[i];
                    int d = E.dist(dx, dy);
                    int rr_ = r << 16;
                    if (d >= rr_) continue;
                    int c = (y << 6) | x;
                    if (wall[c] != 0 && (flag[c] & F_DOOR) == 0) {
                        // walls facing the light get lit too (only if the light can see a neighbour)
                    }
                    if (!losCells(tX[i], tY[i], (x << 16) + 32768, (y << 16) + 32768, true)) continue;
                    int dec = (int) ((long) str * (rr_ - d) / rr_);
                    int nl = baseLight[c] - dec;
                    if (nl < 0) nl = 0;
                    if (nl < baseLight[c]) baseLight[c] = nl;
                    if (flame && dec > 2) flick[c] = 1;
                }
        }
    }

    // ================================================================== things

    static int spawn(int t, int x, int y) {
        if (nt >= MAXT) {
            // recycle an old effect
            for (int i = 0; i < nt; i++) if ((tfl[tType[i]] & TF_FX) != 0) { remove(i); break; }
            if (nt >= MAXT) return -1;
        }
        int i = nt++;
        tType[i] = t; tX[i] = x; tY[i] = y; tZ[i] = 0; tVX[i] = 0; tVY[i] = 0; tVZ[i] = 0; tSt[i] = ST_IDLE; tTim[i] = rnd(8);
        tCool[i] = 30 + rnd(30); tAnim[i] = rnd(16); tAux[i] = 0; tOwn[i] = -1; tLos[i] = false;
        if (isMon(t)) {
            tHp[i] = M_HP[t] * (isBoss(t) ? SK_BOSSHP[skill] : SK_HP[skill]) / 100;
            if (isBoss(t)) bossMax = tHp[i];
            tZ[i] = M_HOVER[t];
        } else tHp[i] = t == KEG || t == TOXIC ? 15 : 1;
        return i;
    }

    static void remove(int i) {
        int j = --nt;
        if (i == j) return;
        tType[i] = tType[j]; tX[i] = tX[j]; tY[i] = tY[j]; tZ[i] = tZ[j]; tVX[i] = tVX[j]; tVY[i] = tVY[j]; tVZ[i] = tVZ[j];
        tSt[i] = tSt[j]; tTim[i] = tTim[j]; tHp[i] = tHp[j]; tCool[i] = tCool[j]; tAnim[i] = tAnim[j]; tAux[i] = tAux[j];
        tOwn[i] = tOwn[j]; tLos[i] = tLos[j];
    }

    static int fx(int t, int x, int y, int z, int life) {
        int i = spawn(t, x, y);
        if (i >= 0) { tZ[i] = z; tTim[i] = life; tAux[i] = life; }
        return i;
    }

    // ================================================================== collision

    static boolean solidCell(int c) {
        if (wall[c] == 0) return false;
        int f = flag[c];
        if ((f & F_DOOR) != 0 && door[c] > ((f & F_SECRET) != 0 ? 65535 : 56000)) return false;
        return true;
    }

    static boolean blocked(int x, int y, int r) {
        int x0 = (x - r) >> 16, x1 = (x + r) >> 16, y0 = (y - r) >> 16, y1 = (y + r) >> 16;
        for (int cy = y0; cy <= y1; cy++)
            for (int cx = x0; cx <= x1; cx++) {
                if (cx < 0 || cy < 0 || cx > 63 || cy > 63) return true;
                if (solidCell((cy << 6) | cx)) return true;
            }
        return false;
    }

    /** Is a solid thing (other than self) overlapping position? Returns index or -1. */
    static int thingAt(int x, int y, int r, int self) {
        for (int i = 0; i < nt; i++) {
            if (i == self) continue;
            int t = tType[i];
            if ((tfl[t] & TF_SOLID) == 0) continue;
            if ((tfl[t] & TF_MON) != 0 && tSt[i] >= ST_DIE) continue;
            if (t == BOULDER && tSt[i] != 2) continue;         // only a boulder at rest blocks (a rolling one shoves)
            int rr_ = r + trad[t];
            int dx = tX[i] - x, dy = tY[i] - y;
            if (dx > rr_ || dx < -rr_ || dy > rr_ || dy < -rr_) continue;
            if ((long) dx * dx + (long) dy * dy < (long) rr_ * rr_) return i;
        }
        return -1;
    }

    /** Line of sight on the cell grid. */
    static boolean losCells(int x0, int y0, int x1, int y1, boolean doorsBlock) {
        int dx = x1 - x0, dy = y1 - y0;
        int d = E.dist(dx, dy);
        int steps = (d >> 14) + 1;
        if (steps > 96) return false;
        int sx = dx / steps, sy = dy / steps, x = x0, y = y0;
        int last = -1;
        for (int i = 0; i < steps; i++) {
            x += sx; y += sy;
            int c = ((y >> 16) << 6) | (x >> 16);
            if (c == last) continue;
            last = c;
            if (c < 0 || c >= 4096) return false;
            if (wall[c] != 0) {
                if ((flag[c] & F_DOOR) != 0 && door[c] > 40000) continue;
                if (i == steps - 1) return true;
                return false;
            }
        }
        return true;
    }

    // ================================================================== flow field (monster pathing)

    static final short[] flow = new short[4096];
    static final short[] queue = new short[4096];
    static int flowCell = -1, flowAge;

    static void updateFlow() {
        int pc = ((py >> 16) << 6) | (px >> 16);
        if (pc == flowCell && flowAge < 30) { flowAge++; return; }
        flowCell = pc;
        flowAge = 0;
        for (int i = 0; i < 4096; i++) flow[i] = 9999;
        int h = 0, t = 0;
        flow[pc] = 0;
        queue[t++] = (short) pc;
        while (h < t) {
            int c = queue[h++];
            int d = flow[c] + 1;
            if (d > 60) continue;
            for (int k = 0; k < 4; k++) {
                int n = k == 0 ? c - 1 : k == 1 ? c + 1 : k == 2 ? c - 64 : c + 64;
                if (n < 0 || n >= 4096 || flow[n] <= d) continue;
                if (wall[n] != 0) {
                    int f = flag[n];
                    if ((f & F_DOOR) == 0 || (f & (F_SECRET | F_KRED | F_KBLUE | F_KGOLD)) != 0) continue;
                } else if (flr[n] == (byte) Res.T_PIT) continue;        // monsters walk around pits
                flow[n] = (short) d;
                queue[t++] = (short) n;
            }
        }
    }

    // ================================================================== doors

    static void openDoor(int c, boolean byPlayer) {
        int f = flag[c];
        if ((f & F_DOOR) == 0) return;
        if (byPlayer) {
            int need = (f & F_KRED) != 0 ? 1 : (f & F_KBLUE) != 0 ? 2 : (f & F_KGOLD) != 0 ? 4 : 0;
            if (need != 0 && (keys & need) == 0) {
                if (tCantMsg <= 0) {
                    G.msg(need == 1 ? "You need the RED skull key" : need == 2 ? "You need the BLUE skull key"
                            : idolLevel ? "The seal needs the GOLDEN IDOL" : "You need the GOLD skull key", 0xff4030);
                    Snd.sfx(Snd.CLICK);
                    tCantMsg = 30;
                }
                return;
            }
        } else if ((f & (F_SECRET | F_KRED | F_KBLUE | F_KGOLD)) != 0) return;
        if (dstate[c] == 1 || dstate[c] == 2) { if (dtime[c] >= 0) dtime[c] = 0; return; }
        dstate[c] = 1;
        dtime[c] = 0;
        if ((f & F_SECRET) != 0 && byPlayer) {
            // a Wolfenstein-style pushwall: the block slides away from the player and stays open
            int dx = px - (((c & 63) << 16) + 32768), dy = py - (((c >> 6) << 16) + 32768);
            if ((dx < 0 ? -dx : dx) > (dy < 0 ? -dy : dy)) push[c] = (byte) (dx < 0 ? 0 : 1);
            else push[c] = (byte) (dy < 0 ? 2 : 3);
            secrets++;
            G.msg("A secret is revealed!", 0xc080ff);
            Snd.sfx(Snd.SECRET);
            Snd.sfxAt(Snd.DOOR, (c & 63) << 16, (c >> 6) << 16);
            G.voice(Snd.V_SECRET, "Ooh. Secret stash.", 60);
            dtime[c] = -30000;                        // secrets stay open forever
        } else {
            Snd.sfxAt(Snd.DOOR, (c & 63) << 16, (c >> 6) << 16);
        }
    }

    static int tCantMsg;

    static final short[] doorList = new short[256];
    static int nDoors;

    static void updateDoors() {
        for (int di = 0; di < nDoors; di++) {
            int c = doorList[di];
            int st = dstate[c];
            if (st == 0) continue;
            if (st == 1) {
                door[c] += (flag[c] & F_SECRET) != 0 ? 2300 : 4600;
                if (door[c] >= 65536) { door[c] = 65536; dstate[c] = 2; }
            } else if (st == 2) {
                if (dtime[c] < 0) continue;
                dtime[c]++;
                if (dtime[c] > 110) {
                    // close if nothing in the way
                    int cx = c & 63, cy = c >> 6;
                    boolean busy = (px >> 16) == cx && (py >> 16) == cy;
                    for (int i = 0; i < nt && !busy; i++)
                        if ((tfl[tType[i]] & TF_MON) != 0 && tSt[i] < ST_DIE && (tX[i] >> 16) == cx && (tY[i] >> 16) == cy) busy = true;
                    if (!busy) { dstate[c] = 3; Snd.sfxAt(Snd.DOOR, cx << 16, cy << 16); } else dtime[c] = 90;
                }
            } else if (st == 3) {
                int cx = c & 63, cy = c >> 6;
                boolean busy = (px >> 16) == cx && (py >> 16) == cy;
                for (int i = 0; i < nt && !busy; i++)
                    if ((tfl[tType[i]] & TF_MON) != 0 && tSt[i] < ST_DIE && (tX[i] >> 16) == cx && (tY[i] >> 16) == cy) busy = true;
                if (busy) { dstate[c] = 1; continue; }
                door[c] -= 4600;
                if (door[c] <= 0) { door[c] = 0; dstate[c] = 0; }
            }
        }
    }

    /** Use / bump: the cell in front of the player. */
    static void use(boolean bump) {
        int fx = px + (E.cos(pa) * 3 >> 2), fy = py + (E.sin(pa) * 3 >> 2);
        int c = ((fy >> 16) << 6) | (fx >> 16);
        if (c < 0 || c >= 4096) return;
        int f = flag[c];
        if ((f & F_EXIT) != 0) {
            if (!exitHit) {
                exitHit = true;
                Snd.sfx(Snd.SWITCH);
                G.levelDone();
            }
            return;
        }
        if (!bump && (wall[c] == (byte) (Res.T_SWITCH + 1) || wall[c] == (byte) (Res.T_SWITCH2 + 1))) { toggleMaze(); return; }
        if ((f & F_DOOR) != 0 && door[c] < 65536) openDoor(c, true);
        else if (!bump && wall[c] != 0) Snd.sfx(Snd.CLICK);
    }

    // ================================================================== tick

    static boolean kFwd, kBack, kLeft, kRight, kSL, kSR, kFire, kUse, kJump;

    static void tick() {
        ticks++;
        if (tCantMsg > 0) tCantMsg--;
        updateDoors();
        E.animTick();
        if (!dead) playerTick();
        else {
            deadTim++;
            if (pz > -26000) pz -= 1500;
        }
        updateFlow();
        for (int i = 0; i < nt; i++) {
            int t = tType[i];
            int fl = tfl[t];
            if ((fl & TF_MON) != 0) { if (!freeze || tSt[i] >= ST_DIE) monsterTick(i); }
            else if ((fl & TF_PROJ) != 0) { if (projTick(i)) i--; }
            else if ((fl & TF_FX) != 0) {
                if (--tTim[i] <= 0) { remove(i); i--; continue; }
                tZ[i] += tVZ[i];
            } else if ((fl & TF_PICK) != 0 && !dead) {
                if (pickTick(i)) i--;
            } else if ((t == KEG || t == TOXIC) && tHp[i] <= 0) {
                int x = tX[i], y = tY[i];
                remove(i);
                i--;
                if (t == TOXIC) { fx(FX_GREEN, x, y, 20000, 14); for (int k = 0; k < 10; k++) part(x, y, 20000, rr(-6000, 6000), rr(-6000, 6000), rr(2000, 7000), P_GREEN, 22); }
                explode(x, y, 10000, t == TOXIC ? 170 : 150, 2 << 16, -2);
            } else if (t == BOULDER && tSt[i] == 1) boulderTick(i);
        }
        particlesTick();
        lightsTick();
        hazardsTick();
        if ((lvFlags & LF_RADIO) != 0) radioTick();
        if (otherT >= 0) otherTick();
        if (noiseT > 0 && --noiseT == 0) noiseX = -1;
        if (flashDmg > 0) flashDmg -= 12;
        if (flashPick > 0) flashPick -= 10;
        if (kick > 0) kick -= 2;
        if (shake > 0) shake--;
        if (bossDeadT >= 0 && ++bossDeadT == 90) G.victory();
        if (bossDeadT >= 0 && bossDeadT < 60 && (bossDeadT & 7) == 0) {
            if (bossType == PRIME && (bossDeadT & 15) == 0) spark(bossX, bossY, 60000, 8, P_CYAN);
            if (bossType == SEVEN) {               // the jade king cracks apart
                spark(bossX + rr(-20000, 20000), bossY + rr(-20000, 20000), 40000 + rnd(50000), 8, P_GREEN);
                fx(FX_DUST, bossX + rr(-30000, 30000), bossY + rr(-30000, 30000), rnd(30000), 14);
                if ((bossDeadT & 15) == 0) { Snd.sfxAt(Snd.STOMP, bossX, bossY); shake = 8; }
            } else if (bossType == COUNT) { fx(FX_SMOKE, bossX + rr(-30000, 30000), bossY + rr(-30000, 30000), rnd(30000), 12); Snd.sfxAt(Snd.BAT, bossX, bossY); }
            else explode(bossX + rr(-40000, 40000), bossY + rr(-40000, 40000), 20000 + rnd(30000), 0, 0, -2);
        }
    }

    static int bossX, bossY;

    /** Cutscene tick: only effects, particles and lights move (actors are driven by the script). */
    static void cutTick() {
        ticks++;
        for (int i = 0; i < nt; i++) {
            if ((tfl[tType[i]] & TF_FX) != 0) {
                if (--tTim[i] <= 0) { remove(i); i--; continue; }
                tZ[i] += tVZ[i];
            }
        }
        particlesTick();
        lightsTick();
        if (shake > 0) shake--;
        if (flashPick > 0) flashPick -= 10;
    }

    // ------------------------------------------------------------------ player

    static void playerTick() {
        if (fallT > 0) { fallTick(); return; }
        // turning with acceleration
        if (kLeft || kRight) {
            turnHeld++;
            int sp = turnHeld < 4 ? 36 : turnHeld < 8 ? 58 : 76;
            pa = (pa + (kLeft ? -sp : sp)) & 4095;
        } else turnHeld = 0;
        int fwd = 0, side = 0;
        if (sprint && (!kFwd || stamina <= 0)) { sprint = false; if (stamina <= 0) staminaRest = 45; }
        if (sprint) { stamina -= 9; if (stamina < 0) stamina = 0; }
        else if (staminaRest > 0) staminaRest--;
        else if (stamina < 1000) { stamina += 6; if (stamina > 1000) stamina = 1000; }
        if (kFwd) fwd += sprint ? 11800 : 7400;
        if (kBack) fwd -= 5600;
        if (kSL) side -= 6200;
        if (kSR) side += 6200;
        int wc = ((py >> 16) << 6) | (px >> 16);
        if (onGround && wall[wc] == 0 && flr[wc] == (byte) Res.T_RIVER) {      // wading through the river is slow going
            fwd = fwd * 3 / 5; side = side * 3 / 5;
            if ((fwd != 0 || side != 0) && (ticks & 3) == 0)
                part(px + (E.cos(pa) >> 2), py + (E.sin(pa) >> 2), 3000, rr(-2500, 2500), rr(-2500, 2500), rr(2500, 5000), P_CYAN, 10);
        }
        int c = E.cos(pa), s = E.sin(pa);
        int tvx = (int) (((long) c * fwd - (long) s * side) >> 16);
        int tvy = (int) (((long) s * fwd + (long) c * side) >> 16);
        pvx += (tvx - pvx) / 2;
        pvy += (tvy - pvy) / 2;
        int r = 16000;
        int nx = px + pvx, ny = py + pvy;
        if (noclip) {                       // cheat: walk through walls (but stay inside the map)
            if (nx > 65536 && nx < ((mapW - 1) << 16)) px = nx;
            if (ny > 65536 && ny < ((mapH - 1) << 16)) py = ny;
        } else {
            if (!blocked(nx, py, r) && thingAt(nx, py, r, -1) < 0) px = nx;
            else bumpAt(nx + (pvx > 0 ? r : -r), py);
            if (!blocked(px, ny, r) && thingAt(px, ny, r, -1) < 0) py = ny;
            else bumpAt(px, ny + (pvy > 0 ? r : -r));
        }
        if (kUse) { use(false); kUse = false; }
        // bobbing
        int spd = (pvx < 0 ? -pvx : pvx) + (pvy < 0 ? -pvy : pvy);
        if (spd > 1500 && onGround) bobPhase = (bobPhase + (sprint ? 220 : 150)) & 4095;
        bobAmp += ((spd > 1500 && onGround ? (spd > 7000 ? 65536 : spd * 9) : 0) - bobAmp) >> 2;
        bob = (int) ((long) E.sin(bobPhase) * bobAmp >> 16) / 30;
        // jumping
        if (kJump && onGround) { pvz = 3700; onGround = false; kJump = false; }
        kJump = false;
        if (!onGround) {
            pz += pvz;
            pvz -= 400;
            if (pz <= 0) { pz = 0; pvz = 0; onGround = true; }
        }
        // conveyor belts carry you along
        int pc = ((py >> 16) << 6) | (px >> 16);
        if (onGround && wall[pc] == 0) {
            int f = flr[pc] & 255, cx = 0, cy = 0;
            if (f == Res.T_CONV_N) cy = -2048; else if (f == Res.T_CONV_S) cy = 2048;
            else if (f == Res.T_CONV_E) cx = 2048; else if (f == Res.T_CONV_W) cx = -2048;
            if (cx != 0 && !blocked(px + cx, py, 16000) && thingAt(px + cx, py, 16000, -1) < 0) px += cx;
            if (cy != 0 && !blocked(px, py + cy, 16000) && thingAt(px, py + cy, 16000, -1) < 0) py += cy;
            pc = ((py >> 16) << 6) | (px >> 16);
        }
        // shock floors
        if (shockOn && onGround && (flr[pc] & 255) == Res.T_SHOCK && wall[pc] == 0) {
            if (++shockHit >= 9) {
                shockHit = 0;
                damagePlayer(6, -1);
                spark(px + (E.cos(pa) >> 2), py + (E.sin(pa) >> 2), 6000, 5, P_CYAN);
                Snd.sfx(Snd.ZAPS);
            }
        } else shockHit = 8;
        // episode 5 traps: pits, pressure plates, spike floors
        if (wall[pc] == 0 && !noclip) {
            int fl = flr[pc] & 255;
            if (onGround && fl == Res.T_PIT) { startFall(); return; }
            if (onGround && fl != Res.T_SPIKES && (flag[pc] & F_HURT) == 0) { safeX = px; safeY = py; }
            if (onGround && fl == Res.T_PPLATE) {
                if (pc != plateCell || ticks - plateT > 40) { plateCell = pc; plateT = ticks; trap(); }
            } else if (fl != Res.T_PPLATE) plateCell = -1;
            if (spikeOn && onGround && fl == Res.T_SPIKES) {
                if (++spikeHit >= 8) {
                    spikeHit = 0;
                    damagePlayer(8, -1);
                    blood(px + (E.cos(pa) >> 2), py + (E.sin(pa) >> 2), 6000, 3);
                }
            } else spikeHit = 7;
            if ((tips & 7) != 7 && (ticks & 7) == 0) lookAhead();
        }
        // teleporters
        if (teleT > 0) teleT--;
        else teleport();
        // hurt floors
        if ((flag[pc] & F_HURT) != 0 && onGround && wall[pc] == 0) {
            if (++hurtTim >= 14) {
                hurtTim = 0;
                damagePlayer(flr[pc] == Res.T_LAVA || flr[pc] == Res.T_XLAVA ? 10 : flr[pc] == Res.T_WATER ? 3 : 6, -1);
            }
        } else hurtTim = 10;
        weaponTick();
        if (health < 25 && health > 0 && ticks - lowHpWarn > 600) {
            lowHpWarn = ticks;
            G.voice(Snd.V_LOWHP, "I need candy. Lots of candy.", 0);
        }
    }

    // ------------------------------------------------------------------ episode 4 mechanics: sprint, teleporters, conveyors, shock floors, shifting maze

    static boolean sprint, shockOn, mazeTold, teleTold, stompTold, noclip, freeze;
    static int stamina = 1000, staminaRest, teleT, shockT, shockHit, mazeState, mazeT, nMaze;
    static final short[] mazeList = new short[512];
    static int swX, swY, swR = -1;            // Frankenstein Prime's stomp shockwave ring
    static boolean swHit;

    static void teleport() {
        for (int i = 0; i < nt; i++) {
            if (tType[i] != TPAD) continue;
            int dx = tX[i] - px, dy = tY[i] - py;
            if (dx > 20000 || dx < -20000 || dy > 20000 || dy < -20000) continue;
            int ch = tAux[i] & 7;
            for (int j = 0; j < nt; j++) {
                if (tType[j] != TDEST || (tAux[j] & 7) != ch) continue;
                fx(FX_SMOKE, px, py, 8000, 12);
                int x = tX[j], y = tY[j];
                for (int k = 0; k < nt; k++) {        // telefrag whatever stands on the arrival point
                    if (!isMon(tType[k]) || tSt[k] >= ST_DIE) continue;
                    int ex = tX[k] - x, ey = tY[k] - y;
                    if (ex < 30000 && ex > -30000 && ey < 30000 && ey > -30000) damageThing(k, isBoss(tType[k]) ? 60 : 999, -1, 2);
                }
                px = x; py = y; pvx = 0; pvy = 0;
                pa = ((tAux[j] >> 3) & 3) << 10;
                teleT = 30;
                flashPick = 120;
                fx(FX_SMOKE, x, y, 8000, 12);
                Snd.sfx(Snd.TELE);
                noiseX = x; noiseY = y; noiseT = 20;
                if (!teleTold) { teleTold = true; G.voice(Snd.V_TELE, "Whoa. That tickles.", 0); }
                return;
            }
        }
    }

    /** Shock floors switch on and off; Frankenstein Prime's shockwave rings spread out. */
    static void hazardsTick() {
        if (E.pairOn[0] != null) {
            if (--shockT <= 0) {
                shockOn = !shockOn;
                shockT = shockOn ? 55 : 80;
                if (shockOn && near(Res.T_SHOCK)) Snd.sfx(Snd.BUZZ);
            }
            boolean show = shockOn || (shockT < 18 && (shockT & 4) != 0);
            E.showPair(0, show);
        }
        if (E.pairOn[1] != null) {              // spike floors: down a while, a warning rattle, up a while
            if (--spikeT <= 0) {
                spikeOn = !spikeOn;
                spikeT = spikeOn ? 34 : 62;
                if (spikeOn && near(Res.T_SPIKES)) Snd.sfx(Snd.SPIKES);
            }
            if (!spikeOn && spikeT == 14 && near(Res.T_SPIKES)) Snd.sfx(Snd.CLICK);
            E.showPair(1, spikeOn || (spikeT < 14 && (spikeT & 4) != 0));
        }
        if (swR >= 0) {
            swR += 8500;
            if (swR > (9 << 16)) swR = -1;
            else if (!swHit && !dead) {
                int dp = E.dist(px - swX, py - swY) - swR;
                if (dp < 22000 && dp > -22000 && pz < 7000) {
                    swHit = true;
                    damagePlayer(rr(14, 22), bossIdx);
                    pvz = 2600; pz = 1; onGround = false;
                    shake = 10;
                }
            }
        }
    }

    static boolean near(int tex) {
        int cx = px >> 16, cy = py >> 16;
        for (int y = cy - 4; y <= cy + 4; y++)
            for (int x = cx - 4; x <= cx + 4; x++)
                if (x >= 0 && y >= 0 && x < 64 && y < 64 && (flr[(y << 6) | x] & 255) == tex) return true;
        return false;
    }

    // ------------------------------------------------------------------ episode 5 mechanics: pits, dart traps, spike floors,
    // the rolling boulder, ambushes, the radio and the Other World

    static int fallT, safeX, safeY, plateCell = -1, plateT, spikeT, spikeHit, radioT, radioLvl, otherT = -1, crushT, tips;
    static boolean spikeOn, triggered, radioTold, otherTold, idolLevel;
    static final int[] pendT = new int[40], pendX = new int[40], pendY = new int[40];
    static int nPend;
    static final int BOULDER_SPD = 11000;      // faster than walking (7400), a little slower than sprinting (11800)

    static void startFall() {
        fallT = 1;
        onGround = false;
        sprint = false;
        Snd.sfx(Snd.FALL);
    }

    /** Down the pit: the view sinks into the dark, then Butch climbs back out where he last stood, bruised. */
    static void fallTick() {
        fallT++;
        pz -= 700 + fallT * 140;
        if (pz < -30000) pz = -30000;
        if (fallT >= 24) {
            fallT = 0;
            px = safeX; py = safeY; pz = 0; pvx = 0; pvy = 0; pvz = 0; onGround = true;
            damagePlayer(15, -1);
            if (!dead && (tips & 8) == 0) { tips |= 8; G.voice(Snd.V_PIT, "Watch your step.", 0); G.tip("Sprint (double-tap UP) before jumping wide pits"); }
        }
    }

    /** First sight of a new kind of trap: a tip. */
    static void lookAhead() {
        int cx = px >> 16, cy = py >> 16;
        for (int y = cy - 3; y <= cy + 3; y++)
            for (int x = cx - 3; x <= cx + 3; x++) {
                if (x < 0 || y < 0 || x > 63 || y > 63) continue;
                int c = (y << 6) | x;
                if (wall[c] != 0) continue;
                int f = flr[c] & 255;
                if (f == Res.T_PIT && (tips & 1) == 0) { tips |= 1; G.tip("A pit! JUMP (#) over it"); return; }
                if (f == Res.T_PPLATE && (tips & 2) == 0) { tips |= 2; G.tip("Pressure plates: JUMP (#) over them"); return; }
                if ((f == Res.T_SPIKES || f == Res.T_SPIKESOFF) && (tips & 4) == 0) { tips |= 4; G.tip("Spike traps: cross while they're down"); return; }
            }
    }

    /** A pressure plate went click: every dart trap nearby fires across its corridor. */
    static void trap() {
        Snd.sfx(Snd.CLICK);
        int cx = px >> 16, cy = py >> 16;
        boolean any = false;
        for (int i = 0; i < nt; i++) {
            if (tType[i] != DARTER) continue;
            int dx = (tX[i] >> 16) - cx, dy = (tY[i] >> 16) - cy;
            if (dx > 5 || dx < -5 || dy > 5 || dy < -5) continue;
            int a = ((tAux[i] >> 3) & 3) << 10;
            int k = spawn(DART, tX[i] - (E.cos(a) * 22 >> 6), tY[i] - (E.sin(a) * 22 >> 6));     // out of the wall behind it
            if (k < 0) continue;
            int sp = 22 * SK_PSPD[skill] / 100;
            tVX[k] = E.cos(a) * sp >> 6;
            tVY[k] = E.sin(a) * sp >> 6;
            tZ[k] = 24000 + rnd(14000);
            tOwn[k] = i;
            any = true;
        }
        if (any) Snd.sfx(Snd.DARTS);
    }

    /** The level's big moment (the idol is lifted, the red key is taken): ambushers appear, boulders drop, the Other World. */
    static void trigger() {
        if (triggered) return;
        triggered = true;
        boolean other = (lvFlags & LF_OTHER) != 0;
        for (int k = 0; k < nPend; k++) {
            int i = spawn(pendT[k], pendX[k], pendY[k]);
            if (i < 0) continue;
            if (other) { tSt[i] = ST_CHASE; tCool[i] = 40 + rnd(40); }
            if (!other) fx(FX_DUST, pendX[k], pendY[k], 8000, 12);
        }
        nPend = 0;
        for (int i = 0; i < nt; i++) {          // walls that move: the way back seals, a way out grinds open
            if (tType[i] != TRIGWALL) continue;
            int c = cellOf(tX[i], tY[i]);
            if (wall[c] != 0) wall[c] = 0;
            else {
                int nb = 0;
                for (int k = 0; k < 4 && nb == 0; k++) {
                    int n = k == 0 ? c - 1 : k == 1 ? c + 1 : k == 2 ? c - 64 : c + 64;
                    if (wall[n] != 0 && (flag[n] & F_DOOR) == 0) nb = wall[n];
                }
                wall[c] = (byte) (nb != 0 ? nb : Res.T_TSTONE + 1);
                for (int k = 0; k < nt; k++)
                    if (isMon(tType[k]) && tSt[k] < ST_DIE && !isBoss(tType[k]) && cellOf(tX[k], tY[k]) == c) { hitKind = 2; kill(k, true); }
            }
            fx(FX_DUST, tX[i], tY[i], 10000, 16);
            Snd.sfxAt(Snd.STOMP, tX[i], tY[i]);
            flowCell = -1;
        }
        boolean drop = false;
        for (int i = 0; i < nt; i++)
            if (tType[i] == BOULDER && tSt[i] == 0) { tSt[i] = 1; tTim[i] = -24; tVX[i] = 0; tZ[i] = 110000; drop = true; }
        if (drop) {
            shake = 12;
            Snd.sfx(Snd.BOULDER);
            G.msg("The temple shakes... RUN!", 0xff5030);
            G.voice(Snd.V_IDOL, "Uh oh.", 0);
        }
        if (other) {
            otherT = 0;
            Snd.sfx(Snd.SIREN);
        }
    }

    /** A rolling boulder: drops out of the ceiling, rolls straight on, flattens monsters and shoves (or squashes) Butch. */
    static void boulderTick(int i) {
        if (tTim[i] < 0) {
            tTim[i]++;
            if (tTim[i] > -12 && tZ[i] > 0) {
                tZ[i] -= 11000;
                if (tZ[i] <= 0) {
                    tZ[i] = 0;
                    shake = 16;
                    Snd.sfxAt(Snd.STOMP, tX[i], tY[i]);
                    for (int k = 0; k < 3; k++) fx(FX_DUST, tX[i] + rr(-30000, 30000), tY[i] + rr(-30000, 30000), rnd(16000), 16);
                }
            } else if ((tTim[i] & 7) == 0) shake = 5;
            return;
        }
        int dir = (tAux[i] >> 3) & 3;
        if (tVX[i] < BOULDER_SPD) tVX[i] += 700;
        int sp = tVX[i];
        int ux = dir == 0 ? 1 : dir == 2 ? -1 : 0, uy = dir == 1 ? 1 : dir == 3 ? -1 : 0;
        int nx = tX[i] + ux * sp, ny = tY[i] + uy * sp;
        int r = trad[BOULDER];
        tAnim[i]++;
        if (blocked(nx, ny, r)) {                // smashes into the wall and stays there for good
            tSt[i] = 2;
            shake = 18;
            Snd.sfxAt(Snd.STOMP, tX[i], tY[i]);
            Snd.sfxAt(Snd.EXPLODE, tX[i], tY[i]);
            for (int k = 0; k < 4; k++) fx(FX_DUST, tX[i] + ux * r + rr(-24000, 24000), tY[i] + uy * r + rr(-24000, 24000), rnd(24000), 16);
            for (int k = 0; k < 12; k++) part(tX[i] + ux * r, tY[i] + uy * r, 30000, rr(-6000, 6000), rr(-6000, 6000), rr(1000, 7000), P_GREY, 24);
            return;
        }
        for (int k = 0; k < nt; k++) {           // whatever stands in the way is flattened
            int tk = tType[k];
            if (!isMon(tk) || tSt[k] >= ST_DIE || isBoss(tk)) continue;
            int ex = tX[k] - nx, ey = tY[k] - ny, rr_ = r + trad[tk];
            if (ex < rr_ && ex > -rr_ && ey < rr_ && ey > -rr_) { hitKind = 2; kill(k, tk != CONQ && tk != WEEPER); }
        }
        if (crushT > 0) crushT--;
        if (!dead) {
            int ex = px - nx, ey = py - ny;
            int along = ex * ux + ey * uy, lat = ex * uy - ey * ux;
            if (lat < 0) lat = -lat;
            int reach = r + 16000;
            if (along >= -8000 && along < reach && lat < reach - 2000) {
                int push = reach + 1000 - along;
                int qx = px + ux * push, qy = py + uy * push;
                boolean ok = !blocked(qx, qy, 16000);
                if (!ok) {                       // can't go forward: slip out to the side Butch is already leaning to
                    int side = (ex * uy - ey * ux) >= 0 ? 1 : -1;
                    int sx = px + uy * side * (reach - lat + 1000), sy = py - ux * side * (reach - lat + 1000);
                    if (!blocked(sx, sy, 16000)) { qx = sx; qy = sy; ok = true; }
                }
                if (ok) {
                    px = qx; py = qy;
                    if (crushT == 0) { crushT = 12; damagePlayer(28, -1); kick = 12; Snd.sfx(Snd.HIT); }
                } else {
                    damagePlayer(999, -1);       // pinned against the wall
                    blood(px, py, 20000, 12);
                }
            }
        }
        tX[i] = nx; tY[i] = ny;
        if ((tAnim[i] % 9) == 0) Snd.sfxAt(Snd.BOULDER, nx, ny);
        if (E.dist(px - nx, py - ny) < (7 << 16) && shake < 3) shake = 3;
        if ((tAnim[i] & 3) == 0) part(nx - ux * r, ny - uy * r, 2000, rr(-2000, 2000), rr(-2000, 2000), rr(1000, 3000), P_GREY, 14);
    }

    /** The radio: static that gets faster the closer a monster is (the fog hides them; the radio doesn't). */
    static void radioTick() {
        if (dead || radioT-- > 0) return;
        int best = 1 << 30;
        for (int i = 0; i < nt; i++) {
            if (!isMon(tType[i]) || tSt[i] >= ST_DIE) continue;
            int dx = tX[i] - px, dy = tY[i] - py;
            if (dx > (10 << 16) || dx < -(10 << 16) || dy > (10 << 16) || dy < -(10 << 16)) continue;
            int d = E.dist(dx, dy);
            if (d < best) best = d;
        }
        if (best >= (10 << 16)) { radioT = 10; radioLvl = 0; return; }
        radioLvl = best < (3 << 16) ? 3 : best < (6 << 16) ? 2 : 1;
        radioT = radioLvl == 3 ? 6 : radioLvl == 2 ? 13 : 24;
        Snd.sfx(Snd.STATIC);
        if (!radioTold) { radioTold = true; G.voice(Snd.V_RADIO, "My radio's acting up.", 0); }
    }

    /** The siren has sounded: the world fades to black, and comes back rusted, bloody and dark. */
    static void otherTick() {
        otherT++;
        if (otherT <= 40) {                      // fade the fog to black, then to blood red
            int k = otherT * 256 / 40;
            E.setFog(fogR + (8 - fogR) * k / 256, fogG + (0 - fogG) * k / 256, fogB + (0 - fogB) * k / 256);
            if (otherT == 1) G.msg("A siren wails over the town...", 0xff6040);
        }
        if (otherT == 40) {
            for (int c = 0; c < 4096; c++) {
                wall[c] = remap(wall[c], true);
                flr[c] = remap(flr[c], false);
                cel[c] = remap(cel[c], false);
            }
            if (skyTex == Res.T_SKY7) skyTex = Res.T_SKY8;
            E.fogK = E.fogK * 4 / 5;
            E.lastEye = -1;
            fogR = 70; fogG = 4; fogB = 2;
            shake = 10;
            flashDmg = 160;
            Snd.music(Snd.M_L13 + 1);            // the factory's grinding beat suits the Other World
        }
        if (otherT > 40 && otherT <= 70) {
            int k = (otherT - 40) * 256 / 30;
            E.setFog(8 + (70 - 8) * k / 256, 4 * k / 256, 2 * k / 256);
        }
        if (otherT == 80 && !otherTold) { otherTold = true; G.voice(Snd.V_OTHER, "Okay. That's new.", 0); }
        if (otherT > 80) otherT = -1;
    }

    static byte remap(byte b, boolean isWall) {
        int v = (b & 255) - (isWall ? 1 : 0);
        if (isWall && b == 0) return 0;
        int n = v == Res.T_ADOBE || v == Res.T_TSTONE ? Res.T_RUST : v == Res.T_ADOBEWIN ? Res.T_RUSTWIN
                : v == Res.T_MURAL || v == Res.T_HUT || v == Res.T_FOLIAGE || v == Res.T_THATCH ? Res.T_RUSTGRATE
                : v == Res.T_JMUD || v == Res.T_JGRASS || v == Res.T_PLANKS || v == Res.T_TFLOOR || v == Res.T_TCEIL ? Res.T_RUSTFLOOR : v;
        return (byte) (n + (isWall ? 1 : 0));
    }

    static boolean pitAt(int x, int y) {
        int c = ((y >> 16) << 6) | (x >> 16);
        return c >= 0 && c < 4096 && wall[c] == 0 && flr[c] == (byte) Res.T_PIT;
    }

    /** A mummy that was only shot gets back up after a while... unless the shovel or a blast finishes it on the ground. */
    static void mummyRise(int i) {
        if (E.dist(px - tX[i], py - tY[i]) < 90000 || thingAt(tX[i], tY[i], trad[MUMMY], i) >= 0) { tCool[i] = 10; return; }
        tVY[i] = 2;
        tSt[i] = ST_PAIN;
        tTim[i] = 16;
        tHp[i] = M_HP[MUMMY] * SK_HP[skill] / 200;
        fx(FX_DUST, tX[i], tY[i], 6000, 14);
        Snd.sfxAt(Snd.MUMMY, tX[i], tY[i]);
        if ((tips & 16) == 0) { tips |= 16; G.voice(Snd.V_RISE, "Stay down!", 0); G.tip("Mummies get back up! Shovel or blast them while they're down"); }
    }

    static boolean downedMummy(int i) {
        return tType[i] == MUMMY && tVY[i] == 1 && tSt[i] >= ST_DIE;
    }

    static void finishMummy(int i, boolean blast) {
        tVY[i] = 3;
        kills++;
        fx(FX_DUST, tX[i], tY[i], 4000, 14);
        for (int k = 0; k < 8; k++) part(tX[i], tY[i], 8000, rr(-4000, 4000), rr(-4000, 4000), rr(1000, 5000), P_BONE, 20);
        if (blast) { tType[i] = GIBS; tSt[i] = ST_DEAD; }
        Snd.sfxAt(Snd.MDIE, tX[i], tY[i]);
        sayKill(13);
    }

    static int hitKind = 2;

    /** A lever was pulled: every shifting wall in the level drops into the floor and every hidden one rises. */
    static void toggleMaze() {
        if (ticks - mazeT < 15) return;
        mazeT = ticks;
        mazeState ^= 1;
        int pc = ((py >> 16) << 6) | (px >> 16);
        for (int k = 0; k < nMaze; k++) {
            int c = mazeList[k];
            if (wall[c] != 0) { wall[c] = 0; continue; }
            if (c == pc) continue;
            for (int i = 0; i < nt; i++)               // anything caught in a rising wall is crushed
                if (isMon(tType[i]) && tSt[i] < ST_DIE && !isBoss(tType[i]) && ((tY[i] >> 16) << 6 | (tX[i] >> 16)) == c) { hitKind = 2; kill(i, tType[i] != SPIDER && tType[i] != DRONE); }
            wall[c] = (byte) (Res.T_SHIFTWALL + 1);
        }
        byte s1 = (byte) (Res.T_SWITCH + 1), s2 = (byte) (Res.T_SWITCH2 + 1);
        for (int c = 0; c < 4096; c++) {
            if (wall[c] == s1) wall[c] = s2;
            else if (wall[c] == s2) wall[c] = s1;
        }
        flowCell = -1;
        shake = 10;
        Snd.sfx(Snd.SWITCH);
        Snd.sfx(Snd.STOMP);
        if (!mazeTold) { mazeTold = true; G.voice(Snd.V_SHIFT, "Did the walls just move?", 0); }
        else G.msg("The walls shift...", 0x80e0ff);
    }

    static void bumpAt(int x, int y) {
        int c = ((y >> 16) << 6) | (x >> 16);
        if (c < 0 || c >= 4096 || !kFwd) return;
        int f = flag[c];
        if ((f & F_DOOR) != 0 && (f & F_SECRET) == 0 && dstate[c] == 0) openDoor(c, true);
        else if ((f & F_EXIT) != 0) use(true);
    }

    static boolean god;
    static int painT = -1000;
    static final int[] dmgLog = new int[NTYPE];      // damage taken per source type (testing aid)

    static void damagePlayer(int d, int from) {
        if (dead || d <= 0 || god) return;
        d = d * SK_DMG[skill] / 100;
        if (d < 1) d = 1;
        dmgLog[from >= 0 && from < nt ? tType[from] : 0] += d;
        if (armor > 0) {
            int a = d / 2;
            if (a > armor) a = armor;
            armor -= a;
            d -= a;
        }
        health -= d;
        flashDmg = 90 + d * 4;
        if (flashDmg > 170) flashDmg = 170;
        kick = 10;
        G.face(1, 12);
        if (health <= 0) {
            health = 0;
            dead = true;
            G.died();                    // switches to the death music first...
            Snd.voice(Snd.V_DIE);        // ...then the scream plays over it
        } else {
            Snd.sfx(Snd.HURT);
            // a grunt now and then, not on every hit: each voice line opens a new player, and a boss fight is a lot of hits
            if (ticks - painT > 100 && rnd(2) == 0) { painT = ticks; Snd.voice(rnd(2) == 0 ? Snd.V_PAIN1 : Snd.V_PAIN2); }
        }
    }

    // ------------------------------------------------------------------ weapons

    static final int WSHOVEL = 0, WREV = 1, WSHOT = 2, WTOMMY = 3, WLAUNCH = 4;
    static final String[] WNAME = {"SHOVEL", "SILVER .44", "BOOMSTICK", "TOMMY GUN", "PUMPKIN LAUNCHER"};

    static boolean hasAmmo(int w) {
        return WAMMO[w] < 0 || ammo[WAMMO[w]] > 0;
    }

    static void selectWeapon(int w) {
        if ((weapons & (1 << w)) == 0 || w == weapon) return;
        pendingWeapon = w;
    }

    static void cycleWeapon(int dir) {
        int w = pendingWeapon >= 0 ? pendingWeapon : weapon;
        for (int k = 0; k < 5; k++) {
            w = (w + dir + 5) % 5;
            if ((weapons & (1 << w)) != 0 && hasAmmo(w)) { selectWeapon(w); return; }
        }
    }

    static final int[] PREF = {WTOMMY, WSHOT, WREV, WLAUNCH, WSHOVEL};

    static void autoSwitch() {
        for (int k = 0; k < PREF.length; k++) {
            int w = PREF[k];
            if ((weapons & (1 << w)) != 0 && hasAmmo(w)) { selectWeapon(w); return; }
        }
    }

    static final int[] WSND = {Snd.SWING, Snd.REVOLVER, Snd.SHOTGUN, Snd.TOMMY, Snd.LAUNCH};
    static int sndWeapon = -1;

    static void weaponTick() {
        int sw = pendingWeapon >= 0 ? pendingWeapon : weapon;
        if (sw != sndWeapon) { sndWeapon = sw; Snd.weapon(WSND[sw]); }   // have the gun's sound ready
        if (pendingWeapon >= 0 && wTim == 0) {
            wSwitch += 6;
            if (wSwitch >= 24) { weapon = pendingWeapon; pendingWeapon = -1; }
            return;
        }
        if (pendingWeapon < 0 && wSwitch > 0) { wSwitch -= 6; if (wSwitch < 0) wSwitch = 0; }
        if (wTim > 0) {
            wTim--;
            int w = weapon;
            if (w == WSHOVEL) {
                wFrame = wTim > 7 ? 1 : wTim > 3 ? 2 : 0;
                if (wTim == 7) meleeHit();
            } else if (w == WREV) wFrame = wTim > 4 ? 1 : 0;
            else if (w == WSHOT) {
                wFrame = wTim > 17 ? 1 : (wTim > 6 && wTim < 14) ? 2 : 0;
                if (wTim == 12) Snd.sfx(Snd.RELOAD);
            } else if (w == WTOMMY) wFrame = wTim > 0 ? 1 + (ticks & 1) : 0;
            else if (w == WLAUNCH) wFrame = wTim > 13 ? 1 : 0;
            return;
        }
        wFrame = 0;
        if (!kFire || wSwitch > 0) return;
        if (!hasAmmo(weapon)) {
            autoSwitch();
            return;
        }
        int w = weapon;
        if (w != WSHOVEL) {
            ammo[WAMMO[w]]--;
            noiseX = px; noiseY = py; noiseT = 6;
            flashLight(px, py, 6);
        }
        switch (w) {
            case WSHOVEL: wTim = 11; wFrame = 1; Snd.sfx(Snd.SWING); break;
            case WREV: wTim = 7; wFrame = 1; kick = 6; Snd.sfx(Snd.REVOLVER); hitscan(1, 12, 22, 34); break;
            case WSHOT: wTim = 22; wFrame = 1; kick = 10; Snd.sfx(Snd.SHOTGUN); hitscan(7, 70, 8, 14); break;
            case WTOMMY: wTim = 3; wFrame = 1; kick = 4; Snd.sfx(Snd.TOMMY); hitscan(1, 40, 11, 17); break;
            case WLAUNCH: {
                wTim = 18; wFrame = 1; kick = 8; Snd.sfx(Snd.LAUNCH);
                int i = spawn(PBOMB, px + (E.cos(pa) >> 2), py + (E.sin(pa) >> 2));
                if (i >= 0) {
                    tVX[i] = E.cos(pa) * 21 >> 6; tVY[i] = E.sin(pa) * 21 >> 6; tZ[i] = 24000 + pz; tOwn[i] = -2;
                }
                break;
            }
        }
    }

    static void meleeHit() {
        int best = -1, bd = 70000;
        for (int i = 0; i < nt; i++) {
            int t = tType[i];
            if ((tfl[t] & TF_SHOOT) == 0) continue;
            if ((tfl[t] & TF_MON) != 0 && tSt[i] >= ST_DIE && !downedMummy(i)) continue;
            int dx = tX[i] - px, dy = tY[i] - py;
            int d = E.dist(dx, dy) - trad[t];
            if (d > 62000 || d > bd) continue;
            int a = (E.atan2(dy, dx) - pa) & 4095;
            if (a > 2048) a -= 4096;
            if (a < -380 || a > 380) continue;
            bd = d;
            best = i;
        }
        if (best >= 0) {
            Snd.sfx(Snd.HIT);
            damageThing(best, rr(30, 46), -1, 1);
            if (isMon(tType[best]) && tSt[best] >= ST_DIE && rnd(3) == 0) G.voice(Snd.V_SHOVEL, "Dig that!", 0);
        }
    }

    /** Ray-march the grid to find the wall distance (Q16) along angle a. */
    static int wallDist(int a) {
        int c = E.cos(a), s = E.sin(a);
        int x = px, y = py;
        for (int d = 0; d < (40 << 16); d += 8192) {
            x += c >> 3; y += s >> 3;
            int cell = ((y >> 16) << 6) | (x >> 16);
            if (cell < 0 || cell >= 4096) return d;
            if (wall[cell] != 0) {
                if ((flag[cell] & (F_DOOR | F_SECRET)) == (F_DOOR | F_SECRET)) {
                    int op = door[cell];
                    if (op == 0) return d;
                    if (op >= 65536) continue;
                    int pd = push[cell];
                    int pos = (pd < 2 ? x : y) & 0xffff;
                    if ((pd & 1) == 0 ? pos >= op : pos < 65536 - op) return d;
                    continue;
                }
                if ((flag[cell] & F_DOOR) != 0) {
                    if (door[cell] > 50000) continue;
                    boolean vert = solidCell(cell - 64) && solidCell(cell + 64);
                    int pos = vert ? (x & 0xffff) : (y & 0xffff);
                    if (pos > 26000 && pos < 39500) return d;
                    continue;
                }
                return d;
            }
        }
        return 40 << 16;
    }

    static void hitscan(int pellets, int spread, int dmin, int dmax) {
        for (int p = 0; p < pellets; p++) {
            int a = (pa + (spread > 0 ? rnd(spread * 2 + 1) - spread : 0)) & 4095;
            int c = E.cos(a), s = E.sin(a);
            int wd = wallDist(a);
            int best = -1, bestAlong = wd;
            for (int i = 0; i < nt; i++) {
                int t = tType[i];
                if ((tfl[t] & TF_SHOOT) == 0) continue;
                if ((tfl[t] & TF_MON) != 0 && tSt[i] >= ST_DIE) continue;
                int dx = tX[i] - px, dy = tY[i] - py;
                int along = (int) (((long) dx * c + (long) dy * s) >> 16);
                if (along <= 0 || along >= bestAlong) continue;
                int perp = (int) (((long) dx * -s + (long) dy * c) >> 16);
                if (perp < 0) perp = -perp;
                int rad = trad[t] + 6000 + along / 40;
                if (perp < rad) { best = i; bestAlong = along; }
            }
            if (best >= 0) {
                damageThing(best, rr(dmin, dmax), -1, 0);
            } else {
                int hx = px + (int) ((long) c * (wd - 3000) >> 16), hy = py + (int) ((long) s * (wd - 3000) >> 16);
                fx(FX_PUFF, hx, hy, 26000 + pz + rr(-6000, 6000), 8);
                spark(hx, hy, 30000 + pz, 3, P_YEL);
            }
        }
    }

    // ------------------------------------------------------------------ damage

    /** kind: 0 bullet, 1 melee, 2 explosion */
    static void damageThing(int i, int d, int src, int kind) {
        int t = tType[i];
        if (t == KEG || t == TOXIC) {
            tHp[i] -= d;
            spark(tX[i], tY[i], 20000, 4, P_YEL);
            return;
        }
        if (downedMummy(i) && kind != 0) { finishMummy(i, kind == 2); return; }
        if (!isMon(t) || tSt[i] >= ST_DIE) return;
        tHp[i] -= d;
        int bz = t == BOSS || t == GIGGLES || t == PRIME || t == SEVEN ? 60000 : t == COUNT ? 52000 : t == BAT || t == DRONE ? tZ[i] + 8000
                : t == SPIDER ? 12000 : t == JAGUAR ? 30000 : 36000;
        if (t == WRAITH || t == WEEPER) spark(tX[i], tY[i], t == WEEPER ? bz + 6000 : bz, 5, P_CYAN);
        else if (t == MUMMY) { spark(tX[i], tY[i], bz, 4, P_BONE); fx(FX_DUST, tX[i], tY[i], bz - 12000, 6); }
        else if (t == SEVEN) { spark(tX[i], tY[i], bz, 5, P_GREEN); spark(tX[i], tY[i], bz, 2, P_BONE); }
        else if (t == FRANK || t == DRONE || t == SPIDER || t == PRIME) { spark(tX[i], tY[i], bz, 4, P_YEL); spark(tX[i], tY[i], bz, 2, P_CYAN); }
        else if (t == SCARE) { spark(tX[i], tY[i], bz, 3, P_ORANGE); blood(tX[i], tY[i], bz, 3); }
        else if (t == SKEL || t == CONQ) { spark(tX[i], tY[i], bz, 5, P_BONE); fx(FX_PUFF, tX[i], tY[i], bz - 10000, 6); }
        else blood(tX[i], tY[i], bz, t == BAT ? 3 : 6);
        if (tSt[i] == ST_IDLE) { tSt[i] = ST_CHASE; sightSound(t, i); }
        if (tHp[i] <= 0) {
            hitKind = kind;
            kill(i, kind == 2 && tHp[i] < -40 && !isBoss(t) && t != WRAITH && t != SKEL && t != BAT && t != VAMP && t != FRANK && t != DRONE
                    && t != SPIDER && t != CONQ && t != WEEPER);
            return;
        }
        if (t == COUNT && tVX[i] > 30 && rnd(5) == 0) tVX[i] = 2;          // the Count blinks away when hurt
        if (t == VAMP && tSt[i] != ST_ATK && rnd(4) == 0 && blink(i, 2)) return;
        if (rnd(256) < M_PAIN[t] && tSt[i] != ST_ATK) {
            tSt[i] = ST_PAIN;
            tTim[i] = 5;
        } else if (isBoss(t) && rnd(4) == 0) vocal(t == GIGGLES ? Snd.GIGGLE : t == COUNT ? Snd.COUNT : t == PRIME ? Snd.ROBOT : t == SEVEN ? Snd.SEVEN : Snd.BOSS, i,
                t == SEVEN ? 160 : 90);
        if (t == WEEPER && tSt[i] != ST_ATK && rnd(5) == 0) blink(i, 3);
    }

    static void kill(int i, boolean gib) {
        int t = tType[i];
        if (t == MUMMY && !gib && tVY[i] == 0 && hitKind == 0) {      // only shot: it will get back up
            tVY[i] = 1;
            tCool[i] = 150 + rnd(80);
            tSt[i] = ST_DIE;
            tTim[i] = 7;
            Snd.sfxAt(Snd.MUMMY, tX[i], tY[i]);
            fx(FX_DUST, tX[i], tY[i], 6000, 12);
            return;
        }
        hitKind = 2;
        kills++;
        G.face(3, 20);
        if (isBoss(t)) {
            tSt[i] = ST_DIE;
            tTim[i] = 30;
            bossDeadT = 0;
            bossX = tX[i]; bossY = tY[i];
            Snd.sfx(Snd.BOSSDIE);
            if (t == BOSS) G.voice(Snd.V_WIN, "Happy Halloween.", 0);
            else if (t == GIGGLES) G.voice(Snd.V_WIN2, "Show's over.", 0);
            else if (t == PRIME) G.voice(Snd.V_WIN4, "Recycled.", 0);
            else if (t == SEVEN) G.voice(Snd.V_WIN5, "Make that eight.", 0);
            else G.voice(Snd.V_WIN3, "Dawn's coming, pal.", 0);
            swR = -1;
            return;
        }
        if (gib) {
            int x = tX[i], y = tY[i];
            for (int k = 0; k < 10; k++) part(x, y, 30000, rr(-6000, 6000), rr(-6000, 6000), rr(1000, 6000), k < 6 ? P_RED : P_DRED, 30);
            tType[i] = GIBS;
            tSt[i] = ST_DEAD;
            Snd.sfxAt(Snd.MDIE, x, y);
            sayKill(4);
            return;
        }
        tSt[i] = ST_DIE;
        tTim[i] = 7;
        if (t == SKEL || t == CONQ) {
            Snd.sfxAt(Snd.SKEL, tX[i], tY[i]);
            for (int k = 0; k < 8; k++) part(tX[i], tY[i], 40000, rr(-5000, 5000), rr(-5000, 5000), rr(1000, 6000), P_BONE, 24);
        } else if (t == MUMMY) {
            Snd.sfxAt(Snd.MUMMY, tX[i], tY[i]);
            fx(FX_DUST, tX[i], tY[i], 6000, 12);
        } else if (t == WEEPER) {
            Snd.sfxAt(Snd.WAIL, tX[i], tY[i]);
            fx(FX_SMOKE, tX[i], tY[i], 10000, 14);
        } else if (t == VAMP) {
            Snd.sfxAt(Snd.VAMP, tX[i], tY[i]);
            fx(FX_SMOKE, tX[i], tY[i], 10000, 12);
        } else if (t == FRANK || t == DRONE || t == SPIDER) {
            spark(tX[i], tY[i], t == SPIDER ? 12000 : 30000, 8, P_YEL);
            if (t != SPIDER) { fx(FX_BOOM, tX[i], tY[i], t == DRONE ? tZ[i] : 10000, 8); flashLight(tX[i], tY[i], 10); }
            Snd.sfxAt(t == SPIDER ? Snd.SKITTER : Snd.EXPLODE, tX[i], tY[i]);
        } else Snd.sfxAt(t == BAT ? Snd.BAT : Snd.MDIE, tX[i], tY[i]);
        sayKill(t == WRAITH ? 2 : t == SCARE ? 3 : t == CLOWN ? 5 : t == SKEL ? 6 : t == WOLF ? 7 : t == BAT ? 8 : t == VAMP ? 9
                : t == FRANK || t == CYBORG ? 10 : t == DRONE ? 11 : t == SPIDER ? 12 : t == MUMMY ? 13 : t == JAGUAR ? 14 : t == CONQ ? 15
                : t == WEEPER ? 16 : 0);
    }

    static void sayKill(int kind) {
        if (ticks - lastVoiceTick < 140 || rnd(10) > 4) return;
        lastVoiceTick = ticks;
        switch (kind) {
            case 2: G.voice(Snd.V_GHOST, "Boo yourself.", 0); break;
            case 3: G.voice(Snd.V_PUMPKIN, "Pumpkin pie, anyone?", 0); break;
            case 4: G.voice(Snd.V_GIB, "Who ordered extra crispy?", 0); break;
            case 5: G.voice(Snd.V_KCLOWN, "Joke's over.", 0); break;
            case 6: G.voice(Snd.V_KSKEL, "Back to the boneyard.", 0); break;
            case 7: G.voice(Snd.V_KWOLF, "Bad dog.", 0); break;
            case 8: G.voice(Snd.V_KBAT, "Pest control.", 0); break;
            case 9: G.voice(Snd.V_KVAMP, "Suck on that.", 0); break;
            case 10: G.voice(Snd.V_KROBOT, "Scrap metal.", 0); break;
            case 11: G.voice(Snd.V_KDRONE, "Unplugged.", 0); break;
            case 12: G.voice(Snd.V_KSPIDER, "Squish.", 0); break;
            case 13: G.voice(Snd.V_KMUMMY, "It's a wrap.", 0); break;
            case 14: G.voice(Snd.V_KJAG, "Bad kitty.", 0); break;
            case 15: G.voice(Snd.V_KCONQ, "Conquer this.", 0); break;
            case 16: G.voice(Snd.V_KWEEP, "Cry me a river.", 0); break;
            default: {
                int r = rnd(5);
                if (r == 0) G.voice(Snd.V_KILL1, "Rest in pieces.", 0);
                else if (r == 1) G.voice(Snd.V_KILL2, "Back in the ground, ugly.", 0);
                else if (r == 2) G.voice(Snd.V_KILL3, "Stay dead this time.", 0);
                else if (r == 3) G.voice(Snd.V_KILL4, "Who's next?", 0);
                else G.voice(Snd.V_KILL5, "I'm just getting warmed up.", 0);
            }
        }
    }

    /** src: -2 player's own bomb (half damage to the player), -3 enemy bomb, else monster index */
    static void explode(int x, int y, int z, int dmg, int rad, int src) {
        fx(FX_BOOM, x, y, z - 20000 < 0 ? 0 : z - 20000, 12);
        Snd.sfxAt(Snd.EXPLODE, x, y);
        flashLight(x, y, 14);
        for (int k = 0; k < 8; k++) part(x, y, z, rr(-7000, 7000), rr(-7000, 7000), rr(2000, 8000), k < 4 ? P_YEL : P_ORANGE, 18);
        int dp = E.dist(px - x, py - y);
        if (dp < (6 << 16)) { kick = 12; shake = 14 - (dp >> 15); }
        if (dmg <= 0) return;
        for (int i = 0; i < nt; i++) {
            int t = tType[i];
            if ((tfl[t] & TF_SHOOT) == 0) continue;
            if (src == -3 && isBoss(t)) continue;
            if (t == ROCK) continue;
            int d = E.dist(tX[i] - x, tY[i] - y) - trad[t];
            if (d < 0) d = 0;
            if (d >= rad) continue;
            if (!losCells(x, y, tX[i], tY[i], true)) continue;
            int dd = (int) ((long) dmg * (rad - d) / rad);
            if (t == KEG || t == TOXIC) { if (tHp[i] > 0) tHp[i] -= dd; }
            else damageThing(i, dd, src, 2);
        }
        if (!dead && dp < rad && losCells(x, y, px, py, true)) {
            int dd = (int) ((long) dmg * (rad - dp) / rad);
            if (src == -2) dd = dd / 2;
            damagePlayer(dd, -1);
        }
    }

    // ------------------------------------------------------------------ monsters

    static final int[] vocalT = new int[Snd.NSFX];

    /** A monster's voice, but the same voice at most once every gap ticks (a room full of clowns is one giggle). */
    static void vocal(int s, int i, int gap) {
        if (ticks - vocalT[s] < gap && ticks >= vocalT[s]) return;
        vocalT[s] = ticks;
        Snd.sfxAt(s, tX[i], tY[i]);
    }

    static void sightSound(int t, int i) {
        int s = t == ZOMBIE ? Snd.ZOMBIE : t == SCARE ? Snd.SCARE : t == WRAITH ? Snd.GHOST : t == WITCH ? Snd.WITCH
                : t == SKEL ? Snd.SKEL : t == CLOWN ? Snd.CLOWN : t == WOLF ? Snd.WOLF : t == BAT ? Snd.BAT : t == VAMP ? Snd.VAMP
                : t == GIGGLES ? Snd.GIGGLE : t == COUNT ? Snd.COUNT : t == FRANK || t == DRONE || t == PRIME ? Snd.ROBOT
                : t == CYBORG ? Snd.SAW : t == SPIDER ? Snd.SKITTER : t == MUMMY ? Snd.MUMMY : t == JAGUAR ? Snd.ROAR : t == CONQ ? Snd.CONQ
                : t == WEEPER ? Snd.WAIL : t == SEVEN ? Snd.SEVEN : Snd.BOSS;
        vocal(s, i, s == Snd.WITCH || s == Snd.CLOWN || s == Snd.WAIL || s == Snd.CONQ ? 150 : 45);
        if (isBoss(t) && ticks - lastVoiceTick > 40) {
            lastVoiceTick = ticks;
            if (t == BOSS) G.voice(Snd.V_BOSS, "Your reign is over, gourd boy.", 40);
            else if (t == GIGGLES) G.voice(Snd.V_BOSS2, "Time to pop your balloon, Giggles.", 40);
            else if (t == PRIME) G.voice(Snd.V_BOSS4, "Let's see what you're made of, tin man.", 40);
            else if (t == SEVEN) G.voice(Snd.V_BOSS5, "Seven deaths? I only need one.", 40);
            else G.voice(Snd.V_BOSS3, "Rise and shine, bloodsucker.", 40);
        }
    }

    static void monsterTick(int i) {
        int t = tType[i], st = tSt[i];
        if (t == GIBS) return;
        int hv = M_HOVER[t];
        if (hv != 0) {
            if (st < ST_DIE || t == WRAITH) tZ[i] = hv + (E.sin(ticks * (t == BAT ? 170 : t == DRONE ? 110 : 60) + i * 300) >> (t == BAT ? 3 : 4));
            else if (tZ[i] > 0) { tZ[i] -= 4000; if (tZ[i] < 0) tZ[i] = 0; }
        }
        if (st == ST_DEAD) {
            if (t == MUMMY && tVY[i] == 1 && --tCool[i] <= 0) mummyRise(i);
            return;
        }
        if (st == ST_DIE) {
            if (--tTim[i] <= 0) tSt[i] = ST_DEAD;
            return;
        }
        if (spikeOn && hv == 0 && (ticks & 7) == 0) {           // spike floors hurt monsters too
            int mc = ((tY[i] >> 16) << 6) | (tX[i] >> 16);
            if (flr[mc] == (byte) Res.T_SPIKES && !isBoss(t)) { hitKind = 1; damageThing(i, 7, -1, 1); if (tSt[i] >= ST_DIE) return; }
        }
        boolean boss = isBoss(t);
        int dx = px - tX[i], dy = py - tY[i];
        int d = E.dist(dx, dy);
        if (tCool[i] > 0) tCool[i]--;
        if (((ticks + i) & 3) == 0) tLos[i] = d < (boss ? (30 << 16) : (18 << 16)) && losCells(tX[i], tY[i], px, py, true);
        if (st == ST_IDLE) {
            if (((ticks + i) & 7) != 0) return;
            boolean wake = (tLos[i] && d < (13 << 16)) || (boss && d < (24 << 16));
            if (!wake && noiseX >= 0 && E.dist(noiseX - tX[i], noiseY - tY[i]) < (boss ? (32 << 16) : (9 << 16))) wake = true;
            if (wake) {
                tSt[i] = ST_CHASE;
                tCool[i] = 10 + rnd(20);
                sightSound(t, i);
            }
            return;
        }
        if (boss) { bossIdx = i; bossType = t; }
        if (dead) {
            if (st != ST_CHASE) tSt[i] = ST_CHASE;
            tAnim[i]++;
            return;
        }
        if (st == ST_PAIN) {
            if (--tTim[i] <= 0) tSt[i] = ST_CHASE;
            return;
        }
        if (st == ST_ATK) {
            tTim[i]--;
            if (tTim[i] == tAux[i]) doAttack(i, d);
            if (tTim[i] <= 0) { tSt[i] = ST_CHASE; }
            return;
        }
        // chase
        tAnim[i]++;
        if (boss && bossSpecial(i, d)) return;
        int melee = boss ? 100000 : t == BAT || t == SPIDER ? 46000 : 58000;
        if (M_MELEE[t] > 0 && d < melee && tCool[i] == 0 && tLos[i]) {
            tSt[i] = ST_ATK;
            tTim[i] = t == BAT || t == SPIDER ? 6 : 9;
            tAux[i] = t == BAT || t == SPIDER ? 3 : 4;
            tCool[i] = cool(t == ZOMBIE ? 22 : boss ? 20 : t == BAT || t == SPIDER ? 14 : t == WOLF || t == CYBORG ? 18 : 24);
            if (t == CYBORG) Snd.sfxAt(Snd.SAW, tX[i], tY[i]);
            tVZ[i] = 0;     // melee
            return;
        }
        int rng = boss ? (24 << 16) : (15 << 16);
        if (M_PROJ[t] != 0 && tCool[i] == 0 && tLos[i] && d < rng && d > 70000 && rnd(M_RCH[t]) == 0) {
            tSt[i] = ST_ATK;
            tTim[i] = boss ? 14 : 11;
            tAux[i] = 5;
            int c = boss ? 22 + rnd(16) : 30 + rnd(30);
            if (boss && tHp[i] * 10 < bossMax * 4) c = c * 4 / 5;      // enraged below 40%
            tCool[i] = cool(c);
            tVZ[i] = 1;     // ranged
            if (t == GIGGLES) tVY[i] = rnd(4) == 0 ? 1 : 0;          // 1 = lob juggling bombs, 0 = knife fan
            if (t == DRONE) { tTim[i] = 9; tAux[i] = 5; }
            if (t == SEVEN) tCool[i] = cool(36 + rnd(24) - (tHp[i] * 10 < bossMax * 4 ? 10 : 0));     // the discs take a while to gather
            if (t == CONQ) {                 // the arquebus: a long aim (dodge it!), a heavy ball, a long reload
                tTim[i] = 26; tAux[i] = 8;
                tCool[i] = cool(75 + rnd(45));
                Snd.sfxAt(Snd.CLICK, tX[i], tY[i]);
            }
            return;
        }
        if (t == WRAITH && tLos[i] && d < (5 << 16) && rnd(40) == 0) vocal(Snd.GHOST, i, 60);
        if (t == BAT && tLos[i] && d < (6 << 16) && rnd(50) == 0) vocal(Snd.BAT, i, 30);
        if (t == CYBORG && tLos[i] && d < (5 << 16) && rnd(45) == 0) vocal(Snd.SAW, i, 30);
        if (t == MUMMY && d < (6 << 16) && rnd(70) == 0) vocal(Snd.MUMMY, i, 70);
        if (t == WEEPER) {                // la llorona: out of sight, she drifts closer... and appears beside you
            if (tVX[i] > 0) tVX[i]--;
            else if (d > (5 << 16) && d < (16 << 16)) {
                tVX[i] = (skill == 0 ? 260 : skill == 1 ? 180 : 130) + rnd(120);
                if (creep(i)) return;
            }
            if (tLos[i] && d < (6 << 16) && rnd(60) == 0) vocal(Snd.WAIL, i, 90);
        }
        // movement
        int spd = M_SPD[t];
        if (t == WOLF || t == SPIDER || t == JAGUAR) {      // werewolves, skull-spiders and jaguar warriors lunge when they get close
            if (tVX[i] > 0) { if (--tVX[i] == 0) tVX[i] = -50; spd = spd * 2; }
            else if (tVX[i] < 0) tVX[i]++;
            else if (tLos[i] && d < (7 << 16) && d > (2 << 16) && rnd(20) == 0) {
                tVX[i] = 16;
                if (t == JAGUAR) vocal(Snd.ROAR, i, 30);
                else Snd.sfxAt(t == WOLF ? Snd.WOLF : Snd.SKITTER, tX[i], tY[i]);
            }
        }
        int tx, ty;
        if (t == DRONE && tLos[i] && d < (4 << 16)) { tx = tX[i] * 2 - px; ty = tY[i] * 2 - py; }    // drones keep their distance
        else if (tLos[i] && d < (9 << 16)) { tx = px; ty = py; }
        else {
            int c = ((tY[i] >> 16) << 6) | (tX[i] >> 16);
            int best = flow[c], bc = -1;
            for (int k = 0; k < 8; k++) {
                int ox = k == 0 ? -1 : k == 1 ? 1 : k == 2 ? 0 : k == 3 ? 0 : k == 4 ? -1 : k == 5 ? 1 : k == 6 ? -1 : 1;
                int oy = k == 0 ? 0 : k == 1 ? 0 : k == 2 ? -1 : k == 3 ? 1 : k == 4 ? -1 : k == 5 ? -1 : k == 6 ? 1 : 1;
                int n = c + oy * 64 + ox;
                if (n < 0 || n >= 4096) continue;
                if (k >= 4 && (wall[c + ox] != 0 || wall[c + oy * 64] != 0)) continue;
                if (flow[n] < best) { best = flow[n]; bc = n; }
            }
            if (bc < 0) { tx = px; ty = py; }
            else {
                tx = ((bc & 63) << 16) + 32768;
                ty = ((bc >> 6) << 16) + 32768;
                if (wall[bc] != 0 && (flag[bc] & F_DOOR) != 0 && dstate[bc] == 0) openDoor(bc, false);
            }
        }
        int mdx = tx - tX[i], mdy = ty - tY[i];
        int md = E.dist(mdx, mdy);
        if (md < 2000) return;
        int vx = (int) ((long) mdx * spd / md), vy = (int) ((long) mdy * spd / md);
        if (t == BAT || t == DRONE) {              // erratic fluttering, drones circle-strafe
            int w = t == BAT ? E.sin(ticks * 220 + i * 777) >> 1 : ((i & 1) == 0 ? 40000 : -40000);
            vx += (int) ((long) -mdy * w / md) * spd >> 16;
            vy += (int) ((long) mdx * w / md) * spd >> 16;
        }
        int r = boss ? 24000 : trad[t];
        int nx = tX[i] + vx, ny = tY[i] + vy;
        int pr = 16000 + r;
        boolean nearP = !dead && (long) (nx - px) * (nx - px) + (long) (ny - py) * (ny - py) < (long) pr * pr;
        if (!nearP) {
            boolean moved = false, walker = hv == 0;
            if (!blocked(nx, tY[i], r) && thingAt(nx, tY[i], r, i) < 0 && !(walker && pitAt(nx, tY[i]))) { tX[i] = nx; moved = true; }
            if (!blocked(tX[i], ny, r) && thingAt(tX[i], ny, r, i) < 0 && !(walker && pitAt(tX[i], ny))) { tY[i] = ny; moved = true; }
            if (!moved) {
                // jitter sideways to get unstuck
                int jx = tX[i] + (rnd(2) == 0 ? spd : -spd), jy = tY[i] + (rnd(2) == 0 ? spd : -spd);
                if (!blocked(jx, jy, r) && thingAt(jx, jy, r, i) < 0 && !(walker && pitAt(jx, jy))) { tX[i] = jx; tY[i] = jy; }
            }
        }
    }

    /** Boss-only behaviour each chase tick: summons, the Count's teleports. True if it consumed the tick. */
    static boolean bossSpecial(int i, int d) {
        int t = tType[i];
        if ((ticks % SK_SUMMON[skill]) == 0) summon(i);
        if (t == PRIME) {
            if (tVX[i] > 0) tVX[i]--;
            if (tVX[i] == 0 && tLos[i] && d < (7 << 16) && swR < 0) {
                tSt[i] = ST_ATK; tTim[i] = 16; tAux[i] = 6; tVZ[i] = 2;
                tVX[i] = (skill == 0 ? 210 : skill == 1 ? 150 : 115) + rnd(60);
                if (tHp[i] * 10 < bossMax * 4) tVX[i] = tVX[i] * 3 / 4;
                Snd.sfxAt(Snd.ROBOT, tX[i], tY[i]);
                return true;
            }
        }
        if (t == SEVEN) {                    // the club slams the floor and the roof of Xibalba comes down
            if (tVY[i] > 0) tVY[i]--;
            else if (tLos[i] && d < (14 << 16) && d > (2 << 16)) {
                tSt[i] = ST_ATK; tTim[i] = 18; tAux[i] = 6; tVZ[i] = 4;
                tVY[i] = (skill == 0 ? 280 : skill == 1 ? 200 : 160) + rnd(60);
                if (tHp[i] * 10 < bossMax * 4) tVY[i] = tVY[i] * 3 / 4;
                vocal(Snd.SEVEN, i, 140);
                return true;
            }
        }
        if (t == COUNT) {
            if (tVX[i] > 0) tVX[i]--;
            if (tVX[i] == 1 || (tVX[i] == 0 && tLos[i] && d < (4 << 16))) {
                tVX[i] = (skill == 0 ? 260 : skill == 1 ? 190 : 140) + rnd(80);
                if (blink(i, 0)) return true;
            }
        }
        return false;
    }

    /** The weeping woman: gone in a puff, and back a few steps from Butch - somewhere he isn't looking. */
    static boolean creep(int i) {
        for (int tries = 0; tries < 16; tries++) {
            int a = rnd(4096);
            int rel = (a - pa) & 4095;
            if (rel > 2048) rel -= 4096;
            if (rel > -700 && rel < 700) continue;
            int dd = rr(3 << 16, 5 << 16);
            int x = px + (int) ((long) E.cos(a) * dd >> 16), y = py + (int) ((long) E.sin(a) * dd >> 16);
            int cx = x >> 16, cy = y >> 16;
            if (cx < 1 || cy < 1 || cx > mapW - 2 || cy > mapH - 2) continue;
            int c = (cy << 6) | cx;
            if (wall[c] != 0 || flow[c] > 40 || flr[c] == (byte) Res.T_PIT) continue;
            if (blocked(x, y, trad[WEEPER]) || thingAt(x, y, trad[WEEPER], i) >= 0 || !losCells(x, y, px, py, true)) continue;
            fx(FX_SMOKE, tX[i], tY[i], 10000, 10);
            tX[i] = x; tY[i] = y;
            fx(FX_SMOKE, x, y, 10000, 10);
            vocal(Snd.WAIL, i, 60);
            tSt[i] = ST_CHASE;
            tCool[i] = 18;
            return true;
        }
        return false;
    }

    /** Vanish in a puff of smoke and reappear elsewhere. far = 0: boss jump across the arena, else a short hop of about far cells. */
    static boolean blink(int i, int far) {
        for (int tries = 0; tries < 24; tries++) {
            int x, y;
            if (far == 0) { x = rr(1, mapW - 2); y = rr(1, mapH - 2); }
            else {
                int a = rnd(4096);
                x = (tX[i] + E.cos(a) * far) >> 16; y = (tY[i] + E.sin(a) * far) >> 16;
                if (x < 1 || y < 1 || x > mapW - 2 || y > mapH - 2) continue;
            }
            int c = (y << 6) | x;
            if (wall[c] != 0 || (flag[c] & F_HURT) != 0 || flow[c] > 60 || flr[c] == (byte) Res.T_PIT) continue;
            int nx = (x << 16) + 32768, ny = (y << 16) + 32768;
            int r = trad[tType[i]];
            if (blocked(nx, ny, r) || thingAt(nx, ny, r, i) >= 0) continue;
            int dp = E.dist(nx - px, ny - py);
            if (far == 0 && (dp < (5 << 16) || dp > (13 << 16))) continue;
            if (far != 0 && dp < (2 << 16)) continue;
            fx(FX_SMOKE, tX[i], tY[i], 8000, 12);
            tX[i] = nx; tY[i] = ny;
            fx(FX_SMOKE, nx, ny, 8000, 12);
            Snd.sfxAt(Snd.TELE, nx, ny);
            tSt[i] = ST_CHASE;
            tCool[i] = 12;
            return true;
        }
        return false;
    }

    static void doAttack(int i, int d) {
        int t = tType[i];
        if (tVZ[i] == 2) {                      // Frankenstein Prime's stomp: a ring of lightning you have to jump over
            swX = tX[i]; swY = tY[i]; swR = 30000; swHit = false;
            shake = 16;
            Snd.sfx(Snd.STOMP);
            flashLight(tX[i], tY[i], 14);
            if (!stompTold) { stompTold = true; G.msg("JUMP (#) over the shockwaves!", 0x80e0ff); }
            return;
        }
        if (tVZ[i] == 4) {                      // Seven Death's slam: rocks rain down where the dust trickles
            slam(i);
            return;
        }
        if (tVZ[i] == 0) {
            int reach = isBoss(t) ? 120000 : t == BAT ? 56000 : 72000;
            if (t == WEEPER) vocal(Snd.WAIL, i, 40);
            if (d < reach && tLos[i]) {
                int dm = M_MELEE[t];
                damagePlayer(rr(dm * 3 / 4, dm * 5 / 4), i);
                if (t == ZOMBIE || t == WOLF || t == FRANK || t == MUMMY || t == JAGUAR || isBoss(t)) Snd.sfx(Snd.HIT);
                if (t == SEVEN) {               // the obsidian club knocks Butch flying
                    int a = E.atan2(py - tY[i], px - tX[i]);
                    int qx = px + (E.cos(a) >> 1), qy = py + (E.sin(a) >> 1);
                    if (!blocked(qx, qy, 16000) && !pitAt(qx, qy)) { px = qx; py = qy; }
                    shake = 8;
                }
                if (t == CYBORG) blood(px + (E.cos(pa) >> 2), py + (E.sin(pa) >> 2), 30000, 4);
            }
            return;
        }
        int a = E.atan2(py - tY[i], px - tX[i]);
        int sp = SK_PSPD[skill];
        switch (t) {
            case BOSS:
                for (int k = -1; k <= 1; k++) shootBall(i, BOSSBALL, (a + k * 120) & 4095, 15 * sp / 100, 42000);
                Snd.sfxAt(Snd.FIREBALL, tX[i], tY[i]);
                break;
            case GIGGLES:
                if (tVY[i] == 1) {
                    for (int k = 0; k < 2; k++) lob(i, (a + (k == 0 ? -70 : 70)) & 4095, d + rr(-30000, 30000));
                } else {
                    int n = skill == 0 ? 3 : 5;
                    for (int k = 0; k < n; k++) shootBall(i, KNIFE, (a + (k - n / 2) * 150) & 4095, 19 * sp / 100, 62000);
                }
                Snd.sfxAt(Snd.KNIFE, tX[i], tY[i]);
                if (rnd(3) == 0) vocal(Snd.GIGGLE, i, 120);
                break;
            case COUNT:
                for (int k = -1; k <= 1; k++) shootBall(i, BOLT, (a + k * 150) & 4095, 17 * sp / 100, 50000);
                Snd.sfxAt(Snd.FIREBALL, tX[i], tY[i]);
                break;
            case PRIME: {
                int n = skill == 0 ? 3 : 5;
                for (int k = 0; k < n; k++) shootBall(i, ZAP, (a + (k - n / 2) * 140) & 4095, 15 * sp / 100, 70000);
                Snd.sfxAt(Snd.ZAPS, tX[i], tY[i]);
                break;
            }
            case FRANK: {
                int k = shootBall(i, ZAP, a, 10 * sp / 100, 40000);
                if (k >= 0) { tAux[k] = 1; tTim[k] = 110; }       // slow, homing
                Snd.sfxAt(Snd.ZAPS, tX[i], tY[i]);
                break;
            }
            case DRONE:
                shootBall(i, LASER, (a + rr(-40, 40)) & 4095, 26 * sp / 100, tZ[i] + 8000);
                Snd.sfxAt(Snd.LASER, tX[i], tY[i]);
                break;
            case WITCH:
                shootBall(i, GREENBALL, a, 17 * sp / 100, 34000);
                Snd.sfxAt(Snd.FIREBALL, tX[i], tY[i]);
                break;
            case CLOWN:
                shootBall(i, KNIFE, a, 20 * sp / 100, 34000);
                Snd.sfxAt(Snd.KNIFE, tX[i], tY[i]);
                break;
            case VAMP:
                shootBall(i, BOLT, a, 15 * sp / 100, 38000);
                Snd.sfxAt(Snd.VAMP, tX[i], tY[i]);
                break;
            case CONQ: {
                int k = shootBall(i, SHOT, (a + rr(-25, 25)) & 4095, 34 * sp / 100, 40000);
                if (k >= 0) fx(FX_SMOKE, tX[i] + (E.cos(a) >> 1), tY[i] + (E.sin(a) >> 1), 34000, 10);
                Snd.sfxAt(Snd.MUSKET, tX[i], tY[i]);
                flashLight(tX[i], tY[i], 8);
                break;
            }
            case SEVEN: {                       // a fan of spinning jade discs
                int n = 3;
                if (tHp[i] * 10 < bossMax * 4) n += 2;
                for (int k = 0; k < n; k++) shootBall(i, DISC, (a + (k - n / 2) * 150) & 4095, 15 * sp / 100, 56000);
                Snd.sfxAt(Snd.KNIFE, tX[i], tY[i]);
                break;
            }
            default:
                shootBall(i, FIREBALL, a, 13 * sp / 100, 38000);
                Snd.sfxAt(Snd.FIREBALL, tX[i], tY[i]);
        }
    }

    static int shootBall(int src, int type, int a, int speed64, int z) {
        int i = spawn(type, tX[src] + (E.cos(a) >> 2), tY[src] + (E.sin(a) >> 2));
        if (i < 0) return -1;
        tVX[i] = E.cos(a) * speed64 >> 6;
        tVY[i] = E.sin(a) * speed64 >> 6;
        tZ[i] = z;
        tOwn[i] = src;
        return i;
    }

    /** Lob a juggling bomb in an arc that lands about dist away. */
    static void lob(int src, int a, int dist) {
        int i = spawn(JBALL, tX[src] + (E.cos(a) >> 2), tY[src] + (E.sin(a) >> 2));
        if (i < 0) return;
        if (dist < 65536) dist = 65536;
        int sp = dist / 36;
        tVX[i] = (int) ((long) E.cos(a) * sp >> 16);
        tVY[i] = (int) ((long) E.sin(a) * sp >> 16);
        tZ[i] = 70000;
        tVZ[i] = 3600;
        tOwn[i] = src;
    }

    /** Seven Death's slam: dust trickles from the roof where each rock is about to fall (one right above Butch). */
    static void slam(int src) {
        shake = 14;
        Snd.sfx(Snd.STOMP);
        flashLight(tX[src], tY[src], 10);
        int n = skill == 0 ? 4 : skill == 1 ? 5 : 6;
        if (tHp[src] * 10 < bossMax * 4) n += 2;
        for (int k = 0; k < n; k++) {
            int x = px, y = py;
            if (k > 0) {
                int a = rnd(4096), dd = rr(30000, 4 << 16);
                x += (int) ((long) E.cos(a) * dd >> 16);
                y += (int) ((long) E.sin(a) * dd >> 16);
                if (blocked(x, y, 9000)) continue;
            }
            int i = spawn(ROCK, x, y);
            if (i < 0) continue;
            tZ[i] = 120000; tVZ[i] = -1800; tAux[i] = 12 + k * 3; tOwn[i] = src;
            fx(FX_DUST, x, y, 2000, tAux[i] + 6);
            for (int p = 0; p < 3; p++) part(x + rr(-8000, 8000), y + rr(-8000, 8000), 62000, 0, 0, -rr(0, 1500), P_GREY, 22);
        }
        if ((tips & 32) == 0) { tips |= 32; G.tip("Falling rocks! Move away from the dust"); }
    }

    static void summon(int boss) {
        int alive = 0;
        for (int i = 0; i < nt; i++) if (isMon(tType[i]) && tSt[i] < ST_DIE) alive++;
        if (alive > SK_SUMMAX[skill]) return;
        int bt = tType[boss];
        int n = skill + 1 + (bt == COUNT ? 1 : 0);
        for (int k = 0; k < n; k++) {
            int a = rnd(4096);
            int x = tX[boss] + (E.cos(a) * 2), y = tY[boss] + (E.sin(a) * 2);
            if (blocked(x, y, 20000)) continue;
            if (pitAt(x, y)) continue;
            int mt = bt == BOSS ? (k % 2 == 0 ? WRAITH : ZOMBIE) : bt == GIGGLES ? (k % 2 == 0 ? CLOWN : SKEL)
                    : bt == PRIME ? (k % 2 == 0 ? SPIDER : DRONE) : bt == SEVEN ? (k % 2 == 0 ? MUMMY : JAGUAR) : (k == 2 && skill > 0 ? WOLF : BAT);
            int i = spawn(mt, x, y);
            if (i >= 0) {
                tSt[i] = ST_CHASE;
                totalKills++;
                fx(bt == COUNT || bt == PRIME ? FX_SMOKE : bt == SEVEN ? FX_DUST : FX_GREEN, x, y, 20000, 10);
            }
        }
        Snd.sfxAt(bt == GIGGLES ? Snd.GIGGLE : bt == COUNT ? Snd.COUNT : bt == PRIME ? Snd.TELE : bt == SEVEN ? Snd.SEVEN : Snd.BOSS, tX[boss], tY[boss]);
    }

    // ------------------------------------------------------------------ projectiles

    static boolean projTick(int i) {
        int t = tType[i];
        if (t == ROCK) return rockTick(i);
        int nx = tX[i] + tVX[i], ny = tY[i] + tVY[i];
        tAnim[i]++;
        boolean hitWall = blocked(nx, ny, 4000);
        if (t == PBOMB) {
            for (int k = 0; k < nt; k++) {
                int tt = tType[k];
                if ((tfl[tt] & TF_SHOOT) == 0 || (isMon(tt) && tSt[k] >= ST_DIE)) continue;
                int r = trad[tt] + 9000;
                int dx = tX[k] - nx, dy = tY[k] - ny;
                if (dx < r && dx > -r && dy < r && dy > -r) { hitWall = true; break; }
            }
            if ((tAnim[i] & 1) == 0) part(tX[i], tY[i], tZ[i], 0, 0, 800, P_ORANGE, 8);
            if (hitWall) {
                remove(i);
                explode(nx - tVX[i], ny - tVY[i], 24000, 140, 2 << 16, -2);
                return true;
            }
        } else if (t == JBALL) {
            if ((tAnim[i] & 1) == 0) part(tX[i], tY[i], tZ[i] + 8000, 0, 0, 600, P_YEL, 6);
            int dx = px - nx, dy = py - ny;
            boolean nearP = !dead && dx < 22000 && dx > -22000 && dy < 22000 && dy > -22000 && tZ[i] < 50000;
            if (hitWall) { tVX[i] = -tVX[i] / 2; tVY[i] = -tVY[i] / 2; nx = tX[i]; ny = tY[i]; }
            if (tZ[i] <= 4000 || nearP) {
                remove(i);
                explode(nx, ny, 20000, 28, 80000, -3);
                return true;
            }
        } else {
            if (t == ZAP && tAux[i] == 1) {        // the Franken-bot's ball lightning drifts toward you, then fizzles out
                if (--tTim[i] <= 0) { fx(FX_ZAP, tX[i], tY[i], tZ[i] - 8000, 6); remove(i); return true; }
                int ex = px - tX[i], ey = py - tY[i], ed = E.dist(ex, ey);
                if (ed > 0) {
                    int sp = E.dist(tVX[i], tVY[i]);
                    tVX[i] += ((int) ((long) ex * sp / ed) - tVX[i]) >> 4;
                    tVY[i] += ((int) ((long) ey * sp / ed) - tVY[i]) >> 4;
                }
                if ((tAnim[i] & 3) == 0) part(tX[i], tY[i], tZ[i], 0, 0, 800, P_CYAN, 6);
            }
            int dx = px - nx, dy = py - ny;
            int r = trad[t] + 14000;
            if (!dead && dx < r && dx > -r && dy < r && dy > -r) {
                damagePlayer(t == BOSSBALL ? rr(11, 18) : t == GREENBALL ? rr(12, 20) : t == KNIFE ? rr(7, 12) : t == BOLT ? rr(9, 16)
                        : t == ZAP ? (tAux[i] == 1 ? rr(10, 16) : rr(9, 14)) : t == LASER ? rr(5, 9) : t == DART ? rr(6, 10)
                        : t == SHOT ? rr(14, 21) : t == DISC ? rr(9, 14) : rr(10, 18), tOwn[i]);
                if (t == BOLT || t == DART || t == SHOT) blood(px, py, 30000, 3);
                hitWall = true;
            }
            if (hitWall) {
                fx(t == GREENBALL || t == DISC ? FX_GREEN : t == KNIFE || t == DART || t == SHOT ? FX_PUFF : t == ZAP ? FX_ZAP : FX_SPARK,
                        tX[i], tY[i], tZ[i] - 8000, 6);
                spark(tX[i], tY[i], tZ[i], 4, t == GREENBALL || t == DISC ? P_GREEN : t == KNIFE || t == SHOT ? P_YEL : t == BOLT || t == LASER ? P_RED
                        : t == ZAP ? P_CYAN : t == DART ? P_BONE : P_ORANGE);
                if (t == KNIFE || t == DART) Snd.sfxAt(Snd.CLICK, tX[i], tY[i]);
                remove(i);
                return true;
            }
        }
        tX[i] = nx;
        tY[i] = ny;
        if (t == PBOMB) { tZ[i] += tVZ[i]; tVZ[i] -= 30; if (tZ[i] < 4000) tZ[i] = 4000; }
        if (t == JBALL) { tZ[i] += tVZ[i]; tVZ[i] -= 290; }
        return false;
    }

    /** A falling rock: waits (dust trickling) up in the dark, then drops. */
    static boolean rockTick(int i) {
        if (tAux[i] > 0) { tAux[i]--; return false; }
        tAnim[i]++;
        tZ[i] += tVZ[i];
        tVZ[i] -= 650;
        if (tZ[i] > 5000) return false;
        int x = tX[i], y = tY[i];
        remove(i);
        Snd.sfxAt(Snd.BONK, x, y);
        fx(FX_DUST, x, y, 0, 12);
        for (int k = 0; k < 8; k++) part(x, y, 6000, rr(-5000, 5000), rr(-5000, 5000), rr(1500, 6000), P_GREY, 18);
        int dp = E.dist(px - x, py - y);
        if (dp < (3 << 16) && shake < 6) shake = 6;
        if (!dead && dp < 36000 && pz < 30000) { damagePlayer(rr(12, 18), -1); kick = 10; }
        for (int k = 0; k < nt; k++) {           // ...and on whatever else stands there
            int tk = tType[k];
            if (!isMon(tk) || isBoss(tk) || tSt[k] >= ST_DIE) continue;
            if (E.dist(tX[k] - x, tY[k] - y) < 30000 + trad[tk]) damageThing(k, 45, -1, 2);
        }
        return true;
    }

    // ------------------------------------------------------------------ pickups

    static boolean pickTick(int i) {
        if (tSt[i] > 0) {                       // waiting to respawn (boss arenas)
            if (--tSt[i] == 0) { fx(FX_GREEN, tX[i], tY[i], 6000, 10); Snd.sfxAt(Snd.SECRET, tX[i], tY[i]); }
            return false;
        }
        int dx = tX[i] - px, dy = tY[i] - py;
        if (dx > 34000 || dx < -34000 || dy > 34000 || dy < -34000) return false;
        int t = tType[i];
        String m = null;
        int col = 0xffe080;
        switch (t) {
            case CANDY:
                if (health >= 100) return false;
                health += 10; if (health > 100) health = 100; m = "Candy corn +10"; break;
            case BUCKET:
                if (health >= 100) return false;
                health += 30; if (health > 100) health = 100; m = "Bucket of candy +30";
                G.voice(Snd.V_HEALTH, "Sweet, sweet candy.", 120); break;
            case BREW:
                health += 100; if (health > 200) health = 200; m = "WITCH'S BREW! +100"; col = 0xff80ff;
                G.voice(Snd.V_HEALTH, "Sweet, sweet candy.", 0); break;
            case ARMOR:
                if (armor >= 100) return false;
                armor = 100; m = "Bone armor vest"; break;
            case BULLETS:
                if (ammo[0] >= AMAX[0]) return false;
                ammo[0] += 24 * SK_AMMO[skill] / 100; if (ammo[0] > AMAX[0]) ammo[0] = AMAX[0]; m = "Silver bullets"; break;
            case SHELLS:
                if (ammo[1] >= AMAX[1]) return false;
                ammo[1] += 8 * SK_AMMO[skill] / 100; if (ammo[1] > AMAX[1]) ammo[1] = AMAX[1]; m = "Shotgun shells"; break;
            case PUMPKINS:
                if (ammo[2] >= AMAX[2]) return false;
                ammo[2] += 4 * SK_AMMO[skill] / 100; if (ammo[2] > AMAX[2]) ammo[2] = AMAX[2]; m = "Pumpkin bombs"; break;
            case SHOTGUN: case TOMMY: case LAUNCHER: {
                int w = t == SHOTGUN ? WSHOT : t == TOMMY ? WTOMMY : WLAUNCH;
                boolean had = (weapons & (1 << w)) != 0;
                int a = WAMMO[w];
                if (had && ammo[a] >= AMAX[a]) return false;
                weapons |= 1 << w;
                ammo[a] += t == SHOTGUN ? 10 : t == TOMMY ? 50 : 6;
                if (ammo[a] > AMAX[a]) ammo[a] = AMAX[a];
                m = "You got the " + WNAME[w] + "!";
                if (!had) {
                    selectWeapon(w);
                    if (t == LAUNCHER) G.voice(Snd.V_LAUNCHER, "Now that's a jack-o-lantern.", 0);
                    else G.voice(Snd.V_WEAPON, "Come to papa.", 0);
                }
                Snd.sfx(Snd.WPICK);
                G.face(3, 30);
                break;
            }
            case KEYR: keys |= 1; m = "RED skull key"; col = 0xff4030; break;
            case KEYB: keys |= 2; m = "BLUE skull key"; col = 0x60a0ff; break;
            case KEYG: keys |= 4; m = "GOLD skull key"; col = 0xffd020; break;
            case IDOL: keys |= 4; m = "The GOLDEN IDOL! It opens the gold seal"; col = 0xffd020; break;
            default: return false;
        }
        boolean trig = t == IDOL || (t == KEYR && (lvFlags & LF_OTHER) != 0);
        if (t >= KEYR) Snd.sfx(Snd.KEY);
        else if (t != SHOTGUN && t != TOMMY && t != LAUNCHER) Snd.sfx(Snd.PICKUP);
        flashPick = 90;
        G.msg(m, col);
        if ((lvFlags & LF_RESPAWN) != 0 && t < KEYR) { tSt[i] = SK_RESPAWN[skill]; return false; }
        remove(i);
        if (trig) trigger();
        return true;
    }

    // ------------------------------------------------------------------ particles & lights

    static void part(int x, int y, int z, int vx, int vy, int vz, int c, int life) {
        if (np >= MAXP) return;
        int i = np++;
        pX[i] = x; pY[i] = y; pZ[i] = z; pVX[i] = vx; pVY[i] = vy; pVZ[i] = vz; pC[i] = c; pL[i] = life;
    }

    static void blood(int x, int y, int z, int n) {
        for (int k = 0; k < n; k++) part(x, y, z, rr(-4000, 4000), rr(-4000, 4000), rr(0, 5000), k % 3 == 0 ? P_DRED : P_RED, 20);
        fx(FX_BLOOD, x, y, z - 10000, 5);
    }

    static void spark(int x, int y, int z, int n, int c) {
        for (int k = 0; k < n; k++) part(x, y, z, rr(-3000, 3000), rr(-3000, 3000), rr(1000, 5000), c, 10);
    }

    static void particlesTick() {
        for (int i = 0; i < np; i++) {
            if (--pL[i] <= 0) {
                int j = --np;
                pX[i] = pX[j]; pY[i] = pY[j]; pZ[i] = pZ[j]; pVX[i] = pVX[j]; pVY[i] = pVY[j]; pVZ[i] = pVZ[j]; pC[i] = pC[j]; pL[i] = pL[j];
                i--;
                continue;
            }
            pX[i] += pVX[i];
            pY[i] += pVY[i];
            pZ[i] += pVZ[i];
            pVZ[i] -= 700;
            if (pZ[i] < 0) { pZ[i] = 0; pVZ[i] = 0; pVX[i] >>= 1; pVY[i] >>= 1; }
        }
    }

    static final int MAXFL = 8;
    static final int[] flX = new int[MAXFL], flY = new int[MAXFL], flS = new int[MAXFL];
    static int nfl;
    static int flickVal;

    static void flashLight(int x, int y, int s) {
        if (nfl >= MAXFL) return;
        flX[nfl] = x; flY[nfl] = y; flS[nfl] = s; nfl++;
    }

    static void lightsTick() {
        if ((ticks & 1) == 0) flickVal = rnd(4);
        // lightning on outdoor levels
        if (lightning != 0) {
            if (--lightningT <= 0) {
                lightningT = 240 + rnd(360);
                lightningBoost = 14;
                thunderT = 6 + rnd(20);
            }
            if (lightningBoost > 0) lightningBoost -= (lightningBoost > 8 ? 1 : 2);
            if (lightningBoost < 0) lightningBoost = 0;
            if (thunderT > 0 && --thunderT == 0) Snd.sfx(Snd.THUNDER);
        }
        int lb = lightningBoost;
        for (int c = 0; c < 4096; c++) {
            int l = baseLight[c];
            if (flick[c] != 0) l += flickVal;
            if (lb > 0 && (flag[c] & F_OUT) != 0) l -= lb;
            light[c] = l < 0 ? 0 : l;
        }
        for (int k = 0; k < nfl; k++) {
            int cx = flX[k] >> 16, cy = flY[k] >> 16, s = flS[k];
            for (int y = cy - 2; y <= cy + 2; y++)
                for (int x = cx - 2; x <= cx + 2; x++) {
                    if (x < 0 || y < 0 || x > 63 || y > 63) continue;
                    int dd = (x - cx) * (x - cx) + (y - cy) * (y - cy);
                    int dec = s - dd * s / 6;
                    if (dec <= 0) continue;
                    int c = (y << 6) | x;
                    int l = light[c] - dec;
                    light[c] = l < 0 ? 0 : l;
                }
            flS[k] -= 4;
        }
        int w = 0;
        for (int k = 0; k < nfl; k++) if (flS[k] > 0) { flX[w] = flX[k]; flY[w] = flY[k]; flS[w] = flS[k]; w++; }
        nfl = w;
    }

    // ================================================================== sprite collection for the renderer

    static void collectSprites() {
        for (int i = 0; i < nt; i++) {
            int t = tType[i], fl = tfl[t], s = tspr[t];
            if ((fl & TF_PICK) != 0 && tSt[i] > 0) continue;        // collected, waiting to respawn
            if (t == ACTOR) s = tAux[i];
            if (t == BOULDER) {
                if (tSt[i] == 0) continue;                          // still hidden in the roof
                s = tSt[i] == 1 && tTim[i] >= 0 && ((tAnim[i] >> 2) & 1) != 0 ? Res.S_BOULDER_2 : Res.S_BOULDER_1;
            }
            int c = ((tY[i] >> 16) << 6) | (tX[i] >> 16);
            int lt = c >= 0 && c < 4096 ? light[c] : 16;
            int vf = 0;
            if ((fl & TF_TRANS) != 0) vf |= E.VF_TRANS;
            if ((fl & TF_BRIGHT) != 0) vf |= E.VF_BRIGHT;
            int z = tZ[i];
            if ((fl & TF_MON) != 0) {
                int[] fr = M_SPR[t];
                int st = tSt[i];
                if (st == ST_DEAD) s = fr[5];
                else if (st == ST_DIE) s = fr[4];
                else if (st == ST_PAIN) s = fr[3];
                else if (st == ST_ATK) s = fr[2];
                else if (st == ST_CHASE) s = fr[(tAnim[i] / 7) & 1];
                else s = fr[0];
                if (t == WRAITH && st >= ST_DIE) vf |= E.VF_TRANS;
            } else if (t == GIBS) s = Res.S_GIBS;
            else if ((fl & TF_PROJ) != 0) {
                if (t == FIREBALL) s = (tAnim[i] & 2) == 0 ? Res.S_FIREBALL1 : Res.S_FIREBALL2;
                else if (t == BOSSBALL) { s = (tAnim[i] & 2) == 0 ? Res.S_FX_BOOM1 : Res.S_FX_BOOM2; z -= 6000; }
                else if (t == GREENBALL) s = (tAnim[i] & 2) == 0 ? Res.S_GREENBALL1 : Res.S_GREENBALL2;
                else if (t == KNIFE) s = (tAnim[i] & 1) == 0 ? Res.S_KNIFE1 : Res.S_KNIFE2;
                else if (t == BOLT) s = (tAnim[i] & 2) == 0 ? Res.S_BOLT1 : Res.S_BOLT2;
                else if (t == ZAP) s = (tAnim[i] & 1) == 0 ? Res.S_ZAP1 : Res.S_ZAP2;
                else if (t == LASER) s = (tAnim[i] & 2) == 0 ? Res.S_LASER1 : Res.S_LASER2;
                else if (t == DART) s = (tAnim[i] & 1) == 0 ? Res.S_DART1 : Res.S_DART2;
                else if (t == SHOT) s = (tAnim[i] & 1) == 0 ? Res.S_SHOT1 : Res.S_SHOT2;
                else if (t == DISC) s = (tAnim[i] & 1) == 0 ? Res.S_DISC1 : Res.S_DISC2;
                else if (t == ROCK && tAux[i] > 0) continue;        // not fallen yet
                if (t == JBALL) z += 8000;
                z -= 8000;
            } else if (t == FX_BOOM) {
                int k = (tAux[i] - tTim[i]) * 4 / (tAux[i] + 1);
                s = Res.S_FX_BOOM1 + (k > 3 ? 3 : k);
            } else if (t == FX_PUFF) s = tTim[i] > 4 ? Res.S_FX_PUFF1 : Res.S_FX_PUFF2;
            else if (t == FX_BLOOD) s = tTim[i] > 2 ? Res.S_FX_BLOOD1 : Res.S_FX_BLOOD2;
            else if (t == FX_SMOKE) { s = tTim[i] * 2 > tAux[i] ? Res.S_FX_SMOKE1 : Res.S_FX_SMOKE2; z += (tAux[i] - tTim[i]) * 1500; }
            else if (t == FX_DUST) s = tTim[i] * 3 > tAux[i] ? Res.S_FX_SMOKE1 : Res.S_FX_SMOKE2;
            else if (t == TPAD) z = 0;
            else if ((fl & TF_PICK) != 0) z = 1200 + (E.sin(ticks * 80 + i * 500) >> 5) + 1200;
            if (tlight[t] != 0 && (fl & TF_PICK) == 0) lt = lt > 4 ? lt - 4 : 0;
            E.addSprite(s, tX[i], tY[i], z, t == ACTOR && tVZ[i] > 0 ? tVZ[i] : tscale[t], vf, lt);
        }
        if (swR >= 0) {                         // the stomp shockwave: a ring of crackling lightning
            for (int k = 0; k < 20; k++) {
                int a = k * 4096 / 20 + ticks * 37;
                int x = swX + (int) ((long) E.cos(a) * swR >> 16), y = swY + (int) ((long) E.sin(a) * swR >> 16);
                int c = ((y >> 16) << 6) | (x >> 16);
                if (c < 0 || c >= 4096 || wall[c] != 0) continue;
                E.addSprite(Res.S_FX_ZAP, x, y, (k & 1) * 3000, 330, E.VF_BRIGHT, 0);
            }
        }
    }
}
