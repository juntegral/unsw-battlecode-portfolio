"""Symmetric aggregate, observed-state switch gates, and selected 7x7 boards."""
import sys
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/codex/astra/stuck-opus']
import json,runpy,io,contextlib
from pathlib import Path
from collections import Counter,deque
from statistics import median
from ladder_replay import replay
from geom import geometry
P=Path('data/codex/astra/skku')
games=[json.loads(p.read_text()) for p in sorted(P.glob('15*.json'))]

def candidate(g):
    d=g['detail'];W,H=d['W'],d['H'];G=geometry(g['base']['text']);q=d['queens'][0]
    def xy(c):return c[1]*W+c[0]
    def gap(a,b):
        dx=abs(a%W-b%W);dy=abs(a//W-b//W);return min(dx,W-dx)+min(dy,H-dy)
    def view(a,b):
        dx=abs(a%W-b%W);dy=abs(a//W-b//W);return min(dx,W-dx)<=3 and min(dy,H-dy)<=3
    memory={};rows=[]
    for s in d['qturn'][0]:
        h=xy(s['h']);occ={xy(c) for b in s['bodies'].values() for c in b if view(xy(c),h)};pearls=set(map(xy,s['pearls']));found=[];adj=[]
        for f in s['foes']:
            body=list(map(xy,s['bodies'][str(f['id'])]));seen=f['seen']
            edge=any(view(c,h) and (min(abs(c%W-h%W),W-abs(c%W-h%W))==3 or min(abs(c//W-h//W),H-abs(c//W-h//W))==3) for c in body)
            partial=seen<2 or edge
            parts=(max(seen,memory[f['id']]) if f['id'] in memory else 0) if partial else seen
            if not partial and seen>=2:memory[f['id']]=seen
            free=(parts+3)//4;queue=deque([(body[0],0,0,[body[0]])]);path=None
            while queue and path is None:
                c,steps,eaten,prev=queue.popleft()
                if steps>=4 or (parts>0 and steps>=free and parts+eaten-max(0,steps-free)<=2):continue
                for n in G['nb'][c]:
                    if n in prev:continue
                    if n==h:path=prev+[n];break
                    if n in occ:
                        if n not in body or parts<=0:continue
                        offset=body.index(n)
                        if offset>=seen or offset<parts+eaten-max(0,steps-free)-steps:continue
                    queue.append((n,steps+1,eaten+(n in pearls),prev+[n]))
            if path is not None:
                found.append(dict(id=f['id'],steps=len(path)-1,path=[(c%W,c//W) for c in path],parts=parts))
                if gap(body[0],h)==1:adj.append(f['id'])
        t=next(t for t in d['turns'] if t['id']==q and t['r']==s['r'])
        if (t['split'] and found) or s['r']==d['qturn'][0][-1]['r']:
            rows.append(dict(r=s['r'],L=s['L'],split=t['split'],blocked=bool(found),paths=found,adjacent=adj))
    return rows

def main():
    result=[]
    with (P/'evidence.txt').open('w') as out,contextlib.redirect_stdout(out):
        for g in games:
            d=g['detail'];s=g['scan'];print('GAME',s['gid'],s['map'])
            c=candidate(g);result.append(dict(gid=s['gid'],head_clear=c));print('HEAD_CLEAR observed geometry',c)
            for side in (0,1):
                tt=[t for t in d['turns'] if t['s']==side and t['id']!=d['queens'][side] and t['L']>=4 and t['r']<100]
                print('early split numerator denominator',side,sum(t['split'] for t in tt),len(tt))
            for de in d['deaths']:
                if de['id'] in (718,783) and de['s']==0 and 'attack' in de:
                    print('LONG DEATH',{k:v for k,v in de.items() if k not in ('body','last')})
                    print('LONG LAST', {k:v for k,v in de['last'][-1].items() if k not in ('bodies','pearls')})
            if s['gid']==1519938:
                print('early deaths',[(x['r'],x['id'],x['L'],x['reason'],x['actor']) for x in d['deaths'] if x['s']==0 and x['r']<40])
            if s['gid']==1519940:
                print('grow-before-split',[(t['r'],t['id'],t['L'],t['eat'],t['split']) for t in d['turns'] if t['id']==3 and 50<=t['r']<=67])
        for label,gs in [('all',games),('losses',[g for g in games if g['scan']['result']=='loss'])]:
            print('AGGREGATE',label)
            for side in (0,1):
                counts=Counter();n=ns=qn=qd=0;homes=[]
                for g in gs:
                    d=g['detail']
                    for role in g['loops']['cnt'][side]:
                        for ph in role:counts.update(ph)
                    for t in d['turns']:
                        if t['s']==side and t['id']!=d['queens'][side] and t['L']>=4 and t['r']<100:n+=1;ns+=t['split']
                    for t in d['qturn'][side]:homes.append(t['home']);qn+=t['L']<=3;qd+=1
                print('side',side,'counts',dict(counts),'early split',ns,n,'queen L<=3',qn,qd,'home median/mean',median(homes),sum(homes)/len(homes))
    (P/'gates.json').write_text(json.dumps(result,indent=2))
    with (P/'boards.txt').open('w') as out,contextlib.redirect_stdout(out):
        for g in games:
            s=g['scan'];d=g['detail'];jobs=[]
            if s['result']=='loss':
                for de in d['deaths']:
                    if de['id']==d['queens'][0]:jobs.append((de['id'],max(0,de['r']-2),de['r']))
            if s['gid']==1514290:jobs.append((783,463,465))
            if s['gid']==1514288:jobs.append((718,497,498))
            for i,r0,r1 in jobs:
                print('GAME',s['gid'],s['map'],'dragon',i)
                sys.argv=['o1_look.py',f"data/online/live-one1/{g['base']['folder']}/M{s['gid']}.replay",str(s['gid']),str(i),str(r0),str(r1)]
                runpy.run_path('data/analysis/ladder/dossier/work/o1_look.py',run_name='__main__')

if __name__=='__main__':main()
