import json
from pathlib import Path
from collections import Counter
from statistics import mean,median
from datetime import datetime
O=Path('data/codex/astra/worstmaps');rs=json.loads((O/'rows.json').read_text());ts={r['gid']:r for r in json.loads((O/'trace.json').read_text())};supply=json.loads((O/'supply.json').read_text());names=['Australia','Tower Defense','Stripes','Around UNSW','Schooltime','Default','Devil']
checks=[]
for r in rs:
 m=json.loads(Path(r['path']).with_name(f'game-{r["gid"]}.json').read_text())
 result='draw' if m['winner'] not in ('a','b') else 'win' if m['winner'].upper()==r['own_side'] else 'loss'
 assert result==r['result'],r['gid']
 for t in (50,100,150,300):
  p=r['spatial'][str(t)];orig=r['snaps'].get(str(t),r['ends'] if t>r['last'] else None)
  assert orig is not None
  for side in (0,1):
   assert p[side]['N']==sum(p[side][k] for k in ('home','far','neutral'))
   assert (p[side]['N'],p[side]['L'],p[side]['Q'])==(orig[side][0],orig[side][1],orig[side][3]),(r['gid'],t)
  assert p[0]['bearing_near']+p[1]['bearing_near']+p[0]['bearing_tie']==r['features']['bearing']
 for side in (0,1):assert ts[r['gid']]['counts'][side].get('natural_eat',0)==sum(e[0]<=100 and e[1]==side and e[3]=='n' for e in r['eats'])
 assert ts[r['gid']]['counts'][0].get('natural_off_config',0)==0
checks=['61 metadata verdicts agree','244 checkpoints match imported ledger','488 head-count spatial sums agree','244 bearing partitions agree','122 natural meal totals agree','0 natural births outside empirical supply union']
(O/'validation.json').write_text(json.dumps(dict(at=datetime.now().isoformat(),checks=checks),indent=2))
lines=['[M] 두 마리 출발의 분열 지연·생산지 상실과, 큰 지도의 종국 최장 판정 패배가 분리된다.', '[E] 카드: 포털 옆 꼬리의 조건부 분열 한 개. 즉시 적용이 아닌 기제 시험 후보다.', '[E] 확신: 현상 높음, 코드 원인 중간, 변경 효과 미검증.', '', '[M] 고유 61판(one5/6/7=27/20/14), 아래 수치는 우리/상대. WHQ·Cache 주표본은 지도별 6판; dev test 1은 지도별 1판의 보조표본이다. 전체 밤 전적을 재사용하지 않았다. Default는 최근 2/8로 “버틴다”는 전제가 성립하지 않는다.', '', '| [M] 지도·표본 | 크기; 열린4방향/출구≤2 비율 | 포털쌍 | 시작 길이(각편); 최소 경로거리 | 관측 생산칸/전체; 빠른 칸 | 재생성 간격 최소/중앙/최대 |', '|---|---|---:|---|---|---|']
for name in names:
 rr=[r for r in rs if r['map']==name]
 for sig in dict.fromkeys(r['features']['supply_sig'] for r in rr):
  sub=[r for r in rr if r['features']['supply_sig']==sig];f=sub[0]['features'];n=f['w']*f['h'];deg=f['degree'];lc=Counter(z['L'] for z in f['starts'][0]);start=','.join(f'{k}×{v}' for k,v in sorted(lc.items()));gap=f['gap_summary'][1:];s='/'.join(f'{x:g}' for x in gap)
  lines.append(f"| {name} ({len(sub)}) | {f['w']}×{f['h']}; {100*deg.get('4',0)/n:.1f}%/{100*sum(v for k,v in deg.items() if int(k)<=2)/n:.1f}% | {f['portals']} | {start}; {f['start_distance']} | {f['bearing']}/{n}; {f['fast']} | {s} |")
lines+=['', '[M] 생산칸은 해당 구조의 기보에서 자연 생성된 위치의 합집합(하한). 빠른 칸은 섭취→다음 자연 생성 간격 표본≥5, 중앙값≤12. 간격은 몸·잔류진주의 방해를 포함하며 엔진 타이머 자체가 아니다. 타이머는 기보에서 숨겨져 확정 불가. Schooltime 두 구조를 분리했다.', '', '| [M] 지도(N) | r50 머리·총길이 | r100 | r150 | r300 | 열세 시작 중앙값(해당 판수) | 패배 원인 |', '|---|---|---|---|---|---|---|']
for name in names:
 rr=[r for r in rs if r['map']==name];vals=[]
 for t in (50,100,150,300):
  vals.append(' / '.join(f"{mean(r['spatial'][str(t)][s]['N'] for r in rr):.1f}·{mean(r['spatial'][str(t)][s]['L'] for r in rr):.1f}" for s in (0,1)))
 turns=[r['turn'] for r in rr if r['turn'] is not None];ca=Counter(r['how'] for r in rr if r['result']=='loss');causes=' '.join(f'{dict(elim="전멸",longest="최장",queen="여왕",total="총길이")[k]}{v}' for k,v in ca.items())
 lines.append(f"| {name}({len(rr)}) | "+' | '.join(vals)+f" | {median(turns):g}({len(turns)}) | {causes} |")
lines+=['', '[M] 열세 시작=상대≥4이고 우리 머릿수<상대/2가 25라운드 지속한 최초 r(전멸 종료는 잔여 구간). 없는 판은 제외; 승부의 인과 전환점은 아니다. 조기 종료 판은 종국 상태를 이월했다.', '', '| [M] 지도·라운드 | 각편 자기 영역 머리 | 각편 상대 영역 머리 | 생산칸 최근접 점유율% |', '|---|---|---|---|']
for name in names:
 rr=[r for r in rs if r['map']==name]
 for t in (50,100,150,300):
  cols=['/'.join(f"{mean(r['spatial'][str(t)][s][k] for r in rr):.1f}" for s in (0,1)) for k in ('home','far')]
  cols.append('/'.join(f"{100*mean(r['spatial'][str(t)][s]['bearing_near']/r['features']['bearing'] for r in rr):.1f}" for s in (0,1)))
  lines.append(f'| {name} r{t} | '+' | '.join(cols)+' |')
lines+=['', '[M] 영역은 시작 머리들의 최단경로 Voronoi; 거리 동률은 중립. 생산칸은 현재 머리의 벽·포털 경로거리로 배정하며 몸은 제외한다. 점유율 잔여는 동률/양편 미도달이다.', '', '| [M] 전체 사망 합계 | 피격램 | 선제램 | 아군머리 | 벽 | 자기몸 | 아군몸 | 적몸 | 행동종료류 |', '|---|---|---|---|---|---|---|---|---|']
for name in names:
 rr=[r for r in rs if r['map']==name];counts=[Counter(d[4] for r in rr for d in r['deaths'] if d[1]==s) for s in (0,1)]
 lines.append('| '+name+' | '+' | '.join(f'{counts[0][k]}/{counts[1][k]}' for k in ['rammed','rams','mate head','wall','own body','mate body','foe body','stop'])+' |')
lines+=['', '[M] 사망은 의도적 먹이기·탈출 희생도 포함한다. 행동종료류는 기존 계수기의 stop 묶음이며, 벽/몸 사망을 “핀”으로 단정하지 않았다.', '', '| 특징별 발견 | 기제와 일반 규칙 | 장면(경기 ID:r) |', '|---|---|---|']
lines += [
'| [M] L2 두 마리 출발: Stripes 첫 분열 중앙 r15/11(우리 1판 없음), Tower r65/41(우리 1판 없음). r100 자연진주 221/517, 110/410. | [C] 1474–1477의 `QS_KEEP_LEN:3`은 L4 여왕을 보존; 1508–1519는 꼬리 공간·포털로 비여왕도 제한. [E] 먹어서 L4가 된 여왕만 안전한 생산지에서 한 번 분열하는 가설. | [M] 1472007:r11 상대 L4→2+2, 우리 r19 L6→4+2; 1479924:r28 상대 여왕 분열, 우리 첫 분열 r83; 1472757:r50 4/4→r100 3/25. |',
'| [M] 넓은 땅+드문 반복 생산지: Australia r50 빠른 칸 점유 30.6/68.4%, r100 자연진주 728/1117. Around r100 57/59마리인데 자연진주 1307/2058. | [C] 6072–6100은 최단 먹이/미관측 목표 중심; `INC_PERIOD:0`(318), 5590–5684의 구역 수입 배치가 꺼져 있다. [E] 관측한 생산량÷아군 수로 여유 소형 개체를 재배치. `INC_PERIOD:10`만 켜기는 보류: 5625–5632가 같은 아군의 여러 관측도 군집 수에 더한다. | [M] 1472753:r5 양편 첫 빠른 진주, r100 19/63마리; 1479925:r50 22/58→r100 48/60, 길이는 120/263. |',
'| [M] 포털 인접 번식: Stripes 비여왕 L≥4 미분열 턴 중 포털 꼬리 53, Default 47, Schooltime 20(r≤100). | [C] 1515–1519는 탈출 가능한 일반 변이 있어도 포털 인접만으로 거부. [E] 아래 카드. | [M] 1472756:r35–36 #6, 1480434:r26 #12, 1471465:r32–33 #11은 L4·포털 꼬리·빈 출구가 있는데 미분열. 앞선 관문 통과는 미확인. |',
'| [M] 큰 지도 종국 집중: Australia/Around/Schooltime의 패배 중 최장 판정 4/5/6판. Schooltime 2패는 종국 총길이도 우리 우세. | [C] 5946·5962–5964의 신선도/먹이기 관문과 4155–4156의 최장 지정. [E] 수신 위치까지의 경로시간을 반영한 합류와 성장 개체 생존을 함께 검증; 단순 신선도 상향 근거 없음. | [M] 1472761:r300 총길이245/173→r499 285/248, 최장35/63; 1477047:r499 총길이156/97, 최장24/28. |']
lines+=['', '| 시험 카드(1개) | 내용 |', '|---|---|', '| [E] 일반 출구가 있는 포털 꼬리에서 번식 | r≤100, 비여왕 L4, 기존 분열 관문을 통과하고 자식이 포털을 걸치지 않으며, **관측된 일반 변의 빈 출구·공간≥4·적 도달 없음**이면 포털 인접 일괄 금지를 예외 처리. |', '| [C] 위치·기존 상수 | `one7-bot/main.cpp:1508–1519`; `CHILD_MIN_ROOM:4` 유지. 예외 스위치는 새로 필요하며 기존 상수만으로 구현 불가. |', '| [M/E] 근거·통과 기준 | 위 세 지도의 120턴은 후보 상한, 확정 발동 수가 아니다. 관문별 로그로 적격 수를 센 뒤 적격 미분열 감소, 새끼 25라운드 생존, r100 생산칸 접근 증가를 확인. 변경 적용 기보는 0판. |', '| [E] 비용·반증 | 포털 출구 오판·자기 혼잡·소형 먹이 경쟁, 추가 국소 탐색 CPU. 새끼 조기사망/기존 개체 봉쇄가 늘거나 생산지 접근이 늘지 않으면 버린다. |', '', '[M] 원장·경기별 라운드: [rows.json](rows.json), [trace.json](trace.json), [inventory.json](inventory.json). [C] 줄 번호는 모두 one7. [E] 두 번째 카드는 보류: 소형 여왕 재분열과 수입 배치는 아직 앞선 실패/관문을 분리하지 못했다.', '', '[M] 미확인: 변경 빌드·CPU·새 경기·실제 내부 기억/점수·타이머 원값. 오프라인 분석만 수행. 판 수 차이와 상대 차이가 있어 버전 개선의 인과를 주장하지 않는다.']
(O/'report.md').write_text('\n'.join(lines)+'\n')
print('report non-table words',len(' '.join(l for l in lines if not l.startswith('|')).split()))
print(checks)
