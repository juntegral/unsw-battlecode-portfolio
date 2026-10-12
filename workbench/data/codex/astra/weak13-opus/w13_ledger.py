"""Ledger of the two one13 battles with losses to lower-rated teams, plus the one8 win over team 501.
Run from the repo root: python3 -B data/codex/astra/weak13-opus/w13_ledger.py > data/codex/astra/weak13-opus/ledger.txt"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from o1_scan import scan

BATTLES = ['b1508960', 'b1513119', 'b1483679']
for b in BATTLES:
    folder = Path('data/online/live-one1') / b
    for mp in sorted(folder.glob('game-*.json')):
        j = json.loads(mp.read_text())
        rp = folder / ('M%d.replay' % j['id'])
        if not rp.exists():
            print(b, j['id'], 'NO REPLAY')
            continue
        g = scan(b, rp, j)
        own = 0 if j['teamAId'] == 1119 else 1
        print('=== %s game %d map %s cells %d side %s bot %s opp %s result %s how %s last r%d elo %s' % (
            b, g['gid'], g['map'], g['cells'], 'AB'[own], g['bot'], g['opp'], g['result'], g['how'], g['last'],
            j.get('eloChange' + 'AB'[own])))
        e = g['ends']
        print('  final us n/total/longest/queen %d/%d/%d/%d  them %d/%d/%d/%d' % (*e[0][:4], *e[1][:4]))
        # behind for good: first round after which the tuple (queen, longest, total) never is >= theirs again
        snaps_all = None
        print('  r    us:n tot long Q | them:n tot long Q')
        for r, v in sorted(g['snaps'].items(), key=lambda kv: int(kv[0])):
            print('  %-4s %4d %4d %4d %3d | %4d %4d %4d %3d' % (r, *v[0][:4], *v[1][:4]))
        qd = [d for d in g['deaths'] if d[6]]
        for d in qd:
            print('  QUEEN DEATH side %s r%d L%d kind %s free %d mates5 %d foes5 %d extra %s own-turn %d head %s' % (
                'us' if d[1] == 0 else 'them', d[0], d[2], d[4], d[5], d[8], d[9], d[18], d[19], d[20]))
        qs = [s for s in g['splits'] if s[5]]
        print('  queen splits us:', [(s[0], s[2], s[3], s[4]) for s in qs if s[1] == 0][:40])
        print('  queen splits them:', [(s[0], s[2], s[3], s[4]) for s in qs if s[1] == 1][:40])
        qe = [x for x in g['eats'] if x[2] == 'q']
        print('  queen eats us %d them %d' % (sum(1 for x in qe if x[1] == 0), sum(1 for x in qe if x[1] == 1)))
        for s in (0, 1):
            ds = [d for d in g['deaths'] if d[1] == s]
            kinds = {}
            for d in ds:
                kinds[d[4]] = kinds.get(d[4], 0) + 1
            print('  deaths %s: %s' % ('us' if s == 0 else 'them', kinds))
