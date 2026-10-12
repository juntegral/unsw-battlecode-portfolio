"""Scratch (diag-whq): who eats whose dead, and how the longest dragon and the queen of each side grow.
Per game: every pearl eaten is booked to the eater's role at that moment (queen, the side's longest of 5 or more, other) and
origin (natural, own dead by cause of death, their dead); every death that is not a collision and had a free tile
(a deliberate stop) with its distance to the own queen and own longest; every death of a queen or of a longest dragon of 8+.
Usage: python3 data/analysis/ladder/dossier/work/wq_feed.py <O|R> <shard> <shards> [limit]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2')


def jobs(src):
    out = []
    if src == 'O':
        for label in LABELS:
            folder = Path('data/online/smoke') / (label + '-new')
            if not folder.is_dir():
                continue
            for mp in sorted(folder.glob('game-*.json')):
                j = json.loads(mp.read_text())
                rp = folder / ('M%d.replay' % j['id'])
                if rp.exists():
                    out.append((label, rp, j, 1119))
    else:
        path = Path('data/analysis/ladder/dossier') / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            rp = Path(r['replay'])
            j = json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text())
            out.append((src, rp, j, team))
        out.sort(key=lambda t: t[2]['id'])
    return out


def wnd(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3 if r <= 400 else 4


def scan(label, path, j, team):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    own = 0 if j['teamAId'] == team else 1

    def side(i):
        return 0 if teams[i] == own else 1

    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def dest(h, d):
        x, y = h
        e = edge_id(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            prow, px = divmod(partner, W + 1)
            py = prow // 2
            return ((px - (d == 3)) % W, (py - (d == 0)) % H)
        dx, dy = STEP[d]
        return ((x + dx) % W, (y + dy) % H)

    def free_sides(h):
        occ = set()
        for bb in bodies.values():
            occ.update(bb)
        n = 0
        for d in range(4):
            if edges.get(edge_id(W, H, h[0], h[1], d), (0, -1))[0] == 1:
                continue
            if dest(h, d) not in occ:
                n += 1
        return n

    def top_of(s):
        best = None
        for i, b in bodies.items():
            if side(i) == s and (best is None or (len(b), -i) > (len(bodies[best]), -best)):
                best = i
        return best

    EAT = Counter()      # (w, s, role, origin) role: q queen, t longest 5+ (not queen), o other; origin: n natural, e their dead, or own-dead kind
    STOPS = []           # deliberate stops
    BIG = []             # deaths of queens and of longest dragons of 8+
    DROP = Counter()     # (w, side of the dead, kind, fate) pearls
    present = {}
    rnd, actor, dirs, used = -1, None, [], 0
    expected = 0
    last_death = None
    victim_kind = None
    turnL0 = 0
    track = []           # every 25 rounds: for each side queen length, longest, second longest, alive
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd % 25 == 0:
                row = [rnd]
                near = []
                for s in (0, 1):
                    ls = sorted((len(b) for i, b in bodies.items() if side(i) == s), reverse=True)
                    row += [len(bodies.get(queens[s], ())), ls[0] if ls else 0, ls[1] if len(ls) > 1 else 0, len(ls), sum(ls)]
                    tp = top_of(s)
                    ds = [gap(b[0], bodies[tp][0]) for i, b in bodies.items() if side(i) == s and i != tp] if tp is not None else []
                    near.append([len(ds), sum(ds), sum(1 for d in ds if d <= 6), sum(1 for d in ds if d <= 15)])
                track.append(row + near[0] + near[1])
        elif k == 1:
            actor, dirs, used = p.i32(0), [], 0
            turnL0 = len(bodies[actor])
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            used = 0
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if expected:
                    present[c] = last_death
                    expected -= 1
                else:
                    present[c] = None
            else:
                rec = present.pop(c)
                s = side(actor)
                t = top_of(s)
                role = 'q' if actor == queens[s] else 't' if (actor == t and turnL0 >= 5) else 'o'
                if rec is None:
                    origin = 'n'
                elif rec['s'] != s:
                    origin = 'e'
                else:
                    origin = rec['k']
                EAT[(wnd(rnd), s, role, origin)] += 1
                if rec is not None:
                    fate = ('own ' + role) if rec['s'] == s else 'enemy'
                    DROP[(wnd(rec['r']), rec['s'], rec['k'], fate)] += 1
                    rec['left'] -= 1
                    if rec.get('stop') is not None and rec['s'] == s:
                        rec['stop']['by_' + role] += 1
                        if actor == rec['stop']['nid']:
                            rec['stop']['by_n'] += 1
                        if rnd - rec['r'] <= 10:
                            rec['stop']['fast'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            L, h, s = len(b), b[0], side(i)
            t = top_of(s)
            if reason == 3:
                if i != actor:
                    kd = 'rammed' if side(actor) != s else 'mate head'
                    victim_kind = kd
                else:
                    kd = 'rams' if victim_kind == 'rammed' else 'mate head'
            elif reason == 2:
                kd = 'body'
                if i == actor and used < len(dirs):
                    c = dest(h, dirs[used])
                    owners = [z for z, bb in bodies.items() if z != i and c in bb]
                    if len(owners) == 1 and side(owners[0]) == s:
                        kd = 'mate body'
            elif reason in (0, 1):
                kd = 'boxed' if free_sides(h) == 0 else 'own move'
            else:
                kd = 'boxed' if free_sides(h) == 0 else 'stop'
            rec = dict(r=rnd, s=s, k=kd, left=(L + 1) // 2, L=L)
            DROP[(wnd(rnd), s, kd, 'dropped')] += (L + 1) // 2
            DROP[(wnd(rnd), s, kd, 'dragons')] += 1
            DROP[(wnd(rnd), s, kd, 'length')] += L
            if kd == 'stop':
                qd = gap(h, bodies[queens[s]][0]) if queens[s] in bodies and queens[s] != i else None
                td = gap(h, bodies[t][0]) if t is not None and t != i else None
                st = dict(r=rnd, s=s, L=L, qd=qd, td=td, tL=len(bodies[t]) if t is not None else 0, qL=len(bodies.get(queens[s], ())),
                          tq=int(t == queens[s]), n=sum(1 for z in bodies if side(z) == s), by_q=0, by_t=0, by_o=0, fast=0, drop=(L + 1) // 2,
                          e4=sum(1 for z, bb in bodies.items() if side(z) != s and gap(h, bb[0]) <= 4))
                big = sorted((gap(h, bb[0]), -len(bb), z) for z, bb in bodies.items() if side(z) == s and z != i and len(bb) >= 2 * L)
                lon = sorted((gap(h, bb[0]), -len(bb), z) for z, bb in bodies.items() if side(z) == s and z != i and len(bb) > L)
                st['d2'] = big[0][0] if big else None
                st['L2'] = -big[0][1] if big else 0
                st['d1'] = lon[0][0] if lon else None
                st['L1'] = -lon[0][1] if lon else 0
                st['by_n'] = 0
                st['nid'] = big[0][2] if big else (lon[0][2] if lon else -1)
                st['seen2'] = int(any(abs(dx) <= 3 and abs(dy) <= 3 for dx, dy in [((bodies[z][0][0] - h[0] + W // 2) % W - W // 2, (bodies[z][0][1] - h[1] + H // 2) % H - H // 2) for _, _, z in big[:6]]))
                STOPS.append(st)
                rec['stop'] = st
            if i == queens[s] or (i == t and L >= 8):
                BIG.append(dict(r=rnd, s=s, L=L, k=kd, q=int(i == queens[s]), top=int(i == t),
                                mL0=turnL0 if (reason == 3 and i != actor) else None, msteps=used + 1 if (reason == 3 and i != actor) else None))
            last_death = rec
            expected = (L + 1) // 2
            bodies.pop(i)
    fin = root.pointer(4)
    winner = fin.u16(6) if fin.u16(4) == 1 else None
    ends = []
    for s in (0, 1):
        ls = sorted((len(b) for i, b in bodies.items() if side(i) == s), reverse=True)
        ends.append([len(bodies.get(queens[s], ())), ls[0] if ls else 0, ls[1] if len(ls) > 1 else 0, len(ls), sum(ls)])
    return dict(src=label, gid=j['id'], map=j['mapName'], cells=W * H, opp=j['team' + 'AB'[1 - own] + 'Name'],
                result='draw' if winner is None else 'win' if winner == own else 'loss', last=rnd, ends=ends, track=track,
                EAT=[list(key) + [n] for key, n in sorted(EAT.items())], DROP=[list(key) + [n] for key, n in sorted(DROP.items())],
                STOPS=STOPS, BIG=BIG)


def main():
    src, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else None
    todo = [t for n, t in enumerate(jobs(src)) if n % shards == shard]
    name = 'wq_feed-test.jsonl'
    if limit is None:
        if src == 'O' and shard == 0:
            name = 'wq_feed-O0.jsonl'
        elif src == 'O':
            name = 'wq_feed-O1.jsonl'
        elif shard == 0:
            name = 'wq_feed-R0.jsonl'
        else:
            name = 'wq_feed-R1.jsonl'
    else:
        todo = todo[:limit]
    with open(OUT + name, 'w') as f:
        for n, (label, path, j, team) in enumerate(todo):
            f.write(json.dumps(scan(label, path, j, team), separators=(',', ':')) + '\n')
            f.flush()
            if n % 20 == 19:
                print(src, shard, n + 1, len(todo), flush=True)
    print('done', src, shard, len(todo))


main()
