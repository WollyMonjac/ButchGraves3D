public class BossPos {
    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true; W.skill = 1;
        W.load(Integer.parseInt(a[0]));
        System.out.println("start " + (W.px / 65536.0) + " " + (W.py / 65536.0) + " " + W.pa);
        for (int i = 0; i < W.nt; i++) if (W.isBoss(W.tType[i])) System.out.println("boss " + W.tType[i] + " " + (W.tX[i] / 65536.0) + " " + (W.tY[i] / 65536.0));
        // map around
        int bx = 0, by = 0;
        for (int i = 0; i < W.nt; i++) if (W.isBoss(W.tType[i])) { bx = W.tX[i] >> 16; by = W.tY[i] >> 16; }
        for (int y = by - 12; y <= by + 12; y++) {
            StringBuilder sb = new StringBuilder();
            for (int x = bx - 16; x <= bx + 16; x++) {
                if (x < 0 || y < 0 || x > 63 || y > 63) { sb.append(' '); continue; }
                int c = (y << 6) | x;
                sb.append(x == bx && y == by ? 'B' : W.wall[c] != 0 ? '#' : '.');
            }
            System.out.println(String.format("%2d ", y) + sb);
        }
    }
}
