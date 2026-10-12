"""Scratch (diag-wipeout): one pass over each replay with my own state machine (not the shared reader). Per game one
JSON row: end-of-round state of both sides, every death with its context (cause, length, heads within 5 tiles, zone,
the rammer's turn-start length and steps, who ate its drops), every turn that began with an enemy head within 2 tiles
and how it ended, per-round turn/split/eat counts and a 5-round spacing sample.
Usage: python3 data/analysis/ladder/dossier/work/wo_scan.py <O|L|R> <shard> <shards> [limit]
O = online smoke labels (team 1119), L = our 500 ladder games, R = rank-1 (team 306) 597 games."""
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
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'sr51-bob1', 'agg7-b1', 'agg7-b2', 'agg7-b3')


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
            out.append((src, rp, j, team, r))
        out.sort(key=lambda t: t[2]['id'])
    return out


def scan(label, path, j, team, row):
    root = replay.load(path).root()
    text = root.text(0)
    lines = text.splitlines()
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
    assert j['team' + 'AB'[own] + 'Id'] == team and j['team' + 'AB'[1 - own] + 'Id'] != team

    def side(i):
        return 0 if teams[i] == own else 1

    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    starts = [[bodies[i][0] for i in bodies if side(i) == s] for s in (0, 1)]

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

    def sample():
        heads = [[], []]
        for i, b in bodies.items():
            heads[side(i)].append((b[0], len(b)))
        out = []
        for s in (0, 1):
            mine, other = heads[s], heads[1 - s]
            n = len(mine)
            if not n:
                out += [0, 0, 0, 0, 0, 0]
                continue
            near_own = sum(sum(1 for c, _ in mine if gap(h, c) <= 5) - 1 for h, _ in mine)
            alone = sum(1 for h, _ in mine if sum(1 for c, _ in mine if gap(h, c) <= 5) == 1)
            ne = [min((gap(h, c) for c, _ in other), default=99) for h, _ in mine]
            out += [n, near_own, alone, sum(1 for x in ne if x <= 3), sum(min(x, 30) for x in ne), sum(1 for _, L in mine if L == 2)]
        return out

    snap, samples, deaths = {}, [], []
    rc = defaultdict(lambda: [0] * 10)   # per round: per side turns, splits, natural eaten, drop eaten, steps
    contact = defaultdict(int)           # (round, side, own L0 capped 9, target L capped 19, d0, outcome) -> n
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
        i, s, L0, tgt, d0, Lt = turn['i'], turn['s'], turn['L0'], turn['tgt'], turn['d0'], turn['Lt']
        rc[rnd][s * 5 + 4] += used
        if tgt is not None:
            if turn['ram']:
                oc = 'R'
            elif i not in bodies:
                oc = 'D'
            else:
                d1 = gap(bodies[i][0], tgt)
                oc = 'A' if d1 > d0 else 'C' if d1 < d0 else 'S'
            contact[(rnd, s, min(L0, 9), min(Lt, 19), d0, oc)] += 1
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
            if rnd % 5 == 0:
                samples.append([rnd] + sample())
        elif k == 1:
            close_turn()
            actor, dirs, used, act = p.i32(0), [], 0, None
            victim = None
            b = bodies[actor]
            s = side(actor)
            rc[rnd][s * 5] += 1
            best = None
            for z, bb in bodies.items():
                if side(z) != s:
                    g = gap(b[0], bb[0])
                    if g <= 2 and (best is None or g < best[0]):
                        best = (g, bb[0], len(bb))
            turn = dict(i=actor, s=s, L0=len(b), h0=b[0], eaten=0, ram=False,
                        tgt=best[1] if best else None, d0=best[0] if best else None, Lt=best[2] if best else 0)
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
                rc[rnd][s * 5 + (3 if rec is not None else 2)] += 1
                if rec is not None:
                    rec['eat'][s] += 1
                    if rnd - rec['r'] <= 5:
                        rec['eat5'][s] += 1
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
            rc[rnd][side(parent) * 5 + 1] += 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif k == 11:
            assert not expected
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            L, h, s = len(b), b[0], side(i)
            mates = [(gap(h, bb[0]), len(bb)) for z, bb in bodies.items() if z != i and side(z) == s]
            foes = [(gap(h, bb[0]), len(bb)) for z, bb in bodies.items() if side(z) != s]
            d_own = min(gap(h, c) for c in starts[s])
            d_th = min(gap(h, c) for c in starts[1 - s])
            d = dict(r=rnd, s=s, i=i, L=L, c=CAUSE[reason], q=int(i == queens[s]),
                     top=int(L == max(len(bb) for z, bb in bodies.items() if side(z) == s)),
                     o5=sum(1 for g, _ in mates if g <= 5), e5=sum(1 for g, _ in foes if g <= 5),
                     o3=sum(1 for g, _ in mates if g <= 3), e3=sum(1 for g, _ in foes if g <= 3),
                     om=max((m for g, m in mates if g <= 3), default=0),
                     z=round(d_own / (d_own + d_th), 3) if d_own + d_th else 0.5, xy=list(h),
                     na=len(mates) + 1, nf=len(foes), eat=[0, 0], eat5=[0, 0], drop=(L + 1) // 2,
                     act=int(i == actor))
            if reason in (0, 1, 2):
                d['free'] = free_sides(h)
            if reason == 2 and i == actor and used < len(dirs):
                c = dest(h, dirs[used])
                owners = [z for z, bb in bodies.items() if z != i and c in bb]
                if len(owners) == 1:
                    d['hit'] = 'mate' if side(owners[0]) == s else 'enemy'
            if reason == 4:
                d['c'] = (act or 'no action') if i == actor else 'no action'
                d['free'] = free_sides(h)
            if i == actor and turn is not None:
                d['L0'] = turn['L0']
                d['steps'] = used + (1 if reason in (0, 1, 2, 3) else 0)
                d['ate'] = turn['eaten']
            if reason == 3:
                if i != actor:
                    victim = d
                    d['role'] = 'hit'
                    ab = bodies[actor]
                    d['m'] = dict(i=actor, s=side(actor), L=len(ab), L0=turn['L0'], steps=used + 1, ate=turn['eaten'],
                                  q=int(actor == queens[side(actor)]), d0=gap(turn['h0'], h))
                    d['cross'] = int(side(actor) != s)
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
    out = dict(src=label, gid=j['id'], map=j['mapName'], W=W, H=H, cells=W * H,
               layout=hashlib.md5(text.encode()).hexdigest()[:10],
               opp=j['team' + 'AB'[1 - own] + 'Name'], opp_id=j['team' + 'AB'[1 - own] + 'Id'],
               result='draw' if winner is None else 'win' if winner == own else 'loss', last=last,
               end_reason=fin.u16(2), final=snap[last],
               snap=[snap.get(r, None) for r in range(last + 1)], deaths=deaths, samples=samples,
               rc=[[r] + v for r, v in sorted(rc.items())],
               contact=[list(key) + [n] for key, n in sorted(contact.items())])
    if row is not None:
        out['layout_key'] = row['layout_key']
        out['opp_rating'] = row['opponent_rating']
        assert row['final_reconstructed']['alive'] == out['final'][0], (j['id'], 'alive differs from dossier row')
    return out


def main():
    src, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else None
    todo = [t for n, t in enumerate(jobs(src)) if n % shards == shard]
    name = 'wo_scan-test.jsonl'
    if limit is None:
        if src == 'O':
            name = 'wo_scan-O0.jsonl'
        elif src == 'L' and shard == 0:
            name = 'wo_scan-L0.jsonl'
        elif src == 'L' and shard == 1:
            name = 'wo_scan-L1.jsonl'
        elif src == 'L':
            name = 'wo_scan-L2.jsonl'
        elif shard == 0:
            name = 'wo_scan-R0.jsonl'
        elif shard == 1:
            name = 'wo_scan-R1.jsonl'
        else:
            name = 'wo_scan-R2.jsonl'
    else:
        todo = todo[:limit]
    with open(OUT + name, 'w') as f:
        for n, (label, path, j, team, row) in enumerate(todo):
            f.write(json.dumps(scan(label, path, j, team, row), separators=(',', ':')) + '\n')
            if n % 20 == 19:
                print(src, shard, n + 1, len(todo), flush=True)
    print('done', src, shard, len(todo))


main()
