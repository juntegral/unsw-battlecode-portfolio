import sys
sys.dont_write_bytecode=True
import json,csv
from pathlib import Path
from collections import Counter,defaultdict
from statistics import median,mean
OUT=Path('data/codex/astra/rallyloss')
CAUSES=['rammed','rams','wall','own body','mate body','foe body','mate head','stop']
def write(name,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/name).open('w') as f:
        writer=csv.DictWriter(f,fieldnames=keys,delimiter='\t');writer.writeheader()
        writer.writerows({k:json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)
def ledger(g,s,cut=350):
    b=g['base'];start=b['snaps'].get(str(cut),b['ends']);eats=[e for e in b['eats'] if e[1]==s and e[0]>cut];ds=[d for d in b['deaths'] if d[1]==s and d[0]>cut]
    row=dict(label=g['label'],gid=g['gid'],map=g['map'],side='ours' if s==0 else g['opp'],last=g['last'],start=start[s][1],natural=sum(e[3]=='n' for e in eats),mate_corpse=sum(e[3]=='own' for e in eats),enemy_corpse=sum(e[3]=='foe' for e in eats))
    for c in CAUSES:row[c]=sum(d[2] for d in ds if d[4]==c)
    row['paid']=sum(p[3] for p in b['paids'] if p[1]==s and p[0]>cut);row['ours_eaten_enemy']=sum(d[11] for d in ds);row['dead']=sum(d[2] for d in ds);row['end']=b['ends'][s][1]
    row['residual']=row['start']+row['natural']+row['mate_corpse']+row['enemy_corpse']-row['dead']-row['paid']-row['end'];assert row['residual']==0,(g['gid'],s,row)
    return row
def main():
    games=list(map(json.loads,(OUT/'games.jsonl').read_text().splitlines()));assert len({g['gid'] for g in games})==len(games)
    ledgers=[];ledgers400=[];records=[];direct=[];leaders=[];folds=[];checkpoints=[];summary={};moments=[]
    for g in games:
        for s in (0,1):
            ledgers.append(ledger(g,s));ledgers400.append(ledger(g,s,400));meta=dict(label=g['label'],gid=g['gid'],map=g['map'],side=s)
            for r in (350,400,g['last']):checkpoints.append(meta|dict(round=r,**g['snapshots'].get(str(r),g['snapshots'][str(g['last'])])[s]))
        meta=dict(label=g['label'],gid=g['gid'],map=g['map'])
        for c in g['trace']['records']:
            records.append(meta|c)
            if c['kind']=='fold':folds.append(meta|c)
        for t in g['trace']['direct']:
            if t['round']>350:direct.append(meta|t)
        for n,d in enumerate(g['base']['deaths']):
            if d[0]<=350 or not d[3] or d[2]<10:continue
            ident=str(g['deaths'][n]['id']);st=g['all_dragons'][ident]
            leaders.append(meta|dict(side=d[1],round=d[0],id=int(ident),length=d[2],cause=d[4],free=d[5],head=d[20],rammer=d[18],stop_pearls=st['stop_drop'],mate_pearls=st['own_drop'],foe_pearls=st['foe_drop'],reclaimed=d[10],stolen=d[11]))
        for c in g['trace']['records']:
            if c['kind']=='rally-proxy' and c['death']:moments.append(meta|c)
    for label in sorted({g['label'] for g in games}):
        gs=[g for g in games if g['label']==label];ss={}
        for s in (0,1):
            ls=[l for l in ledgers if l['label']==label and (l['side']=='ours')==(s==0)];tot={k:sum(x[k] for x in ls) for k in ['start','natural','mate_corpse','enemy_corpse',*CAUSES,'paid','ours_eaten_enemy','dead','end','residual']}
            cs=[c for c in checkpoints if c['label']==label and c['side']==s]
            snap={r:{k:sum(c[k] for c in cs if c['round']==r)/len(gs) for k in ['alive','total','length']} for r in (350,400,499)}
            # terminal games before r350/400 are held at their final absorbing state.
            for r in (350,400,499):
                vals=[g['snapshots'].get(str(r),g['snapshots'][str(g['last'])])[s] for g in gs]
                snap[r]={k:mean(v[k] for v in vals) for k in ['alive','total','length']}
            ss[str(s)]=dict(ledger=tot,snapshots=snap)
        def cohort(kind,side=None,inward=False):
            cs=[c for c in records if c['label']==label and c['kind']==kind and (side is None or c['side']==side) and (not inward or c['inward_rounds']>0)]
            return dict(n=len(cs),mass=sum(c['length'] for c in cs),inward=sum(c['inward_rounds']>0 for c in cs),arrived=sum(c['arrival'] is not None for c in cs),advertised_arrived=sum(c.get('advertised_arrival') is not None for c in cs),died=sum(c['death'] is not None for c in cs),died_before_arrival=sum(c['death'] is not None and c['arrival'] is None for c in cs),ever_top=sum(c['ever_top'] for c in cs),ever_target=sum(c['ever_target'] for c in cs),ever_final_top=sum(c.get('ever_final_top',0) for c in cs),end_final_transferred=sum(c.get('end_final_transferred',0) for c in cs),end_top=sum(c['end_top'] for c in cs),lost=sum(c['lost_tokens'] for c in cs),remaining=sum(c['remaining_tokens'] for c in cs),causes=dict(Counter(c['death']['cause'] for c in cs if c['death'])),first_generation_top=sum(t['top'] and t['side']==c['side'] for c in cs for t in c['first_generation']),first_generation_other=sum(not t['top'] and t['side']==c['side'] for c in cs for t in c['first_generation']),first_generation_enemy=sum(t['side']!=c['side'] for c in cs for t in c['first_generation']),stop_first_top=sum(t['top'] and t['side']==c['side'] and t['cause']=='stop' for c in cs for t in c['first_generation']))
        cover=Counter()
        for g in gs:cover.update(g['trace']['coverage'])
        summary[label]=dict(games=len(gs),wins=sum(g['result']=='win' for g in gs),active_at350=sum(g['last']>=350 for g in gs),sides=ss,rally=cohort('rally-proxy'),rally_inward=cohort('rally-proxy',inward=True),cohort400_ours=cohort('cohort400',0),cohort400_theirs=cohort('cohort400',1),fold=cohort('fold'),coverage=dict(cover),longest_deaths=[l for l in leaders if l['label']==label])
        for field in ['rally','rally_inward','cohort400_ours','cohort400_theirs','fold']:
            kind='rally-proxy' if field.startswith('rally') else 'cohort400' if field.startswith('cohort400') else 'fold'
            side=0 if field.endswith('ours') else 1 if field.endswith('theirs') else None
            cs=[c for c in records if c['label']==label and c['kind']==kind and (side is None or c['side']==side) and (field!='rally_inward' or c['inward_rounds']>0)]
            summary[label][field]['end_transported']=sum(c['end_transported'] for c in cs)
            summary[label][field]['transported']=sum(c['transported'] for c in cs)
    write('ledger.tsv',ledgers);write('ledger400.tsv',ledgers400);write('tracked.tsv',records);write('transfers.tsv',direct);write('leaders.tsv',leaders);write('checkpoints.tsv',checkpoints)
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(OUT/'moments.json').write_text(json.dumps(sorted(moments,key=lambda c:-c['length']),ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
