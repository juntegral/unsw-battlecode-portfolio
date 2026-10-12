# Scratch (early-growth brief): draw a layout with walls, and heat maps of pearl births and of where heads stand.
# Usage: python3 data/analysis/ladder/losses/work/eg_map.py <layout prefix> <L or R: the half our dragons start in> [group]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import Counter
from pathlib import Path

prefix, our = sys.argv[1], sys.argv[2]
games = []
for n in range(4):
    for line in Path('data/analysis/ladder/losses/work/eg_rows-%d.jsonl' % n).read_text().splitlines():
        g = json.loads(line)
        first = [t for t in g['turns'] if t[1] == 'u' and t[0] == 0]
        half = 'L' if first[0][6] % g['w'] < g['w'] // 2 else 'R'
        if g['map_key'].startswith(prefix) and half == our and (len(sys.argv) < 4 or g['group'] == sys.argv[3]):
            games.append(g)
per = {r['game']: r for r in json.loads(Path('data/analysis/ladder/losses/split/per-game.json').read_text())}
g0 = games[0]
w, h = g0['w'], g0['h']
root = replay.load(Path(per[g0['game']]['replay'])).root()
raw, spawn = [], {}
for line in root.text(0).splitlines():
    q = line.split()
    if q and q[0] == 'EDGE':
        raw.append(tuple(map(int, q[1:4])))
    elif q and q[0] == 'DRAGON':
        for k in range(int(q[2])):
            spawn[int(q[4 + 2 * k]) * w + int(q[3 + 2 * k])] = 'AB'[int(q[1])] if k == 0 else 'ab'[int(q[1])]
edges = canonical_edges(w, h, raw)
print(prefix, w, h, 'games with our start in half', our, ':', len(games), 'groups', dict(Counter(g['group'] for g in games)))


def draw(title, cell):
    print()
    print(title)
    for y in range(h):
        top, mid = '', ''
        for x in range(w):
            kn = edges.get(edge_id(w, h, x, y, 0), (0, -1))[0]
            kw = edges.get(edge_id(w, h, x, y, 3), (0, -1))[0]
            top += '+' + ('-' if kn == 1 else '=' if kn == 2 else ' ')
            mid += ('|' if kw == 1 else ':' if kw == 2 else ' ') + cell(y * w + x)
        print(top + '+')
        print(mid + ('|' if edges.get(edge_id(w, h, w - 1, y, 1), (0, -1))[0] == 1 else ' '))


def heat(counter):
    top = max(counter.values(), default=1)

    def cell(c):
        v = counter.get(c, 0)
        if c in spawn and v == 0:
            return spawn[c]
        return '.' if v == 0 else str(min(9, 1 + (8 * v) // top))
    return cell


draw('spawn (A/B head, a/b body), centre X', lambda c: spawn.get(c, 'X' if c == (h // 2) * w + w // 2 else '.'))
births = Counter(p[0] for g in games for p in g['pearls'] if p[2] == 'n' and p[1] <= 60)
draw('natural pearl births r0-60 (1-9 scaled to the busiest tile, %d births)' % sum(births.values()), heat(births))
for lo, hi in ((0, 29), (30, 59), (60, 120)):
    for s, name in (('u', 'OUR'), ('t', 'THEIR')):
        c = Counter(t[6] for g in games for t in g['turns'] if t[1] == s and lo <= t[0] <= hi)
        draw('%s heads at turn start r%d-%d (%d turns)' % (name, lo, hi, sum(c.values())), heat(c))
eat = {s: Counter(p[0] for g in games for p in g['pearls'] if p[7] == s and p[8] <= 60) for s in 'ut'}
draw('pearls WE ate r0-60 (%d)' % sum(eat['u'].values()), heat(eat['u']))
draw('pearls THEY ate r0-60 (%d)' % sum(eat['t'].values()), heat(eat['t']))
