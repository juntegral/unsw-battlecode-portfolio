import json
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
G={g['gid']:g for g in (json.loads(p.read_text()) for p in OUT.glob('game-*.json'))}
ids=[1460076,1460077,1460078,1471965,1471966,1471967]
lines=['[M] 팀 133 상대 여섯 패배는 여왕 판정 4판·전멸 2판. [E] 특별한 조기 공격 증거는 없다.', '[E] 카드 없음: 두 패배 이상을 설명하고 one5 코드의 구체적 규칙까지 확인한 수정안이 없다.', '[M/E] 사건·집계는 확실함(85판 회계 검증); 의도·회피 가능성·승부의 불가역 시점은 미검증.', '', '[M] 작성 2026-10-09 01:33:09 KST. 이전 b1460075는 색인에 누락됐고 제출은 **20366(v62)**다. 최신은 **20980(one5)**; 레이팅은 아래 표.', '', '[M] 라운드는 0부터, 끝은 r499. “지속 열세”는 판정 튜플(여왕→최장→총길이)을 이후 따라잡지 못한 첫 라운드. [E] 불가역 패배 시점은 아니다.', '', '| [M] 판 ID·지도 | 승부 기준·종료 | 지속 열세 | 우리 여왕 사망 | 최대 단일 턴 질량 감소 | 최종 여왕/최장/총길이 우리 : 상대 |', '|---|---|---:|---|---|---|']
for gid in ids:
 g=G[gid];d=g['detail'];q=next(x for x in d['deaths'] if x['side']==0 and x['queen']); t=d['largest_turn_loss']; a,b=g['ends']
 cause={0:'벽',1:'자기 몸',3:'피격'}[q['reason']]
 lines.append(f"| {gid} {g['map']} | {'전멸' if g['how']=='elim' else '여왕'} r{g['last']} | r{d['decisive_retrospective']} | #{q['id']} r{q['r']} L{q['L']} {cause} | r{t['r']} −{t['mass_loss'][0]} | {a[3]}/{a[2]}/{a[1]} : {b[3]}/{b[2]}/{b[1]} |")
lines+=['', '[M] **1460076 Portals:** r9 L5 여왕이 정지 분열로 L3을 남기고 r10 동쪽 자기 몸에 충돌했다. 상대 여왕은 끝에 L8. r478 L10의 무행동 사망은 떨어진 진주 5개를 전부 우리 쪽이 회수했다.', '', '[M] **1460077 Around UNSW:** r56 여왕이 동쪽으로 이동한 뒤 적 #61에게 피격됐다. r263 L27도 적 L3의 두 걸음에 소실됐다. 끝 총길이 214>205·최장 53>36이어도 상대 여왕 L11 때문에 졌다.', '', '[M] **1460078 Slithery Fight:** r200 총길이 219>152였다. r400 여왕은 L59에서 L2를 남기는 정지 분열 후 같은 라운드 피격됐다. r419 최장 L65가 적 L4의 세 걸음에 죽었고, 드롭 33개 중 적이 28개를 먹었다.', '', '[M] **1471965 Maze:** r258 여왕이 (13,9)→(14,9) 이동 후 적 L2의 한 걸음에 피격됐다. r328 L7도 피격됐다. 끝 총길이 95>66·최장 26>24이지만 상대 여왕 L24가 결정했다.', '', '[M] **1471966 Stripes:** r100 머릿수 5:12. 적 여왕은 우리가 r103 죽였지만, 우리 여왕이 r218 포털로 진주를 먹고 (6,2)에 들어가 r219 벽에 죽었다. 아군도 같은 칸에서 r136·142 벽 사망. r263 마지막 드래곤이 없어졌다.', '', '[M] **1471967 Default:** r50 머릿수 8:11, r100 10:20. r71 여왕이 북쪽 이동 후 적 L3의 두 걸음에 피격됐다. r426 남은 최장 L12도 적 L3에게 피격되고, r455 전멸했다.', '', '| [M] 우리 행동·손실, 판 ID | 벽 / 자기 몸 사망 | 새끼 정적 출구 0 분열 | 무행동 사망 | 우리 드롭 중 적 섭취 / 전체 드롭 |', '|---|---:|---:|---:|---:|']
for gid in ids:
 g=G[gid];ds=[x for x in g['deaths'] if x[1]==0];c=Counter(x[4] for x in ds)
 lines.append(f"| {gid} | {c['wall']} / {c['own body']} | {g['detail']['metrics'][0]['split_noexit']} | {c['stop']} | {sum(x[11] for x in ds)} / {sum(x[15] for x in ds)} |")
lines+=['', '[M] 여섯 판 79,012 우리 턴에서 시간초과 0·분열 이외 제자리 생존 0. [E] 위 벽·무행동·출구 집계에는 강제 사망과 수확·먹이기가 섞여 있으므로 모두 판단 오류로 해석하지 않는다.', '', '| [M] 25라운드별 머릿수,총길이 — 각 칸 우리 / 상대 | 1460076 | 1460077 | 1460078 | 1471965 | 1471966 | 1471967 |', '|---|---|---|---|---|---|---|']
for r in range(0,500,25):
 cells=[]
 for gid in ids:
  g=G[gid];sn=g['snaps'].get(str(r));cells.append('—' if sn is None else f'{sn[0][0]},{sn[0][1]} / {sn[1][0]},{sn[1][1]}')
 lines.append('| '+str(r)+' | '+' | '.join(cells)+' |')
lines.append('| 끝(각 종료 라운드) | '+' | '.join(f"{G[gid]['ends'][0][0]},{G[gid]['ends'][0][1]} / {G[gid]['ends'][1][0]},{G[gid]['ends'][1][1]}" for gid in ids)+' |')
lines+=['', '[M] 동일 지도 Maze·Stripes·Default의 one5 상대 행동 비교(각 3판). 조기는 r0–50, 충돌은 적 머리를 직접 친 횟수, 통로 충돌은 피해 칸의 지형 차수≤2. [E] 차수만으로 길막 의도를 판정하지 않는다.', '', '| [M] 상대 | 충돌 / 상대 턴 | 1,000턴당 | 조기 충돌 / 조기 턴 | 우리 여왕을 직접 침 | 통로 충돌 | 벽 사망 |', '|---|---:|---:|---:|---:|---:|---:|']
for name,gs in [('133',[G[x] for x in [1471965,1471966,1471967]]),('WHQ',[g for g in G.values() if g['src']=='one5-w1' and g['map'] in ['Maze','Stripes','Default']]),('Cache',[g for g in G.values() if g['src']=='one5-c1' and g['map'] in ['Maze','Stripes','Default']])]:
 c=Counter()
 for g in gs:c.update(g['detail']['metrics'][1])
 lines.append(f"| {name} | {c['rams']} / {c['turns']} | {1000*c['rams']/c['turns']:.2f} | {c['early_rams']} / {c['early_turns']} | {c['queen_hits']} | {c['corridor_rams']} | {c['wall']} |")
lines+=['', '[E] 133만의 여왕 사냥·조기 램 증거는 없다. 인과 비교는 미확인.', '', '[M] 색인 랭크전 50판 중 상대 레이팅이 낮은 판은 20판·7패. 누락된 b1460075까지 더하면 55판 중 25판·10패. b1473235(상대 357)도 포함했다. 색인의 시각은 수집 시각이며 b1459601은 실제 r0 시작이 22:25라 22:29 이전이다; 이 상대는 우리보다 높아 저레이팅 집계는 동일하다.', '', '| [M] 저레이팅 상대에게 진 모든 판 | 상대 | 지도 | 실제 제출 | 사인·판정 |', '|---|---|---|---|---|']
for gid in sorted(G):
 g=G[gid];m=g['meta'];s='A' if m['teamAId']==1119 else 'B';o='B' if s=='A' else 'A'
 if not m.get('ranked') or m['team'+o+'Elo']>=m['team'+s+'Elo'] or g['result']!='loss':continue
 q=next(x for x in g['detail']['deaths'] if x['side']==0 and x['queen']);cause={0:'벽',1:'자기 몸',3:'선제 충돌' if q['actor']==q['id'] else '피격'}[q['reason']]
 decision={'queen':'상대 여왕 생존','longest':'양 여왕 사망·최장 열세','elim':'우리 전멸'}[g['how']]
 missing=' †' if gid in [1460076,1460077,1460078] else ''
 lines.append(f"| {gid}{missing} | {m['team'+o+'Id']} ({m['team'+o+'Elo']}<{m['team'+s+'Elo']}) | {g['map']} | {g['bot']} | 여왕 r{q['r']} {cause}; {decision} r{g['last']} |")
lines+=['', '[M] † 색인 누락. 지도별 저레이팅 패/판: Slithery 2/2, Stripes 2/3, Portals 1/2, Around UNSW·Trauma·Maze·Australia 각각 1/1, Default 1/3.', '', '[M] Australia는 전체 랭크전 4/4패(팀 280·952·91·1059); Around UNSW는 2/2패(133·91). Stripes는 4/5패이나 팀 1059에게 이겼다. 시작 길이만 묶으면 L2 두 마리 4/6패, L4 두 마리 5/9패라 공통 필패 배치는 아니다. [E] Australia의 공통 원인은 여기서 확정하지 못했다.', '', '[C] 기존 여왕 안전: one5 4197–4199.', '', '[M] 재현은 `analyze.py`·`summarize.py`·`verify.py`(이 폴더). 기존 판독기·집계기를 import했다. 85판 양편 회계·독립 스냅샷, 6판 기보 최종 결과 일치(`verification.json`).', '', '[E] 미점검: 램의 시야·안전 대안, 적 의도, 코드 반사실, 새 판. 출구는 현재 점유·자기 꼬리만 고려했다. 구현·컴파일 없음.']
(OUT/'report.md').write_text('\n'.join(lines)+'\n')
non_tables=[l for l in lines if not l.startswith('|')]
print('non-table whitespace words',len(' '.join(non_tables).split()))
