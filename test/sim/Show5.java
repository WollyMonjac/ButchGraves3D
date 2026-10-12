import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
/**
 * Pose and render one gameplay frame with the real engine (view + weapon), for README screenshots.
 * Showcase level x y angle ticks weapon attackTypes(comma list or -) out.png
 * The world runs `ticks` ticks with the player frozen in god mode (monsters wake up and close in), then the listed monster
 * types are put into their attack pose.
 */
public class Show5 {
    public static void main(String[] a) throws Exception {
        E.load();
        W.initColors();
        G.quiet = true;
        W.skill = 1;
        W.weapons = 31; W.ammo[0] = 120; W.ammo[1] = 30; W.ammo[2] = 10; W.health = 100;
        W.load(Integer.parseInt(a[0]));
        W.px = (int) (Double.parseDouble(a[1]) * 65536);
        W.py = (int) (Double.parseDouble(a[2]) * 65536);
        W.pa = Integer.parseInt(a[3]);
        W.weapon = Integer.parseInt(a[5]);
        W.god = true;
        if (a.length > 8 && a[8].equals("clear")) for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; }
        W.noiseX = W.px; W.noiseY = W.py; W.noiseT = 4;
        if (System.getProperty("trig") != null) W.trigger();
        int ticks = Integer.parseInt(a[4]);
        for (int t = 0; t < ticks; t++) {
            int sx = W.px, sy = W.py, sa = W.pa;
            W.tick();
            W.px = sx; W.py = sy; W.pa = sa; W.pz = 0;
        }
        if (!a[6].equals("-")) {
            // place posed monsters: "type@dist,lateral,pose[,z]" separated by ';' (dist/lateral in cells, pose walk1|walk2|atk|pain)
            for (String e : a[6].split(";")) {
                String[] p = e.split("@");
                int tt = Integer.parseInt(p[0]);
                String[] q = p[1].split(",");
                double d = Double.parseDouble(q[0]), l = Double.parseDouble(q[1]);
                double ang = W.pa * 2 * Math.PI / 4096;
                int x = W.px + (int) ((Math.cos(ang) * d - Math.sin(ang) * l) * 65536), y = W.py + (int) ((Math.sin(ang) * d + Math.cos(ang) * l) * 65536);
                int i = W.spawn(tt, x, y);
                String pose = q[2];
                W.tSt[i] = pose.equals("atk") ? W.ST_ATK : pose.equals("pain") ? W.ST_PAIN : W.ST_CHASE;
                W.tAnim[i] = pose.equals("walk2") ? 7 : 0;
                if (q.length > 3) W.tZ[i] = Integer.parseInt(q[3]);
                if (W.isBoss(tt)) { W.bossIdx = i; W.tHp[i] = W.bossMax * 62 / 100; }
            }
        }
        // drop any projectiles that would sit right in the player's face
        W.flashDmg = 0; W.flashPick = 0; W.kick = 0; W.shake = 0; W.bob = 0;
        W.lightsTick();
        E.setup(240, 320, 278, 0);
        E.buildCmap(0, 0, W.lightningBoost > 0 ? W.lightningBoost * 8 : 0);
        E.px = W.px; E.py = W.py; E.pang = W.pa; E.eyeZ = 32768;
        E.render();
        W.collectSprites();
        E.drawSprites();
        E.drawParticles();
        int w = W.weapon;
        int s = w == 0 ? Res.S_W_SHOVEL0 : w == 1 ? Res.S_W_REVOLVER0 : w == 2 ? Res.S_W_SHOTGUN0 : w == 3 ? Res.S_W_TOMMY0 : Res.S_W_LAUNCHER0;
        int kw = (E.VW << 16) / 160, kh = (E.VH << 16) / 124, k = (kw < kh ? kw : kh) / E.DX;
        int pc = ((W.py >> 16) << 6) | (W.px >> 16);
        int[] tip = {0, 10, 9, 7, -6};
        E.drawScreen(s, E.RW / 2 + (tip[w] * k >> 16), E.RH, k, Math.min(W.light[pc] - 3, 10));
        BufferedImage im = new BufferedImage(E.RW, E.RH, BufferedImage.TYPE_INT_RGB);
        im.setRGB(0, 0, E.RW, E.RH, E.buf, 0, E.RW);
        ImageIO.write(im, "png", new File(a[7]));
        int bi = W.bossIdx;
        System.out.println("boss " + (bi >= 0 && W.isBoss(W.tType[bi]) ? (W.tHp[bi] * 100 / W.bossMax) : -1));
    }
}
