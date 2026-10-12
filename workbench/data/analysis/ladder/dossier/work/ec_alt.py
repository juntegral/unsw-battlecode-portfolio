# Scratch (diag-economy, third pass): the bot's own room verdict for the step onto a pearl beside the head, rebuilt
# from the true board, against the verdict it would give if team mates' bodies cleared in time.
# Followed side only, dragons of length 2 and 3. For the pearl tile q the survey of main.cpp 2895-3035 is walked:
# arrival step 1 on q with one pearl eaten; a tile of the dragon's own body at offset k from the head opens at step
# L-k+1 (1506-1513); every tile of another dragon is shut for good (1452-1453). Count = tiles reached (cap 40).
#   v: 0 fewer than L+2 (PENALTY_TRAPPED), 1 fewer than 3L+8 (PENALTY_TIGHT), 2 enough. tl: own tail reached (else NO_TAIL).
#   now = as the bot counts; mt = team mates of 4 or shorter open like its own body (tile at offset k of n opens
#   at step n-k+1); al = every other dragon of 4 or shorter does. With two pearls beside the head the best "now" is used.
# ns = exits of the pearl's tile other than the head's tile (walls only; 0 = a one-tile nook), capped at 2.
# flags: 1 leader round passed and a longer mate within 9 tiles of the pearl, 2 pocket rule or portal-only step,
#   4 enemy head beside the pearl, 8 team mate's head beside the pearl.
# Values: turns, pearls eaten on the turn, pearls on this and the next 4 own turns, dead within its next 3 turns,
# length lost by a death within its next 5 turns, split on its next turn.
# Second version: another dragon's tile opens at step n-k+1 whatever this dragon has eaten; key gains ob (a tile of the
# dragon's own body, not the head, is an exit of the pearl's tile) and nf (free exits now, capped at 2); a seventh
# value is the family net: pearls eaten minus length lost in deaths on this and the next 4 own turns, counting the
# children it splits off in those turns as well.
# Fourth pass (ec_alt.py): the key is ('A', band, L, verdict now, verdict with mates timed, one-tile nook 0/1,
# alt, flags, kind, ob), alt = the best verdict now among the other free steps of the head (-1 none free).
# Usage: python3 data/analysis/ladder/dossier/work/ec_alt.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
FWD = 5
CAP = 40


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
    cell = {}
    hg = ([0] * N, [0] * N)
    for i, b in bodies.items():
        hg[sd[i]][b[0]] += 1
        for c in b:
            cell[c] = i
    ug, eg = hg
    grow = 300 if N <= 1200 else 150
    present = {}
    expected = deque()
    buf, last = {}, {}
    rnd, actor, cur, band, seq = 0, None, None, 0, 0

    fam = {}

    def commit(r):
        v = acc[r[0] + (1 if r[1] else 0,)]
        v[0] += 1
        v[1] += r[1]
        v[2] += r[2]
        v[3] += r[3]
        v[4] += r[4]
        v[5] += r[6]
        v[6] += r[7]
        r[8] = 1

    def survey(q, a, L, mode, e0=1):
        b = bodies[a]
        tailc = b[-1]
        seen = {q}
        queue = [(q, 1, e0)]
        k = 0
        reach = False
        while k < len(queue) and len(queue) < CAP:
            c, steps, eaten = queue[k]
            k += 1
            for t in adj[c]:
                if t in seen:
                    continue
                j = cell.get(t)
                if j is not None:
                    bb = bodies[j]
                    n = len(bb)
                    if j != a and (mode == 0 or n > 4 or (mode == 1 and sd[j] != 0)):
                        continue
                    off = 0
                    for x in bb:
                        if x == t:
                            break
                        off += 1
                    if steps + 1 - (eaten if j == a else 0) < n - off + 1:
                        continue
                seen.add(t)
                if t == tailc:
                    reach = True
                queue.append((t, steps + 1, eaten + (1 if t in present else 0)))
        n = len(queue)
        return (0 if n < L + 2 else 1 if n < 3 * L + 8 else 2), int(reach), n

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
                adjp = [t for t in adj[head] if t in present]
                if not adjp:
                    key = ('n', band, L)
                else:
                    lead = int(rnd > grow)
                    best = None
                    for q in adjp:
                        now = survey(q, actor, L, 0)
                        sc = (-now[2], -now[1], q)
                        if best is None or sc < best[0]:
                            best = (sc, q, now)
                    q, now = best[1], best[2]
                    if now[0] == 2 and now[1] == 1:
                        mt = al = now
                    else:
                        mt = survey(q, actor, L, 1)
                        al = survey(q, actor, L, 2)
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
                    ns = min(2, len([t for t in adj[q] if t != head]))
                    ob = nf = 0
                    for t in adj[q]:
                        if t != head:
                            j = cell.get(t)
                            if j is None:
                                nf += 1
                            elif j == actor:
                                ob = 1
                    nf = min(nf, 2)
                    kind = present[q]
                    alt = -1
                    for t in adj[head]:
                        if t != q and t not in cell:
                            v = survey(t, actor, L, 0, 1 if t in present else 0)[0]
                            if v > alt:
                                alt = v
                    key = ('A', band, L, now[0], mt[0], int(ns == 0), alt, fl, kind, ob)
                    if fl == 0 and now[0] == 0 and alt == 2 and band < 2 and len(samples) < 400 and seq % 3 == 0:
                        samples.append([row['game'], rnd, actor, L, head % w, head // w, q % w, q // w, int(ns == 0), mt[0], kind])
            rec = [key, 0, 0, 0, 0, 0, 0, 0, 0]
            pr = last.get(actor)
            q = buf.get(actor)
            if q is None:
                q = buf[actor] = deque()
            q.append(rec)
            if len(q) > FWD:
                commit(q.popleft())
            last[actor] = rec
            cur = rec
        elif k == 3:
            t = replay.point(p.pointer(0))
            c = t[1] * w + t[0]
            if p.u32(0):
                present[c] = expected.popleft()[1] if expected else 0
            else:
                present.pop(c)
                if sd[actor] == 0:
                    if cur is not None:
                        cur[1] += 1
                    for r in buf.get(actor, ()):
                        r[2] += 1
                        r[7] += 1
                    for r in fam.get(actor, ()):
                        if not r[8]:
                            r[7] += 1
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
                cell[hd] = i
            while len(b) > 1 and b[-1] != tl:
                c = b.pop()
                if cell.get(c) == i and c not in b:
                    del cell[c]
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            s = sd[a]
            for x in bodies[a]:
                if cell.get(x) == a:
                    del cell[x]
            hg[s][bodies[a][0]] -= 1
            sd[c] = s
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                for x in bodies[i]:
                    cell[x] = i
                hg[s][bodies[i][0]] += 1
            if s == 0 and a == actor:
                if cur is None:
                    pass
                q = buf.get(a)
                if q and len(q) >= 2:
                    q[-2][6] = 1
                if q:
                    fam[c] = list(q) + [r for r in fam.get(a, ()) if not r[8]]
        elif k == 11:
            i = p.i32(0)
            b = bodies[i]
            s = sd[i]
            for seg, x in enumerate(b):
                if cell.get(x) == i:
                    del cell[x]
                if seg % 2 == 0:
                    expected.append((x, 1 if s == 0 else 2))
            hg[s][b[0]] -= 1
            bodies.pop(i)
            if s == 0:
                q = buf.pop(i, None)
                if q:
                    n = len(q)
                    for idx, r in enumerate(q):
                        r[4] += len(b)
                        r[7] -= len(b)
                        if idx >= n - 3:
                            r[3] = 1
                    for r in q:
                        commit(r)
                last.pop(i, None)
                for r in fam.pop(i, ()):
                    if not r[8]:
                        r[7] -= len(b)
    assert not expected
    for q in buf.values():
        for r in q:
            commit(r)


def save(tag, body):
    if tag == 'O0':
        Path(OUT + 'ec_alt-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'ec_alt-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'ec_alt-O2.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'ec_alt-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'ec_alt-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'ec_alt-R2.jsonl').write_text(body)
    else:
        Path(OUT + 'ec_alt-test.jsonl').write_text(body)


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
            accs[lay] = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])
            samp[lay] = []
        a2, s2 = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0]), []
        try:
            scan(r, geos, a2, s2)
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
            continue
        for kk, v in a2.items():
            u = accs[lay][kk]
            for z in range(7):
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
