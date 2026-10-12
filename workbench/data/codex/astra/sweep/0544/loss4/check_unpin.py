import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from analyze import Geo,lr
p=Path(__file__).parent
a=json.loads((p/'1493891-detail.json').read_text());t=next(t for t in a['qturns'] if t['r']==302)
W,H=a['W'],a['H'];hd=t['body'][0];cx,cy=hd%W,hd//W
root=lr.replay.load(Path('data/online/smoke/one8-c2-old/M1493891.replay')).root()
geo=Geo(W,H,[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')])
body={int(i):b for i,b in t['bodies'].items()};own=1;occ={c:i for i,b in body.items() for c in b};pearls=set(t['pearls'])
visible=lambda c: min(abs(c%W-cx),W-abs(c%W-cx))<=3 and min(abs(c//W-cy),H-abs(c//W-cy))<=3
mates=[150,1137]
# Both nearby mate bodies are wholly visible; all decisive edges are known.
rows=[]
for d in [0,1]:
 dest=geo.nxt[hd][d];ours=[dest]+body[own][:]
 if dest not in pearls:ours.pop()
 risks=[]
 for m in mates:
  mb=body[m][:];eaten=set();trace=[];worst=0
  for depth in range(5):
   ns=[];unknown=False
   for c in geo.nxt[mb[0]]:
    if c<0:continue
    if not visible(c):unknown=True
    if c in ours or c in mb:continue
    owner=occ.get(c)
    if owner is not None and owner not in [own,m]:continue
    ns.append(c)
   trace.append({'depth':depth,'head':[mb[0]%W,mb[0]//W],'exits':[[c%W,c//W] for c in ns],'unknown':unknown})
   if unknown or len(ns)>1:break
   if not ns:worst=2 if depth==0 else 1;break
   if depth==4:break
   c=ns[0];mb.insert(0,c)
   if c in pearls and c!=dest and c not in eaten:eaten.add(c)
   else:mb.pop()
  risks.append({'mate':m,'risk':worst,'trace':trace})
 rows.append({'direction':'NESW'[d],'risk':max(x['risk'] for x in risks),'mates':risks})
(p/'unpin-check.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
