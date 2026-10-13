#!/bin/sh
# Usage: test/snd/runexplore.sh [path/to/Snd.java] [models...]   (a minute of an ordinary level; see ExploreTest)
# JOPT=-Dturns: the player chose FX + MUSIC: TAKE TURNS
cd "$(dirname "$0")"
J=/home/claude/tc/jdk8u422-b05/bin
SRC=${1:-../../src/Snd.java}
[ $# -gt 0 ] && shift
MODELS=${*:-N X O U XT}
rm -rf cls && mkdir cls
$J/javac -nowarn -d cls -cp /home/claude/tc/midp20_cldc11.jar fake/javax/microedition/media/*.java G.java W.java BossTest.java ExploreTest.java "$SRC" 2>&1 | grep -v "Picked up\|^Note" || true
for m in $MODELS; do
  timeout 120 $J/java $JOPT -cp cls:/home/claude/tc/midp20_cldc11.jar ExploreTest $m 2>&1 | grep -v "Picked up"
done
