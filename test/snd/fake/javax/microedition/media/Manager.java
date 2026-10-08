package javax.microedition.media;

import java.io.InputStream;

/** Desktop stand-in for MMAPI's Manager: hands out FakePlayers (see FakePlayer for the phone models). */
public final class Manager {
    public static volatile String nextName = "?";   // set by the test's G.open()
    public static int createDelayWav = 40, createDelayMidi = 250;

    public static Player createPlayer(InputStream in, String type) throws java.io.IOException, MediaException {
        String n = nextName;
        boolean midi = type.indexOf("midi") >= 0;
        FakePlayer.sleep(midi ? createDelayMidi / 3 : createDelayWav / 3);
        return new FakePlayer(n, midi);
    }
}
