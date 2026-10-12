#!/usr/bin/env python3
"""Own recount for plan.md: what each proposed change can reach, per loss bucket. Reads rows.jsonl and maps.json only; prints."""
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


def classify(r):
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


def pos(c):
    if c is None:
        return 'missing'
    u, t = c['us']['total'], c['them']['total']
    return 'behind' if 5 * u < 4 * t else 'ahead' if 5 * u > 6 * t else 'level'


for r in rows:
    m = maps[r['map_key']]
    r['_cells'] = m['width'] * m['height']
    r['_big'] = r['_cells'] > 1200
    r['_two'] = m['dragons_at_spawn'] == 2
    r['_sealed'] = bool(m['queen_spawn_dead_end'])
    r['_b'] = classify(r) if r['result'] == 'loss' else None

loss = [r for r in rows if r['result'] == 'loss']
B = ['L1', 'E2', 'Q2', 'Q1', 'E1', 'Other', 'Q3']
print(CODE, 'games', len(rows), 'wins', sum(r['result'] == 'win' for r in rows), 'losses', len(loss),
      'draws', sum(r['result'] == 'draw' for r in rows))
print('buckets', {b: sum(r['_b'] == b for r in loss) for b in B})
print('big losses', sum(r['_big'] for r in loss), 'of big games', sum(r['_big'] for r in rows),
      '| small losses', sum(not r['_big'] for r in loss), 'of', sum(not r['_big'] for r in rows))


def qd(r, side):
    return r['queen'][side]['death_round']


print('\n== A. leader phase (big layouts: step at r151; small: r301) ==')
for b in B:
    g = [r for r in loss if r['_b'] == b and r['_big']]
    p150 = Counter(pos(r['curves']['150']) for r in g)
    print(' big', b, len(g), 'position at r150', dict(p150))
bigl = [r for r in loss if r['_big']]
ok150 = [r for r in bigl if pos(r['curves']['150']) in ('level', 'ahead')]
print(' big losses level or ahead at r150:', len(ok150), 'of', len(bigl), 'by bucket', dict(Counter(r['_b'] for r in ok150)))
bigw = [r for r in rows if r['_big'] and r['result'] == 'win']
print(' big games level or ahead at r150: lost', len(ok150), 'won', sum(pos(r['curves']['150']) in ('level', 'ahead') for r in bigw))
smalll = [r for r in loss if not r['_big']]
ok300 = [r for r in smalll if pos(r['curves']['300']) in ('level', 'ahead')]
print(' small losses reaching r300:', sum(r['curves']['300'] is not None for r in smalll), 'level or ahead at r300:', len(ok300),
      dict(Counter(r['_b'] for r in ok300)))
for name, g in (('big', [r for r in loss if r['_b'] in ('L1', 'Other') and r['_big']]),
                ('small', [r for r in loss if r['_b'] in ('L1', 'Other') and not r['_big']])):
    c = Counter()
    for r in g:
        s = r['curves']['300']
        c['leader longer at r300' if s['us']['longest'] > s['them']['longest'] else
          'leader tied at r300' if s['us']['longest'] == s['them']['longest'] else 'leader shorter at r300'] += 1
    print(' L1+Other', name, len(g), dict(c),
          'median final longest ours/theirs', median(r['final']['us']['longest'] for r in g), median(r['final']['them']['longest'] for r in g))
num = den = tn = td = n = 0
for r in bigl:
    c = r['curves']
    if c['200'] is None or c['150']['us']['alive'] < 20:
        continue
    n += 1
    num += c['200']['us']['pearls'] - c['150']['us']['pearls']
    den += c['150']['us']['pearls'] - c['100']['us']['pearls']
    tn += c['200']['them']['pearls'] - c['150']['them']['pearls']
    td += c['150']['them']['pearls'] - c['100']['them']['pearls']
print(' big losses, pearls r151-200 / r101-150: ours %.3f theirs %.3f on %d games' % (num / den, tn / td, n))

print('\n== B. queen rule with only their queen alive ==')
q1 = [r for r in loss if r['_b'] == 'Q1']
q2 = [r for r in loss if r['_b'] == 'Q2']
print(' Q1', len(q1), 'strictly longer', sum(r['final']['us']['longest'] > r['final']['them']['longest'] for r in q1),
      'sealed-queen layouts', sum(r['_sealed'] for r in q1), 'by map', dict(Counter(r['map_key'] for r in q1)))
print(' Q1 free layouts: their queen length at end', sorted(r['final']['them']['queen_length'] for r in q1 if not r['_sealed']))
print(' Q1 free: their queen is 4 or less', sum(r['final']['them']['queen_length'] <= 4 for r in q1 if not r['_sealed']),
      '5-12', sum(5 <= r['final']['them']['queen_length'] <= 12 for r in q1 if not r['_sealed']),
      '13+', sum(r['final']['them']['queen_length'] >= 13 for r in q1 if not r['_sealed']))
print(' Q1 free: rounds their queen was the only queen', sorted(r['last_round'] - qd(r, 'us') for r in q1 if not r['_sealed']))
print(' Q1: our queen death cause', dict(Counter(r['queen']['us']['death_cause'] for r in q1)),
      'length at death', dict(Counter(r['queen']['us']['death_length'] for r in q1)))
print(' Q2', len(q2), 'sealed', sum(r['_sealed'] for r in q2),
      'our longest > their QUEEN length', sum(r['final']['us']['longest'] > r['final']['them']['queen_length'] for r in q2),
      '| Q1 same', sum(r['final']['us']['longest'] > r['final']['them']['queen_length'] for r in q1))
print(' Q2: our queen death cause', dict(Counter(r['queen']['us']['death_cause'] for r in q2)),
      'dead by r100', sum(qd(r, 'us') <= 100 for r in q2), 'position r100', dict(Counter(pos(r['curves']['100']) for r in q2)))
w = [r for r in rows if r['result'] == 'win']
print(' wins by ending:', dict(Counter((r['ended_by'], r['queens_at_end']) for r in w)))
print(' losses by ending:', dict(Counter((r['ended_by'], r['queens_at_end']) for r in loss)))
ba = [r for r in rows if r['queens_at_end'] == 'both alive' and r['last_round'] == 499]
print(' both queens alive at r500:', len(ba), 'won', sum(r['result'] == 'win' for r in ba),
      '| on layouts of 600 cells or fewer:', sum(r['_cells'] <= 600 for r in ba), 'won', sum(r['result'] == 'win' and r['_cells'] <= 600 for r in ba),
      '| decided on queen rule and won:', sum(r['result'] == 'win' and r['ended_by'] == 'queen rule' for r in ba),
      'of which <=600 cells', sum(r['result'] == 'win' and r['ended_by'] == 'queen rule' and r['_cells'] <= 600 for r in ba),
      'sealed', sum(r['_sealed'] for r in ba))
oo = [r for r in rows if r['queens_at_end'] == 'only ours' and r['last_round'] == 499]
print(' only our queen alive at r500:', len(oo), 'won', sum(r['result'] == 'win' for r in oo), 'our queen length', sorted(r['final']['us']['queen_length'] for r in oo))
print(' our queen length at r500 when alive (full games, free layouts):',
      sorted(r['final']['us']['queen_length'] for r in rows if r['last_round'] == 499 and r['queen']['us']['alive_end'] and not r['_sealed']))

print('\n== C. our queen: who dies first, and how ==')
free = [r for r in rows if not r['_sealed']]
fl = [r for r in free if r['result'] == 'loss']


def first(r):
    a, b = qd(r, 'us'), qd(r, 'them')
    if a is None and b is None:
        return 'neither'
    if b is None or (a is not None and a < b):
        return 'ours first'
    if a is None or b < a:
        return 'theirs first'
    return 'same round'


for name, g in (('all free games', free), ('free losses', fl)):
    print(' ', name, len(g), dict(Counter(first(r) for r in g)))
print('  free games by first queen death -> won/games:',
      {k: '%d/%d' % (sum(r['result'] == 'win' for r in free if first(r) == k), sum(first(r) == k for r in free))
       for k in ('ours first', 'theirs first', 'same round', 'neither')})
held = [r for r in fl if first(r) == 'theirs first']
print('  losses in which THEIR queen died first (we held the only queen):', len(held), 'ours then died in', sum(qd(r, 'us') is not None for r in held),
      'by bucket', dict(Counter(r['_b'] for r in held)), 'cause of her death', dict(Counter(r['queen']['us']['death_cause'] for r in held)),
      'her length', dict(Counter(r['queen']['us']['death_length'] for r in held)))
print('  rounds she was the only queen before dying (those losses):', sorted(qd(r, 'us') - qd(r, 'them') for r in held if qd(r, 'us') is not None))
heldw = [r for r in free if first(r) == 'theirs first' and r['result'] == 'win']
print('  wins with theirs first:', len(heldw), 'our queen alive at end', sum(r['queen']['us']['alive_end'] for r in heldw))
of = [r for r in fl if first(r) == 'ours first']
print('  losses in which OUR queen died first:', len(of), 'by bucket', dict(Counter(r['_b'] for r in of)),
      'cause', dict(Counter(r['queen']['us']['death_cause'] for r in of)), 'by r100', sum(qd(r, 'us') <= 100 for r in of),
      'r101-200', sum(100 < qd(r, 'us') <= 200 for r in of), 'later', sum(qd(r, 'us') > 200 for r in of))
print('  all losses, our queen dead at the end:', sum(not r['queen']['us']['alive_end'] for r in loss), 'of', len(loss),
      'cause', dict(Counter(r['queen']['us']['death_cause'] for r in loss if not r['queen']['us']['alive_end'])),
      'length', dict(Counter(r['queen']['us']['death_length'] for r in loss if not r['queen']['us']['alive_end'])))
box = [r for r in fl if r['queen']['us']['death_cause'] in ('wall', 'own body', 'other dragon body')]
print('  free losses with our queen dead on wall / own body / another body:', len(box), 'by bucket', dict(Counter(r['_b'] for r in box)),
      'window', dict(Counter('r0-100' if qd(r, 'us') <= 100 else 'r101-200' if qd(r, 'us') <= 200 else 'r201+' for r in box)),
      'of these their queen was alive at the end', sum(r['queen']['them']['alive_end'] for r in box),
      'theirs died first', sum(first(r) == 'theirs first' for r in box))
boxw = [r for r in free if r['result'] == 'win' and r['queen']['us']['death_cause'] in ('wall', 'own body', 'other dragon body')]
print('  free wins with the same queen death:', len(boxw))
ram = [r for r in fl if r['queen']['us']['death_cause'] == 'head-on']
print('  free losses with our queen dead head-on:', len(ram), 'she was the standing victim',
      sum((r['queen']['us']['head_on'] or {}).get('victim') == r['queen']['us']['id'] for r in ram),
      'by bucket', dict(Counter(r['_b'] for r in ram)), 'window',
      dict(Counter('r0-100' if qd(r, 'us') <= 100 else 'r101-200' if qd(r, 'us') <= 200 else 'r201+' for r in ram)))

print('\n== D. eliminations ==')
e1 = [r for r in loss if r['_b'] == 'E1']
e2 = [r for r in loss if r['_b'] == 'E2']
for name, g in (('E1', e1), ('E2', e2)):
    c50 = [r for r in g if r['curves']['50'] is not None]
    half = sum(2 * r['curves']['50']['us']['pearls'] < r['curves']['50']['them']['pearls'] for r in c50)
    c100 = [r for r in g if r['curves']['100'] is not None]
    small = sum(r['curves']['100']['us']['alive'] <= 6 for r in c100)
    print(' ', name, len(g), 'two-start', sum(r['_two'] for r in g), 'big', sum(r['_big'] for r in g),
          '| pearls by r50 under half of theirs', half, 'of', len(c50),
          '| 6 or fewer dragons at r100', small, 'of', len(c100), '(no r100:', len(g) - len(c100), ')',
          '| cells<=600', sum(r['_cells'] <= 600 for r in g),
          '| by map', dict(Counter(r['map_key'] for r in g).most_common()))
    print('     our queen dead before r50', sum(qd(r, 'us') is not None and qd(r, 'us') < 50 for r in g),
          'their queen dead at end', sum(not r['queen']['them']['alive_end'] for r in g),
          'median round of wipe-out', median(r['last_round'] for r in g))
two = [r for r in rows if r['_two']]


def never(r):
    c = r['curves']['100']
    return (c is None and r['final']['us']['alive'] == 0) or (c is not None and c['us']['alive'] <= 6)


ng = [r for r in two if never(r)]
print('  2-start layouts:', len(two), 'games, lost', sum(r['result'] == 'loss' for r in two),
      '| never grew (6 or fewer dragons at r100, or wiped out before):', len(ng), 'won', sum(r['result'] == 'win' for r in ng),
      'lost', sum(r['result'] == 'loss' for r in ng), 'by bucket', dict(Counter(r['_b'] for r in ng if r['_b'])))
ngall = [r for r in rows if never(r)]
print('  all layouts never grew:', len(ngall), 'lost', sum(r['result'] == 'loss' for r in ngall),
      'by bucket', dict(Counter(r['_b'] for r in ngall if r['_b'])),
      'by map', dict(Counter(r['map_key'] for r in ngall if r['result'] == 'loss').most_common()))
print('  our pearls by r50 in elimination losses:', sorted(r['curves']['50']['us']['pearls'] for r in e1 + e2 if r['curves']['50']))

print('\n== E. bands ==')
for lo, hi, name in ((0, 1900, '<1900'), (1900, 2100, '1900-2099'), (2100, 9999, '2100+')):
    g = [r for r in rows if lo <= r['opponent_rating'] < hi]
    print(' ', name, len(g), 'lost', sum(r['result'] == 'loss' for r in g), dict(Counter(r['_b'] for r in g if r['_b'])))
