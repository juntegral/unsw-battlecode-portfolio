# Scratch (queen-ring brief, question 2): how far the red-team queen got in each of its games.
# Reads the red-team replays only (true state). Sealed here = at a round end her length is 23 and every tile next to
# her head is her own body or a free tile whose other neighbours are all her own body (walls ignored, so it undercounts).
# Usage: python3 data/analysis/ladder/losses/work/ring_funnel.py <shard> <shards>
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path

RED = Path('~/meow-redteam/runs')


def nb(c, W, H):
    x, y = c
    return (((x + 1) % W, y), ((x - 1) % W, y), (x, (y + 1) % H), (x, (y - 1) % H))


def one(path, side):
    root = replay.load(path).root()
    text = root.text(0)
    W = H = 0
    bodies, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'MAP':
            W, H = int(q[1]), int(q[2])
        elif q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    queen = min(i for i in teams if teams[i] == side)
    start = sum(teams[i] == side for i in teams)
    out = dict(cells=W * H, start=start, len0=len(bodies[queen]), len={}, first23=None, death=None, death_len=None,
               sealed_first=None, sealed_rounds=0, max_len=len(bodies[queen]), splits=0, eats=0)
    rnd = 0

    def round_end(r):
        b = bodies.get(queen)
        if b is None:
            return
        n = len(b)
        out['max_len'] = max(out['max_len'], n)
        if r in (25, 50, 100, 150, 200, 300, 400, 500):
            out['len'][r] = n
        if n >= 22 and out['first23'] is None:
            out['first23'] = r
        if n == 23:
            mine = set(b)
            head = b[0]
            ok = True
            for v in nb(head, W, H):
                if v in mine:
                    continue
                if any(v in bb for i, bb in bodies.items() if i != queen):
                    ok = False
                    break
                if any(u != head and u not in mine for u in nb(v, W, H)):
                    ok = False
                    break
            if ok:
                out['sealed_rounds'] += 1
                if out['sealed_first'] is None:
                    out['sealed_first'] = r

    for ev in root.pointer(3):
        kind, p = ev.u16(0), ev.pointer(0)
        if kind == 0:
            new = p.i32(0) + 1
            if new > 1:
                round_end(new - 1)
            rnd = new
        elif kind == 9:
            i = p.i32(0)
            b = bodies[i]
            before = len(b)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            if b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
            if i == queen and len(b) > before:
                out['eats'] += 1
        elif kind == 10:
            parent, child, team = p.i32(0), p.i32(4), p.u16(8)
            bodies[parent] = deque(replay.point(c) for c in p.pointer(0))
            bodies[child] = deque(replay.point(c) for c in p.pointer(1))
            teams[child] = team
            if parent == queen:
                out['splits'] += 1
        elif kind == 11:
            i = p.i32(0)
            if i == queen:
                out['death'] = rnd
                out['death_len'] = len(bodies[i])
                out['death_reason'] = p.u16(4)
            bodies.pop(i, None)
    round_end(rnd)
    res = root.pointer(4)
    out['rounds'] = rnd
    out['win'] = res.u16(4) == 1 and res.u16(6) == side
    out['their_queen_end'] = res.pointer(1 - side).i32(12)
    out['our_queen_end'] = res.pointer(side).i32(12)
    return out


def main():
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    games = []
    for p in sorted((RED / 'eval-final').glob('*/*/game.replay')):
        games.append(('final', p, int(p.parent.name.split('side-')[1])))
    for p in sorted((RED / 'eval-ringfirst').glob('*/game.replay')):
        games.append(('ringfirst', p, int(p.parent.name.split('side')[1])))
    for n, (kind, p, side) in enumerate(games):
        if n % shards != shard:
            continue
        o = one(p, side)
        name = p.parent.parent.name + '/' + p.parent.name if kind == 'final' else p.parent.name
        print('ROW', kind, name, 'cells', o['cells'], 'start', o['start'], 'len0', o['len0'], 'rounds', o['rounds'], 'win', int(o['win']),
              'len@', ' '.join('%d:%d' % kv for kv in sorted(o['len'].items())), 'max', o['max_len'], 'first22', o['first23'],
              'death', o['death'], 'dlen', o['death_len'], 'dreason', o.get('death_reason'), 'sealed_first', o['sealed_first'],
              'sealed_rounds', o['sealed_rounds'], 'qsplits', o['splits'], 'qeats', o['eats'],
              'queens_end', o['our_queen_end'], o['their_queen_end'], flush=True)


main()
