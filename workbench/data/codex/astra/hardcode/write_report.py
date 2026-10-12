#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

P = Path(__file__).resolve().parent
S = json.loads((P/'summary.json').read_text())
D = json.loads((P/'details.json').read_text())
R = [json.loads(x) for x in (P/'results.jsonl').read_text().splitlines()]
M = json.loads((P/'misses.json').read_text())
T = json.loads((P/'clearest-ten.json').read_text())
pairs = list(csv.DictReader((P/'pair-divergences.tsv').open(),delimiter='\t'))
names={545:'dev',87:'WHQ',1119:'우리'}
byid={r['gid']:r for r in R}
for p in pairs:
    for k in ('team','queen_id'):
        p[k]=int(p[k])
    for k in ('games','first'):
        p[k]=json.loads(p[k])
    p['opponent_set']=json.loads(p['labels'])[0].split('-')[1]
letters={'pearl':'P','enemy':'E','ally':'A','self':'S','nothing':'Ø','unmatched':'U'}

def cell(ps):
    if not ps:
        return '—'
    return ', '.join(sorted({f'{p["first"]["r"]}{"".join(letters[v] for v in p["first"]["view"])}' for p in ps}))

def xy(x,c):
    return f'({c%x["w"]},{c//x["w"]})'

lines=[
'판정: **cannot tell — 사전 지도 지식 여부는 판별 불가.** [E]  ',
'가장 강한 수치: 미관측 먹이 접근은 빈길 기대의 dev **1.44배**, 우리 **1.35배**; dev 표본은 **96이동**뿐이다. [M]  ',
'확신: 이 자료의 식별 한계에는 높음; scripted/general 중 어느 쪽인지는 낮음. [E]',
'',
'[M] 지정 135판(dev 60·WHQ 75), 추가 84판을 재구성했다. 모든 표는 [M], 해석은 [E]. 좌표·라운드는 0부터다. 작성 2026-10-09 01:23 KST. 카드 없음.',
'',
'**1. 시야 밖 지식.** [E] 일반 봇도 직진·지형 탐색으로 1배를 넘을 수 있다. 지형·대조군으로 설명되지 않는 정확한 미관측 접근이면 사전 지식 의심이 커진다. [M] r0–60, 진주와 샘을 아직 본 적 없는 진영의 첫 이동만 측정했다. 샘은 기보 전체의 자연 생성 좌표 합집합으로 추정했다. 작은 지도≤1,200칸. 기대값은 매 턴 가능한 빈길 중 접근 방향의 비율이다.',
'',
'| 크기·팀 | 경기 | 접근/유효 이동 | 빈길 기대 횟수 | 배율 | 첫 식사 r / 시작→그 칸 거리 중앙값 | 중앙값(r+1−거리) |',
'|---|---:|---:|---:|---:|---:|---:|',
]
for size in ('small','big'):
    for team in (545,87,1119):
        x=next(x for x in S['groups'] if x['team']==team and x['size']==size)
        n=x.get('blind_moves',0);expect=x.get('blind_expected',0)
        ratio=f'{x["ratio"]:.2f}' if n else '판별불가'
        lines.append(f'| {"작음" if size=="small" else "큼"}·{names[team]} | {x["games"]} | {x.get("blind_toward",0)}/{n} | {expect:.2f} | {ratio} | {x["first_r_median"]:g} / {x["start_d_median"]:g} | {x["arrival_extra_median"]:g} |')
lines += [
'',
'[M] dev 유효 이동은 weakhold 92번(r0–6), Portals 4번(r0)뿐이다. weakhold 1461128 r1 #1은 숨은 샘 거리 12→13, #4는 8→7; 첫 식사는 r10, 시작 거리14였다. [E] 분열·다중 이동 때문에 식사 라운드와 걸음 거리는 같은 단위가 아니다.',
'',
'**2. 반복 경로.** [E] 일반 봇은 관련 관측에 반응하되 무관한 변화는 무시할 수 있다. 고정 개막도 이후 반응할 수 있어 경로 차이만으로 일반성을 입증하지 못한다. [M] 같은 지형·시작 배치끼리 비교했다. 표는 최초 갈림 `r+관측차이`; q는 시작 여왕 id. P=진주, E=적, A=아군, S=자기 몸, Ø=비교한 항목 동일(전체 입력 동일이라는 뜻 아님). D/W=상대 dev/WHQ.',
'',
'| 지도·q | dev | WHQ | 우리(D) | 우리(W) |',
'|---|---|---|---|---|',
]
for mp in sorted({r['map'] for r in R if not r['extra']}):
    for q in (0,1):
        cols=[]
        for team,opp in ((545,'d1'),(87,'w1'),(1119,'d1'),(1119,'w1')):
            cols.append(cell([p for p in pairs if p['map']==mp and p['queen_id']==q and p['team']==team and p['opponent_set']==opp]))
        lines.append(f'| {mp}·{q} | '+ ' | '.join(cols)+' |')
for label,fn in [('비교 쌍 수',lambda ps:str(len(ps))),('최초 갈림 중앙 r',lambda ps:f'{median(p["first"]["r"] for p in ps):g}'),
                 ('관측 변화에도 같은 경로인 선행 비교 턴',lambda ps:str(sum(int(p['changed_view_same_path']) for p in ps)))]:
    cols=[]
    for team,opp in ((545,'d1'),(87,'w1'),(1119,'d1'),(1119,'w1')):
        cols.append(fn([p for p in pairs if p['team']==team and p['opponent_set']==opp]))
    lines.append(f'| {label} | '+' | '.join(cols)+' |')
lines += [
'',
'[M] 예: dev 1461128↔1471456 r38 #1, 1461129↔1471457 r5 #16은 진주 배치가 다를 때 갈라졌다. 모든 비교 쌍이 r100 전에 갈라졌다. Schooltime은 지형 변형도 있어 일부 쌍을 제외했다.',
'',
'**3. 지나친 진주.** [E] 일반 봇도 안전·분열·다른 먹이 때문에 지나칠 수 있다. 같은 생성 좌표의 반복만으로 스크립트가 되지는 않는다. [M] 요약은 인접 진주를 하나 이상 남긴 턴/기회; 보이는 경우를 병기했다(괄호: 하나도 안 먹음). 반복 비교는 공통 one1·3·4·5만 사용했다. 아래 열 장면은 시야에 진주 하나, 적 머리 없음, 분열·사망·다른 섭취 없음이다.',
'',
'| 팀/지도 | 횟수 또는 경기 | r / 드래곤 | 진주 좌표·반복 | 머리→실제 이동 |',
'|---|---|---|---|---|',
]
for x in D['test3']:
    team=x['team'];c=x['counts'];ds=[]
    predicates=[('D',lambda e:e['label'].endswith('d1')),('W',lambda e:e['label'].endswith('w1') and e['label']!='one2-w1')] if team==1119 else [('',lambda e:e['label']!='one2-w1')]
    for label,pred in predicates:
        tiles=defaultdict(set)
        for e in M[str(team)]:
            if not pred(e):continue
            for tile in set(e['pearls'])&set(e['visible_adjacent']):
                tiles[e['map'],e['side'],tile].add(e['gid'])
        ds.append(f'{label} {sum(len(v)==4 for v in tiles.values())}/{len(tiles)}')
    lines.append(f'| {names[team]} 전체 | {c["miss_turns"]:,}/{c["adjacent_turns"]:,}; 보임 {c["visible_miss_turns"]:,}/{c["visible_adjacent_turns"]:,} ({c["visible_none_taken"]:,}) | 보임 {100*c["visible_miss_turns"]/c["visible_adjacent_turns"]:.1f}% | 4판 모두 반복한 좌표/전체: {"; ".join(ds)} | — |')
for x in T:
    lines.append(f'| dev·{x["map"]} | {x["gid"]} | {x["r"]} / #{x["dragon"]} | {x["tile_xy"]} · {x["recurrence"]["n_games"]}/4판 | {xy(x,x["head"])}→'+ '→'.join(xy(x,c) for c in x['path'])+' |')
lines += [
'',
'**4. 지도 의존.** [E] 일반 봇의 우위도 지형·상대에 따라 달라질 수 있다. [M] 추가 표본은 10/4의 두 상대(264·507), 17지도이며 Autarky·Prisoners Dilemma는 지정 15지도 밖이다. 수치는 r0–100 누적 섭취 차이 평균(조기 종료는 종료까지), 낙하 진주 포함이다.',
'',
'| 지도 | dev−우리(n=4) | WHQ−우리(n=5) | 우리−상대(n=9) | dev−다른 상대(평균; n) |',
'|---|---:|---:|---:|---:|',
]
for x in S['map_leads']:
    v=[]
    for t in ('545','87','1119'):
        v.append(f'{x[t]["mean_lead"]:+.1f}' if x[t]['n'] else '—')
    z=x['545_other']
    lines.append(f'| {x["map"]} | '+' | '.join(v)+f' | {z["mean_lead"]:+.1f}; {z["n"]} |')
lines += [
'',
'[M] 예: Autarky 1047007 r0–100 +67, Prisoners Dilemma 1046936 r0–93 +96. [E] 둘 다 기존 래더 지도라 미지 지도 검증은 아니다.',
'',
'**미확인:** [M] 219판 모두 샘 타이머 이벤트·실제 생성 매개변수가 없다. [E] 끝까지 생성하지 않은 샘, 정확한 입력(타이머·방향·음파), 난수, 상대 버전 변경, 상대 코드, 미지 지도 반사실 실험은 확인하지 못했다. 따라서 “7×7 관측으로 불가능한 행동”은 입증되지 않았고, 사전 지식이 없다는 것도 입증되지 않았다.',
'',
'[방법·검증](methods.md) · [모든 첫 식사](first-meals.tsv) · [경기쌍](pair-divergences.tsv) · [드래곤별 경로](dragon-divergences.tsv) · [모든 반복 좌표·장면](missed-tiles.tsv)',
]
(P/'report.md').write_text('\n'.join(lines)+'\n')
prose='\n'.join(x for x in lines if not x.startswith('|'))
print('prose whitespace words:',len(prose.split()))
