#!/usr/bin/env python3
"""Thin out the busiest music tracks so phones have CPU to spare for the sound effects during boss fights.

A phone plays the MIDI music and mixes the WAV effects on the same small chip. The boss tracks were 3-4 times busier than
the level tracks (double-kick 16ths, three-note power chords, choirs and brass on top), and boss fights are also where the
most effects play at once, which is where phones' audio got into trouble. This keeps every part and every melody but:
  - a chord struck on an instrument keeps its two lowest notes (a power chord loses its octave, which the bass already plays),
  - the kick drum and the hi-hats play on eighth notes, not sixteenths (fills and snares stay as they were),
  - an instrument that strikes more than three times a beat (a sixteenth-note riff) plays it in eighths.
Usage: python3 thin_midi.py [files...]   (default: the boss tracks and the busiest level tracks, in res/snd)"""
import os, sys, struct

HERE = os.path.dirname(os.path.abspath(__file__))
SND = os.path.join(HERE, '..', 'res', 'snd')
# (not m_boss.mid: the Pumpkin King's track plays in full, as it did in the first version - it lost too much)
DEFAULT = ['m_boss2.mid', 'm_boss3.mid', 'm_boss4.mid', 'm_boss5.mid', 'm_level17.mid', 'm_level18.mid',
           'm_level1.mid', 'm_win.mid']
KICKS_HATS = {35, 36, 42, 44, 46, 69, 70, 82}     # kicks, hi-hats, cabasa, maracas, shaker


def vlq_read(d, i):
    v = 0
    while True:
        b = d[i]; i += 1
        v = (v << 7) | (b & 127)
        if b < 128:
            return v, i


def vlq(n):
    b = [n & 0x7f]; n >>= 7
    while n:
        b.append((n & 0x7f) | 0x80); n >>= 7
    return bytes(reversed(b))


def parse(data):
    ntr, ppq = struct.unpack('>HH', data[10:14])
    pos, tracks = 14, []
    for _ in range(ntr):
        ln = struct.unpack('>I', data[pos + 4:pos + 8])[0]
        tr = data[pos + 8:pos + 8 + ln]
        pos += 8 + ln
        ev, i, t, run = [], 0, 0, 0
        while i < len(tr):
            dt, i = vlq_read(tr, i)
            t += dt
            st = tr[i]
            if st == 0xff:
                ml, j = vlq_read(tr, i + 2)
                ev.append((t, tr[i:j + ml])); i = j + ml; continue
            if st & 0x80:
                run = st; i += 1
            n = 1 if (run & 0xf0) in (0xc0, 0xd0) else 2
            ev.append((t, bytes([run]) + tr[i:i + n])); i += n
        tracks.append(ev)
    return data[:14], ppq, tracks


def thin(ev, ppq):
    """Drop note pairs (on + its off) per the rules above."""
    keep = [True] * len(ev)
    by_tick = {}
    span = max([t for t, b in ev] + [1])
    last = {}
    for k, (t, b) in enumerate(ev):
        if len(b) == 3 and (b[0] & 0xf0) == 0x90 and b[2] > 0:
            ch = b[0] & 15
            t0 = last.get(ch, -999)
            if ch != 9 and 0 < t - t0 <= ppq // 12:      # a strummed chord: its notes a few ticks apart count as one
                t = t0
            last[ch] = t
            by_tick.setdefault((t, ch), []).append(k)
    busy = len(by_tick) * ppq / span > 3.0       # an instrument striking more than 3 times a beat (a 16th-note riff)
    drop_on = set()
    for (t, ch), ks in by_tick.items():
        off16 = t % (ppq // 2) != 0
        if ch == 9:
            for k in ks:
                if ev[k][1][1] in KICKS_HATS and off16:
                    drop_on.add(k)
        else:
            if busy and off16 and t % (ppq // 4) == 0:
                drop_on.update(ks)                 # ...plays its riff in eighths
                continue
            if len(ks) > 2:
                ks = sorted(ks, key=lambda k: ev[k][1][1])
                drop_on.update(ks[2:])
    # drop the matching note-offs too
    pending = {}
    for k, (t, b) in enumerate(ev):
        if len(b) == 3 and (b[0] & 0xf0) in (0x80, 0x90):
            key = (b[0] & 15, b[1])
            is_on = (b[0] & 0xf0) == 0x90 and b[2] > 0
            if is_on:
                pending.setdefault(key, []).append(k)
                if k in drop_on:
                    keep[k] = False
            else:
                lst = pending.get(key)
                if lst:
                    on = lst.pop(0)
                    if not keep[on]:
                        keep[k] = False
    return [e for e, kp in zip(ev, keep) if kp]


def write(head, tracks):
    out = bytearray(head)
    for ev in tracks:
        body, last = bytearray(), 0
        for t, b in ev:
            body += vlq(t - last) + b
            last = t
        out += b'MTrk' + struct.pack('>I', len(body)) + body
    return bytes(out)


def notes(tracks):
    return sum(1 for ev in tracks for t, b in ev if len(b) == 3 and (b[0] & 0xf0) == 0x90 and b[2] > 0)


def main(files):
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(SND, f)
        head, ppq, tracks = parse(open(p, 'rb').read())
        n0 = notes(tracks)
        tracks = [thin(ev, ppq) for ev in tracks]
        n1 = notes(tracks)
        open(p, 'wb').write(write(head, tracks))
        print('%-14s notes %5d -> %5d' % (os.path.basename(p), n0, n1))


if __name__ == '__main__':
    main(sys.argv[1:] or DEFAULT)
