#!/bin/zsh
# qmate-opus: wait until $1 of my games have a result.txt or the clock passes $2 (HHMM).
t() { ls $HOME/meow-redteam/solo/runs/qm_qm_*/*/result.txt 2>/dev/null | wc -l; }
until [ $(t) -ge $1 ] || [ $(date +%H%M) -ge $2 ]; do sleep 5; done
ls $HOME/meow-redteam/solo/runs/qm_qm_*/*/result.txt | sed 's/.*runs\///'
date
