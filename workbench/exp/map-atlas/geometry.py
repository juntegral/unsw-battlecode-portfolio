"""Independent static graph, map-table verification, min vertex cuts, SVG plates."""
import pathlib,json,re,collections,math,html
ROOT=pathlib.Path(__file__).resolve().parents[2];OUT=ROOT/'exp/map-atlas/cache'
from collections import deque
def graph(M):
    W,H=M['width'],M['height'];N=W*H
    canon=lambda e:(e['x'],(e['y']+1)%H,'N') if e['side']=='S' else ((e['x']+1)%W,e['y'],'W') if e['side']=='E' else (e['x'],e['y'],e['side'])
    portals={}
    for p in M['portals']:
        a,b=map(canon,p);portals[a]=b;portals[b]=a
    nb=[[] for _ in range(N)];walls=[]
    for y in range(H):
        for x in range(W):
            for z,(dx,dy) in enumerate([(0,-1),(1,0),(0,1),(-1,0)]):
                horiz=z in [0,2];ex=(x+1)%W if z==1 else x;ey=(y+1)%H if z==2 else y
                k=(ex,ey,'N' if horiz else 'W')
                wall=(M['initialHEdges'][ey*W+ex]==1 or ey==0 and M['initialHEdges'][H*W+ex]==1) if horiz else (M['initialVEdges'][ey*(W+1)+ex]==1 or ex==0 and M['initialVEdges'][ey*(W+1)+W]==1)
                if wall and z in [0,3]: walls.append([ex,ey,'N' if horiz else 'W'])
                if k in portals:
                    px,py,_=portals[k]
                    if z==0:py=(py-1)%H
                    if z==3:px=(px-1)%W
                    dest=py*W+px
                elif wall:continue
                else:dest=(y+dy)%H*W+(x+dx)%W
                nb[y*W+x].append(dest)
    return nb,walls,portals
def bfs(nb,seeds):
    D=[999]*len(nb);q=deque()
    for k in seeds:
        if D[k]!=0:D[k]=0;q.append(k)
    while q:
        k=q.popleft()
        for v in nb[k]:
            if D[v]==999:D[v]=D[k]+1;q.append(v)
    return D
def mincut(nb,A,B):
    N=len(nb);S=2*N;T=S+1;adj=[[] for _ in range(T+1)];starts=set(A+B)
    def edge(a,b,c):adj[a].append([b,c,len(adj[b])]);adj[b].append([a,0,len(adj[a])-1])
    for k,vs in enumerate(nb):
        edge(2*k,2*k+1,N if k in starts else 1)
        for v in vs:edge(2*k+1,2*v,N)
    for k in A:edge(S,2*k,N)
    for k in B:edge(2*k+1,T,N)
    flow=0
    while True:
        level=[-1]*len(adj);level[S]=0;q=deque([S])
        while q:
            u=q.popleft()
            for v,c,r in adj[u]:
                if c and level[v]<0:level[v]=level[u]+1;q.append(v)
        if level[T]<0:return flow
        it=[0]*len(adj)
        def dfs(u,f):
            if u==T:return f
            while it[u]<len(adj[u]):
                e=adj[u][it[u]];v,c,rev=e
                if c and level[v]==level[u]+1:
                    got=dfs(v,min(f,c))
                    if got:e[1]-=got;adj[v][rev][1]+=got;return got
                it[u]+=1
            return 0
        while True:
            f=dfs(S,N)
            if not f:break
            flow+=f
def plate(o,nb,walls,terr,gaps):
    M=o['M'];W,H=M['width'],M['height'];sc=12;pad=24
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*sc+48}" height="{H*sc+85}" viewBox="0 0 {W*sc+48} {H*sc+85}">','<rect width="100%" height="100%" fill="white"/>',f'<text x="24" y="19" font-family="sans-serif" font-size="15">{html.escape(o["map"])} / {o["layout"]}</text>']
    for k,t in enumerate(terr):
        x=k%W*sc+pad;y=k//W*sc+pad
        svg.append(f'<rect x="{x}" y="{y}" width="12" height="12" fill="{["#eee","#d9eafe","#ffe5d9"][t]}"/>')
        q=gaps.get(k)
        if q and q[1]:svg.append(f'<circle cx="{x+6}" cy="{y+6}" r="{3 if sum(q)/2<=12 else 1.3}" fill="{ "#048555" if sum(q)/2<=12 else "#7da897"}"/>')
    for x,y,s in walls:
        xx=x*sc+pad;yy=y*sc+pad;dx,dy=(sc,0) if s=='N' else (0,sc)
        svg.append(f'<path d="M{xx} {yy}l{dx} {dy}" stroke="#17262d" stroke-width="2"/>')
    for i,p in enumerate(M['portals']):
        for e in p:
            x,y,s=e['x'],e['y'],e['side'];xx=x*sc+pad;yy=y*sc+pad
            if s=='E':xx+=sc
            if s=='S':yy+=sc
            dx,dy=(sc,0) if s in ['N','S'] else (0,sc)
            svg.append(f'<path d="M{xx} {yy}l{dx} {dy}" stroke="#a040d0" stroke-width="3"/><text x="{xx+2}" y="{yy+9}" font-size="6" fill="#8a22ab">{i}</text>')
    for d in M['initialDragons']:
        for i,p in enumerate(d['body']):
            x=p['x']*sc+pad;y=p['y']*sc+pad
            svg.append(f'<rect x="{x+2}" y="{y+2}" width="8" height="8" fill="{"#2363ae" if d["team"]=="A" else "#d6532b"}"/>')
            if i==0:svg.append(f'<text x="{x+3}" y="{y+9}" font-size="6" fill="white">{d["id"]}</text>')
    svg += [f'<rect x="24" y="24" width="{W*sc}" height="{H*sc}" stroke="#555" stroke-dasharray="3 3" fill="none"/>',f'<text x="24" y="{H*sc+47}" font-family="sans-serif" font-size="10">blue/orange: initial territory and bodies; green: spawn, large: fountain; purple: portal ID</text>',f'<text x="24" y="{H*sc+63}" font-family="sans-serif" font-size="10">All boundaries wrap; dark lines block movement. Distances include portals.</text>','</svg>']
    name=f'{o["map"].lower().replace(" ","_")}-{o["layout"]}.svg';(ROOT/'exp/map-atlas'/name).write_text('\n'.join(svg));return name
def main():
    table=(ROOT/'bot/mapdb.hpp').read_text();pat=r'\{"([^"]+)", (\d+), (\d+),\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*(\d+), PAL(\d+),\s*"([^"]+)", (\d+), \'(.)\', (true|false)\}'
    entries=list(re.finditer(pat,table));pal={int(n):list(map(int,v.split(','))) for n,v in re.findall(r'static const int PAL(\d+)\[\] = \{([^}]+)\}',table)}
    terrtables=re.findall(r'"([012]+)", // ([^\n]+)',(ROOT/'bot/terrdb.hpp').read_text())
    out={}
    for p in sorted(OUT.glob('geometry-*.json')):
        o=json.loads(p.read_text());M=o['M'];name=o['map'];lay=o['layout'];W,H=M['width'],M['height'];N=W*H
        for field in ['initialHEdges','initialVEdges','initialTiles']:
            if isinstance(M[field],dict):M[field]=[v for k,v in sorted(M[field].items(),key=lambda q:int(q[0]))]
        mp=name.lower().replace(' ','_');f=ROOT/('maps/variants' if lay in ['b','10'] else 'maps/online-20260927')/(mp+('_b' if lay=='b' else '_10' if lay=='10' else '')+'.map')
        gaps={};starts=[];sym=None
        for l in f.read_text().splitlines():
            a=l.split()
            if a and a[0]=='TILE':x,y,lo,hi=map(int,a[1:]);gaps[y*W+x]=[lo,hi]
            if a and a[0]=='DRAGON':starts.append({'team':'A' if a[1]=='0' else 'B','len':int(a[2]),'body':[[int(a[i]),int(a[i+1])] for i in range(3,len(a),2)]})
            if a and a[0]=='SYMMETRY':sym=a[1]
        nb,walls,ports=graph(M);A=[q['y']*W+q['x'] for d in M['initialDragons'] if d['team']=='A' for q in d['body']];B=[q['y']*W+q['x'] for d in M['initialDragons'] if d['team']=='B' for q in d['body']]
        da,db=bfs(nb,A),bfs(nb,B);terr=[1 if a<b else 2 if b<a else 0 for a,b in zip(da,db)]
        cap=[0,0,0];sp=[0,0,0];fnt=[0,0,0];classes=collections.Counter();fcoords=[]
        for k,g in gaps.items():
            classes[tuple(g)]+=1
            if g[1]:sp[terr[k]]+=1;cap[terr[k]]+=2/sum(g)
            if g[1] and sum(g)/2<=12:fnt[terr[k]]+=1;fcoords.append([k%W,k//W,*g,terr[k]])
        seen=set();comps=[]
        for k in range(N):
            if k in seen:continue
            q=deque([k]);seen.add(k);c=[]
            while q:
                u=q.popleft();c.append(u)
                for v in nb[u]:
                    if v not in seen:seen.add(v);q.append(v)
            comps.append(c)
        hA=[d['body'][0]['y']*W+d['body'][0]['x'] for d in M['initialDragons'] if d['team']=='A'];hB=[d['body'][0]['y']*W+d['body'][0]['x'] for d in M['initialDragons'] if d['team']=='B'];pd=min(bfs(nb,hA)[k] for k in hB);bd=min(da[k] for k in B)
        torus=min(min(abs(a%W-b%W),W-abs(a%W-b%W))+min(abs(a//W-b//W),H-abs(a//W-b//W)) for a in hA for b in hB)
        matched=None;botGapMismatch=None;botTerrMismatch=None
        for i,e in enumerate(entries):
            g=e.groups()
            if g[0].replace('_',' ')==name and (g[11]==lay or lay in ['6','10'] and (('10' in g[0])==(lay=='10'))):matched=(i,g);break
        # PD10 uses the same family name and is stored as layout b. Match its actual spawn table.
        candidates=[(i,e.groups()) for i,e in enumerate(entries) if e.group(1).replace('_',' ')==name and len(e.group(10))==N]
        if candidates:
            def mismatch(c):
                g=c[1];P=pal[int(g[8])]
                return sum(P[2*(ord(ch)-48):2*(ord(ch)-48)+2]!=gaps.get(k,[0,0]) for k,ch in enumerate(g[9]))
            matched=min(candidates,key=mismatch)
        if matched:
            i,g=matched;P=pal[int(g[8])];spawn=g[9];botGapMismatch=sum(P[2*(ord(c)-48):2*(ord(c)-48)+2]!=gaps.get(k,[0,0]) for k,c in enumerate(spawn))
            if i<len(terrtables):
                t=list(map(int,terrtables[i][0]));botTerrMismatch=min(sum(x!=y for x,y in zip(t,terr)),sum((3-x if x else 0)!=y for x,y in zip(t,terr)))
        row={'map':name,'layout':lay,'W':W,'H':H,'sym':sym,'kelpEdges':len(walls),'kelpDensity':len(walls)/(2*N),'portalPairs':len(M['portals']),'starts':starts,'spawnTiles':sum(sp),'spawnTerr':sp,'fountainTerr':fnt,'capacity':sum(cap),'capTerr':cap,'gapClasses':[{'gap':list(g),'tiles':n} for g,n in sorted(classes.items())],'fountains':fcoords,'terrTiles':[terr.count(z) for z in [0,1,2]],'components':len(comps),'componentSizes':sorted([len(c) for c in comps],reverse=True),'reachableA':sum(d<999 for d in da),'reachableB':sum(d<999 for d in db),'headPath':None if pd==999 else pd,'bodyPath':None if bd==999 else bd,'headTorus':torus,'vertexCut':mincut(nb,A,B) if pd<999 else 0,'frontierEdges':sum(terr[k] and terr[v] and terr[k]!=terr[v] for k,vs in enumerate(nb) for v in vs)//2,'botGapMismatch':botGapMismatch,'botTerrMismatch':botTerrMismatch}
        row['svg']=plate(o,nb,walls,terr,gaps);out[name+'/'+lay]=row
    (OUT/'geometry.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({k:{z:v[z] for z in ['capacity','headPath','vertexCut','botGapMismatch','botTerrMismatch']} for k,v in out.items()}))
if __name__=='__main__':main()
