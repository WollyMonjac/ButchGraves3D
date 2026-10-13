"""Re-pack a JAR as small as plain deflate allows: every entry is compressed with Zopfli (a slower, better deflate
encoder; any phone's unzip reads it) or stored, whichever is smaller. Entry order (manifest first) and contents stay
the same. Needs `pip install zopfli`; without it the JAR is left alone.
Usage: python3 tools/zipmax.py file.jar"""
import struct, sys, zipfile, zlib

try:
    from zopfli.zopfli import compress as zop
except ImportError:
    print('zipmax: zopfli not installed, JAR left as it is')
    sys.exit(0)

path = sys.argv[1]
src = zipfile.ZipFile(path)
entries = [(i, src.read(i.filename)) for i in src.infolist()]
src.close()
out, central = bytearray(), bytearray()
for info, data in entries:
    name = info.filename.encode('utf-8')
    crc = zlib.crc32(data) & 0xffffffff
    method, body = 0, data
    if data:
        d = zop(data, numiterations=15)[2:-4]          # zlib container -> raw deflate
        if len(d) < len(data):
            method, body = 8, d
    y, mo, dd, h, mi, s = info.date_time
    dtime, ddate = (h << 11) | (mi << 5) | (s // 2), ((y - 1980) << 9) | (mo << 5) | dd
    off = len(out)
    out += struct.pack('<IHHHHHIIIHH', 0x04034b50, 20, 0, method, dtime, ddate, crc, len(body), len(data), len(name), 0)
    out += name + body
    central += struct.pack('<IHHHHHHIIIHHHHHII', 0x02014b50, 20, 20, 0, method, dtime, ddate, crc, len(body), len(data),
                           len(name), 0, 0, 0, 0, 0, off) + name
cd = len(out)
out += central
out += struct.pack('<IHHHHIIH', 0x06054b50, 0, 0, len(entries), len(entries), len(central), cd, 0)
before = sum(1 for _ in [0]) and None
old = open(path, 'rb').read()
if len(out) < len(old):
    # check it reads back the same before replacing the JAR
    import io
    z = zipfile.ZipFile(io.BytesIO(bytes(out)))
    assert z.testzip() is None
    assert [i.filename for i in z.infolist()] == [i.filename for i, _ in entries]
    for i, data in entries:
        assert z.read(i.filename) == data
    open(path, 'wb').write(out)
    print('zipmax: %d -> %d bytes' % (len(old), len(out)))
else:
    print('zipmax: no gain, JAR left as it is')
