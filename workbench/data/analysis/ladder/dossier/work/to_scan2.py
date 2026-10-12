# Scratch (diag-topopen), second pass, rounds 0-100, BOTH sides (u = the studied side, t = the other):
#   p1: one row per turn of a dragon of length 4 or less that starts with a pearl one step from its head
#       [round, id, length, queen, action (E ate it / M moved elsewhere / S split / D died), class, room, reaches tail,
#        pearls beside, enemy heads beside the pearl, mate heads beside the pearl, via portal, later (who ate that pearl:
#        s same dragon, m a mate, e the enemy, n nobody yet), rounds until eaten, natural, x, y, px, py]
#       class of the pearl tile: enemy (an enemy head can step onto it), mate (a mate's head can), portal (reached through a portal),
#       trapped (free tiles behind it < length + 3), tight (< 3 x length + 8), notail (no free tile beside the dragon's own tail
#       is reached), open. With several pearls beside the head the one with the most room is described.
#   births: natural pearls born r1-100 [round, steps to the nearest u head, to the nearest t head (13 = farther), eater, eat round]
#   kids: children born r1-100 [round, free tiles beside the head, room (cap 30), pearl in view, steps to nearest pearl (9 = none in 6), first pearl round, death round, cause]
#   gate: turns beside a portal edge with no pearl beside the head -> per window and kind (q queen, s short non-queen, l longer) [turns, portal steps]
#   dead: deaths r0-100 [round, length, cause, free tiles beside the head at turn start (-1 not its turn), age]
# Usage: python3 data/analysis/ladder/dossier/work/to_scan2.py <SRC> <shard> <shards> [limit] [tag]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
STOP = 100
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
        self.padj = []
        self.pdir = set()
        for y in range(h):
            for x in range(w):
                row = set()
                prow = set()
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
                        row.add(t)
                        prow.add(t)
                        self.pdir.add((y * w + x) * 4 + d)
                    else:
                        row.add(((y + dy) % h) * w + (x + dx) % w)
                self.adj.append(sorted(row))
                self.padj.append(prow)
        self.wins = {}

    def window(self, c):
        s = self.wins.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            s = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4)}))
            self.wins[c] = s
        return s


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
    adj = g.adj
    mine = row['side']
    side = lambda i: 'u' if teams[i] == mine else 't'
    other = dict(u='t', t='u')
    queen = {s: min(i for i in bodies if side(i) == s) for s in 'ut'}
    occ = [0] * N
    hg = dict(u=[0] * N, t=[0] * N)
    for i, b in bodies.items():
        hg[side(i)][b[0]] += 1
        for c in b:
            occ[c] += 1
    pv = [0] * N
    present = {}
    born = {i: 0 for i in bodies}
    p1 = dict(u=[], t=[])
    watch = {}
    births = []
    bwatch = {}
    kids = dict(u=[], t=[])
    kid = {}
    gate = dict(u=defaultdict(lambda: [0, 0]), t=defaultdict(lambda: [0, 0]))
    dead = dict(u=[], t=[])
    rnd, actor, used, dirs, kind, cur = 0, None, 0, [], 2, None
    nfree0 = -1
    gkey = None

    def fill(src, cap, tail):
        # free tiles reachable from src (src not counted), stop at cap; whether a tile beside the tail is reached
        seen = {src}
        q = deque([src])
        n = 0
        near = set(adj[tail]) if tail is not None else set()
        hit = src in near
        while q and n < cap:
            z = q.popleft()
            for t in adj[z]:
                if t not in seen and not occ[t]:
                    seen.add(t)
                    n += 1
                    if t in near:
                        hit = True
                    q.append(t)
        return n, hit

    def nearest_heads(src, lim):
        d = {src: 0}
        q = deque([src])
        got = dict(u=lim + 1, t=lim + 1)
        left = 2
        if hg['u'][src]:
            got['u'] = 0
            left -= 1
        if hg['t'][src]:
            got['t'] = 0
            left -= 1
        while q and left:
            z = q.popleft()
            if d[z] >= lim:
                continue
            for t in adj[z]:
                if t not in d:
                    d[t] = d[z] + 1
                    q.append(t)
                    if hg['u'][t] and got['u'] > lim:
                        got['u'] = d[t]
                        left -= 1
                    if hg['t'][t] and got['t'] > lim:
                        got['t'] = d[t]
                        left -= 1
        return got['u'], got['t']

    def head_dist(src, grid, skip, lim):
        d = {src: 0}
        q = deque([src])
        while q:
            z = q.popleft()
            if d[z] >= lim:
                continue
            for t in adj[z]:
                if t not in d:
                    if grid[t] and t != skip:
                        return d[z] + 1
                    d[t] = d[z] + 1
                    q.append(t)
        return 9

    def pearl_dist(src, lim):
        if src in present:
            return 0
        d = {src: 0}
        q = deque([src])
        while q:
            z = q.popleft()
            if d[z] >= lim:
                continue
            for t in adj[z]:
                if t not in d:
                    if t in present:
                        return d[z] + 1
                    d[t] = d[z] + 1
                    q.append(t)
        return 9

    def close_turn():
        nonlocal cur
        if cur is None:
            return
        c = cur
        cur = None
        if c['row'] is not None:
            r = c['row']
            if c['died']:
                r[4] = 'D'
            elif kind == 1:
                r[4] = 'S'
            elif c['ate_tiles']:
                r[4] = 'E'
            else:
                r[4] = 'M'
            if r[4] != 'E' or c['px'] not in c['ate_tiles']:
                if c['px'] in present:
                    watch.setdefault(c['px'], []).append((r, c['id'], c['s']))
            else:
                r[12] = 's'
                r[13] = 0
            p1[c['s']].append(r)

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
            dirs, used, kind = [], 0, 2
            s = side(actor)
            b = bodies[actor]
            head, L = b[0], len(b)
            isq = int(actor == queen[s])
            nfree0 = sum(1 for t in adj[head] if not occ[t])
            cur = dict(s=s, id=actor, row=None, ate_tiles=[], died=False, px=None)
            beside = [t for t in adj[head] if t in present]
            gkey = None
            if beside and L <= 4:
                eg, mg = hg[other[s]], hg[s]
                best = None
                for x in beside:
                    room, tail = fill(x, 40, b[-1])
                    en = sum(eg[t] for t in adj[x])
                    ma = sum(mg[t] for t in adj[x]) - 1
                    via = int(x in g.padj[head])
                    if en:
                        cl = 'enemy'
                    elif ma > 0:
                        cl = 'mate'
                    elif via:
                        cl = 'portal'
                    elif room < L + 3:
                        cl = 'trapped'
                    elif room < 3 * L + 8:
                        cl = 'tight'
                    elif not tail:
                        cl = 'notail'
                    else:
                        cl = 'open'
                    cand = (room, cl, tail, en, ma, via, x)
                    if best is None or cand[0] > best[0]:
                        best = cand
                room, cl, tail, en, ma, via, x = best
                cur['px'] = x
                cur['row'] = [rnd, actor, L, isq, '?', cl, room, int(tail), len(beside), en, ma, via, 'n', -1, int(present[x]), head % w, head // w, x % w, x // w,
                              len(adj[x]), sum(1 for z in adj[x] if not occ[z]), head_dist(x, mg, head, 6), head_dist(x, eg, -1, 6), rnd - born.get(actor, 0)]
            elif not beside and g.pairs:
                if any((head * 4 + d) in g.pdir for d in range(4)):
                    gkey = '%d|%s' % (0 if rnd <= 20 else 1 if rnd <= 40 else 2 if rnd <= 60 else 3, 'q' if isq else 's' if L <= 4 else 'l')
                    gate[s][gkey][0] += 1
        elif k == 4:
            a = p.pointer(0)
            kind = a.u16(0) if a else 2
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present[c] = actor is None
                if actor is None and rnd >= 1:
                    du, dt = nearest_heads(c, 12)
                    rec = [rnd, du, dt, 'n', -1]
                    births.append(rec)
                    bwatch[c] = rec
                for z in g.window(c):
                    pv[z] += 1
            else:
                present.pop(c)
                for z in g.window(c):
                    pv[z] -= 1
                s = side(actor)
                if cur is not None:
                    cur['ate_tiles'].append(c)
                if c in bwatch:
                    rec = bwatch.pop(c)
                    rec[3] = s
                    rec[4] = rnd
                for r, who, ws in watch.pop(c, []):
                    r[12] = 's' if who == actor else 'm' if ws == s else 'e'
                    r[13] = rnd - r[0]
                if actor in kid and kid[actor][5] is None:
                    kid[actor][5] = rnd
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            old = b[0]
            if old != hd:
                s = side(i)
                if i == actor:
                    if used == 0 and gkey is not None and used < len(dirs) and (old * 4 + dirs[used]) in g.pdir:
                        gate[s][gkey][1] += 1
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
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            ch = bodies[child][0]
            hg[s0][ch] += 1
            born[child] = rnd
            room, tail = fill(ch, 30, None)
            rec = [rnd, sum(1 for t in adj[ch] if not occ[t]), room, int(pv[ch] > 0), pearl_dist(ch, 6), None, None, None, len(bodies[child])]
            kid[child] = rec
            kids[s0].append(rec)
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
                cause = 'body'
            elif reason == 3:
                cause = 'headon' if i == actor else 'hit'
            else:
                cause = ('nosplit' if kind == 1 else 'nopay' if kind == 0 else 'noact') if i == actor else 'noact'
            if i == actor and cur is not None:
                cur['died'] = True
            dead[s].append([rnd, len(b), cause, nfree0 if i == actor else -1, rnd - born.get(i, 0), int(born.get(i, 0) > 0)])
            if i in kid:
                kid[i][6] = rnd
                kid[i][7] = cause + ('0' if (i == actor and nfree0 == 0) else '')
    close_turn()
    out = dict(src=row['src'], game=row['game'], map=row['map'], cells=N, w=w, h=h, pairs=g.pairs, walls=g.walls,
               births=births, sides={})
    for s in 'ut':
        out['sides'][s] = dict(team=row[s + 'id'], won=row['winner'] == s, p1=p1[s], kids=kids[s], gate=dict(gate[s]), dead=dead[s])
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
                             uid=team, tid=j['teamBId'] if a else j['teamAId']))

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
                                 winner='u' if r['result'] == 'win' else 't', uid=1119, tid=0))
    seen, out = set(), []
    for r in rows:
        if r['game'] not in seen:
            seen.add(r['game'])
            out.append(r)
    return sorted(out, key=lambda r: r['game'])


def save(tag, body):
    if tag == 'T3-0':
        Path(WORK + 'to_scan2-T3-0.jsonl').write_text(body)
    elif tag == 'T3b-0':
        Path(WORK + 'to_scan2-T3b-0.jsonl').write_text(body)
    elif tag == 'T3c-0':
        Path(WORK + 'to_scan2-T3c-0.jsonl').write_text(body)
    elif tag == 'T1-0':
        Path(WORK + 'to_scan2-T1-0.jsonl').write_text(body)
    elif tag == 'T1-1':
        Path(WORK + 'to_scan2-T1-1.jsonl').write_text(body)
    elif tag == 'OQ-0':
        Path(WORK + 'to_scan2-OQ-0.jsonl').write_text(body)
    elif tag == 'OM-0':
        Path(WORK + 'to_scan2-OM-0.jsonl').write_text(body)
    elif tag == 'OB-0':
        Path(WORK + 'to_scan2-OB-0.jsonl').write_text(body)
    elif tag == 'OT-0':
        Path(WORK + 'to_scan2-OT-0.jsonl').write_text(body)
    elif tag == 'OL-0':
        Path(WORK + 'to_scan2-OL-0.jsonl').write_text(body)
    elif tag == 'OL-1':
        Path(WORK + 'to_scan2-OL-1.jsonl').write_text(body)
    else:
        Path(WORK + 'to_scan2-test.jsonl').write_text(body)


def main():
    src, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    tag = sys.argv[5] if len(sys.argv) > 5 else src
    skip = set()
    for name in sys.argv[6:]:
        for line in Path(name).read_text().splitlines():
            if line.strip():
                skip.add(json.loads(line).get('game'))
    rows = [r for n, r in enumerate(rows_for(src)) if n % shards == shard and r['game'] not in skip]
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
