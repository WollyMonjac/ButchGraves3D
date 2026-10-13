#!/bin/sh
# Build BUTCH GRAVES 3D: compile (Java 1.3 bytecode), package, shrink + preverify with ProGuard, write JAD.
set -e
cd "$(dirname "$0")"
TC=${TC:-/home/claude/tc}
J8=$TC/jdk8u422-b05/bin
API=$TC/midp20_cldc10.jar
VER=2.3.0
NAME=ButchGraves3D
RESDIR=res
if [ "$LITE" = "1" ]; then
  NAME=ButchGraves3D_lite
  rm -rf build_lite_res && cp -r res build_lite_res && rm -f build_lite_res/snd/v_*.wav
  sed -i "s#^voice\.\([a-z0-9]*\) *=.*#voice.\1 =#" build_lite_res/snd/sounds.txt
  RESDIR=build_lite_res
fi
export JAVA_TOOL_OPTIONS=
rm -rf build && mkdir -p build/cls build/stub dist
# vendor APIs the phone may provide (Nokia UI: backlight): compiled against stubs, never packaged
"$J8/javac" -nowarn -source 1.3 -target 1.3 -bootclasspath "$API" -d build/stub stubs/com/nokia/mid/ui/*.java
"$J8/jar" cf build/stub.jar -C build/stub .
"$J8/javac" -nowarn -source 1.3 -target 1.3 -bootclasspath "$API:build/stub.jar" -d build/cls src/*.java
cat > build/MANIFEST.MF <<MF
Manifest-Version: 1.0
MIDlet-1: Butch Graves 3D,/icon.png,BG
MIDlet-Name: Butch Graves 3D
MIDlet-Vendor: Butch Graves Team
MIDlet-Version: $VER
MIDlet-Icon: /icon.png
MIDlet-Description: Halloween FPS - The Halloween Saga
MicroEdition-Configuration: CLDC-1.0
MicroEdition-Profile: MIDP-2.0
Nokia-MIDlet-Category: Game
MF
"$J8/jar" cfm build/in.jar build/MANIFEST.MF -C build/cls . -C $RESDIR .
cat > build/pg.pro <<PG
-injars $PWD/build/in.jar
-outjars $PWD/dist/$NAME.jar
-libraryjars $API
-libraryjars $PWD/build/stub.jar
-microedition
-overloadaggressively
-repackageclasses ''
-allowaccessmodification
-optimizationpasses 3
-dontnote
-keep public class BG
# the only class that touches the Nokia UI API must stay a class of its own (not merged or inlined into the
# game canvas), or phones without that API would fail to load the game
-keep,allowobfuscation class NL { static void lights(); }
PG
"$J8/java" -jar "$TC/proguard-7.4.2/lib/proguard.jar" @build/pg.pro > build/proguard.log 2>&1 || { cat build/proguard.log; exit 1; }
# re-pack with Zopfli (plain deflate, about 5% smaller; skipped if python3 or the zopfli module is missing)
python3 tools/zipmax.py dist/$NAME.jar || true
SIZE=$(wc -c < dist/$NAME.jar | tr -d ' ')
if [ "$LITE" = "1" ] && [ "$SIZE" -gt 1048576 ]; then echo "lite JAR is over 1 MB ($SIZE bytes): many phones refuse it" >&2; exit 1; fi
cat > dist/$NAME.jad <<JAD
MIDlet-1: Butch Graves 3D,/icon.png,BG
MIDlet-Name: Butch Graves 3D
MIDlet-Vendor: Butch Graves Team
MIDlet-Version: $VER
MIDlet-Icon: /icon.png
MIDlet-Description: Halloween FPS - The Halloween Saga
MIDlet-Jar-URL: $NAME.jar
MIDlet-Jar-Size: $SIZE
MicroEdition-Configuration: CLDC-1.0
MicroEdition-Profile: MIDP-2.0
Nokia-MIDlet-Category: Game
JAD
rm -rf build_lite_res
echo "built dist/$NAME.jar ($SIZE bytes)"
