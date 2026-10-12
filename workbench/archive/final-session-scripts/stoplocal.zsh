#!/bin/zsh
# Stop the remaining local batches (nothing more goes live), print their final tallies, then the team feeds and rank.
T=~/.claude/jobs/e2109d93/tmp
for a in mSh1 mSh7 mHl3 mHl6; do python3 $T/killtree.py "zsh $T/h2h17.zsh $a"; done
python3 $T/killtree.py "zsh $T/shed9.zsh"
python3 ~/meow-redteam/solo/tools/h2h_tally.py | grep "_v16" | cut -c1-48
zsh $T/status.zsh | head -n 9
