#!/usr/bin/env node
// Korean labels for the tables of exp/mech-failures/report.js (used to paste class tables into
// research/observations/mech-merge2-failures.md without retyping numbers).
// usage: node exp/mech-failures/report.js ... | node exp/mech-failures/ko.js
'use strict';
const D = [
  // escape classes
  ['second head: outside the 7x7 view at the escape', '다른 머리: 탈출 때 시야(7×7) 밖'],
  ['second head: in view at the escape', '다른 머리: 탈출 때 시야 안'],
  ['pursuit: the head we escaped from', '추격: 피했던 그 머리'],
  ['newborn: child born after the escape', '새끼: 탈출 뒤 태어난 적 조각'],
  ['not a loss: our own TRADE', '손실 아님: 우리 돌진'],
  ['other death: allyHead', '기타: 우리 머리와 정면'],
  ['other death: trap', '기타: 갇힘'],
  ['body lost through a descendant', '자손을 통해 잃음'],
  // rams
  ['priced: in reach, threat in the value (v<0), still hit', '알았음: 도달 거리 안, 값에 위협 반영(v<0)'],
  ['blind spot: path through a tile occupied at the decision', '사각: 결정 순간 막혀 있던 칸'],
  ['reach gap: pearl eaten on the strike path', '도달 오차: 질주 길의 진주'],
  ['reach gap: tail unseen, killer L>=5', '도달 오차: 꼬리 안 보이는 L5 이상'],
  ['unpriced: cause not visible in the replay', '값에 없음: 원인 미상'],
  ['unseen: killer outside the 7x7 view', '못 봄: 시야 밖'],
  ['unseen: killer farther than 8 at the decision', '못 봄: 8칸 밖'],
  ['unseen: killer born after the decision (a split)', '못 봄: 결정 뒤 분열로 태어난 적'],
  ['newborn: no decision before the ram', '막 태어남: 결정 전에 박힘'],
  // feed
  ['target alive at the end', '지목 아군이 끝까지 삶'],
  ['body lives on: loop stub (no-exit)', '몸은 삶: 고리의 남은 조각'],
  ['body lives on: fed onward (chain)', '몸은 삶: 다시 희생(연쇄)'],
  ['body lives on: trap', '몸은 삶: 갇힘'],
  ['body lost: fed onward (chain)', '몸 잃음: 다시 희생(연쇄)'],
  ['body lost: PD king rammed late', '몸 잃음: PD 왕이 끝에 박힘'],
  ['body lost: target rammed', '몸 잃음: 지목 아군이 박힘'],
  ['body lost: loop stub (no-exit)', '몸 잃음: 고리 조각(no-exit)'],
  ['body lost: head-on with our own head', '몸 잃음: 우리 머리와 정면'],
  // gather
  ['ok: fed', '성공: 희생까지'], ['ok: within 3', '성공: 3칸 안'],
  ['stopped: game ended', '멈춤: 경기 끝'], ['stopped: goal lost (news stale or goal changed)', '멈춤: 목표 정보 끊김'],
  ['stopped: became the longest', '멈춤: 스스로 가장 길어짐'], ['stopped: length < 4', '멈춤: 길이 4 미만'], ['stopped: units < 4', '멈춤: 드래곤 수 4 미만'],
  ['died: into our own body', '죽음: 우리 몸에 박음'], ['died: head-on with our own head', '죽음: 우리 머리와 정면'],
  ['died: enemy ram', '죽음: 적 박치기'], ['died: our TRADE', '죽음: 우리 돌진'], ['died: trap', '죽음: 갇힘'], ['died: sac', '죽음: 희생 판정'],
  // portal
  ['exit held by our own dragon (desperate entry)', '출구에 우리 드래곤(필사 진입)'], ['exit held by our own dragon', '출구에 우리 드래곤'],
  ['exit held by an enemy (desperate entry)', '출구에 적(필사 진입)'], ['exit held by an enemy', '출구에 적'],
  ['dead-end exit (no-exit)', '막다른 출구(no-exit)'], ['enemy after the exit', '출구 뒤 적'], ['our own dragon after the exit', '출구 뒤 우리 드래곤'],
  ['feed (deliberate)', '희생(의도)'],
  // trade
  ['our collector nearer or equal', '우리 수거자가 가깝거나 같음'], ['no head of ours within 14', '14칸 안에 우리 머리 없음'], ['their collector nearer', '상대 수거자가 더 가까움'],
  // split
  ['child dead, body lives on (its own escape split)', '새끼는 죽고 몸은 삶(새끼의 탈출 분열)'],
  ['trapped after entering an unexplored portal', '미탐색 포털 뒤 갇힘'], ['trapped after a known portal', '알려진 포털 뒤 갇힘'],
  ['trapped in a pocket (no portal)', '주머니에 갇힘'], ['rammed by an old hunter (>50 rounds)', '오래 산 사냥 조각(50라운드 초과)에게 박힘'],
  ['rammed by a young piece (<=50 rounds)', '젊은 조각(50라운드 이하)에게 박힘'], ['our child rammed (TRADE or forced)', '새끼가 박음(돌진·마지막 수)'],
  ['other: enemyBody', '기타: 적 몸'],
  // headers
  ['| class | n | by opponent | by map | by phase | by length |', '| 유형 | 건수 | 상대별 | 지도별 | 국면별 | 길이별 |'],
  ['| population | response | turns | mean L | mass kept +10 | mass kept +30 | dragon dead <=10 | body dead <=10 |', '| 모집단 | 대응 | 턴 | 평균 길이 | 몸 보존 +10 | 몸 보존 +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |'],
  ['| population | maps | phase | turns | short enemy head <=3 | <=5 | ally head <=3 |', '| 모집단 | 지도 | 국면 | 턴 | 짧은 적 머리 3칸 안 | 5칸 안 | 아군 머리 3칸 안 |'],
  ['| population | length | crossings | dragon alive +3 | body alive +3 | died on the step | held by own team | held by enemy |', '| 모집단 | 길이 | 통과 | 자신 +3 생존 | 몸 +3 생존 | 넘는 걸음에서 죽음 | 출구에 자기 팀 | 출구에 적 |'],
  ['| population (children L<=3, all kinds of split) | children | per game | dead within 30 | causes |', '| 모집단(L≤3 새끼, 모든 분열) | 새끼 | 판당 | 30라운드 안 죽음 | 원인 |'],
  ["| population | sacrifices | per team-game | length per team-game | drops eaten by own team | by enemy | nearest own head (median) | its length (median) | an eater's body alive at the end | an eater on the final king's line | L2-3 share |", '| 모집단 | 희생 | 팀·판당 | 팀·판당 길이 | 진주: 자기 팀 | 적 | 가장 가까운 자기 머리(중앙값) | 그 길이(중앙값) | 먹은 드래곤의 몸이 끝까지 삶 | 먹은 드래곤이 최종 왕 계보 | L2–3 비율 |'],
  ['| set | esc | sprintEsc | rams on our L>=6 | feed | trade pearls | policy split | portal-step deaths |', '| 세트 | esc | 2칸 위협 질주 | 우리 L≥6 박힘 | 먹이 | 돌진 진주 | 정책 분열 | 포털 걸음 죽음 |'],
  ['| population | games | head-ons | children | self deaths r250+ | long-dragon turns |', '| 모집단 | 판 | 머리 충돌 | L≤3 새끼 | r250 뒤 자해 사망(다른 드래곤과 안 부딪힘) | 긴 드래곤 턴 |'],
  ['(mech_check ex ', '(mech_check 정의 '],
  ['us, merge2 (210)', '우리, merge2 (210판)'], ['us, all sets (630)', '우리, 전체 9세트 (630판)'], ['them in our games (630)', '같은 판의 상대 (630판)'],
  ['them in merge2 games (210)', '같은 판의 상대, merge2 (210판)'], ['top-vs-top, per team-game (8734)', '상위권끼리, 팀·판당 (8,734판)'], ['top-vs-top (8734)', '상위권끼리 (8,734판)'],
  ['us, merge2 r0-249 (210)', '우리, merge2, r0-249 (210판)'], ['us, merge2 r250+ (210)', '우리, merge2, r250+ (210판)'],
  ['them in merge2 games r0-249 (210)', '같은 판의 상대, r0-249 (210판)'], ['them in merge2 games r250+ (210)', '같은 판의 상대, r250+ (210판)'],
  ['top-vs-top r0-249 (8734)', '상위권끼리, r0-249 (8,734판)'], ['top-vs-top r250+ (8734)', '상위권끼리, r250+ (8,734판)'],
  ['| us, merge2 |', '| 우리, merge2 |'], ['| top-vs-top |', '| 상위권끼리 |'], ['| our online sets |', '| 우리 온라인 세트 |'],
  ['| single |', '| 한 걸음 |'], ['| split |', '| 분열 |'], ['| sprint2 |', '| 2칸 질주 |'], ['| sprint3 |', '| 3칸 질주 |'],
  ['| elim|', '| 전멸형 |'], ['| r500|', '| 500라운드형 |'],
];
let s = require('fs').readFileSync(0, 'utf8');
for (const [a, b] of D) s = s.split(a).join(b);
process.stdout.write(s);
