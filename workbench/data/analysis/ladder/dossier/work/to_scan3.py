# Scratch (diag-topopen), third pass, rounds 0-60, BOTH sides: turns of non-queen dragons of length 4 or less that start
# with no pearl in their 7 by 7. For each such turn: the nearest portal mouth this dragon has had in view whose far tile it has
# not had in view ("unexplored for it"; a child starts with nothing seen), by walking steps without portals (cap 26).
# Tally key window|band -> [turns, turns that end nearer that mouth, turns that step through a portal]
#   band: m0 on the mouth tile, m1 1-6 steps (where our pull acts), m2 7-12, m3 13-26, u1 no such mouth known but an unexplored
#   mouth lies within 12 steps (not seen yet), none otherwise.
# Usage: python3 data/analysis/ladder/dossier/work/to_scan3.py <SRC> [tag]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
STOP = 60


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.pairs = len(portals)
        self.walk = []
        self.far = {}
        self.pdir = set()
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        t = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                        self.far.setdefault(y * w + x, []).append(t)
                        self.pdir.add((y * w + x) * 4 + d)
                    else:
                        row.append(((y + dy) % h) * w + (x + dx) % w)
                self.walk.append(row)
        self.wins = {}

    def window(self, c):
        s = self.wins.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            s = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4)}))
            self.wins[c] = s
        return s

    def dists(self, src, lim):
        d = {src: 0}
        q = deque([src])
        while q:
            z = q.popleft()
            if d[z] >= lim:
                continue
            for t in self.walk[z]:
                if t not in d:
                    d[t] = d[z] + 1
                    q.append(t)
        return d


def scan(row, geos):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    N = w * h
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
    key = (row['map'], w, h, len(raw))
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    out = dict(src=row['src'], game=row['game'], map=row['map'], cells=N, pairs=g.pairs, sides={s: dict(team=row[s + 'id'], tally={}) for s in 'ut'})
    if not g.pairs:
        return out
    mine = row['side']
    side = lambda i: 'u' if teams[i] == mine else 't'
    queen = {s: min(i for i in bodies if side(i) == s) for s in 'ut'}
    seen = {i: set(g.window(b[0])) for i, b in bodies.items()}
    pv = [0] * N
    tally = dict(u=defaultdict(lambda: [0, 0, 0]), t=defaultdict(lambda: [0, 0, 0]))
    rnd, actor, used, dirs, cur = 0, None, 0, [], None

    def close_turn():
        nonlocal cur
        if cur is None:
            return
        c = cur
        cur = None
        v = tally[c['s']][c['key']]
        v[0] += 1
        v[2] += c['port']
        if c['mouth'] is not None and actor in bodies:
            dm = g.dists(c['mouth'], 30)
            now = dm.get(bodies[actor][0], 99)
            if c['port'] or now < c['d']:
                v[1] += 1

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            close_turn()
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > STOP:
                break
        elif k == 1:
            actor = p.i32(0)
            dirs, used = [], 0
            s = side(actor)
            b = bodies[actor]
            head, L = b[0], len(b)
            seen[actor].update(g.window(head))
            if L <= 4 and actor != queen[s] and pv[head] == 0:
                sn = seen[actor]
                dh = g.dists(head, 26)
                best, bd, ud = None, 99, 99
                for m, fars in g.far.items():
                    dd = dh.get(m)
                    if dd is None:
                        continue
                    if m in sn:
                        if any(f not in sn for f in fars) and dd < bd:
                            best, bd = m, dd
                    elif dd < ud:
                        ud = dd
                if best is not None:
                    band = 'm0' if bd == 0 else 'm1' if bd <= 6 else 'm2' if bd <= 12 else 'm3'
                elif ud <= 12:
                    band = 'u1'
                else:
                    band = 'none'
                cur = dict(s=s, key='%d|%s' % (0 if rnd <= 20 else 1 if rnd <= 40 else 2, band), mouth=best, d=bd, port=0)
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            for z in g.window(c):
                pv[z] += 1 if p.u32(0) else -1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                if i == actor:
                    if cur is not None and used < len(dirs) and (b[0] * 4 + dirs[used]) in g.pdir:
                        cur['port'] = 1
                    used += 1
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            seen[child] = set(g.window(bodies[child][0]))
        elif k == 11:
            bodies.pop(p.i32(0))
    close_turn()
    for s in 'ut':
        out['sides'][s]['tally'] = dict(tally[s])
    return out


def rows_for(src):
    rows = []

    def add(folder, team, tag):
        for gp in sorted(Path(folder).glob('game-*.json')):
            try:
                j = json.loads(gp.read_text())
            except Exception:
                continue
            rp = Path(folder) / ('M%d.replay' % j['id'])
            if not rp.exists() or j.get('status') != 'completed' or team not in (j['teamAId'], j['teamBId']):
                continue
            a = j['teamAId'] == team
            rows.append(dict(src=tag, game=j['id'], replay=str(rp), map=j['mapName'], side='A' if a else 'B',
                             uid=team, tid=j['teamBId'] if a else j['teamAId']))

    if src == 'T3':
        for line in Path('data/online/top3/index.jsonl').read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                add('data/online/top3/%d' % r['battle'], r['team'], 'T3')
    elif src == 'OQ':
        add('data/online/smoke/agg8-q1-new', 1119, 'OQ')
    elif src == 'OM':
        for f in ('agg7-m1-new', 'agg7-m2-new', 'agg7-m3-new'):
            add('data/online/smoke/' + f, 1119, 'OM')
    elif src == 'OB':
        for f in ('agg7-b1-new', 'agg7-b2-new'):
            add('data/online/smoke/' + f, 1119, 'OB')
    elif src == 'OT':
        for f in sorted(Path('data/online/smoke').glob('top-l*')):
            if f.is_dir():
                add(str(f), 1119, 'OT:' + f.name)
    seen, out = set(), []
    for r in rows:
        if r['game'] not in seen:
            seen.add(r['game'])
            out.append(r)
    return sorted(out, key=lambda r: r['game'])


def save(tag, body):
    if tag == 'T3':
        Path(WORK + 'to_scan3-T3.jsonl').write_text(body)
    elif tag == 'OQ':
        Path(WORK + 'to_scan3-OQ.jsonl').write_text(body)
    elif tag == 'OM':
        Path(WORK + 'to_scan3-OM.jsonl').write_text(body)
    elif tag == 'OB':
        Path(WORK + 'to_scan3-OB.jsonl').write_text(body)
    elif tag == 'OT':
        Path(WORK + 'to_scan3-OT.jsonl').write_text(body)
    else:
        Path(WORK + 'to_scan3-test.jsonl').write_text(body)


def main():
    src = sys.argv[1]
    tag = sys.argv[2] if len(sys.argv) > 2 else src
    rows = rows_for(src)
    geos, out, bad = {}, [], 0
    for n, r in enumerate(rows):
        try:
            out.append(json.dumps(scan(r, geos), separators=(',', ':')))
        except Exception as e:
            bad += 1
            out.append(json.dumps(dict(error=repr(e)[:300], game=r['game'], src=r['src'])))
        if n % 25 == 24:
            print(n + 1, len(rows), 'bad', bad, flush=True)
    save(tag, '\n'.join(out) + '\n')
    print('done', src, len(out), 'bad', bad)


main()
