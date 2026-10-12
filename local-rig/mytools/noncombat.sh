#!/bin/sh
# noncombat.sh <tag>: non-combat deaths for my bot vs opponent across runs/<tag>/*
mine=0; theirs=0; g=0
for d in runs/$1/*/; do
  g=$((g+1))
  case "$d" in *side0/) my=A; op=B;; *) my=B; op=A;; esac
  m=$(grep -v head-to-head $d/engine.log | grep -c "team $my")
  t=$(grep -v head-to-head $d/engine.log | grep -c "team $op")
  mine=$((mine+m)); theirs=$((theirs+t))
done
echo "$1: games=$g non-combat deaths mine=$mine theirs=$theirs"
