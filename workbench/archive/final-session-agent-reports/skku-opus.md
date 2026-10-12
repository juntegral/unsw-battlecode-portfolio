# Reports sent to the lead by skku-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:39:58 — skku-opus headline: keep requesting, seat not proven, no constant

skku-opus HEADLINE (55 games on disk, all 10:04-13:58 KST today; the running battle 1535538-42 is not on disk)
5) YES, keep requesting SKKU. Seat A is 28/40 = 0.70 per game [M] (95% range about 0.55-0.82); one17 alone 7/10; both ranked seat-A battles won (4-1, 3-2). Elo break-even against a team 80-100 above us is about 0.37, so even the pooled 33/55 = 0.60 gains rating. I put 0.60-0.65 per game on it, fairly sure it is above 0.5; not sure it is 0.70.
Seat: A 28/40 vs B 5/15 (Fisher p 0.03) is NOT the map draw (seat-A per-map rates applied to the 15 seat-B maps predict 11.1 wins, actual 5) [M], but 55 games cannot pin it on the seat: one13 was played only from seat B (1/5); one15 is level (A 9/15, B 3/5); the gap is one14 (A 12/15, B 1/5, 19 minutes apart). Same versions only: A 21/30 vs B 4/10, p 0.13. The engine gives seat A no first move: queen ids 0/1 alternate game by game inside a battle whatever the seat [M].
Constant for the last upload: NONE. Nothing here is tested and the SKKU pattern is the general one already known, not a new lever.

Numbers behind it [M]:
- First mover (our queen id 0): 19/27; id 1: 14/28 (inside seat A 16/20 vs 12/20; seat B 3/7 vs 2/8). A hint that moving first helps, p about 0.17, not usable.
- Same 11 maps both seats (per-map means): our pearls by r100 142 (A) vs 122 (B); THEIRS 96 vs 120; their dragons r100 18.5 vs 22.0; our queen died 57% vs 82%; their queen died 93% vs 68%. So when they request, they eat about 25% more by r100 and their queen survives more. Their queen sits the same place both seats (4.5 vs 4.3 cells from start to r100; ours 9.4 / 11.0).
- How they kill our queen (27 rams + 8 own-move deaths + 1 other in 36 deaths): rammer length 2-4 in 20/27, from 1-2 cells in 18/27, paying 0-1 steps in 20/27 (paid 1+ in 18), visible the turn before in 21/27, our queen was length 2-3 in 16/27, their queen already dead in 9/27. From seat B all 11 of our queen deaths were rams (10/11 seen the turn before, 8/11 from 1-2 cells, queen length 2-3 in 8/11).
- What kills THEIR queen in our 33 wins (32 deaths): 23 our rams (our length 2-4 in 19/23; from exactly 3 cells paying 2 in 8, from 1 cell free in 8), 9 her own move; 13 dead by r100 in wins vs 2 in our 22 losses. Their queen dies in 44/55 games overall (ours 36/55): staying home (2-5 cells) does not keep her alive, so I do NOT suggest a home leash.
Files: ROOT/data/codex/astra/skku-opus/tables.txt (full table + blocks), tables2.txt (matched maps, per-loss lines), rows.json. Final by 14:46.

---

## 2026-10-09 05:39:58 — skku-opus FINAL: keep requesting; seat unproven; no constant; queen steps next to heads

skku-opus FINAL (55 games v team 249, all today 10:04-13:58 KST; battle 1535538-42 not on disk, not counted)
5) YES, keep requesting SKKU. Seat A 28/40 = 0.70 per game [M] (95% range about 0.55-0.82); by set 12/15, 9/15, 4/5, 3/5. Break-even against a team 80-100 Elo above us is about 0.37, so I put 0.60-0.65 per game on it; fairly sure above 0.5, not sure of 0.70. Stop only if the running battle comes back 1-4 or worse (their bot may have changed; I cannot see their version, botId is blank).
Seat: A 28/40 v B 5/15 is not the map draw (seat-A per-map rates on the 15 seat-B maps predict 11.1 wins, actual 5) and not an engine first move (queen ids 0/1 alternate game by game whatever the seat), but 55 games cannot pin it on the seat: one13 played only seat B (1/5), one15 is level (A 9/15, B 3/5), the whole gap is one14 (A 12/15, B 1/5). Same versions only: 21/30 v 4/10, p 0.13 [M].
Constant for the last upload: NONE. The one new thing I found is a code question, not a value (below), and nothing is tested.

Win rates [M]: version one13 1/5, one14 13/20, one15 12/20, one17 7/10. Map and seat with 3+ games: Devil A 3/4, Stripes A 3/4, Trophy A 3/3, Portals A 1/3, Tower Defense A 1/3. Worst maps overall: Trauma 0/2, Australia 1/4, Tower Defense 1/4, Portals 1/3, Slithery 1/3. Map size does not explain the seat gap (A small/mid/big 14/20, 8/12, 6/8; B 3/8, 1/2, 1/5). Our queen id 0 (we move first) 19/27, id 1 14/28, p about 0.17.

What differs when THEY request (same 11 maps, per-map means) [M]: their pearls by r100 120 v 96, their dragons at r100 22.0 v 18.5; ours 122 v 142 pearls, 23.6 v 25.1 dragons; our queen dies 82% v 57%, theirs 68% v 93%. Whose queen dies first: seat A theirs 21, ours 18; seat B 6 and 6. The decider is economy by r100 plus our queen's survival, not an early queen kill (dead by r100: ours 10/40 and 3/15, theirs 12/40 and 3/15).

Their opening [M]: first split r0 (so do we), first eat r8-9 (ours r7-9), queen length 2 at r50 (ours 3), queen 2-5 cells from her start to r100 (ours 8-9). Staying home does not save her: their queen dies in 44/55 games, ours in 36/55.

How they kill our queen [M]: 36 deaths = 27 rams, 8 her own move, 1 other. Rammer length 2-4 in 20/27, from 1-2 cells in 18/27, paying 0-1 steps in 20/27, in her view the turn before in 21/27, our queen length 2-3 in 16/27, their queen already dead in 9/27.
NEW [M]: in 19 of the 21 rams where the rammer was in her view, our queen's own last step took her one cell CLOSER to that head. In 10 she was outside its reach (free + payable steps) and stepped in; in 8 of 27 she stepped next to a head that was 2 cells away and died to a free step (paid 0). Moments: 1533125 r61 queen L2 (19,3)->(18,3), L3 head at (18,4); 1526090 r86 L3 (28,44)->(27,44), L3 head at (27,43); 1527404 r199 L2 (10,3)->(10,2), L2 head at (9,2); 1514290 r327 L4 (36,13)->(37,13), the only foe in view an L2 head at (37,14), she had also stepped next to it the turn before. Their queen does it less (17 of 25 moved closer, 7 moved away but not far enough).
[E] QS_HIT_PENALTY should veto such a cell; I did not find why it does not (candidates: `qs_plain` switching queen_wary off, main.cpp:6143; or no other open cell, I did not check walls). Distances are torus Manhattan, walls ignored.

What kills their queen in our 33 wins [M]: 32 deaths = 23 our rams (our length 2-4 in 19; from 3 cells paying 2 in 7, from 1 cell free in 8), 9 her own move. Dead by r100 in 13 of our wins, 2 of our 22 losses. Our hunt works against a queen that sits still at length 2-3.

Suggestions, with the overfitting mark:
1. General (any opponent, any map), NOT ready: the queen never ends a move next to a visible enemy head or inside its free step. No existing constant I can name with a value; needs the reason above first.
2. Do not add QUEEN_HOME_LEASH: SKKU-shaped only, and their home-sitting queen dies more than ours.
3. Do not raise QS_PAY_REACH above 4: only 3 of 27 rams came from 5+ cells.

Not checked: their bot version over time, spawn side by seat, walls around the queen at death, death reason codes for own-move deaths, the battle in progress.
Files in ROOT/data/codex/astra/skku-opus/: tables.txt (55-row table: date, version, seat, map, result, how, queens at end, queen death rounds, pearls and dragons at r100; then blocks by seat/result), tables2.txt (matched maps, one line per loss and per win), qlast.txt (last step before each ram), rows.json, scripts run.py agg.py agg2.py qlast.py qlog.py.

---

## 2026-10-09 05:39:58 — closing summary

SKKU 분석을 리드에게 두 번(헤드라인, 최종) 보냈고, 결론은 "계속 신청, 좌석 효과는 미확정, 마지막 업로드에 넣을 상수 없음"입니다. 디스크에 있는 55판(전부 오늘 10:04~13:58 KST)을 셌고, 진행 중인 배틀 1535538-42는 디스크에 없어 빠졌습니다.

- **계속 신청할지**: 예. A석 28/40 = 판당 0.70(95% 구간 약 0.55~0.82), 세트별로 12/15, 9/15, 4/5, 3/5입니다. 80~100점 위 팀 상대 손익분기는 약 0.37이라, 판당 0.60~0.65로 잡습니다. 0.5 이상은 꽤 확신하지만 0.70은 확신하지 못합니다. 진행 중인 배틀이 1-4 이하로 나오면 멈추라고 리드에게 적어 보냈습니다.
- **좌석**: A 28/40 대 B 5/15는 맵 추첨 탓이 아닙니다. A석 맵별 승률을 B석 15판 맵에 적용하면 기대 11.1승인데 실제는 5승입니다. 엔진상 선공도 아닙니다(여왕 id 0/1은 좌석과 무관하게 판마다 번갈아 나옴). 다만 55판으로 좌석 탓이라고 못 박을 수는 없습니다.
  - one13은 B석에서만 뛰었고(1/5), one15는 동률(A 9/15, B 3/5)입니다.
  - 버전을 겹치는 one14·one15로만 좁히면 A 21/30 대 B 4/10(p 0.13)이고, 그 격차는 one14(A 12/15, B 1/5)에서만 납니다.
- **상대가 신청한 판의 차이**(같은 11개 맵 평균): r100까지 상대 진주가 120 대 96으로 더 많고, 우리 여왕 사망은 82% 대 57%입니다.
- **새로 찾은 것**: 우리 여왕이 박혀 죽은 27건 중, 박은 머리가 직전 턴 시야에 있던 21건에서 19건은 여왕의 마지막 한 걸음이 그 머리 쪽으로 한 칸 다가간 것이었습니다. 그중 8건은 2칸 떨어진 머리 옆 칸으로 들어가 무료 한 걸음에 죽었습니다(예: 1533125 r61, 1526090 r86, 1527404 r199, 1514290 r327).
- **왜 상수가 없는지**: `QS_HIT_PENALTY`가 그 칸을 막아야 하는데 왜 안 막는지는 못 찾았습니다(후보는 `main.cpp:6143`의 `qs_plain`, 또는 다른 빈 칸이 없었을 가능성; 벽은 확인하지 않음). 값 조정이 아니라 코드 문제라 테스트 없이 올릴 수 없습니다.
- **하지 말 것**: `QUEEN_HOME_LEASH`는 넣지 않는 게 맞습니다(집에 붙어 있는 SKKU 여왕이 44/55로 우리 36/55보다 더 많이 죽음). `QS_PAY_REACH`를 4 위로 올리는 것도 근거가 없습니다(5칸 이상에서 온 박치기는 27건 중 3건).

확인하지 못한 것은 상대 봇 버전 변화, 좌석별 스폰 위치, 여왕 자멸 8건의 사망 사유 코드입니다. `report.md`는 만들지 않았고 리드에게 보낸 최종 메시지가 보고서입니다.

파일은 `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/skku-opus/`에 있습니다.
- `tables.txt`: 55판 표와 좌석·결과별 집계
- `tables2.txt`: 같은 맵 비교, 패배·승리 판별 한 줄 요약
- `qlast.txt`: 박치기 직전 여왕의 마지막 걸음
- `rows.json`: 판별 원자료
- 스크립트 `run.py`, `agg.py`, `agg2.py`, `qlast.py`, `qlog.py`

---

## 2026-10-09 05:47:33 — skku-opus: battle 1536232-36 per-loss lines and one20 verdicts

skku-opus, battle 1536232-36 (one18, bot 21761), L W L L L [M]. Note: all five game json files have teamAId 1119, so by the files we were seat A here, not B.
1536232 Slithery Fight: lost on queen (0 v 18) at r499. Our queen L4 rammed r170 by an L11 from 4 cells, 4 steps, 1 paid; gap 3 at her last turn start, her last step went AWAY (3 to 4). Their queen alive. Pearls r100 407 v 411, dragons 62 v 63.
1536234 Islands: lost on total (104 v 119, longest 32-32, both queens dead). Our queen L3 rammed r175 by an L3 from 2 cells, 1 free + 1 paid; gap 3 at her last turn start (outside its reach of 2), her last step (0,13)->(55,13) went straight TOWARD the head at (53,13). Their queen alive then (died r250). Pearls 166 v 253, dragons 34 v 50.
1536235 Default: lost by elimination r364. Our queen split 4 to 2 at r60 with two L3 heads 3 and 4 cells away, then r61 rammed by an L3 from 2 cells, 1 free + 1 paid; gap 3 at her last turn start, last step (28,19)->(28,18) TOWARD the head at (28,16). Their queen alive. Pearls 33 v 85, dragons 11 v 26.
1536236 Tower Defense: lost by elimination r233. Our queen paid 4 to 2 fleeing at r94, then r97 rammed by an L3 from 2 cells, 1 free + 1 paid; gap 3 at her last turn start, last step (14,1)->(14,0) TOWARD the head at (12,0). Their queen alive. Pearls 12 v 55, dragons 3 v 14.
(1) Fits: they ate 27% more by r100 over the five games (874 v 686; 30% more in the four losses), our queen died in 4 of 5 (theirs 2 of 5), and in 3 of the 4 losses she stepped from gap 3 to gap 2 toward an L3 that then paid one step, the pattern from my last message. In all three the rammer's length was at least hers, which is what the TRADE_EVEN "worth" test at main.cpp:4584 accepts for the queen [C]; that she was pulled by it is [E].
(2) one20, from the board at the decisive turn (walls not checked, Manhattan gaps):
- Slithery Fight: no. She already moved away; an L11 with 3 free steps from 3 cells cannot be outrun at L4.
- Islands: yes, probably. North and south were open and outside the L3's true reach; all three steps were inside the bot's modelled reach of 4, so the new rule applies and the pull toward the head goes. If she lives, their queen still dies at r250 and we win on queen; whether she lives to r499 I cannot tell.
- Default: no. At r61 west was her own body, east and south were next to another L3 head at (29,20), north was the least bad cell and they paid for it. The mistake was the split to 2 at r60, which one20 does not touch (QS_SHED_MAX 9 only holds queens of 10+).
- Tower Defense: that death yes, probably (south (14,2) held a pearl and was outside both near heads' true reach; the map is 512 cells so dropping QUEEN_DEAD_ALL also removes any dead-end push north); the game cannot tell, we had 3 dragons against 14 at r100.
Output: ROOT/data/codex/astra/skku-opus/last.txt (turns, views and 7x7 boards).

---

## 2026-10-09 05:47:33 — closing summary

방금 끝난 SKKU 배틀(1536232-36, one18, L W L L L) 분석을 14:45쯤 리드에게 보냈습니다. 4패 모두 우리 여왕이 박혀 죽었고, 그중 3판은 여왕이 스스로 상대 머리 쪽으로 한 칸 다가간 직후였습니다.

먼저 리드 말과 다른 점 하나: 다섯 판 json 모두 `teamAId`가 1119라서, 파일상으로는 이번에 우리가 B석이 아니라 A석이었습니다.

| 판 | 맵 | 판정 | 우리 여왕 사망 | 마지막 걸음 | r100 진주 (우리/상대) | r100 드래곤 |
|---|---|---|---|---|---|---|
| 1536232 | Slithery Fight | 여왕 (0 대 18) | r170, L11이 4칸에서 4걸음(1 유료) | 멀어짐 (3→4) | 407 / 411 | 62 / 63 |
| 1536234 | Islands | 총길이 (104 대 119) | r175, L3이 2칸에서 무료 1 + 유료 1 | 머리 쪽으로 (3→2) | 166 / 253 | 34 / 50 |
| 1536235 | Default | 전멸 r364 | r61, L3이 2칸에서 무료 1 + 유료 1 | 머리 쪽으로 (3→2) | 33 / 85 | 11 / 26 |
| 1536236 | Tower Defense | 전멸 r233 | r97, L3이 2칸에서 무료 1 + 유료 1 | 머리 쪽으로 (3→2) | 12 / 55 | 3 / 14 |

네 판 모두 우리 여왕이 죽을 때 상대 여왕은 살아 있었습니다. Default에서는 r60에 L3 머리 둘이 3~4칸 거리에 있는데 여왕이 4에서 2로 분열했고, 다음 턴에 죽었습니다.

**기존 그림과 맞는지**: 맞습니다. 다섯 판 합계로 상대가 r100까지 27% 더 먹었고(874 대 686), 우리 여왕은 5판 중 4판에서 죽었습니다(상대는 2판). 다가가다 죽은 3판 모두 박은 드래곤 길이가 여왕 길이 이상이었는데, 이는 `main.cpp:4584`의 맞교환 가치 판정이 여왕에게도 통과시키는 조건입니다. 다만 그 판정 때문에 끌려갔다는 것은 추정입니다.

**one20이었다면** (결정 턴의 판면 기준, 벽은 확인하지 않았고 거리는 맨해튼):
- **Slithery Fight**: 아니오. 이미 멀어지는 쪽으로 움직였고, L4로는 L11을 따돌릴 수 없습니다.
- **Islands**: 아마 예. 남북 칸이 비어 있었고 L3의 실제 사거리 밖이었습니다. 여왕이 살면 상대 여왕은 r250에 죽으니 여왕 판정으로 이기지만, r499까지 살아남을지는 알 수 없습니다.
- **Default**: 아니오. r61에는 세 칸 모두 상대 사거리 안이었고 북쪽이 그나마 나은 칸이었습니다. 실수는 r60의 분열인데 one20은 그걸 건드리지 않습니다(`QS_SHED_MAX` 9는 길이 10 이상 여왕만 막음).
- **Tower Defense**: 그 죽음은 아마 피했을 겁니다(남쪽 (14,2)에 진주가 있었고 가까운 두 머리의 실제 사거리 밖). 승패는 알 수 없습니다. r100에 드래곤이 3 대 14였습니다.

턴별 기록과 7x7 판면은 `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/skku-opus/last.txt`에 있습니다.
