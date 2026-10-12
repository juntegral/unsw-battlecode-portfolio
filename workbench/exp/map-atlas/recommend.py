"""recommend.py — per map/layout engine assignment and policy.hpp-ready targets (Claude, 2026-10-01).

Every number comes from the full-population caches (extra.json, stats.json, solitaire.json); the assignment rule and the
choice of statistic are written here so that they can be checked and changed in one place.

Targets (elite winners of top-vs-top games, games still running at that round):
  heads r10/r25/r50/r100/r250 = winners' median, capped at 56 (SwarmParams::headCap; the unit limit is 64);
  split speed r0-49 / r50-99 = winners' splits per length >= 4 head-round (phase sums);
  sacrifice clock = the first 10-round bin from r200 in which the winners' sacrifice rate (per team-round) reaches half of its
    r200-499 peak (start50); start25 (a quarter of the peak) and the per-game onset20 median are given beside it;
  feeding radius = the smallest torus-Manhattan distance to the nearest longer ally head that covers >= 75 % of the winners'
    r300+ sacrifices;
  trading = head-on contacts of all top teams by the local balance d8 (own - enemy heads within Manhattan 8): the net pearls per
    contact in each bucket; stance = trade only in the buckets with a positive net;
  king safety = the winners' king (>= 8) share of r300-499 rounds with an enemy head within 3 and within 6, as the ceiling.
"""
import json, pathlib
O = pathlib.Path(__file__).resolve().parent / 'cache'
X = json.loads((O / 'extra.json').read_text()); S = json.loads((O / 'stats.json').read_text())['atlas']
P = json.loads((O / 'solitaire.json').read_text())

# Engine archetypes (reasons in the report, section 2): F = fortress (stack11 as is), SE = swarm economy (500-round),
# SL = swarm economy without the contact rules (solitaire: the halves are disconnected), EL = elimination specialist (territory
# war to r100-250, then the swarm conversion).
ENGINE = {
    'Autarky/a': 'F', 'Prisoners Dilemma/6': 'F', 'Prisoners Dilemma/10': 'F',
    'Portals/a': 'F→SL', 'Trauma/a': 'SE', 'Slithery Fight/a': 'SE', 'Slithery Fight/b': 'SE', 'Schooltime/a': 'SE',
    'Schooltime/b': 'EL', 'Default/a': 'EL', 'Devil/a': 'EL', 'Devil/b': 'EL', 'Queen Of Spades/a': 'EL', 'Queen Of Spades/b': 'EL', 'Trophy/a': 'EL',
}
POLICY_ROW = {'Autarky/a': ('Autarky', '*'), 'Prisoners Dilemma/6': ('Prisoners_Dilemma', 'a'), 'Prisoners Dilemma/10': ('Prisoners_Dilemma', 'b'),
              'Portals/a': ('Portals', '*'), 'Trauma/a': ('Trauma', '*'), 'Slithery Fight/a': ('Slithery_Fight', 'a'), 'Slithery Fight/b': ('Slithery_Fight', 'b'),
              'Schooltime/a': ('Schooltime', 'a'), 'Schooltime/b': ('Schooltime', 'b'), 'Default/a': ('Default', '*'), 'Devil/a': ('Devil', 'a'), 'Devil/b': ('Devil', 'b'),
              'Queen Of Spades/a': ('Queen_Of_Spades', 'a'), 'Queen Of Spades/b': ('Queen_Of_Spades', 'b'), 'Trophy/a': ('Trophy', '*')}

def clock(bins, frac):
    pts = [(int(b), v['rate']) for b, v in bins.items() if v['rate'] is not None and int(b) >= 200]
    if not pts: return None
    peak = max(r for b, r in pts)
    for b, r in sorted(pts):
        if r >= frac * peak: return b
    return None

def main():
    out = {}
    for lay, x in X.items():
        W, L, U = x['W'], x['L'], x['U']; a = S[lay]
        heads = {r: (min(56, round(W[f'heads{r}']['median'])) if W[f'heads{r}'].get('n') else None) for r in [10, 25, 50, 100, 250]}
        headsMean = {r: (W[f'heads{r}']['mean'] if W[f'heads{r}'].get('n') else None) for r in [10, 25, 50, 100, 250]}
        headsN = {r: W[f'heads{r}'].get('n', 0) for r in [10, 25, 50, 100, 250]}
        ours = {r: (U[f'heads{r}']['mean'] if U[f'heads{r}'].get('n') else None) for r in [10, 25, 50, 100, 250]}
        nl = W['feed']['nearLonger']; radius = next((d for d in [1, 2, 3, 4, 6] if nl[f'le{d}'] is not None and nl[f'le{d}'] >= 0.75), None)
        tr = x.get('trade', {}).get('top', {})
        trade = {b: {'n': v['n'], 'share': v['share'], 'netPer': v['netPer'], 'ownShare20': v['ownShare20']} for b, v in tr.items()}
        stance = [b for b in ['advantage', 'balanced', 'disadvantage'] if b in tr and tr[b]['netPer'] > 0]
        out[lay] = {
            'engine': ENGINE[lay], 'policyRow': POLICY_ROW[lay], 'N': a['n'], 'decided': a['n'] - a['draws'], 'eliminationRate': a['eliminationRate']['value'],
            'heads': heads, 'headsMean': headsMean, 'headsN': headsN, 'oursHeads': ours,
            'split': [W['split0']['value'], W['split1']['value'], W['split2']['value']], 'splitOurs': [U['split0']['value'], U['split1']['value']],
            'clockStart50': clock(W['sacBins'], 0.5), 'clockStart25': clock(W['sacBins'], 0.25), 'onset20': W['onset20'], 'onset50': W['onset50'],
            'onset20N': W['onset20']['n'], 'feedRadius': radius, 'feedNear': nl, 'feedN': W['feed']['nearLongerN'],
            'trade': trade, 'tradeStance': stance,
            'kingNear3': W['kingExposure']['near3'], 'kingNear6': W['kingExposure']['near6'], 'kingRounds': W['kingExposure']['kingRounds'],
            'kingNear6L': L['kingExposure']['near6'], 'kingNear6U': U['kingExposure']['near6'],
            'king500W': a['elite']['W']['line']['final'].get('median'), 'king500L': a['elite']['L']['line']['final'].get('median'), 'full': a['elite']['W']['line']['fullN'],
            'oursWins': a['ours']['wins'], 'oursN': a['ours']['n'], 'oursElim': a['ours']['eliminated'], 'oursKing500': a['ours']['line']['final'].get('median'),
            'solitaire': P.get(lay),
        }
    (O / 'recommend.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    f = lambda v, d=0: '–' if v is None else f'{v:.{d}f}'
    for lay, r in out.items():
        print(f"{lay:22s} {r['engine']:5s} N={r['N']:5d} elim={f(r['eliminationRate'], 2)} heads(med) {[r['heads'][k] for k in [10, 25, 50, 100, 250]]} ours {[f(r['oursHeads'][k], 1) for k in [10, 25, 50, 100, 250]]} "
              f"split {f(r['split'][0], 2)}/{f(r['split'][1], 2)} clock50 {r['clockStart50']} clock25 {r['clockStart25']} onset20 {f(r['onset20'].get('median'))} (n {r['onset20N']}) "
              f"radius {r['feedRadius']} near6 W/L/U {f(r['kingNear6'], 2)}/{f(r['kingNear6L'], 2)}/{f(r['kingNear6U'], 2)} near3 {f(r['kingNear3'], 3)} stance {r['tradeStance']}")

if __name__ == '__main__':
    main()
