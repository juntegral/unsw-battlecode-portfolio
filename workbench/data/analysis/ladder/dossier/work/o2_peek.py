"""Scratch (diag-opening2): print the head of a replay's map text and draw the layout (kelp edges, portal edges, tiles that
spawn, starting dragons). Usage: python3 .../o2_peek.py <label> <map name> [text]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from pathlib import Path
from collections import Counter


def main():
    label, name = sys.argv[1], sys.argv[2]
    folder = Path('data/online/smoke') / (label + '-new')
    for mp in sorted(folder.glob('game-*.json')):
        j = json.loads(mp.read_text())
        if j['mapName'] == name:
            break
    root = replay.load(folder / ('M%d.replay' % j['id'])).root()
    lines = root.text(0).splitlines()
    print(j['id'], j['mapName'], 'A', j['teamAName'], 'B', j['teamBName'])
    print(Counter(x.split()[0] for x in lines if x.split()))
    seen = Counter()
    for x in lines:
        q = x.split()
        if q and seen[q[0]] < 3:
            seen[q[0]] += 1
            print('   ', x[:120])
    if len(sys.argv) > 3:
        return
    W, H = map(int, lines[0].split()[1:3])
    spawn, tiles = {}, {}
    edges = {}
    dr = []
    for x in lines:
        q = x.split()
        if not q:
            continue
        if q[0] == 'TILE':
            tiles[(int(q[1]), int(q[2]))] = q[3:]
        elif q[0] == 'EDGE':
            edges[int(q[1])] = (int(q[2]), int(q[3]))
        elif q[0] == 'DRAGON':
            dr.append((len(dr), int(q[1]), [(int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2]))]))
    print('tile field values', Counter(tuple(v) for v in tiles.values()).most_common(8))
    print('edge kinds', Counter(k for k, p in edges.values()))
    for d in dr:
        print('dragon', d)
    grid = [[' '] * (2 * W + 1) for _ in range(2 * H + 1)]
    for y in range(H):
        for x in range(W):
            v = tiles.get((x, y))
            grid[2 * y + 1][2 * x + 1] = '.' if v is None or int(v[1]) == 0 else 'o'
    for i, t, b in dr:
        for n, (x, y) in enumerate(b):
            grid[2 * y + 1][2 * x + 1] = ('ABCD'[i] if n == 0 else 'abcd'[i])
    for e, (k, p) in edges.items():
        row, x = divmod(e, W + 1)
        ch = '#' if k == 1 else ('0123456789'[p % 10] if k == 2 else ' ')
        if row % 2 == 0:
            yy = row
            if yy <= 2 * H and x < W:
                grid[yy][2 * x + 1] = ch if ch != '#' else '-'
        else:
            grid[row][2 * x] = ch if ch != '#' else '|'
    for r in grid:
        print(''.join(r))


main()
