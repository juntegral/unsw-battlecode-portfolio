import sys, json
from pathlib import Path
from collections import deque, Counter
sys.dont_write_bytecode = True
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
from count_local import Geo

def run(gid):
    path = ROOT/f'data/online/smoke/one13-p1-old/M{gid}.replay'
    meta = json.loads(path.with_name(f'game-{gid}.json').read_text())
    base = lr.scan(path, meta, 'one13-p1-old', set())
    base.pop('intervals')
    root = lr.replay.load(path).root()
    w,h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        q = line.split()
        if q[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
        elif q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    geo=Geo(w,h,raw); queens=[base['queens']['us'],base['queens']['them']]
    pearls=set(); turns=[]; qt=[]; splits=[]; cur=None; rnd=-1
    seen={i:set() for i in bodies}
    xy=lambda c:[c%w,c//w]
    tile=lambda p: p.i32(4)*w+p.i32(0)
    def board(head):
        cells={c:('.' if c not in pearls else '*') for c in range(w*h)}
        for i,b in bodies.items():
            for c in b:cells[c]='a' if teams[i]==0 else 'b'
            cells[b[0]]='Q' if i==queens[0] else 'K' if i==queens[1] else 'A' if teams[i]==0 else 'B'
        return [''.join(cells[((head//w+dy)%h)*w+(head%w+dx)%w] for dx in range(-3,4)) for dy in range(-3,4)]
    def finish():
        if cur is not None:
            cur['end']=list(bodies.get(cur['id'],[]))
            turns.append(cur)
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0: finish();cur=None;rnd=p.i32(0)
        elif k==1:
            finish();i=p.i32(0);head=bodies[i][0]
            seen.setdefault(i,set()).update(geo.window(head))
            cur=dict(r=rnd,event=idx,id=i,side=teams[i],body=list(bodies[i]),path=[],dirs=[],eat=0,units=sum(teams[z]==teams[i] for z in bodies),portal_options=[])
            for d,(kind,dest) in enumerate(geo.moves[head]):
                if kind==2:cur['portal_options'].append(dict(dir=d,dest=xy(dest),seen=dest in seen[i]))
            if i==queens[0]:
                cur['board']=board(head)
                cur['near']={z:dict(length=len(b),head=xy(b[0])) for z,b in bodies.items() if b[0] in geo.window(head)}
                cur['edges']=[[geo.moves[((head//w+dy)%h)*w+(head%w+dx)%w][d][0] for d in range(4)] for dy in range(-3,4) for dx in range(-3,4)]
                qt.append(cur)
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c);cur['eat']+=1
        elif k==4:
            a=p.pointer(0)
            cur['action']=a.u16(0) if a else None
            cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
            if a and a.u16(0)==1:cur['split_action']=a.i32(4)
        elif k==9:
            i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                if cur and i==cur['id']:cur['path'].append(hd)
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            splits.append(dict(r=rnd,parent=parent,child=child,before=list(bodies[parent])))
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
            splits[-1]['after']=[list(bodies[parent]),list(bodies[child])]
        elif k==11:bodies.pop(p.i32(0))
    finish()
    base.update(width=w,height=h,turns=turns,queen_turns=qt,splits=splits,final_bodies={i:list(b) for i,b in bodies.items()})
    (OUT/f'{gid}.json').write_text(json.dumps(base,ensure_ascii=False))
    print(gid,'saved',len(turns),'turns',flush=True)
    print('last Q',[(t['r'],xy(t['body'][0]),len(t['body']),t['dirs'],[xy(c) for c in t['path']],t['near']) for t in qt[-3:]],flush=True)
    for label,key in [('longest','longest'),('total','total')]:
        ss=base['snapshots'];last=max((r for r,s in ss.items() if s['us'][key]>=s['them'][key]),default=-1)
        print('permanent behind',label,last+1,flush=True)
    print('Q splits',[s for s in splits if s['parent']==queens[0]],flush=True)

if __name__=='__main__':
    for gid in (1507922,1507923,1507925):run(gid)
