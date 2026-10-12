import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
/** One frame of a level for the manual, optionally lit by a lightning flash: Flash level x y angle out.png [flash 0/1] */
public class Flash {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true; W.skill = 1;
        W.load(Integer.parseInt(a[0]));
        for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; }
        W.px = (int) (Double.parseDouble(a[1]) * 65536); W.py = (int) (Double.parseDouble(a[2]) * 65536); W.pa = Integer.parseInt(a[3]);
        W.lightningBoost = a.length > 5 && a[5].equals("0") ? 0 : 15;
        W.lightsTick();
        E.setup(240, 320, 278, 0);
        E.buildCmap(0, 0, W.lightningBoost * 8);
        E.px = W.px; E.py = W.py; E.pang = W.pa; E.eyeZ = 32768;
        E.render();
        W.collectSprites();
        E.drawSprites();
        BufferedImage im = new BufferedImage(E.RW, E.RH, BufferedImage.TYPE_INT_RGB);
        im.setRGB(0, 0, E.RW, E.RH, E.buf, 0, E.RW);
        ImageIO.write(im, "png", new File(a[4]));
    }
}
