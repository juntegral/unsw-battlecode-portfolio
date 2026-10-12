# Own count (analyst, run 20261007-0400): heads standing at the tiles that keep giving pearls.
# Busy tile = a tile with 8 or more natural pearl births in that game (5 or more is kept as a second cut).
# One JSON line per main or v31 game on a layout with 1500 or more open tiles. snaps rows:
# [round, our heads, their heads, ours within 2 of a busy tile, theirs, ours within 2 of a 5-birth tile, theirs, ours on a tile within 0 (standing on), theirs].
# Snapshots at the start of raw rounds 100, 125, ..., 300. Distance = wrapped Manhattan.
# Usage: python3 data/analysis/ladder/work/h8_fountain.py <shard 0-3>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, defaultdict
from pathlib import Path

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/work/'
D = Path('data/analysis/ladder')
N = 4
MARKS = set(range(100, 301, 25))
NEAR = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if abs(dx) + abs(dy) <= 2]


def study(r):
    battle, game = r['battle'], r['game']
    folder = Path('data/online/ladder') / str(battle)
    j = json.loads((folder / ('game-%d.json' % game)).read_text())
    root = replay.load(folder / ('M%d.replay' % game)).root()
    text = root.text(0)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    bodies = dict()
    teams = dict()
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    ours = 'A' if j['teamAId'] == 1119 else 'B'
    births = defaultdict(int)
    held = []
    indrop = False
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k != 'tileChange':
            indrop = False
        if k == 'roundStart':
            rnd = p.i32(0)
            if rnd in MARKS:
                held.append((rnd, [bb[0] for z, bb in bodies.items() if teams[z] == ours], [bb[0] for z, bb in bodies.items() if teams[z] != ours]))
        elif k == 'tileChange':
            if p.u32(0) and not indrop:
                births[replay.point(p.pointer(0))] += 1
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 'dragonDeath':
            bodies.pop(p.i32(0))
            indrop = True
    busy8 = set(c for c, n in births.items() if n >= 8)
    busy5 = set(c for c, n in births.items() if n >= 5)
    zone8 = set(((c[0] + dx) % W, (c[1] + dy) % H) for c in busy8 for dx, dy in NEAR)
    zone5 = set(((c[0] + dx) % W, (c[1] + dy) % H) for c in busy5 for dx, dy in NEAR)
    snaps = []
    for rnd, hu, ht in held:
        snaps.append([rnd, len(hu), len(ht), sum(1 for h in hu if h in zone8), sum(1 for h in ht if h in zone8),
                      sum(1 for h in hu if h in zone5), sum(1 for h in ht if h in zone5), sum(1 for h in hu if h in busy8), sum(1 for h in ht if h in busy8)])
    return dict(game=game, battle=battle, snaps=snaps, busy8=len(busy8), busy5=len(busy5), zone8=len(zone8), births=sum(births.values()), births_on_busy8=sum(n for c, n in births.items() if n >= 8))


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = [r for r in rows if r['our_code'] in ('main', 'v31') and maps[r['map_key']]['open_tiles'] >= 1500]
    if shard == 0:
        out = open(P + 'h8-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h8-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h8-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h8-shard3.jsonl', 'w')
    else:
        out = open(P + 'h8-shard-test.jsonl', 'w')
        sel = sel[-2:]
    done = 0
    for k, r in enumerate(sel):
        if shard < N and k % N != shard:
            continue
        try:
            rec = study(r)
        except Exception as e:
            rec = dict(game=r['game'], battle=r['battle'], error='%s: %s' % (type(e).__name__, e))
        out.write(json.dumps(rec) + '\n')
        out.flush()
        done += 1
    out.close()
    print('shard', shard, 'games written', done)


main()
