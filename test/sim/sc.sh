#!/bin/sh
# sc.sh level x y angle ticks weapon types out
cd "$(dirname "$0")"
JAVA_TOOL_OPTIONS= /home/claude/tc/jdk8u422-b05/bin/java -cp cls:/home/claude/tc/midp20_cldc11.jar Showcase "$@" 2>&1 | grep -v Picked
