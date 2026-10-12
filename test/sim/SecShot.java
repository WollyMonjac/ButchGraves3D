import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
/** Render the first secret pushwall of a level from 2.5 cells in front: SecShot level index out.png */
public class SecShot {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true; W.skill = 1;
        W.load(Integer.parseInt(a[0]));
        int want = Integer.parseInt(a[1]), k = 0;
        for (int c = 0; c < 4096; c++) {
            if ((W.flag[c] & (W.F_DOOR | W.F_SECRET)) != (W.F_DOOR | W.F_SECRET) || W.wall[c] == 0) continue;
            if (k++ != want) continue;
            int pd = W.push[c], x = c & 63, y = c >> 6;
            // stand in the open on the side the wall is pushed from, as far back as the room allows (max 3 cells)
            int[] dx = {-1, 1, 0, 0}, dy = {0, 0, -1, 1}, an = {0, 2048, 1024, 3072};
            int best = -1, bd = 0;
            for (int j = 0; j < 4; j++) {
                int d = 0;
                if ((W.flag[(y + dy[j]) * 64 + x + dx[j]] & W.F_SECRET) != 0) continue;
                while (d < 3 && W.wall[(y + dy[j] * (d + 1)) * 64 + x + dx[j] * (d + 1)] == 0) d++;
                if (d > bd) { bd = d; best = j; }
            }
            if (best < 0) continue;
            W.px = (int) ((x + 0.5 + dx[best] * (bd - 0.3)) * 65536); W.py = (int) ((y + 0.5 + dy[best] * (bd - 0.3)) * 65536);
            W.pa = an[best];
            for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; }
            W.lightsTick();
            E.setup(240, 320, 278, 0);
            E.buildCmap(0, 0, 0);
            E.px = W.px; E.py = W.py; E.pang = W.pa; E.eyeZ = 32768;
            E.render(); W.collectSprites(); E.drawSprites();
            BufferedImage im = new BufferedImage(E.RW, E.RH, BufferedImage.TYPE_INT_RGB);
            im.setRGB(0, 0, E.RW, E.RH, E.buf, 0, E.RW);
            ImageIO.write(im, "png", new File(a[2]));
            System.out.println("L" + a[0] + " secret at " + x + "," + y + " push " + pd);
            return;
        }
        System.out.println("none");
    }
}
