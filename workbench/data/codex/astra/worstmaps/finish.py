import json
from pathlib import Path
from statistics import mean
from collections import Counter
from datetime import datetime
O=Path('data/codex/astra/worstmaps');rs=json.loads((O/'rows.json').read_text());ts=json.loads((O/'trace.json').read_text());names=['Australia','Tower Defense','Stripes','Around UNSW','Schooltime','Default','Devil']
p=O/'report.md';s=p.read_text();marker='| 특징별 발견 |';table=['[M] 상대를 고정한 주표본 비교(지도별 WHQ 3판+Cache 3판):','', '| [M] 지도 | r100 머릿수 | r100까지 자연진주 합계 |', '|---|---|---|']
for name in names:
 rr=[r for r in rs if r['map']==name and r['opp_id'] in (87,952)];assert len(rr)==6
 ns='/'.join(f"{mean(r['spatial']['100'][i]['N'] for r in rr):.1f}" for i in (0,1));es='/'.join(str(sum(e[0]<=100 and e[1]==i and e[3]=='n' for r in rr for e in r['eats'])) for i in (0,1));table.append(f'| {name} | {ns} | {es} |')
s=s.replace(marker,'\n'.join(table)+'\n\n'+marker)
s=s.replace('[M] 원장·경기별 라운드:', '[M] 출발 배치·경기별 열세/사망은 [evidence.md](evidence.md). 원장·경기별 라운드:')
p.write_text(s)
ls=[f'[M] 작성 시각: {datetime.now().astimezone().isoformat(timespec="seconds")}.', '[M] 입력은 inventory.json에 고정했다. 결과 작성 범위는 이 폴더뿐이다.', '', '| [M] 구조 | 대표 경기·우리 진영 | 우리 시작 머리 (x,y) | 상대 시작 머리 (x,y) |', '|---|---|---|---|']
seen=set()
for r in rs:
 f=r['features'];key=f['supply_sig']
 if key in seen:continue
 seen.add(key);cols=[' '.join(f"({z['xy'][0]},{z['xy'][1]})L{z['L']}" for z in f['starts'][i]) for i in (0,1)]
 ls.append(f"| {r['map']} {key} | {r['gid']} {r['own_side']} | "+' | '.join(cols)+' |')
ls+=['','[M] rは生ログの0起点。종료 뒤 이월은 생존 예측이 아니라 표본 분모 고정이다. 아래 `queen/longest/elim`은 실제 종국 상태의 판정 항목이다.', '', '| [M] 경기 | 지도 | 버전 | 상대 | 결과/판정 | 열세 시작 | 우리 여왕 사망 r:원인 |', '|---|---|---|---|---|---|---|']
for r in rs:
 qd=[f'{d[0]}:{d[4]}' for d in r['deaths'] if d[1]==0 and d[6]]
 ls.append(f"| {r['gid']} | {r['map']} | {r['src']} | {r['opp']} | {r['result']}/{r['how']} | {r['turn'] if r['turn'] is not None else '—'} | {','.join(qd) or 'alive'} |")
ls+=['','[M] 검증: 원 메타데이터 승자 61판, 독립 원장 스냅샷 244개, 진주 섭취 합계 122개와 일치했다. [validation.json](validation.json).', '[C] 기존 계수기는 `o1_scan.scan`, 바이너리 리더는 `label_report.agg.sb.load_replay`, 지형 그래프는 `count_local.Geo`를 import했다. 새 코드는 공간 배정과 공급 관측을 추가한다.', '[M] 온라인 기보는 타이머 사건이 없고 지도 TILE 타이머도 0이다. 구조가 일치하는 로컬 파일도 Devil에서는 관측 생성 위치와 맞지 않았다. 따라서 최종 표는 공급 설정을 사용하지 않고 현재 61판의 자연 생성 위치·섭취 후 생성 간격을 다시 센 결과다.', '[E] 빠른 칸 추정은 식사·점유·표본량에 좌우된다. 기보 전체를 이용한 사후 지형 설명이며 당시 봇이 알 수 있던 정보량을 뜻하지 않는다. 짧은 거리와 생산칸 최근접 배정도 몸 막힘·id 순서·가속을 반영한 실제 소유권은 아니다.', '[M] 공급 구조별 자료: [supply.json](supply.json). 모든 라운드 인구/길이와 기보 경로: [rows.json](rows.json).', '[C] 재생성 순서: `python3 -B analyze.py` → `supply.py` → `enrich.py` → `trace.py` → `render_report.py` → `finish.py` (각 스크립트를 저장소 루트에서 전체 상대경로로 실행). 입력 경기는 inventory.json의 목록을 기준으로 보존한다; analyze.py를 재실행하면 새로 도착한 기보가 추가될 수 있다.', '[M] `nice -n 10`은 환경에서 우선순위 변경이 거부되어 분석은 기본 우선순위로 실행됐다. 네트워크·봇 실행·컴파일·게시·원본 편집은 하지 않았다.']
ls=[x.replace('rは生ログの0起点。','라운드는 원 로그의 0부터 센다. ') for x in ls]
(O/'evidence.md').write_text('\n'.join(ls)+'\n')
print('outside-table words',len(' '.join(l for l in s.splitlines() if not l.startswith('|')).split()))
