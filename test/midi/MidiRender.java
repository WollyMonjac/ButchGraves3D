import javax.sound.midi.*;
import javax.sound.sampled.*;
import java.io.*;

/** Render a MIDI file to WAV with Java's software synth (Gervill) and a GM soundfont: MidiRender font.sf2 in.mid out.wav */
public class MidiRender {
    public static void main(String[] a) throws Exception {
        Soundbank sb = MidiSystem.getSoundbank(new File(a[0]));
        Sequence seq = MidiSystem.getSequence(new File(a[1]));
        com.sun.media.sound.AudioSynthesizer syn = (com.sun.media.sound.AudioSynthesizer) MidiSystem.getSynthesizer();
        AudioFormat fmt = new AudioFormat(22050, 16, 2, true, false);
        AudioInputStream ais = syn.openStream(fmt, null);
        syn.unloadAllInstruments(syn.getDefaultSoundbank());
        syn.loadAllInstruments(sb);
        Receiver rc = syn.getReceiver();
        // flatten all tracks to timestamped events (tempo map aware)
        Track[] tr = seq.getTracks();
        java.util.List<MidiEvent> ev = new java.util.ArrayList<MidiEvent>();
        for (Track t : tr) for (int i = 0; i < t.size(); i++) ev.add(t.get(i));
        java.util.Collections.sort(ev, new java.util.Comparator<MidiEvent>() {
            public int compare(MidiEvent x, MidiEvent y) { return Long.compare(x.getTick(), y.getTick()); } });
        double usPerQ = 500000, res = seq.getResolution(), us = 0;
        long lastTick = 0;
        for (MidiEvent e : ev) {
            us += (e.getTick() - lastTick) * usPerQ / res;
            lastTick = e.getTick();
            MidiMessage m = e.getMessage();
            if (m instanceof MetaMessage) {
                MetaMessage mm = (MetaMessage) m;
                if (mm.getType() == 0x51) { byte[] d = mm.getData(); usPerQ = ((d[0] & 255) << 16) | ((d[1] & 255) << 8) | (d[2] & 255); }
                continue;
            }
            rc.send(m, (long) us);
        }
        long total = (long) ((us / 1e6 + 2.5) * fmt.getSampleRate());
        AudioInputStream out = new AudioInputStream(ais, fmt, total);
        AudioSystem.write(out, AudioFileFormat.Type.WAVE, new File(a[2]));
        syn.close();
    }
}
