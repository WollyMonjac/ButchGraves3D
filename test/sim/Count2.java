/** Ammo damage potential vs. monster health per level and skill (bosses and their respawning arenas excluded). */
public class Count2 {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true;
        double[] tot = new double[3], totHp = new double[3];
        for (int lv = 1; lv <= 20; lv++) {
            StringBuffer sb = new StringBuffer("L" + lv);
            for (int sk = 0; sk < 3; sk++) {
                W.skill = sk; W.load(lv);
                long mhp = 0, dmg = 0, heal = 0;
                for (int i = 0; i < W.nt; i++) {
                    int t = W.tType[i];
                    int am = W.SK_AMMO[sk];
                    if (W.isMon(t) && !W.isBoss(t)) mhp += W.tHp[i];
                    else if (t == W.BULLETS) dmg += 24 * am / 100 * 20;
                    else if (t == W.SHELLS) dmg += 8 * am / 100 * 50;
                    else if (t == W.PUMPKINS) dmg += 4 * am / 100 * 100;
                    else if (t == W.SHOTGUN) dmg += 10 * 50;
                    else if (t == W.TOMMY) dmg += 50 * 14;
                    else if (t == W.LAUNCHER) dmg += 6 * 100;
                    else if (t == W.CANDY) heal += 10; else if (t == W.BUCKET) heal += 30; else if (t == W.BREW) heal += 100;
                }
                for (int k = 0; k < W.nPend; k++) mhp += W.M_HP[W.pendT[k]] * W.SK_HP[sk] / 100;      // ambushers
                double r = mhp == 0 ? 0 : (double) dmg / mhp;
                tot[sk] += dmg; totHp[sk] += mhp;
                sb.append(String.format("   sk%d ammo/hp %.2f  heal %4d", sk, r, heal * 100 / W.SK_DMG[sk]));
            }
            System.out.println(sb);
        }
        for (int sk = 0; sk < 3; sk++) System.out.println(String.format("skill %d: ammo damage / monster hp = %.2f", sk, tot[sk] / totHp[sk]));
    }
}
