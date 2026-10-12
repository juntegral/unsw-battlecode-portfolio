import sys
sys.dont_write_bytecode=True
import json,re
from pathlib import Path
O=Path(__file__).resolve().parent
summary=json.loads((O/'summary.json').read_text())['groups'];inv=json.loads((O/'inventory.json').read_text());val=json.loads((O/'validation.json').read_text())
assert len(inv['games'])==len(val['checks'])==209
assert sum(x['all_dragon_log_events'] for x in val['checks'])==0
lines=[
'[M] 같은 상대·지도·좌석 30쌍에서 one7→one8 비여왕 피격이 4.025→3.301/1,000턴으로 감소했다. [E] SMALL_SPRINT_THREAT를 포함한 변경 묶음의 개선이며 단독효과는 미분리다.',
'[M] one9/10 여왕 사망 21건의 최대군은 **출구 막힘 10건**, 다음은 미관측 피격 6건이다. 희생 카드 대상은 이 중 5건이다.',
'[M] 2026-10-09 04:58:39 KST 인벤토리 209판, 중복 134건 제외, 리플레이 봇 ID 확인. [E] 집계 확신은 높고 개별 스위치 판정은 잠정이다.',
'',
'[M] 벡터는 **한무료/여러무료/유료/경로상섭취/몸잘림/미관측** 피격률이다. 앞 3열은 배타적, 뒤 3열은 중복이다. N=비여왕, Q=여왕, S=길이≤4 비여왕. 비용은 S/Q 진주·턴, 생존턴 Q길이 P25/50/75/90, 보이는 먹이까지 거리가 줄지 않은 Q턴 비율이다.',
'',
'| 대상 | [M] 피격/1,000턴 또는 결정 수치 | 비용·판정·기보 근거 |',
'|---|---|---|'
]
for v in (5,7,8,9,10):
 x=summary[f'one{v}'];c=x['counts'];fmt=lambda kind:'/'.join(f"{x['ram_rates'][kind][k]:.3f}" for k in ('one_free','several_free','paid','pearls_on_way','view_cut','unseen'))
 q=x['queen_length_quantiles'];qs='/'.join(map(str,q[1:]))
 lines.append(f"| [M] one{v}: {x['games']}판; N/Q턴 {c['other_turns']:,}/{c['queen_turns']:,} | N {fmt('other')}<br>Q {fmt('q')} | {x['short_pearls_per_turn']:.4f}/{x['queen_pearls_per_turn']:.4f}; {qs}; {100*x['queen_not_toward_food_fraction']:.1f}% |")
lines += [
'| SMALL_SPRINT_THREAT | 같은 30쌍, 짧은 용의 보이는 소형적 다중걸음 피격 2.184→1.651/S천턴 | [E] **works**, 묶음 기준. [C] one10:3421–3480. [M] 1480436:r41,1484435:r78 |',
'| SHORT_EVADE, PAID=1 | kraken 15쌍, 관측가능 조건군 피격 1.398→0.897/S천턴 | [E] **works**, REACH_EATS와 미분리. [C] one10:787–865. [M] 1485174:r33,1487479:r239 |',
'| REACH_EATS | 같은 15쌍, 보이는 적의 진주섭취 여왕 피격 3→0 | [E] **works**, 잠정. [C] one10:5431–5462. [M] 이전 1485179:r34,1485182:r335 |',
'| CUT_BODY_LEN=4 / QS_PAY_REACH=4 | 잘린 몸의 Q피격 1→0; 이전 1건은 시야테두리 접촉조차 없음 | [E] **nothing**: 단독효과 입증부족. [C] one10:5339–5349. [M] 1487475:r19; 잔존 유료피격 1489832:r87 |',
'| QUEEN_PORTAL_ALL | 직접 관측이력에 없는 출구 진입 4→0; one10 기회 22턴 | [E] **works**, 잠정. [C] one10:5141–5148. [M] 1487476:r154,157; 네 진입 모두 +5라운드 생존 |',
'| QUEEN_EXIT_KEEP | 외길 5건에서 차단 아군 +5라운드 생존, Q는 다음 라운드 사망 | [E] **nothing**, 이 실패군에서. [C] one10:932–960. [M] 1487484:r105–106,1489831:r217–218 |',
'| QUEEN_DEAD_ALL | one9/10 각각 막힘 사망 5건 | [E] **nothing**, 이 실패군에서. [C] one10:4778,6738–6747. [M] 1487476:r196,1489834:r456 |',
'| [M] 남은 Q사망: one9 / one10 | 막힘 5/5; 미관측 3/3; 보이는 유료 1/1; 몸잘림 1/0; 한무료 1/0; 자기돌진 1/0 | 합계 12/9. 미관측 중 1489836:r126은 Q턴 뒤 분열한 새끼. [전체 21건](queen-deaths.json) |',
'',
'[M] **실제 행동 변경 횟수·변경 후 5라운드 결과는 모든 스위치에서 NA**다. dragonLog가 0개이고 개입 전 제안·메모리·점수가 없다. [C] 조건은 [재구성 방법](methods.md)에 명시했다. [M] 게이트 후속결과는 [별도 원자료](feature-observations.json)이며 개입횟수가 아니다. [E] works는 작동 정황, nothing은 명시한 실패군/증거부족 판정이며 인과 결론이 아니다.',
'',
'[E] **카드 하나:** 비여왕 아군이 보이는 Q의 유일한 출구를 막게 되고, 출구를 남기는 이동·분열이 없으며, 알려진 옆벽에 죽으면 출구가 남을 때 벽으로 한 걸음 간다. [C] one5:586 직전 최종검사로 추가; one10 QUEEN_EXIT_KEEP는 벽 죽음을 대안에서 제외한다(:939–943), 기존 상수로 해결되지 않는다. [M] 해당 5건 중 one10 1489831:r217,1489842:r41,1489845:r215. [E] 검증은 이 5상태의 차단 5→0 및 Q의 +5라운드 생존; 생존 대안이 있는데 희생하거나 Q가 계속 죽으면 반증이다. 실제 구제·섭취 손실은 미실험이다.',
'',
'[M] 원자료: [집계](summary.json), [동일조건 비교·부트스트랩](matched.json), [교차검증](validation.json). [E] one7→8 비여왕 차이 95% 구간 −1.779~−0.061/천턴은 변경 묶음에만 해당한다. 비용도 버전간 관측치다. 시드·동시변경의 교란과 미지지도 일반화는 미검증이다.'
]
lines[:3]=[x+'  ' for x in lines[:3]]
report='\n'.join(lines)+'\n';(O/'report.md').write_text(report)
print('words whitespace',len(report.split()),'table separators',sum(line.startswith('|---') for line in lines))
