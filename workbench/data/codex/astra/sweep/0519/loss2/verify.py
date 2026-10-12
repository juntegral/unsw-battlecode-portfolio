import sys,json,gzip
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'data/analysis/ladder/dossier/local');from count_local import Geo
O=Path('data/codex/astra/sweep/0519/loss2');out={}
for gid in [1491744,1492091,1492092]:
 a=json.load(gzip.open(O/f'{gid}-turns.json.gz','rt'));s=json.loads((O/f'{gid}-summary.json').read_text());w,h=a['w'],a['h'];g=Geo(w,h,a['raw']);qi=str(s['queens']['us']);eq=str(s['queens']['them']);cache={};res={'min_graph':None,'min_manhattan':None,'within5_graph_states':0,'within5_manhattan_states':0}
 def check(b,r):
  if qi in b or eq not in b:return
  src=b[eq][0]
  if src not in cache:
   d={src:0};q=deque([src])
   while q:
    c=q.popleft()
    for n in g.adj[c]:
     if n not in d:d[n]=d[c]+1;q.append(n)
   cache[src]=d
  for i,v in b.items():
   if a['team'][i]!=0:continue
   c=v[0];dx=abs(src%w-c%w);dy=abs(src//w-c//w);man=min(dx,w-dx)+min(dy,h-dy);dd=cache[src].get(c,99999)
   for k,n in [('graph',dd),('manhattan',man)]:
    row=[n,r,int(i),[c%w,c//w],[src%w,src//w]]
    if res['min_'+k] is None or row<res['min_'+k]:res['min_'+k]=row
    res['within5_'+k+'_states']+=n<=5
 for t in a['turns']:
  if qi in t['start']:continue
  check(t['start'],t['r']);b=dict(t['start'])
  for u in t['updates']:b[str(u['id'])]=u['body'];check(b,t['r'])
  check(t['end'],t['r'])
 if gid==1492091:
  res['r127_cell28_10']=[(i,v) for t in a['turns'] if t['r']==127 and t['id']==1 for i,v in t['start'].items() if 428 in v]
 if gid==1492092:
  res['922_seen']=[{'r':t['r'],'parts':sum(c in g.window(t['start'][qi][0]) for c in t['start'].get('922',[])),'head_seen':bool(t['start'].get('922') and t['start']['922'][0] in g.window(t['start'][qi][0]))} for t in a['turns'] if t['id']==0 and '922' in t['start']]
  res['late_splits144']=[{'r':t['r'],'L':len(t['start'][str(t['id'])]),'split':t['splits']} for t in a['turns'] if t['id']==144 and t['r']>=478 and t['splits']]
 out[gid]=res;print(gid,json.dumps(res),flush=True)
(O/'verify.json').write_text(json.dumps(out,indent=2))
