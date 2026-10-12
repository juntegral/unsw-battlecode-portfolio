cd "~/01. Project/개인 프로젝트/unsw-swarm"
D=data/codex/astra/stuck-opus
nice -n 10 python3 -B $D/paired.py tot one11-k1 one12-k1 one13-k1 one13-k2 one14-k1
nice -n 10 python3 -B $D/paired.py tot one11-p1 one12-p1 one13-p1 one13-p2 one14-p1
nice -n 10 python3 -B $D/paired.py idle one11-c1 one12-c1 one13-c1 one13-c2 one14-c1
nice -n 10 python3 -B $D/paired.py deadend one11-c1 one12-c1 one13-c1 one13-c2 one14-c1
tail -2 $D/run.log
ls data/online/smoke | grep "one14.*-old"
date
