# Own count (analyst, run 20261007-0700, bar F31_splits): per game, side and 25-round bin: split events, deaths, pearls eaten,
# dragons alive at the bin start, dragons of length 5 or more at the bin start, greatest length at the bin start.
# One JSON line per main or v31 game: bins = list over bin index b (rounds 25b .. 25b+24) of
#   [alive us, alive them, long us, long them, top us, top them, splits us, splits them, deaths us, deaths them, 0, 0, pearls us, pearls them,
#    dragons of length exactly 4 us, them].
# Usage: python3 data/analysis/ladder/work/h14_pass.py <shard 0-3>
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
    bodies = dict()
    teams = dict()
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    ours = 'A' if j['teamAId'] == 1119 else 'B'
    present = set()
    bins = []
    cur = None
    actor = None

    def snap():
        row = [0] * 16
        for i, bb in bodies.items():
            s = 0 if teams[i] == ours else 1
            L = len(bb)
            row[s] += 1
            if L >= 5:
                row[2 + s] += 1
            if L == 4:
                row[14 + s] += 1
            if L > row[4 + s]:
                row[4 + s] = L
        return row

    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
            actor = None
            if rnd % 25 == 0:
                cur = snap()
                bins.append(cur)
        elif k == 'turnStart':
            actor = p.i32(0)
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                if c in present and actor is not None and actor in teams:
                    cur[12 + (0 if teams[actor] == ours else 1)] += 1
                present.discard(c)
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
            cur[6 + (0 if 'AB'[p.u16(8)] == ours else 1)] += 1
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 'dragonDeath':
            i = p.i32(0)
            cur[8 + (0 if teams[i] == ours else 1)] += 1
            bodies.pop(i)
    return dict(game=game, battle=battle, bins=bins)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h14-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h14-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h14-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h14-shard3.jsonl', 'w')
    else:
        out = open(P + 'h14-shard-test.jsonl', 'w')
        sel = [x for x in sel if x['game'] in (1280136, 1276407)]
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
