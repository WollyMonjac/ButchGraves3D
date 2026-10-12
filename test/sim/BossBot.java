/**
 * Plays a boss level with a "decent human" bot: imperfect aim, limited turn speed, strafes to dodge,
 * keeps its distance, grabs health/ammo when low. Usage: BossBot level skill runs [maxTicks]
 * Prints win rate, fight time and health left so the difficulty curve can be checked.
 */
public class BossBot {
    static java.util.Random R;

    public static void main(String[] a) throws Exception {
        int lv = Integer.parseInt(a[0]), skill = Integer.parseInt(a[1]), runs = Integer.parseInt(a[2]);
        int maxT = a.length > 3 ? Integer.parseInt(a[3]) : 20 * 60 * 5;
        E.load();
        W.initColors();
        G.quiet = true;
        int wins = 0; long tSum = 0; int hpSum = 0; int deathT = 0;
        StringBuffer detail = new StringBuffer();
        for (int run = 0; run < runs; run++) {
            R = new java.util.Random(run * 7919 + 13);
            W.seed = 1000 + run * 31;
            W.skill = skill;
            W.health = 100; W.armor = 25; W.weapons = 31; W.weapon = 3; W.ammo[0] = 120; W.ammo[1] = 24; W.ammo[2] = 6;
            W.load(lv);
            G.won = G.died = false;
            int t = 0, strafe = 1, strafeT = 0, aimErr = 0, aimT = 0, fightStart = -1;
            for (; t < maxT && !G.won && !G.died; t++) {
                bot(t);
                W.tick();
                if (fightStart < 0 && W.bossIdx >= 0) fightStart = t;
            }
            int ft = (t - Math.max(0, fightStart)) / 20;
            if (G.won) { wins++; tSum += ft; hpSum += W.health; }
            else if (G.died) deathT += ft;
            int bh = W.bossIdx >= 0 ? W.tHp[W.bossIdx] * 100 / W.bossMax : -1;
            detail.append(G.won ? "W" : G.died ? "D" : "T").append(ft).append("s/").append(G.won ? W.health : bh).append(G.won ? "hp " : "%boss ");
        }
        StringBuffer dl = new StringBuffer();
        for (int k = 0; k < W.NTYPE; k++) if (W.dmgLog[k] > 0) dl.append(k == 0 ? "other" : "type" + k).append("=").append(W.dmgLog[k] / runs).append(" ");
        System.out.println("   damage per run by source: " + dl);
        System.out.println("level " + lv + " skill " + skill + ": won " + wins + "/" + runs
                + (wins > 0 ? "  avg fight " + (tSum / wins) + "s  avg hp left " + (hpSum / wins) : "")
                + "   [" + detail.toString().trim() + "]");
    }

    static int strafe = 1, strafeT, aimErr, aimT;
    static { R = new java.util.Random(1); }

    static void bot(int t) {
        W.kFwd = W.kBack = W.kLeft = W.kRight = W.kSL = W.kSR = W.kFire = false;
        // target: the boss if visible, else the nearest visible monster
        int best = -1, bd = Integer.MAX_VALUE;
        for (int i = 0; i < W.nt; i++) {
            int ty = W.tType[i];
            if (!W.isMon(ty) || W.tSt[i] >= W.ST_DIE) continue;
            int d = E.dist(W.tX[i] - W.px, W.tY[i] - W.py);
            if (W.isBoss(ty) && W.tSt[i] != W.ST_IDLE) d -= 3 << 16;
            if (d < bd && W.losCells(W.px, W.py, W.tX[i], W.tY[i], true)) { bd = d; best = i; }
        }
        // low on health or ammo: go for the nearest visible pickup
        boolean needHp = W.health < 45, needAmmo = W.ammo[0] < 20 && W.ammo[1] < 4;
        int pick = -1, pd = Integer.MAX_VALUE;
        if (needHp || needAmmo) {
            for (int i = 0; i < W.nt; i++) {
                int ty = W.tType[i];
                if ((W.tfl[ty] & W.TF_PICK) == 0 || W.tSt[i] > 0) continue;
                boolean hp = ty == W.CANDY || ty == W.BUCKET || ty == W.BREW;
                boolean am = ty == W.BULLETS || ty == W.SHELLS || ty == W.PUMPKINS || ty == W.TOMMY || ty == W.SHOTGUN;
                if (!((needHp && hp) || (needAmmo && am))) continue;
                int d = E.dist(W.tX[i] - W.px, W.tY[i] - W.py);
                if (d < pd && d < (14 << 16) && W.losCells(W.px, W.py, W.tX[i], W.tY[i], true)) { pd = d; pick = i; }
            }
        }
        if (--aimT <= 0) { aimT = 15 + R.nextInt(20); aimErr = R.nextInt(141) - 70; }
        if (--strafeT <= 0) { strafeT = 20 + R.nextInt(30); strafe = R.nextBoolean() ? 1 : -1; }
        int goal = -1;
        if (pick >= 0) goal = E.atan2(W.tY[pick] - W.py, W.tX[pick] - W.px);
        else if (best >= 0) goal = (E.atan2(W.tY[best] - W.py, W.tX[best] - W.px) + aimErr) & 4095;
        if (goal >= 0) {
            int diff = (goal - W.pa) & 4095; if (diff > 2048) diff -= 4096;
            if (diff > 50) W.kRight = true; else if (diff < -50) W.kLeft = true;
            if (pick >= 0) W.kFwd = diff > -300 && diff < 300;
            else {
                W.kFire = diff > -90 && diff < 90;
                boolean boss = W.isBoss(W.tType[best]);
                int keep = boss ? (6 << 16) : (3 << 16);
                if (bd > keep + (2 << 16)) W.kFwd = true;
                else if (bd < keep) W.kBack = true;
                if (boss || bd < (8 << 16)) { if (strafe > 0) W.kSR = true; else W.kSL = true; }
            }
        } else {
            // nothing visible: wander toward the arena centre
            int cx = (W.mapW << 15), cy = (W.mapH << 15);
            int g2 = E.atan2(cy - W.py, cx - W.px);
            int diff = (g2 - W.pa) & 4095; if (diff > 2048) diff -= 4096;
            if (diff > 60) W.kRight = true; else if (diff < -60) W.kLeft = true; else W.kFwd = true;
        }
        // dodge: an enemy projectile heading our way -> strafe out of its path (reaction ~0.3 s)
        for (int i = 0; i < W.nt; i++) {
            int ty = W.tType[i];
            if ((W.tfl[ty] & W.TF_PROJ) == 0 || ty == W.PBOMB) continue;
            int dx = W.px - W.tX[i], dy = W.py - W.tY[i];
            int d = E.dist(dx, dy);
            if (d > (7 << 16) || d < (1 << 15)) continue;
            long dot = (long) dx * W.tVX[i] + (long) dy * W.tVY[i];
            if (dot <= 0) continue;
            long cross = (long) dx * W.tVY[i] - (long) dy * W.tVX[i];
            int sp = E.dist(W.tVX[i], W.tVY[i]);
            if (sp == 0) continue;
            long miss = Math.abs(cross) / sp;           // closest-approach distance
            if (miss > 40000 || R.nextInt(100) < 35) continue;   // not dangerous, or bot didn't notice
            // projectile velocity in our local frame decides which way to step
            int side = (int) (((long) W.tVX[i] * -E.sin(W.pa) + (long) W.tVY[i] * E.cos(W.pa)) >> 16);
            W.kSR = cross > 0; W.kSL = !W.kSR;
            if (Math.abs(side) > Math.abs(sp) / 2) { W.kSR = side < 0; W.kSL = side > 0; W.kFwd = false; W.kBack = true; }
            strafeT = 12;
            break;
        }
        // Frankenstein Prime's stomp: jump as the ring arrives (a decent human makes it most of the time)
        if (W.swR >= 0 && W.onGround) {
            int dp = E.dist(W.px - W.swX, W.py - W.swY) - W.swR;
            if (dp > 4000 && dp < 30000 && R.nextInt(100) < 55) W.kJump = true;
        }
        // never step onto lava/slime (or a live shock floor): check where this tick's movement would put us
        int fw = (W.kFwd ? 7400 : 0) - (W.kBack ? 5600 : 0), sd = (W.kSR ? 6200 : 0) - (W.kSL ? 6200 : 0);
        int c = E.cos(W.pa), s = E.sin(W.pa);
        for (int look = 2; look <= 6; look += 2) {
            int nx = W.px + (int) (((long) c * fw - (long) s * sd) * look >> 16), ny = W.py + (int) (((long) s * fw + (long) c * sd) * look >> 16);
            int cell = ((ny >> 16) << 6) | (nx >> 16);
            if (cell >= 0 && cell < 4096 && ((W.flag[cell] & W.F_HURT) != 0 || ((W.flr[cell] & 255) == Res.T_SHOCK && W.shockOn))) {
                if (W.kSR || W.kSL) { boolean r = W.kSR; W.kSR = !r; W.kSL = r; strafe = -strafe; strafeT = 25; }
                if (W.kFwd) { W.kFwd = false; }
                if (W.kBack) { W.kBack = false; }
                break;
            }
        }
        // weapon choice: launcher only at range
        if (best >= 0 && W.isBoss(W.tType[best]) && bd > (4 << 16) && W.ammo[2] > 0 && W.weapon != W.WLAUNCH && W.pendingWeapon < 0) W.selectWeapon(W.WLAUNCH);
        else if (W.weapon == W.WLAUNCH && (bd < (3 << 16) || W.ammo[2] == 0) && W.pendingWeapon < 0) W.autoSwitch();
    }
}
