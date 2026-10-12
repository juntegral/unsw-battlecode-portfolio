"""Scratch (diag-wipeout): the first 100 rounds of every game, both sides, in 20-round buckets: turns, turns that
begin with a pearl inside the dragon's 7 by 7 view, eats, turns with nothing in view, steps back onto a tile of the
dragon's own last 12 heads, deaths; tiles the side has had in view; natural pearls born on each half and who ate them.
Usage: python3 data/analysis/ladder/dossier/work/wo_op2.py <O|L|R> <shard> <shards>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'sr51-bob1', 'agg7-b1', 'agg7-b2', 'agg7-b3')
LAST = 100


def jobs(src):
    out = []
    if src == 'O':
        for label in LABELS:
            folder = Path('data/online/smoke') / (label + '-new')
            if not folder.is_dir():
                continue
            for mp in sorted(folder.glob('game-*.json')):
                j = json.loads(mp.read_text())
                rp = folder / ('M%d.replay' % j['id'])
                if rp.exists():
                    out.append((label, rp, j, 1119))
    else:
        path = Path('data/analysis/ladder/dossier') / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            rp = Path(r['replay'])
            j = json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text())
            out.append((src, rp, j, team))
        out.sort(key=lambda t: t[2]['id'])
    return out


def scan(label, path, j, team):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    own = 0 if j['teamAId'] == team else 1

    def side(i):
        return 0 if teams[i] == own else 1

    starts = [[bodies[i][0] for i in bodies if side(i) == s] for s in (0, 1)]

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def inview(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3

    def half(c):
        a = min(gap(c, s) for s in starts[0])
        b = min(gap(c, s) for s in starts[1])
        return 0 if a < b else 1 if b < a else 2

    seen = [set(), set()]

    def look(s, h):
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                seen[s].add(((h[0] + dx) % W, (h[1] + dy) % H))

    for i, b in bodies.items():
        look(side(i), b[0])
    B = [[0] * 16 for _ in range(5)]     # per bucket: per side turns, inview, eats, blind, retread, deaths, splits, foe-in-view turns
    trail = defaultdict(lambda: deque(maxlen=12))
    pearls = {}
    born = [[0, 0, 0], [0, 0, 0]]        # natural pearls born by r60 on our half / their half / level ; row 1 unused
    ate = [[0, 0, 0], [0, 0, 0]]         # eaten by r80 by side, by half of the pearl (natural, born by r60)
    seen_at = {}
    count_at = {}
    first_eat = [None, None]
    first_foe = None
    rnd, actor = -1, None
    cur = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if rnd >= 0 and rnd % 20 == 0:
                seen_at[rnd] = [len(seen[0]), len(seen[1])]
            if rnd >= 0 and rnd % 10 == 0:
                count_at[rnd] = [sum(1 for i in bodies if side(i) == 0), sum(1 for i in bodies if side(i) == 1)]
            rnd, actor = p.i32(0), None
            if rnd > LAST:
                break
        elif k == 1:
            actor = p.i32(0)
            b = bodies[actor]
            s = side(actor)
            bk = B[min(rnd // 20, 4)]
            bk[s * 8] += 1
            h = b[0]
            see = any(inview(h, c) for c in pearls)
            foe = any(side(z) != s and inview(h, bb[0]) for z, bb in bodies.items())
            if see:
                bk[s * 8 + 1] += 1
            else:
                bk[s * 8 + 3] += 1
            if foe:
                bk[s * 8 + 7] += 1
                if s == 0 and first_foe is None:
                    first_foe = rnd
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                nat = actor is None
                pearls[c] = (rnd, nat, half(c))
                if nat and rnd <= 60:
                    born[0][pearls[c][2]] += 1
            else:
                r0, nat, hf = pearls.pop(c)
                s = side(actor)
                B[min(rnd // 20, 4)][s * 8 + 2] += 1
                if first_eat[s] is None:
                    first_eat[s] = rnd
                if nat and r0 <= 60 and rnd <= 80:
                    ate[s][hf if s == 0 else hf] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                s = side(i)
                if hd in trail[i]:
                    B[min(rnd // 20, 4)][s * 8 + 4] += 1
                trail[i].append(b[0])
                b.appendleft(hd)
                look(s, hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            B[min(rnd // 20, 4)][side(parent) * 8 + 6] += 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            look(side(child), bodies[child][0])
        elif k == 11:
            i = p.i32(0)
            B[min(rnd // 20, 4)][side(i) * 8 + 5] += 1
            bodies.pop(i)
    return dict(src=label, gid=j['id'], W=W, H=H, cells=W * H, B=B, seen=seen_at, count=count_at, born=born[0], ate=ate,
                first_eat=first_eat, first_foe=first_foe, start_gap=min(gap(a, b) for a in starts[0] for b in starts[1]),
                start_n=len(starts[0]), start_len=sum(len(b) for b in [])) 


def main():
    src, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    todo = [t for n, t in enumerate(jobs(src)) if n % shards == shard]
    name = 'wo_op2-O0.jsonl'
    if src == 'L' and shard == 0:
        name = 'wo_op2-L0.jsonl'
    elif src == 'L' and shard == 1:
        name = 'wo_op2-L1.jsonl'
    elif src == 'L':
        name = 'wo_op2-L2.jsonl'
    elif src == 'R' and shard == 0:
        name = 'wo_op2-R0.jsonl'
    elif src == 'R' and shard == 1:
        name = 'wo_op2-R1.jsonl'
    elif src == 'R':
        name = 'wo_op2-R2.jsonl'
    with open(OUT + name, 'w') as f:
        for n, (label, path, j, team) in enumerate(todo):
            f.write(json.dumps(scan(label, path, j, team), separators=(',', ':')) + '\n')
            if n % 40 == 39:
                print(src, shard, n + 1, len(todo), flush=True)
    print('done', src, shard, len(todo))


main()
