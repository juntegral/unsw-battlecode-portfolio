import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo

OUT = Path(__file__).resolve().parent
SRC = Path('data/online/live-one1/b1491740')

def scan(gid):
    meta = json.loads((SRC / f'game-{gid}.json').read_text())
    ledger = lr.scan(SRC / f'M{gid}.replay', meta, 'b1491740', set())
    ledger.pop('intervals')
    assert ledger['bots']['A'] == '21200' and meta['teamAId'] == 1119
    (OUT / f'{gid}-ledger.json').write_text(json.dumps(ledger))
    root = lr.replay.load(SRC / f'M{gid}.replay').root()
    w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
    b,teams,edges = {},{},[]
    for line in root.text(0).splitlines():
        a=line.split()
        if a[0]=='DRAGON':
            i=len(b); teams[i]=int(a[1]); b[i]=deque(int(a[4+2*k])*w+int(a[3+2*k]) for k in range(int(a[2])))
        elif a[0]=='EDGE': edges.append(tuple(map(int,a[1:4])))
    g=Geo(w,h,edges); q=[min(i for i in b if teams[i]==s) for s in (0,1)]
    pearls={}; turns=[]; snaps={}; qt=[]; rnd=-1; actor=None; cur=None; near=[]; qdead=False
    tile=lambda p: p.i32(4)*w+p.i32(0)
    xy=lambda c:[c%w,c//w]
    def snap():
        return [sorted([[i,len(bb),xy(bb[0])] for i,bb in b.items() if teams[i]==s],key=lambda z:-z[1]) for s in (0,1)]
    def field(src):
        d={src:0}; queue=deque([src])
        while queue:
            c=queue.popleft()
            for n in g.adj[c]:
                if n not in d: d[n]=d[c]+1;queue.append(n)
        return d
    def close():
        if cur is not None:
            cur['end']=list(b.get(actor,[])); turns.append(cur.copy())
    def proximity(event):
        if not qdead or q[1] not in b: return
        heads=[(i,bb[0]) for i,bb in b.items() if teams[i]==0]
        if not heads:return
        # Directed topology, including portals; bodies ignored.
        vals=[(field(c).get(b[q[1]][0],99999),i,c) for i,c in heads]
        dist,i,c=min(vals)
        if not near or dist<near[-1]['best']:
            near.append(dict(round=rnd,event=event,best=dist,id=i,head=xy(c),enemy=xy(b[q[1]][0])))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            close();cur=None;snaps[rnd]=snap();rnd=p.i32(0);actor=None
        elif k==1:
            close();actor=p.i32(0)
            cur=dict(round=rnd,event=idx,id=actor,side=teams[actor],start=list(b[actor]),action=None,dirs=[],eat=[],updates=[])
            if actor==q[0]:
                view=g.window(b[actor][0]);cur['board']={i:list(bb) for i,bb in b.items() if any(c in view for c in bb)}
                cur['pearls']=list(pearls);qt.append(cur)
            proximity(idx)
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0):pearls[c]='spawn' if actor is None else 'drop'
            else: cur['eat'].append([xy(c),pearls.pop(c)])
        elif k==9:
            i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));bb=b[i]
            if bb[0]!=hd:bb.appendleft(hd)
            while len(bb)>1 and bb[-1]!=tail:bb.pop()
            assert bb[-1]==tail
            if cur is not None: cur['updates'].append([i,xy(hd),len(bb)])
        elif k==10:
            for n,i in enumerate([p.i32(0),p.i32(4)]):
                b[i]=deque(tile(c) for c in p.pointer(n));teams[i]=p.u16(8)
            cur['split']=[p.i32(4),len(b[p.i32(0)]),len(b[p.i32(4)])]
        elif k==11:
            i=p.i32(0);cur.setdefault('deaths',[]).append([i,p.u16(4),list(b[i])]);b.pop(i)
            if i==q[0]:qdead=True
            proximity(idx)
        elif lr.replay.EVENT_NAMES[k]=='dragonAction':
            a=p.pointer(0);cur['action']=a.u16(0)
            cur['dirs']=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []
    close();snaps[rnd]=snap()
    for side, key in enumerate(('us', 'them')):
        expected = ledger['final'][key]
        assert len(snaps[rnd][side]) == expected['alive']
        assert sum(row[1] for row in snaps[rnd][side]) == expected['total']
        assert max((row[1] for row in snaps[rnd][side]), default=0) == expected['longest']
    out=dict(gid=gid,w=w,h=h,queens=q,teams=teams,turns=turns,snaps=snaps,near=near,queen_turns=qt[-3:])
    (OUT/f'{gid}-turns.json').write_text(json.dumps(out))
    lines=[]
    for t in qt[-3:]:
        c=t['start'][0]; x,y=c%w,c//w;view=g.window(c);occ={cc:(i,n) for i,bb in t['board'].items() for n,cc in enumerate(bb)}
        lines.append(f"r{t['round']} Q{q[0]} ({x},{y}) L{len(t['start'])}, dirs={t['dirs']}, updates={t['updates']}")
        for dy in range(-3,4):
            top='';row=''
            for dx in range(-3,4):
                cc=((y+dy)%h)*w+(x+dx)%w
                def edge(d):return '#' if g.moves[cc][d][0]==1 else 'P' if g.moves[cc][d][0]==2 else ' '
                top+='+'+edge(0)
                if cc in occ:
                    i,n=occ[cc];ch=('Q' if n==0 else 'q') if i==q[0] else ('A' if n==0 else 'a') if teams[i]==0 else ('E' if n==0 else 'e')
                else:ch='*' if cc in t['pearls'] else '.'
                row+=edge(3)+ch
            lines.extend([top+'+',row+edge(1)])
        lines.append('+'+'+'.join('#' if g.moves[((y+3)%h)*w+(x+dx)%w][2][0]==1 else 'P' if g.moves[((y+3)%h)*w+(x+dx)%w][2][0]==2 else ' ' for dx in range(-3,4))+'+')
        lines.append('visible bodies '+str({i:[xy(cc) for cc in bb if cc in view] for i,bb in t['board'].items()}))
    (OUT/f'{gid}-boards.txt').write_text('\n'.join(lines)+'\n')
    print(gid,'near',near,'last Q',[(t['round'],t['dirs'],t.get('deaths')) for t in qt[-3:]])

if __name__=='__main__':
    for gid in (1491741,1491742,1491743):scan(gid)
