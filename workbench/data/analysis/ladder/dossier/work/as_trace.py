"""Scratch (diag-aahsplit): turn-by-turn trace of one dragon (and the children it splits off) in one game.
Usage: python3 as_trace.py <gid> <dragon id> <first round> <last round> [follow children: 0/1]"""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'
CAUSE = ('wall', 'own body', 'another body', 'head-on', 'no valid action')
DN = 'NESW'


def main():
    gid, did, r0, r1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    follow = len(sys.argv) > 5 and sys.argv[5] == '1'
    rows = [json.loads(x) for x in Path(WORKREL + 'as_index.jsonl').read_text().splitlines()]
    meta = [x for x in rows if x['gid'] == gid][0]
    print(gid, meta['map'], 'A', meta['an'], 'B', meta['bn'], 'winner', meta['win'])
    root = replay.load(Path(meta['path'])).root()
    lines = root.text(0).splitlines()
    w, h = map(int, lines[0].split()[1:3])
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    watch = {did}
    rnd, actor = 0, None
    line = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1) and line:
            print(line)
            line = None
        if k == 0:
            rnd = p.i32(0)
            if rnd > r1:
                break
        elif k == 1:
            actor = p.i32(0)
            if actor in watch and rnd >= r0:
                b = bodies[actor]
                tm = teams[actor]
                line = 'r%d id %d len %d head %s tail %s alive %d:' % (rnd, actor, len(b), b[0], b[-1], sum(1 for j in bodies if teams[j] == tm))
        elif k == 4:
            if line:
                a = p.pointer(0)
                akind = a.u16(0) if a else 2
                dirs = list(a.pointer(0)) if a and akind == 0 and a.pointer(0) is not None else []
                line += ' ' + ('move ' + ''.join(DN[d] for d in dirs) if akind == 0 else 'SPLIT' if akind == 1 else 'none')
        elif k == 3:
            if line and not p.u32(0):
                line += ' eats %s' % (replay.point(p.pointer(0)),)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            lp = len(bodies[parent])
            bodies[parent] = deque(replay.point(z) for z in p.pointer(0))
            bodies[child] = deque(replay.point(z) for z in p.pointer(1))
            teams[child] = p.u16(8)
            if parent in watch and rnd >= r0:
                if line:
                    line += ' -> %d keeps %d, child %d of %d at %s' % (lp, len(bodies[parent]), child, len(bodies[child]), bodies[child][0])
                if follow:
                    watch.add(child)
        elif k == 11:
            i = p.i32(0)
            if i in watch and rnd >= r0:
                msg = ' DIES (%s) len %d at %s' % (CAUSE[p.u16(4)], len(bodies[i]), bodies[i][0])
                if line and i == actor:
                    line += msg
                else:
                    print('r%d id %d%s during the turn of %s' % (rnd, i, msg, actor))
            bodies.pop(i)
    if line:
        print(line)


main()
