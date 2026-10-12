"""Scratch (diag-opening2): where natural pearls are born on one layout, rounds 0-40, over the ladder games of ours on it.
Cell: '.' never spawns in any game; ',' spawns only after round 40; digit = births in rounds 0-40 per game, rounded up
(9 = 9 or more); capital letters = starting heads (A, C one side; B, D the other), small = their bodies.
Usage: python3 .../o2_spawnmap.py <cells> [last round]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from pathlib import Path
from collections import Counter
import math

DOS = Path('data/analysis/ladder/dossier')


def main():
    cells = int(sys.argv[1])
    last = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    rows = [json.loads(x) for x in (DOS / 'per-game.jsonl').read_text().splitlines()]
    rows = [r for r in rows if r['relation'] == 'us' and r['cells'] == cells]
    early, ever, first = Counter(), Counter(), {}
    n = 0
    lines = None
    for r in rows:
        root = replay.load(Path(r['replay'])).root()
        if lines is None:
            lines = root.text(0).splitlines()
        n += 1
        rnd, actor = 0, None
        for ev in root.pointer(3):
            k = ev.u16(0)
            if k == 0:
                rnd, actor = ev.pointer(0).i32(0), None
            elif k == 1:
                actor = ev.pointer(0).i32(0)
            elif k == 3 and actor is None and ev.pointer(0).u32(0):
                c = replay.point(ev.pointer(0).pointer(0))
                ever[c] += 1
                if rnd <= last:
                    early[c] += 1
                first.setdefault(c, []).append(rnd)
    W, H = map(int, lines[0].split()[1:3])
    edges, dr = {}, []
    for x in lines:
        q = x.split()
        if q and q[0] == 'EDGE':
            edges[int(q[1])] = (int(q[2]), int(q[3]))
        elif q and q[0] == 'DRAGON':
            dr.append((len(dr), [(int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2]))]))
    print(rows[0]['map_name'], W, H, 'games', n, 'tiles that ever spawn', len(ever), 'born r0-%d a game' % last, round(sum(early.values()) / n, 1),
          'born in round 0 a game', round(sum(1 for c, v in first.items() for x in v if x == 0) / n, 1))
    grid = [[' '] * (2 * W + 1) for _ in range(2 * H + 1)]
    for y in range(H):
        for x in range(W):
            c = (x, y)
            v = early[c] / n
            grid[2 * y + 1][2 * x + 1] = '.' if c not in ever else ',' if v == 0 else '0123456789'[min(9, math.ceil(v))]
    for i, b in dr:
        for m, (x, y) in enumerate(b):
            if m == 0:
                grid[2 * y + 1][2 * x + 1] = 'ABCD'[i]
    for e, (k, p) in edges.items():
        row, x = divmod(e, W + 1)
        if k == 0:
            continue
        ch = '#' if k == 1 else '*'
        if row % 2 == 0:
            if row <= 2 * H and x < W:
                grid[row][2 * x + 1] = '-' if k == 1 else '*'
        else:
            grid[row][2 * x] = '|' if k == 1 else '*'
    for r in grid:
        print(''.join(r))


main()
