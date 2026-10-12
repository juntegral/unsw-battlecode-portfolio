import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter
import importlib.util
spec=importlib.util.spec_from_file_location('win1_driver',Path(__file__).with_name('analyze.py'))
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

def main():
    pooled=Counter(); rows=[]; portal_gaps=[]; voluntary=[]; release=[]; stops=[]; bypass=[]
    for gid in (1496000,1496002,1496003,1496004):
        x=json.loads((a.OUT/f'g{gid}.json').read_text())
        d=x['detail'];q,eq=d['queens'];turns=d['turns'];index={(t['r'],t['id']):t for t in turns}
        pooled.update(x['census']['counts'])
        root=a.lr.replay.load(a.ROOT/f'data/online/live-one1/b1496000/M{gid}.replay').root()
        w,h=map(int,root.text(0).splitlines()[0].split()[1:3])
        def visible(c,head):
            dx,dy=abs(c[0]-head[0]),abs(c[1]-head[1])
            return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
        previous=[]
        for t in turns:
            if t['id']==q:
                if t['dirs']:
                    o=t['options'][t['dirs'][0]]
                    if o['edge'][0]==2 and not any(visible(o['n'],head) for head in previous+[t['body'][0]]):
                        legal=[z for z in t['options'] if z['edge'][0]==0 and z['n'] is not None and z['owner'] is None]
                        if legal:portal_gaps.append(dict(gid=gid,r=t['r'],destination=o['n'],alternatives=legal,L=t['L']))
                previous.append(t['body'][0])
                if t['r']>400 and t['L']<6:
                    pooled['late_short_queen_turns']+=1
                    pooled['late_short_queen_splits']+=bool(t['split'])
            if not t['ours']:continue
            pooled['stationary_alive']+=bool(t['endbody'] and t['body'][0]==t['endbody'][0] and not t['split'])
            adjacent=[o for o in t['options'] if o['edge'][0]==0 and o['n'] is not None and o['owner'] is None and o['pearl']]
            if adjacent and t.get('action')==0 and t['path'] and t['path'][0] not in [o['n'] for o in adjacent]:
                bypass.append(dict(gid=gid,r=t['r'],id=t['id'],alternatives=adjacent,dirs=t['dirs']))
        for s in d['splits']:
            if s['parent']==q and len(s['body'])==4 and s['units']<6:
                release.append(dict(gid=gid,r=s['r'],units=s['units']))
            if s['ours'] and s['parent']!=q and len(s['body'])==4 and s['r']<=100 and s['tail_portal']:
                t=index[s['r'],s['parent']]
                if len(t['free'])>=2 and not t['enemies']:
                    voluntary.append(dict(gid=gid,**s))
        for z in x['ledger']['deaths']:
            if z['side']=='us' and z['reason']==4 and index[z['round'],z['id']]['free']:
                stops.append(dict(gid=gid,r=z['round'],id=z['id'],L=z['length']))
        start=[0,0]
        for line in root.text(0).splitlines():
            parts=line.split()
            if parts and parts[0]=='DRAGON':start[int(parts[1])!=1]+=int(parts[2])
        residual=[]
        for side in (0,1):
            residual.append(start[side]+sum(e[1]==side for e in x['base']['eats'])-
                            sum(z[2] for z in x['base']['deaths'] if z[1]==side)-
                            sum(p[3] for p in x['base']['paids'] if p[1]==side)-d['frames'][str(x['base']['last'])][side]['total'])
        assert residual==[0,0]
        rows.append(dict(gid=gid,residual=residual,permanent=d['permanent'],
                         final=d['frames'][str(x['base']['last'])],
                         natural=x['ledger']['eats'],bot=root.text(2)))
    out=dict(rows=rows,counts=dict(pooled),unseen_portal_with_alternative=portal_gaps,
             voluntary_portal_splits=voluntary,queen_release_splits=release,
             stops_with_exits=stops,adjacent_pearl_passes=bypass)
    (a.OUT/'facts.json').write_text(json.dumps(out,indent=2)+'\n')
    print('portal gap',portal_gaps)
    print('voluntary portal splits',[(s['gid'],s['r'],s['parent']) for s in voluntary])
    print('release',release,'stops',len(stops),'pearl passes',len(bypass),'standing',pooled['stationary_alive'])

if __name__=='__main__':main()
