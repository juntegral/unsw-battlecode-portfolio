import sys, json
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/tools')
from ladder_replay import replay
R = '~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/one14-c1-old/M%d.replay'
OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/maps-sonnet/out/'
for gid in [int(a) for a in sys.argv[1:]]:
    t = replay.load(R % gid).root().text(0)
    open(OUT + 'text_%d.txt' % gid, 'w').write(t)
    print(gid, len(t), t.splitlines()[:4])
