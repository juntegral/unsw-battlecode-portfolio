# Scratch (diag-sacrifice): a second, plain look at single deaths. Replays one game up to the death of dragon <id>
# in round <round>, draws the tiles around its head (walls from the map edges, bodies from the dragon updates),
# then lists what its side does in the next three rounds (dragons alive, splits, who eats the dropped pearls).
# Usage: python3 data/analysis/ladder/dossier/work/sc_view.py <game> <round> <id>
#        python3 data/analysis/ladder/dossier/work/sc_view.py pick <team> <kind B or F> <max round>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import deque
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))

if sys.argv[1] == 'pick':
    team, kind, top = sys.argv[2], sys.argv[3], int(sys.argv[4])
    out = []
    for n in range(4):
        for line in Path(W + 'sc_ev-%d.jsonl' % n).read_text().splitlines():
            g = json.loads(line)
            if g['opponent'] != team:
                continue
            for d in g['events']:
                if d['side'] == 't' and d['reason'] == 4 and d['r'] <= top and (d['free'] == 0) == (kind == 'B'):
                    out.append((g['game'], d['r'], d['id'], d['L'], d['free'], d['room'], d['n_side'] + 1, g['layout']))
    for row in out[::max(1, len(out) // 8)][:8]:
        print(row)
    sys.exit()

game, want_round, want_id = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
snap = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())
row = [r for r in snap['rows'] if r['game'] == game][0]
path = Path('data/online/ladder') / str(row['battle']) / ('M%d.replay' % game)
root = replay.load(path).root()
text = root.text(0)
w, h = map(int, text.splitlines()[0].split()[1:3])
bodies, teams, raw = {}, {}, []
for line in text.splitlines():
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = 'AB'[int(q[1])]
    elif q and q[0] == 'EDGE':
        raw.append(tuple(map(int, q[1:4])))
edges = canonical_edges(w, h, raw)


def wall(x, y, d):
    return edges.get(edge_id(w, h, x, y, d), (0, -1))[0]


def draw(i):
    hx, hy = bodies[i][0]
    mine = teams[i]
    cell = {}
    for z, b in bodies.items():
        for k, c in enumerate(b):
            if z == i:
                cell[c] = '@' if k == 0 else '*'
            elif teams[z] == mine:
                cell[c] = 'M' if k == 0 else 'm'
            else:
                cell[c] = 'E' if k == 0 else 'e'
    for dy in range(-3, 4):
        top, mid = '', ''
        for dx in range(-3, 4):
            x, y = (hx + dx) % w, (hy + dy) % h
            top += '+' + ('--' if wall(x, y, 0) == 1 else '==' if wall(x, y, 0) == 2 else '  ')
            left = wall(x, y, 3)
            mid += ('|' if left == 1 else ':' if left == 2 else ' ') + cell.get((x, y), 'o' if (x, y) in pearls else '.') + ' '
        print('   ' + top + '+')
        print('   ' + mid)
    free = 0
    for d in range(4):
        dx, dy = STEP[d]
        c = ((hx + dx) % w, (hy + dy) % h)
        if wall(hx, hy, d) != 1 and (wall(hx, hy, d) == 2 or c not in cell):
            free += 1
    print('   head at', (hx, hy), 'length', len(bodies[i]), '| sides without a wall and without a body (portal sides count as free):', free,
          '| @ head, * own body, M m team mate, E e the other side, o pearl, | -- kelp, : == portal')


pearls = set()
rnd, actor, act = 0, None, None
found_at = None
side = None
drop = set()
log = []
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 4, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
        if found_at is not None:
            if rnd > found_at + 3:
                break
            log.append('round %d starts: its side has %d dragons' % (rnd, sum(1 for z in bodies if teams[z] == side)))
    elif k == 1:
        actor = p.i32(0)
        act = None
    elif k == 4:
        a = p.pointer(0)
        act = ('split order', 'no order', 'no order')[min(a.u16(0), 2)] if a and a.u16(0) >= 1 else 'move' if a else 'no order'
    elif k == 3:
        c = replay.point(p.pointer(0))
        if p.u32(0):
            pearls.add(c)
        else:
            pearls.discard(c)
            if c in drop:
                log.append('round %d: dragon %d (length %d, %s) eats the pearl dropped at %s' % (
                    rnd, actor, len(bodies[actor]), 'same side' if teams[actor] == side else 'OTHER side', c))
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        par, kid = p.i32(0), p.i32(4)
        before = len(bodies[par])
        for z, i in enumerate((par, kid)):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = 'AB'[p.u16(8)]
        if found_at is not None and teams[par] == side:
            log.append('round %d: dragon %d of its side splits %d into %d + %d at %s' % (rnd, par, before, len(bodies[par]), len(bodies[kid]), bodies[par][0]))
        if par == want_id and rnd >= want_round - 2:
            print('round %d: dragon %d splits %d into %d (front, itself) + %d (child %d)' % (rnd, par, before, len(bodies[par]), len(bodies[kid]), kid))
    elif k == 11:
        i, reason = p.i32(0), p.u16(4)
        if i == want_id and rnd == want_round:
            side = teams[i]
            print('game', game, row['map_key'], 'vs', row['opponent'], row['opponent_rating'], '| round', rnd, 'dragon', i, 'dies, engine reason', reason,
                  '(4 = no valid action), its order:', act, '| its side has', sum(1 for z in bodies if teams[z] == side), 'dragons, the other', sum(1 for z in bodies if teams[z] != side))
            draw(i)
            found_at = rnd
            drop = set(c for n, c in enumerate(bodies[i]) if n % 2 == 0)
        bodies.pop(i)
for line in log:
    print('  ', line)
