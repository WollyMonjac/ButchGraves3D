import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
/**
 * Contact sheet of every weapon frame as the game draws it (same scale, anchor, kick offset and shading as G.drawWeapon),
 * over the real view from a level's start, at several cell light levels.
 * WpnShow level out.png [lights comma list]
 */
public class WpnShow {
    // frame, weapon, kick at the time the frame shows, firing flag
    static final int[][] FR = {
        {0, 0, 0}, {1, 0, 0}, {2, 0, 0},
        {0, 1, 0}, {1, 1, 6},
        {0, 2, 0}, {1, 2, 10}, {2, 2, 0},
        {0, 3, 0}, {1, 3, 4}, {2, 3, 2},
        {0, 4, 0}, {1, 4, 8},
    };

    // mirror of G.drawWeapon (no bob / switch)
    static void draw() {
        int w = W.weapon, f = W.wFrame;
        int s;
        switch (w) {
            case 0: s = f == 1 ? Res.S_W_SHOVEL1 : f == 2 ? Res.S_W_SHOVEL2 : Res.S_W_SHOVEL0; break;
            case 1: s = f == 1 ? Res.S_W_REVOLVER1 : Res.S_W_REVOLVER0; break;
            case 2: s = f == 1 ? Res.S_W_SHOTGUN1 : f == 2 ? Res.S_W_SHOTGUN2 : Res.S_W_SHOTGUN0; break;
            case 3: s = f == 1 ? Res.S_W_TOMMY1 : f == 2 ? Res.S_W_TOMMY2 : Res.S_W_TOMMY0; break;
            default: s = f == 1 ? Res.S_W_LAUNCHER1 : Res.S_W_LAUNCHER0;
        }
        int kw = (E.VW << 16) / 160, kh = (E.VH << 16) / 124;
        int k = (kw < kh ? kw : kh) / E.DX;
        int kk = W.kick > 0 ? W.kick * E.RH / 200 : 0;
        int pc = ((W.py >> 16) << 6) | (W.px >> 16);
        int sh = shade(W.light[pc], w, f);
        int[] tip = {0, 10, 9, 7, -6};
        E.drawScreen(s, E.RW / 2 + (tip[w] * k >> 16), E.RH + kk / 2, k, sh);
    }

    static int shade(int l, int w, int f) {
        int sh = l - 3;
        if (sh > 10) sh = 10;
        if (f != 0 && w != 0) sh -= 6;
        return sh;
    }

    public static void main(String[] a) throws Exception {
        E.load();
        W.initColors();
        G.quiet = true;
        W.skill = 1;
        W.load(Integer.parseInt(a[0]));
        for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; }
        W.lightsTick();
        int detail = Integer.getInteger("detail", 0);
        E.setup(240, 320, 278, detail);
        E.buildCmap(0, 0, 0);
        E.px = W.px; E.py = W.py; E.pang = W.pa; E.eyeZ = 32768;
        E.render();
        W.collectSprites();
        E.drawSprites();
        int[] scene = (int[]) E.buf.clone();
        String[] ls = (a.length > 2 ? a[2] : "-1,14,19,24").split(",");
        int pc = ((W.py >> 16) << 6) | (W.px >> 16);
        int l0 = W.light[pc];
        int cw = E.RW, ch = E.RH / 2;               // bottom half of the view is where the gun is
        BufferedImage out = new BufferedImage(cw * FR.length / 2 + cw, ch * ls.length * 2, BufferedImage.TYPE_INT_RGB);
        for (int li = 0; li < ls.length; li++) {
            int lt = Integer.parseInt(ls[li]);
            W.light[pc] = lt < 0 ? l0 : lt;
            for (int fi = 0; fi < FR.length; fi++) {
                System.arraycopy(scene, 0, E.buf, 0, scene.length);
                W.weapon = FR[fi][1]; W.wFrame = FR[fi][0]; W.kick = FR[fi][2];
                W.bobAmp = 0; W.wSwitch = 0;
                draw();
                int col = fi % 7, row = li * 2 + fi / 7;
                out.setRGB(col * cw, row * ch, cw, ch, E.buf, (E.RH - ch) * E.RW, E.RW);
            }
            System.out.println("row " + li + " light " + W.light[pc]);
        }
        ImageIO.write(out, "png", new File(a[1]));
    }
}
