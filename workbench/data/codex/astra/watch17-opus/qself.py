"""watch17-opus: last rounds before a queen death on wall / own body: open neighbours of her head each round start.
Usage (from ROOT): python3 -B .../qself.py <ver> [<ver> ...]"""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path

C = json.loads(Path('data/codex/astra/watch17-opus/cache.json').read_text())
RS = {0: 'wall', 1: 'own', 2: 'body', 3: 'headon', 4: 'other'}
idx = {}
for f in glob.glob('data/online/smoke/one*-old/game-*.json') + glob.glob('data/online/live-one1/b*/game-*.json'):
    idx[Path(f).stem.split('-')[1]] = f
N = replay.EVENT_NAMES


def look(g, back=6):
    f = idx[str(g['id'])]
    j = json.load(open(f))
    ours = g['ours']
    root = replay.load(Path(f).parent / ('M%d.replay' % j['id'])).root()
    G = geometry(root.text(0))
    W, nb = G['W'], G['nb']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Q = min(i for i in teams if teams[i] == ours)
    r0 = g['qdead'][0] - back
    rnd = -1
    rows = []
    for ev in root.pointer(3):
        k = N[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
            if rnd >= r0 and Q in bodies:
                h = bodies[Q][0]
                own = {}
                for i, b in bodies.items():
                    for z, c in enumerate(b):
                        own[c] = ('self' if i == Q else 'mate' if teams[i] == ours else 'foe') + ('-tail' if z == len(b) - 1 else '')
                st = [own.get(n, 'free') for n in nb[h]]
                rows.append('  r%d len %d head %s walls %d sides %s' % (rnd, len(bodies[Q]), (h % W, h // W), 4 - len(nb[h]), st))
        elif k == 'dragonAction':
            if rnd >= r0 and p.i32(0) == Q:
                a = p.pointer(0)
                kind = a.u16(0) if a else 9
                rows.append('     action kind %d dirs %s' % (kind, list(a.pointer(0)) if a and kind == 0 and a.pointer(0) is not None else []))
        elif k == 'dragonUpdate':
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 'dragonSplit':
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
            if Q in (p.i32(0), p.i32(4)) and rnd >= r0:
                rows.append('     SPLIT queen now %d' % len(bodies[Q]))
        elif k == 'dragonDeath':
            i = p.i32(0)
            if i == Q:
                rows.append('     QUEEN DEAD r%d on %s' % (rnd, RS.get(p.u16(4))))
                break
            bodies.pop(i)
    return rows


import re
if sys.argv[1] == 'sum':
    for v in sys.argv[2:]:
        gs = sorted((g for g in C.values() if g.get('ver') == v and g['qdead'] and g['qdead'][2] in (0, 1)), key=lambda g: g['id'])
        n0 = alt = 0
        det = []
        for g in gs:
            rows = look(g, 8)
            st = [(int(re.match(r'\s+r(\d+) len (\d+)', r).group(1)), int(re.match(r'\s+r(\d+) len (\d+)', r).group(2)), r.count("'free'"), i) for i, r in enumerate(rows) if r.startswith('  r')]
            last = st[-1]
            mv = [x for x in st[:-1] if x[3] + 1 < len(rows) and 'kind 0' in rows[x[3] + 1]]
            prev = mv[-1] if mv else None
            n0 += last[2] == 0
            a = bool(prev and prev[2] >= 2)
            alt += a
            det.append('%s r%d len %d free@death %d, step in r%s had %s free sides %s' % (g['id'], g['qdead'][0], g['qdead'][1], last[2], prev[0] if prev else '-', prev[2] if prev else '-', 'W' if g['win'] else 'L'))
        n = sum(1 for g in C.values() if g.get('ver') == v)
        print('%s: games %d, queen died on wall/own %d, with 0 free sides at death %d, entering step had another free side %d' % (v, n, len(gs), n0, alt))
        for d in det:
            print('    ' + d)
    sys.exit()
for v in sys.argv[1:]:
    for g in sorted((g for g in C.values() if g.get('ver') == v and g['qdead'] and g['qdead'][2] in (0, 1)), key=lambda g: g['id']):
        print(v, g['id'], g['map'], 'WIN' if g['win'] else 'LOSS')
        print('\n'.join(look(g)))
