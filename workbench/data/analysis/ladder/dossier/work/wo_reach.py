"""Scratch (diag-wipeout): every cross-team ram, seen from the victim's last own turn. The rammer already stood on
its start tile then. For a victim of length 4 or less: was the rammer's head in its 7 by 7 view, was the tile it ended
on inside the rammer's paid-sprint reach (parts - 1 steps, parts = rammer segments in the victim's view, under 5) but
not beside it, did a free neighbouring tile outside every such reach exist, was the victim a trader by the bot's count
rule. Also the turns of each side that end on such a tile by choice, and how many are rammed before the next turn.
Usage: python3 .../wo_reach.py scan <O|L|R> <shard> <shards>   |   python3 .../wo_reach.py agg <O|L|R>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
WORK = Path('data/analysis/ladder/dossier/work')
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'sr51-bob1')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


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
                    out.append((rp, j, 1119))
    else:
        path = Path('data/analysis/ladder/dossier') / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            rp = Path(r['replay'])
            out.append((rp, json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text()), team))
        out.sort(key=lambda t: t[1]['id'])
    return out


def scan(path, j, team):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    cells = W * H
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 0 if teams[i] == own else 1
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    nb = {}

    def neighbours(c):
        if c not in nb:
            out = []
            x, y = c
            for d in range(4):
                e = edge_id(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    prow, px = divmod(partner, W + 1)
                    py = prow // 2
                    out.append(((px - (d == 3)) % W, (py - (d == 0)) % H))
                else:
                    out.append(((x + STEP[d][0]) % W, (y + STEP[d][1]) % H))
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

    last = {}
    rams = []
    expo = Counter()
    rnd, actor = -1, None
    cur = None
    used = 0
    L0 = 0
    victim = None

    def close():
        nonlocal cur
        if cur is None:
            return
        i = cur['i']
        if i in bodies:
            p1 = bodies[i][0]
            t1 = any(m.get(p1, 9) <= 1 for _, _, m, _ in cur['foes'])
            tS = any(m.get(p1, 9) <= r for _, _, m, r in cur['foes'])
            alt = [n for n in cur['cand'] if not any(m.get(n, 9) <= r for _, _, m, r in cur['foes'])]
            rec = dict(r=rnd, t1=t1, tS=tS, alt=len(alt) > 0, trader=cur['trader'], ate=cur['ate'], ids=dict((z, p) for z, p, _, _ in cur['foes']), L=cur['L'], q=cur['q'])
            last[i] = rec
            s = cur['s']
            if cur['L'] <= 4 and not cur['q'] and cur['foes']:
                expo[(s, 'short turns with a short enemy head in view')] += 1
                if tS and not t1:
                    expo[(s, 'ends in sprint reach only')] += 1
                    if alt and not cur['trader'] and not cur['ate']:
                        expo[(s, 'by choice (free tile outside reach, not a trader, did not eat)')] += 1
                        rec['choice'] = True
                elif t1:
                    expo[(s, 'ends beside the head')] += 1
        cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            rnd, actor = p.i32(0), None
        elif k == 1:
            close()
            actor = p.i32(0)
            used = 0
            victim = None
            b = bodies[actor]
            L0 = len(b)
            s = side(actor)
            h = b[0]
            last.pop(actor, None)
            foes_seen = [(z, bb) for z, bb in bodies.items() if side(z) != s and inview(h, bb[0])]
            if foes_seen and len(b) <= 4:
                occ = set()
                for bb in bodies.values():
                    occ.update(bb)
                foes = []
                worth = False
                for z, bb in foes_seen:
                    parts = sum(1 for c in bb if inview(h, c))
                    if parts < 5:
                        r = max(1, parts - 1)
                        foes.append((z, parts, reach_map(bb[0], occ - {bb[0]}, 3), r))
                    worth = worth or (parts >= len(b) if cells <= 1200 else parts >= max(5, len(b) + 2))
                allies = sum(1 for z, bb in bodies.items() if side(z) == s and z != actor and inview(h, bb[0]))
                units = sum(1 for z in bodies if side(z) == s)
                trader = worth and rnd <= 400 and allies + 1 - len(foes_seen) >= 1 and (cells <= 1200 or units >= 8)
                cand = [n for n in neighbours(h) if n not in occ]
                cur = dict(i=actor, s=s, L=len(b), q=actor in queens, foes=foes, cand=cand, trader=trader, ate=False)
            else:
                cur = dict(i=actor, s=s, L=len(b), q=actor in queens, foes=[], cand=[], trader=False, ate=False)
        elif k == 3:
            if not p.u32(0) and cur is not None:
                cur['ate'] = True
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
            if reason == 3 and i != actor:
                victim = i
                if side(i) != side(actor):
                    rec = last.get(i)
                    steps = used + 1
                    Lv = len(bodies[i])
                    if Lv > 4 or i in queens:
                        c = 'victim 5+ or queen'
                    elif steps == 1:
                        c = 'from 1 step'
                    elif rec is None:
                        c = '2+: no own turn since (new child)'
                    elif actor not in rec['ids']:
                        c = '2+: rammer not in view or 5+ parts'
                    elif rec['trader']:
                        c = '2+: victim was a trader'
                    elif steps > max(1, rec['ids'][actor] - 1):
                        c = '2+: beyond parts-1 steps'
                    elif rec['ate']:
                        c = '2+: ate on that turn'
                    elif not rec['alt']:
                        c = '2+: no free tile outside reach'
                    else:
                        c = '2+: ADDRESSED'
                    rams.append([rnd, side(i), Lv, steps, L0, c])
                    if rec is not None and rec.get('choice'):
                        expo[(side(i), 'by choice, rammed before the next turn')] += 1
            bodies.pop(i)
            last.pop(i, None)
    close()
    return dict(gid=j['id'], cells=cells, rams=rams, expo=[[s, k, v] for (s, k), v in expo.items()])


def do_scan():
    src, shard, shards = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    todo = [t for n, t in enumerate(jobs(src)) if n % shards == shard]
    name = 'wo_reach-O0.jsonl'
    if src == 'L' and shard == 0:
        name = 'wo_reach-L0.jsonl'
    elif src == 'L' and shard == 1:
        name = 'wo_reach-L1.jsonl'
    elif src == 'L':
        name = 'wo_reach-L2.jsonl'
    elif src == 'R' and shard == 0:
        name = 'wo_reach-R0.jsonl'
    elif src == 'R' and shard == 1:
        name = 'wo_reach-R1.jsonl'
    elif src == 'R':
        name = 'wo_reach-R2.jsonl'
    with open(OUT + name, 'w') as f:
        for n, (path, j, team) in enumerate(todo):
            f.write(json.dumps(scan(path, j, team), separators=(',', ':')) + '\n')
            if n % 40 == 39:
                print(src, shard, n + 1, len(todo), flush=True)
    print('done', src, shard, len(todo))


def do_agg():
    src = sys.argv[2]
    win = {}
    klass = {}
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            klass[g['gid']] = 'OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST'
            if g['final'][0] == 0:
                al = [x[0] for x in g['snap']]
                peak = max(al)
                pr = max(r for r, a in enumerate(al) if a == peak)
                hr = next(r for r in range(pr, len(al)) if al[r] * 2 < peak)
                win[g['gid']] = (max(0, hr - 60), hr)
    rows = []
    for p in sorted(WORK.glob('wo_reach-' + src + '[0-9].jsonl')):
        rows += [json.loads(x) for x in p.read_text().splitlines()]
    print(src, 'games', len(rows))
    pops = (('wipe-out windows', lambda g, r: g['gid'] in win and win[g['gid']][0] < r <= win[g['gid']][1]),
            ('all games, all rounds', lambda g, r: True),
            ('1200 cells or fewer, rounds 0-100', lambda g, r: g['cells'] <= 1200 and r <= 100),
            ('above 1200 cells', lambda g, r: g['cells'] > 1200))
    for name, test in pops:
        for s, nm in ((0, 'side 0 is the victim'), (1, 'the opponent is the victim')):
            c = Counter()
            for g in rows:
                for r, vs, Lv, steps, mL0, cl in g['rams']:
                    if vs == s and test(g, r):
                        c[cl] += 1
            n = sum(c.values())
            if n:
                print('%s | %s: rams %d (%.1f a game) | %s' % (name, nm, n, n / len(rows), '; '.join('%s %d (%.0f%%)' % (k, v, 100 * v / n) for k, v in c.most_common())))
    for s, nm in ((0, 'side 0'), (1, 'opponents')):
        e = Counter()
        for g in rows:
            for sd, k, v in g['expo']:
                if sd == s:
                    e[k] += v
        print(nm, 'a game:', '; '.join('%s %.1f' % (k, v / len(rows)) for k, v in e.most_common()))
        a, b = e['by choice (free tile outside reach, not a trader, did not eat)'], e['by choice, rammed before the next turn']
        print('   rammed before the next turn after such a turn: %d of %d (%.1f%%)' % (b, a, 100 * b / max(a, 1)))


if sys.argv[1] == 'scan':
    do_scan()
else:
    do_agg()
