"""Read-only queen-hunt replay measurements; outputs confined to this directory."""
import sys
sys.dont_write_bytecode = True
import json, re, csv, hashlib
from pathlib import Path
from collections import deque, Counter, defaultdict
from functools import lru_cache
from datetime import datetime

ROOT = Path.cwd()
OUT = ROOT / 'data/codex/astra/queenhunt'
sys.path[:0] = [str(ROOT / 'data/analysis/ladder/dossier/online'),
               str(ROOT / 'data/analysis/ladder/dossier/local')]
import label_report as lr
from count_local import Geo
from replay_format import point
from scoreboard import load_replay

BUILDS = {'20850':'one1', '20880':'one2', '20910':'one3', '20941':'one4', '20980':'one5'}
LABELS = ['one1-w1','one1-d1','one2-w1','one3-w1','one3-d1','one4-w1','one4-d1','one5-w1','one5-d1']
RUNS = Path.home() / 'meow-redteam/solo/runs'
ARMS = ['mDo5_vh','m8o2_vh','m9f3_vh','mDqh_vb','mDl5_vb']

def scan(path, own, info):
    root = load_replay(path).root()
    lines = root.text(0).splitlines()
    w,h = map(int, lines[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    for line in lines:
        q=line.split()
        if not q: continue
        if q[0]=='DRAGON':
            i=len(bodies)
            bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
            teams[i]=int(int(q[1])!=own)
        elif q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    home=[bodies[q][0] for q in queens]
    geo=Geo(w,h,raw)
    rev=[[] for _ in geo.adj]
    for c,ns in enumerate(geo.adj):
        for n in ns: rev[n].append(c)
    @lru_cache(maxsize=256)
    def to(target):
        dist=[99999]*(w*h); dist[target]=0; queue=deque([target])
        while queue:
            c=queue.popleft()
            for n in rev[c]:
                if dist[n]==99999: dist[n]=dist[c]+1; queue.append(n)
        return dist
    def man(a,b):
        dx,dy=abs(a%w-b%w),abs(a//w-b//w)
        return min(dx,w-dx)+min(dy,h-dy)
    tile=lambda p: point(p)[1]*w+point(p)[0]
    rnd=-1; actor=None; turn=None
    turns=defaultdict(list); deaths=[]; snaps={}; samples=[]
    queen_context={}; pearls=[0,0]; total_turns=[0,0]
    def snapshot():
        return [dict(alive=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),
                     longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),
                     queen_length=len(bodies.get(queens[s],())),pearls=pearls[s]) for s in (0,1)]
    def sample():
        q=queens[1]
        row=dict(round=rnd,alive=q in bodies,length=0,distance=None,nearest=None,mates5=None,home_distance=None,location='dead')
        if q in bodies:
            head=bodies[q][0]; ds=to(head)
            short=sorted((ds[b[0]],i) for i,b in bodies.items() if teams[i]==0 and 2<=len(b)<=4)
            mates=sum(i!=q and teams[i]==1 and man(head,b[0])<=5 for i,b in bodies.items())
            front=min((ds[b[0]] for i,b in bodies.items() if teams[i]==0),default=99999)
            hd=man(head,home[1]); loc='front' if front<=5 else 'home' if hd<=5 else 'swarm' if mates>=2 else 'isolated'
            row.update(length=len(bodies[q]),head=[head%w,head//w],distance=short[0][0] if short and short[0][0]<99999 else None,
                       nearest=short[0][1] if short and short[0][0]<99999 else None,mates5=mates,home_distance=hd,location=loc,
                       front_distance=front if front<99999 else None)
        samples.append(row)
    def close():
        nonlocal turn
        if turn is None:return
        i=turn['id']
        turn['end']=bodies[i][0] if i in bodies else None
        if turn['target'] is not None:
            ds=to(turn['target'])
            turn['d1']=ds[turn['end']] if turn['end'] is not None else (0 if turn['queen_hit'] else None)
        turns[i].append(turn)
        turn=None
    for index,ev in enumerate(root.pointer(3)):
        k=ev.u16(0)
        if k not in (0,1,3,9,10,11):continue
        p=ev.pointer(0)
        if k==0:
            close()
            if rnd>=0:
                if rnd%10==0:sample()
                if rnd in (100,300):snaps[str(rnd)]=snapshot()
            rnd=p.i32(0);actor=None
        elif k==1:
            close();actor=p.i32(0);s=teams[actor]; eq=queens[1-s]
            target=bodies[eq][0] if eq in bodies else None
            turn=dict(id=actor,side=s,round=rnd,length=len(bodies[actor]),start=bodies[actor][0],target=target,
                      d0=to(target)[bodies[actor][0]] if target is not None else None,d1=None,steps=0,eats=0,queen_hit=False,event=index)
            total_turns[s]+=1
            if actor==queens[s]:
                queen_context[s]={i:(b[0],len(b)) for i,b in bodies.items()}
        elif k==3:
            if not p.u32(0):
                pearls[teams[actor]]+=1
                if turn:turn['eats']+=1
        elif k==9:
            i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
            if hd!=b[0]:
                b.appendleft(hd)
                if turn and i==actor:turn['steps']+=1
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=int(p.u16(8)!=own)
        elif k==11:
            i=p.i32(0);s=teams[i];reason=p.u16(4)
            d=dict(id=i,side=s,round=rnd,reason=reason,actor=actor,length=len(bodies[i]),queen=i==queens[s],event=index,
                   rammed=reason==3 and actor!=i and actor is not None and teams[actor]!=s)
            if d['queen']:
                head=bodies[i][0]
                d['mates5']=sum(z!=i and teams[z]==s and man(head,bb[0])<=5 for z,bb in bodies.items())
                if d['rammed']:
                    d['rammer_length']=turn['length'];d['rammer_start_distance']=turn['d0'];turn['queen_hit']=True
            deaths.append(d);bodies.pop(i)
    close()
    if rnd%10==0:sample()
    final=snapshot()
    for checkpoint in (100,300):
        if str(checkpoint) not in snaps:snaps[str(checkpoint)]=None
    hunters=[[],[]]
    for i,ts in turns.items():
        qualifying=[]
        for n in range(2,len(ts)):
            win=ts[n-2:n+1]
            if all(t['d0'] is not None and t['d1'] is not None and t['d0']<99999 and t['d1']<t['d0'] and not t['queen_hit'] for t in win) and win[-1]['round']-win[0]['round']<=4 and win[0]['d0']>=6 and win[-1]['d1']<=5:
                qualifying.append(n)
        if qualifying:
            ix=sorted({j for n in qualifying for j in range(n-2,n+1)})
            d=next((d for d in deaths if d['id']==i),None)
            hunters[teams[i]].append(dict(id=i,queen=i==queens[teams[i]],windows=[[ts[n-2]['round'],ts[n]['round']] for n in qualifying],
                turns=[ts[j] for j in ix],death=d,eats=sum(ts[j]['eats'] for j in ix),turn_count=len(ix)))
    qdeaths=[next((d for d in deaths if d['id']==q),None) for q in queens]
    for s,d in enumerate(qdeaths):
        if d and d['rammed']:
            ts=turns[d['actor']];hist=[t for t in ts if t['round']<=d['round']][-12:]
            h=next((h for h in hunters[1-s] if h['id']==d['actor']),None)
            prior=[x for x in (h['windows'] if h else []) if x[1]<=d['round'] and d['round']-x[1]<=6]
            d['classification']='approach' if prior else 'no_far_approach' if len(hist)>=3 else 'insufficient_history'
            d['history']=hist
    res=root.pointer(4);winner=res.u16(6) if res.u16(4)==1 else None
    how='elimination' if min(x['alive'] for x in final)==0 else next((k for k in ['queen_length','longest','total'] if final[0][k]!=final[1][k]),'draw')
    row=dict(info,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bot=[root.text(1),root.text(2)][own],
             opponent_bot=[root.text(1),root.text(2)][1-own],queens=queens,width=w,height=h,last=rnd,final=final,snaps=snaps,samples=samples,
             qdeaths=qdeaths,hunters=hunters,turns=total_turns,result='draw' if winner is None else 'win' if winner==own else 'loss',how=how)
    if info.get('winner') in ('a','b'):
        assert winner==('a','b').index(info['winner'])
    return row

def main():
    notes=[]; jobs=[];seen=set()
    for label in LABELS:
        inv=lr.inventory(label,'old');notes+=inv['notes']
        for path,meta in inv['jobs']:
            if meta['id'] in seen:continue
            seen.add(meta['id']);own=int(meta['teamAId']!=1119)
            jobs.append((path,own,dict(kind='online',group=label,game=meta['id'],map=meta['mapName'],winner=meta['winner'])))
    ranked=lr.directory_inventory('ranked','data/online/live-one1/b*')
    for path,meta in ranked['jobs']:
        if meta['id'] in seen:continue
        own=int(meta['teamAId']!=1119)
        rt=load_replay(path).root();bot=[rt.text(1),rt.text(2)][own]
        if bot not in BUILDS:continue
        seen.add(meta['id'])
        jobs.append((path,own,dict(kind='online',group=BUILDS[bot]+'-ranked',game=meta['id'],map=meta['mapName'],winner=meta['winner'])))
    for arm in ARMS:
        paths=sorted((RUNS/arm).glob('*/game.replay'))
        if not paths:notes.append('No replay folder: '+arm)
        for path in paths:
            if not path.with_name('result.txt').exists():continue
            match=re.fullmatch(r'(.+)-seed(\d+)-side(\d)',path.parent.name)
            jobs.append((path,int(match[3]),dict(kind='local',group=arm,game=path.parent.name,map=match[1],seed=int(match[2]))))
    cachepath=OUT/'games.jsonl'
    old={g['path']:g for g in map(json.loads,cachepath.read_text().splitlines())} if cachepath.exists() and '--refresh' not in sys.argv else {}
    rows=[];errors=[]
    with cachepath.open('w') as out:
        for n,(path,own,info) in enumerate(jobs):
            try:
                g=old.get(str(path)) or scan(path,own,info)
                rows.append(g);out.write(json.dumps(g,separators=(',',':'))+'\n');out.flush()
            except Exception as e:
                import traceback
                errors.append([str(path),repr(e)]);traceback.print_exc()
            if (n+1)%10==0:print(n+1,'/',len(jobs),flush=True)
    (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),games=len(rows),errors=errors,notes=notes),indent=2))
    with (OUT/'online-every10.csv').open('w') as f:
        keys=['group','game','map','round','alive','length','distance','nearest','mates5','home_distance','location','front_distance','head']
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader()
        for g in rows:
            if g['kind']=='online':
                for s in g['samples']:wr.writerow(dict(group=g['group'],game=g['game'],map=g['map'],**s))
    print('DONE',len(rows),'errors',len(errors),flush=True)

if __name__=='__main__':main()
