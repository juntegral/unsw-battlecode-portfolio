"""Scratch (diag-one1): first strike. Every turn of a non-queen dragon of 2 to 4 that starts with an enemy head inside its
ram reach (free steps + length - 2, capped at 4, 3 on 1200 cells or fewer; path over free tiles), for both sides:
did it ram, which of our gates were open (local edge, parts >= length, units), and was it rammed before its next turn.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_strike.py <set>"""
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

    def reach_heads(h, R, occ, heads):
        seen = {h: 0}
        qu = deque([h])
        found = {}
        while qu:
            c = qu.popleft()
            if seen[c] >= R:
                continue
            for d in range(4):
                n = dest(c, d)
                if n is None or n in seen:
                    continue
                if n in heads:
                    if heads[n] not in found:
                        found[heads[n]] = seen[c] + 1
                    continue
                if n in occ:
                    continue
                seen[n] = seen[c] + 1
                qu.append(n)
        return found

    rows = []
    open_rec = {}
    rnd, actor, cur = -1, None, None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor, cur = p.i32(0), None, None
        elif k == 1:
            actor = p.i32(0)
            cur = None
            open_rec.pop(actor, None)
            s = side(actor)
            b = bodies[actor]
            L = len(b)
            if actor == queens[s] or L > 4:
                continue
            h = b[0]
            R = min(4 if cells > 1200 else 3, (L + 3) // 4 + L - 2)
            near = False
            for z, bb in bodies.items():
                if side(z) != s:
                    dx = abs(bb[0][0] - h[0]); dy = abs(bb[0][1] - h[1])
                    if min(dx, W - dx) + min(dy, H - dy) <= 6:
                        near = True
                        break
            if not near and not portals:
                continue
            occ = set()
            for bb in bodies.values():
                occ.update(bb)
            heads = {bb[0]: z for z, bb in bodies.items() if side(z) != s}
            found = reach_heads(h, R, occ, heads)
            if not found:
                continue
            allies = sum(1 for z, bb in bodies.items() if side(z) == s and z != actor and inview(h, bb[0]))
            foes = sum(1 for z, bb in bodies.items() if side(z) != s and inview(h, bb[0]))
            units = sum(1 for z in bodies if side(z) == s)
            tg = []
            for z, st in found.items():
                bb = bodies[z]
                parts = sum(1 for c in bb if inview(h, c))
                tg.append([st, len(bb), parts, int(z == queens[1 - s]), z])
            tg.sort()
            cur = dict(r=rnd, s=s, i=actor, L=L, R=R, allies=allies, foes=foes, units=units, tg=tg, ram=0, ramL=0, ramst=0,
                       after='alive', by=-1, byin=0)
            rows.append(cur)
            open_rec[actor] = cur
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
            if reason == 3 and i != actor and side(i) != side(actor):
                if cur is not None:
                    cur['ram'] = 1
                    cur['ramL'] = len(bodies[i])
                    cur['ramst'] = next((t[0] for t in cur['tg'] if t[4] == i), 0)
                rec = open_rec.pop(i, None)
                if rec is not None:
                    rec['after'] = 'rammed'
                    rec['by'] = actor
                    rec['byin'] = int(any(t[4] == actor for t in rec['tg']))
            elif i != actor or reason != 3:
                rec = open_rec.pop(i, None)
                if rec is not None and rec is not cur:
                    rec['after'] = 'died other'
                elif rec is not None:
                    rec['after'] = 'died own move'
            bodies.pop(i)
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=cells, rows=rows)


if __name__ == '__main__':
    name = sys.argv[1]
    todo = jobs(name)
    with open(OUT + 'o1_strike-%s.jsonl' % name, 'w') as f:
        for label, path, j in todo:
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
    print('done', name, len(todo))
