#!/usr/bin/env python3
"""Episode 2/3 audio: Butch's new one-liners, cutscene voices, new monster SFX and new General-MIDI tracks.
All original. Run after gen_audio.py (it rewrites res/snd/sounds.txt with every key)."""
import os, sys, wave, subprocess, tempfile
import numpy as np
import gen_audio as A
from gen_audio import (SR, save_wav, secs, env, noise, lowpass, highpass, tone, reverb, pad, dist, voice, monster_voice,
                       Track, write_midi, seq, power, drums_rock, n2m, PPQ)

rng = np.random.RandomState(7)

# ================================================================== voices

BUTCH = [
    ('v_start3', "Great. Clowns. I hate clowns.", 'mb-us2', 140, 28, 0.9),
    ('v_start4', "Bite me.", 'mb-us2', 125, 26, 0.88),
    ('v_kclown', "Joke's over.", 'mb-us2', 135, 26, 0.9),
    ('v_kskel', "Back to the boneyard.", 'mb-us2', 140, 26, 0.9),
    ('v_kwolf', "Bad dog.", 'mb-us2', 125, 26, 0.9),
    ('v_kbat', "Pest control.", 'mb-us2', 135, 28, 0.9),
    ('v_kvamp', "Suck on that.", 'mb-us2', 135, 26, 0.9),
    ('v_boss2', "Time to pop your balloon, Giggles.", 'mb-us2', 145, 26, 0.88),
    ('v_boss3', "Rise and shine, bloodsucker.", 'mb-us2', 140, 26, 0.88),
    ('v_win2', "Show's over.", 'mb-us2', 125, 26, 0.88),
    ('v_win3', "Dawn's coming, pal.", 'mb-us2', 130, 26, 0.88),
    ('v_kill4', "Who's next?", 'mb-us2', 135, 28, 0.9),
    ('v_kill5', "I'm just getting warmed up.", 'mb-us2', 150, 28, 0.9),
    ('v_c1a', "Best jack-o-lantern on the block.", 'mb-us2', 140, 30, 0.9),
    ('v_c1e', "Kids these days.", 'mb-us2', 125, 26, 0.9),
    ('v_c2a', "Any last words, Giggles?", 'mb-us2', 140, 28, 0.9),
    ('v_c2c', "Worst. Circus. Ever.", 'mb-us2', 115, 26, 0.9),
    ('v_c3b', "Batter up.", 'mb-us2', 125, 28, 0.9),
    ('v_c3d', "Home run.", 'mb-us2', 120, 28, 0.9),
]


def char_line(vid, text, v, speed, pitch, pf, fx, drive=1.6, gain=0.95):
    d = monster_voice(vid, text, v, speed, pitch, pf, fx)
    return save_wav(vid + '.wav', pad(dist(d * 1.3, drive), 0.05), gain)


CHARS = [
    # the Pumpkin King's head: deep, crackling
    ('v_c1b', "You will pay for this, gravedigger!", 'k:am_onyx', 190, 20, 0.76,
     'highpass=f=90,lowpass=f=2600,acompressor=threshold=-22dB:ratio=5:makeup=8,aecho=0.8:0.5:50:0.25', 2.4),
    ('v_c1d', "BOO!", 'k:am_onyx', 110, 18, 0.66,
     'highpass=f=80,lowpass=f=2400,acompressor=threshold=-22dB:ratio=5:makeup=10,aecho=0.8:0.6:70|140:0.35|0.2', 2.8),
    # the little trick-or-treater
    ('v_c1c', "Trick or treat!", 'k:af_sky', 175, 99, 1.2, 'highpass=f=200,lowpass=f=3800', 1.3),
    # Mister Giggles, wheezing
    ('v_c2b', "Honk... honk...", 'k:am_puck', 95, 85, 1.02, 'vibrato=f=7:d=0.4,highpass=f=150,lowpass=f=3200,aecho=0.8:0.4:40:0.2', 1.5),
    # the Count, shrunk into a squeaky little bat
    ('v_c3a', "You have not seen the last of me, gravedigger!", 'k:bm_lewis', 150, 60, 1.42,
     'vibrato=f=9:d=0.25,highpass=f=250,lowpass=f=3800,aecho=0.8:0.4:30:0.2', 1.4),
    ('v_c3c', "Curses!", 'k:bm_lewis', 100, 70, 1.5, 'vibrato=f=12:d=0.5,highpass=f=250,lowpass=f=3800,aecho=0.8:0.6:80|160:0.4|0.25', 1.4),
]

# ================================================================== SFX


def sfx2():
    sz = {}
    # skeleton: dry bone rattle
    n = secs(0.6)
    x = np.zeros(n)
    t0 = 0
    while t0 < n - secs(0.05):
        m = secs(rng.uniform(0.012, 0.03))
        click = highpass(noise(m), 0.5) * env(m, 0.0005, 0.006) * rng.uniform(0.5, 1.0)
        click += tone(rng.uniform(1400, 2600), m) * env(m, 0.0005, 0.004) * 0.3
        x[t0:t0 + m] += click
        t0 += secs(rng.uniform(0.02, 0.06))
    x *= np.minimum(1, (n - np.arange(n)) / secs(0.2))
    sz['s_skel'] = save_wav('s_skel.wav', reverb(x, mix=0.3), 0.8)
    # clown: creepy giggle
    z = monster_voice('s_clown', 'Peekaboo!', 'k:am_puck', 120, 50, 1.08,
                      'vibrato=f=5:d=0.2,highpass=f=150,lowpass=f=3400,aecho=0.8:0.4:40:0.2')
    sz['s_clown'] = save_wav('s_clown.wav', pad(dist(z * 1.2, 1.3), 0.03), 0.7)
    # werewolf howl: rising/falling voiced tone with growl
    n = secs(1.3)
    tt = np.arange(n) / SR
    f0 = 260 + 340 * np.sin(np.clip(tt / 1.2, 0, 1) * np.pi) ** 0.7 + 8 * np.sin(tt * 40)
    src = tone(f0, n, 'saw') * 0.5 + tone(f0 * 2, n) * 0.25 + lowpass(noise(n), 0.2) * 0.25
    x = lowpass(src, 0.3) * np.minimum(1, tt / 0.15) * np.minimum(1, (1.3 - tt) / 0.4)
    sz['s_wolf'] = save_wav('s_wolf.wav', reverb(x, (0.07, 0.11, 0.17), 0.45, 0.5), 0.85)
    # bat: chittering screeches
    n = secs(0.45)
    x = np.zeros(n)
    for k in range(5):
        o = secs(0.02 + k * 0.08); m = secs(0.05)
        if o + m > n:
            break
        f = np.linspace(4200, 2600, m) + rng.uniform(-300, 300)
        x[o:o + m] += tone(f, m) * env(m, 0.002, 0.02) * (0.7 + 0.3 * rng.rand())
    sz['s_bat'] = save_wav('s_bat.wav', x, 0.6)
    # vampire hiss
    n = secs(0.7)
    tt = np.arange(n) / SR
    x = highpass(noise(n), 0.4) * np.minimum(1, tt / 0.05) * np.exp(-tt * 3)
    x += highpass(lowpass(noise(n), 0.6), 0.3) * np.exp(-np.abs(tt - 0.2) * 8) * 0.6
    sz['s_vamp'] = save_wav('s_vamp.wav', reverb(x, mix=0.3), 0.8)
    # Mister Giggles: big maniacal laugh
    z = monster_voice('s_giggle', 'Ha ha ha ha!', 'k:am_puck', 120, 50, 0.85,
                      'highpass=f=100,lowpass=f=2800,acompressor=threshold=-20dB:ratio=4:makeup=6,aecho=0.8:0.55:70|150:0.3|0.18')
    sz['s_giggle'] = save_wav('s_giggle.wav', pad(dist(z * 1.2, 1.4), 0.03), 0.8)
    # the Count: deep "mwahaha"
    z = monster_voice('s_count', 'mwa ha ha', 'mb-en1', 140, 25, 0.72,
                      'lowpass=f=2200,acompressor=threshold=-20dB:ratio=4:makeup=8,aecho=0.8:0.7:90|200:0.4|0.25')
    sz['s_count'] = save_wav('s_count.wav', dist(z * 1.5, 2.0), 0.95)
    # thrown knife: thin swish + tick
    n = secs(0.28)
    tt = np.arange(n) / SR
    x = highpass(noise(n), 0.55) * np.exp(-((tt - 0.09) / 0.05) ** 2) + tone(2400, n) * env(n, 0.001, 0.01) * 0.3
    sz['s_knife'] = save_wav('s_knife.wav', x, 0.7)
    # clown horn honk: two squeezes
    def honk(f, d):
        m = secs(d)
        ff = f * (1 + 0.06 * np.exp(-np.arange(m) / SR * 20))
        s = tone(ff, m, 'saw') + tone(ff * 1.5, m, 'saw') * 0.4
        s = lowpass(s, 0.35) - lowpass(s, 0.04)
        return s * env(m, 0.01, d, 1.0) * np.minimum(1, (m - np.arange(m)) / secs(0.04))
    x = np.concatenate([honk(390, 0.17), np.zeros(secs(0.05)), honk(330, 0.22)])
    sz['s_honk'] = save_wav('s_honk.wav', dist(x, 1.8), 0.85)
    # teleport: reversed swell into a poof with sparkle
    n = secs(0.6)
    tt = np.arange(n) / SR
    x = lowpass(noise(n), 0.3) * (tt / 0.45) ** 2 * (tt < 0.45) + lowpass(noise(n), 0.15) * np.exp(-np.maximum(0, tt - 0.45) * 18) * (tt >= 0.45) * 1.5
    for k in range(6):
        o = secs(0.45 + k * 0.02); m = n - o
        x[o:] += tone(1800 + k * 400, m) * env(m, 0.001, 0.05) * 0.15
    sz['s_tele'] = save_wav('s_tele.wav', reverb(x, mix=0.4), 0.85)
    # cartoon bonk: woodblock knock plus a falling boing
    n = secs(0.7)
    tt = np.arange(n) / SR
    x = tone(900, n) * env(n, 0.0005, 0.03) * 1.2 + lowpass(noise(n), 0.4) * env(n, 0.0005, 0.01)
    x += tone(420 * np.exp(-tt * 1.2) * (1 + 0.08 * np.sin(tt * 60)), n) * env(n, 0.01, 0.5) * 0.7
    sz['s_bonk'] = save_wav('s_bonk.wav', x, 0.85)
    # kid's scream
    z = monster_voice('s_scream', 'aaaaaaaah', 'en-us+f5', 110, 99, 1.3, 'highpass=f=250,lowpass=f=3800,aecho=0.8:0.4:40:0.2')
    sz['s_scream'] = save_wav('s_scream.wav', dist(z * 1.2, 1.5), 0.85)
    return sz

# ================================================================== music


def m_level5():
    """Main Street Mayhem: surf-horror shuffle in A minor (twangy guitar, organ stabs, swing drums)."""
    Q = PPQ
    gtr = Track(0, 27, 96, 44, 50)      # clean electric (twang)
    organ = Track(1, 17, 74, 84, 60)    # percussive organ
    bass = Track(2, 33, 104, 64, 20)
    lead = Track(3, 29, 86, 70, 50)     # overdriven guitar
    sax = Track(4, 66, 78, 54, 60)
    d = Track(9, None, 104, 64, 30)
    T = 2 * Q // 3                       # swung eighth (long part)
    def bar_bass(t, root):
        pat = [0, 7, 12, 10]
        for k, s in enumerate(pat):
            bass.note(t + k * Q, Q - 10, root + s, 104)
    def drums(t, bars, fill=False):
        for b in range(bars):
            bt = t + b * 4 * Q
            for k in range(4):
                d.note(bt + k * Q, Q // 4, 42, 78)
                d.note(bt + k * Q + T, Q // 4, 42, 58)
            d.note(bt, Q // 4, 36, 110); d.note(bt + 2 * Q + T, Q // 4, 36, 96)
            d.note(bt + Q, Q // 4, 38, 104); d.note(bt + 3 * Q, Q // 4, 38, 108)
            if fill and b == bars - 1:
                for k in range(6):
                    d.note(bt + 2 * Q + k * Q // 3, Q // 4, 45 + (k % 3), 90 + k * 4)
    roots = ['A1', 'A1', 'D2', 'A1', 'E2', 'D2', 'A1', 'E2']
    surf = "A4:0.5 C5:0.5 E5:0.5 A5:0.5 G5:0.5 E5:0.5 D#5:0.5 E5:0.5 "
    t = 0
    for rep in range(3):
        st = t
        for b, r in enumerate(roots):
            bt = st + b * 4 * Q
            bar_bass(bt, n2m(r))
            for k in (0, 2):
                for nn in (0, 3, 7):
                    organ.note(bt + k * Q + T, Q // 3, n2m(r) + 24 + nn, 70)
        drums(st, 8, fill=True)
        if rep == 0:
            seq(gtr, st, (surf * 2) + "D5:0.5 F5:0.5 A5:0.5 D6:0.5 C6:0.5 A5:0.5 G#5:0.5 A5:0.5 " + surf +
                "B4:0.5 D5:0.5 E5:0.5 G#5:0.5 B5:1 G#5:1 " + "A4:0.5 C5:0.5 E5:0.5 A5:0.5 G5:0.5 E5:0.5 D5:1 " + surf +
                "E5:1 D#5:1 E5:1 G#4:1", Q, 92, 0.8)
        elif rep == 1:
            seq(sax, st, "E5:1.5 D5:0.5 C5:1 A4:1 C5:2 B4:1 A4:1 F5:1.5 E5:0.5 D5:1 A4:1 E5:4 "
                         "E5:1.5 D5:0.5 C5:1 A4:1 G#4:2 B4:2 C5:1 B4:1 A4:1 G#4:1 A4:4", Q, 88, 0.95)
        else:
            seq(lead, st, "A5:0.5 A5:0.5 G5:0.5 A5:1 C6:1 A5:0.5 G5:1 E5:1 D5:0.5 E5:2 " * 2 +
                "D6:0.5 C6:0.5 A5:1 G5:1 A5:1 E5:4 " + "A5:0.5 A5:0.5 G5:0.5 A5:1 C6:1 A5:0.5 E6:4 r:4", Q, 90, 0.85)
        t = st + 32 * Q
    return write_midi('m_level5.mid', [gtr, organ, bass, lead, sax, d], 150, end=t)


def m_level6():
    """The Midway: a broken-down calliope waltz in D minor (3/4), oom-pah tuba, glockenspiel."""
    Q = PPQ
    call = Track(0, 82, 100, 64, 70)    # calliope lead
    org = Track(1, 20, 70, 50, 70)      # reed organ chords
    tuba = Track(2, 58, 104, 64, 30)
    glock = Track(3, 9, 70, 90, 80)
    strings = Track(4, 49, 60, 40, 90)
    d = Track(9, None, 84, 64, 40)
    prog = ['D', 'D', 'A', 'A', 'A', 'A', 'D', 'D', 'G', 'G', 'D', 'D', 'A', 'E', 'A', 'A']
    CH = {'D': ('D', 'F', 'A'), 'A': ('A', 'C#', 'E'), 'G': ('G', 'Bb', 'D'), 'E': ('E', 'G#', 'B')}
    mel = ("A5:1 F5:1 D5:1 A5:2 F5:1 E5:1 C#5:1 A4:1 E5:2 C#5:1 G5:1 E5:1 C#5:1 A4:1 C#5:1 E5:1 G5:2 F5:1 E5:3 "
           "F5:1 A5:1 D6:1 C6:2 A5:1 Bb5:1 G5:1 D5:1 Bb5:2 G5:1 A5:1 F5:1 D5:1 E5:1 F5:1 G#5:1 A5:3 r:3")
    t = 0
    for rep in range(3):
        st = t
        for b, ch in enumerate(prog):
            bt = st + b * 3 * Q
            root = n2m(CH[ch][0] + '2')
            tuba.note(bt, Q - 10, root, 104)
            tuba.note(bt + Q * 2, Q - 10, root + 7 if ch != 'E' else root + 7, 90)
            for k in (1, 2):
                for nn in CH[ch]:
                    org.note(bt + k * Q, Q // 2, n2m(nn + '4'), 66)
            d.note(bt, Q // 4, 36, 80)
            d.note(bt + Q, Q // 4, 75, 50); d.note(bt + 2 * Q, Q // 4, 75, 50)
        detune = 0 if rep != 2 else -1                    # the calliope goes sour on the third pass
        seq(call, st, mel, Q, 96, 0.92, transpose=detune)
        if rep >= 1:
            seq(glock, st, mel, Q, 70, 0.6, transpose=12)
        if rep == 2:
            seq(strings, st, ' '.join(c + '4+' + CH[c][2] + '4:3' for c in prog), Q, 60, 1.0)
        t = st + 48 * Q
    return write_midi('m_level6.mid', [call, org, tuba, glock, strings, d], 168, num=3, end=t)


def m_level7():
    """The Funhouse: whole-tone xylophone, chromatic bass, wobbly organ, nervous tick-tock."""
    Q = PPQ
    xylo = Track(0, 13, 96, 70, 60)
    organ = Track(1, 18, 72, 50, 70)
    bass = Track(2, 32, 100, 64, 30)
    bassoon = Track(3, 70, 84, 64, 50)
    voice = Track(4, 54, 64, 64, 90)
    d = Track(9, None, 90, 64, 30)
    t = 0
    wt = ['C5', 'D5', 'E5', 'F#5', 'G#5', 'A#5', 'C6']
    for rep in range(4):
        st = t
        for b in range(8):
            bt = st + b * 4 * Q
            r = n2m('C2') + [0, 1, 6, 5, 0, -1, 6, 7][b]
            for k in range(4):
                bass.note(bt + k * Q, Q // 2, r + (12 if k % 2 else 0), 96)
            d.note(bt, Q // 4, 76, 70); d.note(bt + Q, Q // 4, 77, 60); d.note(bt + 2 * Q, Q // 4, 76, 70); d.note(bt + 3 * Q, Q // 4, 77, 60)
            if rep >= 1:
                d.note(bt, Q // 4, 36, 96); d.note(bt + 2 * Q + Q // 2, Q // 4, 36, 80); d.note(bt + Q, Q // 4, 39, 80); d.note(bt + 3 * Q, Q // 4, 39, 84)
            seq(organ, bt, 'C4+E4+G#4:1.5 r:0.5 D4+F#4+A#4:1.5 r:0.5' if b % 2 == 0 else 'C#4+F4+A4:1.5 r:0.5 C4+E4+G#4:1.5 r:0.5', Q, 64)
        line = []
        for k in range(32):
            line.append(wt[(k * 3 + rep) % 7] + ':0.5' if k % 8 != 7 else 'r:0.5')
        seq(xylo, st, ' '.join(line * 2), Q, 88, 0.6)
        if rep in (1, 3):
            seq(bassoon, st, "C3:1 C#3:1 C3:1 B2:1 C3:2 G2:2 Ab2:1 A2:1 Bb2:1 B2:1 C3:4 " * 2, Q, 84, 0.9)
        if rep == 2:
            seq(voice, st, "C5:4 B4:4 Bb4:4 A4:4 Ab4:4 G4:4 F#4:4 G4:4", Q, 70, 1.0)
        t = st + 32 * Q
    return write_midi('m_level7.mid', [xylo, organ, bass, bassoon, voice, d], 124, end=t)


def m_boss2():
    """Mister Giggles: a frantic minor-key circus march played by a metal band."""
    Q = PPQ
    gtr = Track(0, 30, 98, 44, 30)
    gtr2 = Track(1, 30, 82, 84, 30)
    bass = Track(2, 34, 106, 64, 20)
    brass = Track(3, 61, 92, 64, 50)
    call = Track(4, 82, 86, 70, 60)
    d = Track(9, None, 112, 64, 30)
    t = 0
    chrom = "E5:0.25 D#5:0.25 E5:0.25 F5:0.25 E5:0.25 D#5:0.25 E5:0.25 C5:0.25 A4:0.5 E4:0.5 A4:0.5 C5:0.5 "
    march = (chrom * 2 + "D5:0.25 C#5:0.25 D5:0.25 Eb5:0.25 D5:0.25 C#5:0.25 D5:0.25 Bb4:0.25 G4:0.5 D4:0.5 G4:0.5 Bb4:0.5 " * 2 +
             chrom * 2 + "F5:0.5 E5:0.5 D5:0.5 C5:0.5 B4:0.5 A4:0.5 G#4:0.5 B4:0.5 E5:1 B4:1 G#4:1 E4:1 ")
    roots = ['A1', 'A1', 'G1', 'G1', 'A1', 'A1', 'E2', 'E2']
    for rep in range(3):
        st = t
        for b, r in enumerate(roots):
            bt = st + b * 4 * Q
            m = n2m(r)
            for k in range(8):
                if k in (1, 5):
                    continue
                power(gtr, bt + k * Q // 2, Q // 2 - 6, m + 12, 104)
                bass.note(bt + k * Q // 2, Q // 2 - 6, m, 108)
            power(gtr2, bt + Q, Q - 10, m + 24, 90, False)
        drums_rock(d, st, 8, Q, variant=1)
        for b in range(8):
            for k in range(8):
                d.note(st + b * 4 * Q + k * Q // 2, Q // 4, 36, 100)
        if rep == 1:
            seq(brass, st, march, Q, 96, 0.85)
        else:
            seq(call, st, march, Q, 92, 0.8)
            if rep == 2:
                seq(brass, st, march, Q, 90, 0.85, transpose=-12)
        t = st + 32 * Q
    return write_midi('m_boss2.mid', [gtr, gtr2, bass, brass, call, d], 176, end=t)


def m_level9():
    """Blackwater Bayou: slow swamp blues in E (slide guitar, harmonica, brushed drums, crickets of tremolo strings)."""
    Q = PPQ
    slide = Track(0, 25, 94, 44, 60)     # steel-string acoustic
    harp = Track(1, 22, 86, 80, 60)      # harmonica
    bass = Track(2, 32, 100, 64, 30)
    banjo = Track(3, 105, 70, 70, 40)
    trem = Track(4, 44, 54, 64, 90)      # tremolo strings
    d = Track(9, None, 80, 64, 40)
    T = 2 * Q // 3
    prog = ['E', 'E', 'E', 'E', 'A', 'A', 'E', 'E', 'B', 'A', 'E', 'B']
    t = 0
    for rep in range(3):
        st = t
        for b, ch in enumerate(prog):
            bt = st + b * 4 * Q
            r = n2m(ch + '1') if ch != 'E' else n2m('E2')
            for k in range(4):
                bass.note(bt + k * Q, T - 6, r, 98); bass.note(bt + k * Q + T, Q - T - 6, r + 7, 80)
                d.note(bt + k * Q, Q // 4, 42 if k % 2 == 0 else 38, 50 if k % 2 == 0 else 62)
                d.note(bt + k * Q + T, Q // 4, 42, 40)
            d.note(bt, Q // 4, 36, 70)
            for k in range(2):
                for nn in (0, 7, 12, 16):
                    banjo.note(bt + 2 * Q * k + Q + nn // 4 * 10, Q // 2, r + 24 + nn - (4 if ch == 'B' else 0), 60)
            trem.note(bt, 4 * Q - 10, r + 24, 44); trem.note(bt, 4 * Q - 10, r + 31, 40)
        if rep != 1:
            seq(slide, st, "B4:2 G4:1 E4:1 G4:2 r:2 B4:1 D5:1 E5:2 D5:2 B4:2 "
                           "A4:2 C5:1 C#5:1 E5:2 r:2 B4:1 G4:1 E4:2 r:4 "
                           "F#4:2 A4:2 G4:2 E4:2 B3:2 D4:2 E4:4 r:4", Q, 90, 0.9, transpose=12 if rep == 2 else 0)
        else:
            seq(harp, st, "E5:1.5 G5:0.5 A5:1 Bb5:1 B5:4 r:4 A5:1.5 G5:0.5 E5:2 r:4 "
                          "D5:1 E5:1 G5:2 E5:4 r:4 B4:2 D5:2 E5:4 r:4", Q, 88, 0.95)
        t = st + 48 * Q
    return write_midi('m_level9.mid', [slide, harp, bass, banjo, trem, d], 88, end=t)


def m_level10():
    """The Mad Lab: buzzing sequencer arpeggios, theremin-like lead, electric pulses."""
    Q = PPQ
    arp = Track(0, 81, 84, 40, 40)
    pad_ = Track(1, 89, 70, 64, 90)
    bass = Track(2, 38, 100, 64, 20)
    there = Track(3, 79, 90, 80, 90)     # ocarina / whistle as a theremin stand-in
    zap = Track(4, 121, 60, 64, 60)
    d = Track(9, None, 96, 64, 30)
    chords = [('F', 'Ab', 'C'), ('Db', 'F', 'Ab'), ('Bb', 'Db', 'F'), ('C', 'E', 'G')]
    t = 0
    for rep in range(4):
        st = t
        for b in range(8):
            ch = chords[b % 4]
            bt = st + b * 4 * Q
            ns = [n2m(c + '4') for c in ch]
            ns = [n if n >= ns[0] else n + 12 for n in ns]
            seqn = ns + [ns[0] + 12] + ns[::-1][1:] + [ns[0] - 12]
            for k in range(16):
                arp.note(bt + k * Q // 4, Q // 4 - 4, seqn[k % len(seqn)], 70 + (k % 4 == 0) * 16)
            bass.note(bt, Q * 2 - 10, ns[0] - 24, 100); bass.note(bt + 2 * Q + Q // 2, Q - 10, ns[0] - 24, 90)
            bass.note(bt + 3 * Q + Q // 2, Q // 2 - 6, ns[0] - 12, 90)
            pad_.note(bt, 4 * Q - 10, ns[0], 60); pad_.note(bt, 4 * Q - 10, ns[2], 54)
            d.note(bt, Q // 4, 36, 110); d.note(bt + Q, Q // 4, 40, 90); d.note(bt + 2 * Q, Q // 4, 36, 100); d.note(bt + 3 * Q, Q // 4, 40, 96)
            for k in range(8):
                d.note(bt + k * Q // 2, Q // 4, 42, 60)
            if b % 4 == 3:
                zap.note(bt + 3 * Q, Q, n2m('C4'), 70)
        if rep % 2 == 1:
            seq(there, st, "C6:3 Db6:1 C6:2 Ab5:2 F5:4 r:4 Bb5:3 C6:1 Db6:2 F6:2 E6:8", Q, 86, 1.0)
        t = st + 32 * Q
    return write_midi('m_level10.mid', [arp, pad_, bass, there, zap, d], 132, end=t)


def m_level11():
    """Castle Hollowfang: a gothic harpsichord-and-organ invention in C minor with choir."""
    Q = PPQ
    hpsi = Track(0, 6, 96, 44, 70)
    org = Track(1, 19, 84, 80, 80)
    choir = Track(2, 52, 70, 64, 95)
    ped = Track(3, 19, 96, 64, 80)
    bell = Track(4, 14, 70, 64, 90)
    d = Track(9, None, 70, 64, 50)
    subj = "C5:0.5 G4:0.5 Ab4:0.5 G4:0.5 C5:0.5 D5:0.5 Eb5:0.5 D5:0.5 C5:0.5 B4:0.5 C5:0.5 D5:0.5 G4:1 G5:1 "
    ans = "F5:0.5 C5:0.5 Db5:0.5 C5:0.5 F5:0.5 G5:0.5 Ab5:0.5 G5:0.5 F5:0.5 E5:0.5 F5:0.5 G5:0.5 C5:1 C6:1 "
    cad = "Ab5:0.5 G5:0.5 F5:0.5 Eb5:0.5 D5:0.5 C5:0.5 B4:0.5 D5:0.5 C5:2 G4:2 "
    roots = ['C2', 'C2', 'F2', 'F2', 'Ab1', 'G1', 'C2', 'G1']
    t = 0
    for rep in range(3):
        st = t
        seq(hpsi, st, subj + ans + subj + cad, Q, 92, 0.85)
        seq(org, st + 8 * Q, subj + ans + cad, Q, 76, 0.9, transpose=-12)
        for b, r in enumerate(roots):
            ped.note(st + b * 4 * Q, 4 * Q - 10, n2m(r), 92)
            d.note(st + b * 4 * Q, Q, 47, 60)
        if rep >= 1:
            seq(choir, st, "C5+Eb5:8 F4+Ab4:8 Ab4+C5:4 G4+B4:4 C5+Eb5:4 B4+D5:4", Q, 66, 1.0)
        bell.note(st, 4 * Q, n2m('C6'), 64); bell.note(st + 16 * Q, 4 * Q, n2m('G5'), 60)
        t = st + 32 * Q
    return write_midi('m_level11.mid', [hpsi, org, choir, ped, bell, d], 104, end=t)


def m_boss3():
    """Count Hollowfang: thundering organ over a metal gallop in D minor."""
    Q = PPQ
    org = Track(0, 19, 104, 64, 80)
    gtr = Track(1, 30, 96, 44, 30)
    bass = Track(2, 34, 106, 64, 20)
    choir = Track(3, 52, 84, 64, 95)
    timp = Track(4, 47, 108, 64, 50)
    d = Track(9, None, 112, 64, 30)
    roots = ['D2', 'D2', 'Bb1', 'Bb1', 'G1', 'G1', 'A1', 'A1']
    toc = ("D6:0.25 C6:0.25 Bb5:0.25 A5:0.25 G5:0.25 F5:0.25 E5:0.25 D5:0.25 C#5:1 D5:2 "
           "F6:0.25 E6:0.25 D6:0.25 C6:0.25 Bb5:0.25 A5:0.25 G5:0.25 F5:0.25 E5:1 A5:2 ")
    t = 0
    for rep in range(3):
        st = t
        for b, r in enumerate(roots):
            bt = st + b * 4 * Q
            m = n2m(r)
            for k in range(4):
                for g in (0, Q // 4 * 2, Q // 4 * 3):          # gallop
                    power(gtr, bt + k * Q + g, Q // 4 - 4, m + 12, 100)
                    bass.note(bt + k * Q + g, Q // 4 - 4, m, 104)
                    d.note(bt + k * Q + g, Q // 4, 36, 96)
                d.note(bt + k * Q, Q // 4, 42, 70)
            d.note(bt + Q, Q // 4, 38, 110); d.note(bt + 3 * Q, Q // 4, 38, 112)
            timp.note(bt, Q, m + 12 if m + 12 <= 53 else m, 110)
        seq(org, st, toc * 4, Q, 100, 0.95, transpose=0 if rep != 1 else -12)
        seq(choir, st, "D4+A4:4 D4+A4:4 D4+F4:4 D4+F4:4 D4+G4:4 Bb3+G4:4 C#4+E4:4 C#4+A4:4", Q, 80, 1.0)
        if rep == 2:
            d.note(st, Q, 49, 120)
        t = st + 32 * Q
    return write_midi('m_boss3.mid', [org, gtr, bass, choir, timp, d], 160, end=t)


def m_cut():
    """Cutscene sting: a sneaky, comic tuba-and-bassoon march that ends on a wah-wah."""
    Q = PPQ
    tuba = Track(0, 58, 100, 64, 40)
    bsn = Track(1, 70, 92, 64, 50)
    pizz = Track(2, 45, 90, 64, 50)
    trb = Track(3, 57, 96, 64, 60)
    d = Track(9, None, 84, 64, 40)
    t = 0
    for rep in range(4):
        st = t
        seq(tuba, st, "D2:1 A1:1 D2:1 A1:1 Bb1:1 F1:1 A1:1 E1:1 ", Q, 96, 0.5)
        seq(pizz, st, "r:0.5 F3+A3:0.5 r:0.5 F3+A3:0.5 r:0.5 F3+A3:0.5 r:0.5 F3+A3:0.5 r:0.5 D3+F3:0.5 r:0.5 D3+F3:0.5 r:0.5 C#3+E3:0.5 r:0.5 C#3+E3:0.5", Q, 76)
        if rep % 2 == 1:
            seq(bsn, st, "D4:0.5 E4:0.5 F4:0.5 G4:0.5 A4:1 F4:1 Bb4:0.5 A4:0.5 G4:0.5 F4:0.5 E4:2", Q, 90, 0.8)
        for k in range(8):
            d.note(st + k * Q, Q // 4, 76 if k % 2 == 0 else 77, 70)
        t = st + 8 * Q
    # wah wah waaah
    for k, nm in enumerate(('A3', 'Ab3', 'G3')):
        trb.note(t + k * Q, Q - 8, n2m(nm), 100)
    trb.note(t + 3 * Q, 3 * Q, n2m('F#3'), 104)
    t += 7 * Q
    return write_midi('m_cut.mid', [tuba, bsn, pizz, trb, d], 132, end=t)


MUSIC = [m_level5, m_level6, m_level7, m_boss2, m_level9, m_level10, m_level11, m_boss3, m_cut]

# ================================================================== sounds.txt (every key)

SOUNDS_TXT = A.SOUNDS_TXT.replace('''music.level4  = /snd/m_boss.mid
music.win     = /snd/m_win.mid
music.dead    = /snd/m_dead.mid''', '''music.level4  = /snd/m_boss.mid
music.level5  = /snd/m_level5.mid
music.level6  = /snd/m_level6.mid
music.level7  = /snd/m_level7.mid
music.level8  = /snd/m_boss2.mid
music.level9  = /snd/m_level9.mid
music.level10 = /snd/m_level10.mid
music.level11 = /snd/m_level11.mid
music.level12 = /snd/m_boss3.mid
music.win     = /snd/m_win.mid
music.dead    = /snd/m_dead.mid
music.cutscene= /snd/m_cut.mid''').replace('''sfx.bossdie   = /snd/s_bossdie.wav''', '''sfx.bossdie   = /snd/s_bossdie.wav
sfx.skel      = /snd/s_skel.wav
sfx.clown     = /snd/s_clown.wav
sfx.wolf      = /snd/s_wolf.wav
sfx.bat       = /snd/s_bat.wav
sfx.vamp      = /snd/s_vamp.wav
sfx.giggle    = /snd/s_giggle.wav
sfx.count     = /snd/s_count.wav
sfx.knife     = /snd/s_knife.wav
sfx.honk      = /snd/s_honk.wav
sfx.tele      = /snd/s_tele.wav
sfx.bonk      = /snd/s_bonk.wav
sfx.scream    = /snd/s_scream.wav''').replace('''voice.die     = /snd/v_die.wav''', '''voice.die     = /snd/v_die.wav
voice.start3  = /snd/v_start3.wav
voice.start4  = /snd/v_start4.wav
voice.kclown  = /snd/v_kclown.wav
voice.kskel   = /snd/v_kskel.wav
voice.kwolf   = /snd/v_kwolf.wav
voice.kbat    = /snd/v_kbat.wav
voice.kvamp   = /snd/v_kvamp.wav
voice.boss2   = /snd/v_boss2.wav
voice.boss3   = /snd/v_boss3.wav
voice.win2    = /snd/v_win2.wav
voice.win3    = /snd/v_win3.wav
voice.kill4   = /snd/v_kill4.wav
voice.kill5   = /snd/v_kill5.wav

# ---- cutscenes (Butch, the Pumpkin King, the kid, Mister Giggles, Count Hollowfang) ----
voice.c1a     = /snd/v_c1a.wav
voice.c1b     = /snd/v_c1b.wav
voice.c1c     = /snd/v_c1c.wav
voice.c1d     = /snd/v_c1d.wav
voice.c1e     = /snd/v_c1e.wav
voice.c2a     = /snd/v_c2a.wav
voice.c2b     = /snd/v_c2b.wav
voice.c2c     = /snd/v_c2c.wav
voice.c3a     = /snd/v_c3a.wav
voice.c3b     = /snd/v_c3b.wav
voice.c3c     = /snd/v_c3c.wav
voice.c3d     = /snd/v_c3d.wav''')

if __name__ == '__main__':
    what = sys.argv[1:] or ['voice', 'sfx', 'music']
    if 'music' in what:
        for f in MUSIC:
            print(f.__name__, f(), 'bytes')
    if 'voice' in what:
        tot = sum(voice(*v) for v in BUTCH)
        tot += sum(char_line(*c) for c in CHARS)
        print('voice total', tot)
    if 'sfx' in what:
        s = sfx2()
        print('sfx total', sum(s.values()), s)
    with open(os.path.join(A.OUT, 'sounds.txt'), 'w') as f:
        f.write(SOUNDS_TXT)
