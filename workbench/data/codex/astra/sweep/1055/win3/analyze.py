import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter, defaultdict, deque

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/work'),
               str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
import o1_scan
import scoreboard
from count_local import Geo

JOBS = [(1501266,'live-one1/b1501263'), (1502774,'live-one1/b1502774'),
        (1502777,'live-one1/b1502774')]
JOBS += [(i,'live-one1/b1507592') for i in range(1507593,1507597)]
JOBS += [(i,'smoke/one13-c1-old') for i in (1506213,1506214,1506215,1506222,1506223)]

def scan(gid, folder):
    path = ROOT/'data/online'/folder/f'M{gid}.replay'
    meta = json.loads(path.with_name(f'game-{gid}.json').read_text())
    decoded = scoreboard.load_replay(path)
    lr.replay.load = lambda _: decoded
    base = lr.scan(path,meta,folder,set())
    ledger = o1_scan.scan(folder,path,meta)
    root = lr.replay.load(path).root()
    own = int(meta['teamAId'] != 1119)
    bot = int(root.text(own+1))
    assert bot == (21330 if gid in (1501266,1502774,1502777) else 21377)
    assert base['winner'] == 'AB'[own] and ledger['result']=='win'
    bodies,teams,raw = {},{},[]
    for line in root.text(0).splitlines():
        p=line.split()
        if not p: continue
        if p[0]=='MAP': w,h=map(int,p[1:3])
        elif p[0]=='DRAGON':
            i=len(bodies);teams[i]=int(p[1])
            bodies[i]=deque(int(p[4+2*k])*w+int(p[3+2*k]) for k in range(int(p[2])))
        elif p[0]=='EDGE': raw.append(tuple(map(int,p[1:4])))
    geo=Geo(w,h,raw)
    queen,eq=base['queens']['us'],base['queens']['them']
    def man(a,b):
        dx,dy=abs(a%w-b%w),abs(a//w-b//w)
        return min(dx,w-dx)+min(dy,h-dy)
    def path_to(src,dst,occ,cap=1):
        seen={src:0};todo=deque([src])
        while todo:
            c=todo.popleft()
            if seen[c]>=cap: continue
            for n in geo.adj[c]:
                if n==dst: return seen[c]+1
                if n not in occ and n not in seen:
                    seen[n]=seen[c]+1;todo.append(n)
        return None
    def snap():
        return [dict(n=sum(teams[i]==s for i in bodies),
                     q=len(bodies.get(queen if s==own else eq,())),
                     longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),
                     total=sum(len(b) for i,b in bodies.items() if teams[i]==s)) for s in (own,1-own)]
    rnd,actor,cur=-1,None,None
    pearls=set();turns=[];snaps={};sonars=[];logs=[];peak=[0,0];adjrisk=[]
    def finish():
        nonlocal cur
        if cur is None:return
        cur['end']=bodies[actor][0] if actor in bodies else None
        cur['endL']=len(bodies.get(actor,()))
        turns.append(cur);cur=None
    def risks(event):
        if queen not in bodies:return
        qh=bodies[queen][0]
        foes=[[i,len(b),b[0]] for i,b in bodies.items() if teams[i]!=own and qh in geo.adj[b[0]]]
        if foes:adjrisk.append(dict(r=rnd,event=event,qL=len(bodies[queen]),qh=qh,foes=foes))
    for idx,ev in enumerate(root.pointer(3)):
        k,p=ev.u16(0),ev.pointer(0)
        if k==0:
            finish()
            if rnd>=0:snaps[rnd]=snap()
            rnd,actor=p.i32(0),None
        elif k==1:
            finish();actor=p.i32(0)
            b=bodies[actor];hd=b[0];occ={c for bb in bodies.values() for c in bb}
            foes=[(i,bb) for i,bb in bodies.items() if teams[i]!=teams[actor]]
            free=[n for n in geo.adj[hd] if n not in occ]
            cur=dict(r=rnd,event=idx,i=actor,ours=teams[actor]==own,L=len(b),h=hd,
                     body=list(b),steps=[],eats=[],deaths=[],dirs=[],split=None,
                     n=sum(teams[i]==teams[actor] for i in bodies),
                     eqL=len(bodies.get(eq,())),qL=len(bodies.get(queen,())),
                     free=free,adjpearls=[c for c in free if c in pearls],
                     heading=next((d for d,(kind,n) in enumerate(geo.moves[b[1]]) if kind!=1 and n==hd),None),
                     nearest_foe=min([[man(hd,bb[0]),i,len(bb),bb[0]] for i,bb in foes],default=None),
                     visible_foes=[[i,len(bb),bb[0]] for i,bb in foes if bb[0] in geo.window(hd)],
                     near_mates=[[i,len(bb),bb[0],man(hd,bb[0])] for i,bb in bodies.items()
                                 if i!=actor and teams[i]==teams[actor] and man(hd,bb[0])<=6],
                     enemy_step1=[[i,len(bb),bb[0]] for i,bb in foes if hd in geo.adj[bb[0]]],
                     long_escape_near=any(man(hd,bb[0])<=5 for _,bb in foes))
            if actor==queen:
                cur['blocking']=[[i,len(bb),n] for n in geo.adj[hd] for i,bb in bodies.items() if n in bb]
                cur['foe_paths']=[[i,len(bb),bb[0],path_to(bb[0],hd,occ,5)]
                                  for i,bb in foes if man(hd,bb[0])<=6]
        elif k==3:
            c=lr.replay.point(p.pointer(0));cell=c[1]*w+c[0]
            if p.u32(0):pearls.add(cell)
            else:pearls.remove(cell);cur['eats'].append(cell)
        elif k==4:
            a=p.pointer(0);cur['action']=a.u16(0) if a else None
            cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
            cur['tle']=p.bit(32);usage=p.pointer(1);cur['cpu']=usage.u64(0) if usage else None
        elif k==6:logs.append(dict(r=rnd,i=p.i32(0),text=p.text(0)))
        elif k==9:
            i=p.i32(0);pt=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1))
            hd,tail=pt[1]*w+pt[0],tl[1]*w+tl[0];b=bodies[i]
            if b[0]!=hd:
                if i==actor:cur['steps'].append(hd)
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            risks(idx)
        elif k==10:
            parent,child=p.i32(0),p.i32(4);before=len(bodies[parent])
            for z,i in enumerate((parent,child)):
                bodies[i]=deque((pt:=lr.replay.point(c))[1]*w+pt[0] for c in p.pointer(z));teams[i]=p.u16(8)
            cur['split']=[parent,child,before,len(bodies[parent]),len(bodies[child])]
        elif k==11:
            i=p.i32(0);cur['deaths'].append([i,p.u16(4),teams[i],len(bodies[i]),bodies[i][0]])
            bodies.pop(i)
        elif k==12:
            sonars.append(dict(r=rnd,actor=actor,data=[p.u64(o) for o in range(0,p.dwords*8,8)],
                               pts=[lr.replay.point(p.pointer(z)) for z in range(p.pwords)]))
    finish();snaps[rnd]=snap()
    for s,name in enumerate(('us','them')):
        final=base['final'][name]
        assert [snaps[rnd][s][key] for key in ('n','q','longest','total')]==[final[key] for key in ('alive','queen_length','longest','total')]
    def ahead(st):
        if st[0]['n']==0 or st[1]['n']==0:return st[0]['n']>st[1]['n']
        return tuple(st[0][k] for k in ('q','longest','total'))>tuple(st[1][k] for k in ('q','longest','total'))
    permanent=max((r for r,st in snaps.items() if not ahead(st)),default=-1)+1
    result=dict(gid=gid,map=meta['mapName'],opponent=meta['team'+'AB'[1-own]+'Name'],side='AB'[own],bot=bot,
                end=rnd,how=ledger['how'],ahead=permanent,final=base['final'],q_eats=base['q_eats'],
                queen_deaths=[d for d in base['deaths'] if d['id'] in (queen,eq)],
                w=w,h=h,queen=queen,enemy_queen=eq,turns=turns,snaps=snaps,
                adjacency_risks=adjrisk,sonars=sonars,logs=logs,eats=base['eats'],
                collisions=base['collisions'],deaths=base['deaths'])
    (OUT/f'{gid}-trace.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
    (OUT/f'{gid}-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps({k:result[k] for k in ('gid','map','bot','end','how','ahead','final','queen_deaths')},ensure_ascii=False),flush=True)
    return result

if __name__=='__main__':
    rows=[]
    for job in JOBS:
        saved=OUT/f'{job[0]}-trace.json'
        if saved.is_file() and (OUT/f'{job[0]}-ledger.json').is_file():
            rows.append(json.loads(saved.read_text()))
        else:rows.append(scan(*job))
    (OUT/'summary.json').write_text(json.dumps([{k:v for k,v in row.items() if k not in ('turns','snaps','adjacency_risks','sonars','logs','collisions','deaths')} for row in rows],ensure_ascii=False,indent=2)+'\n')
