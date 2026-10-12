#!/usr/bin/env python3
"""Independent map geometry from the server replay header (own edge handling). Read-only."""
import json, sys
from collections import deque, Counter
ROOT = '~/01. Project/개인 프로젝트/unsw-swarm/'
obs = json.load(open(ROOT + 'data/analysis/ladder/map-observations.json'))
maps = json.load(open(ROOT + 'data/analysis/ladder/maps.json'))
texts = {}
variants = Counter()
for o in obs.values():
    texts.setdefault(o['map'], set()).add(o['text'])
def parse(text):
    L = [l.split() for l in text.splitlines() if l.split()]
    W, H = map(int, L[0][1:3])
    edge = {int(l[1]): (int(l[2]), int(l[3])) for l in L if l[0] == 'EDGE'}
    dragons = [(int(l[1]), [(int(l[3 + 2 * k]), int(l[4 + 2 * k])) for k in range(int(l[2]))]) for l in L if l[0] == 'DRAGON']
    sym = next((l[1] for l in L if l[0] == 'SYMMETRY'), None)
    nid = lambda x, y: 2 * y * (W + 1) + x
    wid = lambda x, y: (2 * y + 1) * (W + 1) + x
    pairs = {}
    for i, (k, p) in edge.items():
        if k == 2: pairs.setdefault(p, []).append(i)
    def eid(x, y, d):
        return nid(x, y) if d == 0 else wid((x + 1) % W, y) if d == 1 else nid(x, (y + 1) % H) if d == 2 else wid(x, y)
    def step(x, y, d):
        i = eid(x, y, d); k, p = edge.get(i, (0, -1))
        if k == 1: return None
        if k == 2:
            other = [z for z in pairs[p] if z != i]
            if len(other) != 1: return None
            row, ex = divmod(other[0], W + 1); ey = row // 2
            assert (row % 2 == 0) == (d in (0, 2)), 'portal pair orientation'
            return ((ex - (d == 3)) % W, (ey - (d == 0)) % H)
        dx, dy = ((0, -1), (1, 0), (0, 1), (-1, 0))[d]
        return ((x + dx) % W, (y + dy) % H)
    return W, H, edge, dragons, sym, eid, step, pairs
def props(text):
    W, H, edge, dragons, sym, eid, step, pairs = parse(text)
    deg = {(x, y): sum(edge.get(eid(x, y, d), (0, -1))[0] != 1 for d in range(4)) for x in range(W) for y in range(H)}
    open_n = sum(v > 0 for v in deg.values())
    q = {t: b for t, b in reversed(dragons[:2])}
    assert dragons[0][0] != dragons[1][0]
    (ax, ay), (bx, by) = dragons[0][1][0], dragons[1][1][0]
    gap = lambda a, b, n: min(abs(a - b), n - abs(a - b))
    occupied = {c for _, b in dragons for c in b}
    out = dict(width=W, height=H, open_tiles=open_n, wall_share=sum(4 - v for v in deg.values()) / (4 * W * H),
               portals=len(pairs), queen_spawn_distance=gap(ax, bx, W) + gap(ay, by, H),
               corridor_share=sum(v == 2 for v in deg.values()) / open_n, symmetry=sym,
               queen_len=[len(dragons[0][1]), len(dragons[1][1])], n_dragons=len(dragons), max_edge_id=max(edge), unlisted_border=sum(1 for y in range(H) if (2*y+1)*(W+1)+W in edge) + sum(1 for x in range(W) if 2*H*(W+1)+x in edge))
    rooms = []; trapped = []
    for team, body in dragons[:2]:
        seen = {body[0]}; todo = deque([body[0]])
        while todo and len(seen) < 400:
            c = todo.popleft()
            for d in range(4):
                n = step(*c, d)
                if n is None or n in seen or n in occupied: continue
                seen.add(n); todo.append(n)
        rooms.append(len(seen) - 1)
        # can she make 16 single steps alive, other dragons frozen, no pearls (her tail tile blocks for the step)?
        frozen = occupied - set(body)
        budget = [20000]
        memo = set()
        def go(b, n):
            if n == 0 or budget[0] <= 0: return True
            if (b, n) in memo: return False
            memo.add((b, n)); budget[0] -= 1
            for d in range(4):
                h = step(*b[0], d)
                if h is None or h in b or h in frozen: continue
                if go((h,) + b[:-1], n - 1): return True
            return False
        trapped.append(not go(tuple(body), 16))
    out.update(queen_spawn_room=rooms, queen_spawn_trapped=trapped)
    return out
def region(text):
    W, H, edge, dragons, sym, eid, step, pairs = parse(text)
    out = []
    for team, body in dragons[:2]:
        seen = {body[0]}; todo = deque([body[0]])
        while todo and len(seen) < 400:
            c = todo.popleft()
            for d in range(4):
                n = step(*c, d)
                if n is None or n in seen: continue
                seen.add(n); todo.append(n)
        out.append(min(len(seen), 400))
    return min(out)
bad = 0; checked = 0
for name in sorted(texts):
    for text in sorted(texts[name]):
        p = props(text)
        mine = dict(width=p['width'], height=p['height'], open_tiles=p['open_tiles'], portals=p['portals'], queen_spawn_distance=p['queen_spawn_distance'],
                    wall_share=round(p['wall_share'], 9), corridor_share=round(p['corridor_share'], 9), dragons_at_spawn=p['n_dragons'] // 2,
                    queen_spawn_length=min(p['queen_len']), queen_spawn_room=min(min(p['queen_spawn_room']), 60), queen_spawn_region=region(text),
                    queen_spawn_dead_end=any(p['queen_spawn_trapped']))
        best = None
        for key, m in maps.items():
            if m['name'] != name: continue
            theirs = {k: (round(m[k], 9) if isinstance(m[k], float) else m[k]) for k in mine}
            d = {k: (theirs[k], mine[k]) for k in mine if theirs[k] != mine[k]}
            if best is None or len(d) < len(best[1]): best = (key, d)
        checked += 1; bad += bool(best[1])
        print(f"{name:18s} -> {best[0]:22s} DIFF={best[1] or 'none'}")
print('header variants checked:', checked, 'with a difference:', bad)
print('--- region reachable from each queen head through non-kelp edges, dragons ignored (cap 400) ---')
for name in sorted(texts):
    for text in sorted(texts[name]):
        W, H, edge, dragons, sym, eid, step, pairs = parse(text)
        regs = []
        for team, body in dragons[:2]:
            seen = {body[0]}; todo = deque([body[0]])
            while todo and len(seen) < 400:
                c = todo.popleft()
                for d in range(4):
                    n = step(*c, d)
                    if n is None or n in seen: continue
                    seen.add(n); todo.append(n)
            regs.append(len(seen))
        p = props(text)
        print(f"{name:18s} teamOfDragon0={dragons[0][0]} qlen={p['queen_len']} region={regs} room={p['queen_spawn_room']} trapped={p['queen_spawn_trapped']} dragons={p['n_dragons']} open={p['open_tiles']} wall={p['wall_share']:.4f} corr={p['corridor_share']:.4f}")
