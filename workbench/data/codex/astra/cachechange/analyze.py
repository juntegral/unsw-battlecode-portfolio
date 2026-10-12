import sys
sys.dont_write_bytecode = True
import json, hashlib
from pathlib import Path
from collections import Counter, deque
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_scan import scan, replay

OUT = Path(__file__).parent
LABELS = ['one8-c1', 'one8-c2', 'one10-c1']

def trace(path, meta):
    root = replay.load(path).root()
    bodies, teams = {}, {}
    text = root.text(0)
    W,H = map(int,text.splitlines()[0].split()[1:3])
    for line in text.splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
            teams[i]=int(q[1])
    own=0 if meta['teamAId']==1119 else 1
    side=lambda i: int(teams[i]!=own)
    queens=[min(i for i in bodies if side(i)==s) for s in (0,1)]
    present=set(); rnd=-1; actor=None; turn=None; expected=0
    turns=[]; eats=[]; births=[]; splits=[]; counts=[Counter(),Counter()]; qheads=[set(),set()]
    def close():
        nonlocal turn
        if turn is not None:
            c=counts[turn['side']];c['turns']+=1
            c['early_turns']+=turn['r']<=100
            if turn['r']<=30: turns.append(turn)
            turn=None
    for ev in root.pointer(3):
        k=ev.u16(0)
        if k not in (0,1,3,4,9,10,11):continue
        p=ev.pointer(0)
        if k==0:close();rnd=p.i32(0);actor=None
        elif k==1:
            close();actor=p.i32(0);s=side(actor);h=bodies[actor][0]
            turn=dict(r=rnd,id=actor,side=s,L=len(bodies[actor]),head=h,body=list(bodies[actor]),moves=[],split=None,eats=[])
            if actor==queens[s]:qheads[s].add(h)
            if rnd<=30:
                near=lambda c: min(abs(c[0]-h[0]),W-abs(c[0]-h[0]))<=3 and min(abs(c[1]-h[1]),H-abs(c[1]-h[1]))<=3
                turn['pearls']=sorted(c for c in present if near(c))
                turn['near_foes']=[i for i,b in bodies.items() if side(i)!=s and any(near(c) for c in b)]
                turn['world']=hashlib.sha256(repr((sorted(present),sorted((i,list(b)) for i,b in bodies.items()))).encode()).hexdigest()
        elif k==4:
            a=p.pointer(0)
            turn['action']=[a.u16(0),list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []]
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
                if expected:expected-=1
                elif rnd<=100:births.append([rnd,c])
            else:
                present.remove(c);s=side(actor)
                if rnd<=100:eats.append([rnd,s,actor,c])
                turn['eats'].append(c)
        elif k==9:
            i=p.i32(0);h=replay.point(p.pointer(0));t=replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=h:
                b.appendleft(h)
                if i==actor:turn['moves'].append(h)
            while len(b)>1 and b[-1]!=t:b.pop()
        elif k==10:
            pa,ch=p.i32(0),p.i32(4)
            rec=[rnd,side(pa),pa,len(bodies[pa]),ch]
            for z,i in enumerate((pa,ch)):
                bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
            rec.extend([len(bodies[pa]),len(bodies[ch])]);splits.append(rec);turn['split']=rec[3:]
        elif k==11:
            i=p.i32(0);expected=(len(bodies[i])+1)//2;bodies.pop(i)
    close()
    return dict(bots=[root.text(1),root.text(2)],side=own,map_hash=hashlib.sha256(text.encode()).hexdigest(),turns=turns,
                counts=counts,eats=eats,births=births,splits=splits,queen_unique_heads=list(map(len,qheads)))

if __name__=='__main__':
    for label in LABELS:
        for mp in sorted(Path('data/online/smoke',label+'-old').glob('game-*.json')):
            m=json.loads(mp.read_text());gid=m['id'];op=OUT/f'{gid}.json'
            if op.exists():continue
            p=mp.parent/f'M{gid}.replay'
            g=scan(label,p,m)
            g['trace']=trace(p,m);g['meta']=m
            op.write_text(json.dumps(g,separators=(',',':')))
            print(label,gid,g['map'],g['result'],g['trace']['bots'],flush=True)
