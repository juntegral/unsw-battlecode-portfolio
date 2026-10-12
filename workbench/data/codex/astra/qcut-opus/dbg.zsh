#!/bin/zsh
# debug arms one at a time so the per-pid log can be attributed
cd ~/meow-redteam
T=~/.claude/jobs/e2109d93/tmp
D="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qcut-opus"
for arm in qc_dbg2 qc_dbg2on qc_dbg2w; do
  o=solo/runs/qc_dbg/$arm-sl-seed1-side1
  rm -rf "$o"
  rm -f $T/qcdbg-*.log
  ./play.sh solo/bots/mD17 solo/bots/$arm maps/ladder/ladder_slithery_fight_1.map 1 "$o" > "$o.out" 2>&1
  cat $T/qcdbg-*.log > "$D/dbg-$arm.log"
done
echo done
