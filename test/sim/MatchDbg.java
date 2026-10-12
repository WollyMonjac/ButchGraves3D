import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
public class MatchDbg {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true; W.skill = 1;
        W.load(Integer.parseInt(a[0]));
        if (System.getProperty("trig") != null) { W.god = true; W.trigger(); for (int t = 0; t < 120; t++) { int sx = W.px, sy = W.py; W.tick(); W.px = sx; W.py = sy; } }
        W.lightsTick();
        BufferedImage im = ImageIO.read(new File(a[1]));
        Match.class.getName();
        int W3 = 80, H3 = 92;
        E.setup(W3, H3 + 20, H3, 0); E.buildCmap(0, 0, 0); E.eyeZ = 32768;
        E.px = (int) (Double.parseDouble(a[2]) * 65536); E.py = (int) (Double.parseDouble(a[3]) * 65536); E.pang = Integer.parseInt(a[4]);
        E.render();
        BufferedImage o = new BufferedImage(W3 * 2, H3, BufferedImage.TYPE_INT_RGB);
        o.setRGB(0, 0, W3, H3, E.buf, 0, W3);
        for (int y = 0; y < H3; y++) for (int x = 0; x < W3; x++) {
            int r = 0, g = 0, b = 0;
            for (int dy = 0; dy < 3; dy++) for (int dx = 0; dx < 3; dx++) { int p = im.getRGB(x * 3 + dx, y * 3 + dy); r += (p >> 16) & 255; g += (p >> 8) & 255; b += p & 255; }
            o.setRGB(W3 + x, y, ((r / 9) << 16) | ((g / 9) << 8) | (b / 9));
        }
        ImageIO.write(o, "png", new File(a[5]));
    }
}
