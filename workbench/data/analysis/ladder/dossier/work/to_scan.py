# Scratch (diag-topopen): one pass over a set of games, rounds 0-300, BOTH sides (u = the studied side, t = the other).
# One JSON line per game, written to to_scan-<tag>.jsonl. Sources:
#   T3 = data/online/top3 (today's top teams), T1 = data/online/top1 (to 5 Oct; teams 306, 91, 264, 842, 454),
#   OQ = agg8-q1-new (B7Q live), OM = agg7-m1/m2/m3-new (main), OB = agg7-b1/b2-new (B7), OT = top-l1-*/top-l2-* (live vs top),
#   OL = the 500 main ladder games of wk_index.json (who O).
# Per round 0..300 (state at the end of the round): alive, total length, longest, pearls eaten (all / natural), splits, deaths.
# At sample rounds: deaths by cause, tiles seen (7 by 7 at each turn start, to r100), mean wrapped distance to the nearest
#   team mate's head, portal steps so far, natural pearls born on the whole board.
# Rounds 0-100: turn table key window|length class|context|queen ->
#   [turns, split turns, move turns, steps, turns of 2+ steps, paid steps, paid turns, free extra used, free extra on offer,
#    pearls eaten, paid turns that ate, pearls eaten on paid turns, portal steps]
#   context: P1 pearl 1 step away, P2 pearl 2 free steps away, P3 pearl in the 7 by 7 but farther, E enemy head in view, N nothing.
# Usage: python3 data/analysis/ladder/dossier/work/to_scan.py <SRC> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
STOP = 300
MECH = 100
FAR = 9999
SAMPLES = (0, 5, 10, 20, 30, 40, 60, 80, 100, 150, 200, 300)
OLD_TEAMS = (306, 91, 264, 842, 454)


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.pairs = len(portals)
        self.walls = sum(1 for kp in self.edges.values() if kp[0] == 1)
        self.adj = []
        self.pdir = set()
        for y in range(h):
            for x in range(w):
                row = set()
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        row.add(((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w)
                        self.pdir.add((y * w + x) * 4 + d)
                    else:
                        row.add(((y + dy) % h) * w + (x + dx) % w)
                self.adj.append(sorted(row))
        self.wins = {}

    def window(self, c):
        s = self.wins.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            s = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4)}))
            self.wins[c] = s
        return s

    def dist2(self, src, a, c):
        # path steps from src to tiles a and c (FAR when not reached within 60 steps)
        want = {a, c}
        got = {}
        d = {src: 0}
        q = deque([src])
        while q and len(got) < len(want):
            z = q.popleft()
            if z in want:
                got[z] = d[z]
            if d[z] >= 60:
                continue
            for t in self.adj[z]:
                if t not in d:
                    d[t] = d[z] + 1
                    q.append(t)
        return got.get(a, FAR), got.get(c, FAR)

    def mdist(self, a, c):
        ay, ax = divmod(a, self.w)
        cy, cx = divmod(c, self.w)
        dx, dy = abs(ax - cx), abs(ay - cy)
        return min(dx, self.w - dx) + min(dy, self.h - dy)


def lbucket(L):
    return '2' if L <= 2 else '3' if L == 3 else '4' if L == 4 else '5' if L <= 8 else '9'


def wbucket(r):
    return 0 if r <= 10 else 1 if r <= 20 else 2 if r <= 40 else 3 if r <= 60 else 4


def scan(row, geos):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    N = w * h
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    cap = 0
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
        elif q and q[0] == 'UNIT_LIMIT':
            cap = int(q[1])
    key = (row['map'], w, h, len(raw))
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    mine = row['side']
    side = lambda i: 'u' if teams[i] == mine else 't'
    other = dict(u='t', t='u')
    queen = {s: min(i for i in bodies if side(i) == s) for s in 'ut'}
    cfg = {s: sorted(len(b) for i, b in bodies.items() if side(i) == s) for s in 'ut'}

    occ = [0] * N
    hg = dict(u=[0] * N, t=[0] * N)
    for i, b in bodies.items():
        hg[side(i)][b[0]] += 1
        for c in b:
            occ[c] += 1
    pv = [0] * N
    present = {}
    info = {i: dict(s=side(i), born=0, len0=len(b), par=-1, eat1=None, died=None, cause=None, q=int(i == queen[side(i)]),
                    eats=0, splits=0, sp1=None, tile=b[0], d5=None, d10=None, pd5=None, l10=None, l20=None) for i, b in bodies.items()}
    seen = dict(u=set(), t=set())
    eaten = dict(u=0, t=0)
    nat = dict(u=0, t=0)
    nsplit = dict(u=0, t=0)
    ndeath = dict(u=0, t=0)
    pstep = dict(u=0, t=0)
    pfirst = dict(u=None, t=None)
    pusers = dict(u=set(), t=set())
    born_nat = 0
    causes = dict(u=Counter(), t=Counter())
    names = ('alive', 'total', 'longest', 'eaten', 'nat', 'splits', 'deaths', 'ql')
    series = {s: {n: [] for n in names} for s in 'ut'}
    samp = {s: {} for s in 'ut'}
    splits = dict(u=[], t=[])
    dlist = dict(u=[], t=[])
    paid = dict(u=[], t=[])
    turns = dict(u=defaultdict(lambda: [0] * 13), t=defaultdict(lambda: [0] * 13))
    rnd, actor, used, dirs, kind, cur = 0, None, 0, [], 2, None
    started = False
    hit_side = None

    def sample():
        for s in 'ut':
            ids = [i for i in bodies if side(i) == s]
            v = series[s]
            v['alive'].append(len(ids))
            v['total'].append(sum(len(bodies[i]) for i in ids))
            v['longest'].append(max((len(bodies[i]) for i in ids), default=0))
            v['eaten'].append(eaten[s])
            v['nat'].append(nat[s])
            v['splits'].append(nsplit[s])
            v['deaths'].append(ndeath[s])
            v['ql'].append(len(bodies[queen[s]]) if queen[s] in bodies else 0)
            if rnd in SAMPLES:
                heads = [bodies[i][0] for i in ids]
                n = len(heads)
                nn = -1
                if n >= 2:
                    tot = 0
                    for a in range(n):
                        tot += min(g.mdist(heads[a], heads[c]) for c in range(n) if c != a)
                    nn = round(tot / n, 2)
                hist = Counter(min(len(bodies[i]), 9) for i in ids)
                samp[s][rnd] = dict(dc=dict(causes[s]), seen=len(seen[s]), nn=nn, pstep=pstep[s], pusers=len(pusers[s]),
                                    born=born_nat, lens={str(k): hist[k] for k in sorted(hist)})
        if rnd <= MECH + 20:
            for i, f in info.items():
                if f['born'] > 0 and i in bodies:
                    age = rnd - f['born']
                    if age == 5:
                        ph = bodies[f['par']][0] if f['par'] in bodies else f['tile']
                        a, c = g.dist2(bodies[i][0], f['tile'], ph)
                        f['d5'] = a
                        f['pd5'] = c if f['par'] in bodies else None
                    elif age == 10:
                        f['d10'] = g.dist2(bodies[i][0], f['tile'], f['tile'])[0]
                        f['l10'] = len(bodies[i])
                    elif age == 20:
                        f['l20'] = len(bodies[i])

    def finish_turn():
        nonlocal cur
        if cur is None:
            return
        t = cur
        cur = None
        v = turns[t['s']][t['key']]
        v[0] += 1
        v[9] += t['ate']
        v[12] += t['port']
        if kind == 1:
            v[1] += 1
        elif kind == 0:
            n = len(dirs)
            free = (t['L'] + 3) // 4
            v[2] += 1
            v[3] += used
            v[4] += int(n >= 2)
            v[5] += max(0, n - free)
            v[6] += int(n > free)
            v[7] += min(n, free) - 1 if n >= 1 else 0
            v[8] += free - 1
            if n > free:
                v[10] += int(t['ate'] > 0)
                v[11] += t['ate']
                if len(paid[t['s']]) < 400:
                    paid[t['s']].append([t['r'], t['L'], n, free, t['ate'], t['ctx'], int(t['dead']), t['q'], t['ateat']])

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            finish_turn()
        if k == 0:
            if started and rnd <= STOP:
                sample()
            started = True
            rnd, actor = p.i32(0), None
            if rnd > STOP:
                break
        elif k == 1:
            actor = p.i32(0)
            dirs, used, kind = [], 0, 2
            s = side(actor)
            b = bodies[actor]
            head, L = b[0], len(b)
            if rnd <= MECH:
                win = g.window(head)
                seen[s].update(win)
                eg = hg[other[s]]
                enemy = False
                for c in win:
                    if eg[c]:
                        enemy = True
                        break
                ctx = 'N'
                if pv[head] > 0:
                    ctx = 'P3'
                    for a in g.adj[head]:
                        if a in present:
                            ctx = 'P1'
                            break
                    if ctx != 'P1':
                        for a in g.adj[head]:
                            if occ[a]:
                                continue
                            for c in g.adj[a]:
                                if c in present:
                                    ctx = 'P2'
                                    break
                            if ctx == 'P2':
                                break
                elif enemy:
                    ctx = 'E'
                cur = dict(s=s, L=L, r=rnd, ctx=ctx + ('e' if enemy and ctx[0] == 'P' else ''), ate=0, port=0, dead=False, q=info[actor]['q'], ateat=-1,
                           key='%d|%s|%s|%d' % (wbucket(rnd), lbucket(L), ctx, info[actor]['q']))
        elif k == 4:
            a = p.pointer(0)
            kind = a.u16(0) if a else 2
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present[c] = actor is None
                if actor is None:
                    born_nat += 1
                for z in g.window(c):
                    pv[z] += 1
            else:
                natural = present.pop(c)
                for z in g.window(c):
                    pv[z] -= 1
                s = side(actor)
                eaten[s] += 1
                nat[s] += int(natural)
                f = info[actor]
                f['eats'] += int(rnd <= 60)
                if f['eat1'] is None:
                    f['eat1'] = rnd
                if cur is not None:
                    cur['ate'] += 1
                    if cur['ateat'] < 0:
                        cur['ateat'] = used + 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            old = b[0]
            if old != hd:
                s = side(i)
                if i == actor:
                    if used < len(dirs) and (old * 4 + dirs[used]) in g.pdir:
                        pstep[s] += 1
                        pusers[s].add(i)
                        if pfirst[s] is None:
                            pfirst[s] = rnd
                        if cur is not None:
                            cur['port'] += 1
                    used += 1
                b.appendleft(hd)
                occ[hd] += 1
                hg[s][old] -= 1
                hg[s][hd] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s0 = side(parent)
            before = len(bodies[parent])
            alive0 = sum(1 for i in bodies if side(i) == s0)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            hg[s0][bodies[child][0]] += 1
            info[child] = dict(s=s0, born=rnd, len0=len(bodies[child]), par=parent, eat1=None, died=None, cause=None, q=0, eats=0,
                               splits=0, sp1=None, tile=bodies[child][0], d5=None, d10=None, pd5=None, l10=None, l20=None)
            nsplit[s0] += 1
            if info[parent]['sp1'] is None:
                info[parent]['sp1'] = rnd
            if rnd <= MECH:
                info[parent]['splits'] += 1
                if len(splits[s0]) < 250:
                    splits[s0].append([rnd, before, len(bodies[child]), info[parent]['q'], cur['ctx'] if cur else '?', alive0])
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.pop(i)
            s = side(i)
            for c in b:
                occ[c] -= 1
            hg[s][b[0]] -= 1
            if reason == 0:
                cause = 'wall'
            elif reason == 1:
                cause = 'own'
            elif reason == 2:
                cause = 'body?'
                if i == actor and used < len(dirs):
                    x, y = b[0] % w, b[0] // w
                    d = dirs[used]
                    e = edge_id(w, h, x, y, d)
                    kd, pid = g.edges.get(e, (0, -1))
                    dest = None
                    if kd == 0:
                        dest = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
                    elif kd == 2:
                        plain = {((y + STEP[z][1]) % h) * w + (x + STEP[z][0]) % w for z in range(4)}
                        far = [t for t in g.adj[b[0]] if t not in plain]
                        dest = far[0] if len(far) == 1 else None
                    if dest is not None:
                        owners = [z for z, bb in bodies.items() if dest in bb]
                        if len(owners) == 1:
                            cause = 'matebody' if side(owners[0]) == s else 'enemybody'
            elif reason == 3:
                if i != actor:
                    hit_side = s
                    cause = 'hit-by-' + ('mate' if actor is not None and side(actor) == s else 'enemy')
                else:
                    cause = 'headon-' + ('mate' if hit_side == s else 'enemy')
            else:
                cause = ('nosplit' if kind == 1 else 'nopay' if kind == 0 else 'noact') if i == actor else 'noact'
            info[i]['died'] = rnd
            info[i]['cause'] = cause
            ndeath[s] += 1
            causes[s][cause] += 1
            if i == actor and cur is not None:
                cur['dead'] = True
            if rnd <= MECH and len(dlist[s]) < 300:
                dlist[s].append([rnd, len(b), cause, info[i]['born'], info[i]['q']])
    finish_turn()
    if started and rnd <= STOP and len(series['u']['alive']) <= rnd:
        sample()
    out = dict(src=row['src'], game=row['game'], map=row['map'], cells=N, w=w, h=h, pairs=g.pairs, walls=g.walls, cap=cap,
               reached=min(rnd, STOP + 1), winner=row['winner'], sides={})
    for s in 'ut':
        dr = [[f['born'], f['len0'], f['eat1'], f['died'], f['cause'], f['q'], f['eats'], f['splits'], f['sp1'], f['d5'], f['d10'], f['pd5'], f['l10'], f['l20']]
              for i, f in sorted(info.items()) if f['s'] == s and f['born'] <= MECH][:200]
        out['sides'][s] = dict(team=row[s + 'id'], name=row[s + 'name'], elo=row[s + 'elo'], won=row['winner'] == s, cfg=cfg[s],
                               series=series[s], samp=samp[s], splits=splits[s], turns=dict(turns[s]), deaths=dlist[s], paid=paid[s],
                               pfirst=pfirst[s], dragons=dr)
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
            if not rp.exists() or j.get('status') != 'completed':
                continue
            if team not in (j['teamAId'], j['teamBId']):
                continue
            a = j['teamAId'] == team
            win = (j.get('winner') or '').lower()
            rows.append(dict(src=tag, game=j['id'], replay=str(rp), map=j['mapName'], side='A' if a else 'B',
                             winner=('u' if (win == 'a') == a else 't') if win in ('a', 'b') else None,
                             uid=team, tid=j['teamBId'] if a else j['teamAId'],
                             uname=j['teamAName'] if a else j['teamBName'], tname=j['teamBName'] if a else j['teamAName'],
                             uelo=j['teamAElo'] if a else j['teamBElo'], telo=j['teamBElo'] if a else j['teamAElo']))

    if src == 'T3':
        for line in Path('data/online/top3/index.jsonl').read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                add('data/online/top3/%d' % r['battle'], r['team'], 'T3')
    elif src == 'T1':
        for line in Path('data/top1/index.jsonl').read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r['team'] in OLD_TEAMS:
                    add('data/online/top1/%d' % r['battle'], r['team'], 'T1')
    elif src == 'OQ':
        add('data/online/smoke/agg8-q1-new', 1119, 'OQ')
        if Path('data/online/smoke/agg8-q2-new').exists():
            add('data/online/smoke/agg8-q2-new', 1119, 'OQ')
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
    elif src == 'OL':
        for r in json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text()):
            if r['who'] == 'O':
                rows.append(dict(src='OL', game=r['game'], replay=r['replay'], map=r['layout'], side=r['side'],
                                 winner='u' if r['result'] == 'win' else 't', uid=1119, tid=0, uname='meow', tname='?', uelo=0, telo=r['rating']))
    seen, out = set(), []
    for r in rows:
        if r['game'] not in seen:
            seen.add(r['game'])
            out.append(r)
    return sorted(out, key=lambda r: r['game'])


def save(tag, body):
    if tag == 'T3-0':
        Path(WORK + 'to_scan-T3-0.jsonl').write_text(body)
    elif tag == 'T3b-0':
        Path(WORK + 'to_scan-T3b-0.jsonl').write_text(body)
    elif tag == 'T3c-0':
        Path(WORK + 'to_scan-T3c-0.jsonl').write_text(body)
    elif tag == 'T1-0':
        Path(WORK + 'to_scan-T1-0.jsonl').write_text(body)
    elif tag == 'T1-1':
        Path(WORK + 'to_scan-T1-1.jsonl').write_text(body)
    elif tag == 'OQ-0':
        Path(WORK + 'to_scan-OQ-0.jsonl').write_text(body)
    elif tag == 'OM-0':
        Path(WORK + 'to_scan-OM-0.jsonl').write_text(body)
    elif tag == 'OB-0':
        Path(WORK + 'to_scan-OB-0.jsonl').write_text(body)
    elif tag == 'OT-0':
        Path(WORK + 'to_scan-OT-0.jsonl').write_text(body)
    elif tag == 'OL-0':
        Path(WORK + 'to_scan-OL-0.jsonl').write_text(body)
    elif tag == 'OL-1':
        Path(WORK + 'to_scan-OL-1.jsonl').write_text(body)
    else:
        Path(WORK + 'to_scan-test.jsonl').write_text(body)


def main():
    src, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    tag = sys.argv[5] if len(sys.argv) > 5 else src
    skip = set()
    for name in sys.argv[6:]:
        for line in Path(name).read_text().splitlines():
            if line.strip():
                skip.add(json.loads(line).get('game'))
    rows = [r for n, r in enumerate(rows_for(src if src != 'T3' else 'T3')) if n % shards == shard and r['game'] not in skip]
    if limit:
        rows = rows[:limit]
    geos, out, bad = {}, [], 0
    name = (tag + '-' + str(shard)) if not limit else 'test'
    for n, r in enumerate(rows):
        try:
            out.append(json.dumps(scan(r, geos), separators=(',', ':')))
        except Exception as e:
            bad += 1
            out.append(json.dumps(dict(error=repr(e)[:300], game=r['game'], src=r['src'])))
        if n % 25 == 24:
            save(name, '\n'.join(out) + '\n')
            print(n + 1, len(rows), 'bad', bad, flush=True)
    save(name, '\n'.join(out) + '\n')
    print('done', src, shard, len(out), 'bad', bad)


main()
