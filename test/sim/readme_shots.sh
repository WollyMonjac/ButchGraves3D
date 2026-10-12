#!/bin/sh
# Re-shoot the README screenshots with the real engine (build the simulator first: sh build.sh).
# Show5/Showcase: level x y angle ticks weapon "type@dist,lateral,pose;..." out [clear]; hud.py adds the status bar.
cd "$(dirname "$0")"
J="env JAVA_TOOL_OPTIONS= /home/claude/tc/jdk8u422-b05/bin/java -cp cls:/home/claude/tc/midp20_cldc11.jar"
O=../../screenshots
T=${TMPDIR:-/tmp}
$J Show5 4 19.5 17.6 3072 1 2 "5@2.5,0.0,atk;1@4.0,-2.0,walk1;3@5.0,2.2,walk2" $T/v11.png clear
python3 hud.py $T/v11.png $O/11_the_pumpkin_king.png 84 1 22 face1 "THE PUMPKIN KING"
$J Showcase 8 21.5 31 3072 1 4 "11@4.6,0.0,atk;7@3.8,-1.8,walk1;6@4.4,1.9,walk2" $T/v16.png
python3 hud.py $T/v16.png $O/16_mister_giggles.png 71 2 9 face1 "MISTER GIGGLES"
$J Showcase 12 21.5 31 3072 1 2 "12@3.5,0.0,atk;9@3.2,-1.4,walk1,24000;9@3.8,1.5,walk2,28000" $T/v20.png
python3 hud.py $T/v20.png $O/20_count_hollowfang.png 66 1 21 face1 "COUNT HOLLOWFANG"
$J Show5 16 22.49 14.5 3072 1 4 "17@3.8,0.0,atk;16@2.6,-1.2,walk1;16@3.0,1.3,walk2" $T/v28.png clear
python3 hud.py $T/v28.png $O/28_frankenstein_prime.png 88 2 9 face0 "FRANKENSTEIN PRIME"
$J -Dtrig=1 Show5 17 32.5 15.2 3072 96 1 - $T/v31.png clear
python3 hud.py $T/v31.png $O/31_the_boulder.png 100 0 146 face1
$J -Dtrig=1 Show5 19 30.5 25.74 3072 120 3 "18@2.2,0.25,atk;18@3.4,1.0,walk1;18@7,-2.0,walk2" $T/v34.png clear
python3 hud.py $T/v34.png $O/34_the_other_world.png 100 0 146 face0
$J Show5 20 12.5 21.49 3072 1 4 "22@3.2,0.0,atk;18@4.8,-1.9,walk1;19@5.4,1.9,walk2" $T/v35.png clear
python3 hud.py $T/v35.png $O/35_seven_death.png 100 2 12 face0 "SEVEN DEATH"
