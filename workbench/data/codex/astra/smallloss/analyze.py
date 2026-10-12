import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, hashlib, re
from collections import Counter, defaultdict, deque
from datetime import datetime
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay, canonical_edges, edge_id
from o1_scan import scan as ledger_scan
HERE=Path(__file__).resolve().parent
RUNS=Path.home()/'meow-redteam/solo/runs'
ARMS={'mDl5_vb':'one5','mDone8':'one8','mDone9':'one9','mDone10':'one10','mUw11_vb':'war8'}
MAPS=['sqheld_open_small_90012','ladder_stripes_1','sqheld_portals_small_90029','sqheld_blobs_small_90028']
STEP=((0,-1),(1,0),(0,1),(-1,0))

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def scan(arm,folder):
    path=folder/'game.replay'; ours=int(folder.name[-1]); root=replay.load(path).root()
    lines=root.text(0).splitlines(); W,H=map(int,lines[0].split()[1:3]); bodies={}; teams={}; raw=[]
    for line in lines:
        p=line.split()
        if p[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque((int(p[3+2*k]),int(p[4+2*k])) for k in range(int(p[2])));teams[i]=int(p[1])
        elif p[0]=='EDGE':raw.append(tuple(map(int,p[1:4])))
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]; initial=set(bodies)
    edges=canonical_edges(W,H,raw); portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2:portals[p].append(e)
    def dest(h,d):
        e=edge_id(W,H,*h,d);k,p=edges.get(e,(0,-1))
        if k==1:return None
        if k==2:
            partner=next(z for z in portals[p] if z!=e);row,x=divmod(partner,W+1);y=row//2
            return ((x-(d==3))%W,(y-(d==0))%H)
        return ((h[0]+STEP[d][0])%W,(h[1]+STEP[d][1])%H)
    def distance(a,b):
        x=abs(a[0]-b[0]);y=abs(a[1]-b[1]);return min(x,W-x)+min(y,H-y)
    def visible(a,b):
        x=abs(a[0]-b[0]);y=abs(a[1]-b[1]);return min(x,W-x)<=3 and min(y,H-y)<=3
    turns=[]; deaths=[]; eats=[]; splits=[]; snapshots={}; events=[]; logs=[]
    present={}; expected=deque(); born={}; parent={}; latest={}; cur=None; rnd=-1; actor=None; victim=None; used=0; seq=0
    def snap():
        return [[sum(teams[i]==s for i in bodies),sum(len(b) for i,b in bodies.items() if teams[i]==s),len(bodies.get(queens[s],()))] for s in (ours,1-ours)]
    def finish():
        nonlocal cur
        if cur is not None:
            cur['end']=list(bodies[actor][0]) if actor in bodies else None
            cur['L1']=len(bodies.get(actor,()))
            cur['paid']=cur['T0']+cur['eaten']-cur['lost']-sum(len(b) for i,b in bodies.items() if teams[i]==teams[actor])
            assert cur['paid']>=0
            turns.append(cur); latest[actor]=cur;cur=None
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k in (0,1):finish()
        if k==0:
            if rnd>=0:snapshots[rnd]=snap()
            rnd=p.i32(0);actor=None
        elif k==1:
            actor=p.i32(0);h=bodies[actor][0];L=len(bodies[actor]);s=teams[actor];used=0;victim=None;seq+=1
            occ={c:i for i,b in bodies.items() for c in b};opts=[]
            for d in range(4):
                c=dest(h,d);z=occ.get(c)
                opts.append(dict(d=d,c=c,edge=edges.get(edge_id(W,H,*h,d),(0,-1))[0],occupant=z,pearl=c in present))
            seen=[dict(id=i,L=len(b),parts=sum(visible(h,c) for c in b),head=list(b[0]),dist=distance(h,b[0]),s=int(teams[i]!=ours)) for i,b in bodies.items() if i!=actor and visible(h,b[0])]
            st=json.dumps([sorted((i,list(b)) for i,b in bodies.items()),sorted(present)],separators=(',',':'))
            cur=dict(r=rnd,id=actor,s=int(s!=ours),L=L,head=list(h),body=list(bodies[actor]),q=actor==queens[s],
                count=snap(),near=seen,opts=opts,free=sum(o['c'] is not None and o['occupant'] is None for o in opts),
                tail_portal=any(edges.get(edge_id(W,H,*bodies[actor][-1],d),(0,-1))[0]==2 for d in range(4)),
                state=hashlib.sha256(st.encode()).hexdigest(),action=None,steps=[],eaten=0,natural=0,drop=0,paid=0,lost=0,
                T0=sum(len(b) for i,b in bodies.items() if teams[i]==s),split=None,deaths=[],logs=[],eq=queens[1-s],
                age=rnd-born[actor] if actor in born else None,parent=parent.get(actor))
        elif k==4:
            a=p.pointer(0);ak=a.u16(0) if a else 2
            val=list(a.pointer(0)) if ak==0 and a.pointer(0) is not None else a.i32(4) if ak==1 else None
            cur['action']=[ak,val];events.append([rnd,actor,k,ak,val])
        elif k in (5,6):
            logs.append([rnd,actor,k,p.text(0)])
            if cur is not None:cur['logs'].append(p.text(0))
        elif k==3:
            c=replay.point(p.pointer(0));v=p.u32(0)
            if v:
                if expected:
                    ec,did=expected.popleft();assert c==ec;present[c]=did
                else:present[c]=None
            else:
                origin=present.pop(c);cur['eaten']+=1;cur['natural' if origin is None else 'drop']+=1
                eats.append(dict(r=rnd,id=actor,s=int(teams[actor]!=ours),c=c,origin=origin,L=len(bodies[actor])))
            events.append([rnd,actor,k,v,c])
        elif k==9:
            i=p.i32(0);h=replay.point(p.pointer(0));tail=replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=h:
                b.appendleft(h)
                if i==actor:used+=1;cur['steps'].append(h)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            events.append([rnd,actor,k,i,h,tail])
        elif k==10:
            a,c=p.i32(0),p.i32(4);before=len(bodies[a])
            for z,i in enumerate((a,c)):
                bodies[i]=deque(replay.point(q) for q in p.pointer(z));teams[i]=p.u16(8)
            parent[c]=a;born[c]=rnd
            sp=dict(r=rnd,id=a,child=c,s=int(teams[a]!=ours),L=before,keep=len(bodies[a]),childL=len(bodies[c]),head=bodies[a][0],childHead=bodies[c][0],tail_portal=cur['tail_portal'],q=a in queens)
            splits.append(sp);cur['split']=sp
            events.append([rnd,actor,k,a,c,list(bodies[a]),list(bodies[c])])
        elif k==11:
            i=p.i32(0);reason=p.u16(4);b=bodies[i];h=b[0];s=teams[i];target=None
            if reason==3:
                if i!=actor:victim=i;cause='rammed' if teams[actor]!=s else 'mate-head'
                else:target=victim;cause='rams' if victim is not None and teams[victim]!=s else 'mate-head'
            elif reason==2:
                ak,ds=cur['action'];c=dest(h,ds[used]) if i==actor and ak==0 and used<len(ds) else None
                owners=[z for z,bb in bodies.items() if z!=i and c in bb];target=owners[0] if len(owners)==1 else None
                cause='mate-body' if target is not None and teams[target]==s else 'foe-body'
            else:cause={0:'wall',1:'own-body',4:'no-action'}[reason]
            lt=cur if i==actor else latest.get(i)
            free=sum((c:=dest(h,d)) is not None and not any(c in bb for bb in bodies.values()) for d in range(4))
            rec=dict(r=rnd,id=i,s=int(s!=ours),L=len(b),q=i in queens,cause=cause,actor=actor,target=target,
                head=list(h),age=rnd-born[i] if i in born else None,parent=parent.get(i),free=free,
                last_r=lt['r'] if lt else None,last_action=lt['action'] if lt else None,last_head=lt['head'] if lt else None,
                last_L=lt['L'] if lt else None,last_split=lt['split'] if lt else None,last_logs=lt['logs'] if lt else [],
                last_near=lt['near'] if lt else [],last_free=lt['free'] if lt else None)
            if i==actor and target==queens[1-s]:rec['activity']='ram-enemy-queen'
            elif i not in initial and i not in latest and i!=actor:rec['activity']='child-before-first-turn'
            elif lt and lt['split']:rec['activity']='wait-split' if lt['q'] else 'after-split'
            elif any('SEVADE' in l for l in rec['last_logs']):rec['activity']='evade-logged'
            elif free==0:rec['activity']='boxed-at-death'
            else:rec['activity']='move/unresolved'
            deaths.append(rec);cur['deaths'].append([i,cause]);
            if teams[i]==teams[actor]:cur['lost']+=len(b)
            expected.extend((c,len(deaths)-1) for j,c in enumerate(b) if j%2==0)
            events.append([rnd,actor,k,i,reason]);bodies.pop(i)
    finish();snapshots[rnd]=snap();assert not expected
    result=json.loads((folder/'result.json').read_text());win=result['winner']
    for s,key in ((ours,'a' if ours==0 else 'b'),(1-ours,'b' if ours==0 else 'a')):
        assert sum(teams[i]==s for i in bodies)==result[key+'_dragons']
        assert sum(len(b) for i,b in bodies.items() if teams[i]==s)==result[key+'_length']
        assert len(bodies.get(queens[s],()))==result[key+'_queen']
    behind=None
    for r in reversed(sorted(snapshots)):
        sn=snapshots[r]
        if sn[0][0]<sn[1][0]:behind=r
        else:break
    return dict(arm=arm,version=ARMS[arm],folder=folder.name,path=str(path),sha256=sha(path),side=ours,W=W,H=H,
        winner=win,result='draw' if win is None else 'win' if win==ours else 'loss',last=rnd,how=result['how'],
        queens=queens,snapshots=snapshots,turns=turns,deaths=deaths,eats=eats,splits=splits,events=events,logs=logs,behind=behind)

def firstdiv(a,b):
    for ea,eb in zip(a['events'],b['events']):
        if ea!=eb:return dict(a=ea,b=eb)
    return None

def main():
    gs=[]
    for arm in ARMS:
        for m in MAPS:
            for s in (0,1):
                f=RUNS/arm/(m+'-seed1-side'+str(s))
                if not (f/'result.json').exists():continue
                g=scan(arm,f);gs.append(g)
                (HERE/(ARMS[arm]+'-'+f.name+'.json')).write_text(json.dumps(g,separators=(',',':')))
                print(ARMS[arm],f.name,g['result'],g['last'],'behind',g['behind'],flush=True)
    baseline={g['folder']:g for g in gs if g['version']=='one5'}
    summary=[]
    for g in gs:
        early=[t for t in g['turns'] if 0<=t['r']<=100 and t['s']==0]
        lastwins=[p for p in gs if p['folder']==g['folder'] and list(ARMS).index(p['arm'])<list(ARMS).index(g['arm']) and p['result']=='win']
        prev=lastwins[-1] if lastwins else None
        summary.append({k:g[k] for k in ('version','folder','result','last','behind')}|dict(
            firstdiv=firstdiv(g,baseline[g['folder']]),lastwin=prev['version'] if prev else None,
            lastwindiv=firstdiv(g,prev) if prev else None,early_turns=len(early),early_pearls=sum(t['eaten'] for t in early),
            early_natural=sum(t['natural'] for t in early),early_drop=sum(t['drop'] for t in early),
            early_splits=sum(t['split'] is not None for t in early),logs=len(g['logs']),
            deaths=dict(Counter(d['cause'] for d in g['deaths'] if d['s']==0))))
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2))
    (HERE/'timestamp.txt').write_text(datetime.now().astimezone().isoformat()+'\n')
if __name__=='__main__':main()
