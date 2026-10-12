/**
 * Rooms with monsters but no loot. A room is a group of open cells bounded by walls and doors.
 * Usage: Rooms [raw]   (raw: before the difficulty thinning)
 */
public class Rooms {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true;
        boolean raw = a.length > 0 && (a[0].equals("raw") || a[0].equals("need"));
        if (a.length > 0 && a[0].equals("need")) { need(); return; }
        if (raw) for (int k = 0; k < 3; k++) { W.SK_KEEP[k] = 100; W.SK_KEEP_AMMO[k] = 100; }
        int bad = 0, badMon = 0;
        for (int lv = 1; lv <= 20; lv++) {
            for (int sk = 0; sk < 3; sk++) {
                W.skill = sk; W.load(lv);
                int[] reg = regions();
                int nr = 0;
                for (int c = 0; c < 4096; c++) if (reg[c] + 1 > nr) nr = reg[c] + 1;
                int[] cells = new int[nr], mon = new int[nr], hp = new int[nr], am = new int[nr];
                int[] cx = new int[nr], cy = new int[nr];
                for (int c = 0; c < 4096; c++) if (reg[c] >= 0) { cells[reg[c]]++; cx[reg[c]] += c & 63; cy[reg[c]] += c >> 6; }
                for (int i = 0; i < W.nt; i++) {
                    int t = W.tType[i];
                    int c = ((W.tY[i] >> 16) << 6) | (W.tX[i] >> 16);
                    int r = reg[c];
                    if (r < 0) continue;
                    if (W.isMon(t) && !W.isBoss(t)) mon[r]++;
                    else if (t == W.CANDY || t == W.BUCKET || t == W.BREW || t == W.ARMOR) hp[r]++;
                    else if (t == W.BULLETS || t == W.SHELLS || t == W.PUMPKINS || t == W.SHOTGUN || t == W.TOMMY || t == W.LAUNCHER) am[r]++;
                }
                StringBuffer sb = new StringBuffer();
                for (int r = 0; r < nr; r++) {
                    if (mon[r] >= 2 && hp[r] + am[r] == 0 && cells[r] >= 6) {
                        sb.append("  [" + cx[r] / cells[r] + "," + cy[r] / cells[r] + " " + cells[r] + " cells, " + mon[r] + " mon]");
                        bad++; badMon += mon[r];
                    }
                }
                if (sb.length() > 0) System.out.println("L" + lv + " sk" + sk + ":" + sb);
            }
        }
        System.out.println("empty rooms with monsters: " + bad + " (" + badMon + " monsters)");
    }

    /** Per level (normal skill, before thinning): rooms whose monsters outweigh their ammo, with a free cell for more. */
    static void need() throws Exception {
        for (int k = 0; k < 3; k++) { W.SK_KEEP[k] = 100; W.SK_KEEP_AMMO[k] = 100; }
        for (int lv = 1; lv <= 20; lv++) {
            W.skill = 1; W.load(lv);
            int[] reg = regions();
            int nr = 0;
            for (int c = 0; c < 4096; c++) if (reg[c] + 1 > nr) nr = reg[c] + 1;
            long[] hp = new long[nr], dmg = new long[nr];
            int[] cnt = new int[nr], cx = new int[nr], cy = new int[nr];
            boolean[] used = new boolean[4096];
            for (int c = 0; c < 4096; c++) if (reg[c] >= 0) { cnt[reg[c]]++; cx[reg[c]] += c & 63; cy[reg[c]] += c >> 6; }
            for (int i = 0; i < W.nt; i++) {
                int t = W.tType[i];
                int c = ((W.tY[i] >> 16) << 6) | (W.tX[i] >> 16);
                used[c] = true;
                int r = reg[c];
                if (r < 0) continue;
                if (W.isMon(t) && !W.isBoss(t)) hp[r] += W.tHp[i];
                else if (t == W.BULLETS) dmg[r] += 480; else if (t == W.SHELLS) dmg[r] += 400; else if (t == W.PUMPKINS) dmg[r] += 400;
                else if (t == W.SHOTGUN) dmg[r] += 500; else if (t == W.TOMMY) dmg[r] += 700; else if (t == W.LAUNCHER) dmg[r] += 600;
            }
            StringBuffer sb = new StringBuffer();
            for (int r = 0; r < nr; r++) {
                if (hp[r] < 150 || dmg[r] * 10 >= hp[r] * 18) continue;
                // free cell nearest the room's middle, not next to a wall, not on a hazard
                int mx = cx[r] / cnt[r], my = cy[r] / cnt[r], best = -1, bd = 1 << 30;
                for (int c = 0; c < 4096; c++) {
                    if (reg[c] != r || used[c] || (W.flag[c] & (W.F_HURT | W.F_SECRET)) != 0) continue;
                    int x = c & 63, y = c >> 6;
                    if (x < 1 || y < 1 || x > 62 || y > 62 || W.wall[c - 1] != 0 || W.wall[c + 1] != 0 || W.wall[c - 64] != 0 || W.wall[c + 64] != 0) continue;
                    int d = (x - mx) * (x - mx) + (y - my) * (y - my);
                    if (d < bd) { bd = d; best = c; }
                }
                sb.append("  [room@" + mx + "," + my + " hp " + hp[r] + " ammo " + dmg[r] + (best >= 0 ? " free " + (best & 63) + "," + (best >> 6) : "") + "]");
            }
            if (sb.length() > 0) System.out.println("L" + lv + ":" + sb);
        }
    }

    static int[] regions() {
        int[] reg = new int[4096];
        for (int c = 0; c < 4096; c++) reg[c] = -1;
        int[] st = new int[4096];
        int n = 0;
        for (int c = 0; c < 4096; c++) {
            if (reg[c] >= 0 || !open(c)) continue;
            int sp = 0;
            st[sp++] = c;
            reg[c] = n;
            while (sp > 0) {
                int k = st[--sp];
                int x = k & 63, y = k >> 6;
                int[] nb = {x > 0 ? k - 1 : -1, x < 63 ? k + 1 : -1, y > 0 ? k - 64 : -1, y < 63 ? k + 64 : -1};
                for (int j = 0; j < 4; j++) {
                    int m = nb[j];
                    if (m >= 0 && reg[m] < 0 && open(m)) { reg[m] = n; st[sp++] = m; }
                }
            }
            n++;
        }
        return reg;
    }

    static boolean open(int c) {
        return W.wall[c] == 0 && (W.flag[c] & W.F_DOOR) == 0;
    }
}
