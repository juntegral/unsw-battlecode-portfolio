"""Scratch (diag-attack): sums the independent recount (at_rc-*.json) for comparison with the last table of at_more.py."""
import json
from collections import Counter
from pathlib import Path

D = Path('data/analysis/ladder/dossier/work')
tot = Counter()
for n in range(4):
    for k, v in json.loads((D / ('at_rc-%d.json' % n)).read_text()):
        tot[tuple(k) if isinstance(k, list) else k] += v
print('games', tot['games'])
print('who, class, meetings, mover length, victim length, drops, eaten by mover side, by victim side')
for k in ('they', 'we'):
    for tag in ('all', 'big'):
        print('  %-4s %-3s %6d %7d %7d %7d %7d %7d' % (k, tag, tot[(k, tag, 'n')], tot[(k, tag, 'Lm')], tot[(k, tag, 'Lv')], tot[(k, tag, 'drops')], tot[(k, tag, 'eat_m')], tot[(k, tag, 'eat_v')]))
