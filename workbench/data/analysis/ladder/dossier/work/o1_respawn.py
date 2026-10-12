"""Scratch (diag-one1, job B): spawn tiles. For every natural pearl born in rounds 1-100 on a cell where a pearl was
eaten before: rounds since that meal, which side ate it, where that eater's head is now (free-path steps, cap 12, 99 dead),
the nearest head of each side, and who eats the new pearl. Also first births (cell never eaten from).
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_respawn.py <set>"""
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

    def dists(c):
        occ = set()
        heads = {}
        for z, bb in bodies.items():
            occ.update(bb)
            heads[bb[0]] = z
        out = {}
        seen = {c: 0}
        qu = deque([c])
        while qu:
            x = qu.popleft()
            if seen[x] >= 12:
                continue
            for d in range(4):
                n = dest(x, d)
                if n is None or n in seen:
                    continue
                if n in heads:
                    out.setdefault(heads[n], seen[x] + 1)
                    continue
                if n in occ:
                    continue
                seen[n] = seen[x] + 1
                qu.append(n)
        return out

    recs = []       # [birth round, gap or -1, prev eater side or -1, prev eater steps now, d ours, d theirs, eater side, eat round, same dragon as prev eater]
    live = {}
    lasteat = {}    # cell -> (round, side, id)
    family = {}     # dragon -> root eater tag (children inherit)
    rnd, actor = -1, None
    expected = 0
    pending = []
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1) and pending:
            for c, rec in pending:
                ds = dists(c)
                prev = lasteat.get(c)
                if prev is not None:
                    rec[3] = ds.get(prev[2], 99 if prev[2] not in bodies else 13)
                rec[4] = min((v for z, v in ds.items() if side(z) == 0), default=99)
                rec[5] = min((v for z, v in ds.items() if side(z) == 1), default=99)
            pending = []
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > 150:
                break
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if expected:
                    expected -= 1
                    live[c] = None
                elif 1 <= rnd <= 100:
                    prev = lasteat.get(c)
                    rec = [rnd, rnd - prev[0] if prev else -1, prev[1] if prev else -1, -1, 99, 99, -1, -1, 0]
                    live[c] = rec
                    recs.append(rec)
                    pending.append((c, rec))
                else:
                    live[c] = None
            else:
                rec = live.pop(c)
                if rec is not None:
                    prev = lasteat.get(c)
                    rec[6], rec[7] = side(actor), rnd
                    rec[8] = int(prev is not None and prev[2] == actor)
                if rec is not None or c not in lasteat or True:
                    pass
                lasteat[c] = (rnd, side(actor), actor) if rec is not None or c in lasteat else lasteat.get(c)
                if rec is None and c not in lasteat:
                    pass
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
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=W * H, recs=recs)


if __name__ == '__main__':
    name = sys.argv[1]
    todo = jobs(name)
    with open(OUT + 'o1_respawn-%s.jsonl' % name, 'w') as f:
        for label, path, j in todo:
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
    print('done', name, len(todo))
