#!/usr/bin/env python3
"""Deterministic event fixture and independent real-replay pearl recount."""
import sys
sys.dont_write_bytecode = True
import json
from collections import Counter
from pathlib import Path
import spawn
from replay_format import point


class Wire:
    def __init__(self, values=None, pointers=None, text=''):
        self.values = values or {}
        self.pointers = pointers or {}
        self.string = text
    def i32(self, off):
        return self.values.get(off, 0)
    u16 = u32 = i32
    def bit(self, off):
        return bool(self.i32(off))
    def pointer(self, off):
        return self.pointers.get(off)
    def text(self, off):
        return self.string


def xy(x, y):
    return Wire({0: x, 4: y})


def event(kind, value=0, tile=None, tail=None, reason=None):
    vals = {0: value}
    if reason is not None:
        vals[4] = reason
    ptrs = {0: xy(*tile)} if tile is not None else {}
    if tail is not None:
        ptrs[1] = xy(*tail)
    return Wire({0: kind}, {0: Wire(vals, ptrs)})


def fixture():
    text = ('MAP 5 5\nTILE 2 1 1 2\nTILE 3 1 3 3\nTILE 1 0 3 3\n'
            'DRAGON 0 2 1 1 0 1\nDRAGON 1 2 4 4 3 4\n')
    ev = [event(2, 2, (2, 1)), event(2, 3, (3, 1)), event(2, 3, (1, 0)),
          event(0, 0), event(1, 0), event(9, 0, (2, 1), (1, 1)), event(1, 1),
          event(0, 1), event(2, 1, (2, 1)), event(1, 0), event(9, 0, (2, 2), (2, 1)), event(1, 1),
          event(0, 2), event(2, 1, (2, 1)), event(3, 1, (3, 1)), event(2, 3, (3, 1)), event(3, 1, (1, 0)), event(2, 3, (1, 0)),
          event(1, 0), event(9, 0, (1, 2), (2, 2)), event(1, 1),
          event(0, 3), event(3, 1, (2, 1)), event(2, 1, (2, 1)), event(1, 0),
          event(9, 0, (1, 1), (1, 2)), event(3, 0, (2, 1)), event(9, 0, (2, 1), (1, 2)),
          event(1, 1), event(11, 1, reason=0), event(3, 1, (4, 4))]
    result = Wire({0: 1, 4: 1, 6: 0}, {0: Wire({0: 1, 4: 3, 8: 3}), 1: Wire()})
    root = Wire(pointers={3: ev, 4: result}, text=text)
    original = spawn.read
    spawn.read = lambda _: root
    local = spawn.HERE/'spawn-fixture.map'
    local.write_text(text)
    try:
        row = spawn.scan(spawn.HERE/'spawn-fixture.replay', ('fixture', 0, 0), local)
    finally:
        spawn.read = original
        local.unlink()
    c = row['measures'][0]
    assert c['case1'] == 2 and c['on1'] == 1, c
    assert c['case2'] == 1 and c.get('on2', 0) == 0, c
    assert c['two_cases'] == 1 and c['two_born'] == 1, c
    assert c['blocked'] == 2 and c['blocked_head'] == 1 and c['blocked_trail'] == 1, c
    assert c['born_all'] == 3 and c['eaten_all'] == 1 and c['instant_all'] == 1, c
    assert c['wait_all'] == 0 and c['alive100'] == 1 and c['longest'] == 3
    assert row['measures'][1]['wall'] == 1 and row['measures'][1]['alive300'] == 0
    return 'Fixture: c1/c2 opportunities, substeps, head/trail failed attempts, distance-2 birth, instant eating, death drops, death causes and terminal checkpoints passed.'


def independent(row):
    root = spawn.read(Path(row['replay']))
    teams = {}
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            teams[len(teams)] = int(q[1])
    present, stats = {}, [Counter(), Counter()]
    rnd, actor = -1, None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 10):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
        elif k == 10:
            teams[p.i32(4)] = p.u16(8)
        elif k == 3:
            c = point(p.pointer(0))
            if p.u32(0):
                natural = actor is None
                present[c] = (rnd, natural)
                if natural:
                    for win, (lo, hi) in spawn.WINDOWS.items():
                        if lo <= rnd <= hi:
                            for st in stats:
                                st['born_'+win] += 1
            else:
                birth, natural = present.pop(c)
                if natural:
                    st = stats[int(teams[actor] != row['side'])]
                    for win, (lo, hi) in spawn.WINDOWS.items():
                        if lo <= rnd <= hi:
                            st['eaten_'+win] += 1
                        if lo <= birth <= hi:
                            st['cohort_eaten_'+win] += 1
                            st['instant_'+win] += int(rnd == birth)
                            st['wait_'+win] += rnd-birth
    for s in (0, 1):
        for name, value in stats[s].items():
            assert row['measures'][s].get(name, 0) == value, (row['replay'], s, name)


def main():
    lines = [fixture()]
    cache = {}
    for line in spawn.CACHE.read_text().splitlines():
        row = json.loads(line)
        cache[row['replay']] = row
    selected = [next(r for r in cache.values() if r['arm'] == a) for a in ('m2base', 'm2all4')]
    for row in selected:
        independent(row)
        lines.append('Independent natural-birth/eating/cohort recount passed: '+row['replay'])
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
