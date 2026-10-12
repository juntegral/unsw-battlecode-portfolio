import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
sys.path[:0]=[str(OUT.parent/'deathcell'),str(OUT.parent/'evade'),str(ROOT/'tools')]
from scan import initial
from analyze import Geo
from ladder_replay import replay

def one11(g):
    root=replay.load(ROOT/g['path']).root();geo=Geo(root.text(0));bs,teams=initial(root.text(0));bs={i:tuple(b) for i,b in bs.items()}
    meta=json.loads((ROOT/g['path']).with_name('game-'+str(g['gid'])+'.json').read_text());own=int(meta['teamAId']!=1119)
    queens={s:min(i for i in bs if teams[i]==s) for s in (0,1)}
    targets={d['history'][-1]['event']:d for d in g['deaths'] if d['startfree'] and d['history']}
    occ={c:i for i,b in bs.items() for c in b};out=[];turns=[0,0];deaths=[Counter(),Counter()];r=-1;ps=set()
    for ix,ev in enumerate(root.pointer(3)):
        k=ev.u16(0)
        if k not in (0,1,3,9,10,11):continue
        p=ev.pointer(0)
        if k==0:r=p.i32(0)
        elif k==1:
            actor=p.i32(0);turns[int(teams[actor]!=own)]+=1
            if ix in targets:
                d=targets[ix];t=d['history'][-1];q=queens[teams[actor]];qb=bs.get(q);qh=qb[0] if qb else None
                qvisible=qh is not None and geo.visible(qh,bs[actor][0]);qfree=geo.adj[qh]-occ.keys() if qvisible else set()
                alts=[]
                for o in t['options']:
                    nb=(tuple(o['n']),)+bs[actor] if o['eat'] else (tuple(o['n']),)+bs[actor][:-1]
                    preserves=not qvisible or actor==q or bool(qfree-set(nb))
                    if o['seen'] and not o['portal'] and o['exits'] and preserves:alts.append(o['d'])
                out.append(dict(gid=g['gid'],id=actor,r=r,side=d['side'],q=q,queen_visible=qvisible,queen_free=sorted(qfree),safe_alternatives=alts,
                                strict_candidate=qvisible and actor!=q and d['L']<=3 and not alts))
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0):ps.add(c)
            else:ps.remove(c)
        elif k==9:
            i=p.i32(0);b=bs[i];old=b;h=replay.point(p.pointer(0));tail=replay.point(p.pointer(1))
            if b[0]!=h:b=(h,)+b
            while len(b)>1 and b[-1]!=tail:b=b[:-1]
            assert b[-1]==tail
            for c in old:occ.pop(c,None)
            bs[i]=b
            for c in b:occ[c]=i
        elif k==10:
            pa,ch=p.i32(0),p.i32(4)
            for c in bs[pa]:occ.pop(c,None)
            for z,i in enumerate((pa,ch)):
                b=tuple(replay.point(c) for c in p.pointer(z));bs[i]=b;teams[i]=p.u16(8)
                for c in b:occ[c]=i
        elif k==11:
            i=p.i32(0);reason=p.u16(4);deaths[int(teams[i]!=own)][reason]+=1
            for c in bs[i]:occ.pop(c,None)
            del bs[i]
    assert turns==g['turns']
    for s in (0,1):
        for reason in (0,1):assert deaths[s][reason]==sum(d['side']==s and d['reason']==reason for d in g['deaths'])
    return dict(gid=g['gid'],turns=turns,deaths=[dict(c) for c in deaths],chosen=out)

def main():
    G=[json.loads(p.read_text()) for p in OUT.glob('game-*.json')];checks=[];details=[]
    for g in G:
        assert len(g['deaths'])==g['all_deaths'].get('0',0)+g['all_deaths'].get('1',0)
        assert all(d['startfree'] or d['closure'] is not None for d in g['deaths'])
        p=OUT.parent/'audit-move'/('game-'+str(g['gid'])+'.json')
        if p.exists():
            old=json.loads(p.read_text());ours=[d for d in g['deaths'] if d['side']==0]
            prior=[d for d in old['deaths'] if d['reason'] in (0,1)]
            assert [(d['r'],d['id'],d['reason'],d['L'],d['head']) for d in ours]==[(d['r'],d['id'],d['reason'],d['L'],d['head']) for d in prior]
            assert g['turns'][0]==old['counts']['turns']
            checks.append(dict(gid=g['gid'],deaths=len(ours),turns=g['turns'][0]))
        if g['version']=='one11':details.append(one11(g));print('one11 verified',g['gid'],flush=True)
    out=dict(games=len(G),audit_overlap=checks,one11=details)
    (OUT/'verification.json').write_text(json.dumps(out,indent=2));print('OK',len(G),len(checks),len(details),flush=True)

if __name__=='__main__':main()
