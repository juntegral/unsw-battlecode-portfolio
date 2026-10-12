"""loss15-sonnet: early-game trace. Usage (via run.sh): early.py <gameid> <R> [step]
Per `step` rounds up to R: our dragons alive / total length, their same, pearls on board, per our dragon the free-path distance
(whole map, cells not occupied) from head to nearest pearl, cumulative pearl eats by side, and distinct head cells in the last `step` rounds."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque, defaultdict
from pathlib import Path

gid, R = int(sys.argv[1]), int(sys.argv[2])
step = int(sys.argv[3]) if len(sys.argv) > 3 else 10
mp = [Path(f) for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid) + glob.glob('data/online/smoke/*-old/game-%d.json' % gid)][0]
j = json.load(open(mp))
rp = mp.parent / ('M%d.replay' % gid)
ours = 0 if j['teamAId'] == 1119 else 1
root = replay.load(rp).root()
G = geometry(root.text(0))
W, H, N, nb = G['W'], G['H'], G['N'], G['nb']
bodies = {i: deque(b) for i, b in G['bodies'].items()}
teams = dict(G['teams'])
pearls = {}
eats = [0, 0]
hist = defaultdict(list)
rnd = -1
actor = None


def dist_to_pearl(h):
    occ = set()
    for b in bodies.values():
        occ.update(b)
    seen = {h}
    fr = [h]
    d = 0
    while fr and d < 60:
        d += 1
        nx = []
        for c in fr:
            for n in nb[c]:
                if n in seen:
                    continue
                if n in pearls:
                    return d
                if n in occ:
                    continue
                seen.add(n)
                nx.append(n)
        fr = nx
    return -1


def report():
    parts = []
    for s in (0, 1):
        ids = [i for i in bodies if (teams[i] == ours) == (s == 0)]
        parts.append((len(ids), sum(len(bodies[i]) for i in ids)))
    ds = []
    for i in sorted(bodies):
        if teams[i] == ours:
            hs = set(hist[i][-step:])
            ds.append('%d(L%d)@%d,%d d%d u%d' % (i, len(bodies[i]), bodies[i][0] % W, bodies[i][0] // W, dist_to_pearl(bodies[i][0]), len(hs)))
    print('r%3d us %d/%d them %d/%d pearls %d eats %d/%d | %s' % (rnd, parts[0][0], parts[0][1], parts[1][0], parts[1][1], len(pearls), eats[0], eats[1], '  '.join(ds[:8])))


for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        if rnd >= 0 and rnd % step == 0 and rnd <= R:
            report()
        rnd = p.i32(0)
        actor = None
        if rnd > R:
            break
        for i in bodies:
            hist[i].append(bodies[i][0])
    elif k == 1:
        actor = p.i32(0)
    elif k == 3:
        pt = replay.point(p.pointer(0))
        c = pt[1] * W + pt[0]
        if p.u32(0):
            pearls[c] = rnd
        else:
            pearls.pop(c, None)
            if actor in teams:
                eats[0 if teams[actor] == ours else 1] += 1
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        for z, i in enumerate((p.i32(0), p.i32(4))):
            bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
            teams[i] = p.u16(8)
    elif k == 11:
        bodies.pop(p.i32(0))
