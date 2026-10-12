#!/usr/bin/env python3
"""Units, longest and queen length per team at chosen rounds, plus identity checks.
Usage: td_state.py REPLAY...   |   td_state.py --same A.replay B.replay"""
import sys, os
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness'))
import replay

def strip(events):
    return [tuple(sorted((k, v) for k, v in e.items() if k != 'text')) for e in events if e['kind'] != 'log']

if sys.argv[1] == '--same':
    a = replay.parse(sys.argv[2])[1]; b = replay.parse(sys.argv[3])[1]
    print(os.path.basename(sys.argv[2]), 'vs', os.path.basename(sys.argv[3]), 'events', len(strip(a)), len(strip(b)), 'identical' if strip(a) == strip(b) else 'DIFFERENT')
    sys.exit()

MARKS = (100, 200, 300, 400, 402, 403, 450, 499)
for path in sys.argv[1:]:
    info, events, team_of = replay.parse(path)
    length = {}
    for line in info['map'].splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            length[len(length)] = int(p[2])
    out = {}
    cur = 0
    def snap(r):
        row = {}
        for t in 'AB':
            ls = [l for d, l in length.items() if team_of.get(d) == t]
            q = 0 if t == 'A' else 1
            row[t] = (len(ls), max(ls, default=0), sum(ls), length.get(q, 0))
        out[r] = row
    marks = list(MARKS)
    for e in events:
        while marks and e['round'] > marks[0]:
            snap(marks.pop(0))
        if e['kind'] == 'update':
            length[e['id']] = e['length']
        elif e['kind'] == 'split':
            length[e['id']] = e['parentLength']; length[e['child']] = e['childLength']
        elif e['kind'] == 'death':
            length.pop(e['id'], None)
    while marks:
        snap(marks.pop(0))
    print(os.path.basename(path), ' A =', os.path.basename(info['botA']), ' B =', os.path.basename(info['botB']))
    print('   end of round | A units longest total queen | B units longest total queen')
    for r in MARKS:
        a, b = out[r]['A'], out[r]['B']
        print('   %12d | %7d %7d %5d %5d | %7d %7d %5d %5d' % (r, *a, *b))
