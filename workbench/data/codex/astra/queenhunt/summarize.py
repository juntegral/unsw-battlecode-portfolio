import sys
sys.dont_write_bytecode=True
import json,csv
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean,median
OUT=Path(__file__).resolve().parent
G=[json.loads(s) for s in (OUT/'games.jsonl').read_text().splitlines()]

def write_csv(name,rows):
    if not rows:return
    with (OUT/name).open('w') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)

def avg(xs):return round(mean(xs),2) if xs else None
def med(xs):return median(xs) if xs else None
def hh(g,s):return [h for h in g['hunters'][s] if not h['queen']]
groups=defaultdict(list)
for g in G:groups[g['group']].append(g)
online=[]
for group,gs in groups.items():
    if gs[0]['kind']!='online':continue
    ss=[s for g in gs for s in g['samples'] if s['alive'] and s['round']>0]
    deaths=[g['qdeaths'][0] for g in gs if g['qdeaths'][0] and g['qdeaths'][0]['rammed']]
    row=dict(group=group,games=len(gs),enemy_queen_alive_end=sum(g['final'][1]['queen_length']>0 for g in gs),
        lost_own_dead_enemy_alive=sum(g['result']=='loss' and not g['final'][0]['queen_length'] and g['final'][1]['queen_length']>0 for g in gs),
        alive_samples=len(ss),reachable_samples=sum(s['distance'] is not None for s in ss),
        distance_median=med([s['distance'] for s in ss if s['distance'] is not None]),
        length_median=med([s['length'] for s in ss]),mates5_mean=avg([s['mates5'] for s in ss]),
        distance_le8=sum(s['distance'] is not None and s['distance']<=8 for s in ss),
        home=sum(s['location']=='home' for s in ss),swarm=sum(s['location']=='swarm' for s in ss),
        front=sum(s['location']=='front' for s in ss),isolated=sum(s['location']=='isolated' for s in ss),
        own_queen_rammed=len(deaths),rammer_approach=sum(d['classification']=='approach' for d in deaths),
        rammer_no_far_evidence=sum(d['classification']=='no_far_approach' for d in deaths),
        rammer_short_history=sum(d['classification']=='insufficient_history' for d in deaths),
        opponent_approach_ids_mean=avg([len(hh(g,1)) for g in gs]),own_approach_ids_mean=avg([len(hh(g,0)) for g in gs]))
    online.append(row)
write_csv('online-summary.csv',online)

prices=[]
for g in G:
    if g['kind']!='local':continue
    s=1 if g['group'].endswith('_vh') else 0
    d=g['qdeaths'][1-s];hs=hh(g,s);turns=[t for h in hs for t in h['turns']]
    row=dict(arm=g['group'],game=g['game'],opponent=g['opponent_bot'],our_queen_death=(g['qdeaths'][0] or {}).get('round'),
        enemy_queen_death=(g['qdeaths'][1] or {}).get('round'),target_rammed=bool(d and d['rammed']),
        target_killer=(d or {}).get('actor'),approach_ids=len(hs),approach_turns=len(turns),
        approach_eats=sum(t['eats'] for t in turns),approach_no_eat_turns=sum(t['eats']==0 for t in turns),
        approach_ids_dead=sum(h['death'] is not None for h in hs),
        approach_ids_dead_by_target_death=sum(h['death'] is not None and d is not None and h['death']['round']<=d['round'] for h in hs),
        our_r100_count=g['snaps']['100'][0]['alive'] if g['snaps']['100'] else None,
        their_r100_count=g['snaps']['100'][1]['alive'] if g['snaps']['100'] else None,
        our_r100_total=g['snaps']['100'][0]['total'] if g['snaps']['100'] else None,
        our_r300_count=g['snaps']['300'][0]['alive'] if g['snaps']['300'] else None,
        our_r300_total=g['snaps']['300'][0]['total'] if g['snaps']['300'] else None,
        result=g['result'],how=g['how'],last=g['last'])
    prices.append(row)
write_csv('local-price.csv',prices)
pairs=[]
A={g['game']:g for g in G if g['group']=='mDqh_vb'}
B={g['game']:g for g in G if g['group']=='mDl5_vb'}
for key in sorted(A.keys()&B.keys()):
    a,b=A[key],B[key]
    row=dict(game=key)
    for nm,g in [('hunt',a),('one5',b)]:
        row[nm+'_enemy_queen_death']=(g['qdeaths'][1] or {}).get('round')
        row[nm+'_own_queen_death']=(g['qdeaths'][0] or {}).get('round')
        row[nm+'_result']=g['result'];row[nm+'_how']=g['how'];row[nm+'_last']=g['last']
        for r in ('100','300'):
            z=g['snaps'][r]
            for k in ('alive','total','pearls'):row[nm+'_r'+r+'_'+k]=z[0][k] if z else None
        row[nm+'_final_queen']=g['final'][0]['queen_length']
        row[nm+'_enemy_final_queen']=g['final'][1]['queen_length']
    pairs.append(row)
write_csv('paired.csv',pairs)

out=[]
out+=['[M] 온라인: 살아 있는 상대 여왕의 r10 간격 표본; 거리=최단 지형 경로, 몸통 무시. 위치는 front→home→swarm→isolated 우선순위.\n',
       '|집합|판|종료 생존|거리 중앙|길이 중앙|동료5 평균|home/swarm/front/isolated|우리 여왕 피격: 접근/미검출/이력부족|상대 접근 용/판|',
       '|---|---:|---:|---:|---:|---:|---|---|---:|']
for r in online:
    out.append('|{group}|{games}|{enemy_queen_alive_end}|{distance_median}|{length_median}|{mates5_mean}|{home}/{swarm}/{front}/{isolated}|{rammer_approach}/{rammer_no_far_evidence}/{rammer_short_history}|{opponent_approach_ids_mean}|'.format(**r))
out+=['','[M] m3hunt 가격표: 지정된 세 팔. r100은 도달한 판만; 접근 용은 행동 대용지표.\n',
      '|팔|판|우리 여왕 피격사(≤r100)|피격 r 중앙(범위)|r100 도달|m3hunt/우리 용 수 평균|접근 용/판|접근 용 사망/판|접근 무섭취 턴/전체|',
      '|---|---:|---:|---|---:|---|---:|---:|---|']
for arm in ['mDo5_vh','m8o2_vh','m9f3_vh']:
    gs=groups[arm];ps=[p for p in prices if p['arm']==arm];ds=[g['qdeaths'][0]['round'] for g in gs if g['qdeaths'][0] and g['qdeaths'][0]['rammed']]
    reached=[g for g in gs if g['snaps']['100']]
    out.append(f"|{arm}|{len(gs)}|{sum(p['target_rammed'] for p in ps)} ({sum(r<=100 for r in ds)})|{med(ds)} ({min(ds)}–{max(ds)})|{len(reached)}|{avg([g['snaps']['100'][1]['alive'] for g in reached])}/{avg([g['snaps']['100'][0]['alive'] for g in reached])}|{avg([p['approach_ids'] for p in ps])}|{avg([p['approach_ids_dead'] for p in ps])}|{sum(p['approach_no_eat_turns'] for p in ps)}/{sum(p['approach_turns'] for p in ps)}|")
out+=['','[M] 동일 지도·시드·진영의 사냥/one5 비교. `—`는 해당 라운드 전에 종료. 판정은 승패 기록이며 채택 근거가 아님.\n',
      '|게임(seed1)|상대 여왕 사망 r 사냥/one5|판정 사냥/one5|r100 우리 수·길이 사냥/one5|r300 우리 수·길이 사냥/one5|',
      '|---|---|---|---|---|']
for r in pairs:
    def st(nm,round):
        n=r[nm+'_r'+round+'_alive'];t=r[nm+'_r'+round+'_total']
        return '—' if n is None else f'{n}·{t}'
    out.append(f"|{r['game'].replace('-seed1','')}|{r['hunt_enemy_queen_death']}/{r['one5_enemy_queen_death']}|{r['hunt_result']}·{r['hunt_how']}/{r['one5_result']}·{r['one5_how']}|{st('hunt','100')}/{st('one5','100')}|{st('hunt','300')}/{st('one5','300')}|")
(OUT/'tables.md').write_text('\n'.join(out)+'\n')
print('\n'.join(out))
print('online games',sum(g['kind']=='online' for g in G),'paired',len(pairs),'unpaired',sorted(A.keys()^B.keys()))
