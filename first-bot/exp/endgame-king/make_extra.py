# Run-dependent texts of research/observations/endgame-king.md (population row, limit 1, recount of the full pass, the
# changes note and the note on the proposals' threshold basis), written to exp/endgame-king/narrative-extra.json for
# narrative.py. Inputs: numbers-wl.json (full), numbers-wl-old.json (committed doc), changes.json (diff_numbers.js),
# recount-new300.txt, the key snapshot files. usage: python3 exp/endgame-king/make_extra.py
import json, pathlib, re
D = pathlib.Path(__file__).resolve().parent
N = json.loads((D / 'numbers-wl.json').read_text(encoding='utf8'))
O = json.loads((D / 'numbers-wl-old.json').read_text(encoding='utf8'))['N']
NN = N['N']
CH = json.loads((D / 'changes.json').read_text(encoding='utf8')) if (D / 'changes.json').exists() else []
keys = lambda f: [l for l in (D / f).read_text(encoding='utf8').split('\n') if l.strip()]
snap_all, snap_r500, snap_elim = len(keys('top-keys-2246.keys')), len(keys('top-keys-2246-r500.keys')), len(keys('top-keys-2246-elim.keys'))
old_all = len(keys('top-keys-2126.keys'))
cache_keys = set()
for l in (D.parents[1] / '.cache/endgame-king/top.jsonl').read_text(encoding='utf8').split('\n'):
    m = re.match(r'^\{"key":"([^"]+)"', l)
    if m: cache_keys.add(m.group(1))
r500_done = sum(1 for k in keys('top-keys-2246-r500.keys') if k in cache_keys)
elim_done = sum(1 for k in keys('top-keys-2246-elim.keys') if k in cache_keys)
new_r500 = snap_r500 - 7252
ml_snap = json.loads((D / 'ml-snapshot.json').read_text(encoding='utf8'))['at'] if (D / 'ml-snapshot.json').exists() else '2026-09-30 11:34 KST'
elim_src = f"질량 장부 캐시({ml_snap}의 `data/top` 전부, {int(NN['n_ml']):,}판 읽음·{int(NN['n_ml_kept']):,}판 남김)" if N['elimLineage'] == 'ml' else '이 연구의 추출'
fmt = lambda v: f"{v:,}"
E = {}
E['POP_ROW'] = (f"| 상위권끼리(`data/top`) | 키 스냅숏 {fmt(snap_all)}판(`exp/endgame-king/top-keys-2246.keys`, 2026-09-30 22:46 KST의 `index.jsonl` 전부) | "
  f"500라운드형 {fmt(snap_r500)}판(21:10 스냅숏 7,252판 + 그 뒤 {new_r500}판), 전멸형 {fmt(snap_elim)}판. 멈춘 팀(분열 ≤3, 음파 0)·시간 초과 사망 ≥3 판을 뺐다(`exp/mass-analysis/report.js`와 같은 규칙). "
  f"표의 \"상위권 승자·패자\". **이 연구의 추출은 500라운드형 {fmt(r500_done)}판 전부를 담는다(규칙으로 남김 {int(NN['n_r500_kept']):,}판, 500라운드까지 간 팀-경기 승자·패자 {int(NN['W_n_full']):,}씩).** "
  f"1–2절의 500라운드형 계보와 3–5절의 상위권 값이 이 전체 추출이다. 전멸형 계보(T1e·T1f)는 {elim_src}다(이 연구의 추출은 전멸형 {fmt(elim_done)}판뿐) |")
E['LIMIT_POP'] = (f"1–5절의 500라운드형 상위권 승자·패자 값은 22:46 KST 스냅숏의 500라운드형 {fmt(snap_r500)}판 전부(규칙으로 남김 {int(NN['n_r500_kept']):,}판)다. "
  "추출은 다른 에이전트의 로컬 경기와 겹쳐(load 150–250) 작업 2개, nice 15로 돌았다. 그 뒤 수집된 판은 들어가지 않는다. "
  f"전멸형 계보(T1e·T1f)는 {elim_src}다. 이 연구의 추출이 전멸형은 {fmt(elim_done)}판뿐이기 때문이다. "
  "판마다 계보 분해는 장부와 같다(점검 lin). 노출은 전환 사슬 캐시의 전체 스냅숏(r300·350·400·450, 5,229판)으로도 확인했다. "
  "처음 문서(커밋 175f2e7)의 상위권 값은 21:10 스냅숏 가운데 추출된 500라운드형 4,257판(남김)과 질량 장부 캐시에서 나왔다. 전체로 다시 센 차이는 맨 앞 '전체 모집단으로 다시 셈' 절에 있다.")
# recount of the new games
rc = (D / 'recount-new300.txt').read_text(encoding='utf8') if (D / 'recount-new300.txt').exists() else ''
m1 = re.search(r'games (\d+)', rc); m2 = re.search(r'mismatches \(expected 0\): (\{.*\})', rc); m3 = re.search(r'totals: (\{.*\})', rc)
if m1 and m2 and m3:
    mm, tt = json.loads(m2.group(1)), json.loads(m3.group(1))
    zero = all(v == 0 for v in mm.values())
    E['RECOUNT_FULL'] = (f"전체 추출을 마친 뒤, 재개한 추출이 새로 뽑은 판 가운데 씨앗을 고정한 무작위 {m1.group(1)}판(`exp/endgame-king/recount-new300.keys`, `pick_new300.js`)을 다시 돌려 "
      + ("15개 양 모두 불일치 0이다" if zero else f"불일치가 있다: {json.dumps(mm)}") +
      f"(`recount-new300.txt`; 합계 계보 팀-경기 {tt['lineTeams']:,}, 계보의 자연 진주 {tt['nat']:,} · 우리 사망 진주 {tt['own']:,} · 적 사망 진주 {tt['enemy']:,}, r340 무리 {tt['cohN']:,}, 그 둘레 자연 진주 {tt['cohSp']:,}).")
else:
    E['RECOUNT_FULL'] = ''
# changes note
def unit_txt(u): return {'%p': '%p', '0.01': '', '0.1': '', '1': ''}[u]
def fv(r, v): return (f"{v:.0f}" if r['u'] == '%p' else f"{v:.2f}" if r['u'] in ('0.01', '0.1/판') else f"{v:.1f}").replace('-', '−')
GRP = {'W': '승자', 'L': '패자', 'X': '우리 판의 상대'}
MAPS = {'Autarky': 'Autarky', 'Portals': 'Portals', 'Schooltime': 'Schooltime', 'SlitheryFight': 'Slithery Fight', 'Trauma': 'Trauma', 'min': '가장 작은 쪽', 'max': '가장 큰 쪽',
        'a': 'r300–399', 'b': 'r400–499', 'g': '성장/라운드', 'sac': '희생 진주', 'nat': '자연 진주', 'L300': 'L300', 'fin': '끝 왕', 'cost': '질주·분열', 'n': '팀-경기',
        'en': '적 머리', 'ally': '아군 머리', 'L': '길이', 'rank': '순위', 'dK': '왕까지', 'enB': '적 몫(앞)', 'enA': '적 몫(뒤)', 'selfB': '자기 몫(앞)', 'selfA': '자기 몫(뒤)', 'toline': '계보에 준 진주', 'pg': '판당 수'}
FIXED = {'OW_dfin': 'stack5–7 끝 왕 − 승자 끝 왕', 'OW_dsac': 'stack5–7 − 승자 희생 진주', 'OW_dL300': 'stack5–7 − 승자 L300', 'OW_dnat': 'stack5–7 − 승자 자연 진주',
         'OW_doth': 'stack5–7 − 승자 다른 사망 진주', 'OW_dsplit': 'stack5–7 − 승자 분열', 'OW_mapratio_min': 'stack5–7 희생 진주 ÷ 승자(지도별 가장 작은 곳)',
         'OW_mapratio_max': 'stack5–7 희생 진주 ÷ 승자(지도별 가장 큰 곳)', 'WM_dfin_min': '승자 끝 왕 − merge2·stack1–4 끝 왕(작은 쪽)', 'WM_dfin_max': '승자 끝 왕 − merge2·stack1–4 끝 왕(큰 쪽)',
         'WL_dL300': '승자 − 패자 L300', 'WL_dsac': '승자 − 패자 희생 진주', 'WL_dsplitloss': '승자 − 패자 분열 손실', 'WL_dnat': '승자 − 패자 자연 진주', 'WL_dfin': '승자 − 패자 끝 왕'}
STEM = [(r'^fin_kng$', '끝 왕(r340 왕이 끝까지 간 판)'), (r'^fin_coh$', '끝 왕(무리에서 나온 판)'), (r'^L300$', 'L300(계보)'), (r'^fin$', '끝 왕(500라운드형)'), (r'^nat$', '계보 자연 진주 r300–499'), (r'^sac$', '계보 희생 진주 r300–499'), (r'^oth$', '계보 다른 사망 진주'),
        (r'^en$', '계보 적 사망 진주'), (r'^spr$', '계보 질주'), (r'^split$', '계보 분열'), (r'^sac_b(\d)$', '계보 희생 진주, 구간 {0}'), (r'^nat_b(\d)$', '계보 자연 진주, 구간 {0}'),
        (r'^top300$', 'r300 팀 최장'), (r'^g$', '성장/라운드 r300–500'), (r'^g(\d+)$', '성장/라운드 r{0}–'), (r'^g_c(\d+)$', 'L300 부류 {0} 성장'), (r'^gc_(min|max)$', 'L300 부류별 성장({0})'),
        (r'^longest(\d+)$', '계보 = 팀 최장 r{0}(계보 원천)'), (r'^plongest(\d+)$', '계보 = 팀 최장 r{0}'), (r'^fin_(\w+)$', '끝 왕({0})'), (r'^nat_(\w+)$', '계보 자연 진주({0})'),
        (r'^map_sac_(min|max)$', '지도별 계보 희생 진주({0})'), (r'^e5_(\w+)$', '전멸형·500라운드까지 간 판 {0}'), (r'^ex_(\w+)$', '전멸형·전멸로 끝난 판 {0}'),
        (r'^nk_(\w+)$', '왕 아닌 드래곤 턴 {0}'), (r'^approach$', '왕 쪽으로 가까워지는 턴'), (r'^coh_(\w+)$', 'r340 무리 {0}'), (r'^sac_d(\d)_(\w+)$', '희생, 계보까지 거리 부류 {0}: {1}'),
        (r'^sac_came$', '3칸 안 희생의 20라운드 전 8칸 밖'), (r'^sac_pg$', '희생 판당 수'), (r'^sac_far_pg$', '9칸 밖 희생 판당 수'), (r'^sac_toline$', '희생 진주 → 계보'),
        (r'^far_(\w+)_(min|max)$', '9칸 밖 희생 {0}({1})'), (r'^ls_near_(min|max)$', '계보 희생 진주 중 먹이 3칸 안({0})'), (r'^ls_big_b(\d)$', '계보 희생 진주 중 먹이 길이 ≥8, 구간 {0}'),
        (r'^first$', '처음 최장이 된 라운드'), (r'^fromcoh$', '최종 왕이 r340 무리에서 나옴'), (r'^fromcoh_(\w+)$', '무리에서 나온 최종 왕의 r340 {0}'), (r'^fin_coh$', '끝 왕(무리에서 나온 판)'),
        (r'^fin_kng$', '끝 왕(r340 왕이 끝까지 간 판)'), (r'^exp6_a$', '노출 r300–399(적 머리 ≤6)'), (r'^exp6_b$', '노출 r400–499'), (r'^exp3_(a|b)$', '적 머리 ≤3 ({0})'), (r'^expmap_(\w+)$', '노출({0})'),
        (r'^p5_(a|b)$', '5칸 안 자연 진주/턴({0})'), (r'^own_(a|b)$', '자기 영토 턴({0})'), (r'^hx_(\w+)$', '노출 60% 넘는 판 {0}'), (r'^lx_(\w+)_(min|max)$', '노출 60% 아래 부류 {0}({1})'),
        (r'^allx_g_(min|max)$', '노출 부류별 성장({0})'), (r'^kd_(\w+)_b(\d)$', '길이 ≥8 죽음 {0}, 구간 {1}'), (r'^kloss_en$', '왕을 적 머리에 잃은 판'), (r'^kloss_ally$', '왕을 아군 머리에 잃은 판'),
        (r'^kloss_len$', '적 머리에 잃은 왕의 길이'), (r'^cohenemy_(\w+)$', '무리의 적 머리 죽음({0})')]
def label(k):
    if k in FIXED: return FIXED[k]
    m = re.match(r'^(W|L|X)_(.*)$', k)
    if not m: return k
    g, rest = GRP[m.group(1)], m.group(2)
    for pat, lab in STEM:
        mm = re.match(pat, rest)
        if mm: return g + ' ' + lab.format(*[MAPS.get(x, x) for x in mm.groups()])
    return g + ' ' + rest
lines = []
for r in CH:
    lines.append(f"{label(r['k'])} {fv(r, r['old'])} → {fv(r, r['neu'])}")
basis = [('W_exp6_a', '승자 노출(r300–399, 적 머리 ≤6)'), ('L_exp6_a', '패자 노출(r300–399)'), ('W_exp6_b', '승자 노출(r400–499)'), ('L_exp6_b', '패자 노출(r400–499)'),
         ('W_kloss_en', '승자 왕 손실(r340 뒤, 적 머리)'), ('L_kloss_en', '패자 왕 손실')]
context = [('W_expmap_Schooltime', '승자 노출(Schooltime)'), ('W_expmap_SlitheryFight', '승자 노출(Slithery Fight)')]
bl = []; moved = []; cl = []; cmoved = []
for k, lab in basis:
    bl.append(f"{lab} {O[k]:.1f}% → {NN[k]:.1f}%")
    if abs(NN[k] - O[k]) > 1: moved.append(lab)
for k, lab in context:
    cl.append(f"{lab} {O[k]:.1f}% → {NN[k]:.1f}%")
    if abs(NN[k] - O[k]) > 1: cmoved.append(lab)
E['KX_BASIS'] = '; '.join(bl)
E['KX_MOVED'] = moved
E['KX_CONTEXT_MOVED'] = cmoved
E['KX_BASIS_NOTE'] = ("**전체 모집단으로 다시 센 뒤의 기준값 확인:** 세 제안의 기준값 가운데 상위권 값에 기댄 것은 `kx`의 노출(≤35%, ≤22%)과 왕 손실(≤7%)뿐이다. "
  "`gh`의 가로채기(≤20%), `lwk`의 끝판 창 적중(≥55%)과 그 밖의 우리 쪽 기준은 모두 우리 세트에서 나와 바뀌지 않았다. "
  + "kx 기준의 근거: " + E['KX_BASIS'] + ". "
  + ("모두 1점 안에서 움직여 기준값을 바꾸지 않는다. " if not moved else "1점 넘게 움직인 것: " + ', '.join(moved) + ". ")
  + "지도 순위의 근거(기준값 아님): " + '; '.join(cl)
  + ("." if not cmoved else f". {', '.join(cmoved)}이 1점을 조금 넘게 움직였으나 싸움 지도가 1순위라는 순위는 그대로다(우리 59%, 43%)."))
E['CHANGES'] = ("## 전체 모집단으로 다시 셈 (2026-10-01)\n"
  f"- 처음 문서(커밋 175f2e7)는 상위권 추출이 21:10 스냅숏의 500라운드형 4,355판에서 멈춘 상태였다. 코디네이터의 요청으로 22:46 KST 스냅숏(전체 {fmt(snap_all)}판; 500라운드형 {fmt(snap_r500)}판)의 500라운드형을 모두 추출했다. "
  "3–5절의 상위권 값과 1–2절의 500라운드형 계보(처음에는 11:34 KST 질량 장부 캐시)를 모두 이 전체 추출로 다시 셌다. "
  + (f"전멸형 계보(T1e·T1f)는 질량 장부 캐시를 {ml_snap}의 `data/top` 전부({int(NN['n_ml']):,}판 읽음·{int(NN['n_ml_kept']):,}판 남김)로 넓혀 다시 셌다(처음에는 11:34 KST, 8,404판 남김). " if N['elimLineage'] == 'ml' and ml_snap != '2026-09-30 11:34 KST' else '')
  + "본문의 상위권 수치는 이제 `exp/endgame-king/numbers_wl.js`가 계산한 값을 `narrative.py`가 채운다.\n"
  f"- **1점 넘게 움직인 값**(점 = 몫은 1%p, 길이·진주는 1, 라운드당 성장은 0.01, 판당 죽음·턴당 진주는 0.1; 본문이 인용하는 값만, 표본 크기는 뺌; 원문 `exp/endgame-king/changes.md`): "
  + ('; '.join(lines) if lines else '없다') + ".\n"
  f"- **제안 기준값의 근거:** " + E['KX_BASIS_NOTE'].replace('**전체 모집단으로 다시 센 뒤의 기준값 확인:** ', '') + "\n"
  "- 결론(요약 1–8)과 제안(7절)은 바뀌지 않는다.")
(D / 'narrative-extra.json').write_text(json.dumps(E, ensure_ascii=False, indent=1), encoding='utf8')
print('wrote narrative-extra.json; changes', len(lines), 'kx basis moved', moved)
