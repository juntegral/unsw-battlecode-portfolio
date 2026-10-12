import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter
ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'data/analysis/ladder/dossier/local'))
sys.path.insert(0, str(ROOT/'tools'))
import scoreboard as sb
from count_local import Geo
from replay_format import point
import ladder_replay as lr

def scan(gid):
    path=ROOT/f'data/online/smoke/one14-c1-old/M{gid}.replay'
    meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
    base=lr.scan(path,meta,'one14-c1-old',set())
    root=sb.load_replay(path).root()
    w,h=map(int,root.text(0).splitlines()[0].split()[1:3])
    b,teams,raw={},{},[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q[0]=='DRAGON':
            i=len(b); teams[i]=int(q[1]); b[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        if q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    geo=Geo(w,h,raw); queens=[min(i for i in b if teams[i]==s) for s in (0,1)]
    xy=lambda c:[c%w,c//w]
    tile=lambda p:point(p)[1]*w+point(p)[0]
    rounds,turns,qt,splits,death_context=[],[],[[],[]],[],[]
    pearls=set(); rnd=-1; actor=None; cur=None
    nearest=None; near_examples=[]; near_turns=0; queen_boards=[]
    rev=[[] for _ in range(w*h)]
    for c,adj in enumerate(geo.adj):
        for d in adj: rev[d].append(c)
    distances={}
    def dist(target):
        if target not in distances:
            ds={target:0}; queue=deque([target])
            while queue:
                c=queue.popleft()
                for d in rev[c]:
                    if d not in ds: ds[d]=ds[c]+1; queue.append(d)
            distances[target]=ds
        return distances[target]
    def proximity(event):
        nonlocal nearest
        if queens[0] in b or queens[1] not in b: return
        target=b[queens[1]][0]; ds=dist(target)
        for i,body in b.items():
            if teams[i]!=0:continue
            d=ds.get(body[0],99999)
            if nearest is None or d<nearest['distance']:
                nearest=dict(round=rnd,event=event,id=i,distance=d,head=xy(body[0]),queen=xy(target))
                near_examples.append(nearest)
    def board():
        center=b[queens[0]][0]; cx,cy=xy(center); cells={}
        for i,body in b.items():
            for k,c in enumerate(body):cells[c]=('Q' if i==queens[0] else 'K' if i==queens[1] else 'A' if teams[i]==0 else 'E') if k==0 else ('q' if i==queens[0] else 'a' if teams[i]==0 else 'e')
        rows=[]
        for dy in range(-3,4):
            row=''
            for dx in range(-3,4):
                c=((cy+dy)%h)*w+(cx+dx)%w
                row+=cells.get(c,'*' if c in pearls else '.')
            rows.append(row)
        edges=[]
        for dy in range(-3,4):
            for dx in range(-3,4):
                c=((cy+dy)%h)*w+(cx+dx)%w
                for d,(kind,dest) in enumerate(geo.moves[c]):
                    if kind: edges.append([dx,dy,'NESW'[d],kind,xy(dest)])
        nearby={i:dict(side=teams[i],length=len(body),body=[xy(c) for c in body]) for i,body in b.items() if any(c in geo.window(center) for c in body)}
        return dict(round=rnd,head=xy(center),length=len(b[queens[0]]),rows=rows,edges=edges,nearby=nearby)
    def finish():
        if cur is not None:
            cur['end']=xy(b[actor][0]) if actor in b else None
            cur['end_length']=len(b.get(actor,()))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            finish();cur=None;rnd=p.i32(0);actor=None
        elif k==1:
            finish();actor=p.i32(0)
            cur=dict(round=rnd,event=idx,id=actor,side=teams[actor],length=len(b[actor]),head=xy(b[actor][0]),steps=[],eats=0)
            turns.append(cur)
            if actor in queens:
                qt[teams[actor]].append(cur)
                if actor==queens[0]:queen_boards.append(board())
            proximity(idx)
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c);cur['eats']+=1
        elif k==4:
            a=p.pointer(0)
            cur['action_kind']=a.u16(0) if a else None
            cur['directions']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
        elif k==9:
            i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));body=b[i]
            if body[0]!=hd:
                body.appendleft(hd)
                if i==actor:cur['steps'].append(xy(hd))
            while len(body)>1 and body[-1]!=tail:body.pop()
            assert body[-1]==tail
            proximity(idx)
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            splits.append(dict(round=rnd,parent=parent,child=child,before=len(b[parent])))
            for z,i in enumerate((parent,child)):
                b[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
            splits[-1].update(parent_length=len(b[parent]),child_length=len(b[child]))
            proximity(idx)
        elif k==11:
            i=p.i32(0)
            if i in queens or len(b[i])>=8:
                death_context.append(dict(round=rnd,event=idx,id=i,actor=actor,reason=p.u16(4),length=len(b[i]),body=[xy(c) for c in b[i]],turn=cur,others={j:dict(side=teams[j],length=len(bb),head=xy(bb[0])) for j,bb in b.items() if j!=i}))
            b.pop(i);proximity(idx)
    finish()
    assert len(b)==sum(base['final'][s]['alive'] for s in ('us','them'))
    neg=[r for r,st in base['snapshots'].items() if st['us']['total']>=st['them']['total']]
    permanent=max(neg)+1 if neg else 0
    def standing(st):
        return tuple(st[k] for k in ('queen_length','longest','total'))
    not_losing=[r for r,st in base['snapshots'].items() if standing(st['us'])>=standing(st['them'])]
    permanent_standing=max(not_losing)+1 if not_losing else 0
    chosen=['gid','map','queens','q_eats','q_splits','final','last_round','winner','end_reason','eats','anomalies']
    result={key:base[key] for key in chosen}
    result.update(bot=root.text(1),size=[w,h],permanent_total_behind=permanent,permanent_standing_behind=permanent_standing,post_queen_nearest=nearest,proximity_improvements=near_examples,
                  queen_deaths=[d for d in base['deaths'] if d['id'] in queens],long_deaths=[d for d in base['deaths'] if d['side']=='us' and d['length']>=8],
                  snapshots={r:st for r,st in base['snapshots'].items() if r%25==0 or r in (1,2,3,5,10,permanent,base['last_round'])},
                  last_deaths=base['deaths'][-12:],queen_turns=qt,queen_last_boards=queen_boards[-3:],queen_splits=[s for s in splits if s['parent'] in queens],death_context=death_context,
                  extra_boards=[z for z in queen_boards if z['round'] in (14,25,37,50,65,66,67,156,157,158,217,218,219,220,221,222,223)])
    (OUT/f'{gid}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (OUT/f'{gid}-turns.json').write_text(json.dumps(turns,separators=(',',':')))
    print(json.dumps({k:v for k,v in result.items() if k not in ('queen_turns','queen_last_boards','death_context','snapshots','long_deaths','last_deaths')},ensure_ascii=False))
    print('snapshots',result['snapshots'])
    print('last queens',qt[0][-3:])
    print('long deaths',[(d['id'],d['round'],d['length'],d['cause'],d['actor']) for d in result['long_deaths']])

if __name__=='__main__':
    for gid in (1517689,1517690,1517693):scan(gid)
