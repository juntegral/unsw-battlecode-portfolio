"""Scratch (diag-one1, job B): every natural pearl born in rounds 0-100: free-path steps from it to the nearest head
of each side at birth (cap 12), who eats it and when (watched to round 140), and the eater's steps in that turn.
Also per side: unit count every round to 100, split events (round, parent length before, queen), first-eat rounds.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_pearl.py <set>"""
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
    start = [[len(b) for i, b in sorted(bodies.items()) if side(i) == s] for s in (0, 1)]

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

    def nearest(c):
        occ = set()
        heads = {}
        for z, bb in bodies.items():
            occ.update(bb)
            heads[bb[0]] = side(z)
        best = [99, 99]
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
                    s = heads[n]
                    if best[s] == 99:
                        best[s] = seen[x] + 1
                    continue
                if n in occ:
                    continue
                seen[n] = seen[x] + 1
                qu.append(n)
            if best[0] < 99 and best[1] < 99:
                break
        return best

    recs = []            # [birth round, d ours, d theirs, eater side (-1 none), eat round, eater steps that turn, eater length, eater is queen]
    live = {}
    units = [[], []]
    splits = []
    rnd, actor, used = -1, None, 0
    expected = 0
    pending = []
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1) and pending:
            for c in pending:
                if c in live:
                    b = nearest(c)
                    live[c][1], live[c][2] = b[0], b[1]
            pending = []
        if k == 0:
            if 0 <= rnd <= 100:
                for s in (0, 1):
                    units[s].append(sum(1 for i in bodies if side(i) == s))
            rnd, actor = p.i32(0), None
            if rnd > 140:
                break
        elif k == 1:
            actor, used = p.i32(0), 0
            L0 = len(bodies[actor])
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if expected:
                    expected -= 1
                    live[c] = None
                elif rnd <= 100:
                    rec = [max(rnd, 0), 99, 99, -1, -1, 0, 0, 0]
                    live[c] = rec
                    recs.append(rec)
                    pending.append(c)
                else:
                    live[c] = None
            else:
                rec = live.pop(c)
                if rec is not None:
                    s = side(actor)
                    rec[3], rec[4], rec[5], rec[6], rec[7] = s, rnd, used, L0, int(actor == queens[s])
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            Lb = len(bodies[parent])
            sp = side(parent)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if rnd <= 100:
                splits.append([rnd, sp, Lb, len(bodies[child]), int(parent == queens[sp])])
        elif k == 11:
            i = p.i32(0)
            expected = (len(bodies[i]) + 1) // 2
            bodies.pop(i)
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=cells,
                opp=j['team' + 'AB'[1 - own] + 'Name'], start=start, units=units, splits=splits, pearls=recs)


if __name__ == '__main__':
    name = sys.argv[1]
    todo = jobs(name)
    with open(OUT + 'o1_pearl-%s.jsonl' % name, 'w') as f:
        for label, path, j in todo:
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
    print('done', name, len(todo))
