#!/bin/sh
# Build BUTCH GRAVES 3D: compile (Java 1.3 bytecode), package, shrink + preverify with ProGuard, write JAD.
set -e
cd "$(dirname "$0")"
TC=${TC:-/home/claude/tc}
J8=$TC/jdk8u422-b05/bin
API=$TC/midp20_cldc10.jar
VER=1.0.0
NAME=ButchGraves3D
RESDIR=res
if [ "$LITE" = "1" ]; then
  NAME=ButchGraves3D_lite
  rm -rf build_lite_res && cp -r res build_lite_res && rm -f build_lite_res/snd/v_*.wav
  sed -i "s#^voice\.\([a-z0-9]*\) *=.*#voice.\1 =#" build_lite_res/snd/sounds.txt
  RESDIR=build_lite_res
fi
export JAVA_TOOL_OPTIONS=
rm -rf build && mkdir -p build/cls dist
"$J8/javac" -nowarn -source 1.3 -target 1.3 -bootclasspath "$API" -d build/cls src/*.java
cat > build/MANIFEST.MF <<MF
Manifest-Version: 1.0
MIDlet-1: Butch Graves 3D,/icon.png,BG
MIDlet-Name: Butch Graves 3D
MIDlet-Vendor: Butch Graves Team
MIDlet-Version: $VER
MIDlet-Icon: /icon.png
MIDlet-Description: Halloween FPS - Night of the Pumpkin King
MicroEdition-Configuration: CLDC-1.0
MicroEdition-Profile: MIDP-2.0
Nokia-MIDlet-Category: Game
MF
"$J8/jar" cfm build/in.jar build/MANIFEST.MF -C build/cls . -C $RESDIR .
cat > build/pg.pro <<PG
-injars $PWD/build/in.jar
-outjars $PWD/dist/$NAME.jar
-libraryjars $API
-microedition
-overloadaggressively
-repackageclasses ''
-allowaccessmodification
-optimizationpasses 3
-dontnote
-keep public class BG
PG
"$J8/java" -jar "$TC/proguard-7.4.2/lib/proguard.jar" @build/pg.pro > build/proguard.log 2>&1 || { cat build/proguard.log; exit 1; }
SIZE=$(wc -c < dist/$NAME.jar | tr -d ' ')
cat > dist/$NAME.jad <<JAD
MIDlet-1: Butch Graves 3D,/icon.png,BG
MIDlet-Name: Butch Graves 3D
MIDlet-Vendor: Butch Graves Team
MIDlet-Version: $VER
MIDlet-Icon: /icon.png
MIDlet-Description: Halloween FPS - Night of the Pumpkin King
MIDlet-Jar-URL: $NAME.jar
MIDlet-Jar-Size: $SIZE
MicroEdition-Configuration: CLDC-1.0
MicroEdition-Profile: MIDP-2.0
Nokia-MIDlet-Category: Game
JAD
rm -rf build_lite_res
echo "built dist/$NAME.jar ($SIZE bytes)"
