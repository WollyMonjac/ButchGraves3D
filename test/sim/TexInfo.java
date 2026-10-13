/** Which textures each level has loaded, with their sizes (to pick the screen border's texture). TexInfo [levels...] */
public class TexInfo {
    public static void main(String[] a) throws Exception {
        E.load();
        W.initColors();
        G.quiet = true;
        W.skill = 1;
        for (int lv = 1; lv <= 20; lv++) {
            W.load(lv);
            StringBuffer b = new StringBuffer("L" + lv + ":");
            int[] n = new int[E.tex.length];
            for (int c = 0; c < 4096; c++) { int w = (W.wall[c] & 255) - 1; if (w >= 0 && w < n.length) n[w]++; }
            for (int t = 0; t < E.tex.length; t++)
                if (E.tex[t] != null) b.append(" " + t + "(" + E.texW[t] + "x" + E.texH[t] + (n[t] > 0 ? " w" + n[t] : "") + ")");
            System.out.println(b);
        }
    }
}
