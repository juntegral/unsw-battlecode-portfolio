"""Check proposed card witnesses against sprint fueled by existing pearls too."""
import sys
sys.dont_write_bytecode=True
import json
from collections import Counter
import analyze as a

def main():
    rows=json.loads((a.OUT/'audited-collisions.json').read_text())
    result=[];geos={}
    for r in rows:
        if r['side']!='us' or not r.get('card_observable'):continue
        gid=r['gid']
        if gid not in geos:
            gm=json.loads((a.OUT/f'g{gid}.json').read_text())
            geos[gid]=a.Geo(a.lr.replay.load(a.ROOT/gm['path']).root().text(0))
        g=geos[gid];bs={i:tuple(tuple(c) for c in b) for i,s,b in r['start_bodies']}
        ts={i:s for i,s,b in r['start_bodies']};v=r['victim'];hd=bs[v][0]
        enemies=[i for i,b in bs.items() if ts[i]!='us' and g.visible(b[0],hd) and len(b)>=r['victim_length']]
        safe=[];capped=0
        for op in r['view_certified_all']:
            body=tuple(tuple(c) for c in op['body']);ps=set(tuple(c) for c in op['remaining_pearls'])
            try:
                endangered=any(a.hits(g,bs,i,v,body,ps,extra_budget=True) for i in enemies)
            except RuntimeError:
                capped+=1;continue
            if not endangered:safe.append(op)
        cost=max(0,r['turn']['ate']-max((o['ate'] for o in safe),default=0)) if safe else None
        rec=dict(label=r['label'],gid=gid,collision=r['collision'],round=r['round'],safe=safe,
                 checked=len(r['view_certified_all']),capped=capped,cost=cost)
        result.append(rec)
        (a.OUT/'pearl-sensitivity.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
        print(r['label'],gid,r['round'],'safe',len(safe),'capped',capped,flush=True)
    print('done',len(result),dict(Counter((r['label'],bool(r['safe'])) for r in result)),flush=True)

if __name__=='__main__':main()
