import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
import java.util.*;

/**
 * Find where a screenshot was taken: renders the level's walls, floors and sky from every open spot and direction (at a
 * third of the resolution) and compares with the picture, ignoring the gun's corner and the HUD. Used to re-shoot old
 * README screenshots with new art from exactly the same spot.
 * Match level view.png   (view.png: a 240-wide capture; only its top 278 rows are used)
 * Prints the best spots: x y angle score.
 */
public class Match {
    static final int W3 = 80, H3 = 92;
    static int[] tr = new int[W3 * H3], tg = new int[W3 * H3], tb = new int[W3 * H3];
    static boolean[] use = new boolean[W3 * H3];

    public static void main(String[] a) throws Exception {
        E.load();
        W.initColors();
        G.quiet = true;
        W.skill = 1;
        W.load(Integer.parseInt(a[0]));
        if (System.getProperty("trig") != null) {           // the level after its trigger (the Other World, the boulder)
            W.god = true;
            W.trigger();
            for (int t = 0; t < 120; t++) { int sx = W.px, sy = W.py; W.tick(); W.px = sx; W.py = sy; }
        }
        W.lightsTick();
        BufferedImage im = ImageIO.read(new File(a[1]));
        for (int y = 0; y < H3; y++)
            for (int x = 0; x < W3; x++) {
                int r = 0, g = 0, b = 0;
                for (int dy = 0; dy < 3; dy++)
                    for (int dx = 0; dx < 3; dx++) {
                        int p = im.getRGB(x * 3 + dx, y * 3 + dy);
                        r += (p >> 16) & 255; g += (p >> 8) & 255; b += p & 255;
                    }
                int i = y * W3 + x;
                tr[i] = r / 9; tg[i] = g / 9; tb[i] = b / 9;
                // skip the gun (bottom middle-right), the boss bar strip and the very edges
                use[i] = !(y > 46 && x > 18) && y > 5;
            }
        E.setup(W3, H3 + 20, H3, 0);
        E.buildCmap(0, 0, 0);
        E.eyeZ = 32768;
        List<double[]> best = new ArrayList<double[]>();
        for (int cy = 1; cy < 63; cy++)
            for (int cx = 1; cx < 63; cx++) {
                int c = (cy << 6) | cx;
                if (W.wall[c] != 0) continue;
                for (int sy = 0; sy < 3; sy++)
                    for (int sx = 0; sx < 3; sx++)
                        for (int an = 0; an < 4096; an += 64) {
                            double x = cx + 0.25 + sx * 0.25, y = cy + 0.25 + sy * 0.25;
                            long s = score(x, y, an);
                            keep(best, new double[]{x, y, an, s}, 40);
                        }
            }
        // refine the best few
        List<double[]> fine = new ArrayList<double[]>();
        for (double[] b : best) {
            double[] cur = b.clone();
            for (int pass = 0; pass < 3; pass++) {
                double step = pass == 0 ? 0.08 : pass == 1 ? 0.03 : 0.01;
                int astep = pass == 0 ? 16 : pass == 1 ? 4 : 1;
                double[] bb = cur.clone();
                for (int i = -4; i <= 4; i++)
                    for (int j = -4; j <= 4; j++)
                        for (int k = -6; k <= 6; k++) {
                            double x = cur[0] + i * step, y = cur[1] + j * step;
                            int an = ((int) cur[2] + k * astep) & 4095;
                            int c = (((int) y) << 6) | (int) x;
                            if (x < 1 || y < 1 || x > 63 || y > 63 || W.wall[c] != 0) continue;
                            long s = score(x, y, an);
                            if (s < bb[3]) bb = new double[]{x, y, an, s};
                        }
                cur = bb;
            }
            keep(fine, cur, 10);
        }
        int n = 0;
        for (double[] b : fine) {
            System.out.println(String.format(Locale.US, "%.3f %.3f %d %d", b[0], b[1], (int) b[2], (long) b[3] / 1000));
            if (++n >= 5) break;
        }
    }

    static void keep(List<double[]> l, double[] e, int n) {
        int i = 0;
        while (i < l.size() && l.get(i)[3] <= e[3]) i++;
        if (i >= n) return;
        l.add(i, e);
        if (l.size() > n) l.remove(l.size() - 1);
    }

    static long score(double x, double y, int an) {
        E.px = (int) (x * 65536); E.py = (int) (y * 65536); E.pang = an;
        E.render();
        int[] buf = E.buf;
        long s = 0;
        for (int i = 0; i < W3 * H3; i++) {
            if (!use[i]) continue;
            int p = buf[i];
            int d = Math.abs(((p >> 16) & 255) - tr[i]) + Math.abs(((p >> 8) & 255) - tg[i]) + Math.abs((p & 255) - tb[i]);
            s += d > 150 ? 150 : d;
        }
        return s;
    }
}
