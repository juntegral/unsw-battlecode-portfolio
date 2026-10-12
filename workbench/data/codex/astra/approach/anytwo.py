"""Literal D2 census, including turns which also have an adjacent pearl.
scan.py's nearest-D2 census is the uncontaminated diagnostic subset.
"""
import sys,json
sys.dont_write_bytecode=True
from scan import Board,OUT,inventory
from collections import Counter

def scan(job):
    B=Board(job['path']); own=job['own']; queen=min(i for i in B.bodies if B.teams[i]==own)
    rows=[];cur=None
    def close():
        nonlocal cur
        if cur is None:return
        if cur['split']:cl='split'
        elif cur['first'] is None:cl='died' if cur['died'] else 'no_step'
        else:
            ds=B.flood(cur['first'],3,cur['occ']-{cur['h']})
            distance=min(ds.get(t,99) for t in cur['targets'])
            cl='toward' if distance<2 else 'sideways' if distance==2 else 'away'
        rows.append(dict(**{k:v for k,v in cur.items() if k!='occ'},cls=cl))
        cur=None
    for ev in B.root.pointer(3):
        k=ev.u16(0)
        if k not in (0,1,3,9,10,11):continue
        p=ev.pointer(0)
        if k in (0,1):close()
        if cur is not None:
            if k==9 and p.i32(0)==cur['i']:
                h=replay_point(p.pointer(0))
                if cur['first'] is None and h!=cur['h']:cur['first']=h
            elif k==10 and p.i32(0)==cur['i']:cur['split']=True
            elif k==11 and p.i32(0)==cur['i']:cur['died']=True
            elif k==3 and not p.u32(0):cur['ate']=True
        B.update(k,p)
        if k!=1 or B.teams[B.actor]!=own or B.actor==queen:continue
        h=B.bodies[B.actor][0];occ=set(c for b in B.bodies.values() for c in b)
        ds=B.flood(h,2,occ)
        targets=sorted(c for c in B.pearls if ds.get(c)==2 and B.view(h,c))
        if not targets:continue
        near=B.flood(h,4)
        if any(B.teams[z]!=own and b[0] in near for z,b in B.bodies.items()):continue
        cur=dict(i=B.actor,r=B.rnd,L=len(B.bodies[B.actor]),h=h,occ=occ,targets=targets,
                 adjacent=any(ds.get(c)==1 and B.view(h,c) for c in B.pearls),
                 mate=any(z!=B.actor and B.teams[z]==own and B.view(h,b[0]) for z,b in B.bodies.items()),
                 first=None,split=False,died=False,ate=False)
    close()
    return dict(meta=dict(**job,cells=B.W*B.H,bot=B.root.text(1+own)),rows=rows)

def replay_point(p):
    return p.i32(0),p.i32(4)

def main():
    for job in inventory():
        f=OUT/('anytwo-'+job['label']+'-'+job['game']+'.json')
        if f.exists():continue
        data=scan(job);f.write_text(json.dumps(data,separators=(',',':')))
        print(job['label'],job['game'],len(data['rows']),flush=True)

if __name__=='__main__':main()
