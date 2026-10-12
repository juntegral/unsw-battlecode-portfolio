# Own count (analyst, run 20261007-0300): natural pearls by how far they were born from each side's nearest head.
# One JSON line per main or v31 game: table of [our gap bin, their gap bin, balance, window, eaten by us, eaten by them, not eaten].
# Gap = wrapped Manhattan distance from the birth tile to the nearest head of that side at the birth. Bins 0: 0-3, 1: 4-6, 2: 7-12, 3: 13+.
# Balance 2 = the sides are within 10 percent of each other in dragons alive at the birth, 1 = within 1.5 times, 0 = neither. Last key = fast respawn (the tile's last natural pearl was eaten 12 or fewer rounds before this birth). Window 0: r0-100, 1: r101-300, 2: r301+ (round of birth).
# Usage: python3 data/analysis/ladder/work/h3_reach.py <shard 0-3>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, defaultdict
from pathlib import Path

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/work/'
D = Path('data/analysis/ladder')
N = 4


def gbin(g):
    return 0 if g <= 3 else 1 if g <= 6 else 2 if g <= 12 else 3


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
    tile = dict()
    removed = dict()
    table = defaultdict(lambda: [0, 0, 0])
    rnd = 0
    actor = None
    indrop = False
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k != 'tileChange':
            indrop = False
        if k == 'roundStart':
            rnd = p.i32(0)
            actor = None
        elif k == 'turnStart':
            actor = p.i32(0)
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if indrop:
                    tile[c] = None
                else:
                    gu = 99
                    gt = 99
                    nu = 0
                    nt = 0
                    for z, bb in bodies.items():
                        h = bb[0]
                        dx = abs(h[0] - c[0])
                        dy = abs(h[1] - c[1])
                        g = min(dx, W - dx) + min(dy, H - dy)
                        if teams[z] == ours:
                            nu += 1
                            if g < gu:
                                gu = g
                        else:
                            nt += 1
                            if g < gt:
                                gt = g
                    bal = 0 if (nu == 0 or nt == 0) else 2 if (nu <= 1.1 * nt and nt <= 1.1 * nu) else 1 if (nu <= 1.5 * nt and nt <= 1.5 * nu) else 0
                    tile[c] = (gbin(gu), gbin(gt), bal, 0 if rnd <= 100 else 1 if rnd <= 300 else 2, int(c in removed and rnd - removed[c] <= 12))
            else:
                key = tile.pop(c, None)
                if key is not None:
                    removed[c] = rnd
                if key is not None and actor in teams:
                    table[key][0 if teams[actor] == ours else 1] += 1
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
    for c, key in tile.items():
        if key is not None:
            table[key][2] += 1
    return dict(game=game, battle=battle, table=[list(k) + v for k, v in table.items()])


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h3s-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h3s-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h3s-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h3s-shard3.jsonl', 'w')
    else:
        out = open(P + 'h3s-shard-test.jsonl', 'w')
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
