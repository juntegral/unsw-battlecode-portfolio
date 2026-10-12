# Own count (analyst, run 20261007-0400): how the heads of each side are spread on the board.
# One JSON line per main or v31 game on a layout with 1500 or more open tiles. snaps rows:
# [round, our heads, their heads, our median nearest-friend distance, theirs, our heads in their half, their heads in our half].
# Snapshots at the start of raw rounds 100, 125, ..., 300. Distance = wrapped Manhattan. A head is in the enemy half when it is
# strictly nearer to the enemy queen spawn tile than to its own queen spawn tile.
# Usage: python3 data/analysis/ladder/work/h6_spread.py <shard 0-3>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from statistics import median
from pathlib import Path

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/work/'
D = Path('data/analysis/ladder')
N = 4
MARKS = set(range(100, 301, 25))


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

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    home_us = bodies[min(i for i in bodies if teams[i] == ours)][0]
    home_them = bodies[min(i for i in bodies if teams[i] != ours)][0]
    snaps = []
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
            if rnd in MARKS:
                hu = [bb[0] for z, bb in bodies.items() if teams[z] == ours]
                ht = [bb[0] for z, bb in bodies.items() if teams[z] != ours]
                if len(hu) >= 2 and len(ht) >= 2:
                    nu = median([min(gap(a, b) for b in hu if b is not a) for a in hu])
                    nt = median([min(gap(a, b) for b in ht if b is not a) for a in ht])
                    fu = sum(1 for a in hu if gap(a, home_them) < gap(a, home_us))
                    ft = sum(1 for a in ht if gap(a, home_us) < gap(a, home_them))
                    snaps.append([rnd, len(hu), len(ht), nu, nt, fu, ft])
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
    return dict(game=game, battle=battle, snaps=snaps)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = [r for r in rows if r['our_code'] in ('main', 'v31') and maps[r['map_key']]['open_tiles'] >= 1500]
    if shard == 0:
        out = open(P + 'h6-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h6-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h6-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h6-shard3.jsonl', 'w')
    else:
        out = open(P + 'h6-shard-test.jsonl', 'w')
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
