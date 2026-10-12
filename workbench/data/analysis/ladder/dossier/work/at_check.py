"""Scratch (diag-attack): check of at_scan against the dossier input snapshot (head-on counts and deaths by side)."""
import json
from collections import Counter
from pathlib import Path

D = Path('data/analysis/ladder/dossier/work')
G = {}
for n in range(5):
    with open(D / ('at_scan-%d.jsonl' % n)) as f:
        for line in f:
            g = json.loads(line)
            G[g['game']] = g
rows = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())['rows']
print('games scanned', len(G), 'of', len(rows))
bad = 0
tot = Counter()
for r in rows:
    g = G.get(r['game'])
    if g is None:
        bad += 1
        continue
    cross = sum(1 for x in g['hos'] if x['cross'])
    same = len(g['hos']) - cross
    if cross != r['head_on']['count'] or same != r['head_on']['same_team_count']:
        bad += 1
    want_u = sum(r['deaths'][k]['us']['head-on'] for k in r['deaths'])
    want_t = sum(r['deaths'][k]['them']['head-on'] for k in r['deaths'])
    tot['want_u'] += want_u
    tot['want_t'] += want_t
    for x in g['hos']:
        tot['got_u'] += int(x['ms'] == 0) + int((x['ms'] == 0) == bool(not x['cross']))
        tot['got_t'] += int(x['ms'] == 1) + int((x['ms'] == 1) == bool(not x['cross']))
        if x['cross']:
            tot['cross'] += 1
            tot['they_move'] += x['ms']
            tot['found'] += int(x['d'] >= 0)
            tot['d_eq_k'] += int(x['d'] == x['k'])
            if x['r'] <= 300:
                tot['r300_u_hit'] += int(x['ms'] == 1)
                tot['r300_t_hit'] += int(x['ms'] == 0)
print('games with a different head-on count:', bad)
print(dict(tot))
print('to round 300 a game: ours hit %.1f, theirs hit %.1f (fingerprint: 20.7 and 11.7)' % (tot['r300_u_hit'] / len(rows), tot['r300_t_hit'] / len(rows)))
print('their mover share %.3f; meetings the reach search saw at the turn start %.4f; same step count %.4f' % (
    tot['they_move'] / tot['cross'], tot['found'] / tot['cross'], tot['d_eq_k'] / tot['cross']))
