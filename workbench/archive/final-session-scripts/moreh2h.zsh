#!/bin/zsh
# The machine is idle (load 3): start head to heads against the live bot for three more one15-based arms, one instance each.
T=~/.claude/jobs/e2109d93/tmp
for a in mQ15 mO15 mHs15; do
  pgrep -f "tmp/h2h16.zsh $a" > /dev/null || H2H_P=8 nohup zsh $T/h2h16.zsh $a > $T/h2h16-$a.out 2>&1 &
done
sleep 2; pgrep -fl "tmp/h2h16" | cut -c1-100
