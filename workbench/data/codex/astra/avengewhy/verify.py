import sys,json,hashlib,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
from analyze import replay,Geo,SM,OUT,TARGET
checks=[]
for lp in sorted(OUT.glob('ledger-*.json')):
 l=json.loads(lp.read_text());gid=l['gid'];folder=SM/(l['src']+'-old');meta=json.loads((folder/f'game-{gid}.json').read_text());r=replay.load(folder/f'M{gid}.replay').root();own=int(meta['teamAId']!=1119)
 lines=[s.split() for s in r.text(0).splitlines()];start=[0,0];heads={};w,h=map(int,lines[0][1:3])
 for q in lines:
  if q[0]=='DRAGON':start[int(int(q[1])!=own)]+=int(q[2]);heads[len(heads)]=int(q[4])*w+int(q[3])
 residual=[]
 for side in (0,1):
  expected=start[side]+sum(e[1]==side for e in l['eats'])-sum(d[2] for d in l['deaths'] if d[1]==side)-sum(p[3] for p in l['paids'] if p[1]==side)
  residual.append(l['ends'][side][1]-expected)
 assert residual==[0,0],(gid,residual)
 bad=0;moves=0
 if gid in TARGET:
  g=Geo(w,h,[tuple(map(int,q[1:4])) for q in lines if q[0]=='EDGE'])
  for e in r.pointer(3):
   k=e.u16(0);p=e.pointer(0)
   if k==9:
    i=p.i32(0);x,y=replay.point(p.pointer(0));c=y*w+x
    if c!=heads[i]:moves+=1;bad+=c not in g.adj[heads[i]]
    heads[i]=c
   if k==10:
    for z,i in enumerate((p.i32(0),p.i32(4))):
     x,y=replay.point(next(iter(p.pointer(z))));heads[i]=y*w+x
  assert bad==0,(gid,bad)
 dp=OUT/f'detail-{gid}.json'
 if dp.exists():
  d=json.loads(dp.read_text());assert d['finalQ']==[s[3] for s in l['ends']]
  if gid in TARGET:
   assert all(p.get('state',0)==0 for p in d['pings'])
   assert all(t['L']>8 for t in d['reach'])
   assert not any(x['side']==0 and x['target']==[d['queens'][1],'body'] for x in d['deaths'])
 checks.append(dict(gid=gid,mass_residual=residual,head_moves_checked=moves,bad_head_moves=bad))
assert len(checks)==45
assert sum(bool(l['ends'][0][3] and l['ends'][1][3]) for p in OUT.glob('ledger-*.json') for l in [json.loads(p.read_text())])==6
report=(OUT/'report.md').read_text();words=len(' '.join(l for l in report.splitlines() if not l.startswith('|')).split());assert words<450
out=dict(time=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip(),games=45,report_words_excluding_tables=words,source_sha256=hashlib.sha256((SM/'one8-bot/main.cpp').read_bytes()).hexdigest(),checks=checks)
(OUT/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
