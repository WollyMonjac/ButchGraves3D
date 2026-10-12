/** Checks the episode 4 gadgets with the real world code: teleporters, levers, conveyors, shock floors. */
public class Mech {
    static void at(double x, double y, int a) { W.px = (int) (x * 65536); W.py = (int) (y * 65536); W.pa = a; W.pvx = W.pvy = 0; }

    public static void main(String[] a) throws Exception {
        E.load(); W.initColors(); G.quiet = true; W.skill = 1; W.health = 100; W.weapons = 3; W.weapon = 1;
        W.load(13);
        for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; }
        at(50.5, 34.8, 0);
        for (int t = 0; t < 5; t++) W.tick();
        System.out.println("teleport L13 pad(50,34) -> " + (W.px / 65536.0) + "," + (W.py / 65536.0) + " pa " + W.pa + " (want 6.5,13.5 pa 3072)");
        // shock gauntlet
        W.health = 100; at(43.5, 12.5, 3072);
        int hp0 = W.health, on = 0;
        for (int t = 0; t < 300; t++) { W.tick(); W.px = (int) (43.5 * 65536); W.py = (int) (12.5 * 65536); if (W.shockOn) on++; }
        System.out.println("shock floor 300 ticks: hp " + hp0 + " -> " + W.health + ", on for " + on + " ticks, swapped tex " + (E.tex[Res.T_SHOCK] != E.pairOn[0]));
        // conveyors in L14 hall (north belt at x 5..6)
        W.load(14);
        for (int i = 0; i < W.nt; i++) if (W.isMon(W.tType[i])) { W.remove(i); i--; }
        at(5.5, 34.5, 0);
        for (int t = 0; t < 32; t++) W.tick();
        System.out.println("conveyor 32 ticks: y 34.5 -> " + (W.py / 65536.0) + " (want ~33.5)");
        // lever in L14 corridor
        int c9 = (9 << 6) | 40, c17 = (17 << 6) | 40, cl = (11 << 6) | 37;
        System.out.println("L14 before: barrier " + W.wall[c9] + " behind " + W.wall[c17] + " locker " + W.wall[cl]);
        at(38.4, 13.5, 2048); W.use(false);
        System.out.println("L14 after lever: barrier " + W.wall[c9] + " behind " + W.wall[c17] + " locker " + W.wall[cl] + " state " + W.mazeState);
        // L15 maze: start lever
        W.load(15);
        int ca = (1 << 6) | 3, cb = (28 << 6) | 1;
        System.out.println("L15 start: redkey gate " + W.wall[ca] + " Z0-Z1 gate " + W.wall[cb] + " maze cells " + W.nMaze);
        at(1.4, 34.5, 2048); W.use(false);
        System.out.println("L15 lever: redkey gate " + W.wall[ca] + " Z0-Z1 gate " + W.wall[cb] + " state " + W.mazeState);
        W.ticks += 30; W.use(false);
        System.out.println("L15 lever again: redkey gate " + W.wall[ca] + " Z0-Z1 gate " + W.wall[cb] + " state " + W.mazeState);
    }
}
