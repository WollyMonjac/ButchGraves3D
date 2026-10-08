package javax.microedition.media;

import java.util.*;

/**
 * Fake MMAPI player that models the failure modes of real phone firmware:
 *  A  "mixer lock": stopping/closing the MIDI player while a sampled (WAV) sound is playing waits for
 *     the WAV to finish, but the WAV can't finish while the mixer is locked -> permanent deadlock,
 *     unless another thread stops/closes the WAV.
 *  B  "random hang": the Nth WAV start() never returns, and every later call on that player hangs too.
 *  C  "resource limit": only MAXPREF players may be prefetched at once; prefetch() beyond that throws.
 */
public class FakePlayer implements Player {
    public static final long T0 = System.currentTimeMillis();
    public static final Object eng = new Object();
    public static boolean modelA, modelC;
    public static int hangStartAt = -1, MAXPREF = 6;
    static int wavPlaying, startCount, prefetched;
    static boolean mixerLocked;
    public static final List<String> log = Collections.synchronizedList(new ArrayList<String>());

    final String name;
    final boolean midi;
    volatile int state = UNREALIZED;
    int loops = 1, run;
    boolean hung;
    final Vector<PlayerListener> ls = new Vector<PlayerListener>();

    FakePlayer(String n, boolean m) { name = n.substring(n.lastIndexOf('/') + 1); midi = m; }

    public static long now() { return System.currentTimeMillis() - T0; }
    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException e) { } }
    void log(String s) { log.add(now() + " " + s + " " + name); }
    void hangIfHung() { if (hung) for (;;) sleep(100000); }

    public void realize() throws MediaException { hangIfHung(); if (state == UNREALIZED) state = REALIZED; }

    public void prefetch() throws MediaException {
        hangIfHung();
        if (state >= PREFETCHED) return;
        sleep(midi ? Manager.createDelayMidi * 2 / 3 : Manager.createDelayWav * 2 / 3);
        synchronized (eng) {
            if (modelC && prefetched >= MAXPREF) { log("PREFETCH-FAIL"); throw new MediaException("no audio resources"); }
            prefetched++;
        }
        state = PREFETCHED;
    }

    public void start() throws MediaException {
        hangIfHung();
        if (state < PREFETCHED) prefetch();
        if (state == STARTED) return;
        if (!midi) {
            synchronized (eng) {
                startCount++;
                if (startCount == hangStartAt) { hung = true; log("HANG-IN-START"); }
            }
            hangIfHung();
            synchronized (eng) { wavPlaying++; }
        }
        state = STARTED;
        final int my = ++run;
        log("START");
        final long dur = midi ? (loops == 1 ? 2500 : -1) : (name.startsWith("v_") ? 1200 : 250);
        if (dur < 0) return;           // looping music: plays until stopped
        Thread t = new Thread() {
            public void run() {
                FakePlayer.sleep(dur);
                synchronized (eng) {
                    while (mixerLocked && !midi) { try { eng.wait(); } catch (InterruptedException e) { } }
                    if (state != STARTED || run != my) return;
                    state = PREFETCHED;
                    if (!midi) { wavPlaying--; eng.notifyAll(); }
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
            if (state == STARTED) { run++; if (!midi) { wavPlaying--; eng.notifyAll(); } }
        }
    }

    public void stop() throws MediaException {
        hangIfHung();
        if (state != STARTED) return;
        midiWaitForMixer();
        halt();
        state = PREFETCHED;
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
    public long getMediaTime() { return 0; }
    public int getState() { return state; }
    public long getDuration() { return TIME_UNKNOWN; }
    public String getContentType() { return midi ? "audio/midi" : "audio/x-wav"; }
    public void setLoopCount(int c) { loops = c; }
    public void addPlayerListener(PlayerListener l) { ls.addElement(l); }
    public void removePlayerListener(PlayerListener l) { ls.removeElement(l); }
    public Control[] getControls() { return new Control[0]; }
    public Control getControl(String s) { return null; }
}
