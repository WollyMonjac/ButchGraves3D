/** Count health/ammo pickups per level and skill after the difficulty thinning. */
public class Count {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true;
        for (int lv = 1; lv <= 16; lv++) {
            StringBuffer sb = new StringBuffer("L" + lv);
            for (int sk = 0; sk < 3; sk++) {
                W.skill = sk; W.load(lv);
                int hp = 0, am = 0, mon = 0;
                for (int i = 0; i < W.nt; i++) {
                    int t = W.tType[i];
                    if (t == W.CANDY) hp += 10; else if (t == W.BUCKET) hp += 30; else if (t == W.BREW) hp += 100;
                    else if (t == W.BULLETS || t == W.SHELLS || t == W.PUMPKINS) am++;
                    else if (W.isMon(t)) mon++;
                }
                sb.append("  sk" + sk + ": mon " + mon + " hp " + hp + " ammo " + am);
            }
            System.out.println(sb);
        }
    }
}
