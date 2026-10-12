#!/bin/zsh
# one17 minus one feeding-related switch per arm
S=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
cd $HOME/meow-redteam/solo
typeset -A arms
arms=(uc_nfc "FEED_CAP_ROUND:350," uc_nlf "LEADER_FULL_UNITS:56," uc_nqh "QUEEN_HERD:true," uc_nqb "QUEEN_BOOT_LEN:6," uc_nfe "FEEDER_EAT:true," uc_nam "ATTACK_MIN_UNITS:56,")
for n in ${(k)arms}; do
  V=${S/$arms[$n]/}
  [[ $V == $S ]] && echo "NOT REMOVED $n"
  MKSRC=src/solo/main.cpp python3 tools/mkbots.py "$n=$V" &
done
wait
ls -la bots/uc_n*/bot
