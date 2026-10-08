final class G {
    static java.io.InputStream open(String p) {
        try { return new java.io.FileInputStream("/home/claude/bg/res" + p); } catch (Exception e) { return null; }
    }
    static void msg(String s, int c) { System.out.println("  [msg] " + s); }
    static void voice(int id, String t, int gap) { System.out.println("  [voice] " + t); }
    static void face(int k, int t) { }
    static boolean done, won, died;
    static void levelDone() { done = true; System.out.println("  [LEVEL DONE]"); }
    static void victory() { won = true; System.out.println("  [VICTORY]"); }
    static void died() { died = true; System.out.println("  [DIED]"); }
}
