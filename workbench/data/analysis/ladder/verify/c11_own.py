#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier extras 11 for F38: who is the own dragon beside the queen head on a narrow tile? For every stay (any
length) in which a body tile of another dragon of her side lies next to her head through an open side at a turn
start: is that dragon a child she split off, when was it born, how did the stay end. Only games that the x11 shards
flag are read again from the raw replays. Writes f38-1117-own.txt."""
import sys, json
from pathlib import Path
from collections import deque, Counter
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path('../battlecode').resolve()))
import replay
V = Path('data/analysis/ladder/verify')
LADDER = Path('data/online/ladder')
REASON = ['wall', 'own body', 'other dragon body', 'head-on', 'other']
LINES = []


def say(*a):
    s = ' '.join(str(x) for x in a)
    LINES.append(s)
    print(s)


def north_edge(W, x, y):
    return 2 * y * (W + 1) + x


def west_edge(W, x, y):
    return (2 * y + 1) * (W + 1) + x


def edge_of(W, H, x, y, d):
    if d == 0:
        return north_edge(W, x, y)
    if d == 2:
        return north_edge(W, x, (y + 1) % H)
    if d == 3:
        return west_edge(W, x, y)
    return west_edge(W, (x + 1) % W, y)


def fold(W, H, e):
    row, x = divmod(e, W + 1)
    if row % 2 == 0:
        if x == W:
            return None
        return north_edge(W, x, (row // 2) % H)
    return west_edge(W, x % W, row // 2)


def read_layout(text):
    lines = text.splitlines()
    W, H = int(lines[0].split()[1]), int(lines[0].split()[2])
    dragons = []
    edges = {}
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            n = int(q[2])
            dragons.append((int(q[1]), [(int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(n)]))
        elif q[0] == 'EDGE':
            e, kind, pid = int(q[1]), int(q[2]), int(q[3])
            c = fold(W, H, e)
            if c is None:
                continue
            if c in edges and kind <= edges[c][0]:
                continue
            edges[c] = (kind, pid)
    return W, H, dragons, edges


def build_nbrs(W, H, edges):
    pairs = {}
    for e, (kind, pid) in edges.items():
        if kind == 2:
            pairs.setdefault(pid, []).append(e)
    N = W * H
    nbrs = [[] for _ in range(N)]
    open_sides = [0] * N
    for y in range(H):
        for x in range(W):
            u = y * W + x
            for d in range(4):
                e = edge_of(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                open_sides[u] += 1
                if kind == 2:
                    pr = pairs.get(pid, [])
                    if len(pr) != 2:
                        continue
                    pe = pr[0] if pr[1] == e else pr[1]
                    row, px = divmod(pe, W + 1)
                    if row % 2 != (0 if d in (0, 2) else 1):
                        continue
                    py = row // 2
                    if d == 0:
                        v = ((py - 1) % H) * W + px
                    elif d == 3:
                        v = py * W + (px - 1) % W
                    else:
                        v = py * W + px
                else:
                    if d == 0:
                        v = ((y - 1) % H) * W + x
                    elif d == 1:
                        v = y * W + (x + 1) % W
                    elif d == 2:
                        v = ((y + 1) % H) * W + x
                    else:
                        v = y * W + (x - 1) % W
                nbrs[u].append(v)
    return nbrs, open_sides


def process(path, meta):
    root = replay.load(path).root()
    ours = 0 if meta['teamAId'] == 1119 else 1
    W, H, dragons, edges = read_layout(root.text(0))
    nbrs, open_sides = build_nbrs(W, H, edges)
    bodies = {}
    team = {}
    parent = {}
    born = {}
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = 0 if t == ours else 1
    queen = [min(i for i in team if team[i] == 0), min(i for i in team if team[i] == 1)]
    qside = {queen[0]: 0, queen[1]: 1}
    out = []
    stay = [None, None]
    rnd = 0
    actor = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k != 0 and k != 1 and k != 9 and k != 10 and k != 11:
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            actor = None
        elif k == 1:
            actor = p.i32(0)
            s = qside.get(actor)
            if s is None or actor not in bodies:
                continue
            b = bodies[actor]
            u = b[0][1] * W + b[0][0]
            if open_sides[u] <= 2:
                if stay[s] is None:
                    stay[s] = dict(s=s, start=rnd, n=0, beside=[], splits=[], lens=[], death=None, exits=[])
                st = stay[s]
                st['n'] += 1
                st['lens'].append(len(b))
                nb = set(nbrs[u])
                occ = set()
                for z, bz in bodies.items():
                    cells = set(c[1] * W + c[0] for c in bz)
                    hit = cells.intersection(nb)
                    occ |= hit
                    if z == actor or team[z] != s:
                        continue
                    if hit:
                        st['beside'].append([rnd, z, parent.get(z), born.get(z), len(bz)])
                st['exits'].append(len(nb) - len(occ))
            elif stay[s] is not None:
                if stay[s]['beside']:
                    out.append(stay[s])
                stay[s] = None
        elif k == 9:
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            t = replay.point(p.pointer(1))
            b = bodies.get(i)
            if b is None:
                continue
            if b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != t:
                b.pop()
        elif k == 10:
            par, ch = p.i32(0), p.i32(4)
            sd = team.get(par, 0 if p.u16(8) == ours else 1)
            bodies[par] = deque(replay.point(c) for c in p.pointer(0))
            bodies[ch] = deque(replay.point(c) for c in p.pointer(1))
            team[par] = sd
            team[ch] = sd
            parent[ch] = par
            born[ch] = rnd
            s = qside.get(par)
            if s is not None and stay[s] is not None:
                stay[s]['splits'].append(rnd)
        elif k == 11:
            i = p.i32(0)
            s = qside.get(i)
            if s is not None and stay[s] is not None:
                stay[s]['death'] = p.u16(4)
                stay[s]['death_round'] = rnd
                if stay[s]['beside']:
                    out.append(stay[s])
                stay[s] = None
            bodies.pop(i, None)
    for s in (0, 1):
        if stay[s] is not None and stay[s]['beside']:
            out.append(stay[s])
    return out, queen


def main():
    games = []
    for k in range(6):
        for line in (V / ('x11-%d.jsonl' % k)).read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    pick = [g for g in games if g['code'] in ('main', 'v31') and g['map'] not in ('Schooltime', 'Slithery Fight', 'Portals')
            and any(st[6] for st in g['stays'])]
    say('games in the set with a stay that has an own dragon beside the queen head:', len(pick))
    rows = []
    for g in pick:
        folder = LADDER / str(g['battle'])
        meta = json.loads((folder / ('game-%d.json' % g['game'])).read_text())
        out, queen = process(folder / ('M%d.replay' % g['game']), meta)
        for st in out:
            st['game'] = g['game']
            st['code'] = g['code']
            st['map'] = g['map']
            st['queen'] = queen[st['s']]
            rows.append(st)
    for s, lab in ((0, 'ours'), (1, 'theirs')):
        for name, pred in (('all rounds, any length', lambda st: True), ('begun in r101-200, any length', lambda st: 101 <= st['start'] <= 200),
                           ('begun in r101-200, 3 or more turn starts', lambda st: 101 <= st['start'] <= 200 and st['n'] >= 3),
                           ('all rounds, 3 or more turn starts', lambda st: st['n'] >= 3)):
            R = [st for st in rows if st['s'] == s and pred(st)]
            dead = [st for st in R if st['death'] is not None]
            child = [st for st in R if any(x[2] == st['queen'] for x in st['beside'])]
            child_in = [st for st in R if any(x[2] == st['queen'] and x[3] is not None and x[3] >= st['start'] for x in st['beside'])]
            split_in = [st for st in R if st['splits']]
            last_only = [st for st in dead if st['beside'] and min(x[0] for x in st['beside']) == st['death_round']]
            gap = Counter()
            for st in dead:
                gap[st['death_round'] - min(x[0] for x in st['beside'])] += 1
            noexit = [st for st in dead if st['exits'] and st['exits'][-1] == 0]
            say('%s, %s: stays with an own dragon beside her head %d; ended in her death %d %s; the dragon beside her is a child she split off in %d (born during this stay in %d); she split during the stay in %d; among the deaths: the child of this stay in %d, own dragon first beside her in the round she dies in %d, rounds from first beside to death %s; no free tile next to her head at her last turn start in %d; her length at the last turn start %s' % (
                lab, name, len(R), len(dead), dict(Counter(REASON[st['death']] for st in dead)), len(child), len(child_in), len(split_in),
                sum(1 for st in dead if st in child_in), len(last_only), dict(sorted(gap.items())), len(noexit),
                dict(sorted(Counter(st['lens'][-1] for st in dead).items()))))
    say('')
    say('the stays of ours begun in r101-200 with 3 or more turn starts, one line each (game, code, map, start, turn starts, death, lengths, splits, beside rows [round, id, parent, born, length], free exits):')
    for st in rows:
        if st['s'] == 0 and 101 <= st['start'] <= 200 and st['n'] >= 3:
            say('   ', st['game'], st['code'], st['map'], st['start'], st['n'], REASON[st['death']] if st['death'] is not None else 'alive', st['lens'], st['splits'], st['beside'][:4], st['exits'])
    out = open(P + 'f38-1117-own.txt', 'w')
    out.write('\n'.join(LINES) + '\n')
    out.close()


main()
