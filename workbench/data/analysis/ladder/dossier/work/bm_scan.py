"""Scratch (diag-bigmap): one pass over each replay with my own state machine (after wo_scan.py). Per game one JSON
row: end-of-round state of both sides, every death with context (cause, length, zone seen from side 0, the rammer's
turn-start length, steps, straight distance and segments paid, who ate its drops, whether a long mate stood near),
pearls eaten by eater class and origin, splits by length, the longest dragon of each side every 10 rounds, head
positions by third of the map, length histograms, and every turn that began with an enemy head within 3 tiles.
Usage: python3 data/analysis/ladder/dossier/work/bm_scan.py <O|L|R> <shard> <shards> <min cells> [limit]
O = online labels of 8 Oct (team 1119), L = our 500 ladder games, R = rank-1 (team 306)."""
import sys, json, hashlib
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSE = ('wall', 'own body', 'other body', 'head-on', 'other')
OTHER = ('unpaid sprint', 'illegal split', 'no action', 'timeout')
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2')
HIST = (50, 100, 150, 200, 250, 300, 350, 400, 450, 500)


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
                    out.append((label, rp, j, 1119, None))
    else:
        path = Path('data/analysis/ladder/dossier') / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            rp = Path(r['replay'])
            j = json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text())
            out.append((src, rp, j, team, dict(layout_key=r['layout_key'], opponent_rating=r['opponent_rating'])))
        out.sort(key=lambda t: t[2]['id'])
    return out


def lb(L):
    return L if L <= 4 else 5 if L <= 9 else 10


def scan(label, path, j, team, row, min_cells):
    root = replay.load(path).root()
    text = root.text(0)
    lines = text.splitlines()
    W, H = map(int, lines[0].split()[1:3])
    if W * H <= min_cells:
        return None
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
    assert j['team' + 'AB'[own] + 'Id'] == team and j['team' + 'AB'[1 - own] + 'Id'] != team

    def side(i):
        return 0 if teams[i] == own else 1

    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    starts = [[bodies[i][0] for i in bodies if side(i) == s] for s in (0, 1)]
    start_len = [[len(bodies[i]) for i in sorted(bodies) if side(i) == s] for s in (0, 1)]

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def inview(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3

    zcache = {}

    def zone(h):
        if h not in zcache:
            a = min(gap(h, c) for c in starts[0])
            b = min(gap(h, c) for c in starts[1])
            zcache[h] = round(a / (a + b), 3) if a + b else 0.5
        return zcache[h]

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
            if dest(h, d) in occ:
                continue
            n += 1
        return n

    def state():
        out = []
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if side(i) == s]
            out += [len(ls), sum(ls), max(ls, default=0), len(bodies.get(queens[s], ()))]
        return out

    def histo():
        out = []
        for s in (0, 1):
            c = [0] * 6
            for i, b in bodies.items():
                if side(i) == s:
                    L = len(b)
                    c[0 if L == 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 7 else 4 if L <= 14 else 5] += 1
            out.append(c)
        return out

    def leaders():
        out = []
        for s in (0, 1):
            mine = [(i, b) for i, b in bodies.items() if side(i) == s]
            if not mine:
                out.append(None)
                continue
            i, b = min(mine, key=lambda t: (-len(t[1]), t[0]))
            h = b[0]
            o5 = sum(1 for z, bb in mine if z != i and gap(h, bb[0]) <= 5)
            foes = [(gap(h, bb[0]), len(bb)) for z, bb in bodies.items() if side(z) != s]
            out.append([i, len(b), zone(h), o5, sum(1 for g, _ in foes if g <= 5), min((g for g, _ in foes), default=99),
                        sum(1 for g, L in foes if g <= 8 and L <= 4), int(i == queens[s])])
        return out

    def positions():
        out = []
        for s in (0, 1):
            c = [0] * 6
            for i, b in bodies.items():
                if side(i) == s:
                    z = zone(b[0])
                    if s == 1:
                        z = 1 - z
                    c[(0 if len(b) <= 4 else 3) + (0 if z < 0.35 else 2 if z > 0.65 else 1)] += 1
            out.append(c)
        return out

    snap, deaths = {}, []
    hist, lead, pos = {}, [], []
    rc = defaultdict(lambda: [0] * 12)   # per round, per side: turns, splits, natural eaten, drop eaten, steps, paid
    contact = defaultdict(int)
    chit = defaultdict(int)
    eats = defaultdict(int)
    splits = defaultdict(int)
    last_contact = {}
    present = {}
    rnd, actor, dirs, used, act = -1, None, [], 0, None
    turn = None
    expected = 0
    last_death = None
    victim = None

    def close_turn():
        nonlocal turn
        if turn is None:
            return
        i, s, L0 = turn['i'], turn['s'], turn['L0']
        if i in bodies:
            paid = L0 + turn['eaten'] - len(bodies[i]) - turn['child']
        else:
            paid = L0 + turn['eaten'] - turn['dL']
        rc[rnd][s * 6 + 4] += used
        rc[rnd][s * 6 + 5] += paid
        tgt = turn['tgt']
        if tgt is not None:
            g, tp, Lt, tz = tgt
            if turn['ram']:
                oc = 'R'
            elif i not in bodies:
                oc = 'D'
            else:
                d1 = gap(bodies[i][0], tp)
                oc = 'A' if d1 > g else 'C' if d1 < g else 'S'
            key = (rnd // 50, s, lb(L0), lb(Lt), g, 1 if turn['edge'] >= 1 else 0, oc, turn['q'])
            contact[key] += 1
            if i in bodies:
                last_contact[i] = key
        turn = None

    events = root.pointer(3)
    for idx, ev in enumerate(events):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close_turn()
            if rnd >= 0:
                snap[rnd] = state()
            rnd, actor = p.i32(0), None
            if rnd % 10 == 0:
                lead.append([rnd] + leaders())
                pos.append([rnd] + positions())
            if rnd in HIST:
                hist[rnd] = histo()
        elif k == 1:
            close_turn()
            actor, dirs, used, act = p.i32(0), [], 0, None
            victim = None
            b = bodies[actor]
            s = side(actor)
            h = b[0]
            rc[rnd][s * 6] += 1
            last_contact.pop(actor, None)
            best = None
            al = en = top = 0
            for z, bb in bodies.items():
                if side(z) == s:
                    if len(bb) > top:
                        top = len(bb)
                    if z != actor and inview(h, bb[0]):
                        al += 1
                else:
                    if inview(h, bb[0]):
                        en += 1
                    g = gap(h, bb[0])
                    if g <= 3 and (best is None or (g, -len(bb)) < (best[0], -best[2])):
                        best = (g, bb[0], len(bb), z)
            turn = dict(i=actor, s=s, L0=len(b), h0=h, eaten=0, ram=False, child=0, top=top, edge=al + 1 - en,
                        tgt=best, dL=None, q=int(actor == queens[s]))
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            used = 0
            used_up = p.pointer(1)
            act = 'timeout' if p.bit(32) or (used_up is not None and used_up.bit(64)) else OTHER[a.u16(0)] if a and a.u16(0) < 3 else 'no action'
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                assert c not in present
                if expected:
                    present[c] = last_death
                    expected -= 1
                else:
                    assert actor is None
                    present[c] = None
            else:
                rec = present.pop(c)
                s = side(actor)
                turn['eaten'] += 1
                rc[rnd][s * 6 + (3 if rec is not None else 2)] += 1
                Lnow = len(bodies[actor])
                kind = 'q' if actor == queens[s] else lb(Lnow) if Lnow <= 4 else 5 if Lnow <= 9 else 10
                origin = 0 if rec is None else 3 if rec['s'] != s else 1 if rec.get('fed') else 2
                eats[(rnd // 50, s, kind, int(Lnow >= turn['top']), origin)] += 1
                if rec is not None:
                    rec['eat'][s] += 1
                    if rnd - rec['r'] <= 5:
                        rec['eat5'][s] += 1
                    if Lnow >= 10 or Lnow >= turn['top']:
                        rec['eatB'][s] += 1
        elif k == 9:
            assert not expected
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            assert b[-1] == tl
        elif k == 10:
            assert not expected
            parent, child = p.i32(0), p.i32(4)
            rc[rnd][side(parent) * 6 + 1] += 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if turn is not None and parent == turn['i']:
                turn['child'] += len(bodies[child])
            splits[(rnd // 50, side(parent), min(len(bodies[parent]) + len(bodies[child]), 12), len(bodies[child]))] += 1
        elif k == 11:
            assert not expected
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            L, h, s = len(b), b[0], side(i)
            mates = [(gap(h, bb[0]), len(bb)) for z, bb in bodies.items() if z != i and side(z) == s]
            foes = [(gap(h, bb[0]), len(bb)) for z, bb in bodies.items() if side(z) != s]
            tl_ = max([L] + [m for _, m in mates])
            d = dict(r=rnd, s=s, i=i, L=L, c=CAUSE[reason], q=int(i == queens[s]), top=int(L == tl_), tl=tl_,
                     tf=max((m for _, m in foes), default=0),
                     o5=sum(1 for g, _ in mates if g <= 5), e5=sum(1 for g, _ in foes if g <= 5),
                     m5=max((m for g, m in mates if g <= 5), default=0), m10=max((m for g, m in mates if g <= 10), default=0),
                     zo=zone(h), xy=list(h), na=len(mates) + 1, nf=len(foes), eat=[0, 0], eat5=[0, 0], eatB=[0, 0],
                     drop=(L + 1) // 2, act=int(i == actor))
            if reason in (0, 1, 2):
                d['free'] = free_sides(h)
            if reason == 2 and i == actor and used < len(dirs):
                c = dest(h, dirs[used])
                owners = [z for z, bb in bodies.items() if z != i and c in bb]
                if len(owners) == 1:
                    d['hit'] = 'mate' if side(owners[0]) == s else 'enemy'
                    d['hitL'] = len(bodies[owners[0]])
            if reason == 4:
                d['c'] = (act or 'no action') if i == actor else 'no action'
                d['free'] = free_sides(h)
                d['fed'] = int(d['c'] == 'no action' and d['free'] > 0 and d['m10'] >= 2 * L and not d['q'])
            if i == actor and turn is not None:
                d['L0'] = turn['L0']
                d['steps'] = used + (1 if reason in (0, 1, 2, 3) else 0)
                d['ate'] = turn['eaten']
                turn['dL'] = L
            if reason == 3:
                if i != actor:
                    victim = d
                    d['role'] = 'hit'
                    ab = bodies[actor]
                    d['m'] = dict(i=actor, s=side(actor), L=len(ab), L0=turn['L0'], steps=used + 1, ate=turn['eaten'],
                                  paid=turn['L0'] + turn['eaten'] - len(ab), q=int(actor == queens[side(actor)]),
                                  d0=gap(turn['h0'], h), edge=turn['edge'])
                    d['cross'] = int(side(actor) != s)
                    if d['cross'] and i in last_contact:
                        chit[last_contact[i]] += 1
                else:
                    assert victim is not None
                    d['role'] = 'mover'
                    d['v'] = dict(i=victim['i'], s=victim['s'], L=victim['L'], q=victim['q'], top=victim['top'])
                    d['cross'] = int(victim['s'] != s)
                    if d['cross']:
                        turn['ram'] = True
            deaths.append(d)
            last_death = d
            expected = (L + 1) // 2
            bodies.pop(i)
            last_contact.pop(i, None)
    close_turn()
    assert not expected
    snap[rnd] = state()
    fin = root.pointer(4)
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if teams[i] == z]
        st = fin.pointer(z)
        assert (len(ls), max(ls, default=0), sum(ls)) == (st.i32(0), st.i32(4), st.i32(8)), (j['id'], 'final state')
    winner = fin.u16(6) if fin.u16(4) == 1 else None
    assert (None if winner is None else 'ab'[winner]) == j.get('winner'), (j['id'], 'winner')
    last = max(snap)
    arm = 'MAIN' if label.startswith('agg7-m') else 'B7' if label.startswith('agg7-b') else 'B7Q' if label.startswith('agg8-q') else label
    out = dict(src=label, arm=arm, gid=j['id'], map=j['mapName'], W=W, H=H, cells=W * H,
               layout=hashlib.md5(text.encode()).hexdigest()[:10], start_len=start_len,
               opp=j['team' + 'AB'[1 - own] + 'Name'], opp_id=j['team' + 'AB'[1 - own] + 'Id'],
               result='draw' if winner is None else 'win' if winner == own else 'loss', last=last,
               end_reason=fin.u16(2), final=snap[last],
               snap=[snap.get(r, None) for r in range(last + 1)], deaths=deaths,
               hist=[[r] + v for r, v in sorted(hist.items())], lead=lead, pos=pos,
               rc=[[r] + v for r, v in sorted(rc.items())],
               contact=[list(key) + [n, chit.get(key, 0)] for key, n in sorted(contact.items(), key=str)],
               eats=[list(key) + [n] for key, n in sorted(eats.items(), key=str)],
               splits=[list(key) + [n] for key, n in sorted(splits.items())])
    if row is not None:
        out['layout_key'] = row['layout_key']
        out['opp_rating'] = row['opponent_rating']
    return out


def main():
    src, shard, shards, min_cells = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    limit = int(sys.argv[5]) if len(sys.argv) > 5 else None
    todo = [t for n, t in enumerate(jobs(src)) if n % shards == shard]
    name = 'bm_scan-test.jsonl'
    if limit is None:
        if src == 'O' and shard == 0:
            name = 'bm_scan-O0.jsonl'
        elif src == 'O':
            name = 'bm_scan-O1.jsonl'
        elif src == 'L' and shard == 0:
            name = 'bm_scan-L0.jsonl'
        elif src == 'L':
            name = 'bm_scan-L1.jsonl'
        elif shard == 0:
            name = 'bm_scan-R0.jsonl'
        else:
            name = 'bm_scan-R1.jsonl'
    else:
        todo = todo[:limit]
    done = 0
    with open(OUT + name, 'w') as f:
        for n, (label, path, j, team, row) in enumerate(todo):
            g = scan(label, path, j, team, row, min_cells)
            if g is not None:
                f.write(json.dumps(g, separators=(',', ':')) + '\n')
                done += 1
            if n % 20 == 19:
                print(src, shard, n + 1, len(todo), done, flush=True)
    print('done', src, shard, len(todo), done)


main()
