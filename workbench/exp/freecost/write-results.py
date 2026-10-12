import json, subprocess
from pathlib import Path
p=Path('exp/freecost')
a=json.loads((p/'analysis.json').read_text()); s=json.loads((p/'summary.json').read_text()); audit=json.loads((p/'audit-review.json').read_text()); depth=json.loads((p/'actions.json').read_text())['depth']
timestamp=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()
criteria='''| 사전 기준 | 값(off → on) | N | 판정 |
|---|---|---|---|
| 1. L≥5 무료 다중 이동 수·차례당 비율 증가 | 1,630/119,526(1.364%) → 9,701/111,464(8.703%); 완주 1,613 → 9,681 | 68짝, 각 68판; 시드1 | PASS |
| 2a. 완전한 입력의 지급·길이·꼬리 predictor | oracleDrift 0; 합성 on 2,833/off 1,386 통과 | 기보 완주 MOVE 853,339(160판); 합성 4,219 | PASS |
| 2b. 실제 자기 몸 기억 drift=0 | knownBodyDrift 6,845, uncertainBodyDrift 204; 알려진 불일치의 free/paid/길이 차이 0, 몸 해시 차이 6,845 | predicted 350,600; unknownSlots=0 태그 347,615; 38/68키에서 known drift | FAIL |
| 2c. 재구성·관측 불확실성·태그 | sim/eatTC/splits/drops/ledger/final/lineage/natBal/dropBal/unknownDeath 모두 0; unknownBodies 2,985, blindUnverified 845, missingTags 0 | 160판; on 완주 MOVE 351,445 | PASS(불확실성은 성공에서 제외) |
| 3a. Hit Self 합계·키별 비증가 | 1,317 → 1,343(+26); 증가 23키 | 68짝 | FAIL |
| 3b. Hit Wall 합계·키별 비증가 | 3,490 → 3,289(−201); 증가 17키 | 68짝 | FAIL(합계 PASS, 키별 FAIL) |
| 3c. 여왕 사망·더 이른 사망 비증가 | 57 → 57; 새 사망 4키, 더 이른 사망 12키(새 사망 포함) | 68짝; 양쪽 사망 중 앞당김 8키 | FAIL(합계 PASS, 키별 FAIL) |
| 3d. oversprint·invalidAction·오류 0 | 각각 0 | 160판 | PASS |
| 4a. off 공식 WASM·사건/메시지 동일성 | 496,456 bytes/SHA-256 동일; 두 분석 모두 12/12 same | WASM 2개; 온라인·스프린트·생성 × 양편 × 양 상대 12키 | PASS |
| 4b. CPU <80M 경보/<100M 한도 | 최대 off 32.1M → on 32.4M; CPU 누락 0 | 160판 | PASS |
| 4c. 오류·실행 누락·실패 이력 없음 | missing/historyErrors 0, expectedGames 160, pairs 68, identity 12 | 160판 | PASS |
'''
notes='''- **선택 변화:** arena B/proxy4_king/시드1의 첫 차이 r15 #1은 같은 시작 몸 L5에서 off `N`, on `NE`다. on은 (7,8)→(7,7)→(8,7)의 진주를 먹고 L6으로 끝나며 free=2/paid=0, 비용 개선 +1.6이다. 아래 r16 판면 2개에서 머리 이동과 남은 몸을 확인했다. 기존 후보 관문은 유지된다.
- **3걸음 탈출:** big_empty A/proxy4_king/시드1 r91 #12는 L9에서 `NWW esc`, free=3/paid=0, 진주 없이 L9 유지(+3.2)다. 시작 (20,55)→(20,54)→(19,54)→(18,54), 꼬리 3칸만 정상 전진했다. off의 같은 id는 이미 다른 위치/L5여서 이 비교를 같은 상태의 가격 인과 증거로 쓰지 않는다. r91/92 양쪽 판면은 `exp/freecost/boards/`, 전체 몸은 `selected-states.json`에 있다.
- **비가격 사례:** Trophy B/hunter r12 #1은 양쪽 모두 같은 L3 몸·한 걸음인데 off `S`, on `W`로 달랐다. 무료 비용 개선 사례에서 제외했다. Q2b의 진주 경계 변경과 음파 길이 보고 변경을 이 기보만으로 분리할 수 없어, Q2b만의 기보 인과 효과는 미확인이다. 지급 경계와 threat 소거 방지는 실제 C++ 합성 검사에서 확인했다.
- **몸 전수 확인:** 불일치 7,049건의 시작/완료 몸·fc·실제 진주·포털/벽 경로는 `audit.json`에 있다. 알려진 6,845건은 길이·지급이 맞고 몸 순서/타일 해시가 다르다. 이 중 시작 몸 전체와 이동 경로가 관측창 안인 사례도 16건(Portals)이다. 예: proxy4_king/Portals B r169 #174, L6→7에서 예상 해시 3193563132 ≠ 실제 2175577662. unknownSlots=0이 기억의 모든 타일이 관측으로 확정됐다는 뜻은 아니며, big_empty r350의 갓 태어난 L17 #201처럼 창 밖 몸을 직선으로 추정한 사례도 포함한다. 이러한 표식/기억의 한계를 기준 통과로 바꾸지 않았다. 불확실 경로 204건 중 길이 차이 194건, 지급 차이 0이다. 독립 simulator 0과 완전한 입력 oracle 0으로 실제 기억의 FAIL을 덮지 않는다.
- **사망 판면 전수:** 회귀 34키의 양쪽 S/W 및 여왕 사망 7,154건을 실제 차례 순서의 직전/직후 몸·경로·판면으로 대조했다(`audit.json`, `audit-review.json`). 직후 다음 차례 판면 7,151건, 게임 끝 3건은 최종 전체 상태로 보완했다. 분류는 표식 기반이며 의도적 먹이 on/off 1,104/951, no-exit 2,557/2,501, 일반 자기 경로 0/13, 일반 벽 경로 1/0, 여왕 머리 접촉 14/13이다. 먹이/막힘 변화로 원시 S/W 합계를 면제하지 않았다. 구 유료 꼬리 예측으로는 비었다고 할 자기 칸에서 실제 충돌한 사례는 off 12건/on 0건이다(선택이 달라지므로 개별 동일 상태 개선 인과는 미확인). on Portals A/hunter r307 #175의 `EE`는 첫 E 포털 도착 (19,12) 뒤 둘째 E가 켈프라 사망했다. 공짜여도 알려진 경로 밖 벽 안전성은 미해결이다.
- **여왕 회귀:** 새 사망은 stronghold A/king r236 W, stronghold A/hunter r200 O, Portals B/hunter r172 W, Around UNSW A/hunter r449 W다. 양쪽 사망에서 앞당김은 arena B/king 30→26 H, default_small B/king 136→105 H, Colosseum B/hunter 60→32 H, Portals B/king 178→164 W, Trophy B/hunter 88→50 H, gen_X_07 A/king 125→110(H), B/king 196→171(W), A/hunter 127→97 W다. Slithery 양편·양 상대의 r3 W 4/4, Around UNSW B의 r6 W 2/2는 그대로다. 모든 초기 여왕 id는 팀별 최저 id로 확인했다.
- **탐색 깊이:** 같은 키·라운드·id의 d 표식 117,173쌍에서 on 낮음 1,631, 같음 113,494, 높음 2,048; 평균 off 6.9732/on 6.9763이다. 달라진 관측·선택이 포함돼 예측/태그 비용의 인과 검사는 아니며, CPU 경보는 없다.
'''
boards=[]
for mode in ['off','on']:
    board=(p/'boards'/f'{mode}-proxy4_king_arena_B_1-r16.txt').read_text().strip()
    boards.append(f'**{mode}, arena B/proxy4_king/시드1 r16**\n\n```text\n{board}\n```\n')
proposal='**제안: switch OFF.** 무료 다중 이동 목적은 의도한 방향으로 움직였지만 실제 몸 기억 drift와 키별 안전성 회귀가 남아 “목적 개선 + 깨짐 없음”의 부분 적용 규칙을 충족하지 않는다. 봇·params·스위치는 수정하지 않았다.'
section=f'\n\n## 13. Freecost ANALYSIS 결과 ({timestamp})\n\n기존 160판만 `exp/freecost/ANALYZE.md`대로 `UNSW_RULES=123`으로 분석했다. 새 게임·봇/params 수정·커밋·네트워크 0. 승패·최종 길이는 판정에 쓰지 않았다. 온라인 행동 근거는 `research/observations/duels.md` §9 가설1이다.\n\n{criteria}\n{notes}\n'+ '\n'.join(boards)+'\n'+proposal+'\n'
with Path('versions/v1.8/VERSION.md').open('a') as f:f.write(section)
report=f'# Freecost ANALYSIS — {timestamp}\n\n'+criteria+'\n## 무료 이동 분모\n\n시드1, 각 지도 4짝(A/B × king/hunter). 숫자는 무료 다중 이동/시작 L≥5 차례다. 키별 전체 분모·비율·차이는 `analysis.json.pairs`와 `summary.json.pairs`에 있으며, 평균 대신 전체 수를 합산했다.\n\n| 지도 | off | on | N(짝) |\n|---|---:|---:|---:|\n'
for key,g in s['maps'].items():report+=f"| {key} | {g['off']['freeMulti']}/{g['off']['turnsL5']} | {g['on']['freeMulti']}/{g['on']['turnsL5']} | 4 |\n"
report+='\n| 편/상대/시작 길이 | off 무료 이동/차례 | on 무료 이동/차례 |\n|---|---:|---:|\n'
for group in ['sides','opponents']:
 for key,g in s[group].items():report+=f"| {key} | {g['off']['freeMulti']}/{g['off']['turnsL5']} | {g['on']['freeMulti']}/{g['on']['turnsL5']} |\n"
for band in ['2-4','5-8','9-12','13+']:
 off=s['sets']['off']['bands'][band];on=s['sets']['on']['bands'][band];report+=f"| L{band} | {off['freeMulti']}/{off['turns']} | {on['freeMulti']}/{on['turns']} |\n"
report+='\n68키 중 수 증가 48, 동일 19, 감소 1; 차례당 비율 증가 48키. 양쪽 L≥5 차례가 없는 14키는 비율 미확인이다. gen_L_02/gen_R_01은 L≥5 N=0, gen_S_03은 발동 0/33으로 지도별 기제 미확인이다. 완주하지 못한 무료 시도는 off 17/on 20으로, 증가가 사망 시도에만 생긴 것은 아니다.\n\n'+notes+'\n'+'\n'.join(boards)
report+='\n## 키별 회귀(34키)\n\nΔ는 on−off이며, 왕 앞당김은 on 새 사망도 포함한다. 모든 기준은 합계와 키별로 따로 판정했다.\n\n| 키(모두 seed1) | ΔSelf | ΔWall | Δ여왕 사망 | 여왕 off→on 라운드 |\n|---|---:|---:|---:|---|\n'
for x in s['regressions']:
 def death(d):return f"r{d['round']} {d['reason']}" if d else '생존'
 report+=f"| {x['key']} | {x['selfDelta']:+d} | {x['wallDelta']:+d} | {x['queenDeathDelta']:+d} | {death(x['offDeath'])} → {death(x['onDeath'])} |\n"
report+='\n'+proposal+'\n\n원자료: `analysis.json`, `summary.json`, `audit.json`, `audit-review.json`, `actions.json`, `selected-states.json`; 보조 검증: `identity.txt`, `queendeath.txt`, `fixture-analysis.txt`, `compile-check.json`. 분석기와 보조 분석기만 실행했고 runq는 실행하지 않았다.\n'
(p/'RESULT.md').write_text(report)
lines=[
f'{timestamp} freecost ANALYSIS: 160판, 68 on/off짝, 동일성 12키; 새 게임/봇·params 수정/커밋/네트워크 0.',
'기준1 PASS: 무료 다중 이동 off 1630/119526(1.364%) → on 9701/111464(8.703%); 완주 1613→9681; N=68짝(seed1).',
'기준2 완전 입력 PASS: fixtures on 2833/off 1386, oracleDrift 0/853339 완주 MOVE; 재구성 checks 전부0/160판.',
'기준2 실제 기억 FAIL: knownBodyDrift 6845/347615 unknown=0태그(예측350600), 불확실204·unknown2985·blind845·누락0; 완전 관측 사례16.',
'기준3 FAIL: Self 1317→1343(증가23키), Wall 3490→3289(증가17키), 여왕57→57(새 사망4·앞당김12); N=68짝.',
'기준4 PASS: 공식 base/off WASM 동일, 사건·메시지12/12 동일; CPU 최대32.4M/160판(<80M), CPU누락0; d비교117173쌍(낮음1631).',
'오류/oversprint/invalidAction/missing/historyErrors 모두0/160판; 판면2개·전수 예외·분모는 VERSION.md §13와 exp/freecost/RESULT.md.',
'제안: switch OFF — 목적은 개선됐으나 몸 기억 drift와 키별 안전성 회귀가 남아 부분 적용 규칙의 깨짐 없음 미충족.'
]
(p/'RESULT.txt').write_text('\n'.join(lines)+'\n')
with Path('DECISIONS.md').open('a') as f:f.write(f'\n- **{timestamp} Freecost ANALYSIS(Codex): switch OFF 제안(부분 적용 규칙), 스위치 수정 없음.** 무료 다중 이동 1,630/119,526→9,701/111,464로 증가했으나 실제 기억 knownBodyDrift 6,845, Self +26, 여왕 새 사망 4키/앞당김 12키로 깨짐 없음 미충족. 완전 입력 oracle drift 0/853,339, off 동일성 12/12, CPU 최대32.4M, 실행 오류0/160. 상세 `versions/v1.8/VERSION.md` §13, `exp/freecost/RESULT.txt`(8줄). 새 게임·봇/params 수정·커밋·네트워크0.\n')
print(timestamp)
print('VERSION.md append, RESULT.md, RESULT.txt 8 lines, DECISIONS.md append')
