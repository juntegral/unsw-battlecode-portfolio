import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
import ladder_replay as lr
import o1_scan
import ast,types
geo_path=Path('data/analysis/ladder/dossier/work/tq2_scan.py')
module=ast.parse(geo_path.read_text());module.body=[n for n in module.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.Assign,ast.FunctionDef,ast.ClassDef))]
geo_module=types.ModuleType('geo_import');exec(compile(module,str(geo_path),'exec'),geo_module.__dict__);Geo=geo_module.Geo
OUT=Path(__file__).parent
JOBS=[(1485181,'data/online/smoke/one8-k1-old',0),(1485182,'data/online/smoke/one8-k1-old',0),(1485486,'data/online/live-one1/b1485486',1),(1485489,'data/online/live-one1/b1485486',1),(1485490,'data/online/live-one1/b1485486',1)]
def run(gid,folder,own):
    path=Path(folder)/f'M{gid}.replay'; meta=json.loads((Path(folder)/f'game-{gid}.json').read_text())
    base=lr.scan(path,meta,folder,set()); ledger=o1_scan.scan('loss3',path,meta)
    root=lr.replay.load(path).root(); lines=root.text(0).splitlines(); w,h=map(int,lines[0].split()[1:3]);bodies={}; teams={}; raw=[]
    for line in lines:
        p=line.split()
        if p[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque(int(p[4+2*k])*w+int(p[3+2*k]) for k in range(int(p[2])));teams[i]=int(p[1])
        elif p[0]=='EDGE':raw.append(tuple(map(int,p[1:4])))
    geo=Geo(w,h,raw);qs=[min(i for i in teams if teams[i]==s) for s in (own,1-own)];pearls=set();turns=[]; qt=[];t=None;r=-1;near=[];enemy_q_positions=set(); deadq=False
    def xy(c): return [c%w,c//w]
    def board(c):
        occ={p:('Q' if i==qs[0] and k==0 else 'K' if i==qs[1] and k==0 else 'A' if teams[i]==own and k==0 else 'E' if teams[i]!=own and k==0 else 'a' if teams[i]==own else 'e') for i,b in bodies.items() for k,p in enumerate(b)}
        rows=[]
        for dy in range(-3,4):
            top='';mid=''
            for dx in range(-3,4):
                x,y=(c%w+dx)%w,(c//w+dy)%h;p=y*w+x
                nk=geo.edges.get(lr.edge_id(w,h,x,y,0),(0,-1))[0];wk=geo.edges.get(lr.edge_id(w,h,x,y,3),(0,-1))[0]
                top+='+'+('---' if nk==1 else '~~~' if nk==2 else '   ')
                mid+=('|' if wk==1 else '~' if wk==2 else ' ')+f' {occ.get(p,"*" if p in pearls else ".")} '
            ex=(c%w+4)%w;ey=(c//w+dy)%h;ek=geo.edges.get(lr.edge_id(w,h,ex,ey,3),(0,-1))[0]
            rows += [top+'+',mid+('|' if ek==1 else '~' if ek==2 else ' ')]
        bot=''
        for dx in range(-3,4):
            x,y=(c%w+dx)%w,(c//w+4)%h;k=geo.edges.get(lr.edge_id(w,h,x,y,0),(0,-1))[0];bot+='+'+('---' if k==1 else '~~~' if k==2 else '   ')
        return '\n'.join(rows+[bot+'+'])
    def close():
        if t is not None:t['end']=xy(bodies[t['id']][0]) if t['id'] in bodies else None;t['endL']=len(bodies.get(t['id'],[]))
    def proximity(event):
        if deadq and qs[1] in bodies:
            q=bodies[qs[1]][0];enemy_q_positions.add(tuple(xy(q)))
            for i,b in bodies.items():
                if teams[i]==own:
                    d=geo.ball(b[0]).get(q,99)
                    if d<=5:near.append(dict(r=r,id=i,L=len(b),d=d,head=xy(b[0]),queen=xy(q),event=event))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:close();t=None;r=p.i32(0)
        elif k==1:
            close();i=p.i32(0);t=dict(r=r,id=i,side=teams[i],L=len(bodies[i]),head=xy(bodies[i][0]),steps=[],eats=[],split=None,action=None)
            turns.append(t)
            if i in qs:
                t['board']=board(bodies[i][0]);t['nearby']=[dict(id=j,side=teams[j],L=len(b),body=[xy(c) for c in b]) for j,b in bodies.items() if any(min(abs(c%w-bodies[i][0]%w),w-abs(c%w-bodies[i][0]%w))<=3 and min(abs(c//w-bodies[i][0]//w),h-abs(c//w-bodies[i][0]//w))<=3 for c in b)]
                qt.append(t)
            proximity(idx)
        elif k==4:
            a=p.pointer(0);t['action']={'type':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []}
        elif k==3:
            pt=lr.replay.point(p.pointer(0));c=pt[1]*w+pt[0]
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c);t['eats'].append(list(pt))
        elif k==9:
            i=p.i32(0);hd=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1));hd=hd[1]*w+hd[0];tl=tl[1]*w+tl[0];b=bodies[i]
            if b[0]!=hd:b.appendleft(hd);t['steps'].append(xy(hd))
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl
            proximity(idx)
        elif k==10:
            pa,ch=p.i32(0),p.i32(4);t['split']=[pa,ch]
            for z,i in enumerate((pa,ch)):bodies[i]=deque(pt.i32(4)*w+pt.i32(0) for pt in p.pointer(z));teams[i]=p.u16(8)
            proximity(idx)
        elif k==11:
            i=p.i32(0);bodies.pop(i)
            if i==qs[0]:deadq=True
            proximity(idx)
    close()
    base.pop('intervals',None);base['ledger']=ledger;base['turns']=turns;base['qturns']=qt;base['near_after_qdeath']=near;base['enemy_q_positions_after']=sorted(enemy_q_positions);base['size']=[w,h];base['meta']=meta
    (OUT/f'{gid}.json').write_text(json.dumps(base,ensure_ascii=False))
    print(gid,base['bots'],base['final'],'queen deaths',[(d['id'],d['round'],d['cause'],d['actor'],d['body']) for d in base['deaths'] if d['id'] in qs], 'near',len(near),'first',near[:1])
for job in JOBS:run(*job)
