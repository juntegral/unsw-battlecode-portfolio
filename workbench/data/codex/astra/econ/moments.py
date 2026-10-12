import sys
sys.dont_write_bytecode=True
sys.path[:0]=['data/codex/astra/approach',str(__import__('pathlib').Path(__file__).resolve().parent)]
from scan import Board,replay
from analyze import flood,OUT
from collections import Counter,defaultdict
import json

allrows=[];summaries=[]
for gid in (1480431,1480435,1480436,1479924,1479925):
    g=json.loads((OUT/f'game-{gid}.json').read_text());B=Board(g['path'])
    meta=json.loads(__import__('pathlib').Path(g['path']).with_name(f'game-{gid}.json').read_text())
    own=int(meta['teamAId']!=1119);tiles={tuple(c) for c in g['natural_bearing']}
    rev={c:[] for c in B.adj}
    for c,ns in B.adj.items():
        for n in ns:
            if n is not None:rev[n].append(c)
    dt=flood(rev,tiles);C=Counter();cur=None;rows=[]
    def close():
        global cur
        if cur is None:return
        cur['end']=B.bodies[cur['i']][0] if cur['i'] in B.bodies else None
        if cur['end'] is not None:cur['end_d']=dt.get(cur['end'])
        rows.append(cur);cur=None
    for ev in B.root.pointer(3):
        k=ev.u16(0);p=ev.pointer(0)
        if k in (0,1):close()
        if k==0 and p.i32(0)>150:break
        if cur:
            if k==3 and not p.u32(0):cur['eaten']+=1
            if k==10:cur['split']=True
        B.update(k,p)
        if k==1 and B.teams[B.actor]==own:
            h=B.bodies[B.actor][0];L=len(B.bodies[B.actor]);adj=any(n in B.pearls for n in B.adj[h] if n is not None)
            near=B.flood(h,2)
            mates=sum(i!=B.actor and B.teams[i]==own and b[0] in near for i,b in B.bodies.items())
            visible=sum(B.view(h,t) for t in tiles)
            cur=dict(gid=gid,r=B.rnd,i=B.actor,h=h,L=L,d=dt.get(h),visible_bearing=visible,adjacent_pearl=adj,mates2=mates,eaten=0,split=False)
    close()
    for v in rows:
        C['turns']+=1;C['no_adjacent']+=not v['adjacent_pearl']
        C['no_bearing4']+=v['d'] is None or v['d']>4
        C['no_adjacent_bearing4']+=(not v['adjacent_pearl']) and (v['d'] is None or v['d']>4)
    by=defaultdict(list)
    for v in rows:by[v['i']].append(v)
    drought=[]
    for i,rr in by.items():
        seq=[]
        for v in rr+[dict(eaten=1)]:
            if not v['eaten'] and not v.get('split',False):seq.append(v)
            else:
                if len(seq)>=10:
                    drought.append(dict(i=i,start=seq[0]['r'],end=seq[-1]['r'],turns=len(seq),unique=len({tuple(x['h']) for x in seq}),
                        no_adjacent=sum(not x['adjacent_pearl'] for x in seq),outside4=sum(x['d'] is None or x['d']>4 for x in seq),
                        first=seq[0],last=seq[-1]))
                seq=[]
    summaries.append(dict(gid=gid,map=g['map'],counts=dict(C),droughts=sorted(drought,key=lambda x:-x['turns'])[:8]))
    allrows+=rows
(OUT/'turns.jsonl').write_text('\n'.join(json.dumps(x) for x in allrows)+'\n')
(OUT/'moments.json').write_text(json.dumps(summaries,indent=2))
print(json.dumps(summaries,indent=2))
