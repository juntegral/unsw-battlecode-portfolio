## 20. BODYMEM ANALYSIS 결과 (2026-10-02 11:25:53 KST; 기존 기보만)

§19·`exp/bodymem/ANALYZE.md`를 따랐다. 모든 replay 도구에 `UNSW_RULES=123`을 주었다. 새 게임·봇/params 수정·커밋·네트워크0. **제안은 OFF:** 목적은 개선됐으나 같은 입력 변경 결정의 production 재현·후속3차례 안전이 미확인이다. 갈라진 게임의 사망·여왕 수명은 게이트로 쓰지 않았다.

| 사전 기준 | 값 | N | 판정 |
|---|---|---|---|
| 자료 완전성 | 192/192, 누락0·실패이력0, ON/OFF84짝·동일성12짝 | 192판 | PASS |
| 1 양 arm 공통 표식·시작 drift 감소 | OFF121/3504(3.45%) → ON94/3249(2.89%); 전체 시도 시작 drift121/3638 →94/3355 | OFF3504/ON3249 완주; OFF3638/ON3355 시도 | PASS |
| 1 표식 분모·누락 공개 | 완주 predicted OFF3504/ON3249, 누락0/0; 전체 predicted3513/3253·누락125/102(전부 사망 TRADE) | OFF3638/ON3355 시도 | PASS(완주 누락0; 표식 밖 시도 별도) |
| 1 잔존 입력/끝 예측 분리 | 시작121→94, 끝104→81, 합집합122→95; 시작은 맞고 끝만 틀림1→1; unknown33→28(슬롯375→194), 미관측 경로14→16 | OFF3504/ON3249 완주 | PASS(분리 보고; 불확실 건 성공으로 미산입) |
| 1 완전 추적 시작·다음 관측 배열0 | 동일 ON 이력: World OFF2536/ON0; 동일 OFF 이력: OFF1931/ON0 | ON 이력483636, OFF 이력475849 완전 추적 차례 | PASS |
| 1 초기 긴 몸/부분 관측 별도 | 초기 미관측 몸 OFF3327/ON3515 프로세스; 모든 차례 배열 drift: ON 이력 OFF12318/ON9775, OFF 이력 OFF10207/ON8275 | OFF490962/ON500228 차례 | PASS(한계 공개; 전체 drift0 주장 안 함) |
| 1 실제 World 배열·production 표식 대조 | 완주 다중 시작 불일치 ON94/OFF121건 전부 배열 해시와 일치; 불일치 집합 차이0 | 215 drift 차례; 양 arm6753 완주 | PASS |
| 1 BODYX 전이/독립123 oracle/매 걸음 update | oracleDrift0·stepDrift0·update 누락0, ledger 10항 전부0 | 7659 완주(동일성 포함); 192판 | PASS |
| 2 World/Planner 합성·가격·direct 보고 | resync drift OFF1802/ON0; 지급2453/2453·가격 변경0·아군4/4 | 양 arm 각2448 기억·2453 지급·4 아군 입력 | PASS |
| 2 기존 #14 r188 같은 입력 거절 | OFF NW의 두 번째 걸음 A 사망; ON N 즉시 생존·bodymemr3; OFF147/147 기록 선택 재현 | 기존 실패1 입력; 강제 과거147차례 | PASS(즉시 기제; 후속 안전으로 미산입) |
| 2 무료/유료/진주/포털/LENGTH/분열 판면 | L8 EE 무료2 L8 유지; L14 WSS 무료3 L14 유지; L3 WW 진주2·유료1 L4; 포털 미관측 성장 후 LENGTH 복원; split 부모/다음 입력 대조 | 4 지도군 모두, 168판; ON9561/OFF9224 split | PASS(실제 배열·사례 아래) |
| 2 실제 아군 direct 보고 전수 | ON 길이 과소528/과대0·머리 오차820, OFF1838/0·741; 직접 관측 경로 오류 OFF1385/ON0. ON 잔존 오차는 모두 미관측 경로 | ON399701/OFF391644 direct 보고 | PASS(관측 구간); 미관측 보고 한계 잔존 |
| 2 지급 실패/sprintDeath0 | OFF A/sprintDeath/oversprint1 → ON0; 다중 자기 몸 사망 양쪽0 | OFF3638/ON3355 다중 시도 | PASS |
| 2/4 오류·timeout·no reply0 | 이력 오류0·raw 오류 이벤트0·우리 turn/action 차이0·timeout0 | 192판; ON500228/OFF490962 차례 | PASS |
| 3 동일 입력 production 상태·judge 선택 재현 | native source 선택464/464 재현, 변경 후보11의 new 즉시 생존11·old 사망1; judge-clock/과거 Planner 상태 재현0, 공식 변경 결정 전수 미열거 | 선택 진단3 source/id·464차례·11 후보; 공식 검증0 | FAIL(미확인) |
| 3 이후3차례 fork·새 선택 유발 여왕/용 사망0 | future fate/외생 행동·spawn RNG 복원 검증0; 새 선택만 사망 수 미측정(0으로 간주 안 함) | 11 native 후보 중 fork 완료0; 전체 변경 분모 미확정 | FAIL(미확인) |
| 4 OFF 공식 WASM 바이트 동일 | base/off530752 bytes, SHA256 57afd1216ab3b50e0e1d35431e2502ee1e3e332f0fe3d1dcd3bce605fd1dde19 | 공식 WASM1짝 | PASS |
| 4 OFF/base 사건·음파 동일 | 12/12 IDENTICAL(온라인·스프린트·생성 × A/B × king/hunter) | 12키 | PASS |
| 4 CPU80M/100M·측정 누락 | ON/OFF 최대32.4M; 80M 경보0·100M 초과0·row 측정 누락0 | 192판 | PASS |
| 4 완료 탐색 깊이·미기록 수 보고 | ON 깊이1–7·d0=0/483535태그, OFF0–7·d0=16/474956태그; 깊이 태그 없음16693/16006 | ON500228/OFF490962 action | PASS(보고; 태그 없는 깊이 추정 안 함) |
| 4 동일 입력 judge CPU/깊이 | 측정0; 갈라진 판의 공통 r/id 깊이로 대체 안 함 | 11 native 후보, 공식 검증0 | FAIL(미확인) |

완전 추적 분모는 처음 보인 몸의 알려진 부분과 기록 행동으로 만든 새 머리 이력을 따라, 처음의 미관측 꼬리가 모두 제거됐거나 현재 몸 전체를 직접 관측한 차례만 센다(`memory-trace-strict.js`). 흩어진 조각을 누적 관측한 것만으로 완전한 순서를 안다고 세지 않는다. 이후 실제 LENGTH·분열을 포함한 다음 입력도 같은 배열 비교에 들어간다. 초기 추정/미관측 잔존18,050건의 native ON 시작 drift를 숨기지 않았으며 이는 같은 이력의 OFF22,525건과 별도 비교다. countdown 누락26,174,395 타일 관측·facing 모호0은 몸 위치 검사와 분리하고 native 선택을 인과 PASS로 쓰지 않았다.

사례는 `review.json`·`memory-strict-index.json`에 있다: 무료 L8은 big_empty A/king #48 r146 EE, 무료 L14는 big_empty B/king #10 r264 WSS, 유료 진주는 arena A/king #0 r11 WW다. 번들 arena r16, 온라인 default r113, 스프린트 around_unsw r74, 생성 gen_L_03 B r276에서도 무료 이동을 확인했다. stronghold A/king #308 r459는 포털 밖 진주를 먹어 L13→14이며 다음 LENGTH로 복원됐다. split 부모는 big_empty A/king #2 r2 등 모든 기록 split을 강제 재생했다. portals B/king #265 r217의 BODYX 끝 예측 L6/실제L5는 World 예측·다음 r218 배열 L5와 분리된다; Colosseum B/hunter #49 r124의 기존 끝 예측 L4/실제L2도 다음 r125 배열로 확인했다.

`causal-decisions.jsonl`의11행은 native 후보뿐이다. `replay.js`는 production point clock·과거 Planner 상태를 복원하지 않으며 제공된 도구/기보에 judge snapshot·spawn RNG fork 실행기가 없다. 즉시 oracle11/11 생존을 후속 무해함으로 바꾸지 않았다. 동일 World snapshot의 guard-only 개입과 모든 production 변경 결정의 다음3차례/여왕 인과 검사도 미확인이다.

**문맥만 — 양 arm 원시 사망·여왕 수명.** 아래 수치에는 PASS/FAIL을 붙이지 않는다. 키별 양 arm 원시/기제 사망은 `exp/bodymem/keywise.tsv`, 84키의 여왕 수명·ON−OFF 차이·양방향·관측 종료 여부는 `queen-lifetimes.tsv`에 모두 남겼다(사망=그 round, 생존=마지막 round+1).

| arm | S | W | O | H | A | 전체 사망 |
|---|---:|---:|---:|---:|---:|---:|
| OFF | 1591 | 5421 | 1349 | 717 | 1 | 9079 |
| ON | 1628 | 5654 | 1474 | 673 | 0 | 9429 |

기제 원인 OFF→ON: sac1592→1612, trap6758→7131, rammed301→320, ram268→219, enemyBody11→13, allyHead148→134, fault0→0, sprintDeath1→0. 여왕 수명 연장17키(+5…+254, 합+1731), 단축16키(−252…−10, 합−998), 동일51키; 새 사망4키·사망 회피4키 모두 문맥이다. 공통 r/id의 깊이197168건은 하락2959·동일191106·상승3103으로, 첫 변경 뒤 다른 입력이므로 비용 게이트가 아니다.

**의도한 판면2장 — schooltime A/proxy4_king/seed1, 여왕 #0 r85→86.** L8 WW의 두 걸음은 무료·진주0이다. 시작 `[162,163,164,224,223,222,221,220]` → `[160,161,162,163,164,224,223,222]`: 정상 꼬리2칸만 제거하고 L8을 유지한다. r86 실제 World/다음 LENGTH도 같은 배열이다. `exp/v16/board.js` 출력은 라운드 시작·폭60, a의 대문자는 머리이며 켈프선은 생략된다.

```text
round 85 around 42,3 (x 38..)
 39 ......*.*
  0 ...Bbb...
  1 C...*....
  2 c...Aaa..
  3 ..aaaaaXx
  4 .........
  5 ........x
  6 .........
  7 d.......X
a=#0 L8  b=#7 L3  c=#17 L2  d=#30 L2
```

```text
round 86 around 42,3 (x 38..)
 39 ......*.*
  0 C..b.....
  1 c..bB....
  2 ..Aaaaa..
  3 ....aaax.
  4 .......X.
  5 .........
  6 .........
  7 ........x
a=#0 L8  b=#7 L3  c=#17 L2
```

**제안: switch OFF (`BODYMEM_ON=OFF`).** 목적 개선·identity·CPU·오류 검사는 통과했지만 변경 결정의 후속 인과 무해함은 미확인이라 “목적 개선 + 깨짐 없음”을 모두 충족했다고 판정할 수 없다. 기본값은 수정하지 않았다. 시드1/21지도 표본이며 nice10 요청은 환경의 setpriority 거부로 적용되지 않았다.
