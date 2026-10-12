# Reports sent to the lead by unD-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:56:36 — Heads-up: cliff at QUEEN_MIN_CELLS 600

ud heads-up: possible cliff at QUEEN_MIN_CELLS = 600 (main.cpp:208, is_queen() line 5682), bad side = 600 cells or fewer. One pair so far, not yet isolated.
[M] mD17 v m3base, un_queen600_1 (24x25 = 600): lost BOTH seats by elimination (r158, r135; our dragons at r100 10 and 16 against 59 and 52; our queen dead r86 rammed / r28 she rammed their queen). un_queen600_2 (24x26 = 624, one row more): won BOTH seats by elimination (r84, r78; dragons at r100 61 and 59 against 0; queen alive). Now building arms that move only that constant (ud_q0 = one17 + QUEEN_MIN_CELLS:0 on the 600 map, ud_q624 on the 624 map) to see if the result flips with the constant; result in about 5 minutes. Do not act on this yet.

---

## 2026-10-09 05:00:59 — Correction: QUEEN_MIN_CELLS is not the cause

ud correction: QUEEN_MIN_CELLS is NOT the cause of the 600/624 gap. Do not change it.
[M] ud_q0 (one17 + QUEEN_MIN_CELLS:0) on un_queen600_1 both seats, and ud_q624 (QUEEN_MIN_CELLS:624) on un_queen600_2 seat 1, play the same games as mD17 (same result line, same rounds, every health number equal, replay size differs only by the bot-name length). So our side of that threshold is inert here; the gap between the two maps comes from the opponent (m3base carries the same constant) or from the extra row. No constant change from this pair. Continuing with center700 / center1000 / aggressive1200 pairs and the seat comparison.

---

## 2026-10-09 05:14:22 — ud final: no constant change justified

ud FINAL: NO constant change is justified. No crash/timeout/illegal marker, no loop above 1.0 percent, first eat r0-r12 on every map that has pearls. 36 of 66 games played (18 maps, all under 2000 cells); 15 maps NOT run (aspect x2, timers, width64 and everything of 4096 cells or more, so the cells4096/4097 pair is unanswered); no mirror games.
One thing to know, not to act on: CENTER_SMALL_CELLS 700 -> 699 flips ONE game (un_center700_1 seat 1) from loss to win. n = 1, the other seat on the same map wins as is, and that constant also governs the 512-700 cell ladder maps, which I did not test.

All [M], mD17 v m3base, seed 1. us pearls by r100 / our dragons at r100 (their dragons), result. Every map here has ONE starter per side except startlayout.
map (cells)          seat 0                      seat 1
queen600_1 (600)     360/10 (59) L elim r158     497/16 (52) L elim r135
queen600_2 (624)     576/61 (0)  W elim r84      517/59 (0)  W elim r78
center700_1 (700)    785/64 (1)  W elim r101     358/14 (61) L elim r403
center700_2 (728)    692/61 (0)  W elim r86      881/64 (1)  W elim r117
center1000_1 (1000)  758/60 (60) W longest       703/63 (60) W longest
center1000_2 (1020)  710/60 (59) W longest       811/60 (60) W longest
aggressive1200_1     803/61 (60) W longest       815/60 (60) L longest 87 v 119
aggressive1200_2     782/62 (61) W longest       833/61 (62) L longest 26 v 51
symmetry_1 (x)       511/30 (59) L longest       774/63 (0)  W elim r96
symmetry_2 (y)       619/51 (37) W elim r348     535/27 (57) W elim r353
symmetry_3 (xy)      693/50 (38) W elim r181     829/62 (10) W elim r155
symmetry_4 (none)    436/60 (7)  W elim r128     166/3 (59)  L elim r170
startlength_1 (512)  313/8 (58)  L elim r127     545/60 (1)  W elim r103
edgewrap_1 (256)     261/53 (0)  W elim r91      282/48 (2)  W elim r104
portalonly_1 (512)   1766/57 (54) L longest      1687/60 (56) L longest
startlayout_1 (256)  0 eats, W queen 3 v 2       0 eats, L queen 2 v 3
portalid_1 and _2    W r0 (they ram our split queen, our half survives)   draw r0 (they move first and ram our L4 queen)

Cliffs:
- queen600 (QUEEN_MIN_CELLS, main.cpp:208, is_queen() 5682): the gap is real in the table but NOT ours. ud_q0 (one17 + QUEEN_MIN_CELLS:0) on the 600 map both seats and ud_q624 on the 624 map seat 1 replay the same games as mD17 (every health number equal, replay size differs only by the bot-name length). [E] the gap is m3base's own copy of the constant or the extra row.
- center700 (CENTER_SMALL_CELLS, main.cpp:429, center_map line 612): ud_c699 on un_center700_1 seat 1 = win by elimination r97, 764 pearls, 62 dragons at r100, against mD17's loss r403 (358, 14). One game, one seat. Not isolated further.
- center1000 and aggressive1200: no jump in pearls or dragons across the threshold; the two 1200-side losses are on longest dragon with dragon counts level, one on each side of the threshold.
Seat / asymmetry: no seat effect of ours. symmetry_1: seat A loses under BOTH bots (us r499, m3base r96). symmetry_4: the side that starts L2 against L4 loses under both bots (this is the only line that meets the RED rule "3 dragons at r100 against 59", and it is the map's unequal start). startlayout_1: the map file has no pearl tile, nobody eats in 500 rounds, the longer starting queen wins under both bots.

Not RED by the brief's rule but worth one look after the deadline: with a single starter our queen is dead before r50 in 11 of the 32 games outside portalid, always by a ram, never wall / own body / mate; in 3 of them SHE hit the enemy queen's head (queen600_1 s1 r28, symmetry_1 s1 r30, portalonly_1 s1 r20; results L, W, L). Code path not traced. No ladder map has a single starter.
What would show this wrong: the 15 unplayed maps, more seeds on center700_1, ud_c699 on Stripes / Tower Defense / Devil / Portals / weakhold / Trophy.
Where: runs ~/meow-redteam/solo/runs/ud_mD17, ud_q0, ud_q624, ud_c699; tables ROOT/data/codex/astra/unD-opus/health-*.jsonl (script health.py); maps ~/meow-redteam/maps/un2/ud_un_*.map; bots solo/bots/ud_q0, ud_q624, ud_c699. A few queued games of mine may still be finishing; I started nothing new after 14:09.

---

## 2026-10-09 05:14:22 — closing summary

리드에게 최종 보고를 보냈습니다. 결론: **마지막 30분에 상수를 바꿀 근거는 없습니다.**

- **진행 범위**: 66판 중 36판(2000칸 미만 18개 지도, 양쪽 좌석, 상대 m3base)만 돌렸습니다. 4096칸 이상 전부와 aspect·timers·width64 등 15개 지도는 못 돌렸고, 그래서 cells4096/4097 쌍은 답이 없습니다. 미러전도 없습니다.
- **건강 지표**: 돌린 판에서는 크래시·타임아웃·불법 행동 표시가 없고, 루프는 최대 1.0%, 첫 먹이는 r0~r12입니다(진주가 아예 없는 startlayout_1 제외).
- **queen600 절벽**: 600칸에서는 양쪽 좌석 모두 전멸패, 624칸에서는 양쪽 모두 전멸승으로 차이는 큽니다. 하지만 우리 쪽 `QUEEN_MIN_CELLS`를 0이나 624로 옮긴 빌드가 mD17과 같은 경기를 그대로 재현해서, 우리 상수 탓은 아닙니다. 처음에 리드에게 절벽 의심으로 알렸다가 바로 정정했습니다.
- **center700**: `CENTER_SMALL_CELLS`를 700에서 699로 옮기면 un_center700_1 좌석 1 한 판이 패(r403 전멸)에서 승(r97 전멸)으로 뒤집힙니다. 다만 한 판·한 좌석뿐이고, 같은 지도 좌석 0은 지금 값으로 이깁니다. 이 상수는 512~700칸 래더 지도에도 걸리는데 거기서는 검증하지 못했으니, 참고용이지 바꿀 근거는 아닙니다.
- **center1000, aggressive1200**: 경계 양쪽에서 진주·드래곤 수에 점프가 없습니다.
- **좌석 효과**: 우리 봇 고유의 좌석 효과는 없습니다. symmetry_1은 두 봇 모두 A석이 지고, symmetry_4는 L2로 시작하는 쪽이 두 봇 모두 집니다. startlayout_1은 진주 타일이 없어 시작 여왕 길이로 승부가 납니다.
- **마감 뒤 볼 만한 것**: 시작 드래곤이 1마리인 지도에서 우리 여왕이 r50 전에 죽은 판이 32판 중 11판이고, 전부 박치기입니다. 그중 3판은 여왕이 직접 상대 여왕 머리를 받았습니다. 코드 경로는 추적하지 못했고, 래더에는 시작 1마리 지도가 없습니다.

산출물 위치:
- 경기 기록: `~/meow-redteam/solo/runs/ud_mD17`, `ud_q0`, `ud_q624`, `ud_c699`
- 표와 스크립트: `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unD-opus/` (`health-*.jsonl`, `health.py`)
- 지도 복사본: `~/meow-redteam/maps/un2/ud_un_*.map`
- 비교용 봇: `~/meow-redteam/solo/bots/ud_q0`, `ud_q624`, `ud_c699`

봇 코드, git, 업로드는 건드리지 않았습니다.
