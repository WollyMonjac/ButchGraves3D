#!/bin/sh
# Rebuild the desktop simulator from the game sources (stub G/Snd, real E/W/Res).
cd "$(dirname "$0")"
cp ../../src/E.java ../../src/W.java ../../src/Res.java .
python3 - <<'PY'
import re
src = open('../../src/Snd.java').read()
consts = re.findall(r'(static final int [A-Z_0-9 =,\n]+;)', src)
out = ['final class Snd {']
for c in consts:
    out.append('  ' + ' '.join(c.split()))
out += ['  static void music(int id) {}', '  static void sfx(int id) {}', '  static void sfxAt(int id, int x, int y) {}', '  static void voice(int id) {}', '  static void weapon(int id) {}', '}']
open('Snd.java', 'w').write('\n'.join(out) + '\n')
PY
rm -rf cls && mkdir cls
JAVA_TOOL_OPTIONS= /home/claude/tc/jdk8u422-b05/bin/javac -nowarn -cp /home/claude/tc/midp20_cldc11.jar -d cls *.java 2>&1 | grep -v "^Note\|Picked" || true
