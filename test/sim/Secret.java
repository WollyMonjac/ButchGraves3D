import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
/** Render a secret pushwall closed, sliding and open: Secret level x y angle outprefix */
public class Secret {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true; W.skill = 1;
        W.load(Integer.parseInt(a[0]));
        W.px = (int) (Double.parseDouble(a[1]) * 65536); W.py = (int) (Double.parseDouble(a[2]) * 65536); W.pa = Integer.parseInt(a[3]);
        for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; }
        int[] ticks = {0, 8, 16, 40};
        int done = 0;
        for (int k = 0; k < ticks.length; k++) {
            while (done < ticks[k]) {
                int sx = W.px, sy = W.py, sa = W.pa;
                W.tick(); done++;
                W.px = sx; W.py = sy; W.pa = sa;
            }
            if (ticks[k] == 0 && k == 0) { }
            W.lightsTick();
            E.setup(240, 320, 278, 0);
            E.buildCmap(0, 0, 0);
            E.px = W.px; E.py = W.py; E.pang = W.pa; E.eyeZ = 32768;
            E.render(); W.collectSprites(); E.drawSprites();
            BufferedImage im = new BufferedImage(E.RW, E.RH, BufferedImage.TYPE_INT_RGB);
            im.setRGB(0, 0, E.RW, E.RH, E.buf, 0, E.RW);
            ImageIO.write(im, "png", new File(a[4] + k + ".png"));
            if (k == 0) {
                int sx = W.px, sy = W.py, sa = W.pa;
                W.px = (int) (Double.parseDouble(a[5]) * 65536); W.py = (int) (Double.parseDouble(a[6]) * 65536); W.pa = Integer.parseInt(a[7]);
                W.use(false);
                W.px = sx; W.py = sy; W.pa = sa;
            }
        }
        System.out.println("secrets " + W.secrets);
    }
}
