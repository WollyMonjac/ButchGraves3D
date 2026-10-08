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
            S_OPT = 8, S_HELP = 9, S_INTER = 10, S_DEAD = 11, S_END = 12;
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

    protected void keyPressed(int code) {
        int k = mapKey(code);
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
    }

    static void tickAll() {
        tick++;
        stateTick++;
        for (int i = 0; i < 3; i++) if (msgT[i] > 0) msgT[i]--;
        if (subT > 0) subT--;
        if (faceT > 0) faceT--;
        switch (state) {
            case S_TITLE: menuTitle(); break;
            case S_SKILL: menuSkill(); break;
            case S_STORY: tickStory(); break;
            case S_CARD:
                if (stateTick > 40 || (stateTick > 6 && hit(K_FIRE | K_USE))) startPlay();
                break;
            case S_PLAY: tickPlay(); break;
            case S_PAUSE: menuPause(); break;
            case S_MAP:
                if (hit(K_USE)) {
                    if (++mapCheat >= 3) { mapCheat = 0; setState(S_PLAY); if (W.level == 4) victory(); else levelDone(); break; }
                }
                if (hit(K_MAP | K_FIRE | K_BACK | K_MENU)) { mapCheat = 0; setState(S_PLAY); }
                break;
            case S_OPT: menuOpt(); break;
            case S_HELP:
                if (hit(K_UP) && helpTop > 0) helpTop--;
                if (hit(K_DOWN) && helpTop < helpMax) helpTop++;
                if (hit(K_FIRE | K_BACK | K_MENU | K_USE)) { helpTop = 0; setState(optReturn); }
                break;
            case S_INTER:
                if (stateTick > 10 && hit(K_FIRE | K_USE)) nextLevel();
                break;
            case S_DEAD:
                W.tick();
                if (stateTick > 20 && hit(K_FIRE | K_USE)) restartLevel();
                if (hit(K_MENU | K_BACK)) toTitle();
                break;
            case S_END: tickStory(); break;
        }
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
        nav(TITLE_ITEMS.length);
        if (sel == 1 && !hasSave && (pressed & (K_UP | K_DOWN)) == 0) { }
        if (hit(K_FIRE | K_USE)) {
            switch (sel) {
                case 0: setState(S_SKILL); sel = 1; break;
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
            newGame();
        }
        if (hit(K_BACK | K_MENU)) setState(S_TITLE);
    }

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

    static String[] optItems() {
        return new String[]{"DETAIL: " + DETAIL[detail], "MUSIC: " + (Snd.musicOn ? "ON" : "OFF"), "SOUND FX: " + (Snd.sfxOn ? "ON" : "OFF"),
                "VOICE: " + (Snd.voiceOn ? "ON" : "OFF"), "VIBRATION: " + (vibe ? "ON" : "OFF"), "CROSSHAIR: " + (crosshair ? "ON" : "OFF"),
                "FPS COUNTER: " + (showFps ? "ON" : "OFF"), "BACK"};
    }

    static void menuOpt() {
        nav(8);
        boolean act = hit(K_FIRE | K_USE | K_LEFT | K_RIGHT);
        if (hit(K_BACK | K_MENU) || (act && sel == 7)) {
            saveOptions();
            setState(optReturn);
            if (optReturn == S_PAUSE) sel = 2;
            return;
        }
        if (!act) return;
        Snd.sfx(Snd.CLICK);
        switch (sel) {
            case 0: detail = (detail + 1) % 3; setupView(); break;
            case 1:
                Snd.musicOn = !Snd.musicOn;
                if (Snd.musicOn) Snd.resume(); else Snd.music(-1);
                if (!Snd.musicOn) Snd.wantMusic = optReturn == S_TITLE ? Snd.M_TITLE : Snd.M_L1 + W.level - 1;
                break;
            case 2: Snd.sfxOn = !Snd.sfxOn; break;
            case 3: Snd.voiceOn = !Snd.voiceOn; break;
            case 4: vibe = !vibe; break;
            case 5: crosshair = !crosshair; break;
            case 6: showFps = !showFps; break;
        }
    }

    // ------------------------------------------------------------------ story

    static final String[] STORY = {
            "HOLLOW CREEK.  OCTOBER 31ST.\n\nFor twenty years BUTCH GRAVES has dug the graves of this sleepy town. Quiet work. Quiet neighbours.\n\n"
                    + "Tonight the Harvest Cult lit the Great Jack-o'-Lantern on Blackwood Hill and woke the PUMPKIN KING.\n\n"
                    + "Now the dead are clawing out of Butch's cemetery... and they're ruining his lawn.\n\nGrab the shovel. Time to put them back.",
            "The mausoleum stairs lead past the old iron gate, straight up the hill to BLACKWOOD MANOR - home of the Harvest Cult.\n\n"
                    + "Witches cackle in the windows. Ghosts drift through the halls.\n\nSomewhere inside is the way down to their unholy altar.",
            "Beneath the manor lie the BONE CATACOMBS, dug by the cult over a hundred Halloweens.\n\n"
                    + "The air reeks of slime and old candy wrappers.\n\nThe Pumpkin King's altar is close. Butch can hear it... laughing.",
            "The altar spits Butch out under a BLOOD MOON, right into the Pumpkin King's own patch.\n\n"
                    + "Lava bubbles between the vines. The King is waiting, crowned in fire.\n\nOne more grave to dig. A big one.",
            "The Pumpkin King collapses into a heap of smoking pie filling.\n\nThe Great Jack-o'-Lantern on Blackwood Hill gutters out, and the dead fall silent.\n\n"
                    + "At sunrise Butch walks home through the cemetery, shovel on his shoulder, and fills in one last hole.\n\nHAPPY HALLOWEEN.\n\n...see you next October."};
    static int storyIdx, storyNext;

    static void showStory(int idx, int next) {
        storyIdx = idx;
        storyNext = next;
        layIdx = -1;
        setState(idx == 4 ? S_END : S_STORY);
        Snd.music(idx == 4 ? Snd.M_WIN : Snd.M_STORY);
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
        if (state == S_END) { hasSave = false; saveProgress(); toTitle(); return; }
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

    static void newGame() {
        W.health = 100;
        W.armor = 0;
        W.weapons = 3;           // shovel + revolver
        W.weapon = 1;
        W.ammo[0] = 40; W.ammo[1] = 0; W.ammo[2] = 0;
        if (warp > 1) {
            W.weapons = 31; W.ammo[0] = 150; W.ammo[1] = 30; W.ammo[2] = 12; W.armor = 100;
            showStory(warp - 1, warp);
            return;
        }
        showStory(0, 1);
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
        Snd.music(Snd.M_L1 + lv - 1);
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
        int lv = W.level + 1;
        if (lv > 4) { showStory(4, 0); return; }
        showStory(lv - 1, lv);
    }

    static void victory() {
        interKills = W.kills; interTotal = W.totalKills; interSecrets = W.secrets; interTotalSec = W.totalSecrets; interTime = W.ticks / 20;
        showStory(4, 0);
    }

    static void died() {
        setState(S_DEAD);
        faceKind = 4;
        Snd.music(Snd.M_DEAD);
        vibrate(400);
    }

    static void tickPlay() {
        if (hit(K_MENU | K_BACK)) { setState(S_PAUSE); return; }
        if (hit(K_MAP)) { setState(S_MAP); return; }
        int k = keys;
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

    static void vibrate(int ms) {
        if (!vibe) return;
        try { Display.getDisplay(midlet).vibrate(ms); } catch (Throwable t) { }
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
                    outline(gr, (warp > 1 ? "WARP TO NIGHT " + warp + "  " : "") + (W.god ? "GOD MODE" : ""), SW / 2, SH - fSmall.getHeight() - 4, 0xc080ff, Graphics.TOP | Graphics.HCENTER);
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
            case S_INTER: drawInter(gr); break;
            case S_DEAD: drawGame(gr); drawDead(gr); break;
        }
        if (showFps && state == S_PLAY) {
            gr.setFont(fSmall);
            outline(gr, fps + " fps", SW - 2, 2, 0x80ff80, Graphics.TOP | Graphics.RIGHT);
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
        int lh = f.getHeight() + 2;
        int my = SH - lh * TITLE_ITEMS.length - 8;
        String tag = fSmall.stringWidth("NIGHT OF THE PUMPKIN KING") < SW - 4 ? "NIGHT OF THE PUMPKIN KING" : "PUMPKIN KING";
        if (y0 + fSmall.getHeight() < my - 4) outline(gr, tag, SW / 2, y0, 0xffb040, Graphics.TOP | Graphics.HCENTER);
        for (int y = my - 4; y < SH; y += 4) gr.drawRGB(shade, 0, SW, 0, y, SW, SH - y < 4 ? SH - y : 4, true);
        gr.setFont(f);
        for (int i = 0; i < TITLE_ITEMS.length; i++) {
            boolean s = i == sel;
            int col = s ? ((tick & 4) != 0 ? 0xffe060 : 0xffa020) : (i == 1 && !hasSave ? 0x705850 : 0xd8c8b0);
            String t = TITLE_ITEMS[i];
            if (s) t = "> " + t + " <";
            outline(gr, t, SW / 2, my + i * lh, col, Graphics.TOP | Graphics.HCENTER);
        }
    }

    static void drawMenuScreen(Graphics gr, String title, String[] items) {
        drawBg(gr, true);
        drawMenuItems(gr, title, items, SH / 3);
    }

    static void drawMenuItems(Graphics gr, String title, String[] items, int y) {
        Font tf = SH >= 200 ? fBig : fMed;
        Font f = SH >= 240 ? fMed : fSmall;
        int lh = f.getHeight() + 3;
        // shrink to fit: smaller font first, then move the block up
        if (y + items.length * lh > SH - 4) { f = fSmall; lh = f.getHeight() + 2; tf = fMed; }
        if (y + items.length * lh > SH - 4) y = SH - 4 - items.length * lh;
        if (y < tf.getHeight() + 6) { y = tf.getHeight() + 6; lh = (SH - 4 - y) / items.length; if (lh < f.getHeight()) lh = f.getHeight(); }
        gr.setFont(tf);
        outline(gr, title, SW / 2, y - tf.getHeight() - (y > tf.getHeight() + 8 ? 8 : 3), 0xff6a10, Graphics.TOP | Graphics.HCENTER);
        gr.setFont(f);
        for (int i = 0; i < items.length; i++) {
            boolean s = i == sel;
            int col = s ? ((tick & 4) != 0 ? 0xffe060 : 0xffa020) : 0xd8c8b0;
            outline(gr, s ? "> " + items[i] + " <" : items[i], SW / 2, y + i * lh, col, Graphics.TOP | Graphics.HCENTER);
        }
    }

    static int helpTop, helpMax;

    static void drawHelp(Graphics gr) {
        drawBg(gr, true);
        String[] L = {"2 / UP: walk forward", "8 / DOWN: walk back", "4 6 / LEFT RIGHT: turn", "1 3: strafe", "5 / FIRE: shoot",
                "0: use / open", "7 9: change weapon", "#: jump", "*: automap", "Soft key: menu", "", "Doors open when you walk", "into them. Find the skull keys!"};
        Font tf = SH >= 200 ? fMed : fSmall;
        gr.setFont(tf);
        outline(gr, "CONTROLS", SW / 2, 4, 0xff6a10, Graphics.TOP | Graphics.HCENTER);
        Font f = fSmall;
        gr.setFont(f);
        int lh = f.getHeight();
        int top = 8 + tf.getHeight(), bottom = SH - lh - 6;
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
        if (typed && (tick & 8) != 0) {
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
            outline(gr, s.substring(i, e), x, y, col, Graphics.TOP | Graphics.LEFT);
            y += lh;
            i = e;
            if (i < n && (s.charAt(i) == ' ' || s.charAt(i) == '\n')) {
                if (s.charAt(i) == '\n' && i + 1 < n && s.charAt(i + 1) == '\n') { y += lh / 2; i++; }
                i++;
            }
        }
        return y;
    }

    static void drawCard(Graphics gr) {
        gr.setColor(0x050205);
        gr.fillRect(0, 0, SW, SH);
        gr.setFont(fSmall);
        outline(gr, W.lvSub, SW / 2, SH / 2 - fBig.getHeight() - 10, 0xb08070, Graphics.TOP | Graphics.HCENTER);
        gr.setFont(SW >= 200 ? fBig : fMed);
        outline(gr, W.lvName, SW / 2, SH / 2 - 8, 0xff6a10, Graphics.TOP | Graphics.HCENTER);
        gr.setFont(fSmall);
        String sk = W.skill == 0 ? "Trick" : W.skill == 1 ? "Treat" : "Nightmare";
        outline(gr, "Difficulty: " + sk, SW / 2, SH / 2 + fBig.getHeight(), 0x907060, Graphics.TOP | Graphics.HCENTER);
        if (stateTick > 6 && (tick & 8) != 0) outline(gr, "get ready...", SW / 2, SH - fSmall.getHeight() - 6, 0xffa040, Graphics.TOP | Graphics.HCENTER);
    }

    static void drawInter(Graphics gr) {
        drawBg(gr, true);
        gr.setFont(SW >= 200 ? fBig : fMed);
        outline(gr, "NIGHT " + W.level + " SURVIVED", SW / 2, SH / 6, 0xff6a10, Graphics.TOP | Graphics.HCENTER);
        gr.setFont(fMed);
        int lh = fMed.getHeight() + 4, y = SH / 3 + 4;
        int k = interTotal > 0 ? interKills * 100 / interTotal : 100;
        int s = interTotalSec > 0 ? interSecrets * 100 / interTotalSec : 100;
        outline(gr, "KILLS  " + k + "%", SW / 2, y, 0xffe0c0, Graphics.TOP | Graphics.HCENTER);
        outline(gr, "SECRETS  " + s + "%", SW / 2, y + lh, 0xffe0c0, Graphics.TOP | Graphics.HCENTER);
        int m = interTime / 60, sec = interTime % 60;
        outline(gr, "TIME  " + m + ":" + (sec < 10 ? "0" : "") + sec, SW / 2, y + 2 * lh, 0xffe0c0, Graphics.TOP | Graphics.HCENTER);
        if (stateTick > 10 && (tick & 8) != 0) {
            gr.setFont(fSmall);
            outline(gr, "press 5 to continue", SW / 2, SH - fSmall.getHeight() - 6, 0xff9030, Graphics.TOP | Graphics.HCENTER);
        }
    }

    static void drawDead(Graphics gr) {
        gr.setFont(SW >= 200 ? fBig : fMed);
        outline(gr, "BUTCH GOT BURIED", SW / 2, SH / 3, 0xff2010, Graphics.TOP | Graphics.HCENTER);
        if (stateTick > 20) {
            gr.setFont(fSmall);
            outline(gr, "5: dig yourself out", SW / 2, SH / 3 + fBig.getHeight() + 6, 0xffc0a0, Graphics.TOP | Graphics.HCENTER);
            outline(gr, "menu: quit", SW / 2, SH / 3 + fBig.getHeight() + 8 + fSmall.getHeight(), 0xa08070, Graphics.TOP | Graphics.HCENTER);
        }
    }

    // ------------------------------------------------------------------ in-game view

    static void drawGame(Graphics gr) {
        // palette effects: damage (red), pickups (gold), lightning, and the death fade
        int tint = 0, amt = 0, bright = 0;
        if (W.flashDmg > 0) { tint = 0xff1000; amt = W.flashDmg * 2 / 5; }
        else if (W.flashPick > 0) { tint = 0xffd060; amt = W.flashPick / 4; }
        if (W.dead) { tint = 0x600000; amt = 90 + (W.deadTim > 40 ? 40 : W.deadTim); }
        if (W.lightningBoost > 0) bright = W.lightningBoost * 8;
        E.buildCmap(tint, amt, bright);
        E.px = W.px;
        E.py = W.py;
        E.pang = (W.pa + (W.shake > 0 ? W.rnd(W.shake * 6 + 1) - W.shake * 3 : 0)) & 4095;
        int ez = 32768 + W.pz + W.bob - (W.kick > 0 ? W.kick * 40 : 0);
        E.eyeZ = ez < 4000 ? 4000 : ez > 60000 ? 60000 : ez;
        E.render();
        W.collectSprites();
        E.drawSprites();
        E.drawParticles();
        if (!W.dead) drawWeapon();
        E.blit(gr);
        drawHud(gr);
        if (meltImg != null) drawMelt(gr);
    }

    static long meltStart;

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
        if (f != 0 && w != 0) sh -= 6;
        E.drawScreen(s, E.RW / 2 + bx, E.RH + by + sw + kk / 2, k, sh);
    }

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
        int dy = y0 + (hudH - digH) / 2 + 1;
        int iy = y0 + (hudH - 16) / 2 + 1;
        // health (left)
        icon(gr, 0, 3, iy);
        digits(gr, W.health, 21, dy, imgDig, digW, digH);
        // armor (left, after health) if room
        int ax = 21 + digitsW(W.health, digW) + 4;
        if (W.armor > 0 && ax + 16 + digitsW(W.armor, digSW) < fx - 2) {
            icon(gr, 1, ax, iy);
            digits(gr, W.armor, ax + 17, y0 + (hudH - digSH) / 2 + 1, imgDigS, digSW, digSH);
        }
        // ammo (right)
        int a = W.WAMMO[W.weapon];
        int rx = fx + faceSz + 6;
        if (a >= 0) {
            icon(gr, 2 + a, rx, iy);
            digits(gr, W.ammo[a], rx + 18, dy, imgDig, digW, digH);
        } else {
            gr.setFont(fSmall);
            outline(gr, "DIG", rx + 4, y0 + (hudH - fSmall.getHeight()) / 2, 0xffa040, Graphics.TOP | Graphics.LEFT);
        }
        // keys stacked at the far right
        int kx = SW - 12, ky = y0 + 3;
        for (int k = 0; k < 3; k++) {
            if ((W.keys & (1 << k)) != 0) {
                gr.drawRegion(imgIcons, (5 + k) * 16 + 3, 1, 10, 14, Sprite.TRANS_NONE, kx, ky, Graphics.TOP | Graphics.LEFT);
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
        // messages
        gr.setFont(fSmall);
        int my = 2;
        for (int i = 0; i < 3; i++) {
            if (msgT[i] <= 0 || msgs[i] == null) continue;
            outline(gr, msgs[i], 3, my, msgCol[i], Graphics.TOP | Graphics.LEFT);
            my += fSmall.getHeight();
        }
        if (subT > 0 && subtitle != null) {
            outline(gr, subtitle, SW / 2, vh - fSmall.getHeight() - 4, 0xfff0a0, Graphics.TOP | Graphics.HCENTER);
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
                if (w == 0) col = (f & W.F_HURT) != 0 ? 0x305010 : (f & W.F_OUT) != 0 ? 0x1c2414 : 0x241c18;
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
            if (t < W.KEYR || t > W.KEYG) continue;
            int x = W.tX[i] >> 16, y = W.tY[i] >> 16;
            if (W.seen[(y << 6) | x] == 0) continue;
            gr.setColor(t == W.KEYR ? 0xff3020 : t == W.KEYB ? 0x4080ff : 0xffd020);
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
        outline(gr, W.lvName, SW / 2, 2, 0xff8030, Graphics.TOP | Graphics.HCENTER);
        outline(gr, "kills " + W.kills + "/" + W.totalKills + "  secrets " + W.secrets + "/" + W.totalSecrets, SW / 2,
                SH - fSmall.getHeight() - 2, 0xc0b0a0, Graphics.TOP | Graphics.HCENTER);
    }

    // ================================================================== persistence

    static void loadOptions() {
        try {
            RecordStore rs = RecordStore.openRecordStore("bg3d", true);
            if (rs.getNumRecords() >= 1) {
                byte[] b = rs.getRecord(1);
                if (b != null && b.length >= 7) {
                    detail = b[0] % 3; Snd.musicOn = b[1] != 0; Snd.sfxOn = b[2] != 0; Snd.voiceOn = b[3] != 0;
                    vibe = b[4] != 0; crosshair = b[5] != 0; showFps = b[6] != 0;
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
        byte[] b = {(byte) detail, (byte) (Snd.musicOn ? 1 : 0), (byte) (Snd.sfxOn ? 1 : 0), (byte) (Snd.voiceOn ? 1 : 0),
                (byte) (vibe ? 1 : 0), (byte) (crosshair ? 1 : 0), (byte) (showFps ? 1 : 0)};
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
