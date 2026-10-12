"""Scratch (diag-topaah): one JSON line per game for a studied team (side 0 = the studied team, side 1 = its opponent).
Same rate definitions as count_dossier.py (the scoreboard counters), plus structure: opening actions, split sizes,
queen distance / company, voluntary deaths, who eats the dead, length marks, body kills.
Usage: python3 ta_scan.py <tag> [limit]    tags: a a0 l c1 g g0 q m t c0-0..c0-3 test
Reads ta_index.jsonl (ta_index.py). Writes ta_scan-<tag>.jsonl."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

D = '개인 프로젝트'
WORK = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSES = ('head-on mover', 'head-on hit', 'wall', 'own body', 'another body', 'no action', 'unpaid sprint',
          'illegal split', 'timeout')
MARKS = (10, 25, 50, 75, 100, 150, 200, 300, 400)
ALIVE_T = (4, 8, 16, 32, 48, 60)
LONG_T = (5, 6, 8, 10, 15, 20)
INF = 9999


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.moves = []
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
                self.moves.append(row)
        self.adj = [list({dest for kind, dest in row if kind != 1}) for row in self.moves]
        self.nportal = len(portals)
        self.walls = sum(1 for row in self.moves for kind, dest in row if kind == 1)
        self.wins = {}
        self.dc = {}

    def bfs(self, sources):
        dist = [INF] * len(self.adj)
        queue = deque(sources)
        for s in sources:
            dist[s] = 0
        while queue:
            c = queue.popleft()
            nd = dist[c] + 1
            for t in self.adj[c]:
                if dist[t] == INF:
                    dist[t] = nd
                    queue.append(t)
        return dist

    def window(self, src):
        v = self.wins.get(src)
        if v is None:
            y, x = divmod(src, self.w)
            v = self.wins[src] = {((y + dy) % self.h) * self.w + (x + dx) % self.w
                                  for dy in range(-3, 4) for dx in range(-3, 4)}
        return v

    def visible(self, a, b):
        ay, ax = divmod(a, self.w)
        by, bx = divmod(b, self.w)
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, self.w - dx) <= 3 and min(dy, self.h - dy) <= 3

    def tman(self, a, b):
        ay, ax = divmod(a, self.w)
        by, bx = divmod(b, self.w)
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, self.w - dx) + min(dy, self.h - dy)


def lenclass(n):
    return 'len2' if n <= 2 else 'len3' if n == 3 else 'len4' if n <= 5 else 'len6' if n <= 9 else 'len10'


def scan(path, meta, focus):
    root = replay.load(path).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    g = Geo(w, h, raw)
    fteam = 0 if meta['teamAId'] == focus else 1
    assert meta['teamBId' if fteam else 'teamAId'] == focus
    side = lambda i: 0 if teams[i] == fteam else 1
    start_ids = sorted(bodies)
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    starts = [[[i, len(bodies[i]), bodies[i][0] % w, bodies[i][0] // w] for i in start_ids if side(i) == s] for s in (0, 1)]
    qstart = [bodies[queens[s]][0] for s in (0, 1)]
    qd = [g.bfs([qstart[s]]) for s in (0, 1)]
    radius = min(8, (w + h) / 8)
    reach = [g.bfs([bodies[i][0] for i in start_ids if side(i) == s]) for s in (0, 1)]
    enemy_half = [{c for c in range(w * h) if reach[s][c] > reach[1 - s][c]} for s in (0, 1)]
    occ = {}
    for i, b in bodies.items():
        for x in b:
            occ[x] = i
    cnt = [[Counter() for _ in range(3)] for _ in (0, 1)]
    snaps = {}
    deaths, splits, rams, pearls = [], [], [], []
    present, dropinfo = {}, {}
    births_by_tile = Counter()
    trail = {i: deque([b[0]], maxlen=12) for i, b in bodies.items()}
    lastdir = {}
    contact = [None, None]
    first_split = [None, None]
    first_alive = [{}, {}]
    first_long = [{}, {}]
    for i, b in bodies.items():
        for th in LONG_T:
            if len(b) >= th:
                first_long[side(i)].setdefault(str(th), [0, int(i == queens[side(i)])])
    opening = {i: [] for i in start_ids}
    qtiles = [set(), set()]
    logs = [Counter(), Counter()]
    samples = []
    turn_deaths = []
    rnd, actor, used, W = 0, None, 0, 0
    dirs, action_cause, cur = [], None, None
    started = False
    tile = lambda pt: pt[1] * w + pt[0]

    def snap_side(s):
        ls = sorted((len(b) for i, b in bodies.items() if side(i) == s), reverse=True)
        q = bodies.get(queens[s])
        heads = [b[0] for i, b in bodies.items() if side(i) == s]
        d = dict(alive=len(ls), total=sum(ls), longest=ls[0] if ls else 0, second=ls[1] if len(ls) > 1 else 0,
                 n4=sum(x >= 4 for x in ls), n6=sum(x >= 6 for x in ls), ql=len(q) if q else 0,
                 half=sum(x in enemy_half[s] for x in heads))
        if q:
            d.update(qd=min(qd[s][q[0]], 999), qm=g.tman(q[0], qstart[s]),
                     qg=sum(1 for i, b in bodies.items() if side(i) == s and i != queens[s] and g.tman(b[0], q[0]) <= 5),
                     qe=sum(1 for i, b in bodies.items() if side(i) != s and g.tman(b[0], q[0]) <= 5),
                     qlong=int(len(q) == ls[0]))
        return d

    def snapshot(n):
        if n in MARKS:
            snaps[str(n)] = [snap_side(0), snap_side(1)]

    def finish_turn():
        nonlocal cur
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if len(hs) == 2:
            mover = [d for d in hs if d['id'] == actor][0]
            hit = [d for d in hs if d['id'] != actor][0]
            cross = mover['side'] != hit['side']
            rams.append([rnd, mover['side'], mover['length'], hit['length'], int(hit['queen']), int(mover['queen']), int(cross)])
            if cross:
                cnt[mover['side']][W]['cross_head_on'] += 1
                cnt[hit['side']][W]['cross_head_on'] += 1
            else:
                cnt[mover['side']][W]['same_head_on'] += 1
        turn_deaths.clear()
        if cur is None:
            return
        t = cur
        c = cnt[t['side']][t['W']]
        if t['adjacent']:
            c['adj_missed'] += int(not t['adj_eaten'])
        if t['first'] is not None:
            c['moved'] += 1
            c['retread'] += int(t['first'] in t['trail'])
            if t['no_pearl']:
                c['nv_moved'] += 1
                c['dither'] += int(t['first'] in t['trail'])
                if t['previous'] is not None:
                    c['keeps_eligible'] += 1
                    c['keeps'] += int(t['first_dir'] == t['previous'])
        lastdir[t['id']] = t['first_dir']
        cur = None

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k == 2 or k == 8:
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            finish_turn()
        if k == 0:
            if started:
                snapshot(rnd)
            started = True
            rnd, actor = p.i32(0), None
            W = 0 if rnd <= 100 else 1 if rnd <= 300 else 2
        elif k == 1:
            actor = p.i32(0)
            dirs, used, action_cause = [], 0, None
            s = side(actor)
            b = bodies[actor]
            head, L = b[0], len(b)
            c = cnt[s][W]
            c['turns'] += 1
            c[lenclass(L)] += 1
            if contact[s] is None and any(side(i) != s and g.visible(head, bb[0]) for i, bb in bodies.items()):
                contact[s] = rnd
            win = g.window(head)
            no_pearl = not any(t in win for t in present) if len(present) < 49 else not any(t in present for t in win)
            adjacent = {dest for kind, dest in g.moves[head] if kind != 1 and dest in present}
            hot = births_by_tile[head] >= 2 or any(births_by_tile[t] >= 2 for t in g.adj[head])
            nfree = sum(1 for kind, dest in g.moves[head] if kind != 1 and dest not in occ)
            c['no_view'] += int(no_pearl)
            c['adj_turns'] += int(bool(adjacent))
            c['hot'] += int(hot)
            c['boxed'] += int(nfree == 0)
            cur = dict(id=actor, side=s, W=W, no_pearl=no_pearl, adjacent=adjacent, adj_eaten=False,
                       previous=lastdir.get(actor), trail=set(trail[actor]), first=None, first_dir=None)
            if actor == queens[s]:
                own = sum(1 for i, bb in bodies.items() if i != actor and side(i) == s and g.tman(bb[0], head) <= 5)
                en = sum(1 for i, bb in bodies.items() if side(i) != s and g.tman(bb[0], head) <= 5)
                c['q_turns'] += 1
                c['q_dist'] += min(qd[s][head], 200)
                c['q_inR'] += int(g.tman(head, qstart[s]) <= radius)
                c['q_far'] += int(g.tman(head, qstart[s]) > radius + 4)
                c['q_guard'] += own
                c['q_guard2'] += int(own >= 2)
                c['q_enemy'] += int(en > 0)
                c['q_len'] += L
                c['q_hot'] += int(hot)
                c['q_noview'] += int(no_pearl)
                if rnd <= 150:
                    qtiles[s].add(head)
        elif k == 4:
            a = p.pointer(0)
            akind = a.u16(0) if a else 2
            dirs = list(a.pointer(0)) if a and akind == 0 and a.pointer(0) is not None else []
            fuel = p.pointer(1)
            action_cause = ('timeout' if p.bit(32) or (fuel is not None and fuel.bit(64)) else
                            ('unpaid sprint', 'illegal split', 'no action')[akind] if akind < 3 else 'no action')
            used = 0
            if actor is not None and actor in bodies:
                s = side(actor)
                c = cnt[s][W]
                if len(dirs) > 1:
                    L = len(bodies[actor])
                    c['sprint_turns'] += 1
                    c['sprint_steps'] += len(dirs)
                    c['sprint_paid'] += max(0, len(dirs) - (L + 3) // 4)
                    if actor == queens[s]:
                        c['q_sprint'] += 1
                if rnd <= 11 and actor in opening:
                    opening[actor].append(''.join('NESW'[d] for d in dirs) if akind == 0 else 'S' if akind == 1 else 'X')
        elif k == 3:
            t = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                info = dropinfo.pop(t, None)
                pr = [t, rnd, 'n' if info is None else 'd', -1 if info is None else info[0], -1, -1,
                      0 if info is None else info[1]]
                pearls.append(pr)
                present[t] = pr
                births_by_tile[t] += 1
            else:
                pr = present.pop(t)
                s = side(actor)
                pr[4], pr[5] = s, rnd
                c = cnt[s][W]
                key = 'eat_n' if pr[2] == 'n' else 'eat_own' if pr[3] == s else 'eat_enemy'
                c['eaten'] += 1
                c[key] += 1
                if actor == queens[s]:
                    c['q_eat'] += 1
                    c['q_' + key] += 1
                if key == 'eat_own':
                    L = len(bodies[actor])
                    c['own_to_longer'] += int(L > pr[6])
                    c['own_to_longest'] += int(L >= max(len(bb) for i, bb in bodies.items() if side(i) == s))
                    c['own_wait'] += rnd - pr[1]
                if cur is not None and t in cur['adjacent']:
                    cur['adj_eaten'] = True
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            old = b[0]
            moved = old != hd
            if moved:
                b.appendleft(hd)
                occ[hd] = i
            while len(b) > 1 and b[-1] != tl:
                x = b.pop()
                if occ.get(x) == i:
                    del occ[x]
            if i == actor and moved:
                direction = dirs[used]
                kind, dest = g.moves[old][direction]
                used += 1
                s = side(i)
                if kind == 2:
                    cnt[s][W]['portal'] += 1
                    if i == queens[s]:
                        cnt[s][W]['q_portal'] += 1
                if cur is not None and cur['first'] is None:
                    cur['first'], cur['first_dir'] = hd, direction
                trail[i].append(hd)
                n = len(b)
                if n >= 5:
                    fl = first_long[s]
                    for th in LONG_T:
                        if n >= th and str(th) not in fl:
                            fl[str(th)] = [rnd, int(i == queens[s])]
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = side(parent)
            lp = len(bodies[parent])
            for x in bodies[parent]:
                occ.pop(x, None)
            bodies[parent] = deque(tile(replay.point(z)) for z in p.pointer(0))
            bodies[child] = deque(tile(replay.point(z)) for z in p.pointer(1))
            teams[child] = p.u16(8)
            for i in (parent, child):
                for x in bodies[i]:
                    occ[x] = i
            trail[child] = deque([bodies[child][0]], maxlen=12)
            c = cnt[s][W]
            c['splits'] += 1
            if parent == queens[s]:
                c['q_split'] += 1
            splits.append([rnd, s, lp, len(bodies[child]), int(parent == queens[s])])
            if first_split[s] is None:
                first_split[s] = rnd
            alive = sum(1 for i in bodies if side(i) == s)
            for th in ALIVE_T:
                if alive >= th and str(th) not in first_alive[s]:
                    first_alive[s][str(th)] = rnd
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            b = bodies[i]
            L, hd = len(b), b[0]
            dest = g.moves[hd][dirs[used]][1] if i == actor and used < len(dirs) else None
            cause = ('wall', 'own body', 'another body', 'head-on mover' if i == actor else 'head-on hit',
                     action_cause or 'no action')[reason]
            free = any(kind != 1 and d2 not in occ for kind, d2 in g.moves[hd])
            hit_side = side(occ[dest]) if reason == 2 and dest is not None and dest in occ else -1
            mate = any(j != i and side(j) == s and len(bb) > L and g.tman(bb[0], hd) <= 4 for j, bb in bodies.items())
            alive = sum(1 for j in bodies if side(j) == s)
            foe = any(side(j) != s and g.tman(bb[0], hd) <= 3 for j, bb in bodies.items())
            deaths.append([rnd, s, CAUSES.index(cause), L, int(free), int(i == queens[s]), alive, int(mate), hit_side,
                           used, int(foe)])
            turn_deaths.append(dict(id=i, side=s, reason=reason, length=L, queen=i == queens[s]))
            c = cnt[s][W]
            c['deaths'] += 1
            c['d_' + cause] += 1
            c['len_lost'] += L
            for seg, x in enumerate(b):
                if occ.get(x) == i:
                    del occ[x]
                if seg % 2 == 0:
                    dropinfo[x] = (s, L)
            bodies.pop(i)
        elif k in (5, 6, 7, 12):
            s = side(actor) if actor is not None and actor in teams else 0
            logs[s][('elog', 'log', 'ind', 'x', 'x', 'x', 'x', 'sonar')[k - 5]] += 1
            if k in (6, 7) and s == 0 and len(samples) < 8:
                try:
                    tx = p.text(0)
                except Exception:
                    tx = None
                if tx and tx[:60] not in samples:
                    samples.append(tx[:60])
    finish_turn()
    snapshot(rnd)
    final = [snap_side(0), snap_side(1)]
    res = root.pointer(4)
    order = (0, 1) if fteam == 0 else (1, 0)
    ok = True
    for z in (0, 1):
        st = res.pointer(z)
        f = final[order[z]]
        ok = ok and (f['alive'], f['longest'], f['total']) == (st.i32(0), st.i32(4), st.i32(8))
    winner = res.u16(6) if res.u16(4) == 1 else None
    end_reason = res.u16(2)
    coh = [[Counter() for _ in range(3)] for _ in (0, 1)]
    for pr in pearls:
        wb = 0 if pr[1] <= 100 else 1 if pr[1] <= 300 else 2
        for s in (0, 1):
            c = coh[s][wb]
            kind = 'n' if pr[2] == 'n' else 'own' if pr[3] == s else 'foe'
            c['b_' + kind] += 1
            if pr[4] == s:
                c['e_' + kind] += 1
                c['wait'] += pr[5] - pr[1]
                c['wait_n'] += 1
    other = 'B' if fteam == 0 else 'A'
    me = 'A' if fteam == 0 else 'B'
    return dict(gid=meta['id'], map=meta['mapName'], w=w, h=h, focus=focus, fside=me, opp=meta.get('team' + other + 'Id'),
                opp_name=meta.get('team' + other + 'Name'), opp_elo=meta.get('team' + other + 'Elo'),
                elo=meta.get('team' + me + 'Elo'), at=meta.get('completedAt'),
                win=None if winner is None else int(winner == fteam), end_reason=end_reason, last_round=rnd, ok=ok,
                final=final, snaps=snaps, cnt=[[dict(c) for c in cs] for cs in cnt],
                coh=[[dict(c) for c in cs] for cs in coh], deaths=deaths, splits=splits, rams=rams,
                contact=contact, first_split=first_split, first_alive=first_alive, first_long=first_long,
                opening={str(i): v for i, v in opening.items()}, starts=starts, queens=queens, radius=radius,
                qtiles=[len(x) for x in qtiles], logs=[dict(x) for x in logs], samples=samples,
                portals=g.nportal, walls=g.walls, path=str(path))


def pick(tag):
    rows = [json.loads(x) for x in Path(WORK + 'ta_index.jsonl').read_text().splitlines()]
    def sel(src, team):
        return [(r, team) for r in rows if src in r['src'] and team in (r['a'], r['b'])]
    if tag == 'a':
        return sel('online/top3', 454)
    if tag == 'a0':
        return sel('online/top1', 454)
    if tag == 'l':
        return sel('online/top3', 157)
    if tag == 'c1':
        return sel('online/top3', 306)
    if tag == 'g':
        return sel('online/top3', 70)
    if tag == 'g0':
        return sel('online/top1', 70)
    if tag == 'q':
        return sel('agg8-q1-new', 1119)
    if tag == 'm':
        return sel('agg7-m', 1119)
    if tag == 't':
        return sel('smoke/top-l', 1119)
    if tag.startswith('c0-'):
        n = int(tag[3:])
        return [x for z, x in enumerate(sel('online/top1', 306)) if z % 4 == n]
    if tag == 'test':
        return sel('online/top3', 454)[:2]
    return []


def save(tag, body):
    if tag == 'a':
        Path(WORK + 'ta_scan-a.jsonl').write_text(body)
    elif tag == 'a0':
        Path(WORK + 'ta_scan-a0.jsonl').write_text(body)
    elif tag == 'l':
        Path(WORK + 'ta_scan-l.jsonl').write_text(body)
    elif tag == 'c1':
        Path(WORK + 'ta_scan-c1.jsonl').write_text(body)
    elif tag == 'g':
        Path(WORK + 'ta_scan-g.jsonl').write_text(body)
    elif tag == 'g0':
        Path(WORK + 'ta_scan-g0.jsonl').write_text(body)
    elif tag == 'q':
        Path(WORK + 'ta_scan-q.jsonl').write_text(body)
    elif tag == 'm':
        Path(WORK + 'ta_scan-m.jsonl').write_text(body)
    elif tag == 't':
        Path(WORK + 'ta_scan-t.jsonl').write_text(body)
    elif tag == 'c0-0':
        Path(WORK + 'ta_scan-c0-0.jsonl').write_text(body)
    elif tag == 'c0-1':
        Path(WORK + 'ta_scan-c0-1.jsonl').write_text(body)
    elif tag == 'c0-2':
        Path(WORK + 'ta_scan-c0-2.jsonl').write_text(body)
    elif tag == 'c0-3':
        Path(WORK + 'ta_scan-c0-3.jsonl').write_text(body)
    else:
        Path(WORK + 'ta_scan-test.jsonl').write_text(body)


def main():
    tag = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    todo = pick(tag)
    if limit:
        todo = todo[:limit]
    out = []
    bad = 0
    for n, (r, team) in enumerate(todo):
        meta = dict(id=r['gid'], mapName=r['map'], teamAId=r['a'], teamBId=r['b'], teamAName=r['an'], teamBName=r['bn'],
                    teamAElo=r['ae'], teamBElo=r['be'], completedAt=r['at'])
        try:
            row = scan(Path(r['path']), meta, team)
        except Exception as e:
            bad += 1
            print('FAILED', r['gid'], type(e).__name__, e, flush=True)
            continue
        out.append(json.dumps(row, ensure_ascii=False, separators=(',', ':')))
        if n % 20 == 0:
            print(tag, n, len(todo), flush=True)
    save(tag, '\n'.join(out) + '\n')
    print(tag, 'done', len(out), 'games', bad, 'failed')


main()
