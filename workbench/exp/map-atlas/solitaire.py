"""solitaire.py — Portals (and Trauma for contrast): win probability as a function of our king at r500 against the top-6 teams'
own kings. On Portals the halves are disconnected (geometry: components 240/240, no path between the teams), so each team's
growth is independent of the other's; the winner is the longer king (then total length). Uses our W0-W12 top-6 games
(the opponent's king in the same game) and the top-vs-top games of the same six teams (their king in every Portals game).
"""
import json, pathlib, collections, statistics as st
O = pathlib.Path(__file__).resolve().parent / 'cache'
NAMES = {306: 'Cutlery', 70: 'cheji bt', 20: 'calc', 801: '中国必须人能飞😡', 264: 'forgot to mention', 46: 'Sabotage-d', 545: 'dev test 1 :P'}
WAVES = ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3'] + [f'cand-stack{i}-online' for i in range(1, 7)] + \
        ['cand-stack6-online-r2'] + [f'cand-stack{i}-online' for i in range(7, 12)]
raw = [json.loads(l) for l in open(O / 'raw.jsonl')]
res = {}
for lay in ['Portals/a', 'Trauma/a', 'Slithery Fight/a', 'Slithery Fight/b', 'Schooltime/a']:
    ours = [r for r in raw if r['src'] == 'online' and r.get('set') in WAVES and r['map'] + '/' + r['layout'] == lay and r['oppId'] != 545]
    opp_in_ours = [r['B' if r['us'] == 'A' else 'A']['cp']['500']['king'] for r in ours]
    us = [r[r['us']]['cp']['500']['king'] for r in ours]
    top = [r for r in raw if r['src'] == 'top' and not r['stall'] and r['map'] + '/' + r['layout'] == lay]
    elite = collections.defaultdict(list)
    for r in top:
        for s in 'AB':
            if r['team' + s] in NAMES.values() and r['team' + s] != NAMES[545]: elite[r['team' + s]].append(r[s]['cp']['500']['king'])
    pool = [k for v in elite.values() for k in v]
    def pwin(L, dist):
        return (sum(k < L for k in dist) + 0.5 * sum(k == L for k in dist)) / len(dist) if dist else None
    curve = {L: pwin(L, pool) for L in range(10, 81, 5)}
    model = sum(pwin(L, pool) for L in us) / len(us) if us and pool else None
    res[lay] = {'ourGames': len(ours), 'ourWins': sum(r['winner'] == r['us'] for r in ours), 'ourKing': {'median': st.median(us) if us else None, 'mean': sum(us) / len(us) if us else None},
                'oppKingInOurGames': {'median': st.median(opp_in_ours) if opp_in_ours else None, 'mean': sum(opp_in_ours) / len(opp_in_ours) if opp_in_ours else None},
                'top6KingTopGames': {'n': len(pool), 'median': st.median(pool) if pool else None, 'mean': sum(pool) / len(pool) if pool else None,
                                     'byTeam': {t: {'n': len(v), 'median': st.median(v)} for t, v in elite.items()}},
                'pWinByOurKing': curve, 'modelWinRateForOurKings': model}
    print(lay, json.dumps({k: v for k, v in res[lay].items() if k != 'pWinByOurKing'}, ensure_ascii=False))
    print('   P(win | our king L):', ' '.join(f'{L}:{p:.2f}' for L, p in curve.items() if p is not None))
(O / 'solitaire.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
