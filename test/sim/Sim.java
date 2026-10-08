/** Headless world simulation: loads a level, runs a simple bot and logs what happens. */
public class Sim {
    public static void main(String[] a) throws Exception {
        int lv = Integer.parseInt(a[0]);
        int ticks = Integer.parseInt(a[1]);
        String mode = a.length > 2 ? a[2] : "idle";
        E.load();
        W.initColors();
        W.skill = 1;
        W.health = 100; W.weapons = 31; W.weapon = 1; W.ammo[0] = 200; W.ammo[1] = 50; W.ammo[2] = 30;
        W.load(lv);
        if (a.length > 4) { W.px = (int) (Double.parseDouble(a[3]) * 65536); W.py = (int) (Double.parseDouble(a[4]) * 65536); }
        W.god = mode.indexOf("god") >= 0;
        int mons = 0;
        for (int i = 0; i < W.nt; i++) if ((W.tfl[W.tType[i]] & W.TF_MON) != 0) mons++;
        System.out.println("level " + lv + " " + W.lvName + " things=" + W.nt + " monsters=" + mons + " player=" + (W.px / 65536.0) + "," + (W.py / 65536.0));
        for (int t = 0; t < ticks; t++) {
            // bot: turn toward the nearest awake monster with LOS and fire
            if (mode.indexOf("fight") >= 0) {
                int best = -1, bd = Integer.MAX_VALUE;
                for (int i = 0; i < W.nt; i++) {
                    if ((W.tfl[W.tType[i]] & W.TF_MON) == 0 || W.tSt[i] >= W.ST_DIE) continue;
                    int d = E.dist(W.tX[i] - W.px, W.tY[i] - W.py);
                    if (d < bd && W.losCells(W.px, W.py, W.tX[i], W.tY[i], true)) { bd = d; best = i; }
                }
                W.kFire = false; W.kLeft = W.kRight = false;
                if (best >= 0 && bd < (16 << 16)) {
                    int ang = E.atan2(W.tY[best] - W.py, W.tX[best] - W.px);
                    int diff = (ang - W.pa) & 4095; if (diff > 2048) diff -= 4096;
                    if (diff > 40) W.kRight = true; else if (diff < -40) W.kLeft = true; else W.kFire = true;
                }
            }
            W.tick();
            if (t % 40 == 0 || G.died || G.won) {
                StringBuffer sb = new StringBuffer("t=" + t + " hp=" + W.health + " kills=" + W.kills + "/" + W.totalKills);
                for (int i = 0; i < W.nt; i++) {
                    int ty = W.tType[i];
                    if ((W.tfl[ty] & W.TF_MON) != 0 && (ty == W.BOSS || mode.indexOf("all") >= 0))
                        sb.append(" | " + ty + "@" + (W.tX[i] >> 16) + "," + (W.tY[i] >> 16) + " st" + W.tSt[i] + " hp" + W.tHp[i]);
                }
                System.out.println(sb);
            }
            if (G.died || G.won) break;
        }
    }
}
