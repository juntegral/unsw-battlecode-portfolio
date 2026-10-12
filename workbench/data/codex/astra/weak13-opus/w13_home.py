"""Home area without portals: the tiles reachable from our start heads without crossing a portal edge (kelp blocks, torus wraps).
Prints its size, natural pearl spawns inside / outside in r0-99 and r100-199, our turn starts inside / outside, and the same for them.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_home.py <battle> <gid>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, Counter
from pathlib import Path

battle, gid = sys.argv[1], int(sys.argv[2])
folder = Path('data/online/live-one1') / battle if not battle.startswith('data/') else Path(battle)
j = json.loads((folder / ('game-%d.json' % gid)).read_text())
root = replay.load(folder / ('M%d.replay' % gid)).root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
heads, teams, raw = {}, {}, []
for line in lines:
    q = line.split()
    if not q:
        continue
    if q[0] == 'DRAGON':
        i = len(heads)
        heads[i] = (int(q[3]), int(q[4]))
        teams[i] = int(q[1])
    elif q[0] == 'EDGE':
        raw.append((int(q[1]), int(q[2]), int(q[3])))
edges = canonical_edges(W, H, raw)
own = 0 if j['teamAId'] == 1119 else 1


def area(starts):
    seen = set(starts)
    qu = deque(starts)
    while qu:
        c = qu.popleft()
        for d in range(4):
            if edges.get(edge_id(W, H, c[0], c[1], d), (0, -1))[0] != 0:
                continue
            n = ((c[0] + STEP[d][0]) % W, (c[1] + STEP[d][1]) % H)
            if n not in seen:
                seen.add(n)
                qu.append(n)
    return seen


home = area([h for i, h in heads.items() if teams[i] == own])
theirs = area([h for i, h in heads.items() if teams[i] != own])
c = Counter()
rnd, actor, expected = -1, None, 0
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
        if rnd >= 200:
            break
    elif k == 1:
        actor = p.i32(0)
        s = 'us' if teams[actor] == own else 'th'
        c[rnd // 100, s, 'in' if heads[actor] in (home if s == 'us' else theirs) else 'out'] += 1
    elif k == 3:
        xy = replay.point(p.pointer(0))
        if p.u32(0):
            if expected:
                expected -= 1
            else:
                c[rnd // 100, 'spawn', 'home' if xy in home else 'theirs' if xy in theirs else 'else'] += 1
        else:
            s = 'us' if teams[actor] == own else 'th'
            c[rnd // 100, s, 'eat'] += 1
    elif k == 9:
        heads[p.i32(0)] = replay.point(p.pointer(0))
    elif k == 10:
        for z, i in enumerate((p.i32(0), p.i32(4))):
            body = [replay.point(x) for x in p.pointer(z)]
            heads[i] = body[0]
            teams[i] = p.u16(8)
        # a split leaves pearls nowhere
    elif k == 11:
        i = p.i32(0)
        expected = 0
        heads.pop(i, None)
        # corpse pearls follow as tile changes; count them out of the natural spawns
        expected = -1
    if k == 11:
        expected = 10 ** 6
    elif k in (0, 1) and expected:
        expected = 0
print('%d %s %dx%d=%d tiles: our portal-free home area %d tiles, theirs %d tiles, same area: %s' % (
    gid, j['mapName'], W, H, W * H, len(home), len(theirs), home == theirs))
for hh in (0, 1):
    print('  r%d-%d natural spawns in our home %d, in theirs %d, elsewhere %d | our turn starts inside home %d outside %d, pearls eaten %d | '
          'their turn starts inside their home %d outside %d, pearls eaten %d' % (
              hh * 100, hh * 100 + 99, c[hh, 'spawn', 'home'], c[hh, 'spawn', 'theirs'], c[hh, 'spawn', 'else'],
              c[hh, 'us', 'in'], c[hh, 'us', 'out'], c[hh, 'us', 'eat'], c[hh, 'th', 'in'], c[hh, 'th', 'out'], c[hh, 'th', 'eat']))
