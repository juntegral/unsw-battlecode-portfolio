"""qcut: in our online games (one11..one17), every queen split that sheds a 2-child while she is 6+ long: was she boxed
(all four neighbours a wall or a body), and was one blocker her own segment (index >= 2)? Usage (from ROOT): python3 -B data/codex/astra/qcut-opus/online.py"""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque, Counter
from pathlib import Path

VER = dict(line.split() for line in open('data/online/smoke/versions.tsv'))
VERS = {k: v for k, v in VER.items() if v in ('one11', 'one12', 'one13', 'one14', 'one15', 'one16', 'one17')}


def run(mp, j):
    rp = mp.parent / ('M%d.replay' % j['id'])
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(rp).root()
    bot = root.text(1 if ours == 0 else 2).strip()
    if bot not in VERS:
        return None
    G = geometry(root.text(0))
    W, nb = G['W'], G['nb']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Q = min(i for i in teams if teams[i] == ours)
    rnd = -1
    out = []
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
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
            par, ch = p.i32(0), p.i32(4)
            if par == Q:
                body = list(bodies[Q])
                occ = {}
                for i, b in bodies.items():
                    for c in b:
                        occ[c] = i
                head = body[0]
                units = sum(1 for i in bodies if teams[i] == ours)
                sides = []
                for n in nb[head]:
                    if n == head:
                        sides.append('wall')
                    elif n in occ:
                        sides.append(('own%d' % body.index(n)) if occ[n] == Q else 'mate' if teams[occ[n]] == ours else 'foe')
                    else:
                        sides.append('free')
            for z, i in enumerate((par, ch)):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
            if par == Q:
                out.append(dict(r=rnd, L=len(body), child=len(bodies[ch]), units=units, sides=sides))
        elif k == 11:
            bodies.pop(p.i32(0))
    return dict(id=j['id'], ver=VERS[bot], map=j.get('mapName'), splits=out)


files = sorted(glob.glob('data/online/live-one1/b*/game-*.json')) + sorted(glob.glob('data/online/smoke/one1[1-7]-*-old/game-*.json'))
seen = set()
games = []
for f in files:
    j = json.load(open(f))
    if 1119 not in (j['teamAId'], j['teamBId']) or j.get('status') != 'completed' or j['id'] in seen:
        continue
    seen.add(j['id'])
    try:
        r = run(Path(f), j)
    except Exception as ex:
        continue
    if r:
        games.append(r)
c = Counter()
ex = []
for g in games:
    for s in g['splits']:
        if s['child'] != 2 or s['L'] < 6:
            continue
        own = max((int(x[3:]) for x in s['sides'] if x.startswith('own') and int(x[3:]) >= 2), default=-1)
        boxed = 'free' not in s['sides']
        kind = ('boxed+own' if own >= 2 else 'boxed-noown') if boxed else 'open'
        c[('r<20' if s['r'] < 20 else 'r>=20', 'u>=60' if s['units'] >= 60 else 'u<60', kind)] += 1
        if boxed and own >= 2 and s['r'] >= 20:
            ex.append((g['id'], g['map'], g['ver'], s['r'], s['L'], own, s['units'], s['sides']))
print('games', len(games), 'by version', dict(Counter(g['ver'] for g in games)))
for k, v in sorted(c.items()):
    print('  ', k, v)
print('boxed+own after r20:', len(ex), 'in', len({e[0] for e in ex}), 'games')
for e in ex[:60]:
    print('  ', e)
json.dump(ex, open('data/codex/astra/qcut-opus/online-boxed.json', 'w'))
