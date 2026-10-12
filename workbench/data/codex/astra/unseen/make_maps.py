"""Deterministic audit fixtures, using the existing maps' directive/edge format."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
OUT=HERE/"maps"
OUT.mkdir(exist_ok=True)
manifest=[]

class Map:
    def __init__(self,name,w,h,sym="xy",limit=64):
        self.name,self.w,self.h,self.sym,self.limit=name,w,h,sym,limit
        self.tiles=[(0,0)]*(w*h)
        self.edges=[(0,-1)]*(2*w*h)
        self.dragons=[]
    def tile(self,x,y): return y*self.w+x
    def edge(self,x,y,vertical=False): return (self.w*self.h if vertical else 0)+self.tile(x,y)
    def mirror(self,k,edge=False):
        n=self.w*self.h
        vertical=edge and k>=n
        x,y=(k%n)%self.w,(k%n)//self.w
        if self.sym and "y" in self.sym: x=(self.w-(0 if vertical else 1)-x)%self.w
        if self.sym and "x" in self.sym: y=(self.h-(1 if vertical else 0)-y)%self.h
        return (n if vertical else 0)+y*self.w+x
    def mirrored_tile(self,k):
        x,y=k%self.w,k//self.w
        if self.sym and "y" in self.sym: x=self.w-1-x
        if self.sym and "x" in self.sym: y=self.h-1-y
        return y*self.w+x
    def bed(self,x,y,lo,hi):
        k=self.tile(x,y);self.tiles[k]=(lo,hi)
        if self.sym: self.tiles[self.mirrored_tile(k)]=(lo,hi)
    def wall(self,x,y,vertical=False):
        k=self.edge(x,y,vertical);self.edges[k]=(1,-1)
        if self.sym:self.edges[self.mirror(k,True)]=(1,-1)
    def pair(self,a,b,pid):
        self.edges[a]=self.edges[b]=(2,pid)
    def starter(self,body,team=0,mirror=True):
        self.dragons.append((team,[self.tile(x,y) for x,y in body]))
        if mirror:
            self.dragons.append((1-team,[self.mirrored_tile(k) for k in self.dragons[-1][1]]))
    def save(self,purpose):
        rows=[f"MAP {self.w} {self.h}"]
        if self.sym: rows.append(f"SYMMETRY {self.sym}")
        rows += [f"MAP_NAME {self.name}",f"UNIT_LIMIT {self.limit}",f"TILE_COUNT {len(self.tiles)}"]
        rows += [f"TILE {i%self.w} {i//self.w} {lo} {hi}" for i,(lo,hi) in enumerate(self.tiles)]
        # Alternate horizontal/vertical rows; width+1 stride includes padding.
        rows.append(f"EDGE_COUNT {len(self.edges)}")
        for k,(kind,pid) in enumerate(self.edges):
            n=self.w*self.h;i=k%n;x,y=i%self.w,i//self.w
            raw=(2*y+(k>=n))*(self.w+1)+x
            rows.append(f"EDGE {raw} {kind} {pid}")
        rows.append(f"DRAGON_COUNT {len(self.dragons)}")
        rows += [f"DRAGON {team} {len(body)} "+" ".join(f"{k%self.w} {k//self.w}" for k in body) for team,body in self.dragons]
        rows.append("END")
        p=OUT/(self.name+".map");p.write_text("\n".join(rows)+"\n")
        manifest.append(dict(file=p.name,width=self.w,height=self.h,cells=self.w*self.h,unit_limit=self.limit,dragons=len(self.dragons),purpose=purpose))

def plain(name,w,h,sym="xy",limit=64,length=4):
    m=Map(name,w,h,sym,limit)
    m.starter([(3+i,3) for i in range(length)])
    for y in range(h):
        for x in range(w):
            if (x+y)%7==0:m.bed(x,y,8,30)
    return m

m=plain("un_portalid_1",16,16)
e=m.edge(3,3);m.pair(e,m.mirror(e,True),8000000)
m.save("Sparse portal ID: observing the mouth attempts an 8,000,001-entry array (64,000,008 bytes).")
m=plain("un_portalid_2",16,16)
e=m.edge(3,3);m.pair(e,m.mirror(e,True),0)
m.save("Geometrically identical control with dense portal ID 0.")
for name,w,h in [("un_sonar128_1",129,32),("un_sonar128_2",32,129),("un_sonar128_3",128,128),("un_width64_1",65,16),("un_cells4096_1",64,65),("un_cells4097_1",17,241)]:
    plain(name,w,h).save("Coordinate/index boundaries: compare constructor sonar gate and dormant sight codec.")
m=plain("un_cpu_1",256,256)
m.dragons=[]
for i in range(64):
    x=4+(i%16)*7;y=4+(i//16)*10
    if i==1:x,y=4,6
    m.starter([(x+j,y) for j in range(4)])
m.save("Largest legal open board, 64 starters per side (default unit cap reached); full-map floods and surveys.")
for name,limit,starters in [("un_unitcap_1",8,8),("un_unitcap_2",256,64),("un_id32768_1",512,128)]:
    m=Map(name,128,128,"xy",limit)
    m.tiles=[(1,1)]*(128*128)
    for i in range(starters):
        x=3+(i%16)*7;y=3+(i//16)*6
        m.starter([(x+j,y) for j in range(4)])
    m.save("Custom unit limit and fast births: fixed 56/60 thresholds; high cumulative dragon IDs under churn are not guaranteed.")
for name,w,h in [("un_queen600_1",24,25),("un_queen600_2",24,26),("un_center700_1",28,25),("un_center700_2",28,26),("un_center1000_1",50,20),("un_center1000_2",51,20),("un_aggressive1200_1",48,25),("un_aggressive1200_2",49,25),("un_aspect_1",40,16),("un_aspect_2",16,40)]:
    plain(name,w,h).save("Area/aspect boundary for queen identity gate, center pull, aggression or leader grow timing.")
for sym in ["x","y","xy",None]:
    name="un_symmetry_"+str(["x","y","xy",None].index(sym)+1)
    m=plain(name,32,24,sym)
    m.wall(2,2);m.wall(9,8,True)
    if not sym:
        m.bed(11,7,1,1)
        # Actual queen belongs to B; no assumed A=id0 or mirrored starting bodies.
        m.dragons=[];m.starter([(3,3),(2,3)],team=1,mirror=False);m.starter([(20,16),(21,16),(22,16),(23,16)],team=0,mirror=False)
    m.save("Supported declared symmetry or legal omission/asymmetry. SYM_INFER is false in live one5; do not enable it unvalidated.")
m=plain("un_edgewrap_1",16,16)
for x in range(16):m.wall(x,0)
for y in range(16):m.wall(0,y,True)
m.save("Torus with kelp walls on seam edges (a physically closed rectangle).")
m=Map("un_portalonly_1",32,16,"xy")
for y in range(16):m.wall(16,y,True);m.wall(0,y,True)
e=m.edge(16,3,True);m.pair(e,m.mirror(e,True),0)
m.starter([(12,3),(11,3),(10,3),(9,3)])
for y in range(16):
    for x in range(32):m.bed(x,y,1 if x in range(17,24) or x in range(8,15) else 500,1 if x in range(17,24) or x in range(8,15) else 500)
m.save("Portal access between sealed halves: remote endpoint discovery and size-gated queen portal ban.")
m=plain("un_startlength_1",32,16,length=2);m.save("Two-dragon start, queen length 2 (legal).")
m=Map("un_startlength_2",128,32,"xy")
body=[]
for y in range(1,9):
    body += [(x,y) for x in (range(2,126) if y%2 else range(125,1,-1))]
body += [(2,9),(3,9)]
# 8*124+2 = 994 is below the 1023 sonar length cap; use 9 rows for >1023.
body=[]
for y in range(1,10):body += [(x,y) for x in (range(2,126) if y%2 else range(125,1,-1))]
m.starter(body)
m.save("Two legal long starters (1116): body beyond vision, QH leader length saturates at 1023.")
m=Map("un_startlayout_1",16,16,None)
m.starter([(1,1),(0,1)],1,False);m.starter([(8,8),(9,8),(10,8)],0,False);m.starter([(2,6),(3,6)],1,False)
m.save("Odd starter count, B queen has id 0; non-mirrored lengths and positions.")
m=Map("un_timers_1",32,32,"xy")
m.starter([(3,3),(2,3),(1,3),(0,3)])
for x,y,gap in [(3,2,1),(8,4,30),(11,5,501),(14,6,1000000),(15,9,2147483647)]:m.bed(x,y,gap,gap)
m.save("Timers from 1 to signed-int max; sparse fountains and slow/absent supply challenge hot/barren heuristics.")
m=Map("un_threatreach_1",128,64,None)
m.starter([(3,3),(3,4),(3,5),(3,6)],0,False)
m.starter([(100,50),(101,50)],1,False)
m.starter([(20,40),(21,40)],0,False)
m.starter([(x,3) for x in range(6,67)],1,False)
m.save("Enemy nonqueen L61 head visible beside our queen; most body outside 7x7, actual free reach16 versus visible stub and threat depth caps.")
(HERE/"maps_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(f"Wrote {len(manifest)} maps")
