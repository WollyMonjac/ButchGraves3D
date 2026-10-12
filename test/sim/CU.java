import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
public class CU {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true;
        W.load(101);
        E.setup(240, 320, 278, 0);
        E.buildCmap(0, 0, 0);
        int s = Res.S_CPBUTCH_1;
        System.out.println("sw " + E.sw[s] + " sh " + E.sh[s] + " sox " + E.sox[s] + " soy " + E.soy[s] + " RW " + E.RW + " RH " + E.RH + " spr " + (E.spr[s] != null));
        int k = (int) (((long) E.RH * 60000) / E.sh[s]);
        java.util.Arrays.fill(E.buf, 0x203040);
        E.drawScreen(s, E.RW / 2, E.RH + 2, k, 4);
        BufferedImage im = new BufferedImage(E.RW, E.RH, BufferedImage.TYPE_INT_RGB);
        im.setRGB(0, 0, E.RW, E.RH, E.buf, 0, E.RW);
        ImageIO.write(im, "png", new File(a[0]));
    }
}
