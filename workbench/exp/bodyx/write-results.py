import json
import subprocess
from pathlib import Path

p = Path(__file__).resolve().parent
root = p.parents[1]
a = json.loads((p / 'analysis.json').read_text())
r = json.loads((p / 'review.json').read_text())
v = json.loads((p / 'verification.json').read_text())
f = json.loads((p / 'fixture-check.json').read_text())
stamp = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'], text=True).strip()
on, off = r['sets']['on'], r['sets']['off']
qo, qf = v['sets']['on'], v['sets']['off']
rows = [
    ('자료 완전성', '192/192판, 누락0·실패이력0, 84짝·동일성12짝', '192판', 'PASS'),
    ('(a) census 거절/구 규칙 반례', 'ON 거절10/10, OFF 완주10/10; 모두 세 번째 S·두 걸음 뒤 몸 일치·안전한 한 걸음 대안 있음', '10 입력', 'PASS'),
    ('(a) 합성 전이·가격 보존', '3998/3998, drift0·가격 변경0', '3998 입력', 'PASS'),
    ('(a) 실제 발동·경로 회피', 'bodyxr 제거35(하한); default_small A #0 r52 NNW→N, 전체 사건 첫 차이가 해당 action', '84 ON판; 동일 입력 사례1', 'PASS'),
    ('(b) 모든 드래곤 다중 S', f"OFF19/{off['multi']}→ON0/{on['multi']}; 완주 {off['completed']}→{on['completed']}", 'OFF3189/ON3638 시도', 'PASS'),
    ('(b) 여왕 다중 S', f"OFF9/{qf['queenMulti']}→ON0/{qo['queenMulti']}; 완주 {qf['queenCompleted']}→{qo['queenCompleted']}", '각84 여왕판', 'PASS'),
    ('(b) 완전 입력 몸 배열·길이', 'C++/독립123 oracle/최종 replay drift0', '7281 완주(ON3504)', 'PASS'),
    ('(b) 매 걸음 머리·꼬리/update', f"stepDrift0·누락0; ON {qo['updates']}걸음, OFF {qf['updates']}걸음", '7281 완주 전체 검사', 'PASS'),
    ('(b) 실제 Planner 기억 drift0', '122/3504 불일치: 시작 해시121·끝 해시104·끝 길이1(중복)', '3504 예측/3504 완주', 'FAIL'),
    ('(b) 불확실 입력을 성공으로 제외', f"unknown 슬롯33·미관측 경로14·표식 누락0; 불확실/불일치 합집합 {qo['unqualified']}, 검증 인정 {qo['qualified']}", '3504 ON 완주', 'FAIL(불확실 잔존)'),
    ('(c) 다른 원시 사망 증가 없음', 'H672→717, O1370→1349, W5617→5421, A0→1; 키별 증가44/84', '각84판', 'FAIL'),
    ('(c) 다른 기제 사망 증가 없음', 'sac1573→1592, trap6997→6758, rammed285→301, ram255→268, enemyBody5→11, allyHead132→148, fault0→0, sprintDeath0→1; 증가52/84키', '각84판', 'FAIL'),
    ('(c) 새/조기 여왕 사망', '새5·기존보다 조기8; 전수 전후 판면 확인', '84짝', 'FAIL'),
    ('(c) 지급 실패/invalid A0', 'ON default A/hunter #14 r188 L2 NW에서 두 번째 걸음 A; OFF0', 'ON3638 다중 시도', 'FAIL'),
    ('(c) 오류/timeout/no reply0', '이력 오류0·tle0·action 누락0, ledger 10항 전부0; 잘못 인식 표식0', '192판; action 감사168판', 'PASS'),
    ('(c) OFF 공식 WASM 동일성', 'base/off 518494 bytes 전체 동일, SHA256 5df1351a1cfa33917e91786fa22e573910daf662e869bc6b6d3d76c2da5cce97', '공식 WASM 1짝', 'PASS'),
    ('(c) OFF 사건·음파 동일성', '12/12 IDENTICAL', '12짝', 'PASS'),
    ('(c) CPU80M/100M', 'ON max32.4M, OFF32.3M; 경보0·한도 초과0·측정 누락0', '192판', 'PASS'),
    ('(c) 탐색 깊이 확인', '226781 공통 차례: 하락3728·동일219492·상승3561; ON d0=16, OFF0', '226781 공통 round/id', 'PASS(확인; 깊이 임계치 사전등록 없음)'),
]
table = '\n'.join(['| 사전 기준 | 값 | N | 판정 |', '|---|---|---|---|'] + ['| ' + ' | '.join(row) + ' |' for row in rows])
intro = f'## 18. BODYX ANALYSIS 결과 ({stamp}; 기존 기보만)\n\n'
intro += '§17·`exp/bodyx/ANALYZE.md`의 기준을 유지했다. 모든 replay 도구는 `UNSW_RULES=123`으로 실행했다. 새 게임·봇/params 수정·커밋·네트워크0.\n\n'
details = '''

원시 S는 OFF1588→ON1591이다. 실제 action·차례 몸/지형 이웃으로 전수 확인한 ON1591건은 단일 먹이기1574·빈 출구0의 no-exit17이며, OFF는 먹이기1543·no-exit25·다중19·기타 단일1이다. 원시 집계에서 제외하지 않았다. 84키별 분모·원인 변화는 `exp/bodyx/keywise.tsv`, 증가 원인53키(원시/기제/여왕의 합집합)와 새/조기 여왕13건은 `safety-audit.md`, 전후 판면·실제 차례 입력9145건은 `review.json`·`boards/`에 있다.

기억 drift121건은 실제 시작 몸 해시부터 다르다. 시작이 맞고 끝만 틀린 Colosseum B #49 r124 WS는 미관측2칸의 진주 과대 추정으로 예측L4/실제L2다. 지급 실패 default A #14 r188도 미관측2칸으로 예측L3; 첫 포털 도착(27,27)에 실제 진주가 없어 L2인 채 유료 두 번째 걸음에서 A로 죽었다. 완전 입력 oracle0으로 이 실패를 통과시키지 않았다.

L8 유료 세 번째 사례는 arena A #0 r17 EEN(진주3): free2·paid1·L8→10; L14 무료 세 걸음은 big_empty A #115 r306 NNN(진주0): free4·paid0·L14 유지다. 모든 매 걸음 배열은 drift0이다. 첫 선택 변화60키와 사례87건은 `review.json`에 보존했다. 선택 변화 이후 같은 round/id의 깊이·사망 차이는 순수 비용이나 같은 입력의 인과 증거가 아니다. 시드1/명세21지도이며 시드2·전체 지도 검증은 미실시다. nice10을 요청했으나 환경이 setpriority를 거부했고 분석은 정상 종료했다.

**의도한 상황 판면2개 — default_small A/proxy4_king/seed1, 여왕 #0 L6.** r52까지 의미 있는 사건이 동일하고 첫 차이는 #0의 action(OFF NNW, ON N)이다. 시작 몸 [82,81,65,49,33,34], 진주 없는 NNW는 두 걸음 후 남은 (1,3)=49를 세 번째 W가 친다. ON은 bodyxr1로 제거하고 안전한 N을 출력했다. 다음 그림의 A는 (2,4), 몸은 [66,82,81,65,49,33]로 L6을 유지한다. `exp/v16/board.js`로 r52/r53 라운드 시작을 출력했다; 다른 드래곤도 그 사이 움직이며 켈프선은 생략된다. 해당 여왕의 실제 차례 입력은 별도 확인했다.
'''
pics = '\n\n'.join('```text\n' + (p / name).read_text().strip() + '\n```' for name in ['board-intended-before.txt', 'board-intended-after.txt'])
proposal = '\n\n**제안: switch OFF (`BODYX_ON=OFF`).** 목적(다중 자기 몸 충돌 회피)은 개선됐지만 기억 drift122·지급 실패1·다른 사망/새·조기 여왕 회귀가 남아 “목적 개선 + 깨짐 없음”의 부분 적용 규칙을 충족하지 않는다. 기본값은 수정하지 않았다. 다음 작업은 몸 기억·미관측 진주 입력 검증이다.\n'
text = intro + table + details + '\n' + pics + proposal
(p / 'RESULT.md').write_text(text)
with (root / 'versions/v1.8/VERSION.md').open('a') as out:
    out.write('\n\n' + text)
lines = [
    f'BODYX ANALYSIS {stamp}; 192/192판·84짝·누락0·이력오류0 PASS',
    '발동 PASS: census ON거절10/10·OFF완주10/10, 합성3998/3998, 실제 후보 제거35(하한)',
    f'다중 S PASS: 전체 OFF19/3189→ON0/3638; 여왕 OFF9/{qf["queenMulti"]}→ON0/{qo["queenMulti"]}; 원시S1588→1591',
    '몸 전이 PASS: 완주7281(ON3504) oracle/step/update drift0; 실제 기억 FAIL122/3504, unknown33·unseen14·누락0',
    '안전 FAIL: H+45·A+1, 원시 증가44/84키·기제 증가52/84키, 새여왕5·조기8, 지급실패1',
    '깨짐: 오류/timeout/no reply0 PASS; OFF공식WASM 동일·사건/음파12/12 PASS; CPU max32.4M/192판 PASS, 깊이 비교226781',
    '판면2: board-intended-before.txt / board-intended-after.txt; 기준별 값·N·판정은 VERSION.md §18·RESULT.md',
    '제안: switch OFF — 목적은 개선됐으나 기억 drift·지급 실패·사망 회귀가 남아 부분 적용 규칙 미충족.',
]
assert len(lines) == 8
(p / 'RESULT.txt').write_text('\n'.join(lines) + '\n')
with (root / 'DECISIONS.md').open('a') as out:
    out.write(f'\n\n### {stamp} — BODYX ANALYSIS\n\n다중 자기 몸 사망19→0(여왕9→0), census10/10·완전 입력 drift0. 실제 기억 drift122/3504·지급 실패1·원인별/키별 회귀 때문에 부분 적용 규칙상 OFF 제안. `versions/v1.8/VERSION.md` §18, `exp/bodyx/RESULT.md` 참조. 기존192판만 분석; 봇/params·게임·커밋·네트워크 변경0.\n')
print(stamp)
print('\n'.join(lines))
