# Scratch (queen-ring brief, questions 2 and 5): more ladder counts on the queen. Reads rows.jsonl, maps.json; prints.
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import median

ROOT = Path('data/analysis/ladder')
maps = json.loads((ROOT / 'maps.json').read_text())
rows = [json.loads(line) for line in (ROOT / 'rows.jsonl').read_text().splitlines()]
CODE = sys.argv[1] if len(sys.argv) > 1 else 'main'
rows = [r for r in rows if r['our_code'] == CODE and not maps[r['map_key']]['queen_spawn_dead_end']]
full = [r for r in rows if r['last_round'] == 499]
print(CODE, 'games with a queen free to leave spawn', len(rows), 'full', len(full))

a300 = [r for r in full if r['curves']['300']['us']['queen_alive']]
dead = [r for r in a300 if not r['curves']['end']['us']['queen_alive']]
live = [r for r in a300 if r['curves']['end']['us']['queen_alive']]
print('queen alive at r300 in full games:', len(a300), '| alive at end', len(live), dict(Counter(r['result'] for r in live)),
      '| dead at end', len(dead), dict(Counter(r['result'] for r in dead)))
print('   the dead: death length', sorted(r['queen']['us']['death_length'] for r in dead))
print('   the dead: death round', sorted(r['queen']['us']['death_round'] for r in dead))
print('   the dead: cause', dict(Counter(r['queen']['us']['death_cause'] for r in dead)))
print('   the dead and lost: their queen at end', sorted(r['final']['them']['queen_length'] for r in dead if r['result'] == 'loss'))

long_dead = [r for r in rows if r['queen']['us']['death_round'] is not None and r['queen']['us']['death_length'] >= 10]
print('our queen died at length 10 or more:', len(long_dead))
for r in long_dead:
    q = r['queen']['us']
    print('   game', r['game'], 'round', q['death_round'], 'length', q['death_length'], q['death_cause'], r['result'], r['ended_by'],
          'their queen at end', r['final']['them']['queen_length'])

both = [r for r in full if r['queens_at_end'] == 'both alive']
print('full games, both queens alive at the end:', len(both), dict(Counter(r['result'] for r in both)))
cap = 23
won = [r for r in both if r['final']['us']['queen_length'] > r['final']['them']['queen_length']]
print('   ours longer: %d; of these theirs at %d or more (a queen held at %d would not win them): %d'
      % (len(won), cap, cap, sum(r['final']['them']['queen_length'] >= cap for r in won)))
print('   our length, their length (ours longer):', sorted((r['final']['us']['queen_length'], r['final']['them']['queen_length']) for r in won))
only = [r for r in full if r['queens_at_end'] == 'only ours']
print('full games, only our queen alive:', len(only), dict(Counter(r['result'] for r in only)),
      'her length', sorted(r['final']['us']['queen_length'] for r in only))

for key in ('100', '150', '200'):
    g = [r for r in rows if r['curves'].get(key) and r['curves'][key]['us']['queen_alive']]
    fullg = [r for r in g if r['last_round'] == 499]
    print('queen alive at r%s: %d games | reach round 500: %d | of those her end state: alive %d, dead %d | their queen dead or under %d at end: %d'
          % (key, len(g), len(fullg), sum(r['final']['us']['queen_length'] > 0 for r in fullg), sum(r['final']['us']['queen_length'] == 0 for r in fullg),
             cap, sum(r['final']['them']['queen_length'] < cap for r in fullg)))
    lost = [r for r in fullg if r['result'] == 'loss' and r['final']['them']['queen_length'] < cap]
    print('      lost full games among them with their queen dead or under %d: %d' % (cap, len(lost)))

q = [r for r in rows]
tot_len = {}
for key in ('100', '150', '200', '300'):
    t = [r['curves'][key]['us'] for r in q if r['curves'].get(key)]
    print('r%s team: total length median %s, dragons median %s, longest median %s'
          % (key, median(s['total'] for s in t), median(s['alive'] for s in t), median(s['longest'] for s in t)))
big = [r for r in rows if maps[r['map_key']]['width'] * maps[r['map_key']]['height'] > 1200]
print('layouts above 1200 cells:', len(big), 'games; at or below:', len(rows) - len(big))
for name, g in (('above 1200', big), ('at or below 1200', [r for r in rows if r not in big])):
    for key in ('100', '200', '300'):
        t = [r for r in g if r['curves'].get(key)]
        alive = sum(r['curves'][key]['us']['queen_alive'] for r in t)
        print('   %s: our queen alive at r%s in %d of %d' % (name, key, alive, len(t)))
two = [r for r in rows if maps[r['map_key']]['dragons_at_spawn'] == 2]
print('games on layouts with 2 dragons a side at spawn:', len(two), '| queen splits there mean %.2f, elsewhere %.2f'
      % (sum(r['queen']['us']['splits'] for r in two) / max(1, len(two)),
         sum(r['queen']['us']['splits'] for r in rows if r not in two) / max(1, len(rows) - len(two))))
