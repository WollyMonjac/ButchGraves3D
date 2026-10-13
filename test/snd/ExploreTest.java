import java.util.*;
import javax.microedition.media.FakePlayer;
import javax.microedition.media.Manager;

/**
 * A minute of an ordinary level against Snd with a fake phone audio system: walking about with a growl now and then, a
 * pickup, a door or a lever, a short fight every quarter of a minute, a voice line. The counterpart of BossTest for
 * effects and music taking turns: here the music should play most of the time, in long stretches.
 * Usage: ExploreTest MODEL  (letters as in BossTest; -Dturns: the player chose TAKE TURNS)
 */
public class ExploreTest {
    public static void main(String[] a) throws Exception {
        String model = a[0];
        FakePlayer.modelC = model.indexOf('C') >= 0;
        FakePlayer.modelR = model.indexOf('R') >= 0;
        FakePlayer.modelM = model.indexOf('M') >= 0;
        FakePlayer.modelX = model.indexOf('X') >= 0;
        FakePlayer.modelY = model.indexOf('Y') >= 0;
        FakePlayer.modelQ = model.indexOf('Q') >= 0;
        FakePlayer.modelD = model.indexOf('D') >= 0;
        FakePlayer.modelA = model.indexOf('A') >= 0;
        FakePlayer.modelO = model.indexOf('O') >= 0;
        FakePlayer.modelT = model.indexOf('T') >= 0;
        FakePlayer.modelU = model.indexOf('U') >= 0;
        Snd.fxTurns = System.getProperty("turns") != null;
        Random r = new Random(5);
        Snd.init();
        Snd.weapon(Snd.REVOLVER);
        Snd.newLevel();
        Snd.music(Snd.M_L1);
        Thread.sleep(400);
        int asked = 0;
        int[] mon = {Snd.ZOMBIE, Snd.SKEL, Snd.WITCH, Snd.GHOST, Snd.WOLF, Snd.BAT};
        long m0 = FakePlayer.musicMs(), w0 = System.currentTimeMillis();
        for (int tick = 0; tick < 1200; tick++) {
            int ph = tick % 300;
            boolean fight = ph >= 200 && ph < 260;               // 3 s of fighting every 15 s
            if (fight) {
                if (ph % 7 == 0) { asked++; Snd.sfx(Snd.REVOLVER); if (r.nextInt(2) == 0) Snd.sfx(Snd.HIT); }
                if (ph == 245) Snd.sfx(Snd.MDIE);
                if (r.nextInt(30) == 0) Snd.sfx(Snd.HURT);
                if (r.nextInt(20) == 0) Snd.sfx(mon[r.nextInt(mon.length)]);
            } else {
                if (r.nextInt(100) == 0) Snd.sfx(mon[r.nextInt(mon.length)]);   // something growls somewhere
                if (r.nextInt(120) == 0) Snd.sfx(Snd.PICKUP);
                if (r.nextInt(250) == 0) Snd.sfx(Snd.DOOR);
            }
            if (ph == 262) Snd.voice(Snd.V_KILL1 + r.nextInt(3));
            Snd.poll();
            Thread.sleep(50);
        }
        long mus = (FakePlayer.musicMs() - m0) * 100 / (System.currentTimeMillis() - w0);
        Thread.sleep(500);
        int heard = 0, other = 0, voices = 0, hangs = 0;
        List<String> log = new ArrayList<String>(FakePlayer.log);
        for (String s : log) {
            String[] f = s.split(" ");
            if (f.length < 3) continue;
            if (f[1].startsWith("HANG")) hangs++;
            if (!f[1].equals("START")) continue;
            if (f[2].startsWith("s_revolver")) heard++;
            else if (f[2].startsWith("s_")) other++;
            else if (f[2].startsWith("v_")) voices++;
        }
        System.out.println("model " + BossTest.pad(model, 3) + " MUSIC " + mus + "%" + BossTest.turnsInfo() + "  revolver " + heard + "/" + asked
                + "  other effects " + other + "  voices " + voices + "  hangs " + hangs + (Snd.note != null ? " (" + Snd.note + ")" : "")
                + (FakePlayer.steals > 0 ? " stolen " + FakePlayer.steals : ""));
        if (System.getProperty("dump") != null) {
            java.io.PrintWriter pw = new java.io.PrintWriter("log_explore_" + model + ".txt");
            for (String s : log) pw.println(s);
            pw.close();
        }
        System.exit(0);
    }
}
