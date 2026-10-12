"""Full-event sensitivity: pearls already present may finance extra paid steps."""
import sys
sys.dont_write_bytecode=True
import json
from collections import Counter
import analyze as a

def main():
    rows=json.loads((a.OUT/'audited-collisions.json').read_text());geos={}
    save=a.OUT/'extended.json'
    previous=json.loads(save.read_text()) if save.exists() else []
    cached={r['collision']:r for r in previous};out=[]
    for k,r in enumerate(rows):
        if r['collision'] in cached:out.append(cached[r['collision']]);continue
        rec=dict(collision=r['collision'],label=r['label'],gid=r['gid'],round=r['round'],side=r['side'],status=r['status'],capped=0,safe=[])
        if r['status']=='avoidable':
            gid=r['gid']
            if gid not in geos:
                gm=json.loads((a.OUT/f'g{gid}.json').read_text())
                geos[gid]=a.Geo(a.lr.replay.load(a.ROOT/gm['path']).root().text(0))
            g=geos[gid];bs={i:tuple(tuple(c) for c in b) for i,s,b in r['start_bodies']}
            for op in r['safe']:
                ps=set(tuple(c) for c in op['remaining_pearls']);body=tuple(tuple(c) for c in op['body'])
                try:unsafe=a.hits(g,bs,r['attacker'],r['victim'],body,ps,extra_budget=True)
                except RuntimeError:rec['capped']+=1;continue
                if not unsafe:rec['safe'].append(op)
            rec['status']='avoidable' if rec['safe'] else 'unresolved' if rec['capped'] else 'not avoidable'
        out.append(rec)
        if k%20==0:
            save.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
            print(k+1,len(rows),dict(Counter(x['status'] for x in out)),flush=True)
    save.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
    print('done',len(out),dict(Counter(x['status'] for x in out)),flush=True)

if __name__=='__main__':main()
