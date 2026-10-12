import sys, time
from pathlib import Path
p = Path('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unD-opus/run.log')
n = int(sys.argv[1])
t = time.time() + float(sys.argv[2])
while time.time() < t and len(p.read_text().splitlines()) < n:
    time.sleep(2)
ls = p.read_text().splitlines()
print(len(ls), time.strftime('%H:%M:%S'))
for l in ls[68:]:
    print(l[:150])
