"""Offline death-cell census. Writes only in this directory; imports existing readers/counters."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter, defaultdict, deque

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/online'),
               str(ROOT/'data/analysis/ladder/dossier/work')]
import label_report as lr
import o1_scan
from ladder_replay import edge_id, canonical_edges

BOTS = {'20850':'one1', '20880':'one2', '20910':'one3', '20941':'one4', '20980':'one5'}
STEP = ((0,-1),(1,0),(0,1),(-1,0))

class Geo:
    def __init__(self, text):
        self.w,self.h = map(int,text.splitlines()[0].split()[1:3])
        raw=[tuple(map(int,l.split()[1:4])) for l in text.splitlines() if l.startswith('EDGE ')]
        self.edges=canonical_edges(self.w,self.h,raw)
        self.portals=defaultdict(list)
        for e,(k,p) in self.edges.items():
            if k==2:self.portals[p].append(e)
        self.rev=defaultdict(set)
        for y in range(self.h):
            for x in range(self.w):
                for d in range(4):
                    if self.kind((x,y),d)!=1:self.rev[self.dest((x,y),d)].add((x,y))
        self.near={};self.components={}
    def kind(self,c,d):return self.edges.get(edge_id(self.w,self.h,*c,d),(0,-1))[0]
    def dest(self,c,d):
        e=edge_id(self.w,self.h,*c,d);k,p=self.edges.get(e,(0,-1))
        if k==2:
            z=next(z for z in self.portals[p] if z!=e);row,x=divmod(z,self.w+1)
            return ((x-(d==3))%self.w,(row//2-(d==0))%self.h)
        dx,dy=STEP[d];return ((c[0]+dx)%self.w,(c[1]+dy)%self.h)
    def attackers3(self,c):
        if c not in self.near:
            seen={c};front={c}
            for _ in range(3):
                front={t for x in front for t in self.rev[x]}-seen;seen|=front
            self.near[c]=seen
        return self.near[c]
    def man(self,a,b):
        dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1])
        return min(dx,self.w-dx)+min(dy,self.h-dy)
    def window(self,c):
        return {((c[0]+dx)%self.w,(c[1]+dy)%self.h) for dy in range(-3,4) for dx in range(-3,4)}
    def component(self,c):
        if c in self.components:return self.components[c]
        seen={c};q=deque([c])
        while q:
            a=q.popleft()
            for d in range(4):
                if self.kind(a,d)==0:
                    t=self.dest(a,d)
                    if t not in seen:seen.add(t);q.append(t)
        for x in seen:self.components[x]=seen
        return seen

def initial(text):
    bodies={};teams={}
    for line in text.splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
            teams[i]=int(q[1])
    return bodies,teams

def census(path,meta,root,details=False):
    # Reuse and cross-check the original length/death counter on the very same decoded replay.
    original_load=o1_scan.replay.load
    o1_scan.replay.load=lambda _:type('Loaded',(),{'root':lambda _:root})()
    try: base=o1_scan.scan(path.parent.name,path,meta)
    finally:o1_scan.replay.load=original_load
    geo=Geo(root.text(0));bodies,teams=initial(root.text(0));own=int(meta['teamAId']!=1119)
    queens={s:min(i for i in bodies if int(teams[i]!=own)==s) for s in (0,1)}
    side=lambda i:int(teams[i]!=own)
    pearls=set();entries={};born={};seen=defaultdict(set);seen_edges=defaultdict(set)
    died=[];rnd=-1;actor=None;dirs=[];used=0;pending=None;context=None
    histories=defaultdict(list);remembered=defaultdict(set)
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:rnd=p.i32(0);actor=None
        elif k==1:
            actor=p.i32(0);dirs=[];used=0
            if details and actor in details:
                window=geo.window(bodies[actor][0]);seen[actor]|=window
                remembered[actor]-=window;remembered[actor]|=pearls&window
                seen_edges[actor]|={edge_id(geo.w,geo.h,*c,d) for c in window for d in range(4)}
                context=dict(r=rnd,id=actor,head=bodies[actor][0],body=list(bodies[actor]),
                             bodies={str(i):list(b) for i,b in bodies.items()},teams=dict(teams),
                             pearls=list(pearls),seen=list(seen[actor]),seen_edges=list(seen_edges[actor]),
                             window=list(window),remembered_pearls=list(remembered[actor]))
                histories[actor].append(context)
                histories[actor]=histories[actor][-4:]
        elif k==4:
            a=p.pointer(0);dirs=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [];used=0
        elif k==3:
            c=o1_scan.replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c);pending=c
        elif k==9:
            i=p.i32(0);hd=o1_scan.replay.point(p.pointer(0));tl=o1_scan.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                src=b[0];direction=dirs[used] if i==actor and used<len(dirs) else None
                ent=dict(r=rnd,event=idx,src=src,dest=hd,direction=direction,
                         portal=direction is not None and geo.kind(src,direction)==2,
                         pearl=pending==hd,length_before=len(b),birth=False)
                if details and i in details:ent['context']=context;ent['before_body']=list(b)
                entries[i]=ent;b.appendleft(hd)
                if i==actor:used+=1
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl
            if pending==hd:pending=None
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):
                old=bodies.get(i);bb=deque(o1_scan.replay.point(c) for c in p.pointer(z))
                if old is None or old[0]!=bb[0]:
                    entries[i]=dict(r=rnd,event=idx,src=None,dest=bb[0],direction=None,portal=False,pearl=False,length_before=len(bb),birth=True)
                bodies[i]=bb;teams[i]=p.u16(8);born[i]=rnd
        elif k==11:
            i=p.i32(0);b=bodies[i];s=side(i);reason=p.u16(4);ref=base['deaths'][len(died)]
            assert (ref[0],ref[1],ref[2],ref[20])==(rnd,s,len(b),list(b[0]))
            enemies=[bb[0] for z,bb in bodies.items() if side(z)!=s]
            entry=entries.get(i)
            cell=b[0];comp=geo.component(cell)
            rec=dict(gid=meta['id'],r=rnd,id=i,side=s,length=len(b),queen=i==queens[s],cell=cell,
                     cause=ref[4],reason=reason,event=idx,
                     no_enemy3=not any(c in geo.attackers3(cell) for c in enemies),
                     no_enemy_man3=not any(geo.man(cell,c)<=3 for c in enemies),
                     entry=entry,split_age=rnd-born[i] if i in born else None,
                     component_size=len(comp),component_pearls=len(comp&pearls),pearl_here=cell in pearls,
                     body=list(b),free_sides=ref[5])
            if details and i in details:
                rec['death_context']=context;rec['history']=histories[i]
            died.append(rec);del bodies[i]
    assert len(died)==len(base['deaths'])
    for s in (0,1):
        ls=[len(b) for i,b in bodies.items() if side(i)==s]
        assert (len(ls),sum(ls),max(ls,default=0),len(bodies.get(queens[s],())))==tuple(base['ends'][s][:4])
        assert sum(len(bb) for i,bb in initial(root.text(0))[0].items() if side(i)==s)+sum(e[1]==s for e in base['eats'])-sum(d['length'] for d in died if d['side']==s)-sum(p[3] for p in base['paids'] if p[1]==s)==sum(ls)
    return dict(gid=meta['id'],path=str(path),map=meta['mapName'],bot=base['bot'],version=BOTS.get(base['bot'],'TEST20905'),
                ranked=meta.get('ranked'),opp=base['opp'],w=geo.w,h=geo.h,deaths=died)

def repeated(g,field='no_enemy3'):
    groups=defaultdict(list)
    for d in g['deaths']:
        if d['cause'] in ('wall','own body','mate body') and d[field]:groups[d['side'],tuple(d['cell'])].append(d)
    return [(s,c,ds) for (s,c),ds in groups.items() if len(ds)>=2]

def main():
    inv=lr.directory_inventory('deathcell','data/online/smoke/one[1-5]*-old,data/online/live-one1/b*')
    rows=[];excluded=[];tests=[]
    with (OUT/'games.jsonl').open('w') as f:
        for n,(path,meta) in enumerate(inv['jobs']):
            root=lr.agg.sb.load_replay(path).root();bot=root.text(1+int(meta['teamAId']!=1119))
            if bot not in BOTS and bot!='20905':
                excluded.append(dict(gid=meta['id'],bot=bot));continue
            g=census(path,meta,root)
            if bot=='20905':tests.append(g)
            else:rows.append(g);f.write(json.dumps(g,separators=(',',':'))+'\n');f.flush()
            if n%10==0:print('scanned',n+1,'/',len(inv['jobs']),flush=True)
    (OUT/'test20905.jsonl').write_text(''.join(json.dumps(g,separators=(',',':'))+'\n' for g in tests))
    (OUT/'coverage.json').write_text(json.dumps(dict(notes=inv['notes'],excluded=excluded,core=len(rows),test=len(tests),versions=dict(Counter(g['version'] for g in rows))),indent=2))
    print('done',len(rows),'core;',len(tests),'test;',len(excluded),'excluded',flush=True)

if __name__=='__main__':main()
