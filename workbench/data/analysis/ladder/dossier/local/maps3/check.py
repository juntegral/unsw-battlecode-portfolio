import sys
sys.dont_write_bytecode=True
import json, importlib.util,hashlib
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze_fast as a
from unswbc.engine import EngineModule
OUT=a.OUT
spec=importlib.util.spec_from_file_location('geometry',a.ROOT/'data/analysis/ladder/losses/counts/count_replays.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def route(g,head,length,blocked,spawn):
    seen=set();path=[];dirs=[];on={}
    def dfs(c):
        seen.add(c);on[c]=len(path);path.append(c)
        for d,(kind,t) in enumerate(g.moves[c]):
            if kind==1 or t in blocked or t in spawn:continue
            if t in on and len(path)-on[t]>length:
                return (list(path),dirs+[d],on[t])
            if t not in seen:
                dirs.append(d);ans=dfs(t)
                if ans:return ans
                dirs.pop()
        on.pop(c);path.pop();return None
    return dfs(head)


def controller(slug):
    text=(OUT/('ladder_'+slug+'.map')).read_text();w,h,sym,*_=a.layout(text)
    raw=[];bodies=[];teams=[];spawn=set();pars={}
    for l in text.splitlines():
        q=l.split()
        if not q:continue
        if q[0]=='EDGE':raw.append(tuple(map(int,q[1:])))
        elif q[0]=='DRAGON':bodies.append([int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2]))]);teams.append(int(q[1]))
        elif q[0]=='TILE':
            c=int(q[2])*w+int(q[1]);pars[c]=tuple(map(int,q[3:5]))
            if int(q[4]):spawn.add(c)
    g=m.Geometry(w,h,raw);blocked={c for b in bodies for c in b};routes={};used=set()
    for team in (0,1):
        for i in sorted((i for i,t in enumerate(teams) if t==team),key=lambda i:len(bodies[i])):
            r=route(g,bodies[i][0],len(bodies[i]),(blocked-{bodies[i][0]})|used,spawn)
            if r:
                routes[i]=r;used.update(r[0]);break
        else:raise AssertionError((slug,'no safe non-pearl cycle',team))
    def reply(i,block):
        if i not in routes:return b'SUICIDE\n'
        rnd=int(block.decode().splitlines()[0].split()[1]);path,dirs,start=routes[i]
        index=rnd if rnd<len(dirs) else start+(rnd-start)%(len(dirs)-start)
        return ('MOVE '+'NESW'[dirs[index]]+'\n').encode()
    return reply,dict(routes={str(i):dict(path=r[0],directions=''.join('NESW'[d] for d in r[1]),cycle_start=r[2],length=len(bodies[i]),team=teams[i]) for i,r in routes.items()},initial_cells=sorted(blocked),route_cells=sorted(used),parameters={str(c):list(p) for c,p in pars.items()})


def run(slug,n=100):
    mapdata=(OUT/('ladder_'+slug+'.map')).read_bytes();digest=hashlib.sha256(mapdata).hexdigest()
    out=OUT/'checks'/slug;out.mkdir(parents=True,exist_ok=True)
    cache=out/'runs.json'
    if cache.exists():
        saved=json.loads(cache.read_text())
        if saved.get('map_sha256')==digest and len(saved['runs'])==n:
            print(slug,'reuse',n,'verified seeds',flush=True);return saved['runs'],saved['controller']
    e=EngineModule();reply,control=controller(slug);runs=[]
    w=a.layout(mapdata.decode())[0]
    print(slug,'survivors',[(i,v['length'],len(v['path'])-v['cycle_start']) for i,v in control['routes'].items()],flush=True)
    for seed in range(n):
        deaths=[];result=e.run(mapdata,reply,on_death=lambda *d:deaths.append(d),debug=0,seed=seed)
        assert result.rounds==499,(slug,seed,result,deaths)
        blob=e.replay('pearl-free loop','pearl-free loop')
        if seed<2:(out/('seed-%d.replay'%seed)).write_bytes(blob)
        raw=a.fast_unpack(blob);rnd=-1;actor=None;births=defaultdict(list);ate=0;countdowns=defaultdict(list)
        # Countdowns are kept in the diagnostic seed, while counts use the verified native decoder.
        for k,p in a.event_list(raw):
            if k==0:rnd=p[0];actor=None
            elif k==1:actor=p[0]
            elif k==3:
                if p[0] and actor is None:births[p[2]*w+p[1]].append(rnd)
                elif not p[0]:ate+=1
        assert ate==0,(slug,seed,'ate',ate)
        runs.append(dict(seed=seed,rounds=result.rounds,ate=ate,births={str(c):rs for c,rs in births.items()},deaths=deaths))
        if seed%25==0:print(slug,'seed',seed,flush=True)
    (out/'runs.json').write_text(json.dumps(dict(controller=control,runs=runs,map_sha256=digest),separators=(',',':'))+'\n')
    return runs,control


def compare(slug,runs,control,rows):
    pars={int(c):tuple(p) for c,p in control['parameters'].items()};exclude=set(control['initial_cells'])|set(control['route_cells'])
    result={};phases=[(0,100),(101,300)]
    local_first={c:[min(r['births'].get(str(c),[100000])) for r in runs] for c,p in pars.items() if p[1] and c not in exclude}
    for par in sorted(set(pars.values())-{(0,0)}):
        cls=[c for c,p in pars.items() if p==par and c not in exclude];values=[]
        pool=[b for c in cls for b in local_first[c]]
        hist=Counter(pool);risk=len(pool);hazards=[0.0]
        for rnd in range(301):
            hazards.append(hazards[-1]+(hist[rnd]/risk if risk else 0))
            risk-=hist[rnd]
        for lo,hi in phases:
            lc=ld=prefix_lc=0;tiles=games=risk_rounds=0
            for r in rows:
                if r['last_round']<hi:continue
                games+=1
                for c in cls:
                    # Compare the first birth before any body visit or death drop; moving test bots never enter these tiles.
                    cutoff=min(hi+1,r['virgin_end'].get(str(c),hi+1))
                    if cutoff<=lo:continue
                    tiles+=1;born=r['firstbirth'].get(str(c),100000)
                    ld+=int(lo<=born<cutoff)
                    prefix_lc+=sum(lo<=b<cutoff for b in local_first[c])/len(runs)
                    risk_end=min(cutoff,born+1)
                    if risk_end>lo:
                        lc+=hazards[risk_end]-hazards[lo];risk_rounds+=risk_end-lo
            values.append(dict(phase='%d-%d'%(lo,hi),local=lc,games=games,ladder=ld,tile_games=tiles,ratio=lc/ld if ld else None,local_per_game=lc/games if games else None,ladder_per_game=ld/games if games else None,prefix_local=prefix_lc,prefix_ratio=prefix_lc/ld if ld else None,risk_tile_rounds=risk_rounds))
        result['%d %d'%par]=dict(tiles=len(cls),phases=values)
    totals=[]
    for z,(lo,hi) in enumerate(phases):
        lc=sum(r['phases'][z]['local'] for r in result.values());ld=sum(r['phases'][z]['ladder'] for r in result.values());games=sum(r['last_round']>=hi for r in rows)
        totals.append(dict(phase='%d-%d'%(lo,hi),local=lc,ladder=ld,games=games,local_per_game=lc/games,ladder_per_game=ld/games,ratio=lc/ld if ld else None,prefix_local=sum(r['phases'][z]['prefix_local'] for r in result.values()),prefix_ratio=sum(r['phases'][z]['prefix_local'] for r in result.values())/ld if ld else None))
    raw_games=[r for r in rows if r['last_round']>=100]
    raw_ladder=sum(r['phasebirths'][0] for r in raw_games)/len(raw_games)
    raw_local=sum(sum(sum(b<=100 for b in bs) for bs in r['births'].values()) for r in runs)/len(runs)
    return dict(classes=result,comparable_totals=totals,raw_total_0_100=dict(local_per_game=raw_local,ladder_per_game=raw_ladder,ratio=raw_local/raw_ladder),excluded_tiles=len(exclude),seeds=len(runs))


def main():
    sys.setrecursionlimit(10000)
    rows=[json.loads(l) for l in (OUT/'observations-complete.jsonl').read_text().splitlines()];results={}
    for slug in a.TARGETS:
        runs,control=run(slug,64);result=compare(slug,runs,control,[r for r in rows if r['slug']==slug]);results[slug]=result
        print(slug,'ratios',[r['ratio'] for r in result['comparable_totals']],'raw',result['raw_total_0_100'],flush=True)
        (OUT/'checks.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
