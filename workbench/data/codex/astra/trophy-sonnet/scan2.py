"""Scratch (diag-one1): the full length ledger of both sides, every death with who ate its pearls, every paid turn,
every split, a snapshot every 25 rounds. One json row a game.
Usage (from the repo root): python3 -B data/analysis/ladder/dossier/work/o1_scan.py <set> [limit]
sets: w1 (one1 v WHQ), d1 (one1 v dev test 1), live (ranked), v62a (nc62-whq1-old), v62b (agg8-q1-new WHQ games)"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
SM = Path('data/online/smoke')


def jobs(name):
    out, seen = [], set()
    if name == 'live':
        skip = set()
        for f in ('one1-w1-old', 'one1-d1-old'):
            skip |= {int(p.stem[5:]) for p in (SM / f).glob('game-*.json')}
        folders = sorted(Path('data/online/live-one1').glob('b*'))
    else:
        skip = set()
        folders = [SM / dict(w1='one1-w1-old', d1='one1-d1-old', v62a='nc62-whq1-old', v62b='agg8-q1-new', o2='one2-w1-old', o3='one3-w1-old', o3d='one3-d1-old', o4='one4-w1-old', o4d='one4-d1-old')[name]]
    for folder in folders:
        for mp in sorted(folder.glob('game-*.json')):
            j = json.loads(mp.read_text())
            rp = folder / ('M%d.replay' % j['id'])
            if not rp.exists() or j['id'] in skip or j['id'] in seen:
                continue
            if 1119 not in (j['teamAId'], j['teamBId']):
                continue
            opp = j['teamBName'] if j['teamAId'] == 1119 else j['teamAName']
            if name == 'v62b' and 'Quiz' not in opp:
                continue
            seen.add(j['id'])
            out.append((name, rp, j))
    return out


def scan(label, path, j, team=1119):
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

    def total(s):
        return sum(len(b) for i, b in bodies.items() if side(i) == s)

    def snapshot():
        row = []
        for s in (0, 1):
            ls = sorted((len(b) for i, b in bodies.items() if side(i) == s), reverse=True)
            row.append([len(ls), sum(ls), ls[0] if ls else 0, len(bodies.get(queens[s], ())),
                        sum(1 for x in ls if x == 2), sum(1 for x in ls if x == 3), sum(1 for x in ls if x == 4),
                        sum(1 for x in ls if 5 <= x <= 9), sum(1 for x in ls if x >= 10),
                        sum(x for x in ls if x >= 10), ls[1] if len(ls) > 1 else 0])
        return row

    deaths, eats, paids, splits, snaps = [], [], [], [], {}
    xings = []
    present = {}
    born = {}
    rnd, actor, dirs, used = -1, None, [], 0
    expected = 0
    last_death = None
    victim_kind = None
    turn = None
    nat = 0

    def close_turn():
        nonlocal turn
        if turn is None:
            return
        s = turn['s']
        T1 = total(s)
        paid = turn['T0'] + turn['e'] - turn['D'] - T1
        assert paid >= 0, (j['id'], rnd, turn, T1)
        if paid:
            paids.append([turn['r'], s, turn['L0'], paid, turn['e'], turn['ram'], int(turn['i'] == queens[s]), turn['died']])
        turn = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close_turn()
            if rnd >= 0:
                snaps[rnd] = snapshot()
            rnd, actor = p.i32(0), None
        elif k == 1:
            close_turn()
            actor, dirs, used = p.i32(0), [], 0
            victim_kind = None
            s = side(actor)
            turn = dict(i=actor, r=rnd, s=s, L0=len(bodies[actor]), T0=total(s), e=0, D=0, ram=0, died=0, h0=bodies[actor][0])
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
                    nat += 1
            else:
                rec = present.pop(c)
                s = side(actor)
                turn['e'] += 1
                t = top_of(s)
                role = 'q' if actor == queens[s] else 't' if (actor == t and turn['L0'] >= 5) else 'o'
                origin = 'n' if rec is None else ('own' if rec[1] == s else 'foe')
                eats.append([rnd, s, role, origin, rec[4] if rec is not None else '', turn['L0']])
                if rec is not None:
                    rec[10 + (0 if rec[1] == s else 1)] += 1
                    if rec[1] == s and role != 'o':
                        rec[12] += 1
                    if rnd - rec[0] <= 10:
                        rec[13 + (0 if rec[1] == s else 1)] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                dx = abs(b[0][0] - hd[0]); dy = abs(b[0][1] - hd[1])
                if min(dx, W - dx) + min(dy, H - dy) != 1:
                    xings.append([rnd, side(i), i, int(i == queens[side(i)]), len(b)])
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            assert b[-1] == tl
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            Lb = len(bodies[parent])
            sp = side(parent)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            born[parent] = rnd
            born[child] = rnd
            splits.append([rnd, sp, Lb, len(bodies[parent]), len(bodies[child]), int(parent == queens[sp])])
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            L, h, s = len(b), b[0], side(i)
            t = top_of(s)
            extra = None
            if reason == 3:
                if i != actor:
                    kd = 'rammed' if side(actor) != s else 'mate head'
                    victim_kind = kd
                    if kd == 'rammed':
                        extra = [turn['L0'], used + 1, turn['L0'] + turn['e'] - len(bodies[actor]), gap(turn['h0'], h),
                                 int(actor == queens[side(actor)])]
                else:
                    kd = 'rams' if victim_kind == 'rammed' else 'mate head'
                    extra = [turn['L0'], used + 1, turn['L0'] + turn['e'] - L]
                    if kd == 'rams':
                        turn['ram'] = 1
            elif reason == 2:
                kd = 'foe body'
                if i == actor and used < len(dirs):
                    c = dest(h, dirs[used])
                    owners = [z for z, bb in bodies.items() if z != i and c in bb]
                    if len(owners) == 1 and side(owners[0]) == s:
                        kd = 'mate body'
            elif reason == 0:
                kd = 'wall'
            elif reason == 1:
                kd = 'own body'
            else:
                kd = 'stop'
            fr = free_sides(h)
            mates5 = sum(1 for z, bb in bodies.items() if z != i and side(z) == s and gap(h, bb[0]) <= 5)
            foes5 = sum(1 for z, bb in bodies.items() if side(z) != s and gap(h, bb[0]) <= 5)
            td = gap(h, bodies[t][0]) if t is not None and t != i else -1
            tL = len(bodies[t]) if t is not None else 0
            #      0    1  2  3      4   5   6                 7                              8       9
            rec = [rnd, s, L, i == t and 1 or 0, kd, fr, int(i == queens[s]), rnd - born[i] if i in born else -1, mates5, foes5,
                   0, 0, 0, 0, 0, (L + 1) // 2, td, tL, extra, int(i == actor), list(h)]
            #      10 own eaten, 11 foe eaten, 12 own eaten by queen/top, 13 own in 10 rounds, 14 foe in 10 rounds, 15 dropped
            deaths.append(rec)
            if turn is not None and side(i) == turn['s']:
                turn['D'] += L
                if i == turn['i']:
                    turn['died'] = 1
            last_death = rec
            expected = (L + 1) // 2
            bodies.pop(i)
    close_turn()
    snaps[rnd] = snapshot()
    fin = root.pointer(4)
    winner = fin.u16(6) if fin.u16(4) == 1 else None
    ends = snapshot()
    if winner is not None and (ends[0][0] == 0 or ends[1][0] == 0):
        how = 'elim'
    elif ends[0][3] != ends[1][3]:
        how = 'queen'
    elif ends[0][2] != ends[1][2]:
        how = 'longest'
    else:
        how = 'total'
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=W * H, opp=j['team' + 'AB'[1 - own] + 'Name'],
                result='draw' if winner is None else 'win' if winner == own else 'loss', how=how, last=rnd, ends=ends,
                snaps={str(r): v for r, v in snaps.items() if r % 25 == 0 or r == rnd}, deaths=deaths, eats=eats,
                paids=paids, splits=splits, nat=nat, xings=xings)


def main():
    name = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    todo = jobs(name)
    out = OUT + ('o1_scan-test.jsonl' if limit else 'o1_scan-%s.jsonl' % name)
    if limit:
        todo = todo[:limit]
    with open(out, 'w') as f:
        for n, (label, path, j) in enumerate(todo):
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
            f.flush()
    print('done', name, len(todo))


if __name__ == '__main__':
    main()
