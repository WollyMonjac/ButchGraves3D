import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
/** Render one frame of the real engine to a PNG: Shot level x y angle out.png */
public class Shot {
    public static void main(String[] a) throws Exception {
        E.load();
        W.initColors();
        W.load(Integer.parseInt(a[0]));
        W.px = (int) (Double.parseDouble(a[1]) * 65536);
        W.py = (int) (Double.parseDouble(a[2]) * 65536);
        W.pa = Integer.parseInt(a[3]);
        W.lightsTick();
        E.setup(240, 320, 278, 0);
        E.buildCmap(0, 0, 0);
        E.px = W.px; E.py = W.py; E.pang = W.pa; E.eyeZ = 32768;
        E.render();
        W.collectSprites();
        E.drawSprites();
        BufferedImage im = new BufferedImage(E.RW, E.RH, BufferedImage.TYPE_INT_RGB);
        im.setRGB(0, 0, E.RW, E.RH, E.buf, 0, E.RW);
        ImageIO.write(im, "png", new File(a[4]));
    }
}
