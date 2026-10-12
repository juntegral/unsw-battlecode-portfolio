# Own count (analyst, run 20261007-0600, bar F27). One JSON line per main or v31 game.
# chances: every turn start of a non-queen dragon whose head has the living enemy queen head one open-edge or portal step away:
#   [round, acting side u or t, dragon length, own queen of the acting side alive 0/1, taken 0/1 (the enemy queen dies in that turn
#    by head-on with this dragon as the mover), enemy queen length, enemy queen alive 3 rounds later 0/1 or -1 if the game ended,
#    this dragon alive at the end of its turn 0/1].
# Usage: python3 data/analysis/ladder/work/h11_pass.py <shard 0-3>
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
    qdeath = dict()
    chances = []
    cur = None
    rnd = 0
    actor = None

    def close():
        if cur is not None:
            cur[7] = int(cur[8] in bodies)
            chances.append(cur)

    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            close()
            cur = None
            rnd = p.i32(0)
            actor = None
        elif k == 'turnStart':
            close()
            cur = None
            actor = p.i32(0)
            if actor in bodies and actor not in qids:
                s = side(actor)
                o = 'them' if s == 'us' else 'us'
                eq = queens[o]
                if eq in bodies and bodies[eq][0] in nxt[bodies[actor][0]]:
                    cur = [rnd, s[0], len(bodies[actor]), int(queens[s] in bodies), 0, len(bodies[eq]), o, 0, actor]
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
            if i in qids:
                qdeath[side(i)] = rnd
                if cur is not None and reason == 3 and i != actor and side(i) == cur[6]:
                    cur[4] = 1
            bodies.pop(i)
    close()
    last = r['last_round']
    out = []
    for c in chances:
        dr = qdeath.get(c[6])
        later = -1 if c[0] + 3 > last else int(dr is None or dr > c[0] + 3)
        out.append([c[0], c[1], c[2], c[3], c[4], c[5], later, c[7]])
    return dict(game=game, battle=battle, chances=out)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h11-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h11-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h11-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h11-shard3.jsonl', 'w')
    else:
        out = open(P + 'h11-shard-test.jsonl', 'w')
        sel = sel[-6:]
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
