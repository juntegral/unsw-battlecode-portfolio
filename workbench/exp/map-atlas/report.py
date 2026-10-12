"""report.py — renders the atlas tables (Korean) from the study caches (Claude, 2026-10-01).

Inputs (exp/map-atlas/cache): stats.json (analyze.py), extra.json (extra.py), compare.json (compare.py), solitaire.json,
geometry.json + geocheck.json, mechanisms.jsonl (per wave), recommend.json (recommend.py).
Output: exp/map-atlas/tables.md — one block per map/layout, each fenced by '<!-- lay:<map>/<layout> -->' markers, plus the
summary tables; assemble.py joins it with the narrative into research/observations/map-atlas.md.
"""
import json, pathlib, collections, math
O = pathlib.Path(__file__).resolve().parent / 'cache'
ORDER = ['Autarky/a', 'Prisoners Dilemma/6', 'Prisoners Dilemma/10', 'Portals/a', 'Trauma/a', 'Slithery Fight/a', 'Slithery Fight/b',
         'Schooltime/a', 'Schooltime/b', 'Default/a', 'Devil/a', 'Devil/b', 'Queen Of Spades/a', 'Queen Of Spades/b', 'Trophy/a']
LABEL = {'Prisoners Dilemma/6': 'Prisoners Dilemma 6마리(a)', 'Prisoners Dilemma/10': 'Prisoners Dilemma 10마리(PD10, policy b)'}
WN = ['W0a', 'W0b', 'W0c'] + [f'W{i}' for i in range(1, 13)]
PH = ['0–49', '50–99', '100–249', '250–349', '350–449', '450–499']

def lab(k): return LABEL.get(k, k.replace('/', ' '))
def f(v, d=1):
    if v is None: return '–'
    if isinstance(v, float) and (math.isnan(v)): return '–'
    return f'{v:.{d}f}' if isinstance(v, float) else str(v)
def pct(v, d=0): return '–' if v is None else f'{100 * v:.{d}f}%'
def wilson(k, n, z=1.96):
    if not n: return (None, None)
    p = k / n; b = 1 + z * z / n; c = (p + z * z / (2 * n)) / b; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / b; return (c - h, c + h)
def table(head, rows):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '|'.join(['---'] * len(head)) + '|']
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(out)

def load():
    S = json.loads((O / 'stats.json').read_text()); X = json.loads((O / 'extra.json').read_text())
    C = json.loads((O / 'compare.json').read_text()) if (O / 'compare.json').exists() else None
    P = json.loads((O / 'solitaire.json').read_text()) if (O / 'solitaire.json').exists() else {}
    G = json.loads((O / 'geometry.json').read_text()); GC = json.loads((O / 'geocheck.json').read_text())
    R = json.loads((O / 'recommend.json').read_text()) if (O / 'recommend.json').exists() else {}
    K = json.loads((O / 'kingsafe.json').read_text()); C2 = json.loads((O / 'cluster2.json').read_text())
    return S, X, C, P, G, GC, R, K, C2

BORDER = json.loads((O / 'border.json').read_text()) if (O / 'border.json').exists() else {}

def geo_table(g, gc):
    A = [s for s in g['starts'] if s['team'] == 'A']
    b = BORDER.get(g['map'] + '/' + g['layout'])
    starts = ', '.join(f"{s['len']}@({s['body'][0][0]},{s['body'][0][1]})" for s in A)
    rows = [
        ['크기 / 대칭', f"{g['W']}×{g['H']} / {g['sym']}"],
        ['감싸기(가장자리 해초: 위·아래 / 좌·우)', (f"위·아래 {b['topBottomWalled']}/{b['W']}, 좌·우 {b['leftRightWalled']}/{b['H']} 칸이 해초" + (' → 감싸기 없음' if b['topBottomWalled'] == b['W'] and b['leftRightWalled'] == b['H'] else ' → 완전 감싸기(토러스)' if b['topBottomWalled'] == 0 and b['leftRightWalled'] == 0 else ' → 일부 감싸기')) if b else '–'],
        ['해초 경계 / 밀도', f"{g['kelpEdges']} / {g['kelpDensity']:.2f} (경계 수 ÷ 2·칸 수)"],
        ['포털 쌍', g['portalPairs']],
        ['시작 드래곤(팀당)', f"{len(A)}마리, 길이 {sorted([s['len'] for s in A], reverse=True)}; A쪽 머리 {starts}"],
        ['생성 칸(A / B / 중립)', f"{g['spawnTerr'][1]} / {g['spawnTerr'][2]} / {g['spawnTerr'][0]} (전체 {g['spawnTiles']})"],
        ['샘(평균 간격 ≤12) 칸(A / B / 중립)', f"{g['fountainTerr'][1]} / {g['fountainTerr'][2]} / {g['fountainTerr'][0]}"],
        ['기대 생성량(진주/라운드, Σ2/(min+max))', f"전체 {g['capacity']:.2f}, 팀 영토당 {g['capTerr'][1]:.2f}, 중립 {g['capTerr'][0]:.2f}"],
        ['영토 칸(A / B / 같음)', f"{g['terrTiles'][1]} / {g['terrTiles'][2]} / {g['terrTiles'][0]} (시작 몸에서 경로 거리)"],
        ['머리 사이 경로 거리 / 토러스 맨해튼', f"{g['headPath'] if g['headPath'] is not None else '연결 없음'} / {g['headTorus']}  (독립 재계산 {gc['headPath'] if gc['headPath'] is not None else '연결 없음'})"],
        ['연결 성분(큰 셋)', f"{g['components']} ({', '.join(map(str, g['componentSizes'][:3]))}); 독립 재계산 {gc['components']}"],
        ['두 팀 사이 최소 정점 절단 / 영토 경계 변', f"{g['vertexCut']} / {g['frontierEdges']}"],
        ['간격 부류(min–max: 칸)', ', '.join(f"{c['gap'][0]}–{c['gap'][1]}: {c['tiles']}" for c in g['gapClasses'])],
        ['봇 표(mapdb/terrdb)와 불일치 칸', f"{g['botGapMismatch']} / {g['botTerrMismatch']}"],
    ]
    return table(['항목', '값'], rows)

def heads_table(x, xe):
    W, L, U = xe['W'], xe['L'], xe['U']; rows = []
    for r in [10, 25, 50, 100, 150, 250, 350]:
        def cell(s):
            h = s.get(f'heads{r}', {})
            if not h or not h.get('n'): return '–'
            return f"{h['mean']:.1f} ({h['median']:.0f}) [{h['n']}]"
        rows.append([f'r{r}', cell(W), cell(L), cell(U)])
    return table(['라운드', '승자 평균(중앙) [N]', '패자 평균(중앙) [N]', '우리 W0–W12 상위 6팀 평균(중앙) [N]'], rows)

def phase_table(x):
    W, L, U = x['elite']['W']['phase'], x['elite']['L']['phase'], x['ours']['phase']; rows = []
    for p in range(6):
        def sp(a): return f"{a['splitSpeed']['value']:.2f}" if a['splitSpeed']['value'] is not None else '–'
        def nat(a): return f"{a['naturalRate']['value']:.2f}" if a['naturalRate']['value'] is not None else '–'
        def raid(a): return pct(a['raidShare']['value']) if a['raidShare']['value'] is not None else '–'
        rows.append([PH[p], f"{sp(W[p])} / {sp(L[p])} / {sp(U[p])}", f"{nat(W[p])} / {nat(L[p])} / {nat(U[p])}",
                     f"{raid(W[p])} / {raid(L[p])} / {raid(U[p])}", f"{W[p]['games']} / {L[p]['games']} / {U[p]['games']}"])
    return table(['국면(라운드)', '분열 속도 승/패/우리 (분열 ÷ 길이≥4 머리-라운드)', '자연 진주 섭취/라운드 승/패/우리', '적 영토 머리 몫 승/패/우리', '판 수 승/패/우리'], rows)

def terr_table(x, xe):
    W, L, U = x['elite']['W'], x['elite']['L'], x['ours']
    def cpv(t, r, fld):
        v = t['cp'][str(r)][fld]; return v['mean'] if v['n'] else None
    rows = [['r100 영토 보로노이 몫(우리 쪽 생성 용량 중 우리 머리가 더 가까운 몫)', f(cpv(W, 100, 'vor'), 2), f(cpv(L, 100, 'vor'), 2), f(cpv(U, 100, 'vor'), 2)],
            ['r100 적이 더 가까운 몫', f(cpv(W, 100, 'enemyNear'), 2), f(cpv(L, 100, 'enemyNear'), 2), f(cpv(U, 100, 'enemyNear'), 2)],
            ['r100 적 영토 안 머리 수', f(cpv(W, 100, 'raid'), 1), f(cpv(L, 100, 'raid'), 1), f(cpv(U, 100, 'raid'), 1)],
            ['전멸당함(판 비율)', f"{W['eliminated']}/{W['n']}", f"{L['eliminated']}/{L['n']} ({pct(L['eliminationRate']['value'])})", f"{U['eliminated']}/{U['n']} ({pct(U['eliminationRate']['value'])})"],
            ['전멸 라운드 중앙(사분위)', '–', f"{f(L['elimRound'].get('median'), 0)} ({f(L['elimRound'].get('q25'), 0)}–{f(L['elimRound'].get('q75'), 0)})" if L['elimRound']['n'] else '–',
             f"{f(U['elimRound'].get('median'), 0)} ({f(U['elimRound'].get('q25'), 0)}–{f(U['elimRound'].get('q75'), 0)})" if U['elimRound']['n'] else '–']]
    return table(['지표', '승자', '패자', '우리'], rows)

def sac_table(x, xe):
    W, L, U = xe['W'], xe['L'], xe['U']; xw, xl, xu = x['elite']['W'], x['elite']['L'], x['ours']
    def on(s, k): o = s[k]; return f"{f(o.get('median'), 0)} ({f(o.get('q25'), 0)}–{f(o.get('q75'), 0)}) [{o['n']}]" if o.get('n') else '–'
    def fd(s, k): v = s['feed']; return v
    def near(s): v = s['feed']['nearLonger']; return f"{pct(v['le1'])} / {pct(v['le2'])} / {pct(v['le3'])} / {pct(v['le6'])}" if v['le3'] is not None else '–'
    def line(t): v = t['line']['sac300']; return f"{v['mean']:.1f} ({v['median']:.0f}) [{v['n']}]" if v['n'] else '–'
    def late(t): v = t['lateBirths']; return f"{v['mean']:.1f} [{v['n']}]" if v['n'] else '–'
    def l22(t): v = t['late22']; return f"{v['mean']:.1f}" if v['n'] else '–'
    rows = [['onset10 중앙(사분위) [N]', on(W, 'onset10'), on(L, 'onset10'), on(U, 'onset10')],
            ['onset20', on(W, 'onset20'), on(L, 'onset20'), on(U, 'onset20')],
            ['onset50', on(W, 'onset50'), on(L, 'onset50'), on(U, 'onset50')],
            ['r200 뒤 첫 희생', on(W, 'first200'), on(L, 'first200'), on(U, 'first200')],
            ['r300 뒤 희생 수 / 길이 (500형 판당)', f"{f(W['feed']['perGame'])} / {f(W['feed']['lengthPerGame'])}", f"{f(L['feed']['perGame'])} / {f(L['feed']['lengthPerGame'])}", f"{f(U['feed']['perGame'])} / {f(U['feed']['lengthPerGame'])}"],
            ['희생 길이 구성 2 / 3–4 / 5–7 / 8+', ' / '.join(pct(W['feed']['lenShare'][k]) for k in ['2', '3-4', '5-7', '8+']), ' / '.join(pct(L['feed']['lenShare'][k]) for k in ['2', '3-4', '5-7', '8+']), ' / '.join(pct(U['feed']['lenShare'][k]) for k in ['2', '3-4', '5-7', '8+'])],
            ['먹이 반경: 더 긴 아군 머리까지 ≤1 / ≤2 / ≤3 / ≤6', near(W), near(L), near(U)],
            ['떨군 진주 중 우리 팀이 먹은 몫 / 최종 왕 계보 몫(우리 팀 섭취 중)', f"{pct(W['feed']['ownEat'])} / {pct(W['feed']['lineShareOfOwn'])}", f"{pct(L['feed']['ownEat'])} / {pct(L['feed']['lineShareOfOwn'])}", f"{pct(U['feed']['ownEat'])} / {pct(U['feed']['lineShareOfOwn'])}"],
            ['왕 계보 희생 진주 r300–499 평균(중앙) [500형 N]', line(xw), line(xl), line(xu)],
            ['r250 뒤 작은 조각(≤3) 탄생 / 그중 2+2', f"{late(xw)} / {l22(xw)}", f"{late(xl)} / {l22(xl)}", f"{late(xu)} / {l22(xu)}"]]
    return table(['지표', '승자', '패자', '우리'], rows)

def king_table(x, xe, ks):
    xw, xl, xu = x['elite']['W'], x['elite']['L'], x['ours']; W, L, U = xe['W'], xe['L'], xe['U']
    def kp(s):
        k = ks[s]
        if not k.get('kingRounds'): return '–'
        if k['median'] >= 31: return f"적 머리에 닿는 길 없음 또는 31+ (왕-라운드 {k['kingRounds']})"
        return f"{pct(k['le3'], 1)} / {pct(k['le6'])} / 10분위 {k['p10']} / 중앙 {k['median']} [{k['kingRounds']}]"
    def kpd(s):
        k = ks[s]
        if not k.get('kingDeaths'): return f"0 [{k.get('games', 0)}판]"
        return f"{f(k['kingDeathsPerGame'], 2)}/판 [{k['kingDeaths']}]; 그 라운드 거리 중앙 {k['deathDistMedian'] if k['deathDistMedian'] is not None and k['deathDistMedian'] < 999 else '닿지 않음'}, ≤3 {pct(k['deathDistLe3'])}; 죽인 쪽 길이 중앙 {k['killerLenMedian'] if k['killerLenMedian'] is not None else '–'}"
    def v(t, k, d=1): s = t['line'][k]; return f"{s['mean']:.{d}f} ({s['median']:.{max(0, d - 1)}f})" if s.get('n') else '–'
    def ex(s): e = s['kingExposure']; return f"{pct(e['near3'])} / {pct(e['near6'])} [{e['kingRounds']}]" if e['kingRounds'] else '–'
    def kd(s):
        k = s['kingDeaths']
        if not k['games']: return '–'
        c = ', '.join(f'{a} {b}' for a, b in sorted(k['causes'].items(), key=lambda z: -z[1])[:3])
        kl = k['killerLen']; return f"{f(k['perGame'], 2)}/판 [{k['events']}/{k['games']}]; {c}; 죽인 쪽 길이 중앙 {f(kl.get('median'), 0)}" if k['events'] else f"0 [{k['games']}]"
    rows = [['500형 판 수', xw['line']['fullN'], xl['line']['fullN'], xu['line']['fullN']],
            ['r300 최장 평균(중앙)', v(xw, 'current300'), v(xl, 'current300'), v(xu, 'current300')],
            ['r400 최장', v(xw, 'current400'), v(xl, 'current400'), v(xu, 'current400')],
            ['r500 최장', v(xw, 'final'), v(xl, 'final'), v(xu, 'final')],
            ['r300 때 최종 왕 계보 길이', v(xw, 'ancestor300'), v(xl, 'ancestor300'), v(xu, 'ancestor300')],
            ['최장 성장/라운드 r300–500 · r400–500', f"{v(xw, 'growth300', 2)} · {v(xw, 'growth400', 2)}", f"{v(xl, 'growth300', 2)} · {v(xl, 'growth400', 2)}", f"{v(xu, 'growth300', 2)} · {v(xu, 'growth400', 2)}"],
            ['왕(≥8) 노출: 적 머리 ≤3 / ≤6 (r300–499, 토러스 맨해튼, Codex 정의) [왕-라운드]', ex(W), ex(L), ex(U)],
            ['왕(≥8)과 가장 가까운 적 머리의 경로 거리: ≤3 / ≤6 / 10분위 / 중앙 [왕-라운드] (kingpath.js)', kp('W'), kp('L'), kp('U')],
            ['r300 뒤 왕 죽음(판당, 원인, 죽인 쪽 길이; Codex 정의)', kd(W), kd(L), kd(U)],
            ['r300 뒤 왕 죽음과 그 라운드 시작 때 적 머리 경로 거리 (kingpath.js)', kpd('W'), kpd('L'), kpd('U')]]
    return table(['지표', '승자', '패자', '우리'], rows)

def mass_table(xe):
    W, L, U = xe['W'], xe['L'], xe['U']
    def t(s, r): v = s[f'total{r}']; return f"{v['mean']:.1f} ({v['median']:.0f}) [{v['n']}]" if v.get('n') else '–'
    def c(s): v = s['conversion']; return f"{v['median']:.2f} ({v['q25']:.2f}–{v['q75']:.2f}) [{v['n']}]" if v.get('n') else '–'
    def h(s): v = s['heads500']; return f"{v['median']:.0f} [{v['n']}]" if v.get('n') else '–'
    rows = [[f'총길이 r{r} 평균(중앙) [이어진 판]', t(W, r), t(L, r), t(U, r)] for r in [100, 250, 300, 400]]
    rows.append(['전환 비율 = r500 최장 ÷ r400 총길이, 중앙(사분위) [500형 판]', c(W), c(L), c(U)])
    rows.append(['r500 살아 있는 수 중앙 [500형 판]', h(W), h(L), h(U)])
    return table(['지표', '승자', '패자', '우리'], rows)

NAMES = {'heads25': 'r25 머리', 'heads50': 'r50 머리', 'heads100': 'r100 머리', 'heads250': 'r250 머리', 'vor100': 'r100 보로노이 몫',
         'enemyNear100': 'r100 적이 더 가까운 몫', 'split0': '분열 속도 r0–49', 'nat100': '자연 진주 r0–99', 'raid100': '적 영토 머리 몫 r0–99',
         'lateBirths': 'r250 뒤 조각 탄생', 'lineSac300': '왕 계보 희생 진주 r300+', 'sac300Len': 'r300 뒤 희생 길이', 'king500': 'r500 최장(점수)',
         'onset20': '희생 onset20', 'exposure6': '왕 노출 ≤6'}

def wins_table(x):
    rows = []
    for m, p in sorted(x['paired'].items(), key=lambda kv: -abs(kv[1]['standardized'] or 0)):
        if p['n'] < 20 or p['standardized'] is None: continue
        ta = p['teamAgreement']; rows.append([NAMES.get(m, m), p['n'], f(p['winner'], 2 if abs(p['winner'] or 0) < 2 else 1), f(p['loser'], 2 if abs(p['loser'] or 0) < 2 else 1),
                     f(p['delta'], 2 if abs(p['delta']) < 2 else 1), f(p['standardized'], 2), pct(p['positive']['value']), f"{ta['num']}/{ta['den']}",
                     f"{f(p['seatA']['mean'], 2 if abs(p['seatA']['mean'] or 0) < 2 else 1)} / {f(p['seatB']['mean'], 2 if abs(p['seatB']['mean'] or 0) < 2 else 1)}"])
    return table(['지표(승자−패자, 같은 판)', 'N', '승자', '패자', '차', '표준화 차(차÷SD)', '승자가 큰 판', '팀 일치(자기 승 vs 패)', '좌석 A승 / B승 차'], rows)

def ours_table(x, key):
    O = x['ours']; D = x['dev']; E = x['early']
    lo, hi = wilson(O['wins'], O['n'])
    waves = ' '.join(f"{w} {v['wins']}/{v['n']}" for w, v in x['waves'].items() if v['n'])
    early = ', '.join(f"{s} {v['wins']}/{v['n']}" for s, v in x['earlySets'].items() if v['n'])
    k = O['cp']['500']['king']
    rows = [['상위 6팀 승 / 판 (95% 구간)', f"{O['wins']}/{O['n']} ({pct(lo)}–{pct(hi)})"],
            ['DEV 545 승 / 판', f"{D['wins']}/{D['n']}"],
            ['이전 계열 승 / 판', f"{E['wins']}/{E['n']} ({early})"],
            ['전멸당함', f"{O['eliminated']}/{O['n']}"],
            ['끝 최장 평균(전멸 0 포함) / 500형 판만', f"{f(k['mean'])} / {f(O['line']['final'].get('mean'))} [{O['line']['fullN']}]"],
            ['자연 진주 섭취 몫(우리 ÷ 둘 합)', f"{pct(O['intakeShare']['value'])} ({O['natural']} / {O['natural'] + O['enemyNatural']})"],
            ['왕 계보 희생 진주 r300–499', f"{f(O['line']['sac300'].get('mean'))} [{O['line']['sac300'].get('n', 0)}]"],
            ['웨이브별 승/판', waves]]
    return table(['항목', '값'], rows)

MECH_ORDER = ['csplit', 'lsplit', 'frag', 'F', 'F2', 'cl', 'cov', 'conv', 'feed', 'g', 'grab', 'tg', 'esc', 'escape-split', 'no-exit', 'esc-split', 'portal', 'floor', 'kcap', 'bsp', 'lnt veto', 'pf']
MK = {'csplit': 'csplit', 'lsplit': 'lsplit', 'frag': 'frag', 'F': 'fguard', 'cl': 'cl', 'cov': 'cov', 'conv': 'conv', 'feed': 'feed', 'g': 'gather', 'grab': 'grab', 'tg': 'tg',
      'escape-split': 'escsplit', 'esc-split': 'escsplit2', 'no-exit': 'noexit', 'esc': 'esc', 'portal': 'portal', 'floor': 'floor', 'kcap': 'kcap', 'bsp': 'bsplit', 'lnt veto': 'lntv', 'pf': 'pf'}

def mech_table(x, per_wave):
    M = x['mechanisms']; rows = []
    for m in MECH_ORDER:
        v = M.get(m)
        if v is None: continue
        if m == 'F2':
            if v['n'] == 0:
                rows.append(['F2', '–', 0, '–', '–', '–', '–', '–']); continue
            rows.append(['F2', '–', v['n'], '–', f"{pct(v['successRate']['value'])} [{v['okN']}]", '–', '–', '–']); continue
        if v['n'] == 0:
            rows.append([m, f"0/{v['games']}", 0, '0.0', '–', '–', '–', '–']); continue
        waves = per_wave.get(m, [])
        rows.append([m, f"{v['fireGames']}/{v['games']}", v['n'], f(v['per1000Turns']['value'], 1), f"{pct(v['successRate']['value'])} [{v['okN']}]" if v['okN'] else '–',
                     f(v['adjustedWinCorrelation'], 2), f(v['kingCorrelation'], 2), ' '.join(waves) if waves else '–'])
    return table(['기능', '발동 판/판(상위 7팀)', '발동 수', '1000차례당', '의도 효과(mech_check 기준) [N]', '승 상관(웨이브·상대 고정효과 뺀 뒤)', '끝 최장 상관', '발동한 웨이브'], rows)

def per_wave_mech():
    """{layout: {mechanism label: [wave names where it fired]}} from mechanisms.jsonl joined to raw rows."""
    raw = {}
    for l in open(O / 'raw.jsonl'):
        r = json.loads(l)
        if r['src'] == 'online' and r.get('wave') is not None: raw[r['key']] = (r['map'] + '/' + r['layout'], r['wave'])
    out = collections.defaultdict(lambda: collections.defaultdict(set))
    for l in open(O / 'mechanisms.jsonl'):
        m = json.loads(l)
        if m['key'] not in raw: continue
        lay, w = raw[m['key']]
        for lab_, k in MK.items():
            if m['by'].get(k, {}).get('n', 0) > 0: out[lay][lab_].add(w)
    return {lay: {k: [WN[i] for i in sorted(v)] for k, v in d.items()} for lay, d in out.items()}

def compact_waves(ws):
    return ws

def compare_table(C, key):
    a, b = C['codex'].get(key), C['recount'].get(key)
    if not a or not b: return ''
    rows = []
    for n in a:
        x, y = a[n], b.get(n, [None, 0])
        rows.append([n, f"{f(x[0], 3 if isinstance(x[0], float) and abs(x[0]) < 2 else 1)} [{x[1]}]", f"{f(y[0], 3 if isinstance(y[0], float) and abs(y[0]) < 2 else 1)} [{y[1]}]", '같음' if x == y else '다름'])
    return table(['핵심 수치', '파이프라인(extract.js → 집계)', '독립 재계산(recount.js)', '대조'], rows)

def wave_rows():
    """{layout: {wave index: accumulators}} from raw.jsonl (our W0-W12 top-6 games)."""
    acc = collections.defaultdict(lambda: collections.defaultdict(lambda: {'n': 0, 'w': 0, 'e': 0, 'h100': [], 'k500': [], 'nat': 0, 'natE': 0, 'split0': [0, 0]}))
    for l in open(O / 'raw.jsonl'):
        r = json.loads(l)
        if r['src'] != 'online' or r.get('wave') is None or r.get('oppId') == 545: continue
        a = acc[r['map'] + '/' + r['layout']][r['wave']]; u = r['us']; e = 'B' if u == 'A' else 'A'
        a['n'] += 1; a['w'] += r['winner'] == u; a['e'] += r[u]['cp']['500']['heads'] == 0
        if '100' in r[u]['cp']: a['h100'].append(r[u]['cp']['100']['heads'])
        if r['rounds'] == 500: a['k500'].append(r[u]['cp']['500']['king'])
        a['nat'] += sum(p['nat'] for p in r[u]['phase']); a['natE'] += sum(p['nat'] for p in r[e]['phase'])
        a['split0'][0] += r[u]['phase'][0]['splits']; a['split0'][1] += r[u]['phase'][0]['eligibleHR']
    return acc

def wave_table(acc):
    rows = []
    for w in sorted(acc):
        a = acc[w]
        rows.append([WN[w], f"{a['w']}/{a['n']}", f"{a['e']}/{a['n']}", f(sum(a['h100']) / len(a['h100'])) if a['h100'] else '–',
                     f"{sorted(a['k500'])[len(a['k500']) // 2]} [{len(a['k500'])}]" if a['k500'] else '–',
                     pct(a['nat'] / (a['nat'] + a['natE'])) if a['nat'] + a['natE'] else '–', f(a['split0'][0] / a['split0'][1], 2) if a['split0'][1] else '–'])
    return table(['웨이브', '승/판', '전멸/판', 'r100 머리 평균', '끝 최장 중앙 [500형 판]', '자연 섭취 몫', '분열 속도 r0–49'], rows)

def legacy_mech_pivot():
    """Per mechanism x map: the online wave reports' per-map lines ('- 지도별:'), pooled over reports (n-weighted rate)."""
    M = json.loads((O / 'mechanism-reports.json').read_text())
    maps = ['Autarky', 'Prisoners Dilemma', 'Portals', 'Trauma', 'Slithery Fight', 'Schooltime', 'Default', 'Devil', 'Queen Of Spades', 'Trophy']
    piv = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0.0, 0, set()]))
    for m in M:
        src = m['source'].split('/')[-1]
        if not (src.startswith('mech-cand-stack') or src.startswith('mech-merge2')): continue
        sec = m['section'].lstrip('# ').strip(); a = piv[sec][m['map']]
        a[0] += m['n']; a[3].add(src)
        if m['rate'] is not None: a[1] += m['rate'] * m['n']; a[2] += m['n']
    rows = []
    for sec, d in sorted(piv.items(), key=lambda kv: -sum(v[0] for v in kv[1].values())):
        rows.append([sec] + [(f"{pct(d[mp][1] / d[mp][2])} ({d[mp][0]})" if d[mp][2] else (f"– ({d[mp][0]})" if d[mp][0] else '')) for mp in maps] + [len(set().union(*[v[3] for v in d.values()]))])
    return table(['기능(보고서 절)'] + maps + ['보고서 수'], rows)

ENG_NOTE = {'Autarky/a': '요새(F), W4 시대 경제로', 'Prisoners Dilemma/6': '요새(F), W4 시대 경제로', 'Prisoners Dilemma/10': '요새(F) 유지(약함, 혼합 후보)',
            'Schooltime/b': '전멸형 전문(EL, 느린형)', 'Queen Of Spades/a': '전멸형 전문(EL, 느린형)', 'Queen Of Spades/b': '전멸형 전문(EL, 느린형)'}
ENG = {'F': '요새(F)', 'F→SL': '요새 유지 → 요새+전환(F+C) 로컬 검증', 'SE': '떼 경제(SE)', 'EL': '전멸형 전문(EL)'}

def summary_table(A, X, R, G, K):
    rows = []
    for key in ORDER:
        x = A[key]; r = R[key]; g = G[key]; xe = X[key]; k = K[key]
        feat = f"{g['W']}×{g['H']}, 시작 {len([s for s in g['starts'] if s['team'] == 'A'])}마리, 경로 {g['headPath'] if g['headPath'] is not None else '없음'}, 생성량 {g['capacity']:.1f}/라운드, 전멸 {pct(r['eliminationRate'])}"
        elite = f"머리 {r['heads']['100']}·{r['heads']['250']} (r100·r250), 분열 {r['split'][0]:.2f}, 시계 {r['clockStart50']}, 끝 최장 {f(r['king500W'], 0)}/{f(r['king500L'], 0)}"
        ours = f"{r['oursWins']}/{r['oursN']}승, 전멸 {r['oursElim']}, r100 {f(r['oursHeads']['100'])}마리, 분열 {f(r['splitOurs'][0], 2)}, 끝 최장 {f(r['oursKing500'], 0)}"
        rows.append([lab(key), feat, elite, ours, ENG_NOTE.get(key, ENG[r['engine']])])
    return table(['지도(판본)', '핵심 특징 [사실]', '상위권 승자 목표 (끝 최장 승/패 중앙) [사실]', '우리 W0–W12 상위 6팀 [사실]', '권장 엔진 [해석]'], rows)

def policy_table(R, K):
    rows = []
    for key in ORDER:
        r = R[key]; k = K[key]['W']; fam, lay = r['policyRow']
        tr = r['trade']; dis = tr.get('disadvantage', {}).get('netPer')
        stance = '교환 없음(접촉 불가)' if not tr else ('d8 ≤ −3 거부' if dis is not None and dis < 0 else 'd8 ≤ −3도 손해 아님(거부 안 함)')
        ksafe = '적이 닿지 않음' if k.get('median', 0) >= 31 and key == 'Portals/a' else f"하한 4 / 목표 {max(6, min(10, k['p10']))} (승자 ≤3 {pct(k['le3'], 1)}, 10분위 {k['p10']})"
        rows.append([f'{{"{fam}", \'{lay}\'}}', ENG[r['engine']].split('(')[-1].rstrip(')') if r['engine'] != 'F→SL' else 'F → F+C',
                     ' / '.join(str(r['heads'][str(h)]) for h in [10, 25, 50, 100, 250]), f"{r['split'][0]:.2f} / {r['split'][1]:.2f}",
                     f"{r['clockStart50']} (onset20 {f(r['onset20'].get('median'), 0)}, onset50 {f(r['onset50'].get('median'), 0)})",
                     f"3 (≤2 {pct(r['feedNear']['le2'])}, ≤3 {pct(r['feedNear']['le3'])})", stance, ksafe])
    return table(['policy 행 {fam, layout}', '엔진', 'headsR10 / R25 / R50 / R100 / R250', 'splitRate r0–49 / r50–99', 'convClock (onset20, onset50)', '먹이 반경 CONV_MAX_DIST', '교환 자세', '왕 안전 경로 거리'], rows)

def cluster_tables(S, C2):
    cl = S['cluster']; out = []
    feats = cl['features']; rows = []
    for lab_, v in zip(cl['labels'], cl['rawFeatures']): rows.append([lab_] + [f(x, 2) if isinstance(x, float) else str(x) for x in v])
    out.append('**군집 A(Codex 정의, 상위권 승자 행동 수준 11개)**\n\n' + table(['판본'] + feats, rows))
    out.append('실루엣: ' + ', '.join(f"k={k} {v:.3f}" for k, v in cl['silhouettes'].items()) + '\n\n' + '\n'.join(f"- k={k}: " + ' | '.join('{' + ', '.join(g) + '}' for g in gs) for k, gs in sorted(cl['cuts'].items(), key=lambda kv: int(kv[0]))))
    feats2 = C2['features']; rows = []
    for lab_, v in C2['raw'].items(): rows.append([lab_] + [f(x, 2) for x in v])
    out.append('**군집 B(새로 추가, 무엇이 가르나: 같은 판 승자−패자 표준화 차 8개 + 전멸 비율 + 연결 여부)**\n\n' + table(['판본'] + feats2, rows))
    out.append('실루엣: ' + ', '.join(f"k={k} {v:.3f}" for k, v in C2['silhouettes'].items()) + '\n\n' + '\n'.join(f"- k={k}: " + ' | '.join('{' + ', '.join(g) + '}' for g in gs) for k, gs in sorted(C2['cuts'].items(), key=lambda kv: int(kv[0]))))
    # distance matrix of B, short labels
    labs = list(C2['raw'].keys()); short = {l: l.replace('Prisoners Dilemma', 'PD').replace('Queen Of Spades', 'QoS').replace('Slithery Fight', 'Sli').replace('Schooltime', 'Sch').replace('/a', 'a').replace('/b', 'b').replace('/6', '6').replace('/10', '10') for l in labs}
    rows = [[short[a]] + [f(C2['distances'][a][b], 2) for b in labs] for a in labs]
    out.append('**군집 B 거리(표준화 특징의 유클리드 거리 ÷ √특징 수)**\n\n' + table([''] + [short[b] for b in labs], rows))
    return '\n\n'.join(out)


def decision_table(A):
    """Decision rows (data/decisions, per dragon turn; Codex decisions.cpp over 1.18e8 rows): split per eligible (L >= 4)
    weighted turn, the B3 ram rate (a piece L <= 4 with an adjacent enemy head of length >= L that rams), 'suicide' actions per game."""
    rows = []
    for key in ORDER:
        x = A[key]; d = x['decisions']; o = x['decisionOurs']
        def g(t, k): v = t.get(k); return f"{v['value']:.2f}" if v and v.get('value') is not None else '–'
        def n(t, k): return t.get(k, 0)
        rows.append([lab(key), f"{d['W']['games']} / {o['games']}", f"{g(d['W'], 'splitEligible')} / {g(d['L'], 'splitEligible')} / {g(o, 'splitEligible')}",
                     f"{g(d['W'], 'B3Rate')} / {g(d['L'], 'B3Rate')} / {g(o, 'B3Rate')} [{n(d['W'], 'adjacentLongestB3N')} / {n(o, 'adjacentLongestB3N')}]",
                     f"{d['W'].get('suicideActionN', 0) / max(1, d['W']['games']):.1f} / {o.get('suicideActionN', 0) / max(1, o['games']):.1f}"])
    return table(['판본', '판(승자 쪽 / 우리)', '길이≥4 차례당 분열 승/패/우리', 'B3 박음률 승/패/우리 [기회 승자 / 우리]', '행동 없음(자결) 판당 승자 / 우리'], rows)

def main():
    S, X, C, P, G, GC, R, K, C2 = load(); A = S['atlas']; pw = per_wave_mech(); wr = wave_rows(); out = []
    for key in ORDER:
        x = A[key]; xe = X[key]; g = G[key]; gc = GC[key]
        out.append(f'<!-- lay:{key} -->')
        out.append(f"#### 기하와 배치 [사실]\n\n{geo_table(g, gc)}\n")
        out.append(f"#### 상위권 머리 곡선 [사실]\n\n상위권 N = {x['n']}판(멈춘 팀 판 {x['excluded']}판 제외), 승부가 난 판 {x['n'] - x['draws']}, 팀 {x['teamN']}, 대전 {x['battleN']}. 괄호 [N]은 그 라운드까지 이어진 판 수다(끝난 판의 값은 채우지 않는다).\n\n{heads_table(x, xe)}\n")
        out.append(f"#### 국면별 분열·섭취·습격 [사실]\n\n{phase_table(x)}\n")
        out.append(f"#### 영토와 전멸 [사실]\n\n{terr_table(x, xe)}\n")
        out.append(f"#### 질량과 전환 [사실]\n\n{mass_table(xe)}\n")
        out.append(f"#### 희생 시계·양·먹이 반경 [사실]\n\n{sac_table(x, xe)}\n")
        out.append(f"#### 왕 [사실]\n\n{king_table(x, xe, K[key])}\n")
        out.append(f"#### 무엇이 이기나: 같은 판 승자−패자 [사실]\n\n{wins_table(x)}\n")
        out.append(f"#### 우리 성적 W0–W12 [사실]\n\n{ours_table(x, key)}\n\n웨이브별(상위 6팀 판):\n\n{wave_table(wr[key])}\n")
        out.append(f"#### 기능별 발동과 적용 W0–W12(상위 7팀 판) [사실, 상관은 교란 있음]\n\n{mech_table(x, pw.get(key, {}))}\n")
        if C: out.append(f"#### 독립 재계산 대조\n\n{compare_table(C, key)}\n")
        out.append(f'<!-- /lay:{key} -->\n')
    out.append('<!-- global:summary -->\n' + summary_table(A, X, R, G, K) + '\n<!-- /global:summary -->\n')
    out.append('<!-- global:policy -->\n' + policy_table(R, K) + '\n<!-- /global:policy -->\n')
    out.append('<!-- global:cluster -->\n' + cluster_tables(S, C2) + '\n<!-- /global:cluster -->\n')
    out.append('<!-- global:legacymech -->\n' + legacy_mech_pivot() + '\n<!-- /global:legacymech -->\n')
    out.append('<!-- global:decisions -->\n' + decision_table(A) + '\n<!-- /global:decisions -->\n')
    (pathlib.Path(__file__).resolve().parent / 'tables.md').write_text('\n'.join(out))
    print('tables.md', sum(len(s) for s in out), 'chars')

if __name__ == '__main__':
    main()
