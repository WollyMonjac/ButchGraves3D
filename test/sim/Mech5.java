/** Checks the episode 5 gadgets with the real world code: pits, pressure plates and darts, spikes, the idol and the
 *  boulder, the rising mummy, the radio, the weeping woman, the Other World. */
public class Mech5 {
    static void at(double x, double y, int a) { W.px = (int) (x * 65536); W.py = (int) (y * 65536); W.pa = a; W.pvx = W.pvy = 0; }

    static void noMonsters() { for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; } }

    static void clearKeys() { W.kFwd = W.kBack = W.kLeft = W.kRight = W.kSL = W.kSR = W.kFire = W.kUse = W.kJump = false; W.sprint = false; }

    static int find(int t) { for (int i = 0; i < W.nt; i++) if (W.tType[i] == t) return i; return -1; }

    static String pos() { return String.format("%.2f,%.2f", W.px / 65536.0, W.py / 65536.0); }

    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true; W.skill = 1; W.health = 100; W.weapons = 31; W.weapon = 1; W.ammo[0] = 100;
        // ---- pits: walk into the tunnel pit of L17 (opened by the trigger), then jump it
        W.load(17); noMonsters(); W.trigger(); W.nPend = 0;
        for (int i = 0; i < W.nt; i++) if (W.tType[i] == W.BOULDER) { W.remove(i); i--; }
        for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; }
        at(32.5, 11.5, 1024); clearKeys(); W.health = 100;
        int fell = 0;
        for (int t = 0; t < 60; t++) { W.kFwd = t < 20; W.tick(); if (W.fallT > 0) fell++; }
        System.out.println("walk into pit: fell for " + fell + " ticks, now at " + pos() + " hp " + W.health + " (want ~23 ticks, back at ~32.5,12.9, hp 85)");
        at(32.5, 11.3, 1024); clearKeys(); W.health = 100; fell = 0;
        for (int t = 0; t < 40; t++) { W.kFwd = true; if (W.py > (int) (12.45 * 65536) && W.onGround && fell == 0) W.kJump = true; W.tick(); if (W.fallT > 0) fell++; }
        System.out.println("jump the pit: fell " + fell + " ticks, now at " + pos() + " hp " + W.health + " (want 0, y > 14)");
        // ---- pressure plate + darts in the hall of darts (L17: plates at y 10 and 7, darters on both walls)
        W.load(17); noMonsters();
        at(20.5, 11.6, 3072); clearKeys(); W.health = 100;
        int darts = 0;
        for (int t = 0; t < 30; t++) { W.kFwd = t < 8; W.tick(); for (int i = 0; i < W.nt; i++) if (W.tType[i] == W.DART) darts++; }
        System.out.println("step on a plate and stop: dart-ticks " + darts + ", hp " + W.health + " (want darts and damage)");
        at(20.5, 11.6, 3072); clearKeys(); W.health = 100; W.ticks += 100;
        for (int t = 0; t < 40; t++) { W.kFwd = true; if (t == 2) W.kJump = true; W.tick(); }
        System.out.println("jump the plate: at " + pos() + " hp " + W.health + " plateCell " + W.plateCell);
        // ---- spikes in the tomb gallery (x 22-24, y 2-4)
        at(23.5, 3.5, 0); clearKeys(); W.health = 100;
        int on = 0;
        for (int t = 0; t < 200; t++) { W.tick(); at(23.5, 3.5, 0); if (W.spikeOn) on++; }
        System.out.println("stand on spikes 200 ticks: hp " + W.health + ", up for " + on + " ticks, tex swapped " + (E.pairOn[1] != null));
        // ---- the idol: the boulder drops and rolls; sprint away and survive, dawdle and get flattened
        for (int mode = 0; mode < 3; mode++) {
            W.load(17); noMonsters(); W.nPend = 0;
            W.health = 100; W.dead = false; G.died = false; java.util.Arrays.fill(W.dmgLog, 0);
            int b = find(W.BOULDER);
            at(32.5, 5.6, 1024); clearKeys();
            W.tick();                        // picks the idol up
            int doorCell = (3 << 6) | 26, tunnel = (10 << 6) | 32;
            int t = 0, maxD = 0, hp = 0;
            for (; t < 400; t++) {
                W.kFwd = mode < 2;
                if (mode == 0 && t > 2 && W.stamina > 100) W.sprint = true;
                if (mode == 0 && W.py > (int) (12.4 * 65536) && W.py < (int) (12.6 * 65536)) W.kJump = true;
                if (mode == 1 && W.py > (int) (12.3 * 65536) && W.py < (int) (12.5 * 65536)) W.kJump = true;
                if (W.py > (int) (19.5 * 65536)) { W.kFwd = false; W.kSL = true; }
                W.tick();
                if (W.dead) break;
            }
            b = find(W.BOULDER);
            System.out.println("idol run (" + (mode == 0 ? "sprint" : mode == 1 ? "walk" : "stand") + "): keys " + W.keys + " sealed " + (W.wall[doorCell] != 0)
                    + " tunnel open " + (W.wall[tunnel] == 0) + " boulder st " + W.tSt[b] + " at " + String.format("%.2f,%.2f", W.tX[b] / 65536.0, W.tY[b] / 65536.0)
                    + " player " + pos() + " hp " + W.health + (W.dead ? " DEAD at t" + t : "") + " dmg other " + W.dmgLog[0]);
        }
        // ---- the rising mummy
        W.load(17); noMonsters();
        at(10.5, 46.5, 3072); clearKeys();
        int m = W.spawn(W.MUMMY, 10 << 16 | 32768, 42 << 16 | 32768);
        W.tSt[m] = W.ST_CHASE;
        int k0 = W.kills;
        W.damageThing(m, 999, -1, 0);
        int rose = -1;
        for (int t = 0; t < 400; t++) { W.tick(); at(10.5, 47.5, 3072); if (W.tSt[m] < W.ST_DIE && rose < 0) rose = t; }
        System.out.println("mummy shot: rose after " + rose + " ticks, hp " + W.tHp[m] + ", kills " + (W.kills - k0) + " (want ~150-230, 55, 0)");
        W.damageThing(m, 999, -1, 0);
        for (int t = 0; t < 400; t++) { W.tick(); at(10.5, 47.5, 3072); }
        System.out.println("mummy shot again: state " + W.tSt[m] + " kills " + (W.kills - k0) + " (want 5 = dead for good, 1)");
        W.health = 100; W.dead = false;
        int m2 = W.spawn(W.MUMMY, 10 << 16 | 32768, 45 << 16 | 32768);
        W.tSt[m2] = W.ST_CHASE;
        W.damageThing(m2, 999, -1, 0);
        for (int t = 0; t < 10; t++) W.tick();
        at(10.5, 46.4, 3072);
        W.weapon = 0; W.wTim = 0; W.kFire = true; W.wSwitch = 0; W.pendingWeapon = -1;
        for (int t = 0; t < 14; t++) { W.tick(); W.kFire = false; at(10.5, 46.4, 3072); }
        System.out.println("downed mummy + shovel: tVY " + W.tVY[m2] + " kills " + (W.kills - k0) + " (want 3, 2)");
        // ---- the fog: radio, weeping woman, Other World
        W.load(19);
        at(27.5, 52.5, 3072); clearKeys();
        int lvl = 0;
        for (int t = 0; t < 120; t++) { W.tick(); at(27.5, 52.5, 3072); lvl = Math.max(lvl, W.radioLvl); }
        System.out.println("radio near the start: max level " + lvl + " fog " + E.fogK);
        noMonsters();
        int wp = W.spawn(W.WEEPER, 27 << 16 | 32768, 34 << 16 | 32768);
        W.tSt[wp] = W.ST_CHASE;
        at(27.5, 44.5, 1024);
        int creeps = 0, lx = W.tX[wp], ly = W.tY[wp];
        for (int t = 0; t < 600; t++) {
            W.tick(); at(27.5, 44.5, 1024);
            if (Math.abs(W.tX[wp] - lx) > 65536 || Math.abs(W.tY[wp] - ly) > 65536) creeps++;
            lx = W.tX[wp]; ly = W.tY[wp];
        }
        System.out.println("weeping woman, 30 s: jumps " + creeps + ", now " + String.format("%.1f,%.1f", W.tX[wp] / 65536.0, W.tY[wp] / 65536.0) + " (Butch at 27.5,44.5)");
        W.load(19);
        int pend = W.nPend, mons0 = 0;
        for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) mons0++;
        int church = (5 << 6) | 20;
        int w0 = W.wall[church];
        at(28.5, 7.7, 3072); clearKeys(); W.health = 100; W.dead = false;
        W.tick();
        for (int t = 0; t < 100; t++) { W.tick(); W.health = 100; }
        int mons1 = 0;
        for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) mons1++;
        System.out.println("red key: keys " + W.keys + " church wall " + w0 + " -> " + W.wall[church] + " (rust " + (Res.T_RUST + 1) + ") sky " + W.skyTex
                + " (sky8 " + Res.T_SKY8 + ") rust loaded " + (E.tex[Res.T_RUST] != null) + " monsters " + mons0 + " -> " + mons1 + " (pending " + pend
                + ") fog " + E.fogR + "," + E.fogG + "," + E.fogB);
    }
}
