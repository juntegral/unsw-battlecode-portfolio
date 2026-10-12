#!/usr/bin/env python3
"""Verifier extraction. Own state rebuild from the raw replays (only the byte decoder is shared);
one JSON line per game. Usage: python3 extract.py <shard> <shards>"""
import sys, json, hashlib
from pathlib import Path
from collections import deque, Counter
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path('../battlecode').resolve()))
import replay

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
MAIN = ('18066', '18068', '18504', '18570')
US = 1119
LADDER = Path('data/online/ladder')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
MARKS = (50, 100, 150, 200, 300)


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
    name = None
    dragons = []
    edges = {}
    conflicts = 0
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'MAP_NAME':
            name = ' '.join(q[1:])
        elif q[0] == 'DRAGON':
            n = int(q[2])
            dragons.append((int(q[1]), [(int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(n)]))
        elif q[0] == 'EDGE':
            e, kind, pid = int(q[1]), int(q[2]), int(q[3])
            c = fold(W, H, e)
            if c is None:
                continue
            if c in edges and edges[c] != (kind, pid):
                conflicts += 1
                if kind <= edges[c][0]:
                    continue
            edges[c] = (kind, pid)
    return W, H, name, dragons, edges, conflicts


def build_step(W, H, edges):
    by_pid = {}
    for e, (kind, pid) in edges.items():
        if kind == 2:
            by_pid.setdefault(pid, []).append(e)
    partner = {}
    bad = 0
    for pid, es in by_pid.items():
        if len(es) == 2:
            partner[es[0]] = es[1]
            partner[es[1]] = es[0]
        else:
            bad += 1

    def step(x, y, d):
        e = edge_of(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 1:
            return None
        if kind == 2 and e in partner:
            row, px = divmod(partner[e], W + 1)
            py = row // 2
            flat = row % 2 == 0
            if flat and d == 0:
                return (px, (py - 1) % H)
            if flat and d == 2:
                return (px, py % H)
            if not flat and d == 1:
                return (px % W, py)
            if not flat and d == 3:
                return ((px - 1) % W, py)
            return 'turn'
        return ((x + STEP[d][0]) % W, (y + STEP[d][1]) % H)
    return step, bad, len(by_pid)




def forced(path, meta):
    """Free first steps the queen had when she died by wall (0) or own body (1)."""
    root = replay.load(path).root()
    ours = 0 if meta['teamAId'] == US else 1
    W, H, name, dragons, edges, conflicts = read_layout(root.text(0))
    step, bad, n = build_step(W, H, edges)
    bodies = {}
    team = {}
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = t
    queens = (min(i for i in team if team[i] == 0), min(i for i in team if team[i] == 1))
    out = []
    actor = None
    moved = 0
    rnd = 0
    gone = set()
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 1:
            actor = p.i32(0)
            moved = 0
            gone = set()
        elif k == 9:
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            t = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                b.appendleft(h)
                if i == actor:
                    moved += 1
            while len(b) > 1 and b[-1] != t:
                b.pop()
        elif k == 10:
            par, ch, tm = p.i32(0), p.i32(4), p.u16(8)
            bodies[par] = deque(replay.point(c) for c in p.pointer(0))
            bodies[ch] = deque(replay.point(c) for c in p.pointer(1))
            team[par] = tm
            team[ch] = tm
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            if i in queens and i in bodies:
                occupied = set(gone)
                for z, b in bodies.items():
                    occupied.update(b)
                head = bodies[i][0]
                free = 0
                kelp = 0
                for d in range(4):
                    t = step(head[0], head[1], d)
                    if t is None:
                        kelp += 1
                    elif t not in occupied:
                        free += 1
                out.append(dict(side='us' if team[i] == ours else 'them', reason=reason, round=rnd, length=len(bodies[i]), free=free, kelp_sides=kelp,
                                steps_before=moved if i == actor else None, own_turn=i == actor,
                                alive_us=sum(1 for z in bodies if team[z] == ours), alive_them=sum(1 for z in bodies if team[z] != ours)))
            gone.update(bodies.get(i, ()))
            bodies.pop(i, None)
    return out


def main():
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    games = []
    for k in range(4):
        for line in (Path('data/analysis/ladder/verify') / ('shard%d.jsonl' % k)).read_text().splitlines():
            games.append(json.loads(line))
    order = sorted(games, key=lambda g: (g['completedAt'], g['game']))
    seen = {}
    rows = []
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        if not g['main'] or maps[g['map_key']]['queen_spawn_dead_end']:
            continue
        if not any(g['queen_death'][s] for s in ('us', 'them')):
            continue
        folder = LADDER / g['battle']
        meta = json.loads((folder / ('game-%d.json' % g['game'])).read_text())
        for r in forced(folder / ('M%d.replay' % g['game']), meta):
            r.update(game=g['game'], map_key=g['map_key'], win=g['win'], hour=g['at_kst'][5:13])
            rows.append(r)
    lines = []
    for s in ('us', 'them'):
        rs = [r for r in rows if r['side'] == s]
        lines.append('%s queen deaths %d' % (s, len(rs)))
        for reason in range(5):
            rr = [r for r in rs if r['reason'] == reason]
            lines.append('   reason %d: %d | on her own turn %d, of which boxed in (0 free first steps, first step of the action) %d, had a free step or was mid-sprint %d | not on her own turn %d' % (
                reason, len(rr), sum(1 for r in rr if r['own_turn']), sum(1 for r in rr if r['own_turn'] and r['free'] == 0 and not r['steps_before']),
                sum(1 for r in rr if r['own_turn'] and (r['free'] > 0 or r['steps_before'])), sum(1 for r in rr if not r['own_turn'])))
        box = [r for r in rs if r['own_turn'] and r['free'] == 0 and not r['steps_before']]
        lines.append('   boxed in on her own turn, any reason: %d | by round r0-100 %d, r101-300 %d, r301+ %d | in games we won %d, lost %d' % (
            len(box), sum(1 for r in box if r['round'] <= 100), sum(1 for r in box if 100 < r['round'] <= 300), sum(1 for r in box if r['round'] > 300),
            sum(1 for r in box if r['win']), sum(1 for r in box if not r['win'])))
        free = [r for r in rs if r['own_turn'] and (r['free'] > 0 or r['steps_before'])]
        lines.append('   died on her own turn with a free step available or mid-sprint, any reason: %d %s' % (len(free), dict(Counter(r['reason'] for r in free))))
    for r in rows:
        lines.append(json.dumps(r, ensure_ascii=False))
    Path(P + 'f3-forced-all.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines[:18]))


main()
