# Scratch (queen-ring brief, question 2c): layouts whose queen spawns long or trapped: what happens to her now.
# Reads rows.jsonl and maps.json; prints. Usage: python3 data/analysis/ladder/losses/work/ring_spawn.py
import json
from collections import Counter
from pathlib import Path
from statistics import median

ROOT = Path('data/analysis/ladder')
maps = json.loads((ROOT / 'maps.json').read_text())
rows = [json.loads(x) for x in (ROOT / 'rows.jsonl').read_text().splitlines()]
rows = [r for r in rows if r['our_code'] == 'main']
RING = 23
for key, m in maps.items():
    if m['queen_spawn_length'] < RING:
        continue
    g = [r for r in rows if r['map_key'] == key]
    full = [r for r in g if r['last_round'] == 499]
    print('layout with queen spawn length', m['queen_spawn_length'], '| dragons a side at spawn', m['dragons_at_spawn'], '| spawn room', m['queen_spawn_room'],
          '| games', len(g), dict(Counter(r['result'] for r in g)), '| full', len(full), dict(Counter(r['queens_at_end'] for r in full)))
    for side in ('us', 'them'):
        q = [r['queen'][side] for r in g]
        d = sorted(x['death_round'] for x in q if x['death_round'] is not None)
        print('  ', side, 'queen died in', len(d), 'of', len(q), '| median round', median(d) if d else '-',
              '| death length', dict(Counter(x['death_length'] for x in q if x['death_round'] is not None).most_common(8)))
        for k in ('50', '100', '200', 'end'):
            a = [r['curves'][k][side]['queen_length'] for r in g if r['curves'].get(k) and r['curves'][k][side]['queen_alive']]
            print('      r%s: alive %d, length median %s, min %s, max %s' % (k, len(a), median(a) if a else '-', min(a) if a else '-', max(a) if a else '-'))
    lost = [r for r in full if r['result'] == 'loss']
    theirs = sorted(r['final']['them']['queen_length'] for r in lost)
    print('   full losses', len(lost), '| our queen dead at the end in', sum(r['final']['us']['queen_length'] == 0 for r in lost),
          '| their queen at the end', theirs, '| dead or under %d: %d' % (RING, sum(n < RING for n in theirs)))

print()
print('our queen died at %d or longer, all main games:' % RING)
n = turn = 0
for r in rows:
    q = r['queen']['us']
    if q['death_round'] is None or q['death_length'] < RING:
        continue
    n += 1
    by_rule = r['result'] == 'loss' and r['last_round'] == 499 and r['final']['them']['queen_length'] < RING
    turn += by_rule
    print('   game', r['game'], 'spawn length', maps[r['map_key']]['queen_spawn_length'], 'round', q['death_round'], 'length', q['death_length'], q['death_cause'],
          r['result'], r['ended_by'], 'their queen at end', r['final']['them']['queen_length'], '| turned by a living queen of %d: %s' % (RING, by_rule))
print('   total', n, 'of', len(rows), 'games | losses that turn by rule', turn, 'of', sum(r['result'] == 'loss' for r in rows))
