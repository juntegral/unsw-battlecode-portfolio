# Scratch (diag-drops), second pass: as dr_scan.py but rounds 0-400, the adj window is a phase (0: 0-100, 1: 101-150,
# 2: 151-200, 3: 201-300, 4: 301-350, 5: 351-400), mask bits 64 and 128 are set in every round, bit 512 = the dragon is its
# side's longest, the last adj field is who finally ate the pearl it left (tens: 1 itself, 2 a mate of 4 or less, 4 a mate
# of 5 or more, 3 the other side; units: 0 within 3 rounds, 1 within 15, 2 later; 0 never; 9 n/a), and a watcher carries
# z = a longer team mate's head within 9 tiles of a pearl of the death. Output dr_scan2-*.jsonl.
# Scratch (diag-drops): one pass over every game of ours (who=O, team 1119, 500 main ladder games) or of rank-1
# (who=R, team 306, 597 games). Side 0 = the followed team, side 1 = its opponent. One output line per game.
# deaths : every death of rounds 0-300, both sides, with the pearls it drops. Per pearl: nearest head of each side and the
#          heads of each side within 2 and within 5 path steps of the pearl's tile at the death (open edges and portals,
#          bodies ignored; the dying dragon and, in a head-on, the mover that dies with it are left out), who ate it, after
#          how many rounds (followed to the end of the game), the eater's length and how far its head was at the death.
#          Per side the nearest head within 5 steps of any pearl of the death is the "watcher"; its next 6 turns while a
#          pearl of that death still lies are coded as <distance at turn start><code>:
#          E ate a pearl of this death, T ended nearer, A ended farther, P ended as far (lower case: it ate another pearl
#          on the way), S split, R was rammed on another dragon's turn, and its own deaths W wall, O own body, B another
#          body, M head-on it started, N no action, I illegal split, U unpaid sprint, Z timeout. Distance 9 = over 6 steps.
# adj    : every turn of rounds 0-300 that starts with a pearl on a tile the head can step to (the dossier's "adjacent
#          pearl turn"), counted by (side, window, length class, role, pearls beside, kind and age of the least blocked
#          pearl, its blocker mask, what the dragon did, who ate that pearl within 3 rounds).
#          mask bits: 1 enemy head can step onto the pearl's tile, 2 a team mate's head can, 4 pocket rule (open-edge
#          room under 48 and length+1 above half of it), 8 the bot's threat term is non-zero there (length 4 or less: an
#          enemy head of 4 or less beside the tile; longer: an enemy head within clamp(its length, 2, 6) steps),
#          16 fewer than length+2 free tiles reachable from the tile, 32 fewer than 3*length+8, 64 after the leader
#          round a longer team mate's head is within 9 tiles of the pearl, 128 that mate is the side's longest,
#          256 feeding phase (round over 200, 56+ alive) and a mate at least twice as long within 15 tiles.
#          did: 0 ate a pearl that was beside it, 1 moved elsewhere, 2 split, 3 died by no action, 4 died otherwise,
#          5 ate a pearl that was not beside it. after: 9 n/a, 1 itself, 2 a team mate, 3 the other side, 0 nobody in 3.
# Usage: python3 data/analysis/ladder/dossier/work/dr_scan.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LAST = 400
RAD = 6
WATCH = 6
CAUSE = ('W', 'O', 'B')
ACT = ('U', 'I', 'N')


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.moves, self.adj, self.oadj = [], [], []
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append((kind, dest))
                self.moves.append(row)
                self.adj.append(sorted({dest for kind, dest in row if kind != 1}))
                self.oadj.append(sorted({dest for kind, dest in row if kind == 0}))
        self.balls, self.pockets = {}, {}

    def ball(self, c):
        d = self.balls.get(c)
        if d is None:
            d = {c: 0}
            q = deque([c])
            while q:
                z = q.popleft()
                if d[z] >= RAD:
                    continue
                for t in self.adj[z]:
                    if t not in d:
                        d[t] = d[z] + 1
                        q.append(t)
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


def lclass(L):
    return 0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 7 else 4


def scan(row, geos):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    key = (row['layout'], w, h)
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    focal = row['side']
    sd = {i: 0 if teams[i] == focal else 1 for i in bodies}
    queen = [min(i for i in bodies if sd[i] == 0), min(i for i in bodies if sd[i] == 1)]
    heads, occ, alive = {}, Counter(), [0, 0]
    for i, b in bodies.items():
        heads[b[0]] = i
        alive[sd[i]] += 1
        for c in b:
            occ[c] += 1
    grow = 300 if w * h <= 1200 else 150
    present, expected = {}, deque()
    deaths, watches, adjc = [], {}, Counter()
    chk = [[0, 0] for _ in range(6)]
    st = dict(rnd=0, actor=None, dirs=[], used=0, actc=None, ate=set(), split=False, died=None, cur=None, tw=[], hit=None)

    def dist(hd, tiles):
        best = 9
        for t in tiles:
            d = g.ball(t).get(hd)
            if d is not None and d < best:
                best = d
        return best

    def room(p, cap):
        seen = {p}
        q = [p]
        k = 0
        while k < len(q) and len(q) < cap:
            for t in g.adj[q[k]]:
                if t not in seen and occ[t] == 0:
                    seen.add(t)
                    q.append(t)
            k += 1
        return len(q)

    def longest(s):
        best, who = 0, -1
        for j, bb in bodies.items():
            if sd[j] == s and len(bb) > best:
                best, who = len(bb), j
        return best, who

    def make_cur(a, hd, s, L, adjp):
        rnd = st['rnd']
        en = 1 - s
        top_len, top_id = longest(s)
        role = 1 if a == queen[s] else 2 if (L >= 5 and L >= top_len) else 0
        feeder = False
        if rnd > 200 and alive[s] >= 56 and a != queen[s]:
            for j, bb in bodies.items():
                if sd[j] == s and j != a and len(bb) >= 2 * L and g.man(bb[0], hd) <= 15:
                    feeder = True
                    break
        best = None
        for p in sorted(set(adjp)):
            m = 0
            eh, ah = [], []
            for t in g.adj[p]:
                j = heads.get(t)
                if j is None or j == a:
                    continue
                (eh if sd[j] == en else ah).append(j)
            if eh:
                m |= 1
            if ah:
                m |= 2
            pk = g.pocket(p)
            if pk < 48 and L + 1 > pk // 2:
                m |= 4
            if L <= 4:
                if any(len(bodies[j]) <= 4 for j in eh):
                    m |= 8
            else:
                for t, d in g.ball(p).items():
                    j = heads.get(t)
                    if j is not None and sd[j] == en and d <= min(6, max(2, len(bodies[j]))):
                        m |= 8
                        break
            cap = 3 * L + 8
            rm = room(p, cap)
            tight = 0
            if rm < L + 2:
                m |= 16
            elif rm < cap:
                m |= 32
                tight = 1
            for j, bb in bodies.items():
                if sd[j] == s and j != a and len(bb) > L and g.man(bb[0], p) <= 9:
                    m |= 64
                    if j == top_id:
                        m |= 128
            if L >= top_len:
                m |= 512
            if feeder:
                m |= 256
            score = (bin(m).count('1') - tight, m)
            if best is None or score < best[0]:
                best = (score, p, m)
        p, m = best[1], best[2]
        rec = present[p]
        kind = 0 if rec[0] == 0 else 1 if rec[2] == s else 2
        age = rnd - rec[1]
        ac = 0 if age <= 2 else 1 if age <= 15 else 2
        win = 0 if rnd <= 100 else 1 if rnd <= 150 else 2 if rnd <= 200 else 3 if rnd <= 300 else 4 if rnd <= 350 else 5
        return dict(adj=set(adjp), p=p, rec=rec, s=s, win=win,
                    key=(s, win, lclass(L), role, min(2, len(set(adjp))), kind, ac, m))

    def finish_turn():
        a = st['actor']
        if a is None:
            return
        alive_now = a in bodies
        if st['tw']:
            for wt, d0 in st['tw']:
                if wt['done']:
                    continue
                if wt['hit']:
                    code = 'E'
                elif st['split']:
                    code = 'S'
                else:
                    d1 = dist(bodies[a][0], wt['D']['left'])
                    code = 'T' if d1 < d0 else 'A' if (d1 > d0 or d1 == 9) else 'P'
                    if st['ate']:
                        code = code.lower()
                wt['t'].append(str(d0) + code)
                if len(wt['t']) >= WATCH:
                    wt['done'] = True
            st['tw'] = []
        cur = st['cur']
        if cur is not None:
            taken = not cur['adj'].isdisjoint(st['ate'])
            if taken:
                out = 0
            elif not alive_now:
                out = 3 if st['died'] == 'N' else 4
            elif st['split']:
                out = 2
            elif st['ate']:
                out = 5
            else:
                out = 1
            k2 = cur['key'] + (out,)
            if cur['s'] == 0:
                chk[cur['win']][0] += 1
                chk[cur['win']][1] += int(not taken)
            if taken:
                adjc[k2 + (9,)] += 1
            else:
                rec = present.get(cur['p'])
                if rec is cur['rec']:
                    rec[5].append((k2, a, st['rnd']))
                else:
                    adjc[k2 + (8,)] += 1
            st['cur'] = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            finish_turn()
            st['rnd'], st['actor'] = p.i32(0), None
        elif k == 1:
            finish_turn()
            a = p.i32(0)
            st.update(actor=a, dirs=[], used=0, actc=None, ate=set(), split=False, died=None, hit=None)
            b = bodies[a]
            hd, s, L = b[0], sd[a], len(b)
            ws = watches.get(a)
            if ws:
                keep, tw = [], []
                for wt in ws:
                    if wt['done']:
                        continue
                    if not wt['D']['left']:
                        wt['done'] = True
                        wt['end'] = 'G'
                        continue
                    wt['hit'] = False
                    tw.append((wt, dist(hd, wt['D']['left'])))
                    keep.append(wt)
                st['tw'] = tw
                if keep:
                    watches[a] = keep
                else:
                    del watches[a]
            if st['rnd'] <= LAST:
                adjp = [dest for kind, dest in g.moves[hd] if kind != 1 and dest in present]
                if adjp:
                    st['cur'] = make_cur(a, hd, s, L, adjp)
        elif k == 4:
            a = p.pointer(0)
            st['dirs'] = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            st['used'] = 0
            fuel = p.pointer(1)
            st['actc'] = 'Z' if p.bit(32) or (fuel is not None and fuel.bit(64)) else ACT[a.u16(0)] if a and a.u16(0) < 3 else 'N'
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            rnd, actor = st['rnd'], st['actor']
            if p.u32(0):
                assert c not in present
                if expected:
                    xy, D, prow, near = expected.popleft()
                    assert xy == c
                    present[c] = [1, rnd, D['s'] if D is not None else -1, D, prow, [], near]
                else:
                    present[c] = [0, rnd, -1, None, None, [], None]
            else:
                rec = present.pop(c)
                es = sd[actor]
                st['ate'].add(c)
                if rec[3] is not None:
                    D, prow = rec[3], rec[4]
                    prow[7], prow[8], prow[9] = es, rnd - D['r'], len(bodies[actor])
                    prow[10], prow[11] = rec[6].get(actor, 9), actor
                    D['left'].discard(c)
                    for wt, d0 in st['tw']:
                        if wt['D'] is D:
                            wt['hit'] = True
                for k2, did, r0 in rec[5]:
                    who2 = 1 if actor == did else 3 if sd.get(did) != es else 4 if len(bodies[actor]) >= 5 else 2
                    fu = who2 * 10 + (0 if rnd - r0 <= 3 else 1 if rnd - r0 <= 15 else 2)
                    adjc[k2 + (fu,)] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                if heads.get(b[0]) == i:
                    del heads[b[0]]
                b.appendleft(hd)
                heads[hd] = i
                occ[hd] += 1
                if i == st['actor']:
                    st['used'] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = sd[parent]
            for c in bodies[parent]:
                occ[c] -= 1
            if heads.get(bodies[parent][0]) == parent:
                del heads[bodies[parent][0]]
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                sd[i] = 0 if teams[i] == focal else 1
                heads[bodies[i][0]] = i
                for c in bodies[i]:
                    occ[c] += 1
            alive[s] += 1
            if parent == st['actor']:
                st['split'] = True
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            rnd, actor = st['rnd'], st['actor']
            s = sd[i]
            b = bodies[i]
            L, hd = len(b), b[0]
            ps, pL = -1, 0
            if reason == 3:
                if i != actor:
                    cause = 'H'
                    ps, pL = sd[actor], len(bodies[actor])
                    st['hit'] = (s, L)
                else:
                    cause = 'M'
                    if st['hit'] is not None:
                        ps, pL = st['hit']
            elif reason < 3:
                cause = CAUSE[reason]
                if reason == 2 and i == actor and st['used'] < len(st['dirs']):
                    dest = g.moves[hd][st['dirs'][st['used']]][1]
                    for j, bb in bodies.items():
                        if j != i and dest in bb:
                            ps, pL = sd[j], len(bb)
                            break
            else:
                cause = (st['actc'] or 'N') if i == actor else 'N'
            fr = sum(1 for t in g.adj[hd] if occ[t] == 0)
            top = int(L >= 5 and L >= longest(s)[0])
            al = list(alive)
            if heads.get(hd) == i:
                del heads[hd]
            for c in b:
                occ[c] -= 1
            bodies.pop(i)
            alive[s] -= 1
            if i == actor:
                st['died'] = cause
            ws = watches.pop(i, None)
            if ws:
                mine = {id(wt): d0 for wt, d0 in st['tw']} if i == actor else {}
                for wt in ws:
                    if wt['done']:
                        continue
                    d0 = mine.get(id(wt))
                    if d0 is None:
                        d0 = dist(hd, wt['D']['left']) if wt['D']['left'] else 0
                    wt['t'].append(str(d0) + ('R' if cause == 'H' else cause))
                    wt['done'] = True
            tiles = [c for seg, c in enumerate(b) if seg % 2 == 0]
            if rnd <= LAST:
                D = dict(r=rnd, i=i, s=s, L=L, q=int(i == queen[s]), c=cause, ps=ps, pL=pL, fr=fr, al=al, top=top,
                         p=[], w=[None, None], left=set(tiles))
                deaths.append(D)
                excl = actor if (reason == 3 and i != actor) else -1
                bestw = [(9, -1), (9, -1)]
                for c in tiles:
                    near, cnt, nn = {}, [0, 0, 0, 0], [9, 9]
                    for t, d in g.ball(c).items():
                        j = heads.get(t)
                        if j is None or j == excl:
                            continue
                        sj = sd[j]
                        near[j] = d
                        if d <= 2:
                            cnt[sj * 2] += 1
                        if d <= 5:
                            cnt[sj * 2 + 1] += 1
                            if (d, j) < bestw[sj]:
                                bestw[sj] = (d, j)
                        if d < nn[sj]:
                            nn[sj] = d
                    prow = [c, nn[0], nn[1], cnt[0], cnt[1], cnt[2], cnt[3], -1, -1, 0, 9, -1]
                    D['p'].append(prow)
                    expected.append((c, D, prow, near))
                for sj in (0, 1):
                    d, j = bestw[sj]
                    if j >= 0:
                        Lj = len(bodies[j])
                        wt = dict(id=j, d=d, L=Lj, q=int(j == queen[sj]), top=int(Lj >= 5 and Lj >= longest(sj)[0]),
                                  t=[], D=D, done=False, hit=False, end='')
                        wt['z'] = int(any(sd[j2] == sj and j2 != j and len(b2) > Lj and min(g.man(b2[0], c2) for c2 in tiles) <= 9
                                          for j2, b2 in bodies.items()))
                        D['w'][sj] = wt
                        watches.setdefault(j, []).append(wt)
            else:
                for c in tiles:
                    expected.append((c, None, None, None))
    finish_turn()
    assert not expected
    for rec in present.values():
        for k2, did, r0 in rec[5]:
            adjc[k2 + (0,)] += 1
    out = []
    for D in deaths:
        ws = []
        for wt in D['w']:
            ws.append(None if wt is None else [wt['id'], wt['d'], wt['L'], wt['q'], wt['top'], wt['end'], ''.join(wt['t']), wt['z']])
        out.append([D['r'], D['i'], D['s'], D['L'], D['q'], D['c'], D['ps'], D['pL'], D['fr'], D['al'][0], D['al'][1],
                    D['top'], D['p'], ws[0], ws[1]])
    return dict(who=row['who'], game=row['game'], layout=row['layout'], cells=w * h, result=row['result'],
                rating=row['rating'], last_round=st['rnd'], chk=chk, deaths=out,
                adj=[list(kk) + [n] for kk, n in sorted(adjc.items())])


def save(tag, body):
    if tag == 'O0':
        Path(OUT + 'dr_scan2-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'dr_scan2-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'dr_scan2-O2.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'dr_scan2-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'dr_scan2-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'dr_scan2-R2.jsonl').write_text(body)
    else:
        Path(OUT + 'dr_scan2-test.jsonl').write_text(body)


def main():
    who, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[::max(1, len(rows) // limit)][:limit]
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            rec = scan(r, geos)
            assert rec['last_round'] == r['last_round'], (rec['last_round'], r['last_round'])
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 10 == 9:
            print(n + 1, len(rows), 'bad', len(bad), flush=True)
    save('test' if limit else who + str(shard), '\n'.join(out) + '\n')
    print('done', who, shard, len(out), 'bad', bad)


main()
