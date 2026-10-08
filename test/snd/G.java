/** Test stand-in for the game canvas: only what Snd needs. */
final class G {
    static java.io.InputStream open(String p) {
        if (p.endsWith(".txt")) return null;       // no sounds.txt -> default file names
        javax.microedition.media.Manager.nextName = p;
        return new java.io.ByteArrayInputStream(new byte[64]);
    }
}
