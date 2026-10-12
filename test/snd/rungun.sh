#!/bin/sh
# Usage: test/snd/rungun.sh [path/to/Snd.java] [models...]
cd "$(dirname "$0")"
J=/home/claude/tc/jdk8u422-b05/bin
SRC=${1:-../../src/Snd.java}
[ $# -gt 0 ] && shift
MODELS=${*:-N R M C S RS RC}
rm -rf cls && mkdir cls
$J/javac -nowarn -d cls -cp /home/claude/tc/midp20_cldc11.jar fake/javax/microedition/media/*.java G.java W.java GunTest.java "$SRC" 2>&1 | grep -v "Picked up" || true
for m in $MODELS; do
  timeout 60 $J/java -cp cls:/home/claude/tc/midp20_cldc11.jar GunTest $m 2>&1 | grep -v "Picked up"
done
