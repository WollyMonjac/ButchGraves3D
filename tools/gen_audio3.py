#!/usr/bin/env python3
"""Episode 4 audio (Halloween 2099): Butch's new one-liners, Dr. Franken, robot SFX and four synth tracks.
All original. Run after gen_audio.py and gen_audio2.py (it rewrites res/snd/sounds.txt with every key)."""
import os, sys
import numpy as np
import gen_audio as A
import gen_audio2 as A2
from gen_audio import (SR, save_wav, secs, env, noise, lowpass, highpass, tone, reverb, pad, dist, voice, Track, write_midi,
                       seq, power, n2m, PPQ)
from gen_audio2 import char_line

rng = np.random.RandomState(11)

# ================================================================== voices

BUTCH = [
    ('v_start5', "Halloween, twenty ninety-nine. Same monsters. More batteries.", 'mb-us2', 145, 28, 0.9),
    ('v_krobot', "Scrap metal.", 'mb-us2', 130, 26, 0.9),
    ('v_kdrone', "Unplugged.", 'mb-us2', 125, 26, 0.9),
    ('v_kspider', "Squish.", 'mb-us2', 120, 26, 0.9),
    ('v_boss4', "Let's see what you're made of, tin man.", 'mb-us2', 145, 26, 0.88),
    ('v_win4', "Recycled.", 'mb-us2', 120, 26, 0.88),
    ('v_tele', "Whoa. That tickles.", 'mb-us2', 135, 28, 0.9),
    ('v_shift', "Did the walls just move?", 'mb-us2', 140, 30, 0.9),
    ('v_c4a', "Should've stuck to pumpkins, Doc.", 'mb-us2', 140, 28, 0.9),
    ('v_c4b', "Terrifying.", 'mb-us2', 110, 26, 0.9),
    ('v_c4c', "Time to go home.", 'mb-us2', 130, 26, 0.9),
    ('v_c1f', "Don't mind if I do.", 'mb-us2', 135, 28, 0.9),
    # the gory cutscenes
    ('v_g1a', "Shut your pie hole.", 'mb-us2', 130, 26, 0.9),
    ('v_g1b', "Field goal.", 'mb-us2', 125, 26, 0.9),
    ('v_g2a', "Honk this.", 'mb-us2', 125, 26, 0.88),
    ('v_g4a', "Fetch.", 'mb-us2', 120, 26, 0.9),
]

DOC_FX = 'vibrato=f=6:d=0.25,highpass=f=180,lowpass=f=3600,acompressor=threshold=-20dB:ratio=4:makeup=6,aecho=0.8:0.4:35:0.2'
CHARS = [
    # Dr. Viktor Franken: shrill and manic
    ('v_c4d', "You ruined my masterpiece!", 'k:bm_george', 170, 80, 1.1, DOC_FX, 1.5),
    ('v_c4e', "Behold! My ultimate creation!", 'k:bm_george', 150, 85, 1.1, DOC_FX, 1.5),
    ('v_c4f', "It's a prototype!", 'k:bm_george', 185, 90, 1.12, DOC_FX, 1.5),
    # the Pumpkin King's head, unimpressed
    ('v_g1c', "Wait! No, no, no!", 'k:am_onyx', 160, 20, 0.8,
     'highpass=f=90,lowpass=f=2600,acompressor=threshold=-22dB:ratio=5:makeup=8,aecho=0.8:0.5:50:0.25', 2.4),
    ('v_g4b', "My baby!", 'k:bm_george', 170, 80, 1.12, DOC_FX, 1.5),
    ('v_c4g', "You're late.", 'k:am_onyx', 120, 20, 0.76,
     'highpass=f=90,lowpass=f=2600,acompressor=threshold=-22dB:ratio=5:makeup=8,aecho=0.8:0.5:50:0.25', 2.4),
]

# ================================================================== SFX


def sfx3():
    sz = {}
    # zap: crackling electric burst with a falling whine
    n = secs(0.45)
    tt = np.arange(n) / SR
    crack = highpass(noise(n), 0.45) * (rng.rand(n) < 0.35) * 1.4
    whine = tone(1600 * np.exp(-tt * 4) + 300, n, 'saw') * 0.35
    x = (crack + whine) * np.exp(-tt * 6) * np.minimum(1, tt / 0.004)
    sz['s_zap'] = save_wav('s_zap.wav', dist(x, 2.0), 0.85)
    # laser: quick downward "pew"
    n = secs(0.2)
    tt = np.arange(n) / SR
    f = 2200 * np.exp(-tt * 14) + 260
    x = tone(f, n, 'sq') * 0.5 + tone(f * 1.01, n) * 0.5
    sz['s_laser'] = save_wav('s_laser.wav', lowpass(x, 0.6) * env(n, 0.002, 0.16), 0.7)
    # chainsaw: two-stroke engine revving up and down
    n = secs(0.75)
    tt = np.arange(n) / SR
    f0 = 55 + 45 * np.sin(np.clip(tt / 0.6, 0, 1) * np.pi)
    ph = np.cumsum(f0) / SR
    pulse = (np.sin(2 * np.pi * ph) > 0.6).astype(float)
    x = lowpass(pulse * 0.8 + noise(n) * 0.35 * pulse, 0.35) + tone(f0 * 4, n, 'saw') * 0.2
    x *= np.minimum(1, tt / 0.03) * np.minimum(1, (0.75 - tt) / 0.1)
    sz['s_saw'] = save_wav('s_saw.wav', dist(x * 1.5, 3.0), 0.8)
    # robot: servo whir and a two-tone beep
    n = secs(0.6)
    tt = np.arange(n) / SR
    x = tone(320 + 900 * np.clip(tt / 0.3, 0, 1), n, 'saw') * 0.25 * (tt < 0.32) * np.minimum(1, tt / 0.02)
    for k, (o, fq) in enumerate(((0.34, 880), (0.46, 660))):
        m = secs(0.09); s0 = secs(o)
        x[s0:s0 + m] += tone(fq, m, 'sq') * 0.4 * env(m, 0.002, 0.08, 1.0)
    sz['s_robot'] = save_wav('s_robot.wav', lowpass(x, 0.7), 0.75)
    # skitter: fast metallic tapping of eight legs
    n = secs(0.5)
    x = np.zeros(n)
    t0 = 0
    while t0 < n - secs(0.03):
        m = secs(0.012)
        x[t0:t0 + m] += (highpass(noise(m), 0.6) + tone(rng.uniform(3000, 4200), m) * 0.4) * env(m, 0.0003, 0.004) * rng.uniform(0.4, 1.0)
        t0 += secs(rng.uniform(0.015, 0.035))
    sz['s_skitter'] = save_wav('s_skitter.wav', x, 0.7)
    # buzz: shock floor powering up, 60 Hz hum with crackle
    n = secs(0.7)
    tt = np.arange(n) / SR
    hum = tone(60, n, 'saw') * 0.5 + tone(120, n, 'sq') * 0.25 + tone(180, n) * 0.15
    crack = highpass(noise(n), 0.5) * (rng.rand(n) < 0.06)
    x = (hum + crack) * np.minimum(1, tt / 0.08) * np.minimum(1, (0.7 - tt) / 0.2)
    sz['s_buzz'] = save_wav('s_buzz.wav', dist(x, 1.8), 0.7)
    # stomp: huge metal footfall with a clang
    n = secs(0.9)
    tt = np.arange(n) / SR
    thump = tone(70 * np.exp(-tt * 3) + 28, n) * np.exp(-tt * 5) * 1.4
    clang = sum(tone(f, n) * np.exp(-tt * d) for f, d in ((523, 7), (781, 9), (1187, 12))) * 0.25
    x = thump + clang + lowpass(noise(n), 0.2) * np.exp(-tt * 14) * 0.8
    sz['s_stomp'] = save_wav('s_stomp.wav', reverb(dist(x, 1.6), (0.05, 0.09, 0.13), 0.4, 0.35), 0.95)
    return sz

# ================================================================== music


def drums_synth(d, t0, bars, Q, half=False, fill=True):
    """Four-on-the-floor electro beat (GM drums)."""
    for b in range(bars):
        bt = t0 + b * 4 * Q
        if b == 0:
            d.note(bt, Q, 49, 100)
        for k in range(4):
            d.note(bt + k * Q, Q // 4, 36, 112)
            if not half or k % 2 == 1:
                d.note(bt + k * Q + Q // 2, Q // 4, 42, 76)
        d.note(bt + Q, Q // 4, 39, 104)          # hand clap
        d.note(bt + 3 * Q, Q // 4, 38, 108)
        if fill and b == bars - 1:
            for k in range(8):
                d.note(bt + 2 * Q + k * Q // 4, Q // 4, 38 if k % 2 == 0 else 50, 80 + k * 4)


def m_level13():
    """Neon Graveyard: spooky synthwave in E minor (arpeggiated bass, saw lead, warm pad)."""
    Q = PPQ
    bass = Track(0, 38, 104, 64, 30)
    arp = Track(1, 81, 70, 40, 70)
    lead = Track(2, 80, 92, 84, 80)
    pad_ = Track(3, 89, 66, 64, 100)
    bell = Track(4, 14, 70, 90, 90)
    d = Track(9, None, 100, 64, 30)
    prog = [('E2', ('E', 'G', 'B')), ('C2', ('C', 'E', 'G')), ('A1', ('A', 'C', 'E')), ('B1', ('B', 'D#', 'F#'))]
    lead1 = ("B4:1.5 G4:0.5 E4:1 F#4:1 G4:2 A4:1 B4:1 C5:1.5 B4:0.5 A4:1 G4:1 E4:2 r:2 "
             "A4:1.5 C5:0.5 E5:1 D5:1 C5:2 B4:1 A4:1 B4:1.5 A4:0.5 G4:1 F#4:1 D#4:2 r:2")
    t = 0
    for rep in range(4):
        st = t
        for b in range(8):
            r, ch = prog[b % 4]
            bt = st + b * 4 * Q
            m = n2m(r)
            for k in range(8):
                bass.note(bt + k * Q // 2, Q // 2 - 6, m + (12 if k % 2 else 0), 96 + (k % 2 == 0) * 10)
            notes = [n2m(c + '4') for c in ch] + [n2m(ch[0] + '5')]
            for k in range(16):
                arp.note(bt + k * Q // 4, Q // 4 - 4, notes[k % 4], 62 + (k % 4 == 0) * 12)
            pad_.note(bt, 4 * Q - 10, notes[0] - 12, 58); pad_.note(bt, 4 * Q - 10, notes[1] - 12, 54)
        if rep >= 1:
            drums_synth(d, st, 8, Q, half=(rep == 1))
        if rep >= 2:
            seq(lead, st, lead1, Q, 96, 0.92)
        if rep % 2 == 0:
            bell.note(st, 2 * Q, n2m('B5'), 60); bell.note(st + 16 * Q, 2 * Q, n2m('E6'), 56)
        t = st + 32 * Q
    return write_midi('m_level13.mid', [bass, arp, lead, pad_, bell, d], 116, end=t)


def m_level14():
    """The Assembly Line: industrial machine groove in D (clanking percussion, synth brass stabs, pulsing bass)."""
    Q = PPQ
    bass = Track(0, 39, 108, 64, 20)
    brass = Track(1, 62, 92, 50, 50)
    lead = Track(2, 84, 86, 80, 60)
    hit = Track(3, 55, 96, 64, 70)
    d = Track(9, None, 104, 64, 30)
    riff = [0, 0, 12, 0, 3, 0, 5, 3, 0, 0, 12, 0, 7, 5, 3, 1]
    roots = ['D2', 'D2', 'F2', 'C2', 'D2', 'D2', 'Bb1', 'A1']
    stabs = "r:1 D4+F4+A4:0.5 r:1 D4+F4+A4:0.5 r:1 r:1 C4+E4+G4:0.5 r:0.5 r:1 F4+A4+C5:1 r:1"
    mel = "D5:1 F5:1 E5:0.5 D5:0.5 C5:1 D5:2 A4:2 F5:1 G5:1 A5:1 G5:0.5 F5:0.5 E5:2 C#5:2"
    t = 0
    for rep in range(4):
        st = t
        for b, r in enumerate(roots):
            bt = st + b * 4 * Q
            m = n2m(r)
            for k, o in enumerate(riff):
                bass.note(bt + k * Q // 4, Q // 4 - 4, m + o, 100 + (k % 4 == 0) * 12)
            for k in range(4):
                d.note(bt + k * Q, Q // 4, 36, 112)
                d.note(bt + k * Q + Q // 2, Q // 8, 56, 70)          # cowbell clank
                d.note(bt + k * Q + Q * 3 // 4, Q // 8, 75, 64)      # claves
            d.note(bt + Q, Q // 4, 38, 110); d.note(bt + 3 * Q, Q // 4, 38, 110); d.note(bt + 3 * Q + Q // 2, Q // 4, 38, 80)
            if b % 4 == 0:
                hit.note(bt, Q, m + 24, 100)
        if rep >= 1:
            for b in range(0, 8, 2):
                seq(brass, st + b * 4 * Q, stabs, Q, 96, 0.8, transpose=0 if b < 4 else -2)
        if rep >= 2:
            seq(lead, st, mel + ' ' + mel, Q, 92, 0.9)
        t = st + 32 * Q
    return write_midi('m_level14.mid', [bass, brass, lead, hit, d], 132, end=t)


def m_level15():
    """The Circuit Maze: sparse, unsettling C# minor; music-box arpeggios over a heartbeat pulse and data chirps."""
    Q = PPQ
    box = Track(0, 10, 80, 50, 100)
    pad_ = Track(1, 94, 64, 64, 110)
    bass = Track(2, 38, 100, 64, 40)
    chirp = Track(3, 98, 60, 90, 90)
    d = Track(9, None, 90, 64, 50)
    prog = [('C#2', ('C#', 'E', 'G#')), ('A1', ('A', 'C#', 'E')), ('F#1', ('F#', 'A', 'C#')), ('G#1', ('G#', 'B#', 'D#'))]
    t = 0
    for rep in range(4):
        st = t
        for b in range(8):
            r, ch = prog[(b // 2) % 4]
            bt = st + b * 4 * Q
            m = n2m(r)
            bass.note(bt, Q // 2, m, 104); bass.note(bt + Q // 2 + Q // 4, Q // 3, m, 84)        # heartbeat
            bass.note(bt + 2 * Q, Q // 2, m, 100); bass.note(bt + 2 * Q + Q * 3 // 4, Q // 3, m, 80)
            notes = [n2m(c + '5') for c in ch]
            for k in range(6):
                box.note(bt + k * Q * 2 // 3, Q // 2, notes[(k * 2) % 3] + (12 if k == 5 else 0), 60 + (k == 0) * 14)
            if b % 2 == 0:
                for c in ch:
                    pad_.note(bt, 8 * Q - 10, n2m(c + '3'), 52)
            d.note(bt, Q // 4, 36, 70)
            d.note(bt + 2 * Q, Q // 4, 36, 66)
            if rep >= 1:
                for k in range(8):
                    d.note(bt + k * Q // 2, Q // 8, 42, 40 + (k % 2) * 10)
                d.note(bt + 3 * Q + Q // 2, Q // 4, 37, 70)            # side stick
            if rep >= 2 and b % 2 == 1:
                for k in range(3):
                    chirp.note(bt + 3 * Q + k * Q // 6, Q // 8, n2m('C#7') - k * 5, 50)
        t = st + 32 * Q
    return write_midi('m_level15.mid', [box, pad_, bass, chirp, d], 96, end=t)


def m_boss4():
    """Frankenstein Prime: synth-metal in D minor (double kick, power chords, saw lead, choir and orchestra hits)."""
    Q = PPQ
    gtr = Track(0, 30, 98, 44, 30)
    bass = Track(1, 38, 108, 64, 20)
    lead = Track(2, 81, 94, 84, 60)
    choir = Track(3, 52, 84, 64, 100)
    hit = Track(4, 55, 100, 64, 60)
    d = Track(9, None, 112, 64, 30)
    roots = ['D2', 'D2', 'Bb1', 'Bb1', 'C2', 'C2', 'A1', 'A1']
    mel = ("D5:0.5 F5:0.5 A5:1 G5:0.5 F5:0.5 E5:1 F5:0.5 E5:0.5 D5:1 C#5:1 A4:1 "
           "Bb4:0.5 D5:0.5 F5:1 E5:0.5 D5:0.5 C5:1 D5:0.5 E5:0.5 F5:1 E5:2 "
           "D6:0.5 C6:0.5 A5:1 F5:1 G5:0.5 A5:0.5 Bb5:1 A5:1 F5:1 G5:0.5 F5:0.5 E5:1 D5:1 C#5:1 A4:1 C#5:1 E5:1 A5:2")
    t = 0
    for rep in range(3):
        st = t
        for b, r in enumerate(roots):
            bt = st + b * 4 * Q
            m = n2m(r)
            for k in range(8):
                power(gtr, bt + k * Q // 2, Q // 2 - 6, m + 12, 100 + (k % 2 == 0) * 8)
                bass.note(bt + k * Q // 2, Q // 2 - 6, m, 108)
            for k in range(16):
                d.note(bt + k * Q // 4, Q // 4, 36, 100 if k % 2 == 0 else 84)              # double kick
            for k in range(4):
                d.note(bt + k * Q, Q // 4, 51, 80)
            d.note(bt + Q, Q // 4, 38, 116); d.note(bt + 3 * Q, Q // 4, 38, 118)
            if b % 2 == 0:
                hit.note(bt, Q, m + 24, 110)
                choir.note(bt, 8 * Q - 10, m + 24, 76); choir.note(bt, 8 * Q - 10, m + 31, 72)
        if rep >= 1:
            seq(lead, st, mel, Q, 100, 0.9)
        d.note(st, Q, 49, 120)
        t = st + 32 * Q
    return write_midi('m_boss4.mid', [gtr, bass, lead, choir, hit, d], 152, end=t)


MUSIC = [m_level13, m_level14, m_level15, m_boss4]

# ================================================================== sounds.txt (every key)

SOUNDS_TXT = A2.SOUNDS_TXT.replace('''music.cutscene= /snd/m_cut.mid''', '''music.cutscene= /snd/m_cut.mid
music.level13 = /snd/m_level13.mid
music.level14 = /snd/m_level14.mid
music.level15 = /snd/m_level15.mid
music.level16 = /snd/m_boss4.mid''').replace('''sfx.scream    = /snd/s_scream.wav''', '''sfx.scream    = /snd/s_scream.wav
sfx.zap       = /snd/s_zap.wav
sfx.laser     = /snd/s_laser.wav
sfx.saw       = /snd/s_saw.wav
sfx.robot     = /snd/s_robot.wav
sfx.skitter   = /snd/s_skitter.wav
sfx.buzz      = /snd/s_buzz.wav
sfx.stomp     = /snd/s_stomp.wav''').replace('''voice.kill5   = /snd/v_kill5.wav''', '''voice.kill5   = /snd/v_kill5.wav
voice.start5  = /snd/v_start5.wav
voice.krobot  = /snd/v_krobot.wav
voice.kdrone  = /snd/v_kdrone.wav
voice.kspider = /snd/v_kspider.wav
voice.boss4   = /snd/v_boss4.wav
voice.win4    = /snd/v_win4.wav
voice.tele    = /snd/v_tele.wav
voice.shift   = /snd/v_shift.wav''').replace('''voice.c3d     = /snd/v_c3d.wav''', '''voice.c3d     = /snd/v_c3d.wav
voice.c1f     = /snd/v_c1f.wav
voice.c4a     = /snd/v_c4a.wav
voice.c4b     = /snd/v_c4b.wav
voice.c4c     = /snd/v_c4c.wav
voice.c4d     = /snd/v_c4d.wav
voice.c4e     = /snd/v_c4e.wav
voice.c4f     = /snd/v_c4f.wav
voice.c4g     = /snd/v_c4g.wav

# ---- the gory cutscenes ----
voice.g1a     = /snd/v_g1a.wav
voice.g1b     = /snd/v_g1b.wav
voice.g1c     = /snd/v_g1c.wav
voice.g2a     = /snd/v_g2a.wav
voice.g4a     = /snd/v_g4a.wav
voice.g4b     = /snd/v_g4b.wav''')

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
        s = sfx3()
        print('sfx total', sum(s.values()), s)
    with open(os.path.join(A.OUT, 'sounds.txt'), 'w') as f:
        f.write(SOUNDS_TXT)
    for k in ('music.level16', 'sfx.stomp', 'voice.c4g', 'voice.shift', 'voice.g4b'):
        assert k in SOUNDS_TXT, k
