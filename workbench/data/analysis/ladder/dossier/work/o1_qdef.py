"""Scratch (diag-one1): our queen's death by a ram and what her mates could do. For every turn of a non-queen dragon of
ours that has our queen's head and a non-queen enemy head in its 7 by 7: is the head within 3 steps of the queen (bodies
ignored, as guards_queen), is it inside this mate's ram reach over free tiles, did the mate ram it. At the queen's death:
the rammer's start distance and steps, and each mate's last such turn.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_qdef.py <set>"""
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
    cells = W * H
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
    Q = queens[0]

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

    def gap(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def inview(h, c):
        dx = (c[0] - h[0] + W // 2) % W - W // 2
        dy = (c[1] - h[1] + H // 2) % H - H // 2
        return abs(dx) <= 3 and abs(dy) <= 3

    def bfs(h, R, occ, target):
        seen = {h: 0}
        qu = deque([h])
        while qu:
            c = qu.popleft()
            if seen[c] >= R:
                continue
            for d in range(4):
                n = dest(c, d)
                if n is None or n in seen:
                    continue
                if n == target:
                    return seen[c] + 1
                if n in occ:
                    continue
                seen[n] = seen[c] + 1
                qu.append(n)
        return 99

    guard_turns = []   # [r, mate L, mate id, enemy id, enemy L, steps queen-enemy, mate reach R, mate steps to enemy, rammed it, rammed other]
    last = {}
    out = None
    rnd, actor, cur = -1, None, []
    qlast = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor, cur = p.i32(0), None, []
        elif k == 1:
            actor = p.i32(0)
            cur = []
            if actor == Q:
                h = bodies[Q][0]
                qlast = dict(r=rnd, L=len(bodies[Q]), h=list(h),
                             foes=sorted([bfs(h, 6, set(), bb[0]), len(bb), z] for z, bb in bodies.items() if side(z) == 1 and z != queens[1] and gap(h, bb[0]) <= 6),
                             mates=sorted([gap(h, bb[0]), len(bb), z] for z, bb in bodies.items() if side(z) == 0 and z != Q and gap(h, bb[0]) <= 5))
            if side(actor) == 1:
                continue
            if actor == Q or Q not in bodies:
                continue
            h = bodies[actor][0]
            qh = bodies[Q][0]
            L = len(bodies[actor])
            last[actor] = dict(r=rnd, L=L, dq=gap(h, qh), seesq=int(inview(h, qh)), g=[])
            if not inview(h, qh):
                continue
            occ = None
            for z, bb in bodies.items():
                if side(z) != 1 or z == queens[1] or not inview(h, bb[0]):
                    continue
                sq = bfs(qh, 5, set(), bb[0])
                if sq > 5:
                    continue
                if occ is None:
                    occ = set()
                    for b2 in bodies.values():
                        occ.update(b2)
                R = min(4 if cells > 1200 else 3, (L + 3) // 4 + L - 2)
                ms = bfs(h, 6, occ, bb[0])
                row = [rnd, L, actor, z, len(bb), sq, R, ms, 0, 0]
                guard_turns.append(row)
                cur.append(row)
                last[actor]['g'].append(row)
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
            i, reason = p.i32(0), p.u16(4)
            if reason == 3 and i != actor and side(i) == 1 and side(actor) == 0:
                for row in cur:
                    if row[3] == i:
                        row[8] = 1
                    else:
                        row[9] = 1
            if i == Q:
                qh = bodies[Q][0]
                out = dict(r=rnd, L=len(bodies[Q]), reason=reason, mover=int(actor == Q), qlast=qlast)
                if reason == 3 and actor != Q:
                    out['rammer'] = actor
                    out['rammerL'] = len(bodies[actor])
                    out['mates'] = [dict(id=z, L=len(bb), dq=gap(qh, bb[0]), last=last.get(z)) for z, bb in bodies.items()
                                    if side(z) == 0 and z != Q and gap(qh, bb[0]) <= 5]
                last.pop(i, None)
            last.pop(i, None)
            bodies.pop(i)
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=cells, death=out, guard=guard_turns)


if __name__ == '__main__':
    name = sys.argv[1]
    todo = jobs(name)
    with open(OUT + 'o1_qdef-%s.jsonl' % name, 'w') as f:
        for label, path, j in todo:
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
    print('done', name, len(todo))
