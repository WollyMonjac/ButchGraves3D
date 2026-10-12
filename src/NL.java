/** Nokia backlight control, in its own class so phones without the Nokia UI API never load it. */
final class NL {
    static void lights() {
        com.nokia.mid.ui.DeviceControl.setLights(0, 100);
    }
}
