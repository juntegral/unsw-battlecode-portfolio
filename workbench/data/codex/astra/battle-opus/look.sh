#!/bin/zsh
# usage: look.sh <battle> <game> <dragon> <r0> <r1>   (7x7 boards without the eat lines)
cd "~/01. Project/개인 프로젝트/unsw-swarm"
python3 -B data/analysis/ladder/dossier/work/o1_look.py data/online/live-one1/b$1/M$2.replay $2 $3 $4 $5 2>&1 | grep -v " eats "
