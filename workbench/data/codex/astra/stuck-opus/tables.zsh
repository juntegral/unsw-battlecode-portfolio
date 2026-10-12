cd "~/01. Project/개인 프로젝트/unsw-swarm"
D=data/codex/astra/stuck-opus
wc -l $D/rows-one*.jsonl | tail -1
echo "== by version"; nice -n 10 python3 -B $D/cls.py online ver
echo "== by set"; nice -n 10 python3 -B $D/cls.py online set
echo "== by phase"; nice -n 10 python3 -B $D/cls.py online phase
nice -n 10 python3 -B $D/cls.py online map > $D/t-cls-map.txt
nice -n 10 python3 -B $D/agg.py online an a2n b c d > $D/t-online.txt 2>&1
nice -n 10 python3 -B $D/agg.py local an a2n b c d > $D/t-local.txt 2>&1
nice -n 10 python3 -B $D/cls.py local fam > $D/t-cls-local.txt
nice -n 10 python3 -B $D/cls.py local size >> $D/t-cls-local.txt
tail -3 $D/run.log
date
