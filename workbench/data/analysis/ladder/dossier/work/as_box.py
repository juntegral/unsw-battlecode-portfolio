"""Scratch (diag-aahsplit): every turn a dragon of 4+ of the studied side starts with no free tile beside its head:
what stands on each of the four sides, what it does, and who is alive 3 rounds later.
Usage: python3 as_box.py <tag> [limit]   tags a l q m"""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def geo(w, h, raw):
    edges = canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    moves = []
    for y in range(h):
        for x in range(w):
            row = []
            for d in range(4):
                dx, dy = STEP[d]
                e = edge_id(w, h, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                else:
                    dest = ((y + dy) % h) * w + (x + dx) % w
                row.append((kind, dest))
            moves.append(row)
    return moves


def process(path, meta, focus):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    w, h = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    moves = geo(w, h, raw)
    fteam = 0 if meta['a'] == focus else 1
    queen = min(i for i in bodies if teams[i] == fteam)
    occ = {}
    for i, b in bodies.items():
        for t in b:
            occ[t] = i
    out = []
    watch = {}
    rnd, actor = 0, None
    cur = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            cur = None
            if teams[actor] == fteam:
                b = bodies[actor]
                L = len(b)
                if L >= 4:
                    sides = []
                    free = 0
                    for kind, dest in moves[b[0]]:
                        if kind == 1:
                            sides.append([0, 0, 0])
                            continue
                        o = occ.get(dest)
                        if o is None:
                            free += 1
                            break
                        ob = bodies[o]
                        idx = len(ob) - 1 - list(ob).index(dest)      # 0 = tail tip
                        sides.append([1 if o == actor else 2 if teams[o] == fteam else 3, idx, len(ob)])
                    if not free:
                        cur = [rnd, actor, L, sum(1 for j in bodies if teams[j] == fteam), int(actor == queen), 0, 0, sides, 0, 0]
                        out.append(cur)
        elif k == 9:
            i = p.i32(0)
            a, z = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = a[1] * w + a[0], z[1] * w + z[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                occ[hd] = i
            while len(b) > 1 and b[-1] != tl:
                t = b.pop()
                if occ.get(t) == i and t not in b:
                    del occ[t]
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            bodies[parent] = deque(c[1] * w + c[0] for c in (replay.point(z) for z in p.pointer(0)))
            bodies[child] = deque(c[1] * w + c[0] for c in (replay.point(z) for z in p.pointer(1)))
            teams[child] = p.u16(8)
            for t in bodies[child]:
                occ[t] = child
            if cur is not None and parent == actor:
                cur[5] = len(bodies[child])
                watch[parent] = (cur, 8)
                watch[child] = (cur, 9)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if cur is not None and i == actor:
                cur[6] = reason + 1
            z = watch.get(i)
            if z is not None and rnd - z[0][0] <= 3:
                z[0][z[1]] = 1
            for t in bodies[i]:
                if occ.get(t) == i:
                    del occ[t]
            bodies.pop(i)
    return dict(gid=meta['gid'], map=meta['map'], rows=out)


def pick(tag):
    rows = [json.loads(x) for x in Path(WORK + 'as_index.jsonl').read_text().splitlines()]

    def sel(src, team):
        return [(r, team) for r in rows if src in r['src'] and team in (r['a'], r['b'])]
    if tag == 'a':
        return sel('online/top3', 454)
    if tag == 'l':
        return sel('online/top3', 157)
    if tag == 'q':
        return sel('agg8-q1-new', 1119)
    if tag == 'm':
        return sel('agg7-m', 1119)
    return []


def main():
    tag = sys.argv[1]
    todo = pick(tag)
    test = len(sys.argv) > 2
    if test:
        todo = todo[:int(sys.argv[2])]
    out = []
    for r, team in todo:
        try:
            out.append(json.dumps(process(Path(r['path']), r, team), separators=(',', ':')))
        except Exception as e:
            print('FAILED', r['gid'], type(e).__name__, e, flush=True)
    body = '\n'.join(out) + '\n'
    if test:
        Path(WORK + 'as_box-test.jsonl').write_text(body)
    elif tag == 'a':
        Path(WORK + 'as_box-a.jsonl').write_text(body)
    elif tag == 'l':
        Path(WORK + 'as_box-l.jsonl').write_text(body)
    elif tag == 'q':
        Path(WORK + 'as_box-q.jsonl').write_text(body)
    elif tag == 'm':
        Path(WORK + 'as_box-m.jsonl').write_text(body)
    print(tag, 'done', len(out), flush=True)


main()
