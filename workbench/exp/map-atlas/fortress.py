"""fortress.py — the fortress maps across wave eras (Claude, 2026-10-01; coordinator request 03:50).

Maps: Autarky, PD6, PD10, Portals. Eras: W0-W4 (merge2 x3, stack1-4), W5-W9 (stack5-8, incl. W7 = stack6 rerun), W10-W12
(stack9-11); also finer groups for Autarky: W5-W7 (csplit/F/no-exit s, mapid/bsp), W8-W9 (+ floor/kcap, F2/cl), W10-W12
(+ lsplit/fc/cov, lnt, gh/kx). Top-6 games only (DEV 545 apart).
Per era, for us and for the opponent in the same games: r100 heads, r250 / r400 total length (games still running), king500
(500-round games), king500 / r400 total, wins, king (longest >= 8) deaths by kind per game (all rounds):
  own-move = the king was the mover (trap, sacrifice-class death, into an enemy body, head-on it started, sprint, fault),
  enemy = an enemy head moved into it (rammed), ally = one of ours moved into its head.
Mechanism records per game by era (mech_check.analyse via mechanisms.jsonl; record kinds of the W5+ features).
Tests: Mann-Whitney (normal approximation, ties averaged) and two-sided Fisher exact.
Output: cache/fortress.json and cache/fortress.md.
"""
import json, pathlib, collections, statistics as st, math
from math import comb
O = pathlib.Path(__file__).resolve().parent / 'cache'
WN = ['W0a', 'W0b', 'W0c'] + [f'W{i}' for i in range(1, 13)]
MAPS = ['Autarky/a', 'Prisoners Dilemma/6', 'Prisoners Dilemma/10', 'Portals/a']
ERA3 = lambda w: 'W0–W4' if w <= 6 else ('W5–W9' if w <= 11 else 'W10–W12')
ERA_A = lambda w: 'W0–W4' if w <= 6 else ('W5–W7' if w <= 9 else ('W8–W9' if w <= 11 else 'W10–W12'))
MECH = ['csplit', 'fguard', 'cl', 'cov', 'covw', 'lsplit', 'frag', 'floor', 'kcap', 'bsplit', 'mapid', 'lntv', 'lnt', 'gh', 'ghd', 'kx', 'lwk', 'gx', 'escsplit', 'noexit', 'gather', 'feed', 'conv', 'grab', 'tg']

def mw(a, b):
    n1, n2 = len(a), len(b)
    if not n1 or not n2: return None
    allv = sorted([(v, 0) for v in a] + [(v, 1) for v in b]); rk = [0.0] * len(allv); i = 0
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]: j += 1
        for k in range(i, j): rk[k] = (i + j + 1) / 2
        i = j
    R1 = sum(rk[k] for k in range(len(allv)) if allv[k][1] == 0); U = R1 - n1 * (n1 + 1) / 2
    z = (U - n1 * n2 / 2) / math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12); return {'z': z, 'p': math.erfc(abs(z) / math.sqrt(2))}

def pf_(p): return '< 0.0001' if p < 0.0001 else f'{p:.4f}'

def fisher(a, b, c, d):
    n = a + b + c + d; r1 = a + b; c1 = a + c
    pr = lambda x: comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1); p0 = pr(a)
    return sum(pr(x) for x in range(max(0, r1 - (n - c1)), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9))

raw = [json.loads(l) for l in open(O / 'raw.jsonl')]
games = [r for r in raw if r['src'] == 'online' and r.get('wave') is not None and r.get('oppId') != 545 and r['map'] + '/' + r['layout'] in MAPS]
mech = {}
for l in open(O / 'mechanisms.jsonl'):
    m = json.loads(l)
    mech[m['key']] = m['by']

def side_vals(g, t):
    c = g[t]['cp']; full = g['rounds'] == 500
    kd = g[t]['kd']; own = sum(1 for k in kd if k[4] == 1); enemy = sum(1 for k in kd if k[4] == 0 and k[2] == 'rammed'); ally = sum(1 for k in kd if k[4] == 0 and k[2] == 'allyHead')
    return {'h100': c.get('100', {}).get('heads'), 't250': c.get('250', {}).get('total'), 't400': c.get('400', {}).get('total'),
            'k500': c['500']['king'] if full else None, 'conv': (c['500']['king'] / c['400']['total']) if full and c.get('400', {}).get('total') else None,
            'kdOwn': own, 'kdEnemy': enemy, 'kdAlly': ally}

def agg(gs, who):
    vals = [side_vals(g, g['us'] if who == 'us' else ('B' if g['us'] == 'A' else 'A')) for g in gs]
    def mean(k): v = [x[k] for x in vals if x[k] is not None]; return (sum(v) / len(v), len(v)) if v else (None, 0)
    def med(k): v = [x[k] for x in vals if x[k] is not None]; return (st.median(v), len(v)) if v else (None, 0)
    out = {'n': len(gs), 'h100': mean('h100'), 't250': mean('t250'), 't400': mean('t400'), 'k500': med('k500'), 'k500mean': mean('k500'), 'conv': med('conv'),
           'kdOwn': sum(x['kdOwn'] for x in vals) / len(vals) if vals else None, 'kdEnemy': sum(x['kdEnemy'] for x in vals) / len(vals) if vals else None,
           'kdAlly': sum(x['kdAlly'] for x in vals) / len(vals) if vals else None, 'k500list': [x['k500'] for x in vals if x['k500'] is not None]}
    if who == 'us': out['wins'] = sum(g['winner'] == g['us'] for g in gs)
    return out

res = {}; md = []
f = lambda v, d=1: '–' if v is None else f'{v:.{d}f}'
for L in MAPS:
    gl = [g for g in games if g['map'] + '/' + g['layout'] == L]
    eras = ['W0–W4', 'W5–W9', 'W10–W12']; by = {e: [g for g in gl if ERA3(g['wave']) == e] for e in eras}
    res[L] = {'eras': {}}
    md.append(f'\n**{L}** (상위 6팀 판)\n')
    md.append('| 시기 | 판 | 승 | r100 머리 우리 / 상대 | r250 총길이 우리 / 상대 | r400 총길이 우리 / 상대 | 끝 최장 중앙 우리 / 상대 [500형 판] | 전환 비율 중앙 우리 / 상대 | 왕 죽음/판: 자기 움직임 · 적 박음 · 아군 박음 (우리) | 같은 값 (상대) |')
    md.append('|---|---|---|---|---|---|---|---|---|---|')
    for e in eras:
        gs = by[e]
        if not gs: continue
        u = agg(gs, 'us'); o = agg(gs, 'opp'); res[L]['eras'][e] = {'us': u, 'opp': o}
        md.append(f"| {e} | {u['n']} | {u['wins']} | {f(u['h100'][0])} / {f(o['h100'][0])} | {f(u['t250'][0])} / {f(o['t250'][0])} | {f(u['t400'][0])} / {f(o['t400'][0])} | "
                  f"{f(u['k500'][0], 1)} / {f(o['k500'][0], 1)} [{u['k500'][1]}] | {f(u['conv'][0], 2)} / {f(o['conv'][0], 2)} | {f(u['kdOwn'], 2)} · {f(u['kdEnemy'], 2)} · {f(u['kdAlly'], 2)} | {f(o['kdOwn'], 2)} · {f(o['kdEnemy'], 2)} · {f(o['kdAlly'], 2)} |")
    a = res[L]['eras']['W0–W4']; b_us = res[L]['eras']['W5–W9']['us']['k500list'] + res[L]['eras']['W10–W12']['us']['k500list']
    b_op = res[L]['eras']['W5–W9']['opp']['k500list'] + res[L]['eras']['W10–W12']['opp']['k500list']
    w0 = a['us']['wins']; n0 = a['us']['n']; w1 = res[L]['eras']['W5–W9']['us']['wins'] + res[L]['eras']['W10–W12']['us']['wins']; n1 = res[L]['eras']['W5–W9']['us']['n'] + res[L]['eras']['W10–W12']['us']['n']
    t_us = mw(a['us']['k500list'], b_us); t_op = mw(a['opp']['k500list'], b_op); pf = fisher(w0, n0 - w0, w1, n1 - w1)
    res[L]['tests'] = {'ourKing_W0W4_vs_W5W12': t_us, 'oppKing_W0W4_vs_W5W12': t_op, 'wins_fisher': pf}
    md.append(f"\n- 검정(W0–W4 대 W5–W12): 우리 끝 최장 Mann–Whitney z {f(t_us['z'], 2)}, p {pf_(t_us['p'])}; 상대 끝 최장 z {f(t_op['z'], 2)}, p {pf_(t_op['p'])}; 승 {w0}/{n0} 대 {w1}/{n1}, Fisher p {pf:.3f}.")
    # mechanism records per game by era
    md.append(f"\n기능 기록(판당, mech_check 기록 수; 우리 쪽):\n")
    md.append('| 시기 | 판 | ' + ' | '.join(MECH) + ' |'); md.append('|---|---|' + '---|' * len(MECH))
    res[L]['mech'] = {}
    for e in eras:
        gs = [g for g in by[e] if g['key'] in mech]
        if not gs: continue
        row = {k: sum(mech[g['key']].get(k, {}).get('n', 0) for g in gs) / len(gs) for k in MECH}; res[L]['mech'][e] = row
        md.append(f"| {e} | {len(gs)} | " + ' | '.join(f(row[k], 1) for k in MECH) + ' |')
    # per wave king (Autarky detail)
    if L == 'Autarky/a':
        md.append('\nAutarky 세부 시기(W5 뒤의 추가 토글): W5–W7 = csplit·F·no-exit s + mapid·bsp, W8–W9 = + floor·kcap + F2·cl, W10–W12 = + lsplit·fc·cov + lnt + gh·kx.\n')
        md.append('| 세부 시기 | 판 | 승 | r100 머리 | 끝 최장 중앙 우리 / 상대 [N] | 전환 비율 중앙 |'); md.append('|---|---|---|---|---|---|')
        fine = {}
        for e in ['W0–W4', 'W5–W7', 'W8–W9', 'W10–W12']:
            gs = [g for g in gl if ERA_A(g['wave']) == e]; u = agg(gs, 'us'); o = agg(gs, 'opp'); fine[e] = (u, o)
            md.append(f"| {e} | {u['n']} | {u['wins']} | {f(u['h100'][0])} | {f(u['k500'][0], 1)} / {f(o['k500'][0], 1)} [{u['k500'][1]}] | {f(u['conv'][0], 2)} |")
        t1 = mw(fine['W5–W7'][0]['k500list'], fine['W8–W9'][0]['k500list'] + fine['W10–W12'][0]['k500list'])
        t2 = mw(fine['W5–W7'][0]['k500list'] + fine['W8–W9'][0]['k500list'], fine['W10–W12'][0]['k500list'])
        t3 = mw(fine['W0–W4'][0]['k500list'], fine['W5–W7'][0]['k500list'])
        res[L]['fineTests'] = {'W0W4_vs_W5W7': t3, 'W5W7_vs_W8W12': t1, 'W5W9_vs_W10W12': t2}
        md.append(f"\n- 검정: W0–W4 대 W5–W7 z {f(t3['z'], 2)} p {pf_(t3['p'])}; W5–W7 대 W8–W12 z {f(t1['z'], 2)} p {pf_(t1['p'])}; W5–W9 대 W10–W12 z {f(t2['z'], 2)} p {pf_(t2['p'])}.")
        md.append('\n웨이브별 끝 최장 중앙(우리, 판 6씩): ' + ', '.join(f"{WN[w]} {st.median([g[g['us']]['cp']['500']['king'] for g in gl if g['wave'] == w and g['rounds'] == 500])}" for w in range(15)))
for L in res:
    for e in res[L]['eras'].values():
        e['us'].pop('k500list', None); e['opp'].pop('k500list', None)
(O / 'fortress.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
(O / 'fortress.md').write_text('\n'.join(md) + '\n')
print('\n'.join(md))
