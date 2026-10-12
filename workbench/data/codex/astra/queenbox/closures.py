"""Reconstruct actor choices at each final closure; no game execution."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
from collections import deque
sys.path[:0]=['data/analysis/ladder/dossier/local']
from replay_format import load,point
from count_local import Geo
OUT=Path('data/codex/astra/queenbox')

def scan(g):
    close=g['closures'][-1] if g['closures'] else None
    if not close:return {}
    target=close['event'];qid=g['queen'];w=g['width'];h=g['height']
    root=load(g['path']).root();bodies={};teams={};raw=[];pearls=set()
    for line in root.text(0).splitlines():
        t=line.split()
        if t[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque(int(t[4+2*k])*w+int(t[3+2*k]) for k in range(int(t[2])));teams[i]=int(t[1])
        elif t[0]=='EDGE':raw.append(tuple(map(int,t[1:4])))
    geo=Geo(w,h,raw);rnd=-1;actor=None;ctx=None
    tile=lambda p:point(p)[1]*w+point(p)[0]
    def xy(c):return [c%w,c//w]
    def context():
        occ={c:i for i,b in bodies.items() for c in b};b=list(bodies[actor]);q=list(bodies[qid]);qh=q[0]
        choices=[]
        for d,(k,c) in enumerate(geo.moves[b[0]]):
            if k==1 or c in occ:continue
            nb=[c]+b
            if c not in pearls:nb.pop()
            occupied=(set(occ)-set(b))|set(nb)
            nq=nb if actor==qid else q
            exits=[xy(n) for ek,n in geo.moves[nq[0]] if ek!=1 and n not in occupied]
            self_exits=sum(ek!=1 and n not in occupied for ek,n in geo.moves[nb[0]])
            choices.append(dict(d='NESW'[d],cell=xy(c),pearl=c in pearls,queen_exits=exits,self_exits=self_exits,portal=k==2))
        qfree=[xy(n) for k,n in geo.moves[qh] if k!=1 and n not in occ]
        visible=geo.window(b[0])
        return dict(round=rnd,actor=actor,ally=teams[actor]==teams[qid],length=len(b),head=xy(b[0]),queen_head=xy(qh),
                    queen_free=qfree,queen_visible=qh in visible,all_queen_neighbors_visible=all(n in visible for k,n in geo.moves[qh] if k!=1),
                    choices=choices,pearls=0,moves=[],split=False)
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0)
        if k not in (0,1,3,9,10,11):continue
        p=ev.pointer(0)
        if k==0:rnd=p.i32(0)
        elif k==1:
            actor=p.i32(0)
            ctx=context() if actor==close['actor'] and rnd==close['round'] else None
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:
                pearls.discard(c)
                if ctx:ctx['pearls']+=1
        elif k==9:
            i=p.i32(0);hd=tile(p.pointer(0));tl=tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd)
                if ctx and i==actor:ctx['moves'].append(xy(hd))
            while len(b)>1 and b[-1]!=tl:b.pop()
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(tile(c) for c in p.pointer(z));teams[i]=p.u16(8)
            if ctx:ctx['split']=True
        elif k==11:bodies.pop(p.i32(0))
        if idx==target:return dict(game=g['game'],closure=close,actor_turn=ctx)
    raise AssertionError(g['game'])

def main():
    rows=list(map(json.loads,(OUT/'games.jsonl').read_text().splitlines()))
    out=[]
    for g in rows:
        if g.get('bot') and g['bot'] not in {'20850','20880','20910','20941','20980'}:continue
        d=g.get('death')
        if not d or d['reason']==3:continue
        out.append(scan(g))
    (OUT/'closure-actors.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print('closures audited',len(out))
if __name__=='__main__':main()
