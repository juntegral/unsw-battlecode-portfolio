"""Tables and code-geometry diagnoses, without claiming unseen score traces."""
import sys
sys.dont_write_bytecode=True
import json
import csv
from collections import Counter
from datetime import datetime
import analyze as a

def agg(rows):
    return dict(n=len(rows),status=dict(Counter(r['status'] for r in rows)),
                lost=sum(r['victim_impact_length'] for r in rows),
                last_pearls=sum(r.get('turn',{}).get('ate',0) for r in rows),
                last_eating_turns=sum(r.get('turn',{}).get('ate',0)>0 for r in rows),
                previous2_pearls=sum(r.get('pearls_two_turns',0) for r in rows),
                complete5=sum(r['complete5'] for r in rows),
                drop5={s:sum(r['recovered5'][s] for r in rows) for s in ('us','them')},
                drops=len([p for r in rows for p in r['drops']]),
                eventual_eaters=dict(Counter(p['eater'] for r in rows for p in r['drops'])),
                action=dict(Counter(r.get('turn',{}).get('kind') for r in rows)),
                blind=dict(Counter(r.get('threat_blind_kind') for r in rows)),
                distances=dict(Counter(r.get('distance') for r in rows)),
                lengths=dict(Counter(f'{r.get("victim_length")}/{r.get("attacker_length")}' for r in rows)),
                single_free_escape=sum(any(len(op['path'])==1 for op in r.get('safe',[])) for r in rows),
                known_escape=sum(bool(r.get('known_safe')) for r in rows),
                outside_initial_attack_range=sum(not r.get('chosen_reachable',True) for r in rows),
                pearl_extended_attacks=sum(r.get('attacker_pearl_extended',False) for r in rows))

def main():
    games=[json.loads(p.read_text()) for p in sorted(a.OUT.glob('verified-*.json'))]
    assert len(games)==45
    code_audits=[]
    for game in games:
        root=a.lr.replay.load(a.ROOT/game['path']).root();g=a.Geo(root.text(0))
        initial=[]
        for line in root.text(0).splitlines():
            q=line.split()
            if q and q[0]=='DRAGON': initial.append(int(q[1]))
        qids=[initial.index(s) for s in (0,1)]
        for row in game['rows']:
            if row['status']=='not seen' or row['side']!='us':continue
            bs={i:tuple(tuple(c) for c in b) for i,s,b in row['start_bodies']};ts={i:s for i,s,b in row['start_bodies']}
            v=row['victim'];head=bs[v][0];L=row['victim_length'];first=tuple(row['first_step']) if row['first_step'] else None
            enemies=[i for i in bs if ts[i]!='us' and g.visible(bs[i][0],head)]
            allies=[i for i in bs if i!=v and ts[i]=='us' and g.visible(bs[i][0],head)]
            defense=False
            for i in enemies:
                eh=bs[i][0]
                for j in allies:
                    ah=bs[j][0];ds=g.distances_to(ah)
                    dx,dy=abs(ah[0]-eh[0]),abs(ah[1]-eh[1])
                    man=min(dx,g.w-dx)+min(dy,g.h-dy)
                    if j in qids and ds.get(eh,99999)<=3: defense=True
                    if sum(g.visible(c,head) for c in bs[j])>=10 and man<=6: defense=True
            nontrader=L<=4 and row['local_outnumbered'] and not defense
            rammer_penalty=0.0 if not row['first_attacker_adjacent'] or row['attacker_parts']>=5 else 450*max(.5,L/4)
            row.update(defense_target_geometry=defense,nontrader_certified=nontrader,
                       first_pearl=first in set(tuple(c) for c in row['start_pearls']) if first else False,
                       rammer_first_penalty_if_nontrader=rammer_penalty)
            row['card_strong_cost']=max(0,row['turn']['ate']-max((o['ate'] for o in row['terrain_safe_all']),default=0))
            row['card_observable_cost']=max(0,row['turn']['ate']-max((o['ate'] for o in row['view_certified_all']),default=0))
            code_audits.append(dict(gid=row['gid'],round=row['round'],victim=v,attacker=row['attacker'],status=row['status'],
                                    locally_outnumbered=row['local_outnumbered'],nontrader_certified=nontrader,
                                    defense_target_geometry=defense,first_pearl=row['first_pearl'],
                                    rammer_first_penalty_if_nontrader=rammer_penalty))
    rows=[r for game in games for r in game['rows']]
    summary=dict(time=datetime.now().astimezone().isoformat(),games=len(games),rows=len(rows),sets={},cards={},avoidables={})
    for label in a.LABELS:
        summary['sets'][label]={s:agg([r for r in rows if r['label']==label and r['side']==s]) for s in ('us','them')}
        summary['avoidables'][label]=agg([r for r in rows if r['label']==label and r['side']=='us' and r['status']=='avoidable'])
        cr=[r for r in rows if r['label']==label and r['side']=='us' and r.get('card_strong')]
        known=[r for r in cr if r.get('card_observable')]
        summary['cards'][label]=dict(terrain=agg(cr),observable=agg(known),terrain_cost=sum(r['card_strong_cost'] for r in cr),
                                     observable_cost=sum(r['card_observable_cost'] for r in known),
                                     games=len(set(r['gid'] for r in cr)),observable_games=len(set(r['gid'] for r in known)),
                                     nontrader=sum(r['nontrader_certified'] for r in cr),
                                     zero_rammer_penalty=sum(r['nontrader_certified'] and r['rammer_first_penalty_if_nontrader']==0 for r in cr),
                                     first_food=sum(r['first_pearl'] for r in cr),
                                     selected_ids=[r['collision'] for r in cr],observable_ids=[r['collision'] for r in known])
    summary['code_avoidable_one5']=dict(Counter(
        'outnumbered nontrader; rammer unpriced' if r['nontrader_certified'] and r['rammer_first_penalty_if_nontrader']==0 else
        'outnumbered nontrader; one-step rammer penalty' if r['nontrader_certified'] else
        'trader status not resolved' for r in rows if r['label'].startswith('one5') and r['side']=='us' and r['status']=='avoidable' and r['victim_length']<=4))
    (a.OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    (a.OUT/'audited-collisions.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
    with (a.OUT/'code-audit.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(code_audits[0]));w.writeheader();w.writerows(code_audits)
    with (a.OUT/'drops.csv').open('w') as f:
        ps=[dict(collision=r['collision'],avoidable=r['status']=='avoidable',label=r['label'],victim_side=r['side'],**p) for r in rows for p in r['drops']]
        w=csv.DictWriter(f,fieldnames=list(ps[0]));w.writeheader();w.writerows(ps)
    tables=['[M] r0–200 비여왕 피격 전수. 대안은 무료 1..ceil(L/4) 걸음, 기본 적 질주 예산 ceil(L/4)+L−2.',
            '', '| 집단 | 피격 편 | 전체 | 회피 대안 | 대안 미확인 | 머리 미관측 |', '|---|---|---:|---:|---:|---:|']
    for label in a.LABELS:
        for side in ('us','them'):
            z=summary['sets'][label][side];ss=z['status']
            tables.append(f'| {label} | {side} | {z["n"]} | {ss.get("avoidable",0)} | {ss.get("not avoidable",0)} | {ss.get("not seen",0)} |')
    tables+=['','[M] 우리 회피 대안 사건의 실제 섭취·회수. 양쪽 시체 진주 합산; 회수는 r+5까지.',
             '', '| 집단 | 사건 | 직전 차례 섭취 | 두 차례 섭취 | 낙하 | 5R 우리/상대 | 마지막까지 우리/상대/잔류 | 완결 5R |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for label in a.LABELS:
        z=summary['avoidables'][label];e=z['eventual_eaters'];dr=z['drop5']
        tables.append(f'| {label} | {z["n"]} | {z["last_pearls"]} | {z["previous2_pearls"]} | {z["drops"]} | {dr["us"]}/{dr["them"]} | {e.get("us",0)}/{e.get("them",0)}/{e.get("nobody",0)} | {z["complete5"]} |')
    tables+=['','[M] 카드가 표시하는 기존 피격 차례. 필터: L≤4, 자기 포함 시야 머릿수 열세, 확인된 적 길이≥L, 아군이 충돌점에 더 가깝지 않음, 실제 MOVE 종점이 공격자 기본 도달 안.',
             '', '| 집단 | 지형만으로도 적 전체 기본예산 밖 대안 | 해당 경기 | 시야만으로 확정한 대안 | 해당 경기 | 각각 즉시 진주 손실 |', '|---|---:|---:|---:|---:|---:|']
    for label in a.LABELS:
        c=summary['cards'][label]
        tables.append(f'| {label} | {c["terrain"]["n"]} | {c["games"]} | {c["observable"]["n"]} | {c["observable_games"]} | {c["terrain_cost"]}/{c["observable_cost"]} |')
    tables+=['','[M] 직전 거리·길이 조합, 무료/유료 도달 예산, 선택 이동·대안·진주 원장은 `collisions.csv`, `audited-collisions.json`, `drops.csv`에 있다. 이하 전체 빈도는 `summary.json`에 보존한다.']
    (a.OUT/'tables.md').write_text('\n'.join(tables)+'\n')
    print(json.dumps(summary['cards'],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
