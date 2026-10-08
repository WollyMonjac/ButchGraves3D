#!/bin/sh
# usage: run.sh script.txt outdir W H
SCRIPT=$1; OUT=$2; W=${3:-240}; H=${4:-320}
rm -rf $OUT; mkdir -p $OUT
sed "s#@OUT#$OUT#g" $SCRIPT > $OUT/_script.txt
cd /home/claude/tc/harness
JAVA_TOOL_OPTIONS= timeout 180 /home/claude/tc/jdk8u422-b05/bin/java -Djava.awt.headless=true -cp /home/claude/tc/freej2me/freej2me-lib.jar:. Harness /home/claude/bg/dist/ButchGraves3D.jar $W $H $OUT/_script.txt 2>&1 | grep -v -E "Picked up|MIDlet-1|Create" | tail -8
python3 - "$OUT" "$W" "$H" <<'PY'
import sys, glob
from PIL import Image
out, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
fs = sorted(glob.glob(out + '/*.png'))
if not fs: sys.exit()
cols = 5
rows = (len(fs) + cols - 1) // cols
sh = Image.new('RGB', (cols * (w + 4), rows * (h + 4)), (0, 0, 0))
for k, f in enumerate(fs):
    sh.paste(Image.open(f), ((k % cols) * (w + 4), (k // cols) * (h + 4)))
sh.save(out + '_sheet.png')
PY
