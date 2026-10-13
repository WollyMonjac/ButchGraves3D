import java.util.*;
import javax.microedition.media.FakePlayer;
import javax.microedition.media.Manager;

/**
 * Busy fire fight against Snd with a fake phone audio system: counts how many gunshots are heard.
 * Usage: GunTest MODEL   (letters: N healthy, R restart race, M one channel, C resource limit, S slow loading)
 */
public class GunTest {
    public static void main(String[] a) throws Exception {
        String model = a[0];
        FakePlayer.modelC = model.indexOf('C') >= 0;
        FakePlayer.modelR = model.indexOf('R') >= 0;
        FakePlayer.modelM = model.indexOf('M') >= 0;
        FakePlayer.modelX = model.indexOf('X') >= 0;
        FakePlayer.modelY = model.indexOf('Y') >= 0;
        FakePlayer.modelZ = model.indexOf('Z') >= 0;
        FakePlayer.modelP = model.indexOf('P') >= 0;
        FakePlayer.modelO = model.indexOf('O') >= 0;
        FakePlayer.modelT = model.indexOf('T') >= 0;
        FakePlayer.modelU = model.indexOf('U') >= 0;
        FakePlayer.modelQ = model.indexOf('Q') >= 0;
        FakePlayer.modelD = model.indexOf('D') >= 0;
        FakePlayer.modelL = model.indexOf('L') >= 0;
        FakePlayer.modelA = model.indexOf('A') >= 0;
        Snd.fxTurns = System.getProperty("turns") != null;
        if (model.indexOf('S') >= 0) Manager.createDelayWav = 150;
        Random r = new Random(7);
        java.lang.reflect.Method wm = null;
        try { wm = Snd.class.getDeclaredMethod("weapon", new Class[]{int.class}); wm.setAccessible(true); } catch (Exception e) { }
        Snd.init();
        // (K: the player chose music by hand - no longer different: the engine never turns music off itself)
        Snd.music(Snd.M_L1);
        Thread.sleep(400);
        long m0 = FakePlayer.musicMs(), w0 = System.currentTimeMillis();
        int[] guns = {Snd.REVOLVER, Snd.SHOTGUN, Snd.TOMMY};
        int[] every = {7, 22, 3};
        int[] mon = {Snd.ZOMBIE, Snd.SCARE, Snd.WITCH, Snd.CLOWN, Snd.SKEL, Snd.GHOST, Snd.WOLF, Snd.BAT};
        int[] asked = new int[3];
        String[] names = {"s_revolver", "s_shotgun", "s_tommy"};
        for (int g = 0; g < 3; g++) {
            if (wm != null) wm.invoke(null, new Object[]{new Integer(guns[g])});
            if (g > 0) { Snd.newLevel(); Snd.music(Snd.M_L1 + g); }   // next level: new track
            for (int tick = 0; tick < 200; tick++) {
                if (tick % every[g] == 0) {
                    asked[g]++;
                    Snd.sfx(guns[g]);
                    if (r.nextInt(2) == 0) Snd.sfx(Snd.HIT);
                }
                if (r.nextInt(25) == 0) Snd.sfx(mon[r.nextInt(mon.length)]);
                if (r.nextInt(40) == 0) Snd.sfx(Snd.MDIE);
                if (r.nextInt(30) == 0) Snd.sfx(Snd.FIREBALL);
                if (r.nextInt(35) == 0) Snd.sfx(Snd.KNIFE);
                if (r.nextInt(45) == 0) Snd.sfx(Snd.HURT);
                if (r.nextInt(80) == 0) Snd.sfx(Snd.PICKUP);
                if (r.nextInt(100) == 0) Snd.sfx(Snd.EXPLODE);
                if (r.nextInt(120) == 0) Snd.voice(Snd.V_KILL1 + r.nextInt(3));
                Snd.poll();
                Thread.sleep(50);              // the game ticks 20 times a second
            }
        }
        long mus = (FakePlayer.musicMs() - m0) * 100 / (System.currentTimeMillis() - w0);
        Thread.sleep(500);
        int[] heard = new int[3];
        int lost = 0, busy = 0, other = 0;
        List<String> log = new ArrayList<String>(FakePlayer.log);
        for (String s : log) {
            String[] f = s.split(" ");
            if (f.length < 3) continue;
            if (f[1].equals("START-LOST")) lost++;
            if (f[1].equals("START-BUSY")) busy++;
            if (!f[1].equals("START")) continue;
            boolean gun = false;
            for (int g = 0; g < 3; g++) if (f[2].startsWith(names[g])) { heard[g]++; gun = true; }
            if (!gun && f[2].startsWith("s_")) other++;
        }
        System.out.print("model " + pad(model, 3) + " heard: ");
        int ta = 0, th = 0;
        for (int g = 0; g < 3; g++) {
            System.out.print(names[g].substring(2) + " " + heard[g] + "/" + asked[g] + "  ");
            ta += asked[g]; th += heard[g];
        }
        int nomix = 0;
        for (String q : log) if (q.indexOf("START-NOMIX") >= 0) nomix++;
        System.out.println(" total " + (100 * th / ta) + "%  MUSIC " + mus + "%" + turnsInfo() + "   other effects " + other + "   lost starts " + lost + "  busy " + busy
                + (nomix > 0 ? "  no-mix failures " + nomix : "") + "  music mode " + Snd.musicMode + (Snd.note != null ? " (note: " + Snd.note + ")" : "") + " restarts " + Snd.restarts + (Snd.musicDead ? " musicDead" : "") + (Snd.sampledDead ? " sampledDead" : ""));
        java.io.PrintWriter pw = new java.io.PrintWriter("log_gun_" + model + ".txt");
        for (String s : log) pw.println(s);
        pw.close();
        System.exit(0);
    }

    static String turnsInfo() {
        return (Snd.turns() ? (Snd.autoTurns ? "  AUTO-TURNS" : "  TURNS") + " pauses " + Snd.musicPauses : "")
                + (FakePlayer.resumes + FakePlayer.topStarts > 0 ? "  resumed " + FakePlayer.resumes + " fromTop " + FakePlayer.topStarts : "")
                + (FakePlayer.seeks > 0 ? " seeks " + FakePlayer.seeks : "") + (Snd.deep ? " DEEP" : "")
                + "  music stretches " + FakePlayer.segs + " (" + FakePlayer.shortSegs + " under 1 s)";
    }

    static String pad(String s, int n) { while (s.length() < n) s += " "; return s; }
}
