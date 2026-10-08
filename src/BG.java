import javax.microedition.lcdui.Display;
import javax.microedition.midlet.MIDlet;

/** BUTCH GRAVES 3D - Night of the Pumpkin King. MIDP 2.0 / CLDC 1.0 */
public class BG extends MIDlet {
    G canvas;

    protected void startApp() {
        if (canvas == null) {
            G.midlet = this;
            canvas = new G();
            Display.getDisplay(this).setCurrent(canvas);
            canvas.start();
        } else {
            Display.getDisplay(this).setCurrent(canvas);
        }
    }

    protected void pauseApp() {
        G.paused = true;
        Snd.stopAll();
    }

    protected void destroyApp(boolean unconditional) {
        G.running = false;
        Snd.shutdown();
    }

    void quit() {
        G.running = false;
        try { G.saveOptions(); } catch (Throwable t) { }
        Snd.shutdown();
        notifyDestroyed();
    }
}
