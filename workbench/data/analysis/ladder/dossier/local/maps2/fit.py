import sys
sys.dont_write_bytecode=True
import json,math
from collections import defaultdict,Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze_fast as a
OUT=a.OUT
CANDIDATES=[(1,1),(1,5),(1,10),(1,20),(1,30),(8,30),(10,30),(20,50),(20,80),(20,200),(40,200),(100,300),(100,500),(250,500),(1,100),(1,200),(1,500),(1,1000),(1,2000),(1,2559)]

def ll(par,events,censors):
    lo,hi=par;n=hi-lo+1
    if events and (min(events)<lo or max(events)>hi):return -math.inf
    value=-len(events)*math.log(n)
    for t,num in Counter(censors).items():
        remaining=hi-max(t,lo-1)
        if remaining<=0:return -math.inf
        value+=num*math.log(remaining/n)
    return value

def main():
    rows=[json.loads(l) for l in (OUT/'observations-complete.jsonl').read_text().splitlines()]
    grouped=defaultdict(list)
    for r in rows:grouped[r['slug']].append(r)
    results={}
    for slug,rs in grouped.items():
        source=(OUT.parent/'maps'/('ladder_'+slug+'.map')).read_bytes();w,h,sym,*_=a.layout(source.decode())
        tiles=sorted({int(c) for r in rs for c in r['tile_births']});orbs=defaultdict(list)
        for c in tiles:orbs[a.orbit(c,w,h,sym)].append(c)
        estimates={};parameters={};groupstats=defaultdict(lambda:dict(events=[],censors=[],orbits=[]))
        for o,cs in sorted(orbs.items()):
            mirrors=[c for c in range(w*h) if a.orbit(c,w,h,sym)==o]
            events=[];censors=[];exact=[];residual=[];first=[]
            for r in rs:
                end=min(r['last_round']+1,max(r['virgin_end'].get(str(c),r['last_round']+1) for c in mirrors))
                if end>0:
                    born=min((r['firstbirth'].get(str(c),100000) for c in mirrors))
                    if born<end:events.append(born+1)
                    else:censors.append(end)
                z=r['samples'].get(str(o),{})
                exact+=z.get('exact',[]);residual+=z.get('residual',[]);first+=z.get('first',[])
            data=events if events else exact
            scores=sorted([(ll(p,data,censors if events else []),p) for p in CANDIDATES],reverse=True)
            finite=[x for x in scores if math.isfinite(x[0])]
            if not finite:
                raise AssertionError((slug,o,min(data),max(data)))
            score,p=finite[0]
            estimates[str(o)]=dict(tiles=cs,events=len(events),censors=len(censors),exact=len(exact),residual=len(residual),first=len(first),observed_min=min(data) if data else None,observed_max=max(data) if data else None,selected=list(p),delta=score-finite[1][0] if len(finite)>1 else None,alternatives=[[list(p0),round(v-score,3)] for v,p0 in finite[:4]])
            parameters[o]=p
            g=groupstats[p];g['events']+=events;g['censors']+=censors;g['orbits'].append(o)
        # Large intervals exceed the replay horizon: pool a coherent class and use its censored MLE.
        large=[p for p in groupstats if p[1]>=1000]
        # Do not invent distinct 2000/2559 classes from noisy individual censoring.
        large_source=(1,2000) if slug=='australia_1' else (1,2559) if slug in ('islands_1','slithery_fight_1') else (1,1000)
        large_events=[];large_censors=[];large_orbits=[]
        for p in large:
            g=groupstats[p];large_events+=g['events'];large_censors+=g['censors'];large_orbits+=g['orbits']
        if large_orbits:
            low=max(501,max(large_events,default=1));best=max(range(low,6001),key=lambda hi:ll((1,hi),large_events,large_censors));v=ll((1,best),large_events,large_censors)
            interval=[hi for hi in range(low,6001) if ll((1,hi),large_events,large_censors)>=v-1.92]
            known=large_source[1];knownll=ll(large_source,large_events,large_censors)
            # Snap only if the matching historical map's value lies in the pooled 95% support interval.
            par=large_source if interval[0]<=known<=interval[-1] else (1,best)
            for o in large_orbits:parameters[o]=par;estimates[str(o)]['final']=list(par)
            large_fit=dict(mle=[1,best],ci95=[interval[0],interval[-1]],hypothesis=list(large_source),hypothesis_loglike_delta=v-knownll,selected=list(par),events=len(large_events),censors=len(large_censors),orbits=len(large_orbits))
        else:large_fit=None
        # Every tile lacking an observed natural birth remains disabled, even if its mirror spawned.
        final={c:parameters[a.orbit(c,w,h,sym)] if c in tiles else (0,0) for c in range(w*h)}
        lines=[]
        for l in source.splitlines(keepends=True):
            if l.startswith(b'TILE '):
                q=l.split();c=int(q[2])*w+int(q[1]);lo,hi=final[c]
                # Retain the entire line if it stays disabled.
                if (lo,hi)!=(0,0):
                    tail=b'\r\n' if l.endswith(b'\r\n') else b'\n' if l.endswith(b'\n') else b''
                    l=b' '.join(q[:3])+b' '+str(lo).encode()+b' '+str(hi).encode()+tail
            lines.append(l)
        data=b''.join(lines);(OUT/('ladder_'+slug+'.map')).write_bytes(data)
        old_non=[l for l in source.splitlines(keepends=True) if not l.startswith(b'TILE ')];new_non=[l for l in data.splitlines(keepends=True) if not l.startswith(b'TILE ')]
        assert old_non==new_non
        result=dict(games=len(rs),main=sum(r['main'] for r in rs),classes={'%d %d'%p:n for p,n in sorted(Counter(final.values()).items())},orbits=estimates,large_fit=large_fit)
        results[slug]=result;print(slug,result['games'],result['classes'],'large',large_fit,flush=True)
    (OUT/'estimates.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
