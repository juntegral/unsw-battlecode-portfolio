cd "~/01. Project/개인 프로젝트/unsw-swarm"
python3 -B data/codex/astra/qbox-opus/on1.py 12 1504492 > data/codex/astra/qbox-opus/on-1504492.txt 2>&1
python3 -B data/codex/astra/qbox-opus/on1.py 12 1516204 > data/codex/astra/qbox-opus/on-1516204.txt 2>&1
python3 -B data/codex/astra/qbox-opus/on1.py 3 1507926 1515670 1508919 1520833 > data/codex/astra/qbox-opus/on-early2.txt 2>&1
python3 -B data/codex/astra/qbox-opus/on1.py 2 > data/codex/astra/qbox-opus/on-all.txt 2>&1
grep "^  r\|QUEEN DEAD\|queen action\|QUEEN SPLIT\|queen eats" data/codex/astra/qbox-opus/on-1504492.txt
grep "^  r\|QUEEN DEAD\|queen action\|QUEEN SPLIT\|queen eats" data/codex/astra/qbox-opus/on-1516204.txt
