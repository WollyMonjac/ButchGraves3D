/** How much faster a shrunk view draws (Options -> screen size): times the real renderer (walls, floors, sprites) over a
 *  full turn in a level at each size and detail, on a 240x320 screen. Speed [level] */
public class Speed {
    public static void main(String[] a) throws Exception {
        int lv = a.length > 0 ? Integer.parseInt(a[0]) : 1;
        E.load();
        W.initColors();
        G.quiet = true;
        W.skill = 1;
        W.load(lv);
        W.lightsTick();
        int SW = 240, AH = 320 - 42;
        int[] pct = {100, 90, 80, 70, 60};
        String[] det = {"HIGH", "MEDIUM", "LOW"};
        for (int d = 0; d < 3; d++) {
            long base = 0;
            StringBuffer b = new StringBuffer(det[d] + ":");
            for (int k = 0; k < pct.length; k++) {
                int vw = SW, vh = AH;
                if (pct[k] < 100) { vw = (SW * pct[k] / 100) & ~1; vh = (AH * pct[k] / 100) & ~1; }
                E.setup(vw, 320, vh, d);
                E.buildCmap(0, 0, 0);
                E.eyeZ = 32768;
                E.px = W.px; E.py = W.py;
                for (int w = 0; w < 40; w++) frame(w);                 // warm up
                long t0 = System.nanoTime();
                int n = 600;
                for (int f = 0; f < n; f++) frame(f);
                long ns = (System.nanoTime() - t0) / n;
                if (k == 0) base = ns;
                b.append(String.format("  %d%% %.2f ms (x%.2f)", pct[k], ns / 1e6, (double) base / ns));
            }
            System.out.println(b);
        }
    }

    static void frame(int f) {
        E.pang = (f * 4096 / 300) & 4095;
        E.render();
        W.collectSprites();
        E.drawSprites();
    }
}
