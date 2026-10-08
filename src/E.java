import java.io.DataInputStream;
import java.io.IOException;
import javax.microedition.lcdui.Graphics;

/**
 * Assets + software renderer: fixed-point DDA raycaster with thin sliding doors,
 * textured floors/ceilings, panoramic sky, fog colormaps, per-cell lighting and
 * z-buffered billboard sprites. Everything is integer math (no floats: CLDC 1.0 safe).
 */
final class E {
    // ------------------------------------------------------------------ assets
    static final int[] pal = new int[256];
    static final int[] SIN = new int[4096];
    static short[] ATAN;
    static byte[][] tex;
    static int[] texW, texH;
    static byte[][] spr;
    static short[] sw, sh, sox, soy;
    static short[][] sTop, sBot;
    static final int PPU = 96;            // sprite pixels per world unit

    static void load() throws IOException {
        DataInputStream in = new DataInputStream(G.open("/d.bin"));
        in.readInt();
        in.readShort();
        for (int i = 0; i < 256; i++) {
            int r = in.readUnsignedByte(), g = in.readUnsignedByte(), b = in.readUnsignedByte();
            pal[i] = (r << 16) | (g << 8) | b;
        }
        int nq = in.readShort();
        int[] q = new int[nq];
        for (int i = 0; i < nq; i++) q[i] = in.readInt();
        for (int a = 0; a < 4096; a++) {
            int k = a & 1023, quad = a >> 10, v;
            if (quad == 0) v = q[k];
            else if (quad == 1) v = q[1024 - k];
            else if (quad == 2) v = -q[k];
            else v = -q[1024 - k];
            SIN[a] = v;
        }
        int na = in.readShort();
        ATAN = new short[na];
        for (int i = 0; i < na; i++) ATAN[i] = in.readShort();
        int nt = in.readShort();
        tex = new byte[nt][];
        texW = new int[nt];
        texH = new int[nt];
        for (int i = 0; i < nt; i++) {
            int w = in.readShort(), h = in.readShort();
            texW[i] = w;
            texH[i] = h;
            tex[i] = new byte[w * h];
            in.readFully(tex[i]);
        }
        int ns = in.readShort();
        spr = new byte[ns][];
        sw = new short[ns]; sh = new short[ns]; sox = new short[ns]; soy = new short[ns];
        sTop = new short[ns][];
        sBot = new short[ns][];
        for (int i = 0; i < ns; i++) {
            int w = in.readShort(), h = in.readShort();
            sw[i] = (short) w; sh[i] = (short) h;
            sox[i] = in.readShort(); soy[i] = in.readShort();
            byte[] d = new byte[w * h];
            in.readFully(d);
            spr[i] = d;
            short[] t = new short[w], b = new short[w];
            for (int x = 0; x < w; x++) {
                int o = x * h, y0 = 0, y1 = h;
                while (y0 < h && d[o + y0] == 0) y0++;
                while (y1 > y0 && d[o + y1 - 1] == 0) y1--;
                t[x] = (short) y0;
                b[x] = (short) y1;
            }
            sTop[i] = t;
            sBot[i] = b;
        }
        in.close();
    }

    static int sin(int a) { return SIN[a & 4095]; }
    static int cos(int a) { return SIN[(a + 1024) & 4095]; }

    /** atan2 in 4096-units (0 = +x, 1024 = +y). */
    static int atan2(int y, int x) {
        if (x == 0 && y == 0) return 0;
        int ax = x < 0 ? -x : x, ay = y < 0 ? -y : y, a;
        if (ax >= ay) a = ATAN[(int) (((long) ay << 10) / ax)];
        else a = 1024 - ATAN[(int) (((long) ax << 10) / ay)];
        if (x < 0) a = 2048 - a;
        if (y < 0) a = -a;
        return a & 4095;
    }

    static int isqrt(int n) {
        if (n <= 0) return 0;
        int x = n, y = (x + 1) >> 1;
        while (y < x) { x = y; y = (x + n / x) >> 1; }
        return x;
    }

    /** Distance of a Q16 vector, result Q16. */
    static int dist(int dx, int dy) {
        long s = (long) dx * dx + (long) dy * dy;
        // sqrt of Q32 -> Q16
        long x = s, r = 0, bit = 1L << 62;
        while (bit > x) bit >>= 2;
        while (bit != 0) {
            if (x >= r + bit) { x -= r + bit; r = (r >> 1) + bit; } else r >>= 1;
            bit >>= 2;
        }
        return (int) r;
    }

    // ------------------------------------------------------------------ colormaps
    static final int NSH = 32;
    static final int[] cmap = new int[NSH * 256];
    static final int[] skyPal = new int[256];
    static int fogR, fogG, fogB;
    static int curTint = -1, curTintAmt = -1, curBright = -1;

    static void setFog(int r, int g, int b) {
        fogR = r; fogG = g; fogB = b;
        curTint = -1;
    }

    /** Rebuild the shading tables. tint 0xRRGGBB mixed by amt/256, bright adds amt/256 light. */
    static void buildCmap(int tint, int amt, int bright) {
        if (tint == curTint && amt == curTintAmt && bright == curBright) return;
        curTint = tint; curTintAmt = amt; curBright = bright;
        int tr = (tint >> 16) & 255, tg = (tint >> 8) & 255, tb = tint & 255;
        for (int s = 0; s < NSH; s++) {
            int f = (31 - s) * 256 / 31;
            int f2 = (f * f + f * 256) >> 9;
            int o = s << 8;
            for (int i = 0; i < 256; i++) {
                int c = pal[i];
                int r = (c >> 16) & 255, g = (c >> 8) & 255, b = c & 255;
                if (i < Res.FB0) {
                    r = (r * f2 + fogR * (256 - f2)) >> 8;
                    g = (g * f2 + fogG * (256 - f2)) >> 8;
                    b = (b * f2 + fogB * (256 - f2)) >> 8;
                }
                if (bright > 0) {
                    r += (r * bright >> 8) + (bright >> 4); g += (g * bright >> 8) + (bright >> 4); b += (b * bright >> 8) + (bright >> 4);
                    if (r > 255) r = 255;
                    if (g > 255) g = 255;
                    if (b > 255) b = 255;
                }
                if (amt > 0) {
                    r += (tr - r) * amt >> 8; g += (tg - g) * amt >> 8; b += (tb - b) * amt >> 8;
                }
                cmap[o | i] = (r << 16) | (g << 8) | b;
            }
        }
        for (int i = 0; i < 256; i++) {
            int c = pal[i];
            int r = (c >> 16) & 255, g = (c >> 8) & 255, b = c & 255;
            if (bright > 0) {
                r += r * bright >> 7; g += g * bright >> 7; b += b * bright >> 7;
                if (r > 255) r = 255;
                if (g > 255) g = 255;
                if (b > 255) b = 255;
            }
            if (amt > 0) { r += (tr - r) * amt >> 8; g += (tg - g) * amt >> 8; b += (tb - b) * amt >> 8; }
            skyPal[i] = (r << 16) | (g << 8) | b;
        }
    }

    /** Find the palette index closest to an RGB colour (range lo..hi). */
    static int nearest(int rgb, int lo, int hi) {
        int r = (rgb >> 16) & 255, g = (rgb >> 8) & 255, b = rgb & 255, best = lo, bd = 1 << 30;
        for (int i = lo; i < hi; i++) {
            int c = pal[i];
            int dr = ((c >> 16) & 255) - r, dg = ((c >> 8) & 255) - g, db = (c & 255) - b;
            int d = dr * dr + dg * dg + db * db;
            if (d < bd) { bd = d; best = i; }
        }
        return best;
    }

    // ------------------------------------------------------------------ view setup
    static int SW, SH, VW, VH, RW, RH, DX = 2, DY = 1;
    static int[] buf, strip;
    static int[] camX, colAng, zbuf, wtop, wbot, rowDist, rowShd, skyCB, skyRI;
    static int proj, projY, hor;
    static final int KQ = 42560;                 // tan(33 deg) in Q16 -> 66 degree FOV
    static final int[] SHC = new int[160];       // clamp shade sums -> cmap offsets
    static int fogK = 18;

    static void setup(int sw_, int sh_, int vh, int detail) {
        SW = sw_; SH = sh_; VW = sw_; VH = vh;
        DX = detail == 0 ? 1 : 2;
        DY = detail == 2 ? 2 : 1;
        RW = (VW + DX - 1) / DX;
        RH = (VH + DY - 1) / DY;
        buf = null; strip = null;
        System.gc();
        buf = new int[RW * RH];
        if (DX > 1 || DY > 1) strip = new int[VW * 16];
        camX = new int[RW]; colAng = new int[RW]; zbuf = new int[RW]; wtop = new int[RW]; wbot = new int[RW]; skyCB = new int[RW];
        rowDist = new int[RH]; rowShd = new int[RH]; skyRI = new int[RH];
        proj = (int) (((long) RW << 15) / KQ);
        projY = proj * DX / DY;
        hor = RH / 2;
        for (int x = 0; x < RW; x++) {
            camX[x] = (int) ((((long) (2 * x + 1 - RW)) << 16) / RW);
            int t = (int) ((long) camX[x] * KQ >> 16);          // tan of the column angle, Q16
            int at = t < 0 ? -t : t;
            int a = at >= 65536 ? 512 : ATAN[at >> 6];
            colAng[x] = t < 0 ? -a : a;
        }
        for (int i = 0; i < SHC.length; i++) SHC[i] = (i > 31 ? 31 : i) << 8;
        lastEye = -1;
    }

    // ------------------------------------------------------------------ frame state
    static int px, py, pang, eyeZ, lastEye = -1, bobY;
    static final int UNIT = 65536;

    static void setRows() {
        if (eyeZ == lastEye) return;
        lastEye = eyeZ;
        for (int y = 0; y < RH; y++) {
            int d;
            if (y > hor) d = (int) (((long) eyeZ * projY * 2) / (2 * (y - hor) + 1));
            else if (y < hor) d = (int) (((long) (UNIT - eyeZ) * projY * 2) / (2 * (hor - y) - 1));
            else d = 64 << 16;
            rowDist[y] = d;
            int s = (int) (((long) d * fogK) >> 20);
            rowShd[y] = s > 40 ? 40 : s;
        }
    }

    // ------------------------------------------------------------------ world raycast
    static int dirX, dirY, plX, plY;

    static void render() {
        final byte[] wall = W.wall, flag = W.flag, flr = W.flr, cel = W.cel;
        final int[] door = W.door, light = W.light;
        final byte[] seen = W.seen;
        final int[] buf = E.buf, cmap = E.cmap, zb = zbuf, wt = wtop, wb = wbot, SHC = E.SHC;
        final byte[][] tex = E.tex;
        final int RW = E.RW, RH = E.RH;
        dirX = cos(pang); dirY = sin(pang);
        plX = (int) ((long) -dirY * KQ >> 16);
        plY = (int) ((long) dirX * KQ >> 16);
        setRows();
        final int px = E.px, py = E.py, hor = E.hor, projY = E.projY, eyeZ = E.eyeZ;
        final int fk = fogK;
        int doorframe = Res.T_DOORFRAME;
        for (int x = 0; x < RW; x++) {
            int rdx = dirX + (int) ((long) plX * camX[x] >> 16);
            int rdy = dirY + (int) ((long) plY * camX[x] >> 16);
            int mx = px >> 16, my = py >> 16;
            int ddx = rdx == 0 ? 0x1fffffff : (int) ((1L << 32) / (rdx < 0 ? -rdx : rdx));
            int ddy = rdy == 0 ? 0x1fffffff : (int) ((1L << 32) / (rdy < 0 ? -rdy : rdy));
            if (ddx > 0x1fffffff) ddx = 0x1fffffff;
            if (ddy > 0x1fffffff) ddy = 0x1fffffff;
            int stx, sty, sdx, sdy;
            if (rdx < 0) { stx = -1; sdx = (int) (((long) (px & 0xffff) * ddx) >> 16); }
            else { stx = 1; sdx = (int) (((long) (0x10000 - (px & 0xffff)) * ddx) >> 16); }
            if (rdy < 0) { sty = -1; sdy = (int) (((long) (py & 0xffff) * ddy) >> 16); }
            else { sty = 1; sdy = (int) (((long) (0x10000 - (py & 0xffff)) * ddy) >> 16); }
            int side = 0, perp = 0, texId = 0, u = 0, prev = (my << 6) | mx, c = prev;
            boolean hit = false;
            for (int step = 0; step < 72; step++) {
                prev = c;
                if (sdx < sdy) { sdx += ddx; mx += stx; side = 0; } else { sdy += ddy; my += sty; side = 1; }
                if (mx < 0 || my < 0 || mx > 63 || my > 63) break;
                c = (my << 6) | mx;
                seen[c] = 1;
                int w = wall[c];
                if (w == 0) continue;
                int fl = flag[c];
                if ((fl & W.F_DOOR) != 0) {
                    int op = door[c];
                    if (side == 0) {
                        int dm = sdx - ddx + (ddx >> 1);
                        if (dm >= sdy) continue;
                        int wy = py + (int) ((long) dm * rdy >> 16);
                        int fr = wy & 0xffff;
                        if (fr < op) continue;
                        perp = dm;
                        u = ((fr - op) >> 10) & 63;
                        if (rdx < 0) u = 63 - u;
                    } else {
                        int dm = sdy - ddy + (ddy >> 1);
                        if (dm >= sdx) continue;
                        int wx = px + (int) ((long) dm * rdx >> 16);
                        int fr = wx & 0xffff;
                        if (fr < op) continue;
                        perp = dm;
                        u = ((fr - op) >> 10) & 63;
                        if (rdy > 0) u = 63 - u;
                    }
                    texId = (w & 255) - 1;
                    hit = true;
                    prev = c;
                    break;
                }
                perp = side == 0 ? sdx - ddx : sdy - ddy;
                int wc;
                if (side == 0) wc = py + (int) ((long) perp * rdy >> 16);
                else wc = px + (int) ((long) perp * rdx >> 16);
                u = (wc >> 10) & 63;
                if (side == 0 && rdx < 0) u = 63 - u;
                if (side == 1 && rdy > 0) u = 63 - u;
                texId = (w & 255) - 1;
                if ((flag[prev] & (W.F_DOOR | W.F_SECRET)) == W.F_DOOR) texId = doorframe;
                hit = true;
                break;
            }
            if (!hit || perp < 256) perp = perp < 256 ? 256 : 64 << 16;
            zb[x] = perp;
            int top = hor - (int) (((long) (UNIT - eyeZ) * projY) / perp);
            int bot = hor + (int) (((long) eyeZ * projY) / perp);
            int ys = top < 0 ? 0 : top, ye = bot > RH ? RH : bot;
            wt[x] = ys;
            wb[x] = ye;
            if (!hit) { wt[x] = hor; wb[x] = hor; continue; }
            int s = (int) (((long) perp * fk) >> 20) + light[prev] + (side == 1 ? 2 : 0);
            int so = SHC[s < 0 ? 0 : s];
            byte[] t = tex[texId];
            int base = u << 6;
            int stp = (int) (((long) perp << 6) / projY);
            int tp = (ys - top) * stp;
            int o = ys * RW + x;
            for (int y = ys; y < ye; y++) {
                buf[o] = cmap[so | (t[base + ((tp >> 16) & 63)] & 255)];
                tp += stp;
                o += RW;
            }
        }
        // ---------------- floors and ceilings (row casting)
        int rd0x = dirX - plX, rd0y = dirY - plY, rd1x = dirX + plX, rd1y = dirY + plY;
        byte[] sky = W.skyTex >= 0 ? tex[W.skyTex] : null;
        int skyH = W.skyTex >= 0 ? texH[W.skyTex] : 1;
        if (sky != null) {
            for (int x = 0; x < RW; x++) skyCB[x] = (((pang + colAng[x]) & 4095) >> 3) * skyH;
            for (int y = 0; y < hor; y++) {
                int r = skyH - 1 - (hor - y) * (skyH - 1) / (hor > 0 ? hor : 1);
                skyRI[y] = r < 0 ? 0 : r;
            }
        }
        final int[] skyPal = E.skyPal;
        for (int y = 0; y < RH; y++) {
            if (y == hor) {
                continue;
            }
            int d = rowDist[y];
            int fx = px + (int) ((long) d * rd0x >> 16);
            int fy = py + (int) ((long) d * rd0y >> 16);
            int sx = (int) (((long) d * (rd1x - rd0x) >> 16) / RW);
            int sy = (int) (((long) d * (rd1y - rd0y) >> 16) / RW);
            int rs = rowShd[y];
            int o = y * RW;
            if (y > hor) {
                for (int x = 0; x < RW; x++, o++, fx += sx, fy += sy) {
                    if (y < wb[x]) continue;
                    int c = (((fy >> 16) & 63) << 6) | ((fx >> 16) & 63);
                    byte[] t = tex[flr[c]];
                    buf[o] = cmap[SHC[rs + light[c]] | (t[((fx >> 4) & 0xfc0) | ((fy >> 10) & 63)] & 255)];
                }
            } else {
                int sr = sky != null ? skyRI[y] : 0;
                for (int x = 0; x < RW; x++, o++, fx += sx, fy += sy) {
                    if (y >= wt[x]) continue;
                    int c = (((fy >> 16) & 63) << 6) | ((fx >> 16) & 63);
                    int ce = cel[c] & 255;
                    if (ce == 255) {
                        if (sky != null) buf[o] = skyPal[sky[skyCB[x] + sr] & 255];
                        else buf[o] = 0;
                        continue;
                    }
                    byte[] t = tex[ce];
                    buf[o] = cmap[SHC[rs + light[c]] | (t[((fx >> 4) & 0xfc0) | ((fy >> 10) & 63)] & 255)];
                }
            }
        }
        // the horizon row: copy from neighbour to avoid a seam
        if (hor > 0 && hor < RH) {
            int o = hor * RW;
            for (int x = 0; x < RW; x++) if (hor < wt[x] || hor >= wb[x]) buf[o + x] = buf[o + x - RW];
        }
    }

    // ------------------------------------------------------------------ sprites
    static final int MAXV = 160;
    static final int[] vS = new int[MAXV], vX = new int[MAXV], vY = new int[MAXV], vZ = new int[MAXV], vK = new int[MAXV],
            vF = new int[MAXV], vD = new int[MAXV], vL = new int[MAXV], vOrd = new int[MAXV];
    static int nv;
    static final int VF_TRANS = 1, VF_BRIGHT = 2;

    static void addSprite(int s, int x, int y, int z, int scale, int flags, int lightShade) {
        if (nv >= MAXV || s < 0) return;
        int dx = x - px, dy = y - py;
        int depth = (int) (((long) dx * dirX + (long) dy * dirY) >> 16);
        if (depth < 9000 || depth > (40 << 16)) return;
        vS[nv] = s; vX[nv] = x; vY[nv] = y; vZ[nv] = z; vK[nv] = scale; vF[nv] = flags; vD[nv] = depth; vL[nv] = lightShade;
        nv++;
    }

    static void drawSprites() {
        // sort far to near (insertion sort on indices)
        for (int i = 0; i < nv; i++) vOrd[i] = i;
        for (int i = 1; i < nv; i++) {
            int k = vOrd[i], d = vD[k], j = i - 1;
            while (j >= 0 && vD[vOrd[j]] < d) { vOrd[j + 1] = vOrd[j]; j--; }
            vOrd[j + 1] = k;
        }
        final int[] buf = E.buf, cmap = E.cmap, zb = zbuf;
        final int RW = E.RW, RH = E.RH;
        for (int n = 0; n < nv; n++) {
            int i = vOrd[n];
            int s = vS[i], depth = vD[i];
            int dx = vX[i] - px, dy = vY[i] - py;
            int lat = (int) (((long) dx * -dirY + (long) dy * dirX) >> 16);
            int sx = RW / 2 + (int) ((long) lat * proj / depth);
            // buffer px per sprite px (Q16)
            long ppu = ((long) proj << 32) / depth;                 // Q16 px per unit
            int kx = (int) (ppu * vK[i] / (PPU * 256));
            int ky = kx * DX / DY;
            if (kx < 64) continue;
            int w = sw[s], h = sh[s];
            int floorY = hor + (int) (((long) (eyeZ - vZ[i]) * projY) / depth);
            int left = sx - (int) ((long) sox[s] * kx >> 16);
            int top = floorY - (int) ((long) soy[s] * ky >> 16);
            int scrW = (int) ((long) w * kx >> 16), scrH = (int) ((long) h * ky >> 16);
            if (left >= RW || left + scrW <= 0 || top >= RH || top + scrH <= 0) continue;
            int ikx = (int) ((1L << 32) / kx), iky = (int) ((1L << 32) / ky);
            int sd = (int) (((long) depth * fogK) >> 20) + vL[i];
            if ((vF[i] & VF_BRIGHT) != 0) sd = 0;
            int so = SHC[sd < 0 ? 0 : sd];
            boolean trans = (vF[i] & VF_TRANS) != 0;
            byte[] d = spr[s];
            short[] st = sTop[s], sb = sBot[s];
            int c0 = left < 0 ? 0 : left, c1 = left + scrW > RW ? RW : left + scrW;
            int uq = (c0 - left) * ikx;
            for (int c = c0; c < c1; c++, uq += ikx) {
                if (depth >= zb[c]) continue;
                int u = uq >> 16;
                if (u >= w) break;
                int t0 = st[u], t1 = sb[u];
                if (t0 >= t1) continue;
                int y0 = top + (int) ((long) t0 * ky >> 16), y1 = top + (int) ((long) t1 * ky >> 16) + 1;
                if (y0 < 0) y0 = 0;
                if (y1 > RH) y1 = RH;
                int vq = (y0 - top) * iky;
                int base = u * h, o = y0 * RW + c;
                if (!trans) {
                    for (int y = y0; y < y1; y++, vq += iky, o += RW) {
                        int v = vq >> 16;
                        if (v >= h) break;
                        int p = d[base + v] & 255;
                        if (p != 0) buf[o] = cmap[so | p];
                    }
                } else {
                    for (int y = y0; y < y1; y++, vq += iky, o += RW) {
                        int v = vq >> 16;
                        if (v >= h) break;
                        int p = d[base + v] & 255;
                        if (p != 0) buf[o] = ((buf[o] & 0xfefefe) >> 1) + ((cmap[so | p] & 0xfefefe) >> 1);
                    }
                }
            }
        }
        nv = 0;
    }

    /** Particles: tiny z-tested squares. */
    static void drawParticles() {
        final int[] buf = E.buf, zb = zbuf;
        for (int i = 0; i < W.np; i++) {
            int dx = W.pX[i] - px, dy = W.pY[i] - py;
            int depth = (int) (((long) dx * dirX + (long) dy * dirY) >> 16);
            if (depth < 12000) continue;
            int lat = (int) (((long) dx * -dirY + (long) dy * dirX) >> 16);
            int sx = RW / 2 + (int) ((long) lat * proj / depth);
            if (sx < 0 || sx >= RW || depth >= zb[sx]) continue;
            int sy = hor + (int) (((long) (eyeZ - W.pZ[i]) * projY) / depth);
            int sz = (int) (((long) proj * 1200) / depth);
            if (sz < 1) sz = 1;
            if (sz > 3) sz = 3;
            int szy = sz * DX / DY;
            int sd = (int) (((long) depth * fogK) >> 20) + 4;
            int col = W.pC[i] >= Res.FB0 ? cmap[W.pC[i]] : cmap[SHC[sd] | W.pC[i]];
            for (int yy = sy; yy < sy + szy; yy++) {
                if (yy < 0 || yy >= RH) continue;
                int o = yy * RW;
                for (int xx = sx; xx < sx + sz && xx < RW; xx++) buf[o + xx] = col;
            }
        }
    }

    /** Screen-space sprite (weapon). cx = buffer x of anchor, by = buffer y of anchor, k = Q16 scale (buffer px per sprite px). */
    static void drawScreen(int s, int cx, int by, int k, int shade) {
        int w = sw[s], h = sh[s];
        int ky = k * DX / DY;
        int left = cx - (int) ((long) sox[s] * k >> 16), top = by - (int) ((long) soy[s] * ky >> 16);
        int scrW = (int) ((long) w * k >> 16), scrH = (int) ((long) h * ky >> 16);
        int ik = (int) ((1L << 32) / k), iky = (int) ((1L << 32) / ky);
        int so = SHC[shade < 0 ? 0 : shade];
        byte[] d = spr[s];
        int c0 = left < 0 ? 0 : left, c1 = left + scrW > RW ? RW : left + scrW;
        int r0 = top < 0 ? 0 : top, r1 = top + scrH > RH ? RH : top + scrH;
        final int[] buf = E.buf, cmap = E.cmap;
        int uq = (c0 - left) * ik;
        for (int c = c0; c < c1; c++, uq += ik) {
            int u = uq >> 16;
            if (u >= w) break;
            int base = u * h, o = r0 * RW + c, vq = (r0 - top) * iky;
            for (int y = r0; y < r1; y++, vq += iky, o += RW) {
                int v = vq >> 16;
                if (v >= h) break;
                int p = d[base + v] & 255;
                if (p != 0) buf[o] = cmap[so | p];
            }
        }
    }

    /** Copy the render buffer to the screen, upscaling for low detail modes. */
    static void blit(Graphics g) {
        if (DX == 1 && DY == 1) {
            g.drawRGB(buf, 0, RW, 0, 0, RW, RH, false);
            return;
        }
        int rowsPer = 16 / DY;
        int[] st = strip;
        for (int y0 = 0; y0 < RH; y0 += rowsPer) {
            int n = RH - y0 < rowsPer ? RH - y0 : rowsPer;
            int so = 0;
            for (int r = 0; r < n; r++) {
                int bo = (y0 + r) * RW;
                if (DX == 2) {
                    int lim = VW >> 1;
                    for (int x = 0; x < lim; x++) {
                        int p = buf[bo + x];
                        st[so++] = p;
                        st[so++] = p;
                    }
                    if ((VW & 1) != 0) st[so++] = buf[bo + RW - 1];
                } else {
                    System.arraycopy(buf, bo, st, so, VW);
                    so += VW;
                }
                if (DY == 2) {
                    System.arraycopy(st, so - VW, st, so, VW);
                    so += VW;
                }
            }
            int sy = y0 * DY, hgt = n * DY;
            if (sy + hgt > VH) hgt = VH - sy;
            if (hgt > 0) g.drawRGB(st, 0, VW, 0, sy, VW, hgt, false);
        }
    }
}
