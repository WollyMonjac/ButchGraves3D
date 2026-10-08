#!/usr/bin/env python3
"""Voice lines (espeak-ng + MBROLA), synthesized SFX and General-MIDI music for Butch Graves 3D.
Writes res/snd/*. Everything here is original or public domain (Bach, BWV 565 opening)."""
import os, sys, struct, wave, subprocess, tempfile
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'res', 'snd')
SR = 8000
rng = np.random.RandomState(1)

# ================================================================== helpers


def save_wav(name, x, gain=0.92, sr=SR):
    x = np.asarray(x, float)
    m = np.max(np.abs(x)) + 1e-9
    x = x / m * gain
    f = min(len(x), 60)
    x[-f:] *= np.linspace(1, 0, f)
    pcm = np.clip(np.round(x * 127 + 128), 0, 255).astype(np.uint8)
    path = os.path.join(OUT, name)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(1); w.setframerate(sr); w.writeframes(pcm.tobytes())
    return os.path.getsize(path)


def secs(s):
    return int(s * SR)


def env(n, a=0.003, d=0.1, curve=4.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    return e * np.exp(-np.maximum(0, t - a) * curve / max(d, 1e-4))


def noise(n):
    return rng.uniform(-1, 1, n)


def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y


def highpass(x, a):
    return x - lowpass(x, a)


def tone(freq, n, kind='sin'):
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, float)
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == 'sin':
        return np.sin(ph)
    if kind == 'saw':
        return 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    if kind == 'sq':
        return np.sign(np.sin(ph))
    if kind == 'tri':
        return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1.0) - 1) - 1


def reverb(x, delays=(0.031, 0.047, 0.071, 0.113), fb=0.35, mix=0.35):
    y = x.copy()
    for d in delays:
        k = secs(d)
        buf = np.zeros(len(x) + k * 6)
        buf[:len(x)] += x
        for r in range(1, 6):
            buf[k * r:k * r + len(x)] += x * (fb ** r)
        y = y + buf[:len(x)] * mix / len(delays)
    return y


def pad(x, s):
    return np.concatenate([x, np.zeros(secs(s))])


def dist(x, drive=3.0):
    return np.tanh(x * drive) / np.tanh(drive)

# ================================================================== voice


VOICE = [
    # id, text, espeak voice, speed, pitch, post-pitch factor
    ('v_start1', "Trick or treat. I'm the trick.", 'mb-us2', 140, 28, 0.9),
    ('v_start2', "Graveyard shift just started.", 'mb-us2', 140, 28, 0.9),
    ('v_kill1', "Rest in pieces.", 'mb-us2', 135, 26, 0.9),
    ('v_kill2', "Back in the ground, ugly.", 'mb-us2', 145, 26, 0.9),
    ('v_kill3', "Stay dead this time.", 'mb-us2', 140, 26, 0.9),
    ('v_ghost', "Boo yourself.", 'mb-us2', 135, 30, 0.9),
    ('v_pumpkin', "Pumpkin pie, anyone?", 'mb-us2', 150, 32, 0.9),
    ('v_shovel', "Dig that!", 'mb-us2', 140, 30, 0.9),
    ('v_gib', "Who ordered extra crispy?", 'mb-us2', 150, 30, 0.9),
    ('v_weapon', "Come to papa.", 'mb-us2', 130, 26, 0.9),
    ('v_launcher', "Now that's a jack-o-lantern.", 'mb-us2', 145, 30, 0.9),
    ('v_health', "Sweet, sweet candy.", 'mb-us2', 135, 30, 0.9),
    ('v_lowhp', "I need candy. Lots of candy.", 'mb-us2', 145, 30, 0.9),
    ('v_secret', "Ooh. Secret stash.", 'mb-us2', 140, 34, 0.9),
    ('v_boss', "Your reign is over, gourd boy.", 'mb-us2', 140, 26, 0.88),
    ('v_win', "Happy Halloween.", 'mb-us2', 125, 26, 0.88),
    ('v_level', "Too easy.", 'mb-us2', 130, 26, 0.9),
    ('v_pain1', "Ugh!", 'mb-us2', 160, 30, 0.9),
    ('v_pain2', "Argh!", 'mb-us2', 160, 34, 0.9),
    ('v_die', "Noooo!", 'mb-us2', 110, 30, 0.85),
]


def voice(vid, text, v, speed, pitch, pf):
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, 'r.wav')
        subprocess.run(['espeak-ng', '-v', v, '-s', str(speed), '-p', str(pitch), '-g', '2', text, '-w', raw], check=True,
                       stderr=subprocess.DEVNULL)
        out = os.path.join(td, 'o.wav')
        sr_in = 16000
        flt = ('silenceremove=start_periods=1:start_threshold=-42dB:stop_periods=-1:stop_duration=0.25:stop_threshold=-42dB,'
               'asetrate=%d,aresample=16000,atempo=%.3f,highpass=f=110,lowpass=f=3600,'
               'acompressor=threshold=-22dB:ratio=5:attack=4:release=80:makeup=7,'
               'aecho=0.85:0.5:24:0.16,volume=1.4,'
               'silenceremove=stop_periods=-1:stop_duration=0.12:stop_threshold=-38dB' % (int(sr_in * pf), 1.12 / pf))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', flt, '-ar', str(SR), '-ac', '1', '-f', 'wav',
                        '-acodec', 'pcm_s16le', out], check=True)
        with wave.open(out) as w:
            d = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    d = dist(d * 1.4, 1.6)        # a little grit
    return save_wav(vid + '.wav', pad(d, 0.05), 0.95)


def monster_voice(vid, text, v, speed, pitch, pf, fx):
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, 'r.wav')
        subprocess.run(['espeak-ng', '-v', v, '-s', str(speed), '-p', str(pitch), text, '-w', raw], check=True,
                       stderr=subprocess.DEVNULL)
        out = os.path.join(td, 'o.wav')
        with wave.open(raw) as w:
            sr_in = w.getframerate()
        flt = ('silenceremove=start_periods=1:start_threshold=-40dB:stop_periods=-1:stop_duration=0.2:stop_threshold=-40dB,'
               'asetrate=%d,aresample=16000,%s' % (int(sr_in * pf), fx))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', flt, '-ar', str(SR), '-ac', '1', '-f', 'wav',
                        '-acodec', 'pcm_s16le', out], check=True)
        with wave.open(out) as w:
            d = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    return d

# ================================================================== SFX


def sfx():
    sz = {}
    t = lambda s: np.arange(secs(s)) / SR
    # revolver: crack + boomy tail
    n = secs(0.5)
    x = noise(n) * env(n, 0.001, 0.04, 5) * 1.5 + lowpass(noise(n), 0.12) * env(n, 0.001, 0.18, 4) * 2
    x += tone(np.linspace(180, 60, n), n) * env(n, 0.001, 0.08) * 0.8
    sz['s_revolver'] = save_wav('s_revolver.wav', dist(reverb(x, mix=0.5), 2.0))
    # shotgun: bigger, longer
    n = secs(0.75)
    x = noise(n) * env(n, 0.001, 0.06, 4) * 1.6 + lowpass(noise(n), 0.07) * env(n, 0.002, 0.3, 4) * 3
    x += tone(np.linspace(120, 40, n), n) * env(n, 0.001, 0.15) * 1.2
    sz['s_shotgun'] = save_wav('s_shotgun.wav', dist(reverb(x, mix=0.6, fb=0.4), 2.5))
    # reload (break-action click-clack)
    k1 = highpass(noise(secs(0.04)), 0.6) * env(secs(0.04), 0.001, 0.01)
    x = np.concatenate([k1, np.zeros(secs(0.12)), k1 * 0.8 + tone(1800, secs(0.04)) * env(secs(0.04), 0.001, 0.01) * 0.3,
                        np.zeros(secs(0.18)), k1 * 1.2])
    sz['s_reload'] = save_wav('s_reload.wav', x, 0.7)
    # tommy: short punchy
    n = secs(0.16)
    x = noise(n) * env(n, 0.001, 0.025, 5) * 1.4 + lowpass(noise(n), 0.15) * env(n, 0.001, 0.06) * 2
    sz['s_tommy'] = save_wav('s_tommy.wav', dist(x, 2.2), 0.85)
    # launcher: thump + whoosh
    n = secs(0.6)
    tt = np.arange(n) / SR
    x = tone(np.linspace(90, 45, n), n) * env(n, 0.001, 0.1) * 2 + lowpass(noise(n), 0.3) * np.exp(-((tt - 0.2) / 0.12) ** 2) * 1.2
    x += lowpass(noise(n), 0.08) * env(n, 0.001, 0.08) * 2
    sz['s_launch'] = save_wav('s_launch.wav', x, 0.9)
    # explosion
    n = secs(1.2)
    tt = np.arange(n) / SR
    x = lowpass(noise(n), 0.05) * np.exp(-tt * 2.8) * 4 + lowpass(noise(n), 0.4) * np.exp(-tt * 12) * 1.5
    x += tone(np.linspace(70, 28, n), n) * np.exp(-tt * 4) * 1.5
    sz['s_explode'] = save_wav('s_explode.wav', dist(reverb(x, mix=0.4), 2.5), 0.95)
    # shovel swing whoosh
    n = secs(0.3)
    tt = np.arange(n) / SR
    x = highpass(lowpass(noise(n), 0.35), 0.05) * np.exp(-((tt - 0.12) / 0.07) ** 2)
    sz['s_swing'] = save_wav('s_swing.wav', x, 0.7)
    # shovel hit: thunk + metallic ring
    n = secs(0.35)
    x = lowpass(noise(n), 0.2) * env(n, 0.001, 0.04) * 2 + tone(np.linspace(140, 80, n), n) * env(n, 0.001, 0.06) * 1.2
    for f, a in ((620, 0.5), (1170, 0.35), (1730, 0.25)):
        x += tone(f, n) * env(n, 0.001, 0.15) * a
    sz['s_hit'] = save_wav('s_hit.wav', x, 0.85)
    # creaky door: jittery sawtooth through formant-ish filter
    n = secs(0.9)
    tt = np.arange(n) / SR
    f0 = 70 + 40 * np.sin(tt * 3.0) + 25 * np.sin(tt * 17) + 15 * rng.uniform(-1, 1, n)
    src = tone(np.clip(f0, 30, 200), n, 'saw') * (0.6 + 0.4 * np.abs(np.sin(tt * 37)))
    x = lowpass(src, 0.35) - lowpass(src, 0.06) * 0.6
    x *= np.minimum(1, tt / 0.05) * np.minimum(1, (0.9 - tt) / 0.2)
    x += lowpass(noise(n), 0.05) * env(n, 0.75, 0.1) * 0.0
    sz['s_door'] = save_wav('s_door.wav', x, 0.75)
    # pickup bling
    n = secs(0.25)
    x = np.zeros(n)
    for f, d0 in ((988, 0.0), (1319, 0.05), (1976, 0.1)):
        o = secs(d0); m = n - o
        x[o:] += tone(f, m, 'tri') * env(m, 0.002, 0.08)
    sz['s_pickup'] = save_wav('s_pickup.wav', x, 0.6)
    # weapon pickup: cocking chk-chk
    k = lambda: highpass(noise(secs(0.05)), 0.5) * env(secs(0.05), 0.001, 0.012) + tone(900, secs(0.05), 'sq') * env(secs(0.05), 0.001, 0.01) * 0.3
    x = np.concatenate([k(), np.zeros(secs(0.09)), k() * 1.2, np.zeros(secs(0.05))])
    sz['s_wpick'] = save_wav('s_wpick.wav', x, 0.8)
    # key: eerie jingle
    n = secs(0.6)
    x = np.zeros(n)
    for f, d0 in ((1568, 0.0), (1865, 0.08), (2349, 0.16), (2093, 0.24)):
        o = secs(d0); m = n - o
        x[o:] += (tone(f, m) + 0.3 * tone(f * 2.7, m)) * env(m, 0.002, 0.2)
    sz['s_key'] = save_wav('s_key.wav', reverb(x), 0.6)
    # player hurt: low thud (voice lines play on top)
    n = secs(0.18)
    sz['s_hurt'] = save_wav('s_hurt.wav', lowpass(noise(n), 0.15) * env(n, 0.001, 0.05) + tone(90, n) * env(n, 0.001, 0.06), 0.7)
    # fireball whoosh
    n = secs(0.5)
    tt = np.arange(n) / SR
    x = lowpass(noise(n), 0.25) * np.minimum(1, tt / 0.05) * np.exp(-tt * 4) + lowpass(noise(n), 0.06) * env(n, 0.01, 0.2) * 1.5
    sz['s_fireball'] = save_wav('s_fireball.wav', x, 0.8)
    # monster death squelch
    n = secs(0.5)
    tt = np.arange(n) / SR
    x = lowpass(noise(n), 0.12) * (np.exp(-tt * 9) + 0.6 * np.exp(-np.abs(tt - 0.15) * 30)) * 2
    x += tone(np.linspace(220, 60, n), n, 'saw') * env(n, 0.01, 0.15) * 0.5
    sz['s_mdie'] = save_wav('s_mdie.wav', lowpass(x, 0.5), 0.85)
    # thunder
    n = secs(1.6)
    tt = np.arange(n) / SR
    x = lowpass(noise(n), 0.03) * (np.exp(-tt * 2.4) * 3 + 0.8 * np.exp(-np.abs(tt - 0.35) * 6))
    x += lowpass(noise(n), 0.25) * np.exp(-tt * 14) * 1.2
    sz['s_thunder'] = save_wav('s_thunder.wav', reverb(x, (0.05, 0.09, 0.13), 0.5, 0.5), 0.95)
    # click (menu / empty)
    n = secs(0.05)
    sz['s_click'] = save_wav('s_click.wav', tone(1400, n, 'sq') * env(n, 0.001, 0.015) + tone(700, n) * env(n, 0.001, 0.02), 0.5)
    # switch clunk
    n = secs(0.3)
    x = lowpass(noise(n), 0.3) * env(n, 0.001, 0.03) * 1.5 + tone(np.linspace(220, 90, n), n, 'sq') * env(n, 0.001, 0.08) * 0.5
    sz['s_switch'] = save_wav('s_switch.wav', x, 0.8)
    # secret: spooky rising chime
    n = secs(1.0)
    x = np.zeros(n)
    for i, f in enumerate((440, 554, 659, 880, 1109)):
        o = secs(i * 0.08); m = n - o
        x[o:] += tone(f, m, 'tri') * env(m, 0.003, 0.4) * (0.6 + 0.1 * i)
    sz['s_secret'] = save_wav('s_secret.wav', reverb(x, mix=0.5), 0.6)
    # monsters (voices processed into creatures)
    z = monster_voice('s_zombie', 'braaains', 'mb-us3', 75, 10, 0.62,
                      'tremolo=f=9:d=0.5,lowpass=f=2200,acompressor=threshold=-20dB:ratio=4:makeup=6,aecho=0.8:0.6:60:0.25')
    sz['s_zombie'] = save_wav('s_zombie.wav', dist(z * 1.5, 2.0), 0.9)
    z = monster_voice('s_scare', 'heh heh heh heh', 'en+m7', 170, 70, 0.8,
                      'flanger=delay=3:depth=4,lowpass=f=3000,aecho=0.8:0.5:40:0.2')
    sz['s_scare'] = save_wav('s_scare.wav', dist(z * 1.3, 2.0), 0.9)
    z = monster_voice('s_witch', 'hee hee hee hee hee', 'en+f4', 190, 95, 1.1,
                      'aecho=0.8:0.55:35|70:0.3|0.15,lowpass=f=3600')
    sz['s_witch'] = save_wav('s_witch.wav', z, 0.9)
    z = monster_voice('s_ghost', 'whooooooooo', 'en+f2', 60, 60, 1.0,
                      'vibrato=f=5:d=0.6,flanger=delay=5:depth=6,aecho=0.8:0.7:90|180:0.4|0.25,lowpass=f=2500')
    sz['s_ghost'] = save_wav('s_ghost.wav', z, 0.85)
    z = monster_voice('s_boss', 'ha ha ha', 'mb-us3', 120, 15, 0.55,
                      'lowpass=f=1800,acompressor=threshold=-20dB:ratio=4:makeup=8,aecho=0.8:0.6:70:0.3')
    sz['s_boss'] = save_wav('s_boss.wav', dist(z * 1.8, 2.5), 0.95)
    z = monster_voice('s_bossdie', 'noooooo', 'mb-us3', 90, 15, 0.5,
                      'lowpass=f=1600,acompressor=threshold=-20dB:ratio=4:makeup=8,aecho=0.8:0.8:90|200:0.45|0.3')
    sz['s_bossdie'] = save_wav('s_bossdie.wav', dist(z * 1.8, 2.5), 0.95)
    return sz

# ================================================================== MIDI

PPQ = 96
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def n2m(s):
    if s in ('r', 'R', '-'):
        return None
    k = NOTE[s[0]]; i = 1
    while i < len(s) and s[i] in '#b':
        k += 1 if s[i] == '#' else -1; i += 1
    return 12 * (int(s[i:]) + 1) + k


def vlq(n):
    b = [n & 0x7f]; n >>= 7
    while n:
        b.append((n & 0x7f) | 0x80); n >>= 7
    return bytes(reversed(b))


class Track:
    def __init__(self, ch, prog=None, vol=100, pan=64, rev=40):
        self.ch = ch
        self.ev = []
        if prog is not None:
            self.ev.append((0, 0, bytes([0xC0 | ch, prog])))
        self.ev.append((0, 0, bytes([0xB0 | ch, 7, vol])))
        self.ev.append((0, 0, bytes([0xB0 | ch, 10, pan])))
        self.ev.append((0, 0, bytes([0xB0 | ch, 91, rev])))

    def note(self, t, dur, n, vel=90):
        if n is None:
            return
        vel = max(1, min(127, int(vel)))
        self.ev.append((int(t), 2, bytes([0x90 | self.ch, n, vel])))
        self.ev.append((int(t + max(1, dur)), 1, bytes([0x80 | self.ch, n, 0])))

    def data(self):
        out = b''; last = 0
        for t, o, b in sorted(self.ev, key=lambda e: (e[0], e[1])):
            out += vlq(t - last) + b; last = t
        out += b'\x00\xff\x2f\x00'
        return b'MTrk' + struct.pack('>I', len(out)) + out


def write_midi(name, tracks, bpm, num=4, den=4, end=None):
    tempo = int(60000000 / bpm)
    t0 = b'\x00\xff\x51\x03' + struct.pack('>I', tempo)[1:]
    t0 += b'\x00\xff\x58\x04' + bytes([num, {2: 1, 4: 2, 8: 3}[den], 24, 8])
    if end is not None:
        # pad conductor track to the exact loop length so loops are seamless
        t0 += vlq(int(end)) + b'\xff\x2f\x00'
    else:
        t0 += b'\x00\xff\x2f\x00'
    data = b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks) + 1, PPQ)
    data += b'MTrk' + struct.pack('>I', len(t0)) + t0
    for tr in tracks:
        data += tr.data()
    with open(os.path.join(OUT, name), 'wb') as f:
        f.write(data)
    return len(data)


def seq(track, start, text, unit, vel=90, legato=0.9, accent=None, transpose=0):
    t = start
    rs = np.random.RandomState(len(text))
    for i, tok in enumerate(text.split()):
        nm, d = tok.split(':')
        d = float(d) * unit
        v = vel + rs.randint(-5, 6)
        if accent and i % accent == 0:
            v += 10
        for part in nm.split('+'):
            m = n2m(part)
            track.note(t, d * legato, None if m is None else m + transpose, v)
        t += d
    return t


def power(track, t, dur, root, vel=100, oct_=True):
    for k in (0, 7) + ((12,) if oct_ else ()):
        track.note(t, dur, root + k, vel - (k > 0) * 6)


def drums_rock(d, t0, bars, Q, fill=True, crash=True, variant=0):
    for b in range(bars):
        bt = t0 + b * 4 * Q
        if b == 0 and crash:
            d.note(bt, Q, 49, 110)
        for k in range(8):
            d.note(bt + k * Q // 2, Q // 4, 42, 70 + (k % 2 == 0) * 18)
        kicks = [0, 1.5, 2.5] if variant == 0 else [0, 0.5, 2, 2.75]
        for k in kicks:
            d.note(bt + int(k * Q), Q // 4, 36, 112)
        d.note(bt + Q, Q // 4, 38, 110)
        d.note(bt + 3 * Q, Q // 4, 38, 112)
        if fill and b == bars - 1:
            for k, n_ in enumerate((50, 50, 48, 48, 45, 45, 41, 41)):
                d.note(bt + 2 * Q + k * Q // 4, Q // 4, n_, 90 + k * 3)


# ------------------------------------------------------------------ title: Toccata (Bach) + dark groove

def m_title():
    Q = PPQ
    org = Track(0, 19, 110, 64, 80)     # church organ
    ped = Track(1, 19, 105, 64, 80)
    choir = Track(2, 52, 80, 64, 90)
    timp = Track(3, 47, 110, 64, 60)
    bells = Track(4, 14, 80, 80, 90)
    strings = Track(5, 48, 70, 50, 80)
    d = Track(9, None, 100, 64, 30)
    t = 0
    # BWV 565 opening (public domain): mordent and descent, three octaves
    for o in (5, 4, 3):
        a = n2m('A%d' % o)
        seq(org, t, 'A%d:0.125 G%d:0.125 A%d:1.75 r:0.5 G%d:0.25 F%d:0.25 E%d:0.25 D%d:0.25 C#%d:1 D%d:2.5 r:0.5' % ((o,) * 4 + (o,) * 5), Q, 108, 0.97)
        seq(org, t, 'A%d:0.125 G%d:0.125 A%d:1.75 r:0.5 G%d:0.25 F%d:0.25 E%d:0.25 D%d:0.25 C#%d:1 D%d:2.5 r:0.5' % ((o - 1,) * 4 + (o - 1,) * 5), Q, 100, 0.97)
        t += 7.5 * Q
    # low pedal D and rolled diminished seventh, resolving
    ped.note(t, 8 * Q, n2m('D2'), 110)
    ped.note(t, 8 * Q, n2m('D1'), 100)
    roll = ['C#3', 'E3', 'G3', 'Bb3', 'C#4', 'E4', 'G4', 'Bb4']
    for k, nm in enumerate(roll):
        org.note(t + k * Q // 4, 4 * Q - k * Q // 4, n2m(nm), 100)
    t += 4 * Q
    for nm in ('D3', 'F3', 'A3', 'D4', 'F4', 'A4', 'D5'):
        org.note(t, 4 * Q, n2m(nm), 110)
    timp.note(t, 2 * Q, n2m('D3'), 120)
    t += 4 * Q
    # original dark groove (8 bars x2): organ ostinato, choir, drums
    prog = ['Dm', 'Bb', 'Gm', 'A', 'Dm', 'Bb', 'Em7b5', 'A']
    CH = {'Dm': ('D', 'F', 'A'), 'Bb': ('Bb', 'D', 'F'), 'Gm': ('G', 'Bb', 'D'), 'A': ('A', 'C#', 'E'), 'Em7b5': ('E', 'G', 'Bb')}
    mel = ("D5:1.5 E5:0.5 F5:1 A5:1 G5:1.5 F5:0.5 E5:1 D5:1 Bb4:1.5 D5:0.5 G5:1 F5:1 E5:3 r:1 "
           "F5:1.5 G5:0.5 A5:1 D6:1 C6:1 Bb5:1 A5:1 G5:1 G5:1.5 F5:0.5 E5:1 D5:1 C#5:3 r:1")
    for rep in range(2):
        st = t
        if rep == 1:
            seq(bells, st, mel, Q, 84, 0.95)
        seq(choir if rep == 0 else strings, st, mel, Q, 76, 1.0, transpose=-12 if rep == 0 else 0)
        for b, ch in enumerate(prog):
            bt = st + b * 4 * Q
            notes = [n2m(x + '3') for x in CH[ch]]
            notes = [n if n >= notes[0] else n + 12 for n in notes]
            pat = [0, 1, 2, 1, 0, 1, 2, 1]
            for k, ix in enumerate(pat):
                org.note(bt + k * Q // 2, Q // 2, notes[ix] + 12, 80 + (k % 4 == 0) * 14)
            ped.note(bt, 4 * Q * 0.95, notes[0] - 12, 100)
            timp.note(bt, Q, notes[0] - 12 if notes[0] - 12 >= 38 else notes[0], 100)
            for k in range(4):
                d.note(bt + k * Q, Q // 4, 36 if k % 2 == 0 else 38, 90 if k % 2 == 0 else 80)
                d.note(bt + k * Q + Q // 2, Q // 4, 42, 50)
        t = st + 8 * 4 * Q
    return write_midi('m_title.mid', [org, ped, choir, timp, bells, strings, d], 92, end=t)


# ------------------------------------------------------------------ level 1: Graveyard Shift (E minor rock)

def m_level1():
    Q = PPQ
    gtr = Track(0, 30, 96, 44, 30)
    gtr2 = Track(1, 30, 80, 84, 30)
    bass = Track(2, 34, 104, 64, 20)
    lead = Track(3, 81, 92, 70, 50)
    organ = Track(4, 16, 76, 64, 60)
    bells = Track(5, 14, 76, 90, 90)
    choir = Track(6, 52, 70, 64, 90)
    d = Track(9, None, 110, 64, 30)
    E = n2m('E2')
    # 2-bar riff, roots in eighths (None = rest)
    riffA = ['E2', 'E2', 'r', 'E2', 'G2', 'r', 'E2', 'A2', 'E2', 'E2', 'r', 'E2', 'Bb2', 'r', 'A2', 'G2']
    riffB = ['C3', 'C3', 'r', 'C3', 'D3', 'r', 'C3', 'B2', 'A2', 'A2', 'r', 'A2', 'B2', 'r', 'C3', 'D3']

    def riff(t, r, vel=100, both=True):
        for k, nm in enumerate(r):
            if nm == 'r':
                continue
            m = n2m(nm)
            power(gtr, t + k * Q // 2, Q // 2 - 6, m, vel)
            if both:
                power(gtr2, t + k * Q // 2, Q // 2 - 6, m + 12, vel - 10, False)
            bass.note(t + k * Q // 2, Q // 2 - 8, m - 12, 105)
        return t + 8 * Q

    t = 0
    # intro: riff on guitar alone with hats, then full band
    for k in range(2):
        tt = riff(t, riffA, 92, False)
        for j in range(16):
            d.note(t + j * Q // 2, Q // 4, 42, 60 + (j % 2 == 0) * 15)
        t = tt
    # verse: riffA x4 with drums
    st = t
    for k in range(4):
        t = riff(t, riffA)
    drums_rock(d, st, 8, Q)
    seq(organ, st + 8 * Q, 'E4+G4+B4:0.5 r:3.5 E4+G4+B4:0.5 r:3.5 ' * 3, Q, 70)
    # chorus: riffB + lead melody
    st = t
    for k in range(4):
        t = riff(t, riffB if k % 2 == 0 else riffA)
    drums_rock(d, st, 8, Q, variant=1)
    leadm = ("E5:1 G5:0.5 A5:0.5 B5:1.5 A5:0.5 G5:1 F#5:1 E5:2 "
             "D5:1 E5:0.5 G5:0.5 A5:2 G5:1 F#5:1 E5:2 B4:2 "
             "C5:1 E5:0.5 G5:0.5 C6:1.5 B5:0.5 A5:1 G5:1 A5:2 "
             "B5:1 A5:0.5 G5:0.5 F#5:1 G5:0.5 F#5:0.5 E5:4")
    seq(lead, st, leadm, Q, 96, 0.92)
    # bridge: half time spooky (bells + choir over chugs)
    st = t
    for b in range(4):
        bt = st + b * 4 * Q
        for k in range(4):
            power(gtr, bt + k * Q, Q // 3, E, 96)
        bass.note(bt, 4 * Q * 0.9, E - 12, 100)
        d.note(bt, Q // 4, 36, 110); d.note(bt + 2 * Q, Q // 4, 38, 110)
        d.note(bt + Q * 3 + Q // 2, Q // 4, 36, 100)
        for k in range(4):
            d.note(bt + k * Q, Q // 4, 51, 70)
    seq(bells, st, 'E5:1 B4:1 Bb4:2 E5:1 B4:1 G4:2 E5:1 B4:1 Bb4:2 A4:1 G4:1 F#4:2', Q, 90, 0.95)
    seq(choir, st, 'E4+B4:4 E4+Bb4:4 E4+B4:4 D#4+A4:4', Q, 70, 1.0)
    t = st + 16 * Q
    # final verse with lead harmony
    st = t
    for k in range(4):
        t = riff(t, riffA)
    drums_rock(d, st, 8, Q)
    seq(lead, st, leadm, Q, 90, 0.92, transpose=-12)
    return write_midi('m_level1.mid', [gtr, gtr2, bass, lead, organ, bells, choir, d], 138, end=t)


# ------------------------------------------------------------------ level 2: Manor of Madness (waltz)

def m_level2():
    Q = PPQ
    hpsi = Track(0, 6, 92, 50, 60)
    mbox = Track(1, 10, 100, 80, 80)
    strings = Track(2, 48, 72, 64, 80)
    pizz = Track(3, 45, 96, 64, 50)
    timp = Track(4, 47, 100, 64, 50)
    choir = Track(5, 53, 64, 64, 90)
    d = Track(9, None, 80, 64, 40)
    prog = ['Dm', 'A7', 'Dm', 'Gm', 'Dm', 'Bb', 'Edim', 'A7']
    prog2 = ['Gm', 'Dm', 'A7', 'Dm', 'Gm', 'Dm', 'Edim', 'A7']
    CH = {'Dm': ('D', 'F', 'A'), 'A7': ('A', 'C#', 'G'), 'Gm': ('G', 'Bb', 'D'), 'Bb': ('Bb', 'D', 'F'), 'Edim': ('E', 'G', 'Bb')}
    melA = ("A5:2 D6:1 C#6:1.5 Bb5:0.5 A5:1 F5:2 E5:1 D5:3 "
            "A5:1 Bb5:1 C6:1 D6:2 Bb5:1 A5:1 G5:1 F5:1 "
            "E5:1.5 F5:0.5 G5:1 Bb5:2 G5:1 C#5:1.5 D5:0.5 E5:1 A4:3")
    melB = ("G5:2 Bb5:1 D6:2 C6:1 Bb5:1 A5:1 G5:1 F5:3 "
            "E5:1 F5:1 G5:1 A5:2 F5:1 D5:3 "
            "Bb4:1 C#5:1 E5:1 G5:2 Bb5:1 A5:3 A4:3")
    t = 0
    for sec, (pr, mel) in enumerate(((prog, melA), (prog2, melB), (prog, melA), (prog2, melB))):
        st = t
        seq(mbox if sec % 2 == 0 else strings, st, mel, Q, 96 if sec % 2 == 0 else 80, 0.95)
        if sec == 2:
            seq(choir, st, mel, Q, 60, 1.0, transpose=-12)
        for b, ch in enumerate(pr):
            bt = st + b * 3 * Q
            ns = [n2m(x + '3') for x in CH[ch]]
            ns = [n if n >= ns[0] else n + 12 for n in ns]
            pizz.note(bt, Q * 0.6, ns[0] - 12, 100)
            for k in (1, 2):
                for n in ns:
                    hpsi.note(bt + k * Q, Q * 0.7, n + 12, 70 + (k == 1) * 8)
            if sec >= 1:
                for n in ns:
                    strings.note(bt, 3 * Q * 0.95, n, 50) if sec % 2 == 0 else None
            if b % 4 == 3:
                for k in range(6):
                    timp.note(bt + k * Q // 2, Q // 2, n2m('A2'), 60 + k * 8)
            d.note(bt, Q // 4, 75, 60)   # claves tick
            d.note(bt + Q, Q // 4, 76, 40)
            d.note(bt + 2 * Q, Q // 4, 76, 40)
        t = st + len(pr) * 3 * Q
    return write_midi('m_level2.mid', [hpsi, mbox, strings, pizz, timp, choir, d], 108, 3, 4, end=t)


# ------------------------------------------------------------------ level 3: Bone Catacombs (slow, heavy)

def m_level3():
    Q = PPQ
    org = Track(0, 19, 90, 64, 90)
    gtr = Track(1, 30, 92, 50, 40)
    bass = Track(2, 38, 100, 64, 30)
    choir = Track(3, 52, 80, 64, 100)
    bells = Track(4, 14, 86, 80, 100)
    pad = Track(5, 89, 70, 64, 100)
    d = Track(9, None, 110, 64, 50)
    t = 0
    roots = ['C#2', 'C#2', 'D2', 'C#2', 'A1', 'G1', 'G#1', 'G#1']
    for sec in range(3):
        st = t
        for b, r in enumerate(roots):
            bt = st + b * 4 * Q
            m = n2m(r)
            org.note(bt, 4 * Q * 0.98, m + 12, 80)
            org.note(bt, 4 * Q * 0.98, m + 12 + 7 if b % 2 == 0 else m + 12 + 6, 72)   # fifth / tritone
            if sec >= 1:
                for k, dd in ((0, 1.5), (1.5, 0.5), (2, 1.5), (3.5, 0.5)):
                    power(gtr, bt + int(k * Q), int(dd * Q) - 8, m + 12, 96, False)
                bass.note(bt, 2 * Q, m, 100); bass.note(bt + 2 * Q, 2 * Q, m, 90)
                d.note(bt, Q // 4, 36, 115); d.note(bt + Q * 3 // 2, Q // 4, 36, 100)
                d.note(bt + 2 * Q, Q // 4, 38, 115)
                d.note(bt + 3 * Q, Q // 4, 41, 90); d.note(bt + 3 * Q + Q // 2, Q // 4, 43, 90)
                d.note(bt, Q // 4, 57 if b % 4 == 0 else 51, 80)
            else:
                pad.note(bt, 4 * Q, m + 24, 70)
                d.note(bt, Q // 2, 41, 70)
            if b % 2 == 0:
                bells.note(bt, 3 * Q, m + 36, 92)
                bells.note(bt + Q * 3 // 2, 2 * Q, m + 36 + 6, 70)
        cm = ("C#4:4 D4:2 C#4:2 B3:4 G#3:4 A3:4 G#3:2 F#3:2 G#3:8" if sec != 1 else
              "E4:2 F#4:2 G#4:4 A4:2 G#4:2 F#4:4 E4:4 D4:4 C#4:8")
        seq(choir, st, cm, Q, 80, 1.0)
        t = st + 8 * 4 * Q
    return write_midi('m_level3.mid', [org, gtr, bass, choir, bells, pad, d], 76, end=t)


# ------------------------------------------------------------------ boss: The Pumpkin King

def m_boss():
    Q = PPQ
    gtr = Track(0, 30, 100, 40, 30)
    gtr2 = Track(1, 29, 86, 88, 30)
    bass = Track(2, 34, 106, 64, 20)
    org = Track(3, 19, 88, 64, 70)
    choir = Track(4, 52, 84, 64, 90)
    lead = Track(5, 81, 90, 70, 50)
    timp = Track(6, 47, 110, 64, 50)
    d = Track(9, None, 115, 64, 30)
    t = 0
    pat = ['D2', 'D2', 'D2', 'D2', 'F2', 'D2', 'D2', 'Eb2', 'D2', 'D2', 'D2', 'D2', 'Ab2', 'G2', 'F2', 'Eb2']
    sections = [('intro', 2), ('A', 4), ('B', 4), ('A', 4), ('C', 4)]
    for sec, bars in sections:
        st = t
        for b in range(bars):
            bt = st + b * 4 * Q
            for k, nm in enumerate(pat):
                m = n2m(nm)
                if sec == 'B':
                    m += [0, 0, 5, 3][b % 4]
                vel = 104 if k % 4 == 0 else 90
                power(gtr, bt + k * Q // 4, Q // 4 - 4, m, vel, False)
                if sec != 'intro':
                    bass.note(bt + k * Q // 4, Q // 4 - 4, m - 12, 100)
            if sec != 'intro':
                for k in range(16):
                    d.note(bt + k * Q // 4, Q // 8, 36, 100 + (k % 4 == 0) * 15)
                d.note(bt + Q, Q // 4, 38, 120); d.note(bt + 3 * Q, Q // 4, 38, 120)
                for k in range(8):
                    d.note(bt + k * Q // 2, Q // 4, 42 if b % 2 else 51, 70)
                if b == 0:
                    d.note(bt, Q, 49, 120)
            else:
                timp.note(bt, Q, n2m('D2') + 12, 110); timp.note(bt + 2 * Q, Q, n2m('A2'), 100)
        if sec in ('A',):
            seq(choir, st, 'D4+A4:4 C4+G4:4 Bb3+F4:4 A3+E4:4 D4+A4:4 Eb4+Bb4:4 D4+A4:4 C#4+G#4:4', Q * 2 // 2, 86, 1.0)
            seq(org, st, 'D5:1 F5:1 A5:1 D6:1 C6:2 A5:2 Bb5:1 A5:1 G5:1 F5:1 E5:2 C#5:2 '
                         'D5:1 F5:1 A5:1 D6:1 Eb6:2 D6:2 C6:1 Bb5:1 A5:1 G5:1 A5:4', Q, 92, 0.95)
        if sec == 'B':
            seq(lead, st, 'A5:0.5 G5:0.5 F5:0.5 Eb5:0.5 D5:2 F5:1 Ab5:1 G5:2 F5:0.5 G5:0.5 Ab5:1 A5:4 '
                          'D6:0.5 C6:0.5 Bb5:0.5 A5:0.5 G5:2 Bb5:1 D6:1 C#6:2 A5:2 D6:4', Q, 100, 0.9)
            seq(gtr2, st, 'D4+A4:4 F4+C5:4 G4+D5:4 F4+C5:4', Q * 1, 86, 1.0)
        if sec == 'C':
            seq(choir, st, 'D4+F4+A4:4 Eb4+G4+Bb4:4 D4+F4+A4:4 C#4+E4+A4:4', Q, 96, 1.0)
            seq(timp, st, 'D3:1 D3:1 A2:1 A2:1 ' * 4, Q, 110)
        t = st + bars * 4 * Q
    return write_midi('m_boss.mid', [gtr, gtr2, bass, org, choir, lead, timp, d], 168, end=t)


# ------------------------------------------------------------------ story: creepy music-box lullaby

def m_story():
    Q = PPQ
    mb = Track(0, 10, 100, 64, 100)
    cel = Track(1, 8, 70, 50, 100)
    strings = Track(2, 49, 60, 64, 100)
    mel = ("E5:1 A5:1 C6:1 B5:2 A5:1 G#5:2 B5:1 E5:3 "
           "D5:1 F5:1 A5:1 G#5:2 F5:1 E5:3 r:3 "
           "E5:1 A5:1 C6:1 E6:2 D6:1 C6:1 B5:1 A5:1 "
           "G#5:1 B5:1 D6:1 C6:2 B5:1 A5:3 r:3")
    prog = ['Am', 'E', 'Dm', 'E', 'Am', 'C', 'E', 'Am']
    CH = {'Am': ('A', 'C', 'E'), 'E': ('E', 'G#', 'B'), 'Dm': ('D', 'F', 'A'), 'C': ('C', 'E', 'G')}
    t = 0
    for rep in range(2):
        st = t
        seq(mb, st, mel, Q, 92 - rep * 10, 0.95)
        if rep:
            seq(cel, st, mel, Q, 60, 0.9, transpose=-12)
        for b, ch in enumerate(prog):
            bt = st + b * 6 * Q
            ns = [n2m(x + '3') for x in CH[ch]]
            ns = [n if n >= ns[0] else n + 12 for n in ns]
            for n in ns:
                strings.note(bt, 6 * Q * 0.98, n, 54)
        t = st + 8 * 6 * Q
    return write_midi('m_story.mid', [mb, cel, strings], 84, 3, 4, end=t)


def m_win():
    Q = PPQ
    org = Track(0, 19, 110, 64, 90)
    tr = Track(1, 56, 104, 60, 60)
    choir = Track(2, 52, 90, 64, 90)
    timp = Track(3, 47, 110, 64, 60)
    seq(tr, 0, 'D5:0.5 D5:0.5 D5:0.5 A4:0.5 D5:1 F#5:1 A5:3 r:1 G5:0.5 F#5:0.5 E5:1 F#5:0.5 G5:0.5 A5:4', Q, 108)
    for (t, ch, d_) in ((0, ('D', 'F#', 'A'), 4), (4, ('G', 'B', 'D'), 2), (6, ('A', 'C#', 'E'), 2), (8, ('D', 'F#', 'A'), 4)):
        for nm in ch:
            org.note(t * Q, d_ * Q, n2m(nm + '4'), 96)
            choir.note(t * Q, d_ * Q, n2m(nm + '4'), 84)
        timp.note(t * Q, Q // 2, n2m('D3'), 120)
    for k in range(8):
        timp.note(10 * Q + k * Q // 4, Q // 4, n2m('D3'), 70 + k * 6)
    return write_midi('m_win.mid', [org, tr, choir, timp], 100, end=12 * Q)


def m_dead():
    Q = PPQ
    org = Track(0, 19, 100, 64, 100)
    choir = Track(1, 52, 84, 64, 100)
    seq(org, 0, 'D4+F4+A4:2 C#4+E4+G4:2 C4+Eb4+G4:2 B3+D4+F4:2 Bb3+D4+F4:4 A3+C#4+E4:4', Q, 96, 1.0)
    seq(choir, 0, 'A4:2 G4:2 G4:2 F4:2 F4:4 E4:4', Q, 80, 1.0)
    return write_midi('m_dead.mid', [org, choir], 70, end=16 * Q)


# ================================================================== config file

SOUNDS_TXT = """# BUTCH GRAVES 3D - sound configuration
# Format:  key = /path/in/jar.ext   (leave empty or delete a line to silence it)
# Supported types depend on the phone: .mid .wav .amr .mp3 (mime type from the extension).
# To use your own sounds: copy the files into the JAR (it's a ZIP, use 7-Zip/WinRAR),
# then point the keys below at them. If you install with the .jad, update its
# MIDlet-Jar-Size to the new JAR size (or install the .jar alone).

# ---- music (looped) ----
music.title   = /snd/m_title.mid
music.story   = /snd/m_story.mid
music.level1  = /snd/m_level1.mid
music.level2  = /snd/m_level2.mid
music.level3  = /snd/m_level3.mid
music.level4  = /snd/m_boss.mid
music.win     = /snd/m_win.mid
music.dead    = /snd/m_dead.mid

# ---- weapons ----
sfx.revolver  = /snd/s_revolver.wav
sfx.shotgun   = /snd/s_shotgun.wav
sfx.reload    = /snd/s_reload.wav
sfx.tommy     = /snd/s_tommy.wav
sfx.launch    = /snd/s_launch.wav
sfx.explode   = /snd/s_explode.wav
sfx.swing     = /snd/s_swing.wav
sfx.hit       = /snd/s_hit.wav

# ---- world ----
sfx.door      = /snd/s_door.wav
sfx.pickup    = /snd/s_pickup.wav
sfx.wpick     = /snd/s_wpick.wav
sfx.key       = /snd/s_key.wav
sfx.hurt      = /snd/s_hurt.wav
sfx.fireball  = /snd/s_fireball.wav
sfx.mdie      = /snd/s_mdie.wav
sfx.thunder   = /snd/s_thunder.wav
sfx.click     = /snd/s_click.wav
sfx.switch    = /snd/s_switch.wav
sfx.secret    = /snd/s_secret.wav

# ---- monsters ----
sfx.zombie    = /snd/s_zombie.wav
sfx.scare     = /snd/s_scare.wav
sfx.witch     = /snd/s_witch.wav
sfx.ghost     = /snd/s_ghost.wav
sfx.boss      = /snd/s_boss.wav
sfx.bossdie   = /snd/s_bossdie.wav

# ---- Butch's voice lines ----
voice.start1  = /snd/v_start1.wav
voice.start2  = /snd/v_start2.wav
voice.kill1   = /snd/v_kill1.wav
voice.kill2   = /snd/v_kill2.wav
voice.kill3   = /snd/v_kill3.wav
voice.ghost   = /snd/v_ghost.wav
voice.pumpkin = /snd/v_pumpkin.wav
voice.shovel  = /snd/v_shovel.wav
voice.gib     = /snd/v_gib.wav
voice.weapon  = /snd/v_weapon.wav
voice.launcher= /snd/v_launcher.wav
voice.health  = /snd/v_health.wav
voice.lowhp   = /snd/v_lowhp.wav
voice.secret  = /snd/v_secret.wav
voice.boss    = /snd/v_boss.wav
voice.win     = /snd/v_win.wav
voice.level   = /snd/v_level.wav
voice.pain1   = /snd/v_pain1.wav
voice.pain2   = /snd/v_pain2.wav
voice.die     = /snd/v_die.wav
"""

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    what = sys.argv[1:] or ['voice', 'sfx', 'music']
    if 'music' in what:
        for f in (m_title, m_level1, m_level2, m_level3, m_boss, m_story, m_win, m_dead):
            print(f.__name__, f(), 'bytes')
    if 'voice' in what:
        tot = 0
        for v in VOICE:
            tot += voice(*v)
        print('voice total', tot)
    if 'sfx' in what:
        s = sfx()
        print('sfx total', sum(s.values()))
    with open(os.path.join(OUT, 'sounds.txt'), 'w') as f:
        f.write(SOUNDS_TXT)
