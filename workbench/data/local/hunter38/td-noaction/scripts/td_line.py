#!/usr/bin/env python3
"""One line per game: winner, units at end of round 400, no-action deaths per team with first round, queen fates.
Usage: td_line.py REPLAY..."""
import sys, os
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness'))
import replay
NONE = replay.DEATH_REASONS[4]
EN = dict(zip(replay.DEATH_REASONS, ('wall', 'self', 'body', 'headon', 'no-action')))
print('%-28s %-7s %-7s %3s | %-13s | %-13s | %-17s | %-17s | %s' % ('game', 'A', 'B', 'win', 'units r400 A:B', 'longest A:B', 'no-action A (first)', 'no-action B (first)', 'queen A / queen B'))
for path in sys.argv[1:]:
    info, events, team_of = replay.parse(path)
    length = {}
    for line in info['map'].splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            length[len(length)] = int(p[2])
    snap = None
    last = 0
    for e in events:
        if snap is None and e['round'] > 400:
            snap = dict(length)
        if e['kind'] == 'update': length[e['id']] = e['length']
        elif e['kind'] == 'split': length[e['id']] = e['parentLength']; length[e['child']] = e['childLength']
        elif e['kind'] == 'death': length.pop(e['id'], None)
        last = e['round']
    if snap is None: snap = {}
    def side(t):
        ls = [l for d, l in snap.items() if team_of.get(d) == t]
        return len(ls), max(ls, default=0)
    a, b = side('A'), side('B')
    none = [e for e in events if e['kind'] == 'death' and e['reason'] == NONE]
    def na(t):
        r = [e['round'] for e in none if e['team'] == t]
        return '%d (%s)' % (len(r), min(r) if r else '-')
    def q(i):
        d = [e for e in events if e['kind'] == 'death' and e['id'] == i]
        return 'r%d %s' % (d[0]['round'], EN[d[0]['reason']]) if d else 'alive'
    print('%-28s %-7s %-7s %3s | %13s | %13s | %-17s | %-17s | %s / %s' % (os.path.basename(path).replace('.replay', ''), os.path.basename(info['botA'])[:7], os.path.basename(info['botB'])[:7], (info['winner'] or '-') + ('' if last >= 499 else '*'),
          '%d:%d' % (a[0], b[0]), '%d:%d' % (a[1], b[1]), na('A'), na('B'), q(0), q(1)))
print('* = ended before round 500 (one side wiped out)')
