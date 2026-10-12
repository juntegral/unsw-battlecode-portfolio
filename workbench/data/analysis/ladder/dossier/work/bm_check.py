"""Scratch (diag-bigmap): recount of the headline cells with the shared reader (tools/ladder_replay.py), not my
state machine: games, wins, deciding rule, rams each way and their length, dragons and longest at r300, queens alive
at r150 and the end, natural and dropped pearls, for the online games above 1200 cells.
Usage: python3 data/analysis/ladder/dossier/work/bm_check.py"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
import ladder_replay
from pathlib import Path
from statistics import median

LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2')
BIG = ('Australia', 'Islands', 'Around UNSW', 'Schooltime', 'Slithery Fight')
acc = {}
for label in LABELS:
    folder = Path('data/online/smoke') / (label + '-new')
    if not folder.is_dir():
        continue
    arm = 'MAIN' if label.startswith('agg7-m') else 'NEW'
    for mp in sorted(folder.glob('game-*.json')):
        j = json.loads(mp.read_text())
        rp = folder / ('M%d.replay' % j['id'])
        if not rp.exists() or j['mapName'] not in BIG:
            continue
        g = ladder_replay.scan(rp, j, label, set())
        W, H = map(int, g['text'].splitlines()[0].split()[1:3])
        assert W * H > 1200
        a = acc.setdefault(arm, dict(n=0, won=0, on_us=0, on_them=0, len_us=0, len_them=0, c300=[], t300=[], l300=[], lt300=[], q150=0, qt150=0, qe=0, qte=0, nat=0, natt=0, drop=0, dropt=0, dec=dict(Q=0, L=0, T=0, E=0)))
        a['n'] += 1
        ours = g['ours']
        a['won'] += int(g['winner'] == ours)
        for c in g['collisions']:
            if not c['cross_team']:
                continue
            ds = [d for d in g['deaths'] if d['collision'] == c['collision']]
            victim = [d for d in ds if d['id'] != d['actor']][0]
            if victim['side'] == 'us':
                a['on_us'] += 1
                a['len_us'] += victim['length']
            else:
                a['on_them'] += 1
                a['len_them'] += victim['length']
        last = g['last_round']
        s300 = g['snapshots'][min(300, last)]
        s150 = g['snapshots'][min(150, last)]
        f = g['final']
        a['c300'].append(s300['us']['alive'])
        a['t300'].append(s300['them']['alive'])
        a['l300'].append(s300['us']['longest'])
        a['lt300'].append(s300['them']['longest'])
        a['q150'] += int(s150['us']['queen_alive'])
        a['qt150'] += int(s150['them']['queen_alive'])
        a['qe'] += int(f['us']['queen_alive'])
        a['qte'] += int(f['them']['queen_alive'])
        a['nat'] += g['eats']['us']['spawn']
        a['natt'] += g['eats']['them']['spawn']
        a['drop'] += g['eats']['us']['drop']
        a['dropt'] += g['eats']['them']['drop']
        u, t = f['us'], f['them']
        k = 'E' if u['alive'] == 0 or t['alive'] == 0 else 'Q' if u['queen_length'] != t['queen_length'] else 'L' if u['longest'] != t['longest'] else 'T'
        a['dec'][k] += 1
for arm, a in sorted(acc.items()):
    n = a['n']
    print(arm, 'games', n, 'won', a['won'], '| rammed a game %.1f, length %.0f | we ram %.1f, length %.0f' % (a['on_us'] / n, a['len_us'] / n, a['on_them'] / n, a['len_them'] / n),
          '| dragons r300 median %g v %g | longest r300 %g v %g' % (median(a['c300']), median(a['t300']), median(a['l300']), median(a['lt300'])),
          '| queen alive r150 %d v %d, end %d v %d' % (a['q150'], a['qt150'], a['qe'], a['qte']),
          '| natural %.0f v %.0f, dropped %.0f v %.0f' % (a['nat'] / n, a['natt'] / n, a['drop'] / n, a['dropt'] / n), '| decided', a['dec'])
