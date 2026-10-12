import sys, json
from pathlib import Path
from collections import deque
sys.dont_write_bytecode = True
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'data/analysis/ladder/dossier/local'), str(ROOT/'data/analysis/ladder/losses/counts')]
import replay_format as rf
from scoreboard import load_replay
from count_replays import Geometry

def scan(gid):
    ledger = json.loads((OUT/f'{gid}-ledger.json').read_text())
    root = load_replay(ROOT/ledger['folder']/f'M{gid}.replay').root()
    w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,edges = {},{},[]
    for line in root.text(0).splitlines():
        p=line.split()
        if p[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque(int(p[4+2*k])*w+int(p[3+2*k]) for k in range(int(p[2])));teams[i]=int(p[1])
        elif p[0]=='EDGE': edges.append(tuple(map(int,p[1:4])))
    geo=Geometry(w,h,edges);own='AB'.index(ledger['ours']);q=ledger['queens']['us'];eq=ledger['queens']['them']
    tile=lambda p: rf.point(p)[1]*w+rf.point(p)[0]
    xy=lambda c: [c%w,c//w]
    pearls=set();turns=[];rnd=-1;turn=None;snaps={};close=[];death=False;mind=65535;nearest=None
    def board(c):
        cells={z: ('Q' if i==q and k==0 else 'q' if i==q else 'E' if i==eq and k==0 else 'A' if teams[i]==own and k==0 else 'a' if teams[i]==own else 'H' if k==0 else 'b') for i,b in bodies.items() for k,z in enumerate(b)}
        return [''.join(cells.get(((c//w+dy)%h)*w+(c%w+dx)%w,'*' if ((c//w+dy)%h)*w+(c%w+dx)%w in pearls else '.') for dx in range(-3,4)) for dy in range(-3,4)]
    def proximity(index):
        nonlocal mind,nearest
        if not death or eq not in bodies:return
        dist=geo.distances(bodies[eq][0])
        for i,b in bodies.items():
            if teams[i]!=own:continue
            if dist[b[0]]<mind:
                mind=dist[b[0]];nearest=dict(round=rnd,event=index,id=i,distance=mind,head=xy(b[0]),enemy_head=xy(bodies[eq][0]))
            if dist[b[0]]<=5 and not close:close.append(dict(round=rnd,event=index,id=i,distance=dist[b[0]],head=xy(b[0]),enemy_head=xy(bodies[eq][0])))
    for index,ev in enumerate(root.pointer(3)):
        kind=ev.u16(0);p=ev.pointer(0)
        if kind==0:
            if rnd>=0:snaps[rnd]={i:[len(b),*xy(b[0])] for i,b in bodies.items()}
            rnd=p.i32(0);turn=None
        elif kind==1:
            actor=p.i32(0);b=bodies[actor]
            turn=dict(round=rnd,event=index,id=actor,side=teams[actor],length=len(b),body=[xy(c) for c in b],eats=0,moves=[],action=None)
            if actor in (q,eq):
                turn['board']=board(b[0]);turn['near']={i:[len(bb),*xy(bb[0])] for i,bb in bodies.items() if geo.visible(b[0],bb[0])}
                turn['edges']=[(d,k,xy(z)) for d,(k,z) in enumerate(geo.moves[b[0]])]
                turn['visible_bodies']={i:[xy(z) for z in bb if geo.visible(b[0],z)] for i,bb in bodies.items() if any(geo.visible(b[0],z) for z in bb)}
                turn['pearls']=[xy(z) for z in pearls if geo.visible(b[0],z)]
            turns.append(turn);proximity(index)
        elif kind==4:
            a=p.pointer(0)
            turn['action']=[a.u16(0),list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else []]
        elif kind==3:
            c=tile(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c);turn['eats']+=1
        elif kind==9:
            i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd)
                if turn is not None:turn['moves'].append(xy(hd))
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            if turn is not None:turn['end_length']=len(b)
            proximity(index)
        elif kind==10:
            parent,child=p.i32(0),p.i32(4)
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
            turn['split']=[child,len(bodies[parent]),len(bodies[child])];proximity(index)
        elif kind==11:
            i=p.i32(0)
            if i==q:death=True
            turn.setdefault('deaths',[]).append([i,p.u16(4),len(bodies[i])]);bodies.pop(i);proximity(index)
    snaps[rnd]={i:[len(b),*xy(b[0])] for i,b in bodies.items()}
    result=dict(gid=gid,w=w,h=h,queen=q,enemy_queen=eq,own=own,teams=teams,turns=turns,snapshots=snaps,postqueen_first5=close,postqueen_nearest=nearest)
    (OUT/f'{gid}-detail.json').write_text(json.dumps(result))
    print(gid,'near',close,nearest)
    qt=[t for t in turns if t['id']==q]
    print('LAST Q',json.dumps(qt[-3:]))
    for d in ledger['deaths']:
        if d['id']==q:print('ATTACK',json.dumps([t for t in turns if t['round']==d['round'] and t['id']==d['actor']]))
    return result

if __name__=='__main__':
    for gid in (1515126,1509097,1509100):scan(gid)
