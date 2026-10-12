import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
from collections import deque
sys.path[:0] = ['data/codex/astra/approach', 'data/analysis/ladder/dossier/local']
from scan import Board, replay
from scoreboard import load_replay
replay.load = load_replay
OUT = Path(__file__).resolve().parent

def scan(path, meta, group):
    b = Board(path)
    own = int(meta['teamAId'] != 1119)
    bot = b.root.text(own + 1)
    if bot != '21033':
        return None
    queens = [min(i for i in b.bodies if b.teams[i] == s) for s in (own, 1-own)]
    q = queens[0]
    cur = None
    history = deque(maxlen=4)
    death = None
    entries = []
    splits = []
    long_deaths = []
    rounds = {}
    target = meta['id'] == 1479875
    def snap():
        return [[sum(b.teams[i] == s for i in b.bodies),
                 sum(len(bb) for i, bb in b.bodies.items() if b.teams[i] == s),
                 max((len(bb) for i, bb in b.bodies.items() if b.teams[i] == s), default=0),
                 len(b.bodies.get(queens[z], ()))] for z,s in enumerate((own,1-own))]
    def close():
        nonlocal cur
        if cur is not None:
            history.append(cur)
            cur = None
    for ev in b.root.pointer(3):
        k = ev.u16(0)
        if k not in (0,1,3,4,9,10,11): continue
        p = ev.pointer(0)
        if k in (0,1): close()
        if k == 0 and b.rnd >= 0: rounds[b.rnd] = snap()
        if k == 4 and cur is not None:
            a = p.pointer(0)
            cur['action'] = a.u16(0) if a else None
            cur['dirs'] = list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        if k == 10 and p.i32(0) == q:
            splits.append(dict(r=b.rnd, before=len(b.bodies[q]), after=len(p.pointer(0))))
        if k == 9 and p.i32(0) == q and cur is not None:
            h = replay.point(p.pointer(0))
            if h != b.bodies[q][0]:
                cur['moves'].append(h)
                n = len(cur['moves'])-1
                if n == 0 and cur['cages'] and h in map(tuple,cur['cages']):
                    entries.append(dict(r=b.rnd, src=cur['body'][0], dest=h,
                                        alternatives=cur['alternatives'], length=len(cur['body'])))
        if k == 11:
            i=p.i32(0)
            if i == q:
                death=dict(r=b.rnd,reason=p.u16(4),actor=b.actor,body=list(b.bodies[i]),
                           history=list(history),current=cur)
            if target and len(b.bodies[i]) >= 15:
                long_deaths.append(dict(r=b.rnd,id=i,own=b.teams[i]==own,length=len(b.bodies[i]),
                                        reason=p.u16(4),actor=b.actor,body=list(b.bodies[i])))
        b.update(k,p)
        if k==1 and b.actor==q:
            body=list(b.bodies[q]); h=body[0]
            occupied={c for i,bb in b.bodies.items() if i!=q for c in bb}
            alternatives=[];cages=[];options=[]
            for z,n in enumerate(b.adj[h]):
                legal=n is not None and n not in body and n not in occupied
                cage=False
                if legal:
                    post=[n]+(body if n in b.pearls else body[:-1])
                    cage=all(v is None or v in post for v in b.adj[n])
                    if cage:cages.append(n)
                    else:alternatives.append(dict(dir=z,dest=n))
                options.append(dict(dir=z,dest=n,legal=legal,cage=cage))
            cur=dict(r=b.rnd,body=body,moves=[],cages=cages,alternatives=alternatives,options=options)
            if target and 110<=b.rnd<=116:
                cur['bodies']={str(i):list(bb) for i,bb in b.bodies.items() if any(b.view(h,c) for c in bb)}
                cur['pearls']=[c for c in b.pearls if b.view(h,c)]
    close();rounds[b.rnd]=snap()
    final=rounds[b.rnd]
    for z,s in enumerate((own,1-own)):
        stats=b.root.pointer(4).pointer(s)
        assert final[z][:3]==[stats.i32(0),stats.i32(8),stats.i32(4)]
        assert final[z][1]==meta['scores'+'AB'[s]]
    return dict(game=meta['id'],group=group,map=meta['mapName'],bot=bot,queens=queens,
                win=meta['winner']=='ab'[own],final=final,death=death,cage_entries=entries,
                queen_splits=splits,long_deaths=long_deaths,
                snapshots={r:s for r,s in rounds.items() if r%25==0 or r==b.rnd},
                permanent_behind=1+max((r for r,s in rounds.items() if tuple(s[0][i] for i in (3,2,1))>=tuple(s[1][i] for i in (3,2,1))),default=-1))

def main():
    paths=[]
    for folder in sorted(Path('data/online/smoke').glob('one6-*-old')):
        paths.extend((p,folder.name) for p in sorted(folder.glob('game-*.json')))
    for p in sorted(Path('data/online/live-one1').glob('b*/game-*.json')):
        meta=json.loads(p.read_text())
        if (meta.get('startedAt') or '') >= '2026-10-08T16:30':paths.append((p,'live'))
    rows=[];seen=set()
    for p,group in paths:
        meta=json.loads(p.read_text())
        if meta['id'] in seen:continue
        seen.add(meta['id']);rp=p.with_name(f"M{meta['id']}.replay")
        if not rp.exists():continue
        cache=OUT/f"sample-{meta['id']}.json"
        row=json.loads(cache.read_text()) if cache.exists() else scan(rp,meta,group)
        if row is not None:
            cache.write_text(json.dumps(row))
            rows.append(row)
            print(row['game'],group,'death',row['death']['r'] if row['death'] else None,'cages',len(row['cage_entries']),flush=True)
    (OUT/'samples.json').write_text(json.dumps(rows))

if __name__=='__main__':main()
