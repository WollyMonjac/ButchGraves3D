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
 *  - no Player method is ever called from a PlayerListener callback (no listeners at all);
 *  - few players and little churn: at most 5 effect players are kept open (real phones run out of
 *    audio resources, and on some creating players while the MIDI plays hangs the audio);
 *  - the player's own gun gets a second copy of its sound instead of stopping and restarting the one
 *    still playing (emulators built on Java Sound or Android's MediaPlayer silently ignore that restart),
 *    its shots jump the queue, and its players are evicted last;
 *  - the music comes first: the engine never switches it off by itself. When the phone can't play effects over the
 *    MIDI, or its audio hangs while both play, it is the effects that give way (fewer players, then none but the
 *    gun's) - and if the phone stops the music on its own (it took the music's channel
 *    for an effect, or ignored the loop count), the music is started again and fewer effects play at once over it;
 *  - when the phone's audio hangs, the engine backs off step by step instead of retrying the same thing:
 *    a hang while starting music stops music retries until the next level, repeated effect hangs without music
 *    shrink the player pool and then switch sampled sounds off for the session;
 *  - a phone that can only play one sampled sound at a time is detected and handled.
 */
final class Snd implements Runnable {
    // ---------------- sound effect ids (order matches SFX keys)
    static final int REVOLVER = 0, SHOTGUN = 1, RELOAD = 2, TOMMY = 3, LAUNCH = 4, EXPLODE = 5, SWING = 6, HIT = 7, DOOR = 8,
            PICKUP = 9, WPICK = 10, KEY = 11, HURT = 12, FIREBALL = 13, MDIE = 14, THUNDER = 15, CLICK = 16, SWITCH = 17,
            SECRET = 18, ZOMBIE = 19, SCARE = 20, WITCH = 21, GHOST = 22, BOSS = 23, BOSSDIE = 24, SKEL = 25, CLOWN = 26, WOLF = 27,
            BAT = 28, VAMP = 29, GIGGLE = 30, COUNT = 31, KNIFE = 32, HONK = 33, TELE = 34, BONK = 35, SCREAM = 36, ZAPS = 37, LASER = 38,
            SAW = 39, ROBOT = 40, SKITTER = 41, BUZZ = 42, STOMP = 43, BOULDER = 44, DARTS = 45, MUSKET = 46, ROAR = 47, MUMMY = 48,
            WAIL = 49, SIREN = 50, STATIC = 51, SPIKES = 52, SEVEN = 53, FALL = 54, CONQ = 55, NSFX = 56;
    static final String[] SFXKEY = {"revolver", "shotgun", "reload", "tommy", "launch", "explode", "swing", "hit", "door",
            "pickup", "wpick", "key", "hurt", "fireball", "mdie", "thunder", "click", "switch", "secret", "zombie", "scare",
            "witch", "ghost", "boss", "bossdie", "skel", "clown", "wolf", "bat", "vamp", "giggle", "count", "knife", "honk", "tele",
            "bonk", "scream", "zap", "laser", "saw", "robot", "skitter", "buzz", "stomp", "boulder", "darts", "musket", "roar", "mummy",
            "wail", "siren", "static", "spikes", "seven", "fall", "conq"};
    // ---------------- voice lines
    static final int V_START1 = 0, V_START2 = 1, V_KILL1 = 2, V_KILL2 = 3, V_KILL3 = 4, V_GHOST = 5, V_PUMPKIN = 6, V_SHOVEL = 7,
            V_GIB = 8, V_WEAPON = 9, V_LAUNCHER = 10, V_HEALTH = 11, V_LOWHP = 12, V_SECRET = 13, V_BOSS = 14, V_WIN = 15,
            V_LEVEL = 16, V_PAIN1 = 17, V_PAIN2 = 18, V_DIE = 19, V_START3 = 20, V_START4 = 21, V_KCLOWN = 22, V_KSKEL = 23,
            V_KWOLF = 24, V_KBAT = 25, V_KVAMP = 26, V_BOSS2 = 27, V_BOSS3 = 28, V_WIN2 = 29, V_WIN3 = 30, V_KILL4 = 31, V_KILL5 = 32,
            V_C1A = 33, V_C1B = 34, V_C1C = 35, V_C1D = 36, V_C1E = 37, V_C2A = 38, V_C2B = 39, V_C2C = 40, V_C3A = 41, V_C3B = 42,
            V_C3C = 43, V_C3D = 44, V_START5 = 45, V_KROBOT = 46, V_KDRONE = 47, V_KSPIDER = 48, V_BOSS4 = 49, V_WIN4 = 50, V_TELE = 51,
            V_SHIFT = 52, V_C4A = 53, V_C4B = 54, V_C4C = 55, V_C4D = 56, V_C4E = 57, V_C4F = 58, V_C4G = 59, V_C1F = 60,
            V_G1A = 61, V_G1B = 62, V_G1C = 63, V_G2A = 64, V_G4A = 65, V_G4B = 66, V_START6 = 67, V_BOSS5 = 68, V_WIN5 = 69,
            V_KMUMMY = 70, V_KJAG = 71, V_KCONQ = 72, V_KWEEP = 73, V_PIT = 74, V_IDOL = 75, V_RADIO = 76, V_OTHER = 77, V_RISE = 78,
            V_C5A = 79, V_C5B = 80, V_C5C = 81, V_C5D = 82, V_C5E = 83, V_C5F = 84, V_G5A = 85, V_G5B = 86, V_C5G = 87,
            NVOICE = 88;
    static final String[] VKEY = {"start1", "start2", "kill1", "kill2", "kill3", "ghost", "pumpkin", "shovel", "gib", "weapon",
            "launcher", "health", "lowhp", "secret", "boss", "win", "level", "pain1", "pain2", "die", "start3", "start4", "kclown",
            "kskel", "kwolf", "kbat", "kvamp", "boss2", "boss3", "win2", "win3", "kill4", "kill5", "c1a", "c1b", "c1c", "c1d", "c1e",
            "c2a", "c2b", "c2c", "c3a", "c3b", "c3c", "c3d", "start5", "krobot", "kdrone", "kspider", "boss4", "win4", "tele", "shift",
            "c4a", "c4b", "c4c", "c4d", "c4e", "c4f", "c4g", "c1f", "g1a", "g1b", "g1c", "g2a", "g4a", "g4b", "start6", "boss5", "win5",
            "kmummy", "kjag", "kconq", "kweep", "pit", "idol", "radio", "other", "rise", "c5a", "c5b", "c5c", "c5d", "c5e", "c5f", "g5a", "g5b", "c5g"};
    // ---------------- music
    static final int M_TITLE = 0, M_STORY = 1, M_L1 = 2, M_WIN = 14, M_DEAD = 15, M_CUT = 16, M_L13 = 17, M_L17 = 21, NMUS = 25;
    static final String[] MKEY = {"title", "story", "level1", "level2", "level3", "level4", "level5", "level6", "level7", "level8",
            "level9", "level10", "level11", "level12", "win", "dead", "cutscene", "level13", "level14", "level15", "level16",
            "level17", "level18", "level19", "level20"};

    static boolean sfxOn = true, voiceOn = true;
    // music: on, off, or only on the menus/story/tally screens (the player's choice in Options; the engine itself never
    // turns the music off). Some phones (e.g. some Nokia Series 40 XpressMusic models) can't play a WAV while a MIDI
    // plays: there the effects wait for the music (noMix), and "menus only" is how the player can get them back.
    static final int MUS_OFF = 0, MUS_ON = 1, MUS_MENUS = 2;
    static int musicMode = MUS_ON;
    static int mixFails;
    static boolean noMix;                // effects fail while the MIDI plays (found out again on every level)
    static int calm;                     // audio hangs while the MIDI played: 1 fewer players, 2 no new ones but the gun's
                                         // and no voices over the music (for the session)
    static int maxWav = 99;              // sampled sounds allowed at once over the music (lowered when the phone takes
                                         // the music's channel for an effect)
    static int musicKicks;               // times the music had to be started again (shown with the FPS counter)
    static volatile int mSt = -1;        // the music player's state as the worker last saw it
    static boolean alive = true;
    static final String[] sfxPath = new String[NSFX], vPath = new String[NVOICE], mPath = new String[NMUS];
    static final long[] lastPlay = new long[NSFX];
    static int wantMusic = -1, fails, restarts;
    static int curWeapon = -1;           // effect id of the player's current weapon (kept loaded)
    static int plimit = 5;               // effect players kept open; lowered if the phone runs out or hangs
    static boolean oneChannel;           // this phone can't mix two sampled sounds
    static int oneChanHits;
    // hang recovery (see poll): what the stuck worker was doing, and what has been given up on this session
    static int busyCmd = -1, musicHangs, sfxHangs, mixHangs;
    static boolean musicPlaying;         // a MIDI is started (kept by the worker; never ask a stuck player)
    static boolean musicDead, sampledDead;
    static String note;                  // something the game should tell the player (set by the audio thread)
    static long mutedUntil;              // effects/voice are skipped until then after repeated failures

    // ---------------- command queue: <1000 effect, 1000+ voice, 2001+ music, 3000 stop all, 4000+ preload effect
    static final int C_VOICE = 1000, C_MUSIC = 2000, C_STOP = 3000, C_LOAD = 4000, QN = 32, PMAX = 8;
    static final int[] q = new int[QN];
    static final long[] qtime = new long[QN];
    static int qh, qt, gen;
    static long busyAt;                  // when the worker started its current command (0 = idle)
    static final Object lock = new Object();
    static Snd worker;

    // ---------------- per-worker state (a replaced worker keeps its own players)
    final int myGen;
    final Player victim;                 // non-null: this instance only closes one abandoned player
    final Player[] pp = new Player[PMAX];   // effect players; several may hold the same effect
    final int[] pid = new int[PMAX];        // effect id per player (-1 = empty)
    final long[] puse = new long[PMAX];     // when each player was last started
    Player music, voiceP;
    int curMusic = -1;
    boolean musicLoop;                      // the current track loops (keep it going)
    long keepT;                             // last music check
    long lastMt = -1;                       // the music's media time at the last check that found it not started
    int kickFails;                          // restarts in a row that didn't take (then leave it alone)
    int peak;                               // most sampled sounds playing at once lately (at peakT)
    long peakT;
    long lastCreate;                        // when this worker last opened an effect player
    boolean done;

    Snd(int g) { myGen = g; victim = null; for (int i = 0; i < PMAX; i++) pid[i] = -1; }

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
        String[] mdef = {"m_title", "m_story", "m_level1", "m_level2", "m_level3", "m_boss", "m_level5", "m_level6", "m_level7",
                "m_boss2", "m_level9", "m_level10", "m_level11", "m_boss3", "m_win", "m_dead", "m_cut", "m_level13", "m_level14",
                "m_level15", "m_boss4", "m_level17", "m_level18", "m_level19", "m_boss5"};
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

    /** The player's own weapon sounds: never dropped, played before anything else that is waiting. */
    static boolean prio(int id) {
        return id == REVOLVER || id == SHOTGUN || id == TOMMY || id == LAUNCH || id == SWING;
    }

    /** Effects worth a new player even in a busy moment: the player's gun, getting hurt, pickups, keys, doors, explosions
     *  and the bosses and traps that tell you what's coming. Everything else (a monster's growl, a hit, a click) only
     *  plays if its player is already open, or once the engine hasn't opened one for a while. */
    static boolean important(int id) {
        return prio(id) || id == HURT || id == EXPLODE || id == PICKUP || id == WPICK || id == KEY || id == SECRET || id == DOOR
                || id == SWITCH || id == BOSS || id == BOSSDIE || id == GIGGLE || id == COUNT || id == ROBOT || id == SEVEN
                || id == STOMP || id == BOULDER || id == SIREN || id == TELE || id == FALL || id == DARTS || id == MUSKET;
    }

    /** How many copies of an effect may play at once (fast weapons overlap their own sound). */
    static int copies(int id) {
        return prio(id) && id == curWeapon && plimit >= 4 ? 2 : 1;
    }

    static void push(int cmd) {
        synchronized (lock) {
            int n = qt - qh;
            if (n < 0) n += QN;
            if (cmd < C_VOICE && n >= (prio(cmd) ? 12 : 4)) return;   // effects backlog: a late bang is worse than none
            if (cmd < C_VOICE && prio(cmd)) {
                // the same shot still waiting (slow phone): one bang is enough, just keep it fresh
                for (int i = qh; i != qt; i = (i + 1) % QN) if (q[i] == cmd) { qtime[i] = System.currentTimeMillis(); return; }
            }
            if (n >= QN - 1) qh = (qh + 1) % QN;        // full: drop the oldest command
            q[qt] = cmd;
            qtime[qt] = System.currentTimeMillis();
            qt = (qt + 1) % QN;
            lock.notifyAll();
        }
    }

    static void sfx(int id) {
        if (!sfxOn || sampledDead || sfxPath[id] == null) return;
        if (musicPlaying && noMix) return;                      // the music has the phone's only channel
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
        if (!voiceOn || sampledDead || vPath[id] == null || System.currentTimeMillis() < mutedUntil) return;
        if (musicPlaying && (noMix || calm >= 2)) return;
        push(C_VOICE + id);
    }

    /** One short line about the audio, shown under the FPS counter, so a player can tell what their phone does:
     *  whether the music is really playing, K how often it had to be restarted, W how many effects may play over it,
     *  C how far the effects backed off after hangs, NOMIX if effects can't play over music, H audio hangs. */
    static String status() {
        StringBuffer b = new StringBuffer(!musicPlaying ? "NO MUSIC" : mSt == Player.STARTED ? "MUSIC ON" : "MUSIC STOPPED");
        if (musicKicks > 0) b.append(" K").append(musicKicks);
        if (maxWav < 99) b.append(" W").append(maxWav);
        if (calm > 0) b.append(" C").append(calm);
        if (noMix) b.append(" NOMIX");
        if (restarts > 0) b.append(" H").append(restarts);
        return b.toString();
    }

    static String prop(String k) {
        try { return System.getProperty(k); } catch (Throwable t) { return null; }
    }

    /** The track that really plays for a wanted one, given the music setting (-1 = silence). */
    static int effective(int id) {
        if (id < 0 || musicMode == MUS_OFF || musicDead) return -1;
        if (musicMode == MUS_MENUS && (id == M_CUT || (id >= M_L1 && id < M_WIN) || id >= M_L13)) return -1;
        if (id == M_CUT && (noMix || calm >= 2)) return -1;     // a cutscene is about its voices: they get the channel
        return id;
    }

    /** Switch the music track (-1 = none). Call it BEFORE any voice line that goes with the change. */
    static void music(int id) {
        wantMusic = id;
        push(C_MUSIC + 1 + effective(id));
    }

    static void stopAll() { push(C_STOP); }

    /** The player switched weapon: its sound gets a second copy and is evicted last. */
    static void weapon(int id) {
        curWeapon = id;
    }

    static void resume() {
        if (wantMusic >= 0) push(C_MUSIC + 1 + effective(wantMusic));
    }

    /** New level / restart: give a phone that had audio trouble another chance. */
    static void newLevel() {
        synchronized (lock) {
            fails = 0;
            mixFails = 0;
            noMix = false;                   // a phone that really can't mix shows it again within a few effects
            musicDead = false;               // music that hung gets one more try per level
            if (worker == null && alive) {   // the audio had been given up on: try again with a fresh worker
                restarts = 4;
                gen++;
                startWorker();
            }
            mutedUntil = 0;
        }
    }

    /** Watchdog, called every frame by the game loop. */
    static void poll() {
        Snd old;
        synchronized (lock) {
            if (busyAt == 0) return;
            int hc = busyCmd;
            boolean isMusic = hc >= C_MUSIC && hc < C_LOAD;
            if (System.currentTimeMillis() - busyAt < (isMusic ? 5000 : 4000)) return;
            // the worker has been stuck inside one MMAPI call: the phone's audio hung. Replace the worker, and back
            // off from whatever hung so the new one doesn't walk straight into the same hang.
            old = worker;
            gen++;
            busyAt = 0;
            fails = 0;
            mutedUntil = 0;
            boolean retryMusic = true;
            if (isMusic) {
                retryMusic = false;              // don't restart the track that just hung (that loops forever)
                if (++musicHangs >= 2) musicDead = true;
            } else if (hc >= 0 && hc < C_MUSIC) {
                if (musicPlaying) {
                    // an effect or a voice hung while the MIDI played: this phone struggles to do both. The music stays;
                    // the effects back off: fewer players, then no new ones but the gun's (and no voices) over it
                    mixHangs++;
                    if (plimit > 3) plimit = 3;
                    if (calm < 2 && ++calm == 2) note = "SOUND TROUBLE: FEWER EFFECTS DURING MUSIC (SEE OPTIONS)";
                } else if (++sfxHangs >= 4) {
                    sampledDead = true;          // effects and voices off for this session, music stays
                } else {
                    plimit = sfxHangs >= 2 ? 2 : 3;
                }
            }
            musicPlaying = false;
            if (++restarts > 16) { worker = null; mutedUntil = Long.MAX_VALUE; }   // give up until the next level
            else {
                if (restarts > 8) mutedUntil = Long.MAX_VALUE;   // effects and voices rest until the next level, music goes on
                startWorker();
                if (retryMusic && wantMusic >= 0) push(C_MUSIC + 1 + effective(wantMusic));
            }
        }
        if (old == null) return;
        // close each of the stuck worker's players on its own throw-away thread: the one that is
        // stuck may block again, but then only that thread hangs and the others still get freed.
        // Sampled sounds go first (see class comment); the MIDI one simply waits if it has to.
        for (int i = 0; i < PMAX; i++) reap(old.pp[i]);
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
                    // a weapon shot waiting behind other effects or voices goes first (never past music/stop)
                    int k = qh;
                    for (int i = qh; i != qt; i = (i + 1) % QN) {
                        if (q[i] >= C_MUSIC && q[i] < C_LOAD) break;
                        if (q[i] < C_VOICE && prio(q[i])) { k = i; break; }
                    }
                    cmd = q[k];
                    at = qtime[k];
                    for (int i = k; i != qh; ) {          // close the gap
                        int pr = (i + QN - 1) % QN;
                        q[i] = q[pr];
                        qtime[i] = qtime[pr];
                        i = pr;
                    }
                    qh = (qh + 1) % QN;
                    if (cmd >= C_MUSIC && cmd < C_LOAD) {
                        // skip a music change that a newer music/stop command already replaces
                        for (int i = qh; i != qt; i = (i + 1) % QN) if (q[i] >= C_MUSIC && q[i] < C_LOAD) { cmd = -2; break; }
                    }
                }
                busyAt = System.currentTimeMillis();
                busyCmd = cmd;
            }
            boolean played = false;
            try {
                if (cmd == -1) idle();
                else if (cmd >= C_LOAD) { if (copiesOf(cmd - C_LOAD) == 0) load(cmd - C_LOAD); }
                else if (cmd >= C_STOP) doStop();
                else if (cmd >= C_MUSIC) doMusic(cmd - C_MUSIC - 1);
                else if (cmd >= C_VOICE) {
                    if (System.currentTimeMillis() - at < 1500) doVoice(cmd - C_VOICE);
                    fails = 0;
                } else if (cmd >= 0) {
                    if (System.currentTimeMillis() - at < 400) played = doSfx(cmd);
                    fails = 0;
                }
                // a sound really started while the MIDI plays: this phone mixes (an effect skipped by the churn limit
                // proves nothing either way)
                if ((played || (cmd >= C_VOICE && cmd < C_MUSIC)) && music != null && state(music) == Player.STARTED) mixFails = 0;
                keep();
            } catch (Throwable t) {
                if (cmd >= 0 && cmd < C_MUSIC && music != null && state(music) == Player.STARTED && ++mixFails >= 4 && !noMix) {
                    // every effect fails while the MIDI plays: this phone can't mix. The music keeps playing and the
                    // effects wait for it (Options -> music in menus only brings them back)
                    noMix = true;
                    note = "NO SOUND MIXING: NO EFFECTS DURING MUSIC (SEE OPTIONS)";
                }
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
        for (int i = 0; i < PMAX; i++) {
            if (pp[i] != null) { kill(pp[i]); pp[i] = null; }
            pid[i] = -1;
        }
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

    /** Sampled sounds playing right now. */
    int playing() {
        int n = voiceP != null && state(voiceP) == Player.STARTED ? 1 : 0;
        for (int i = 0; i < PMAX; i++) if (pp[i] != null && state(pp[i]) == Player.STARTED) n++;
        return n;
    }

    /** Make room for one more sampled sound over the music: cut the oldest effect short (the current gun's last). */
    boolean makeRoom(int keep) {
        int ev = -1;
        long best = Long.MAX_VALUE;
        for (int i = 0; i < PMAX; i++) {
            if (i == keep || pp[i] == null || state(pp[i]) != Player.STARTED) continue;
            long u = puse[i] + (pid[i] == curWeapon ? 1000000000L : 0);
            if (u < best) { best = u; ev = i; }
        }
        if (ev < 0) return false;
        try { pp[ev].stop(); } catch (Throwable t) { }
        return true;
    }

    /** Remember how many sampled sounds play at once (just after one started), for working out a late channel steal. */
    void notePeak() {
        int n = playing();
        long now = System.currentTimeMillis();
        if (n >= peak || now - peakT > 1500) { peak = n; peakT = now; }
    }

    /** True when the music is a looping track that is really playing (checked before starting a sampled sound). */
    boolean musicOn() {
        return musicPlaying && music != null && musicLoop && state(music) == Player.STARTED;
    }

    /** Starting a sampled sound just stopped the music: the phone ran out of channels and took the music's. Play
     *  fewer sounds at once over the music from now on, and give it its channel back. */
    void stolen() {
        int n = playing() - 1;
        if (n < 1) n = 1;
        if (n < maxWav) maxWav = n;
        kick();
    }

    void kick() {
        synchronized (lock) { busyCmd = C_MUSIC + 1 + curMusic; }   // a hang in here counts as a music hang
        try { music.start(); musicKicks++; } catch (Throwable t) { }
        mSt = state(music);
        if (mSt == Player.STARTED) kickFails = 0;
        else kickFails++;
    }

    /** Keep the music going: if the phone stopped it on its own (took its channel for an effect, ignored the loop
     *  count, paused it for something of its own), start it again where it stopped, as soon as there is room. */
    void keep() {
        if (music == null || !musicPlaying || !musicLoop) return;
        long now = System.currentTimeMillis();
        if (now - keepT < 600) return;
        keepT = now;
        int st = state(music);
        mSt = st;
        if (st == Player.STARTED) { lastMt = -1; return; }
        if (st == Player.CLOSED) { music = null; curMusic = -1; push(C_MUSIC + 1 + effective(wantMusic)); return; }
        // some phones report a wrong state: if the music's clock is still running, it is playing - leave it alone
        boolean end = atEnd();
        long mt = -1;
        try { mt = music.getMediaTime(); } catch (Throwable e) { }
        boolean moving = !end && mt > 0 && mt != lastMt;
        lastMt = mt;
        if (moving || kickFails >= 3) return;          // (three restarts that didn't take: this phone won't, stop trying)
        int n = playing();
        if (!end && (n > 0 || now - peakT < 2000)) {
            // stopped in the middle of the track while effects play: the phone took its channel for one of them (and
            // only said so late): play fewer at once over the music than were playing then
            int m = (now - peakT < 2000 && peak > n ? peak : n) - 1;
            if (m < 1) m = 1;
            if (m < maxWav) maxWav = m;
        }
        if (n >= maxWav) makeRoom(-1);                 // no free channel: the music gets one, an effect is cut short
        kick();
    }

    /** The music stopped at the end of the track (a phone that ignores the loop count), as far as the phone tells. */
    boolean atEnd() {
        try {
            long d = music.getDuration(), t = music.getMediaTime();
            return d > 0 && t >= d - 1000000;
        } catch (Throwable e) { return false; }
    }

    int copiesOf(int id) {
        int n = 0;
        for (int i = 0; i < PMAX; i++) if (pp[i] != null && pid[i] == id) n++;
        return n;
    }

    /** Open one more player for an effect; returns its slot or -1.
     *  Opening and closing players while the MIDI plays is what hangs phone audio (the more of it, the sooner), and a boss
     *  fight asks for a dozen different sounds a second. So while music plays a new player is opened at most every 0.5 s
     *  for an important effect and every 1.2 s for anything else (the gun is never held back), and a minor effect never
     *  pushes out a player that an important one used in the last few seconds. */
    int load(int id) throws Exception {
        idle();
        long now = System.currentTimeMillis();
        boolean imp = important(id);
        if (musicPlaying && !prio(id) && (calm >= 2 || now - lastCreate < (imp ? 500 : 1200))) return -1;
        int used = 0, slot = -1;
        for (int i = 0; i < PMAX; i++) {
            if (pp[i] != null && state(pp[i]) == Player.CLOSED) { pp[i] = null; pid[i] = -1; }
            if (pp[i] != null) used++;
            else if (slot < 0) slot = i;
        }
        if (used >= plimit || slot < 0) {
            // evict the least recently used player that is not playing; the current weapon's goes last
            int ev = -1;
            long best = Long.MAX_VALUE;
            for (int i = 0; i < PMAX; i++) {
                if (pp[i] == null || state(pp[i]) == Player.STARTED) continue;
                if (!imp && important(pid[i]) && now - puse[i] < 4000) continue;
                long u = puse[i] + (pid[i] == curWeapon ? 1000000000L : 0);
                if (u < best) { best = u; ev = i; }
            }
            if (ev < 0) return -1;            // everything is playing: skip this effect
            kill(pp[ev]);
            pp[ev] = null;
            pid[ev] = -1;
            slot = ev;
        }
        Player p;
        try {
            p = create(sfxPath[id]);
        } catch (Exception e) {
            // out of audio resources: keep fewer players open from now on, free the others, try once more
            if (used > 3 && used - 1 < plimit) plimit = used - 1;
            flush(false);
            slot = 0;
            p = create(sfxPath[id]);
        }
        lastCreate = System.currentTimeMillis();
        if (p == null) { sfxPath[id] = null; return -1; }
        pp[slot] = p;
        pid[slot] = id;
        puse[slot] = 0;
        return slot;
    }

    /** Stop every other effect that is playing; false if none was. */
    boolean stopOthers(int keep) {
        boolean any = false;
        for (int i = 0; i < PMAX; i++) {
            if (i == keep || pp[i] == null || state(pp[i]) != Player.STARTED) continue;
            try { pp[i].stop(); any = true; } catch (Throwable t) { }
        }
        return any;
    }

    /** Play an effect; false if it was skipped (no free player, or the churn limit said not now). */
    boolean doSfx(int id) throws Exception {
        int free = -1, oldest = -1, n = 0;
        for (int i = 0; i < PMAX; i++) {
            if (pp[i] == null || pid[i] != id) continue;
            int st = state(pp[i]);
            if (st == Player.CLOSED) { pp[i] = null; pid[i] = -1; continue; }
            n++;
            if (st != Player.STARTED) { if (free < 0 || puse[i] < puse[free]) free = i; }
            else if (oldest < 0 || puse[i] < puse[oldest]) oldest = i;
        }
        int slot = free;
        // still playing: open another copy rather than restarting it (a restart is lost on many emulators)
        if (slot < 0 && n < copies(id)) slot = load(id);
        boolean restart = false;
        if (slot < 0) {
            // every copy is busy: only the player's own gun (or a one-channel phone) cuts its sound short
            if (oldest < 0 || !(prio(id) || oneChannel)) return false;
            slot = oldest;
            restart = true;
        }
        Player p = pp[slot];
        if (oneChannel) {
            if (voiceP != null && state(voiceP) == Player.STARTED) return false;   // a voice line has the only channel
            stopOthers(slot);
        }
        boolean mOn = musicOn();
        if (mOn && maxWav < 99 && playing() - (restart ? 1 : 0) >= maxWav) {
            // as many sounds as this phone can play over the music: only the gun gets one, by cutting another short
            if (!prio(id) || !makeRoom(slot)) return false;
        }
        try {
            if (restart) p.stop();
            p.setMediaTime(0);
        } catch (Throwable t) { }
        try {
            p.start();
        } catch (Exception e) {
            // maybe the phone can't mix two sampled sounds: free the channel; twice in a row and that's what it is
            if (oneChannel || !stopOthers(slot)) throw e;
            p.start();
            if (++oneChanHits >= 2) oneChannel = true;
        }
        puse[slot] = System.currentTimeMillis();
        if (mOn) {
            notePeak();
            if (state(music) != Player.STARTED) stolen();
        }
        return true;
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
        boolean mOn = musicOn();
        if (mOn && maxWav < 99) while (playing() >= maxWav && makeRoom(-1)) { }
        p.start();
        if (mOn) {
            notePeak();
            if (state(music) != Player.STARTED) stolen();
        }
    }

    void doMusic(int id) throws Exception {
        if (music != null && curMusic == id && state(music) != Player.CLOSED) {
            if (state(music) != Player.STARTED) music.start();
            musicPlaying = true;
            return;
        }
        // silence every WAV before touching the MIDI player: stopping a MIDI while a WAV plays
        // freezes the audio system on many phones (the old "music never stops after death" bug)
        flush(true);
        if (music != null) { musicPlaying = false; kill(music); music = null; curMusic = -1; }
        if (id < 0 || mPath[id] == null) return;
        Player p;
        try {
            p = create(mPath[id]);
        } catch (Exception e) {
            // out of audio resources (e.g. players of a replaced worker still closing): retry once
            try { Thread.sleep(300); } catch (InterruptedException ie) { }
            p = create(mPath[id]);
        }
        if (p == null) return;
        musicLoop = !(id == M_WIN || id == M_DEAD || id == M_CUT);
        lastMt = -1;
        kickFails = 0;
        p.setLoopCount(musicLoop ? -1 : 1);
        music = p;
        curMusic = id;
        p.start();
        musicPlaying = true;
        mSt = Player.STARTED;
    }

    void doStop() {
        flush(true);
        if (music != null) { musicPlaying = false; try { music.stop(); } catch (Throwable t) { } }
    }
}
