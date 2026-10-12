import json,statistics
from pathlib import Path
from collections import defaultdict,Counter
P=Path('data/analysis/ladder/dossier');W=P/'work'
top_sides={r['game']:r['our_side'] for r in (json.loads(x) for x in (P/'target/per-game-top1.jsonl').open()) if r['relation']=='us'}
rows=[]
for i in range(4):
    status=json.loads((W/f'lr_status-{i}.json').read_text())
    assert not status['bad'],status
    rows.extend(json.loads(x) for x in (W/f'lr_events-{i}.jsonl').open())
for r in rows:
    if r['source']=='top1':
        meta=json.loads((Path('data/online/top1')/str(r['battle'])/f"game-{r['game']}.json").read_text())
        expected_side=top_sides[r['game']]
        assert meta['team'+expected_side+'Id']==306,(r['game'],expected_side)
assert len(rows)==1097 and len({(r['source'],r['game']) for r in rows})==1097
G=defaultdict(list);games=Counter()
for r in rows:
    groups=['Top1'] if r['source']=='top1' else ['Us','Opp2100+' if r['rating']>=2100 else 'OtherOpp']
    for g in groups:games[g]+=1
    for h in r['hos']:
        if not h['cross'] or not 0<=h['r']<=499:continue
        g='Top1' if r['source']=='top1' and h['ms']==0 else None
        if r['source']=='main':g='Us' if h['ms']==0 else ('Opp2100+' if r['rating']>=2100 else 'OtherOpp')
        if g is None:continue
        typ='Long' if h['L0']>=5 and 2*h['Lv']<h['L0'] else 'Equal'
        assert typ=='Long' or 2<=h['L0']<=4 and h['Lv']==h['L0']
        G[g,typ].append(h)
old=Counter()
for p in W.glob('at_scan-[0-4].jsonl'):
    for x in p.open():
        r=json.loads(x)
        for h in r['hos']:
            if h['cross'] and 0<=h['r']<=499 and ((h['L0']>=5 and 2*h['Lv']<h['L0']) or (2<=h['L0']<=4 and h['Lv']==h['L0'])):
                g='Us' if h['ms']==0 else ('Opp2100+' if r['rating']>=2100 else 'OtherOpp');typ='Long' if h['L0']>=5 else 'Equal';old[g,typ]+=1
for k,n in old.items():assert len(G[k])==n,(k,n,len(G[k]))

def med(a):return statistics.median(a) if a else None
def mean(a):return statistics.mean(a) if a else None
summary=[]
for g in ('Opp2100+','OtherOpp','Us','Top1'):
    for typ in ('Long','Equal'):
        hs=G[g,typ];n=len(hs);full=[h for h in hs if h['net15'] is not None];alive=[h for h in hs if h['qalive']];hist=[h for h in alive if h['history_n']==2]
        c=dict(group=g,type=typ,games=games[g],n=n,band=[sum(a<=h['r']<=b for h in hs) for a,b in ((0,100),(101,300),(301,499))],
            band_medians=[[med([h[k] for h in hs if a<=h['r']<=b]) for k in ('L0','Lv')] for a,b in ((0,100),(101,300),(301,499))],
            median_lengths=[med([h[k] for h in hs]) for k in ('L0','Lv')],longest=sum(h['mtop'] for h in hs),queen=sum(h['mq'] for h in hs),
            queen_alive=len(alive),queen_dead=n-len(alive),queen_distance=[sum(h['qdist'] is not None and a<=h['qdist']<=b for h in alive) for a,b in ((0,3),(4,8),(9,10**9))],queen_unreachable=sum(h['qdist'] is None for h in alive),
            history2=len(hist),toward_any=sum(h['toward_any'] for h in hist),toward_both=sum(h['toward_both'] for h in hist),
            victim_big=sum(h['victim_big'] for h in hs),victim_queen=sum(h['victim_queen'] for h in hs),
            sweep3_mean=mean([h['sweep3'] for h in hs]),sweep3_bins=[sum(lo<=h['sweep3']<=hi for h in hs) for lo,hi in ((0,0),(1,1),(2,10**9))],
            free_start=sum(h['open_start']>0 for h in hs),free_impact=sum(h['open_impact']>0 for h in hs),first_start=sum(h['first_start'] for h in hs),first_impact=sum(h['first_impact'] for h in hs),
            full=len(full),censored=n-len(full),drop_all=[sum(h[k] for h in hs) for k in ('dm','dv')],drop_full=[sum(h[k] for h in full) for k in ('dm','dv')],
            eaten=[sum(h['mm']+h['vm'] for h in full),sum(h['mv']+h['vv'] for h in full)],
            eaten_origin=[[sum(h[k] for h in full) for k in ('mm','mv')],[sum(h[k] for h in full) for k in ('vm','vv')]],
            net15=[mean([h['net15'][s] for h in full]) for s in (0,1)],
            collision_account=[mean([-h['Ld']+h['mm']+h['vm'] for h in full]),mean([-h['Lv']+h['mv']+h['vv'] for h in full])])
        assert sum(c['eaten'])<=sum(c['drop_full'])
        summary.append(c)
(W/'lr_summary.json').write_text(json.dumps({'games':dict(games),'groups':summary,'validation':{'games':1097,'main_existing_matches':500,'errors':0}},indent=2)+'\n')
print(json.dumps(summary,indent=2))
