"""Geometry diagnostics, not reconstruction of the bot's remembered score.
Mate distances <=2 use visible heads and replay blockers. Safety searches
advance our entire body while other bodies stay frozen.
"""
import sys,json
sys.dont_write_bytecode=True
from scan import Board,OUT
from traps import escape
from collections import Counter,deque

def main():
    for sf in sorted(OUT.glob('scan-*.json')):
        dest=OUT/('diag-'+sf.name[5:])
        if dest.exists():continue
        meta=json.loads(sf.read_text())['meta']
        B=Board(meta['path']); rows=[]
        snaps=json.loads((OUT/('snap-'+sf.name[5:])).read_text())
        for r in snaps:
            if r['d']!=2 or r['cls']!='away':continue
            s=r['snapshot']; i=r['i']; own=meta['own']; h=tuple(r['h']); L=r['L']
            bodies={int(z):tuple(map(tuple,b)) for z,b in s['bodies'].items()}
            teams={int(z):v for z,v in s['teams'].items()}
            occ=set(c for b in bodies.values() for c in b)
            pearls=set(map(tuple,s['pearls'])); targets=list(map(tuple,r['targets']))
            mates=[b[0] for z,b in bodies.items() if z!=i and teams[z]==own and B.view(h,b[0])]
            md={t:99 for t in targets}
            for m in mates:
                ds=B.flood(m,2,occ)
                for t in targets:md[t]=min(md[t],ds.get(t,99))
            assignment='all_mate_nearer' if all(md[t]<2 for t in targets) else 'has_unclaimed'
            unclaimed=[t for t in targets if md[t]>=2]
            paths=[]
            for n in B.adj[h]:
                if n is None or n in occ:continue
                for t in B.adj[n]:
                    if t not in targets or t in occ:continue
                    body1=(n,)+bodies[i][:-1]
                    others=occ-set(bodies[i])
                    safe=escape(B,body1,t,pearls,others)
                    paths.append(dict(first=n,target=t,mate_distance=md[t],safety=safe))
            rs={k:v for k,v in r.items() if k!='snapshot'}
            rs.update(assignment=assignment,paths=paths,
                      safe_unclaimed=any(p['mate_distance']>=2 and p['safety']['status']=='escape' for p in paths),
                      safe_any=any(p['safety']['status']=='escape' for p in paths))
            rows.append(rs)
        dest.write_text(json.dumps(dict(meta=meta,rows=rows),separators=(',',':')))
        print(meta['label'],meta['game'],len(rows),dict(Counter(r['assignment'] for r in rows)),flush=True)

if __name__=='__main__':main()
