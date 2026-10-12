"""Per-turn trace of one side (or chosen dragons) over a round range.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_trace.py <battle> <gid> <r0> <r1> [us|them|all] [ids comma] [maxlines]
One line a turn: round, id, side, length before, head before, action (dirs / split / none), head after, length after, eats, deaths in turn,
nearest enemy head (torus manhattan) at turn start."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

battle, gid, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
who = sys.argv[5] if len(sys.argv) > 5 else 'us'
only = set(int(x) for x in sys.argv[6].split(',')) if len(sys.argv) > 6 and sys.argv[6] != '-' else None
folder = Path('data/online/live-one1') / battle if not battle.startswith('data/') else Path(battle)
j = json.loads((folder / ('game-%d.json' % gid)).read_text())
root = replay.load(folder / ('M%d.replay' % gid)).root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams = {}, {}
for line in lines:
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = int(q[1])
own = 0 if j['teamAId'] == 1119 else 1
REASON = {0: 'wall', 1: 'ownbody', 2: 'body', 3: 'head', 4: 'stop'}


def gap(a, b):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


rnd = -1
cur = None


def flush():
    global cur
    if cur is None:
        return
    i = cur['i']
    mine = cur['team'] == own
    show = r0 <= cur['r'] <= r1 and (who == 'all' or (who == 'us') == mine) and (only is None or i in only)
    if show:
        b = bodies.get(i)
        print('r%-3d #%-4d %s L%-2d %s %-14s -> %s L%s eat %d %s | foe %s' % (
            cur['r'], i, 'us' if mine else 'TH', cur['L'], cur['h'], cur['act'], b[0] if b else 'DEAD', len(b) if b else 0,
            cur['e'], ' '.join(cur['dead']), cur['foe']))
    cur = None


for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 4, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        flush()
        rnd = p.i32(0)
        if rnd > r1:
            break
    elif k == 1:
        flush()
        a = p.i32(0)
        b = bodies[a]
        foes = sorted((gap(b[0], bb[0]), z, len(bb)) for z, bb in bodies.items() if teams[z] != teams[a])[:2]
        cur = dict(i=a, r=rnd, team=teams[a], L=len(b), h=b[0], act='none', e=0, dead=[], foe=foes)
    elif k == 4:
        a = p.pointer(0)
        if a is not None:
            t = a.u16(0)
            if t == 0:
                d = list(a.pointer(0)) if a.pointer(0) is not None else []
                cur['act'] = 'mv ' + ''.join('NESW'[x] for x in d)
            else:
                cur['act'] = 'act%d' % t
        if p.bit(32):
            cur['act'] += ' TIMEOUT'
    elif k == 3:
        if not p.u32(0) and cur is not None:
            cur['e'] += 1
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        par, ch = p.i32(0), p.i32(4)
        for z, i in enumerate((par, ch)):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
        if cur is not None:
            cur['act'] = 'split->%d+%d(#%d)' % (len(bodies[par]), len(bodies[ch]), ch)
    elif k == 11:
        i, reason = p.i32(0), p.u16(4)
        if cur is not None:
            cur['dead'].append('X#%d(%s L%d %s)' % (i, 'us' if teams[i] == own else 'TH', len(bodies[i]), REASON.get(reason, reason)))
        bodies.pop(i)
flush()
