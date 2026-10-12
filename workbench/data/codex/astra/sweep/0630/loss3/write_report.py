from pathlib import Path
from datetime import datetime

P=Path(__file__).resolve().parent
report='''[M] 최다 공통 결손은 초반 섭취·증식 부족(Default·Trauma, 2/3); [E] 이후 전멸·여왕 공급 단절로 이어졌다.
[C/E] 카드 A = BEING BUILT `TERRITORY_DECAY:16`; 기존 후보를 검증하며 새 제안으로 세지 않는다.
[M/C] 판정·사망·코드 분기는 확신 높음; [E] 거리 할인으로 패전이 바뀐다는 확신은 낮음.

[M] 출전은 모두 A=21269(one11), 상대 팀 952. 라운드는 기보의 0 기준이며 r499가 마지막이다. [C] 줄 번호는 `data/online/smoke/one11-bot/main.cpp`. [M] 전환점은 사후적으로 다시 회복하지 못한 시점이지, 당시 승패 확정이라는 뜻은 아니다.

| 경기 | 실제 판정·최종 A / B (여왕, 최장, 총길이, 생존수) | 전환점·단일 핵심 패인 |
|---|---|---|
| 1496851 Around UNSW | [M] 최장. (0,33,372,60) / (0,34,175,24) | [M] r498 최장 33=33에서 r499 적 #1055가 (26,60)의 사체 진주를 먹어 34. 우리 최장 #1123은 r431 #728의 분열로 L30을 물려받은 뒤 69차례 중 66차례 무섭취, 자연진주 0·사체진주 3. **살아 있는 최장에게 성장이 붙지 않았다.** #720 L27, #971 L21도 살아 끝남. r455 #1121 L18 피격은 부수 손실이며 마지막 최장을 잃은 패전이 아니다. |
| 1496852 Default | [M] r329 전멸. (0,0,0,0) / (0,6,162,63) | [M] 총길이는 r14부터 계속 열세, 최장은 r318부터 계속 열세. r50 생존 8:14, r100 11:29. [E] **초반 무섭취 이동으로 증식이 뒤처진 뒤 소모전에서 전멸.** [M] r305 #183·r310 #177·r322 #211은 자신이 정면충돌, 마지막 #154는 r329 #207에게 피격. [E] 아래 여왕 피격이 별도의 승리 경로도 없앴다. |
| 1496857 Trauma | [M] 여왕. (31,31,31,1) / (42,42,134,35) | [M] 총길이 r19부터 열세. 마지막 아군 #422가 r394 #519에게 피격하여 여왕 #1만 남음. r395–499 여왕은 105차례 중 99차례 무섭취, 자연진주 6·공급 0; 적 #0은 자연 6·아군 사체 12를 먹음. [E] **공급자 소멸**이 성장 격차를 만들었다. [M] r436 30=30, r437 30:31부터 끝까지 열세. |

| 경제 재계수 [M], r0–100 | Default A:B | Trauma A:B |
|---|---:|---:|
| 자연 / 사체 진주 | 23:53 / 4:18 | 25:93 / 4:22 |
| 분열 횟수 | 13:31 | 13:51 |
| 우리 무섭취 이동 차례 / 그중 인접한 빈칸에 진주 없음¹ | 791 / 790 | 546 / 543 |

[M] ¹포털을 건너지 않는 한 걸음만 센다. [C] `EAT_FIRST:true`의 L7838–7842는 바로 갈 칸의 `pearl_here`가 필요하다. 따라서 위 790·543차례는 그 우선조건부터 거짓이다. [E] 원거리 목표 선택의 결손 후보지만 지도 접근성·경쟁과 분리하지 못했으며 특정 점수항의 책임은 미입증이다.

| 여왕 사망·공격 [M] | 켜진 보호가 놓친 정확한 조건 [C/M] | 사망 뒤 적 여왕 5걸음 접근 [M] |
|---|---|---|
| Around #1, r239 L3. #503 L4가 (58,27)→(59,27)*→(59,28)→(59,29)→(59,30)으로 4걸음 피격. | 마지막 여왕 차례에 공격자 몸 전체가 시야 밖이며 과거 머리 목격도 0. `QUEEN_SAFETY:true`, `REACH_EATS:true`여도 L4030–4035의 로컬/기억 입력에 없다. `QUEEN_DEFEND_STEPS:3`: 마지막 여왕 차례의 가까운 #520은 L5여서 L4298의 `length > TRADE_MAX_LENGTH(4)`로 제외. 공격자를 본 #467은 여왕을 못 봄. `QUEEN_FAR_HEADS:0`·`QUEEN_EDGE_REACH:0`은 CARDS의 BEING BUILT 영역. | 해당 없음. 적 #0이 먼저 r46 (12,56)에서 자기 몸 (12,55)에 충돌사. 살아 있는 추격 대상이 없었다. |
| Default #0, r60 L3. #23 L3가 (7,24)→(7,25)*→(6,25)→(5,25), 3걸음 피격. | `CUT_BODY_LEN:4`, `CUT_BODY_STRIDE:true`, `REACH_EATS:true` 모두 LIVE. 공격자의 나머지 몸은 포털 너머 (27,27),(27,26). 보이는 머리 (7,24)는 시야 테두리가 아님. L2486–2487에서 `edge_ids`에 못 들어가고 L5997–5998이 길이 **1** 반환. L6102–6103은 진주 1개를 먹어도 두 번째 걸음을 불허하여 실제 3걸음을 누락. | 해당 없음. 우리 #11이 r54 (8,23)의 적 #1 L6을 먼저 정면충돌로 죽였다. |
| Trauma #1 생존 | `QUEEN_BOOT_LEN:6`은 L7315–7317의 `known_leader_len < 6`에서만 예외 공급. r395 L25에서는 해당 안 됨. L3869의 생존수 ≤3 공급 금지도 적용 대상이며, 마지막 아군 사망 뒤 공급자 자체가 없다. 이 공급 예외는 공급자를 다시 만들지 않는다. | 우리 여왕 사망 없음. |

[M] 아래는 죽은 여왕의 마지막 세 **자기 차례 시작** 7×7 판면이다. 중앙 Q=여왕 머리, q=몸, A/a=아군 머리/몸, E/e=적, *=진주, .=빈칸, 선=켈프, :=포털. 좌표는 중앙이며 북쪽이 위다. 화살표는 실제 선택.

BOARDS

| 순위·설명 범위 | 카드·코드·검증 수치 |
|---|---|
| 1. [M/E] 초반 섭취·증식 부족 → 전멸/공급자 소멸, Default·Trauma **2/3** | **A — BEING BUILT.** [C/E] 일반 용의 영역 점수에서 멀리 있는 공급을 `exp(-(steps-1)/16)`로 할인해 가까운 공급을 택하게 한다. 기존 `TERRITORY_DECAY:16`, L402, L4742–4745, L5235–5245; 현재 값 0. [M] 기준 자연진주 23·25, 무섭취 이동 791·546, r100 생존 11·9. [E] 같은 관측 조건에서 자연진주/차례·분열이 늘고 r100 생존이 줄지 않아야 한다. 총섭취가 늘어도 자연진주/차례가 그대로거나 생존이 감소하면 설명/카드 반증. 효과는 미측정. |
| 공동 1. 보조 원인: [M] 여왕 위험 입력 누락, Around·Default **2/3**; 최종 패인 순위와 중복 | **B — LIVE-BUT-FAILED** (`CUT_BODY_LEN:4`, `CUT_BODY_STRIDE:true`). [E] 여왕이 본 적 몸이 **포털 경계에 닿으면** 시야 테두리처럼 잘린 몸으로 처리하고 기억 길이/하한 4를 적용한다. L2486–2487의 조건 확장 → L5995–6002·L1886–1892 재사용. 새 규칙은 아직 없음. [M/C] Default (7,24)의 북쪽은 포털이며 현재 인식길이 1. [E] 검증: 이 입력의 길이 1→≥4, 실제 도착칸 (5,25)의 누락 1→0, 안전 대안 선택 여부를 센다. 포털 오경보로 안전 출구를 모두 거부하거나 생존이 악화하면 반증. 직접 대상 **1/3**이며 Around의 시야 밖 머리는 이 카드로 해결되지 않는다. |
| 3. [M] 최장 성장 정체, Around **1/3** | **No card.** [C] `FEED_CAP_ROUND:350`은 L7326–7328의 공급 시기만 연다. 먼 아군 유도는 `RALLY_FRESH:0`, `RALLY_END_FRESH:0`이라 L7306의 `fresh <= 0`에서 꺼짐. [M] 최장 #1123 자연섭취 0/69차례. [E] 개별 공급자의 리더 기억·거리 조건은 복원하지 않았으므로 이것만으로 랠리 재채택을 주장하지 않는다(CARDS의 dropped). |

[M] `analyze.py`는 기존 `tools/ladder_replay.py`를 가져와 읽었고, `detail.py`·`audit.py`로 판면·최종 상태·섭취를 교차 확인했다. 근거는 `*-scan.json`, `*-detail.json`, `audit.json`. [E] 행동 변경 후 생존·승패, 내부 점수/음파 기억, CPU는 미검증. 게임·네트워크·봇 실행은 하지 않았다.

기록 시각: TIMESTAMP.
'''
blocks=(P/'boards.txt').read_text().strip().split('\n\n')
assert len(blocks)==6
table=''
for start in (0,3):
    labels=[]; cells=[]
    for block in blocks[start:start+3]:
        lines=block.splitlines();title=lines[0]
        label=title.split(' action=')[0]+' → '+('북' if start==0 else '동' if len(labels)<2 else '남')
        labels.append('[M] '+label)
        cells.append('<pre>'+''.join(line.replace('|','&#124;')+'<br>' for line in lines[1:16])+'</pre>')
    table+='| '+' | '.join(labels)+' |\n|---|---|---|\n| '+' | '.join(cells)+' |\n\n'
report=report.replace('BOARDS',table).replace('TIMESTAMP',datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z'))
(P/'report.md').write_text(report)
prose='\n'.join(line for line in report.splitlines() if not line.startswith('|'))
assert len(prose.split())<600
print('report written; prose words excluding tables:',len(prose.split()))
