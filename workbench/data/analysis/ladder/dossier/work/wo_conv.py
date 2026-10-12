"""Scratch (diag-wipeout): rounds 0-40 of games on layouts of 1200 cells or fewer where each side starts with two
dragons of total length 6 or less. For every turn of both sides: path distance (open edges and portals, bodies block,
depth 14) from the head to the nearest pearl at the start of the turn, and what the turn did (ate, ended nearer,
same, farther, died). Also whether the dragon could split and did. Printed by outcome class.
Usage: python3 data/analysis/ladder/dossier/work/wo_conv.py <O|L|R> [nostripes] [last round, default 40]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path

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
            if r['relation'] != 'us' or r['cells'] > 1200:
                continue
            st = r['all_starting_dragons']['us']
            if len(st) != 2 or sum(d['length'] for d in st) > 6:
                continue
            rp = Path(r['replay'])
            out.append((rp, json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text()), team))
    return out


def scan(path, j, team, last):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    if W * H > 1200:
        return None
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 0 if teams[i] == own else 1
    if sum(1 for i in bodies if side(i) == 0) != 2 or sum(len(b) for i, b in bodies.items() if side(i) == 0) > 6:
        return None
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
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

    pearls = set()

    def dist(h, occ):
        if not pearls:
            return None
        seen = {h}
        q = deque([(h, 0)])
        while q:
            c, d = q.popleft()
            if d >= 14:
                continue
            for n in neighbours(c):
                if n in seen or n in occ:
                    continue
                if n in pearls:
                    return d + 1
                seen.add(n)
                q.append((n, d + 1))
        return 99

    def occupied():
        occ = set()
        for bb in bodies.values():
            occ.update(bb)
        return occ

    rows = []
    rnd, actor = -1, None
    cur = None

    def close():
        nonlocal cur
        if cur is None:
            return
        i = cur['i']
        if i not in bodies:
            oc = 'died'
        elif cur['ate']:
            oc = 'ate'
        elif cur['d0'] is None:
            oc = 'nopearl'
        else:
            d1 = dist(bodies[i][0], occupied() - {bodies[i][0]})
            oc = 'nearer' if d1 is not None and d1 < cur['d0'] else 'same' if d1 == cur['d0'] else 'farther'
        rows.append((rnd, cur['s'], cur['L'], cur['d0'], oc, cur['split'], cur['n']))
        cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            rnd, actor = p.i32(0), None
            if rnd > last:
                break
        elif k == 1:
            close()
            actor = p.i32(0)
            b = bodies[actor]
            occ = occupied()
            cur = dict(i=actor, s=side(actor), L=len(b), d0=dist(b[0], occ), ate=False, split=False,
                       n=sum(1 for z in bodies if side(z) == side(actor)))
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
                if cur is not None:
                    cur['ate'] = True
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if cur is not None:
                cur['split'] = True
        elif k == 11:
            bodies.pop(p.i32(0))
    close()
    return rows


def band(d):
    return 'none on map' if d is None else '1' if d == 1 else '2' if d == 2 else '3-4' if d <= 4 else '5-8' if d <= 8 else '9-14' if d <= 14 else 'beyond 14'


def main():
    src = sys.argv[1]
    nostripes = len(sys.argv) > 2 and sys.argv[2] == 'nostripes'
    last = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    cls = {}
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            cls[g['gid']] = 'OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST'
    tab = defaultdict(Counter)
    games = Counter()
    for path, j, team in jobs(src):
        if nostripes and j['mapName'] == 'Stripes':
            continue
        rows = scan(path, j, team, last)
        if rows is None:
            continue
        c = cls[j['id']]
        games[c] += 1
        for rnd, s, L, d0, oc, split, n in rows:
            tab[(c, s, band(d0))][oc] += 1
            tab[(c, s, 'ALL')][oc] += 1
            if L >= 4:
                tab[(c, s, 'could split')]['did' if split else 'did not'] += 1
    print(src, 'games', dict(games), 'rounds 0-%d' % last, 'no Stripes' if nostripes else '')
    for c in ('OUT', 'KILL', 'REST'):
        for b in ('ALL', '1', '2', '3-4', '5-8', '9-14', 'beyond 14', 'none on map'):
            line = '%-4s path to nearest pearl %-11s' % (c, b)
            for s, nm in ((0, 'us'), (1, 'them')):
                t = tab[(c, s, b)]
                n = sum(t.values())
                line += ' | %s turns %5d (%.1f a game): ate %.0f%% nearer %.0f%% same %.0f%% farther %.0f%% died %.1f%%' % (
                    nm, n, n / max(games[c], 1), 100 * t['ate'] / max(n, 1), 100 * t['nearer'] / max(n, 1), 100 * t['same'] / max(n, 1),
                    100 * t['farther'] / max(n, 1), 100 * t['died'] / max(n, 1))
            print(line)
        for s, nm in ((0, 'us'), (1, 'them')):
            t = tab[(c, s, 'could split')]
            print('%-4s %s turns at length 4 or more: %d, split on %.0f%%' % (c, nm, sum(t.values()), 100 * t['did'] / max(sum(t.values()), 1)))


main()
