import java.util.*;
import javax.microedition.media.FakePlayer;
import javax.microedition.media.Manager;

/**
 * A minute of boss fight against Snd with a fake phone audio system: the tommy gun hammering, the boss's attacks, voice
 * and summons, explosions, Butch getting hit (and grunting), pickups coming back. Counts what was heard, how many sampled
 * players had to be created (the churn that hangs real phones) and what the engine had to give up.
 * Usage: BossTest MODEL  (letters as in GunTest)
 */
public class BossTest {
    public static void main(String[] a) throws Exception {
        String model = a[0];
        FakePlayer.modelC = model.indexOf('C') >= 0;
        FakePlayer.modelR = model.indexOf('R') >= 0;
        FakePlayer.modelM = model.indexOf('M') >= 0;
        FakePlayer.modelX = model.indexOf('X') >= 0;
        FakePlayer.modelY = model.indexOf('Y') >= 0;
        FakePlayer.modelZ = model.indexOf('Z') >= 0;
        FakePlayer.modelP = model.indexOf('P') >= 0;
        FakePlayer.modelQ = model.indexOf('Q') >= 0;
        FakePlayer.modelL = model.indexOf('L') >= 0;
        FakePlayer.modelD = model.indexOf('D') >= 0;
        FakePlayer.modelA = model.indexOf('A') >= 0;
        if (model.indexOf('S') >= 0) Manager.createDelayWav = 150;
        Random r = new Random(11);
        Snd.init();
        // (K: the player chose music by hand - no longer different: the engine never turns music off itself)
        Snd.weapon(Snd.TOMMY);
        Snd.newLevel();
        Snd.music(Snd.M_L13 + 3);
        Thread.sleep(400);
        int asked = 0, painAsked = 0;
        int[] bossSnd = {Snd.FIREBALL, Snd.KNIFE, Snd.ZAPS, Snd.STOMP, Snd.SEVEN, Snd.BOSS, Snd.GIGGLE, Snd.COUNT};
        int[] mon = {Snd.ZOMBIE, Snd.MUMMY, Snd.ROAR, Snd.SKEL, Snd.BAT, Snd.WOLF, Snd.SKITTER, Snd.ROBOT};
        int lastPain = -1000;
        long m0 = FakePlayer.musicMs(), w0 = System.currentTimeMillis();
        for (int tick = 0; tick < 1200; tick++) {
            boolean firing = (tick / 60) % 3 != 2;                 // bursts of fire, short pauses
            if (firing && tick % 3 == 0) { asked++; W.ticks = tick; Snd.sfx(Snd.TOMMY); if (r.nextInt(3) == 0) Snd.sfx(Snd.HIT); }
            if (tick % 30 == 0) Snd.sfx(bossSnd[r.nextInt(bossSnd.length)]);
            if (r.nextInt(40) == 0) Snd.sfx(mon[r.nextInt(mon.length)]);
            if (r.nextInt(60) == 0) Snd.sfx(Snd.MDIE);
            if (r.nextInt(70) == 0) Snd.sfx(Snd.EXPLODE);
            if (r.nextInt(25) == 0) {                              // Butch gets hit
                Snd.sfx(Snd.HURT);
                if (r.nextInt(3) == 0 && W.painOk(tick)) { painAsked++; Snd.voice(r.nextInt(2) == 0 ? Snd.V_PAIN1 : Snd.V_PAIN2); }
            }
            if (r.nextInt(150) == 0) Snd.sfx(Snd.SECRET);           // supplies coming back
            if (r.nextInt(90) == 0) Snd.sfx(Snd.PICKUP);
            if (r.nextInt(300) == 0) Snd.voice(Snd.V_KILL1 + r.nextInt(3));
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
            if (f[2].startsWith("s_tommy")) heard++;
            else if (f[2].startsWith("s_")) other++;
            else if (f[2].startsWith("v_")) voices++;
        }
        System.out.println("model " + pad(model, 3) + " MUSIC " + mus + "%  tommy " + heard + "/" + asked + " (" + (100 * heard / asked) + "%)  other effects " + other
                + "  voices " + voices + "/" + painAsked + "+  wav players created " + Manager.wavCreates + "  hangs " + hangs
                + "  music mode " + Snd.musicMode + (Snd.note != null ? " (" + Snd.note + ")" : "") + (Snd.musicDead ? " musicDead" : "")
                + (Snd.sampledDead ? " sampledDead" : "") + " restarts " + Snd.restarts
                + (FakePlayer.steals > 0 ? " stolen " + FakePlayer.steals : "") + (FakePlayer.loopEnds > 0 ? " loopEnds " + FakePlayer.loopEnds : ""));
        System.exit(0);
    }

    static String pad(String s, int n) { while (s.length() < n) s += " "; return s; }
}
