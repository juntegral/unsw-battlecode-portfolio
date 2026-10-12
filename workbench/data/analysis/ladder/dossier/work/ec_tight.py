# Scratch (diag-economy, second pass): why the tile of a pearl beside the head is cramped, and what the dragon does.
# Followed side only, dragons of length 2 and 3, rounds 0-300 (and 301+ as band 2). For every turn that starts with a
# pearl on a tile the head can step to, the free tiles reachable from that tile are counted five ways (cap 3L+8):
#   rs walls only; rm walls and team mates' bodies; re walls and enemy bodies; rb walls and every other dragon's body
#   (what main.cpp counts: 1452-1453 mark every visible part of another dragon blocked for good); ro all bodies.
# cause (first that holds; level 1 = fewer than L+2 tiles, level 2 = fewer than 3L+8):
#   S1 walls alone; Bm1 team mates' bodies alone make it so; Be1 enemy bodies alone; Bx1 only both together;
#   O1 only with its own body counted; then S2, Bm2, Be2, Bx2, O2 the same at level 2; F free.
#   With two or more pearls beside the head the least cramped one is taken.
# hs = tiles reachable from the head by walls only (1 under 6, 2 under 14, 3 more); box as ec_scan.py.
# flags: 1 leader round passed and a longer mate within 9 tiles of the pearl, 2 pocket rule or portal-only step,
#   4 enemy head beside the pearl, 8 team mate's head beside the pearl.
# Values per key: turns, pearls eaten on the turn, pearls on this and the next 4 own turns, dead within its next 3
# turns, length lost by a death within its next 5 turns, died on this turn.
# Usage: python3 data/analysis/ladder/dossier/work/ec_tight.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
FWD = 5
SEV = dict(F=0, O2=1, Bm2=2, Be2=2, Bx2=2, S2=3, O1=4, Bm1=5, Be1=5, Bx1=5, S1=6)


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.adj, self.oadj, self.padj = [], [], []
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
                self.oadj.append(sorted(o))
                self.padj.append(frozenset(dest for kind, dest in row if kind == 2) - o)
        self.srooms, self.pockets = {}, {}

    def sroom(self, c):
        n = self.srooms.get(c)
        if n is None:
            seen = {c}
            q = [c]
            k = 0
            while k < len(q) and len(q) < 18:
                for t in self.adj[q[k]]:
                    if t not in seen:
                        seen.add(t)
                        q.append(t)
                k += 1
            n = len(q)
            self.srooms[c] = n
        return n

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


def scan(row, geos, acc, samples):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    N = w * h
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    gkey = (row['layout'], w, h)
    if gkey not in geos:
        geos[gkey] = Geo(w, h, raw)
    g = geos[gkey]
    adj, padj = g.adj, g.padj
    focal = row['side']
    sd = {i: 0 if teams[i] == focal else 1 for i in bodies}
    occ = ([0] * N, [0] * N)
    hg = ([0] * N, [0] * N)
    for i, b in bodies.items():
        hg[sd[i]][b[0]] += 1
        for c in b:
            occ[sd[i]][c] += 1
    o0, o1 = occ
    ug, eg = hg
    grow = 300 if N <= 1200 else 150
    present = {}
    expected = deque()
    buf, prev = {}, {}
    rnd, actor, cur, band, seq = 0, None, None, 0, 0
    taken = 0

    def commit(r):
        v = acc[r[0] + (1 if r[1] else 0,)]
        v[0] += 1
        v[1] += r[1]
        v[2] += r[2]
        v[3] += r[3]
        v[4] += r[4]
        v[5] += r[5]

    def room(start, cap, mode, own):
        seen = {start}
        q = [start]
        k = 0
        while k < len(q) and len(q) < cap:
            for t in adj[q[k]]:
                if t in seen:
                    continue
                if mode == 1:
                    if o0[t] and t not in own:
                        continue
                elif mode == 2:
                    if o1[t]:
                        continue
                elif mode == 3:
                    if (o0[t] or o1[t]) and t not in own:
                        continue
                elif mode == 4:
                    if o0[t] or o1[t]:
                        continue
                seen.add(t)
                q.append(t)
            k += 1
        return len(q)

    def cause_of(p, L, own):
        lo, hi = L + 2, 3 * L + 8
        rs = min(g.sroom(p), hi)
        if rs < lo:
            return 'S1'
        rb = room(p, hi, 3, own)
        if rb < lo:
            if room(p, lo, 1, own) < lo:
                return 'Bm1'
            if room(p, lo, 2, own) < lo:
                return 'Be1'
            return 'Bx1'
        ro = room(p, hi, 4, own)
        if ro < lo:
            return 'O1'
        if rs < hi:
            return 'S2'
        if rb < hi:
            if room(p, hi, 1, own) < hi:
                return 'Bm2'
            if room(p, hi, 2, own) < hi:
                return 'Be2'
            return 'Bx2'
        if ro < hi:
            return 'O2'
        return 'F'

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor, cur = p.i32(0), None, None
            seq += 1
            band = 0 if rnd <= 100 else 1 if rnd <= 300 else 2
        elif k == 1:
            actor = p.i32(0)
            seq += 1
            cur = None
            b = bodies.get(actor)
            if b is None or sd[actor] != 0:
                continue
            L, head = len(b), b[0]
            if L >= 4:
                key = ('G', band)
            else:
                st = g.sroom(head) - 1
                hs = 1 if st < 6 else 2 if st < 14 else 3
                fr = 0
                for t in adj[head]:
                    if o0[t] == 0 and o1[t] == 0:
                        fr += 1
                if fr == 0:
                    box = 0
                else:
                    rm = room(head, 15, 4, ()) - 1
                    box = 1 if rm < 6 else 2 if rm < 14 else 3
                adjp = [t for t in adj[head] if t in present]
                if not adjp:
                    key = ('n', band, L, hs, box)
                else:
                    own = set(b)
                    lead = int(rnd > grow)
                    best = None
                    for q in adjp:
                        c = cause_of(q, L, own)
                        sc = (SEV[c], q)
                        if best is None or sc < best[0]:
                            best = (sc, q, c)
                    q, c = best[1], best[2]
                    fl = 0
                    if lead:
                        for j, bb in bodies.items():
                            if sd[j] == 0 and j != actor and len(bb) > L and g.man(bb[0], q) <= 9:
                                fl = 1
                                break
                    pk = g.pocket(q)
                    if (pk < 48 and L + 1 > pk // 2) or q in padj[head]:
                        fl += 2
                    eh = mh = 0
                    for t in adj[q]:
                        if t != head:
                            if eg[t]:
                                eh = 1
                            if ug[t]:
                                mh = 1
                    fl += 4 * eh + 8 * mh
                    kind, pseq = present[q]
                    pr = prev.get(actor)
                    origin = 3 if pr is None else 0 if pseq >= pr[0] else 2 if q in adj[pr[1]] else 1
                    key = ('A', band, L, lead, c, hs, box, fl, kind, origin)
                    if fl == 0 and c[0] == 'B' and band < 2 and len(samples) < 400 and seq % 7 == 0:
                        samples.append([row['game'], rnd, actor, L, head % w, head // w, q % w, q // w, c, kind, box])
            rec = [key, 0, 0, 0, 0, 0]
            q = buf.get(actor)
            if q is None:
                q = buf[actor] = deque()
            q.append(rec)
            if len(q) > FWD:
                commit(q.popleft())
            prev[actor] = (seq, head)
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
            else:
                present.pop(c)
                if sd[actor] == 0:
                    if cur is not None:
                        cur[1] += 1
                    for r in buf.get(actor, ()):
                        r[2] += 1
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            s = sd[i]
            if b[0] != hd:
                hg[s][b[0]] -= 1
                hg[s][hd] += 1
                b.appendleft(hd)
                occ[s][hd] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[s][b.pop()] -= 1
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            s = sd[a]
            for cell in bodies[a]:
                occ[s][cell] -= 1
            hg[s][bodies[a][0]] -= 1
            sd[c] = s
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                for cell in bodies[i]:
                    occ[s][cell] += 1
                hg[s][bodies[i][0]] += 1
        elif k == 11:
            i = p.i32(0)
            b = bodies[i]
            s = sd[i]
            for seg, cell in enumerate(b):
                occ[s][cell] -= 1
                if seg % 2 == 0:
                    expected.append((cell, 1 if s == 0 else 2))
            hg[s][b[0]] -= 1
            bodies.pop(i)
            if s == 0:
                if i == actor and cur is not None:
                    cur[5] = 1
                q = buf.pop(i, None)
                if q:
                    n = len(q)
                    for idx, r in enumerate(q):
                        r[4] += len(b)
                        if idx >= n - 3:
                            r[3] = 1
                    for r in q:
                        commit(r)
                prev.pop(i, None)
    assert not expected
    for q in buf.values():
        for r in q:
            commit(r)


def save(tag, body):
    if tag == 'O0':
        Path(OUT + 'ec_tight-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'ec_tight-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'ec_tight-O2.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'ec_tight-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'ec_tight-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'ec_tight-R2.jsonl').write_text(body)
    else:
        Path(OUT + 'ec_tight-test.jsonl').write_text(body)


def main():
    who, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[::max(1, len(rows) // limit)][:limit]
    geos, bad = {}, []
    accs, samp, games = {}, {}, Counter()
    for n, r in enumerate(rows):
        lay = r['layout']
        if lay not in accs:
            accs[lay] = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
            samp[lay] = []
        a2, s2 = defaultdict(lambda: [0, 0, 0, 0, 0, 0]), []
        try:
            scan(r, geos, a2, s2)
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
            continue
        for kk, v in a2.items():
            u = accs[lay][kk]
            for z in range(6):
                u[z] += v[z]
        if len(samp[lay]) < 60:
            samp[lay].extend(s2[::max(1, len(s2) // 6)][:6])
        games[lay] += 1
        if n % 10 == 9:
            print(n + 1, len(rows), 'bad', len(bad), flush=True)
    out = []
    for lay in sorted(accs):
        out.append(json.dumps(dict(who=who, layout=lay, games=games[lay],
                                   acc=[list(kk) + v for kk, v in sorted(accs[lay].items(), key=repr)],
                                   samples=samp[lay]), separators=(',', ':')))
    save('test' if limit else who + str(shard), '\n'.join(out) + '\n')
    print('done', who, shard, sum(games.values()), 'bad', bad)


main()
