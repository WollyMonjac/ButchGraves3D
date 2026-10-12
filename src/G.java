import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.game.GameCanvas;
import javax.microedition.lcdui.game.Sprite;
import javax.microedition.rms.RecordStore;

/** The game canvas: main loop, input, menus, story, HUD and state machine. */
final class G extends GameCanvas implements Runnable {
    static G g;
    static BG midlet;
    static boolean running = true, paused;
    static int SW, SH, hudH;

    // ------------------------------------------------------------------ states
    static final int S_LOAD = 0, S_TITLE = 1, S_SKILL = 2, S_STORY = 3, S_CARD = 4, S_PLAY = 5, S_PAUSE = 6, S_MAP = 7,
            S_OPT = 8, S_HELP = 9, S_INTER = 10, S_DEAD = 11, S_END = 12, S_EPI = 13, S_CUT = 14, S_TEST = 15;
    static int state = S_LOAD, prevState, sel, tick, stateTick, loadPct;
    static int optReturn;
    // options
    static int detail = 1;
    static boolean vibe = true, crosshair = true, showFps;
    // progress
    static boolean hasSave;
    static int saveLevel = 1, saveSkill = 1;
    static int[] lvStart = new int[9];     // health, armor, weapons, weapon, ammo0..2, skill, level

    // ------------------------------------------------------------------ input
    static final int K_UP = 1, K_DOWN = 2, K_LEFT = 4, K_RIGHT = 8, K_FIRE = 16, K_SL = 32, K_SR = 64, K_USE = 128, K_PREV = 256,
            K_NEXT = 512, K_MAP = 1024, K_JUMP = 2048, K_MENU = 4096, K_BACK = 8192;
    static int keys, pressed;

    // ------------------------------------------------------------------ images & fonts
    static Image hudBg, meltImg;
    static int meltT;
    static int[] meltOff;
    static Image imgTitle, imgLogo, imgDig, imgIcons, imgDigS;
    static Image[] imgFace = new Image[5];
    static int digW, digH, digSW, digSH, faceSz;
    static Font fBig, fMed, fSmall;
    static int[] shade;

    // ------------------------------------------------------------------ messages
    static String[] msgs = new String[3];
    static int[] msgCol = new int[3], msgT = new int[3];
    static String subtitle;
    static int subT, faceKind, faceT, cardT;
    static long fpsT;
    static int fpsN, fps;

    G() {
        super(false);
        setFullScreenMode(true);
        g = this;
    }

    void start() {
        new Thread(this).start();
    }

    static java.io.InputStream open(String p) {
        return g.getClass().getResourceAsStream(p);
    }

    // ================================================================== main loop

    public void run() {
        Graphics gr = getGraphics();
        SW = getWidth();
        SH = getHeight();
        draw(gr);
        flushGraphics();
        try {
            loadAll(gr);
        } catch (Throwable t) {
            t.printStackTrace();
            gr.setColor(0);
            gr.fillRect(0, 0, SW, SH);
            gr.setColor(0xff4040);
            gr.drawString("Load error: " + t, 2, 2, 20);
            flushGraphics();
            return;
        }
        setState(S_TITLE);
        Snd.music(Snd.M_TITLE);
        long last = System.currentTimeMillis(), acc = 0;
        while (running) {
            long now = System.currentTimeMillis();
            if (getWidth() != SW || getHeight() != SH) resize();
            acc += now - last;
            last = now;
            if (acc > 250) acc = 250;
            if (paused) acc = 0;
            while (acc >= 50) {
                acc -= 50;
                try { tickAll(); } catch (Throwable t) { t.printStackTrace(); }
            }
            try { draw(gr); } catch (Throwable t) { t.printStackTrace(); }
            flushGraphics();
            Snd.poll();                  // sound watchdog
            fpsN++;
            if (now - fpsT >= 1000) { fps = fpsN; fpsN = 0; fpsT = now; }
            long spent = System.currentTimeMillis() - now;
            try { Thread.sleep(spent < 28 ? 30 - spent : 2); } catch (Exception e) { }
        }
    }

    static void loadAll(Graphics gr) throws Exception {
        loadOptions();
        loadPct = 10; g.paintLoad(gr);
        E.load();
        loadPct = 60; g.paintLoad(gr);
        W.initColors();
        Snd.init();
        fBig = Font.getFont(Font.FACE_PROPORTIONAL, Font.STYLE_BOLD, Font.SIZE_LARGE);
        fMed = Font.getFont(Font.FACE_PROPORTIONAL, Font.STYLE_BOLD, Font.SIZE_MEDIUM);
        fSmall = Font.getFont(Font.FACE_PROPORTIONAL, Font.STYLE_BOLD, Font.SIZE_SMALL);
        loadImages();
        loadPct = 90; g.paintLoad(gr);
        setupView();
        loadPct = 100;
    }

    void paintLoad(Graphics gr) {
        draw(gr);
        flushGraphics();
    }

    static void loadImages() throws Exception {
        Image t = Image.createImage("/title.png");
        imgTitle = scaleCover(t, SW, SH);
        t = null;
        String logo = SW >= 220 ? "/logo230.png" : SW >= 160 ? "/logo176.png" : "/logo120.png";
        imgLogo = Image.createImage(logo);
        boolean big = SH >= 260 || SW >= 260;
        imgDig = Image.createImage(big ? "/dig16.png" : "/dig10.png");
        digW = imgDig.getWidth() / 12;
        digH = imgDig.getHeight();
        imgDigS = Image.createImage("/dig10.png");
        digSW = imgDigS.getWidth() / 12;
        digSH = imgDigS.getHeight();
        imgIcons = Image.createImage("/icons.png");
        imgDig8 = Image.createImage("/dig8.png");
        hudKey = -1;
        faceSz = big ? 36 : 24;
        String[] fn = {"face0", "face1", "face2", "facegrin", "facedead"};
        for (int i = 0; i < 5; i++) imgFace[i] = Image.createImage("/" + fn[i] + "_" + faceSz + ".png");
        shade = new int[SW * 4];
        for (int i = 0; i < shade.length; i++) shade[i] = 0xb8000000;
    }

    static Image scaleCover(Image src, int w, int h) {
        int sw = src.getWidth(), sh = src.getHeight();
        int[] s = new int[sw * sh];
        src.getRGB(s, 0, sw, 0, 0, sw, sh);
        // cover: keep aspect, crop
        int scw = w * 1024 / sw, sch = h * 1024 / sh, sc = scw > sch ? scw : sch;
        int ox = (sw * sc / 1024 - w) / 2, oy = (sh * sc / 1024 - h) / 2;
        int[] d = new int[w * h];
        for (int y = 0; y < h; y++) {
            int sy = (y + oy) * 1024 / sc;
            if (sy >= sh) sy = sh - 1;
            for (int x = 0; x < w; x++) {
                int sx = (x + ox) * 1024 / sc;
                if (sx >= sw) sx = sw - 1;
                d[y * w + x] = s[sy * sw + sx];
            }
        }
        return Image.createRGBImage(d, w, h, false);
    }

    static void setupView() {
        hudH = SH >= 300 ? 42 : SH >= 200 ? 32 : 24;
        if (faceSz == 36 && hudH < 40) hudH = 40;
        E.setup(SW, SH, SH - hudH, detail);
    }

    void resize() {
        SW = getWidth();
        SH = getHeight();
        try {
            imgTitle = null;
            System.gc();
            loadImages();
            setupView();
        } catch (Throwable t) { }
    }

    protected void sizeChanged(int w, int h) {
        // handled in the loop
    }

    protected void hideNotify() {
        paused = true;
        keys = 0;
        if (state == S_PLAY) setState(S_PAUSE);
        Snd.stopAll();
    }

    protected void showNotify() {
        paused = false;
        Snd.resume();
    }

    // ================================================================== input

    static int mapKey(int code) {
        switch (code) {
            case KEY_NUM2: return K_UP;
            case KEY_NUM8: return K_DOWN;
            case KEY_NUM4: return K_LEFT;
            case KEY_NUM6: return K_RIGHT;
            case KEY_NUM5: return K_FIRE;
            case KEY_NUM1: return K_SL;
            case KEY_NUM3: return K_SR;
            case KEY_NUM0: return K_USE;
            case KEY_NUM7: return K_PREV;
            case KEY_NUM9: return K_NEXT;
            case KEY_STAR: return K_MAP;
            case KEY_POUND: return K_JUMP;
        }
        if (code == -6 || code == -21 || code == 21 || code == -202 || code == 57345 || code == 113) return K_MENU;
        if (code == -7 || code == -22 || code == 22 || code == -203 || code == 57346 || code == 112 || code == -11) return K_BACK;
        try {
            switch (g.getGameAction(code)) {
                case UP: return K_UP;
                case DOWN: return K_DOWN;
                case LEFT: return K_LEFT;
                case RIGHT: return K_RIGHT;
                case FIRE: return K_FIRE;
                case GAME_A: return K_USE;
                case GAME_B: return K_JUMP;
                case GAME_C: return K_PREV;
                case GAME_D: return K_NEXT;
            }
        } catch (Throwable t) { }
        if (code == 10 || code == -5 || code == 32) return K_FIRE;
        return 0;
    }

    // ---- cheat codes: the last keys typed on the keypad
    static final StringBuffer codeBuf = new StringBuffer();
    static int codeT;

    static boolean code(String c) {
        int n = codeBuf.length();
        if (n < c.length() || tick - codeT > 60) return false;
        for (int i = 0; i < c.length(); i++) if (codeBuf.charAt(n - c.length() + i) != c.charAt(i)) return false;
        codeBuf.setLength(0);
        return true;
    }

    protected void keyPressed(int code) {
        if ((code >= KEY_NUM0 && code <= KEY_NUM9) || code == KEY_STAR || code == KEY_POUND) {
            if (tick - codeT > 60) codeBuf.setLength(0);
            codeBuf.append((char) code);
            if (codeBuf.length() > 8) codeBuf.deleteCharAt(0);
            codeT = tick;
        }
        int k = mapKey(code);
        keyT = tick;
        if ((k & (K_FIRE | K_USE)) != 0) fireT = tick;
        keys |= k;
        pressed |= k;
    }

    protected void keyReleased(int code) {
        keys &= ~mapKey(code);
    }

    static boolean hit(int k) {
        if ((pressed & k) != 0) { pressed &= ~k; return true; }
        return false;
    }

    // ================================================================== state machine

    static void setState(int s) {
        prevState = state;
        state = s;
        stateTick = 0;
        sel = 0;
        pressed = 0;
        skipArmed = false;
    }

    // After a fight the fire key is usually still being hammered, and a cutscene, the tally screen, a story page or the
    // ending must not be skipped by that: fire and use presses only count once the key has been left alone for half a
    // second (the menu key still skips a cutscene at once).
    static boolean skipArmed;

    static void guardSkip() {
        if (skipArmed) return;
        pressed &= ~(K_FIRE | K_USE);
        if (stateTick >= 15 && (((keys & (K_FIRE | K_USE)) == 0 && tick - fireT >= 10) || stateTick >= 400))
            skipArmed = true;                      // (the 20 s fallback: some phones lose key releases)
    }

    static void tickAll() {
        tick++;
        stateTick++;
        if (tick % 80 == 0) keepLit();
        for (int i = 0; i < 3; i++) if (msgT[i] > 0) msgT[i]--;
        if (subT > 0) subT--;
        if (faceT > 0) faceT--;
        if (state == S_CUT || state == S_INTER || state == S_STORY || state == S_END) guardSkip();
        switch (state) {
            case S_TITLE: menuTitle(); break;
            case S_SKILL: menuSkill(); break;
            case S_EPI: menuEpisode(); break;
            case S_CUT: tickCut(); break;
            case S_STORY: tickStory(); break;
            case S_CARD:
                if (stateTick > 40 || (stateTick > 6 && hit(K_FIRE | K_USE))) startPlay();
                break;
            case S_PLAY: tickPlay(); break;
            case S_PAUSE: menuPause(); break;
            case S_MAP:
                pressed &= ~(K_USE | K_SL | K_UP | K_SR | K_LEFT | K_RIGHT | K_PREV | K_DOWN | K_NEXT);
                if (mapCodes()) break;
                if (hit(K_MAP | K_FIRE | K_BACK | K_MENU)) setState(S_PLAY);
                break;
            case S_TEST: menuTest(); break;
            case S_OPT: menuOpt(); break;
            case S_HELP:
                if (hit(K_UP) && helpTop > 0) helpTop--;
                if (hit(K_DOWN) && helpTop < helpMax) helpTop++;
                if (hit(K_FIRE | K_BACK | K_MENU | K_USE)) { helpTop = 0; int r = optReturn; setState(r); helpText = HELP; if (r == S_TEST) sel = 8; }
                break;
            case S_INTER:
                if (stateTick > 10 && hit(K_FIRE | K_USE)) nextLevel();
                break;
            case S_DEAD:
                W.tick();
                // a burst of fire still going when Butch dies must not skip the death screen: presses count only
                // after 2.5 s, and only once the fire key has been left alone for half a second
                if (!deadArmed) {
                    pressed &= ~(K_FIRE | K_USE);
                    if (stateTick >= DEAD_WAIT && (((keys & (K_FIRE | K_USE)) == 0 && tick - fireT >= 10)
                            || stateTick >= DEAD_WAIT * 4)) deadArmed = true;   // (some phones lose key releases)
                } else if (hit(K_FIRE | K_USE)) restartLevel();
                if (hit(K_MENU | K_BACK)) toTitle();
                break;
            case S_END: tickStory(); break;
        }
    }

    /** Codes typed on the automap (classic style). Returns true if the automap was closed. */
    static boolean mapCodes() {
        if (code("000")) { setState(S_PLAY); if (W.level % 4 == 0) victory(); else levelDone(); return true; }
        if (code("111")) { W.god = !W.god; cheatMsg(W.god ? "GOD MODE ON" : "GOD MODE OFF"); }
        if (code("222")) {
            W.weapons = 31; W.ammo[0] = W.AMAX[0]; W.ammo[1] = W.AMAX[1]; W.ammo[2] = W.AMAX[2]; W.keys = 7;
            cheatMsg("ALL WEAPONS, AMMO AND KEYS");
        }
        if (code("333")) { W.health = 200; W.armor = 100; cheatMsg("HEALTH 200, ARMOR 100"); }
        if (code("444")) { for (int i = 0; i < 4096; i++) W.seen[i] = 1; cheatMsg("MAP REVEALED"); }
        if (code("404")) { setState(S_PLAY); W.god = false; W.armor = 0; W.damagePlayer(9999, -1); return true; }
        if (code("666")) {
            int n = 0;
            for (int i = 0; i < W.nt; i++)
                if (W.isMon(W.tType[i]) && !W.isBoss(W.tType[i]) && W.tSt[i] < W.ST_DIE) { W.kill(i, false); n++; }
            cheatMsg(n + " MONSTERS KILLED");
        }
        if (code("777")) { W.noclip = !W.noclip; cheatMsg(W.noclip ? "WALK THROUGH WALLS ON" : "WALK THROUGH WALLS OFF"); }
        if (code("888")) { W.freeze = !W.freeze; cheatMsg(W.freeze ? "MONSTERS FROZEN" : "MONSTERS UNFROZEN"); }
        if (code("999")) { setState(S_PLAY); victory(); return true; }
        return false;
    }

    static void cheatMsg(String m) {
        msg(m, 0xc080ff);
        Snd.sfx(Snd.SECRET);
    }

    // ---- the test menu (title screen: press * three times)
    static int testCut = 1, testLevel = 1, testStory, testSkill = 1;
    static boolean testAllWeapons = true, testPlayAll, testFromMenu;
    static final String[] LEVEL_NAMES = {"DEAD END CEMETERY", "BLACKWOOD MANOR", "BONE CATACOMBS", "PUMPKIN KING'S PATCH",
            "MAIN STREET MAYHEM", "THE MIDWAY", "THE FUNHOUSE", "THE BIG TOP", "BLACKWATER BAYOU", "THE MAD LAB",
            "CASTLE HOLLOWFANG", "THE COUNT'S THRONE", "NEON GRAVEYARD", "THE ASSEMBLY LINE", "THE CIRCUIT MAZE", "FRANKENSTEIN PRIME",
            "THE LOST TEMPLE", "RIVER OF BONES", "THE FOG", "XIBALBA"};
    static final String[] SKILL_NAMES = {"TRICK", "TREAT", "NIGHTMARE"};
    static final String[] CODES = {"Open the automap (*) and type:", "", "000  finish the level", "111  god mode",
            "222  all weapons, ammo, keys", "333  health 200, armor 100", "404  bury Butch (death screen)", "444  reveal the map", "666  kill all monsters",
            "777  walk through walls", "888  freeze monsters", "999  play the episode ending", "",
            "Title screen: * * * opens this test menu.", "",
            "Difficulty screen: # warps, 0 toggles god mode."};

    static String[] testItems() {
        return new String[]{"CUTSCENE: EPISODE " + testCut, "STYLE: " + (gore ? "GORY" : "CLASSIC"), "PLAY ALL CUTSCENES",
                "LEVEL " + testLevel + ": " + LEVEL_NAMES[testLevel - 1], "SKILL: " + SKILL_NAMES[testSkill],
                "STORY SCREEN: " + (testStory + 1) + "/" + STORY.length, "GOD MODE: " + (W.god ? "ON" : "OFF"),
                "ALL WEAPONS: " + (testAllWeapons ? "ON" : "OFF"), "CHEAT CODES", "BACK"};
    }

    static String[] testItemsShort() {
        return new String[]{"CUTSCENE " + testCut, gore ? "GORY" : "CLASSIC", "ALL CUTSCENES", "LEVEL " + testLevel,
                "SKILL " + SKILL_NAMES[testSkill], "STORY " + (testStory + 1), "GOD " + (W.god ? "ON" : "OFF"),
                "WEAPONS " + (testAllWeapons ? "ON" : "OFF"), "CODES", "BACK"};
    }

    static void menuTest() {
        nav(10);
        int d = hit(K_RIGHT) ? 1 : hit(K_LEFT) ? -1 : 0;
        if (d != 0) {
            Snd.sfx(Snd.CLICK);
            switch (sel) {
                case 0: testCut = (testCut + NEP - 1 + d) % NEP + 1; break;
                case 1: gore = !gore; saveOptions(); break;
                case 3: testLevel = (testLevel + NEP * 4 - 1 + d) % (NEP * 4) + 1; break;
                case 4: testSkill = (testSkill + 3 + d) % 3; break;
                case 5: testStory = (testStory + STORY.length + d) % STORY.length; break;
                case 6: W.god = !W.god; break;
                case 7: testAllWeapons = !testAllWeapons; break;
            }
        }
        if (hit(K_FIRE | K_USE)) {
            Snd.sfx(Snd.CLICK);
            switch (sel) {
                case 0: testFromMenu = true; testPlayAll = false; testGear(); startCut(testCut); break;
                case 1: gore = !gore; saveOptions(); break;
                case 2: testFromMenu = true; testPlayAll = true; testGear(); startCut(1); break;
                case 3:
                    testFromMenu = false;
                    W.skill = testSkill;
                    testGear();
                    episode = epOf(testLevel);
                    beginLevel(testLevel, false);
                    break;
                case 4: testSkill = (testSkill + 1) % 3; break;
                case 5: testFromMenu = true; showStory(testStory, -100); break;
                case 6: W.god = !W.god; break;
                case 7: testAllWeapons = !testAllWeapons; break;
                case 8: helpText = CODES; optReturn = S_TEST; setState(S_HELP); break;
                case 9: toTitle(); break;
            }
        }
        if (hit(K_BACK | K_MENU)) toTitle();
    }

    static void testGear() {
        W.health = 100; W.armor = 0; W.weapons = 3; W.weapon = 1; W.ammo[0] = 40; W.ammo[1] = 0; W.ammo[2] = 0;
        if (testAllWeapons) { W.weapons = 31; W.ammo[0] = 150; W.ammo[1] = 30; W.ammo[2] = 12; W.armor = 100; }
    }

    static void backToTest(int s) {
        testFromMenu = false;
        setState(S_TEST);
        sel = s;
        Snd.music(Snd.M_TITLE);
    }

    static void toTitle() {
        setState(S_TITLE);
        Snd.music(Snd.M_TITLE);
    }

    // ------------------------------------------------------------------ menus

    static final String[] TITLE_ITEMS = {"NEW GAME", "CONTINUE", "OPTIONS", "CONTROLS", "EXIT"};

    static int nav(int n) {
        if (hit(K_UP)) { sel = (sel + n - 1) % n; Snd.sfx(Snd.CLICK); }
        if (hit(K_DOWN)) { sel = (sel + 1) % n; Snd.sfx(Snd.CLICK); }
        return sel;
    }

    static void menuTitle() {
        if (code("***")) { Snd.sfx(Snd.SECRET); setState(S_TEST); return; }
        nav(TITLE_ITEMS.length);
        if (sel == 1 && !hasSave && (pressed & (K_UP | K_DOWN)) == 0) { }
        if (hit(K_FIRE | K_USE)) {
            switch (sel) {
                case 0: setState(S_EPI); break;
                case 1:
                    if (hasSave) {
                        W.skill = saveSkill;
                        restoreStart();
                        beginLevel(saveLevel, false);
                    } else Snd.sfx(Snd.CLICK);
                    break;
                case 2: optReturn = S_TITLE; setState(S_OPT); break;
                case 3: optReturn = S_TITLE; setState(S_HELP); break;
                case 4: running = false; midlet.quit(); break;
            }
        }
        if (hit(K_BACK)) { running = false; midlet.quit(); }
    }

    static final String[] SKILLS = {"TRICK  (easy)", "TREAT  (normal)", "NIGHTMARE  (hard)"};

    static int warp = 1;

    static void menuSkill() {
        if (stateTick == 1) sel = 1;
        nav(3);
        if (hit(K_JUMP)) { warp = warp % 4 + 1; Snd.sfx(Snd.SECRET); }
        if (hit(K_USE)) { W.god = !W.god; Snd.sfx(Snd.SECRET); }
        if (hit(K_FIRE)) {
            W.skill = sel;
            newGame(episode);
        }
        if (hit(K_BACK | K_MENU)) { setState(S_EPI); sel = episode - 1; }
    }

    static final String[] EPISODES = {"1: NIGHT OF THE PUMPKIN KING", "2: CARNIVAL OF CARNAGE", "3: BITE NIGHT", "4: VOLTAGE OF THE DAMNED",
            "5: CURSE OF THE JADE SKULL"};
    static final String[] EPISODES_S = {"1: PUMPKIN KING", "2: CARNIVAL", "3: BITE NIGHT", "4: VOLTAGE", "5: JADE SKULL"};
    static final int NEP = 5;
    static int episode = 1;

    static void menuEpisode() {
        if (stateTick == 1) sel = episode - 1;
        nav(NEP);
        if (hit(K_FIRE | K_USE)) { episode = sel + 1; setState(S_SKILL); sel = 1; }
        if (hit(K_BACK | K_MENU)) setState(S_TITLE);
    }

    static int epOf(int lv) { return (lv - 1) / 4 + 1; }

    static int firstLevel(int ep) { return (ep - 1) * 4 + 1; }

    static final String[] PAUSE_ITEMS = {"RESUME", "AUTOMAP", "OPTIONS", "CONTROLS", "QUIT TO TITLE"};

    static void menuPause() {
        nav(PAUSE_ITEMS.length);
        if (hit(K_BACK | K_MENU)) { setState(S_PLAY); Snd.resume(); return; }
        if (hit(K_FIRE | K_USE)) {
            switch (sel) {
                case 0: setState(S_PLAY); Snd.resume(); break;
                case 1: setState(S_MAP); break;
                case 2: optReturn = S_PAUSE; setState(S_OPT); break;
                case 3: optReturn = S_PAUSE; setState(S_HELP); break;
                case 4: toTitle(); break;
            }
        }
    }

    static final String[] DETAIL = {"HIGH", "MEDIUM", "LOW"};

    static boolean gore;                      // cutscene style: false = classic (funny), true = gory (Duke style)

    static String[] optItems() {
        return new String[]{"DETAIL: " + DETAIL[detail], "MUSIC: " + (Snd.musicMode == Snd.MUS_ON ? "ON" : Snd.musicMode == Snd.MUS_MENUS ? "MENUS ONLY" : "OFF"), "SOUND FX: " + (Snd.sfxOn ? "ON" : "OFF"),
                "VOICE: " + (Snd.voiceOn ? "ON" : "OFF"), "VIBRATION: " + (vibe ? "ON" : "OFF"), "CROSSHAIR: " + (crosshair ? "ON" : "OFF"),
                "FPS COUNTER: " + (showFps ? "ON" : "OFF"), "CUTSCENES: " + (gore ? "GORY" : "CLASSIC"), "BACK"};
    }

    static void menuOpt() {
        nav(9);
        boolean act = hit(K_FIRE | K_USE | K_LEFT | K_RIGHT);
        if (hit(K_BACK | K_MENU) || (act && sel == 8)) {
            saveOptions();
            setState(optReturn);
            if (optReturn == S_PAUSE) sel = 2;
            return;
        }
        if (!act) return;
        Snd.sfx(Snd.CLICK);
        switch (sel) {
            case 0: detail = (detail + 1) % 3; setupView(); break;
            case 1:     // on -> menus only -> off
                Snd.musicMode = Snd.musicMode == Snd.MUS_ON ? Snd.MUS_MENUS : Snd.musicMode == Snd.MUS_MENUS ? Snd.MUS_OFF : Snd.MUS_ON;
                Snd.wantMusic = optReturn == S_TITLE ? Snd.M_TITLE : W.lvMusic;
                Snd.resume();
                break;
            case 2: Snd.sfxOn = !Snd.sfxOn; break;
            case 3: Snd.voiceOn = !Snd.voiceOn; break;
            case 4: vibe = !vibe; break;
            case 5: crosshair = !crosshair; break;
            case 6: showFps = !showFps; break;
            case 7: gore = !gore; break;
        }
    }

    // ------------------------------------------------------------------ story

    static final String[] STORY = {
            // ---- episode 1: night of the pumpkin king
            "HOLLOW CREEK.  OCTOBER 31ST.\n\nFor twenty years BUTCH GRAVES has dug the graves of this sleepy town. Quiet work. Quiet neighbours.\n\n"
                    + "Tonight the Harvest Cult lit the Great Jack-o'-Lantern on Blackwood Hill and woke the PUMPKIN KING.\n\n"
                    + "Now the dead are clawing out of Butch's cemetery... and they're ruining his lawn.\n\nGrab the shovel. Time to put them back.",
            "The mausoleum stairs lead past the old iron gate, straight up the hill to BLACKWOOD MANOR - home of the Harvest Cult.\n\n"
                    + "Witches cackle in the windows. Ghosts drift through the halls.\n\nSomewhere inside is the way down to their unholy altar.",
            "Beneath the manor lie the BONE CATACOMBS, dug by the cult over a hundred Halloweens.\n\n"
                    + "The air reeks of slime and old candy wrappers.\n\nThe Pumpkin King's altar is close. Butch can hear it... laughing.",
            "The altar spits Butch out under a BLOOD MOON, right into the Pumpkin King's own patch.\n\n"
                    + "Lava bubbles between the vines. The King is waiting, crowned in fire.\n\nOne more grave to dig. A big one.",
            "The Pumpkin King now lives on Butch's porch, glowing and grumbling.\n\nThe dead are back in the ground and Hollow Creek sleeps.\n\n"
                    + "But out past the edge of town a wheezy calliope starts to play. A carnival that wasn't there yesterday is putting up its tents...",
            // ---- episode 2: carnival of carnage
            "EPISODE 2:  CARNIVAL OF CARNAGE\n\nThe Harvest Cult had friends. MISTER GIGGLES' TRAVELING CARNIVAL OF SOULS rolled into Hollow Creek at midnight, "
                    + "and by one o'clock all of Main Street was screaming.\n\nClowns in the diner. Skeletons in the hardware store. Balloons everywhere.\n\n"
                    + "Butch hates clowns.",
            "Main Street is quiet again, if you don't count the honking.\n\nPast the gate the MIDWAY glows: rigged games, a freak show, "
                    + "and a haunted house ride that is a little too haunted.\n\nSomewhere beyond it waits the funhouse.",
            "The FUNHOUSE. Mirrors that lie, floors that tilt, and a laugh track that never stops.\n\n"
                    + "The big top is on the other side. So is Mister Giggles.",
            "Under the BIG TOP the band plays a funeral march. The bleachers are full of things that used to be the audience.\n\n"
                    + "In the center ring, Mister Giggles takes a bow.\n\nTime to bring the house down.",
            "The carnival packs up in a hurry, minus one clown car.\n\nIn Giggles' trailer Butch finds the contract: the carnival, the cult and "
                    + "this whole Halloween mess were paid for by COUNT HOLLOWFANG, the old vampire in the castle across the swamp.\n\n"
                    + "He signed it in blood. Of course he did.",
            // ---- episode 3: bite night
            "EPISODE 3:  BITE NIGHT\n\nCastle Hollowfang sits on Raven Peak, past the BLACKWATER BAYOU. Werewolves hunt the boardwalks "
                    + "and bats blot out the moon.\n\nThe Count has thrown a Halloween party every year for three hundred years. Nobody leaves early.\n\n"
                    + "Butch brought a shovel. And a lot of shells.",
            "The swamp road ends at a grate under the castle. Below it hums the MAD LAB, where the Count's pet scientist stitched wolves to men "
                    + "and men to worse.\n\nThe tesla coils are still running.",
            "Up the back stairs and into CASTLE HOLLOWFANG: velvet, candlelight, and a coffin in every bedroom.\n\n"
                    + "The Count knows Butch is coming. He set out extra wine glasses.",
            "The tower stairs climb to the roof, where the Count waits on his throne under the full moon, cape spread like wings.\n\n"
                    + "\"Gravedigger,\" he purrs. \"How appropriate.\"\n\nThis is the last grave. Make it deep.",
            "The bats scatter into the sunrise. The castle falls silent, and Hollow Creek wakes up to a perfectly normal November first.\n\n"
                    + "Almost normal. Down in the Count's mad lab the tesla coils are still humming, the operating table is empty, "
                    + "and a crackling green PORTAL hangs in the air where the doctor used to be.\n\n"
                    + "On the floor lies his diary, open at the last page:\n\n\"OCTOBER 31ST, 2099. ALL HALLOWS' EVE. THE PERFECT NIGHT FOR MY MASTERPIECE.\"",
            // ---- episode 4: voltage of the damned
            "EPISODE 4:  VOLTAGE OF THE DAMNED\n\nHALLOWEEN, 2099.\n\nThe Count's pet scientist, DR. VIKTOR FRANKEN, fled through his time portal "
                    + "and kept stitching. Seventy-five years later Hollow Creek is NEO-HOLLOW: a city of neon, holo-graves and robot butlers.\n\n"
                    + "Tonight the robots are climbing out of the graves.\n\nButch steps through the portal, shovel first.",
            "Beyond the holo-cemetery towers FRANKENTECH INDUSTRIES, a factory the size of a mountain.\n\n"
                    + "Inside, conveyor belts carry battery packs, chainsaw arms and spare skulls down the ASSEMBLY LINE.\n\n"
                    + "Watch your step. Everything in here is moving.",
            "Deeper in lies the doctor's mainframe: the CIRCUIT MAZE. Corridors of humming server racks that rearrange themselves "
                    + "whenever someone pulls a lever.\n\nThe doctor's voice crackles over the speakers: \"Lost, gravedigger? Pull a lever. Any lever. Hee hee!\"",
            "At the heart of the factory a reactor glows green. Above it stands the doctor's masterpiece, FRANKENSTEIN PRIME: "
                    + "forty tons of stitched steel, with the doctor himself in the cockpit.\n\nIts shoulders crackle with lightning. "
                    + "When it stomps, the whole floor lights up.\n\nWhen it stomps... jump.",
            "The portal drops Butch on his own front lawn at dawn on November first. The kettle is still warm.\n\n"
                    + "The Pumpkin King grumbles on the porch. Somewhere far in the future a tiny robot rolls around an empty lab, looking for its master.\n\n"
                    + "And in the mailbox waits a crate covered in foreign stamps. It smells of mould and old tombs. Inside, a telegram:\n\n"
                    + "\"MR GRAVES STOP THE DEAD WALK IN THE JUNGLE STOP ONLY A GRAVEDIGGER WILL DO STOP COME AT ONCE STOP\n- PROF. A. CRANE\"",
            // ---- episode 5: curse of the jade skull
            "EPISODE 5:  CURSE OF THE JADE SKULL\n\nNOVEMBER 1ST. THE DAY OF THE DEAD.\n\nA rattling seaplane drops Butch in the jungles of XOCHITLAN, "
                    + "where PROFESSOR ALISTAIR CRANE has spent ten years digging for the JADE SKULL of SEVEN DEATH, Lord of the Underworld.\n\n"
                    + "The professor's camp is empty. His diggers ran off. The temple drums didn't.\n\n"
                    + "Crane left a note on his tent: \"The golden idol opens the way. DON'T step on the plates.\"",
            "Butch staggers out of the temple with the golden idol and a lot of new bruises.\n\n"
                    + "The idol's ruby eyes point downriver, to the RIVER OF BONES, where the conquistadors who came for the skull "
                    + "four hundred years ago never left.\n\nThey still stand guard. Their muskets are still loaded.",
            "At the great falls Butch finally finds the professor... with the JADE SKULL already in his hands.\n\n"
                    + "\"Splendid work, Mr. Graves! You cleared the path beautifully. Every expedition needs a good... shovel.\"\n\n"
                    + "Crane vanishes into the mist toward SAN LAZARO, the mission town that was swallowed by fog the night the skull was buried.\n\n"
                    + "Nobody has walked out of that fog since. The church bell still rings at midnight.",
            "Under the church, the crypt stairs go down... and down... and down, into XIBALBA, the Place of Fear.\n\n"
                    + "Rivers of lava. Racks of skulls. And on an obsidian throne, waiting for his skull to come home: SEVEN DEATH.\n\n"
                    + "Crane is already on his knees. \"Great Lord! I bring you your skull! Grant me eternal life!\"\n\n"
                    + "Seven Death smiles. That's never a good sign.",
            "The sun comes up over Xochitlan on the second of November, and the village throws the biggest Day of the Dead fiesta anyone can remember.\n\n"
                    + "The professor got his eternal life. Sort of.\n\nButch buried the Jade Skull himself, six feet down, where nobody will ever dig it up. "
                    + "He'd know. He's a professional.\n\nBack home, the Pumpkin King asks where he's been.\n\n\"Digging,\" says Butch.\n\n"
                    + "HAPPY HALLOWEEN.\n\nTHE END\n\nBUTCH GRAVES 3D\nThe Halloween Saga\n\nThanks for playing!"};
    static int storyIdx, storyNext;

    static void showStory(int idx, int next) {
        storyIdx = idx;
        storyNext = next;
        layIdx = -1;
        setState(idx == NEP * 5 - 1 ? S_END : S_STORY);
        Snd.music(idx % 5 == 4 ? Snd.M_WIN : Snd.M_STORY);
    }

    static void tickStory() {
        layoutStory();
        boolean typed = (stateTick - pageTick) * 2 >= pageLen;
        if (hit(K_BACK | K_MENU)) { endStory(); return; }
        if (hit(K_UP)) {
            if (page > 0) { page--; pageTick = stateTick - 1000; Snd.sfx(Snd.CLICK); }
            return;
        }
        if (hit(K_FIRE | K_USE | K_DOWN)) {
            if (!typed) { pageTick = stateTick - 1000; return; }
            if (page < pages.length - 1) { page++; pageTick = stateTick; Snd.sfx(Snd.CLICK); return; }
            endStory();
        }
    }

    static void endStory() {
        if (testFromMenu && storyNext == -100) { backToTest(5); return; }
        if (state == S_END) { hasSave = false; saveProgress(); toTitle(); return; }
        if (storyNext < 0) {                       // episode finished: on to the next episode's intro
            int ep = -storyNext;
            if (W.health < 100) W.health = 100;
            showStory((ep - 1) * 5, firstLevel(ep));
            return;
        }
        beginLevel(storyNext, true);
    }

    // ---- story pagination: wrap the text for the current font/screen and split it into pages
    static String[][] pages = new String[0][];
    static int page, pageTick, pageLen, layIdx = -1, layW, layH;

    static Font storyFont() {
        if (SH < 200) return fSmall;
        return SW >= 220 ? fMed : fSmall;
    }

    static void layoutStory() {
        if (layIdx == storyIdx && layW == SW && layH == SH && pages.length > 0) return;
        Font f = storyFont();
        java.util.Vector lines = new java.util.Vector();
        String s = STORY[storyIdx];
        int w = SW - 16, i = 0, n = s.length();
        while (i < n) {
            if (s.charAt(i) == '\n') { lines.addElement(""); i++; continue; }
            int e = i, lastSp = -1;
            while (e < n && s.charAt(e) != '\n') {
                if (s.charAt(e) == ' ') lastSp = e;
                if (f.substringWidth(s, i, e - i + 1) > w) break;
                e++;
            }
            if (e < n && s.charAt(e) != '\n' && lastSp > i) e = lastSp;
            lines.addElement(s.substring(i, e));
            i = e;
            if (i < n && s.charAt(i) == ' ') i++;
            else if (i < n && s.charAt(i) == '\n') i++;
        }
        int lh = f.getHeight();
        int per = (SH - 12 - fSmall.getHeight() - 8) / lh;
        if (per < 3) per = 3;
        java.util.Vector pg = new java.util.Vector();
        java.util.Vector cur = new java.util.Vector();
        for (int k = 0; k < lines.size(); k++) {
            String l = (String) lines.elementAt(k);
            if (cur.size() == 0 && l.length() == 0) continue;          // no blank line at the top of a page
            // break early at a paragraph gap if the next paragraph would be split right after its first line
            if (cur.size() >= per) { pg.addElement(cur); cur = new java.util.Vector(); if (l.length() == 0) continue; }
            cur.addElement(l);
        }
        if (cur.size() > 0) pg.addElement(cur);
        pages = new String[pg.size()][];
        for (int k = 0; k < pages.length; k++) {
            java.util.Vector v = (java.util.Vector) pg.elementAt(k);
            int m = v.size();
            while (m > 0 && ((String) v.elementAt(m - 1)).length() == 0) m--;
            pages[k] = new String[m];
            for (int j = 0; j < m; j++) pages[k][j] = (String) v.elementAt(j);
        }
        if (layIdx != storyIdx) { page = 0; pageTick = stateTick; }
        if (page >= pages.length) page = pages.length - 1;
        layIdx = storyIdx; layW = SW; layH = SH;
    }

    // ------------------------------------------------------------------ game flow

    static void newGame(int ep) {
        W.health = 100;
        W.armor = 0;
        W.weapons = 3;           // shovel + revolver
        W.weapon = 1;
        W.ammo[0] = 40; W.ammo[1] = 0; W.ammo[2] = 0;
        int base = (ep - 1) * 5, lv = firstLevel(ep);
        if (warp > 1) {
            W.weapons = 31; W.ammo[0] = 150; W.ammo[1] = 30; W.ammo[2] = 12; W.armor = 100;
            showStory(base + warp - 1, lv + warp - 1);
            return;
        }
        showStory(base, lv);
    }

    static void beginLevel(int lv, boolean fromStory) {
        try {
            W.load(lv);
        } catch (Throwable t) {
            msg("Level load failed: " + t, 0xff0000);
            return;
        }
        if (W.health <= 0) W.health = 100;
        rememberStart(lv);
        saveLevel = lv;
        saveSkill = W.skill;
        hasSave = true;
        saveProgress();
        setState(S_CARD);
        cardT = 0;
        Snd.newLevel();
        Snd.music(W.lvMusic);
    }

    static void startPlay() {
        try {
            meltImg = Image.createImage(SW, SH);
            drawCard(meltImg.getGraphics());
            meltT = 0;
            int n = (SW + 3) / 4;
            meltOff = new int[n];
            int v = -W.rnd(16);
            for (int i = 0; i < n; i++) {
                v += W.rnd(3) - 1;
                if (v > 0) v = 0;
                if (v < -15) v = -15;
                meltOff[i] = v;
            }
        } catch (Throwable t) { meltImg = null; }
        setState(S_PLAY);
        for (int i = 0; i < 3; i++) msgT[i] = 0;
        if (W.level == 1) voice(Snd.V_START1, "Trick or treat. I'm the trick.", 0);
        else if (W.level == 4) voice(Snd.V_START2, "Graveyard shift just started.", 0);
        else if (W.level == 5) voice(Snd.V_START3, "Great. Clowns. I hate clowns.", 0);
        else if (W.level == 9) voice(Snd.V_START4, "Bite me.", 0);
        else if (W.level == 13) voice(Snd.V_START5, "Halloween twenty ninety-nine. Same monsters, more batteries.", 0);
        else if (W.level == 17) voice(Snd.V_START6, "Jungle. Why'd it have to be jungle?", 0);
    }

    static void rememberStart(int lv) {
        lvStart[0] = W.health; lvStart[1] = W.armor; lvStart[2] = W.weapons; lvStart[3] = W.weapon;
        lvStart[4] = W.ammo[0]; lvStart[5] = W.ammo[1]; lvStart[6] = W.ammo[2]; lvStart[7] = W.skill; lvStart[8] = lv;
    }

    static void restoreStart() {
        W.health = lvStart[0]; W.armor = lvStart[1]; W.weapons = lvStart[2]; W.weapon = lvStart[3];
        W.ammo[0] = lvStart[4]; W.ammo[1] = lvStart[5]; W.ammo[2] = lvStart[6];
        if (W.health <= 0) W.health = 100;
    }

    static void restartLevel() {
        restoreStart();
        beginLevel(W.level, false);
    }

    static int mapCheat;
    static int interKills, interTotal, interSecrets, interTotalSec, interTime;

    static void levelDone() {
        interKills = W.kills; interTotal = W.totalKills; interSecrets = W.secrets; interTotalSec = W.totalSecrets; interTime = W.ticks / 20;
        setState(S_INTER);
        Snd.music(Snd.M_WIN);            // music change first: it silences the effects still playing
        voice(Snd.V_LEVEL, "Too easy.", 0);
    }

    static void nextLevel() {
        int lv = W.level;
        showStory((epOf(lv) - 1) * 5 + (lv - 1) % 4 + 1, lv + 1);
    }

    /** The episode's boss is dead: roll the cutscene. */
    static void victory() {
        interKills = W.kills; interTotal = W.totalKills; interSecrets = W.secrets; interTotalSec = W.totalSecrets; interTime = W.ticks / 20;
        startCut(epOf(W.level));
    }

    static void episodeDone(int ep) {
        if (ep < NEP) { storyNextEp = ep + 1; showStory((ep - 1) * 5 + 4, -(ep + 1)); }
        else showStory(NEP * 5 - 1, 0);
    }

    static int storyNextEp;

    static void died() {
        setState(S_DEAD);
        deadArmed = false;
        faceKind = 4;
        Snd.music(Snd.M_DEAD);
        vibrate(400);
    }

    static int upTapT = -100;

    static void tickPlay() {
        String sn = Snd.note;
        if (sn != null) {                 // the sound engine changed a setting to keep this phone's audio working
            Snd.note = null;
            msg(sn, 0xffc080);
            saveOptions();
        }
        if (hit(K_MENU | K_BACK)) { setState(S_PAUSE); return; }
        if (hit(K_MAP)) { setState(S_MAP); return; }
        int k = keys;
        if ((pressed & K_UP) != 0) {              // double-tap forward (and hold) to sprint
            pressed &= ~K_UP;
            if (W.ticks - upTapT < 9 && W.stamina > 150) W.sprint = true;
            upTapT = W.ticks;
        }
        W.kFwd = (k & K_UP) != 0;
        W.kBack = (k & K_DOWN) != 0;
        W.kLeft = (k & K_LEFT) != 0;
        W.kRight = (k & K_RIGHT) != 0;
        W.kSL = (k & K_SL) != 0;
        W.kSR = (k & K_SR) != 0;
        W.kFire = stateTick > 8 && ((k & K_FIRE) != 0 || (pressed & K_FIRE) != 0);
        pressed &= ~K_FIRE;
        if (hit(K_USE)) W.kUse = true;
        if (hit(K_JUMP)) W.kJump = true;
        if (hit(K_PREV)) W.cycleWeapon(-1);
        if (hit(K_NEXT)) W.cycleWeapon(1);
        int hp = W.health;
        W.tick();
        if (W.health < hp && vibe) vibrate(60);
    }

    // ------------------------------------------------------------------ feedback hooks used by the world

    static void msg(String s, int col) {
        for (int i = 2; i > 0; i--) { msgs[i] = msgs[i - 1]; msgCol[i] = msgCol[i - 1]; msgT[i] = msgT[i - 1]; }
        msgs[0] = s;
        msgCol[0] = col;
        msgT[0] = 60;
    }

    /** A how-to hint: stays up longer than a pickup message. */
    static void tip(String s) {
        msg(s, 0xffd080);
        msgT[0] = 120;
    }

    static int lastVoiceT = -1000;

    static void voice(int id, String text, int minGap) {
        if (tick - lastVoiceT < minGap) return;
        lastVoiceT = tick;
        Snd.voice(id);
        subtitle = "\"" + text + "\"";
        subT = 50;
    }

    static void face(int kind, int t) {
        if (kind == 1 && faceKind == 3 && faceT > 0) return;
        faceKind = kind;
        faceT = t;
    }

    // ------------------------------------------------------------------ backlight
    // Phones switch the screen off after a few seconds without a key press, which kills cutscenes, story pages and
    // the tally screen. Every 4 s while one of those is up (or while someone is actually playing) the lights are
    // switched back on: with the Nokia UI API where the phone has it, else with MIDP's flashBacklight (cutscene-type
    // screens only there, because a few phones really flash with it).
    static int keyT, lightApi = -1;      // -1 unknown, 0 none, 1 Nokia, 2 MIDP flash

    static void keepLit() {
        boolean watch = state == S_CUT || state == S_STORY || state == S_CARD || state == S_INTER || state == S_END
                || state == S_DEAD;
        boolean play = state == S_PLAY && tick - keyT < 1200;      // a minute after the last key, let it sleep
        if (!watch && !play) return;
        if (lightApi < 0) {
            try { Class.forName("com.nokia.mid.ui.DeviceControl"); lightApi = 1; } catch (Throwable t) { lightApi = 2; }
        }
        if (lightApi == 1) {
            try { NL.lights(); return; } catch (Throwable t) { lightApi = 2; }
        }
        if (lightApi == 2 && watch) {
            try { Display.getDisplay(midlet).flashBacklight(6000); } catch (Throwable t) { lightApi = 0; }
        }
    }

    static void vibrate(int ms) {
        if (!vibe) return;
        try { Display.getDisplay(midlet).vibrate(ms); } catch (Throwable t) { }
    }

    // ================================================================== cutscenes (in-engine, scripted)

    static int cutEp, cutT, cutFade;
    static final int[] cutA = new int[12];        // thing index of each actor
    static String cutWho, cutLine;
    static int cutWhoId;
    static int cutWhoCol, cutLineT, cutBand;       // cutBand: the tallest subtitle band this cutscene has needed

    static void startCut(int ep) {
        try {
            W.load(100 + ep);
        } catch (Throwable t) {
            episodeDone(ep);
            return;
        }
        W.pz = 0; W.bob = 0; W.bobAmp = 0; W.kick = 0; W.shake = 0; W.flashDmg = 0; W.flashPick = 0;
        cutEp = ep; cutT = 0; cutLine = null; cutLineT = 0; cutFade = 255; cutBand = 0;
        cuA = -1; cuShake = 0; capImg = null; capT0 = -1; splatT0 = -1;
        for (int k = 0; k < cutA.length; k++) {
            int i = W.spawn(W.ACTOR, 0, 0);
            cutA[k] = i;
            if (i >= 0) W.tAux[i] = -1;
        }
        setState(S_CUT);
        Snd.music(Snd.M_CUT);
    }

    static void endCut() {
        if (W.health <= 0) W.health = 100;
        cuA = -1; capImg = null; rayMap = null;
        if (testFromMenu) {
            if (testPlayAll && cutEp < NEP) { startCut(cutEp + 1); return; }
            backToTest(testPlayAll ? 2 : 0);
            return;
        }
        episodeDone(cutEp);
    }

    static void tickCut() {
        cutT++;
        if (cutT > 15 && hit(K_FIRE | K_USE | K_MENU | K_BACK)) { endCut(); return; }
        if (cutLineT > 0) cutLineT--;
        if (cuA >= 0 && ++cuT >= cuDur) { cuA = -1; cuShake = 0; }
        if (cuShake > 0 && (cuT & 1) == 0) cuShake--;
        if (cutGlow > 0) cutGlow = cutGlow > 10 ? cutGlow - 10 : 0;
        W.cutTick();
        if (gore) {
            if (cutEp == 1) cutG1(cutT);
            else if (cutEp == 2) cutG2(cutT);
            else if (cutEp == 3) cutG3(cutT);
            else if (cutEp == 4) cutG4(cutT);
            else cutG5(cutT);
        } else if (cutEp == 1) cut1(cutT);
        else if (cutEp == 2) cut2(cutT);
        else if (cutEp == 3) cut3(cutT);
        else if (cutEp == 4) cut4(cutT);
        else cut5(cutT);
    }

    // ---- script helpers: positions are in 1/16 of a cell
    static void cam(int x16, int y16, int ang) { W.px = x16 << 12; W.py = y16 << 12; W.pa = ang & 4095; }

    static void put(int k, int spr, int x16, int y16, int z) {
        int i = cutA[k];
        if (i < 0) return;
        W.tAux[i] = spr; W.tX[i] = x16 << 12; W.tY[i] = y16 << 12; W.tZ[i] = z;
    }

    static void scale(int k, int sc) { if (cutA[k] >= 0) W.tVZ[cutA[k]] = sc; }

    static void hide(int k) { if (cutA[k] >= 0) W.tAux[cutA[k]] = -1; }

    /** Move actor k from (x0,y0) to (x1,y1) during ticks t0..t0+dur, alternating walk frames a/b. */
    static void walk(int k, int t, int t0, int dur, int x0, int y0, int x1, int y1, int a, int b) {
        if (t < t0 || t > t0 + dur || cutA[k] < 0) return;
        int f = t - t0;
        put(k, ((f / 5) & 1) == 0 ? a : b, x0 + (x1 - x0) * f / dur, y0 + (y1 - y0) * f / dur, W.tZ[cutA[k]]);
    }

    static void say(int who, String line, int voiceId) {
        cutWho = who == 0 ? "BUTCH" : who == 1 ? "PUMPKIN KING" : who == 2 ? "LITTLE GHOST" : who == 3 ? "MISTER GIGGLES" : who == 4 ? "COUNT HOLLOWFANG"
                : who == 5 ? "DR. FRANKEN" : who == 6 ? "PROFESSOR CRANE" : "SEVEN DEATH";
        cutWhoCol = who == 0 ? 0xffa040 : who == 1 ? 0xffd040 : who == 2 ? 0xe0e0ff : who == 3 ? 0xff5050 : who == 4 ? 0xd070ff : who == 5 ? 0x80ffa0
                : who == 6 ? 0xe0c080 : 0x40ff90;
        cutLine = line;
        cutLineT = 62 + (line.length() > 40 ? line.length() - 40 : 0);      // long lines stay up longer
        cutWhoId = who;
        if (voiceId >= 0) Snd.voice(voiceId);
    }

    static void fadeIn(int t, int t0, int dur) { if (t >= t0 && t <= t0 + dur) cutFade = 255 - 255 * (t - t0) / dur; }

    static void fadeOut(int t, int t0, int dur) { if (t >= t0) cutFade = t >= t0 + dur ? 255 : 255 * (t - t0) / dur; }

    // ---- Duke-style close-ups: a talking portrait punched in over a spinning-rays backdrop
    static int cuA = -1, cuB = -1, cuT, cuDur, cuWho, cuSide, cuC1, cuC2, cuShake;
    static byte[] rayMap;
    static int rayW, rayH;
    static Image capImg;
    static int capT0 = -1, capEp;

    /** Cut to a close-up of portrait sprites a (mouth shut) / b (mouth open) for dur ticks. who = speaker id for lip sync,
     *  bg = backdrop colour pair, side = slide in from the left (-1), right (1) or punch in (0). */
    static void closeUp(int a, int b, int dur, int who, int c1, int c2, int side) {
        cuA = a; cuB = b; cuT = 0; cuDur = dur; cuWho = who; cuSide = side;
        cuC1 = E.nearest(c1, 1, Res.FB0); cuC2 = E.nearest(c2, 1, Res.FB0);
    }

    /** say() plus a close-up of the speaker. */
    static void talk(int who, String line, int voiceId, int dur) {
        say(who, line, voiceId);
        int a, b, c1, c2;
        switch (who) {
            case 0: a = Res.S_CPBUTCH_1; b = Res.S_CPBUTCH_2; c1 = 0xd05010; c2 = 0x601808; break;
            case 1: a = Res.S_CPPK_1; b = Res.S_CPPK_2; c1 = 0xe02000; c2 = 0xff9010; break;
            case 2: a = Res.S_CPKID_1; b = Res.S_CPKID_1; c1 = 0x3050c0; c2 = 0x101840; break;
            case 3: a = Res.S_CPGIG_1; b = Res.S_CPGIG_2; c1 = 0xe0c020; c2 = 0xc01010; break;
            case 4: a = Res.S_CPCOUNT_1; b = Res.S_CPCOUNT_2; c1 = 0x601070; c2 = 0x180820; break;
            case 6: a = Res.S_CPCRANE_1; b = Res.S_CPCRANE_2; c1 = 0xb08a30; c2 = 0x2c4018; break;
            case 7: a = Res.S_CPSEVEN_1; b = Res.S_CPSEVEN_2; c1 = 0x108050; c2 = 0x400808; break;
            default: a = Res.S_CPDOC_1; b = Res.S_CPDOC_2; c1 = 0x20a050; c2 = 0x0a3020; break;
        }
        closeUp(a, b, dur, who, c1, c2, (who & 1) == 0 ? -1 : 1);
    }

    static void cutCard(int ep) {
        try {
            capImg = Image.createImage((gore ? "/capg" : "/cap") + ep + (SW >= 200 ? ".png" : "s.png"));
        } catch (Throwable t) { capImg = null; }
        capT0 = cutT; capEp = ep;
        Snd.sfx(Snd.EXPLODE);
        W.shake = 10;
    }

    /** Draw the close-up into the render buffer (the 3D view is not rendered while it is on screen). */
    static void drawCloseUp() {
        final int RW = E.RW, RH = E.RH;
        int hw = (RW + 1) >> 1, hh = (RH + 1) >> 1;          // the backdrop map is kept at half resolution
        if (rayMap == null || rayW != RW || rayH != RH) {
            rayMap = new byte[hw * hh];
            rayW = RW; rayH = RH;
            int cx = hw / 2, cy = hh * 3 / 5, maxd = E.dist(cx << 8, cy << 8) >> 8;
            for (int y = 0; y < hh; y++)
                for (int x = 0; x < hw; x++) {
                    int ang = E.atan2((y - cy) * E.DY, (x - cx) * E.DX) * 64 >> 12;
                    int d = (E.dist((x - cx) * E.DX << 8, (y - cy) * E.DY << 8) >> 8) * 4 / (maxd > 0 ? maxd : 1);
                    rayMap[y * hw + x] = (byte) (ang | ((d > 3 ? 3 : d) << 6));
                }
        }
        final int[] buf = E.buf, cmap = E.cmap;
        final byte[] rm = rayMap;
        int rot = cuT, c1 = cuC1, c2 = cuC2;
        for (int y = 0, o = 0; y < RH; y++) {
            int row = (y >> 1) * hw;
            for (int x = 0; x < RW; x++, o++) {
                int b = rm[row + (x >> 1)] & 255;
                buf[o] = cmap[((2 + (b >> 6) * 4) << 8) | ((((b & 63) + rot) & 4) == 0 ? c1 : c2)];
            }
        }
        boolean open = cutLineT > 0 && cutWhoId == cuWho && cuA != cuB && (((cuT / 3) + (cuT / 7)) & 1) == 1;
        int spr = open ? cuB : cuA;
        int h = E.sh[cuA] > 0 ? E.sh[cuA] : 100;
        int k = (int) (((long) RH * 51000) / h) * E.DY / E.DX;        // ~78% of the view height (k is per render column)
        int kw = (int) (((long) RW * 62000) / (E.sw[cuA] > 0 ? E.sw[cuA] : 100));   // ...and no wider than the screen
        if (kw < k) k = kw;
        if (cuT < 6) k = k * (130 - cuT * 5) / 100;                    // zoom punch
        k = k * (1000 + cuT * 2) / 1000;                               // slow push in
        int sx = RW / 2;
        if (cuSide != 0 && cuT < 5) sx += cuSide * RW * (5 - cuT) / 12;
        int by = RH + 2 + (E.sin(cuT * 90) * RH >> 16) / 60;
        if (cuShake > 0) { sx += W.rnd(cuShake * 2 + 1) - cuShake; by += W.rnd(cuShake + 1); }
        E.drawScreen(spr, sx, by, k, 4);
    }

    // ---- animation helpers
    /** Linear interpolation from a to b over ticks t0..t0+dur (clamped). */
    static int lerp(int t, int t0, int dur, int a, int b) {
        if (t <= t0) return a;
        if (t >= t0 + dur) return b;
        return a + (b - a) * (t - t0) / dur;
    }

    /** Smooth (ease in/out) interpolation. */
    static int ease(int t, int t0, int dur, int a, int b) {
        if (t <= t0) return a;
        if (t >= t0 + dur) return b;
        int f = (t - t0) * 1024 / dur;
        f = f * f * (3072 - 2 * f) >> 20;          // smoothstep, 0..1024
        return a + (b - a) * f / 1024;
    }

    /** Bouncing height: |sin| hops of the given period (ticks) and height. */
    static int hop(int t, int period, int h) {
        int v = E.sin((t % period) * 2048 / period);
        return v * h >> 16;
    }

    /** Move the camera from one spot/angle to another during t0..t0+dur. */
    static void camMove(int t, int t0, int dur, int x0, int y0, int a0, int x1, int y1, int a1) {
        if (t < t0 || t > t0 + dur) return;
        cam(ease(t, t0, dur, x0, x1), ease(t, t0, dur, y0, y1), ease(t, t0, dur, a0, a1));
    }

    static int actX(int k) { return cutA[k] < 0 ? 0 : W.tX[cutA[k]] >> 12; }

    static int actY(int k) { return cutA[k] < 0 ? 0 : W.tY[cutA[k]] >> 12; }

    /** Episode 1: Butch carries the Pumpkin King's carved head home to his porch. A trick-or-treater gets a fright. */
    static void cut1(int t) {
        if (t == 1) {
            cam(184, 236, 3072);
            put(0, Res.S_BUTCH_CWALK1, 96, 150, 0);
            put(1, Res.S_CS_PKHEAD, 96, 153, 26000);
            scale(1, 300);
        }
        fadeIn(t, 1, 24);
        camMove(t, 1, 70, 184, 236, 3072, 184, 166, 3072);              // slow push in toward the porch
        if (t >= 1 && t <= 70) {                                     // Butch carries the head up the path
            int x = lerp(t, 1, 70, 96, 196), y = lerp(t, 1, 70, 150, 124);
            put(0, ((t / 6) & 1) == 0 ? Res.S_BUTCH_CWALK1 : Res.S_BUTCH_CWALK2, x, y, 0);
            put(1, Res.S_CS_PKHEAD, x, y + 3, 26000 + hop(t, 12, 1600));
        }
        if (t == 71) put(0, Res.S_BUTCH_CARRY, 196, 124, 0);
        if (t > 72 && t <= 88) put(1, Res.S_CS_PKHEAD, lerp(t, 72, 16, 196, 198), lerp(t, 72, 16, 127, 112), ease(t, 72, 16, 26000, 0));
        if (t == 89) Snd.sfx(Snd.HIT);
        walk(0, t, 90, 14, 196, 124, 168, 128, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        if (t == 105) put(0, Res.S_BUTCH_POINT, 168, 128, 0);
        if (t == 108) talk(0, "Best jack-o'-lantern on the block.", Snd.V_C1A, 50);
        if (t == 158) put(0, Res.S_BUTCH_STAND, 168, 128, 0);
        if (t >= 160 && t < 226) {                                   // the head rocks, then yaps
            int r = E.sin(t * 300) * 2 >> 16;
            put(1, t > 176 && ((t / 4) & 1) == 0 ? Res.S_CS_PKHEAD2 : Res.S_CS_PKHEAD, 198 + r, 112, hop(t, 10, 1500));
        }
        if (t == 176) talk(1, "You will pay for this, gravedigger!", Snd.V_C1B, 50);
        if (t == 228) { put(1, Res.S_CS_PKHEAD, 198, 112, 0); put(0, Res.S_BUTCH_SHRUG, 168, 128, 0); }
        camMove(t, 236, 30, 184, 166, 3072, 190, 172, 3072 + 170);    // pan right: someone is coming
        if (t >= 236 && t <= 276) put(2, Res.S_CS_KID, lerp(t, 236, 40, 250, 206), lerp(t, 236, 40, 160, 132), hop(t, 10, 3000));
        camMove(t, 266, 14, 190, 172, 3072 + 170, 186, 178, 3072 + 60);
        if (t == 276) put(0, Res.S_BUTCH_STAND, 168, 128, 0);
        if (t == 282) talk(2, "Trick or treat!", Snd.V_C1C, 34);
        // BOO! smash cut to the head, then to the kid
        if (t == 330) { talk(1, "BOO!", Snd.V_C1D, 26); cuShake = 8; W.shake = 8; }
        if (t == 356) { closeUp(Res.S_CPKID_2, Res.S_CPKID_2, 20, 2, 0x8090ff, 0x202060, 0); cuShake = 5; Snd.sfx(Snd.SCREAM); }
        if (t >= 376 && t < 386) put(2, Res.S_CS_KID2, 206, 132, hop(t - 376, 20, 14000));     // jumps out of his sheet
        if (t == 384) put(3, Res.S_CANDY, 210, 136, 16000);
        if (t > 384 && t <= 394) put(3, Res.S_CANDY, 210, 136, lerp(t, 384, 10, 16000, 0));
        if (t >= 386 && t <= 418) {                                  // ...and runs off zig-zagging
            int f = t - 386;
            put(2, Res.S_CS_KID2, 206 + f * 3 + (E.sin(f * 400) * 10 >> 16), 132 + f * 2, hop(f, 6, 5000));
        }
        if (t == 419) hide(2);
        if (t == 424) talk(0, "Kids these days.", Snd.V_C1E, 40);
        walk(0, t, 466, 26, 168, 128, 204, 134, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        if (t == 493) { hide(3); put(0, Res.S_BUTCH_STAND, 204, 134, 0); Snd.sfx(Snd.PICKUP); }
        if (t == 498) { talk(0, "Don't mind if I do.", Snd.V_C1F, 40); cuA = Res.S_CPBUTCH_3; }
        if (t >= 540 && t < 580) put(1, ((t / 4) & 1) == 0 ? Res.S_CS_PKHEAD2 : Res.S_CS_PKHEAD, 198 + (E.sin(t * 300) * 2 >> 16), 112, 0);
        if (t == 580) put(1, Res.S_CS_PKHEAD, 198, 112, 0);
        if (t == 548) cutCard(1);
        fadeOut(t, 610, 22);
        if (t > 634) endCut();
    }

    static final int[] CLX = {160, 184, 208, 168, 189, 206}, CLY = {128, 128, 128, 144, 144, 144};

    /** Episode 2: Giggles' getaway in a clown car does not go well. */
    static void cut2(int t) {
        if (t == 1) {
            cam(130, 200, 3072 - 260);
            put(1, Res.S_GIGGLES_FALL, 200, 112, 0);
            put(0, Res.S_BUTCH_WALK1, 120, 166, 0);
        }
        fadeIn(t, 1, 20);
        camMove(t, 1, 50, 130, 200, 3072 - 260, 184, 190, 3072);
        walk(0, t, 1, 44, 120, 166, 166, 154, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        if (t == 46) put(0, Res.S_BUTCH_POINT, 166, 154, 0);
        if (t > 20 && t < 120 && (t % 23) < 3) put(1, Res.S_GIGGLES_FALL, 200 + (t & 1) * 2, 112, 0);    // twitching
        if (t == 52) talk(0, "Any last words, Giggles?", Snd.V_C2A, 46);
        if (t >= 100 && t < 120) put(1, (t / 6 & 1) == 0 ? Res.S_GIGGLES_PAIN : Res.S_GIGGLES_FALL, 200, 112, (t / 6 & 1) == 0 ? hop(t, 12, 3000) : 0);
        if (t == 120) talk(3, "Honk... honk...", Snd.V_C2B, 40);
        if (t == 160) { put(1, Res.S_GIGGLES_FALL, 200, 112, 0); put(0, Res.S_BUTCH_STAND, 166, 154, 0); }
        // the clown car bounces in from the right; the camera follows it
        if (t == 162) { put(2, Res.S_CS_CAR, 300, 124, 0); scale(2, 430); Snd.sfx(Snd.HONK); }
        if (t >= 162 && t <= 194) put(2, Res.S_CS_CAR, ease(t, 162, 32, 300, 218), lerp(t, 162, 32, 124, 118), hop(t, 8, 2500));
        camMove(t, 160, 20, 184, 190, 3072, 184, 190, 3072 + 200);
        camMove(t, 188, 20, 184, 190, 3072 + 200, 184, 192, 3072 + 60);
        if (t > 194 && t < 262) put(2, Res.S_CS_CAR, 218, 118, t < 242 ? hop(t, 6, 900) : 0);     // rocking as they climb out
        for (int k = 0; k < 6; k++) {               // ...clowns pop out of the tiny car in big arcs
            int t0 = 200 + k * 6;
            if (t == t0) Snd.sfx(k % 2 == 0 ? Snd.HONK : Snd.CLOWN);
            if (t >= t0 && t <= t0 + 14)
                put(3 + k, Res.S_CLOWN_PAIN, lerp(t, t0, 14, 218, CLX[k]), lerp(t, t0, 14, 118, CLY[k]), hop(t - t0, 30, 40000));
            if (t > t0 + 14 && t < 254) {            // capering about
                int f = t - t0 + k * 5;
                put(3 + k, ((f / 4) & 1) == 0 ? Res.S_CLOWN_WALK1 : Res.S_CLOWN_WALK2, CLX[k] + (E.sin(f * 200) * 6 >> 16),
                        CLY[k] + (E.cos(f * 200) * 3 >> 16), hop(f, 9, 4000));
            }
            if (t == 254) put(3 + k, Res.S_CLOWN_ATTACK, CLX[k], CLY[k], 0);
        }
        if (t == 264) { put(0, Res.S_BUTCH_AIM, 166, 154, 0); Snd.sfx(Snd.SHOTGUN); W.flashPick = 100; W.shake = 8; }
        if (t == 274) put(0, Res.S_BUTCH_STAND, 166, 154, 0);
        for (int k = 0; k < 6; k++) {               // ...flinch, then scramble back in
            if (t >= 265 && t < 274) put(3 + k, Res.S_CLOWN_PAIN, CLX[k], CLY[k], hop(t - 265, 18, 9000 + k * 1500));
            int t0 = 274 + k * 2;
            if (t >= t0 && t <= t0 + 12)
                put(3 + k, ((t / 3) & 1) == 0 ? Res.S_CLOWN_WALK1 : Res.S_CLOWN_WALK2, lerp(t, t0, 12, CLX[k], 218), lerp(t, t0, 12, CLY[k], 118),
                        hop(t, 6, 6000));
            if (t == t0 + 13) hide(3 + k);
        }
        walk(1, t, 278, 16, 200, 112, 214, 116, Res.S_GIGGLES_WALK1, Res.S_GIGGLES_WALK2);
        if (t == 295) hide(1);
        if (t == 300) Snd.sfx(Snd.HONK);
        // ...and roars off, straight into the strongman's weights
        if (t >= 302 && t <= 330) put(2, Res.S_CS_CAR, ease(t, 302, 28, 218, 130), lerp(t, 302, 28, 118, 124), hop(t, 7, 3000));
        camMove(t, 302, 26, 184, 192, 3072 + 60, 184, 192, 3072 - 440);
        if (t == 331) {
            hide(2);
            Snd.sfx(Snd.EXPLODE); W.shake = 18; W.flashPick = 120;
            for (int k = 0; k < 4; k++) W.fx(W.FX_BOOM, (126 + k * 5) << 12, (120 + k * 3) << 12, 6000 + k * 9000, 12 + k * 2);
            for (int k = 0; k < 14; k++) W.part(130 << 12, 124 << 12, 20000, W.rr(-8000, 8000), W.rr(-8000, 8000), W.rr(3000, 9000), k % 2 == 0 ? W.P_YEL : W.P_ORANGE, 26);
        }
        if (t == 337 || t == 343) { W.fx(W.FX_BOOM, (132 + (t & 7)) << 12, 122 << 12, 22000, 10); Snd.sfx(Snd.EXPLODE); }
        if (t >= 344 && t < 470 && (t % 12) == 0) W.fx(W.FX_SMOKE, 130 << 12, 124 << 12, 8000, 14);
        if (t == 346) put(9, Res.S_CS_BALLOON, 132, 122, 0);
        if (t > 346 && t < 470 && cutA[9] >= 0) {
            W.tZ[cutA[9]] = (t - 346) * 1400;
            W.tX[cutA[9]] = (132 + (E.sin(t * 90) * 5 >> 16)) << 12;
        }
        camMove(t, 350, 24, 184, 192, 3072 - 440, 176, 186, 3072 - 160);
        if (t == 376) talk(0, "Worst. Circus. Ever.", Snd.V_C2C, 44);
        if (t == 422) put(0, Res.S_BUTCH_SHRUG, 166, 154, 0);
        if (t == 430) cutCard(2);
        fadeOut(t, 492, 22);
        if (t > 516) endCut();
    }

    /** Episode 3: the Count escapes as a bat. Batter up. */
    static void cut3(int t) {
        if (t == 1) {
            cam(256, 48, 1360);                       // looking at the moon
            put(0, Res.S_BUTCH_STAND, 234, 87, 0);
            W.fx(W.FX_SMOKE, 238 << 12, 84 << 12, 20000, 14);
            Snd.sfx(Snd.TELE);
        }
        fadeIn(t, 1, 20);
        if (t > 1 && t < 156) {                       // flutter around Butch's head
            int a = t * 130;
            put(1, ((t / 3) & 1) == 0 ? Res.S_CS_CBAT1 : Res.S_CS_CBAT2, 236 + (E.cos(a) * 14 >> 16), 84 + (E.sin(a) * 6 >> 16),
                    52000 + (E.sin(t * 300) >> 3));
        }
        if (t == 30) talk(4, "You have not seen the last of me, gravedigger!", Snd.V_C3A, 62);
        if (t == 100) { put(0, Res.S_BUTCH_WIND, 234, 87, 0); }
        if (t == 108) { talk(0, "Batter up.", Snd.V_C3B, 32); cuA = Res.S_CPBUTCH_3; }
        if (t == 156) { put(0, Res.S_BUTCH_SWING, 234, 87, 0); Snd.sfx(Snd.BONK); W.shake = 8; W.flashPick = 60; }
        if (t >= 156 && t < 216) {                    // off toward the moon
            int f = t - 156;
            put(1, ((t / 2) & 1) == 0 ? Res.S_CS_CBAT1 : Res.S_CS_CBAT2, 232 - f * 157 / 100, 86 + f * 278 / 100, 52000 + f * f * 120);
        }
        if (t == 166) say(4, "Cuuuurses!", Snd.V_C3C);
        if (t == 216) { hide(1); put(2, Res.S_CS_STAR, 138, 253, 480000); scale(2, 600); Snd.sfx(Snd.SECRET); }
        if (t == 234) hide(2);
        if (t == 236) put(0, Res.S_BUTCH_STAND, 234, 87, 0);
        if (t == 240) { talk(0, "Home run.", Snd.V_C3D, 36); cuA = Res.S_CPBUTCH_3; }
        if (t == 300) say(0, "Happy Halloween.", Snd.V_WIN);
        if (t == 310) cutCard(3);
        fadeOut(t, 372, 24);
        if (t > 398) endCut();
    }

    /** Episode 4: the doctor climbs out of his wrecked mech and flees through his time portal. Butch follows him home. */
    static void cut4(int t) {
        if (t == 1) {
            cam(184, 228, 3072);
            put(1, Res.S_CS_WRECK, 184, 128, 0);
            scale(1, 512);
            put(0, Res.S_BUTCH_STAND, 165, 147, 0);
            put(2, Res.S_CS_DOC, 190, 124, 0);
            hide(2);
        }
        fadeIn(t, 1, 22);
        camMove(t, 1, 60, 184, 228, 3072, 184, 188, 3072);
        if (t < 340 && (t % 14) == 0) W.fx(W.FX_SMOKE, (176 + (t * 7) % 18) << 12, (124 + (t * 5) % 6) << 12, 22000, 14);
        if (t < 340 && (t % 9) == 0) W.spark((184 + (t * 13) % 24 - 12) << 12, 128 << 12, 26000, 4, W.P_CYAN);
        // the doctor pops out of the cockpit
        if (t >= 30 && t <= 46) put(2, Res.S_CS_DOC, lerp(t, 30, 16, 190, 204), lerp(t, 30, 16, 126, 144), hop(t - 30, 32, 20000));
        if (t == 30) Snd.sfx(Snd.ROBOT);
        if (t >= 46 && t < 156) put(2, ((t / 5) & 1) == 0 ? Res.S_CS_DOCRANT : Res.S_CS_DOC, 204, 144, hop(t, 10, 3500));    // hopping mad
        if (t == 52) talk(5, "You ruined my masterpiece!", Snd.V_C4D, 50);
        if (t == 102) put(0, Res.S_BUTCH_POINT, 165, 147, 0);
        if (t == 104) talk(0, "Should've stuck to pumpkins, Doc.", Snd.V_C4A, 46);
        if (t == 156) { put(2, Res.S_CS_DOCRANT, 204, 144, 0); put(0, Res.S_BUTCH_STAND, 165, 147, 0); W.flashPick = 60; Snd.sfx(Snd.TELE); }
        if (t == 160) talk(5, "Behold my ultimate creation!", Snd.V_C4E, 40);
        // ...a tiny robot rolls in and bumps into Butch's boot
        if (t >= 202 && t <= 240) { put(3, ((t / 3) & 1) == 0 ? Res.S_CS_MINIBOT1 : Res.S_CS_MINIBOT2, lerp(t, 202, 38, 236, 170), lerp(t, 202, 38, 166, 152), 0); scale(3, 440); }
        if (t == 220) put(2, Res.S_CS_DOC, 204, 144, 0);
        if (t >= 240 && t < 252) put(3, Res.S_CS_MINIBOT1, lerp(t, 240, 12, 170, 176), 154, hop(t - 240, 24, 6000));
        if (t == 240) Snd.sfx(Snd.BONK);
        if (t == 254) put(0, Res.S_BUTCH_SHRUG, 165, 147, 0);
        if (t == 258) { talk(0, "Terrifying.", Snd.V_C4B, 30); cuB = cuA; }
        if (t == 290) put(2, Res.S_CS_DOCRANT, 204, 144, 0);
        if (t == 292) talk(5, "It's a prototype!", Snd.V_C4F, 32);
        // the portal opens behind the wreck and the doctor runs for it
        if (t == 326) { Snd.sfx(Snd.TELE); W.flashPick = 90; W.shake = 6; }
        if (t >= 326 && t < 476) put(4, ((t / 3) & 1) == 0 ? Res.S_CS_PORTAL1 : Res.S_CS_PORTAL2, 211, 110, 0);
        if (t >= 326 && t < 346) scale(4, lerp(t, 326, 20, 40, 380));
        if (t == 346) put(0, Res.S_BUTCH_STAND, 165, 147, 0);
        if (t >= 346 && t <= 376) put(2, ((t / 3) & 1) == 0 ? Res.S_CS_DOCRUN1 : Res.S_CS_DOCRUN2, lerp(t, 346, 30, 204, 211), lerp(t, 346, 30, 144, 112), 0);
        if (t >= 346 && t <= 382) put(3, ((t / 2) & 1) == 0 ? Res.S_CS_MINIBOT1 : Res.S_CS_MINIBOT2, lerp(t, 346, 36, 176, 211), lerp(t, 346, 36, 154, 114), 0);
        if (t == 377) { hide(2); Snd.sfx(Snd.TELE); W.flashPick = 70; }
        if (t == 383) { hide(3); Snd.sfx(Snd.TELE); }
        if (t == 392) talk(0, "Time to go home.", Snd.V_C4C, 34);
        walk(0, t, 428, 44, 165, 147, 211, 113, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        camMove(t, 428, 44, 184, 188, 3072, 190, 186, 3072 + 80);
        if (t == 472) { hide(0); Snd.sfx(Snd.TELE); W.flashPick = 255; }
        if (t >= 474 && t < 482) fadeOut(t, 474, 6);
        // ---- cut to dawn on Butch's porch (the east half of the map)
        if (t == 482) {
            for (int k = 0; k < cutA.length; k++) hide(k);
            cam(568, 214, 3072);
            put(5, Res.S_CS_PKHEAD, 582, 112, 0);
            scale(5, 300);
            put(4, Res.S_CS_PORTAL1, 568, 150, 0);
            scale(4, 380);
        }
        fadeIn(t, 482, 16);
        if (t >= 482 && t < 528) { put(4, ((t / 3) & 1) == 0 ? Res.S_CS_PORTAL1 : Res.S_CS_PORTAL2, 568, 150, 0); }
        if (t == 498) { put(0, Res.S_BUTCH_WALK1, 568, 152, 0); Snd.sfx(Snd.TELE); W.flashPick = 120; }
        walk(0, t, 498, 24, 568, 152, 562, 180, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        if (t >= 518 && t < 538) scale(4, lerp(t, 518, 20, 380, 10));
        if (t == 538) hide(4);
        if (t == 523) put(0, Res.S_BUTCH_STAND, 562, 180, 0);
        camMove(t, 498, 40, 568, 214, 3072, 566, 206, 3072 + 30);
        if (t >= 540 && t < 548) put(5, Res.S_CS_PKHEAD2, 582, 112, hop(t - 540, 16, 4000));
        if (t == 548) talk(1, "You're late.", Snd.V_C4G, 36);
        if (t == 584) put(5, Res.S_CS_PKHEAD, 582, 112, 0);
        if (t == 590) { talk(0, "Happy Halloween.", Snd.V_WIN, 40); cuA = Res.S_CPBUTCH_3; }
        if (t == 634) cutCard(4);
        fadeOut(t, 700, 24);
        if (t > 726) endCut();
    }

    // ---- gore on the lens: blobs of blood (or pumpkin guts) that hit the camera and slide down
    static int splatT0 = -1, splatC1, splatC2, splatSeed;

    static void splat(int c1, int c2) {
        splatT0 = cutT; splatC1 = c1; splatC2 = c2; splatSeed = cutT * 7919 + 13;
        W.flashDmg = 120;
    }

    static void drawSplat(Graphics gr, int top, int vh) {
        int f = cutT - splatT0;
        if (f > 75) { splatT0 = -1; return; }
        if (cuA >= 0) return;                                  // the close-up camera is clean
        int seed = splatSeed;
        int unit = SW / 24 + 1, h = vh - top;
        for (int k = 0; k < 4; k++) {                          // a few splats, each a ragged core + radial spray + runs
            seed = seed * 1103515245 + 12345; int r1 = (seed >>> 8) & 0xffff;
            seed = seed * 1103515245 + 12345; int r2 = (seed >>> 8) & 0xffff;
            int cx = SW / 6 + r1 % (SW * 2 / 3), cy = top + h / 6 + r2 % (h / 2);
            int fall = f < 12 ? 0 : (f - 12) * (f - 12) * (2 + k % 2) / 40;    // the whole mess slowly slides down the lens
            cy += fall;
            if (cy - unit * 4 > vh) continue;
            int sz = unit * (k == 0 ? 3 : 2);
            for (int b = 0; b < 6; b++) {                     // ragged core: overlapping lumps
                seed = seed * 1103515245 + 12345; int r = (seed >>> 8) & 0xffff;
                int bx = cx + (r % (sz + 1)) - sz / 2, by = cy + ((r >> 5) % (sz + 1)) - sz / 2, br = sz / 2 + (r >> 10) % (sz / 2 + 1);
                gr.setColor(b < 4 ? splatC2 : splatC1);
                gr.fillArc(bx - br / 2, by - br / 2, br, br * 3 / 4 + 1, 0, 360);
            }
            for (int d = 0; d < 14; d++) {                    // spray: droplets flung outward, longer streaks further out
                seed = seed * 1103515245 + 12345; int r = (seed >>> 8) & 0xffff;
                int a = (r & 4095), dist = sz + (r >> 12) % (sz * 2 + 1);
                int dx = E.cos(a) * dist >> 16, dy = E.sin(a) * dist >> 16;
                int dr = 1 + (r >> 4) % 3;
                gr.setColor((d & 3) == 0 ? splatC1 : splatC2);
                gr.fillArc(cx + dx - dr, cy + dy - dr, dr * 2, dr * 2, 0, 360);
                if (d < 5) gr.drawLine(cx + dx / 2, cy + dy / 2, cx + dx, cy + dy);
            }
            for (int d = 0; d < 3; d++) {                     // runs dripping down from the core
                seed = seed * 1103515245 + 12345; int r = (seed >>> 8) & 0xffff;
                int rx = cx - sz / 2 + r % (sz + 1), len = (f < 50 ? f : 50) * (1 + r % 3) / 2;
                int w = 1 + (r >> 6) % 2;
                gr.setColor(splatC2);
                gr.fillRect(rx, cy, w, len);
                gr.fillArc(rx - 1, cy + len - 1, w + 2, w + 3, 0, 360);
            }
            gr.setColor(0xd84030);                             // a wet glint
            gr.fillRect(cx - sz / 4, cy - sz / 4, 2, 2);
        }
    }

    // ================================================================== the GORY cutscenes (Options: CUTSCENES: GORY)

    static final int BLOOD = 0x8a0004, BLOOD2 = 0x500000, GUTS = 0xe06a10;

    static void bloodBurst(int x16, int y16, int z, int n) {
        int x = x16 << 12, y = y16 << 12;
        for (int k = 0; k < n; k++)
            W.part(x, y, z, W.rr(-9000, 9000), W.rr(-9000, 9000), W.rr(2000, 11000), k % 3 == 0 ? W.P_DRED : W.P_RED, 30);
        for (int k = 0; k < 3; k++) W.fx(W.FX_BLOOD, x + W.rr(-12000, 12000), y + W.rr(-12000, 12000), z + W.rr(-8000, 8000), 6);
    }

    static void boom(int x16, int y16, int z) {
        W.fx(W.FX_BOOM, x16 << 12, y16 << 12, z, 12);
        Snd.sfx(Snd.EXPLODE);
        W.flashLight(x16 << 12, y16 << 12, 14);
    }

    /** Gory episode 1: the Pumpkin King's head mouths off one time too many. Field goal. */
    static void cutG1(int t) {
        if (t == 1) {
            cam(184, 236, 3072);
            put(0, Res.S_BUTCH_CWALK1, 96, 150, 0);
            put(1, Res.S_CS_PKHEAD, 96, 153, 26000);
            scale(1, 300);
        }
        fadeIn(t, 1, 24);
        camMove(t, 1, 60, 184, 236, 3072, 184, 182, 3072);
        if (t >= 1 && t <= 60) {
            int x = lerp(t, 1, 60, 96, 172), y = lerp(t, 1, 60, 150, 142);
            put(0, ((t / 6) & 1) == 0 ? Res.S_BUTCH_CWALK1 : Res.S_BUTCH_CWALK2, x, y, 0);
            put(1, Res.S_CS_PKHEAD, x, y + 3, 26000 + hop(t, 12, 1600));
        }
        if (t == 61) put(0, Res.S_BUTCH_CARRY, 172, 142, 0);
        if (t > 62 && t <= 76) put(1, Res.S_CS_PKHEAD, lerp(t, 62, 14, 172, 190), lerp(t, 62, 14, 145, 140), hop(t - 62, 28, 22000));   // dropped
        if (t == 76) { Snd.sfx(Snd.HIT); put(0, Res.S_BUTCH_STAND, 172, 142, 0); }
        if (t >= 80 && t < 150) put(1, ((t / 4) & 1) == 0 ? Res.S_CS_PKHEAD2 : Res.S_CS_PKHEAD, 190 + (E.sin(t * 300) * 2 >> 16), 140, 0);
        if (t == 82) talk(1, "You will pay for this, gravedigger!", Snd.V_C1B, 66);
        if (t == 150) talk(0, "Shut your pie hole.", Snd.V_G1A, 40);
        if (t >= 192 && t < 214) put(1, ((t / 3) & 1) == 0 ? Res.S_CS_PKHEAD2 : Res.S_CS_PKHEAD, 190, 140, hop(t, 6, 2500));    // panicking
        if (t == 194) say(1, "Wait! No, no, no!", Snd.V_G1C);
        if (t == 206) cam(192, 100, 1024);                            // reverse angle from the porch: the kick comes at us
        if (t == 214) { put(0, Res.S_BUTCH_KICK, 176, 142, 0); Snd.sfx(Snd.BONK); W.shake = 6; }
        if (t >= 214 && t <= 224) put(1, Res.S_CS_PKHEAD2, lerp(t, 214, 10, 190, 192), lerp(t, 214, 10, 140, 107), lerp(t, 214, 10, 4000, 30000));
        if (t == 225) {
            hide(1);
            splat(GUTS, BLOOD);
            Snd.sfx(Snd.MDIE); Snd.sfx(Snd.EXPLODE); W.shake = 14;
            for (int k = 0; k < 16; k++) W.part(192 << 12, 108 << 12, 32000, W.rr(-6000, 6000), W.rr(1000, 9000), W.rr(0, 6000), k % 2 == 0 ? W.P_ORANGE : W.P_RED, 30);
        }
        if (t == 244) put(0, Res.S_BUTCH_STAND, 176, 142, 0);
        if (t == 262) { talk(0, "Field goal.", Snd.V_G1B, 34); cuA = Res.S_CPGORE_1; cuB = Res.S_CPGORE_2; }
        if (t == 296) {                                               // back to the front: what is left of the King is all over the porch
            cam(184, 182, 3072);
            put(2, Res.S_CS_PKSMASH, 192, 100, 0); scale(2, 420);
            bloodBurst(192, 100, 6000, 10);
        }
        walk(0, t, 300, 30, 176, 142, 190, 112, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        if (t == 331) put(0, Res.S_BUTCH_STAND, 190, 112, 0);
        if (t == 336) { talk(0, "Pumpkin pie, anyone?", Snd.V_PUMPKIN, 46); cuA = Res.S_CPGORE_1; cuB = Res.S_CPGORE_2; }
        if (t > 296 && t < 480 && (t % 16) == 0) W.fx(W.FX_SMOKE, 192 << 12, 100 << 12, 4000, 14);
        if (t == 390) cutCard(1);
        fadeOut(t, 460, 22);
        if (t > 484) endCut();
    }

    /** Gory episode 2: Giggles gets the last laugh stuffed down his throat. The clown car does not help. */
    static void cutG2(int t) {
        if (t == 1) {
            cam(130, 200, 3072 - 260);
            put(1, Res.S_GIGGLES_FALL, 200, 112, 0);
            put(0, Res.S_BUTCH_WALK1, 120, 166, 0);
        }
        fadeIn(t, 1, 20);
        camMove(t, 1, 50, 130, 200, 3072 - 260, 184, 190, 3072);
        walk(0, t, 1, 44, 120, 166, 166, 154, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        if (t == 46) put(0, Res.S_BUTCH_POINT, 166, 154, 0);
        if (t > 20 && t < 148 && (t % 23) < 3) put(1, Res.S_GIGGLES_FALL, 200 + (t & 1) * 2, 112, 0);
        if (t == 52) talk(0, "Any last words, Giggles?", Snd.V_C2A, 46);
        if (t >= 100 && t < 106) put(1, Res.S_GIGGLES_PAIN, 200, 112, hop(t, 12, 3000));
        if (t == 106) talk(3, "Honk... honk...", Snd.V_C2B, 40);
        // a lit pumpkin bomb, right down the gullet
        if (t == 148) { put(0, Res.S_BUTCH_AIM, 166, 154, 0); Snd.sfx(Snd.LAUNCH); }
        if (t >= 148 && t <= 164) { put(2, Res.S_PBOMB, lerp(t, 148, 16, 166, 202), lerp(t, 148, 16, 150, 114), 40000 + hop(t - 148, 32, 20000)); scale(2, 500); }
        if (t == 165) { hide(2); put(1, Res.S_GIGGLES_PAIN, 200, 112, 0); Snd.sfx(Snd.HONK); put(0, Res.S_BUTCH_STAND, 166, 154, 0); }
        if (t > 165 && t < 202) {
            put(1, Res.S_GIGGLES_PAIN, 200 + (t & 1) * 2, 112, hop(t, 8, 2000));
            if ((t & 3) == 0) W.part(204 << 12, 114 << 12, 60000, W.rr(-1500, 1500), W.rr(-1500, 1500), 3000, W.P_YEL, 8);
        }
        if (t == 170) { talk(0, "Honk this.", Snd.V_G2A, 30); cuA = Res.S_CPBUTCH_3; }
        if (t == 202) {
            hide(1);
            boom(200, 112, 40000); boom(204, 110, 70000);
            bloodBurst(200, 112, 50000, 34);
            for (int k = 0; k < 3; k++) { put(6 + k, Res.S_GIBS, 186 + k * 14, 106 + (k & 1) * 12, 0); scale(6 + k, 300); }
            W.shake = 18;
        }
        if (t == 206) boom(196, 114, 20000);
        if (t >= 204 && t <= 216) { put(9, Res.S_CS_NOSE, lerp(t, 204, 12, 200, 184), lerp(t, 204, 12, 112, 186), 30000 + hop(t - 204, 24, 30000)); scale(9, 700); }
        if (t == 217) { hide(9); Snd.sfx(Snd.HONK); splat(BLOOD, BLOOD2); }
        if (t > 206 && t < 250 && (t & 1) == 0)                       // it rains clown
            W.part(W.rr(170, 230) << 12, W.rr(96, 130) << 12, 90000, 0, 0, -2000, (t & 2) == 0 ? W.P_RED : W.P_DRED, 30);
        // the rescue party arrives...
        if (t == 252) { put(2, Res.S_CS_CAR, 300, 124, 0); scale(2, 430); Snd.sfx(Snd.HONK); }
        if (t >= 252 && t <= 284) put(2, Res.S_CS_CAR, ease(t, 252, 32, 300, 218), lerp(t, 252, 32, 124, 118), hop(t, 8, 2500));
        camMove(t, 250, 20, 184, 190, 3072, 184, 190, 3072 + 200);
        camMove(t, 278, 20, 184, 190, 3072 + 200, 184, 192, 3072 + 60);
        if (t > 284 && t < 362) put(2, Res.S_CS_CAR, 218, 118, t < 326 ? hop(t, 6, 900) : 0);
        for (int k = 0; k < 3; k++) {
            int t0 = 290 + k * 8;
            if (t == t0) Snd.sfx(k % 2 == 0 ? Snd.HONK : Snd.CLOWN);
            if (t >= t0 && t <= t0 + 14) put(3 + k, Res.S_CLOWN_WALK1, lerp(t, t0, 14, 218, CLX[k]), lerp(t, t0, 14, 118, CLY[k]), hop(t - t0, 30, 30000));
            if (t > t0 + 14 && t < 340) put(3 + k, Res.S_CLOWN_PAIN, CLX[k], CLY[k], hop(t, 7, 3000));     // ...and see what is left of the boss
        }
        if (t == 340) { put(0, Res.S_BUTCH_AIM, 166, 154, 0); Snd.sfx(Snd.LAUNCH); for (int k = 0; k < 3; k++) put(3 + k, Res.S_CLOWN_ATTACK, CLX[k], CLY[k], 0); }
        if (t >= 340 && t <= 358) { put(10, Res.S_PBOMB, lerp(t, 340, 18, 166, 214), lerp(t, 340, 18, 150, 120), 40000 + hop(t - 340, 36, 26000)); scale(10, 500); }
        if (t == 359) {
            hide(10); hide(2); for (int k = 0; k < 3; k++) hide(3 + k);
            boom(218, 118, 20000); boom(206, 126, 40000); boom(190, 128, 30000);
            bloodBurst(200, 124, 40000, 40);
            put(9, Res.S_CS_BALLOON, 214, 120, 0);
            for (int k = 0; k < 3; k++) { put(3 + k, Res.S_GIBS, 194 + k * 12, 124 + (k & 1) * 6, 0); scale(3 + k, 300); }
            W.shake = 22; W.flashPick = 120;
            put(0, Res.S_BUTCH_STAND, 166, 154, 0);
        }
        if (t == 365 || t == 372) boom(214 - (t & 7) * 3, 118, 30000);
        if (t > 359 && t < 520 && cutA[9] >= 0) { W.tZ[cutA[9]] = (t - 359) * 1400; W.tX[cutA[9]] = (214 + (E.sin(t * 90) * 5 >> 16)) << 12; }
        if (t > 362 && t < 520 && (t % 12) == 0) W.fx(W.FX_SMOKE, 212 << 12, 120 << 12, 8000, 14);
        if (t == 386) { talk(0, "Who ordered extra crispy?", Snd.V_GIB, 50); cuA = Res.S_CPGORE_1; cuB = Res.S_CPGORE_2; }
        if (t == 448) cutCard(2);
        fadeOut(t, 510, 22);
        if (t > 534) endCut();
    }

    /** Gory episode 3: batter up. The bat does not make it to the moon. */
    static void cutG3(int t) {
        if (t == 1) {
            cam(256, 48, 1360);
            put(0, Res.S_BUTCH_STAND, 234, 87, 0);
            W.fx(W.FX_SMOKE, 238 << 12, 84 << 12, 20000, 14);
            Snd.sfx(Snd.TELE);
        }
        fadeIn(t, 1, 20);
        if (t > 1 && t < 156) {
            int a = t * 130;
            put(1, ((t / 3) & 1) == 0 ? Res.S_CS_CBAT1 : Res.S_CS_CBAT2, 236 + (E.cos(a) * 14 >> 16), 84 + (E.sin(a) * 6 >> 16),
                    52000 + (E.sin(t * 300) >> 3));
        }
        if (t == 30) talk(4, "You have not seen the last of me, gravedigger!", Snd.V_C3A, 56);
        if (t == 100) put(0, Res.S_BUTCH_WIND, 234, 87, 0);
        if (t == 108) { talk(0, "Batter up.", Snd.V_C3B, 32); cuA = Res.S_CPBUTCH_3; }
        if (t == 156) {
            put(0, Res.S_BUTCH_SWING, 234, 87, 0);
            hide(1);
            Snd.sfx(Snd.BONK); Snd.sfx(Snd.MDIE); Snd.sfx(Snd.BAT);
            bloodBurst(236, 86, 52000, 44);
            put(2, Res.S_BAT_DEAD, 236, 86, 52000);
            W.shake = 14;
        }
        if (t > 156 && t <= 180) put(2, Res.S_BAT_DEAD, lerp(t, 156, 24, 236, 240), lerp(t, 156, 24, 86, 92), lerp(t, 156, 24, 52000, 0) + hop(t - 156, 48, 6000));
        if (t == 159) splat(BLOOD, BLOOD2);
        if (t == 182) { Snd.sfx(Snd.HIT); put(0, Res.S_BUTCH_STAND, 234, 87, 0); }
        if (t == 196) { talk(0, "Pest control.", Snd.V_KBAT, 36); cuA = Res.S_CPGORE_1; cuB = Res.S_CPGORE_2; }
        if (t == 260) cutCard(3);
        if (t == 300) say(0, "Happy Halloween.", Snd.V_WIN);
        fadeOut(t, 340, 24);
        if (t > 366) endCut();
    }

    /** Gory episode 4: the doctor's ultimate creation comes home to daddy. */
    static void cutG4(int t) {
        if (t == 1) {
            cam(184, 228, 3072);
            put(1, Res.S_CS_WRECK, 184, 128, 0);
            scale(1, 512);
            put(0, Res.S_BUTCH_STAND, 165, 147, 0);
            put(2, Res.S_CS_DOC, 190, 124, 0);
            hide(2);
        }
        fadeIn(t, 1, 22);
        camMove(t, 1, 60, 184, 228, 3072, 184, 188, 3072);
        if (t < 400 && (t % 14) == 0) W.fx(W.FX_SMOKE, (176 + (t * 7) % 18) << 12, (124 + (t * 5) % 6) << 12, 22000, 14);
        if (t < 400 && (t % 9) == 0) W.spark((184 + (t * 13) % 24 - 12) << 12, 128 << 12, 26000, 4, W.P_CYAN);
        if (t >= 30 && t <= 46) put(2, Res.S_CS_DOC, lerp(t, 30, 16, 190, 204), lerp(t, 30, 16, 126, 144), hop(t - 30, 32, 20000));
        if (t == 30) Snd.sfx(Snd.ROBOT);
        if (t >= 46 && t < 156) put(2, ((t / 5) & 1) == 0 ? Res.S_CS_DOCRANT : Res.S_CS_DOC, 204, 144, hop(t, 10, 3500));
        if (t == 52) talk(5, "You ruined my masterpiece!", Snd.V_C4D, 50);
        if (t == 102) put(0, Res.S_BUTCH_POINT, 165, 147, 0);
        if (t == 104) talk(0, "Should've stuck to pumpkins, Doc.", Snd.V_C4A, 46);
        if (t == 156) { put(2, Res.S_CS_DOCRANT, 204, 144, 0); put(0, Res.S_BUTCH_STAND, 165, 147, 0); W.flashPick = 60; Snd.sfx(Snd.TELE); }
        if (t == 160) talk(5, "Behold my ultimate creation!", Snd.V_C4E, 40);
        if (t >= 202 && t <= 240) { put(3, ((t / 3) & 1) == 0 ? Res.S_CS_MINIBOT1 : Res.S_CS_MINIBOT2, lerp(t, 202, 38, 236, 170), lerp(t, 202, 38, 166, 152), 0); scale(3, 440); }
        if (t == 220) put(2, Res.S_CS_DOC, 204, 144, 0);
        if (t >= 240 && t < 252) put(3, Res.S_CS_MINIBOT1, lerp(t, 240, 12, 170, 172), 152, hop(t - 240, 24, 4000));
        if (t == 240) Snd.sfx(Snd.BONK);
        if (t == 254) { talk(0, "Fetch.", Snd.V_G4A, 26); cuA = Res.S_CPBUTCH_3; }
        // punted straight back to its maker
        if (t == 282) { put(0, Res.S_BUTCH_KICK, 165, 147, 0); Snd.sfx(Snd.BONK); W.shake = 6; }
        if (t >= 282 && t <= 298) put(3, Res.S_CS_MINIBOT2, lerp(t, 282, 16, 172, 204), lerp(t, 282, 16, 152, 146), hop(t - 282, 32, 26000));
        if (t == 299) { put(2, Res.S_CS_DOCRANT, 204, 144, 0); put(3, Res.S_CS_MINIBOT1, 204, 146, 26000); put(0, Res.S_BUTCH_STAND, 165, 147, 0); }
        if (t == 302) talk(5, "My baby!", Snd.V_G4B, 30);
        if (t > 332 && t < 348) {                                     // beep... beep. beepbeepbeep
            put(3, (t & 1) == 0 ? Res.S_CS_MINIBOT1 : Res.S_CS_MINIBOT2, 204 + (t & 1), 146, 26000);
            if ((t & 1) == 0) { W.spark(204 << 12, 146 << 12, 30000, 3, W.P_CYAN); Snd.sfx(Snd.CLICK); }
        }
        if (t == 348) {
            hide(2); hide(3);
            boom(204, 144, 26000); boom(208, 140, 50000);
            bloodBurst(204, 144, 36000, 40);
            for (int k = 0; k < 2; k++) { put(6 + k, Res.S_GIBS, 196 + k * 16, 140 + k * 6, 0); scale(6 + k, 300); }
            W.shake = 18; W.flashPick = 100;
        }
        if (t >= 350 && t <= 364) { put(5, Res.S_CS_GOGGLES, lerp(t, 350, 14, 204, 186), lerp(t, 350, 14, 144, 176), 30000 + hop(t - 350, 28, 26000)); scale(5, 900); }
        if (t == 365) { put(5, Res.S_CS_GOGGLES, 186, 176, 0); Snd.sfx(Snd.CLICK); }
        if (t == 354) splat(BLOOD, BLOOD2);
        if (t == 388) { talk(0, "Recycled.", Snd.V_WIN4, 30); cuA = Res.S_CPGORE_1; cuB = Res.S_CPGORE_2; }
        // the reactor goes critical; the doctor's portal is still open
        if (t == 410) { Snd.sfx(Snd.TELE); W.flashPick = 90; W.shake = 6; }
        if (t >= 410 && t < 520) put(4, ((t / 3) & 1) == 0 ? Res.S_CS_PORTAL1 : Res.S_CS_PORTAL2, 211, 110, 0);
        if (t >= 410 && t < 430) scale(4, lerp(t, 410, 20, 40, 380));
        if (t > 410 && t < 520 && (t % 9) == 0) { boom(170 + (t * 13) % 30, 116 + (t * 7) % 18, 10000 + (t * 37) % 40000); W.shake = 8; }
        if (t == 432) { talk(0, "Time to go home.", Snd.V_C4C, 34); cuA = Res.S_CPGORE_1; cuB = Res.S_CPGORE_2; }
        walk(0, t, 468, 44, 165, 147, 211, 113, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        camMove(t, 468, 44, 184, 188, 3072, 190, 186, 3072 + 80);
        if (t == 512) { hide(0); Snd.sfx(Snd.TELE); }
        if (t == 518) { boom(184, 128, 30000); boom(176, 120, 10000); boom(194, 134, 50000); W.flashPick = 255; W.shake = 24; }
        if (t >= 524 && t < 532) fadeOut(t, 524, 6);
        if (t == 534) cutCard(4);
        if (t > 610) endCut();
    }

    // ---- episode 5 actors: 0 Butch, 1 Seven Death's rubble, 2 the Jade Skull, 3 Crane, 4 the shrunken head, 5 Crane's bones
    // places (1/16 cell): rubble (184,84), Butch (158,140), Crane runs in from (290,170) to (206,112)
    static final int CRX = 206, CRY = 112;
    static int cutGlow;                      // the skull's green light washing over the scene (0..255)

    /** Episode 5, both styles: Seven Death lies in rubble. Professor Crane runs in with the Jade Skull, wants its power
     *  and asks it for eternal life. The skull answers. (t up to 300; the two endings part ways after that.) */
    static void cut5open(int t) {
        if (t == 1) {
            cam(184, 240, 3072);
            put(1, Res.S_CS_RUBBLE, 184, 84, 0);
            scale(1, 600);
            put(0, Res.S_BUTCH_STAND, 158, 140, 0);
            put(3, Res.S_CS_CRANE, 290, 170, 0);
            hide(3);
            cutGlow = 0;
        }
        fadeIn(t, 1, 22);
        camMove(t, 1, 60, 184, 240, 3072, 186, 196, 3072 - 20);
        // what's left of Seven Death still smoulders green
        if (t < 300 && (t % 11) == 0) W.spark((176 + (t * 7) % 18) << 12, 84 << 12, 8000, 3, W.P_GREEN);
        if (t < 300 && (t % 17) == 0) W.fx(W.FX_DUST, (176 + (t * 5) % 16) << 12, 86 << 12, 2000, 14);
        if (t == 30) put(0, Res.S_BUTCH_POINT, 158, 140, 0);
        if (t == 32) talk(0, "Stay dead this time.", Snd.V_KILL3, 40);
        // the professor comes running out from behind the pillar, the skull held high
        if (t == 72) put(0, Res.S_BUTCH_STAND, 158, 140, 0);
        walk(3, t, 74, 36, 290, 170, CRX, CRY, Res.S_CS_CRANERUN1, Res.S_CS_CRANERUN2);
        camMove(t, 74, 36, 186, 196, 3072 - 20, 200, 150, 3072 + 20);       // in close as he arrives
        if (t == 111) put(3, Res.S_CS_CRANE, CRX, CRY, 0);
        if (t == 114) talk(6, "Out of my way, gravedigger! With his lordship dead, the skull's power is mine!", Snd.V_C5A, 84);
        if (t == 200) put(0, Res.S_BUTCH_SHRUG, 158, 140, 0);
        // he holds the skull up to the light; it starts to glow
        camMove(t, 200, 24, 200, 150, 3072 + 20, 206, 138, 3072);
        if (t == 204) { put(3, Res.S_CS_CRANERANT, CRX, CRY, 0); Snd.sfx(Snd.SECRET); }
        if (t == 208) say(6, "Skull of Seven Death! Grant me eternal life!", Snd.V_C5B);
        if (t >= 204 && t < 300 && (t % 4) == 0)
            W.part((CRX + 3) << 12, CRY << 12, 76000, W.rr(-2500, 2500), W.rr(-2500, 2500), W.rr(0, 3000), W.P_GREEN, 14);
        if (t >= 210 && t < 262) cutGlow = 30 + ((t - 210) & 15) * 4;
        if (t == 262) { cutGlow = 230; W.shake = 10; Snd.sfx(Snd.SEVEN); }
        if (t == 266) talk(7, "Eternal life? Granted.", Snd.V_C5C, 44);
    }

    /** Then the dawn: Butch walks out of the temple into the jungle (the east half of the map). */
    static void cut5dawn(int t, int t0, boolean head) {
        if (t == t0) {
            for (int k = 0; k < cutA.length; k++) hide(k);
            W.flashDmg = 0; splatT0 = -1; cutGlow = 0;
            cam(568, 236, 3072);
            put(0, Res.S_BUTCH_WALK1, 568, 92, 0);
        }
        fadeIn(t, t0, 18);
        int f = t - t0;
        if (f >= 0 && f <= 60) {
            int x = lerp(t, t0, 60, 568, 562), y = lerp(t, t0, 60, 92, 176);
            put(0, head ? (((f / 6) & 1) == 0 ? Res.S_BUTCH_CWALK1 : Res.S_BUTCH_CWALK2) : (((f / 5) & 1) == 0 ? Res.S_BUTCH_WALK1 : Res.S_BUTCH_WALK2), x, y, 0);
            if (head) { put(4, Res.S_CS_SHRUNK, x, y + 3, 24000 + hop(f, 12, 1500)); scale(4, 330); }
        }
        if (f == 61) {
            put(0, head ? Res.S_BUTCH_CARRY : Res.S_BUTCH_STAND, 562, 176, 0);
            if (head) put(4, Res.S_CS_SHRUNK, 562, 179, 24000);
        }
        camMove(t, t0, 60, 568, 236, 3072, 566, 214, 3072 + 20);
        if (f == 66) { talk(0, "Happy Day of the Dead.", Snd.V_C5F, 40); cuA = Res.S_CPBUTCH_3; }
        if (f == 116) cutCard(5);
        fadeOut(t, t0 + 170, 24);
        if (t > t0 + 196) endCut();
    }

    /** Episode 5 (classic): eternal life... at about four inches tall. */
    static void cut5(int t) {
        cut5open(t);
        // close on the professor: he shrinks in four jolts of green light
        if (t == 310) cam(206, 132, 3072);
        if (t == 312) say(6, "Wait! Not like thiiis!", Snd.V_C5D);
        for (int k = 0; k < 4; k++) {
            int t0 = 316 + k * 12;
            if (t == t0) {
                scale(3, 256 - (k + 1) * 50);
                put(3, (k & 1) == 0 ? Res.S_CS_CRANE : Res.S_CS_CRANERANT, CRX, CRY, 0);
                cutGlow = 200; W.shake = 4;
                W.spark(CRX << 12, CRY << 12, 30000 - k * 6000, 10, W.P_GREEN);
                Snd.sfx(Snd.TELE);
            }
        }
        if (t == 364) {
            hide(3);
            W.fx(W.FX_SMOKE, CRX << 12, CRY << 12, 4000, 12);
            put(4, Res.S_CS_SHRUNK, CRX, CRY, 20000); scale(4, 430);
            put(2, Res.S_CS_JSKULL, CRX + 6, CRY - 2, 30000); scale(2, 370);
        }
        if (t > 364 && t <= 376) {
            put(4, Res.S_CS_SHRUNK, CRX, CRY + (t - 364) / 3, lerp(t, 364, 12, 20000, 0) + hop(t - 364, 24, 4000));
            put(2, Res.S_CS_JSKULL, CRX + 6, CRY - 2, lerp(t, 364, 12, 30000, 0));
        }
        if (t == 376) Snd.sfx(Snd.BONK);
        if (t >= 378 && t < 390) put(4, Res.S_CS_SHRUNK, CRX + ((t & 2) == 0 ? 1 : -1), CRY + 4, 0);     // a tiny head, hopping mad
        // Butch strolls over and picks him up
        if (t == 390) { cam(214, 150, 2586); put(4, Res.S_CS_SHRUNK, CRX, CRY + 4, 0); }
        walk(0, t, 394, 30, 158, 140, CRX - 10, CRY + 10, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        if (t == 425) { put(0, Res.S_BUTCH_CARRY, CRX - 10, CRY + 10, 0); put(4, Res.S_CS_SHRUNK, CRX - 10, CRY + 13, 24000); }
        if (t > 425 && t < 538) put(4, Res.S_CS_SHRUNK, CRX - 10 + (E.sin(t * 120) * 2 >> 16), CRY + 13, 24000);
        if (t == 430) { talk(6, "Unhand me, you oaf! I am immortal!", Snd.V_C5G, 46); cuA = Res.S_CPSHRUNK_1; cuB = Res.S_CPSHRUNK_2; }
        if (t == 480) talk(0, "Eternal life. As a keychain.", Snd.V_C5E, 44);
        if (t >= 524 && t < 540) fadeOut(t, 524, 14);
        if (t >= 540) cut5dawn(t, 540, true);
    }

    /** Gory episode 5: the skull grants the wish. Faces were not part of the deal. */
    static void cutG5(int t) {
        cut5open(t);
        if (t == 314) { cam(206, 132, 3072); put(3, Res.S_CS_CRANERANT, CRX, CRY, 0); cutGlow = 160; }
        if (t == 320) {
            closeUp(Res.S_CPMELT_1, Res.S_CPMELT_2, 64, 6, 0x30c060, 0x400000, 0);
            say(6, "My face! My beautiful face!", Snd.V_G5A);
            cuShake = 6;
        }
        if (t > 320 && t < 384 && (t % 9) == 0) cuShake = 5;
        // back on the professor, close: the flesh slides off, the skull blazes, and down he goes
        if (t == 384) put(3, Res.S_CS_CRANEMELT2, CRX, CRY, 0);
        if (t > 384 && t < 412) {
            put(3, Res.S_CS_CRANEMELT2, CRX + (t & 1) * 2, CRY, 0);
            cutGlow = 90;
            if ((t & 1) == 0) W.part((CRX + 1) << 12, CRY << 12, 54000, W.rr(-3000, 3000), W.rr(-3000, 3000), W.rr(0, 2000), (t & 2) == 0 ? W.P_RED : W.P_GREEN, 18);
        }
        if (t == 386) Snd.sfx(Snd.SCREAM);
        if (t == 412) {
            hide(3);
            put(5, Res.S_CS_CRANEBONES, CRX, CRY + 2, 0); scale(5, 534);
            bloodBurst(CRX, CRY, 30000, 40);
            W.spark(CRX << 12, CRY << 12, 40000, 10, W.P_GREEN);
            splat(BLOOD, BLOOD2);
            Snd.sfx(Snd.MDIE); W.shake = 12; cutGlow = 0;
        }
        // the skull rolls out of the mess, right up to Butch's boots
        if (t >= 414 && t <= 434) { put(2, Res.S_CS_JSKULL, lerp(t, 414, 20, CRX, 172), lerp(t, 414, 20, CRY, 132), hop(t - 414, 10, 2500)); scale(2, 374); }
        if (t == 424) cam(214, 150, 2450);
        if (t > 412 && W.flashDmg > 0) W.flashDmg -= 3;
        if (t == 438) put(0, Res.S_BUTCH_POINT, 158, 140, 0);
        if (t == 442) { talk(0, "Should've left it in the ground, Prof.", Snd.V_G5B, 50); cuA = Res.S_CPGORE_1; cuB = Res.S_CPGORE_2; }
        walk(0, t, 496, 20, 158, 140, 168, 134, Res.S_BUTCH_WALK1, Res.S_BUTCH_WALK2);
        if (t == 517) { put(0, Res.S_BUTCH_STAND, 168, 134, 0); hide(2); Snd.sfx(Snd.PICKUP); }
        if (t >= 528 && t < 544) fadeOut(t, 528, 14);
        if (t >= 544) cut5dawn(t, 544, false);
    }

    static void drawCut(Graphics gr) {
        drawGame(gr);
        if (splatT0 >= 0) drawSplat(gr, SH / 10, SH - (hudH > fSmall.getHeight() * 3 + 8 ? hudH : fSmall.getHeight() * 3 + 8));
        int top = SH / 10, bot = hudH;
        int need = fSmall.getHeight() * 3 + 8;
        if (cutLineT > 0 && cutLine != null) {          // a long line on a big font: the subtitle band grows to fit all of it
            int h = fSmall.getHeight() + wrap(null, cutLine, 0, 0, SW - 12, 0, fSmall) + 6;
            if (h > cutBand) cutBand = h > SH / 2 ? SH / 2 : h;
        }
        if (need < cutBand) need = cutBand;
        if (bot < need) bot = need;
        gr.setColor(0);
        gr.fillRect(0, 0, SW, top);
        gr.fillRect(0, SH - bot, SW, bot);
        gr.setFont(fSmall);
        if (cutLineT > 0 && cutLine != null) {
            int y = SH - bot + 3;
            outline(gr, cutWho, 6, y, cutWhoCol, Graphics.TOP | Graphics.LEFT);
            wrap(gr, cutLine, 6, y + fSmall.getHeight(), SW - 12, 0xfff4e0, fSmall);
        }
        if (skipArmed && (tick & 16) != 0) outline(gr, "5: skip", SW - 4, 2, 0x806050, Graphics.TOP | Graphics.RIGHT);
        if (capT0 >= 0 && cutT >= capT0) {                    // the end card drops in and lands with a thud
            int f = cutT - capT0, vh = SH - bot;
            int ch = capImg != null ? capImg.getHeight() : fBig.getHeight();
            int ty = top + (vh - top - ch) / 3;
            int y = f < 8 ? top - ch + (ty - top + ch) * f * f / 64 : ty;
            if (f >= 8 && f < 14) y += (14 - f) * ((f & 1) == 0 ? 1 : -1);
            if (capImg != null) gr.drawImage(capImg, SW / 2, y, Graphics.TOP | Graphics.HCENTER);
            gr.setFont(fSmall);
            if (f > 14) outline(gr, clip("EPISODE " + capEp + " COMPLETE", fSmall, SW - 6), SW / 2, y + ch + 4, 0xffd080, Graphics.TOP | Graphics.HCENTER);
        }
    }

    // ================================================================== drawing

    void draw(Graphics gr) {
        gr.setClip(0, 0, SW, SH);
        switch (state) {
            case S_LOAD: drawLoad(gr); break;
            case S_TITLE: drawTitle(gr); break;
            case S_SKILL:
                drawMenuScreen(gr, "CHOOSE YOUR FRIGHT", SKILLS);
                if (warp > 1 || W.god) {
                    gr.setFont(fSmall);
                    String wt = (warp > 1 ? "WARP TO LEVEL " + (firstLevel(episode) + warp - 1) + "  " : "") + (W.god ? "GOD MODE" : "");
                    outline(gr, clip(wt, fSmall, SW - 6), SW / 2, SH - fSmall.getHeight() - 4, 0xc080ff, Graphics.TOP | Graphics.HCENTER);
                }
                break;
            case S_STORY: case S_END: drawStory(gr); break;
            case S_CARD: drawCard(gr); break;
            case S_PLAY: drawGame(gr); break;
            case S_PAUSE: drawGame(gr); dim(gr); drawMenuItems(gr, "PAUSED", PAUSE_ITEMS, SH / 3); break;
            case S_MAP: drawMap(gr); break;
            case S_OPT:
                if (optReturn == S_PAUSE) { drawGame(gr); dim(gr); } else drawBg(gr, true);
                drawMenuItems(gr, "OPTIONS", optItems(), SH / 5);
                break;
            case S_HELP: drawHelp(gr); break;
            case S_TEST:
                drawBg(gr, true);
                drawMenuItems(gr, "TEST MENU", testItems(), testItemsShort(), SH / 5);
                gr.setFont(fSmall);
                outline(gr, clip("4 6: change   5: go", fSmall, SW - 6), SW / 2, SH - fSmall.getHeight() - 2, 0x9080a0, Graphics.TOP | Graphics.HCENTER);
                break;
            case S_INTER: drawInter(gr); break;
            case S_DEAD: drawGame(gr); drawDead(gr); break;
            case S_CUT: drawCut(gr); break;
            case S_EPI:
                drawBg(gr, true);
                drawMenuItems(gr, "CHOOSE EPISODE", EPISODES, EPISODES_S, SH / 3);
                break;
        }
        if (showFps && state == S_PLAY) {
            gr.setFont(fSmall);
            outline(gr, fps + " fps", SW - 2, 2, 0x80ff80, Graphics.TOP | Graphics.RIGHT);
            outline(gr, Snd.status(), SW - 2, 3 + fSmall.getHeight(), 0x80ff80, Graphics.TOP | Graphics.RIGHT);
        }
    }

    static void drawLoad(Graphics gr) {
        gr.setColor(0x080408);
        gr.fillRect(0, 0, SW, SH);
        gr.setColor(0xff7010);
        Font f = Font.getFont(Font.FACE_PROPORTIONAL, Font.STYLE_BOLD, Font.SIZE_MEDIUM);
        gr.setFont(f);
        gr.drawString("BUTCH GRAVES 3D", SW / 2, SH / 2 - 20, Graphics.TOP | Graphics.HCENTER);
        gr.setColor(0x401808);
        gr.fillRect(SW / 6, SH / 2 + 8, SW * 2 / 3, 6);
        gr.setColor(0xff8020);
        gr.fillRect(SW / 6, SH / 2 + 8, SW * 2 / 3 * loadPct / 100, 6);
        gr.setColor(0x806050);
        gr.setFont(Font.getFont(Font.FACE_PROPORTIONAL, Font.STYLE_PLAIN, Font.SIZE_SMALL));
        gr.drawString("digging up graves...", SW / 2, SH / 2 + 20, Graphics.TOP | Graphics.HCENTER);
    }

    static void drawBg(Graphics gr, boolean dimmed) {
        if (imgTitle != null) gr.drawImage(imgTitle, 0, 0, Graphics.TOP | Graphics.LEFT);
        else { gr.setColor(0x100810); gr.fillRect(0, 0, SW, SH); }
        if (dimmed) dim(gr);
    }

    static void dim(Graphics gr) {
        for (int y = 0; y < SH; y += 4) gr.drawRGB(shade, 0, SW, 0, y, SW, SH - y < 4 ? SH - y : 4, true);
    }

    // ---- text that always fits: phone system fonts vary a lot in size, so everything is measured
    /** The biggest font, starting at pref and going down, in which s fits into w pixels (fSmall if none does). */
    static Font fit(String s, int w, Font pref) {
        if (pref == fBig) { if (fBig.stringWidth(s) <= w) return fBig; pref = fMed; }
        if (pref == fMed && fMed.stringWidth(s) <= w) return fMed;
        return fSmall;
    }

    /** s shortened with ".." so that it fits into w pixels in font f. */
    static String clip(String s, Font f, int w) {
        if (f.stringWidth(s) <= w) return s;
        int n = s.length();
        while (n > 1 && f.substringWidth(s, 0, n) + f.stringWidth("..") > w) n--;
        return s.substring(0, n) + "..";
    }

    /** Centred text in the biggest font (from pref down) that fits; wraps onto more lines if even the small font is too wide.
     *  Returns the height used. */
    static int centerText(Graphics gr, String s, int y, int col, Font pref) {
        int w = SW - 6;
        Font f = fit(s, w, pref);
        gr.setFont(f);
        if (f.stringWidth(s) <= w) { outline(gr, s, SW / 2, y, col, Graphics.TOP | Graphics.HCENTER); return f.getHeight(); }
        int y0 = y, i = 0, n = s.length();
        while (i < n) {
            int e = i, lastSp = -1;
            while (e < n) {
                if (s.charAt(e) == ' ') lastSp = e;
                if (f.substringWidth(s, i, e - i + 1) > w) break;
                e++;
            }
            if (e < n && lastSp > i) e = lastSp;
            if (e == i) e = i + 1;
            outline(gr, s.substring(i, e), SW / 2, y, col, Graphics.TOP | Graphics.HCENTER);
            y += f.getHeight();
            i = e;
            while (i < n && s.charAt(i) == ' ') i++;
        }
        return y - y0;
    }

    /** Height centerText would use. */
    static int centerTextH(String s, Font pref) {
        int w = SW - 6;
        Font f = fit(s, w, pref);
        if (f.stringWidth(s) <= w) return f.getHeight();
        return f.getHeight() * ((f.stringWidth(s) + w - 1) / w + 1);
    }

    /** Menu items: one font for the whole list (the biggest that fits), "> <" markers or a highlight bar, the short
     *  label when the long one is too wide, and a scrolling (marquee) selected item if even that does not fit. */
    static void drawItems(Graphics gr, String[] items, String[] alt, int y, int lh, Font pref, boolean[] grey) {
        int w = SW - 6;
        Font f = pref;
        while (true) {
            boolean ok = true;
            for (int i = 0; i < items.length && ok; i++) {
                String t = items[i];
                if (f.stringWidth(t) > w && (alt == null || f.stringWidth(alt[i]) > w)) ok = false;
            }
            if (ok || f == fSmall) break;
            f = f == fBig ? fMed : fSmall;
        }
        gr.setFont(f);
        if (lh < f.getHeight()) lh = f.getHeight();
        int mw = f.stringWidth("> <  ");
        for (int i = 0; i < items.length; i++) {
            String t = items[i];
            if (f.stringWidth(t) > w && alt != null && f.stringWidth(alt[i]) <= w) t = alt[i];
            boolean sl = i == sel;
            int col = sl ? ((tick & 4) != 0 ? 0xffe060 : 0xffa020) : (grey != null && grey[i] ? 0x705850 : 0xd8c8b0);
            int yy = y + i * lh;
            int tw = f.stringWidth(t);
            if (sl && tw + mw > w) {                            // no room for the markers: a highlight bar instead
                gr.setColor(0x501a08);
                gr.fillRect(1, yy - 1, SW - 2, f.getHeight() + 1);
                gr.setColor(0xff7010);
                gr.drawRect(1, yy - 1, SW - 3, f.getHeight());
            }
            if (tw <= w) {
                outline(gr, sl && tw + mw <= w ? "> " + t + " <" : t, SW / 2, yy, col, Graphics.TOP | Graphics.HCENTER);
            } else if (sl) {                                    // marquee
                int over = tw - w + 8, ph = (tick * 2) % (over * 2 + 60);
                int off = ph < 30 ? 0 : ph < 30 + over ? ph - 30 : ph < 60 + over ? over : over - (ph - 60 - over);
                if (off < 0) off = 0;
                gr.setClip(3, yy - 1, SW - 6, f.getHeight() + 2);
                outline(gr, t, 4 - off, yy, col, Graphics.TOP | Graphics.LEFT);
                gr.setClip(0, 0, SW, SH);
            } else outline(gr, clip(t, f, w), SW / 2, yy, col, Graphics.TOP | Graphics.HCENTER);
        }
    }

    static void outline(Graphics gr, String s, int x, int y, int col, int anchor) {
        gr.setColor(0x000000);
        gr.drawString(s, x - 1, y, anchor);
        gr.drawString(s, x + 1, y, anchor);
        gr.drawString(s, x, y - 1, anchor);
        gr.drawString(s, x, y + 1, anchor);
        gr.drawString(s, x + 1, y + 1, anchor);
        gr.setColor(col);
        gr.drawString(s, x, y, anchor);
    }

    static void drawTitle(Graphics gr) {
        drawBg(gr, false);
        int ly = SH / 40;
        gr.drawImage(imgLogo, SW / 2, ly, Graphics.TOP | Graphics.HCENTER);
        int y0 = ly + imgLogo.getHeight() + 2;
        gr.setFont(fSmall);

        // menu at the bottom on a dark band
        Font f = SH >= 240 ? fMed : fSmall;
        if (f.getHeight() * TITLE_ITEMS.length + 12 > SH / 2) f = fSmall;
        int lh = f.getHeight() + 2;
        int my = SH - lh * TITLE_ITEMS.length - 8;
        String tag = fSmall.stringWidth("THE HALLOWEEN SAGA") < SW - 4 ? "THE HALLOWEEN SAGA" : "HALLOWEEN SAGA";
        if (y0 + fSmall.getHeight() < my - 4) outline(gr, tag, SW / 2, y0, 0xffb040, Graphics.TOP | Graphics.HCENTER);
        for (int y = my - 4; y < SH; y += 4) gr.drawRGB(shade, 0, SW, 0, y, SW, SH - y < 4 ? SH - y : 4, true);
        boolean[] grey = new boolean[TITLE_ITEMS.length];
        grey[1] = !hasSave;
        drawItems(gr, TITLE_ITEMS, null, my, lh, f, grey);
    }

    static void drawMenuScreen(Graphics gr, String title, String[] items) {
        drawBg(gr, true);
        drawMenuItems(gr, title, items, SH / 3);
    }

    static void drawMenuItems(Graphics gr, String title, String[] items, int y) {
        drawMenuItems(gr, title, items, null, y);
    }

    static void drawMenuItems(Graphics gr, String title, String[] items, String[] alt, int y) {
        Font tf = SH >= 200 ? fBig : fMed;
        Font f = SH >= 240 ? fMed : fSmall;
        int th = centerTextH(title, tf);
        int lh = f.getHeight() + 3;
        // shrink to fit: smaller font first, then move the block up
        if (y + items.length * lh > SH - 4) { f = fSmall; lh = f.getHeight() + 2; tf = tf == fBig ? fMed : fSmall; th = centerTextH(title, tf); }
        if (y + items.length * lh > SH - 4) y = SH - 4 - items.length * lh;
        if (y < th + 6) { y = th + 6; lh = (SH - 4 - y) / items.length; if (lh < f.getHeight()) lh = f.getHeight(); }
        int ty = y - th - (y > th + 8 ? 8 : 3);
        centerText(gr, title, ty < 1 ? 1 : ty, 0xff6a10, tf);
        drawItems(gr, items, alt, y, lh, f, null);
    }

    static int helpTop, helpMax;
    static final String[] HELP = {"2 / UP: walk forward", "8 / DOWN: walk back", "4 6 / LEFT RIGHT: turn", "1 3: strafe",
            "5 / FIRE: shoot", "0: use / open / pull levers", "7 9: change weapon", "#: jump", "*: automap", "Soft key: menu", "",
            "Double-tap 2 and hold it to SPRINT.", "", "Doors open when you walk into them. Find the skull keys!", "",
            "Secret walls look like any other wall: press 0 on a suspicious one."};
    static String[] helpCache, helpText = HELP, helpCacheSrc;
    static int helpCacheW;

    /** The help text word-wrapped for the current font and width. */
    static String[] helpLines(Font f, int w) {
        if (helpCache != null && helpCacheW == w && helpCacheSrc == helpText) return helpCache;
        java.util.Vector v = new java.util.Vector();
        for (int k = 0; k < helpText.length; k++) {
            String s = helpText[k];
            if (s.length() == 0 || f.stringWidth(s) <= w) { v.addElement(s); continue; }
            int i = 0, n = s.length();
            while (i < n) {
                int e = i, lastSp = -1;
                while (e < n) {
                    if (s.charAt(e) == ' ') lastSp = e;
                    if (f.substringWidth(s, i, e - i + 1) > w) break;
                    e++;
                }
                if (e < n && lastSp > i) e = lastSp;
                if (e == i) e = i + 1;
                v.addElement(s.substring(i, e));
                i = e;
                while (i < n && s.charAt(i) == ' ') i++;
            }
        }
        helpCache = new String[v.size()];
        v.copyInto(helpCache);
        helpCacheW = w;
        helpCacheSrc = helpText;
        return helpCache;
    }

    static void drawHelp(Graphics gr) {
        drawBg(gr, true);
        Font tf = SH >= 200 ? fMed : fSmall;
        int th = centerText(gr, helpText == CODES ? "CHEAT CODES" : "CONTROLS", 4, 0xff6a10, tf);
        Font f = fSmall;
        gr.setFont(f);
        String[] L = helpLines(f, SW - 8);
        int lh = f.getHeight();
        int top = 8 + th, bottom = SH - lh - 6;
        int fit = (bottom - top) / lh;
        if (fit < 1) fit = 1;
        helpMax = L.length > fit ? L.length - fit : 0;
        if (helpTop > helpMax) helpTop = helpMax;
        int y = top;
        for (int i = helpTop; i < L.length && i < helpTop + fit; i++, y += lh) outline(gr, L[i], SW / 2, y, 0xe0d0b8, Graphics.TOP | Graphics.HCENTER);
        String hint = helpMax > 0 ? (helpTop < helpMax ? "8: more   5: back" : "2: up   5: back") : "5: back";
        outline(gr, hint, SW / 2, SH - lh - 3, 0xff9030, Graphics.TOP | Graphics.HCENTER);
    }

    static void drawStory(Graphics gr) {
        drawBg(gr, true);
        layoutStory();
        Font f = storyFont();
        gr.setFont(f);
        String[] L = pages[page];
        int left = (stateTick - pageTick) * 2, total = 0, y = 8, lh = f.getHeight();
        for (int k = 0; k < L.length; k++) {
            String l = L[k];
            total += l.length();
            if (left > 0 && l.length() > 0) {
                outline(gr, left >= l.length() ? l : l.substring(0, left), 8, y, 0xffe0c0, Graphics.TOP | Graphics.LEFT);
                left -= l.length();
            }
            y += lh;
        }
        pageLen = total;
        boolean typed = (stateTick - pageTick) * 2 >= total;
        gr.setFont(fSmall);
        int hy = SH - fSmall.getHeight() - 4;
        if (pages.length > 1) outline(gr, (page + 1) + "/" + pages.length, SW - 6, hy, 0xa08070, Graphics.TOP | Graphics.RIGHT);
        if (typed && skipArmed && (tick & 8) != 0) {
            String h = page < pages.length - 1 ? "5: next page" : state == S_END ? "5: the end" : "5: continue";
            outline(gr, h, SW / 2, hy, 0xff9030, Graphics.TOP | Graphics.HCENTER);
        }
    }

    /** Word wrap with outline; returns bottom y. */
    static int wrap(Graphics gr, String s, int x, int y, int w, int col, Font f) {
        int lh = f.getHeight();
        int i = 0, n = s.length();
        while (i < n) {
            int e = i, lastSp = -1;
            while (e < n && s.charAt(e) != '\n') {
                if (s.charAt(e) == ' ') lastSp = e;
                if (f.substringWidth(s, i, e - i + 1) > w) break;
                e++;
            }
            if (e < n && s.charAt(e) != '\n' && lastSp > i) e = lastSp;
            if (gr != null) outline(gr, s.substring(i, e), x, y, col, Graphics.TOP | Graphics.LEFT);     // no Graphics: just measure
            y += lh;
            i = e;
            if (i < n && (s.charAt(i) == ' ' || s.charAt(i) == '\n')) {
                if (s.charAt(i) == '\n' && i + 1 < n && s.charAt(i + 1) == '\n') { y += lh / 2; i++; }
                i++;
            }
        }
        return y;
    }

    /** Draw a title centred at y in the biggest font that fits (two lines if needed). Returns the height used. */
    static int title(Graphics gr, String s, int y, int col) {
        Font[] fs = {fBig, fMed, fSmall};
        int w = SW - 8;
        for (int k = SW >= 200 ? 0 : 1; k < 3; k++) {
            if (fs[k].stringWidth(s) <= w) {
                gr.setFont(fs[k]);
                outline(gr, s, SW / 2, y, col, Graphics.TOP | Graphics.HCENTER);
                return fs[k].getHeight();
            }
        }
        int best = -1;                                     // split at the space closest to the middle
        for (int i = 0; i < s.length(); i++)
            if (s.charAt(i) == ' ' && (best < 0 || Math.abs(i - s.length() / 2) < Math.abs(best - s.length() / 2))) best = i;
        String a = best < 0 ? s : s.substring(0, best), b = best < 0 ? "" : s.substring(best + 1);
        for (int k = SW >= 200 ? 0 : 1; k < 3; k++) {
            if (fs[k].stringWidth(a) <= w && fs[k].stringWidth(b) <= w || k == 2) {
                gr.setFont(fs[k]);
                outline(gr, a, SW / 2, y, col, Graphics.TOP | Graphics.HCENTER);
                outline(gr, b, SW / 2, y + fs[k].getHeight(), col, Graphics.TOP | Graphics.HCENTER);
                return fs[k].getHeight() * 2;
            }
        }
        return 0;
    }

    static void drawCard(Graphics gr) {
        gr.setColor(0x050205);
        gr.fillRect(0, 0, SW, SH);
        gr.setFont(fSmall);
        outline(gr, clip(W.lvSub, fSmall, SW - 6), SW / 2, SH / 2 - fBig.getHeight() - 10, 0xb08070, Graphics.TOP | Graphics.HCENTER);
        int th = title(gr, W.lvName, SH / 2 - 8, 0xff6a10);
        gr.setFont(fSmall);
        String sk = W.skill == 0 ? "Trick" : W.skill == 1 ? "Treat" : "Nightmare";
        outline(gr, "Difficulty: " + sk, SW / 2, SH / 2 - 8 + th + 6, 0x907060, Graphics.TOP | Graphics.HCENTER);
        if (stateTick > 6 && (tick & 8) != 0) outline(gr, "get ready...", SW / 2, SH - fSmall.getHeight() - 6, 0xffa040, Graphics.TOP | Graphics.HCENTER);
    }

    static void drawInter(Graphics gr) {
        drawBg(gr, true);
        int th = title(gr, W.lvName, SH / 6, 0xff6a10);
        gr.setFont(fMed);
        outline(gr, "CLEARED!", SW / 2, SH / 6 + th + 2, 0xffc040, Graphics.TOP | Graphics.HCENTER);
        Font sf = fit("SECRETS  100%", SW - 6, fMed);
        gr.setFont(sf);
        int lh = sf.getHeight() + 4, y = SH / 6 + th + 6 + fMed.getHeight();
        if (y < SH / 3 + fMed.getHeight() && SH / 3 + fMed.getHeight() + 3 * lh < SH - fSmall.getHeight() - 8) y = SH / 3 + fMed.getHeight();
        int k = interTotal > 0 ? interKills * 100 / interTotal : 100;
        int s = interTotalSec > 0 ? interSecrets * 100 / interTotalSec : 100;
        outline(gr, "KILLS  " + k + "%", SW / 2, y, 0xffe0c0, Graphics.TOP | Graphics.HCENTER);
        outline(gr, "SECRETS  " + s + "%", SW / 2, y + lh, 0xffe0c0, Graphics.TOP | Graphics.HCENTER);
        int m = interTime / 60, sec = interTime % 60;
        outline(gr, "TIME  " + m + ":" + (sec < 10 ? "0" : "") + sec, SW / 2, y + 2 * lh, 0xffe0c0, Graphics.TOP | Graphics.HCENTER);
        if (skipArmed && (tick & 8) != 0) {
            gr.setFont(fSmall);
            outline(gr, "press 5 to continue", SW / 2, SH - fSmall.getHeight() - 6, 0xff9030, Graphics.TOP | Graphics.HCENTER);
        }
    }

    static final int DEAD_WAIT = 50;          // ticks (20 per second)
    static boolean deadArmed;
    static int fireT;

    static void drawDead(Graphics gr) {
        int th = centerText(gr, "BUTCH GOT BURIED", SH / 3, 0xff2010, SW >= 200 ? fBig : fMed);
        if (deadArmed) {
            gr.setFont(fSmall);
            outline(gr, clip("5: dig yourself out", fSmall, SW - 6), SW / 2, SH / 3 + th + 6, 0xffc0a0, Graphics.TOP | Graphics.HCENTER);
            outline(gr, "menu: quit", SW / 2, SH / 3 + th + 8 + fSmall.getHeight(), 0xa08070, Graphics.TOP | Graphics.HCENTER);
        }
    }

    // ------------------------------------------------------------------ in-game view

    static void drawGame(Graphics gr) {
        // palette effects: damage (red), pickups (gold), lightning, and the death fade
        int tint = 0, amt = 0, bright = 0;
        if (W.flashDmg > 0) { tint = 0xff1000; amt = W.flashDmg * 2 / 5; }
        else if (W.flashPick > 0) { tint = 0xffd060; amt = W.flashPick / 4; }
        if (W.dead) { tint = 0x600000; amt = 90 + (W.deadTim > 40 ? 40 : W.deadTim); }
        else if (W.fallT > 0) { tint = 0; amt = W.fallT * 11 > 250 ? 250 : W.fallT * 11; }
        if (W.lightningBoost > 0) bright = W.lightningBoost * 8;
        boolean cut = state == S_CUT;
        if (cut && cutGlow > 0) { tint = 0x40ff70; amt = cutGlow / 2; bright = cutGlow / 3; }
        if (cut && cutFade > 0) { tint = 0; amt = cutFade; bright = 0; }
        E.buildCmap(tint, amt, bright);
        E.px = W.px;
        E.py = W.py;
        E.pang = (W.pa + (W.shake > 0 ? W.rnd(W.shake * 6 + 1) - W.shake * 3 : 0)) & 4095;
        int ez = 32768 + W.pz + W.bob - (W.kick > 0 ? W.kick * 40 : 0);
        E.eyeZ = ez < 4000 ? 4000 : ez > 60000 ? 60000 : ez;
        if (cut && cuA >= 0) {
            if (cuT < 2 && cutFade == 0) E.buildCmap(0xffffff, 150, 0);       // white pop on the cut
            drawCloseUp();
        } else {
            E.render();
            W.collectSprites();
            E.drawSprites();
            E.drawParticles();
        }
        if (!W.dead && !cut) drawWeapon();
        E.blit(gr);
        if (!cut && W.radioLvl > 0 && !W.dead && (W.lvFlags & W.LF_RADIO) != 0) drawStatic(gr);
        if (!cut) drawHud(gr);
        if (meltImg != null) drawMelt(gr);
    }

    static long meltStart;
    static int noiseSeed = 1;

    /** The radio's static bleeds into the picture: the closer the monster, the more snow. */
    static void drawStatic(Graphics gr) {
        int n = W.radioLvl * W.radioLvl * 3, vh = E.VH;
        for (int k = 0; k < n; k++) {
            noiseSeed = noiseSeed * 1103515245 + 12345;
            int r = (noiseSeed >>> 8) & 0xffffff;
            int y = r % vh, x = (r >> 9) % SW, w = 3 + (r >> 4) % (SW / 5 + 1);
            int g = 0x70 + (r & 0x7f);
            gr.setColor((g << 16) | (g << 8) | g);
            gr.drawLine(x, y, x + w, y);
        }
    }

    static void drawMelt(Graphics gr) {
        if (meltT == 0) meltStart = System.currentTimeMillis();
        meltT = (int) ((System.currentTimeMillis() - meltStart) / 40) + 1;
        boolean any = false;
        int sp = SH / 16 + 1;
        for (int i = 0; i < meltOff.length; i++) {
            int o = meltOff[i] + meltT;
            int dy = o <= 0 ? 0 : o * o * sp / 40;
            if (dy >= SH) continue;
            any = true;
            int x = i * 4, w = x + 4 > SW ? SW - x : 4;
            gr.drawRegion(meltImg, x, 0, w, SH - dy, Sprite.TRANS_NONE, x, dy, Graphics.TOP | Graphics.LEFT);
        }
        if (!any) { meltImg = null; meltOff = null; }
    }

    static void drawWeapon() {
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
        int bx = (int) ((long) E.cos(W.bobPhase) * W.bobAmp >> 16) * E.RW / (40 << 16);
        int bs = E.sin(W.bobPhase);
        int by = (int) ((long) (bs < 0 ? -bs : bs) * W.bobAmp >> 16) * E.RH / (70 << 16);
        int sw = W.wSwitch * E.RH / 50;
        int kk = W.kick > 0 ? W.kick * E.RH / 200 : 0;
        int pc = ((W.py >> 16) << 6) | (W.px >> 16);
        int sh = W.light[pc] - 3;
        if (sh > 10) sh = 10;          // the gun and Butch's hands never sink into the dark or the fog: always at least half lit
        if (f != 0 && w != 0) sh -= 6;
        E.drawScreen(s, E.RW / 2 + bx + (WTIP[w] * k >> 16), E.RH + by + sw + kk / 2, k, sh);
    }

    // the guns are held a little left of centre: slide each one so its muzzle sits right under the crosshair
    // (sprite pixels, measured on the idle frames; the shovel has no muzzle)
    static final int[] WTIP = {0, 10, 9, 7, -6};

    static void digits(Graphics gr, int v, int x, int y, Image img, int cw, int ch) {
        String s = String.valueOf(v);
        int adv = cw * 3 / 4;
        for (int i = 0; i < s.length(); i++) {
            int d = s.charAt(i) - '0';
            gr.drawRegion(img, d * cw, 0, cw, ch, Sprite.TRANS_NONE, x + i * adv, y, Graphics.TOP | Graphics.LEFT);
        }
    }

    static int digitsW(int v, int cw) {
        return String.valueOf(v).length() * (cw * 3 / 4) + cw / 4;
    }

    static void icon(Graphics gr, int i, int x, int y) {
        gr.drawRegion(imgIcons, i * 16, 0, 16, 16, Sprite.TRANS_NONE, x, y, Graphics.TOP | Graphics.LEFT);
    }

    // status bar layout, worked out per screen size: the biggest digits and icons whose health block and ammo block
    // both fit beside Butch's face (small phones get the hand-drawn 6x8 digits and 12 px icons)
    static Image hDig, sDig, imgDig8;
    static int hW, hH, sW, sH, icW, hudKey = -1;
    static boolean ammoIcon, keyPips;

    static void layoutHud(int fx) {
        hudKey = SW * 1000 + hudH;
        keyPips = hudH < 32;
        int keyW = keyPips ? 7 : 13;
        int leftB = fx - 4, rightB = SW - (fx + faceSz) - (keyPips ? 6 : 4);
        Image[] cand = digH > 16 ? new Image[]{imgDig, imgDigS, imgDig8} : new Image[]{imgDig, imgDig8};
        hDig = null;
        for (int c = 0; c < cand.length && hDig == null; c++) {
            int cw = cand[c].getWidth() / 12, w3 = digitsW(200, cw);
            for (int ic = 16; ic >= 12 && hDig == null; ic -= 4) {
                if (3 + ic + 2 + w3 <= leftB && ic + 2 + w3 + keyW <= rightB) {
                    hDig = cand[c]; icW = ic; ammoIcon = true;
                    sDig = c + 1 < cand.length ? cand[c + 1] : cand[c];
                }
            }
        }
        if (hDig == null) {                    // smallest phones: small digits, no ammo icon (the gun says it all)
            hDig = sDig = imgDig8; icW = 12;
            ammoIcon = 12 + 2 + digitsW(200, hDig.getWidth() / 12) + keyW <= rightB;
        }
        hW = hDig.getWidth() / 12; hH = hDig.getHeight();
        sW = sDig.getWidth() / 12; sH = sDig.getHeight();
    }

    static void hudIcon(Graphics gr, int i, int x, int y) {
        if (icW >= 16) icon(gr, i, x, y);
        else gr.drawRegion(imgIcons, i * 16 + 2, 2, 12, 12, Sprite.TRANS_NONE, x, y, Graphics.TOP | Graphics.LEFT);
    }

    static void drawHud(Graphics gr) {
        int y0 = SH - hudH;
        if (hudBg == null || hudBg.getWidth() != SW || hudBg.getHeight() != hudH) {
            hudBg = Image.createImage(SW, hudH);
            Graphics hg = hudBg.getGraphics();
            // bar background: dark iron with an orange rim and rivets
            for (int i = 0; i < hudH; i++) {
                int t = i * 255 / hudH;
                hg.setColor((40 - t * 28 / 255) << 16 | (28 - t * 20 / 255) << 8 | (24 - t * 18 / 255));
                hg.drawLine(0, i, SW, i);
            }
            hg.setColor(0xff7010);
            hg.drawLine(0, 0, SW, 0);
            hg.setColor(0x601c04);
            hg.drawLine(0, 1, SW, 1);
            hg.setColor(0x806050);
            for (int x = 6; x < SW; x += SW / 6) { hg.fillRect(x, hudH - 4, 2, 2); }
        }
        gr.drawImage(hudBg, 0, y0, Graphics.TOP | Graphics.LEFT);
        // face
        int fk;
        if (W.dead) fk = 4;
        else if (faceT > 0 && faceKind == 3) fk = 3;
        else if (faceT > 0 && faceKind == 1) fk = W.health > 50 ? 1 : 2;
        else fk = W.health > 60 ? 0 : W.health > 25 ? 1 : 2;
        int fy = y0 + (hudH - faceSz) / 2 + 1;
        int fx = SW / 2 - faceSz / 2;
        gr.setColor(0x140806);
        gr.fillRect(fx - 2, fy - 1, faceSz + 4, faceSz + 2);
        gr.setColor(0x804010);
        gr.drawRect(fx - 2, fy - 1, faceSz + 3, faceSz + 1);
        gr.drawImage(imgFace[fk], fx, fy, Graphics.TOP | Graphics.LEFT);
        if (hudKey != SW * 1000 + hudH) layoutHud(fx);
        int dy = y0 + (hudH - hH) / 2 + 1;
        int iy = y0 + (hudH - icW) / 2 + 1;
        int hx = 3 + icW + 2;
        // health (left) and armor: side by side if there is room, else armor in small digits under health,
        // else (tiny screens) armor as a bar along the bottom
        int ax = hx + digitsW(W.health, hW) + 4;
        boolean wide = ax + icW + 1 + digitsW(W.armor, sW) < fx - 3;
        if (wide || W.armor <= 0) {
            hudIcon(gr, 0, 3, iy);
            digits(gr, W.health, hx, dy, hDig, hW, hH);
            if (W.armor > 0) {
                hudIcon(gr, 1, ax, iy);
                digits(gr, W.armor, ax + icW + 1, y0 + (hudH - sH) / 2 + 1, sDig, sW, sH);
            }
        } else if (hudH >= hH + sH + 2) {
            int hy = y0 + (hudH - hH - sH - 1) / 2 + 1;
            hudIcon(gr, 0, 3, hy + (hH - icW) / 2);
            digits(gr, W.health, hx, hy, hDig, hW, hH);
            int ay = hy + hH + 1;
            gr.drawRegion(imgIcons, 16 + 3, 3, 10, 10, Sprite.TRANS_NONE, 3 + (icW - 10) / 2, ay + (sH - 10) / 2, Graphics.TOP | Graphics.LEFT);
            digits(gr, W.armor, hx, ay, sDig, sW, sH);
        } else {
            hudIcon(gr, 0, 3, iy);
            digits(gr, W.health, hx, dy, hDig, hW, hH);
            int bw = fx - 8, by = y0 + hudH - 4;
            gr.setColor(0x202830); gr.fillRect(3, by, bw, 3);
            gr.setColor(0x80c0ff); gr.fillRect(3, by, bw * (W.armor > 100 ? 100 : W.armor) / 100, 3);
        }
        // stamina (sprint) bar just above the status bar
        if (W.stamina < 1000 && !W.dead) {
            int sw = SW / 4, sx = (SW - sw) / 2, sy = y0 - 5;
            gr.setColor(0x000000); gr.fillRect(sx - 1, sy - 1, sw + 2, 4);
            gr.setColor(W.staminaRest > 0 ? 0xa02010 : W.sprint ? 0xffe040 : 0x60c0ff);
            gr.fillRect(sx, sy, sw * W.stamina / 1000, 2);
        }
        // ammo (right)
        int a = W.WAMMO[W.weapon];
        int rx = fx + faceSz + (keyPips ? 4 : 6);
        int keyW = keyPips ? 7 : 13;
        if (a >= 0) {
            if (ammoIcon) {
                hudIcon(gr, 2 + a, rx, iy);
                digits(gr, W.ammo[a], rx + icW + 2, dy, hDig, hW, hH);
            } else digits(gr, W.ammo[a], SW - keyW - digitsW(W.ammo[a], hW), dy, hDig, hW, hH);
        } else {
            gr.setFont(fSmall);
            outline(gr, "DIG", rx + 4, y0 + (hudH - fSmall.getHeight()) / 2, 0xffa040, Graphics.TOP | Graphics.LEFT);
        }
        // keys stacked at the far right (small coloured tags when the bar is too short for the skull keys)
        int ky = y0 + 3;
        for (int k = 0; k < 3; k++) {
            if ((W.keys & (1 << k)) == 0) continue;
            if (keyPips) {
                int kx = SW - 7;
                gr.setColor(0x180804); gr.fillRect(kx - 1, ky - 1, 7, 7);
                gr.setColor(k == 0 ? 0xff3020 : k == 1 ? 0x3090ff : 0xffc020); gr.fillRect(kx, ky, 5, 5);
                ky += (hudH - 6) / 3;
            } else {
                gr.drawRegion(imgIcons, (5 + k) * 16 + 3, 1, 10, 14, Sprite.TRANS_NONE, SW - 12, ky, Graphics.TOP | Graphics.LEFT);
                ky += (hudH - 6) / 3;
            }
        }
        // crosshair
        int vh = SH - hudH;
        if (crosshair && !W.dead) {
            int cx = SW / 2, cy = vh / 2;
            gr.setColor(0xffd040);
            gr.drawLine(cx - 4, cy, cx - 2, cy);
            gr.drawLine(cx + 2, cy, cx + 4, cy);
            gr.drawLine(cx, cy - 4, cx, cy - 2);
            gr.drawLine(cx, cy + 2, cx, cy + 4);
        }
        // boss health bar
        gr.setFont(fSmall);
        int my = 2;
        int bi = W.bossIdx;
        if (bi >= 0 && bi < W.nt && W.isBoss(W.tType[bi]) && W.tSt[bi] < W.ST_DIE && W.tSt[bi] != W.ST_IDLE) {
            int bw = SW - 16, bx = 8, by = 3, hp = W.tHp[bi] * (bw - 2) / (W.bossMax > 0 ? W.bossMax : 1);
            if (hp < 0) hp = 0;
            gr.setColor(0x000000); gr.fillRect(bx - 1, by - 1, bw + 2, 7);
            gr.setColor(0x401010); gr.fillRect(bx, by, bw, 5);
            gr.setColor(0xd02010); gr.fillRect(bx + 1, by + 1, hp, 3);
            gr.setColor(0xff8040); gr.drawRect(bx, by, bw - 1, 4);
            int t = W.tType[bi];
            outline(gr, clip(t == W.BOSS ? "THE PUMPKIN KING" : t == W.GIGGLES ? "MISTER GIGGLES" : t == W.PRIME ? "FRANKENSTEIN PRIME" : t == W.SEVEN ? "SEVEN DEATH" : "COUNT HOLLOWFANG", fSmall, SW - 6), SW / 2, by + 7, 0xffb080,
                    Graphics.TOP | Graphics.HCENTER);
            my = by + 8 + fSmall.getHeight();
        }
        // messages
        for (int i = 0; i < 3; i++) {
            if (msgT[i] <= 0 || msgs[i] == null) continue;
            String m = msgs[i];
            if (fSmall.stringWidth(m) > SW - 6) {               // too long for this screen: break it at a space
                int b = m.length() - 1;
                while (b > 0 && (m.charAt(b) != ' ' || fSmall.substringWidth(m, 0, b) > SW - 6)) b--;
                if (b > 0) { outline(gr, m.substring(0, b), 3, my, msgCol[i], Graphics.TOP | Graphics.LEFT); my += fSmall.getHeight(); m = m.substring(b + 1); }
                m = clip(m, fSmall, SW - 6);
            }
            outline(gr, m, 3, my, msgCol[i], Graphics.TOP | Graphics.LEFT);
            my += fSmall.getHeight();
        }
        if (subT > 0 && subtitle != null) {
            int lh = fSmall.getHeight();
            if (fSmall.stringWidth(subtitle) <= SW - 4) outline(gr, subtitle, SW / 2, vh - lh - 4, 0xfff0a0, Graphics.TOP | Graphics.HCENTER);
            else {                                       // narrow screen: two lines, split near the middle
                int best = -1, n = subtitle.length();
                for (int i = 0; i < n; i++)
                    if (subtitle.charAt(i) == ' ' && (best < 0 || Math.abs(i - n / 2) < Math.abs(best - n / 2))) best = i;
                if (best < 0) best = n / 2;
                outline(gr, subtitle.substring(0, best), SW / 2, vh - 2 * lh - 4, 0xfff0a0, Graphics.TOP | Graphics.HCENTER);
                outline(gr, subtitle.substring(best).trim(), SW / 2, vh - lh - 4, 0xfff0a0, Graphics.TOP | Graphics.HCENTER);
            }
        }
        // weapon name while switching
        if (W.pendingWeapon >= 0) outline(gr, W.WNAME[W.pendingWeapon], SW / 2, vh - 2 * fSmall.getHeight() - 6, 0xffa040, Graphics.TOP | Graphics.HCENTER);
    }

    // ------------------------------------------------------------------ automap

    static void drawMap(Graphics gr) {
        gr.setColor(0x080406);
        gr.fillRect(0, 0, SW, SH);
        int cs = SW >= 200 ? 5 : 3;
        int cx = W.px >> 16, cy = W.py >> 16;
        int ox = SW / 2 - ((W.px * cs) >> 16), oy = SH / 2 - ((W.py * cs) >> 16);
        for (int y = 0; y < 64; y++) {
            int sy = oy + y * cs;
            if (sy < -cs || sy > SH) continue;
            for (int x = 0; x < 64; x++) {
                int c = (y << 6) | x;
                if (W.seen[c] == 0) continue;
                int sx = ox + x * cs;
                if (sx < -cs || sx > SW) continue;
                int w = W.wall[c], f = W.flag[c];
                int col;
                if (w == 0 || ((f & W.F_SECRET) != 0 && W.door[c] >= 65536)) col = (f & W.F_HURT) != 0 ? 0x305010 : (f & W.F_OUT) != 0 ? 0x1c2414 : 0x241c18;
                else if ((f & W.F_EXIT) != 0) col = 0x30ff40;
                else if ((f & W.F_KRED) != 0) col = 0xff3020;
                else if ((f & W.F_KBLUE) != 0) col = 0x4080ff;
                else if ((f & W.F_KGOLD) != 0) col = 0xffd020;
                else if ((f & W.F_DOOR) != 0 && (f & W.F_SECRET) == 0) col = 0xc08030;
                else col = 0x908070;
                gr.setColor(col);
                gr.fillRect(sx, sy, cs, cs);
            }
        }
        // keys in the world
        for (int i = 0; i < W.nt; i++) {
            int t = W.tType[i];
            if ((t < W.KEYR || t > W.KEYG) && t != W.TPAD) continue;
            int x = W.tX[i] >> 16, y = W.tY[i] >> 16;
            if (W.seen[(y << 6) | x] == 0) continue;
            gr.setColor(t == W.KEYR ? 0xff3020 : t == W.KEYB ? 0x4080ff : t == W.TPAD ? 0xc060ff : 0xffd020);
            gr.fillRect(ox + ((W.tX[i] * cs) >> 16) - 1, oy + ((W.tY[i] * cs) >> 16) - 1, 3, 3);
        }
        // player arrow
        int px = SW / 2, py = SH / 2;
        int a = W.pa;
        int l = cs * 2;
        int x1 = px + (E.cos(a) * l >> 16), y1 = py + (E.sin(a) * l >> 16);
        int x2 = px + (E.cos(a + 1450) * l >> 17), y2 = py + (E.sin(a + 1450) * l >> 17);
        int x3 = px + (E.cos(a - 1450) * l >> 17), y3 = py + (E.sin(a - 1450) * l >> 17);
        gr.setColor(0xffffff);
        gr.fillTriangle(x1, y1, x2, y2, x3, y3);
        gr.setFont(fSmall);
        outline(gr, clip(W.lvName, fSmall, SW - 6), SW / 2, 2, 0xff8030, Graphics.TOP | Graphics.HCENTER);
        outline(gr, clip("kills " + W.kills + "/" + W.totalKills + "  secrets " + W.secrets + "/" + W.totalSecrets, fSmall, SW - 4), SW / 2,
                SH - fSmall.getHeight() - 2, 0xc0b0a0, Graphics.TOP | Graphics.HCENTER);
    }

    // ================================================================== persistence

    static void loadOptions() {
        Snd.musicMode = Snd.MUS_ON;      // first run: music on everywhere (the engine itself backs off if it must)
        try {
            RecordStore rs = RecordStore.openRecordStore("bg3d", true);
            if (rs.getNumRecords() >= 1) {
                byte[] b = rs.getRecord(1);
                if (b != null && b.length >= 7) {
                    detail = b[0] % 3; Snd.sfxOn = b[2] != 0; Snd.voiceOn = b[3] != 0;
                    vibe = b[4] != 0; crosshair = b[5] != 0; showFps = b[6] != 0;
                    if (b.length >= 8) gore = b[7] != 0;
                    // byte 1: music mode; byte 8: record version; byte 9: music flags (1 = switched to "menus only"
                    // by the engine of versions 2.0-2.2, which no longer does that: such music comes back on).
                    // Versions before 2 guessed "menus only" from the phone's own mixing flag: their music comes back on.
                    if (b.length >= 10 && b[8] >= 2) {
                        Snd.musicMode = b[1] % 3;
                        if ((b[9] & 1) != 0 && Snd.musicMode == Snd.MUS_MENUS) Snd.musicMode = Snd.MUS_ON;
                    } else Snd.musicMode = b[1] == 0 ? Snd.MUS_OFF : Snd.MUS_ON;
                }
            }
            if (rs.getNumRecords() >= 2) {
                byte[] b = rs.getRecord(2);
                if (b != null && b.length >= 12 && b[0] == 1) {
                    hasSave = true;
                    saveLevel = b[1]; saveSkill = b[2];
                    lvStart[0] = (b[3] & 255) | ((b[4] & 255) << 8); lvStart[1] = b[5] & 255; lvStart[2] = b[6] & 255; lvStart[3] = b[7];
                    lvStart[4] = b[8] & 255; lvStart[5] = b[9] & 255; lvStart[6] = b[10] & 255; lvStart[7] = saveSkill; lvStart[8] = saveLevel;
                }
            }
            rs.closeRecordStore();
        } catch (Throwable t) { }
    }

    static void saveOptions() {
        byte[] b = {(byte) detail, (byte) Snd.musicMode, (byte) (Snd.sfxOn ? 1 : 0), (byte) (Snd.voiceOn ? 1 : 0),
                (byte) (vibe ? 1 : 0), (byte) (crosshair ? 1 : 0), (byte) (showFps ? 1 : 0), (byte) (gore ? 1 : 0), 2,
                0};
        write(1, b);
    }

    static void saveProgress() {
        byte[] b = {(byte) (hasSave ? 1 : 0), (byte) saveLevel, (byte) saveSkill, (byte) lvStart[0], (byte) (lvStart[0] >> 8),
                (byte) lvStart[1], (byte) lvStart[2], (byte) lvStart[3], (byte) lvStart[4], (byte) lvStart[5], (byte) lvStart[6], 0};
        write(2, b);
    }

    static void write(int id, byte[] b) {
        try {
            RecordStore rs = RecordStore.openRecordStore("bg3d", true);
            while (rs.getNumRecords() < 2) rs.addRecord(new byte[1], 0, 1);
            rs.setRecord(id, b, 0, b.length);
            rs.closeRecordStore();
        } catch (Throwable t) { }
    }
}
