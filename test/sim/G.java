final class G {
    static java.io.InputStream open(String p) {
        try { return new java.io.FileInputStream("/home/claude/bg/res" + p); } catch (Exception e) { return null; }
    }
    static boolean quiet, gore;
    static void msg(String s, int c) { if (!quiet) System.out.println("  [msg] " + s); }
    static void tip(String s) { msg(s, 0); }
    static void voice(int id, String t, int gap) { if (!quiet) System.out.println("  [voice] " + t); }
    static void face(int k, int t) { }
    static boolean done, won, died;
    static void levelDone() { done = true; if (!quiet) System.out.println("  [LEVEL DONE]"); }
    static void victory() { won = true; if (!quiet) System.out.println("  [VICTORY]"); }
    static void died() { died = true; if (!quiet) System.out.println("  [DIED]"); }
}
