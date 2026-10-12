import sys, json, ast, types
from pathlib import Path
from collections import deque
sys.dont_write_bytecode = True
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work']
from ladder_replay import replay
source=Path('data/analysis/ladder/dossier/work/tr_scan.py')
tree=ast.parse(source.read_text())
tree.body=[n for n in tree.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='main')]
module=types.ModuleType('tr_scan_readonly')
exec(compile(tree,str(source),'exec'),module.__dict__)
Geo=module.Geo

OUT = Path(__file__).resolve().parent
root = replay.load('data/online/live-one1/b1488287/M1488290.replay').root()
text = root.text(0)
W,H = map(int,text.splitlines()[0].split()[1:3])
bodies,teams,raw = {},{},[]
for line in text.splitlines():
    q=line.split()
    if q and q[0]=='DRAGON':
        i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
        teams[i]='AB'[int(q[1])]
    elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
geo=Geo(W,H,raw)
tile=lambda xy: xy[1]*W+xy[0]
pearls=set();rnd=0;actor=None;turn=None;turns=[];near=[];dead=False;closest=None;positions={};attacker_seen=[]
def snap():
    return dict(bodies={i:list(b) for i,b in bodies.items()},pearls=sorted(pearls))
def finish():
    if turn is not None:
        turn['end']=list(bodies.get(actor,()))
        turns.append(turn)
for ix,ev in enumerate(root.pointer(3)):
    k=replay.EVENT_NAMES[ev.u16(0)];p=ev.pointer(0)
    if k=='roundStart':rnd=p.i32(0)
    elif k=='turnStart':
        finish();actor=p.i32(0)
        turn=dict(r=rnd,id=actor,event=ix,start=list(bodies[actor]),events=[])
        if actor==0 and 82 in bodies:
            view=geo.window(tile(bodies[0][0]))
            if tile(bodies[82][0]) in view:attacker_seen.append(rnd)
        if (actor==0 and rnd>=170) or (actor==82 and 170<=rnd<=175):turn.update(snap())
        if dead and 1 in bodies and teams[actor]=='A':
            pos=bodies[1][0]; positions[rnd]=pos
            ds=geo.ball(tile(bodies[actor][0]));d=ds.get(tile(pos))
            if d is not None and d<=5:
                row=dict(r=rnd,id=actor,length=len(bodies[actor]),head=bodies[actor][0],queen=pos,distance=d,event=ix)
                near.append(row)
                if closest is None or d<closest['distance']:closest=row
    elif k=='dragonAction':
        a=p.pointer(0);turn['action_kind']=a.u16(0) if a else None
        turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
    elif k=='tileChange':
        c=replay.point(p.pointer(0));v=p.u32(0)
        if v:pearls.add(c)
        else:
            pearls.remove(c)
            if turn is not None:turn['events'].append(dict(k='eat',xy=c))
    elif k=='dragonUpdate':
        i=p.i32(0);h=replay.point(p.pointer(0));tail=replay.point(p.pointer(1));b=bodies[i]
        if b[0]!=h:b.appendleft(h)
        while len(b)>1 and b[-1]!=tail:b.pop()
        assert b[-1]==tail
        if turn is not None:turn['events'].append(dict(k=k,id=i,head=h,length=len(b)))
    elif k=='dragonSplit':
        for z,i in enumerate((p.i32(0),p.i32(4))):
            bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]='AB'[p.u16(8)]
        turn['events'].append(dict(k=k,parent=p.i32(0),child=p.i32(4)))
    elif k=='dragonDeath':
        i=p.i32(0);turn['events'].append(dict(k=k,id=i,reason=p.u16(4),body=list(bodies[i])))
        bodies.pop(i)
        if i==0:dead=True
finish()
last=[t for t in turns if t['id']==0][-3:]
def board(t):
    cx,cy=t['start'][0];occupants={}
    for i,bb in t['bodies'].items():
        for n,c in enumerate(bb):occupants[tuple(c)]=('Q' if i==0 else 'X' if i==82 else 'A' if teams[i]=='A' else 'B') if n==0 else ('q' if i==0 else 'x' if i==82 else 'a' if teams[i]=='A' else 'b')
    return [''.join(occupants.get(((cx+dx)%W,(cy+dy)%H),'*' if ((cx+dx)%W,(cy+dy)%H) in map(tuple,t['pearls']) else '.') for dx in range(-3,4)) for dy in range(-3,4)]
for t in last:t['board']=board(t)
result=dict(W=W,H=H,bots=[root.text(1),root.text(2)],last=last,attacker_seen_by_queen=attacker_seen,attacker=[t for t in turns if t['id']==82 and 170<=t['r']<=175],near=near,closest=closest,teams=teams,queen_positions=positions,turns=[{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in turns])
(OUT/'evidence.json').write_text(json.dumps(result))
for t in last:
    print('QUEEN',t['r'],t['start'],t.get('dirs'),t['end']);print('\n'.join(t['board']))
    print('ATTACKER',t['bodies'].get(82));print('events',t['events'])
for t in result['attacker']:print('ATTACK', {k:v for k,v in t.items() if k not in ('bodies','pearls')})
print('NEAR',len(near),'unique dragons',len(set(t['id'] for t in near)),'first',near[:3],'closest',closest)
