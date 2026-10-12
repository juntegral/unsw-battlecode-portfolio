# Scratch (diag-opening): print what each dragon of the followed side does, turn by turn.
# Usage: python3 data/analysis/ladder/dossier/work/op_view.py <game id> <first round> <last round> [t]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path

NAMES = 'NESW'


def main():
    gid, r0, r1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    follow = sys.argv[4] if len(sys.argv) > 4 else 'u'
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    row = [r for r in rows if r['game'] == gid][0]
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    bodies, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    mine = row['side']
    side = lambda i: 'u' if teams[i] == mine else 't'
    print(row['who'], row['layout'], w, h, 'result', row['result'], 'followed side', mine)
    print('start', {i: (side(i), list(b)) for i, b in bodies.items()})
    pearls = set()
    rnd, actor, line = 0, None, None
    out = []
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            if rnd > r1:
                break
            if rnd >= r0:
                out.append('-- round %d  pearls on board %d  alive u %d t %d' % (rnd, len(pearls), sum(1 for i in bodies if side(i) == 'u'), sum(1 for i in bodies if side(i) == 't')))
        elif k == 1:
            actor = p.i32(0)
            if r0 <= rnd <= r1 and side(actor) == follow:
                b = bodies[actor]
                hx, hy = b[0]
                near = sorted((max(min(abs(px - hx), w - abs(px - hx)), min(abs(py - hy), h - abs(py - hy))), (px, py)) for px, py in pearls)
                inview = [c for d, c in near if d <= 3]
                foe = [bodies[i][0] for i in bodies if side(i) != follow and max(min(abs(bodies[i][0][0] - hx), w - abs(bodies[i][0][0] - hx)), min(abs(bodies[i][0][1] - hy), h - abs(bodies[i][0][1] - hy))) <= 3]
                out.append('   id %d L%d head %s pearls in view %s enemy heads in view %s' % (actor, len(b), b[0], inview[:4], foe[:3]))
        elif k == 4:
            a = p.pointer(0)
            if r0 <= rnd <= r1 and side(actor) == follow:
                kind = a.u16(0) if a else 2
                if kind == 0 and a.pointer(0) is not None:
                    out.append('      move ' + ''.join(NAMES[d] for d in a.pointer(0)))
                else:
                    out.append('      ' + ('split' if kind == 1 else 'none'))
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
                if r0 <= rnd <= r1 and side(actor) == follow:
                    out.append('      eats %s' % (c,))
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            if r0 <= rnd <= r1 and side(p.i32(0)) == follow:
                out.append('      split: parent %d keeps %d, child %d gets %d' % (p.i32(0), len(bodies[p.i32(0)]), p.i32(4), len(bodies[p.i32(4)])))
        elif k == 11:
            i = p.i32(0)
            if r0 <= rnd <= r1:
                out.append('      DEATH id %d side %s L%d reason %d' % (i, side(i), len(bodies[i]), p.u16(4)))
            bodies.pop(i)
    print('\n'.join(out))


main()
