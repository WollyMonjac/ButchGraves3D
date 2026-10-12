/** Crash/behaviour sweep: every level, a god-mode bot that hunts monsters for N ticks; reports kills, exceptions,
 *  damage the bot would have taken per monster type, and the asset memory resident for that level. */
public class Sweep {
    public static void main(String[] a) throws Exception {
        int ticks = Integer.parseInt(a[0]);
        E.load(); W.initColors(); G.quiet = true;
        int lv0 = a.length > 1 ? Integer.parseInt(a[1]) : 1, lv1 = a.length > 2 ? Integer.parseInt(a[2]) : 16;
        for (int lv = lv0; lv <= lv1; lv++) {
            for (int sk = 0; sk < 3; sk++) {
                W.skill = sk; W.health = 100; W.armor = 0; W.weapons = 31; W.weapon = 3; W.ammo[0] = 200; W.ammo[1] = 50; W.ammo[2] = 30;
                W.load(lv);
                java.util.Arrays.fill(W.dmgLog, 0);
                W.god = false;
                int mons = W.totalKills;
                String err = "";
                try {
                    for (int t = 0; t < ticks; t++) {
                        BossBot.R = new java.util.Random(t);
                        BossBot.bot(t);
                        W.health = 100;     // immortal but damage is still logged
                        W.dead = false;
                        W.tick();
                    }
                } catch (Throwable e) { err = " EXCEPTION " + e; e.printStackTrace(); }
                long mem = 0;
                for (int i = 0; i < E.tex.length; i++) if (E.tex[i] != null) mem += E.tex[i].length;
                for (int i = 0; i < E.spr.length; i++) if (E.spr[i] != null) mem += E.spr[i].length;
                StringBuffer dl = new StringBuffer();
                for (int k = 0; k < W.NTYPE; k++) if (W.dmgLog[k] > 0) dl.append(k).append(':').append(W.dmgLog[k]).append(' ');
                System.out.println("L" + lv + " sk" + sk + " monsters " + mons + " killed " + W.kills + " art " + (mem / 1024) + "KB dmg " + dl + err);
            }
        }
    }
}
