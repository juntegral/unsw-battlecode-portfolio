"""Losses of our dragons of length >= MINL in a round range: deaths (cause, attacker length / steps / distance / eaten on the way)
and splits, plus our deaths by cause and length class in the range.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_big.py <battle> <gid> <r0> <r1> [minL=10]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path

battle, gid, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
MINL = int(sys.argv[5]) if len(sys.argv) > 5 else 10
folder = Path('data/online/live-one1') / battle
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
REASON = ('wall', 'own body', 'body', 'head', 'stop')


def gap(a, b):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


rnd = -1
turn = None
kinds = Counter()
print('%d %s r%d-%d, our dragons of %d or longer' % (gid, j['mapName'], r0, r1, MINL))
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 4, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
        if rnd > r1:
            break
    elif k == 1:
        a = p.i32(0)
        turn = dict(i=a, L=len(bodies[a]), h=bodies[a][0], e=0, steps=0, act='none')
    elif k == 4:
        a = p.pointer(0)
        if a is not None and a.u16(0) == 0 and a.pointer(0) is not None:
            turn['act'] = ''.join('NESW'[x] for x in a.pointer(0))
    elif k == 3:
        if not p.u32(0) and turn:
            turn['e'] += 1
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
            if turn and i == turn['i']:
                turn['steps'] += 1
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        par, ch = p.i32(0), p.i32(4)
        L0 = len(bodies[par])
        for z, i in enumerate((par, ch)):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
        if teams[par] == own and L0 >= MINL and r0 <= rnd <= r1:
            print('  r%d #%d L%d splits -> keeps %d, child #%d %d' % (rnd, par, L0, len(bodies[par]), ch, len(bodies[ch])))
    elif k == 11:
        i, reason = p.i32(0), p.u16(4)
        L = len(bodies[i])
        if teams[i] == own and r0 <= rnd <= r1:
            mine = turn['i'] == i
            cls = '2-3' if L <= 3 else '4-9' if L <= 9 else '10+'
            what = REASON[reason] if mine and reason != 3 else 'rams' if mine else 'rammed' if reason == 3 else REASON[reason]
            kinds[cls, what] += 1
            if L >= MINL:
                if mine:
                    print('  r%d #%d L%d dies on its own turn: %s, order "%s" after %d steps from %s' % (rnd, i, L, REASON[reason], turn['act'], turn['steps'], turn['h']))
                else:
                    t = turn
                    print('  r%d #%d L%d rammed at %s by #%d (%s) L%d from %s, %d steps (free %d), ate %d on the way, distance %d, order "%s"' % (
                        rnd, i, L, bodies[i][0], t['i'], 'theirs' if teams[t['i']] != own else 'OURS', t['L'], t['h'], t['steps'] + 1,
                        -(-t['L'] // 4), t['e'], gap(t['h'], bodies[i][0]), t['act']))
        bodies.pop(i)
print('  our deaths by length class and cause:', sorted(kinds.items()))
