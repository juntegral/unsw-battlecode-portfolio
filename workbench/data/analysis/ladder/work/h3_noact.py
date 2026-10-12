# Own count (analyst, run 20261007-0300): our no-action deaths. Where they happen and who eats the drop.
# One JSON line per main or v31 game. Row per death:
# [round, length, gap to nearest own head at least twice as long (None if no such dragon), that dragon's length,
#  gap to our longest other head, gap to nearest enemy head, pearls dropped, eaten within 15 rounds by us, by them,
#  eaten within 15 by an own dragon at least twice as long as the dead one, our dragons alive, their dragons alive]
# Usage: python3 data/analysis/ladder/work/h3_noact.py <shard 0-3>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/work/'
D = Path('data/analysis/ladder')
N = 4


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

    def side(i):
        return 'us' if teams[i] == ours else 'them'

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    tile = dict()
    rnd = 0
    actor = None
    ctx = None
    recs = []
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k != 'tileChange':
            ctx = None
        if k == 'roundStart':
            rnd = p.i32(0)
            actor = None
        elif k == 'turnStart':
            actor = p.i32(0)
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                tile[c] = ctx
                if ctx is not None:
                    ctx[6] += 1
            else:
                rec = tile.pop(c, None)
                if rec is not None and actor in bodies and rnd - rec[0] <= 15:
                    if side(actor) == 'us':
                        rec[7] += 1
                        if len(bodies[actor]) >= 2 * rec[1]:
                            rec[9] += 1
                    else:
                        rec[8] += 1
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
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.pop(i)
            if reason == 4 and side(i) == 'us':
                L = len(b)
                own = [(gap(bb[0], b[0]), len(bb)) for z, bb in bodies.items() if side(z) == 'us']
                big = [x for x in own if x[1] >= 2 * L]
                en = [gap(bb[0], b[0]) for z, bb in bodies.items() if side(z) == 'them']
                nb = min(big) if big else (None, 0)
                lg = max(own, key=lambda x: x[1])[0] if own else None
                ctx = [rnd, L, nb[0], nb[1], lg, min(en) if en else None, 0, 0, 0, 0, len(own) + 1, len(en)]
                recs.append(ctx)
    return dict(game=game, battle=battle, last_round=rnd, noact=recs)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h3n-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h3n-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h3n-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h3n-shard3.jsonl', 'w')
    else:
        out = open(P + 'h3n-shard-test.jsonl', 'w')
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
