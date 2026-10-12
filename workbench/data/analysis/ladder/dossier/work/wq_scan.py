"""Scratch (diag-whq): one pass over each replay with my own state machine. Per game one JSON row for both sides:
turns, steps, paid segments and pearls by length class, window and zone; splits by length; end-of-round state; every death
with context (cause, length, heads near, zone, the rammer's turn-start length, steps, paid, what it ate); contact turns
(nearest enemy head within 3 tiles) and how they end; every cross-team ram seen from the victim's last own turn; samples
every 5 rounds (queen, longest, crowd).
Usage: python3 data/analysis/ladder/dossier/work/wq_scan.py <O|L|R> <shard> <shards> [limit]"""
import sys, json, hashlib
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSE = ('wall', 'own body', 'other body', 'head-on', 'other')
OTHER = ('unpaid sprint', 'illegal split', 'no action', 'timeout')
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
    return 0 if r <= 40 else 1 if r <= 100 else 2 if r <= 200 else 3 if r <= 300 else 4 if r <= 400 else 5


def cls(L):
    return 0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 9 else 4


def scan(label, path, j, team):
    root = replay.load(path).root()
    text = root.text(0)
    lines = text.splitlines()
    W, H = map(int, lines[0].split()[1:3])
    cells = W * H
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
    assert j['team' + 'AB'[own] + 'Id'] == team

    def side(i):
        return 0 if teams[i] == own else 1

    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    starts = [[bodies[i][0] for i in bodies if side(i) == s] for s in (0, 1)]
    start_len = [[len(bodies[i]) for i in bodies if side(i) == s] for s in (0, 1)]
    qstart = [bodies[queens[s]][0] for s in (0, 1)]
    nb = {}
    zc = {}

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def zone(h, s):
        if h not in zc:
            d_own = min(gap(h, c) for c in starts[0])
            d_th = min(gap(h, c) for c in starts[1])
            f = d_own / (d_own + d_th) if d_own + d_th else 0.5
            zc[h] = 0 if f < 0.35 else 2 if f > 0.65 else 1
        return zc[h] if s == 0 else 2 - zc[h]

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

    def neighbours(c):
        if c not in nb:
            out = []
            for d in range(4):
                if edges.get(edge_id(W, H, c[0], c[1], d), (0, -1))[0] == 1:
                    continue
                out.append(dest(c, d))
            nb[c] = out
        return nb[c]

    def inview(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3

    def reach_map(e, occ, depth):
        dist = {e: 0}
        q = deque([e])
        while q:
            c = q.popleft()
            if dist[c] >= depth:
                continue
            for n in neighbours(c):
                if n in dist or n in occ:
                    continue
                dist[n] = dist[c] + 1
                q.append(n)
        return dist

    def free_sides(h):
        occ = set()
        for bb in bodies.values():
            occ.update(bb)
        return sum(1 for n in neighbours(h) if n not in occ)

    def state():
        out = []
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if side(i) == s]
            out += [len(ls), sum(ls), max(ls, default=0), len(bodies.get(queens[s], ()))]
        return out

    def sample():
        heads = [[], []]
        for i, b in bodies.items():
            heads[side(i)].append((b[0], len(b), i))
        out = []
        for s in (0, 1):
            mine, other = heads[s], heads[1 - s]
            n = len(mine)
            if not n:
                out.append(None)
                continue
            own5 = [sum(1 for c, _, _ in mine if gap(h, c) <= 5) - 1 for h, _, _ in mine]
            en5 = [sum(1 for c, _, _ in other if gap(h, c) <= 5) for h, _, _ in mine]
            en3 = [sum(1 for c, _, _ in other if gap(h, c) <= 3) for h, _, _ in mine]
            zs = [0, 0, 0]
            zl = [0, 0, 0]
            for h, L, _ in mine:
                zs[zone(h, s)] += 1
                zl[zone(h, s)] += L
            top = max(range(n), key=lambda k: (mine[k][1], -mine[k][2]))
            qi = [k for k in range(n) if mine[k][2] == queens[s]]
            rec = dict(n=n, o5=sum(own5), e5=sum(en5), e3=sum(en3), zs=zs, zl=zl,
                       top=[mine[top][1], zone(mine[top][0], s), own5[top], en5[top], en3[top], int(mine[top][2] == queens[s])])
            if qi:
                k = qi[0]
                rec['q'] = [mine[k][1], zone(mine[k][0], s), own5[k], en5[k], en3[k], gap(mine[k][0], qstart[s])]
            out.append(rec)
        return out

    snap, samples, deaths, rams = {}, [], [], []
    T = Counter()
    E = Counter()
    S = Counter()
    MV = Counter()
    contact = Counter()
    expo = Counter()
    rc = defaultdict(lambda: [0] * 10)
    present = {}
    last = {}
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
        w = wnd(rnd)
        c0 = cls(L0)
        rc[rnd][s * 5 + 4] += used
        alive = i in bodies
        paid = 0
        if alive and not turn['split']:
            paid = L0 + turn['eaten'] - len(bodies[i])
        elif not alive:
            paid = turn.get('paid', 0)
        MV[(w, s, c0, 'steps')] += used
        if used >= 2:
            MV[(w, s, c0, 'sprints')] += 1
        if paid > 0:
            MV[(w, s, c0, 'paid turns')] += 1
            MV[(w, s, c0, 'paid segs')] += paid
        if used == 0 and alive and not turn['split']:
            MV[(w, s, c0, 'stay')] += 1
        if turn['tgt'] is not None:
            if turn['ram']:
                oc = 'R'
            elif not alive:
                oc = 'D'
            else:
                d1 = gap(bodies[i][0], turn['tgt'])
                oc = 'A' if d1 > turn['d0'] else 'C' if d1 < turn['d0'] else 'S'
            Lt = turn['Lt']
            rel = 0 if Lt < L0 else 1 if Lt < 2 * L0 else 2
            contact[(w, s, min(L0, 5), rel, turn['d0'], turn['tq'], turn['ttop'], int(turn['q']), oc)] += 1
        if alive and turn['foes'] is not None:
            p1 = bodies[i][0]
            foes = turn['foes']
            t1 = any(m.get(p1, 9) <= 1 for _, _, _, m, _, _ in foes)
            tR = any(m.get(p1, 9) <= rt for _, _, _, m, rt, _ in foes)
            tS = any(rs is not None and m.get(p1, 9) <= rs for _, _, _, m, _, rs in foes)
            altR = any(not any(m.get(n, 9) <= rt for _, _, _, m, rt, _ in foes) for n in turn['cand'])
            altS = any(not any(rs is not None and m.get(n, 9) <= rs for _, _, _, m, _, rs in foes) for n in turn['cand'])
            rec = dict(r=rnd, t1=t1, tR=tR, tS=tS, altR=altR, altS=altS, ate=turn['eaten'] > 0, trader=turn['trader'],
                       ids=dict((z, (parts, Lz, m.get(p1, 9), rt)) for z, parts, Lz, m, rt, _ in foes), L=L0, q=turn['q'],
                       moved=used, split=turn['split'])
            last[i] = rec
            kind = 'Q' if turn['q'] else 'S'
            if foes:
                expo[(s, kind, 'turns with an enemy head in view')] += 1
                if t1:
                    expo[(s, kind, 'ends beside a head')] += 1
                elif tR:
                    expo[(s, kind, 'ends in true reach, not beside')] += 1
                    if altR and not turn['eaten']:
                        expo[(s, kind, 'ends in true reach by choice')] += 1
                        rec['choice'] = True
                    if tS:
                        expo[(s, kind, 'ends in parts-1 reach, not beside')] += 1
                        if altS and not turn['eaten'] and not turn['trader']:
                            expo[(s, kind, 'ends in parts-1 reach by choice')] += 1
                            rec['choiceS'] = True
        elif alive:
            last[i] = dict(r=rnd, ids={}, L=L0, q=turn['q'], long=True)
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
            h = b[0]
            L0 = len(b)
            isq = actor == queens[s]
            rc[rnd][s * 5] += 1
            T[(wnd(rnd), s, cls(L0), zone(h, s), int(isq))] += 1
            best = None
            emax = 0
            seen = []
            for z, bb in bodies.items():
                if side(z) != s:
                    if len(bb) > emax:
                        emax = len(bb)
                    g = gap(h, bb[0])
                    if g <= 3 and (best is None or g < best[0]):
                        best = (g, bb[0], len(bb), z)
                    if g <= 6 and inview(h, bb[0]):
                        seen.append((z, bb))
            last.pop(actor, None)
            foes = None
            cand = []
            trader = False
            if L0 <= 4 or isq:
                foes = []
                if seen:
                    occ = set()
                    for bb in bodies.values():
                        occ.update(bb)
                    worth = False
                    for z, bb in seen:
                        parts = sum(1 for c in bb if inview(h, c))
                        Lz = len(bb)
                        rt = min(5, (Lz + 3) // 4 + max(0, Lz - 2))
                        rs = max(1, parts - 1) if parts < 5 else None
                        foes.append((z, parts, Lz, reach_map(bb[0], occ - {bb[0]}, 5), rt, rs))
                        worth = worth or (parts >= L0 if cells <= 1200 else parts >= max(5, L0 + 2))
                    allies = sum(1 for z, bb in bodies.items() if side(z) == s and z != actor and inview(h, bb[0]))
                    units = sum(1 for z in bodies if side(z) == s)
                    trader = worth and rnd <= 400 and allies + 1 - len(seen) >= 1 and (cells <= 1200 or units >= 8)
                    cand = [n for n in neighbours(h) if n not in occ]
            turn = dict(i=actor, s=s, L0=L0, h0=h, eaten=0, ram=False, split=False, q=isq,
                        tgt=best[1] if best else None, d0=best[0] if best else None, Lt=best[2] if best else 0,
                        tq=int(best is not None and best[3] == queens[1 - s]),
                        ttop=int(best is not None and best[2] == emax and emax >= 5),
                        foes=foes, cand=cand, trader=trader)
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
                origin = 0 if rec is None else 1 if rec['s'] == s else 2
                E[(wnd(rnd), s, cls(turn['L0']), origin, int(turn['q']))] += 1
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
            Lb = len(bodies[parent])
            rc[rnd][side(parent) * 5 + 1] += 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            S[(wnd(rnd), side(parent), min(Lb, 20), min(len(bodies[child]), 10), int(parent == queens[side(parent)]))] += 1
            if turn is not None and turn['i'] == parent:
                turn['split'] = True
        elif k == 11:
            assert not expected
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            L, h, s = len(b), b[0], side(i)
            mates = [(gap(h, bb[0]), len(bb)) for z, bb in bodies.items() if z != i and side(z) == s]
            foes = [(gap(h, bb[0]), len(bb)) for z, bb in bodies.items() if side(z) != s]
            d = dict(r=rnd, s=s, i=i, L=L, c=CAUSE[reason], q=int(i == queens[s]),
                     top=int(L == max(len(bb) for z, bb in bodies.items() if side(z) == s)),
                     o5=sum(1 for g, _ in mates if g <= 5), e5=sum(1 for g, _ in foes if g <= 5),
                     z=zone(h, s), xy=list(h), na=len(mates) + 1, nf=len(foes), eat=[0, 0], eat5=[0, 0],
                     drop=(L + 1) // 2, act=int(i == actor))
            if reason in (0, 1, 2):
                d['free'] = free_sides(h)
            if reason == 2 and i == actor and used < len(dirs):
                c = dest(h, dirs[used])
                owners = [z for z, bb in bodies.items() if z != i and c in bb]
                if len(owners) == 1:
                    d['hit'] = 'mate' if side(owners[0]) == s else 'enemy'
                    d['hitq'] = int(owners[0] in queens)
                    d['hitL'] = len(bodies[owners[0]])
            if reason == 4:
                d['c'] = (act or 'no action') if i == actor else 'no action'
                d['free'] = free_sides(h)
            if i == actor and turn is not None:
                d['L0'] = turn['L0']
                d['steps'] = used + (1 if reason in (0, 1, 2, 3) else 0)
                d['ate'] = turn['eaten']
                turn['paid'] = turn['L0'] + turn['eaten'] - L
            if reason == 3:
                if i != actor:
                    victim = d
                    d['role'] = 'hit'
                    ab = bodies[actor]
                    d['m'] = dict(i=actor, s=side(actor), L=len(ab), L0=turn['L0'], steps=used + 1, ate=turn['eaten'],
                                  paid=turn['L0'] + turn['eaten'] - len(ab),
                                  q=int(actor == queens[side(actor)]), d0=gap(turn['h0'], h), z=zone(h, side(actor)))
                    d['cross'] = int(side(actor) != s)
                    if d['cross']:
                        rec = last.get(i)
                        row = [rnd, s, L, d['q'], d['top'], used + 1, turn['L0'], d['m']['paid'], turn['eaten']]
                        if rec is None:
                            row += ['new']
                        elif rec.get('long'):
                            row += ['long']
                        elif actor not in rec['ids']:
                            row += ['unseen', int(rec['t1']), int(rec['tR']), int(rec['altR']), int(rec['ate']), int(rec['trader']), rec['moved'], int(rec['split'])]
                        else:
                            parts, Lz, dist, rt = rec['ids'][actor]
                            row += ['seen', int(rec['t1']), int(rec['tR']), int(rec['altR']), int(rec['ate']), int(rec['trader']), rec['moved'], int(rec['split']),
                                    parts, Lz, dist, rt, int(rec['altS']), int(rec['tS'])]
                        rams.append(row)
                        if rec is not None and rec.get('choice'):
                            expo[(s, 'Q' if d['q'] else 'S', 'by choice, rammed before the next turn')] += 1
                        if rec is not None and rec.get('choiceS'):
                            expo[(s, 'Q' if d['q'] else 'S', 'parts-1 by choice, rammed before the next turn')] += 1
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
            last.pop(i, None)
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
    lastr = max(snap)
    ends = [sorted((len(b) for i, b in bodies.items() if side(i) == s), reverse=True)[:6] for s in (0, 1)]
    return dict(src=label, gid=j['id'], map=j['mapName'], W=W, H=H, cells=cells,
                layout=hashlib.md5(text.encode()).hexdigest()[:10], start_len=start_len,
                opp=j['team' + 'AB'[1 - own] + 'Name'], opp_id=j['team' + 'AB'[1 - own] + 'Id'],
                result='draw' if winner is None else 'win' if winner == own else 'loss', last=lastr,
                end_reason=fin.u16(2), final=snap[lastr], ends=ends,
                snap=[snap.get(r, None) for r in range(lastr + 1)], deaths=deaths, samples=samples, rams=rams,
                rc=[[r] + v for r, v in sorted(rc.items())],
                T=[list(key) + [n] for key, n in sorted(T.items())],
                E=[list(key) + [n] for key, n in sorted(E.items())],
                S=[list(key) + [n] for key, n in sorted(S.items())],
                MV=[list(key) + [n] for key, n in sorted(MV.items())],
                contact=[list(key) + [n] for key, n in sorted(contact.items())],
                expo=[list(key) + [n] for key, n in sorted(expo.items())])


def main():
    src, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else None
    todo = [t for n, t in enumerate(jobs(src)) if n % shards == shard]
    name = 'wq_scan-test.jsonl'
    if limit is None:
        if src == 'O' and shard == 0:
            name = 'wq_scan-O0.jsonl'
        elif src == 'O':
            name = 'wq_scan-O1.jsonl'
        elif src == 'L' and shard == 0:
            name = 'wq_scan-L0.jsonl'
        elif src == 'L':
            name = 'wq_scan-L1.jsonl'
        elif shard == 0:
            name = 'wq_scan-R0.jsonl'
        else:
            name = 'wq_scan-R1.jsonl'
    else:
        todo = todo[:limit]
    with open(OUT + name, 'w') as f:
        for n, (label, path, j, team) in enumerate(todo):
            f.write(json.dumps(scan(label, path, j, team), separators=(',', ':')) + '\n')
            f.flush()
            if n % 10 == 9:
                print(src, shard, n + 1, len(todo), flush=True)
    print('done', src, shard, len(todo))


main()
