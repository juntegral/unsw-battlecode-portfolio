#!/usr/bin/env python3
"""Compare rows.jsonl with the independent Node recount (recount-*.jsonl). Read-only."""
import json, sys, glob
from collections import Counter
ROWS = sys.argv[1]; REC = sys.argv[2:]
rows = {r['game']: r for r in map(json.loads, open(ROWS))}
rec = {}
for f in REC:
    for l in open(f):
        r = json.loads(l); rec[r['game']] = r
print('rows', len(rows), 'recounted', len(rec), 'errors', sum('error' in r for r in rec.values()))
for g, r in rec.items():
    if 'error' in r: print('  ERROR', g, r['error'])
bad = Counter(); examples = {}
def diff(field, g, a, b):
    if a != b:
        bad[field] += 1; examples.setdefault(field, []).append((g, a, b))
chk = Counter()
for g, row in rows.items():
    r = rec.get(g)
    if not r or 'error' in r: bad['missing'] += 1; continue
    diff('our_side', g, row['our_side'], r['ours'])
    diff('result', g, row['result'], r['result'])
    diff('win', g, row['win'], r['result'] == 'win')
    diff('rule_winner', g, row['result'], {'us': 'win', 'them': 'loss', None: 'draw'}[r['ruleWinner']])
    diff('last_round', g, row['last_round'], r['last_round'])
    diff('ended_by', g, row['ended_by'], r['ended_by'])
    diff('queens_at_end', g, row['queens_at_end'], r['queens_at_end'])
    diff('our_bot.id', g, str(row['our_bot']['id']) if row['our_bot'] else '', r['bot' + r['ours']])
    diff('opponent bot blank', g, r['bot' + ('B' if r['ours'] == 'A' else 'A')], '')
    diff('notes.result', g, 'result' in row['notes'], False)
    for w in ('r0-100', 'r101-300', 'r301-500'):
        for s in ('us', 'them'):
            diff('deaths_other', g, row['deaths_other'][w][s], r['deaths_other'][w][s])
    for s in ('us', 'them'):
        o = r['official'][s]
        diff('final.queen_length(official)', g, row['final'][s]['queen_length'], o['queenLength'])
        diff('final.longest(official)', g, row['final'][s]['longest'], o['longestDragon'])
        diff('final.total(official)', g, row['final'][s]['total'], o['totalLength'])
        diff('final.alive(official)', g, row['final'][s]['alive'], o['dragonCount'])
        for m in ('50', '100', '150', '200', '300', '400'):
            a = row['curves'][m]; b = r['curves'][m]
            if a is None or b is None: diff(f'curves.null', g, a is None, b is None); continue
            for k in ('alive', 'total', 'longest', 'pearls', 'queen_alive', 'queen_length'):
                diff(f'curves.{k}', g, a[s][k], b[s][k])
        qa, qb = row['queen'][s], r['queen'][s]
        for k in ('id', 'death_round', 'death_cause', 'death_other', 'death_length', 'death_hit_id', 'head_on', 'pearls_eaten', 'splits'):
            diff(f'queen.{k}', g, qa[k], qb[k])
        for m in ('100', '200', '300', '400'):
            diff('queen.length', g, qa['length'][m], qb['length'][m])
        want500 = r['official'][s]['queenLength'] if (r['endReason'] == 'roundLimit' and r['last_round'] == 499) else None
        diff('queen.length.500', g, qa['length']['500'], want500)
        for w in ('r0-100', 'r101-300', 'r301-500'):
            for c in ('wall', 'own body', 'other dragon body', 'head-on', 'other'):
                diff(f'deaths.{c}', g, row['deaths'][w][s][c], r['deaths'][w][s][c])
            diff('pearls.eaten', g, row['pearls'][w]['eaten'][s], r['pearls'][w][s])
        diff('head_on.drops', g, row['head_on']['drops'][s], r['head_on']['drops'][s])
    for w in ('r0-100', 'r101-300', 'r301-500'):
        e = r['pearls'][w]; n = e['us'] + e['them']
        diff('pearls.our_share', g, row['pearls'][w]['our_share'], e['us'] / n if n else None)
    diff('head_on.count', g, row['head_on']['count'], r['head_on']['count'])
    diff('head_on.same_team_count', g, row['head_on']['same_team_count'], r['head_on']['same_team_count'])
    c = r['checks']
    for k in ('geoMismatch', 'splitTeamBad', 'unpairedH', 'dropBad', 'spawnInTurn'): chk[k] += c[k]
    chk['deaths'] += c['deaths']; chk['eats'] += c['eats']
    chk['finalMatchesOfficial'] += r['finalMatchesOfficial']
    if c['geoBad']: examples.setdefault('geoBad', []).append((g, c['geoBad']))
print('disagreements by field:', dict(bad) or 'none')
for k, v in examples.items(): print(' ', k, len(v), v[:4])
print('recount self-checks:', dict(chk))
print('ended_by (recount):', Counter(r['ended_by'] for r in rec.values() if 'error' not in r))
print('endReason:', Counter((r['endReason'], r['terminated'], r['last_round'] == 499) for r in rec.values() if 'error' not in r))
