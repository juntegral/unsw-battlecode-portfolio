"""replay -> .map. Geometry (walls, portals, dragons) is read verbatim from the map text inside the replay.
Pearl gaps are redacted there (TILE .. 0 0); they are ESTIMATED from natural pearl spawns (see below).
usage: python3 -I convert.py <game id> <out.map>"""
import sys, json
from collections import defaultdict
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/tools')
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/fountain-analysis-2')
from ladder_replay import base
replay = base.replay
R = '~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/one14-c1-old/M%d.replay'
BIG = 10000000

gid = int(sys.argv[1]); out = sys.argv[2]
root = replay.load(R % gid).root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
sym = lines[1].split()[1]

def mirror(c):
    x, y = c
    return (W - 1 - x if 'y' in sym else x, H - 1 - y if 'x' in sym else y)  # 'y' = mirrored across the y axis (flips x)

# events: natural spawns (between roundStart and first turnStart) vs everything else
rnd = 0; in_turn = False
removed = {}              # tile -> round the pearl was last removed
gaps = defaultdict(list)  # tile -> observed respawn gaps
spawned = set(); r0 = set(); eaten = set()
for ev in root.pointer(3):
    k = replay.EVENT_NAMES[ev.u16(0)]; p = ev.pointer(0)
    if k == 'roundStart':
        rnd = p.i32(0); in_turn = False
    elif k == 'turnStart':
        in_turn = True
    elif k == 'tileChange':
        c = replay.point(p.pointer(0)); v = p.u32(0)
        if v == 1 and not in_turn:
            spawned.add(c)
            if rnd == 0: r0.add(c)
            if c in removed: gaps[c].append(rnd - removed[c])
        elif v == 0:
            removed[c] = rnd; eaten.add(c)

beds = set(spawned)
beds |= {mirror(c) for c in list(beds)}
est = {}
for c in beds:
    g = gaps.get(c, []) + gaps.get(mirror(c), [])
    if g: est[c] = (min(g), max(g), len(g))
    else: est[c] = None
obs = [v for v in est.values() if v]
pool = (min(v[0] for v in obs), max(v[1] for v in obs), 0) if obs else (1, 10, 0)
for c in est:
    if est[c] is None: est[c] = pool   # never seen to respawn: pooled map-wide range (ESTIMATE)
res = []
for ln in lines:
    q = ln.split()
    if q and q[0] == 'TILE':
        c = (int(q[1]), int(q[2]))
        if c in est:
            ln = 'TILE %d %d %d %d' % (c[0], c[1], est[c][0], est[c][1])
    if ln.strip() != 'END': res.append(ln)
open(out, 'w').write('\n'.join(res) + '\nEND\n')
print(gid, 'W,H', W, H, sym, 'beds', len(beds), 'with gap obs', sum(1 for v in est.values() if v[2]), 'unobserved', sum(1 for v in est.values() if not v[2]))
