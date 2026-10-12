# Own count (analyst, run 20261007-0300). One JSON line per main or v31 game:
# cross-team head-on meetings (mover side, both lengths, queen flags, dragons alive, heads near the spot),
# our no-action deaths (round, length, distance to the head of our longest other dragon), split rounds per side,
# and on 2-dragon-start layouts the path distance from each side's nearest head to the nearest pearl in raw rounds 0-50.
# Usage: python3 data/analysis/ladder/work/h3_extract.py <shard 0-3>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from statistics import median
from pathlib import Path

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/work/'
D = Path('data/analysis/ladder')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
N = 4


def study(r, want_path):
    battle, game = r['battle'], r['game']
    folder = Path('data/online/ladder') / str(battle)
    j = json.loads((folder / ('game-%d.json' % game)).read_text())
    root = replay.load(folder / ('M%d.replay' % game)).root()
    text = root.text(0)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    bodies = dict()
    teams = dict()
    raw = []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    ours = 'A' if j['teamAId'] == 1119 else 'B'

    def side(i):
        return 'us' if teams[i] == ours else 'them'

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    nxt = None
    if want_path:
        edges = canonical_edges(W, H, raw)
        portals = defaultdict(list)
        for e, kp in edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        nxt = dict()
        for y in range(H):
            for x in range(W):
                out = []
                for d in range(4):
                    e = edge_id(W, H, x, y, d)
                    kind, pid = edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e]
                        if len(partner) != 1:
                            continue
                        row, px = divmod(partner[0], W + 1)
                        out.append(((px - (d == 3)) % W, (row // 2 - (d == 0)) % H))
                    else:
                        out.append(((x + STEP[d][0]) % W, (y + STEP[d][1]) % H))
                nxt[(x, y)] = out

    def nearest(heads, pset):
        seen = set(heads)
        for h in seen:
            if h in pset:
                return 0
        frontier = list(seen)
        dist = 0
        while frontier:
            dist += 1
            new = []
            for c in frontier:
                for t in nxt[c]:
                    if t in seen:
                        continue
                    if t in pset:
                        return dist
                    seen.add(t)
                    new.append(t)
            frontier = new
        return None

    present = set()
    rnd = 0
    started = False
    actor = None
    victim = None
    meetings = []
    noact = []
    splits = dict(us=[], them=[])
    split_len = dict(us=[], them=[])
    pd = dict(us=[], them=[])
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            if started and want_path and rnd <= 50:
                for s in ('us', 'them'):
                    heads = [b[0] for i, b in bodies.items() if side(i) == s]
                    if heads and present:
                        pd[s].append(nearest(heads, present))
            started = True
            rnd = p.i32(0)
            actor = None
            victim = None
        elif k == 'turnStart':
            actor = p.i32(0)
            victim = None
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
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
            par = p.i32(0)
            s = 'us' if 'AB'[p.u16(8)] == ours else 'them'
            splits[s].append(rnd)
            split_len[s].append(len(bodies[par]))
            for z, i in enumerate((par, p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 'dragonDeath':
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies[i]
            s = side(i)
            if reason == 3 and i != actor:
                au = sum(1 for z in bodies if side(z) == 'us')
                at = len(bodies) - au
                nu = sum(1 for z, bb in bodies.items() if z != i and z != actor and side(z) == 'us' and gap(bb[0], b[0]) <= 5)
                nt = sum(1 for z, bb in bodies.items() if z != i and z != actor and side(z) == 'them' and gap(bb[0], b[0]) <= 5)
                victim = dict(id=i, side=s, length=len(b), queen=i == queens[s], au=au, at=at, nu=nu, nt=nt)
            elif reason == 3 and i == actor and victim is not None:
                if victim['side'] != s:
                    meetings.append([rnd, s[0], len(b), victim['length'], int(i == queens[s]), int(victim['queen']), victim['au'], victim['at'], victim['nu'], victim['nt']])
                victim = None
            elif reason == 4 and s == 'us':
                others = [(len(bb), z) for z, bb in bodies.items() if z != i and side(z) == 'us']
                if others:
                    ln, z = max(others)
                    noact.append([rnd, len(b), gap(bodies[z][0], b[0]), ln, int(z == queens['us']), len(others) + 1, int(i == queens['us'])])
                else:
                    noact.append([rnd, len(b), None, 0, 0, 1, int(i == queens['us'])])
            bodies.pop(i)
    out = dict(game=game, battle=battle, meetings=meetings, noact=noact,
               splits=dict(us=splits['us'][:40], them=splits['them'][:40]), nsplits=dict(us=len(splits['us']), them=len(splits['them'])),
               split_len=dict(us=split_len['us'][:40], them=split_len['them'][:40]))
    if want_path:
        out['path'] = dict((s, dict(median=median([x for x in pd[s] if x is not None]) if [x for x in pd[s] if x is not None] else None, rounds=len(pd[s]),
                                    within8=sum(1 for x in pd[s] if x is not None and x <= 8))) for s in ('us', 'them'))
    return out


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h3-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h3-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h3-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h3-shard3.jsonl', 'w')
    else:
        out = open(P + 'h3-shard-test.jsonl', 'w')
        sel = sel[-3:]
    done = 0
    for k, r in enumerate(sel):
        if shard < N and k % N != shard:
            continue
        want = maps[r['map_key']]['dragons_at_spawn'] == 2
        try:
            rec = study(r, want)
        except Exception as e:
            rec = dict(game=r['game'], battle=r['battle'], error='%s: %s' % (type(e).__name__, e))
        out.write(json.dumps(rec) + '\n')
        out.flush()
        done += 1
    out.close()
    print('shard', shard, 'games written', done)


main()
