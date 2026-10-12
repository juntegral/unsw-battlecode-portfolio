import json,gzip,hashlib,base64,collections,subprocess,time
from pathlib import Path
O=Path(__file__).parent
errors=[];checks=0
def guard():
    d=subprocess.check_output(['df','-k','.'],text=True).strip().splitlines()[-1].split();m=subprocess.check_output(['memory_pressure','-Q'],text=True)
    import re
    match=re.search(r'System-wide memory free percentage:\s*(\d+)%',m)
    return int(d[3])/1048576>=21 and match and int(match[1])>=10
def check(label,a,b):
    global checks
    checks+=1
    if a!=b:errors.append({'label':label,'expected':a,'actual':b})
def build(M):
    W,H=M['width'],M['height'];N=W*H
    def array(v):return [v[str(i)] for i in range(len(v))] if isinstance(v,dict) else v
    M={**M,'initialHEdges':array(M['initialHEdges']),'initialVEdges':array(M['initialVEdges'])}
    def tile(x,y):return y%H*W+x%W
    def step(k,d):return tile(k%W+[0,1,0,-1][d],k//W+[-1,0,1,0][d])
    def edge(k,d):return [k,N+step(k,1),step(k,2),N+k][d]
    kind=[0]*(2*N);partners={}
    for y in range(H):
        for x in range(W):
            k=y*W+x;kind[k]=int(M['initialHEdges'][k]==1 or y==0 and M['initialHEdges'][N+x]==1);kind[N+k]=int(M['initialVEdges'][y*(W+1)+x]==1 or x==0 and M['initialVEdges'][y*(W+1)+W]==1)
    for pair in M['portals']:
        a,b=[edge(tile(p['x'],p['y']),'NESW'.index(p['side'])) for p in pair];kind[a]=kind[b]=2;partners[a]=b;partners[b]=a
    def mirror(k,h):return tile(W-1-k%W if h in (0,2) else k%W,H-1-k//W if h in (1,2) else k//W)
    md=[[0,3,2,1],[2,1,0,3],[2,3,0,1]]
    em=[]
    for h in range(3):
        m=[0]*(2*N)
        for k in range(N):
            for d in (0,3):m[edge(k,d)]=edge(mirror(k,h),md[h][d])
        em.append(m)
    def known(seen):return {edge(k,d) for k in range(N) if seen[k] for d in range(4)}
    def graph(seen,mode,physical=None,h=None):
        seen_edges=known(seen);physical=seen_edges if physical is None else physical;resolved={e for e in physical if e in partners and partners[e] in physical}
        if h is not None:resolved|={em[h][e] for e in list(resolved)}
        nb=[set() for k in range(N)];unresolved=0
        for k in range(N):
            for d in range(4):
                e=edge(k,d)
                if e not in seen_edges:
                    if mode!='wall':nb[k].add(step(k,d))
                elif kind[e]==0:nb[k].add(step(k,d))
                elif kind[e]==2:
                    p=partners[e]
                    if p in seen_edges and e in resolved:nb[k].add(step(p%N,d) if d in (0,3) else p%N)
                    else:
                        unresolved+=1
                        if mode=='literal':nb[k].add(step(k,d))
                        elif mode=='open':
                            for j in range(0 if d%2==0 else N,N if d%2==0 else 2*N):
                                if j not in seen_edges or kind[j]==2 and j not in resolved:
                                    v=step(j%N,d) if d in (0,3) else j%N
                                    if v!=k:nb[k].add(v)
        return nb,unresolved
    starts={t:[d['body'][0]['y']*W+d['body'][0]['x'] for d in M['initialDragons'] if d['team']==t] for t in 'AB'}
    return N,mirror,known,graph,starts
def core(nb):
    # Synchronous fixed-point peeling, independent of the extractor's degree queue.
    a=[set(v) for v in nb]
    for k,vs in enumerate(nb):
        for v in vs:a[v].add(k)
    live=set(range(len(nb)))
    while True:
        gone={k for k in live if len(a[k]&live)<2}
        if not gone:return live
        live-=gone
def distance(nb,seeds):
    d=[-1]*len(nb);q=collections.deque()
    for s in seeds:
        if d[s]<0:d[s]=0;q.append(s)
    while q:
        u=q.popleft()
        for v in nb[u]:
            if d[v]<0:d[v]=d[u]+1;q.append(v)
    return d
def bins(nb,a,b):
    x,y=distance(nb,a),distance(nb,b);return [5 if u<0 and v<0 else 4 if u<0 else 0 if v<0 else min(4,int(5*(u/(u+v) if u+v else .5))) for u,v in zip(x,y)]
def main():
    P=json.loads((O/'population.json').read_text());groups=collections.defaultdict(list)
    for t in P['tasks']:groups[(t['src'],t['map'],t.get('layout','a'))].append(t)
    # At least one local/online/elite replay for every available map and layout; selected without outcomes.
    chosen=[sorted(ts,key=lambda t:hashlib.sha256(('geometry:'+t['key']).encode()).hexdigest())[0] for ts in groups.values()]
    geometryN=0;truthSeen=set()
    for t in chosen:
        while not guard():print('RESOURCE PAUSE',flush=True);time.sleep(30)
        a=json.load(gzip.open(O/'raw'/(hashlib.sha256(t['key'].encode()).hexdigest()[:20]+'.json.gz'),'rt'));N,mirror,known,graph,starts=build(a['M']);full=graph([1]*N,'literal')[0];trueCore=core(full);truth={tm:bins(full,starts[tm],starts['B' if tm=='A' else 'A']) for tm in 'AB'}
        for r,c in a['cp'].items():
            for tm,v in c['teams'].items():
                raw=list(base64.b64decode(v['seenMask']));h={1:0,2:1,4:2}.get(v['mask']);mir=raw.copy()
                if h is not None:
                    for k in range(N):
                        if raw[k]:mir[mirror(k,h)]=1
                for label,seen in [('raw',raw),('mirrored',mir)]:
                    e=known(raw);g=v['geometry'][label]
                    for mode,key in [('open','optimistic'),('wall','pessimistic'),('literal','literalOptimistic')]:
                        nb,un=graph(seen,mode,e,h if label=='mirrored' else None);co=core(nb);tp=sum(seen[k] and k not in co and k not in trueCore for k in range(N));fp=sum(seen[k] and k not in co and k in trueCore for k in range(N));fn=N-len(trueCore)-tp
                        for k,n in [('tp',tp),('fp',fp),('fn',fn)]:check(f"{t['key']} r{r} {tm} {label} {mode} {k}",n,g[key][k])
                        geometryN+=1
                        if mode=='literal':
                            guess=h if h is not None else 2 if v['mask']&4 else 0 if v['mask']&1 else 1;fb=bins(nb,starts[tm],[mirror(k,guess) for k in starts[tm]]);cor=sum(seen[k] and fb[k]==truth[tm][k] for k in range(N));check(f"{t['key']} r{r} {tm} {label} fbin",cor,g['frontier']['correct'])
        if len(truthSeen)%5==0:print('geometry',len(truthSeen),len(chosen),flush=True)
        truthSeen.add(t['key'])
    out={'method':'separate Python edge/portal graph, synchronous 2-core peeling, deque BFS, all map/source/layout strata; raw/mirrored regions and three unknown-edge modes','games':len(chosen),'graphN':geometryN,'comparisonN':checks,'mismatchN':len(errors),'mismatches':errors[:100]};(O/'verification-geometry.json').write_text(json.dumps(out,ensure_ascii=False,indent=1)+'\n');print(out)
if __name__=='__main__':main()
