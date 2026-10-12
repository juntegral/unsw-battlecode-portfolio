"""Scratch (diag-topaah): every turn of the studied side (side 0) that starts with a pearl beside the head, rounds 101+.
Row = [round, length, queen, mover is the side's longest, longest length, tiles mover-to-longest head, tiles pearl-to-longest head,
       own dragons alive, origin (0 natural, 1 own dead, 2 their dead), enemy head within 2 of the pearl, room behind the pearl (cap 20),
       action (0 ate it, 1 split, 2 stepped elsewhere, 3 died), cells, turns since the mover last ate or was born]
Fate row (first time a pearl is declined) = [round, tiles pearl-to-longest, mover-to-longest, longest length, origin, feeder-like, fate, wait]
  fate: 0 eaten by the side's longest, 1 by the decliner, 2 by another mate, 3 by the enemy, 4 nobody by game end.
Usage: python3 ta_s3.py <tag> [limit]   tags a l c1 g q m t"""
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
    adj = [[dest for kind, dest in row if kind != 1] for row in moves]
    fteam = 0 if meta['a'] == focus else 1
    side = lambda i: 0 if teams[i] == fteam else 1
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]

    def tman(a, b):
        ay, ax = divmod(a, w)
        by, bx = divmod(b, w)
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, w - dx) + min(dy, h - dy)

    occ = {}
    for i, b in bodies.items():
        for x in b:
            occ[x] = i
    pearls = {}
    dropinfo = {}
    lastfed = {i: 0 for i in bodies}
    nturn = {i: 0 for i in bodies}
    rows, fates = [], []
    rnd, actor = 0, None
    cur = None
    akind = 2
    longest_cache = [-1, None]

    def longest0():
        if longest_cache[0] != rnd:
            best = None
            for i, b in bodies.items():
                if side(i) == 0 and (best is None or len(b) > len(bodies[best])):
                    best = i
            longest_cache[0], longest_cache[1] = rnd, best
        j = longest_cache[1]
        if j is None or j not in bodies:
            best = None
            for i, b in bodies.items():
                if side(i) == 0 and (best is None or len(b) > len(bodies[best])):
                    best = i
            longest_cache[1] = j = best
        return j

    def room(start, mover):
        seen = {start}
        todo = deque([start])
        while todo and len(seen) < 21:
            c = todo.popleft()
            for t in adj[c]:
                if t not in seen and (t not in occ or occ[t] == mover):
                    seen.add(t)
                    todo.append(t)
        return min(len(seen) - 1, 20)

    def close():
        nonlocal cur
        if cur is None:
            return
        row, tiles, mover = cur
        if mover not in bodies:
            row[11] = 3
        elif any(pearls.get(t) is None or pearls[t]['id'] != pid for t, pid in tiles) and row[11] == 2 and row[14]:
            row[11] = 0
        rows.append(row[:14])
        if row[11] != 0:
            for t, pid in tiles:
                pr = pearls.get(t)
                if pr is not None and pr['id'] == pid and pr['dec'] is None:
                    feeder = int((row[0] > 400 or (row[0] > 200 and row[7] >= 56)) and row[5] <= 15 and row[1] * 2 <= row[4] and not row[2] and not row[3])
                    pr['dec'] = [row[0], row[6], row[5], row[4], row[8], feeder, mover]
        cur = None

    pid_next = 0
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            close()
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            akind = 2
            nturn[actor] = nturn.get(actor, 0) + 1
            if rnd > 100 and side(actor) == 0:
                b = bodies[actor]
                head = b[0]
                near = [t for t in adj[head] if t in pearls]
                if near:
                    lead = longest0()
                    lh = bodies[lead][0]
                    L = len(b)
                    best = min(near, key=lambda t: tman(t, lh))
                    alive = sum(1 for i in bodies if side(i) == 0)
                    foe = any(side(i) == 1 and tman(bb[0], best) <= 2 for i, bb in bodies.items())
                    pr = pearls[best]
                    origin = 0 if pr['o'] < 0 else 1 if pr['o'] == 0 else 2
                    row = [rnd, L, int(actor == queens[0]), int(actor == lead), len(bodies[lead]), tman(head, lh), tman(best, lh), alive,
                           origin, int(foe), room(best, actor), 2, w * h, nturn[actor] - lastfed.get(actor, 0), False]
                    cur = (row, [(t, pearls[t]['id']) for t in near], actor)
        elif k == 4:
            a = p.pointer(0)
            akind = a.u16(0) if a else 2
            if cur is not None and akind == 1:
                cur[0][11] = 1
        elif k == 3:
            pt = replay.point(p.pointer(0))
            t = pt[1] * w + pt[0]
            if p.u32(0):
                info = dropinfo.pop(t, None)
                pearls[t] = dict(id=pid_next, o=-1 if info is None else info, born=rnd, dec=None)
                pid_next += 1
            else:
                pr = pearls.pop(t)
                lastfed[actor] = nturn.get(actor, 0)
                if cur is not None and cur[2] == actor and any(pid == pr['id'] for tt, pid in cur[1]):
                    cur[0][14] = True
                    cur[0][11] = 0
                if pr['dec'] is not None:
                    d = pr['dec']
                    s = side(actor)
                    fate = 3 if s == 1 else 0 if actor == longest0() else 1 if actor == d[6] else 2
                    fates.append(d[:6] + [fate, rnd - d[0]])
        elif k == 9:
            i = p.i32(0)
            a, z = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = a[1] * w + a[0], z[1] * w + z[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                occ[hd] = i
            while len(b) > 1 and b[-1] != tl:
                x = b.pop()
                if occ.get(x) == i:
                    del occ[x]
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for x in bodies[parent]:
                occ.pop(x, None)
            bodies[parent] = deque(c[1] * w + c[0] for c in (replay.point(z) for z in p.pointer(0)))
            bodies[child] = deque(c[1] * w + c[0] for c in (replay.point(z) for z in p.pointer(1)))
            teams[child] = p.u16(8)
            for i in (parent, child):
                for x in bodies[i]:
                    occ[x] = i
            nturn[child] = 0
            lastfed[child] = 0
        elif k == 11:
            i = p.i32(0)
            s = side(i)
            for seg, x in enumerate(bodies[i]):
                if occ.get(x) == i:
                    del occ[x]
                if seg % 2 == 0:
                    dropinfo[x] = s
            bodies.pop(i)
    close()
    for t, pr in pearls.items():
        if pr['dec'] is not None:
            d = pr['dec']
            fates.append(d[:6] + [4, rnd - d[0]])
    return dict(gid=meta['gid'], map=meta['map'], cells=w * h, last=rnd, rows=rows, fates=fates)


def pick(tag):
    rows = [json.loads(x) for x in Path(WORK + 'ta_index.jsonl').read_text().splitlines()]
    def sel(src, team):
        return [(r, team) for r in rows if src in r['src'] and team in (r['a'], r['b'])]
    if tag == 'a':
        return sel('online/top3', 454)
    if tag == 'l':
        return sel('online/top3', 157)
    if tag == 'c1':
        return sel('online/top3', 306)
    if tag == 'g':
        return sel('online/top3', 70)
    if tag == 'q':
        return sel('agg8-q1-new', 1119)
    if tag == 'm':
        return sel('agg7-m', 1119)
    if tag == 't':
        return sel('smoke/top-l', 1119)
    return []


def save(tag, body):
    if tag == 'a':
        Path(WORK + 'ta_s3-a.jsonl').write_text(body)
    elif tag == 'l':
        Path(WORK + 'ta_s3-l.jsonl').write_text(body)
    elif tag == 'c1':
        Path(WORK + 'ta_s3-c1.jsonl').write_text(body)
    elif tag == 'g':
        Path(WORK + 'ta_s3-g.jsonl').write_text(body)
    elif tag == 'q':
        Path(WORK + 'ta_s3-q.jsonl').write_text(body)
    elif tag == 'm':
        Path(WORK + 'ta_s3-m.jsonl').write_text(body)
    elif tag == 't':
        Path(WORK + 'ta_s3-t.jsonl').write_text(body)


def main():
    tag = sys.argv[1]
    todo = pick(tag)
    if len(sys.argv) > 2:
        todo = todo[:int(sys.argv[2])]
    out = []
    for n, (r, team) in enumerate(todo):
        try:
            out.append(json.dumps(process(Path(r['path']), r, team), separators=(',', ':')))
        except Exception as e:
            print('FAILED', r['gid'], type(e).__name__, e, flush=True)
    save(tag, '\n'.join(out) + '\n')
    print(tag, 'done', len(out))


main()
