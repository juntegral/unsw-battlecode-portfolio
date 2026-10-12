#!/bin/zsh
# sight-opus: return when pool.log has $1 lines or the clock passes $2 (HHMM).
D=${0:A:h}
until [ -f $D/pool.log ] && [ $(grep -c . $D/pool.log) -ge $1 ] || [ $(date +%H%M) -ge $2 ]; do sleep 10; done
date +%H:%M:%S
cat $D/pool.log
