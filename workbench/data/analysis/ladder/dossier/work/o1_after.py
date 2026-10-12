"""Scratch (diag-one1, job B): what a dragon does after a meal. For every natural pearl eaten in rounds 1-80 by a dragon
that is not the queen: the eater's free-path steps to that tile at the start of each of the next 6 rounds (cap 9, -1 dead),
and at its next own turn whether another pearl or an enemy head is in its 7 by 7; when the tile's next pearl is born
(within 12 rounds) and who eats it how soon. Usage (repo root): python3 -B .../o1_after.py <set>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from o1_scan import jobs, OUT, STEP


def scan(label, path, j, team=1119):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 0 if teams[i] == own else 1
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]

    def dest(h, d):
        x, y = h
        e = edge_id(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 1:
            return None
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            prow, px = divmod(partner, W + 1)
            py = prow // 2
            return ((px - (d == 3)) % W, (py - (d == 0)) % H)
        dx, dy = STEP[d]
        return ((x + dx) % W, (y + dy) % H)

    def inview(h, c):
        dx = (c[0] - h[0] + W // 2) % W - W // 2
        dy = (c[1] - h[1] + H // 2) % H - H // 2
        return abs(dx) <= 3 and abs(dy) <= 3

    def steps(a, b):
        if a == b:
            return 0
        occ = set()
        for bb in bodies.values():
            occ.update(bb)
        seen = {a: 0}
        qu = deque([a])
        while qu:
            x = qu.popleft()
            if seen[x] >= 8:
                continue
            for d in range(4):
                n = dest(x, d)
                if n is None or n in seen:
                    continue
                if n == b:
                    return seen[x] + 1
                if n in occ:
                    continue
                seen[n] = seen[x] + 1
                qu.append(n)
        return 9

    recs = []
    open_recs = []
    by_eater = {}
    by_cell = {}
    live = {}
    rnd, actor = -1, None
    expected = 0
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > 100:
                break
            keep = []
            for rec in open_recs:
                dt = rnd - rec['r']
                if 1 <= dt <= 6:
                    i = rec['i']
                    rec['d'].append(steps(bodies[i][0], rec['c']) if i in bodies else -1)
                if dt <= 12:
                    keep.append(rec)
                else:
                    by_cell.pop(rec['c'], None) if by_cell.get(rec['c']) is rec else None
            open_recs = keep
        elif k == 1:
            actor = p.i32(0)
            rec = by_eater.pop(actor, None)
            if rec is not None and actor in bodies:
                h = bodies[actor][0]
                rec['pearl'] = int(any(inview(h, c) and c != rec['c'] for c in live))
                rec['foe'] = int(any(side(z) != rec['s'] and inview(h, bb[0]) for z, bb in bodies.items()))
                rec['mates'] = sum(1 for z, bb in bodies.items() if z != actor and side(z) == rec['s'] and inview(h, bb[0]))
                rec['L'] = len(bodies[actor])
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if expected:
                    expected -= 1
                    live[c] = 'dead'
                else:
                    live[c] = 'nat'
                    rec = by_cell.get(c)
                    if rec is not None and rec['born'] < 0:
                        rec['born'] = rnd - rec['r']
            else:
                o = live.pop(c)
                s = side(actor)
                rec = by_cell.get(c)
                if rec is not None and rec['born'] >= 0 and rec['next'] is None:
                    rec['next'] = [s, rnd - rec['r'] - rec['born'], int(actor == rec['i'])]
                if o == 'nat' and 1 <= rnd <= 80 and actor != queens[s]:
                    rec = dict(r=rnd, s=s, i=actor, c=c, d=[], born=-1, next=None, pearl=-1, foe=-1, mates=-1, L=0)
                    recs.append(rec)
                    open_recs.append(rec)
                    by_eater[actor] = rec
                    by_cell[c] = rec
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif k == 11:
            i = p.i32(0)
            expected = (len(bodies[i]) + 1) // 2
            bodies.pop(i)
    for rec in recs:
        rec['c'] = list(rec['c'])
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=W * H, w=W, h=H, recs=recs)


if __name__ == '__main__':
    name = sys.argv[1]
    todo = jobs(name)
    with open(OUT + 'o1_after-%s.jsonl' % name, 'w') as f:
        for label, path, j in todo:
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
    print('done', name, len(todo))
