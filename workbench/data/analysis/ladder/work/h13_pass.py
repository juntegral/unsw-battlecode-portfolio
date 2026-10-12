# Own count (analyst, run 20261007-0700, bar F31): adjacent free pearls a dragon does not eat, by round and by the leader pearl zone.
# A chance = a non-queen dragon turn that starts with a pearl on a tile next to its head (open edge or portal) that no dragon body is on.
# Eaten = that dragon removes a pearl during that turn. One JSON line per main or v31 game:
# table rows [side 0 ours 1 theirs, round bin (0 r0-100, 1 r101-125, 2 r126-150, 3 r151-175, 4 r176-199, 5 r200-250, 6 r251-300, 7 r301-350, 8 r351+),
#   enemy 1 if every such pearl has an enemy head within 2 tiles (wrapped Manhattan) else 0,
#   zone class: for each adjacent free pearl the wrapped Manhattan distance to the nearest head among the same-side dragons that have the
#     side's greatest length at that moment (the actor left out); the class takes the largest of these: 0 = 9 or less, 1 = 10 to 18, 2 = more, 3 = no other dragon,
#   top 1 if the actor itself has the side's greatest length (ties count) else 0,
#   length class 0 = 2, 1 = 3, 2 = 4, 3 = 5 or more, side greatest length class 0 = under 6, 1 = 6 to 9, 2 = 10 or more, chances, eaten].
# Usage: python3 data/analysis/ladder/work/h13_pass.py <shard 0-3>
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
BINS = (100, 125, 150, 175, 199, 250, 300, 350)


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
    qa = min(i for i in bodies if teams[i] == 'A')
    qb = min(i for i in bodies if teams[i] == 'B')
    nxt = build_nxt(W, H, raw)
    present = set()
    table = defaultdict(lambda: [0, 0])
    rnd = 0
    actor = None
    pending = None
    ate = 0

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart' or k == 'turnStart':
            if pending is not None:
                table[pending][0] += 1
                table[pending][1] += ate
            pending = None
            ate = 0
            actor = None
        if k == 'roundStart':
            rnd = p.i32(0)
        elif k == 'turnStart':
            actor = p.i32(0)
            if actor in bodies and actor != qa and actor != qb:
                head = bodies[actor][0]
                cand = [t for t in nxt[head] if t in present]
                if cand:
                    occ = set(c for bb in bodies.values() for c in bb)
                    cand = [t for t in cand if t not in occ]
                    if cand:
                        mine = teams[actor]
                        foes = [bb[0] for z, bb in bodies.items() if teams[z] != mine]
                        top = max(len(bb) for z, bb in bodies.items() if teams[z] == mine)
                        tops = [bb[0] for z, bb in bodies.items() if teams[z] == mine and z != actor and len(bb) == top]
                        allnear = 1
                        worst = -1
                        for t in cand:
                            nearfoe = 0
                            for f in foes:
                                if gap(f, t) <= 2:
                                    nearfoe = 1
                                    break
                            if not nearfoe:
                                allnear = 0
                            if tops:
                                dz = min(gap(h2, t) for h2 in tops)
                                if dz > worst:
                                    worst = dz
                        zone = 3 if not tops else 0 if worst <= 9 else 1 if worst <= 18 else 2
                        L = len(bodies[actor])
                        rb = 8
                        for z, lim in enumerate(BINS):
                            if rnd <= lim:
                                rb = z
                                break
                        pending = (0 if mine == ours else 1, rb, allnear, zone, int(L == top),
                                   0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3, 0 if top < 6 else 1 if top < 10 else 2)
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                if c in present and pending is not None:
                    ate = 1
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
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 'dragonDeath':
            bodies.pop(p.i32(0))
    if pending is not None:
        table[pending][0] += 1
        table[pending][1] += ate
    return dict(game=game, battle=battle, table=[list(k) + v for k, v in table.items()])


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h13-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h13-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h13-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h13-shard3.jsonl', 'w')
    else:
        out = open(P + 'h13-shard-test.jsonl', 'w')
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
