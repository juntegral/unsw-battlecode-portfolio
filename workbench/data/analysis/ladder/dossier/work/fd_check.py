# Scratch (diag-feeding): independent recount of the round-401 figures from rows.jsonl alone (the runner's own
# reconstruction, not fd_scan). Compares with fd_games.jsonl. Prints only.
import json
from collections import Counter
from pathlib import Path

mine = dict((r['game'], r) for r in (json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()))
scanned = set()
for k in range(4):
    for l in Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k).open():
        scanned.add(json.loads(l[:l.index(',')] + '}')['game'])
rows = [json.loads(l) for l in open('data/analysis/ladder/rows.jsonl')]
main = [r for r in rows if r['our_code'] == 'main']
print('rows.jsonl main games now', len(main), 'scanned', len(scanned), 'not scanned (arrived later)', sum(r['game'] not in scanned for r in main))
main = [r for r in main if r['game'] in scanned]
late = [r for r in main if r['last_round'] >= 401 and r['curves'].get('400')]
print('reach r401', len(late), Counter(r['result'] for r in late), '| fd_games with a r401 snapshot', sum('401' in r['mid'] for r in mine.values()))
w = [r for r in late if r['result'] == 'win' and r['ended_by'] in ('longest dragon', 'total length')]
lt = sum(r['curves']['400']['us']['longest'] < r['final']['them']['longest'] for r in w)
eq = sum(r['curves']['400']['us']['longest'] == r['final']['them']['longest'] for r in w)
print('won on longest/total', len(w), 'our r400-end longest < their final', lt, 'equal', eq, 'longer', len(w) - lt - eq)
bad = 0
for r in late:
    m = mine.get(r['game'])
    if m is None or '401' not in m['mid']:
        bad += 1
        continue
    a = m['mid']['401']
    c = r['curves']['400']
    if [a[0], a[1], a[2], a[4], a[5], a[6]] != [c['us']['alive'], c['us']['longest'], c['us']['total'], c['them']['alive'], c['them']['longest'], c['them']['total']]:
        bad += 1
print('r401 standings that differ between the two reconstructions', bad, 'of', len(late))
el = [r for r in main if r['ended_by'] == 'elimination' and r['result'] == 'loss' and r['last_round'] >= 401]
print('lost by elimination with last round 401+', len(el), '| in fd_games (wiped, last 401+)', sum(r['Ue'][0] == 0 and r['last'] >= 401 for r in mine.values()))
print('all main scanned: reach r201', sum(r['last_round'] >= 201 for r in main), 'r301', sum(r['last_round'] >= 301 for r in main), 'full', sum(r['last_round'] == 499 for r in main))
