"""Scratch (diag-theirqueen): one record per queen turn for BOTH queens, plus every sure chance at a queen's head.
side 0 = the focus team (1119; 306 for top1), side 1 = its opponent. queen = lowest starting id of a side.
Usage: python3 tq_scan.py online <label> | ladder <shard> <shards> | top1 <shard> <shards>   [limit]
Writes tq_scan-<tag>.jsonl, one JSON line per game. Turn record = list, index names in tq_agg.py (F)."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
DOS = Path('data/analysis/ladder/dossier')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAP = 8
CHECK = (10, 25, 50, 100, 150, 200, 300, 400)


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.nxt, self.por, self.kelp = [], [], []
        for y in range(h):
            for x in range(w):
                four, pf, kc = [-1, -1, -1, -1], [0, 0, 0, 0], 0
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 1:
                        kc += 1
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        four[d] = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                        pf[d] = 1
                    else:
                        four[d] = ((y + dy) % h) * w + (x + dx) % w
                self.nxt.append(four)
                self.por.append(pf)
                self.kelp.append(kc)
        self.balls = {}
        self.o3 = {}
        self.pockets(60)

    def ball(self, src):
        s = self.balls.get(src)
        if s is None:
            s = {src: 0}
            q = deque([src])
            while q:
                c = q.popleft()
                if s[c] >= CAP:
                    continue
                for t in self.nxt[c]:
                    if t >= 0 and t not in s:
                        s[t] = s[c] + 1
                        q.append(t)
            self.balls[src] = s
        return s

    def open3(self, src):
        v = self.o3.get(src)
        if v is None:
            v = sum(1 for x in self.ball(src).values() if x <= 3)
            self.o3[src] = v
        return v

    def pockets(self, limit):
        """pocket[c] = size of the smallest region holding c that one edge (a bridge of the terrain graph) cuts off, 0 if none of at most limit cells."""
        w, h = self.w, self.h
        n = w * h
        adj = [[] for _ in range(n)]
        ids = {}
        for c in range(n):
            x, y = c % w, c // w
            for d in range(4):
                t = self.nxt[c][d]
                if t < 0 or t == c:
                    continue
                e = edge_id(w, h, x, y, d)
                kind, pid = self.edges.get(e, (0, -1))
                key = (min(c, t), max(c, t), kind == 2, pid if kind == 2 else e)
                k = ids.setdefault(key, len(ids))
                adj[c].append((t, k))
        tin, low, tout, order = [-1] * n, [0] * n, [0] * n, []
        pocket, comp = [0] * n, [0] * n
        for root in range(n):
            if tin[root] >= 0:
                continue
            t0 = len(order)
            tin[root] = low[root] = len(order)
            order.append(root)
            stack = [[root, -1, 0]]
            bridges = []
            while stack:
                top = stack[-1]
                u = top[0]
                if top[2] < len(adj[u]):
                    v, k = adj[u][top[2]]
                    top[2] += 1
                    if k == top[1]:
                        continue
                    if tin[v] >= 0:
                        if tin[v] < low[u]:
                            low[u] = tin[v]
                    else:
                        tin[v] = low[v] = len(order)
                        order.append(v)
                        stack.append([v, k, 0])
                else:
                    stack.pop()
                    tout[u] = len(order) - 1
                    if stack:
                        pu = stack[-1][0]
                        if low[u] < low[pu]:
                            low[pu] = low[u]
                        if low[u] > tin[pu]:
                            bridges.append(u)
            size = len(order) - t0
            for c in order[t0:]:
                comp[c] = size
            for v in bridges:
                sub = tout[v] - tin[v] + 1
                other = size - sub
                if sub <= other and sub <= limit:
                    zs = range(tin[v], tout[v] + 1)
                    val = sub
                elif other < sub and other <= limit:
                    zs = list(range(t0, tin[v])) + list(range(tout[v] + 1, t0 + size))
                    val = other
                else:
                    continue
                for z in zs:
                    c = order[z]
                    if pocket[c] == 0 or val < pocket[c]:
                        pocket[c] = val
        self.pocket, self.comp = pocket, comp


def scan(path, own_letter, info, geos):
    root = replay.load(Path(path)).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 0 if 'AB'[int(q[1])] == own_letter else 1
        elif q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    key = (w, h, tuple(sorted(raw)))
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    nxt, por = g.nxt, g.por

    def man(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    tile = lambda z: replay.point(z)[1] * w + replay.point(z)[0]
    queen = [min(i for i in bodies if teams[i] == 0), min(i for i in bodies if teams[i] == 1)]
    start = [bodies[queen[0]][0], bodies[queen[1]][0]]
    recs = [[], []]
    fate = [None, None]
    splits, attacks, bodykills = [[], []], [[], []], [[], []]
    chances = []
    near = [[0, 0], [0, 0]]
    snaps = {}
    present = set()
    st = dict(rnd=-1, actor=None, used=0, dirs=[], ate=0, act=2, child=0, died=0, open=None, ch=None, shead=0, slen=0)

    def snap():
        out = []
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if teams[i] == s]
            out.append([len(bodies.get(queen[s], ())), len(ls), max(ls, default=0), sum(ls)])
        return out

    def close_turn():
        o = st['open']
        if o is None:
            return
        s, rec, threats = o
        q = queen[s]
        alive = q in bodies
        rec[19], rec[20], rec[22], rec[25], rec[28] = st['act'], st['used'], st['ate'], st['died'], st['child']
        rec[21] = len(bodies[q]) if alive else 0
        rec[23] = bodies[q][0] if alive else -1
        if threats and alive:
            ball = g.ball(bodies[q][0])
            rec[24] = min(ball.get(t, 9) for t in threats)
        st['open'] = None

    def open_turn(s, q):
        b = bodies[q]
        head, L = b[0], len(b)
        ball = g.ball(head)
        occupied = set()
        ob2 = 0
        own_heads, en = [], []
        for i, bb in bodies.items():
            occupied.update(bb)
            if teams[i] == s:
                if i != q:
                    own_heads.append(bb[0])
                    for c in bb:
                        if man(c, head) <= 2:
                            ob2 += 1
            else:
                en.append((i, bb[0], len(bb)))
        od = [man(head, x) for x in own_heads]
        o3 = sum(1 for x in od if x <= 3)
        o5 = sum(1 for x in od if x <= 5)
        nom = min(od, default=20)
        e3m = e5m = ep3 = ep3n = ep5n = inr = sep = ep3s = 0
        ne, neL, nem, nearest = 9, 0, 20, -1
        threats = []
        eq = queen[1 - s]
        for i, eh, eL in en:
            m = man(head, eh)
            p = ball.get(eh, 9)
            if m <= 3:
                e3m += 1
                if p > 3:
                    sep += 1
            if m <= 5:
                e5m += 1
            if m < nem:
                nem, nearest = m, eh
            if p < ne:
                ne, neL = p, eL
            if p <= 3:
                ep3 += 1
                if i != eq:
                    ep3n += 1
                    threats.append(eh)
                    if eL <= 4:
                        ep3s += 1
            if p <= 5 and i != eq:
                ep5n += 1
            if i != eq and p <= (eL + 3) // 4 + eL - 2:
                inr += 1
        mn = -1
        if nem <= 8:
            mn = int(any(man(x, nearest) < nem for x in own_heads))
        fx = sum(1 for t in nxt[head] if t >= 0 and t not in occupied)
        db = min((ball.get(t, 9) for t in threats), default=-1)
        pd, p3 = 9, 0
        for c in present:
            dd = ball.get(c, 9)
            if dd < pd:
                pd = dd
            if dd <= 3:
                p3 += 1
        rec = [st['rnd'], head, L, man(head, start[s]), o3, o5, e3m, e5m, ep3, ne, neL, min(nem, 20), min(nom, 20), g.kelp[head], fx,
               g.pocket[head], mn, inr, ob2, 2, 0, 0, 0, -1, -1, 0, 0, ep3n, 0, sep, db, ep5n, g.open3(head), len(own_heads) + 1, len(en), pd, p3, ep3s]
        recs[s].append(rec)
        st['open'] = (s, rec, threats)

    def chance(m, mover):
        tq = queen[1 - m]
        if tq not in bodies:
            return
        b = bodies[mover]
        head, L = b[0], len(b)
        th = bodies[tq][0]
        d0 = man(head, th)
        if d0 <= 5:
            near[m][1] += 1
        if d0 > 3:
            return
        near[m][0] += 1
        reach = min(3, (L + 3) // 4 + L - 2)
        occupied = set()
        for bb in bodies.values():
            occupied.update(bb)
        dist = {head: 0}
        dq = deque([head])
        found = 0
        while dq and not found:
            c = dq.popleft()
            if dist[c] >= reach:
                continue
            for d in range(4):
                t = nxt[c][d]
                if t < 0 or por[c][d] or t in dist:
                    continue
                if t == th:
                    found = dist[c] + 1
                    break
                if t in occupied:
                    continue
                dist[t] = dist[c] + 1
                dq.append(t)
        if found:
            ch = [st['rnd'], m, L, found, 0, len(bodies[tq])]
            chances.append(ch)
            st['ch'] = ch

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close_turn()
            if st['rnd'] in CHECK:
                snaps[st['rnd']] = snap()
            st['rnd'], st['actor'] = p.i32(0), None
        elif k == 1:
            close_turn()
            a = p.i32(0)
            st['actor'], st['used'], st['dirs'], st['ate'], st['act'], st['child'], st['died'], st['ch'] = a, 0, [], 0, 2, 0, 0, None
            st['shead'], st['slen'] = bodies[a][0], len(bodies[a])
            s = teams[a]
            if a == queen[s]:
                open_turn(s, a)
            else:
                chance(s, a)
        elif k == 4:
            a = p.pointer(0)
            kind = a.u16(0) if a else 2
            st['dirs'] = [int(x) for x in a.pointer(0)] if a and kind == 0 and a.pointer(0) is not None else []
            st['act'] = min(kind, 2)
        elif k == 3:
            c = tile(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
                if st['actor'] is not None:
                    st['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(p.pointer(0)), tile(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == st['actor']:
                    st['used'] += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(pt) for pt in p.pointer(z))
            teams[child] = 0 if 'AB'[p.u16(8)] == own_letter else 1
            s = teams[parent]
            if parent == queen[s]:
                splits[s].append([st['rnd'], st['slen'], len(bodies[parent]), len(bodies[child])])
                st['child'] = len(bodies[child])
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = teams[i]
            actor = st['actor']
            b = bodies[i]
            if i == queen[s]:
                head = b[0]
                mates = [man(head, bb[0]) for j, bb in bodies.items() if teams[j] == s and j != i]
                f = dict(r=st['rnd'], L=len(b), reason=reason, own_move=int(i == actor), ds=man(head, start[s]), o3=sum(1 for x in mates if x <= 3),
                         o5=sum(1 for x in mates if x <= 5), kelp=g.kelp[head], pocket=g.pocket[head], head=head)
                if i != actor and actor is not None:
                    f.update(mover=actor, mside=teams[actor], mL=st['slen'], msteps=st['used'] + 1, mdist=man(st['shead'], head),
                             mqueen=int(actor == queen[teams[actor]]))
                    if recs[s]:
                        recs[s][-1][26] = 1
                    if st['ch'] is not None and reason == 3:
                        st['ch'][4] = 1
                elif i == actor:
                    st['died'] = (1, 2, 3, 4, 5)[min(reason, 4)]
                fate[s] = f
            if actor is not None and i != actor and reason == 3 and actor == queen[teams[actor]] and teams[actor] != s:
                attacks[teams[actor]].append([st['rnd'], st['slen'], len(b), int(i == queen[s])])
            if reason == 2 and i == actor and st['used'] < len(st['dirs']):
                dest = nxt[b[0]][st['dirs'][st['used']]]
                eq = queen[1 - s]
                if eq in bodies and dest in bodies[eq]:
                    bodykills[1 - s].append([st['rnd'], len(b), len(bodies[eq])])
            bodies.pop(i)
    close_turn()
    final = snap()
    res = root.pointer(4)
    winner = ('A', 'B')[res.u16(6)] if res.u16(4) == 1 else None
    win = None if winner is None else int(winner == own_letter)
    if not final[0][1] or not final[1][1]:
        decided = 'elimination'
    elif final[0][0] != final[1][0]:
        decided = 'queen'
    elif final[0][2] != final[1][2]:
        decided = 'longest'
    else:
        decided = 'total'
    out = dict(info)
    out.update(w=w, h=h, cells=w * h, win=win, decided=decided, last=st['rnd'], start=start, queen=queen, recs=recs, fate=fate,
               splits=splits, attacks=attacks, bodykills=bodykills, chances=chances, near=near, snaps=snaps, final=final,
               spocket=[g.pocket[start[0]], g.pocket[start[1]]], scomp=[g.comp[start[0]], g.comp[start[1]]])
    return out


def jobs_online(label):
    folder = Path('data/online/smoke') / (label + '-new')
    jobs = []
    for rp in sorted(folder.glob('M*.replay')):
        gid = int(rp.stem[1:])
        mp = folder / ('game-%d.json' % gid)
        if not mp.exists():
            continue
        meta = json.loads(mp.read_text())
        own = 'A' if meta['teamAId'] == 1119 else 'B'
        other = 'B' if own == 'A' else 'A'
        jobs.append((rp, own, dict(game=gid, label=label, map=meta['mapName'], opp=meta['team' + other + 'Name'], meta_winner=meta.get('winner'))))
    return jobs


def jobs_rows(src, shard, shards, limit):
    name = 'per-game.jsonl' if src == 'ladder' else 'target/per-game-top1.jsonl'
    jobs = []
    n = 0
    for line in (DOS / name).read_text().splitlines():
        r = json.loads(line)
        if r['relation'] != 'us':
            continue
        n += 1
        if (n - 1) % shards != shard:
            continue
        jobs.append((r['replay'], r['our_side'], dict(game=r['game'], label=src, map=r['map_name'], layout=r['layout_key'], opp=None,
                                                      row_result=r['result'], row_q=r['final_reconstructed']['queen_length'])))
    return jobs[:limit] if limit else jobs


def emit(tag, body):
    if tag == 'm1':
        Path(WORK + 'tq_scan-m1.jsonl').write_text(body)
    elif tag == 'm2':
        Path(WORK + 'tq_scan-m2.jsonl').write_text(body)
    elif tag == 'm3':
        Path(WORK + 'tq_scan-m3.jsonl').write_text(body)
    elif tag == 'b1':
        Path(WORK + 'tq_scan-b1.jsonl').write_text(body)
    elif tag == 'b2':
        Path(WORK + 'tq_scan-b2.jsonl').write_text(body)
    elif tag == 'q1':
        Path(WORK + 'tq_scan-q1.jsonl').write_text(body)
    elif tag == 'q2':
        Path(WORK + 'tq_scan-q2.jsonl').write_text(body)
    elif tag == 'sr51':
        Path(WORK + 'tq_scan-sr51.jsonl').write_text(body)
    elif tag == 'L0':
        Path(WORK + 'tq_scan-L0.jsonl').write_text(body)
    elif tag == 'L1':
        Path(WORK + 'tq_scan-L1.jsonl').write_text(body)
    elif tag == 'T0':
        Path(WORK + 'tq_scan-T0.jsonl').write_text(body)
    elif tag == 'T1':
        Path(WORK + 'tq_scan-T1.jsonl').write_text(body)
    else:
        Path(WORK + 'tq_scan-test.jsonl').write_text(body)


def main():
    src = sys.argv[1]
    if src == 'online':
        label = sys.argv[2]
        jobs = jobs_online(label)
        tag = {'agg7-m1': 'm1', 'agg7-m2': 'm2', 'agg7-m3': 'm3', 'agg7-b1': 'b1', 'agg7-b2': 'b2', 'agg8-q1': 'q1', 'agg8-q2': 'q2',
               'sr51-bob1': 'sr51'}.get(label, 'test')
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        if limit:
            jobs, tag = jobs[:limit], 'test'
    else:
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        jobs = jobs_rows(src, int(sys.argv[2]), int(sys.argv[3]), limit)
        tag = 'test' if limit else ('L' if src == 'ladder' else 'T') + sys.argv[2]
    geos, bad, out = {}, [], []
    for n, (path, own, info) in enumerate(jobs):
        try:
            rec = scan(path, own, info, geos)
            if info.get('meta_winner') in ('a', 'b'):
                assert (rec['win'] == 1) == (info['meta_winner'].upper() == own), (rec['win'], info)
            if 'row_result' in info:
                assert (rec['win'] == 1) == (info['row_result'] == 'win'), (rec['win'], info)
                assert rec['final'][0][0] == info['row_q'], (rec['final'], info)
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((info['game'], repr(e)[:300]))
        if n % 10 == 9:
            print(n + 1, len(jobs), len(bad), flush=True)
    emit(tag, '\n'.join(out) + '\n')
    print('done', src, tag, len(out), 'bad', bad, flush=True)


main()
