"""eras.py — our per-map indicators before and after the economy-touching waves (W0-W4 vs W5-W9 vs W10-W12), top-6 games.
W5 brought csplit/F/no-exit s (the first head-count change); W10 brought lsplit/cov (late pieces). Opponents also changed over
time, so a step is evidence of a change in our play on that map, not a clean causal estimate."""
import json, pathlib, collections, math
O = pathlib.Path(__file__).resolve().parent / 'cache'
ORDER = ['Autarky/a', 'Prisoners Dilemma/6', 'Prisoners Dilemma/10', 'Portals/a', 'Trauma/a', 'Slithery Fight/a', 'Slithery Fight/b', 'Schooltime/a', 'Schooltime/b', 'Default/a', 'Devil/a', 'Devil/b', 'Queen Of Spades/a', 'Queen Of Spades/b', 'Trophy/a']
ERA = lambda w: 'W0–W4' if w <= 6 else ('W5–W9' if w <= 11 else 'W10–W12')   # wave index: 0-2 W0a-c, 3-6 W1-W4, 7-11 W5-W9, 12-14 W10-W12
acc = collections.defaultdict(lambda: collections.defaultdict(lambda: {'n': 0, 'w': 0, 'e': 0, 'h100': [], 's0': [0, 0], 'k': [], 'nat': 0, 'natE': 0, 'tot250': []}))
for l in open(O / 'raw.jsonl'):
    r = json.loads(l)
    if r['src'] != 'online' or r.get('wave') is None or r.get('oppId') == 545: continue
    a = acc[r['map'] + '/' + r['layout']][ERA(r['wave'])]; u = r['us']; e = 'B' if u == 'A' else 'A'
    a['n'] += 1; a['w'] += r['winner'] == u; a['e'] += r[u]['cp']['500']['heads'] == 0
    if '100' in r[u]['cp']: a['h100'].append(r[u]['cp']['100']['heads'])
    if '250' in r[u]['cp']: a['tot250'].append(r[u]['cp']['250']['total'])
    a['s0'][0] += r[u]['phase'][0]['splits']; a['s0'][1] += r[u]['phase'][0]['eligibleHR']
    if r['rounds'] == 500: a['k'].append(r[u]['cp']['500']['king'])
    a['nat'] += sum(p['nat'] for p in r[u]['phase']); a['natE'] += sum(p['nat'] for p in r[e]['phase'])
out = {}
print('| 판본 | 시기 | 승/판 | 전멸 | 분열 r0–49 | r100 머리 | r250 총길이 | 섭취 몫 | 끝 최장 중앙 [500형] |')
print('|---|---|---|---|---|---|---|---|---|')
for k in ORDER:
    for era in ['W0–W4', 'W5–W9', 'W10–W12']:
        a = acc[k][era]
        if not a['n']: continue
        row = {'n': a['n'], 'wins': a['w'], 'elim': a['e'], 'split0': a['s0'][0] / a['s0'][1] if a['s0'][1] else None,
               'heads100': sum(a['h100']) / len(a['h100']) if a['h100'] else None, 'total250': sum(a['tot250']) / len(a['tot250']) if a['tot250'] else None,
               'intake': a['nat'] / (a['nat'] + a['natE']) if a['nat'] + a['natE'] else None, 'king500': sorted(a['k'])[len(a['k']) // 2] if a['k'] else None, 'fullN': len(a['k'])}
        out.setdefault(k, {})[era] = row
        f = lambda v, d=1: '–' if v is None else f'{v:.{d}f}'
        print(f"| {k} | {era} | {a['w']}/{a['n']} | {a['e']}/{a['n']} | {f(row['split0'], 2)} | {f(row['heads100'])} | {f(row['total250'])} | {f(100 * row['intake'], 0) + '%' if row['intake'] is not None else '–'} | {row['king500'] if row['king500'] is not None else '–'} [{row['fullN']}] |")
(O / 'eras.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
