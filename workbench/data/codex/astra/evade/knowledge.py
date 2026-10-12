"""Card audit using only current view, with optimistic unknown terrain/pearls."""
import sys
sys.dont_write_bytecode=True
import json
from collections import deque,Counter
import analyze as a

def possible(g,body,goal,window,pearls):
    outside=(-1,-1)
    inside=list(window);portals=set();boundary=set()
    adj={}
    for c in inside:
        ns=set()
        for d,n in enumerate(g.moves[c]):
            edge=g.edges.get(a.lr.edge_id(g.w,g.h,*c,d),(0,-1))[0]
            if edge==2:
                portals.add(c)
                # A visible portal's unknown partner could end outside or at another visible portal.
                ns.add(outside);ns.update(n for n in g.adj[c] if n in window)
            elif n is not None:
                ns.add(n if n in window else outside)
                if n not in window:boundary.add(c)
        adj[c]=ns
    for c in portals: adj[c].update(portals)
    adj[outside]=boundary|portals|{outside}
    ps=sorted(pearls&window);bits={c:1<<k for k,c in enumerate(ps)}
    free=(len(body)+3)//4
    todo=deque([(body[0],0,len(body),0)]);seen=set(todo)
    while todo:
        c,phase,L,mask=todo.popleft()
        if phase==free and L<3:continue
        for n in adj[c]:
            if n==goal:return True
            bit=bits.get(n,0);eat=n==outside or bool(bit and not mask&bit)
            ll=L+eat-(phase==free);ph=min(free,phase+1);mm=mask|bit
            state=(n,ph,ll,mm)
            if state not in seen:
                seen.add(state);todo.append(state)
                if len(seen)>100000:return None
    return False

def main():
    rows={r['collision']:r for r in json.loads((a.OUT/'audited-collisions.json').read_text())}
    prior=json.loads((a.OUT/'pearl-sensitivity.json').read_text());result=[];geos={}
    for item in prior:
        r=rows[item['collision']];gid=r['gid']
        if gid not in geos:
            gm=json.loads((a.OUT/f'g{gid}.json').read_text());geos[gid]=a.Geo(a.lr.replay.load(a.ROOT/gm['path']).root().text(0))
        g=geos[gid];bs={i:tuple(tuple(c) for c in b) for i,s,b in r['start_bodies']};ts={i:s for i,s,b in r['start_bodies']}
        v=r['victim'];hd=bs[v][0];window={c for c in g.adj if g.visible(c,hd)}
        enemies=[i for i,b in bs.items() if ts[i]!='us' and b[0] in window and len(b)>=r['victim_length']]
        safe=[];capped=0
        for op in item['safe']:
            pearl=set(tuple(c) for c in op['remaining_pearls']);goal=tuple(op['body'][0]);okay=True
            for i in enemies:
                can=possible(g,bs[i],goal,window,pearl)
                if can is None:capped+=1
                if can is not False:okay=False;break
            if okay:safe.append(op)
        result.append(dict(label=r['label'],gid=gid,collision=r['collision'],round=r['round'],safe=safe,capped=capped,
                           cost=max(0,r['turn']['ate']-max(op['ate'] for op in safe)) if safe else None))
    (a.OUT/'knowledge-sensitivity.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
    print(dict(Counter((r['label'],bool(r['safe'])) for r in result)))
    print('cost',dict((lab,sum(r['cost'] for r in result if r['label']==lab and r['safe'])) for lab in a.LABELS))

if __name__=='__main__':main()
