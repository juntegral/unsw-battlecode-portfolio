# Own count (analyst, run 20261007-0900), bar F38 (saved in state.json at 09:08, before this file).
# One JSON line per main or v31 game. At the start of every queen turn (both queens):
# tiles: per side, per window (0: raw rounds 0-100, 1: 101-200, 2: 201-300, 3: 301+), per number of open sides of her head tile (0 to 4;
#   open = no kelp on that edge, a portal edge is open, dragons ignored): [queen turns, turns with no free tile next to her head,
#   turns with exactly one free tile, turns with another dragon of her team next to her head, sum of her length].
# deaths: one record per queen death: side, round, reason (engine: 0 wall, 1 own body, 2 other body, 3 head-on, 4 other), and from the start
#   of her last turn: turn_round, open sides, free tiles, own dragon next to her head (0/1), her length.
# Usage: python3 data/analysis/ladder/work/h19_pass.py <shard 0-3>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/work/'
D = Path('data/analysis/ladder')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
N = 4


def build_nxt(W, H, raw):
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
    return nxt


def win(rnd):
    return 0 if rnd <= 100 else 1 if rnd <= 200 else 2 if rnd <= 300 else 3


def study(r):
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

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qids = (queens['us'], queens['them'])
    nxt = build_nxt(W, H, raw)
    tiles = dict(us=[[[0] * 5 for _ in range(5)] for _ in range(4)], them=[[[0] * 5 for _ in range(5)] for _ in range(4)])
    snap = dict()
    deaths = []
    rnd = 0
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
        elif k == 'turnStart':
            actor = p.i32(0)
            if actor in qids and actor in bodies:
                s = side(actor)
                qh = bodies[actor][0]
                occ = dict()
                for z, bb in bodies.items():
                    for c in bb:
                        occ[c] = z
                nb = nxt[qh]
                free = 0
                ally = 0
                for t in nb:
                    z = occ.get(t)
                    if z is None:
                        free += 1
                    elif z != actor and side(z) == s:
                        ally = 1
                op = min(4, len(nb))
                L = len(bodies[actor])
                tt = tiles[s][win(rnd)][op]
                tt[0] += 1
                tt[1] += free == 0
                tt[2] += free == 1
                tt[3] += ally
                tt[4] += L
                snap[s] = (rnd, op, free, ally, L)
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
            if i in qids:
                s = side(i)
                sn = snap.get(s)
                if sn is not None:
                    deaths.append(dict(side=s, round=rnd, reason=p.u16(4), turn_round=sn[0], open=sn[1], free=sn[2], ally=sn[3], qlen=sn[4]))
                else:
                    deaths.append(dict(side=s, round=rnd, reason=p.u16(4), turn_round=None))
            bodies.pop(i)
    return dict(game=game, battle=battle, tiles=tiles, deaths=deaths)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h19-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h19-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h19-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h19-shard3.jsonl', 'w')
    else:
        out = open(P + 'h19-shard-test.jsonl', 'w')
        sel = sel[-4:]
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
