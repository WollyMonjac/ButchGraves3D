final class W {
    static int px, py, ticks, lastPain = -1000;
    static boolean painLimit = System.getProperty("painlimit") != null;
    /** Butch's pain grunt: the game allows one every 5 seconds. */
    static boolean painOk(int t) {
        if (!painLimit) return true;
        if (t - lastPain < 100) return false;
        lastPain = t;
        return true;
    }
}
