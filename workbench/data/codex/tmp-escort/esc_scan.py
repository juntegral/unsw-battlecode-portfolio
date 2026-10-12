"""esc_scan.py <arm>... : queen company and chase counts for local runs (definitions of dossier/diag-topqueen.md, tq2_def.py).
One json line per game to src/w-escort/esc-<arm>.jsonl. Our side = the arm's bot. Tiles = torus Manhattan, steps = open edges
and portals with bodies ignored. Chase = consecutive queen turns that start with a non-queen enemy head within 3 steps."""
import sys
sys.dont_write_bytecode = True
import json
import re
from collections import defaultdict, deque
from pathlib import Path
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/local')
from replay_format import load, point
from count_local import Geo

RUNS = Path('~/meow-redteam/solo/runs')
HERE = Path(__file__).resolve().parent
CHECK = (50, 100, 150, 300)


def scan(path, our_side):
    root = load(path).root()
    bodies, teams, raw = {}, {}, []
    w = h = 0
    for line in root.text(0).splitlines():
        q = line.split('#', 1)[0].split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = 0 if int(q[1]) == our_side else 1
        elif q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    g = Geo(w, h, raw)
    tile = lambda p: p[1]*w+p[0]
    queen = [min(i for i in bodies if teams[i] == s) for s in (0, 1)]
    balls = {}

    def ball(src):
        if src not in balls:
            d, q = {src: 0}, deque([src])
            while q:
                c = q.popleft()
                if d[c] >= 3:
                    continue
                for t in g.adj[c]:
                    if t not in d:
                        d[t] = d[c]+1
                        q.append(t)
            balls[src] = d
        return balls[src]

    def man(a, c):
        dx, dy = abs(a % w-c % w), abs(a // w-c // w)
        return min(dx, w-dx)+min(dy, h-dy)

    qturns, deaths, snaps = [], [], {}
    pearls = [0, 0]
    pearls_band = [0, 0, 0, 0]
    st = dict(rnd=-1, actor=None, qn=0)
    fate = None
    last = None

    def snapshot():
        return dict(alive=sum(1 for i in bodies if teams[i] == 0), total=sum(len(b) for i, b in bodies.items() if teams[i] == 0),
                    ealive=sum(1 for i in bodies if teams[i] == 1), etotal=sum(len(b) for i, b in bodies.items() if teams[i] == 1),
                    queen=len(bodies.get(queen[0], ())), equeen=len(bodies.get(queen[1], ())))

    def queen_turn():
        q = queen[0]
        b = bodies[q]
        head = b[0]
        st['qn'] += 1
        near = ball(head)
        occ = {}
        for i, bb in bodies.items():
            for c in bb:
                occ[c] = i
        ids = [i for i, bb in bodies.items() if teams[i] == 1 and i != queen[1] and near.get(bb[0], 9) <= 3]
        mates = [(man(head, bb[0]), len(bb), i, bb[0]) for i, bb in bodies.items() if teams[i] == 0 and i != q]
        nb = [t for t in g.adj[head]]
        free = sum(1 for t in nb if t not in occ)
        mate_block = sum(1 for t in nb if t in occ and occ[t] != q and teams[occ[t]] == 0)
        own3 = sum(1 for m in mates if m[0] <= 3)
        own5 = sum(1 for m in mates if m[0] <= 5)
        short5 = sum(1 for m in mates if m[0] <= 5 and m[1] <= 4)
        rec = dict(n=st['qn'], r=st['rnd'], L=len(b), head=head, own3=own3, own5=own5, short5=short5, ids=ids, free=free, open=len(nb),
                   mate_block=mate_block,
                   pur=[[i, len(bodies[i]), bodies[i][0]] for i in ids],
                   mates=[[m[2], m[1], m[3], m[0]] for m in mates if m[0] <= 7])
        qturns.append(rec)
        return rec

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if st['rnd'] in CHECK:
                snaps[st['rnd']] = snapshot()
            st['rnd'], st['actor'] = p.i32(0), None
        elif k == 1:
            a = p.i32(0)
            st['actor'] = a
            if a == queen[0]:
                last = queen_turn()
        elif k == 3:
            if not p.bit(0) and st['actor'] is not None:
                s = teams[st['actor']]
                pearls[s] += 1
                if s == 0:
                    r = st['rnd']
                    pearls_band[0 if r <= 50 else 1 if r <= 100 else 2 if r <= 300 else 3] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(point(p.pointer(0))), tile(point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(point(c)) for c in p.pointer(z))
            teams[child] = teams[parent]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            actor = st['actor']
            hd = bodies[i][0]
            dq = man(hd, bodies[queen[0]][0]) if queen[0] in bodies else 99
            deaths.append(dict(r=st['rnd'], id=i, s=teams[i], reason=reason, mover=actor if actor is not None else -1, L=len(bodies[i]), dq=dq,
                               head=hd, qn=st['qn']))
            if i == queen[0]:
                kind = 'rammed' if reason == 3 and i != actor else 'into_head' if reason == 3 else 'boxed'
                fate = dict(r=st['rnd'], L=len(bodies[i]), reason=reason, kind=kind, qn=st['qn'], head=hd,
                            free=last['free'] if last else -1, mate_block=last['mate_block'] if last else -1,
                            own5=last['own5'] if last else -1)
            bodies.pop(i)
    end = st['rnd']
    snaps['end'] = snapshot()
    for c in CHECK:
        snaps.setdefault(c, snaps['end'])
    res = root.pointer(4)
    winner = res.u16(6) if res.u16(4) == 1 else None
    return dict(w=w, h=h, end=end, win=None if winner is None else int(winner == our_side), queen=queen, fate=fate, qturns=qturns,
                deaths=[d for d in deaths if d['reason'] == 3 or (d['s'] == 0 and d['dq'] <= 8)], snaps={str(k): v for k, v in snaps.items()}, pearls=pearls,
                pearls_band=pearls_band)


def main():
    only = None
    arms = [a for a in sys.argv[1:] if not a.startswith('only=')]
    for a in sys.argv[1:]:
        if a.startswith('only='):
            only = set(Path(a[5:]).read_text().split())
    for arm in arms:
        out = []
        for d in sorted((RUNS / arm).iterdir()):
            m = re.fullmatch(r'(.+)-seed(\d+)-side([01])', d.name)
            rp = d / 'game.replay'
            if not m or not rp.exists() or not (d / 'result.txt').exists() or (only is not None and d.name not in only):
                continue
            rec = scan(rp, int(m.group(3)))
            rec.update(game=d.name, map=m.group(1), seed=int(m.group(2)), side=int(m.group(3)), arm=arm)
            out.append(json.dumps(rec, separators=(',', ':')))
        (HERE / ('esc-%s.jsonl' % arm)).write_text('\n'.join(out) + '\n')
        print(arm, len(out), flush=True)


main()
