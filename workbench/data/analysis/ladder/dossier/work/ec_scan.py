# Scratch (diag-economy): one pass over every game of ours (who=O, team 1119, 500 main ladder games) or of rank-1
# (who=R, team 306, 597 games); the followed side only. Every turn of a dragon of length 2 or 3 is put in one
# situation at the turn start and the pearls it eats on that turn are counted, by origin of the pearl.
# pd: A a pearl on a tile the head can step to; B nearest pearl in view 2-3 path steps away (bodies ignored);
#     C a pearl in the 7 by 7 view but farther or walled off; S no pearl in view, a tile in view tries to spawn
#     within 3 rounds (births and their mirror tiles); N nothing. G = a dragon of 4 or longer (coarse row).
# Flags: E enemy head within 3 path steps; box 0 no free step, 1 fewer than 6 free tiles reachable, 2 fewer than 14,
#     3 more; J 1 child in its first 3 turns, 2 parent in the 3 turns after its split; lead = round above the leader
#     round (150 above 1200 cells, else 300); n56 = 56+ alive; D (added at commit) = dead within its next 3 turns.
# A sub: kind (0 natural, 1 own dead, 2 their dead), origin (0 appeared since this dragon's last turn began, 1 the
#     dragon came beside it, 2 it was beside the head last turn too, 3 first turn of life), mask (1 enemy head beside
#     the pearl, 2 team mate's head beside it, 4 pocket rule, 8 reached by portal only, 16 fewer than L+2 free tiles
#     from it, 32 a longer team mate's head within 9 tiles of it, 64 two or more pearls beside the head).
# B sub: steps (2, 3), kind, fresh (0/1/3 as origin), a mate's head strictly nearer, an enemy head as near, longer mate in 9.
# S sub: steps to the nearest such tile (0 on it, 1, 2, 3, 4 = farther), its countdown.
# Values per key: turns, pearls eaten on the turn by kind (3), pearls eaten on this and the next 4 own turns.
# trans: (band, L, pd, E, lead, sub...) + (what it did: 0 moved, 1 ate, 2 split, 3 died on its turn; pd at its next turn).
# Usage: python3 data/analysis/ladder/dossier/work/ec_scan.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
FWD = 5


class Geo:
    def __init__(self, w, h, raw, sym):
        self.w, self.h = w, h
        edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.adj, self.oadj, self.padj, self.adjset = [], [], [], []
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
                a = sorted({dest for kind, dest in row if kind != 1})
                o = {dest for kind, dest in row if kind == 0}
                self.adj.append(a)
                self.adjset.append(frozenset(a))
                self.oadj.append(sorted(o))
                self.padj.append(frozenset(dest for kind, dest in row if kind == 2) - o)
        self.mirror = []
        for y in range(h):
            for x in range(w):
                mx = w - 1 - x if 'y' in sym else x
                my = h - 1 - y if 'x' in sym else y
                self.mirror.append(my * w + mx)
        self.wins, self.balls, self.pockets = {}, {}, {}

    def window(self, c):
        s = self.wins.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            t = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4)}))
            s = (t, frozenset(t))
            self.wins[c] = s
        return s

    def ball(self, c):
        d = self.balls.get(c)
        if d is None:
            d = {c: 0}
            frontier = [c]
            for k in (1, 2, 3):
                nxt = []
                for u in frontier:
                    for v in self.adj[u]:
                        if v not in d:
                            d[v] = k
                            nxt.append(v)
                frontier = nxt
            del d[c]
            self.balls[c] = d
        return d

    def pocket(self, c):
        n = self.pockets.get(c)
        if n is None:
            seen = {c}
            q = [c]
            k = 0
            while k < len(q) and len(q) < 48:
                for t in self.oadj[q[k]]:
                    if t not in seen and len(q) < 48:
                        seen.add(t)
                        q.append(t)
                k += 1
            n = len(q)
            self.pockets[c] = n
        return n

    def man(self, a, c):
        ay, ax = divmod(a, self.w)
        cy, cx = divmod(c, self.w)
        dx, dy = abs(ax - cx), abs(ay - cy)
        return min(dx, self.w - dx) + min(dy, self.h - dy)


def scan(row, geos, acc, trans):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    N = w * h
    bodies, teams, raw, sym = {}, {}, [], ''
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
        elif q and q[0] == 'SYMMETRY':
            sym = q[1]
    gkey = (row['layout'], w, h)
    if gkey not in geos:
        geos[gkey] = Geo(w, h, raw, sym)
    g = geos[gkey]
    adj, adjset, padj, mirror = g.adj, g.adjset, g.padj, g.mirror
    focal = row['side']
    sd = {i: 0 if teams[i] == focal else 1 for i in bodies}
    occ = [0] * N
    hg = ([0] * N, [0] * N)
    alive = [0, 0]
    for i, b in bodies.items():
        alive[sd[i]] += 1
        hg[sd[i]][b[0]] += 1
        for c in b:
            occ[c] += 1
    ug, eg = hg
    grow = 300 if N <= 1200 else 150
    events = list(root.pointer(3))

    nat = defaultdict(list)
    rnd, inturn = 0, False
    for ev in events:
        k = ev.u16(0)
        if k == 0:
            rnd, inturn = ev.pointer(0).i32(0), False
        elif k == 1:
            inturn = True
        elif k == 3 and not inturn:
            p = ev.pointer(0)
            if p.u32(0):
                t = replay.point(p.pointer(0))
                nat[rnd].append(t[1] * w + t[0])
    att = {}
    for r, ts in nat.items():
        s = set(ts)
        for t in ts:
            s.add(mirror[t])
        att[r] = tuple(sorted(s))

    present = {}
    pv, sv = [0] * N, [0] * N
    expected = deque()
    buf, prev, jmark = {}, {}, {}
    chk = [[0, 0], [0, 0], [0, 0]]
    sup = Counter()
    added_upto = -1
    seq = 0
    rnd, actor, cur = 0, None, None
    band = 0

    def commit(r):
        v = acc[r[0] + (r[5],)]
        v[0] += 1
        v[1] += r[1]
        v[2] += r[2]
        v[3] += r[3]
        v[4] += r[4]
        trans[r[8] + (1 if (r[1] + r[2] + r[3]) else r[6], r[7])] += 1

    def room(start, cap):
        seen = {start}
        q = [start]
        k = 0
        while k < len(q) and len(q) < cap:
            for t in adj[q[k]]:
                if t not in seen and occ[t] == 0:
                    seen.add(t)
                    q.append(t)
            k += 1
        return len(q)

    def mate9(a, L, p):
        for j, bb in bodies.items():
            if sd[j] == 0 and j != a and len(bb) > L and g.man(bb[0], p) <= 9:
                return 1
        return 0

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor, cur = p.i32(0), None, None
            seq += 1
            band = 0 if rnd <= 100 else 1 if rnd <= 300 else 2
            if rnd <= added_upto:
                for c in att.get(rnd, ()):
                    for z in g.window(c)[0]:
                        sv[z] -= 1
            for rr in range(max(added_upto + 1, rnd + 1), rnd + 4):
                for c in att.get(rr, ()):
                    for z in g.window(c)[0]:
                        sv[z] += 1
            added_upto = max(added_upto, rnd + 3)
        elif k == 1:
            actor = p.i32(0)
            seq += 1
            cur = None
            b = bodies.get(actor)
            if b is None or sd[actor] != 0:
                continue
            L, head = len(b), b[0]
            chk[band][0] += 1
            pr = prev.get(actor)
            if L >= 4:
                pd = 'G'
                key = ('G', band, 4 if L == 4 else 5 if L <= 7 else 8)
                tkey = ('G', band)
                jm = jmark.get(actor)
                if jm is not None:
                    jm[1] -= 1
                    if jm[1] == 0:
                        del jmark[actor]
            else:
                lead = int(rnd > grow)
                n56 = int(alive[0] >= 56)
                jm = jmark.get(actor)
                J = 0
                if jm is not None:
                    J = jm[0]
                    jm[1] -= 1
                    if jm[1] == 0:
                        del jmark[actor]
                ball = g.ball(head)
                E = 0
                for t in ball:
                    if eg[t]:
                        E = 1
                        break
                fr = 0
                for t in adj[head]:
                    if occ[t] == 0:
                        fr += 1
                if fr == 0:
                    box = 0
                else:
                    rm = room(head, 15) - 1
                    box = 1 if rm < 6 else 2 if rm < 14 else 3
                sub = ()
                tsub = ()
                if pv[head]:
                    adjp = [t for t in adj[head] if t in present]
                    if adjp:
                        pd = 'A'
                        best = None
                        for q in adjp:
                            m = 0
                            m2 = 0
                            for t in adj[q]:
                                if t == head:
                                    continue
                                if eg[t]:
                                    m |= 1
                                if ug[t]:
                                    m2 = 2
                            pk = g.pocket(q)
                            if pk < 48 and L + 1 > pk // 2:
                                m |= 4
                            if q in padj[head]:
                                m |= 8
                            if room(q, L + 2) < L + 2:
                                m |= 16
                            if mate9(actor, L, q):
                                m |= 32
                            sc = (bin(m + m2).count('1'), q)
                            if best is None or sc < best[0]:
                                best = (sc, q, m, m2)
                        q, m, m2 = best[1], best[2], best[3]
                        kind, pseq = present[q]
                        origin = 3 if pr is None else 0 if pseq >= pr[0] else 2 if q in adjset[pr[1]] else 1
                        sub = (kind, origin, m + m2 + (64 if len(adjp) >= 2 else 0))
                        tsub = (kind, origin, m)
                    else:
                        winset = g.window(head)[1]
                        bd, bp = 9, -1
                        for t, d in ball.items():
                            if d < bd and t in present and t in winset:
                                bd, bp = d, t
                        if bp >= 0:
                            pd = 'B'
                            kind, pseq = present[bp]
                            fresh = 3 if pr is None else 0 if pseq >= pr[0] else 1
                            mn = en = 0
                            for t, dd in g.ball(bp).items():
                                if t != head:
                                    if dd < bd and ug[t]:
                                        mn = 1
                                    if dd <= bd and eg[t]:
                                        en = 1
                            sub = (bd, kind, fresh, mn, en, mate9(actor, L, bp))
                            tsub = (bd, mn, en)
                        else:
                            pd = 'C'
                elif sv[head] > 0:
                    pd = 'S'
                    winset = g.window(head)[1]
                    bd, cd = 9, 0
                    for rr in (rnd + 1, rnd + 2, rnd + 3):
                        for t in att.get(rr, ()):
                            if t in winset:
                                d = 0 if t == head else ball.get(t, 4)
                                if d < bd:
                                    bd, cd = d, rr - rnd
                    sub = (bd, cd)
                    tsub = (bd, cd)
                else:
                    pd = 'N'
                key = ('T', band, L, pd, E, box, J, lead, n56) + sub
                tkey = ('T', band, L, pd, E, lead) + tsub
            rec = [key, 0, 0, 0, 0, 0, 0, 'Z', tkey]
            if pr is not None:
                pr[2][7] = pd
            q = buf.get(actor)
            if q is None:
                q = buf[actor] = deque()
            q.append(rec)
            if len(q) > FWD:
                commit(q.popleft())
            prev[actor] = (seq, head, rec)
            cur = rec
        elif k == 3:
            t = replay.point(p.pointer(0))
            c = t[1] * w + t[0]
            if p.u32(0):
                if expected:
                    xy, kind = expected.popleft()
                    assert xy == c
                else:
                    kind = 0
                present[c] = (kind, seq)
                for z in g.window(c)[0]:
                    pv[z] += 1
                sup[('born', band, kind)] += 1
            else:
                kind = present.pop(c)[0]
                for z in g.window(c)[0]:
                    pv[z] -= 1
                if sd[actor] == 0:
                    chk[band][1] += 1
                    if cur is not None:
                        cur[1 + kind] += 1
                    for r in buf.get(actor, ()):
                        r[4] += 1
                else:
                    sup[('opp_eat', band, kind)] += 1
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                s = sd[i]
                hg[s][b[0]] -= 1
                hg[s][hd] += 1
                b.appendleft(hd)
                occ[hd] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            s = sd[a]
            for cell in bodies[a]:
                occ[cell] -= 1
            hg[s][bodies[a][0]] -= 1
            sd[c] = s
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                for cell in bodies[i]:
                    occ[cell] += 1
                hg[s][bodies[i][0]] += 1
            alive[s] += 1
            if s == 0:
                jmark[a] = [2, 3]
                jmark[c] = [1, 3]
                sup[('split', band, 0)] += 1
                if a == actor and cur is not None:
                    cur[6] = 2
        elif k == 11:
            i = p.i32(0)
            b = bodies[i]
            s = sd[i]
            for seg, cell in enumerate(b):
                occ[cell] -= 1
                if seg % 2 == 0:
                    expected.append((cell, 1 if s == 0 else 2))
            hg[s][b[0]] -= 1
            bodies.pop(i)
            alive[s] -= 1
            if s == 0:
                sup[('death', band, 0)] += 1
                if i == actor and cur is not None:
                    cur[6] = 3
                q = buf.pop(i, None)
                if q:
                    n = len(q)
                    for idx, r in enumerate(q):
                        if idx >= n - 3:
                            r[5] = 1
                    q[-1][7] = 'X'
                    for r in q:
                        commit(r)
                prev.pop(i, None)
                jmark.pop(i, None)
    assert not expected
    for q in buf.values():
        for r in q:
            commit(r)
    for kk, n in sup.items():
        acc[('U',) + kk][0] += n
    acc[('U', 'games', 0, 0)][0] += 1
    return chk


def save(tag, body):
    if tag == 'O0':
        Path(OUT + 'ec_scan-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'ec_scan-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'ec_scan-O2.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'ec_scan-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'ec_scan-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'ec_scan-R2.jsonl').write_text(body)
    else:
        Path(OUT + 'ec_scan-test.jsonl').write_text(body)


def main():
    who, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[::max(1, len(rows) // limit)][:limit]
    geos, bad, off = {}, [], 0
    accs, transs, games = {}, {}, Counter()
    for n, r in enumerate(rows):
        lay = r['layout']
        if lay not in accs:
            accs[lay] = defaultdict(lambda: [0, 0, 0, 0, 0])
            transs[lay] = Counter()
        a2, t2 = defaultdict(lambda: [0, 0, 0, 0, 0]), Counter()
        try:
            chk = scan(r, geos, a2, t2)
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
            continue
        for wi, name in enumerate(('0-100', '101-300')):
            if r[name]['turns'] != chk[wi][0] or r[name]['pearls'] != chk[wi][1]:
                off += 1
                if off <= 12:
                    print('MISMATCH', r['game'], name, r[name]['turns'], chk[wi][0], r[name]['pearls'], chk[wi][1], flush=True)
        for kk, v in a2.items():
            u = accs[lay][kk]
            for z in range(5):
                u[z] += v[z]
        transs[lay].update(t2)
        games[lay] += 1
        if n % 10 == 9:
            print(n + 1, len(rows), 'bad', len(bad), 'off', off, flush=True)
    out = []
    for lay in sorted(accs):
        out.append(json.dumps(dict(who=who, layout=lay, games=games[lay],
                                   acc=[list(kk) + v for kk, v in sorted(accs[lay].items(), key=repr)],
                                   trans=[list(kk) + [v] for kk, v in sorted(transs[lay].items(), key=repr)]),
                              separators=(',', ':')))
    save('test' if limit else who + str(shard), '\n'.join(out) + '\n')
    print('done', who, shard, sum(games.values()), 'bad', bad, 'mismatches', off)


main()
