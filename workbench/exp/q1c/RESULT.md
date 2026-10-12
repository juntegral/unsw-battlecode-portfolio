

## 14. Q1c ANALYSIS 결과 (2026-10-02 07:10:31 KST)

기존 196판을 `exp/q1c/ANALYZE.md`대로 `UNSW_RULES=123`으로 분석했다. 소스·명세 검증 통과(현재 v1.8 변경 없음), 새 게임·봇/params 수정·커밋·네트워크 0. 승패·최종 총 길이는 판정에 쓰지 않았다. 주 집계는 원 지도 36키이며 flip 8키는 별도 id 검증이다.

| 사전 기준/안전 점검 | 값 | N | 판정 |
|---|---|---|---|
| b: 백업 길이 r350 증가 | Δ 중앙값 +1; +/0/−=6/2/2 | 공통 생존 12키 중 관측 10; null 2 | PASS |
| b: 백업 길이 r400 증가 | Δ 중앙값 0; +/0/−=4/2/4 | 같은 10키; null 2 | FAIL |
| b: 백업 길이 r430 증가 | Δ 중앙값 +2.5; +/0/−=6/2/2 | 같은 10키; null 2 | PASS |
| b: 여왕 2칸 안 머리 비증가 | r340–429 중앙값 0→0, ≥2 0/117→0/117; 공통 checkpoint 증가 4/102. r430–480 중앙값 0→0, ≥2 0/78→0/66; 증가 1/60 | 36키; 증가 키 각각 4/1 | FAIL(개별 증가; 집계 중앙값·≥2 몫은 유지) |
| b: r300 이후 아군 몸 함정 비증가 | off/b 각각 0; 새 함정 0 | 36키씩; flip 8키씩도 0 | PASS |
| b: 목표 id·실제 질량 이동 | 목표 #228 L10 직접 시야·bl10 일치; #268→#256 진주 2/2 섭취; flip A 여왕 #1 목표 허용 | 판면 목표 표본 2; 기증 1; BUILD 변형 fixture 4 | PASS(표본); 전체 내부 관측기억 전수 검증은 아님 |
| c: 네 RETURN 여왕 feed/merge 관문 | 믿음=false 위반 0; c/on/self 여왕 feed 17/16/12 | 전체 feed 947/938/310; cv2 실판 기회 0 | PASS(발동 경로); cv2 미확인 |
| c: c 믿음 정확도>50% | 정확도 45.60%, P/R 70.69%/9.31%; TP/FP/FN/TN=12067/5004/117515/90616 | 225202(원지도36키) | FAIL |
| c: c 송신 bit(송신 차례 중복 제거) 정확도>50% | 정확도 43.50%, P/R 81.77%/2.96%; TP/FP/FN/TN=3813/850/124971/93076 | 222710(원지도36키) | FAIL |
| c: c 송신 bit(ray) 정확도>50% | 정확도 49.86%, P/R 84.95%/2.01%; TP/FP/FN/TN=5358/949/261180/255316 | 522803(원지도36키) | FAIL |
| c: on 믿음 정확도>50% | 정확도 49.67%, P/R 73.55%/10.72%; TP/FP/FN/TN=12952/4657/107819/98027 | 223455(원지도36키) | FAIL |
| c: on 송신 bit(송신 차례 중복 제거) 정확도>50% | 정확도 47.01%, P/R 82.10%/3.18%; TP/FP/FN/TN=3816/832/116296/100086 | 221030(원지도36키) | FAIL |
| c: on 송신 bit(ray) 정확도>50% | 정확도 55.75%, P/R 86.02%/2.31%; TP/FP/FN/TN=5376/874/227710/282642 | 516602(원지도36키) | PASS |
| c: self 믿음 정확도>50% | 정확도 47.74%, P/R 86.68%/17.50%; TP/FP/FN/TN=8591/1320/40514/29620 | 80045 | FAIL |
| c: self 송신 bit(송신 차례 중복 제거) 정확도>50% | 정확도 40.58%, P/R 95.46%/4.01%; TP/FP/FN/TN=1957/93/46821/30079 | 78950 | FAIL |
| c: self 송신 bit(ray) 정확도>50% | 정확도 51.57%, P/R 93.53%/3.46%; TP/FP/FN/TN=3337/231/93243/96190 | 193001 | PASS |
| c: true 직접 소나 전달·다음 차례 설정 | c 1634/1634, on 1771/1771, self 1347/1347; delay≤1; 팀 불일치 0 | 4752 신선한 채택 기회; 중복/더 신선한 증거 제외 993 | PASS |
| c: stale/same-round/false/relay 비갱신·50 감쇠·비메아리 | 재구성 errors 0; 만료 true 0; 수신 믿음만 가진 송신 true 0 | 655277 우리 차례; 만료 605238차례 | PASS |
| 공통: off WASM·사건/소나 동일 | 518494 bytes/SHA 동일; identity 두 도구 각각 6/6 | WASM 2; 동일성 6키/12판 | PASS |
| 공통: r300 목표 시계·초기 물리 차이 공개 | Q1 시계 300 유지; 소나/표식 제외 첫 행동 r300전 off/b 7키(최초65), off/c 1키(209), b/on 0키 | 각44키 | PASS(시계); b의 의도 범위 밖 행동 변화는 안전성 우려 |
| 공통: CPU 경보80M·한도100M | 최대32.7M; ≥80M/≥100M 0; CPU 누락0 | 196판 | PASS |
| 공통: 오류·누락·재구성 깨짐 0 | historyErrors/missing/errors 및 checks 전 항 0; validation 오류0 | 196판; c/on/self 655277차례 | PASS |
| both 안전 판면: 새 여왕 아군 몸 함정 | stronghold B/hunter r496 trap/a 1; off/b/c는 해당 여왕 생존 | b/on 44짝; 새 함정1키 | FAIL |

**flip 별도 확인(독립 표본에 합산하지 않음):** b 공통 생존 6키의 r350/400/430 Δ중앙값 −1.5/−0.5/0(각 N6, +/0/− 각각0/1/5·2/1/3·3/0/3): 길이 증가 FAIL. crowd 중앙값·≥2 몫 유지, 공통 checkpoint 1/90 증가로 비증가 FAIL; trap0 PASS. 팀 최저 id가 원 지도 반대편과 같음을 실제 초기 상태에서 확인했다.

| flip 목격 기준 | 값 | N | 판정 |
|---|---|---|---|
| c 믿음 정확도>50% | 정확도33.90%, P/R 89.78%/5.40%; TP/FP/FN/TN=2320/264/40642/18659 | 61885, 8키 | FAIL |
| c 송신 차례 정확도>50% | 정확도31.26%, P/R 93.29%/1.05%; TP/FP/FN/TN=445/32/42113/18723 | 61313, 8키 | FAIL |
| c ray 정확도>50% | 정확도35.46%, P/R 95.13%/0.68%; TP/FP/FN/TN=625/32/90791/49281 | 140729, 8키 | FAIL |
| on 믿음 정확도>50% | 정확도37.11%, P/R 83.90%/5.64%; TP/FP/FN/TN=2403/461/40224/21602 | 64690, 8키 | FAIL |
| on 송신 차례 정확도>50% | 정확도34.85%, P/R 92.77%/1.24%; TP/FP/FN/TN=526/41/41728/21820 | 64115, 8키 | FAIL |
| on ray 정확도>50% | 정확도41.18%, P/R 93.86%/1.15%; TP/FP/FN/TN=1039/68/89296/61528 | 151931, 8키 | FAIL |

- **b:** 공통 r430 생존 12키 중 arena/hunter A와 M_07/king B는 이미 종료돼 checkpoint가 null이다. 0으로 채우지 않았다. 한쪽만 생존한 4키는 Australia B/hunter(off r256 trap/a→b 생존), L_03 A/king(off 생존→b r242 rammed), L_03 A/hunter(생존→r371 sac), L_03 B/hunter(생존→r414 rammed)다. 선택 변화·사망 ±2라운드·몸/행동은 `review.json`, crowd 증가 6키(원5+flip1)의 ±2라운드 실제 판면은 `crowd-review.txt`다. r400 증가는 없지만 r430·실제 백업 섭취는 개선 방향이다. 개별 crowd 증가를 숨기지 않는다.
- **목표와 관측:** Trauma B/king r340 #213 L2는 직접 보이는 #228 L10(30,19)을 목표로 S 이동한다(`qbk228,-1`, `bl10@30,19`). big_empty B/king r340 #11 L14는 #12 L26 소식(1,52)을 택한다. 실제 그 라운드 머리는 (1,49)라 소식과 ground truth를 구분한다. flip Trauma A/king의 여왕은 팀 최저 id #1이며 r400 여왕 L19가 최장이므로 #3/#18 등이 #1을 목표로 삼는 것은 정상이다. r300–339는 목표 소식, r340부터 이동, r430 이후 기존 late 규칙이다. 전체 관측 최장 재현을 두 표본으로 주장하지 않았다.
- **c:** 관문은 발동했으나 true 목격이 드물어 false 정확도만으로 성공을 주장할 수 없다. 주 집계 정확도는 c 믿음45.60%/송신차례43.50%, on 49.67%/47.01%, self 47.74%/40.58%다. 정확도·precision/recall·분모의 지도/편/상대/시기 및 ray/송신차례 표는 `RESULT.md`에 있다. flip을 독립 표본으로 합산하지 않는다. cv2 표식 발동0은 미확인이다.
- **전파·감쇠:** true가 실제 다음 아군 차례에 전달된 횟수 c/on/self=1964/2116/1665; 더 신선하지 않은 330/345/318건을 제외한 1634/1771/1347건 전부 설정됐고 최대 지연1이다. 마지막 증거+50 초과 true 0, 수신만 가진 송신 bit=true 0, 모든 qc/수신·송신 재구성 오류0. self 8판 중 목격8/8, 채택6/8, r430+ feed7/8이며 전체 true 전파·late queen feed가 있다. M_07 두 편에는 전파 기회0이므로 그 키의 전파는 미확인이다.
- **stale는 위반과 구분:** c/on stronghold A/hunter r300 #184→여왕 #0는 heard280(age20), 실제 적 여왕은 이미 죽었으나 belief=true라 관문위반은 아니다. flip Trauma B/hunter c r406 #55는 heard389(age17), on r368 #40은 seen246(age122)/heard357(age11), r370 #45는 heard353(age17)다. 총5표식 모두 FP로 계산했으며 몸·±2라운드 상태는 `review.json`, 실제 판면은 `stale-boards.txt`다. 소나 진실은 차례 시작 기준이며 해당 차례 도중 적 여왕 사망 가능성은 독립 death 훅으로 확인했고, 모든 FP를 그대로 유지했다.
- **새 함정:** on stronghold B/hunter r494 여왕 L4가 escape-split2(qw)로 L2가 되고, r495 S로 (45,1), r496의 N은 자기 몸/켈프이고 E/S/W는 아군 #188 L79 몸이라 no-exit 후 충돌한다. qc=false(heard135)다. r494–498 벽 포함 판면은 `trap-on.txt`/`trap-base.txt`; off/b/c는 해당 여왕이 산다. 원시 새 함정을 의도적 먹이로 면제하지 않았다. b-only의 r300전 차이7키 원인(태그/메모리 비용·탐색 예산)은 이 기보로 분리할 수 없다.
- **원자료:** `analysis.json`, `summary.json`, `backup-mechanism.md`, `sight-mechanism.md`, `identity.txt`, `propagation-audit.json`, `review.json`. BUILD WASM/fixture를 확인했고 `nice -n 10` 호출은 환경에서 setpriority를 거부했으나 분석 명령은 정상 종료했다. 전 지도·시드2는 명세 밖이다.

**판면 2개: b-only stronghold A/hunter/시드1, 백업 #256 주변.** r395 #268 L3가 #256에 먹이로 사망하고 진주2개가 실제 #256에 모두 섭취됐다. 아래 r395→399의 L8→10과 donor-origin 섭취2를 함께 확인했다(두 번째 진주는 r398 #256의 S 행동에서 섭취). 해당 라운드 여왕 #0가 최장이어서 `computeGoal`은 여왕 목표도 허용한다. 이 한 사례를 모든 기증자의 집결 목표가 백업으로 바뀌었다는 증거로 쓰지 않는다.

```text
round 395 around 10,17 (x 7..)
 14 aaaa**.
 15 a.aa...
 16 b......
 17 B.dd...
 18 *Ddd...
 19 Ccc....
 20 ..cc...
a=#0 L51  b=#256 L8  c=#264 L5  d=#265 L5
```

```text
round 399 around 10,17 (x 7..)
 14 aaaa**.
 15 a.aa...
 16 b......
 17 bbbb...
 18 *.*B...
 19 c......
 20 c......
a=#0 L52  b=#256 L10  c=#264 L5
```

**제안: switch OFF (Q1B_BACKUP_ON=OFF, Q1C_SIGHT_ON=OFF).** b는 일부 질량 이동이 개선됐지만 개별 crowd 증가와 의도 밖 초기 행동·새 여왕 사망이 남는다. c는 관문·전파는 개선 방향이나 정확도 목표 미달과 both의 새 아군 몸 함정이 남아 “목적 개선 + 깨짐 없음”을 충족하지 않는다. 스위치는 수정하지 않았다.

## 분모·하위집계

### c: 믿음

| 분류 | 키 | N | TP | FP | FN | TN | 정확도 | precision | recall |
|---|---|---|---|---|---|---|---|---|---|
| map | arena | 146 | 135 | 8 | 3 | 0 | 92.47% | 94.41% | 97.83% |
| map | big_empty | 68028 | 433 | 843 | 39288 | 27464 | 41.01% | 33.93% | 1.09% |
| map | Colosseum | 8707 | 743 | 1097 | 126 | 6741 | 85.95% | 40.38% | 85.50% |
| map | default_small | 12478 | 1371 | 1960 | 555 | 8592 | 79.84% | 41.16% | 71.18% |
| map | stronghold | 35643 | 3538 | 550 | 12934 | 18621 | 62.17% | 86.55% | 21.48% |
| map | trauma | 18211 | 1984 | 0 | 7075 | 9152 | 61.15% | 100.00% | 21.90% |
| map | australia | 40297 | 120 | 7 | 31010 | 9160 | 23.03% | 94.49% | 0.39% |
| map | gen_M_07 | 8869 | 34 | 22 | 268 | 8545 | 96.73% | 60.71% | 11.26% |
| map | gen_L_03 | 32823 | 3709 | 517 | 26256 | 2341 | 18.43% | 87.77% | 12.38% |
| map | trauma_flip | 18829 | 1089 | 264 | 4089 | 13387 | 76.88% | 80.49% | 21.03% |
| map | australia_flip | 43056 | 1231 | 0 | 36553 | 5272 | 15.10% | 100.00% | 3.26% |
| side | A | 143059 | 7922 | 2944 | 73245 | 58948 | 46.74% | 72.91% | 9.76% |
| side | B | 144028 | 6465 | 2324 | 84912 | 50327 | 39.43% | 73.56% | 7.08% |
| opp | proxy4_king | 115975 | 6296 | 844 | 62593 | 46242 | 45.30% | 88.18% | 9.14% |
| opp | bot-hunter | 171112 | 8091 | 4424 | 95564 | 63033 | 41.57% | 64.65% | 7.81% |
| period | 0-299 | 172551 | 10891 | 4559 | 108202 | 48899 | 34.65% | 70.49% | 9.14% |
| period | 300-429 | 91887 | 2901 | 627 | 45216 | 43143 | 50.11% | 82.23% | 6.03% |
| period | 430+ | 22649 | 595 | 82 | 4739 | 17233 | 78.71% | 87.89% | 11.15% |

### c: 송신 차례(네 ray 중복 제거)

| 분류 | 키 | N | TP | FP | FN | TN | 정확도 | precision | recall |
|---|---|---|---|---|---|---|---|---|---|
| map | arena | 145 | 132 | 8 | 5 | 0 | 91.03% | 94.29% | 96.35% |
| map | big_empty | 67496 | 95 | 84 | 39435 | 27882 | 41.45% | 53.07% | 0.24% |
| map | Colosseum | 8605 | 504 | 196 | 362 | 7543 | 93.52% | 72.00% | 58.20% |
| map | default_small | 12317 | 881 | 502 | 1027 | 9907 | 87.59% | 63.70% | 46.17% |
| map | stronghold | 35039 | 712 | 19 | 15552 | 18756 | 55.56% | 97.40% | 4.38% |
| map | trauma | 18046 | 545 | 0 | 8459 | 9042 | 53.13% | 100.00% | 6.05% |
| map | australia | 39981 | 47 | 0 | 30858 | 9076 | 22.82% | 100.00% | 0.15% |
| map | gen_M_07 | 8377 | 32 | 21 | 267 | 8057 | 96.56% | 60.38% | 10.70% |
| map | gen_L_03 | 32704 | 865 | 20 | 29006 | 2813 | 11.25% | 97.74% | 2.90% |
| map | trauma_flip | 18669 | 269 | 32 | 4881 | 13487 | 73.68% | 89.37% | 5.22% |
| map | australia_flip | 42644 | 176 | 0 | 37232 | 5236 | 12.69% | 100.00% | 0.47% |
| side | A | 141557 | 2674 | 564 | 77969 | 60350 | 44.52% | 82.58% | 3.32% |
| side | B | 142466 | 1584 | 318 | 89115 | 51449 | 37.23% | 83.28% | 1.75% |
| opp | proxy4_king | 114935 | 1878 | 132 | 66598 | 46327 | 41.94% | 93.43% | 2.74% |
| opp | bot-hunter | 169088 | 2380 | 750 | 100486 | 65472 | 40.13% | 76.04% | 2.31% |
| period | 0-299 | 171221 | 3711 | 862 | 114810 | 51838 | 32.44% | 81.15% | 3.13% |
| period | 300-429 | 90630 | 403 | 20 | 47175 | 43032 | 47.93% | 95.27% | 0.85% |
| period | 430+ | 22172 | 144 | 0 | 5099 | 16929 | 77.00% | 100.00% | 2.75% |

원지도·flip ray/송신차례 분리: `summary.json`의 primary/flip. true 목격/relay/채택 원분모:

```json
{
  "primary": {
    "games": 36,
    "belief": {
      "N": 225202,
      "TP": 12067,
      "FP": 5004,
      "FN": 117515,
      "TN": 90616,
      "accuracy": 0.455959538547615,
      "precision": 0.7068713022084236,
      "recall": 0.09312250158200985
    },
    "rays": {
      "N": 522803,
      "TP": 5358,
      "FP": 949,
      "FN": 261180,
      "TN": 255316,
      "accuracy": 0.4986084624610035,
      "precision": 0.8495322657364833,
      "recall": 0.020102199311167638
    },
    "senderTurns": {
      "N": 222710,
      "TP": 3813,
      "FP": 850,
      "FN": 124971,
      "TN": 93076,
      "accuracy": 0.4350455749629563,
      "precision": 0.8177139180784903,
      "recall": 0.029607715244129706
    },
    "relay": 191140,
    "directTrue": 5361,
    "visible": 997,
    "receivedOnly": 11710,
    "propagation": {
      "N": 1490,
      "set": 1490,
      "delayMax": 1
    },
    "feeds": 750,
    "queenFeeds": 14,
    "staleFeeds": [
      {
        "key": "bot-hunter:stronghold:A:1",
        "r": 300,
        "id": 184,
        "target": 0,
        "toQueen": true,
        "d": 2,
        "L": 2,
        "slack": 196,
        "kind": "conv",
        "belief": true,
        "enemyAlive": false,
        "queenAlive": true
      }
    ]
  },
  "flip": {
    "games": 8,
    "belief": {
      "N": 61885,
      "TP": 2320,
      "FP": 264,
      "FN": 40642,
      "TN": 18659,
      "accuracy": 0.3389997576149309,
      "precision": 0.8978328173374613,
      "recall": 0.05400121037195661
    },
    "rays": {
      "N": 140729,
      "TP": 625,
      "FP": 32,
      "FN": 90791,
      "TN": 49281,
      "accuracy": 0.3546248463358654,
      "precision": 0.9512937595129376,
      "recall": 0.006836877570665967
    },
    "senderTurns": {
      "N": 61313,
      "TP": 445,
      "FP": 32,
      "FN": 42113,
      "TN": 18723,
      "accuracy": 0.31262538124052,
      "precision": 0.9329140461215933,
      "recall": 0.01045631843601673
    },
    "relay": 47780,
    "directTrue": 527,
    "visible": 60,
    "receivedOnly": 2057,
    "propagation": {
      "N": 144,
      "set": 144,
      "delayMax": 1
    },
    "feeds": 197,
    "queenFeeds": 3,
    "staleFeeds": [
      {
        "key": "bot-hunter:trauma_flip:B:1",
        "r": 406,
        "id": 55,
        "target": 0,
        "toQueen": true,
        "d": 3,
        "L": 6,
        "slack": 85,
        "kind": "FE",
        "belief": true,
        "enemyAlive": false,
        "queenAlive": true
      }
    ]
  }
}
```

### on: 믿음

| 분류 | 키 | N | TP | FP | FN | TN | 정확도 | precision | recall |
|---|---|---|---|---|---|---|---|---|---|
| map | arena | 146 | 135 | 8 | 3 | 0 | 92.47% | 94.41% | 97.83% |
| map | big_empty | 68046 | 428 | 788 | 33679 | 33151 | 49.35% | 35.20% | 1.25% |
| map | Colosseum | 8707 | 743 | 1097 | 126 | 6741 | 85.95% | 40.38% | 85.50% |
| map | default_small | 12478 | 1371 | 1960 | 555 | 8592 | 79.84% | 41.16% | 71.18% |
| map | stronghold | 33878 | 3538 | 550 | 13359 | 16431 | 58.94% | 86.55% | 20.94% |
| map | trauma | 18427 | 2340 | 0 | 6846 | 9241 | 62.85% | 100.00% | 25.47% |
| map | australia | 41559 | 221 | 0 | 31333 | 10005 | 24.61% | 100.00% | 0.70% |
| map | gen_M_07 | 8869 | 34 | 22 | 268 | 8545 | 96.73% | 60.71% | 11.26% |
| map | gen_L_03 | 31345 | 4142 | 232 | 21650 | 5321 | 30.19% | 94.70% | 16.06% |
| map | trauma_flip | 19048 | 1220 | 372 | 3639 | 13817 | 78.94% | 76.63% | 25.11% |
| map | australia_flip | 45642 | 1183 | 89 | 36585 | 7785 | 19.65% | 93.00% | 3.13% |
| side | A | 144714 | 8354 | 3023 | 64421 | 68916 | 53.39% | 73.43% | 11.48% |
| side | B | 143431 | 7001 | 2095 | 83622 | 50713 | 40.24% | 76.97% | 7.73% |
| opp | proxy4_king | 115595 | 6496 | 514 | 55548 | 53037 | 51.50% | 92.67% | 10.47% |
| opp | bot-hunter | 172550 | 8859 | 4604 | 92495 | 66592 | 43.73% | 65.80% | 8.74% |
| period | 0-299 | 172360 | 10632 | 4504 | 107995 | 49229 | 34.73% | 70.24% | 8.96% |
| period | 300-429 | 91595 | 3149 | 362 | 37486 | 50598 | 58.68% | 89.69% | 7.75% |
| period | 430+ | 24190 | 1574 | 252 | 2562 | 19802 | 88.37% | 86.20% | 38.06% |

### on: 송신 차례(네 ray 중복 제거)

| 분류 | 키 | N | TP | FP | FN | TN | 정확도 | precision | recall |
|---|---|---|---|---|---|---|---|---|---|
| map | arena | 145 | 132 | 8 | 5 | 0 | 91.03% | 94.29% | 96.35% |
| map | big_empty | 67519 | 95 | 86 | 33919 | 33419 | 49.64% | 52.49% | 0.28% |
| map | Colosseum | 8605 | 504 | 196 | 362 | 7543 | 93.52% | 72.00% | 58.20% |
| map | default_small | 12317 | 881 | 502 | 1027 | 9907 | 87.59% | 63.70% | 46.17% |
| map | stronghold | 33304 | 712 | 19 | 15954 | 16619 | 52.04% | 97.40% | 4.27% |
| map | trauma | 18260 | 578 | 0 | 8555 | 9127 | 53.15% | 100.00% | 6.33% |
| map | australia | 41257 | 40 | 0 | 31303 | 9914 | 24.13% | 100.00% | 0.13% |
| map | gen_M_07 | 8377 | 32 | 21 | 267 | 8057 | 96.56% | 60.38% | 10.70% |
| map | gen_L_03 | 31246 | 842 | 0 | 24904 | 5500 | 20.30% | 100.00% | 3.27% |
| map | trauma_flip | 18888 | 280 | 41 | 4556 | 14011 | 75.66% | 87.23% | 5.79% |
| map | australia_flip | 45227 | 246 | 0 | 37172 | 7809 | 17.81% | 100.00% | 0.66% |
| side | A | 143230 | 2728 | 566 | 69660 | 70276 | 50.97% | 82.82% | 3.77% |
| side | B | 141915 | 1614 | 307 | 88364 | 51630 | 37.52% | 84.02% | 1.79% |
| opp | proxy4_king | 114586 | 1840 | 112 | 59915 | 52719 | 47.61% | 94.26% | 2.98% |
| opp | bot-hunter | 170559 | 2502 | 761 | 98109 | 69187 | 42.03% | 76.68% | 2.49% |
| period | 0-299 | 171030 | 3672 | 864 | 114386 | 52108 | 32.61% | 80.95% | 3.11% |
| period | 300-429 | 90431 | 394 | 9 | 39853 | 50175 | 55.92% | 97.77% | 0.98% |
| period | 430+ | 23684 | 276 | 0 | 3785 | 19623 | 84.02% | 100.00% | 6.80% |

원지도·flip ray/송신차례 분리: `summary.json`의 primary/flip. true 목격/relay/채택 원분모:

```json
{
  "primary": {
    "games": 36,
    "belief": {
      "N": 223455,
      "TP": 12952,
      "FP": 4657,
      "FN": 107819,
      "TN": 98027,
      "accuracy": 0.49665033228166744,
      "precision": 0.7355329660968822,
      "recall": 0.1072442887779351
    },
    "rays": {
      "N": 516602,
      "TP": 5376,
      "FP": 874,
      "FN": 227710,
      "TN": 282642,
      "accuracy": 0.5575239739683547,
      "precision": 0.86016,
      "recall": 0.023064448315214127
    },
    "senderTurns": {
      "N": 221030,
      "TP": 3816,
      "FP": 832,
      "FN": 116296,
      "TN": 100086,
      "accuracy": 0.47008098448174457,
      "precision": 0.8209982788296041,
      "recall": 0.031770347675502866
    },
    "relay": 189308,
    "directTrue": 5415,
    "visible": 1058,
    "receivedOnly": 12194,
    "propagation": {
      "N": 1583,
      "set": 1583,
      "delayMax": 1
    },
    "feeds": 750,
    "queenFeeds": 13,
    "staleFeeds": [
      {
        "key": "bot-hunter:stronghold:A:1",
        "r": 300,
        "id": 184,
        "target": 0,
        "toQueen": true,
        "d": 2,
        "L": 2,
        "slack": 196,
        "kind": "conv",
        "belief": true,
        "enemyAlive": false,
        "queenAlive": true
      }
    ]
  },
  "flip": {
    "games": 8,
    "belief": {
      "N": 64690,
      "TP": 2403,
      "FP": 461,
      "FN": 40224,
      "TN": 21602,
      "accuracy": 0.3710774462822693,
      "precision": 0.839036312849162,
      "recall": 0.05637272151453304
    },
    "rays": {
      "N": 151931,
      "TP": 1039,
      "FP": 68,
      "FN": 89296,
      "TN": 61528,
      "accuracy": 0.4118119409468772,
      "precision": 0.938572719060524,
      "recall": 0.011501632811202745
    },
    "senderTurns": {
      "N": 64115,
      "TP": 526,
      "FP": 41,
      "FN": 41728,
      "TN": 21820,
      "accuracy": 0.34852998518287454,
      "precision": 0.927689594356261,
      "recall": 0.012448525583376722
    },
    "relay": 52668,
    "directTrue": 639,
    "visible": 61,
    "receivedOnly": 2225,
    "propagation": {
      "N": 188,
      "set": 188,
      "delayMax": 1
    },
    "feeds": 188,
    "queenFeeds": 3,
    "staleFeeds": [
      {
        "key": "bot-hunter:trauma_flip:B:1",
        "r": 368,
        "id": 40,
        "target": 0,
        "toQueen": true,
        "d": 2,
        "L": 2,
        "slack": 128,
        "kind": "conv",
        "belief": true,
        "enemyAlive": false,
        "queenAlive": true
      },
      {
        "key": "bot-hunter:trauma_flip:B:1",
        "r": 370,
        "id": 45,
        "target": 0,
        "toQueen": true,
        "d": 2,
        "L": 2,
        "slack": 126,
        "kind": "conv",
        "belief": true,
        "enemyAlive": false,
        "queenAlive": true
      }
    ]
  }
}
```

### self: 믿음

| 분류 | 키 | N | TP | FP | FN | TN | 정확도 | precision | recall |
|---|---|---|---|---|---|---|---|---|---|
| map | big_empty | 34986 | 432 | 929 | 17328 | 16297 | 47.82% | 31.74% | 2.43% |
| map | stronghold | 16575 | 7868 | 0 | 8707 | 0 | 47.47% | 100.00% | 47.47% |
| map | gen_M_07 | 8624 | 18 | 0 | 155 | 8451 | 98.20% | 100.00% | 10.40% |
| map | gen_L_03 | 19860 | 273 | 391 | 14324 | 4872 | 25.91% | 41.11% | 1.87% |
| side | A | 40043 | 4327 | 310 | 21800 | 13606 | 44.78% | 93.31% | 16.56% |
| side | B | 40002 | 4264 | 1010 | 18714 | 16014 | 50.69% | 80.85% | 18.56% |
| opp | bot | 80045 | 8591 | 1320 | 40514 | 29620 | 47.74% | 86.68% | 17.50% |
| period | 0-299 | 44632 | 6619 | 619 | 28933 | 8461 | 33.79% | 91.45% | 18.62% |
| period | 300-429 | 28513 | 1726 | 353 | 11189 | 15245 | 59.52% | 83.02% | 13.36% |
| period | 430+ | 6900 | 246 | 348 | 392 | 5914 | 89.28% | 41.41% | 38.56% |

### self: 송신 차례(네 ray 중복 제거)

| 분류 | 키 | N | TP | FP | FN | TN | 정확도 | precision | recall |
|---|---|---|---|---|---|---|---|---|---|
| map | big_empty | 34732 | 77 | 68 | 17646 | 16941 | 49.00% | 53.10% | 0.43% |
| map | stronghold | 16311 | 1746 | 0 | 14565 | 0 | 10.70% | 100.00% | 10.70% |
| map | gen_M_07 | 8134 | 16 | 0 | 154 | 7964 | 98.11% | 100.00% | 9.41% |
| map | gen_L_03 | 19773 | 118 | 25 | 14456 | 5174 | 26.76% | 82.52% | 0.81% |
| side | A | 39491 | 1254 | 20 | 24705 | 13512 | 37.39% | 98.43% | 4.83% |
| side | B | 39459 | 703 | 73 | 22116 | 16567 | 43.77% | 90.59% | 3.08% |
| opp | bot | 78950 | 1957 | 93 | 46821 | 30079 | 40.58% | 95.46% | 4.01% |
| period | 0-299 | 44182 | 1509 | 48 | 33888 | 8737 | 23.19% | 96.92% | 4.26% |
| period | 300-429 | 28049 | 314 | 24 | 12448 | 15263 | 55.53% | 92.90% | 2.46% |
| period | 430+ | 6719 | 134 | 21 | 485 | 6079 | 92.47% | 86.45% | 21.65% |

원지도·flip ray/송신차례 분리: `summary.json`의 primary/flip. true 목격/relay/채택 원분모:

```json
{
  "primary": {
    "games": 8,
    "belief": {
      "N": 80045,
      "TP": 8591,
      "FP": 1320,
      "FN": 40514,
      "TN": 29620,
      "accuracy": 0.4773689799487788,
      "precision": 0.8668146503884573,
      "recall": 0.17495163425313104
    },
    "rays": {
      "N": 193001,
      "TP": 3337,
      "FP": 231,
      "FN": 93243,
      "TN": 96190,
      "accuracy": 0.5156812659001767,
      "precision": 0.9352578475336323,
      "recall": 0.034551667011803684
    },
    "senderTurns": {
      "N": 78950,
      "TP": 1957,
      "FP": 93,
      "FN": 46821,
      "TN": 30079,
      "accuracy": 0.4057758074730842,
      "precision": 0.9546341463414634,
      "recall": 0.04012054614785354
    },
    "relay": 71168,
    "directTrue": 2438,
    "visible": 467,
    "receivedOnly": 7473,
    "propagation": {
      "N": 1347,
      "set": 1347,
      "delayMax": 1
    },
    "feeds": 310,
    "queenFeeds": 12,
    "staleFeeds": []
  },
  "flip": {
    "games": 0,
    "belief": {
      "N": 0,
      "TP": 0,
      "FP": 0,
      "FN": 0,
      "TN": 0,
      "accuracy": null,
      "precision": null,
      "recall": null
    },
    "rays": {
      "N": 0,
      "TP": 0,
      "FP": 0,
      "FN": 0,
      "TN": 0,
      "accuracy": null,
      "precision": null,
      "recall": null
    },
    "senderTurns": {
      "N": 0,
      "TP": 0,
      "FP": 0,
      "FN": 0,
      "TN": 0,
      "accuracy": null,
      "precision": null,
      "recall": null
    },
    "relay": 0,
    "directTrue": 0,
    "visible": 0,
    "receivedOnly": 0,
    "propagation": {
      "N": 0,
      "set": 0,
      "delayMax": null
    },
    "feeds": 0,
    "queenFeeds": 0,
    "staleFeeds": []
  }
}
```

## 백업 원 길이·한쪽만 생존·crowd·새 함정

```json
{
  "primary/off/b": {
    "N": 36,
    "commonN": 12,
    "keys": [
      "proxy4_king:big_empty:B:1",
      "proxy4_king:stronghold:A:1",
      "proxy4_king:stronghold:B:1",
      "bot-hunter:arena:A:1",
      "bot-hunter:stronghold:A:1",
      "bot-hunter:stronghold:B:1",
      "proxy4_king:trauma:B:1",
      "bot-hunter:trauma:A:1",
      "bot-hunter:trauma:B:1",
      "proxy4_king:australia:B:1",
      "bot-hunter:australia:A:1",
      "proxy4_king:gen_M_07:B:1"
    ],
    "checkpoints": {
      "350": {
        "N": 10,
        "null": 2,
        "medianDelta": 1.0,
        "positive": 6,
        "zero": 2,
        "negative": 2,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 27,
            "on": 28
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 5,
            "on": 6
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 8,
            "on": 5
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 5,
            "on": 12
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 5,
            "on": 6
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 4,
            "on": 4
          },
          {
            "key": "bot-hunter:trauma:B:1",
            "off": 13,
            "on": 16
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 13,
            "on": 11
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 48,
            "on": 54
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          }
        ]
      },
      "400": {
        "N": 10,
        "null": 2,
        "medianDelta": 0.0,
        "positive": 4,
        "zero": 2,
        "negative": 4,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 40,
            "on": 39
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 8,
            "on": 2
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 8,
            "on": 10
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 3,
            "on": 10
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 16,
            "on": 9
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 7,
            "on": 7
          },
          {
            "key": "bot-hunter:trauma:B:1",
            "off": 8,
            "on": 18
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 13,
            "on": 10
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 51,
            "on": 56
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          }
        ]
      },
      "430": {
        "N": 10,
        "null": 2,
        "medianDelta": 2.5,
        "positive": 6,
        "zero": 2,
        "negative": 2,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 44,
            "on": 55
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 2,
            "on": 2
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 9,
            "on": 11
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 3,
            "on": 18
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 23,
            "on": 6
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 10,
            "on": 13
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 7,
            "on": 7
          },
          {
            "key": "bot-hunter:trauma:B:1",
            "off": 14,
            "on": 18
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 16,
            "on": 10
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 52,
            "on": 56
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          }
        ]
      }
    },
    "oneSidedAlive": [
      {
        "key": "bot-hunter:australia:B:1",
        "off": {
          "r": 256,
          "cause": "trap",
          "block": "a"
        },
        "on": null
      },
      {
        "key": "proxy4_king:gen_L_03:A:1",
        "off": null,
        "on": {
          "r": 242,
          "cause": "rammed",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:gen_L_03:A:1",
        "off": null,
        "on": {
          "r": 371,
          "cause": "sac",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:gen_L_03:B:1",
        "off": null,
        "on": {
          "r": 414,
          "cause": "rammed",
          "block": "-"
        }
      }
    ],
    "crowd": {
      "340": {
        "off": {
          "N": 117,
          "median": 0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 117,
          "median": 0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 102,
        "increased": 4,
        "decreased": 3,
        "increaseKeys": [
          "bot-hunter:stronghold:B:1",
          "proxy4_king:big_empty:B:1",
          "proxy4_king:stronghold:A:1",
          "proxy4_king:trauma:B:1"
        ]
      },
      "430": {
        "off": {
          "N": 78,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 66,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 60,
        "increased": 1,
        "decreased": 0,
        "increaseKeys": [
          "bot-hunter:stronghold:A:1"
        ]
      }
    },
    "newTraps": [],
    "queenDeaths": [
      {
        "key": "bot-hunter:big_empty:A:1",
        "off": {
          "r": 258,
          "cause": "rammed",
          "block": "-"
        },
        "on": {
          "r": 391,
          "cause": "rammed",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:australia:B:1",
        "off": {
          "r": 256,
          "cause": "trap",
          "block": "a"
        },
        "on": null
      },
      {
        "key": "proxy4_king:gen_L_03:A:1",
        "off": null,
        "on": {
          "r": 242,
          "cause": "rammed",
          "block": "-"
        }
      },
      {
        "key": "proxy4_king:gen_L_03:B:1",
        "off": {
          "r": 336,
          "cause": "sac",
          "block": "-"
        },
        "on": {
          "r": 237,
          "cause": "sac",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:gen_L_03:A:1",
        "off": null,
        "on": {
          "r": 371,
          "cause": "sac",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:gen_L_03:B:1",
        "off": null,
        "on": {
          "r": 414,
          "cause": "rammed",
          "block": "-"
        }
      }
    ]
  },
  "primary/off/c": {
    "N": 36,
    "commonN": 14,
    "keys": [
      "proxy4_king:big_empty:B:1",
      "proxy4_king:stronghold:A:1",
      "proxy4_king:stronghold:B:1",
      "bot-hunter:arena:A:1",
      "bot-hunter:stronghold:A:1",
      "bot-hunter:stronghold:B:1",
      "proxy4_king:trauma:B:1",
      "bot-hunter:trauma:A:1",
      "bot-hunter:trauma:B:1",
      "proxy4_king:australia:B:1",
      "bot-hunter:australia:A:1",
      "proxy4_king:gen_M_07:B:1",
      "proxy4_king:gen_L_03:A:1",
      "bot-hunter:gen_L_03:B:1"
    ],
    "checkpoints": {
      "350": {
        "N": 12,
        "null": 2,
        "medianDelta": 0.0,
        "positive": 5,
        "zero": 5,
        "negative": 2,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 27,
            "on": 30
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 5,
            "on": 7
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 8,
            "on": 13
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 5,
            "on": 6
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 5,
            "on": 5
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 4,
            "on": 4
          },
          {
            "key": "bot-hunter:trauma:B:1",
            "off": 13,
            "on": 11
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 13,
            "on": 13
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 48,
            "on": 47
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          },
          {
            "key": "proxy4_king:gen_L_03:A:1",
            "off": 3,
            "on": 3
          },
          {
            "key": "bot-hunter:gen_L_03:B:1",
            "off": 9,
            "on": 12
          }
        ]
      },
      "400": {
        "N": 12,
        "null": 2,
        "medianDelta": 3.0,
        "positive": 8,
        "zero": 1,
        "negative": 3,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 40,
            "on": 46
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 8,
            "on": 6
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 8,
            "on": 32
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 3,
            "on": 13
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 16,
            "on": 6
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 10,
            "on": 11
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 7,
            "on": 5
          },
          {
            "key": "bot-hunter:trauma:B:1",
            "off": 8,
            "on": 17
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 13,
            "on": 15
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 51,
            "on": 55
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          },
          {
            "key": "proxy4_king:gen_L_03:A:1",
            "off": 3,
            "on": 3
          },
          {
            "key": "bot-hunter:gen_L_03:B:1",
            "off": 8,
            "on": 14
          }
        ]
      },
      "430": {
        "N": 12,
        "null": 2,
        "medianDelta": 7.0,
        "positive": 9,
        "zero": 1,
        "negative": 2,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 44,
            "on": 69
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 2,
            "on": 11
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 9,
            "on": 36
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 3,
            "on": 16
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 23,
            "on": 9
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 10,
            "on": 14
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 7,
            "on": 5
          },
          {
            "key": "bot-hunter:trauma:B:1",
            "off": 14,
            "on": 21
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 16,
            "on": 21
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 52,
            "on": 59
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          },
          {
            "key": "proxy4_king:gen_L_03:A:1",
            "off": 3,
            "on": 3
          },
          {
            "key": "bot-hunter:gen_L_03:B:1",
            "off": 8,
            "on": 17
          }
        ]
      }
    },
    "oneSidedAlive": [
      {
        "key": "bot-hunter:gen_L_03:A:1",
        "off": null,
        "on": {
          "r": 354,
          "cause": "rammed",
          "block": "-"
        }
      }
    ],
    "crowd": {
      "340": {
        "off": {
          "N": 117,
          "median": 0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 110,
          "median": 0.0,
          "ge2": 1,
          "share": 0.00909090909090909
        },
        "matchedN": 110,
        "increased": 8,
        "decreased": 3,
        "increaseKeys": [
          "bot-hunter:australia:A:1",
          "bot-hunter:gen_L_03:B:1",
          "bot-hunter:stronghold:A:1",
          "bot-hunter:stronghold:B:1",
          "proxy4_king:big_empty:B:1"
        ]
      },
      "430": {
        "off": {
          "N": 78,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 71,
          "median": 0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 71,
        "increased": 5,
        "decreased": 0,
        "increaseKeys": [
          "bot-hunter:stronghold:A:1",
          "proxy4_king:australia:B:1",
          "proxy4_king:big_empty:B:1"
        ]
      }
    },
    "newTraps": [],
    "queenDeaths": [
      {
        "key": "proxy4_king:stronghold:B:1",
        "off": null,
        "on": {
          "r": 476,
          "cause": "rammed",
          "block": "-"
        }
      },
      {
        "key": "proxy4_king:gen_L_03:B:1",
        "off": {
          "r": 336,
          "cause": "sac",
          "block": "-"
        },
        "on": {
          "r": 307,
          "cause": "rammed",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:gen_L_03:A:1",
        "off": null,
        "on": {
          "r": 354,
          "cause": "rammed",
          "block": "-"
        }
      }
    ]
  },
  "primary/b/on": {
    "N": 36,
    "commonN": 12,
    "keys": [
      "proxy4_king:big_empty:B:1",
      "proxy4_king:stronghold:A:1",
      "proxy4_king:stronghold:B:1",
      "bot-hunter:arena:A:1",
      "bot-hunter:stronghold:A:1",
      "bot-hunter:stronghold:B:1",
      "proxy4_king:trauma:B:1",
      "bot-hunter:trauma:A:1",
      "proxy4_king:australia:B:1",
      "bot-hunter:australia:A:1",
      "bot-hunter:australia:B:1",
      "proxy4_king:gen_M_07:B:1"
    ],
    "checkpoints": {
      "350": {
        "N": 10,
        "null": 2,
        "medianDelta": 0.0,
        "positive": 4,
        "zero": 3,
        "negative": 3,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 28,
            "on": 27
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 6,
            "on": 6
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 5,
            "on": 13
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 12,
            "on": 9
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 6,
            "on": 15
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 4,
            "on": 4
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 11,
            "on": 13
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 54,
            "on": 49
          },
          {
            "key": "bot-hunter:australia:B:1",
            "off": 27,
            "on": 28
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          }
        ]
      },
      "400": {
        "N": 10,
        "null": 2,
        "medianDelta": 4.0,
        "positive": 7,
        "zero": 2,
        "negative": 1,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 39,
            "on": 32
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 2,
            "on": 6
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 10,
            "on": 28
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 10,
            "on": 14
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 9,
            "on": 37
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 7,
            "on": 7
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 10,
            "on": 13
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 56,
            "on": 61
          },
          {
            "key": "bot-hunter:australia:B:1",
            "off": 43,
            "on": 47
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          }
        ]
      },
      "430": {
        "N": 10,
        "null": 2,
        "medianDelta": 1.5,
        "positive": 5,
        "zero": 2,
        "negative": 3,
        "raw": [
          {
            "key": "proxy4_king:big_empty:B:1",
            "off": 55,
            "on": 43
          },
          {
            "key": "proxy4_king:stronghold:A:1",
            "off": 2,
            "on": 6
          },
          {
            "key": "proxy4_king:stronghold:B:1",
            "off": 11,
            "on": 40
          },
          {
            "key": "bot-hunter:arena:A:1",
            "off": null,
            "on": null
          },
          {
            "key": "bot-hunter:stronghold:A:1",
            "off": 18,
            "on": 16
          },
          {
            "key": "bot-hunter:stronghold:B:1",
            "off": 6,
            "on": 51
          },
          {
            "key": "proxy4_king:trauma:B:1",
            "off": 13,
            "on": 13
          },
          {
            "key": "bot-hunter:trauma:A:1",
            "off": 7,
            "on": 7
          },
          {
            "key": "proxy4_king:australia:B:1",
            "off": 10,
            "on": 13
          },
          {
            "key": "bot-hunter:australia:A:1",
            "off": 56,
            "on": 64
          },
          {
            "key": "bot-hunter:australia:B:1",
            "off": 54,
            "on": 49
          },
          {
            "key": "proxy4_king:gen_M_07:B:1",
            "off": null,
            "on": null
          }
        ]
      }
    },
    "oneSidedAlive": [
      {
        "key": "bot-hunter:trauma:B:1",
        "off": null,
        "on": {
          "r": 338,
          "cause": "allyHead",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:gen_L_03:B:1",
        "off": {
          "r": 414,
          "cause": "rammed",
          "block": "-"
        },
        "on": null
      }
    ],
    "crowd": {
      "340": {
        "off": {
          "N": 117,
          "median": 0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 105,
          "median": 0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 104,
        "increased": 10,
        "decreased": 3,
        "increaseKeys": [
          "bot-hunter:australia:B:1",
          "proxy4_king:australia:B:1",
          "proxy4_king:stronghold:A:1",
          "proxy4_king:stronghold:B:1",
          "proxy4_king:trauma:B:1"
        ]
      },
      "430": {
        "off": {
          "N": 66,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 65,
          "median": 0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 59,
        "increased": 3,
        "decreased": 1,
        "increaseKeys": [
          "proxy4_king:stronghold:B:1",
          "proxy4_king:trauma:B:1"
        ]
      }
    },
    "newTraps": [
      {
        "key": "bot-hunter:stronghold:B:1",
        "r": 496,
        "cause": "trap",
        "block": "a",
        "indicator": {
          "r": 496,
          "text": "no-exit qc0,-1000,135,0 E=F"
        }
      }
    ],
    "queenDeaths": [
      {
        "key": "bot-hunter:big_empty:A:1",
        "off": {
          "r": 391,
          "cause": "rammed",
          "block": "-"
        },
        "on": {
          "r": 364,
          "cause": "rammed",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:stronghold:B:1",
        "off": null,
        "on": {
          "r": 496,
          "cause": "trap",
          "block": "a"
        }
      },
      {
        "key": "bot-hunter:trauma:B:1",
        "off": null,
        "on": {
          "r": 338,
          "cause": "allyHead",
          "block": "-"
        }
      },
      {
        "key": "proxy4_king:australia:B:1",
        "off": null,
        "on": {
          "r": 478,
          "cause": "rammed",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:gen_L_03:A:1",
        "off": {
          "r": 371,
          "cause": "sac",
          "block": "-"
        },
        "on": {
          "r": 364,
          "cause": "sac",
          "block": "-"
        }
      },
      {
        "key": "bot-hunter:gen_L_03:B:1",
        "off": {
          "r": 414,
          "cause": "rammed",
          "block": "-"
        },
        "on": null
      }
    ]
  },
  "flip/off/b": {
    "N": 8,
    "commonN": 6,
    "keys": [
      "proxy4_king:trauma_flip:A:1",
      "proxy4_king:australia_flip:A:1",
      "bot-hunter:trauma_flip:A:1",
      "bot-hunter:trauma_flip:B:1",
      "bot-hunter:australia_flip:A:1",
      "bot-hunter:australia_flip:B:1"
    ],
    "checkpoints": {
      "350": {
        "N": 6,
        "null": 0,
        "medianDelta": -1.5,
        "positive": 0,
        "zero": 1,
        "negative": 5,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 13,
            "on": 11
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 4,
            "on": 3
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 4,
            "on": 3
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 22,
            "on": 20
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 26,
            "on": 24
          }
        ]
      },
      "400": {
        "N": 6,
        "null": 0,
        "medianDelta": -0.5,
        "positive": 2,
        "zero": 1,
        "negative": 3,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 13,
            "on": 10
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 7,
            "on": 6
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 4,
            "on": 7
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 27,
            "on": 34
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 39,
            "on": 38
          }
        ]
      },
      "430": {
        "N": 6,
        "null": 0,
        "medianDelta": 0.0,
        "positive": 3,
        "zero": 0,
        "negative": 3,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 10,
            "on": 13
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 16,
            "on": 10
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 10,
            "on": 7
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 4,
            "on": 7
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 37,
            "on": 46
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 46,
            "on": 43
          }
        ]
      }
    },
    "oneSidedAlive": [],
    "crowd": {
      "340": {
        "off": {
          "N": 54,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 54,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 54,
        "increased": 1,
        "decreased": 0,
        "increaseKeys": [
          "proxy4_king:trauma_flip:A:1"
        ]
      },
      "430": {
        "off": {
          "N": 36,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 36,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 36,
        "increased": 0,
        "decreased": 0,
        "increaseKeys": []
      }
    },
    "newTraps": [],
    "queenDeaths": []
  },
  "flip/off/c": {
    "N": 8,
    "commonN": 6,
    "keys": [
      "proxy4_king:trauma_flip:A:1",
      "proxy4_king:australia_flip:A:1",
      "bot-hunter:trauma_flip:A:1",
      "bot-hunter:trauma_flip:B:1",
      "bot-hunter:australia_flip:A:1",
      "bot-hunter:australia_flip:B:1"
    ],
    "checkpoints": {
      "350": {
        "N": 6,
        "null": 0,
        "medianDelta": 0.0,
        "positive": 1,
        "zero": 4,
        "negative": 1,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 13,
            "on": 13
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 4,
            "on": 4
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 4,
            "on": 4
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 22,
            "on": 30
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 26,
            "on": 25
          }
        ]
      },
      "400": {
        "N": 6,
        "null": 0,
        "medianDelta": 2.0,
        "positive": 6,
        "zero": 0,
        "negative": 0,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 10,
            "on": 11
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 13,
            "on": 15
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 7,
            "on": 8
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 4,
            "on": 6
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 27,
            "on": 56
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 39,
            "on": 41
          }
        ]
      },
      "430": {
        "N": 6,
        "null": 0,
        "medianDelta": 3.5,
        "positive": 4,
        "zero": 1,
        "negative": 1,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 10,
            "on": 14
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 16,
            "on": 21
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 10,
            "on": 13
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 4,
            "on": 4
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 37,
            "on": 62
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 46,
            "on": 44
          }
        ]
      }
    },
    "oneSidedAlive": [],
    "crowd": {
      "340": {
        "off": {
          "N": 54,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 54,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 54,
        "increased": 1,
        "decreased": 0,
        "increaseKeys": [
          "bot-hunter:australia_flip:B:1"
        ]
      },
      "430": {
        "off": {
          "N": 36,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 36,
          "median": 0.0,
          "ge2": 1,
          "share": 0.027777777777777776
        },
        "matchedN": 36,
        "increased": 4,
        "decreased": 0,
        "increaseKeys": [
          "bot-hunter:australia_flip:A:1",
          "bot-hunter:australia_flip:B:1",
          "proxy4_king:australia_flip:A:1"
        ]
      }
    },
    "newTraps": [],
    "queenDeaths": []
  },
  "flip/b/on": {
    "N": 8,
    "commonN": 6,
    "keys": [
      "proxy4_king:trauma_flip:A:1",
      "proxy4_king:australia_flip:A:1",
      "bot-hunter:trauma_flip:A:1",
      "bot-hunter:trauma_flip:B:1",
      "bot-hunter:australia_flip:A:1",
      "bot-hunter:australia_flip:B:1"
    ],
    "checkpoints": {
      "350": {
        "N": 6,
        "null": 0,
        "medianDelta": 0.5,
        "positive": 3,
        "zero": 3,
        "negative": 0,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 11,
            "on": 13
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 3,
            "on": 3
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 3,
            "on": 4
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 20,
            "on": 22
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 24,
            "on": 24
          }
        ]
      },
      "400": {
        "N": 6,
        "null": 0,
        "medianDelta": 0.0,
        "positive": 2,
        "zero": 2,
        "negative": 2,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 10,
            "on": 10
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 10,
            "on": 13
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 6,
            "on": 6
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 7,
            "on": 6
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 34,
            "on": 35
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 38,
            "on": 33
          }
        ]
      },
      "430": {
        "N": 6,
        "null": 0,
        "medianDelta": 0.0,
        "positive": 2,
        "zero": 2,
        "negative": 2,
        "raw": [
          {
            "key": "proxy4_king:trauma_flip:A:1",
            "off": 13,
            "on": 13
          },
          {
            "key": "proxy4_king:australia_flip:A:1",
            "off": 10,
            "on": 13
          },
          {
            "key": "bot-hunter:trauma_flip:A:1",
            "off": 7,
            "on": 6
          },
          {
            "key": "bot-hunter:trauma_flip:B:1",
            "off": 7,
            "on": 8
          },
          {
            "key": "bot-hunter:australia_flip:A:1",
            "off": 46,
            "on": 46
          },
          {
            "key": "bot-hunter:australia_flip:B:1",
            "off": 43,
            "on": 38
          }
        ]
      }
    },
    "oneSidedAlive": [],
    "crowd": {
      "340": {
        "off": {
          "N": 54,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 54,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 54,
        "increased": 4,
        "decreased": 1,
        "increaseKeys": [
          "bot-hunter:australia_flip:B:1",
          "proxy4_king:australia_flip:A:1",
          "proxy4_king:trauma_flip:A:1"
        ]
      },
      "430": {
        "off": {
          "N": 36,
          "median": 0.0,
          "ge2": 0,
          "share": 0.0
        },
        "on": {
          "N": 35,
          "median": 0,
          "ge2": 0,
          "share": 0.0
        },
        "matchedN": 35,
        "increased": 3,
        "decreased": 0,
        "increaseKeys": [
          "bot-hunter:trauma_flip:A:1",
          "proxy4_king:trauma_flip:A:1"
        ]
      }
    },
    "newTraps": [],
    "queenDeaths": [
      {
        "key": "proxy4_king:australia_flip:A:1",
        "off": null,
        "on": {
          "r": 478,
          "cause": "rammed",
          "block": "-"
        }
      }
    ]
  }
}
```

## 소나/표식 제외 최초 물리 행동 차이(양 팀 dragonAction)

```json
[
  {
    "key": "proxy4_king:arena:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:arena:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:arena:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:arena:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:arena:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:arena:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:arena:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:arena:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:arena:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:arena:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:arena:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:arena:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:big_empty:A:1",
    "comparison": "off/b",
    "first": {
      "index": 1767,
      "off": {
        "r": 65,
        "id": 46,
        "action": {
          "kind": "move",
          "steps": [
            "E",
            "N"
          ]
        }
      },
      "on": {
        "r": 65,
        "id": 46,
        "action": {
          "kind": "move",
          "steps": [
            "E",
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:big_empty:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:big_empty:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:big_empty:B:1",
    "comparison": "off/b",
    "first": {
      "index": 27057,
      "off": {
        "r": 300,
        "id": 116,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 116,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:big_empty:B:1",
    "comparison": "off/c",
    "first": {
      "index": 28122,
      "off": {
        "r": 310,
        "id": 137,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 310,
        "id": 137,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:big_empty:B:1",
    "comparison": "b/on",
    "first": {
      "index": 28122,
      "off": {
        "r": 310,
        "id": 137,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 310,
        "id": 137,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:big_empty:A:1",
    "comparison": "off/b",
    "first": {
      "index": 3318,
      "off": {
        "r": 93,
        "id": 78,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 93,
        "id": 78,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:big_empty:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:big_empty:A:1",
    "comparison": "b/on",
    "first": {
      "index": 25464,
      "off": {
        "r": 352,
        "id": 159,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      },
      "on": {
        "r": 352,
        "id": 159,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:big_empty:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:big_empty:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:big_empty:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:Colosseum:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:Colosseum:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:Colosseum:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:Colosseum:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:Colosseum:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:Colosseum:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:Colosseum:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:Colosseum:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:Colosseum:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:Colosseum:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:Colosseum:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:Colosseum:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:default_small:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:default_small:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:default_small:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:default_small:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:default_small:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:default_small:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:default_small:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:default_small:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:default_small:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:default_small:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:default_small:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:default_small:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:stronghold:A:1",
    "comparison": "off/b",
    "first": {
      "index": 13057,
      "off": {
        "r": 302,
        "id": 142,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 302,
        "id": 142,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:stronghold:A:1",
    "comparison": "off/c",
    "first": {
      "index": 12889,
      "off": {
        "r": 300,
        "id": 77,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 77,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:stronghold:A:1",
    "comparison": "b/on",
    "first": {
      "index": 12889,
      "off": {
        "r": 300,
        "id": 77,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 77,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:stronghold:B:1",
    "comparison": "off/b",
    "first": {
      "index": 13203,
      "off": {
        "r": 300,
        "id": 218,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 218,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:stronghold:B:1",
    "comparison": "off/c",
    "first": {
      "index": 13378,
      "off": {
        "r": 303,
        "id": 172,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 303,
        "id": 172,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:stronghold:B:1",
    "comparison": "b/on",
    "first": {
      "index": 13253,
      "off": {
        "r": 301,
        "id": 190,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 190,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:stronghold:A:1",
    "comparison": "off/b",
    "first": {
      "index": 11095,
      "off": {
        "r": 300,
        "id": 108,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 108,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:stronghold:A:1",
    "comparison": "off/c",
    "first": {
      "index": 11320,
      "off": {
        "r": 304,
        "id": 175,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 304,
        "id": 175,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:stronghold:A:1",
    "comparison": "b/on",
    "first": {
      "index": 11555,
      "off": {
        "r": 309,
        "id": 43,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 309,
        "id": 43,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:stronghold:B:1",
    "comparison": "off/b",
    "first": {
      "index": 10924,
      "off": {
        "r": 301,
        "id": 15,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 15,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:stronghold:B:1",
    "comparison": "off/c",
    "first": {
      "index": 11983,
      "off": {
        "r": 320,
        "id": 200,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 320,
        "id": 200,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:stronghold:B:1",
    "comparison": "b/on",
    "first": {
      "index": 12212,
      "off": {
        "r": 324,
        "id": 203,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      },
      "on": {
        "r": 324,
        "id": 203,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:trauma:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:trauma:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:trauma:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:trauma:B:1",
    "comparison": "off/b",
    "first": {
      "index": 9766,
      "off": {
        "r": 306,
        "id": 3,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 306,
        "id": 3,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:trauma:B:1",
    "comparison": "off/c",
    "first": {
      "index": 10360,
      "off": {
        "r": 318,
        "id": 132,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 318,
        "id": 132,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:trauma:B:1",
    "comparison": "b/on",
    "first": {
      "index": 11077,
      "off": {
        "r": 333,
        "id": 132,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 333,
        "id": 132,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma:A:1",
    "comparison": "off/b",
    "first": {
      "index": 4465,
      "off": {
        "r": 300,
        "id": 6,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 6,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma:A:1",
    "comparison": "off/c",
    "first": {
      "index": 4795,
      "off": {
        "r": 310,
        "id": 55,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 310,
        "id": 55,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:trauma:B:1",
    "comparison": "off/b",
    "first": {
      "index": 4769,
      "off": {
        "r": 306,
        "id": 3,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 306,
        "id": 3,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma:B:1",
    "comparison": "off/c",
    "first": {
      "index": 4694,
      "off": {
        "r": 303,
        "id": 63,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 303,
        "id": 63,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma:B:1",
    "comparison": "b/on",
    "first": {
      "index": 5495,
      "off": {
        "r": 326,
        "id": 50,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 326,
        "id": 50,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:australia:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:australia:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:australia:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:australia:B:1",
    "comparison": "off/b",
    "first": {
      "index": 19012,
      "off": {
        "r": 301,
        "id": 256,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 256,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:australia:B:1",
    "comparison": "off/c",
    "first": {
      "index": 18933,
      "off": {
        "r": 301,
        "id": 61,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 61,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:australia:B:1",
    "comparison": "b/on",
    "first": {
      "index": 18933,
      "off": {
        "r": 301,
        "id": 61,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 61,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia:A:1",
    "comparison": "off/b",
    "first": {
      "index": 15121,
      "off": {
        "r": 300,
        "id": 75,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 75,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia:A:1",
    "comparison": "off/c",
    "first": {
      "index": 15340,
      "off": {
        "r": 303,
        "id": 29,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 303,
        "id": 29,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia:A:1",
    "comparison": "b/on",
    "first": {
      "index": 15245,
      "off": {
        "r": 302,
        "id": 2,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 302,
        "id": 2,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia:B:1",
    "comparison": "off/b",
    "first": {
      "index": 6388,
      "off": {
        "r": 181,
        "id": 3,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 181,
        "id": 3,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:australia:B:1",
    "comparison": "b/on",
    "first": {
      "index": 16035,
      "off": {
        "r": 301,
        "id": 21,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 21,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:gen_M_07:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:gen_M_07:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:gen_M_07:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:gen_M_07:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:gen_M_07:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:gen_M_07:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:gen_M_07:A:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:gen_M_07:A:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:gen_M_07:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:gen_M_07:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "bot-hunter:gen_M_07:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "bot-hunter:gen_M_07:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:gen_L_03:A:1",
    "comparison": "off/b",
    "first": {
      "index": 2660,
      "off": {
        "r": 192,
        "id": 5,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 192,
        "id": 5,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:gen_L_03:A:1",
    "comparison": "off/c",
    "first": {
      "index": 20549,
      "off": {
        "r": 452,
        "id": 16,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 452,
        "id": 16,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:gen_L_03:A:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "proxy4_king:gen_L_03:B:1",
    "comparison": "off/b",
    "first": {
      "index": 2815,
      "off": {
        "r": 194,
        "id": 22,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      },
      "on": {
        "r": 194,
        "id": 22,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:gen_L_03:B:1",
    "comparison": "off/c",
    "first": {
      "index": 3366,
      "off": {
        "r": 209,
        "id": 22,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 209,
        "id": 22,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:gen_L_03:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:gen_L_03:A:1",
    "comparison": "off/b",
    "first": {
      "index": 7030,
      "off": {
        "r": 300,
        "id": 66,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 66,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:gen_L_03:A:1",
    "comparison": "off/c",
    "first": {
      "index": 7030,
      "off": {
        "r": 300,
        "id": 66,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 66,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:gen_L_03:A:1",
    "comparison": "b/on",
    "first": {
      "index": 8759,
      "off": {
        "r": 323,
        "id": 36,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 323,
        "id": 36,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:gen_L_03:B:1",
    "comparison": "off/b",
    "first": {
      "index": 6836,
      "off": {
        "r": 297,
        "id": 7,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 297,
        "id": 7,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:gen_L_03:B:1",
    "comparison": "off/c",
    "first": {
      "index": 7209,
      "off": {
        "r": 302,
        "id": 7,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 302,
        "id": 7,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:gen_L_03:B:1",
    "comparison": "b/on",
    "first": {
      "index": 7233,
      "off": {
        "r": 302,
        "id": 32,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      },
      "on": {
        "r": 302,
        "id": 32,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:trauma_flip:A:1",
    "comparison": "off/b",
    "first": {
      "index": 9766,
      "off": {
        "r": 306,
        "id": 3,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 306,
        "id": 3,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:trauma_flip:A:1",
    "comparison": "off/c",
    "first": {
      "index": 10360,
      "off": {
        "r": 318,
        "id": 132,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 318,
        "id": 132,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:trauma_flip:A:1",
    "comparison": "b/on",
    "first": {
      "index": 11077,
      "off": {
        "r": 333,
        "id": 132,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 333,
        "id": 132,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:trauma_flip:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:trauma_flip:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:trauma_flip:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:trauma_flip:A:1",
    "comparison": "off/b",
    "first": {
      "index": 5503,
      "off": {
        "r": 302,
        "id": 27,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 302,
        "id": 27,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma_flip:A:1",
    "comparison": "off/c",
    "first": {
      "index": 5712,
      "off": {
        "r": 307,
        "id": 59,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 307,
        "id": 59,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma_flip:A:1",
    "comparison": "b/on",
    "first": {
      "index": 6575,
      "off": {
        "r": 331,
        "id": 36,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 331,
        "id": 36,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma_flip:B:1",
    "comparison": "off/b",
    "first": {
      "index": 5092,
      "off": {
        "r": 301,
        "id": 2,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 2,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma_flip:B:1",
    "comparison": "off/c",
    "first": {
      "index": 6364,
      "off": {
        "r": 344,
        "id": 34,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      },
      "on": {
        "r": 344,
        "id": 34,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:trauma_flip:B:1",
    "comparison": "b/on",
    "first": {
      "index": 5879,
      "off": {
        "r": 328,
        "id": 40,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 328,
        "id": 40,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:australia_flip:A:1",
    "comparison": "off/b",
    "first": {
      "index": 19012,
      "off": {
        "r": 301,
        "id": 256,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 256,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:australia_flip:A:1",
    "comparison": "off/c",
    "first": {
      "index": 18933,
      "off": {
        "r": 301,
        "id": 61,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 61,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:australia_flip:A:1",
    "comparison": "b/on",
    "first": {
      "index": 18933,
      "off": {
        "r": 301,
        "id": 61,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 301,
        "id": 61,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "proxy4_king:australia_flip:B:1",
    "comparison": "off/b",
    "first": null
  },
  {
    "key": "proxy4_king:australia_flip:B:1",
    "comparison": "off/c",
    "first": null
  },
  {
    "key": "proxy4_king:australia_flip:B:1",
    "comparison": "b/on",
    "first": null
  },
  {
    "key": "bot-hunter:australia_flip:A:1",
    "comparison": "off/b",
    "first": {
      "index": 11136,
      "off": {
        "r": 233,
        "id": 75,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 233,
        "id": 75,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia_flip:A:1",
    "comparison": "off/c",
    "first": {
      "index": 16673,
      "off": {
        "r": 300,
        "id": 9,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 300,
        "id": 9,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia_flip:A:1",
    "comparison": "b/on",
    "first": {
      "index": 17066,
      "off": {
        "r": 305,
        "id": 9,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      },
      "on": {
        "r": 305,
        "id": 9,
        "action": {
          "kind": "move",
          "steps": [
            "W"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia_flip:B:1",
    "comparison": "off/b",
    "first": {
      "index": 17409,
      "off": {
        "r": 303,
        "id": 143,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 303,
        "id": 143,
        "action": {
          "kind": "move",
          "steps": [
            "S"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia_flip:B:1",
    "comparison": "off/c",
    "first": {
      "index": 17409,
      "off": {
        "r": 303,
        "id": 143,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      },
      "on": {
        "r": 303,
        "id": 143,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      }
    }
  },
  {
    "key": "bot-hunter:australia_flip:B:1",
    "comparison": "b/on",
    "first": {
      "index": 20145,
      "off": {
        "r": 337,
        "id": 26,
        "action": {
          "kind": "move",
          "steps": [
            "E"
          ]
        }
      },
      "on": {
        "r": 337,
        "id": 26,
        "action": {
          "kind": "move",
          "steps": [
            "N"
          ]
        }
      }
    }
  }
]
```

## 사망 뒤 최장·먹이 대상 대조

우리 여왕이 양쪽 모두 죽은 off/c 및 b/on 공통 47짝의 원 길이(r350/400/430)·사망시각·후속 모든 먹이 대상은 `dead-queen-backup.json`이다. 종료 checkpoint를 0으로 채우지 않았다. 해당 자료는 최장 경로 보존의 행동 대조이고 길이·승패 채택 게이트가 아니다. stale feed 5표식의 4개 고유 판면(c/on stronghold r300은 같은 물리 상태)은 `stale-boards.txt`다.
