"""Scratch (diag-topqueen): what becomes of the enemy heads that come within 3 steps of a queen.
Per queen turn with a non-queen enemy head within 3 steps (path, bodies ignored): the ids of those heads.
Per death: round, id, side, reason, the mover of the turn, and for a head-on the other dragon.
Usage: python3 tq2_chase.py top3 <shard> <shards> | top1 <team> <shard> <shards> | online <label>   -> tq2_chase-<tag>.jsonl"""
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

    def man(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    tile = lambda z: replay.point(z)[1] * w + replay.point(z)[0]
    queen = [min(i for i in bodies if teams[i] == 0), min(i for i in bodies if teams[i] == 1)]
    qturns = [[], []]
    nturn = [0, 0]
    turns = [0, 0]
    fate = [None, None]
    deaths = []
    near = [[0, 0, 0, 0], [0, 0, 0, 0]]
    st = dict(rnd=-1, actor=None, used=0, slen=0, open=None, pend=[])

    def flush():
        pend = st['pend']
        hs = [d for d in pend if d[3] == 3]
        other = {}
        if len(hs) == 2:
            other[hs[0][1]] = hs[1][1]
            other[hs[1][1]] = hs[0][1]
        for d in pend:
            # round, id, side, reason, mover, other id, length, distance to own queen head, distance to enemy queen head
            deaths.append([d[0], d[1], d[2], d[3], d[4], other.get(d[1], -1), d[5], d[6], d[7]])
            if d[3] == 3 and d[1] in other:
                # a head-on between a queen's mate and an enemy, near that queen (5 tiles): who moved
                for s in (0, 1):
                    if d[2] == s and d[1] != queen[s] and d[6] <= 5 and teams_all.get(other[d[1]]) == 1 - s:
                        near[s][0 if d[4] == d[1] else 1] += 1
        st['pend'] = []

    teams_all = dict(teams)

    def close_turn():
        o = st['open']
        if o is not None:
            o[5] = st['used']
            st['open'] = None
        flush()

    def open_turn(s, q):
        b = bodies[q]
        head = b[0]
        nturn[s] += 1
        turns[s] += 1
        ball = g.ball(head)
        eq = queen[1 - s]
        ids = [i for i, bb in bodies.items() if teams[i] != s and i != eq and ball.get(bb[0], 9) <= 3]
        if not ids:
            return
        o5 = sum(1 for i, bb in bodies.items() if teams[i] == s and i != q and man(head, bb[0]) <= 5)
        rec = [nturn[s], st['rnd'], ids, len(b), o5, 0, [len(bodies[i]) for i in ids]]
        qturns[s].append(rec)
        st['open'] = rec

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close_turn()
            st['rnd'], st['actor'] = p.i32(0), None
        elif k == 1:
            close_turn()
            a = p.i32(0)
            st['actor'], st['used'] = a, 0
            s = teams[a]
            if a == queen[s]:
                open_turn(s, a)
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
            teams_all[child] = teams[child]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = teams[i]
            actor = st['actor']
            hd = bodies[i][0]
            dq = man(hd, bodies[queen[s]][0]) if queen[s] in bodies else 99
            de = man(hd, bodies[queen[1 - s]][0]) if queen[1 - s] in bodies else 99
            st['pend'].append((st['rnd'], i, s, reason, actor if actor is not None else -1, len(bodies[i]), dq, de))
            if i == queen[s]:
                fate[s] = [st['rnd'], len(bodies[i]), reason, int(i == actor), nturn[s]]
            bodies.pop(i)
    close_turn()
    res = root.pointer(4)
    winner = ('A', 'B')[res.u16(6)] if res.u16(4) == 1 else None
    out = dict(info)
    out.update(w=w, h=h, win=None if winner is None else int(winner == own_letter), qturns=qturns, turns=turns, fate=fate, queen=queen,
               deaths=[d for d in deaths if d[7] <= 8 or d[8] <= 8], near=near)
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
        Path(WORK + 'tq2_chase-top3-0.jsonl').write_text(body)
    elif tag == 'top3-1':
        Path(WORK + 'tq2_chase-top3-1.jsonl').write_text(body)
    elif tag == 't91-0':
        Path(WORK + 'tq2_chase-t91-0.jsonl').write_text(body)
    elif tag == 't91-1':
        Path(WORK + 'tq2_chase-t91-1.jsonl').write_text(body)
    elif tag == 't264-0':
        Path(WORK + 'tq2_chase-t264-0.jsonl').write_text(body)
    elif tag == 't264-1':
        Path(WORK + 'tq2_chase-t264-1.jsonl').write_text(body)
    elif tag == 't306-0':
        Path(WORK + 'tq2_chase-t306-0.jsonl').write_text(body)
    elif tag == 't306-1':
        Path(WORK + 'tq2_chase-t306-1.jsonl').write_text(body)
    elif tag == 't0-0':
        Path(WORK + 'tq2_chase-t0-0.jsonl').write_text(body)
    elif tag == 't0-1':
        Path(WORK + 'tq2_chase-t0-1.jsonl').write_text(body)
    elif tag == 't842-0':
        Path(WORK + 'tq2_chase-t842-0.jsonl').write_text(body)
    elif tag == 't454-0':
        Path(WORK + 'tq2_chase-t454-0.jsonl').write_text(body)
    elif tag == 'agg8-q1':
        Path(WORK + 'tq2_chase-q1.jsonl').write_text(body)
    elif tag == 'agg7-m1':
        Path(WORK + 'tq2_chase-m1.jsonl').write_text(body)
    elif tag == 'agg7-m2':
        Path(WORK + 'tq2_chase-m2.jsonl').write_text(body)
    elif tag == 'agg7-m3':
        Path(WORK + 'tq2_chase-m3.jsonl').write_text(body)
    elif tag == 'top-l1':
        Path(WORK + 'tq2_chase-l1.jsonl').write_text(body)
    elif tag == 'top-l2':
        Path(WORK + 'tq2_chase-l2.jsonl').write_text(body)
    else:
        Path(WORK + 'tq2_chase-test.jsonl').write_text(body)


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
