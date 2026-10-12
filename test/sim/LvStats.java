/** Monsters per level and difficulty as the game really places them (after the easy-mode cull), plus ambushers. */
public class LvStats {
    static final String[] NM = {"", "ghoul", "scarecrow", "wraith", "witch", "PUMPKIN KING", "skeleton", "clown", "werewolf", "bat", "bride",
            "GIGGLES", "COUNT", "frankenbot", "drone", "cyberghoul", "spider", "PRIME", "mummy", "jaguar", "conquistador", "weeper", "SEVEN"};
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true;
        for (int lv = 1; lv <= 20; lv++) {
            StringBuffer sb = new StringBuffer("L" + lv);
            for (int sk = 0; sk < 3; sk++) {
                W.skill = sk;
                W.load(lv);
                int[] c = new int[W.NMON];
                for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) c[W.tType[i]]++;
                int amb = W.nPend;
                for (int k = 0; k < W.nPend; k++) c[W.pendT[k]]++;
                sb.append(" | sk" + sk + " total " + W.totalKills + (amb > 0 ? " (ambush " + amb + ")" : "") + " secrets " + W.totalSecrets + ":");
                for (int t = 1; t < W.NMON; t++) if (c[t] > 0) sb.append(" " + NM[t] + "=" + c[t]);
            }
            System.out.println(sb);
        }
    }
}
