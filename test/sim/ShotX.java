import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
/** Render frames of the real engine: ShotX level x y angle ticks trig(0/1) out.png [x y angle out2.png ...]
 *  The world runs `ticks` ticks first (player frozen, god mode); trig=1 fires the level trigger before that. */
public class ShotX {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true; W.skill = 1; W.god = true;
        W.load(Integer.parseInt(a[0]));
        W.px = (int) (Double.parseDouble(a[1]) * 65536); W.py = (int) (Double.parseDouble(a[2]) * 65536); W.pa = Integer.parseInt(a[3]);
        if (a[5].equals("1")) W.trigger();
        int ticks = Integer.parseInt(a[4]);
        for (int t = 0; t < ticks; t++) { int sx = W.px, sy = W.py, sa = W.pa; W.tick(); W.px = sx; W.py = sy; W.pa = sa; W.pz = 0; }
        E.setup(240, 320, 278, 0);
        for (int k = 6; k < a.length; k += 4) {
            if (k > 6) { W.px = (int) (Double.parseDouble(a[k - 3]) * 65536); W.py = (int) (Double.parseDouble(a[k - 2]) * 65536); W.pa = Integer.parseInt(a[k - 1]); }
            W.lightsTick();
            E.buildCmap(0, 0, 0); E.curTint = -1; E.buildCmap(0, 0, 0);
            E.px = W.px; E.py = W.py; E.pang = W.pa; E.eyeZ = 32768; E.lastEye = -1;
            E.render(); W.collectSprites(); E.drawSprites(); E.drawParticles();
            BufferedImage im = new BufferedImage(E.RW, E.RH, BufferedImage.TYPE_INT_RGB);
            im.setRGB(0, 0, E.RW, E.RH, E.buf, 0, E.RW);
            ImageIO.write(im, "png", new File(a[k]));
        }
    }
}
