"""Publish the compact report, full definitions and final per-event ledger."""
import sys
sys.dont_write_bytecode=True
import json
import csv
import hashlib
from collections import Counter
from datetime import datetime
import analyze as a

def main():
    rows=json.loads((a.OUT/'audited-collisions.json').read_text())
    ext={r['collision']:r for r in json.loads((a.OUT/'extended.json').read_text())}
    know={r['collision']:r for r in json.loads((a.OUT/'knowledge-sensitivity.json').read_text())}
    assert len(rows)==len(ext)==1328
    final={}
    for label in a.LABELS:
        final[label]={}
        for side in ('us','them'):
            zz=[r for r in rows if r['label']==label and r['side']==side]
            aa=[r for r in zz if ext[r['collision']]['status']=='avoidable']
            ownps=[p for r in aa for p in r['drops'] if p['dragon']==r['victim']]
            final[label][side]=dict(total=len(zz),basic=dict(Counter(r['status'] for r in zz)),
                                   extended=dict(Counter(ext[r['collision']]['status'] for r in zz)),
                                   avoidable_last_meals=sum(r['turn']['ate'] for r in aa),
                                   avoidable_two_meals=sum(r['pearls_two_turns'] for r in aa),
                                   avoidable_victim_drops=len(ownps),victim_recovered5={s:sum(p['eater']==s and p['wait']<=5 for p in ownps) for s in ('us','them')},
                                   both_recovered5={s:sum(r['recovered5'][s] for r in aa) for s in ('us','them')},
                                   complete5=sum(r['complete5'] for r in aa))
        cr=[r for r in rows if r['label']==label and r['side']=='us' and r['collision'] in know and know[r['collision']]['safe']]
        final[label]['card']=dict(n=len(cr),games=len(set(r['gid'] for r in cr)),
                                  pearls_lost=sum(know[r['collision']]['cost'] for r in cr),
                                  unpriced=sum(r['rammer_first_penalty_if_nontrader']==0 for r in cr),
                                  nontrader=sum(r['nontrader_certified'] for r in cr),ids=[r['collision'] for r in cr])
    now=datetime.now().astimezone().isoformat()
    sha=hashlib.sha256((a.ROOT/'data/online/smoke/one5-bot/main.cpp').read_bytes()).hexdigest()
    assert sha==json.loads((a.OUT/'inventory.json').read_text())['source_sha256']
    (a.OUT/'final-summary.json').write_text(json.dumps(dict(time=now,source_sha256=sha,sets=final),ensure_ascii=False,indent=2))
    ledger=[]
    for r in rows:
        z={k:v for k,v in r.items() if not isinstance(v,(dict,list))}
        z.update(basic_status=r['status'],status=ext[r['collision']]['status'],extended_alternatives=len(ext[r['collision']]['safe']),
                 actual_attack_steps=r['attacking_turn']['used']+1,
                 actual_attack_start_length=r['attacking_turn']['length'],
                 last_action_kind=r.get('turn',{}).get('kind'),last_action_steps=r.get('turn',{}).get('used'),
                 last_action_dirs=json.dumps(r.get('turn',{}).get('dirs')),last_action_pearls=r.get('turn',{}).get('ate'),
                 visible_us=r.get('view',{}).get('us'),visible_them=r.get('view',{}).get('them'),
                 queen_excluded=True,knowledge_card=r['collision'] in know and bool(know[r['collision']]['safe']),
                 knowledge_card_cost=know.get(r['collision'],{}).get('cost'),
                 us_recovered5=r['recovered5']['us'],them_recovered5=r['recovered5']['them'])
        ledger.append(z)
    fields=list(dict.fromkeys(k for z in ledger for k in z))
    with (a.OUT/'collisions.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(ledger)
    counts=['| 집단 | 피격 편 | 전수 | 회피 대안(기본→진주 포함) | 대안 미확인¹ | 미관측² |', '|---|---|---:|---:|---:|---:|']
    meal=['| 집단 | 회피 대안 사건 | 직전/두 차례 섭취 | 우리 시체 진주 | 5R 회수 우리/상대 | 양 시체 5R 회수 우리/상대 |', '|---|---:|---:|---:|---:|---:|']
    cards=['| 집단 | 엄격한 카드 사례/경기 | 즉시 진주 손실 | 공격자 위협 무가격/약한 벌점 |','|---|---:|---:|---:|']
    for label in a.LABELS:
        for side in ('us','them'):
            z=final[label][side];b=z['basic'];e=z['extended']
            counts.append(f'| {label} | {"우리" if side=="us" else "상대"} | {z["total"]} | {b.get("avoidable",0)}→{e.get("avoidable",0)} | {e.get("not avoidable",0)} | {e.get("not seen",0)} |')
        z=final[label]['us'];p=z['victim_recovered5'];both=z['both_recovered5'];c=final[label]['card']
        meal.append(f'| {label} | {z["extended"]["avoidable"]} | {z["avoidable_last_meals"]}/{z["avoidable_two_meals"]} | {z["avoidable_victim_drops"]} | {p["us"]}/{p["them"]} | {both["us"]}/{both["them"]} |')
        cards.append(f'| {label} | {c["n"]}/{c["games"]} | {c["pearls_lost"]} | {c["unpriced"]}/{c["n"]-c["unpriced"]} |')
    report='''[M/C] 발견: one5 비여왕 피격 559건 중 329건에 무료 회피 대안이 있었다. 짧은 용의 유료 질주 위협 누락이 반복된다.
[M/E] 카드: SHORT_EVADE 한 장, 기본 끔으로 기제 시험. 관측만으로 확인한 one5 22차례의 즉시 섭취 비용은 진주 4개다.
[M/E] 확신: 사건·기하 높음(45판 독립 대조), 실제 생존·전략 효과 미검증.

[M] 집계 시각: TIME. 모든 지도·승패 포함, r0–200. 상대 행은 우리가 상대 비여왕을 들이받은 동일 기준선이다.

COUNTS

[M/E] ¹ 무료 이동 종점에 충분한 빈 공간과 고리가 있는 대안을 확인하지 못했다는 뜻이며 절대 불가 증명은 아니다. ² 직전 차례 없음도 포함(우리 one5 4건). 시야·거리·양쪽 길이·행동·대안 전수는 [collisions.csv](collisions.csv), 경로·판면 상태는 [audited-collisions.json](audited-collisions.json)과 [extended.json](extended.json).

[C] `one5-bot/main.cpp:2620–2673,2685–2692`: L≤4는 보이는 몸<5인 적의 한 걸음만 위협으로 쓴다. 몸≥5인 적은 짧은 위협장에서 빠진다. `:1677–1679,4202–4207,4468–4473`의 도달 위험장은 현재 비여왕에게 적용되지 않는다. `:3717–3729`의 `enemy_can_step_to`도 한 걸음뿐이다.

[M/C] 엄격한 22차례 모두 일반 trade 조건(:2831–2844)의 시야 우세가 없고 방어 예외도 없다. 18차례는 공격자가 선택 종점에 두 걸음 떨어져 그 머리의 벌점이 0, 나머지 4차례는 약한 벌점이다. [C] 비리더 L2의 −225(:5773–5786)보다 진주 +300(:111,5729–5732)이 크다. 영토는 칸당 +1.5(:377–378,5644–5649). [E] 실제 승리한 점수 항은 기록이 없어 확정할 수 없다. 무섭지 않게 계산된 적 곁으로 식량·공간 점수가 이동을 허용하는 구조다.

[M] 회피 대안 뒤 낙하와 이전 식사(진주 포함 도달 기준). 우리 시체만 회수한 값과 양 시체 합계를 구분했다. 5R 미완결: one5-c1 1건, one3-w1 2건. 진주별 먹은 용·라운드는 [drops.csv](drops.csv).

MEALS

[E] 카드 규칙: 비여왕 L≤4, 자기 포함 시야 머릿수 열세일 때, 길이가 확인된 동길이 이상 적이 닿는 최종 행동을 거부한다. 알려진 길로 아군이 만남 칸에 더 가까우면 예외다. 시야 안에서 공간·고리가 확인되는 무료 대안이 있을 때만 그 대안 중 섭취가 가장 많은 것을 고른다.

[C/E] 삽입: `act():597–641`과 출력 전 `hunt_path`(:639–646)·`ram_path`(:706–712)에 같은 검문, 종점 선택은 `pick_direction():6065–6089` 확장. `SMALL_SPRINT_THREAT`(:273)을 켜면 L3/4 질주 일부를 반영하지만 여전히 연성 벌점이며 몸≥5인 적을 누락한다. 기존 `SMALL_THREAT_OUTNUMBERED`(:323,5781–5785)는 자기 머리를 포함하지 않는다.

CARDS

[M/E] 위 카드 수는 구현 발동 수가 아니라 현재 사건의 반사실 표본이다. 숨은 지형·진주를 적에게 유리하게 허용하고 몸을 무시해도 22/9차례의 대안은 도달 밖이다. [E] 통과 기준: 표본의 다음 차례까지 노출 감소와 무료 경로·공간 확인, 즉시 진주 손실≤4(one3≤2). 반증: 도달 밖이라 판정한 종점에 피격, 갇힘 증가, 여왕 방어를 건너뛴 새 사망. 전체 발동 차례의 섭취 비용은 미계산이다.

[M] 기보 장면(방향 N/E/S/W)

| 확인 | 경기 r / 우리 또는 상대 피해자←공격자 | 실제 행동·대안·회수 |
|---|---|---|
| 두 걸음 누락 | 1472005 r40 / 우리 #30←#41 | L2/L3, 시야2/4, E로 거리3→2; W는 회피. 두 차례 섭취0. #49가 r45 우리 머리 진주 회수. |
| 두 걸음 누락 | 1472008 r95 / 우리 #27←#26 | L3/L3, 시야2/3, S로 거리3→2; N/E는 회피. 두 차례 섭취1. #33이 r98 우리 머리 진주 회수. |
| 두 걸음 누락 | 1472762 r135 / 우리 #67←#97 | L2/L3, 시야1/2, S로 거리3→2; N/W는 회피. 두 차례 섭취0. #100이 r139 우리 머리 진주 회수. |
| 식사/연성 벌점 | 1472010 r127 / 우리 #74←#63 | L2/L2, W로 진주1 섭취; N은 회피. #41/#75가 r128–129 양 시체 진주3 회수. |
| 식사/연성 벌점 | 1472759 r183 / 우리 #59←#37 | L2/L2, W로 진주1 섭취; S는 회피. #115가 r186–190 양 시체 진주3 회수. |
| 상대 기준선 | 1472004 r69 / 상대 #51←우리 #12 | L2/L3, 상대 시야1/3; S 대신 N 회피 가능. |
| 상대 기준선 | 1472752 r122 / 상대 #16←우리 #57 | L2/L2, 상대 시야1/3; W 대신 N 회피 가능. 우리 진주2 회수≤5R. |
| 미관측 | 1472004 r133 / 우리 #113←#147 | 공격자 머리는 7×7 밖이지만 포털 경로 거리2. |
| 미관측 | 1472753 r68 / 우리 #19←#87 | L2/L2, 머리 (41,15)/(9,49); 시야 밖이지만 포털 경로 거리2. |
| 대안 미확인 | 1472003 r150 / 우리 #79←#98 | L2/L2, 직전 거리2. 공간·고리가 인증되는 무료 종점0. |
| 대안 미확인 | 1472752 r139 / 우리 #71←#47 | L2/L2, 직전 거리2; E 이동. 공간·고리가 인증되는 무료 종점0. |

[E] 미검증: 행동 점수·기억·음파 재실행, 타 용의 후속 이동/사망, 다음 라운드의 새 진주, 패치 대전·CPU·생존 효과. 봇·공용 문서 수정, 대전, 네트워크, 업로드 없음. 상세 정의와 재현은 [methods.md](methods.md).
'''
    report=report.replace('TIME',now).replace('COUNTS','\n'.join(counts)).replace('MEALS','\n'.join(meal)).replace('CARDS','\n'.join(cards))
    (a.OUT/'report.md').write_text(report)
    text='\n'.join(line for line in report.splitlines() if not line.startswith('|'))
    assert len(text.split())<450,len(text.split())
    print('report words excluding tables',len(text.split()))
    print('final',json.dumps(final,ensure_ascii=False))

if __name__=='__main__':main()
