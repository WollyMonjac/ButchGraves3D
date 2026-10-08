import java.io.InputStream;
import java.util.Hashtable;
import javax.microedition.media.Manager;
import javax.microedition.media.Player;

/**
 * Sound manager. All MMAPI work happens on a background worker so a slow phone never stalls the
 * renderer. File names come from /snd/sounds.txt inside the JAR (editable).
 *
 * Phone audio firmware is fragile, so the worker is defensive:
 *  - every sampled sound (effects, voice) is stopped and closed BEFORE the MIDI music is stopped or
 *    switched: on many phones stopping a MIDI while a WAV plays deadlocks the audio system forever;
 *  - a watchdog (poll(), called every frame) replaces a worker stuck in one call for too long and
 *    closes each of the stuck worker's players on its own throw-away thread;
 *  - repeated failures mute effects for a few seconds instead of forever;
 *  - stale effects are dropped instead of piling up, music/stop commands are never dropped;
 *  - no Player method is ever called from a PlayerListener callback (no listeners at all).
 */
final class Snd implements Runnable {
    // ---------------- sound effect ids (order matches SFX keys)
    static final int REVOLVER = 0, SHOTGUN = 1, RELOAD = 2, TOMMY = 3, LAUNCH = 4, EXPLODE = 5, SWING = 6, HIT = 7, DOOR = 8,
            PICKUP = 9, WPICK = 10, KEY = 11, HURT = 12, FIREBALL = 13, MDIE = 14, THUNDER = 15, CLICK = 16, SWITCH = 17,
            SECRET = 18, ZOMBIE = 19, SCARE = 20, WITCH = 21, GHOST = 22, BOSS = 23, BOSSDIE = 24, NSFX = 25;
    static final String[] SFXKEY = {"revolver", "shotgun", "reload", "tommy", "launch", "explode", "swing", "hit", "door",
            "pickup", "wpick", "key", "hurt", "fireball", "mdie", "thunder", "click", "switch", "secret", "zombie", "scare",
            "witch", "ghost", "boss", "bossdie"};
    // ---------------- voice lines
    static final int V_START1 = 0, V_START2 = 1, V_KILL1 = 2, V_KILL2 = 3, V_KILL3 = 4, V_GHOST = 5, V_PUMPKIN = 6, V_SHOVEL = 7,
            V_GIB = 8, V_WEAPON = 9, V_LAUNCHER = 10, V_HEALTH = 11, V_LOWHP = 12, V_SECRET = 13, V_BOSS = 14, V_WIN = 15,
            V_LEVEL = 16, V_PAIN1 = 17, V_PAIN2 = 18, V_DIE = 19, NVOICE = 20;
    static final String[] VKEY = {"start1", "start2", "kill1", "kill2", "kill3", "ghost", "pumpkin", "shovel", "gib", "weapon",
            "launcher", "health", "lowhp", "secret", "boss", "win", "level", "pain1", "pain2", "die"};
    // ---------------- music
    static final int M_TITLE = 0, M_STORY = 1, M_L1 = 2, M_WIN = 6, M_DEAD = 7, NMUS = 8;
    static final String[] MKEY = {"title", "story", "level1", "level2", "level3", "level4", "win", "dead"};

    static boolean musicOn = true, sfxOn = true, voiceOn = true;
    static boolean alive = true;
    static final String[] sfxPath = new String[NSFX], vPath = new String[NVOICE], mPath = new String[NMUS];
    static final long[] lastPlay = new long[NSFX];
    static int wantMusic = -1, fails, restarts;
    static long mutedUntil;              // effects/voice are skipped until then after repeated failures

    // ---------------- command queue: <1000 effect, 1000+ voice, 2001+ music, 3000 stop all
    static final int C_VOICE = 1000, C_MUSIC = 2000, C_STOP = 3000, QN = 32;
    static final int[] q = new int[QN];
    static final long[] qtime = new long[QN];
    static int qh, qt, gen;
    static long busyAt;                  // when the worker started its current command (0 = idle)
    static final Object lock = new Object();
    static Snd worker;

    // ---------------- per-worker state (a replaced worker keeps its own players)
    final int myGen;
    final Player victim;                 // non-null: this instance only closes one abandoned player
    final Player[] cache = new Player[NSFX];
    Player music, voiceP;
    int curMusic = -1, cached;
    boolean done;

    Snd(int g) { myGen = g; victim = null; }

    Snd(Player v) { myGen = -1; victim = v; }

    static void init() {
        Hashtable cfg = new Hashtable();
        try {
            InputStream in = G.open("/snd/sounds.txt");
            if (in != null) {
                byte[] buf = new byte[8192];
                int n = 0, r;
                while ((r = in.read(buf, n, buf.length - n)) > 0) n += r;
                in.close();
                String s = new String(buf, 0, n);
                int p = 0;
                while (p < s.length()) {
                    int e = s.indexOf('\n', p);
                    if (e < 0) e = s.length();
                    String line = s.substring(p, e).trim();
                    p = e + 1;
                    if (line.length() == 0 || line.charAt(0) == '#') continue;
                    int eq = line.indexOf('=');
                    if (eq < 0) continue;
                    cfg.put(line.substring(0, eq).trim(), line.substring(eq + 1).trim());
                }
            }
        } catch (Throwable t) { }
        for (int i = 0; i < NSFX; i++) sfxPath[i] = path(cfg, "sfx." + SFXKEY[i], "/snd/s_" + SFXKEY[i] + ".wav");
        for (int i = 0; i < NVOICE; i++) vPath[i] = path(cfg, "voice." + VKEY[i], "/snd/v_" + VKEY[i] + ".wav");
        String[] mdef = {"m_title", "m_story", "m_level1", "m_level2", "m_level3", "m_boss", "m_win", "m_dead"};
        for (int i = 0; i < NMUS; i++) mPath[i] = path(cfg, "music." + MKEY[i], "/snd/" + mdef[i] + ".mid");
        startWorker();
    }

    static void startWorker() {
        worker = new Snd(gen);
        new Thread(worker).start();
    }

    static String path(Hashtable cfg, String key, String def) {
        Object o = cfg.get(key);
        if (o == null) return cfg.isEmpty() ? def : null;
        String s = ((String) o).trim();
        if (s.length() == 0) return null;
        if (s.charAt(0) != '/') s = "/" + s;
        return s;
    }

    static String mime(String p) {
        String l = p.toLowerCase();
        if (l.endsWith(".mid") || l.endsWith(".midi")) return "audio/midi";
        if (l.endsWith(".amr")) return "audio/amr";
        if (l.endsWith(".mp3")) return "audio/mpeg";
        if (l.endsWith(".aac")) return "audio/aac";
        return "audio/x-wav";
    }

    // ---------------- public API (called from the game thread, never blocks)

    static void push(int cmd) {
        synchronized (lock) {
            int n = qt - qh;
            if (n < 0) n += QN;
            if (cmd < C_VOICE && n >= 4) return;        // effects backlog: a late bang is worse than none
            if (n >= QN - 1) qh = (qh + 1) % QN;        // full: drop the oldest command
            q[qt] = cmd;
            qtime[qt] = System.currentTimeMillis();
            qt = (qt + 1) % QN;
            lock.notifyAll();
        }
    }

    static void sfx(int id) {
        if (!sfxOn || sfxPath[id] == null) return;
        long now = System.currentTimeMillis();
        if (now < mutedUntil) return;
        if (now - lastPlay[id] < 70) return;
        lastPlay[id] = now;
        push(id);
    }

    static void sfxAt(int id, int x, int y) {
        int dx = (x - W.px) >> 16, dy = (y - W.py) >> 16;
        if (dx * dx + dy * dy > 150) return;
        sfx(id);
    }

    static void voice(int id) {
        if (!voiceOn || vPath[id] == null || System.currentTimeMillis() < mutedUntil) return;
        push(C_VOICE + id);
    }

    /** Switch the music track (-1 = none). Call it BEFORE any voice line that goes with the change. */
    static void music(int id) {
        wantMusic = id;
        push(C_MUSIC + 1 + id);
    }

    static void stopAll() { push(C_STOP); }

    static void resume() {
        if (wantMusic >= 0) push(C_MUSIC + 1 + wantMusic);
    }

    /** New level / restart: give a phone that had audio trouble another chance. */
    static void newLevel() {
        if (worker != null) mutedUntil = 0;
        fails = 0;
    }

    /** Watchdog, called every frame by the game loop. */
    static void poll() {
        Snd old;
        synchronized (lock) {
            if (busyAt == 0 || System.currentTimeMillis() - busyAt < 4000) return;
            // the worker has been stuck inside one MMAPI call for 4 s: the phone's audio hung.
            old = worker;
            gen++;
            busyAt = 0;
            fails = 0;
            mutedUntil = 0;
            if (++restarts > 6) { worker = null; mutedUntil = Long.MAX_VALUE; }   // this phone's audio is hopeless
            else {
                startWorker();
                if (wantMusic >= 0) push(C_MUSIC + 1 + wantMusic);
            }
        }
        if (old == null) return;
        // close each of the stuck worker's players on its own throw-away thread: the one that is
        // stuck may block again, but then only that thread hangs and the others still get freed.
        // Sampled sounds go first (see class comment); the MIDI one simply waits if it has to.
        for (int i = 0; i < NSFX; i++) reap(old.cache[i]);
        reap(old.voiceP);
        reap(old.music);
    }

    static void reap(Player p) {
        try { if (p != null) new Thread(new Snd(p)).start(); } catch (Throwable t) { }
    }

    static void shutdown() {
        synchronized (lock) {
            alive = false;
            lock.notifyAll();
        }
        // give the worker a moment to close its players so nothing keeps playing after exit
        for (int i = 0; i < 10; i++) {
            Snd w = worker;
            if (w == null || w.done) return;
            try { Thread.sleep(50); } catch (InterruptedException e) { }
        }
    }

    // ---------------- worker

    public void run() {
        if (victim != null) {
            kill(victim);
            return;
        }
        while (true) {
            int cmd = -1;
            long at = 0;
            synchronized (lock) {
                if (!alive || gen != myGen) break;
                if (qh == qt) {
                    try { lock.wait(500); } catch (InterruptedException e) { }
                    if (!alive || gen != myGen) break;
                }
                if (qh != qt) {
                    cmd = q[qh];
                    at = qtime[qh];
                    qh = (qh + 1) % QN;
                    if (cmd >= C_MUSIC) {
                        // skip a music change that a newer music/stop command already replaces
                        for (int i = qh; i != qt; i = (i + 1) % QN) if (q[i] >= C_MUSIC) { cmd = -2; break; }
                    }
                }
                busyAt = System.currentTimeMillis();
            }
            try {
                if (cmd == -1) idle();
                else if (cmd >= C_STOP) doStop();
                else if (cmd >= C_MUSIC) doMusic(cmd - C_MUSIC - 1);
                else if (cmd >= C_VOICE) {
                    if (System.currentTimeMillis() - at < 1500) doVoice(cmd - C_VOICE);
                    fails = 0;
                } else if (cmd >= 0) {
                    if (System.currentTimeMillis() - at < 400) doSfx(cmd);
                    fails = 0;
                }
            } catch (Throwable t) {
                if (cmd >= 0 && cmd < C_MUSIC && ++fails > 12) {
                    fails = 0;
                    mutedUntil = System.currentTimeMillis() + 5000;   // stop hammering, retry in 5 s
                }
            }
            synchronized (lock) {
                if (gen == myGen) busyAt = 0;
            }
        }
        release();
        done = true;
    }

    static Player create(String p) throws Exception {
        InputStream in = G.open(p);
        if (in == null) return null;
        Player pl = Manager.createPlayer(in, mime(p));
        pl.realize();
        pl.prefetch();
        return pl;
    }

    static int state(Player p) {
        try { return p.getState(); } catch (Throwable t) { return Player.CLOSED; }
    }

    static void kill(Player p) {
        if (p == null) return;
        try { if (p.getState() == Player.STARTED) p.stop(); } catch (Throwable t) { }
        try { p.close(); } catch (Throwable t) { }
    }

    /** Stop and close every sampled-sound player (keeps a voice line that is still playing unless all). */
    void flush(boolean all) {
        for (int i = 0; i < NSFX; i++) {
            if (cache[i] != null) { kill(cache[i]); cache[i] = null; }
        }
        cached = 0;
        if (voiceP != null && (all || state(voiceP) != Player.STARTED)) { kill(voiceP); voiceP = null; }
    }

    void release() {
        flush(true);              // sampled sounds first, then the MIDI (see class comment)
        kill(music);
        music = null;
        curMusic = -1;
    }

    void idle() {
        // free a voice line that has finished playing
        if (voiceP != null && state(voiceP) != Player.STARTED) { kill(voiceP); voiceP = null; }
    }

    void doSfx(int id) throws Exception {
        Player p = cache[id];
        if (p != null && state(p) == Player.CLOSED) { cache[id] = null; cached--; p = null; }
        if (p == null) {
            idle();
            if (cached >= 5) {
                // evict the least recently used player
                int ev = -1;
                long old = Long.MAX_VALUE;
                for (int i = 0; i < NSFX; i++) if (cache[i] != null && lastPlay[i] < old) { old = lastPlay[i]; ev = i; }
                if (ev >= 0) { kill(cache[ev]); cache[ev] = null; cached--; }
            }
            try {
                p = create(sfxPath[id]);
            } catch (Exception e) {
                flush(false);     // out of audio resources? free the other effects and try once more
                p = create(sfxPath[id]);
            }
            if (p == null) { sfxPath[id] = null; return; }
            cache[id] = p;
            cached++;
        }
        try {
            if (p.getState() == Player.STARTED) p.stop();
            p.setMediaTime(0);
        } catch (Throwable t) { }
        p.start();
    }

    void doVoice(int id) throws Exception {
        if (voiceP != null) { kill(voiceP); voiceP = null; }
        Player p;
        try {
            p = create(vPath[id]);
        } catch (Exception e) {
            flush(false);
            p = create(vPath[id]);
        }
        if (p == null) { vPath[id] = null; return; }
        voiceP = p;
        p.start();
    }

    void doMusic(int id) throws Exception {
        if (music != null && curMusic == id && musicOn && state(music) != Player.CLOSED) {
            if (state(music) != Player.STARTED) music.start();
            return;
        }
        // silence every WAV before touching the MIDI player: stopping a MIDI while a WAV plays
        // freezes the audio system on many phones (the old "music never stops after death" bug)
        flush(true);
        if (music != null) { kill(music); music = null; curMusic = -1; }
        if (id < 0 || !musicOn || mPath[id] == null) return;
        Player p;
        try {
            p = create(mPath[id]);
        } catch (Exception e) {
            // out of audio resources (e.g. players of a replaced worker still closing): retry once
            try { Thread.sleep(300); } catch (InterruptedException ie) { }
            p = create(mPath[id]);
        }
        if (p == null) return;
        p.setLoopCount(id == M_WIN || id == M_DEAD ? 1 : -1);
        music = p;
        curMusic = id;
        p.start();
    }

    void doStop() {
        flush(true);
        if (music != null) { try { music.stop(); } catch (Throwable t) { } }
    }
}
