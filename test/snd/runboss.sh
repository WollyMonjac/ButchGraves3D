#!/bin/sh
# Usage: test/snd/runboss.sh [path/to/Snd.java] [models...]   (a minute of boss fight; see BossTest)
cd "$(dirname "$0")"
J=/home/claude/tc/jdk8u422-b05/bin
SRC=${1:-../../src/Snd.java}
[ $# -gt 0 ] && shift
MODELS=${*:-N Y YK P C S}
rm -rf cls && mkdir cls
$J/javac -nowarn -d cls -cp /home/claude/tc/midp20_cldc11.jar fake/javax/microedition/media/*.java G.java W.java BossTest.java "$SRC" 2>&1 | grep -v "Picked up\|^Note" || true
for m in $MODELS; do
  timeout 120 $J/java $JOPT -cp cls:/home/claude/tc/midp20_cldc11.jar BossTest $m 2>&1 | grep -v "Picked up"
done
