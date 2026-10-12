#!/usr/bin/env python3
"""Episode 5 audio (the jungle): Butch's new lines, Professor Crane, Seven Death, the jungle SFX and four new tracks.
All original. Run after gen_audio.py, gen_audio2.py and gen_audio3.py (it rewrites res/snd/sounds.txt with every key)."""
import os, sys
import numpy as np
import gen_audio as A
import gen_audio3 as A3
from gen_audio import (SR, save_wav, secs, env, noise, lowpass, highpass, tone, reverb, pad, dist, voice, Track, write_midi,
                       seq, power, n2m, PPQ, monster_voice)
from gen_audio2 import char_line

rng = np.random.RandomState(17)

# ================================================================== voices

BUTCH = [
    ('v_start6', "Jungle. Why'd it have to be jungle?", 'mb-us2', 140, 28, 0.9),
    ('v_boss5', "Seven deaths? I only need one.", 'mb-us2', 140, 26, 0.88),
    ('v_win5', "Make that eight.", 'mb-us2', 125, 26, 0.88),
    ('v_kmummy', "It's a wrap.", 'mb-us2', 130, 28, 0.9),
    ('v_kjag', "Bad kitty.", 'mb-us2', 125, 28, 0.9),
    ('v_kconq', "Conquer this.", 'mb-us2', 130, 26, 0.9),
    ('v_kweep', "Cry me a river.", 'mb-us2', 135, 28, 0.9),
    ('v_pit', "Watch your step.", 'mb-us2', 130, 28, 0.9),
    ('v_idol', "Uh oh.", 'mb-us2', 110, 30, 0.9),
    ('v_radio', "My radio's acting up.", 'mb-us2', 135, 28, 0.9),
    ('v_other', "Okay. That's new.", 'mb-us2', 125, 28, 0.9),
    ('v_rise', "Stay down!", 'mb-us2', 140, 30, 0.9),
    ('v_c5e', "Eternal life. As a keychain.", 'mb-us2', 135, 28, 0.9),
    ('v_c5f', "Happy Day of the Dead.", 'mb-us2', 130, 26, 0.88),
    ('v_g5b', "Should've left it in the ground, Prof.", 'mb-us2', 140, 26, 0.9),
]

CRANE_FX = 'highpass=f=140,lowpass=f=3800,acompressor=threshold=-20dB:ratio=4:makeup=6,aecho=0.8:0.35:30:0.15'
SEVEN_FX = ('highpass=f=60,lowpass=f=2600,acompressor=threshold=-22dB:ratio=6:makeup=9,'
            'aecho=0.8:0.6:90|180|260:0.45|0.3|0.2')
CHARS = [
    # Professor Alistair Crane: plummy, pompous, greedy (Kokoro; the MBROLA en1 voice was tried and sounded worse)
    ('v_c5a', "Out of my way, gravedigger! With his lordship dead, the skull's power is mine!", 'k:bm_fable', 150, 50, 1.0, CRANE_FX, 1.4),
    ('v_c5b', "Skull of Seven Death! Grant me eternal life!", 'k:bm_fable', 140, 50, 0.98, CRANE_FX, 1.4),
    ('v_c5d', "Wait! Not like thiiis!", 'k:bm_fable', 170, 80, 1.55, 'vibrato=f=10:d=0.4,' + CRANE_FX, 1.4),
    ('v_c5g', "Unhand me, you oaf! I am immortal!", 'k:bm_fable', 165, 80, 1.5, CRANE_FX, 1.4),     # the shrunken head
    ('v_g5a', "My face! My beautiful face!", 'k:bm_fable', 175, 60, 1.08, 'vibrato=f=7:d=0.5,' + CRANE_FX, 2.0),
    # Seven Death, from the skull: a voice from very far down
    ('v_c5c', "Eternal life? Granted.", 'k:am_onyx*0.6+am_santa*0.4', 110, 20, 0.66, SEVEN_FX, 2.2),
]


# ================================================================== SFX


def burst(n, a=0.4):
    return highpass(noise(n), a)


def sfx4():
    sz = {}
    # boulder: a deep rolling rumble with stone knocks
    n = secs(0.75)
    tt = np.arange(n) / SR
    rum = lowpass(noise(n), 0.04) * 6 + tone(38 + 6 * np.sin(tt * 9), n) * 0.5
    knocks = np.zeros(n)
    for k in range(5):
        s0 = secs(0.04 + k * 0.14 + rng.uniform(0, 0.04)); m = secs(0.06)
        knocks[s0:s0 + m] += lowpass(noise(m), 0.15) * env(m, 0.001, 0.04) * 3
    x = (rum + knocks) * np.minimum(1, tt / 0.05) * np.minimum(1, (0.75 - tt) / 0.15)
    sz['s_boulder'] = save_wav('s_boulder.wav', dist(x, 1.8), 0.62)
    # darts: a click in the wall, then several thin whooshes
    n = secs(0.4)
    tt = np.arange(n) / SR
    x = np.zeros(n)
    m = secs(0.02)
    x[:m] += burst(m, 0.5) * env(m, 0.0005, 0.01) * 1.2
    for k in range(3):
        s0 = secs(0.03 + k * 0.05); m = secs(0.18)
        f = 2600 - np.arange(m) / SR * 7000
        w = highpass(noise(m), 0.3) * 0.5 + tone(np.maximum(f, 600), m) * 0.15
        x[s0:s0 + m] += w * np.sin(np.linspace(0, np.pi, m)) * (0.9 - k * 0.2)
    sz['s_darts'] = save_wav('s_darts.wav', x, 0.7)
    # musket: flintlock snap, a big powder boom, rolling echo
    n = secs(1.0)
    tt = np.arange(n) / SR
    snap = np.zeros(n); m = secs(0.015)
    snap[:m] = burst(m, 0.6) * 1.5
    boom = np.zeros(n); s0 = secs(0.03)
    bt = tt[: n - s0]
    boom[s0:] = (lowpass(noise(n - s0), 0.25) * 2.5 + tone(60 * np.exp(-bt * 6) + 35, n - s0) * 1.2) * np.exp(-bt * 7)
    x = reverb(dist(snap + boom, 2.2), (0.11, 0.19, 0.29), 0.45, 0.4)
    sz['s_musket'] = save_wav('s_musket.wav', x, 0.9)
    # roar: a big cat's snarl - rough, pitch rising then falling, throaty
    n = secs(0.8)
    tt = np.arange(n) / SR
    f0 = 110 + 90 * np.sin(np.clip(tt / 0.8, 0, 1) * np.pi)
    ph = np.cumsum(f0) / SR
    buzz = (np.sin(2 * np.pi * ph) > 0.2).astype(float) * 0.6 + tone(f0 * 2, n, 'saw') * 0.3
    x = lowpass(buzz + burst(n, 0.2) * 0.5, 0.25) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * tt))
    x *= np.minimum(1, tt / 0.06) * np.minimum(1, (0.8 - tt) / 0.25)
    sz['s_roar'] = save_wav('s_roar.wav', dist(x * 2, 2.6), 0.6)
    # mummy: a dry, dusty moan through old bandages
    d = monster_voice('s_mummy', "Uuuhhhhhh...", 'k:am_onyx', 80, 10, 0.62,
                      'highpass=f=90,lowpass=f=1800,acompressor=threshold=-22dB:ratio=5:makeup=8,aecho=0.8:0.4:60:0.25')
    d = d[:secs(1.1)]
    d = d + lowpass(noise(len(d)), 0.3) * 0.08 * np.abs(d).max()
    sz['s_mummy'] = save_wav('s_mummy.wav', pad(dist(d * 1.4, 1.8), 0.05), 0.75)
    # wail: la llorona's lament - a long falling cry that hangs in the air
    d = monster_voice('s_wail', "¡Aaaaay!", 'k:ef_dora@es', 70, 60, 1.12,
                      'vibrato=f=6:d=0.6,highpass=f=300,lowpass=f=3600,aecho=0.8:0.6:120|240:0.4|0.25')
    d = d[:secs(1.3)]
    n = len(d)
    tt = np.arange(n) / SR
    ghost = tone(900 * np.exp(-tt * 0.7) + 300 + 25 * np.sin(2 * np.pi * 5.5 * tt), n) * 0.18 * np.abs(d).max()
    sz['s_wail'] = save_wav('s_wail.wav', pad(d + ghost * np.minimum(1, tt / 0.2), 0.05), 0.78)
    # siren: the town's air-raid siren winding up, wailing, winding down
    n = secs(2.3)
    tt = np.arange(n) / SR
    f = 180 + 520 * np.clip(tt / 0.8, 0, 1) - 70 * np.clip((tt - 1.0) / 0.25, 0, 1) + 70 * np.clip((tt - 1.25) / 0.25, 0, 1) \
        - 560 * np.clip((tt - 1.6) / 0.7, 0, 1)
    x = tone(f, n, 'saw') * 0.4 + tone(f * 2.01, n) * 0.25 + tone(f * 1.5, n, 'sq') * 0.1
    x = lowpass(x, 0.35) * np.minimum(1, tt / 0.25) * np.minimum(1, (2.3 - tt) / 0.45)
    sz['s_siren'] = save_wav('s_siren.wav', reverb(x, (0.09, 0.17, 0.23), 0.5, 0.45), 0.7)
    # static: a burst of radio hiss and crackle
    n = secs(0.22)
    tt = np.arange(n) / SR
    x = highpass(noise(n), 0.2) * 0.5 + burst(n, 0.6) * (rng.rand(n) < 0.05) * 1.6
    x *= 0.6 + 0.4 * (np.sin(2 * np.pi * 37 * tt) > 0)
    x = lowpass(x, 0.6) * np.minimum(1, tt / 0.01) * np.minimum(1, (0.22 - tt) / 0.05)
    sz['s_static'] = save_wav('s_static.wav', x, 0.45)
    # spikes: a stone click and a ringing steel shing
    n = secs(0.5)
    tt = np.arange(n) / SR
    x = sum(tone(f, n) * np.exp(-tt * k) for f, k in ((2100, 9), (3170, 12), (4410, 15))) * 0.35
    x += burst(n, 0.5) * np.exp(-tt * 40) * 0.8 + lowpass(noise(n), 0.2) * np.exp(-tt * 30) * 0.6
    sz['s_spikes'] = save_wav('s_spikes.wav', x * np.minimum(1, tt / 0.002), 0.7)
    # seven: Seven Death's laugh, from the bottom of the world
    d = monster_voice('s_seven', "Ha ha ha ha!", 'k:am_onyx*0.6+am_santa*0.4', 120, 20, 0.62, SEVEN_FX)
    d = d[:secs(1.2)] * np.minimum(1, (secs(1.2) - np.arange(min(len(d), secs(1.2)))) / secs(0.3))
    sz['s_seven'] = save_wav('s_seven.wav', pad(dist(d * 1.4, 2.0), 0.05), 0.8)
    # fall: a falling whistle and a far-off thud
    n = secs(0.9)
    tt = np.arange(n) / SR
    x = tone(1400 * np.exp(-tt * 1.6) + 200, n) * 0.35 * np.minimum(1, (0.7 - tt) / 0.1).clip(0, 1)
    s0 = secs(0.7); m = n - s0
    x[s0:] += lowpass(noise(m), 0.1) * env(m, 0.002, 0.15) * 2.5
    sz['s_fall'] = save_wav('s_fall.wav', x, 0.7)
    # conq: a ghost soldier's challenge, in old Spanish
    d = monster_voice('s_conq', "¡Intrusos!", 'k:em_alex@es', 150, 30, 0.82,
                      'vibrato=f=5:d=0.3,highpass=f=120,lowpass=f=2800,acompressor=threshold=-22dB:ratio=4:makeup=7,'
                      'aecho=0.8:0.5:70|140:0.35|0.2')
    sz['s_conq'] = save_wav('s_conq.wav', pad(dist(d * 1.3, 1.7), 0.05), 0.8)
    return sz

# ================================================================== music


def jungle_drums(d, t0, bars, Q, busy=1):
    """Hand percussion: congas, bongos and a shaker (GM drums)."""
    for b in range(bars):
        bt = t0 + b * 4 * Q
        for k in range(16):
            d.note(bt + k * Q // 4, Q // 8, 70, 46 + (k % 4 == 0) * 16)               # maracas
        for (o, n_, v) in ((0, 64, 100), (0.75, 63, 80), (1.5, 62, 86), (2, 64, 96), (2.5, 63, 82), (3, 63, 90), (3.5, 62, 78)):
            d.note(bt + int(o * Q), Q // 4, n_, v)
        if busy:
            for (o, n_) in ((1, 61), (1.25, 60), (3.25, 61), (3.75, 60)):
                d.note(bt + int(o * Q), Q // 4, n_, 76)
        if busy > 1:
            d.note(bt, Q // 2, 36, 96); d.note(bt + 2 * Q, Q // 2, 36, 90)


def m_level17():
    """The Lost Temple: a brassy adventure march in C minor over jungle hand drums and a driving string ostinato."""
    Q = PPQ
    strings = Track(0, 48, 92, 54, 70)
    brass = Track(1, 61, 96, 74, 60)
    tpt = Track(2, 56, 100, 64, 60)
    timp = Track(3, 47, 108, 64, 50)
    flute = Track(4, 75, 82, 40, 80)
    bass = Track(5, 32, 100, 64, 30)
    d = Track(9, None, 96, 64, 40)
    prog = [('C', ('C', 'Eb', 'G')), ('Ab', ('Ab', 'C', 'Eb')), ('Bb', ('Bb', 'D', 'F')), ('G', ('G', 'B', 'D'))]
    theme = ("G4:0.75 G4:0.25 C5:1 D5:1 Eb5:1 F5:1.5 Eb5:0.5 C5:2 D5:0.75 D5:0.25 F5:1 Bb4:1 D5:1 B4:2 G4:2 "
             "G4:0.75 G4:0.25 C5:1 D5:1 Eb5:1 Ab5:1.5 G5:0.5 Eb5:1 C5:1 F5:1 D5:1 Bb4:1 D5:1 C5:3 r:1")
    counter = "Eb4:2 G4:2 C4:2 Eb4:2 D4:2 F4:2 D4:2 B3:2 Eb4:2 G4:2 Ab4:2 C5:2 Bb4:2 F4:2 G4:4"
    t = 0
    for rep in range(4):
        st = t
        for b in range(8):
            r, ch = prog[b % 4]
            bt = st + b * 4 * Q
            m = n2m(r + '2')
            arp = [m, m + 7, m + 12, m + 7]
            for k in range(8):
                strings.note(bt + k * Q // 2, Q // 2 - 4, arp[k % 4] + 12, 78 + (k % 4 == 0) * 12)
            bass.note(bt, Q - 8, m, 104); bass.note(bt + 2 * Q, Q - 8, m, 96); bass.note(bt + 3 * Q + Q // 2, Q // 2, m + 7, 90)
            timp.note(bt, Q // 2, m + 12 if r != 'G' else m, 104)
            if b % 4 == 3:
                for k in range(4):
                    timp.note(bt + 2 * Q + k * Q // 4, Q // 4, m, 80 + k * 8)
            if rep >= 1:
                for k, c in enumerate(ch):
                    brass.note(bt, Q + Q // 2, n2m(c + '4'), 82)
                    brass.note(bt + 2 * Q + Q // 2, Q, n2m(c + '4'), 74)
        jungle_drums(d, st, 8, Q, busy=1 + (rep >= 2))
        if rep >= 2:
            seq(tpt, st, theme, Q, 100, 0.92, transpose=12 if rep == 3 else 0)
        if rep == 3:
            seq(flute, st, counter, Q, 80, 0.95, transpose=12)
        d.note(st, Q, 49, 100)
        t = st + 32 * Q
    return write_midi('m_level17.mid', [strings, brass, tpt, timp, flute, bass, d], 120, end=t)


def m_level18():
    """River of Bones: a Spanish-tinged jungle groove (the conquistadors' Andalusian cadence) - nylon guitar, marimba,
    pan flute and castanets over congas."""
    Q = PPQ
    gtr = Track(0, 24, 96, 50, 60)
    mar = Track(1, 12, 90, 80, 60)
    flute = Track(2, 75, 92, 60, 80)
    bass = Track(3, 32, 104, 64, 30)
    pad_ = Track(4, 49, 64, 64, 100)
    d = Track(9, None, 92, 64, 40)
    prog = [('D', ('D', 'F', 'A')), ('C', ('C', 'E', 'G')), ('Bb', ('Bb', 'D', 'F')), ('A', ('A', 'C#', 'E'))]
    mel1 = ("A4:1 D5:0.5 E5:0.5 F5:1 E5:0.5 D5:0.5 E5:1 C5:1 G4:2 F5:1 D5:0.5 Bb4:0.5 D5:1 F5:1 E5:1.5 C#5:0.5 A4:2")
    mel2 = ("D5:0.5 F5:0.5 A5:1 G5:0.5 F5:0.5 E5:1 G5:1 E5:1 C5:2 D5:1 F5:0.5 E5:0.5 D5:1 Bb4:1 A4:1 C#5:1 E5:1 A5:1")
    t = 0
    for rep in range(4):
        st = t
        for b in range(8):
            r, ch = prog[b % 4]
            bt = st + b * 4 * Q
            m = n2m(r + '2')
            notes = [n2m(c + '3') for c in ch]
            for k, o in enumerate((0, 1.5, 2, 3)):                       # strummed chords
                for j, nn in enumerate(notes + [notes[0] + 12]):
                    gtr.note(bt + int(o * Q) + j * 6, Q // 2, nn, 78 + (k == 0) * 14)
            bass.note(bt, Q + Q // 2, m, 104); bass.note(bt + Q + Q // 2, Q // 2, m + 7, 90); bass.note(bt + 2 * Q, Q * 2 - 8, m, 98)
            if rep >= 1:
                for k in range(8):
                    mar.note(bt + k * Q // 2, Q // 3, notes[(0, 2, 1, 2)[k % 4]] + 24, 70 + (k % 2 == 0) * 10)
            if b % 2 == 0:
                for c in ch:
                    pad_.note(bt, 8 * Q - 10, n2m(c + '4'), 50)
            if rep >= 1:
                d.note(bt + 2 * Q, Q // 8, 85, 70); d.note(bt + 2 * Q + Q // 4, Q // 8, 85, 60); d.note(bt + 3 * Q + Q // 2, Q // 8, 85, 74)
        jungle_drums(d, st, 8, Q, busy=1 if rep < 2 else 2)
        if rep >= 2:
            seq(flute, st, mel1 + ' ' + mel2, Q, 96, 0.9, transpose=12 if rep == 3 else 0)
        t = st + 32 * Q
    return write_midi('m_level18.mid', [gtr, mar, flute, bass, pad_, d], 104, end=t)


def m_level19():
    """The Fog: slow, heavy trip-hop in A minor - a lonely guitar arpeggio, a tolling bell, a music box that's out of
    tune with everything else."""
    Q = PPQ
    gtr = Track(0, 25, 88, 44, 90)
    pad_ = Track(1, 94, 70, 64, 120)
    bass = Track(2, 35, 104, 64, 40)
    bell = Track(3, 14, 80, 84, 120)
    box = Track(4, 10, 72, 90, 110)
    d = Track(9, None, 100, 64, 60)
    prog = [('A', ('A', 'C', 'E')), ('F', ('F', 'A', 'C')), ('D', ('D', 'F', 'A')), ('E', ('E', 'G#', 'B'))]
    tune = "E5:2 F5:1 E5:1 C5:4 D5:2 Bb4:2 B4:4 A4:2 C5:1 B4:1 G#4:4 A4:1 E5:1 Eb5:2 E5:4"
    t = 0
    for rep in range(4):
        st = t
        for b in range(8):
            r, ch = prog[b % 4]
            bt = st + b * 4 * Q
            m = n2m({'A': 'A1', 'F': 'F1', 'D': 'D2', 'E': 'E1'}[r])
            pat = [n2m(ch[0] + '3'), n2m(ch[2] + '3'), n2m(ch[0] + '4'), n2m(ch[1] + '4'), n2m(ch[2] + '4'), n2m(ch[1] + '4'),
                   n2m(ch[0] + '4'), n2m(ch[2] + '3')]
            if rep >= 1:
                for k in range(8):
                    gtr.note(bt + k * Q // 2, Q, pat[k], 64 + (k == 0) * 14)
            bass.note(bt, Q * 2 - 10, m + 12, 100); bass.note(bt + 2 * Q + Q // 2, Q, m + 12, 88)
            if b % 2 == 0:
                for c in ch:
                    pad_.note(bt, 8 * Q - 10, n2m(c + '3'), 56)
            if rep >= 2:
                d.note(bt, Q // 2, 36, 112); d.note(bt + Q * 3 // 2 + Q // 4, Q // 2, 36, 96)
                d.note(bt + Q, Q // 2, 38, 104); d.note(bt + 3 * Q, Q // 2, 38, 108)
                for k in range(8):
                    d.note(bt + k * Q // 2, Q // 8, 42, 38 + (k % 2) * 16)
                if b % 4 == 3:
                    d.note(bt + 3 * Q + Q // 2, Q // 4, 40, 90)
        bell.note(st, 4 * Q, n2m('A4'), 76); bell.note(st + 16 * Q, 4 * Q, n2m('Eb5'), 64)       # the tritone toll
        if rep == 3 or rep == 1:
            seq(box, st, tune, Q, 70, 0.95, transpose=12)
        t = st + 32 * Q
    return write_midi('m_level19.mid', [gtr, pad_, bass, bell, box, d], 76, end=t)


def m_boss5():
    """Xibalba: a war-drum ritual in E phrygian - taiko and toms, choir, distorted guitar riff, low brass and a death
    whistle (pan flute) shrieking over the top."""
    Q = PPQ
    gtr = Track(0, 30, 96, 44, 30)
    choir = Track(1, 52, 88, 64, 100)
    brass = Track(2, 58, 100, 70, 50)
    taiko = Track(3, 116, 112, 64, 50)
    whistle = Track(4, 75, 84, 84, 90)
    bass = Track(5, 33, 108, 64, 20)
    d = Track(9, None, 110, 64, 40)
    riff = [0, 0, 1, 0, 0, 3, 1, 0, 0, 0, 1, 0, 5, 3, 1, 0]
    roots = ['E2', 'E2', 'F2', 'E2', 'E2', 'E2', 'D2', 'F2']
    mel = ("E5:1 F5:1 G5:1 F5:0.5 E5:0.5 D5:2 E5:2 G5:1 A5:1 Bb5:1 A5:0.5 G5:0.5 F5:2 E5:2 "
           "B5:1 A5:0.5 G5:0.5 F5:1 E5:1 F5:1 G5:1 F5:2 E5:1 D5:1 E5:1 F5:1 E5:4")
    t = 0
    for rep in range(3):
        st = t
        for b, r in enumerate(roots):
            bt = st + b * 4 * Q
            m = n2m(r)
            for k, o in enumerate(riff):
                power(gtr, bt + k * Q // 4, Q // 4 - 4, m + 12 + o, 96 + (k % 4 == 0) * 10)
                if k % 2 == 0:
                    bass.note(bt + k * Q // 4, Q // 2 - 6, m + o, 106)
            for (o, n_, v) in ((0, 36, 116), (0.75, 36, 100), (1.5, 36, 108), (2, 36, 116), (2.5, 36, 100), (3, 36, 110)):
                d.note(bt + int(o * Q), Q // 4, n_, v)
            d.note(bt + Q, Q // 4, 38, 112); d.note(bt + 3 * Q, Q // 4, 38, 116)
            for k in range(8):
                d.note(bt + k * Q // 2, Q // 8, 46 if k % 2 else 42, 70)
            taiko.note(bt, Q, m + 12, 110); taiko.note(bt + Q + Q // 2, Q // 2, m + 12, 96); taiko.note(bt + 2 * Q, Q, m + 12, 104)
            if b % 4 == 3:
                for k, tom in enumerate((50, 48, 47, 45, 43, 41, 41, 41)):
                    d.note(bt + 2 * Q + k * Q // 4, Q // 4, tom, 96 + k * 3)
            if b % 2 == 0:
                choir.note(bt, 8 * Q - 10, m + 24, 80); choir.note(bt, 8 * Q - 10, m + 31, 74)
            if rep >= 1 and b % 2 == 1:
                brass.note(bt + 2 * Q, 2 * Q, m + 12, 100); brass.note(bt + 2 * Q, 2 * Q, m + 19, 92)
        if rep >= 1:
            seq(whistle if rep == 2 else brass, st, mel, Q, 104, 0.9, transpose=0 if rep == 2 else -12)
        if rep == 2:
            for k in range(4):                                       # the death whistle
                whistle.note(st + (k * 8 + 7) * Q, Q, n2m('E7'), 70)
        d.note(st, Q, 49, 120)
        t = st + 32 * Q
    return write_midi('m_boss5.mid', [gtr, choir, brass, taiko, whistle, bass, d], 150, end=t)


MUSIC = [m_level17, m_level18, m_level19, m_boss5]

# ================================================================== sounds.txt (every key)

SOUNDS_TXT = A3.SOUNDS_TXT.replace('''music.level16 = /snd/m_boss4.mid''', '''music.level16 = /snd/m_boss4.mid
music.level17 = /snd/m_level17.mid
music.level18 = /snd/m_level18.mid
music.level19 = /snd/m_level19.mid
music.level20 = /snd/m_boss5.mid''').replace('''sfx.stomp     = /snd/s_stomp.wav''', '''sfx.stomp     = /snd/s_stomp.wav
sfx.boulder   = /snd/s_boulder.wav
sfx.darts     = /snd/s_darts.wav
sfx.musket    = /snd/s_musket.wav
sfx.roar      = /snd/s_roar.wav
sfx.mummy     = /snd/s_mummy.wav
sfx.wail      = /snd/s_wail.wav
sfx.siren     = /snd/s_siren.wav
sfx.static    = /snd/s_static.wav
sfx.spikes    = /snd/s_spikes.wav
sfx.seven     = /snd/s_seven.wav
sfx.fall      = /snd/s_fall.wav
sfx.conq      = /snd/s_conq.wav''').replace('''voice.shift   = /snd/v_shift.wav''', '''voice.shift   = /snd/v_shift.wav
voice.start6  = /snd/v_start6.wav
voice.boss5   = /snd/v_boss5.wav
voice.win5    = /snd/v_win5.wav
voice.kmummy  = /snd/v_kmummy.wav
voice.kjag    = /snd/v_kjag.wav
voice.kconq   = /snd/v_kconq.wav
voice.kweep   = /snd/v_kweep.wav
voice.pit     = /snd/v_pit.wav
voice.idol    = /snd/v_idol.wav
voice.radio   = /snd/v_radio.wav
voice.other   = /snd/v_other.wav
voice.rise    = /snd/v_rise.wav''').replace('''voice.c4g     = /snd/v_c4g.wav''', '''voice.c4g     = /snd/v_c4g.wav
voice.c5a     = /snd/v_c5a.wav
voice.c5b     = /snd/v_c5b.wav
voice.c5c     = /snd/v_c5c.wav
voice.c5d     = /snd/v_c5d.wav
voice.c5e     = /snd/v_c5e.wav
voice.c5f     = /snd/v_c5f.wav
voice.c5g     = /snd/v_c5g.wav''').replace('''voice.g4b     = /snd/v_g4b.wav''', '''voice.g4b     = /snd/v_g4b.wav
voice.g5a     = /snd/v_g5a.wav
voice.g5b     = /snd/v_g5b.wav''')

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
        s = sfx4()
        print('sfx total', sum(s.values()), s)
    with open(os.path.join(A.OUT, 'sounds.txt'), 'w') as f:
        f.write(SOUNDS_TXT)
    if 'music' in what:
        import thin_midi                 # the busiest tracks, lighter for the phone (see thin_midi.py)
        thin_midi.main(thin_midi.DEFAULT)
    for k in ('music.level20', 'sfx.conq', 'voice.rise', 'voice.c5f', 'voice.g5b', 'sfx.stomp', 'voice.g4b'):
        assert k in SOUNDS_TXT, k
