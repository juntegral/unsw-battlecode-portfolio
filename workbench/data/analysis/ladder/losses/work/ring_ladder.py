# Scratch (queen-ring brief, questions 2 and 5): what the ladder says about our queen's length, eating and death,
# and about their queen at the end. Reads rows.jsonl and maps.json only; prints.
# Usage: python3 data/analysis/ladder/losses/work/ring_ladder.py [code, default main]
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import median

ROOT = Path('data/analysis/ladder')
maps = json.loads((ROOT / 'maps.json').read_text())
rows = [json.loads(line) for line in (ROOT / 'rows.jsonl').read_text().splitlines()]
CODE = sys.argv[1] if len(sys.argv) > 1 else 'main'
rows = [r for r in rows if r['our_code'] == CODE]
RING = 23


def bucket(r):
    end, q = r['ended_by'], r['queens_at_end']
    if end == 'elimination' and r['final']['us']['alive'] == 0:
        return 'E1' if r['last_round'] <= 125 else 'E2'
    if end == 'queen rule' and q == 'only theirs':
        return 'Q1' if r['final']['us']['longest'] >= r['final']['them']['longest'] else 'Q2'
    if end == 'queen rule' and q == 'both alive' and r['final']['us']['queen_length'] < r['final']['them']['queen_length']:
        return 'Q3'
    if q == 'both dead' and end in ('longest dragon', 'total length'):
        return 'L1'
    return 'Other'


def band(n):
    return '2-3' if n <= 3 else '4-9' if n <= 9 else '10-22' if n < RING else '23+'


for r in rows:
    m = maps[r['map_key']]
    r['_cells'] = m['width'] * m['height']
    r['_vault'] = bool(m['queen_spawn_dead_end'])
    r['_qlen0'] = m['queen_spawn_length']
    r['_two'] = m['dragons_at_spawn']
    r['_full'] = r['last_round'] == 499

print(CODE, 'games', len(rows), 'wins', sum(r['result'] == 'win' for r in rows), 'losses', sum(r['result'] == 'loss' for r in rows))
print('layouts by queen spawn length:', dict(Counter((maps[k]['queen_spawn_length'], maps[k]['dragons_at_spawn'], bool(maps[k]['queen_spawn_dead_end'])) for k in maps)),
      '(length, dragons per side at spawn, trapped at spawn)')
print('games on layouts where the queen is trapped at spawn:', sum(r['_vault'] for r in rows), '| queen spawn length over 3:', sum(r['_qlen0'] > 3 for r in rows))
free = [r for r in rows if not r['_vault']]
full = [r for r in rows if r['_full']]
print('full games (round 500 reached):', len(full), dict(Counter(r['queens_at_end'] for r in full)))
print('full games, queen free to leave spawn:', sum(not r['_vault'] for r in full), dict(Counter(r['queens_at_end'] for r in full if not r['_vault'])))

print('\n== our queen, layouts where she can leave spawn (%d games) ==' % len(free))
for side in ('us', 'them'):
    print(' side', side)
    for key in ('50', '100', '150', '200', '300', '400', 'end'):
        snaps = [r['curves'][key][side] for r in free if r['curves'].get(key)]
        alive = [s['queen_length'] for s in snaps if s['queen_alive']]
        c = Counter(band(n) for n in alive)
        print('   r%-3s games %3d | queen alive %3d (%.0f%%) | length of the living: median %s, max %s | 2-3: %d, 4-9: %d, 10-22: %d, 23+: %d'
              % (key, len(snaps), len(alive), 100 * len(alive) / max(1, len(snaps)), median(alive) if alive else '-', max(alive) if alive else '-',
                 c['2-3'], c['4-9'], c['10-22'], c['23+']))
    q = [r['queen'][side] for r in free]
    lived = [(x['death_round'] if x['death_round'] is not None else r['last_round']) + 1 for x, r in zip(q, free)]
    eaten = [x['pearls_eaten'] for x in q]
    splits = [x['splits'] for x in q]
    print('   whole game: pearls eaten by the queen: total %d, per game mean %.2f median %s | splits mean %.2f median %s'
          % (sum(eaten), sum(eaten) / len(q), median(eaten), sum(splits) / len(q), median(splits)))
    print('   rounds she lived: total %d, median %s | pearls per 100 rounds alive: %.2f | rounds per pearl: %.1f'
          % (sum(lived), median(lived), 100 * sum(eaten) / sum(lived), sum(lived) / max(1, sum(eaten))))
    early = [(x, n, r) for x, n, r in zip(q, lived, free) if n <= 100]
    print('   games in which she lived 100 rounds or fewer: %d, her pearls per 100 rounds there %.2f'
          % (len(early), 100 * sum(x['pearls_eaten'] for x, n, r in early) / max(1, sum(n for x, n, r in early))))
    dead = [x for x in q if x['death_round'] is not None]
    dr = sorted(x['death_round'] for x in dead)
    print('   died in %d of %d games | by r25 %d, r50 %d, r100 %d, r150 %d, r200 %d, r300 %d | death length: %s | cause: %s'
          % (len(dead), len(q), sum(d <= 25 for d in dr), sum(d <= 50 for d in dr), sum(d <= 100 for d in dr), sum(d <= 150 for d in dr),
             sum(d <= 200 for d in dr), sum(d <= 300 for d in dr),
             dict(Counter(band(x['death_length']) for x in dead)), dict(Counter(x['death_cause'] for x in dead))))

print('\n== our queen once she is the fed leader (round 300 on; main.cpp:522-526, 1776) ==')
a300 = [r for r in free if r['curves'].get('300') and r['curves']['300']['us']['queen_alive'] and r['_full']]
print('   full games with our queen alive at r300:', len(a300))
for key in ('300', '400', 'end'):
    alive = [r['curves'][key]['us']['queen_length'] for r in a300 if r['curves'][key]['us']['queen_alive']]
    c = Counter(band(n) for n in alive)
    print('   r%-3s alive %3d | median %s max %s | 2-3: %d, 4-9: %d, 10-22: %d, 23+: %d'
          % (key, len(alive), median(alive) if alive else '-', max(alive) if alive else '-', c['2-3'], c['4-9'], c['10-22'], c['23+']))
print('   of these, result:', dict(Counter(r['result'] for r in a300)),
      '| queen dead at the end:', sum(not r['curves']['end']['us']['queen_alive'] for r in a300))

print('\n== their queen at the end of full games (a sealed queen of %d wins the queen rule only if theirs is dead or shorter) ==' % RING)
for label, group in (('all full games', full), ('full games we lost', [r for r in full if r['result'] == 'loss']),
                     ('full games we won', [r for r in full if r['result'] == 'win'])):
    t = [r['final']['them']['queen_length'] for r in group]
    print('   %-20s %3d | their queen dead %d, alive and under %d: %d, exactly %d: %d, longer: %d | longest seen %s'
          % (label, len(t), sum(n == 0 for n in t), RING, sum(0 < n < RING for n in t), RING, sum(n == RING for n in t), sum(n > RING for n in t), max(t) if t else '-'))
for lo, hi, name in ((0, 1900, 'under 1900'), (1900, 2100, '1900-2099'), (2100, 9999, '2100 and over')):
    g = [r for r in full if lo <= (r['opponent_rating'] or 0) < hi]
    t = [r['final']['them']['queen_length'] for r in g]
    print('   opponent %-14s full games %3d | their queen dead %d, under %d: %d, %d or longer: %d'
          % (name, len(g), sum(n == 0 for n in t), RING, sum(0 < n < RING for n in t), RING, sum(n >= RING for n in t)))
for key in ('200', '300', '400'):
    t = [r['curves'][key]['them'] for r in full if r['curves'].get(key)]
    alive = [s['queen_length'] for s in t if s['queen_alive']]
    print('   their queen at r%s: alive in %d of %d, %d or longer in %d' % (key, len(alive), len(t), RING, sum(n >= RING for n in alive)))

print('\n== upper bound: losses a living queen of %d would turn, everything else unchanged ==' % RING)
loss = [r for r in rows if r['result'] == 'loss']
print('   losses', len(loss), 'by bucket', dict(Counter(bucket(r) for r in loss)))
reach = [r for r in loss if r['_full'] and r['final']['them']['queen_length'] < RING and not r['_vault']]
print('   full-game losses with their queen dead or under %d at the end, queen free to leave spawn: %d %s'
      % (RING, len(reach), dict(Counter(bucket(r) for r in reach))))
keep = [r for r in loss if r['_full'] and r['final']['them']['queen_length'] >= RING]
print('   full-game losses with their queen at %d or longer (not turned): %d %s' % (RING, len(keep), dict(Counter(bucket(r) for r in keep))))
elim = [r for r in loss if not r['_full']]
print('   losses that end before round 500 (not turned by the rule; she would also have to survive the wipe-out): %d' % len(elim))
late = [r for r in elim if r['last_round'] > 300]
print('      of these after r300: %d' % len(late))
alive100 = [r for r in reach if r['queen']['us']['alive'].get('100')]
alive200 = [r for r in reach if r['queen']['us']['alive'].get('200')]
print('   of the %d: our queen alive at r100 in %d, at r200 in %d' % (len(reach), len(alive100), len(alive200)))
big = [r for r in reach if r['_cells'] > 1200]
print('   of the %d: on layouts above 1200 cells %d, at or below %d' % (len(reach), len(big), len(reach) - len(big)))
wins = [r for r in rows if r['result'] == 'win' and r['_full']]
print('   full-game wins %d, of them by queen rule with only ours alive %d, both dead %d'
      % (len(wins), sum(r['queens_at_end'] == 'only ours' for r in wins), sum(r['queens_at_end'] == 'both dead' for r in wins)))

print('\n== team supply: could the swarm feed her 20 pearls early? ==')
for key in ('50', '100', '150', '200'):
    t = [r['curves'][key]['us'] for r in free if r['curves'].get(key)]
    p = sorted(s['pearls'] for s in t)
    print('   r%-3s team pearls eaten so far: median %s, lower quartile %s, games under 20: %d of %d | dragons alive median %s'
          % (key, median(p), p[len(p) // 4], sum(x < 20 for x in p), len(p), median([s['alive'] for s in t])))
