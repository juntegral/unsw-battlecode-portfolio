"""Scratch (diag-aahsplit): every split, every turn of a dragon of 4 or longer, steps per turn, deaths by length,
and the count/length timeline. Side 0 = the studied team.
Usage: python3 as_scan.py <tag> [limit]   tags: a (aAah fresh) a0 (aAah to 5 Oct) l (larp) c1 (Cutlery fresh) g (chad gdp)
       q (ours B7Q) m (ours main) t (ours live v top) cs (every 6th Cutlery to 5 Oct)"""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
MARKS = (10, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300)


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


def band(r):
    return 0 if r <= 20 else 1 if r <= 60 else 2 if r <= 150 else 3 if r <= 300 else 4


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

    def side(i):
        return 0 if teams[i] == fteam else 1

    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    starters = sorted(len(b) for i, b in bodies.items() if side(i) == 0)
    occ = {}
    for i, b in bodies.items():
        for t in b:
            occ[t] = i
    pearls = set()
    st = {i: [0, 0, 0] for i in bodies if side(i) == 0}   # born round, pearls since birth/split, turns at this length

    def tman(a, b):
        ay, ax = divmod(a, w)
        by, bx = divmod(b, w)
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, w - dx) + min(dy, h - dy)

    def free(t):
        n = 0
        for kind, dest in moves[t]:
            if kind != 1 and dest not in occ:
                n += 1
        return n

    def near(t, s, cap):
        best = cap
        for i, b in bodies.items():
            if side(i) == s:
                d = tman(b[0], t)
                if d < best:
                    best = d
        return best

    def pearl_bfs(start):
        """(steps to the nearest pearl, 7 = none within 6; pearls within 3 steps); bodies block."""
        seen = {start}
        frontier = [start]
        pd, n3 = 7, 0
        for depth in range(1, 7):
            nxt = []
            for t in frontier:
                for kind, dest in moves[t]:
                    if kind == 1 or dest in seen or dest in occ:
                        continue
                    seen.add(dest)
                    nxt.append(dest)
                    if dest in pearls:
                        if pd == 7:
                            pd = depth
                        if depth <= 3:
                            n3 += 1
            if pd < 7 and depth >= 3:
                break
            frontier = nxt
            if not frontier:
                break
        return pd, n3

    T = Counter()
    SP = Counter()
    marks = {}
    hist = {}
    rams = []
    splits = []
    rows = []
    split_of = {}
    rnd, actor, W = 0, None, 0
    dirs, used, nsteps, akind = [], 0, 0, 2
    cur = None
    turn_deaths = []
    started = False

    def snap():
        out = []
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if side(i) == s]
            q = bodies.get(queens[s])
            out.append([len(ls), sum(ls), sum(1 for x in ls if 5 <= x <= 8), sum(1 for x in ls if x >= 6), max(ls, default=0),
                        sum(1 for x in ls if x == 4), sum(1 for x in ls if x >= 9), len(q) if q else 0])
        return out

    def flood(start, cap):
        seen = {start}
        frontier = [start]
        n = 0
        while frontier and n < cap:
            nxt = []
            for t in frontier:
                for kind, dest in moves[t]:
                    if kind == 1 or dest in seen or dest in occ:
                        continue
                    seen.add(dest)
                    nxt.append(dest)
                    n += 1
            frontier = nxt
        return min(n, cap)

    def feats(i):
        b = bodies[i]
        hd, tl = b[0], b[-1]
        pd, n3 = pearl_bfs(hd)
        oh = sum(1 for j, bb in bodies.items() if j != i and side(j) == 0 and tman(bb[0], hd) <= 3)
        return [free(tl), near(hd, 1, 9), near(tl, 1, 9), pd, n3, oh]

    def extra(i):
        b = bodies[i]
        hd, tl = b[0], b[-1]
        ea = sum(1 for j in bodies if side(j) == 1)
        tot = sum(len(bb) for j, bb in bodies.items() if side(j) == 0)
        tport = int(any(kind == 2 for kind, dest in moves[tl])) + 2 * int(any(kind == 2 for kind, dest in moves[b[-2]]))
        hport = int(any(kind == 2 for kind, dest in moves[hd]))
        return [flood(hd, 24), flood(tl, 24), pearl_bfs(tl)[0], tport, ea, tot, hport, tman(hd, tl)]

    def close_turn():
        nonlocal cur
        hs = [d for d in turn_deaths if d[2] == 3]
        if len(hs) == 2:
            mv = [d for d in hs if d[0] == actor][0]
            ht = [d for d in hs if d[0] != actor][0]
            if mv[1] != ht[1]:
                rams.append([rnd, mv[1], mv[3], ht[3], nsteps, max(0, nsteps - (mv[3] + 3) // 4), int(ht[4]), int(mv[4])])
                if ht[1] == 0:
                    T['%d|%d|dv' % (W, min(ht[3], 13))] += 1
                if cur is not None:
                    cur['ram'] = 1
            elif ht[1] == 0:
                T['%d|%d|dvs' % (W, min(ht[3], 13))] += 1
        turn_deaths.clear()
        if cur is None:
            return
        c = cur
        cur = None
        i, L, fh = c['i'], c['L'], c['fh']
        Lc = min(L, 13)
        key = '%d|%d|' % (W, Lc)
        n = nsteps
        T[key + 't'] += 1
        T[key + 'n%d' % min(n, 4)] += 1
        T[key + 'e'] += len(c['eat'])
        T[key + 'e2'] += int(len(c['eat']) >= 2)
        T[key + 'fh0'] += int(fh == 0)
        freeN = (L + 3) // 4
        if n > freeN:
            T[key + 'paid'] += n - freeN
            T[key + 'paidt'] += 1
        died = c['died']
        if died >= 0:
            T[key + 'da%d' % died] += 1
            T[key + 'dab'] += int(fh == 0)
            if died == 2:
                T[key + ('da2e' if c['hit_enemy'] else 'da2o')] += 1
            if died == 3:
                T[key + ('da3e' if c['ram'] else 'da3o')] += 1
        if c['split']:
            T[key + 'sp'] += 1
        elif akind == 1:
            T[key + 'isp'] += 1
        if n >= 2:
            G = 0 if L <= 3 else 1 if L == 4 else 2 if L <= 8 else 3 if L <= 12 else 4
            f = c['f']
            if f is None:
                f = feats_pre
            ed, pd = f[1], f[3]
            eat = c['eat']
            alive = i in bodies
            if alive:
                hd = bodies[i][0]
                ed2 = near(hd, 1, 9)
                pd2 = pearl_bfs(hd)[0]
            else:
                ed2, pd2 = 9, 7
            if died == 3 and c['ram']:
                cat = 'ram'
            elif died >= 0:
                cat = 'die'
            elif len(eat) >= 2:
                cat = 'eat2'
            elif eat and eat[-1] == n:
                cat = 'endp'
            elif eat:
                cat = 'eatgo'
            elif ed <= 3 and ed2 > ed:
                cat = 'esc'
            elif ed <= 5 and ed2 < ed:
                cat = 'app'
            elif pd <= 6 and pd2 < pd:
                cat = 'topearl'
            elif pd > 6 and pd2 <= 6:
                cat = 'found'
            else:
                cat = 'plain'
            sk = '%d|%d|%d|' % (W, G, int(n > freeN))
            SP[sk + 'n'] += 1
            SP[sk + cat] += 1
            SP[sk + 'straight'] += int(len(set(dirs)) == 1)
            if alive:
                SP[sk + 'endpearl'] += int(bool(eat) and eat[-1] == n)
                SP[sk + 'pd2_1'] += int(pd2 == 1)
                if ed <= 3:
                    SP[sk + 'ednear'] += 1
                    SP[sk + ('edup' if ed2 > ed else 'eddown' if ed2 < ed else 'edsame')] += 1
                if pd == 2 and eat and eat[-1] == n and len(eat) == 1:
                    SP[sk + 'pd2eat'] += 1
        s = st.get(i)
        if L >= 4:
            f = c['f']
            rows.append([rnd, i, L, c['alive'], int(i == queens[0]), c['lng'], fh] + f + [s[2], s[1], rnd - s[0],
                        c['split'] if c['split'] else (-1 if akind == 1 else 0), n, len(c['eat']), died + 1] + c['x'])
        if i in bodies:
            s[1] += len(c['eat'])
            if c['split']:
                s[1] = 0
            s[2] = s[2] + 1 if len(bodies[i]) == L else 0

    feats_pre = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            close_turn()
        if k == 0:
            if started:
                if rnd in MARKS:
                    marks[str(rnd)] = snap()
                if rnd in (60, 100, 200):
                    hist[str(rnd)] = dict(Counter(min(len(b), 20) for i, b in bodies.items() if side(i) == 0))
            started = True
            rnd, actor = p.i32(0), None
            W = band(rnd)
        elif k == 1:
            actor = p.i32(0)
            dirs, used, nsteps, akind = [], 0, 0, 2
            if side(actor) == 0:
                b = bodies[actor]
                L = len(b)
                ls = [len(bb) for j, bb in bodies.items() if side(j) == 0]
                mx = max(ls)
                cur = dict(i=actor, L=L, fh=free(b[0]), alive=len(ls), lng=2 if (L == mx and ls.count(mx) == 1) else 1 if L == mx else 0,
                           f=feats(actor) if L >= 4 else None, x=extra(actor) if L >= 4 else None, eat=[], died=-1, split=0, ram=0, hit_enemy=0)
            else:
                cur = None
        elif k == 4:
            a = p.pointer(0)
            akind = a.u16(0) if a else 2
            dirs = list(a.pointer(0)) if a and akind == 0 and a.pointer(0) is not None else []
            nsteps = len(dirs)
            if cur is not None and nsteps >= 2 and cur['f'] is None:
                feats_pre = feats(actor)
        elif k == 3:
            pt = replay.point(p.pointer(0))
            t = pt[1] * w + pt[0]
            if p.u32(0):
                pearls.add(t)
            else:
                pearls.discard(t)
                if cur is not None:
                    cur['eat'].append(used + 1)
        elif k == 9:
            i = p.i32(0)
            a, z = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = a[1] * w + a[0], z[1] * w + z[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                occ[hd] = i
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                t = b.pop()
                if occ.get(t) == i and t not in b:
                    del occ[t]
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = side(parent)
            lp = len(bodies[parent])
            old = bodies[parent]
            bodies[parent] = deque(c[1] * w + c[0] for c in (replay.point(z) for z in p.pointer(0)))
            bodies[child] = deque(c[1] * w + c[0] for c in (replay.point(z) for z in p.pointer(1)))
            teams[child] = p.u16(8)
            for t in bodies[child]:
                occ[t] = child
            if s == 0:
                st[child] = [rnd, 0, 0]
                keeps_head = int(bodies[parent][0] == old[0])
                child_head_is_old_tail = int(bodies[child][0] == old[-1])
                if cur is not None and parent == actor:
                    cur['split'] = len(bodies[child])
                    f = cur['f'] if cur['f'] is not None else [0, 9, 9, 7, 0, 0]
                    sx = st[parent]
                    splits.append([rnd, parent, lp, len(bodies[child]), len(bodies[parent]), cur['alive'], int(parent == queens[0]),
                                   cur['lng'], cur['fh']] + f + [sx[2], sx[1], rnd - sx[0], keeps_head, child_head_is_old_tail, 0, 0] + (cur['x'] or []))
                    split_of[parent] = (len(splits) - 1, 20)
                    split_of[child] = (len(splits) - 1, 21)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            b = bodies[i]
            L = len(b)
            turn_deaths.append((i, s, reason, L, int(i == queens[s])))
            if s == 0:
                T['%d|%d|ll' % (W, min(L, 13))] += L
                T['%d|%d|d' % (W, min(L, 13))] += 1
                z = split_of.get(i)
                if z is not None and rnd - splits[z[0]][0] <= 3:
                    splits[z[0]][z[1]] = 1
            if i == actor and reason == 2 and used < len(dirs):
                kind, dest = moves[b[0]][dirs[used]]
                owner = occ.get(dest)
                if owner is not None and owner != i and owner in bodies:
                    if side(owner) != s:
                        if cur is not None:
                            cur['hit_enemy'] = 1
                        if side(owner) == 0:
                            T['%d|%d|kb' % (W, min(len(bodies[owner]), 13))] += 1
            if cur is not None and i == actor:
                cur['died'] = reason
            for t in b:
                if occ.get(t) == i:
                    del occ[t]
            bodies.pop(i)
    close_turn()
    marks['end'] = snap()
    won = int((meta['win'] == 'a') == (meta['a'] == focus)) if meta['win'] in ('a', 'b') else -1
    return dict(gid=meta['gid'], map=meta['map'], w=w, h=h, won=won, last=rnd, starters=starters, marks=marks, hist=hist,
                T=dict(T), SP=dict(SP), rams=rams, splits=splits, rows=rows,
                opp=meta['b'] if meta['a'] == focus else meta['a'], oppelo=meta['be'] if meta['a'] == focus else meta['ae'])


def pick(tag):
    rows = [json.loads(x) for x in Path(WORK + 'as_index.jsonl').read_text().splitlines()]

    def sel(src, team):
        return [(r, team) for r in rows if src in r['src'] and team in (r['a'], r['b'])]
    if tag == 'a':
        return sel('online/top3', 454)
    if tag == 'a0':
        return sel('online/top1', 454)
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
    if tag == 'cs':
        return [x for z, x in enumerate(sel('online/top1', 306)) if z % 6 == 0]
    return []


def save(tag, body):
    if tag == 'a':
        Path(WORK + 'as_scan-a.jsonl').write_text(body)
    elif tag == 'a0':
        Path(WORK + 'as_scan-a0.jsonl').write_text(body)
    elif tag == 'l':
        Path(WORK + 'as_scan-l.jsonl').write_text(body)
    elif tag == 'c1':
        Path(WORK + 'as_scan-c1.jsonl').write_text(body)
    elif tag == 'g':
        Path(WORK + 'as_scan-g.jsonl').write_text(body)
    elif tag == 'q':
        Path(WORK + 'as_scan-q.jsonl').write_text(body)
    elif tag == 'm':
        Path(WORK + 'as_scan-m.jsonl').write_text(body)
    elif tag == 't':
        Path(WORK + 'as_scan-t.jsonl').write_text(body)
    elif tag == 'cs':
        Path(WORK + 'as_scan-cs.jsonl').write_text(body)
    else:
        Path(WORK + 'as_scan-test.jsonl').write_text(body)


def main():
    tag = sys.argv[1]
    todo = pick(tag)
    test = len(sys.argv) > 2
    if test:
        todo = todo[:int(sys.argv[2])]
    out = []
    for n, (r, team) in enumerate(todo):
        try:
            out.append(json.dumps(process(Path(r['path']), r, team), separators=(',', ':')))
        except Exception as e:
            print('FAILED', r['gid'], type(e).__name__, e, flush=True)
    save('test' if test else tag, '\n'.join(out) + '\n')
    print(tag, 'done', len(out), flush=True)


main()
