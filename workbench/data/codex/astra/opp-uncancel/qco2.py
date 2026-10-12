"""opp-uncancel: per game, over our queen's turns: turns with a foe head within 5 / within 2, share of those with a mate within 5,
and steps where she took a smaller nearest-foe gap than the best free option (foe within 5). Same for THEIR queen (mirror)."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path

OPP = 899
games = {}
for f in glob.glob('data/online/live-one1/b*/game-*.json'):
    j = json.load(open(f))
    if OPP in (j.get('teamAId'), j.get('teamBId')) and 1119 in (j.get('teamAId'), j.get('teamBId')):
        games[j['id']] = (j, Path(f))
print('gid     map            res | side: Qturns  foe<=5  mate<=5 on those  foe<=2  closer-than-best | same for them')
for gid in sorted(games):
    j, mp = games[gid]
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(mp.parent / ('M%d.replay' % gid)).root()
    G = geometry(root.text(0))
    W, H, nb = G['W'], G['H'], G['nb']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Qs = {s: min(i for i in teams if teams[i] == s) for s in (0, 1)}
    st = {s: dict(t=0, f5=0, m5=0, f2=0, closer=0, af5=0, af2=0, at=0) for s in (0, 1)}
    pend = {}

    def gap(a, b):
        ax, ay, bx, by = a % W, a // W, b % W, b // W
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, W - dx) + min(dy, H - dy)

    rnd, actor = -1, None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            actor = None
        elif k == 1:
            actor = p.i32(0)
            for s in (0, 1):
                Q = Qs[s]
                if actor == Q and Q in bodies:
                    occ = set()
                    for b in bodies.values():
                        occ.update(b)
                    h = bodies[Q][0]
                    foes = [b[0] for i, b in bodies.items() if teams[i] != s]
                    if not foes:
                        continue
                    near = min(gap(h, f) for f in foes)
                    x = st[s]
                    x['t'] += 1
                    if near <= 5:
                        x['f5'] += 1
                        if any(i != Q and teams[i] == s and gap(h, b[0]) <= 5 for i, b in bodies.items()):
                            x['m5'] += 1
                        opts = {n: min(gap(n, f) for f in foes) for n in nb[h] if n not in occ}
                        pend[s] = opts
                    if near <= 2:
                        x['f2'] += 1
                    if Qs[1 - s] not in bodies:
                        x['at'] += 1
                        x['af5'] += near <= 5
                        x['af2'] += near <= 2
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                for s in (0, 1):
                    if i == Qs[s] and actor == i and s in pend:
                        opts = pend.pop(s)
                        if hd in opts and opts[hd] < max(opts.values()):
                            st[s]['closer'] += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            par, ch = p.i32(0), p.i32(4)
            for z, i in enumerate((par, ch)):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
        elif k == 11:
            bodies.pop(p.i32(0), None)
    res = 'win' if (j['winner'] == 'ab'[ours]) else 'loss'
    a, b = st[ours], st[1 - ours]
    print('   after the other queen died: our Q turns %d foe<=5 %d foe<=2 %d | their Q turns %d our head<=5 %d <=2 %d' % (a['at'], a['af5'], a['af2'], b['at'], b['af5'], b['af2']))
    print('%d %-14s %-4s | us: %3d %3d %3d %3d %3d | them: %3d %3d %3d %3d %3d' % (
        gid, j['mapName'][:14], res, a['t'], a['f5'], a['m5'], a['f2'], a['closer'], b['t'], b['f5'], b['m5'], b['f2'], b['closer']))
