# Own count (analyst, run 20261007-0400): adjacent pearls passed up, split by the bot's own pocket rule.
# Region of a tile = tiles reachable over open edges only (kelp and portal edges closed).
# A chance = a dragon turn that starts with a pearl on a tile next to its head (open edge or portal) that no dragon body is on.
# Pocket chance = every such pearl tile has a region under 48 tiles and (dragon length + 1) > region size // 2. Otherwise open chance.
# One JSON line per main or v31 game: table rows [side 0 ours 1 theirs, window 0 r0-100 1 r101-199 2 r200+, pocket 0/1,
#   via portal 0/1 (the pearl counted is reached through a portal edge), length class 0 = 2, 1 = 3, 2 = 4 or more, chances, eaten];
#   births_all / births_small = natural pearl births in the game / those on tiles whose region has 7 or fewer tiles; small_tiles = such tiles on the map.
# Usage: python3 data/analysis/ladder/work/h7_pocket.py <shard 0-3>
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


def build(W, H, raw):
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
                    out.append((((px - (d == 3)) % W, (row // 2 - (d == 0)) % H), 1))
                else:
                    out.append((((x + STEP[d][0]) % W, (y + STEP[d][1]) % H), 0))
            nxt[(x, y)] = out
    region = dict()
    for start in nxt:
        if start in region:
            continue
        comp = [start]
        seen = set(comp)
        k = 0
        while k < len(comp):
            c = comp[k]
            k += 1
            for t, viap in nxt[c]:
                if viap or t in seen:
                    continue
                seen.add(t)
                comp.append(t)
        for c in comp:
            region[c] = len(comp)
    return nxt, region


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
    nxt, region = build(W, H, raw)
    present = set()
    table = defaultdict(lambda: [0, 0])
    rnd = 0
    pending = None
    ate = 0
    indrop = False
    ball = 0
    bsmall = 0
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k != 'tileChange':
            indrop = False
        if k == 'roundStart' or k == 'turnStart':
            if pending is not None:
                table[pending][0] += 1
                table[pending][1] += ate
            pending = None
            ate = 0
        if k == 'roundStart':
            rnd = p.i32(0)
        elif k == 'turnStart':
            actor = p.i32(0)
            if actor in bodies:
                head = bodies[actor][0]
                cand = [tv for tv in nxt[head] if tv[0] in present]
                if cand:
                    occ = set(c for bb in bodies.values() for c in bb)
                    cand = [tv for tv in cand if tv[0] not in occ]
                    if cand:
                        L = len(bodies[actor])
                        opens = [tv for tv in cand if not (region[tv[0]] < 48 and L + 1 > region[tv[0]] // 2)]
                        if opens:
                            pocket = 0
                            viap = min(tv[1] for tv in opens)
                        else:
                            pocket = 1
                            viap = min(tv[1] for tv in cand)
                        pending = (0 if teams[actor] == ours else 1, 0 if rnd <= 100 else 1 if rnd <= 199 else 2, pocket, viap, 0 if L <= 2 else 1 if L == 3 else 2)
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
                if not indrop:
                    ball += 1
                    if region[c] <= 7:
                        bsmall += 1
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
            indrop = True
    if pending is not None:
        table[pending][0] += 1
        table[pending][1] += ate
    sizes = defaultdict(int)
    for c, s in region.items():
        if s <= 47:
            sizes[s] += 1
    return dict(game=game, battle=battle, table=[list(k) + v for k, v in table.items()], births_all=ball, births_small=bsmall,
                small_tiles=sum(1 for s in region.values() if s <= 7), pocket_tiles_by_region_size=sorted(sizes.items()))


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h7-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h7-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h7-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h7-shard3.jsonl', 'w')
    else:
        out = open(P + 'h7-shard-test.jsonl', 'w')
        sel = [x for x in sel if x['game'] == 1254072] + sel[-1:]
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
