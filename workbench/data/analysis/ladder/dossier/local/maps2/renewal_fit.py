import sys
sys.dont_write_bytecode=True
import ctypes,json,math,time
from collections import defaultdict,Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze_fast as a
from fit import CANDIDATES
OUT=a.OUT
lib=ctypes.CDLL(str(OUT/'renewal-fast.dylib'));lib.renewal_ll.argtypes=[ctypes.c_int]*3+[ctypes.c_void_p]*2;lib.renewal_ll.restype=ctypes.c_double

def prepare(rows,o,mirrors):
    seqs=[]
    for r in rows:
        rec=r['records'].get(str(o))
        if rec is not None:
            T=r['last_round']+1;bits=int(rec['free_bits'],16);free=bytes((bits>>i)&1 for i in range(T));bs=set(rec['births']);birth=bytes(int(i in bs) for i in range(T))
        else:
            T=min(r['last_round']+1,max(r['virgin_end'].get(str(c),r['last_round']+1) for c in mirrors));free=b'\1'*T;birth=b'\0'*T
        if T:seqs.append((T,free,birth))
    return seqs

def main():
    results=json.loads((OUT/('estimates-renewal.json' if (OUT/'estimates-renewal.json').exists() else 'estimates.json')).read_text());rows=defaultdict(list)
    for l in (OUT/'observations-complete.jsonl').read_text().splitlines():r=json.loads(l);rows[r['slug']].append(r)
    for slug,res in results.items():
        if all('renewal' in e for e in res['orbits'].values()) and res['games']==len(rows[slug]) and (res.get('large_fit_renewal') or not any(e['renewal']['selected'][1]>=1000 for e in res['orbits'].values())):
            print(slug,'reuse complete renewal fit',flush=True);continue
        w,h,sym,*_=a.layout((OUT.parent/'maps'/('ladder_'+slug+'.map')).read_text());pars={};groupstats=defaultdict(list)
        # Fixed-spawn hypotheses from the matching historical map are tested, never copied.
        known={};name=slug.rsplit('_',1)[0]
        p=Path('~/01. Project/개인 프로젝트/battlecode/tune_runs/official127')/(name+'.map')
        if p.exists():
            for l in p.read_text().splitlines():
                q=l.split()
                if q and q[0]=='TILE':known[int(q[2])*w+int(q[1])]=tuple(map(int,q[3:5]))
        for z,(os,est) in enumerate(res['orbits'].items()):
            o=int(os);mirrors=[c for c in range(w*h) if a.orbit(c,w,h,sym)==o];seqs=prepare(rows[slug],o,mirrors)
            candidates={tuple(p) for p,v in est['alternatives']}|{known.get(o,(0,0))};candidates.discard((0,0))
            # The no-first-sample case must use complete renewal likelihood, including blocked attempts.
            if est['events']==0:candidates=set(CANDIDATES)
            scores=[]
            for p in candidates:
                value=sum(lib.renewal_ll(*p,T,free,birth) for T,free,birth in seqs)
                scores.append((value,p))
            scores.sort(reverse=True);v,par=scores[0]
            if not math.isfinite(v):
                scores=[(sum(lib.renewal_ll(*p,T,free,birth) for T,free,birth in seqs),p) for p in CANDIDATES]
                scores.sort(reverse=True);v,par=scores[0]
            assert math.isfinite(v),(slug,o,scores)
            pars[o]=par;groupstats[par].append((o,seqs))
            est['renewal']=dict(selected=list(par),delta=v-scores[1][0] if len(scores)>1 else None,scores=[[list(p),v0-v] for v0,p in scores[:4]])
            if z%50==0:print(slug,z,'/',len(res['orbits']),flush=True)
        # Pool genuinely long-interval tiles; preserve short/shifted ranges separately.
        large_items=[item for par,items in groupstats.items() if par[1]>=1000 for item in items]
        if large_items:
            seqs=[seq for o,ss in large_items for seq in ss]
            # All first and exact information, and failed hidden attempts, enter this fit.
            coarse=range(800,4001,100);values={hi:sum(lib.renewal_ll(1,hi,T,f,b) for T,f,b in seqs) for hi in coarse};best=max(values,key=values.get)
            fine=range(max(501,best-150),best+151,5);values.update({hi:sum(lib.renewal_ll(1,hi,T,f,b) for T,f,b in seqs) for hi in fine});best=max(values,key=values.get);peak=values[best]
            # Historical values must agree with the renewal fit before snapping.
            candidate=2000 if slug=='australia_1' else 2559 if slug in ('islands_1','slithery_fight_1') else 1000
            v=sum(lib.renewal_ll(1,candidate,T,f,b) for T,f,b in seqs)
            chosen=candidate if peak-v<=1.92 else best
            supported=sorted(hi for hi,value in values.items() if peak-value<=1.92)
            res['large_fit_renewal']=dict(mle=[1,best],ci95_grid=[supported[0],supported[-1]],historical=[1,candidate],historical_delta=peak-v,selected=[1,chosen],orbits=len(large_items))
            for o,ss in large_items:pars[o]=(1,chosen)
        source=(OUT.parent/'maps'/('ladder_'+slug+'.map')).read_bytes();enabled={int(c) for r in rows[slug] for c in r['tile_births']};final={c:pars[a.orbit(c,w,h,sym)] if c in enabled else (0,0) for c in range(w*h)}
        lines=[]
        for l in source.splitlines(keepends=True):
            if l.startswith(b'TILE '):
                q=l.split();c=int(q[2])*w+int(q[1]);lo,hi=final[c]
                if hi:l=b' '.join(q[:3])+b' '+str(lo).encode()+b' '+str(hi).encode()+b'\n'
            lines.append(l)
        data=b''.join(lines);(OUT/('ladder_'+slug+'.map')).write_bytes(data)
        res['classes']={'%d %d'%p:n for p,n in sorted(Counter(final.values()).items())}
        for os,est in res['orbits'].items():est['final']=list(pars[int(os)])
        (OUT/'estimates-renewal.json').write_text(json.dumps(results,indent=2)+'\n')
        print(slug,'classes',res['classes'],'large',res.get('large_fit_renewal'),flush=True)

if __name__=='__main__':main()
