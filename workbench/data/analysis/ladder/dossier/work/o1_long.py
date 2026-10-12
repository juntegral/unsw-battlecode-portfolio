"""Scratch (diag-one1, job F): dragons of 20+ after round 300, both sides. Every turn of such a dragon: steps moved,
mates and enemy heads near, and (stored for its last turn) what the enemy heads in its 7 by 7 could reach and whether a
tile out of their reach was open to it. Every ram on such a dragon with the rammer's last three turn starts.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_long.py <set>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from o1_scan import jobs, OUT, STEP
MINL, R0 = 20, 300


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
    side = lambda i: 0 if teams[i] == own else 1
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]

    def dest(h, d):
        x, y = h
        e = edge_id(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 1:
            return None
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            prow, px = divmod(partner, W + 1)
            py = prow // 2
            return ((px - (d == 3)) % W, (py - (d == 0)) % H)
        dx, dy = STEP[d]
        return ((x + dx) % W, (y + dy) % H)

    def gap(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def inview(h, c):
        dx = (c[0] - h[0] + W // 2) % W - W // 2
        dy = (c[1] - h[1] + H // 2) % H - H // 2
        return abs(dx) <= 3 and abs(dy) <= 3

    def flood(h, R, occ):
        seen = {h: 0}
        qu = deque([h])
        while qu:
            c = qu.popleft()
            if seen[c] >= R:
                continue
            for d in range(4):
                n = dest(c, d)
                if n is None or n in seen or n in occ:
                    continue
                seen[n] = seen[c] + 1
                qu.append(n)
        return seen

    def occupied():
        occ = set()
        for bb in bodies.values():
            occ.update(bb)
        return occ

    T = [Counter(), Counter()]
    rams = []
    hist = defaultdict(lambda: deque(maxlen=3))     # turn-start heads of every dragon
    info = {}                                       # last-turn record of long dragons
    rnd, actor, used, cur = -1, None, 0, None
    L0 = 0
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1) and cur is not None:
            i = cur['i']
            if i in bodies:
                cur['end'] = bodies[i][0]
                cur['steps'] = cur['used']
                # where it ended, by the picture at its turn start
                e = cur['end']
                cur['end_free'] = int(any(f.get(e, 99) <= fr for f, fr, full in cur['reach']))
                cur['end_pay1'] = int(any(f.get(e, 99) <= fr + 1 for f, fr, full in cur['reach']))
                cur['end_full'] = int(any(f.get(e, 99) <= full for f, fr, full in cur['reach']))
                s = cur['s']
                T[s]['turns'] += 1
                T[s]['still'] += cur['used'] == 0
                T[s]['steps'] += cur['used']
                T[s]['mates5'] += cur['mates5']
                T[s]['foe5'] += cur['foe5'] > 0
                T[s]['foe3'] += cur['foe3'] > 0
                T[s]['foe in view'] += len(cur['reach']) > 0
                T[s]['ends in free+1 reach of a head in view'] += cur['end_pay1']
                if cur['q']:
                    T[s]['queen turns'] += 1
                del cur['reach']
                info[i] = cur
            cur = None
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor, used = p.i32(0), 0
            b = bodies[actor]
            L0 = len(b)
            hist[actor].append(b[0])
            s = side(actor)
            if rnd > R0 and L0 >= MINL:
                h = b[0]
                occ = occupied()
                reach = []
                foes = []
                for z, bb in bodies.items():
                    if side(z) == s or not inview(h, bb[0]):
                        continue
                    Lz = len(bb)
                    fr = (Lz + 3) // 4
                    full = min(6, fr + max(0, Lz - 2))
                    reach.append((flood(bb[0], full, occ - {bb[0], h}), fr, full))
                    foes.append([z, Lz, sum(1 for c in bb if inview(h, c))])
                free = (L0 + 3) // 4
                mine = flood(h, min(free, 4), occ - {h})
                cand = [c for c in mine if c != h]
                first = [c for c in cand if mine[c] == 1]
                def clean(c, mode):
                    for f, fr, full in reach:
                        lim = fr + 1 if mode == 1 else full
                        if f.get(c, 99) <= lim:
                            return False
                    return True
                cur = dict(i=actor, s=s, r=rnd, L=L0, q=int(actor == queens[s]), start=h, used=0, split=0, reach=reach, foes=foes,
                           open1=len(first), cand=len(cand),
                           clean1_pay1=sum(1 for c in first if clean(c, 1)), clean1_full=sum(1 for c in first if clean(c, 2)),
                           clean_pay1=sum(1 for c in cand if clean(c, 1)), clean_full=sum(1 for c in cand if clean(c, 2)),
                           mates5=sum(1 for z, bb in bodies.items() if z != actor and side(z) == s and gap(h, bb[0]) <= 5),
                           foe5=sum(1 for z, bb in bodies.items() if side(z) != s and gap(h, bb[0]) <= 5),
                           foe3=sum(1 for z, bb in bodies.items() if side(z) != s and gap(h, bb[0]) <= 3))
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
                    if cur is not None:
                        cur['used'] = used
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if cur is not None and cur['i'] == parent:
                cur['split'] = 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            L, s = len(b), side(i)
            if rnd > R0 and L >= MINL:
                T[s]['deaths'] += 1
                T[s]['death ' + ('rammed' if reason == 3 and i != actor and side(actor) != s else 'as rammer' if reason == 3 and i == actor else 'other')] += 1
            if reason == 3 and i != actor and side(actor) != s and rnd > R0 and L >= MINL:
                vh = b[0]
                rh = list(hist[actor])
                occ = occupied()
                fl = flood(vh, 9, occ - {vh, rh[-1]})
                lastv = info.get(i)
                mates = []
                for z, bb in bodies.items():
                    if z != i and side(z) == s and gap(vh, bb[0]) <= 5:
                        Lz = len(bb)
                        R = min(4, (Lz + 3) // 4 + Lz - 2)
                        dz = flood(bb[0], 6, occ - {bb[0], rh[-1]}).get(rh[-1], 99)
                        mates.append([Lz, gap(vh, bb[0]), dz, int(Lz <= 4 and dz <= R)])
                rec = dict(r=rnd, s=s, q=int(i == queens[s]), L=L, top=int(L == max(len(bb) for z, bb in bodies.items() if side(z) == s)),
                           rammer_L=L0, rammer_steps=used + 1, rammer_free=(L0 + 3) // 4, rammer_q=int(actor == queens[side(actor)]),
                           d1=fl.get(rh[-1], 99), in_view1=int(inview(vh, rh[-1])),
                           d2=fl.get(rh[-2], 99) if len(rh) >= 2 else -1, in_view2=int(inview(vh, rh[-2])) if len(rh) >= 2 else -1,
                           mates=mates, last=None, prev_steps=None)
                if lastv is not None:
                    rec['last'] = {k2: lastv[k2] for k2 in ('r', 'L', 'used', 'split', 'open1', 'cand', 'clean1_pay1', 'clean1_full', 'clean_pay1', 'clean_full', 'end_free', 'end_pay1', 'end_full', 'mates5', 'foe5', 'foe3')}
                    rec['last']['foes'] = lastv['foes']
                    rec['last']['rammer_seen'] = int(any(f[0] == actor for f in lastv['foes']))
                    rec['last']['rammer_parts'] = next((f[2] for f in lastv['foes'] if f[0] == actor), 0)
                rams.append(rec)
            info.pop(i, None)
            hist.pop(i, None)
            bodies.pop(i)
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=W * H,
                opp=j['team' + 'AB'[1 - own] + 'Name'], T=[dict(T[0]), dict(T[1])], rams=rams)


if __name__ == '__main__':
    name = sys.argv[1]
    todo = jobs(name)
    with open(OUT + 'o1_long-%s.jsonl' % name, 'w') as f:
        for label, path, j in todo:
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
    print('done', name, len(todo))
