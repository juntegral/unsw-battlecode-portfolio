#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from statistics import median
H=Path(__file__).resolve().parent
f=json.loads((H/'findings.json').read_text())
s=json.loads((H/'summary.json').read_text())
t=json.loads((H/'timing_relationships.json').read_text())
rows=[json.loads(l) for l in (H/'games.jsonl').read_text().splitlines()]
by={(x['arm'],x['cells']):x for x in t}
large=[x for x in rows if x.get('finished') and x['arm']=='mGx6_vb' and x['cells']==65536]
ratios=[x['ratio'] for x in f['matched_4096_65536']]
text=[
'[M] 큰 지도에서 시간은 늘었으나, 기록된 timeout·메모리 kill·실행 오류는 0건이다.',
f'[M] 65,536칸: {min(x["ms_per_turn"] for x in large):.2f}–{max(x["ms_per_turn"] for x in large):.2f}ms/턴; 4판 완결, 2판 미완결, 10판 파일 없음.',
'[M/E] 로그 집계는 확실하다. WASM 100M/48MB 및 CPU 1초/벽시계 10초 한도 안전성은 미측정이다. 카드 없음.',
'',
f'[M] {f["as_of"]} 집계: {f["arms"]} arms, {f["folders"]}폴더, {f["complete"]}완결판, {f["turns"]:,}턴. 전부 native이고 턴별 usage 기록은 0개다. 모든 로그에 오류 문구가 없고, 완결판의 timeout 표시·실행 오류·unpaid sprint·illegal split은 모두 0이다.',
'',
'[M] 아래 ms는 **경기 전체 벽시계/양쪽 드래곤 턴 수**다. 엔진·상대·시작/정리 비용을 포함한다. N은 턴 시점 양쪽 생존수의 가중평균, r은 같은 면적에서 판별 평균 N과 ms의 Pearson 상관이다. [E] 지형·길이·동시 실행을 통제하지 않아 개체수 효과나 발산 경계로 해석할 수 없다.',
'',
'| [M] arm | 칸 | 완결/폴더 | ms/턴 | N | r | no-action 우리/old |',
'|---|---:|---:|---:|---:|---:|---:|',
]
for x in s:
    y=by[x['arm'],x['cells']]
    r=y['pearson_game_mean_alive_vs_game_ms']
    text.append(f'| {x["arm"]} | {x["cells"]:,} | {x["complete"]}/{x["dirs"]} | {y["weighted_ms"]:.3f} | {y["weighted_alive"]:.1f} | {r:.2f} | {x["action_death_ours"].get("no_action",0)}/{x["action_death_old_main"].get("no_action",0)} |' if r is not None else
                f'| {x["arm"]} | {x["cells"]:,} | {x["complete"]}/{x["dirs"]} | {y["weighted_ms"]:.3f} | {y["weighted_alive"]:.1f} | — | {x["action_death_ours"].get("no_action",0)}/{x["action_death_old_main"].get("no_action",0)} |')
text += [
'',
f'[M] 같은 가족·좌석의 4,096→65,536칸 짝 4개에서 ms는 {min(ratios):.2f}–{max(ratios):.2f}배다(면적 16배). Islands 양편은 N≈124로 비슷하다. [E] 최대 크기에서 비용 증가는 보이나 초선형 꺾임은 입증되지 않았다.',
'',
f'[M] 4,096칸 이상 {f["large_games"]}판: no-action 우리 {f["large_action_death_ours"].get("no_action",0)}, old main {f["large_action_death_old_main"].get("no_action",0)}; timeout 0. 최대 크기만은 20/33이다. 모두 action=no-action, timeout=false였고 로그 사망수와 일치했다.',
'',
'[M] 기보 순간(0-based): `mGx6_vb/gx_islands_256x256_911207-seed1-side0` r205 #32(old), r355 #71(우리); `...-side1` r358 #110(우리)는 no-action이며 timeout=false다. 같은 양편 r499 종료가 크기 비교의 종점이다. 로그 라운드는 +1이다.',
'',
'[M] 미완결은 `mGx6_vb/gx_ring_256x256_911307-seed1-side0/1`: 마지막 사망 로그 173/140, 결과·기보 없음. [E] 중단 원인은 모른다. 8개 최대 지도 중 완결은 Islands/Poor 두 지도뿐이다.',
'',
'[C] 감사 기준 `one5-bot/main.cpp`의 비용 경로는 rival/ally floods 2512–2546, survey 3089–3231, herd 3430–3499, QH 2158–2248이다. [E] **턴 전체 공통 작업량 상한**으로 이들을 묶어야 한다. survey는 끝난 뒤에만 `turn_cells`를 증가시킨다(:3231); `CELL_BUDGET=12000`(:164), `SURVEY_CAP=0`(:187)은 현재 전체 비용을 제한하지 않는다. 배열 초기화·DFS·입출력 비용과 합법 fallback 여유도 남겨야 한다. [E] 안전한 숫자 상한은 points 실측 없이 정할 수 없고, 로그만으로 즉시 필요함도 입증되지 않는다.',
'',
'[C] 무행동 먹이기 경로도 있다(:647–652). [E] no-action 사망 자체를 CPU 실패로 세면 안 된다.',
'',
'[M] one6와 mGx6 소스 해시는 같다. 최신 one11의 최대 지도 WASM points/RSS, 개별 턴 소요시간, 미완결 원인은 확인하지 못했다. 새 게임·네트워크·봇 단독 실행은 하지 않았다. 원자료: [games](games.jsonl), [크기별 집계](summary.tsv), [마릿수 관계](timing_relationships.json), [최대 지도 누락](one6_coverage.json), [로그 검사](log_audit.json).',
]
report='\n'.join(text)+'\n'
body='\n'.join(l for l in text if not l.startswith('|'))
assert len(body.split())<350,len(body.split())
assert sum(l.startswith('|---') for l in text)==1
(H/'report.md').write_text(report)
print('words outside table',len(body.split()),'table rows',len(s),'report written')
