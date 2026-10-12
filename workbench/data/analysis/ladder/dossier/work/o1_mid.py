"""Scratch (diag-one1, job B): rounds 0-100, every dragon turn of both sides put in one class:
eat / split / died / blind (no pearl in the 7 by 7) / walled (pearls in view, none within 7 free steps) /
mate (a mate is nearer to every reachable pearl) / approach (ends nearer its nearest own pearl) / away (does not).
For away and blind turns a few board facts. One json row a game with counters keyed by (side, window, class...).
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_early.py <set>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from o1_scan import jobs, OUT, STEP
LAST = 300


def wnd(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2


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
    start_units = [sum(1 for i in bodies if side(i) == s) for s in (0, 1)]
    starts = [[bb[0] for i, bb in bodies.items() if side(i) == s] for s in (0, 1)]
    start_len = [sum(len(b) for i, b in bodies.items() if side(i) == s) for s in (0, 1)]

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

    def flood(h, R, occ):
        seen = {h: 0}
        qu = deque([h])
        while qu:
            c = qu.popleft()
            if seen[c] >= R:
                continue
            for d in range(4):
                n = dest(c, d)
                if n is None or n in seen or n in occ:
                    continue
                seen[n] = seen[c] + 1
                qu.append(n)
        return seen

    def exits(c, occ, frm):
        n = 0
        for d in range(4):
            t = dest(c, d)
            if t is not None and t not in occ and t != frm:
                n += 1
        return n

    C = Counter()
    pearls = {}          # cell -> birth round (None = natural at start), origin
    trail = defaultdict(lambda: deque(maxlen=12))
    rnd, actor, cur = -1, None, None
    expected = 0
    snaps = {}

    def close():
        nonlocal cur
        if cur is None:
            return
        s, w = cur['s'], wnd(cur['r'])
        i = cur['i']
        key = None
        if cur['ate']:
            key = 'eat'
        elif cur['died']:
            key = 'died'
        elif cur['split']:
            key = 'split'
        else:
            h1 = bodies[i][0]
            if cur['cls'] == 'own':
                occ = set()
                for bb in bodies.values():
                    occ.update(bb)
                d1 = flood(h1, 8, occ - {h1}).get(cur['tgt'], 99)
                if d1 < cur['d']:
                    key = 'approach'
                else:
                    key = 'away'
                    reason = 'beside, not taken' if cur['d'] == 1 else 'enemy head near' if cur['foe'] else 'dead end' if cur['exits'] == 0 else 'tie with a mate' if cur['tie'] else 'other'
                    C[(s, w, 'away:' + reason)] += 1
                    C[(s, w, 'away d%d' % min(cur['d'], 4))] += 1
            else:
                key = cur['cls']
                if key == 'blind':
                    C[(s, w, 'blind:retread' if h1 in cur['trail'] else 'blind:new tile')] += 1
                    C[(s, w, 'blind:mates in view %d' % min(cur['mates'], 2))] += 1
        if cur.get('d1ctx') and key in ('eat', 'away', 'approach'):
            C[(s, w, 'D1 %s | %s' % ('taken    ' if key == 'eat' else 'not taken', cur['d1ctx']))] += 1
            C[(s, w, 'D1 %s | %s' % ('taken    ' if key == 'eat' else 'not taken', 'portal in view' if cur['d1port'] else 'no portal in view'))] += 1
        C[(s, w, key)] += 1
        C[(s, w, 'turns')] += 1
        C[(s, w, 'turns L%s' % (cur['L'] if cur['L'] < 5 else '5+'))] += 1
        if cur['q']:
            C[(s, w, 'q:' + key)] += 1
            if cur['L'] >= 4:
                C[(s, w, 'Q4+ turns')] += 1
                C[(s, w, 'Q4+ ' + ('split' if key == 'split' else 'no split'))] += 1
        elif cur['L'] >= 4:
            C[(s, w, 'O4+ turns')] += 1
            C[(s, w, 'O4+ ' + ('split' if key == 'split' else 'no split: ' + ('eat' if key == 'eat' else 'died' if key == 'died' else 'move')))] += 1
            if key != 'split':
                C[(s, w, 'O4+ no split L%s' % (cur['L'] if cur['L'] < 6 else '6+'))] += 1
            C[(s, w, 'O4+ %s | %s' % ('split   ' if key == 'split' else 'no split', cur.get('tailfact', '?')))] += 1
        if key in ('eat', 'approach', 'away', 'mate', 'walled'):
            C[(s, w, 'pearl in view')] += 1
        if i in bodies:
            trail[i].append(cur['h0'])
        cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            if rnd >= 0 and rnd % 10 == 0:
                snaps[rnd] = [[sum(1 for i in bodies if side(i) == s), sum(len(b) for i, b in bodies.items() if side(i) == s)] for s in (0, 1)]
            rnd, actor = p.i32(0), None
            if rnd > LAST:
                break
        elif k == 1:
            close()
            actor = p.i32(0)
            s = side(actor)
            b = bodies[actor]
            h = b[0]
            L = len(b)
            cur = dict(i=actor, s=s, r=rnd, L=L, h0=h, ate=0, died=0, split=0, q=int(actor == queens[s]), trail=set(trail[actor]),
                       mates=sum(1 for z, bb in bodies.items() if z != actor and side(z) == s and inview(h, bb[0])))
            C[(s, wnd(rnd), 'foe head in view')] += int(any(side(z) != s and inview(h, bb[0]) for z, bb in bodies.items()))
            ds = [min(gap(h, x) for x in starts[k]) for k in (0, 1)]
            C[(s, wnd(rnd), 'on the other side of the board')] += int(ds[1 - s] < ds[s])
            if actor != queens[s] and L >= 4:
                tail = b[-1]
                occ0 = set()
                for bb in bodies.values():
                    occ0.update(bb)
                ex = 0
                port = 0
                for d in range(4):
                    e = edge_id(W, H, tail[0], tail[1], d)
                    if edges.get(e, (0, -1))[0] == 2:
                        port = 1
                    t = dest(tail, d)
                    if t is not None and t not in occ0:
                        ex += 1
                room = len(flood(tail, 4, occ0 - {tail})) - 1
                adj = sum(1 for d in range(4) if dest(h, d) in pearls)
                foe3 = int(any(side(z) != s and gap(bb[0], h) <= 3 for z, bb in bodies.items()))
                cur['tailfact'] = 'tail has no exit' if ex == 0 else 'tail beside a portal' if port else 'fewer than 5 free tiles behind the tail' if room < 5 else 'enemy head within 3' if foe3 else 'pearl beside the head' if adj else 'nothing in the way'
            P = [c for c in pearls if inview(h, c)]
            if not P:
                cur['cls'] = 'blind'
                continue
            occ = set()
            for bb in bodies.values():
                occ.update(bb)
            mine = flood(h, 7, occ - {h})
            reach = [(mine[c], c) for c in P if c in mine]
            if not reach:
                cur['cls'] = 'walled'
                continue
            floods = {}
            best = None
            tie = False
            for d, c in sorted(reach):
                nearer = False
                eq = False
                for z, bb in bodies.items():
                    if z == actor or side(z) != s or gap(bb[0], c) >= d + 1:
                        continue
                    if z not in floods:
                        floods[z] = flood(bb[0], 7, occ - {bb[0]})
                    dz = floods[z].get(c, 99)
                    if dz < d:
                        nearer = True
                        break
                    if dz == d:
                        eq = True
                if not nearer:
                    best = (d, c)
                    tie = eq
                    break
            if best is None:
                cur['cls'] = 'mate'
                continue
            d, c = best
            cur['cls'] = 'own'
            cur['d'] = d
            cur['tgt'] = c
            cur['tie'] = tie
            cur['foe'] = int(any(side(z) != s and gap(bb[0], c) <= 3 for z, bb in bodies.items()))
            cur['exits'] = exits(c, occ, None) - (1 if d == 1 else 0) if d == 1 else exits(c, occ, None)
            C[(s, wnd(rnd), 'own pearl at d%d' % min(d, 4))] += 1
            if d == 1 and actor != queens[s]:
                low = int(any(side(z) == s and z < actor and inview(h, bb[0]) for z, bb in bodies.items()))
                anym = int(any(side(z) == s and z != actor and inview(h, bb[0]) for z, bb in bodies.items()))
                seen_port = 0
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        cc = ((h[0] + dx) % W, (h[1] + dy) % H)
                        if any(edges.get(edge_id(W, H, cc[0], cc[1], dd), (0, -1))[0] == 2 for dd in range(4)):
                            seen_port = 1
                cur['d1ctx'] = 'lower-id mate in view' if low else 'only higher-id mates in view' if anym else 'no mate in view'
                cur['d1port'] = seen_port
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if expected:
                    pearls[c] = 'dead'
                    expected -= 1
                else:
                    pearls[c] = 'nat'
                    C[(2, wnd(max(rnd, 0)), 'born')] += 1
            else:
                o = pearls.pop(c)
                if cur is not None:
                    cur['ate'] += 1
                    C[(cur['s'], wnd(rnd), 'pearls ' + o)] += 1
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
            if cur is not None and cur['i'] == parent:
                cur['split'] = 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            L = len(bodies[i])
            C[(side(i), wnd(rnd), 'deaths')] += 1
            C[(side(i), wnd(rnd), 'death ' + ('head-on' if reason == 3 else 'other'))] += 1
            C[(side(i), wnd(rnd), 'dead length')] += L
            if cur is not None and cur['i'] == i:
                cur['died'] = 1
            expected = (L + 1) // 2
            bodies.pop(i)
    close()
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=cells,
                opp=j['team' + 'AB'[1 - own] + 'Name'], start=[start_units, start_len], snaps=snaps,
                C=[[a, b, c, n] for (a, b, c), n in sorted(C.items())])


if __name__ == '__main__':
    name = sys.argv[1]
    todo = jobs(name)
    with open(OUT + 'o1_mid-%s.jsonl' % name, 'w') as f:
        for label, path, j in todo:
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
    print('done', name, len(todo))
