import java.io.DataInputStream;

/** World state and gameplay: level, player, monsters, weapons, projectiles, doors, pickups, particles. */
final class W {
    // ------------------------------------------------------------------ map
    static final int F_DOOR = 1, F_SECRET = 2, F_EXIT = 4, F_HURT = 8, F_KRED = 16, F_KBLUE = 32, F_KGOLD = 64, F_OUT = 128;
    static final byte[] wall = new byte[4096], flr = new byte[4096], cel = new byte[4096], flag = new byte[4096], seen = new byte[4096];
    static final int[] door = new int[4096], light = new int[4096], baseLight = new int[4096];
    static final byte[] flick = new byte[4096], dstate = new byte[4096];
    static final short[] dtime = new short[4096];
    static int skyTex = -1, level, skill = 1, lightning, lvMusic, mapW, mapH;
    static String lvName = "", lvSub = "";
    static int fogR, fogG, fogB;

    // ------------------------------------------------------------------ thing types
    static final int ZOMBIE = 1, SCARE = 2, WRAITH = 3, WITCH = 4, BOSS = 5;
    static final int CANDY = 10, BUCKET = 11, BREW = 12, ARMOR = 13, BULLETS = 14, SHELLS = 15, PUMPKINS = 16, SHOTGUN = 17,
            TOMMY = 18, LAUNCHER = 19, KEYR = 20, KEYB = 21, KEYG = 22;
    static final int JACK = 30, JACK2 = 31, CANDLES = 32, TREE = 33, TOMB = 34, TOMB2 = 35, HANGING = 36, CAULDRON = 37, KEG = 38,
            SKULLS = 39, LAMP = 40, PATCH = 41, GIBS = 42;
    static final int FIREBALL = 50, GREENBALL = 51, BOSSBALL = 52, PBOMB = 53;
    static final int FX_BOOM = 60, FX_PUFF = 61, FX_BLOOD = 62, FX_SPARK = 63, FX_GREEN = 64, FX_ECTO = 65;
    static final int NTYPE = 70;
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
        defType(FIREBALL, TF_PROJ | TF_BRIGHT, Res.S_FIREBALL1, 300, 8000, 0);
        defType(GREENBALL, TF_PROJ | TF_BRIGHT, Res.S_GREENBALL1, 300, 8000, 0);
        defType(BOSSBALL, TF_PROJ | TF_BRIGHT, Res.S_FX_BOOM1, 230, 12000, 0);
        defType(PBOMB, TF_PROJ, Res.S_PBOMB, 400, 9000, 0);
        defType(FX_BOOM, TF_FX | TF_BRIGHT, Res.S_FX_BOOM1, 520, 0, 0);
        defType(FX_PUFF, TF_FX, Res.S_FX_PUFF1, 256, 0, 0);
        defType(FX_BLOOD, TF_FX, Res.S_FX_BLOOD1, 300, 0, 0);
        defType(FX_SPARK, TF_FX | TF_BRIGHT, Res.S_FX_SPARK, 256, 0, 0);
        defType(FX_GREEN, TF_FX | TF_BRIGHT, Res.S_FX_GREEN, 360, 0, 0);
        defType(FX_ECTO, TF_FX | TF_BRIGHT, Res.S_FX_ECTO, 360, 0, 0);
    }

    // monster tables (index by type 1..5)
    static final int[] M_HP = {0, 55, 90, 60, 100, 3200};
    static final int[] M_SPD = {0, 2300, 2000, 4000, 1900, 2600};
    static final int[] M_MELEE = {0, 8, 8, 9, 7, 22};
    static final int[] M_PAIN = {0, 190, 110, 150, 90, 18};
    static final int[][] M_SPR = {null,
            {Res.S_ZOMBIE_WALK1, Res.S_ZOMBIE_WALK2, Res.S_ZOMBIE_ATTACK, Res.S_ZOMBIE_PAIN, Res.S_ZOMBIE_FALL, Res.S_ZOMBIE_DEAD},
            {Res.S_SCARECROW_WALK1, Res.S_SCARECROW_WALK2, Res.S_SCARECROW_ATTACK, Res.S_SCARECROW_PAIN, Res.S_SCARECROW_FALL, Res.S_SCARECROW_DEAD},
            {Res.S_WRAITH_WALK1, Res.S_WRAITH_WALK2, Res.S_WRAITH_ATTACK, Res.S_WRAITH_PAIN, Res.S_WRAITH_FALL, Res.S_WRAITH_DEAD},
            {Res.S_WITCH_WALK1, Res.S_WITCH_WALK2, Res.S_WITCH_ATTACK, Res.S_WITCH_PAIN, Res.S_WITCH_FALL, Res.S_WITCH_DEAD},
            {Res.S_BOSS_WALK1, Res.S_BOSS_WALK2, Res.S_BOSS_ATTACK, Res.S_BOSS_PAIN, Res.S_BOSS_FALL, Res.S_BOSS_DEAD}};
    static final int ST_IDLE = 0, ST_CHASE = 1, ST_ATK = 2, ST_PAIN = 3, ST_DIE = 4, ST_DEAD = 5;

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
    static int P_RED, P_DRED, P_YEL, P_GREEN, P_ORANGE, P_GREY, P_CYAN;

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
    }

    static void load(int lv) throws java.io.IOException {
        level = lv;
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
        in.readUnsignedByte();
        mapW = in.readUnsignedByte();
        mapH = in.readUnsignedByte();
        int sx = in.readShort(), sy = in.readShort(), sa = in.readShort();
        skyTex = sky == 255 ? -1 : (sky == 0 ? Res.T_SKY0 : Res.T_SKY1);
        for (int i = 0; i < 4096; i++) {
            wall[i] = (byte) (Res.T_STONE + 1); flr[i] = 0; cel[i] = 0; flag[i] = 0; seen[i] = 0; door[i] = 0; baseLight[i] = 20;
            flick[i] = 0; dstate[i] = 0; dtime[i] = 0;
        }
        byte[] row = new byte[mapW];
        for (int a = 0; a < 5; a++) {
            for (int y = 0; y < mapH; y++) {
                in.readFully(row);
                for (int x = 0; x < mapW; x++) {
                    int c = (y << 6) | x;
                    if (a == 0) wall[c] = row[x];
                    else if (a == 1) flr[c] = (byte) (Res.T_GRASS + (row[x] & 255));
                    else if (a == 2) cel[c] = (row[x] & 255) == 255 ? (byte) 255 : (byte) (Res.T_GRASS + (row[x] & 255));
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
        for (int i = 0; i < n; i++) {
            int t = in.readUnsignedByte();
            int x = in.readShort() << 12, y = in.readShort() << 12;
            int sk = in.readByte();
            if (sk > skill) continue;
            if (skill == 0 && (tfl[t] & TF_MON) != 0 && t != BOSS && (i % 3) == 2) continue;
            int k = spawn(t, x, y);
            if (k >= 0 && (tfl[t] & TF_MON) != 0) totalKills++;
        }
        in.close();
        px = sx << 12; py = sy << 12; pa = sa & 4095; pz = 0; pvz = 0; pvx = 0; pvy = 0;
        kills = 0; secrets = 0; ticks = 0; dead = false; deadTim = 0; exitHit = false; bossDeadT = -1;
        flashDmg = 0; flashPick = 0; kick = 0; hurtTim = 0; wTim = 0; wFrame = 0; wRaise = 0; wSwitch = 0; pendingWeapon = -1;
        noiseX = -1; lightningT = 200 + rnd(300); lightningBoost = 0; thunderT = 0; lowHpWarn = 0;
        keys = 0;
        bakeLights();
        E.setFog(fogR, fogG, fogB);
        flowCell = -1;
    }

    /** Pre-compute light from jack-o-lanterns, candles, lamps and cauldrons (with line of sight). */
    static void bakeLights() {
        for (int i = 0; i < nt; i++) {
            int str = tlight[tType[i]];
            if (str == 0) continue;
            int cx = tX[i] >> 16, cy = tY[i] >> 16, r = str >= 11 ? 4 : 3;
            boolean flame = tType[i] != LAMP;
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
        tHp[i] = t <= BOSS ? M_HP[t] * (skill == 2 ? 13 : 10) / 10 : (t == KEG ? 15 : 1);
        if (t == WRAITH) tZ[i] = 9000;
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
        if ((flag[c] & F_DOOR) != 0 && door[c] > 56000) return false;
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
                }
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
                    G.msg(need == 1 ? "You need the RED skull key" : need == 2 ? "You need the BLUE skull key" : "You need the GOLD skull key", 0xff4030);
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
            flag[c] = (byte) (f & ~F_SECRET | F_DOOR);
            secrets++;
            G.msg("A secret is revealed!", 0xc080ff);
            Snd.sfx(Snd.SECRET);
            G.voice(Snd.V_SECRET, "Ooh. Secret stash.", 60);
            flag[c] = (byte) (flag[c] | F_SECRET);   // keep the disguise texture; mark as found below
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
                door[c] += 4600;
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
        if ((f & F_DOOR) != 0 && door[c] < 65536) openDoor(c, true);
        else if (!bump && wall[c] != 0) Snd.sfx(Snd.CLICK);
    }

    // ================================================================== tick

    static boolean kFwd, kBack, kLeft, kRight, kSL, kSR, kFire, kUse, kJump;

    static void tick() {
        ticks++;
        if (tCantMsg > 0) tCantMsg--;
        updateDoors();
        if (!dead) playerTick();
        else {
            deadTim++;
            if (pz > -26000) pz -= 1500;
        }
        updateFlow();
        for (int i = 0; i < nt; i++) {
            int t = tType[i];
            int fl = tfl[t];
            if ((fl & TF_MON) != 0) monsterTick(i);
            else if ((fl & TF_PROJ) != 0) { if (projTick(i)) i--; }
            else if ((fl & TF_FX) != 0) {
                if (--tTim[i] <= 0) { remove(i); i--; continue; }
                tZ[i] += tVZ[i];
            } else if ((fl & TF_PICK) != 0 && !dead) {
                if (pickTick(i)) i--;
            } else if (t == KEG && tHp[i] <= 0) {
                int x = tX[i], y = tY[i];
                remove(i);
                i--;
                explode(x, y, 10000, 150, 2 << 16, -2);
            }
        }
        particlesTick();
        lightsTick();
        if (noiseT > 0 && --noiseT == 0) noiseX = -1;
        if (flashDmg > 0) flashDmg -= 12;
        if (flashPick > 0) flashPick -= 10;
        if (kick > 0) kick -= 2;
        if (shake > 0) shake--;
        if (bossDeadT >= 0 && ++bossDeadT == 90) G.victory();
        if (bossDeadT >= 0 && bossDeadT < 60 && (bossDeadT & 7) == 0)
            explode(bossX + rr(-40000, 40000), bossY + rr(-40000, 40000), 20000 + rnd(30000), 0, 0, -2);
    }

    static int bossX, bossY;

    // ------------------------------------------------------------------ player

    static void playerTick() {
        // turning with acceleration
        if (kLeft || kRight) {
            turnHeld++;
            int sp = turnHeld < 4 ? 36 : turnHeld < 8 ? 58 : 76;
            pa = (pa + (kLeft ? -sp : sp)) & 4095;
        } else turnHeld = 0;
        int fwd = 0, side = 0;
        if (kFwd) fwd += 7400;
        if (kBack) fwd -= 5600;
        if (kSL) side -= 6200;
        if (kSR) side += 6200;
        int c = E.cos(pa), s = E.sin(pa);
        int tvx = (int) (((long) c * fwd - (long) s * side) >> 16);
        int tvy = (int) (((long) s * fwd + (long) c * side) >> 16);
        pvx += (tvx - pvx) / 2;
        pvy += (tvy - pvy) / 2;
        int r = 16000;
        int nx = px + pvx, ny = py + pvy;
        if (!blocked(nx, py, r) && thingAt(nx, py, r, -1) < 0) px = nx;
        else bumpAt(nx + (pvx > 0 ? r : -r), py);
        if (!blocked(px, ny, r) && thingAt(px, ny, r, -1) < 0) py = ny;
        else bumpAt(px, ny + (pvy > 0 ? r : -r));
        if (kUse) { use(false); kUse = false; }
        // bobbing
        int spd = (pvx < 0 ? -pvx : pvx) + (pvy < 0 ? -pvy : pvy);
        if (spd > 1500 && onGround) bobPhase = (bobPhase + 150) & 4095;
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
        // hurt floors
        int pc = ((py >> 16) << 6) | (px >> 16);
        if ((flag[pc] & F_HURT) != 0 && onGround && wall[pc] == 0) {
            if (++hurtTim >= 14) {
                hurtTim = 0;
                damagePlayer(flr[pc] == Res.T_LAVA ? 10 : 6, -1);
            }
        } else hurtTim = 10;
        weaponTick();
        if (health < 25 && health > 0 && ticks - lowHpWarn > 600) {
            lowHpWarn = ticks;
            G.voice(Snd.V_LOWHP, "I need candy. Lots of candy.", 0);
        }
    }

    static void bumpAt(int x, int y) {
        int c = ((y >> 16) << 6) | (x >> 16);
        if (c < 0 || c >= 4096 || !kFwd) return;
        int f = flag[c];
        if ((f & F_DOOR) != 0 && dstate[c] == 0) openDoor(c, true);
        else if ((f & F_EXIT) != 0) use(true);
    }

    static boolean god;

    static void damagePlayer(int d, int from) {
        if (dead || d <= 0 || god) return;
        if (skill == 0) d = d * 6 / 10;
        if (skill == 2) d = d * 14 / 10;
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
            Snd.voice(Snd.V_DIE);
            G.died();
        } else {
            Snd.sfx(Snd.HURT);
            if (rnd(3) == 0) Snd.voice(rnd(2) == 0 ? Snd.V_PAIN1 : Snd.V_PAIN2);
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

    static void weaponTick() {
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
            if ((tfl[t] & TF_MON) != 0 && tSt[i] >= ST_DIE) continue;
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
            if (tType[best] <= BOSS && tSt[best] >= ST_DIE && rnd(3) == 0) G.voice(Snd.V_SHOVEL, "Dig that!", 0);
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
        if (t == KEG) {
            tHp[i] -= d;
            spark(tX[i], tY[i], 20000, 4, P_YEL);
            return;
        }
        if ((tfl[t] & TF_MON) == 0 || tSt[i] >= ST_DIE) return;
        tHp[i] -= d;
        // blood
        int bz = t == BOSS ? 60000 : 36000;
        if (t == WRAITH) spark(tX[i], tY[i], bz, 5, P_CYAN);
        else if (t == SCARE) { spark(tX[i], tY[i], bz, 3, P_ORANGE); blood(tX[i], tY[i], bz, 3); }
        else blood(tX[i], tY[i], bz, 6);
        if (tSt[i] == ST_IDLE) { tSt[i] = ST_CHASE; sightSound(t, i); }
        if (tHp[i] <= 0) {
            kill(i, kind == 2 && tHp[i] < -40 && t != BOSS && t != WRAITH);
        } else if (rnd(256) < M_PAIN[t] && tSt[i] != ST_ATK) {
            tSt[i] = ST_PAIN;
            tTim[i] = 5;
        } else if (t == BOSS && rnd(4) == 0) Snd.sfxAt(Snd.BOSS, tX[i], tY[i]);
    }

    static void kill(int i, boolean gib) {
        int t = tType[i];
        kills++;
        G.face(3, 20);
        if (t == BOSS) {
            tSt[i] = ST_DIE;
            tTim[i] = 30;
            bossDeadT = 0;
            bossX = tX[i]; bossY = tY[i];
            Snd.sfx(Snd.BOSSDIE);
            G.voice(Snd.V_WIN, "Happy Halloween.", 0);
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
        Snd.sfxAt(Snd.MDIE, tX[i], tY[i]);
        if (t == WRAITH) sayKill(2);
        else if (t == SCARE) sayKill(3);
        else sayKill(0);
    }

    static void sayKill(int kind) {
        if (ticks - lastVoiceTick < 140 || rnd(10) > 4) return;
        lastVoiceTick = ticks;
        switch (kind) {
            case 2: G.voice(Snd.V_GHOST, "Boo yourself.", 0); break;
            case 3: G.voice(Snd.V_PUMPKIN, "Pumpkin pie, anyone?", 0); break;
            case 4: G.voice(Snd.V_GIB, "Who ordered extra crispy?", 0); break;
            default: {
                int r = rnd(3);
                if (r == 0) G.voice(Snd.V_KILL1, "Rest in pieces.", 0);
                else if (r == 1) G.voice(Snd.V_KILL2, "Back in the ground, ugly.", 0);
                else G.voice(Snd.V_KILL3, "Stay dead this time.", 0);
            }
        }
    }

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
            int d = E.dist(tX[i] - x, tY[i] - y) - trad[t];
            if (d < 0) d = 0;
            if (d >= rad) continue;
            if (!losCells(x, y, tX[i], tY[i], true)) continue;
            int dd = (int) ((long) dmg * (rad - d) / rad);
            if (t == KEG) { if (tHp[i] > 0) tHp[i] -= dd; }
            else damageThing(i, dd, src, 2);
        }
        if (!dead && dp < rad && losCells(x, y, px, py, true)) {
            int dd = (int) ((long) dmg * (rad - dp) / rad);
            if (src == -2) dd = dd / 2;
            damagePlayer(dd, -1);
        }
    }

    // ------------------------------------------------------------------ monsters

    static void sightSound(int t, int i) {
        int s = t == ZOMBIE ? Snd.ZOMBIE : t == SCARE ? Snd.SCARE : t == WRAITH ? Snd.GHOST : t == WITCH ? Snd.WITCH : Snd.BOSS;
        Snd.sfxAt(s, tX[i], tY[i]);
        if (t == BOSS && ticks - lastVoiceTick > 40) {
            lastVoiceTick = ticks;
            G.voice(Snd.V_BOSS, "Your reign is over, gourd boy.", 40);
        }
    }

    static void monsterTick(int i) {
        int t = tType[i], st = tSt[i];
        if (t == GIBS) return;
        if (t == WRAITH) tZ[i] = 9000 + (E.sin(ticks * 60 + i * 300) >> 4);
        if (st == ST_DEAD) return;
        if (st == ST_DIE) {
            if (--tTim[i] <= 0) tSt[i] = ST_DEAD;
            return;
        }
        int dx = px - tX[i], dy = py - tY[i];
        int d = E.dist(dx, dy);
        if (tCool[i] > 0) tCool[i]--;
        if (((ticks + i) & 3) == 0) tLos[i] = d < (t == BOSS ? (30 << 16) : (18 << 16)) && losCells(tX[i], tY[i], px, py, true);
        if (st == ST_IDLE) {
            if (((ticks + i) & 7) != 0) return;
            boolean wake = (tLos[i] && d < (13 << 16)) || (t == BOSS && d < (24 << 16));
            if (!wake && noiseX >= 0 && E.dist(noiseX - tX[i], noiseY - tY[i]) < (t == BOSS ? (32 << 16) : (9 << 16))) wake = true;
            if (wake) {
                tSt[i] = ST_CHASE;
                tCool[i] = 10 + rnd(20);
                sightSound(t, i);
            }
            return;
        }
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
        int melee = t == BOSS ? 100000 : 58000;
        if (d < melee && tCool[i] == 0 && tLos[i]) {
            tSt[i] = ST_ATK;
            tTim[i] = 9;
            tAux[i] = 4;
            tCool[i] = t == ZOMBIE ? 22 : t == BOSS ? 20 : 24;
            tVZ[i] = 0;     // melee
            return;
        }
        if ((t == SCARE || t == WITCH || t == BOSS) && tCool[i] == 0 && tLos[i] && d < (t == BOSS ? (24 << 16) : (15 << 16)) && d > 70000 && rnd(t == BOSS ? 8 : 18) == 0) {
            tSt[i] = ST_ATK;
            tTim[i] = t == BOSS ? 14 : 11;
            tAux[i] = 5;
            tCool[i] = t == BOSS ? 22 + rnd(16) : 30 + rnd(30);
            tVZ[i] = 1;     // ranged
            return;
        }
        if (t == WRAITH && tLos[i] && d < (5 << 16) && rnd(40) == 0) Snd.sfxAt(Snd.GHOST, tX[i], tY[i]);
        if (t == BOSS && (ticks % 260) == 0) summon(i);
        // movement
        int spd = M_SPD[t];
        int tx, ty;
        if (tLos[i] && d < (9 << 16)) { tx = px; ty = py; }
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
        int r = t == BOSS ? 24000 : trad[t];
        int nx = tX[i] + vx, ny = tY[i] + vy;
        int pr = 16000 + r;
        boolean nearP = !dead && (long) (nx - px) * (nx - px) + (long) (ny - py) * (ny - py) < (long) pr * pr;
        if (!nearP) {
            boolean moved = false;
            if (!blocked(nx, tY[i], r) && thingAt(nx, tY[i], r, i) < 0) { tX[i] = nx; moved = true; }
            if (!blocked(tX[i], ny, r) && thingAt(tX[i], ny, r, i) < 0) { tY[i] = ny; moved = true; }
            if (!moved) {
                // jitter sideways to get unstuck
                int jx = tX[i] + (rnd(2) == 0 ? spd : -spd), jy = tY[i] + (rnd(2) == 0 ? spd : -spd);
                if (!blocked(jx, jy, r) && thingAt(jx, jy, r, i) < 0) { tX[i] = jx; tY[i] = jy; }
            }
        }
    }

    static void doAttack(int i, int d) {
        int t = tType[i];
        if (tVZ[i] == 0) {
            int reach = t == BOSS ? 120000 : 72000;
            if (d < reach && tLos[i]) {
                int dm = M_MELEE[t];
                damagePlayer(rr(dm * 3 / 4, dm * 5 / 4), i);
                if (t == ZOMBIE || t == BOSS) Snd.sfx(Snd.HIT);
            }
            return;
        }
        int a = E.atan2(py - tY[i], px - tX[i]);
        if (t == BOSS) {
            for (int k = -1; k <= 1; k++) shootBall(i, BOSSBALL, (a + k * 120) & 4095, 15, 42000);
            Snd.sfxAt(Snd.FIREBALL, tX[i], tY[i]);
        } else if (t == WITCH) {
            shootBall(i, GREENBALL, a, 17, 34000);
            Snd.sfxAt(Snd.WITCH, tX[i], tY[i]);
        } else {
            shootBall(i, FIREBALL, a, 13, 38000);
            Snd.sfxAt(Snd.FIREBALL, tX[i], tY[i]);
        }
    }

    static void shootBall(int src, int type, int a, int speed64, int z) {
        int i = spawn(type, tX[src] + (E.cos(a) >> 2), tY[src] + (E.sin(a) >> 2));
        if (i < 0) return;
        tVX[i] = E.cos(a) * speed64 >> 6;
        tVY[i] = E.sin(a) * speed64 >> 6;
        tZ[i] = z;
        tOwn[i] = src;
    }

    static void summon(int boss) {
        int alive = 0;
        for (int i = 0; i < nt; i++) if ((tfl[tType[i]] & TF_MON) != 0 && tSt[i] < ST_DIE) alive++;
        if (alive > 7) return;
        for (int k = 0; k < 2; k++) {
            int a = rnd(4096);
            int x = tX[boss] + (E.cos(a) * 2), y = tY[boss] + (E.sin(a) * 2);
            if (blocked(x, y, 20000)) continue;
            int i = spawn(k == 0 ? WRAITH : ZOMBIE, x, y);
            if (i >= 0) {
                tSt[i] = ST_CHASE;
                totalKills++;
                fx(FX_GREEN, x, y, 20000, 10);
            }
        }
        Snd.sfxAt(Snd.BOSS, tX[boss], tY[boss]);
    }

    // ------------------------------------------------------------------ projectiles

    static boolean projTick(int i) {
        int t = tType[i];
        int nx = tX[i] + tVX[i], ny = tY[i] + tVY[i];
        tAnim[i]++;
        boolean hitWall = blocked(nx, ny, 4000);
        if (t == PBOMB) {
            for (int k = 0; k < nt; k++) {
                int tt = tType[k];
                if ((tfl[tt] & TF_SHOOT) == 0 || ((tfl[tt] & TF_MON) != 0 && tSt[k] >= ST_DIE)) continue;
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
        } else {
            int dx = px - nx, dy = py - ny;
            int r = trad[t] + 14000;
            if (!dead && dx < r && dx > -r && dy < r && dy > -r) {
                damagePlayer(t == BOSSBALL ? rr(16, 26) : t == GREENBALL ? rr(12, 20) : rr(10, 18), tOwn[i]);
                hitWall = true;
            }
            if (hitWall) {
                fx(t == GREENBALL ? FX_GREEN : FX_SPARK, tX[i], tY[i], tZ[i] - 8000, 6);
                spark(tX[i], tY[i], tZ[i], 4, t == GREENBALL ? P_GREEN : P_ORANGE);
                remove(i);
                return true;
            }
        }
        tX[i] = nx;
        tY[i] = ny;
        if (t == PBOMB) { tZ[i] += tVZ[i]; tVZ[i] -= 30; if (tZ[i] < 4000) tZ[i] = 4000; }
        return false;
    }

    // ------------------------------------------------------------------ pickups

    static boolean pickTick(int i) {
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
                ammo[0] += 24; if (ammo[0] > AMAX[0]) ammo[0] = AMAX[0]; m = "Silver bullets"; break;
            case SHELLS:
                if (ammo[1] >= AMAX[1]) return false;
                ammo[1] += 8; if (ammo[1] > AMAX[1]) ammo[1] = AMAX[1]; m = "Shotgun shells"; break;
            case PUMPKINS:
                if (ammo[2] >= AMAX[2]) return false;
                ammo[2] += 4; if (ammo[2] > AMAX[2]) ammo[2] = AMAX[2]; m = "Pumpkin bombs"; break;
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
            default: return false;
        }
        if (t >= KEYR) Snd.sfx(Snd.KEY);
        else if (t != SHOTGUN && t != TOMMY && t != LAUNCHER) Snd.sfx(Snd.PICKUP);
        flashPick = 90;
        G.msg(m, col);
        remove(i);
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
                if (t == BOSS && st == ST_ATK) vf &= ~E.VF_TRANS;
            } else if (t == GIBS) s = Res.S_GIBS;
            else if ((fl & TF_PROJ) != 0) {
                if (t == FIREBALL) s = (tAnim[i] & 2) == 0 ? Res.S_FIREBALL1 : Res.S_FIREBALL2;
                else if (t == BOSSBALL) { s = (tAnim[i] & 2) == 0 ? Res.S_FX_BOOM1 : Res.S_FX_BOOM2; z -= 6000; }
                else if (t == GREENBALL) s = (tAnim[i] & 2) == 0 ? Res.S_GREENBALL1 : Res.S_GREENBALL2;
                z -= 8000;
            } else if (t == FX_BOOM) {
                int k = (tAux[i] - tTim[i]) * 4 / (tAux[i] + 1);
                s = Res.S_FX_BOOM1 + (k > 3 ? 3 : k);
            } else if (t == FX_PUFF) s = tTim[i] > 4 ? Res.S_FX_PUFF1 : Res.S_FX_PUFF2;
            else if (t == FX_BLOOD) s = tTim[i] > 2 ? Res.S_FX_BLOOD1 : Res.S_FX_BLOOD2;
            else if ((fl & TF_PICK) != 0) z = 1200 + (E.sin(ticks * 80 + i * 500) >> 5) + 1200;
            if (t == JACK || t == JACK2 || t == CANDLES || t == LAMP) lt = lt > 4 ? lt - 4 : 0;
            E.addSprite(s, tX[i], tY[i], z, tscale[t], vf, lt);
        }
    }
}
