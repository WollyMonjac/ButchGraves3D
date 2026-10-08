import java.lang.reflect.Method;
import java.util.*;
import javax.microedition.media.FakePlayer;

/**
 * Plays a scripted game session against Snd with a fake phone audio system:
 * title -> level 1 -> 5 s of combat -> death -> 3 s on the death screen -> restart -> combat.
 * Usage: SndTest MODEL   (MODEL: N = healthy phone, A = mixer deadlock, B = random hang, C = resource limit)
 */
public class SndTest {
    public static void main(String[] a) throws Exception {
        String model = a[0];
        FakePlayer.modelA = model.indexOf('A') >= 0;
        FakePlayer.modelC = model.indexOf('C') >= 0;
        if (model.indexOf('B') >= 0) FakePlayer.hangStartAt = 20;
        Method poll = find("poll"), newLevel = find("newLevel");
        boolean fixed = poll != null;
        Snd.init();
        Snd.music(Snd.M_TITLE);
        long deathAt = 0, restartAt = 0;
        for (int tick = 0; tick < 300; tick++) {
            if (tick == 20) Snd.music(Snd.M_L1);
            if (tick == 30) Snd.voice(Snd.V_START1);
            boolean combat = (tick > 30 && tick < 160) || tick > 225;
            if (combat) {
                if (tick % 3 == 0) Snd.sfx(Snd.TOMMY);
                if (tick % 5 == 0) Snd.sfx(Snd.HIT);
                if (tick % 7 == 0) Snd.sfx(Snd.ZOMBIE);
                if (tick % 9 == 0) Snd.sfx(Snd.HURT);
                if (tick % 11 == 0) Snd.sfx(Snd.FIREBALL);
                if (tick % 13 == 0) Snd.sfx(Snd.MDIE);
                if (tick % 27 == 0) Snd.voice(Snd.V_PAIN1);
            }
            if (tick == 160) {                       // the player dies (same call order as the game)
                deathAt = FakePlayer.now();
                FakePlayer.log.add(deathAt + " ======== DEATH");
                if (fixed) { Snd.music(Snd.M_DEAD); Snd.voice(Snd.V_DIE); }
                else { Snd.voice(Snd.V_DIE); Snd.music(Snd.M_DEAD); }
            }
            if (tick > 160 && tick < 220 && tick % 7 == 0) Snd.sfx(Snd.ZOMBIE);   // monsters still growling
            if (tick == 220) {                       // press 5: restart the level
                restartAt = FakePlayer.now();
                FakePlayer.log.add(restartAt + " ======== RESTART");
                if (newLevel != null) newLevel.invoke(null);
                Snd.music(Snd.M_L1);
            }
            if (poll != null) poll.invoke(null);     // the game loop calls this every frame
            Thread.sleep(50);
        }
        Thread.sleep(300);

        List<String> log = new ArrayList<String>(FakePlayer.log);
        long deadStart = -1, levelStop = -1, levelRestart = -1, dieVoice = -1;
        int sfxAfterRestart = 0, sfxBeforeDeath = 0;
        for (String s : log) {
            String[] f = s.split(" ");
            long t = Long.parseLong(f[0]);
            if (f.length < 3) continue;
            String ev = f[1], n = f[2];
            if (t >= deathAt && t < restartAt) {
                if (ev.equals("START") && n.equals("m_dead.mid") && deadStart < 0) deadStart = t - deathAt;
                if ((ev.equals("STOP") || ev.equals("CLOSE")) && n.equals("m_level1.mid") && levelStop < 0) levelStop = t - deathAt;
                if (ev.equals("START") && n.equals("v_die.wav") && dieVoice < 0) dieVoice = t - deathAt;
            }
            if (t >= restartAt) {
                if (ev.equals("START") && n.equals("m_level1.mid") && levelRestart < 0) levelRestart = t - restartAt;
                if (ev.equals("START") && n.startsWith("s_")) sfxAfterRestart++;
            }
            if (t < deathAt && ev.equals("START") && n.startsWith("s_")) sfxBeforeDeath++;
        }
        System.out.println("model " + model + " / " + (fixed ? "NEW Snd" : "OLD Snd"));
        System.out.println("  sound effects played before death:      " + sfxBeforeDeath);
        System.out.println("  level music stopped after death:        " + ms(levelStop));
        System.out.println("  death scream started:                   " + ms(dieVoice));
        System.out.println("  death music started:                    " + ms(deadStart));
        System.out.println("  level music restarted after restart:    " + ms(levelRestart));
        System.out.println("  sound effects played after restart:     " + sfxAfterRestart);
        boolean ok = levelStop >= 0 && levelStop < 1500 && deadStart >= 0 && deadStart < 1500 && dieVoice >= 0
                && levelRestart >= 0 && levelRestart < 1500 && sfxAfterRestart >= 20;
        System.out.println("  RESULT: " + (ok ? "PASS" : "FAIL"));
        java.io.PrintWriter pw = new java.io.PrintWriter("log_" + model + "_" + (fixed ? "new" : "old") + ".txt");
        for (String s : log) pw.println(s);
        pw.close();
        System.exit(0);
    }

    static String ms(long v) { return v < 0 ? "NEVER" : "after " + v + " ms"; }

    static Method find(String n) {
        try { Method m = Snd.class.getDeclaredMethod(n); m.setAccessible(true); return m; } catch (Exception e) { return null; }
    }
}
