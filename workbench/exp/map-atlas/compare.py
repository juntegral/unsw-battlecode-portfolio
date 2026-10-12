"""compare.py — the atlas pipeline (extract.js, Codex) against the independent recount (recount.js, Claude).

Two levels:
  1. game by game: every shared field of every game (heads and longest at each checkpoint, splits, eligible head-rounds and
     natural intake per phase, sacrifice rounds and lengths, pings, king exposure counts, stall, layout, winner) must be equal;
  2. per map/layout: the key numbers of the report computed from each source by the same aggregation code below.
Writes cache/compare.json and prints a markdown table. Reconstruction checks of the recount (all expected 0) are summed.
"""
import json, pathlib, statistics as st, collections
O = pathlib.Path(__file__).resolve().parent / 'cache'
CPS = [10, 25, 50, 100, 150, 250, 300, 350, 400]

def jl(p):
    with open(p) as f:
        for l in f:
            if l.strip():
                yield json.loads(l)

def norm_codex(r):
    """Codex row -> the recount's field names."""
    out = {'key': r['key'], 'src': r['src'], 'set': r.get('set'), 'map': r['map'], 'layout': r['layout'], 'rounds': r['rounds'],
           'winner': r['winner'], 'end': r['endReason'], 'us': r.get('us'), 'opp': r.get('oppId'), 'wave': r.get('wave'), 'stall': sorted(r['stall'])}
    for t in 'AB':
        u = r[t]
        out[t] = {'heads': {int(k): v['heads'] for k, v in u['cp'].items() if int(k) in CPS + [500]},
                  'king': {int(k): v['king'] for k, v in u['cp'].items() if int(k) in CPS + [500]},
                  'splits': [p['splits'] for p in u['phase']], 'eligHR': [p['eligibleHR'] for p in u['phase']],
                  'nat': [p['nat'] for p in u['phase']], 'sac': sorted([a[0], a[1]] for a in u['sac']), 'pings': u['pings'],
                  'kingR': [u['exposure'][0][0], u['exposure'][1][0]], 'kingNear3': [u['exposure'][0][1], u['exposure'][1][1]],
                  'kingNear6': [u['exposure'][0][2], u['exposure'][1][2]]}
    return out

def norm_recount(r):
    out = {'key': r['key'], 'src': r['src'], 'set': r.get('set'), 'map': r['map'], 'layout': r['layout'], 'rounds': r['rounds'],
           'winner': r['winner'], 'end': r['endReason'], 'us': r.get('us'), 'opp': r.get('opp'), 'stall': sorted(r['stall'])}
    for t in 'AB':
        u = r[t]
        out[t] = {'heads': {int(k): v for k, v in u['heads'].items()}, 'king': {int(k): v for k, v in u['king'].items()},
                  'splits': u['splits'], 'eligHR': u['eligHR'], 'nat': u['nat'], 'sac': sorted(u['sac']), 'pings': u['pings'],
                  'kingR': u['kingR'], 'kingNear3': u['kingNear3'], 'kingNear6': u['kingNear6']}
    return out

def onset(sac, f=0.2):
    rows = sorted(a for a in sac if a[0] >= 200); tot = sum(a[1] for a in rows)
    if tot < 10: return None
    run = 0
    for a in rows:
        run += a[1]
        if run >= tot * f: return a[0]

def mean(a):
    a = [x for x in a if x is not None]; return (sum(a) / len(a), len(a)) if a else (None, 0)

def med(a):
    a = [x for x in a if x is not None]; return (st.median(a), len(a)) if a else (None, 0)

WAVES = ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3'] + [f'cand-stack{i}-online' for i in range(1, 7)] + \
        ['cand-stack6-online-r2'] + [f'cand-stack{i}-online' for i in range(7, 12)]

def key_numbers(games):
    """games: normalised rows of one source. Returns {layout: {name: (value, n)}}."""
    by = collections.defaultdict(list)
    for g in games: by[g['map'] + '/' + g['layout']].append(g)
    res = {}
    for lay, gs in sorted(by.items()):
        top = [g for g in gs if g['src'] == 'top']; kept = [g for g in top if not g['stall']]
        dec = [g for g in kept if g['winner']]
        W = [(g, g['winner']) for g in dec]; L = [(g, 'B' if g['winner'] == 'A' else 'A') for g in dec]
        x = {'N': (len(kept), len(kept)), 'excluded': (len(top) - len(kept), len(top)),
             'elimination': ((sum(g['end'] == 'teamEliminated' for g in kept) / len(kept)) if kept else None, len(kept))}
        for r in [10, 25, 50, 100, 250]:
            x[f'W heads r{r}'] = mean([g[s]['heads'].get(r) for g, s in W])
        x['L heads r100'] = mean([g[s]['heads'].get(100) for g, s in L])
        for p in [0, 1]:
            num = sum(g[s]['splits'][p] for g, s in W); den = sum(g[s]['eligHR'][p] for g, s in W)
            x[f'W split p{p}'] = (num / den if den else None, den)
        x['W onset20 median'] = med([onset(g[s]['sac']) for g, s in W])
        full = [(g, s) for g, s in W if g['rounds'] == 500]; fullL = [(g, s) for g, s in L if g['rounds'] == 500]
        x['W king500 (full)'] = mean([g[s]['king'].get(500) for g, s in full])
        x['L king500 (full)'] = mean([g[s]['king'].get(500) for g, s in fullL])
        kr = sum(sum(g[s]['kingR']) for g, s in W); k6 = sum(sum(g[s]['kingNear6']) for g, s in W)
        x['W king near6'] = (k6 / kr if kr else None, kr)
        ours = [g for g in gs if g['src'] == 'online' and g.get('set') in WAVES and str(g.get('opp')) != '545']
        x['ours top6 wins'] = (sum(g['winner'] == g['us'] for g in ours), len(ours))
        x['ours heads r100'] = mean([g[g['us']]['heads'].get(100) for g in ours])
        x['ours eliminated'] = (sum(g[g['us']]['heads'].get(500) == 0 for g in ours), len(ours))
        res[lay] = x
    return res

def main():
    rc = {r['key']: r for r in jl(O / 'recount.jsonl')}
    checks = collections.Counter()
    for r in rc.values():
        for k in ['lenMismatch', 'finalMismatch', 'unpaired', 'strayPearls', 'initMismatch']: checks[k] += r[k]
    cx = {}
    for r in jl(O / 'raw.jsonl'):
        if r['src'] == 'local' or r['key'] not in rc: continue
        cx[r['key']] = norm_codex(r)
    rn = {k: norm_recount(rc[k]) for k in cx}
    diff = collections.Counter(); examples = collections.defaultdict(list)
    for k, a in cx.items():
        b = rn[k]
        for f in ['map', 'rounds', 'winner', 'end', 'stall']:
            if a[f] != b[f]: diff[f] += 1; examples[f].append(k)
        la, lb = a['layout'], b['layout']
        if la != lb: diff['layout'] += 1; examples['layout'].append((k, la, lb))
        for t in 'AB':
            for f in ['heads', 'king', 'splits', 'eligHR', 'nat', 'sac', 'pings', 'kingR', 'kingNear3', 'kingNear6']:
                if a[t][f] != b[t][f]: diff[f] += 1; examples[f].append((k, t))
    ka = key_numbers(cx.values()); kb = key_numbers(rn.values())
    out = {'games': len(cx), 'recountRows': len(rc), 'recountChecks': dict(checks), 'fieldDifferences': dict(diff),
           'examples': {k: v[:5] for k, v in examples.items()}, 'codex': ka, 'recount': kb}
    (O / 'compare.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print('games compared', len(cx), 'recount rows', len(rc)); print('recount checks', dict(checks)); print('field differences', dict(diff))
    for f, v in examples.items(): print(' ', f, v[:5])
    names = list(next(iter(ka.values())).keys())
    fmt = lambda v: '-' if v is None else (f'{v:.3f}' if isinstance(v, float) and abs(v) < 2 else f'{v:.1f}' if isinstance(v, float) else str(v))
    for lay in ka:
        print(f'\n{lay}')
        for n in names:
            a, b = ka[lay][n], kb[lay].get(n, (None, 0))
            print(f'  {n:20s} codex {fmt(a[0]):>8s} (n {a[1]})  recount {fmt(b[0]):>8s} (n {b[1]})  {"SAME" if a == b else "DIFF"}')

if __name__ == '__main__':
    main()
