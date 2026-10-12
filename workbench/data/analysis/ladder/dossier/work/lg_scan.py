"""Scratch (diag-longest): the longest-dragon race, both sides, one JSON line per game.
side 0 = the focus team (1119; 306 for top1), side 1 = its opponent. "top" = a dragon whose length equals its side's maximum.
Usage: python3 lg_scan.py online <label> [limit] | ladder <shard> <shards> [limit] | top1 <shard> <shards> [limit]
Per game: snaps[r] = end-of-round [top0, top1, second0, second1, n0, n1, total0, total1, queen0, queen1, topid0, topid1];
tdeaths = deaths of a top dragon of 6 or more (with the rammer and the dragon's last two turn records);
tsplits = splits by a top dragon of 6 or more; feeds = every death with no valid action; leadeat[s][bucket] = pearls
eaten by a top dragon by origin (nat, feed, own, opp); lt[s][band] = safety counts over top-dragon turns (8 or more)."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
DOS = Path('data/analysis/ladder/dossier')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
BANDS = (8, 12, 16, 20, 31)
DEPTH = 9


def band_of(L):
    k = -1
    for z, lo in enumerate(BANDS):
        if L >= lo:
            k = z
    return k


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.nxt = []
        for y in range(h):
            for x in range(w):
                four = [-1, -1, -1, -1]
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        four[d] = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        four[d] = ((y + dy) % h) * w + (x + dx) % w
                self.nxt.append(four)


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
    nxt = geos[key].nxt

    def man(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    def cheb(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return max(min(dx, w - dx), min(dy, h - dy))

    tile = lambda z: replay.point(z)[1] * w + replay.point(z)[0]
    queen = [min(i for i in bodies if teams[i] == 0), min(i for i in bodies if teams[i] == 1)]
    present = {}
    expected = deque()
    snaps = []
    tdeaths, tsplits, feeds, qdeath = [], [], [], [None, None]
    leadeat = [[[0, 0, 0, 0] for _ in range(5)] for _ in (0, 1)]
    alleat = [[[0, 0, 0, 0] for _ in range(5)] for _ in (0, 1)]
    roundeat = []
    feedfate = [[[0, 0, 0, 0, 0] for _ in range(5)] for _ in (0, 1)]
    deaths = [[[0] * 12 for _ in range(5)] for _ in (0, 1)]
    beside = [[[0] * 12 for _ in range(5)] for _ in (0, 1)]
    lt = [[[0] * 14 for _ in BANDS] for _ in (0, 1)]
    dreat = {}
    birth = {}
    lens50 = {}
    last = {}
    topc = [None, None]
    st = dict(rnd=0, actor=None, used=0, ate=0, act=2, slen=0, shead=0, istop=0, open=None)

    def top(s):
        v = topc[s]
        if v is None:
            v = max((len(b) for i, b in bodies.items() if teams[i] == s), default=0)
            topc[s] = v
        return v

    def topid(s):
        best, bl = -1, 0
        for i, b in bodies.items():
            if teams[i] == s and (len(b) > bl or (len(b) == bl and i < best)):
                best, bl = i, len(b)
        return best

    def snap():
        out = []
        ls = [sorted((len(b) for i, b in bodies.items() if teams[i] == s), reverse=True) for s in (0, 1)]
        for s in (0, 1):
            out.append(ls[s][0] if ls[s] else 0)
        for s in (0, 1):
            out.append(ls[s][1] if len(ls[s]) > 1 else 0)
        for s in (0, 1):
            out.append(len(ls[s]))
        for s in (0, 1):
            out.append(sum(ls[s]))
        for s in (0, 1):
            out.append(len(bodies.get(queen[s], ())))
        for s in (0, 1):
            out.append(topid(s))
        return out

    def threat(t, head, ehead, occ):
        """Enemy heads that can reach tile t on their next turn: [true reach, free + 1 paid, the same two for enemies in view]."""
        res = [0, 0, 0, 0]
        dist = {t: 0}
        dq = deque([t])
        while dq:
            c = dq.popleft()
            dc = dist[c]
            if dc >= DEPTH:
                continue
            for u in nxt[c]:
                if u < 0 or u in dist:
                    continue
                dist[u] = dc + 1
                e = ehead.get(u)
                if e is not None:
                    L = e[1]
                    free = (L + 3) // 4
                    tr = free + L - 2
                    c54 = min(tr, free + 1)
                    view = cheb(head, u) <= 3
                    if dc + 1 <= tr:
                        res[0] += 1
                        if view:
                            res[2] += 1
                    if dc + 1 <= c54:
                        res[1] += 1
                        if view:
                            res[3] += 1
                    continue
                if u in occ:
                    continue
                dq.append(u)
        return res

    def open_turn(a, s):
        b = bodies[a]
        head, L = b[0], len(b)
        ehead = {}
        nview = 0
        en = {}
        for i, bb in bodies.items():
            if teams[i] != s:
                m = man(head, bb[0])
                if m <= 12:
                    ehead[bb[0]] = (i, len(bb))
                    en[i] = [cheb(head, bb[0]), m, len(bb)]
                if cheb(head, bb[0]) <= 3:
                    nview += 1
        own5 = sum(1 for i, bb in bodies.items() if teams[i] == s and i != a and man(head, bb[0]) <= 5)
        rec = dict(r=st['rnd'], head=head, L=L, view=nview, near=len(ehead), opts=[], end=None, steps=0, ate=0, endthr=None, en=en, own5=own5)
        occ = None
        if ehead:
            occ = set()
            for bb in bodies.values():
                occ.update(bb)
            for d in range(4):
                t = nxt[head][d]
                if t < 0:
                    continue
                if t in occ:
                    rec['opts'].append([t, 1, 0, 0, 0, 0])
                else:
                    rec['opts'].append([t, 0] + threat(t, head, ehead, occ))
        st['open'] = (a, s, rec, ehead, occ)

    def close_turn():
        o = st['open']
        if o is None:
            return
        a, s, rec, ehead, occ = o
        st['open'] = None
        alive = a in bodies
        rec['steps'], rec['ate'] = st['used'], st['ate']
        rec['end'] = bodies[a][0] if alive else -1
        k = band_of(rec['L'])
        row = lt[s][k] if k >= 0 else None
        if row is not None:
            row[0] += 1
        if ehead and alive:
            if row is not None:
                row[1] += 1
            e = rec['end']
            thr = None
            for o2 in rec['opts']:
                if o2[0] == e and st['used'] == 1:
                    thr = o2[2:]
            if thr is None:
                thr = [0, 0, 0, 0] if e == rec['head'] else threat(e, rec['head'], ehead, occ)
            rec['endthr'] = thr
            free = [o2 for o2 in rec['opts'] if not o2[1]]
            clean = [int(any(o2[2 + z] == 0 for o2 in free)) for z in range(4)]
            rec['clean'] = clean
            rec['nopen'] = len(free)
            if row is not None:
                for z in range(4):
                    if thr[z]:
                        row[2 + 2 * z] += 1
                        if clean[z]:
                            row[3 + 2 * z] += 1
                if free and not clean[0]:
                    row[10] += 1
                if free and not clean[2]:
                    row[11] += 1
                if st['used'] > 1:
                    row[12] += 1
        pr = last.get(a)
        last[a] = (pr[1] if pr else None, rec)

    def cat_of(origin, s):
        if origin is None:
            return 0
        if origin['s'] != s:
            return 3
        return 1 if origin['delib'] else 2

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close_turn()
            new = p.i32(0)
            if new > 0 or snaps:
                snaps.append(snap())
            if st['rnd'] % 50 == 0:
                lens50[st['rnd']] = dict((i, len(b)) for i, b in bodies.items() if len(b) >= 6)
            st['rnd'], st['actor'] = new, None
        elif k == 1:
            close_turn()
            a = p.i32(0)
            b = bodies[a]
            s = teams[a]
            st['actor'], st['used'], st['ate'], st['act'] = a, 0, 0, 2
            st['shead'], st['slen'] = b[0], len(b)
            st['istop'] = int(len(b) >= top(s))
            if st['istop'] and len(b) >= 6:
                open_turn(a, s)
        elif k == 4:
            a = p.pointer(0)
            kind = a.u16(0) if a else 2
            st['act'] = min(kind, 2)
        elif k == 3:
            c = tile(p.pointer(0))
            if p.u32(0):
                if expected and expected[0][0] == c:
                    present[c] = expected.popleft()[1]
                else:
                    present[c] = None
            else:
                origin = present.pop(c, None)
                a = st['actor']
                if a is not None and a in bodies:
                    s = teams[a]
                    cat = cat_of(origin, s)
                    bk = min(st['rnd'] // 100, 4)
                    alleat[s][bk][cat] += 1
                    st['ate'] += 1
                    de = dreat.get(a)
                    if de is None:
                        de = [0] * 20
                        dreat[a] = de
                    de[bk * 4 + cat] += 1
                    if st['istop']:
                        leadeat[s][bk][cat] += 1
                        roundeat.append([st['rnd'], s, cat, a, st['slen']])
                    if origin is not None and origin['delib']:
                        ds = origin['s']
                        who = 3 if s != ds else 0 if st['istop'] else 1 if st['slen'] >= 8 else 2
                        feedfate[ds][origin['bk']][who] += 1
                        origin['left'][0] -= 1
                    topc[s] = None
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(p.pointer(0)), tile(p.pointer(1))
            b = bodies[i]
            before = len(b)
            if b[0] != hd:
                b.appendleft(hd)
                if i == st['actor']:
                    st['used'] += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            if len(b) != before:
                topc[teams[i]] = None
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = teams[parent]
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(pt) for pt in p.pointer(z))
            teams[child] = 0 if 'AB'[p.u16(8)] == own_letter else 1
            birth[child] = [st['rnd'], len(bodies[child]), parent]
            topc[s] = None
            if st['istop'] and st['slen'] >= 6 and parent == st['actor']:
                tsplits.append([st['rnd'], s, st['slen'], len(bodies[parent]), len(bodies[child]), parent, int(parent == queen[s])])
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = teams[i]
            actor = st['actor']
            b = bodies[i]
            L, head = len(b), b[0]
            bk = min(st['rnd'] // 100, 4)
            own_move = int(i == actor)
            code = (0, 1, 2, 3 if own_move else 4, 5 + (st['act'] if own_move else 2))[min(reason, 4)]
            deaths[s][bk][code] += 1
            deaths[s][bk][8] += L
            tl = top(s)
            was_top = L >= tl
            mates = [(man(head, bb[0]), len(bb), j) for j, bb in bodies.items() if teams[j] == s and j != i]
            foes = [(man(head, bb[0]), len(bb), j) for j, bb in bodies.items() if teams[j] != s]
            dtop = min((m[0] for m in mates if m[1] >= tl), default=99) if not was_top else 0
            if not was_top and tl >= 8 and dtop <= 3:
                beside[s][bk][code] += 1
                beside[s][bk][8] += L
            if reason == 4:
                freeb = 0
                for t in nxt[head]:
                    if t >= 0 and not any(t in bb for bb in bodies.values()):
                        freeb = 1
                        break
                left = [(L + 1) // 2]
                origin = dict(s=s, delib=freeb, bk=bk, left=left)
                feeds.append([st['rnd'], s, L, dtop, tl, st['act'] if own_move else 2, len(mates) + 1, left, freeb])
                if freeb:
                    deaths[s][bk][9] += L
                    deaths[s][bk][10] += (L + 1) // 2
                else:
                    deaths[s][bk][11] += 1
            else:
                origin = dict(s=s, delib=0, bk=bk, left=[0])
            if i == queen[s]:
                qdeath[s] = [st['rnd'], L, int(reason), own_move]
            if was_top and L >= 6:
                if own_move:
                    close_turn()
                lr = last.get(i)
                d = dict(s=s, r=st['rnd'], id=i, L=L, q=int(i == queen[s]), reason=int(reason), own=own_move, act=st['act'] if own_move else None,
                         second=max((m[1] for m in mates), default=0), opp=top(1 - s), n=[len(mates), len(foes)],
                         own5=sum(1 for m in mates if m[0] <= 5), own3=sum(1 for m in mates if m[0] <= 3), en5=sum(1 for m in foes if m[0] <= 5),
                         own5long=sum(1 for m in mates if m[0] <= 5 and m[1] >= 4),
                         last=lr[1] if lr else None, prev=lr[0] if lr else None)
                if not own_move and actor is not None:
                    d['ram'] = dict(id=actor, s=teams[actor], L=st['slen'], steps=st['used'] + 1, mdist=man(st['shead'], head),
                                    cheb=cheb(st['shead'], head), free=(st['slen'] + 3) // 4, q=int(actor == queen[teams[actor]]))
                    if lr and lr[1] and lr[1]['r'] >= st['rnd'] - 1:
                        d['ram']['then'] = lr[1]['en'].get(actor)
                    if lr and lr[1]:
                        kk = band_of(lr[1]['L'])
                        if kk >= 0 and reason == 3:
                            lt[s][kk][13] += 1
                tdeaths.append(d)
            for seg, c in enumerate(b):
                if seg % 2 == 0:
                    expected.append((c, origin))
            bodies.pop(i)
            last.pop(i, None)
            topc[s] = None
            if st['open'] is not None and st['open'][0] == i:
                st['open'] = None
    close_turn()
    snaps.append(snap())
    final = snaps[-1]
    res = root.pointer(4)
    winner = ('A', 'B')[res.u16(6)] if res.u16(4) == 1 else None
    win = None if winner is None else int(winner == own_letter)
    if not final[4] or not final[5]:
        decided = 'elimination'
    elif final[8] != final[9]:
        decided = 'queen'
    elif final[0] != final[1]:
        decided = 'longest'
    else:
        decided = 'total'
    for f in feeds:
        f[7] = f[7][0]
    for f in feeds:
        if f[8]:
            feedfate[f[1]][min(f[0] // 100, 4)][4] += f[7]
    tops = []
    for s in (0, 1):
        i = final[10 + s]
        tops.append(dict(id=i, L=final[s], birth=birth.get(i), eat=dreat.get(i), q=int(i == queen[s]),
                         lens=dict((r, v.get(i, 0)) for r, v in lens50.items())) if i >= 0 else None)
    out = dict(info)
    out.update(w=w, h=h, cells=w * h, win=win, decided=decided, last=st['rnd'], queen=queen, qdeath=qdeath, snaps=snaps, final=final,
               tdeaths=tdeaths, tsplits=tsplits, feeds=feeds, leadeat=leadeat, alleat=alleat, roundeat=roundeat, feedfate=feedfate,
               deaths=deaths, beside=beside, lt=lt, tops=tops)
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
                                                      rating=r.get('opponent_rating'), row_result=r['result'])))
    return jobs[:limit] if limit else jobs


def emit(tag, body):
    if tag == 'm1':
        Path(WORK + 'lg_scan-m1.jsonl').write_text(body)
    elif tag == 'm2':
        Path(WORK + 'lg_scan-m2.jsonl').write_text(body)
    elif tag == 'm3':
        Path(WORK + 'lg_scan-m3.jsonl').write_text(body)
    elif tag == 'b1':
        Path(WORK + 'lg_scan-b1.jsonl').write_text(body)
    elif tag == 'b2':
        Path(WORK + 'lg_scan-b2.jsonl').write_text(body)
    elif tag == 'q1':
        Path(WORK + 'lg_scan-q1.jsonl').write_text(body)
    elif tag == 'q2':
        Path(WORK + 'lg_scan-q2.jsonl').write_text(body)
    elif tag == 'L0':
        Path(WORK + 'lg_scan-L0.jsonl').write_text(body)
    elif tag == 'L1':
        Path(WORK + 'lg_scan-L1.jsonl').write_text(body)
    elif tag == 'T0':
        Path(WORK + 'lg_scan-T0.jsonl').write_text(body)
    elif tag == 'T1':
        Path(WORK + 'lg_scan-T1.jsonl').write_text(body)
    else:
        Path(WORK + 'lg_scan-test.jsonl').write_text(body)


def main():
    src = sys.argv[1]
    if src == 'online':
        label = sys.argv[2]
        jobs = jobs_online(label)
        tag = {'agg7-m1': 'm1', 'agg7-m2': 'm2', 'agg7-m3': 'm3', 'agg7-b1': 'b1', 'agg7-b2': 'b2', 'agg8-q1': 'q1', 'agg8-q2': 'q2'}.get(label, 'test')
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
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((info['game'], repr(e)[:300]))
        if n % 10 == 9:
            print(n + 1, len(jobs), len(bad), flush=True)
    emit(tag, '\n'.join(out) + '\n')
    print('done', src, tag, len(out), 'bad', bad, flush=True)


main()
