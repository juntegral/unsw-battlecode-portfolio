"""Scratch (diag-bigmap): every cross-team ram on a dragon of 8 or more, seen from the victim's last own turn. The
rammer already stood on its start tile then. Was its head in the victim's 7 by 7 view, how many path steps from the
tile the victim ended on, was that inside the reach the bot gives it (visible parts, 2 to 6, +2 for a victim of 15+;
main.cpp 2510-2512) and inside its real reach (ceil(L/4) + L - 2), did a free neighbouring tile outside every such
reach exist, how many free neighbours the victim had.
Usage: python3 data/analysis/ladder/dossier/work/bm_big.py scan <O|L|R> | agg <O|L|R>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
WORK = Path('data/analysis/ladder/dossier/work')
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
MINL = 8


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
            out.append((src, rp, json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text()), team))
        out.sort(key=lambda t: t[2]['id'])
    return out


def scan(label, path, j, team):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    cells = W * H
    if cells <= 1200:
        return None
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

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

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
    turns = Counter()
    pearls = set()
    rnd, actor = -1, None
    cur = None
    used = 0
    L0 = 0
    h0 = None

    def close():
        nonlocal cur
        if cur is None:
            return
        i = cur['i']
        if i in bodies:
            p1 = bodies[i][0]
            foes = {}
            for z, parts, Lr, m, pos in cur['foes']:
                rc = max(2, min(6, parts + (2 if cur['L'] >= 15 else 0)))
                rt = (Lr + 3) // 4 + Lr - 2
                foes[z] = [parts, Lr, m.get(p1, 9), rc, rt, m.get(cur['h'], 9)]
            exposed = any(v[2] <= v[3] for v in foes.values())
            alt = [n for n in cur['cand'] if not any(m.get(n, 9) <= max(2, min(6, parts + (2 if cur['L'] >= 15 else 0))) for z, parts, Lr, m, pos in cur['foes'])]
            alt_t = [n for n in cur['cand'] if not any(m.get(n, 9) <= (Lr + 3) // 4 + Lr - 2 for z, parts, Lr, m, pos in cur['foes'])]
            last[i] = dict(r=rnd, foes=foes, ncand=len(cur['cand']), alt=len(alt), alt_t=len(alt_t), exposed=exposed, steps=used, ate=cur['ate'], h=list(cur['h']), p1=list(p1), L=cur['L'], near=cur['near'])
            s = cur['s']
            if cur['foes']:
                turns[(s, 'turns of an 8+ with an enemy head in view')] += 1
                if exposed:
                    turns[(s, 'ends inside a code reach')] += 1
                    if alt:
                        turns[(s, 'ends inside a code reach though a free tile outside existed')] += 1
                    last[i]['flag'] = 1
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
            b = bodies[actor]
            L0 = len(b)
            h0 = b[0]
            s = side(actor)
            last.pop(actor, None)
            if len(b) >= MINL:
                h = b[0]
                occ = set()
                for bb in bodies.values():
                    occ.update(bb)
                foes = []
                near = {}
                for z, bb in bodies.items():
                    if side(z) != s:
                        g = gap(h, bb[0])
                        if g <= 8:
                            near[z] = [list(bb[0]), len(bb), int(inview(h, bb[0]))]
                        if inview(h, bb[0]):
                            parts = sum(1 for c in bb if inview(h, c))
                            foes.append((z, parts, len(bb), reach_map(bb[0], occ - {bb[0], h}, 7), bb[0]))
                cand = [n for n in neighbours(h) if n not in occ]
                cur = dict(i=actor, s=s, L=len(b), h=h, foes=foes, cand=cand, ate=0, near=near)
            else:
                cur = None
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
                if cur is not None:
                    cur['ate'] += 1
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
            last.pop(child, None)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if reason == 3 and i != actor and side(i) != side(actor) and len(bodies[i]) >= MINL:
                rec = last.get(i)
                Lv = len(bodies[i])
                top = int(Lv == max(len(bb) for z, bb in bodies.items() if side(z) == side(i)))
                steps = used + 1
                row = dict(r=rnd, vs=side(i), Lv=Lv, top=top, q=int(i in queens), Lr=L0, steps=steps, d0=gap(h0, bodies[i][0]), vh=list(bodies[i][0]), rh=list(h0))
                if rec is None:
                    row['c'] = 'no own turn since'
                else:
                    row.update(vr=rec['r'], ncand=rec['ncand'], alt=rec['alt'], alt_t=rec['alt_t'], vsteps=rec['steps'], vate=rec['ate'], h=rec['h'])
                    f = rec['foes'].get(actor)
                    if f is None:
                        nr = rec['near'].get(actor)
                        row['c'] = 'rammer out of view' if nr is not None else 'rammer more than 8 tiles off'
                        if nr is not None:
                            row['rpos'] = nr[0]
                    else:
                        row.update(parts=f[0], dend=f[2], rc=f[3], rt=f[4], dstart=f[5])
                        if f[2] > f[3]:
                            row['c'] = 'seen, ended outside the code reach'
                        elif rec['alt']:
                            row['c'] = 'seen, ended inside the code reach, a free tile outside existed'
                        elif rec['ncand'] == 0:
                            row['c'] = 'seen, no free tile at all'
                        else:
                            row['c'] = 'seen, every free tile inside a code reach'
                rams.append(row)
            bodies.pop(i)
            last.pop(i, None)
    close()
    arm = 'MAIN' if label.startswith('agg7-m') else 'B7' if label.startswith('agg7-b') else 'B7Q' if label.startswith('agg8-q') else label
    return dict(gid=j['id'], arm=arm, map=j['mapName'], cells=cells, opp=j['team' + 'AB'[1 - own] + 'Name'], rams=rams, turns=[[s, k, v] for (s, k), v in turns.items()])


def do_scan():
    src = sys.argv[2]
    todo = jobs(src)
    name = 'bm_big-O.jsonl'
    if src == 'L':
        name = 'bm_big-L.jsonl'
    elif src == 'R':
        name = 'bm_big-R.jsonl'
    n = 0
    with open(OUT + name, 'w') as f:
        for k, (label, path, j, team) in enumerate(todo):
            g = scan(label, path, j, team)
            if g is not None:
                f.write(json.dumps(g, separators=(',', ':')) + '\n')
                n += 1
            if k % 40 == 39:
                print(src, k + 1, len(todo), n, flush=True)
    print('done', src, len(todo), n)


def do_agg():
    src = sys.argv[2]
    rows = [json.loads(x) for x in (WORK / ('bm_big-' + src + '.jsonl')).read_text().splitlines()]
    sets = [('ALL', rows)]
    if src == 'O':
        sets = [('MAIN', [g for g in rows if g['arm'] == 'MAIN']), ('B7+B7Q', [g for g in rows if g['arm'] != 'MAIN'])]
    for name, gs in sets:
        n = len(gs)
        print()
        print('=====', name, n, 'games')
        for s, nm in ((0, 'victim ours'), (1, 'victim theirs')):
            for lo, hi in ((8, 999), (10, 999), (15, 999)):
                v = [r for g in gs for r in g['rams'] if r['vs'] == s and lo <= r['Lv'] <= hi]
                if not v:
                    continue
                c = Counter(r['c'] for r in v)
                print('%s, length %d+: %d (%.2f a game), the longest of its side %d' % (nm, lo, len(v), len(v) / n, sum(r['top'] for r in v)))
                for k, x in c.most_common():
                    sub = [r for r in v if r['c'] == k]
                    extra = ''
                    if k.startswith('seen'):
                        extra = '; rammer length %s; path steps from the end tile %s; code reach %s; real reach %s; free tiles the victim had %s; with a tile outside every real reach %d' % (
                            sorted(Counter(min(r['Lr'], 6) for r in sub).items()), sorted(Counter(r['dend'] for r in sub).items()), sorted(Counter(r['rc'] for r in sub).items()), sorted(Counter(min(r['rt'], 7) for r in sub).items()), sorted(Counter(r['ncand'] for r in sub).items()), sum(1 for r in sub if r['alt_t']))
                    print('    %-62s %3d (%.2f)%s' % (k, x, x / len(v), extra))
        for s, nm in ((0, 'ours'), (1, 'theirs')):
            t = Counter()
            for g in gs:
                for sd, k, x in g['turns']:
                    if sd == s:
                        t[k] += x
            print(nm, 'a game:', '; '.join('%s %.1f' % (k, x / n) for k, x in t.most_common()))


def do_list():
    src = sys.argv[2]
    rows = [json.loads(x) for x in (WORK / ('bm_big-' + src + '.jsonl')).read_text().splitlines()]
    for g in rows:
        for r in g['rams']:
            if r['vs'] == 0 and r['Lv'] >= int(sys.argv[3]) and g['arm'] != 'MAIN':
                print(g['gid'], g['arm'], g['map'][:8], 'r%d' % r['r'], 'victim L%d%s at %s (turn start %s, steps %s, free tiles %s, outside code reach %s)' % (r['Lv'], 'T' if r['top'] else '', r['vh'], r.get('h'), r.get('vsteps'), r.get('ncand'), r.get('alt')), 'rammer L%d from %s, %d steps' % (r['Lr'], r['rh'], r['steps']), '|', r['c'], 'parts %s path %s code %s real %s' % (r.get('parts'), r.get('dend'), r.get('rc'), r.get('rt')))


if sys.argv[1] == 'scan':
    do_scan()
elif sys.argv[1] == 'agg':
    do_agg()
else:
    do_list()
