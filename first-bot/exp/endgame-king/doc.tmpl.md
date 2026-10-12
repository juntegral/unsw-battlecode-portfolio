# 끝판 왕: 마지막 200라운드에 최종 왕은 어떻게 자라고, 우리 "왕에게 모이기"는 돕나 해치나 (2026-09-30)

- 작성: 2026-09-30, 서브에이전트(끝판 왕). 리플레이만 읽었다. 로컬 경기, 네트워크, 원격 작업, `bot/`·`exp/cand-*`·`STACK-BACKLOG.md` 수정, 커밋은 0건이다. 추출은 `nice`, 자식 프로세스 3개로 돌렸다.
- 고침: 2026-10-01, 코디네이터 요청으로 상위권 500라운드형 전체(22:46 KST 스냅숏)를 추출하고(자식 프로세스 2개, nice 15), 질량 장부 캐시를 23:55 KST까지 넓혀 모든 상위권 값을 다시 셌다. 무엇이 움직였는지는 '전체 모집단으로 다시 셈' 절에 있다.
- 질문(코디네이터): 500라운드형 지도의 점수는 500라운드에 살아 있는 가장 긴 드래곤 하나다. 최종 왕은 마지막 200라운드에 어떻게 자라나? 우리 봇의 "왕에게 모이기"(`g<거리>` 이동 표식, r340부터)는 돕나 해치나? 세부 질문 다섯은 1–5절이다.
- 표기: **[사실]**은 스크립트 수치다. **[해석]**은 추론이고 검증 전이다.
- 방법(사용자 규칙 세 단계): (1) 전체 계산: 누적 전체 판을 스크립트로 센다. (2) 분류: 부류와 부류 크기를 적는다. (3) 선별 기보 연구: 읽기 전에 정한 규칙으로 고른 기보만 깊이 읽는다(6절).
- 1차 표본은 표식이 있는 우리 세트다. `g`, `feed`, `conv` 표식이 우리 봇이 언제 모이고 언제 먹였는지 정확히 말한다. 상위권끼리 판은 비교 기준이다.
- 스크립트(`exp/endgame-king/`): `extract.js`(판마다 한 줄, 캐시 `.cache/endgame-king/`), `report.js`(영문 전체 표 `report.md`), `extra.js`(보조 표 `extra.md`), `ml_top.js`(질량 장부 캐시의 승자·패자 계보 `ml-top.md`, 교차 확인), `numbers_wl.js`(본문이 인용하는 모든 상위권 값 `numbers-wl.json`), `diff_numbers.js`(처음 문서 대비 움직인 값 `changes.md`), `cc_expo.js`·`cc_intercept.js`(전환 사슬 캐시로 교차 확인), `doc.js`(이 문서의 표 `doc-tables.md`), `narrative.py`·`fill.js`(본문과 표 끼우기), `recount.js`(독립 재계산 `recount.txt`), `wl_sheet.js`(본문이 인용하는 상위권 값), `cases.js`(선별 `cases.md`), `film.js`(기보 읽기).

## 모집단
<!--POP-->

| 묶음 | 판 | 비고 |
|---|---:|---|
{{POP_ROW}}
| 우리 온라인 세트 | 1,469판(21세트) | stack1–8(stack6 두 웨이브), merge2 세 웨이브, swarm8, avoid6, portal1, baseline-r1 ×3(g4r4), px 셋(px8, px9d, px-king-v2). `r1-online`, `r1-autoscrim`, `g1`, `g2`는 뺐다. W9(`cand-stack8-online`)는 {{STACK8}} |
| 그 판의 상대 | 같은 판의 상대 쪽 | 극상위권 6팀과 DEV. 표의 "우리 판의 상대" |

- 집단 표기: g4r4 = baseline-r1·r1b·r1c, merge2 = 세 웨이브, stack1–4, stack5–7 = stack5·stack6(두 웨이브)·stack7(덮기 분열 이후), stack8 = W9, px = 흉내 계열(표식 없음). 옛 봇(swarm8, avoid6, portal1)은 `report.md`에만 있다.
- 500라운드형 = Autarky, Portals, Schooltime, Slithery Fight, Trauma. 전멸형 = Devil, Trophy, Prisoners Dilemma(6·10마리), Queen Of Spades, Default.

{{CHANGES}}

## 점검
- [사실] 질량 장부의 재구성 점검(sim, splits, drops, eatTC, ledger, final, lineage, natBal, dropBal, unknownDeath)은 모든 판에서 0이다.
- [사실] 이 연구의 점검도 모두 0이다.
  - spawn: 앞 훑기로 찾은 자연 진주(처음 + 생성) 수 = 장부의 natStart + natSpawned.
  - pair: 자연 진주를 먹은 사건마다 그 칸의 생성과 짝이 맞음.
  - lin: 이 연구의 계보 분해로 낸 L300·L350·L400·L450과 끝 길이 = 장부의 `lin.cp[t].Lt`와 끝 길이.
  - dec: 뿌리 드래곤의 처음 길이 + 모든 흐름 = 끝 왕 길이.
  - surv: 살아남은 드래곤마다 태어난 길이 + 먹은 진주 − 질주 − 떼어 낸 새끼 = 끝 길이.
- [사실] 독립 재계산(`recount.js`): 장부와 추출 코드를 쓰지 않고 원 사건만 쓴다. 길이는 셈이다(처음 몸, 행동하는 드래곤의 턴에 진주 칸이 비면 +1, 여러 걸음 이동은 −(걸음−1), 분열 몸은 `dragonSplit`). 사망 직후 이어지는 진주 칸이 그 드래곤의 사망 진주이고 나머지는 자연 진주다. {{RECOUNT}}
- [사실] 앞선 연구와 맞는다: 상위권 승자의 왕 아닌 드래곤(길이 ≥4)의 r340 뒤 턴 가운데 왕에서 17칸 밖 {{W_FAR}}(공급 사슬: 16칸 밖 65%), 한 턴에 왕 쪽으로 가까워지는 비율 26–28%(공급 사슬 25–29%), 끝 왕 길이 승자 {{W_FIN}}(질량 장부 45.9–46.5), 계보 = 팀 최장 r350 {{W_LR350}}(전환 사슬 59%), r300 뒤 승자 희생 진주 가운데 계보가 먹은 몫 {{W_SACLINE}}(전환 사슬 24%).
- [사실] 교차 확인: 가로채기 몫(3.4절)은 전환 사슬 캐시의 먹은 쪽 분류로 다시 세어 겹치는 8세트 모두 같다(`cc_intercept.js`). 노출(5절)은 전환 사슬 캐시의 r300·350·400·450 스냅숏(상위권 500라운드형 5,229 팀-경기씩, 모든 길이)으로 다시 재어 같은 방향이다(`cc-expo.md`).

## 정의
- **최종 왕, 계보:** 끝에 가장 긴 드래곤(같으면 작은 id)과 그 부모들. 계보 드래곤 i는 태어난 때부터 계보 드래곤 i+1이 태어난 분열까지를 맡는다(질량 장부의 약속). 끝 왕 = L_t + 계보가 먹은 진주 − 질주 − 떼어 낸 새끼(분열: 떼어 냄) − 계보가 새끼로 넘어갈 때 부모 쪽에 남긴 몸(분열: 넘김).
- **흐름 분해(1절):** 계보가 먹은 진주를 출처로 나눈다. 자연, 우리 희생(장부의 sac: 차례 시작에 빈 이웃이 있는데 스스로 죽음), 우리 다른 사망(갇힘·박힘·아군 머리 등), 적 사망. 50라운드 구간은 r300–349, r350–399, r400–449, r450–499다.
- **왕(그 순간):** 그 라운드 첫 턴에 팀에서 가장 긴 드래곤. **계보 드래곤(그 순간):** 그때 살아 있는 최종 왕의 조상. 둘은 다를 수 있다(4절).
- **r340 무리:** r340 첫 턴에 살아 있는, 왕이 아닌 길이 ≥4 드래곤(우리 봇의 모이기 대상과 같은 조건: `GATHER_FEED_MIN_LEN` 4). 끝은 가족(그 드래곤과 r340 뒤 태어난 자손)으로 본다: 계보(자기나 자손이 최종 왕 계보) / 가족 삶 / 희생 / 다른 죽음 / 분열 뒤 가족 죽음.
- **모이기 에피소드:** 이동 표식에 `g<거리>`가 처음 붙은 우리 드래곤. **뿌리 에피소드:** 부모가 이미 모이는 중일 때 분열로 태어난 드래곤을 뺀 것. 통로 고리와 분열 유턴이 몸을 새 id로 넘기기 때문이다(Autarky 한 판에 id 기준 79개). 뿌리 에피소드의 끝도 가족으로 본다: 계보 / 계보 밖 삶 / 표식 먹이(마지막 죽음이 `feed`·`conv`) / 다른 희생 / 다른 죽음.
- **시작 칸 둘레:** 모이기 시작(또는 r340) 때 머리에서 토러스 맨해튼 5 안의 칸에 생긴 자연 진주. 앞 40라운드와 뒤 40라운드에 누가 먹었나(자기 / 다른 우리 / 적 / 안 먹힘)를 센다. 떠난 자리를 적에게 내줬는지 보는 잣대다.
- **노출:** 계보 드래곤의 턴 시작에 가장 가까운 적 머리까지 토러스 맨해튼 거리. 해초와 포털은 무시한다. Portals는 벽 너머도 가깝게 재므로 따로 본다.
- **표식 먹이:** `feed #<id> …`(모이기 창 r340–429는 왕 부류만, r430 뒤 끝판 창은 5걸음 안의 더 긴 아군 누구든), `feed #<id> … conv`(r300부터 길이 ≤4가 3걸음 안의 길이 ≥8·자기보다 4 이상 긴 아군에게). 코드는 `exp/cand-stack8/bot/plan.cpp` `decide()` L1062–1147.

## 요약
{{SUMMARY}}

## 1. 최종 왕의 길이는 어디서 오나 (질문 1)
<!--T:T1-->

<!--T:T1b-->

{{S1_FACTS1}}

<!--T:T1c-->

{{S1_FACTS2}}

<!--T:T1e-->

<!--T:T1f-->

{{S1_FACTS3}}

## 2. 늦게 빨리 자라나, 길게 시작하나 (질문 2)
<!--T:T2-->

<!--T:T2b-->

{{S2_FACTS}}

## 3. 모이기 (질문 3)
### 3.1 모이는 드래곤은 무엇을 하나
<!--T:T3-->

{{S31_FACTS}}

<!--T:T3b-->

{{S31_FACTS2}}

### 3.2 무엇을 내주나
<!--T:T3d-->

{{S32_FACTS}}

### 3.3 상위권의 왕 아닌 드래곤
<!--T:T3c-->

{{S33_FACTS}}

### 3.4 모이기의 먹이는 계보로 가나
<!--T:T3e-->

<!--T:T3f-->

{{S34_FACTS}}

## 4. 곁의 더 긴 아군에게 먹이면 최종 왕에게 가나 (질문 4)
<!--T:T4-->

{{S4_FACTS1}}

<!--T:T4b-->

<!--T:T4c-->

{{S4_FACTS2}}

## 5. 그 밖에 끝판을 가르는 것: 왕의 노출 (질문 5)
<!--T:T5-->

<!--T:T5b-->

<!--T:T5c-->

<!--T:T5d-->

{{S5_FACTS}}

## 6. 선별 기보 연구 (3단계)
{{S6}}

## 7. 메커니즘 제안
{{S7}}

## 한계
{{LIMITS}}

## 다시 돌리기
- 추출(이미 있는 판은 건너뜀): `nice -n 10 node exp/endgame-king/extract.js online <세트> [...] --jobs 3`, `nice -n 10 node exp/endgame-king/extract.js top --jobs 2 --keys exp/endgame-king/top-keys-2246-r500.keys`(전체 추출; 전멸형은 `-elim.keys`). `exp/endgame-king/run_full.sh`가 차례로 하고, `memwatch.sh`가 여유 메모리 10% 아래에서 멈춘다.
- 표: `node exp/endgame-king/report.js`(→ `report.md`, `numbers.json`), `node exp/endgame-king/extra.js`(→ `extra.md`), `node exp/endgame-king/ml_top.js > exp/endgame-king/ml-top.md`(질량 장부 전체 캐시의 승자·패자 계보), `node exp/endgame-king/cc_expo.js > exp/endgame-king/cc-expo.md`(노출 교차 확인), `node exp/endgame-king/cc_intercept.js`(가로채기 교차 확인), `node exp/endgame-king/wl_sheet.js`(상위권 값 한눈에).
- 이 문서: `exp/endgame-king/finalize.sh pass ml`(값 표 → 앞뒤 비교 → 표 → 본문 → 끼우기를 차례로; 첫째 인자는 500라운드형 계보, 둘째는 전멸형 계보의 원천). 본문은 `narrative.py`, 틀은 `doc.tmpl.md`, 실행마다 바뀌는 문장은 `make_extra.py`가 만든다.
- 독립 재계산: `nice -n 10 node exp/endgame-king/recount.js --top-every 10 --jobs 3` → `exp/endgame-king/recount.txt`(한 세트만: `--only-set <세트> --out recount-<이름>.txt`; 새 판 무작위 300판: `node exp/endgame-king/pick_new300.js > exp/endgame-king/recount-new300.keys` 뒤 `--keys exp/endgame-king/recount-new300.keys --out recount-new300.txt`).
- 선별과 기보: `node exp/endgame-king/cases.js --per 2 > exp/endgame-king/cases.md`, `node exp/endgame-king/film.js <키> <id,...|lineA|lineB> --from 330 --to 500 --every 5`.
