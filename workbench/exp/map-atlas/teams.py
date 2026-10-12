"""teams.py — robustness of the head targets across teams, and the top-6 opponents' own profile per map/layout (Claude).
Per layout: winners' r50/r100/r250 heads as (a) the population median (all winners), (b) the median of team medians (teams with >= 10
wins there), (c) the top-6 teams' winners' median; plus the top-6 teams' r100 heads and king500 in all their games (win or lose),
and their win rate against other top teams on that layout. Output: cache/teams.json, cache/teams.md."""
import json, pathlib, collections, statistics as st
O = pathlib.Path(__file__).resolve().parent / 'cache'
TOP6 = {'Cutlery', 'cheji bt', 'calc', '中国必须人能飞😡', 'forgot to mention', 'Sabotage-d'}
ORDER = ['Autarky/a', 'Prisoners Dilemma/6', 'Prisoners Dilemma/10', 'Portals/a', 'Trauma/a', 'Slithery Fight/a', 'Slithery Fight/b', 'Schooltime/a', 'Schooltime/b', 'Default/a', 'Devil/a', 'Devil/b', 'Queen Of Spades/a', 'Queen Of Spades/b', 'Trophy/a']
raw = [json.loads(l) for l in open(O / 'raw.jsonl')]
top = [r for r in raw if r['src'] == 'top' and not r['stall'] and r['layout'] != '?' and r['winner']]
res = {}; md = ['| 판본 | 승자 r100 머리 중앙: 전체 / 팀 중앙의 중앙 [팀 수] (팀 간 사분위) / 상위 6팀 승자 | 승자 r50 · r250 같은 셋 | 상위 6팀 모든 판: r100 머리 중앙 · 끝 최장 중앙(500형) · 상위권 상대 승률 [판] |', '|---|---|---|---|']
q = lambda a, p: sorted(a)[int(round((len(a) - 1) * p))] if a else None
for L in ORDER:
    gs = [r for r in top if r['map'] + '/' + r['layout'] == L]
    byteam = collections.defaultdict(lambda: collections.defaultdict(list)); t6w = collections.defaultdict(list)
    t6 = {'h100': [], 'k500': [], 'w': 0, 'n': 0}
    for g in gs:
        w = g['winner']; l = 'B' if w == 'A' else 'A'
        for r in [50, 100, 250]:
            h = g[w]['cp'].get(str(r), {}).get('heads')
            if h is not None:
                byteam[g['team' + w]][r].append(h)
                if g['team' + w] in TOP6: t6w[r].append(h)
        for s in 'AB':
            if g['team' + s] in TOP6:
                t6['n'] += 1; t6['w'] += g['winner'] == s
                h = g[s]['cp'].get('100', {}).get('heads')
                if h is not None: t6['h100'].append(h)
                if g['rounds'] == 500: t6['k500'].append(g[s]['cp']['500']['king'])
    out = {}
    for r in [50, 100, 250]:
        allv = [h for t in byteam.values() for h in t[r]]
        tm = [st.median(t[r]) for t in byteam.values() if len(t[r]) >= 10]
        out[r] = {'all': st.median(allv) if allv else None, 'teamMedian': st.median(tm) if tm else None, 'teams': len(tm), 'teamQ25': q(tm, .25), 'teamQ75': q(tm, .75),
                  'top6': st.median(t6w[r]) if t6w[r] else None, 'top6N': len(t6w[r])}
    out['top6Profile'] = {'h100': st.median(t6['h100']) if t6['h100'] else None, 'k500': st.median(t6['k500']) if t6['k500'] else None, 'k500N': len(t6['k500']), 'winRate': t6['w'] / t6['n'] if t6['n'] else None, 'n': t6['n']}
    res[L] = out
    f = lambda v: '–' if v is None else (f'{v:.0f}' if isinstance(v, (int, float)) and abs(v - round(v)) < 1e-9 else f'{v:.1f}')
    o = out[100]; p = out['top6Profile']
    md.append(f"| {L} | {f(o['all'])} / {f(o['teamMedian'])} [{o['teams']}] ({f(o['teamQ25'])}–{f(o['teamQ75'])}) / {f(o['top6'])} [{o['top6N']}] | "
              f"r50 {f(out[50]['all'])} / {f(out[50]['teamMedian'])} / {f(out[50]['top6'])}; r250 {f(out[250]['all'])} / {f(out[250]['teamMedian'])} / {f(out[250]['top6'])} | "
              f"{f(p['h100'])} · {f(p['k500'])} [{p['k500N']}] · {100 * p['winRate']:.0f}% [{p['n']}] |")
(O / 'teams.json').write_text(json.dumps(res, ensure_ascii=False, indent=1)); (O / 'teams.md').write_text('\n'.join(md) + '\n')
print('\n'.join(md))
