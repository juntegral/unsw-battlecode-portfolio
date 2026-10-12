"""Scratch (diag-topqueen): how a queen moves at each distance from the nearest enemy head (enemy queen not counted).
One record per queen turn that starts with such a head within 8 steps (path over open edges and portals, bodies ignored):
[round, her length, steps to it before, steps from her new head to the same heads after (-1 dead), Manhattan before, Manhattan after,
 steps she moved, child length if she split, own heads within 5 tiles, length of that nearest head, heads within 5 steps, pearls eaten,
 died on her own move, rammed before her next turn, a mate nearer that head than she is, free tiles beside her head, kelp sides of her tile,
 index of this turn among her turns]. Also her turn count per band and her fate.
Usage: python3 tq2_near.py top3 <shard> <shards> | top1 <team> <shard> <shards> | online <label>   -> tq2_near-<tag>.jsonl"""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAP = 8
CHECK = (10, 25, 50, 75, 100, 150, 200, 250, 300, 400)
STUDIED = (454, 157, 306, 70)


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
        self.comp = self.components()

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

    def components(self):
        n = self.w * self.h
        comp = [0] * n
        seen = [False] * n
        for root in range(n):
            if seen[root]:
                continue
            seen[root] = True
            cells = [root]
            q = deque([root])
            while q:
                c = q.popleft()
                for t in self.nxt[c]:
                    if t >= 0 and not seen[t]:
                        seen[t] = True
                        cells.append(t)
                        q.append(t)
            for c in cells:
                comp[c] = len(cells)
        return comp




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
    nxt = g.nxt

    def man(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    tile = lambda z: replay.point(z)[1] * w + replay.point(z)[0]
    queen = [min(i for i in bodies if teams[i] == 0), min(i for i in bodies if teams[i] == 1)]
    recs = [[], []]
    turns = [[0, 0, 0, 0], [0, 0, 0, 0]]
    nturn = [0, 0]
    fate = [None, None]
    st = dict(rnd=-1, actor=None, used=0, ate=0, child=0, died=0, open=None)

    def close_turn():
        o = st['open']
        if o is None:
            return
        s, rec, heads = o
        q = queen[s]
        rec[6], rec[7], rec[11], rec[12] = st['used'], st['child'], st['ate'], st['died']
        if q in bodies:
            hd = bodies[q][0]
            ball = g.ball(hd)
            rec[3] = min(ball.get(t, 9) for t in heads)
            rec[5] = min(man(hd, t) for t in heads)
        st['open'] = None

    def open_turn(s, q):
        b = bodies[q]
        head, L = b[0], len(b)
        r = st['rnd']
        turns[s][0 if r <= 50 else 1 if r <= 100 else 2 if r <= 300 else 3] += 1
        nturn[s] += 1
        ball = g.ball(head)
        eq = queen[1 - s]
        best, bestL, n5 = 9, 0, 0
        heads = []
        for i, bb in bodies.items():
            if teams[i] != s and i != eq:
                p = ball.get(bb[0], 9)
                if p <= 8:
                    heads.append(bb[0])
                    if p <= 5:
                        n5 += 1
                    if p < best:
                        best, bestL, bh = p, len(bb), bb[0]
        if not heads:
            return
        occupied = set()
        o5 = 0
        mn = 0
        for i, bb in bodies.items():
            occupied.update(bb)
            if teams[i] == s and i != q:
                if man(head, bb[0]) <= 5:
                    o5 += 1
                if g.ball(bb[0]).get(bh, 9) < best:
                    mn = 1
        fx = sum(1 for t in nxt[head] if t >= 0 and t not in occupied)
        rec = [r, L, best, -1, min(man(head, t) for t in heads), -1, 0, 0, o5, bestL, n5, 0, 0, 0, mn, fx, g.kelp[head], nturn[s]]
        recs[s].append(rec)
        st['open'] = (s, rec, heads)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close_turn()
            st['rnd'], st['actor'] = p.i32(0), None
        elif k == 1:
            close_turn()
            a = p.i32(0)
            st['actor'], st['used'], st['ate'], st['child'], st['died'] = a, 0, 0, 0, 0
            s = teams[a]
            if a == queen[s]:
                open_turn(s, a)
        elif k == 3:
            if not p.u32(0) and st['actor'] is not None:
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
            if parent == queen[teams[parent]]:
                st['child'] = len(bodies[child])
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = teams[i]
            actor = st['actor']
            if i == queen[s]:
                fate[s] = [st['rnd'], len(bodies[i]), reason, int(i == actor), nturn[s]]
                if i != actor and actor is not None and reason == 3:
                    if recs[s] and recs[s][-1][17] == nturn[s]:
                        recs[s][-1][13] = 1
                elif i == actor:
                    st['died'] = 1
            bodies.pop(i)
    close_turn()
    res = root.pointer(4)
    winner = ('A', 'B')[res.u16(6)] if res.u16(4) == 1 else None
    out = dict(info)
    out.update(w=w, h=h, win=None if winner is None else int(winner == own_letter), recs=recs, turns=turns, fate=fate)
    return out


def meta_job(rp, mp, team, src, battle):
    meta = json.loads(mp.read_text())
    if team is None:
        team = meta['teamAId'] if meta['teamAId'] in STUDIED else meta['teamBId']
    if meta['teamAId'] == team:
        own, other = 'A', 'B'
    elif meta['teamBId'] == team:
        own, other = 'B', 'A'
    else:
        return None
    return (rp, own, dict(game=meta['id'], src=src, battle=battle, map=meta['mapName'], t=[meta['team' + own + 'Id'], meta['team' + other + 'Id']],
                          names=[meta['team' + own + 'Name'], meta['team' + other + 'Name']],
                          elo=[meta.get('team' + own + 'Elo'), meta.get('team' + other + 'Elo')], meta_winner=meta.get('winner'),
                          ranked=meta.get('ranked')))


def folder_jobs(folder, team, src, battle):
    jobs = []
    for rp in sorted(folder.glob('M*.replay')):
        mp = folder / ('game-' + rp.stem[1:] + '.json')
        if not mp.exists():
            continue
        j = meta_job(rp, mp, team, src, battle)
        if j is not None:
            jobs.append(j)
    return jobs


def jobs_top3():
    base = Path('data/online/top3')
    who = {}
    upto = 0
    for a in sys.argv:
        if a.startswith('upto'):
            upto = int(a[4:])
    rows = [json.loads(line) for line in (base / 'index.jsonl').read_text().splitlines() if line.strip()]
    for r in (rows[:upto] if upto else rows):
        who[str(r['battle'])] = r['team']
    jobs = []
    for folder in sorted(x for x in base.iterdir() if x.is_dir()):
        if upto and folder.name not in who:
            continue
        jobs += folder_jobs(folder, who.get(folder.name), 'top3', folder.name)
    return jobs


def jobs_top1(team):
    base = Path('data/online/top1')
    jobs = []
    for line in Path('data/top1/index.jsonl').read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if (r['team'] != team) if team else (r['team'] in (91, 264, 306, 842, 454)):
            continue
        folder = base / str(r['battle'])
        if folder.is_dir():
            jobs += folder_jobs(folder, r['team'], 'top1', str(r['battle']))
    return jobs


def emit(tag, body):
    if tag == 'top3-0':
        Path(WORK + 'tq2_near-top3-0.jsonl').write_text(body)
    elif tag == 'top3-1':
        Path(WORK + 'tq2_near-top3-1.jsonl').write_text(body)
    elif tag == 't91-0':
        Path(WORK + 'tq2_near-t91-0.jsonl').write_text(body)
    elif tag == 't91-1':
        Path(WORK + 'tq2_near-t91-1.jsonl').write_text(body)
    elif tag == 't264-0':
        Path(WORK + 'tq2_near-t264-0.jsonl').write_text(body)
    elif tag == 't264-1':
        Path(WORK + 'tq2_near-t264-1.jsonl').write_text(body)
    elif tag == 't306-0':
        Path(WORK + 'tq2_near-t306-0.jsonl').write_text(body)
    elif tag == 't306-1':
        Path(WORK + 'tq2_near-t306-1.jsonl').write_text(body)
    elif tag == 't0-0':
        Path(WORK + 'tq2_near-t0-0.jsonl').write_text(body)
    elif tag == 't0-1':
        Path(WORK + 'tq2_near-t0-1.jsonl').write_text(body)
    elif tag == 't842-0':
        Path(WORK + 'tq2_near-t842-0.jsonl').write_text(body)
    elif tag == 't454-0':
        Path(WORK + 'tq2_near-t454-0.jsonl').write_text(body)
    elif tag == 'agg8-q1':
        Path(WORK + 'tq2_near-q1.jsonl').write_text(body)
    elif tag == 'agg7-m1':
        Path(WORK + 'tq2_near-m1.jsonl').write_text(body)
    elif tag == 'agg7-m2':
        Path(WORK + 'tq2_near-m2.jsonl').write_text(body)
    elif tag == 'agg7-m3':
        Path(WORK + 'tq2_near-m3.jsonl').write_text(body)
    elif tag == 'top-l1':
        Path(WORK + 'tq2_near-l1.jsonl').write_text(body)
    elif tag == 'top-l2':
        Path(WORK + 'tq2_near-l2.jsonl').write_text(body)
    else:
        Path(WORK + 'tq2_near-test.jsonl').write_text(body)


def main():
    src = sys.argv[1]
    if src == 'top3':
        jobs = jobs_top3()
        shard, shards = int(sys.argv[2]), int(sys.argv[3])
        tag = 'top3-' + sys.argv[2]
    elif src == 'top1':
        jobs = jobs_top1(int(sys.argv[2]))
        shard, shards = int(sys.argv[3]), int(sys.argv[4])
        tag = 't' + sys.argv[2] + '-' + sys.argv[3]
    else:
        jobs = folder_jobs(Path('data/online/smoke') / (sys.argv[2] + ('-old' if sys.argv[2].startswith('top-l') else '-new')), 1119, sys.argv[2], sys.argv[2])
        shard, shards = 0, 1
        tag = sys.argv[2]
    seen = set()
    uniq = []
    for j in jobs:
        if j[2]['game'] not in seen:
            seen.add(j[2]['game'])
            uniq.append(j)
    jobs = [j for n, j in enumerate(uniq) if n % shards == shard]
    if sys.argv[-1].startswith('limit'):
        jobs = jobs[:int(sys.argv[-1][5:])]
        tag = 'test'
    geos, bad, out = {}, [], []
    for n, (path, own, info) in enumerate(jobs):
        try:
            rec = scan(path, own, info, geos)
            if info.get('meta_winner') in ('a', 'b'):
                assert (rec['win'] == 1) == (info['meta_winner'].upper() == own), (rec['win'], info['game'])
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((info['game'], repr(e)[:300]))
        if n % 20 == 19:
            sys.stderr.write('%d %d bad %d\n' % (n + 1, len(jobs), len(bad)))
            sys.stderr.flush()
    emit(tag, '\n'.join(out) + '\n')
    print('done', src, tag, len(out), 'bad', bad, flush=True)


main()
