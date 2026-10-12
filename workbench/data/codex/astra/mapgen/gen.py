#!/usr/bin/env python3
"""Deterministic unseen-map suite. Uses no bot and executes no game turns."""
import argparse
from collections import Counter, deque
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
RED = Path.home() / 'meow-redteam'
OFFICIAL = RED / 'engine/venv/lib/python3.13/site-packages/unswbc/templates/maps'
FAMILIES = ('open','rooms','corridors','islands','ring','rotation','poor','rich')

class Map:
    def __init__(self, w, h, symmetry='xy'):
        self.w, self.h, self.symmetry = w, h, symmetry
        self.n = w*h
        self.tiles = [(0,0)]*self.n
        self.edges = [(0,-1)]*(2*self.n)
        self.dragons = []
    def mirror(self, k):
        x,y = k%self.w,k//self.w
        return (self.h-1-y if 'x' in self.symmetry else y)*self.w + (self.w-1-x if 'y' in self.symmetry else x)
    def mirror_edge(self, e):
        k=e%self.n; x,y=k%self.w,k//self.w; north=e<self.n
        if 'y' in self.symmetry: x=(self.w-(1 if north else 0)-x)%self.w
        if 'x' in self.symmetry: y=(self.h-(0 if north else 1)-y)%self.h
        return (0 if north else self.n)+y*self.w+x
    def endpoints(self,e):
        k=e%self.n; x,y=k%self.w,k//self.w
        return (((y-1)%self.h)*self.w+x,k) if e<self.n else (y*self.w+(x-1)%self.w,k)
    def between(self,a,b):
        x,y=a%self.w,a//self.w; xx,yy=b%self.w,b//self.w
        if x==xx:
            if (y+1)%self.h==yy: return b
            if (y-1)%self.h==yy: return a
        if y==yy:
            if (x+1)%self.w==xx: return self.n+b
            if (x-1)%self.w==xx: return self.n+a
        return None
    def set_edge(self,e,value):
        self.edges[e]=self.edges[self.mirror_edge(e)]=value
    def graph(self, portals=True):
        pairs={}
        for e,(t,p) in enumerate(self.edges):
            if t==2: pairs.setdefault(p,[]).append(e)
        partners={a:b for es in pairs.values() if len(es)==2 for a,b in (es,es[::-1])}
        nb=[[] for _ in range(self.n)]
        for e,(t,_) in enumerate(self.edges):
            a,b=self.endpoints(e)
            if t==0: nb[a].append(b); nb[b].append(a)
            elif t==2 and portals:
                c,d=self.endpoints(partners[e]); nb[a].append(d); nb[b].append(c)
        return [sorted(set(xs)) for xs in nb]
    def text(self,name):
        lines=[f'MAP {self.w} {self.h}',f'SYMMETRY {self.symmetry}',f'MAP_NAME {name}',f'TILE_COUNT {self.n}']
        lines += [f'TILE {k%self.w} {k//self.w} {lo} {hi}' for k,(lo,hi) in enumerate(self.tiles)]
        es=[]
        for e,(t,p) in enumerate(self.edges):
            if t:
                k=e%self.n; idx=(2*(k//self.w)+(e>=self.n))*(self.w+1)+k%self.w
                es.append(f'EDGE {idx} {t} {p}')
        lines += [f'EDGE_COUNT {len(es)}',*es,f'DRAGON_COUNT {len(self.dragons)}']
        for team,body in self.dragons:
            lines.append(f'DRAGON {team} {len(body)} '+' '.join(f'{k%self.w} {k//self.w}' for k in body))
        return '\n'.join(lines+['END',''])

def read_map(p):
    lines=p.read_text().splitlines(); w,h=map(int,lines[0].split()[1:]); m=Map(w,h)
    for line in lines[1:]:
        a=line.split()
        if not a: continue
        if a[0]=='SYMMETRY': m.symmetry=a[1]
        elif a[0]=='TILE':
            x,y,lo,hi=map(int,a[1:]);m.tiles[y*w+x]=(lo,hi)
        elif a[0]=='EDGE':
            i,t,pid=map(int,a[1:]); row,x=divmod(i,w+1)
            if row%2==0 and x==w: continue
            e=((row//2)%h)*w+(x%w)+(m.n if row%2 else 0)
            if t: m.edges[e]=(t,pid)
        elif a[0]=='DRAGON':
            team,n,*xy=map(int,a[1:]); assert len(xy)==2*n
            m.dragons.append((team,[xy[i+1]*w+xy[i] for i in range(0,len(xy),2)]))
    return m

def distances(nb,seeds):
    d={k:0 for k in seeds}; q=deque(seeds)
    while q:
        k=q.popleft()
        for j in nb[k]:
            if j not in d: d[j]=d[k]+1;q.append(j)
    return d

def metrics(m):
    gaps=Counter(f'{a}..{b}' for a,b in m.tiles if b)
    starts=[[len(b) for t,b in m.dragons if t==s] for s in (0,1)]
    heads=[[b[0] for t,b in m.dragons if t==s] for s in (0,1)]
    nb=m.graph(); d=distances(nb,heads[0]); ds=[d[k] for k in heads[1] if k in d]
    a,b=heads[0][0],heads[1][0];dx=abs(a%m.w-b%m.w);dy=abs(a//m.w-b//m.w)
    return dict(w=m.w,h=m.h,cells=m.n,symmetry=m.symmetry,
        kelp=sum(t==1 for t,p in m.edges)/(2*m.n),portals=len({p for t,p in m.edges if t==2}),
        bearing=sum(gaps.values()),bearing_share=sum(gaps.values())/m.n,timers=dict(sorted(gaps.items())),
        starts=starts,start_distance=min(ds) if ds else None,
        queen_torus_distance=min(dx,m.w-dx)+min(dy,m.h-dy))

def ladder():
    names=json.loads((REPO/'data/online/smoke/one5-w1.json').read_text())['maps']
    historical=json.loads((REPO/'data/analysis/ladder/maps.json').read_text())
    rows=[]
    for item in names:
        name=item['name']; stem=name.lower().replace(' ','_')
        candidates=sorted((RED/'maps/ladder').glob(f'ladder_{stem}_*.map'))
        p=candidates[0] if candidates else OFFICIAL/f'{stem}.map'
        assert p.exists(),p
        m=read_map(p); measured=metrics(m)
        history=historical[name+' #1']
        assert (m.w,m.h)==(history['width'],history['height'])
        rows.append(dict(name=name,source=str(p),historical_metadata={k:history[k] for k in ('width','height','wall_share','portals','pearl_tiles','dragons_at_spawn','queen_spawn_length','queen_spawn_distance')},**measured))
    bounds={key:[min(r[key] for r in rows if r[key] is not None),max(r[key] for r in rows if r[key] is not None)] for key in ('w','h','cells','kelp','portals','bearing_share','start_distance')}
    gaps=[tuple(map(int,g.split('..'))) for r in rows for g in r['timers']]
    bounds['timer_lo']=[min(a for a,b in gaps),max(a for a,b in gaps)]
    bounds['timer_hi']=[min(b for a,b in gaps),max(b for a,b in gaps)]
    bounds['start_lengths']=sorted({n for r in rows for n in r['starts'][0]})
    bounds['start_count']=[min(len(r['starts'][0]) for r in rows),max(len(r['starts'][0]) for r in rows)]
    (ROOT/'ladder-data.json').write_text(json.dumps(dict(rows=rows,bounds=bounds),indent=2)+'\n')
    lines=['# Ladder parameters','',
        'The current 15-name roster is read from `data/online/smoke/one5-w1.json` (offline). `maps.json` contains 19 historical variants; Autarky and Prisoners Dilemma are absent from this roster. Schooltime has two historical variants; the first stored variant is tabulated.',
        '', 'Source preference: the 9 files in `~/meow-redteam/maps/ladder` (8 distinct names), then installed engine 1.2.7 bundled maps. Each row links its actual source below. Ladder reconstructions may have estimated pearl timers; bundled maps supply exact local configuration, not verified current server timers.',
        '', 'Cells = width × height; kelp share = closed canonical torus edges / (2 × cells); portals = pairs; timers = min..max:number of bearing tiles; starts list lengths in queen-first order per side. Distance is minimum traversable head-to-head steps including portal routing; queen torus distance is also shown. Neither distance counts starting bodies as obstacles. None means the starts are disconnected. The additional historical column quotes maps.json bearing counts and queen torus distance; it is not substituted for the local map configuration.',
        '', '| Name | W | H | Cells | Symmetry | Kelp share | Portal pairs | Bearing tiles / timers | Starts A / B | Start distance / queen torus | maps.json bearing / queen distance |',
        '|---|---:|---:|---:|---|---:|---:|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['name']} | {r['w']} | {r['h']} | {r['cells']} | {r['symmetry']} | {r['kelp']:.6f} | {r['portals']} | {r['bearing']}; "+'; '.join(f'{g}:{n}' for g,n in r['timers'].items())+f" | {r['starts'][0]} / {r['starts'][1]} | {r['start_distance']} / {r['queen_torus_distance']} | {r['historical_metadata']['pearl_tiles']} / {r['historical_metadata']['queen_spawn_distance']} |")
    lines += ['', '## Sources','']+[f"- {r['name']}: `{r['source']}`" for r in rows]
    lines += ['', '## Measured envelope','', '```json',json.dumps(bounds,indent=2),'```','',
        '`inside` means every numeric dimension above is within its marginal ladder bounds; start lengths belong to the observed set. It does not mean the joint geometry occurred on the ladder. `outside` means at least one dimension is outside. Symmetries x, y, xy are all observed.',
        '', 'The brief additionally requests a lone length-4 queen. This layout is legal but is not present among these 15 local ladder configurations; it is included as outside-range coverage.',
        '', '## Loader rules','',
        'Installed engine: `~/meow-redteam/engine/venv/.../unswbc/engine.py` and `unswbc_engine.wasm` (1.2.7). The wheel exposes `ubc_run`, not a separate parse function. `loader_check.py` aborts at the first spawn callback, after loading and before any turn/reply. No bot process exists.',
        '', 'Loader dimension probes establish each side in 7..256 inclusive; 6 is rejected with “map must be at least 7x7”, 257 with “map must be at most 256x256”. SYMMETRY accepts x (top/bottom), y (left/right), xy (180-degree rotation); diagonal declarations are unsupported. EDGE kind 0=open, 1=kelp, 2=paired portal; EDGE indices use alternating horizontal/vertical rows of width W+1, with torus aliases. TILE records contain coordinates and positive ordered respawn bounds or 0 0. DRAGON teams alternate, segments are head-first, minimum length 2. Generator writes all tiles, non-open canonical edges, all dragons, and END. Generated timer/length values are validated by the loader rather than assumed to be exhaustive engine limits.']
    (ROOT/'ladder-params.md').write_text('\n'.join(lines)+'\n')
    return rows,bounds


def geometry(m,family,rng):
    w,h,n=m.w,m.h,m.n
    if family in ('open','poor','rich'):
        for e in range(2*n):
            if e<=m.mirror_edge(e) and rng.random()<0.085: m.set_edge(e,(1,-1))
    elif family=='rooms':
        spacing=max(3,min(w,h)//5)
        for e in range(2*n):
            k=e%n;x,y=k%w,k//w
            if (y%spacing==0 and e<n and x%spacing!=1) or (x%spacing==0 and e>=n and y%spacing!=1):
                m.set_edge(e,(1,-1))
        for y in range(1,h,spacing):
            for x in range(w): m.set_edge(n+y*w+x,(0,-1))
        for x in range(1,w,spacing):
            for y in range(h): m.set_edge(y*w+x,(0,-1))
    elif family=='corridors':
        for y in range(h):
            if y%4 in (0,1):
                for x in range(w): m.set_edge(y*w+x,(1,-1))
        for y in range(1,h,4):
            x=rng.randrange(w);m.set_edge(n+y*w+x,(1,-1))
            door=(x+w//2)%w;m.set_edge(y*w+door,(0,-1))
    elif family=='islands':
        for x in (0,w//2):
            for y in range(h): m.set_edge(n+y*w+x,(1,-1))
        for e in range(2*n):
            if m.edges[e][0]==0 and e<=m.mirror_edge(e) and rng.random()<0.075: m.set_edge(e,(1,-1))
        for pid,y in enumerate((1,h//2-1)):
            e=n+y*w;f=m.mirror_edge(e)
            if e!=f and m.edges[e][0]!=2 and m.edges[f][0]!=2:
                m.edges[e]=m.edges[f]=(2,pid)
    elif family=='ring':
        margin=max(1,min(w,h)//4)
        for e in range(2*n):
            a,b=m.endpoints(e)
            inner=lambda k: margin<=k%w<w-margin and margin<=k//w<h-margin
            if inner(a)!=inner(b): m.set_edge(e,(1,-1))
            elif e<=m.mirror_edge(e) and rng.random()<0.06: m.set_edge(e,(1,-1))
    elif family=='rotation':
        for e in range(2*n):
            k=e%n;x,y=k%w,k//w
            if (x-y)%11==0 and rng.random()<0.7: m.set_edge(e,(1,-1))
    else: raise ValueError(family)


def place_starts(m,lengths,rng,family):
    nb=m.graph(portals=False); occupied=set();reserved=set();dragons=[]
    margin=max(1,min(m.w,m.h)//4)
    central=lambda k: margin<=k%m.w<m.w-margin and margin<=k//m.w<m.h-margin
    candidates=[k for k in range(m.n) if k<m.mirror(k) and len(nb[k])>=2 and (family!='ring' or not central(k))]
    rng.shuffle(candidates)
    for length in lengths:
        found=None
        for head in candidates:
            if head in occupied or head in reserved: continue
            for attempt in range(12):
                body=[head];seen={head,m.mirror(head)}
                while len(body)<length:
                    options=[k for k in nb[body[-1]] if k not in occupied|reserved|seen and m.mirror(k) not in occupied|reserved|seen]
                    if not options: break
                    options.sort(); k=rng.choice(options);body.append(k);seen.update((k,m.mirror(k)))
                exits=[k for k in nb[head] if k not in occupied|seen and m.mirror(k) not in occupied|seen]
                if len(body)==length and exits:
                    found=(body,exits[0]);break
            if found: break
        if not found: raise ValueError('could not place starts')
        body,exit=found; mirrored=[m.mirror(k) for k in body]
        occupied.update(body+mirrored);reserved.update((exit,m.mirror(exit)))
        dragons.extend(((0,body),(1,mirrored)))
    m.dragons=dragons


def supply(m,family,inside,rng):
    share=0.085 if family=='poor' and inside else 0.018 if family=='poor' else 0.93 if family=='rich' else 0.22
    timer=(300,3000) if family=='poor' and inside else (4000,12000) if family=='poor' else (1,3) if family=='rich' else (5,80)
    for k in range(m.n):
        if k<=m.mirror(k) and rng.random()<share:
            m.tiles[k]=m.tiles[m.mirror(k)]=timer
    nb=m.graph();occupied={k for t,b in m.dragons for k in b}
    for t,body in m.dragons:
        reachable=distances(nb,[body[0]])
        choices=sorted((d,k) for k,d in reachable.items() if k not in occupied)
        assert choices
        k=choices[min(3,len(choices)-1)][1]
        m.tiles[k]=m.tiles[m.mirror(k)]=timer


def outside_reasons(m,bounds):
    r=metrics(m); reasons=[]
    for key in ('w','h','cells','kelp','portals','bearing_share','start_distance'):
        lo,hi=bounds[key];v=r[key]
        if v is None or not lo-1e-12<=v<=hi+1e-12: reasons.append(key)
    for side in r['starts']:
        if not bounds['start_count'][0]<=len(side)<=bounds['start_count'][1]: reasons.append('start_count')
        if any(n not in bounds['start_lengths'] for n in side):reasons.append('start_lengths')
    for lo,hi in m.tiles:
        if hi and not (bounds['timer_lo'][0]<=lo<=bounds['timer_lo'][1] and bounds['timer_hi'][0]<=hi<=bounds['timer_hi'][1]): reasons.append('timers');break
    return sorted(set(reasons))


def validate(m):
    assert 7<=m.w<=256 and 7<=m.h<=256
    assert all(m.tiles[k]==m.tiles[m.mirror(k)] for k in range(m.n))
    pairs={}
    for e,(t,p) in enumerate(m.edges):
        assert t==m.edges[m.mirror_edge(e)][0]
        if t==2: pairs.setdefault(p,[]).append(e)
    for es in pairs.values():
        assert len(es)==2 and (es[0]<m.n)==(es[1]<m.n)
        mirrored=[m.mirror_edge(e) for e in es]
        assert m.edges[mirrored[0]][1]==m.edges[mirrored[1]][1]
    occupied=set()
    for i,(team,body) in enumerate(m.dragons):
        assert team==i%2 and len(body)>=2
        assert (1-team,[m.mirror(k) for k in body]) in m.dragons
        for j,k in enumerate(body):
            assert k not in occupied;occupied.add(k)
            if j:
                edge=m.between(body[j-1],k);assert edge is not None and m.edges[edge][0]==0
    nb=m.graph(); pearl_dist=[];free_exits=[]
    for t,b in m.dragons:
        d=distances(nb,[b[0]])
        ds=[v for k,v in d.items() if m.tiles[k][1]];assert ds
        exits=[k for k in nb[b[0]] if k not in occupied];assert exits
        pearl_dist.append(min(ds));free_exits.append(len(exits))
    return dict(symmetry=True,body_symmetry=True,portal_pairing=True,body_adjacency=True,
                no_overlap=True,pearl_distances=pearl_dist,unoccupied_first_step_exits=free_exits)


def generate(bounds,base_seed):
    sizes=[(7,7),(24,12),(64,16),(24,64),(64,64),(7,256),(256,7),(256,256)]
    layouts=[[4],[2,2],[3,3],[4,4],[4,4,4],[4],[4,4,2,2,2,2,3,4,3,10],[25,7,4,2,5,2,2]]
    records=[]
    for fi,family in enumerate(FAMILIES):
        for i,(w,h) in enumerate(sizes):
            seed=base_seed+fi*100+i;inside=1<=i<=4
            for retry in range(400):
                rng=random.Random(seed*1000+retry);m=Map(w,h)
                geometry(m,family,rng)
                if inside:
                    # Keep geometry while matching the measured edge-density envelope.
                    lower,upper=bounds['kelp']
                    if family=='corridors': upper=0.20
                    es=[e for e in range(2*m.n) if e<=m.mirror_edge(e) and m.edges[e][0]!=2]
                    rng.shuffle(es)
                    count=sum(t==1 for t,p in m.edges)
                    for e in es:
                        delta=1 if e==m.mirror_edge(e) else 2
                        if count<lower*2*m.n and m.edges[e][0]==0:
                            m.set_edge(e,(1,-1));count+=delta
                        elif count>upper*2*m.n and m.edges[e][0]==1:
                            m.set_edge(e,(0,-1));count-=delta
                try:
                    if family=='corridors':
                        end=min(w-2,max(4,min(12,w//3)))
                        for x in range(1,end+1):
                            m.set_edge(2*w+x,(1,-1));m.set_edge(3*w+x,(1,-1))
                        m.set_edge(m.n+2*w+1,(1,-1))
                        for x in range(2,end+2): m.set_edge(m.n+2*w+x,(0,-1))
                    place_starts(m,layouts[i],rng,family);supply(m,family,inside,rng)
                    reasons=outside_reasons(m,bounds)
                    if inside and reasons: continue
                    checks=validate(m)
                    if family=='corridors': assert any(len(xs)==1 for xs in m.graph())
                except (ValueError,AssertionError): continue
                break
            else: raise RuntimeError(f'Could not generate {family} {w}x{h}')
            name=f'gx_{family}_{w}x{h}_{seed}'
            text=m.text(name);p=ROOT/'maps'/f'{name}.map';p.write_text(text)
            loaded=read_map(p);assert loaded.text(name)==text
            checks=validate(loaded)
            records.append(dict(name=p.name,family=family,seed=seed,retry=retry,range='inside' if inside else 'outside',
                outside_reasons=reasons,sha256=hashlib.sha256(text.encode()).hexdigest(),**metrics(m),checks=checks))
            print(name, 'inside' if inside else 'outside',flush=True)
    return records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=int,default=910900)
    parser.add_argument('--skip-loader',action='store_true',help='Generate static checks only; completion is not certified')
    args=parser.parse_args()
    ROOT.joinpath('maps').mkdir(exist_ok=True)
    rows,bounds=ladder();records=generate(bounds,args.seed)
    if not args.skip_loader:
        from loader_check import load_only
        for r in records:
            r['loader']=load_only((ROOT/'maps'/r['name']).read_bytes())
            assert r['loader']['loaded'] and not r['loader']['notices'],(r['name'],r['loader'])
    assert len(records)==64 and sum(r['range']=='inside' for r in records)==32
    assert all(sum(r['family']==f for r in records)==8 for f in FAMILIES)
    fields=['name','family','w','h','cells','symmetry','portals','bearing_tiles','start_layout','ladder_range']
    with (ROOT/'maps/INDEX.tsv').open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=fields,delimiter='\t');writer.writeheader()
        for r in records:
            writer.writerow({**{k:r[k] for k in fields if k in r},'bearing_tiles':r['bearing'],
                'start_layout':'A:'+','.join(map(str,r['starts'][0]))+';B:'+','.join(map(str,r['starts'][1])),
                'ladder_range':r['range']})
    (ROOT/'validation.json').write_text(json.dumps(dict(seed=args.seed,records=records),indent=2)+'\n')
    done=[datetime.now().astimezone().isoformat(), '64 maps: 8 families × 8; 32 inside the measured numeric ladder envelope, 32 outside but legal.',
        'Static checks: declared tile/edge/body symmetry, portal pairing and orientation, contiguous nonoverlapping starting bodies, pearl reachability for every start, at least one immediately free first step for every start.',
        'Loader: '+('NOT CHECKED (--skip-loader).' if args.skip_loader else '64/64 accepted by installed engine 1.2.7, no correction notices. Abort on first spawn; 0 bot processes and 0 turns.'),
        'Deterministic rerun: PYTHONDONTWRITEBYTECODE=1 ~/meow-redteam/engine/venv/bin/python data/codex/astra/mapgen/gen.py --seed '+str(args.seed),
        'Could not validate: actual gameplay, bot CPU, competitive balance, or eventual survival (no games authorized). Reachability is topological, not a strategy guaranteeing survival. Current server pearl timers are not independently verified; ladder reconstructions can contain estimates. The requested nice -n 10 command was attempted; this sandbox reports setpriority Operation not permitted. Diagonal symmetry is not legal; rotation family uses engine-supported xy (180°). All generated maps use xy.',
        'Roster discrepancy resolved from offline one5-w1.json: 15 current names vs 19 historical maps.json records; table uses actual local files and labels provenance. Lone length-4 queen is requested by the brief but absent from the 15 local configurations; included as legal outside-range coverage.',
        'Output only under data/codex/astra/mapgen/. No analysis report, no card, no network, no games.']
    (ROOT/'done.txt').write_text('\n'.join(done)+'\n')

if __name__=='__main__':
    main()
