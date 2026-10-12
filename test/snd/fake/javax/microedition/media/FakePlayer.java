package javax.microedition.media;

import java.util.*;

/**
 * Fake MMAPI player that models the failure modes of real phone firmware:
 *  A  "mixer lock": stopping/closing the MIDI player while a sampled (WAV) sound is playing waits for
 *     the WAV to finish, but the WAV can't finish while the mixer is locked -> permanent deadlock,
 *     unless another thread stops/closes the WAV.
 *  B  "random hang": the Nth WAV start() never returns, and every later call on that player hangs too.
 *  C  "resource limit": only MAXPREF players may be prefetched at once; prefetch() beyond that throws.
 *  R  "restart race" (Java Sound Clip based emulators, Android MediaPlayer): start() right after stop()
 *     on the same player is silently ignored - the line still reports itself running.
 *  M  "one channel": only one WAV can play at a time; start() of a second one throws.
 *  X  "no mixing" (Nokia Series 40): no WAV can start while a MIDI is playing.
 *  Y  "WAV+MIDI hang": every 5th WAV prefetched while a MIDI plays never returns.
 *  Z  "MIDI hang": the 2nd MIDI start() never returns.
 *  P  "too many players": prefetching a 7th player never returns (instead of throwing like C).
 *  Q  "channel steal": the phone has three audio streams; a WAV that starts when all are busy silently takes the
 *     MIDI's (the music just stops, no exception, no event: its state goes back to PREFETCHED).
 *  D  like Q, but the music stops a moment (150 ms) after the effect started, as when the phone tells the MIDI
 *     player to give up its channel through its own event queue.
 *  L  "loop ignored": setLoopCount(-1) is ignored, the MIDI plays once (8 s here) and stops at its end.
 * Music uptime (how long a MIDI was really playing) is measured for every model: musicMs().
 */
public class FakePlayer implements Player {
    public static final long T0 = System.currentTimeMillis();
    public static final Object eng = new Object();
    public static boolean modelA, modelC, modelR, modelM, modelX, modelY, modelZ, modelP, modelQ, modelL, modelD;
    static long midiSince = -1, midiTotal;
    static final Vector<FakePlayer> midis = new Vector<FakePlayer>();
    static void midiUp() { if (midiPlaying++ == 0) midiSince = now(); }
    static void midiDown() { if (--midiPlaying == 0 && midiSince >= 0) { midiTotal += now() - midiSince; midiSince = -1; } }
    /** Total ms some MIDI was really playing so far. */
    public static long musicMs() { synchronized (eng) { return midiTotal + (midiPlaying > 0 && midiSince >= 0 ? now() - midiSince : 0); } }
    public static int steals, loopEnds;
    static int prefWithMidi, midiStarts;
    static int midiPlaying;
    public static int durScale = 1;
    public static int hangStartAt = -1, MAXPREF = 6;
    static int wavPlaying, startCount, prefetched;
    static boolean mixerLocked;
    public static final List<String> log = Collections.synchronizedList(new ArrayList<String>());

    final String name;
    final boolean midi;
    volatile int state = UNREALIZED;
    int loops = 1, run;
    long lastStop = -1000;
    long playStart, played;                    // ms of the track played (media time)
    boolean hung;
    final Vector<PlayerListener> ls = new Vector<PlayerListener>();

    FakePlayer(String n, boolean m) { name = n.substring(n.lastIndexOf('/') + 1); midi = m; if (m) midis.addElement(this); }

    public static long now() { return System.currentTimeMillis() - T0; }
    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException e) { } }
    void log(String s) { log.add(now() + " " + s + " " + name); }
    void hangIfHung() { if (hung) for (;;) sleep(100000); }

    public void realize() throws MediaException { hangIfHung(); if (state == UNREALIZED) state = REALIZED; }

    public void prefetch() throws MediaException {
        hangIfHung();
        if (state >= PREFETCHED) return;
        synchronized (eng) {
            if (!midi && modelY && midiPlaying > 0 && ++prefWithMidi % 5 == 0) { hung = true; log("HANG-PREFETCH-WITH-MIDI"); }
            if (modelP && prefetched >= 6) { hung = true; log("HANG-TOO-MANY"); }
        }
        hangIfHung();
        sleep(midi ? Manager.createDelayMidi * 2 / 3 : Manager.createDelayWav * 2 / 3);
        synchronized (eng) {
            if (modelC && prefetched >= MAXPREF) { log("PREFETCH-FAIL"); throw new MediaException("no audio resources"); }
            prefetched++;
        }
        state = PREFETCHED;
    }

    static void stealMidi() {
        for (int i = 0; i < midis.size(); i++) {
            FakePlayer m = midis.elementAt(i);
            if (m.state == STARTED) { m.run++; m.played += now() - m.playStart; m.state = PREFETCHED; midiDown(); steals++; m.log("MIDI-STOLEN"); }
        }
    }

    public void start() throws MediaException {
        hangIfHung();
        if (state < PREFETCHED) prefetch();
        if (state == STARTED) return;
        if (!midi && modelR && now() - lastStop < 30) { log("START-LOST"); return; }
        if (!midi && modelM) synchronized (eng) { if (wavPlaying > 0) { log("START-BUSY"); throw new MediaException("busy"); } }
        if (!midi && modelX) synchronized (eng) { if (midiPlaying > 0) { log("START-NOMIX"); throw new MediaException("midi playing"); } }
        if (midi && modelZ) synchronized (eng) { if (++midiStarts == 2) { hung = true; log("HANG-MIDI-START"); } }
        hangIfHung();
        if (midi) synchronized (eng) { midiUp(); }
        if (!midi) {
            synchronized (eng) {
                startCount++;
                if (startCount == hangStartAt) { hung = true; log("HANG-IN-START"); }
            }
            hangIfHung();
            synchronized (eng) {
                if ((modelQ || modelD) && wavPlaying + midiPlaying >= 3) {
                    if (modelQ) stealMidi();
                    else {
                        Thread t = new Thread() { public void run() { FakePlayer.sleep(150); synchronized (eng) { stealMidi(); } } };
                        t.setDaemon(true);
                        t.start();
                    }
                }
                wavPlaying++;
            }
        }
        state = STARTED;
        if (midi && modelL && played >= 8000) played = 0;   // started again at the end: from the top
        playStart = now();
        final int my = ++run;
        log("START");
        final long dur = midi ? (loops == 1 ? 2500 : modelL ? 8000 : -1) : (name.startsWith("v_") ? 1200 : name.startsWith("s_revolver") ? 500 : name.startsWith("s_shotgun") ? 750 : name.startsWith("s_tommy") ? 160 : 350);
        if (dur < 0) return;           // looping music: plays until stopped
        Thread t = new Thread() {
            public void run() {
                FakePlayer.sleep(dur);
                synchronized (eng) {
                    while (mixerLocked && !midi) { try { eng.wait(); } catch (InterruptedException e) { } }
                    if (state != STARTED || run != my) return;
                    state = PREFETCHED;
                    if (!midi) { wavPlaying--; eng.notifyAll(); } else { midiDown(); if (loops != 1) loopEnds++; played = dur; }
                }
                log("END");
                for (int i = 0; i < ls.size(); i++) ls.elementAt(i).playerUpdate(FakePlayer.this, PlayerListener.END_OF_MEDIA, null);
            }
        };
        t.setDaemon(true);
        t.start();
    }

    void midiWaitForMixer() {
        if (!midi || !modelA) return;
        synchronized (eng) {
            if (wavPlaying == 0) return;
            log("WAITING-FOR-MIXER");
            mixerLocked = true;
            while (wavPlaying > 0) { try { eng.wait(); } catch (InterruptedException e) { } }
            mixerLocked = false;
            eng.notifyAll();
        }
    }

    void halt() {
        synchronized (eng) {
            if (state == STARTED) { run++; played += now() - playStart; if (!midi) { wavPlaying--; eng.notifyAll(); } else midiDown(); }
        }
    }

    public void stop() throws MediaException {
        hangIfHung();
        if (state != STARTED) return;
        midiWaitForMixer();
        halt();
        state = PREFETCHED;
        lastStop = now();
        log("STOP");
    }

    public void deallocate() { }

    public void close() {
        hangIfHung();
        if (state == CLOSED) return;
        if (state == STARTED) midiWaitForMixer();
        halt();
        synchronized (eng) { if (state >= PREFETCHED) prefetched--; }
        state = CLOSED;
        log("CLOSE");
    }

    public long setMediaTime(long t) throws MediaException { hangIfHung(); return 0; }
    public long getMediaTime() { return (played + (state == STARTED ? now() - playStart : 0)) * 1000; }
    public int getState() { return state; }
    public long getDuration() { return midi && modelL ? 8000000 : TIME_UNKNOWN; }
    public String getContentType() { return midi ? "audio/midi" : "audio/x-wav"; }
    public void setLoopCount(int c) { loops = c; }
    public void addPlayerListener(PlayerListener l) { ls.addElement(l); }
    public void removePlayerListener(PlayerListener l) { ls.removeElement(l); }
    public Control[] getControls() { return new Control[0]; }
    public Control getControl(String s) { return null; }
}
