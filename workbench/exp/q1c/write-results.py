import json, subprocess
from pathlib import Path
P=Path(__file__).parent; root=P.parents[1]
A=json.loads((P/'analysis.json').read_text());S=json.loads((P/'summary.json').read_text());R=json.loads((P/'review.json').read_text());PA=json.loads((P/'propagation-audit.json').read_text())
now=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()
def pct(v):return '미확인' if v is None else f'{100*v:.2f}%'
def aggregate(s,field):
 z=[S['groups'][s]['primary'][field]];d={k:sum(x[k] for x in z) for k in ['N','TP','FP','FN','TN']}
 d.update(accuracy=(d['TP']+d['TN'])/d['N'],precision=d['TP']/(d['TP']+d['FP']),recall=d['TP']/(d['TP']+d['FN']));return d
rows=[
('b: 백업 길이 r350 증가','Δ 중앙값 +1; +/0/−=6/2/2','공통 생존 12키 중 관측 10; null 2','PASS'),
('b: 백업 길이 r400 증가','Δ 중앙값 0; +/0/−=4/2/4','같은 10키; null 2','FAIL'),
('b: 백업 길이 r430 증가','Δ 중앙값 +2.5; +/0/−=6/2/2','같은 10키; null 2','PASS'),
('b: 여왕 2칸 안 머리 비증가','r340–429 중앙값 0→0, ≥2 0/117→0/117; 공통 checkpoint 증가 4/102. r430–480 중앙값 0→0, ≥2 0/78→0/66; 증가 1/60','36키; 증가 키 각각 4/1','FAIL(개별 증가; 집계 중앙값·≥2 몫은 유지)'),
('b: r300 이후 아군 몸 함정 비증가','off/b 각각 0; 새 함정 0','36키씩; flip 8키씩도 0','PASS'),
('b: 목표 id·실제 질량 이동','목표 #228 L10 직접 시야·bl10 일치; #268→#256 진주 2/2 섭취; flip A 여왕 #1 목표 허용','판면 목표 표본 2; 기증 1; BUILD 변형 fixture 4','PASS(표본); 전체 내부 관측기억 전수 검증은 아님'),
('c: 네 RETURN 여왕 feed/merge 관문','믿음=false 위반 0; c/on/self 여왕 feed 17/16/12','전체 feed 947/938/310; cv2 실판 기회 0','PASS(발동 경로); cv2 미확인'),
]
for s in ['c','on','self']:
 for field,label in [('belief','믿음'),('senderTurns','송신 bit(송신 차례 중복 제거)'),('rays','송신 bit(ray)')]:
  d=aggregate(s,field);rows.append((f'c: {s} {label} 정확도>50%',f"정확도 {pct(d['accuracy'])}, P/R {pct(d['precision'])}/{pct(d['recall'])}; TP/FP/FN/TN={d['TP']}/{d['FP']}/{d['FN']}/{d['TN']}",str(d['N']),'PASS' if d['accuracy']>.5 else 'FAIL'))
rows.extend([
('c: true 직접 소나 전달·다음 차례 설정','c 1634/1634, on 1771/1771, self 1347/1347; delay≤1; 팀 불일치 0','4752 신선한 채택 기회; 중복/더 신선한 증거 제외 993','PASS'),
('c: stale/same-round/false/relay 비갱신·50 감쇠·비메아리','재구성 errors 0; 만료 true 0; 수신 믿음만 가진 송신 true 0','655277 우리 차례; 만료 605238차례','PASS'),
('공통: off WASM·사건/소나 동일','518494 bytes/SHA 동일; identity 두 도구 각각 6/6','WASM 2; 동일성 6키/12판','PASS'),
('공통: r300 목표 시계·초기 물리 차이 공개','Q1 시계 300 유지; 소나/표식 제외 첫 행동 r300전 off/b 7키(최초65), off/c 1키(209), b/on 0키','각44키','PASS(시계); b의 의도 범위 밖 행동 변화는 안전성 우려'),
('공통: CPU 경보80M·한도100M','최대32.7M; ≥80M/≥100M 0; CPU 누락0','196판','PASS'),
('공통: 오류·누락·재구성 깨짐 0','historyErrors/missing/errors 및 checks 전 항 0; validation 오류0','196판; c/on/self 655277차례','PASS'),
('both 안전 판면: 새 여왕 아군 몸 함정','stronghold B/hunter r496 trap/a 1; off/b/c는 해당 여왕 생존','b/on 44짝; 새 함정1키','FAIL'),
])
table='| 사전 기준/안전 점검 | 값 | N | 판정 |\n|---|---|---|---|\n'+'\n'.join('| '+' | '.join(row)+' |' for row in rows)+'\n'
lead=f'\n\n## 14. Q1c ANALYSIS 결과 ({now})\n\n기존 196판을 `exp/q1c/ANALYZE.md`대로 `UNSW_RULES=123`으로 분석했다. 소스·명세 검증 통과(현재 v1.8 변경 없음), 새 게임·봇/params 수정·커밋·네트워크 0. 승패·최종 총 길이는 판정에 쓰지 않았다. 주 집계는 원 지도 36키이며 flip 8키는 별도 id 검증이다.\n\n'
notes='''
- **b:** 공통 r430 생존 12키 중 arena/hunter A와 M_07/king B는 이미 종료돼 checkpoint가 null이다. 0으로 채우지 않았다. 한쪽만 생존한 4키는 Australia B/hunter(off r256 trap/a→b 생존), L_03 A/king(off 생존→b r242 rammed), L_03 A/hunter(생존→r371 sac), L_03 B/hunter(생존→r414 rammed)다. 선택 변화·사망 ±2라운드·몸/행동은 `review.json`, crowd 증가 6키(원5+flip1)의 ±2라운드 실제 판면은 `crowd-review.txt`다. r400 증가는 없지만 r430·실제 백업 섭취는 개선 방향이다. 개별 crowd 증가를 숨기지 않는다.
- **목표와 관측:** Trauma B/king r340 #213 L2는 직접 보이는 #228 L10(30,19)을 목표로 S 이동한다(`qbk228,-1`, `bl10@30,19`). big_empty B/king r340 #11 L14는 #12 L26 소식(1,52)을 택한다. 실제 그 라운드 머리는 (1,49)라 소식과 ground truth를 구분한다. flip Trauma A/king의 여왕은 팀 최저 id #1이며 r400 여왕 L19가 최장이므로 #3/#18 등이 #1을 목표로 삼는 것은 정상이다. r300–339는 목표 소식, r340부터 이동, r430 이후 기존 late 규칙이다. 전체 관측 최장 재현을 두 표본으로 주장하지 않았다.
- **c:** 관문은 발동했으나 true 목격이 드물어 false 정확도만으로 성공을 주장할 수 없다. 주 집계 정확도는 c 믿음45.60%/송신차례43.50%, on 49.67%/47.01%, self 47.74%/40.58%다. 정확도·precision/recall·분모의 지도/편/상대/시기 및 ray/송신차례 표는 `RESULT.md`에 있다. flip을 독립 표본으로 합산하지 않는다. cv2 표식 발동0은 미확인이다.
- **전파·감쇠:** true가 실제 다음 아군 차례에 전달된 횟수 c/on/self=1964/2116/1665; 더 신선하지 않은 330/345/318건을 제외한 1634/1771/1347건 전부 설정됐고 최대 지연1이다. 마지막 증거+50 초과 true 0, 수신만 가진 송신 bit=true 0, 모든 qc/수신·송신 재구성 오류0. self 8판 중 목격8/8, 채택6/8, r430+ feed7/8이며 전체 true 전파·late queen feed가 있다. M_07 두 편에는 전파 기회0이므로 그 키의 전파는 미확인이다.
- **stale는 위반과 구분:** c/on stronghold A/hunter r300 #184→여왕 #0는 heard280(age20), 실제 적 여왕은 이미 죽었으나 belief=true라 관문위반은 아니다. flip Trauma B/hunter c r406 #55는 heard389(age17), on r368 #40은 seen246(age122)/heard357(age11), r370 #45는 heard353(age17)다. 총5표식 모두 FP로 계산했으며 몸·판면은 `review.json`의 해당 차례/±2라운드다. 소나 진실은 차례 시작 기준이며 해당 차례 도중 적 여왕 사망 가능성은 독립 death 훅으로 확인했고, 모든 FP를 그대로 유지했다.
- **새 함정:** on stronghold B/hunter r494 여왕 L4가 escape-split2(qw)로 L2가 되고, r495 S로 (45,1), r496의 N은 자기 몸/켈프이고 E/S/W는 아군 #188 L79 몸이라 no-exit 후 충돌한다. qc=false(heard135)다. r494–498 벽 포함 판면은 `trap-on.txt`/`trap-base.txt`; off/b/c는 해당 여왕이 산다. 원시 새 함정을 의도적 먹이로 면제하지 않았다. b-only의 r300전 차이7키 원인(태그/메모리 비용·탐색 예산)은 이 기보로 분리할 수 없다.
- **원자료:** `analysis.json`, `summary.json`, `backup-mechanism.md`, `sight-mechanism.md`, `identity.txt`, `propagation-audit.json`, `review.json`. BUILD WASM/fixture를 확인했고 `nice -n 10` 호출은 환경에서 setpriority를 거부했으나 분석 명령은 정상 종료했다. 전 지도·시드2는 명세 밖이다.
'''
boards='\n**판면 2개: b-only stronghold A/hunter/시드1, 백업 #256 주변.** r395 #268 L3가 #256에 먹이로 사망하고 진주2개가 실제 #256에 모두 섭취됐다. 아래 r395→398의 L8→9는 섭취·다른 이동 비용을 함께 포함하며 순섭취2를 길이차와 혼동하지 않는다. 해당 라운드 여왕 #0가 최장이어서 `computeGoal`은 여왕 목표도 허용한다. 이 한 사례를 모든 기증자의 집결 목표가 백업으로 바뀌었다는 증거로 쓰지 않는다.\n\n'
for name in ['board-backup-before.txt','board-backup-after.txt']:boards+='```text\n'+(P/name).read_text().rstrip()+'\n```\n\n'
proposal='**제안: switch OFF (Q1B_BACKUP_ON=OFF, Q1C_SIGHT_ON=OFF).** b는 일부 질량 이동이 개선됐지만 개별 crowd 증가와 의도 밖 초기 행동·새 여왕 사망이 남는다. c는 관문·전파는 개선 방향이나 정확도 목표 미달과 both의 새 아군 몸 함정이 남아 “목적 개선 + 깨짐 없음”을 충족하지 않는다. 스위치는 수정하지 않았다.\n'
append=lead+table+notes+boards+proposal
with (root/'versions/v1.8/VERSION.md').open('a') as f:f.write(append)
detail=append+'\n## 분모·하위집계\n'
for variant in ['c','on','self']:
 z=S['groups'][variant]
 for label,field in [('믿음','beliefTable'),('송신 차례(네 ray 중복 제거)','signalTable')]:
  detail+=f'\n### {variant}: {label}\n\n| 분류 | 키 | N | TP | FP | FN | TN | 정확도 | precision | recall |\n|---|---|---|---|---|---|---|---|---|---|\n'
  for d in z[field]:detail+='| '+' | '.join(str(v) for v in [d['grouping'],d['key'],d['N'],d['TP'],d['FP'],d['FN'],d['TN'],pct(d['accuracy']),pct(d['precision']),pct(d['recall'])])+' |\n'
 detail+='\n원지도·flip ray/송신차례 분리: `summary.json`의 primary/flip. true 목격/relay/채택 원분모:\n\n```json\n'+json.dumps({p:z[p] for p in ['primary','flip']},ensure_ascii=False,indent=2)+'\n```\n'
detail+='\n## 백업 원 길이·한쪽만 생존·crowd·새 함정\n\n```json\n'+json.dumps(S['backup'],ensure_ascii=False,indent=2)+'\n```\n'
detail+='\n## 소나/표식 제외 최초 물리 행동 차이(양 팀 dragonAction)\n\n```json\n'+json.dumps(R['differences'],ensure_ascii=False,indent=2)+'\n```\n'
(P/'RESULT.md').write_text(detail)
lines=[f'Q1c ANALYSIS {now}; 기존196판, UNSW_RULES=123, 새 판/봇수정/커밋/네트워크0.',
'b 길이: 공통12키(관측10/null2), r350/400/430 Δ중앙값 +1/0/+2.5; PASS/FAIL/PASS.',
'b 안전: crowd 공통checkpoint 증가5/162(원5키), 중앙값·≥2몫 유지; FAIL. r300후 trap 0→0 PASS.',
'c 관문: 위반0/2195 feed, 여왕feed45; PASS. 믿음 정확도 원지도 c45.60/on49.67/self47.74% FAIL.',
'c 전파·감쇠:4752/4752 채택≤1라운드, 제외993;655277차례 재구성오류/만료true/수신만true송신0 PASS.',
'공통:196/196 누락·오류·checks0, 동일성6/6·WASM동일, CPU최대32.7M/누락0 PASS; both 새trap1 FAIL.',
'판면2개·모든 값/N/PASS/FAIL: versions/v1.8/VERSION.md §14; 하위표·예외 exp/q1c/RESULT.md.',
'제안: switch OFF (Q1B_BACKUP_ON=OFF, Q1C_SIGHT_ON=OFF); crowd·초기행동·새함정으로 깨짐 없음 미충족.']
assert len(lines)==8;(P/'RESULT.txt').write_text('\n'.join(lines)+'\n')
with (root/'DECISIONS.md').open('a') as f:f.write(f'\n\n### {now} — Q1c ANALYSIS\n기존196판/1.2.3 분석 완료. b r430 백업 Δ중앙값+2.5(N10, null2), r400 0; 개별 crowd 증가5 checkpoint/5키. c 전파4752/4752·관문위반0이나 목격 정확도50% 미달, both stronghold B/hunter r496 새 trap/a. 부분 적용 규칙으로 Q1B/Q1C 모두 OFF 제안, 스위치 변경 없음. 기준별 값/N/판정·판면2개는 `versions/v1.8/VERSION.md` §14, 8줄 요약은 `exp/q1c/RESULT.txt`. 새 게임·봇수정·커밋·네트워크0.\n')
print(now, 'result lines',len(lines))
