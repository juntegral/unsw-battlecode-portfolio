cd "~/01. Project/개인 프로젝트/unsw-swarm"
python3 -B data/codex/astra/qbox-opus/on1.py 3 1504492 1516204 1520833 > data/codex/astra/qbox-opus/on-early.txt 2>&1
python3 -B data/codex/astra/qbox-opus/on1.py 1 > data/codex/astra/qbox-opus/on-all.txt 2>&1
grep -c "QUEEN DEAD" data/codex/astra/qbox-opus/on-all.txt
grep -A1 "QUEEN DEAD" data/codex/astra/qbox-opus/on-all.txt | grep "  r" | awk '{print $6, $7, $8, $9, $10, $11}' | sort | uniq -c
