#!/bin/zsh
# usage: run2.sh <out file> <script path from ROOT> args...
cd "~/01. Project/개인 프로젝트/unsw-swarm"
out=$1; shift
python3 -B "$@" > "$out" 2>&1
