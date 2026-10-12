"""Offline supplementary counts; model flags are not claimed as bot execution traces."""
import sys, json
from pathlib import Path
from collections import deque, defaultdict, Counter
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, '../battlecode/work')
from ladder_replay import replay, edge_id, canonical_edges
from card_42_check import make_key, unseal, parse
OUT = Path(__file__).resolve().parent
STEP = ((0,-1),(1,0),(0,1),(-1,0))

def scan(label, path, meta):
    root = replay.load(path).root()
    lines = [l.split() for l in root.text(0).splitlines()]
    W,H = map(int,lines[0][1:3]); N=W*H
    bodies,teams,raw,spawns = {},{},{},set()
    def ix(p): return p[1]*W+p[0]
    for q in lines:
        if not q: continue
        if q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1])
            bodies[i]=deque(int(q[4+2*k])*W+int(q[3+2*k]) for k in range(int(q[2])))
        elif q[0]=='EDGE': raw[int(q[1])] = (int(q[2]),int(q[3]))
        elif q[0]=='TILE' and int(q[4])>0: spawns.add(int(q[2])*W+int(q[1]))
    edges=canonical_edges(W,H,[(e,*v) for e,v in raw.items()])
    ports=defaultdict(list)
    for e,(k,pid) in edges.items():
        if k==2: ports[pid].append(e)
    own=0 if meta['teamAId']==1119 else 1
    side=lambda i: 0 if teams[i]==own else 1
    queens=[min(i for i in bodies if side(i)==s) for s in (0,1)]
    xy=[(c%W,c//W) for c in range(N)]
    near=[[(y+dy)%H*W+(x+dx)%W for dx,dy in STEP] for x,y in xy]
    eids=[[edge_id(W,H,x,y,d) for d in range(4)] for x,y in xy]
    adj=[[] for _ in range(N)]; rev=[[] for _ in range(N)]
    for c in range(N):
        for d,e in enumerate(eids[c]):
            k,pid=edges.get(e,(0,-1))
            if k==1: adj[c].append(-1); continue
            t=near[c][d]
            if k==2:
                ep=next(z for z in ports[pid] if z!=e)
                row,x=divmod(ep,W+1); y=row//2
                t=(y-(d==0))%H*W+(x-(d==3))%W
            adj[c].append(t); rev[t].append(c)
    views=[{(y+dy)%H*W+(x+dx)%W for dx in range(-3,4) for dy in range(-3,4)} for x,y in xy]
    def gap(a,b):
        x,y=xy[a]; u,v=xy[b]; dx=abs(x-u); dy=abs(y-v)
        return min(dx,W-dx)+min(dy,H-dy)
    def flood(starts,occ=frozenset(),limit=N,back=False):
        ds={c:0 for c in starts}; queue=deque(ds)
        graph=rev if back else adj
        while queue:
            c=queue.popleft(); d=ds[c]
            if d>=limit: continue
            for t in graph[c]:
                if t<0 or t in ds or t in occ: continue
                ds[t]=d+1; queue.append(t)
        return ds
    # A side-union of observations, explicitly not shared bot memory.
    side_seen=[set(),set()]; own_seen=defaultdict(set); known_edges=defaultdict(set)
    remembered=defaultdict(set); known_spawn_dist=[[N+1]*N for _ in (0,1)]
    born={}; birthparent={}; split_at={}; hist=defaultdict(lambda:deque(maxlen=12))
    pearls={}; expect=0; rnd=-1; actor=None; cur=None
    C=Counter(); grounds=[]; examples=defaultdict(list); d1rows=[]; blindrows=[]
    key=make_key(W,H,2 if own==0 else 1); streams={}; opened={}

    def add_spawns(s,new):
        ds=known_spawn_dist[s]; q=deque(new)
        for c in new: ds[c]=0
        while q:
            c=q.popleft()
            for t in rev[c]:
                if ds[t]>ds[c]+1: ds[t]=ds[c]+1; q.append(t)
    def observe(i):
        s=side(i); v=views[bodies[i][0]]
        new=(v-side_seen[s]) & spawns
        side_seen[s].update(v); add_spawns(s,new)
        own_seen[i].update(v)
        for c in v: known_edges[i].update(eids[c])
        remembered[i].difference_update(v); remembered[i].update(v & pearls.keys())

    def pocket(i,start):
        seen={start}; q=deque([start]); doors=[]
        while q:
            c=q.popleft()
            for d,e in enumerate(eids[c]):
                if e not in known_edges[i]: return 48
                k,pid=edges.get(e,(0,-1))
                if k!=0:
                    if k==2 and all(z in known_edges[i] for z in ports[pid]): doors.append((near[c][d],adj[c][d]))
                    continue
                t=near[c][d]
                if t not in seen:
                    if len(seen)>=48: return 48
                    seen.add(t); q.append(t)
        if any(a in seen and b not in seen for a,b in doors): return 48
        return len(seen)

    def survey_model(i,start,occ):
        # Own full body is a model assumption; remembered edges/pearls come only from this dragon's views.
        b=bodies[i]; seen=own_seen[i]; ek=known_edges[i]; rp=remembered[i]
        free={c:len(b)-k+1 for k,c in enumerate(b)}
        blocked=(occ-set(b)) & views[b[0]]
        ds={start:(1,int(start in rp))}; q=deque([start]); room=0; tail=False
        while q:
            c=q.popleft(); steps,eaten=ds[c]
            room+=1 if c in seen else .5
            tail |= c==b[-1]
            if tail and room>=3*len(b)+8: break
            for d,e in enumerate(eids[c]):
                k,pid=edges.get(e,(0,-1)) if e in ek else (0,-1)
                if k==1: continue
                if k==2:
                    if not all(z in ek for z in ports[pid]): continue
                    t=adj[c][d]
                else: t=near[c][d]
                if t in ds or t in blocked or steps+1-eaten<free.get(t,0): continue
                ds[t]=(steps+1,eaten+int(t in rp)); q.append(t)
        return room,tail

    def flags(i,t,occ):
        b=bodies[i]; L=len(b); h=b[0]; s=side(i); v=views[h]
        es=[z for z in bodies if side(z)!=s and bodies[z][0] in v]
        immediate=any(t in adj[bodies[z][0]] for z in es)
        pk=pocket(i,t); room,tail=survey_model(i,t,occ)
        return dict(pocket=pk, pocket_block=pk<48 and L+1>pk//2, body_visible=all(c in v for c in b),
                    room=room, tail=tail, dead_model=not tail and room<3*L+8,
                    closed_model=not tail and room<L+2, enemy_step=immediate,
                    ally_step=any(t in adj[bb[0]] for z,bb in bodies.items() if z!=i and side(z)==s and bb[0] in v),
                    foe_visible=bool(es), queen=i==queens[s], portal=all(edges.get(eids[h][d],(0,-1))[0]==2 for d in range(4) if adj[h][d]==t))

    def close():
        nonlocal cur
        if cur is None: return
        i,s,r=cur['i'],cur['s'],cur['r']
        if 101<=r<=300:
            w=1 if r<=200 else 2
            cl=cur['cls']; C[s,w,'turns']+=1; C[s,w,'class:'+cl]+=1
            C[s,w,'nat:'+cl]+=cur['nat']; C[s,w,'allpearls:'+cl]+=cur['ate']
            if cur['adj']:
                outcome='eat' if cur['ate'] else 'died' if cur['died'] else 'split' if cur['split'] else 'miss'
                C[s,w,'D1:'+outcome]+=1
                if s==0 and outcome=='miss':
                    reason='portal' if all(f['portal'] for f in cur['flags']) else 'pocket' if all(f['pocket_block'] for f in cur['flags']) else 'enemy_step' if all(f['enemy_step'] for f in cur['flags']) else 'room_model' if all(f['dead_model'] or f['closed_model'] for f in cur['flags']) else 'queen_risk_unknown' if cur['i']==queens[0] else 'hunter_ping' if cur['hunter'] else 'unresolved_score'
                    C[s,w,'D1reason:'+reason]+=1
                    cur['reason']=reason
                    d1rows.append({k:cur[k] for k in ('i','r','L','h','end','dirs','adj','flags','hunter','reason')})
            if cur['blindsolo']:
                # Same surviving/moving class as o1_mid; raw context is counted separately.
                C[s,w,'solo_raw']+=1
                if not (cur['ate'] or cur['split'] or cur['died']):
                    C[s,w,'solo']+=1
                    lb=str(cur['L']) if cur['L']<5 else '5+'
                    age=cur['age']; ab='starter' if age<0 else '0-5' if age<=5 else '6-25' if age<=25 else '26+'
                    dist=cur['spawn_dist']; db='0' if dist==0 else '1-3' if dist<=3 else '4-7' if dist<=7 else '8+' if dist<=N else 'none'
                    pd=cur['visible_pearl_dist']; pb='0-3' if pd<=3 else '4-7' if pd<=7 else '8+' if pd<=N else 'none'
                    for field,value in [('L',lb),('age',ab),('spawn',db),('visible_pearl',pb),('hunter',str(cur['hunter']))]: C[s,w,'solo '+field+':'+value]+=1
                    C[s,w,'solo retread']+=int(cur['end'] in cur['hist'])
                    C[s,w,'solo portal_recent']+=int(r-cur['portal_round']<=5)
                    d0=cur['spawn_dist']; d1=known_spawn_dist[s][cur['end']]
                    move='closer' if d1<d0 else 'farther' if d1>d0 else 'same'
                    C[s,w,'solo move:'+move]+=1
                    if s==0:
                        blindrows.append({k:cur[k] for k in ('i','r','L','age','h','end','dirs','spawn_dist','visible_pearl_dist','hunter','portal_round')})
                        blindrows[-1]['move']=move; blindrows[-1]['retread']=cur['end'] in cur['hist']
        if i in bodies: hist[i].append(cur['h'])
        cur=None

    portal_round=defaultdict(lambda:-1000)
    for ev in root.pointer(3):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            close()
            if 100<=rnd<=300 and rnd%10==0:
                ds=[flood([bb[0] for i,bb in bodies.items() if side(i)==s]) for s in (0,1)]
                row={'r':rnd}
                for name,tiles in [('spawn',spawns),('pearls',set(pearls)),('natural', {c for c,o in pearls.items() if o=='nat'})]:
                    cc=Counter()
                    for c in tiles:
                        a,b=ds[0].get(c,N+1),ds[1].get(c,N+1)
                        cc['none' if a==b==N+1 else 'tie' if a==b else 'ours' if a<b else 'theirs']+=1
                    row[name]=dict(cc)
                grounds.append(row)
            rnd=p.i32(0); actor=None
            if rnd>300: break
        elif k==1:
            close(); actor=p.i32(0); observe(actor)
            h=bodies[actor][0]; s=side(actor); v=views[h]; P=v & pearls.keys()
            occ=set(c for bb in bodies.values() for c in bb)
            ds=flood([h],occ-{h},7) if P else {}
            reach=[c for c in P if c in ds]; adjp=[c for c in reach if ds[c]==1]
            cl='blind' if not P else 'unreachable7' if not reach else 'adjacent' if adjp else 'reachable2+'
            mates=[z for z,bb in bodies.items() if z!=actor and side(z)==s and bb[0] in v]
            pd=N+1
            if not P and not mates and rnd>=101:
                targets={c for c in pearls if any(c in views[bb[0]] for z,bb in bodies.items() if side(z)==s)}
                if targets:
                    seen={h}; q=deque([(h,0)])
                    while q:
                        c,dep=q.popleft()
                        if c in targets: pd=dep; break
                        for t in adj[c]:
                            if t>=0 and t not in seen: seen.add(t); q.append((t,dep+1))
            cur=dict(i=actor,s=s,r=rnd,L=len(bodies[actor]),h=h,end=h,cls=cl,adj=adjp,
                     flags=[flags(actor,c,occ) for c in adjp] if s==0 and rnd>=101 else [],
                     ate=0,nat=0,split=False,died=False,dirs=[],hunter=False,
                     blindsolo=not P and not mates,age=rnd-split_at[actor] if actor in split_at else -1,
                     spawn_dist=known_spawn_dist[s][h],visible_pearl_dist=pd,hist=set(hist[actor]),portal_round=portal_round[actor])
        elif k==4 and cur:
            a=p.pointer(0)
            cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==3:
            c=ix(replay.point(p.pointer(0)))
            if p.u32(0):
                if not expect and c not in spawns:
                    spawns.add(c)
                    for s in (0,1):
                        if c in side_seen[s]: add_spawns(s,{c})
                pearls[c]='dead' if expect else 'nat'; expect=max(0,expect-1)
            else:
                origin=pearls.pop(c)
                if cur: cur['ate']+=1; cur['nat']+=int(origin=='nat')
        elif k==9:
            i=p.i32(0); hd=ix(replay.point(p.pointer(0))); tl=ix(replay.point(p.pointer(1))); b=bodies[i]
            old=b[0]
            if old!=hd:
                if any(adj[old][d]==hd and edges.get(eids[old][d],(0,-1))[0]==2 for d in range(4)): portal_round[i]=rnd
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl: b.pop()
            if cur and i==cur['i']: cur['end']=hd
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(ix(replay.point(c)) for c in p.pointer(z)); teams[i]=p.u16(8); split_at[i]=rnd
            born[child]=rnd; birthparent[child]=parent
            if cur and cur['i']==parent: cur['split']=True
        elif k==11:
            i=p.i32(0); expect=(len(bodies[i])+1)//2
            if cur and cur['i']==i: cur['died']=True
            del bodies[i]
        elif k==12 and cur and cur['s']==0 and (cur['blindsolo'] or cur['adj']) and 101<=rnd<=300:
            if p.i32(0)!=cur['i']: continue
            wire=p.u64(16)
            if wire not in opened: opened[wire]=unseal(key,wire,streams)
            plain=opened[wire]
            if plain is not None and parse(plain)[0]=='queen' and not ((plain>>23)&1): cur['hunter']=True
    close()
    return dict(label=label,gid=meta['id'],map=meta['mapName'],W=W,H=H,C=[[s,w,k,v] for (s,w,k),v in sorted(C.items())],ground=grounds,d1=d1rows,blind=blindrows)

if __name__=='__main__':
    for label in sys.argv[1:] or ['one5-w1','one5-c1','one3-w1']:
        dest=OUT/(label+'-scan-v2.jsonl')
        done={json.loads(l)['gid'] for l in dest.read_text().splitlines()} if dest.exists() else set()
        with dest.open('a') as out:
            for mp in sorted((Path('data/online/smoke')/(label+'-old')).glob('game-*.json')):
                meta=json.loads(mp.read_text())
                if meta['id'] in done: continue
                row=scan(label,mp.with_name('M%d.replay'%meta['id']),meta)
                out.write(json.dumps(row,separators=(',',':'))+'\n'); out.flush()
                print(label,meta['id'],flush=True)
