"""extra.py — policy-ready numbers the Codex aggregation (analyze.py) did not produce (Claude, 2026-10-01).

Reads cache/raw.jsonl (extract.js rows; top games without a stalled team, W0-W12 wave games) and cache/cache-audit.json.
Per map/layout, for the elite winners (W), losers (L) and our top-6 wave games (U):
  heads: mean / median / q25 / q75 at r10, r25, r50, r100, r150, r250 (games still running at that round) and the share alive;
  splits per eligible (length >= 4) head-round in r0-24, r25-49 (from phase sums: r0-49 only), r50-99;
  sacrifice clock: pooled sacrifice events per team-round in 10-round bins from r200, the per-game onset10/onset20/onset50
    (the round by which 10/20/50 % of the r>=200 sacrifice length is done; games with >= 10 such length), first sacrifice >= r200;
  feeding radius: for sacrifices at r >= 300, the nearest longer ally head (torus Manhattan) <= 1, 2, 3, 4, 6 and the share of
    dropped pearls later eaten by the own team / by the final king line;
  king safety: share of king rounds (>= 8, r300-499, first turn) with an enemy head within 3 / 6, and late king deaths per game
    by cause with the killer's length;
  trading: head-on contacts (econ-principles cache, mover view) by the local head balance d8 (own - enemy heads within
    Manhattan 8 of the contact, pair excluded): count share and net pearls per contact.
Writes cache/extra.json.
"""
import json, pathlib, collections, statistics as st, math
O = pathlib.Path(__file__).resolve().parent / 'cache'
WAVES = ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3'] + [f'cand-stack{i}-online' for i in range(1, 7)] + \
        ['cand-stack6-online-r2'] + [f'cand-stack{i}-online' for i in range(7, 12)]

def q(a, p):
    a = sorted(a)
    if not a: return None
    x = (len(a) - 1) * p; i = int(x); return a[i] + (a[min(i + 1, len(a) - 1)] - a[i]) * (x - i)

def summ(a):
    a = [x for x in a if x is not None]
    if not a: return {'n': 0}
    return {'n': len(a), 'mean': sum(a) / len(a), 'median': st.median(a), 'q25': q(a, .25), 'q75': q(a, .75), 'q10': q(a, .1), 'q90': q(a, .9)}

def onset(sac, f):
    rows = sorted(a for a in sac if a[0] >= 200); tot = sum(a[1] for a in rows)
    if tot < 10: return None
    run = 0
    for a in rows:
        run += a[1]
        if run >= tot * f: return a[0]

def side_stats(pairs):
    out = {'n': len(pairs)}
    for r in [10, 25, 50, 100, 150, 250, 350]:
        v = [g[s]['cp'].get(str(r), {}).get('heads') for g, s in pairs]
        out[f'heads{r}'] = summ(v); out[f'alive{r}'] = sum(1 for g, s in pairs if str(r) in g[s]['cp'] and g[s]['cp'][str(r)]['heads'] > 0)
        out[f'running{r}'] = sum(1 for g, s in pairs if str(r) in g[s]['cp'])
    for p in range(3):
        num = sum(g[s]['phase'][p]['splits'] for g, s in pairs); den = sum(g[s]['phase'][p]['eligibleHR'] for g, s in pairs)
        out[f'split{p}'] = {'num': num, 'den': den, 'value': num / den if den else None}
    # sacrifice clock: events per team-round (team alive) by 10-round bin from r200
    bins = collections.defaultdict(lambda: [0, 0, 0])   # bin -> [team-rounds alive, events, length]
    for g, s in pairs:
        last = g['rounds'] - 1 if g[s]['cp']['500']['heads'] == 0 else g['rounds'] - 1
        for b in range(200, 500, 10):
            if b <= last: bins[b][0] += min(10, last - b + 1)
        for a in g[s]['sac']:
            if a[0] >= 200: bins[a[0] // 10 * 10][1] += 1; bins[a[0] // 10 * 10][2] += a[1]
    out['sacBins'] = {b: {'teamRounds': v[0], 'events': v[1], 'length': v[2], 'rate': v[1] / v[0] if v[0] else None} for b, v in sorted(bins.items())}
    for f in [0.1, 0.2, 0.5]:
        out[f'onset{int(f * 100)}'] = summ([onset(g[s]['sac'], f) for g, s in pairs])
    out['first200'] = summ([min([a[0] for a in g[s]['sac'] if a[0] >= 200], default=None) for g, s in pairs])
    late = [a for g, s in pairs if g['rounds'] == 500 for a in g[s]['sac'] if a[0] >= 300]
    full = sum(1 for g, s in pairs if g['rounds'] == 500)
    nb = [a[6] for a in late if a[6] != 999]
    out['feed'] = {'fullGames': full, 'events': len(late), 'perGame': len(late) / full if full else None,
                   'lengthPerGame': sum(a[1] for a in late) / full if full else None,
                   'nearLonger': {f'le{d}': (sum(x <= d for x in nb) / len(nb) if nb else None) for d in [1, 2, 3, 4, 6]},
                   'nearLongerN': len(nb), 'meanLen': (sum(a[1] for a in late) / len(late)) if late else None,
                   'lenShare': {k: (sum(1 for a in late if lo <= a[1] <= hi) / len(late) if late else None) for k, (lo, hi) in {'2': (2, 2), '3-4': (3, 4), '5-7': (5, 7), '8+': (8, 999)}.items()},
                   'ownEat': (sum(a[2] for a in late) / sum(a[2] + a[3] for a in late)) if sum(a[2] + a[3] for a in late) else None,
                   'dropsEatenShare': (sum(a[2] + a[3] for a in late) / sum(math.ceil(a[1] / 2) for a in late)) if late else None,
                   'lineShareOfOwn': (sum(a[4] for a in late) / sum(a[2] for a in late)) if sum(a[2] for a in late) else None}
    # mass and conversion: total length at checkpoints (games still running), final longest over r400 total (500-round games)
    for r in [100, 250, 300, 400]:
        out[f'total{r}'] = summ([g[s]['cp'].get(str(r), {}).get('total') for g, s in pairs])
    out['conversion'] = summ([g[s]['cp']['500']['king'] / g[s]['cp']['400']['total'] for g, s in pairs
                              if g['rounds'] == 500 and g[s]['cp'].get('400', {}).get('total')])
    out['heads500'] = summ([g[s]['cp']['500']['heads'] for g, s in pairs if g['rounds'] == 500])
    ex = [0, 0, 0]
    for g, s in pairs:
        for h in g[s]['exposure']: ex[0] += h[0]; ex[1] += h[1]; ex[2] += h[2]
    out['kingExposure'] = {'kingRounds': ex[0], 'near3': ex[1] / ex[0] if ex[0] else None, 'near6': ex[2] / ex[0] if ex[0] else None}
    kd = [k for g, s in pairs for k in g[s]['kd'] if k[0] >= 300]; reach300 = sum(1 for g, s in pairs if g['rounds'] > 300)
    causes = collections.Counter(k[2] for k in kd)
    out['kingDeaths'] = {'games': reach300, 'events': len(kd), 'perGame': len(kd) / reach300 if reach300 else None, 'causes': dict(causes),
                         'killerLen': summ([k[3] for k in kd if k[3] > 0]), 'len': summ([k[1] for k in kd])}
    return out

def main():
    raw = [json.loads(l) for l in open(O / 'raw.jsonl')]
    top = [r for r in raw if r['src'] == 'top' and not r['stall'] and r['layout'] != '?']
    ours = [r for r in raw if r['src'] == 'online' and r.get('set') in WAVES and r.get('oppId') != 545]
    res = {}
    for lay in sorted({r['map'] + '/' + r['layout'] for r in top}):
        gs = [r for r in top if r['map'] + '/' + r['layout'] == lay and r['winner']]
        W = [(g, g['winner']) for g in gs]; L = [(g, 'B' if g['winner'] == 'A' else 'A') for g in gs]
        U = [(g, g['us']) for g in ours if g['map'] + '/' + g['layout'] == lay]
        res[lay] = {'W': side_stats(W), 'L': side_stats(L), 'U': side_stats(U)}
    audit = json.loads((O / 'cache-audit.json').read_text())
    trade = collections.defaultdict(dict)
    for k, v in audit['trade'].items():
        lay, src, b = k.split('|'); trade[lay].setdefault(src, {})[b] = v
    for lay, d in trade.items():
        for src, bs in d.items():
            n = sum(v['n'] for v in bs.values())
            for b, v in bs.items():
                v['share'] = v['n'] / n if n else None; v['netPer'] = v['net'] / v['n'] if v['n'] else None
                v['ownShare20'] = v['own20'] / (v['own20'] + v['enemy20']) if (v['own20'] + v['enemy20']) else None
        if lay in res: res[lay]['trade'] = d
    (O / 'extra.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
    f = lambda v, d=2: '-' if v is None else f'{v:.{d}f}'
    for lay, x in res.items():
        W = x['W']; U = x['U']
        print(lay, 'W n', W['n'], 'heads r10/25/50/100/250 median', [f(W[f'heads{r}'].get('median'), 1) for r in [10, 25, 50, 100, 250]],
              'split', [f(W[f'split{p}']['value']) for p in range(3)], 'onset10/20/50 med', [f(W[f'onset{p}'].get('median'), 0) for p in [10, 20, 50]],
              'onset20 q25', f(W['onset20'].get('q25'), 0), 'feed<=3', f(W['feed']['nearLonger']['le3']), 'ownEat', f(W['feed']['ownEat']),
              'kingNear6 W/L/U', f(W['kingExposure']['near6']), f(x['L']['kingExposure']['near6']), f(U['kingExposure']['near6']),
              'kingDeaths/g W/L', f(W['kingDeaths']['perGame']), f(x['L']['kingDeaths']['perGame']))

if __name__ == '__main__':
    main()
